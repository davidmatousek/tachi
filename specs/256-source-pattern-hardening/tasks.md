---
description: "Task list for F-2 Source-Pattern Hardening (BLP-02 Wave 2)"
triad:
  pm_signoff:
    agent: product-manager
    date: 2026-05-04
    status: APPROVED
    notes: "All 9 FRs + 15 SCs + 8 USs + 6 Q-* adjudications cleanly traced to T001..T062. Scope creep checks pass (no F-1 redefinition, no finding.yaml schema changes, no JSON/TOML alternatives). F-1 contract amendment ripple fully threaded (T026 tests + T032 implementation + T053 CHANGELOG migration guidance). MVP split-contingency scope correctly named in §Implementation Strategy (default = single PR). Manual flags correctly placed (T044 automated; T057-T062 [MANUAL]). 62-task count consistent with F-1's 50 + library/site/ripple expansion. No changes required. Full review: .aod/results/product-manager-tasks.md."
  architect_signoff:
    agent: architect
    date: 2026-05-04
    status: APPROVED
    notes: "All 13 architectural correctness criteria pass. T010 7-step flow correct; test-first ordering enforced (T009→T010, T014→T015-18, T020-21→T022-23, T025-26→T027-32, T034→T035, T037-38→T039); strict reorder T032+T031 in F-2's PR; H-3 function name corrected; H-4 strict :558 semantic equivalence preserved; B-3 here-string mechanism named; ADR-040 dual-commit T042→T054; Stream 4 watchdog includes L-1 trap + Q-3 footgun + AOD_FETCH_TIMEOUT regex; pytest-via-subprocess + session-scoped fixture per F-250 ADR-039; bash 3.2 constraint explicit; stream dependencies + critical path explicit; Day-5 (T044) + Day-8 (T048) checkpoints named with all GREEN-LIGHT conditions. 3 informational observations (non-blocking). Full review: .aod/results/architect-tasks.md."
  techlead_signoff:
    agent: team-lead
    date: 2026-05-04
    status: APPROVED_WITH_CONCERNS
    notes: "62 tasks across 11 phases; timeline math closes 8.75d single-agent-interleaved within 9.5d active (0.75d headroom). T044 Day-5 slip-watch verbatim with 4 conditions + 3-tier escalation ladder. T048 Day-8 secondary checkpoint verbatim with soak-day fallback. Buffer floor preserved (15.8% on 9.5d > 12.5% floor). MVP scope (Q-1 split contingency) correctly identifies Phases 1-5 + 9 with 3-4d F-2b recovery. Critical path explicit. All test-first orderings preserved (Constitution VI). [MANUAL] tags correct. 5 informational observations (non-blocking): (1) reabsorption authority chain not restated in tasks.md (governed by plan.md); (2) per-task agent ownership implicit (PRD §Resources mandates senior-backend-engineer cadence); (3) conversion-lever-not-buffer-expansion not restated; (4) Day-4 tester fixture-design review not explicit task; (5) two-agent parallel escape hatch not in tasks.md. NO VETO. Full review: .aod/results/team-lead-tasks.md."
---

# Tasks: Source-Pattern Hardening (BLP-02 Wave 2)

**Input**: Design documents from `/specs/256-source-pattern-hardening/`
**Prerequisites**: plan.md (✓ PM + Architect APPROVED), spec.md (✓ PM APPROVED), research.md, data-model.md, contracts/{config-load-helper-contract.md, stack-pack-defaults-schema.md}, quickstart.md

**Tests**: REQUIRED — Per spec FR-009 + Regression Protection Plan, this feature requires 5 pytest test files + adversarial fixture corpus (Stream 5). Test tasks are NOT optional for F-2.

**Organization**: Tasks are grouped by user story (US-256-1..US-256-8) with cross-references to plan.md streams (Stream 1..Stream 5). The 8 user stories map onto 5 implementation streams; overlapping work (e.g., Stream 1 library bring-up serves US-2 + US-5 + foundation for US-1/US-3/US-8) is tagged with the dominant user story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies on incomplete tasks)
- **[Story]**: Maps task to user story (US1..US8)
- **[MANUAL]**: Cannot be automated; closing operator action at `/aod.deliver`
- File paths are absolute or rooted at repo root

## Path Conventions

- Source bash scripts: `.aod/scripts/bash/template-config-load.sh` (NEW); `scripts/init.sh` (modified); `.aod/scripts/bash/template-git.sh` (modified); `.aod/scripts/bash/template-substitute.sh` (modified); `.aod/scripts/bash/init-input.sh` (F-1 amendment)
- Contracts: `contracts/stack-pack-defaults-schema.md` (NEW)
- ADR: `docs/architecture/02_ADRs/ADR-040-config-file-parsing-hardening.md` (NEW)
- Tests: `tests/scripts/test_template_*.py` (NEW); `tests/scripts/test_init_sh_defaults_env.py` (NEW); `tests/scripts/conftest.py` (modified)
- Fixtures: `tests/fixtures/config-load/{valid,adversarial}/` (NEW); `tests/fixtures/regenerate-config-load-baseline.sh` (NEW)

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Workspace verification and directory scaffolding before implementation begins.

- [X] T001 Verify feature branch + draft PR state: `git branch --show-current` returns `256-source-pattern-hardening`; `gh pr view 257` returns draft PR with title `feat(256): harden source-pattern surface — bash source/eval → KV parser + clone timeout`; spec.md and plan.md frontmatter contain required sign-offs (PM + Architect)
- [X] T002 [P] Create `tests/fixtures/config-load/valid/` directory: `mkdir -p tests/fixtures/config-load/valid/`
- [X] T003 [P] Create `tests/fixtures/config-load/adversarial/` directory: `mkdir -p tests/fixtures/config-load/adversarial/`
- [X] T004 [P] Snapshot dependency manifests for NFR-002 verification: capture `git show HEAD:pyproject.toml` and `git show HEAD:requirements*.txt` (and any `package.json` if present) baselines; record SHA-256 of each in `specs/256-source-pattern-hardening/tasks-runlog.txt` for end-of-build comparison

