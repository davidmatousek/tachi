# Python Surface Inventory

**Last Updated**: 2026-06-10
**Status**: RT-010 freeze snapshot
**Scope**: active Python runtime entrypoints, Python packaging, Python test surfaces, and Python-based stack scaffolds that still ship in `tachi-rust`

This inventory freezes the current Python surface so the migration can remove it in a controlled order. The active Python files below are the ones discovered from the current repository tree after excluding fixture and spec artifacts.

## Retirement Map

- `scripts/*.py` runtime entrypoints map to Rust CLI commands under `crates/tachi-cli` and Rust core helpers under `crates/tachi-core`
- `tests/scripts/*.py` and `tests/schemas/*.py` map to Rust unit and integration tests under `crates/*/tests`
- RT-009 roadmap and documentation contract coverage has moved from `tests/test_rt009_docs.py` to `crates/tachi-core/tests/rt009_docs.rs`
- Taxonomy catalog integrity coverage has moved from `tests/schemas/test_taxonomy_integrity.py` to `crates/tachi-core/tests/taxonomy_integrity.rs`
- Project-name parser coverage has moved from `tests/scripts/test_project_name_parser.py` to `crates/tachi-core/tests/parsers.rs`
- YAML import invariant coverage has moved from `tests/scripts/test_pyyaml_deferred_import.py` to `crates/tachi-core/tests/yaml_imports.rs`
- Infographic command-dispatch coverage has moved from `tests/scripts/test_command_dispatch.py` to `crates/tachi-core/tests/infographic_command_dispatch.rs`
- Source-attribution parser coverage has moved from `tests/scripts/test_source_attribution.py` to `crates/tachi-core/tests/parsers.rs`
- Template substitute shim canary coverage has moved from `tests/scripts/test_substitute_shim_canary.py` to `crates/tachi-core/tests/substitute_shim_canary.rs`
- Template substitute no-`eval` lint coverage has moved from `tests/scripts/test_template_substitute_lint_no_eval.py` to `crates/tachi-core/tests/substitute_shim_canary.rs`
- Template substitute literal substitution coverage has moved from `tests/scripts/test_template_substitute_unit.py` to `crates/tachi-core/tests/substitute_shim_canary.rs`
- Template config load unit coverage has moved from `tests/scripts/test_template_config_load_unit.py` to `crates/tachi-shell/tests/template_config_load.rs`
- Init input unit coverage has moved from `tests/scripts/test_init_input_unit.py` to `crates/tachi-core/tests/init_input.rs`
- Template config load integration coverage has moved from `tests/scripts/test_template_config_load_integration.py` to `crates/tachi-shell/tests/template_config_load.rs`
- Defaults-env init coverage has moved from `tests/scripts/test_init_sh_defaults_env.py` to `crates/tachi-shell/tests/init_defaults_env.rs`
- Finding-pattern parser coverage has moved from `tests/scripts/test_finding_pattern_parser.py` to `crates/tachi-core/tests/parsers.rs`
- Report-data image binding coverage has moved from `tests/scripts/test_extract_report_data.py` to `crates/tachi-core/tests/report_data.rs` and `crates/tachi-cli/tests/control_plane_cli.rs`
- Asset-sensitivity tag parser coverage has moved from `tests/scripts/test_asset_sensitivity_tags.py` to `crates/tachi-core/tests/parsers.rs`
- `pyproject.toml` and `requirements-dev.txt` map to retirement once the Rust-native tooling path is complete
- `stacks/fastapi-react*` scaffolds map to archive/retirement once Rust/Tauri-only stack guidance is stable

## Active Python Files

