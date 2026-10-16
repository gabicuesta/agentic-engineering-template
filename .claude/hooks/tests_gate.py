#!/usr/bin/env python3
"""Stop: if Python files changed, run the tests before the agent may finish.

A failing suite blocks the stop and hands the failure back to the agent. `stop_hook_active`
is set when the agent is already continuing because of this hook; we let it stop then, so a
test the agent can't fix never turns into an infinite loop.
"""

import json
import subprocess
import sys


def changed_python_files() -> list[str]:
    try:
        out = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True, timeout=20).stdout
    except (OSError, subprocess.TimeoutExpired):
        return []
    return [line[3:] for line in out.splitlines() if line.strip().endswith(".py")]


def main() -> int:
    event = json.load(sys.stdin)
    if event.get("stop_hook_active"):
        return 0
    if not changed_python_files():
        return 0

    try:
        result = subprocess.run(
            [sys.executable, "-m", "pytest", "-q", "-x", "--no-header"], capture_output=True, text=True, timeout=240
        )
    except subprocess.TimeoutExpired:
        print(json.dumps({"decision": "block", "reason": "Tests timed out after 240 s. Investigate before finishing."}))
        return 0

    if result.returncode not in (0, 5):  # 5 = no tests collected
        tail = "\n".join((result.stdout + result.stderr).strip().splitlines()[-30:])
        print(
            json.dumps(
                {
                    "decision": "block",
                    "reason": f"Python files changed and the test suite is failing. Fix it before finishing:\n{tail}",
                }
            )
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
