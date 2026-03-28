---
triad:
  pm_signoff:
    agent: product-manager
    date: 2026-03-28
    status: APPROVED
    notes: "14/14 FRs covered, 5/5 user stories mapped, 7/7 success criteria achievable. No scope creep."
  architect_signoff:
    agent: architect
    date: 2026-03-28
    status: APPROVED_WITH_CONCERNS
    notes: "Architecture sound. Concerns addressed: (1) Section reference ambiguity clarified — Section 1 for aggregate distribution, Section 2 for per-finding detail. (2) Missing Copilot instructions adapter added to scope."
  techlead_signoff: null
---

# Implementation Plan: Standalone /infographic Command

**Branch**: `039-standalone-infographic-command` | **Date**: 2026-03-28 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `specs/039-standalone-infographic-command/spec.md`

## Summary

Extract infographic generation from Phase 6 of the `/threat-model` pipeline into a standalone `/infographic` command. The command auto-detects the richest available data source (`risk-scores.md` preferred over `threats.md`), supports explicit file path override, and generates visual risk diagrams using existing templates. The infographic agent gains dual-path data extraction to consume quantitative composite scores from `risk-scores.md` while reading structural/spatial data from co-located `threats.md`. Phase 6 is removed from the orchestrator and all platform adapters are updated to reflect a 5-phase pipeline.

## Technical Context

**Language/Version**: Markdown + YAML (agent prompts, command files, templates — no application code)
**Primary Dependencies**: Existing tachi agent framework, Gemini API (optional, image generation)
**Storage**: Filesystem — markdown specifications and JPEG images written to output directory
**Testing**: Manual verification against example threat model outputs in `examples/`
**Target Platform**: Any LLM agent platform (Claude Code, Copilot, Cursor, generic prompts)
**Project Type**: Knowledge system — methodology and governance template
**Performance Goals**: Spec generation < 30 seconds; Gemini image generation < 60 seconds timeout
**Constraints**: Fresh context isolation per ADR-010; spec-first per ADR-014; graceful degradation on API failure
**Scale/Scope**: 1 new command file, 1 agent enhancement, 1 orchestrator cleanup, ~10 adapter updates

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. General-Purpose Architecture | PASS | Command is domain-agnostic (works with any threat model output) |
| II. API-First Design | N/A | No API endpoints — agent command interface only |
| III. Backward Compatibility | PASS | Existing `threats.md` input path preserved; `risk-scores.md` is additive |
| IV. Concurrency & Data Integrity | N/A | No shared state — file-based I/O only |
| V. Privacy & Data Isolation | N/A | No multi-tenant concerns |
| VI. Testing Excellence | PASS | Verified against example outputs in `examples/` |
| VII. Definition of Done | PASS | 3-step validation applies |
| VIII. Observability | PASS | Error handling follows ADR-006 non-fatal pattern |
| IX. Git Workflow | PASS | Feature branch `039-standalone-infographic-command` |
| X. Product-Spec Alignment | PASS | PM sign-off on spec.md obtained |
| XI. SDLC Triad Collaboration | PASS | Dual sign-off on this plan required |

## Project Structure

### Documentation (this feature)

```
specs/039-standalone-infographic-command/
├── plan.md              # This file
├── research.md          # Research phase output (from spec phase)
├── data-model.md        # Data flow contract
├── quickstart.md        # Usage guide
├── contracts/           # Command interface contracts
│   └── infographic-command.md
└── tasks.md             # Task breakdown (/aod.tasks output)
```

### Source Code (repository root)

