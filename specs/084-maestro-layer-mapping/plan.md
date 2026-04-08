---
triad:
  pm_signoff:
    agent: product-manager
    date: 2026-04-07
    status: APPROVED
    notes: "All 12 FRs traced to plan components. All 5 user stories implementable. All 5 success criteria have verification paths. All 5 deferred decisions resolved. Zero scope creep."
  architect_signoff:
    agent: architect
    date: 2026-04-07
    status: APPROVED_WITH_CONCERNS
    notes: "3 findings (0 blocking, 2 medium, 1 low). Medium: (1) threat-report agent missing from modification list for column awareness, (2) template files not audited for hardcoded table headers. Low: baseline-aware column position phrasing ambiguous. All 5 deferred decisions correctly resolved. Schema, backward compat, data flow, architecture alignment all pass."
  techlead_signoff: null  # Added by /aod.tasks
---

# Implementation Plan: MAESTRO Layer Mapping

**Branch**: `084-maestro-layer-mapping` | **Date**: 2026-04-07 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `specs/084-maestro-layer-mapping/spec.md`

## Summary

Add CSA MAESTRO seven-layer architectural taxonomy as a classification overlay in Phase 1 of the tachi pipeline. Each component is classified by MAESTRO layer (L1-L7) using keyword matching, and the layer tag propagates passively through all findings to downstream outputs: threats.md tables, risk summary, SARIF, risk-scores.md, and compensating-controls.md. This is a taxonomy overlay — no changes to agent detection logic, scoring formulas, or dispatch rules.

## Technical Context

**Language/Version**: Markdown + YAML (agent definitions, shared references, output templates, schemas)
**Primary Dependencies**: tachi pipeline (orchestrator, 11 threat agents, risk-scorer, control-analyzer, threat-report)
**Storage**: File-based (markdown agent definitions, YAML schemas, markdown output templates)
**Testing**: Manual pipeline execution against 6 example architectures; diff-based regression verification
**Target Platform**: Claude Code agents (AI-powered pipeline)
**Project Type**: Knowledge system (agent definitions + shared references)
**Performance Goals**: Negligible overhead — keyword matching against <100 keywords per component
**Constraints**: Full backward compatibility with all existing pipeline output; all new fields optional
**Scale/Scope**: 7 MAESTRO layers, ~50-80 keywords, 6 example architectures to regenerate

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. General-Purpose Architecture | PASS | MAESTRO is an industry-standard taxonomy, not domain-specific logic |
| II. API-First Design | N/A | No API endpoints — file-based pipeline |
| III. Backward Compatibility | PASS | All new fields optional with "Unclassified" default; existing output unchanged |
| IV. Concurrency & Data Integrity | N/A | No concurrent state mutations |
| V. Privacy & Data Isolation | N/A | No user data involved |
| VI. Testing Excellence | PASS | Diff-based regression testing across 6 example architectures |
| VII. Definition of Done | PASS | Will validate via example regeneration and output comparison |
| VIII. Observability & Root Cause Analysis | N/A | No runtime services |
| IX. Git Workflow | PASS | Feature branch `084-maestro-layer-mapping` created |
| X. Product-Spec Alignment | PASS | Spec has PM sign-off (APPROVED) |
| XI. SDLC Triad Collaboration | PASS | PRD approved by full Triad |

No violations. Proceeding to Phase 0.

## Project Structure

### Documentation (this feature)

```
specs/084-maestro-layer-mapping/
├── plan.md              # This file
├── research.md          # Research phase output
├── data-model.md        # Schema extension design
├── spec.md              # Feature specification (PM approved)
├── checklists/
│   └── requirements.md  # Spec quality checklist
└── tasks.md             # Task breakdown (pending)
```

### Source Code (files to create/modify)

