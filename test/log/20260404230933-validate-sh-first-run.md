# validate.sh First Run — Bug Discovery and Fix Log

**Date:** 2026-04-04 23:09
**Action:** First execution of validate.sh against main repository
**Result:** 4 script bugs found and fixed, 3 real repo issues discovered

---

## Script Bugs Found

### Bug 1: `set -e` + `pipefail` + `grep` early termination

- **Symptom:** Script stopped after Check 2 with no error message
- **Cause:** `grep` returns exit code 1 when no match is found. Combined with `set -euo pipefail`, any grep with no matches caused the entire script to exit immediately.
- **Fix:** Removed `set -e`. The script now uses `set -uo pipefail` only. Error tracking is handled via temp file instead of relying on exit codes.
- **Lesson:** Never use `set -e` in scripts that call `grep` on content that may not match. This is a well-known bash pitfall but easy to overlook.

### Bug 2: Pipeline subshell variable isolation

- **Symptom:** ERRORS counter always reported 0 despite `fail()` being called inside loops
- **Cause:** `find ... | while read` runs the while loop in a subshell. Variable modifications (`ERRORS=$((ERRORS + 1))`) inside the subshell do not propagate to the parent shell.
- **Fix:** Replaced `find ... | while read` with `while read ... done < <(find ...)` (process substitution) so the loop runs in the current shell. Additionally, error tracking moved to a temp file (`mktemp`) that persists across subshell boundaries.
- **Lesson:** In bash, any command on the right side of a pipe runs in a subshell. Use process substitution `< <(cmd)` when you need to modify variables inside a loop that reads from a command.

### Bug 3: `sed` flag misplacement

- **Symptom:** `sed: can't read p: No such file or directory` (hundreds of times)
- **Cause:** `sed -n 's/pattern/replacement/' p` — the space before `p` made sed interpret `p` as a filename argument instead of the print flag.
- **Fix:** Changed to `sed -n 's/pattern/replacement/p'` (flag attached to the s command).
- **Lesson:** In `sed -n`, the `p` flag must be part of the substitution command (`s///p`), not a separate argument.

### Bug 4: False positive on links inside inline code

- **Symptom:** `FAIL: plugin/skills/audit/SKILL.md: broken link to 'audit-history.md'`
- **Cause:** The link checker extracted `[text](path)` patterns from all content, including backtick-wrapped code examples like `` `- [Audit history](audit-history.md)` ``. These are not real links but instructions for users.
- **Fix:** Added `awk` preprocessing to strip fenced code blocks and inline code before link extraction: `awk '/^```/{skip=!skip; next} !skip{gsub(/`[^`]*`/,""); print}'`
- **Lesson:** Markdown link extraction must account for code blocks and inline code. Raw regex matching on the full file content produces false positives.

---

## Real Repository Issues Found

After all script bugs were fixed, 3 genuine validation failures remained:

| File | Issue | Details |
|------|-------|---------|
| docs/guides/claude-md-guide.md | Line count exceeded | 146 lines (limit: 130) |
| docs/guides/effective-usage-guide.md | Line count exceeded | 136 lines (limit: 130) |
| docs/guides/mcp-guide.md | Line count exceeded | 133 lines (limit: 130) |

These violate the rule in CLAUDE.md: "Guides in docs/guides/ should stay concise — most under ~130 lines."

---

## Final Validation Result

```
138 checks passed, 3 checks failed, 0 warnings
```

## Takeaways for Future Development

1. **Always run scripts on real data before considering them done.** All 4 bugs were invisible until the script processed actual repository files.
2. **bash + grep + pipefail is a known hazard.** Consider this combination a default risk in any new shell script.
3. **Subshell variable isolation is the #1 bash scripting pitfall.** Prefer process substitution over pipes when loop bodies modify state.
4. **Link checkers need code-awareness.** Markdown files contain code examples that include link-like syntax — naive regex extraction will always produce false positives.
