# Architect Review: Feature 054 -- Security Assessment PDF Booklet

**Reviewer**: Architect
**Date**: 2026-03-28
**Status**: APPROVED_WITH_CONCERNS
**Findings**: 3 concerns (0 blocking, 2 moderate, 1 minor)

---

## Review Scope

Full architecture review of the implemented Feature 054 deliverables:
- Command file, agent file, schema, and 8 Typst templates
- Evaluated against: spec.md (23 FRs, 6 user stories), plan.md (4-phase design)
- Cross-referenced with existing tachi patterns (infographic command, risk-scorer agent, infographic schema)

---

## 1. Architecture Soundness -- PASS

The implementation achieves clean separation across four layers:

| Layer | File | Responsibility |
|-------|------|----------------|
| Entry point | `security-report.md` | Argument parsing, prerequisite validation, artifact detection, agent invocation |
| Orchestration | `report-assembler.md` | Data extraction, Typst data generation, compilation |
| Schema | `security-report.yaml` | Declarative page assembly rules, artifact mappings, tier definitions |
| Rendering | `templates/security-report/*.typ` | Visual output, page layout, design tokens |

**Strengths**:
- Command-to-agent boundary is well-defined. The command handles all user interaction (flags, detection reporting, error display). The agent handles all data transformation (parsing, extraction, data file generation). Neither crosses into the other's domain.
- The data injection pattern (`report-data.typ` as a generated intermediate) cleanly separates data extraction from rendering. The agent writes Typst variables; the templates consume them. No business logic in templates, no rendering logic in the agent.
- Schema-driven page assembly (`security-report.yaml`) makes the page sequence, artifact mappings, and tier definitions declarative. Future extensions (new page types, different orderings) modify the schema rather than command or agent logic.

**Architecture alignment**: Follows the same 4-step command pattern as `/infographic` (Parse -> Validate -> Generate -> Report). Agent metadata block mirrors `threat-infographic.md` structure. Schema follows the `schema_version` + domain-specific section convention established by `output.yaml`, `risk-scoring.yaml`, and `infographic.yaml`.

---

## 2. Data Flow Correctness -- PASS

The end-to-end data flow is sound:

```
User artifacts (markdown/JPEG)
  -> Command detects (Step 1)
  -> Agent parses (Step 2)
  -> Agent generates report-data.typ (Step 3)
  -> Typst compiles main.typ + report-data.typ + page templates (Step 4)
  -> security-report.pdf
  -> Agent cleans up report-data.typ
```

**Key validations**:

1. **Artifact detection matrix**: The 7-file detection in the command matches the schema's `artifacts` section exactly. Each artifact's `enables` list correctly maps to the page types it supports.

2. **3-tier data source preference**: Correctly implemented -- compensating-controls.md (tier 1) takes priority over risk-scores.md (tier 2), which takes priority over threats.md (tier 3). The tier selection in the command matches the agent's parsing logic and the schema's `data_source_tiers` definition.

3. **Variable contract**: The agent's Step 3 defines every variable that `main.typ` imports. The page function signatures in `main.typ` reference the correct variable names. No dangling references.

4. **Image path resolution**: The agent generates relative paths from `templates/security-report/` back to the target directory (`../../{target_dir}/filename.jpg`). This correctly accounts for Typst's path resolution behavior relative to the `.typ` file that calls `#image()`.

5. **Conditional page inclusion**: `main.typ` uses `#if` guards on boolean flags that match the agent's page inclusion flags. The remediation roadmap guard (`has-compensating-controls or (has-threat-report and remediation-actions != none and remediation-actions.len() > 0)`) correctly expresses the dual-source dependency.

---

## 3. Template Modularity -- PASS

Each `.typ` file is self-contained and follows a consistent pattern:

| File | Imports | Exports | Responsibility |
|------|---------|---------|----------------|
| `shared.typ` | (none) | Colors, fonts, geometry, header/footer | Design token authority |
| `cover.typ` | `shared.typ` | `cover-page()` | Cover page rendering |
| `executive-summary.typ` | `shared.typ` | `executive-summary-page()` | Executive summary with rich/minimal modes |
| `full-bleed.typ` | `shared.typ` | `full-bleed-page()` | Zero-margin infographic page |
| `findings-detail.typ` | `shared.typ` | `findings-detail-page()` | 3-tier severity table |
| `control-coverage.typ` | `shared.typ` | `control-coverage-page()` | STRIDE coverage matrix + controls |
| `remediation-roadmap.typ` | `shared.typ` | `remediation-roadmap-page()` | Grouped remediation actions |
| `main.typ` | All of the above + `report-data.typ` | (document) | Page orchestration |