**Checkpoint**: Workspace is clean and ready for library bring-up.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Decisions and artifacts that MUST be complete before any user-story work can proceed. Day-1 baseline benchmark, contract authoring, and stack-pack schema land here.

**CRITICAL**: T005 baseline benchmark gates the post-swap measurement in T013 (Stream 1 Day-1 perf comparison). T006-T007 contract authoring is a Stream 1 deliverable that the library implementation (Phase 3) and Site A refactor (Phase 4) depend on for the canonical key set.

- [X] T005 Stream 1 Day-1 baseline benchmark (NFR-004 + SC-010): from a snapshot of pre-merge state, time the existing `source` paths against the canonical fixture set (`stacks/nextjs-supabase/defaults.env`, `stacks/fastapi-react/defaults.env`, recorded-valid `.aod/aod-kit-version`, recorded-valid `.aod/personalization.env`). Methodology per SC-010: 100 invocations × 4 fixtures × p50/p95; per-file delta (NOT aggregate); warm-cache + cold-cache reported separately. Capture timings to tasks-runlog.txt for ADR-040 §Consequences (Phase 9)
- [X] T006 [P] Move and finalize `contracts/stack-pack-defaults-schema.md` (NEW lockstep contract for stack-pack `defaults.env` files): currently authored in `specs/256-source-pattern-hardening/contracts/`; move to repo-root `contracts/` directory at Stream 1 commit time. Documents the canonical 5 keys (`TECH_STACK`, `TECH_STACK_DATABASE`, `TECH_STACK_VECTOR`, `TECH_STACK_AUTH`, `CLOUD_PROVIDER`), value-shape rules, and lockstep update procedure (per FR-002 + plan §Stream 1 deliverables)
- [X] T007 [P] Verify `contracts/config-load-helper-contract.md` is complete (specs-internal contract for `aod_template_load_kv_file` API surface); reviewers reference this during Phase 3 implementation review
- [X] T008 [P] Append CHANGELOG.md placeholder entry under v4.x heading for F-2 changes (final wording lands in T053 once implementation is complete; the placeholder reserves the space and ensures the entry is not forgotten)

**Checkpoint**: Baseline benchmark recorded; contracts ready; CHANGELOG slot reserved. Library bring-up can now begin.

---

## Phase 3: User Story 2 + 5 (P1) — Library bring-up (Stream 1, critical path)

**Stream 1 — Library Bring-Up (Critical Path, 2.5d per H-1)** — covers US-256-2 (maintainer adding new config-file site) and the foundation for US-256-5 (security reviewer audit), US-256-1, US-256-3, US-256-7, US-256-8.

**Goal**: `aod_template_load_kv_file` library authored, unit tests passing on macOS bash 3.2.57, Day-1 perf benchmark recorded, Day-5 slip-watch GREEN-LIGHT condition 1 met (≥17/17 cases pass).

**Independent Test**: Run `pytest tests/scripts/test_template_config_load_unit.py -v` on macOS local — at least 17 of 27 cases pass; the function loads valid KV files into caller scope; rejects malformed lines exit 8; rejects unknown keys exit 8 when whitelist provided; supports `<key_case>=lower` mode; defensive identifier check fires on invalid `${var_prefix}${KEY}`.

### Tests for Library Bring-Up (Stream 5 first pass — authored before library implementation per Constitution VI test-first principle)

**NOTE: Tests written FIRST per Constitution VI. Test file lands before library implementation; tests fail against an empty/missing library; tests pass after T010-T012 implementation.**

- [X] T009 [P] [US2] Author `tests/scripts/test_template_config_load_unit.py` first pass with all 27 test cases per FR-009 AC-9.2:
  Cases 1-5 valid KV (no whitelist) — KEY=value, KEY="quoted", KEY='single-quoted', KEY=path/with/slashes, KEY=email@example.com;
  Case 6 valid KV with whitelist — all keys present;
  Cases 7-15 invalid lines — command substitution `KEY="$(rm -rf /)"`, unbalanced quote, backtick, embedded `$`, KEY with lowercase (in upper mode), missing whitelisted key, line with only KEY no `=`, embedded literal newline, embedded NUL;
  Case 16 bare `KEY=` empty unquoted (B-1) PASS;
  Case 17 defensive identifier check — invalid `<var_prefix>` rejected (H-1);
  Case 18 empty-value PASS (B-1);
  Cases 19-23 B-3 cases — trailing-newline / no-trailing-newline / CRLF / leading-whitespace / blank-line-followed-by-content;
  Case 24 missing-arg behavior (`<path>` empty);
  Case 25 file-absent behavior;
  Case 26 `<key_case>=lower` regex variant — accepts `version=4.28.0`, rejects `VERSION=4.28.0`;
  Case 27 `<key_case>=mixed` rejection (per Q-2.5).
  Use `subprocess.run` to invoke `bash -c 'source .aod/scripts/bash/template-config-load.sh && aod_template_load_kv_file ...; echo "EXIT=$?"; declare -p ${var_prefix}${KEY}'`. Process substitution `< <(printf ...)` REQUIRED (pipes cause subshell scope loss per F-1 R-1 lesson). First parametrized test MUST be `case_0_canary_positive` to detect pipe-regression early.

### Implementation for Library Bring-Up

