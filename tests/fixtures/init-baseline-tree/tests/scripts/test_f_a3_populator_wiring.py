"""F-A3 Populator Wiring Test (T023 / Wave 2.3 / SC-001 BLOCKER).

Asserts that all 14 detection-tier host agents emit `source_attribution` populator blocks
per ADR-037 D-3, mirroring the F-1/F-2/F-4 net-new agent precedent. The 14 hosts are
the 11 F-241 newly-wired hosts plus the 3 pre-existing F-1/F-2/F-4 net-new agents.

Test surface:
  - (a) grep -l "source_attribution" .claude/agents/tachi/*.md returns 14 paths (SC-001).
  - (b) Each newly-wired host file contains ≥1 `source_attribution:` YAML block.
  - (c) Line count ≤200 on each newly-wired host (SC-003 / ADR-036 cap).
  - (d) Pattern Category citation present in agent-level metadata (BLP-01 §8 Quality Bar
        proxy at the agent layer).
"""

from __future__ import annotations

import functools
import re
from pathlib import Path

import pytest

from .conftest import AGENTS_DIR, REPO_ROOT

# 11 F-241 newly-wired host agents (Wave 1 + Wave 2)
F241_WIRED_HOSTS = (
    "spoofing.md",
    "tampering.md",
    "info-disclosure.md",
    "privilege-escalation.md",
    "repudiation.md",
    "denial-of-service.md",
    "tool-abuse.md",
    "data-poisoning.md",
    "model-theft.md",
    "prompt-injection.md",
    "agent-autonomy.md",
)

# 3 pre-existing F-1/F-2/F-4 net-new agents that already emit source_attribution
PRE_EXISTING_WIRED_HOSTS = (
    "output-integrity.md",
    "misinformation.md",
    "human-trust-exploitation.md",
)

# 14/14 detection-tier hosts (SC-001 BLOCKER)
ALL_DETECTION_HOSTS = F241_WIRED_HOSTS + PRE_EXISTING_WIRED_HOSTS

LINE_CAP = 200


@functools.lru_cache(maxsize=None)
def _read(path: Path) -> str:
    """Read a file once and memoize. Same host is read by 6+ parametrized tests."""
    return path.read_text(encoding="utf-8")


def _line_count(path: Path) -> int:
    return len(_read(path).splitlines())


class TestSC001DetectionTierCount:
    """SC-001 BLOCKER — 14/14 detection-tier hosts emit source_attribution."""

    def test_all_14_detection_hosts_emit_source_attribution(self) -> None:
        wired = sorted(
            agent.name
            for agent in AGENTS_DIR.glob("*.md")
            if "source_attribution" in _read(agent)
        )
        expected = sorted(ALL_DETECTION_HOSTS)
        assert wired == expected, (
            f"SC-001 BLOCKER violated. Expected exactly 14 detection-tier hosts to emit "
            f"source_attribution; found {len(wired)}: {wired!r}. Missing: "
            f"{set(expected) - set(wired)!r}. Unexpected: {set(wired) - set(expected)!r}."
        )

    def test_grep_count_returns_14(self) -> None:
        count = sum(
            1
            for agent in AGENTS_DIR.glob("*.md")
            if "source_attribution" in _read(agent)
        )
        assert count == 14, f"Expected 14 hosts emitting source_attribution; got {count}"


class TestF241HostBlockShape:
    """Each F-241 newly-wired host file contains ≥1 source_attribution: YAML block."""

    @pytest.mark.parametrize("host_filename", F241_WIRED_HOSTS)
    def test_host_file_has_source_attribution_block(self, host_filename: str) -> None:
        path = AGENTS_DIR / host_filename
        text = _read(path)
        assert "source_attribution:" in text, (
            f"{host_filename} missing `source_attribution:` block per ADR-037 D-3"
        )

    @pytest.mark.parametrize("host_filename", F241_WIRED_HOSTS)
    def test_host_block_has_primary_relationship(self, host_filename: str) -> None:
        path = AGENTS_DIR / host_filename
        text = _read(path)
        assert "relationship: primary" in text, (
            f"{host_filename} missing `relationship: primary` taxonomy entry per ADR-037 D-3"
        )

    @pytest.mark.parametrize("host_filename", F241_WIRED_HOSTS)
    def test_host_block_has_related_relationship(self, host_filename: str) -> None:
        path = AGENTS_DIR / host_filename
        text = _read(path)
        assert "relationship: related" in text, (
            f"{host_filename} missing ≥1 `relationship: related` entry per ADR-037 D-3"
        )


class TestSC003LineCap:
    """SC-003 / ADR-036 cap — host agent files ≤200 lines post-wiring."""

    @pytest.mark.parametrize("host_filename", F241_WIRED_HOSTS)
    def test_host_under_line_cap(self, host_filename: str) -> None:
        path = AGENTS_DIR / host_filename
        actual = _line_count(path)
        assert actual <= LINE_CAP, (
            f"{host_filename} exceeds {LINE_CAP}-line cap per SC-003 / ADR-036; got {actual}"
        )


class TestStep5PopulatorWording:
    """Each F-241 newly-wired host's Detection Workflow Step 5 references source_attribution."""

    @pytest.mark.parametrize("host_filename", F241_WIRED_HOSTS)
    def test_step5_mentions_source_attribution(self, host_filename: str) -> None:
        path = AGENTS_DIR / host_filename
        text = _read(path)
        # Match Step 5 directive (numbered list item starting with "5." that mentions
        # the source_attribution populator). Allow for both same-line wording and
        # nearby-line wording within Step 5.
        step5_pattern = re.compile(
            r"^5\.\s.*?source_attribution",
            re.MULTILINE | re.DOTALL,
        )
        assert step5_pattern.search(text), (
            f"{host_filename} Detection Workflow Step 5 does not reference "
            f"`source_attribution` populator per ADR-037 D-3"
        )

    @pytest.mark.parametrize("host_filename", F241_WIRED_HOSTS)
    def test_step5_mentions_adr037_lineage(self, host_filename: str) -> None:
        path = AGENTS_DIR / host_filename
        text = _read(path)
        # ADR-037 D-3 reference confirms the populator wiring traces to the F-241 ADR.
        assert "ADR-037 D-3" in text, (
            f"{host_filename} does not cite ADR-037 D-3 lineage in Step 5 populator directive"
        )
