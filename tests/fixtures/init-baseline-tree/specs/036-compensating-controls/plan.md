---
triad:
  pm_signoff:
    agent: product-manager
    date: 2026-03-27
    status: APPROVED
    notes: "All 20 FRs covered, all 5 P0 user stories addressable, all 9 success criteria supported, P0/P1 boundary clean, all 4 PRD personas served."
  architect_signoff:
    agent: architect
    date: 2026-03-27
    status: APPROVED_WITH_CONCERNS
    notes: "7 findings (0 High, 3 Medium, 4 Low). Medium: relatedLocations dual-purpose ambiguity, sub-batch splitting heuristic underspecified, cross-component control sharing unaddressed. All resolvable during task decomposition or build."
  techlead_signoff: null
---

# Implementation Plan: Compensating Controls Analysis

**Branch**: `036-compensating-controls` | **Date**: 2026-03-27 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/036-compensating-controls/spec.md`

## Summary

Build a `/compensating-controls` command and supporting agent that scans a target codebase against scored threats to detect existing security controls, map them to threats, recommend missing controls, calculate residual risk, and output results in dual format (markdown + SARIF 2.1.0). This is the third link in tachi's threat analysis pipeline: `/threat-model` → `/risk-score` → `/compensating-controls`.

## Technical Context

**Language/Version**: Markdown, YAML (agent definitions, command files, schemas, templates — no application code)
**Primary Dependencies**: Claude Code agent framework, existing tachi pipeline (`/threat-model`, `/risk-score`)
**Storage**: Filesystem (markdown + SARIF JSON output files)
**Testing**: Manual validation against `examples/agentic-app/` codebase with 34 scored threats
**Target Platform**: Any system running Claude Code CLI or IDE extension
**Project Type**: Knowledge system — agent definitions + command orchestration + schemas + templates
**Performance Goals**: < 3 min for 50 threats, < 10 min for 200 threats
**Constraints**: ~80K tokens per analysis pass, max 200 file reads per run, files > 5K tokens truncated
**Scale/Scope**: 8 control detection categories, 34 example threats for validation

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. General-Purpose Architecture | PASS | Command is domain-agnostic — detects controls in any codebase, not tachi-specific |
| III. Backward Compatibility | PASS | New command; no existing workflows affected |
| VI. Testing Excellence | PASS | Validation against examples/agentic-app/ planned |
| VII. Definition of Done | PASS | DoD checklist will be generated during /aod.build |
| IX. Git Workflow | PASS | Feature branch 036-compensating-controls created |
| X. Product-Spec Alignment | PASS | Spec approved by PM (APPROVED_WITH_CONCERNS) |

No violations. No complexity tracking needed.

## Components

### Component Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    /compensating-controls                        │
│                    (Command Orchestrator)                        │
│                                                                 │
│  Parses flags → Validates input → Dispatches agent → Reports   │
└──────────────┬──────────────────────────────────────────────────┘
               │ invokes
               ▼
┌─────────────────────────────────────────────────────────────────┐
│              tachi-control-analyzer                              │
│              (Analysis Agent)                                    │
│                                                                 │
│  Phase 1: Parse Input (risk-scores.md/sarif)                   │
│  Phase 2: Discover Codebase (architecture-guided or heuristic) │
│  Phase 3: Detect Controls (8 categories, per-component batch)  │
│  Phase 4: Map Controls → Threats + Classify                    │
│  Phase 5: Recommend + Calculate Residual Risk                  │
│  Phase 6: Generate Output (MD + SARIF)                         │
└─────────────┬───────────────────────────────────────────────────┘
              │ reads                              │ reads
              ▼                                    ▼
┌──────────────────────┐           ┌────────────────────────────┐
│  risk-scores.md/sarif │           │  Target Codebase           │
│  (Input: scored       │           │  (--target path)           │
│   threats from        │           │  Scanned for control       │
│   /risk-score)        │           │  patterns with file:line   │
│                       │           │  evidence                  │
└───────────────────────┘           └────────────────────────────┘
              │                                    │
              ▼                                    ▼
┌─────────────────────────────────────────────────────────────────┐
│                     Output Files                                │
│                                                                 │
│  compensating-controls.md    compensating-controls.sarif        │
│  (Human-readable report)     (SARIF 2.1.0 for GitHub)          │
│                                                                 │
│  Supersedes risk-scores.sarif in alert chain                   │
│  Fingerprints preserved for alert continuity                   │
└─────────────────────────────────────────────────────────────────┘
```

### File Inventory

