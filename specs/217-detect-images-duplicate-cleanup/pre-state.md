# Pre-State: Extractor Suites (T001)

**Date**: 2026-07-01 · **Branch**: `217-detect-images-duplicate-cleanup` · **Purpose**: KB Entry 15 discipline — freeze the literal pre-change baseline before touching `scripts/extract-report-data.py` or its tests.

## Command

```
.venv/bin/python3 -m pytest tests/scripts/test_extract_report_data.py tests/scripts/test_extractor_contract_fixes.py -q
```

(Equivalent to `python3 -m pytest tests/scripts/test_extract_report_data.py tests/scripts/test_extractor_contract_fixes.py -q` run inside the project's `.venv` — the bare system `python3` has no `pytest` installed; `.venv` is the project-configured environment per `requirements-dev.txt` / `Makefile test` target.)

## Literal Output

```
......................                                                   [100%]
22 passed in 9.70s
```

## Totals

| Metric | Count |
|---|---|
| Passed | 22 |
| Failed | 0 |
| Errors | 0 |
| Skipped | 0 |
| **Total** | **22** |

## Reconciliation Target (for T008/T017)

Pre-state total (22) + 9 new T003 cases = **31 expected post-state total**, zero new failures.

---

## Post-state (T017)

**Date**: 2026-07-01 · **Branch**: `217-detect-images-duplicate-cleanup` · **Purpose**: Close the loop on the T001 baseline after US1–US3 implementation, US2 dogfood cleanup, and Polish (T015–T016) — confirm the actual post-state total reconciles to the target with zero regressions.

### Command

```
.venv/bin/python3 -m pytest tests/scripts/test_extract_report_data.py tests/scripts/test_extractor_contract_fixes.py -q
```

### Literal Output

```
...............................                                          [100%]
31 passed in 13.40s
```

### Totals

| Metric | Count |
|---|---|
| Passed | 31 |
| Failed | 0 |
| Errors | 0 |
| Skipped | 0 |
| **Total** | **31** |

### Reconciliation

| Metric | T001 Pre-state | T017 Post-state | Delta |
|---|---|---|---|
| Total | 22 | 31 | +9 |
| Failed | 0 | 0 | 0 |
| Errors | 0 | 0 | 0 |

22 (pre-state) + 9 new T003 cases (AC-1a–AC-1h + FR-005 deletion-failure) = **31 actual**, matching the expected post-state total exactly. Zero regressions: all 22 pre-existing cases remain green, `test_extractor_contract_fixes.py` is unmodified and fully green (FR-006 compat oracle — confirms two-positional `detect_images` callers are unaffected by the new `cleanup` kwarg), and the 9 new cases are additive only.

### Gated-Suite + Catalog-Drift Cross-Check (T016)

For completeness, the CI-gated 15-module F-248/F-256 pytest subset (`.github/workflows/tachi-pytest.yml`) and the `tachi-catalog-drift.yml` guard were also run locally against committed HEAD (`4680423`) as part of T016 — both green (143 passed/1 skipped/1 xfailed pre-existing-and-unrelated, and 15/15 passed respectively). Full detail in `.aod/results/senior-backend-engineer-polish.md`.