```
# NEW files
.claude/skills/tachi-shared/references/maestro-layers-shared.md  # Shared reference: layer definitions + keywords

# MODIFIED schemas
schemas/finding.yaml                                              # Add maestro_layer field (optional)

# MODIFIED agent definitions
.claude/agents/tachi/orchestrator.md                              # Phase 1 classification + dispatch table + output tables

# MODIFIED orchestration references
.claude/skills/tachi-orchestration/references/dispatch-rules.md   # Dispatch table format with MAESTRO Layer column
.claude/skills/tachi-orchestration/references/output-schemas.md   # Output table formats + Risk by MAESTRO Layer section

# MODIFIED shared references
.claude/skills/tachi-shared/references/finding-format-shared.md   # IR field documentation
.claude/skills/tachi-shared/SKILL.md                              # Loading table for new reference

# MODIFIED downstream agents (passive propagation)
.claude/agents/tachi/risk-scorer.md                               # Propagate maestro_layer field
.claude/agents/tachi/control-analyzer.md                          # Propagate maestro_layer field

# MODIFIED SARIF specification
.claude/skills/tachi-orchestration/references/sarif-specification.md  # MAESTRO tag + property rules

# REGENERATED example outputs (6 examples)
examples/agentic-app/threats.md
examples/web-app/threats.md
examples/microservices/threats.md
examples/ascii-web-api/threats.md
examples/free-text-microservice/threats.md
examples/mermaid-agentic-app/threats.md
```

**Structure Decision**: Knowledge system project — no application code directories. All changes are to agent definitions (markdown), shared references (markdown), schemas (YAML), and output templates (markdown).

## Deferred Technical Decisions (from PRD Architect Review)

These five questions were deferred from PRD to plan. Decisions documented here with rationale.

### TD-1: "Risk by MAESTRO Layer" Subsection Placement

**Decision**: Place as a subsection within Section 6 (Risk Summary), immediately after the existing Risk Calibration Matrix table and before Section 7 (Recommended Actions).

**Rationale**: Risk summary sections are naturally grouped together. Adding a new top-level Section 6a would break the existing section numbering (Section 7 Recommended Actions, Section 8 Delta Summary) and invalidate references in the validation checklist. A subsection within Section 6 keeps the numbering stable while placing layer-based risk data adjacent to the existing risk level breakdown.

**Format**:
```markdown
#### Risk by MAESTRO Layer

| MAESTRO Layer | Finding Count | Highest Severity |
|---------------|---------------|------------------|
| L3 — Agent Framework | 8 | Critical |
| L2 — Data Operations | 3 | High |
| L5 — Security | 2 | Medium |
```

Layers with zero findings are omitted. Rows are ordered by highest severity descending, then by finding count descending.

### TD-2: Backward Compatibility Verification Method

**Decision**: Diff-based regression testing on example architecture outputs.

**Rationale**: Feature flags add complexity for a metadata-only change. Since MAESTRO columns are additive (new columns in existing tables, new subsection in risk summary), a diff-based approach is sufficient: capture pre-change baseline outputs for all 6 examples, implement changes, regenerate outputs, and verify that all content outside the new MAESTRO columns/subsections is identical. This avoids runtime branching logic entirely.

**Verification Process**:
1. Before changes: Save current example outputs as baseline (git stash or separate directory)
2. After changes: Regenerate all 6 example outputs
3. Compare: Strip MAESTRO-specific content (MAESTRO Layer columns, Risk by MAESTRO Layer subsection) from post-change output and diff against baseline
4. Pass criteria: Zero differences in non-MAESTRO content

### TD-3: Schema Version Bump

**Decision**: Bump `schema_version` from `"1.1"` to `"1.2"` in `schemas/finding.yaml` and in the threats.md frontmatter `schema_version` field.

**Rationale**: The addition of `maestro_layer` as an optional field is a backward-compatible schema extension (minor version bump). Consumers that don't recognize the field can safely ignore it. The version bump signals to downstream tools that MAESTRO fields may be present without breaking existing consumers.

**Changes**:
- `schemas/finding.yaml`: `schema_version: "1.2"`
- `output-schemas.md` frontmatter validation: `schema_version` is `"1.2"`
- threats.md frontmatter: `schema_version: "1.2"`

### TD-4: SARIF Properties Merge (Baseline + MAESTRO)

**Decision**: Additive merge — MAESTRO properties are added alongside existing baseline properties with no conflict.

**Rationale**: MAESTRO uses distinct property keys (`maestro-layer` in `properties`, `maestro-layer:{layer}` in `properties.tags`) that do not overlap with baseline properties (`delta_status`, `baseline_run_id` in `partialFingerprints`). The SARIF spec allows arbitrary properties in `result.properties`, so adding new keys alongside existing ones is safe. No merge conflict resolution needed.

**SARIF Result Structure** (combined example):
```json
{
  "ruleId": "S-1",
  "level": "error",
  "partialFingerprints": {
    "findingId/v1": "S-1",
    "primaryLocationLineHash": "a1b2c3d4",
    "baselineRunId": "2026-03-25T12-53-57"
  },
  "properties": {
    "tags": ["security", "stride", "spoofing", "maestro-layer:L5"],
    "maestro-layer": "L5 — Security",
    "delta_status": "NEW"
  }
}
```

