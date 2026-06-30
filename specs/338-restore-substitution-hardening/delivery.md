# Delivery Document: Feature 338 — Restore F-248/F-256 Substitution Hardening

**Delivery Date**: 2026-06-30
**Branch**: `338-restore-substitution-hardening`
**PR**: #340 (squash-merged to `main` as `6fbce10`; released v4.45.1 via release-please #341)

---

## What Was Delivered

- **Restored the F-248 `patsub_replacement` shim** (`.aod/scripts/bash/template-substitute.sh`) — `&`-bearing values (`AT&T`, `R&D`) stay literal on bash 5.2+ instead of corrupting to `AT{{PROJECT_NAME}}T`.
- **Restored the F-248 substitution path + F-256 Site A whitelist loader** (`scripts/init.sh`) — parameter-expansion + input-validation substitution (not `sed`), and `aod_template_load_kv_file … STACK_PACK_ALLOWED_KEYS` (not a plain `source defaults.env`), so a malicious `defaults.env` is rejected (exit 8) instead of executed.
- **Restored the F-256 `AOD_FETCH_TIMEOUT` clone watchdog** (`.aod/scripts/bash/template-git.sh`) — a hung template upstream can no longer block `init` forever.
- **Restored the canonical 5-key `defaults.env` surface** across all 5 shipped packs (`TECH_STACK` added to each; disallowed `ORCHESTRATION_TARGET` removed from `knowledge-system`) so the restored whitelist loader accepts them (FR-009 / OQ-3).
- All three script bodies are **byte-identical to last-good v4.44.0 (`5b64f68`)** — a clean generic-revert, confirmed by an empty `git diff`.
- **Standing guardrail** (groundwork `99507b2`): `tachi-pytest.yml` now gates `push:[main]` (not only `pull_request`) via a shared `&hardening_paths` anchor (FR-006), so a future direct-to-`main` clobber reddens CI immediately; the pre-existing `#329` baseline-staleness test is quarantined `xfail` (FR-007).

---

## How to See & Test

1. **Confirm the shim is on `main`**: `grep patsub_replacement .aod/scripts/bash/template-substitute.sh` → present (5 hits).
2. **Confirm the watchdog is on `main`**: `grep AOD_FETCH_TIMEOUT .aod/scripts/bash/template-git.sh` → present (3 hits).
3. **Confirm byte-parity to v4.44.0**: `git diff 5b64f68 -- scripts/init.sh .aod/scripts/bash/template-substitute.sh .aod/scripts/bash/template-git.sh` → empty.
4. **Run the gated suite**: `python -m pytest tests/scripts/ -v --timeout=1080` → canary `AT&T→AT&T` passes, malicious-pack rejected (no `/tmp/...`), missing-key rejected, clone-timeout bounded; `test_personalized_tree_bytes_match_baseline` is `xfail` (FR-007).
5. **Confirm the CI gate fires on push**: inspect `.github/workflows/tachi-pytest.yml` — `push: branches:[main]` shares the `pull_request` `paths` anchor (`*hardening_paths`).
6. **Confirm both matrix legs green**: CI run `28455027920` — `pytest init.sh suite — macos-latest` ✅ and `— ubuntu-latest` ✅.

---

## Delivery Metrics

| Metric | Value |
|--------|-------|
| Estimated Duration | 1–2 days (feasibility: floor 1 / planning 2 / ceiling 3 eng-days) |
| Actual Duration | ~1 day (first commit 2026-06-29 10:23 → squash-merge 2026-06-30 11:38) |
| Variance | Under / on-target — landed at the optimistic floor (clean generic-revert, `defaults.env` gate resolved RED→fixed in 1 line/pack, CI green first try) |

---

## Surprise Log

The regression this feature *restores* nearly re-occurred **at deliver time**: the long-lived restore branch had fallen behind a fast-moving `main` (PR `CONFLICTING`, blocking CI), and local `main` carried a stale, **unpushed `/aod.update` clobber** (`ad390f8`) — the exact direct-to-`main` revert class #338 fixes. A deliver-stage docs push from that diverged local `main` would have re-clobbered the just-restored hardening. The merge conflicts were confined to 3 non-hardening metadata files, so the hardening surface stayed provably byte-identical to `5b64f68`; the `git reset --hard` guard forced a loss-proof realignment (`origin/main` already contained `ad390f8`'s content).

---

## Lessons Learned

| Category | Lesson | KB Entry |
|----------|--------|----------|
| Process | The regression you are restoring can re-occur AT DELIVER — verify the feature branch is current with `origin/main` and local `main` == `origin/main` before any merge or direct-to-`main` push; keep the hardening surface a byte-identical generic-revert so conflicts stay confined to metadata and a one-line `git diff <SHA>` is the standing parity oracle. | Entry 18 in INSTITUTIONAL_KNOWLEDGE.md |

---

## Feedback Loop

**New Ideas**: 1

- Deliver-stage preflight: guard against stale/diverged local `main` and behind-`main` feature branch before any merge or direct-to-`main` push — Issue #342 (type:retro)

---

## Source Artifacts

