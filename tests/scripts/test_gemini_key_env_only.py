"""Feature 393 — GEMINI_API_KEY is read from the environment only.

Static contract over three distributed files:
  * the infographic agent's "API Key Check" and its adapter copy read the key from the
    process environment only — no `.env` sourcing, no `export`/`source`/`xargs` loader;
  * the Gemini request form in the infographics skill reference is pinned: the key header
    travels through `curl --config -` on stdin, never on the command line or in a query string;
  * no fenced shell block under the distributed agents, commands and tachi skills runs a bare
    `export $(...)` substitution.

Stdlib + pytest only. Gated in `.github/workflows/tachi-pytest.yml`.
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
AGENT = ROOT / ".claude" / "agents" / "tachi" / "threat-infographic.md"
ADAPTER = ROOT / "adapters" / "claude-code" / "agents" / "references" / "infographic-gemini-api.md"
REFERENCE = ROOT / ".claude" / "skills" / "tachi-infographics" / "references" / "gemini-prompt-construction.md"

FENCE_RE = re.compile(r"```(?:bash|sh|shell|zsh)?\n(.*?)```", re.S)
FORBIDDEN_LOADER = re.compile(r"export \$\(|source\s+\S*\.env|\.\s+\S*\.env|set -a|grep[^\n]*\.env|xargs")


def _section(text: str, heading: str) -> str:
    assert heading in text, f"missing heading {heading!r}"
    body = text.split(heading, 1)[1]
    return body.split("\n---", 1)[0]


@pytest.mark.parametrize("path", [AGENT, ADAPTER], ids=["agent", "adapter"])
def test_api_key_check_reads_environment_only(path: Path) -> None:
    section = _section(path.read_text(encoding="utf-8"), "### API Key Check")
    assert "process environment only" in section
    assert "never reads the key from a file" in section
    for block in FENCE_RE.findall(section):
        assert ".env" not in block, f"{path.name}: a fenced block still references .env"
        assert not FORBIDDEN_LOADER.search(block), f"{path.name}: a fenced block still loads the key"
    # the old fallback phrasing is gone everywhere in the file
    assert "source it" not in path.read_text(encoding="utf-8")


def test_request_form_is_pinned_and_keeps_the_key_off_argv() -> None:
    text = REFERENCE.read_text(encoding="utf-8")
    assert "**Request form (pinned)**" in text
    assert "--config -" in text
    assert 'header = "x-goog-api-key: $GEMINI_API_KEY"' in text
    assert "--data @" in text
    for line in text.splitlines():
        if "?key=" in line or re.search(r"--header\s+\"x-goog-api-key|-H\s+\"x-goog-api-key", line):
            assert "never" in line, f"key-on-argv or query form outside a prohibition: {line[:80]!r}"


def test_no_bare_export_substitution_in_distributed_shell_blocks() -> None:
    files = (
        list((ROOT / ".claude" / "agents" / "tachi").glob("*.md"))
        + list((ROOT / ".claude" / "commands").glob("tachi.*.md"))
        + [p for p in (ROOT / ".claude" / "skills").rglob("*.md") if p.parts[-2:][0].startswith("tachi") or "tachi-" in str(p)]
    )
    assert files, "no distributed files found"
    offenders = []
    for path in files:
        for block in FENCE_RE.findall(path.read_text(encoding="utf-8")):
            if re.search(r"export \$\(", block):
                offenders.append(str(path.relative_to(ROOT)))
    assert not offenders, f"bare export substitution in: {offenders}"
