---
triad:
  pm_signoff:
    agent: product-manager
    date: 2026-05-10
    status: APPROVED
    notes: "All 6 user stories (US-1 through US-6) addressed across task phases; no scope creep — every task maps to a spec FR or carry-forward concern; Wave 1→5 dependency ordering preserved per plan §Wave-Sequencing; all 7 carry-forward concerns reflected in specific tasks (Architect CONCERN-1 → T013 co-located runner; CONCERN-2 → T014/T014a pytest matrix + workflow lock-step; CONCERN-3 → T016 version check + T022 floor justification; CONCERN-4 → T033 post-merge maintenance Issue; PM-PLAN-1 → T009 fixture rule-ID assertion comments; PM-PLAN-2 → T022 §Re-init-Behavior flag-first-run-only clarification; PM-PLAN-3 → T011 fixture #14 schema-out-of-scope header); PM-3 consolidation correctly captured at T005 (single FR-008+FR-009 task family). Carry-forward traceability table at §Phase-10 confirms all 8 mappings explicit. Full review: .aod/results/product-manager-tasks-282.md."
  architect_signoff:
    agent: architect
    date: 2026-05-10
    status: APPROVED
    notes: "All 9/9 evaluation criteria PASS: Wave 1→5 dependency soundness verified; Pre-Mortem FM-5 wrapper exit-code-capture pattern explicit at T005; F-256 lock-step pattern explicit at T014a (tachi-pytest.yml paths: + invocation lock-step); CI parity workflow technically correct at T027 (gitleaks binary direct, NOT proprietary action; SARIF upload; checksum verification; full-repo Q5 scan); all 4 carry-forward CONCERNs mapped to specific tasks per traceability table; parallel opportunities correctly marked with [P] for file-disjoint tasks; critical path identified in §Dependencies-Execution-Order; init.sh insertion point at line 177-185 region per T015; ADR-042 trufflehog runtime correction (Go not Python) explicit at T023. Zero concerns. Full review: .aod/results/architect-tasks-282.md."
  techlead_signoff:
    agent: team-lead
    date: 2026-05-10
    status: APPROVED_WITH_CONCERNS
    notes: "Granularity proportional to F-5 scope (37 tasks for 12-15h envelope vs F-3's 30 / F-4's 30 — F-5 +7 over precedents justified by 16 fixtures + 1 test runner + 1 pytest test + 1 wrapper + 1 TOML config unique to F-5). Critical path tight; parallelism appropriately marked. All 4 architect carry-forward CONCERNs + 3 PM-PLAN concerns + PM-3 consolidation explicitly addressed in specific tasks; traceability table at §Phase-10 is exemplary. Capacity: single-maintainer Saturday 2026-05-10 + slack 2026-05-11 viable. 6 Pre-Mortem failure modes + 4 non-blocking recommendations logged (all execution-calibration, no tasks.md revision required): bash quoting around T005 wrapper stderr augmentation could need 60-min spike budget (FM-5 vulnerable surface); T014 pytest matrix 6 cases × ~5-15min runtime via run_init_in_clone(timeout_sec=900) may need pytest.mark.slow; T022 §Known-Limitations now carries 7 explicit items (CONCERN-3 + PM-PLAN-2 + original 5) — section LOC budget ~30 LOC recommended; T029 pre-merge verification reviewer cross-check on AC-10 catalog parity may underrun 30-min budget. Envelope-hit probability material downward revision from PRD: ~60% for 9-13h Phase 2 envelope (PRD A-1 said ~70%); ~75% for 12-15h tasks.md envelope (with slack); ~70% for 2026-05-10 wall-clock with 2026-05-11 slack (PRD A-5 said ~80%). Reasoning: carry-forward concerns inflated envelope by ~1-2h vs PRD baseline — T014a workflow lock-step (~30 min), T016 version check (~30 min), T022 §Known-Limitations expansion (~30 min), T009 fixture header comments (~10 min). Recommend proceed to /aod.build 282 with 2026-05-11 slack already booked. Full review: .aod/results/team-lead-tasks-282.md."
---

# Tasks: Pre-commit Secret-Scanning Defaults (F-5)

