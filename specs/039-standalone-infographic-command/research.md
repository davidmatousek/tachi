# Research Summary: Standalone /infographic Command

## Knowledge Base Findings
- KB search infrastructure not available (no `kb-search` make target configured)
- No prior patterns found for command extraction or pipeline decoupling

## Codebase Analysis

### Existing Components
| Component | Path | Status |
|-----------|------|--------|
| Infographic Agent | `.claude/agents/tachi/threat-infographic.md` | Mature, threats.md only |
| Baseball Card Template | `.claude/agents/tachi/templates/infographic-baseball-card.md` | Stable, no changes needed |
| System Architecture Template | `.claude/agents/tachi/templates/infographic-system-architecture.md` | Stable, no changes needed |
| /threat-model Command | `.claude/commands/threat-model.md` | Phase 6 removal needed |
| Orchestrator Agent | `.claude/agents/tachi/orchestrator.md` | Phase 6 cleanup needed |
| Infographic Schema | `schemas/infographic.yaml` | Stable, no changes needed |
| Risk-Scoring Schema | `schemas/risk-scoring.yaml` | Reference for dual-path extraction |
| /infographic Command | `.claude/commands/infographic.md` | **Does not exist — must create** |

### Data Extraction Patterns
- **From threats.md**: 5-step extraction (metadata, Section 6 severity counts, component heat map, top findings, architecture overlay) + spatial layout (trust zones, data flows)
- **From risk-scores.md**: Quantitative composite scores, severity bands — but LACKS structural/spatial data (no project metadata, trust zones, data flows)
- **Dual-source strategy**: risk-scores.md for quantitative scores + co-located threats.md for structural skeleton

### Platform Adapters Requiring Updates
1. `adapters/claude-code/agents/orchestrator.md`
2. `adapters/copilot/agents/orchestrator.agent.md`
3. `adapters/cursor/rules/orchestrator.mdc`
4. `adapters/generic/prompts/00-orchestrator.md`
5. `adapters/claude-code/commands/threat-model.md`

### Key Agent Metadata
```yaml
# From threat-infographic.md
aliases:
  corporate-white: baseball-card
templates:
  baseball-card: .claude/agents/tachi/templates/infographic-baseball-card.md
  system-architecture: .claude/agents/tachi/templates/infographic-system-architecture.md
```

## Architecture Constraints

### Relevant ADRs
| ADR | Decision | Impact |
|-----|----------|--------|
| ADR-014 | Gemini API optional with graceful degradation (6 conditions) | Spec is always primary deliverable; image is best-effort |
| ADR-010 | Minimal-return subagent architecture | Agent writes to disk, returns <10 lines |
| ADR-011 | Multi-flag opt-out pattern | Each flag independent, fully combinable |
| ADR-008 | Opt-out flag for default-on steps | `--no-X` naming convention |
| ADR-006 | Non-fatal error handling for observability | Never block primary execution |
| ADR-002 | Prompt segmentation for context efficiency | Core + on-demand reference files |

### Key Constraints
- **Fresh context isolation** (ADR-010): Infographic agent runs with only selected data source as input
- **Spec-first** (ADR-014): Markdown spec is primary deliverable; Gemini image is best-effort
- **Graceful degradation**: 6 error conditions all result in spec saved, image skipped
- **Risk distribution accuracy**: Counts must match input file EXACTLY (zero discrepancy)

### Dependencies
- PRD-018 (Threat Infographic Agent) — delivered, provides agent + templates
- PRD-035 (Quantitative Risk Scoring) — delivered, provides risk-scores.md format
- Gemini API via `GEMINI_API_KEY` environment variable

## Industry Research
- **Unix Philosophy**: Small, composable tools that do one thing well — directly supports decoupling infographic generation from the pipeline
- **CLI best practices**: Machine-readable output, streams as universal interface, progress to stderr
- **Modern trend**: Terminal-first AI development favors composable command patterns over monolithic pipelines

## Recommendations for Spec
- Follow existing command structure pattern from `/threat-model` and `/risk-score` commands
- Implement dual-path data extraction as the major enhancement to the infographic agent
- Auto-detection should prefer richest data source (risk-scores.md > threats.md)
- Require co-located threats.md when risk-scores.md is primary (for structural data)
- Remove Phase 6 completely from orchestrator — not optional, not behind a flag
- Update all 5 platform adapter files to reflect 5-phase pipeline
- Template files and schema require no changes
- Error handling follows ADR-014 graceful degradation pattern