**Strengths**:
- Single export per page template. Each file exports exactly one function. No inter-template dependencies.
- `shared.typ` is the sole design authority. All colors, fonts, and geometry constants are defined once and imported by all pages. No hardcoded values in page templates.
- Internal helpers are prefixed with `_` (e.g., `_severity-row`, `_status-colors`, `_group-by-severity`) to distinguish them from exported functions.
- Every page template handles its own empty state (no findings, no controls, no actions) gracefully.

---

## 4. Graceful Degradation -- PASS

Degradation is correctly implemented at every level:

| Level | Mechanism | Validated |
|-------|-----------|-----------|
| **Command** | Requires `threats.md`; all others optional | FR-002 |
| **Agent** | Per-artifact parsing with fallback on failure | Agent error handling rules |
| **main.typ** | `#if` guards on boolean flags | All conditional pages |
| **findings-detail.typ** | 3-tier config selection based on `data-source-tier` | Tier 1/2/3 column sets |
| **executive-summary.typ** | Rich mode (narrative) vs. minimal mode (counts only) | Auto-detected |
| **remediation-roadmap.typ** | Empty state message when no actions | `actions.len() == 0` guard |
| **control-coverage.typ** | Empty controls table guard | `controls.len() == 0` early return |

The spec's five artifact combinations (threats-only; threats+risk-scores; threats+risk-scores+controls; any+infographics; v1.0 schema) are all correctly handled by the tiered conditional logic.

---

## 5. Pattern Adherence -- PASS

Cross-checked against existing tachi patterns:

| Pattern | Reference | 054 Implementation | Match |
|---------|-----------|---------------------|-------|
| Command structure | `infographic.md` | Step 0 (parse) -> Step 1 (validate+detect) -> Step 2 (generate) -> Step 3 (report) | Yes |
| Agent metadata | `threat-infographic.md` | YAML frontmatter with `category`, `input_schemas`, `output_files`, `references` | Yes |
| Schema format | `infographic.yaml` | `schema_version: "1.0"`, domain section, structured sub-sections | Yes |
| Flag conventions | `infographic.md` `--output-dir` | Same flag name and behavior | Yes |
| Agent invocation | `infographic.md` Step 2 | `subagent_type: "senior-backend-engineer"` pattern | Yes |
| Error messages | `infographic.md` prerequisite check | Same pattern: named dependency + platform install instructions | Yes |

---

## 6. Image Path Resolution -- PASS (with concern)

The agent generates paths relative to `templates/security-report/`:

```typst
#let funnel-image-path = "../../{target_dir}/threat-risk-funnel.jpg"
```

This is correct for the standard case where `target_dir` is a relative path from the project root. The `--root .` flag in the `typst compile` invocation ensures Typst's root directory matches the project root, and the `../../` prefix navigates from `templates/security-report/` back to the project root.

**Concern C-1 (Moderate)**: See findings below for the absolute path edge case.

---

## Findings

### C-1 (Moderate): Intermediate file not in `.gitignore`

`report-data.typ` is a runtime-generated intermediate file written to `templates/security-report/report-data.typ`. The agent cleans it up after successful compilation (Step 4d), but on compilation failure it is preserved for debugging (Step 4b). If a user commits after a failed compilation (or interrupts the process), this file could be accidentally committed.

The `.gitignore` has no entry for `report-data.typ` or `*.typ` intermediates.

**Recommendation**: Add `templates/security-report/report-data.typ` to `.gitignore`. This is a hygiene issue -- the file contains extracted data from the user's threat model artifacts and should not be version-controlled.

**Severity**: Moderate -- accidental commit of extracted security assessment data is a data hygiene risk. Not blocking because the agent documents the cleanup lifecycle and the file is project-local.

---

### C-2 (Moderate): Image path resolution with absolute target directory paths

The agent's Step 3f constructs image paths as:

```typst
#let funnel-image-path = "../../{target_dir}/threat-risk-funnel.jpg"
```

This works when `target_dir` is a relative path (e.g., `examples/sample-project/`). However, if the user invokes `/security-report /absolute/path/to/artifacts/`, the generated path becomes `../..//absolute/path/to/artifacts/threat-risk-funnel.jpg`, which is invalid. The `../../` prefix conflicts with the absolute path.

The command file's Step 0 does not normalize the target directory to a relative path. The agent documentation does not address this edge case.

