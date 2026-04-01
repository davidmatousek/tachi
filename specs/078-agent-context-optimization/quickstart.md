# Quickstart: Working with Restructured Agents

**Feature**: 078 | **Date**: 2026-04-01

## How Restructured Agents Work

After Feature 078, tachi agents follow a two-layer architecture:

1. **Agent definition** (`.claude/agents/tachi/{agent}.md`) — orchestration logic only
2. **Skill references** (`.claude/skills/tachi-*/references/`) — domain knowledge loaded on-demand

## Finding Domain Knowledge

If you need to modify detection patterns, scoring schemas, output templates, or format specifications:

| What | Where |
|------|-------|
| STRIDE dispatch rules | `.claude/skills/tachi-orchestration/references/dispatch-rules.md` |
| CVSS base vectors | `.claude/skills/tachi-risk-scoring/references/cvss-vectors.md` |
| Severity bands | `.claude/skills/tachi-shared/references/severity-bands-shared.md` |
| Control detection patterns | `.claude/skills/tachi-control-analysis/references/control-categories.md` |
| Narrative templates | `.claude/skills/tachi-threat-reporting/references/narrative-templates.md` |
| Typst page specs | `.claude/skills/tachi-report-assembly/references/typst-template-contract.md` |
| Infographic design | `.claude/skills/tachi-infographics/references/visual-design-system.md` |

## Loading Pattern

Agents use the Read tool to load references on-demand. Each agent contains a **skill reference table** mapping phases to files:

```markdown
| Reference | File | Load When |
|-----------|------|-----------|
| CVSS vectors | .claude/skills/tachi-risk-scoring/references/cvss-vectors.md | Phase 3: CVSS scoring |
| Severity bands | .claude/skills/tachi-shared/references/severity-bands-shared.md | Phase 7: Composite calc |
```

At each workflow branch point, the agent includes a MANDATORY Read instruction. This ensures domain knowledge is loaded exactly when needed and evicted from context afterward.

## Tier Caps

| Tier | Agents | Hard Cap | Target |
|------|--------|----------|--------|
| Leaf | 11 STRIDE + AI agents | 200 lines | 150 lines |
| Report | report-assembler, threat-report, threat-infographic | 300 lines | 250 lines |
| Methodology | orchestrator, risk-scorer, control-analyzer | 500 lines | 400 lines |

## Verification

Check agent compliance: `wc -l .claude/agents/tachi/*.md`

Run regression test: Execute `/threat-model` on `examples/agentic-app/architecture.md` and compare output structure.
