"""Tests for Issue #198: source_attribution must be visible to F-B at all tiers.

Background: Feature 194 / F-B's gate predicate reads ``source_attribution`` off
each finding dict. Only ``parse_threats_findings`` attaches the field (via the
Section 9 YAML block in ``threats.md``). When the full pipeline has produced
``compensating-controls.md`` (Tier 1) or ``risk-scores.md`` (Tier 2), the
findings passed downstream come from ``parse_compensating_controls_md`` or
``parse_risk_scores_findings`` — neither reads Section 9. Result:
``has-source-attribution`` stayed false on every real pipeline run that had
cc.md or rs.md, silently omitting Section 10 from the PDF.

The fix merges ``source_attribution`` from Section 9 onto cc/rs findings after
parsing, keyed by finding ID, via a new ``_merge_source_attribution`` helper
on ``extract-report-data.py``. These tests exercise that helper directly — no
fixture pipeline required — and verify the three relevant cases: present
Section 9 with matching IDs, present Section 9 without matching IDs, and
absent Section 9 (no-op preserving the pre-fix gate=false contract).
"""

import pytest


SECTION_9_ON_TWO_FINDINGS = """---
schema_version: "1.5"
---

# Threat Model

## 7. Findings

| ID | … |

## 9. Source Attribution

```yaml
S-1:
  - {taxonomy: owasp, id: A07, relationship: primary}
  - {taxonomy: cwe, id: CWE-522, relationship: primary}
I-1:
  - {taxonomy: owasp, id: A02, relationship: primary}
```
"""

SECTION_9_PRESENT_BUT_EMPTY = """---
schema_version: "1.5"
---

## 9. Source Attribution

```yaml
```
"""

NO_SECTION_9 = """---
schema_version: "1.5"
---

## 7. Findings

| ID | … |

(no Section 9 here)
"""


def _make_tier1_findings() -> list[dict]:
    """Minimal finding dicts shaped like ``parse_compensating_controls_md`` output.

    Only the ``id`` key is required by ``_merge_source_attribution``; other
    keys are included to keep the shape realistic for the reader.
    """
    return [
        {"id": "S-1", "title": "API key spoofing", "risk_level": "Critical"},
        {"id": "I-1", "title": "Credential disclosure", "risk_level": "Critical"},
        {"id": "T-3", "title": "Config tampering", "risk_level": "Medium"},
    ]


def _make_tier2_findings() -> list[dict]:
    """Minimal finding dicts shaped like ``parse_risk_scores_findings`` output."""
    return [
        {"id": "S-1", "title": "API key spoofing", "composite_score": 8.5},
        {"id": "I-1", "title": "Credential disclosure", "composite_score": 8.2},
        {"id": "T-3", "title": "Config tampering", "composite_score": 5.1},
    ]


def test_merge_attaches_attribution_on_matching_tier_1_findings(extract_report_data):
    """Tier 1 cc findings gain source_attribution from Section 9 by ID match.

    Pre-fix: findings from ``parse_compensating_controls_md`` never carried
    source_attribution, so F-B's gate stayed false even when Section 9 was
    populated. The fix merges attribution onto cc findings keyed by ID.
    """
    findings = _make_tier1_findings()
    extract_report_data._merge_source_attribution(findings, SECTION_9_ON_TWO_FINDINGS)

    assert findings[0]["source_attribution"] == [
        {"taxonomy": "owasp", "id": "A07", "relationship": "primary"},
        {"taxonomy": "cwe", "id": "CWE-522", "relationship": "primary"},
    ]
    assert findings[1]["source_attribution"] == [
        {"taxonomy": "owasp", "id": "A02", "relationship": "primary"},
    ]
    assert "source_attribution" not in findings[2], (
        "T-3 has no Section 9 entry — the conditional-key semantic must hold "
        "(absent → key omitted, not empty list)"
    )


def test_merge_attaches_attribution_on_matching_tier_2_findings(extract_report_data):
    """Same contract on Tier 2 rs findings — the helper is tier-agnostic."""
    findings = _make_tier2_findings()
    extract_report_data._merge_source_attribution(findings, SECTION_9_ON_TWO_FINDINGS)

    assert findings[0]["source_attribution"] == [
        {"taxonomy": "owasp", "id": "A07", "relationship": "primary"},
        {"taxonomy": "cwe", "id": "CWE-522", "relationship": "primary"},
    ]
    assert findings[1]["source_attribution"] == [
        {"taxonomy": "owasp", "id": "A02", "relationship": "primary"},
    ]
    assert "source_attribution" not in findings[2]


def test_merge_is_noop_when_section_9_absent(extract_report_data):
    """No Section 9 header → every finding stays without source_attribution.

    Regression guard: this is the backward-compat byte-identity path (SC-002).
    Baselines that don't carry Section 9 MUST produce byte-identical PDFs
    before and after the fix, which requires the merge to leave findings
    untouched when threats.md has no Section 9 header at all.
    """
    findings = _make_tier1_findings()
    extract_report_data._merge_source_attribution(findings, NO_SECTION_9)
    for finding in findings:
        assert "source_attribution" not in finding


def test_merge_is_noop_when_section_9_header_present_but_block_empty(extract_report_data):
    """Section 9 header present with empty YAML fence → still a no-op.

    The underlying ``_extract_source_attribution_block`` returns ``{}`` (not
    ``None``) in this case. The merge must still leave findings untouched.
    """
    findings = _make_tier1_findings()
    extract_report_data._merge_source_attribution(findings, SECTION_9_PRESENT_BUT_EMPTY)
    for finding in findings:
        assert "source_attribution" not in finding


def test_merge_leaves_unmatched_findings_untouched(extract_report_data):
    """Findings whose IDs are not in Section 9 must NOT gain the key.

    Conditional-key semantic per Feature 104 delta_status precedent: absent-
    from-Section-9 → key omitted entirely (not ``source_attribution: []``).
    """
    findings = [
        {"id": "D-7", "title": "Only in findings, not in Section 9"},
        {"id": "E-2", "title": "Also unmatched"},
    ]
    extract_report_data._merge_source_attribution(findings, SECTION_9_ON_TWO_FINDINGS)
    for finding in findings:
        assert "source_attribution" not in finding


def test_gate_flips_true_after_merge_when_section_9_matches(extract_report_data):
    """End-to-end on the gate: merge → compute_has_source_attribution flips true.

    Combines the merge helper with the F-B gate predicate to prove the round
    trip: unattributed cc findings + populated Section 9 → gate fires true,
    unblocking Section 10 rendering downstream.
    """
    findings = _make_tier1_findings()
    assert extract_report_data.compute_has_source_attribution(findings) is False
    extract_report_data._merge_source_attribution(findings, SECTION_9_ON_TWO_FINDINGS)
    assert extract_report_data.compute_has_source_attribution(findings) is True


def test_gate_stays_false_after_merge_when_section_9_absent(extract_report_data):
    """No Section 9 → merge no-ops → gate stays false. Backward-compat SC-002."""
    findings = _make_tier1_findings()
    extract_report_data._merge_source_attribution(findings, NO_SECTION_9)
    assert extract_report_data.compute_has_source_attribution(findings) is False
