---
triad:
  pm_signoff:
    agent: product-manager
    date: 2026-03-22
    status: APPROVED
    notes: "Plan covers 13/14 spec FRs fully, 1 partially (FR-010, low risk). All 5 user stories addressed. All 10 success criteria achievable. No scope creep. 2 low observations noted."
  architect_signoff:
    agent: architect
    date: 2026-03-22
    status: APPROVED
    notes: "Technically sound across all 7 evaluation criteria. DFD targeting matrix verified correct against all 5 agent files and interface contract. Four-wave structure well-sequenced. 2 informational observations, no corrections needed."
  techlead_signoff: null
---

# Implementation Plan: AI Threat Agents

**Branch**: `007-ai-threat-agents` | **Date**: 2026-03-22 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `specs/007-ai-threat-agents/spec.md`

## Summary

Validate, complete, and integration-test all 5 AI threat agent prompt files (`agents/ai/*.md`) to ensure they produce component-specific, schema-compliant, OWASP-grounded findings when dispatched by the orchestrator (F-003) against architecture input containing AI/LLM/agentic components. The agents already exist with substantial content (134-168 lines each); this feature validates correctness, verifies DFD element targeting, confirms OWASP AI framework references, and performs end-to-end integration testing alongside the validated STRIDE agents (F-005).

## Technical Context

**Language/Version**: Markdown + YAML (no application code — agents are structured prompt files)
**Primary Dependencies**: Orchestrator agent (`agents/orchestrator.md`, F-003 delivered), Finding IR schema (`schemas/finding.yaml` v1.0), STRIDE agents (`agents/stride/*.md`, F-005 delivered)
**Storage**: Filesystem only (markdown files in `agents/ai/`)
**Testing**: Validation-by-example — run agents against sample architectures, verify output against schema and quality criteria
**Target Platform**: Any LLM capable of following structured markdown prompts (platform-neutral)
**Project Type**: Content/prompt engineering (not application code)
**Performance Goals**: N/A (no runtime performance — prompt quality measured by output correctness)
**Constraints**: No schema modifications (`schemas/finding.yaml` is stable); agents must work within orchestrator's existing two-layer dispatch protocol; agents must coexist with STRIDE agents without ID namespace conflicts
**Scale/Scope**: 5 agent files, ~731 total lines of existing content to validate and complete

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. General-Purpose Architecture | PASS | Agents are domain-agnostic AI threat analysis prompts, applicable to any architecture with AI/LLM/agentic components |
| II. API-First Design | N/A | No API — agents are markdown prompt files |
| III. Backward Compatibility | PASS | No changes to existing schemas, interface contract, or STRIDE agents |
| IV. Concurrency & Data Integrity | N/A | No state management — agents produce stateless findings |
| V. Privacy & Data Isolation | PASS | Agents analyze architecture descriptions, not user data; outputs marked `classification: "confidential"` |
| VI. Testing Excellence | PASS | Validation approach: run against sample architectures, verify 100% schema compliance, component specificity, and OWASP reference coverage |
| VII. Definition of Done | PASS | 3-step DoD: pushed to branch, tested via sample runs, user-validated via orchestrator integration |
| VIII. Observability & Root Cause | N/A | No runtime operations |
| IX. Git Workflow | PASS | Feature branch `007-ai-threat-agents`, PR required |
| X. Product-Spec Alignment | PASS | Spec approved by PM (APPROVED_WITH_CONCERNS) |
| XI. SDLC Triad Collaboration | PASS | PRD approved by full Triad; spec PM-approved; plan dual-reviewed |

No violations. No complexity tracking needed.

## Project Structure

### Documentation (this feature)

```
specs/007-ai-threat-agents/
├── plan.md              # This file
├── research.md          # Research phase output (completed during /aod.spec)
├── data-model.md        # Validation matrix and agent inventory
├── checklists/
│   └── requirements.md  # Spec quality checklist
└── tasks.md             # Task breakdown (/aod.tasks output)
```

### Source Content (repository root)

```
agents/ai/
├── prompt-injection.md      # LLM agent — validate & complete (134 lines)
├── data-poisoning.md        # LLM agent — validate & complete (143 lines)
├── model-theft.md           # LLM agent — validate & complete (147 lines)
├── agent-autonomy.md        # AG agent — validate & complete (168 lines)
└── tool-abuse.md            # AG agent — validate & complete (139 lines)

schemas/
├── finding.yaml             # Finding IR schema (read-only, no changes)
├── input.yaml               # Input schema (read-only)
└── output.yaml              # Output schema (read-only)

examples/
└── mermaid-agentic-app/     # Primary validation input (contains AI/LLM/agentic components)
```

**Structure Decision**: No new directories needed. All work modifies existing agent files in `agents/ai/` and creates validation artifacts in `specs/007-ai-threat-agents/`.

## Components

### Agent Validation Framework

