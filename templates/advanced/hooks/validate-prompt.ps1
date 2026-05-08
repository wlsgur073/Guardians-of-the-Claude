# validate-prompt.ps1 -- Windows PowerShell port of validate-prompt.sh
#
# Warns when user prompt mentions migration-related keywords. Companion
# entry in .claude/settings.json mirrors the dual-entry pattern from
# plugin/hooks/hooks.json so this advanced-template hook works on bare
# Windows shells without Git Bash or WSL. Behavior matches the bash
# version: same regex, same warning lines, always exits 0 (advisory,
# not blocking).

$ErrorActionPreference = 'Stop'

# Force UTF-8 on stdout so non-ASCII characters survive Windows PowerShell
# 5.1's default OEM/Windows-1252 encoding. Source stays ASCII-only as a
# second defense (PS 5.1 reads BOM-less .ps1 files with the system ANSI
# codepage). Same hardening as plugin/hooks/session-start.ps1.
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

# Skip if bash is also on PATH -- the bash hook entry will handle the
# warning, avoiding duplicate output on dual-interpreter systems (e.g.,
# Windows with Git Bash + PowerShell). The bash entry takes precedence
# when both exist; this entry only runs as a fallback on bare shells.
if (Get-Command bash -ErrorAction SilentlyContinue) {
    exit 0
}

# Read all of stdin as a single string. $input is a lazy enumerator over
# pipeline objects and would split multi-line prompts; ReadToEnd matches
# `cat` byte-for-byte.
$PromptText = [Console]::In.ReadToEnd()

if ($PromptText -imatch 'migration|migrate|schema change|alter table|drop table') {
    Write-Output "Migration-related keywords detected. Remember:"
    Write-Output "  - Migration files are protected (PreToolUse hook blocks edits)"
    Write-Output "  - Run 'npm run migrate' to apply existing migrations"
    Write-Output "  - Create new migrations with 'npm run migrate:create <name>'"
    exit 0
}

exit 0
