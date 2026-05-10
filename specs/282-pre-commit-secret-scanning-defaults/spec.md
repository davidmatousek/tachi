---
prd_reference: docs/product/02_PRD/282-pre-commit-secret-scanning-defaults-2026-05-09.md
triad:
  pm_signoff:
    agent: product-manager
    date: 2026-05-10
    status: APPROVED_WITH_CONCERNS
    notes: "All 17 mandatory PRD ACs (AC-1 through AC-17) plus AC-SPEC-1 functionally covered by 15 FRs; 4/4 PRD user stories covered with 2 well-justified P2 expansions (US-5 SecOps reviewer, US-6 CI back-stop); 9/9 SCs measurable or [QUALITATIVE-ONLY]-justified; 10/10 PRD §Non-Goals carried over verbatim; Q1-Q10 resolutions match user-provided answers and PRD positions. Pre-Mortem lens applied (5 failure modes evaluated). 5 minor concerns logged: PM-1 (AC-3+AC-5 trace labels missing on FR-002/FR-008 — RESOLVED inline before frontmatter inject), PM-2 (SC-007 qualitative-disclaimer — RESOLVED inline), PM-4 (pin-bump cadence assumption — RESOLVED inline), PM-5 (wrapper script LOCAL-ONLY clarification per Pre-Mortem FM-2 — RESOLVED inline by amending FR-007 + FR-008 acceptance to make wrapper-vs-CI invocation explicit). PM-3 (FR-009 redundancy with FR-008) deferred to /aod.project-plan for design-time consolidation. Full review: .aod/results/product-manager-spec-282.md."
  architect_signoff: null  # Added by /aod.project-plan
  techlead_signoff: null   # Added by /aod.tasks
---

# Feature Specification: Pre-commit Secret-Scanning Defaults (F-5)

