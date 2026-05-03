---
triad:
  pm_signoff:
    agent: product-manager
    date: 2026-04-01
    status: APPROVED_WITH_CONCERNS
    notes: "2 non-blocking: (1) document shared reference validation strategy in best practices update, (2) clarify Phase 3b ordering — prototype uses existing skill refs, shared refs created later. All 13 FRs covered, all 5 user stories traceable, scope aligned."
  architect_signoff:
    agent: architect
    date: 2026-04-01
    status: APPROVED_WITH_CONCERNS
    notes: "7 non-blocking findings: accept 510-520 tolerance for orchestrator, add SKILL.md to tachi-shared, clarify YAML data format (enhanced .md), reconcile consumer expectations for shared refs, add correlation group count to regression criteria, annotate agent-autonomy 210-line exception, fix file count discrepancy. Architecture sound, skill pattern endorsed, prototype-first gate endorsed."
  techlead_signoff: null
---

# Implementation Plan: Agent Context Optimization

**Branch**: `078-agent-context-optimization` | **Date**: 2026-04-01 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `specs/078-agent-context-optimization/spec.md`

## Summary

Restructure 6 oversized tachi agent definitions (3 methodology + 3 report) to enforce tighter tier caps (Methodology: 500, Report: 300, Leaf: 200 lines), add `model:` frontmatter to all 17 agents, and update the best practices document. All domain knowledge extracted from agents relocates to skill reference files, deterministic YAML data files, output templates, and shared references. Risk-scorer is restructured first as a prototype to validate the deterministic YAML pattern before committing to remaining agents.

## Technical Context

**Language/Version**: Markdown + YAML (agent definitions, skill references, data files). No runtime code.
**Primary Dependencies**: Claude Code agent/skill system, Read tool for on-demand loading, existing tachi-orchestration/tachi-risk-scoring/tachi-control-analysis skills
**Storage**: File-based (`.claude/agents/tachi/`, `.claude/skills/tachi-*/references/`)
**Testing**: Structural regression — pipeline output comparison on `examples/agentic-app/architecture.md` (finding count, severity distribution, SARIF count, section presence)
**Target Platform**: Claude Code CLI / Claude Agent SDK
**Project Type**: Content restructuring (markdown/YAML files, no compiled code)
**Performance Goals**: No increase in total token cost per pipeline run; lazy loading net-neutral or net-positive
**Constraints**: Zero quality regression, relocation not deletion, no interface changes, prototype-first gate on risk-scorer
**Scale/Scope**: 17 agent files (6 restructured, 11 leaf + model field only), ~15 new reference files, 3 new skill directories, 6 existing reference enhancements

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. General-Purpose Architecture | PASS | Agent restructuring is internal — no domain-specific logic in core |
| III. Backward Compatibility | PASS | Zero interface changes; all pipeline outputs identical |
| VI. Testing Excellence | PASS | Structural regression testing on example architectures |
| VII. Definition of Done | PASS | DoD checklist in spec: line counts, model fields, regression, docs |
| IX. Git Workflow | PASS | Feature branch `078-agent-context-optimization` created |
| X. Product-Spec Alignment | PASS | Spec approved by PM (APPROVED_WITH_CONCERNS) |
| XI. SDLC Triad Collaboration | PASS | Full Triad workflow active |

No constitution violations. No complexity tracking entries needed.

## Project Structure

### Documentation (this feature)

```
specs/078-agent-context-optimization/
├── plan.md              # This file
├── research.md          # Spec-phase research (completed)
├── data-model.md        # Content extraction map
├── quickstart.md        # Working with restructured agents
├── checklists/
│   └── requirements.md  # Spec quality checklist
└── tasks.md             # Task breakdown (pending)
```

### Source Structure (repository — files affected)

