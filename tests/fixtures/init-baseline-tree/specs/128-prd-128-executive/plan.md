---
spec_reference: specs/128-prd-128-executive/spec.md
triad:
  pm_signoff:
    agent: product-manager
    date: 2026-04-09
    status: APPROVED
    notes: "Plan covers FR-001 to FR-036 and US-1 to US-4 with full traceability. Scope disciplined (Out of Scope items honored, severity legend deferral preserved). Backward compat validation procedure documented. ~320 line estimate vs PRD 210-250 justified by constitutionally required tests + FR-036 skill reference doc. 0 concerns. Full review at .aod/results/product-manager-plan.md."
  architect_signoff:
    agent: architect
    date: 2026-04-09
    status: APPROVED
    notes: "All 4 PRD architect concerns resolved. ADR-014/016/017/019 compliant. Pattern reuse of F-091 + F-112 correct and explicit. infographic-page() reuse documented (no new Typst function). Constitution Principles III/VI/VII/IX satisfied. 2 low-severity non-blocking observations for /aod.tasks handling: (L-1) add component name normalization in callout matcher with mixed-case test; (L-2) confirm baseline PDF storage approach. Full review at .aod/results/architect-plan.md."
  techlead_signoff: null
---

# Implementation Plan: Executive Threat Architecture Infographic

