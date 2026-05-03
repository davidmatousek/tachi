# Code Review: Feature 091 — MAESTRO Infographic Templates and PDF Report Section

**Reviewer**: code-reviewer
**Date**: 2026-04-08
**Branch**: 091-maestro-infographic-templates
**Verdict**: APPROVED_WITH_CONCERNS

---

## Summary

Reviewed 10 files (841 lines added/modified across 3 new files and 7 modified files). The implementation is solid and follows existing patterns consistently. Python extraction code is well-structured with proper error handling and fallback logic. Typst template follows the single-export-function pattern from findings-detail.typ. Documentation updates are complete and consistent across SKILL.md, command file, and INFOGRAPHIC_TEMPLATES.md.

**Total Findings**: 7 (0 CRITICAL, 3 WARNING, 4 SUGGESTION)

---

## Findings

### WARNING-01: MAESTRO layer name mismatch in maestro-stack ASCII layout diagram

**File**: `/Users/david/Projects/tachi/templates/tachi/infographics/infographic-maestro-stack.md`, lines 22 and 26
**Issue**: The ASCII layout diagram uses incorrect MAESTRO layer names:
- Line 22: `L6 — Deployment` (should be `L6 — Agent Ecosystem`)
- Line 26: `L4 — Tooling` (should be `L4 — Deployment Infrastructure`)

The canonical layer names from `.claude/skills/tachi-shared/references/maestro-layers-shared.md` are:
- L4 = Deployment Infrastructure
- L6 = Agent Ecosystem

The Zone Specifications text below correctly says "Each band shows layer ID, name..." and the Gemini prompt template uses `{layer_bands_text}` placeholders (dynamically populated from correct data), so **the generated image will be correct**. However, the ASCII diagram in the template file itself is misleading for anyone reading the template.

**Impact**: Developers or reviewers reading the template file will see incorrect layer names. No impact on generated output since the Gemini prompt uses dynamic data.
**Fix**: Update line 22 to `L6 — Agent Ecosystem` and line 26 to `L4 — Deployment Infrastructure`.

---

### WARNING-02: Inconsistent em-dash parsing between extract-infographic-data.py and extract-report-data.py

**File**: `/Users/david/Projects/tachi/scripts/extract-infographic-data.py`, line 914 and line 1057
**File**: `/Users/david/Projects/tachi/scripts/extract-report-data.py`, line 237 and line 348
**Issue**: The two scripts use different approaches to split MAESTRO layer strings:

- `extract-infographic-data.py` line 914: `layer_raw.split("—", 1)` — splits on literal em-dash character
- `extract-infographic-data.py` line 1057: `layer_raw.split("—")[0].strip().split("–")[0].strip()` — handles both em-dash AND en-dash
- `extract-report-data.py` line 237: `layer_raw.split("\u2014", 1)` — splits on Unicode em-dash escape
- `extract-report-data.py` line 348: `parts[0].strip().split("\u2013")[0].strip()` — handles both em-dash and en-dash

These are functionally equivalent for well-formed data, but the approach differs. The `parse_maestro_layer_distribution()` in `extract-infographic-data.py` (line 914) splits on literal `"—"` without en-dash fallback, while the `compute_maestro_heatmap()` in the same file (line 1057) does handle both. This means if a layer string somehow uses en-dash (`–`) instead of em-dash (`—`), the distribution parser would fail to split it correctly while the heatmap parser would handle it.

**Impact**: Low risk — tachi output uses em-dash consistently. But the inconsistency within the same file is a latent bug.
**Fix**: Make `parse_maestro_layer_distribution()` at line 914 also handle en-dash, matching the pattern at line 1057.

---

### WARNING-03: Missing Unclassified handling in extract-infographic-data.py

**File**: `/Users/david/Projects/tachi/scripts/extract-infographic-data.py`
**Issue**: The spec (Edge Cases section) requires: "Findings without MAESTRO layer should be treated as 'Unclassified.'" The `extract-report-data.py` correctly handles this at line 344 by assigning `lid = "Unclassified"` when `maestro_layer` is empty. However, `extract-infographic-data.py` has no equivalent Unclassified handling in its `parse_per_finding_maestro()` function or `compute_maestro_heatmap()` function.

In `compute_maestro_heatmap()` (line 1053), findings with empty `maestro_layer` are silently skipped (`if not comp or not layer_raw: continue`), and findings with non-standard layer IDs are also skipped (`if layer_id not in _MAESTRO_LAYERS: continue`). This means Unclassified findings are excluded from the heatmap entirely rather than being grouped.

**Impact**: Pre-084 findings in a mixed-schema threats.md will be silently dropped from heatmap data rather than appearing in an "Unclassified" row. The heatmap would show an incomplete picture.
**Fix**: Add an "Unclassified" row handling to `compute_maestro_heatmap()` for findings with empty `maestro_layer`, or document that the heatmap intentionally excludes unclassified findings (since the grid columns are L1-L7 only, an Unclassified column may not make visual sense).

---

### SUGGESTION-01: Duplicated MAESTRO parsing logic across two scripts

**File**: `/Users/david/Projects/tachi/scripts/extract-infographic-data.py`, lines 898-1135
**File**: `/Users/david/Projects/tachi/scripts/extract-report-data.py`, lines 200-397
**Issue**: Both scripts contain near-identical MAESTRO parsing functions (Section 6 table parsing, Section 3/4 per-finding extraction, most-exposed-layer computation). The implementations are slightly different (e.g., dash handling, `strip_bold` usage, Unclassified handling) which creates maintenance burden and subtle inconsistency risk.