The validation approach follows the three-layer framework proven in F-005 (STRIDE agents):

**Layer 1: Structural Audit** (per agent)
- Frontmatter fields present and correct (`agent_name`, `category`, `threat_class`, `dfd_targets`, `owasp_references`, `output_schema`)
- Section structure matches canonical organization (purpose, detection scope, patterns, finding template, risk computation, references)
- `dfd_targets` matches interface contract AI extension dispatch rules

**Layer 2: Content Quality** (per agent)
- Detection patterns cover all attack subcategories from PRD FR-8
- Finding template examples demonstrate component-specific threats (not generic)
- Mitigation examples are actionable with specific technology references
- Framework references include OWASP AI framework IDs (LLM0x:2025, ASI-xx, MCP-xx:2025)
- Risk computation section includes correct OWASP 3x3 matrix
- Agent-level trigger keywords (Layer 2 dispatch) extend orchestrator-level keywords (Layer 1 dispatch)

**Layer 3: Integration Validation** (all agents together)
- Run orchestrator against `examples/mermaid-agentic-app/input.md`
- Verify AG and LLM tables have findings in assembled `threats.md`
- Verify two-layer keyword dispatch: correct components activated for correct agent categories
- Verify dual-dispatch behavior for components matching both LLM and agentic keywords
- Verify 100% component specificity (zero generic findings)
- Verify risk levels match OWASP 3x3 matrix computations
- Verify empty results for non-AI components

### AI Agent DFD Targeting Matrix

Reference table for Layer 1 structural audit — each agent's `dfd_targets` must match:

| Agent | category | threat_class | dfd_targets (expected) | OWASP Framework |
|-------|----------|-------------|----------------------|-----------------|
| prompt-injection.md | llm | LLM | [Process] | LLM Top 10 v2025 (LLM01) |
| data-poisoning.md | llm | LLM | [Data Store, Data Flow] | LLM Top 10 v2025 (LLM03, LLM04) |
| model-theft.md | llm | LLM | [Data Store, Process] | LLM Top 10 v2025 (LLM10) |
| agent-autonomy.md | agentic | AG | [Process] | Agentic Top 10 (ASI01, ASI06, ASI08, ASI09, ASI10) |
| tool-abuse.md | agentic | AG | [Process] | Agentic Top 10 (ASI02, ASI04), MCP Top 10 (MCP03) |

### OWASP AI Framework Reference Completeness

Current state — verify each agent references its primary OWASP framework:

| Agent | Primary OWASP | Expected References | P1 Cross-References |
|-------|---------------|--------------------|--------------------|
| prompt-injection.md | LLM01:2025 | LLM01:2025, LLM07:2025 | MITRE ATLAS, CWE-77 |
| data-poisoning.md | LLM04:2025 | LLM03:2025, LLM04:2025, LLM08:2025 | MITRE ATLAS, CWE-1321 |
| model-theft.md | LLM10:2025 | LLM03:2025, LLM10:2025 | MITRE ATLAS, CWE-200 |
| agent-autonomy.md | ASI01 | ASI01, ASI06, ASI08, ASI09, ASI10 | MITRE ATLAS |
| tool-abuse.md | ASI02, MCP03 | ASI02, ASI04, MCP03:2025, MCP05:2025 | MITRE ATLAS |

### Two-Layer Keyword Dispatch Validation Matrix

Expected dispatch behavior for `examples/mermaid-agentic-app/input.md`:

| Component | DFD Type | Layer 1 Keywords Matched | STRIDE Dispatch | AI Dispatch |
|-----------|----------|-------------------------|----------------|------------|
| User | External Entity | None | S, R | None |
| LLM Agent Orchestrator | Process | "LLM" + "Agent" + "Orchestrator" | S, T, R, I, D, E | All 5 AI agents (dual-dispatch) |
| MCP Tool Server | Process | "MCP" + "Tool Server" | S, T, R, I, D, E | agent-autonomy, tool-abuse |
| Knowledge Base | Data Store | None | T, I, D | None |
| External API | External Entity | None | S, R | None |

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
          │ + AI keyword dispatch (Layer 1)
          ▼
┌──────────────────┐    ┌──────────────────┐
│ 6 STRIDE Agents  │    │ 5 AI Agents      │
│ (F-005 validated)│    │ (F-007 — this)   │
│                  │    │                  │
│ Each agent:      │    │ Each agent:      │
│ 1. Receives arch │    │ 1. Receives arch │
│ 2. Filters by    │    │ 2. Filters by    │
│    dfd_targets   │    │    dfd_targets   │
│ 3. Applies       │    │ 3. Applies Layer │
│    patterns      │    │    2 keywords    │
│ 4. Produces      │    │ 4. Applies       │
│    findings (IR) │    │    patterns      │
│                  │    │ 5. Produces      │
│                  │    │    findings (IR) │
└────────┬─────────┘    └────────┬─────────┘
         │                       │
         └───────────┬───────────┘
                     │ all findings per schemas/finding.yaml
                     ▼
