# ADR 0003: AI review is a first pass; humans own the merge

- **Status:** Accepted
- **Date:** 2026-10-16

## Context

Agents can now write a change, open the PR and review it. It is tempting to let an approving AI review be enough.
But accountability, the context of the business, and the cost of a bad change all sit with people.

## Decision

- **AI review on every PR**, as a first pass: it catches the cheap problems before a human spends time.
- **Branch protection requires at least one human approval.** `CODEOWNERS` routes changes to agent
  configuration to the people accountable for it.
- The PR template asks the author to **declare AI assistance** and to confirm they have read every line and own
  the change.
- Background agents (`@claude`) open branches and PRs. They never push to `main`.

## Consequences

- Review load is the main hidden cost of agents. We track it in the metrics and keep PRs small.
- Accountability stays clear: whoever approves and merges a change owns it.
