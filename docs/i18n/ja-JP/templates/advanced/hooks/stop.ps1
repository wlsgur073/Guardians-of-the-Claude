# Stop hook -- appends one entry per turn (Claude finishes responding).
# Note: Stop fires per-turn, not per-session-end.
# Always exits 0 -- observability hook does not block.

$ErrorActionPreference = 'Stop'
trap { exit 0 }

# Force UTF-8 on stdout so non-ASCII characters survive Windows PowerShell 5.1's
# default OEM/Windows-1252 output encoding. Strings in this file stay ASCII-only
# as a second defense, since PS 5.1 also reads BOM-less .ps1 source files with
# the system ANSI codepage.
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

$ProjectDir = if ($env:CLAUDE_PROJECT_DIR) { $env:CLAUDE_PROJECT_DIR } else { (Get-Location).Path }
$OutDir = Join-Path $ProjectDir ".claude/local/hooks"
$OutFile = Join-Path $OutDir "turn-log.md"
New-Item -ItemType Directory -Force -Path $OutDir | Out-Null

$StdinJson = [Console]::In.ReadToEnd()
try {
    $Payload = $StdinJson | ConvertFrom-Json
    $SessionId = if ($Payload.session_id) { $Payload.session_id } else { "(unknown)" }
} catch {
    $SessionId = "(unknown)"
}

$Timestamp = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
$PwdVal = (Get-Location).Path
$Branch = try { (git branch --show-current 2>$null).Trim() } catch { "" }
if (-not $Branch) {
    $Branch = try { (git rev-parse --short HEAD 2>$null).Trim() } catch { "(not a git repo)" }
    if (-not $Branch) { $Branch = "(not a git repo)" }
}
$ModifiedCount = try { (git diff --name-only HEAD 2>$null | Measure-Object -Line).Lines } catch { 0 }
if (-not $ModifiedCount) { $ModifiedCount = 0 }

$Entry = @"
## Turn $Timestamp

- **Session ID**: $SessionId
- **Working dir**: $PwdVal
- **Branch**: $Branch
- **Modified files (vs HEAD)**: $ModifiedCount

---

"@

Add-Content -Path $OutFile -Value $Entry -Encoding UTF8
exit 0
