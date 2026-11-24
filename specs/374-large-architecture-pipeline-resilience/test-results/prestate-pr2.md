# W1′ pre-state census at the cut line (T084)

**Result:** PR 2's pre-state is frozen at `03a8f0d`, the cut line (gate G1). It is the tip of PR 2's branch at its first push, and PR 1's W1 tip. Its code is `main` at `b040fa1` (v4.48.4) plus PR 1's W0 and W1.
- Every CI job that has finished is green, with the same totals twice. PR 2's first run (draft PR #425) and PR 1's run at the same commit (draft PR #423) agree job for job and module for module. PR 2's `tachi-pytest.yml` ubuntu leg finished with the same 896 / 0 / 5. Its macOS leg then finished with the same 900 / 0 / 1 as PR 1's run (section 2).
- The local totals are session 1's W1 post-wave census at the cut line, reused: **4214 passed, 35 failed (27 failures and 8 errors), 38 skipped** of 4287. No CI gate runs any of the 35. They are #365's six, 28 others, and one load-dependent mmdc flake. The other 34 are the same node ids as T001's (sections 5 and 6).
- The F-374 coverage gate reads **98.17%** over four scripts (floor 80%). `tachi_parsers.py`'s ratchet reads **52.2%** (503 of 963 statements). Its gate is still T001's floor, **44.9%** (section 7).

Reading rule for later gates (T085, T127 and PR 2's wave gates): a run regresses only if a node id that passes here fails there, or if a gate total below drops. Skips are named, so that a new skip is visible. A skip that turns into a pass is expected where section 3.1 says its script lands. `prestate.md` (T001) still holds for what this record doesn't repeat: the 23-module table, the first-divergence offsets of #365's six, and the consequence scope (its section 8).

## 1. Frozen state and environment

| Item | Value |
|---|---|
| Date | 2026-11-23 |
| Cut-line commit | `03a8f0d`, "mark W1's tasks done in tasks.md, ahead of gate G1". PR 2's branch `374-pipeline-resilience-track-o` was cut from it and pushed. PR 2 is #425 (draft, base `main` at `b040fa1`); PR 1 is #423 |
| Distance from T001's tip | 41 commits and 279 files after `1c55360`. 212 of the files are the synthetic fixture tree under `tests/scripts/fixtures/large_arch/`. The commits added six test modules and three scripts (`tachi_parts.py`, `tachi_scoring.py`, `tachi-stage.py`), and edited `sarif_common.py`, `tachi_parsers.py`, the two workflows, six agent files and the shared skill references. They touched nothing under `templates/` or `examples/`, and not `extract-report-data.py` |
| Local census | Session 1's W1 post-wave run at `03a8f0d`, reused (T084's brief): the command, the commit and the Python are the same as T001's full census, so nothing was re-run. `python3 -m pytest tests/scripts tests/schemas --timeout=1080` in a scratch clone of the committed tip (H1), Python 3.11.13, macOS, mmdc present. It took 926.7 s and exited 1. It left 36 tracked PNGs modified in its clone (#365, mechanism 2). Its junit and its summary (`wave-01/results.json`, on PR 1's branch) agree on every total. Local totals for a gate below are the sum of that gate's modules in this run |
| CI toolchain | ubuntu-latest = image ubuntu-26.04, Python 3.11.18, pytest 9.2.0, pytest-timeout 2.4.0; `f374-offline` adds pytest-cov 7.1.0 (coverage 7.17.5). `f374-py39-floor`: image ubuntu-24.04, Python 3.9.25, pytest 8.4.2 (the newest that installs on 3.9), pytest-timeout 2.4.0. macos-latest = image macos-26-arm64, Python 3.11.9, pytest 9.2.0 |
| Workflows triggered | Five, on PR 2's first run and on PR 1's run at the same commit: `tachi-pytest.yml`, `tachi-install-fidelity.yml`, `tachi-permissions-verify.yml`, `tachi-maestro-coverage.yml` and `gitleaks.yml`. `tachi-mmdc-preflight.yml` and `tachi-catalog-drift.yml` ran on neither: no `paths:` entry matches the diff. PR 2 has no changes of its own yet, and its first run still started the matrix, because the filters see the PR's whole diff against `main` (290 files) |
| Not yet existing | PR 2's four scripts (`join-threats-md.py`, `attack-chains.py`, `assemble-report.py`, `check-threat-model.py`) and their tests, and PR 1's W2 and W3 scripts (`render-risk-scores.py`, `tachi_scoring_rules.py`, `render-compensating-controls.py`). `test_runtime_floor_374.py` skips its cases for each (section 3.1). T085's entry merge brings in PR 1's three |

