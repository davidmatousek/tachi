---
prd:
  number: "075"
  topic: tachi-agent-best-practices
  created: 2026-03-31
  status: Approved
  type: feature
triad:
  pm_signoff: {agent: product-manager, date: 2026-03-31, status: APPROVED, notes: "Directly addresses context efficiency and maintainability — prerequisite for #74 baseline-aware pipeline"}
  architect_signoff: {agent: architect, date: 2026-03-31, status: APPROVED_WITH_CONCERNS, notes: "Clarify skill loading mechanism (native vs Read-tool per ADR-002); add reference file staleness risk; consider domain-concept skill naming; consider ADR"}
  techlead_signoff: {agent: team-lead, date: 2026-03-31, status: APPROVED_WITH_CONCERNS, notes: "Realistic single phase (4 waves, 12-18h); define concrete tone audit threshold at spec stage; orchestrator extraction may need architect checkpoint"}
source:
  idea_id: 75
  story_id: null
---

# Tachi Agent Best Practices — Product Requirements Document

**Status**: Approved
**Created**: 2026-03-31
**Author**: product-manager
**Reviewers**: architect, team-lead
**Priority**: P1 (High)

---

## Executive Summary

### The One-Liner

Enforce a 1,000-line hard cap on tachi agents by extracting domain knowledge into on-demand skills, aligned with Anthropic Claude 4.6 prompting best practices.

### Problem Statement

Three tachi methodology agents significantly exceed reasonable size limits, consuming excessive context window space on every invocation:

| Agent | Current Lines | Over 1,000 Cap By |
|-------|--------------|-------------------|
| orchestrator | 2,000 | +1,000 (2x cap) |
| risk-scorer | 1,419 | +419 |
| control-analyzer | 1,367 | +367 |

Anthropic's published guidance confirms that complex system prompts trigger excessive adaptive thinking in Claude 4.6, and large prompts dilute attention on key instructions. These oversized agents waste context window budget and reduce model focus on the user's actual architecture input.

### Proposed Solution

A three-part approach:

1. **Skill extraction**: Move domain knowledge (scoring schemas, detection patterns, dispatch rules) from agent definitions into skills that load on-demand via Anthropic's progressive disclosure pattern
2. **Tiered line caps**: Enforce Leaf (300), Report (800), and Methodology (1,000) hard caps documented in `_TACHI_AGENT_BEST_PRACTICES.md`
3. **Claude 4.6 alignment**: Audit all tachi agents for instruction tone, data-top ordering, tool restrictions, and description field quality

### Success Criteria

- All three methodology agents at or below 1,000 lines
- threat-report agent at or below 800 lines
- Pipeline output quality preserved (equivalent results pre/post extraction)
- All tachi agents pass the 8-criterion quality checklist

### Timeline

Single implementation phase — all refactoring and skill creation in one feature branch.

---

## Strategic Alignment

### Product Vision Alignment

**Reference**: [product-vision.md](../01_Product_Vision/product-vision.md)

This feature directly supports tachi's mission as an automated threat modeling toolkit. Leaner agents mean faster invocations, sharper model focus on user architecture input, and a more maintainable codebase for contributors. It also unblocks Issue #74 (baseline-aware pipeline), which needs room in methodology agents for new phases.

### Prerequisite Chain

- **Enables**: #74 (Baseline-aware pipeline — agents need room for new phases)
- **Related**: Feature 003 (original AOD agent refactoring), Features 067/071 (determinism pattern)

---

## Target Users & Personas

### Primary Persona: Agent Maintainer

- **Role**: Developer extending or maintaining tachi agents
- **Goals**: Add new capabilities without exceeding context limits
- **Pain Points**: Oversized agents are hard to reason about, modify, and test; no clear guidelines on what belongs in an agent vs. a skill

### Secondary Persona: Pipeline Operator

- **Role**: Developer running `/threat-model` on their architecture
- **Goals**: Fast, focused threat analysis with accurate results
- **Pain Points**: Model wastes thinking budget on 2,000 lines of inline content instead of focusing on the architecture being analyzed

### Tertiary Persona: New Contributor

- **Role**: Developer adding new threat categories or agents to tachi
- **Goals**: Clear patterns to follow so new agents are lean from the start
- **Pain Points**: No documented tier system or extraction pattern before this feature

