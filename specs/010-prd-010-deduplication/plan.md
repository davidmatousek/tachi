---
triad:
  pm_signoff:
    agent: product-manager
    date: 2026-03-22
    status: APPROVED
    notes: "All 11 FRs trace to plan components. All 3 user stories and 10 acceptance scenarios covered. No scope creep. Full PRD-spec-plan consistency verified."
  architect_signoff:
    agent: architect
    date: 2026-03-22
    status: APPROVED_WITH_CONCERNS
    notes: "Technically sound. Both PRD High concerns resolved (Section 4a numbering, cell model unification). 3 medium findings on schema versioning strategy — addressable during task creation: bump schema_version to 1.1, describe Section 4a as numbered section in interface contract."
  techlead_signoff: null
---

# Implementation Plan: Deduplication & Risk Rating

**Branch**: `010-prd-010-deduplication` | **Date**: 2026-03-22 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `specs/010-prd-010-deduplication/spec.md`

## Summary

Add cross-agent finding deduplication, correlation tracking, and enhanced coverage matrix to the orchestrator's assembly phase. Five deterministic correlation rules detect when STRIDE and AI agents produce overlapping findings on the same component. Correlated findings are grouped in a new output section while original findings are preserved for audit. Coverage matrix and risk summary reflect deduplicated counts.

All changes are prompt-only — extending existing markdown and YAML files. No application code.

## Technical Context

**Language/Version**: Markdown + YAML (knowledge system — prompt files, schemas, templates)
**Primary Dependencies**: Existing orchestrator prompt (`agents/orchestrator.md`), Finding IR schema (`schemas/finding.yaml`), Output schema (`schemas/output.yaml`), Output template (`templates/threats.md`), Interface contract (`docs/INTERFACE-CONTRACT.md`)
**Storage**: Filesystem (markdown and YAML files)
**Testing**: Manual validation via orchestrator integration runs against example architectures
**Target Platform**: Any LLM capable of following structured prompt instructions
**Project Type**: Knowledge system (no compiled code)
**Performance Goals**: N/A (prompt-based, no runtime performance targets)
**Constraints**: Prompt-only implementation; deterministic rule-based matching; single-pass assembly; backward compatible with existing output schema v1.0
**Scale/Scope**: ~100–150 lines added to orchestrator prompt; ~30 lines added to output template; ~20 lines added to output schema; ~10 lines updated in interface contract

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. General-Purpose Architecture | PASS | Correlation rules are domain-neutral (STRIDE × AI category pairing). No security-domain-specific logic in core — rules are defined in orchestrator prompt, which is the threat modeling domain. |
| II. API-First Design | N/A | No API endpoints involved. This is a prompt-file change. |
| III. Backward Compatibility | PASS | Output format changes are additive. New Section 4a is inserted; existing 7-section numbering preserved. Existing example outputs remain valid. |
| IV. Concurrency & Data Integrity | N/A | No concurrent state. Orchestrator runs single-pass. |
| V. Privacy & Data Isolation | N/A | No user data or authentication involved. |
| VI. Testing Excellence | PASS | Validation via orchestrator integration runs against `examples/mermaid-agentic-app/input.md` and `examples/ascii-web-api/input.md`. |
| VII. Definition of Done | PASS | Will be verified during `/aod.deliver`. |
| VIII. Observability & Root Cause Analysis | N/A | No runtime services or logging involved. |
| IX. Git Workflow | PASS | Feature branch `010-prd-010-deduplication` created. Will PR before merge. |
| X. Product-Spec Alignment | PASS | Spec has PM sign-off (APPROVED_WITH_CONCERNS). Plan will get dual sign-off. |
| XI. SDLC Triad Collaboration | PASS | Following Triad workflow: `/aod.define` → `/aod.plan` → `/aod.build`. |

## Components

### Component 1: Orchestrator Prompt — Correlation Detection Phase

**File**: `agents/orchestrator.md`
**Type**: Extend existing Phase 3 (Determine Countermeasures)
**Purpose**: Add correlation detection logic after all agent findings are collected and risk-validated, before coverage matrix generation.

**New section** inserted between AI Threat Table Assembly and Phase 4:

