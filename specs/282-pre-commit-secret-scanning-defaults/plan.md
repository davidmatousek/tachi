---
triad:
  pm_signoff:
    agent: product-manager
    date: 2026-05-10
    status: APPROVED_WITH_CONCERNS
    notes: "Plan correctly translates the spec into a build-time-ordered 5-wave sequence with full 15-FR traceability, correct PM-3 resolution (FR-008+FR-009 consolidation in §FR-Consolidation), accurate carry-forward of PM-4 (pin-bump cadence in §Tech-Stack + §Risk-Register R-3 + §Pre-Mortem FM-4) + PM-5 (wrapper LOCAL-ONLY / CI native invocation in 5 places: §Summary, Components item 7, Data Flow §CI-parity-flow, Components item 8, §Pre-Mortem FM-2). Pre-Mortem FM-3 follow-through (init.sh prompt-flag matrix 6 cases) surfaced as tasks.md candidate per user input. No scope creep — every Component/Data Flow/Tech Stack item maps to PRD §Proposed-Solution / FR / §Risk-Register. 3 minor 6-month-horizon concerns logged as tasks.md calibration notes (non-blocking): PM-PLAN-1 fixture rule-ID assertion comments to handle pin-bump cadence rule renames; PM-PLAN-2 PRECOMMIT_HOOKS.md §Re-init-Behavior should clarify --no-precommit/--precommit flags are first-run-only; PM-PLAN-3 fixture #14 header comment noting schema-out-of-scope (F-260b follow-on planned). All AC-12/AC-15/AC-17 delivery-gate ACs surface in Wave 5 with FR traceability. Full review: .aod/results/product-manager-plan-282.md."
  architect_signoff:
    agent: architect
    date: 2026-05-10
    status: APPROVED_WITH_CONCERNS
    notes: "Plan technical fidelity to PRD v1.1 CHANGES (C-1 personalization.env.example, C-2 wrapper-script, C-3 raw read-p waiver, C-4 synthetic-fixture preventive test) all carried through correctly. Pin strategy (tag → `pre-commit autoupdate --freeze` → SHA) correctly addresses PRD §R-3 supply-chain hygiene. `[[allowlists]]` schema (v8.25.0+) targets v8.30.1 correctly. Native gitleaks-binary CI invocation correctly avoids `gitleaks-action@v2` paid license for org repos. LOCAL-ONLY wrapper / native CI invocation preserves SARIF compatibility per PM-5. trufflehog runtime correction (Go not Python) reflected in §Phase-0 Research-Summary table. Wave 1→5 dependencies sound. Constitution Principles III/V/VI/VII/VIII/IX/X/XI all PASS. 4 NON-BLOCKING concerns: CONCERN-1 (HIGH) test-runner location `tests/scripts/test_gitleaks_rules.sh` collides with existing pytest convention — recommend `tests/fixtures/gitleaks-rule-interaction/run.sh` co-location at /aod.tasks; CONCERN-2 (MEDIUM) init.sh prompt-flag matrix test should be pytest not bash to leverage existing `init_sh_helpers.py` + `tachi-pytest.yml` integration; CONCERN-3 (MEDIUM) R-10 mitigation depth — add `pre-commit --version` check in init.sh + justify v3.5.0 floor in PRECOMMIT_HOOKS.md §Known-Limitations; CONCERN-4 (LOW) pin-bump cadence accountability — surface as tasks.md candidate or post-merge tracking issue. Pre-Mortem lens applied (3 architect-only FMs surfaced beyond spec's FM-1 through FM-5). Plan readiness: APPROVED. Full review: .aod/results/architect-plan-282.md."
  techlead_signoff: null  # Added by /aod.tasks
---

# Implementation Plan: Pre-commit Secret-Scanning Defaults (F-5)

