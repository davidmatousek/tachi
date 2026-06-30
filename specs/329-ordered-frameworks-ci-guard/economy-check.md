# Economy Gate — Feature 329 (ORDERED_FRAMEWORKS Catalog-Drift CI Guard)

**Date**: 2026-06-30 · **Scope**: 4 changed code files (`git diff main...HEAD`; advisory) · **Verdict**: PASSED — no over-build found

Judgment-based over-build assessment against the laziness ladder in `.claude/rules/code-economy.md` (inline verdict — trivially small diff already reviewed by the Step 5 code-reviewer, which returned APPROVED_WITH_CONCERNS with 0 over-build findings).

| File | Lowest rung satisfied | Verdict |
|------|----------------------|---------|
| `scripts/check-catalog-drift.py` | **Rung 2 (reuse)** — importlib-loads the renderer's own `_load_framework_yaml_records` loader + `ORDERED_FRAMEWORKS` tuple instead of re-implementing the YAML walk; **Rung 3 (stdlib)** — hashlib/json/importlib/pathlib/argparse only, **zero new dependencies**. Minimal fingerprint core + fail-closed sidecar I/O + CLI. No speculative abstraction. | No over-build |
| `scripts/regenerate-ca-baselines.sh` | **Rung 2** — formalizes the pre-existing `baseline-regen.contract.md` manual recipe; reuses `extract-report-data.py` + `typst`. bash 3.2-compatible, no added machinery. | No over-build |
| `tests/scripts/test_catalog_drift_guard.py` | Carve-out (FR-007 mandates a runnable check); 15 focused cases, no redundant scaffolding. | N/A (required check) |
| `tests/scripts/test_init_sh_substitution.py` | One-line xfail reason-string re-point (#329→#345). | Trivial |

**Safety carve-outs** (Section 1) — none shortened: input is all hardcoded repo-relative constants; the sidecar path fails closed on missing/partial/unparseable/member-absent; the `_canonical` isinstance guard fails closed on a malformed record (Architect C-2). Error handling and validation are *added*, not traded away for brevity.

**Conclusion**: The guard is an exemplary rung-2 reuse (loader reuse via importlib is the deliberate, correct choice — re-implementing the YAML walk would have been the anti-pattern). No net-new code reaches for a higher rung where a lower one would do. **No action required.**
