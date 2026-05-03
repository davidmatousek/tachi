---
triad:
  pm_signoff:
    agent: product-manager
    date: 2026-03-31
    status: APPROVED
    notes: "Full spec-to-plan traceability confirmed. All 14 FRs addressed, 4 waves cover all deliverables. 2 non-blocking observations."
  architect_signoff:
    agent: architect
    date: 2026-03-31
    status: APPROVED_WITH_CONCERNS
    notes: "Technically sound architecture aligned with ADR-002 and Feature 029 precedent. 3 concerns addressed in plan: skill loading mechanism (Read tool per ADR-002), reference file size cap (500 lines), rollback strategy added."
  techlead_signoff: null
---

# Implementation Plan: Tachi Agent Best Practices

**Branch**: `075-tachi-agent-best` | **Date**: 2026-03-31 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `specs/075-tachi-agent-best/spec.md`

## Summary

Enforce tiered line caps on tachi agents by extracting domain knowledge from three oversized methodology agents (orchestrator, risk-scorer, control-analyzer) into on-demand skills using Anthropic's three-level progressive disclosure pattern. Additionally, audit all 18 tachi agents for Claude 4.6 instruction tone alignment, trim threat-report by 1 line, and update the compliance table in `_TACHI_AGENT_BEST_PRACTICES.md`.

## Technical Context

**Language/Version**: Markdown/YAML — all deliverables are agent prompts and skill files (zero application code)
**Primary Dependencies**: None — file-based prompt engineering, no runtime dependencies
**Storage**: File system — `.claude/agents/tachi/` for agents, `.claude/skills/tachi-*/` for skills
**Testing**: Manual pipeline comparison — before/after output quality on example threat models
**Target Platform**: Claude Code agent framework (`.claude/` directory conventions)
**Project Type**: Single — docs/prompt engineering feature
**Performance Goals**: Net context savings of >=1,500 lines across three methodology agents
**Constraints**: Methodology agents <=1,000 lines, Report agents <=800 lines, Leaf agents <=300 lines
**Scale/Scope**: 18 tachi agent files, 3 new skill packages, 1 documentation update

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. General-Purpose Architecture | PASS | Skills are domain-agnostic structure; tachi content is the payload |
| III. Backward Compatibility | PASS | No behavioral changes — content relocated, not modified |
| VI. Testing Excellence | PASS | Before/after pipeline comparison validates output equivalence |
| VII. Definition of Done | PASS | Line count verification + pipeline quality gate + compliance table |
| IX. Git Workflow | PASS | Feature branch `075-tachi-agent-best`, PR workflow |
| X. Product-Spec Alignment | PASS | Spec approved by PM, plan under dual review |

No violations detected. No Complexity Tracking needed.

## Project Structure

### Documentation (this feature)

```
specs/075-tachi-agent-best/
├── plan.md              # This file
├── research.md          # Research phase output (completed during spec)
├── checklists/
│   └── requirements.md  # Spec quality checklist
└── tasks.md             # Task breakdown (/aod.tasks output)
```

### Source Files (repository root)

```
.claude/agents/tachi/
├── orchestrator.md              # Refactor: 2,000 → <=1,000 lines
├── risk-scorer.md               # Refactor: 1,419 → <=1,000 lines
├── control-analyzer.md          # Refactor: 1,367 → <=1,000 lines
├── threat-report.md             # Trim: 801 → <=800 lines
├── {11 leaf agents}.md          # Tone audit only (already compliant on size)
├── {2 report agents}.md         # Tone audit only (already compliant on size)
└── _TACHI_AGENT_BEST_PRACTICES.md  # Update compliance table

.claude/skills/
├── tachi-orchestration/
│   ├── SKILL.md                 # Level 2 — orchestration domain knowledge
│   └── references/
│       ├── sarif-specification.md       # SARIF 2.1.0 generation spec (~490 lines)
│       ├── dispatch-rules.md            # STRIDE + AI dispatch rules and correlation matrices
│       └── output-schemas.md            # Output schema tables, validation checklist, error templates
├── tachi-risk-scoring/
│   ├── SKILL.md                 # Level 2 — risk scoring domain knowledge
│   └── references/
│       ├── scoring-dimensions.md        # Four-dimensional scoring model definitions
│       ├── cvss-vectors.md              # CVSS base vector mappings and weight tables
│       └── severity-bands.md            # Severity band definitions and composite formulas
└── tachi-control-analysis/
    ├── SKILL.md                 # Level 2 — control analysis domain knowledge
    └── references/
        ├── control-categories.md        # 8 control category definitions with detection patterns
        ├── evidence-criteria.md         # Evidence criteria and effectiveness classification
        └── residual-risk.md             # Residual risk calculation formulas and recommendations
```

**Structure Decision**: Skill packages follow the established `.claude/skills/{name}/SKILL.md` + `references/` pattern (ADR-002 prompt segmentation). Each skill's SKILL.md provides an overview and loading instructions; reference files contain the domain-specific content that loads on-demand at Level 3.

## Components

### Component 1: Skill Packages (3 new)

