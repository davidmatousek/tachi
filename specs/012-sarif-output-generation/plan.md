---
triad:
  pm_signoff:
    agent: product-manager
    date: 2026-03-22
    status: APPROVED
    notes: "All 12 spec FRs covered with explicit traceability. All 4 user stories aligned. No scope creep. 3-wave delivery strategy sound. 3 components sufficient."
  architect_signoff:
    agent: architect
    date: 2026-03-22
    status: APPROVED_WITH_CONCERNS
    notes: "Technically sound. 2 medium findings addressable in Wave 2: M-01 trust_zone cross-reference from Phase 1 data needs task documentation; M-02 output.yaml update scope (Note row fix only, not CVSS range changes)."
  techlead_signoff: null
---

# Implementation Plan: SARIF Output Generation

**Branch**: `012-sarif-output-generation` | **Date**: 2026-03-22 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/012-sarif-output-generation/spec.md`

## Summary

Extend the orchestrator's Phase 4 (Assess) to produce a `threats.sarif` file alongside `threats.md`. The implementation modifies three files: the orchestrator prompt (new SARIF generation section), the output schema (Note-level severity fix), and a new SARIF reference template. All changes are markdown/YAML prompt instructions — no application code.

## Technical Context

**Language/Version**: Markdown / YAML (prompt-only implementation — no programming languages)
**Primary Dependencies**: SARIF 2.1.0 JSON Schema (OASIS standard), Finding IR schema v1.0, Output schema v1.1
**Storage**: File system — output directory (`YYYY-MM-DD-{phase}/threats.sarif`)
**Testing**: SARIF schema validation via example runs against `examples/mermaid-agentic-app/input.md` and `examples/ascii-web-api/input.md`; manual upload test to GitHub Code Scanning via `codeql/upload-sarif@v3`
**Target Platform**: Any LLM capable of following structured markdown prompts (platform-neutral)
**Project Type**: Knowledge system (orchestrator prompt engineering)
**Performance Goals**: SARIF generation adds no additional orchestrator phases — occurs within Phase 4 alongside existing output generation
**Constraints**: JSON output fidelity from LLM — mitigated by structural self-check; SARIF rule IDs must be stable across tachi versions
**Scale/Scope**: Typical threat models produce <100 findings, well within GitHub's 25,000 result limit

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. General-Purpose Architecture | PASS | SARIF is a standard format — domain-agnostic output |
| II. API-First Design | N/A | No API — prompt-only implementation |
| III. Backward Compatibility | PASS | threats.md unchanged; SARIF is additive |
| IV. Concurrency & Data Integrity | N/A | Single-file output, no concurrent access |
| V. Privacy & Data Isolation | PASS | SARIF contains same data as threats.md (already classified confidential) |
| VI. Testing Excellence | PASS | Validated via example runs and schema validation |
| VII. Definition of Done | PASS | 3-step validation: schema validates, examples produce correct output, GitHub upload succeeds |
| VIII. Observability | N/A | No runtime services |
| IX. Git Workflow | PASS | Feature branch `012-sarif-output-generation` |
| X. Product-Spec Alignment | PASS | PM approved spec; dual sign-off on this plan |
| XI. SDLC Triad | PASS | Following Triad workflow |

## Project Structure

### Documentation (this feature)

```
specs/012-sarif-output-generation/
├── plan.md              # This file
├── research.md          # Research phase output (completed)
├── spec.md              # Feature specification (PM approved)
├── checklists/
│   └── requirements.md  # Spec quality checklist
└── tasks.md             # Task breakdown (next step)
```

### Source Files (repository root — files modified by this feature)

```
agents/
└── orchestrator.md          # MODIFIED — Phase 4 extended with SARIF generation section

schemas/
└── output.yaml              # MODIFIED — Note-level severity fix (none→note, 0.0→0.1)

