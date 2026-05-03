---
triad:
  pm_signoff:
    agent: product-manager
    date: 2026-03-25
    status: APPROVED
    notes: "All 15 functional requirements have traceable plan coverage. All 4 user stories and 16 acceptance scenarios map to specific wave steps. 4-wave structure matches PRD exactly. No scope creep. Non-blocking observation: report agent estimated at ~448 lines post-extraction, above 300-400 target — team should pursue additional condensation during Wave 3."
  architect_signoff:
    agent: architect
    date: 2026-03-25
    status: APPROVED_WITH_CONCERNS
    notes: "All line ranges verified accurate against source files. Extraction classifications correct. Error handling split at right boundary. Reference document design follows lazy-load patterns. Wave sequencing respects all dependencies. No anti-patterns. 3 minor concerns addressed in plan: (1) error trigger summaries retained in core agent, (2) report agent target adjusted to ~400-450 realistic floor, (3) orchestrator ~1,200 lines acknowledged as accepted residual."
  techlead_signoff: null
---

# Implementation Plan: Agent Refactoring — Right-Size Orchestrator, Report, and Infographic Agents

**Branch**: `029-agent-refactoring-right` | **Date**: 2026-03-25 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `specs/029-agent-refactoring-right/spec.md`

## Summary

Extract consultation-only content from 3 oversized agents into on-demand reference documents. The orchestrator (2,085 lines), threat-report (801 lines), and threat-infographic (592 lines) all exceed the 300-line best-practices ceiling. Reference extraction reduces always-loaded context without splitting the sequential pipeline, preserving all capabilities while improving instruction-following fidelity.

## Technical Context

**Language/Version**: Markdown (agent prompts and reference documents)
**Primary Dependencies**: Claude Code agent framework (Read tool for on-demand reference loading)
**Storage**: File system — all artifacts are markdown files in `adapters/claude-code/agents/`
**Testing**: Regression testing via `/threat-model` on `examples/agentic-app/architecture.md`; `wc -l` for line counts; `git diff` for zero-regression verification on threat agents
**Target Platform**: Any LLM platform capable of reading markdown files (platform-neutral agents)
**Project Type**: Content refactoring — markdown agent files, no runtime code
**Performance Goals**: No increase in total token cost per threat model run
**Constraints**: Preservation-first — all capabilities inventoried before changes; zero external interface changes
**Scale/Scope**: 3 agent files refactored, 5-6 reference documents created, 11 threat agents verified unchanged

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. General-Purpose Architecture | PASS | Refactoring is domain-agnostic — reference extraction pattern works for any agent |
| III. Backward Compatibility | PASS | Zero external interface changes; `/threat-model` invocation and output formats unchanged |
| VII. Definition of Done | PASS | Regression test, line count verification, capability inventory committed |
| VIII. Observability | PASS | Missing reference documents produce clear error messages |
| IX. Git Workflow | PASS | Feature branch `029-agent-refactoring-right` created |
| X. Product-Spec Alignment | PASS | Spec approved by PM; plan requires dual PM + Architect sign-off |

No violations requiring justification.

## Project Structure

### Documentation (this feature)

```
specs/029-agent-refactoring-right/
├── plan.md                    # This file
├── spec.md                    # Feature specification (PM approved)
├── research.md                # Research phase output
├── capability-inventory.md    # Pre-refactoring capability inventory (deliverable)
└── checklists/
    └── requirements.md        # Spec quality checklist
```

### Source Code (repository root)

```
adapters/claude-code/agents/
├── orchestrator.md                  # Refactored: 2,085 → ~1,100-1,200 lines
├── threat-report.md                 # Refactored: 801 → ~300-400 lines
├── threat-infographic.md            # Refactored: 592 → ~300-400 lines
├── references/                      # NEW — on-demand reference documents
│   ├── sarif-generation.md          # ~494 lines, loaded at Phase 4 completion
│   ├── validation-checklist.md      # ~85 lines, loaded at pipeline end
│   ├── error-templates.md           # ~100 lines, loaded on error
│   ├── report-templates.md          # ~293 lines, loaded during report generation
│   ├── infographic-gemini-api.md    # ~143 lines, loaded during image generation
│   └── infographic-error-handling.md # ~59 lines, loaded on infographic error
├── spoofing.md                      # UNCHANGED (108 lines)
├── tampering.md                     # UNCHANGED (121 lines)
├── repudiation.md                   # UNCHANGED (119 lines)
├── info-disclosure.md               # UNCHANGED (123 lines)
├── denial-of-service.md             # UNCHANGED (136 lines)
├── privilege-escalation.md          # UNCHANGED (131 lines)
├── prompt-injection.md              # UNCHANGED (162 lines)
├── data-poisoning.md                # UNCHANGED (166 lines)
├── model-theft.md                   # UNCHANGED (183 lines)
├── agent-autonomy.md                # UNCHANGED (196 lines)
└── tool-abuse.md                    # UNCHANGED (180 lines)
```

**Structure Decision**: No new directories beyond `references/`. All reference documents co-located with the agents they serve, under a single `references/` subdirectory.

