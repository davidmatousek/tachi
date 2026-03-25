---
prd:
  number: "029"
  topic: agent-refactoring-right-size
  created: 2026-03-25
  status: Approved
  type: feature
triad:
  pm_signoff: { agent: product-manager, date: 2026-03-25, status: APPROVED, notes: "Research-backed, tight scope, measurable criteria. Two non-blocking observations for spec phase." }
  architect_signoff: { agent: architect, date: 2026-03-25, status: APPROVED_WITH_CONCERNS, notes: "Error handling section is 228 lines (not 130); split into pure error templates vs defensive spec. Preservation inventory should be committed artifact." }
  techlead_signoff: { agent: team-lead, date: 2026-03-25, status: APPROVED_WITH_CONCERNS, notes: "4-wave execution recommended. Report agent needs granular content inventory during Plan phase. 10-15 hour estimate." }
source:
  idea_id: 29
  story_id: null
---

# Agent Refactoring: Right-Size Orchestrator, Report, and Infographic Agents — Product Requirements Document

**Status**: Approved
**Created**: 2026-03-25
**Author**: product-manager
**Reviewers**: architect, team-lead
**Priority**: P1 (High)

---

## Executive Summary

### The One-Liner
Extract consultation-only content from 3 oversized agents into on-demand reference documents so the LLM follows instructions with higher fidelity.

### Problem Statement
Three tachi agents (orchestrator at 2,085 lines, threat-report at 801 lines, threat-infographic at 592 lines) significantly exceed the 300-line best-practices ceiling. Research confirms that prompt bloat degrades instruction-following accuracy by up to 30% (Chroma "Context Rot" study, July 2025). The orchestrator at ~28K tokens is 2x Anthropic's Claude Code production benchmark of ~14K tokens. Critical rules — SARIF compliance, correlation detection, risk matrix calculations — sit in the middle of these prompts where the "lost in the middle" effect is strongest.

### Proposed Solution
Apply a reference-extraction pattern: move consultation-only content (SARIF specification, validation checklists, error templates, output examples) into separate reference documents loaded on-demand at specific pipeline phases. This reduces always-loaded context without splitting the sequential pipeline (which would increase token cost) and without removing any capabilities.

### Success Criteria
- All 3 agents reduced to target line counts (orchestrator: ~1,100-1,200; report: ~300-400; infographic: ~300-400)
- `/threat-model` produces identical output on `examples/agentic-app/architecture.md` (regression test)
- SARIF output validates against SARIF 2.1.0 schema
- All 11 STRIDE/AI threat agents remain unchanged (zero regression)

### Timeline
Estimated 10-15 hours across 4 execution waves:
1. **Prep** — Capability inventory and baseline regression capture
2. **Orchestrator** — Extract references, condense prose, verify regression
3. **Report + Infographic** (parallel) — Extract references from both agents simultaneously
4. **Final Validation** — End-to-end regression test, SARIF validation, threat agent byte-comparison

---

## Strategic Alignment

### Product Vision Alignment
**Reference**: [product-vision.md](docs/product/01_Product_Vision/product-vision.md)

tachi's vision is to be "the default threat modeling toolkit for any team building agentic AI applications." Output quality directly drives adoption. If instruction-following degrades due to prompt bloat, threat models become unreliable — undermining the core value proposition.

### Roadmap Fit
This is a quality-improvement refactoring that strengthens existing delivered features (PRDs 003, 015, 018) without changing external interfaces.

---

## Target Users & Personas

### Primary Persona: Threat Model User
- **Role**: Developer or security engineer running `/threat-model`
- **Goal**: Get accurate, complete, well-structured threat analysis
- **Pain Point**: Output quality may silently degrade as agent prompts grow beyond optimal size — user cannot tell the difference between a good-fidelity run and a degraded one
- **Why This Matters**: Right-sizing ensures the orchestrator, report, and infographic agents process instructions with maximum accuracy, producing reliable threat models every time