templates/
└── threats.sarif            # NEW — SARIF 2.1.0 reference template with placeholder structure
```

**Structure Decision**: No new directories. Three file changes in existing locations consistent with tachi's content architecture.

## Components

This feature modifies the orchestrator's prompt instructions. There are no traditional software components — all deliverables are markdown and YAML files.

### Component 1: Orchestrator Phase 4 Extension (`agents/orchestrator.md`)

**What changes**: Add a new "SARIF Output Generation" section to Phase 4, after the existing "Output Structural Validation" section. This section contains:

1. **SARIF Generation Instructions** — Step-by-step prompt instructions for the LLM to produce a `threats.sarif` JSON file from the findings already collected in Phase 3.

2. **Finding IR → SARIF Result Mapping Table** — The canonical field-by-field mapping from spec FR-003, embedded in the orchestrator prompt so the LLM follows it deterministically.

3. **Category → Rule ID Mapping Table** — The canonical mapping from spec FR-004 (resolving the `info-disclosure` → `information-disclosure` naming gap).

4. **Severity Mapping Table** — From spec FR-005 with the Note-level fix (`note`/`"0.1"`).

5. **SARIF Tool Metadata Template** — The `tool.driver` structure from spec FR-006.

6. **Rule Definition Templates** — `reportingDescriptor` structure for each of the 8 threat categories, with `shortDescription`, `fullDescription`, `help.text`, `help.markdown`, and `properties.tags`.

7. **Correlated Finding Instructions** — How to map correlation groups to `relatedLocations[]` and `partialFingerprints.correlationGroup` per spec FR-007.

8. **Fingerprint Computation Instructions** — How to compute `primaryLocationLineHash` from `ruleId` + `component_name` per spec FR-008.

9. **Dual-Location Instructions** — Physical location (input file, startLine: 1) + logical locations (component name, trust zone, DFD kind) per spec FR-011.

10. **JSON Structural Self-Check** — Validation checklist the LLM runs before outputting the SARIF file, per spec FR-010.

**Integration point**: The orchestrator already collects all findings and produces `threats.md` in Phase 4. The SARIF section uses the same finding data — no new data collection needed.

### Component 2: Output Schema Update (`schemas/output.yaml`)

**What changes**: Update the SARIF Severity Mapping comment block (lines 156-164) to fix the Note-level mapping:

- Before: `Note | none | 0.0`
- After: `Note | note | 0.1`

This resolves the Architect's high-priority concern from the PRD review.

### Component 3: SARIF Reference Template (`templates/threats.sarif`)

**What changes**: Create a new reference template showing the complete SARIF 2.1.0 structure with placeholder values. This template serves as documentation and a structural reference (not a runtime template — the orchestrator generates SARIF from prompt instructions, not by filling a template).

The template includes:
- Top-level `$schema`, `version`, `runs` structure
- `tool.driver` with `name`, `semanticVersion`, `informationUri`, `rules[]`
- Example `result` objects showing all mapped fields
- Example `relatedLocations` for correlated findings
- Example `partialFingerprints` with `primaryLocationLineHash`, `findingId/v1`, and `correlationGroup`
- Dual-location example (`physicalLocation` + `logicalLocations[]`)

## Data Flow

```
Architecture Input (5 formats)
        ↓
Phase 1: Scope (extract components, trust boundaries)
        ↓
Phase 2: Determine Threats (dispatch to STRIDE + AI agents)
        ↓
Phase 3: Countermeasures (collect findings, validate, correlate)
        ↓
Phase 4: Assess
  ├── Coverage Matrix (Section 5)
  ├── Risk Summary (Section 6)
  ├── Recommended Actions (Section 7)
  ├── Output Structural Validation
  └── *** SARIF Generation (NEW) ***
        ├── Map findings → SARIF results (FR-003)
        ├── Map categories → SARIF rules (FR-004)
        ├── Map severity → SARIF levels (FR-005)
        ├── Populate tool metadata (FR-006)
        ├── Map correlations → relatedLocations (FR-007)
        ├── Compute partialFingerprints (FR-008)
        ├── Add dual locations (FR-011)
        └── Run JSON structural self-check (FR-010)
        ↓
Output: threats.md + threats.sarif (same directory)
```

## Tech Stack

- **Prompt Engineering**: Markdown instructions in `agents/orchestrator.md`
- **Schema**: YAML (`schemas/output.yaml`)
- **Template**: JSON reference (`templates/threats.sarif`)
- **Validation**: SARIF 2.1.0 JSON Schema (OASIS standard)
- **CI Integration**: `codeql/upload-sarif@v3` GitHub Action

## Implementation Strategy

### Wave 1: Schema + Template (Parallel, No Dependencies)
1. Update `schemas/output.yaml` Note-level severity mapping
2. Create `templates/threats.sarif` reference template

### Wave 2: Orchestrator Extension (Depends on Wave 1 decisions)
3. Add SARIF Generation section to `agents/orchestrator.md` Phase 4
   - Finding → Result mapping instructions
   - Category → Rule mapping table
   - Severity mapping table
   - Tool metadata template
   - Rule definition templates (8 categories)
   - Correlation mapping instructions
   - Fingerprint computation instructions
   - Dual-location instructions
   - JSON structural self-check

### Wave 3: Validation (Depends on Wave 2)
4. Test against `examples/mermaid-agentic-app/input.md` (STRIDE + AI)
5. Test against `examples/ascii-web-api/input.md` (STRIDE-only)
6. Validate SARIF output against SARIF 2.1.0 JSON schema

### P1 Follow-up (After Core Delivery)
7. Add `taxonomies` array for OWASP/CWE frameworks (FR-012)

## Complexity Tracking

No constitution violations. All changes are additive prompt instructions within the existing orchestrator structure.

## Risk Mitigation

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| JSON fidelity — LLM produces malformed JSON | Medium | Medium | FR-010 self-check validates structure before output; SARIF template provides reference |
| Note severity inconsistency across docs | Low | Low | Single source of truth in output.yaml; orchestrator references the mapping table directly |
| Rule ID instability across runs | Low | High | Rule IDs are deterministic from category enum — no LLM variability |
| GitHub Code Scanning rejects SARIF | Low | Medium | Follow GitHub's documented requirements (physicalLocation, security-severity as numeric string) |