```text
scripts/generate-threats-sarif.py
scripts/generate-risk-scores-sarif.py
scripts/tachi_parsers.py
scripts/sarif_common.py
scripts/extract-infographic-data.py
scripts/extract-report-data.py
stacks/fastapi-react-local/scaffold/backend/alembic/env.py
stacks/fastapi-react-local/scaffold/backend/tests/api/__init__.py
stacks/fastapi-react-local/scaffold/backend/tests/__init__.py
stacks/fastapi-react-local/scaffold/backend/tests/conftest.py
stacks/fastapi-react-local/scaffold/backend/app/services/__init__.py
stacks/fastapi-react-local/scaffold/backend/app/main.py
tests/scripts/test_pattern_extraction.py
tests/scripts/test_attack_chain_extraction.py
tests/scripts/init_sh_helpers.py
tests/scripts/test_pattern_synthesis.py
tests/scripts/generate_pagination_fixture.py
tests/scripts/test_attack_chains.py
stacks/fastapi-react-local/scaffold/backend/app/api/__init__.py
stacks/fastapi-react-local/scaffold/backend/app/api/deps.py
stacks/fastapi-react-local/scaffold/backend/app/api/v1/router.py
stacks/fastapi-react-local/scaffold/backend/app/api/v1/__init__.py
tests/scripts/test_coverage_percentage_computation.py
tests/scripts/test_init_precommit_matrix.py
tests/scripts/__init__.py
~~tests/scripts/test_misinformation.py~~ - migrated to `crates/tachi-core/tests/taxonomy_integrity.rs::misinformation_id_schema_contract_is_rust_native`
~~tests/scripts/test_output_integrity.py~~ - migrated to `crates/tachi-core/tests/taxonomy_integrity.rs::output_integrity_schema_contract_is_rust_native`
tests/scripts/test_mmdc_preflight.py
tests/scripts/test_coverage_attestation.py
~~tests/scripts/test_f_a3_populator_wiring.py~~ - migrated to `crates/tachi-core/tests/f_a3_populator_wiring.rs::f_a3_populator_wiring_contract_is_rust_native`
tests/scripts/test_coverage_attestation_audit.py
tests/scripts/test_human_trust_exploitation.py
tests/scripts/test_coverage_attestation_pagination.py
tests/scripts/test_pdf_page_positioning.py
tests/scripts/test_init_sh_adversarial.py
tests/scripts/test_init_sh_substitution.py
~~tests/scripts/test_init_sh_self_delete.py~~ - migrated to `crates/tachi-shell/tests/control_plane.rs::init_output_preserves_state_files_when_script_self_deletes`
tests/scripts/test_extractor_contract_fixes.py
~~tests/scripts/test_init_input_unit.py~~ - migrated to `crates/tachi-core/tests/init_input.rs::init_input_unit_contract_is_rust_native`
tests/scripts/test_pattern_classification_rules.py
tests/scripts/conftest.py
tests/scripts/test_extract_infographic_data.py
tests/scripts/test_init_sh_constitution.py
~~tests/scripts/test_template_substitute_unit.py~~ - migrated to `crates/tachi-core/tests/substitute_shim_canary.rs::template_substitute_literal_project_names_are_rust_native`
~~tests/scripts/test_init_sh_defaults_env.py~~ - migrated to `crates/tachi-shell/tests/init_defaults_env.rs::init_defaults_env_contract_is_rust_native`
tests/scripts/test_backward_compatibility.py
stacks/fastapi-react-local/scaffold/backend/app/db/base.py
stacks/fastapi-react-local/scaffold/backend/app/db/__init__.py
stacks/fastapi-react-local/scaffold/backend/app/db/session.py
tests/conftest.py
tests/__init__.py
tests/schemas/__init__.py
stacks/fastapi-react-local/scaffold/backend/app/schemas/__init__.py
stacks/fastapi-react-local/scaffold/backend/app/models/__init__.py
stacks/fastapi-react-local/scaffold/backend/app/__init__.py
stacks/fastapi-react-local/scaffold/backend/app/core/middleware.py
stacks/fastapi-react-local/scaffold/backend/app/core/exceptions.py
stacks/fastapi-react-local/scaffold/backend/app/core/__init__.py
stacks/fastapi-react-local/scaffold/backend/app/config.py
stacks/fastapi-react/scaffold/backend/alembic/env.py
tests/scripts/test_tool_abuse_enrichment.py
tests/scripts/test_executive_architecture_payload.py
tests/scripts/test_template_git_clone_timeout.py
~~tests/scripts/test_template_config_load_unit.py~~ - migrated to `crates/tachi-shell/tests/template_config_load.rs::template_config_load_unit_contract_is_rust_native`
tests/scripts/test_ml_top_10_coverage_bundle_enrichment.py
tests/scripts/test_coverage_attestation_tiers.py
~~tests/scripts/test_extract_report_data.py~~ - migrated to `crates/tachi-core/tests/report_data.rs::build_report_data_typst_matches_retired_image_binding_pytest_contract` and `crates/tachi-cli/tests/control_plane_cli.rs`
tests/scripts/test_llm10_unbounded_consumption_enrichment.py
~~tests/scripts/test_asset_sensitivity_tags.py~~ - migrated to `crates/tachi-core/tests/parsers.rs::parse_component_asset_map_matches_retired_pytest_contract`
~~tests/scripts/test_template_config_load_integration.py~~ - migrated to `crates/tachi-shell/tests/template_config_load.rs::template_config_load_integration_contract_is_rust_native`
tests/scripts/test_coverage_attestation_in_scope.py
tests/scripts/test_smoke.py
tests/scripts/test_mobile_top_10_coverage_bundle_enrichment.py
stacks/fastapi-react/scaffold/backend/tests/api/__init__.py
stacks/fastapi-react/scaffold/backend/tests/__init__.py
stacks/fastapi-react/scaffold/backend/tests/conftest.py
stacks/fastapi-react/scaffold/backend/app/config.py
stacks/fastapi-react/scaffold/backend/app/__init__.py
stacks/fastapi-react/scaffold/backend/app/services/__init__.py
stacks/fastapi-react/scaffold/backend/app/main.py
stacks/fastapi-react/scaffold/backend/app/models/__init__.py
stacks/fastapi-react/scaffold/backend/app/db/base.py
stacks/fastapi-react/scaffold/backend/app/db/__init__.py
stacks/fastapi-react/scaffold/backend/app/db/session.py
stacks/fastapi-react/scaffold/backend/app/core/middleware.py
stacks/fastapi-react/scaffold/backend/app/core/exceptions.py
stacks/fastapi-react/scaffold/backend/app/core/__init__.py
stacks/fastapi-react/scaffold/backend/app/schemas/__init__.py
stacks/fastapi-react/scaffold/backend/app/api/__init__.py
stacks/fastapi-react/scaffold/backend/app/api/deps.py
stacks/fastapi-react/scaffold/backend/app/api/v1/router.py
stacks/fastapi-react/scaffold/backend/app/api/v1/__init__.py
.claude/skills/~aod-build/scripts/generate_checkpoint.py
.claude/skills/~aod-build/scripts/analyze_tasks.py
.claude/skills/~aod-build/scripts/update_index.py
```

## Notes

- The inventory intentionally excludes fixture copies under `tests/fixtures/` and spec artifacts under `specs/`.
- RT-011 has started retiring pytest-centric coverage by moving the RT-009 documentation contract, taxonomy integrity checks, project-name parser contract, YAML import invariant, infographic command-dispatch contract, source-attribution parser contract, template substitute shim canary, template substitute no-`eval` lint, template substitute literal substitution contract, finding-pattern parser contract, misinformation schema contract, output-integrity schema contract, init self-delete contract, F-A3 populator wiring contract, report-data image binding contract, and asset-sensitivity tag parser contract to Rust-native tests.
- RT-014 will remove the packaging and scaffold surfaces once parity is stable.