---

## User Stories

### US-1: Agent Maintainer — Room for New Phases

**When** I need to add baseline-aware logic to the orchestrator, risk-scorer, or control-analyzer for Issue #74,
**I want to** find each agent under 1,000 lines with domain knowledge extracted into skills,
**So I can** add new phases without exceeding context limits.

**Acceptance Criteria**:
- Given the orchestrator agent, when I count its lines, then it is at or below 1,000 lines
- Given the risk-scorer agent, when I count its lines, then it is at or below 1,000 lines
- Given the control-analyzer agent, when I count its lines, then it is at or below 1,000 lines

**Priority**: P0
**Effort**: L

### US-2: Pipeline Operator — On-Demand Skill Loading

**When** I run `/threat-model` on my architecture,
**I want to** the orchestrator to load scoring schemas on-demand via skills instead of carrying 2,000 lines of inline content,
**So I can** get faster invocations with the model focused on my architecture.

**Acceptance Criteria**:
- Given a threat model invocation, when the orchestrator dispatches to risk-scorer, then scoring schemas load from the `tachi-risk-scoring` skill, not inline
- Given a threat model invocation, when the pipeline completes, then output quality is equivalent to pre-extraction results

**Priority**: P0
**Effort**: M

### US-3: New Contributor — Clear Tier Guidelines

**When** I extend tachi with a new threat category or agent,
**I want to** clear tier guidelines and a documented skill extraction pattern,
**So I can** build lean agents from the start.

**Acceptance Criteria**:
- Given `_TACHI_AGENT_BEST_PRACTICES.md`, when I read the tier table, then I find target and hard cap for each tier (Leaf, Report, Methodology)
- Given an agent exceeding its cap, when I follow the extraction checklist, then I can move domain knowledge into a skill without losing functionality

**Priority**: P1
**Effort**: S (documentation already exists)

### US-4: Pipeline Operator — Claude 4.6 Alignment

**When** I run the tachi pipeline,
**I want to** agents aligned with Claude 4.6 prompting best practices,
**So I can** avoid overtriggering on aggressive instructions and wasted thinking budget.

**Acceptance Criteria**:
- Given any tachi agent, when I scan for `CRITICAL`, `MUST`, `ALWAYS`, `NEVER` patterns, then only genuinely critical uses remain
- Given any tachi agent, when I check its frontmatter, then tool restrictions are declared
- Given any tachi agent, when I read its description field, then it is specific enough for correct delegation routing

**Priority**: P1
**Effort**: M

---

## Functional Requirements

### FR-1: Skill Creation

Create three skill packages:

| Skill | Source Agent | Content to Extract |
|-------|-------------|-------------------|
| `tachi-orchestration` | orchestrator | STRIDE dispatch rules, correlation matrices, output schemas |
| `tachi-risk-scoring` | risk-scorer | Scoring dimensions, CVSS base vectors, weight tables, severity bands |
| `tachi-control-analysis` | control-analyzer | Control categories, detection patterns, evidence criteria |

