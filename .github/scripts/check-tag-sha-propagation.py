#!/usr/bin/env python3
"""Verify a local annotated tag SHA matches the remote refs/tags/<tag> SHA.

Compares:
    local  = `git rev-parse v<tag>`           (annotated tag object SHA)
    remote = `git ls-remote --tags origin v<tag>`  (refs/tags/v<tag> object SHA, NOT peeled ^{})

Mismatch indicates the annotation didn't propagate — the remote may have only
the lightweight commit ref. Re-push with `git push origin refs/tags/v<tag>` to fix.

Usage:
    python check-tag-sha-propagation.py v2.17.2

Env override (for CI / non-interactive):
    TAG=v2.17.2 python check-tag-sha-propagation.py

Exit codes:
    0 - SHAs match
    1 - mismatch or git command failure
    2 - tag argument missing (soft-skip in CI when no tag context)
"""
from __future__ import annotations

import os
import re
import subprocess
import sys

TAG_RE = re.compile(r"^v[0-9]+\.[0-9]+\.[0-9]+$")


def run(cmd: list[str]) -> tuple[int, str]:
    proc = subprocess.run(cmd, capture_output=True, text=True)
    return proc.returncode, (proc.stdout + proc.stderr).strip()


def main() -> int:
    tag = (sys.argv[1] if len(sys.argv) > 1 else os.environ.get("TAG", "")).strip()
    if not tag:
        print("SKIP - no tag argument or TAG env var; soft-skip")
        return 2
    if not TAG_RE.match(tag):
        print(f"FAIL - tag {tag!r} does not match expected vX.Y.Z format")
        return 1

    rc, local = run(["git", "rev-parse", tag])
    if rc != 0:
        print(f"FAIL - `git rev-parse {tag}` failed: {local}")
        return 1

    rc, remote_raw = run(["git", "ls-remote", "--tags", "origin", tag])
    if rc != 0:
        print(f"FAIL - `git ls-remote --tags origin {tag}` failed: {remote_raw}")
        return 1
    if not remote_raw:
        print(f"FAIL - tag {tag} not found on remote origin")
        return 1

    # ls-remote output: "<sha>\trefs/tags/<tag>" — pick the line WITHOUT the ^{} suffix
    remote_sha = ""
    for line in remote_raw.splitlines():
        sha, _, ref = line.partition("\t")
        if ref == f"refs/tags/{tag}":
            remote_sha = sha.strip()
            break
    if not remote_sha:
        print(f"FAIL - could not extract refs/tags/{tag} SHA from ls-remote output:")
        print(remote_raw)
        return 1

    if local != remote_sha:
        print(f"FAIL - annotation did not propagate")
        print(f"       local : {local}")
        print(f"       remote: {remote_sha}")
        print(f"       fix   : git push origin refs/tags/{tag}")
        return 1

    print(f"PASS - {tag} annotated SHA propagated ({local[:12]}...)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
