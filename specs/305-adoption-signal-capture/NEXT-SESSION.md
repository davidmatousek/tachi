# NEXT SESSION — Feature 305 (Adoption Signal Capture, BLP-04 Wave 3)

**Generated**: 2026-06-01 (Mon) at the 3-wave standalone build ceiling
**Branch**: `305-adoption-signal-capture` | **Draft PR**: [#306](https://github.com/davidmatousek/tachi/pull/306) (`feat(305):` title ✓)
**Build status**: **PARTIAL** — Waves 0–2 of 7 complete (13/21 tasks, 62%). NOT delivered. Resume at **Wave 3**.

---

## What's complete (Waves 0–2 — in-repo MVP, verified + tone-gated)

| Wave | Tasks | Result |
|------|-------|--------|
| 0 — Setup & Foundational Guard | T001, T002 | `docs/adopters/` created; Gate A passed (`_internal/` gitignored, 0 tracked files). |
| 1 — In-Repo Authoring | T003, T004, T006, T009, T011, T015, T016, T017 | Template + consent block, adopters index, CHANGELOG entry, README cross-link, gitignored signal-log subsection, welcome-post draft (#305), outreach-message draft (#305). |
| 2 — Verification + Tone Gate | T005, T010, T012, **Gate B** | Tester PASS (3/3, 12/12 sub-criteria); Gate B tone-review PASS (PM). |

**Committed + pushed** to the draft PR branch this session. `git status` clean of any `_internal/` path (gitignore guarantee verified).

### Artifacts produced
- `docs/adopters/case-study-template.md` — 5 required + 3 optional sections + required consent block (default-deny).
- `docs/adopters/README.md` — index with "How to submit" pointer + valid empty state.
- `CHANGELOG.md` — `### Adopter case-study + adoption-signal infrastructure (BLP-04 Wave 3)` under `## Unreleased`.
- `README.md` — §Community "In the Wild" line augmented to also point at `docs/adopters/` (no duplicate link).
- `_internal/strategy/BLP-03-signed-updates.md` — **GITIGNORED** "Adoption signal log (BLP-04 F-3)" subsection, distinct from the Re-evaluation log, primed with 1 genuine entry (@north-echo, `adopter-story`).
- Issue **#305** comments: T006 welcome-post draft + T017 outreach-message draft (with recipient-log scaffold).

---

## Next Actions (resume here)

> Run `/aod.build 305` in a fresh session — Step 1 auto-detects Waves 0–2 complete and resumes at Wave 3. (`/aod.build 305 --orchestrated` lifts the 3-wave ceiling if you want to drive all remaining waves in one session.)

### Wave 3 — Pre-Merge Acceptance Gate (HARD GATE → PR-ready) — **T018**
Co-owned by `security-analyst` + `product-manager` + `architect`. Scan **all** public artifacts (template, index, CHANGELOG entry, README cross-link) **AND the Step-6 auto-appended `docs/architecture/01_system_design/README.md` Feature-305 section** (prose AND Data-Flow diagram — Architect MEDIUM-1):
- **Privacy/consent (FR-008)**: no adopter identity without a consent grant; public Data Flow excludes the private `_internal` log + Issue-#305 recipient nodes; `git status` shows no `_internal/` path.
- **Positioning-neutrality (FR-009)**: no commercial/pricing/competitor/buyer-signal/BLP-03 framing in any public surface.
- **FR-012**: diff has no application code and no new `docs/architecture/02_ADRs/` file.
- **NOTE**: the Step-6 `01_system_design/README.md` 305 section is auto-appended during the final-validation/doc step. If it does not yet exist, it must be created **privacy-abstracted** (private nodes out of the published Data Flow, no buyer-signal prose) and then scanned — it is in T018's predecessor set.

### Wave 4 — Merge + Release — **T019** (`devops`) **[maintainer]**
Mark PR #306 ready → squash-merge as `feat(305): …` → verify a release-please PR opens within ~30s (`gh pr list --state open --search "release-please"`). If it skips, push an empty `feat(305):` marker commit (F-212 fallback). **Weekday only** (see calendar guard).

### Wave 5 — Post-Merge Platform & Outreach Tail **[maintainer-executed]**
Independent pairs; run in parallel:
- **T007/T008** (`senior-backend-engineer` + `tester`): publish the welcome post in "In the Wild", apply a **category-level pin** (In-the-Wild's own 0→1/4 pool; global pins stay 3/4), update the category description. Verify live + pinned + links resolve.
- **T013/T014** (`senior-backend-engineer` + `tester`): post the AIVSS v1.0 partial-scope tracking comment on **Issue #168** + apply an **issue pin** (0→1/3). Reference Feature 143 / ADR-024. Verify.
- **T020** (`senior-backend-engineer` **[maintainer sends]**): select ≥3 **previously-engaged** contacts (enumerable rule — prior Discussion comment / prior issue or PR / direct reply to a tachi post / prior logged inbound; NO cold or first-degree-network sends), send the tone-reviewed message, log recipients in #305 (public handles only). Gate E: hard "recipients-logged-in-#305" check.

### Wave 6 — Close-Out — **T021** (`team-lead`) **[maintainer]**
Close Issue #305 with deliverable URLs (template, index, channel) + the `_internal/` signal-log cross-link.

---

## Prerequisites / context for resume

- **Maintainer-executed rows** (T007, T013, T019 merge, T020): require a human with repo-admin rights and a real GitHub identity for platform clicks and the actual outreach sends. The named agent owns the content/verification logic; the maintainer performs the click-through / send.
- **Calendar guard**: today is Mon 2026-06-01. Keep merge (T019) and platform/outreach (Wave 5) on **weekdays only** — Sat 06-06 / Sun 06-07 are excluded (avoids the #292 weekend-placement defect). Outer bound Mon 06-08. No build date is hard-asserted anywhere.
- **Close gate**: F-3 closes on **endogenous SC-001…SC-009**. The ≥3 outreach *sends* (T020) are endogenous and ARE a close item. Actual case-study/≥3-inbound *capture* (SC-010) is **exogenous** (R1) and is NOT a close gate.
- **Then**: `/aod.deliver 305` (mark PR ready, release verification) → `/aod.document`.
- **Test posture**: docs-only DoD — `waves_tested: 0` recorded in `test-results/summary.json` with explicit skip_reason (not a silent skip). No automated tests apply.

## Resume prompt
```
claude "Resume Feature 305 (Adoption Signal Capture) implementation (branch: 305-adoption-signal-capture). Waves 0-2 complete (in-repo MVP authored + verified + tone-gated, committed + pushed to draft PR #306). Run /aod.build 305 to continue at Wave 3 — the pre-merge acceptance gate (T018)."
```
