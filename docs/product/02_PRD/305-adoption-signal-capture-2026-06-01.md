---
prd:
  number: 305
  topic: adoption-signal-capture
  created: 2026-06-01
  status: Approved
  type: feature
triad:
  pm_signoff: {agent: product-manager, date: 2026-06-01, status: APPROVED_WITH_CONCERNS, notes: "0 BLOCKING / 0 HIGH / 3 MEDIUM / 4 LOW. All 6 PM focus areas PASS: 5/5 Issue #305 stories preserved + AC-enriched (Skill Step 1b satisfied), template complete, consent discipline is default-private/publish-on-consent (strongest part of the doc), positioning-neutrality verified EMPIRICALLY (commercial-vocab scan vs _internal/CLAUDE.md privacy table = every match in guard/Out-of-scope framing, zero leak), scope tight, Q1/Q6 sound. 3 MEDIUM folded inline: M-1 (BLP-03 bare-repo link → plain text; codename is an established public label across ~20 docs/ files, so link-hygiene not a leak); M-2 (added a required Consent block to FR-1 so NFR-1 is self-enforcing at submission, not a manual maintainer gate); M-3 (softened Problem-stmt gap-3 + US-4 to adopter-neutral purpose — a public reader needn't know which deferred internal initiative the ledger feeds; the internal tie stays in the gitignored log). PM-RESOLVED Q1 = reuse 'In the Wild' + Q6 = feat(305):. Full review .aod/results/product-manager.md."}
  architect_signoff: {agent: architect, date: 2026-06-01, status: APPROVED_WITH_CONCERNS, notes: "0 BLOCKING / 0 HIGH / 3 MEDIUM / 4 LOW. ALL 4 mandated current-state claims VERIFIED ACCURATE against the live repo (docs/adopters absent; 'In the Wild' exists — 7-category enum verbatim-correct; #168 OPEN; _internal/ gitignored at .gitignore:198 with 0 tracked files = structurally guaranteed, not merely intended) plus spot-checks (F-1/F-2 closure, v4.37.0, BLP-03 file already carries a re-evaluation-log table). Zero inaccuracies — cleanest possible factual result. No-ADR call CONFIRMED correct (no hidden architectural decision; Q6 is a rules-note-or-nothing per existing git-workflow.md; #302 precedent). 3 MEDIUM (all plan-resolvable; folded for accuracy): M-1 (GitHub 4-pinned-discussions ceiling already at 3/4 — welcome-pin takes the last slot → FR-3/Q5 pin-budget note); M-2 (NFR-4 mis-mechanized — pins are server-side state, not commit-bound → NFR-4 reframed to slot-pressure/un-pin risk); M-3 (signal-log column-schema vs the existing table → FR-6 signal-type enum + Q3 drift-guard). Reuse-'In the Wild' and single-branch both sound. Full review .aod/results/architect.md."}
  techlead_signoff: {agent: team-lead, date: 2026-06-01, status: APPROVED_WITH_CONCERNS, notes: "0 BLOCKING / 0 HIGH / 3 MEDIUM / 4 LOW. CALENDAR PASS — independent cal 6/2026 verification; today 2026-06-01 is Monday; no concrete build date asserted (correctly deferred to /aod.tasks) so the #292 weekend-defect cannot recur; the window lands Tue 06-02 -> Mon 06-08, all weekdays. CAPACITY CLEAR — 0 open PRs project-wide; F-1 #296 CLOSED 05-30 16:02, F-2 #302 CLOSED 06-01 12:28 (v4.37.0, so no cadence pressure on F-3); 5 stale local branches = optional housekeeping. 3 MEDIUM (plan-time; folded as sharpened carry-forward): M-1 (the ~2-3d envelope holds via human-judgment work — warm-prospect selection + tone-review — not file volume → Timeline note + privacy pass as explicit acceptance step); M-2 (SC-10 reframed as a measurability assertion, NOT an F-3 close gate — F-3 closes on SC-1..SC-9 endogenous, avoiding an un-closeable exogenous trap); M-3 (outreach needs an enumerable 'previously-engaged' rule + a named tone-review gate vs David's house voice → Q4 sharpened). L-2 signal-type enum folded into FR-6. Effort=7 / ~2-3d realistic-to-generous. Full review .aod/results/team-lead.md."}
source:
  idea_id: 305
  story_id: null
---

# F-3 — Adoption Signal Capture (BLP-04 Wave 3): Product Requirements Document