- [X] T010 [US2] Author `.aod/scripts/bash/template-config-load.sh` — the canonical config-load primitive. Implement the function `aod_template_load_kv_file <path> <var_prefix> [<allowed_keys_array_name>] [<key_case>]` per FR-001:
  Step 1 argument validation (path / var_prefix regex / key_case enum);
  Step 2 file existence check (return 3 with error);
  Step 3 single `cat $path` into in-memory buffer (TOCTOU mitigation);
  Step 4 per-line iteration via `while IFS= read -r line; do ...; done <<< "$content"` with CRLF strip + leading-whitespace strip (path-a per B-3);
  Step 5 per-line regex validation (mode-dependent — `[A-Z_][A-Z_0-9]*=...` for upper, `[a-z_][a-z_0-9]*=...` for lower; value class with `*` quantifier per B-1);
  Step 6 whitelist enforcement (during pass for unknown-key abort + post-pass completeness check for missing-key);
  Step 7 defensive identifier check (`^[A-Za-z_][A-Za-z_0-9]*$` on `${var_prefix}${KEY}` per H-1) + `printf -v` assignment (NOT eval; quote stripping for surrounding quotes);
  Internal `eval` carve-out: ONE invocation `eval "local keys=(\"\${${allowed_keys_array_name}[@]}\")"` for bash 3.2 indirect array access (audit-clarity per ADR-040 Decision Item 7).
  Bash 3.2 verified: no associative arrays, no `mapfile`, no `${var,,}`, scalar `${!var}` only.
- [X] T011 [US2] Verify T010 implementation: run `pytest tests/scripts/test_template_config_load_unit.py -v` on macOS local (bash 3.2.57). All 27 cases MUST pass. If fewer than 17 pass at this point, escalate per Day-5 slip-watch rule
- [X] T012 [US2] Verify T010 implementation on Linux: run the same pytest invocation in CI (or local `bash --version` ≥ 4.0 environment). All 27 cases MUST pass on Linux as well

### Library Day-1 Benchmark

- [X] T013 [US2] Stream 1 Day-1 post-implementation benchmark (NFR-004 + SC-010): time `aod_template_load_kv_file` against the canonical fixture set captured in T005. Same methodology (100 inv × 4 fixtures × p50/p95; per-file delta; warm/cold cache). Record numbers in tasks-runlog.txt for ADR-040 §Consequences (T053 finalizes the entry). Apply NFR-004 escalation rules:
  ≤5% delta — proceed (no PRD update);
  5-25% delta — proceed (loosen NFR-004 to 25% in ADR-040);
  25-50% delta — Team-Lead approval required + security tradeoff rationale in ADR-040;
  >50% delta — escalate to PM for re-scope (Q-5 Option c levers)

**Checkpoint**: Library is functional and unit-tested on both bash 3.2 + bash 4+; benchmark numbers staged. Stream 2 (refactor sites) can begin.

---

## Phase 4: User Story 1 (P1) — Site A defaults.env refactor (Stream 2.A, 0.5d)

**Stream 2 Site A** — covers US-256-1 (adopter running init.sh against tampered defaults.env). Closes TACHI-VULN-6f5a95085056 (HIGH).

**Goal**: `init.sh:106` no longer sources `defaults.env` as bash; calls `aod_template_load_kv_file` with `STACK_PACK_ALLOWED_KEYS` whitelist; downstream code in `init.sh` migrated to read `STACK_*`-prefixed variables.

**Independent Test**: Run `init.sh` against `stacks/nextjs-supabase` (valid pack) — verify `STACK_TECH_STACK=nextjs` etc. are populated and init proceeds. Run against fixture `stacks/malicious-pack/defaults.env` containing `CUSTOM_HOOK="$(touch /tmp/F-256-pwned)"` — verify init exits 8 and `/tmp/F-256-pwned` is never created.

### Tests for Site A (Stream 5)

- [X] T014 [P] [US1] Author `tests/scripts/test_init_sh_defaults_env.py` (Test-4) — pytest test file for init.sh end-to-end with refactored Site A:
  Case 1 each shipped stack pack (`nextjs-supabase`, `fastapi-react`) loads cleanly on macOS + Linux — Day-5 slip-watch GREEN-LIGHT condition 2;
  Case 2 malicious-pack fixture (`stacks/malicious-pack/defaults.env` with `CUSTOM_HOOK="$(touch /tmp/F-256-pwned)"`) rejected exit 8 + `/tmp/F-256-pwned` never created;
  Case 3 missing-key fixture (pack omitting `CLOUD_PROVIDER`) rejected exit 8 with missing-key error.
  Use `subprocess.run` with env var inputs (PROJECT_NAME=tachi etc.) for non-interactive testability.

### Implementation for Site A

- [X] T015 [US1] Add library source preamble at top of `scripts/init.sh` alongside existing `template-substitute.sh` + `init-input.sh` sources:
  ```bash
  if [ -f ".aod/scripts/bash/template-config-load.sh" ]; then
    # shellcheck disable=SC1091
    source .aod/scripts/bash/template-config-load.sh
  else
    echo -e "${RED}ERROR: .aod/scripts/bash/template-config-load.sh not found${NC}" >&2
    exit 1
  fi
  ```
- [X] T016 [US1] Replace `source "stacks/$SELECTED_PACK/defaults.env"` at `scripts/init.sh:106` with the library invocation:
  ```bash
  STACK_PACK_ALLOWED_KEYS=(TECH_STACK TECH_STACK_DATABASE TECH_STACK_VECTOR TECH_STACK_AUTH CLOUD_PROVIDER)
  aod_template_load_kv_file "stacks/$SELECTED_PACK/defaults.env" "STACK_" STACK_PACK_ALLOWED_KEYS
  ```
- [X] T017 [US1] Rename pass downstream of T016: scan `scripts/init.sh` for direct reads of `$TECH_STACK`, `$TECH_STACK_DATABASE`, `$TECH_STACK_VECTOR`, `$TECH_STACK_AUTH`, `$CLOUD_PROVIDER` post-line-106 and migrate to `$STACK_TECH_STACK` etc. (the `STACK_` prefix is REQUIRED — disambiguates from canonical-12 personalization values that also flow through caller scope)
- [X] T018 [US1] Author `tests/fixtures/config-load/adversarial/malicious-pack-defaults.env` test fixture file containing `CUSTOM_HOOK="$(touch /tmp/F-256-pwned)"` plus the canonical 5 keys with valid values — used by T014 case 2. File MUST carry `# DO NOT SOURCE — malicious test fixture` header per L-2
- [X] T019 [US1] Run `pytest tests/scripts/test_init_sh_defaults_env.py -v` on macOS + Linux. All 3 cases MUST pass

