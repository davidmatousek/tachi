# T017: Regression Validation (No-Baseline Scenario)

**Feature**: 104 — Downstream Baseline Propagation
**Task**: T017 — Verify backward compatibility when no baseline is present
**Date**: 2026-04-08
**Validator**: BDD Testing Agent

---

## Summary

All 10 modified files correctly guard delta logic behind baseline presence checks. Running without a baseline produces output identical to pre-Feature-104 behavior.

**Overall Verdict: PASS** (0 backward compatibility issues found)

---

## Component Results

### 1. Python Scripts — Execution Tests

#### a) `scripts/tachi_parsers.py` — PASS

| Function | Input | Expected | Actual | Status |
|----------|-------|----------|--------|--------|
| `parse_baseline_frontmatter()` | Frontmatter with NO baseline block | All None values | `{source: None, date: None, finding_count: None, run_id: None}` | PASS |
| `parse_resolved_findings()` | Content with NO Section 4b | Empty list | `[]` | PASS |
| `parse_threats_findings()` | Section 7 with NO Status column | No `delta_status` field in dicts | Findings returned with keys: `component, id, impact, likelihood, mitigation, risk_level, threat` — no `delta_status` | PASS |
| All three functions | Real example `examples/agentic-app/threats.md` (pre-104 data, 22 findings) | No delta fields, all baseline None, no resolved | 22 findings, no `delta_status`, all baseline None, 0 resolved | PASS |

**Guard mechanism**: `parse_threats_findings()` at line 498 — Status column is extracted via `row.get("Status", "").strip()`, and the field is only added when the value is non-empty: `if status: finding["delta_status"] = status`. Tables without a Status column produce findings without `delta_status`.

#### b) `scripts/extract-infographic-data.py` — PASS

| Check | Expected | Actual | Status |
|-------|----------|--------|--------|
| Delta logic guarded by `if has_baseline:` (line 1249, 1333) | Yes | Confirmed: `has_baseline = baseline["source"] is not None` (line 1229); delta_status in top_findings only added inside `if has_baseline:` block (line 1249); delta_data computed only inside `if has_baseline:` block (line 1333) | PASS |
| No baseline: severity counts include all findings | All 22 findings counted | Severity distribution total = 22 | PASS |
| No baseline: `delta` key absent from JSON output | No `delta` key | Confirmed absent (line 1360: `if delta_data: data["delta"] = delta_data` — delta_data is None) | PASS |
| No baseline: top_findings have no `delta_status` | No delta_status fields | Confirmed via JSON inspection | PASS |

**Real-world execution**: `python3 scripts/extract-infographic-data.py --target-dir examples/agentic-app --template baseball-card` produced valid JSON with 22 findings, no delta object, no errors.

#### c) `scripts/extract-report-data.py` — PASS

| Check | Expected | Actual | Status |
|-------|----------|--------|--------|
| Delta logic guarded by `if has_baseline:` (line 985) | Yes | Confirmed: `has_baseline = baseline["source"] is not None` (line 885); delta_counts computed with actual values only inside `if has_baseline:` (line 985); else branch sets all counts to 0 (line 997) | PASS |
| No baseline: `resolved_findings` is empty list | Empty list | `parse_resolved_findings()` returns `[]` when no Section 4b present | PASS |
| No baseline: Typst variables default correctly | `has-baseline = false`, all delta counts = 0, `baseline-source = ""`, `resolved-findings = ()` | Confirmed in generated `/tmp/t017-report-data-test.typ` | PASS |
| No baseline: active severity counts = total counts | 22 = 22 | Sum of severity counts (22) equals total-findings (22) | PASS |
| Finding format: `delta_status` only when present | Field omitted when empty | Line 803-806: `ds = f.get("delta_status", ""); if ds: base += ...` — backward compatible conditional inclusion | PASS |

**Real-world execution**: `python3 scripts/extract-report-data.py --target-dir examples/agentic-app --output /tmp/t017-report-data-test.typ --template-dir templates/tachi/security-report/` produced valid Typst data with 22 findings, `has-baseline = false`, all delta counts 0.

---

### 2. Agent Instructions — Content Review

#### d) `agents/threat-report.md` — PASS

| Check | Location | Content | Status |
|-------|----------|---------|--------|
| Section 8 omission when no baseline | Line 837 | "This section is **only present when the input threats.md contains baseline data** (i.e., `baseline.source` is non-null in frontmatter). When no baseline is present, omit Section 8 entirely" | PASS |
| Skip gate documented | Line 841 | "Check the input `threats.md` frontmatter for `baseline.source`. If it is null, `~`, or absent, skip Section 8 completely." | PASS |
| Attack trees: all fresh when no baseline | Line 698 | "**No baseline** (baseline.source is null): Generate all attack trees fresh with no delta annotations. This is standard first-run behavior — identical to pre-delta behavior." | PASS |
| Delta annotations skipped when no baseline | Line 88 | "`delta_status` ... Only present when baseline data exists in input." | PASS |
| Primary gate documented | Line 67 | "`baseline.source` ... **Primary gate for delta-aware behavior.** When non-null, enable all delta logic. When null (first run), skip Section 8 and all delta annotations." | PASS |
| Quality checklist: Section 8 conditional | Line 119 | "Section 8 (Delta Summary) present when baseline data exists in input; absent when no baseline" | PASS |

#### e) `agents/threat-infographic.md` — PASS

