# Research Summary: F-1 Substitution Surface Hardening (Feature 248)

**Feature**: BLP-02 Wave 1 — close 5 /security vulns in `init.sh` substitution surface
**PRD**: [docs/product/02_PRD/248-substitution-surface-hardening-2026-05-03.md](../../docs/product/02_PRD/248-substitution-surface-hardening-2026-05-03.md)
**Created**: 2026-05-03

## Knowledge Base Findings

**ADR-038 — to be authored, not yet citable**: Highest existing ADR is ADR-037. ADR-038 must be authored by F-1 as a hard deliverable (PRD §SC-10, FR-6). Use the dual-commit pattern (Proposed → Accepted) per BLP-01 precedent (ADR-027/028/029/030/031). Template at [docs/architecture/02_ADRs/ADR-000-template.md](../../docs/architecture/02_ADRs/ADR-000-template.md).

**Highly relevant prior ADR — ADR-009**: [docs/architecture/02_ADRs/ADR-009-template-variable-expansion-scope.md:12](../../docs/architecture/02_ADRs/ADR-009-template-variable-expansion-scope.md) ratified "sed at make init time" (Feature 061, 2026-03-03) — the exact mechanism F-1 is now superseding on the *mechanism* axis. ADR-038 must cite ADR-009 in §Related Decisions; placeholder enumeration in ADR-009 remains valid.

**Existing safe substitution helper (already shipped)**: [.aod/scripts/bash/template-substitute.sh:318-411](../../.aod/scripts/bash/template-substitute.sh) — `aod_template_substitute_placeholders` uses `${content//\{\{KEY\}\}/$val}` (literal substitution), atomic .tmp→mv, mode preservation. Currently used by `/aod.update`. F-1 wires `init.sh` to existing function — not new code. Companion `aod_template_assert_no_residual` at lines 414-457; canonical 12-element placeholder array at lines 50-63.

**Empty institutional KB**: [docs/INSTITUTIONAL_KNOWLEDGE.md](../../docs/INSTITUTIONAL_KNOWLEDGE.md) is the unedited template. No `patterns/` or `bugs/` directories. Institutional learning lives in CHANGELOG entries, ADRs, and `docs/devops/`.

**Prior bash bug pattern — Feature 132 lesson**: [docs/devops/CI_CD_GUIDE.md:372](../../docs/devops/CI_CD_GUIDE.md) — command substitution under `set -euo pipefail` aborts before `local rc=$?` captures rc on bash 3.2. Use explicit `set +e`/`set -e` bracket. Apply this discipline to the new `aod_init_read_validated` helper.

## Codebase Analysis

**Vulnerable code locations (all confirmed)**:

| Vuln ID | File:Line | Description |
|---------|-----------|-------------|
| TACHI-VULN-6bc17fd01ac8 (HIGH) | [scripts/init.sh:117-159](../../scripts/init.sh) | `replace_in_files()` — 12 sed substitutions, macOS branch at L124 + Linux branch at L144 |
| TACHI-VULN-77f0519f9cfb (MEDIUM) | [scripts/init.sh:24-28](../../scripts/init.sh), :74, :76, :78 | 7 unvalidated `read -p` prompts (no length/charset/newline guards) |
| TACHI-VULN-bc67ca510ea9 (MEDIUM) | [.gitignore:222](../../.gitignore) | Already present (verified) — needs CHANGELOG documentation of git-rm migration for existing adopters |
| TACHI-VULN-30bbfd90959a (LOW) | [.claude/mcp-config.json:6](../../.claude/mcp-config.json), :9 | Two `{{PROJECT_PATH}}` orphans; not in canonical-12 |
| TACHI-VULN-18127be5d214 (LOW) | [scripts/init.sh:235-241](../../scripts/init.sh) | 4 sed calls (2 macOS + 2 Linux) on `constitution.md` for HTML-comment + Template-Instructions deletion |

**Init.sh reorder constraint (Architect Pass 1 BLOCKING B-2)**: Current flow: set vars → sed-substitute → write `.aod/personalization.env` → version-pin → self-delete (`scripts/init.sh:354 rm -f scripts/init.sh`). New flow: set vars → write snapshot FIRST → `aod_template_load_personalization_env` → `aod_template_substitute_placeholders` → residual scan → version-pin → self-delete. Self-delete IS the re-init prevention mechanism (Q-3 Option b).

**Test infrastructure**: pytest-via-subprocess (NOT bats). Existing convention: `tests/scripts/test_*.py` + module-scoped fixtures in `conftest.py`. Existing CI matrix runs on `macos-latest` (bash 3.2.57) + `ubuntu-latest` (bash 5.x). No bats integration; bootstrapping bats is explicitly out of scope (SC-14). New tests land at `tests/scripts/test_init_sh_substitution.py` and `tests/scripts/test_init_input_validation.py`.

**Canonical placeholder set (locked at 12)**: PROJECT_NAME, PROJECT_DESCRIPTION, GITHUB_ORG, GITHUB_REPO, AI_AGENT, TECH_STACK, TECH_STACK_DATABASE, TECH_STACK_VECTOR, TECH_STACK_AUTH, RATIFICATION_DATE, CURRENT_DATE, CLOUD_PROVIDER. **No PROJECT_PATH** (Q-1 → remove `mcp-config.json`).

**Constitution sed → pre-stripped template path**: New file at `.aod/templates/constitution-clean.md` (not repo root). FR-5 canonical path is `.aod/templates/`.

## Architecture Constraints

**Backwards compatibility (Constitution III, NON-NEGOTIABLE)**: Re-init NOT supported (Q-3 Option b). Existing-adopter migration is gitignore-only via `git rm --cached .aod/personalization.env` documented in CHANGELOG. Substitution semantics shift from regex-with-metachar to literal — strict improvement, byte-identical on valid inputs.

