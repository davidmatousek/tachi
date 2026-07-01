---
prd:
  number: 281
  topic: ci-governance-hardening-tail
  created: 2026-06-30
  status: Delivered
  type: feature
triad:
  pm_signoff:
    agent: product-manager
    date: 2026-06-30
    status: APPROVED
    notes: "Authored via /aod.define as PM draft (Feature workflow). Bundle scope + split-valve traced to _internal/strategy/BLP-06 Wave 2 F-2."
  architect_signoff:
    agent: architect
    date: 2026-06-30
    status: APPROVED_WITH_CONCERNS
    notes: "Core design sound (reuse of delivered AC-2 script, catalog-drift CI pattern, dual-trigger, doc-presence degradation for AC-7/AC-12, contents:read) — all verified vs live repo. 0 blocking. C-1 (gitleaks-binary provisioning), C-2 (jq-guard FR), C-3 (checkout dependency) folded into FR-281.7/FR-281.8/FR-285.5; A-1 into FR-287.1. See .aod/results/architect-281.md."
  techlead_signoff:
    agent: team-lead
    date: 2026-06-30
    status: APPROVED_WITH_CONCERNS
    notes: "FEASIBLE, no timeline/capacity veto. Estimate 2.0d central / 1.0 floor / 3.0 ceiling (high confidence). Bundle-of-4 endorsed; split deferred to /aod.tasks (§8). C-1 sequencing (#285 before #287) folded into §8. See .aod/results/team-lead-281.md."
source:
  idea_id: 281        # equals prd.number (GitHub Issue #281)
  story_id: null
bundle:
  lead: 281
  members: [281, 285, 286, 287]
  split_valve_candidates: [285, 286]
  note: "#280 (the fifth original tail item) was pre-delivered 2026-05-11 via PR #290 and is NOT part of this bundle."
---

# PRD-281 — CI & Governance Hardening Tail (F-4/F-5 follow-ups)

> **Bundle PRD.** Lead issue **#281**; bundles **#285**, **#286**, **#287**. This is the Wave-2 hygiene-tail feature of BLP-06 (`_internal/strategy/BLP-06-integrity-and-hardening.md` §F-2), following the delivered Wave-2 lead #329 and the #338 restore. The fifth original tail item, **#280, was already delivered** (PR #290, 2026-05-11) and is excluded. Per the BLP-06 split-valve rule, the two `enhancement` items (**#285/#286**) may be carved into their own feature at `/aod.plan` if they exceed chore size.

---

## 1. Problem Statement

