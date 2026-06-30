---
prd:
  number: 338
  topic: restore-substitution-hardening
  created: 2026-06-29
  status: Approved
  type: feature
triad:
  pm_signoff: {agent: product-manager, date: 2026-06-29, status: APPROVED, notes: "Authored via ~aod-define. BLP-06 Wave 2, F-2 — restore the F-248/F-256 hardening the 2026-06-28 /aod.update silently reverted on public main, + document the landed push-gate/xfail groundwork (99507b2). User value (adopters scaffold from main; main must not ship weaker hardening than the release) and the hard scope-fence (FR-008 keeps the entangled docs/defaults.env reconciliation out) are clear. Folded both reviewers' corrections at v1.1: FR-004 reframed clean-revert (architect HIGH-1), FR-008 attribution fixed + update.sh acknowledged, byte-parity oracle softened (MEDIUM-1), all 3 OQs resolved."}
  architect_signoff: {agent: architect, date: 2026-06-29, status: APPROVED_WITH_CONCERNS, notes: "0 BLOCKING / 2 HIGH / 3 MEDIUM / 3 LOW; all verified against the live tree (5b64f68..HEAD). HIGH-1 (folded): FR-004's '3-way reconciliation, Sprint→Loop entangled in these files' is contradicted by the diff — the 3 in-scope files are a PURE generic-revert (0 Sprint/Loop, 0 surviving tachi markers), so restore = checkout-from-5b64f68 + confirmation diff, NOT a hand-merge; Risk-1 is Low/Low for these files, the real entanglement is in OUT-OF-SCOPE docs/defaults.env (correctly fenced). HIGH-2: defaults.env entanglement is TECH_STACK-loss/ORCHESTRATION_TARGET-readd (whitelist-schema, not Sprint→Loop) — verify test_init_sh_defaults_env.py is green with TECH_STACK absent or pull it in (1 line/file). MEDIUM-2: OQ-1 resolved — manifest is already MORE hardened at HEAD (init.sh user| not owned|); do NOT revert it. MEDIUM-1: byte-parity test is xfail'd so suite-green proves behavioral not byte parity (SC-005 softened). MEDIUM-3: classify scripts/update.sh delta for SC-004. Full: .aod/results/architect.md"}
  techlead_signoff: {agent: team-lead, date: 2026-06-29, status: APPROVED_WITH_CONCERNS, notes: "FEASIBLE — single Plan→Build→Deliver cycle, do NOT split (3 files share one reconciliation context + one CI oracle). Every dependency/done-claim verified against the repo (5b64f68 intact, 99507b2 is branch tip, hardening gone on main). Effort M (cut-line-bound, not LOC). 3 concerns, 0 blockers: C-1 OQ-1 manifest boundary (architect resolved: leave manifest), C-2 OQ-3 defaults.env gate state (HIGHEST-leverage plan question), C-3/W-1 xfail byte-surface blind spot → add manual byte spot-check. Carry S-1 deliver-gate (don't push until restore green — push:[main] would redden main). Estimate planning=2, floor=1, ceiling=3 eng-days. Full: .aod/results/team-lead.md"}
source:           # Automatically populated from GitHub Issue
  idea_id: 338    # Always equals prd.number (GitHub Issue number)
  story_id: null  # Deprecated — user stories now stored in GitHub Issue body
---

# Restore F-248/F-256 Substitution Hardening — Product Requirements Document

**Status**: Approved (2026-06-29 — PM ✓ + Architect ⚠ + Team-Lead ⚠; 0 blockers; corrections folded at v1.1)
**Created**: 2026-06-29
**Author**: product-manager
**Reviewers**: architect, team-lead
**Phase**: BLP-06 — Integrity & Hardening (Wave 2, F-2)
**Priority**: P0

---

## 📋 Executive Summary

### The One-Liner
A template-sync accidentally reverted tachi's shipped security hardening on public `main`; this feature puts it back — and slams the door that let it happen silently.

### Problem Statement
On 2026-06-28 the `/aod.update` AOD-Kit re-sync (commits `3ec1eec → ad390f8`) reverted three tachi-customized bash hardening files to their upstream-generic versions, **silently dropping shipped security hardening from public `main`**:

| File | Lost hardening |
|------|----------------|
| `.aod/scripts/bash/template-substitute.sh` | **F-248 `patsub_replacement` shim** — disables bash 5.2+'s `patsub_replacement` so `&` in a replacement value stays literal. Without it, `AT&T`-style values corrupt to `AT{{PROJECT_NAME}}T` (the original F-248 regression class, ADR-038). |
| `scripts/init.sh` | **F-248 substitution hardening** (sed → parameter-expansion + input validation; ~240 lines reverted). |
| `.aod/scripts/bash/template-git.sh` | **F-256 git-clone-timeout hardening** (bounded fetch via `AOD_FETCH_TIMEOUT`). |

The hardening was **intact at the v4.44.0 release** (`5b64f68`) and was removed *after*, by the update. It reached public `origin/main` because **`/aod.update` commits direct to `main`, bypassing the PR-triggered `tachi-pytest.yml` gate** — the exact blind spot tracked in #329. For adopters, public `main` is the source-of-truth they scaffold from: shipping reverted hardening regresses the very security posture tachi advertises (`AT&T`-class corruption returns; an unresponsive clone upstream can hang `init` indefinitely).

This is the **second occurrence** of this clobber pattern (first resolved at `07236cf`, 2026-06-15; regressed again 2026-06-28) — which is why the fix pairs *restoration* with a *standing guardrail*, not just a one-off revert.

### Proposed Solution
Three moves, scoped tightly to the F-248/F-256 surface:

1. **Restore** the F-248/F-256 hardening to `main`. For the three in-scope files this is a **clean generic-revert restore** — verified by the Architect review: the three files were reverted *completely* to upstream-generic with **no surviving legit change to preserve**, so the operation is a `checkout` of the three file bodies from last-good `5b64f68` followed by a **confirmation diff** (not a hand-merge). The genuine "reconciliation" caution applies only to the **out-of-scope** docs/`defaults.env` surface, which FR-008 fences out.
2. **Harden the gate** — add a `push:[main]` trigger to `tachi-pytest.yml` so a future direct-to-main clobber of the hardening surface **reddens `main` immediately** instead of shipping silently. *(✅ landed in approach-independent groundwork commit `99507b2`.)*
3. **Quarantine** the unrelated, pre-existing baseline-fixture staleness (`test_personalized_tree_bytes_match_baseline`, red since *before* the clobber) as `xfail` with a #329 tracking ref, so the restore can land green without masking it. *(✅ landed in `99507b2`.)*

### Success Criteria
- The F-248 + F-256 CI-gated suite is **green on both matrix legs** (macOS bash 3.2.57 + ubuntu bash 5.x) on `main`.
- The F-248 patsub canary passes: an `AT&T`-style value substitutes to `AT&T`, never `AT{{PROJECT_NAME}}T`.
- The restored three file bodies match last-good `5b64f68` behavior (confirmation diff is the parity oracle).
- The *restore commit's* diff touches **only** the in-scope hardening surfaces; out-of-scope deltas already on the branch are explicitly accounted for (SC-004 baseline).
- A future direct-to-main clobber of a hardening-surface file makes CI **fail visibly** rather than ship silently.

### Timeline
Single feature on the in-flight `338-restore-substitution-hardening` branch. Groundwork (gate + xfail) already committed; the remaining deliverable is the clean-revert restore + CI-green verification. **Team-Lead estimate: 2 eng-days central (1 floor / 3 ceiling)** — trending toward the floor now that the Architect has confirmed the three files are a clean revert (see `specs/338-restore-substitution-hardening/feasibility-check.md`). One Plan → Build → Deliver cycle; do not split.

---

## 🎯 Strategic Alignment

### Product Vision Alignment
**Reference**: [product-vision.md](../01_Product_Vision/product-vision.md)

tachi's positioning is a trustworthy **security harness** that teams install into their own projects. That trust is undermined the moment public `main` ships *less* hardening than a tagged release. This feature restores the integrity of the adopter-facing source-of-truth and ensures a template-sync can never again silently weaken it without a red build. It is integrity maintenance on the exact surface adopters install from.

### Initiative Fit — BLP-06 Wave 2
**Reference**: BLP-06 — Integrity & Hardening (`_internal/strategy/`)

