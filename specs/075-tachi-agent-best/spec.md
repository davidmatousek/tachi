---
prd_reference: docs/product/02_PRD/075-tachi-agent-best-practices-2026-03-31.md
triad:
  pm_signoff:
    agent: product-manager
    date: 2026-03-31
    status: APPROVED
    notes: "Full PRD alignment confirmed. 3 non-blocking observations: priority label cosmetic mismatch (US-2/US-3 both P2 vs PRD P1/P1), valid US-2 consolidation of PRD tone audit scope, data-top ordering addition well-grounded in FR-3."
  architect_signoff: null
  techlead_signoff: null
---

# Feature Specification: Tachi Agent Best Practices

**Feature Branch**: `075-tachi-agent-best`
**Created**: 2026-03-31
**Status**: Draft
**Input**: PRD 075 — Enforce 1,000-line hard cap on tachi agents by extracting domain knowledge into on-demand skills, aligned with Anthropic Claude 4.6 prompting best practices

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Skill Extraction for Methodology Agents (Priority: P1)

An agent maintainer needs to add baseline-aware logic to the orchestrator, risk-scorer, or control-analyzer for Issue #74. Today, all three agents exceed 1,000 lines because domain knowledge (scoring schemas, detection patterns, dispatch rules) is embedded inline. The maintainer needs each agent refactored to reference on-demand skills, bringing them within the 1,000-line cap and freeing room for new phases.