```
.claude/agents/tachi/
├── orchestrator.md              # Restructure: 1,286 → ≤500 lines
├── risk-scorer.md               # Restructure: 1,093 → ≤500 lines (PROTOTYPE)
├── control-analyzer.md          # Restructure: 973 → ≤500 lines
├── report-assembler.md          # Restructure: 654 → ≤300 lines
├── threat-report.md             # Restructure: 800 → ≤300 lines
├── threat-infographic.md        # Restructure: 775 → ≤300 lines
├── [11 leaf agents]             # model: field addition only
└── _TACHI_AGENT_BEST_PRACTICES.md  # Update caps, compliance, research

.claude/skills/
├── tachi-orchestration/
│   ├── SKILL.md                 # Update navigation table
│   └── references/
│       ├── dispatch-rules.md         # Existing (244 lines)
│       ├── output-schemas.md         # Existing (506 lines)
│       ├── sarif-specification.md    # Existing (536 lines) — enhance
│       ├── baseline-correlation.md   # Existing (137 lines)
│       ├── format-detection.md       # NEW — input format recognition
│       ├── dfd-classification.md     # NEW — DFD element signals
│       ├── trust-boundaries.md       # NEW — boundary notation per format
│       ├── coverage-requirements.md  # NEW — category requirements per type
│       └── coverage-matrix-model.md  # NEW — cell model and footnotes
│
├── tachi-risk-scoring/
│   ├── SKILL.md                 # Update navigation table
│   └── references/
│       ├── cvss-vectors.md           # Existing (74 lines) — enhance
│       ├── scoring-dimensions.md     # Existing (256 lines)
│       ├── severity-bands.md         # Existing (195 lines) — enhance
│       ├── trust-zones.md            # NEW — zone extraction rules
│       ├── reachability-analysis.md  # NEW — zone baselines and adjustments
│       └── output-formatting.md      # NEW — table specs and formatting
│
├── tachi-control-analysis/
│   ├── SKILL.md                 # Verify navigation table
│   └── references/
│       ├── control-categories.md     # Existing (249 lines) — verify
│       ├── evidence-criteria.md      # Existing (117 lines) — verify
│       └── residual-risk.md          # Existing (171 lines) — verify
│
├── tachi-report-assembly/       # NEW SKILL
│   ├── SKILL.md                 # Navigation table
│   └── references/
│       ├── typst-artifacts.md        # Artifact detection table
│       ├── typst-template-contract.md # Typst variable bindings
│       └── brand-asset-guidelines.md  # Brand asset handling
│
├── tachi-threat-reporting/      # NEW SKILL
│   ├── SKILL.md                 # Navigation table
│   └── references/
│       ├── narrative-templates.md    # Exec summary, architecture, threats
│       ├── attack-tree-construction.md # Mermaid conventions, validation
│       └── attack-tree-examples.md   # Reference patterns
│
└── tachi-infographics/          # NEW SKILL
    ├── SKILL.md                 # Navigation table
    └── references/
        ├── infographic-specifications.md   # Section formats
        ├── template-specific-formats.md    # Baseball/Architecture/Funnel
        ├── gemini-prompt-construction.md   # Prompt hygiene, placeholders
        └── visual-design-system.md         # Colors, typography, layout

.claude/skills/tachi-shared/     # NEW — shared references
└── references/
    ├── severity-bands-shared.md      # Shared severity definitions
    ├── stride-categories-shared.md   # Shared STRIDE descriptions
    └── finding-format-shared.md      # Shared finding format spec
```

**Structure Decision**: Content restructuring project — no traditional src/ directory. All deliverables are markdown and YAML files in `.claude/agents/tachi/` and `.claude/skills/tachi-*/`. Three new skill directories created for report agents. One shared reference directory for deduplicated content.

## Components

### Agent Definitions (6 files restructured)
Files in `.claude/agents/tachi/` containing orchestration logic only. Each agent retains: role identity (2-3 lines), workflow skeleton (phases, decision points), skill loading instructions (navigation table + MANDATORY Read at branch points), output format summary, constraints and error handling.

### Skill Reference Files (15 new + 6 enhanced)
Domain knowledge files in `.claude/skills/tachi-*/references/` loaded on-demand via Read tool. Categories: detection patterns, scoring schemas, output templates, format specifications, construction rules, visual design tokens.

### Deterministic Data Files
YAML files containing static lookup tables processed mechanically by agents. Candidates: CVSS base vector mappings (in `cvss-vectors.md`), severity band thresholds (in `severity-bands.md`), STRIDE dispatch mappings (in `dispatch-rules.md`). Follow existing schema conventions from `schemas/` directory.

