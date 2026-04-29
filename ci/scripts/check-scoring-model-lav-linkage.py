"""4-assertion structural verifier for LAV-axis <-> scoring-model.md linkage.

Assertions:
    1. scoring-model.md contains `## LAV Axis Summary` heading with 6 table rows
       covering L1 through L6 with numeric ranges matching lav.md:23-28.
    2. scoring-model.md contains `### LAV/T3 Boundary Rule` heading with the 3 boundary
       pairs (T3.1<->L1, T3.3<->L2, T3.7<->L2).
    3. scoring-model.md count-source footnote declares profile count fields
       and skill co-ownership.
    4. scoring-model.md DS/SB/cap-tier formula block (## Formula ```markdown...```) is
       byte-identical to the content-anchor hash -- ensures no formula drift.
       Uses content-anchor (section-header search) not line numbers, so later
       line insertions do not cause false failures.

Exit codes:
    0 -- all 4 assertions pass
    1 -- one or more assertions fail
    2 -- scoring-model.md not found
"""
import sys
import hashlib
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCORING_MODEL = ROOT / "plugin" / "references" / "scoring-model.md"

# SHA256 of the ## Formula code block content (```markdown...``` inclusive).
# Content-anchor approach: locates the block via ## Formula section heading,
# independent of line numbers.
# This hash freezes the displayed formula block, including labels; update it only
# with reviewed scoring-model.md changes.
DS_SB_CAP_HASH = "a4b159b8d9262cb42cfe5842f60bca68e9da2e32e1b9c1faffe7896f74a79814"

# L1-L6 axis names + numeric ranges as declared in lav.md:23-28.
# Each tuple: (axis_label_substring, range_substring)
# Ranges use Unicode minus sign (U+2212, '\u2212') as written in scoring-model.md.
# Note: lav.md uses ASCII hyphen-minus in its table; scoring-model.md intentionally
# adopts U+2212 for typographic consistency with the prose. The verifier matches
# scoring-model.md content, so U+2212 is the correct expected value here.
LAV_AXES = [
    ("L1", "\u22123 / 0 / +2"),
    ("L2", "\u22122 / 0 / +2"),
    ("L3", "0 / +1 / +3"),
    ("L4", "\u22121 / 0 / +1"),
    ("L5", "\u22123 / 0 / +1"),
    ("L6", "0 / +1"),
]

# LAV/T3 Boundary Rule pairs: each must appear as a table row with both labels.
BOUNDARY_PAIRS = [
    ("T3.1", "L1"),
    ("T3.3", "L2"),
    ("T3.7", "L2"),
]

COUNT_SOURCE_SUBSTRINGS = (
    "profile.claude_code_configuration_state.*_count",
    "co-owned across `/audit` + `/secure` + `/create`",
    "plugin/references/lib/merge_rules.md",
)


def check_assertion_1(text: str) -> tuple:
    """## LAV Axis Summary heading present + 6 axis table rows with correct ranges."""
    if "## LAV Axis Summary" not in text:
        return False, "## LAV Axis Summary heading not found"
    missing = []
    for axis_label, range_str in LAV_AXES:
        pattern = re.compile(
            re.escape(axis_label) + r".*" + re.escape(range_str) + r"|"
            + re.escape(range_str) + r".*" + re.escape(axis_label)
        )
        if not pattern.search(text):
            missing.append(axis_label + " row with range '" + range_str + "'")
    if missing:
        return False, "Missing axis rows: " + "; ".join(missing)
    return True, "6 axis rows with correct ranges found"


def check_assertion_2(text: str) -> tuple:
    """### LAV/T3 Boundary Rule heading + 3 boundary pair rows."""
    if "### LAV/T3 Boundary Rule" not in text:
        return False, "### LAV/T3 Boundary Rule heading not found"
    missing = []
    for t3_item, lav_axis in BOUNDARY_PAIRS:
        pattern = re.compile(
            re.escape(t3_item) + r".*" + re.escape(lav_axis) + r"|"
            + re.escape(lav_axis) + r".*" + re.escape(t3_item)
        )
        if not pattern.search(text):
            missing.append(t3_item + "<->" + lav_axis)
    if missing:
        return False, "Missing boundary pairs: " + "; ".join(missing)
    return True, "3 boundary pairs found"


