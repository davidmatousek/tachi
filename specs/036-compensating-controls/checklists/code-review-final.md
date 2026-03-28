# Code Review: Feature 036 — Compensating Controls

**Reviewer**: code-reviewer
**Date**: 2026-03-28
**Branch**: `036-compensating-controls`
**Verdict**: APPROVED_WITH_CONCERNS

---

## Review Scope

| # | File | Type |
|---|------|------|
| 1 | `.claude/agents/tachi/control-analyzer.md` | Agent persona (1,366 lines) |
| 2 | `.claude/commands/compensating-controls.md` | Command orchestrator (195 lines) |
| 3 | `schemas/compensating-controls.yaml` | Controlled finding schema (176 lines) |
| 4 | `templates/compensating-controls.md` | Markdown output template (327 lines) |
| 5 | `templates/compensating-controls.sarif` | SARIF 2.1.0 output template (603 lines) |

---

## Findings Summary

| Severity | Count |
|----------|-------|
| CRITICAL | 1 |
| WARNING | 3 |
| SUGGESTION | 3 |
| **Total** | **7** |

---

## CRITICAL Findings

### C-1: Schema `Producers` header references non-existent agent file

**File**: `schemas/compensating-controls.yaml`, line 7
**Issue**: The `Producers` comment declares `agents/tachi/compensating-controls-scanner.md` as the producing agent. This file does not exist. The actual agent file is `agents/tachi/control-analyzer.md`.
**Impact**: Developer following the schema header to find the producing agent will encounter a broken reference. Anyone extending or debugging the pipeline will be misled about which agent owns this schema.
**Fix**: Change line 7 from:
```
# Producers: agents/tachi/compensating-controls-scanner.md
```
to:
```
# Producers: agents/tachi/control-analyzer.md
```

**Cross-reference check**: The markdown template (`templates/compensating-controls.md`, line 10) and the SARIF template (`templates/compensating-controls.sarif`, line 2) both correctly reference `agents/tachi/control-analyzer.md`. Only the schema has the stale name.

---

## WARNING Findings

### W-1: SARIF template `startLine` type inconsistency in `relatedLocations`