**Branch**: `128-prd-128-executive` | **Date**: 2026-04-09 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/128-prd-128-executive/spec.md`

## Summary

Add a sixth infographic template (`executive-architecture`) to the tachi pipeline and surface its output on pages 2–3 of the security report PDF (immediately after the Executive Summary). The template renders a layered architecture diagram with narrative threat callouts (Critical/High only, one per architectural layer, ≤25 words plain English) so executive readers see the most important visual within their attention window.

The technical approach reuses two established patterns: F-091 for adding a new infographic template (extraction branch + spec template + schema entry + command dispatch) and F-112 for inserting a new PDF page at a specific position (boolean-gated `infographic-page()` call in `main.typ` after the Executive Summary). The existing `infographic-page()` Typst function is already portrait, so no new page-layout code is required. Architectural layers are derived from threats.md Section 2 trust boundaries (with Section 1 component grouping as a fallback), explicitly distinct from MAESTRO layers.

## Technical Context

**Language/Version**: Python 3.11 (extraction scripts), Typst 0.11+ (PDF templates), Markdown + YAML (agent specs and schemas)
**Primary Dependencies**: Existing `scripts/tachi_parsers.py` (shared parser module), Gemini API via existing `tachi-threat-infographic` agent, Typst CLI for PDF compilation
**Storage**: Filesystem only — markdown spec files and JPEG images written to per-run output folders under `examples/` or user-supplied directories
**Testing**: pytest for Python script unit tests (existing convention in `tests/scripts/`), shell-based integration tests for full pipeline runs, byte-comparison tests for PDF backward compatibility
**Target Platform**: Cross-platform CLI (macOS, Linux); no server runtime
**Project Type**: Single project — tachi is a methodology toolkit with Python scripts, Markdown agents, Typst templates, and YAML schemas; no separate frontend/backend
**Performance Goals**: Extraction adds ≤2s to `extract-infographic-data.py` runtime; PDF compilation time unchanged for examples without the new image; Gemini image generation latency acceptable per existing template baselines (typically 5–15s)
**Constraints**:
- Backward compatibility: existing 5 examples must produce byte-identical PDFs when the new image is absent (Constitution Principle III, NON-NEGOTIABLE)
- Deterministic extraction: byte-identical output on identical input (ADR-017)
- Spec-first: markdown spec is primary; image generation is best-effort (ADR-014)
- No new required dependencies, no new environment variables
- One callout per architectural layer maximum (executive simplicity)
**Scale/Scope** (revised after team-lead tasks review on 2026-04-09):
- 8 source files modified, plus test infrastructure bootstrap (new), plus 2 test files, plus 1 example folder regenerated
- ~745 lines total: ~215 source + ~30 skill reference doc + ~60 test infrastructure bootstrap + ~370 test code + ~70 misc (verification writeups, PR)
- ~5–6 focused sessions of work (initial PRD estimate of 1–2 sessions did not account for the missing test infrastructure)
- 36 functional requirements across extraction, agent spec, command, schema, and PDF integration

**Plan correction (2026-04-09)**: The original plan claimed pytest was the "existing convention in `tests/scripts/`" — this was incorrect. tachi has no `tests/` directory, no `pytest.ini`, no `conftest.py`, no `pyproject.toml` test config, and no `requirements-dev.txt`. F-091 and F-112 (the patterns this feature reuses) added zero Python tests. To satisfy Constitution Principle VI (Testing Excellence ≥80% coverage), F-128 must bootstrap the pytest harness as a Phase 0 task. The test infrastructure work (~60 lines, ~0.5–1 session) is folded into tasks.md and the timeline is revised from 1–2 sessions to 5–6 sessions. The architectural decisions in this plan are unchanged.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Compliance | Notes |
|-----------|------------|-------|
| I. General-Purpose Architecture | ✅ Pass | F-128 is a content/visualization template, not a domain-specific feature |
| II. API-First Design | N/A | tachi has no REST API; this is a CLI/methodology toolkit |
| III. Backward Compatibility (NON-NEGOTIABLE) | ✅ Pass | All 5 unmodified examples must produce byte-identical PDFs (FR-031, FR-035, SC-003); boolean gating via `has-executive-architecture` follows established F-091/F-112 pattern |
| IV. Concurrency & Data Integrity | N/A | No shared mutable state; each pipeline run writes to its own output folder |
| V. Privacy & Data Isolation | N/A | No user data persistence beyond output files; no cross-tenant concerns |
| VI. Testing Excellence | ✅ Pass | Plan includes unit tests for new extraction function (≥80% coverage), integration test for full pipeline run, byte-comparison test for backward compatibility |
| VII. Definition of Done (NON-NEGOTIABLE) | ✅ Pass | DoD verified via: tests passing in CI, agentic-app example regenerated and committed, manual review of PDF page positioning |
| VIII. Observability & Root Cause Analysis | ✅ Pass | Extraction script uses existing logging convention; exit codes follow established 0/1/2 pattern; clear error messages on validation failure |
| IX. Git Workflow (NON-NEGOTIABLE) | ✅ Pass | Working on branch `128-prd-128-executive`; conventional commits; PR review before merge |
| X. Product-Spec Alignment (NON-NEGOTIABLE) | ✅ Pass | PRD has Triad sign-offs; spec has PM sign-off; this plan will receive PM + Architect dual sign-off |
| XI. SDLC Triad Collaboration | ✅ Pass | Triad workflow followed end-to-end; no skipped governance gates |

**Initial Constitution Check Result**: ✅ PASS — no violations to justify in Complexity Tracking.

### Architectural Decision Records Touched

- **ADR-014 (Spec-First Architecture)**: F-128 conforms — extraction always produces a markdown spec, image generation is best-effort
- **ADR-016 (Standalone Command Pattern)**: F-128 conforms — `/tachi.infographic --template executive-architecture` works standalone, decoupled from orchestrator
- **ADR-017 (Deterministic Extraction)**: F-128 conforms — extraction is pure Python with byte-identical output; LLM-based rewriting is in the agent's Gemini prompt phase, not the extraction script
- **ADR-019 (Schema-First Development)**: F-128 conforms — `schemas/infographic.yaml` will be updated to enumerate the new template before code-level changes
- **No new ADRs required**: This feature follows existing patterns and does not introduce new architectural concepts

## Project Structure

### Documentation (this feature)

```
specs/128-prd-128-executive/
├── plan.md              # This file (/aod.project-plan output)
├── spec.md              # Feature specification (PM-approved)
├── research.md          # Research findings (codebase, architecture, web)
├── data-model.md        # Data structures: JSON payload, layer entity, callout entity
├── quickstart.md        # How to run F-128 end-to-end on agentic-app
├── contracts/           # Schema additions and CLI argument contracts
│   ├── infographic-schema-additions.yaml   # Diff for schemas/infographic.yaml
│   ├── extraction-cli-contract.md          # extract-infographic-data.py CLI args + JSON payload shape
│   └── report-data-typst-contract.md       # report-data.typ variable bindings
└── tasks.md             # Task breakdown (/aod.tasks output, future)
```

### Source Code (repository root)

This is the **single project** structure used by tachi. tachi is a methodology toolkit, not an application — there is no `src/` directory in the conventional sense. The relevant source files for F-128 are:

```
tachi/
├── scripts/
│   ├── extract-infographic-data.py      # MODIFIED: add executive-architecture extraction branch
│   ├── extract-report-data.py           # MODIFIED: detect threat-executive-architecture.jpg, set has-executive-architecture flag
│   └── tachi_parsers.py                 # READ-ONLY: reuse parse_scope_data() and trust-zone helpers
├── schemas/
│   └── infographic.yaml                 # MODIFIED: add executive-architecture template enumeration
├── templates/tachi/security-report/
│   ├── main.typ                         # MODIFIED: insert executive-architecture page after Executive Summary
│   └── full-bleed.typ                   # READ-ONLY: reuse infographic-page() (already portrait)
├── .claude/
│   ├── agents/tachi/
│   │   ├── threat-infographic.md        # MODIFIED: add executive-architecture spec template structure
│   │   └── report-assembler.md          # MODIFIED: update artifact detection table
│   ├── commands/
│   │   └── tachi.infographic.md         # MODIFIED: add executive-architecture + exec alias + all expansion
│   └── skills/tachi-infographics/
│       └── references/                  # MODIFIED: add executive-architecture reference doc
├── tests/
│   └── scripts/
│       ├── test_extract_infographic_data.py    # MODIFIED: add unit tests for executive-architecture branch
│       └── test_extract_report_data.py         # MODIFIED: add unit test for has-executive-architecture detection
└── examples/agentic-app/
    └── sample-report/                   # REGENERATED: add threat-executive-architecture-spec.md, threat-executive-architecture.jpg, updated PDF
