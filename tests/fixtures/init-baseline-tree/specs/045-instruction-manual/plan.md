---
triad:
  pm_signoff:
    agent: product-manager
    date: 2026-03-28
    status: APPROVED
    notes: "All 15 FRs addressed across 4 phases. Phase sequencing correct (spec-first). Quick Start approach sound. No scope creep. 3 non-blocking observations noted."
  architect_signoff:
    agent: architect
    date: 2026-03-28
    status: APPROVED_WITH_CONCERNS
    notes: "Technical details accurate against command specs. Data flow correct. 3 findings: (M) compensating-controls command path should verify both .claude/commands/ and adapters/ locations; (L) plan could note git mv preserves history; (L) Appendix B validation should cross-check actual output samples."
  techlead_signoff: null
---

# Implementation Plan: 045 — End-to-End tachi Instruction Manual

**Branch**: `045-instruction-manual` | **Date**: 2026-03-28 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `specs/045-instruction-manual/spec.md`

## Summary

Update the existing prompt specification and developer guide to cover the full 4-command tachi pipeline (`/threat-model` → `/risk-score` → `/compensating-controls` → `/infographic`). This is a documentation-only deliverable: no code, no agents, no commands are modified. The approach is targeted insertion of missing sections into existing documents, not full regeneration.

## Technical Context

**Language/Version**: Markdown (documentation-only feature)
**Primary Dependencies**: None (no runtime dependencies)
**Storage**: Local filesystem — markdown files in `docs/guides/`
**Testing**: Manual walkthrough validation (Quick Start and full pipeline)
**Target Platform**: Any markdown renderer (GitHub, VS Code, terminal)
**Project Type**: Documentation update
**Performance Goals**: Quick Start completable in under 5 minutes
**Constraints**: No code changes, single markdown file for guide, prompt spec is source of truth
**Scale/Scope**: ~1,000-1,400 lines of new content across 2 primary files

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. General-Purpose Architecture | PASS | Documentation only — no architecture changes |
| II. API-First Design | N/A | No API changes |
| III. Backward Compatibility | PASS | No functional changes — only documentation |
| IV. Concurrency & Data Integrity | N/A | No state changes |
| V. Privacy & Data Isolation | PASS | No PII in documentation content |
| VI. Testing Excellence | PASS | Manual walkthrough validation per DoD exception for docs-only |
| VII. Definition of Done | PASS | Docs-only exception applies: no production deployment required; user validation required |
| VIII. Observability | N/A | No system changes |
| IX. Git Workflow | PASS | Feature branch `045-instruction-manual` created |
| X. Product-Spec Alignment | PASS | Spec has PM sign-off (APPROVED) |
| XI. SDLC Triad Collaboration | PASS | Full Triad governance in progress |

**Gate result**: PASS — no violations.

## Project Structure

### Documentation (this feature)

```
specs/045-instruction-manual/
├── plan.md              # This file
├── research.md          # Research phase output (completed during /aod.spec)
├── checklists/
│   └── requirements.md  # Quality checklist
├── pm-review.md         # PM review of spec
└── tasks.md             # Task breakdown (/aod.tasks output)
```

### Files Modified (repository)

```
docs/guides/
├── prompts/
│   ├── GUIDE_PROMPT.md                    # DELETED (renamed)
│   └── developer-guide-prompt.md          # CREATED (renamed from GUIDE_PROMPT.md)
└── DEVELOPER_GUIDE_TACHI.md               # UPDATED (new sections added)
```

**No source code directories are affected.** This feature modifies only documentation files.

## Components

### Component 1: Prompt Specification (Source of Truth)

**File**: `docs/guides/prompts/GUIDE_PROMPT.md` → `docs/guides/prompts/developer-guide-prompt.md`

**Current state**: 633 lines covering `/threat-model` comprehensively. Missing 3 command sections and pipeline workflow.

**Changes required**:

1. **Add `/risk-score` section** (after Output Artifacts, ~80-100 lines):
   - Invocation: `/risk-score [input_dir] [--output-dir path]`
   - Input: `threats.md` (primary), `threats.sarif` (fallback), optional `architecture.md`
   - Output: `risk-scores.md`, `risk-scores.sarif`
   - Scoring dimensions: CVSS, exploitability, scalability, reachability
   - Composite score: weighted formula combining all 4 dimensions
   - Governance fields: owner, SLA, disposition, review date