```
.claude/
├── commands/
│   ├── threat-model.md          # MODIFY: Remove Phase 6, flags, add hint
│   └── infographic.md           # CREATE: New standalone command
├── agents/tachi/
│   ├── threat-infographic.md    # MODIFY: Add dual-path data extraction
│   └── orchestrator.md          # MODIFY: Remove Phase 6 dispatch

adapters/
├── claude-code/
│   ├── commands/
│   │   ├── threat-model.md      # MODIFY: Mirror .claude/commands changes
│   │   └── infographic.md       # CREATE: Adapter copy
│   └── agents/
│       ├── orchestrator.md      # MODIFY: Remove Phase 6
│       └── threat-infographic.md # MODIFY: Mirror agent changes
├── copilot/agents/
│   ├── orchestrator.agent.md    # MODIFY: Remove Phase 6
│   └── threat-infographic.agent.md # MODIFY: Mirror agent changes
├── cursor/rules/
│   ├── orchestrator.mdc         # MODIFY: Remove Phase 6
│   └── threat-infographic.mdc   # MODIFY: Mirror agent changes
└── generic/prompts/
    ├── 00-orchestrator.md       # MODIFY: Remove Phase 6
    └── 13-threat-infographic.md # MODIFY: Mirror agent changes

schemas/
└── infographic.yaml             # NO CHANGE (output schema unchanged)
```

**Structure Decision**: No new directories created. The `/infographic` command follows the existing command file pattern at `.claude/commands/`. Agent enhancement is in-place modification of the existing `threat-infographic.md` agent.

## Components

### Component 1: `/infographic` Command (NEW)

**File**: `.claude/commands/infographic.md`
**Pattern**: Follows `/risk-score` command structure (Step 0 → Step 1 → Step 2 → Step 3)

**Command Interface**:
```
/infographic [path/to/data-source] [--template {baseball-card|system-architecture|all}] [--output-dir <path>]
```

**Steps**:
- **Step 0: Parse Flags** — Extract `--template` (default: `all`), `--output-dir` (default: input file directory), remaining args as explicit data source path. Resolve `corporate-white` alias to `baseball-card`.
- **Step 1: Validate Prerequisites** — Check infographic agent exists. Detect data source: if explicit path provided, use it; otherwise scan for `risk-scores.md` first, then `threats.md`. Validate file exists. If `risk-scores.md` is primary, verify co-located `threats.md` exists.
- **Step 2: Run Infographic Agent** — Read data source file(s). Invoke `tachi-threat-infographic` agent in fresh context with data source content, template name, and data source type indicator. Agent writes spec + optional image.
- **Step 3: Report Results** — Display summary: data source used, templates generated, output files, image generation status.

### Component 2: Infographic Agent Enhancement (MODIFY)

**File**: `.claude/agents/tachi/threat-infographic.md`
**Change**: Add dual-path data extraction section

**New Capability**: When the data source is `risk-scores.md`:
1. Parse Section 1 (Executive Summary) for aggregate severity distribution counts; parse Section 2 (Scored Threat Table) for per-finding quantitative composite scores and severity bands
2. Use Section 1 aggregate distribution for risk distribution chart; use Section 2 per-finding composite scores for component heat map and top findings ranking
3. Read co-located `threats.md` for structural data:
   - Section 1 (System Overview): project metadata, component list, agent count
   - Section 2 (Trust Boundaries): trust zones, component-to-zone mapping, data flows
4. Merge: quantitative scores from `risk-scores.md` + structural skeleton from `threats.md`

**Data Source Detection**: Detect file type from content structure:
- Contains `## 2. Scored Threat Table` with `Composite` column → `risk-scores.md`
- Contains `## 6. Risk Summary` with severity counts → `threats.md`

**Existing threats.md path**: Unchanged (5-step extraction methodology preserved)

### Component 3: /threat-model Pipeline Cleanup (MODIFY)

**File**: `.claude/commands/threat-model.md`
**Changes**:
- Remove `--infographic-template` flag from Step 0 parsing
- Remove `--skip-infographic` flag references
- Remove `TACHI_SKIP_INFOGRAPHIC` env var references
- Remove Phase 6 output files from output listing
- Update Step 2 orchestrator invocation to request 5 phases only
- Update Step 3 report to list 5-phase output only
- Remove infographic-related quality checklist items
- Add post-pipeline hint: "Run `/infographic` to generate visual risk diagrams"

