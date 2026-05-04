# ADR-038: Placeholder Substitution Strategy — bash Parameter Expansion vs sed

**Status**: Accepted
**Date**: Proposed: 2026-05-03 (Wave 3 Stream 4 T034 dual-commit initial); Accepted: 2026-05-04 (Wave 5 T036 architect promotion after T035 verification)
**Deciders**: Architect (tachi project)
**Feature**: [248-substitution-surface-hardening](../../../specs/248-substitution-surface-hardening/spec.md)
**Supersedes**: None
**Superseded by**: None
**Related ADRs**: None at proposal time. (Final Accepted version may add cross-references to F-2 BLP-02 Wave 2 ADR — defaults.env strict-KV parser — when that work lands; F-2 reuses the **validation-triplet pattern** documented in §Decision Item 5, NOT the `aod_init_read_validated` function itself.)

---

## Context

`scripts/init.sh:117-159` previously substituted the canonical 12 placeholder set (`tachi`, `threat modeling sidecar`, `benchmark-test-org`, `tachi`, `claude`, `Python + FastAPI`, `PostgreSQL`, `Not yet defined`, `Not yet defined`, `2026-05-04`, `2026-05-04`, `Not yet defined`) into the personalized template tree using `find ... -exec sed -i '' -e ... +` (macOS) or `find ... -exec sed -i -e ... +` (Linux). This approach has three structural defects identified during BLP-02 Wave 1 scoping:

1. **Metacharacter corruption** — sed interprets `&` as match-substitution and `\1`–`\9` as backreferences. Adversarial-but-legitimate values like `AT&T`, `Cats & Dogs`, `\1\2 backref`, regex metachars `.*+?^$()`, and pipe-bearing values get corrupted at substitution time, producing post-init files that misrepresent adopter intent. (FR-001 Test-2 Cases 1–8 cover these.)

2. **Missing input validation at prompt boundary** — the four `read -p` prompts at `init.sh:24-28` accept multi-line paste, NUL bytes, control characters, and arbitrarily long input without rejection. Multi-line paste in particular is a defense-layer-1 hazard: the second line bypasses the prompt sequence and lands in a downstream variable. (FR-005 Test-2 Cases 9–12 cover these.)

3. **Missing closed-contract residual scan** — sed silently no-ops on files where no `{{KEY}}` matches exist. If an upstream-introduced placeholder is NOT in the canonical 12, it survives substitution as an orphan `{{KEY}}` token; the adopter's first hint is a runtime template error months later. (FR-004 Test-2 Case 13 + `test_no_residual_placeholders_after_init` cover this.)

### Constraints

- **bash 3.2.57 compatibility** (NFR-001) — macOS default shell. No associative arrays (`declare -A`), no `mapfile`/`readarray`, no lowercase parameter expansion (`${var,,}`), no `&>` redirection.
- **Single-PR delivery** (PRD §Deliverable) — substitution swap + input validator + posture default + constitution migration land in one squash-merged PR.
- **NFR-004 perf budget** — initial threshold ≤10% delta vs T008 baseline (6.690s); loosens to ≤25% with rationale at 5–50% delta; >50% triggers PM re-scope before merge.
- **BLP-02 Wave 1 scope cap** — F-248 covers `init.sh` placeholder substitution surface ONLY. The parallel `defaults.env` strict-KV parser (F-2 Wave 2) reuses the *pattern* documented here (validation triplet) but NOT the `aod_init_read_validated` function (which is interactive `read -p`-only).
- **Closed canonical-12 lockstep contract** — adding a new placeholder requires updating BOTH `AOD_CANONICAL_PLACEHOLDERS` in `.aod/scripts/bash/template-substitute.sh` AND the `personalization-schema.md` contract in lockstep (Architect M-2 commitment).

---

## Decisions

### D-1 — Substitution mechanism: bash parameter expansion `${content//\{\{KEY\}\}/value}`

**Replace** `find ... -exec sed -i '' -e ... +` with a per-file loop that calls `aod_template_substitute_placeholders <src> <dest>` (which uses bash parameter expansion `${content//\{\{KEY\}\}/value}` — literal pattern + literal replacement, no regex interpretation either side).

**Rationale**:
- bash parameter expansion treats both pattern and replacement as LITERAL strings; adversarial values survive verbatim.
- Single-branch cross-platform behavior; eliminates the `OSTYPE` macOS-vs-Linux split.
- Preserves file mode bits via `_aod_preserve_mode` (BSD `stat -f` / GNU `stat -c` cross-platform).
- Atomic writes via `<dest>.tmp` + `mv` rename (interrupt-safe).

