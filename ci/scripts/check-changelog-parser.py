"""6-assertion changelog parser verifier.

Validates that _parse_changelog_entries in check-smoke-fixtures.py correctly
handles the v1.1.0 format (bullet_model field + frontmatter dispatcher +
Compacted History anchor parse) while maintaining v1.0.0 backward-compat.

Assertions:
    A1 — v1.1.0 full fixture: entries[0]["bullet_model"] == "claude-opus-4-7"
    A2 — v1.1.0 delta-omit fixture: /secure entry has bullet_model is None
    A3 — v1.0.0 legacy fixture: all entries bullet_model is None, anchors == []
    A4 — Unknown version fixture: parser raises ValueError with "version" in message
    A5 — v1.1.0 full fixture with Compacted History: anchors is non-empty list
         with "skill" + "last_model" keys per entry
    A6 — v1.1.0 synthetic "- Model: (none)" → bullet_model is None
         (defense-in-depth: forbidden literal must not leak)

Exit codes:
    0 — all 6 assertions PASS
    1 — at least one assertion FAILS
    2 — check-smoke-fixtures.py not yet updated (pre-T4a state — bullet_model key absent)
"""
import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FIXTURES = ROOT / "ci" / "fixtures"
SMOKE_SCRIPT = ROOT / ".github" / "scripts" / "check-smoke-fixtures.py"