### Secondary Persona: tachi Developer
- **Role**: Contributor maintaining or extending tachi agents
- **Goal**: Understand agent boundaries and modify agents confidently
- **Pain Point**: A 2,085-line agent file is hard to navigate, understand, and modify safely
- **Why This Matters**: Extracted reference documents create clear separation between core orchestration logic and consultation content, making the codebase more maintainable

---

## User Stories

### US-1: Orchestrator Right-Sizing
**When** running a threat model analysis on any architecture description,
**I want** the orchestrator to operate within production prompt sizing benchmarks,
**So I can** trust that critical rules (SARIF compliance, correlation detection, risk matrix) are followed with high fidelity and not degraded by the "lost in the middle" effect.

**Acceptance Criteria**:
- **Given** the orchestrator agent, **when** measured, **then** it is ~1,100-1,200 lines (reduced from 2,085)
- **Given** SARIF generation specification (~490 lines), **when** Phase 4 completes, **then** it is loaded from a reference document on-demand
- **Given** the validation checklist (~80 lines), **when** the pipeline ends, **then** it is loaded from a reference document on-demand
- **Given** error handling templates (~100 lines of pure error templates), **when** an error occurs, **then** they are loaded from a reference document on-demand
- **Given** defensive specification content (~128 lines of DFD classification, non-conforming finding handling, three-state cell model), **when** identified during extraction, **then** it is retained in the core agent or extracted to phase-specific reference documents (not the error-only reference)
- **Given** verbose prose (~200 lines), **when** reviewed, **then** it has been condensed or removed

**Priority**: P0 | **Effort**: L

### US-2: Report Agent Right-Sizing
**When** generating a narrative threat report with attack trees,
**I want** the report agent to follow instructions with high fidelity,
**So I can** get well-structured reports that accurately reflect the threat findings.

**Acceptance Criteria**:
- **Given** the threat-report agent, **when** measured, **then** it is ~300-400 lines (reduced from 801)
- **Given** output templates and verbose examples, **when** identified, **then** they are extracted to reference documents

**Note**: The threat-report agent requires a detailed content inventory during the Plan phase (spec.md) to identify specific extraction targets — the research provides granular analysis only for the orchestrator. The ~50% extraction target (801 → 300-400) must be validated by inventorying output format templates, Mermaid attack tree examples, markdown formatting instructions, and verbose prose.

**Priority**: P0 | **Effort**: M

### US-3: Infographic Agent Right-Sizing
**When** generating threat model infographics via Gemini API,
**I want** the infographic agent to follow Gemini API integration instructions accurately,
**So I can** get correctly rendered infographic specifications and images.

**Acceptance Criteria**:
- **Given** the threat-infographic agent, **when** measured, **then** it is ~300-400 lines (reduced from 592)
- **Given** Gemini API specification and error handling, **when** identified, **then** they are extracted to reference documents

**Priority**: P0 | **Effort**: M

### US-4: Zero Regression on Threat Agents
**When** the refactoring is complete,
**I want** all 11 STRIDE/AI threat agents to remain completely unchanged,
**So I can** trust that no regression is introduced in the focused, well-sized agents already in the optimal range (108-196 lines).

**Acceptance Criteria**:
- **Given** any of the 11 threat agents (spoofing, tampering, repudiation, info-disclosure, denial-of-service, privilege-escalation, prompt-injection, data-poisoning, model-theft, agent-autonomy, tool-abuse), **when** compared before and after refactoring, **then** the files are byte-identical
- **Given** the example architecture at `examples/agentic-app/architecture.md`, **when** `/threat-model` is run before and after refactoring, **then** the output structure and quality are equivalent

**Priority**: P0 | **Effort**: S

---

## Functional Requirements

### Core Capabilities

#### FR-1: Reference Document Extraction
**Description**: Extract consultation-only content from oversized agents into standalone reference documents that can be loaded on-demand.