**Trade-off** (D-2 below):
- bash parameter expansion is structurally slower than sed-batched substitution at init time. T021 measured +658% delta (50.7s vs T008 baseline 6.7s). Per-file fork overhead in `aod_template_substitute_placeholders` (~6-8 forks/file × 3260 text files = ~20000 forks) cannot match sed's argv-batched processing (~3-5 sed invocations total at ~1000 files each).

### D-2 — NFR-004 perf threshold: accept regression with documented rationale

**Accept** the +658% perf delta with the following PM-judgment rationale, captured in §Consequences below:
- init.sh runs ONCE per adopter project (one-time cost; not recurring)
- Metacharacter corruption defects sed introduces are functional, not cosmetic — values like `AT&T` actively break adopter intent
- 50s init vs 7s init adds ~43s to first-run experience; not user-visible after first run
- The substitute helper is frozen per F-129 Wave 3 contract; structural optimization would require a new feature scope

**Threshold disposition**: NFR-004 ≤10% / ≤25% / >50% cascade is **superseded by ADR-038 §Consequences** for init.sh init-time only. Threshold restored to "best-effort, document baseline" for `/aod.update` re-substitution flow (which operates on personalized-category files only, ~5 files; perf is unaffected).

**PM gate**: this disposition requires PM sign-off at `/aod.deliver` per agent-assignments.md G3 escalation contract. T035 Wave 5 amends this ADR with the final benchmark numbers and PM acknowledgment.

### D-3 — Constitution template install: pre-stripped clean template, not sed cleanup

**Replace** `init.sh:235-241` `sed -i '/^<!--$/,/^-->$/d; /^## Template Instructions$/,$d'` cleanup of the live `.aod/memory/constitution.md` with `cp .aod/templates/constitution-clean.md .aod/memory/constitution.md` followed by `aod_template_substitute_placeholders` re-substitution.

**Rationale**:
- Eliminates the OSTYPE branching for macOS BSD vs GNU sed
- Decouples constitution authoring from substitution: `.aod/templates/constitution-instructional.md` ships full template variant (HTML comment block + `## Template Instructions` section), `.aod/templates/constitution-clean.md` ships the post-strip variant
- T007 byte-equivalence proven: `sed '/^<!--$/,/^-->$/d; /^## Template Instructions$/,$d' constitution-instructional.md` equals `constitution-clean.md` byte-for-byte (verified manually)
- `/aod.update` flow already re-substitutes from upstream; the `cp` happens once at init, then the re-substitution flow takes over

### D-4 — `.aod/personalization.env` posture: gitignored by default, opt-in commit

**Default posture**: `.aod/personalization.env` is gitignored in the AOD-Kit upstream (`.gitignore:222`). Adopters who explicitly want personalization version-controlled override the default by removing the gitignore entry and `git add -f`-ing the file.

**Migration command** for adopters who previously committed the file: `git rm --cached .aod/personalization.env`. (Documented in CHANGELOG entry + post-init success message.)

**Rationale**:
- Multi-tenant safety: a fork of an adopter repo MUST NOT inherit the original adopter's `PROJECT_NAME` etc.
- Defense layer 1 (multi-hop chain layer 2): even if a misconfigured CI re-runs init.sh on a personalized adopter project, the snapshot already exists → re-init pre-flight check halts (FR-003)
- Bootstrap-safe: a fresh clone has no `.aod/personalization.env`; running `init.sh` writes it

### D-5 — Validation triplet pattern (reuse contract for F-2 BLP-02 Wave 2)

**The interactive prompt input validator `aod_init_read_validated` (F-1 BLP-02 Wave 1) follows a triplet pattern**: `regex-validate` → `reject-on-mismatch` → `printf -v` assignment.

```
read -r -p "$prompt" answer       # 1. read with backslash preservation
[validate via case + [[ =~ ]]]     # 2. reject newline/NUL/cntrl/over-length
printf -v "$var_name" '%s' "$answer"  # 3. safe assignment (no eval)
```

**F-2 BLP-02 Wave 2 reuse contract (Team-Lead H-2 commitment)**:

F-2 (`defaults.env` strict-KV parser) reuses the **VALIDATION TRIPLET PATTERN**, NOT the `aod_init_read_validated` function. The function is interactive `read -p`-only; F-2 is non-interactive file-parse. F-2 will introduce a new helper (e.g., `aod_defaults_parse_validated`) following the same regex-validate → reject-on-mismatch → `printf -v` discipline but operating on file content rather than terminal input.