### Shared References (3 new files)
Content used by multiple agents stored once in `tachi-shared/references/`. Consumers: orchestrator + risk-scorer + control-analyzer (severity bands), all STRIDE agents + orchestrator (STRIDE categories), all threat agents (finding format).

## Data Flow

```
Architecture Description
        │
        ▼
┌──────────────────────────────┐
│  Orchestrator Agent          │ ── Read ──▶ tachi-orchestration/references/
│  (≤500 lines orchestration)  │            (dispatch-rules, format-detection,
│                              │             coverage-requirements, etc.)
│                              │ ── Read ──▶ tachi-shared/references/
│                              │            (severity-bands, stride-categories)
└──────────┬───────────────────┘
           │ dispatches
           ▼
┌──────────────────────────────┐
│  11 Leaf Agents              │  (unchanged behavior, model: field added)
│  (≤200 lines each)          │
└──────────┬───────────────────┘
           │ findings
           ▼
┌──────────────────────────────┐
│  Risk-Scorer Agent           │ ── Read ──▶ tachi-risk-scoring/references/
│  (≤500 lines orchestration)  │            (cvss-vectors, trust-zones,
│                              │             reachability, severity-bands)
└──────────┬───────────────────┘
           │ scored findings
           ▼
┌──────────────────────────────┐
│  Control-Analyzer Agent      │ ── Read ──▶ tachi-control-analysis/references/
│  (≤500 lines orchestration)  │            (categories, evidence, residual-risk)
└──────────┬───────────────────┘
           │ controls + residual risk
           ▼
┌──────────────────────────────┐
│  Report Agents (3)           │ ── Read ──▶ tachi-report-assembly/references/
│  (≤300 lines each)          │ ── Read ──▶ tachi-threat-reporting/references/
│                              │ ── Read ──▶ tachi-infographics/references/
└──────────────────────────────┘
```

## Tech Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Agent definitions | Markdown + YAML frontmatter | Orchestration logic, workflow skeletons |
| Skill references | Markdown | Domain knowledge, templates, patterns |
| Data files | YAML | Static lookup tables (CVSS, severity, dispatch) |
| Shared references | Markdown | Deduplicated cross-agent content |
| Regression testing | Pipeline output comparison | Structural equivalence verification |

## Phase 0: Research Findings

Research was completed during spec generation (see [research.md](research.md)). Key decisions:

| Decision | Rationale | Alternatives Considered |
|----------|-----------|------------------------|
| Risk-scorer as prototype | Most structured extractable content (CVSS tables, severity bands); validates YAML data pattern | Orchestrator (too complex for first extraction); control-analyzer (already mostly extracted) |
| YAML for deterministic data | 9 existing YAML schemas in `schemas/`; project convention | JSON (viable but inconsistent with project); Markdown tables (current, but not mechanically parseable) |
| Lazy loading via Read tool | Validated by Feature 075; 78% context reduction per ADR-002 | Eager via `skills:` frontmatter (defeats optimization purpose) |
| `sonnet` for all agents | Architect recommendation; simplest to maintain; escalate to `opus` only on regression | Per-tier model assignment (premature optimization) |
| Shared references for severity bands | Used by 6+ agents; single-source-of-truth eliminates update-in-multiple-places burden | Duplicated in each skill (current state; maintenance risk) |
| agent-autonomy at 200 lines | Accept ~210 after `model:` addition as leaf exception; extracting 10 lines adds complexity without meaningful benefit | Extract content to reduce below 200 (over-engineering for 10 lines) |

## Phase 1: Design

### Content Extraction Map

Detailed extraction plan per agent (from content analysis):

**Methodology Agents → ≤500 lines:**

| Agent | Current | Orchestration (stays) | Domain (moves) | Target | New References | Enhanced References |
|-------|---------|----------------------|----------------|--------|---------------|-------------------|
| orchestrator | 1,286 | ~450 | ~500 | ≤500 | 5 new files | sarif-specification.md |
| risk-scorer | 1,093 | ~320 | ~480 | ≤500 | 3 new files | cvss-vectors.md, severity-bands.md |
| control-analyzer | 973 | ~460 | ~170 | ≤500 | 0 (verify existing) | control-categories.md, evidence-criteria.md, residual-risk.md |

**Report Agents → ≤300 lines:**