### TD-5: Keyword Table Ordering Rationale

**Decision**: Document first-match-wins ordering rationale directly in the MAESTRO shared reference file header.

**Rationale**: The L1-L7 ordering is load-bearing — changing the order changes classification results. The rationale (most specific layers first, most general last) must be co-located with the keyword table so future editors understand the constraint before modifying keywords.

**Documentation**: Include a "Classification Algorithm" section at the top of `maestro-layers-shared.md` explaining:
- Layers are evaluated in L1-L7 order
- First keyword match wins (no multi-layer assignment)
- Order rationale: L1 (Foundation Model) is most specific, L7 (User Interface) is most general
- Changing keyword order changes classification — test against examples after any modification

## Components

### Component 1: MAESTRO Shared Reference File

**File**: `.claude/skills/tachi-shared/references/maestro-layers-shared.md`

A new shared reference file following the Feature 078 pattern. Contains:
- YAML frontmatter (type, name, version, source_schema, consumers)
- Seven-layer taxonomy table (L1-L7) with name, description, example components
- Keyword-to-layer mapping table (case-insensitive keywords per layer)
- Classification algorithm (first-match-wins, "Unclassified" default)

**Keyword Table Design** (derived from CSA MAESTRO framework + PRD examples):

| Layer | Keywords |
|-------|----------|
| L1 — Foundation Model | LLM, language model, GPT, Claude, Gemini, base model, fine-tuned model, model weights, foundation model, inference engine |
| L2 — Data Operations | vector, RAG, embedding, training data, data pipeline, knowledge base, vector DB, vector store, fine-tuning, dataset, corpus, index |
| L3 — Agent Framework | orchestrator, planner, executor, tool dispatch, agent framework, tool server, MCP server, function calling, chain, workflow engine |
| L4 — Deployment Infrastructure | container, runtime, API gateway, load balancer, reverse proxy, CDN, DNS, ingress, kubernetes, docker, serverless, network |
| L5 — Security | auth, WAF, firewall, secrets manager, audit log, guardrail, content filter, rate limit, encryption, RBAC, IAM, access control, security |
| L6 — Agent Ecosystem | multi-agent, agent-to-agent, swarm, delegation, coordination, supervisor, sub-agent, agent registry, agent mesh |
| L7 — User Interface | chat UI, dashboard, admin console, web interface, frontend, user portal, API endpoint, REST API, GraphQL |

### Component 2: Finding IR Schema Extension

**File**: `schemas/finding.yaml`

Add optional `maestro_layer` field after `dfd_element_type`:

```yaml
maestro_layer:
  type: string
  enum:
    - "L1 — Foundation Model"
    - "L2 — Data Operations"
    - "L3 — Agent Framework"
    - "L4 — Deployment Infrastructure"
    - "L5 — Security"
    - "L6 — Agent Ecosystem"
    - "L7 — User Interface"
    - "Unclassified"
  default: "Unclassified"
  description: >
    CSA MAESTRO architectural layer classification for the component.
    Assigned during Phase 1 based on keyword matching against component
    name, description, and DFD type. Propagated passively through all
    downstream phases.
```

### Component 3: Orchestrator Phase 1 Extension

**File**: `.claude/agents/tachi/orchestrator.md`

Modifications to Phase 1 (Scope):
1. Add loading instruction for `maestro-layers-shared.md` in reference loading table
2. After DFD classification, add MAESTRO layer classification step using keyword matching
3. Add MAESTRO Layer column to Component Inventory intermediate output
4. Add MAESTRO Layer column to Dispatch Table intermediate output

Modifications to Phase 4 (Output Assembly):
1. Add MAESTRO Layer column to STRIDE table format (after Component)
2. Add MAESTRO Layer column to AI table format (after Component)
3. Add "Risk by MAESTRO Layer" subsection in Section 6

### Component 4: Dispatch Rules Update

**File**: `.claude/skills/tachi-orchestration/references/dispatch-rules.md`

Add MAESTRO Layer column to dispatch table format:

```
| Component | DFD Type | MAESTRO Layer | STRIDE Categories | AI Categories | Total Agents |
```

Update self-check to validate MAESTRO layer assignments.

### Component 5: Output Schema Update