Each skill package contains:
- **SKILL.md**: Frontmatter (`name`, `description`) + overview of the domain knowledge + loading table mapping reference files to workflow phases
- **references/**: Domain knowledge files extracted verbatim from the source agent, with frontmatter (`source_agent`, `extracted_from`, `version`) per Feature 029 precedent

**Extraction principle**: Content is relocated, not rewritten. The domain knowledge in reference files must be identical to what was in the agent — no rewording, no summarization. The agent retains orchestration logic (workflow steps, validation rules, dispatch decisions) and adds a "Skill References" section pointing to the skill.

**Loading mechanism**: Agents use the Read tool to load skill reference files on-demand at specific workflow phases — not frontmatter `skills:` declarations. This follows the ADR-002 pattern: the agent body contains loading instructions (e.g., "Read `tachi-risk-scoring/references/scoring-dimensions.md` when entering scoring phase") and the content is evictable after use. Tachi agents are subagents invoked by the orchestrator, so they do not need Level 1 discovery — the orchestrator already knows which agent to dispatch.

**Reference file size cap**: Individual reference files should stay under 500 lines (matching the SKILL.md body recommendation from Anthropic guidance). If a reference file approaches this limit, split it into focused sub-files. Reference files include a `version` field in frontmatter for staleness detection when agent or skill content evolves independently.

### Component 2: Agent Refactoring (4 agents)

Each refactored agent:
- Retains its complete workflow, phases, and orchestration logic
- Replaces inline domain knowledge with a "Skill References" section containing a loading table (reference name, path, load condition)
- Adds tool restrictions to frontmatter
- Has description field reviewed for delegation routing quality
- Follows data-top ordering (schemas/tables before workflow steps)

### Component 3: Tone Audit (18 agents)

All tachi agents receive:
- Scan for `CRITICAL`, `MUST`, `ALWAYS`, `NEVER` patterns
- Non-critical uses softened (e.g., `MUST` → `should`, `ALWAYS` → default behavior described without emphasis)
- Genuinely critical uses preserved (SARIF format compliance, scoring accuracy, output consistency)
- Tool restrictions added to frontmatter (if missing)
- Description field reviewed for delegation routing specificity

### Component 4: Compliance Table Update

`_TACHI_AGENT_BEST_PRACTICES.md` Section 5 updated with:
- Post-refactoring line counts for all 18 agents
- Status column confirming all agents within tier caps
- Extraction notes for methodology agents (skill name reference)

## Data Flow

```
Before extraction:
  Agent invocation → Full agent (2,000 lines) loads into context → Pipeline execution

After extraction:
  Agent invocation → Lean agent (<=1,000 lines) loads into context
    → Agent reads skill SKILL.md (Level 2) when domain knowledge needed
    → Agent reads specific reference file (Level 3) at relevant workflow phase
    → Pipeline execution with equivalent output
```

## Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| Agent definitions | Markdown + YAML frontmatter | Agent identity, workflow, tool restrictions |
| Skills | Markdown + YAML frontmatter | Domain knowledge with progressive disclosure |
| Validation | Manual pipeline runs | Before/after output quality comparison |
| Line counting | `wc -l` | Tier cap compliance verification |

## Implementation Approach

### Wave 1: Baseline Capture (prerequisite for all other waves)

Capture pre-extraction pipeline output on an example architecture for regression comparison. This establishes the quality gate for SC-006.

### Wave 2: Skill Extraction (3 parallel tracks)

Extract domain knowledge from each methodology agent into its skill package. The three extractions are independent — orchestrator, risk-scorer, and control-analyzer have no cross-dependencies.

**Per-agent extraction workflow** (from `_TACHI_AGENT_BEST_PRACTICES.md` Section 4):
1. Identify extractable content (domain knowledge vs. orchestration logic)
2. Create skill directory and SKILL.md with frontmatter
3. Move content to reference files with source metadata
4. Add "Skill References" section to agent with loading table
5. Remove extracted content from agent body
6. Verify agent is within line cap
7. Verify no content duplication between agent and skill

### Wave 3: Tone Audit + Threat-Report Trim (parallelizable with Wave 2 for leaf/report agents)

Audit all 18 agents for Claude 4.6 alignment. The methodology agent tone audit runs after Wave 2 (since those agents are being restructured). Leaf and report agent audits can run in parallel with Wave 2.

### Wave 4: Validation and Documentation

1. Run full pipeline on example architecture post-extraction
2. Compare output quality against Wave 1 baseline
3. Verify all line counts within tier caps
4. Update compliance table in `_TACHI_AGENT_BEST_PRACTICES.md`

## Risk Mitigation

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Skill extraction degrades output quality | Low | High | Before/after comparison on example threat models (Wave 1 baseline → Wave 4 validation). Rollback: revert to pre-extraction agent files from main branch (`git checkout main -- .claude/agents/tachi/`) |
| Progressive disclosure doesn't load reference files reliably | Low | Medium | Test with actual pipeline runs; agent retains enough context to function without reference files |
| Agent still exceeds cap after extraction | Low | Low | Re-evaluate orchestration/domain boundary; some specification content may be further decomposable |
| Tone audit removes genuinely critical emphasis | Low | Medium | Pipeline comparison catches behavioral regression; preserve all SARIF/format-compliance emphasis |

## Quality Gates

1. **Pre-extraction baseline**: Pipeline output captured before any changes
2. **Per-agent line count**: Each refactored agent verified at or below tier cap
3. **No content duplication**: Agents reference skills, never duplicate content
4. **Post-extraction equivalence**: Pipeline output matches pre-extraction baseline
5. **8-criterion checklist**: All 18 agents pass quality checklist from `_TACHI_AGENT_BEST_PRACTICES.md` Section 6
6. **Compliance table accuracy**: Every line count in the table matches actual file
