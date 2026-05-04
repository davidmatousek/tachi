# Session Continuation: Adversarial Unit Extraction Hot-Fix (Feature 250)

**Generated**: 2026-05-04 10:19
**Branch**: `250-adversarial-unit-extraction-hotfix`
**Last Commit**: `8447331 chore(250): checkpoint before Wave 4 resume`
**Build status**: Wave 6 of 8 complete — paused at standalone 3-wave hard ceiling

---

## Completed This Session

Build executed Waves 4–6 (8 of 21 tasks). Per `.claude/rules` standalone build ceiling, execution stops after 3 waves and resumes in a fresh conversation.

- **T006** ✓ — `tests/scripts/test_template_substitute_unit.py` authored: 8 substitution cases per data-model.md §Schema 1; 3 shim-sensitive (1/3/6) + 5 not-sensitive (2/4/5/7/8); 8/8 PASS in 0.30s on bash 3.2.57; ZERO `init_sh_helpers` imports
- **T007** ✓ — `tests/scripts/test_init_input_unit.py` authored: 5 input cases per data-model.md §Schema 2 (canary FIRST per FR-007); 5/5 PASS in 0.09s; process-substitution invocation only (R-1 mitigation); rejection-class substrings adapted to helper's actual emissions ("NUL byte"/"control character"/"over-length") per data-model.md §Reason-class authority; `printf '%b'` chosen over `%s` to allow NUL-byte case (Python env vars cannot carry NUL)
- **T015** ✓ — `tests/scripts/test_substitute_shim_canary.py` authored: 1-test TC-1 closure asserting `shopt -u patsub_replacement` substring is present in `.aod/scripts/bash/template-substitute.sh`; failure-mode rehearsed (canary fires loudly with diagnostic message, then passes after byte-identical restoration)
- **T008** ✓ — `tests/scripts/test_init_sh_adversarial.py` delete-block surgery: 122-line deletion (lines 41–162); post-state 166 lines; ONE contiguous deletion, ZERO additions; preserved blocks (lines 1–39, 165–227, 229–288) byte-identical to main; `from init_sh_helpers import ...` line preserved for the 2 retained integration tests
- **T009** ✓ — Local pytest gate 15/15 PASS. Deviation: --timeout=15 too aggressive for the 2 retained integration tests (test_case_13 + test_no_residual take ~140s each on dev hardware); re-ran them with --timeout=300 and both PASSED. Audit: `.aod/results/wave-6-t009-deviation-note.md`
- **T010** ✓ — FR-003 zero-import grep: 0 matches over the 2 new subprocess-invoking modules (grep exit 1)
- **T011** ✓ — TC-4 scope-fence diff: empty (6 files byte-clean vs main: `.aod/scripts/bash/{template-substitute,init-input}.sh`, `tests/scripts/{init_sh_helpers.py,conftest.py}`, `pyproject.toml`, `.github/workflows/tachi-pytest.yml`)
- **T012** ✓ — FR-014 invocation-count audit: 5 active call sites (target ≤5). Audit: `.aod/results/init-sh-invocation-audit-250.md`

Recent commits:
- `8447331 chore(250): checkpoint before Wave 4 resume`
- `7054ca2 chore(250): checkpoint before build resume`
- `f20c785 docs(250): plan stage — spec ✓, plan ✓✓, tasks ✓✓✓`

---

## Current State

- **Phase**: implement (Triad-approved tasks.md; build in progress)
- **Uncommitted**: 6 entries — 2 modified files (`tasks.md` task checkmarks, `test_init_sh_adversarial.py` post-delete state), 3 new test modules (T006/T007/T015), 1 new directory (`specs/250-adversarial-unit-extraction-hotfix/test-results/`)
- **Tasks**: 13 / 21 complete (62%)
- **Audit artifacts** (gitignored, local-only):
  - `.aod/results/wave-4-t006.md` (T006 implementation notes)
  - `.aod/results/wave-4-t007.md` (T007 implementation notes — including helper-class adaptation)
  - `.aod/results/wave-4-t015.md` (T015 failure-mode rehearsal)
  - `.aod/results/wave-6-t009-pytest-output.txt` (raw pytest output)
  - `.aod/results/wave-6-t009-deviation-note.md` (timeout deviation full record)
  - `.aod/results/wave-6-t010-t012-audit.md` (combined audit log)
  - `.aod/results/init-sh-invocation-audit-250.md` (FR-014 invocation-count breakdown)

---

## Next Actions

### TC-3 G-6 HARD GATE — STATUS: PASS

All four conditions met:
- T009 (local pytest) — 15/15 PASS (with timeout deviation noted; integration tests re-run with --timeout=300)
- T010 (zero-import grep) — 0 matches
- T011 (TC-4 scope-fence diff) — empty
- T012 (init.sh invocation count) — 5 active call sites

Wave 8 atomic commit (T016) is now unblocked from a gate perspective. Wave 7 (deliberate-fault matrix) is next.

### Resume sequence (next session)

