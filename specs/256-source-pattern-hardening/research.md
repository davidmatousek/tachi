# Research Summary: F-2 Source-Pattern Hardening (BLP-02 Wave 2)

**PRD Reference**: [docs/product/02_PRD/256-source-pattern-hardening-2026-05-04.md](../../docs/product/02_PRD/256-source-pattern-hardening-2026-05-04.md)
**Created**: 2026-05-04
**Author**: spec author (research phase)

---

## Knowledge Base / Institutional Knowledge

### Pattern: F-1 Substitution Surface Hardening (PRD #248, delivered 2026-05-04)

- **What it established**: the **validation-triplet pattern** — regex-validate → reject-on-mismatch → `printf -v` assignment — for adopter-supplied input. Implemented in `aod_init_read_validated` (`.aod/scripts/bash/init-input.sh`) for **interactive `read -p` input**.
- **What F-2 reuses**: the *pattern* (regex-validate → reject → `printf -v`), NOT the function. F-2 builds the **non-interactive file-parse** version: `aod_template_load_kv_file` in a NEW sourced library at `.aod/scripts/bash/template-config-load.sh`.
- **F-1 explicit forecast** (ADR-038 §Constraints, line 28): *"the parallel `defaults.env` strict-KV parser (F-2 Wave 2) reuses the *pattern* documented here (validation triplet) but NOT the `aod_init_read_validated` function (which is interactive `read -p`-only)"*.
- **Lesson**: pytest-via-subprocess is the canonical test harness for bash library work in tachi. F-1 Pass 1 BLOCKING B-1 ruled this conclusively (`tests/scripts/test_*.py`); F-2 inherits the convention.

### Pattern: F-250 Adversarial Unit Extraction Hot-Fix (PRD #250, delivered 2026-05-04)

- **What it established**: **adversarial test cases live at the unit level** (subprocess invocation of the bash function, sub-second per case), not the integration level (full `init.sh` end-to-end, ~30s per case). 12 cases extracted into pytest unit-level modules.
- **ADR-039 canon** (`docs/architecture/02_ADRs/ADR-039-test-architecture-fixture-scope-and-asymmetric-baseline.md`): test fixture scope and asymmetric-baseline rules.
- **F-2 inheritance**: Stream 5 fixture work at `tests/fixtures/config-load/` (NEW directory) follows the unit-level cadence — each adversarial fixture is a standalone file, exercised by `subprocess.run`, sub-second per case.

### Pattern: BLP-02 Closed-Loop Cadence

- **Established by F-1**: LinkedIn note (Daniel Wood, 2026-05-02) → `/security` scan → BLP-02 blueprint → PRD → spec → plan → tasks → ADR → release-please → public artifact.
- **F-2 demonstrates**: the cadence holds for **larger, library-introducing** features (not just refactor-to-existing-helper).
- **Release-please belt-and-suspenders** (per F-212 incident, `.claude/rules/git-workflow.md` Reference Incident): post-merge `gh pr list --state open --search "release-please"` verification within ~30s; empty-marker commit fallback if release-please skips.

---

## Codebase Analysis

### Verified call sites (line numbers checked against current `main` post-F-1)

| Site | File | Line(s) | Pattern | Severity |
|---|---|---|---|---|
| A | `scripts/init.sh` | **106** | `source "stacks/$SELECTED_PACK/defaults.env"` (preceded by `aod_init_read_validated` source preamble F-1 added) | HIGH |
| B-primary | `.aod/scripts/bash/template-git.sh` | **561** | `source "$path"` in `aod_template_read_version_file` (function header `:544`) — sources BEFORE per-field validators at `:568+` run | HIGH |
| B-roundtrip | `.aod/scripts/bash/template-git.sh` | **501** | `source "$tmp_path" 2>/dev/null` in `aod_template_write_version_file` (function header `:485-515`) — round-trip validation block | HIGH (parallel) |
| C | `.aod/scripts/bash/template-substitute.sh` | **217, 249, 536, 558** | `eval`-based dynamic assignment (read-side `:217`/`:536`/`:558` and write-side `:249`) | MEDIUM |
| D | `.aod/scripts/bash/template-substitute.sh` | **162-209** | `aod_template_load_personalization_env` subshell-validate-then-caller-source (TOCTOU) | MEDIUM |
| E | `.aod/scripts/bash/template-git.sh` | **102-104** | `git clone --depth=1 ... "$url" "$destdir"` (no timeout) in `aod_template_fetch_upstream` | LOW |

