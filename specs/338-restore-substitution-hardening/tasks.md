---
triad:
  pm_signoff:
    agent: product-manager
    date: 2026-06-29
    status: APPROVED
    notes: "All in-scope FRs map to tasks (FR-001..005→T003-T007, FR-008→T008 audit, FR-009→T004/T005); FR-006/FR-007 cordoned in Phase 2 as landed groundwork (99507b2 = branch tip, do-not-re-task). All SC-001..006 have verifying tasks. US1 fully decomposed (T003∥T004→T005→T006); US2/US3 NOT re-tasked. FR-009 stays surgical (canonical-5-key edits, not whole-file) — hard SC-001/SC-006 dependency, not creep. S-1 deliver gate (T009) + SC-004 scope audit (T008, branch-vs-main-pre-restore; accounts for the on-branch package.json #336 dep-bump delta) both present. No scope creep/gaps. 2 observational/non-gating. No veto. Full: .aod/results/product-manager-tasks.md"
  architect_signoff:
    agent: architect
    date: 2026-06-29
    status: APPROVED
    notes: "Technically correct, executable, faithful to the approved plan. All 7 dimensions PASS, verified live (HEAD 99507b2 vs 5b64f68). Dependency order correct (T001∥T002→T003∥T004→T005→T006→T007∥T008→T009→T010; no cycles). Restore METHOD correct on every axis: OQ-2 direct checkout (0 surviving hardening markers at HEAD = clean generic-revert), OQ-3 FR-009 surgical-not-whole-file, OQ-1 do-not-revert-manifest, MEDIUM-3 do-not-touch-update.sh. OBS-2 discharged: W-1→T007 [MANUAL-ONLY], SC-004→T008 [MANUAL-ONLY] measured branch-vs-main-pre-restore (branch-vs-5b64f68=31 files would falsely flag ~28). bash 3.2.57 boundary respected; [P] markers all disjoint-file valid. 2 non-gating (grep cosmetic; W-1 framing consistent). Full: .aod/results/architect-tasks.md"
  techlead_signoff:
    agent: team-lead
    date: 2026-06-29
    status: APPROVED
    notes: "All 6 dimensions PASS, verified live. Granularity fits an M cut-line-bound restore (10 tasks, no padding). Single-wave / no-cross-agent-parallelism honored; critical path T001/T002→T003∥T004→T005→T006→T007∥T008→T009→T010, [P] intra-wave only. Three carry-forwards encoded: S-1→T009 (no push until green, via devops), W-1→T007, C-2/OQ-3→FR-009/T004 (gate confirmed RED live). S-3 satisfied (99507b2 = tip; FR-006/FR-007 documented DONE, nothing re-tasks them). Assignments feasible/no overload (SBE restore, tester verify, devops deliver; architect discharged at plan). Estimate floor 1/plan 2/ceiling 3 stands. 2 non-gating (OBS-1 route T008 to commit-holder; OBS-2 cosmetic git-describe label mooted by T001). No veto. Full: .aod/results/team-lead-tasks.md"
---

# Tasks: Restore F-248/F-256 Substitution Hardening

**Input**: Design documents from `specs/338-restore-substitution-hardening/`
**Prerequisites**: plan.md (PM+Architect approved), spec.md (PM approved), research.md, quickstart.md
**Feature**: #338 · BLP-06 Wave 2, F-2 · Branch `338-restore-substitution-hardening`

**Tests**: NOT authored here. The F-248/F-256 behavioral suite (`tests/scripts/`) **already exists** and is the
acceptance oracle — running it is T006, not writing it. No TDD test-authoring tasks (restoration of tested code).

> **Definition of Done** (constitution VII):
> 1. ✅ Pushed to Production — restore merged to `main` (post-green, via devops).
> 2. ✅ Tested — F-248/F-256 gated suite green on **both** matrix legs.
> 3. ✅ User Validated — confirmation diff vs `5b64f68` + canary (`AT&T→AT&T`); adopter scaffolds hardened from `main`.

<!-- DOD-ACK -->

## Format: `[ID] [P?] [Story] Description`
- **[P]**: Can run in parallel (different files, no dependencies)
- Include exact file paths in descriptions

## Path Conventions
Single project (CLI/tooling). Restore surface at repo root: `scripts/`, `.aod/scripts/bash/`, `stacks/*/defaults.env`. Tests at `tests/scripts/`.

---

## Phase 1: Setup

**Purpose**: Confirm restore preconditions before touching the tree.

