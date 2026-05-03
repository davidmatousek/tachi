---
prd:
  number: "078"
  topic: agent-context-optimization
  created: 2026-04-01
  status: Approved
  type: feature
triad:
  pm_signoff: { agent: product-manager, date: 2026-04-01, status: APPROVED_WITH_CONCERNS, notes: "2 non-blocking concerns: unvalidated quality improvement claim (add qualitative regression criteria in spec), US-5 is a constraint not a story. Prototype-first gate mitigates confidence risk." }
  architect_signoff: { agent: architect, date: 2026-04-01, status: APPROVED_WITH_CONCERNS, notes: "6 findings (1 blocking — orchestrator line count corrected). Lazy loading endorsed. YAML over JSON. Report agent extraction is highest risk. Shared references reduce implicit coupling." }
  techlead_signoff: { agent: team-lead, date: 2026-04-01, status: APPROVED_WITH_CONCERNS, notes: "2 blocking (line count corrected, prototype-first gate added). 21-33 hours est. 11 waves. Prototype risk-scorer first. Max parallelism 3 agents in Phases 2b/3." }
source:
  idea_id: 78
  story_id: null
---

# Agent Context Optimization: Enforce Tier Caps, Add Model Fields, Restructure Domain Knowledge

**Status**: Approved
**Created**: 2026-04-01
**Author**: product-manager
**Reviewers**: architect, team-lead
**Priority**: P2 (High Impact, Low Confidence)
**Predecessor**: PRD 029 (Agent Refactoring: Right-Size) and Feature 075 (Agent Best Practices)

---

## Executive Summary

### The One-Liner
Relocate domain knowledge from 6 oversized agent definitions into skills and helper files, enforce tighter tier caps, and add missing `model:` frontmatter to all 17 agents.

### Problem Statement
Despite two rounds of refactoring (PRD 029 reduced the orchestrator from 2,085 to ~1,100 lines; Feature 075 extracted skills and brought agents to documented caps), agent definitions have grown again. The orchestrator is at 1,286 lines, the risk-scorer at 1,093, and Feature 074's baseline-aware pipeline additions pushed both past the 1,000-line cap. Meanwhile, all 17 agents are missing the `model:` frontmatter field, and the best practices compliance table is stale.

Every line in an agent definition consumes context window space on every invocation — competing with the actual analysis work for model attention. Leaner agents improve focus, reduce per-invocation cost, and leave more context budget for the architecture being analyzed.

### Proposed Solution
Restructure agent definitions so they contain only orchestration logic (role, workflow skeleton, skill loading instructions, output format summary, constraints). All domain data — tables, schemas, detection patterns, scoring dimensions, output templates — moves to skill reference files, deterministic data files, or shared references loaded on-demand via Read tool.

This is a restructuring, not a reduction in capability. Every line removed from an agent must land in an externalized file. Nothing gets deleted — it gets relocated.

### Success Criteria
- All agents within tier hard caps (Leaf: 200, Report: 300, Methodology: 500)
- All 17 agents have `model:` field in frontmatter
- Zero quality regression — pipeline output equivalent on example architectures
- Best practices document updated with accurate compliance table and research findings

### Timeline
4 phases, 11 execution waves, estimated 21-33 hours (realistic midpoint: 27 hours):
- Phase 1: Best practices + model fields (2-3 hours)
- Phase 2: Methodology agents with prototype-first gate (10-15 hours)
- Phase 3: Report agents (5-8 hours)
- Phase 4: Final validation (2-3 hours)

**Prototype-first gate**: The risk-scorer is restructured first as a prototype. It has the most structured extractable content and is the best candidate for the new deterministic YAML pattern. Only after the prototype is validated do the remaining methodology agents proceed.

---

## Strategic Alignment

### Product Vision Alignment
**Reference**: [product-vision.md](docs/product/01_Product_Vision/product-vision.md)

tachi's vision is "the default threat modeling toolkit for any team building agentic AI applications." Output quality is the primary adoption driver. Context-optimized agents produce more reliable threat models by dedicating more of the model's attention to analysis rather than processing their own instructions.

### Roadmap Fit
Continues the quality-improvement trajectory of PRD 029 (first right-sizing) and Feature 075 (skill extraction and best practices). This is the third and final pass to reach sustainable tier caps.

