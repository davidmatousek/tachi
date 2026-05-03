---
triad:
  pm_signoff:
    agent: product-manager
    date: 2026-04-09
    status: APPROVED
    notes: "All 4 user stories covered, all 15 FRs traceable to tasks, zero scope creep, traceability table accurate."
  architect_signoff:
    agent: architect
    date: 2026-04-09
    status: APPROVED_WITH_CONCERNS
    notes: "Architecturally sound. Medium concerns: (C-1) detect_artifacts() return pattern should use boolean+path pair consistent with existing pattern, (C-2) Mermaid narrative parsing should use node naming convention not shape syntax. Low concerns noted for implementation."
  techlead_signoff:
    agent: team-lead
    date: 2026-04-09
    status: APPROVED
    notes: "18 tasks across 7 waves, critical path well-defined, 1 sprint feasible. Agent assignments generated."
---

# Tasks: Attack Path Pages in Security Report PDF

**Input**: Design documents from `/specs/112-attack-path-pages/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md

**Tests**: Not requested in spec. Manual validation against 6 example outputs.

**Organization**: Tasks are grouped by pipeline layer to enable parallel work on independent files, with user story traceability via [US] labels.

## Phase 1: Foundational — Artifact Detection & Parsing

**Purpose**: Extend the shared parser and extraction script with attack tree detection and parsing. MUST complete before Typst template work can be validated end-to-end.

- [X] T001 [P] Update `detect_artifacts()` to detect `attack-trees/` directory in `scripts/tachi_parsers.py`
- [X] T002 [P] Implement `parse_attack_trees()` function to extract metadata and Mermaid code from `attack-trees/*.md` files in `scripts/extract-report-data.py`
- [X] T003 Implement `render_mermaid_to_png()` function for Mermaid-to-PNG conversion via `mmdc` subprocess in `scripts/extract-report-data.py`
- [X] T004 Implement narrative construction and remediation text splitting in `parse_attack_trees()` in `scripts/extract-report-data.py`
- [X] T005 Add attack tree data binding section to `format_report_data()` output in `scripts/extract-report-data.py`

**Details**:

**T001** — `scripts/tachi_parsers.py`:
- Add `attack-trees/` directory detection to `detect_artifacts()` return dict
- Return `has_attack_trees: bool` and `attack_trees_dir: str` (path or empty)
- Detection: check if `os.path.isdir(os.path.join(target_dir, "attack-trees"))` and contains at least one `*-attack-tree.md` file

**T002** — `scripts/extract-report-data.py`, new function `parse_attack_trees(target_dir, findings)`:
- Scan `{target_dir}/attack-trees/` for `*-attack-tree.md` files (primary source)
- If no standalone files: fall back to inline trees in `threat-report.md` Section 5 (extract Mermaid blocks between `## Attack Tree: {ID}` headers)
- For each file: parse metadata table (Finding ID, Component, Risk Level, Threat) using `parse_markdown_table()` from `tachi_parsers`
- Extract Mermaid code block (content between triple-backtick mermaid fences)
- Cross-reference finding ID with `findings` list to get authoritative severity and mitigation text
- Filter to Critical and High severity only
- Sort: Critical first, then High; within same severity, sort by finding ID (case-insensitive)
- Return list of dicts: `{id, component, severity, title, mermaid_code, mitigation}`
- Covers FR-001, FR-002, FR-003, FR-004, FR-008

**T003** — `scripts/extract-report-data.py`, new function `render_mermaid_to_png(attack_trees, target_dir)`:
- Check `mmdc` availability via `shutil.which("mmdc")`
- If unavailable: log warning, set `has_image = False` for all entries, return early
- Create `tempfile.TemporaryDirectory()` context manager
- For each entry: write `{id}.mmd` file with Mermaid code, invoke `subprocess.run(["mmdc", "-i", mmd_path, "-o", png_path, "-s", "2", "-b", "transparent"], capture_output=True, timeout=30)`
- On success: copy PNG to `{target_dir}/attack-trees/{id}-attack-tree.png`, set `has_image = True`, `image_path` = relative path from template dir
- On failure (CalledProcessError or timeout): log warning with stderr, set `has_image = False`
- Temp directory auto-cleaned on context manager exit
- Covers FR-005, FR-006

**T004** — In `parse_attack_trees()` (or helper), after T002:
- **Narrative**: Parse Mermaid code to extract root node label, OR/AND gate structure, sub-goal labels, and leaf node labels. Construct 2-4 sentence narrative: "An attacker targets {component} by attempting to {root_label}. The attack proceeds through {sub-goal descriptions}, requiring {AND: all of / OR: any of} {leaf actions}."
- **Remediation**: Take mitigation text from cross-referenced finding, split at sentence boundaries (`. `) or semicolons (`;`), return as list of strings for bulleted display
- Store in each entry dict: `narrative` (str), `remediation` (list of str)

**T005** — In `format_report_data()`, after MAESTRO data section:
- Add comment: `// --- Attack Tree Data ---`
- Write `#let has-attack-trees = {true|false}`
- If attack trees exist, write `#let attack-trees = (` array of dicts with keys: `id`, `component`, `severity`, `title`, `image-path`, `has-image`, `mermaid-text`, `narrative`, `remediation`
- `remediation` formatted as Typst array of strings: `("step 1", "step 2", ...)`
- `mermaid-text` escaped via `escape_typst_string()`
- If no attack trees: write `#let attack-trees = ()`
- Covers FR-007, FR-008

**Checkpoint**: Extraction pipeline complete. Running `python3 scripts/extract-report-data.py --target-dir examples/agentic-app/sample-report/ --output /tmp/test-data.typ` should produce attack tree variables in output.

---

## Phase 2: US1+US2+US3 — Attack Path Page Template (P1)

**Goal**: Create the Typst page template that renders each attack path as a portrait page with severity badge, diagram, narrative, and remediation. Includes ordering (US2) via data from Phase 1 and image/text fallback (US3).

**Independent Test**: Compile a test PDF with sample attack tree data in `report-data.typ`. Verify pages render with correct layout, severity colors, and diagram display.

- [X] T006 [P] [US1] Create attack path page template in `templates/tachi/security-report/attack-path.typ`
- [X] T007 [US1] Update main orchestrator with import, defaults, and page sequencing in `templates/tachi/security-report/main.typ`

**Details**:

**T006** — New file `templates/tachi/security-report/attack-path.typ`:
- Import `shared.typ` (severity-color, report-header, report-footer, fonts, page geometry)
- Export single function: `attack-path-page(entry: (:), classification: none)`
- **Severity badge helper** `_attack-severity-badge(level)`: Reuse pattern from `maestro-findings.typ:_severity-badge()` — `box(fill: severity-color(level), radius: 3pt, ...)` with finding ID text
- **Layout** (portrait, US Letter):
  1. `report-header(classification: classification, title: "Attack Path Analysis")`
  2. Heading: severity badge + finding title (e.g., `[CRITICAL] E-3 — Administrative Tool Access via Parameter Manipulation`)
  3. Diagram section (~60% page height): `if entry.at("has-image") { image(entry.at("image-path"), width: 100%) } else { raw(entry.at("mermaid-text"), lang: "mermaid") }` — scale image to fit with `fit: "contain"`
  4. Narrative section: `text(size: 10pt)[#{entry.at("narrative")}]`
  5. Remediation section: heading "Remediation Steps" + bulleted list from `entry.at("remediation")` array
- Covers FR-009, FR-013

**T007** — Modify `templates/tachi/security-report/main.typ`:
1. Add import after `remediation-roadmap.typ` import line: `#import "attack-path.typ": attack-path-page`
2. Add backward-compatible defaults after MAESTRO defaults block:
   ```typst
   #let has-attack-trees = if has-attack-trees != none { has-attack-trees } else { false }
   #let attack-trees = if attack-trees != none { attack-trees } else { () }
   ```
3. Insert conditional block after Executive Summary page (after line ~187, before Risk Reduction Funnel):
   ```typst
   #if has-attack-trees and attack-trees.len() > 0 {
     section-divider("Attack Path Analysis", classification: classification)
     for entry in attack-trees {
       page(width: page-width, height: page-height,
         margin: (top: margin-top, bottom: margin-bottom, left: margin-left, right: margin-right),
         footer: report-footer(),
       )[#attack-path-page(entry: entry, classification: classification)]
     }
   }
   ```
- Covers FR-010, FR-011, FR-012, FR-014 (TOC auto-generated from headings)

**Checkpoint**: Full pipeline testable. Run extraction + Typst compile on `examples/agentic-app/sample-report/` and verify attack path pages appear in PDF.

---

## Phase 3: US4 — Section Header and TOC Integration (P2)

**Goal**: Section divider page and TOC entry for the Attack Path Analysis section.

**Independent Test**: Generate PDF, verify "Attack Path Analysis" appears in TOC and as a section divider page.

Note: The section divider call is already included in T007. This phase validates it works correctly.

- [X] T008 [US4] Verify section divider and TOC integration by compiling sample report and checking page sequence in `templates/tachi/security-report/main.typ`

**Details**:

**T008** — Validation task:
- Compile `examples/agentic-app/sample-report/` through full pipeline
- Verify: (1) "Attack Path Analysis" section divider page appears after Executive Summary, (2) TOC includes "Attack Path Analysis" entry, (3) page numbering is continuous, (4) when no attack trees exist the section is completely absent
- Covers FR-011, FR-014

**Checkpoint**: Section header and TOC confirmed working.

---

## Phase 4: Artifact Detection Updates

**Purpose**: Update command documentation and agent instructions to detect attack tree artifacts.

- [X] T009 [P] Update artifact detection table in `.claude/commands/security-report.md`
- [X] T010 [P] Update artifact detection in `.claude/agents/tachi/report-assembler.md`

**Details**:

**T009** — `.claude/commands/security-report.md`:
- Add row to artifact detection table: `| Attack Trees | attack-trees/*.md | optional | Attack Path pages (portrait) |`
- Add `attack-trees/ ................. {FOUND (N files) | not found}` to detection display
- Add `{if attack-trees found: "N. Attack Path Analysis ...... portrait (US Letter)"}` to page listing (after Executive Summary)

**T010** — `.claude/agents/tachi/report-assembler.md`:
- Add `attack-trees/` to artifact detection step
- Document that extraction script auto-detects the directory (no separate flag needed)
- Add attack path pages to page sequence description

**Checkpoint**: Command and agent documentation updated.

---

## Phase 5: Polish & Cross-Cutting Concerns

**Purpose**: Regenerate example outputs, update project documentation, backward compatibility validation.

- [X] T011 [P] Regenerate `examples/agentic-app/sample-report/` security report with attack path pages
- [X] T012 [P] Regenerate `examples/cloud-native/sample-report/` security report
- [X] T013 [P] Regenerate `examples/data-pipeline/sample-report/` security report
- [X] T014 [P] Regenerate `examples/healthcare-ai/sample-report/` security report
- [X] T015 [P] Regenerate `examples/iot-fleet/sample-report/` security report
- [X] T016 [P] Regenerate `examples/rag-chatbot/sample-report/` security report
- [X] T017 Update Feature 112 entry in Recent Changes section of `CLAUDE.md`
- [X] T018 Backward compatibility validation — compile a report with no `attack-trees/` directory and verify identical output to pre-feature baseline

**Details**:

**T011-T016**: For each example:
- Run extraction script: `python3 scripts/extract-report-data.py --target-dir {example}/sample-report/ --output templates/tachi/security-report/report-data.typ --template-dir templates/tachi/security-report/`
- Compile: `typst compile templates/tachi/security-report/main.typ {example}/sample-report/security-report.pdf --root .`
- Verify: attack path pages present for examples with `attack-trees/` directory, absent for those without

**T017**: Add to CLAUDE.md `## Recent Changes`:
- Feature 112: Attack Path Pages in Security Report PDF
- New files: `attack-path.typ`, `parse_attack_trees()`, `render_mermaid_to_png()`
- Updated files: `main.typ`, `extract-report-data.py`, `tachi_parsers.py`, `security-report.md`, `report-assembler.md`

**T018**: Backward compatibility — use an example without `attack-trees/` directory (or temporarily rename it). Verify:
- No attack path pages appear
- No errors or warnings
- All existing pages render correctly
- PDF is byte-identical to pre-feature output (same report-data.typ → same PDF)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Foundational)**: No dependencies — can start immediately
  - T001, T002 can run in parallel (different files)
  - T003, T004 depend on T002 (need parsed tree structure)
  - T005 depends on T002, T003, T004 (needs all extraction data)
- **Phase 2 (Template)**: T006 can start in parallel with Phase 1 (different file). T007 depends on T006.
- **Phase 3 (Validation)**: Depends on Phase 1 + Phase 2 (needs full pipeline)
- **Phase 4 (Detection)**: No code dependencies — can run in parallel with Phase 2 or 3
- **Phase 5 (Polish)**: Depends on Phase 1, 2, 3 completion (needs working pipeline)
  - T011-T016 can all run in parallel
  - T017 can run in parallel with T011-T016
  - T018 depends on T011-T016 (needs baseline comparison)

### Critical Path

T002 → T003/T004 → T005 → T007 → T008 → T011-T016 → T018

### User Story Traceability

| User Story | Tasks | FRs Covered |
|-----------|-------|-------------|
| US1 (P1) | T002, T004, T005, T006, T007 | FR-001 to FR-004, FR-007 to FR-010, FR-012, FR-013 |
| US2 (P1) | T002, T005 | FR-004, FR-008 |
| US3 (P1) | T003, T006 | FR-005, FR-006 |
| US4 (P2) | T007, T008 | FR-010, FR-011, FR-014 |
| Backward compat | T001, T005, T007, T018 | FR-012, FR-015 |

### Parallel Opportunities

**Wave 1** (no dependencies):
- T001: tachi_parsers.py artifact detection
- T002: parse_attack_trees() in extract-report-data.py
- T006: attack-path.typ template (independent file)
- T009: security-report.md update
- T010: report-assembler.md update

**Wave 2** (depends on T002):
- T003: render_mermaid_to_png()
- T004: narrative/remediation text logic

**Wave 3** (depends on T003, T004):
- T005: report-data.typ output binding

**Wave 4** (depends on T005, T006):
- T007: main.typ orchestrator update

**Wave 5** (depends on T007):
- T008: section divider + TOC validation

**Wave 6** (depends on T008):
- T011-T016: example regeneration (all parallel)
- T017: CLAUDE.md update

**Wave 7** (depends on T011-T016):
- T018: backward compatibility validation

---

## Implementation Strategy

### MVP First (US1 + US2 + US3)

1. Complete Phase 1: Extraction pipeline (T001-T005)
2. Complete Phase 2: Typst template + orchestrator (T006-T007)
3. **VALIDATE**: Compile agentic-app example, verify attack path pages in PDF
4. This delivers all P1 user stories — core feature is shippable

### Incremental Delivery

1. Phase 1 + Phase 2 → Core pipeline working (MVP)
2. Phase 3 → Section header/TOC validated (P2 complete)
3. Phase 4 → Documentation updated
4. Phase 5 → All examples regenerated, backward compatibility confirmed

---

## Notes

- [P] tasks = different files, no dependencies
- T006 can be developed in parallel with Phase 1 since it's a standalone .typ file
- All 18 tasks target 5 existing files + 1 new file — minimal blast radius
- No new schemas, no new dependencies beyond optional `mmdc`
- Graceful degradation: entire feature is invisible when attack trees are absent
