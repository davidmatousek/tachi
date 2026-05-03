---
prd_reference: docs/product/02_PRD/078-agent-context-optimization-2026-04-01.md
triad:
  pm_signoff:
    agent: product-manager
    date: 2026-04-01
    status: APPROVED_WITH_CONCERNS
    notes: "2 non-blocking: (1) added severity-level stability criterion to SC-004, (2) agent-autonomy line cap decision (edge case #2) should be resolved before plan.md. All 5 user stories covered, all 13 FRs trace to PRD, scope matches PRD exactly."
  architect_signoff: null
  techlead_signoff: null
---

# Feature Specification: Agent Context Optimization

**Feature Branch**: `078-agent-context-optimization`
**Created**: 2026-04-01
**Status**: Draft
**Input**: PRD 078 — Agent Context Optimization: Enforce Tier Caps, Add Model Fields, Restructure Domain Knowledge

## User Scenarios & Testing

### User Story 1 — Methodology Agent Restructuring (Priority: P0)

A threat model user runs `/threat-model` on their architecture description. The orchestrator, risk-scorer, and control-analyzer each load only orchestration logic from their agent definitions and fetch domain knowledge (dispatch rules, scoring schemas, detection patterns) on-demand from skill reference files. The pipeline produces the same threat analysis output as before restructuring.

**Why this priority**: Methodology agents are the pipeline backbone. The orchestrator (1,286 lines) and risk-scorer (1,093 lines) currently exceed their caps, consuming context that should be reserved for analyzing the user's architecture. Reducing these to under 500 lines restores focus to analysis work.

**Independent Test**: Run `/threat-model` on `examples/agentic-app/architecture.md` before and after restructuring. Compare output structure: finding count per category, risk level distribution, SARIF result count, all 7 sections present in threats.md. Structural equivalence confirms no regression.

**Acceptance Scenarios**:

1. **Given** the orchestrator agent at 1,286 lines, **When** restructured with domain data moved to skill references, **Then** the agent file is under 500 lines and all moved content exists in skill reference files.
2. **Given** the risk-scorer agent at 1,093 lines, **When** restructured with scoring schemas, CVSS vectors, and governance rules moved to skill references, **Then** the agent file is under 500 lines and all moved content exists in skill reference files.
3. **Given** the control-analyzer agent at 973 lines, **When** restructured with detection patterns and evidence criteria moved to skill references, **Then** the agent file is under 500 lines and all moved content exists in skill reference files.
4. **Given** any restructured methodology agent, **When** a required skill reference file is missing at runtime, **Then** the agent produces a clear error message identifying the missing file.

---

### User Story 2 — Report Agent Restructuring (Priority: P0)

A user generates a threat report, infographic, or PDF security booklet. The report agents load formatting specifications and output templates on-demand from skill reference files rather than carrying them inline. Generated outputs are identical in structure and content to pre-restructuring results.

**Why this priority**: Report agents (654–800 lines) carry large output templates inline. Moving templates to dedicated files makes them independently editable and reduces agent context consumption, improving formatting fidelity.

**Independent Test**: Run the full pipeline including `/threat-model`, `/risk-score`, `/compensating-controls`, and each report command on `examples/agentic-app/architecture.md`. Compare report structure: section presence, Mermaid diagram syntax, SARIF compliance, PDF page sequence.

**Acceptance Scenarios**:

1. **Given** the report-assembler agent at 654 lines, **When** restructured with Typst template specifications moved to skill references, **Then** the agent file is under 300 lines and all moved content exists in reference files.
2. **Given** the threat-report agent at 800 lines, **When** restructured with narrative templates and attack tree specifications moved to skill references, **Then** the agent file is under 300 lines and all moved content exists in reference files.
3. **Given** the threat-infographic agent at 775 lines, **When** restructured with template specifications moved to skill references, **Then** the agent file is under 300 lines and all moved content exists in reference files.

---

### User Story 3 — Model Field Assignment (Priority: P1)

A tachi contributor inspects any of the 17 agent definitions. Each agent's YAML frontmatter includes a `model:` field specifying the intended model for invocation. Model selection is intentional and documented rather than implicitly inherited.

**Why this priority**: Explicit model fields enable cost tracking, reproducibility, and intentional model-to-task matching. Lower priority than restructuring because agents function correctly without it — this is a governance improvement.

**Independent Test**: Inspect all 17 agent YAML frontmatter blocks. Each must contain a `model:` field with a valid model identifier.

**Acceptance Scenarios**:

1. **Given** any of the 17 tachi agents, **When** the YAML frontmatter is inspected, **Then** it contains a `model:` field with a valid value.
2. **Given** the model assignments, **When** reviewed against agent computational requirements, **Then** assignments are justified (all agents start with `sonnet`; `opus` only if regression testing shows quality issues).

---

### User Story 4 — Best Practices Document Update (Priority: P1)

A tachi contributor opens `_TACHI_AGENT_BEST_PRACTICES.md` to understand agent design conventions. The document reflects the new tier caps (200/300/500), contains accurate line counts matching actual files, documents the corrected research finding (200-line limit applies to MEMORY.md only), and explains the lazy loading recommendation.

**Why this priority**: The best practices document is the contributor reference guide. Stale caps and inaccurate compliance data undermine its purpose. Lower priority than agent restructuring because it's documentation, not behavior.

**Independent Test**: Compare every line count in the compliance table against `wc -l` output for each agent file. Verify tier caps match the values in this specification. Verify research findings section corrects the MEMORY.md misconception.

**Acceptance Scenarios**:

1. **Given** the best practices document, **When** the tier caps section is read, **Then** caps match: Leaf 200, Report 300, Methodology 500.
2. **Given** the compliance table, **When** compared to actual `wc -l` output for all 17 agents, **Then** every line count matches.
3. **Given** the research findings section, **When** read, **Then** it documents that the 200-line limit applies only to MEMORY.md (not agent files).
4. **Given** the skill loading section, **When** read, **Then** it explains eager (`skills:` frontmatter) vs lazy (Read tool) loading and recommends lazy loading for domain knowledge.

---

### User Story 5 — Zero Regression Verification (Priority: P0)

After all restructuring is complete, the pipeline produces equivalent output on example architectures. No user-visible quality is lost. All 11 leaf agents remain byte-identical (zero changes beyond `model:` field addition).

**Why this priority**: Quality regression would negate the entire feature. This is the validation gate that confirms restructuring was a relocation, not a reduction.

**Independent Test**: Run full pipeline on `examples/agentic-app/architecture.md` before and after all changes. Compare: finding count per STRIDE+AI category, severity distribution, SARIF result count, section presence in all output files. Diff leaf agents to confirm only `model:` field was added.

**Acceptance Scenarios**:

1. **Given** `examples/agentic-app/architecture.md`, **When** `/threat-model` is run before and after restructuring, **Then** output structure is equivalent: finding count per category within ±2, risk distribution proportions preserved, SARIF result count within ±2, all 7 sections present.
2. **Given** all 11 leaf agents, **When** diffed before and after the feature, **Then** the only change is the addition of the `model:` field in frontmatter.

---

### Edge Cases

- **Missing reference file at runtime**: Agent must fail with a clear error naming the missing file and its expected path — not silently degrade output.
- **agent-autonomy at exactly 200 lines**: Adding `model:` field pushes it to ~210 lines. Decision needed: accept 210 as leaf exception, or extract content to bring it back under 200.
- **Deterministic YAML data file proves unreliable**: If the agent cannot reliably process YAML lookup tables, fall back to markdown skill references (the proven pattern).
- **Shared reference file modified**: When shared content (severity bands, STRIDE descriptions) changes, all consuming agents must be validated — not just one.

## Requirements

### Functional Requirements

- **FR-001**: System MUST restructure orchestrator, risk-scorer, and control-analyzer agents to under 500 lines each, with all extracted domain data in skill reference files.
- **FR-002**: System MUST restructure report-assembler, threat-report, and threat-infographic agents to under 300 lines each, with all extracted templates and formatting specs in skill reference files.
- **FR-003**: System MUST add a `model:` field to the YAML frontmatter of all 17 tachi agents, with `sonnet` as the default assignment.
- **FR-004**: System MUST create deterministic data files in YAML format for static lookup tables (CVSS base vectors, severity band thresholds, STRIDE dispatch mappings, control category patterns).
- **FR-005**: System MUST create shared reference files for content duplicated across multiple agents (severity band definitions, STRIDE category descriptions, finding format specification).
- **FR-006**: System MUST create output template files for format specifications currently inline in agents (threats.md structure, risk-scores.md format, compensating-controls.md format, Typst page specs, Mermaid attack tree format).
- **FR-007**: System MUST update `_TACHI_AGENT_BEST_PRACTICES.md` with new tier caps (200/300/500), accurate compliance table, corrected research findings, and lazy loading recommendation.
- **FR-008**: System MUST NOT modify any of the 11 leaf agents beyond adding the `model:` field to frontmatter.
- **FR-009**: System MUST NOT change any pipeline output formats (SARIF, threats.md, risk-scores.md, compensating-controls.md, narrative reports, infographics, PDF booklets).
- **FR-010**: System MUST NOT change the `/threat-model` command interface or parameters.
- **FR-011**: Every line removed from an agent definition MUST exist in a corresponding skill reference, data file, template, or shared reference — nothing is deleted, only relocated.
- **FR-012**: Restructured agents MUST produce clear error messages when a required skill reference file is missing at runtime.
- **FR-013**: The risk-scorer MUST be restructured first as a prototype to validate the deterministic YAML pattern before proceeding to remaining agents.