PRD-corrected line numbers per Pass 1 H-3: function name `aod_template_validate_version_content` (v1.0 reference) is **incorrect** — that function does not exist on `main`. The `:501` inner round-trip block lives inside `aod_template_write_version_file:485-515`.

### Bash library siblings (`.aod/scripts/bash/`)

| File | Size | Function count | Role |
|---|---|---|---|
| `template-git.sh` | 25K | 6 | git operations (clone, version-file read/write, manifest read) |
| `template-substitute.sh` | 26K | 5 | placeholder substitution + personalization snapshot read/write |
| `template-manifest.sh` | 13K | 4 | manifest schema + integrity |
| `template-validate.sh` | 10K | 4 | path safety + symlink rejection + residual scan |
| `template-json.sh` | 6K | 4 | minimal JSON read |
| `init-input.sh` | 8.7K | 1 | F-1 helper: `aod_init_read_validated` (interactive prompt) |

**Naming convention**: `aod_template_<verb>_<noun>` for bash-library functions. F-2's new function name `aod_template_load_kv_file` follows this convention. Sibling-file placement (Q-4 Option a) — new file at `.aod/scripts/bash/template-config-load.sh` — matches F-1's `init-input.sh` precedent.

### F-1 spec/plan/tasks structural pattern (to mirror)

Located at `specs/248-substitution-surface-hardening/`:

- `spec.md` — 7 user stories (US-1 to US-7); Edge Cases section; FR-001 to FR-011; NFR-001 to NFR-005; Internal-Tooling Search Outcome; Key Entities; SC-001 to SC-015 (where SC-015 is non-DoD public visibility); Dependencies and Assumptions; Regression Protection Plan; Risks; References.
- `plan.md` — 35K; data-model, API contracts, agent assignments, delivery scheduling, security scan plan.
- `tasks.md` — 39K; T001-T040+ tasks across 5 streams + 3 agent waves.

F-2 mirrors this structure. The PRD is structurally compatible; user stories US-256-1 through US-256-8 in the PRD map to spec User Stories 1-8.

### Test infrastructure precedent (F-1, F-250)

- **F-1 test files**: `tests/scripts/test_init_input_unit.py`, `test_init_sh_substitution.py`, `test_init_sh_adversarial.py`, `test_init_sh_constitution.py`, `test_init_sh_self_delete.py`.
- **Pattern**: subprocess invocation of `bash -c source` (sub-second per case); process substitution `< <(printf ...)` REQUIRED (pipes cause subshell scope loss — silent false pass on `printf -v`); locale pinning for reproducibility.
- **R-1 critical lesson** (from F-1): the first parametrized test must be `case_0_canary_positive` to detect pipe-regression early (FR-007 module-load canary).
- **F-2 test files** (NEW per PRD §FR-9):
  - `tests/scripts/test_template_config_load_unit.py` (Test-1 — library function in isolation; 27 cases)
  - `tests/scripts/test_template_config_load_integration.py` (Test-2 — adversarial across 4 sites; H-2 TOCTOU residual fixture)
  - `tests/scripts/test_template_git_clone_timeout.py` (Test-3 — timeout + writer→reader round-trip per H-3)
  - `tests/scripts/test_init_sh_defaults_env.py` (Test-4 — init.sh end-to-end)
  - `tests/scripts/test_template_substitute_lint_no_eval.py` (Test-5 — `eval` removal verification)
  - `tests/scripts/conftest.py` (modified — session-scoped `hanging_upstream` fixture per M-3)

### Stack pack contracts

