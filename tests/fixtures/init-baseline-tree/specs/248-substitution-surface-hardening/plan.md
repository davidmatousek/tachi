---
triad:
  pm_signoff:
    agent: product-manager
    date: 2026-05-03
    status: APPROVED
    notes: "Plan faithfully implements all 11 spec FRs + 5 NFRs across 5 streams matching PRD's 8d/10d timeline; no scope creep into BLP-02 Wave 2+; constitution clean; PROJECT_PATH Option b fallback path preserved. 2 minor observations: Day-1 hard checkpoint for internal-tooling search; NFR-004 >50% PM escalation gating correctly locked."
  architect_signoff:
    agent: architect
    date: 2026-05-03
    status: APPROVED
    notes: "All 8 architect criteria pass; B-1/B-2/H-1/H-2/H-3/M-1/M-2/M-3 honored; ADR-038 structure complete (Status, Context, Decision, Alternatives Considered with 4 enumerated rejections, Consequences, Related Decisions citing ADR-009, References with web.archive.org snapshot); bash 3.2 compatibility preserved; pytest-via-subprocess wired; reorder pattern P1; no blockers. Details: .aod/results/architect-plan.md"
  techlead_signoff: null  # Added by /aod.tasks
---

# Implementation Plan: Substitution Surface Hardening (BLP-02 Wave 1)

