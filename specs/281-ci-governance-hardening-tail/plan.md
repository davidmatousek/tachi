---
triad:
  pm_signoff:
    agent: product-manager
    date: 2026-07-01
    status: APPROVED
    notes: "Faithful, complete how-to-build of the PM-approved spec; zero scope creep. All 24 requirements (19 FR + 5 NFR) trace 1:1 to phases P1/P2/P3; split-valve preserved in all four elements (4-in-scope, carve-at-/aod.tasks, #281+#287 committed core, 3.0-d trip-wire, #285-before-#287 sequencing); priorities/sizing match the 2.0-d feasibility estimate; every out-of-scope decision honored. No must-fix items. Details: .aod/results/product-manager-plan-281.md"
  architect_signoff:
    agent: architect
    date: 2026-07-01
    status: APPROVED
    notes: "All load-bearing claims verified against live main. tachi-permissions-verify.yml sketch structurally identical to the tachi-catalog-drift.yml clone target on all six axes; correctly omits security-events:write (no SARIF) and does NOT touch the pytest &hardening_paths anchor. Fail-closed sound (AC-2 any-non-zero reddens, jq-guard precedes jq empty, doc-greps match byte-exact live headings, sparse-checkout exits 2). gitleaks provisioning (v8.30.1, 551f6fc8…) fail-never-skip; no-new-ADR + Phase-1-N/A justified; baseline green live (93↔93, AC-2 exit 0). 2 advisory notes only (main-leg over-trigger intended; §8/§9 authoring-precision reminder for build). Details: .aod/results/architect-plan-281.md"
  techlead_signoff: null  # Added by /aod.tasks
---

# Implementation Plan: CI & Governance Hardening Tail (F-4/F-5 follow-ups)

**Branch**: `281-ci-governance-hardening-tail` | **Date**: 2026-07-01 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `specs/281-ci-governance-hardening-tail/spec.md` (PM APPROVED_WITH_CONCERNS)

## Summary

Port the already-delivered F-4/F-5 **local** pre-commit checks into **CI-enforced / auditable / maintainable** surfaces. Four deliverables behind lead **#281**:

1. **#281 (P1)** — a new GitHub Actions workflow `tachi-permissions-verify.yml` that runs the F-4 verification recipe (`jq empty` + the delivered #280 AC-2 cross-check script + a §3/§4 doc-presence grep) on `pull_request` + `push:[main]`, gated by a single YAML-anchored `paths:` filter. **Near-1:1 clone of `tachi-catalog-drift.yml`**; reuses `claude-permissions-ac2-crosscheck.sh` verbatim.
2. **#287 (P2)** — promote the in-comment gitleaks pin-bump folklore into a single canonical, referenceable cadence surface (bump recipe + rule-ID re-derivation) grounded in ADR-042 Decision Item 6.
3. **#285 (P3, split-valve)** — empirically derive and document the active gitleaks default-rule → canonical-pattern catalog in `PRECOMMIT_HOOKS.md §3`.
4. **#286 (P3, split-valve)** — ship a `.gitleaks.toml.adopter-template` (~80–120 LOC, 4 commented sections) + doc pointers.

**Technical approach**: reuse over rebuild (code-economy rung 2 / NFR-4). Every net-new artifact clones an existing, delivered repo pattern — no new machinery, no new dependency, no new ADR.

## Technical Context