### Predecessor Relationship
| Feature | What It Did | Where It Left Off |
|---------|-------------|-------------------|
| PRD 029 | First extraction — orchestrator 2,085 → ~1,100, report/infographic → ~300-400 | Established reference-extraction pattern |
| Feature 075 | Skill extraction — orchestrator → 769, risk-scorer → 994, control-analyzer → 935. Created `_TACHI_AGENT_BEST_PRACTICES.md` | Established tiered caps (300/800/1,000) and skill loading |
| Feature 074 | Baseline-aware pipeline | Grew methodology agents past 1,000-line cap (orchestrator to 1,286, risk-scorer to 1,093) |
| **This PRD** | Tighten caps, restructure remaining domain data, add model fields | Sustainable target caps with clear separation of concerns |

---

## Target Users & Personas

### Primary Persona: Threat Model User
- **Role**: Developer running `/threat-model` on their architecture
- **Goal**: Accurate, complete, well-structured threat analysis
- **Impact**: Leaner agents produce more focused analysis; user sees higher quality output without knowing the implementation changed

### Secondary Persona: tachi Contributor
- **Role**: Developer maintaining or extending tachi agents
- **Goal**: Understand and modify agents confidently
- **Impact**: Agent files under 500 lines are navigable. Domain knowledge in well-organized skill files is independently editable and testable.

---

## User Stories

### US-1: Methodology Agent Restructuring
**When** running a threat model analysis,
**I want** the orchestrator, risk-scorer, and control-analyzer to operate within the 500-line cap,
**So that** critical orchestration logic gets full model attention without being diluted by inline reference data.

**Acceptance Criteria**:
- **Given** the orchestrator (currently 1,286 lines), **when** restructured, **then** it is under 500 lines with all domain data in skill references
- **Given** the risk-scorer (currently 1,093 lines), **when** restructured, **then** it is under 500 lines with scoring schemas, CVSS vectors, and governance rules in skill references
- **Given** the control-analyzer (currently 973 lines), **when** restructured, **then** it is under 500 lines with detection patterns and evidence criteria in skill references
- **Given** any restructured agent, **when** a skill reference file is missing, **then** the agent fails with a clear error message

**Priority**: P0 | **Effort**: L

### US-2: Report Agent Restructuring
**When** generating threat reports, infographics, or PDF booklets,
**I want** the report agents to operate within the 300-line cap,
**So that** output generation instructions are focused and the model follows formatting specifications with high fidelity.

**Acceptance Criteria**:
- **Given** report-assembler (654 lines), **when** restructured, **then** it is under 300 lines with Typst templates in skill references
- **Given** threat-report (800 lines), **when** restructured, **then** it is under 300 lines with narrative templates and attack tree specs in skill references
- **Given** threat-infographic (775 lines), **when** restructured, **then** it is under 300 lines with template specifications in skill references

**Priority**: P0 | **Effort**: M

### US-3: Model Field Addition
**When** a tachi agent is invoked,
**I want** the `model:` field to be explicitly set in its frontmatter,
**So that** model selection is intentional, reproducible, and cost-trackable rather than inherited by default.

**Acceptance Criteria**:
- **Given** any of the 17 tachi agents, **when** inspected, **then** its YAML frontmatter includes a `model:` field
- **Given** the model assignments, **when** reviewed, **then** they match the agent's computational requirements (not all agents need the same model)

**Priority**: P1 | **Effort**: S

### US-4: Best Practices Update
**When** a contributor modifies or creates a tachi agent,
**I want** the `_TACHI_AGENT_BEST_PRACTICES.md` to reflect current caps, research findings, and accurate compliance data,
**So that** the document serves as a reliable reference rather than a stale artifact.

**Acceptance Criteria**:
- **Given** the best practices document, **when** read, **then** tier caps match the new targets (150→200, 250→300, 400→500)
- **Given** the compliance table, **when** compared to `wc -l` output, **then** all line counts match actual files
- **Given** the research section, **when** read, **then** it documents that the 200-line limit applies only to MEMORY.md (not agent files)
- **Given** the skill loading section, **when** read, **then** it explains eager (`skills:` frontmatter) vs lazy (Read tool) loading and recommends lazy loading

**Priority**: P1 | **Effort**: S

### US-5: Zero Regression
**When** all restructuring is complete,
**I want** the pipeline to produce equivalent output on example architectures,
**So that** no user-visible quality is lost.

**Acceptance Criteria**:
- **Given** `examples/agentic-app/architecture.md`, **when** `/threat-model` is run before and after restructuring, **then** output structure and quality are equivalent (finding count, risk distribution, SARIF result count, section presence)
- **Given** all 11 leaf agents, **when** compared before and after, **then** they are byte-identical (zero changes)

**Priority**: P0 | **Effort**: S

---

## Functional Requirements

### FR-1: Extended Skill Extraction
**Description**: Relocate remaining inline domain data from 6 agents into skill reference files loaded via Read tool on-demand.