Features **F-4** (Claude permissions baseline, #277) and **F-5** (pre-commit secret-scanning defaults, #282) each shipped with a small tail of deferred nice-to-haves and recurring-maintenance obligations, logged as backlog issues at `/aod.deliver` time. Those obligations currently rely on **manual discipline** rather than **mechanized enforcement**, so three governance gaps persist:

1. **F-4's deterministic verification recipe runs only locally.** The JSON-validity (`jq empty .claude/settings.json`) and AC-2 cross-check (every non-built-in rule in `settings.json` is documented in `CLAUDE_PERMISSIONS.md` §4, and vice-versa) now run as **local pre-commit hooks** (delivered under #280, PR #290). But a contributor who commits with `--no-verify`, whose hook is uninstalled, or who edits the permissions surface via the GitHub web UI **bypasses those checks entirely**. There is no CI back-stop — the same gap the F-5 `gitleaks.yml` CI-parity workflow was built to close for secret-scanning. F-4's own **AC-16** named this and deferred it.

2. **F-5's gitleaks rule coverage is implicit, not documented.** `.gitleaks.toml` extends `useDefault = true`, inheriting the upstream gitleaks default ruleset. The F-5 build verified false-positive avoidance and pass-through of canonical credential patterns via fixtures, but **never enumerated which default rule IDs are actually active** for the canonical patterns tachi adopters risk committing (`ghp_*`, `AKIA*`, `sk-*`, `sk-ant-*`, PEM blocks, high-entropy strings). Adopters and maintainers cannot audit coverage without reading the upstream ruleset cold (**#285 / spec AC-18**).

3. **F-5's gitleaks pin has no cadence accountability.** `.pre-commit-config.yaml` and `gitleaks.yml` pin gitleaks `v8.30.1`. ADR-042 §Consequences documents a bump-on-each-minor-release-with-fixture-re-test policy, but **without a tracked surface the policy is folklore** — the pin silently rots and adopters inherit an aging secret-scanner (**#287 / CONCERN-4**). Separately, adopters wanting to extend the ruleset must derive safe customization paths by reading `.gitleaks.toml` cold — there is no starter template (**#286 / spec AC-19**).

None of these add product capability. All of them make the **already-shipped** F-4/F-5 surface more *defensible* (CI-enforced), more *auditable* (documented coverage), and more *maintainable* (tracked cadence, extensibility template) — the maintenance-side of the same OSS-hardening thesis.

---

## 2. Goals & Non-Goals

### Goals

- **G1 (#281)** — Port F-4's deterministic verification recipe into CI so the permissions surface is enforced on PRs (and direct `push:[main]`), not just on local pre-commit.
- **G2 (#285)** — Enumerate and document the active gitleaks default-rule coverage for tachi's canonical credential patterns, converting the `[MANUAL-ONLY]` cross-check into a documented, machine-verifiable catalog.
- **G3 (#286)** — Ship an adopter-extensibility starter template (`.gitleaks.toml.adopter-template`) that lowers time-to-first-custom-rule from ~1h to ~5min.
- **G4 (#287)** — Give the gitleaks pin-bump cadence a tracked, single-source-of-truth surface so the pin cannot silently rot.

### Non-Goals

- **NG1** — Re-implementing or replacing the delivered #280 local pre-commit hooks. #281 *reuses* the existing `.aod/scripts/bash/claude-permissions-ac2-crosscheck.sh` in a CI context; it does not re-author it.
- **NG2** — Making AC-7 (WebFetch subdomain probe) or AC-12 (cross-file deny precedence) fully machine-executable in CI. Both require an **interactive Claude Code session**; in CI they degrade to a **documentation-presence check** (the relevant `CLAUDE_PERMISSIONS.md` sections exist), and remain `[MANUAL-ONLY]` for full execution at `/aod.build` time.
- **NG3** — The **AC-7 ANOMALY subdomain compaction** (removing the ~6 github-family `WebFetch` rules subsumed by the parent `WebFetch(domain:github.com)` rule via transitive collapse). This is a `settings.json` *content* change that interacts with the AC-2 cross-check, orthogonal to "run the F-4 checks in CI." Recommended as a **sibling issue** (see OQ-1), not folded here.
- **NG4** — Changing the gitleaks scan scope, pin version, or ruleset in *this* feature. #287 documents the *cadence*; it does not perform a bump.
- **NG5** — Any new threat-scanner capability. This is maintenance, per BLP-06's subtractive thesis.

---

## 3. User Stories

- **US-1 (maintainer, #281)** — *As a tachi maintainer,* I want the permissions surface (`.claude/settings.json` + `CLAUDE_PERMISSIONS.md`) validated in CI on every PR that touches it, *so that* a `--no-verify` commit or a web-UI edit that breaks JSON validity or orphans a rule/table-row reddens the build instead of silently landing on `main`.
- **US-2 (SecOps auditor, #285)** — *As a SecOps reviewer auditing tachi's secret-scanning posture,* I want a documented catalog of which gitleaks default rules cover each canonical credential pattern, *so that* I can produce a coverage audit without reverse-engineering the upstream ruleset.
- **US-3 (adopter, #286)** — *As an adopter extending tachi's secret-scanning,* I want a commented starter template for custom rules, allow-lists, severity, and tool-swap, *so that* I can add my first industry-specific credential pattern in minutes instead of an hour.
- **US-4 (maintainer, #287)** — *As a tachi maintainer,* I want a single tracked surface defining the gitleaks pin-bump process, *so that* each upstream minor release has an unambiguous, re-testable bump recipe and the pin does not silently age.

---

## 4. Functional Requirements

### #281 — CI integration for the F-4 verification recipe (LEAD)

- **FR-281.1** — A new GitHub Actions workflow (`.github/workflows/tachi-permissions-verify.yml`) MUST run on `pull_request` **and** `push: [main]`, gated by a `paths:` filter (a single YAML-anchored list per the F-250 lock-step rule) covering: `.claude/settings.json`, `docs/standards/CLAUDE_PERMISSIONS.md`, `.aod/scripts/bash/claude-permissions-ac2-crosscheck.sh`, and the workflow file itself. Day-to-day commits that touch none of these pay zero CI cost.
- **FR-281.2** — The workflow MUST run `jq empty .claude/settings.json` and fail the job on non-zero exit (JSON-validity gate; F-4 FR-001).
- **FR-281.3** — The workflow MUST run `.aod/scripts/bash/claude-permissions-ac2-crosscheck.sh` (the delivered #280 script) and fail the job on non-zero exit (AC-2 cross-check; F-4 FR-002 — zero orphaned rules, zero orphaned table rows).
- **FR-281.4** — For AC-7 and AC-12 (interactive-only), the workflow MUST run a **documentation-presence check**: assert that `CLAUDE_PERMISSIONS.md` still contains the §3 (cross-file deny precedence) and §4 (per-rule rationale / Category-4 subdomain) sections that document those behaviors. A missing section fails the job; full behavioral verification stays `[MANUAL-ONLY]` at `/aod.build` (F-4 AC-6).
- **FR-281.5** — The workflow MUST declare least-privilege permissions (`contents: read`; no `write` scopes) and run on a single `ubuntu-latest` runner (the checks are OS-independent string/JSON assertions).
- **FR-281.6** — The workflow MUST invoke the checks **directly** (`jq`, `bash <script>`, `grep`), NOT via any `/aod.*` slash command (slash commands cannot run in CI), mirroring the `tachi-catalog-drift.yml` / `tachi-pytest.yml` repo pattern.
- **FR-281.7** *(Architect C-2)* — The workflow MUST assert `jq` presence (`command -v jq`, or an explicit install step) **before** the `jq empty` gate, so a runner-image change that drops `jq` fails loudly rather than erroring ambiguously. A governance gate must not silently stop governing on runner drift.
- **FR-281.8** *(Architect C-3)* — The workflow MUST use `actions/checkout@v4` with a working `.git` tree (default full checkout; NOT a sparse / no-git / trimmed checkout), because the reused AC-2 script resolves the repo root via `git rev-parse --show-toplevel`. The dependency degrades closed today but MUST be stated so a future checkout tweak cannot silently repoint the root.

### #285 — gitleaks rule-coverage probe

- **FR-285.1** — Enumerate the active gitleaks default rule IDs (under `.gitleaks.toml` `useDefault = true`, gitleaks v8.30.1) that fire for each canonical pattern: GitHub PAT (`ghp_*`), AWS access key (`AKIA*`), OpenAI key (`sk-*`), Anthropic key (`sk-ant-*`), PEM/private-key blocks, generic high-entropy strings.
- **FR-285.2** — Verify coverage empirically by running gitleaks against a temp fixture set (one fixture per canonical pattern, mirroring the F-5 staged-credential fixtures) and mapping each hit to its rule ID.
- **FR-285.3** — Document the active-rule catalog in `docs/standards/PRECOMMIT_HOOKS.md` §3 "What gets scanned" → §"Per-rule rationale catalog" (converting the existing `[MANUAL-ONLY]` note into a concrete per-pattern → rule-ID table).
- **FR-285.4** — Any canonical pattern NOT covered by an active default rule MUST be flagged and filed as a separate `enhancement` issue (not silently accepted).
- **FR-285.5** *(Architect C-1 / A-4 — governs FR-285.2, FR-286.2, FR-287.1)* — Any empirical, CI, or build context that runs the gitleaks fixture matrix (`tests/fixtures/gitleaks-rule-interaction/run.sh`) or `gitleaks detect` MUST provision the gitleaks binary via the pinned-download + SHA256-verify stanza already proven in `.github/workflows/gitleaks.yml` (v8.30.1, checksum `551f6fc8…`) — gitleaks is NOT preinstalled on `ubuntu-latest`. An absent binary MUST **fail** the step, never skip: a silent-green on an unrun probe would hollow SC-2 and reintroduce, one level up, the exact anti-pattern this feature exists to kill.

### #286 — adopter-extensibility template

- **FR-286.1** — Author `.gitleaks.toml.adopter-template` (~80–120 LOC) with sectioned, commented examples for: (1) custom rules, (2) allow-list extension, (3) per-rule severity, (4) tool-swap to trufflehog / detect-secrets (per ADR-042 §Alternatives).
- **FR-286.2** — The template MUST load cleanly (`gitleaks detect --config=.gitleaks.toml.adopter-template …` syntactic validity), verified as a build check.
- **FR-286.3** — Add a §9 "Adopter customization" → §"Adopter-Customization-Template" subsection to `PRECOMMIT_HOOKS.md` pointing to the template with usage instructions, and a single-line cross-reference from `README.md`'s Security subsection (consistent with the F-5 pattern).

### #287 — gitleaks pin-bump cadence accountability

- **FR-287.1** — Establish a single tracked surface documenting the pin-bump process: on each gitleaks minor release, a child issue updates the tag → `pre-commit autoupdate --freeze` → re-runs the 16-fixture rule-interaction matrix (`tests/fixtures/gitleaks-rule-interaction/run.sh`, 16/16 required) → runs `pre-commit run --all-files` (zero findings) → **re-derives the #285 per-pattern → rule-ID mapping** to catch upstream rule-ID renames *(Architect A-1: a rename keeps `run.sh` green while silently staling #285's catalog — the fire/no-fire matrix alone only half-mitigates R-2)* → updates ADR-042 §References + `PRECOMMIT_HOOKS.md` §Known-Limitations on any guarantee change.
- **FR-287.2** — The cadence surface MUST be the single source of truth referenced by future child bump issues (a canonical body/checklist, e.g., an issue template or a documented section future `chore(deps): bump gitleaks vX.Y.Z` issues reference).
- **FR-287.3** — *(Optional, split-valve)* A lightweight scheduled mechanism MAY detect new gitleaks releases (e.g., a scheduled workflow querying `repos/gitleaks/gitleaks/releases/latest`) and open the child issue automatically. If it exceeds chore size, it defers to a sibling issue rather than blocking #287's documentation deliverable.

---

## 5. Non-Functional Requirements

- **NFR-1 (zero-cost-when-idle)** — Both CI additions (#281 workflow; any #287 scheduled job) MUST be `paths:`-filtered or schedule-only so they impose no cost on unrelated commits.
- **NFR-2 (determinism)** — The #281 CI checks MUST be deterministic and environment-independent (JSON parse + string cross-check + section-presence grep); no network, no rendering, sub-second — cannot false-red on runner variance.
- **NFR-3 (least privilege)** — All new workflows declare `contents: read` only (no `security-events: write` needed — these checks emit no SARIF, unlike `gitleaks.yml`).
- **NFR-4 (reuse over rebuild)** — #281 MUST reuse the delivered `claude-permissions-ac2-crosscheck.sh` and the existing repo CI conventions (YAML-anchored `paths:`, dual-trigger, pinned tool installs) rather than introduce new machinery (code-economy rung 2).
- **NFR-5 (bash 3.2 / macOS compatibility)** — Any new shell logic MUST stay bash-3.2 compatible (no `mapfile`, no associative arrays, no `&>`), consistent with the existing `precommit-wrap.sh` / `common.sh` precedent, so local re-runs match CI.

---

## 6. Acceptance Criteria

- **AC-1 (#281)** — Given a PR that introduces a JSON syntax error into `.claude/settings.json`, When CI runs, Then `tachi-permissions-verify` fails at the `jq empty` step. Given a PR that adds a rule to `settings.json` without a matching `CLAUDE_PERMISSIONS.md` §4 row (or vice-versa), Then it fails at the AC-2 cross-check step. Given a PR touching neither governed file, Then the workflow does not run (path filter).
- **AC-2 (#281)** — Given the current (clean) `main`, When the workflow runs, Then all steps pass (rc=0): `jq empty` green, AC-2 cross-check green, §3/§4 doc-presence green. *(Baseline-green pre-state confirmed 2026-06-30: both checks already exit 0.)*
- **AC-3 (#281)** — Given a direct `push` to `main` touching the permissions surface (bypassing PRs), When it lands, Then the `push:[main]` trigger runs the same gate (closing the direct-to-main bypass, per the #338/#329 precedent).
- **AC-4 (#285)** — Given the documented per-pattern → rule-ID catalog in `PRECOMMIT_HOOKS.md`, When a reviewer checks any canonical pattern, Then the active gitleaks rule ID is listed and empirically confirmed by a fixture hit; any uncovered pattern has a filed follow-up issue.
- **AC-5 (#286)** — Given `.gitleaks.toml.adopter-template`, When `gitleaks detect --config=.gitleaks.toml.adopter-template` runs, Then it loads without a config error; and `PRECOMMIT_HOOKS.md` §9 + `README.md` reference it.
- **AC-6 (#287)** — Given the pin-bump cadence surface, When a maintainer needs to bump gitleaks, Then a single canonical process (tag → freeze → 16-fixture re-test → doc updates) is documented and referenceable by child bump issues.
- **AC-7 (bundle)** — Given the delivered feature, When `/aod.deliver` runs, Then it ships as a single `feat(281):` (or `fix:`) PR with a release-please release; any split-off (#285/#286) is tracked as its own issue with its own delivery.

---

## 7. Success Criteria

- **SC-1** — `main` cannot silently accept a permissions-surface regression (broken JSON, orphaned rule/table-row) — CI reddens on both PR and direct push. *(closes F-4 AC-16)*
- **SC-2** — A SecOps reviewer can audit tachi's gitleaks coverage from `PRECOMMIT_HOOKS.md` alone. *(closes #285 / AC-18)*
- **SC-3** — Adopter time-to-first-custom-rule drops from ~1h to ~5min via the template. *(closes #286 / AC-19)*
- **SC-4** — The gitleaks pin has a tracked, re-testable bump recipe; it cannot silently rot. *(closes #287 / CONCERN-4)*
- **SC-5** — Zero new CI cost on unrelated commits (path-filtered / schedule-only).

---

## 8. Bundle & Split-Valve Strategy

This PRD scopes **four** issues behind lead **#281**. The bundle is coherent along the "CI & governance hardening of the F-4/F-5 pre-commit/permissions surface" axis, but spans two sub-surfaces:

| Sub-surface | Issues | Nature | Risk |
|---|---|---|---|
| F-4 permissions CI | **#281** (lead) | CI workflow — reuses delivered #280 script | Low (config + reuse) |
| F-5 gitleaks governance | **#287** | Documentation / process + optional schedule | Low (docs) |
| F-5 gitleaks enhancements | **#285**, **#286** | Probe + template + docs | **Split candidates** |

**Split valve (decided mechanically at `/aod.tasks`, not `/aod.plan` — both reviewers):** the carve trigger is *empirical* and only observable after task decomposition. Carve **#285/#286 into a separate `F-5-enhancements` feature** if, at `/aod.tasks`, either: #285 requires a **committed** fixture harness (not a throwaway tmpdir run), OR #286 exceeds ~120 LOC / grows its own test surface. The **ceiling estimate (3.0 eng-days) is the numeric trip-wire** — if reality trends there, carve. The two enhancement items are `enhancement`-labeled and P3; #281 (lead) + #287 (P2) are the load-bearing hardening core (SC-1 / SC-4) and MUST NOT be blocked by the enhancements. Both reviewers lean **toward carving out** (Architect A-3: #285's empirical step *already* reuses the committed `run.sh`+fixtures the trigger names; Team-Lead: keep bundled through `/aod.plan`, decide at `/aod.tasks`).

**Sequencing note (Team-Lead C-1):** author **#285 before or with #287** — #287's bump recipe re-runs the same 16-fixture matrix and must preserve the rule-ID set #285 maps (FR-287.1 re-derivation depends on FR-285.1's method). #281 lands first regardless (cheapest, highest-value SC-1).

---

## 9. Timeline & Milestones

> Sized 1:1 to the Team-Lead estimate in `specs/281-ci-governance-hardening-tail/feasibility-check.md`: **planning 2.0 eng-days** (central, all four in-scope) · **floor 1.0** (#285/#286 split out — #281 + #287 only) · **ceiling 3.0** (#285/#286 stay in and balloon → the §8 carve trip-wire). Confidence: **high** (every dependency pre-satisfied on `main`; lead item clones #329).

| Phase | Scope | Sizing |
|---|---|---|
| P1 — Permissions CI (#281, lead) | Clone `tachi-catalog-drift.yml`; swap gates to `jq empty` + AC-2 script + §3/§4 grep; failure-injection smoke test | **0.5 d** |
| P2 — gitleaks cadence (#287) | Formalize the in-comment pin policy into a canonical referenceable surface; ADR-042 wiring; catalog re-derivation step | **0.5 d** |
| P3 — gitleaks enhancements (#285/#286) | Coverage probe + per-pattern→rule-ID catalog · adopter template + docs — **OR carved out at `/aod.tasks`** | **1.0 d** (split candidate) |
| **Dev Complete** | All in-scope ACs green; split decision recorded at `/aod.tasks` | **= 2.0 d planning** (1.0 floor if carved / 3.0 ceiling if balloons) |

---

## 10. Dependencies

- **Delivered #280** (PR #290) — #281 reuses `.aod/scripts/bash/claude-permissions-ac2-crosscheck.sh`. Hard dependency, already satisfied on `main`.
- **F-4 #277** — `CLAUDE_PERMISSIONS.md` §3/§4 structure (the doc-presence check target). Satisfied.
- **F-5 #282** — `.gitleaks.toml`, `PRECOMMIT_HOOKS.md`, `tests/fixtures/gitleaks-rule-interaction/`, ADR-042. Satisfied.
- **No cross-dependency on Wave-1 (#333) or the delivered Wave-2 leads (#329/#338).** Fully interleavable.

---

## 11. Risks & Open Questions

### Risks

- **R-1 (over/under-triggering path filter, #281)** — Too-narrow `paths:` misses a governed edit; too-broad re-runs harmlessly. Mitigation: include the AC-2 script + workflow file in the filter (a script change can alter cross-check behavior), erring broad — the `tachi-catalog-drift.yml` precedent (under-triggering is the only real risk).
- **R-2 (gitleaks default-rule drift, #285)** — The documented catalog is pinned to v8.30.1; an upstream bump can rename/shift rule IDs, staling the catalog. Mitigation: #287's cadence explicitly re-tests and updates on each bump — the two items reinforce each other.
- **R-3 (scope creep in #285/#286)** — "Probe" becomes a fixture framework; "template" becomes a config DSL. Mitigation: the §8 split valve; bound each to its issue's ACs at `/aod.plan`.
- **R-4 (jq availability in CI)** — `jq` is preinstalled on `ubuntu-latest`, but a runner-image change could remove it. Mitigation: a one-line `apt-get install -y jq` guard or `which jq` assertion in the workflow.

### Open Questions

- **OQ-1 (AC-7 ANOMALY compaction)** — Should the ~6 redundant github-family `WebFetch` rules (subsumed by parent `github.com` via the confirmed transitive collapse) be compacted? **Recommendation: file as a sibling issue, NOT in this bundle** — it is a `settings.json` content change coupled to the AC-2 table, orthogonal to CI integration (NG3). Decide at `/aod.plan`.
- **OQ-2 (#287 mechanism)** — Documented-process-only, or documented-process + scheduled release-detector workflow? **Recommendation: ship documentation first (FR-287.1/.2); treat the scheduled detector (FR-287.3) as split-valve** — a `tachi-citation-linkrot.yml`-style scheduled monitor is a proven pattern but is separable.
- **OQ-3 (split decision timing)** — Confirm #285/#286 carve-in vs. carve-out at **`/aod.tasks`** (after task decomposition surfaces whether the committed-fixture-harness / >120-LOC triggers fire), per §8. Keep bundled through `/aod.plan`.

---

## 12. References

- Lead issue: [#281](https://github.com/davidmatousek/tachi/issues/281) — CI integration for F-4 verification recipe
- Bundled: [#285](https://github.com/davidmatousek/tachi/issues/285) (AC-18 probe), [#286](https://github.com/davidmatousek/tachi/issues/286) (AC-19 template), [#287](https://github.com/davidmatousek/tachi/issues/287) (gitleaks cadence)
- Pre-delivered (excluded): #280 (PR #290, 2026-05-11)
- F-4 spec: `specs/277-claude-permissions-baseline/spec.md` (FR-001/FR-002/AC-6/AC-16); `docs/standards/CLAUDE_PERMISSIONS.md`; ADR-041
- F-5 spec: `specs/282-pre-commit-secret-scanning-defaults/spec.md` (AC-18/AC-19/CONCERN-4); `docs/standards/PRECOMMIT_HOOKS.md`; ADR-042
- CI pattern precedent: `.github/workflows/tachi-catalog-drift.yml` (#329), `.github/workflows/gitleaks.yml` (#282 CI-parity), `.github/workflows/tachi-pytest.yml` (dual-trigger anchor)
- Strategy: `_internal/strategy/BLP-06-integrity-and-hardening.md` §F-2 (Wave 2)
