# Agentic Engineering Template

> A reference repository showing how an engineering team works with AI coding agents. It includes shared
> instructions, guardrails enforced as tested hooks, specialised subagents, workflow skills, `@claude` in GitHub,
> automatic AI review, and metrics that show whether speed is costing quality.

[![CI](https://github.com/gabicuesta/agentic-engineering-template/actions/workflows/ci.yml/badge.svg)](https://github.com/gabicuesta/agentic-engineering-template/actions/workflows/ci.yml)
![Python](https://img.shields.io/badge/python-3.11%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)

🇪🇸 [Versión en español más abajo](#-en-español)

Most teams adopt coding agents one laptop at a time. Each person ends up with different prompts, different
permissions and different habits, and there's no shared quality bar. This template makes the setup **part of the
repository**: versioned, reviewed, tested, and the same for every engineer and every CI run.

The sample app, `quotes-api`, is a small FastAPI service for renovation job requests and quotes. It exists so
that every piece of the setup has something real to act on.

**Start with the [team playbook](docs/playbook.md).** The configuration is the easy part; the operating
model is what makes it work.

## What's inside

```
AGENTS.md                     shared instructions for any agent (Claude Code, Codex, Cursor, Copilot…)
CLAUDE.md                     imports AGENTS.md and adds Claude Code specifics
.claude/
  settings.json               permissions (allow / ask / deny) and hook wiring
  hooks/                      guardrails and feedback loops, in Python and covered by tests
  agents/                     subagents: code-reviewer, test-writer, security-auditor
  skills/                     /new-endpoint, /adr, /pre-pr
.mcp.json                     project MCP servers (example: spain-open-data-mcp)
.github/
  workflows/ci.yml            lint + tests, including the agent configuration tests
  workflows/claude.yml        @claude in issues and PRs → branch + PR
  workflows/claude-review.yml AI first-pass review on every PR
  workflows/agent-metrics.yml monthly metrics summary
  pull_request_template.md    includes an "AI assistance" disclosure
  ISSUE_TEMPLATE/agent-task.md how to specify a task an agent can do
  CODEOWNERS                  humans own the agent configuration
scripts/agent_metrics.py      agent vs human commits: size, tests, reverts
docs/playbook.md              autonomy levels, review rules, metrics, cost
```

## Guardrails and feedback loops

| Hook | Event | What it does |
|---|---|---|
| `protect_files.py` | before Edit/Write | Blocks edits to `.env*`, keys, certificates and `secrets/`, and points to `.env.example` instead |
| `guard_bash.py` | before Bash | Blocks force-push, pushing to main, `--no-verify`, `curl \| sh`, broad `rm -rf`, and anything touching `.env` |
| `lint_python.py` | after Edit/Write | Formats the file and feeds remaining lint errors back to the agent (exit 2), so it fixes them in the same loop |
| `tests_gate.py` | on Stop | If Python files changed and tests fail, the agent can't finish. Loop-safe through `stop_hook_active` |
| `session_context.py` | at session start | Tells the agent the branch, recent commits and pending changes, and warns if it is on `main` |

The permission rules in `settings.json` and the hooks overlap on purpose: the rules are the first line of
defence, the hooks catch variants and explain *why*. **Every hook has tests** in
[`tests/test_agent_config.py`](tests/test_agent_config.py). They also check that the settings point to existing
scripts, and that subagents and skills are well-formed.

## Using it

```bash
git clone https://github.com/gabicuesta/agentic-engineering-template && cd agentic-engineering-template
pip install -e ".[dev]"
pytest -q          # 48 tests: app + guardrails + config + metrics
claude             # open Claude Code: AGENTS.md, hooks, subagents and skills load automatically
```

Try:

- `/new-endpoint list the quotes of a job sorted by price`
- "ask the code-reviewer subagent to review my changes"
- `/pre-pr`

In GitHub:

1. Run `/install-github-app` from Claude Code, or add the `ANTHROPIC_API_KEY` secret.
2. Protect `main` and require one human approval.
3. Open an issue with the *Agent-ready task* template and comment `@claude`.

Hooks call `python`. If your machine only has `python3`, as on some macOS setups, change the command in `.claude/settings.json`.

**Adopting it in your repo:** copy `AGENTS.md`, `CLAUDE.md`, `.claude/`, `.github/` and the config tests. Then
rewrite `AGENTS.md` for your stack and adjust the commands in `settings.json` and the hooks. Keep the tests.

## Design decisions

The full records are in [`docs/adr`](docs/adr).

1. **`AGENTS.md` is the source of truth; `CLAUDE.md` imports it.** One set of instructions for every tool, and
   tool-specific additions on top. ([ADR 0001](docs/adr/0001-agents-md-as-source-of-truth.md))
2. **Guardrails as tested code, not as prompt text.** Instructions get forgotten under pressure; hooks don't. A
   guardrail without a test is one we haven't checked. ([ADR 0002](docs/adr/0002-guardrails-as-tested-hooks.md))
3. **Humans own the merge.** AI review is a first pass. Branch protection, CODEOWNERS and the PR template keep
   accountability with people. ([ADR 0003](docs/adr/0003-humans-own-the-merge.md))

## Part of a series

- [spain-open-data-mcp](https://github.com/gabicuesta/spain-open-data-mcp): MCP server used in `.mcp.json`.
- [ai-renovation-estimator](https://github.com/gabicuesta/ai-renovation-estimator): vision and
  structured output, with multi-model evals.
- [llm-gateway](https://github.com/gabicuesta/llm-gateway): budgets, fallback and PII redaction for teams
  using LLMs.

## See it in action

A real task, done end to end with this setup:

1. **Issue [#4](https://github.com/gabicuesta/agentic-engineering-template/issues/4)**: specified with the *Agent-ready task* template (goal, context, acceptance criteria, out of scope).
2. **`@claude` comment** → Claude Code ran in GitHub Actions, following `AGENTS.md`, the hooks and the `/new-endpoint` skill, and pushed a branch.
3. **PR [#5](https://github.com/gabicuesta/agentic-engineering-template/pull/5)**: CI green on three Python versions, plus a first-pass AI review.
4. **A human reviewed, approved and merged it.** The PR declares the AI assistance; the merge stays with a person.

## License

MIT.

---

## 🇪🇸 En español

**Repositorio de referencia de cómo trabaja un equipo de ingeniería con agentes de IA.**

La mayoría de equipos adoptan los agentes de forma individual: cada persona con sus propios prompts, permisos y
costumbres, y sin un estándar común. Esta plantilla convierte esa configuración en **parte del repositorio**:
versionada, revisada, probada e igual para todo el equipo y para la CI.

Incluye:

- **`AGENTS.md` compartido:** instrucciones para cualquier herramienta, y un `CLAUDE.md` que lo importa.
- **Guardrails como hooks probados:** bloquean secretos, push a `main` y comandos destructivos, formatean y
  devuelven errores de lint al agente, y no le dejan terminar con tests en rojo.
- **Subagentes:** revisor, autor de tests y auditor de seguridad.
- **Skills:** `/new-endpoint`, `/adr` y `/pre-pr`.
- **GitHub:** `@claude` en issues y PRs, revisión automática con IA, plantilla de PR que declara el uso de IA,
  CODEOWNERS y métricas mensuales.

Lo más importante es el [playbook del equipo](docs/playbook.md): niveles de autonomía, cómo revisar código escrito
por agentes, cómo especificar tareas y qué métricas mirar para saber si la velocidad está costando calidad.