2. **Add `/compensating-controls` section** (~80-100 lines):
   - Invocation: `/compensating-controls [input_dir] [--target path] [--output-dir path]`
   - Input: `risk-scores.md` (primary), `risk-scores.sarif` (fallback), optional `architecture.md`
   - Output: `compensating-controls.md`, `compensating-controls.sarif`
   - Control classification: Control Found / Partial Control / No Control Found
   - Residual risk: Inherent Score x (1 - Mitigation Factor)
   - Evidence: file:line references for all detected controls

3. **Add standalone `/infographic` section** (~60-80 lines):
   - Invocation: `/infographic [data_source] [--template value] [--output-dir path]`
   - Templates: `baseball-card`, `system-architecture`, `all` (default)
   - Legacy alias: `corporate-white` → `baseball-card`
   - Auto-detection: prefers `risk-scores.md` over `threats.md`
   - Co-located dependency: requires `threats.md` in same directory as risk-scores.md
   - Output: `threat-{template}-spec.md` + `threat-{template}.jpg` (Gemini-dependent)

4. **Add post-pipeline enrichment workflow section** (~40-60 lines):
   - Data flow diagram showing all 4 commands
   - Input/output dependency chain
   - When each enrichment command is optional vs. recommended

5. **Factual corrections**:
   - Agent count: 14 → 15 (risk-scorer agent added in Feature 035)
   - Template names: `infographic-corporate-white.md` → `infographic-baseball-card.md`, `infographic-system-architecture.md`

6. **Extend OpenClaw worked example** (~40-60 lines):
   - Add `/risk-score` step with sample output
   - Add `/compensating-controls` step with sample residual risk
   - Add `/infographic` step with template selection

7. **Rename**: `GUIDE_PROMPT.md` → `developer-guide-prompt.md` via `git mv`

**Estimated additions**: ~300-400 lines → total ~930-1,030 lines

### Component 2: Developer Guide (Published Artifact)

**File**: `docs/guides/DEVELOPER_GUIDE_TACHI.md`

**Current state**: 1,366 lines. Complete for `/threat-model`. Missing 3 command sections.

**Changes required**:

1. **Quick Start enhancement** (update existing Part 1):
   - After Step 6 (review results), add a "What's Next" callout mentioning the 3 enrichment commands
   - Keep Quick Start focused on `/threat-model` for the 5-minute target
   - Add cross-references to new pipeline sections

2. **New Section: Post-Pipeline Enrichment Workflow** (insert after Section 7, ~100-120 lines):
   - Pipeline overview diagram (ASCII/Mermaid)
   - Data dependencies between all 4 commands
   - When each command is optional vs. recommended
   - Time estimates per command

3. **New Section: Running `/risk-score`** (~200-250 lines):
   - Prerequisites (threats.md must exist)
   - Invocation (copy-pasteable, minimal + flagged)
   - Output artifacts (risk-scores.md, risk-scores.sarif)
   - Interpretation: 4 scoring dimensions explained (what it measures, range, high/low meaning)
   - Composite score explanation
   - Governance fields overview
   - Next step: run `/compensating-controls`

4. **New Section: Running `/compensating-controls`** (~180-220 lines):
   - Prerequisites (risk-scores.md must exist)
   - Invocation (copy-pasteable, minimal + flagged + with --target)
   - Output artifacts (compensating-controls.md, compensating-controls.sarif)
   - Interpretation: coverage matrix, control classification, evidence, residual risk
   - Recommendations section explanation
   - Next step: run `/infographic`

5. **New Section: Running `/infographic` Standalone** (~150-180 lines):
   - Prerequisites (threats.md or risk-scores.md must exist)
   - Auto-detection behavior (prefers richest data source)
   - Invocation (copy-pasteable, with --template variants)
   - Template descriptions (baseball-card vs. system-architecture)
   - Gemini API key requirement and fallback behavior
   - Output artifacts (spec files + .jpg images)

6. **OpenClaw worked example extension** (insert after existing example, ~100-120 lines):
   - Step 11: Run `/risk-score` on OpenClaw threats → sample output
   - Step 12: Run `/compensating-controls` → sample residual risk
   - Step 13: Run `/infographic` → template selection and output

