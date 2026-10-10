# T033 (N4 part) — N4 Set Re-Run at W2 vs W0 Pre-State

**Feature**: 373-adopter-install-output-fidelity
**Task**: T033, N4 re-run part (C-2, R-8)
**Agent**: `tester`
**W0 commit** (baseline): `0ce39d0`
**W2 commit** (this re-run): `4bea6c5` (pushed HEAD at end of W2)
**Compared against**: `specs/373-adopter-install-output-fidelity/test-results-prestate.md` §S1(d) and §S2 (T001)

**Role boundary**: this document records facts and first-look causes only. Attribution (deciding *why* a delta happened and what to do about it) is the architect's job at P0.

---

## S0. Environment

Scratch clone (per standing rule / #365 — never the main tree):
```bash
git clone --no-hardlinks /Users/david/Projects/tachi "$SCR"
```
`$SCR = /private/tmp/claude-501/-Users-david-Projects-tachi/5f109275-e25c-4be3-ac01-c337226261e5/scratchpad/t033-n4/tachi`

Verified `git -C "$SCR" rev-parse --short HEAD` = `4bea6c5` immediately after cloning and again after all runs below.

| Tool | W0 version | W2 version | Match? |
|---|---|---|---|
| python3 | 3.12.11 | 3.12.11 | yes |
| pytest | 9.1.0 | 9.1.0 | yes |
| typst | 0.14.2 (unknown hash) | 0.14.2 (unknown hash) | yes |

All commands below ran with `cwd = $SCR` unless stated otherwise.

**W0 raw evidence used for this comparison**: in addition to the prestate doc's prose summary, this session's own scratchpad still had T001's raw per-module `pytest -v` stdout/stderr logs at `$SESSION_SCRATCHPAD/w0-t001/logs/n4/<module>.std{out,err}.log` (same session, same task T001, produced immediately before the prestate doc was written). These were used to check node-id-level and byte-offset-level detail that the prestate doc's prose summarizes but does not enumerate line-by-line. Nothing about this re-run depended on the main tree.

---

## S1. N4 grep re-derivation

Same command as T001, run from the scratch clone root:
```bash
grep -lE "tachi_parsers|extract[-_]infographic[-_]data|extract[-_]report[-_]data" tests/scripts/test_*.py | sort
```

| | W0 (`0ce39d0`) | W2 (`4bea6c5`) |
|---|---|---|
| Files matched | 31 | **35** |

**New matches (4)** — present in W2, absent from W0's 31:
- `tests/scripts/test_extraction_sibling_parity.py`
- `tests/scripts/test_gemini_request_contract.py`
- `tests/scripts/test_install_manifest_completeness.py`
- `tests/scripts/test_report_posture_contract.py`

**Dropped matches**: none — all 31 of W0's files still match in W2.

These 4 new modules are test files added during W1/W2 of Feature 373 itself (their names align with the K9–K15 work threads visible in the commit log — request-contract, sibling-parity, manifest-completeness, and posture-contract tests). They are **not** part of "the W0 list" this task was scoped to re-run (§S1(d)'s 23-module table), so they were not executed here and carry no W0-vs-W2 comparison row below. Flagging them is informational only: a future task would need to decide whether N4's boundary should formally grow to include them.

---

## S2. Per-module re-run: the W0 §S1(d) 23-module list

Command (repeated per module, identical to T001):
```bash
python3 -m pytest tests/scripts/<module>.py -v
```
stdout and stderr captured separately per module to scratch files under `$WORK/out/<module>.std{out,err}`.

Wall clock: 2026-09-28T07:05:45Z -> 07:06:33Z (48s; W0 was 50s for the same 23 modules).

| # | Module | W0 totals | W2 totals | Node-id-level status diff | stderr bytes (W0 / W2) |
|---|---|---|---|---|---|
| 1 | `test_attack_chain_extraction.py` | 27 passed | 27 passed | none | 0 / 0 |
| 2 | `test_attack_chains.py` | 26 passed | 26 passed | none | 0 / 0 |
| 3 | `test_backward_compatibility.py` | 6 failed, 6 passed, 2 skipped | 6 failed, 6 passed, 2 skipped | none (same 6 FAILED + same 2 SKIPPED node ids) — **but see S3.1: 1 of the 6 FAILED has a changed failure signature** | 0 / 0 |
| 4 | `test_catalog_drift_guard.py` | 16 passed | 16 passed | none | 0 / 0 |
| 5 | `test_coverage_attestation.py` | 16 passed | 16 passed | none | 0 / 0 |
| 6 | `test_coverage_attestation_in_scope.py` | 3 failed, 16 passed | 3 failed, 16 passed | none | 0 / 0 |
| 7 | `test_coverage_attestation_pagination.py` | 5 passed | 5 passed | none | 0 / 0 |
| 8 | `test_coverage_attestation_tiers.py` | 7 passed | 7 passed | none | 0 / 0 |
| 9 | `test_coverage_percentage_computation.py` | 48 passed | 48 passed | none | 0 / 0 |
| 10 | `test_finding_pattern_parser.py` | 59 passed, 5 warnings | 59 passed, 5 warnings | none | 0 / 0 |
| 11 | `test_human_trust_exploitation.py` | 1 failed, 24 passed, 8 errors | 1 failed, 24 passed, 8 errors | none | 0 / 0 |
| 12 | `test_maestro_coverage_invariant.py` | 9 passed, 2 skipped | 9 passed, 2 skipped | none | 0 / 0 |
| 13 | `test_maestro_cross_surface_consistency.py` | 2 passed | 2 passed | none | 0 / 0 |
| 14 | `test_mmdc_preflight.py` | 8 passed | 8 passed | none | 0 / 0 |
| 15 | `test_pattern_classification_rules.py` | 15 passed | 15 passed | none | 0 / 0 |
| 16 | `test_pattern_extraction.py` | 33 passed | 33 passed | none | 0 / 0 |
| 17 | `test_pattern_synthesis.py` | 39 passed | 39 passed | none | 0 / 0 |
| 18 | `test_pdf_page_positioning.py` | 2 passed | 2 passed | none | 0 / 0 |
| 19 | `test_project_name_parser.py` | 16 passed | 16 passed | none | 0 / 0 |
| 20 | `test_pyyaml_deferred_import.py` | 1 failed, 10 passed | 1 failed, 10 passed | none | 0 / 0 |
| 21 | `test_smoke.py` | 1 passed | 1 passed | none | 0 / 0 |
| 22 | `test_source_attribution.py` | 9 passed | 9 passed | none | 0 / 0 |
| 23 | `test_tool_abuse_enrichment.py` | 3 failed, 14 passed | 3 failed, 14 passed | none | 0 / 0 |

**Grand total across 23 modules**: W0 = 408 passed, 14 failed, 4 skipped, 8 errors (434 collected). W2 = **408 passed, 14 failed, 4 skipped, 8 errors (434 collected)** — identical.

Per-module summary-line durations differ slightly run to run (process-startup / machine-load noise, e.g. `test_pdf_page_positioning.py` 20.94s at W0 vs 18.51s at W2) — these are not behavioral deltas and are not itemized further.

---

## S3. Deltas

### S3.0 Status-transition deltas (pass→fail, fail→pass, new test, removed test)

**Zero.** A full node-id-level comparison (every `PASSED`/`FAILED`/`ERROR`/`SKIPPED` line, keyed by node id, W0 vs W2) across all 23 modules found no status transitions anywhere. Every node id that existed at W0 still exists at W2 with the identical status. No test was added or removed inside any of the 23 modules.

### S3.1 Signature change within an unchanged-status red (the one real delta)

`test_backward_compatibility.py::test_unmodified_examples_byte_identical_pdfs[maestro-reference]` is **FAILED at both W0 and W2** (no status transition — already counted as "none" in S2's table), but its underlying divergence is a **different class of mismatch** at W2 than at W0:

| | W0 (`0ce39d0`) | W2 (`4bea6c5`) |
|---|---|---|
| Baseline size | 7,034,341 bytes | 7,034,341 bytes (unchanged — confirmed `git diff 0ce39d0..4bea6c5 -- examples/maestro-reference/` is empty) |
| Generated size | 7,034,326 bytes (**15 bytes smaller**) | 7,073,393 bytes (**39,052 bytes larger**) |
| First divergence offset | byte 828,878 | byte 52 |
| Divergence location | `/BaseFont` tag inside an embedded font subset | `/Pages` dict: `/Count` and `/Kids` array (page tree) |
| Baseline bytes at divergence | `...2f5a 5a4d 4a57 47...` = `/ZZMJWG+...` | `...2f43 6f75 6e74 2038 36...` = `/Count 86...` |
| Generated bytes at divergence | `...2f53 5055 4555 4a...` = `/SPUEUJ+...` | `...2f43 6f75 6e74 2038 38...` = `/Count 88...` |
| Failure class | Font-subset-tag drift (same class as the other 5 parametrizations) | **Page-count mismatch: generated PDF has 2 more pages (88) than baseline (86)** |

The other 5 parametrizations (`web-app`, `microservices`, `ascii-web-api`, `mermaid-agentic-app`, `free-text-microservice`) are **byte-for-byte identical between W0 and W2** — same offset, same context bytes, same size delta, same `ZZMJWG+`→`SPUEUJ+` font-subset-tag pattern W0 described. Only `maestro-reference` changed class.

**First-look cause** (not attribution): the committed `.pdf.baseline` for `maestro-reference` is unchanged between W0 and W2 (confirmed via `git diff`), and the local `typst` toolchain version is identical (0.14.2) in both runs, ruling out a baseline-drift or toolchain-version explanation. Of the 51 commits between `0ce39d0` and `4bea6c5`, 13 touch `templates/` or `scripts/extract-report-data.py`, including several from the K11/K13-posture work threads (e.g. `1e1ed70` "K13-posture emit the risk posture into report-data.typ", `fa7fa10` "K13-posture cover renders posture from data, with a stale-data guard", `a4ea956` "K13.1 recommendation fallback and placeholder on every data tier"). These are plausible candidates for newly-added report content that would push `maestro-reference`'s generated page count from 86 to 88, but confirming which commit(s) and why is P0 architect work, not this task's.

### S3.2 New reds outside the W0 set

None. Every FAILED/ERROR node id observed at W2 across the 23-module W0 list is a node id that was already FAILED/ERROR at W0 (§S2 "none" column). No module outside the W0 red set produced a failure.

### S3.3 Every W0 red — persistence check

All 22 W0 reds (§S2 of the prestate doc) persist at W2 with identical status. Detail beyond status (verified against W0's raw per-node logs, not just the prestate doc's prose):

| W0 # | Node id(s) | W0 cause | Persists unchanged at W2? |
|---|---|---|---|
| 1-6 | `test_backward_compatibility.py::test_unmodified_examples_byte_identical_pdfs[*]` (6x) | PDF byte mismatch, font-subset-tag drift | **5 of 6 unchanged** (byte-identical failure detail); **1 of 6 (`maestro-reference`) has a changed signature** — see S3.1 |
| 7-9 | `test_coverage_attestation_in_scope.py::...test_aggregator_matches_expected_fixture[*]` (3x) | Stale fixture: expects `mitre-atlas.yaml_record_count == 30`, catalog has 36 | Unchanged — same `aggregate`/`expected` dict values (`36` vs `30`) verified byte-for-byte in both runs |
| 10 | `test_human_trust_exploitation.py::test_no_agp_te_prose_synthesis` | Missing untracked `F4-wave5` test-output directory | Unchanged (same assertion, same missing-path cause; the directory remains untracked/absent in this fresh scratch clone) |
| 11-18 | `test_human_trust_exploitation.py::test_wave5_*` (8x, ERROR) | Same missing `F4-wave5` fixture directory | Unchanged — identical 8 node ids, identical ERROR (not FAILED) status |
| 19 | `test_pyyaml_deferred_import.py::test_yaml_import_is_function_scoped[check-citation-urls.py]` | Module-level `import yaml` in `scripts/check-citation-urls.py:44` | Unchanged — identical assertion line (`tests/scripts/test_pyyaml_deferred_import.py:204`) |
| 20 | `test_tool_abuse_enrichment.py::test_tool_abuse_line_count_within_cap` | `tool-abuse.md` is 152 lines, cap is 150 | Unchanged — **exact same line count (152) in both runs**, so the 2-line overage has neither grown nor shrunk between W0 and W2 |
| 21 | `test_tool_abuse_enrichment.py::test_categories_1_8_byte_identity_against_main` | `git show main:...` exits 128 (scratch clone has no local `main` ref) | Unchanged — identical `subprocess.CalledProcessError` command and exit code in both runs; this is a property of the clone recipe, reproduced identically |
| 22 | `test_tool_abuse_enrichment.py::test_validate_source_attribution_on_regen` | No `[NEW]`-tagged `AG-{N}` finding in committed `examples/agentic-app/sample-report/threats.md` | Unchanged — identical `assert []` (empty list) in both runs |

### S3.4 stderr warning-class comparison (vs W0 §S3)

- **OS-level stderr**: 0 bytes in all 23 modules at both W0 and W2 (verified via `stat` byte-count diff — zero differences). Nothing in this bundle's suite writes to the real stderr stream, in either baseline.
- **pytest warnings-summary (stdout reporter feature)**: identical at W0 and W2 — exactly one module (`test_finding_pattern_parser.py`) shows `5x PytestRemovedIn10Warning` ("Class-scoped fixture defined as instance method is deprecated", `_pytest/fixtures.py:1312`), same source line, same test class (`TestParseThreatsFindingsPreFeature142Backward`). No module gained or lost a warnings-summary between W0 and W2.

---

## S4. Commands used

```bash
# Clone
git clone --no-hardlinks /Users/david/Projects/tachi "$SCR"
git -C "$SCR" rev-parse --short HEAD   # confirmed 4bea6c5

# N4 grep re-derivation (from $SCR root)
grep -lE "tachi_parsers|extract[-_]infographic[-_]data|extract[-_]report[-_]data" tests/scripts/test_*.py | sort

# Per-module run (repeated for each of the 23 W0-list modules, from $SCR root)
python3 -m pytest tests/scripts/<module>.py -v > "$WORK/out/<module>.stdout" 2> "$WORK/out/<module>.stderr"
```

Full module list run (identical to T001's §S1(d) table order):
`test_attack_chain_extraction.py`, `test_attack_chains.py`, `test_backward_compatibility.py`, `test_catalog_drift_guard.py`, `test_coverage_attestation.py`, `test_coverage_attestation_in_scope.py`, `test_coverage_attestation_pagination.py`, `test_coverage_attestation_tiers.py`, `test_coverage_percentage_computation.py`, `test_finding_pattern_parser.py`, `test_human_trust_exploitation.py`, `test_maestro_coverage_invariant.py`, `test_maestro_cross_surface_consistency.py`, `test_mmdc_preflight.py`, `test_pattern_classification_rules.py`, `test_pattern_extraction.py`, `test_pattern_synthesis.py`, `test_pdf_page_positioning.py`, `test_project_name_parser.py`, `test_pyyaml_deferred_import.py`, `test_smoke.py`, `test_source_attribution.py`, `test_tool_abuse_enrichment.py`.

---

## S5. Final git status checks

**Scratch clone** (`$SCR`): after all 23 runs, `git status --short` shows 33 modified tracked PNGs under `examples/agentic-app/sample-report/{attack-chains,attack-trees}/`, `examples/maestro-reference/{attack-chains,attack-trees}/`, and `examples/mermaid-agentic-app/attack-trees/` — this is the expected #365 re-render hazard the scratch-clone rule exists to contain (running this suite re-renders tracked example PNGs). The scratch clone is disposable and this drift never leaves it. It does not affect any comparison above: the PDF byte-diff tests write their generated output to a pytest `tmp_path`, never into `examples/`, and the PDF/JSON assertions compared in this report are keyed off pytest's own captured output, not off the working tree's PNG state.

**Main tree** (`/Users/david/Projects/tachi`):
```
$ git -C /Users/david/Projects/tachi status --short
(empty)
```
Clean. No pytest, extractor, or `install.sh` invocation ran against the main tree at any point in this task.
