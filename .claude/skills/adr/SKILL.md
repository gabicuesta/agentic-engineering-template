---
name: adr
description: Record an architecture decision as an ADR in docs/adr. Use when a decision with lasting consequences is made or asked to be documented.
argument-hint: "<decision title>"
disable-model-invocation: true
---

Write an Architecture Decision Record for: $ARGUMENTS

1. Find the highest number in `docs/adr/` and use the next one, zero-padded to 4 digits. File name:
   `docs/adr/NNNN-short-kebab-title.md`.
2. Use exactly this structure:

   ```
   # ADR NNNN: <Title>

   - Status: Proposed
   - Date: <today, YYYY-MM-DD>

   ## Context
   <the forces at play: problem, constraints, what happens if we do nothing>

   ## Options considered
   <2-4 options, each with pros and cons>

   ## Decision
   <what we chose and why it wins over the alternatives>

   ## Consequences
   <what gets easier, what gets harder, what we must now do or watch>
   ```
3. Ask for any context you don't have rather than inventing it. Keep it under one page.