- [X] T001 [P] Confirm restore preconditions in repo root: on branch `338-restore-substitution-hardening`; `git cat-file -e 5b64f68^{commit}` (reachable); branch tip is `99507b2` (groundwork present). **Authoritative SHA-content check** (moots the cosmetic git-describe label discrepancy, PM MINOR-1): `git show 5b64f68:.aod/scripts/bash/template-substitute.sh | grep -c patsub_replacement` == 5 and `git show 5b64f68:.aod/scripts/bash/template-git.sh | grep -c AOD_FETCH_TIMEOUT` == 3.
- [X] T002 [P] Install test deps for local verification: `python -m pip install 'pytest>=8' 'pytest-timeout>=2' 'pyyaml>=6'` (matches `.github/workflows/tachi-pytest.yml`).

---

## Phase 2: Foundational (completed dependencies — NOT re-tasked)

**Purpose**: Document the landed groundwork. No tasks here — this is a callout (team-lead S-3).

- **FR-006** (`push:[main]` gate on `.github/workflows/tachi-pytest.yml`, single `*hardening_paths` anchor) — ✅ landed in `99507b2`. US2 DONE.
- **FR-007** (`test_personalized_tree_bytes_match_baseline` xfail `strict=False` with #329 reason) — ✅ landed in `99507b2`. US3 DONE.
- No new blocking prerequisites. **Do NOT re-implement or re-task FR-006/FR-007.**

**Checkpoint**: groundwork verified present (T001) → US1 restore can begin.

---

## Phase 3: User Story 1 — Restore the lost hardening to `main` (Priority: P1) — MVP & only remaining story

**Goal**: Restore the F-248/F-256 hardening + the canonical `defaults.env` key surface so `main` behaves exactly as v4.44.0 (`5b64f68`): `&`-bearing values stay literal, malicious `defaults.env` is rejected, clone fetch is time-bounded, and all 5 shipped packs load cleanly under the restored whitelist loader.

**Independent Test**: F-248/F-256 gated suite green on both matrix legs (macOS bash 3.2.57 + ubuntu bash 5.x) + canary `AT&T→AT&T` + confirmation diff vs `5b64f68`.

### Implementation for User Story 1

- [X] T003 [P] [US1] Restore the three file bodies (clean generic-revert, FR-001..004): `git checkout 5b64f68 -- scripts/init.sh .aod/scripts/bash/template-substitute.sh .aod/scripts/bash/template-git.sh`. Direct restore of whole bodies, NOT a 3-way merge (OQ-2 ratified).
- [X] T004 [P] [US1] Restore the canonical `defaults.env` key surface (FR-009 — OQ-3) via **surgical key edits, NOT whole-file checkout**: add `TECH_STACK="<pack>"` to all five packs — `stacks/nextjs-supabase/defaults.env`→`nextjs`, `stacks/fastapi-react/defaults.env`→`fastapi-react`, `stacks/fastapi-react-local/defaults.env`→`fastapi-react-local`, `stacks/swiftui-cloudkit/defaults.env`→`swiftui-cloudkit`, `stacks/knowledge-system/defaults.env`→`knowledge-system` — AND remove the disallowed `ORCHESTRATION_TARGET` line from `stacks/knowledge-system/defaults.env`. (T003 ∥ T004: disjoint files.)
- [X] T005 [US1] Verify the restore in the working tree (depends on T003, T004) per `quickstart.md` steps 1-2: hardening markers present (`patsub_replacement` in `template-substitute.sh`, `AOD_FETCH_TIMEOUT` in `template-git.sh`, `STACK_PACK_ALLOWED_KEYS` in `scripts/init.sh`); each `stacks/*/defaults.env` key set **exactly equals** the canonical 5 (`TECH_STACK, TECH_STACK_DATABASE, TECH_STACK_VECTOR, TECH_STACK_AUTH, CLOUD_PROVIDER`).
- [X] T006 [US1] Run the F-248/F-256 gated suite locally (depends on T005): `python -m pytest tests/scripts/ -v --timeout=1080`. Confirm green: `test_substitute_shim_canary.py` (`AT&T→AT&T`, SC-002), `test_init_sh_defaults_env.py` (5/5 packs exit 0, SC-006), `test_template_git_clone_timeout.py`, `test_init_sh_substitution.py`/`test_init_sh_adversarial.py`; `test_personalized_tree_bytes_match_baseline` is **xfail** (FR-007, expected). CI runs **both** matrix legs — both must be green for SC-001.

**Checkpoint**: US1 functionally complete — hardening restored, gated suite green locally.

---

## Phase 4: Acceptance Verification & Deliver Gate (cross-cutting)

**Purpose**: Close the parity-oracle gap, audit scope discipline, and gate delivery (architect OBS-2; team-lead S-1).

- [X] T007 [P] W-1 byte spot-check (FR-005 / SC-005 / architect OBS-2; depends on T006): `git diff 5b64f68 -- scripts/init.sh .aod/scripts/bash/template-substitute.sh .aod/scripts/bash/template-git.sh` — confirm the three restored bodies are byte-identical to `5b64f68` (clean checkout ⇒ empty diff; any delta must be the generic→hardened direction only). Closes the gap the xfail'd byte-identity baseline left. **[MANUAL-ONLY]** diff-direction review (no automated assertion covers the xfail'd byte surface).
- [X] T008 [P] SC-004 scope-fence audit (architect OBS-2; depends on T006): confirm the restore commit's diff (measured **branch-vs-`main`-pre-restore**, NOT vs `5b64f68`) touches ONLY the 8 in-scope paths (3 scripts + 5 `defaults.env`); confirm every other branch delta (`scripts/update.sh`, `.aod/template-manifest.txt`, docs/devops, etc.) is named in FR-008. **[MANUAL-ONLY]** scope-fence audit against FR-008. Target: 0 unaccounted out-of-scope files in the restore commit.
- [X] T009 Deliver gate S-1 (constitution VII / git-workflow; depends on T006, T007, T008): **do NOT `git push` the branch or open/ready the PR until T006 is green locally** (the FR-006 `push:[main]` gate would otherwise redden `main`). Then merge to `main` through **devops** with a Conventional-Commit PR title — `fix(338): restore F-248/F-256 substitution hardening` (release-triggering). ✅ DONE: branch pushed post-green, PR #340 opened; CI both legs green (macOS bash 3.2.57 + ubuntu bash 5.x, run `28455027920`) — the devops verification gate — then squash-merged to `main` as `6fbce10`. (Branch was first merged up to `origin/main` to clear conflicts in 3 non-hardening metadata files; hardening surface re-proven byte-identical to `5b64f68`.)
- [X] T010 Post-merge release verification (depends on T009): confirm a release-please PR opened within ~30s of the squash-merge (`gh pr list --state open --search "release-please" --limit 3`); if empty, push an empty `fix(338): restore F-248/F-256 hardening — release marker` commit (AOD deliver-release gate). ✅ DONE: release-please PR #341 (`chore(main): release 4.45.1`) opened — captures `**338:** restore F-248/F-256 substitution hardening (#340)`. No marker commit needed.

