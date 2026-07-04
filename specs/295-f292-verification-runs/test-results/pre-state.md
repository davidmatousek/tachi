# T002 — Pre-State Suite Totals (FR-019)

**Date**: 2026-07-03
**Branch**: `295-f292-verification-runs`
**Purpose**: Capture the D-E suite baseline BEFORE any US1/US2/US3 artifact commits land, per KB Entry 15 inherited-vs-own discipline. This file BLOCKS all subsequent commits — it must predate artifact commits in git history (Phase 2 checkpoint).

**Working tree state at run time**: clean at HEAD except one unrelated pre-existing change (`docs/product/_backlog/BACKLOG.md`, an auto-regenerated `/aod.status` timestamp) — not part of `tests/scripts/` and not touched by this task. The F-248/F-256 clone-HEAD harness behavior (tests that `git show HEAD:...` internally) is unaffected.

---

## 1. `test_backward_compatibility.py` (incl. slow PDF suite)

**Command**: `python3 -m pytest tests/scripts/test_backward_compatibility.py -v --timeout=1080`

**Verbatim summary line**:
```
======================== 13 passed, 1 skipped in 20.98s ========================
```

**Skip detail** (verbatim):
```
SKIPPED [1] tests/scripts/test_backward_compatibility.py:392: mermaid-agentic-app is excluded from SC-003 per T033 narrowed interpretation (multi-agent gate predicate evaluates TRUE via condition (a)+(b); pattern classification is a documented known-limitation pending R-04/R-06 rule-tuning follow-up).
```

**Full pass list** (14 collected: 13 passed + 1 skipped):
```
test_unmodified_examples_byte_identical_pdfs[web-app] PASSED
test_unmodified_examples_byte_identical_pdfs[microservices] PASSED
test_unmodified_examples_byte_identical_pdfs[ascii-web-api] PASSED
test_unmodified_examples_byte_identical_pdfs[mermaid-agentic-app] PASSED
test_unmodified_examples_byte_identical_pdfs[free-text-microservice] PASSED
test_unmodified_examples_byte_identical_pdfs[maestro-reference] PASSED
test_feature_142_zero_edit_invariant_on_detection_agents PASSED
test_feature_142_backward_compat_pattern_defaults PASSED
test_feature_142_multi_agent_gate_predicate_false_on_baselines[web-app] PASSED
test_feature_142_multi_agent_gate_predicate_false_on_baselines[microservices] PASSED
test_feature_142_multi_agent_gate_predicate_false_on_baselines[ascii-web-api] PASSED
test_feature_142_multi_agent_gate_predicate_false_on_baselines[mermaid-agentic-app] SKIPPED
test_feature_142_multi_agent_gate_predicate_false_on_baselines[free-text-microservice] PASSED
test_feature_142_multi_agent_gate_predicate_false_on_baselines[maestro-reference] PASSED
```

---

## 2. `test_maestro_coverage_invariant.py` + `test_maestro_cross_surface_consistency.py`

**Command**: `python3 -m pytest tests/scripts/test_maestro_coverage_invariant.py tests/scripts/test_maestro_cross_surface_consistency.py -v`

**Verbatim summary line**:
```
======================== 11 passed, 2 skipped in 0.15s =========================
```

**Skip detail** (verbatim):
```
SKIPPED [1] tests/scripts/test_maestro_coverage_invariant.py:140: examples/consumer-agent-app/sample-report/threats.md has no 'Risk by MAESTRO Layer' table (intermediate-format sample report); coverage invariant N/A.
SKIPPED [1] tests/scripts/test_maestro_coverage_invariant.py:140: examples/predictive-ml-app/sample-report/threats.md has no 'Risk by MAESTRO Layer' table (intermediate-format sample report); coverage invariant N/A.
```

---

## 3. `test_catalog_drift_guard.py`

**Command**: `python3 -m pytest tests/scripts/test_catalog_drift_guard.py -v`

**Verbatim summary line**:
```
============================= 15 passed in 12.36s ==============================
```

---

## 4. `test_affected_assets_wiring.py`

**Command**: `python3 -m pytest tests/scripts/test_affected_assets_wiring.py -v`

**Verbatim summary line**:
```
============================== 35 passed in 0.05s ==============================
```

---

## Aggregate Totals

| Suite | Passed | Skipped | Failed |
|---|---|---|---|
| test_backward_compatibility.py | 13 | 1 | 0 |
| test_maestro_coverage_invariant.py + test_maestro_cross_surface_consistency.py | 11 | 2 | 0 |
| test_catalog_drift_guard.py | 15 | 0 | 0 |
| test_affected_assets_wiring.py | 35 | 0 | 0 |
| **Total** | **74** | **3** | **0** |

**Inherited-red disposition**: NONE — all four suites are fully green (0 failures). All 3 skips are pre-existing, named, and documented in-repo as intentional (mermaid-agentic-app SC-003 narrowed-interpretation known-limitation; consumer-agent-app and predictive-ml-app intermediate-format sample reports lacking the MAESTRO table by design). No fix-vs-file decision is required — there is nothing inherited to triage.

---

## Corpus-Coupling Sweep (`examples/**` glob / count-pin exposure)

**Command**:
```bash
grep -rn "examples/\*\*\|glob.*examples\|BASELINE_EXAMPLES\|len(.*examples" tests/ --include="*.py" | grep -v test-output
```