**Reference Document Structure**:
```
adapters/claude-code/agents/references/
├── sarif-generation.md          (~490 lines, orchestrator Phase 4)
├── validation-checklist.md      (~80 lines, orchestrator pipeline end)
├── error-templates.md           (~100 lines, orchestrator on-error only)
├── report-templates.md          (threat-report extraction target)
├── infographic-gemini-api.md    (threat-infographic extraction target)
└── infographic-error-handling.md (threat-infographic extraction target)
```

**Important distinction**: The orchestrator error handling section (~228 lines total) contains two types of content:
- **Pure error templates** (~100 lines): Loaded on-error only → extract to `error-templates.md`
- **Defensive specification** (~128 lines): DFD classification rules, non-conforming finding handler, three-state cell model — needed during normal pipeline execution → retain in core agent or extract to phase-specific references

**Business Rules**:
- Reference documents are loaded on-demand at specific pipeline phases, not pre-loaded
- Each reference document must be self-contained — no cross-references between reference docs
- Core agent files retain all orchestration logic, phase sequencing, dispatch rules, and defensive specification content needed during normal execution
- Reference documents contain specification content only (schemas, templates, checklists)
- Content needed during normal pipeline phases must NOT be placed in on-error reference documents

#### FR-2: Orchestrator Prose Condensation
**Description**: Remove or condense ~200 lines of verbose, redundant narration in the orchestrator that adds no specification value.

**Business Rules**:
- Only narration/prose is condensed — never specification content (tables, schemas, algorithms)
- The heuristic vs. specification distinction from the research must guide what is compressible

#### FR-3: Agent Loading Instructions
**Description**: Each refactored agent must include clear instructions for when and how to load its reference documents.

**Business Rules**:
- Loading instructions specify: which reference document, at what pipeline phase, and the file path
- The orchestrator uses `Read` tool to load reference content just-in-time

### Integration Requirements

**Preserved Interfaces**:
- `/threat-model` command: no changes to invocation or parameters
- SARIF 2.1.0 output format: identical schema compliance
- `threats.md` output format: identical structure
- Narrative report format: identical structure
- Infographic specification format: identical structure
- All 11 threat agent dispatch interfaces: unchanged

---

## Non-Functional Requirements

### Performance Requirements
- No increase in total token cost per threat model run (reference extraction should be net-neutral or net-positive since consultation content is only loaded when needed)
- No increase in pipeline execution time beyond reference document read latency

### Reliability Requirements
- If a reference document is missing, the agent must fail with a clear error message (not silently produce incomplete output)

### Maintainability Requirements
- Reference documents are individually editable without touching the core agent
- Agent line counts are verifiable via `wc -l`

---

## Success Metrics

### Primary Metrics

| Metric | Baseline | Target | Measurement |
|--------|----------|--------|-------------|
| Orchestrator line count | 2,085 | 1,100-1,200 | `wc -l orchestrator.md` |
| Report agent line count | 801 | 300-400 | `wc -l threat-report.md` |
| Infographic agent line count | 592 | 300-400 | `wc -l threat-infographic.md` |
| Threat agent changes | 0 | 0 | `git diff` on all 11 threat agents |
| SARIF schema validation | Pass | Pass | Schema validation on output |
| Regression test | N/A | Pass | Structural equivalence: finding count, risk distribution, SARIF result count, section presence |

---

## Scope & Boundaries

### In Scope (P0)
- Extract SARIF generation spec from orchestrator to reference document
- Extract validation checklist from orchestrator to reference document
- Extract error handling templates from orchestrator to reference document
- Condense/remove verbose prose from orchestrator
- Extract output templates from threat-report agent
- Extract Gemini API spec from threat-infographic agent
- Create `adapters/claude-code/agents/references/` directory
- Add loading instructions to refactored agents
- Regression testing against example architecture

### Out of Scope
- Modifying any of the 11 STRIDE/AI threat agents
- Modifying the 2 infographic design templates (`templates/infographic-baseball-card.md`, `templates/infographic-system-architecture.md`)
- Modifying any schemas in `schemas/`
- Changing the `/threat-model` command interface
- Changing output formats (SARIF, threats.md, report, infographic)
- Splitting the orchestrator into phase-agents (research ruled this out — increases token cost)
- Performance benchmarking beyond regression verification