**Language/Version**: GitHub Actions workflow YAML; Bash **3.2**-compatible shell (no `mapfile`, no associative arrays, no `&>` — NFR-5); `jq` (JSON); `grep`/`awk`/`sed`/`diff` (POSIX text).
**Primary Dependencies**: reused `.aod/scripts/bash/claude-permissions-ac2-crosscheck.sh` (#280, delivered); `gitleaks` **v8.30.1** single binary (SHA256 `551f6fc83ea457d62a0d98237cbad105af8d557003051f41f3e7ca7b3f2470eb`, provisioned by pinned download — NOT preinstalled on `ubuntu-latest`); `actions/checkout@v4`. No new package-manifest dependency.
**Storage**: N/A (config/text files under version control; no datastore).
**Testing**: (a) #281 failure-injection smoke — run each check command against a deliberately-broken *temp copy* and assert non-zero; (b) #285/#286 empirical — the committed 16-fixture `tests/fixtures/gitleaks-rule-interaction/run.sh` matrix (16/16) + per-pattern temp fixtures; (c) #286 `gitleaks detect --config=` config-validity.
**Target Platform**: `ubuntu-latest` CI runner (checks are OS-independent) + local macOS pre-commit parity (bash 3.2).
**Project Type**: single (infra / tooling / docs — no application source, no UI, no API).
**Performance Goals**: #281 CI job sub-second, deterministic, no network (NFR-2).
**Constraints**: zero-cost-when-idle (path-filtered / schedule-only — NFR-1); least-privilege `contents: read` only (NFR-3); fail-closed everywhere (missing/partial/unparseable input reddens, never skips).
**Scale/Scope**: repo-level governance gate; 1 new workflow, 1 new template file, 3 doc surfaces, 0 new scripts.

## Constitution Check

*GATE: evaluated pre-design and re-confirmed post-design. Tier: standard.*

| Principle | Verdict | Evidence |
|---|---|---|
| I. General-Purpose Architecture | ✅ PASS | No new domain logic; governs tachi's own repo hygiene. Template ships adopter-generic extensibility (#286). |
| II. API-First | ✅ N/A | No API surface — CI workflow + docs. |
| Code-Economy (reuse ladder) | ✅ PASS (exemplary) | Rung 2 satisfied: #281 clones `tachi-catalog-drift.yml` + reuses the delivered #280 script; #285/#286/#287 reuse the `gitleaks.yml` provisioning stanza + committed 16-fixture harness. Zero net-new machinery. |
| Security (least-privilege / fail-closed / supply-chain) | ✅ PASS | `contents: read` only (no SARIF → no `security-events: write`); SHA256-verified gitleaks download; jq-presence guard; full-checkout dependency stated; any non-zero exit fails. |
| Design-Quality (WCAG/UI) | ✅ N/A | No UI. |
| Local-First | ✅ PASS | Checks run identically as local pre-commit (delivered) and in CI (this feature); CI is a *back-stop*, not a replacement. |
| Product-Spec Alignment (Principle VIII) | ✅ PASS | plan traces 1:1 to spec FRs; split-valve preserved; no scope creep. |

**No violations** → Complexity Tracking empty.

## Tech Stack

- **CI**: GitHub Actions (`ubuntu-latest`), `actions/checkout@v4`.
- **Assertion tools**: `jq` (JSON validity), `bash` 3.2 (AC-2 cross-check script, reused), `grep -E` (doc-presence).
- **Secret-scanning**: `gitleaks` v8.30.1 (SHA256-pinned download), `useDefault = true` ruleset.
- **No language runtime, no build system, no package manager** added.

## Components

| Component | Type | Change | Reuses |
|---|---|---|---|
| `.github/workflows/tachi-permissions-verify.yml` | CI workflow | **new** | structure of `tachi-catalog-drift.yml` (dual-trigger, `paths:` anchor, `contents: read`, header comment block) |
| `claude-permissions-ac2-crosscheck.sh` | Bash script | **reused (invoked, not edited)** | delivered #280 (PR #290) |
| `docs/standards/PRECOMMIT_HOOKS.md` §3 | doc | modify — add per-pattern→rule-ID catalog | existing §3 "What gets scanned" |
| `.gitleaks.toml.adopter-template` | config template | **new** (~80–120 LOC) | `.gitleaks.toml` structure + ADR-042 §Alternatives |
| `docs/standards/PRECOMMIT_HOOKS.md` §9 + `README.md` | doc | modify — template pointer + cross-ref | F-5 doc pattern |
| gitleaks pin-bump cadence surface | doc (+ optional issue template) | **new/modify** | ADR-042 Decision Item 6 + `.pre-commit-config.yaml:31` in-comment folklore |

## Data Flow

```
#281 workflow (per PR / push:[main] touching a governed path):
  GitHub event
    └─▶ paths: filter (single &verify_paths anchor)   ── no governed path? → job never runs (zero cost)
          └─▶ actions/checkout@v4  (FULL checkout — .git required by AC-2 script)
                └─▶ [1] command -v jq            (FR-281.7 guard — fail loud if jq absent)
                └─▶ [2] jq empty settings.json   (FR-281.2 — JSON validity)
                └─▶ [3] bash claude-permissions-ac2-crosscheck.sh   (FR-281.3 — exit 0 pass / 1 orphan / 2 invariant; any non-zero fails)
                └─▶ [4] grep -E '^## 3\. Settings precedence' + '^## 4\. Per-rule rationale table'  (FR-281.4 doc-presence)
                      └─▶ all green → pass ; any non-zero → RED (blocks merge / flags direct push)
```

## Implementation Design (phased)

### Phase P1 — #281 permissions CI (LEAD, P1) — ~0.5 d

**Workflow sketch** (`.github/workflows/tachi-permissions-verify.yml`):

```yaml
name: tachi permissions-verify
on:
  pull_request:
    paths: &verify_paths
      - '.claude/settings.json'
      - 'docs/standards/CLAUDE_PERMISSIONS.md'
      - '.aod/scripts/bash/claude-permissions-ac2-crosscheck.sh'
      - '.github/workflows/tachi-permissions-verify.yml'
  push:
    branches: [main]
    paths: *verify_paths            # SAME anchor — F-250 lock-step (no second list)
permissions:
  contents: read
jobs:
  verify:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4   # FULL checkout — AC-2 script needs .git (git rev-parse --show-toplevel) — FR-281.8
      - name: Assert jq present     # FR-281.7
        run: command -v jq >/dev/null || { echo "::error::jq missing on runner"; exit 1; }
      - name: JSON validity         # FR-281.2
        run: jq empty .claude/settings.json
      - name: AC-2 cross-check      # FR-281.3 (fails on ANY non-zero: 1 orphan, 2 invariant)
        run: bash .aod/scripts/bash/claude-permissions-ac2-crosscheck.sh
      - name: Doc-presence §3/§4     # FR-281.4
        run: |
          grep -qE '^## 3\. Settings precedence'      docs/standards/CLAUDE_PERMISSIONS.md || { echo "::error::§3 missing"; exit 1; }
          grep -qE '^## 4\. Per-rule rationale table'  docs/standards/CLAUDE_PERMISSIONS.md || { echo "::error::§4 missing"; exit 1; }
```

- **Header comment block** (replicate `tachi-catalog-drift.yml` lines 1–43): document the dual-trigger rationale, the single-anchor F-250 lock-step invariant, the full-checkout dependency (FR-281.8), and the single-OS justification — self-documenting for future editors.
- **Failure-injection smoke test** (the code-economy "one runnable check" carve-out): a throwaway local script copies each governed file to a tmp dir, injects (a) a JSON syntax error, (b) an orphaned `settings.json` rule, (c) a deleted §3/§4 heading, and asserts each step command exits non-zero; then asserts clean `main` exits 0 (AC scenario 4 — baseline green today). Not committed (throwaway) unless the split-valve promotes it.
- **AC coverage**: AC-1 (JSON + orphan reddening), AC-2 (clean-main green), AC-3 (`push:[main]`), plus FR-281.7 (jq guard) and the AC-7/AC-12 doc-presence degradation.

### Phase P2 — #287 pin-bump cadence (P2) — ~0.5 d

- **Single source of truth**: add a `PRECOMMIT_HOOKS.md` subsection (canonical bump recipe) + update `ADR-042 §References`. Bump recipe steps (ADR-042 Decision Item 6): update tag → `pre-commit autoupdate --freeze` → re-run `tests/fixtures/gitleaks-rule-interaction/run.sh` (16/16) → `pre-commit run --all-files` (0 findings) → **re-derive the #285 per-pattern→rule-ID mapping** (Architect A-1 — catches rule-ID renames the fire/no-fire matrix misses) → update ADR-042 §References + `PRECOMMIT_HOOKS.md §Known-Limitations` on any guarantee change.
- **Referenceability** (FR-287.2): a `.github/ISSUE_TEMPLATE/gitleaks-bump.md` (or a documented anchor) so future `chore(deps): bump gitleaks vX.Y.Z` issues cite the canonical recipe.
- **FR-287.3 scheduled detector**: OUT of the core; flagged as split-valve for `/aod.tasks` (a `tachi-citation-linkrot.yml`-style scheduled monitor is separable).

### Phase P3 — #285 + #286 (P3, SPLIT-VALVE) — ~1.0 d (or carved out)

- **#285 probe**: build-time script provisions gitleaks (FR-285.5 SHA256 stanza), creates one temp fixture per canonical pattern (`ghp_*`, `AKIA*`, `sk-*`, `sk-ant-*`, PEM, high-entropy), runs `gitleaks dir --report-format=json`, parses each hit's `RuleID`, emits the per-pattern→rule-ID map. Hand-author the catalog table into `PRECOMMIT_HOOKS.md §3`. Any uncovered pattern → filed `enhancement` issue (FR-285.4). **Empirical, fail-never-skip.**
- **#286 template**: author `.gitleaks.toml.adopter-template` with 4 commented sections (custom rules / allow-list extension / per-rule severity / tool-swap to trufflehog|detect-secrets, grounded in ADR-042 §Alternatives — differentiator is *allow-list ergonomics*, not runtime). Validate with `gitleaks detect --config=.gitleaks.toml.adopter-template` (FR-286.2). Add `PRECOMMIT_HOOKS.md §9` pointer + `README.md` Security cross-ref (FR-286.3).
- **Split decision (at `/aod.tasks`, both reviewers)**: carve #285/#286 into `F-5-enhancements` if #285 needs a **committed** fixture harness OR #286 exceeds ~120 LOC / grows a test surface. **3.0 eng-day ceiling = numeric trip-wire.** #281 + #287 core ships regardless. **Sequencing**: #285 before/with #287 (cadence re-derivation consumes #285's mapping).

## ADR Decision

**No new ADR.** This feature is a mechanical extension of three accepted decisions and introduces no new architecturally-significant choice:
- **ADR-037 D-14** — the `tachi-catalog-drift.yml` catalog-drift CI-guard pattern #281 clones (dual-trigger, anchored `paths:`, fail-closed).
- **ADR-041** — the Claude permissions baseline whose §3/§4 structure and AC-2 cross-check #281 enforces.
- **ADR-042 Decision Item 6** — the gitleaks pin-bump cadence #287 formalizes (+ §Alternatives grounding #286's tool-swap section).

#287 adds a `§References` pointer to ADR-042; #285/#287 may update `§Known-Limitations` on a guarantee change. Architect reviewer confirms no ADR is warranted.

## Project Structure

### Documentation (this feature)

```
specs/281-ci-governance-hardening-tail/
├── plan.md              # This file
├── spec.md              # PM-approved (APPROVED_WITH_CONCERNS)
├── research.md          # Phase 0 — complete, 0 unresolved NEEDS CLARIFICATION
├── feasibility-check.md # team-lead estimate (2.0 d central)
├── checklists/          # spec quality checklist
└── tasks.md             # (/aod.tasks output — next)
```

**Phase 1 design artifacts (`data-model.md`, `contracts/`, `quickstart.md`): intentionally N/A.**
- No data entities → no `data-model.md`. The "Key Artifacts" table in spec.md + the Components table here fully capture the touched surfaces.
- No API endpoints → no `contracts/`.
- No new user-facing runtime → no `quickstart.md`; local-run instructions already live in `CLAUDE_PERMISSIONS.md` / `PRECOMMIT_HOOKS.md` (avoiding duplication per code-economy).
- Generating empty ceremony files would violate code-economy rung 1 (spec does not require them). **AOD-SIMPLIFICATION: Phase-1 artifacts omitted — upgrade: add if a future sub-feature introduces an API or datastore.**

### Source (repository root)

```
.github/workflows/tachi-permissions-verify.yml   # new (#281)
.github/ISSUE_TEMPLATE/gitleaks-bump.md          # new, optional (#287 referenceability)
.gitleaks.toml.adopter-template                  # new (#286)
docs/standards/PRECOMMIT_HOOKS.md                # modify §3 (#285), §9 (#286), §Known-Limitations (#287)
docs/architecture/02_ADRs/ADR-042-*.md           # modify §References (#287)
README.md                                        # modify Security subsection (#286 cross-ref)
.aod/scripts/bash/claude-permissions-ac2-crosscheck.sh   # REUSED, unmodified (#281)
tests/fixtures/gitleaks-rule-interaction/run.sh  # REUSED, unmodified (#285/#287 re-test)
```

**Structure Decision**: single-project infra layout — new CI workflow under `.github/workflows/`, new template at repo root (mirrors `.gitleaks.toml` sibling), doc edits under `docs/standards/`. No `src/` (no application code).

## Testing Strategy

- **#281**: failure-injection smoke (throwaway) asserting each step reddens on a broken temp copy + greens on clean `main`. The checks are independently runnable (that IS the reuse value — same commands as local pre-commit).
- **#285/#286**: the committed 16-fixture `run.sh` matrix (16/16) provisioned with the SHA256-verified gitleaks binary; per-pattern temp fixtures for the catalog; `gitleaks detect --config=` for template validity.
- **Determinism**: all #281 checks are network-free string/JSON assertions (NFR-2) — no flake surface.

## Complexity Tracking

*No Constitution Check violations.* — table intentionally empty.

## Risks & Mitigations (carried from spec/PRD)

| Risk | Mitigation |
|---|---|
| R-1 path filter under-triggers (misses a governed edit) | include the AC-2 script + workflow file in the anchor; err broad (over-trigger is safe) |
| R-2 gitleaks default-rule drift stales #285 catalog | #287 re-derivation step (rule-ID, not just fire/no-fire) on each bump |
| R-3 scope creep in #285/#286 | §8 split-valve; 3.0-d ceiling trip-wire at `/aod.tasks` |
| R-4 `jq` absent on runner | FR-281.7 jq-presence guard (fail loud before `jq empty`) |
| C-1 gitleaks not preinstalled | FR-285.5 SHA256-verified download; fail-never-skip |
| C-3 sparse checkout repoints repo root | FR-281.8 full `actions/checkout@v4` + header-comment invariant |
