#!/usr/bin/env python3
"""PostToolUse (Edit/Write): format the edited Python file and feed remaining lint errors back.

Exit code 2 sends stderr to the agent, so it fixes lint issues in the same loop instead of
leaving them for CI or a human reviewer.
"""

import json
import shutil
import subprocess
import sys
from pathlib import Path


def run(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(args, capture_output=True, text=True, timeout=50)


def main() -> int:
    event = json.load(sys.stdin)
    path = (event.get("tool_input") or {}).get("file_path", "")
    if not path.endswith(".py") or not Path(path).is_file() or not shutil.which("ruff"):
        return 0

    run("ruff", "format", "--quiet", path)
    run("ruff", "check", "--fix", "--quiet", path)
    result = run("ruff", "check", "--output-format", "concise", path)
    if result.returncode != 0:
        print(f"Lint errors remain in {path}; fix them before continuing:\n{result.stdout.strip()}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