**File**: `templates/compensating-controls.sarif`, lines 309, 323, 391, 495, 559
**Issue**: In `relatedLocations` entries for control evidence, `startLine` values are encoded as string placeholders (`"<control-evidence-line-number>"`). Per SARIF 2.1.0 specification, `region.startLine` is an integer field. While the primary `locations[0]` entries correctly use integer `startLine: 1`, the related locations use a string type for the placeholder.
**Impact**: An implementer copying the template structure literally (rather than following the agent's Phase 6c instructions) could produce invalid SARIF with string-typed line numbers. GitHub Code Scanning would reject or silently ignore such entries.
**Fix**: Change the `relatedLocations` `startLine` placeholders to indicate integer type, consistent with how the upstream `risk-scores.sarif` and `threats.sarif` templates handle it. For example:
```json
"startLine": 0
```
with a `_comment` noting it should be replaced with the actual integer line number. Alternatively, add a comment in the template noting the placeholder must be replaced with an integer value.

### W-2: Command orchestrator does not declare `--target` as required for non-self-analysis

**File**: `.claude/commands/compensating-controls.md`, line 16 (Step 0, item 2)
**Issue**: The `--target` flag defaults to `"."` (current working directory). When a user runs `/compensating-controls` from their project root, the command will scan the entire project (including tachi's own `.claude/` directory, `schemas/`, `templates/`, etc.) rather than just application code. The `/risk-score` command does not have an equivalent `--target` flag because it does not scan codebases, so there is no precedent in the pipeline for this behavior.
**Impact**: Users running the command from a tachi-instrumented project without `--target` will get control detections from tachi's own agent files (which contain security keywords like `jwt.verify`, `bcrypt`, `csrf`), producing false positive control evidence. The 200-file budget would also be consumed by non-application files.
**Fix**: Add a warning in the command output when `--target` defaults to `"."`, such as:
```
Note: --target defaults to current directory. For best results, specify the
application source directory (e.g., --target ./src).
```
This is a documentation/UX concern, not a blocking issue.

### W-3: Agent metadata `output_schema` uses relative path that traverses 3 levels

**File**: `.claude/agents/tachi/control-analyzer.md`, line 12
**Issue**: The metadata `references` block uses relative paths like `../../../schemas/compensating-controls.yaml` and `../../../templates/compensating-controls.md`. While these paths are technically correct from the agent file's location, they are fragile -- any restructuring of the `.claude/agents/tachi/` hierarchy would break all 7 reference paths.
**Impact**: Low immediate impact since these paths are informational metadata (the agent loads files by absolute path at runtime). However, if a validation tool ever resolves these references, they would break on any directory restructuring.
**Fix**: Consider using project-root-relative paths (e.g., `schemas/compensating-controls.yaml`) to match the convention used in schema and template headers. The upstream `risk-scorer.md` agent should be checked for consistency -- if it also uses `../../../` paths, this is an existing convention and can be deferred.

---

## SUGGESTION Findings

### S-1: Markdown template Section 3 includes P1 effectiveness assessment table

**File**: `templates/compensating-controls.md`, lines 129-137
**Issue**: The template includes a full effectiveness assessment table with four dimensions (Coverage, Configuration, Currency, Completeness) and placeholder fields for each. The agent instructions (Phase 6b, Section 3 rules) explicitly state that in P0, the dimension breakdown table should be replaced with a note: "Detailed effectiveness assessment available in P1 (User Story 6)."
**Impact**: The template structure invites implementers to fill in the 4-dimension table even in P0, when the agent is not designed to produce those values. This creates a mismatch between template expectations and agent capabilities.
**Fix**: Add an HTML comment in the template indicating the effectiveness assessment table is a P1 feature:
```markdown
<!-- P0: Replace this table with: *Detailed effectiveness assessment available in P1 (User Story 6).* -->
```

### S-2: Schema `control_category` enum has 8 values but agentic/LLM may need AI-specific categories in P1

**File**: `schemas/compensating-controls.yaml`, lines 44-53
**Issue**: The `control_category` enum lists exactly 8 categories. The STRIDE-to-control mapping comment for `agentic` notes "all 8 (P0); ai-specific (P1)" and for `llm` notes "input-validation, logging-audit (P0); ai-specific (P1)". The schema does not include a P1 extension point or comment indicating where AI-specific categories would be added.
**Impact**: When P1 adds AI-specific control categories, the enum will need to be extended. No immediate issue, but a forward-compatibility note would help future developers.
**Fix**: Add a comment after the enum:
```yaml
    # P1: Add AI-specific categories (e.g., prompt-guard, model-access-control, tool-scope-enforcement)
```

### S-3: Usage examples section could include SARIF-input fallback example

**File**: `.claude/commands/compensating-controls.md`, lines 165-177
**Issue**: All four usage examples show the standard flow. None demonstrates the SARIF-input fallback path (when only `risk-scores.sarif` exists without `risk-scores.md`). The command's Step 1 explicitly supports this fallback, but users have no example showing it in action.
**Impact**: Minor -- users who only have SARIF input may not realize the command supports it without reading Step 1 carefully.
**Fix**: Add a commented example:
```bash
# When only risk-scores.sarif exists (no risk-scores.md), SARIF is used as fallback input
/compensating-controls --target ./my-app ./reports-with-sarif-only/
```

---

## Checklist Assessment

| # | Check | Result | Notes |
|---|-------|--------|-------|
| 1 | Command maps to one user workflow | PASS | Single workflow: validate -> analyze -> report. No monolithic combining. |
| 2 | Master content immutable | PASS | No `_Global/` modifications. Agent reads codebase files but never modifies them. |
| 3 | Naming conventions followed | PASS | `control-analyzer.md` (kebab-case agent), `compensating-controls.md` (kebab-case command), `compensating-controls.yaml` (kebab-case schema). |
| 4 | Context loading declared (lazy) | PASS | Agent uses explicit "Reference File Loading" section with per-phase lazy loading. Template and schema loaded only in Phase 6. |
| 5 | References consistent | FAIL | Schema `Producers` header references `compensating-controls-scanner.md` (does not exist). See C-1. |
| 6 | Agent well-structured | PASS | Clear 6-phase pipeline with input/output documented per phase. Input boundary, processing capacity, and error handling all specified. |
| 7 | SARIF template structurally valid | PASS (with concern) | Valid SARIF 2.1.0 structure. All required fields present. `startLine` type concern noted in W-1. Five example results cover all control status variants plus correlation groups. |
| 8 | Markdown template complete | PASS | All 6 sections present in correct order. Frontmatter, executive summary, coverage matrix, control details, recommendations, residual risk summary, methodology all included. |
| 9 | Orphaned references or broken paths | FAIL | Schema `Producers` path is broken (C-1). No other orphaned references found. |
| 10 | Command consistent with risk-score.md pattern | PASS | Same Step 0 flag parsing, Step 1 validation, Step 2 agent invocation, Step 3 reporting structure. Adds `--target` flag which is new but architecturally appropriate for codebase scanning. |

---

## Architecture Alignment

- **Pipeline chain**: The command correctly positions itself as the third link: `/threat-model` -> `/risk-score` -> `/compensating-controls`. Input/output contracts align with the upstream `risk-scores.md` and `risk-scores.sarif` formats.
- **SARIF supersession chain**: The template comment and agent instructions correctly describe the three-file chain (`threats.sarif` -> `risk-scores.sarif` -> `compensating-controls.sarif`) with fingerprint preservation for GitHub Code Scanning alert continuity.
- **Schema inheritance**: `controlled_finding extends scored_finding` properly chains from `finding.yaml` -> `risk-scoring.yaml` -> `compensating-controls.yaml`.
- **Dual-format output**: Both markdown and SARIF outputs are generated with an explicit cross-format consistency verification step (Phase 6d), matching the pattern established by `/risk-score`.
- **Agent platform neutrality**: The agent explicitly declares itself as platform-neutral (line 37), consistent with tachi's design principle that agents work with any LLM capable of following structured markdown prompts.

---

## Security Review

- No PII, credentials, or secrets in any file.
- No hardcoded absolute paths (all paths are relative or provided at runtime).
- The agent reads target codebase files but never modifies them (read-only discipline enforced in Phase 2 and Phase 3).
- The 200-file read budget prevents unbounded filesystem access.
- Large file truncation (5,000 token limit) prevents context window exhaustion attacks via adversarial file placement.

---

## Verdict

**APPROVED_WITH_CONCERNS**

The deliverables are well-structured, architecturally aligned, and follow established patterns from the upstream pipeline stages. The 6-phase agent is comprehensive with clear boundaries, error handling, and validation checks at each phase transition.

One critical finding (C-1: broken `Producers` reference in the schema) must be fixed before merge. This is a one-line change. The three warnings are non-blocking but should be addressed in a follow-up or during the fix commit.

### Required Before Merge

1. Fix `schemas/compensating-controls.yaml` line 7: change `compensating-controls-scanner.md` to `control-analyzer.md`

### Recommended (Non-Blocking)

2. Add integer-type indicator or comment for SARIF template `relatedLocations.startLine` placeholders (W-1)
3. Add `--target` default warning in command output (W-2)
4. Evaluate relative path convention in agent metadata against upstream agents (W-3)