| Artifact | Path | Purpose |
|----------|------|---------|
| Command | `.claude/commands/compensating-controls.md` | User-facing command orchestrator |
| Agent | `.claude/agents/tachi/control-analyzer.md` | 6-phase analysis agent |
| Schema | `schemas/compensating-controls.yaml` | Control finding IR extension |
| MD Template | `templates/compensating-controls.md` | Markdown output structure |
| SARIF Template | `templates/compensating-controls.sarif` | SARIF 2.1.0 output structure |
| Example Output | `examples/agentic-app/sample-report/compensating-controls.md` | Validation reference |
| Example SARIF | `examples/agentic-app/sample-report/compensating-controls.sarif` | Validation reference |

## Data Flow

```
risk-scores.md ──┐                    architecture.md (optional)
                 │                           │
risk-scores.sarif┤                           │
                 ▼                           ▼
         ┌──────────────┐          ┌─────────────────┐
         │ Parse Scored  │          │ Map Components  │
         │ Threats       │          │ to Directories  │
         └──────┬───────┘          └────────┬────────┘
                │                           │
                ▼                           ▼
         ┌──────────────────────────────────────────┐
         │         Group Threats by Component        │
         │  (Component-based batching for efficiency)│
         └──────────────────┬───────────────────────┘
                            │
                  ┌─────────┴─────────┐
                  ▼                   ▼
         ┌──────────────┐    ┌──────────────┐
         │ Component A   │    │ Component B   │
         │ Batch         │    │ Batch         │   ... per component
         │ - Read files  │    │ - Read files  │
         │ - Detect ctrl │    │ - Detect ctrl │
         │ - Classify    │    │ - Classify    │
         └──────┬───────┘    └──────┬───────┘
                │                   │
                └─────────┬─────────┘
                          ▼
         ┌──────────────────────────────────────────┐
         │           Merge Batch Results             │
         │  - Deduplicate across components          │
         │  - Resolve multi-control per threat       │
         │    (highest effectiveness wins)            │
         └──────────────────┬───────────────────────┘
                            │
                  ┌─────────┴─────────┐
                  ▼                   ▼
         ┌──────────────┐    ┌──────────────────────┐
         │ Recommend     │    │ Calculate Residual   │
         │ (gaps only)   │    │ Risk per Threat      │
         │ Sort by score │    │ Inherent*(1-factor)  │
         └──────┬───────┘    └──────┬───────────────┘
                │                   │
                └─────────┬─────────┘
                          ▼
         ┌──────────────────────────────────────────┐
         │         Generate Output Files             │
         │  - compensating-controls.md               │
         │  - compensating-controls.sarif             │
         │  - Preserve findingId/v1 fingerprints     │
         └──────────────────────────────────────────┘
```

## Tech Stack

| Layer | Technology | Rationale |
|-------|-----------|-----------|
| Command | Claude Code command file (`.claude/commands/`) | Follows `/risk-score` precedent |
| Agent | Claude Code agent definition (`.claude/agents/tachi/`) | Follows `risk-scorer.md` precedent |
| Schema | YAML (`.yaml`) | Follows `risk-scoring.yaml` precedent |
| Templates | Markdown + JSON | Follows `risk-scores.md` + `risk-scores.sarif` precedent |
| Output | Markdown + SARIF 2.1.0 JSON | Dual-format per pipeline convention |

## Agent Pipeline Design

The `tachi-control-analyzer` agent follows a 6-phase pipeline (modeled on `risk-scorer.md`):

### Phase 1: Parse Input
- Read `risk-scores.md` (canonical) or `risk-scores.sarif` (fallback)
- Extract per-threat: ID, category, component, description, composite_score, severity_band
- Preserve governance fields and fingerprints for output passthrough
- Validate: at least 1 scored threat exists; input format is parseable

### Phase 2: Discover Codebase
- If `architecture.md` present: extract component-to-directory mapping
- If absent: list file tree from `--target`, prioritize heuristic directories
- Build component → file list mapping
- Enforce 200-file read budget; warn if exceeded

### Phase 3: Detect Controls (per-component batch)
- For each component batch:
  - Read component's files (amortize I/O)
  - Scan for 8 control categories using pattern + semantic analysis
  - Record evidence: file path, line number, code snippet, confidence
- STRIDE-to-control-category mapping table (embedded in agent):

| STRIDE Category | Control Categories to Search |
|----------------|----------------------------|
| Spoofing | Authentication, Access Control |
| Tampering | Input Validation |
| Repudiation | Logging/Audit |
| Information Disclosure | Encryption |
| Denial of Service | Rate Limiting |
| Elevation of Privilege | Access Control |
| Agentic (AI) | All 8 (P0); AI-specific (P1) |
| LLM (AI) | Input Validation, Logging/Audit (P0); AI-specific (P1) |

