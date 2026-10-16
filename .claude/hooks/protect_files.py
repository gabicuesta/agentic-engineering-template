#!/usr/bin/env python3
"""PreToolUse (Edit/Write): block edits to secrets and credentials.

Defence in depth: settings.json also denies these paths, but a hook gives the agent a clear
reason and an alternative, and it is tested (tests/test_hooks.py).
"""

import json
import re
import sys
from pathlib import PurePath

PROTECTED = [
    (re.compile(r"^\.env(\..+)?$"), "Secrets live in .env files. Document new variables in .env.example instead."),
    (re.compile(r".*\.(pem|key|p12|pfx)$"), "Private keys and certificates must never be edited by an agent."),
    (re.compile(r"^id_(rsa|ed25519|ecdsa)(\.pub)?$"), "SSH keys must never be edited by an agent."),
]
ALLOWED = {".env.example", ".env.sample", ".env.template"}


def check(path: str) -> str | None:
    p = PurePath(path)
    if "secrets" in p.parts:
        return "Files under secrets/ are off-limits for agents."
    if p.name in ALLOWED:
        return None
    for pattern, reason in PROTECTED:
        if pattern.match(p.name):
            return reason
    return None


def main() -> int:
    event = json.load(sys.stdin)
    tool_input = event.get("tool_input") or {}
    path = tool_input.get("file_path") or tool_input.get("notebook_path") or ""
    reason = check(path) if path else None
    if reason:
        print(
            json.dumps(
                {
                    "hookSpecificOutput": {
                        "hookEventName": "PreToolUse",
                        "permissionDecision": "deny",
                        "permissionDecisionReason": f"Blocked edit to {path}: {reason}",
                    }
                }
            )
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
