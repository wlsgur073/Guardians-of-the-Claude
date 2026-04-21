"""Normalization-table fixture validator.

Reference implementation of normalize_model_id:
- Parses the Normalization Table section from plugin/references/model-drift-rules.md
- Applies longest-match + fail-safe null
- Validates all test cases in ci/fixtures/t3-model-drift/test-cases.json

This is the TABLE validator only. Runtime /audit integration is handled separately.

Exit codes:
    0 — all test cases PASS
    1 — at least one test case FAIL or table parse error
    2 — model-drift-rules.md or test-cases.json not found
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RULES_FILE = ROOT / "plugin" / "references" / "model-drift-rules.md"
TESTS_FILE = ROOT / "ci" / "fixtures" / "t3-model-drift" / "test-cases.json"

# Canonical axis value sets (closed enumerations).
# Used for post-match validation (canonicalization guard).
VALID_FAMILY_TIER = {"opus", "sonnet", "haiku"}
VALID_CONTEXT_WINDOW = {"200k", "1M"}
VALID_REASONING = {"none", "extended_any"}
VALID_CONTEXT_MGMT = {"manual", "compaction_capable"}

FINGERPRINT_AXES = ("family_tier", "context_window_class", "reasoning_class", "context_management_class")


def parse_normalization_table(md_text: str) -> list[dict]:
    """Extract observed rows from the Normalization Table section.

    Returns list of dicts with keys:
        raw_pattern, normalized_id, family_tier, context_window_class,
        reasoning_class, context_management_class, evidence_status

    Only rows with evidence_status == 'observed' are returned
    (hypothesized / extrapolated are inactive per model-drift-rules.md Evidence Status Labels section).
    """
    # Locate the Normalization Table section.
    section_match = re.search(
        r"^## Normalization Table\s*\n(.*?)(?=^## |\Z)",
        md_text,
        re.MULTILINE | re.DOTALL,
    )
    if not section_match:
        raise ValueError("Normalization Table section not found in model-drift-rules.md")

    section = section_match.group(1)

    # Find the markdown table — header row starts with '| raw_pattern'
    table_match = re.search(
        r"(\| raw_pattern \|.*?\n\|[-| ]+\|\n)((?:\|.*\n)*)",
        section,
        re.IGNORECASE,
    )
    if not table_match:
        raise ValueError("Normalization Table markdown table not found")

    header_line = table_match.group(1).split("\n")[0]
    headers = [h.strip().strip("`") for h in header_line.split("|") if h.strip()]

    rows_text = table_match.group(2)
    rules = []
    for line in rows_text.splitlines():
        line = line.strip()
        if not line or not line.startswith("|"):
            continue
        cells = [c.strip().strip("`") for c in line.split("|") if c.strip() != ""]
        if len(cells) != len(headers):
            print(
                f"[WARN] Skipped malformed row (got {len(cells)} cells, "
                f"expected {len(headers)}): {line!r}",
                file=sys.stderr,
            )
            continue
        row = dict(zip(headers, cells))
        if row.get("evidence_status") != "observed":
            continue
        rules.append(row)

    return rules


def pattern_to_regex(raw_pattern: str) -> re.Pattern:
    """Convert a raw_pattern with wildcard notation to a compiled regex.

    Wildcard '*' at end-of-pattern is treated as '.*' (any trailing suffix).
    Non-wildcard characters are escaped. Match is anchored (full-string match).
    """
    # Escape all regex-special characters, then restore intended wildcards.
    escaped = re.escape(raw_pattern)
    # re.escape converts '*' to r'\*'; restore as '.*' for suffix wildcard.
    regex_str = escaped.replace(r"\*", ".*")
    return re.compile(r"^" + regex_str + r"$")


def normalize_model_id(raw: str, rules: list[dict]) -> dict | None:
    """Longest-match normalization.

    Contracts implemented:
    #1 Totality   — always returns fingerprint dict or None; never raises.
    #2 Canonical  — returned axis values are in the closed enumeration sets.
    #3 Fail-safe  — unrecognized / unparseable / out-of-space → None.
    #4 Longest-match — most-specific (longest raw_pattern string) wins.
    #5 Determinism — pure function; no I/O, no state, no randomness.
    """
    try:
        # Build (pattern_length, compiled_regex, rule) tuples — longest pattern first.
        candidates = []
        for rule in rules:
            pattern = rule["raw_pattern"]
            regex = pattern_to_regex(pattern)
            candidates.append((len(pattern), regex, rule))

        # Sort descending by pattern length (longest wins on overlap).
        # Secondary key: raw_pattern string for deterministic tie-breaking
        # (table-order independence if two patterns share length AND match).
        candidates.sort(key=lambda t: (t[0], t[2]["raw_pattern"]), reverse=True)

        matched_rule = None
        for _length, regex, rule in candidates:
            if regex.match(raw):
                matched_rule = rule
                break

        if matched_rule is None:
            return None  # #3 Fail-safe: no matching rule

        # Build fingerprint dict from matched rule.
        fp = {
            "family_tier": matched_rule["family_tier"],
            "context_window_class": matched_rule["context_window_class"],
            "reasoning_class": matched_rule["reasoning_class"],
            "context_management_class": matched_rule["context_management_class"],
        }

        # #2 + #3: canonicalization guard — axis values must be in the closed enumeration sets.
        if fp["family_tier"] not in VALID_FAMILY_TIER:
            return None
        if fp["context_window_class"] not in VALID_CONTEXT_WINDOW:
            return None
        if fp["reasoning_class"] not in VALID_REASONING:
            return None
        if fp["context_management_class"] not in VALID_CONTEXT_MGMT:
            return None

        return fp

    except Exception:
        # #1 Totality: never propagate exceptions.
        return None


def main() -> None:
    missing = []
    if not RULES_FILE.exists():
        missing.append(str(RULES_FILE))
    if not TESTS_FILE.exists():
        missing.append(str(TESTS_FILE))
    if missing:
        print("[ERROR] Required file(s) not found:")
        for p in missing:
            print(f"  {p}")
        sys.exit(2)

    # Parse normalization table.
    try:
        rules = parse_normalization_table(RULES_FILE.read_text(encoding="utf-8"))
    except ValueError as exc:
        print(f"[ERROR] Table parse failed: {exc}")
        sys.exit(1)

    if not rules:
        print("[ERROR] No observed rows found in Normalization Table")
        sys.exit(1)

    print(f"Loaded {len(rules)} observed rule(s) from normalization table.")

    # Load test cases.
    tests = json.loads(TESTS_FILE.read_text(encoding="utf-8"))

    fails = []
    for tc in tests:
        raw_input = tc["input"]
        expected = tc["expected_fingerprint"]
        actual = normalize_model_id(raw_input, rules)
        if actual != expected:
            fails.append(
                f"  [{raw_input}]\n"
                f"    expected: {expected}\n"
                f"    got:      {actual}"
            )

    if fails:
        print(f"[FAIL] {len(fails)}/{len(tests)} test case(s) FAILED:")
        for f in fails:
            print(f)
        sys.exit(1)

    print(f"All {len(tests)} test case(s) PASS - normalization table consistent with contracts S3.5.")
    sys.exit(0)


if __name__ == "__main__":
    main()