**Checkpoint**: Site A refactor complete + green. TACHI-VULN-6f5a95085056 closed. Day-5 slip-watch GREEN-LIGHT condition 2 met.

---

## Phase 5: User Story 3 (P1) — Site B aod-kit-version refactor (Stream 2.B, 0.75d per H-3)

**Stream 2 Site B** — covers US-256-3 (adopter running /aod.update against malformed aod-kit-version). Closes TACHI-VULN-bf5496e9fcdf (HIGH).

**Goal**: `template-git.sh:561` (`aod_template_read_version_file`) AND `:485-515` (`aod_template_write_version_file` inner round-trip block at `:501`) no longer source `$path` / `$tmp_path` as bash; both call `aod_template_load_kv_file ... lower` (no whitelist; lowercase mode per Q-2.5). Existing per-field validators at `template-git.sh:568+` run unchanged after the load.

**Independent Test**: Place fixture `.aod/aod-kit-version` containing `version='1.0'; touch /tmp/F-256-pwned` and call `aod_template_read_version_file` — verify exit 8 and `/tmp/F-256-pwned` never created. Call against valid lowercase fixture (`version='4.28.0'`, `sha=abc123`, `updated_at=2026-05-04T12:00:00Z`, `upstream_url=...`, `manifest_sha256=...`) — verify load succeeds and per-field validators run.

### Tests for Site B (Stream 5)

- [X] T020 [P] [US3] Author Test-2 Site B section in `tests/scripts/test_template_config_load_integration.py` (full file authored at T028 — Site B parametrize cases land here):
  Case Site-B-malformed `version='1.0'; touch /tmp/F-256-pwned` → exit 8 + no /tmp file;
  Case Site-B-valid lowercase (5 fields) → exit 0 + per-field validators run;
  Case Site-B-bare-version `version=` empty unquoted → exit 0 (B-1 contract preserved);
  Case Site-B-uppercase `VERSION=4.28.0` → exit 8 (lowercase mode rejects uppercase keys).
  Author `tests/fixtures/config-load/adversarial/aod-kit-version-malformed` and `tests/fixtures/config-load/valid/aod-kit-version-valid` fixtures
- [X] T021 [P] [US3] Author Test-3 H-3 round-trip case in `tests/scripts/test_template_git_clone_timeout.py` (full file authored at T037 — Site B-roundtrip parametrize lands here as a parametrize case):
  Writer round-trip (per H-3): construct field values, invoke `aod_template_write_version_file`, observe inner round-trip block at `:485-515` (`:501`) succeeds via `aod_template_load_kv_file "$tmp_path" "" "" lower`; assert post-load missing-field detection runs unchanged.

### Implementation for Site B

- [X] T022 [US3] Modify `aod_template_read_version_file` in `.aod/scripts/bash/template-git.sh` (function header at `:544`): replace `source "$path" || ...` at `:561` with:
  ```bash
  aod_template_load_kv_file "$path" "" "" lower || {
      local rc=$?
      echo "[aod] ERROR: failed to parse version file: $path (exit $rc)" >&2
      return 3
  }
  ```
  Existing per-field regex validators at `template-git.sh:568+` are NOT modified — they run AFTER the load and provide stronger field-shape checking