7. **Appendix B expansion** (~80-100 lines):
   - `risk-scores.md` structure (sections, fields)
   - `risk-scores.sarif` schema additions
   - `compensating-controls.md` structure (4 sections)
   - `compensating-controls.sarif` schema additions

8. **Appendix C glossary additions** (~10-15 lines):
   - Composite Score, Compensating Control, Residual Risk, Exploitability, Scalability, Reachability

**Estimated additions**: ~820-1,005 lines → total ~2,186-2,371 lines

## Data Flow

```
/threat-model (INPUT: architecture.md)
    │
    ├── threats.md
    ├── threats.sarif
    ├── threat-report.md
    └── attack-trees/
    │
    ▼
/risk-score (INPUT: threats.md)
    │
    ├── risk-scores.md
    └── risk-scores.sarif
    │
    ▼
/compensating-controls (INPUT: risk-scores.md, --target codebase)
    │
    ├── compensating-controls.md
    └── compensating-controls.sarif
    │
    ▼
/infographic (INPUT: auto-detect — prefers risk-scores.md, falls back to threats.md)
    │
    ├── threat-{template}-spec.md
    └── threat-{template}.jpg (if GEMINI_API_KEY set)
```

## Implementation Phases

### Phase 1: Prompt Specification Update (FR-001 through FR-005)

**Sequence**: Must complete before Phase 2 (spec is source of truth).

1. Read existing `GUIDE_PROMPT.md` and identify insertion points
2. Add `/risk-score` command section after Output Artifacts
3. Add `/compensating-controls` command section
4. Add standalone `/infographic` command section
5. Add post-pipeline enrichment workflow section
6. Correct agent count (14 → 15) and template names
7. Extend OpenClaw worked example with post-pipeline steps
8. Update Output Artifacts section to include all 12+ artifacts

### Phase 2: Prompt Specification Rename (FR-006)

1. `git mv docs/guides/prompts/GUIDE_PROMPT.md docs/guides/prompts/developer-guide-prompt.md`
2. Verify no other files reference the old path (search codebase)

### Phase 3: Developer Guide Update (FR-007 through FR-015)

**Sequence**: After Phase 1+2 complete (guide draws from updated spec).

1. Read existing `DEVELOPER_GUIDE_TACHI.md` to identify precise insertion points
2. Add Quick Start "What's Next" callout after Step 6
3. Insert post-pipeline enrichment workflow section (with data flow diagram)
4. Insert `/risk-score` section (Prerequisites → Invocation → Outputs → Interpretation → Next Step)
5. Insert `/compensating-controls` section (same template)
6. Insert standalone `/infographic` section (same template)
7. Extend OpenClaw worked example (Steps 11-13)
8. Expand Appendix B with post-pipeline output structures
9. Add glossary terms to Appendix C

### Phase 4: Validation

1. Verify all internal file path references resolve
2. Verify all command invocations match actual command specs
3. Verify Quick Start flow is completable
4. Verify OpenClaw example is consistent across all 4 command steps
5. Verify Appendix B structures match actual output formats
6. Verify README.md link to guide resolves

## Per-Command Section Template

Each new command section in the developer guide follows this consistent structure:

```markdown
## Section N: Running /command-name

### What It Does
[One-sentence purpose]

### Prerequisites
[Required input files and their source commands]

### Running the Command
[Copy-pasteable code blocks: minimal + with flags]

### Understanding the Output
[Annotated explanation of each output file section]

### Scoring/Analysis Details
[Command-specific: dimensions, calculations, classifications]

### What to Do Next
[Which command to run next in the pipeline, or remediation actions]
```

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Generated guide drifts from actual behavior | Medium | High | Cross-reference every command detail against actual command specs in `adapters/claude-code/commands/` |
| Guide length becomes unwieldy | Low | Medium | Quick Start provides immediate value; comprehensive sections are reference, not linear reading |
| Prompt spec and guide diverge | Medium | Medium | Update spec first (Phase 1), then guide (Phase 3); validate parity in Phase 4 |

## Complexity Tracking

No constitution violations. No complexity justifications needed.