**Branch**: `282-pre-commit-secret-scanning-defaults` | **Date**: 2026-05-10 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/282-pre-commit-secret-scanning-defaults/spec.md`
**PRD**: [docs/product/02_PRD/282-pre-commit-secret-scanning-defaults-2026-05-09.md](../../docs/product/02_PRD/282-pre-commit-secret-scanning-defaults-2026-05-09.md)
**Initiative**: BLP-02 Wave 4+ — fifth and final feature of the 5-feature enterprise hardening initiative

## Summary

Ship a `gitleaks`-via-`pre-commit-framework` default-deny gate against accidental credential exposure. Eight new files (`.pre-commit-config.yaml`, `.gitleaks.toml`, `.aod/personalization.env.example`, `docs/standards/PRECOMMIT_HOOKS.md`, `docs/architecture/02_ADRs/ADR-042-pre-commit-secret-scanning-default.md`, `.github/workflows/gitleaks.yml`, `.aod/scripts/bash/precommit-wrap.sh`, plus a synthetic-fixture test directory `tests/fixtures/gitleaks-rule-interaction/`) + three deltas (`scripts/init.sh` ~10-20 LOC opt-in prompt + flag handling, `CHANGELOG.md` Unreleased entry, `README.md` one-line Security pointer). The wrapper script is **LOCAL-ONLY** (invoked by the pre-commit hook); CI parity workflow invokes the gitleaks binary directly to preserve native output (text/JSON/SARIF) for GitHub Code Scanning compatibility. Primary technical approach: pinned-commit-SHA gitleaks (v8.30.1 → autoupdate-frozen SHA), TOML `[[allowlists]]`-array schema (gitleaks v8.25.0+), TTY-gated init.sh prompt with `--no-precommit`/`--precommit` flag overrides, 16+ synthetic-fixture cases for AC-SPEC-1 preventive false-positive verification.

## Technical Context

**Language/Version**: Bash 3.2+ (macOS-native compat; init.sh + wrapper script); TOML (gitleaks config); YAML (pre-commit framework + GitHub Actions); Markdown (docs + ADR).
**Primary Dependencies**:
- `pre-commit` framework v3.5.0+ (PRD R-10 floor; current upstream v4.6.0 — ample headroom)
- `gitleaks` v8.30.1 (pinned commit SHA via `pre-commit autoupdate --freeze`)
- GitHub Actions (`runs-on: ubuntu-latest`) for CI parity workflow
- F-1 #248 substitution-surface (gitignore at `.gitignore:226` is the satisfied prerequisite)

**Storage**: N/A (config + scaffold + docs only; no application state)
**Testing**:
- AC-SPEC-1 synthetic-fixture rule-interaction test (16+ cases under `tests/fixtures/gitleaks-rule-interaction/`)
- init.sh prompt-flag matrix test (Pre-Mortem FM-3 design consideration; 6 cases: `[TTY/no-TTY] × [no-flag/--no-precommit/--precommit]`)
- Existing `tachi-pytest.yml` workflow does NOT need pytest changes (gitleaks-rule-interaction test is gitleaks-driven, not pytest-driven)

**Target Platform**: macOS (primary dev environment, Bash 3.2 native compat); Linux (CI runners + adopter dev environments)
**Project Type**: Documentation + scaffold + bash script delta (no application code)
**Performance Goals**:
- Pre-commit hook: <2s scan time on tachi's tree (gitleaks Go binary, default-rule scan baseline)
- CI parity workflow: <30s end-to-end (binary download + scan)
- Release-please trigger SLO: <30s post-squash-merge (per F-4 precedent ~23s)

**Constraints**:
- No telemetry by design (gitleaks pattern-match-only; no outbound HTTP)
- No `gitleaks-action@v2` (proprietary; org-repo would require paid `GITLEAKS_LICENSE`)
- No tachi-agent / command / skill behavior changes (NG3 scope boundary)
- No `finding.yaml` schema changes (NG2 — 12th feature in a row preserving detection-tier contract continuity)

**Scale/Scope**: 8 new files + 3 deltas + ~50-80 LOC `.gitleaks.toml` + ~150-250 LOC docs + ~130-180 LOC ADR + ~25-40 LOC CI workflow + ~30-60 LOC wrapper + 16 synthetic fixtures. Total: ~440-685 LOC (per PRD §File-Surface table). Materially larger than F-3 (~100 LOC); comparable to F-4 (~430 LOC structured config + standards doc + ADR).

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Applicable Principles (and verdicts)

| Principle | Applies? | Verdict | Notes |
|-----------|----------|---------|-------|
| I. General-Purpose Architecture | NO | N/A | F-5 is template scaffolding for adopters; not a SaaS API surface. |
| II. API-First Design | NO | N/A | No API surface. |
| III. Backward Compatibility (NON-NEGOTIABLE) | YES | ✅ PASS | Existing-adopter no-auto-install (FR-010) preserves existing pre-commit setups; opt-in posture preserves backward compatibility for adopters who decline. |
| IV. Concurrency & Data Integrity | NO | N/A | No state mutations. |
| V. Privacy & Data Isolation | YES (partial) | ✅ PASS | gitleaks runs locally only; no telemetry, no outbound HTTP, no data leaving adopter's environment. PRECOMMIT_HOOKS.md §Privacy section documents this. |
| VI. Testing Excellence | YES | ✅ PASS | AC-SPEC-1 synthetic-fixture test (FR-013) covers 16+ rule-interaction cases preventively. init.sh prompt-flag matrix (Pre-Mortem FM-3) covers TTY/flag combinations. |
| VII. Definition of Done (NON-NEGOTIABLE) | YES | ✅ PASS | DoD applies fully (executable surface present: init.sh delta, gitleaks invocation, wrapper script, synthetic-fixture test). NO §Exceptions waiver invoked (unlike F-3 documentation-only). |
| VIII. Observability & RCA | YES (partial) | ✅ PASS | gitleaks structured logging is gitleaks-default (rule ID + file:line). Wrapper augmentation extends this. Five Whys methodology applies if false-positive flood post-merge (R-1 contingency). |
| IX. Git Workflow & Feature Branching (NON-NEGOTIABLE) | YES | ✅ PASS | Branch `282-pre-commit-secret-scanning-defaults` created at /aod.plan kickoff; PR title `feat(282): pre-commit secret-scanning defaults` from draft PR creation; squash-merge with conventional-commit prefix at /aod.deliver. |
| X. Product-Spec Alignment & Architecture Review (NON-NEGOTIABLE) | YES | 🟡 PASS WITH GATES | This plan IS the Architect-review artifact. PM sign-off on spec.md is in place (APPROVED_WITH_CONCERNS, frontmatter injected). Architect sign-off pending this plan's review. |
| XI. SDLC Triad Collaboration | YES | ✅ PASS | PRD followed Triad workflow (PM v1.1 APPROVED + Architect v1.1 APPROVED_WITH_CONCERNS + Team-Lead v1.0 APPROVED_WITH_CONCERNS). Spec carried forward Triad context. Plan invokes dual sign-off. |

### Constitution Compliance Notes

- **Tier**: Standard (default per constitution). All Plan-stage gates active: PM spec sign-off ✅ done; PM+Architect plan sign-off ← this artifact; Triple sign-off on tasks.md → next sub-step.
- **Backward compatibility (Principle III)**: F-5's existing-adopter no-auto-install posture is the headline backward-compat decision. CHANGELOG entry and README pointer are the documented opt-in path. AC-9/FR-010 verification ensures compliance empirically.
- **Five Whys (Principle VIII)**: If R-1 (false-positive flood) realizes post-merge, apply Five Whys to determine whether the cause is (1) gitleaks default rule too aggressive, (2) tachi allow-list incomplete, (3) adopter custom-format conflict, (4) gitleaks upstream change, or (5) wrapper-script silent regression. Currently AC-SPEC-1 + R-1 contingency hot-patch path are pre-staged.
- **Test coverage (Principle VI)**: F-5's "tests" are synthetic-fixture rule-interaction tests, not unit tests for application code. The 80% coverage target does not apply to config files; instead coverage is measured by the 16+ fixture cases mapping to allow-list entries + custom rule definitions.

### Gate Outcomes

- **Initial gate**: PASS. No constitutional violations. Proceed to Phase 0.
- **Post-design gate (re-check after Phase 1)**: ✅ PASS — see end of plan.

## Phase 0: Outline & Research

**Status**: ✅ COMPLETE. Research was conducted at /aod.spec time; outputs already in [research.md](research.md). No additional Phase 0 research needed.

### Research Summary (cross-reference)

| Decision | Rationale | Alternatives | Source |
|----------|-----------|--------------|--------|
| **Tool**: gitleaks (not trufflehog/detect-secrets/git-secrets/SecretLint/GitGuardian) | MIT license; Go binary single-file distribution; <2s scan; pattern-match-only (privacy-preserving); active upstream dev. | trufflehog (AGPL-3.0 friction; Go runtime per research correction; verified-credential probing privacy concern); detect-secrets (baseline-file model conflicts with tachi state-less posture); GitGuardian (commercial SaaS; outbound metadata); SecretLint (Node.js runtime); git-secrets (sparse upstream activity; AWS-narrow defaults). | research.md §Industry Research; PRD §Tech-Selection table; ADR-042 §Alternatives (9 evaluated). |
| **Pin strategy**: tag (v8.30.1) → `pre-commit autoupdate --freeze` → commit SHA stored in `.pre-commit-config.yaml` | Tag readability for humans; SHA immutability for supply-chain hygiene per PRD §R-3. | Floating tag (rejected — supply-chain risk on tag force-move); branch reference (rejected — moves on every push). | research.md §Pre-commit Framework + Gitleaks Pinning. |
| **Schema**: `[[allowlists]]` (TOML array of tables; gitleaks v8.25.0+) | Latest schema; multiple allowlists for finer-grained scoping. | Legacy `[allowlist]` (rejected — deprecated in v8.25.0; future schema break risk). | research.md §`.gitleaks.toml` Schema. |
| **CLI shape**: `gitleaks git --staged` for local hook; `gitleaks git` (full repo) for CI | New shape per gitleaks v8.19.0+ deprecation of `detect`/`protect`. | `detect`/`protect` (rejected — deprecated; `--help` hides them in v8.19.0+). | research.md §Gitleaks CLI Shape Change. |
| **CI invocation**: gitleaks **binary directly** in `.github/workflows/gitleaks.yml` | Avoids `gitleaks-action@v2` proprietary license that requires paid `GITLEAKS_LICENSE` for org repos. | `gitleaks-action@v2` (rejected — license cost); `gitleaks-action@v1` MIT (rejected — abandoned, last release pre-v2). | research.md §gitleaks-action License Issue. |
| **Wrapper**: separate file at `.aod/scripts/bash/precommit-wrap.sh` (Q9 resolved) | Testable in isolation; versionable; LOCAL-ONLY (CI uses native binary invocation per PM-5 resolution). | Inline `entry: bash -c '...'` in `.pre-commit-config.yaml` (rejected — harder to maintain, cannot unit-test). | research.md §Wrapper-Script Pattern; PM-5 LOCAL-ONLY clarification. |
| **Init prompt**: raw `read -p` (Q10 resolved) | Single-char Y/n is below F-1 free-text-injection threshold; precedent already in init.sh lines 85/110/144/146/148/177; documented waiver in ADR-042 §Consequences. | F-1 `aod_init_read_validated` helper (rejected — over-engineering for Y/n; consistency-with-itself argument doesn't apply since init.sh already mixes patterns). | research.md §F-1 Substitution-Surface Helper. |
| **TTY check**: `[ -t 0 ]` at start of prompt block | Canonical bash idiom; transparent semantics; works on macOS Bash 3.2 + Linux Bash 4.x+. | `tty -s` (functionally equivalent; rejected for `[ -t 0 ]` consistency with existing tachi bash idioms). | research.md §init.sh Insertion Point. |
| **Custom rule disposition**: warn-only for `tachi-personalization-env` and `tachi-security-exceptions-jsonl` (Q1/Q2) | Non-blocking on first run; teaches without breaking CI; complements F-1 detection-tier contract continuity. | Block (rejected — first-run kill-switch risk; adopter pulls update, runs `pre-commit run --all-files`, hits warn-only blockers, reports false positives). | spec.md §Resolved-Questions Q1/Q2. |
| **CI scope**: full-repo scan on PRs (Q5) | Catches pre-existing-but-unscanned credentials in older commits at merge time. | PR-diff scope (rejected — risks missing pre-existing credentials; one-time full scan at PR open is adequate). | spec.md §Resolved-Questions Q5. |

## Phase 1: Design & Contracts

**Status**: Generated below. F-5 has no API contracts (no API surface) and no data model (no application state). The "design artifacts" for F-5 are: (1) component architecture, (2) data flow, (3) tech stack inventory, (4) adopter quickstart, (5) AC-SPEC-1 fixture catalog.

### 1. Components

```
┌──────────────────────────────────────────────────────────────────────┐
│                    Adopter Developer Workstation                      │
│                                                                       │
│  ┌────────────────┐    ┌──────────────────────┐    ┌──────────────┐ │
│  │  scripts/      │    │  .pre-commit-config  │    │   gitleaks   │ │
│  │  init.sh       │───▶│  .yaml (pinned SHA)  │───▶│   binary     │ │
│  │  + opt-in      │    │  invokes wrapper     │    │  (Go, MIT)   │ │
│  │    prompt      │    └──────────┬───────────┘    └──────┬───────┘ │
│  │  + TTY gate    │               │                       │         │
│  │  + flag        │    ┌──────────▼─────────────┐         │         │
│  │    handling    │    │ .aod/scripts/bash/     │◀────────┤         │
│  └────────┬───────┘    │ precommit-wrap.sh      │         │         │
│           │            │ (LOCAL-ONLY)           │         │         │
│           │            │ - calls gitleaks       │         │         │
│           │            │ - augments stderr w/   │         │         │
│           │            │   bypass + docs link   │         │         │
│           │            └────────────────────────┘         │         │
│           │                                               │         │
│           ▼                                               ▼         │
│  ┌──────────────────┐                          ┌────────────────┐  │
│  │ .aod/            │                          │  .gitleaks.    │  │
│  │ personalization  │                          │  toml          │  │
│  │ .env.example     │                          │  - allowlist   │  │
│  │ (template,       │                          │  - 2 custom    │  │
│  │  path-allow-     │                          │    rules       │  │
│  │  listed)         │                          │    (warn-only) │  │
│  └──────────────────┘                          └────────────────┘  │
│                                                                     │
└──────────────────────────────────────────────────────────────────────┘
                              │ git push
                              ▼
