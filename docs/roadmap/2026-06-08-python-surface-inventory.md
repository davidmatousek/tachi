# Python Surface Inventory

**Last Updated**: 2026-06-11
**Status**: RT-010 freeze snapshot
**Scope**: active Python runtime entrypoints, Python packaging, Python test surfaces, and Python-based stack scaffolds that still ship in `tachi-rust`

This inventory freezes the current Python surface so the migration can remove it in a controlled order. The active Python files below are the ones discovered from the current repository tree after excluding fixture and spec artifacts.

## Retirement Map

- `scripts/*.py` runtime entrypoints map to Rust CLI commands under `crates/tachi-cli` and Rust core helpers under `crates/tachi-core`
- `tests/scripts/*.py` and `tests/schemas/*.py` map to Rust unit and integration tests under `crates/*/tests`
- RT-009 roadmap and documentation contract coverage has moved from `tests/test_rt009_docs.py` to `crates/tachi-core/tests/rt009_docs.rs`
- Taxonomy catalog integrity coverage has moved from `tests/schemas/test_taxonomy_integrity.py` to `crates/tachi-core/tests/taxonomy_integrity.rs`
- Project-name parser coverage has moved from `tests/scripts/test_project_name_parser.py` to `crates/tachi-core/tests/parsers.rs`
- The retired `scripts/tachi_parsers.py` runtime hub has been replaced by Rust parser modules in `tachi-core`
- YAML import invariant coverage has moved from `tests/scripts/test_pyyaml_deferred_import.py` to `crates/tachi-core/tests/yaml_imports.rs`
- Infographic command-dispatch coverage has moved from `tests/scripts/test_command_dispatch.py` to `crates/tachi-core/tests/infographic_command_dispatch.rs`
- Executive-architecture infographic payload coverage has moved from `tests/scripts/test_extract_infographic_data.py` and `tests/scripts/test_executive_architecture_payload.py` to `crates/tachi-core/tests/infographic_payload.rs` and `crates/tachi-cli/tests/control_plane_cli.rs`
- Report-data generation/runtime handling has moved from `scripts/extract-report-data.py` to `crates/tachi-cli/src/bin/report-data.rs` and `crates/tachi-core/src/report_data.rs`
- Infographic extraction runtime handling has moved from `scripts/extract-infographic-data.py` to `crates/tachi-cli/src/bin/infographic-data.rs`
- Source-attribution parser coverage has moved from `tests/scripts/test_source_attribution.py` to `crates/tachi-core/tests/parsers.rs`
- Template substitute shim canary coverage has moved from `tests/scripts/test_substitute_shim_canary.py` to `crates/tachi-core/tests/substitute_shim_canary.rs`
- Template substitute no-`eval` lint coverage has moved from `tests/scripts/test_template_substitute_lint_no_eval.py` to `crates/tachi-core/tests/substitute_shim_canary.rs`
- Template substitute literal substitution coverage has moved from `tests/scripts/test_template_substitute_unit.py` to `crates/tachi-core/tests/substitute_shim_canary.rs`
- Template config load unit coverage has moved from `tests/scripts/test_template_config_load_unit.py` to `crates/tachi-shell/tests/template_config_load.rs`
- Init input unit coverage has moved from `tests/scripts/test_init_input_unit.py` to `crates/tachi-core/tests/init_input.rs`
- Template config load integration coverage has moved from `tests/scripts/test_template_config_load_integration.py` to `crates/tachi-shell/tests/template_config_load.rs`
- Defaults-env init coverage has moved from `tests/scripts/test_init_sh_defaults_env.py` to `crates/tachi-shell/tests/init_defaults_env.rs`
- Adversarial init coverage has moved from `tests/scripts/test_init_sh_adversarial.py` to `crates/tachi-shell/tests/init_adversarial.rs`
- Template git clone timeout coverage has moved from `tests/scripts/test_template_git_clone_timeout.py` to `crates/tachi-shell/tests/template_git_clone_timeout.rs`
- Init pre-commit matrix coverage has moved from `tests/scripts/test_init_precommit_matrix.py` to `crates/tachi-shell/tests/init_precommit_matrix.rs`
- The dead init helper package (`tests/scripts/{__init__.py,conftest.py,init_sh_helpers.py}`) has been retired now that the init pre-commit matrix is Rust-native
- The dead root pytest support package (`tests/{conftest.py,__init__.py,schemas/__init__.py}`) has been retired now that the remaining root pytest inventory has been eliminated
- mmdc preflight coverage has moved from `tests/scripts/test_mmdc_preflight.py` to `crates/tachi-core/tests/mmdc_preflight.rs`
- FastAPI Alembic `env.py` scaffold coverage has been retired from both `stacks/fastapi-react/` variants
- FastAPI backend test-package scaffolding (`tests/{__init__,conftest,api/__init__}.py`) has been retired from both `stacks/fastapi-react/` variants
- PDF page-positioning coverage has moved from `tests/scripts/test_pdf_page_positioning.py` to `crates/tachi-core/tests/report_data.rs::build_report_data_typst_renders_executive_architecture_page_between_summary_and_attack_path`
- Backward-compatibility PDF byte-identity coverage has moved from `tests/scripts/test_backward_compatibility.py` to `crates/tachi-core/tests/backward_compatibility.rs::unmodified_examples_byte_identical_pdfs`
- Init substitution E2E coverage has moved from `tests/scripts/test_init_sh_substitution.py` to `crates/tachi-shell/tests/init_substitution.rs`
- Init constitution coverage has moved from `tests/scripts/test_init_sh_constitution.py` to `crates/tachi-shell/tests/init_constitution.rs`
- Finding-pattern parser coverage has moved from `tests/scripts/test_finding_pattern_parser.py` to `crates/tachi-core/tests/parsers.rs`
- Report-data image binding coverage has moved from `tests/scripts/test_extract_report_data.py` to `crates/tachi-core/tests/report_data.rs` and `crates/tachi-cli/tests/control_plane_cli.rs`
- Asset-sensitivity tag parser coverage has moved from `tests/scripts/test_asset_sensitivity_tags.py` to `crates/tachi-core/tests/parsers.rs`
- MAESTRO pattern-classification rules coverage has moved from `tests/scripts/test_pattern_classification_rules.py` to `crates/tachi-core/tests/pattern_classification_rules.rs`
- Pattern synthesis coverage has moved from `tests/scripts/test_pattern_synthesis.py` to `crates/tachi-core/tests/pattern_synthesis.rs`
- Threat SARIF generation has moved from `scripts/generate-threats-sarif.py` to `crates/tachi-cli/src/bin/threats-sarif.rs`
- Risk-score SARIF generation has moved from `scripts/generate-risk-scores-sarif.py` to `crates/tachi-cli/src/bin/risk-scores-sarif.rs`
- Shared SARIF helpers have moved from `scripts/sarif_common.py` to `crates/tachi-core/src/sarif_common.rs`
- `pyproject.toml` and `requirements-dev.txt` map to retirement once the Rust-native tooling path is complete
- `stacks/fastapi-react*` scaffolds map to archive/retirement once Rust/Tauri-only stack guidance is stable

