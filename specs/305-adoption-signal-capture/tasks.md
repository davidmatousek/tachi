---
triad:
  pm_signoff:
    agent: product-manager
    date: 2026-06-01
    status: APPROVED_WITH_CONCERNS
    notes: "0 BLOCKING / 0 HIGH / 1 MEDIUM / 3 LOW. All 6 PM areas PASS: US1-US5 fully delivered with [US#] traceability; FR-001..012 + SC-001..009 mapped with zero gaps; SC-010 correctly a non-gate (measurability assertion); no scope creep (all 6 Out-of-Scope items honored, README cross-link stays a one-liner); T018 acceptance gate covers FR-008/009 over all public artifacts incl. the system-design append; T019 preserves feat(305): + release-please verification. MEDIUM = confirmation of the outreach-sequencing carry-forward resolution (T017 tone-gate + T020 >=3 discrete owner-assigned sends with a hard recipients-logged-in-#305 close check), not a new defect. Full review .aod/results/product-manager.md."
  architect_signoff:
    agent: architect
    date: 2026-06-01
    status: APPROVED_WITH_CONCERNS
    notes: "0 BLOCKING / 0 HIGH / 1 MEDIUM / 3 LOW. Dependency graph acyclic + correctly ordered (T004->T003 same-file; T007->merged T003+T011; T019->T018 gate = merge boundary; T020->merged template+T017; T021->T007+T013); no false [P] (all disjoint files/surfaces); in-repo vs post-merge split correct; all 4 carried decisions live-verified vs repo+GitHub API (D1 pin accounting global 3/4 unchanged + issue 0->1/3, D4 signal-log distinct subsection, MEDIUM-1 README scan, FR-012 no-code/no-ADR); docs-only DoD (waves_tested:0 + skip_reason; not in CI paths filter) + gitignore guards sound. MEDIUM (FOLDED into T018): scan the Step-6 system-design README PROSE not just the Data-Flow node set for buyer-signal/BLP-03 framing (structural half already remediated in the committed diff). L-1 T018 explicit predecessor set (FOLDED), L-2/L-3 already in wording. Full review .aod/results/architect.md."
  techlead_signoff:
    agent: team-lead
    date: 2026-06-01
    status: APPROVED_WITH_CONCERNS
    notes: "0 BLOCKING / 0 HIGH / 0 MEDIUM / 2 LOW. All 6 dimensions PASS: 21 tasks right-sized with authoring/verification split + full FR/SC traceability (no orphans); critical path correctly human-judgment-weighted (T017 tone-gate + T018 privacy/neutrality pass + T020 prospect-selection are schedule-determining, NOT file volume); in-repo authoring wave maximally parallel (T003/T006/T009/T011/T015/T016/T017), T004 correctly serialized after T003; CALENDAR independently verified via cal+date - today Mon 2026-06-01, window Tue 06-02 -> Mon 06-08 all weekdays, NO hard-asserted build date so the #292 weekend-placement defect cannot recur; M-1/M-2 outreach sequenced as discrete owner-assigned tasks with a hard recipients-logged-in-#305 close check so T021 cannot stall; capacity clear (only draft #306 open; F-1/F-2 both CLOSED). LOW-1 build-time weekday discipline reminder (no change), LOW-2 T021 dependency-list nit (FOLDED). Full review .aod/results/team-lead.md."
---

# Tasks: Adoption Signal Capture (F-3, BLP-04 Wave 3)

**Input**: Design documents from `specs/305-adoption-signal-capture/`
**Prerequisites**: plan.md ✓ (PM + Architect signed), spec.md ✓ (PM signed), research.md, data-model.md, quickstart.md

**Tests**: This is a **docs + GitHub platform-config feature with no application code**. Per the docs-only DoD (Constitution Principle VII §Exceptions; KB Entry 4), there are **no automated test tasks** — verification is **manual inspection** (in-repo) + **post-merge attestation** (platform/outreach). Verification tasks below are `[MANUAL-ONLY]`. Record `waves_tested: 0` with an explicit `skip_reason` in `test-results/summary.json` at build (not a silent skip).

**Organization**: Tasks are grouped by user story. Phase numbering follows spec priority (US1/US2/US3 = P1, US4 = P2, US5 = P3); the real execution order is **in-repo authoring + pre-merge acceptance gate → merge → post-merge platform config + outreach → close-out** (plan Phases A→F). `[POST-MERGE]` marks actions that run at/after the squash-merge.

