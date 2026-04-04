#!/usr/bin/env bash
# validate.sh — Static structural validation for the main repository
#
# Usage: ./validate.sh [repo-root]
# Default: validates the repository root (two levels up from this script)
#
# Checks:
# 1. YAML frontmatter required fields
# 2. Internal link targets exist
# 3. Guide line count limits
# 4. JSON file validity
# 5. Deprecated keyword absence
# 6. Template TaskFlow references

set -uo pipefail
# Note: set -e intentionally omitted — grep returning no matches (exit 1)
# combined with pipefail would kill the script prematurely.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="${1:-$(cd "$SCRIPT_DIR/../.." && pwd)}"

# Use a temp file for error tracking to avoid subshell variable issues.
# Pipelines (cmd | while read) run in subshells — variable changes inside
# don't propagate to the parent shell.
ERROR_LOG=$(mktemp)
trap 'rm -f "$ERROR_LOG"' EXIT

CHECKS=0
WARNINGS=0

pass() { CHECKS=$((CHECKS + 1)); }
fail() {
    CHECKS=$((CHECKS + 1))
    echo "$1" >> "$ERROR_LOG"
    echo "  FAIL: $1"
}
warn() { WARNINGS=$((WARNINGS + 1)); echo "  WARN: $1"; }

# ============================================================
# Check 1: YAML frontmatter required fields
# ============================================================
echo "[1/6] Checking YAML frontmatter..."

# Guide files need: title, description, version
for f in "$REPO_ROOT"/docs/guides/*.md; do
    [ -f "$f" ] || continue
    filename="$(basename "$f")"

    has_title=$(head -20 "$f" | grep -c "^title:" || true)
    has_desc=$(head -20 "$f" | grep -c "^description:" || true)
    has_version=$(head -20 "$f" | grep -c "^version:" || true)

    if [ "$has_title" -eq 0 ]; then fail "docs/guides/$filename: missing 'title' in frontmatter"; fi
    if [ "$has_desc" -eq 0 ]; then fail "docs/guides/$filename: missing 'description' in frontmatter"; fi
    if [ "$has_version" -eq 0 ]; then fail "docs/guides/$filename: missing 'version' in frontmatter"; fi
    if [ "$has_title" -gt 0 ] && [ "$has_desc" -gt 0 ] && [ "$has_version" -gt 0 ]; then pass; fi
done

# Skill files need: name, description
for f in "$REPO_ROOT"/plugin/skills/*/SKILL.md; do
    [ -f "$f" ] || continue
    skill_name="$(basename "$(dirname "$f")")"

    has_name=$(head -10 "$f" | grep -c "^name:" || true)
    has_desc=$(head -10 "$f" | grep -c "^description:" || true)

    if [ "$has_name" -eq 0 ]; then fail "plugin/skills/$skill_name/SKILL.md: missing 'name' in frontmatter"; fi
    if [ "$has_desc" -eq 0 ]; then fail "plugin/skills/$skill_name/SKILL.md: missing 'description' in frontmatter"; fi
    if [ "$has_name" -gt 0 ] && [ "$has_desc" -gt 0 ]; then pass; fi
done

# ============================================================
# Check 2: Internal link targets exist
# ============================================================
echo "[2/6] Checking internal links..."

# Collect all markdown files (excluding fixtures, .git, node_modules)
while IFS= read -r mdfile; do
    dir="$(dirname "$mdfile")"
    # Extract markdown links: [text](relative-path)
    # Skip http(s), mailto, and anchor-only links
    while IFS= read -r match; do
        # Extract path from [text](path) — get content between ( and )
        link=$(echo "$match" | sed -n 's/.*](\([^)]*\)).*/\1/p')
        [ -z "$link" ] && continue

        # Skip external links and anchors
        case "$link" in
            http://*|https://*|mailto:*|\#*) continue ;;
        esac

        # Strip anchor fragment
        link="${link%%#*}"
        [ -z "$link" ] && continue

        target="$dir/$link"
        if [ ! -e "$target" ]; then
            rel_path="${mdfile#$REPO_ROOT/}"
            fail "$rel_path: broken link to '$link'"
        else
            pass
        fi
    # Strip fenced code blocks and inline code before extracting links.
    # Without this, [text](path) inside backticks produces false positives.
    done <<< "$(awk '/^```/{skip=!skip; next} !skip{gsub(/`[^`]*`/,""); print}' "$mdfile" | grep -o '\[[^]]*\]([^)]*)' 2>/dev/null || true)"