**Status**: Approved (MEDIUM concerns folded inline; residual plan-stage items → `/aod.plan`)
**Created**: 2026-06-01
**Spec**: TBD (will land at `specs/305-adoption-signal-capture/spec.md` after `/aod.plan`)
**Author**: product-manager
**Reviewers**: architect, team-lead
**Phase**: BLP-04 Adoption Push, Wave 3 (Adoption Signal Capture)
**Priority**: P1
**Parent Initiative**: BLP-04 Adoption Push (4-feature initiative; F-1 [#296](https://github.com/davidmatousek/tachi/issues/296) CLOSED 2026-05-30, F-2 [#302](https://github.com/davidmatousek/tachi/issues/302) CLOSED 2026-06-01)
**Source**: Seed Issue [#305](https://github.com/davidmatousek/tachi/issues/305) (captured 2026-06-01; pre-vetted in the BLP-04 blueprint Wave-3 planning, 2026-05-28)
**Related**: Issue [#168](https://github.com/davidmatousek/tachi/issues/168) (AIVSS v1.0 + first-adopter tracking, OPEN)
**ICE**: 22 (Impact 8, Confidence 7, Effort 7)

---

## 📋 Executive Summary

### The One-Liner

Build the **receiving infrastructure** — a structured adopter case-study template, a `docs/adopters/` index, a dedicated public Discussions channel for adopter stories, a soft-outreach round to previously-engaged prospects, AIVSS-release tracking, and an internal append-only signal log — so the inbound generated by F-1's 50/50-coverage launch and F-2's asset-tag follow-up is **captured and structured** instead of evaporating as unmeasured noise.

### Problem Statement

F-1 ([#296](https://github.com/davidmatousek/tachi/issues/296), 50/50 OWASP coverage distribution) and F-2 ([#302](https://github.com/davidmatousek/tachi/issues/302), asset-tag output wiring) pushed tachi's positioning onto multiple public surfaces — README hero, OWASP coverage doc, evergreen poster, LinkedIn, a refreshed GitHub profile, and a v4.37.0 release with community credit. That distribution generates inbound: page views, stars, Discussion engagement, prospect inquiries, citations, and the occasional production adopter. **tachi has no structured way to ingest any of it.**

Concretely, four gaps:

1. **No submission path.** An adopter who wants to say "we run tachi in production" has nowhere to do it — no template, no index, no clear channel.
2. **No peer-signal surface.** A prospect evaluating tachi for procurement cannot see whether *anyone else* uses it. Social proof is invisible.
3. **No inbound ledger.** Citations, inquiries, and procurement-checklist appearances arrive scattered across email, DMs, and threads, with no single place to log them — so "is adoption happening?" is unanswerable, and there is no evidence base to inform when the next hardening initiative should be prioritized.
4. **No AIVSS tracking.** OWASP's AIVSS v1.0 (which tachi already evaluated in Feature 143, ADR-024) ships on its own timeline; there is no pinned watch so tachi's response stays timely.

The cost is asymmetric: distribution is the expensive, already-spent investment (F-1 + F-2). Without cheap receiving infrastructure, even a launch that lands well produces **no durable, structured evidence of adoption** — the signal decays in inboxes and feeds.

### Proposed Solution

A **single feature branch** delivers the in-repo docs/template files; the remaining items are out-of-repo or platform-config actions tracked in Issue #305:

1. **`docs/adopters/case-study-template.md`** — a structured template: adopter org, scale of use, integration point, capabilities used, outcomes, and optional logo/quote/link.
2. **`docs/adopters/README.md`** — an index of accepted case studies plus a clear "How to submit" pointer.
3. **A dedicated public Discussions channel** for adopter stories. ⚠️ **Reconciliation required**: the blueprint (2026-05-28) assumed no such category existed and planned a new "Adopter stories" category. As of 2026-06-01 the repo **already has an "In the Wild" category** (alongside Q&A, Feature Requests, Ideas & RFCs, Announcements, Integrations, Threat Model Patterns). "In the Wild" is the conventional OSS adopter-sighting channel — so the likely correct action is **reuse + pin a welcome post**, not create a redundant category. Decision deferred to Open Question Q1.
4. **Outreach script** — a short, warm follow-up template (DM / email / LinkedIn reply) sent to **≥3 previously-engaged** prospects (not cold contacts). Recipients logged privately in Issue #305.
5. **AIVSS v1.0 tracking** — a partial-scope comment on Issue [#168](https://github.com/davidmatousek/tachi/issues/168) confirming F-3 covers the watch (not the evaluation), plus a pin.
6. **Internal append-only signal log** — a section in the **gitignored `_internal/` strategic workspace** (BLP-03 re-evaluation log) that records each inbound signal in a uniform shape (date · source · signal-type · decision), priming initiative-level tracking.

The deliverable is *receiving infrastructure*, not content. Actual case-study text is co-authored later, when an adopter surfaces.

### Scope

**In Scope (this feature)**:
- `docs/adopters/case-study-template.md` (structured submission template)
- `docs/adopters/README.md` (index + "How to submit")
- Adopter-stories Discussions channel — **reuse "In the Wild"** (default per Q1) or create "Adopter stories"; pinned welcome post either way
- Outreach script (in-repo template) + **≥3 soft outreach messages sent** out-of-repo (recipients logged privately in Issue #305)
- AIVSS v1.0 partial-scope tracking comment on Issue #168 + Issue pinned
- Internal signal-log section primed with **≥1 entry** in canonical shape (gitignored `_internal/`)
- `CHANGELOG.md` entry (release framing per Q6)
- Issue #305 closed with deliverable + channel URLs

**Out of Scope (deferred / belongs elsewhere)**:
- ❌ **Actual case-study content** — F-3 builds the *receiving* infrastructure; case studies are co-authored when adopters surface (also tracked by Issue #168's "first adopter case study").
- ❌ **Full outreach campaign** — soft outreach only (≥3 warm contacts); cold pitching, ad spend, and acquisition campaigns are out.
- ❌ **AIVSS v1.0 technical evaluation** — tracking/watch only; a future evaluation initiative opens when AIVSS v1.0 actually ships.
- ❌ **Commercial / pricing / tier positioning** — BLP-04 is OSS-track only; commercial positioning lives outside this repo.
- ❌ **README / documentation overhaul** — adopters docs are new and self-contained; no structural docs rewrite.
- ❌ **MAESTRO 7-layer matrix polish** — that is F-4 (Issue #98), the independent Wave-4 feature.

---

## 🎯 User Stories

> Job-Story format (Intercom). Preserved verbatim-in-substance from Issue #305.

**US-1 — Submission path (maintainer)**
**When** an adopter reaches out wanting to share their experience, **I want** a structured case-study template, **so** they have a clear, self-serve submission path instead of an ad-hoc email thread.
*AC*: Given the template file exists, when a prospective contributor opens it, then every field needed to convey production use (org, scale, integration point, capabilities, outcomes, optional logo/quote/link) is present and labeled required vs optional.

**US-2 — Peer channel (adopter)**
**When** I use tachi in production and want to tell others, **I want** a dedicated public Discussions channel, **so** other prospective adopters can find peer signal without contacting me privately.
*AC*: Given the adopter-stories channel is live, when a logged-in GitHub user visits Discussions, then the channel is publicly visible and a pinned welcome post explains how to post an adopter story or link a case study.

**US-3 — Procurement validation (prospect)**
**When** I evaluate tachi for procurement, **I want** to see ≥1 case study (or adopter story) confirming production use, **so** the tool carries external validation, not just self-description.
*AC*: Given the adopters index and channel exist, when a prospect lands on `docs/adopters/README.md` or the channel, then the submission path and any captured stories are discoverable in one place.

**US-4 — Inbound ledger (maintainer)**
**When** an inbound signal arrives (inquiry, citation, procurement-checklist appearance), **I want** to log it in one place in a consistent shape, **so** initiative-level adoption tracking becomes decidable rather than aspirational (is adoption happening, and should the next hardening initiative be prioritized).
*AC*: Given the internal signal-log section exists, when a signal is logged, then it follows the canonical shape (date · source · signal-type · decision) and lives only in the gitignored `_internal/` workspace.

**US-5 — AIVSS watch (OWASP-ecosystem participant)**
**When** OWASP releases AIVSS v1.0, **I want** the release tracked, **so** tachi's response is timely (Feature 143 already evaluated AIVSS; F-3 keeps the watch warm).
*AC*: Given Issue #168, when F-3 closes, then #168 carries a partial-scope comment (watch covered here; evaluation is a separate future initiative) and is pinned.

---

## ✅ Functional Requirements

**FR-1 — Case-study template** (`docs/adopters/case-study-template.md`): structured markdown with required sections (adopter org/identifier, scale of use, integration point, capabilities used, outcomes) and optional sections (logo, pull-quote, external link). Required vs optional clearly marked. Includes a frontmatter or header block so submissions are uniform. **Consent block (required)**: an explicit permission section — *may we publish your org name?* (yes / anonymized / no); *may we use your logo?* (yes / no); *preferred attribution + contact* — so consent (NFR-1) is captured **at submission**, not enforced manually after the fact (the most likely breach is an over-eager publish of a submission that never granted name/logo rights).

**FR-2 — Adopters index** (`docs/adopters/README.md`): lists accepted case studies (empty-state acceptable at launch) and a "How to submit" pointer that routes to the template + the Discussions channel. Renders correctly on GitHub.

**FR-3 — Adopter-stories Discussions channel**: a public, lightly-moderated channel with a pinned welcome post. **Resolved (Q1): reuse the existing "In the Wild" category** — do not create a redundant "Adopter stories" category. Welcome post links to the template and the adopters index. **Pin-budget note**: GitHub caps pinned discussions at 4/repo and 3 are already pinned (#176/#177/#178), so a global welcome-pin takes the last slot (4/4, zero headroom); the plan (Q5) chooses deliberately between a global pin (record 4/4 accounting) and a category-level guidelines/description surface that consumes no global slot.

**FR-4 — Outreach script + round**: an in-repo (or Issue-tracked) short message template for warm follow-up; **≥3 messages sent** to previously-engaged prospects. The script embeds a self-serve link to the template so recipients can submit without further coordination. Recipient identities logged **privately** in Issue #305 (never published without consent).

**FR-5 — AIVSS tracking**: partial-scope comment on Issue #168 (watch covered; evaluation out of scope) + Issue pinned so the watch is visible.

**FR-6 — Internal signal log**: an append-only section in the gitignored `_internal/` strategic workspace, primed with ≥1 entry. Every entry uses the canonical shape: **date · source · signal-type · decision**, where `signal-type` is a small **closed vocabulary** (e.g. `inquiry | citation | procurement-mention | traffic | adopter-story`) so the ledger stays mechanical, not interpretive (NFR-6). Q3 pins whether this is a new distinct subsection or folds into the existing re-evaluation-log table already in that file, to prevent column-schema drift.

**FR-7 — CHANGELOG entry**: a `CHANGELOG.md` entry describing the new adopter case-study + signal-capture infrastructure. Conventional-commit prefix (`feat:` vs `docs:`) decided in Q6.

**FR-8 — Privacy guard**: no adopter names, orgs, or logos published in public docs/channels without explicit consent; outreach recipient list stays private to the Issue.

---

## 🚧 Non-Functional Requirements

**NFR-1 — Privacy / consent (hard)**: adopter identities and outreach recipients are private by default; publication requires explicit consent. This is the dominant NFR — getting it wrong is a trust-and-reputation failure, not a cosmetic one.

**NFR-2 — Repo cleanliness / no leakage (hard)**: the internal signal log lives only in the gitignored `_internal/` workspace; `_internal/` must never appear in `git status` for a public commit. Public docs carry **no commercial, pricing, or buyer-signal framing** (OSS-track discipline).

**NFR-3 — Template completeness**: the template captures, in a single pass, everything an adopter needs to convey production use — so a respondent never has to come back for "we also need X."

**NFR-4 — Persistence**: pins are **server-side GitHub state, persistent until manually changed** — orthogonal to git commits. The real risks are (a) the GitHub **4-pinned-discussions-per-repo ceiling** (currently 3/4 used; the welcome post would take the last slot — see FR-3/Q5) and (b) accidental un-pin by other workflow activity (the issue-pin pool is 0/3, so the #168 pin has ample headroom). Verification targets *those*: confirm pins present at delivery + record pin-slot accounting — not "survives a commit," which tests nothing.

**NFR-5 — Low-friction submission**: a respondent who receives the outreach can self-serve from link → template → submission with no further coordination round-trip.

**NFR-6 — Format consistency**: signal-log entries are uniform in shape across time so the ledger is scannable and the gating decision is mechanical, not interpretive.

---

## 🎯 Success Criteria

- **SC-1**: `docs/adopters/case-study-template.md` merged to main with all required sections present and required/optional fields marked.
- **SC-2**: `docs/adopters/README.md` merged with a working "How to submit" pointer to the template + channel.
- **SC-3**: Adopter-stories Discussions channel live (reused or created per Q1) with a pinned welcome post that renders correctly and links to the template.
- **SC-4**: ≥3 soft outreach messages sent to previously-engaged prospects; recipients logged privately in Issue #305.
- **SC-5**: Issue #168 carries the AIVSS v1.0 partial-scope tracking comment and is pinned.
- **SC-6**: Internal signal-log section exists with ≥1 entry in canonical shape (date · source · signal-type · decision), in the gitignored `_internal/` workspace.
- **SC-7**: `CHANGELOG.md` entry present with the Q6-decided prefix.
- **SC-8**: Issue #305 closed with deliverable URLs (template, index, channel) + `_internal/` cross-link recorded.
- **SC-9**: No PII or commercial framing in public docs; `git status` shows no `_internal/` path on the feature branch.
- **SC-10** *(measurability assertion, NOT an F-3 close gate)*: the BLP-04 DoD line "≥1 case study captured OR ≥3 documented inbound signals" becomes *mechanically evaluable* once this infra exists. **F-3 closes on SC-1…SC-9** (all endogenous, all closeable in-window) — capturing an actual case study or ≥3 signals is exogenous (R1) and must NOT gate F-3 closure.

---

## ❓ Open Questions (Architect/PM-Owned, Resolve in `/aod.plan`)

- **Q1 (RESOLVED at define — PM + Architect concur) — Discussions channel**: **reuse the existing "In the Wild" category** (verified present); do NOT create a redundant "Adopter stories" category (it would fragment signal — R4 — and add to an already-7-category list). Remaining plan detail is Q5 (pin mechanics). *This reconciles the blueprint's stale "no category exists" research (2026-05-28).*
- **Q2 — Template shape** *(PM)*: one all-in-one template (required core + optional rich fields) vs separate "quick intro" and "full case study" templates? **PM lean: single template** to minimize submission friction (NFR-5).
- **Q3 — Signal-log placement** *(PM)*: the blueprint specifies the BLP-03 re-evaluation log. Confirm the exact `_internal/` file + that the section is append-only and neutrally framed (no commercial detail in any artifact that could be copied outward).
- **Q4 — Outreach scope** *(Team-Lead)*: confirm the ≥3 targets are warm and define an **enumerable "previously-engaged" rule** — a traceable prior interaction with tachi (a Discussion comment, an issue/PR, a direct reply to a tachi post, or a prior inbound already in the log); no cold or first-degree-network sends. Add a **named pre-send tone-review gate** checking the script against David's house voice (soft "here's what shipped," no ask/CTA) before any of the ≥3 go out (R2). Full decomposition at `/aod.tasks`.
- **Q5 — Pin mechanics** *(Architect)*: choose between a global welcome-pin (4/4 ceiling — record slot accounting) and a category-level guidelines surface (consumes no global slot); confirm the Issue #168 pin (issue-pin pool 0/3, ample headroom) and document the pin method. NFR-4 is reframed — the persistence risk is slot-pressure + accidental un-pin, not commit-loss.
- **Q6 (RESOLVED at define — PM + Architect concur) — Release framing**: use **`feat(305):`** — adopters gain a new submission path + Discussions channel (user-visible capability), per `.claude/rules/git-workflow.md`'s "default to `feat:` for user-visible work." No cadence pressure (F-2 shipped v4.37.0 today), so this is a deliberate release-visibility choice, not a cadence fix. **`/aod.deliver` MUST run the post-merge release-please verification** (memory `feedback_aod_deliver_release_gate.md`) to avoid an F-212-style silent skip.

---

## ⚠️ Risks & Mitigations

- **R1 — No inbound after distribution** *(Medium likelihood, Medium impact)*: F-1 + F-2 land but nothing comes back; the template/channel sit empty. *Mitigation*: receiving infra is low-cost standing infrastructure regardless; the signal log is honest about empty state; BLP-03 simply stays deferred (it already is). An empty ledger is a valid, decidable result.
- **R2 — Outreach reads as spam** *(Medium likelihood, High impact on reputation)*: warm-follow-up that lands as a cold pitch damages standing. *Mitigation*: target only previously-engaged contacts; review script tone before sending; soft framing ("here's what shipped"), not solicitation (Q4).
- **R3 — Privacy / consent breach** *(Low likelihood, High impact)*: publishing an adopter name/logo or a recipient list without consent. *Mitigation*: NFR-1 + FR-8 — recipients private to the Issue; publication consent-gated.
- **R4 — Channel proliferation / wrong surface** *(Medium likelihood, Low impact)*: creating a redundant "Adopter stories" category when "In the Wild" already serves the purpose. *Mitigation*: Q1 reconciliation before any category action.
- **R5 — Commercial-framing leak into public docs** *(Low likelihood, High impact)*: buyer-signal / pricing language migrating from the internal log into a public artifact. *Mitigation*: NFR-2 — signal log stays gitignored; public PRD and docs use neutral, adopter-facing language only.
- **R6 — `feat:`-vs-`docs:` ambiguity** *(Low likelihood, Low impact)*: an accidental prefix choice that mis-fires (or fails to fire) a release, echoing F-1's cadence gap. *Mitigation*: Q6 resolved deliberately at `/aod.plan`; release framing is an explicit decision, recorded.

---

## 📅 Estimated Timeline

**Envelope**: ~2–3 working days from `/aod.plan` approval (writing- and config-bound, not code-bound). Precise calendar scheduling and weekend-placement verification are the Team-Lead's at `/aod.tasks`. **The envelope holds because of human-judgment work, not file volume**: file-authoring is hours, but warm-prospect selection (≥3) and outreach-script tone-review (R2) are think-time, and the privacy/consent pass (NFR-1) is a review gate on every public artifact — so `/aod.plan` should decompose into file-authoring / prospect-selection + tone-review / platform-actions / close-out, with the consent pass as an explicit acceptance step.

- **Define**: 2026-06-01 (Mon, today) — this PRD.
- **Plan → Build → Deliver**: sequenced over the following ~2–3 weekdays.
- **No hard external deadline**: unlike F-2 (which carried a 2026-06-11 cadence-restoration deadline), F-2 already restored `feat:` cadence with v4.37.0 on 2026-06-01. F-3 has **no cadence pressure**, so timing is preference, not constraint.
- **Exogenous tail**: SC-4 (≥3 messages sent) is bounded; the *responses* those messages generate, and SC-10's case-study capture, are exogenous and explicitly outside the build window.

---

## 🔗 Dependencies

- **F-1 ([#296](https://github.com/davidmatousek/tachi/issues/296))** — CLOSED 2026-05-30. Distribution traffic source; the template/channel without inbound is a dead document, so F-1 must precede. ✅ satisfied.
- **F-2 ([#302](https://github.com/davidmatousek/tachi/issues/302))** — CLOSED 2026-06-01. Demonstrates the community-recognition pattern and makes the asset-tag story provable end-to-end. ✅ satisfied.
- **Issue [#168](https://github.com/davidmatousek/tachi/issues/168)** — OPEN. Target of FR-5 (AIVSS tracking comment + pin); partial overlap (AIVSS watch in F-3; case-study production is the exogenous remainder).
- **Existing Discussions infrastructure** — "In the Wild" category already exists (drives Q1). No new platform capability required.
- **No code dependencies**; no external blockers. Single feature branch for the in-repo docs.

```
F-3 (Adoption Signal Capture)
  ├─ Depends on: F-1 #296 (distribution traffic)        ✅ CLOSED
  ├─ Depends on: F-2 #302 (recognition pattern)         ✅ CLOSED
  ├─ Touches:    Issue #168 (AIVSS watch — comment+pin)
  └─ Independent of: F-4 #98 (MAESTRO 7-layer polish)
```

---

## 📌 Governance Notes

- **Workflow**: Feature (parallel Architect + Team-Lead review; PM drafts and finalizes). Standard SDLC Triad.
- **ADR**: **No new ADR** — F-3 is docs + platform-config infrastructure with no architectural decision. (If Q6 escalates the release-policy framing into a durable rule, that is a CLAUDE.md/rules note, not an ADR.)
- **PM sign-off focus**: template field completeness (NFR-3), privacy/consent discipline (NFR-1/FR-8), positioning neutrality (NFR-2), and the Q1 channel decision.
- **Architect sign-off focus**: Discussions category configuration + "In the Wild" reconciliation (Q1/Q5), repo cleanliness / gitignore guarantee (NFR-2), pin persistence (NFR-4).
- **Team-Lead sign-off focus**: outreach scope as *soft* not spam (Q4/R2), signal-log format consistency (NFR-6), and the ~2–3 day timeline with no weekend-placement defects.
- **Privacy boundary**: this PRD is a **public** artifact. The internal adoption-signal log stays in the gitignored `_internal/` workspace; no commercial, pricing, or buyer-signal framing appears in any public surface (per `_internal/` privacy rules).
- **Initiative framing**: F-3 is the third of four BLP-04 waves; closing it leaves only F-4 (MAESTRO 7-layer polish, Issue #98) before initiative-level BLP-04 closure.
