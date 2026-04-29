#!/usr/bin/env pwsh
# Preflight schema probe — Windows companion (invokes Python script).
$python = if ($env:PYTHON) { $env:PYTHON } else { "python" }
& $python "$PSScriptRoot/preflight-schema.py" $args
exit $LASTEXITCODE