**What moves to skills/helpers**:
- Domain data tables (STRIDE mappings, CVSS vectors, severity bands)
- Scoring schemas, dimension definitions, weight tables
- Detection patterns, evidence criteria, control categories
- Output templates (full markdown templates with placeholders)
- Example outputs and sample findings
- Dispatch rules and correlation matrices

**What stays in the agent definition**:
- Role identity and responsibility (2-3 lines)
- Workflow skeleton (phases, sequence, decision points)
- Skill loading instructions (which file to Read at which phase)
- Output format summary (structure, not full template)
- Constraints and error handling

### FR-2: Deterministic Data Files (New Pattern)
**Description**: Move static lookup tables into structured YAML data files that the agent reads and applies mechanically — no LLM interpretation needed.

**Candidates**:
- CVSS base vectors (currently inline tables in risk-scorer)
- Severity band thresholds (used by risk-scorer, control-analyzer, orchestrator)
- STRIDE-to-element dispatch mappings (used by orchestrator)
- Control category detection patterns (used by control-analyzer)

### FR-3: Output Templates as Files (New Pattern)
**Description**: Move output format specifications into template files that agents Read and populate.

**Candidates**:
- `threats.md` section structure (orchestrator)
- `risk-scores.md` output format (risk-scorer)
- `compensating-controls.md` output format (control-analyzer)
- Typst page specifications (report-assembler)
- Mermaid attack tree format (threat-report)

### FR-4: Shared Reference Files (New Pattern)
**Description**: Extract content duplicated across multiple agents into shared references.

**Candidates for deduplication**:
- Severity band definitions (used by risk-scorer, control-analyzer, orchestrator)
- STRIDE category descriptions (used by all STRIDE agents + orchestrator)
- Finding format specification (used by all threat agents)

### FR-5: Model Field Assignment
**Description**: Add `model:` field to all 17 agent YAML frontmatter blocks.

### Integration Requirements
**Preserved Interfaces** (zero changes):
- `/threat-model` command invocation and parameters
- SARIF 2.1.0 output format and schema compliance
- `threats.md`, `risk-scores.md`, `compensating-controls.md` output formats
- Narrative report and infographic formats
- All 11 leaf agent dispatch interfaces

---

## Non-Functional Requirements

### Performance
- No increase in total token cost per pipeline run (lazy loading should be net-neutral or net-positive)
- Reference file reads add acceptable latency (Read tool calls are fast)

### Reliability
- Missing reference files produce clear error messages, not silent degradation

### Maintainability
- Agent line counts verifiable via `wc -l`
- Domain knowledge independently editable without touching agent orchestration
- Shared references eliminate update-in-multiple-places maintenance burden

---

## Success Metrics

| Metric | Baseline | Target | Measurement |
|--------|----------|--------|-------------|
| Orchestrator lines | 1,286 | ≤500 (target 400) | `wc -l orchestrator.md` |
| Risk-scorer lines | 1,093 | ≤500 (target 400) | `wc -l risk-scorer.md` |
| Control-analyzer lines | 973 | ≤500 (target 400) | `wc -l control-analyzer.md` |
| Report-assembler lines | 654 | ≤300 (target 250) | `wc -l report-assembler.md` |
| Threat-report lines | 800 | ≤300 (target 250) | `wc -l threat-report.md` |
| Threat-infographic lines | 775 | ≤300 (target 250) | `wc -l threat-infographic.md` |
| Agents with `model:` field | 0/17 | 17/17 | YAML frontmatter inspection |
| Leaf agent changes | 0 | 0 | `git diff` on 11 leaf agents (byte-identical) |
| Regression test | N/A | Pass | Output equivalence on example architectures |

---

## Scope & Boundaries

### In Scope
- Restructure 3 methodology agents to ≤500 lines
- Restructure 3 report agents to ≤300 lines
- Add `model:` field to all 17 agents
- Create new skill reference files, deterministic data files, and output templates
- Create shared reference files for deduplicated content
- Update `_TACHI_AGENT_BEST_PRACTICES.md` with new caps, research, and compliance table
- Regression testing against example architectures

### Out of Scope
- Modifying any of the 11 leaf agents (beyond adding `model:` field)
- Changing output formats (SARIF, threats.md, reports, infographics)
- Changing the `/threat-model` command interface
- Splitting agents into sub-agents (researched and ruled out in PRD 029)
- Performance benchmarking beyond regression verification
- Changing skill loading from lazy (Read tool) to eager (`skills:` frontmatter)

### Assumptions
- Lazy loading via Read tool is context-efficient and does not degrade output quality
- Deterministic data files (YAML) are readable and processable by Claude Code agents
- Line count is a reasonable proxy for context consumption

