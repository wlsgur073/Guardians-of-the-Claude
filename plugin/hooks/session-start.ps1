# plugin/hooks/session-start.ps1 -- PowerShell mirror of session-start.sh
#
# Same gate-then-stack architecture as the bash version.
# Read-only over canonical state. Source filter + lock-based dual-entry de-duplication.
# Runs on bare Windows (PowerShell 5.1+ ships with every Windows 10+ install),
# so users without Git Bash or WSL still get the SessionStart auto-guidance.
# On non-Windows systems `powershell` is typically absent, so this hook entry
# exits with ENOENT and Claude Code silently skips it -- the bash entry wins.

$ErrorActionPreference = 'Stop'

# Force UTF-8 on stdout so non-ASCII characters in additionalContext survive
# Windows PowerShell 5.1's default OEM/Windows-1252 output encoding.
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

$ProfilePath = ".claude/.plugin-cache/guardians-of-the-claude/local/profile.json"
$RecsPath = ".claude/.plugin-cache/guardians-of-the-claude/local/recommendations.json"
$LockDir = ".claude/.plugin-cache/guardians-of-the-claude/local/.session-start.lock"

# Threshold constants (kept in sync with session-start.sh).
$N_Days = 7      # unresolved age threshold
$K_Count = 3     # unresolved pending_count threshold
$M_Declines = 3  # repeated-decline threshold

# Wall clock with SMOKE_PINNED_UTC override for deterministic fixture runs.
if ($env:SMOKE_PINNED_UTC) {
    try {
        $NowUtc = [int][DateTimeOffset]::Parse(
            $env:SMOKE_PINNED_UTC,
            [System.Globalization.CultureInfo]::InvariantCulture,
            [System.Globalization.DateTimeStyles]::AssumeUniversal -bor [System.Globalization.DateTimeStyles]::AdjustToUniversal
        ).ToUnixTimeSeconds()
    } catch {
        Write-Error "SMOKE_PINNED_UTC parse failed: $($env:SMOKE_PINNED_UTC)"
        exit 1
    }
} else {
    $NowUtc = [int][DateTimeOffset]::UtcNow.ToUnixTimeSeconds()
}

# Source filter (script-side; hooks.json matcher is the load-bearing first-line filter).
# Fail-open default: if stdin is empty or malformed, default to startup.
$Source = "startup"
try {
    $Stdin = [Console]::In.ReadToEnd()
    if ($Stdin) {
        $Parsed = $Stdin | ConvertFrom-Json -ErrorAction SilentlyContinue
        if ($Parsed -and $Parsed.source) { $Source = $Parsed.source }
    }
} catch { }
if ($Source -in @("clear", "compact")) { exit 0 }

# Stale lock cleanup -- skip if mtime read fails (rare race).
if (Test-Path $LockDir -PathType Container) {
    try {
        $LockMtime = (Get-Item $LockDir -Force).LastWriteTimeUtc
        $LockEpoch = [int][DateTimeOffset]::new($LockMtime, [TimeSpan]::Zero).ToUnixTimeSeconds()
        $LockAge = $NowUtc - $LockEpoch
        if ($LockAge -gt 30) { Remove-Item $LockDir -Force -ErrorAction SilentlyContinue }
    } catch { }  # mtime read race -- let mkdir below decide
}

# Parent dir ensure (in case skills haven't created local/ yet).
$LockParent = Split-Path -Parent $LockDir
if (-not (Test-Path $LockParent)) {
    New-Item -ItemType Directory -Path $LockParent -Force -ErrorAction SilentlyContinue | Out-Null
}

# Atomic lock acquisition via try/catch IOException -- race-free per Windows CreateDirectoryW.
# Do NOT rely on -ErrorAction SilentlyContinue + $? -- that has a check-after-create gap.
try {
    New-Item -ItemType Directory -Path $LockDir -ErrorAction Stop | Out-Null
} catch [System.IO.IOException] {
    exit 0  # sibling holds lock
} catch {
    exit 0  # any other failure -- silent
}

