# ADR 0001: AGENTS.md as the source of truth, CLAUDE.md imports it

- **Status:** Accepted
- **Date:** 2026-10-16

## Context

Engineers use different agents: Claude Code, Codex, Cursor, Copilot. Each tool reads its own instructions file.
Keeping several copies in sync fails quickly, and the agents end up with contradictory rules.

## Options considered

1. **One file per tool, maintained by hand.** Maximum flexibility, but the copies drift.
2. **Symlinks between files.** Fragile on Windows and confusing in reviews.
3. **`AGENTS.md` as the shared standard, with tool files importing it.** One source, plus a thin
   tool-specific layer on top.

## Decision

Option 3.

- `AGENTS.md` holds everything that is true regardless of the tool: commands, architecture, conventions,
  boundaries and the definition of done.
- `CLAUDE.md` starts with `@AGENTS.md` and adds only Claude Code specifics: hooks, subagents and skills.

## Consequences

- One place to update. Reviews of `AGENTS.md` changes are reviews of team practice.
- `AGENTS.md` must stay short. Every line costs context on every task, so link to docs instead of pasting them.