**File**: `.claude/skills/tachi-orchestration/references/output-schemas.md`

1. Update STRIDE table format — add MAESTRO Layer column after Component (or after Status when baseline-aware)
2. Update AI table format — add MAESTRO Layer column after Component (or after Status when baseline-aware)
3. Add "Risk by MAESTRO Layer" subsection specification in Section 6
4. Update validation checklist to include MAESTRO Layer validation
5. Update `schema_version` to `"1.2"` in frontmatter validation

### Component 6: Finding Format Shared Reference Update

**File**: `.claude/skills/tachi-shared/references/finding-format-shared.md`

Add `maestro_layer` to the table format documentation:
- STRIDE table format gains MAESTRO Layer column
- AI table format gains MAESTRO Layer column
- Document field as optional with "Unclassified" default

### Component 7: SARIF Specification Update

**File**: `.claude/skills/tachi-orchestration/references/sarif-specification.md`

Add MAESTRO layer SARIF extension rules:
- `result.properties.tags[]` gains `"maestro-layer:{layer-name}"` entry
- `result.properties.maestro-layer` gains layer name string value
- Document merge behavior with baseline properties (additive, no conflict)

### Component 8: Downstream Agent Propagation

**Files**: `.claude/agents/tachi/risk-scorer.md`, `.claude/agents/tachi/control-analyzer.md`

Add passive propagation instructions:
- Read `maestro_layer` from input findings if present
- Include in output tables/records without modification
- Default to "Unclassified" if field absent

### Component 9: Shared References Skill Update

**File**: `.claude/skills/tachi-shared/SKILL.md`

Add the new MAESTRO reference file to:
- Domain Coverage section (4th reference file)
- Loading Table (consumers: orchestrator, risk-scorer, control-analyzer)

### Component 10: Example Architecture Regeneration

**Files**: All 6 `examples/*/threats.md` files

Regenerate pipeline output for all 6 example architectures with MAESTRO layer classifications. Verify >90% non-"Unclassified" classification rate per SC-001.

## Data Flow

```
Architecture Input
       │
       ▼
  Phase 1: Scope
  ├─ Extract components
  ├─ Classify DFD types
  ├─ Classify MAESTRO layers (NEW — keyword matching from shared reference)
  ├─ Produce Component Inventory with MAESTRO Layer column (NEW)
  └─ Produce Dispatch Table with MAESTRO Layer column (NEW)
       │
       ▼
  Phase 2: Determine Threats
  └─ Dispatch agents (UNCHANGED — MAESTRO layer is metadata, not dispatch input)
       │
       ▼
  Phase 3: Determine Countermeasures
  ├─ Collect findings from agents
  ├─ Each finding inherits maestro_layer from its target component (NEW)
  └─ Assemble STRIDE and AI tables with MAESTRO Layer column (NEW)
       │
       ▼
  Phase 4: Assess & Output
  ├─ Coverage matrix (UNCHANGED — no MAESTRO column per PRD scope)
  ├─ Risk summary with "Risk by MAESTRO Layer" subsection (NEW)
  ├─ SARIF output with maestro-layer tags and properties (NEW)
  └─ Recommended actions (UNCHANGED)
       │
       ▼
  Downstream Phases (passive propagation)
  ├─ Risk Scoring → risk-scores.md includes maestro_layer (NEW)
  ├─ Controls Analysis → compensating-controls.md includes maestro_layer (NEW)
  └─ Threat Report → threat-report.md passively includes layer if present (NEW)
```

## Tech Stack

- **Content format**: Markdown (agent definitions, shared references, output templates)
- **Schema format**: YAML (finding.yaml)
- **Output format**: Markdown (threats.md, risk-scores.md, compensating-controls.md) + JSON (SARIF)
- **Classification engine**: Keyword matching (case-insensitive substring match — identical to existing AI keyword dispatch pattern)
- **Reference framework**: CSA MAESTRO seven-layer taxonomy for agentic AI architectures

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Keyword coverage insufficient (<90% classification rate) | Low | Medium | Validate against all 6 examples; tune keyword table iteratively |
| First-match-wins ordering produces surprising classifications | Low | Low | Document rationale; order layers from most specific to most general |
| Example regeneration introduces unrelated diff noise | Medium | Low | Regenerate using identical pipeline version; review diffs carefully |
| Downstream agents fail to propagate field | Very Low | Medium | Field is optional with default; propagation is read-only |

## Complexity Tracking

No constitution violations to justify.
