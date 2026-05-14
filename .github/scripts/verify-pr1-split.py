#!/usr/bin/env python3
"""verify-pr1-split.py — One-shot Tier 2B verifier for PR1 mechanical split.

Confirms that the 8 new subfiles collectively reconstitute the original
learning-system.md section content, modulo intentional additions
(new subfile frontmatter, orchestrator stubs).

Reads the original via `git show <ref>:plugin/references/learning-system.md`
where <ref> defaults to `main`. Compare-by-section, normalized whitespace.

Usage:
    python .github/scripts/verify-pr1-split.py [--original-ref main]

Exit codes:
    0 = pass (split is mechanical)
    1 = fail (content drift or missing section detected)
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path
from typing import Optional

# Ensure UTF-8 stdout on Windows (cp949 default would mangle CJK / em-dash)
sys.stdout.reconfigure(encoding="utf-8")

# Manifest: original section H2 text -> target subfile.
MANIFEST = {
    "Common Phase 0: Load Context & Learn": "phase-0.md",
    "Learning Rules (CSA Pattern)": "learning-rules.md",
    "Common Final Phase: Persist Results & Learn": "final-phase.md",
    "Per-Skill Merge Rules (Final Phase under state-mutation lock)": "final-phase.md",
    "Model Bullet Emission (config-changelog.md)": "drift-state.md",
    "Same-Day Duplicate Check (Step 3a)": "compaction.md",
    "Compaction Algorithm (Step 3b)": "compaction.md",
    "Legacy Project Profile Format (pre-v2.11.0)": "schema-policy.md",
    "config-changelog.md Format": "state-rendering.md",
    "State Rendering": "state-rendering.md",
    "Drift Advisory Derivation": "drift-state.md",
    "Migration Notice (printed once after legacy→JSON conversion)": "phase-0.md",
    "Schema Evolution Policy": "schema-policy.md",
    "Recommendation ID Registry": "schema-policy.md",
    "Token Budget": "state-rendering.md",
    "Critical Thinking & Insight Delivery": "critical-thinking.md",
}

REFERENCES_DIR = Path("plugin/references")


def load_original(git_ref: str) -> str:
    """Load original learning-system.md from git history."""
    result = subprocess.run(
        ["git", "show", f"{git_ref}:plugin/references/learning-system.md"],
        capture_output=True, text=True, check=True, encoding="utf-8",
    )
    return result.stdout


def split_into_sections(content: str) -> dict:
    """Split markdown into {h2_text: section_body_lines_joined}.

    Skips H2 headings inside fenced code blocks (``` ... ```).
    The original learning-system.md embeds H2-style example markdown inside
    fenced ```markdown blocks (Legacy Profile Format example, State Rendering
    layout); naive splitting would treat those as new sections and mangle the
    parent section bodies.
    """
    sections: dict = {}
    current_heading: Optional[str] = None
    current_body: list = []
    in_fence = False
    for line in content.splitlines():
        if line.startswith("```"):
            in_fence = not in_fence
            if current_heading is not None:
                current_body.append(line)
            continue
        if not in_fence:
            m = re.match(r"^## (.+)$", line)
            if m:
                if current_heading is not None:
                    sections[current_heading] = "\n".join(current_body).rstrip()
                current_heading = m.group(1).strip()
                current_body = []
                continue
        if current_heading is not None:
            current_body.append(line)
    if current_heading is not None:
        sections[current_heading] = "\n".join(current_body).rstrip()
    return sections


def strip_frontmatter(content: str) -> str:
    """Remove leading YAML frontmatter block."""
    if content.startswith("---\n"):
        end = content.find("\n---\n", 4)
        if end != -1:
            return content[end + 5:].lstrip()
    return content


def load_subfile_sections(subfile_name: str):
    path = REFERENCES_DIR / subfile_name
    if not path.exists():
        return None
    content = path.read_text(encoding="utf-8")
    content = strip_frontmatter(content)
    return split_into_sections(content)


def normalize(text: str) -> str:
    """Normalize whitespace for comparison (collapse all whitespace runs)."""
    return re.sub(r"\s+", " ", text).strip()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--original-ref", default="main",
                        help="Git ref to read original learning-system.md from (default: main)")
    args = parser.parse_args()

    original = load_original(args.original_ref)
    original_sections = split_into_sections(original)

    errors: list = []
    subfile_cache: dict = {}

    # Verify every original H2 has a manifest entry
    for h2 in original_sections:
        if h2 not in MANIFEST:
            errors.append(f"MANIFEST MISSING: original section '{h2}' has no target subfile")

    # Verify every manifest entry resolves correctly
    for h2, target in MANIFEST.items():
        if h2 not in original_sections:
            errors.append(f"ORIGINAL MISSING: '{h2}' (manifest expects it in original)")
            continue
        if target not in subfile_cache:
            subfile_cache[target] = load_subfile_sections(target)
        sections = subfile_cache[target]
        if sections is None:
            errors.append(f"SUBFILE MISSING: {target} (for section '{h2}')")
            continue
        if h2 not in sections:
            errors.append(f"SECTION MISSING: '{h2}' not found as H2 in {target}")
            continue
        if normalize(original_sections[h2]) != normalize(sections[h2]):
            errors.append(
                f"CONTENT DRIFT: section '{h2}' in {target} differs from original "
                f"(orig {len(original_sections[h2])} chars vs subfile {len(sections[h2])} chars)"
            )

    if errors:
        print(f"FAIL: {len(errors)} mechanical split violation(s):\n")
        for err in errors:
            print(f"  - {err}")
        return 1

    print(f"PASS: All {len(MANIFEST)} sections preserved across split.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
