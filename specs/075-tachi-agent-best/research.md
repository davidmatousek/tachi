# Research Summary: Tachi Agent Best Practices

## Knowledge Base Findings

- **PAT-012**: Docs-only template features complete faster than estimated (50-70% reduction). This feature modifies only markdown agent/skill files — single-session delivery expected.
- **KB-010**: Docs-only prompt engineering features deliver in a single session. All 075 changes are markdown/YAML prompt edits.
- **PAT-008**: Well-structured specs with atomic tasks enable same-day delivery. Feature 039 touched 32 files across 5 adapters same-day — similar scope to 075.
- **PAT-001**: Wave-based parallelism for content-heavy features. Independent agent refactoring can run in parallel.
- Key lesson: Content-only features (markdown/YAML) have high parallelism potential because most files have no cross-dependencies.

## Codebase Analysis

### Agents Requiring Refactoring

| Agent | Lines | Tier Cap | Over By | File Size |
|-------|-------|----------|---------|-----------|
| orchestrator.md | 2,000 | 1,000 | +1,000 | 111 KB |
| risk-scorer.md | 1,419 | 1,000 | +419 | 85 KB |
| control-analyzer.md | 1,367 | 1,000 | +367 | 83 KB |
| threat-report.md | 801 | 800 | +1 | — |

### Extraction Candidates (from codebase audit)

**Orchestrator** (~1,000 lines extractable):
- SARIF 2.1.0 generation specification (~490 lines)
- Validation checklist (~80 lines)
- Error templates (~100 lines)
- Output schema tables and correlation matrices
- STRIDE dispatch rules table

**Risk-Scorer** (~419+ lines extractable):
- Scoring dimension definitions and tables
- CVSS base vector mappings
- Weight tables and formulas
- Severity band definitions
- Example scoring calculations

**Control-Analyzer** (~367+ lines extractable):
- 8 control category definitions
- Detection patterns per category
- Evidence criteria specifications
- Control effectiveness classification rules
- Residual risk calculation formulas

### Prior Precedent: Feature 029 (Agent Refactoring Right-Size)

Feature 029 successfully refactored **AOD agents** (not tachi) using the identical pattern:
- orchestrator: 2,085 → 1,273 lines (6 reference documents created)
- threat-report: 801 → 472 lines
- threat-infographic: 592 → 414 lines

Key lessons from 029:
1. **Preservation-first**: Run capability inventory before extracting
2. **Reference document frontmatter**: Use `source_agent`, `loaded_at`, `extracted_from`, `version` fields (snake_case)
3. **Zero-regression validation**: Byte-identical checks on untouched agents
4. **Loading instructions pattern**: Agents include "Reference Documents" section with loading table
5. **Realistic line targets**: Account for irreducible specification content

### No Existing tachi-* Skills

No skills matching `tachi-*` pattern exist yet. All 21 existing skills are AOD lifecycle skills. The field is clear for new skill creation.

### Compliance Status (All 18 tachi agents)

- 11 Leaf agents: All compliant (108-196 lines, cap 300)
- 3 Report agents: 2 compliant, 1 over by 1 line (threat-report)
- 3 Methodology agents: All over cap (totaling +1,786 lines over)
- 1 Best practices guide: 245 lines (documentation, not an agent)

### Aggressive Emphasis Scan

- orchestrator.md: 4+ `MUST` instances — all genuinely critical SARIF spec compliance
- risk-scorer.md: 30+ `MUST` instances — many critical, some opportunity for tone reduction
- control-analyzer.md: 30+ `MUST` instances — similar distribution to risk-scorer

## Architecture Constraints

### Relevant ADRs

- **ADR-002** (Prompt Segmentation): Monolithic skill split into core + on-demand references. Achieved 78% token reduction (25,800 → 5,690 tokens). Pattern: MANDATORY Read instructions at branch points.
- **ADR-010** (Minimal-Return Architecture): Subagents write findings to `.aod/results/`, return only brief summaries (<10 lines). Convention-based enforcement.
- **ADR-007** (Stack Pack Dual-Surface): Rules auto-loaded, personas on-demand. 800-line context budget for rules surface.
- **ADR-011** (Multi-Flag Opt-Out): Independent skip flags per quality gate step.

### Skill Structure Pattern

Three-level progressive disclosure:
- **Level 1** (always loaded): Skill name + description in frontmatter (~100 tokens)
- **Level 2** (on invocation): Full SKILL.md body — workflow steps, routing tables
- **Level 3** (on demand): Reference files in `references/` subdirectory

### Key Constraint

Feature 075 uses **skills** (`.claude/skills/tachi-*/`) not **reference documents** (`.../references/`). Feature 029 used reference docs in `adapters/claude-code/agents/references/`. The distinction: skills are first-class Anthropic constructs with three-level loading; references are ad-hoc files loaded via Read tool.

## Industry Research

### Anthropic Official Guidance

- **Context is the bottleneck, not intelligence.** Every token competes with conversation history and user input.
- **SKILL.md body target**: Under 500 lines. Split into reference files when approaching this limit.
- **CLAUDE.md target**: 50-60 lines / ~500 tokens for always-loaded root context.
- **Sub-agent returns**: 1,000-2,000 tokens (tachi stricter: 15 lines max per ADR-010).
- **Frontier LLMs**: Follow ~150-200 instructions reliably; Claude Code system prompt already consumes ~50 slots.
- **Progressive disclosure achieves**: 96% token savings, 93% latency improvement.
- **Keep references one level deep** from SKILL.md — deeply nested references cause partial reads.

### Key Principles

1. Challenge each line: "Does this justify its token cost?"
2. Start simple — increase complexity only when simpler solutions fail
3. Match specificity to fragility — exact scripts for fragile operations, heuristics for flexible tasks
4. Delegate enforceable rules to tools — replace prose with linter commands where possible
5. Position-aware placement — beginning and end of context processed more reliably

## Recommendations for Spec

- **Scope tightly to PRD**: 3 skill extractions + 1 trivial trim + tone audit + compliance table update
- **Quality gate**: Before/after pipeline comparison on example threat models (PRD Risk 1 mitigation)
- **Skill structure**: Follow existing `.claude/skills/` pattern with SKILL.md + references/ — not the Feature 029 reference document pattern
- **No behavioral changes**: Content is identical, just relocated. Pipeline output must be byte-equivalent
- **Parallelism opportunity**: Three skill extractions are independent — can run as parallel waves
- **Tone audit scope**: All 18 tachi agents, but only the 4 over-cap agents get structural changes
- **Estimation**: Single-session delivery per PAT-012/KB-010 pattern (docs-only, no runtime code)