**Branch**: `248-substitution-surface-hardening` | **Date**: 2026-05-03 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/248-substitution-surface-hardening/spec.md`

## Summary

Replace the `sed`-based template substitution path in `scripts/init.sh` with bash parameter expansion via the existing `aod_template_substitute_placeholders` function (already used by `/aod.update`); add prompt-time input validation in a new sourced helper `.aod/scripts/bash/init-input.sh`; verify gitignore-default for `.aod/personalization.env`; migrate constitution cleanup off `sed` to a `cp` against pre-stripped templates under `.aod/templates/`; remove `.claude/mcp-config.json` (Q-1 Option b default disposition); author public ADR-038; trigger release-please via Conventional-Commits PR title with belt-and-suspenders post-merge verification. Single squash-merged PR closes 5 `/security` vulns (1 HIGH + 2 MEDIUM + 2 LOW). Test runner: pytest-via-subprocess on existing macOS+Linux CI matrix (NOT bats).

## Technical Context

**Language/Version**: bash 3.2+ (macOS-default 3.2.57) AND bash 4+ (Linux 5.x) for `init.sh` + new `init-input.sh` helper; Python 3.x (existing) for pytest test runners. **No bash-4-only features** in adopter-facing helpers (no associative arrays, no `mapfile`/`readarray`, no `${var,,}`).
**Primary Dependencies**: bash builtins only (parameter expansion `${str//pat/rep}`, `printf -v`, `[[`); existing `aod_template_substitute_placeholders` + `aod_template_load_personalization_env` + `aod_template_assert_no_residual` from `.aod/scripts/bash/template-substitute.sh` (already in-repo, contract-defined, unit-tested). pytest (existing dev dependency). **Empty diff** on `pyproject.toml`, `requirements*.txt`, `package.json` per NFR-002.
**Storage**: Filesystem only — `.aod/personalization.env` (KEY=VALUE snapshot, gitignored), `.aod/memory/constitution.md` (post-init template copy), `.aod/templates/constitution-{clean,instructional}.md` (new pre-stripped templates), `.security/vulnerabilities.jsonl` (REMEDIATED events). No DB, no vector store.
**Testing**: pytest-via-subprocess (NOT bats) per Architect Pass 1 BLOCKING B-1. New test files at `tests/scripts/test_init_sh_*.py`; new fixtures at `tests/fixtures/init-baseline-tree/` + `tests/fixtures/regenerate-baseline.sh`. Existing `conftest.py` convention: module-scoped fixtures, regex-compiled patterns.
**Target Platform**: cross-platform — macOS-latest (bash 3.2.57 default in CI) AND ubuntu-latest (bash 5.x in CI). Existing GitHub Actions matrix runs both; F-1 adds tests to the already-running matrix without authoring a new workflow file.
**Project Type**: methodology template (single repo, no application backend/frontend — adopters bring their own code). Bash scripts + markdown templates + YAML config + Python tests.
**Performance Goals**: NFR-004 — init duration on canonical fixture MUST NOT regress by more than **10%** vs current `replace_in_files()` baseline. Stream 1 Day 1 benchmark mandatory; recorded in ADR-038 §Consequences. Escalation thresholds: ≤5% delta holds at 10%; 5–50% delta loosens NFR-004 to 25% with rationale; >50% delta escalates to PM for re-scope.
**Constraints**: bash 3.2 compatibility (NFR-001); zero new runtime dependencies (NFR-002); byte-identity substitution semantics across ≥13 adversarial inputs (NFR-003); zero `finding.yaml` schema bump (NFR-005); 8 working days active + 2 working days hard ceiling (PRD Timeline); single-PR delivery (no scope splitting).
**Scale/Scope**: 12 locked canonical placeholders (no PROJECT_PATH under Q-1 Option b); ~100-file canonical fixture for byte-comparison; 5 vuln_ids closed (1 HIGH + 2 MEDIUM + 2 LOW); 4 prompts wrapped in input validation; 1 new ADR (ADR-038); 4 new pytest files; 2 new constitution template variants; 1 file removed (`.claude/mcp-config.json`); ≥13 adversarial inputs in Test-2 corpus.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Per `.aod/memory/constitution.md` (v1.0.0, ratified 2026-03-21). Six load-bearing principles applicable to F-1; the rest are N/A (API design, concurrency, data isolation are SaaS-platform concerns; F-1 is a template-only change).

| Principle | Status | Justification |
|-----------|--------|---------------|
| **I. General-Purpose Architecture** | ✓ PASS | Substitution mechanism is domain-agnostic; no security-specific or use-case-specific code introduced. The new `aod_init_read_validated` helper is a generic input validator. |
| **II. API-First Design** | N/A | No API surface changes. F-1 is a shell-script + template-content change; no endpoints added/modified. |
| **III. Backward Compatibility (NON-NEGOTIABLE)** | ✓ PASS | `aod_template_substitute_placeholders` already used by `/aod.update`; F-1 adoption in `init.sh` introduces zero new failure mode for adopters who run `init.sh` cleanly today. Substitution semantics shift from regex-with-metachar to literal — strict improvement. Re-init not supported (Q-3 Option b); existing self-delete at `init.sh:354` IS the prevention; gitignore-only migration documented in CHANGELOG. |
| **IV. Concurrency & Data Integrity** | N/A | F-1 is a single-user shell script; no concurrency surface. |
| **V. Privacy & Data Isolation** | ✓ PASS | `.aod/personalization.env` gitignored by default protects `PROJECT_DESCRIPTION` (potentially proprietary positioning). Adopters can opt-in to commit. |
| **VI. Testing Excellence** | ✓ PASS | 7-test Regression Protection Plan (Test-1..Test-5', Test-6 manual smoke, Test-7 post-merge re-scan); ≥13 adversarial inputs in Test-2; pytest-via-subprocess on existing macOS+Linux CI matrix. Test-first authorship per Stream 1 sequencing (test_init_sh_substitution.py lands with the substitution adoption). |
| **VII. Definition of Done (NON-NEGOTIABLE)** | ✓ PASS | Spec includes a 14-item DoD; `/aod.deliver` validates pre-merge. Belt-and-suspenders release-please verification per FR-010. |
| **VIII. Observability & RCA** | ✓ PASS | 5 `REMEDIATED` events in `.security/vulnerabilities.jsonl` carry merge SHA + timestamp — full audit trail. ADR-038 documents the root-cause migration (sed → bash param expansion) per Five Whys discipline. |
| **IX. Git Workflow & Feature Branching (NON-NEGOTIABLE)** | ✓ PASS | Feature branch `248-substitution-surface-hardening` created; draft PR #249 already opened at plan stage; conventional-commits PR title `feat(248): ...`; release-please verification per `.claude/rules/git-workflow.md` R12. |
| **X. Product-Spec Alignment + Architecture Review (NON-NEGOTIABLE)** | ✓ PASS | PRD with full Triad sign-off (v1.2 final); spec.md PM-approved; this plan.md will receive dual sign-off; tasks.md will receive triple sign-off. |
| **XI. SDLC Triad Collaboration** | ✓ PASS | PM/Architect/Team-Lead chain enforced via `/aod.plan` orchestration. PRD already has all three Triad sign-offs; plan dual sign-off + tasks triple sign-off complete the chain. |

**Pre-Phase-0 verdict**: PASS — no violations; no Complexity Tracking entries needed.

## Project Structure

### Documentation (this feature)

```
specs/248-substitution-surface-hardening/
├── plan.md              # This file (/aod.project-plan output)
├── research.md          # Already authored by /aod.spec
├── spec.md              # PM-approved
├── data-model.md        # Phase 1 artifact (this iteration)
├── quickstart.md        # Phase 1 artifact (this iteration)
├── contracts/           # Phase 1 artifact (this iteration)
│   └── init-input-helper-contract.md
├── checklists/
│   └── requirements.md  # Spec quality checklist
└── tasks.md             # Task breakdown (/aod.tasks output, next sub-step)
```

### Source Code (repository root)

```
.aod/
├── scripts/
│   └── bash/
│       ├── template-substitute.sh    # EXISTING — already implements aod_template_substitute_placeholders (no edit)
│       └── init-input.sh             # NEW — aod_init_read_validated helper (Q-2 Option b)
├── templates/
│   ├── constitution-clean.md         # NEW — post-strip output (used at init time)
│   └── constitution-instructional.md # NEW — full template with embedded instructions (fork docs)
├── memory/
│   └── constitution.md               # EXISTING — written by `cp .aod/templates/constitution-clean.md` post-init
└── personalization.env               # EXISTING contract — written by init.sh; gitignored

scripts/
└── init.sh                           # MODIFIED — replace_in_files() removed; aod_init_read_validated wired to 4 prompts;
                                      # constitution sed → cp; pre-flight check; reorder write→load→substitute

.claude/
└── mcp-config.json                   # REMOVED (Q-1 Option b default; conditional on internal-tooling search)

contracts/
└── personalization-schema.md         # MODIFIED — document local-only as default

docs/
└── architecture/
    └── 02_ADRs/
        └── ADR-038-placeholder-substitution-strategy.md  # NEW — dual-commit Proposed → Accepted

.gitignore                            # VERIFIED unchanged at line 222 (.aod/personalization.env already present)

CHANGELOG.md                          # MODIFIED — v4.x entry with migration command + .claude/mcp-config.json removal note

.security/
└── vulnerabilities.jsonl             # MODIFIED — 5 REMEDIATED events appended post-merge

tests/
├── scripts/
│   ├── conftest.py                   # EXISTING — pytest fixtures (no edit)
│   ├── test_init_sh_substitution.py  # NEW — Test-1 (fixture-replay byte-comparison)
│   ├── test_init_sh_adversarial.py   # NEW — Test-2 (≥13 adversarial inputs)
│   ├── test_init_sh_constitution.py  # NEW — Test-4 (constitution byte-compare)
│   └── test_init_sh_self_delete.py   # NEW — Test-5' (self-delete preservation)
└── fixtures/
    ├── init-baseline-tree/           # NEW — recorded baseline tree for byte-comparison
    └── regenerate-baseline.sh        # NEW — baseline regeneration script (Stream 5 deliverable)
```

**Structure Decision**: tachi is a methodology template (single repo, no application code split). The structure follows existing conventions: `.aod/scripts/bash/` for sourced bash libraries (sibling to existing `template-*.sh` library files), `.aod/templates/` for AOD-Kit-managed templates (per Architect Pass 1 H-3 — `.aod/templates/`, NOT repo-root `templates/`), `tests/scripts/` for pytest tests targeting bash scripts via `subprocess.run`, `docs/architecture/02_ADRs/` for sequentially-numbered ADRs (ADR-038 is next; ADR-037 is the current latest).

## Architecture Approach

### Five Implementation Streams

The work decomposes into five streams matching PRD §Timeline. The first stream is the critical path; streams 2/3/4 advance independently in parallel; stream 5 follows stream 1.

#### Stream 1 — Substitution Adoption (Critical Path, 2.5 days)

**Goal**: Remove `replace_in_files()`, route every personalization-target file through `aod_template_substitute_placeholders`, add residual scan, add pre-flight check, add benchmark.

**Components**:

1. **`init.sh` reorder** (per Architect Pass 1 BLOCKING B-2 pattern P1):
   - Move snapshot-write to BEFORE the substitution loop.
   - Add `source .aod/scripts/bash/template-substitute.sh` at the top of `init.sh` (replaces the lazy source at the existing `:336`).
   - Add `aod_template_load_personalization_env .aod/personalization.env` immediately after snapshot-write.
   - Replace `replace_in_files()` with a `find ... -print0 | while read -d ''` loop that calls `aod_template_substitute_placeholders <file> <file>` (in-place).
   - After the loop, run `aod_template_assert_no_residual <file>` per file; halt non-zero on any residual.

2. **Pre-flight check** (top of `init.sh`, after sourcing):
   ```bash
   if [[ -f .aod/personalization.env ]]; then
       echo "[init] FATAL: Repository already personalized. Re-init is not supported. To re-personalize, remove .aod/personalization.env and re-run init.sh." >&2
       exit 1
   fi
   ```

3. **Constitution cleanup** (FR-008): replace the two `sed -i` invocations at `:235-241` with `cp ".aod/templates/constitution-clean.md" .aod/memory/constitution.md`. Author both `.aod/templates/constitution-clean.md` (post-strip output) and `.aod/templates/constitution-instructional.md` (full template).

4. **PROJECT_PATH disposition** (FR-007): default Option (b) — `git rm .claude/mcp-config.json`. **Internal-tooling search** during Day 1 (per Team-Lead L-2): grep `mcp-config.json` across `.aod/scripts/`, `.claude/agents/`, `.claude/commands/`, `Makefile`, `scripts/`. If a wired consumer surfaces, flip to Option (a) — add PROJECT_PATH to canonical-13 with `realpath` normalization + path-character whitelist `[A-Za-z0-9._/-]`.

5. **Day 1 benchmark** (NFR-004): `time ./scripts/init.sh` on the canonical fixture before and after the substitution swap. Record both timings in ADR-038 §Consequences. Apply NFR-004 escalation rules.

**Deliverables**: modified `scripts/init.sh`; new `.aod/templates/constitution-clean.md` + `.aod/templates/constitution-instructional.md`; conditional removal of `.claude/mcp-config.json`; benchmark numbers staged for ADR-038.

#### Stream 2 — Input Validation (Independent, 1.0 day)

**Goal**: Add `aod_init_read_validated` helper; wrap 4 `read -p` prompts.

**Components**:

1. **New file `.aod/scripts/bash/init-input.sh`** (Q-2 Option b sibling to existing `template-*.sh`):
   ```bash
   # Function signature: aod_init_read_validated <prompt> <var_name> <max_len>
   aod_init_read_validated() {
       local prompt="$1" var_name="$2" max_len="$3"
       local answer attempt=0 reason
       while (( attempt < 3 )); do
           read -r -p "$prompt" answer
           reason=""
           if [[ "$answer" =~ $'\n' ]]; then reason="newline not allowed"
           elif [[ "$answer" =~ $'\0' ]]; then reason="NUL byte not allowed"
           elif [[ "$answer" =~ [[:cntrl:]] ]]; then reason="control character not allowed"
           elif (( ${#answer} > max_len )); then reason="over-length (max $max_len chars)"
           fi
           if [[ -z "$reason" ]]; then
               printf -v "$var_name" '%s' "$answer"
               return 0
           fi
           echo "[init] Input rejected: $reason; please re-enter." >&2
           ((attempt++))
       done
       echo "[init] FATAL: 3 consecutive invalid inputs for $var_name; aborting." >&2
       exit 1
   }
   ```
   Apply Feature 132 lesson: explicit `set +e`/`set -e` bracket if needed inside the helper for bash 3.2 compatibility (`local rc=$?` after command-substitution can abort under `set -euo pipefail` on bash 3.2).

2. **Wire prompts** in `scripts/init.sh:24-28`:
   - `aod_init_read_validated "Project Name: " PROJECT_NAME 100`
   - `aod_init_read_validated "Project Description: " PROJECT_DESCRIPTION 300`
   - `aod_init_read_validated "GitHub Organization: " GITHUB_ORG 39`  # GitHub login hard limit
   - `aod_init_read_validated "GitHub Repository [$PROJECT_NAME]: " GITHUB_REPO 100`
   (The fourth prompt's default-fallback behavior is preserved — empty input → `GITHUB_REPO=$PROJECT_NAME` per existing logic; the helper accepts empty input within `max_len` bound.)

**Deliverables**: new `.aod/scripts/bash/init-input.sh`; modified `scripts/init.sh:24-28` prompt block.

#### Stream 3 — Posture Defaults (Independent, 0.5 day)

**Goal**: Verify `.gitignore` entry; document local-only default in `contracts/personalization-schema.md`; add CHANGELOG migration command.

**Components**:

1. **Verify `.gitignore:222`** contains `.aod/personalization.env` (already present per `b27f3ea` 2026-04-19; verification only — no code change).
2. **Update `contracts/personalization-schema.md`** §Substitution Strategy: document local-only as default, opt-in path (remove the gitignore line) as opt-out from default.
3. **Add CHANGELOG entry** under v4.x:
   ```
   - **Hardened defaults (BLP-02 F-1)**: `.aod/personalization.env` is now gitignored by default.
     Adopters who already committed the file should run:
     ```
     git rm --cached .aod/personalization.env
     git commit -m "chore: untrack personalization snapshot per BLP-02 default"
     ```
   - **`.claude/mcp-config.json` removed**: file was an unwired example template; Claude Code's MCP config lives at `~/.config/claude-code/`. Adopters who symlinked or copied the file should update their config from upstream Claude Code documentation.
   ```
4. **Init success message** add a one-liner about the gitignore default after personalization completes.

**Deliverables**: modified `contracts/personalization-schema.md`; modified `CHANGELOG.md`; modified `scripts/init.sh` post-init success-message block.

#### Stream 4 — ADR + Release Trigger (Independent, 0.5 day)

**Goal**: Author ADR-038; verify Conventional-Commits PR title; document belt-and-suspenders post-merge verification.

**Components**:

1. **`docs/architecture/02_ADRs/ADR-038-placeholder-substitution-strategy.md`** — dual-commit (Proposed → Accepted) following ADR-000-template:
   - **Status**: Proposed → Accepted
   - **Context**: Two existing substitution paths (`init.sh` sed-based at line 124; `update.sh` via `aod_template_substitute_placeholders`); the multi-hop execution chain via `.claude/mcp-config.json`; Daniel Wood's 2026-05-02 LinkedIn note (URL + `web.archive.org` snapshot).
   - **Decision**: Adopt bash parameter expansion (`${str//pat/rep}`) via `aod_template_substitute_placeholders` as the canonical substitution method across both `init.sh` and `update.sh`. The Decision section explicitly notes the residual-scan regex character class (`[A-Z_]` for canonical placeholders) and commits to lockstep update if the canonical placeholder list expands to digits.
   - **Alternatives considered**:
     - sed with metachar-escaping wrapper — REJECTED (escape-of-escape bypasses are well-documented; OWASP Injection Prevention Cheat Sheet explicitly warns against this approach)
     - `awk -v` — REJECTED (still spawns external process; doesn't solve the fork+exec cost; awk has its own metachar-handling complexity)
     - Python `string.Template` — REJECTED (introduces Python dependency at init time; bash-only is the baseline)
     - Perl `s|||g` — REJECTED (introduces Perl dependency; metachar handling no better than sed)
   - **Consequences**: One canonical pattern across init + update; bash 3.2 compatibility preserved; literal-substitution semantics by language definition; PROJECT_PATH disposition resolved (Option b — file removed); Day 1 benchmark numbers (record both pre/post timings here per NFR-004).
   - **Related Decisions**: cite ADR-009 as the prior decision being superseded on the *mechanism* axis (placeholder enumeration in ADR-009 remains valid).
   - **Related Findings**: TACHI-VULN-{6bc17fd01ac8, 77f0519f9cfb, bc67ca510ea9, 30bbfd90959a, 18127be5d214} — 5 vuln_ids closed.
   - **References**: Daniel Wood LinkedIn URL + `web.archive.org` snapshot URL (per Team-Lead Pass 1 L-1).

2. **PR title** at draft creation: `feat(248): harden init.sh substitution surface — sed → bash param expansion + input validation + gitignore default`. (The existing draft PR #249 has title `feat(248): substitution surface hardening` from `/aod.plan` setup; needs retitle before merge per `.claude/rules/git-workflow.md` Deliver Stage pre-merge check.)

3. **Belt-and-suspenders post-merge verification** (per `.claude/rules/git-workflow.md` R12): `gh pr list --state open --search "release-please" --limit 3` within ~30s post-merge; if empty, push empty marker commit. **Manual operator action at /aod.deliver**, not in this PR.

**Deliverables**: new `docs/architecture/02_ADRs/ADR-038-placeholder-substitution-strategy.md`; PR #249 retitle annotation in tasks.md.

#### Stream 5 — Test Infrastructure (3.0 days)

**Goal**: Author 4 pytest test files; record canonical baseline tree; provide regeneration script. Existing CI matrix runs the new tests automatically.

**Components**:

1. **`tests/scripts/test_init_sh_substitution.py`** (Test-1):
   - Use `subprocess.run` to invoke `init.sh` against a controlled tmpdir clone of the template (`PROJECT_NAME=tachi`, `PROJECT_DESCRIPTION=threat modeling sidecar`, `GITHUB_ORG=davidmatousek`, `GITHUB_REPO=tachi`, `AI_AGENT=claude`, etc.).
   - Pass inputs via either env vars OR pre-populated stdin (TBD during build — env-var approach preferred for non-interactive testability).
   - Walk the resulting personalized tree; for each file, byte-compare against `tests/fixtures/init-baseline-tree/` using `Path.read_bytes()` equality.
   - Assert mode preservation (executable bit) via `Path.stat().st_mode`.

2. **`tests/scripts/test_init_sh_adversarial.py`** (Test-2):
   - `pytest.mark.parametrize` table of ≥13 cases:
     1. `AT&T` (sed-metachar `&`)
     2. `foo|bar` (sed-delimiter `|`)
     3. `\1\2 backref` (sed-backref `\1`-`\9`)
     4. `'single-quoted'` (shell quoting)
     5. `"double-quoted\"escaped"` (shell quoting + embedded escape)
     6. `Ⅷ-Ⅸ` (multibyte UTF-8 at U+2160 range)
     7. Leading-whitespace input
     8. Trailing-whitespace input
     9. Multi-line paste (`"foo\nbar"`) — expect prompt rejection
     10. NUL paste — expect prompt rejection
     11. Over-length input (101+ chars for PROJECT_NAME; 40+ for GITHUB_ORG) — expect prompt rejection
     12. Control character (0x07 BEL) — expect prompt rejection
     13. **Trailing-newline edge case** (per Architect Pass 1 M-1): a fixture file containing the literal 4 bytes `a\nb` (backslash-n, no actual LF byte) — verify byte-identical preservation. A second fixture file ending without a trailing newline — verify byte-identical preservation.
   - Each case has an expected outcome class: `substituted-byte-identical` OR `prompt-rejected-with-reason-<class>`.
   - Adversarial input flow: env-var injection bypasses prompt (validates substitution semantics); stdin injection exercises prompt validation.

3. **`tests/scripts/test_init_sh_constitution.py`** (Test-4):
   - Run `init.sh` end-to-end; assert `Path(".aod/memory/constitution.md").read_bytes() == Path(".aod/templates/constitution-clean.md").read_bytes()`.

4. **`tests/scripts/test_init_sh_self_delete.py`** (Test-5'):
   - Run `init.sh` end-to-end; assert `not Path("scripts/init.sh").exists()`.
   - Replaces the original Test-5 (re-init parity) per Architect M-3 + Team-Lead Q-3 Option (b).

5. **`tests/fixtures/init-baseline-tree/`** — recorded baseline tree (committed). Generated once by Stream 5 Day 1 with the canonical fixture inputs.

6. **`tests/fixtures/regenerate-baseline.sh`** — documented regeneration script (per Team-Lead Pass 1 M-5):
   - Clone tachi fresh into a tmpdir.
   - Run `init.sh` with the canonical fixture inputs.
   - Copy the personalized tree to `tests/fixtures/init-baseline-tree/`.
   - Document: regenerate when canonical placeholders change; do NOT regenerate to mask a substitution-semantics regression.

**Deliverables**: 4 new pytest test files; `tests/fixtures/init-baseline-tree/` directory; `tests/fixtures/regenerate-baseline.sh`; CI matrix runs all four on macos-latest + ubuntu-latest with no new workflow file.

### Critical Path & Slip-Watch

- **Day 5 (Wed 2026-05-08) slip-watch checkpoint** (per Team-Lead Pass 1): if Stream 5 has not recorded a green CI matrix run by EOD Day 5, escalate to PM for scope-cut adjudication.
- **Day 8 merge target**, Day 10 hard ceiling.
- Stream 4 has 0.5d reabsorption authority into Stream 5 if CI iteration costs more than the 0.5d baked-in buffer.

### Threading & Dependencies

```
Day 1                        Day 2-3            Day 4-5            Day 6-7         Day 8
─────                        ───────            ───────            ───────         ─────
Stream 1 ███ (substitution + pre-flight + benchmark + Q-1 search)
Stream 2 ███ (input validation helper) — in parallel with Stream 1
Stream 3  █ (posture defaults + CHANGELOG) — in parallel
Stream 4   █ (ADR-038) — Day 2 after Stream 1 benchmark
Stream 5    ███████ (test files + baseline) — depends on Stream 1
                                              │
                                              └── Day 5 slip-watch ─── Day 7 review ─── Day 8 merge
```

## Risks & Mitigations (cross-reference PRD §Risks)

| Risk | Severity | Mitigation Plan |
|------|----------|-----------------|
| R-1 bash 3.2 incompatibility in helper | MEDIUM | Code review checklist for bash-4-only features; CI matrix runs macOS bash 3.2.57; existing safe function is already 3.2-compatible |
| R-2 Substitution-semantics drift on edge-case files | MEDIUM | Test-1 fixture-replay byte-comparison + Test-2 adversarial corpus including no-trailing-newline + literal `a\nb` cases |
| R-3 Re-init not supported | LOW (RESOLVED) | Pre-flight check + existing self-delete; CHANGELOG migration command |
| R-4 release-please skip | LOW | FR-010 belt-and-suspenders empty-marker commit pattern (F-212 incident lesson) |
| R-5 Option (b) breaks downstream wired adopter | LOW | Internal-tooling search during Stream 1 Day 1; fallback to Option (a) |
| R-6 Over-strict validator rejects legitimate Unicode | LOW | Test-2 case 6 (`Ⅷ-Ⅸ` multibyte UTF-8); validator rejects ASCII control 0x00–0x1F only |

## Phase 0 — Research

**Status**: COMPLETE. The /aod.spec phase already authored a comprehensive research.md combining four parallel research agent outputs (knowledge base, codebase, architecture, web). All NEEDS CLARIFICATION items from the spec are resolved (the spec has 0 markers per the requirements checklist). No additional research needed at the plan stage.

**Research summary** (see [research.md](research.md) for full):

| Decision | Rationale | Alternatives Rejected |
|----------|-----------|-----------------------|
| Bash parameter expansion via existing `aod_template_substitute_placeholders` | In-repo, contract-defined, unit-tested, used by `/aod.update`. Literal substitution by language semantics. ~50–500× faster than sed. | sed escape wrapper (OWASP-flagged anti-pattern); awk -v (still external process); Python string.Template (new dependency); Perl s\|\|g (new dependency) |
| `aod_init_read_validated` in new file `.aod/scripts/bash/init-input.sh` | Sibling to existing `template-*.sh` library convention; F-2 Wave 2 reuses *pattern* not function | Inline in init.sh (poor reusability; bloats init.sh); merge into template-substitute.sh (interactive read mixed with non-interactive substitution is a contract smell) |
| Pre-stripped constitution templates at `.aod/templates/` | AOD-Kit canonical convention per Architect Pass 1 H-3; aligned with existing `.aod/templates/{spec,plan,tasks}-template.md` | repo-root `templates/` (does not exist; would be a new convention conflicting with the AOD-Kit lineage) |
| Remove `.claude/mcp-config.json` (Q-1 Option b default) | File is unwired; Claude Code's MCP config lives at `~/.config/claude-code/`; Option (a) reintroduces JSON-injection vector via `pwd` | Add PROJECT_PATH to canonical-13 (mutates contract for unwired example; reintroduces injection vector) |
| pytest-via-subprocess (NOT bats) | Repo has zero `.bats` files; existing pytest matrix on macos-latest + ubuntu-latest already runs; bats CI bootstrap is ~1d out-of-scope | bats-core (greenfield CI bootstrap; out of scope per Architect B-1) |
| Re-init NOT supported (Q-3 Option b) | Existing self-delete IS the prevention mechanism; pre-flight check is the soft guard; CHANGELOG migration is sufficient delta path | Support re-init (adds 0.5d Stream 5; conflates posture-hardening with adopter-ergonomics) |

## Phase 1 — Design Artifacts

### data-model.md

The "data" entities for F-1 are configuration files and contract-bearing markdown — not domain objects. The data-model.md will document:

- **Personalization snapshot** (`.aod/personalization.env`): KEY=VALUE shape, 12 canonical keys, validation rules (no embedded newlines, value-set non-empty), file-mode 0644, gitignored.
- **Canonical placeholder set**: enumeration locked at 12 (under Q-1 Option b) or 13 (under Option a fallback). Owner contract: `.aod/scripts/bash/template-substitute.sh:50-63`.
- **Vulnerability event log shape** (`.security/vulnerabilities.jsonl`): event types `DETECTED`, `REMEDIATED`, `WONTFIX`; fields per existing schema (no schema bump per NFR-005); new entries appended post-merge with merge SHA + timestamp.
- **Constitution variants shape**: clean (post-strip) vs instructional (full); both markdown; both ship under `.aod/templates/`; relation: `instructional` → strip-comments + strip-instructions → `clean`.
- **ADR-038 shape**: standard ADR template per ADR-000-template.md; dual-commit Proposed → Accepted lifecycle.

(Full data-model.md to be authored in this iteration's contracts pass.)

### contracts/

Per FR-005 (Q-2 Option b), the new `aod_init_read_validated` helper has a contract surface that the validator function MUST honor. Captured in `contracts/init-input-helper-contract.md`:

- **Function**: `aod_init_read_validated <prompt> <var_name> <max_len>`
- **Inputs**: 3 positional args (all required).
- **Pre-condition**: `var_name` is a valid bash identifier (`[A-Za-z_][A-Za-z0-9_]*`); `max_len` is a positive integer.
- **Behavior**: prompts via `read -r -p`; rejects on newline / NUL / control / over-length with named-class message; re-prompts up to 3 times; exits non-zero on the 3rd consecutive rejection; on success, sets the variable named by `$var_name` via `printf -v` (no `eval`, no global-namespace pollution).
- **Output**: writes prompt to stdout; writes rejection messages to stderr; sets the named bash variable on success.
- **Exit codes**: 0 on success; 1 on 3-strikes-out rejection.
- **Bash compatibility**: 3.2.57+. No associative arrays. No `mapfile`. No `${var,,}`.

(Full contracts/init-input-helper-contract.md to be authored in this iteration.)

### quickstart.md

A maintainer-facing quickstart that captures the post-F-1 init flow:

1. Clone tachi fresh.
2. Run `./scripts/init.sh`.
3. Answer prompts (PROJECT_NAME, PROJECT_DESCRIPTION, GITHUB_ORG, GITHUB_REPO).
4. Observe: `.aod/personalization.env` written; substitution loop runs literal substitution via bash parameter expansion; residual scan asserts zero `{{KEY}}` remain; constitution copied from `.aod/templates/constitution-clean.md`; `init.sh` self-deletes.
5. Run `git status` — verify `.aod/personalization.env` is gitignored.
6. Optional: re-run `./scripts/init.sh` — observe pre-flight check fires `[init] FATAL: Repository already personalized.` (cannot actually run because self-delete already removed the script).

(Full quickstart.md to be authored in this iteration.)

### Agent Context Update

Run `.aod/scripts/bash/update-agent-context.sh claude` to update `.claude/CLAUDE.md` (or equivalent) with the new bash 3.2 compatibility constraint and the `aod_init_read_validated` helper convention.

## Constitution Re-Check (Post-Phase-1)

After Phase 1 design artifacts are authored, re-evaluate the Constitution Check table. **No design decision in Phase 1 introduces a new constitutional violation**:

- I (General-Purpose) — preserved; helper is generic.
- III (Backward Compat) — preserved; existing function reused; semantic shift is improvement.
- VI (Testing) — strengthened by the 7-test plan + ≥13-input adversarial corpus.
- IX (Git Workflow) — preserved; draft PR #249 already opened.
- X (Triad alignment) — preserved; this plan.md will receive dual sign-off.

**Post-Phase-1 verdict**: PASS. Complexity Tracking remains empty.

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| (none) | — | — |

## Open Questions

All four PRD-stage open questions (Q-1..Q-4) have been adjudicated and folded into the spec. **Plan-stage open questions: none.** The internal-tooling search outcome for Q-1 Option b is provisional (codebase research already strongly indicates no wired consumer); Stream 1 Day 1 reconfirms.

## References

- **PRD**: [docs/product/02_PRD/248-substitution-surface-hardening-2026-05-03.md](../../docs/product/02_PRD/248-substitution-surface-hardening-2026-05-03.md)
- **Spec**: [spec.md](spec.md) (PM APPROVED)
- **Research**: [research.md](research.md)
- **Constitution**: [.aod/memory/constitution.md](../../.aod/memory/constitution.md) (v1.0.0)
- **Existing safe function**: [.aod/scripts/bash/template-substitute.sh:318-411](../../.aod/scripts/bash/template-substitute.sh)
- **Prior ADR superseded on mechanism axis**: [docs/architecture/02_ADRs/ADR-009-template-variable-expansion-scope.md](../../docs/architecture/02_ADRs/ADR-009-template-variable-expansion-scope.md)
- **ADR template**: [docs/architecture/02_ADRs/ADR-000-template.md](../../docs/architecture/02_ADRs/ADR-000-template.md)
- **Git workflow**: [.claude/rules/git-workflow.md](../../.claude/rules/git-workflow.md) (R12 release-please verification pattern; F-212 incident reference)
- **BLP-02 strategy**: [_internal/strategy/BLP-02-enterprise-hardening.md](../../_internal/strategy/BLP-02-enterprise-hardening.md)
- **Draft PR**: [#249](https://github.com/davidmatousek/tachi/pull/249) (opened at plan stage; will be retitled at deliver stage if needed)