| Agent | Current | Orchestration (stays) | Domain (moves) | Target | New Skill |
|-------|---------|----------------------|----------------|--------|-----------|
| report-assembler | 654 | ~250 | ~200 | ≤300 | tachi-report-assembly (3 refs) |
| threat-report | 800 | ~280 | ~500 | ≤300 | tachi-threat-reporting (3 refs) |
| threat-infographic | 775 | ~280 | ~460 | ≤300 | tachi-infographics (4 refs) |

### Shared Reference Deduplication

| Shared Content | Current Locations | Shared File | Consumers |
|----------------|-------------------|-------------|-----------|
| Severity band definitions | orchestrator, risk-scorer, control-analyzer, threat-report, threat-infographic, report-assembler | `tachi-shared/severity-bands-shared.md` | All 6 restructured agents |
| STRIDE category descriptions | orchestrator, dispatch-rules.md | `tachi-shared/stride-categories-shared.md` | orchestrator + 11 leaf agents |
| Finding format specification | All threat agents (implicit) | `tachi-shared/finding-format-shared.md` | orchestrator + leaf agents + risk-scorer |

### Agent Restructuring Pattern

Each restructured agent follows this internal structure:
1. **YAML frontmatter** — name, description, tools, model, metadata
2. **Role identity** — 2-3 lines defining the agent's purpose
3. **Skill reference table** — navigation table mapping phases to reference files with load-when conditions
4. **Workflow skeleton** — numbered phases with decision points, referencing skill files at each branch
5. **Output format summary** — structure overview (not full template)
6. **Constraints** — error handling, validation rules, what not to do

### Prototype Validation Gate

The risk-scorer is restructured first (Phase 2a). Validation criteria before proceeding:
1. `wc -l risk-scorer.md` ≤ 500
2. All extracted content exists in skill reference files
3. Pipeline run on `examples/agentic-app/architecture.md` produces structurally equivalent risk-scores.md and risk-scores.sarif
4. Deterministic YAML data tables (CVSS vectors, severity bands) are correctly processed

If prototype fails: diagnose, adjust extraction approach, retry. Only proceed to remaining agents after prototype passes.

### Phasing Strategy

| Phase | What | Agents | Dependencies | Estimated Effort |
|-------|------|--------|-------------|-----------------|
| 1 | Best practices + model fields | All 17 | None | 2-3 hours |
| 2a | Risk-scorer prototype | risk-scorer | Phase 1 | 3-4 hours |
| 2b (gate) | Prototype validation | — | Phase 2a | 1-2 hours |
| 2c | Remaining methodology agents | orchestrator, control-analyzer | Phase 2b pass | 4-6 hours |
| 3a | Report agent skills | report-assembler, threat-report, threat-infographic | Phase 2c | 5-8 hours |
| 3b | Shared references | tachi-shared/ | Phases 2c + 3a | 2-3 hours |
| 4 | Final validation + regression | All | All phases | 2-3 hours |

**Total estimated: 19-29 hours** (midpoint: 24 hours, within PRD range of 21-33)

### Parallel Execution Opportunities

- Phase 1: Model field addition to all 17 agents can run in parallel (independent files)
- Phase 2c: Orchestrator and control-analyzer can be restructured in parallel (independent skills)
- Phase 3a: All 3 report agents can be restructured in parallel (independent new skills)
- Phase 3b: Shared references can start once any 2 consuming agents are restructured

### Risk Mitigations

| Risk | Mitigation |
|------|-----------|
| Quality regression from extraction | Per-agent regression test; prototype-first gate on risk-scorer |
| Deterministic YAML unreliable | Fall back to markdown skill references (proven pattern) |
| Agent still over cap after extraction | Identify additional inline content for extraction; tighten orchestration prose |
| Shared references create coupling | Shared refs are read-only lookup tables; changes validated against all consumers |
| Report agent extraction harder than methodology | Methodology agents have structured data; report templates may need more careful extraction |

## Post-Design Constitution Re-Check

| Principle | Status | Notes |
|-----------|--------|-------|
| III. Backward Compatibility | PASS | No interface changes; all outputs identical |
| VI. Testing Excellence | PASS | Regression testing at prototype gate and final validation |
| VII. Definition of Done | PASS | Line count verification, model field inspection, regression test |

No new violations introduced by the design.
