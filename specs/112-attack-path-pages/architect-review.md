# Architect Review: Feature 112 -- Attack Path Pages in Security Report PDF

**Reviewer**: architect
**Date**: 2026-04-09
**Status**: APPROVED_WITH_CONCERNS
**Branch**: `112-attack-path-pages`

---

## Summary

Feature 112 adds dedicated attack path pages to the tachi security report PDF. The implementation is architecturally sound -- it follows established patterns (conditional page inclusion, tier-aware data extraction, Typst page template modularity) and maintains full backward compatibility. The subprocess invocation is properly secured. Two medium-severity concerns (inline fallback dead path, missing skill reference updates) and three low-severity observations are documented below.

---

## Architecture Consistency: PASS

### Conditional Page Pattern
The implementation follows the exact same conditional page inclusion pattern used by MAESTRO, infographic, and control coverage pages:
- Boolean gate variable: `has-attack-trees` (Python) / `has-attack-trees` (Typst)
- Backward-compatible defaults in `main.typ` lines 98-99: `#let has-attack-trees = if has-attack-trees != none { has-attack-trees } else { false }`
- Conditional section divider + page loop gated by both boolean and array length check (line 197)

This is consistent with the `has-maestro-data`, `has-funnel-image`, `has-compensating-controls` patterns.

### Tier-Aware Data
`_get_finding_severity()` correctly chains tier-aware field access (`residual_severity` > `severity` > `risk_level`), ensuring attack trees work across all three data source tiers. `_get_finding_mitigation()` similarly chains `recommendation` > `mitigation` > `threat`.

### Typst Template Structure
`attack-path.typ` follows the `maestro-findings.typ` pattern: imports `shared.typ` wildcard, exports a single page-rendering function, uses `severity-color()`, `report-header()`, and `report-footer()` from shared design tokens.

### Data Flow Integrity
The data pipeline is complete and linear:
1. `detect_artifacts()` (tachi_parsers.py) -- detects `attack-trees/` directory
2. `parse_attack_trees()` -- extracts entries from standalone files or inline fallback
3. `render_mermaid_to_png()` -- optional Mermaid-to-PNG conversion with graceful fallback
4. `generate_report_data_typ()` section 3q -- serializes to Typst variable bindings
5. `main.typ` -- conditionally includes section divider + per-entry pages
6. `attack-path.typ` -- renders each page with badge, diagram, narrative, remediation

### Page Placement
Attack path pages are correctly placed after Executive Summary and before infographic pages (Risk Funnel, Baseball Card, etc.), matching the spec requirement FR-010.

---

## Security Review: PASS

### Subprocess Invocation (mmdc)

**No injection risk.** The implementation passes arguments as a list to `subprocess.run()`:
```python
subprocess.run(
    ["mmdc", "-i", str(mmd_file), "-o", str(png_file), "-s", "2", "-b", "transparent"],
    capture_output=True,
    timeout=30,
    check=True,
)
```

Security positives:
- **No `shell=True`** -- arguments are passed as array elements, preventing shell injection
- **30-second timeout** -- prevents runaway processes from blocking the pipeline
- **`capture_output=True`** -- stdout/stderr captured, not echoed to terminal
- **Temp directory isolation** -- intermediate `.mmd` and `.png` files written to `tempfile.TemporaryDirectory()`, auto-cleaned via context manager
- **`shutil.which("mmdc")` check** -- verifies tool existence before any subprocess invocation
- **Error message truncation** -- stderr limited to 200 chars in warning output (`stderr_msg[:200]`)

### File System Safety
- `attack_trees_dir.mkdir(exist_ok=True)` -- safe directory creation
- `shutil.copy2()` for final PNG placement -- preserves metadata
- No user-controlled paths in subprocess arguments -- finding IDs come from parsed markdown, not user input

---

## Backward Compatibility: PASS

### No-Attack-Trees Path
When `has_attack_trees` is `False` in `detect_artifacts()`:
- `main()` skips `parse_attack_trees()` and `render_mermaid_to_png()` entirely (line 1350)
- `data["has_attack_trees"]` = `False`, `data["attack_trees"]` = `[]`
- `generate_report_data_typ()` emits `#let has-attack-trees = false` and `#let attack-trees = ()`
- `main.typ` conditional (line 197) evaluates to false, no section divider or pages emitted
- Report output is byte-identical to pre-feature behavior