┌──────────────────────────────────────────────────────────────────────┐
│                          GitHub Actions Runner                        │
│                                                                       │
│  ┌─────────────────────────────────┐                                 │
│  │ .github/workflows/gitleaks.yml  │                                 │
│  │ - on: pull_request              │                                 │
│  │ - download gitleaks binary      │                                 │
│  │   (release tarball + checksum)  │                                 │
│  │ - run: gitleaks git             │                                 │
│  │     --config=.gitleaks.toml     │                                 │
│  │     --report-format=sarif       │                                 │
│  │ - NATIVE OUTPUT (no wrapper)    │                                 │
│  │ - upload SARIF to               │                                 │
│  │   GitHub Code Scanning          │                                 │
│  └─────────────────────────────────┘                                 │
│                                                                       │
└──────────────────────────────────────────────────────────────────────┘
```

**Component summary**:
- **`scripts/init.sh`** (delta): adds opt-in prompt block (~10-20 LOC) gated by `[ -t 0 ]` TTY check + `--no-precommit`/`--precommit` flag handling. Inserts after personalization-confirmation block (line 177-185 region per research). Uses raw `read -p` (Q10 waiver in ADR-042 §Consequences).
- **`.pre-commit-config.yaml`** (new): pinned-commit-SHA reference to `gitleaks/gitleaks` repo; hook entry invokes `.aod/scripts/bash/precommit-wrap.sh`. Hook is opt-in — file presence does NOT auto-install; adopter must run `pre-commit install` (or accept init.sh prompt).
- **`.aod/scripts/bash/precommit-wrap.sh`** (new): local-only wrapper. Captures gitleaks exit code BEFORE any stderr augmentation (Pre-Mortem FM-5 mitigation). Augments gitleaks stderr with (a) rule ID, (b) file:line — already in gitleaks default output, (c) `SKIP=gitleaks git commit ...` bypass guidance, (d) `See docs/standards/PRECOMMIT_HOOKS.md` docs link. Preserves exit code.
- **`.gitleaks.toml`** (new): `[extend] useDefault = true` + `[[allowlists]]` for env-var placeholders + fixture/docs/example paths + `.aod/personalization.env.example` + 2 `[[rules]]` entries (`tachi-personalization-env`, `tachi-security-exceptions-jsonl`) — both warn-only (Q1/Q2). Excluded paths: `node_modules/`, `.git/`, `archive/`.
- **`.aod/personalization.env.example`** (new): template documenting expected `init.sh` keys with placeholder values. Path-allow-listed in `.gitleaks.toml`. Tracked (not gitignored) — the populated `.aod/personalization.env` remains gitignored per F-1.
- **`docs/standards/PRECOMMIT_HOOKS.md`** (new, ~150-250 LOC): self-contained operator handbook. 9 sections per PRD AC-10. Per-rule rationale catalog cross-linked to `.gitleaks.toml`.
- **`docs/architecture/02_ADRs/ADR-042-pre-commit-secret-scanning-default.md`** (new, ~130-180 LOC): architecture decision record. Sections: Context / Decision / Alternatives (9) / Consequences (pin-bump cadence + raw-read-p waiver) / References. Trufflehog comparison entry corrected to `runtime: Go` (PRD comparison-matrix error).
- **`.github/workflows/gitleaks.yml`** (new, ~25-40 LOC): dedicated single-purpose CI parity workflow. Triggers on `pull_request`. Downloads gitleaks binary directly (release tarball + checksum verification); invokes `gitleaks git --config=.gitleaks.toml`; reports SARIF to GitHub Code Scanning. Uses native gitleaks output (NO wrapper script — preserves SARIF compatibility per PM-5).
- **`tests/fixtures/gitleaks-rule-interaction/`** (new): 16+ synthetic-fixture cases for AC-SPEC-1 preventive rule-interaction test. Subdirectories: `staged-credential/`, `placeholder/`, `path-allow-listed/`, `path-excluded/`. Each fixture is a standalone file with deliberately-fake credential payload. Test runner is a small bash script (or pytest test under existing `tachi-pytest.yml` if convenient — TBD at task time).
- **`CHANGELOG.md`** (delta, ~3-5 LOC): sibling-h3 BLP-02-cluster placement (`### Pre-commit secret-scanning defaults (BLP-02 F-5)`) — N-4 carry-forward through F-2/F-3/F-4.
- **`README.md`** (delta, ~1 LOC): one-line pointer in existing "Security" subsection (Q7 resolved).

