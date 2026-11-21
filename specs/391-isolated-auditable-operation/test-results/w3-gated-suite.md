# W3 gated-suite run (T043)

**Result: PASS.** Both committed tips pass every gated set.
- 0 regressions and 0 new failures.
- The only failures are #365's six byte-identity cases, on both tips. Their first-divergence offsets are the same as at T003.
- X-5 passes: 702 tests under Python 3.9.6 with Typst required, against the architect's baseline of 667.
- The zsh manual-loop cases passed on both tips. None was skipped.
- Part-b holds no archiver module, schema, test or fixture.
- Totals on Python 3.12.11 over the gated sets (the run list, the three install-fidelity jobs, `test_coverage_attestation.py` and the byte-identity suite): Part A 984 passed, 6 failed, 3 skipped, 1 xfailed; part-b 1113 passed, 6 failed, 3 skipped, 1 xfailed. The failures are #365's six on each tip.

| Item | Value |
|---|---|
| Date | 2026-11-20, local evening (capture 02:30 to 02:47 UTC on 2026-11-21) |
| Part A tip | `b71a0d75d7ad008b9ad408ff2151395d0593fd87`, branch `391-isolated-auditable-operation` |
| part-b tip | `f34e0ed0ee2b0ac570b042e0ef1f4ffa9375de19`, branch `391-isolated-auditable-operation-part-b`: the BX''' merge after the TW-B1 stop, so part-b carries B2 only |
| Scratch clones | Eight fresh clones, `git clone --no-hardlinks` of the local repo and then `git checkout <tip>`; `git log -1` was checked before any result was read (every run log opens with the head and its full SHA).<br>• `$SCRATCH/w3t043-{A,B}-gated`: the `tachi-pytest.yml` run list.<br>• `$SCRATCH/w3t043-{A,B}-fid`: the three install-fidelity jobs and `test_coverage_attestation.py`.<br>• `$SCRATCH/w3t043-{A,B}-byte`: the byte-identity suite, each a fresh tree that nothing else had touched.<br>• `$SCRATCH/w3t043-{A,B}-py39`: the guard self-tests, the permissions steps, X-5, the py39-floor list and the extra 3.9.6 runs.<br>Four more clones, at `46aec8d`, `8273669`, `7e64fd7` and `2c5fe08`, were used only for `--collect-only`, to compare test ids and counts with the earlier records.<br>`$SCRATCH` is the test session's scratchpad, outside every work tree. Its absolute path is left out because it contains a home-directory path |
| Python | **3.12.11** (pytest 9.1.0, pytest-timeout 2.4.0, PyYAML 6.0.3) for the gated sets. CI runs 3.11, so 3.12.11 stands in for it.<br>**3.9.6** (`/usr/bin/python3`, pytest 8.4.2, pytest-timeout 2.4.0, PyYAML 6.0.2) for X-5, the py39-floor list and the extra manifest-completeness run. CI's py39-floor job runs 3.9 on ubuntu-24.04 |
| Other tools | typst 0.14.2, mmdc 11.12.0 (the image-flag cases ran instead of skipping), zsh 5.9, jq 1.7.1, `/bin/bash` 3.2.57, macOS arm64 |
| Command shape | From the clone root, `PYTHONDONTWRITEBYTECODE=1 <python> -m pytest <modules> -q -p no:cacheprovider [--timeout=N] --junitxml=<file outside the clone>`. `pyproject.toml` adds `-ra --strict-markers`. Each module list was read from that clone's own workflow file, so the run list is the one at that tip: 21 modules on Part A and 23 on part-b. Counts come from the junit files and match each pytest summary line |
| Main tree | No pytest and no extractor ran in it (the #365 rule). The main tree's `git status --short` is under "Main-tree check" below |

The "earlier record" column quotes T003 (`w0-prestate.md`, `46aec8d`), wave-02 (G1: `8273669` and `7e64fd7`) or the X-5 baseline in `p0-architect-checkpoint.md`.

## Part A: `b71a0d7`

| Set | Python | Passed | Failed | Skipped | xfailed | Earlier record |
|---|---|---|---|---|---|---|
| `tachi-pytest.yml` run list, 21 modules, `--timeout=1080` | 3.12.11 | 615 | 0 | 1 | 1 | W2: 592 passed, 1 skipped, 1 xfailed, same 21 modules |
| install-fidelity `manifest-completeness` | 3.12.11 | 17 | 0 | 0 | 0 | W2: 17 passed |
| install-fidelity `extraction-fidelity`, 7 modules | 3.12.11 | 255 | 0 | 0 | 0 | W2: 255 passed |
| install-fidelity `report-posture` + `test_write_confinement.py`, `TACHI_REQUIRE_TYPST=1` | 3.12.11 | 75 | 0 | 0 | 0 | W2: 63 passed (X-1 added 12) |
| `test_coverage_attestation.py`, run explicitly (not gated; T012 edits it) | 3.12.11 | 16 | 0 | 0 | 0 | T003 and W2: 16 passed |
| `test_backward_compatibility.py` (byte-identity), fresh clone | 3.12.11 | 6 | 6 | 2 | 0 | T003 and W2: 6 failed, 6 passed, 2 skipped |
| `check-agent-privileges.py --self-test` | 3.12.11 | exit 0 | | | | S2a: exit 0 |
| `check-agent-privileges.py --self-test` | 3.9.6 | exit 0 | | | | S2a: exit 0 |
| **X-5**: 12 installed-script modules, `TACHI_REQUIRE_TYPST=1` | 3.9.6 | 702 | 0 | 0 | 0 | Checkpoint: 667 passed |
| `manifest-completeness`, for the zsh cases under 3.9 (extra) | 3.9.6 | 16 | 0 | 1 | 0 | none (new run) |
| Permissions workflow run steps, incl. the guard with `--self-test` (extra) | 3.12.11 | exit 0 | | | | W2: exit 0 |

- The matrix run took 14 min 37 s. W2 collected 594 ids for the same 21 modules and this run collects 617: 8 more in `test_agent_privilege_guard.py` (X-2) and 15 more in `test_isolated_profile_contract.py` (the AR-21 and AR-21a controls). All 617 ran: 615 passed, 1 skipped, 1 xfailed.
- The skip is `test_init_precommit_matrix.py::test_tty_no_flag_default_y` (it needs a real TTY) and the xfail is `test_init_sh_substitution.py::test_personalized_tree_bytes_match_baseline` (stale baseline fixture since v4.44.0). Both are at the T003 pre-state.
- Under 3.9.6, `manifest-completeness` skips one case, `test_distributable_imports_stdlib_only`, which needs Python 3.10 or later (`sys.stdlib_module_names`) and is in the file at the T003 pre-state. It is not a zsh case.

## part-b: `f34e0ed`

| Set | Python | Passed | Failed | Skipped | xfailed | Earlier record |
|---|---|---|---|---|---|---|
| `tachi-pytest.yml` run list, 23 modules, `--timeout=1080` | 3.12.11 | 744 | 0 | 1 | 1 | W2: 1203 passed, 1 skipped, 1 xfailed, 22 modules incl. the archiver |
| `py39-floor` job list, 2 modules, `--timeout=600` | 3.9.6 | 128 | 0 | 1 | 0 | W2: 942 passed, 2 skipped, 3 modules incl. the archiver |
| install-fidelity `manifest-completeness` | 3.12.11 | 17 | 0 | 0 | 0 | W2: 10 passed (before the Part A merge) |
| install-fidelity `extraction-fidelity`, 7 modules | 3.12.11 | 255 | 0 | 0 | 0 | W2: 255 passed |
| install-fidelity `report-posture` + `test_write_confinement.py`, `TACHI_REQUIRE_TYPST=1` | 3.12.11 | 75 | 0 | 0 | 0 | W2: 6 passed (`test_report_posture_contract.py` alone) |
| `test_coverage_attestation.py`, run explicitly (not gated; T012 edits it) | 3.12.11 | 16 | 0 | 0 | 0 | T003 and W2: 16 passed |
| `test_backward_compatibility.py` (byte-identity), fresh clone | 3.12.11 | 6 | 6 | 2 | 0 | T003 and W2: 6 failed, 6 passed, 2 skipped |
| `check-agent-privileges.py --self-test` | 3.12.11 | exit 0 | | | | S2a: exit 0 |
| `check-agent-privileges.py --self-test` | 3.9.6 | exit 0 | | | | S2a: exit 0 |
| X-5's 12 modules on part-b as well, `TACHI_REQUIRE_TYPST=1` (extra) | 3.9.6 | 702 | 0 | 0 | 0 | Part A, above: 702 passed |
| `manifest-completeness`, for the zsh cases under 3.9 (extra) | 3.9.6 | 16 | 0 | 1 | 0 | none (new run) |
| Permissions workflow run steps, incl. the guard with `--self-test` (extra) | 3.12.11 | exit 0 | | | | W2: exit 0 |

- The matrix run took 14 min 53 s. Against W2 (1203 passed with the archiver's 828 cases) the archiver module is gone and `test_agent_privilege_guard.py` (154) and `test_isolated_profile_contract.py` (202) joined through the Part A merge; `test_tachi_version_marker.py` and `test_threats_schema_contract.py` gained 13 ids between W2 and W3. 1203 - 828 + 154 + 202 + 13 = 744.
- The py39-floor skip is `test_threats_schema_contract.py::test_the_stamp_script_imports_only_the_standard_library`, a 3.10+ guard in the module itself. It runs under 3.12.11, which is why the 3.12.11 matrix has no skip there.
- The matrix skip and xfail are the same two as on Part A.

## Byte-identity against the T003 pre-state

`tests/scripts/test_backward_compatibility.py` ran once per tip, each in a fresh clone that nothing else had touched, on 3.12.11. The T003 pre-state is **6 failed, 6 passed, 2 skipped**.

| Tip | Failed | Passed | Skipped | New failures |
|---|---|---|---|---|
| T003, `46aec8d` | 6 | 6 | 2 | none |
| Part A, `b71a0d7` | 6 | 6 | 2 | **0** |
| part-b, `f34e0ed` | 6 | 6 | 2 | **0** |

The six failing node ids are #365's, the same set at both tips. Each fails at the same first-divergence byte offset as at T003 and in wave-02, and the baseline and generated sizes are the same at both tips. A change before the first divergence would have moved an offset. T003's masking caveat still stands: a change after the first divergence in a red example is not seen by this suite, and for `maestro-reference` that floor is byte 52.

| Node id (`test_unmodified_examples_byte_identical_pdfs[...]`) | First divergence, T003 and W2 | Part A | part-b | Baseline and generated size, both tips |
|---|---|---|---|---|
| `[web-app]` | 224224 | 224224 | 224224 | 1322909 and 1322910 |
| `[microservices]` | 261105 | 261105 | 261105 | 1375313 and 1375314 |
| `[ascii-web-api]` | 197843 | 197843 | 197843 | 1281938 and 1281939 |
| `[mermaid-agentic-app]` | 260842 | 260842 | 260842 | 2176776 and 2176694 |
| `[free-text-microservice]` | 221304 | 221304 | 221304 | 1318260 and 1318261 |
| `[maestro-reference]` | 52 | 52 | 52 | 7034341 and 7073393 |

- The two skips are the ones at T003: `test_feature_142_zero_edit_invariant_on_detection_agents` (it runs only on `142-` branches) and `test_feature_142_multi_agent_gate_predicate_false_on_baselines[mermaid-agentic-app]` (excluded per F-142 T033).
- The six passes are `test_feature_142_backward_compat_pattern_defaults` and the other five `test_feature_142_multi_agent_gate_predicate_false_on_baselines[...]` cases.
- The suite rewrote the same 21 tracked PNGs in each clone: 3 under `examples/maestro-reference/attack-chains/`, 6 under `examples/maestro-reference/attack-trees/` and 12 under `examples/mermaid-agentic-app/attack-trees/`. T003 recorded the same 21. This is #365's hazard again, and why the suite runs only in a scratch clone.

## X-5: Part A's installed-script modules under Python 3.9.6

`TACHI_REQUIRE_TYPST=1 /usr/bin/python3 -m pytest` over the 12 modules the checkpoint lists, in `$SCRATCH/w3t043-A-py39` at `b71a0d7`: **702 passed, 0 failed, 0 skipped** in 62 s. The clone was clean afterwards. The baseline is the checkpoint's 667 passed; collecting the same 12 modules at `2c5fe08` also gives 667 ids, so the per-module baseline below is exact.

| Module | At `2c5fe08` | Now | Change |
|---|---|---|---|
| `tests/scripts/test_agent_privilege_guard.py` | 146 | 154 | +8 |
| `tests/scripts/test_coverage_attestation.py` | 16 | 16 | 0 |
| `tests/scripts/test_executive_architecture_payload.py` | 12 | 12 | 0 |
| `tests/scripts/test_extract_infographic_data.py` | 60 | 60 | 0 |
| `tests/scripts/test_extract_report_data.py` | 54 | 54 | 0 |
| `tests/scripts/test_extraction_sibling_parity.py` | 7 | 7 | 0 |
| `tests/scripts/test_extractor_contract_fixes.py` | 8 | 8 | 0 |
| `tests/scripts/test_gemini_request_contract.py` | 66 | 66 | 0 |
| `tests/scripts/test_isolated_profile_contract.py` | 187 | 202 | +15 |
| `tests/scripts/test_report_posture_contract.py` | 6 | 6 | 0 |
| `tests/scripts/test_tachi_parsers.py` | 48 | 48 | 0 |
| `tests/scripts/test_write_confinement.py` | 57 | 69 | +12 |
| **Total** | **667** | **702** | **+35** |

- The +35 is test_agent_privilege_guard +8 (X-2), test_isolated_profile_contract +15 (the AR-21 and AR-21a controls) and test_write_confinement +12 (X-1). No other module changed.
- The checkpoint's table gives X-5's branch as "both", so the same 12 modules also ran on part-b (`$SCRATCH/w3t043-B-py39`, `f34e0ed`): 702 passed, 0 failed, 0 skipped, the same per-module counts.
- Part A has no Python 3.9 CI leg, and part-b's `py39-floor` job runs only its two B2 modules, so this run is the 3.9 coverage of these 12 modules.

## The zsh manual-loop cases

zsh 5.9 is on the PATH, so the cases that skip on a runner without zsh ran. Each passed; none was skipped.

| Case | Part A, 3.12.11 | Part A, 3.9.6 | part-b, 3.12.11 | part-b, 3.9.6 |
|---|---|---|---|---|
| `test_install_manifest_completeness.py::test_manual_install_loop_zsh` | passed | passed | passed | passed |
| `test_install_manifest_completeness.py::test_installed_agent_tools_match_matrix[manual-loop-zsh]` | passed | passed | passed | passed |

- Both live in `test_install_manifest_completeness.py`. Each has a `pytest.skip` when zsh is not on the PATH, which is what a CI runner without zsh would do.
- On part-b, `test_tachi_version_marker.py` also runs the README manual-install block under zsh, with the same skip. Both cases passed under 3.12.11 in the matrix run and under 3.9.6 in the `py39-floor` run:
  - `test_tachi_version_marker.py::test_manual_loop_writes_the_describe_value[zsh]`
  - `test_tachi_version_marker.py::test_manual_loop_without_a_git_tree_reads_unknown[zsh]`

## Guard self-test

`python3 -I -B scripts/check-agent-privileges.py --self-test`, run in the `-py39` clones.

| Tip | 3.12.11 | 3.9.6 |
|---|---|---|
| Part A `b71a0d7` | exit 0 | exit 0 |
| part-b `f34e0ed` | exit 0 | exit 0 |

Each run reported C1 to C7 as PASS (21 agents, 6 commands, 3 Bash-capable agents, 21 write-location paths) and C8 as PASS (mutations M1 to M5 each detected by the check named for it). The clones were clean afterwards.

## part-b: B1 is absent

The TW-B1 stop removed B1, so part-b carries B2 only. Validated in `$SCRATCH/w3t043-B-py39` at `f34e0ed`, and in the Part A clone for comparison:

| Check | part-b | Part A |
|---|---|---|
| `git ls-files -- scripts/archive-run-transcripts.py schemas/run-manifest.yaml tests/scripts/test_archive_run_transcripts.py tests/fixtures/transcripts \| wc -l` | **0** | 0 |
| Tracked file names matching the archiver script, the run-manifest schema, `fixtures/transcripts` or the archiver test | 1: `specs/391-isolated-auditable-operation/contracts/run-manifest.md`, a contract document, not a module or fixture | the same 1 |
| Workflow files under `.github` that name the archiver | 0 | 0 |
| `INSTALL_MANIFEST.md` lines that name the archiver or the run manifest | 0 | 0 |
| Files under `tests/` that name the archiver or the run manifest | 0 | 0 |
| Tracked files outside `specs/`, `docs/` and `CHANGELOG.md` that name the archiver | 0 | 0 |
| `tachi-pytest.yml` run list | 23 modules, no archiver module | 21 modules |
| `py39-floor` job list | 2 modules: `test_tachi_version_marker.py`, `test_threats_schema_contract.py` | no such job |

## Test ids against the earlier records

`pytest --collect-only` on 3.12.11, to catch a test that vanished without failing.

- **T003 pre-state (`46aec8d`).** The 30 modules that exist there (the 19 matrix modules, `test_install_manifest_completeness.py`, the 7 extraction-fidelity modules, `test_report_posture_contract.py`, `test_coverage_attestation.py`, `test_backward_compatibility.py`) collect 562 ids. At Part A and at part-b the same 30 modules collect 569 each. **0 ids are missing at either tip.** The 7 new ids are all in `test_install_manifest_completeness.py` (10 to 17).
- **W2, Part A (`8273669`).** The 21 matrix modules collected 594 ids; the same modules now collect 617. One id is missing: `test_self_test_stays_valid_on_a_drifted_tree` (unparametrized), which X-2 replaced with four parametrized cases of the same name. 24 ids are new: 9 in `test_agent_privilege_guard.py` (those four cases and five more) and 15 in `test_isolated_profile_contract.py`.
- **W2, part-b (`7e64fd7`).** Excluding `test_archive_run_transcripts.py` (828 ids, removed by the TW-B1 stop), the other 21 modules collected 377 ids and collect 390 now, **0 missing**. The 13 new ids are in `test_tachi_version_marker.py` (10) and `test_threats_schema_contract.py` (3).

## Main-tree check

`git -C <main tree> status --short`, run after every set had finished and before these two records were written (02:46 UTC):

```
?? .aod/revision-context.md
```

That is only the file that was already untracked at the start of the session. No pytest and no extractor ran in the main tree, and the only other git use there was `git clone` reading from it.

The same command after the records were written (02:48 UTC):

```
 M specs/391-isolated-auditable-operation/test-results/security-b1.md
 M specs/391-isolated-auditable-operation/test-results/w3-sweeps.md
?? .aod/revision-context.md
?? specs/391-isolated-auditable-operation/test-results/w3-gated-suite.md
?? specs/391-isolated-auditable-operation/test-results/wave-03/results.json
```

- `.aod/revision-context.md` is the file that was already untracked.
- The two `??` records under `specs/391-isolated-auditable-operation/test-results/` are this run's output, the only files T043 wrote.
- The two ` M` files are **not this run's**. `tasks.md` names both as append targets (T041 appends to `w3-sweeps.md`, T042 to `security-b1.md`). `w3-sweeps.md` now ends with a section headed "T041: W3 sweeps (tester, 2026-11-20)" (modified 21:48 local) and `security-b1.md` with one headed "T042: W3 snippet review (2026-11-20)" (modified 21:47 local). Both changes appeared after the first status above, which shows neither file as modified, and T043 writes to neither file.
- So the expected state, `.aod/revision-context.md` plus the two records, holds for this run's own writes. The two extra ` M` lines come from the T041 and T042 work that was running alongside, not from T043.

## Gate verdict

**PASS** (soft gate, `gate_decision: pass`). The rule is: PASS only if there are no regressions and no new failures outside #365's six.

| Count | Value |
|---|---|
| Regressions (a node id that passes at T003 and fails now) | **0** |
| New failures outside #365's six | **0** |
| Pre-existing failures, both tips | 6 each: #365's `test_unmodified_examples_byte_identical_pdfs[...]` cases, offsets unchanged |

Totals per tip, over the gated sets run on 3.12.11 (the matrix, the three install-fidelity jobs, `test_coverage_attestation.py` and the byte-identity suite):

| Tip | Passed | Failed | Skipped | xfailed |
|---|---|---|---|---|
| Part A `b71a0d7` | 984 | 6 | 3 | 1 |
| part-b `f34e0ed` | 1113 | 6 | 3 | 1 |

The failed column is #365's six on each tip. The 3.9.6 sets (X-5, py39-floor, the extra manifest-completeness run) are separate and add 0 failures; their counts are in the tables above.

## What this run does not cover

- CI. The runs are local on macOS arm64. The ubuntu legs, the macOS CI leg, the runner without zsh and CI's own Python 3.11 are CI's to report; S2b step 1 re-checks CI on both tips.
- Python 3.11. The local 3.12.11 stands in for the matrix's 3.11, and the stock macOS 3.9.6 stands in for CI's Linux 3.9.
- The rest of `tests/scripts/` and `tests/schemas/`. The T003 census found 35 failures and errors there, all outside every gate and all older than the feature (listed in `wave-01/census-failing.txt`). This run did not repeat the census.

## Re-run on the final W3 tips (after T044's fixes)

Dated 2026-11-20, local night (capture 04:05 to 04:21 UTC on 2026-11-21).

**Result: PASS.** Both final tips pass every gated set again, with the same results as the first run apart from the new tests. This is the full T043 re-run that G3 requires.
- 0 regressions and 0 new failures.
- The only failures are #365's six byte-identity cases, on both tips, at the same first-divergence offsets as in T003 and in the first run, and with the same baseline and generated sizes as in the first run.
- X-5 passes: 706 tests under Python 3.9.6 with Typst required (the first run had 702; the baseline is 667).
- The zsh manual-loop cases passed on both tips. None was skipped.
- Part-b still holds no archiver module, schema, test or fixture.
- Totals on Python 3.12.11 over the gated sets (the run list, the three install-fidelity jobs, `test_coverage_attestation.py` and the byte-identity suite): Part A 988 passed, 6 failed, 3 skipped, 1 xfailed; part-b 1121 passed, 6 failed, 3 skipped, 1 xfailed. The failures are #365's six on each tip.

| Item | Value |
|---|---|
| Part A tip | `6ade38411dae4999ee1f103c6cb08769d77ee308`, branch `391-isolated-auditable-operation`; 7 commits after the first run's `b71a0d7` |
| part-b tip | `3cc82948abfa2f5c2702f296001aa766c7ff3f41`, branch `391-isolated-auditable-operation-part-b`: the BX''''' merge after the T044 fixes; 12 commits after the first run's `f34e0ed` |
| What changed in code and tests since the first run | **Part A:**<br>• `scripts/check-agent-privileges.py` refuses ambiguous frontmatter delimiters (CR-1), with 4 new exit-2 cases in `tests/scripts/test_agent_privilege_guard.py`.<br>• `.claude/agents/tachi/report-assembler.md` quotes paths that contain spaces (CR-6).<br>• The runbook, ADR-049, a contract line each in `cli-contracts.md` and `version-marker.md`, and the records.<br>**part-b adds:**<br>• The marker line's nested-copy rule in `README.md` and `DEVELOPER_GUIDE_TACHI.md`, with 4 new cases in `tests/scripts/test_tachi_version_marker.py` (CR-2, CR-5).<br>• The section 8.4 row wording in `CLAUDE_PERMISSIONS.md` (CR-7).<br>• `tachi-pytest.yml` comment wording (CR-4) and a docstring edit in `test_threats_schema_contract.py` (CR-8). The run lists did not change. |
| Scratch clones | Ten fresh clones at new paths, `git clone --no-hardlinks` of the local repo and then `git checkout <tip>`; `git log -1` was checked before any result was read (every run log opens with the head and its full SHA).<br>• `$SCRATCH/w3t043r2-{A,B}-{gated,fid,byte,py39}`: the same eight roles as the first run (run list; install-fidelity and attestation; byte-identity on a fresh tree; guard, permissions steps, X-5, py39-floor and the 3.9.6 extras).<br>• `$SCRATCH/w3t043r2-{A,B}-coll`: `--collect-only` only, to compare test ids with the first run's tips and the T003 pre-state.<br>The first run's clones were used read-only, for `--collect-only` at its tips |
| Python and tools | As in the first run: **3.12.11** (pytest 9.1.0, pytest-timeout 2.4.0, PyYAML 6.0.3; CI runs 3.11) for the gated sets, **3.9.6** (`/usr/bin/python3`, pytest 8.4.2) for X-5, py39-floor and the extra manifest-completeness run; typst 0.14.2, mmdc 11.12.0, zsh 5.9, jq 1.7.1, `/bin/bash` 3.2.57, macOS arm64 |
| Run lists | Read again from each clone's own workflow file: 21 modules on Part A, 23 on part-b, and 2 in part-b's `py39-floor` job. All three lists, and the install-fidelity jobs' lists, are identical to the first run's |
| Main tree | No pytest and no extractor ran in it (the #365 rule). The `git status --short` runs are under "Main-tree check (re-run)" below |

The "first run" column is this file's first part (`b71a0d7` and `f34e0ed`).

### Part A: `6ade384`

| Set | Python | Passed | Failed | Skipped | xfailed | First run (`b71a0d7`), and the change |
|---|---|---|---|---|---|---|
| `tachi-pytest.yml` run list, 21 modules, `--timeout=1080` | 3.12.11 | 619 | 0 | 1 | 1 | 615 passed, 1 skipped, 1 xfailed; +4: the CR-1 exit-2 cases |
| install-fidelity `manifest-completeness` | 3.12.11 | 17 | 0 | 0 | 0 | 17 passed |
| install-fidelity `extraction-fidelity`, 7 modules | 3.12.11 | 255 | 0 | 0 | 0 | 255 passed |
| install-fidelity `report-posture` + `test_write_confinement.py`, `TACHI_REQUIRE_TYPST=1` | 3.12.11 | 75 | 0 | 0 | 0 | 75 passed |
| `test_coverage_attestation.py`, run explicitly | 3.12.11 | 16 | 0 | 0 | 0 | 16 passed |
| `test_backward_compatibility.py` (byte-identity), fresh clone | 3.12.11 | 6 | 6 | 2 | 0 | 6 passed, 6 failed, 2 skipped; T003: 6 failed, 6 passed, 2 skipped |
| `check-agent-privileges.py --self-test` | 3.12.11 | exit 0 | | | | exit 0 |
| `check-agent-privileges.py --self-test` | 3.9.6 | exit 0 | | | | exit 0 |
| **X-5**: 12 installed-script modules, `TACHI_REQUIRE_TYPST=1` | 3.9.6 | 706 | 0 | 0 | 0 | 702 passed; +4: the CR-1 cases; checkpoint baseline 667 |
| `manifest-completeness`, for the zsh cases under 3.9 (extra) | 3.9.6 | 16 | 0 | 1 | 0 | 16 passed, 1 skipped |
| Permissions workflow run steps, incl. the guard with `--self-test` (extra) | 3.12.11 | exit 0 | | | | exit 0 |

- The run list took 14 min 53 s and all 621 collected ids are accounted for (passed, skipped or xfailed, as in the table). The 4 new ids are `test_agent_privilege_guard.py::test_an_input_the_guard_cannot_interpret_is_exit_2[...]` with the parameters `allow-listed-document-with-a-yaml-opener`, `command-indented-delimiter-hides-allowed-tools`, `document-end-marker-hides-a-key`, `indented-delimiter-hides-a-key`.
- The skip and the xfail are the same two as in the first run and at T003: `test_init_precommit_matrix.py::test_tty_no_flag_default_y` and `test_init_sh_substitution.py::test_personalized_tree_bytes_match_baseline`.
- Under 3.9.6, `manifest-completeness` skips `test_distributable_imports_stdlib_only` (it needs Python 3.10 or later), as in the first run. It is not a zsh case.

### part-b: `3cc8294`

| Set | Python | Passed | Failed | Skipped | xfailed | First run (`f34e0ed`), and the change |
|---|---|---|---|---|---|---|
| `tachi-pytest.yml` run list, 23 modules, `--timeout=1080` | 3.12.11 | 752 | 0 | 1 | 1 | 744 passed, 1 skipped, 1 xfailed; +8: the 4 CR-1 cases and 4 marker cases |
| `py39-floor` job list, 2 modules, `--timeout=600` | 3.9.6 | 132 | 0 | 1 | 0 | 128 passed, 1 skipped; +4: the marker cases |
| install-fidelity `manifest-completeness` | 3.12.11 | 17 | 0 | 0 | 0 | 17 passed |
| install-fidelity `extraction-fidelity`, 7 modules | 3.12.11 | 255 | 0 | 0 | 0 | 255 passed |
| install-fidelity `report-posture` + `test_write_confinement.py`, `TACHI_REQUIRE_TYPST=1` | 3.12.11 | 75 | 0 | 0 | 0 | 75 passed |
| `test_coverage_attestation.py`, run explicitly | 3.12.11 | 16 | 0 | 0 | 0 | 16 passed |
| `test_backward_compatibility.py` (byte-identity), fresh clone | 3.12.11 | 6 | 6 | 2 | 0 | 6 passed, 6 failed, 2 skipped; T003: 6 failed, 6 passed, 2 skipped |
| `check-agent-privileges.py --self-test` | 3.12.11 | exit 0 | | | | exit 0 |
| `check-agent-privileges.py --self-test` | 3.9.6 | exit 0 | | | | exit 0 |
| X-5's 12 modules on part-b as well, `TACHI_REQUIRE_TYPST=1` (extra) | 3.9.6 | 706 | 0 | 0 | 0 | 702 passed; +4: the CR-1 cases |
| `manifest-completeness`, for the zsh cases under 3.9 (extra) | 3.9.6 | 16 | 0 | 1 | 0 | 16 passed, 1 skipped |
| Permissions workflow run steps, incl. the guard with `--self-test` (extra) | 3.12.11 | exit 0 | | | | exit 0 |

- The run list took 15 min 11 s and all 754 collected ids are accounted for (passed, skipped or xfailed, as in the table). The 8 new ids are the same 4 guard cases and these 4 in `test_tachi_version_marker.py`: `test_manual_loop_inside_another_repo_reads_unknown[bash]`, `test_manual_loop_inside_another_repo_reads_unknown[zsh]`, `test_marker_guard_refuses_a_non_regular_marker`, `test_marker_guard_refuses_a_symlinked_marker`.
- The `py39-floor` skip is `test_threats_schema_contract.py::test_the_stamp_script_imports_only_the_standard_library` (a 3.10+ guard), as in the first run. All 4 new marker cases pass under 3.9.6 as well.
- The run list's skip and xfail are the same two as on Part A.

### Byte-identity against the T003 pre-state

`tests/scripts/test_backward_compatibility.py` ran once per tip, each in a fresh clone that nothing else had touched, on 3.12.11. The pre-state is **6 failed, 6 passed, 2 skipped**.

| Tip | Failed | Passed | Skipped | New failures |
|---|---|---|---|---|
| T003, `46aec8d` | 6 | 6 | 2 | none |
| First run, Part A `b71a0d7` and part-b `f34e0ed` | 6 and 6 | 6 and 6 | 2 and 2 | 0 and 0 |
| Part A, `6ade384` | 6 | 6 | 2 | **0** |
| part-b, `3cc8294` | 6 | 6 | 2 | **0** |

The six failing node ids are #365's, the same set at both tips and the same as in the first run. Each fails at the same first-divergence byte offset as at T003 and in the first run (web-app 224224, microservices 261105, ascii-web-api 197843, mermaid-agentic-app 260842, free-text-microservice 221304, maestro-reference 52), and with the same baseline and generated sizes as in the first run. T003's masking caveat still stands: a change after the first divergence in a red example is not seen by this suite, and for `maestro-reference` that floor is byte 52.

- The two skips and the six passes are the same cases as in the first run.
- The suite rewrote the same 21 tracked PNGs in each clone (3 under `examples/maestro-reference/attack-chains/`, 6 under `examples/maestro-reference/attack-trees/`, 12 under `examples/mermaid-agentic-app/attack-trees/`), as at T003 and in the first run.

### X-5: Part A's installed-script modules under Python 3.9.6

`TACHI_REQUIRE_TYPST=1 /usr/bin/python3 -m pytest` over the 12 modules the checkpoint lists, in `$SCRATCH/w3t043r2-A-py39` at `6ade384`: **706 passed, 0 failed, 0 skipped** in 84 s. The clone was clean afterwards. The same modules on part-b (`$SCRATCH/w3t043r2-B-py39`, `3cc8294`): 706 passed, 0 failed, 0 skipped, the same per-module counts.

| Module | At `2c5fe08` (baseline) | First run (`b71a0d7`) | Now (`6ade384`) | Change since the first run |
|---|---|---|---|---|
| `tests/scripts/test_agent_privilege_guard.py` | 146 | 154 | 158 | +4 |
| `tests/scripts/test_coverage_attestation.py` | 16 | 16 | 16 | 0 |
| `tests/scripts/test_executive_architecture_payload.py` | 12 | 12 | 12 | 0 |
| `tests/scripts/test_extract_infographic_data.py` | 60 | 60 | 60 | 0 |
| `tests/scripts/test_extract_report_data.py` | 54 | 54 | 54 | 0 |
| `tests/scripts/test_extraction_sibling_parity.py` | 7 | 7 | 7 | 0 |
| `tests/scripts/test_extractor_contract_fixes.py` | 8 | 8 | 8 | 0 |
| `tests/scripts/test_gemini_request_contract.py` | 66 | 66 | 66 | 0 |
| `tests/scripts/test_isolated_profile_contract.py` | 187 | 202 | 202 | 0 |
| `tests/scripts/test_report_posture_contract.py` | 6 | 6 | 6 | 0 |
| `tests/scripts/test_tachi_parsers.py` | 48 | 48 | 48 | 0 |
| `tests/scripts/test_write_confinement.py` | 57 | 69 | 69 | 0 |
| **Total** | **667** | **702** | **706** | **+4** |

- Only `test_agent_privilege_guard.py` changed since the first run: +4, the CR-1 exit-2 cases. Against the checkpoint's 667 the total is +39: guard +12 (X-2 and CR-1), profile contract +15, write confinement +12.

### The zsh manual-loop cases

zsh 5.9 is on the PATH, so the cases that skip on a runner without zsh ran. Each passed; none was skipped.

| Case | Part A, 3.12.11 | Part A, 3.9.6 | part-b, 3.12.11 | part-b, 3.9.6 |
|---|---|---|---|---|
| `test_install_manifest_completeness.py::test_manual_install_loop_zsh` | passed | passed | passed | passed |
| `test_install_manifest_completeness.py::test_installed_agent_tools_match_matrix[manual-loop-zsh]` | passed | passed | passed | passed |

- On part-b, `test_tachi_version_marker.py` runs the README manual-install block under zsh, with the same skip. Its three zsh cases passed under 3.12.11 in the run list and under 3.9.6 in the `py39-floor` run. The first two are from the first run; the third is new (CR-2, CR-5):
  - `test_tachi_version_marker.py::test_manual_loop_inside_another_repo_reads_unknown[zsh]` (new)
  - `test_tachi_version_marker.py::test_manual_loop_without_a_git_tree_reads_unknown[zsh]`
  - `test_tachi_version_marker.py::test_manual_loop_writes_the_describe_value[zsh]`

### Guard self-test

`python3 -I -B scripts/check-agent-privileges.py --self-test`, run in the `-py39` clones. The guard and `report-assembler.md` both changed since the first run.

| Tip | 3.12.11 | 3.9.6 |
|---|---|---|
| Part A `6ade384` | exit 0 | exit 0 |
| part-b `3cc8294` | exit 0 | exit 0 |

Each run reported C1 to C7 as PASS (21 agents, 6 commands, 3 Bash-capable agents, 21 write-location paths) and C8 as PASS (mutations M1 to M5 each detected by the check named for it). The permissions workflow's run steps (jq present, settings.json well-formed, the AC-2 cross-check, the section 3 and 4 heading checks, python3 present, the guard with `--self-test`) also exit 0 on both tips. The clones were clean afterwards.

### part-b: B1 is still absent

Validated in `$SCRATCH/w3t043r2-B-py39` at `3cc8294`, and in the Part A clone for comparison:

| Check | part-b | Part A |
|---|---|---|
| `git ls-files -- scripts/archive-run-transcripts.py schemas/run-manifest.yaml tests/scripts/test_archive_run_transcripts.py tests/fixtures/transcripts \| wc -l` | **0** | 0 |
| Tracked file names matching the archiver script, the run-manifest schema, `fixtures/transcripts` or the archiver test | 1: `specs/391-isolated-auditable-operation/contracts/run-manifest.md`, a contract document, not a module or fixture | the same 1 |
| Workflow files under `.github` that name the archiver | 0 | 0 |
| `INSTALL_MANIFEST.md` lines that name the archiver or the run manifest | 0 | 0 |
| Files under `tests/` that name the archiver or the run manifest | 0 | 0 |
| Tracked files outside `specs/`, `docs/` and `CHANGELOG.md` that name the archiver | 0 | 0 |
| `tachi-pytest.yml` run list | 23 modules, no archiver module | 21 modules |
| `py39-floor` job list | 2 modules: `test_tachi_version_marker.py`, `test_threats_schema_contract.py` | no such job |

### Test ids against the earlier records

`pytest --collect-only` on 3.12.11, to catch a test that vanished without failing.

- **T003 pre-state (`46aec8d`).** The 30 modules that exist there collect 562 ids. At the final Part A and part-b tips the same 30 modules collect 569 each. **0 ids are missing at either tip**; the 7 new ids are the same 7 in `test_install_manifest_completeness.py` as in the first run.
- **The first run's tips.** Over the gated modules (the run list, the install-fidelity jobs, `test_coverage_attestation.py` and `test_backward_compatibility.py`), Part A `b71a0d7` collected 994 ids and `6ade384` collects 998; part-b `f34e0ed` collected 1123 and `3cc8294` collects 1131. **0 ids are missing at either tip.** The 4 new Part A ids and 8 new part-b ids are the ones named above.

### Main-tree check (re-run)

`git -C <main tree> status --short`, run after every set had finished and before these records were written:

```
 M specs/391-isolated-auditable-operation/NEXT-SESSION.md
?? .aod/revision-context.md
```

No pytest and no extractor ran in the main tree, and the only other git use there was `git clone` reading from it. The same command after `w3-gated-suite.md` and `wave-03/results.json` were updated:

```
 M specs/391-isolated-auditable-operation/NEXT-SESSION.md
 M specs/391-isolated-auditable-operation/test-results/w3-gated-suite.md
 M specs/391-isolated-auditable-operation/test-results/wave-03/results.json
?? .aod/revision-context.md
```

- ` M .../w3-gated-suite.md` and ` M .../wave-03/results.json` are this run's output. They show as modified, not untracked, because the first run's versions are already committed (`b2385ca`). They are the only files T043 wrote.
- ` M .../NEXT-SESSION.md` is the S2b handoff file. It was already modified when the first status above was taken (modified 23:05 local, 04:05 UTC, as this re-run began), so it is not from T043, which does not write to it.
- `?? .aod/revision-context.md` is the file that was already untracked at the start of the session.
- So T043's own writes are exactly the two records, and the main tree holds nothing else of T043's.

### Gate verdict (re-run on the final tips)

**PASS** (soft gate, `gate_decision: pass` in `wave-03/results.json`). The rule is: PASS only if there are no regressions and no new failures outside #365's six.

| Count | Value |
|---|---|
| Regressions (a node id that passes at T003 and fails now) | **0** |
| New failures outside #365's six | **0** |
| Pre-existing failures, both tips | 6 each: #365's `test_unmodified_examples_byte_identical_pdfs[...]` cases, offsets unchanged |

Totals per final tip, over the gated sets run on 3.12.11 (the run list, the three install-fidelity jobs, `test_coverage_attestation.py` and the byte-identity suite):

| Tip | Passed | Failed | Skipped | xfailed |
|---|---|---|---|---|
| Part A `6ade384` | 988 | 6 | 3 | 1 |
| part-b `3cc8294` | 1121 | 6 | 3 | 1 |

The failed column is #365's six on each tip. The 3.9.6 sets (X-5 at 706 passed on both tips, py39-floor at 132 passed and 1 skipped, the extra manifest-completeness runs) are separate and add 0 failures; their counts are in the tables above. This section covers the same ground as the first run and does not cover CI, Python 3.11 or the rest of `tests/scripts/`; see "What this run does not cover" above.

