#!/usr/bin/env python3
"""Drift-aware /audit structural + state-machine validator.

Covers 17 assertions:
  A1 drift advisory state machine simulation (5 fixtures)
  A2 .model field in Step 0.5 profile.json write set (phase-0.md)
  A3 install-integrity pre-Phase-0 substep in /audit SKILL.md
  A4 Final Phase triggers (model write + scoring-model-change banner + drift advisory)
  A5 output-format.md drift block position (between Score and ★ Most impactful)
  A6 output-format.md drift block format (changed-axes-only + baseline annotation + no severity)
  A7 drift-state schema files exist + wrapper pins version + I7 cold-start invariant
  A8 phase-0/final-phase/state-rendering reference docs mention drift-state.json
  A9 algorithm replacement — drift-state.md/output-format.md no longer carry legacy strings
  A10 cross-field invariant I9 — baseline.first_observed_at == legacy_migration.source_changelog_anchor_run_id
  A_LOCK1 state_io.md §State-mutation lock uses atomic mkdir + rename-aside (no check-then-act)
  A_LOCK2 final-phase.md/drift-state.md/merge_rules.md carry no old-contract "re-read/merge under lock" phrasing
  A_LOCK3 phase-0.md Step 0.5 encodes marker preflight + genesis + torn-set recovery
  A_LOCK4 drift-state.md drops "tracked separately"; state-rendering.md echoes commit_id (changelog frontmatter + summary header)
  A_LOCK5 drift-state.md affirmatively encodes marker/OCC-derivation (Step-C compare-and-commit; commit_id marker) + final-phase.md Step C / OCC framing exists (POSITIVE companion to A9's negative)
  A_LOCK6 drift-state.md canonical-microsecond + monotonic-bump current_audit_run_id contract present (OCC Step-C derivation-path scope; NOT the repo-wide every-emitted invariant — migration path legitimately bare-Z)
  A_LOCK7 verification gate — ANY plugin/skills/*/SKILL.md carries no old-contract "re-read/merge under (state-mutation) lock" phrasing nor retired Final-Phase Step-numbering (globbed, not audit-hardcoded)
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

# ---------------------------------------------------------------------------
# A1: drift advisory state machine
# ---------------------------------------------------------------------------

Fingerprint = dict  # {family_tier: opus|sonnet|haiku, context_window_class: 200k|1M, reasoning_class: none|extended_any, context_management_class: manual|compaction_capable}


def drift_state(
    current_fp: Fingerprint | None,
    baseline_present: bool,
    baseline_fp: Fingerprint | None,
) -> str:
    """Pure drift advisory state machine (silence evaluation order).

    Returns one of: "match", "missing_baseline", "normalization_null", "drift".
    """
    # Silence evaluation order (short-circuit, deterministic).
    if current_fp is None or (baseline_present and baseline_fp is None):
        return "normalization_null"
    if not baseline_present:
        return "missing_baseline"
    if current_fp == baseline_fp:
        return "match"
    return "drift"


# Fixture table.
A1_FIXTURES = [
    (
        "match",
        {"family_tier": "opus", "context_window_class": "200k",
         "reasoning_class": "extended_any", "context_management_class": "manual"},
        True,
        {"family_tier": "opus", "context_window_class": "200k",
         "reasoning_class": "extended_any", "context_management_class": "manual"},
        "match",
    ),
    (
        "drift",
        {"family_tier": "sonnet", "context_window_class": "1M",
         "reasoning_class": "extended_any", "context_management_class": "manual"},
        True,
        {"family_tier": "opus", "context_window_class": "200k",
         "reasoning_class": "extended_any", "context_management_class": "manual"},
        "drift",
    ),
    (
        "normalization_null_current",
        None,
        True,
        {"family_tier": "opus", "context_window_class": "200k",
         "reasoning_class": "extended_any", "context_management_class": "manual"},
        "normalization_null",
    ),
    (
        "normalization_null_baseline",
        {"family_tier": "opus", "context_window_class": "200k",
         "reasoning_class": "extended_any", "context_management_class": "manual"},
        True,
        None,
        "normalization_null",
    ),
    (
        "missing_baseline",
        {"family_tier": "opus", "context_window_class": "200k",
         "reasoning_class": "extended_any", "context_management_class": "manual"},
        False,
        None,
        "missing_baseline",
    ),
]


def check_a1_state_machine() -> list[str]:
    failures = []
    for name, current, present, baseline, expected in A1_FIXTURES:
        actual = drift_state(current, present, baseline)
        if actual != expected:
            failures.append(f"A1 {name}: expected {expected!r}, got {actual!r}")
    return failures


# ---------------------------------------------------------------------------
# A2: Step 0.5 — .model field emission in profile.json write set
# ---------------------------------------------------------------------------


def check_a2_write_point_1() -> list[str]:
    """Verify .model field is part of the Step 0.5 profile.json write set."""
    failures = []
    phase_0_md = (
        REPO_ROOT / "plugin" / "references" / "phase-0.md"
    ).read_text(encoding="utf-8")

    step_05_match = re.search(
        r"\*\*Step 0\.5 — Migration & Stale Check\*\*.*?(?=\n## |\n---)",
        phase_0_md,
        flags=re.DOTALL,
    )
    if not step_05_match:
        failures.append("A2: Step 0.5 section not found in phase-0.md")
        return failures

    step_05 = step_05_match.group(0)

    if ".model" not in step_05:
        failures.append("A2: Step 0.5 missing .model field in profile.json write set")

    return failures


# ---------------------------------------------------------------------------
# A3: Install-integrity pre-Phase-0 substep in /audit SKILL.md
# ---------------------------------------------------------------------------


def check_a3_install_integrity() -> list[str]:
    """Verify /audit SKILL.md declares an install-integrity check before Phase 0."""
    failures = []
    skill_md = (
        REPO_ROOT / "plugin" / "skills" / "audit" / "SKILL.md"
    ).read_text(encoding="utf-8")

    phase_0_idx = skill_md.find("## Phase 0")
    if phase_0_idx == -1:
        failures.append("A3: Phase 0 heading not found in /audit SKILL.md")
        return failures

    pre_phase_0 = skill_md[:phase_0_idx]

    required_markers = [
        ("install-integrity", "A3: no 'install-integrity' mention before Phase 0"),
        ("scoring_contract_id", "A3: no 'scoring_contract_id' mention before Phase 0"),
        ("abort", "A3: pre-Phase-0 check missing abort-on-mismatch language"),
    ]
    for marker, msg in required_markers:
        if marker not in pre_phase_0:
            failures.append(msg)
    return failures


# ---------------------------------------------------------------------------
# A4: Final Phase triggers — model write + banner + drift advisory
# ---------------------------------------------------------------------------


def check_a4_final_phase_triggers() -> list[str]:
    """Verify Phase 5 declares model write + banner + drift advisory triggers."""
    failures = []
    skill_md = (
        REPO_ROOT / "plugin" / "skills" / "audit" / "SKILL.md"
    ).read_text(encoding="utf-8")

    phase_5_match = re.search(
        r"## Phase 5:.*?(?=\n## |\Z)",
        skill_md,
        flags=re.DOTALL,
    )
    if not phase_5_match:
        failures.append("A4: Phase 5 section not found in /audit SKILL.md")
        return failures
    phase_5 = phase_5_match.group(0)

    required = [
        ("Final Phase model write", "A4: Phase 5 missing Final Phase model write trigger"),
        ("scoring-model-change banner", "A4: Phase 5 missing scoring-model-change banner reference"),
        ("drift advisory", "A4: Phase 5 missing drift advisory trigger"),
        ("stateless", "A4: Phase 5 missing stateless mode guard"),
        ("NOT added to recommendations.json", "A4: Phase 5 does not state drift advisory is NOT persisted in recommendations.json"),
    ]
    for marker, msg in required:
        if marker not in phase_5:
            failures.append(msg)
    return failures


# ---------------------------------------------------------------------------
# A5: output-format.md drift block position (between Score and Most impactful)
# ---------------------------------------------------------------------------


def check_a5_drift_block_position() -> list[str]:
    """Verify drift block example appears between Score line and Most impactful."""
    failures = []
    of_md = (
        REPO_ROOT / "plugin" / "skills" / "audit" / "references" / "output-format.md"
    ).read_text(encoding="utf-8")

    drift_header = "Model drift detected"
    if drift_header not in of_md:
        failures.append(f"A5: '{drift_header}' marker not found in output-format.md")
        return failures

    score_idx = of_md.find("Score:")
    most_impactful_idx = of_md.find("Most impactful")
    drift_idx = of_md.find(drift_header)
    if score_idx == -1 or most_impactful_idx == -1:
        failures.append("A5: cannot locate Score or Most impactful anchors")
        return failures
    if not (score_idx < drift_idx < most_impactful_idx):
        failures.append(
            f"A5: drift block position wrong (Score={score_idx}, Drift={drift_idx}, MostImpactful={most_impactful_idx})"
        )
    return failures


# ---------------------------------------------------------------------------
# A6: output-format.md drift block format (changed-axes-only + baseline + no severity + conditional)
# ---------------------------------------------------------------------------


def check_a6_drift_block_format() -> list[str]:
    """Verify drift block description includes 4 format requirements."""
    failures = []
    of_md = (
        REPO_ROOT / "plugin" / "skills" / "audit" / "references" / "output-format.md"
    ).read_text(encoding="utf-8")

    required = [
        ("changed axes only", "A6: drift block format must specify changed-axes only"),
        ("baseline", "A6: drift block format must mention baseline source annotation"),
        ("No severity label", "A6: drift block must document no-severity-label rule"),
        ("conditional", "A6: drift block must be documented as conditional"),
    ]
    for marker, msg in required:
        if marker.lower() not in of_md.lower():
            failures.append(msg)
    return failures


# ---------------------------------------------------------------------------
# A7: Schema integrity — drift-state schema files exist + wrapper pins version
# ---------------------------------------------------------------------------


def check_a7_schema_integrity() -> list[str]:
    """Verify drift-state schema files exist, wrapper pins schema_version,
    and cold-start invariant (I7) is encoded as wrapper if/then — checking
    both the if-clause (baseline=null) and the then-branch (last_seen=null
    AND legacy_migration=null) so a mutation dropping either half is caught."""
    failures = []
    base_path = REPO_ROOT / "plugin" / "references" / "schemas" / "drift-state.schema.base.json"
    wrapper_path = REPO_ROOT / "plugin" / "references" / "schemas" / "drift-state.schema.v1.0.0.json"

    if not base_path.exists():
        failures.append(f"A7: drift-state.schema.base.json missing at {base_path}")
    if not wrapper_path.exists():
        failures.append(f"A7: drift-state.schema.v1.0.0.json missing at {wrapper_path}")

    if wrapper_path.exists():
        wrapper_text = wrapper_path.read_text(encoding="utf-8")
        if '"const": "1.0.0"' not in wrapper_text:
            failures.append('A7: v1.0.0 wrapper does not pin schema_version with {"const": "1.0.0"}')
        # I7 cold-start invariant: if-clause + then-branch both required
        # if-clause: baseline == null
        if '"baseline": { "type": "null" }' not in wrapper_text:
            failures.append('A7: v1.0.0 wrapper missing I7 if-clause (baseline=null)')
        # then-branch: last_seen == null AND legacy_migration == null
        if '"last_seen": { "type": "null" }' not in wrapper_text:
            failures.append('A7: v1.0.0 wrapper missing I7 then-branch (last_seen=null)')
        if '"legacy_migration": { "type": "null" }' not in wrapper_text:
            failures.append('A7: v1.0.0 wrapper missing I7 then-branch (legacy_migration=null)')

    return failures


# ---------------------------------------------------------------------------
# A8: Integration references — phase-0/final-phase/state-rendering mention drift-state.json
# ---------------------------------------------------------------------------


def check_a8_integration_references() -> list[str]:
    """Verify phase-0.md, final-phase.md, state-rendering.md reference drift-state.json."""
    failures = []
    targets = [
        ("plugin/references/phase-0.md", "Step 0.5 migration"),
        ("plugin/references/final-phase.md", "atomic write list"),
        ("plugin/references/state-rendering.md", "source list"),
    ]
    for rel_path, role in targets:
        full_path = REPO_ROOT / rel_path
        if not full_path.exists():
            failures.append(f"A8: {rel_path} not found")
            continue
        text = full_path.read_text(encoding="utf-8")
        if "drift-state.json" not in text:
            failures.append(f"A8: {rel_path} ({role}) does not mention 'drift-state.json'")
    return failures


# ---------------------------------------------------------------------------
# A9: Algorithm replacement — drift-state.md/output-format.md no longer carry legacy strings
# ---------------------------------------------------------------------------


def check_a9_algorithm_replacement() -> list[str]:
    """Verify reverse-scan algorithm vocabulary fully removed.

    drift-state.md must not contain 'reverse-chronological' or
    'first-anchor-wins'; output-format.md must not contain
    'since last /audit'.

    drift-state.md checks are case-insensitive (.lower()) because these terms
    can appear capitalized in prose headings; output-format.md check is
    case-sensitive — the slash in 'since last /audit' makes casing variation
    implausible.
    """
    failures = []
    drift_state_path = REPO_ROOT / "plugin" / "references" / "drift-state.md"
    output_format_path = REPO_ROOT / "plugin" / "skills" / "audit" / "references" / "output-format.md"

    if drift_state_path.exists():
        ds_text = drift_state_path.read_text(encoding="utf-8").lower()
        if "reverse-chronological" in ds_text:
            failures.append("A9: drift-state.md still contains 'reverse-chronological'")
        if "first-anchor-wins" in ds_text:
            failures.append("A9: drift-state.md still contains 'first-anchor-wins'")
    else:
        failures.append(f"A9: drift-state.md missing at {drift_state_path}")

    if output_format_path.exists():
        of_text = output_format_path.read_text(encoding="utf-8")
        if "since last /audit" in of_text:
            failures.append("A9: output-format.md still contains 'since last /audit'")
    else:
        failures.append(f"A9: output-format.md missing at {output_format_path}")

    return failures


# ---------------------------------------------------------------------------
# A10: Cross-field invariant I9 — baseline.first_observed_at == legacy_migration.source_changelog_anchor_run_id
# ---------------------------------------------------------------------------


def check_a10_i9_cross_field() -> list[str]:
    """Parse the migrated positive fixture; assert I9 cross-field equality.

    JSON Schema cannot enforce cross-field value equality (only conditional
    presence). I9 (baseline.first_observed_at == legacy_migration
    .source_changelog_anchor_run_id when legacy_migration is non-null) is
    closed by this runtime parse-based check.
    """
    failures = []
    migrated_path = (
        REPO_ROOT
        / "plugin"
        / "references"
        / "schemas"
        / "examples"
        / "drift-state.migrated.example.json"
    )
    if not migrated_path.exists():
        failures.append(f"A10: migrated example fixture missing at {migrated_path}")
        return failures

    try:
        data = json.loads(migrated_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        failures.append(f"A10: migrated fixture is not valid JSON: {exc}")
        return failures

    legacy_mig = data.get("legacy_migration")
    baseline = data.get("baseline")
    if legacy_mig is None:
        failures.append("A10: migrated fixture has legacy_migration=null; expected non-null object for I9 test")
        return failures
    if baseline is None:
        failures.append("A10: migrated fixture has baseline=null; invariant violation in fixture itself (baseline must be non-null when legacy_migration is non-null)")
        return failures

    first_obs = baseline.get("first_observed_at")
    source_anchor = legacy_mig.get("source_changelog_anchor_run_id")
    if first_obs != source_anchor:
        failures.append(
            f"A10: I9 violation in migrated fixture — "
            f"baseline.first_observed_at={first_obs!r}, "
            f"legacy_migration.source_changelog_anchor_run_id={source_anchor!r}"
        )
    return failures


# ---------------------------------------------------------------------------
# A_LOCK1: state_io.md §State-mutation lock — atomic mkdir + rename-aside
# ---------------------------------------------------------------------------


def check_a_lock1_short_lock_primitive() -> list[str]:
    """Verify state_io.md specifies the short-lock primitive.

    The §State-mutation lock section must use the atomic create-or-fail
    primitive (`os.mkdir`) and the atomic stale-reclaim path (`rename-aside`),
    and must NOT retain the retired racy check-then-act phrasing
    ('does not exist, write a fresh lock').
    """
    failures = []
    state_io_path = REPO_ROOT / "plugin" / "references" / "lib" / "state_io.md"

    if not state_io_path.exists():
        failures.append(f"A_LOCK1: state_io.md missing at {state_io_path}")
        return failures

    text = state_io_path.read_text(encoding="utf-8")

    if "os.mkdir" not in text:
        failures.append("A_LOCK1: state_io.md missing 'os.mkdir' acquire-gate primitive")
    if "rename-aside" not in text:
        failures.append("A_LOCK1: state_io.md missing 'rename-aside' stale-reclaim path")
    if "does not exist, write a fresh lock" in text:
        failures.append("A_LOCK1: state_io.md still contains retired check-then-act phrasing ('does not exist, write a fresh lock')")

    return failures


# ---------------------------------------------------------------------------
# A_LOCK2: final-phase.md/drift-state.md/merge_rules.md carry no old-contract
#          lock phrasing
# ---------------------------------------------------------------------------

# Old-contract phrasings the OCC rewrite must eliminate: "re-read under the
# lock", "merge under the lock", "under the lock ... merge", and "holding the
# lock ... re-read/merge". Precise, line-scoped, case-insensitive. By
# construction these patterns do NOT match the new-contract phrasings
# ("the lock is held only across the write burst", bare `§state-mutation-lock`
# cross-references, "under the state-mutation lock" applied to a write
# sub-step) or the unrelated word "threshold" — verified zero matches against
# state_io.md and phase-0.md (both intentionally OUT of scan scope; that check
# is only a non-over-broad sanity guard).
_A_LOCK2_PATTERNS = [
    re.compile(r"re-?read[^.\n]*\bunder\b[^.\n]*\block\b", re.IGNORECASE),
    re.compile(r"\bmerg(e|ing)\b[^.\n]*\bunder\b[^.\n]*\block\b", re.IGNORECASE),
    re.compile(r"\bunder\b[^.\n]*\block\b[^.\n]*\bmerg(e|ing)\b", re.IGNORECASE),
    re.compile(r"holding the lock[^.\n]*(re-?read|merg(e|ing))", re.IGNORECASE),
]


def check_a_lock2_no_old_contract_lock_phrasing() -> list[str]:
    """Verify final-phase.md, drift-state.md, and lib/merge_rules.md no longer
    encode the broken long-lock model (re-read + merge held under the
    state-mutation lock).

    Scoped to exactly these three files (NOT phase-0.md, NOT state_io.md).
    Evaluated per-line, case-insensitive; FAIL if ANY line of ANY of these
    files matches ANY old-contract pattern. The failure message names the
    offending file:line:pattern.
    """
    failures = []
    scoped = [
        REPO_ROOT / "plugin" / "references" / "final-phase.md",
        REPO_ROOT / "plugin" / "references" / "drift-state.md",
        REPO_ROOT / "plugin" / "references" / "lib" / "merge_rules.md",
    ]
    for path in scoped:
        if not path.exists():
            failures.append(f"A_LOCK2: {path} missing")
            continue
        lines = path.read_text(encoding="utf-8").splitlines()
        for lineno, line in enumerate(lines, start=1):
            for pat in _A_LOCK2_PATTERNS:
                if pat.search(line):
                    failures.append(
                        f"A_LOCK2: old-contract lock phrasing at "
                        f"{path.name}:{lineno}: matched /{pat.pattern}/ "
                        f"-- {line.strip()!r}"
                    )
    return failures


# ---------------------------------------------------------------------------
# A_LOCK3: phase-0.md Step 0.5 — marker preflight + genesis + torn-set recovery
# ---------------------------------------------------------------------------


def check_a_lock3_phase0_preflight_genesis_recovery() -> list[str]:
    """Verify phase-0.md Step 0.5 encodes the §8/§9 model.

    The rewritten Step 0.5 replaces the legacy MD→JSON migration/stale
    machine with the commit_id marker-preflight + genesis + torn-set
    recovery model. Assert the body carries the load-bearing vocabulary
    (case-insensitive substring):
      - "marker preflight"  — §8 preflight-before-schema-validation gate
      - "genesis"           — §8 all-4-absent ⇒ Step 0.5 mints first commit_id
      - "legacy-backup"     — §9 preserve-first quarantine before STOP
      - an "all 4 ... absent" phrase — the genesis classification rule
      - "partial" AND "torn" — the partial/mixed ⇒ torn-set branch
    """
    failures = []
    phase_0_path = REPO_ROOT / "plugin" / "references" / "phase-0.md"

    if not phase_0_path.exists():
        failures.append(f"A_LOCK3: phase-0.md missing at {phase_0_path}")
        return failures

    text = phase_0_path.read_text(encoding="utf-8")
    lowered = text.lower()

    if "marker preflight" not in lowered:
        failures.append("A_LOCK3: phase-0.md missing 'marker preflight' (§8 preflight gate)")
    if "genesis" not in lowered:
        failures.append("A_LOCK3: phase-0.md missing 'genesis' (§8 first commit_id mint)")
    if "legacy-backup" not in lowered:
        failures.append("A_LOCK3: phase-0.md missing 'legacy-backup' (§9 preserve-first quarantine)")
    # §8 genesis classification rule: a phrase conveying "all 4 ... absent".
    if not re.search(r"all 4[^.\n]*absent", lowered):
        failures.append("A_LOCK3: phase-0.md missing 'all 4 ... absent' genesis classification rule")
    # §8/§9 partial/mixed ⇒ torn-set branch.
    if "partial" not in lowered:
        failures.append("A_LOCK3: phase-0.md missing 'partial' (partial/mixed ⇒ torn branch)")
    if "torn" not in lowered:
        failures.append("A_LOCK3: phase-0.md missing 'torn' (torn-set recovery branch)")

    return failures


# ---------------------------------------------------------------------------
# A_LOCK4: drift-state.md forward-ref removed + state-rendering.md commit_id echo
# ---------------------------------------------------------------------------


def check_a_lock4_drift_state_pointer_and_commit_id_echo() -> list[str]:
    """Verify the Milestone-① cross-file reconciliation landed.

    drift-state.md MUST NOT contain the substring 'tracked separately'
    (the forward-reference was replaced by a pointer to the now-implemented
    short-lock + OCC commit_id mechanism). state-rendering.md MUST echo
    'commit_id' inside BOTH its config-changelog.md frontmatter block AND
    its state-summary.md header layout (commit_id is the per-write nonce;
    the summary echoes it but is a non-authoritative cache).
    """
    failures = []
    drift_state_path = REPO_ROOT / "plugin" / "references" / "drift-state.md"
    state_rendering_path = REPO_ROOT / "plugin" / "references" / "state-rendering.md"

    if not drift_state_path.exists():
        failures.append(f"A_LOCK4: drift-state.md missing at {drift_state_path}")
    else:
        ds_text = drift_state_path.read_text(encoding="utf-8")
        if "tracked separately" in ds_text:
            failures.append(
                "A_LOCK4: drift-state.md still contains forward-ref phrasing "
                "('tracked separately') — replace with pointer to the "
                "implemented short-lock + OCC commit_id mechanism"
            )

    if not state_rendering_path.exists():
        failures.append(f"A_LOCK4: state-rendering.md missing at {state_rendering_path}")
    else:
        sr_text = state_rendering_path.read_text(encoding="utf-8")
        changelog_match = re.search(
            r"## config-changelog\.md Format.*?(?=\n## )",
            sr_text,
            flags=re.DOTALL,
        )
        if not changelog_match:
            failures.append("A_LOCK4: state-rendering.md missing '## config-changelog.md Format' section")
        elif "commit_id" not in changelog_match.group(0):
            failures.append("A_LOCK4: state-rendering.md config-changelog.md frontmatter block does not echo 'commit_id'")

        layout_match = re.search(
            r"\*\*Layout\*\* \(exact\):.*?(?=\n### |\n## )",
            sr_text,
            flags=re.DOTALL,
        )
        if not layout_match:
            failures.append("A_LOCK4: state-rendering.md missing '**Layout** (exact):' state-summary.md header block")
        elif "commit_id" not in layout_match.group(0):
            failures.append("A_LOCK4: state-rendering.md state-summary.md header layout does not echo 'commit_id'")

    return failures


# ---------------------------------------------------------------------------
# A_LOCK5: drift-state derivation reads the commit_id marker under the OCC
# compare-and-commit (Step C) — POSITIVE companion to A9's negative
# ---------------------------------------------------------------------------


def check_a_lock5_marker_driven_derivation() -> list[str]:
    """Verify drift-state.md affirmatively encodes the marker/OCC-derivation
    contract (the POSITIVE side; A9 only asserts the absence of the retired
    'reverse-chronological'/'first-anchor-wins' vocab).

    The canonical drift-state is produced by reading/comparing the persisted
    `commit_id` marker under the OCC compare-and-commit (Final-Phase short
    lock — Step C of final-phase.md), NOT by a reverse-chronological
    changelog scan. This asserts the PRESENCE of that affirmative
    marker-driven phrasing in BOTH:
      - drift-state.md: the Step-A snapshot input + the Step-C
        compare-and-commit recovery write, and the explicit
        'computed under the Final-Phase short lock during the OCC
        compare-and-commit write path — Step C' derivation anchor.
      - final-phase.md: the Step C compare-and-commit definition and the
        OCC three-step framing (so the cross-referenced contract the
        drift-state.md anchor points at actually exists).

    FAILs if the affirmative marker/OCC-derivation phrasing is removed or
    weakened. NOT a duplicate of A9 (A9 = absence of bad vocab; A_LOCK5 =
    presence of the correct marker/OCC contract)."""
    failures = []
    drift_state_path = REPO_ROOT / "plugin" / "references" / "drift-state.md"
    final_phase_path = REPO_ROOT / "plugin" / "references" / "final-phase.md"

    if not drift_state_path.exists():
        failures.append(f"A_LOCK5: drift-state.md missing at {drift_state_path}")
    else:
        ds_text = drift_state_path.read_text(encoding="utf-8")
        # The derivation anchor: current_audit_run_id is computed under
        # the Final-Phase short lock during the OCC compare-and-commit write
        # path — Step C (durable phrasing, drift-state.md ~:56).
        if "Final-Phase short lock during the OCC compare-and-commit write path" not in ds_text:
            failures.append(
                "A_LOCK5: drift-state.md missing affirmative OCC-derivation anchor "
                "('Final-Phase short lock during the OCC compare-and-commit write path')"
            )
        # The Step-A snapshot input + Step-C compare-and-commit recovery write
        # (durable phrasing, drift-state.md ~:36): the canonical drift-state
        # is read into the snapshot and the Step C compare-and-commit writes
        # the recovered document — i.e. marker/OCC driven, not reverse scan.
        if "the Step C compare-and-commit writes the recovered document" not in ds_text:
            failures.append(
                "A_LOCK5: drift-state.md missing Step-C compare-and-commit "
                "recovery-write phrasing ('the Step C compare-and-commit "
                "writes the recovered document')"
            )
        # commit_id is the OCC observation marker the derivation path keys on.
        if "commit_id" not in ds_text:
            failures.append(
                "A_LOCK5: drift-state.md no longer references the 'commit_id' "
                "marker (the OCC compare-and-commit observation token)"
            )

    if not final_phase_path.exists():
        failures.append(f"A_LOCK5: final-phase.md missing at {final_phase_path}")
    else:
        fp_text = final_phase_path.read_text(encoding="utf-8")
        # The cross-referenced Step C contract must actually exist as the
        # compare-and-commit step under the short lock (final-phase.md ~:34).
        if "Step C — Compare-and-commit (short lock)" not in fp_text:
            failures.append(
                "A_LOCK5: final-phase.md missing the 'Step C — Compare-and-commit "
                "(short lock)' definition the drift-state.md anchor cross-references"
            )
        # The OCC three-step optimistic-concurrency framing (final-phase.md ~:11).
        if "optimistic concurrency" not in fp_text:
            failures.append(
                "A_LOCK5: final-phase.md no longer frames the write path as "
                "'optimistic concurrency' (OCC)"
            )

    return failures


# ---------------------------------------------------------------------------
# A_LOCK6: audit_run_id canonical-microsecond + monotonic-bump contract
# present in drift-state.md derivation subsection
# ---------------------------------------------------------------------------


def check_a_lock6_audit_run_id_canonical_contract() -> list[str]:
    """Verify drift-state.md carries the canonical-microsecond +
    monotonic-bump `current_audit_run_id` derivation contract.

    SCOPE (deliberate): this asserts the **OCC Step-C derivation-path** rule
    only — the rule that governs how `current_audit_run_id` is minted on the
    Final-Phase OCC compare-and-commit write path. It is NOT a repo-wide
    "every emitted audit_run_id, by any writer, is never bare-Z" invariant.
    The Phase-0.5 *migration* path legitimately still emits bare-`Z`
    second-precision audit_run_id and is intentionally out of derivation-anchor scope
    (ruled FAITHFUL-SCOPING). Accordingly the anchors below are taken from
    the derivation SUBSECTION ('current_audit_run_id derivation (canonical
    microsecond form + monotonic bump)') — deliberately NOT the standalone
    'every emitted audit_run_id ... never …Z, never second-precision'
    sentence, which read as a global invariant would contradict the
    (correct) migration path.

    FAILs if the scoped derivation-subsection contract is removed/weakened."""
    failures = []
    drift_state_path = REPO_ROOT / "plugin" / "references" / "drift-state.md"

    if not drift_state_path.exists():
        failures.append(f"A_LOCK6: drift-state.md missing at {drift_state_path}")
        return failures

    ds_text = drift_state_path.read_text(encoding="utf-8")

    # Anchor 1 — the derivation SUBSECTION heading (scopes the contract to
    # the OCC Step-C mint path; drift-state.md ~:54).
    if "`current_audit_run_id` derivation (canonical microsecond form + monotonic bump)" not in ds_text:
        failures.append(
            "A_LOCK6: drift-state.md missing the derivation subsection "
            "heading ('`current_audit_run_id` derivation (canonical "
            "microsecond form + monotonic bump)')"
        )
    # Anchor 2 — the literal canonical-form example (6 fractional digits +
    # explicit +00:00 offset; drift-state.md ~:58, inside the subsection).
    if "2026-05-18T09:00:00.000000+00:00" not in ds_text:
        failures.append(
            "A_LOCK6: drift-state.md missing the literal canonical-microsecond "
            "example '2026-05-18T09:00:00.000000+00:00'"
        )
    # Anchor 3 — the never-string-sort monotonic-bump rule (drift-state.md ~:59).
    if "Never string-sort" not in ds_text:
        failures.append(
            "A_LOCK6: drift-state.md missing the 'Never string-sort' "
            "monotonic-bump rule"
        )
    # Anchor 4 — the +1 microsecond bump quantum (drift-state.md ~:59).
    if "1 microsecond" not in ds_text:
        failures.append(
            "A_LOCK6: drift-state.md missing the '1 microsecond' monotonic "
            "bump quantum"
        )
    # Anchor 5 — the audit_run_id ⟂ commit_id independence clause: the bump
    # consults only audit_run_id, never commit_id (drift-state.md ~:60).
    if "Independent of `commit_id`" not in ds_text:
        failures.append(
            "A_LOCK6: drift-state.md missing the 'Independent of `commit_id`' "
            "ordering-carrier separation clause"
        )

    return failures


# ---------------------------------------------------------------------------
# A_LOCK7: verification gate — ANY plugin/skills/*/SKILL.md carries no
# old-contract long-lock phrasing nor retired Final-Phase Step-numbering
# ---------------------------------------------------------------------------

# The audit drift-aware design names three forbidden old-contract residues across
# state_io.md / final-phase.md / phase-0.md / drift-state.md / *any SKILL.md*.
# A_LOCK1-3 cover the four reference .md files; this gate closes the
# "any SKILL.md" sub-clause by globbing EVERY plugin/skills/*/SKILL.md
# (general, NOT audit-hardcoded — the gate applies to "any SKILL.md").
#
# Patterns (precise, per-line, case-insensitive — same philosophy as
# _A_LOCK2_PATTERNS):
#   1. "re-?read ... under ... lock"  — the retired "re-read under the
#      lock" canonical-read phrasing (the OCC model reads only in the
#      Step-A snapshot, never "under lock" held across merge).
#   2/3. "merge ... under ... lock" / "under ... lock ... merge" — the
#      retired long-lock merge (Step B is lock-free). Mirrors A_LOCK2
#      patterns 2-3 so a SKILL.md cannot reintroduce what final-phase.md
#      was scrubbed of. By construction these do NOT match the
#      new-contract write-side "under the state-mutation lock" applied to
#      an atomic-write sub-step (no re-read/merge co-occurrence).
#   4. Retired Final-Phase Step-numbering in the persist/mutation block:
#      bold "**Step N additions**" and the indented colon sub-step form
#      "**Step N**:" (N in 1-5). These denote the pre-OCC long-lock
#      "Step 1=write summary / Step 2=re-read / Step 3=mutate / Step 5=
#      atomic-write" model. Deliberately scoped so it does NOT match the
#      still-valid Common Phase 0 "**Step N override:**" stubs (Phase 0's
#      Step 2/3 are the learning-system Phase-0 steps, not Final-Phase
#      OCC steps) — "override" is not "additions" and the Phase-0 stubs
#      never use the bare "**Step N**:" colon form. Step A/B/C OCC
#      vocabulary (and OCC-annotated "Step N (captured in the Step A
#      snapshot)" cross-refs) are unaffected — they contain no bare
#      "**Step [1-5]**:" / "**Step [1-5] additions**".
#   5. Literal "Final Phase Step N" (N in 1-5) back-reference — the
#      retired numeric Final-Phase pointer (e.g. "Final Phase Step 1
#      fully skipped"); the OCC model refers to Final Phase Step A/B/C.
_A_LOCK7_PATTERNS = [
    re.compile(r"re-?read[^.\n]*\bunder\b[^.\n]*\block\b", re.IGNORECASE),
    re.compile(r"\bmerg(e|ing)\b[^.\n]*\bunder\b[^.\n]*\block\b", re.IGNORECASE),
    re.compile(r"\bunder\b[^.\n]*\block\b[^.\n]*\bmerg(e|ing)\b", re.IGNORECASE),
    re.compile(r"\*\*Step [12345]\*\*\s*:|\*\*Step [12345] additions", re.IGNORECASE),
    re.compile(r"\bFinal Phase Step [12345]\b", re.IGNORECASE),
]


def check_a_lock7_skill_md_no_old_contract() -> list[str]:
    """Verify NO plugin/skills/*/SKILL.md retains the broken long-lock
    model — the "any SKILL.md" verification-gate clause.

    Globs EVERY plugin/skills/*/SKILL.md (not just audit/ — the gate is
    general). Evaluated per-line, case-insensitive; FAIL if ANY line of
    ANY SKILL.md matches ANY old-contract pattern. The failure message
    names the offending file:line:pattern (UTF-8 stdout reconfigure in
    main() covers the em-dash/non-ASCII lines these messages echo).
    """
    failures = []
    skill_mds = sorted((REPO_ROOT / "plugin" / "skills").glob("*/SKILL.md"))
    if not skill_mds:
        failures.append(
            "A_LOCK7: no plugin/skills/*/SKILL.md found (glob matched nothing)"
        )
        return failures
    for path in skill_mds:
        lines = path.read_text(encoding="utf-8").splitlines()
        for lineno, line in enumerate(lines, start=1):
            for pat in _A_LOCK7_PATTERNS:
                if pat.search(line):
                    rel = path.relative_to(REPO_ROOT).as_posix()
                    failures.append(
                        f"A_LOCK7: old-contract long-lock phrasing at "
                        f"{rel}:{lineno}: matched /{pat.pattern}/ "
                        f"-- {line.strip()!r}"
                    )
    return failures


# ---------------------------------------------------------------------------
# Driver
# ---------------------------------------------------------------------------

CHECKS = [
    ("A1 drift state machine", check_a1_state_machine),
    ("A2 Step 0.5 .model write set", check_a2_write_point_1),
    ("A3 Install-integrity pre-Phase-0", check_a3_install_integrity),
    ("A4 Phase 5 Final triggers", check_a4_final_phase_triggers),
    ("A5 Drift block position", check_a5_drift_block_position),
    ("A6 Drift block format", check_a6_drift_block_format),
    ("A7 Schema integrity", check_a7_schema_integrity),
    ("A8 Integration references", check_a8_integration_references),
    ("A9 Algorithm replacement", check_a9_algorithm_replacement),
    ("A10 I9 cross-field", check_a10_i9_cross_field),
    ("A_LOCK1 state_io short-lock primitive", check_a_lock1_short_lock_primitive),
    ("A_LOCK2 no old-contract lock phrasing", check_a_lock2_no_old_contract_lock_phrasing),
    ("A_LOCK3 phase-0 preflight/genesis/recovery", check_a_lock3_phase0_preflight_genesis_recovery),
    ("A_LOCK4 drift-state pointer + commit_id echo", check_a_lock4_drift_state_pointer_and_commit_id_echo),
    ("A_LOCK5 marker-driven OCC derivation", check_a_lock5_marker_driven_derivation),
    ("A_LOCK6 audit_run_id canonical contract", check_a_lock6_audit_run_id_canonical_contract),
    ("A_LOCK7 any-SKILL.md no old-contract", check_a_lock7_skill_md_no_old_contract),
]


def main() -> int:
    # A_LOCK2 failure messages echo file lines verbatim, which contain
    # em-dashes / non-ASCII; the default Windows console codec (cp949)
    # raises UnicodeEncodeError on print. Force UTF-8 stdout/stderr.
    for _stream in (sys.stdout, sys.stderr):
        if hasattr(_stream, "reconfigure"):
            _stream.reconfigure(encoding="utf-8")

    all_failures: list[str] = []
    for label, check in CHECKS:
        try:
            failures = check()
        except Exception as exc:  # noqa: BLE001 — validator must never re-raise mid-run
            failures = [f"{label}: raised {exc!r}"]
        if failures:
            print(f"[FAIL] {label}")
            for f in failures:
                print(f"        - {f}")
            all_failures.extend(failures)
        else:
            print(f"[PASS] {label}")
    if all_failures:
        print(f"\n{len(all_failures)} assertion(s) failed", file=sys.stderr)
        return 1
    print("\nAll drift-aware assertions passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
