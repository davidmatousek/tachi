# Finding Contract: `MI-{N}` Misinformation Findings

**Feature**: 206 (F-2)
**Status**: Phase 1 design artifact
**Schema**: `schemas/finding.yaml` v1.7 (post-F-2 bump)

## Overview

Every emitted `MI-{N}` finding MUST conform to the canonical Finding IR shape plus the F-A2 `source_attribution` contract. F-2 is the second net-new producer of `source_attribution` after F-1, validating the contract on an independent production-path finding flow with LLM09 primary citation.

## Shape

```yaml
id: "MI-{N}"                          # monotonically increasing per run; MI prefix introduced in schema 1.7
category: "llm"                       # existing enum value — unchanged
title: "{pattern_category}: {short_summary}"
# e.g., "Ungrounded Factual Emission: medical summarizer emits clinical claims without RAG"
# e.g., "Citation Fabrication: legal-research agent emits citations not present in retrieval corpus"
# e.g., "Overreliance: financial advisory agent auto-approves loans without HITL"
severity: "low" | "medium" | "high" | "critical"
# OWASP 3×3 matrix via severity-bands-shared.md; typical distribution:
#   - Ungrounded factual emission / citation fabrication: MEDIUM to HIGH (consumer-facing decision impact)
#   - Overreliance / missing HITL on consumer-facing high-stakes: HIGH to CRITICAL
#   - Overreliance / missing HITL on internal low-stakes: MEDIUM or below
#   - Retrieval-grounding gaps / calibration absence: MEDIUM (architectural hygiene)
component: "{DFD Process component name}"
# e.g., "Medical Summarizer", "Legal Research Agent", "Financial Advisory Agent", "Clinical Decision Support"
description: "{2-4 sentence threat description}"
# Distinguishes among three LLM09 sub-classes per OWASP LLM09:2025 taxonomy:
#   - factual-emission (ungrounded output)
#   - citation-integrity (RAG present but sources not labeled)
#   - decision-overreliance (auto-action without HITL)
mitigation: "{grounding/verification/HITL/calibration mechanism}"
# MUST name a specific mechanism, not generic "ground the LLM":
#   - Ungrounded factual emission → "mandatory RAG grounding with per-claim source attribution"
#   - Citation fabrication → "output-time citation verification against retrieved source URIs"
#   - Overreliance / missing HITL → "human-in-the-loop review queue on decision-critical output"
#   - Retrieval-grounding gaps → "declared retrieval-strength metric (hit-rate, recall@k)"
#   - Confidence-calibration absence → "calibration layer (temperature scaling + ECE monitor)"
references:
  - "OWASP LLM09:2025"
  - "https://cwe.mitre.org/data/definitions/{CWE_NUMBER}.html"
source_attribution:
  - {taxonomy: "owasp", id: "LLM09", relationship: "primary"}   # REQUIRED on every MI-{N} finding
  - {taxonomy: "cwe", id: "CWE-345", relationship: "related"}   # for ungrounded factual emission / citation fabrication / retrieval-grounding gaps / confidence-calibration absence
  - {taxonomy: "cwe", id: "CWE-223", relationship: "related"}   # for overreliance / missing HITL (primary); optional for other categories when factual authenticity is also unverified
maestro_layer: "L5"                   # assigned downstream by orchestrator Phase 1 (existing Feature 084)
agentic_pattern: "none" | "multi-agent"  # assigned downstream by orchestrator Phase 3.6 (existing Feature 142)
delta_status: null                    # assigned downstream if baseline present (existing Feature 104)
```

## Invariants

### Source Attribution

- **MUST** contain at minimum `{taxonomy: owasp, id: LLM09, relationship: primary}` on every `MI-{N}` finding
- **MUST** pass `validate_source_attribution()` at orchestrator Phase 4
- **MUST** use CWE IDs present in `schemas/taxonomy/cwe.yaml`:
  - **CWE-345** (Insufficient Verification of Data Authenticity) — applicable to all 5 pattern categories
  - **CWE-223** (Omission of Security-relevant Information) — primary for overreliance / missing HITL; optional for other categories when factual authenticity is unverified
- **MUST NOT** include `AML.T0042` (confirmed absent from `schemas/taxonomy/mitre-atlas.yaml`)
- **MUST NOT** include NIST AI 600-1 section-level IDs (not catalogued)

### ID Pattern

- **MUST** match schema 1.7 `id.pattern` regex: `^(S|T|R|I|D|E|AG|LLM|AGP|OI|MI)-\d+$`
- **MUST** be monotonically increasing per run, unique across the finding set

### Mitigation Field

- **MUST** name at least one specific grounding, verification, HITL, or calibration mechanism matched to the finding's pattern category
- **MUST NOT** be generic ("ground the LLM", "verify the output", "add HITL")
- **SHOULD** distinguish consumer-facing high-stakes (HIGH/CRITICAL) from internal low-stakes (MEDIUM or below) for overreliance/missing HITL findings

