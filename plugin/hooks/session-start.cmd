@echo off
REM Guardians-of-the-Claude — Windows onboarding fallback.
REM Emits onboarding JSON only when bash is NOT available.
REM On Linux/macOS, this script is never invoked (cmd interpreter absent).
where bash >NUL 2>&1
if %ERRORLEVEL% EQU 0 exit /b 0
echo {"hookSpecificOutput":{"hookEventName":"SessionStart","additionalContext":"Guardians-of-the-Claude plugin requires bash, but it was not found on this Windows system. To enable the plugin: install Git for Windows (https://git-scm.com/download/win) which provides Git Bash, or set up WSL. After installation, restart Claude Code. Until then, the plugin's SessionStart digest will not be emitted."}}
exit /b 0