```

**Structure Decision**: Single project, using the existing tachi directory layout. No new top-level directories. All changes are additive to existing files except the new executive-architecture reference doc and the regenerated example artifacts.

### File Change Summary

| File | Action | Estimated Δ Lines | Purpose |
|------|--------|-------------------|---------|
| `scripts/extract-infographic-data.py` | Modify | ~80 | Add executive-architecture extraction branch (filter, layer grouping, callout selection, JSON payload assembly) |
| `scripts/extract-report-data.py` | Modify | ~20 | Add image detection for `threat-executive-architecture.jpg`, write `has-executive-architecture` flag and image path to `report-data.typ` |
| `schemas/infographic.yaml` | Modify | ~25 | Add executive-architecture template enumeration with section structure |
| `templates/tachi/security-report/main.typ` | Modify | ~15 | Insert `if has-executive-architecture { infographic-page(...) }` block after Executive Summary, before Attack Path Analysis |
| `.claude/agents/tachi/threat-infographic.md` | Modify | ~50 | Add executive-architecture template description, six-section spec structure, Gemini prompt construction guidance (portrait, layers, callouts, ≤25 words) |
| `.claude/agents/tachi/report-assembler.md` | Modify | ~10 | Update artifact detection table with new artifact and flag |
| `.claude/commands/tachi.infographic.md` | Modify | ~15 | Add executive-architecture to choices, add `exec` alias, include in `all` expansion |
| `.claude/skills/tachi-infographics/references/` | Add | ~30 | New reference doc for executive-architecture template |
| `tests/scripts/test_extract_infographic_data.py` | Modify | ~60 | Unit tests: filter, layer grouping, callout selection, skip-image edge case |
| `tests/scripts/test_extract_report_data.py` | Modify | ~15 | Unit tests: image detection, flag setting |
| `examples/agentic-app/sample-report/` | Regenerate | (artifacts) | New spec, new JPEG, updated PDF (1 manual run) |

**Total estimated change**: ~320 lines across 8 source files + 2 test files + 1 example regeneration. This is slightly above the PRD tech-lead estimate (210–250 lines) because the plan adds 30 lines for the new skill reference doc and ~75 lines of test coverage. Both additions are required by Constitution Principle VI (Testing Excellence) and the F-091 pattern (skill references must document each template).

## Phase 0: Outline & Research

**Status**: ✅ Complete (executed during `/aod.spec`)

**Output**: [research.md](research.md) — see for full findings.

**Key resolutions**:

1. **Pattern reuse identified**: F-091 (template addition) + F-112 (early-page insertion) provide all required patterns. No new architectural concepts.
2. **Portrait function already exists**: `infographic-page()` in `templates/tachi/security-report/full-bleed.typ:40-86` is already portrait. No new Typst function required (resolves architect concern #1 and tech-lead concern #3).
3. **Architectural layer source defined**: Trust zones from `threats.md` Section 2 (parsed by existing `parse_scope_data()` and `_compute_trust_zones()`), with DFD component-type grouping as fallback (resolves architect concern #3 and tech-lead concern #2).
4. **Callout text rewriting location**: Extraction passes raw descriptions; agent's Gemini prompt rewrites to ≤25 words plain English (resolves architect concern #4 and tech-lead concern #1).
5. **Page insertion point identified**: Lines 191 → 197 in `main.typ` (after Executive Summary, before Attack Path Analysis conditional block). Pattern: `#if has-executive-architecture { infographic-page(...) }`.
6. **Boolean gating pattern confirmed**: `extract-report-data.py:797-830` has the existing `detect_images()` function that needs one new entry for `threat-executive-architecture.jpg`.
7. **No new dependencies needed**: All required parsing logic already exists in `scripts/tachi_parsers.py`. Gemini API is reused via the existing `tachi-threat-infographic` agent.

