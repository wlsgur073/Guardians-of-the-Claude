---
title: State I/O Primitives
description: Skill-facing spec for atomic write, state-mutation lock, and deterministic I/O. Skills reference this file instead of restating rules inline.
version: 1.1.1
---

# State I/O Primitives

---

## Atomic write

Every write to a canonical or derived state file must use a temp-file-then-rename pattern. No direct open-and-overwrite.

**Files covered**: `profile.json`, `recommendations.json`, `config-changelog.md`, `drift-state.json`, `state-summary.md` — and the state-mutation lock file itself when acquiring.

**Rule**: Write the new content to a temporary file in the **same directory** as the target, then use `os.replace` to move the temp file to the target path. `os.replace` provides POSIX-rename semantics on every platform (atomic overwrite on both POSIX and Windows since Python 3.3). Do NOT use `os.rename` — on Windows it raises `FileExistsError` when the target already exists, which is the normal case for every update after the first run. Readers never observe a partial write; partial files are impossible mid-write.

**`config-changelog.md` note**: This file uses whole-file read-modify-write semantics (read → edit in memory → atomic write). Do not use `O_APPEND` — append atomicity is unreliable across platforms, and the changelog needs same-day update semantics (editing an existing entry in place), which append cannot express.

**Python idiom**:
```python
import os, tempfile
from pathlib import Path

def atomic_write(path: Path, content: str) -> None:
    dir_ = path.parent
    with tempfile.NamedTemporaryFile("w", dir=dir_, encoding="utf-8",
                                     newline="\n", delete=False) as tmp:
        tmp.write(content)
        tmp_path = tmp.name
    os.replace(tmp_path, path)
```

---

### Multi-file write order

In any multi-file batch that includes derived views, **write source files first and derived views last**. This ensures `derived_mtime ≥ max(source_mtimes)` is the natural fresh state, eliminating false tamper-detection on derived files written within the same atomic batch.

Order amongst source files themselves is unspecified — partial-write recovery during a multi-file batch relies on file presence + schema validation (per Phase 0.5 stale/recovery routing), not intra-batch ordering.

This is a general principle. The concrete order for the current canonical state set is specified in `plugin/references/final-phase.md` Step C (source files first, then `state-summary.md` last).

**No `fsync` between writes** — the current repo contract is `os.replace`-based atomic single-file writes. Adding `fsync` is a durability policy change and belongs to a separate state I/O hardening effort, not this multi-file order rule.

---

## State-mutation lock

A single lock object (`local/.state.lock/`, a directory) serializes all state mutations. **Both** Step 0.5 (migration) and the Final Phase (merge + write) share this one lock. Never use separate lock objects per phase — that introduces ordering and deadlock risk. The lock is a *short* lock: it is held only across a bounded burst of `os.replace` calls with **no LLM work under the lock**, so the held window is sub-second.

**Lock object**: a directory `local/.state.lock/`. Owner metadata lives in `local/.state.lock/owner.json = {"token": <random nonce>, "started_at": "<ISO-8601 UTC>"}` where `token` is a fresh random acquisition nonce generated per acquire — **not** the pid (pid is unsound across hosts on a network mount: pids collide between machines, so a pid-based liveness or ownership test is meaningless on NFS).

**Acquire gate**: `os.mkdir("local/.state.lock")` — atomic create-or-fail on POSIX, Windows, Git Bash, and NFS. `FileExistsError` ⇒ contention (an existing lock dir). There is no "test then create" step; the directory create *is* the test.

**owner.json write**: write `owner.json` via a unique tempfile that is a **sibling under `local/`** (same filesystem) then `os.replace` it into `local/.state.lock/owner.json`. Never place the tempfile inside the lock dir — a stranded temp file there would break the `os.rmdir` on release.

**Stale reclaim**: if `owner.json` is present and its `started_at` age ≥ the reclaim threshold, OR `owner.json` is absent and the lock-dir `st_mtime` age ≥ the threshold, reclaim via a single atomic rename-aside: `os.replace("local/.state.lock", "local/.state.lock.dead.<token>")`. Concurrent reclaimers serialize on this rename — exactly one succeeds; losers get `FileNotFoundError` and re-evaluate from the acquire gate. The winner then `os.mkdir`s a fresh lock. A corrupt `owner.json` is **not** reclaimable: because owner.json is written via atomic replace, a malformed body is a tamper/durability concern (out of scope), so treat it as a live/hard-error and never as stale. `local/.state.lock.dead.*` directories are tombstones only — never read, never used for synchronization; best-effort GC of tombstones older than the threshold happens on acquire.

