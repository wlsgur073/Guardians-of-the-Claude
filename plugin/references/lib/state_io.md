---
title: State I/O Primitives
description: Skill-facing spec for atomic write, state-mutation lock, and deterministic I/O. Skills reference this file instead of restating rules inline.
version: 1.0.0
---

# State I/O Primitives

Authoritative source: `docs/superpowers/v3-roadmap/phase-1-contracts.md` §Shared Primitives 1, 2, 5. This file is the skill-facing projection.

---

## Atomic write

Every write to a canonical or derived state file must use a temp-file-then-rename pattern. No direct open-and-overwrite.

**Files covered**: `profile.json`, `recommendations.json`, `config-changelog.md`, `state-summary.md` — and the state-mutation lock file itself when acquiring.

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

## State-mutation lock

A single lock file (`local/.state.lock`) serializes all state mutations. **Both** Step 0.5 (migration) and the Final Phase (merge + write) share this one lock. Never use separate lock files per phase — that introduces ordering and deadlock risk.

**Lock content** (JSON): `{"pid": <int>, "started_at": "<ISO-8601-UTC>"}`.

**Acquire**:
1. If `local/.state.lock` does not exist, write a fresh lock via atomic write (temp + rename) and proceed.
2. If the lock exists and `started_at` is less than 60 seconds ago: another skill is mid-mutation. Behavior depends on the caller:
   - **Step 0.5**: abort immediately with "Concurrent state operation detected. Retry in a moment."
   - **Final Phase**: wait up to 30 seconds before aborting. Aborting after a long skill run is bad UX; the write window is short.
3. If the lock exists and `started_at` is 60 seconds or older: the previous holder crashed. Remove the stale lock and write a fresh one.

**Release**: `os.unlink("local/.state.lock")` after all writes complete. Always release the lock in a `finally` block or equivalent cleanup path so it runs even if a write raises. The 60-second stale auto-release recovers abandoned locks, but relying on it degrades UX — Step 0.5 of the next run will abort, and Final Phase will stall up to 30 seconds.

**Scope**: the lock covers the entire mutation window — from the moment canonical files are first written until all four files (`profile.json`, `recommendations.json`, `config-changelog.md`, `state-summary.md`) are atomically written and the lock is released.

---

## Deterministic I/O

All file writes must produce byte-for-byte identical output across platforms given the same logical content.

**Encoding**: always `open(path, "w", encoding="utf-8", newline="\n")`. Explicit LF line endings prevent Windows CRLF drift.

**Timestamps at runtime** (production skill invocation): `datetime.now(timezone.utc).isoformat(timespec="seconds")` — ISO-8601 UTC, second precision.

**Timestamps in verifier** (smoke test / CI): read from the `SMOKE_PINNED_UTC` environment variable. Never call `datetime.now()` inside a verifier run. This guarantees reproducible fixture output.

**Directory iteration**: always `sorted(Path(...).glob(...))` — platform glob order is undefined; sorting ensures deterministic file processing order.