**No NEEDS CLARIFICATION markers remaining**.

## Phase 1: Design & Contracts

**Prerequisites**: Phase 0 research complete ✅

### 1.1 Data Model

See [data-model.md](data-model.md) for the full data model.

**Key entities**:

- **`ArchitecturalLayer`**: A grouping of system components by trust zone (preferred) or by DFD component type (fallback). Fields: `name`, `position` (ordinal in trust hierarchy), `components[]` (list of component names), `component_count`. Distinct from MAESTRO layers.
- **`ThreatCallout`**: A narrative annotation on one architectural layer. Fields: `layer_name`, `finding_id`, `severity` (Critical or High only), `raw_description`, `composite_score` (optional, from compensating-controls or risk-scores tier).
- **`ExecutiveArchitecturePayload`**: Top-level JSON output of the extraction script. Fields: `metadata` (template name, tier, source file, timestamp, total_filtered_count, qualifying_layer_count, skip_image bool), `layers[]` (ordered ArchitecturalLayer list), `callouts[]` (one ThreatCallout per layer that has a qualifying finding), `severity_distribution` (Critical and High counts only).

### 1.2 Contracts

See [contracts/](contracts/) for the full contract specifications.

- **`infographic-schema-additions.yaml`**: Diff to `schemas/infographic.yaml` enumerating the `executive-architecture` template, its six section names, and its visual directives (portrait, pastel layer fills, red dashed-border callouts, warning icons).
- **`extraction-cli-contract.md`**: CLI argument additions to `extract-infographic-data.py` (`--template executive-architecture`), JSON payload shape, exit codes (0/1/2), error messages.
- **`report-data-typst-contract.md`**: New variable bindings in the generated `report-data.typ`: `has-executive-architecture` (bool), `executive-architecture-image-path` (string).

**No REST API contracts** — tachi is a CLI toolkit, not an API service. The "contracts" here are CLI argument shapes, JSON payload schemas, and Typst variable bindings.

### 1.3 Quickstart

See [quickstart.md](quickstart.md) for the end-to-end run procedure.

**Quickstart summary**:
```bash
# 1. Run threat model on the example (already in repo)
cat examples/agentic-app/sample-report/threats.md  # verify exists

# 2. Generate the new infographic
/tachi.infographic --template executive-architecture --output examples/agentic-app/sample-report/

# 3. Compile the PDF (automatically picks up the new image)
/tachi.security-report --output examples/agentic-app/sample-report/

# 4. Verify page position
# Open the resulting PDF and confirm the executive architecture page
# appears immediately after the Executive Summary
```

### 1.4 Agent Context Update

After this plan is approved, run:

```bash
.aod/scripts/bash/update-agent-context.sh claude
```

This updates the Claude agent context file with the new technologies / patterns introduced by F-128 (none, since F-128 reuses existing patterns), preserving manual additions between markers.

### 1.5 Implementation Phases (high level — actual breakdown comes from `/aod.tasks`)

