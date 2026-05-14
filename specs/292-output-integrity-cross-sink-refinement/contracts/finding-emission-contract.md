# Contract: OI-{N} Finding Emission Preservation

**Feature**: F-292
**Phase**: 1 (Design)
**Date**: 2026-05-14

This contract codifies the **schema invariance and emission-preservation invariants** that the F-292 implementation must honor.

---

## 1. Schema Invariance (FR-011, SC-011)

**Invariant**: `schemas/finding.yaml` MUST be byte-identical pre/post merge of F-292.

**Verification**:
```bash
git diff main -- schemas/finding.yaml
# Expected: empty output (no modifications)
```

**Schema version field**: `schema_version: "1.8"` (current post-F-4 state). UNCHANGED.

**Finding-id pattern**: `^(S|T|R|I|D|E|AG|LLM|AGP|OI|MI|TE)-\d+$` at line 18. UNCHANGED.

**`OI` prefix reuse**: New Cat 6 findings emit with `OI-{N}` ids — same prefix as Cat 1–5. No new prefix introduced (preempts R4 risk: `OQ-{N}` pushback).

**Rationale (per ADR-032 D3 inheritance)**: The no-schema-bump status is the *operational signal* that the signal-class identity claim is upheld. A schema bump would implicitly claim cross-sink refinement is a distinct signal class — contradicting the enrichment rationale.

---

## 2. Source-Attribution Populator Contract Preservation

**Invariant**: Every new Cat 6 `OI-{N}` finding MUST carry a populated `source_attribution` array per F-1 / ADR-030 Decision 1.

**Required `source_attribution` fields** (each finding):

```yaml
source_attribution:
  - taxonomy: OWASP_LLM_2025
    id: LLM08:2025  # Vector and Embedding Weaknesses (primary)
    relationship: primary
  - taxonomy: OWASP_LLM_2025
    id: LLM05:2025  # Improper Output Handling (cross-anchor)
    relationship: related
  - taxonomy: CWE
    id: CWE-943  # Improper Neutralization of Special Elements in Data Query Logic
    relationship: primary
  - taxonomy: CWE
    id: CWE-89  # SQL Injection (taxonomic neighbor)
    relationship: related
```

**Referential integrity** (per ADR-028 / F-A2 contract): Every `(taxonomy, id)` pair MUST resolve against `schemas/taxonomy/{taxonomy}.yaml`. CWE-943 confirmed present at `schemas/taxonomy/cwe.yaml:238` (per spec research codebase analysis).

**Inheritance**: F-292's host agent (`output-integrity`) is the canonical populator per ADR-030 D1. F-292 does NOT regress to the F-5/F-6/F-A3-deferral pattern. The populator-wiring contract is preserved end-to-end.

---

## 3. Severity Range (per ADR-030 D1 inheritance)

**Cat 6 finding severity targets**: HIGH severity bracket (matching LLM08:2025 baseline OWASP severity assessment).

**Justification**: Vector-DB tenant-scoping bypass functionally equivalent to SQL injection across tenant boundaries; same impact as Cat 2 server-side execution sinks but distinct CWE family.

**Computed via existing F-1 severity-bands skill reference** (`.claude/skills/tachi-output-integrity/references/severity-bands.md` — unchanged by F-292). The severity computation logic is inherited; F-292 contributes only the trigger-keyword and indicator content that feeds the existing computation.

---

## 4. F-292 Adds 22-File Zero-Edit Invariant Extension

**Pre-F-292 invariant (per ADR-032 / ADR-034 / ADR-035 lineage)**: 22 frozen tier files + 11 frozen companion files + all post-F-1/F-2/F-3/F-4/F-5/F-6 hosts unchanged.

**F-292 invariant extension (24+2 file zero-edit)**:
- 22 frozen tier files: unchanged
- 11 frozen companion files: unchanged
- F-1 host (`output-integrity.md`): MODIFIED (≤10 line cross-link prose)
- F-1 companion (`tachi-output-integrity/references/detection-patterns.md`): MODIFIED (Cat 6 + Gap 3 subsection)
- All other hosts (F-2 / F-3 / F-4 / F-5 / F-6 / F-7 / etc.): unchanged
- All other companions: unchanged