### Constraints
- **Quality-first**: Zero regression in output quality. If an extraction degrades quality, fix the skill file or revert — don't accept degradation.
- **Relocation, not deletion**: Every line removed from an agent must exist in a skill reference, data file, or template
- **No interface changes**: All pipeline consumers see identical results

---

## Risks & Dependencies

### Technical Risks

**Risk 1: Quality regression from aggressive extraction** (Confidence concern — ICE C:3)
- **Likelihood**: Medium
- **Impact**: High
- **Mitigation**: Per-agent regression testing. Restructure one methodology agent first as a prototype before committing to all six. Compare output quality at each step.

**Risk 2: Deterministic data files are a new, unproven pattern**
- **Likelihood**: Medium
- **Impact**: Medium
- **Mitigation**: Prototype with one data file (e.g., CVSS vectors) before committing to the pattern. Fall back to markdown skill references if YAML processing proves unreliable.

**Risk 3: Shared references create hidden coupling**
- **Likelihood**: Low
- **Impact**: Medium
- **Mitigation**: Shared references are read-only lookup tables, not orchestration logic. Changes to shared content are validated against all consuming agents.

### Dependencies

**Internal**:
- Feature 075 skill infrastructure (tachi-orchestration, tachi-risk-scoring, tachi-control-analysis)
- Feature 074 baseline-aware pipeline additions (the content that caused growth)
- Example architectures in `examples/` for regression testing

**External**: None

---

## Research Findings (Embedded)

### Agent File Limits — Myth vs Reality

| Claim | Verdict | Source |
|---|---|---|
| 200-line / 25KB hard limit on agent `.md` files | **FALSE** — applies only to MEMORY.md | Claude Code docs: memory.md |
| Agent `.md` files loaded in full | **TRUE** — no documented truncation | Claude Code docs: sub-agents.md |
| `skills:` frontmatter injects full content eagerly | **TRUE** — defeats extraction purpose | Claude Code docs: sub-agents.md |

### Skill Loading: Eager vs Lazy

| Strategy | Context Cost | Recommendation |
|---|---|---|
| `skills:` frontmatter (eager) | High — all content always in context | Avoid for large domain knowledge |
| Read tool on-demand (lazy, current) | Low — loaded only when needed | Keep — correct for optimization goal |

---

## Open Questions

- [x] Which model should each agent tier use? — **Resolved**: All agents use `sonnet` (uniform model, simplest to maintain). Escalate individual agents to `opus` only if regression testing shows quality issues. (Architect recommendation)
- [x] Should deterministic data files use YAML or JSON? — **Resolved**: Use YAML. The project already has 9 YAML schema files in `schemas/`. Consistency over convention. (Architect recommendation)
- [x] What is the minimum regression test? — **Resolved**: Structural equivalence, not full content diff (LLM non-determinism makes verbatim matching unreliable). Test: finding count per category, risk level distribution, SARIF result count, all 7 sections present in threats.md, structural validation checklist passes. (Architect recommendation)
- [ ] Leaf agent-autonomy is exactly 200 lines — adding `model:` will exceed the 200-line cap. Accept 210 as leaf cap, or extract 1+ lines from agent-autonomy? (Architect F-03)

---

## References

### Predecessor PRDs
- [PRD 029 — Agent Refactoring: Right-Size](docs/product/02_PRD/029-agent-refactoring-right-size-2026-03-25.md)
- [PRD 075 — Agent Best Practices](docs/product/02_PRD/075-tachi-agent-best-practices-2026-03-31.md)

### Product Documentation
- [Product Vision](docs/product/01_Product_Vision/product-vision.md)
- [GitHub Issue #78](https://github.com/davidmatousek/tachi/issues/78)

### Technical Documentation
- [Tachi Agent Best Practices](.claude/agents/tachi/_TACHI_AGENT_BEST_PRACTICES.md)
- [Constitution](.aod/memory/constitution.md)
- Claude Code docs: sub-agents.md (agent file loading)
- Claude Code docs: memory.md (MEMORY.md truncation)

---

## Definition of Done

- [ ] All methodology agents ≤500 lines (target 400)
- [ ] All report agents ≤300 lines (target 250)
- [ ] All leaf agents ≤200 lines (target 150) — currently compliant
- [ ] All 17 agents have `model:` field in frontmatter
- [ ] Pipeline produces equivalent output on `examples/agentic-app/architecture.md`
- [ ] All 11 leaf agents are byte-identical (zero changes beyond `model:` addition)
- [ ] `_TACHI_AGENT_BEST_PRACTICES.md` updated with accurate compliance table
- [ ] Skill reference files organized, non-duplicative, and independently loadable
- [ ] No domain data remains inline in agent bodies — only orchestration logic
