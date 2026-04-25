"""Regression tests for Issue #209 — extractor/agent contract-drift bug batch.

Five producer/consumer contract mismatches were fixed in this batch. Each test
below exercises the failure mode reported in the corresponding bug report and
asserts the post-fix behavior. Synthetic artifact strings are inlined so the
tests remain stable if fixture artifacts are later regenerated.

Bug 1 — ``parse_compensating_controls_md`` dedupes cross-listed findings
Bug 2 — ``parse_attack_trees`` accepts agent-emitted ``{ID}-{slug}.md`` names
Bug 3 — ``parse_threat_report_md`` falls back to full Section 1 prose
Bug 4 — ``detect_images`` finds both ``.jpg`` and ``.png`` extensions
Bug 5 — ``_merge_delta_status`` populates ``delta_status`` at Tier 1/2
"""

import sys
from pathlib import Path

import pytest

# tachi_parsers lives alongside the scripts; expose it to the test namespace.
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))


# ---------------------------------------------------------------------------
# Bug 1 — compensating-controls dedupe
# ---------------------------------------------------------------------------

CC_MD_WITH_CROSS_LISTED = """---
schema_version: "1.0"
---

## 1. Executive Summary

**Risk Reduction**: 100.0 inherent -> 60.0 residual (**40.0%** reduction)
**Coverage**: 30% Found | 30% Partial | 40% Missing

## 2. Coverage Matrix

### High Residual Severity

| Threat ID | Component | Threat | Residual Score | Residual Severity | Control Status |
|-----------|-----------|--------|----------------|-------------------|----------------|
| S-1 | API | Auth bypass | 8.0 | High | Partial |
| S-2 | DB | Data exfil | 5.5 | High | Missing |

### Medium Residual Severity

| Threat ID | Component | Threat | Residual Score | Residual Severity | Control Status |
|-----------|-----------|--------|----------------|-------------------|----------------|
| S-2 | DB | Data exfil | 5.5 | Medium | Missing |
| S-3 | Net | Flood | 4.5 | Medium | Found |

### Low Residual Severity

| Threat ID | Component | Threat | Residual Score | Residual Severity | Control Status |
|-----------|-----------|--------|----------------|-------------------|----------------|

### Critical Residual Severity

| Threat ID | Component | Threat | Residual Score | Residual Severity | Control Status |
|-----------|-----------|--------|----------------|-------------------|----------------|

## 3. Control Details
## 4. Recommendations
"""


def test_bug1_compensating_controls_dedupes_cross_listed_findings():
    """Control-analyzer cross-lists S-2 in both High and Medium sections to
    show the score-derived reclassification (score 5.5 -> Medium). The parser
    must dedupe by Threat ID so severity["total"] matches the unique count,
    not the raw row count. Pre-fix: total=4 (rows), sev_sum=4, but validator
    downstream compared populations counted under different rules — mismatch.
    """
    from tachi_parsers import parse_compensating_controls_md

    data = parse_compensating_controls_md(CC_MD_WITH_CROSS_LISTED)
    ids = [f["id"] for f in data["findings"]]

    assert len(data["findings"]) == 3, (
        f"Expected 3 unique findings after dedupe, got {len(data['findings'])}: {ids}"
    )
    assert ids.count("S-2") == 1, (
        f"S-2 cross-listed in 2 sections should dedupe to 1 entry, got {ids.count('S-2')}"
    )
    assert data["severity"]["total"] == 3
    assert (
        sum(data["severity"][k] for k in ("critical", "high", "medium", "low"))
        == data["severity"]["total"]
    ), "Severity buckets must sum to total after dedupe"


# ---------------------------------------------------------------------------
# Bug 2 — attack-tree glob
# ---------------------------------------------------------------------------

ATTACK_TREE_AGENT_NATIVE = """# Attack Tree: S-1 -- API auth bypass

| Field | Value |
|-------|-------|
| Finding ID | S-1 |
| Component | API |
| Risk Level | Critical |
| Threat | Attacker bypasses API auth |

```mermaid
graph TD
    A[Attacker] --> B[API]
```
"""


def test_bug2_attack_tree_glob_accepts_agent_native_filenames(tmp_path, extract_report_data):
    """The attack-tree-delta agent writes ``{ID}-{slug}.md`` (e.g.
    ``S-1-api-auth-bypass.md``). Pre-fix: extractor globbed ``*-attack-tree.md``
    and matched 0 files; entire Attack Path section dropped. Post-fix: glob
    ``*.md`` and let _parse_attack_tree_file filter by structure.
    """
    attack_trees_dir = tmp_path / "attack-trees"
    attack_trees_dir.mkdir()
    (attack_trees_dir / "S-1-api-auth-bypass.md").write_text(
        ATTACK_TREE_AGENT_NATIVE, encoding="utf-8"
    )

    findings = [{"id": "S-1", "risk_level": "Critical", "mitigation": "Rotate keys"}]
    entries = extract_report_data.parse_attack_trees(tmp_path, findings)

    assert len(entries) == 1, f"Expected 1 entry from agent-native filename, got {len(entries)}"
    assert entries[0]["id"] == "S-1"


