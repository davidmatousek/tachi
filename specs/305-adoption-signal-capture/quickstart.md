# Quickstart: Adoption Signal Capture (F-3, BLP-04 Wave 3)

**Feature**: 305 | **Date**: 2026-06-01 | **Plan**: [plan.md](./plan.md)

This feature ships **receiving infrastructure**. Below are the three usage flows it enables and the manual verification checklist that stands in for automated tests (docs-only DoD — Constitution Principle VII §Exceptions).

---

## Flow 1 — An adopter submits a case study

1. Adopter opens `docs/adopters/case-study-template.md` (linked from the adopters index and the "In the Wild" welcome post).
2. They fill the required sections (org/identifier, scale, integration point, capabilities used, outcomes) and any optional fields (logo, pull-quote, public-reference link).
3. They complete the **Consent block**: publish org name? (yes/anonymized/no), use logo? (yes/no), attribution + contact.
4. They submit (PR against `docs/adopters/`, or a post in the "In the Wild" Discussions category).
5. The maintainer lists the accepted case study in `docs/adopters/README.md` **only as the consent grant permits** (name or anonymized; logo only if granted).

> Default-deny: absent an explicit `yes`, no identifying field is published.

---

## Flow 2 — The maintainer logs an inbound signal

1. An inbound signal arrives (an inquiry, a citation, a procurement-checklist mention, a traffic spike, or an adopter story).
2. The maintainer appends one row to the **signal-log subsection** of `_internal/strategy/BLP-03-signed-updates.md` (gitignored) in canonical shape:
   `date · source · signal-type · decision` — where `signal-type ∈ {inquiry, citation, procurement-mention, traffic, adopter-story}`.
3. The entry is append-only and positioning-neutral. It never enters a commit.

---

## Flow 3 — The maintainer activates the channel + watch (one-time, manual)

1. Author a welcome post in the existing **"In the Wild"** Discussions category linking to the template + index.
2. Apply a **category-level pin** to the welcome post (In-the-Wild's own pin pool — leaves the global 3/4 untouched) and update the category description to point at the submission path.
3. On **Issue #168**, add a partial-scope comment (AIVSS *watch* covered here; evaluation is a separate future initiative) and apply an **issue pin**.
4. Run the warm outreach round: select ≥3 previously-engaged contacts, pass the tone-review gate, send, and log recipients privately in Issue #305.

---

## Manual Verification Checklist (stands in for automated tests)

Run at the appropriate stage; `[BUILD]` = checkable in-repo before merge, `[DELIVER]` = platform/outreach action verified at close-out.

**In-repo (`[BUILD]`)**
- [ ] `docs/adopters/case-study-template.md` exists; all 5 required sections present + marked required; optional sections marked optional. (SC-001)
- [ ] Template Consent block present with all 3 prompts; default-deny stated. (SC-002)
- [ ] `docs/adopters/README.md` exists; "How to submit" links to template + "In the Wild" channel; valid empty state renders. (SC-003)
- [ ] `CHANGELOG.md` has a `feat(305):`-framed entry under a `### … (BLP-04 Wave 3)` heading. (SC-008)
- [ ] Positioning-neutrality scan: no commercial/pricing/competitor/buyer-signal framing in any public artifact (matches only in guard/out-of-scope framing). (FR-009)
- [ ] `git status` shows **no** `_internal/` path on the feature branch. (SC-009)
- [ ] Feature diff: no application code, no new `docs/architecture/02_ADRs/` file. (FR-012)

**Internal (`[BUILD]`, local only)**
- [ ] Signal-log subsection exists in `_internal/strategy/BLP-03-signed-updates.md` with ≥1 entry in canonical shape, distinct from the re-evaluation-log table. (SC-007)

**Platform / outreach (`[DELIVER]`, `[MANUAL-ONLY]`)**
- [ ] "In the Wild" is the adopter-stories channel with a pinned welcome post linking to template + index; pin slot accounting recorded (global 3/4 unchanged; category 0→1/4). (SC-004)
- [ ] ≥3 soft outreach messages sent to previously-engaged contacts (enumerable rule); recipients logged privately in Issue #305. (SC-005)
- [ ] Issue #168 carries the AIVSS partial-scope comment and is pinned (issue pin 0→1/3). (SC-006)
- [ ] Issue #305 closed with deliverable URLs (template, index, channel) + `_internal/` cross-link. (SC-009)
- [ ] Post-merge: a release-please PR opened after the `feat(305):` squash-merge (F-212 marker-commit fallback if not). (D6)

**Close gate**: F-3 closes on **SC-001…SC-009** (endogenous). SC-010 (an actual case study captured OR ≥3 inbound signals) is a measurability assertion, **not** a close gate — it is exogenous (R1).