## Format: `[ID] [P?] [Story] Description`
- **[P]**: Can run in parallel (different files/surfaces, no dependency on an incomplete task)
- **[Story]**: US1–US5 (maps to spec user stories)
- **[POST-MERGE]**: executes at or after the PR squash-merge
- **[MANUAL-ONLY]**: manual inspection / platform / outreach action (no automation possible)

---

## Phase 1: Setup

**Purpose**: Create the new docs surface.

- [X] T001 Create the `docs/adopters/` directory (on branch `305-adoption-signal-capture`).

---

## Phase 2: Foundational (pre-merge guard)

**Purpose**: Confirm the repo-cleanliness precondition that the internal signal-log work depends on.

- [X] T002 Verify `_internal/` is gitignored (`git check-ignore _internal/` returns a match; `git ls-files _internal/` is empty) — structural guard for FR-006/SC-009.

**Checkpoint**: Surface ready; gitignore guarantee confirmed. In-repo authoring can proceed.

---

## Phase 3: User Story 1 — Self-serve submission path (Priority: P1) MVP

**Goal**: A structured, self-serve case-study template with a required consent block.

**Independent Test**: Open `docs/adopters/case-study-template.md`; confirm every production-use field is present, required/optional are marked, and a consent grant is captured at submission.

- [X] T003 [P] [US1] Author `docs/adopters/case-study-template.md` — required sections (adopter org/identifier, scale of use, integration point, capabilities used, outcomes) + optional sections (logo, pull-quote, external public-reference link), with required vs optional clearly marked (FR-001). Match docs/standards house style (HTML-comment header).
- [X] T004 [US1] Add the required **Consent block** to the template (publish org name? yes/anonymized/no · use logo? yes/no · preferred attribution + contact) with an explicit **default-deny** note: absent a `yes`, nothing identifying is published (FR-002). Depends on T003.
- [X] T005 [US1] [MANUAL-ONLY] Verify the template has all 5 required + 3 optional sections and the consent block with all 3 prompts (SC-001, SC-002).

**Checkpoint**: Submission path exists — the keystone artifact.

---

## Phase 4: User Story 2 — Peer-signal channel (Priority: P1)

**Goal**: The existing "In the Wild" Discussions category activated as the adopter-stories channel with a pinned welcome post.

**Independent Test**: A logged-in GitHub user sees "In the Wild" with a pinned welcome post linking to the template + index.

