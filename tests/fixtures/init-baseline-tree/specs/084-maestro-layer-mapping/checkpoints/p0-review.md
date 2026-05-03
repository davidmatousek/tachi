# P0 Checkpoint Review: MAESTRO Layer Mapping (Feature 084)

**Reviewer**: Architect
**Date**: 2026-04-07
**Scope**: Waves 1-2 (Foundation + Pipeline References)
**Gate**: POC Validation / Go-No-Go for Wave 3

---

## Status: APPROVED_WITH_CONCERNS

**Verdict**: The foundation is solid. Proceed to Wave 3 (orchestrator modifications) after addressing 2 medium concerns. No blocking issues.

---

## Review Criteria Results

### 1. Architecture Alignment

**PASS**

The reference file changes correctly define the MAESTRO integration points as designed in plan.md. The data flow is clean:

- Shared reference (`maestro-layers-shared.md`) defines taxonomy + keywords + algorithm
- Schema (`finding.yaml`) defines the IR field
- Dispatch rules (`dispatch-rules.md`) defines the intermediate artifact format
- Output schemas (`output-schemas.md`) defines the output table formats + risk summary subsection
- Finding format (`finding-format-shared.md`) documents the IR field for agent consumers
- SARIF spec (`sarif-specification.md`) defines the SARIF mapping

This matches the Component 1-7 architecture from plan.md. The separation of concerns is correct: shared reference owns definitions, schema owns validation, each pipeline reference file owns its downstream format.

### 2. Schema Consistency

**PASS**

The `maestro_layer` field definition is consistent across all four touchpoints:

| File | Enum Values | Default | Type |
|------|-------------|---------|------|
| `schemas/finding.yaml` | L1-L7 + Unclassified | "Unclassified" | string |
| `finding-format-shared.md` | L1-L7 + Unclassified | "Unclassified" | string (enum) |
| `output-schemas.md` (field completeness) | "L1-L7 or Unclassified" | (implied) | (checklist) |
| `maestro-layers-shared.md` | L1-L7 + Unclassified (algorithm) | "Unclassified" | (reference) |

The enum values use consistent em dash formatting ("L1 — Foundation Model") across all files. The default is consistently "Unclassified" everywhere.

### 3. Backward Compatibility

**PASS**

All changes are additive:

- `finding.yaml`: New optional field with default, no existing fields modified
- Schema version bump: 1.1 -> 1.2 (minor version, correct for additive change)
- Dispatch table: New column added, no existing columns removed or reordered
- STRIDE/AI tables: New column inserted after Component, no existing columns removed
- SARIF: New properties added to `result.properties` with no key conflicts
- Self-checks: Existing checks preserved, new MAESTRO checks added alongside

No breaking changes to existing pipeline behavior.

### 4. Cross-Reference Consistency

**PASS WITH CONCERNS** (see Findings C-001 and C-002 below)

Column positions are consistent across files:

**STRIDE table (standard):**
- `output-schemas.md`: ID | Component | MAESTRO Layer | Threat | Likelihood | Impact | Risk Level | Mitigation
- `finding-format-shared.md`: ID | Component | MAESTRO Layer | Threat | Likelihood | Impact | Risk Level | Mitigation

**STRIDE table (baseline-aware):**
- `output-schemas.md`: ID | Status | Component | MAESTRO Layer | Threat | Likelihood | Impact | Risk Level | Mitigation
- `finding-format-shared.md`: ID | Status | Component | MAESTRO Layer | Threat | Likelihood | Impact | Risk Level | Mitigation

**AI table (standard):**
- `output-schemas.md`: ID | Component | MAESTRO Layer | Threat | OWASP Reference | Likelihood | Impact | Risk Level | Mitigation
- `finding-format-shared.md`: ID | Component | MAESTRO Layer | Threat | OWASP Reference | Likelihood | Impact | Risk Level | Mitigation

**AI table (baseline-aware):**
- `output-schemas.md`: ID | Status | Component | MAESTRO Layer | Threat | OWASP Reference | Likelihood | Impact | Risk Level | Mitigation
- `finding-format-shared.md`: ID | Status | Component | MAESTRO Layer | Threat | OWASP Reference | Likelihood | Impact | Risk Level | Mitigation

**Dispatch table:**
- `dispatch-rules.md`: Component | DFD Type | MAESTRO Layer | STRIDE Categories | AI Categories | Total Agents

All table formats agree on column names and positions. MAESTRO Layer is consistently placed after Component (or after Status when baseline-aware) in finding tables, and after DFD Type in the dispatch table.

**SARIF mapping:**
- `sarif-specification.md`: `result.properties.tags[]` gets `"maestro-layer:{layer-id}"`, `result.properties["maestro-layer"]` gets full layer name
- Consistent with plan.md TD-4 decision

### 5. POC Viability

**PASS**

The foundation is ready for Wave 3:

- The shared reference file is complete with taxonomy, keywords, algorithm, and output format documentation
- The schema is extended with proper validation constraints
- All pipeline reference files have consistent table formats ready for the orchestrator to implement
- The SARIF specification has clear mapping rules for Wave 4 implementation
- Self-checks in dispatch-rules.md and output-schemas.md include MAESTRO validation
- The SARIF self-check in sarif-specification.md includes a MAESTRO layer properties check

The orchestrator agent (Wave 3) has unambiguous instructions in every reference file it consumes.

---

## Findings

### C-001: Frontmatter Example Not Updated to Schema 1.2 (Medium)

**Location**: `.claude/skills/tachi-orchestration/references/output-schemas.md`, lines 24-31, 34-35

**Issue**: The frontmatter code example and field description table still show `schema_version: "1.1"` and the description says `Always "1.1" for this release`. However, the Frontmatter Validation checklist (line 240) was correctly updated to validate `"1.2"`.

This creates a contradiction within the same file: the example says "1.1" but the validation checklist says "1.2". The orchestrator reads both sections and may produce inconsistent output depending on which section it follows.

**Impact**: The orchestrator could generate threats.md with `schema_version: "1.1"` in the frontmatter (following the example) and then fail its own validation checklist (which expects "1.2"). Or it could write "1.2" and ignore the example. Either way, the inconsistency is a source of ambiguity.

**Recommendation**: Update the frontmatter code example to `schema_version: "1.2"` and the field description to `Always "1.2" for this release`. This is a two-line fix.

**Severity**: Medium -- will cause validation confusion during Wave 3 orchestrator implementation.

### C-002: SKILL.md Loading Table Consumer List Incomplete (Medium)

**Location**: `.claude/skills/tachi-shared/SKILL.md`, line 29

**Issue**: The MAESTRO layers entry in the Loading Table lists consumers as `orchestrator, risk-scorer, control-analyzer`. This matches plan.md Component 8 (downstream agent propagation) and the `maestro-layers-shared.md` frontmatter consumers list.

However, the plan.md also identifies the threat-report agent as needing MAESTRO awareness (noted in the architect sign-off on plan.md as a medium concern: "threat-report agent missing from modification list for column awareness"). If threat-report needs MAESTRO layer context for narrative reporting (User Story 5 mentions "narrative threat report" in downstream propagation), it should be listed as a consumer.

**Impact**: The threat-report agent will not know to load the MAESTRO layers reference during Phase 5, which could result in layer data being omitted from narrative reports. This can be addressed in Wave 4 when downstream agent propagation is implemented.

**Recommendation**: Confirm whether threat-report is a consumer of maestro-layers-shared.md. If yes, add it to both the SKILL.md Loading Table and the maestro-layers-shared.md frontmatter consumers list. This is a Wave 3-4 concern, not blocking for Wave 3 start.

**Severity**: Medium -- does not block Wave 3 but should be resolved before Wave 4 downstream propagation.

### C-003: Keyword Collision Risk Between Layers (Low)

**Location**: `.claude/skills/tachi-shared/references/maestro-layers-shared.md`

**Observation**: The keyword "runtime" (L4 - Deployment Infrastructure) could match components like "LLM Runtime" or "Agent Runtime" that might more accurately belong to L1 or L3. Similarly, "index" (L2 - Data Operations) could match database index components that are really L4 infrastructure. The "chain" keyword (L3 - Agent Framework) could match "blockchain" components.

The first-match-wins algorithm and L1-L7 ordering mitigate this: "LLM Runtime" would match L1 first (via "LLM" keyword), and "Agent Runtime" would match L3 (via "agent" -- but "agent" is not actually an L3 keyword; it is only in the AI dispatch keyword list, not MAESTRO keywords). Actually, reviewing more carefully: the MAESTRO L3 keywords do not include "agent" itself. The AI dispatch keywords include "agent" but MAESTRO L3 does not. This means a component named "Agent Runtime" would match L4 (via "runtime"), which may be surprising.

**Impact**: Low. The keyword table is documented as tunable, and the >90% classification rate target (SC-001) will validate coverage during Wave 5 example regeneration. False classifications are correctable by updating keywords.

**Recommendation**: No immediate action needed. During Wave 5 example validation, check whether any components receive surprising classifications and tune keywords if needed. Consider adding "agent" to L3 keywords if the AI dispatch "agent" keyword frequently co-occurs with agent framework components.

**Severity**: Low -- design-as-intended (tunable), validated by success criteria SC-001.

---

## Summary

| Criterion | Result |
|-----------|--------|
| Architecture alignment | PASS |
| Schema consistency | PASS |
| Backward compatibility | PASS |
| Cross-reference consistency | PASS with 2 concerns |
| POC viability | PASS |

**Findings**: 3 total (0 blocking, 2 medium, 1 low)

- **C-001** (Medium): Frontmatter example in output-schemas.md still shows "1.1" -- fix before Wave 3
- **C-002** (Medium): threat-report agent consumer listing -- resolve before Wave 4
- **C-003** (Low): Keyword collision edge cases -- validate during Wave 5

**Go/No-Go**: GO -- proceed to Wave 3 after fixing C-001.