### 2. Data Flow

#### Local pre-commit hook flow (US-1, US-2, US-4)

```
1. Developer: git add <file>
2. Developer: git commit -m "..."
3. git invokes: .git/hooks/pre-commit (installed via `pre-commit install`)
4. pre-commit framework reads: .pre-commit-config.yaml
5. pre-commit framework invokes hook entry: .aod/scripts/bash/precommit-wrap.sh
6. precommit-wrap.sh invokes: gitleaks git --staged --config=.gitleaks.toml
   (or current CLI shape per gitleaks v8.30.1)
7. gitleaks scans staged-content payload against:
   a. gitleaks default rules (extended via [extend] useDefault=true)
   b. tachi custom rules (tachi-personalization-env warn-only,
      tachi-security-exceptions-jsonl warn-only)
   c. tachi allowlist ([[allowlists]] env-var placeholders, fixture/docs paths,
      .aod/personalization.env.example, node_modules/, archive/)
8a. gitleaks exits 0 (no findings) → wrapper exits 0 silently → commit proceeds.
8b. gitleaks exits 1 (rule fired) → wrapper captures exit code →
    augments stderr with (rule ID + file:line + SKIP guidance + docs link) →
    wrapper exits with gitleaks' captured exit code → commit refused.
9. Developer remediation: either fix the credential, add `# gitleaks:allow`,
   add path to `.gitleaks.toml` allowlist, OR `SKIP=gitleaks git commit ...`.
```

#### CI parity flow (US-6)

```
1. Developer: git push origin <feature-branch>
2. Developer: gh pr create
3. GitHub triggers .github/workflows/gitleaks.yml on pull_request event.
4. Workflow runs:
   a. checkout repo (full history per Q5 full-repo scan resolution)
   b. download gitleaks binary release tarball + verify checksum
   c. invoke: gitleaks git --config=.gitleaks.toml
       --report-format=sarif --report-path=gitleaks.sarif
       (NATIVE invocation — NO wrapper; preserves SARIF compatibility)
   d. upload-sarif action publishes to GitHub Code Scanning