## 2. Gate totals (literal)

Totals are passed / failed / skipped. "PR 2 run" is the first CI run on PR 2's branch (run IDs below). "PR 1 run" is the CI run on PR 1's branch at the same commit, on 2026-11-23 at 03:23 UTC, with the same code. "Local" is the sum of the gate's modules in session 1's census (section 1).

| Gate / job | Modules | CI, PR 2 run | CI, PR 1 run (same commit) | Local |
|---|---|---|---|---|
| `tachi-pytest.yml`, ubuntu-latest leg | 23 | **896 / 0 / 5** in 9 m 26 s (run 45286236425, job 138083171935) | 896 / 0 / 5 in 9 m 49 s (run 45105676082, job 137466270032) | n/a (no Linux here) |
| `tachi-pytest.yml`, macos-latest leg | 23 | **900 / 0 / 1** in 42 m 33 s (same run, job 138083171596) | **900 / 0 / 1** in 36 m 07 s (same run, job 137466269544) | 900 / 0 / 1 |
| `tachi-install-fidelity.yml` / `manifest-completeness` | 1 | **15 / 0 / 2** in 4.84 s (run 45286236426, job 138083172098) | 15 / 0 / 2 | 17 / 0 / 0 (macOS has zsh, so the 2 CI skips run) |
| same run / `extraction-fidelity` | 7 | **270 / 0 / 6** in 10.21 s (job 138083172534) | 270 / 0 / 6 | 276 / 0 / 0 (mmdc present) |
| same run / `report-posture` | 2 | **90 / 0 / 0** in 10.09 s (job 138083172588) | 90 / 0 / 0 | 90 / 0 / 0 |
| same run / `f374-offline` | 9 | **2576 / 0 / 34** in 13.32 s (job 138083172587) | 2576 / 0 / 34 | 2577 / 0 / 33 |
| same run / `f374-py39-floor` | 8 | **2546 / 0 / 34** in 7.99 s (job 138083172640) | 2546 / 0 / 34 | 2547 / 0 / 33 (Python 3.11, not 3.9) |
| same run / `f374-macos` | 1 | **355 / 0 / 0** in 0.85 s (job 138083172753) | 355 / 0 / 0 | 355 / 0 / 0 |
| `tachi-permissions-verify.yml` | script | **C1 to C8 pass**, exit 0 (run 45286236561) | same (run 45105676095) | not run |
| `tachi-maestro-coverage.yml` | 2 | **11 / 0 / 2** in 0.22 s (run 45286236411) | 11 / 0 / 2 | 11 / 0 / 2 |
| `gitleaks.yml` (CI parity) | scan | **success** (run 45286236413) | success (run 45105676174) | not run |
| `tachi-mmdc-preflight.yml` | script | not triggered | not triggered | `test_mmdc_preflight.py` 8 / 0 / 0 |
| `tachi-catalog-drift.yml` | 1 | not triggered | not triggered | 16 / 0 / 0 |

