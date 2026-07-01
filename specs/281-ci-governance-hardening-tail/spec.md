---
prd_reference: docs/product/02_PRD/281-ci-governance-hardening-tail-2026-06-30.md
triad:
  pm_signoff:
    agent: product-manager
    date: 2026-07-01
    status: APPROVED_WITH_CONCERNS
    notes: "Faithful, complete refinement of the bundle PRD — all 4 goals (G1–G4), 19 namespaced FRs (1:1 traceability), all ACs, 5 SCs, and the split-valve boundary covered with zero new product capability. C-1 (stale internal cross-ref: edge-case cited 'US-4 scenario 3'; #287 is US-2 after priority reorder) FIXED 2026-07-01. C-2 (SC-3 ~1h→~5min is a PRD-inherited estimate, not instrumented — awareness only; substrate FR-286.1/.2/.3 fully specified). Cleared to /aod.project-plan. Details: .aod/results/product-manager-281.md"
  architect_signoff: null  # Added by /aod.project-plan
  techlead_signoff: null   # Added by /aod.tasks
---

# Feature Specification: CI & Governance Hardening Tail (F-4/F-5 follow-ups)

**Feature Branch**: `281-ci-governance-hardening-tail`
**Created**: 2026-07-01
**Status**: Draft
**Input**: Bundle PRD `docs/product/02_PRD/281-ci-governance-hardening-tail-2026-06-30.md` — lead issue **#281**, members **#285 / #286 / #287** (#285/#286 are split-valve candidates whose carve-in vs. carve-out is decided at `/aod.tasks`, not here). #280 pre-delivered (PR #290) and excluded.

> **Bundle spec.** This is the Wave-2 hygiene-tail feature of BLP-06. It ports the already-shipped F-4 (permissions) and F-5 (gitleaks) local pre-commit checks into CI-enforced, auditable, maintainable surfaces. It adds **no** product capability — it makes the existing surface *more defensible*. Requirements preserve the PRD's namespaced IDs (`FR-281.x` etc.) for 1:1 traceability.

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 — Permissions surface verified in CI (Priority: P1) · #281 (lead)

*As a tachi maintainer,* I want the permissions surface (`.claude/settings.json` + `CLAUDE_PERMISSIONS.md`) validated in CI on every PR that touches it **and** on direct pushes to `main`, *so that* a `--no-verify` commit, an uninstalled hook, or a GitHub web-UI edit that breaks JSON validity or orphans a rule/table-row **reddens the build** instead of silently landing on `main`.

**Why this priority**: This is the load-bearing hardening core (closes F-4 AC-16 / delivers SC-1). It is the cheapest, highest-value item — a near-1:1 clone of the delivered `tachi-catalog-drift.yml` reusing the delivered #280 script — and MUST NOT be blocked by the enhancement items. It is independently shippable and delivers the whole point of the feature on its own.

**Independent Test**: Open a PR that breaks `settings.json` JSON validity (or orphans a rule vs. `CLAUDE_PERMISSIONS.md` §4) and confirm the new `tachi permissions-verify` workflow fails; open a PR touching neither governed file and confirm the workflow does not run.

**Acceptance Scenarios**:

1. **Given** a PR that introduces a JSON syntax error into `.claude/settings.json`, **When** `tachi permissions-verify` runs, **Then** the job fails at the `jq empty` step.
2. **Given** a PR that adds a rule to `settings.json` without a matching `CLAUDE_PERMISSIONS.md` §4 row (or adds a §4 row without a matching rule), **When** the workflow runs, **Then** the job fails at the AC-2 cross-check step on a non-zero exit (exit **1** orphan-diff **or** exit **2** invariant-violation — any non-zero fails).
3. **Given** a PR touching none of the governed paths, **When** the PR opens, **Then** `tachi permissions-verify` does not run at all (path filter → zero CI cost).
4. **Given** the current clean `main`, **When** the workflow runs, **Then** every step passes (rc=0): jq-presence guard green, `jq empty` green, AC-2 cross-check exit 0, and the §3/§4 doc-presence check green. *(Baseline-green pre-state confirmed 2026-06-30: 93 `settings.json` rules ↔ 93 §4 rows, byte-exact.)*
5. **Given** a direct `push` to `main` that touches the permissions surface (bypassing PRs), **When** it lands, **Then** the `push:[main]` trigger runs the same gate (closing the direct-to-main bypass, per the #338/#329 precedent).
6. **Given** a runner image that lacks `jq`, **When** the workflow runs, **Then** it fails loudly at the jq-presence guard *before* the `jq empty` gate — a governance gate must not silently stop governing on runner drift.
7. **Given** a PR that deletes the `## 3. Settings precedence` or `## 4. Per-rule rationale table` section from `CLAUDE_PERMISSIONS.md`, **When** the workflow runs, **Then** the doc-presence check fails. Full behavioral verification of AC-7 (WebFetch subdomain matching) and AC-12 (cross-file deny precedence) is `[MANUAL-ONLY]` requires an interactive Claude Code session and stays at `/aod.build`; CI covers only section presence.

---

### User Story 2 — gitleaks pin-bump cadence is a tracked surface (Priority: P2) · #287

*As a tachi maintainer,* I want a single tracked surface defining the gitleaks pin-bump process, *so that* each upstream release has an unambiguous, re-testable bump recipe and the pin cannot silently rot.

**Why this priority**: Load-bearing hardening core (delivers SC-4). Documentation-only, low-risk, and — together with #281 — the non-negotiable pair that ships even if the enhancement items carve out. It converts the in-comment folklore at `.pre-commit-config.yaml:31` into a canonical, referenceable surface, and its re-derivation step is what keeps #285's catalog honest across bumps.

**Independent Test**: Confirm a single documented process (tag → `autoupdate --freeze` → 16-fixture re-test → rule-ID re-derivation → doc updates) exists and is referenceable by a future `chore(deps): bump gitleaks vX.Y.Z` child issue.

**Acceptance Scenarios**:

1. **Given** the pin-bump cadence surface, **When** a maintainer needs to bump gitleaks on a minor release, **Then** a single canonical process is documented and re-runnable: update tag → `pre-commit autoupdate --freeze` → re-run the 16-fixture rule-interaction matrix (16/16 required) → `pre-commit run --all-files` (zero findings) → **re-derive the #285 per-pattern → rule-ID mapping** → update `ADR-042 §References` + `PRECOMMIT_HOOKS.md §Known-Limitations` on any guarantee change.
2. **Given** a future gitleaks bump child issue, **When** it is opened, **Then** it references the single canonical cadence surface (a documented section and/or issue template) rather than re-deriving the recipe ad hoc.
3. **Given** an upstream gitleaks bump that renames a default rule ID, **When** the cadence's re-derivation step runs, **Then** the staled #285 catalog entry is caught — the fire/no-fire fixture matrix alone stays green on a rename, so the rule-ID re-derivation is the half of R-2 the matrix does not cover. `[MANUAL-ONLY]` runs at bump time and requires provisioning the pinned gitleaks binary.
4. **Given** the (optional, split-valve) scheduled release-detector, **When** it is deemed to exceed chore size at `/aod.tasks`, **Then** it defers to a sibling issue rather than blocking #287's documentation deliverable.

---

### User Story 3 — gitleaks default-rule coverage is documented (Priority: P3) · #285 *(split-valve candidate)*

*As a SecOps reviewer auditing tachi's secret-scanning posture,* I want a documented catalog of which gitleaks default rules cover each canonical credential pattern, *so that* I can produce a coverage audit without reverse-engineering the upstream ruleset.

**Why this priority**: Enhancement-labeled, P3. Genuinely useful for auditability (delivers SC-2) but not load-bearing, and a **split-valve candidate** — its empirical step already reuses the committed `run.sh` + fixture harness that the carve trigger names, so both reviewers lean toward carving it into a separate `F-5-enhancements` feature at `/aod.tasks` if it grows a committed harness of its own.

**Independent Test**: Read the per-pattern → rule-ID catalog in `PRECOMMIT_HOOKS.md` and confirm each canonical pattern maps to a rule ID that a fixture hit empirically confirms; confirm any uncovered pattern has a filed follow-up issue.

**Acceptance Scenarios**:

1. **Given** the documented per-pattern → rule-ID catalog in `PRECOMMIT_HOOKS.md` §3, **When** a reviewer checks any canonical pattern (`ghp_*`, `AKIA*`, `sk-*`, `sk-ant-*`, PEM/private-key blocks, generic high-entropy strings), **Then** the active gitleaks default rule ID is listed and was empirically confirmed by a fixture hit (rule IDs derived by running gitleaks, not transcribed from memory).
2. **Given** a canonical pattern with no covering active default rule, **When** the probe runs, **Then** the gap is flagged and filed as a separate `enhancement` issue — never silently accepted.
3. **Given** the empirical probe step (in CI or at build), **When** it runs, **Then** it provisions the gitleaks binary via the pinned-download + SHA256-verify stanza (v8.30.1, checksum `551f6fc8…`, per `gitleaks.yml`); an absent binary **fails** the step and never skips — a silent-green on an unrun probe would reintroduce the exact anti-pattern this feature exists to kill.

---

### User Story 4 — adopter extensibility starter template (Priority: P3) · #286 *(split-valve candidate)*

*As an adopter extending tachi's secret-scanning,* I want a commented starter template for custom rules, allow-lists, severity, and tool-swap, *so that* I can add my first industry-specific credential pattern in minutes instead of an hour.

**Why this priority**: Enhancement-labeled, P3 (delivers SC-3). A convenience/adoption asset, not a hardening gate, and the second **split-valve candidate** — if it exceeds ~120 LOC or grows its own test surface it carves out with #285.

**Independent Test**: Run `gitleaks detect --config=.gitleaks.toml.adopter-template` and confirm it loads without a config error; confirm `PRECOMMIT_HOOKS.md §9` and `README.md` reference the template.

**Acceptance Scenarios**:

1. **Given** `.gitleaks.toml.adopter-template`, **When** `gitleaks detect --config=.gitleaks.toml.adopter-template` runs (binary provisioned per FR-285.5), **Then** it loads without a config/syntax error.
2. **Given** the template, **When** an adopter reads it, **Then** it contains sectioned, commented examples for (1) custom rules, (2) allow-list extension, (3) per-rule severity, and (4) tool-swap to trufflehog / detect-secrets (grounded in ADR-042 §Alternatives — the differentiator is allow-list ergonomics, not runtime).
3. **Given** `PRECOMMIT_HOOKS.md §9` and the `README.md` Security subsection, **When** an adopter looks for extensibility docs, **Then** both reference the template with usage instructions (consistent with the F-5 pattern).

---

### Edge Cases

- **`jq` missing from runner** → jq-presence guard fails loudly before `jq empty` (FR-281.7); the gate never silently no-ops.
- **Sparse / no-git / trimmed checkout** → the reused AC-2 script's `git rev-parse --show-toplevel` cannot resolve the root and the script exits 2 (fails closed); FR-281.8 mandates a full `actions/checkout@v4` checkout so this cannot silently repoint the root.
- **gitleaks binary download fails or checksum mismatches** → the provisioning step fails; the dependent probe/template-validation step never runs green on an unprovisioned binary (FR-285.5).
- **PR touches none of the governed paths** → workflow does not run (path filter) — zero CI cost (SC-5).
- **Direct push to `main` touching the surface** → `push:[main]` trigger runs the same gate (US-1 scenario 5) — no PR-only blind spot.
- **Canonical pattern with no covering default rule** → flagged + filed as a separate issue (FR-285.4), not silently accepted.
- **Upstream gitleaks bump renames a default rule ID** → the #285 catalog stales silently while the fire/no-fire matrix stays green; #287's re-derivation step (US-2 scenario 3 / FR-287.1) is the compensating catch.
- **Tag push** → GitHub `paths:` filters are bypassed on tag events, but `tachi permissions-verify` triggers only on `pull_request` + `push:[main]` (no tag trigger), so this gotcha does not apply.
- **Governed edit outside the path filter (under-triggering)** → the real risk (a governed edit slips the gate); mitigated by including the AC-2 script + workflow file in the filter and erring broad (over-triggering is the safe direction).

---

## Requirements *(mandatory)*

> **AC Rule**: acceptance scenarios above follow Given/When/Then. `[MANUAL-ONLY] <reason>` marks behavior that cannot run headless in CI (AC-7/AC-12 full verification; bump-time empirical re-derivation).

### Functional Requirements

#### #281 — CI integration for the F-4 verification recipe (LEAD, P1)

- **FR-281.1** — A new workflow `.github/workflows/tachi-permissions-verify.yml` (job/name `tachi permissions-verify`) MUST run on `pull_request` **and** `push: [main]`, gated by a **single YAML-anchored `paths:` list** (F-250 lock-step rule — no second list that can drift) covering: `.claude/settings.json`, `docs/standards/CLAUDE_PERMISSIONS.md`, `.aod/scripts/bash/claude-permissions-ac2-crosscheck.sh`, and the workflow file itself.
- **FR-281.2** — The workflow MUST run `jq empty .claude/settings.json` and fail the job on non-zero exit (JSON-validity gate; F-4 FR-001).
- **FR-281.3** — The workflow MUST run `.aod/scripts/bash/claude-permissions-ac2-crosscheck.sh` (the delivered #280 script) and fail the job on **any** non-zero exit — exit **1** (orphaned rule/table-row) **and** exit **2** (invariant violation: missing files, jq parse error, empty section) both fail.
- **FR-281.4** — For AC-7 and AC-12 (interactive-only), the workflow MUST run a **doc-presence check** asserting `CLAUDE_PERMISSIONS.md` still contains the **`## 3. Settings precedence`** section (documents cross-file deny precedence / AC-12) and the **`## 4. Per-rule rationale table`** section (documents per-rule rationale + Category-4 subdomain / AC-7). A missing section fails the job; the grep MUST match the actual current heading text.
- **FR-281.5** — The workflow MUST declare least-privilege permissions (`contents: read` only; no `write` scopes — it emits no SARIF) and run on a single `ubuntu-latest` runner (checks are OS-independent string/JSON assertions).
- **FR-281.6** — The workflow MUST invoke the checks **directly** (`command -v`, `jq`, `bash <script>`, `grep`), NOT via any `/aod.*` slash command, mirroring the `tachi-catalog-drift.yml` / `tachi-pytest.yml` pattern. It MUST get its OWN workflow file and MUST NOT touch the pytest gate's `&hardening_paths` anchor.
- **FR-281.7** *(Architect C-2)* — The workflow MUST assert `jq` presence (`command -v jq`, or an explicit install step) **before** the `jq empty` gate, so a runner-image change that drops `jq` fails loudly rather than erroring ambiguously.
- **FR-281.8** *(Architect C-3)* — The workflow MUST use `actions/checkout@v4` with a working `.git` tree (default full checkout; NOT sparse/no-git/trimmed), because the reused AC-2 script resolves the repo root via `git rev-parse --show-toplevel`. The dependency MUST be stated in the workflow header comment so a future checkout tweak cannot silently repoint the root.

#### #285 — gitleaks rule-coverage probe (P3, split-valve)

- **FR-285.1** — Enumerate the active gitleaks default rule IDs (under `useDefault = true`, gitleaks v8.30.1) that fire for each canonical pattern: GitHub PAT (`ghp_*`), AWS access key (`AKIA*`), OpenAI key (`sk-*`), Anthropic key (`sk-ant-*`), PEM/private-key blocks, generic high-entropy strings. Rule IDs MUST be **empirically derived** (read from actual gitleaks hits), not transcribed — upstream gives no immutable-ID guarantee.
- **FR-285.2** — Verify coverage empirically by running gitleaks against a temp fixture set (one fixture per canonical pattern, mirroring the F-5 staged-credential fixtures) and mapping each hit to its rule ID.
- **FR-285.3** — Document the active-rule catalog in `PRECOMMIT_HOOKS.md §3 "What gets scanned"` (a concrete per-pattern → rule-ID table converting the existing `[MANUAL-ONLY]` note).
- **FR-285.4** — Any canonical pattern NOT covered by an active default rule MUST be flagged and filed as a separate `enhancement` issue (not silently accepted).
- **FR-285.5** *(Architect C-1 / A-4 — governs FR-285.2, FR-286.2, FR-287.1)* — Any empirical/CI/build context that runs the gitleaks fixture matrix or `gitleaks detect` MUST provision the gitleaks binary via the pinned-download + SHA256-verify stanza proven in `.github/workflows/gitleaks.yml` (v8.30.1, checksum `551f6fc83ea457d62a0d98237cbad105af8d557003051f41f3e7ca7b3f2470eb`) — gitleaks is NOT preinstalled on `ubuntu-latest`. An absent binary MUST **fail** the step, never skip.

#### #286 — adopter-extensibility template (P3, split-valve)

- **FR-286.1** — Author `.gitleaks.toml.adopter-template` (~80–120 LOC) with sectioned, commented examples for: (1) custom rules, (2) allow-list extension, (3) per-rule severity, (4) tool-swap to trufflehog / detect-secrets (per ADR-042 §Alternatives).
- **FR-286.2** — The template MUST load cleanly (`gitleaks detect --config=.gitleaks.toml.adopter-template` syntactic validity), verified as a build check (binary provisioned per FR-285.5).
- **FR-286.3** — Add a `PRECOMMIT_HOOKS.md §9 "Adopter customization"` subsection pointing to the template with usage instructions, plus a single-line cross-reference from `README.md`'s Security subsection (consistent with the F-5 pattern).

#### #287 — gitleaks pin-bump cadence accountability (P2)

- **FR-287.1** — Establish a single tracked surface documenting the pin-bump process: on each gitleaks minor release — update tag → `pre-commit autoupdate --freeze` → re-run the 16-fixture rule-interaction matrix (16/16 required) → `pre-commit run --all-files` (zero findings) → **re-derive the #285 per-pattern → rule-ID mapping** (catches upstream rule-ID renames the fire/no-fire matrix misses — Architect A-1) → update `ADR-042 §References` + `PRECOMMIT_HOOKS.md §Known-Limitations` on any guarantee change. Follows ADR-042 Decision Item 6 (minor→re-test-before-merge; patch→opportunistic on CVE; major→ADR re-eval).
- **FR-287.2** — The cadence surface MUST be the single source of truth referenced by future child bump issues (a canonical documented section and/or issue template that `chore(deps): bump gitleaks vX.Y.Z` issues reference).
- **FR-287.3** — *(Optional, split-valve)* A lightweight scheduled mechanism MAY detect new gitleaks releases and open the child issue automatically. If it exceeds chore size at `/aod.tasks`, it defers to a sibling issue rather than blocking #287's documentation deliverable.

### Non-Functional Requirements

- **NFR-1 (zero-cost-when-idle)** — Both CI additions (#281 workflow; any #287 scheduled job) MUST be `paths:`-filtered or schedule-only so they impose no cost on unrelated commits.
- **NFR-2 (determinism)** — The #281 CI checks MUST be deterministic and environment-independent (JSON parse + string cross-check + section-presence grep); no network, sub-second, cannot false-red on runner variance.
- **NFR-3 (least privilege)** — All new workflows declare `contents: read` only (no `security-events: write` — these checks emit no SARIF).
- **NFR-4 (reuse over rebuild)** — #281 MUST reuse the delivered `claude-permissions-ac2-crosscheck.sh` and existing repo CI conventions (YAML-anchored `paths:`, dual-trigger, pinned tool installs) rather than introduce new machinery (code-economy rung 2).
- **NFR-5 (bash 3.2 / macOS compatibility)** — Any new shell logic MUST stay bash-3.2 compatible (no `mapfile`, no associative arrays, no `&>`), consistent with `precommit-wrap.sh` / `common.sh`, so local re-runs match CI.

### Key Artifacts

| Issue | New / Modified | Path | Nature |
|---|---|---|---|
| #281 | **new** | `.github/workflows/tachi-permissions-verify.yml` | CI workflow (clone of `tachi-catalog-drift.yml`) |
| #281 | reused | `.aod/scripts/bash/claude-permissions-ac2-crosscheck.sh` | delivered #280 script (invoked, not edited) |
| #285 | modified | `docs/standards/PRECOMMIT_HOOKS.md` §3 | per-pattern → rule-ID catalog |
| #286 | **new** | `.gitleaks.toml.adopter-template` | ~80–120 LOC commented starter |
| #286 | modified | `docs/standards/PRECOMMIT_HOOKS.md` §9 + `README.md` | template pointer + cross-ref |
| #287 | modified/new | cadence surface (`PRECOMMIT_HOOKS.md` §Known-Limitations + `ADR-042 §References` + optional issue template) | pin-bump process SoT |

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-1** — `main` cannot silently accept a permissions-surface regression (broken JSON, orphaned rule/table-row): `tachi permissions-verify` reddens on both a PR and a direct `push:[main]`, verified by a failure-injection test. *(closes F-4 AC-16)*
- **SC-2** — A SecOps reviewer can audit tachi's gitleaks coverage from `PRECOMMIT_HOOKS.md` alone (every canonical pattern maps to an empirically-confirmed rule ID; uncovered patterns have filed issues). *(closes #285 / AC-18)*
- **SC-3** — Adopter time-to-first-custom-rule drops from ~1h to ~5min via a config-valid, sectioned template referenced from `PRECOMMIT_HOOKS.md §9` and `README.md`. *(closes #286 / AC-19)*
- **SC-4** — The gitleaks pin has a single tracked, re-testable bump recipe (tag → freeze → 16-fixture re-test → rule-ID re-derivation → doc updates) referenceable by child bump issues; it cannot silently rot. *(closes #287 / CONCERN-4)*
- **SC-5** — Zero new CI cost on unrelated commits (path-filtered / schedule-only): a PR touching no governed path does not run the workflow.

---

## Scope Boundaries & Split-Valve

### In scope (bundle of 4, lead #281)

#281 (CI workflow), #285 (coverage catalog), #286 (adopter template), #287 (pin-bump cadence). **#281 + #287 are the committed, load-bearing hardening core** (SC-1 / SC-4) and ship regardless of the split decision.

### Split-valve (decided mechanically at `/aod.tasks`, both reviewers — NOT here)

Carve **#285/#286 into a separate `F-5-enhancements` feature** if, at `/aod.tasks`, either: #285 requires a **committed** fixture harness (not a throwaway tmpdir run), OR #286 exceeds ~120 LOC / grows its own test surface. The **3.0 eng-day ceiling is the numeric trip-wire**. Both reviewers lean toward carving out (the #285 empirical step already reuses the committed `run.sh` + fixtures). The enhancements MUST NOT block the #281 + #287 core.

**Sequencing** (Team-Lead C-1): author **#285 before or with #287** — #287's bump recipe re-derives the rule-ID set #285 maps. #281 lands first regardless (cheapest, highest-value SC-1).

### Out of scope

- **NG1** — Re-authoring the delivered #280 pre-commit hooks (#281 *reuses* the AC-2 script in CI).
- **NG2** — Making AC-7 / AC-12 fully machine-executable in CI; they degrade to a doc-presence check and stay `[MANUAL-ONLY]` for full behavioral verification at `/aod.build`.
- **NG3 / OQ-1** — The AC-7 ANOMALY subdomain compaction (removing ~6 github-family `WebFetch` rules) — a `settings.json` *content* change coupled to the AC-2 table, orthogonal to CI integration → **sibling issue**, not this bundle.
- **NG4 / OQ-2** — Changing the gitleaks scan scope, pin version, or ruleset; and the #287 scheduled release-detector (FR-287.3) is optional/split-valve, not a core deliverable.
- **NG5** — Any new threat-scanner capability (this is maintenance, per BLP-06's subtractive thesis).
- **Repo-wide `actions/checkout` SHA-pinning** — web best-practice favors SHA-pins over `@v4` tags, but migrating all 7 workflows is a separate supply-chain decision; #281 matches the existing `@v4` convention for consistency + reuse.

---

## Dependencies

- **Delivered #280** (PR #290) — #281 reuses `claude-permissions-ac2-crosscheck.sh`. Hard dependency, satisfied on `main`.
- **F-4 #277** — `CLAUDE_PERMISSIONS.md` §3/§4 structure (doc-presence target). Satisfied.
- **F-5 #282** — `.gitleaks.toml`, `PRECOMMIT_HOOKS.md`, `tests/fixtures/gitleaks-rule-interaction/`, `ADR-042`. Satisfied.
- **`gitleaks.yml` provisioning stanza** — the pinned-download + SHA256 pattern #285/#286/#287 reuse (v8.30.1, `551f6fc8…`). Satisfied.
- No cross-dependency on Wave-1 (#333) or the delivered Wave-2 leads (#329/#338) — fully interleavable.

## Assumptions

1. **`actions/checkout@v4` (tag) is the repo convention** and is retained for consistency; a repo-wide SHA-pin migration is deferred (out of scope).
2. **`ubuntu-latest` ships `jq`, `awk`, `grep`, `sed`, `diff`** today; FR-281.7 guards the one (`jq`) that the AC-2 script hard-depends on, so an image change fails loud.
3. **`gitleaks` is NOT preinstalled** on `ubuntu-latest` → every gitleaks-touching step provisions it via the SHA256-verified download (FR-285.5).
4. **The baseline is green today** (93 rules ↔ 93 §4 rows byte-exact; `jq empty` rc=0) — the #281 workflow is expected to pass on clean `main` from first run (US-1 scenario 4).
5. **The split decision is deferred to `/aod.tasks`** per the PRD §8 mechanical trigger; this spec keeps all four issues in scope.
