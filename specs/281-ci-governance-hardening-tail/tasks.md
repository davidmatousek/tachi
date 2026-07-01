---
triad:
  pm_signoff:
    agent: product-manager
    date: 2026-07-01
    status: APPROVED
    notes: "18 tasks cover all 4 user stories + 19 FR/5 NFR with 1:1 traceability, zero scope creep (FR-287.3 correctly the only unauthored FR — spec-marked optional/split-valve). MVP (US1 #281=SC-1) + P1/P2/P3 preserved; #281+#287 core protected. Concurs with CARVE-IN (triggers don't fire; #287↔#285 coupling decisive; build-time fallback intact). Details: .aod/results/product-manager-tasks-281.md"
  architect_signoff:
    agent: architect
    date: 2026-07-01
    status: APPROVED_WITH_CONCERNS
    notes: "CONCURS with CARVE-IN — reconciled own A-1 vs A-3 against live main: A-1 coupling decisive (carving #285 out would leave #287 forward-referencing a catalog in a different feature — worse than carve-in); A-3 trigger does not fire (fixtures already committed, T010 authors no new harness). Critical path, T007→T011 cross-phase dep, #285-before-#287 sequencing, T002 fail-never-skip, #281 workflow fidelity, [P]/4-wave all sound. 4 non-blocking authoring-precision fixes (T007 section placement, T010 high-entropy fixture, T011 §3 state, T015 §9 modify-not-add) APPLIED 2026-07-01. Details: .aod/results/architect-tasks-281.md"
  techlead_signoff:
    agent: team-lead
    date: 2026-07-01
    status: APPROVED
    notes: "Concurs with CARVE-IN — all 3 §8 carve triggers empirically false vs live main; 3.0-d numeric trip-wire does NOT fire (~1.0 d headroom, central 2.0 d = 4×0.5 d). 18-task/4-wave decomposition appropriately granular; critical path T001→T002→T010→T011→T007→T009 is the true longest chain with #281/US1 off it as independent MVP; C-1 sequencing (#285 before #287) mechanically enforced; core isolated from #285/#286 with retained build-time fallback (T016). Details: .aod/results/team-lead-tasks-281.md"
---

# Tasks: CI & Governance Hardening Tail (F-4/F-5 follow-ups)

