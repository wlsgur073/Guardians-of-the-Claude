#!/usr/bin/env bash
# Pre-commit / PreToolUse secret + injection scan — a thin, REPLACEABLE wrapper.
# It does NOT implement scanning; it delegates to a mature tool you choose.
# Pick the tool with SECRET_SCANNER (default: gitleaks). Disable via PROJECT_HOOK_PROFILE=off.
set -u

[ "${PROJECT_HOOK_PROFILE:-standard}" = "off" ] && exit 0

SCANNER="${SECRET_SCANNER:-gitleaks}"
command -v "$SCANNER" >/dev/null 2>&1 || {
  echo "secret-scan-hook: '$SCANNER' not found — install it or set SECRET_SCANNER. Skipping (non-blocking)." >&2
  exit 0
}

case "$SCANNER" in
  gitleaks)   "$SCANNER" detect --no-banner --redact ;;
  trufflehog) "$SCANNER" git "file://$PWD" --fail --no-update ;;
  *)          "$SCANNER" ;;   # custom scanner: must exit non-zero on findings
esac
status=$?

[ "$status" -eq 0 ] && exit 0
echo "BLOCK: secret/injection scan found issues (scanner: $SCANNER). Resolve or add a reviewed allowlist entry before committing." >&2
exit 2