How the CI evidence reads:
- **Same totals twice.** Every finished job in PR 2's run matches PR 1's run: the same pass, fail and skip totals, the same per-module counts (section 3), and the same coverage tables (section 7). The code is identical; only the branch differs. That includes PR 2's ubuntu `tachi-pytest.yml` leg (the same 23 per-module counts). PR 1's run is the figure for the macOS leg until PR 2's finishes.
- **Against T001's CI totals** (`b040fa1`). Both pytest legs are up by 226, from `test_cvss_category_defaults.py` growing 22 to 248 (670 to 896 on ubuntu, 674 to 900 on macOS). `extraction-fidelity` is up by 21 (249 to 270) and `report-posture` by 6 (84 to 90); section 3.2 names the modules. `manifest-completeness` (15 / 0 / 2) and `maestro-coverage` (11 / 0 / 2) are unchanged. The three f374 jobs are new.
- **Permissions guard.** It prints T001's lines unchanged: C1 roster (21 agents, 1 allow-listed document), C2 tools, C3 model and C4 frontmatter keys (21 agents each), C5 command keys (6), C6 bash families (3 Bash-capable agents), C7 write locations (21 paths), and the C8 self-test with its five planted mutations. `RESULT: pass (exit 0)`.
- **The macOS leg is the long pole.** In PR 1's run it took 36 m 07 s against 9 m 49 s on ubuntu (PR 2's ubuntu leg: 9 m 26 s). Every push to PR 2 starts `tachi-pytest.yml` while PR 2's diff carries PR 1's work, so each push waits about 36 minutes for the macOS leg. The f374 jobs and the install-fidelity jobs finish in under a minute each.

## 3. Per-module totals

### 3.1 The f374 modules

Passed / failed / skipped. The CI columns are PR 2's run (PR 1's run gives the same). "Local" is macOS and Python 3.11.13. `f374-macos` runs one module.

| Module | Tests | `f374-offline` (ubuntu, 3.11) | `f374-py39-floor` (ubuntu, 3.9) | `f374-macos` | Local |
|---|---|---|---|---|---|
| `test_tachi_parts.py` | 1272 | 1272/0/0 | 1272/0/0 | | 1272/0/0 |
| `test_tachi_stage.py` | 255 | 255/0/0 | 255/0/0 | | 255/0/0 |
| `test_runtime_floor_374.py` | 77 | 44/0/33 | 44/0/33 | | 44/0/33 |
| `test_tachi_parsers.py` | 69 | 69/0/0 | 69/0/0 | | 69/0/0 |
| `test_sarif_identity.py` | 355 | 354/0/1 | 354/0/1 | 355/0/0 | 355/0/0 |
| `test_fixture_374.py` | 68 | 68/0/0 | 68/0/0 | | 68/0/0 |
| `test_contract_text_374.py` | 236 | 236/0/0 | 236/0/0 | | 236/0/0 |
| `test_cvss_category_defaults.py` | 248 | 248/0/0 | 248/0/0 | | 248/0/0 |
| `test_sarif_common_affected_assets.py` | 30 | 30/0/0 | not in the list | | 30/0/0 |
| **Total** | **2610** | **2576/0/34** | **2546/0/34** (8 modules, 2580 tests) | **355/0/0** | **2577/0/33** (the 9 modules) |

Two things differ between the legs, and both are named:
- `test_sarif_identity.py` has one case that needs a real case-insensitive volume, `test_a_real_case_variant_gives_the_same_uri_on_a_real_case_insensitive_volume`. It skips on ubuntu ("this volume is case-sensitive") and runs on macOS, which is why `f374-macos` exists.
- `test_runtime_floor_374.py` skips 33 cases, one set per script that doesn't exist yet. The skip turns into a pass when the script lands. Of the 33, 20 are PR 2's own scripts and 13 are PR 1's.

| Skipped script | Cases | Lands in | Lane |
|---|---|---|---|
| `scripts/join-threats-md.py` | 5 | PR 2, W2′ | OS |
| `scripts/attack-chains.py` | 5 | PR 2, W2′ | OC |
| `scripts/assemble-report.py` | 5 | PR 2, W2′ | T |
| `scripts/check-threat-model.py` | 5 | PR 2, W3′ | OC |
| `scripts/render-risk-scores.py` | 5 | PR 1, W2 | R1 |
| `scripts/render-compensating-controls.py` | 5 | PR 1, W3 | R2 |
| `scripts/tachi_scoring_rules.py` | 3 | PR 1, W2 | R1b |

