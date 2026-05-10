# Research Summary: F-5 Pre-commit Secret-Scanning Defaults

**Feature**: F-5 (Issue #282) — Pre-commit Secret-Scanning Defaults
**PRD**: [docs/product/02_PRD/282-pre-commit-secret-scanning-defaults-2026-05-09.md](../../docs/product/02_PRD/282-pre-commit-secret-scanning-defaults-2026-05-09.md)
**Date**: 2026-05-10
**Phase**: BLP-02 Wave 4+ — fifth and final feature in the 5-feature enterprise hardening initiative

---

## Knowledge Base Findings

Reusable patterns from BLP-02 Waves 1–4 (Institutional Knowledge Entries 1–5):

- **Documentation-only DoD waiver does NOT apply.** F-3 invoked Constitution Principle VII §Exceptions for the disclosure-channel-only feature. F-5 has executable surface (init.sh delta, `.pre-commit-config.yaml` invocation, AC-SPEC-1 synthetic-fixture rule-interaction test) so it must run TC waves on the touched executable surface.
- **Per-rule rationale catalog with one-to-one cross-link** (F-3, F-4 precedent): every entry in `.gitleaks.toml` (allow-list, custom rule, excluded path) MUST have a one-to-one rationale in `docs/standards/PRECOMMIT_HOOKS.md`. Reviewer cross-checks both files for parity.
- **CHANGELOG sibling-h3 BLP-02-cluster placement** (N-4 carry-forward through F-2/F-3/F-4): `### Pre-commit secret-scanning defaults (BLP-02 F-5)` at sibling level with `### Features`/`### Bug Fixes`, NOT under `### Features`.
- **PR title `feat(282):` from draft creation** at /aod.plan stage; pre/post-merge verification at /aod.deliver (release-please ~30s SLO; F-4 PR #279 opened ~23s post-squash-merge).
- **Posture-gap closure framing** (F-4 precedent): F-5 closes ZERO `/security` vuln_ids but DOES close a real attack surface (accidental credential commit). Frame both in spec.md.
- **AC-7 ANOMALY inline note pattern** (F-4 Entry 5): if any non-obvious gitleaks rule-interaction mechanic emerges during synthetic-fixture testing (e.g., global `[[allowlists]]` overriding per-rule allow-list, or `# gitleaks:allow` annotation precedence), document inline as `§ANOMALY` in `PRECOMMIT_HOOKS.md`.

**Key KB sources**: [docs/INSTITUTIONAL_KNOWLEDGE.md:177-291](../../docs/INSTITUTIONAL_KNOWLEDGE.md), [specs/272-security-md-disclosure/](../272-security-md-disclosure/), [specs/277-claude-permissions-baseline/](../277-claude-permissions-baseline/)

## Codebase Analysis

### `scripts/init.sh` — current shape (442 lines)

- Sources F-1 helper at line 28-34: `.aod/scripts/bash/init-input.sh` — provides `aod_init_read_validated` (validation triplet pattern, free-text input)
- **Hard-exit guard at lines 65-70**: checks `.aod/personalization.env` pre-existence; halts if found. Confirms Team-Lead A-3 finding — re-init double-prompt scenario is impossible.
- **Self-delete at line 442**: `rm -f scripts/init.sh` after successful run.
- **TTY detection NOT currently used** — script uses raw `read -p` for menu choices unconditionally (lines 85, 110, 144, 146, 148, 177).
- **Existing raw `read -p` usage** at lines 85/110/144/146/148/177 establishes precedent for single-character / short-bounded input. F-5's Y/n prompt is consistent with this established pattern.
- **Insertion point for F-5 opt-in prompt**: after line 177 (post-confirmation block, pre-snapshot-write at line 195).

**Source**: [scripts/init.sh:1-442](../../scripts/init.sh)

### F-1 substitution-surface helper (`aod_init_read_validated`)

- Function at [.aod/scripts/bash/init-input.sh:88](../../.aod/scripts/bash/init-input.sh) — reads byte-by-byte using `read -r -n 1 -d ""`, rejects NUL/control chars/over-length input, up to 3 re-prompts, exits non-zero on 3rd rejection. Uses `printf -v` (NOT `eval`) for safe caller-scope assignment.
- F-2 (#256) amended the helper to reject `$`, `\`, backtick at the prompt boundary.
- **F-5 waiver justification**: Y/n input is single character with default-Y fallback — trivially-bounded input space below F-1's free-text-injection threat threshold. ADR-042 §Consequences must document this waiver verbatim (per Architect C-3 resolution).

### GitHub Actions workflow inventory

- 3 existing workflows totaling ~70 LOC: `release-please.yml`, `tachi-mmdc-preflight.yml`, `tachi-pytest.yml`.
- **No existing `security-scan.yml` or `gitleaks.yml`** — confirms Team-Lead A-2 finding. F-5 introduces NEW dedicated `.github/workflows/gitleaks.yml` (~25-40 LOC).
- **F-256 lock-step lesson**: when adding new test surface, update `tachi-pytest.yml` `paths:` filter AND `pytest` invocation in the same commit. F-5's new gitleaks workflow does NOT need pytest changes — the synthetic-fixture rule-interaction test is gitleaks-driven, not pytest-driven.

### F-3 / F-4 precedent files

- `docs/standards/CLAUDE_PERMISSIONS.md` (F-4) — ~289 LOC self-contained operator handbook. Sections: Why this hook ships / Installation / Per-rule rationale / Opt-out paths / Known limitations / Adopter customization. F-5's `docs/standards/PRECOMMIT_HOOKS.md` follows same template.
- `docs/architecture/02_ADRs/ADR-041-claude-permissions-baseline.md` — ~195 LOC. Sections: Context / Decision (7 DIs) / Alternatives (1 evaluated) / Consequences. F-5's ADR-042 expected ~130-180 LOC with 9 alternatives + pin-bump cadence + raw-read-p waiver.
- `SECURITY.md` is at repo root (NOT `docs/standards/`); F-3 followed GitHub-canonical 5-section template.

**Sources**: [docs/standards/CLAUDE_PERMISSIONS.md](../../docs/standards/CLAUDE_PERMISSIONS.md), [docs/architecture/02_ADRs/ADR-041-claude-permissions-baseline.md](../../docs/architecture/02_ADRs/ADR-041-claude-permissions-baseline.md), [docs/architecture/02_ADRs/ADR-038-placeholder-substitution-strategy.md](../../docs/architecture/02_ADRs/ADR-038-placeholder-substitution-strategy.md), [docs/architecture/02_ADRs/ADR-040-config-file-parsing-hardening.md](../../docs/architecture/02_ADRs/ADR-040-config-file-parsing-hardening.md)

### Existing fixture surface

- No deliberately-fake credential fixtures exist in `tests/fixtures/`. AC-SPEC-1 must CREATE synthetic-fixture cases under `tests/fixtures/gitleaks-rule-interaction/` (per PRD §AC-SPEC-1).
- Existing fixture conventions (config-load valid/adversarial split) inform structure: separate `placeholder/` (allow-listed-and-passes), `staged-credential/` (rule-fires), `path-allow-listed/` (under fixture path; rule does NOT fire).

### `.aod/personalization.env` gitignore

Confirmed at [.gitignore:226](../../.gitignore) — explicit gitignore with rationale comment per F-1 #248. F-5's `.aod/personalization.env.example` (NEW template file) is explicitly tracked (not gitignored), allowing adopters to discover expected keys + giving `.gitleaks.toml` a path-allow-listed location.

### Bash wrapper-script conventions

Established pattern across `.aod/scripts/bash/`: `#!/usr/bin/env bash` shebang; stderr via `>&2`; color-coded warnings; exit codes 0/1/8. The new `.aod/scripts/bash/precommit-wrap.sh` follows this style.

### Standards index placement

[docs/standards/README.md](../../docs/standards/README.md) — `PRECOMMIT_HOOKS.md` inserted between `CLAUDE_PERMISSIONS.md` and `DEFINITION_OF_DONE.md` (alphabetical) with cross-link to ADR-042.

## Architecture Constraints

- **Constitution Principle VIII (Product-Spec Alignment)**: spec.md MUST trace each FR back to a PRD requirement. Coverage gate enforced at PM sign-off.
- **Constitution Principle VII (Definition of Done)**: F-5 has executable surface (init.sh delta, gitleaks invocation), so DoD applies fully — TC waves required for touched surface. §Exceptions waiver does NOT apply.
- **Git workflow** ([.claude/rules/git-workflow.md](../../.claude/rules/git-workflow.md)): branch `282-pre-commit-secret-scanning-defaults` (NNN-feature-name); PR title `feat(282): pre-commit secret-scanning defaults` from draft creation; release-please verification at /aod.deliver.
- **F-1 dependency satisfied**: `.aod/personalization.env` is gitignored on `main`. F-5 builds against this baseline (per Team-Lead A-4).
- **No `finding.yaml` / taxonomy schema changes** (12th feature in a row preserving detection-tier contract continuity).

## Industry Research

### Gitleaks releases + pinning

- **Latest gitleaks**: v8.30.1 (2026-03-21). v8.30.0 added Looker / Airtable PAT detection.
- **Latest pre-commit framework**: v4.6.0 (2026-04-21). PRD's R-10 floor of `>= 3.5.0` is conservative-and-safe (current is two majors ahead).
- **Pinning approach**: Official gitleaks recommends tag-based pinning (`rev: v8.30.1`); both tags and SHAs are valid in pre-commit framework. **`pre-commit autoupdate --freeze`** converts tags to commit SHAs for guaranteed immutability. **Recommendation for tachi**: pin to a tag for readability + use `--freeze` to also store the SHA for supply-chain hygiene per PRD §R-3.

### `.gitleaks.toml` schema (v8.25.0+)

- **Breaking change**: `[allowlist]` → `[[allowlists]]` (TOML array of tables). Tachi MUST target the new schema.
- **`[extend]`**: `useDefault = true` inherits built-in rules; `disabledRules` for selective opt-out; external paths supported.
- **Global vs per-rule allow-lists**: Global `[[allowlists]]` have higher precedence than per-rule `[[rules.allowlists]]`.
- **Custom rule fields**: `id`, `description`, `regex`, `secretGroup`, `entropy` (Shannon threshold), `path`, `keywords`, `tags`.
- **Composite rules (v8.28.0+)**: `[[rules.required]]` table with proximity constraints — not needed for F-5 baseline.

### Gitleaks output behavior — confirms Architect C-2

**gitleaks does NOT support stderr-message templating at the CLI level.** Default verbose output goes to stdout (with `-v`/`--verbose`), not stderr. `--report-format=json|csv|junit|sarif|template` controls FILE output (paired with `--report-path`); the `template` format uses Go `text/template` + Masterminds/sprig — but this is a REPORT FILE template, not a stderr template. There is no documented CLI flag to inject custom messages into the human-readable terminal output. **Wrapper script REQUIRED for AC-15** (rule ID + file:line + bypass guidance + docs link contract).

### Gitleaks CLI shape change (v8.19.0+)

`detect` / `protect` deprecated → use `gitleaks git` / `gitleaks dir` / `gitleaks stdin`. **Recommended for F-5**:
- Pre-commit hook: `gitleaks stdin` on staged diff (fast, single-commit scope). Pre-commit framework default integration uses `gitleaks protect --staged` historically; we transition to `gitleaks git --staged` or `gitleaks stdin` per current shape.
- CI parity: `gitleaks git` for full-repo scan on PR (per Q5 PRD position).

### gitleaks-action license issue

- v2.x of `gitleaks/gitleaks-action` is **proprietary** (license changed from MIT pre-v2.0.0).
- **Free for personal accounts**; **organizations require a `GITLEAKS_LICENSE` key** (paid).
- Tachi is org-owned (`davidmatousek/tachi`) — would require paid license.
- **Recommendation**: invoke gitleaks **binary directly** in `.github/workflows/gitleaks.yml` (download release tarball, verify checksum, run `gitleaks git`). Avoids proprietary license while keeping MIT-licensed gitleaks core.

### Bypass mechanisms (verified)

- `SKIP=gitleaks git commit ...` — pre-commit framework standard, skips one hook.
- `# gitleaks:allow` inline — per-line opt-out; `--ignore-gitleaks-allow` globally disables.
- `git commit --no-verify` — bypasses entire pre-commit chain (framework feature).
- Bonus: `.gitleaksignore` (fingerprint-level, marked experimental); `--baseline-path` for previously-detected findings.

### Comparison-matrix corrections to PRD

PRD line 376 says trufflehog runtime is "Python" — **INCORRECT**. trufflehog v3+ is **Go** (license is AGPL-3.0; pre-v3.0 was GPL-2.0 + Python). Spec.md must correct this. License claims for all other tools are accurate per PRD.

## Recommendations for Spec

1. **Pin gitleaks to v8.30.1 in `.pre-commit-config.yaml`** with `pre-commit autoupdate --freeze` to convert tag → commit SHA for supply-chain hygiene. PRD's "pinned commit hash (NOT a floating tag)" framing is satisfied by the freeze step.
2. **Use new `[[allowlists]]` schema** (TOML array of tables) — gate on gitleaks >= v8.25.0 (current is v8.30.1).
3. **Use new CLI shape** (`gitleaks git --staged` / `gitleaks stdin`); avoid deprecated `detect`/`protect`.
4. **Skip `gitleaks-action` for org repo** — invoke gitleaks binary directly in `.github/workflows/gitleaks.yml`.
5. **Wrapper script REQUIRED** at `.aod/scripts/bash/precommit-wrap.sh` (Q9 resolved: separate file for testability) — gitleaks does NOT support stderr templating (Architect C-2 confirmed by independent verification).
6. **Raw `read -p` waiver** documented in ADR-042 §Consequences (Q10 resolved: PRD position; single-char Y/n below F-1 free-text-injection threat threshold).
7. **AC-SPEC-1 synthetic-fixture rule-interaction test** as /aod.spec entry-criteria — preventive false-positive verification per Architect C-4. Fixture cases: placeholder env vars / populated env vars / fixture credentials / `.security/exceptions.jsonl` entries / docs placeholders / `.aod/personalization.env.example` template / 10-20 expected adopter cases.
8. **CHANGELOG sibling-h3 BLP-02-cluster** placement — N-4 carry-forward through F-2/F-3/F-4 establishes 4th consecutive convention.
9. **PR title `feat(282):` from draft creation** at /aod.plan; release-please ~30s SLO at /aod.deliver.
10. **PRD trufflehog runtime correction**: spec + ADR-042 must say trufflehog runtime is **Go** not Python (PRD §Tool Selection table line 376).
11. **`[ -t 0 ]` TTY check** for non-interactive skip in init.sh (Q4 resolved: TTY check baseline + `--no-precommit` flag override per Architect Q4 expansion).
12. **Q1/Q2 warn-only** for custom rules `tachi-personalization-env` and `tachi-security-exceptions-jsonl` (PRD position) — non-blocking warnings teach adopters without breaking CI on first run.
13. **Q5 full-repo scan on PRs** for CI parity (PRD position) — PR-diff scope risks missing pre-existing-but-unscanned credentials in older commits.
14. **Q7 README pointer under existing "Security" subsection** consistent with F-3 SECURITY.md and F-4 CLAUDE_PERMISSIONS.md placement.

## References

- PRD: [docs/product/02_PRD/282-pre-commit-secret-scanning-defaults-2026-05-09.md](../../docs/product/02_PRD/282-pre-commit-secret-scanning-defaults-2026-05-09.md)
- F-3 spec/plan/tasks: [specs/272-security-md-disclosure/](../272-security-md-disclosure/)
- F-4 spec/plan/tasks: [specs/277-claude-permissions-baseline/](../277-claude-permissions-baseline/)
- ADR-038 (F-1): [docs/architecture/02_ADRs/ADR-038-placeholder-substitution-strategy.md](../../docs/architecture/02_ADRs/ADR-038-placeholder-substitution-strategy.md)
- ADR-040 (F-2): [docs/architecture/02_ADRs/ADR-040-config-file-parsing-hardening.md](../../docs/architecture/02_ADRs/ADR-040-config-file-parsing-hardening.md)
- ADR-041 (F-4): [docs/architecture/02_ADRs/ADR-041-claude-permissions-baseline.md](../../docs/architecture/02_ADRs/ADR-041-claude-permissions-baseline.md)
- Gitleaks GitHub: https://github.com/gitleaks/gitleaks
- Pre-commit framework: https://pre-commit.com/
- Gitleaks v8.30.1 release: https://github.com/gitleaks/gitleaks/releases/tag/v8.30.1
- Gitleaks Action license: https://github.com/gitleaks/gitleaks-action