# ---------------------------------------------------------------------------
# Bug 3 — executive narrative fallback
# ---------------------------------------------------------------------------

THREAT_REPORT_PROSE_ONLY = """# Threat Report

## 1. Executive Summary

The system under review is a SaaS application with 42 active findings.

**Risk profile by count**: 5 Critical, 12 High, 20 Medium, 5 Low.

**Most critical unresolved exposure**: The auth service allows unauthenticated
admin access via a legacy flag that was never removed.

## 2. Architecture Overview

Components and trust boundaries follow below.
"""


def test_bug3_narrative_fallback_to_full_section1_prose(extract_report_data):
    """When the threat-report agent emits a prose Executive Summary with
    bold-label paragraphs (the current emission pattern) instead of the
    extractor's preferred ### subsections, the narrative must fall back to
    the full Section 1 prose rather than returning None.
    """
    result = extract_report_data.parse_threat_report_md(THREAT_REPORT_PROSE_ONLY)

    assert result["executive_narrative"] is not None, (
        "Narrative must be populated when Section 1 is prose-only (Bug 3 regression)"
    )
    assert "42 active findings" in result["executive_narrative"]
    assert "Risk profile by count" in result["executive_narrative"]
    assert "## 2." not in result["executive_narrative"], (
        "Fallback must stop at Section 2 header"
    )


# ---------------------------------------------------------------------------
# Bug 4 — detect_images finds both .jpg and .png
# ---------------------------------------------------------------------------

# Issue #215 follow-up tightened the contract: detect_images now selects by
# magic bytes, not just by filename presence. The bytes below are the minimum
# headers required to be recognized as JPEG/PNG by the byte probe.
_JPEG_MAGIC_BYTES = b"\xff\xd8\xff\xe0\x00\x10JFIF" + b"\x00" * 16
_PNG_MAGIC_BYTES = b"\x89PNG\r\n\x1a\n" + b"\x00" * 16


@pytest.mark.parametrize(
    "extension,payload",
    [(".jpg", _JPEG_MAGIC_BYTES), (".png", _PNG_MAGIC_BYTES)],
)
def test_bug4_detect_images_finds_both_extensions(
    tmp_path, extract_report_data, extension, payload
):
    """Gemini's ``gemini-2.5-flash-image`` fallback returns PNG bytes; the agent
    now writes ``threat-*.png`` when the MIME is ``image/png``. detect_images
    must accept both ``.jpg`` (canonical) and ``.png`` when the bytes match.
    """
    template_dir = tmp_path / "templates"
    template_dir.mkdir()
    target_dir = tmp_path / "target"
    target_dir.mkdir()

    (target_dir / f"threat-risk-funnel{extension}").write_bytes(payload)

    images = extract_report_data.detect_images(target_dir, template_dir)

    assert images["funnel_image_path"].endswith(f"threat-risk-funnel{extension}"), (
        f"detect_images must find threat-risk-funnel{extension}, "
        f"got {images['funnel_image_path']!r}"
    )


# ---------------------------------------------------------------------------
# Bug 5 — _merge_delta_status at Tier 1/2
# ---------------------------------------------------------------------------

THREATS_MD_WITH_DELTA_STATUS = """# Threat Model

```yaml
---
schema_version: "1.4"
date: "2026-04-24"
---
```

## 7. Recommended Actions

| Finding ID | Status | Component | MAESTRO Layer | Threat | Risk Level | Mitigation |
|------------|--------|-----------|---------------|--------|------------|------------|
| S-1 | UNCHANGED | API | L3 | Auth bypass | Critical | Rotate keys |
| S-2 | NEW | DB | L2 | Data exfil | High | Encrypt |
"""


def test_bug5_merge_delta_status_populates_tier1_findings(extract_report_data):
    """Tier 1 findings (from parse_compensating_controls_md) have no
    delta_status by default. The _merge_delta_status helper must read Section 7
    of threats.md and merge the Status column onto matching findings, so
    compute_delta_counts sees non-zero NEW/UNCHANGED counts.
    """
    findings = [
        {"id": "S-1", "component": "API", "threat": "Auth bypass"},
        {"id": "S-2", "component": "DB", "threat": "Data exfil"},
        {"id": "S-3", "component": "Net", "threat": "Unknown"},  # not in Section 7
    ]

    extract_report_data._merge_delta_status(findings, THREATS_MD_WITH_DELTA_STATUS)

    assert findings[0]["delta_status"] == "UNCHANGED"
    assert findings[1]["delta_status"] == "NEW"
    assert "delta_status" not in findings[2], (
        "Findings not in Section 7 must not have delta_status injected"
    )
