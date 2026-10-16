# AGENTS.md

Instructions for AI coding agents working in this repository (Claude Code, Codex, Cursor, Copilot…).
Humans: this is also the shortest accurate description of how we work here.

## Project

`quotes-api` is a FastAPI service where homeowners post renovation **job requests** and professionals send
**quotes**; the owner accepts one. It is small on purpose: it exists to show how the team works with agents.

## Commands

| Task | Command |
|---|---|
| Install | `pip install -e ".[dev]"` |
| Run | `uvicorn quotes_api.main:app --reload` |
| Test | `pytest -q` |
| Lint & format | `ruff check . && ruff format --check .` |
| Fix formatting | `ruff format . && ruff check --fix .` |

Run the tests and the linter before you say a task is done. If you can't run them, say so explicitly.

## Architecture

```
src/quotes_api/
  domain/    business rules, pure Python, no FastAPI or Pydantic imports
  storage/   repository port (Protocol) + adapters
  api/       FastAPI routers, request/response schemas, dependency wiring
  main.py    application factory
```

- **Rules live in `domain/`.** Routers validate input, call the domain and map `DomainError` → HTTP 409. Never
  put a business rule in a router.
- **API schemas are not domain models.** Add fields to `api/schemas.py` deliberately; don't expose internals.
- **Storage goes through `JobRepository`.** Don't access the in-memory dict from anywhere else.

## Conventions

- Python 3.11+, type hints everywhere, `from __future__ import annotations`.
- Money is `Decimal`, never `float`. Timestamps are timezone-aware UTC.
- Errors: domain raises `DomainError` with a message a user could read; API maps it, never leaks stack traces.
- Tests: one behaviour per test, named after the behaviour (`test_accepting_a_quote_rejects_the_others`).
  Domain rules get unit tests in `tests/test_domain.py`; endpoints get API tests in `tests/test_api.py`.
- Small, focused changes. If a task grows beyond ~300 lines of diff, stop and propose a split.

## How to work

1. **Understand first.** Read the relevant code and tests. For anything non-trivial, write a short plan
   before editing and state your assumptions.
2. **Test first for behaviour changes.** Add or change a failing test, then make it pass.
3. **Verify.** Run tests and linter. Read your own diff as a reviewer would.
4. **Explain.** Summarise what changed, why, and what you did *not* do or could not verify.

## Boundaries

Always ask a human before you:
- add a dependency, change `pyproject.toml`, CI workflows or anything under `.claude/` / `.github/`;
- change a public API contract (paths, field names, status codes) or delete tests;
- touch authentication, permissions, payments or personal data handling.

Never:
- read, print or edit secrets (`.env*`, keys, tokens) — use `.env.example` for documentation;
- push to `main`, force-push, or rewrite published history;
- disable or skip tests, lint rules or hooks to make a check pass;
- invent results: if a command failed or wasn't run, say so.

## Definition of done

- [ ] Tests cover the new behaviour and pass locally
- [ ] `ruff check` and `ruff format --check` are clean
- [ ] Public API changes are reflected in schemas and the PR description
- [ ] The PR template is filled in, including the AI-assistance section