- [X] T006 [P] [US2] Draft the welcome-post content (links to the template + the adopters index; explains how to post an adopter story) in **Issue #305** as a pre-merge draft.
- [ ] T007 [US2] [POST-MERGE] [MANUAL-ONLY] Configure "In the Wild" as the adopter-stories channel: publish the welcome post, apply a **category-level pin** (In-the-Wild's own 0/4 pool — leaves the global 3/4 untouched), and update the category description to point at the template/index (FR-004, plan D1). Record slot accounting: global discussion pins 3/4 (unchanged); In-the-Wild category pins 0→1/4. Depends on T011 + T003 merged (welcome post links to live template + index).
- [ ] T008 [US2] [POST-MERGE] [MANUAL-ONLY] Verify the channel is live, the welcome post is pinned, and its links resolve (SC-004).

**Checkpoint**: Peer-signal surface live; no global pin slot consumed.

---

## Phase 5: User Story 3 — Inbound ledger (Priority: P1)

**Goal**: A uniform, append-only internal signal log priming initiative-level adoption tracking.

**Independent Test**: Add one entry to the gitignored signal log in canonical shape; confirm `git status` shows no `_internal/` path.

- [X] T009 [P] [US3] Add an append-only **signal-log subsection** to `_internal/strategy/BLP-03-signed-updates.md` under its own clearly-delimited heading (distinct from the existing 2-condition "Re-evaluation log" table — no schema overload), primed with ≥1 entry in canonical shape **date · source · signal-type · decision** where `signal-type ∈ {inquiry, citation, procurement-mention, traffic, adopter-story}` (FR-006, plan D4). Gitignored — never committed. Keep entries positioning-neutral.
- [X] T010 [US3] [MANUAL-ONLY] Verify the entry follows the canonical four-field shape with a closed-enum signal-type, the subsection is distinct from the re-eval table, and `git status` shows no `_internal/` path (SC-007, SC-009).

**Checkpoint**: Capture half of the feature is live (local, private).

---

## Phase 6: User Story 4 — Procurement validation (Priority: P2)

**Goal**: A discoverable adopters index tying the template + channel together, with a valid empty state.

**Independent Test**: Land on `docs/adopters/README.md`; the "How to submit" pointer routes to the template + channel; the empty state renders.

- [X] T011 [P] [US4] Author `docs/adopters/README.md` — an accepted-case-study list with an explicit, non-broken **empty state** at launch + a "How to submit" pointer routing to `case-study-template.md` and the "In the Wild" channel (FR-003). Renders correctly on GitHub.
- [X] T012 [US4] [MANUAL-ONLY] Verify the index renders, all internal links resolve, and the empty state is valid (SC-003).

**Checkpoint**: Discovery surface complete.

---

## Phase 7: User Story 5 — AIVSS release watch (Priority: P3)

**Goal**: The AIVSS v1.0 release watch is tracked and visible on Issue #168.

**Independent Test**: Issue #168 carries a partial-scope tracking comment and is pinned.

- [ ] T013 [US5] [POST-MERGE] [MANUAL-ONLY] Add a partial-scope AIVSS v1.0 tracking comment to Issue #168 (watch covered here; technical evaluation is a separate future initiative; reference Feature 143 / ADR-024 for continuity) and apply an **issue pin** (FR-010). Record issue-pin 0→1/3.
- [ ] T014 [US5] [POST-MERGE] [MANUAL-ONLY] Verify #168 carries the comment and is pinned (SC-006).

**Checkpoint**: Watch warm and visible.

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Release framing, the pre-merge acceptance gate, outreach, merge, and close-out.

- [X] T015 [P] Add a `CHANGELOG.md` entry under a sibling `### … (BLP-04 Wave 3)` heading describing the adopter case-study + signal-capture infrastructure, `feat(305):` framing (FR-007, SC-008).
- [X] T016 [P] *(optional)* Augment the existing README §Community "In the Wild" line to also point at `docs/adopters/` — **do not add a duplicate In-the-Wild link** (Architect LOW-3).
- [X] T017 Draft the warm outreach message in **Issue #305** (soft "here's what shipped" framing, no ask/CTA — memory `user_linkedin_voice.md`) and pass a named **tone-review gate** against the house voice before any send (FR-005 template, R2). Single source: Issue #305 only (plan D7) — not duplicated in-repo.
- [ ] T018 **[ACCEPTANCE GATE — pre-merge] [MANUAL-ONLY]** Privacy/consent pass (FR-008) + positioning-neutrality scan (FR-009) over **all** public artifacts — `docs/adopters/*`, the `CHANGELOG.md` entry, the README cross-link, **and the Step-6 auto-appended `docs/architecture/01_system_design/README.md` Feature-305 section** (Architect MEDIUM-1 / PM L-3). Confirm: no adopter identity without a consent grant; no commercial/pricing/competitor/buyer-signal/BLP-03 framing in any public surface — for the system-design 305 section, scan **both the Data Flow diagram AND the surrounding prose** (the strategic "why" stays in the gitignored log + specs/ plan, never the public architecture doc) (Architect M-1); the public Data Flow excludes the private `_internal`/recipient nodes; the diff contains **no application code and no new `docs/architecture/02_ADRs/` file** (FR-012); `git status` shows no `_internal/` path. **Gate to mark PR ready.**
- [ ] T019 [POST-MERGE] Mark PR #306 ready → squash-merge as `feat(305): …` → verify a release-please PR opens within ~30s (`gh pr list --state open --search "release-please"`); if it skips, push an empty `feat(305):` marker commit (F-212 fallback) (plan D6, memory `feedback_aod_deliver_release_gate.md`).
- [ ] T020 [POST-MERGE] [MANUAL-ONLY] Select ≥3 **previously-engaged** contacts (enumerable rule: prior Discussion comment / prior issue or PR / direct reply to a tachi post / prior logged inbound — **no cold or first-degree-network sends**), send the tone-reviewed message, and log recipients **privately in Issue #305** (already-public handles only; never private contact details) (FR-005, SC-005).
- [ ] T021 [POST-MERGE] [MANUAL-ONLY] Close Issue #305 with deliverable URLs (template, index, channel) + the `_internal/` signal-log cross-link recorded (FR-011, SC-009).

---

## Dependencies & Execution Order

### Real execution order (plan Phases A→F)

1. **In-repo authoring (pre-merge, parallelizable)**: T001 → T002 → {T003→T004, T011, T009, T015, T016, T006, T017} can proceed together (different files/surfaces).
2. **Pre-merge acceptance gate**: T018 (privacy/consent + positioning-neutrality over all public artifacts incl. the system-design append) + the in-repo verification checks T005, T010, T012. **Gates the PR-ready.**
3. **Merge + release**: T019 (mark ready, squash-merge `feat(305):`, verify release-please).
4. **Post-merge platform + outreach**: T007/T008 (channel), T013/T014 (AIVSS), T020 (outreach sends).
5. **Close-out**: T021 (close #305).

### Key dependencies

- T004 depends on T003 (same file).
- T007 (welcome post + pin) depends on T003 + T011 being **merged** (the post links to the live template + index).
- T020 (outreach sends) depends on T003/T011 merged (the message links to the live template) and T017 (tone-reviewed message).
- T018 (acceptance gate) depends on all public-artifact authoring complete: T003/T004 (template), T011 (index), T015 (CHANGELOG), T016 (README cross-link) + the Step-6 system-design README section (Architect L-1 — explicit predecessor set).
- T019 depends on T018 (acceptance gate passes before PR ready).
- T021 depends on the deliverable URLs from T007 (channel) + T013 (AIVSS) existing, plus the merged template/index (T003/T011 via T019) and the T009 `_internal/` cross-link — all part of the close-comment payload (Team-Lead L-2: content already specified in T021).
- US3 (T009/T010) is fully independent — local + gitignored.

### Parallel opportunities

- **In-repo authoring wave**: T003, T006, T009, T011, T015, T016, T017 — all different files/surfaces, runnable together.
- Verification tasks (T005, T010, T012) run as soon as their authoring task completes.
- Post-merge platform tasks T007, T013 are independent of each other.

---

## Implementation Strategy

### MVP (in-repo, mergeable)

The mergeable MVP is the **in-repo infrastructure**: T001–T005 (template + consent), T011/T012 (index), T009/T010 (signal log), T015 (CHANGELOG), T018 (acceptance gate). This is a complete, valid deliverable on its own — the platform/outreach tail layers activation on top.

### Post-merge activation tail (exogenous-adjacent)

T007/T008 (channel), T013/T014 (AIVSS), T020 (outreach sends), T021 (close-out). Per the plan, **F-3 closes on endogenous SC-001…SC-009**; the actual case-study/≥3-signal *capture* (SC-010) is exogenous (R1) and is **not** a close gate. The ≥3 outreach *sends* (T020) are endogenous (controllable) and are a close item, executed in the post-merge tail with a hard "recipients logged in #305" acceptance check (PM M-1 sequencing note).

### Definition of Done (docs-only)

- No automated tests apply (not in CI `paths:` filter; no code). Record `waves_tested: 0` + `skip_reason` (Constitution VII §Exceptions) at build.
- All FR Given/When/Then ACs verified manually (in-repo at build; platform/outreach at deliver).
- Post-merge release-please verification (T019) + F-212 fallback.

---

## Notes

- `[P]` = different files/surfaces, no dependency on an incomplete task.
- `[Story]` label maps each task to its spec user story for traceability.
- The internal signal log (T009) is gitignored — never committed; verify `git status` is clean of `_internal/` after.
- Commit in-repo artifacts in logical groups; the post-merge tail is tracked via Issue #305 + the delivery doc.
- FR coverage: FR-001→T003, FR-002→T004, FR-003→T011, FR-004→T006/T007, FR-005→T017/T020, FR-006→T009, FR-007→T015, FR-008→T018, FR-009→T018, FR-010→T013, FR-011→T021, FR-012→T018. SC coverage: SC-001/002→T005, SC-003→T012, SC-004→T008, SC-005→T020, SC-006→T014, SC-007→T010, SC-008→T015, SC-009→T010/T018/T021, SC-010 = measurability assertion (not a gate).
