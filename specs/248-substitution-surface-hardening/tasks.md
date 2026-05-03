---
triad:
  pm_signoff:
    agent: product-manager
    date: 2026-05-03
    status: APPROVED
    notes: "All 7 US, 11 FRs, 5 NFRs, 4 Q-adjudications, 15 SCs, 14-item DoD trace cleanly to task IDs; zero BLP-02 Wave 2+ scope creep; single-PR delivery preserved; NFR-004 PM veto at >50% retained."
  architect_signoff:
    agent: architect
    date: 2026-05-03
    status: APPROVED
    notes: "All 8 architect criteria pass; B-1/B-2/H-1/H-2/H-3/M-1/M-2/M-3/Q-1/Q-2/Q-3 honored; test-first preserved (T009-T013 before T015-T021); strict reorder T017→T018→T019→T020; dual-commit ADR T034 (Proposed) → T035 (benchmark amendment) → T036 (Accepted); bash 3.2 constraint explicit at T022; .aod/templates/ paths verified."
  techlead_signoff:
    agent: team-lead
    date: 2026-05-03
    status: APPROVED_WITH_CONCERNS
    notes: "50 tasks across 10 phases; timeline math closes 8d active / 10d ceiling; test-first preserved per Constitution VI (T009-T013 before T015-T021, T014 deferred post-Stream-1); Day-5 slip-watch named (T041); [MANUAL] correctly flagged on T042/T044-T050; 1 HIGH concern (F-1→F-2 pattern-vs-function reuse contract in ADR-038) folded into T034 prior to commit."
---

# Tasks: Substitution Surface Hardening (BLP-02 Wave 1)

**Input**: Design documents from `/specs/248-substitution-surface-hardening/`
**Prerequisites**: plan.md (✓ PM + Architect APPROVED), spec.md (✓ PM APPROVED), research.md, data-model.md, contracts/, quickstart.md

**Tests**: REQUIRED — Per spec FR-011 + Regression Protection Plan, this feature requires 4 pytest test files + baseline fixtures (Stream 5). Test tasks are NOT optional for F-1.

**Organization**: Tasks are grouped by user story (US-248-1..US-248-7) with cross-references to plan.md streams (Stream 1..Stream 5). The 7 user stories map onto 5 implementation streams; overlapping work (e.g., Stream 1 substitution adoption serves US-248-1 + US-248-4 + US-248-5 + US-248-6) is tagged with the dominant user story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies on incomplete tasks)
- **[Story]**: Maps task to user story (US1..US7)
- **[MANUAL]**: Cannot be automated; closing operator action at `/aod.deliver`
- File paths are absolute or rooted at repo root

## Path Conventions

- Source bash scripts: `scripts/init.sh` (modified); `.aod/scripts/bash/init-input.sh` (NEW)
- Templates: `.aod/templates/constitution-{clean,instructional}.md` (NEW)
- ADR: `docs/architecture/02_ADRs/ADR-038-placeholder-substitution-strategy.md` (NEW)
- Tests: `tests/scripts/test_init_sh_*.py` (NEW); `tests/fixtures/init-baseline-tree/` + `tests/fixtures/regenerate-baseline.sh` (NEW)
- Contract docs: `contracts/personalization-schema.md` (modified)

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Workspace verification and directory scaffolding before implementation begins.

- [X] T001 Verify feature branch + draft PR state: `git branch --show-current` returns `248-substitution-surface-hardening`; `gh pr view 249` returns draft PR with title `feat(248): substitution surface hardening`; spec.md and plan.md frontmatter contain required sign-offs (PM, Architect)
- [X] T002 [P] Create `.aod/templates/` directory if not present (verify `ls -d .aod/templates/` succeeds; create with `mkdir -p .aod/templates/` if missing)
- [X] T003 [P] Create `tests/fixtures/` directory if not present (verify `ls -d tests/fixtures/` succeeds; create with `mkdir -p tests/fixtures/` if missing)
- [X] T004 [P] Snapshot dependency manifests for NFR-002 verification: capture `git show HEAD:pyproject.toml` and `git show HEAD:requirements*.txt` baselines; record SHA-256 of each in tasks-runlog.txt for end-of-build comparison

**Checkpoint**: Workspace is clean and ready for substitution-surface work.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Decisions and artifacts that MUST be complete before any user-story work can proceed. Architect adjudication, baseline benchmark, and pre-stripped templates land here.