## Content Inventory & Extraction Map

### Orchestrator (2,085 lines → ~1,100-1,200 target)

| Section | Lines | Range | Action | Destination |
|---------|-------|-------|--------|-------------|
| Metadata + agent roster | ~40 | 1-41 | KEEP | Core agent |
| Input Sanitization Boundary | ~20 | 60-80 | KEEP | Core agent |
| Output Format Specification (7 sections) | ~185 | 82-267 | KEEP | Core agent |
| Phase 1: Scope (format detection, DFD, trust boundaries) | ~265 | 269-533 | KEEP + CONDENSE | Core agent |
| Phase 2: Determine Threats (STRIDE dispatch, AI keywords) | ~265 | 534-810 | KEEP | Core agent |
| Phase 3: Countermeasures (risk validation, correlation) | ~200 | 811-1011 | KEEP | Core agent |
| Phase 4: Assess (coverage matrix, risk summary) | ~125 | 1012-1137 | KEEP | Core agent |
| Output Structural Validation Checklist | ~85 | 1138-1223 | EXTRACT | `references/validation-checklist.md` |
| SARIF Output Generation | ~494 | 1224-1718 | EXTRACT | `references/sarif-generation.md` |
| Phase 5: Report dispatch | ~65 | 1719-1784 | KEEP + CONDENSE | Core agent |
| Phase 6: Infographic dispatch | ~72 | 1785-1856 | KEEP + CONDENSE | Core agent |
| Error Handling — UNSUPPORTED_FORMAT | ~45 | 1863-1908 | SPLIT | YAML templates → `references/error-templates.md`; trigger summary (1-2 lines) retained in core agent |
| Error Handling — NO_COMPONENTS | ~41 | 1908-1949 | SPLIT | YAML templates → `references/error-templates.md`; trigger summary (1-2 lines) retained in core agent |
| Error Handling — INVALID_FORMAT_VALUE | ~41 | 1949-1990 | SPLIT | YAML templates → `references/error-templates.md`; trigger summary (1-2 lines) retained in core agent |
| Error Evaluation Order | ~8 | 1990-2001 | KEEP | Core agent (defensive spec) |
| Ambiguous DFD Classification | ~35 | 2002-2036 | KEEP | Core agent (defensive spec) |
| Non-Conforming Finding Handling | ~28 | 2037-2069 | KEEP | Core agent (defensive spec) |
| Three-State Cell Model | ~16 | 2070-2085 | KEEP | Core agent (defensive spec) |
| Verbose prose (scattered) | ~200 | Scattered | DELETE | N/A |

**Estimated reduction**: 494 (SARIF) + 85 (validation) + ~100 (error templates) + ~200 (prose) = **~879 lines removed**
**Estimated post-refactor**: 2,085 - 879 = **~1,206 lines** (within 1,100-1,200 target)

**Accepted residual**: The orchestrator at ~1,200 lines remains 4x over the 300-line best-practices ceiling. This is an accepted position — the research analysis identifies ~1,400 lines as irreducible specification content (phase sequencing, dispatch rules, risk matrices, output format definitions). The 300-line ceiling applies to heuristic/guidance agents, not specification-heavy orchestrators.

### Threat-Report (801 lines → ~300-400 target)

| Section | Lines | Range | Action | Destination |
|---------|-------|-------|--------|-------------|
| Metadata + Core Mission | ~37 | 1-37 | KEEP | Core agent |
| Input Contract | ~55 | 40-92 | KEEP | Core agent |
| Quality Standards + Validation Checklist | ~50 | 93-151 | KEEP | Core agent |
| Report Generation Methodology | ~135 | 153-287 | KEEP | Core agent |
| Correlation Group Handling | ~60 | 288-348 | KEEP | Core agent |
| Attack Tree Construction Rules | ~44 | 349-392 | EXTRACT | `references/report-templates.md` |
| Mermaid Conventions + Validation Checklist | ~139 | 393-531 | EXTRACT | `references/report-templates.md` |
| Example Attack Trees (2 full examples) | ~110 | 532-642 | EXTRACT | `references/report-templates.md` |
| Dual Output Location | ~57 | 643-700 | KEEP + CONDENSE | Core agent |
| Remediation Roadmap Generation | ~101 | 700-801 | KEEP + CONDENSE | Core agent |

**Estimated reduction**: 44 (attack tree rules) + 139 (mermaid) + 110 (examples) + ~60 (prose condensation) = **~353 lines removed**
**Estimated post-refactor**: 801 - 353 = **~448 lines**

**Target adjustment**: The report agent's realistic floor is ~400-450 lines post-extraction. Additional prose condensation candidates: executive summary generation methodology (~20 lines of verbose explanation), architecture overview narrative (~15 lines), and per-finding narrative template (~15 lines). Best-effort condensation should bring the total to ~390-420. If the floor exceeds 400 after best-effort condensation, document the justification in the capability inventory — the remaining content is specification, not prose.

### Threat-Infographic (592 lines → ~300-400 target)

