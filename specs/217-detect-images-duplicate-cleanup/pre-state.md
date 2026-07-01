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