try {
    # Case 1: No Claude Code configuration at all (PRESERVED VERBATIM)
    if (-not (Test-Path "CLAUDE.md") -and -not (Test-Path ".claude/settings.json")) {
        Write-Output @'
{
  "hookSpecificOutput": {
    "hookEventName": "SessionStart",
    "additionalContext": "This project has no Claude Code configuration yet. The guardians-of-the-claude plugin is installed -- suggest the user run /guardians-of-the-claude:create to set up CLAUDE.md and .claude/ configuration through a guided interview."
  }
}
'@
        exit 0
    }

    # Case 2: Configuration exists but no profile yet (PRESERVED VERBATIM)
    if (-not (Test-Path $ProfilePath)) {
        Write-Output @'
{
  "hookSpecificOutput": {
    "hookEventName": "SessionStart",
    "additionalContext": "Claude Code configuration exists but no project profile has been generated yet. Running /guardians-of-the-claude:audit will generate a project profile for more accurate recommendations across all skills."
  }
}
'@
        exit 0
    }

    # Drift family -- 4 reasons in priority order.
    function Get-DriftLine {
        $primary = ""
        $primaryMsg = ""
        $otherCount = 0

        # Reason 1: legacy_mtime -- any of 23 monitored manifests newer than profile.
        $manifests = @(
            "package.json","package-lock.json","pnpm-lock.yaml","yarn.lock",
            "pnpm-workspace.yaml","lerna.json","nx.json","turbo.json","rush.json",
            "tsconfig.json",
            "pyproject.toml","poetry.lock","uv.lock","requirements.txt",
            "go.mod","go.sum",
            "Cargo.toml","Cargo.lock",
            "pom.xml",
            "Gemfile","Gemfile.lock",
            ".mcp.json",".claude/settings.json"
        )
        $profileMtime = (Get-Item $script:ProfilePath).LastWriteTime
        foreach ($f in $manifests) {
            if ((Test-Path $f) -and (Get-Item $f).LastWriteTime -gt $profileMtime) {
                $primary = "legacy_mtime"
                $primaryMsg = "$f newer than profile"
                break
            }
        }

        # Profile object for remaining reasons.
        $profileObj = $null
        try { $profileObj = Get-Content $script:ProfilePath -Raw -ErrorAction Stop | ConvertFrom-Json -ErrorAction Stop } catch { }

        # Reason 2: schema_version_mismatch -- expected 1.2.0.
        $expectedSv = "1.2.0"
        $profileSv = if ($profileObj.schema_version) { $profileObj.schema_version } else { "" }
        if ($profileSv -and $profileSv -ne $expectedSv) {
            if (-not $primary) {
                $primary = "schema_version_mismatch"
                $primaryMsg = "profile.schema_version $profileSv expected $expectedSv"
            } else { $otherCount++ }
        }

        # Reason 3: ecosystem_change -- workspace declaration present but profile records single_project.
        $monorepoDetected = $false
        if ($profileObj.project_structure.monorepo_detection.detected -eq $true) { $monorepoDetected = $true }
        $hasWorkspace = $false
        foreach ($wf in @("pnpm-workspace.yaml","lerna.json","nx.json","turbo.json","rush.json")) {
            if (Test-Path $wf) { $hasWorkspace = $true; break }
        }
        if ($hasWorkspace -and -not $monorepoDetected) {
            if (-not $primary) {
                $primary = "ecosystem_change"
                $primaryMsg = "workspace declaration present but profile records single_project"
            } else { $otherCount++ }
        }

        # Reason 4: scoring_contract_bump -- expected audit-score-v4.1.0.
        $expectedScore = "audit-score-v4.1.0"
        $profileScoreAck = if ($profileObj.claude_code_configuration_state.scoring_model_ack.contract_id) {
            $profileObj.claude_code_configuration_state.scoring_model_ack.contract_id
        } else { "" }
        if ($profileScoreAck -and $profileScoreAck -ne $expectedScore) {
            if (-not $primary) {
                $primary = "scoring_contract_bump"
                $primaryMsg = "profile.scoring_model_ack $profileScoreAck expected $expectedScore"
            } else { $otherCount++ }
        }

        if (-not $primary) { return "" }
        if ($otherCount -gt 0) {
            return "Drift: $primaryMsg (+$otherCount other drift signals); run /guardians-of-the-claude:audit."
        }
        return "Drift: $primaryMsg; run /guardians-of-the-claude:audit."
    }

    # Unresolved family -- PENDING with age >= N OR pending_count >= K. STALE excluded.
    function Get-UnresolvedLine {
        if (-not (Test-Path $script:RecsPath)) { return "" }
        try {
            $recsObj = Get-Content $script:RecsPath -Raw -ErrorAction Stop | ConvertFrom-Json -ErrorAction Stop
        } catch { return "" }
        if (-not $recsObj.recommendations) { return "" }

        $matching = @()
        foreach ($r in $recsObj.recommendations) {
            if ($r.status -ne "PENDING") { continue }
            $firstSeenEpoch = [int][DateTimeOffset]::Parse(
                $r.first_seen,
                [System.Globalization.CultureInfo]::InvariantCulture,
                [System.Globalization.DateTimeStyles]::AssumeUniversal -bor [System.Globalization.DateTimeStyles]::AdjustToUniversal
            ).ToUnixTimeSeconds()
            $ageDays = [Math]::Floor(($script:NowUtc - $firstSeenEpoch) / 86400)
            if ($ageDays -ge $script:N_Days -or $r.pending_count -ge $script:K_Count) {
                $matching += $r | Add-Member -NotePropertyName _ageDays -NotePropertyValue $ageDays -PassThru -Force
            }
        }
        if ($matching.Count -eq 0) { return "" }

        $sorted = $matching | Sort-Object first_seen
        $oldest = $sorted[0]
        $count = $matching.Count
        # ConvertFrom-Json auto-converts ISO 8601 strings to [DateTime] in PS 5.1+ and 7+,
        # and `-split "T"` on a DateTime stringifies via current culture (e.g. "04/29/2026 00:00:00" on en-US).
        # Force ISO short-date (YYYY-MM-DD) output regardless of input shape for parity with the bash hook.
        $oldestDate = if ($oldest.first_seen -is [DateTime]) {
            $oldest.first_seen.ToUniversalTime().ToString("yyyy-MM-dd", [System.Globalization.CultureInfo]::InvariantCulture)
        } else {
            ([string]$oldest.first_seen -split "T")[0]
        }
        return "Open recommendations: $count pending since $oldestDate; oldest: $($oldest.id) (seen pending $($oldest.pending_count) times)."
    }

    # Repeated-decline family -- DECLINED with decline_count >= M. STALE excluded.
    # PENDING recs with historical decline_count > 0 do NOT fire (status guard).
    function Get-RepeatedDeclineLine {
        if (-not (Test-Path $script:RecsPath)) { return "" }
        try {
            $recsObj = Get-Content $script:RecsPath -Raw -ErrorAction Stop | ConvertFrom-Json -ErrorAction Stop
        } catch { return "" }
        if (-not $recsObj.recommendations) { return "" }

        $matching = @()
        foreach ($r in $recsObj.recommendations) {
            if ($r.status -ne "DECLINED") { continue }
            $dc = if ($null -ne $r.decline_count) { $r.decline_count } else { 0 }
            if ($dc -ge $script:M_Declines) {
                $matching += $r | Add-Member -NotePropertyName _dc -NotePropertyValue $dc -PassThru -Force
            }
        }
        if ($matching.Count -eq 0) { return "" }

        $sorted = $matching | Sort-Object @{Expression={$_._dc};Descending=$true}, @{Expression={$_.last_seen};Descending=$true}
        $top = $sorted[0]
        return "Repeated declines: $($top.id) declined $($top._dc) times total; consider acknowledging or updating manually."
    }

    $DriftLine = Get-DriftLine
    $UnresolvedLine = Get-UnresolvedLine
    $RepeatedDeclineLine = Get-RepeatedDeclineLine

    if ($DriftLine -or $UnresolvedLine -or $RepeatedDeclineLine) {
        $body = "Guardians: project state needs attention."
        if ($DriftLine)            { $body += "`n- $DriftLine" }
        if ($UnresolvedLine)       { $body += "`n- $UnresolvedLine" }
        if ($RepeatedDeclineLine)  { $body += "`n- $RepeatedDeclineLine" }

        # Char cap defense -- truncate at 1997 + sentinel if somehow over 2000 chars.
        if ($body.Length -gt 2000) {
            $body = $body.Substring(0, 1997) + "..."
            Write-Error "Digest body exceeded 2000 chars; truncated"
        }

        $output = @{
            hookSpecificOutput = @{
                hookEventName = "SessionStart"
                additionalContext = $body
            }
        } | ConvertTo-Json -Depth 4 -Compress
        Write-Output $output
    }
} finally {
    Remove-Item $LockDir -Force -ErrorAction SilentlyContinue
}

exit 0