def check_assertion_3(text: str) -> tuple:
    """Count-source footnote declares profile count fields and skill co-ownership."""
    missing = [s for s in COUNT_SOURCE_SUBSTRINGS if s not in text]
    if not missing:
        return True, "Count-source footnote elements found"
    return False, "Count-source footnote missing: " + "; ".join(missing)


def check_assertion_4(path: Path) -> tuple:
    """Formula block (## Formula ```markdown...```) SHA256 unchanged.

    Uses content-anchor: locates ## Formula section, finds the ```markdown...```
    code block within it, hashes that slice. Line-number-independent so later
    line insertions do not cause false failures.
    """
    lines = path.read_text(encoding="utf-8").splitlines(keepends=True)

    start_idx = None
    end_idx = None
    in_formula_section = False
    in_code_block = False
    for i, line in enumerate(lines):
        stripped = line.rstrip()
        if stripped == "## Formula":
            in_formula_section = True
            continue
        if in_formula_section and stripped.startswith("## ") and stripped != "## Formula":
            break
        if in_formula_section and stripped.startswith("```") and not in_code_block:
            in_code_block = True
            start_idx = i
            continue
        if in_formula_section and in_code_block and stripped == "```":
            end_idx = i
            break

    if start_idx is None or end_idx is None:
        return False, "Could not locate ## Formula code block in scoring-model.md"

    chunk = "".join(lines[start_idx : end_idx + 1])
    actual_hash = hashlib.sha256(chunk.encode("utf-8")).hexdigest()

    if actual_hash == DS_SB_CAP_HASH:
        return True, "Formula block hash verified (content-anchor, hash: " + actual_hash[:16] + "...)"
    return False, (
        "Formula block hash mismatch -- formula may have been changed. "
        "Actual: " + actual_hash[:16] + "... Expected: " + DS_SB_CAP_HASH[:16] + "..."
    )


def _safe_print(label: str, msg: str) -> None:
    """Print safely, replacing unencodable chars for terminals with limited charsets."""
    encoding = sys.stdout.encoding or "utf-8"
    line = "[" + label + "] " + msg
    safe = line.encode(encoding, errors="replace").decode(encoding, errors="replace")
    print(safe)


def main():
    if not SCORING_MODEL.exists():
        print("[BLOCKED] " + str(SCORING_MODEL) + " not found.")
        sys.exit(2)

    text = SCORING_MODEL.read_text(encoding="utf-8")
    results = []

    ok1, msg1 = check_assertion_1(text)
    results.append((ok1, "A1 (LAV Axis Summary + 6 rows)", msg1))

    ok2, msg2 = check_assertion_2(text)
    results.append((ok2, "A2 (LAV/T3 Boundary Rule + 3 pairs)", msg2))

    ok3, msg3 = check_assertion_3(text)
    results.append((ok3, "A3 (count-source footnote ownership)", msg3))

    ok4, msg4 = check_assertion_4(SCORING_MODEL)
    results.append((ok4, "A4 (DS/SB/cap formula hash unchanged)", msg4))

    all_pass = True
    for ok, label, msg in results:
        status = "PASS" if ok else "FAIL"
        if not ok:
            all_pass = False
        _safe_print(status, label + ": " + msg)

    if all_pass:
        print("All 4 assertions PASS -- LAV linkage verified.")
        sys.exit(0)
    else:
        fail_count = sum(1 for ok, _, _ in results if not ok)
        print(str(fail_count) + "/4 assertion(s) FAILED.")
        sys.exit(1)


if __name__ == "__main__":
    main()
