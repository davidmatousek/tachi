# Code Review: Feature 054 — Security Assessment PDF Booklet

**Reviewer**: code-reviewer
**Date**: 2026-03-28
**Branch**: `054-security-assessment-pdf`
**Verdict**: APPROVED_WITH_CONCERNS

---

## Review Scope

| File | Type | Lines |
|------|------|-------|
| `.claude/commands/security-report.md` | Command file (new) | 231 |
| `.claude/agents/tachi/report-assembler.md` | Agent file (new) | 567 |
| `schemas/security-report.yaml` | Schema file (new) | 117 |
| `templates/security-report/main.typ` | Typst orchestrator (new) | 155 |
| `templates/security-report/shared.typ` | Typst shared styles (new) | 209 |
| `templates/security-report/cover.typ` | Typst cover page (new) | 232 |
| `templates/security-report/executive-summary.typ` | Typst exec summary (new) | 297 |
| `templates/security-report/full-bleed.typ` | Typst full-bleed page (new) | 45 |
| `templates/security-report/findings-detail.typ` | Typst findings table (new) | 199 |
| `templates/security-report/control-coverage.typ` | Typst control coverage (new) | 432 |
| `templates/security-report/remediation-roadmap.typ` | Typst remediation page (new) | 361 |
| `templates/security-report/README.md` | Template documentation (new) | 75 |
| `templates/README.md` | Root templates README (modified) | 30 |
| `docs/architecture/01_system_design/README.md` | System design (modified) | +79 lines |
| `docs/product/02_PRD/INDEX.md` | PRD index (modified) | +1 line |
| `docs/product/_backlog/BACKLOG.md` | Backlog (modified) | moved entry |

---

## Summary

Feature 054 delivers a complete `/security-report` command that assembles tachi pipeline artifacts into a professional PDF booklet via Typst. The implementation is well-structured, follows established tachi patterns closely, and demonstrates strong attention to detail in the Typst template design. The command file mirrors the 4-step pattern from `/infographic`, the agent file provides thorough step-by-step extraction instructions with a complete data contract, and the Typst templates are modular with consistent shared styles.

Overall quality is high. I found 0 critical issues, 4 warnings, and 5 suggestions.

---

## Findings

### WARNINGS (4)

#### W-001: Agent references Section 7 for Tier 3 findings but also references Section 7 as "Recommended Actions" inconsistently with Section 2 references elsewhere

**File**: `/Users/david/Projects/tachi/.claude/agents/tachi/report-assembler.md`, lines 88-89 and 136-156
**Issue**: Step 1b references `threats.md Section 7` for Tier 3 findings, and Step 2b heading says "Parse threats.md Section 7 for Tier 3 Findings". However, the threats.md schema (`schemas/output.yaml`) defines Section 7 as "Recommended Actions". The agent instructions use Section 7 consistently but the column mapping in Step 2b defines `likelihood` and `impact` columns with em-dash fallback values since Section 7 does not contain those columns. This creates a data mismatch: the Tier 3 column configuration in both the schema (`schemas/security-report.yaml`, line 93) and `findings-detail.typ` (line 52) expects `likelihood` and `impact` columns, but the agent will always produce em-dash values for those fields.
**Impact**: Tier 3 PDF output will display two columns ("Likelihood" and "Impact") that always contain em-dashes, which is visually confusing and wastes table space. Users seeing a Tier 3 report get 7 columns where 2 are always blank.
**Fix**: Either (a) reduce Tier 3 to 5 columns (ID, Component, Threat, Risk Level, Mitigation) by updating the schema, agent, and `findings-detail.typ`, or (b) document in the agent that the em-dash columns are intentional placeholders for parity with Tier 1/2 column counts.

---

#### W-002: Findings Detail page rendering pattern differs from other text pages — may cause header/footer inconsistency

**File**: `/Users/david/Projects/tachi/templates/security-report/main.typ`, lines 111-131
**Issue**: The Findings Detail page is wrapped in an explicit `#page(...)[]` block in `main.typ` with `footer: report-footer()` but no `header` parameter, relying on `findings-detail-page` to call `report-header()` inline (line 95 of findings-detail.typ). All other text pages (executive-summary, control-coverage, remediation-roadmap) set both `header` and `footer` parameters on their own `page()` calls. This asymmetric pattern means the Findings Detail page header is rendered as content within the page body rather than as a page-level header, which may cause layout differences (e.g., the header content pushes the table down by a different amount than page-level headers on other pages, and the header will not repeat on continuation pages when the findings table overflows to multiple pages).
**Impact**: On multi-page findings tables (oversized findings sets per spec edge case), the classification bar and page title will appear only on the first page, not on continuation pages. Other pages have these in the `header` parameter which Typst automatically repeats.
**Fix**: Refactor `findings-detail-page` to use the same self-contained `page()` wrapper pattern as `control-coverage-page` and `remediation-roadmap-page`, setting `header: report-header(...)` as a page parameter rather than inline content. This would require `findings-detail-page` to manage its own `page()` block.

---

#### W-003: Remediation roadmap condition in main.typ does not fully match agent data generation logic

