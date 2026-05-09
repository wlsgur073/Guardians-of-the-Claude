# A'-briefing n=5 Sampling — Data Unavailable

**Status**: Attempt closed (data-source gap, not a sampling result)
**Created**: 2026-05-09
**Scope**: Documents an attempt at the n=5 hypothesis-generation sampling specified as A'-briefing's defer-unblock condition (per Round 1 Proposal A' Prerequisites and `decision-backlog.md` Defer bucket). Reports a data-source gap rather than a classification result.

---

## What Was Attempted

Round 1 Proposal A' Prerequisites specify a two-stage causal sampling to gate A'-briefing adoption:

> Stage 1 — hypothesis generation (n=5). Pull 5 recent `/audit` runs where subagent findings were rejected as false positive. Classify each by cause:
> - Briefing-gap (subagent lacked context the parent had)
> - Model hallucination (subagent had sufficient context but fabricated)
> - Criterion ambiguity (subagent read correctly but interpreted rule differently)
> - Other

Stage 1's data requirement: 5 incidents where a `/audit` subagent finding was rejected as false positive in real execution, with enough context to classify each by cause.

---

## Data Sources Surveyed

| Source | What it contains | Suitable for n=5 cause classification? |
|---|---|---|
| `test/results/2026-04-05-audit-*.md` (10 files) | Simulated `/audit` runs, eval author grades simulated output against expected results known in advance | **No** — simulations have no subagent dispatch; the False Positives rubric (1-5 scale) measures simulation accuracy against the author's expectation, not real dispatch failures |
| `test/log/2026040*-*.md` (5 files) | Eval workflow logs (setup, batch completion) | No — record workflow, not per-finding rejection |
| memory `feedback_subagent_verification.md` (cited in R1 as recording 38-50% false-positive rate across n=14 raw claims in 2 batches) | Per Round 1 line 67, the canonical source for the prior rate evidence | **Not present** in current memory store. Only `feedback_subagent_staging_split.md` exists (covers subagent git-index race conditions, different topic). The cited memory is renamed, deleted, or never persisted across machines. |
| Real `/audit` session transcripts | Per-claim subagent dispatch + rejection annotation | Outside repo scope; no centralized capture mechanism currently exists |

Across all four sources, no canonical record of `/audit` subagent-finding rejections classified by cause is available.

---

## Findings

1. **The R1 Prerequisite is unverifiable from current repo state.** A'-briefing's defer condition (n=5 sampling, then n=15-20 decision gate) cannot be evaluated because the input data does not exist in a form that supports causal classification.

2. **Eval rubrics measure simulation accuracy, not real-execution failures.** The False Positives dimension in `test/rubrics/audit-rubric.md` grades whether the eval author's simulated `/audit` output matches expected results, which is correctness against a known-good state, not real subagent dispatch noise. Even result files scoring below 5/5 on False Positives (e.g., `audit-go-web-overconfigured` at 4/5) capture the eval author's judgment about a simulation, not an incident with subagent context to classify.

3. **The canonical citation is broken.** The R1 proposal cites `feedback_subagent_verification.md` as the source of the 38-50% false-positive rate; that memory is not present in the current memory store. Any claim about historical false-positive rates derived from this memory is no longer traceable in this repo's state.

---

## Implications for A'-briefing

The defer condition for A'-briefing is not "we have data and need to classify it" but rather "we have neither data nor a capture mechanism that would produce classifiable data". This is a different kind of defer than the backlog's wording suggests.

| Aspect | Old framing (R1 + backlog) | Revised framing (post this attempt) |
|---|---|---|
| Defer reason | n=5 sampling not yet performed | No data source supports n=5 cause classification |
| Unblock prerequisite | Run the sampling | **Establish a data-capture mechanism first**, then sample |

Possible data-capture routes (each is a separate piece of work, larger than n=5 sampling itself):

1. Add per-subagent-finding rejection logging to the `/audit` Phase 3.7 Output Validation contract so future runs accumulate cause-classifiable incidents over time.
2. Restore or replace `feedback_subagent_verification.md` with the original n=14 cases (if any persist in chat history outside this repo) and classify those.
3. Run a deliberate `/audit` session against a known-broken fixture with capture instrumentation, then classify the resulting subagent-finding rejections.

Each route is a meaningful piece of work; none is in scope for this current cycle.

---

## Recommendation

Update `decision-backlog.md` A'-briefing row to record the data-source gap as the operative defer reason. A'-briefing remains in the Defer bucket; the n=5 step itself does not need re-attempting until a data-capture mechanism is in place. This document is the discovery artifact justifying the row update.

---

## References

- Round 1 Proposal A' Prerequisites — `anthropic-engineering-insights-review.md` § "Proposal A' — Subagent Briefing + Deterministic Post-check"
- `decision-backlog.md` — A'-briefing row in Defer bucket
- `test/rubrics/audit-rubric.md` — false-positive rubric definition (1-5 simulation-accuracy scale)
- `test/results/` — 10 surveyed audit eval simulation files
- memory `feedback_subagent_staging_split.md` — adjacent (but topically different) subagent memory; the cited `feedback_subagent_verification.md` is not present
