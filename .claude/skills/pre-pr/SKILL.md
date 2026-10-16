---
name: pre-pr
description: Final checks before opening a pull request - tests, lint, independent review and a filled-in PR description. Use when the user says the work is ready or asks to open a PR.
disable-model-invocation: true
---

Prepare the current branch for a pull request.

1. Make sure you are not on `main`. If you are, stop and ask which branch to create.
2. Run `ruff format --check .`, `ruff check .` and `pytest -q`. If anything fails, fix it (or report why you
   can't) before continuing.
3. Delegate a review to the `code-reviewer` subagent. If the change touches endpoints, schemas or storage,
   also delegate to `security-auditor`. Fix every Blocker; list the rest.
4. Draft the PR description following `.github/pull_request_template.md`:
   - what and why, in two or three sentences;
   - how it was tested (commands and results, not "tested locally");
   - API changes, if any;
   - the **AI assistance** section: what the agent did, what a human reviewed and decided.
5. Show the description and the remaining review findings. Do not push or open the PR: a human does that.