**File**: `/Users/david/Projects/tachi/templates/security-report/main.typ`, line 149
**Issue**: The remediation roadmap page inclusion guard is:
```
#if has-compensating-controls or (has-threat-report and remediation-actions != none and remediation-actions.len() > 0)
```
This checks `has-compensating-controls` as a boolean (without checking whether `remediation-actions` has data from compensating-controls). Meanwhile, the agent (report-assembler.md lines 462-466) may set `remediation-actions = none` if compensating-controls.md Section 3 has no recommendations AND threat-report.md has no remediation timeline. So if `has-compensating-controls` is true but the controls file has no Section 3 recommendations, the remediation roadmap page would be included with `remediation-actions = none`, which would hit the empty-state rendering in `remediation-roadmap.typ` (line 242).
**Impact**: Users with compensating-controls.md that lacks a Section 3 recommendations section would see a remediation roadmap page that just says "No remediation actions identified." This is not broken (the empty state renders gracefully), but it adds a blank-looking page that may confuse stakeholders.
**Fix**: Tighten the condition in main.typ to:
```
#if remediation-actions != none and remediation-actions.len() > 0
```
This way the page is only included when there is actual remediation data, regardless of source.

---

#### W-004: The `report-data.typ` intermediate file is generated inside the tracked `templates/security-report/` directory

**File**: `/Users/david/Projects/tachi/.claude/agents/tachi/report-assembler.md`, lines 288, 470
**Issue**: The agent writes `report-data.typ` to `templates/security-report/report-data.typ`, which is inside a tracked directory. While the agent cleans up the file after successful compilation (Step 4d), if compilation fails the file is intentionally preserved for debugging (Step 4b, line 509). A `.gitignore` entry for this intermediate file is not present, creating risk of accidental commit.
**Impact**: If an agent run fails or the user interrupts the process, `report-data.typ` (containing extracted assessment data) could be accidentally committed and pushed. This is a content safety concern since the file may contain sensitive finding details.
**Fix**: Add `templates/security-report/report-data.typ` to `.gitignore`. This was noted in the architect's review concerns ("intermediate file path strategy") but has not been addressed in the implementation.

---

### SUGGESTIONS (5)

#### S-001: Schema file lacks `repeat_header` property for tables that overflow to multiple pages

**File**: `/Users/david/Projects/tachi/schemas/security-report.yaml`
**Issue**: The schema defines page types and dimensions but does not declare whether tables should repeat headers on overflow pages. The Typst templates implement this via `repeat: true` on `table.header()`, but the schema (which the plan says "drives conditional page inclusion") could also declare this behavior for documentation completeness.
**Impact**: Minor documentation gap. The Typst templates correctly implement header repetition independent of the schema.
**Fix**: Optionally add a `table_overflow: repeat_headers` property to the `findings-detail` and `remediation-roadmap` page entries in the schema.

---

#### S-002: Cover page classification banner positioning uses negative margin offset

**File**: `/Users/david/Projects/tachi/templates/security-report/cover.typ`, line 82
**Issue**: The classification banner uses `dy: -margin-top + 0.0in` to position itself at the absolute top of the page, above the margin. This works but is fragile — if `margin-top` changes in `shared.typ`, this placement might not adapt correctly since it hard-codes an offset relationship.
**Impact**: Low risk since margin values are stable constants. But the pattern is less robust than, for example, using a page-level header parameter.
**Fix**: Consider using the `header` parameter on the cover page's `page()` call for the classification bar placement, similar to how other pages use `report-header()`. Alternatively, document the offset relationship with a comment referencing `shared.typ`.

---

#### S-003: The `_group-by-severity` function in remediation-roadmap.typ initializes an unused `groups` variable

**File**: `/Users/david/Projects/tachi/templates/security-report/remediation-roadmap.typ`, lines 54-58
**Issue**: The function declares `let groups = (("Critical", ()), ("High", ()), ("Medium", ()), ("Low", ()),)` at line 54-58 but never uses this variable. Instead it creates separate `critical`, `high`, `medium`, `low`, `other` arrays (lines 62-66) and builds the result from those. The `groups` binding is dead code.
**Impact**: No functional impact. Dead code that slightly clutters readability.
**Fix**: Remove lines 53-58 (the `let groups = ...` declaration).

---

#### S-004: The command file "Overview" section appears after Step 0 rather than before it

**File**: `/Users/david/Projects/tachi/.claude/commands/security-report.md`, lines 28-36
**Issue**: The "Overview" section (lines 28-36) appears between Step 0 and Step 1. In the `/infographic` command (the reference pattern), the Overview appears before Step 0. This is a minor structural difference from the established pattern.
**Impact**: No functional impact. The command executes correctly regardless of section ordering.
**Fix**: Move the Overview section to appear before Step 0 to match the `/infographic` command pattern.

---

#### S-005: Templates README lists Typst version "0.14.2" but plan.md specifies "0.11.x-0.12.x" compatibility range