def _load_parser():
    """Load _parse_changelog_entries from check-smoke-fixtures.py via importlib.

    Registers the module in sys.modules before exec_module to satisfy the
    dataclasses._is_type() check on Python 3.14 (sys.modules[cls.__module__] lookup).
    SMOKE_PINNED_UTC is required by the smoke script's module-level guard.
    """
    import os
    if "SMOKE_PINNED_UTC" not in os.environ:
        os.environ["SMOKE_PINNED_UTC"] = "2026-04-14T00:00:00Z"
    spec = importlib.util.spec_from_file_location("check_smoke_fixtures", SMOKE_SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    # Must register BEFORE exec_module so dataclasses can resolve __module__ via
    # sys.modules lookup (Python 3.14 dataclasses._is_type() requirement).
    sys.modules["check_smoke_fixtures"] = mod
    spec.loader.exec_module(mod)
    return mod._parse_changelog_entries


def _read(fixture_dir: str, filename: str = "changelog.md") -> str:
    path = FIXTURES / fixture_dir / filename
    return path.read_text(encoding="utf-8")


def run_assertions(parse_fn):
    results = []

    # A1: v1.1.0 full fixture — first entry has bullet_model set
    try:
        text = _read("changelog-v1.1.0-full")
        parsed = parse_fn(text)
        entries = parsed["entries"]
        actual = entries[0]["bullet_model"]
        expected = "claude-opus-4-7"
        if actual == expected:
            results.append(("A1", "PASS", f"entries[0].bullet_model == {expected!r}"))
        else:
            results.append(("A1", "FAIL", f"expected {expected!r}, got {actual!r}"))
    except Exception as exc:
        results.append(("A1", "FAIL", f"exception: {exc}"))

    # A2: v1.1.0 delta-omit fixture — /secure entry omits bullet → bullet_model is None
    try:
        text = _read("changelog-v1.1.0-delta-omit")
        parsed = parse_fn(text)
        entries = parsed["entries"]
        # second entry is /secure which omits the - Model: bullet
        secure_entries = [e for e in entries if e["skill"] == "secure"]
        if not secure_entries:
            results.append(("A2", "FAIL", "no /secure entry found in delta-omit fixture"))
        else:
            actual = secure_entries[0]["bullet_model"]
            if actual is None:
                results.append(("A2", "PASS", "/secure entry bullet_model is None (delta-omit path)"))
            else:
                results.append(("A2", "FAIL", f"expected None, got {actual!r}"))
    except Exception as exc:
        results.append(("A2", "FAIL", f"exception: {exc}"))

    # A3: v1.0.0 legacy fixture — all entries bullet_model is None, anchors == []
    try:
        text = _read("changelog-legacy-v1.0.0")
        parsed = parse_fn(text)
        entries = parsed["entries"]
        anchors = parsed["anchors"]
        all_none = all(e["bullet_model"] is None for e in entries)
        if len(entries) != 3:
            results.append(("A3", "FAIL", f"expected 3 entries, got {len(entries)}"))
        elif not all_none:
            bad = [e["skill"] for e in entries if e["bullet_model"] is not None]
            results.append(("A3", "FAIL", f"non-None bullet_model on skills: {bad}"))
        elif anchors != []:
            results.append(("A3", "FAIL", f"expected anchors == [], got {anchors!r}"))
        else:
            results.append(("A3", "PASS", "v1.0.0 legacy: 3 entries, all bullet_model None, anchors == []"))
    except Exception as exc:
        results.append(("A3", "FAIL", f"exception: {exc}"))

    # A4: unknown version fixture → raises ValueError containing "version"
    try:
        bad_text = (
            "---\n"
            "title: Test\n"
            "version: 99.0.0\n"
            "---\n\n"
            "## Recent Activity\n\n"
        )
        raised = False
        error_msg = ""
        try:
            parse_fn(bad_text)
        except ValueError as ve:
            raised = True
            error_msg = str(ve)
        if raised and "version" in error_msg.lower():
            results.append(("A4", "PASS", f"ValueError raised with 'version' in message"))
        elif raised:
            results.append(("A4", "FAIL", f"ValueError raised but 'version' not in message: {error_msg!r}"))
        else:
            results.append(("A4", "FAIL", "no ValueError raised for unknown version 99.0.0"))
    except Exception as exc:
        results.append(("A4", "FAIL", f"unexpected exception: {exc}"))

    # A5: v1.1.0 full fixture with Compacted History → anchors non-empty with skill + last_model keys
    try:
        text = _read("changelog-v1.1.0-full")
        parsed = parse_fn(text)
        anchors = parsed["anchors"]
        if not anchors:
            results.append(("A5", "FAIL", "anchors is empty — expected non-empty list from Compacted History"))
        else:
            missing_keys = [a for a in anchors if "skill" not in a or "last_model" not in a]
            if missing_keys:
                results.append(("A5", "FAIL", f"{len(missing_keys)} anchor(s) missing 'skill' or 'last_model' keys"))
            else:
                results.append(("A5", "PASS", f"anchors: {len(anchors)} item(s), all have 'skill' + 'last_model'"))
    except Exception as exc:
        results.append(("A5", "FAIL", f"exception: {exc}"))

    # A6: v1.1.0 synthetic "- Model: (none)" → bullet_model is None
    # Defense-in-depth: the "(none)" literal is forbidden for writers;
    # parser must coerce it to None if it ever appears (e.g., from a
    # hand-edited changelog or a third-party writer violation).
    try:
        synthetic_text = (
            "---\n"
            "title: Test\n"
            "version: 1.1.0\n"
            "---\n\n"
            "## Recent Activity\n\n"
            "### 2026-04-20 — /audit\n"
            "- Model: (none)\n"
            "- Detected: (none)\n"
            "- Applied: (none)\n"
            "- Recommendations: (none)\n"
        )
        parsed = parse_fn(synthetic_text)
        entries = parsed["entries"]
        if not entries:
            results.append(("A6", "FAIL", "no entries parsed from synthetic (none) fixture"))
        else:
            actual = entries[0]["bullet_model"]
            if actual is None:
                results.append(("A6", "PASS", "- Model: (none) coerced to None (defense-in-depth)"))
            else:
                results.append(("A6", "FAIL", f"- Model: (none) leaked as {actual!r}; expected None"))
    except Exception as exc:
        results.append(("A6", "FAIL", f"exception: {exc}"))

    return results


def main():
    if not SMOKE_SCRIPT.exists():
        print(f"[BLOCKED] {SMOKE_SCRIPT} not found.", file=sys.stderr)
        sys.exit(2)

    try:
        parse_fn = _load_parser()
    except Exception as exc:
        print(f"[BLOCKED] Failed to load _parse_changelog_entries: {exc}", file=sys.stderr)
        sys.exit(2)

    # Pre-T4a guard: if bullet_model key absent from a parsed entry, this is pre-T4a state
    try:
        sample = _read("changelog-legacy-v1.0.0")
        result = parse_fn(sample)
        if isinstance(result, list):
            print("[BLOCKED] _parse_changelog_entries still returns list[dict] (pre-T4a state).")
            print("          Update check-smoke-fixtures.py per plan Step 5 before running this verifier.")
            sys.exit(2)
        entries = result.get("entries", [])
        if entries and "bullet_model" not in entries[0]:
            print("[BLOCKED] bullet_model key absent from entry dict (pre-Step 3 state).")
            sys.exit(2)
    except Exception:
        pass  # Let individual assertions report failures

    results = run_assertions(parse_fn)
    passes = sum(1 for _, status, _ in results if status == "PASS")
    fails = sum(1 for _, status, _ in results if status == "FAIL")

    for name, status, detail in results:
        marker = "[PASS]" if status == "PASS" else "[FAIL]"
        print(f"{marker} {name}: {detail}")

    print()
    print(f"Result: {passes}/6 PASS, {fails}/6 FAIL")

    if fails > 0:
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
