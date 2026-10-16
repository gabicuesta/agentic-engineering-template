# Engineering with agents: team playbook

How this team uses AI coding agents. The configuration in this repo enforces most of it; this document explains
the *why*, so people can apply judgement where configuration can't.

## Principles

1. **Humans own outcomes.** Whoever merges a change owns it, whoever wrote it. "The agent did it" is not
   an explanation in a postmortem.
2. **Make the right way the easy way.** Conventions live in `AGENTS.md`, and guardrails live in hooks and
   permissions, not in people's memory. If we keep correcting the same thing in review, we encode it.
3. **Agents get the same quality bar, not a lower one.** Same tests, same lint, same review. Code is no cheaper
   to maintain because it was cheap to write.
4. **Measure outcomes, not usage.** "% of code written by AI" is a vanity metric. Lead time, change failure rate
   and review load are what matter.

## Levels of autonomy

| Level | What it looks like | Who reviews | Use it for |
|---|---|---|---|
| **L1: Assisted** | Engineer drives, the agent suggests or edits in their session | Normal PR review | Everything |
| **L2: Delegated** | Engineer hands a well-specified task to an agent locally, then reviews the result before pushing | Normal PR review, plus the `/pre-pr` checks | Features and fixes with clear acceptance criteria |
| **L3: Background** | `@claude` on an `agent-ready` issue: the agent opens a branch and a PR on its own | A human reviewer is required; the AI review is a first pass only | Small, well-bounded tasks: bug fixes with a reproduction, tests, refactors, dependency bumps |

Move a type of work up a level only when the previous level has been reliable for it. Move it back down after an
incident.

## What agents do and don't do here

**Allowed without asking:** reading code, running tests and linters, editing source and tests on a feature
branch, and committing to that branch.

**Ask a human first:** new dependencies; changes to CI, `.claude/`, `AGENTS.md` or public API contracts;
anything involving auth, payments or personal data.

**Never, enforced by hooks and tested in CI:**

- reading or editing secrets;
- pushing to `main` or force-pushing;
- `--no-verify`;
- piping downloads into a shell;
- recursive deletes of broad paths.

These are a safety net, not a sandbox. Agents with real credentials run in isolated environments.

## Reviewing agent-written code

- **Read the whole diff.** Agent changes look plausible, which is exactly why they need a careful review.
- **Check the tests before the code.** Do they test behaviour, or just mirror the implementation? Would they
  fail if the feature broke?
- **Watch for the classic failure modes:**
  - code that solves a slightly different problem
  - invented APIs or config keys
  - over-engineering
  - silently weakened tests or assertions
  - unrelated "improvements"
- **Keep PRs small.** If a PR is too big to review well, ask for a split. Agents make it cheap to generate a
  big diff, but reviewing one is still expensive.
- **Fill in the "AI assistance" section of the PR template.** It isn't blame. It tells us where to look and
  feeds our metrics.

## Writing tasks agents can do

The `agent-ready` issue template is the format. A good task has:

- **One outcome**, not a list of loosely related changes.
- **Context:** the files, endpoints and decisions (ADRs) involved.
- **Acceptance criteria that are observable**, e.g. "returns 409 when…", "test X passes".
- **Out of scope:** what must not change.

If a new teammate couldn't do the task without asking you questions, neither can an agent. Writing these
tasks well is a senior skill, and it makes us better at specifying work for humans too.

## Changing how agents behave

`AGENTS.md`, `CLAUDE.md`, `.claude/` and `.mcp.json` are code:

- Changes go through PRs and are owned by `CODEOWNERS`.
- Hooks and config are covered by `tests/test_agent_config.py`. A guardrail without a test is a guardrail
  we haven't checked.
- When an agent repeats a mistake, fix the instructions or add a guardrail. Don't only fix the instance.
- Prefer a short `AGENTS.md`. Every line costs context on every task; link to docs instead of pasting them.
- MCP servers in `.mcp.json` need the same scrutiny as a new dependency: what data can they read, and where
  does it go?

## Metrics

Run `scripts/agent_metrics.py`. CI also runs it every month and publishes a summary.

| Signal | Why it matters | Warning sign |
|---|---|---|
| Share of agent-assisted commits | Adoption | Rising fast while the other signals get worse |
| Code commits that also change tests | Whether speed costs quality | Lower for agent commits than for human ones |
| Reverts | Change failure | Agent commits reverted more often |
| Median change size | Reviewability | Agent changes growing larger |
| PR review time and review comments (from GitHub) | Hidden cost moved to reviewers | Review load growing faster than throughput |

Review these signals quarterly, together with lead time and incident data, and adjust the autonomy levels.

## Cost

Agent usage has a direct cost, so treat it like any other infrastructure:

- Use an org account with spend limits, or route through an LLM gateway with per-team budgets.
- Default to balanced models for routine tasks. Reserve the largest models for design, debugging and reviews
  where depth pays off.
- Background (L3) runs have `--max-turns` and job timeouts.