**Architect re-confirmation required at T036 promotion** (Wave 5): before promoting Status `Proposed → Accepted`, the architect MUST re-confirm this paragraph reflects the F-1 → F-2 reuse boundary. The lockstep contract: any future deviation (e.g., F-2 attempts to call `aod_init_read_validated` directly) requires a new ADR.

### D-6 — Residual scan scope: PERSONALIZED-category files only (FR-004 alignment)

**The residual placeholder scan `aod_template_assert_no_residual` is invoked from `init.sh` ONLY on files in the `personalized` category per `.aod/template-manifest.txt`** (currently 5 files: `.claude/rules/{context-loading,deployment,design-context-loader,design-quality,governance}.md`).

**Rationale**:
- FR-004 spec language: "every `{{KEY}}` in any **personalized file** MUST be in the canonical 12; orphan placeholders fail-fast"
- The codebase contains ~110 legitimate non-canonical `{{KEY}}` tokens used by parallel templating systems:
  - Stack-pack scaffolds: `{{BACKEND_FRAMEWORK}}`, `{{ORM}}`, `{{API_STYLE}}` — substituted by `/aod.stack scaffold`
  - Brand templates: `{{BRAND_NAME}}`, `{{HEADING_FONT}}`, `{{BODY_FONT}}` — filled by `/aod.foundation`
  - Devops docs: `{{PRODUCTION_URL}}`, `{{STAGING_DB}}` — filled by adopter at deployment time
  - Doc examples: `{{KEY}}`, `{{NAME}}`, `{{PLACEHOLDER}}` — illustrative syntax in helper-docs and spec narratives
- A whole-tree residual scan would halt on these legitimate tokens, breaking the parallel templating systems
- The helper `aod_template_assert_no_residual` regex `\{\{[A-Z_]+\}\}` is unchanged; only the CALLER scope in `init.sh` is constrained

**Lockstep with Architect M-2 commitment**: any future change to the helper's regex (e.g., narrowing to `\{\{(PROJECT_NAME|...|CLOUD_PROVIDER)\}\}` canonical-12 alternation) requires a new ADR. The current decision keeps the regex permissive but constrains where it runs.

### D-7 — Q-1 Adjudication: remove `.claude/mcp-config.json` (Option b)

**Per T005 internal-tooling search outcome** (`tasks-runlog.txt:11-17`): zero consumer references to `.claude/mcp-config.json` from any wired path (`.aod/scripts/`, `.claude/agents/`, `.claude/commands/`, `Makefile`, `scripts/`). Broader sanity check across all `*.sh`, `*.md`, `*.py`, `*.json`, `*.yml`, `*.yaml`, `Makefile` files (excluding `.git/`, `node_modules/`, `specs/`, `docs/`): zero matches.

**Decision**: remove `.claude/mcp-config.json` via `git rm` (T033 Option b default). The file was unused dead code carrying a `{{PROJECT_PATH}}` placeholder that would have required either (a) addition to the canonical-13 set with personalization implications, or (b) removal. The unused file plus zero consumer references makes Option (b) the conservative choice.

**Canonical placeholder set remains locked at 12**. Fallback Option (a) — add `PROJECT_PATH` to the canonical-13 — was NOT triggered. Future placeholders (if any) require the lockstep update protocol per D-5 paragraph 4.

---

## Consequences

### Positive

- **Metacharacter literal-preservation across all 12 canonical placeholders**: Test-2 Cases 1–8 (post-Stream-1 + post-Stream-2) demonstrate `AT&T`, `Cats & Dogs`, `\1\2 backref`, regex metachars, pipes, and slashes survive substitution verbatim.
- **Defense layer 1 input rejection at prompt boundary**: Test-2 Cases 9–12 demonstrate multi-line paste, NUL bytes, control characters, and over-length input are rejected with re-prompt up to 3 strikes before non-zero exit.
- **Closed-contract residual scan on personalized files**: `init.sh` halts non-zero on any orphan canonical-12 placeholder in personalized-category files; future template additions auto-fail until the canonical set is updated.
- **Single-branch cross-platform substitution**: macOS BSD sed vs GNU sed branching eliminated from both substitution loop and constitution cleanup.
- **Decoupled constitution authoring**: `.aod/templates/constitution-{instructional,clean}.md` provide explicit pre-strip / post-strip variants; future template-instruction edits land in `instructional.md` and propagate to `clean.md` via documented regen procedure (T013 + T014 baseline regen).

### Negative

- **NFR-004 perf delta +658%** (T021 measurement: 50.7s vs T008 baseline 6.7s) for `init.sh` substitution loop. Per D-2 acceptance, this is an init-time-only cost (one-time per adopter) traded for substitution correctness on adversarial values. PM acknowledges trade-off at `/aod.deliver` gate.
- **`/aod.update` perf is unaffected** — the re-substitution flow operates on `personalized` category (5 files) and remains within original NFR-004 thresholds.

