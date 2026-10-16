---
name: new-endpoint
description: Add a new API endpoint the way this repo does it - domain rule, schema, router, tests. Use when asked to add or change an endpoint.
argument-hint: "<what the endpoint should do>"
---

Add the endpoint described in: $ARGUMENTS

Follow this order and do not skip steps:

1. **Plan** (show it before editing): HTTP method and path, request/response schemas, the domain rule it
   needs, error cases and their status codes (422 validation, 404 missing, 409 business rule).
2. **Domain first:** if there is a business rule, add it as a method on the domain model in
   `src/quotes_api/domain/models.py`, raising `DomainError` with a readable message. Add unit tests in
   `tests/test_domain.py` and run them.
3. **Schemas:** add request/response models in `src/quotes_api/api/schemas.py` with explicit bounds.
4. **Router:** add the route to the right router in `src/quotes_api/api/`. Keep it thin: load via the
   repository, call the domain, map `DomainError` to 409, save.
5. **API tests:** happy path, validation error, not found, and each business-rule violation in
   `tests/test_api.py`.
6. **Verify:** `pytest -q` and `ruff check .`. Then summarise the new contract (method, path, bodies, status
   codes) so it can be pasted into the PR description.