**Release** (in a `finally`, idempotent): re-read `owner.json`; only if its `token` equals the token this caller acquired with, `unlink` owner.json then `os.rmdir` the lock dir (ignore `ENOENT`/`FileNotFoundError`). If the token does not match, we were stale-reclaimed by another holder — do nothing (deleting would clobber the new owner's lock).

**Reclaim threshold = 30s**, deliberately sized far above the bounded write burst (the lock is held only across a few `os.replace` calls with NO LLM work), so reclaiming a live burst is effectively impossible while a genuinely crashed holder is still recovered. `commit_id` is defense-in-depth: a freak mid-burst reclaim yields a torn set that is *detected*, never silently merged.

**Caller asymmetry**: the 30s stale-reclaim threshold and the Final-Phase contention-wait bound are deliberately the **same value** — their interaction is explicit, not an accidental collision.
- **Step 0.5**: aborts immediately on live contention with "Concurrent state operation detected. Retry in a moment."
- **Final Phase**: re-attempts acquisition until one of: (i) it acquires; (ii) the held lock crosses the 30s stale threshold and is reclaimed via the rename-aside path (crashed holder); or (iii) 30s elapse with the holder still live → abort with the "state not persisted; re-run" message. A live holder cannot exceed 30s while holding (sub-second burst, no LLM work under the lock), so (iii) means genuinely persistent contention and (ii) only fires for a truly crashed holder — the shared value is the single coherent "give up or reclaim" boundary by design.

**Scope**: the lock covers the entire mutation window — from the moment canonical files are first written until all five canonical files (`profile.json`, `recommendations.json`, `config-changelog.md`, `drift-state.json`, `state-summary.md`) are atomically written and the lock is released.

**Python idiom** (acquire/release; mirrors `atomic_write` above for the owner.json write):
```python
import os, time, json, secrets, tempfile
from pathlib import Path

LOCK_DIR = Path("local/.state.lock")
RECLAIM_THRESHOLD = 30.0  # seconds; far above the sub-second write burst

def _now_iso() -> str:
    from datetime import datetime, timezone
    return datetime.now(timezone.utc).isoformat(timespec="seconds")

def _write_owner(token: str) -> None:
    # tempfile is a sibling under local/ (same fs), never inside the lock dir
    with tempfile.NamedTemporaryFile("w", dir=LOCK_DIR.parent, encoding="utf-8",
                                     newline="\n", delete=False) as tmp:
        json.dump({"token": token, "started_at": _now_iso()}, tmp)
        tmp_path = tmp.name
    os.replace(tmp_path, LOCK_DIR / "owner.json")

def _age_seconds(started_at_iso: str) -> float:
    from datetime import datetime, timezone
    started = datetime.fromisoformat(started_at_iso)
    return (datetime.now(timezone.utc) - started).total_seconds()

def _try_reclaim_if_stale() -> None:
    """Atomic rename-aside of a stale lock. Losers raise FileNotFoundError."""
    owner_path = LOCK_DIR / "owner.json"
    try:
        owner = json.loads(owner_path.read_text(encoding="utf-8"))
        stale = _age_seconds(owner["started_at"]) >= RECLAIM_THRESHOLD
    except FileNotFoundError:
        # owner.json absent ⇒ fall back to lock-dir st_mtime age
        stale = (time.time() - LOCK_DIR.stat().st_mtime) >= RECLAIM_THRESHOLD
    except (ValueError, KeyError):
        # corrupt owner.json is a tamper/durability concern: NOT stale
        stale = False
    if stale:
        # exactly one concurrent reclaimer wins; losers get FileNotFoundError
        os.replace(LOCK_DIR, f"local/.state.lock.dead.{secrets.token_hex(8)}")

def acquire() -> str:
    token = secrets.token_hex(16)
    while True:
        try:
            os.mkdir(LOCK_DIR)            # atomic create-or-fail = the test
            _write_owner(token)
            return token
        except FileExistsError:
            try:
                _try_reclaim_if_stale()  # crashed holder → rename-aside
            except FileNotFoundError:
                pass                      # lost the reclaim race; retry gate
            # Step 0.5: abort here; Final Phase: loop until acquire/30s/stale

def release(token: str) -> None:
    owner_path = LOCK_DIR / "owner.json"
    try:
        owner = json.loads(owner_path.read_text(encoding="utf-8"))
    except (FileNotFoundError, ValueError):
        return                            # already gone / reclaimed: no-op
    if owner.get("token") != token:
        return                            # stale-reclaimed: do not clobber
    try:
        owner_path.unlink()
        os.rmdir(LOCK_DIR)
    except FileNotFoundError:
        pass                              # idempotent: ignore ENOENT
```

---

## Deterministic I/O

All file writes must produce byte-for-byte identical output across platforms given the same logical content.

**Encoding**: always `open(path, "w", encoding="utf-8", newline="\n")`. Explicit LF line endings prevent Windows CRLF drift.

**Timestamps at runtime** (production skill invocation): `datetime.now(timezone.utc).isoformat(timespec="seconds")` — ISO-8601 UTC, second precision.

**Exception (`audit_run_id` only)**: `audit_run_id` uses canonical ISO-8601 UTC with microseconds and an explicit offset (e.g. `2026-05-18T09:00:00.000000+00:00`; the bare-`Z` form is normalized away). Under the Final-Phase short lock its value is monotonically bumped by parsing existing `audit_run_id` values to `datetime` (never string-sorting) and, if the candidate ≤ max(existing), setting it to max(existing) + 1µs. This is the only carve-out from the second-precision rule; verifier determinism is preserved because the bump reads on-disk values, not the wall clock.

**Timestamps in verifier** (smoke test / CI): read from the `SMOKE_PINNED_UTC` environment variable. Never call `datetime.now()` inside a verifier run. This guarantees reproducible fixture output.

**Directory iteration**: always `sorted(Path(...).glob(...))` — platform glob order is undefined; sorting ensures deterministic file processing order.
