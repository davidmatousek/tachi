# W0 pre-state and branches (T003)

**Result:** the pre-state is frozen at `46aec8d`.
- The three workflows are green at HEAD.
- The byte-identity suite fails only on the six #365 cases.
- 0 of 75 file:line anchors are broken; 6 moved.
- The Part B branch, its worktree and its draft PR exist.
- **G0 passes.**

| Item | Value |
|---|---|
| Date | 2026-11-19 (capture 21:17–21:30 UTC) |
| Part A HEAD | `46aec8d`: a merge of `origin/main` (`39af1ce`, release 4.48.2) into `864121b` (the W0' record). A merge, not a rebase, and clean: no file was changed on both sides. Pushed. |
| T0 | The key-handling patch is on `main` as `1c03746` (#394), released in 4.48.2 (`39af1ce`) |
| What the merge brought | 11 files: `threat-infographic.md`, `gemini-prompt-construction.md`, the adapter's `infographic-gemini-api.md`, `README.md`, `DEVELOPER_GUIDE_TACHI.md`, `scripts/install.sh`, `.env.example`, `tachi-pytest.yml`, `CHANGELOG.md`, `.release-please-manifest.json`, and the new `tests/scripts/test_gemini_key_env_only.py` |
| Part B branch | `391-isolated-auditable-operation-part-b`, created from `46aec8d` and pushed. Its first commit, `97db2e6`, is an empty `feat(391): isolated and auditable operation (Part B)` opener, because a PR needs at least one commit ahead of its base |
| Part B PR | Draft PR #396, with base `391-isolated-auditable-operation`. Its title and body passed the Wording sweep: Pattern A 0, Pattern B 0 |
| Worktrees | part-b: `$SCRATCH/wt/391-part-b`. A read-only view of `46aec8d` for audits: `$SCRATCH/wt/ro-46aec8d` |
| Scratch clones | • `$SCRATCH/prestate-A`: the gated sets.<br>• `$SCRATCH/prestate-B`: the byte-identity suite, on a fresh tree.<br>• `$SCRATCH/prestate-C`: the census.<br>Each is a `git clone --no-hardlinks` of the local repo, checked out at `46aec8d`; `git log -1` was checked before reading any result.<br>`$SCRATCH` is the build session's scratchpad, outside every work tree. Its absolute path is left out because it contains a home-directory path |
| Local toolchain | Python 3.12.11 (CI uses 3.11), pytest 9.1.0, typst 0.14.2, mmdc 11.12.0, jq 1.7.1, `/bin/bash` 3.2.57 |

## CI at HEAD

`46aec8d` differs from `39af1ce` only in the feature's planning records:
- `specs/391-isolated-auditable-operation/**`
- `docs/product/**`
- `docs/architecture/01_system_design/README.md`

None of those paths is in any of the three workflows' path anchors. On the merge, PR #392 therefore ran only gitleaks (pass), and the `push:[main]` runs at `39af1ce` stand for HEAD.

| Workflow | Evidence | Result |
|---|---|---|
| `tachi-pytest.yml` | push run 44532606708 at `39af1ce` | success, both legs |
| `tachi-install-fidelity.yml` | push run 44532606662 at `39af1ce` | success |
| `tachi-permissions-verify.yml` | Last run: 28546232009 at `cf8ef12` (2026-07-01). Its four anchored paths are unchanged from `cf8ef12` to `46aec8d` | success |

An unrelated observation: the release-please PR runs of `tachi-pytest.yml` and `tachi-install-fidelity.yml` fail with no jobs ("workflow file issue"). That happened on #395 and on October's release PR alike, and the `main` push runs after each merge are green.

## Local gated sets (clone A)

| Set | Scope | Result |
|---|---|---|
| `tachi-pytest.yml` run list | The 19 modules at `46aec8d`, including `test_gemini_key_env_only.py`; `--timeout=1080` | 259 passed, 1 skipped, 1 xfailed (763 s) |
| install-fidelity `manifest-completeness` | `test_install_manifest_completeness.py` | 10 passed |
| install-fidelity `extraction-fidelity` | 7 modules | 255 passed. mmdc is installed locally, so the image-flag cases ran instead of skipping |
| install-fidelity `report-posture` | `TACHI_REQUIRE_TYPST=1`, `test_report_posture_contract.py` | 6 passed |
| permissions-verify, run locally | jq presence; `jq empty .claude/settings.json`; the AC-2 cross-check script; the §3 and §4 heading greps | exit 0 |
| `test_coverage_attestation.py` (not gated; T012 edits it) | 1 module | 16 passed |

Skipped and xfailed at baseline:
- `test_init_sh_substitution::test_personalized_tree_bytes_match_baseline` is an xfail. Its baseline fixture has been stale since v4.44.0.
- `test_init_precommit_matrix::test_tty_no_flag_default_y` is skipped because it needs a real TTY.

The clone stayed clean after every set: `git status --short` was empty.

## Byte-identity suite (clone B, fresh tree)

`tests/scripts/test_backward_compatibility.py`: **6 failed, 6 passed, 2 skipped**. These are the same totals as F-362's T024 record.

| Example | First divergence (byte offset) | Signature |
|---|---|---|
| web-app | 224224 | font-subset tag `/ZZMJWG+` in the baseline, `/SPUEUJ+` in the render (#365, mechanism 1) |
| microservices | 261105 | same offset as F-362 T024 |
| ascii-web-api | 197843 | same offset as F-362 T024 |
| mermaid-agentic-app | 260842 | same offset as F-362 T024 |
| free-text-microservice | 221304 | same offset as F-362 T024 |
| maestro-reference | **52** | **Changed.** The page tree's `/Count` is 86 in the baseline and 88 in the render. F-362 T024 recorded 828878, the font tag |

The two skips:
- `test_feature_142_zero_edit_invariant_on_detection_agents` runs only on `142-` branches.
- `test_feature_142_multi_agent_gate_predicate_false_on_baselines[mermaid-agentic-app]` is excluded per F-142 T033.

**maestro-reference.**
- The six failing node ids are unchanged, so they remain the pre-existing set for 391's gates.
- But the maestro-reference red no longer stops at the font tag. Its render now has two more pages than its baseline.
- From byte 52 onward, any later change to that example is masked. That is the masking floor #365 describes.
- Commits that touched the render path since F-362 T024: `3d67ca7` (F-362 simplify), `109705c` (F-373), `d909992` (F-373 documentation review). The local toolchain may also differ from August's.
- The cause is not investigated here; it belongs to #365.

**The suite rewrites tracked inputs.** After this one run, clone B had 21 modified PNGs:
- 9 under `examples/maestro-reference/attack-{trees,chains}/`;
- 12 under `examples/mermaid-agentic-app/attack-trees/`.

That is why the #365 rule stands: the suite and the extractors run only in scratch clones.

## File:line anchors (DEVOPS-E)

75 anchors were checked at `46aec8d`: the 62 that tasks.md cites, plus 13 more in plan.md's Source Code block. **69 hold, 6 moved, 0 are broken.**

| Task | Anchor as cited | Now | Cause |
|---|---|---|---|
| T009 | `DEVELOPER_GUIDE_TACHI.md` 1710–1732 | 1710–1733 | +1: the merge added one line at 1717–1718 |
| T009 | `DEVELOPER_GUIDE_TACHI.md` 1798–1802 | 1799–1803 | the same +1 |
| plan | `DEVELOPER_GUIDE_TACHI.md :1607-1608` | 1609 | already off before the merge. tasks.md already uses 1609 |
| plan | `tachi-pytest.yml :84-127` (path anchor) | 84–131 | +4: the four F-393 entries |
| plan | `tachi-pytest.yml :147-150` (Python step) | 151–154 | +4 |
| plan | `tachi-pytest.yml :199-219` (run list) | 203–224 | +4 at the start, +5 at the end |

Other drift:
- **T043's module count.** `tachi-pytest.yml` now runs **19** modules, not 18.
- **New triggers.** That workflow's path anchor now lists `threat-infographic.md` and `gemini-prompt-construction.md` as inputs, so the edits in T013 and T005 will trigger it.
- **T005's client pin is not needed.** The key-handling patch already pinned the Gemini request form at `gemini-prompt-construction.md:253-266`: `curl` with the `x-goog-api-key` header passed through `--config -`, and the key read from the environment only. **So R-5 does not apply.**

Notes for later tasks:
1. **T005.** There is a third prompt path:
   - It is the locked executive-architecture block in `.claude/skills/tachi-infographics/references/executive-architecture.md`, lines 140–196.
   - `/tachi.infographic all` and the `exec` alias reach it, and the A10 test hash-pins it.
   - The field list must cover what it sends. The block itself cannot be edited.
2. **T012.** `report-assembler.md` also names the template directory outside Steps 2a, 2c, 3a, 3b and 3d: lines 24, 32–33, 48, 72, 78–79, 83, 107, 160–161 and 216. The same-commit sweep must cover them.
3. **T004, T025, T026.** The first-token Bash families on the live tree are:
   - orchestrator: {`python3`};
   - report-assembler: {`test`, `python3`, `typst`};
   - threat-infographic: {`test`, `python`, `[`}. `python` becomes `python3` in T013.

   The `[` comes from the patch's one-line `if [ -z … ]` key check at `threat-infographic.md:348`; it is the live tree's reserved-word case. The `curl` form lives in the skill reference, where C6 does not look, so §8 must say how it is declared.

   `test_gemini_key_env_only.py` fails on any bare `export $(` in a fenced shell block, so the T012 and T013 recipes must not add one.
4. **T032, T039.** `INSTALL_MANIFEST.md:15` and `:64` say "4 Python files". The Part B whitelist commits must update the count.
5. **T008, T009.** The patch already placed environment-only key statements on the lines these tasks edit.

## G0 (S1 launch gate)

| Check | Result |
|---|---|
| The key-handling patch is merged on `main` (T0) | Yes: `1c03746`, released in 4.48.2 |
| T002's TW-B1 verdict is recorded | Yes: PASS (`w0-spike.md`) |
| No open #369 branch edits the same workflow anchors | Yes: #369 is an open issue with no branch and no PR |
| `/aod.build --no-tests` runs, with its reason recorded | Yes. The reason is the #365 PNG hazard, seen again above; gated sets run in scratch clones |
| The scratch clone path is set | Yes: `$SCRATCH/prestate-{A,B,C}` |

**G0: PASS.** W1 may start. B1 launches once P0-B0 passes (R-6).
