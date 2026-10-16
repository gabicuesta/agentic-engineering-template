#!/usr/bin/env python3
"""How is the team working with agents? A git-only snapshot, no external services.

    python scripts/agent_metrics.py --since "90 days ago" [--markdown]

A commit counts as agent-assisted when it has a Co-Authored-By trailer from a known agent
(Claude Code adds one by default). For each group we report size, how often tests change
with code, and reverts: the signals that tell you whether speed is costing quality.
"""

from __future__ import annotations

import argparse
import re
import statistics
import subprocess
from dataclasses import dataclass, field

AGENT_TRAILER = re.compile(
    r"^co-authored-by:.*(claude|anthropic|copilot|codex|cursor|devin|gemini|ai agent)", re.IGNORECASE | re.MULTILINE
)
SEP = "\x1e"


@dataclass
class Commit:
    sha: str
    subject: str
    body: str
    files: list[tuple[int, int, str]] = field(default_factory=list)

    @property
    def agent(self) -> bool:
        return bool(AGENT_TRAILER.search(self.body))

    @property
    def lines(self) -> int:
        return sum(a + d for a, d, _ in self.files)

    @property
    def touches_code(self) -> bool:
        return any(p.endswith(".py") and not p.startswith("tests/") for _, _, p in self.files)

    @property
    def touches_tests(self) -> bool:
        return any(p.startswith("tests/") for _, _, p in self.files)

    @property
    def is_revert(self) -> bool:
        return self.subject.startswith("Revert ")


def read_commits(since: str, repo: str = ".") -> list[Commit]:
    fmt = f"{SEP}%H%n%s%n%b%n{SEP}"
    out = subprocess.run(
        ["git", "-C", repo, "log", "--no-merges", f"--since={since}", f"--pretty=format:{fmt}", "--numstat"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout
    commits: list[Commit] = []
    chunks = out.split(SEP)
    # chunks: ["", header1, numstat1, header2, numstat2, ...]
    for i in range(1, len(chunks) - 1, 2):
        sha, _, rest = chunks[i].strip("\n").partition("\n")
        subject, _, body = rest.partition("\n")
        commit = Commit(sha=sha, subject=subject, body=body)
        for line in chunks[i + 1].strip().splitlines():
            parts = line.split("\t")
            if len(parts) == 3:
                added, deleted, path = parts
                commit.files.append(
                    (int(added) if added.isdigit() else 0, int(deleted) if deleted.isdigit() else 0, path)
                )
        commits.append(commit)
    return commits


def summarise(commits: list[Commit]) -> dict:
    def group(cs: list[Commit]) -> dict:
        code = [c for c in cs if c.touches_code]
        return {
            "commits": len(cs),
            "median_lines": statistics.median([c.lines for c in cs]) if cs else 0,
            "code_commits_with_tests": round(sum(c.touches_tests for c in code) / len(code), 2) if code else None,
        }

    agent = [c for c in commits if c.agent]
    human = [c for c in commits if not c.agent]
    reverted_subjects = {c.subject.removeprefix('Revert "').removesuffix('"') for c in commits if c.is_revert}
    return {
        "total": len(commits),
        "agent_share": round(len(agent) / len(commits), 2) if commits else 0.0,
        "agent": group(agent),
        "human": group(human),
        "reverted_agent_commits": sum(1 for c in agent if c.subject in reverted_subjects),
        "reverted_human_commits": sum(1 for c in human if c.subject in reverted_subjects),
    }


def render(s: dict, since: str, markdown: bool) -> str:
    pct = lambda v: "–" if v is None else f"{v:.0%}"  # noqa: E731
    rows = [
        ("Commits", s["agent"]["commits"], s["human"]["commits"]),
        ("Median lines changed", s["agent"]["median_lines"], s["human"]["median_lines"]),
        ("Code commits that also change tests", pct(s["agent"]["code_commits_with_tests"]),
         pct(s["human"]["code_commits_with_tests"])),
        ("Commits later reverted", s["reverted_agent_commits"], s["reverted_human_commits"]),
    ]  # fmt: skip
    title = f"Agent-assisted share of commits since {since}: {pct(s['agent_share'])} of {s['total']}"
    if markdown:
        lines = [f"### {title}", "", "| | Agent-assisted | Human-only |", "|---|---:|---:|"]
        lines += [f"| {name} | {a} | {h} |" for name, a, h in rows]
    else:
        lines = [title, ""] + [f"{name:<38} {a!s:>15} {h!s:>12}" for name, a, h in rows]
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--since", default="90 days ago")
    parser.add_argument("--repo", default=".")
    parser.add_argument("--markdown", action="store_true")
    args = parser.parse_args()
    print(render(summarise(read_commits(args.since, args.repo)), args.since, args.markdown))


if __name__ == "__main__":
    main()
