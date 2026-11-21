# Economy Gate (`/aod.build` Step 8): Feature 391, Part A

**Date**: 2026-11-21 (S2c)
**Scope**: `git diff main...391-isolated-auditable-operation` at `617ee92` (PR #392). The 10 changed code files:
- `scripts/check-agent-privileges.py`, `scripts/extract-report-data.py`, `scripts/extract-infographic-data.py`, `scripts/populate-affected-assets.py`;
- `templates/tachi/security-report/report-config.typ`;
- `tests/scripts/test_agent_privilege_guard.py`, `test_write_confinement.py`, `test_isolated_profile_contract.py`, `test_install_manifest_completeness.py` and `test_coverage_attestation.py`.

**Reviewer**: code-reviewer, judgment-based and advisory, against `.claude/rules/code-economy.md`. Probes ran in a scratch clone; nothing ran in the main tree.
**Verdict**: **FINDINGS, 5 advisories** (4 economy, 1 carve-out). None blocks the merge.

## Findings

| ID | File | Lower rung that applied | Suggested reduction |
|---|---|---|---|
| EC-1 | `tests/scripts/test_install_manifest_completeness.py` (SC-A4 helpers and their negative test) | Rung 2, existing code: the guard's `run_checks` already does the C1 and C2 comparison | Call `run_checks` on the installed tree and assert no C1 or C2 finding, keeping one red case (about 190 lines to about 25) |
| EC-2 | Same file (the `_install_via_*` helpers) | Rung 2, existing code: the module's three install tests already perform these installs | Have the existing tests call the helpers, so there is one copy of each install body (about 45 lines; 3 to 4 fewer installs per CI run in the fuller form) |
| EC-3 | `tests/scripts/test_isolated_profile_contract.py` (a port of GitHub's anchor rule) | Rungs 1 and 6: the §8 heading and its fragment are fixed constants | Pin the heading line and the link fragment instead of porting the slug algorithm (about 85 lines to about 10) |
| EC-4 | `tests/scripts/test_agent_privilege_guard.py` and `test_install_manifest_completeness.py` (two more importlib loaders) | Rung 2, existing helper: `tests/conftest.py`'s `_load_hyphenated_script` | One shared session fixture in `tests/conftest.py` (about 32 lines to about 8) |
| EC-5 | `scripts/extract-report-data.py`: `_resolve_cli_mode`, and two `_guard_build_dir` rules ("contains the target directory", "exists and is not a directory") | **Carve-out §1, one runnable check** | One parametrized case beside the build-dir refusal tests in `test_write_confinement.py`: argv, exit 2, a message fragment, an unchanged snapshot (about +12 lines). The reviewer's scratch-clone probes found each refusal branch exits 2 with its reason and writes nothing; no test yet keeps it so |

**Carve-out survival.** No simplification shortened a safety carve-out:
- The build-dir path guard, the `TACHI_MMDC_PUPPETEER_CONFIG` check and the guard's strict input parsers keep every validation rule.
- Error paths fail loudly with exit 2.
- Deletion goes only through the guarded `--remove-build-dir`.

EC-5 is a missing runnable check, not a weakened control. Declining the lenient repository parsers in favour of the guard's strict ones is the right rung, because reusing them would shorten the input-validation carve-out.

Full review (local): `.aod/results/code-reviewer-economy-391.md`.

## Decision

The maintainer chose on 2026-11-21: fix EC-5 now, and file EC-1 to EC-4.

- **EC-5: fixed in `97208fe`.** One parametrized test adds 9 refusal cases, each pinned by a mutation check. `test_write_confinement.py` gives 78 passed in a scratch clone of `97208fe`, with `TACHI_REQUIRE_TYPST=1`.
- **EC-1 to EC-4: acknowledged and filed as #417.**
