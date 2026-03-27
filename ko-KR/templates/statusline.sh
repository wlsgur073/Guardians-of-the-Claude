#!/bin/bash
input=$(cat)

MODEL=$(echo "$input" | jq -r '.model.display_name')
DIR=$(echo "$input" | jq -r '.workspace.current_dir')
PCT=$(echo "$input" | jq -r '.context_window.used_percentage // 0' | cut -d. -f1)
DURATION_MS=$(echo "$input" | jq -r '.cost.total_duration_ms // 0')
FIVE_H=$(echo "$input" | jq -r '.rate_limits.five_hour.used_percentage // empty')

CYAN='\033[36m'; GREEN='\033[32m'; YELLOW='\033[33m'; RED='\033[31m'
GOLD='\033[38;5;222m'; RESET='\033[0m'

# 컨텍스트 사용량에 따라 바 색상 선택
if [ "$PCT" -ge 90 ]; then BAR_COLOR="$RED"
elif [ "$PCT" -ge 70 ]; then BAR_COLOR="$YELLOW"
else BAR_COLOR="$GREEN"; fi

FILLED=$((PCT / 10)); EMPTY=$((10 - FILLED))
printf -v FILL "%${FILLED}s"; printf -v PAD "%${EMPTY}s"
BAR="${FILL// /█}${PAD// /░}"

MINS=$((DURATION_MS / 60000)); SECS=$(((DURATION_MS % 60000) / 1000))

BRANCH=""
git rev-parse --git-dir > /dev/null 2>&1 && BRANCH=" 🌿 $(git branch --show-current 2>/dev/null)"

DIR_NAME=$(basename "${DIR//\\//}")

# 라인 1: 모델 + 5시간 사용량 바
# 5시간 사용량 바 (마젠타 팔레트, 컨텍스트의 초록/노랑/빨강과 구별)
USAGE=""
if [ -n "$FIVE_H" ]; then
    FIVE_H_INT=$(printf '%.0f' "$FIVE_H")
    if [ "$FIVE_H_INT" -ge 90 ]; then UC="$RED"
    elif [ "$FIVE_H_INT" -ge 70 ]; then UC="$YELLOW"
    else UC="$GOLD"; fi
    UF=$((FIVE_H_INT / 10)); UE=$((10 - UF))
    printf -v UFILL "%${UF}s"; printf -v UPAD "%${UE}s"
    UBAR="${UFILL// /█}${UPAD// /░}"
    USAGE=" | ⚡ ${UC}${UBAR}${RESET} ${FIVE_H_INT}%"
fi
printf '%b\n' "${CYAN}[$MODEL]${RESET}${USAGE} | 📁 ${DIR_NAME}"

# 라인 2: git 브랜치 + 컨텍스트 바 + 소요 시간
printf '%b\n' "${BRANCH:+$BRANCH | }${BAR_COLOR}${BAR}${RESET} ${PCT}% | ⏱️ ${MINS}m ${SECS}s"