1. **Correlation Rule Table**: Define 5 deterministic rules mapping STRIDE-to-AI category pairs:

   | Rule | STRIDE Category | AI Category | Correlation Basis |
   |------|----------------|-------------|-------------------|
   | CR-1 | Tampering (T) | Data-Poisoning (LLM) | Data integrity |
   | CR-2 | Privilege-Escalation (E) | Agent-Autonomy (AG) | Excessive permissions |
   | CR-3 | Info-Disclosure (I) | Prompt-Injection (LLM) | Information leakage |
   | CR-4 | Repudiation (R) | Agent-Autonomy (AG) | Accountability gaps |
   | CR-5 | Denial-of-Service (D) | Tool-Abuse (AG) | Resource exhaustion |

2. **Correlation Detection Algorithm**:
   - Group all findings by target component
   - Within each component group, check each cross-category finding pair against the 5 rules
   - When a match is found, create a correlation group (CG-N)
   - If multiple rules match findings on the same component, merge all matched findings into one group
   - Each finding belongs to at most one correlation group

3. **Correlation Group Assembly**:
   - Assign sequential IDs: CG-1, CG-2, ...
   - Risk level = highest among member findings
   - Threat summary = each agent perspective prefixed by category name
   - Store correlation groups for use in Phase 4 (coverage matrix, risk summary)

4. **Self-Check**: Verify no finding appears in more than one group; verify all group member IDs exist in STRIDE/AI tables.

### Component 2: Output Template — Correlated Findings Section

**File**: `templates/threats.md`
**Type**: Add new Section 4a between AI Threat Tables (Section 4) and Coverage Matrix (Section 5)
**Purpose**: Display correlation groups in a dedicated section preserving existing section numbering.

**Section structure**:

```markdown
## 4a. Correlated Findings

| Group | Findings | Component | Threat Summary | Risk Level |
|-------|----------|-----------|----------------|------------|
| CG-1  | T-2, LLM-1 | LLM Agent Orchestrator | Tampering: data corruption risk; Data-Poisoning: training data manipulation risk | High |
```

When zero correlations: "No cross-agent correlations detected" with empty table header.

### Component 3: Output Template — Enhanced Coverage Matrix

**File**: `templates/threats.md` (Section 5)
**Type**: Modify existing coverage matrix section
**Purpose**: Show deduplicated counts, gap highlighting, and n/a marking.

**Changes**:
- Cell values use deduplicated counts (correlation group = 1 finding per component-category pair)
- Zero-coverage cells: "—" (analyzed, no findings found)
- Non-applicable cells: "n/a" (category not dispatched for component)
- Footnote when correlations exist: "Counts reflect deduplicated findings. N correlation groups merged M individual findings."
- Total row and column reflect deduplicated counts

### Component 4: Output Template — Risk Calibration Matrix

**File**: `templates/threats.md` (Section 6)
**Type**: Add subsection to existing Risk Summary
**Purpose**: Document the OWASP 3×3 matrix prominently in the output for reader verification.

**Addition**: A "Risk Calibration Matrix" subsection before the risk summary table, showing the 3×3 matrix. The existing matrix reference in the template header is already present; this formalizes it as a named subsection with the note "Risk summary counts below reflect deduplicated findings."

### Component 5: Output Template — Deduplicated Risk Summary

**File**: `templates/threats.md` (Section 6)
**Type**: Modify existing Risk Summary table
**Purpose**: Show deduplicated counts with raw count parenthetical.

**Changes**:
- Count column uses deduplicated finding count
- Parenthetical shows raw count when different: e.g., "5 (7 raw)"
- Percentage column based on deduplicated total

### Component 6: Orchestrator Prompt — Enhanced Phase 4

**File**: `agents/orchestrator.md`
**Type**: Modify existing Phase 4 (Assess)
**Purpose**: Update coverage matrix generation and risk summary computation to use deduplicated counts.

**Changes to Coverage Matrix Generation**:
- When computing cell counts, check if any findings in the cell belong to a correlation group
- Correlation group members contribute 1 to the cell count collectively (not individually)
- Apply three-state cell model: count (deduplicated), "—" (analyzed, clean), "n/a" (not applicable)
- Add footnote generation when correlation groups > 0

**Changes to Risk Summary**:
- Count deduplicated findings (correlation group = 1) instead of raw findings
- Show parenthetical raw count when different
- Compute percentages from deduplicated total

