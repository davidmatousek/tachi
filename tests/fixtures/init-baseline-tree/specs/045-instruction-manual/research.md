# Research Summary: 045 - Instruction Manual

## Knowledge Base Findings
- No KB entries found (KB not yet initialized for this project)
- No prior documentation-generation patterns or bug fixes to reference

## Codebase Analysis

### Existing Assets
- **Developer Guide**: `docs/guides/DEVELOPER_GUIDE_TACHI.md` (1,366 lines) — covers `/threat-model` comprehensively; missing `/risk-score`, `/compensating-controls`, standalone `/infographic`, and post-pipeline enrichment workflow
- **Prompt Spec**: `docs/guides/prompts/GUIDE_PROMPT.md` (633 lines, ~80% complete) — source of truth for guide generation; missing sections for Features 035, 036, 039
- **README.md**: Already references `docs/guides/DEVELOPER_GUIDE_TACHI.md` in Integration Reference table
- **Interface Contract**: `docs/INTERFACE-CONTRACT.md` (524 lines) — covers `/threat-model` input/output specs only

### Guide Structure (existing)
- Part 1: Quick Start (6 steps, `/threat-model` only)
- Part 2: Comprehensive Guide (9 sections + 3 appendices)
- Appendix A: OWASP Framework Reference
- Appendix B: Output File Reference (threats.md, SARIF, threat-report.md, attack trees, infographic spec)
- Appendix C: Glossary

### Command Implementations Found
1. `adapters/claude-code/commands/threat-model.md` — Primary pipeline
2. `adapters/claude-code/commands/risk-score.md` — Feature 035, 4-dimensional scoring
3. `adapters/claude-code/commands/infographic.md` — Feature 039, standalone with auto-detection
4. `adapters/claude-code/skills/compensating-controls/` — Feature 036, control detection + residual risk

### Data Flow (verified from command specs)
```
/threat-model (architecture.md) → threats.md, threats.sarif, threat-report.md, attack-trees/
/risk-score (threats.md) → risk-scores.md, risk-scores.sarif
/compensating-controls (risk-scores.md) → compensating-controls.md, compensating-controls.sarif
/infographic (auto-detects richest: risk-scores.md > threats.md) → spec + .jpg per template
```

### Known Issues in Existing Guide
- Stale template name: `infographic-corporate-white.md` should be `infographic-baseball-card.md`
- Agent count: References "14 agents" but should be 15 (Feature 035 added `risk-scorer.md`)
- `/infographic` documented only as `/threat-model` sub-feature, not standalone command

### Examples Directory
- `examples/agentic-app/sample-report/` has complete `/threat-model` output but NO post-pipeline outputs (risk-scores, compensating-controls)
- OpenClaw is described textually in guide, not present as standalone example

## Architecture Constraints
- **Docs-only feature**: No code changes, no agent modifications
- **DoD exception**: Documentation-only phases may not require production deployment
- **User validation required**: A developer must follow the guide end-to-end
- **Single markdown file**: Guide is one file, not a multi-page site
- **Prompt-driven**: Prompt spec is source of truth; guide is generated/updated from it

## Industry Research

### Documentation Structure
- **Diataxis framework** (Tier 1): Tutorial → How-to → Reference → Explanation maps to Quick Start → Pipeline Sections → Appendices → Concept Sections
- Existing 3-part structure is sound; no reorganization needed

### Pipeline Documentation Patterns
- **Data flow diagram** early in guide as orientation anchor
- **Per-command template**: Prerequisites → Invocation → Outputs → Interpretation → Next Step
- **Dependency callouts** at top of each command section
- Each section must be self-contained for non-linear readers

### Output Interpretation
- "Start here" guidance (which section to read first)
- Annotated output snippets with field explanations
- Risk prioritization flowchart (Critical → High → Medium → Low)
- Scoring dimension explanations: what it measures / range / high means / low means

### Prompt-Driven Documentation
- Update spec BEFORE updating guide (maintains source of truth)
- Backport guide-only improvements to spec (prevents drift)
- Targeted update approach (per PRD FR-3) is pragmatic and correct

## Recommendations for Spec
- Sequence FR-1 (spec update) → FR-2 (rename) → FR-3 (guide update) → FR-4/FR-5 (validate)
- Use consistent per-command template for new sections
- Add pipeline overview diagram as anchor for enrichment workflow
- Each command section: Prerequisites → Invocation → Outputs → Interpretation → Next Step
- Extend OpenClaw worked example through all 4 commands (continuity > new example)
- Keep guide structure as-is; gap is content coverage, not architecture
