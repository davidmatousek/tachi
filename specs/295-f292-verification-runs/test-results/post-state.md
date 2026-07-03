# T020 — Post-State Suite Totals vs Pre-State (FR-019/FR-020 closure cross-check)

**Date**: 2026-07-03
**Branch**: `295-f292-verification-runs` @ `b98295f` (HEAD at time of this run)
**Purpose**: Re-run the identical D-E suite set captured in `test-results/pre-state.md` (committed `2a3e6c8`, before any US1/US2/US3 artifact commits) now that all landed phases (US1 commit `bfd90a3`, FR-014 enabler `995359f`, US2 disposition `eba3a09`, T012 mark `b98295f`) are on the branch. Every flip from pre-state MUST be attributed to a named commit — no silent absorption (KB Entry 15 discipline).

---

## 1. `test_backward_compatibility.py` (incl. slow PDF suite)

**Command**: `python3 -m pytest tests/scripts/test_backward_compatibility.py -v --timeout=1080`

**Verbatim summary line**:
```
======================== 13 passed, 1 skipped in 22.04s ========================
```

Identical to pre-state (13 passed / 1 skipped / 0 failed). The one skip is the same pre-existing, documented `mermaid-agentic-app` SC-003 narrowed-interpretation case. **No flip.**

---

## 2. `test_maestro_coverage_invariant.py` + `test_maestro_cross_surface_consistency.py`

**Command**: `python3 -m pytest tests/scripts/test_maestro_coverage_invariant.py tests/scripts/test_maestro_cross_surface_consistency.py -v`

**Verbatim summary line**:
```
======================== 11 passed, 2 skipped in 0.21s =========================
```

Identical to pre-state (11 passed / 2 skipped / 0 failed). Both skips are the same pre-existing, documented intermediate-format sample reports (`consumer-agent-app`, `predictive-ml-app`). **No flip.** Consistent with the expectation that no `examples/multi-tenant-rag-app/threats.md` was committed (T013 gate FAIL stopped Phase 4 before the artifact-landing step) — the self-healing glob in this suite has nothing new to discover.

---

## 3. `test_catalog_drift_guard.py`

**Command**: `python3 -m pytest tests/scripts/test_catalog_drift_guard.py -v`

**Verbatim summary line**:
```
============================= 15 passed in 0.51s ==============================
```

Identical to pre-state (15 passed / 0 skipped / 0 failed). **No flip.**

---

## 4. `test_affected_assets_wiring.py`

**Command**: `python3 -m pytest tests/scripts/test_affected_assets_wiring.py -v`

**Verbatim summary line**:
```
============================== 39 passed in 0.04s ==============================
```

**FLIP: 35 → 39 passed (+4), 0 skipped, 0 failed.**

### Attribution (all 4 accounted for)

Commit `995359f` ("feat(295): FR-014 input-path URI derivation + covering assertion + hardening-paths anchor (T010/T011)") added exactly 4 new test functions to this module (confirmed via `git diff main -- tests/scripts/test_affected_assets_wiring.py` and cross-checked against `git show 995359f --stat`, which independently shows `tests/scripts/test_affected_assets_wiring.py | 120 +++++++++++++++++++++` for that same commit):

1. `test_fr014_artifact_uri_for_repo_relative_path_matches_second_example` — PASSED
2. `test_fr014_artifact_uri_for_tmp_path_outside_repo_falls_back_to_resolved_posix` — PASSED
3. `test_fr014_build_sarif_wires_derived_uri_into_artifact_location` — PASSED
4. `test_fr014_build_sarif_default_source_uri_preserves_agentic_app_constant` — PASSED

This is exactly the T011 "covering assertion" requirement for the FR-014 `artifact_uri_for()` enabler (T010). No other test in this module changed name, count, or outcome — the pre-existing 35 all still PASSED (verified by full `-v` pass-list inspection, not just the summary count). **Fully attributed; zero unexplained delta.**

---

## Aggregate Totals — Pre → Post Delta Table

| Suite | Pre (P/S/F) | Post (P/S/F) | Delta | Attribution |
|---|---|---|---|---|
| test_backward_compatibility.py | 13/1/0 | 13/1/0 | none | — |
| test_maestro_coverage_invariant.py + test_maestro_cross_surface_consistency.py | 11/2/0 | 11/2/0 | none | — |
| test_catalog_drift_guard.py | 15/0/0 | 15/0/0 | none | — |
| test_affected_assets_wiring.py | 35/0/0 | 39/0/0 | **+4 passed** | 4 new FR-014 URI-derivation assertions, commit `995359f` (T010/T011) |
| **Total** | **74/3/0** | **78/3/0** | **+4 passed, 0 new skips, 0 failed** | fully attributed above |

**Verdict: PASS.** Every flip between pre-state and post-state is attributed to a specific named commit with the specific test names identified. Skip count is byte-identical (same 3 pre-existing, documented skips). Zero failures in either state. No silent absorption.
