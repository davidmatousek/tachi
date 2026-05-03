---
triad:
  pm_signoff:
    agent: product-manager
    date: 2026-03-21
    status: APPROVED
    notes: "All 12 spec FRs addressed across 3 waves. All 5 user stories mapped. All 8 success criteria achievable. No scope creep. OWASP API Security 2023 gap analysis complete with specific per-agent mappings."
  architect_signoff:
    agent: architect
    date: 2026-03-21
    status: APPROVED
    notes: "Technically sound. STRIDE-per-Element matrix verified across 4 sources. 3-wave sequencing correct. No over-engineering. Schema read-only constraint respected. Data flow diagram faithful to F-003 orchestrator. Constitution check comprehensive."
  techlead_signoff: null
---

# Implementation Plan: STRIDE Threat Agents

**Branch**: `005-stride-threat-agents` | **Date**: 2026-03-21 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `specs/005-stride-threat-agents/spec.md`

## Summary

Validate, complete, and integration-test all 6 STRIDE threat agent prompt files (`agents/stride/*.md`) to ensure they produce component-specific, schema-compliant, framework-grounded findings when dispatched by the orchestrator (F-003). The agents already exist with substantial content (100-116 lines each); this feature validates correctness, fills gaps (OWASP API Security cross-references), and performs end-to-end integration testing against sample architecture input.

## Technical Context

**Language/Version**: Markdown + YAML (no application code — agents are structured prompt files)
**Primary Dependencies**: Orchestrator agent (`agents/orchestrator.md`, F-003 delivered), Finding IR schema (`schemas/finding.yaml` v1.0)
**Storage**: Filesystem only (markdown files in `agents/stride/`)
**Testing**: Validation-by-example — run agents against sample architectures, verify output against schema and quality criteria
**Target Platform**: Any LLM capable of following structured markdown prompts (platform-neutral)
**Project Type**: Content/prompt engineering (not application code)
**Performance Goals**: N/A (no runtime performance — prompt quality measured by output correctness)
**Constraints**: No schema modifications (`schemas/finding.yaml` is stable); agents must work within orchestrator's existing dispatch protocol
**Scale/Scope**: 6 agent files, ~650 total lines of existing content to validate and complete

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. General-Purpose Architecture | PASS | Agents are domain-agnostic threat analysis prompts, applicable to any architecture |
| II. API-First Design | N/A | No API — agents are markdown prompt files |
| III. Backward Compatibility | PASS | No changes to existing schemas or interface contract |
| IV. Concurrency & Data Integrity | N/A | No state management — agents produce stateless findings |
| V. Privacy & Data Isolation | PASS | Agents analyze architecture descriptions, not user data; outputs marked `classification: "confidential"` |
| VI. Testing Excellence | PASS | Validation approach: run against 3 sample architectures, verify 100% schema compliance and component specificity |
| VII. Definition of Done | PASS | 3-step DoD: pushed to branch, tested via sample runs, user-validated via orchestrator integration |
| VIII. Observability & Root Cause | N/A | No runtime operations |
| IX. Git Workflow | PASS | Feature branch `005-stride-threat-agents`, PR required |
| X. Product-Spec Alignment | PASS | Spec approved by PM (APPROVED_WITH_CONCERNS) |
| XI. SDLC Triad Collaboration | PASS | PRD approved by full Triad; spec PM-approved; plan dual-reviewed |

No violations. No complexity tracking needed.

## Project Structure

### Documentation (this feature)

```
specs/005-stride-threat-agents/
├── plan.md              # This file
├── research.md          # Research phase output (completed during /aod.spec)
├── data-model.md        # Validation matrix and agent inventory
├── checklists/
│   └── requirements.md  # Spec quality checklist
└── tasks.md             # Task breakdown (/aod.tasks output)
```

### Source Content (repository root)

```
agents/stride/
├── spoofing.md              # S agent — validate & complete
├── tampering.md             # T agent — validate & complete
├── repudiation.md           # R agent — validate & complete
├── info-disclosure.md       # I agent — validate & complete
├── denial-of-service.md     # D agent — validate & complete
└── privilege-escalation.md  # E agent — validate & complete

schemas/
├── finding.yaml             # Finding IR schema (read-only, no changes)
├── input.yaml               # Input schema (read-only)
└── output.yaml              # Output schema (read-only)

examples/
├── mermaid-agentic-app/     # Primary validation input
├── ascii-web-api/           # Secondary validation input
└── free-text-microservice/  # Tertiary validation input
```

**Structure Decision**: No new directories needed. All work modifies existing agent files in `agents/stride/` and creates validation artifacts in `specs/005-stride-threat-agents/`.

## Components

### Agent Validation Framework

The validation approach has three layers:

**Layer 1: Structural Audit** (per agent)
- Frontmatter fields present and correct (`agent_name`, `category`, `threat_class`, `dfd_targets`, `owasp_references`, `output_schema`)
- Section structure matches canonical organization (purpose, detection scope, patterns, finding template, risk computation, references)
- `dfd_targets` matches STRIDE-per-Element matrix row for this category

**Layer 2: Content Quality** (per agent)
- Detection patterns cover all attack subcategories from PRD FR-7
- Finding template examples demonstrate component-specific threats (not generic)
- Mitigation examples are actionable with specific technology references
- Framework references include OWASP, CWE, and MITRE ATT&CK identifiers
- Risk computation section includes correct OWASP 3x3 matrix

**Layer 3: Integration Validation** (all agents together)
- Run orchestrator against `examples/mermaid-agentic-app/input.md`
- Verify all 6 STRIDE tables have findings in assembled `threats.md`
- Verify coverage matrix shows correct STRIDE-per-Element targeting
- Verify 100% component specificity (zero generic findings)
- Verify risk levels match OWASP 3x3 matrix computations