**Impact**: Future changes to MAESTRO parsing need to be applied in two places. The existing `tachi_parsers.py` shared module is the established pattern for cross-script parsing.
**Fix**: Consider extracting the shared MAESTRO parsing functions into `tachi_parsers.py` in a follow-up refactor. Not blocking for this feature.

---

### SUGGESTION-02: Typography color values in maestro-stack template don't match dark theme

**File**: `/Users/david/Projects/tachi/templates/tachi/infographics/infographic-maestro-stack.md`, lines 86-92
**Issue**: The Typography table uses dark-on-light colors (`#111827`, `#374151`, `#4B5563`) which are inappropriate for a Dark Navy (`#1E293B`) background. The maestro-heatmap template correctly uses light-on-dark colors (`#F8FAFC`, `#94A3B8`).

However, this is a **pre-existing pattern** — the baseball-card template has the same inconsistency where its Typography table lists dark colors but its Color Palette table and Gemini prompt specify light colors. The Gemini prompt template overrides these values with "white or light gray" directives.

**Impact**: No visual impact — the Gemini prompt correctly specifies light text. The Typography table is misleading but is a pre-existing issue across templates.
**Fix**: No action needed for this feature. Consider standardizing Typography tables across all templates in a future cleanup.

---

### SUGGESTION-03: Duplicate MAESTRO variables section in typst-template-contract.md

**File**: `/Users/david/Projects/tachi/.claude/skills/tachi-report-assembly/references/typst-template-contract.md`
**Issue**: The MAESTRO variables are documented twice — once in the main "Variable Definitions" section (lines 262-298) and again in a dedicated "MAESTRO Data Variables (Feature 091)" section (lines 319-365). The content is consistent but the duplication adds unnecessary length to the reference file.

**Impact**: Minor — agents reading this file get redundant information. No functional impact.
**Fix**: Consider removing the duplicate "MAESTRO Data Variables (Feature 091)" section in a future cleanup, keeping only the inline documentation within "Variable Definitions."

---

### SUGGESTION-04: Text Label Budget missing from maestro-stack template

**File**: `/Users/david/Projects/tachi/templates/tachi/infographics/infographic-maestro-stack.md`
**Issue**: The maestro-heatmap template includes a "Text Label Budget" subsection (lines 215-224) that helps the Gemini model manage visual complexity. The maestro-stack template does not include an equivalent section.

**Impact**: Minor — the stack template has fewer labels than the heatmap, so this is less critical. The Gemini prompt is detailed enough to guide generation.
**Fix**: Consider adding a Text Label Budget section for consistency with the heatmap template.

---

## Architecture Alignment

| Aspect | Status | Notes |
|--------|--------|-------|
| Plan compliance | PASS | All 8 components implemented per plan.md |
| FR coverage | PASS | FR-001 through FR-015 all addressed |
| Backward compatibility | PASS | `has-maestro-data` boolean gates all new sections; defaults in main.typ Section 2b |
| Template pattern compliance | PASS | Both infographic templates follow all mandatory sections (layout, style, palette, typography, zones, prompt, API config, accessibility) |
| Typst single-export pattern | PASS | maestro-findings.typ exports single function matching findings-detail.typ pattern |
| CLI extension | PASS | `--template` choices correctly extended with maestro-stack and maestro-heatmap |
| Data flow | PASS | threats.md -> extraction -> JSON/Typst -> rendering pipeline correctly implemented |

## Security Review

| Check | Status | Notes |
|-------|--------|-------|
| No hardcoded secrets | PASS | No credentials or API keys in any file |
| Input validation | PASS | Template choices validated by argparse; file paths validated via detect_artifacts |
| Injection safety | PASS | Typst strings escaped via escape_typst_string(); JSON output via json.dumps |

## Test Coverage

| Check | Status | Notes |
|-------|--------|-------|
| Example validation | VERIFIED | Results in t023-example-validation.md show 6/6 examples processed |
| Regression test | VERIFIED | Results in t024-regression.md confirm existing templates unaffected |
| Edge cases | PARTIAL | Pre-084 empty state handled; Unclassified findings partially handled (WARNING-03) |

## Documentation Consistency

| Document | Status | Notes |
|----------|--------|-------|
| SKILL.md | PASS | MAESTRO templates and maestro shorthand documented |
| template-specific-formats.md | PASS | Section 5 formats for both templates added with edge cases |
| typst-template-contract.md | PASS | All 8 MAESTRO variables documented with types, sources, defaults |
| INFOGRAPHIC_TEMPLATES.md | PASS | Both templates in Available Templates table, Output Files, and Using Templates |
| infographic.md command | PASS | Valid template values include maestro-stack, maestro-heatmap, maestro |

---

## Verdict: APPROVED_WITH_CONCERNS

The implementation is complete, well-structured, and follows established patterns. No blocking issues found. The 3 WARNING-level findings are low-risk and can be addressed in a follow-up commit or during the `/aod.document` phase.

Recommended priority for fixes:
1. WARNING-01 (layer name typo in ASCII diagram) — trivial fix
2. WARNING-02 (em-dash parsing inconsistency) — defensive fix
3. WARNING-03 (Unclassified heatmap handling) — design decision needed