| Check | Location | Content | Status |
|-------|----------|---------|--------|
| Delta emphasis conditional on data presence | Line 72 | "`delta_status` ... optional" — field is optional, only present when baseline exists | PASS |
| Delta gate on `delta.has_baseline` | Line 80 | "`delta.has_baseline` boolean — Gate for all delta-aware visual directives" | PASS |
| No behavior alteration when no delta data | Lines 84-86 | Delta emphasis directives are conditioned on "When delta data is present" — no action when absent | PASS |

#### f) `.claude/agents/tachi/report-assembler.md` — PASS

| Check | Location | Content | Status |
|-------|----------|---------|--------|
| No-baseline rendering rule | Line 231 | "**No-baseline behavior**: When `has-baseline` is false, render findings as before (no separation, no annotations, no resolved section). All delta variables default to zero/empty." | PASS |
| `has-baseline` as gate variable | Line 217 | "`has-baseline` boolean — Gate for delta-aware page sections" | PASS |
| Schema version handling | Lines 206-209 | v1.2 explicitly called out; v1.0 treated conservatively | PASS |

---

### 3. Command Files — Content Review

#### g) `.claude/commands/infographic.md` — PASS

| Check | Location | Content | Status |
|-------|----------|---------|--------|
| Delta context conditional | Lines 168-172 | "If the JSON contains a 'delta' object (has_baseline: true), include delta context..." — conditional check means no delta context when no delta object | PASS |
| No delta object when no baseline | Verified via Python | `extract-infographic-data.py` only emits `data["delta"]` when `delta_data` is non-None (line 1360-1361), which only happens when `has_baseline` is True | PASS |

#### h) `.claude/commands/security-report.md` — PASS

| Check | Location | Content | Status |
|-------|----------|---------|--------|
| Baseline display conditional | Line 113 | `{if threats.md has baseline.source != null: "Baseline: {source} ({date}) — delta counts will appear in report"}` — conditional display, skipped when no baseline | PASS |
| Delta context in agent prompt conditional | Lines 153-163 | "When baseline data is present in threats.md, the extraction script automatically includes delta-aware variables" — no action when no baseline | PASS |

---

### 4. Schema Templates — Content Review

#### i) `templates/tachi/output-schemas/threats.md` — PASS

| Check | Location | Content | Status |
|-------|----------|---------|--------|
| Section 4b conditional presence | Line 393 | "**When no baseline is present** (first run): Omit this section entirely. Do not include the header or an empty table." | PASS |
| Section 8 conditional presence | Line 577 | "_Present only when a baseline was used for the current run. Omit this entire section (header and content) on first run (no baseline)._" | PASS |
| Example frontmatter: first run no baseline | Lines 96-113 | Explicit example showing `baseline: source: null, date: null, finding_count: null, run_id: null` | PASS |
| Status column documented as baseline-aware only | Line 229 | "**Status column** (baseline-aware mode only)" — makes clear the column is conditional | PASS |

#### j) `templates/tachi/output-schemas/threat-report.md` — PASS

| Check | Location | Content | Status |
|-------|----------|---------|--------|
| Section 8 conditional | Line 255 | "_Present only when the input threats.md contains baseline data (i.e., `baseline.source` is non-null in frontmatter). Omit this entire section on first run (no baseline)._" | PASS |
| Frontmatter delta_counts nullable | Lines 53-57 | "`delta_counts` object, nullable — ... All values null when no baseline." | PASS |
| baseline_source nullable | Line 51 | "`baseline_source` string, nullable — Null when no baseline (first run)." | PASS |
| attack_tree_count no-baseline behavior | Line 50 | "When no baseline, equals total Critical + High findings." | PASS |

---

### 5. Real-World Regression Test — PASS

| Script | Input | Exit Code | Output | Delta Fields | Status |
|--------|-------|-----------|--------|--------------|--------|
| `extract-infographic-data.py` | `examples/agentic-app/threats.md` (no baseline) | 0 | Valid JSON, 22 findings, Tier 3 | No `delta` key in output | PASS |
| `extract-report-data.py` | `examples/agentic-app/threats.md` (no baseline) | 0 | Valid Typst, 22 findings, Tier 3 | `has-baseline = false`, all delta counts = 0, `resolved-findings = ()` | PASS |

---

## Guard Mechanism Summary

All 10 files use consistent guard patterns:

| File Type | Guard Mechanism | Pattern |
|-----------|-----------------|---------|
| `tachi_parsers.py` | Conditional field inclusion | `if status: finding["delta_status"] = status` — field absent when column missing |
| `tachi_parsers.py` | Section absence → empty return | `parse_resolved_findings()` returns `[]` when no Section 4b header found |
| `tachi_parsers.py` | Null default return | `parse_baseline_frontmatter()` returns all-None dict when no baseline block |
| `extract-infographic-data.py` | Boolean gate | `has_baseline = baseline["source"] is not None` → guards delta_status injection and delta_data emission |
| `extract-report-data.py` | Boolean gate + else branch | `if has_baseline:` computes real counts; `else:` sets all counts to zero |
| `extract-report-data.py` | Conditional Typst field | `if ds: base += ', delta_status: ...'` — field omitted from Typst output when empty |
| Agent/command files | Textual conditional language | "When no baseline", "only present when", "omit entirely on first run" |
| Schema templates | Explicit omission instructions | "Omit this section entirely", "All values null when no baseline" |