**Why this priority**: This is the core deliverable. Without skill extraction, the methodology agents cannot accommodate new capabilities (Issue #74 blocker) and waste context window budget on every invocation.

**Independent Test**: Run the full `/threat-model` pipeline followed by `/risk-score` and `/compensating-controls` on an existing example architecture before and after extraction. Compare output quality — threat detection completeness, risk scores, and control coverage must be equivalent.

**Acceptance Scenarios**:

1. **Given** the orchestrator agent at 2,000 lines, **When** domain knowledge is extracted into the `tachi-orchestration` skill, **Then** the orchestrator is at or below 1,000 lines and references the skill for STRIDE dispatch rules, correlation matrices, and output schemas.
2. **Given** the risk-scorer agent at 1,419 lines, **When** scoring dimensions, CVSS vectors, weight tables, and severity bands are extracted into the `tachi-risk-scoring` skill, **Then** the risk-scorer is at or below 1,000 lines.
3. **Given** the control-analyzer agent at 1,367 lines, **When** control categories, detection patterns, and evidence criteria are extracted into the `tachi-control-analysis` skill, **Then** the control-analyzer is at or below 1,000 lines.
4. **Given** any extracted skill, **When** the agent references it during pipeline execution, **Then** the skill's SKILL.md loads at Level 2 and reference files load on-demand at Level 3.
5. **Given** the full pipeline run pre-extraction and post-extraction on the same example architecture, **When** outputs are compared, **Then** threat detection completeness, risk scoring accuracy, and control detection coverage are equivalent.

---

### User Story 2 - Claude 4.6 Tone Audit (Priority: P2)

A pipeline operator runs `/threat-model` and wants the model focused on their architecture input, not distracted by aggressive emphasis patterns in agent prompts. All tachi agents need auditing for instruction tone, tool restrictions, description field quality, and data-top ordering per Anthropic Claude 4.6 best practices.

**Why this priority**: Tone audit improves model focus across all invocations. It is independent of skill extraction and can be tested separately, but lower priority because the context savings from US-1 have larger impact.

**Independent Test**: Scan all tachi agent files for `CRITICAL`, `MUST`, `ALWAYS`, `NEVER` patterns before and after the audit. Verify that remaining instances are genuinely critical. Check that all agents have tool restrictions in frontmatter and specific description fields.

**Acceptance Scenarios**:

1. **Given** any tachi agent, **When** scanned for aggressive emphasis patterns (`CRITICAL`, `MUST`, `ALWAYS`, `NEVER`), **Then** only genuinely critical uses remain — non-critical instances have been softened or removed.
2. **Given** any tachi agent, **When** its frontmatter is inspected, **Then** tool restrictions are declared.
3. **Given** any tachi agent, **When** its description field is read, **Then** it is specific enough for correct delegation routing by the orchestrator.
4. **Given** any tachi agent with schemas or tables, **When** its content ordering is reviewed, **Then** data definitions appear before workflow steps (data-top ordering).

---

### User Story 3 - Threat-Report Trim (Priority: P2)

The threat-report agent is 1 line over its 800-line Report tier cap. A trivial trim brings it into compliance without structural changes.

**Why this priority**: Minimal effort for compliance. Can be done independently alongside US-1 or US-2.

**Independent Test**: Count lines in `threat-report.md` after trim. Verify it is at or below 800 lines and that no functional content was removed.

**Acceptance Scenarios**:

1. **Given** the threat-report agent at 801 lines, **When** trimmed, **Then** it is at or below 800 lines.
2. **Given** the trimmed threat-report agent, **When** a threat report is generated from example output, **Then** the report quality is equivalent to pre-trim output.

---

### User Story 4 - Best Practices Guide and Compliance Table (Priority: P3)

A new contributor wants to extend tachi with a new threat category. They consult `_TACHI_AGENT_BEST_PRACTICES.md` for tier guidelines, extraction patterns, and the current compliance table. The compliance table must reflect post-refactoring line counts to confirm all agents are within tier caps.

**Why this priority**: Documentation update depends on US-1, US-2, and US-3 completing first. It is the final verification step.

**Independent Test**: Read the compliance table in `_TACHI_AGENT_BEST_PRACTICES.md` and verify every agent's line count matches the actual file.

**Acceptance Scenarios**:

1. **Given** the compliance table in `_TACHI_AGENT_BEST_PRACTICES.md`, **When** compared against actual file line counts post-refactoring, **Then** all entries are accurate and within their tier caps.
2. **Given** a new contributor reading the best practices guide, **When** they follow the skill extraction checklist, **Then** the steps are clear and actionable for moving domain knowledge from an agent into a skill.

---

### Edge Cases

- What happens if a skill's reference file exceeds the recommended size? The reference file should be split into smaller, focused files — each loadable independently.
- What happens if an agent still exceeds its cap after extraction of all identified domain knowledge? Re-evaluate what constitutes "orchestration logic" vs. "domain knowledge" — some content classified as orchestration may be extractable with a different decomposition.
- What happens if the tone audit removes emphasis that was genuinely critical? The before/after pipeline comparison (US-1 quality gate) catches any behavioral regression from tone changes.
- What happens if extracted content is duplicated between the skill and agent? This is a defect — the agent must reference the skill, not duplicate its content. The extraction checklist in `_TACHI_AGENT_BEST_PRACTICES.md` Section 4 guards against this.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system must create a `tachi-orchestration` skill containing STRIDE dispatch rules, correlation matrices, and output schemas extracted from the orchestrator agent
- **FR-002**: The system must create a `tachi-risk-scoring` skill containing scoring dimensions, CVSS base vectors, weight tables, and severity band definitions extracted from the risk-scorer agent
- **FR-003**: The system must create a `tachi-control-analysis` skill containing control categories, detection patterns, and evidence criteria extracted from the control-analyzer agent
- **FR-004**: Each skill must follow the three-level progressive disclosure structure: SKILL.md (Level 2) plus reference files in a `references/` subdirectory (Level 3)
- **FR-005**: The orchestrator agent must be refactored to at or below 1,000 lines, referencing the `tachi-orchestration` skill for extracted content
- **FR-006**: The risk-scorer agent must be refactored to at or below 1,000 lines, referencing the `tachi-risk-scoring` skill for extracted content
- **FR-007**: The control-analyzer agent must be refactored to at or below 1,000 lines, referencing the `tachi-control-analysis` skill for extracted content
- **FR-008**: The threat-report agent must be trimmed to at or below 800 lines with no functional content removed
- **FR-009**: All tachi agents must be audited for aggressive emphasis patterns, with non-critical uses of `CRITICAL`, `MUST`, `ALWAYS`, `NEVER` softened or removed
- **FR-010**: All tachi agents must have tool restrictions declared in their frontmatter
- **FR-011**: All tachi agents must have description fields specific enough for correct delegation routing
- **FR-012**: All tachi agents with schemas or tables must follow data-top ordering (data definitions before workflow steps)
- **FR-013**: The compliance table in `_TACHI_AGENT_BEST_PRACTICES.md` must be updated with accurate post-refactoring line counts for all agents
- **FR-014**: Pipeline output quality must be preserved — the threat analysis pipeline must produce equivalent results before and after all changes

### Key Entities

- **Skill Package**: A directory under `.claude/skills/tachi-{name}/` containing a SKILL.md file and optional `references/` subdirectory with on-demand content files
- **Agent Definition**: A markdown file under `.claude/agents/tachi/` defining an agent's identity, capabilities, workflow, and tool restrictions
- **Tier**: A classification (Leaf/Report/Methodology) with associated target and hard cap line limits governing agent size
- **Reference File**: A markdown file within a skill's `references/` directory containing domain knowledge that loads on-demand during specific workflow phases

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: The orchestrator agent is at or below 1,000 lines (down from 2,000)
- **SC-002**: The risk-scorer agent is at or below 1,000 lines (down from 1,419)
- **SC-003**: The control-analyzer agent is at or below 1,000 lines (down from 1,367)
- **SC-004**: The threat-report agent is at or below 800 lines (down from 801)
- **SC-005**: Three skill packages exist: `tachi-orchestration`, `tachi-risk-scoring`, `tachi-control-analysis` — each with SKILL.md and at least one reference file
- **SC-006**: Pipeline output quality preserved — running `/threat-model`, `/risk-score`, and `/compensating-controls` on the same example architecture produces equivalent results before and after extraction
- **SC-007**: All 18 tachi agents pass the 8-criterion quality checklist in `_TACHI_AGENT_BEST_PRACTICES.md` Section 6
- **SC-008**: The compliance table in `_TACHI_AGENT_BEST_PRACTICES.md` reflects accurate, post-refactoring line counts with all agents within their tier caps
- **SC-009**: Net context savings of at least 1,500 lines across the three methodology agents (from 4,786 total to at most 3,000)

### Assumptions

- Anthropic's three-level progressive disclosure works as documented — SKILL.md loads at Level 2 when the skill is invoked, reference files load at Level 3 on demand
- Extracted domain knowledge can be cleanly separated from orchestration logic without creating circular dependencies between agents and their skills
- The existing `.claude/skills/` directory structure supports tachi-namespaced skill packages alongside AOD skills
- No changes to the AOD agent best practices document (`_AGENT_BEST_PRACTICES.md`) are needed — this feature targets tachi agents only
- All 11 Leaf agents are already compliant and require no structural changes (only tone audit applies to them)