1. **Wave 7 — Deliberate-fault matrix (T013, T014)** — bash 5.x required for T013
   - **T013**: senior-backend-engineer (bash 5.x shell-switch). On a Linux container / devcontainer / WSL with bash 5.x, run the substitution-shim deliberate-fault matrix per `quickstart.md §4`: backup helper, sed-out the `shopt -u patsub_replacement` line, run pytest, expect cases 1/3/6 FAIL + 2/4/5/7/8 PASS, restore. Record full matrix output (bash version, timestamp, command outputs, PASS/FAIL table per case) in `.aod/results/deliberate-fault-matrix-250.md`. Local dev workstation reports bash 3.2.57 — agent MUST switch shells.
   - **T014**: tester. Inject a temporary breakage in `aod_init_read_validated` (e.g., comment out the rejection regex line in `.aod/scripts/bash/init-input.sh`, NOT a committed change). Run pytest on `test_init_input_unit.py`, confirm at least one rejection case fails, stderr names rejection class, failing test ID is in the unit module. Revert breakage, confirm 5/5 PASS. Append to `.aod/results/deliberate-fault-matrix-250.md` under "## Input-validator regression demonstration".

2. **Wave 8 — Atomic ship (T016, T017, T018, T019)** — devops, sequential
   - **T016**: stage all four new/modified files + spec dir + (per tasks.md) `docs/architecture/01_system_design/README.md` if applicable. Single commit with Conventional-Commits subject `fix(250): extract adversarial unit tests — eliminate cold-cache CI flake`. NO intermediate commits.
   - **T017**: push to draft PR #253 — `git push origin 250-adversarial-unit-extraction-hotfix`.
   - **T018**: `gh pr checks 253 --watch` — confirm both `macos-latest` and `ubuntu-latest` legs green; record `macos-latest` init.sh-suite duration vs baseline `25314246672` (target ≤15 min, ≥25 min savings).
   - **T019**: `gh pr edit 253 --title "fix(250): ..."` if title drifted, then `gh pr ready 253`.

3. **Wave 9 — Post-merge (T020, T021)** — devops; T020 within ~30s of squash-merge; T021 sustained KPI tracking days 1–14, recorded in delivery retrospective during /aod.deliver.

### Resume command

```bash
claude "Resume Feature 250 (adversarial-unit-extraction-hotfix) implementation. Branch: 250-adversarial-unit-extraction-hotfix. Waves 1-6 complete (13/21 tasks). Run /aod.build 250 to continue with Wave 7 (T013 bash 5.x + T014 input-validator deliberate-fault)."
```

When `/aod.build 250` runs in the new conversation, it auto-resumes from Wave 7 by detecting `[X]` checkmarks on T001-T012 + T015 in `tasks.md`.

---

## Context Files

**Required reading on resume** (the new conversation will re-load these):

- `specs/250-adversarial-unit-extraction-hotfix/spec.md` — feature requirements (FR-001..FR-022, SC-001..SC-008)
- `specs/250-adversarial-unit-extraction-hotfix/plan.md` — components, data flow, tech stack
- `specs/250-adversarial-unit-extraction-hotfix/tasks.md` — 21-task breakdown with `[X]` resume markers on T001-T012 + T015
- `specs/250-adversarial-unit-extraction-hotfix/agent-assignments.md` — wave decomposition (Wave 7 next)
- `specs/250-adversarial-unit-extraction-hotfix/quickstart.md` — §4 deliberate-fault matrix procedure (T013 reference)
- `.aod/results/wave-6-t009-deviation-note.md` — T009 timeout deviation context
- `.aod/results/init-sh-invocation-audit-250.md` — FR-014 5-count audit
- `tests/scripts/test_template_substitute_unit.py` — T006 deliverable (8 substitute cases)
- `tests/scripts/test_init_input_unit.py` — T007 deliverable (5 input cases incl. canary)
- `tests/scripts/test_substitute_shim_canary.py` — T015 deliverable (TC-1 closure)
- `tests/scripts/test_init_sh_adversarial.py` — post-T008 state (166 lines, 2 retained tests)

---

## Notes

- The 6 uncommitted entries (2 modified files + 3 new modules + 1 new directory) are intentional artifacts of this build session. The next `/aod.build` invocation will auto-commit them as a checkpoint before resuming Wave 7. Wave 8 / T016 is the official atomic-PR commit (TC-3) that supersedes all chore checkpoints when squash-merged to main.
- TC-3 atomic-PR ordering means Waves 4, 5, 6, 7, and 8 ship together — no intermediate commits between T006/T007/T015 (add) and T008 (delete-block) and T013/T014 (audit) and T016 (commit).
- T013 (Wave 7) requires shell-switch to bash 5.x. The local dev workstation is bash 3.2.57 per T002. Agent MUST use a Linux container / devcontainer / WSL — do NOT silently bypass the bash 5.x requirement; FR-010 / SC-006 audit completeness depends on it.
- T009 deviation: the T009 spec's `--timeout=15` is correct for the 13 new unit tests but inappropriate for the 2 retained integration tests. A future cleanup task may wish to update T009 to use a two-pass invocation. This deviation does NOT block the TC-3 G-6 hard gate — all 15 tests pass; aggregate gate satisfied.
- T007 deviation note: the rejection-class substrings in `INPUT_CASES` are adapted from data-model.md's aspirational labels ("empty"/"multiline"/"disallowed") to the helper's actual emissions ("NUL byte"/"control character"/"over-length"). Per data-model.md §Reason-class authority, this is the correct path. Case IDs were preserved (case_9..case_12) for spec traceability; the test bodies match the helper's real behaviour.