**Feature Branch**: `282-pre-commit-secret-scanning-defaults`
**Issue**: [#282](https://github.com/davidmatousek/tachi/issues/282)
**PRD**: [docs/product/02_PRD/282-pre-commit-secret-scanning-defaults-2026-05-09.md](../../docs/product/02_PRD/282-pre-commit-secret-scanning-defaults-2026-05-09.md)
**Created**: 2026-05-10
**Status**: Draft
**Initiative**: BLP-02 Wave 4+ — fifth and final feature in the 5-feature enterprise hardening initiative
**Input**: User description: "PRD: 282 - pre-commit-secret-scanning-defaults; resolve Q1-Q2 (warn-only), Q4 (TTY check baseline + --no-precommit override), Q5 (full-repo scan on PRs), Q6 (wrapper-script approach), Q7 (under Security subsection), Q9 (separate file at .aod/scripts/bash/precommit-wrap.sh), Q10 (raw read -p with ADR-042 waiver); also include AC-SPEC-1 synthetic-fixture rule-interaction test fixtures as entry-criteria."

---

## Overview

Ship a pre-commit hook configuration (`.pre-commit-config.yaml`) running `gitleaks` against staged commit content as a default-deny gate against accidental credential exposure. Opt-in for new adopters via an `init.sh` prompt (default Y in TTY contexts; auto-skipped in non-interactive contexts) and opt-in (no auto-install on `git pull`) for existing adopters. Ship a tachi-tuned `.gitleaks.toml` with allow-listing for env-var placeholders, fixture/docs/example paths, the new `.aod/personalization.env.example` template, and two additive custom rules (`tachi-personalization-env` warn-only, `tachi-security-exceptions-jsonl` warn-only). Ship `docs/standards/PRECOMMIT_HOOKS.md` documenting installation/opt-out/bypass paths, `ADR-042` capturing the gitleaks-vs-trufflehog decision and the opt-in posture, a dedicated `.github/workflows/gitleaks.yml` for CI parity (full-repo scan on PRs), a wrapper script `.aod/scripts/bash/precommit-wrap.sh` augmenting gitleaks stderr with bypass guidance + docs link, the `.aod/personalization.env.example` template, plus CHANGELOG and README pointer.

This is the third LinkedIn-thread gap closed (after F-3 disclosure and F-4 permissions). Closes BLP-02 5/5.

## Resolved Questions (from PRD)

The PRD listed 10 open questions for /aod.spec resolution. Resolutions captured here for plan/tasks downstream:

| Q | Topic | Resolution | Rationale |
|---|-------|-----------|-----------|
| Q1 | `tachi-personalization-env` rule disposition | **Warn-only** | PRD position; non-blocking; teaches without breaking first-run CI. |
| Q2 | `tachi-security-exceptions-jsonl` rule disposition | **Warn-only** | PRD position; complements F-1 detection-tier contract continuity. |
| Q3 | AC-18/AC-19 follow-up timing | **Post-merge** | Standard /aod.deliver pattern; non-blocking. |
| Q4 | Non-interactive opt-out mechanism | **TTY check baseline (`[ -t 0 ]`) + `--no-precommit` flag override; explicit `--precommit` flag for `expect`-style automation** | Architect Q4 expansion; flag-driven override gives CI/automation explicit control. |
| Q5 | CI parity scope | **Full-repo scan on PRs** | PR-diff risks missing pre-existing un-scanned credentials in older commits; full-repo scan catches them at merge time. |
| Q6 | Refused-commit error customization | **Wrapper script** | Architect C-2 + independent verification: gitleaks does NOT support stderr-message templating. |
| Q7 | README pointer placement | **Under existing "Security" subsection** | Consistent with F-3 SECURITY.md and F-4 CLAUDE_PERMISSIONS.md README pointers. |
| Q8 | Next-day delivery realism | **2026-05-10 target with 2026-05-11 slack** | Resolved at PRD review per Team-Lead A-5. |
| Q9 | Wrapper script location | **`.aod/scripts/bash/precommit-wrap.sh`** (separate file) | Easier to unit-test, version, and maintain than inline `entry: bash -c '...'`. |
| Q10 | init.sh prompt validator | **Raw `read -p` with ADR-042 waiver** | Single-char Y/n below F-1 free-text-injection threshold; precedent already in init.sh lines 85/110/144/146/148/177. |

## User Scenarios & Testing *(mandatory)*

### User Story 1 — First-time adopter accidentally committing a credential (Priority: P1)

A first-time adopter clones tachi for production-adjacent use, configures `.aod/personalization.env` with a real-format-but-fake API key for testing, and accidentally `git add`-s the file. The pre-commit hook fires, refuses the commit, displays the rule ID + file:line + bypass guidance + docs link, and prevents the credential from reaching the local commit history.

**Why this priority**: This is the primary defense-in-depth gate and the headline value proposition. Without it, F-5 is just documentation.

**Independent Test**: Clone fresh tachi, run `init.sh` accepting prompt default Y, stage a file containing `ghp_<random40chars>`, attempt `git commit -m "test"`, observe commit refused with structured error message containing all four contract items.

**Acceptance Scenarios**:

1. **Given** a fresh tachi clone with `init.sh` run accepting prompt default Y, **When** I stage a file containing `ghp_<random40chars>` and attempt `git commit -m "test"`, **Then** the commit is refused and the wrapper-script stderr output contains (a) the gitleaks rule ID for "GitHub Personal Access Token", (b) the file:line of the match, (c) `SKIP=gitleaks git commit ...` bypass guidance, (d) docs link `See docs/standards/PRECOMMIT_HOOKS.md`.
2. **Given** the commit was refused in scenario 1, **When** I run `SKIP=gitleaks git commit -m "test"` instead, **Then** the commit succeeds (the bypass mechanism works as documented).

---

### User Story 2 — Security-conscious team wanting default-deny without per-repo design cost (Priority: P1)

A security-conscious team adopting tachi as their project template inherits `.pre-commit-config.yaml` + `.gitleaks.toml` shipped at repo root with default rules catching the common credential patterns (AWS access keys, GitHub PATs, OpenAI/Anthropic API keys, generic high-entropy strings) without having to design rules from scratch.

**Why this priority**: P1 because this is the second-largest user surface and validates the "shipped default" value proposition.

**Independent Test**: Without modifying `.gitleaks.toml`, stage files containing each of the five canonical credential patterns; verify each one fires the appropriate rule.

**Acceptance Scenarios**:

1. **Given** the shipped `.gitleaks.toml` is unmodified, **When** I stage a file with `AKIA<16chars>` (AWS access key format) and attempt `git commit`, **Then** the commit is refused with the AWS-access-key rule ID.
2. **Given** the shipped `.gitleaks.toml` is unmodified, **When** I stage a file with `sk-ant-<random>` (Anthropic API key format) and attempt `git commit`, **Then** the commit is refused with the corresponding rule ID.
3. **Given** the shipped `.gitleaks.toml` is unmodified, **When** I stage a file with a generic high-entropy random string of sufficient length, **Then** the commit is refused with the generic-high-entropy rule ID.

---

### User Story 3 — Existing adopter not surprised by auto-installed hook (Priority: P1)

An existing adopter who already ran an older `init.sh` and now runs `make update` (or `git pull`) to apply the F-5 update does NOT have a new `.git/hooks/pre-commit` script written without their consent. The CHANGELOG and a one-line README pointer instruct how to opt in (`pre-commit install`).

**Why this priority**: P1 because surprise behavior on `git pull` is a trust-breaker for existing adopters with their own pre-commit setups (gitleaks, trufflehog, internal tooling); a single bad-surprise update could permanently sour a security-conscious adopter.

**Independent Test**: Simulate existing-adopter clone (no `.git/hooks/pre-commit`); apply F-5 update via `git pull` from feature branch; inspect `.git/hooks/pre-commit` post-pull — no file written.

**Acceptance Scenarios**:

1. **Given** an existing adopter clone with no `.git/hooks/pre-commit` script, **When** I `git pull` the F-5 update, **Then** `.git/hooks/pre-commit` remains absent and the CHANGELOG entry instructs me to run `pre-commit install` to opt in.
2. **Given** an existing adopter clone, **When** I read the README "Security" subsection, **Then** I see a one-line pointer to `docs/standards/PRECOMMIT_HOOKS.md`.

---

### User Story 4 — Adopter not frustrated by false positives on legitimate placeholder content (Priority: P1)

An adopter committing legitimate placeholder content (env-var references, the `.aod/personalization.env.example` template, fixture credentials under `tests/fixtures/`, documentation placeholders under `docs/`) does NOT have the hook fire false-positives. The default `.gitleaks.toml` allow-list recognizes tachi's conventions.

**Why this priority**: P1 because false-positive flood is the primary kill-switch for opt-in security tooling adoption (~5+ false positives → adopter uninstalls hook in frustration).

**Independent Test**: Run `pre-commit run --all-files` from a clean F-5 branch clone with the shipped `.gitleaks.toml` — observe ZERO findings on tachi's pre-F-5 baseline tree.

**Acceptance Scenarios**:

1. **Given** the shipped `.gitleaks.toml` is unmodified, **When** I stage a file containing `password = "$ENV_VAR"` and `OPENAI_API_KEY=PLACEHOLDER`, **Then** the commit succeeds without hook intervention.
2. **Given** the shipped `.gitleaks.toml` is unmodified, **When** I stage a file under `tests/fixtures/` containing a deliberately-fake AWS key, **Then** the commit succeeds (path-allow-listed).
3. **Given** the shipped `.gitleaks.toml` is unmodified, **When** I stage a file under `docs/` containing `ghp_<placeholder>`, **Then** the commit succeeds (path-allow-listed).
4. **Given** the new `.aod/personalization.env.example` template file is committed at repo root, **When** I run `pre-commit run --all-files`, **Then** no finding is reported on the template file's content.

---

### User Story 5 — SecOps reviewer auditing tachi's secret-scanning posture (Priority: P2)

A SecOps reviewer auditing tachi for procurement-questionnaire purposes reads `docs/standards/PRECOMMIT_HOOKS.md` as their first introduction to the secret-scanning posture and produces an audit summary (which scanner / which rules / which opt-out / which bypass / which CI back-stop) without follow-up questions.

**Why this priority**: P2 because the document is read after the technical implementation lands; a SecOps reviewer is the secondary persona, not the daily-developer persona.

**Independent Test**: PM walk-through of `PRECOMMIT_HOOKS.md` against a SecOps procurement-questionnaire template; confirm all expected sections present.

**Acceptance Scenarios**:

1. **Given** `docs/standards/PRECOMMIT_HOOKS.md` lands at the documented path, **When** a SecOps reviewer reads it cold, **Then** they can answer (a) which scanner ships (gitleaks), (b) which rules apply (defaults + allow-list + 2 custom rules), (c) how to opt out (`pre-commit uninstall`), (d) how to bypass per-commit (`SKIP=gitleaks`), (e) what the CI back-stop is (`.github/workflows/gitleaks.yml`).
2. **Given** the document, **When** the reviewer cross-checks `.gitleaks.toml` rule IDs against the document's per-rule rationale catalog, **Then** every rule and allow-list entry has a one-to-one rationale.

---

### User Story 6 — CI gate catches credentials that bypass local hook (Priority: P2)

A developer using `git commit --no-verify` to bypass the local pre-commit hook still has their PR fail in CI when `.github/workflows/gitleaks.yml` runs gitleaks against the PR's full-repo content.

**Why this priority**: P2 because it's the back-stop for the P1 local hook; valuable but secondary to local prevention.

**Independent Test**: Open a feature branch with a deliberately-bad credential file using `--no-verify` to bypass local hook; push; verify the GitHub Actions check fails. Delete the bad file and force-push; verify the check passes.

**Acceptance Scenarios**:

1. **Given** the new `.github/workflows/gitleaks.yml` workflow is shipped, **When** a PR is opened containing a deliberately-bad credential file (added via `--no-verify`), **Then** the gitleaks GitHub Actions check fails with a finding message that matches the rule ID and file:line a local hook would have produced.
2. **Given** the bad-credential commit is removed and the branch is force-pushed, **When** GitHub Actions re-runs, **Then** the gitleaks check passes.

---

### Edge Cases

- **`init.sh` runs in non-interactive context** (CI, `expect`, `</dev/null` pipe): TTY check `[ -t 0 ]` fails → prompt is skipped → `pre-commit install` is NOT invoked → no error / no hang. Adopter must manually `pre-commit install` post-init.
- **Adopter declines prompt (types `n`)**: prompt completes, `pre-commit install` is NOT invoked, init.sh continues. Adopter can re-invoke `pre-commit install` later.
- **`pre-commit` framework not installed on adopter system**: `pre-commit install` fails → init.sh logs a one-line `WARN: pre-commit install failed; install pre-commit framework manually and run 'pre-commit install'` and continues. init.sh does NOT abort.
- **Adopter's existing `.git/hooks/pre-commit` is non-pre-commit-framework script**: `pre-commit install` overwrites it. Documented in PRECOMMIT_HOOKS.md §Known-Limitations.
- **Adopter renames `tests/fixtures/` to `samples/`**: `.gitleaks.toml` path-allow-list does NOT match the new path → false positives fire. Documented in PRECOMMIT_HOOKS.md §Adopter-Customization with the merge-conflict resolution pattern.
- **Adopter modifies `.gitleaks.toml` and runs `make update`**: merge conflict on `.gitleaks.toml` (R-9). PRECOMMIT_HOOKS.md §Adopter-Customization documents the resolution pattern.
- **gitleaks framework upstream tag force-move**: pinned commit hash protects against this (R-3).
- **Pre-commit framework version drift below 3.5.0**: PRECOMMIT_HOOKS.md §Known-Limitations documents minimum version (R-10).
- **`git commit --no-verify` deliberate bypass**: documented as known limitation; CI parity is the back-stop (US-6).
- **gitleaks-action license issue for org repos**: F-5 sidesteps by invoking gitleaks binary directly in the workflow (per research-recommended approach), avoiding the proprietary v2.x action.

## Requirements *(mandatory)*

> **Acceptance Criteria Rule**: Each AC MUST begin with **Given** and follow Given/When/Then structure. Use `[MANUAL-ONLY] <reason>` (reason ≥10 chars) inline to mark ACs that cannot be automated.

### Functional Requirements

#### FR-001 — `.pre-commit-config.yaml` at repo root
System MUST ship `.pre-commit-config.yaml` at repo root referencing the `gitleaks/gitleaks` upstream repo with a pinned commit hash (NOT a floating tag — supply-chain hygiene). The hook invokes the wrapper script at `.aod/scripts/bash/precommit-wrap.sh` (per Q9 + Architect C-2) which delegates to gitleaks with `--config=.gitleaks.toml`.

**Acceptance**:
- **Given** the F-5 branch is checked out, **When** I read `.pre-commit-config.yaml`, **Then** it references `gitleaks/gitleaks` with `rev:` set to a pinned commit SHA (40-character hex string), and the hook entry invokes `.aod/scripts/bash/precommit-wrap.sh`.
- **Given** `.pre-commit-config.yaml` is shipped, **When** an adopter has not run `pre-commit install`, **Then** the hook is NOT installed in `.git/hooks/` (file-presence does NOT auto-install).

Traces to: PRD AC-1, US-1, US-2.

#### FR-002 — `.gitleaks.toml` at repo root
System MUST ship `.gitleaks.toml` at repo root extending gitleaks default rules with: (a) tachi-specific allow-list (env-var placeholders, fixture/docs/examples paths, `.aod/personalization.env.example` path), (b) two additive custom rules (`tachi-personalization-env` warn-only, `tachi-security-exceptions-jsonl` warn-only), (c) excluded paths (`node_modules/`, `.git/`, `archive/`). Schema uses `[[allowlists]]` (TOML array of tables) per gitleaks v8.25.0+.

**Acceptance**:
- **Given** the F-5 branch is checked out, **When** I read `.gitleaks.toml`, **Then** the file has `[extend] useDefault = true`, at least one `[[allowlists]]` entry covering env-var placeholders + fixture/docs paths + `.aod/personalization.env.example`, and exactly two `[[rules]]` entries with IDs `tachi-personalization-env` and `tachi-security-exceptions-jsonl`.
- **Given** `.gitleaks.toml` is shipped, **When** I run `gitleaks detect --config=.gitleaks.toml --no-git --source=.` (or current-CLI-shape equivalent) against tachi's pre-F-5 baseline tree, **Then** zero findings are produced.
- **Given** `.gitleaks.toml` is shipped, **When** I stage a file containing `password = "$ENV_VAR"` and `OPENAI_API_KEY=PLACEHOLDER` and attempt `git commit`, **Then** the commit succeeds (no rule fires on legitimate placeholder content per AC-5).

Traces to: PRD AC-2, AC-4, AC-5, US-2, US-4.

#### FR-003 — `.aod/personalization.env.example` template file
System MUST ship `.aod/personalization.env.example` at the documented path containing placeholder values for the keys `init.sh` expects (project name, stack pack, brand name, plus all keys documented in `init.sh`). The file is path-allow-listed in `.gitleaks.toml`. The populated `.aod/personalization.env` remains gitignored per F-1 #248.

**Acceptance**:
- **Given** the F-5 branch is checked out, **When** I read `.aod/personalization.env.example`, **Then** the file contains a header comment instructing users to copy the file to `.aod/personalization.env`, all keys documented in `scripts/init.sh`, and placeholder values (NO real credentials).
- **Given** `.aod/personalization.env.example` is shipped, **When** I run `pre-commit run --all-files`, **Then** no finding is reported on the template file's content.

Traces to: PRD AC-8, PRD §Proposed-Solution item 3, C-1 resolution.

#### FR-004 — `init.sh` opt-in prompt with TTY check
System MUST add a single prompt step to `scripts/init.sh` that (a) checks TTY via `[ -t 0 ]`, (b) prompts `Install pre-commit secret-scanning hook (gitleaks)? [Y/n]` with default Y when TTY is present, (c) invokes `pre-commit install` on Y, (d) skips silently in non-interactive contexts, (e) honors a `--no-precommit` command-line flag to force-skip the prompt even in TTY contexts, (f) honors a `--precommit` flag for `expect`-style automation that needs explicit accept-without-prompt. Uses raw `read -p` (Q10 resolution: waiver in ADR-042 §Consequences).

**Acceptance**:
- **Given** a fresh tachi clone in a TTY, **When** I run `scripts/init.sh` and accept the prompt default Y, **Then** the script invokes `pre-commit install` and `.git/hooks/pre-commit` is written.
- **Given** a fresh tachi clone, **When** I run `scripts/init.sh </dev/null` (non-interactive), **Then** the prompt is skipped and no error / no hang occurs.
- **Given** a fresh tachi clone in a TTY, **When** I run `scripts/init.sh --no-precommit`, **Then** the prompt is skipped even though TTY is present.
- **Given** a fresh tachi clone, **When** I run `scripts/init.sh --precommit </dev/null` (non-interactive but explicit accept), **Then** `pre-commit install` is invoked without a prompt.
- **Given** the prompt fires and `pre-commit` is not installed on the system, **When** `pre-commit install` fails, **Then** init.sh logs `WARN: pre-commit install failed; install pre-commit framework manually and run 'pre-commit install'` and continues (does NOT abort).

Traces to: PRD AC-6, AC-7, US-1, US-3, Q4 / Q10.

#### FR-005 — `docs/standards/PRECOMMIT_HOOKS.md`
System MUST ship `docs/standards/PRECOMMIT_HOOKS.md` (~150-250 LOC) self-contained operator handbook with sections: Why this hook ships / Installation paths (3) / What gets scanned / Bypass mechanisms / Refused-commit error message contract / CI parity / Re-init behavior / Known limitations / Adopter customization. Every rule and allow-list entry in `.gitleaks.toml` MUST have a one-to-one rationale entry in this document.

**Acceptance**:
- **Given** the F-5 branch is checked out, **When** I read `docs/standards/PRECOMMIT_HOOKS.md`, **Then** all 9 expected sections are present.
- **Given** the document, **When** I cross-check each rule ID and allow-list entry in `.gitleaks.toml` against the document's per-rule rationale catalog, **Then** each one has a one-to-one rationale entry. [MANUAL-ONLY] requires reviewer judgment to assess rationale clarity.

Traces to: PRD AC-10, US-5.

#### FR-006 — ADR-042 architecture decision record
System MUST ship `docs/architecture/02_ADRs/ADR-042-pre-commit-secret-scanning-default.md` (~130-180 LOC) with Status `Accepted` after Architect sign-off. Sections: Context / Decision (gitleaks-vs-trufflehog rationale, opt-in posture, pin-bump cadence per A-2, raw `read -p` waiver per C-3, wrapper-script per C-2) / Alternatives (9: trufflehog, detect-secrets, GitHub native push-protection, custom regex hook, opt-out flag, tier the hooks, GitGuardian, SecretLint, git-secrets) / Consequences / References. **Note**: ADR-042 must correct the PRD comparison-matrix error — trufflehog runtime is **Go** not Python.

**Acceptance**:
- **Given** the F-5 branch is checked out, **When** I read `docs/architecture/02_ADRs/ADR-042-pre-commit-secret-scanning-default.md`, **Then** the status is `Accepted`, sections Context / Decision / Alternatives / Consequences / References are all present, 9 alternatives are enumerated each with rejection rationale, and the trufflehog comparison entry says runtime is **Go** (not Python).
- **Given** ADR-042, **When** I read §Consequences, **Then** the pin-bump cadence policy and the raw `read -p` waiver are both documented.

Traces to: PRD AC-11, PRD §Proposed-Solution item 6.

#### FR-007 — `.github/workflows/gitleaks.yml` CI parity workflow
System MUST ship `.github/workflows/gitleaks.yml` (~25-40 LOC) — a dedicated single-purpose workflow running gitleaks against the **full repo** on every PR (per Q5 resolution). The workflow uses the same `.gitleaks.toml` config as the local hook. Implementation invokes the gitleaks **binary directly** (downloads release tarball, verifies checksum, runs `gitleaks git`) rather than the proprietary `gitleaks/gitleaks-action@v2` (which requires a paid `GITLEAKS_LICENSE` for org repos).

**Acceptance**:
- **Given** the F-5 branch is checked out, **When** I read `.github/workflows/gitleaks.yml`, **Then** the workflow downloads gitleaks binary directly (with checksum verification), invokes `gitleaks git` against the full repo, references `.gitleaks.toml` as the config, and triggers on `pull_request` events.
- **Given** the workflow is shipped, **When** a PR is opened with a deliberately-bad credential file, **Then** the GitHub Actions check fails with a gitleaks finding message (rule ID + file:line) matching what the local hook would produce.
- **Given** the bad-credential commit is removed and the branch is force-pushed, **When** GitHub Actions re-runs, **Then** the gitleaks check passes.
- **Given** the workflow is shipped, **When** I read `.github/workflows/gitleaks.yml`, **Then** it invokes the gitleaks binary directly **WITHOUT** the wrapper script — preserving native gitleaks output (text/JSON/SARIF) for downstream tooling (GitHub Code Scanning SARIF upload, GitHub Actions log fidelity). Wrapper script is **LOCAL-ONLY** per FR-008.

Traces to: PRD AC-12, US-6, Q5.

#### FR-008 — `.aod/scripts/bash/precommit-wrap.sh` wrapper script
System MUST ship `.aod/scripts/bash/precommit-wrap.sh` (~30-60 LOC) following established `.aod/scripts/bash/` conventions (`#!/usr/bin/env bash` shebang, stderr via `>&2`, exit codes 0/1/8). The wrapper invokes gitleaks with the staged-content scope (current CLI shape: `gitleaks git --staged` or equivalent), captures gitleaks output, and on non-zero exit emits a structured stderr message containing (a) the gitleaks rule ID, (b) the file:line of the match, (c) `SKIP=gitleaks git commit ...` bypass guidance, (d) `See docs/standards/PRECOMMIT_HOOKS.md` docs link. Preserves gitleaks' exit code.

**Acceptance**:
- **Given** the F-5 branch is checked out, **When** I read `.aod/scripts/bash/precommit-wrap.sh`, **Then** the script has the standard shebang, invokes gitleaks with the documented config, and emits the four-item structured stderr message on non-zero exit.
- **Given** the wrapper is shipped and called by the pre-commit hook, **When** I stage a file containing `ghp_<random40chars>` and attempt `git commit`, **Then** the captured stderr contains all four contract items (rule ID, file:line, bypass guidance, docs link).
- **Given** the wrapper is shipped, **When** gitleaks exits 0 (no findings), **Then** the wrapper exits 0 with no stderr augmentation.
- **Given** the wrapper is shipped, **When** I trace its invocation surface, **Then** the wrapper is invoked **ONLY by the local pre-commit hook** (FR-001) — CI parity (FR-007) invokes gitleaks binary directly to preserve native output for SARIF/GitHub-Code-Scanning compatibility.

Traces to: PRD AC-3, AC-15, US-1, Q6 / Q9.

#### FR-009 — Refused-commit error message contract
System MUST emit a refused-commit error message containing all four contract items (rule ID, file:line, `SKIP=gitleaks` bypass, docs link) when gitleaks blocks a commit. The wrapper script (FR-008) is the mechanism; gitleaks default output covers items (a) and (b), the wrapper augments with (c) and (d).

**Acceptance**: Same as FR-008 acceptance scenarios 2.

Traces to: PRD AC-15, US-1.

#### FR-010 — Existing-adopter no-surprise flow
System MUST NOT auto-install the pre-commit hook on `git pull` for existing adopters. The CHANGELOG entry and a one-line README pointer instruct existing adopters how to opt in (`pre-commit install`).

**Acceptance**:
- **Given** an existing adopter clone with no `.git/hooks/pre-commit`, **When** I `git pull` the F-5 update from the merged feature branch, **Then** `.git/hooks/pre-commit` remains absent (no auto-install).
- **Given** the F-5 update is pulled, **When** I read CHANGELOG.md, **Then** the entry contains the instruction `to enable, run pre-commit install from the repo root after git pull`.
- **Given** the F-5 update is pulled, **When** I read README.md "Security" subsection, **Then** I see a one-line pointer to `docs/standards/PRECOMMIT_HOOKS.md`.

Traces to: PRD AC-9, AC-13, AC-14, US-3, Q7.

#### FR-011 — CHANGELOG entry under Unreleased → Added
System MUST add a CHANGELOG entry under `Unreleased → Added` referencing all new/modified files (`.pre-commit-config.yaml`, `.gitleaks.toml`, `.aod/personalization.env.example`, `docs/standards/PRECOMMIT_HOOKS.md`, ADR-042, `.github/workflows/gitleaks.yml`, `.aod/scripts/bash/precommit-wrap.sh`, `scripts/init.sh` delta, README.md delta) and the existing-adopter opt-in path. **Placement**: sibling-h3 under Unreleased (`### Pre-commit secret-scanning defaults (BLP-02 F-5)`), NOT under `### Features` — N-4 carry-forward through F-2/F-3/F-4.

**Acceptance**:
- **Given** the F-5 branch is checked out, **When** I read CHANGELOG.md, **Then** the entry is present at sibling-h3 level under `## [Unreleased]` with all required file references and the existing-adopter opt-in instruction.

Traces to: PRD AC-13, KB Entry 4 §Pattern 3.

#### FR-012 — README.md "Security" subsection pointer
System MUST add a one-line pointer to `docs/standards/PRECOMMIT_HOOKS.md` in README.md's existing "Security" subsection (or equivalent). Format consistent with F-3 and F-4 README pointers.

**Acceptance**:
- **Given** the F-5 branch is checked out, **When** I read README.md, **Then** the "Security" subsection (or equivalent existing security/scanning section) contains a one-line pointer to `docs/standards/PRECOMMIT_HOOKS.md`.

Traces to: PRD AC-14, Q7.

#### FR-013 — AC-SPEC-1 synthetic-fixture rule-interaction test
System MUST ship a synthetic-fixture rule-interaction test under `tests/fixtures/gitleaks-rule-interaction/` containing synthetic versions of every adopter scenario currently on file, plus 10-20 expected adopter cases. The test runs `gitleaks --config=.gitleaks.toml` against each fixture and verifies the **expected** rule fires per case (or no rule fires for legitimate placeholder content). This is preventive false-positive verification per Architect C-4 resolution.

**Test surface (16 synthetic cases minimum)**:

Should-fire fixtures (rule-fires-and-blocks):
1. `staged-credential/github-pat.txt` — contains `ghp_<random40chars>` → fires `github-pat` rule
2. `staged-credential/aws-access-key.txt` — contains `AKIA<16chars>` → fires `aws-access-token` rule
3. `staged-credential/openai-key.txt` — contains `sk-<random48chars>` (real-format) → fires `openai-api-key` rule (or generic-api-key)
4. `staged-credential/anthropic-key.txt` — contains `sk-ant-<random>` → fires `anthropic-api-key` or generic
5. `staged-credential/private-key-block.pem` — contains `-----BEGIN RSA PRIVATE KEY-----...` → fires `private-key` rule
6. `staged-credential/personalization-env-populated.env` — non-placeholder values → fires `tachi-personalization-env` warn-only

Should-NOT-fire fixtures (allow-listed):
7. `placeholder/env-var-reference.txt` — `password = "$ENV_VAR"` → no rule fires (env-var-placeholder allow-list)
8. `placeholder/openai-placeholder.env` — `OPENAI_API_KEY=PLACEHOLDER` → no rule fires
9. `placeholder/sk-placeholder.env` — `OPENAI_API_KEY=sk-PLACEHOLDER...` → no rule fires
10. `placeholder/sk-test-stripe.env` — `STRIPE_KEY=sk-test-...` → no rule fires (Stripe test-mode)
11. `path-allow-listed/personalization-env-example` — copy of `.aod/personalization.env.example` → no rule fires (path allow-list)
12. `path-allow-listed/tests-fixtures-fake-aws.txt` — fake AWS key UNDER `tests/fixtures/...` path → no rule fires
13. `path-allow-listed/docs-placeholder.md` — `ghp_<placeholder>` UNDER `docs/...` path → no rule fires
14. `path-allow-listed/security-exceptions-jsonl-auto.jsonl` — auto-generated `.security/exceptions.jsonl` entry → no rule fires (or fires `tachi-security-exceptions-jsonl` warn-only on manual edit, not auto-gen)
15. `path-excluded/node-modules-credential.txt` — fake credential under `node_modules/` → no rule fires (excluded path)
16. `path-excluded/archive-credential.txt` — fake credential under `archive/` → no rule fires (excluded path)

**Acceptance**:
- **Given** the synthetic-fixture directory and a test runner, **When** I run `gitleaks detect --config=.gitleaks.toml` (or current-CLI equivalent) against each fixture, **Then** each should-fire fixture produces the expected rule ID and each should-NOT-fire fixture produces zero findings.
- **Given** the test exists pre-merge, **When** the F-5 PR is reviewed, **Then** the test passes in CI before merge.

Traces to: PRD AC-SPEC-1, R-1 strengthened mitigation, C-4 preventive resolution.

#### FR-014 — Post-merge `/security` re-scan
System MUST produce zero NEW findings on the file surfaces F-5 touches when `/security` is re-run post-merge.

**Acceptance**:
- **Given** F-5 has been squash-merged to main, **When** `/security` is run on main, **Then** zero new findings are emitted on the F-5 file surface (`scripts/init.sh`, `.pre-commit-config.yaml`, `.gitleaks.toml`, `.aod/personalization.env.example`, `docs/standards/PRECOMMIT_HOOKS.md`, ADR-042, `.github/workflows/gitleaks.yml`, `.aod/scripts/bash/precommit-wrap.sh`).

Traces to: PRD AC-16, Issue #282 §Definition-of-Done.

#### FR-015 — Release-please verification
System MUST verify that the squash-merge of PR #<F-5> with commit subject `feat(282): pre-commit secret-scanning defaults` triggers a release-please PR within ~30s (per `.claude/rules/git-workflow.md` §Conventional-Commit-PR-Titles).

**Acceptance**:
- **Given** F-5 has been squash-merged with `feat(282):` commit subject, **When** I check `gh pr list --state open --search "release-please"` within 30 seconds, **Then** a release-please PR is open. If not, push an empty `feat(282): … — release marker` commit per the documented recovery flow.

Traces to: PRD AC-17, F-4 release-please precedent (~23s SLO).

### Key Entities

- **Pre-commit hook configuration** (`.pre-commit-config.yaml`): Pinned commit-SHA reference to gitleaks repo + hook entry invoking `precommit-wrap.sh`.
- **Gitleaks ruleset** (`.gitleaks.toml`): Schema v8.25.0+ `[[allowlists]]` array of tables; extends defaults; tachi-specific allow-list + 2 custom rules (warn-only).
- **Personalization template** (`.aod/personalization.env.example`): Tracked template documenting expected keys; path-allow-listed in gitleaks config.
- **Init prompt** (`scripts/init.sh` delta): TTY-gated opt-in prompt + `--no-precommit`/`--precommit` flag overrides.
- **Operator handbook** (`docs/standards/PRECOMMIT_HOOKS.md`): Self-contained ~150-250 LOC; per-rule rationale catalog.
- **ADR-042**: Architecture decision record; 9 alternatives; pin-bump cadence; raw-`read -p` waiver.
- **CI parity workflow** (`.github/workflows/gitleaks.yml`): Direct gitleaks-binary invocation (avoids proprietary action license); full-repo scan on PR.
- **Wrapper script** (`.aod/scripts/bash/precommit-wrap.sh`): Augments gitleaks stderr with bypass guidance + docs link.
- **Synthetic-fixture test** (`tests/fixtures/gitleaks-rule-interaction/`): 16+ cases verifying rule-interaction; AC-SPEC-1 entry-criteria.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001 (False-positive rate on tachi's pre-F-5 baseline)**: ZERO findings when `gitleaks detect --config=.gitleaks.toml` runs against tachi's pre-F-5 baseline tree (verified by FR-002 + FR-013 synthetic-fixture test). This is the kill-criterion: any false positive on the shipped baseline disqualifies the rule set.
- **SC-002 (Refused-commit error message contract completeness)**: 100% of refused commits include all four contract items (rule ID + file:line + `SKIP=gitleaks` bypass guidance + docs link). Verified empirically by FR-008 acceptance scenarios.
- **SC-003 (Existing-adopter no-surprise rate)**: 100% of `git pull` simulations produce zero `.git/hooks/pre-commit` writes (verified by FR-010).
- **SC-004 (CI parity local↔CI rule-ID match)**: 100% of credential-detection events that would fire locally also fire in CI with the **same rule ID** and **same file:line** (verified by FR-007 acceptance scenarios + FR-013).
- **SC-005 (Documentation parity)**: 100% of rule IDs and allow-list entries in `.gitleaks.toml` have a one-to-one rationale entry in `docs/standards/PRECOMMIT_HOOKS.md` (verified by FR-005 [MANUAL-ONLY] cross-check).
- **SC-006 (Release-please trigger SLO)**: Squash-merge with `feat(282):` subject opens a release-please PR within 30 seconds (verified by FR-015; F-4 precedent ~23s).
- **SC-007 (Adopter init.sh adoption rate)** `[QUALITATIVE-ONLY] [NON-GATING-SC]`: >70% of first-time adopters running `init.sh` interactively accept the prompt (target; measured qualitatively via community feedback per PRD §M1; tachi has no telemetry by design — this is a leading-indicator target, NOT a delivery gate).
- **SC-008 (BLP-02 closure)**: BLP-02 5/5 delivered post-F-5 merge (baseline 4/5).
- **SC-009 (LinkedIn-thread punch-list closure)**: 3/3 LinkedIn-thread gaps closed (disclosure F-3 / permissions F-4 / secret-scanning F-5).

## Assumptions

- gitleaks v8.30.1 (current latest) is the pin target; `pre-commit autoupdate --freeze` converts the tag → commit SHA.
- Pre-commit framework version >= 3.5.0 is supported; minimum documented in PRECOMMIT_HOOKS.md §Known-Limitations.
- Tachi is org-owned (`davidmatousek/tachi`) — F-5 invokes gitleaks binary directly to avoid proprietary `gitleaks-action@v2` license.
- F-1 (#248) `.aod/personalization.env` gitignore is in place on main (verified at .gitignore:226).
- The PRD comparison-matrix correction (trufflehog runtime is Go, not Python) is reflected in ADR-042 — does NOT require a PRD revision (PRD remains as-approved; ADR-042 corrects the technical detail downstream).
- Adopters with proprietary credential formats add custom rules to `.gitleaks.toml`; merge conflicts on `make update` are documented (R-9).
- `gh` CLI is available in the dev environment (used for release-please verification at /aod.deliver; degrades gracefully if absent).
- Pin-bump cadence (per ADR-042 §Consequences) requires synthetic-fixture re-test (FR-013) before merging the bump — guards against future schema breaks (e.g., the `[allowlist]` → `[[allowlists]]` change at gitleaks v8.25.0). Owner accountability lives in BLP-02 closure memo as a recurring maintenance commitment.

## Dependencies

- F-1 (#248) DELIVERED 2026-05-04 — `.aod/personalization.env` gitignore baseline (FR-003 builds on this).
- gitleaks repo at `https://github.com/gitleaks/gitleaks` (external; pinned commit-SHA mitigates upstream tag force-move per R-3).
- Pre-commit framework at `https://pre-commit.com/` (external; minimum version 3.5.0 documented in R-10).
- GitHub Actions runtime (for FR-007 CI parity).

## Out of Scope (Explicit)

- Runtime credential vault / rotation / encryption (NG1).
- `finding.yaml` / taxonomy schema changes (NG2; 12th feature in a row preserving detection-tier contract continuity).
- Tachi agent / command / skill behavior changes other than init.sh delta and the new GitHub Actions workflow (NG3).
- Protection against `git commit --no-verify` deliberate bypass (NG4; documented limitation; CI parity is back-stop).
- Verified-credential probing (NG5; pattern-match-only).
- Multi-language secret detection beyond gitleaks defaults + tachi custom rules (NG6).
- `.secrets.baseline`-style pre-existing-findings snapshot (NG7).
- Bug-bounty incentive for finding allow-list gaps (NG8).
- Per-skill / per-agent secret-scanning scoping (NG9).
- Replacement for managed-environment policies that disable `--no-verify` or enforce signed commits (NG10).

## References

### Product Documentation
- PRD: [docs/product/02_PRD/282-pre-commit-secret-scanning-defaults-2026-05-09.md](../../docs/product/02_PRD/282-pre-commit-secret-scanning-defaults-2026-05-09.md)
- Issue: [#282](https://github.com/davidmatousek/tachi/issues/282)
- Initiative: BLP-02 enterprise hardening (5/5 with F-5 closure)

### Research Grounding
- Research summary: [research.md](research.md)

### Precedents
- F-3 spec: [specs/272-security-md-disclosure/spec.md](../272-security-md-disclosure/spec.md)
- F-4 spec: [specs/277-claude-permissions-baseline/spec.md](../277-claude-permissions-baseline/spec.md)
- ADR-038 (F-1): [docs/architecture/02_ADRs/ADR-038-placeholder-substitution-strategy.md](../../docs/architecture/02_ADRs/ADR-038-placeholder-substitution-strategy.md)
- ADR-040 (F-2): [docs/architecture/02_ADRs/ADR-040-config-file-parsing-hardening.md](../../docs/architecture/02_ADRs/ADR-040-config-file-parsing-hardening.md)
- ADR-041 (F-4): [docs/architecture/02_ADRs/ADR-041-claude-permissions-baseline.md](../../docs/architecture/02_ADRs/ADR-041-claude-permissions-baseline.md)
- F-1 helper: [.aod/scripts/bash/init-input.sh](../../.aod/scripts/bash/init-input.sh)
- KB lessons: [docs/INSTITUTIONAL_KNOWLEDGE.md](../../docs/INSTITUTIONAL_KNOWLEDGE.md) Entries 1-5

### External
- Gitleaks: https://github.com/gitleaks/gitleaks (latest v8.30.1, 2026-03-21)
- Pre-commit framework: https://pre-commit.com/ (latest v4.6.0, 2026-04-21)
- Gitleaks Action: https://github.com/gitleaks/gitleaks-action (proprietary v2.x — avoided)