| Artifact | Path |
|----------|------|
| Specification | specs/338-restore-substitution-hardening/spec.md |
| Implementation Plan | specs/338-restore-substitution-hardening/plan.md |
| Task Breakdown | specs/338-restore-substitution-hardening/tasks.md |
| PRD | docs/product/02_PRD/338-restore-substitution-hardening-2026-06-29.md |

---

## Test Evidence

### Test Scenarios (Living Documentation)

| AC ID | Given/When/Then | Scenario(s) | Status |
|-------|-----------------|-------------|--------|
| US1-AC1 | shim present in `template-substitute.sh` | `test_substitute_shim_canary.py` | Covered |
| US1-AC2 | `AT&T` value substitutes literally on bash 5.2+ | `test_substitute_shim_canary.py` (`AT&T→AT&T`) | Covered |
| US1-AC4 | malicious `defaults.env` rejected (exit 8) | `test_init_sh_defaults_env.py` / `test_init_sh_adversarial.py` | Covered |
| US1-AC5 | clone watchdog bounds an unresponsive upstream | `test_template_git_clone_timeout.py` | Covered |
| US1-AC6 | 5/5 packs load clean under restored loader | `test_init_sh_defaults_env.py` | Covered |
| US1-AC7 | both matrix legs green | CI `tachi-pytest` (macOS bash 3.2.57 + ubuntu bash 5.x) | Covered |
| FR-004/005 (byte parity) | restored bodies == `5b64f68` | `[MANUAL-ONLY]` confirmation diff (empty) — T007 | Manual |

### Execution Evidence

#### E2E Validation Gate

| Field | Value |
|-------|-------|
| Status | N/A (skipped — no E2E contract) |
| Gate Mode | n/a |
| Gate Result | skip |
| Tests Passed | N/A |
| Tests Failed | N/A |
| Tests Skipped | N/A |

**Failure Details**: N/A — the active stack pack (`knowledge-system`) declares no `aod-test-contract` block in `STACK.md` (`stack-contract-lint.sh` exit 5); this is a CLI/bash-tooling restore with no Playwright/E2E surface. Behavioral validation is the F-248/F-256 pytest suite below.

#### Build-Wave Test Results

| Wave | Tests | Passed | Failed | Status |
|------|-------|--------|--------|--------|
| wave-1 | 144 | 143 | 0 | pass |

**Build Summary**: pass — 143/144 passed (1 skip = `test_init_precommit_matrix` Case 4 TTY pty sim; 1 xfail = `test_personalized_tree_bytes_match_baseline`, FR-007 / #329). 0 regressions. CI-gated 15-module F-248/F-256 subset (`tachi-pytest.yml`), macOS bash 3.2.57 leg locally + both legs green in CI run `28455027920`.

#### Artifacts

| Artifact | Path | Summary |
|----------|------|---------|
| Build-wave summary | specs/338-restore-substitution-hardening/test-results/summary.json | 143 pass / 0 fail / 1 skip; gate pass |
| Wave-01 results | specs/338-restore-substitution-hardening/test-results/wave-01/results.json | 143 pass / 0 fail / 1 skip / 1 xfail; 0 regressions |
| Security scan | specs/338-restore-substitution-hardening/security-scan.md | PASSED — 0 findings (SAST 2 files, SCA 1 manifest) |

**Archived Artifact Metrics**:
- Tests Run: 144
- Passed: 143
- Failed: 0
- Coverage: N/A (bash/CLI suite)

**Notes**: Behavioral parity validated via the F-248/F-256 pytest suite; byte-parity validated via the FR-004 confirmation diff vs `5b64f68` (`[MANUAL-ONLY]`). Security scan PASSED (0 findings). Economy gate PASSED (pure restore — no new code/deps).

### Manual Validation

**Manual-only acceptance criteria** (carried from `spec.md`):

- FR-004 / FR-005: [MANUAL-ONLY] byte-for-byte confirmation diff of the three restored bodies vs `5b64f68` (empty diff confirmed at T007; the byte-identity baseline test is `xfail` under #329, so green CI alone does not prove byte parity).
- SC-004: [MANUAL-ONLY] scope-fence audit — the restore commit touched only the 8 in-scope paths; all other branch deltas are FR-008-named (T008).

---

## Documentation Updates

| Domain | Agent | Files Updated | Status |
|--------|-------|---------------|--------|
| Product | product-manager | 0 (no-op — INDEX.md already current; STATUS/completed-features do not exist in this project; BACKLOG is auto-generated) | APPROVED |
| Architecture | architect | 2 (ADR-038 + ADR-040 Revision-History notes: restored via #338, durability via push:[main] gate) | APPROVED |
| DevOps | devops | 2 (CI_CD_GUIDE.md new "Tachi Pytest Workflow" section; environment-variables.md cross-ref) | APPROVED |

PRD INDEX.md 338→Delivered row + narrative was spliced by the deliver orchestrator (merge-aware, preserving the #333 row).

---

## Cleanup

- [x] Feature branch deleted (local + remote)
- [x] All tasks complete (T001–T010)
- [x] No TBD/TODO in docs
- [x] Committed and pushed
- [x] GitHub Issue closed (`stage:done`)

**Feature 338 is now officially CLOSED.**