### Phase 4: Map & Classify
- For each scored threat, determine control status:
  - **Control Found**: Matching control detected with evidence
  - **Partial Control**: Control exists but doesn't cover all paths/vectors
  - **No Control Found**: No matching control detected
- When multiple controls address one threat: use highest effectiveness

### Phase 5: Recommend & Calculate Residual Risk
- For "No Control Found" and "Partial Control" threats: generate recommendations
  - What to implement/harden
  - Where (file/module suggestion)
  - Reference patterns/libraries
  - Effort: Low (config) / Medium (new code) / High (architectural)
- Sort recommendations by composite_score descending
- Calculate residual risk: `Inherent * (1 - Factor)`
  - Found: 0.50, Partial: 0.25, Missing: 0.00
- Clamp residual to [0.0, 10.0], map to severity bands

### Phase 6: Generate Output
- **compensating-controls.md**: Executive Summary → Coverage Matrix → Control Details → Recommendations → Residual Risk Summary
- **compensating-controls.sarif**: SARIF 2.1.0 with `tachi-control-analyzer` tool metadata, per-result control properties, preserved fingerprints, `relatedLocations` for control evidence
- Both files written to output directory

## SARIF Supersession Chain Design

```
threats.sarif                    → security-severity: static category-level
    ↓ superseded by
risk-scores.sarif                → security-severity: per-finding composite score
    ↓ superseded by
compensating-controls.sarif      → security-severity: per-finding RESIDUAL score
```

**Fingerprint continuity**: `partialFingerprints.findingId/v1` is preserved unchanged through all three files. This ensures GitHub Code Scanning treats uploads as updates to existing alerts (not new alerts).

**Tool metadata shift**: Each file declares its own `tool.driver.name`:
- `tachi` (threat model)
- `tachi-risk-scorer` (risk scoring)
- `tachi-control-analyzer` (compensating controls)

**Property bag extension**: `compensating-controls.sarif` adds these per-result properties beyond what `risk-scores.sarif` provides:
- `control-status`: "found" / "partial" / "missing"
- `control-evidence`: `[{"file": "path", "line": N, "snippet": "code"}]`
- `control-effectiveness`: "strong" / "moderate" / "weak" / "none"
- `inherent-risk`: original composite score (passthrough from risk-scores)
- `residual-risk`: calculated residual score
- `recommendation`: remediation guidance text
- `effort-estimate`: "Low" / "Medium" / "High"

## Context Window Management Strategy

**Budget allocation per component batch**:
- ~80,000 tokens total per analysis pass
- ~20,000 tokens: agent instructions + schema + mapping table
- ~10,000 tokens: scored threats for this batch
- ~50,000 tokens: codebase file content for this component

**Batching logic** (in command layer, not agent):
1. Group threats by component
2. For each component, estimate file count from discovery
3. If component has > 50 files, split into sub-batches
4. Agent processes one batch at a time
5. Command merges results across batches

**Large file handling**:
- Files > 5,000 tokens: truncate to imports + exports + security-relevant sections
- Emit warning: "File {path} truncated to {N} tokens (original: {M} tokens)"

**Graceful degradation**:
- If batch exceeds context: split by threat count (halve until fits)
- Partial results always emitted; failures logged with warnings

## Project Structure

### Documentation (this feature)

```
specs/036-compensating-controls/
├── plan.md              # This file
├── research.md          # Research phase output (from spec phase)
├── data-model.md        # Control finding schema design
├── quickstart.md        # Usage guide
├── checklists/          # Quality checklists
└── tasks.md             # Task breakdown (/aod.tasks output)
```

### Source (repository root)

```
.claude/
├── commands/
│   └── compensating-controls.md     # NEW: Command orchestrator
└── agents/
    └── tachi/
        └── control-analyzer.md      # NEW: 6-phase analysis agent

schemas/
└── compensating-controls.yaml       # NEW: Control finding IR extension

templates/
├── compensating-controls.md         # NEW: Markdown output template
└── compensating-controls.sarif      # NEW: SARIF output template

examples/
└── agentic-app/
    └── sample-report/
        ├── compensating-controls.md     # NEW: Example output
        └── compensating-controls.sarif  # NEW: Example SARIF
```

**Structure Decision**: Knowledge system pattern — agent definitions + command orchestration + schemas + templates. No traditional source code directories. Follows the exact pattern established by `/risk-score` (Issue #35).
