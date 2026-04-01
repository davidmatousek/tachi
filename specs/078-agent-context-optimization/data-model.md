# Content Extraction Map: Agent Context Optimization

**Feature**: 078 | **Date**: 2026-04-01

## Entity: Agent Definition

A markdown file defining orchestration logic for a tachi pipeline agent.

| Field | Description |
|-------|-------------|
| YAML frontmatter | name, description, tools, model (NEW), metadata |
| Role identity | 2-3 lines defining purpose |
| Skill reference table | Navigation table: phase → reference file → load condition |
| Workflow skeleton | Numbered phases with decision points |
| Output format summary | Structure overview (not full template) |
| Constraints | Error handling, validation, boundaries |

**Relationships**: Agent → loads → Skill Reference Files (1:many via Read tool)

## Entity: Skill Reference File

A markdown or YAML file containing domain knowledge loaded on-demand.

| Field | Description |
|-------|-------------|
| File path | `.claude/skills/tachi-*/references/{name}.md` |
| Content type | detection-patterns, scoring-schemas, output-templates, format-specs, construction-rules, visual-design |
| Load condition | Phase or decision point when Read is triggered |
| Consumers | List of agents that load this reference |

**Relationships**: Skill Reference → consumed by → Agent Definitions (many:many)

## Entity: Shared Reference

A reference file used by multiple agents, stored once.

| Field | Description |
|-------|-------------|
| File path | `.claude/skills/tachi-shared/references/{name}.md` |
| Content | Deduplicated cross-agent content (severity bands, STRIDE categories, finding format) |
| Consumers | All agents that previously duplicated this content |

**Relationships**: Shared Reference → consumed by → Multiple Agents

## Extraction Map Summary

| Source Agent | Lines Extracted | Destination Skill | New Files | Enhanced Files |
|-------------|----------------|-------------------|-----------|----------------|
| orchestrator (1,286) | ~500 | tachi-orchestration | 5 | 1 |
| risk-scorer (1,093) | ~480 | tachi-risk-scoring | 3 | 2 |
| control-analyzer (973) | ~170 | tachi-control-analysis | 0 | 3 (verify) |
| report-assembler (654) | ~200 | tachi-report-assembly (NEW) | 3 | 0 |
| threat-report (800) | ~500 | tachi-threat-reporting (NEW) | 3 | 0 |
| threat-infographic (775) | ~460 | tachi-infographics (NEW) | 4 | 0 |
| **Total** | **~2,310** | **6 skills** | **18 files** | **6 files** |
