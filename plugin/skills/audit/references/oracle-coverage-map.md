# `/audit` Oracle Coverage Map

**Status**: Active (discovery artifact informing later pilot proposals)
**Created**: 2026-05-09
**Scope**: Maps `/audit`'s 14 rules (Tiers 1–3) against the 11 `.github/scripts/check-*.py` CI validators to surface the upper bound of deterministic verifiability available from this repo's CI surface.

---

## Summary Finding

**Zero direct oracle coverage.** None of the 11 CI scripts oracles any of the 14 `/audit` rules, because the two sets target different domains:

- **CI scripts** validate this repository's own content (frontmatter parity across EN/i18n, JSON schema conformance for our manifests, smoke fixtures byte-diff, README badge sync, etc.).
- **`/audit` rules** evaluate user projects' Claude Code configurations (CLAUDE.md content quality, deny patterns, hook portability, agent diversity, etc.).

The deterministic portions of `/audit` rules are **rule-internal** (file existence, string match, JSON parse, line count, Glob match) — they do not need an external oracle because they ARE the deterministic check. The remaining surface (severity grading, scope decisions, conditional recommendations) is LLM-judgment-bound.

---

## Rule × CI-Script Mapping

| Rule (audit) | What is checked | External CI oracle | Rule-internal determinism |
| --- | --- | --- | --- |
| T1.1 CLAUDE.md existence | file existence | none | inherent |
| T1.2 Test command | string match | none | inherent |
| T1.3 Build command | string match | none | inherent |
| T1.4 Project overview | heuristic on first 20 lines | none | partial (line scan deterministic; "vague" LLM) |
| T2.1 Sensitive file protection | settings.json parse + deny pattern presence + op coverage | none† | inherent (parse + pattern scan); "weaker protection" LLM |
| T2.2 Security rules | filename/keyword search | none | partial (presence deterministic; "security-relevant surface" heuristic) |
| T2.3 Hook config quality | field presence + portability + event-type | none‡ | partial (field presence deterministic; "inappropriate" LLM) |
| T3.1 Directory references | Glob check on extracted paths | none | inherent |
| T3.2 CLAUDE.md length | line count | none | inherent |
| T3.3 Command availability | manifest + tool-config existence | none | inherent |
| T3.4 Rules path validation | Glob match on rule `paths:` frontmatter | none | inherent |
| T3.5 Agent configuration quality | YAML field presence + diversity | none§ | partial (presence deterministic; diversity-adequacy LLM) |
| T3.6 MCP configuration | `.mcp.json` existence + dep cross-check | none | inherent |
| T3.7 Environment variable documentation | env var scan + CLAUDE.md cross-ref | none | partial (pattern detection deterministic; "sufficient documentation" LLM) |

† `check-json-schemas.py` validates this repo's manifests against canonical Claude Code schemas; validation *logic* (JSON parse + schema match) is reusable conceptually, but the script does not run on user projects.
‡ `check-hook-script-parity.py` checks `.sh` ↔ `.ps1` companion presence in `templates/advanced/hooks/`. Different concern (cross-platform parity) than T2.3 (config field quality).
§ `check-skill-stability.py` validates SKILL.md frontmatter contract for OUR plugin skills (same YAML-field-presence pattern as T3.5 but applied to a different file type / scope).

---

## CI Script Inventory (none oracle `/audit` rules)

| Script | Validates |
| --- | --- |
| check-frontmatter-parity.py | EN/i18n guide & template `version:` lockstep |
| check-i18n-parity.py | `docs/i18n/{ko-KR,ja-JP}/` directory mirror of EN |
| check-json-schemas.py | `plugin.json`, `marketplace.json`, `templates/*/.claude/settings.json` |
| check-recommendation-registry.py | `recommendations.json` shape + ISO date validity |
| check-skill-stability.py | SKILL.md frontmatter contract for the four plugin skills |
| check-changelog-anchor-slug.py | CHANGELOG `[X.Y.Z]` heading slug consistency |
| check-hook-script-parity.py | `.sh` ↔ `.ps1` companion presence in `templates/advanced/hooks/` |
| check-qa-report-shape.py | `/audit` QA report OUTPUT shape (not rule-correctness) |
| check-readme-badge-sync.py | `README.md` shields.io version badge ↔ `plugin.json` |
| check-smoke-fixtures.py | `ci/golden/` byte-diff regression for plugin output |
| check-tag-sha-propagation.py | annotated tag SHA matches origin after push |

---

## Implications for Downstream Proposals

### Reframe of "Oracle check" terminology

The Round 4 proposal originally framed CI scripts as the oracle for `/audit`'s deterministic post-check. The mapping above shows that framing is incoherent — CI scripts and `/audit` rules target different domains. The right framing is **rule-internal determinism**: each `/audit` rule contains its own deterministic check (file existence, regex match, Glob, JSON parse), and the post-check re-runs that check on the subagent's claim before surfacing.

### Implication for `deterministic_tests` grader (K-schema)

A YAML rubric `deterministic_tests` grader for `/audit` should not invoke CI scripts. Instead, it should re-execute the rule's own deterministic primitives (`Read` the cited file, re-run the rule's pattern matcher) against the subagent's claim. CI scripts remain useful only as oracles for **this repo's own integrity** (frontmatter parity, schema validity, etc.), not as a general-purpose validator pool.

### Implication for reliability strategy

Rule-internal determinism is already at near-100% coverage of the deterministic surface — the rules ARE the determinism. The reliability gap lives in three judgment-heavy surfaces:

1. **Severity grading** (PASS / PARTIAL / FAIL / MINIMAL) — multiple severity levels per rule, LLM-bound
2. **Scope detection** (e.g., "is this project security-relevant?") — heuristic decision at the start of T2.2
3. **Conditional recommendations** ("consider extracting…", "consider differentiating models…") — recommendation-heavy

These are the LLM-judge cluster's domain (tracked in `docs/ROADMAP.md` "Revisit Triggers" → "LLM-as-judge evals for `/audit` rubrics" row, blocked on a 20–50-item human-scored calibration set). The matrix confirms why that cluster cannot be skipped — deterministic coverage of rule-internal checks does not improve reliability on the judgment-heavy surface above it.

---

## References

- `checks/{t1-foundation,t2-protection,t3-optimization}.md` — full `/audit` rule definitions
- `.github/scripts/check-*.py` — the 11 CI validators