### Assumptions
- The reference-extraction pattern (load via `Read` tool on-demand) works within the Claude Code agent framework
- Line count is a reasonable proxy for prompt token size
- The "lost in the middle" effect applies to the current model (Claude Opus 4.6)

### Constraints
- **Preservation-first**: All capabilities must be inventoried before changes — nothing may be accidentally dropped
- **No external interface changes**: All consumers of `/threat-model` output must see identical results
- **Research-backed targets**: Line count targets come from the analysis in `docs/research/agent-sizing-analysis.md`

---

## Risks & Dependencies

### Technical Risks

**Risk 1**: Reference document loading adds latency or fails silently
- **Likelihood**: Low
- **Impact**: Medium
- **Mitigation**: Explicit error handling when reference file is not found; test loading in CI

**Risk 2**: Extraction accidentally removes specification content needed during always-loaded phases
- **Likelihood**: Medium
- **Impact**: High
- **Mitigation**: Preservation-first checklist — inventory all capabilities before extraction; regression test

**Risk 3**: Condensed prose removes context that aids instruction-following
- **Likelihood**: Low
- **Impact**: Medium
- **Mitigation**: Only remove clearly redundant narration; preserve all specification content; regression test

### Dependencies

**Internal Dependencies**:
- Delivered PRD 003 (Orchestrator Agent) — defines the orchestrator's pipeline phases
- Delivered PRD 015 (Threat Report Agent) — defines report generation
- Delivered PRD 018 (Threat Infographic Agent) — defines infographic generation
- Research analysis at `docs/research/agent-sizing-analysis.md` — extraction targets

**External Dependencies**: None

---

## Open Questions

- [x] Should the orchestrator be split into phase-agents? — **Answered: No** (research shows net token cost increases due to pipeline state passing)
- [x] What content is irreducible vs. extractable? — **Answered**: See `docs/research/agent-sizing-analysis.md` Section 3
- [x] Should reference documents use a consistent frontmatter format for metadata? — **Answered: Yes** — Each reference document should include minimal frontmatter: `source-agent`, `loaded-at` (pipeline phase), and `extracted-from` (source file line range). Format to be finalized in spec.md.

---

## References

### Research
- [Agent Sizing Analysis](docs/research/agent-sizing-analysis.md) — Full inventory, web research, first principles analysis
- Chroma: Context Rot (July 2025) — 30% accuracy drop from context bloat
- Liu et al.: Lost in the Middle (TACL 2024) — middle-of-prompt attention degradation
- Anthropic: Context Engineering for AI Agents — just-in-time retrieval pattern

### Product Documentation
- [Product Vision](docs/product/01_Product_Vision/product-vision.md)
- [PRD 003 — Orchestrator Agent](docs/product/02_PRD/003-orchestrator-agent-2026-03-21.md)
- [PRD 015 — Threat Report Agent](docs/product/02_PRD/015-threat-report-agent-attack-trees-2026-03-23.md)
- [PRD 018 — Threat Infographic Agent](docs/product/02_PRD/018-threat-infographic-agent-2026-03-23.md)

### Technical Documentation
- [Agent Best Practices](.claude/agents/_AGENT_BEST_PRACTICES.md)
- [Constitution](.aod/memory/constitution.md)

---

## Definition of Done

- [ ] All 3 agents reduced to target line counts
- [ ] Reference documents created and loadable on-demand
- [ ] `/threat-model` produces equivalent output on `examples/agentic-app/architecture.md` (regression test)
- [ ] SARIF output validates against SARIF 2.1.0 schema
- [ ] Preservation-first capability inventory committed as `specs/029-agent-refactoring-right-size/capability-inventory.md`
- [ ] All 11 threat agents are byte-identical (zero changes)
- [ ] Both infographic design templates are unchanged
- [ ] All schemas in `schemas/` are unchanged