**Changes to Recommended Actions**:
- No change to sorting or content — recommended actions list all individual findings, not correlation groups (each finding's mitigation is specific to its category perspective)

**Changes to Output Structural Validation Checklist**:
- Add check: Section 4a (Correlated Findings) is present
- Add check: Coverage matrix counts match deduplicated totals
- Add check: Risk summary counts match deduplicated totals

### Component 7: Output Schema Update

**File**: `schemas/output.yaml`
**Type**: Extend existing schema
**Purpose**: Add Correlated Findings section to the schema definition.

**New section entry** (inserted between AI Threat Tables and Coverage Matrix):

```yaml
- name: Correlated Findings
  required: true
  description: >
    Cross-agent correlation groups where findings from different
    categories target the same component for related threats.
  row_fields:
    - group_id
    - findings
    - component
    - threat_summary
    - risk_level
```

**Coverage Matrix update**: Add `dedup_note` field to describe footnote behavior.

### Component 8: Interface Contract Update

**File**: `docs/INTERFACE-CONTRACT.md`
**Type**: Modify Section 3 (AI Extension Dispatch Rules) and Section 4 (Output Specification)
**Purpose**: Formalize deduplication behavior and new output section.

**Changes**:
- Section 3: Replace the forward-reference sentence about coverage matrix dedup with concrete description of the correlation detection algorithm
- Section 4: Add Section 4a (Correlated Findings) to the Required Sections table, updating section count from 7 to "7 + 1 subsection (4a)"
- Section 4: Document three-state coverage matrix cell model

## Data Flow

```
Architecture Input
        │
        ▼
┌─────────────────────────────┐
│ Orchestrator Phase 1-2      │
│ (unchanged)                 │
│ - Format detection          │
│ - Component classification  │
│ - Agent dispatch            │
└────────┬────────────────────┘
         │
    ┌────┴────────┐
    ▼             ▼
┌─────────┐  ┌──────────┐
│ STRIDE   │  │ AI       │
│ Agents   │  │ Agents   │
│ (6)      │  │ (5)      │
└────┬────┘  └────┬─────┘
     │            │
     └─────┬──────┘
           │ all findings (IR schema)
           ▼
┌─────────────────────────────┐
│ Phase 3: Determine          │
│ Countermeasures              │
│ (extended)                  │
│                             │
│ 1. Collect findings         │
│ 2. Validate risk levels     │  ◄── existing
│ 3. Assemble STRIDE tables   │
│ 4. Assemble AI tables       │
│ 5. *** NEW: Correlation ***  │  ◄── NEW
│    - Group by component     │
│    - Match against 5 rules  │
│    - Create CG-N groups     │
│    - Self-check             │
│ 6. Assemble Section 4a      │  ◄── NEW
└────────┬────────────────────┘
         │
         ▼
┌─────────────────────────────┐
│ Phase 4: Assess              │
│ (modified)                  │
│                             │
│ 1. Coverage matrix          │
│    (deduplicated counts,    │  ◄── MODIFIED
│     "—" / "n/a" cells,     │
│     footnote)               │
│ 2. Risk Calibration Matrix  │  ◄── NEW
│ 3. Risk summary             │
│    (dedup counts + raw      │  ◄── MODIFIED
│     parenthetical)          │
│ 4. Recommended actions      │  (unchanged)
│ 5. Structural validation    │
│    (+ Section 4a check)     │  ◄── MODIFIED
└────────┬────────────────────┘
         │
         ▼
   threats.md output
   (7 sections + Section 4a)
```

## Tech Stack

| Technology | Purpose |
|-----------|---------|
| Markdown prompt | Orchestrator prompt extension — platform-agnostic |
| YAML schema | Output validation contract update |
| Markdown template | Output format specification |
| OWASP 3×3 Matrix | Risk calibration documentation (already implemented) |

## Project Structure

### Documentation (this feature)

```
specs/010-prd-010-deduplication/
├── plan.md              # This file
├── research.md          # Research phase output (completed during spec)
├── spec.md              # Feature specification (PM approved)
├── checklists/
│   └── requirements.md  # Spec quality checklist
└── tasks.md             # Task breakdown (pending)
```

### Source Files (repository root)

```
agents/
└── orchestrator.md          # MODIFY: Add correlation detection (Phase 3) + enhance Phase 4

templates/
└── threats.md               # MODIFY: Add Section 4a, enhance Section 5 + 6

schemas/
└── output.yaml              # MODIFY: Add Correlated Findings section schema

docs/
└── INTERFACE-CONTRACT.md    # MODIFY: Formalize dedup in Sections 3 + 4
```

**Structure Decision**: No new files created. All changes modify existing files. This follows the pattern of F-003 (orchestrator), F-005 (STRIDE agents), and F-007 (AI agents) where features extend the prompt and schema infrastructure.

## Complexity Tracking

No constitution violations to justify. All changes are additive extensions to existing files within the established knowledge system pattern.