done < <(find "$REPO_ROOT" -name "*.md" \
    -not -path "*/.git/*" \
    -not -path "*/node_modules/*" \
    -not -path "*/test/fixtures/*" \
    -not -path "*/test/results/*" \
    -not -path "*/test/scenarios/*" 2>/dev/null)

# ============================================================
# Check 3: Guide line count limits
# ============================================================
echo "[3/6] Checking guide line counts..."

for f in "$REPO_ROOT"/docs/guides/*.md; do
    [ -f "$f" ] || continue
    filename="$(basename "$f")"
    line_count=$(wc -l < "$f")

    if [ "$filename" = "advanced-features-guide.md" ]; then
        limit=200
    else
        limit=130
    fi

    if [ "$line_count" -gt "$limit" ]; then
        fail "docs/guides/$filename: $line_count lines (limit: $limit)"
    else
        pass
    fi
done

# CLAUDE.md line count (root)
if [ -f "$REPO_ROOT/CLAUDE.md" ]; then
    claude_lines=$(wc -l < "$REPO_ROOT/CLAUDE.md")
    if [ "$claude_lines" -gt 200 ]; then
        fail "CLAUDE.md: $claude_lines lines (limit: 200)"
    else
        pass
    fi
fi

# ============================================================
# Check 4: JSON file validity
# ============================================================
echo "[4/6] Checking JSON validity..."

while IFS= read -r jsonfile; do
    [ -z "$jsonfile" ] && continue
    rel_path="${jsonfile#$REPO_ROOT/}"
    if python -m json.tool "$jsonfile" > /dev/null 2>&1; then
        pass
    elif python3 -m json.tool "$jsonfile" > /dev/null 2>&1; then
        pass
    else
        fail "$rel_path: invalid JSON"
    fi
done < <(find "$REPO_ROOT" -name "*.json" \
    -not -path "*/node_modules/*" \
    -not -path "*/.git/*" \
    -not -path "*/test/fixtures/*" 2>/dev/null)

# ============================================================
# Check 5: Deprecated keyword absence
# ============================================================
echo "[5/6] Checking for deprecated keywords..."

# allowed-tools is deprecated in skill frontmatter
for f in "$REPO_ROOT"/plugin/skills/*/SKILL.md; do
    [ -f "$f" ] || continue
    skill_name="$(basename "$(dirname "$f")")"

    if head -20 "$f" | grep -q "allowed-tools"; then
        fail "plugin/skills/$skill_name/SKILL.md: contains deprecated 'allowed-tools' in frontmatter"
    else
        pass
    fi
done

# allowed-tools in template skill files
while IFS= read -r f; do
    [ -z "$f" ] && continue
    rel_path="${f#$REPO_ROOT/}"
    if head -20 "$f" | grep -q "allowed-tools"; then
        fail "$rel_path: contains deprecated 'allowed-tools'"
    else
        pass
    fi
done < <(find "$REPO_ROOT/templates" -name "SKILL.md" 2>/dev/null)

# ============================================================
# Check 6: Template TaskFlow references
# ============================================================
echo "[6/6] Checking TaskFlow references in templates..."

for f in "$REPO_ROOT"/templates/*/CLAUDE.md; do
    [ -f "$f" ] || continue
    rel_path="${f#$REPO_ROOT/}"

    if grep -qi "taskflow" "$f"; then
        pass
    else
        fail "$rel_path: does not reference 'TaskFlow'"
    fi
done

# ============================================================
# Summary
# ============================================================
ERRORS=0
if [ -f "$ERROR_LOG" ]; then
    ERRORS=$(wc -l < "$ERROR_LOG")
fi

echo ""
echo "=============================="
echo "Validation Results"
echo "=============================="
echo "Checks passed: $((CHECKS - ERRORS))"
echo "Checks failed: $ERRORS"
echo "Warnings:      $WARNINGS"
echo "=============================="

if [ "$ERRORS" -gt 0 ]; then
    echo "RESULT: FAIL"
    exit 1
else
    echo "RESULT: PASS"
    exit 0
fi