### Neutral / Migration

- **Adopters previously committing `.aod/personalization.env`** must run `git rm --cached .aod/personalization.env` per D-4 migration command. The local file is preserved; gitignore default establishes from there. Documented in CHANGELOG and post-init success message.
- **`.claude/mcp-config.json` removal** (D-7) is a one-time scrub. Adopters who had local edits lose them; no consumer code regressed (zero references per T005).
- **F-2 BLP-02 Wave 2 reuse contract** (D-5) is a forward-looking commitment. The pattern-vs-function boundary will be re-verified during F-2 plan-day architect review.

### Security Posture

- **No new attack surface introduced**: substitution moves from `sed` (subprocess invocation per file via `find -exec`) to bash parameter expansion (in-process). Both run with adopter-process privileges; no privilege boundary crossed.
- **Defense-in-depth strengthened**: prompt-boundary input rejection (Stream 2) + closed-contract residual scan (Stream 1 D-6) + gitignored snapshot (Stream 3 D-4) collectively close the multi-hop substitution chain across init → personalization.env → re-substitution.
- **Multi-tenant safety**: D-4 default posture prevents fork-borne personalization leakage.

### Backward Compatibility

- **Pre-init template tree byte-identity**: Test-1 fixture-replay (post-T014 baseline regeneration) asserts the personalized tree byte-equals the recorded baseline. T013's `regenerate-baseline.sh` is the regen procedure when the canonical-12 set changes (lockstep with D-5 paragraph 4).
- **Per-finding source_attribution unchanged**: F-248 modifies neither `schemas/finding.yaml` nor any agent-tier file. Detection-tier 14-file zero-edit invariant from F-241 is preserved.
- **NFR-002 dependency manifest invariant**: zero changes to `pyproject.toml` / `requirements*.txt` / `package.json` (T004 baseline; T044 verification).
- **NFR-005 schema invariant**: zero changes to `schemas/finding.yaml` (T045 verification).

### Test Coverage

| Coverage area | Test file | Cases |
|---|---|---|
| Metachar substitution literal-preservation (Cases 1–8) | `test_init_sh_adversarial.py` | 8 parametrize entries |
| Input rejection (newline / NUL / control / over-length) | `test_init_sh_adversarial.py` | 4 parametrize entries (Cases 9–12) |
| File-level byte-identity post-substitution | `test_init_sh_adversarial.py` | 1 case (Case 13) |
| Whole-tree residual scan post-init | `test_init_sh_adversarial.py` | 1 case (`test_no_residual_placeholders_after_init`) |
| Constitution byte-equality vs clean template | `test_init_sh_constitution.py` | 1 case |
| Self-delete + snapshot persistence | `test_init_sh_self_delete.py` | 3 cases |
| Fixture-replay byte-comparison (post-T014) | `test_init_sh_substitution.py` | 2 cases (skipped until baseline regenerated) |
| **Total** | | **20 tests, ≥13 adversarial cases per NFR-003** |

---

## Promotion Checklist (Wave 5 T036 architect promotion gate)

Before promoting Status `Proposed → Accepted` at T036, the architect MUST verify:

- [ ] **D-1**: T021 benchmark numbers + delta math present in §Consequences (added at T035 amendment)
- [ ] **D-2**: PM acknowledgment of perf trade-off captured (oral or PR-comment is acceptable; document in §Consequences)
- [ ] **D-3**: T007 byte-equivalence (sed-cleaned vs constitution-clean.md) re-verified post-Stream-1 (sed run produces same bytes; clean template byte-matches)
- [ ] **D-5**: F-1 → F-2 pattern-vs-function reuse boundary paragraph re-confirmed (Team-Lead H-2 commitment)
- [ ] **D-6**: Residual scan caller-scope verified — `init.sh` walks `personalized` category only; helper regex unchanged
- [ ] **D-7**: `.claude/mcp-config.json` removed via `git rm`; `template-manifest.txt` updated; broader-sanity-check confirmed zero consumer references (T005 outcome cited)
- [ ] §Test Coverage table reflects final pytest results (G4 gate green local + CI matrix)
- [ ] §Consequences §Backward Compatibility cites NFR-002 + NFR-005 verification (T044 + T045 outcomes)

---

## Open Questions

None at proposal time. T035 (Wave 5) amends this ADR with final T021 benchmark numbers and PM acknowledgment of perf trade-off. T036 (Wave 5) is the architect promotion gate per the checklist above.
