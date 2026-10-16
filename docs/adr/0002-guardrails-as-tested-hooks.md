# ADR 0002: Guardrails as tested hooks, not prompt instructions

- **Status:** Accepted
- **Date:** 2026-10-16

## Context

"Never edit `.env`" or "run the tests before finishing" written in a prompt is a request, not a guarantee. Agents
follow instructions most of the time, which is not good enough for secrets, shared history or the main branch.

## Options considered

1. **Instructions only.** Cheap, but not enforced.
2. **Permission rules only.** Enforced, but they match command prefixes and miss variants (flag order, pipes,
   absolute paths). They also don't explain *why* to the agent.
3. **Permission rules plus hooks, with tests.**

## Decision

Option 3.

- Permission rules are the first line of defence. Hooks catch the variants the rules miss and return a reason
  the agent can act on.
- Hooks also create **feedback loops**: lint errors go back to the agent after each edit, and a failing test
  suite blocks the agent from finishing.
- Hooks are written in Python, not bash plus `jq`, so they run the same on macOS, Linux and Windows.
- Every hook has tests, and CI checks that the settings point to existing scripts.

## Consequences

- Guardrails are reviewable and regression-tested, like any other code.
- Hooks are a safety net, not a security boundary. Agents with real credentials still need isolated environments.
- The Stop hook adds test time at the end of a task. It runs only when Python files changed, and it lets the
  agent stop if it is already retrying, to avoid loops.
