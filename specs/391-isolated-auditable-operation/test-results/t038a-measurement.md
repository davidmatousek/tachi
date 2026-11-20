# T038a measurement and the CF-21 verdict (Lane B2)

**Record of:** T036 (`b4888e9`) and T038a (`df37b4b`) on `391-isolated-auditable-operation-part-b`, measured in a scratch clone of the part-b tip `97db2e6` with both changes applied. The pre-state is T003's (`w0-prestate.md`).

| Suite | Before | After |
|---|---|---|
| `test_install_sh_symlink_preflight.py` / `test_install_sh_ref_restore.py` / `test_install_manifest_completeness.py` | 65 / 9 / 10 passed | 65 / 9 / 10 passed, after T036 and again after both tasks |
| Fast set (46 modules, 1102 tests) | 34 failing, all in `wave-01/census-failing.txt` | the same 34; one extra pass, a new `test_pyyaml_deferred_import` case for the generator |
| `test_backward_compatibility.py` | 6 failed, 6 passed, 2 skipped | the same, and all six first-divergence offsets unchanged |
| Slow `init.sh` group | 84 tests | 52 run on committed content: 51 passed, 1 documented xfail. The other 32 were not run locally. The two tasks touch no `{{KEY}}` placeholder and nothing the init-baseline fixture mirrors. CI's `tachi-pytest.yml` run on PR #396 is the gate (the path anchor includes `scripts/install.sh`) |

## CF-21: churn, so the flag stays off

Writing `schema_version` from `schemas/output.yaml` (1.5) into the 44 tracked threats files turns five tests red. Each is `tests/scripts/test_extract_infographic_data.py::test_existing_templates_unchanged`, for baseball-card, maestro-heatmap, maestro-stack, risk-funnel and system-architecture. The five frozen golden JSONs each embed `"schema_version": "1.1"`.

**Verdict:** this is not zero churn. T039 invokes Step 2.6 **without** `--schema-version-from-template`, and `schema_version` stays model-authored and declared-only, which the schema documentation already states.

## Observations for T040 and T045
- The "tracked 1.7/1.8 SARIF twins reproduce unchanged" premise (PM L-5) holds only in part. The `examples/agentic-app/sample-report` SARIF twin carries 1.7, but its input `threats.md` declares 1.4, so a regeneration would now say 1.4. No tracked `.sarif` was edited and no test compares them. This is a candidate for the L-5 follow-up list, next to the consumer-agent-app twin's 1.8.
- `scripts/generate-threats-sarif.py` imports the private `_extract_frontmatter_text` from `tachi_parsers`. The architect decides at T040 whether a public wrapper is wanted.
- T037's synthetic manifests must list `templates/tachi/`, because the marker is written only when the project receives that folder.