### Older report-data.typ Files
The `main.typ` defaults (lines 98-99) handle the case where `has-attack-trees` and `attack-trees` are not defined in an older `report-data.typ`, using `!= none` guard to fall back to `false` and `()`.

---

## Concerns

### C-1: Inline Fallback Dead Path (Medium)

**Finding**: The `main()` function in `extract-report-data.py` gates attack tree processing on `artifacts.get("has_attack_trees")` (line 1350). This artifact flag is set by `detect_artifacts()` which only returns `True` when the `attack-trees/` directory exists and contains `.md` files. However, `parse_attack_trees()` has a fallback path (lines 446-451) that extracts inline trees from `threat-report.md` Section 5 when no standalone files exist.

**Impact**: The inline fallback in `parse_attack_trees()` can never be reached from `main()` because the outer gate prevents `parse_attack_trees()` from being called when no `attack-trees/` directory exists. If a user has inline attack trees in their `threat-report.md` but no standalone files, no attack path pages will be generated.

**Spec Reference**: FR-002 requires fallback to inline trees from threat-report.md Section 5.

**Recommendation**: Either:
(a) Remove the inline fallback from `parse_attack_trees()` if it is intentionally not supported from the main pipeline (and update the spec/plan to remove FR-002), or
(b) Call `parse_attack_trees()` unconditionally (or gate on `has_attack_trees OR threat_report_md`) so the fallback can activate. Example:

```python
# Attack tree data
if artifacts.get("has_attack_trees") or artifacts.get("threat_report_md"):
    attack_trees = parse_attack_trees(target_dir, data["findings"])
    ...
```

This is the higher-impact option because some users may only have `threat-report.md` without standalone attack tree files.

### C-2: Skill Reference Files Not Updated (Medium)

**Finding**: The `tachi-report-assembly` skill references (`typst-artifacts.md` and `typst-template-contract.md`) contain no mention of `attack-trees`, `has-attack-trees`, or the new attack tree Typst variables. These files are documented as MANDATORY reads for the report-assembler agent during Steps 1 and 2.

**Impact**: The report-assembler agent's skill references are incomplete. If an LLM agent reads only the skill references (as instructed), it will not know about the attack tree data contract. This does not affect the Python extraction script (which is deterministic), but it could cause confusion during manual debugging or agent-driven report assembly.

**Recommendation**: Update both skill reference files:
- `typst-artifacts.md` -- add `attack-trees/` directory to the artifact detection table
- `typst-template-contract.md` -- add `has-attack-trees` (boolean) and `attack-trees` (array with keys: id, component, severity, title, image-path, has-image, mermaid-text, narrative, remediation) to the variable contract

---

## Low-Severity Observations

### L-1: Finding ID Case Sensitivity in Sort

The sort key in `parse_attack_trees()` uses `e["id"].lower()` for secondary sort within same severity. This is correct for deterministic ordering but differs from the rest of the codebase where finding IDs are compared case-sensitively. Not a bug -- just a style note for consistency if revisited.

### L-2: Mermaid Code in Typst String Escaping

Large Mermaid code blocks are serialized into Typst string literals via `escape_typst_string()` in the `mermaid-text` field. This works for the text fallback case but produces very long single-line strings in `report-data.typ`. For diagrams with 20+ nodes, these strings can exceed 2000 characters on a single line. Typst handles this fine, but it reduces debuggability of the generated data file.

### L-3: No Validation of Attack Tree Count in `validate()`

The `validate()` function checks severity sums and finding ID uniqueness but does not validate attack tree data (e.g., duplicate attack tree IDs, entries without Mermaid code). Since the attack tree data is derived from findings and the rendering pipeline handles empty/invalid entries gracefully, this is low risk.

---

## Verdict

The implementation is architecturally sound and follows established patterns. The subprocess security is well-implemented. Backward compatibility is fully maintained. The two medium concerns (C-1 inline fallback dead path, C-2 skill reference gaps) should be addressed before merging but are not blocking.

**APPROVED_WITH_CONCERNS** -- address C-1 and C-2 before merging.
