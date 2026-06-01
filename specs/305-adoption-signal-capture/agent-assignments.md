# Agent Assignments: Adoption Signal Capture (Feature 305, BLP-04 Wave 3)

**Feature ID**: 305-adoption-signal-capture
**Branch**: `305-adoption-signal-capture`
**Source tasks**: `specs/305-adoption-signal-capture/tasks.md` (21 tasks T001–T021, 8 phases)
**Feasibility**: APPROVED_WITH_CONCERNS (Triad triple sign-off complete: PM + Architect + Team-Lead, 2026-06-01)
**Generated**: 2026-06-01 (Mon) by team-lead
**Agent registry**: `.claude/agents/_README.md` — all agent names below are exact registry entries.

---

## Feasibility Status

| Dimension | Assessment |
|-----------|------------|
| Effort | Low volume. Docs + GitHub platform-config feature, **no application code**. ~6 in-repo authoring artifacts + 5 manual verifications + post-merge platform/outreach tail. |
| Capacity | Clear. Only draft Issue #306 open; BLP-04 F-1 (#296) and F-2 (#302) both CLOSED. No agent overloaded. |
| Timeline | **Review-bound, not volume-bound.** Schedule-determining items are human-judgment gates (T017 tone gate, T018 privacy/positioning gate, T020 prospect selection) — not file count. ~2–3 weekday envelope. |
| Dependencies | Acyclic, verified by Architect. T004→T003 (same file); T007→merged T003+T011; T018→all public-artifact authoring; T019→T018 (merge boundary); T020→merged template+T017; T021→T007+T013. |

**Verdict**: FEASIBLE. Proceed via the in-repo authoring wave → pre-merge acceptance gate → merge → post-merge platform/outreach tail → close-out sequence.

---

## Agent Assignment Matrix