**CRITICAL**: T005 (internal-tooling search outcome) gates T028 (PROJECT_PATH disposition implementation). T006-T007 gate T027 (constitution cleanup). T008 baseline benchmark gates the post-swap measurement in T015.

- [X] T005 Internal-tooling search for Q-1 adjudication: grep `mcp-config.json` across `.aod/scripts/`, `.claude/agents/`, `.claude/commands/`, `Makefile`, `scripts/` for any wired consumer reading the file from the project tree (5-minute scope). Record outcome in `specs/248-substitution-surface-hardening/spec.md` §Internal-Tooling Search Outcome (replace "provisional" line with confirmed outcome). Default disposition: Option (b) — remove `.claude/mcp-config.json`. Fallback: Option (a) — add PROJECT_PATH to canonical-13.
- [X] T006 [P] Author `.aod/templates/constitution-instructional.md` — full template variant containing HTML comment block at top + `## Template Instructions` section + main constitution body (preserves the current pre-init template content that the existing `sed -i` cleanup operates on)
- [X] T007 [P] Author `.aod/templates/constitution-clean.md` — post-strip output variant: byte-equivalent to running the current sed cleanup over `constitution-instructional.md` (remove `<!--...-->` comment block + `## Template Instructions` section to EOF). Validate byte-faithful relationship manually: `sed '/^<!--$/,/^-->$/d; /^## Template Instructions$/,$d' constitution-instructional.md` MUST equal `constitution-clean.md` byte-for-byte
- [X] T008 Stream 1 Day 1 baseline benchmark (NFR-004): from a snapshot of pre-merge state, time `./scripts/init.sh` on the canonical fixture inputs (PROJECT_NAME=tachi, PROJECT_DESCRIPTION=threat modeling sidecar, etc.) using the bash `time` builtin. Capture `real`, `user`, `sys` values to tasks-runlog.txt for ADR-038 §Consequences

**Checkpoint**: Internal-tooling search outcome committed; constitution templates ready; baseline benchmark recorded. Stream 1 substitution swap can now begin.

---

## Phase 3: User Story 1 + 6 (P1) — Substitution-semantics correctness + multi-hop chain defense layer 2

**Stream 1 — Substitution Adoption (Critical Path, 2.5d)** — covers US-248-1 (metacharacter-bearing project name), US-248-4 (sed removal), US-248-5 (placeholder contract closure), and the substitution-semantics layer of US-248-6 (multi-hop chain defense-in-depth).

**Goal**: `replace_in_files()` removed; substitution loop routes through `aod_template_substitute_placeholders` (literal substitution via bash parameter expansion); residual scan halts on any orphan `{{KEY}}`; pre-flight check prevents re-init.

**Independent Test**: Run `init.sh` with `PROJECT_NAME=AT&T`; verify literal substitution survives in all personalized files; verify `aod_template_assert_no_residual` reports zero residuals; verify init exits 0; verify pre-flight rejects subsequent re-invocation.

### Tests for User Story 1+6 (Stream 5 — authored before Stream 1 implementation per Constitution VI test-first principle)

**NOTE: Tests written FIRST per Constitution VI. Test files land before substitution swap; tests fail against pre-merge baseline; tests pass after Stream 1 implementation.**

- [X] T009 [P] [US1] Author `tests/scripts/test_init_sh_substitution.py` (Test-1 fixture-replay byte-comparison): use `subprocess.run` to invoke `init.sh` against a controlled tmpdir clone with the canonical fixture inputs; walk the resulting personalized tree; for each file, assert `Path.read_bytes()` equality against `tests/fixtures/init-baseline-tree/`; assert mode preservation via `Path.stat().st_mode`. Pass inputs via env vars (preferred) for non-interactive testability
- [X] T010 [P] [US1] Author `tests/scripts/test_init_sh_adversarial.py` (Test-2: ≥13 adversarial inputs) using `pytest.mark.parametrize` table:
  Cases 1–6 substitution-semantics (env-var injection bypasses prompt): `AT&T` / `foo|bar` / `\1\2 backref` / `'single-quoted'` / `"double-quoted\"escaped"` / multibyte UTF-8 `Ⅷ-Ⅸ` — assert literal substitution survives byte-identical;
  Case 7 leading-whitespace, Case 8 trailing-whitespace — assert preserved per spec;
  Cases 9–12 prompt-rejection (stdin injection): multi-line / NUL / over-length / control char (0x07 BEL) — assert exit non-zero with named-class rejection message;
  Case 13 trailing-newline edge cases (per Architect Pass 1 M-1): fixture file containing literal 4 bytes `a\nb` (backslash-n, no LF) — assert byte-identical preservation; second fixture file ending without trailing LF — assert byte-identical preservation