1. **Schema** (~25 lines): Add `executive-architecture` to `schemas/infographic.yaml` (schema-first per ADR-019)
2. **Extraction script** (~80 lines): Add new branch in `extract-infographic-data.py` with helper functions for layer grouping, callout selection, and JSON payload assembly
3. **Report extraction** (~20 lines): Add image detection and Typst variable bindings in `extract-report-data.py`
4. **Typst page integration** (~15 lines): Insert `if has-executive-architecture` block in `main.typ` at the post-Executive-Summary position
5. **Agent spec** (~50 lines): Add executive-architecture six-section template and Gemini prompt construction guidance in `threat-infographic.md`
6. **Command + alias** (~15 lines): Update `tachi.infographic.md` with new template, exec alias, and `all` expansion
7. **Report assembler doc + skill reference** (~40 lines): Update `report-assembler.md` artifact detection table; add new skill reference doc
8. **Tests** (~75 lines): Unit tests for extraction branch and report-data flag
9. **Example regeneration**: Run pipeline on agentic-app, commit the resulting spec, image, and PDF

### 1.6 Backward Compatibility Validation Plan

Before merge:

1. Run `/tachi.security-report` against all 6 example folders WITHOUT generating the new image
2. Diff each resulting PDF against its pre-F-128 baseline (committed in repo)
3. All 5 unmodified examples (web-app, microservices, ascii-web-api, mermaid-agentic-app, free-text-microservice) MUST be byte-identical to baseline
4. The agentic-app example will be different because we are intentionally regenerating it

**Tooling**: Use `cmp` or `diff` for byte-level comparison. Document the comparison procedure in the test plan.

## Constitution Check (Post-Design Re-Evaluation)

After completing Phase 1 design:

| Principle | Compliance | Re-check Notes |
|-----------|------------|----------------|
| I. General-Purpose Architecture | ✅ Pass | Design adds a content template; no domain-specific logic in core components |
| III. Backward Compatibility (NON-NEGOTIABLE) | ✅ Pass | Backward compatibility validation plan defined in 1.6; boolean gating in main.typ ensures no impact when image absent |
| VI. Testing Excellence | ✅ Pass | Test plan covers extraction branch (≥80% coverage), report-data flag, byte-comparison for backward compatibility |
| VII. Definition of Done (NON-NEGOTIABLE) | ✅ Pass | DoD verifiable: tests pass, agentic-app regenerated, PDF page position manually confirmed |
| IX. Git Workflow (NON-NEGOTIABLE) | ✅ Pass | Branch in use; conventional commits; PR review required |
| X. Product-Spec Alignment (NON-NEGOTIABLE) | ✅ Pass | This plan is being submitted for PM + Architect dual sign-off |

**Post-Design Constitution Check Result**: ✅ PASS — design conforms to all applicable principles.

## Complexity Tracking

*No constitutional violations to justify.*

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|--------------------------------------|
| (none) | (n/a) | (n/a) |

**Note on scope vs PRD estimate**: The plan estimates ~320 lines vs the PRD tech-lead's 210–250 line estimate. The delta is due to (1) adding test coverage required by Constitution Principle VI which the PRD did not size, and (2) adding the skill reference doc to satisfy F-091 pattern parity. Both are required, not optional. If the team-lead reviewer flags this as scope expansion, the recommended course is to keep both since they support the constitution and existing patterns; the PRD estimate was sized at 8 source files only.

## Components

The feature touches the following logical components of the tachi pipeline:

### Extraction Layer
- **`extract-infographic-data.py`**: Receives `--template executive-architecture`; reads threats.md (with optional risk-scores or compensating-controls for tier upgrade); parses scope data via shared `tachi_parsers.parse_scope_data()`; groups components into architectural layers via existing `_compute_trust_zones()`; filters findings to Critical/High; selects one callout per layer (severity desc → composite score desc → finding ID asc); outputs JSON payload to stdout.
- **`extract-report-data.py`**: Adds new entry in `detect_images()` for `threat-executive-architecture.jpg`; writes `has-executive-architecture` boolean and `executive-architecture-image-path` string into the generated `report-data.typ` file.

