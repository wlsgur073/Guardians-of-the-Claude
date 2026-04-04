#!/usr/bin/env bash
# setup-scenario.sh — Create a test project directory from a scenario definition
#
# Usage: ./setup-scenario.sh <scenario-id> [output-dir]
# Example: ./setup-scenario.sh python-fastapi-new /tmp/eval
#
# The script:
# 1. Reads the scenario definition from scenarios/<id>.md
# 2. Extracts the fixture name from YAML frontmatter
# 3. Copies the fixture to the output directory
# 4. Applies state modifications (existing = adds more source files)
# 5. Prints the ready path

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TEST_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

# --- Argument parsing ---
if [ $# -lt 1 ]; then
    echo "Usage: $(basename "$0") <scenario-id> [output-dir]"
    echo ""
    echo "Available scenarios:"
    ls "$TEST_DIR/scenarios/"*.md 2>/dev/null | while read -r f; do
        basename "$f" .md
    done | grep -v "^matrix$" | sort
    exit 1
fi

SCENARIO_ID="$1"
OUTPUT_BASE="${2:-/tmp/eval}"
SCENARIO_FILE="$TEST_DIR/scenarios/${SCENARIO_ID}.md"

if [ ! -f "$SCENARIO_FILE" ]; then
    echo "Error: Scenario file not found: $SCENARIO_FILE"
    exit 1
fi

# --- Parse YAML frontmatter ---
# Extract fixture and state from scenario file (POSIX-compatible, no yq/jq)
FIXTURE=""
STATE=""

in_frontmatter=false
while IFS= read -r line; do
    if [ "$line" = "---" ]; then
        if [ "$in_frontmatter" = true ]; then
            break
        fi
        in_frontmatter=true
        continue
    fi
    if [ "$in_frontmatter" = true ]; then
        case "$line" in
            fixture:*)
                FIXTURE="$(echo "$line" | sed 's/^fixture:[[:space:]]*//')"
                ;;
            state:*)
                STATE="$(echo "$line" | sed 's/^state:[[:space:]]*//')"
                ;;
        esac
    fi
done < "$SCENARIO_FILE"

if [ -z "$FIXTURE" ]; then
    echo "Error: No 'fixture' field found in frontmatter of $SCENARIO_FILE"
    exit 1
fi

FIXTURE_DIR="$TEST_DIR/fixtures/$FIXTURE"
if [ ! -d "$FIXTURE_DIR" ]; then
    echo "Error: Fixture directory not found: $FIXTURE_DIR"
    exit 1
fi

# --- Create output directory ---
OUTPUT_DIR="$OUTPUT_BASE/$SCENARIO_ID"

if [ -d "$OUTPUT_DIR" ]; then
    echo "Warning: Output directory exists, removing: $OUTPUT_DIR"
    rm -rf "$OUTPUT_DIR"
fi

mkdir -p "$OUTPUT_DIR"

# --- Copy fixture files ---
cp -r "$FIXTURE_DIR"/* "$OUTPUT_DIR/" 2>/dev/null || true
# Copy hidden files if any
cp -r "$FIXTURE_DIR"/.[!.]* "$OUTPUT_DIR/" 2>/dev/null || true

# --- Apply state modifications ---
if [ "$STATE" = "existing" ]; then
    # For existing projects, add more realistic source files
    # to simulate a project that has been developed but has no Claude Code config
    case "$FIXTURE" in
        python-*)
            mkdir -p "$OUTPUT_DIR/app/models" "$OUTPUT_DIR/app/routes"
            echo "# Database models" > "$OUTPUT_DIR/app/models/__init__.py"
            echo "# API routes" > "$OUTPUT_DIR/app/routes/__init__.py"
            echo ".env" > "$OUTPUT_DIR/.gitignore"
            ;;
        javascript-*)
            mkdir -p "$OUTPUT_DIR/src/components" "$OUTPUT_DIR/src/lib"
            echo "// Shared utilities" > "$OUTPUT_DIR/src/lib/utils.js"
            echo "node_modules/" > "$OUTPUT_DIR/.gitignore"
            ;;
        rust-*)
            mkdir -p "$OUTPUT_DIR/src/commands"
            echo "// CLI subcommands" > "$OUTPUT_DIR/src/commands/mod.rs"
            echo "target/" > "$OUTPUT_DIR/.gitignore"
            ;;
        java-*)
            mkdir -p "$OUTPUT_DIR/src/main/java/com/example/service"
            echo "// Business logic" > "$OUTPUT_DIR/src/main/java/com/example/service/AppService.java"
            echo "target/" > "$OUTPUT_DIR/.gitignore"
            ;;
        c-cmake|cpp-cmake)
            mkdir -p "$OUTPUT_DIR/src/utils" "$OUTPUT_DIR/tests"
            echo "// Utility functions" > "$OUTPUT_DIR/src/utils/helpers.c"
            echo "build/" > "$OUTPUT_DIR/.gitignore"
            ;;
        go-*)
            mkdir -p "$OUTPUT_DIR/internal/config"
            echo "// App configuration" > "$OUTPUT_DIR/internal/config/config.go"
            ;;
        monorepo)
            echo "node_modules/" > "$OUTPUT_DIR/.gitignore"
            ;;
    esac
fi

echo "Ready: $OUTPUT_DIR"
echo "  Fixture: $FIXTURE"
echo "  State: ${STATE:-new}"
echo ""
echo "Next steps:"
echo "  1. Open this directory in Claude Code"
echo "  2. Run /generate or /audit"
echo "  3. Evaluate against rubric and record results"
