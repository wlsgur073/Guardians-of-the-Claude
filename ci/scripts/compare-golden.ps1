#!/usr/bin/env pwsh
# Debug helper: compare fixtures/<name>/expected/ against golden/<name>/ for
# maintainers authoring new fixtures.
$ErrorActionPreference = "Stop"
Set-Location "$PSScriptRoot/../.."

$names = @("migration", "beginner-path", "warm-start", "monorepo")
if ($args.Count -gt 0) { $names = $args }

$rc = 0
foreach ($name in $names) {
  $expected = "ci/fixtures/$name/expected"
  $golden = "ci/golden/$name"
  if (-not (Test-Path $expected) -or -not (Test-Path $golden)) {
    Write-Output "[SKIP] $name`: missing expected/ or golden/"
    continue
  }
  Write-Output "=== $name`: expected vs golden ==="
  $expectedFiles = Get-ChildItem -Recurse -File $expected | ForEach-Object { $_.FullName.Substring((Resolve-Path $expected).Path.Length + 1) }
  $goldenFiles = Get-ChildItem -Recurse -File $golden | ForEach-Object { $_.FullName.Substring((Resolve-Path $golden).Path.Length + 1) }
  $all = ($expectedFiles + $goldenFiles) | Sort-Object -Unique
  $mismatch = $false
  foreach ($rel in $all) {
    $e = Join-Path $expected $rel
    $g = Join-Path $golden $rel
    if (-not (Test-Path $e)) { Write-Output "missing in expected: $rel"; $mismatch = $true; continue }
    if (-not (Test-Path $g)) { Write-Output "missing in golden: $rel"; $mismatch = $true; continue }
    $eBytes = [System.IO.File]::ReadAllBytes($e)
    $gBytes = [System.IO.File]::ReadAllBytes($g)
    if (-not ([System.Linq.Enumerable]::SequenceEqual($eBytes, $gBytes))) {
      Write-Output "byte mismatch: $rel"
      $mismatch = $true
    }
  }
  if ($mismatch) {
    $rc = 1
  } else {
    Write-Output "[OK] $name"
  }
}
exit $rc