| Section | Lines | Range | Action | Destination |
|---------|-------|-------|--------|-------------|
| Metadata + Core Mission | ~61 | 1-61 | KEEP | Core agent |
| Input Contract | ~37 | 63-99 | KEEP | Core agent |
| Data Extraction Methodology | ~84 | 102-185 | KEEP | Core agent |
| Infographic Specification Format | ~155 | 186-341 | KEEP | Core agent |
| Quality Standards | ~46 | 342-388 | KEEP | Core agent |
| Gemini API Prompt Construction | ~56 | 389-445 | EXTRACT | `references/infographic-gemini-api.md` |
| Gemini API Integration (config, request, response) | ~87 | 446-532 | EXTRACT | `references/infographic-gemini-api.md` |
| Error Handling & Graceful Degradation | ~59 | 533-592 | EXTRACT | `references/infographic-error-handling.md` |

**Estimated reduction**: 56 (API prompt) + 87 (API integration) + 59 (error handling) = **~202 lines removed**
**Estimated post-refactor**: 592 - 202 = **~390 lines** (within 300-400 target)

## Reference Document Design

### Frontmatter Standard

Each reference document includes minimal frontmatter:

```yaml
---
source_agent: "{agent-filename}"
loaded_at: "{pipeline phase or condition}"
extracted_from: "{description of original location}"
version: "1.0"
---
```

### Loading Instructions Pattern

Each refactored agent includes a loading instructions section:

```markdown
## Reference Documents

This agent loads reference documents on-demand at specific pipeline phases.
Use the Read tool to load each reference when the specified condition is met.

| Reference | Path | Load When |
|-----------|------|-----------|
| SARIF Generation | adapters/claude-code/agents/references/sarif-generation.md | Phase 4 completion (SARIF output generation) |
| Validation Checklist | adapters/claude-code/agents/references/validation-checklist.md | Pipeline end (final validation) |
| Error Templates | adapters/claude-code/agents/references/error-templates.md | Error condition encountered |

If any reference document is missing, STOP and report the error:
"ERROR: Required reference document not found: {path}"
```

### Self-Containment Rule

Each reference document is self-contained:
- No cross-references between reference documents
- All necessary context included within the document
- Can be loaded and used independently
- No dependency on other reference documents being loaded first

## Implementation Approach

### Wave 1: Preparation (Pre-requisite for all extraction)

1. Capture baseline regression output by running `/threat-model` on `examples/agentic-app/architecture.md`
2. Create capability inventory documenting all capabilities of the 3 target agents
3. Record byte checksums of all 11 threat agents and 2 infographic templates
4. Create `adapters/claude-code/agents/references/` directory

### Wave 2: Orchestrator Refactoring

1. Extract SARIF generation section (lines 1224-1718) to `references/sarif-generation.md`
2. Extract validation checklist (lines 1138-1223) to `references/validation-checklist.md`
3. Split error handling section — extract pure error templates (~100 lines) to `references/error-templates.md`; retain defensive specification content (error evaluation order, ambiguous DFD classification, non-conforming finding handling, three-state cell model) in core agent
4. Condense verbose prose (~200 lines scattered throughout)
5. Add loading instructions section to orchestrator
6. Verify line count target (~1,100-1,200)
7. Run regression test on orchestrator output

### Wave 3: Report + Infographic Refactoring (Parallel)

**Report agent** (can run in parallel with infographic):
1. Extract attack tree construction rules, Mermaid conventions, and example trees (lines 349-642) to `references/report-templates.md`
2. Condense prose in dual output location and remediation roadmap sections
3. Add loading instructions section
4. Verify line count target (~300-400)

**Infographic agent** (can run in parallel with report):
1. Extract Gemini API prompt construction + integration (lines 389-532) to `references/infographic-gemini-api.md`
2. Extract error handling & graceful degradation (lines 533-592) to `references/infographic-error-handling.md`
3. Add loading instructions section
4. Verify line count target (~300-400)

### Wave 4: Final Validation

1. Run end-to-end `/threat-model` on `examples/agentic-app/architecture.md` — compare output structure against baseline
2. Validate SARIF output against SARIF 2.1.0 schema structure
3. Verify all 11 threat agents are byte-identical (zero changes)
4. Verify both infographic templates are unchanged
5. Verify all schemas in `schemas/` are unchanged
6. Verify all reference documents load correctly via Read tool
7. Update capability inventory with post-refactoring verification results

## Risk Mitigations

| Risk | Mitigation |
|------|-----------|
| Extraction accidentally removes needed specification content | Preservation-first inventory before any changes; regression test after each wave |
| Reference document loading fails or is slow | Explicit error-on-missing handling; reference docs are small files (<500 lines) |
| Prose condensation removes context that aids instruction-following | Only remove clearly redundant narration; preserve all specification content; regression test |
| Error handling split misclassifies defensive spec as pure template | The PRD and research analysis provide clear categorization — error evaluation order, ambiguous DFD, non-conforming findings, and three-state cell model are defensive spec |

## Complexity Tracking

No constitution violations requiring justification. This is a straightforward content refactoring with no new architectural patterns, no external dependencies, and no API changes.