### Component 4: Orchestrator Phase 6 Removal (MODIFY)

**File**: `.claude/agents/tachi/orchestrator.md`
**Changes**:
- Remove Phase 6 dispatch section (~lines 1785-1862)
- Remove Phase 6 from phase summary/enumeration
- Remove Phase 6 validation checklist items
- Remove Phase 6 skip condition documentation
- Update pipeline phase count from 6 to 5 throughout

### Component 5: Platform Adapter Updates (MODIFY)

**Files**: All adapter variants of orchestrator, threat-model command, and threat-infographic agent

| Adapter | Orchestrator | Command | Agent |
|---------|-------------|---------|-------|
| Claude Code | `adapters/claude-code/agents/orchestrator.md` | `adapters/claude-code/commands/threat-model.md` | `adapters/claude-code/agents/threat-infographic.md` |
| Copilot | `adapters/copilot/agents/orchestrator.agent.md` + `adapters/copilot/instructions/tachi-orchestrator-context.instructions.md` | — | `adapters/copilot/agents/threat-infographic.agent.md` |
| Cursor | `adapters/cursor/rules/orchestrator.mdc` | — | `adapters/cursor/rules/threat-infographic.mdc` |
| Generic | `adapters/generic/prompts/00-orchestrator.md` | — | `adapters/generic/prompts/13-threat-infographic.md` |

**New adapter files to create**:
- `adapters/claude-code/commands/infographic.md` — Claude Code adapter of the new command

**Changes per adapter**:
- Orchestrator: Remove Phase 6 dispatch, update phase count to 5
- threat-model command: Remove infographic flags and Phase 6 output references
- Infographic agent: Add dual-path data extraction (risk-scores.md support)

## Data Flow

```
User invokes /infographic
        │
        ▼
   ┌─────────────────┐
   │  Parse flags     │  --template, --output-dir, explicit path
   └────────┬────────┘
            │
            ▼
   ┌─────────────────────────┐
   │  Detect data source      │
   │  risk-scores.md > threats.md │
   └────────┬────────────────┘
            │
     ┌──────┴──────┐
     │             │
     ▼             ▼
  threats.md    risk-scores.md
  (sole input)  (primary) + threats.md (structural)
     │             │
     └──────┬──────┘
            │
            ▼
   ┌─────────────────────────┐
   │  Infographic Agent       │
   │  (fresh context)         │
   │  - Extract data          │
   │  - Apply template        │
   │  - Generate spec         │
   │  - Attempt Gemini image  │
   └────────┬────────────────┘
            │
            ▼
   ┌─────────────────────────┐
   │  Output files            │
   │  - threat-{name}-spec.md │
   │  - threat-{name}.jpg     │
   │    (optional)            │
   └─────────────────────────┘
```

## Tech Stack

| Layer | Technology | Rationale |
|-------|-----------|-----------|
| Command | Markdown command file | Follows existing tachi command pattern |
| Agent | Markdown agent prompt | Extends existing `threat-infographic.md` |
| Templates | Markdown template files | No changes — existing templates reused |
| Image Generation | Gemini API (optional) | Existing integration preserved |
| Schema | YAML | Existing `schemas/infographic.yaml` unchanged |
| Output | Markdown spec + JPEG image | Existing format preserved |

## Complexity Tracking

No constitution violations. All changes follow established patterns (command files, agent prompts, adapter sync).

## Risk Mitigation

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Dual-path extraction introduces data inconsistency | Medium | High | Validate risk distribution counts match source file exactly (zero discrepancy rule) |
| Removing Phase 6 breaks existing workflows | Medium | Low | Post-pipeline hint directs users to `/infographic`; same output achievable |
| Adapter sync drift | Low | Medium | Systematic update of all 4 adapter platforms in single task wave |
| `risk-scores.md` without co-located `threats.md` | Medium | Medium | Explicit error message explaining requirement |