### Spec Generation Layer
- **`tachi-threat-infographic` agent (`.claude/agents/tachi/threat-infographic.md`)**: Receives the JSON payload from extraction; renders the six-section markdown spec; constructs the Gemini prompt with portrait orientation, layer ordering, pastel fills, red dashed-border callouts, warning icons, and ≤25-word plain-English narrative instructions.

### Image Generation Layer
- **Existing Gemini integration**: Reused as-is. The agent invokes Gemini with the constructed prompt; on success writes `threat-executive-architecture.jpg` to the output folder; on failure leaves the spec file in place (spec-first per ADR-014).

### PDF Assembly Layer
- **`main.typ`**: Imports `report-data.typ`; conditionally renders the executive architecture page using existing `infographic-page()` (already portrait), gated by `has-executive-architecture`, positioned immediately after Executive Summary and immediately before Attack Path Analysis.
- **`report-assembler` agent**: Documentation update only — adds the new artifact to its detection table.

### Schema and Command Layer
- **`schemas/infographic.yaml`**: Adds `executive-architecture` to the template enumeration with section structure and visual directive constants.
- **`.claude/commands/tachi.infographic.md`**: Adds new template to argparse choices, adds `exec` alias, includes in `all` expansion before MAESTRO additions.
- **`.claude/skills/tachi-infographics/references/`**: New reference doc describing the template, its outputs, and expected behavior.

## Data Flow

```
┌──────────────────────────────────────────────────────────────────────────┐
│  threats.md (+ optional risk-scores.md / compensating-controls.md)       │
└─────────────────────────┬────────────────────────────────────────────────┘
                          │
                          ▼
┌──────────────────────────────────────────────────────────────────────────┐
│  scripts/tachi_parsers.py                                                │
│   - parse_scope_data() → components, trust_boundaries, data_flows       │
│   - parse_threats_findings() → Critical/High findings with metadata     │
└─────────────────────────┬────────────────────────────────────────────────┘
                          │
                          ▼
┌──────────────────────────────────────────────────────────────────────────┐
│  scripts/extract-infographic-data.py (--template executive-architecture)│
│   1. Detect tier (compensating > risk-scores > threats)                 │
│   2. Group components into ArchitecturalLayers via _compute_trust_zones │
│      OR fall back to DFD type grouping if no zones                      │
│   3. Filter findings to Critical/High                                    │
│   4. Select one callout per layer (severity → score → ID)               │
│   5. Build ExecutiveArchitecturePayload JSON                            │
│   6. Emit JSON to stdout                                                 │
└─────────────────────────┬────────────────────────────────────────────────┘
                          │
                          ▼
┌──────────────────────────────────────────────────────────────────────────┐
│  .claude/agents/tachi/threat-infographic.md                             │
│   1. Read JSON payload                                                   │
│   2. Render threat-executive-architecture-spec.md (6 sections)          │
│   3. Construct Gemini prompt (portrait, layers, callouts, ≤25 words)   │
│   4. Invoke Gemini API                                                   │
│   5. Write threat-executive-architecture.jpg (best-effort)              │
└─────────────────────────┬────────────────────────────────────────────────┘
                          │
                          ▼
┌──────────────────────────────────────────────────────────────────────────┐
│  Output folder contents:                                                 │
│   - threat-executive-architecture-spec.md  (always)                     │
│   - threat-executive-architecture.jpg      (if Gemini succeeds)         │
└─────────────────────────┬────────────────────────────────────────────────┘
                          │
                          ▼
┌──────────────────────────────────────────────────────────────────────────┐
│  scripts/extract-report-data.py                                          │
│   - detect_images() finds threat-executive-architecture.jpg              │
│   - Writes has-executive-architecture: true and image path              │
│     into report-data.typ                                                 │
└─────────────────────────┬────────────────────────────────────────────────┘
                          │
                          ▼
┌──────────────────────────────────────────────────────────────────────────┐
│  Typst compilation (templates/tachi/security-report/main.typ)           │
│   - Imports report-data.typ                                              │
│   - On encountering `if has-executive-architecture { ... }` after the   │
│     Executive Summary block, calls infographic-page() (portrait)        │
│   - Otherwise skips the page entirely (backward compatibility)          │
└─────────────────────────┬────────────────────────────────────────────────┘
                          │
                          ▼
┌──────────────────────────────────────────────────────────────────────────┐
│  Final PDF: pages 1 (cover), 2 (TOC), 3 (Methodology),                  │
│  4 (Scope), 5 (Executive Summary),                                       │
│  → 6 (NEW: Executive Threat Architecture)                               │
│  → 7+ (Attack Path Analysis, existing infographics, findings, etc.)     │
└──────────────────────────────────────────────────────────────────────────┘
```