5a. gitleaks exits 0 → workflow check passes → PR proceeds.
5b. gitleaks exits 1 → workflow check fails → PR blocked from merge.
6. Developer remediation: same as local flow (see step 9 above).
```

#### init.sh prompt flow (US-1 first-time-adopter, US-3 existing-adopter no-surprise, FR-004)

```
First-time adopter (TTY context, no flags):
1. Adopter: bash scripts/init.sh
2. init.sh: ... existing personalization prompts ...
3. init.sh checks: [ -t 0 ] → TRUE (TTY present)
4. init.sh checks: $1 = --no-precommit? → NO
5. init.sh checks: $1 = --precommit? → NO
6. init.sh prompts: "Install pre-commit secret-scanning hook (gitleaks)? [Y/n] "
7. Adopter: <press Enter> (defaults to Y)
8. init.sh invokes: pre-commit install
9a. pre-commit installed → .git/hooks/pre-commit written → init.sh continues.
9b. pre-commit not installed → init.sh logs WARN, continues (does NOT abort).

Non-interactive adopter (CI / expect / </dev/null):
1. Adopter: bash scripts/init.sh </dev/null
2. init.sh: ... existing personalization prompts handled by --json or env-var path ...
3. init.sh checks: [ -t 0 ] → FALSE (no TTY)
4. init.sh checks: $1 = --precommit? → NO (path 6 below for opposite)
5. init.sh skips prompt + skips pre-commit install.
6. init.sh: ... continues with rest of init flow ...

Adopter with --no-precommit override (TTY context):
1. Adopter: bash scripts/init.sh --no-precommit
2. init.sh: ... existing personalization prompts ...
3. init.sh checks: [ -t 0 ] → TRUE
4. init.sh checks: $1 = --no-precommit? → YES
5. init.sh skips prompt + skips pre-commit install.
6. init.sh: ... continues with rest of init flow ...

Adopter with --precommit explicit-accept (non-interactive expect-style):
1. Adopter: bash scripts/init.sh --precommit </dev/null
2. init.sh: ... existing personalization prompts ...
3. init.sh checks: [ -t 0 ] → FALSE (no TTY)
4. init.sh checks: $1 = --precommit? → YES
5. init.sh invokes: pre-commit install (without prompting)
6. init.sh: ... continues with rest of init flow ...
```

#### Existing-adopter no-surprise flow (US-3, FR-010)

```
1. Existing adopter: cd <existing-tachi-clone>; git pull
2. git pull pulls F-5 changes including:
   - .pre-commit-config.yaml (new file)
   - .gitleaks.toml (new file)
   - scripts/init.sh (delta — but init.sh already self-deleted on previous run!)
   - CHANGELOG.md (delta)
   - README.md (delta)
3. .git/hooks/pre-commit: NOT WRITTEN (file presence of .pre-commit-config.yaml
   does NOT auto-install).
4. Adopter reads CHANGELOG: "to enable, run pre-commit install".
5. Adopter chooses: ignore (no opt-in) OR explicit pre-commit install (opt-in).
```

### 3. Tech Stack

| Component | Technology | Version | License | Pinning |
|-----------|-----------|---------|---------|---------|
| Pre-commit framework | `pre-commit` | >= 3.5.0 (R-10 floor; current upstream v4.6.0) | MIT | adopter-installed; not vendored by tachi |
| Secret scanner | `gitleaks` | v8.30.1 (commit SHA via `pre-commit autoupdate --freeze`) | MIT | pinned commit SHA in `.pre-commit-config.yaml` |
| Bash | `bash` | 3.2+ (macOS native compat) | GPL-3.0 (system bash; not redistributed) | system-provided |
| TOML parser | `gitleaks` internal (Go `toml` package) | bundled with gitleaks | MIT (bundled) | bundled |
| GitHub Actions runner | `ubuntu-latest` | GitHub-managed | N/A | GitHub-managed |
| YAML parser | `pre-commit` framework + GitHub Actions | bundled | MIT / various | bundled |

### 4. Adopter Quickstart

**Audience**: First-time tachi adopter wanting to enable pre-commit secret-scanning.

**Steps**:
1. `git clone https://github.com/davidmatousek/tachi.git my-project`
2. `cd my-project`
3. `bash scripts/init.sh` — accept the default `Y` at the prompt: `Install pre-commit secret-scanning hook (gitleaks)? [Y/n]`
4. Verify: `ls -la .git/hooks/pre-commit` — should exist after init.sh.
5. Test: stage a deliberately-fake credential (e.g., `echo "ghp_$(openssl rand -hex 20)" > /tmp/test-cred && cp /tmp/test-cred test.txt && git add test.txt`), run `git commit -m "test"`, verify the commit is refused with rule ID + file:line + bypass guidance + docs link.
6. Cleanup: `git reset HEAD test.txt && rm test.txt /tmp/test-cred`.

**Existing adopter (re-running update)**:
1. `cd <existing-tachi-clone>; git pull origin main`
2. `pre-commit install` (manual opt-in; `git pull` does NOT auto-install).
3. Verify + test as above.

**Opt-out**:
1. `pre-commit uninstall` removes `.git/hooks/pre-commit`.
2. Re-running `pre-commit install` re-enables the hook.
3. Per-commit bypass: `SKIP=gitleaks git commit -m "..."`.
4. Per-line opt-out: append `# gitleaks:allow` adjacent to the known-fake credential.
5. Full disable: `git commit --no-verify` (bypasses all pre-commit hooks).

### 5. AC-SPEC-1 Synthetic-Fixture Catalog (FR-013)

Per spec.md FR-013, the fixture directory `tests/fixtures/gitleaks-rule-interaction/` ships 16 cases minimum. Catalog:

#### Should-fire (rule fires AND blocks commit)

| # | Path | Content | Expected Rule | Test Outcome |
|---|------|---------|---------------|--------------|
| 1 | `staged-credential/github-pat.txt` | `ghp_` + 36 random hex chars | `github-pat` | gitleaks exits 1, rule ID `github-pat` |
| 2 | `staged-credential/aws-access-key.txt` | `AKIA` + 16 alphanumeric | `aws-access-token` | gitleaks exits 1, rule ID `aws-access-token` |
| 3 | `staged-credential/openai-key.txt` | `sk-` + 48 alphanumeric (real format) | `openai-api-key` (or `generic-api-key`) | gitleaks exits 1, real-format rule ID |
| 4 | `staged-credential/anthropic-key.txt` | `sk-ant-` + random | `anthropic-api-key` (or `generic-api-key`) | gitleaks exits 1, rule ID matches |
| 5 | `staged-credential/private-key-block.pem` | `-----BEGIN RSA PRIVATE KEY-----...` PEM block | `private-key` | gitleaks exits 1, rule ID `private-key` |
| 6 | `staged-credential/personalization-env-populated.env` | `AOD_PERSONALIZATION_PROJECT_NAME=acme-prod` (non-placeholder) | `tachi-personalization-env` | gitleaks exits 1 (warn-only — but exit is non-zero per gitleaks default for findings; warn-only here means severity=warning in `.gitleaks.toml`, NOT exit-code-zero) |