Each task maps to one **exact** registry agent. Authoring of markdown/docs/CHANGELOG and message-text drafting → `senior-backend-engineer` (the registry's general implementation agent for non-UI repo content). Manual inspection/acceptance verification → `tester`. The privacy/positioning acceptance gate (T018) is co-owned: `security-analyst` (privacy/consent, FR-008) + `product-manager` (positioning-neutrality, FR-009) + `architect` (system-design-doc prose/diagram scan, MEDIUM-1). Release/merge mechanics → `devops`. Governance close-out → `team-lead`.

> **Maintainer-owned note**: Several `[POST-MERGE] [MANUAL-ONLY]` actions are inherently **human/maintainer** operations — GitHub Discussions/issue platform configuration (T007, T013), pin application, and the *act of sending* outreach + selecting real prospects (T020) require a human with repo-admin rights and a real GitHub identity. The agent named on each such row owns the **content/verification logic**; the maintainer performs the platform click-through and the send. This is flagged inline as **(maintainer-executed)**.

| Task | Tags | Story | Agent (exact registry name) | One-line rationale |
|------|------|-------|------------------------------|--------------------|
| T001 | — | Setup | `senior-backend-engineer` | Create `docs/adopters/` directory on branch — trivial repo scaffolding, implementation agent. |
| T002 | — | Foundational | `tester` | Structural guard verification: `git check-ignore` / `git ls-files` on `_internal/` — a pass/fail inspection. |
| T003 | [P] | US1 | `senior-backend-engineer` | Author `case-study-template.md` (markdown authoring to house style) — keystone artifact. |
| T004 | — | US1 | `senior-backend-engineer` | Add Consent block to the template (same file as T003) — serialized after T003, same author. |
| T005 | [MANUAL-ONLY] | US1 | `tester` | Verify 5 required + 3 optional sections + 3 consent prompts (SC-001/002) — acceptance inspection. |
| T006 | [P] | US2 | `senior-backend-engineer` | Draft welcome-post **content** in Issue #305 (text authoring; pre-merge draft) — message drafting. |
| T007 | [POST-MERGE] [MANUAL-ONLY] | US2 | `senior-backend-engineer` **(maintainer-executed)** | Configure "In the Wild" channel + category-pin + publish welcome post. Agent owns description/post content + slot-accounting logic; maintainer applies the platform pin. |
| T008 | [POST-MERGE] [MANUAL-ONLY] | US2 | `tester` | Verify channel live, post pinned, links resolve (SC-004) — post-merge attestation. |
| T009 | [P] | US3 | `senior-backend-engineer` | Add append-only signal-log subsection to gitignored `_internal/strategy/BLP-03-signed-updates.md` (canonical 4-field shape) — local file authoring. |
| T010 | [MANUAL-ONLY] | US3 | `tester` | Verify canonical four-field shape, closed-enum signal-type, distinct subsection, clean `git status` (SC-007/009) — inspection. |
| T011 | [P] | US4 | `senior-backend-engineer` | Author `docs/adopters/README.md` index with valid empty state + "How to submit" pointer (FR-003) — markdown authoring. |
| T012 | [MANUAL-ONLY] | US4 | `tester` | Verify index renders, links resolve, empty state valid (SC-003) — acceptance inspection. |
| T013 | [POST-MERGE] [MANUAL-ONLY] | US5 | `senior-backend-engineer` **(maintainer-executed)** | Add AIVSS v1.0 partial-scope tracking comment to Issue #168 + issue-pin. Agent drafts the comment text + continuity references; maintainer posts + pins. |
| T014 | [POST-MERGE] [MANUAL-ONLY] | US5 | `tester` | Verify #168 carries comment + is pinned (SC-006) — post-merge attestation. |
| T015 | [P] | Polish | `senior-backend-engineer` | Add `CHANGELOG.md` entry under sibling `### … (BLP-04 Wave 3)` heading, `feat(305):` framing (FR-007/SC-008) — docs authoring. |
| T016 | [P] | Polish | `senior-backend-engineer` | Augment existing README §Community "In the Wild" line to point at `docs/adopters/` (no duplicate link) — docs edit. |
| T017 | — | Polish | `senior-backend-engineer` | Draft warm outreach message text in Issue #305 (soft framing, no CTA) — message authoring. **Tone-review gate** co-owned below (see Quality Gates). |
| T018 | [ACCEPTANCE GATE — pre-merge] [MANUAL-ONLY] | Polish | `security-analyst` + `product-manager` + `architect` | **Pre-merge gate.** `security-analyst` runs the privacy/consent pass (FR-008: no adopter identity without consent grant, no `_internal`/recipient nodes, clean `git status`). `product-manager` runs positioning-neutrality (FR-009: no commercial/pricing/competitor/buyer-signal/BLP-03 framing) + FR-012 (no app code, no new ADR). `architect` scans the Step-6 auto-appended `docs/architecture/01_system_design/README.md` Feature-305 section — **both the Data Flow diagram AND the surrounding prose** (MEDIUM-1). |
| T019 | [POST-MERGE] | Polish | `devops` | Mark PR #306 ready → squash-merge `feat(305): …` → verify release-please PR within ~30s; push empty `feat(305):` marker if it skips (F-212 fallback). Release/merge mechanics = devops execution scope. |
| T020 | [POST-MERGE] [MANUAL-ONLY] | Polish | `senior-backend-engineer` **(maintainer-executed)** | Select ≥3 previously-engaged contacts (enumerable rule), send the tone-reviewed message, log recipients privately in #305. Agent owns the enumerable-prospect logic + recipient-log structure; maintainer performs the sends and applies human judgment on prospect selection (schedule-determining). |
| T021 | [POST-MERGE] [MANUAL-ONLY] | Polish | `team-lead` | Close Issue #305 with deliverable URLs (template, index, channel) + `_internal/` signal-log cross-link (FR-011/SC-009) — governance close-out. |

**Agent roster used (all from `.claude/agents/_README.md`)**: `senior-backend-engineer`, `tester`, `security-analyst`, `product-manager`, `architect`, `devops`, `team-lead`. (7 distinct agents; no invented labels.)

---

## Parallel Execution Waves

Grouped by dependency. The in-repo authoring wave (Wave 1) is **maximally parallel** — all distinct files/surfaces. Verifications attach as soon as their authoring task lands. The merge boundary (T019) is the hard pre-merge/post-merge divider.

### Wave 0 — Setup & Foundational Guard (sequential prereq)
| Task | Agent | Notes |
|------|-------|-------|
| T001 | `senior-backend-engineer` | Create `docs/adopters/` directory. |
| T002 | `tester` | Confirm `_internal/` gitignored (guard for FR-006/SC-009). |

**Runnable together** (T001 and T002 are independent), but both must complete before Wave 1 file authoring.

### Wave 1 — In-Repo Authoring (MAXIMALLY PARALLEL, pre-merge)
All distinct files/surfaces — run together per tasks.md §Parallel opportunities.
| Task | [P] | Agent | Surface |
|------|-----|-------|---------|
| T003 | [P] | `senior-backend-engineer` | `docs/adopters/case-study-template.md` |
| T006 | [P] | `senior-backend-engineer` | Issue #305 (welcome-post draft) |
| T009 | [P] | `senior-backend-engineer` | `_internal/strategy/BLP-03-signed-updates.md` (gitignored) |
| T011 | [P] | `senior-backend-engineer` | `docs/adopters/README.md` |
| T015 | [P] | `senior-backend-engineer` | `CHANGELOG.md` |
| T016 | [P] | `senior-backend-engineer` | `README.md` §Community |
| T017 | [P] | `senior-backend-engineer` | Issue #305 (outreach message draft) |

**Serial dependent (runs immediately after T003 in-wave):**
| Task | Agent | Surface |
|------|-------|---------|
| T004 | `senior-backend-engineer` | Consent block — same file as T003 (`case-study-template.md`); must follow T003. |

### Wave 2 — In-Repo Verification + Tone Gate (pre-acceptance)
Each verification runs as soon as its authoring task completes; all complete before T018.
| Task | Agent | Validates |
|------|-------|-----------|
| T005 | `tester` | Template sections + consent prompts (SC-001/002). |
| T010 | `tester` | Signal-log canonical shape + clean `git status` (SC-007/009). |
| T012 | `tester` | Index renders + empty state (SC-003). |
| T017 tone-review gate | `product-manager` | Named tone-review of the T017 message against house voice (FR-005 template, R2) before any send is permitted. See Gate B. |

### Wave 3 — Pre-Merge Acceptance Gate (HARD GATE → PR-ready)
| Task | Agents | Scope |
|------|--------|-------|
| T018 | `security-analyst` + `product-manager` + `architect` | Privacy/consent (FR-008) + positioning-neutrality (FR-009) + FR-012 + system-design-doc prose/diagram scan (MEDIUM-1) over **all** public artifacts. **Gates marking PR ready.** See Gate C. |

### Wave 4 — Merge + Release (boundary)
| Task | Agent | Action |
|------|-------|--------|
| T019 | `devops` | Mark PR #306 ready → squash-merge `feat(305): …` → verify release-please PR (F-212 fallback if skipped). |

### Wave 5 — Post-Merge Platform & Outreach Tail (parallel where independent)
T007/T008 (channel) and T013/T014 (AIVSS) are independent of each other and run in parallel. T020 needs the merged template (via T019) + the tone-reviewed message (T017).
| Task | Agent | Action |
|------|-------|--------|
| T007 | `senior-backend-engineer` **(maintainer-executed)** | Configure "In the Wild" channel + category-pin + publish welcome post (global 3/4 pins untouched; category 0→1/4). |
| T008 | `tester` | Verify channel live + pinned + links (SC-004). |
| T013 | `senior-backend-engineer` **(maintainer-executed)** | AIVSS v1.0 tracking comment on #168 + issue-pin (0→1/3). |
| T014 | `tester` | Verify #168 comment + pin (SC-006). |
| T020 | `senior-backend-engineer` **(maintainer-executed)** | ≥3 previously-engaged contacts, send tone-reviewed message, log recipients in #305 (FR-005/SC-005). |

### Wave 6 — Close-Out
| Task | Agent | Action |
|------|-------|--------|
| T021 | `team-lead` | Close Issue #305 with deliverable URLs + `_internal/` signal-log cross-link (FR-011/SC-009). Depends on T007 + T013 deliverable URLs + merged template/index (via T019) + T009 cross-link. |

**Wave count: 7** (Wave 0 through Wave 6).

---

## Quality Gates Between Waves

| Gate | After Wave | Owner(s) | Pass Criteria | Blocks |
|------|-----------|----------|---------------|--------|
| **Gate A — Foundational** | Wave 0 | `tester` | `git check-ignore _internal/` matches AND `git ls-files _internal/` empty. | Wave 1 (T009 signal-log work) |
| **Gate B — Tone Review** | Wave 2 | `product-manager` | T017 message passes named tone-review vs house voice (soft "here's what shipped", **no ask/CTA**, no em dashes/semicolons/mid-colons per `user_linkedin_voice.md`). | T020 sends (no send before pass) |
| **Gate C — Acceptance Gate (PRE-MERGE, HARD)** | Wave 3 | `security-analyst` + `product-manager` + `architect` | **(1) Privacy/consent** (`security-analyst`): no adopter identity without a consent grant; public Data Flow excludes private `_internal`/recipient nodes; `git status` shows no `_internal/` path. **(2) Positioning-neutrality** (`product-manager`): no commercial/pricing/competitor/buyer-signal/BLP-03 framing in any public surface; FR-012 — diff has **no application code and no new `docs/architecture/02_ADRs/` file**. **(3) System-design scan** (`architect`): the Step-6 auto-appended `docs/architecture/01_system_design/README.md` Feature-305 section is clean in **both the Data Flow diagram AND the surrounding prose** (MEDIUM-1). Predecessor set complete: T003/T004, T011, T015, T016 + the Step-6 system-design section. | **Marking PR #306 ready** (Wave 4) — nothing merges until all three pass. |
| **Gate D — Release Verification** | Wave 4 | `devops` | PR squash-merged as `feat(305): …`; a release-please PR opens within ~30s (`gh pr list --state open --search "release-please"`). If skipped → empty `feat(305):` marker commit pushed (F-212 fallback). | Adopter-visible release (post-merge tail proceeds regardless; this gate guards SemVer visibility). |
| **Gate E — Outreach Close Check** | Wave 5 | `team-lead` | ≥3 discrete owner-assigned sends complete (T020) AND recipients logged privately in Issue #305 (public handles only). Hard "recipients-logged-in-#305" check so T021 cannot stall (PM M-1 sequencing). | Wave 6 close-out (T021) |

---

## Time Estimates Per Wave

Docs/platform-config feature — **review-bound, not volume-bound**. Authoring artifacts are small; the schedule is driven by human-judgment gates (Gate B tone review, Gate C acceptance, T020 prospect selection) and platform/outreach actions that require a maintainer.

**Calendar discipline**: Today is **Mon 2026-06-01**. Window = **Tue 06-02 → Mon 06-08**, all weekdays. **06-06 (Sat) and 06-07 (Sun) are weekends — no merge, no outreach, no platform config on those days** (avoids the #292 weekend-placement defect). Outer bound: **Mon 06-08**.

| Wave | Work | Estimate | Target Day(s) |
|------|------|----------|---------------|
| Wave 0 | Setup + foundational guard | ~10 min | Mon 06-01 |
| Wave 1 | In-repo authoring (7 parallel + T004 serial) | ~1.5–2.5 hrs (parallel) | Mon 06-01 → Tue 06-02 |
| Wave 2 | Verifications + tone-review gate | ~30–45 min | Tue 06-02 |
| Wave 3 | Acceptance gate (3 reviewers, may parallel via context-fork) | ~30–45 min | Tue 06-02 → Wed 06-03 |
| Wave 4 | Merge + release verification | ~15 min | Wed 06-03 (weekday) |
| Wave 5 | Post-merge platform + outreach tail | ~1–2 hrs active; gated by maintainer availability + prospect judgment | Wed 06-03 → Thu 06-04 (weekday sends only) |
| Wave 6 | Close-out (#305) | ~10 min | Thu 06-04 |

**Envelope**:
- **Optimistic**: 1.5 weekdays — all in-repo work Mon, gate + merge + tail Tue–Wed. Close Wed 06-03.
- **Realistic**: 2–3 weekdays — authoring Mon/Tue, gate Tue/Wed, merge Wed, outreach Thu. Close **Thu 06-04**.
- **Pessimistic**: bounded by **Mon 06-08** — if tone-review iterates or prospect selection slips, the weekend (06-06/06-07) is skipped and outreach + close-out land Mon 06-08. **Never Sat/Sun.**

**Confidence**: HIGH on in-repo waves (deterministic, low volume). MEDIUM on Wave 5 (maintainer-executed platform + outreach, human-judgment-gated, exogenous-adjacent). No hard-asserted build date is encoded anywhere, so the weekend-placement defect cannot recur.

---

## Handoff to Orchestrator

- **Feasibility**: APPROVED (with documented concerns; triple sign-off complete).
- **tasks.md**: `specs/305-adoption-signal-capture/tasks.md`.
- **Wave strategy**: 7 waves (Wave 0 setup → Wave 1 maximally-parallel authoring → Wave 2 verify + tone gate → Wave 3 hard acceptance gate → Wave 4 merge/release → Wave 5 post-merge platform/outreach → Wave 6 close-out).
- **Critical gate**: Gate C (T018) is the **pre-merge hard gate** co-owned by `security-analyst` + `product-manager` + `architect`. Nothing merges until all three pass over **all** public artifacts including the Step-6 system-design README append (prose + diagram).
- **Maintainer-executed rows**: T007, T013, T020 require a human with repo-admin + a real GitHub identity for the platform click-through and outreach sends; the named agent owns the content/verification logic.
- **Calendar guard**: keep merge (T019) and outreach/platform (Wave 5) on weekdays only; outer bound Mon 06-08.