---

## Dependencies & Execution Order

### Phase Dependencies
- **Setup (Phase 1)**: no dependencies — T001, T002 can start immediately (both [P]).
- **Foundational (Phase 2)**: completed groundwork (FR-006/FR-007 in `99507b2`); no work, no blocking.
- **US1 (Phase 3)**: starts after Setup. T003 ∥ T004 → T005 → T006.
- **Acceptance & Deliver (Phase 4)**: after T006. T007 ∥ T008 → T009 → T010.

### Within User Story 1
- T003 (scripts/libs) ∥ T004 (defaults.env) — disjoint files, parallelizable.
- T005 depends on both T003 and T004 (verifies the combined restored state).
- T006 depends on T005 (run the suite against the verified restore).

### Parallel Opportunities
- Setup: T001 ∥ T002.
- US1: T003 ∥ T004.
- Acceptance: T007 ∥ T008.
- **No cross-agent wave parallelism** (team-lead): single shared-context reconciliation against one CI oracle — one wave, one primary implementer. The [P] markers above are intra-wave, disjoint-file parallelism only.

---

## Parallel Example: User Story 1

```bash
# T003 and T004 touch disjoint files — run together:
Task: "Restore 3 file bodies: git checkout 5b64f68 -- scripts/init.sh .aod/scripts/bash/template-substitute.sh .aod/scripts/bash/template-git.sh"
Task: "Restore canonical defaults.env key surface (FR-009): add TECH_STACK to 5 packs + remove ORCHESTRATION_TARGET from knowledge-system"
```

---

## Implementation Strategy

### MVP = the whole feature (User Story 1)
1. Phase 1: Setup (confirm preconditions, deps).
2. Phase 3: US1 — restore 3 bodies (T003) ∥ restore keys (T004) → verify (T005) → suite green (T006).
3. **STOP & VALIDATE**: gated suite green both legs + canary + confirmation diff.
4. Phase 4: byte spot-check (T007) ∥ scope audit (T008) → S-1 deliver gate (T009) → release verify (T010).

US2 + US3 are already delivered (`99507b2`); no incremental stories remain. Single Plan→Build→Deliver cycle; do not split.

---

## Notes
- [P] = different files, no dependencies (intra-wave only here).
- Tests pre-exist (`tests/scripts/`) — T006 runs them; no test authoring.
- Restore source-of-truth is the **SHA `5b64f68`** (authoritative; tag-label provenance is cosmetic — T001 verifies content).
- FR-009 is surgical key edits, NOT a whole-file `defaults.env` checkout (those files carry FR-008-fenced non-key content).
- Do NOT revert `.aod/template-manifest.txt` (more hardened at HEAD) or touch `scripts/update.sh` (not a hardening surface).
- Commit after the restore is verified; honor S-1 (no push until green).