- [X] T023 [US3] Modify `aod_template_write_version_file:485-515` in `.aod/scripts/bash/template-git.sh` (per H-3 correction — this is the actual function name; v1.0 PRD's `aod_template_validate_version_content` reference was incorrect): replace `source "$tmp_path" 2>/dev/null` at `:501` with:
  ```bash
  local validate_rc=0
  aod_template_load_kv_file "$tmp_path" "" "" lower || validate_rc=$?
  ```
  Existing post-load missing-field detection at `:501+` runs unchanged
- [X] T024 [US3] Run T020 + T021 cases on macOS + Linux. All cases MUST pass

**Checkpoint**: Site B refactor complete + green. TACHI-VULN-bf5496e9fcdf closed. H-3 round-trip preserved.

---

## Phase 6: User Story 7 + 5 (P2/P1) — Site C eval removal + writer escape pass removal (Stream 2.C, 0.5d)

**Stream 2 Site C** — covers US-256-7 (maintainer reviewing template-substitute.sh for eval removal) and US-256-5 (security reviewer audit). Closes TACHI-VULN-9a7512071b4a (MEDIUM).

**Goal**: All four `eval` invocations at `template-substitute.sh:217, :249, :536, :558` replaced with bash 3.2-compatible alternatives; writer escape pass at `:566-571` removed; F-1 `aod_init_read_validated` amended to additionally reject `$`, `\`, backtick at prompt boundary (per B-2 Path R-2).

**Independent Test**: Run `grep -c '\beval\b' .aod/scripts/bash/template-substitute.sh` — expect `0`. Run F-1's existing prompt validator tests with new metachar rejection cases — expect updated rejection error messages. Verify writer-reader round-trip is preserved without escape pass (write a `PROJECT_NAME` value through `aod_init_read_validated` → `aod_template_init_personalization` → `aod_template_load_personalization_env`; observe identity).

### Tests for Site C (Stream 5)

- [X] T025 [P] [US7] Author `tests/scripts/test_template_substitute_lint_no_eval.py` (Test-5) — eval removal verification + future-PR-blocker lint:
  Case 1 `subprocess.run(['grep', '-c', '\\beval\\b', '.aod/scripts/bash/template-substitute.sh'])` returns `0`;
  Case 2 (future-PR-blocker semantics) — comment in test explains that this test will fail if a future PR introduces a new `eval` to that file, blocking review at the canonical-pattern rule.
  Note: this is NOT applied to `template-config-load.sh` (the library has the audit-clarity carve-out per ADR-040 Decision Item 7).
- [X] T026 [P] [US7] Augment F-1's existing `tests/scripts/test_init_input_unit.py` (or equivalent F-1 prompt validator test) with parametrize cases for the new metachar rejection (rejecting `$`, `\`, backtick at prompt boundary):
  Case `$` injection (e.g., `my$project`) → `[init] Input rejected: metachar ($, \, backtick) not allowed; please re-enter.`;
  Case `\` injection (e.g., `proj\name`) → same rejection;
  Case backtick injection → same rejection.
  These complement F-1's existing newline / NUL / control / over-length rejection cases (CHANGELOG migration guidance in T053)

### Implementation for Site C

- [X] T027 [US7] Modify `.aod/scripts/bash/template-substitute.sh:217` — replace `eval "val=\"\${$key:-}\""` (read-side dynamic lookup with `:-` default) with:
  ```bash
  local var_name="$key"
  local val="${!var_name:-}"
  ```
- [X] T028 [US7] Modify `.aod/scripts/bash/template-substitute.sh:249` — replace `eval "AOD_PERSONALIZATION_${key}=\"\$val\""` (write-side dynamic assignment) with:
  ```bash
  printf -v "AOD_PERSONALIZATION_${key}" '%s' "$val"
  ```
- [X] T029 [US7] Modify `.aod/scripts/bash/template-substitute.sh:536` — replace `eval "val=\"\${$key:-}\""` (second read-side, with `:-` default) with the same `${!var_name:-}` pattern as T027
- [X] T030 [US7] Modify `.aod/scripts/bash/template-substitute.sh:558` — replace `eval "val=\"\${$key}\""` (third read-side, NO `:-` default) with **strict semantic equivalent** per H-4:
  ```bash
  local var_name="$key"
  local val="${!var_name}"   # No :- default — matches existing :558 semantics; aod_template_init_personalization validates non-empty key at :535-540 before reaching :558
  ```
- [X] T031 [US7] Modify `.aod/scripts/bash/template-substitute.sh:566-571` — REMOVE the four-line escape block (`\\`/`"`/`$`/backtick escape pass in writer). Replace with direct emission:
  ```bash
  printf '%s="%s"\n' "$key" "$val" >> "$tmp_path"
  ```
- [X] T032 [US7] Modify `.aod/scripts/bash/init-input.sh` — extend `aod_init_read_validated` validator to additionally reject `$`, `\`, backtick at prompt boundary (per B-2 Path R-2 + F-1 contract amendment IN F-2's PR):
  Insert after existing newline / NUL / control / over-length checks (in the same `while (( attempt < 3 ))` loop):
  ```bash
  elif [[ "$answer" =~ [\$\\\`] ]]; then reason="metachar (\$, \\, backtick) not allowed"
  ```
- [X] T033 [US7] Run T025 + T026 cases on macOS + Linux. All cases MUST pass. Run `grep -c '\beval\b' .aod/scripts/bash/template-substitute.sh` and assert it returns `0`

**Checkpoint**: Site C refactor complete + green. TACHI-VULN-9a7512071b4a closed. F-1 contract amendment ripple landed.

---

## Phase 7: User Story 8 (P2) — Site D TOCTOU collapse (Stream 2.D, 0.75-1.0d)

**Stream 2 Site D** — covers US-256-8 (adopter in TOCTOU race-prone environment). Closes TACHI-VULN-4dc6cf8f88ea (MEDIUM).

**Goal**: `aod_template_load_personalization_env` body at `template-substitute.sh:162-209` collapsed from 47 lines of subshell-validate-then-caller-source to ~7 lines of library delegation; behavior preserved (missing-path / file-absent / validation-failure / missing-key detection / caller-scope variable population all preserved).

**Independent Test**: Verify `strace -e openat` (Linux) traces a single `openat(...)` of the personalization.env path within the function body. Run a fixture race-test that swaps `.aod/personalization.env` content via a forked process between two operations — verify caller-scope values match the file's content **at the moment of `cat`**, not the post-swap content.

### Tests for Site D (Stream 5)

- [X] T034 [P] [US8] Author Test-2 Site D section in `tests/scripts/test_template_config_load_integration.py` (Site D parametrize cases):
  Case Site-D-collapsed-body — invoke the post-F-2 `aod_template_load_personalization_env` against a valid `.aod/personalization.env` fixture; assert caller-scope `AOD_PERSONALIZATION_PROJECT_NAME=...` etc. populated;
  Case Site-D-toctou-residual (per H-2 + M-1) — fork a process that swaps the file between cat and assignment; assert caller-scope values match pre-swap content (file is opened once); test uses bash 3.2-compatible mechanism (background `&` + `sleep 0.01` + file rewrite);
  Case Site-D-missing-path — exit 1 (unchanged);
  Case Site-D-file-absent — exit 3 (unchanged via library);
  Case Site-D-validation-failure (embedded NUL) — exit 8 (unchanged; regex implicitly excludes NUL);
  Case Site-D-missing-key — exit 8 with missing-key message (unchanged behavior via whitelist mechanism)

### Implementation for Site D

- [X] T035 [US8] Modify `.aod/scripts/bash/template-substitute.sh:162-209` — REPLACE the entire 47-line `aod_template_load_personalization_env` body with ~7 lines of library delegation:
  ```bash
  aod_template_load_personalization_env() {
      local path="${1:-}"
      if [ -z "$path" ]; then
          echo "[aod] ERROR: aod_template_load_personalization_env requires <path>" >&2
          return 1
      fi
      aod_template_load_kv_file "$path" "AOD_PERSONALIZATION_" AOD_CANONICAL_PLACEHOLDERS
  }
  ```
  Behavior preserved per FR-005: missing-path → 1 (unchanged); file-absent → 3 (unchanged via library); validation-failure → 8 (regex implicitly excludes newline + NUL); missing-key detection → 8 (via whitelist mechanism); `AOD_PERSONALIZATION_<KEY>` populated (unchanged).
- [X] T036 [US8] Run T034 cases on macOS + Linux. All cases MUST pass. Verify F-1's regression test suite (`tests/scripts/test_init_sh_*.py` from F-1) still passes — no regressions in the personalization-snapshot round-trip

**Checkpoint**: Site D refactor complete + green. TACHI-VULN-4dc6cf8f88ea closed. TOCTOU race window collapsed per H-2 framing.

---

## Phase 8: User Story 4 (P2) — Clone timeout + watchdog SIGINT trap (Stream 4, 1.0d)

**Stream 4 — Clone Timeout** (independent of Streams 1-3; can advance in parallel) — covers US-256-4 (adopter running /aod.update with hanging upstream). Closes TACHI-VULN-851fd6a21ba9 (LOW).

**Goal**: `aod_template_fetch_upstream` (`.aod/scripts/bash/template-git.sh:102-104`) wraps `git clone --depth=1 ...` with a portable bash background+kill watchdog. `AOD_FETCH_TIMEOUT` env var (default 60, positive integer required). SIGINT/SIGTERM/EXIT trap cleans up watchdog if outer script interrupted (per L-1).

**Independent Test**: Spin up a TCP listener that accepts but never responds (test fixture: Python `socket.bind()`); point `aod_template_fetch_upstream` at it with `AOD_FETCH_TIMEOUT=3`; verify exit 9 within ~3-4s and `destdir` removed. Re-run with `AOD_FETCH_TIMEOUT=10`; verify exit 9 at ~10s. Set `AOD_FETCH_TIMEOUT=0`; verify exit 1 (Q-3 footgun).

### Tests for Stream 4 (Stream 5)

- [X] T037 [P] [US4] Author `tests/scripts/test_template_git_clone_timeout.py` (Test-3) — clone timeout behavior:
  Case 1 hanging fixture with AOD_FETCH_TIMEOUT=3 → exit 9 within ~3-4s + destdir removed + stderr error;
  Case 2 same hanging fixture with AOD_FETCH_TIMEOUT=10 → exit 9 at ~10s, not 60s;
  Case 3 AOD_FETCH_TIMEOUT=0 → exit 1 with Q-3 footgun error message;
  Case 4 AOD_FETCH_TIMEOUT=abc → exit 1;
  Case 5 AOD_FETCH_TIMEOUT=01 (leading zero) → exit 1 (regex `^[1-9][0-9]*$` rejects);
  Case 6 fast clone (succeeds normally) with AOD_FETCH_TIMEOUT=60 → exit 0 + no zombie watchdog process.
  Use the session-scoped `hanging_upstream` fixture (T038)
- [X] T038 [P] [US4] Modify `tests/scripts/conftest.py` — add session-scoped `hanging_upstream` pytest fixture (per M-3 + F-250 ADR-039 fixture-scope canon):
  Use Python `socket.socket(AF_INET, SOCK_STREAM)`, `bind(('127.0.0.1', 0))` (ephemeral port), `listen(1)`, accept connections in a thread but never respond. Tear down at session end. Yield the URL `http://127.0.0.1:<port>/`. Session-scoped to amortize the bind/listen cost across all clone-timeout test cases.

### Implementation for Stream 4

- [X] T039 [US4] Modify `aod_template_fetch_upstream` in `.aod/scripts/bash/template-git.sh:102-104` — wrap the existing `git clone --depth=1 ...` invocation with the watchdog pattern per FR-006 + L-1:
  - Validate `AOD_FETCH_TIMEOUT` against `^[1-9][0-9]*$` (default 60 if unset; reject with exit 1 if invalid per Q-3).
  - Background the clone with `&`; capture `clone_pid=$!`.
  - Spawn watchdog `( sleep "$fetch_timeout" && kill -TERM "$clone_pid" 2>/dev/null ) &`; capture `watchdog_pid=$!`.
  - Install L-1 trap: `local watchdog_pid_local=$watchdog_pid; trap 'kill "$watchdog_pid_local" 2>/dev/null; trap - INT TERM EXIT' INT TERM EXIT`.
  - `wait "$clone_pid"; clone_rc=$?`.
  - Cleanup watchdog post-wait: `kill "$watchdog_pid" 2>/dev/null`.
  - On `clone_rc` 143 (SIGTERM) or 130 (SIGINT) → `rm -rf "$destdir"`, emit `[aod] ERROR: upstream fetch timed out after ${fetch_timeout}s for url=$url ref=$ref`, `trap - INT TERM EXIT`, return 9.
  - On any other `clone_rc` → propagate (return rc) and `trap - INT TERM EXIT`.
- [X] T040 [US4] Smoke test the watchdog pattern locally on macOS bash 3.2.57 — fast clone (any reachable repo) + hanging fixture (T038). Capture results in tasks-runlog.txt for Day-5 slip-watch GREEN-LIGHT condition 4
- [X] T041 [US4] Run T037 cases on macOS + Linux CI. All 6 cases MUST pass

**Checkpoint**: Stream 4 complete + green. TACHI-VULN-851fd6a21ba9 closed. Day-5 slip-watch GREEN-LIGHT condition 4 met. L-1 watchdog process-leak window closed.

---

## Phase 9: User Story 6 (P2) — ADR-040 + release trigger (Stream 3, 0.5-0.75d)

**Stream 3 — ADR-040** (independent of Streams 1-4; can advance in parallel) — covers US-256-6 (enterprise security architect pre-sales review).

**Goal**: ADR-040 authored in dual-commit pattern (Proposed → Accepted per Q-6 + F-1 ADR-038 precedent); release-please trigger verified via Conventional-Commits PR title; CHANGELOG migration guidance written.

**Independent Test**: Verify `docs/architecture/02_ADRs/ADR-040-config-file-parsing-hardening.md` exists with Status field transitioning Proposed → Accepted across two commits. Verify the file contains 7 Decision items, 6 Alternatives Considered (including M-5 source-then-`declare -p` diff rejection), Consequences with canonical fixture set + benchmark methodology, Related Findings (5 vuln_ids), References (LinkedIn web archive snapshot, F-1 ADR-038, F-250 ADR-039).

### Implementation for Stream 3

- [X] T042 [US6] Author `docs/architecture/02_ADRs/ADR-040-config-file-parsing-hardening.md` first commit (Status: Proposed) per Q-6 dual-commit pattern. Sections per FR-007 + plan §Stream 3:
  Status (Proposed); Context (4 source/eval sites + F-1 precedent + LinkedIn note); Decision Items 1-7 (pattern; regex; Q-1 single-PR; Q-3 footgun; H-2 TOCTOU framing; F-1 amendment per B-2 Path R-2; internal eval carve-out per ADR-040 Decision Item 7);
  Alternatives Considered (6 alternatives — JSON, TOML, point-fixes, set -r, bash -r -c, source-then-declare-p-diff per M-5);
  Consequences (one canonical pattern; bash 3.2 preserved; perf benchmark per SC-010 with canonical fixture set + methodology; awk micro-opt rejected; ADR-038 relationship; F-1 contract amendment;
  TOCTOU residual race window framing);
  Related findings (5 vuln_ids); References (LinkedIn web archive snapshot URL, F-1 ADR-038, F-250 ADR-039)
- [X] T043 [US6] Verify PR #257 title: `gh pr view 257 --json title --jq .title` returns `feat(256): harden source-pattern surface — bash source/eval → KV parser + clone timeout`. If not, retitle via `gh pr edit 257 --title "..."` (per FR-008 AC-8.1)

**Checkpoint**: ADR-040 Proposed (first commit) committed; PR title verified. Day-5 slip-watch GREEN-LIGHT condition 3 met (ADR-040 §Context + §Decision + §Alternatives Considered drafted).

---

## Phase 10: Polish & Cross-Cutting Concerns

**Purpose**: Day-5 slip-watch verification, full Stream 5 test execution, ADR-040 Accepted promotion, CHANGELOG finalization, NFR verification.

**CRITICAL**: T044 Day-5 slip-watch is the named conversion-lever decision point per plan §Critical Path. T053 ADR-040 Accepted promotion folds in Stream 1 benchmark numbers from T013.

- [X] T044 Day-5 slip-watch checkpoint (Mon 2026-05-11 EOD) — verify all 4 GREEN-LIGHT conditions per plan §Day-5 Slip-Watch Checkpoint:
  Condition 1 — `pytest tests/scripts/test_template_config_load_unit.py -v` ≥17/17 cases pass on macos-latest CI (T011/T012);
  Condition 2 — Site A green on Linux (T019);
  Condition 3 — ADR-040 Proposed committed (T042);
  Condition 4 — clone timeout watchdog smoke-tests pass on macOS bash 3.2 (T040).
  If 0-1 conditions red: continue. 2 conditions red: Team-Lead escalates to PM with recovery levers (Q-1 split / drop key_case / drop clone timeout). 3+ conditions red: structural slip; escalate immediately. Record outcome in tasks-runlog.txt
- [X] T045 [P] Author `tests/fixtures/regenerate-config-load-baseline.sh` (per F-1 M-5 precedent) — fixture regeneration script:
  Generate the canonical fixture set from current contracts;
  Generate `tests/fixtures/config-load/valid/{defaults-env-nextjs-supabase, defaults-env-fastapi-react, aod-kit-version-valid, personalization-env-valid}` from real config files in repo;
  Generate `tests/fixtures/config-load/adversarial/*` corpus per Test-1/Test-2 enumeration;
  Documentation header: regenerate when STACK_PACK_ALLOWED_KEYS or AOD_CANONICAL_PLACEHOLDERS change; do NOT regenerate to mask a regex regression
- [X] T046 [P] Run T045 to populate `tests/fixtures/config-load/{valid,adversarial}/` — commit the fixtures
- [X] T047 [P] Author additional Test-1 cases B-3 19-23 if not already covered in T009: trailing-newline / no-trailing-newline / CRLF / leading-whitespace / blank-line-followed-by-content. Each case verifies the per-line iteration mechanism handles edge formats correctly
- [X] T048 [P] Day-8 secondary checkpoint (Wed 2026-05-13 EOD) — verify all Stream 1+2 sites refactored + green; Stream 5 tests authored ≥80% case coverage; Stream 3 ADR-040 transitioning to Accepted. If Stream 5 isn't green by Day 8 EOD, use Day 9 as soak day; merge at Day 10-11 within hard ceiling
- [X] T049 Run full test suite on macOS + Linux CI: `pytest tests/scripts/test_template_config_load_unit.py tests/scripts/test_template_config_load_integration.py tests/scripts/test_template_git_clone_timeout.py tests/scripts/test_init_sh_defaults_env.py tests/scripts/test_template_substitute_lint_no_eval.py -v`. ALL cases MUST pass on both legs of the matrix (NFR-001 + FR-009)
- [X] T050 Verify NFR-002 (no new runtime dependencies): re-snapshot `pyproject.toml`, `requirements*.txt`, `package.json` SHA-256 from T004 baseline. Diff MUST be empty
- [X] T051 Verify NFR-005 (no `finding.yaml` schema change): `git diff main..HEAD -- schemas/finding.yaml` MUST be empty
- [X] T052 Verify SC-005 lint rule passes: `grep -c '\beval\b' .aod/scripts/bash/template-substitute.sh` returns `0`
- [X] T053 Finalize CHANGELOG.md v4.x entry (placeholder reserved at T008):
  `### Hardened config-file load (BLP-02 F-2)` heading;
  Document the new `aod_template_load_kv_file` library + 4 refactored sites + clone timeout (`AOD_FETCH_TIMEOUT` env var);
  Document the F-1 contract amendment (`aod_init_read_validated` now rejects `$`, `\`, backtick at prompt boundary) with adopter migration guidance;
  Reference ADR-040 + 5 closed vuln_ids
- [X] T054 Promote ADR-040 to `Status: Accepted` (Stream 3 second commit per Q-6 dual-commit pattern):
  Update §Status field;
  Fold in Stream 1 benchmark numbers from T013 into §Consequences (per-file delta, p50/p95, warm/cold cache);
  Document final NFR-004 disposition (which threshold tier was hit and Architect/Team-Lead/PM approval if required)
- [X] T055 Verify SC-010 benchmark documentation in ADR-040 §Consequences is complete (canonical fixture set listed; methodology described; per-file delta reported; warm/cold cache reported separately)
- [X] T056 Final pre-merge verification: confirm spec.md (PM ✓), plan.md (PM ✓ + Architect ✓), tasks.md (PM + Architect + Team-Lead ✓ — frontmatter injected by `/aod.tasks`); confirm draft PR #257 title is Conventional-Commits format; confirm zero `finding.yaml` schema diff; confirm 5 test files green on macOS + Linux CI

**Checkpoint**: All implementation complete; ADR-040 Accepted; CHANGELOG finalized; all NFRs + SCs verified. Ready for `/aod.deliver`.

---

## Phase 11: Post-Merge (Manual at /aod.deliver)

**Purpose**: Closing operator actions at `/aod.deliver` — NOT automated within this PR. Provided here for handoff completeness.

- [ ] T057 [MANUAL] Pre-merge re-verify PR #257 title is Conventional-Commits format (FR-008 AC-8.1): `gh pr view 257 --json title --jq .title` matches `^feat\(256\):`. Retitle via `gh pr edit 257 --title "..."` if needed
- [ ] T058 [MANUAL] Squash-merge PR #257 via `gh pr merge 257 --squash`. Note the squash-merge SHA
- [ ] T059 [MANUAL] Append 5 `REMEDIATED` events to `.security/vulnerabilities.jsonl` per SC-001:
  TACHI-VULN-6f5a95085056 (HIGH), TACHI-VULN-bf5496e9fcdf (HIGH), TACHI-VULN-9a7512071b4a (MEDIUM), TACHI-VULN-4dc6cf8f88ea (MEDIUM), TACHI-VULN-851fd6a21ba9 (LOW). Each event carries timestamp + merge SHA + feature_id (`F-2` / `256`) + pr_number (`257`)
- [ ] T060 [MANUAL] Belt-and-suspenders release-please verification per FR-008 AC-8.2 + `.claude/rules/git-workflow.md`: `gh pr list --state open --search "release-please" --limit 3` within ~30s post-merge. If empty, push empty release-marker commit `feat(256): source-pattern hardening — release marker` per AC-8.3 + F-212 incident lesson
- [ ] T061 [MANUAL] Post-merge `/security` re-scan against `main` HEAD (Test-7 + SC-002): verify zero new findings within source-pattern surface (`scripts/init.sh`, `.aod/scripts/bash/template-git.sh`, `.aod/scripts/bash/template-substitute.sh`, `.aod/scripts/bash/template-config-load.sh`)
- [ ] T062 [MANUAL] Test-6 fresh-checkout smoke test: clone tachi fresh into a tmpdir from post-merge `main`, run `./scripts/init.sh` against `nextjs-supabase` stack pack. Verify normal load. Verify no failures or regressions in user-facing flow

**Checkpoint**: Feature delivered + REMEDIATED events recorded + release-please PR opened. F-2 closes BLP-02 Wave 2.

---

## Dependencies / Story Completion Order

```
Phase 1 (Setup) ─── T001-T004 ──┐
                                 ↓
Phase 2 (Foundational) ─── T005-T008 ──┐
                                        ↓
Phase 3 (US2+US5 Library) ─── T009-T013 (Stream 1 critical path) ──┐
                                                                    ↓
Phase 4 (US1 Site A) ─── T014-T019 ─────────────────────┐
Phase 5 (US3 Site B) ─── T020-T024 ─────────────────────┤  (Streams 2.A through 2.D
Phase 6 (US7+US5 Site C) ─── T025-T033 ──────────────────┤   blocks on Stream 1)
Phase 7 (US8 Site D) ─── T034-T036 ──────────────────────┤
                                                          │
Phase 8 (US4 Stream 4 Clone Timeout) ─── T037-T041 ───────┤  (Stream 4 independent)
Phase 9 (US6 Stream 3 ADR-040) ─── T042-T043 ─────────────┤  (Stream 3 independent)
                                                          ↓
Phase 10 (Polish) ─── T044-T056 (Day-5 + Day-8 checkpoints; full test suite; ADR Accepted; NFRs)
                                                          ↓
Phase 11 (Post-Merge — MANUAL at /aod.deliver) ─── T057-T062
```

**Parallel opportunities** (within phases marked [P]):
- Phase 1: T002, T003, T004 in parallel (different directories/files)
- Phase 2: T006, T007, T008 in parallel (different artifacts)
- Phase 3: T009 (test authoring) parallel with T010-T012 dependencies (test must land before implementation per Constitution VI)
- Phase 4-7: Sites A/B/C/D refactor — can ALL begin once Phase 3 complete; T014, T020, T021, T025, T026, T034 (test authoring) parallel
- Phase 8: T037, T038 parallel
- Phase 10: T045, T047, T048 parallel; T049 depends on T045+T046

**Critical path**: T010 (library implementation) → T015-T017 (Site A) → T022-T023 (Site B) → T027-T032 (Site C) → T035 (Site D) → T039 (clone timeout) → T044 (Day-5 slip-watch) → T049 (full test suite) → T054 (ADR Accepted) → T056 (final verification).

**Total tasks**: 62 (vs F-1's 50; F-2 is +25% scope due to library bring-up + 4-site refactor + F-1 contract amendment ripple).

## Implementation Strategy (MVP First)

**MVP scope** (ship first if Day-5 slip-watch fires Q-1 split contingency):
- Phase 1-3 (Setup + Foundational + Library bring-up) — enables future config-load sites
- Phase 4 (Site A) — closes the highest-severity adopter-facing vuln (TACHI-VULN-6f5a95085056 HIGH)
- Phase 5 (Site B) — closes the highest-severity multi-hop chain vuln (TACHI-VULN-bf5496e9fcdf HIGH)
- Phase 9 (ADR-040 Proposed) + post-merge release trigger

**Defer to F-2b (split contingency only)**:
- Phase 6 (Site C eval removal + writer escape pass removal + F-1 contract amendment)
- Phase 7 (Site D TOCTOU collapse)
- Phase 8 (Stream 4 clone timeout)

**Default (no split)**: ship all phases as planned in single squash-merged PR per Q-1 ruling.
