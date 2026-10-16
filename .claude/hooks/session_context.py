#!/usr/bin/env python3
"""SessionStart: give the agent a short orientation (branch, recent commits, pending changes).

Whatever this prints on stdout is added to the session context.
"""

import subprocess
import sys


def git(*args: str) -> str:
    try:
        return subprocess.run(["git", *args], capture_output=True, text=True, timeout=10).stdout.strip()
    except (OSError, subprocess.TimeoutExpired):
        return ""


def main() -> int:
    branch = git("branch", "--show-current") or "(detached or not a git repo)"
    log = git("log", "--oneline", "-5")
    changes = [line for line in git("status", "--porcelain").splitlines() if line.strip()]
    lines = [f"Current branch: {branch}"]
    if branch in ("main", "master"):
        lines.append("You are on the default branch: create a feature branch before committing.")
    if log:
        lines += ["Recent commits:", *[f"  {entry}" for entry in log.splitlines()]]
    if changes:
        lines.append(f"Uncommitted changes in {len(changes)} file(s).")
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    sys.exit(main())
