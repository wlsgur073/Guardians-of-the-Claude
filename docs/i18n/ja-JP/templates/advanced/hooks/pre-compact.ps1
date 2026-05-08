# PreCompact hook -- captures pre-compact snapshot for post-compaction debugging.
# Trigger: per-compaction (manual or auto). Output: file-only.
# Always exits 0 -- observability hook does not block compaction.

$ErrorActionPreference = 'Stop'
trap { exit 0 }

# Force UTF-8 on stdout so non-ASCII characters survive Windows PowerShell 5.1's
# default OEM/Windows-1252 output encoding. Strings in this file stay ASCII-only
# as a second defense, since PS 5.1 also reads BOM-less .ps1 source files with
# the system ANSI codepage.
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

$ProjectDir = if ($env:CLAUDE_PROJECT_DIR) { $env:CLAUDE_PROJECT_DIR } else { (Get-Location).Path }
$OutDir = Join-Path $ProjectDir ".claude/local/hooks"
$OutFile = Join-Path $OutDir "pre-compact-snapshot.md"
New-Item -ItemType Directory -Force -Path $OutDir | Out-Null

$StdinJson = [Console]::In.ReadToEnd()
try {
    $Payload = $StdinJson | ConvertFrom-Json
    $SessionId = if ($Payload.session_id) { $Payload.session_id } else { "(unknown)" }
    $Trigger = if ($Payload.trigger) { $Payload.trigger } else { "(unspecified)" }
} catch {
    $SessionId = "(unknown)"
    $Trigger = "(unspecified)"
}

$Timestamp = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
$PwdVal = (Get-Location).Path
$Branch = try { (git branch --show-current 2>$null).Trim() } catch { "" }
if (-not $Branch) {
    $Branch = try { (git rev-parse --short HEAD 2>$null).Trim() } catch { "(not a git repo)" }
    if (-not $Branch) { $Branch = "(not a git repo)" }
}
$GitStatus = try { (git status --porcelain 2>$null) } catch { "(not a git repo)" }
if (-not $GitStatus) { $GitStatus = "(clean)" }
$RecentCommits = try { (git log -5 --oneline 2>$null) } catch { "(no commits)" }
if (-not $RecentCommits) { $RecentCommits = "(no commits)" }

$DenyRe = '(?i)(KEY|TOKEN|SECRET|PASSWORD|PASSWD|CREDENTIAL|AUTH|BEARER|DATABASE_URL|DB_URL|REDIS_URL|MONGO_URI|AWS_|GITHUB_|STRIPE_|ANTHROPIC_|OPENAI_|API_)'
$AllowRe = '^(NODE_ENV|PORT|CI|LANG|LC_.*|TZ|PWD|CLAUDE_PROJECT_DIR|CLAUDE_CODE_REMOTE)$'
$EnvLines = @()
foreach ($e in (Get-ChildItem env:)) {
    $name = $e.Name
    if ($name -cmatch $AllowRe) {
        if ($name -match $DenyRe) { continue }
        $EnvLines += "$name=$($e.Value)"
    }
}
$EnvOut = $EnvLines -join "`n"

$Content = @"
# Pre-Compact Snapshot

**Timestamp**: $Timestamp
**Session ID**: $SessionId
**Trigger**: $Trigger
**Working dir**: $PwdVal
**Branch**: $Branch

## Git Status
``````
$GitStatus
``````

## Recent Commits
``````
$RecentCommits
``````

## Environment (sanitized)
``````
$EnvOut
``````
"@

Set-Content -Path $OutFile -Value $Content -Encoding UTF8 -NoNewline
exit 0