#### Should-NOT-fire (rule does not fire OR is allow-listed)

| # | Path | Content | Allow-list mechanism | Test Outcome |
|---|------|---------|----------------------|--------------|
| 7 | `placeholder/env-var-reference.txt` | `password = "$ENV_VAR"` | env-var-placeholder allowlist regex | gitleaks exits 0 |
| 8 | `placeholder/openai-placeholder.env` | `OPENAI_API_KEY=PLACEHOLDER` | placeholder allowlist regex | gitleaks exits 0 |
| 9 | `placeholder/sk-placeholder.env` | `OPENAI_API_KEY=sk-PLACEHOLDER...` | sk-PLACEHOLDER allowlist | gitleaks exits 0 |
| 10 | `placeholder/sk-test-stripe.env` | `STRIPE_KEY=sk-test-...` | sk-test- allowlist (Stripe test-mode) | gitleaks exits 0 |
| 11 | `path-allow-listed/personalization-env-example` | duplicate of `.aod/personalization.env.example` | path allowlist | gitleaks exits 0 |
| 12 | `path-allow-listed/tests-fixtures-fake-aws.txt` | fake AWS key UNDER `tests/fixtures/` path | path allowlist | gitleaks exits 0 |
| 13 | `path-allow-listed/docs-placeholder.md` | `ghp_<placeholder>` UNDER `docs/` path | path allowlist | gitleaks exits 0 |
| 14 | `path-allow-listed/security-exceptions-jsonl-auto.jsonl` | auto-generated `.security/exceptions.jsonl` entry | conditional: if auto-generated marker present, no rule fires; if manual edit detected, `tachi-security-exceptions-jsonl` warn-only fires | gitleaks exits 0 (auto-gen path) |
| 15 | `path-excluded/node-modules-credential.txt` | fake credential UNDER `node_modules/` | excluded paths | gitleaks exits 0 |
| 16 | `path-excluded/archive-credential.txt` | fake credential UNDER `archive/` | excluded paths | gitleaks exits 0 |

**Test runner**: a small bash script `tests/scripts/test_gitleaks_rules.sh` (~30-50 LOC) iterates over `tests/fixtures/gitleaks-rule-interaction/` subdirectories. For each fixture:
- Determine expected outcome from subdirectory (`staged-credential/` → fire; `placeholder/` + `path-allow-listed/` + `path-excluded/` → no-fire).
- Invoke `gitleaks detect --no-git --source=<fixture-path> --config=.gitleaks.toml --report-format=json --report-path=/tmp/gitleaks-result.json`.
- Compare exit code + JSON findings against expectation.
- Emit pass/fail per fixture.
- Exit 1 if any fixture fails expectation; exit 0 if all pass.

**CI integration**: invoke `tests/scripts/test_gitleaks_rules.sh` from `.github/workflows/gitleaks.yml` (after the full-repo scan step) OR from a separate workflow step OR from existing `tachi-pytest.yml` (if pytest harness preferred — TBD at task time per Pre-Mortem FM-3 guidance).

### 6. Init.sh Prompt-Flag Matrix Test (Pre-Mortem FM-3 Design Consideration)

Per Pre-Mortem FM-3 and user input, surface the `init.sh` prompt-flag matrix as a tasks.md candidate. Matrix (6 cases):

| TTY | Flag | Expected Behavior |
|-----|------|-------------------|
| TTY | (no flag) | Prompt fires, defaults Y, `pre-commit install` invoked on accept |
| TTY | `--no-precommit` | Prompt skipped, `pre-commit install` NOT invoked |
| TTY | `--precommit` | Prompt skipped, `pre-commit install` invoked unconditionally |
| no-TTY | (no flag) | Prompt skipped, `pre-commit install` NOT invoked |
| no-TTY | `--no-precommit` | Prompt skipped, `pre-commit install` NOT invoked (no-op flag) |
| no-TTY | `--precommit` | Prompt skipped, `pre-commit install` invoked unconditionally |

**Test mechanism**: bash harness invoking init.sh under various stdin/argv combinations using `expect`-style automation OR shell redirect tricks (`</dev/null` for no-TTY simulation). Matrix runs in CI to prevent FM-3 ("flag silently doesn't work due to bash-quoting edge case") regression.

**Decision deferred to /aod.tasks**: whether to ship this matrix test as a new test file (`tests/scripts/test_init_precommit_matrix.sh`) or fold into existing init.sh test harness (if any). Both options preserve test coverage; choice depends on existing test layout.

### 7. Phase 1 Re-evaluation

**Constitution re-check after design**:
- All 11 applicable principles still PASS (no design choices introduced violations).
- Principle V (Privacy) explicitly preserved: gitleaks runs locally only; binary download in CI is one-time per workflow run, not per-commit metadata phone-home.
- Principle VI (Testing) strengthened by AC-SPEC-1 fixture catalog + FM-3 matrix consideration.
- Principle VII (DoD) gates engaged at /aod.deliver: AC-3, AC-4, AC-5, AC-6, AC-7, AC-9, AC-12, AC-15, AC-16 all empirically verifiable.

**Architectural integrity**:
- No new application code paths.
- No state mutations.
- No taxonomy / `finding.yaml` changes (12-feature streak preserved).
- Local-only privacy posture preserved.
- Existing test infrastructure (`tachi-pytest.yml`) is touched only if the FM-3 matrix test or AC-SPEC-1 runner is hosted there.

## Project Structure

### Documentation (this feature)

```
specs/282-pre-commit-secret-scanning-defaults/
├── plan.md              # This file
├── spec.md              # Feature spec (PM APPROVED_WITH_CONCERNS)
├── research.md          # /aod.spec research output
├── checklists/
│   └── requirements.md  # Spec quality checklist
└── tasks.md             # Generated by /aod.tasks (next sub-step)
```