`test_tachi_parsers.py` also runs in `extraction-fidelity` (69 passed there too). T150 extends `test_runtime_floor_374.py` for PR 2 (E1); the 20 PR 2 skips turn into passes as the four scripts land.

### 3.2 Modules whose totals moved since T001

| Module | Gate | T001 (`1c55360`) | Cut line | Change |
|---|---|---|---|---|
| `test_cvss_category_defaults.py` | `tachi-pytest.yml` (both legs) and both f374 jobs | 22 | 248 | +226 |
| `test_tachi_parsers.py` | `extraction-fidelity` and both f374 jobs | 48 | 69 | +21 |
| `test_write_confinement.py` | `report-posture` | 78 | 84 | +6 |
| `test_pyyaml_deferred_import.py` | none | 11 (10 pass, 1 fail) | 13 (12 pass, 1 fail) | +2: its new `sarif_common.py` and `tachi_scoring.py` cases pass |

Every other module of the three T001 gates equals T001's section 3, on both CI legs and in the census: the 22 other `tachi-pytest.yml` modules, `test_install_manifest_completeness.py` (15/0/2 on CI, 17/0/0 local), the six other `extraction-fidelity` modules, `test_report_posture_contract.py` (6/0/0) and the two maestro modules (9/0/2 and 2/0/0).

## 4. Skips in the gates, by name

| Gate | Skipped | Reason |
|---|---|---|
| `tachi-pytest.yml`, both CI legs and the census (1) | `test_init_precommit_matrix.py::test_tty_no_flag_default_y` | needs a real TTY |
| `tachi-pytest.yml`, ubuntu only (4) | the four case-variant cases of `test_install_sh_symlink_preflight.py` (61/0/4 on ubuntu, 65/0/0 on macOS) | need a case-insensitive volume; T001's section 4 names them |
| `manifest-completeness`, CI only (2) | `test_manual_install_loop_zsh`, `test_installed_agent_tools_match_matrix[manual-loop-zsh]` | zsh not on the ubuntu PATH |
| `extraction-fidelity`, CI only (6) | `test_extract_report_data.py`: the five `has-*-image` flags and `test_render_mermaid_to_png_completes_with_crafted_entry_in_list` | mmdc not on PATH |
| `maestro-coverage` (2) | `test_maestro_table_covers_all_seven_layers` for `consumer-agent-app` and `predictive-ml-app` | intermediate-format reports with no "Risk by MAESTRO Layer" table |
| `f374-offline` and `f374-py39-floor` (34 each) | 33 in `test_runtime_floor_374.py` (section 3.1) and 1 in `test_sarif_identity.py` | planned scripts that don't exist yet; a case-sensitive volume |
| the census only (2) | `test_backward_compatibility.py`: the 142-branch zero-edit case and `mermaid-agentic-app`'s multi-agent gate case | the first runs only on `142-` branches; the second is excluded by F-142 T033 |

The census's 38 skips are these: 33 floor cases, 2 byte-identity cases, 1 TTY case and 2 maestro cases. There is no xfail in the census or in any gate.

## 5. #365's six reds, by name

All six sit in `tests/scripts/test_backward_compatibility.py`, which no workflow runs. In the census the module gave **6 passed, 6 failed, 2 skipped**, the same split as T001. The failing cases are `test_unmodified_examples_byte_identical_pdfs[…]` for each of these examples:

| Failing case | T001's first divergence (section 5 of `prestate.md`) |
|---|---|
| `web-app` | byte 224224, font-subset tag (#365, mechanism 1) |
| `microservices` | byte 261105, same tag |
| `ascii-web-api` | byte 197843, same tag |
| `mermaid-agentic-app` | byte 260842, same tag |
| `free-text-microservice` | byte 221304, same tag |
| `maestro-reference` | byte 52, the page tree's `/Count` (the masking floor #365 describes) |

The census reports pass or fail, not offsets, so the offsets above are T001's and were not re-measured. The 41 commits since T001's tip touched nothing under `templates/` or `examples/` and not `extract-report-data.py` (section 1), so the offsets are expected to hold. Hazard (#365, mechanism 2): the census run left 36 modified tracked PNGs in its clone, as T001's did. That is why every run here was in a scratch clone.

## 6. Full census and the out-of-gate failures

The census is compared with T001's. Session 1's W0 census at its tip gave the same figures as T001's (1730 passed, 34 failed or errored, 5 skipped), so the move since is W1's.

| | T001, `1c55360` | Cut line, `03a8f0d` |
|---|---|---|
| Collected | 1769 | 4287 |
| Passed | 1730 | 4214 |
| Failed | 26 | 27 |
| Errors | 8 | 8 |
| Skipped | 5 | 38 |
| Time | 950.96 s | 926.7 s |
| Gated modules | 36 modules, 1060 tests, 0 failures | 43 modules, 3606 tests: 3570 / 0 / 36 |
| Ungated modules | 31 modules, 709 tests, all 34 failures and errors | 30 modules, 681 tests: 644 / 35 / 2 |

The 7 added gated modules are the six new test modules and `test_sarif_common_affected_assets.py`, which joined `f374-offline`. The 2484 more passes reconcile with section 3: the six new modules give 2230 (1272 + 255 + 44 + 355 + 68 + 236), the moved modules give 255 (226 + 21 + 6 + 2), and one case that passed at T001 failed once here (the flake below).

**The 28 other failures and errors**, in 8 modules that no gate runs. The node ids and the first assertion of each are T001's section 6 unchanged; the assertions were read again from the census junit.

| Module | Cases | Cause (the first assertion) |
|---|---|---|
| `test_human_trust_exploitation.py` | 9 (1 failure, 8 errors) | the regenerated `threats.md` and `threat-report.md` that the wave-5 cases read are not committed |
| `test_mobile_top_10_coverage_bundle_enrichment.py` | 6 | five agent specs are over the 120-line STRIDE cap (135 to 142 lines); one companion file lacks its "Pattern Category 11" header |
| `test_coverage_attestation_in_scope.py` | 3 | the Stream 4 fixtures expect 30 `mitre-atlas` records and the catalog has 36 |
| `test_tool_abuse_enrichment.py` | 3 | `tool-abuse.md` is 152 lines against a 150 cap; a `git show main:…` byte-identity assertion fails in a clone with no local `main`; the regenerated `threats.md` has no `[NEW]` AG finding |
| `test_coverage_attestation_audit.py` | 2 | one covered OWASP record is cited by no agent spec, and another by no detection-patterns category |
| `test_llm10_unbounded_consumption_enrichment.py` | 2 | `denial-of-service.md` is 143 lines (cap 120); `model-theft.md` is 162 (cap 150) |
| `test_ml_top_10_coverage_bundle_enrichment.py` | 2 | `tampering.md` is 138 lines (cap 120); `model-theft.md` is 162 (cap 150) |
| `test_pyyaml_deferred_import.py` | 1 | `scripts/check-citation-urls.py` imports `yaml` at module level, which breaks the stdlib-only load invariant |

**One flake, not a red.** `tests/scripts/test_pdf_page_positioning.py::test_executive_architecture_skip_image_pdf_omits_page` failed once, in the full 15-minute run. `extract-report-data.py` exited 1 in its Mermaid render, because mmdc exited 1 on four attack-tree files. It passed 2 of 2 when re-run alone in the same clone at the same commit. T001's census saw the module green, and F-391's W0 census saw a sibling case (`test_executive_architecture_page_position`) fail and then pass alone in the same way. No gate runs the module. Treat a failure in it during a full census as a flake until it fails alone.

Together the 35 are: #365's 6, the 28 above, and the flake.

## 7. Coverage gate and ratchet floor (E3, ADR-050 D16)

Both come from `f374-offline`, in PR 2's run and in PR 1's run, with identical coverage tables. Python 3.11.18, pytest-cov 7.1.0.

**The F-374 coverage gate** (`tests/scripts/coverage-f374.ini`, in-process runs only, H15). The step prints `Required test coverage of 80.0% reached. Total coverage: 98.17%`.

| Script | Statements | Missed | Cover | Missing lines |
|---|---|---|---|---|
| `scripts/sarif_common.py` | 579 | 15 | 97.41% | 108-122 |
| `scripts/tachi-stage.py` | 524 | 0 | 100.00% | |
| `scripts/tachi_parts.py` | 901 | 25 | 97.23% | 343-344, 384, 386-387, 490-493, 496, 507, 687, 717-718, 785, 1003, 1005, 1017, 1160, 1166, 1186, 1395, 1410-1411, 1442 |
| `scripts/tachi_scoring.py` | 180 | 0 | 100.00% | |
| **Total** | **2184** | **40** | **98.17%** | |

PR 2's four scripts join the gate's `include` list as they land, and the total has to stay at or above 80%.

**The ratchet.** `scripts/tachi_parsers.py` has 963 statements and 460 missed, so 503 are covered (**52.2%**), with `--fail-under=44.9` still the gate. T001's floor was 44.9% (412 of 917). W1 added parser code and tests. `tests/scripts/test_tachi_parsers.py` alone gives the figure (69 passed in 0.29 s), so each new parser function's unit tests go there (H15). Missing lines at the cut line, for `--show-missing` diffs at T127:

```
98-101, 111-112, 293, 297-299, 429, 440, 475-528, 541-544, 553-575, 586-607, 640-656, 665-689, 711-770,
784-789, 803-816, 824-831, 836-838, 848-862, 908, 1118, 1126-1128, 1155-1158, 1165, 1172, 1179, 1357-1359,
1373-1396, 1403-1404, 1431-1438, 1450-1499, 1549, 1578, 1580-1581, 1584-1602, 1632, 1670, 1711, 1775-1787,
1806, 1808-1809, 1812-1866, 1892-1958, 1963-1974, 1979-1996, 2007-2052, 2103-2140, 2151-2154, 2164-2178,
2188-2191
```

## 8. For later tasks

| Task | Use |
|---|---|
| T085 (W2′ entry merge) | The merge brings in PR 1's W2 and W3 work, so the totals move: the 13 PR 1 skips in `test_runtime_floor_374.py` should become passes, and PR 1's new modules and cases join the f374 lists. T085's own record (`w2-entry-pr2.md`) takes the post-merge totals as W2′'s base. This record stays the base for node-id regressions: a case that passes here must pass there |
| T148 and W2′ lanes | The modules they extend are in section 3.1: `test_fixture_374.py` (68), `test_tachi_parts.py` (1272), `test_tachi_stage.py` (255), `test_runtime_floor_374.py` (44 / 0 / 33) and `test_tachi_parsers.py` (69, the ratchet file) |
| T089, T127, TW-CI | Compare each CI leg with section 2. The two CI legs of `tachi-pytest.yml` total 901 tests (896 + 5 skipped on ubuntu, 900 + 1 on macOS). A red that matches nothing in sections 2, 5 or 6 is new |
| T127 (E3) | The gate is 44.9% and the cut-line figure is 52.2% (section 7) |
| Any local run | Use a scratch clone of the committed tip (H1). The full census takes about 15 minutes and leaves 36 modified tracked PNGs in its clone |
| T001's section 8 | Its line numbers date from `1c55360`. The 41 commits since then edited `orchestrator.md` (21 lines added, 6 removed), `threat-report.md` (10 and 2) and `report-assembler.md` (5 and 4), and added 2 lines to each of the first two adapter copies. Re-grep before relying on a line number in its section 8.2 |

How this record was made: the local totals are session 1's junit, parsed per module and checked against its summary; the CI figures are read from the Actions job logs (`gh run view --job <id> --log`, or the jobs API while a run is still going) of PR 2's run and of PR 1's run, and compared module by module. No test ran in a tracked tree (H1).
