@AGENTS.md

## Claude Code specifics

- Guardrails are enforced by hooks in `.claude/hooks/` (see `.claude/settings.json`). If a hook blocks you,
  read its message and change approach; never try to work around it.
- After you edit a Python file, a hook formats it and reports remaining lint errors: fix them before moving on.
- When you finish, a Stop hook runs the test suite if Python files changed. If it fails, keep working.
- Use subagents for independent second opinions:
  - `code-reviewer` before opening a PR,
  - `test-writer` to strengthen tests for a change,
  - `security-auditor` for anything touching input handling, auth or data exposure.
- Skills: `/new-endpoint` to add an endpoint the house way, `/adr` to record a decision,
  `/pre-pr` to run checks and draft the PR description.
