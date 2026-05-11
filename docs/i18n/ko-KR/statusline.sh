#!/bin/bash
input=$(cat)

MODEL=$(echo "$input" | jq -r '.model.display_name')
DIR=$(echo "$input" | jq -r '.workspace.current_dir')
PCT=$(echo "$input" | jq -r '.context_window.used_percentage // 0' | cut -d. -f1)
DURATION_MS=$(echo "$input" | jq -r '.cost.total_duration_ms // 0')
FIVE_H=$(echo "$input" | jq -r '.rate_limits.five_hour.used_percentage // empty')
FIVE_H_RESET=$(echo "$input" | jq -r '.rate_limits.five_hour.resets_at // empty')

CYAN='\033[36m'; GREEN='\033[32m'; YELLOW='\033[33m'; RED='\033[31m'
GOLD='\033[38;5;222m'; RESET='\033[0m'

# Pick bar color based on context usage
if [ "$PCT" -ge 90 ]; then BAR_COLOR="$RED"
elif [ "$PCT" -ge 70 ]; then BAR_COLOR="$YELLOW"
else BAR_COLOR="$GREEN"; fi

FILLED=$((PCT / 10)); EMPTY=$((10 - FILLED))
printf -v FILL "%${FILLED}s"; printf -v PAD "%${EMPTY}s"
BAR="${FILL// /█}${PAD// /░}"

MINS=$((DURATION_MS / 60000)); SECS=$(((DURATION_MS % 60000) / 1000))

BRANCH=""
git rev-parse --git-dir > /dev/null 2>&1 && BRANCH=" 🌿 $(git branch --show-current 2>/dev/null)"

# Build display path: full path with ~ substitution, abbreviate if too long
FULL_PATH="${DIR//\\//}"
# Convert Windows drive letter (C:/) to Unix format (/c/)
if [[ "$FULL_PATH" =~ ^([A-Za-z]):/ ]]; then
    DRIVE_LOWER=$(echo "${BASH_REMATCH[1]}" | tr 'A-Z' 'a-z')
    FULL_PATH="/${DRIVE_LOWER}${FULL_PATH:2}"
fi

# Track whether the path is actually home-relative so the truncated form
# doesn't misleadingly prefix non-home paths with ~/
IS_HOME=0
if [[ "$FULL_PATH" == "$HOME"* ]]; then
    DISPLAY_PATH="~${FULL_PATH#$HOME}"
    IS_HOME=1
else
    DISPLAY_PATH="$FULL_PATH"
fi

MAX_PATH_LEN=20
if [ ${#DISPLAY_PATH} -gt $MAX_PATH_LEN ]; then
    CURRENT=$(basename "$DISPLAY_PATH")
    PARENT=$(basename "$(dirname "$DISPLAY_PATH")")
    if [ "$IS_HOME" -eq 1 ]; then
        DISPLAY_PATH="~/…/${PARENT}/${CURRENT}"
    else
        DISPLAY_PATH="…/${PARENT}/${CURRENT}"
    fi
fi

# Line 1: current dir + model + 5h rate limit bar
# 5h usage bar (magenta palette, distinct from context's green/yellow/red)
USAGE=""
if [ -n "$FIVE_H" ]; then
    FIVE_H_INT=$(printf '%.0f' "$FIVE_H")
    if [ "$FIVE_H_INT" -ge 90 ]; then UC="$RED"
    elif [ "$FIVE_H_INT" -ge 70 ]; then UC="$YELLOW"
    else UC="$GOLD"; fi
    UF=$((FIVE_H_INT / 10)); UE=$((10 - UF))
    printf -v UFILL "%${UF}s"; printf -v UPAD "%${UE}s"
    UBAR="${UFILL// /█}${UPAD// /░}"
    RESET_STR=""
    if [ -n "$FIVE_H_RESET" ]; then
        NOW=$(date +%s)
        REMAINING=$((FIVE_H_RESET - NOW))
        if [ $REMAINING -gt 0 ]; then
            RESET_H=$((REMAINING / 3600))
            RESET_M=$(((REMAINING % 3600) / 60))
            RESET_STR=" (${RESET_H}h ${RESET_M}m)"
        else
            RESET_STR=" (reset)"
        fi
    fi
    USAGE=" | ⚡ ${UC}${UBAR}${RESET} ${FIVE_H_INT}%${RESET_STR}"
fi
printf '%b\n' "📁 ${DISPLAY_PATH} | ${CYAN}[$MODEL]${RESET}${USAGE}"

# Line 2: git branch + context bar + duration
printf '%b\n' "${BRANCH:+$BRANCH | }📊 ${BAR_COLOR}${BAR}${RESET} ${PCT}% | ⏱️ ${MINS}m ${SECS}s"