**Verbatim output**:
```
tests/scripts/test_backward_compatibility.py:24:These targets are excluded by simply not appearing in ``BASELINE_EXAMPLES``.
tests/scripts/test_backward_compatibility.py:45:BASELINE_EXAMPLES = [
tests/scripts/test_backward_compatibility.py:72:@pytest.mark.parametrize("example_name", BASELINE_EXAMPLES)
tests/scripts/test_backward_compatibility.py:375:@pytest.mark.parametrize("example_name", BASELINE_EXAMPLES)
tests/scripts/test_backward_compatibility.py:384:    in BASELINE_EXAMPLES but the SC-003 interpretation in tasks.md T033
tests/scripts/test_maestro_coverage_invariant.py:60:        for p in REPO_ROOT.glob("examples/**/threats.md")
tests/scripts/test_maestro_cross_surface_consistency.py:60:        for p in REPO_ROOT.glob("examples/**/threats.md")
```

**Supplementary due-diligence check** (not part of the prescribed sweep pattern, run to confirm no other hardcoded corpus-count assertion exists outside the D-E suite set):
```bash
grep -rn "examples/README\|== 6\|== 7\|assert len(" tests/scripts/test_backward_compatibility.py tests/scripts/test_maestro_coverage_invariant.py tests/scripts/test_maestro_cross_surface_consistency.py tests/scripts/test_catalog_drift_guard.py tests/scripts/test_affected_assets_wiring.py
```
Hits: `test_backward_compatibility.py:292` (`DETECTION_AGENT_PATHS == 1`, unrelated — detection-agent glob), `test_backward_compatibility.py:344` (`findings == 1`, unrelated, single-example scoped), `test_maestro_cross_surface_consistency.py:194` (`matches == 1`, unrelated, single-example scoped), `test_affected_assets_wiring.py:152` and `:1105` (`VALID_ASSET_TAGS == 6`, the frozen F-260 asset-tag enum — unrelated to example/corpus count). None reference the examples corpus cardinality. Confirms the two files below are the complete at-risk set.

### Enumerated At-Risk Tests (for T015 co-update reference)

| File | Mechanism | Includes `multi-tenant-rag-app` today? | Co-update needed when T014/T015 land? |
|---|---|---|---|
| `tests/scripts/test_backward_compatibility.py` — `BASELINE_EXAMPLES` (line 45, static list of 6) | Hardcoded enumeration, NOT auto-discovered. Drives `test_unmodified_examples_byte_identical_pdfs` (PDF byte-identity vs `.baseline`). | No. | **No.** The 5-artifact set T014/T015 commit for `multi-tenant-rag-app` (`threats.md threat-report.md risk-scores.md risk-scores.sarif threats.sarif`) does NOT include a `security-report.pdf.baseline`. Per the file's own docstring (lines 15–24), examples are excluded from this list "by simply not appearing" — this is the documented mechanism for opt-out, matching this feature's scope exactly. Landing the 5 artifacts will not add a new parametrize case here and will not flip this test. T015 should NOT add `multi-tenant-rag-app` to `BASELINE_EXAMPLES` (no PDF baseline exists to compare against).|
| `tests/scripts/test_maestro_coverage_invariant.py` — `_discover_example_threats()` (line 56–62, dynamic `REPO_ROOT.glob("examples/**/threats.md")`) | Live glob at collection time, self-healing by design (docstring: "No snapshot counts are hardcoded"). | N/A — discovers whatever exists at collection time. | **No manual pin**, but **behavior WILL change automatically**: once `examples/multi-tenant-rag-app/threats.md` is committed (T014/T015), the next collection will add one new parametrized case (`test_maestro_table_covers_all_seven_layers[examples/multi-tenant-rag-app/threats.md]`). This case will PASS only if the committed file's "Risk by MAESTRO Layer" table carries all 7 canonical L1–L7 rows — which is exactly what T014's own FR-012 gate (`grep -c "^| L[1-7] " examples/multi-tenant-rag-app/threats.md`) is designed to verify BEFORE commit. No code change required in this test file; T015 should simply confirm the FR-012 grep check passed before committing (already in its task description).|
| `tests/scripts/test_maestro_cross_surface_consistency.py` — same glob pattern (line 60) | Live glob, same self-healing mechanism, scoped to named cross-surface fixtures (`microservices` 3-surface check, forced-divergence fixture) rather than iterating the full corpus for assertions. | N/A | **No.** This file's two tests (`test_microservices_three_surfaces_agree`, `test_forced_l7_divergence_is_caught`) are anchored to specific named examples (`microservices` and a synthetic fixture), not to corpus cardinality. The glob-matching line is a shared helper import path, not a per-corpus assertion in this file. No action for T015.|

**At-risk count-pin tests requiring T015 co-update: 0.** Both live corpus-glob tests self-heal automatically; the one static list (`BASELINE_EXAMPLES`) correctly and intentionally excludes `multi-tenant-rag-app` by omission because no PDF baseline is part of this feature's 5-artifact scope. T015 needs no test-file edits for count-pin reasons — only the FR-013 `examples/README.md:15` row-accuracy check (already in its own task line) and confirmation that the MAESTRO all-7-row grep passed.

---

## Overall T002 Verdict

**STATUS: PASS** — 74 passed / 3 skipped (all pre-existing and documented) / 0 failed across the D-E suite set. No inherited reds to triage. Corpus-coupling sweep confirms zero test files require a manual count-pin co-update when the multi-tenant-rag-app artifacts land in Phase 4. Checkpoint cleared — artifact/enabler commits may now proceed (Phase 2 gate satisfied).