- [X] T011 [P] [US1] Author `tests/scripts/test_init_sh_constitution.py` (Test-4 byte-compare): run `init.sh` end-to-end; assert `Path(".aod/memory/constitution.md").read_bytes() == Path(".aod/templates/constitution-clean.md").read_bytes()`
- [X] T012 [P] [US1] Author `tests/scripts/test_init_sh_self_delete.py` (Test-5' self-delete preservation): run `init.sh` end-to-end; assert `not Path("scripts/init.sh").exists()` post-init (replaces original Test-5 re-init parity per Architect M-3 + Team-Lead Q-3 Option b)
- [X] T013 [P] [US1] Author `tests/fixtures/regenerate-baseline.sh` script (per Team-Lead Pass 1 M-5): clones tachi fresh into tmpdir, runs `init.sh` with canonical fixture inputs, copies personalized tree to `tests/fixtures/init-baseline-tree/`, includes documentation header explaining when to regenerate (canonical-12 expansion only — never to mask substitution-semantics regression)
- [ ] T014 [US1] Run `tests/fixtures/regenerate-baseline.sh` once with the **post-Stream-1 init.sh** to populate `tests/fixtures/init-baseline-tree/` (deferred dependency: must run AFTER T015–T021 substitution swap completes; T014 establishes the baseline reference Test-1 will compare against). Commit the baseline tree

### Implementation for User Story 1+6 (Stream 1 substitution adoption)

- [X] T015 [US1] Add `source .aod/scripts/bash/template-substitute.sh` at the top of `scripts/init.sh` (replace the lazy source at existing `:336` with eager top-of-file source). Preserves bash 3.2 compatibility per NFR-001
- [X] T016 [US1] Add re-init pre-flight check at top of `scripts/init.sh` (after sourcing template-substitute.sh): if `[[ -f .aod/personalization.env ]]`, exit 1 with `[init] FATAL: Repository already personalized. Re-init is not supported. To re-personalize, remove .aod/personalization.env and re-run init.sh.` (FR-003)
- [X] T017 [US1] Reorder `scripts/init.sh` snapshot-write to BEFORE the substitution loop (per Architect Pass 1 BLOCKING B-2 pattern P1; existing snapshot-write at `:346` moves to a new line position immediately after prompts). Output: `.aod/personalization.env` is fully populated before any substitution call (FR-002)
- [X] T018 [US1] Add `aod_template_load_personalization_env .aod/personalization.env` immediately after snapshot-write in `scripts/init.sh`. Sets `AOD_PERSONALIZATION_<KEY>` env vars in caller scope as pre-condition for `aod_template_substitute_placeholders` (FR-002)
- [X] T019 [US1] Replace `replace_in_files()` function body at `scripts/init.sh:117-159` with a `find ... -print0 | while IFS= read -r -d '' file` loop that calls `aod_template_substitute_placeholders "$file" "$file"` (in-place substitution) per file. Preserve the existing `find` filter (excludes `.git/`, `node_modules/`, `*.png`, `*.jpg`, `*.ico`). Remove the macOS/Linux sed branching entirely (FR-001)
- [X] T020 [US1] After the substitution loop in `scripts/init.sh`, add a residual scan: `aod_template_assert_no_residual "$file"` per file (re-walk the same `find` filter or store the file list from T019). On any non-zero return, print `[init] FATAL: residual placeholder in <file>; aborting.` and exit 1 (FR-004)
- [ ] T021 [US1] Stream 1 Day 1 post-swap benchmark (NFR-004): time `./scripts/init.sh` on the canonical fixture (matching T008 inputs); calculate delta vs T008 baseline (`(post - pre) / pre * 100%`). Apply NFR-004 escalation: ≤5% holds NFR-004 at 10% (record numbers); 5–50% loosens NFR-004 to 25% with rationale (record in ADR-038 §Consequences); >50% escalate to PM for re-scope before merge

**Checkpoint**: User Stories 1+6 (substitution-semantics layer) functional. Test-1 + Test-2 substitution cases pass. Move to T014 (baseline regeneration) and Stream 2.

---

## Phase 4: User Story 2 (P1) — Multi-line paste rejection + multi-hop chain defense layer 1

**Stream 2 — Input Validation (1.0d, parallelizable with Stream 1)** — covers US-248-2 (multi-line paste rejection) and the prompt-time rejection layer of US-248-6 (multi-hop chain defense-in-depth).

**Goal**: New helper `aod_init_read_validated` rejects newline / NUL / control char / over-length input at prompt time; 3-strikes exit; all 4 `read -p` prompts in `init.sh:24-28` wrapped.

**Independent Test**: Send a multi-line value to the PROJECT_NAME prompt via stdin; verify rejection message; verify re-prompt; after 3 strikes, verify exit non-zero with FATAL message.

### Tests for User Story 2 (covered by T010 Test-2 cases 9–12 above — no separate test files)

### Implementation for User Story 2 (Stream 2 input validation)

- [ ] T022 [P] [US2] Author `.aod/scripts/bash/init-input.sh` per `specs/248-substitution-surface-hardening/contracts/init-input-helper-contract.md`: function `aod_init_read_validated <prompt> <var_name> <max_len>` with rejection ladder (newline → NUL → control char → over-length); 3-strikes exit; `printf -v "$var_name" '%s' "$answer"` on success (no `eval`); bash 3.2 compatible (no associative arrays, no `mapfile`, no `${var,,}`). Apply Feature 132 lesson: if internal command-substitution under `set -euo pipefail` is added, bracket with `set +e`/`set -e` (FR-005)
- [ ] T023 [US2] Source the new helper at top of `scripts/init.sh`: add `source .aod/scripts/bash/init-input.sh` alongside the existing `source .aod/scripts/bash/template-substitute.sh` (depends on T022; T022 file must exist before sourcing)
- [ ] T024 [US2] Wire prompt 1 in `scripts/init.sh`: replace `read -p "Project Name: " PROJECT_NAME` (existing line 24) with `aod_init_read_validated "Project Name: " PROJECT_NAME 100`
- [ ] T025 [US2] Wire prompt 2 in `scripts/init.sh`: replace `read -p "Project Description: " PROJECT_DESCRIPTION` (existing line 25) with `aod_init_read_validated "Project Description: " PROJECT_DESCRIPTION 300`
- [ ] T026 [US2] Wire prompt 3 in `scripts/init.sh`: replace `read -p "GitHub Organization: " GITHUB_ORG` (existing line 26) with `aod_init_read_validated "GitHub Organization: " GITHUB_ORG 39` (GitHub login hard limit per Architect Pass 1 L-1)
- [ ] T027 [US2] Wire prompt 4 in `scripts/init.sh`: replace `read -p "GitHub Repository [$PROJECT_NAME]: " GITHUB_REPO` (existing line 27) with `aod_init_read_validated "GitHub Repository [$PROJECT_NAME]: " GITHUB_REPO 100`. Preserve the existing post-prompt default-fallback logic: empty input → `GITHUB_REPO=$PROJECT_NAME`

**Checkpoint**: User Story 2 functional. Test-2 cases 9–12 (prompt rejection) pass. 4 prompts wrapped.

---

## Phase 5: User Story 3 (P1) — Gitignore default

**Stream 3 — Posture Defaults (0.5d, parallelizable with Streams 1+2)** — covers US-248-3 (gitignore default).

**Goal**: `.gitignore` excludes `.aod/personalization.env` (already present per `b27f3ea`); `contracts/personalization-schema.md` documents local-only default; CHANGELOG provides migration command for previously-committed adopters; init success message documents the default.

**Independent Test**: Run `init.sh`; run `git status`; verify `.aod/personalization.env` does not appear in change set. Verify `contracts/personalization-schema.md` §Substitution Strategy describes local-only default. Verify CHANGELOG.md has the migration command.

### Implementation for User Story 3 (Stream 3 posture defaults)

- [ ] T028 [US3] Verify `.gitignore:222` contains `.aod/personalization.env`: `grep -n "^.aod/personalization.env$" .gitignore` returns `222:.aod/personalization.env`. No code change; verification only (FR-006 AC-6.1)
- [ ] T029 [P] [US3] Update `contracts/personalization-schema.md` §Substitution Strategy: add a paragraph documenting local-only-by-default behavior, the rationale (avoids unintended commit of proprietary `PROJECT_DESCRIPTION` content), and the opt-in path (remove the `.gitignore` line to track) (FR-006)
- [ ] T030 [P] [US3] Add CHANGELOG.md entry under v4.x: include the copy-pasteable text `git rm --cached .aod/personalization.env && git commit -m "chore: untrack personalization snapshot per BLP-02 default"` plus a one-line note: "**Hardened defaults (BLP-02 F-1)**: .aod/personalization.env is now gitignored by default" (FR-006)
- [ ] T031 [US3] Add post-init success-message line in `scripts/init.sh` (after substitution loop, before self-delete): `echo "[init] Note: .aod/personalization.env is gitignored by default. To track it, remove the line from .gitignore."`

**Checkpoint**: User Story 3 functional. `git status` after fresh init confirms gitignore default.

---

## Phase 6: User Story 4 + 7 (P2) — Single canonical surface, ADR, enterprise artifact bundle

**Stream 4 — ADR + Release Trigger (0.5d, parallelizable with Streams 1+2+3)** — covers US-248-4 (sed removal in constitution cleanup, ADR-038), US-248-7 (artifact bundle for enterprise architect), and the JSON-parser-sink elimination layer of US-248-6 (multi-hop chain defense).

**Goal**: ADR-038 authored with dual-commit Proposed → Accepted; constitution sed cleanup replaced by `cp` from pre-stripped template; `.claude/mcp-config.json` removed (Q-1 Option b default); PR title is conventional-commits-formatted; release-please trigger verified.

**Independent Test**: After build, `grep -n "sed " scripts/init.sh` returns 0 matches; `ls .claude/mcp-config.json` returns "No such file or directory" (Option b); `docs/architecture/02_ADRs/ADR-038-placeholder-substitution-strategy.md` exists with Status: Accepted (post dual-commit); `gh pr view 249` title matches `feat(248): harden init.sh substitution surface — sed → bash param expansion + input validation + gitignore default`.

### Implementation for User Story 4+7 (Stream 4 ADR + release)

- [ ] T032 [US4] Replace constitution sed cleanup at `scripts/init.sh:235-241` with `cp ".aod/templates/constitution-clean.md" .aod/memory/constitution.md` (single line; remove the four `sed -i` invocations entirely — both macOS and Linux branches). Depends on T006+T007 constitution templates being authored. Add a comment line above explaining the post-F-1 mechanism (FR-008)
- [ ] T033 [US4] Implement Q-1 disposition per T005 outcome:
  - **If T005 confirmed Option (b) default (no wired consumer found)**: run `git rm .claude/mcp-config.json`; verify `ls .claude/mcp-config.json` returns "No such file or directory"; ensure no remaining grep references survive in active code (`grep -r "{{PROJECT_PATH}}" . --exclude-dir=.git --exclude-dir=node_modules` returns zero matches)
  - **If T005 surfaced a wired consumer (Option a fallback)**: add `PROJECT_PATH` as 13th element of `AOD_CANONICAL_PLACEHOLDERS` array at `.aod/scripts/bash/template-substitute.sh:50-63`; populate via `realpath "$(pwd)"` at init time; validate against character whitelist `[A-Za-z0-9._/-]`; document in `contracts/personalization-schema.md` (FR-007)
- [ ] T034 [P] [US4] Author `docs/architecture/02_ADRs/ADR-038-placeholder-substitution-strategy.md` with Status `Proposed` (initial commit per dual-commit pattern). Required sections per FR-009: Status, Context (cite Daniel Wood 2026-05-02 LinkedIn note + multi-hop chain), Decision (bash parameter expansion via `aod_template_substitute_placeholders`; explicitly note residual-scan regex character class `[A-Z_]+` and lockstep-update commitment per Architect Pass 1 M-2), Alternatives Considered (4 enumerated: sed-escape wrapper, awk -v, Python string.Template, Perl), Consequences (capture T021 benchmark numbers; **explicitly document the F-1→F-2 pattern-vs-function reuse contract per Team-Lead Pass 1 H-2: F-2 (BLP-02 Wave 2 — defaults.env strict KV parser) reuses the validation triplet pattern (regex-validate → reject-on-mismatch → `printf -v` assignment), NOT the `aod_init_read_validated` function itself; the function is interactive `read -p`-only while F-2 is non-interactive file-parse**), Related Decisions (cite ADR-009 superseded on mechanism axis), Related Findings (5 vuln_ids), References (Daniel Wood LinkedIn URL + `web.archive.org` snapshot URL per Team-Lead Pass 1 L-1)
- [ ] T035 [US4] Append T021 benchmark numbers + final NFR-004 disposition (≤5% / 5–50% / >50%) to ADR-038 §Consequences (depends on T021 + T034)
- [ ] T036 [US4] Promote ADR-038 Status from `Proposed` to `Accepted` (dual-commit pattern, second commit per Architect review). Update the in-file Status field; commit with message `docs(248): ADR-038 promoted to Accepted post architect review`
- [ ] T037 [US7] Update PR #249 title to `feat(248): harden init.sh substitution surface — sed → bash param expansion + input validation + gitignore default` via `gh pr edit 249 --title "..."`. Re-verify via `gh pr view 249 --json title` returning the new title (FR-010)

**Checkpoint**: User Stories 4 + 7 functional. ADR-038 published; constitution sed migrated; mcp-config.json disposition implemented; PR title set.

---

## Phase 7: User Story 5 (P2) — Placeholder contract closure verification

**Goal**: Verify `aod_template_assert_no_residual` runs against every substituted file post-init. (Implementation already wired in T020; this phase is verification + future-proofing.)

**Independent Test**: Run a deliberately-broken probe — temporarily add a file `tests/fixtures/probe-orphan.txt` containing `{{NON_CANONICAL}}` placeholder; run `init.sh`; verify init halts non-zero with the orphan placeholder named in stderr; remove the probe file before commit.

### Implementation for User Story 5

- [ ] T038 [US5] Manual verification (one-shot, not committed): create temp file `/tmp/orphan-probe.txt` with content `{{ORPHAN_FOR_PROBE}}`; copy into a fresh `init.sh` test environment; run `init.sh`; assert non-zero exit with message naming `{{ORPHAN_FOR_PROBE}}`. Record outcome in tasks-runlog.txt (Test-2 case 13 covers automated regression of this behavior; T038 is a one-time manual gating check)

**Checkpoint**: Placeholder contract closure verified. The residual scan IS the contract enforcer.

---

## Phase 8: Test Execution + CI Verification (Stream 5 finalization)

**Stream 5 — Test Infrastructure Finalization (3.0d total; T009-T013 already executed; this phase covers test-run + CI verification)** — covers all 7 user stories' regression protection.

**Goal**: All 4 pytest test files run green locally + CI matrix (macOS bash 3.2.57 + ubuntu bash 5.x) per FR-011. Day 5 slip-watch checkpoint passes by EOD Wed 2026-05-08.

**Independent Test**: `pytest tests/scripts/ -v` runs green on macOS locally; CI matrix shows green on both runners.

### Implementation for Stream 5 finalization

- [ ] T039 Run `pytest tests/scripts/test_init_sh_*.py -v` locally on macOS (bash 3.2.57 default). All 4 test files MUST pass. Capture run log to tasks-runlog.txt
- [ ] T040 Push all changes to `origin/248-substitution-surface-hardening`; verify GitHub Actions CI matrix (macos-latest + ubuntu-latest) runs the new tests and both runners report green. Wait for completion; capture run URLs to tasks-runlog.txt
- [ ] T041 Day 5 (Wed 2026-05-08) slip-watch checkpoint: if T040 has not recorded green CI matrix by EOD Day 5, escalate to PM for scope-cut adjudication. Possible scope cuts (priority order): (1) drop Test-2 corpus from ≥13 to 8 cases (keep all rejection-class cases; drop substitution-only cases); (2) defer Stream 4 ADR §Consequences benchmark numbers to a post-merge ADR amendment; (3) defer Test-7 post-merge re-scan documentation to /aod.deliver retrospective. **Hard floor**: do NOT drop Test-1 fixture-replay byte-comparison or Test-2 cases 1–6 substitution-semantics correctness

**Checkpoint**: All 7 tests in Regression Protection Plan pass on cross-platform CI matrix.

---

## Phase 9: Polish & Cross-Cutting Concerns

**Purpose**: Manual smoke test + pre-merge release-please verification.

- [ ] T042 [MANUAL] Test-6 manual smoke test on fresh checkout (gating action before marking PR ready): execute `quickstart.md` §Adversarial Smoke Test against `/tmp/tachi-smoke-test`. Verify: (a) `AT&T` literal substitution count > 0; (b) zero residual `{{KEY}}` placeholders; (c) `git status` shows `.aod/personalization.env` gitignored; (d) constitution byte-equality. If any fails, file CHANGES_REQUESTED and address regression
- [ ] T043 Pre-merge: re-verify PR #249 title is conventional-commits-formatted (R12 belt-and-suspenders): `gh pr view 249 --json title` MUST return exactly `feat(248): harden init.sh substitution surface — sed → bash param expansion + input validation + gitignore default`; if not, retitle via T037 path
- [ ] T044 [MANUAL] Verify dependency manifests unchanged (NFR-002): `git diff main..HEAD -- pyproject.toml requirements*.txt package.json` MUST be empty. If any diff exists, treat as a regression (likely from a stray `pip install` or `npm install` invocation during build); revert or escalate
- [ ] T045 [MANUAL] Verify schemas/finding.yaml unchanged (NFR-005): `git diff main..HEAD -- schemas/finding.yaml` MUST be empty. If any diff exists, treat as scope creep; remove

**Checkpoint**: F-1 implementation complete; all DoD items 1-12 satisfied. Ready for `/aod.deliver`.

---

## Phase 10: Post-Merge (Manual at /aod.deliver)

**Purpose**: Vulnerability log update + release-please verification + post-merge re-scan. These tasks execute at `/aod.deliver` time, NOT during build.

- [ ] T046 [MANUAL] Squash-merge PR #249 (closing operator action at `/aod.deliver`)
- [ ] T047 [MANUAL] Append 5 `REMEDIATED` events to `.security/vulnerabilities.jsonl` with merge SHA + ISO 8601 timestamp:
  - TACHI-VULN-6bc17fd01ac8 (HIGH)
  - TACHI-VULN-77f0519f9cfb (MEDIUM)
  - TACHI-VULN-bc67ca510ea9 (MEDIUM)
  - TACHI-VULN-30bbfd90959a (LOW)
  - TACHI-VULN-18127be5d214 (LOW)
  Each event uses the existing finding.yaml schema (NFR-005 — no schema bump)
- [ ] T048 [MANUAL] Verify release-please opens release PR within ~30s post-merge: `gh pr list --state open --search "release-please" --limit 3`; if empty, push empty release-marker commit (FR-010 R12 fallback): `git commit --allow-empty -m "feat(248): substitution surface hardening — release marker" && git push origin main`
- [ ] T049 [MANUAL] Run `/security` re-scan against main HEAD targeting the substitution surface (`scripts/init.sh`, `.gitignore`, `.aod/templates/constitution-*.md`, `contracts/personalization-schema.md`, `.claude/mcp-config.json` if Option a). Expected: zero new findings; 5 REMEDIATED events visible in `.security/vulnerabilities.jsonl` (Test-7)
- [ ] T050 [MANUAL] [PM-controlled, NOT a DoD gate] Public Visibility Action (within 5 business days of release-please PR merge per Team-Lead Pass 1 M-3): paste the comment template on Daniel Wood's 2026-05-02 LinkedIn thread linking the merge commit + ADR-038 + CHANGELOG entry + 5 REMEDIATED events. Posting is at user discretion; NOT decoupled from F-248 closure

**Checkpoint**: F-1 fully delivered; vulnerability event log updated; release published; public posture trail visible.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies; can start Day 1.
- **Foundational (Phase 2)**: Depends on Setup; T005 internal-tooling search outcome BLOCKS T033; T006-T007 constitution templates BLOCK T032; T008 baseline benchmark BLOCKS T021 delta calculation.
- **User Story Phases (Phase 3-7)**: Phase 3 (US1+6 substitution) is the critical path; Phases 4 (US2 input validation), 5 (US3 posture defaults), and 6 (US4+7 ADR/release) advance in parallel after Foundational completes.
- **Test Execution (Phase 8)**: Depends on Phase 3 (substitution swap) being complete + T014 baseline regeneration.
- **Polish (Phase 9)**: Depends on Phases 3-8 completion.
- **Post-Merge (Phase 10)**: Executes only at `/aod.deliver` after all PR review approvals.

### User Story Dependencies (cross-story)

- **US1 (P1)**: Independent; can start after Foundational.
- **US2 (P1)**: Independent of US1; can start after Foundational. Sequencing constraint: T023 (source helper in init.sh) MUST come after T015 (template-substitute source line at top), but T022 (helper file authored) is independent.
- **US3 (P1)**: Independent of US1+US2.
- **US4 (P2)**: T032 (constitution sed migration) depends on T006+T007 (templates authored). T034 (ADR-038 Proposed) is independent. T035 (ADR §Consequences benchmark) depends on T021 (post-swap benchmark).
- **US5 (P2)**: T038 manual verification depends on T020 (residual scan wired).
- **US6 (P1)**: Spans US1+US2+US4 (defense-in-depth chain). No standalone tasks; verified by Phase 8 test execution.
- **US7 (P2)**: T037 PR retitle is independent; verifies at delivery time.

### Within Each User Story

- Tests written BEFORE implementation (T009-T013 land BEFORE T015-T021 substitution swap, per Constitution VI test-first principle for core features).
- Models/data: N/A (no new data entities; canonical-12 array is locked).
- Services: helper functions (`aod_init_read_validated`) before integration (`init.sh` wires the helper).
- Implementation before integration: substitute function call before residual scan.

### Parallel Opportunities

- T002, T003, T004 in Phase 1 — different files, parallel.
- T006, T007 in Phase 2 — different files, parallel.
- T009, T010, T011, T012, T013 in Phase 3 (test authorship) — different test files, parallel.
- T022 in Phase 4 — independent file; parallel with anything in Phase 3 implementation that doesn't touch init.sh source line.
- T029, T030 in Phase 5 — different files (contracts/personalization-schema.md vs CHANGELOG.md), parallel.
- T034 (ADR Proposed) in Phase 6 — independent file; parallel with anything else.
- All Phase 4-6 user stories can advance in parallel after Foundational (Phase 2) completes.

---

## Parallel Example: Phase 3 Test Authorship (Stream 5 leading edge)

```bash
# Launch all 4 test files + regen script in parallel (different files, no dependencies):
Task: "T009 [P] [US1] Author tests/scripts/test_init_sh_substitution.py (Test-1 fixture-replay byte-comparison)"
Task: "T010 [P] [US1] Author tests/scripts/test_init_sh_adversarial.py (Test-2 ≥13 adversarial inputs)"
Task: "T011 [P] [US1] Author tests/scripts/test_init_sh_constitution.py (Test-4 byte-compare)"
Task: "T012 [P] [US1] Author tests/scripts/test_init_sh_self_delete.py (Test-5' self-delete preservation)"
Task: "T013 [P] [US1] Author tests/fixtures/regenerate-baseline.sh script"
```

## Parallel Example: Phases 4 + 5 + 6 (post-Foundational)

```bash
# Once Foundational completes, three streams advance in parallel:
# Stream 2 (US2) input validation:
Task: "T022 [P] [US2] Author .aod/scripts/bash/init-input.sh helper"
# Stream 3 (US3) posture defaults:
Task: "T029 [P] [US3] Update contracts/personalization-schema.md"
Task: "T030 [P] [US3] Add CHANGELOG.md entry with migration command"
# Stream 4 (US4+7) ADR + release:
Task: "T034 [P] [US4] Author ADR-038 Proposed"
```

---

## Implementation Strategy

### MVP Scope (Days 1-5)

1. **Day 1**: Phase 1 (Setup) + Phase 2 (Foundational T005-T008) + Phase 3 test authorship (T009-T013).
2. **Day 2-3**: Phase 3 implementation (T015-T021 — Stream 1 substitution adoption).
3. **Day 3 parallel**: Phases 4, 5, 6 advance in parallel (Streams 2+3+4).
4. **Day 4**: T014 baseline regeneration; Phase 8 test execution (T039-T040).
5. **Day 5 EOD**: Slip-watch checkpoint (T041) — verify CI matrix green; escalate if not.

### Critical Path

Stream 1 (T015-T021 substitution adoption) → T014 (baseline regeneration with post-swap output) → T039-T040 (test execution + CI verification) → T036 (ADR Accepted post-architect-review) → T042 (manual smoke test) → ready for `/aod.deliver`.

### Incremental Delivery

The feature is single-PR by design (PRD §Deliverable). Incremental commits MAY land within the feature branch as work progresses, but the squash-merge to `main` is the atomic delivery unit.

### Solo-Agent Sequencing

Per PRD §Timeline single-agent serial assumption (8d active is realistic for one `senior-backend-engineer`). Two-agent parallel could compress to 5d but coordination overhead on single-PR squash sequencing is net wash.

---

## Notes

- [P] tasks operate on different files with no dependencies on incomplete tasks.
- [Story] label maps tasks to user stories US1..US7 (per spec.md).
- [MANUAL] tasks are gating actions executed by the closing operator at `/aod.deliver`, NOT during build.
- Per Constitution VI: tests authored BEFORE implementation; verify failures pre-implementation; verify passes post-implementation.
- Commit after each logical group of tasks; use conventional-commit prefix `feat(248):` to ensure release-please recognizes the feature work.
- DoD checklist (per spec.md §Definition of Done) covers 14 items + the [MANUAL] post-merge gates; verify each at `/aod.deliver`.
- **Slip-watch**: Day 5 EOD checkpoint (T041) is the gate for scope-cut adjudication.
- **Hard ceiling**: Day 10 (Fri 2026-05-15) per PRD Timeline.