### STRIDE-per-Element Validation Matrix

Reference table for Layer 1 structural audit — each agent's `dfd_targets` must match:

| Agent | threat_class | dfd_targets (expected) | Existing (verified) |
|-------|-------------|----------------------|---------------------|
| spoofing.md | S | [External Entity, Process] | [External Entity, Process] |
| tampering.md | T | [Process, Data Store, Data Flow] | [Process, Data Store, Data Flow] |
| repudiation.md | R | [External Entity, Process] | [External Entity, Process] |
| info-disclosure.md | I | [Process, Data Store, Data Flow] | [Process, Data Store, Data Flow] |
| denial-of-service.md | D | [Process, Data Store, Data Flow] | [Process, Data Store, Data Flow] |
| privilege-escalation.md | E | [Process] | [Process] |

All 6 agents have correct `dfd_targets`. No corrections needed.

### OWASP Cross-Reference Completeness

Current state — check whether P1 cross-references (OWASP API Security Top 10 2023) are present:

| Agent | OWASP Top 10 2021 | OWASP API Security 2023 | CWE | ATT&CK | Gap |
|-------|-------------------|------------------------|-----|--------|-----|
| spoofing.md | A07:2021 | Missing | CWE-287, 290, 384 | T1078, T1556 | Add API2:2023 |
| tampering.md | A03:2021, A08:2021 | Missing | CWE-345, 352, 494 | T1565 | Add API3:2023 |
| repudiation.md | A09:2021 | Missing | CWE-778, 223, 117 | T1070 | Add API9:2023 |
| info-disclosure.md | A01:2021, A02:2021 | Missing | CWE-200, 209, 532 | T1005 | Add API3:2023 |
| denial-of-service.md | None (cheat sheet only) | Missing | CWE-400, 770, 502 | T1498, T1499 | Add API4:2023 |
| privilege-escalation.md | A01:2021 | Missing | CWE-269, 285, 639, 862 | T1548 | Add API1:2023, API5:2023 |

**Gap**: All 6 agents are missing OWASP API Security Top 10 2023 cross-references. This is a P1 deliverable per the spec.

## Data Flow

```
Architecture Input (any format)
         │
         ▼
┌─────────────────────────────┐
│ Orchestrator (F-003)        │
│  Phase 1: Scope             │
│  - Format detection         │
│  - Component classification │
│  - DFD element assignment   │
└─────────┬───────────────────┘
          │ dispatch per STRIDE-per-Element
          ▼
┌─────────────────────────────┐
│ 6 STRIDE Agents (F-005)     │
│  Each agent:                │
│  1. Receives full arch      │
│  2. Filters by dfd_targets  │
│  3. Applies detection       │
│     patterns                │
│  4. Produces findings       │
│     (IR schema)             │
└─────────┬───────────────────┘
          │ findings per schemas/finding.yaml
          ▼
┌─────────────────────────────┐
│ Orchestrator (F-003)        │
│  Phase 3-4: Assemble        │
│  - Validate risk_level      │
│  - Build STRIDE tables      │
│  - Generate coverage matrix │
│  - Compute risk summary     │
└─────────┬───────────────────┘
          │
          ▼
    threats.md output
```

## Tech Stack

| Component | Technology | Justification |
|-----------|-----------|---------------|
| Agent files | Markdown with YAML frontmatter | Platform-neutral, LLM-agnostic prompt format |
| Schema | YAML | Machine-readable validation contract |
| Validation | Manual review + orchestrator integration run | No automated test framework needed for prompt files |
| Version control | Git | Standard for content versioning |

## Implementation Approach

### Wave 1: Structural Audit (all 6 agents in parallel)

Audit each agent for structural compliance:
1. Verify frontmatter fields match expected schema
2. Verify section order matches canonical structure
3. Verify `dfd_targets` matches STRIDE-per-Element matrix
4. Flag any structural gaps

**Parallelizable**: All 6 agents can be audited simultaneously — no cross-dependencies.

### Wave 2: Content Completion (all 6 agents in parallel)

For each agent, address identified gaps:
1. Add OWASP API Security Top 10 2023 cross-references to frontmatter and references section
2. Verify detection patterns cover all PRD FR-7 subcategories
3. Verify finding template examples demonstrate component-specific threats
4. Verify mitigation examples are actionable (not generic)
5. Add any missing CWE or ATT&CK references identified in gap analysis

**Parallelizable**: Each agent is an independent file — no cross-dependencies between agents.

### Wave 3: Integration Validation (sequential)

End-to-end validation using orchestrator:
1. Run orchestrator against `examples/mermaid-agentic-app/input.md`
2. Verify assembled `threats.md` has all 6 STRIDE tables with findings
3. Verify coverage matrix matches STRIDE-per-Element targeting expectations
4. Verify 100% component specificity (zero generic findings)
5. Verify risk_level computations match OWASP 3x3 matrix
6. Run against secondary inputs (ascii-web-api, free-text-microservice) for broader coverage

**Sequential**: Integration testing requires all agents to be validated first.

### Post-Constitution Re-Check

| Principle | Status | Notes |
|-----------|--------|-------|
| III. Backward Compatibility | PASS | No schema changes; only agent content additions (OWASP API refs) |
| VI. Testing Excellence | PASS | 3 validation inputs; coverage matrix validates targeting accuracy |
| X. Product-Spec Alignment | PASS | All 12 spec FRs addressed; all 8 success criteria measurable |

No violations introduced by design.
