# W0 pre-state census (T001)

**Result:** the pre-state is frozen at `1c55360`, the committed tip of `374-large-architecture-pipeline-resilience`. Its code is `main` at `b040fa1` (v4.48.4), because the branch adds documents only.
- Every gate is green at that code, on CI and in a scratch clone. The scratch totals equal CI's wherever the environment matches.
- #365's six reds are the only failures in the byte-identity suite. The full census has 28 more failures and errors, all in modules that no gate runs.
- `tachi_parsers.py`'s ratchet floor (E3) is **44.9%**: 412 of 917 statements.

Reading rule for later gates (T026, T069, T084, T127): a run regresses only if a node id that passes here fails there, or if a gate total below drops. Skips are named so that a new skip is visible.

## 1. Frozen state and environment

| Item | Value |
|---|---|
| Date | 2026-11-22 |
| Committed tip | `1c55360`, nine commits ahead of `main` at `b040fa1`. The diff is 17 files, all under `specs/374-*` and `docs/` (the ADR, the PRD, `INDEX.md`, `BACKLOG.md`) |
| Workflow triggers | None of the six workflows' `paths:` filters matches those 17 files, so the draft PR (#423) fires none of them. The `push:[main]` runs at `b040fa1` stand for the tip |
| Scratch clones | Fresh `git clone --branch 374-large-architecture-pipeline-resilience` of the local repository, one per job (gated set, full census, byte-identity, each install-fidelity job, each co-fired gate, the ratchet). `git log -1` read `1c55360` in every one. The main checkout and the lane worktree ran nothing (H1) |
| Local toolchain | macOS 26.6 (arm64); Python 3.11.13 (uv venv); pytest 9.2.0; pytest-timeout 2.4.0; pytest-cov 7.1.0; coverage 7.17.4; PyYAML 6.0.4; Typst 0.14.2; mmdc 11.12.0; jq 1.7.1; `/bin/bash` 3.2.57 |
| Local environment | A scrubbed environment (`env -i`, then `HOME`, `USER`, `LANG`, `TERM`, `TMPDIR` and an explicit `PATH`), so no ambient secret or virtualenv reaches a test. "CI-shaped" PATH: system directories only, so no Typst and no mmdc (the ubuntu runner's shape; Typst is added for report-posture and mmdc-preflight, as their workflows do). "Local" PATH: Homebrew first, so Typst and mmdc are present |
| CI toolchain (`b040fa1`) | ubuntu-latest = image ubuntu-26.04, Python 3.11.18; macos-latest: Python 3.11.9, `/bin/bash` 3.2.57; pytest 9.2.0, pytest-timeout 2.4.0 and PyYAML 6.0.4, the same versions as the local venv; report-posture: Typst 0.15.1 (setup-typst, `latest`) |
| Not yet existing | `f374-offline`, `f374-py39-floor`, `f374-macos` and the new modules (`test_tachi_parts.py` and the rest) have no pre-state. W1 creates them (T022) |

## 2. Gate totals (literal)

Totals are passed / failed / skipped. "CI" is a GitHub Actions run, cited by ID. "Scratch" is a local run in a fresh clone (macOS, Python 3.11.13).

| Gate / job | Modules | CI at `b040fa1` | Scratch clone |
|---|---|---|---|
| `tachi-pytest.yml`, ubuntu-latest leg | 23 | **670 / 0 / 5** in 11 m 04 s (run 44962377970, job 137023792115) | n/a (no Linux here) |
| `tachi-pytest.yml`, macos-latest leg | 23 | **674 / 0 / 1** in 32 m 32 s (same run, job 137023791910) | **674 / 0 / 1** in 14 m 44 s (`--timeout=1080`, local PATH) |
| `tachi-install-fidelity.yml` / `manifest-completeness` | 1 | **15 / 0 / 2** in 3.7 s (run 44962378018) | 17 / 0 / 0 (macOS has zsh, so the 2 CI skips run) |
| `tachi-install-fidelity.yml` / `extraction-fidelity` | 7 | **249 / 0 / 6** in 6.8 s (same run) | CI-shaped PATH: 249 / 0 / 6. Local PATH (mmdc present): 255 / 0 / 0 |
| `tachi-install-fidelity.yml` / `report-posture` | 2 | **84 / 0 / 0** in 7.7 s (same run; `TACHI_REQUIRE_TYPST=1`, Typst 0.15.1) | 84 / 0 / 0 (Typst 0.14.2) |
| `tachi-permissions-verify.yml` | script | **C1 to C8 pass**, exit 0 (run 44962378072); table in section 4 | same lines, exit 0; the other five steps exit 0 |
| `tachi-maestro-coverage.yml` | 2 | **11 / 0 / 2** (PR run 44959288486, at `1ece22b`, #421's head) | 11 / 0 / 2 |
| `tachi-mmdc-preflight.yml` | script | **pass**: exit 1, all three tokens present (PR run 44930608231, at `1b8f0ac`, #392's head) | exit 1, all three tokens present |
| `tachi-catalog-drift.yml` | 1 | **16 / 0 / 0** (push run 44936411675 at `e83ca6b`) | 16 / 0 / 0 |

How the CI evidence reaches the tip:
- **Same totals twice.** The previous `main` push (`a7f9ec5`, run 44962274746) gave the same pytest totals: 670 / 0 / 5 and 674 / 0 / 1.
- **PR-only and path-filtered gates.** maestro-coverage and mmdc-preflight have no `push` trigger, and catalog-drift's last push run is `e83ca6b`. Between each cited SHA and `b040fa1`, no file in the gate's `paths:` anchor differs, with one exception: mmdc-preflight's `README.md` and `scripts/install.sh` differ by the release-please version strings only. The script it runs, `scripts/extract-report-data.py`, is identical.
- **Release PRs.** On release-please PRs (#422 here) these workflows end "failure" with no jobs (a workflow-file issue, seen on every release PR). That is not a gate result, and the `push:[main]` runs after the merge are green.
- **The macOS leg is the long pole.** It takes about three times the ubuntu leg (32 m 32 s against 11 m 04 s), so a push that triggers `tachi-pytest.yml` waits about 33 minutes for it.

## 3. Per-module totals

Passed / failed / skipped for the 23 modules of the `tachi-pytest.yml` run list. The CI columns are the two legs of run 44962377970 (section 2). Both CI legs and the scratch macOS run use the same command, `-v --timeout=1080`.

| Module | Tests | CI ubuntu | CI macOS | Scratch macOS |
|---|---|---|---|---|
| `test_init_sh_substitution.py` | 2 | 2/0/0 | 2/0/0 | 2/0/0 |
| `test_init_sh_adversarial.py` | 2 | 2/0/0 | 2/0/0 | 2/0/0 |
| `test_init_sh_constitution.py` | 1 | 1/0/0 | 1/0/0 | 1/0/0 |
| `test_init_sh_self_delete.py` | 3 | 3/0/0 | 3/0/0 | 3/0/0 |
| `test_template_substitute_unit.py` | 8 | 8/0/0 | 8/0/0 | 8/0/0 |
| `test_init_input_unit.py` | 8 | 8/0/0 | 8/0/0 | 8/0/0 |
| `test_substitute_shim_canary.py` | 1 | 1/0/0 | 1/0/0 | 1/0/0 |
| `test_init_sh_defaults_env.py` | 4 | 4/0/0 | 4/0/0 | 4/0/0 |
| `test_template_config_load_unit.py` | 31 | 31/0/0 | 31/0/0 | 31/0/0 |
| `test_template_config_load_integration.py` | 11 | 11/0/0 | 11/0/0 | 11/0/0 |
| `test_template_git_clone_timeout.py` | 6 | 6/0/0 | 6/0/0 | 6/0/0 |
| `test_template_substitute_lint_no_eval.py` | 1 | 1/0/0 | 1/0/0 | 1/0/0 |
| `test_init_precommit_matrix.py` | 6 | 5/0/1 | 5/0/1 | 5/0/1 |
| `test_asset_sensitivity_tags.py` | 26 | 26/0/0 | 26/0/0 | 26/0/0 |
| `test_affected_assets_wiring.py` | 39 | 39/0/0 | 39/0/0 | 39/0/0 |
| `test_owasp_2026_contract.py` | 34 | 34/0/0 | 34/0/0 | 34/0/0 |
| `test_install_sh_symlink_preflight.py` | 65 | 61/0/4 | 65/0/0 | 65/0/0 |
| `test_install_sh_ref_restore.py` | 9 | 9/0/0 | 9/0/0 | 9/0/0 |
| `test_isolated_profile_contract.py` | 202 | 202/0/0 | 202/0/0 | 202/0/0 |
| `test_agent_privilege_guard.py` | 158 | 158/0/0 | 158/0/0 | 158/0/0 |
| `test_gemini_key_env_only.py` | 4 | 4/0/0 | 4/0/0 | 4/0/0 |
| `test_cvss_category_defaults.py` | 22 | 22/0/0 | 22/0/0 | 22/0/0 |
| `test_baseline_owasp_rekey.py` | 32 | 32/0/0 | 32/0/0 | 32/0/0 |
| **Total** | **675** | **670/0/5** | **674/0/1** | **674/0/1** |

The other gated modules (passed / failed / skipped). The CI column is the run cited for that gate in section 2; the scratch columns are macOS, Python 3.11.13.

| Module | Gate | Tests | CI | Scratch, CI-shaped PATH | Scratch, local PATH |
|---|---|---|---|---|---|
| `test_install_manifest_completeness.py` | manifest-completeness | 17 | 15/0/2 | 17/0/0 (macOS has zsh) | n/a |
| `test_tachi_parsers.py` | extraction-fidelity | 48 | 48/0/0 | 48/0/0 | 48/0/0 |
| `test_extract_infographic_data.py` | extraction-fidelity | 60 | 60/0/0 | 60/0/0 | 60/0/0 |
| `test_extract_report_data.py` | extraction-fidelity | 54 | 48/0/6 | 48/0/6 | 54/0/0 |
| `test_extractor_contract_fixes.py` | extraction-fidelity | 8 | 8/0/0 | 8/0/0 | 8/0/0 |
| `test_executive_architecture_payload.py` | extraction-fidelity | 12 | 12/0/0 | 12/0/0 | 12/0/0 |
| `test_gemini_request_contract.py` | extraction-fidelity | 66 | 66/0/0 | 66/0/0 | 66/0/0 |
| `test_extraction_sibling_parity.py` | extraction-fidelity | 7 | 7/0/0 | 7/0/0 | 7/0/0 |
| `test_report_posture_contract.py` | report-posture | 6 | 6/0/0 | 6/0/0 (Typst 0.14.2) | n/a |
| `test_write_confinement.py` | report-posture | 78 | 78/0/0 | 78/0/0 (Typst 0.14.2) | n/a |
| `test_maestro_coverage_invariant.py` | maestro-coverage | 11 | 9/0/2 | 9/0/2 | n/a |
| `test_maestro_cross_surface_consistency.py` | maestro-coverage | 2 | 2/0/0 | 2/0/0 | n/a |
| `test_catalog_drift_guard.py` | catalog-drift | 16 | 16/0/0 | 16/0/0 | n/a |

`extraction-fidelity` has 255 tests. With mmdc off the PATH, 6 skip, as on CI. With mmdc present, all 255 pass, and the clone stayed clean. Each job ran in its own fresh clone.

## 4. Permissions guard, skips and xfails

`tachi-permissions-verify.yml` runs six steps: jq present; `jq empty .claude/settings.json`; the AC-2 cross-check; the §3 and §4 heading greps; python3 present; `check-agent-privileges.py --self-test`. All six exit 0 on CI and in the scratch clone. The guard prints the same lines in both:

| Check | Result | Count |
|---|---|---|
| C1 roster | PASS | 21 agents, 1 allow-listed document |
| C2 tools | PASS | 21 agents |
| C3 model | PASS | 21 agents |
| C4 frontmatter keys | PASS | 21 agents |
| C5 command keys | PASS | 6 commands |
| C6 bash families | PASS | 3 Bash-capable agents |
| C7 write locations | PASS | 21 paths |
| C8 self-test | PASS | five planted mutations, all detected: M1 by C2, M2 to M5 by C1 |

Every skip in the gates, by name:

| Gate | Skipped | Reason |
|---|---|---|
| `tachi-pytest.yml` (both CI legs and the scratch run) | `test_init_precommit_matrix.py::test_tty_no_flag_default_y` | needs a real TTY (`pty.openpty()`) |
| `tachi-pytest.yml`, ubuntu only (4) | `test_install_sh_symlink_preflight.py::test_case_variant_link_into_clone_refused_without_flag`, `…_with_flag`, `test_project_root_case_variant_of_clone_refused`, `test_project_inside_clone_via_case_variant_path_refused` | needs a case-insensitive volume (macOS); the macOS legs run them |
| `manifest-completeness`, CI only (2) | `test_manual_install_loop_zsh`, `test_installed_agent_tools_match_matrix[manual-loop-zsh]` | zsh not on the ubuntu PATH |
| `extraction-fidelity`, CI-shaped only (6) | `test_extract_report_data.py::test_existing_image_flags_unchanged[…]` for the five `has-*-image` flags (funnel, baseball, architecture, maestro-stack, maestro-heatmap), and `test_render_mermaid_to_png_completes_with_crafted_entry_in_list` | mmdc not on PATH |
| `maestro-coverage` (2) | `test_maestro_table_covers_all_seven_layers[examples/consumer-agent-app/sample-report/threats.md]` and `[examples/predictive-ml-app/sample-report/threats.md]` | intermediate-format reports with no "Risk by MAESTRO Layer" table |
| byte-identity (not gated; 2) | `test_feature_142_zero_edit_invariant_on_detection_agents`, `test_feature_142_multi_agent_gate_predicate_false_on_baselines[mermaid-agentic-app]` | the first runs only on `142-` branches; the second is excluded by F-142 T033 |

There is no xfail in any gate. `#419` removed the last one.

## 5. #365's six reds, by name

`tests/scripts/test_backward_compatibility.py` in a fresh clone (local PATH, Typst 0.14.2, mmdc 11.12.0, `SOURCE_DATE_EPOCH` pinned by the test): **6 failed, 6 passed, 2 skipped**, in 17 s. Python 3.11.13 gives the same totals and offsets as Python 3.12.11 did at F-391's W0 (`46aec8d`). No workflow runs this module.

| Failing case (`test_unmodified_examples_byte_identical_pdfs[…]`) | First divergence | Signature |
|---|---|---|
| `web-app` | byte 224224 | font-subset tag `/ZZMJWG+` in the baseline, `/SPUEUJ+` in the render (#365, mechanism 1) |
| `microservices` | byte 261105 | same tag |
| `ascii-web-api` | byte 197843 | same tag |
| `mermaid-agentic-app` | byte 260842 | same tag |
| `free-text-microservice` | byte 221304 | same tag |
| `maestro-reference` | byte **52** | the page tree's `/Count` is 86 in the baseline and 88 in the render. That is the masking floor #365 describes: nothing after byte 52 is compared |

Hazard (#365, mechanism 2): after this one run the clone held **21 modified tracked PNGs** (9 under `examples/maestro-reference/attack-{trees,chains}/` and 12 under `examples/mermaid-agentic-app/attack-trees/`). That is why every run here was in a scratch clone. No test ran in the main checkout or in the lane worktree.

## 6. Full census and the out-of-gate failures

`python3 -m pytest tests/scripts tests/schemas --timeout=1080` in a fresh clone (local PATH): **1730 passed, 26 failed, 8 errors, 5 skipped** of 1769 collected, in 950.96 s (15 m 50 s). Collection is scoped to those two directories, because `pytest tests/` as a whole also reaches `tests/fixtures/init-baseline-tree/`, whose copy of `test_init_sh_adversarial.py` cannot import `init_sh_helpers`.

The 67 modules split into 36 that a CI gate runs (1060 tests, **0 failures**) and 31 that no gate runs (709 tests, **all 34 failures and errors**). Six of the 34 are #365's (section 5). The other **28** are below: 20 failures and 8 errors, in 8 modules. T001 says "about 19"; the measured count is 28, and it is 19 without the nine `test_human_trust_exploitation.py` cases.

| Module | Cases | Cause (the first assertion) |
|---|---|---|
| `test_human_trust_exploitation.py` | 9: `test_no_agp_te_prose_synthesis` fails; 8 errors in `test_wave5_te_count_is_five`, `…_source_attribution_present`, `…_primary_is_owasp_asi09`, `…_cwe_451_absent_from_source_attribution[CWE-451]`, `…_mitre_atlas_absent_from_source_attribution`, `…_external_regulatory_absent_from_source_attribution`, `…_source_attribution_resolves_against_catalog`, `…_no_trust_exploitation_agentic_pattern` | the regenerated `threats.md` and `threat-report.md` that the F-4 wave-5 cases read are not committed ("Wave 5 must run before this test") |
| `test_mobile_top_10_coverage_bundle_enrichment.py` | 6: `TestLineCountCaps::test_{spoofing,tampering,info_disclosure,privilege_escalation,repudiation}_md_line_cap`; `TestNewPatternCategoriesPresent::test_privilege_escalation_companion_has_M8_priv_gain` | five agent specs are over the 120-line STRIDE cap (135 to 142 lines); one companion file lacks its "Pattern Category 11" header |
| `test_coverage_attestation_in_scope.py` | 3: `TestStream4CoveragePercentage::test_aggregator_matches_expected_fixture[findings_in_scope_only, findings_oos_only, findings_mixed]` | the Stream 4 fixtures expect 30 `mitre-atlas` records and the catalog has 36 |
| `test_tool_abuse_enrichment.py` | 3: `test_tool_abuse_line_count_within_cap`, `test_categories_1_8_byte_identity_against_main`, `test_validate_source_attribution_on_regen` | `tool-abuse.md` is 152 lines against a 150 cap; a byte-identity assertion against `main` fails (without a local `main` ref it fails earlier, on `git show main:…`); the regenerated `threats.md` has no `[NEW]` AG finding |
| `test_coverage_attestation_audit.py` | 2: `TestCitationCompleteness::test_every_covered_owasp_has_agent_citation`, `…_has_pattern_category_citation` | one covered OWASP record is cited by no agent spec, and another by no `detection-patterns.md` category |
| `test_llm10_unbounded_consumption_enrichment.py` | 2: `TestLineCountCaps::test_dos_agent_line_count_within_cap`, `…test_model_theft_agent_line_count_within_cap` | `denial-of-service.md` is 143 lines (cap 120); `model-theft.md` is 162 (cap 150) |
| `test_ml_top_10_coverage_bundle_enrichment.py` | 2: `TestLineCountCaps::test_tampering_md_line_cap`, `…test_model_theft_md_line_cap` | `tampering.md` is 138 lines (cap 120); `model-theft.md` is 162 (cap 150) |
| `test_pyyaml_deferred_import.py` | 1: `test_yaml_import_is_function_scoped[check-citation-urls.py]` | `scripts/check-citation-urls.py:44` imports `yaml` at module level, which breaks KB-037's stdlib-only load invariant |

Other census facts:
- **Skipped (5), all named in section 4:** the TTY case, the two maestro cases and the two byte-identity cases.
- **Against F-391's W0 census** (`46aec8d`, 35 failing: #365's six and 29 others): one fewer. `test_pdf_page_positioning::test_executive_architecture_page_position` listed there passes now, and passed again run alone (2 passed).
- **The run rewrote tracked files.** It left 36 modified PNGs in its clone: 15 under `examples/agentic-app/sample-report/attack-{trees,chains}/`, 9 under `examples/maestro-reference/` and 12 under `examples/mermaid-agentic-app/`. This is #365 mechanism 2 again, and why no test ran in the main checkout.

## 7. Ratchet floor for `tachi_parsers.py` (E3, ADR-050 D16)

**Floor: 44.9%.** `scripts/tachi_parsers.py` has 917 statements and 505 missed, so 412 are covered (44.93%).

Taken at the committed tip, before any parser change, in a fresh clone under Python 3.11.13 (pytest-cov 7.1.0, coverage 7.17.4), with exactly T001's two commands:

```
python3 -m pytest --cov=scripts --cov-report= tests/scripts/test_tachi_parsers.py     # 48 passed in 0.25 s
python3 -m coverage report --include=scripts/tachi_parsers.py --precision=1 --show-missing
Name                       Stmts   Miss  Cover
scripts/tachi_parsers.py     917    505  44.9%
```

Missing lines, for `--show-missing` diffs at T069 and T127:

```
93-96, 106-107, 288, 292-294, 420, 431, 448-449, 464-517, 530-533, 542-564, 575-596, 629-645, 654-678,
700-759, 773-778, 792-805, 813-820, 825-827, 837-851, 897, 1084-1089, 1104-1127, 1140-1174, 1190-1191, 1216,
1237, 1260-1262, 1276-1299, 1306-1307, 1334-1341, 1353-1402, 1452, 1481, 1483-1484, 1487-1505, 1535, 1573,
1614, 1678-1690, 1709, 1711-1712, 1715-1769, 1795-1861, 1866-1877, 1882-1899, 1910-1955, 2006-2043, 2054-2057,
2067-2081, 2091-2094
```

- **Repeatable.** A second clone with the local PATH (Typst and mmdc present) printed identical lines. The module has no `sys.platform`, `sys.version_info`, `os.environ` or `shutil.which` branch, so ubuntu-latest should print the same figure.
- **Rounding.** coverage 7.17.4 rounds the total to the threshold's decimals. With `--fail-under=44.9`, a total of 44.85% or more passes, which tolerates about one extra uncovered statement (412 of 918 is 44.88%; 412 of 919 is 44.83% and fails). That follows ADR-050 D16 as written; it is noted for T022.
- **Scope.** The 48 tests are the whole of `test_tachi_parsers.py`, the file the ratchet measures. The same file runs in `extraction-fidelity` (48 passed in CI).

## 8. Consequence scope (P-10)

What reads or pins the files this bundle changes, taken from the tracked tree at `1c55360`. Each test module is placed in its gate, and shown with its pre-state as passed / failed / skipped. Modules in no gate take the census figure (section 6).

### 8.1 Readers of the four renderer-owned files

The files are `risk-scores.md`, `risk-scores.sarif`, `compensating-controls.md` and `compensating-controls.sarif`.

| Reader | Where | Detail |
|---|---|---|
| `parse_risk_scores_severity` | `scripts/tachi_parsers.py:808` | called at `extract-report-data.py:2859` and `extract-infographic-data.py:319` |
| `parse_risk_scores_findings` | `scripts/tachi_parsers.py:1302` | called at `extract-report-data.py:2836` and `:2860`, `extract-infographic-data.py:310` and `:320` |
| `parse_compensating_controls_md` | `scripts/tachi_parsers.py:1409` | called at `extract-report-data.py:2837` and `extract-infographic-data.py:314` |
| `detect_artifacts` | `scripts/tachi_parsers.py:685` | picks the tier (controls, then scores, then threats); called at `extract-report-data.py:2778` and `extract-infographic-data.py:2155` |
| the two extractors | `scripts/extract-report-data.py`, `scripts/extract-infographic-data.py` | 8 and 25 lines name the files |
| SARIF writer (regeneration tier) | `scripts/generate-risk-scores-sarif.py` | reads `risk-scores.md`; ADR-050 D1 retires it in PR 1 |
| agents, commands, skills, adapters, templates | 36 files: 4 agents, 5 commands, 12 skill files, 7 adapter files, 8 template files | the writers (`risk-scorer.md`, `control-analyzer.md`, their adapter copies) and the readers (`threat-infographic.md`, `report-assembler.md`, the infographic and security-report commands, the Typst templates) |
| test modules | 9 modules reach the files, by name or by a parser call: `test_extract_infographic_data.py`, `test_tachi_parsers.py`, `test_affected_assets_wiring.py`, `test_extraction_sibling_parity.py`, `test_coverage_percentage_computation.py`, `test_extract_report_data.py`, `test_report_posture_contract.py`, `test_coverage_attestation_tiers.py` and `test_extractor_contract_fixes.py`; the helper `install_sh_helpers.py` names them too | `test_write_confinement.py` and `test_pdf_page_positioning.py` read them indirectly, through an extractor run over `fidelity_373/posture_mmdc_free` and `examples/agentic-app/sample-report` |
| fixtures | `tests/scripts/fixtures/golden/` (5 JSONs, built from `exec_arch/agentic_app/`), `report_data/` (the frozen image-flag golden, checked against a report built from `examples/agentic-app/sample-report`; its three image cases hold `threats.md` only), `exec_arch/agentic_app/` (both `.md` files), `fidelity_373/` (12 case directories: 11 with controls, 4 with scores) | read by the extractor suites |
| coverage pins | `test_coverage_percentage_computation.py` (48/0/0), `test_coverage_attestation_tiers.py` (7/0/0), both in no gate | read the files and pin the coverage figures derived from them |
| the six byte-gated PDFs (#365) | `examples/{web-app,microservices,ascii-web-api,mermaid-agentic-app,free-text-microservice,maestro-reference}/security-report.pdf.baseline` | only `maestro-reference` carries the four files; the other five build from `threats.md` alone |

### 8.2 Readers of `attack-chains.md` and of the Phase 3.5 outcome

No record of the Phase 3.5 outcome exists yet (SC-2's baseline: a skip looks like zero), so the "outcome" readers below are the Phase 3.5 text and its consumers. PR 2 adds the record.

| Reader | Where |
|---|---|
| report agent | `.claude/agents/tachi/threat-report.md` (`attack-chains.md` at `:17`, `:38`, `:65`, `:114`, `:152`, `:228`, `:232`, `:263`, `:285`) |
| orchestrator, which writes the file | `.claude/agents/tachi/orchestrator.md` (`attack-chains.md` at `:60`, `:66`, `:484-488`, `:548`, `:580`; Phase 3.5 at `:60`, `:91`, `:391-411`, `:552-580`) |
| `detect_artifacts` and `parse_attack_chains` | `scripts/tachi_parsers.py:736-741` (presence and size), `:1778` |
| `prepare_attack_chains` | `scripts/extract-report-data.py:1192` (reads the file at `:1214`; called at `:2945`) |
| report template | `templates/tachi/security-report/main.typ:108-109` and `:275-277` |
| orchestration references | `.claude/skills/tachi-orchestration/references/output-schemas.md` (`:189`, `:347-353`, `:368`) and `dispatch-rules.md` (`:308`, `:331`, `:372`, `:404`; Phase 3.5 at `:288-410`); `.claude/skills/tachi-shared/references/attack-chain-patterns-shared.md` (`:13`, `:184`, `:190`) and `maestro-agentic-patterns-shared.md:399` |
| command | `.claude/commands/tachi.security-report.md` (`:61`, `:87`, `:132`) |
| tests | `test_attack_chains.py` and `test_attack_chain_extraction.py` (in no gate; PR 2 moves them into `extraction-fidelity`), `test_write_confinement.py` and `test_report_posture_contract.py` (one line each) |
| shipped outputs | `examples/agentic-app/sample-report/attack-chains.md`, `examples/maestro-reference/attack-chains.md` |

### 8.3 Tests that pin the regeneration-tier generators

| Test | Pins | Gate |
|---|---|---|
| `test_affected_assets_wiring.py` | loads both generators at `:536-537`; SC-006 and FR-014 | `tachi-pytest.yml` |
| `test_owasp_2026_contract.py` | loads both generators at `:81-82` | `tachi-pytest.yml` |
| `test_tachi_parsers.py:610` and `:620` | `test_pin_generate_risk_scores_sarif_scored_threat_table_unaffected`, `…_governance_fields_unaffected` (the table headers the generator uses at its `:53` and `:139`) | `extraction-fidelity` |
| `test_sarif_common_affected_assets.py` | `sarif_common.parse_affected_assets`, which both generators share; joins `f374-offline` (Architect re-sign, v1.4) | none today |

### 8.4 Example-tied tests and the `agentic_app` 9.1 exception

Thirteen test modules read `examples/` (a fourteenth, `test_misinformation.py`, names it in a comment). The exception that KB 26 names is a fixture, not an example: `tests/scripts/fixtures/exec_arch/agentic_app/risk-scores.md` carries a typed CVSS base of **9.1** at `:55`, `:56`, `:62`, `:170`, `:196` and `:340`. Five golden JSONs are built from that fixture, and the spec says they depend on its 9.1 (`baseball-card`, `maestro-heatmap`, `maestro-stack`, `risk-funnel` and `system-architecture`, all under `tests/scripts/fixtures/golden/`). `test_extract_infographic_data.py:590-606` (`test_existing_templates_unchanged`, one case per golden) compares each with a fresh extraction of that fixture. Any recompute-from-vector check added in PR 1 must leave that fixture alone.

| Example-tied module | Reads | Gate | Pre-state |
|---|---|---|---|
| `test_extract_report_data.py` | `agentic-app/sample-report` (copied), `microservices/threats.md` | extraction-fidelity | 48/0/6 CI-shaped; 54/0/0 with mmdc |
| `test_extract_infographic_data.py` | `microservices/threats.md` (anchor), the five goldens | extraction-fidelity | 60/0/0 |
| `test_maestro_coverage_invariant.py` | every `examples/**/threats.md` | maestro-coverage | 9/0/2 |
| `test_maestro_cross_surface_consistency.py` | `microservices` | maestro-coverage | 2/0/0 |
| `test_affected_assets_wiring.py` | `agentic-app` and `multi-tenant-rag-app` path strings (URI cases) | tachi-pytest | 39/0/0 |
| `test_asset_sensitivity_tags.py` | the `agentic-app` worked example | tachi-pytest | 26/0/0 |
| `test_backward_compatibility.py` | the six byte-gated examples | none | 6/6/2 (section 5) |
| `test_coverage_percentage_computation.py` | the six baseline examples' `threats.md` | none | 48/0/0 |
| `test_coverage_attestation.py`, `…_pagination.py` | `web-app` | none | 16/0/0 and 5/0/0 |
| `test_pdf_page_positioning.py` | `agentic-app/sample-report` | none | 2/0/0 |
| `test_human_trust_exploitation.py` | `consumer-agent-app`, `maestro-reference` | none | 24/9/0 (section 6) |
| `test_tool_abuse_enrichment.py` | `agentic-app/sample-report/threats.md` | none | 14/3/0 (section 6) |

Pre-state is passed / failed (errors included) / skipped: the CI totals from section 2 for gated modules, and the section 6 census (macOS, Python 3.11.13) for the rest.

### 8.5 Shipped examples

Eleven directories hold 434 tracked files under `examples/`, with 10 PDF baselines (6 byte-gated), 5 tracked PDFs and 48 tracked attack-tree and attack-chain PNGs. They regenerate through the renderer under #364 (NG5), not in this bundle.

| Example | threats | scorer files | controls files | attack-chains | PDF baseline | Byte-gated |
|---|---|---|---|---|---|---|
| `agentic-app` (`sample-report/`) | md, sarif | md, sarif | md, sarif | yes | yes | no |
| `consumer-agent-app` (`sample-report/`) | md, sarif | md, sarif | md, sarif | no | yes | no |
| `maestro-reference` | md, sarif | md, sarif | md, sarif | yes | yes | yes |
| `mobile-banking-app` (`sample-report/`) | md, sarif | md, sarif | md, sarif | no | yes | no |
| `predictive-ml-app` (`sample-report/`) | md, sarif | md, sarif | md, sarif | no | yes | no |
| `mermaid-agentic-app` | md | no | no | no | yes | yes |
| `web-app`, `microservices`, `ascii-web-api`, `free-text-microservice` | md | no | no | no | yes | yes |
| `multi-tenant-rag-app` | none (`architecture.md` only) | no | no | no | no | no |

Five examples carry scorer and controls output: those are the corpus for the oracle gate (plan.md, Verification 7).

## 9. For later tasks

| Task | Use |
|---|---|
| T022, T039, T047 (wiring pushes) | Compare each CI leg with section 2. `tachi-pytest.yml` has 62 `paths:` entries and a 23-module run list; its two legs total 675 tests each (670 + 5 skipped on ubuntu, 674 + 1 on macOS). New f374 modules add to `f374-offline`, not to that list, unless a test needs the two-OS bash matrix |
| T026 (G1), T069, T084, T127 | A regression is a node id that passes here and fails later. The out-of-gate failures in section 6 and #365's six are the only known reds. Take a fresh census at the cut-line commit (T084) before comparing PR 2 |
| T022, T069, T127 (E3) | The floor is 44.9% (section 7). The same figure comes from `test_tachi_parsers.py` alone, so each new parser function's tests must go in that file (H15) |
| Any gated run | Run it in a scratch clone of the committed tip (H1). One run of the byte-identity suite alone leaves 21 modified tracked PNGs, and the full census leaves more (section 6) |
| TW-CI | The two CI legs, the three install-fidelity jobs, the permissions guard and the three co-fired gates were green and stable across two consecutive `main` pushes (`a7f9ec5`, `b040fa1`). A red that matches nothing in sections 2, 5 or 6 is new |

How this record was made, for T084's refresh: a `git clone --branch` of the committed tip per job; a Python 3.11 venv from `uv` with `requirements-dev.txt` and `pytest-timeout`; each command run under `env -i` with an explicit PATH; the same command lines as the workflows (`tachi-pytest.yml`'s run step verbatim, 23 modules, `--timeout=1080`); the CI figures read from the Actions job logs (`gh run view --job <id> --log`).