┌─────────────────────────────┐
│ Orchestrator (F-003)        │
│  Phase 3-4: Assemble        │
│  - Validate risk_level      │
│  - Build 6 STRIDE tables    │
│  - Build 2 AI tables        │
│    (AG table + LLM table)   │
│  - Generate coverage matrix │
│  - Compute risk summary     │
└─────────┬───────────────────┘
          │
          ▼
    threats.md output
    (8 threat tables total)
```

## Tech Stack

| Component | Technology | Justification |
|-----------|-----------|---------------|
| Agent files | Markdown with YAML frontmatter | Platform-neutral, LLM-agnostic prompt format; matches F-005 STRIDE pattern |
| Schema | YAML (`schemas/finding.yaml` v1.0) | Machine-readable validation contract; read-only for this feature |
| Validation | Manual review + orchestrator integration run | No automated test framework needed for prompt files |
| Version control | Git | Standard for content versioning |
| OWASP references | LLM Top 10 v2025, Agentic Top 10 2026, MCP Top 10 2025 | Three complementary AI security frameworks covering model, agent, and protocol layers |

## Implementation Approach

### Wave 1: Structural Audit (all 5 agents in parallel)

Audit each agent for structural compliance:
1. Verify frontmatter fields match expected schema (6 fields: agent_name, category, threat_class, dfd_targets, owasp_references, output_schema)
2. Verify section order matches canonical structure (purpose, detection scope, patterns, finding template, risk computation, references)
3. Verify `dfd_targets` matches AI Agent DFD Targeting Matrix above
4. Verify `category` field uses correct value (`llm` or `agentic`)
5. Flag any structural gaps

**Parallelizable**: All 5 agents can be audited simultaneously — no cross-dependencies.

### Wave 2: Content Validation (Agentic + LLM agents in parallel tracks)

**Track A — Agentic agents** (agent-autonomy, tool-abuse):
1. Verify detection patterns cover all PRD FR-8 subcategories for each agent
2. Verify finding template demonstrates component-specific threats (references named components, not generic descriptions)
3. Verify OWASP Agentic Top 10 (ASI-xx) references are present and correctly formatted
4. Verify OWASP MCP Top 10 (MCP-xx:2025) references for tool-abuse agent
5. Verify mitigation examples are actionable (specific technology/configuration)
6. Add P1 cross-references (MITRE ATLAS, CWE) if missing

**Track B — LLM agents** (prompt-injection, data-poisoning, model-theft):
1. Verify detection patterns cover all PRD FR-8 subcategories for each agent
2. Verify finding template demonstrates component-specific threats
3. Verify OWASP LLM Top 10 v2025 (LLM0x:2025) references are present and correctly formatted
4. Verify mitigation examples are actionable
5. Add P1 cross-references (MITRE ATLAS, CWE) if missing

**Parallelizable**: Track A and Track B have no cross-dependencies — agentic and LLM agents are independent.

### Wave 3: Cross-Agent Consistency Check

After individual agent validation, verify consistency across all 5 agents:
1. All agents follow identical section organization (FR-012)
2. Finding ID prefix conventions are consistent (AG-N for agentic, LLM-N for LLM)
3. Risk computation sections use identical OWASP 3x3 matrix
4. All agents reference `schemas/finding.yaml` as output_schema
5. Frontmatter field names are identical across all 5 agents
6. Detection scope keywords don't conflict with each other or with orchestrator Layer 1 keywords

### Wave 4: Integration Validation (sequential — depends on Waves 1-3)

End-to-end validation using orchestrator:
1. Run orchestrator against `examples/mermaid-agentic-app/input.md`
2. Verify assembled `threats.md` has AG and LLM tables with findings
3. Verify two-layer keyword dispatch: "LLM Agent Orchestrator" triggers all 5 AI agents (dual-dispatch), "MCP Tool Server" triggers only agentic agents, "Knowledge Base" triggers no AI agents
4. Verify 100% component specificity (zero generic findings across AG and LLM tables)
5. Verify risk_level computations match OWASP 3x3 matrix
6. Verify finding ID namespaces don't conflict with STRIDE findings (AG/LLM prefixes vs S/T/R/I/D/E)
7. Verify coverage matrix shows correct AI dispatch targeting
8. Verify empty results scenario: confirm AI agents produce zero findings for non-AI components

### Post-Constitution Re-Check

| Principle | Status | Notes |
|-----------|--------|-------|
| III. Backward Compatibility | PASS | No schema changes; only agent content validation and completion |
| VI. Testing Excellence | PASS | Multi-layer validation; integration testing against sample architecture |
| X. Product-Spec Alignment | PASS | All 14 spec FRs addressed; all 10 success criteria measurable |

No violations introduced by design.