**Skill file structure** (per Anthropic's three-level progressive disclosure):
```
.claude/skills/tachi-{agent-name}/
  SKILL.md                    # Level 2 — loads when invoked
  references/
    scoring-schema.md         # Level 3 — loads on-demand
    detection-patterns.md
    output-template.md
```

### FR-2: Agent Refactoring

Refactor three methodology agents to reference skills instead of inline content:

| Agent | Current | Target | Action |
|-------|---------|--------|--------|
| orchestrator | 2,000 | <=1,000 | Extract into `tachi-orchestration` skill |
| risk-scorer | 1,419 | <=1,000 | Extract into `tachi-risk-scoring` skill |
| control-analyzer | 1,367 | <=1,000 | Extract into `tachi-control-analysis` skill |
| threat-report | 801 | <=800 | Trivial trim (1 line over cap) |

### FR-3: Claude 4.6 Tone Audit

Audit all tachi agents for:
- Aggressive emphasis patterns (`CRITICAL`, `MUST`, `ALWAYS`, `NEVER`) — reduce to genuinely critical uses only
- Tool restrictions added to frontmatter
- Description field quality for delegation routing
- Data-top ordering (schemas/tables before workflow steps)

### FR-4: Compliance Table Update

Update `_TACHI_AGENT_BEST_PRACTICES.md` Section 5 (Current Compliance) with post-refactor line counts confirming all agents are within tier caps.

---

## Non-Functional Requirements

### Output Quality Preservation

The pipeline must produce equivalent threat analysis results after extraction. This is the primary quality gate — no regression in:
- Threat detection completeness
- Risk scoring accuracy
- Control detection coverage
- Report and infographic quality

### Context Efficiency

- Methodology agents consume <=1,000 lines of context per invocation (down from 2,000 max)
- Domain knowledge loads on-demand only when the skill is invoked
- Net context savings: ~2,786 lines across three agents (from 4,786 to <=3,000 total)

---

## Scope & Boundaries

### In Scope (P0/P1)

- Create skill packages for orchestrator, risk-scorer, control-analyzer
- Refactor three methodology agents to reference skills
- Trim threat-report to <=800 lines
- Audit all tachi agents for Claude 4.6 instruction tone
- Add tool restrictions to agent frontmatter
- Review description fields for delegation routing quality
- Update compliance table in `_TACHI_AGENT_BEST_PRACTICES.md`
- Verify output quality preserved post-extraction

### Out of Scope

- AOD agent changes (AOD has its own `_AGENT_BEST_PRACTICES.md`)
- Leaf agent changes (all 11 already compliant at 108-196 lines)
- Behavioral changes to pipeline output (that's #74)
- Report-assembler or threat-infographic changes (both within cap)

### Assumptions

- Anthropic's skill loading (progressive disclosure) works as documented — SKILL.md loads at Level 2, reference files at Level 3
- Extracted content can be referenced without duplication (agent body is self-contained orchestration)
- No circular dependencies between agents and their skills

---

## Risks & Dependencies

### Technical Risks

**Risk 1**: Skill extraction degrades output quality
- **Likelihood**: Low (content is identical, just relocated)
- **Impact**: High (threat analysis accuracy is core value)
- **Mitigation**: Before/after comparison on existing example threat models

**Risk 2**: Progressive disclosure doesn't load reference files reliably
- **Likelihood**: Low (documented Anthropic pattern)
- **Impact**: Medium (agents would need inline fallback)
- **Mitigation**: Test with actual pipeline runs before merging

### Dependencies

**Enables**: Issue #74 (baseline-aware pipeline — agents need room for new phases)
**No blocking dependencies** — this feature can proceed independently.

---

## Definition of Done

- [ ] Skills created: `tachi-orchestration/`, `tachi-risk-scoring/`, `tachi-control-analysis/`
- [ ] orchestrator.md refactored to <=1,000 lines, referencing `tachi-orchestration` skill
- [ ] risk-scorer.md refactored to <=1,000 lines, referencing `tachi-risk-scoring` skill
- [ ] control-analyzer.md refactored to <=1,000 lines, referencing `tachi-control-analysis` skill
- [ ] threat-report.md trimmed to <=800 lines
- [ ] All tachi agents: aggressive emphasis patterns reduced to genuinely critical uses
- [ ] All tachi agents: tool restrictions added to frontmatter
- [ ] All tachi agents: description field reviewed for delegation routing quality
- [ ] Output quality preserved: pipeline produces equivalent results pre/post extraction
- [ ] `_TACHI_AGENT_BEST_PRACTICES.md` compliance table updated with post-refactor line counts
- [ ] AOD `_AGENT_BEST_PRACTICES.md` unchanged

---

## References

- [GitHub Issue #75](https://github.com/davidmatousek/tachi/issues/75) — Source idea with full detail
- [_TACHI_AGENT_BEST_PRACTICES.md](../../.claude/agents/tachi/_TACHI_AGENT_BEST_PRACTICES.md) — Tier definitions, extraction pattern, compliance table
- Anthropic: "Building Effective Agents" — six workflow patterns
- Anthropic: "Effective Context Engineering for AI Agents" — progressive disclosure
- Anthropic: "Claude 4.6 Best Practices" — instruction tone, overtriggering
- Anthropic: "Equipping Agents with Agent Skills" — three-level disclosure, SKILL.md structure
- Feature 029: [Agent Refactoring: Right-Size](029-agent-refactoring-right-size-2026-03-25.md) — prior refactoring precedent

---

## Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-03-31 | product-manager | Initial PRD from GitHub Issue #75 |
