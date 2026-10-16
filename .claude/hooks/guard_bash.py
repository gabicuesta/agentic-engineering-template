#!/usr/bin/env python3
"""PreToolUse (Bash): block destructive or secret-leaking shell commands.

Permission rules in settings.json match command prefixes; this hook catches the variants they
miss (flags in a different order, pipes, absolute paths). Not a sandbox: a last line of defence.
"""

import json
import re
import shlex
import sys

RULES = [
    (
        r"\brm\s+(-[a-zA-Z]*r[a-zA-Z]*f|-[a-zA-Z]*f[a-zA-Z]*r)\b[^|;&]*\s(/|~|\.|\*)(\s|$)",
        "Recursive force-delete of a broad path. Delete specific files instead.",
    ),
    (r"\bgit\s+push\b[^|;&]*\s(--force(-with-lease)?|-f)\b", "Force-push rewrites shared history. Ask a human."),
    (r"\bgit\s+push\b[^|;&]*\b(origin\s+)?(main|master)\b", "Never push to main. Push a branch and open a PR."),
    (r"\bgit\s+(reset\s+--hard|clean\s+-[a-zA-Z]*f)", "This discards work irreversibly. Ask a human."),
    (r"--no-verify\b", "Skipping git hooks hides failing checks. Fix the check instead."),
    (r"\b(curl|wget)\b[^|]*\|\s*(sudo\s+)?(ba|z)?sh\b", "Piping a download into a shell runs unreviewed code."),
    (r"^\s*(printenv|env)\s*($|\|)", "Dumping the environment can expose secrets."),
]
COMPILED = [(re.compile(p), reason) for p, reason in RULES]


ENV_FILE = re.compile(r"(^|[/=<>])\.env(\.[\w-]+)?$")
SAFE_ENV = (".env.example", ".env.sample", ".env.template")


def touches_env_file(command: str) -> bool:
    try:
        tokens = shlex.split(command, posix=True)
    except ValueError:
        tokens = command.split()
    return any(ENV_FILE.search(t) and not t.endswith(SAFE_ENV) for t in tokens)


def check(command: str) -> str | None:
    if touches_env_file(command):
        return "Commands must not touch .env files (secrets). Use .env.example to see variable names."
    for pattern, reason in COMPILED:
        if pattern.search(command):
            return reason
    return None


def main() -> int:
    event = json.load(sys.stdin)
    command = (event.get("tool_input") or {}).get("command", "")
    reason = check(command)
    if reason:
        print(
            json.dumps(
                {
                    "hookSpecificOutput": {
                        "hookEventName": "PreToolUse",
                        "permissionDecision": "deny",
                        "permissionDecisionReason": f"Blocked command: {reason}",
                    }
                }
            )
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
