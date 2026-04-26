# Finding IR Contract: TE-{N} (Feature 224 — `human-trust-exploitation`)

**Phase**: 1 (Design & Contracts)
**Schema version**: 1.8 (post-bump per FR-011)
**Date**: 2026-04-26

## Contract Shape

```yaml
id: "TE-{N}"                          # monotonically increasing per run; TE prefix new in schema 1.8
category: "agentic"                   # existing enum value — unchanged (Q3 binding)
title: "{pattern_category}: {short_summary}"
                                       # e.g., "Undisclosed AI Authorship: customer-support chatbot lacks AI-generation disclosure banner"
severity: "low" | "medium" | "high" | "critical"
                                       # OWASP 3×3 matrix via severity-bands-shared.md (deterministic per NFR-001)
component: "{DFD Process component name}"
                                       # the specific Process component the agent identified
description: "{2-4 sentence threat description}"
                                       # MUST distinguish authorship-disclosure / authority-attestation / persuasion-manipulation / persona-boundary / synthetic-relationship
mitigation: "{specific named mechanism}"
                                       # MUST name at least one specific AI-disclosure / confidence-calibration / refusal-pattern / persona-boundary / synthetic-relationship-safeguard mechanism
                                       # NFR-007: neutral framing ("Implement X" / "Configure Y" / "Enable Z"); no persuasive language

references:
  - "OWASP ASI09:2026"                # primary framework reference
  - "https://cwe.mitre.org/data/definitions/{CWE_NUMBER}.html"
                                       # per applicable pattern category

source_attribution:                   # F-A2 schema (Feature 189) — REQUIRED non-empty array
  - {taxonomy: "owasp", id: "ASI09", relationship: "primary"}
                                       # REQUIRED on every TE-{N} finding
  - {taxonomy: "cwe", id: "CWE-{NUMBER}", relationship: "related"}
                                       # per applicable pattern category (CWE-223, CWE-345, CWE-287, CWE-290)
                                       # CWE-451 MUST NOT appear (catalog absent)
                                       # MITRE ATLAS entries MUST NOT appear (no direct trust-exploitation match)
                                       # External regulatory refs (FTC/FDA/ABA/SEC/SB-1001/AARP) MUST NOT appear (not framework-anchored)

maestro_layer: "L7"                   # assigned downstream by orchestrator Phase 1 (existing Feature 084) — agentic-tier default
agentic_pattern: "none" | "<existing enum value>"
                                       # assigned downstream by orchestrator Phase 3.6 (Feature 142)
                                       # CRITICAL R11 INVARIANT: MUST NOT be "trust_exploitation" — that's the agent-to-agent multi-agent topology pattern, NOT the agent-to-human communication-axis pattern from F-4
delta_status: null                    # assigned downstream if baseline present (existing Feature 104)
```

## Per-Pattern-Category source_attribution Templates

### Pattern Category 1: Undisclosed AI Authorship

```yaml
source_attribution:
  - {taxonomy: "owasp", id: "ASI09", relationship: "primary"}
  - {taxonomy: "cwe", id: "CWE-223", relationship: "related"}  # Omission of Security-relevant Information
```

### Pattern Category 2: Authority-Claim Emission Without Confidence/Source Attestation

```yaml
source_attribution:
  - {taxonomy: "owasp", id: "ASI09", relationship: "primary"}
  - {taxonomy: "cwe", id: "CWE-345", relationship: "related"}  # Insufficient Verification of Data Authenticity
```

### Pattern Category 3: Persuasive-Tone Manipulation / Missing Uncertainty Disclosure

```yaml
source_attribution:
  - {taxonomy: "owasp", id: "ASI09", relationship: "primary"}
  - {taxonomy: "cwe", id: "CWE-345", relationship: "related"}  # Insufficient Verification of Data Authenticity
  # Optional: {taxonomy: "cwe", id: "CWE-223", relationship: "related"}  # for missing uncertainty disclosure
```

