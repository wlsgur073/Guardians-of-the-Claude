#!/usr/bin/env python3
"""config-resolve.sh atomic fixture runner.

Invokes plugin/references/lib/config-resolve.sh against ci/fixtures/config-resolve/
inputs (defaults + user + project injected via env vars) and compares the emitted
JSON to expected/effective.json (semantic JSON equality, key-order-independent).

Exit codes: 0 PASS | 1 FAIL (diff) | 2 setup error (missing file / jq / bash).
"""
from __future__ import annotations
import json, os, shutil, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
HELPER = ROOT / "plugin" / "references" / "lib" / "config-resolve.sh"
FIX = ROOT / "ci" / "fixtures" / "config-resolve"
DEFAULTS = FIX / "input" / "guardians-config.defaults.json"
USER_CFG = FIX / "input" / "user" / "guardians" / "config.json"
PROJECT_DIR = FIX / "input" / "project"
EXPECTED = FIX / "expected" / "effective.json"


def _find_bash() -> str | None:
    for c in (r"C:\Program Files\Git\bin\bash.exe", "bash"):
        if shutil.which(c) or Path(c).exists():
            return c
    return None


def main() -> int:
    for p in (HELPER, DEFAULTS, USER_CFG, EXPECTED):
        if not p.exists():
            print(f"[FATAL] missing: {p}", file=sys.stderr)
            return 2
    if not shutil.which("jq"):
        print("[FATAL] jq not on PATH (hard dependency)", file=sys.stderr)
        return 2
    bash = _find_bash()
    if not bash:
        print("[FATAL] bash not found", file=sys.stderr)
        return 2

    env = dict(os.environ)
    env["GUARDIANS_CONFIG_DEFAULTS"] = str(DEFAULTS)
    env["GUARDIANS_USER_CONFIG"] = str(USER_CFG)
    proc = subprocess.run(
        [bash, str(HELPER), str(PROJECT_DIR)],
        capture_output=True, text=True, env=env,
    )
    if proc.returncode != 0:
        print(f"[FAIL] helper exit {proc.returncode}: {proc.stderr.strip()}", file=sys.stderr)
        return 1
    try:
        got = json.loads(proc.stdout)
    except json.JSONDecodeError as exc:
        print(f"[FAIL] helper stdout is not JSON: {exc}\n{proc.stdout!r}", file=sys.stderr)
        return 1
    want = json.loads(EXPECTED.read_text(encoding="utf-8"))
    if got == want:
        print("[PASS] config-resolve")
        return 0
    print("[FAIL] config-resolve: output != expected", file=sys.stderr)
    print("GOT :", json.dumps(got, sort_keys=True, ensure_ascii=False), file=sys.stderr)
    print("WANT:", json.dumps(want, sort_keys=True, ensure_ascii=False), file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