### Two-Part Emission Gate (FR-011)

- The agent **MUST** enforce emission gating: `MI-{N}` finding emission requires BOTH:
  1. LLM trigger keyword match on the Process component, AND
  2. At least one factual-output indicator in the component's description or connected Data Flows
- LLM keyword match alone MUST NOT emit a finding
- Architectures with no qualifying Process emit zero `MI-{N}` findings (no speculation)

## Example Findings

### Example 1: Ungrounded Factual Emission

```yaml
id: "MI-1"
category: "llm"
title: "Ungrounded Factual Emission: Medical Summarizer emits clinical claims without RAG grounding"
severity: "high"
component: "Medical Summarizer"
description: "The Medical Summarizer component produces clinical summaries with factual claims (diagnoses, treatment recommendations, drug interactions) without a declared RAG grounding mechanism. Per OWASP LLM09:2025, ungrounded factual emission in high-stakes clinical contexts presents significant misinformation risk."
mitigation: "Mandatory RAG grounding with per-claim source attribution; add a RetrievalLayer component with declared retrieval-strength metric (hit-rate ≥ 0.85) gating model output; emit confidence-calibrated scores alongside claims."
references:
  - "OWASP LLM09:2025"
  - "https://cwe.mitre.org/data/definitions/345.html"
source_attribution:
  - {taxonomy: "owasp", id: "LLM09", relationship: "primary"}
  - {taxonomy: "cwe", id: "CWE-345", relationship: "related"}
maestro_layer: "L5"
agentic_pattern: "none"
delta_status: null
```

### Example 2: Citation Fabrication

```yaml
id: "MI-2"
category: "llm"
title: "Citation Fabrication: Legal Research Agent emits citations absent from retrieval corpus"
severity: "high"
component: "Legal Research Agent"
description: "The Legal Research Agent runs a RAG pipeline but does not verify output citations against retrieved source URIs. Per OWASP LLM09:2025 citation fabrication sub-class, LLMs are known to emit syntactically plausible but fabricated citations — this presents material risk in legal research contexts where citations are authoritative."
mitigation: "Output-time citation verification against retrieved source URIs; enforce strict citation-token constraint on decoder output limiting citations to the retrieved set; reject outputs whose citations fail URI verification."
references:
  - "OWASP LLM09:2025"
  - "https://cwe.mitre.org/data/definitions/345.html"
source_attribution:
  - {taxonomy: "owasp", id: "LLM09", relationship: "primary"}
  - {taxonomy: "cwe", id: "CWE-345", relationship: "related"}
maestro_layer: "L5"
agentic_pattern: "none"
delta_status: null
```

### Example 3: Overreliance / Missing HITL

```yaml
id: "MI-3"
category: "llm"
title: "Overreliance: Financial Advisory Agent auto-approves loans without HITL review"
severity: "critical"
component: "Financial Advisory Agent"
description: "The Financial Advisory Agent drives automated approve/deny decisions based on LLM output without a human-in-the-loop review gate. Per OWASP LLM09:2025 overreliance sub-class, automated decisions in high-stakes consumer-facing contexts require HITL review to mitigate factual-integrity failures. Missing HITL on loan decisions presents both misinformation risk (factual errors in advice) and undisclosed-AI risk (no provenance on the decision)."
mitigation: "Human-in-the-loop review queue on decision-critical output; risk-threshold-based auto-escalation (decisions above a monetary threshold MUST route to human reviewer); AI-provenance disclosure on all emitted decisions; secondary-verification dual-model ensemble gate on high-stakes recommendations."
references:
  - "OWASP LLM09:2025"
  - "https://cwe.mitre.org/data/definitions/223.html"
  - "https://cwe.mitre.org/data/definitions/345.html"
source_attribution:
  - {taxonomy: "owasp", id: "LLM09", relationship: "primary"}
  - {taxonomy: "cwe", id: "CWE-223", relationship: "related"}
  - {taxonomy: "cwe", id: "CWE-345", relationship: "related"}
maestro_layer: "L5"
agentic_pattern: "none"
delta_status: null
```

## Validation

- **Regex unit test**: `tests/scripts/test_misinformation.py::test_regex_matches_mi_prefix` — confirms schema 1.7 `id.pattern` matches `MI-\d+` and preserves backward compatibility on pre-1.7 prefixes
- **Fixture round-trip**: `tests/scripts/fixtures/misinformation/valid_mi_finding.yaml` — parses and validates without error
- **Negative-case fixture**: `tests/scripts/fixtures/misinformation/invalid_attribution_finding.yaml` — includes AML.T0042 and is rejected by `validate_source_attribution`
- **End-to-end verification**: regenerated `agentic-app/` post-extension surfaces ≥1 `MI-{N}` finding passing all referential-integrity checks (Wave 4 deliverable)