- `stacks/nextjs-supabase/defaults.env` and `stacks/fastapi-react/defaults.env` — both reside in tachi repo as canonical stack-pack examples.
- Allowed-key set per PRD FR-2: `TECH_STACK`, `TECH_STACK_DATABASE`, `TECH_STACK_VECTOR`, `TECH_STACK_AUTH`, `CLOUD_PROVIDER`.
- **Contract artifact** (NEW): `contracts/stack-pack-defaults-schema.md` — F-2 Stream 1 deliverable; documents the canonical key set + value-shape constraints (analogous to F-1's `contracts/personalization-schema.md`).

### Personalization snapshot

- `.aod/personalization.env` — canonical 12-element KV file (F-1 contract).
- Canonical placeholder array: `AOD_CANONICAL_PLACEHOLDERS` at `.aod/scripts/bash/template-substitute.sh:50-63` (12 elements; locked under Option (b) of F-1; possibly 13 under Option (a) if `PROJECT_PATH` was added).
- F-2 reuses the array as the whitelist for `aod_template_load_kv_file` at the personalization.env site.

---

## Architecture Constraints

### Bash 3.2 compatibility (NFR-1; macOS default shell)

**Verified compatible** in `aod_template_load_kv_file` design:

- `cat`, `printf`, `[[`, `=~`, parameter expansion `${var}`, indirect expansion `${!var}` (scalars only), here-strings `<<<`, command substitution `$(...)`, while-read loops, `&` background, `wait`, `kill`, `sleep`, regex match operator `=~`.

**NOT used** (bash 4+ only):

- Associative arrays (`declare -A`)
- `mapfile` / `readarray`
- Lowercase parameter expansion (`${var,,}`)
- `&>` redirection shorthand

### Three-decision precedent set by F-1

1. **Library-then-adoption sequencing internal to feature branch** (Q-1 Architect ruling): single PR, library + adopters. F-2 inherits.
2. **Pre-stripped templates beat in-place sed** (D-3 ADR-038): cleaner cross-platform behavior; eliminates OSTYPE branching. F-2 inherits the "data, not code" principle for config files.
3. **Posture-as-evidence cadence** (Constitution Principle VIII): visible posture commit converts `DETECTED → REMEDIATED` with full traceability. F-2 inherits.

### TOCTOU mitigation framing (H-2 corrected per Architect Pass 1)

`cat "$path"` opens the file once; the attacker race window collapses from "between two operations" to "before cat opens". The mitigation is "no double-read", not "no race". The residual race window is small but non-zero. ADR-040 §Decision documents this explicitly.

### Watchdog process-leak window (L-1)

Bare bash `( sleep ... && kill ... ) &` watchdog spawns an orphan if the outer script is interrupted. F-2 adds a `trap` in `aod_template_fetch_upstream` to clean up on SIGINT/SIGTERM/EXIT. Process-leak window: up to `$AOD_FETCH_TIMEOUT` seconds when outer script is interrupted.

### Empty unquoted value support (B-1)

Regex value alternation accepts empty unquoted (`KEY=` bare form) — required by version-file contract because `aod-kit-version` line 1 is literally `version=` when installed off a non-tagged commit. Zero-or-more quantifier `*` (NOT `+`) on the unquoted character class.

### Writer escape-pass removal (B-2 Path R-2 chosen)

F-1's `aod_init_read_validated` is **amended in F-2's PR** (NOT F-1's) to additionally reject `$`, `\`, backtick at the prompt boundary. The writer at `template-substitute.sh:566-571` no longer needs an escape pass — values are guaranteed metachar-free at the F-1 prompt. CHANGELOG note tied to F-2 documents this one-time contract amendment.

---

## Industry / External Research

### "Don't source untrusted config files" — security canon

- **OWASP A03 Injection** (CWE-78 Command Injection, CWE-94 Code Injection): bash `source` of attacker-controlled content is a textbook A03. The remediation is "treat data as data" — parse strictly, assign without re-interpretation.
- **`printf -v` pattern**: the canonical bash idiom for assigning a variable by computed name without `eval`. Compatible with bash 3.1+ (3.2 default on macOS).
- **No `bash -r` rescue**: `set -r` (restricted-shell) is not a security boundary — command substitution still works in restricted mode. Pre-emptively rejected in ADR-040 §Alternatives Considered (item 4).

### Bash `source` alternatives surveyed

| Approach | Pros | Cons | Verdict |
|---|---|---|---|
| Strict KV regex + `printf -v` | bash 3.2 compatible; zero deps; data-not-code | Per-line constant factor cost | **CHOSEN** (FR-1) |
| JSON config + `jq` | Standard format | New runtime dep; breaks adopter contract | Rejected (ADR-040 §Alternatives 1) |
| TOML config + parser | Standard format | No native bash parser; extra dep | Rejected (ADR-040 §Alternatives 2) |
| Bash sourcing in `set -r` | bash-builtin | Not a security boundary | Rejected (ADR-040 §Alternatives 4) |
| `bash -r -c` external | Process isolation | Breaks caller-scope assignment | Rejected (ADR-040 §Alternatives 5) |
| Source-then-`declare -p` diff | Detects unknown keys | Malicious code already ran | Rejected (ADR-040 §Alternatives 6) |

### Portable git clone timeout patterns

- **GNU coreutils `timeout(1)`**: not on macOS by default; would require Homebrew install (NFR-2 violation).
- **Bash `&` + watchdog**: bash 3.2 compatible, no external deps. **CHOSEN** (FR-6).
- **`git -c core.askPass=...` + signal trap**: requires recent git versions; less portable.

### Posture-claims-to-evidence ratio (enterprise pre-sales angle)

Source-of-truth positioning (per `tachi.md` strategic alignment): tachi is the upstream machine-readable contract. An enterprise security architect doing pre-sales review searches `grep -rn "source " .aod/ scripts/` against the post-F-1 / pre-F-2 tree and finds five `source` invocations and three `eval` invocations across the bash library — each one a procurement-stopping question. F-2 closes that surface in one coherent commit. The F-1+F-2 sequence demonstrates *repeatable* cadence — not a singleton response.

---

## Recommendations for Spec

1. **Mirror F-1 spec structure**: 8 User Stories (one per US-256-N from PRD), Edge Cases section, FR-001 to FR-009 (matching PRD FR-1 to FR-9), NFR-001 to NFR-006 (matching PRD NFR-1 to NFR-6), Key Entities, SC-001 to SC-015, Dependencies and Assumptions, Regression Protection Plan summary, Risks summary, References.

2. **No SC-015 in F-2**: F-1 had SC-015 as a non-DoD public visibility action (LinkedIn comment template). F-2 does NOT have a parallel public visibility commitment in the PRD; the cadence-demonstration angle is captured in US-256-6 (enterprise architect pre-sales review) and is part of the standard DoD via the release-please verification.

3. **Internal-Tooling Search NOT applicable**: F-1's spec captured a "5-minute internal-tooling search outcome" for FR-007 (Option a vs b for `PROJECT_PATH`). F-2 has no analogous search; all four call sites are explicit and pre-enumerated. Skip this section.

4. **Q-1..Q-6 already adjudicated in PRD v1.1**: PRD §Open Question Resolutions (v1.1) section folds in all six adjudications. Spec references the PRD section rather than re-deciding.

5. **Name FR-001 to FR-009 to align with PRD's FR-1 to FR-9**: PRD uses `FR-N` (single-digit); spec uses `FR-NNN` (zero-padded triple-digit) per spec template convention.

6. **Acceptance Criteria Rule** (per spec template): each AC begins with **Given** and follows Given/When/Then structure. ACs that cannot be automated are marked `[MANUAL-ONLY] <reason>` inline (e.g., post-merge `/security` re-scan, LinkedIn-related actions if any).

7. **Bash 3.2 compatibility constraint** appears in NFR-001; the per-FR text should call out specific bash-3.2-compatible primitives where relevant (e.g., FR-001 lists `${!var}`, `printf -v`, here-string `<<<`).

8. **Test files all subprocess-pytest**: per F-1 BLOCKING B-1; FR-009 explicitly notes this; spec notes the canonical test paths.

9. **Public ADR-040 reference**: spec notes its dual-commit pattern (Proposed → Accepted) per F-1 ADR-038 precedent and Q-6 ruling.

10. **Edge case coverage**: include the 8 PRD §Edge Cases (file ending without trailing newline, four-byte literal `a\nb`, multibyte UTF-8, bash 3.2 vs 4+, re-init attempt, hanging clone, watchdog SIGINT, F-1 prompt validator amendment).

---

## References

- **PRD**: [docs/product/02_PRD/256-source-pattern-hardening-2026-05-04.md](../../docs/product/02_PRD/256-source-pattern-hardening-2026-05-04.md)
- **F-1 spec** (mirror structure): [specs/248-substitution-surface-hardening/spec.md](../248-substitution-surface-hardening/spec.md)
- **F-1 ADR-038**: [docs/architecture/02_ADRs/ADR-038-placeholder-substitution-strategy.md](../../docs/architecture/02_ADRs/ADR-038-placeholder-substitution-strategy.md)
- **F-250 ADR-039** (test architecture canon): [docs/architecture/02_ADRs/ADR-039-test-architecture-fixture-scope-and-asymmetric-baseline.md](../../docs/architecture/02_ADRs/ADR-039-test-architecture-fixture-scope-and-asymmetric-baseline.md)
- **Constitution**: [.aod/memory/constitution.md](../../.aod/memory/constitution.md)
- **Git workflow rules**: [.claude/rules/git-workflow.md](../../.claude/rules/git-workflow.md)
- **F-212 release-please incident**: `.claude/rules/git-workflow.md` Reference Incident section
- **BLP-02 strategy** (if present): `_internal/strategy/BLP-02-enterprise-hardening.md`
- **Issue**: [#256](https://github.com/davidmatousek/tachi/issues/256)
