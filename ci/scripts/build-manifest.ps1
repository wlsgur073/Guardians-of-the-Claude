#!/usr/bin/env pwsh
# Generate eval-manifest.json describing the smoke-lane result for this commit.
$ErrorActionPreference = "Stop"
Set-Location "$PSScriptRoot/../.."

if (-not $env:SMOKE_PINNED_UTC) { $env:SMOKE_PINNED_UTC = "2026-04-14T00:00:00Z" }

python - @'
import hashlib
import json
import os
import subprocess
from pathlib import Path

env = os.environ.copy()
env["SMOKE_PINNED_UTC"] = env.get("SMOKE_PINNED_UTC", "2026-04-14T00:00:00Z")
proc = subprocess.run(
    ["python", ".github/scripts/check-smoke-fixtures.py"],
    capture_output=True,
    text=True,
    env=env,
)

results = {}
for line in proc.stdout.splitlines():
    if line.startswith("[PASS]"):
        passed = True
    elif line.startswith("[FAIL]"):
        passed = False
    else:
        continue
    rest = line.split("] ", 1)[1]
    name, _, msg = rest.partition(": ")
    results[name] = {"pass": passed, "msg": msg.strip()}

plugin_sha = subprocess.check_output(["git", "rev-parse", "HEAD"]).decode().strip()
manifest = {
    "manifest_version": "1.0.0",
    "release_tag": None,
    "plugin_sha": plugin_sha,
    "script_version": "smoke-runner v1.0.0",
    "fixtures_executed": list(results.keys()),
    "results": results,
    "pass_count": sum(1 for r in results.values() if r["pass"]),
    "fail_count": sum(1 for r in results.values() if not r["pass"]),
    "expected_diffs": [],
    "bundle_hash": "sha256:" + hashlib.sha256(
        json.dumps(results, sort_keys=True).encode()
    ).hexdigest(),
    "maintainer_signoff": None,
}
Path("eval-manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
print("eval-manifest.json written")
'@
exit $LASTEXITCODE