**Input**: Design documents from `specs/281-ci-governance-hardening-tail/` (plan.md + spec.md + research.md)
**Feature**: #281 (lead) + #285 / #286 / #287 · BLP-06 Wave-2 maintenance
**Tests**: failure-injection smoke (#281) + empirical fixture matrix (#285/#286) — infra verification, not app unit tests.

> **Definition of Done** (constitution VII): (1) merged to `main` via `feat(281):` PR with a release-please release; (2) all in-scope ACs green (#281 workflow passes on clean `main`, fixture matrix 16/16, template config-valid); (3) governance triple sign-off recorded.
<!-- DOD-ACK -->

---

## ⚖️ Split-Valve Determination (PRD §8 — decided mechanically here)

**PRODUCER DETERMINATION: CARVE-IN — all four issues (#281/#285/#286/#287) ship in feature 281.** Triple review confirms/overturns.

| PRD §8 carve trigger | Decomposition evidence | Fires? |
|---|---|---|
| #285 requires a **committed** fixture harness (not throwaway) | T010 does a **throwaway/reuse** empirical read against the *existing* committed `tests/fixtures/gitleaks-rule-interaction/` should-fire fixtures + hand-authors a doc table. No **new** committed harness. | ❌ No |
| #286 exceeds ~120 LOC / grows its own test surface | T013 template is ~80–120 LOC (FR-286.1); T014 validation is a single `gitleaks detect --config=` command, not a test surface. | ❌ No |
| 3.0 eng-day ceiling (numeric trip-wire) | Central 2.0 d with all four in (4 × 0.5 d); not trending to ceiling. | ❌ No |
| **Architect A-1 coupling** (#287 re-derives #285's mapping) | #287's cadence recipe (T007) consumes #285's rule-ID catalog (T011) → the two cannot cleanly separate; #287 is P2 core. | ➡️ favors **carve-IN** |

**Fallback**: the split-valve remains available at `/aod.build` — if T013 blows past 120 LOC or T010 requires authoring a committed harness during implementation, carve #285/#286 into a follow-up `F-5-enhancements` feature then (AC-7). #281 (US1) + #287 (US2) are the committed load-bearing core (SC-1/SC-4) and MUST NOT be blocked by #285/#286 regardless.

---

## Phase 1: Setup & Baseline

**Purpose**: Confirm the AC-2 baseline-green precondition before authoring the gate that enforces it.

- [X] T001 Verify baseline-green pre-state: run `jq empty .claude/settings.json` (expect rc=0), `bash .aod/scripts/bash/claude-permissions-ac2-crosscheck.sh` (expect exit 0 — 93 rules ↔ 93 §4 rows), and confirm `## 3. Settings precedence` + `## 4. Per-rule rationale table` headings exist in `docs/standards/CLAUDE_PERMISSIONS.md`. Establishes the US-1 scenario-4 precondition.

## Phase 2: Foundational (Blocking Prerequisite for gitleaks-touching tasks)

**Purpose**: Provision the gitleaks binary for build-time verification (NOT preinstalled on runners; the #281 workflow does NOT need it — only #285/#286/#287 steps do).

- [X] T002 [P] Provision `gitleaks` v8.30.1 for build-time steps via the SHA256-pinned download stanza reused verbatim from `.github/workflows/gitleaks.yml` (checksum `551f6fc83ea457d62a0d98237cbad105af8d557003051f41f3e7ca7b3f2470eb`); **fail (never skip)** on absent/mismatched binary (FR-285.5). Blocks T010, T014, and the T007 re-test reference.

---

## Phase 3: User Story 1 — #281 permissions CI (Priority: P1) 🎯 MVP

**Goal**: The permissions surface (`.claude/settings.json` + `CLAUDE_PERMISSIONS.md`) is CI-verified on every PR touching it and on direct `push:[main]`.
**Independent Test**: Break `settings.json` JSON validity (or orphan a rule vs. §4) in a PR → `tachi permissions-verify` fails; touch neither governed file → workflow does not run.

- [X] T003 [P] [US1] Author `.github/workflows/tachi-permissions-verify.yml` scaffold — clone `.github/workflows/tachi-catalog-drift.yml` structure: `name: tachi permissions-verify`; dual-trigger `pull_request` + `push: branches:[main]`; **single YAML-anchored** `paths: &verify_paths` list = [`.claude/settings.json`, `docs/standards/CLAUDE_PERMISSIONS.md`, `.aod/scripts/bash/claude-permissions-ac2-crosscheck.sh`, `.github/workflows/tachi-permissions-verify.yml`] reused via `*verify_paths` on the push leg; `permissions: contents: read`; `runs-on: ubuntu-latest`; `actions/checkout@v4` (full checkout) (FR-281.1/.5/.6/.8).
- [X] T004 [US1] Add the four ordered verify steps to `tachi-permissions-verify.yml`: (1) jq-presence guard `command -v jq >/dev/null || exit 1` **before** the parse (FR-281.7); (2) `jq empty .claude/settings.json` (FR-281.2); (3) `bash .aod/scripts/bash/claude-permissions-ac2-crosscheck.sh` — job fails on **any** non-zero (1 orphan **and** 2 invariant) (FR-281.3); (4) doc-presence `grep -qE '^## 3\. Settings precedence'` + `grep -qE '^## 4\. Per-rule rationale table'` on `docs/standards/CLAUDE_PERMISSIONS.md` (FR-281.4).
- [X] T005 [US1] Add the self-documenting header comment block to `tachi-permissions-verify.yml` (replicate `tachi-catalog-drift.yml` lines 1–43): dual-trigger rationale, single-anchor F-250 lock-step invariant, the full-checkout dependency (FR-281.8 — AC-2 script uses `git rev-parse --show-toplevel`), and the single-OS justification.
- [X] T006 [US1] Failure-injection smoke test (throwaway, **not committed**): copy each governed file to a tmp dir and assert each check reddens — (a) inject JSON syntax error → `jq empty` non-zero; (b) add an orphan `settings.json` rule → AC-2 script non-zero; (c) delete a §3/§4 heading → doc-grep non-zero; then assert clean `main` → all steps rc=0. Covers AC-1/AC-2/AC-3.

**Checkpoint**: US1 alone delivers SC-1 (the whole hardening point) — this is the MVP increment.

---

## Phase 4: User Story 2 — #287 pin-bump cadence (Priority: P2)

**Goal**: A single tracked, referenceable surface for the gitleaks pin-bump process so the pin cannot silently rot.
**Independent Test**: A future `chore(deps): bump gitleaks vX.Y.Z` issue can cite one canonical recipe (tag → freeze → 16-fixture re-test → rule-ID re-derivation → doc updates).
**⚠️ Sequencing**: T007's rule-ID re-derivation step references the #285 catalog (T011) — **build US3 (T010–T011) before T007** (Team-Lead C-1 / Architect A-1).

- [X] T007 [US2] Author the canonical gitleaks pin-bump cadence surface in `docs/standards/PRECOMMIT_HOOKS.md` as a **new dedicated section** (e.g., "§Gitleaks pin-bump cadence" — NOT under §Known-Limitations, which is reserved for limitations, not processes; the §Known-Limitations edit below is only the guarantee-change note): document the ADR-042 Decision-Item-6 recipe — update tag → `pre-commit autoupdate --freeze` → re-run `tests/fixtures/gitleaks-rule-interaction/run.sh` (16/16) → `pre-commit run --all-files` (0 findings) → **re-derive the #285 per-pattern → rule-ID mapping** (catches upstream rule-ID renames the fire/no-fire matrix misses) → update ADR-042 §References + `PRECOMMIT_HOOKS.md §Known-Limitations` on any guarantee change (FR-287.1). *Depends on T011.*
- [X] T008 [P] [US2] Add `.github/ISSUE_TEMPLATE/gitleaks-bump.md` — a canonical child-issue template whose body references the T007 cadence surface, so future bump issues cite the single source of truth (FR-287.2).
- [X] T009 [US2] Update `docs/architecture/02_ADRs/ADR-042-pre-commit-secret-scanning-default.md` §References to point at the T007 cadence surface (FR-287.1 doc wiring). *(FR-287.3 scheduled release-detector stays OUT — split-valve / sibling issue.)*

---

## Phase 5: User Story 3 — #285 gitleaks coverage catalog (Priority: P3, split-valve)

**Goal**: A documented per-pattern → active-default-rule-ID catalog so a SecOps reviewer can audit coverage from `PRECOMMIT_HOOKS.md` alone.
**Independent Test**: Each canonical pattern in the catalog maps to a rule ID confirmed by a fixture hit; uncovered patterns have filed issues.
**Sequencing**: build **before** T007 (US2 consumes this catalog).

- [X] T010 [US3] Empirical probe (gitleaks provisioned per T002): run `gitleaks dir --report-format=json` against the committed should-fire fixtures in `tests/fixtures/gitleaks-rule-interaction/` covering `ghp_*`, `AKIA*`, `sk-*`, `sk-ant-*`, PEM/private-key (5 patterns), **plus a throwaway temp fixture for the generic high-entropy pattern (which has no committed fixture)**; parse each hit's `RuleID` to build the per-pattern → rule-ID map (FR-285.1/.2). **Throwaway/reuse read — do NOT author a new committed harness (split-valve trigger).**
- [X] T011 [US3] Hand-author the per-pattern → rule-ID catalog table as a **new subsection** under `docs/standards/PRECOMMIT_HOOKS.md §3 "What gets scanned"` (FR-285.3); if a `[MANUAL-ONLY]` coverage note already exists elsewhere in the doc, cross-link it rather than assuming it lives in §3.
- [X] T012 [US3] For any canonical pattern NOT covered by an active default rule: file a separate `enhancement` GitHub issue and cross-reference it in the catalog (FR-285.4). If all six are covered, state "all 6 covered" explicitly.

---

## Phase 6: User Story 4 — #286 adopter-extensibility template (Priority: P3, split-valve)

**Goal**: An adopter can add a first custom credential rule in minutes via a commented starter template.
**Independent Test**: `gitleaks detect --config=.gitleaks.toml.adopter-template` loads without a config error; `PRECOMMIT_HOOKS.md §9` + `README.md` reference it.

- [X] T013 [P] [US4] Author `.gitleaks.toml.adopter-template` (~80–120 LOC) with 4 commented sections: (1) custom rules, (2) allow-list extension, (3) per-rule severity, (4) tool-swap to trufflehog / detect-secrets (grounded in ADR-042 §Alternatives — the differentiator is **allow-list ergonomics**, not runtime) (FR-286.1). **≤120 LOC ceiling = split-valve trigger; if exceeded, carve at build.**
- [X] T014 [US4] Validate template config-validity (gitleaks provisioned per T002): `gitleaks detect --config=.gitleaks.toml.adopter-template` → assert no config error (FR-286.2).
- [X] T015 [US4] Extend the **existing** `docs/standards/PRECOMMIT_HOOKS.md §9 "Adopter customization"` (modify, not create — §9 already exists) with a subsection pointing to the template with usage instructions + a single-line `README.md` Security cross-ref (FR-286.3).

---

## Phase 7: Polish & Cross-Cutting

- [X] T016 Split-valve final confirmation: re-measure `.gitleaks.toml.adopter-template` LOC (≤120?), confirm T010 stayed throwaway (no new committed harness), and total effort (≤3.0 d?); record the final carve-in/carve-out determination for `/aod.deliver`.
- [X] T017 [P] Regression sweep: run `tests/fixtures/gitleaks-rule-interaction/run.sh` (16/16) + `pre-commit run --all-files` (0 findings) to confirm the #285/#286 gitleaks work introduced no fixture regression.
- [X] T018 Final AC/SC sweep: verify AC-1..AC-7 and SC-1..SC-5; confirm `tachi permissions-verify` is green on clean `main` (US-1 scenario 4) and the doc-greps match the live byte-exact headings.

---

## Dependencies & Execution Order

**Story completion order (by dependency, not priority)**: US1 (#281) ∥ US4-authoring (#286) → US3 (#285) → US2 (#287).

```
T001 (baseline) ─┐
                 ├─▶ T002 (provision gitleaks) ─▶ T010 ─▶ T011 ─▶ T007 ─▶ T009  (critical path: #285 catalog → #287 cadence)
                 │                              └─▶ T014                    T008 [P]
T003 ─▶ T004 ─▶ T005 ─▶ T006  (#281 US1 — fully independent, off critical path)
T013 (#286 template) ─▶ T014 (validate) ─▶ T015 (docs)
                                                    └─▶ T016 ─▶ T017 ─▶ T018 (polish)
```

- **Critical path**: T001 → T002 → T010 → T011 → T007 → T009 (baseline → provision → probe → catalog → cadence → ADR wiring).
- **#281 (US1)** is independent of gitleaks — runs fully parallel; it is the MVP and lands first.
- **Cross-phase dependency**: T007 (US2) depends on T011 (US3) — the one place priority order (US2 before US3) and build order (US3 before US2) diverge.

## Parallel Execution Waves

- **Wave 1** (no deps): T001, T002 [P], T003→T006 (#281 US1 chain), T013 (#286 template authoring).
- **Wave 2** (after T002): T010→T011→T012 (#285 catalog), T014 (#286 validation), T015 (#286 docs).
- **Wave 3** (after T011): T007 (#287 cadence), T008 [P] (issue template), T009 (ADR wiring).
- **Wave 4** (polish): T016, T017 [P], T018.

## Implementation Strategy

- **MVP = US1 (#281) alone** — delivers SC-1 (the load-bearing hardening gate). Shippable independently if the rest slips.
- **Incremental**: US1 → US3 (#285 catalog) → US2 (#287 cadence, consumes catalog) → US4 (#286 template, parallel).
- **Build-time split-valve**: if #285/#286 balloon (T013 >120 LOC or T010 needs a committed harness), carve them to `F-5-enhancements`; ship #281+#287 core.

## Task Summary

- **Total**: 18 tasks (T001–T018).
- **By story**: US1 (#281) 4 · US2 (#287) 3 · US3 (#285) 3 · US4 (#286) 3 · Setup/Foundational 2 · Polish 3.
- **Parallel-eligible [P]**: T002, T003, T008, T013, T017.
- **MVP scope**: T001–T006 (US1 = #281).
- **Split decision**: CARVE-IN (triggers don't fire; #287↔#285 coupling decisive) — build-time fallback retained.