## Active Python Files

```text
stacks/fastapi-react-local/scaffold/backend/app/main.py
~~scripts/extract-report-data.py~~ - migrated to `crates/tachi-cli/src/bin/report-data.rs` and `crates/tachi-core/src/report_data.rs`
~~scripts/tachi_parsers.py~~ - migrated to `crates/tachi-core` parser modules
~~tests/scripts/test_pattern_extraction.py~~ - migrated to `crates/tachi-core/tests/coverage_attestation.rs::build_per_finding_rows_groups_taxonomies_and_preserves_order` and `crates/tachi-cli/tests/control_plane_cli.rs::report_data_binary_emits_coverage_attestation_payload_when_source_attribution_exists`
~~tests/scripts/test_attack_chain_extraction.py~~ - migrated to `crates/tachi-core/tests/attack_chains.rs::parse_attack_chains_extracts_chain_metadata_and_members`, `crates/tachi-core/tests/attack_chains.rs::parse_attack_chains_extracts_findings_and_controls_in_order`, and `crates/tachi-core/tests/attack_chains.rs::generate_chain_mermaid_renders_layers_and_edges`
~~tests/scripts/test_pattern_synthesis.py~~ - migrated to `crates/tachi-core/tests/pattern_synthesis.rs::pattern_synthesis_contract_is_rust_native` and the full Rust-native reference-implementation contract suite
~~tests/scripts/generate_pagination_fixture.py~~ - migrated to `crates/tachi-core/tests/coverage_attestation_pagination.rs::coverage_attestation_pagination_smoke_compiles_at_scale`
~~tests/scripts/test_attack_chains.py~~ - migrated to `crates/tachi-core/tests/attack_chains.rs::generate_chain_mermaid_renders_layers_and_edges` and `crates/tachi-core/tests/attack_chains.rs::parse_attack_chains_extracts_chain_metadata_and_members`
stacks/fastapi-react-local/scaffold/backend/app/api/deps.py
stacks/fastapi-react-local/scaffold/backend/app/api/v1/router.py
~~tests/scripts/test_coverage_percentage_computation.py~~ - migrated to `crates/tachi-core/tests/coverage_percentage_computation.rs::baseline_cross_check_matches_independent_percentage_formula` and `crates/tachi-core/tests/coverage_percentage_computation.rs::mixed_and_oos_fixtures_match_expected_percentage_shape`
~~tests/scripts/test_misinformation.py~~ - migrated to `crates/tachi-core/tests/taxonomy_integrity.rs::misinformation_id_schema_contract_is_rust_native`
~~tests/scripts/test_output_integrity.py~~ - migrated to `crates/tachi-core/tests/taxonomy_integrity.rs::output_integrity_schema_contract_is_rust_native`
~~tests/scripts/test_mmdc_preflight.py~~ - migrated to `crates/tachi-core/tests/mmdc_preflight.rs::preflight_errors_when_renderer_is_missing_for_attack_trees` and `crates/tachi-core/tests/mmdc_preflight.rs::render_failure_summary_includes_all_failure_records`
~~tests/scripts/test_coverage_attestation.py~~ - migrated to `crates/tachi-core/tests/report_data.rs::build_report_data_typst_emits_coverage_attestation_payload_when_source_attribution_exists`, `crates/tachi-core/tests/report_data.rs::build_report_data_typst_marks_empty_source_attribution_reports_as_false`, and `crates/tachi-core/tests/report_data.rs::build_report_data_typst_keeps_typst_compilable_when_report_data_lacks_new_bindings`
~~tests/scripts/test_f_a3_populator_wiring.py~~ - migrated to `crates/tachi-core/tests/f_a3_populator_wiring.rs::f_a3_populator_wiring_contract_is_rust_native`
~~tests/scripts/test_coverage_attestation_audit.py~~ - migrated to `crates/tachi-core/tests/coverage_attestation_audit.rs::coverage_attestation_audit_contract_is_rust_native`
~~tests/scripts/test_human_trust_exploitation.py~~ - migrated to `crates/tachi-core/tests/human_trust_exploitation.rs::human_trust_exploitation_contract_is_rust_native`, `crates/tachi-core/tests/human_trust_exploitation.rs::te_schema_prefix_and_fixture_attribution_are_rust_native`, and `crates/tachi-core/tests/human_trust_exploitation.rs::invalid_te_fixture_keeps_trust_exploitation_disambiguation_but_fails_validation`
~~tests/scripts/test_coverage_attestation_pagination.py~~ - migrated to `crates/tachi-core/tests/coverage_attestation_pagination.rs::coverage_attestation_pagination_smoke_compiles_at_scale`
~~tests/scripts/test_coverage_attestation_tiers.py~~ - migrated to `crates/tachi-core/tests/coverage_attestation_tiers.rs::coverage_attestation_tiers_contract_is_rust_native`, `crates/tachi-core/tests/coverage_attestation_tiers.rs::merge_attaches_attribution_on_matching_tier_1_findings`, and `crates/tachi-core/tests/coverage_attestation_tiers.rs::merge_attaches_attribution_on_matching_tier_2_findings`
~~tests/scripts/test_ml_top_10_coverage_bundle_enrichment.py~~ - migrated to `crates/tachi-core/tests/ml_top_10_coverage_bundle_enrichment.rs::ml_top_10_coverage_bundle_contract_is_rust_native` and the Rust-native ML bundle contract suite
~~tests/scripts/test_llm10_unbounded_consumption_enrichment.py~~ - migrated to `crates/tachi-core/tests/llm10_unbounded_consumption_enrichment.rs::llm10_unbounded_consumption_contract_is_rust_native` and the Rust-native LLM10 contract suite
~~tests/scripts/test_pdf_page_positioning.py~~ - migrated to `crates/tachi-core/tests/report_data.rs::build_report_data_typst_renders_executive_architecture_page_between_summary_and_attack_path`
~~tests/scripts/test_init_sh_constitution.py~~ - migrated to `crates/tachi-shell/tests/init_constitution.rs::init_constitution_contract_is_rust_native` and `crates/tachi-shell/tests/init_constitution.rs::constitution_byte_equals_clean_template`
~~tests/scripts/test_init_sh_substitution.py~~ - migrated to `crates/tachi-shell/tests/init_substitution.rs::init_substitution_contract_is_rust_native` and the Rust-native byte/mode comparison suite
~~tests/scripts/test_init_sh_self_delete.py~~ - migrated to `crates/tachi-shell/tests/control_plane.rs::init_output_preserves_state_files_when_script_self_deletes`
~~tests/scripts/test_extractor_contract_fixes.py~~ - migrated to `crates/tachi-core/tests/extractor_contract_fixes.rs::extractor_contract_fixes_contract_is_rust_native`, `crates/tachi-core/tests/extractor_contract_fixes.rs::parse_attack_trees_accepts_agent_emitted_slugged_filenames`, `crates/tachi-core/tests/extractor_contract_fixes.rs::parse_threat_report_md_falls_back_to_full_section1_prose`, `crates/tachi-core/tests/extractor_contract_fixes.rs::detect_images_accepts_matching_png_and_jpeg_bytes`, `crates/tachi-core/tests/extractor_contract_fixes.rs::parse_compensating_controls_dedupes_cross_listed_findings`, and `crates/tachi-core/tests/extractor_contract_fixes.rs::merge_delta_status_populates_tier1_findings`
~~tests/scripts/test_init_input_unit.py~~ - migrated to `crates/tachi-core/tests/init_input.rs::init_input_unit_contract_is_rust_native`
~~tests/scripts/test_extract_infographic_data.py~~ - migrated to `crates/tachi-core/tests/infographic_payload.rs::build_infographic_payload_executive_architecture_includes_layers_callouts_and_overlay` and `crates/tachi-cli/tests/control_plane_cli.rs::infographic_data_binary_returns_executive_architecture_payload`
~~tests/scripts/test_template_substitute_unit.py~~ - migrated to `crates/tachi-core/tests/substitute_shim_canary.rs::template_substitute_literal_project_names_are_rust_native`
~~tests/scripts/test_init_sh_defaults_env.py~~ - migrated to `crates/tachi-shell/tests/init_defaults_env.rs::init_defaults_env_contract_is_rust_native`
~~tests/scripts/test_init_precommit_matrix.py~~ - migrated to `crates/tachi-shell/tests/init_precommit_matrix.rs::init_precommit_matrix_is_rust_native` and `crates/tachi-shell/tests/init_precommit_matrix.rs::non_tty_no_flag_skips_prompt_and_install`
~~tests/scripts/test_backward_compatibility.py~~ - migrated to `crates/tachi-core/tests/backward_compatibility.rs::backward_compatibility_contract_is_rust_native` and `crates/tachi-core/tests/backward_compatibility.rs::unmodified_examples_byte_identical_pdfs`
stacks/fastapi-react-local/scaffold/backend/app/db/base.py
stacks/fastapi-react-local/scaffold/backend/app/db/session.py
stacks/fastapi-react-local/scaffold/backend/app/core/middleware.py
stacks/fastapi-react-local/scaffold/backend/app/core/exceptions.py
stacks/fastapi-react-local/scaffold/backend/app/config.py
~~tests/scripts/test_tool_abuse_enrichment.py~~ - migrated to `crates/tachi-core/tests/tool_abuse_enrichment.rs`
~~tests/scripts/test_executive_architecture_payload.py~~ - migrated to `crates/tachi-core/tests/infographic_payload.rs::build_infographic_payload_executive_architecture_requires_scope_data` and `crates/tachi-cli/tests/control_plane_cli.rs::infographic_data_binary_returns_executive_architecture_payload`
~~tests/scripts/test_template_config_load_unit.py~~ - migrated to `crates/tachi-shell/tests/template_config_load.rs::template_config_load_unit_contract_is_rust_native`
~~tests/scripts/test_extract_report_data.py~~ - migrated to `crates/tachi-core/tests/report_data.rs::build_report_data_typst_matches_retired_image_binding_pytest_contract` and `crates/tachi-cli/tests/control_plane_cli.rs`
~~tests/scripts/test_asset_sensitivity_tags.py~~ - migrated to `crates/tachi-core/tests/parsers.rs::parse_component_asset_map_matches_retired_pytest_contract`
~~tests/scripts/test_template_config_load_integration.py~~ - migrated to `crates/tachi-shell/tests/template_config_load.rs::template_config_load_integration_contract_is_rust_native`
~~tests/scripts/test_coverage_attestation_in_scope.py~~ - migrated to `crates/tachi-core/tests/coverage_attestation_in_scope.rs::load_framework_yaml_records_from_dir_filters_oos_and_treats_missing_field_as_in_scope` and `crates/tachi-core/tests/coverage_attestation_in_scope.rs::build_per_framework_aggregates_in_dir_uses_in_scope_denominator`
~~tests/scripts/test_smoke.py~~ - migrated to `crates/tachi-core/tests/infographic_scaffold.rs::extract_prompt_scaffold_reads_template_prompt_segments`
~~tests/scripts/test_mobile_top_10_coverage_bundle_enrichment.py~~ - migrated to `crates/tachi-core/tests/mobile_top_10_coverage_bundle_enrichment.rs::mobile_top_10_coverage_bundle_contract_is_rust_native`
stacks/fastapi-react/scaffold/backend/app/config.py
stacks/fastapi-react/scaffold/backend/app/main.py
stacks/fastapi-react/scaffold/backend/app/db/base.py
stacks/fastapi-react/scaffold/backend/app/db/session.py
stacks/fastapi-react/scaffold/backend/app/core/middleware.py
stacks/fastapi-react/scaffold/backend/app/core/exceptions.py
stacks/fastapi-react/scaffold/backend/app/api/deps.py
stacks/fastapi-react/scaffold/backend/app/api/v1/router.py
.claude/skills/~aod-build/scripts/generate_checkpoint.py
.claude/skills/~aod-build/scripts/analyze_tasks.py
.claude/skills/~aod-build/scripts/update_index.py
```

## Notes

- The inventory intentionally excludes fixture copies under `tests/fixtures/` and spec artifacts under `specs/`.
- RT-011 has started retiring pytest-centric coverage by moving the RT-009 documentation contract, taxonomy integrity checks, project-name parser contract, YAML import invariant, infographic command-dispatch contract, executive-architecture infographic payload contract, source-attribution parser contract, template substitute shim canary, template substitute no-`eval` lint, template substitute literal substitution contract, finding-pattern parser contract, misinformation schema contract, output-integrity schema contract, init self-delete contract, F-A3 populator wiring contract, report-data image binding contract, asset-sensitivity tag contract, adversarial init contract, template git clone timeout contract, MAESTRO pattern-classification rules contract, ML Top 10 coverage bundle enrichment contract, LLM10 unbounded consumption contract, and report-data runtime entrypoint contract to Rust-native tests.
- RT-014 will remove the packaging and scaffold surfaces once parity is stable.
