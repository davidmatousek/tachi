# T034 (N4 part) — N4 Set Re-Run at W3 vs W0/W2 Baselines

**Feature**: 373-adopter-install-output-fidelity
**Task**: T034, N4 ungated re-run (per `p0-architect-review.md` §5's rule: "keep the W0 23-module list, or subtract every module named in `.github/workflows/*.yml` from the grep" — the 4 W2-added modules are gated, so N4's boundary does not grow)
**Agent**: `tester`
**W0 commit** (baseline): `0ce39d0`
**W2 commit** (baseline): `4bea6c5`
**W3 commit** (this re-run): `91e4542`
**Compared against**: `specs/373-adopter-install-output-fidelity/test-results-prestate.md` §S1(d)/§S2 (T001) and `test-results/n4-rerun-w2.md` (T033)

**Role boundary**: this document records facts and totals only. No product file or test was edited by this task.

---

## S0. Environment

Scratch clone (per standing rule / #365 — never the main tree):
```bash
git clone -q --no-hardlinks /Users/david/Projects/tachi "$SCR"
```
`$SCR = /private/tmp/claude-501/-Users-david-Projects-tachi/2ad26401-b1da-4436-8824-d43d5ff80457/scratchpad/n4w3/tachi`

Verified `git -C "$SCR" rev-parse --short HEAD` = `91e4542`, `git -C "$SCR" status --short` empty, immediately after cloning.

| Tool | W0 | W2 | W3 | Match? |
|---|---|---|---|---|
| python3 | 3.12.11 | 3.12.11 | 3.12.11 | yes |
| pytest | 9.1.0 | 9.1.0 | 9.1.0 | yes |

All commands below ran with `cwd = $SCR` unless stated otherwise.

---

## S1. What changed since W2 (`4bea6c5` -> `91e4542`)

```bash
git log --oneline 4bea6c5..91e4542
```
7 commits: `20f7d8d` (T033 P0 GO docs, Session 1 handoff), `add7912` (BACKLOG regen), `f04254c` (RC-1 regression test), `7b8a93f` (RC-3 fix), `7cf98f0` (RC-2 fix), `60f3714` (RC-1 fix), `91e4542` (RC-1 test-first record docs).

`git diff --stat 4bea6c5..91e4542` touches exactly 3 production files:
- `scripts/install.sh` — **RC-1**: whole-path existence guard made the first statement of `resolve()` (P0 RC-1, SEC-K3-01 residual).
- `scripts/extract-infographic-data.py` — **RC-2**: `risk-scores.md` parsed once on the tier-1 path; row-count warning only emitted on a readable table (P0 RC-2, K11).
- `scripts/tachi_parsers.py` — **RC-3**: `parse_markdown_table` stop rule changed to `level <= max(matched_level, 2)` (P0 RC-3, K9).

Plus their own tests: `tests/scripts/test_install_sh_symlink_preflight.py`, `tests/scripts/test_extract_infographic_data.py`, `tests/scripts/test_tachi_parsers.py` — **none of which are members of the N4 23-module list** (the latter two are W0 §S1(a)'s "4 fast-workflow modules" group; the first is a K3 module gated under `tachi-install-fidelity.yml`). The remainder of the diff is docs/spec/results files (`NEXT-SESSION.md`, contracts, `data-model.md`, `tasks.md`, `test-results/*`, `BACKLOG.md`).

---

## S2. N4 module-list boundary check (unchanged from W2)

Re-ran the grep from the scratch clone root:
```bash
grep -lE "tachi_parsers|extract[-_]infographic[-_]data|extract[-_]report[-_]data" tests/scripts/test_*.py | sort
```
**35 files matched** — same count as W2 (31 at W0 + the same 4 W2-added modules: `test_extraction_sibling_parity.py`, `test_gemini_request_contract.py`, `test_install_manifest_completeness.py`, `test_report_posture_contract.py`). Confirmed via `grep` on `.github/workflows/*.yml` that all 4 are still referenced exclusively inside `tachi-install-fidelity.yml` (gated) — no workflow file changed between W2 and W3 (confirmed by the `--stat` diff in S1), so the gating is unchanged. Per P0 §5's rule, **N4 stays the identical W0 23-module list** — no re-derivation of membership was needed beyond this confirmation.

---

## S3. Per-module re-run: the W0 §S1(d) 23-module list

Command (repeated per module, identical to T001/T033):
```bash
python3 -m pytest tests/scripts/<module>.py -v > out/<module>.stdout 2> out/<module>.stderr
```
Wall clock: 2026-10-06T15:28:10Z -> 15:29:03Z (53s; W0 was 50s, W2 was 48s — process-startup/machine-load noise, not behavioral).

| # | Module | W0/W2 totals | W3 totals | Status-transition? |
|---|---|---|---|---|
| 1 | `test_attack_chain_extraction.py` | 27 passed | 27 passed | none |
| 2 | `test_attack_chains.py` | 26 passed | 26 passed | none |
| 3 | `test_backward_compatibility.py` | 6 failed, 6 passed, 2 skipped | 6 failed, 6 passed, 2 skipped | none (same 6 FAILED + same 2 SKIPPED node ids; 1 of 6 carries the known W2 signature — see S4) |
| 4 | `test_catalog_drift_guard.py` | 16 passed | 16 passed | none |
| 5 | `test_coverage_attestation.py` | 16 passed | 16 passed | none |
| 6 | `test_coverage_attestation_in_scope.py` | 3 failed, 16 passed | 3 failed, 16 passed | none |
| 7 | `test_coverage_attestation_pagination.py` | 5 passed | 5 passed | none |
| 8 | `test_coverage_attestation_tiers.py` | 7 passed | 7 passed | none |
| 9 | `test_coverage_percentage_computation.py` | 48 passed | 48 passed | none |
| 10 | `test_finding_pattern_parser.py` | 59 passed, 5 warnings | 59 passed, 5 warnings | none |
| 11 | `test_human_trust_exploitation.py` | 1 failed, 24 passed, 8 errors | 1 failed, 24 passed, 8 errors | none |
| 12 | `test_maestro_coverage_invariant.py` | 9 passed, 2 skipped | 9 passed, 2 skipped | none |
| 13 | `test_maestro_cross_surface_consistency.py` | 2 passed | 2 passed | none |
| 14 | `test_mmdc_preflight.py` | 8 passed | 8 passed | none |
| 15 | `test_pattern_classification_rules.py` | 15 passed | 15 passed | none |
| 16 | `test_pattern_extraction.py` | 33 passed | 33 passed | none |
| 17 | `test_pattern_synthesis.py` | 39 passed | 39 passed | none |
| 18 | `test_pdf_page_positioning.py` | 2 passed | 2 passed | none |
| 19 | `test_project_name_parser.py` | 16 passed | 16 passed | none |
| 20 | `test_pyyaml_deferred_import.py` | 1 failed, 10 passed | 1 failed, 10 passed | none |
| 21 | `test_smoke.py` | 1 passed | 1 passed | none |
| 22 | `test_source_attribution.py` | 9 passed | 9 passed | none |
| 23 | `test_tool_abuse_enrichment.py` | 3 failed, 14 passed | 3 failed, 14 passed | none |

**Grand total**: W0 = W2 = W3 = **408 passed, 14 failed, 4 skipped, 8 errors (434 collected)** — identical across all three commits.

**Node-id-level check** (not just aggregate counts): every `FAILED`/`ERROR` line (`grep -h "^FAILED\|^ERROR" out/*.stdout`) and every `SKIPPED` line across all 23 captures was extracted and compared against the W0/W2 red set (prestate.md §S2; `n4-rerun-w2.md` §S2/§S3.3):
- All 6 `test_backward_compatibility.py::test_unmodified_examples_byte_identical_pdfs[web-app|microservices|ascii-web-api|mermaid-agentic-app|free-text-microservice|maestro-reference]` FAILED node ids — identical.
- All 3 `test_coverage_attestation_in_scope.py::...test_aggregator_matches_expected_fixture[findings_in_scope_only|findings_oos_only|findings_mixed]` FAILED node ids — identical.
- `test_human_trust_exploitation.py::test_no_agp_te_prose_synthesis` FAILED, plus all 8 `test_wave5_*` ERROR node ids — identical.
- `test_pyyaml_deferred_import.py::test_yaml_import_is_function_scoped[check-citation-urls.py]` FAILED — identical.
- All 3 `test_tool_abuse_enrichment.py::{test_tool_abuse_line_count_within_cap, test_categories_1_8_byte_identity_against_main, test_validate_source_attribution_on_regen}` FAILED — identical.
- 4 SKIPPED: `test_backward_compatibility.py::test_feature_142_zero_edit_invariant_on_detection_agents`, `test_backward_compatibility.py::test_feature_142_multi_agent_gate_predicate_false_on_baselines[mermaid-agentic-app]`, `test_maestro_coverage_invariant.py::test_maestro_table_covers_all_seven_layers[consumer-agent-app/sample-report|predictive-ml-app/sample-report]` — identical.

**Zero additions, zero removals, zero status flips across all 23 modules.**

stderr: all 23 modules captured **0 bytes** of OS-level stderr, identical to W0 and W2.

---

## S4. Signature check: the one known PDF divergence

`test_backward_compatibility.py::test_unmodified_examples_byte_identical_pdfs[maestro-reference]` — FAILED at W0, W2, and W3 (no status transition, counted as "none" in S3). Per P0 §5, this signature changed class between W0 and W2 (font-subset-tag drift -> page-count mismatch), attributed to K13.1 M5 and ruled **intended** (no baseline regen, NFR-8; #364 absorbs it). At W3:

| | W2 (`4bea6c5`) | W3 (`91e4542`) |
|---|---|---|
| Baseline size | 7,034,341 bytes | 7,034,341 bytes (unchanged — RC-1/RC-2/RC-3 touch no `examples/` content) |
| Generated size | 7,073,393 bytes | 7,073,393 bytes (unchanged) |
| First divergence offset | byte 52 | byte 52 (unchanged) |
| Baseline bytes at divergence | `/Count 86` | `/Count 86` (unchanged) |
| Generated bytes at divergence | `/Count 88` | `/Count 88` (unchanged) |

**Byte-for-byte identical signature to W2.** Expected: none of RC-1/RC-2/RC-3 touch `templates/`, `scripts/extract-report-data.py`, or any K13.1 code path.

The other 5 parametrizations (`web-app`, `microservices`, `ascii-web-api`, `mermaid-agentic-app`, `free-text-microservice`) were checked: all 5 still show the `ZZMJWG+` -> `SPUEUJ+` font-subset-tag divergence class, each at its own example-specific byte offset (224224 / 261105 / 197843 / 260842 / 221304 respectively) — same class W0 and W2 described, just naturally example-specific offsets since each generated PDF has a different byte layout. No new divergence class appeared anywhere.

---

## S5. RC-2 stderr relevance check (K11, maestro-reference / consumer-agent-app)

RC-2 removes a duplicate "could not find Scored Threat Table" line and a false "rows (0)" line from `extract-infographic-data.py`'s stderr, on `maestro-reference` and `consumer-agent-app/sample-report`. That code path is exercised by the oracle snapshot (`snapshot.sh`, prestate.md §S4), not by any assertion inside the N4 23-module list — the module that owns `extract-infographic-data.py`'s own unit coverage (`test_extract_infographic_data.py`) is in W0 §S1(a)'s 4-module group, not N4. Consistent with that: **every one of the 23 N4 modules captured 0 stderr bytes** at W0, W2, and W3 alike — RC-2's stderr change is invisible to this set by construction, exactly as expected. (RC-2's own regression test, per P0 §9, lands in `test_extract_infographic_data.py`, outside this report's scope.)

---

## S6. Git status

**Scratch clone** (`$SCR`): `git status --short` shows **36 modified tracked PNGs** under `examples/{agentic-app/sample-report,maestro-reference,mermaid-agentic-app}/{attack-chains,attack-trees}/` — the expected #365 re-render hazard the scratch-clone rule exists to contain (W2 saw 33; the small count difference run-to-run is non-behavioral PNG-render variance, not a regression signal — none of the PDF/JSON/node-id comparisons above are keyed off working-tree PNG state). Disposable; never leaves the scratch clone.

**Main tree** (`/Users/david/Projects/tachi`): `git status --short` was empty before this file was written. The only change this task introduces to the main tree is this record file itself — no pytest, extractor, or `install.sh` invocation ran against the main tree at any point.

---

## S7. Commands used

```bash
# Clone
git clone -q --no-hardlinks /Users/david/Projects/tachi "$SCR"
git -C "$SCR" rev-parse --short HEAD   # confirmed 91e4542

# N4 boundary re-check (from $SCR root)
grep -lE "tachi_parsers|extract[-_]infographic[-_]data|extract[-_]report[-_]data" tests/scripts/test_*.py | sort
grep -n "test_extraction_sibling_parity\|test_gemini_request_contract\|test_install_manifest_completeness\|test_report_posture_contract" .github/workflows/*.yml

# Per-module run (repeated for each of the 23 W0-list modules, from $SCR root)
python3 -m pytest tests/scripts/<module>.py -v > out/<module>.stdout 2> out/<module>.stderr
```

Full module list run (identical to T001's §S1(d) / T033's §S2 order, 23 modules):
`test_attack_chain_extraction.py`, `test_attack_chains.py`, `test_backward_compatibility.py`, `test_catalog_drift_guard.py`, `test_coverage_attestation.py`, `test_coverage_attestation_in_scope.py`, `test_coverage_attestation_pagination.py`, `test_coverage_attestation_tiers.py`, `test_coverage_percentage_computation.py`, `test_finding_pattern_parser.py`, `test_human_trust_exploitation.py`, `test_maestro_coverage_invariant.py`, `test_maestro_cross_surface_consistency.py`, `test_mmdc_preflight.py`, `test_pattern_classification_rules.py`, `test_pattern_extraction.py`, `test_pattern_synthesis.py`, `test_pdf_page_positioning.py`, `test_project_name_parser.py`, `test_pyyaml_deferred_import.py`, `test_smoke.py`, `test_source_attribution.py`, `test_tool_abuse_enrichment.py`.

---

## Verdict

**PASS.** 0 status transitions, 0 new reds, 0 fixed reds, across W0 -> W2 -> W3 (408 passed, 14 failed, 4 skipped, 8 errors at all three commits). The one pre-existing signature change (W0->W2: font-subset-tag drift -> page-count mismatch on `maestro-reference`, attributed to K13.1/M5, ruled intended) is stable and byte-for-byte unchanged at W3. RC-1, RC-2, and RC-3 — the three P0-required changes that landed in this W3 commit — introduced no regression and no new divergence anywhere in the ungated N4 set. **No unattributed delta.**