## Tech Stack

| Layer | Technology | Version | Role in F-128 |
|-------|------------|---------|---------------|
| Extraction | Python | 3.11 | Modify `extract-infographic-data.py` and `extract-report-data.py` |
| Parsing | `tachi_parsers.py` | existing | Reuse for scope data and finding parsing — NO modifications |
| Schema | YAML | 1.2 | Modify `schemas/infographic.yaml` |
| Agent | Markdown | n/a | Modify `.claude/agents/tachi/threat-infographic.md` and `report-assembler.md` |
| Command | Markdown | n/a | Modify `.claude/commands/tachi.infographic.md` |
| Image generation | Gemini API | existing integration | Reuse via agent — NO new API calls or dependencies |
| PDF compilation | Typst | 0.11+ | Modify `main.typ`; reuse `infographic-page()` (no new template function) |
| Testing | pytest | existing | Add unit tests in `tests/scripts/` |

**No new dependencies introduced.**

## Risk Register

| Risk | Likelihood | Impact | Mitigation | Contingency |
|------|-----------|--------|------------|-------------|
| Trust zones too coarse to produce meaningful layers in agentic-app example | Medium | Medium | Implement DFD type fallback (FR-003) | If both fail, surface validation error with code 2 and clear message; tune extraction in a follow-up |
| Gemini prompt does not produce the desired layered visual style | Medium | Low | FR-015 specifies prompt construction in detail; iterate on prompt during implementation phase | Spec file is still usable for manual diagram creation; image generation is best-effort per ADR-014 |
| Backward compatibility regression on one of the 5 unmodified examples | Low | High | Backward compatibility validation plan in 1.6 runs byte-comparison on all 5 examples before merge | Block merge until regression is identified and fixed; isolate changes to additive paths only |
| Test coverage below 80% on new extraction branch | Low | Medium | Plan includes ~75 lines of test coverage targeting all branches of the new code | If coverage falls short, add edge-case tests in the test step before requesting merge |
| Page insertion shifts other pages and breaks attack path positioning | Low | Medium | Insertion is conditional on `has-executive-architecture` flag; when absent, page count is identical to baseline | Backward compatibility validation catches this; revert insertion point if needed |

## Deliverables Checklist

- [ ] `schemas/infographic.yaml` updated with executive-architecture enumeration
- [ ] `scripts/extract-infographic-data.py` extended with executive-architecture branch
- [ ] `scripts/extract-report-data.py` extended with image detection and Typst variable bindings
- [ ] `templates/tachi/security-report/main.typ` extended with conditional page insertion
- [ ] `.claude/agents/tachi/threat-infographic.md` extended with new template structure and Gemini prompt
- [ ] `.claude/agents/tachi/report-assembler.md` artifact detection table updated
- [ ] `.claude/commands/tachi.infographic.md` extended with new template, exec alias, all expansion
- [ ] `.claude/skills/tachi-infographics/references/` new reference doc
- [ ] `tests/scripts/test_extract_infographic_data.py` extended with unit tests
- [ ] `tests/scripts/test_extract_report_data.py` extended with unit test
- [ ] `examples/agentic-app/sample-report/` regenerated (spec, JPEG, PDF)
- [ ] All 5 unmodified examples produce byte-identical PDFs to baseline
- [ ] PR opened with conventional commit format and CHANGELOG entry deferred to `/aod.document`

## Open Questions for `/aod.tasks`

None blocking. The plan is fully specified for task generation.

Two minor implementation details for the team-lead to size during `/aod.tasks`:

1. Whether the new skill reference doc should be a single file or split into multiple (purpose vs visual layout vs CLI args). Recommendation: single file for parity with other templates.
2. Whether to add a regression test that runs the full pipeline on agentic-app and asserts the PDF page count and TOC contents. Recommendation: yes, as a sanity check at the system level.