**Input**: Design documents from `/specs/282-pre-commit-secret-scanning-defaults/`
**Feature Branch**: `282-pre-commit-secret-scanning-defaults`
**Issue**: [#282](https://github.com/davidmatousek/tachi/issues/282)
**Initiative**: BLP-02 Wave 4+ — fifth and final feature in the 5-feature enterprise hardening initiative
**Tests**: REQUIRED per AC-SPEC-1 entry-criteria + Pre-Mortem FM-3 design consideration. AC-SPEC-1 synthetic-fixture rule-interaction test (16 fixtures + runner) and init.sh prompt-flag matrix test (6 cases) are mandatory deliverables.

**Organization**: Tasks are grouped into 5 build waves matching plan.md §Wave-Sequencing (Wave 1 foundation → Wave 2 verification → Wave 3 init.sh + CI → Wave 4 docs + ADR → Wave 5 delivery + verification).

## Format: `[ID] [P?] [Story] Description`
- **[P]**: Can run in parallel (different files, no dependencies on incomplete tasks)
- **[Story]**: User story label (US1-US6) for user-story phases; Setup/Foundational/Polish phases have NO story label
- File paths are absolute or repo-root-relative

## Path Conventions
- All file paths are relative to repo root `/Users/david/Projects/tachi/`
- Single-project layout (no frontend/backend split)
- Task identifiers T001-T036 in execution order

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Branch + draft PR scaffolding (already partially complete from /aod.plan kickoff)

- [X] T001 Verify feature branch `282-pre-commit-secret-scanning-defaults` is current per `git branch --show-current`; rebase on `main` if upstream changed since /aod.plan kickoff
- [X] T002 Create draft PR with title `feat(282): pre-commit secret-scanning defaults` via `gh pr create --draft --title "feat(282): pre-commit secret-scanning defaults" --body "..."` (per `.claude/rules/git-workflow.md` §Conventional-Commit-PR-Titles); include PRD + spec + plan links in body

---

## Phase 2: Foundational — Wave 1 (Foundation: Pre-commit Hook Surface)

**Purpose**: Ship the hook + ruleset + wrapper so subsequent waves can verify them

**CRITICAL**: All Wave 2 verification depends on these files existing with finalized rules + allow-list shape.

- [X] T003 [P] Create `.gitleaks.toml` at repo root (~50-80 LOC) with: (a) `[extend] useDefault = true` clause, (b) `[[allowlists]]` array of tables (gitleaks v8.25.0+ schema) for env-var placeholders (`\$[A-Z_]+`, `<placeholder>`, `PLACEHOLDER`, `your-api-key-here`, `sk-PLACEHOLDER...`, `sk-test-...`), fixture/docs/example paths (`tests/fixtures/`, `examples/`, `docs/`), `.aod/personalization.env.example` path, (c) two `[[rules]]` entries `tachi-personalization-env` (warn-only severity per Q1; regex matching populated AOD_PERSONALIZATION_* vars without placeholders) and `tachi-security-exceptions-jsonl` (warn-only per Q2; regex detecting manual edits to `.security/exceptions.jsonl`), (d) excluded paths (`node_modules/`, `.git/`, `archive/`). Each entry MUST have inline comments explaining rationale.
- [X] T004 [P] Create `.aod/personalization.env.example` at repo root (~10-20 LOC) with header comment instructing users to copy to `.aod/personalization.env`, all keys documented in `scripts/init.sh` (AOD_PERSONALIZATION_PROJECT_NAME, AOD_PERSONALIZATION_STACK_PACK, AOD_PERSONALIZATION_BRAND_NAME, plus any others init.sh expects), and placeholder values (NO real credentials). Path MUST be in `.gitleaks.toml` allow-list per T003.
- [X] T005 [P] Create `.aod/scripts/bash/precommit-wrap.sh` (~30-60 LOC) following `.aod/scripts/bash/` conventions: `#!/usr/bin/env bash` shebang; explicit `set -e` discipline OR explicit error handling per init-input.sh precedent; invoke `gitleaks git --staged --config=.gitleaks.toml` (or current CLI shape verified at task time); capture exit code BEFORE stderr augmentation per Pre-Mortem FM-5 pattern (`gitleaks ...; rc=$?; { stderr augmentation; } >&2; exit $rc`); on rc != 0, emit four-item structured stderr (rule ID + file:line — already in gitleaks default output; `SKIP=gitleaks git commit ...` bypass guidance; `See docs/standards/PRECOMMIT_HOOKS.md` docs link); preserve gitleaks' exit code via `exit $rc`. **Note** (per PM-3 consolidation): this single task family covers both FR-008 (wrapper script) AND FR-009 (refused-commit error contract) — they describe the same mechanism.
- [X] T006 Create `.pre-commit-config.yaml` at repo root (~30-50 LOC) referencing `https://github.com/gitleaks/gitleaks` repo with `rev:` set to a tag (initial value `v8.30.1`); after first install, run `pre-commit autoupdate --freeze` to convert tag to pinned commit SHA in-place. Hook entry invokes `.aod/scripts/bash/precommit-wrap.sh` from T005. `stages: [pre-commit]`. Depends on T005 (wrapper must exist).
- [X] T007 Verify Wave 1 surface manually: run `pre-commit install` from a clean clone state; stage a deliberately-fake credential (`echo "ghp_$(openssl rand -hex 20)" > /tmp/test-cred && cp /tmp/test-cred test.txt && git add test.txt`); run `git commit -m "wave1-smoke"`; confirm commit refused with all four stderr items (rule ID + file:line + bypass + docs link); cleanup `git reset HEAD test.txt && rm test.txt /tmp/test-cred`. Depends on T003-T006.

**Checkpoint**: Pre-commit hook is installable and functionally fires the wrapper-augmented stderr message. Wave 2 can begin.

---

## Phase 3: User Story 1 — First-time adopter accidentally committing a credential (Priority: P1) — MVP

**Goal**: First-time adopters running init.sh and accepting the prompt have a working pre-commit secret-scanning hook installed and active that refuses bad credentials with the four-item structured stderr error.

**Independent Test**: From a fresh tachi clone, run `init.sh` accepting prompt default Y, attempt to commit a known-bad fixture, observe commit blocked with rule ID + file:line + bypass guidance + docs link.

### Tests for User Story 1 (REQUIRED — AC-SPEC-1 entry-criteria + FM-3 matrix)

> Wave 2 verification surface. AC-SPEC-1 synthetic-fixture rule-interaction test is the preventive false-positive verification per Architect C-4.

- [X] T008 [P] [US1] Create fixture directory `tests/fixtures/gitleaks-rule-interaction/` with 4 subdirectories: `staged-credential/`, `placeholder/`, `path-allow-listed/`, `path-excluded/`. Each subdirectory uses one fixture file per case.
- [X] T009 [P] [US1] Create 6 should-fire fixtures under `tests/fixtures/gitleaks-rule-interaction/staged-credential/`: `github-pat.txt` (`ghp_` + 36 hex), `aws-access-key.txt` (`AKIA` + 16 alphanumeric), `openai-key.txt` (`sk-` + 48 alphanumeric), `anthropic-key.txt` (`sk-ant-` + random), `private-key-block.pem` (PEM block), `personalization-env-populated.env` (non-placeholder AOD_PERSONALIZATION_*). Each fixture MUST include a header comment naming the **expected** gitleaks rule ID as of v8.30.1 (per PM-PLAN-1 carry-forward) so future maintainers can update assertions if upstream renames a rule.
- [X] T010 [P] [US1] Create 4 should-NOT-fire placeholder fixtures under `tests/fixtures/gitleaks-rule-interaction/placeholder/`: `env-var-reference.txt` (`password = "$ENV_VAR"`), `openai-placeholder.env` (`OPENAI_API_KEY=PLACEHOLDER`), `sk-placeholder.env` (`OPENAI_API_KEY=sk-PLACEHOLDER...`), `sk-test-stripe.env` (`STRIPE_KEY=sk-test-...`). Each fixture MUST include a header comment naming the allow-list mechanism that protects it.
- [X] T011 [P] [US1] Create 4 should-NOT-fire path-allow-listed fixtures under `tests/fixtures/gitleaks-rule-interaction/path-allow-listed/`: `personalization-env-example` (duplicate of `.aod/personalization.env.example`), `tests-fixtures-fake-aws.txt` (under tests/fixtures/), `docs-placeholder.md` (under docs/), `security-exceptions-jsonl-auto.jsonl` (auto-generated marker). The fixture #14 file (`security-exceptions-jsonl-auto.jsonl`) MUST include a header comment per PM-PLAN-3: "This fixture verifies gitleaks rule interaction only — schema alignment with `.security/exceptions.jsonl` is NOT verified here. See F-260/F-260b for schema specs."
- [X] T012 [P] [US1] Create 2 should-NOT-fire excluded-path fixtures under `tests/fixtures/gitleaks-rule-interaction/path-excluded/`: `node-modules-credential.txt` (under node_modules/-equivalent path), `archive-credential.txt` (under archive/-equivalent path). Note: these fixtures are STILL placed UNDER `tests/fixtures/gitleaks-rule-interaction/path-excluded/` for collection convenience, but the test harness MUST simulate scanning them as if they were under `node_modules/` / `archive/` (e.g., copy to a temp location with the matching path prefix before invoking gitleaks).
- [X] T013 [US1] Create test runner `tests/fixtures/gitleaks-rule-interaction/run.sh` (~30-50 LOC) per Architect CONCERN-1 (HIGH) — co-located with fixtures, NOT under `tests/scripts/` (which is pytest-only territory). Runner: iterate over 4 subdirectories; determine expected outcome from subdirectory; for `path-excluded/` cases, copy fixture to a temp path under simulated `node_modules/` / `archive/` before invoking gitleaks; invoke `gitleaks detect --no-git --source=<path> --config=.gitleaks.toml --report-format=json --report-path=/tmp/gitleaks-result.json`; compare exit code + JSON findings against expectation; emit pass/fail per fixture; exit 1 if any fail; exit 0 if all pass. `#!/usr/bin/env bash` shebang; stderr `>&2`; exit codes 0/1. Depends on T008-T012.
- [X] T014 [P] [US1] Create init.sh prompt-flag matrix pytest test at `tests/scripts/test_init_precommit_matrix.py` per Architect CONCERN-2 (MEDIUM) — pytest convention, NOT bash. Leverage existing `init_sh_helpers.py` `run_init_in_clone(timeout_sec=900)` session-scoped fixture. 6 matrix cases per plan §Phase-1 §6: `[TTY/no-TTY] × [no-flag/--no-precommit/--precommit]`. Each test asserts: prompt fired/skipped + `pre-commit install` invoked/not. Depends on T015 (init.sh delta) for the flag handling under test, but the test file itself can be authored in parallel.
- [X] T014a [US1] Update `.github/workflows/tachi-pytest.yml` `paths:` filter to include `tests/scripts/test_init_precommit_matrix.py` AND extend the pytest invocation block (lines 164-175 region) to include the new test file. Per F-256 lock-step lesson (KB Entry 3): adding a new test file requires updating both `paths:` AND invocation in the same commit. Depends on T014.

### Implementation for User Story 1

- [X] T015 [US1] Modify `scripts/init.sh` (~10-20 LOC delta) — insert opt-in prompt block after personalization-confirmation block (line 177-185 region per research). Block structure: (a) parse `--no-precommit` and `--precommit` flags from `$@` at script start (early exit/skip variables), (b) `[ -t 0 ]` TTY check, (c) raw `read -p "Install pre-commit secret-scanning hook (gitleaks)? [Y/n] " response` with `${response:-Y}` default-Y fallback, (d) on Y match (`[[ "${response:-Y}" =~ ^[Yy]$ ]]`), invoke `pre-commit install || echo "WARN: pre-commit install failed; install pre-commit framework manually and run 'pre-commit install'" >&2`, (e) flag overrides: `--no-precommit` skips prompt + skip install regardless of TTY; `--precommit` skips prompt + force-install regardless of TTY. Use raw `read -p` per Q10 (waiver in ADR-042 §Consequences).
- [X] T016 [US1] Add `pre-commit --version` floor check to init.sh per Architect CONCERN-3 (MEDIUM): before invoking `pre-commit install` in T015, check `pre-commit --version` output parses to >= 3.5.0; if `pre-commit` command is missing or returns lower version, log a one-line WARN to stderr (`WARN: pre-commit framework version < 3.5.0 detected; minimum supported is 3.5.0; please upgrade via `pip install --upgrade pre-commit` or `brew upgrade pre-commit``) and continue without installing. Depends on T015.
- [X] T017 [US1] Verify FR-004 acceptance scenarios empirically per AC-6 + AC-7: (a) TTY no-flag default-Y → `pre-commit install` invoked; (b) `</dev/null` non-TTY → prompt skipped; (c) TTY `--no-precommit` → prompt skipped; (d) `--precommit </dev/null` → install invoked without prompting; (e) `pre-commit` missing → WARN logged, init.sh continues. Use a fresh tachi clone for each scenario. Depends on T015 + T016.

**Checkpoint**: User Story 1 fully functional. Hook installed via init.sh prompt; refusal contract verified end-to-end. Wave 1 + Wave 2 + Wave 3 (init.sh delta) all consumed.

---

## Phase 4: User Story 2 — Default-deny inheritance (Priority: P1)

**Goal**: Adopters get gitleaks' canonical credential patterns (AWS access keys, GitHub PATs, OpenAI/Anthropic API keys, generic high-entropy) caught without modifying `.gitleaks.toml`.

**Independent Test**: Without modifying `.gitleaks.toml`, stage files containing each canonical credential pattern; verify each fires the appropriate rule. Subsumed under T009 (fixtures #1-#5 each cover one canonical pattern); T013 runner asserts.

### Implementation for User Story 2

- [X] T018 [US2] Verify FR-002 acceptance scenarios via T013 runner: run `bash tests/fixtures/gitleaks-rule-interaction/run.sh`; confirm fixtures #1 (GitHub PAT) + #2 (AWS access key) + #3 (OpenAI key) + #4 (Anthropic key) + #5 (private-key block) all fire and the runner exits 0 with all-pass. Depends on T013.

**Checkpoint**: Default-deny ruleset inheritance verified.

---

## Phase 5: User Story 3 — Existing-adopter no-surprise (Priority: P1)

**Goal**: Existing adopters who pull the F-5 update via `git pull` do NOT have `.git/hooks/pre-commit` written automatically.

**Independent Test**: Simulate existing-adopter clone (one with no `.git/hooks/pre-commit`); apply F-5 update via `git pull`; inspect `.git/hooks/pre-commit` post-pull — no file written.

### Implementation for User Story 3

- [X] T019 [US3] Empirically verify FR-010 / AC-9: clone tachi to a fresh location BEFORE F-5 changes are merged (or check out main); confirm no `.git/hooks/pre-commit`. Apply F-5 changes via `git pull origin 282-pre-commit-secret-scanning-defaults` (or equivalent). Inspect `.git/hooks/pre-commit` post-pull — must NOT exist. Document the pre/post state in `.aod/results/ac9-existing-adopter-verification.md`. [MANUAL-ONLY] verification — depends on git environment fidelity.

**Checkpoint**: Existing-adopter no-surprise flow verified.

---

## Phase 6: User Story 4 — False-positive avoidance (Priority: P1)

**Goal**: Tachi's own `make test`, `pre-commit run --all-files`, and routine `/aod.build` workflows produce ZERO gitleaks false-positive findings on the pre-F-5 baseline tree.

**Independent Test**: Run `pre-commit run --all-files` (or equivalent) from F-5 branch with shipped `.gitleaks.toml`; observe ZERO findings.

### Implementation for User Story 4

- [X] T020 [US4] Empirically verify FR-002 acceptance scenario 1 (AC-4): from F-5 branch with all Wave 1 files in place, run `pre-commit install && pre-commit run --all-files`. Confirm zero findings. If any findings appear: investigate (a) is it a legitimate credential we should remove from the tree? (b) is it a tachi-specific allow-list gap we should add to `.gitleaks.toml`? (c) is it gitleaks default-rule overreach we need to suppress? Apply Five Whys per Constitution Principle VIII. Document outcome in `.aod/results/ac4-baseline-zero-findings.md`. Depends on T003-T006 (Wave 1 files).
- [X] T021 [US4] Verify placeholder + path-allow-list cases via T013 runner: confirm fixtures #7-#16 all produce zero findings as expected. Depends on T013.

**Checkpoint**: False-positive rate verified zero on tachi's pre-F-5 baseline.

---

## Phase 7: Wave 4 — Documentation & ADR (User Stories 5+ docs surface)

**Goal**: Self-contained operator handbook + accepted ADR + CHANGELOG sibling-h3 entry + README pointer.

**Note**: This phase serves User Story 5 (SecOps reviewer P2) directly via FR-005 + FR-006, and serves cross-cutting concerns (CHANGELOG/README) for FR-011 + FR-012.

### Implementation for User Story 5 (Priority: P2) + cross-cutting

- [X] T022 [P] [US5] Author `docs/standards/PRECOMMIT_HOOKS.md` (~150-250 LOC) with 9 sections per AC-10: §Why-this-hook-ships, §Installation-paths (3: init.sh-default-Y, existing-adopter `pre-commit install`, manual `pip install pre-commit && pre-commit install`), §What-gets-scanned (staged content only; default rules + custom rules; per-rule rationale catalog), §Bypass-mechanisms (`SKIP=gitleaks`, `# gitleaks:allow`, `pre-commit uninstall`, `--no-verify` honest disclosure), §Refused-commit-error-message-contract (4-item via wrapper per FR-008), §CI-parity (`.github/workflows/gitleaks.yml`), §Re-init-behavior (init.sh hard-exits on second run; **per PM-PLAN-2 carry-forward**, explicitly state "The `--no-precommit` and `--precommit` flags affect only the *first-run* init.sh invocation. To opt out post-init, run `pre-commit uninstall` from the repo root."), §Known-limitations (`--no-verify`, framework distribution risk, custom rule limits, staged-content-only, post-history-rewrite leaks, GH-Actions-secret-in-logs out of scope, **per Architect CONCERN-3 carry-forward**: `pre-commit framework version drift` with explicit minimum >= v3.5.0 floor + justification: "tachi's `.pre-commit-config.yaml` schema requires v3.5.0+ for stable hook resolution; below this version, hook installation may silently partial-install or runtime-crash on first invocation."), §Adopter-customization (per-rule additions; merge conflict guidance per R-9; gitleaks-vs-trufflehog-vs-detect-secrets swap path; directory-rename considerations per Architect A-3). Per-rule rationale catalog cross-links one-to-one with `.gitleaks.toml` rules per AC-10 [MANUAL-ONLY] reviewer cross-check. Depends on T003 (`.gitleaks.toml` finalized).
- [X] T023 [P] [US5] Author `docs/architecture/02_ADRs/ADR-042-pre-commit-secret-scanning-default.md` (~130-180 LOC) with status `Proposed` initially (will be flipped to `Accepted` post-Architect-sign-off at /aod.deliver). Sections per AC-11: §Context (credential-exposure-prevention deficit; PRD §Problem-Statement #1-#6 enumerated), §Decision (gitleaks-vs-trufflehog rationale; opt-in install posture; pin-bump cadence policy per A-2; raw `read -p` waiver per C-3 per Q10; wrapper script per C-2 per Q9), §Alternatives-considered (9 with rejection rationale: trufflehog, detect-secrets, GitHub native push-protection, custom regex hook, opt-out flag, tier the hooks, GitGuardian, SecretLint, git-secrets — **MUST correct PRD comparison-matrix error: trufflehog runtime is Go, not Python**), §Consequences (positive: defense-in-depth gate, BLP-02 closure; negative: pre-commit framework dependency adoption, false-positive risk; mitigation: AC-SPEC-1 + R-1 hot-patch contingency; pin-bump cadence policy: bump on each gitleaks minor release with empirical re-verification — synthetic-fixture re-test per FR-013 before merging the bump), §References (PRD link, spec link, plan link, F-3/F-4 ADR links, gitleaks repo).
- [X] T024 [P] Modify `CHANGELOG.md` Unreleased section per FR-011 — add sibling-h3 entry `### Pre-commit secret-scanning defaults (BLP-02 F-5)` (NOT under `### Features`; N-4 carry-forward through F-2/F-3/F-4 per KB Entry 4 §Pattern 3) describing all new files (`.pre-commit-config.yaml`, `.gitleaks.toml`, `.aod/personalization.env.example`, `.aod/scripts/bash/precommit-wrap.sh`, `docs/standards/PRECOMMIT_HOOKS.md`, ADR-042, `.github/workflows/gitleaks.yml`) + deltas (`scripts/init.sh`, `README.md`) + the existing-adopter opt-in path (`To enable, run pre-commit install from the repo root after git pull`).
- [X] T025 [P] Modify `README.md` per FR-012 — add one-line pointer to `docs/standards/PRECOMMIT_HOOKS.md` in existing "Security" subsection (Q7 resolution; placement consistent with F-3 SECURITY.md and F-4 CLAUDE_PERMISSIONS.md README pointers). Single-line addition; do NOT rewrite the Security section.
- [X] T026 Update `docs/standards/README.md` index — insert `PRECOMMIT_HOOKS.md` row in the Standards Index Table after `CLAUDE_PERMISSIONS.md` (alphabetical adjacency) with description: `Pre-commit secret-scanning configuration, gitleaks rule customization for tachi conventions, install/opt-out/bypass paths, and adopter troubleshooting (Feature 282 — F-5 Pre-commit Secret-Scanning Defaults, BLP-02 Wave 4+). Companion to ADR-042.`

**Checkpoint**: Documentation surface complete; SecOps reviewer can audit cold.

---

## Phase 8: Wave 3 (continued) — CI Parity Workflow (User Story 6 P2)

**Goal**: New `.github/workflows/gitleaks.yml` runs gitleaks against PR full-repo content as a back-stop for `--no-verify` deliberate bypass.

**Independent Test**: Open a feature branch with a deliberately-bad credential file using `--no-verify`; push; verify the GitHub Actions check fails. Delete the bad file; force-push; verify the check passes.

### Implementation for User Story 6

- [X] T027 [US6] Create `.github/workflows/gitleaks.yml` (~25-40 LOC) per FR-007: triggers on `pull_request` events; uses `runs-on: ubuntu-latest`; downloads gitleaks binary directly from GitHub release tarball at the version pinned in `.pre-commit-config.yaml` (v8.30.1 initially); verifies tarball SHA256 checksum; invokes `gitleaks git --config=.gitleaks.toml --report-format=sarif --report-path=gitleaks.sarif`; uploads SARIF to GitHub Code Scanning via `github/codeql-action/upload-sarif@v3` (or equivalent action). Native gitleaks output ONLY — does NOT invoke `.aod/scripts/bash/precommit-wrap.sh` (LOCAL-ONLY per PM-5). Full-repo scan per Q5. Avoids proprietary `gitleaks-action@v2` license trap per research finding. Depends on T003 (`.gitleaks.toml` exists).
- [X] T028 [US6] Empirically verify FR-007 acceptance scenarios via PR test: on this F-5 feature branch, temporarily commit a deliberately-bad credential file (e.g., `tests/fixtures/_DELETE_ME_GITHUB_PAT.txt` containing `ghp_<random40chars>`) using `git commit --no-verify` to bypass local hook; push to remote; observe the gitleaks GHA check fail with rule ID + file:line matching local hook output. Then `git rm tests/fixtures/_DELETE_ME_GITHUB_PAT.txt && git commit && git push`; observe GHA check pass. Per Architect A-10 (PRD): cleanup discipline — the bad-credential commit MUST be removed before /aod.deliver merge. Depends on T027.

**Checkpoint**: CI parity verified end-to-end.

---

## Phase 9: Wave 5 — Delivery Verification

**Goal**: Pre-merge final verification + post-merge release-please verification + post-merge follow-up Issues.

### Implementation (cross-cutting; no story label)

- [X] T029 Pre-merge final verification suite: (a) re-run `pre-commit run --all-files` from F-5 branch — confirm zero findings (AC-4 / FR-002 / SC-001); (b) re-run `bash tests/fixtures/gitleaks-rule-interaction/run.sh` — confirm 16/16 fixtures pass (AC-SPEC-1 / FR-013); (c) re-run `pytest tests/scripts/test_init_precommit_matrix.py` — confirm 6/6 matrix cases pass; (d) confirm CI workflow green on PR (T028 already-verified); (e) confirm reviewers can cross-check `.gitleaks.toml` rule IDs against PRECOMMIT_HOOKS.md per-rule rationale catalog (AC-10 / FR-005). Document in `.aod/results/wave5-pre-merge-verification.md`. [MANUAL-ONLY] reviewer cross-check on (e). Depends on all prior tasks.
- [ ] T030 At /aod.deliver time: pre-merge title verification per `.claude/rules/git-workflow.md` §Conventional-Commit-PR-Titles — confirm PR title is `feat(282): pre-commit secret-scanning defaults`; if not, retitle via `gh pr edit <PR> --title "feat(282): pre-commit secret-scanning defaults"`. Mark draft PR ready via `gh pr ready`. Squash-merge via `gh pr merge --squash`.
- [ ] T031 At /aod.deliver time: post-merge release-please verification per FR-015 / SC-006 — within 30 seconds of squash-merge, run `gh pr list --state open --search "release-please" --limit 3`. If empty, push an empty release-marker commit: `git commit --allow-empty -m "feat(282): pre-commit secret-scanning defaults — release marker" && git push origin main`. Document in `.aod/results/release-please-verification-282.md`. [MANUAL-ONLY] verification — depends on actual release-please cadence.
- [ ] T032 At /aod.deliver time: post-merge `/security` re-scan per FR-014 / AC-16 — run `/security` against main post-F-5-merge; confirm zero NEW findings on F-5 file surface (`scripts/init.sh`, `.pre-commit-config.yaml`, `.gitleaks.toml`, `.aod/personalization.env.example`, `docs/standards/PRECOMMIT_HOOKS.md`, ADR-042, `.github/workflows/gitleaks.yml`, `.aod/scripts/bash/precommit-wrap.sh`). Document in `.aod/results/security-rescan-282.md`. [MANUAL-ONLY] runs at /aod.deliver time.
- [ ] T033 At /aod.deliver time: file post-merge follow-up Issues per Q3 + Architect CONCERN-4 + AC-18 + AC-19: (a) AC-18 rule-coverage probe Issue — enumerate gitleaks default rule IDs active for tachi and confirm threat surface (PAT / AWS / OpenAI / Anthropic / generic-high-entropy) fully covered; (b) AC-19 adopter-extensibility template Issue — `.gitleaks.toml.adopter-template` documenting custom-rule additions; (c) **per Architect CONCERN-4 carry-forward**: pin-bump cadence accountability Issue — recurring `maintenance` label, references ADR-042 §Consequences cadence policy, triggered on each gitleaks minor release for synthetic-fixture re-verification before merging the bump. Title format: `chore(282): post-merge follow-up — <topic>` to avoid release-please trigger. Use `gh issue create --label maintenance --title "..." --body "..."` for each.
- [ ] T034 At /aod.deliver time: flip ADR-042 status from `Proposed` to `Accepted` in the ADR file's frontmatter / status header, with the post-merge date. Per ADR convention (F-1, F-2, F-4 precedents).
- [ ] T035 At /aod.deliver time: update memory `project_blp02_enterprise_hardening.md` to mark BLP-02 5/5 closed (G9 / SC-008); update memory `project_blp01_threat_coverage.md` cross-reference if needed; document the LinkedIn-thread punch-list 3/3 closure (G3 / SC-009).
- [ ] T036 At /aod.deliver time: regenerate BACKLOG.md via `bash .aod/scripts/bash/backlog-regenerate.sh` after Issue #282 closure.

**Checkpoint**: BLP-02 5/5 closed. LinkedIn-thread 3/3 closed. F-5 delivered.

---

## Phase 10: Polish & Cross-Cutting Concerns

(No additional polish tasks beyond Wave 5. F-5's polish IS the documentation + ADR + CI parity already covered. The 7 carry-forward concerns are all addressed in-line above:)

| Carry-Forward | Where Addressed |
|---------------|-----------------|
| Architect CONCERN-1 (test runner location) | T013 (co-located at `tests/fixtures/gitleaks-rule-interaction/run.sh`) |
| Architect CONCERN-2 (init.sh matrix as pytest) | T014 + T014a (`tests/scripts/test_init_precommit_matrix.py` + `tachi-pytest.yml` lock-step) |
| Architect CONCERN-3 (pre-commit version check + v3.5.0 floor doc) | T016 (init.sh `--version` check) + T022 (PRECOMMIT_HOOKS.md §Known-Limitations justification) |
| Architect CONCERN-4 (pin-bump cadence tracking) | T033 (post-merge maintenance Issue) |
| PM-PLAN-1 (fixture rule-ID assertion comments) | T009 (header comments naming expected gitleaks rule ID as of v8.30.1) |
| PM-PLAN-2 (PRECOMMIT_HOOKS.md flag-first-run-only) | T022 (§Re-init-behavior explicit clarification) |
| PM-PLAN-3 (fixture #14 schema-out-of-scope comment) | T011 (fixture #14 header comment per F-260b call-out) |
| PM-3 consolidation (FR-008 + FR-009 single task family) | T005 (single wrapper task explicitly notes consolidation) |

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: T001-T002 — no dependencies
- **Phase 2 (Foundational/Wave 1)**: T003-T007 — depends on T001-T002 (branch + draft PR)
- **Phase 3-6 (User Stories 1-4)**: depend on Wave 1 (T003-T006) complete; then Wave 2 verification (T008-T013) + Wave 3 init.sh (T015-T017) + matrix test (T014/T014a) can run partially in parallel
- **Phase 7 (Wave 4 docs + ADR)**: T022-T026 depend on T003 (`.gitleaks.toml` finalized for per-rule rationale catalog)
- **Phase 8 (Wave 3 CI)**: T027-T028 depend on T003 (`.gitleaks.toml` exists for CI to use)
- **Phase 9 (Wave 5 delivery)**: T029-T036 depend on all prior phases

### Critical Path

T001 → T002 → T003-T006 (Wave 1 parallel) → T007 (smoke test) → [T008-T013 + T015-T016] (Wave 2 + Wave 3 init.sh parallel) → T014/T014a (matrix test) + T017 (init.sh empirical) → T020 (US4 baseline verification) → T022-T026 (Wave 4 docs parallel) + T027-T028 (Wave 3 CI sequential) → T029 (pre-merge verification) → T030-T036 (Wave 5 delivery, mostly /aod.deliver-time)

### Parallel Opportunities

- **Wave 1**: T003 + T004 + T005 file-disjoint, parallel-safe
- **Wave 2 fixtures**: T009 + T010 + T011 + T012 fixture creation file-disjoint, parallel-safe
- **Wave 3 init.sh + Wave 2 fixtures**: T014/T014a (matrix pytest) authoring is parallel with Wave 2 fixture creation (different files)
- **Wave 4 docs + ADR + CHANGELOG + README**: T022 + T023 + T024 + T025 file-disjoint, parallel-safe
- **Wave 5 delivery-time tasks**: mostly sequential (squash-merge → release-please → security re-scan → memory update)

### Single-maintainer Realistic Ordering

Per Team-Lead A-1 calibration (~9-13h Phase 2 envelope):

1. ~30min: T001 + T002 (branch + draft PR)
2. ~2h: T003 + T004 + T005 + T006 (Wave 1 — `.gitleaks.toml`, `.env.example`, wrapper, hook config)
3. ~30min: T007 (Wave 1 smoke test)
4. ~2-3h: T008-T013 (Wave 2 — fixtures + runner)
5. ~1h: T015 + T016 (init.sh delta + version check)
6. ~30-45min: T017 (init.sh empirical verification — 5 scenarios)
7. ~1.5h: T014 + T014a (matrix pytest + workflow lock-step)
8. ~30-45min: T020 + T021 (Wave 1 + Wave 2 baseline + fixture cross-check)
9. ~30min: T019 (existing-adopter no-surprise verification)
10. ~2-3h: T022 (PRECOMMIT_HOOKS.md ~150-250 LOC) + T023 (ADR-042 ~130-180 LOC)
11. ~15min: T024 + T025 + T026 (CHANGELOG / README / standards index)
12. ~30-60min: T027 (CI workflow) + T028 (CI empirical with bad-credential push/cleanup)
13. ~30min: T029 (pre-merge verification consolidation)
14. /aod.deliver time: T030-T036 (~30-45min total at delivery)

**Total active envelope**: ~12-15h (realistic for Saturday 2026-05-10 + slack 2026-05-11 per Team-Lead A-5).

---

## Implementation Strategy

### MVP Scope (User Story 1 only)

If time pressures force scope reduction, the MVP is User Story 1 (P1):
- T001-T002, T003-T007 (Wave 1 + smoke), T008-T013 (Wave 2 fixtures + runner), T015-T017 (init.sh delta), T020 (US4 baseline), T022 (PRECOMMIT_HOOKS.md minimal), T024-T025 (CHANGELOG + README).
- ADR-042 (T023) can be Proposed (not Accepted) at MVP merge with explicit Accepted-at-/aod.deliver flip.
- CI parity (T027-T028) can defer to a v4.34.x patch release if CI binary-direct invocation hits an edge case.
- AC-19 + AC-18 follow-ups defer to post-merge per Q3.

**MVP excludes**: Wave 3 CI parity (T027-T028 — defer to v4.34.x), Wave 5 follow-up Issues (T033 — defer to /aod.deliver), AC-19 adopter-extensibility template.

### Incremental Delivery (preferred)

Ship full F-5 in single squash-merge PR per BLP-02 convention (F-1 / F-2 / F-3 / F-4 precedent). Single `feat(282):` commit subject triggers release-please (R-1 SLO ~30s).

### Risk-mitigation strategy

- **R-1 (false-positive flood)**: AC-SPEC-1 fixture catalog (T009-T013) is preventive verification BEFORE merge per C-4
- **R-3 (gitleaks tag force-move)**: T006 commits pinned commit SHA (not tag); T033 post-merge maintenance Issue tracks pin-bump cadence
- **R-4 (existing-adopter dual-hook)**: T019 verifies AC-9 explicitly
- **R-9 (`.gitleaks.toml` divergence on `make update`)**: T022 PRECOMMIT_HOOKS.md §Adopter-Customization documents merge pattern
- **R-10 (pre-commit framework version drift)**: T016 init.sh `--version` check; T022 PRECOMMIT_HOOKS.md §Known-Limitations floor justification

---

## File Surface Summary

| File | Status | Approx LOC | Wave | Tasks |
|------|--------|-----------|------|-------|
| `.pre-commit-config.yaml` | NEW | 30-50 | 1 | T006 |
| `.gitleaks.toml` | NEW | 50-80 | 1 | T003 |
| `.aod/personalization.env.example` | NEW | 10-20 | 1 | T004 |
| `.aod/scripts/bash/precommit-wrap.sh` | NEW | 30-60 | 1 | T005 |
| `tests/fixtures/gitleaks-rule-interaction/` | NEW | 16 fixtures | 2 | T008-T012 |
| `tests/fixtures/gitleaks-rule-interaction/run.sh` | NEW | 30-50 | 2 | T013 |
| `tests/scripts/test_init_precommit_matrix.py` | NEW | 50-80 | 2 | T014 |
| `.github/workflows/tachi-pytest.yml` | DELTA | ~5 | 2 | T014a |
| `scripts/init.sh` | DELTA | 10-20 + 5 (version check) | 3 | T015-T016 |
| `docs/standards/PRECOMMIT_HOOKS.md` | NEW | 150-250 | 4 | T022 |
| `docs/architecture/02_ADRs/ADR-042-pre-commit-secret-scanning-default.md` | NEW | 130-180 | 4 | T023 |
| `CHANGELOG.md` | DELTA | ~3-5 | 4 | T024 |
| `README.md` | DELTA | ~1 | 4 | T025 |
| `docs/standards/README.md` | DELTA | ~1 | 4 | T026 |
| `.github/workflows/gitleaks.yml` | NEW | 25-40 | 3 | T027 |

**Total**: 8 new files + 5 deltas + 16 fixture files + 1 test runner + 1 pytest test = ~440-685 LOC core + fixtures + test scaffolding (per PRD §File-Surface table calibration).

---

## References

- Spec: [spec.md](spec.md)
- Plan: [plan.md](plan.md)
- Research: [research.md](research.md)
- PRD: [docs/product/02_PRD/282-pre-commit-secret-scanning-defaults-2026-05-09.md](../../docs/product/02_PRD/282-pre-commit-secret-scanning-defaults-2026-05-09.md)
- Constitution: [.aod/memory/constitution.md](../../.aod/memory/constitution.md)
- Spec PM review: [.aod/results/product-manager-spec-282.md](../../.aod/results/product-manager-spec-282.md)
- Plan PM review: [.aod/results/product-manager-plan-282.md](../../.aod/results/product-manager-plan-282.md)
- Plan Architect review: [.aod/results/architect-plan-282.md](../../.aod/results/architect-plan-282.md)
- F-3 tasks precedent: [specs/272-security-md-disclosure/tasks.md](../272-security-md-disclosure/tasks.md)
- F-4 tasks precedent: [specs/277-claude-permissions-baseline/tasks.md](../277-claude-permissions-baseline/tasks.md)