**Verification**:
```bash
# Confirm no edits to non-F-1 host agents
git diff main -- .claude/agents/tachi/ | grep -E "^\+\+\+ b/" | grep -v "output-integrity.md"
# Expected: empty output

# Confirm no edits to non-F-1 companion skill references
git diff main -- .claude/skills/ | grep -E "^\+\+\+ b/" | grep -v "tachi-output-integrity"
# Expected: empty output
```

**Special case (FR-010 catch-all + PM L-1 resolution)**: Explicit grep for F-4 trust-exploitation to verify the catch-all covers the case:
```bash
git diff main -- .claude/agents/tachi/human-trust-exploitation.md
# Expected: empty output (no modifications to F-4 agent file)

git diff main -- .claude/skills/tachi-human-trust-exploitation/
# Expected: empty output (no modifications to F-4 skill references)
```

---

## 5. Backward-Compatibility Test Harness Coverage

**Existing harness**: `tests/scripts/test_backward_compatibility.py` (per ADR-021).

**Required test runs**:

```bash
# 5 non-qualifying baselines must reproduce byte-identical (SC-004)
SOURCE_DATE_EPOCH=1700000000 pytest tests/scripts/test_backward_compatibility.py::test_web_app_baseline_byte_identical
SOURCE_DATE_EPOCH=1700000000 pytest tests/scripts/test_backward_compatibility.py::test_microservices_baseline_byte_identical
SOURCE_DATE_EPOCH=1700000000 pytest tests/scripts/test_backward_compatibility.py::test_ascii_web_api_baseline_byte_identical
SOURCE_DATE_EPOCH=1700000000 pytest tests/scripts/test_backward_compatibility.py::test_mermaid_agentic_app_baseline_byte_identical
SOURCE_DATE_EPOCH=1700000000 pytest tests/scripts/test_backward_compatibility.py::test_free_text_microservice_baseline_byte_identical

# Multi-agent baseline cross-link no-emission verification (SC-003)
SOURCE_DATE_EPOCH=1700000000 pytest tests/scripts/test_backward_compatibility.py::test_agentic_app_oi_scoped_byte_identical
```

**Test invocation lock-step** (per KB Entry 3 / F-256 institutional lesson): if any test module is added, both `tests/scripts/tachi-pytest.yml` `paths:` entries AND the `python -m pytest` invocation must be updated in the same commit. **F-292 likely adds no new test modules** (uses existing harness with existing baselines + 1 new optional baseline). If a test for the new `multi-tenant-rag-app/` baseline is added, the lock-step rule applies.

---

## 6. Acceptance Tests

| Contract Invariant | Acceptance Test | Spec Anchor |
|---|---|---|
| `schemas/finding.yaml` unchanged | `git diff main -- schemas/finding.yaml` empty | FR-011 + SC-011 |
| `OI-{N}` prefix reused | New Cat 6 findings have ids matching `^OI-\d+$` | FR-001 + FR-011 |
| `source_attribution` populated | Every new finding has non-empty `source_attribution` array with primary OWASP + primary CWE | FR-003 |
| Cat 6 severity in HIGH bracket | Severity score for vector-DB tenant-bypass finding ≥ HIGH threshold | A-6 (existing detection workflow) |
| 22+2 file zero-edit invariant | Structural diff of threat-agent + companion-skill-ref surfaces shows only `output-integrity.md` and `detection-patterns.md` modified | FR-010 + SC-010 |
| 5 non-qualifying baselines byte-identical | pytest backward-compat harness PASS on 5 non-qualifying baselines | SC-004 |
| Multi-agent baseline OI-scoped byte-identical | pytest backward-compat harness PASS on `agentic-app/` OI-scoped finding subset | SC-003 |
