# SubagentStop hook -- appends one JSONL line per subagent completion.
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
$OutFile = Join-Path $OutDir "subagent-log.jsonl"
New-Item -ItemType Directory -Force -Path $OutDir | Out-Null

$StdinJson = [Console]::In.ReadToEnd()
try {
    $Payload = $StdinJson | ConvertFrom-Json
} catch {
    $Payload = [PSCustomObject]@{}
}

$Record = [ordered]@{
    ts = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
    event = "subagent_stop"
    session_id = if ($Payload.session_id) { $Payload.session_id } else { $null }
    agent_id = if ($Payload.agent_id) { $Payload.agent_id } else { $null }
    agent_type = if ($Payload.agent_type) { $Payload.agent_type } else { $null }
    cwd = (Get-Location).Path
}

$Line = $Record | ConvertTo-Json -Compress
Add-Content -Path $OutFile -Value $Line -Encoding UTF8
exit 0