**Schema invariant (NFR-5)**: Zero `finding.yaml` schema bump. Eighth consecutive feature preserving the BLP-01 detection-tier contract.

**Bash 3.2 compatibility (NFR-1, R-1)**: macOS pre-installed bash. No associative arrays, no `mapfile`/`readarray`, no `${var,,}`. Existing safe function is already 3.2-compatible.

**Performance budget (NFR-4)**: Init-duration regression cap on canonical fixture vs current `replace_in_files()`. Stream 1 Day 1 benchmark mandatory; recorded in ADR-038 §Consequences. Escalation thresholds: ≤5% holds; 5–50% loosens to 25% with rationale; >50% PM re-scope.

**BLP-02 Wave fit**:
- **F-1 (this feature)** — Wave 1, P0; closes 5 of 11 /security vulns; ships first
- **F-2 (Wave 2)** — Source-Pattern Hardening; depends on F-1 finalizing canonical placeholder set + locking the validation triplet pattern (regex-validate → reject-on-mismatch → `printf -v` assignment) in ADR-038
- **F-3 (Wave 3)** — SECURITY.md disclosure channel
- **F-4 (Wave 4)** — Claude permissions
- **F-5 (Wave 4)** — Secret-scanning

ADR cadence: ADR-038 (F-1), ADR-039 (F-2), ADR-040 (F-4), ADR-041 (F-5). F-3 has no ADR (process change).

**Cross-cutting Constitution principles**:
- III. Backward Compatibility (NON-NEGOTIABLE)
- VI. Testing Excellence (7-test Regression Protection Plan; ≥13 adversarial inputs)
- VII. Definition of Done (NON-NEGOTIABLE; 14-item DoD)
- IX. Git Workflow (`feat(248):` prefix; release-please belt-and-suspenders verification per F-212 incident)
- X. Product-Spec Alignment + Architecture Review (NON-NEGOTIABLE)

## Industry Research

**OWASP consensus**: Treating shell-string-tool substitution on tainted input as command-injection territory is the OWASP default. CWE-77 (Command Injection); A03:2021 Injection. *"Never attempt to sanitize input by escaping shell metacharacters"* (OWASP Injection Prevention Cheat Sheet) — escape-based sanitization is brittle (escape-of-escape bypasses, locale issues, multi-pass interpretation).

**Bash parameter expansion semantics** (GNU Bash manual §Shell-Parameter-Expansion):
- `${parameter//pattern/string}` — pattern is glob, replacement is **literal**
- Replacement supports `;`, `|`, `` ` ``, `$`, `(`, `)`, embedded newlines verbatim — no re-parsing
- Edge case: `\&` is consumed (yields literal `&`); plain `&` is also literal in replacement
- Edge case: under `set -u`, unset parameter errors out — guard with `${parameter-}` defaulting

**Validation patterns**:
- POSIX character classes (`[[:alnum:]]`, `[[:digit:]]`) preferred over `[A-Z]` for locale safety
- Bounded length: `^[[:alnum:]_-]{1,64}$` style
- Trim leading whitespace before validation
- **Reject, don't sanitize**: refuse invalid input with a clear error
- `read -r` to disable backslash continuation; `read -s` for secrets

**Test patterns**:
- Fixture table of malicious inputs (`&`, `\1`, `;`, `|`, `` ` ``, `$(...)`, embedded newline, embedded NUL, `../`, leading `-`, oversized)
- Assert literal payload survives unchanged in output
- Pytest + subprocess preferred when surrounding repo is Python-heavy (the F-1 case)
- ShellCheck as static gate

**Performance**: Bash parameter expansion is **~50–500x faster than sed** for in-memory substitution due to fork+exec elimination. Performance argument *reinforces* the security choice — no trade-off.

**Sources**:
- [OWASP OS Command Injection Defense Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/OS_Command_Injection_Defense_Cheat_Sheet.html)
- [OWASP Injection Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Injection_Prevention_Cheat_Sheet.html)
- [OWASP Input Validation Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Input_Validation_Cheat_Sheet.html)
- [GNU Bash Manual — Shell Parameter Expansion](https://www.gnu.org/software/bash/manual/html_node/Shell-Parameter-Expansion.html)
- [CWE-77: Command Injection](https://cwe.mitre.org/data/definitions/77.html)

## Recommendations for Spec

1. **ADR-038 is a deliverable, not a citation** — call it out at `docs/architecture/02_ADRs/ADR-038-placeholder-substitution-strategy.md` with "to be authored, dual-commit Proposed → Accepted".
2. **Cross-reference ADR-009** as the prior decision being superseded on mechanism (placeholder enumeration remains valid).
3. **Apply Feature 132 `set +e`/`set -e` bracket discipline** to `aod_init_read_validated` to avoid bash 3.2 errexit foot-gun.
4. **Lock validation triplet pattern (regex → reject → `printf -v`)** in ADR-038 — F-2 reuses the *pattern*, not the function.
5. **Existing safe function is the substitution layer** — F-1 wires init.sh to it; no new substitution code.
6. **Preserve self-delete (`rm -f scripts/init.sh` at line 354)** as the re-init prevention mechanism; add pre-flight check at top of init.sh that FATAL-exits if `.aod/personalization.env` already exists.
7. **Use POSIX character classes** in validators for locale safety.
8. **Test corpus ≥13 adversarial inputs** covering metacharacter classes (`&`, `;`, `|`, newline, NUL, `$(...)`, etc.).
9. **Pre-stripped constitution template at `.aod/templates/constitution-clean.md`** (NOT repo root) — replaces sed cleanup pass.
10. **Remove `.claude/mcp-config.json`** (Q-1 Option b); no PROJECT_PATH placeholder added.