### Pattern Category 4: Persona-Boundary Violations on Long-Running Dialogues

```yaml
source_attribution:
  - {taxonomy: "owasp", id: "ASI09", relationship: "primary"}
  - {taxonomy: "cwe", id: "CWE-287", relationship: "related"}  # Improper Authentication (architect MEDIUM-2 addition)
  - {taxonomy: "cwe", id: "CWE-290", relationship: "related"}  # Authentication Bypass by Spoofing
```

### Pattern Category 5: Synthetic-Relationship Exploitation

```yaml
source_attribution:
  - {taxonomy: "owasp", id: "ASI09", relationship: "primary"}
  - {taxonomy: "cwe", id: "CWE-223", relationship: "related"}  # missing relationship-context disclosure
  - {taxonomy: "cwe", id: "CWE-290", relationship: "related"}  # impersonation of relationship trust
```

## Hard Invariants (Validator-Enforced)

The following invariants MUST hold on every emitted `TE-{N}` finding. F-A2 `validate_source_attribution()` at orchestrator Phase 4 enforces invariants 1-7. FR-018 grep-checkable test enforces invariant 8.

1. **`id` regex match**: `id` MUST match schema 1.8 `id.pattern`: `^(S|T|R|I|D|E|AG|LLM|AGP|OI|MI|TE)-\d+$`
2. **`category` value**: MUST be `agentic` (existing enum)
3. **`source_attribution` non-empty**: array MUST contain at least one entry
4. **Primary attribution present**: `source_attribution` MUST contain `{taxonomy: owasp, id: ASI09, relationship: primary}`
5. **Catalog-resolvable IDs only**: every `id` value in `source_attribution` MUST be present in the corresponding `schemas/taxonomy/{taxonomy}.yaml`. CWE-451 MUST NOT appear (absent from catalog). MITRE ATLAS entries MUST NOT appear (no direct match). External regulatory references MUST NOT appear (not framework-anchored).
6. **Mitigation specificity**: `mitigation` field MUST name at least one specific mechanism (not generic "disclose AI authorship"); pattern-category-specific mechanisms enumerated in FR-004.
7. **Two-part emission gate**: finding emission requires BOTH AI-agent keyword match AND at least one human-user-facing emission indicator (FR-013); architect/code-reviewer verifies at Wave 1.3 EOD checkpoint and Wave 4 false-positive check.
8. **Naming Disambiguation invariant (R11)**: `agentic_pattern` field, when assigned by orchestrator Phase 3.6, MUST NOT take the value `trust_exploitation` (that's the multi-agent topology pattern from Feature 142, not the F-4 communication-axis pattern). FR-018 grep test verifies no prose synthesis between `AGP-{N}` (multi-agent topology) and `TE-{N}` (human-trust communication axis) findings at threat-report rendering on the regenerated example.

## Soft Invariants (Best-Practice / Code-Reviewer-Enforced)

9. **NFR-006 safe-language patterns**: worked examples in pattern catalog (and any agent-prose example findings) MUST apply all four safe-language patterns:
   - "Hypothetical:" prefix
   - Regulatory citations framed as "for context, not legal interpretation"
   - Non-clinical distress framing (no "suicidal ideation"; use "user expresses high emotional distress")
   - No real institutional/clinician/lawyer/advisor/product names

10. **NFR-007 self-disclosure discipline**: agent prose, mitigation text, and worked examples MUST use neutral mitigation language ("Implement X" / "Configure Y" / "Enable Z") without persuasive framing ("you really should..." / "this is critical to fix immediately"). The agent's voice models the disclosure discipline it recommends.

11. **Vulnerable-population escalation discipline**: findings in pattern category 5 (Synthetic-Relationship Exploitation) MUST cite consumer-protection rationale in description prose AND MUST recommend escalation-to-human path as a baseline mitigation when the architecture indicates vulnerable-population deployment (mental health / eldercare / minors / cognitive-impairment users).

## Test Fixtures

Located in `tests/scripts/fixtures/human_trust_exploitation/`:

### `valid_te_finding.yaml`

Demonstrates a fully-valid `TE-{N}` finding passing all hard invariants:

```yaml
findings:
  - id: "TE-1"
    category: "agentic"
    title: "Undisclosed AI Authorship: hypothetical chatbot lacks AI-generation disclosure"
    severity: "high"
    component: "Customer Support Chatbot"
    description: "The architecture describes a customer-support chatbot emitting responses to end users without a declared AI-generation disclosure mechanism. The Process has an outgoing Data Flow to a 'Customer' External Entity (FR-006 Indicator A). Per OWASP ASI09:2026, undisclosed AI authorship undermines user-side trust calibration and may violate consumer-protection disclosure requirements."
    mitigation: "Implement mandatory AI-generation disclosure banner on every user-facing turn. Configure pre-conversation AI-disclosure splash with explicit consent confirmation. Enable refusal pattern for identity-impersonation challenges."
    references:
      - "OWASP ASI09:2026"
      - "https://cwe.mitre.org/data/definitions/223.html"
    source_attribution:
      - {taxonomy: "owasp", id: "ASI09", relationship: "primary"}
      - {taxonomy: "cwe", id: "CWE-223", relationship: "related"}
    maestro_layer: "L7"
    agentic_pattern: "none"
    delta_status: null
```

### `invalid_attribution_finding.yaml`

Demonstrates rejection cases for the F-A2 referential-integrity validator:

```yaml
findings:
  # Case 1: CWE-451 in source_attribution (MUST be rejected — catalog absent)
  - id: "TE-2"
    category: "agentic"
    source_attribution:
      - {taxonomy: "owasp", id: "ASI09", relationship: "primary"}
      - {taxonomy: "cwe", id: "CWE-451", relationship: "related"}  # INVALID — absent from cwe.yaml
    # ... rest of fields ...

  # Case 2: agentic_pattern = "trust_exploitation" on TE-{N} (MUST be rejected — Naming Disambiguation invariant 8)
  - id: "TE-3"
    category: "agentic"
    agentic_pattern: "trust_exploitation"  # INVALID — that's multi-agent topology, not communication axis
    source_attribution:
      - {taxonomy: "owasp", id: "ASI09", relationship: "primary"}
    # ... rest of fields ...

  # Case 3: empty source_attribution (MUST be rejected — invariant 3)
  - id: "TE-4"
    category: "agentic"
    source_attribution: []  # INVALID — non-empty required
    # ... rest of fields ...
```

## Test Cases (`test_human_trust_exploitation.py`)

| Test name | Verifies |
|-----------|----------|
| `test_regex_matches_te_prefix` | Schema 1.8 `id.pattern` matches `TE-1`, `TE-99`; rejects malformed |
| `test_valid_te_finding_passes_validation` | `valid_te_finding.yaml` passes `validate_source_attribution()` |
| `test_cwe_451_rejected` | Findings with CWE-451 in `source_attribution` are rejected (catalog absent) |
| `test_atlas_in_source_attribution_rejected` | Findings with MITRE ATLAS entries in `source_attribution` are rejected (no direct match) |
| `test_external_regulatory_in_source_attribution_rejected` | Findings with `taxonomy: ftc/fda/aba/sec/regulatory` in `source_attribution` are rejected (not catalog-resolvable) |
| `test_empty_source_attribution_rejected` | Findings with `source_attribution: []` are rejected |
| `test_missing_asi09_primary_rejected` | Findings without `{taxonomy: owasp, id: ASI09, relationship: primary}` are rejected |
| `test_no_agp_te_prose_synthesis` | FR-018 grep test on regenerated `threat-report.md`: `AGP-` and `TE-` prefixes appear in distinct prose blocks (no shared bullet, no shared sentence, no shared synthesis paragraph) when both are present |
| `test_naming_disambiguation_invariant` | TE-{N} findings MUST NOT have `agentic_pattern: "trust_exploitation"` |