- BLP-06 is the project's **first maintenance/consolidation initiative** (subtractive, not additive): close integrity gaps and harden CI rather than ship net-new scanner capability.
- **Wave 2, F-2 (this PRD, #338)**: restore the F-248/F-256 hardening the 2026-06-28 `/aod.update` clobbered + gate `tachi-pytest` on direct main pushes. Founder-promoted from a Maintenance-Lane green-check finding to feature-sized once it became clear the work needed a standing guardrail and a careful scope-fence, not a one-line revert.
- **Sibling**: F-1 (#333, citation-URL remediation) — the other BLP-06 integrity headline. #338 is disjoint from #333 (verified: no file overlap).
- **Lineage**: the hardening originates in **F-248** (substitution surface hardening, ADR-038) and **F-256** (source-pattern hardening, ADR-040); #338 does not re-design it — it restores it.

### Roadmap Fit
**Phase**: BLP-06 Wave 2 (P0 — integrity regression on public `main`).
**Dependencies**: the last-good hardening reference (`5b64f68`, v4.44.0-era, verified intact) and the in-branch groundwork (`99507b2`, verified = branch tip). No downstream feature blocks on #338; it unblocks confidence in the install surface.

---

## 🧑‍💼 Target Users & Personas

### Primary Persona: tachi Adopter (scaffolding from `main`)
- **Role**: Developer installing tachi into their project via `scripts/init.sh` / template scaffolding off public `main`.
- **Goal**: Get the same safe, hardened substitution behavior that the v4.44.0 release advertised.
- **Pain Point**: With the hardening reverted, a project value containing `&` (e.g., `AT&T`, `R&D`) corrupts during `{{PROJECT_NAME}}` substitution on bash 5.2+, and an unresponsive template upstream can hang `init` with no timeout.
- **Why this matters**: The adopter never sees the release tag — they scaffold from `main`. `main` regressing below the release is a direct, silent quality hit.

### Secondary Persona: tachi Maintainer
- **Role**: Engineer running `/aod.update` to pull upstream AOD-Kit template improvements.
- **Goal**: Adopt upstream refreshes without silently reverting tachi-local hardening.
- **Pain Point**: `/aod.update` commits direct to `main` and bypasses the PR-gated hardening suite, so a clobber ships invisibly (this is the second occurrence).
- **Why this matters**: A standing `push:[main]` gate converts an invisible regression into an immediate red build — the maintainer finds out in minutes, not on the next adopter bug report.

### Tertiary Persona: Security-conscious Evaluator
- **Role**: Someone auditing tachi's own hygiene before adopting it as a security tool.
- **Goal**: Confirm tachi practices what it preaches — shipped hardening stays shipped.
- **Why this matters**: "Their `main` shipped weaker hardening than their release, silently" is exactly the kind of finding that erodes confidence in a security harness. Closing it (and gating it) is a credibility control.

---

## 📖 User Stories

#### US-338.1: Restore the lost hardening to `main`
**When** I scaffold a project from current `main` (via `scripts/init.sh` / template substitution),
**I want** the F-248 substitution hardening and the F-256 clone-timeout hardening present and behaving as they did at v4.44.0,
**So I can** trust `&`-bearing values stay literal and a hung upstream can't block `init` forever.

**Acceptance Criteria**:
- **Given** `template-substitute.sh` on `main`, **when** I inspect it, **then** the F-248 `patsub_replacement` shim is present.
- **Given** a `{{PROJECT_NAME}}` substitution with an `AT&T`-style value on bash 5.2+, **when** `init` runs, **then** the output is `AT&T`, never `AT{{PROJECT_NAME}}T` (the ADR-038 / F-248 canary passes).
- **Given** `scripts/init.sh` on `main`, **when** I inspect substitution, **then** it uses the F-248 parameter-expansion + input-validation path (not the upstream `sed` path).
- **Given** `template-git.sh` on `main`, **when** a clone targets an unresponsive upstream, **then** the F-256 `AOD_FETCH_TIMEOUT` watchdog bounds it.
- **Given** the F-248 + F-256 CI-gated suite, **when** it runs on `main`, **then** both matrix legs (macOS bash 3.2.57 + ubuntu bash 5.x) are green.

**Priority**: P0 (core) · **Effort**: M *(cut-line-bound, not LOC; the restore source is known-good v4.44.0 code)*

#### US-338.2: Make a future direct-to-main clobber visible immediately *(✅ landed — `99507b2`)*
**When** a future `/aod.update` (or any direct-to-`main` push) reverts a hardening-surface file,
**I want** `tachi-pytest.yml` to run on the push and fail,
**So I can** catch the regression on `main` in minutes instead of shipping it silently to adopters.

**Acceptance Criteria**:
- **Given** `tachi-pytest.yml`, **when** I inspect its triggers, **then** it has a `push: branches:[main]` trigger reusing the `pull_request` paths via a single YAML anchor (no third path list to drift out of lock-step).
- **Given** a direct-to-`main` push that changes a hardening-surface path, **when** CI runs, **then** the F-248/F-256 suite executes (not skipped by the path filter).

**Priority**: P1 · **Effort**: S · **Status**: ✅ landed in groundwork commit `99507b2`.

#### US-338.3: Land the restore green without masking unrelated staleness *(✅ landed — `99507b2`)*
**When** the restore lands,
**I want** the pre-existing-red baseline-fixture test quarantined with a tracking ref,
**So I can** read green CI as "hardening restored," not a conflation with an unrelated fixture-staleness failure.

**Acceptance Criteria**:
- **Given** `test_personalized_tree_bytes_match_baseline` (red at v4.44.0, *before* the clobber), **when** the suite runs, **then** it is `xfail(strict=False)` with a #329 reason.
- **Given** a future fixture regen that fixes the staleness, **when** the suite runs, **then** the test **XPASSes** — the explicit signal to delete the marker.

**Priority**: P2 · **Effort**: S · **Status**: ✅ landed in groundwork commit `99507b2`.

---

## ⚙️ Functional Requirements

#### FR-001: Restore the F-248 `patsub_replacement` shim (`template-substitute.sh`)
`.aod/scripts/bash/template-substitute.sh` MUST restore the F-248 shim that disables bash 5.2+ `patsub_replacement`, so `&` in a replacement value is treated literally. Behavioral acceptance = `test_substitute_shim_canary.py` green.

#### FR-002: Restore the F-248 substitution hardening (`scripts/init.sh`)
`scripts/init.sh` MUST restore the F-248 substitution path (parameter-expansion + input validation; the ~240 lines reverted by the update), replacing the upstream-generic `sed` path. Behavioral acceptance = the `test_init_sh_substitution.py` / `test_init_sh_adversarial.py` suite green (modulo the #329-tracked baseline staleness, FR-007).

#### FR-003: Restore the F-256 git-clone-timeout hardening (`template-git.sh`)
`.aod/scripts/bash/template-git.sh` MUST restore the F-256 bounded-fetch hardening (`AOD_FETCH_TIMEOUT` watchdog). Behavioral acceptance = `test_template_git_clone_timeout.py` green.

#### FR-004: Restore method — clean generic-revert + confirmation diff *(corrected at v1.1 per Architect HIGH-1)*
The restore of the three in-scope files is a **clean generic-revert**, NOT a 3-way hand-merge. The Architect verified `5b64f68..HEAD` for all three files: they were reverted *completely* to upstream-generic — **zero Sprint→Loop terminology and zero surviving tachi/F-248/F-256 markers in these files** — so there is **no legit in-file change to preserve**. The correct operation is therefore: **restore the three file bodies from `5b64f68`, then run a confirmation diff** proving (a) the lost F-248/F-256 hardening is back and (b) no non-hardening upstream change was discarded. This is *restore-and-verify*, not blind: the bash-3.2.57 NFR and the confirmation diff still gate it. The genuine reconciliation caution applies to the **out-of-scope** `docs/*` and `stacks/*/defaults.env` surface (where the real Sprint→Loop refresh and the `TECH_STACK`/`ORCHESTRATION_TARGET` whitelist entanglement live), which FR-008 fences out. *(Resolves OQ-2: direct restore, no reapply.)*

#### FR-005: CI-green on both matrix legs
After the restore, the F-248 + F-256 CI-gated suite MUST pass on **both** matrix legs (macOS bash 3.2.57 — the strict compatibility gate; ubuntu bash 5.x — the modern reference). Green CI proves the *behavioral* assertions (canary, adversarial, clone-timeout, config-load); the FR-004 confirmation diff vs `5b64f68` is the complementary *parity* oracle (because the byte-identity baseline test is xfail'd under FR-007 — see Assumption 2 / SC-005). A manual byte spot-check of the restored three file bodies vs `5b64f68` is part of acceptance (Team-Lead W-1).

#### FR-006: Gate `tachi-pytest` on direct main pushes *(✅ landed — `99507b2`)*
`tachi-pytest.yml` MUST run on `push:[main]` (not only `pull_request`), reusing the PR `paths` via a single YAML anchor so the trigger surface stays single-source. *Done in groundwork; documented here for traceability.*

#### FR-007: Quarantine the pre-existing baseline staleness *(✅ landed — `99507b2`)*
`test_personalized_tree_bytes_match_baseline` MUST be `xfail(strict=False)` with a #329 reason (it was red before the clobber; it is not part of this regression). `strict=False` so a future fixture regen surfaces as XPASS. *Done in groundwork; documented here for traceability.*

#### FR-008 (constraint — scope fence)
This feature MUST NOT undertake any of the following (each a separate defect-class or entangled-with-legit-refresh follow-up, explicitly out of scope per the Issue):
- The broader **content** reconciliation of `docs/devops/CI_CD_GUIDE.md`, `docs/devops/README.md`, `docs/standards/README.md` (the actual Sprint→Loop refresh lives here, plus `AOD_GUIDE_INDEX.md` / `AOD_QUICKSTART.md` — Architect-verified).
- Restoration of the **F-2 `TECH_STACK` key** in `stacks/*/defaults.env`. *(Attribution corrected at v1.1 per Architect HIGH-2: the entanglement here is `TECH_STACK`-loss vs `ORCHESTRATION_TARGET`-readd — a **whitelist-schema** concern, NOT a Sprint→Loop refresh.)* See OQ-3 for the one tension this creates with FR-005.
- The **#329** enrichment-cap / byte-identity baseline drift (never CI-gated; the FR-007 xfail only quarantines it, it does not fix it).
- The **`scripts/update.sh`** delta (+92 lines, `5b64f68..HEAD`) is **not** a hardening surface (Architect grep found no hardening signal) and is **not** restored or modified by this feature; it is named here as explicitly-untouched so SC-004 stays auditable (Architect MEDIUM-3). *(Plan stage to ratify the classification.)*
- **Preventing** a future `/aod.update` re-clobber *at the source*. This feature provides **detection** (the push gate); the complementary control is `/aod.update` operator process insurance (mandatory checkpoint + `--dry-run` + `git diff --stat` the at-risk set), referenced but not built here. *(The manifest `owned`-fix was tried at `07236cf` and regressed at the next update, so detection is the load-bearing control — and per OQ-1 the manifest must NOT be reverted, it is already correctly hardened at HEAD.)*

---

## 🚀 Non-Functional Requirements

### Compatibility
Restored scripts MUST preserve **bash 3.2.57+** compatibility (F-248 NFR-001: no `mapfile`, no associative arrays, no `${var,,}`). The macOS matrix leg is the hard enforcement point. The restored code is known-good from v4.44.0, which already passed this leg (Architect LOW-1 confirms Risk-3 Low/Medium is accurate).

### Security
This is a **restoration of prior security posture**, not new surface (Architect LOW-1 confirms HEAD is generic and `5b64f68` is the prior-shipped hardened state): re-establishing input validation (literal-`&`, newline rejection) and bounded clone fetch. No new attack surface is introduced. Failing to restore leaves public `main` shipping the F-248 corruption class and an unbounded-clone hang to adopters.

### Determinism & Backward Compatibility
`init.sh` output MUST remain byte-deterministic where the live F-248 suite asserts it. The one known determinism gap (`test_personalized_tree_bytes_match_baseline`) is pre-existing (#329) and quarantined via FR-007 — it MUST NOT be "fixed" by masking a restore-introduced byte change inside it (Team-Lead W-1 / Architect MEDIUM-1). The FR-004 confirmation diff is the guard against that.

### No New Dependencies
Pure bash + the existing pytest harness (`pytest`, `pytest-timeout`, `pyyaml`). No manifest additions (laziness-ladder rung 5: nothing new added — Architect LOW-2 confirms).

---

## 📊 Success Metrics

- **SC-001 (CI green)**: The F-248/F-256 CI-gated suite passes on `main` on both matrix legs. **Target: 2/2 legs green.**
- **SC-002 (canary)**: `test_substitute_shim_canary.py` passes — `AT&T` → `AT&T`. **Target: pass (the F-248 regression class is closed).**
- **SC-003 (gate live)**: `tachi-pytest.yml` has a `push:[main]` trigger and it fires on a hardening-surface path change. **Target: present & firing.** *(✅ landed `99507b2`.)*
- **SC-004 (scope discipline)**: The **restore commit's** diff (measured branch-vs-`main`-pre-restore, NOT branch-vs-`5b64f68` — the branch sits atop a 30-file update delta, Architect LOW-3) touches only in-scope hardening surfaces; every out-of-scope delta already on the branch is named in FR-008. **Target: 0 unaccounted out-of-scope files in the restore commit.**
- **SC-005 (parity to v4.44.0)**: The restored three file bodies reproduce last-good v4.44.0 behavior, validated by the **FR-004 confirmation diff vs `5b64f68`** + the canary/adversarial/clone-timeout/config-load suites. **Behavioral parity is the asserted target; full byte-parity is NOT claimed this cycle** because the byte-identity baseline test is xfail'd under #329 (Architect MEDIUM-1). **Target: behavioral parity + confirmation-diff clean.**

---

## 🔍 Scope & Boundaries

### In Scope (P0/P1)
- ✅ Restore the F-248 patsub shim (`template-substitute.sh`) — FR-001.
- ✅ Restore the F-248 substitution hardening (`init.sh`) — FR-002.
- ✅ Restore the F-256 clone-timeout hardening (`template-git.sh`) — FR-003.
- ✅ Clean generic-revert restore + confirmation diff (not a hand-merge) — FR-004.
- ✅ CI-green on both matrix legs + byte spot-check — FR-005.
- ✅ `push:[main]` gate on `tachi-pytest.yml` — FR-006 *(done)*.
- ✅ xfail the pre-existing baseline staleness — FR-007 *(done)*.

### Out of Scope
- ❌ **Broader docs/devops content reconciliation** (`CI_CD_GUIDE.md`, devops/standards READMEs, AOD guide/quickstart) — this is where the real Sprint→Loop refresh lives; separate 3-way reconciliation follow-up.
- ❌ **F-2 `TECH_STACK` key restoration** in `stacks/*/defaults.env` — a whitelist-schema concern (TECH_STACK-loss/ORCHESTRATION_TARGET-readd); separate follow-up. See OQ-3.
- ❌ **`.aod/template-manifest.txt`** — do NOT revert it; HEAD's classification (`user|init.sh`, `merge|` for the two libs) is *more* hardened than `5b64f68`'s (`owned|`). Reverting would regress it (Architect MEDIUM-2 / OQ-1).
- ❌ **`scripts/update.sh`** delta — not a hardening surface; left untouched (named for SC-004 auditability).
- ❌ **#329** enrichment-cap / byte-identity baseline drift — distinct, never-CI-gated defect class; only quarantined here, not fixed.
- ❌ **Preventing** a future `/aod.update` re-clobber at the source — detection (push gate) is in scope; source-prevention (operator `--dry-run`/diff insurance) is referenced, not built.

### Assumptions
- The F-248/F-256 hardening at `5b64f68` is the correct last-good reference and reproduces v4.44.0 behavior (`git describe` = `v4.44.0-1-g5b64f68`; Team-Lead + Architect verified the shim/watchdog are intact there and gone on `main`).
- Suite-green proves **behavioral** parity (canary + adversarial + clone-timeout + config-load); **byte**-identity is NOT asserted this cycle (the baseline test is xfail'd under #329). The FR-004 confirmation diff vs `5b64f68` is the parity oracle that closes the gap (Architect MEDIUM-1). *(Softened at v1.1 from the v1.0 "suite-green is a sufficient oracle" claim.)*
- The three in-scope files are a clean generic-revert (Architect HIGH-1, verified) — the only open cut-line risk is the *out-of-scope* `defaults.env` gate-state question (OQ-3).

### Constraints
- **Technical**: the restore must thread bash 3.2.57+ compatibility; for the three files this is the *only* real constraint now that the 3-way-merge premise is retired (FR-004).
- **Process (S-1, load-bearing)**: lands on the existing `338-restore-substitution-hardening` branch; per `99507b2`'s own warning, **do not push/PR until the restore is green locally** — the FR-006 `push:[main]` gate would otherwise redden `main` on its own behalf. Encode as the final deliver-gate task.

---

## 🛣️ Timeline & Milestones

**Team-Lead feasibility estimate** (`specs/338-restore-substitution-hardening/feasibility-check.md`): **planning 2 eng-days** (floor 1 / ceiling 3), single cycle, do not split. The Architect's HIGH-1 (clean revert) trends the realistic case toward the **floor (1 day)**; planning is held at 2 pending the C-2/OQ-3 `defaults.env` gate-state check (the one genuine unknown).

| Milestone | Owner | Status |
|-----------|-------|--------|
| PRD Approval (this doc) | product-manager | ✅ Approved (2026-06-29) |
| Spec + restore method (ratify OQ-1/2/3) | architect | 📋 Pending (`/aod.plan`) |
| Tasks + assignments (S-1 gate, W-1 spot-check) | team-lead | 📋 Pending (`/aod.plan`) |
| Build — clean-revert restore + CI green | senior-backend-engineer + tester | 📋 Pending |
| Gate + xfail groundwork | — | ✅ Done (`99507b2`) |
| Deliver + release (S-1 pre-push gate) | devops | 📋 Pending |

Single feature; no multi-week phasing. Heaviest unit is the FR-004 restore + confirmation diff; the gate and xfail are already landed.

---

## ⚠️ Risks & Dependencies

### Technical Risks

**Risk 1 — Cut-line on the OUT-OF-SCOPE surface** *(downgraded for the 3 files at v1.1 per Architect HIGH-1)*
- **For the three in-scope files**: **Low / Low** — they are a clean generic-revert with no surviving legit change to preserve; restore is a checkout + confirmation diff.
- **The residual cut-line risk lives out-of-scope** (`defaults.env` `TECH_STACK`, docs Sprint→Loop refresh), correctly fenced by FR-008. The one place it touches in-scope work is OQ-3 (the `defaults.env` gate-state question).
- **Mitigation**: confirmation diff vs `5b64f68`; the CI suite is the green-gate; the scope fence keeps the entangled surface out.

**Risk 2 — `defaults.env` gate state blocks "CI green"** *(Team-Lead C-2 / Architect HIGH-2 — highest-leverage)*
- **Likelihood**: Medium · **Impact**: High (could fail SC-001 through no fault of the restore)
- `stacks/*/defaults.env` is on the FR-006 push-gate `paths`. The `/aod.update` deleted the F-2 `TECH_STACK` key (out of scope to restore). If the gated `test_init_sh_defaults_env.py` asserts the 5-key surface, it may be **red with `TECH_STACK` absent**, blocking FR-005.
- **Mitigation (resolve at `/aod.plan`, OQ-3)**: confirm the test is green with `TECH_STACK` absent; if red, either pull the `TECH_STACK` restore in-scope (1 line/file, trivial) or apply the same xfail+track treatment. **Settle at plan or it is a build surprise.**

**Risk 3 — Re-clobber on the next `/aod.update`**
- **Likelihood**: Medium · **Impact**: High — this is the second occurrence.
- **Mitigation**: the `push:[main]` gate (this feature) makes a recurrence **immediately visible** on `main`; the operator-side `--dry-run` + `git diff --stat` insurance on `/aod.update` is the complementary process control. The manifest `owned`-fix is *not* relied upon (tried `07236cf`, regressed; and per OQ-1 the manifest is already correct at HEAD and must not be reverted).

**Risk 4 — bash 3.2 regression in restored code**
- **Likelihood**: Low · **Impact**: Medium · the restored code must run on macOS bash 3.2.57.
- **Mitigation**: the macOS matrix leg is a hard CI gate; the restored code is known-good from v4.44.0, which already passed this leg.

### Dependencies
- **Last-good reference**: `5b64f68` (`v4.44.0-1-g5b64f68`; hardening verified intact) — the restore source.
- **In-branch groundwork**: `99507b2` (push gate + xfail; verified = branch tip) — US-338.2 / US-338.3 done; list as completed deps, do not re-task (Team-Lead S-3).
- **Design rationale (honor, don't re-litigate)**: ADR-038 (F-248 placeholder substitution strategy), ADR-040 (F-256 config-file parsing hardening).
- **Tracking ref**: #329 (enrichment-cap / byte-identity drift; fixture regen) — the FR-007 xfail's pointer.

```
v4.44.0 hardening intact (5b64f68)
        │
        ▼  /aod.update 2026-06-28 (3ec1eec→ad390f8) — direct-to-main, bypassed PR gate
   main REGRESSED  ──▶  #338: clean-revert restore (FR-001..005) + gate (FR-006 ✅) + xfail (FR-007 ✅)
                              ◀── BLP-06 Wave 2, F-2
```

---

## ❓ Open Questions

*All three resolved by the Architect review; carried to `/aod.plan` for ratification in spec.*

- [x] **OQ-1 — restore surface boundary**: **RESOLVED — three file bodies suffice.** The manifest is already *more* hardened at HEAD (`user|init.sh`, `merge|` libs) than at `5b64f68` (`owned|`); do **NOT** revert it. Active-stack state (`.aod/stack-active.json`) is out-of-surface (unchanged `5b64f68..HEAD`). `99507b2`'s "manifest + active-stack state" describes the clobber's *blast radius*, not the restore's *inputs*. — *Architect (MEDIUM-2)* — ratify at `/aod.plan`.
- [x] **OQ-2 — reconciliation method**: **RESOLVED — direct restore of the three file bodies from `5b64f68` + confirmation diff, NOT a 3-way merge** (the files are a clean generic-revert with no surviving legit change). — *Architect (HIGH-1)* — ratify at `/aod.plan`.
- [ ] **OQ-3 — `defaults.env` gate state** *(the one still-open question — highest-leverage)*: confirm `test_init_sh_defaults_env.py` is GREEN with the F-2 `TECH_STACK` key absent. If red, pull `TECH_STACK` restoration in-scope (1 line/file) or xfail+track it — else it blocks FR-005's "CI green on both legs." — *Architect + Team-Lead* — settle at `/aod.plan` **before build**.

---

## 📚 References

- **Issue**: [#338](https://github.com/davidmatousek/tachi/issues/338) — restore F-248/F-256 hardening + gate tachi-pytest on push (this PRD's source; body is primary input).
- **Groundwork commit**: `99507b2` — `ci(338): gate tachi-pytest on direct main pushes; xfail pre-existing baseline` (push gate + xfail; restore explicitly deferred as feature-sized).
- **Last-good hardening reference**: `5b64f68` (`v4.44.0-1-g5b64f68`).
- **Originating features**: `specs/248-substitution-surface-hardening/` (F-248, ADR-038), `specs/256-source-pattern-hardening/` (F-256, ADR-040).
- **CI gate**: `.github/workflows/tachi-pytest.yml` (the 2-runner bash-version matrix).
- **Tracking**: #329 (enrichment-cap / byte-identity drift, fixture regen) — FR-007 xfail pointer.
- **Initiative**: BLP-06 — Integrity & Hardening, Wave 2 (`_internal/strategy/`).
- **Sibling**: `docs/product/02_PRD/333-citation-url-remediation-2026-06-29.md` (BLP-06 Wave 1, F-1).
- **Review artifacts**: `.aod/results/architect.md`, `.aod/results/team-lead.md`; estimate in `specs/338-restore-substitution-hardening/feasibility-check.md`.

---

## ✅ Approval & Sign-Off

| Role | Name | Status | Date | Comments |
|------|------|--------|------|----------|
| Product Manager | product-manager | ✅ Approved | 2026-06-29 | Authored via ~aod-define; folded both reviews at v1.1 (FR-004 clean-revert, FR-008 attribution + update.sh, oracle softening, OQ resolutions) |
| Architect | architect | 🟡 Approved with Comments | 2026-06-29 | 0 blocking / 2 HIGH / 3 MEDIUM / 3 LOW; HIGH-1 inverts FR-004 to clean-revert (easier, lower-risk); resolved OQ-1/2/3. See `.aod/results/architect.md` |
| Engineering Lead | team-lead | 🟡 Approved with Comments | 2026-06-29 | FEASIBLE, single cycle, do not split; est. 2d (1/3); C-2 defaults.env gate is the highest-leverage plan question; carry S-1 + W-1. See `.aod/results/team-lead.md` |

Legend: ✅ Approved | 🟡 Approved with Comments | ❌ Rejected | 📋 Pending

---

## 📝 Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-06-29 | product-manager | Initial PRD (BLP-06 Wave 2, #338) — reconcile-restore F-248/F-256 hardening + document landed gate/xfail groundwork |
| 1.1 | 2026-06-29 | product-manager | Folded parallel Triad review (0 blockers): **FR-004 reframed clean generic-revert** (Architect HIGH-1, inverts the 3-way-merge premise) + Risk-1 downgraded; **FR-008 attribution fixed** (defaults.env = whitelist-schema not Sprint→Loop, HIGH-2) + `update.sh` named for SC-004; **Assumption 2 / SC-005 softened** (byte-parity not asserted; confirmation diff is the oracle, MEDIUM-1); **OQ-1/OQ-2 resolved** (don't revert manifest; direct restore), **OQ-3** sharpened as the one open gate-state question; SC-004 baseline defined (MEDIUM-3/LOW-3); timeline from Team-Lead estimate (2d). All three sign-offs recorded. |
