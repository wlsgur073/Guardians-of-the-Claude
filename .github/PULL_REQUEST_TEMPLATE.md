## Summary

What does this PR change and why?

## Changes

-
-

## Test plan

- [ ] Local validator sweep passes (`check-json-schemas.py`, `check-readme-badge-sync.py`, `check-changelog-anchor-slug.py`, `check-smoke-fixtures.py` — see CLAUDE.md "Verifying Changes Locally")
- [ ] If touching `plugin/`, `templates/`, or `ci/`: smoke fixtures verified
- [ ] If touching a `docs/guides/` file: line-count check (`(Get-Content file).Count` or `wc -l`) within the guide's documented limit

## Checklist

- [ ] If touching a guide or template file: `version:` field in YAML frontmatter bumped (each file has its own semver, see CLAUDE.md "Contribution Rules")
- [ ] CHANGELOG entry added under `## [Unreleased]` if user-facing