**No `data-model.md`, no `contracts/` directory, no separate `quickstart.md`** — F-5 has no API surface and no data model. The "design artifacts" for this feature are folded into this plan.md (Components / Data Flow / Tech Stack / Adopter Quickstart sections).

### Source Code (repository root)

```
tachi/
├── .pre-commit-config.yaml            # NEW (~30-50 LOC) — pre-commit framework config
├── .gitleaks.toml                     # NEW (~50-80 LOC) — gitleaks rules + allowlist
├── .aod/
│   ├── personalization.env.example    # NEW (~10-20 LOC) — adopter-keys template
│   └── scripts/
│       └── bash/
│           └── precommit-wrap.sh      # NEW (~30-60 LOC) — local-only wrapper
├── .github/
│   └── workflows/
│       └── gitleaks.yml               # NEW (~25-40 LOC) — CI parity (binary-direct)
├── docs/
│   ├── architecture/
│   │   └── 02_ADRs/
│   │       └── ADR-042-pre-commit-secret-scanning-default.md  # NEW (~130-180 LOC)
│   └── standards/
│       └── PRECOMMIT_HOOKS.md         # NEW (~150-250 LOC) — operator handbook
├── scripts/
│   └── init.sh                        # DELTA (~10-20 LOC) — opt-in prompt + flags
├── tests/
│   ├── fixtures/
│   │   └── gitleaks-rule-interaction/  # NEW — 16+ synthetic fixtures
│   │       ├── staged-credential/      # 6 fixtures — should-fire
│   │       ├── placeholder/            # 4 fixtures — should-NOT-fire (placeholder)
│   │       ├── path-allow-listed/      # 4 fixtures — should-NOT-fire (path)
│   │       └── path-excluded/          # 2 fixtures — should-NOT-fire (excluded)
│   └── scripts/
│       └── test_gitleaks_rules.sh     # NEW (~30-50 LOC) — fixture runner
├── CHANGELOG.md                        # DELTA (~3-5 LOC) — Unreleased BLP-02 F-5
└── README.md                           # DELTA (~1 LOC) — Security pointer
```

**Structure Decision**: Documentation + scaffold + bash-script-delta only. No new app directories. New top-level paths: `tests/fixtures/gitleaks-rule-interaction/`, `tests/scripts/` (if not already present); `.aod/scripts/bash/precommit-wrap.sh` extends existing `.aod/scripts/bash/` directory; remainder are repo-root or existing-subdir additions/deltas.

## Components

(see Phase 1 §1 above)

## Data Flow

(see Phase 1 §2 above)

## Tech Stack

(see Phase 1 §3 above)

## FR Consolidation (PM-3 Resolution)

Per PM-3 deferred concern: FR-009 ("Refused-commit error message contract") fully duplicates FR-008 ("`.aod/scripts/bash/precommit-wrap.sh` wrapper script"). Consolidation decision:

**Decision**: Promote FR-008 to dual-mandate naming. Effective FR-008 description: "Wrapper script + refused-commit error message contract." FR-009 retained as a sub-clause-style placeholder pointing to FR-008 acceptance scenario 2 (which already covers the contract).

**Rationale**: The wrapper script IS the mechanism that delivers the four-item refused-commit contract. Two FRs for one mechanism inflates FR count without adding distinct verifiable behavior.

**Implementation note**: The spec's FR-009 explicitly says "Acceptance: Same as FR-008 acceptance scenarios 2." This consolidation does not require a spec edit — it is a plan-time clarification that tasks.md will treat the contract as a single deliverable per FR-008.

**Tasks.md guidance**: Generate ONE task family for FR-008 covering wrapper-script implementation + AC-15 contract verification + AC-3 empirical-test-fires verification (all three traces converge on the wrapper).

## Pre-Mortem Failure-Mode Mitigations (Carry-forward)

| FM | Description | Mitigation in plan |
|----|-------------|---------------------|
| FM-1 | False-positive flood despite AC-SPEC-1 (R-1 realized) | AC-SPEC-1 16+ fixtures; PRD §R-1 contingency hot-patch; AC-19 follow-up Issue at /aod.deliver |
| FM-2 | Wrapper breaks gitleaks JSON output for CI parity | **RESOLVED in spec amendment**: FR-007 acceptance + FR-008 acceptance both clarify wrapper is LOCAL-ONLY; CI invokes gitleaks binary directly to preserve SARIF compatibility |
| FM-3 | Q4 `--precommit` flag goes untested | tasks.md candidate: init.sh prompt-flag matrix test (6 cases) — surfaced in Phase 1 §6 |
| FM-4 | Pin-bump cadence never executes | ADR-042 §Consequences captures cadence; BLP-02 closure memo in /aod.deliver references it as recurring maintenance commitment |
| FM-5 | Wrapper exit-code semantics break gitleaks | Implementation pattern documented: `gitleaks ...; rc=$?; { stderr augmentation; } >&2; exit $rc` — capture exit code BEFORE augmentation |

## Complexity Tracking

| Decision | Why Needed | Simpler Alternative Rejected Because |
|----------|------------|-------------------------------------|
| Wrapper script (FR-008) instead of inline `entry: bash -c '...'` | Testability + maintainability; gitleaks does NOT support stderr templating per Architect C-2 + research independent verification | Inline `entry:` rejected per Q9 because cannot unit-test the augmentation logic in isolation |
| Direct gitleaks binary invocation in CI instead of `gitleaks-action@v2` | gitleaks-action@v2 license is proprietary; org-repo would require paid `GITLEAKS_LICENSE` per research finding | gitleaks-action@v1 (last MIT release pre-v2) rejected because abandoned upstream; binary invocation gives equivalent functionality without license cost |
| Synthetic-fixture rule-interaction test (FR-013) instead of integration tests against real-world adopter scenarios | Preventive false-positive verification per Architect C-4; deterministic + reproducible | Integration tests rejected because adopter scenarios are not enumerable upfront; synthetic fixtures cover known patterns + 10-20 expected adopter cases |
| Two custom rules warn-only (Q1/Q2) instead of block | Non-blocking on first-run; teaches without breaking CI; complements F-1 detection-tier contract continuity | Block rejected because first-run kill-switch risk dominates teaching value; warn-only preserves opt-in incentive |
| Full-repo CI scan (Q5) instead of PR-diff scope | Catches pre-existing-but-unscanned credentials in older commits at merge time | PR-diff rejected because risks missing pre-existing credentials; full-repo scan is one-time-per-PR cost |