### Key Entities

- **Agent Definition**: A markdown file in `.claude/agents/tachi/` containing role identity, workflow skeleton, skill loading instructions, and constraints. The orchestration logic that drives agent behavior.
- **Skill Reference File**: A markdown or YAML file in `.claude/skills/tachi-*/references/` containing domain knowledge loaded on-demand via Read tool. Schemas, lookup tables, detection patterns, templates.
- **Deterministic Data File**: A YAML file containing static lookup tables that agents read and apply mechanically — no LLM interpretation needed. CVSS vectors, severity bands, dispatch mappings.
- **Shared Reference**: A file containing content used by multiple agents, stored once and loaded by each consumer. Eliminates duplication and ensures consistency.
- **Output Template**: A file containing the format specification for a pipeline output artifact. Agents Read the template and populate it with analysis results.

## Success Criteria

### Measurable Outcomes

- **SC-001**: All 3 methodology agents (orchestrator, risk-scorer, control-analyzer) are under 500 lines each, verified by `wc -l`.
- **SC-002**: All 3 report agents (report-assembler, threat-report, threat-infographic) are under 300 lines each, verified by `wc -l`.
- **SC-003**: All 17 tachi agents contain a `model:` field in YAML frontmatter, verified by frontmatter inspection.
- **SC-004**: Pipeline output on `examples/agentic-app/architecture.md` is structurally equivalent before and after restructuring — finding count per category within ±2, SARIF result count within ±2, all 7 sections present in threats.md, and severity distribution (Critical/High/Medium/Low counts) within ±1 per level.
- **SC-005**: All 11 leaf agents are byte-identical before and after (excluding `model:` field addition), verified by `git diff`.
- **SC-006**: `_TACHI_AGENT_BEST_PRACTICES.md` compliance table line counts match actual `wc -l` output for all 17 agents.
- **SC-007**: No domain data (tables, schemas, detection patterns, output templates, scoring dimensions) remains inline in any restructured agent body — only orchestration logic (role, workflow, skill loading instructions, constraints).
- **SC-008**: All extracted content is traceable — every line removed from an agent exists in a skill reference, data file, template, or shared reference.

### Assumptions

- Lazy loading via Read tool is context-efficient and does not degrade output quality (validated by Feature 075 regression tests).
- Deterministic YAML data files are reliably processable by Claude agents (to be validated by risk-scorer prototype).
- Line count is a reasonable proxy for context consumption.
- `sonnet` model is sufficient for all 17 agents; escalation to `opus` only if regression testing shows quality issues.
- The existing 3 skill directories (tachi-orchestration, tachi-risk-scoring, tachi-control-analysis) will be extended with additional reference files — no new skill directories needed for methodology agents.
- Report agents will each need a new skill directory for their extracted templates and format specifications.

### Constraints

- **Quality-first**: Zero regression in output quality. If extraction degrades quality, fix the skill file or revert.
- **Relocation, not deletion**: Every line removed must exist in an externalized file.
- **No interface changes**: All pipeline consumers see identical results.
- **Prototype-first gate**: Risk-scorer restructuring must be validated before remaining methodology agents proceed.

### Dependencies

- Feature 075 skill infrastructure (tachi-orchestration, tachi-risk-scoring, tachi-control-analysis skills)
- Feature 074 baseline-aware pipeline additions (content that caused recent growth)
- Example architectures in `examples/` for regression testing
- Existing YAML schema conventions in `schemas/` directory

### Scope Boundaries

**In Scope**: Restructure 6 agents, add model fields to 17 agents, create skill references and data files, create shared references, update best practices document, regression testing.

**Out of Scope**: Modifying leaf agent behavior, changing output formats, changing `/threat-model` interface, splitting agents into sub-agents, performance benchmarking beyond regression verification, switching from lazy to eager skill loading.
