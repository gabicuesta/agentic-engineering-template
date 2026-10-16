import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / "scripts"))

import agent_metrics  # noqa: E402


def commit(repo: Path, files: dict[str, str], message: str) -> None:
    for name, content in files.items():
        path = repo / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)
    subprocess.run(["git", "add", "-A"], cwd=repo, check=True)
    subprocess.run(
        ["git", "-c", "user.name=Dev", "-c", "user.email=dev@example.com", "commit", "-q", "-m", message],
        cwd=repo,
        check=True,
    )


def test_metrics_split_agent_and_human_commits(tmp_path):
    subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True)
    trailer = "\n\nCo-Authored-By: Claude <noreply@anthropic.com>"
    commit(tmp_path, {"src/a.py": "a = 1\n", "tests/test_a.py": "def test(): pass\n"}, "Add a" + trailer)
    commit(tmp_path, {"src/b.py": "b = 2\n"}, "Add b" + trailer)
    commit(tmp_path, {"src/c.py": "c = 3\n"}, "Add c")
    subprocess.run(["git", "-c", "user.name=Dev", "-c", "user.email=d@e.com", "revert", "--no-edit", "HEAD~1"],
                   cwd=tmp_path, check=True, capture_output=True)  # fmt: skip

    summary = agent_metrics.summarise(agent_metrics.read_commits("1 year ago", str(tmp_path)))

    assert summary["total"] == 4
    assert summary["agent"]["commits"] == 2 and summary["human"]["commits"] == 2
    assert summary["agent"]["code_commits_with_tests"] == 0.5
    assert summary["reverted_agent_commits"] == 1
    assert "Agent-assisted share" in agent_metrics.render(summary, "1 year ago", markdown=True)