## Dependencies & Sequencing (preview for /aod.tasks)

Implementation order constraints (drives tasks.md wave structure):

1. **Wave 1 (foundation)** — `.gitleaks.toml` + `.pre-commit-config.yaml` + `.aod/personalization.env.example` + `.aod/scripts/bash/precommit-wrap.sh`. These are file-disjoint and can be authored in parallel by a single engineer. Produces an installable hook.
2. **Wave 2 (verification)** — `tests/fixtures/gitleaks-rule-interaction/` + `tests/scripts/test_gitleaks_rules.sh`. Depends on Wave 1 (`.gitleaks.toml` must exist for fixtures to validate). AC-SPEC-1 entry-criteria gate.
3. **Wave 3 (init.sh + CI)** — `scripts/init.sh` delta + `.github/workflows/gitleaks.yml`. Depends on Wave 1. The init.sh delta exercises Wave 1's hook; the CI workflow uses Wave 1's `.gitleaks.toml`.
4. **Wave 4 (docs + ADR)** — `docs/standards/PRECOMMIT_HOOKS.md` + `ADR-042` + `CHANGELOG.md` + `README.md`. Depends on Waves 1-3 (must reference final implementation behavior). Per-rule rationale catalog cross-checks against Wave 1's `.gitleaks.toml`.
5. **Wave 5 (delivery + verification)** — AC-12 CI dry-run + AC-15 wrapper-output empirical test + AC-17 release-please verification. Depends on Wave 4 complete.

Realistic single-maintainer ordering: Wave 1 + Wave 3 partially-parallel; Wave 2 sequential after Wave 1; Wave 4 sequential after Waves 1-3; Wave 5 at /aod.deliver time. Total ~9-13h active per Team-Lead A-1 calibration.

## Risk Register (carried forward from PRD §R-1 through §R-10)

| ID | Risk | Likelihood | Impact | Mitigation | Plan Section |
|----|------|-----------|--------|------------|--------------|
| R-1 | False-positive flood on adopter codebases | Medium | High | AC-SPEC-1 (FR-013); R-1 contingency hot-patch | Phase 1 §5 |
| R-2 | Pre-commit framework distribution friction | Low-Medium | Medium | init.sh fallback WARN; PRECOMMIT_HOOKS.md 3 install paths | Components |
| R-3 | gitleaks upstream tag force-move | Low | High | Pinned commit SHA; pin-bump cadence policy in ADR-042 | Tech Stack |
| R-4 | Existing-adopter dual-hook conflict | Medium | Low | No-auto-install; explicit `pre-commit install` opt-in | Data Flow |
| R-5 | `git commit --no-verify` bypass | High | Medium | Documented limitation; CI parity back-stop | Components + Data Flow |
| R-6 | gitleaks default rule set evolves | Medium | Medium | Pinned commit SHA freezes; pin-bump cadence requires synthetic-fixture re-test | Pre-Mortem FM-4 |
| R-7 | Privacy concern (gitleaks scanning adopter content) | N/A | N/A | Local-only; no outbound HTTP | Tech Stack + Components |
| R-8 | PR/CI gate flakiness | Low | Low | gitleaks deterministic; pinned hash mitigates upstream-distribution flakiness | Components |
| R-9 | Adopter `.gitleaks.toml` divergence on `make update` | High | Medium | PRECOMMIT_HOOKS.md §Adopter-Customization documents merge pattern | Adopter Quickstart |
| R-10 | Pre-commit framework version drift | Low | Low | Minimum version 3.5.0 in PRECOMMIT_HOOKS.md §Known-Limitations | Tech Stack |

## References

- Spec: [spec.md](spec.md)
- Research: [research.md](research.md)
- PRD: [docs/product/02_PRD/282-pre-commit-secret-scanning-defaults-2026-05-09.md](../../docs/product/02_PRD/282-pre-commit-secret-scanning-defaults-2026-05-09.md)
- Constitution: [.aod/memory/constitution.md](../../.aod/memory/constitution.md)
- F-3 plan precedent: [specs/272-security-md-disclosure/plan.md](../272-security-md-disclosure/plan.md)
- F-4 plan precedent: [specs/277-claude-permissions-baseline/plan.md](../277-claude-permissions-baseline/plan.md)
- ADR-038 (F-1 substitution surface): [docs/architecture/02_ADRs/ADR-038-placeholder-substitution-strategy.md](../../docs/architecture/02_ADRs/ADR-038-placeholder-substitution-strategy.md)
- ADR-040 (F-2 config-file parsing): [docs/architecture/02_ADRs/ADR-040-config-file-parsing-hardening.md](../../docs/architecture/02_ADRs/ADR-040-config-file-parsing-hardening.md)
- ADR-041 (F-4 permissions baseline): [docs/architecture/02_ADRs/ADR-041-claude-permissions-baseline.md](../../docs/architecture/02_ADRs/ADR-041-claude-permissions-baseline.md)
- F-1 helper source: [.aod/scripts/bash/init-input.sh](../../.aod/scripts/bash/init-input.sh)
- gitleaks repo: https://github.com/gitleaks/gitleaks
- pre-commit framework: https://pre-commit.com/

## Status & Next Steps

- **Plan status**: Draft → Pending dual sign-off (PM + Architect)
- **PM concerns carried forward from /aod.spec**:
  - PM-1 (trace label gap) — RESOLVED inline in spec amendment
  - PM-2 (SC-007 qualitative disclaimer) — RESOLVED inline in spec amendment
  - PM-3 (FR-009 redundancy) — **RESOLVED in this plan**: §FR Consolidation (PM-3 Resolution)
  - PM-4 (pin-bump cadence assumption) — RESOLVED inline in spec amendment
  - PM-5 (wrapper LOCAL-ONLY / CI uses native invocation) — RESOLVED inline in spec amendment + reinforced in this plan §1 + §2
- **Pre-Mortem FM-3 design consideration carried forward**: init.sh prompt-flag matrix (6 cases) — surfaced as tasks.md candidate per user input
- **Next**: dual sign-off (PM + Architect) parallel review per Step 3 of /aod.project-plan