**File**: `/Users/david/Projects/tachi/templates/security-report/README.md`, line 56
**Issue**: The README states "Tested with Typst 0.14.2. Should work with 0.11.x+." The plan.md (line 28) specifies the compatibility range as "0.11.x-0.12.x". The README suggests a broader working range (0.11.x+) while also documenting a tested version (0.14.2) that is outside the plan's stated range.
**Impact**: Minor version documentation inconsistency. The broader range in the README is likely more accurate if testing was done with 0.14.2, but it contradicts the plan's narrower specification.
**Fix**: Align the README with the actual tested range. If 0.14.2 works, update the plan's compatibility statement or note that it was tested beyond the original target range.

---

## Pattern Compliance Assessment

### Command File (security-report.md)

| Criterion | Status | Notes |
|-----------|--------|-------|
| 4-step pattern (Parse/Validate/Generate/Report) | PASS | Steps 0-3 match the infographic command pattern |
| `$ARGUMENTS` handling | PASS | Flags parsed with strip, remaining args as target dir |
| `--output-dir` flag | PASS | Follows `/infographic` convention |
| `--title` flag | PASS | New flag specific to this command, cleanly implemented |
| Prerequisite validation | PASS | Typst check with platform-specific instructions |
| Agent invocation | PASS | Uses `subagent_type: "senior-backend-engineer"` |
| Detection matrix display | PASS | Clear artifact-by-artifact detection table |
| Error messages | PASS | Specific, actionable, with file paths and next steps |
| Quality checklist | PASS | 11-item checklist covering all functional paths |

### Agent File (report-assembler.md)

| Criterion | Status | Notes |
|-----------|--------|-------|
| YAML frontmatter metadata | PASS | Name, description, category, schemas |
| Step-by-step instructions | PASS | 4 steps with lettered sub-steps |
| Data contract documentation | PASS | Full Typst variable binding specification |
| Input/output schema references | PASS | References all relevant schemas |
| Error handling | PASS | Graceful degradation rules, schema version handling |
| String escaping guidance | PASS | Explicit escape instructions for quotes and backslashes |

### Schema File (security-report.yaml)

| Criterion | Status | Notes |
|-----------|--------|-------|
| Schema version field | PASS | `schema_version: "1.0"` |
| Header comment block | PASS | Producers/Consumers/Version format matches existing schemas |
| Artifact detection matrix | PASS | 7 entries with required/optional and enables |
| Page sequence | PASS | 8 page types in correct order |
| Data source tiers | PASS | 3 tiers with source and column definitions |
| Page dimensions | PASS | US Letter + custom 16:9 |

### Typst Templates

| Criterion | Status | Notes |
|-----------|--------|-------|
| `shared.typ` single source of truth | PASS | All design tokens centralized |
| Severity color palette matches spec | PASS | DC2626, F97316, EAB308, 4169E1 |
| Page modules import shared.typ | PASS | All 6 page templates import shared.typ |
| Conditional page inclusion | PASS | `#if` guards in main.typ |
| Full-bleed 16:9 rendering | PASS | 11in x 6.1875in, zero margins, fit: "cover" |
| Header/footer consistency | PARTIAL | W-002: findings-detail uses inline header |
| Multi-page table headers | PARTIAL | W-002: findings-detail repeat may not work for header |
| Empty state handling | PASS | findings-detail and remediation-roadmap handle empty |
| Typography pairing | PASS | Sans-serif headings, serif body, mono tables |

### Naming Conventions

| Criterion | Status | Notes |
|-----------|--------|-------|
| Command file: kebab-case | PASS | `security-report.md` |
| Agent file: kebab-case | PASS | `report-assembler.md` |
| Schema file: kebab-case | PASS | `security-report.yaml` |
| Template files: kebab-case | PASS | All `.typ` files are kebab-case |
| Template directory: kebab-case | PASS | `templates/security-report/` |

### Documentation

| Criterion | Status | Notes |
|-----------|--------|-------|
| Template README accurate | PASS | File inventory, data contract, color palette documented |
| Root README updated | PASS | Rendering vs Reference distinction clearly made |
| System design updated | PASS | Components and data flow diagram added |
| PRD INDEX updated | PASS | Feature 054 entry added with correct status markers |
| BACKLOG updated | PASS | Issue #54 moved from Discover to Build stage |

---

## Architecture Alignment

The implementation faithfully follows `specs/054-security-assessment-pdf/plan.md`:
- All 4 components (command, agent, schema, templates) are implemented as specified
- The 8 Typst template files match the plan's project structure exactly
- The data flow matches the plan's Mermaid diagram
- The 3-tier data source preference is correctly implemented in agent, schema, and findings-detail.typ
- The severity color palette matches the plan's specification (from established tachi pattern)

---

## Verdict

**APPROVED_WITH_CONCERNS**

The implementation is solid and well-crafted. The 4 warnings are non-blocking but should be addressed before or shortly after merge:
- W-001 and W-002 affect PDF output quality for specific artifact combinations
- W-003 is a minor edge case for empty remediation roadmap pages
- W-004 is a content safety concern that should be addressed with a `.gitignore` entry

No critical or blocking issues found. The feature is production-ready with the noted concerns.