**Recommendation**: The agent should detect whether `target_dir` is absolute. If absolute, omit the `../../` prefix and use the absolute path directly. If relative, prepend `../../` as currently documented. Add a note in the agent's Step 3f documenting this logic.

**Severity**: Moderate -- absolute paths are a plausible user input pattern (`/security-report /Users/david/projects/my-app/threat-output/`). The resulting Typst compilation would fail with a "file not found" error for images, but text pages would still render. The error message from Step 4b would help debugging, but the root cause would not be obvious.

---

### C-3 (Minor): Page counter resets not suppressed on full-bleed pages

The `full-bleed.typ` template suppresses header and footer (correct for full-bleed rendering), but `main.typ` uses Typst's default page counter which increments on every `#page()` call. The full-bleed pages consume page numbers (e.g., page 3, 4, 5 for infographics) even though they display no page number.

This means the visible "Page N" numbers on text pages will have gaps (e.g., Cover=none, Executive Summary=Page 2, Risk Funnel=no footer, Baseball Card=no footer, System Architecture=no footer, Findings Detail=Page 6). This is cosmetically acceptable -- the total page count is correct and the page numbers in a PDF viewer match the footer numbers -- but it means the footer numbering does not represent "text page 1 of N text pages."

**Recommendation**: No code change needed. This is standard PDF behavior (infographic pages are real pages in the document). Document this in the template README for clarity: "Page numbers reflect the PDF page index. Full-bleed pages are counted but do not display page numbers."

**Severity**: Minor -- purely cosmetic. The PDF viewer's page numbers match the footer numbers, which is the expected behavior for a mixed-orientation document.

---

## Items Not Flagged (Positive Observations)

1. **Multi-page table overflow**: Both `findings-detail.typ` and `remediation-roadmap.typ` use `table.header(repeat: true)` for header repetition on continuation pages. This addresses the spec's edge case for oversized findings tables.

2. **Severity color consistency**: All four severity colors are defined once in `shared.typ` and used consistently across all 6 page templates. The `severity-color()` function provides case-insensitive lookup with a gray fallback for unknown values.

3. **Empty state handling**: Every conditional component handles the empty case: empty findings array shows "No findings to display", empty controls array returns early, empty actions array shows a styled placeholder. No runtime errors from empty data.

4. **Classification marking propagation**: The `classification` variable flows from `report-data.typ` through `main.typ` to every page that accepts it. The cover page handles it with a top-of-page banner; text pages handle it through `report-header()`. Full-bleed pages correctly omit it (they have no chrome).

5. **Schema-spec alignment**: All 8 page types in the schema match the 8 page types in the spec. The 3-tier column definitions in the schema match the 3-tier column definitions in `findings-detail.typ`. The `custom-16x9` dimensions (11in x 6.1875in) match between the schema, `full-bleed.typ`, and the spec.

6. **Typst version handling**: The README documents tested version (0.14.2) with compatibility note (0.11.x+). No deprecated Typst APIs are used. Font fallback chains ensure cross-platform rendering.

---

## Architecture Decision Validation

| Plan Decision | Implementation | Correct |
|---------------|---------------|---------|
| Typst for PDF rendering | All templates use Typst; `typst compile` invoked by agent | Yes |
| Data injection via generated `.typ` file | `report-data.typ` generated by agent, imported by `main.typ` | Yes |
| One `.typ` file per page type | 6 page files + 1 shared + 1 orchestrator = 8 files | Yes |
| `#if` guards for conditional pages | `main.typ` lines 90-154 | Yes |
| Custom page dimensions for 16:9 | `full-bleed.typ` uses `11in x 6.1875in` with `0in` margins | Yes |
| Shared styles single source | `shared.typ` imported by all page templates | Yes |
| Schema-driven assembly | `security-report.yaml` defines artifact matrix, page sequence, tiers | Yes |
| 4-step command pattern | Command implements Parse -> Validate+Detect -> Generate -> Report | Yes |

---

## Verdict

**APPROVED_WITH_CONCERNS**

The architecture is sound. Clean layer separation, correct data flow, faithful pattern adherence, comprehensive graceful degradation, and well-structured Typst templates. The two moderate concerns (`.gitignore` hygiene and absolute path edge case) are non-blocking and can be addressed as incremental improvements. The minor concern (page counter behavior on full-bleed pages) requires no code change, only documentation.

All 23 functional requirements from the spec are architecturally addressed. The implementation matches the approved plan's component design, data flow, and tech stack decisions.
