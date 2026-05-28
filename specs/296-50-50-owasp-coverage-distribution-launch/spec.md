---
prd_reference: docs/product/02_PRD/296-50-50-owasp-coverage-distribution-launch-2026-05-28.md
triad:
  pm_signoff:
    agent: product-manager
    date: 2026-05-28
    status: APPROVED
    notes: "0H/0M/2L. Spec.md faithfully translates PRD #296 into a build-ready specification with all 5 PM-deferred concerns resolved at the appropriate locations: US-7 enterprise-buyer persona (P3) + US-8 prospective-contributor folded into FR-003 §f (P3); FR-013 + SC-013 + NFR-005(d) triple-reinforce memory carve-out (PM M-2); NFR-005(c) BLP-04 strategy doc cross-reference timing copy-edited to 'retroactively at F-1 close' (PM M-3); FR-009 material-critique definition pre-decided with 3-condition any-of test plus explicit negation of cosmetic/snarky critique (PM L-2). Tone discipline exemplary — @armorer-labs gap-analysis-commenter framing reinforced at US-5 narrative + AC-2 + AC-3 + FR-005 + Edge Case R5 (NOT 'requester'/'discussion-opener'). Sequencing constraint operationalized via FR-007 + SC-007 + US-6 AC-4 (Architect M2 F-2-ship-by-2026-06-11 + post-close edit rule if F-2 slips). Architect H2 anchor docs/standards/OWASP_COVERAGE.md referenced 8+ times with Wave 0 sequencing. Allowed file set (FR-011/SC-010) extended with INDEX.md, BACKLOG.md, BLP-04 strategy doc. Architect M3 release-please-skip-as-EXPECTED framing captured in Edge Case. 2 LOW findings (SC-014 verify-list restructure; FR-003 §b example-pairing soft framing) are polish-only and may be addressed at /aod.plan without re-review. Full review at .aod/results/product-manager.md."
  architect_signoff: null  # Added by /aod.project-plan
  techlead_signoff: null   # Added by /aod.tasks
---

# Feature Specification: F-1 — 50/50 OWASP Coverage Distribution Launch (BLP-04 Wave 1)

**Feature Branch**: `296-50-50-owasp-coverage-distribution-launch`
**Created**: 2026-05-28
**Status**: Draft
**Input**: User description: "PRD: 296 - 50-50-owasp-coverage-distribution-launch"
**PRD**: [docs/product/02_PRD/296-50-50-owasp-coverage-distribution-launch-2026-05-28.md](../../docs/product/02_PRD/296-50-50-owasp-coverage-distribution-launch-2026-05-28.md)
**Research**: [research.md](research.md)
**Parent Initiative**: BLP-04 Adoption Push (4-feature initiative, PROPOSED 2026-05-28)
**Phase**: BLP-04 Wave 1 (Distribution Launch)

## User Scenarios & Testing *(mandatory)*

### User Story 1 — README Hero OWASP Coverage Block (Priority: P1)

A security architect evaluating threat-modeling tools lands on the tachi `README.md` for the first time. Today, the hero (first viewport, lines 1–16) carries the harness positioning and a get-started line but no OWASP coverage block; the 50/50 claim is buried at line 29 inside the "What is tachi?" body section. The architect wants to see the five-framework coverage block in the first viewport so they can assess fit without reading the full body.

**Why this priority**: Hero placement is the single highest-leverage in-tree surface. Every other artifact (LinkedIn post, Cybersec article, GitHub profile, Discussion #179 close) back-links to the README; if the README hero doesn't carry the claim cleanly, the back-links land on diluted positioning. P1 because all downstream artifacts depend on hero readiness.

**Independent Test**: Render `README.md` on github.com. The first viewport (above the first H2 collapse at `## What is tachi?`, currently line 17) contains a five-framework coverage block listing LLM 2025 / Agentic 2026 / ML 2023 / Mobile 2024 / Web/API 2021/2023 with 10/10 status per framework. The block links to `docs/standards/OWASP_COVERAGE.md` (canonical anchor) and/or a per-baseline `Coverage Attestation` page in `examples/*/sample-report/security-report.pdf`. The block renders without broken anchors, broken links, or truncated tables.

**Acceptance Scenarios**:

1. **Given** the F-1 README hero block is merged, **When** a viewer loads `README.md` on github.com, **Then** the first viewport (above `## What is tachi?` H2) contains a coverage block enumerating all five framework slots — LLM 2025, Agentic 2026, ML 2023, Mobile 2024, Web/API 2021/2023 — each with 10/10 status.
2. **Given** the F-1 README hero block is merged, **When** a viewer reads the Web/API combined-slot cell, **Then** an explicit footnote or per-bucket detail states: "Web/API combined slot: OWASP Web Top 10:2021 (A01–A10) + OWASP API Security Top 10:2023 (API1–API10) — 20 items, 20/20".
3. **Given** the F-1 README hero block is merged, **When** a viewer clicks the canonical-anchor link, **Then** the link resolves to `docs/standards/OWASP_COVERAGE.md` (newly authored at Wave 0) without 404 or broken anchor.
4. **Given** the F-1 README hero block is merged, **When** the maintainer runs `git diff main -- README.md | grep -E "^[+-]" | wc -l`, **Then** the changed-line count is ≤30. If the count exceeds 30, the F-1 close-out commit cites an Architect sign-off in `/aod.plan` covering the increment (FR-011 escape hatch).
5. **Given** the F-1 README hero block is merged, **When** a viewer inspects the existing `brand/posters/2026-05-08-cycle-outcomes-poster.jpg` reference at line 7, **Then** the poster reference is preserved unchanged (no collision with the new hero block).

---

### User Story 2 — LinkedIn Post Closing the Daniel Wood Loop (Priority: P1)

A SecOps practitioner who previously engaged with Daniel Wood's 2026-05-02 enterprise-hardening thread sees a maintainer-authored response thread closing that loop. The practitioner discovers tachi as responsive to community feedback, follows the back-link to the Cybersec article (or the repo), and adds tachi to their evaluation shortlist.

**Why this priority**: LinkedIn is the only published external artifact that converts the BLP-02 community-feedback origin (Daniel Wood thread) into a discoverable distribution surface. Without F-2, the BLP-02 closure (v4.36.0, 2026-05-14) remains a private engineering win. P1 because LinkedIn is time-sensitive (NFR-7 stale-decay) and the BLP-02 audience is warm.

**Independent Test**: The maintainer's LinkedIn feed contains a published post (URL recorded in Issue #296) referencing Daniel Wood's 2026-05-02 thread by name or quoted excerpt with attribution, stating the 50/50 OWASP coverage milestone explicitly, and providing CTA links to the tachi repo + Cybersec article + BLP-02 closure anchor (v4.36.0 release notes or PR #293). The post is dated within the F-1 window (target 2026-05-29 → 2026-06-04, slack to 2026-06-11). The post is published AFTER the Cybersec article PR merges (PRD Q2 lean = (c)).

**Acceptance Scenarios**:

1. **Given** the Cybersec article PR is merged (FR-003 satisfied), **When** the maintainer publishes the LinkedIn post, **Then** the post body contains: (a) a reference to Daniel Wood's 2026-05-02 BLP-02 thread by name or quoted excerpt with attribution, (b) the explicit 50/50 OWASP coverage statement, (c) CTA links to the tachi repo, the Cybersec article, and the BLP-02 closure (v4.36.0 release notes or PR #293).
2. **Given** the LinkedIn post is published, **When** the maintainer records its URL in Issue #296, **Then** the closing comment for Issue #296 includes the LinkedIn URL among the five required artifact URLs.
3. **Given** the LinkedIn post is published, **When** the post format is reviewed against 2026 LinkedIn algorithm patterns ([research.md §4](research.md)), **Then** the post delivers the core insight in the post body (native-content first), reserves the article URL for comments or in-body inline (post author's choice) rather than the "link-in-comments-as-primary-CTA" pattern that 2026 LinkedIn suppresses. **[MANUAL-ONLY]** algorithmic-reach validation is not automatable; maintainer judgment governs.

---

### User Story 3 — Cybersecurity Content Long-Form Article (Priority: P1)

A security researcher or practitioner who follows long-form content in the cybersecurity space discovers a ~3000-word article explaining what tachi's 50/50 OWASP coverage actually means and how to independently verify it. The reader trusts the claim because it ships with a reproducible verification walkthrough using public `tachi.threat-model` runs on worked architectures.

**Why this priority**: The article is the **anchor asset** — LinkedIn + Discussion #179 + README hero all back-link to it. Long-form gets shared, linked, and indexed; short-form competes in noise. P1 because article-merge sequencing gates the LinkedIn post (Q2 lean = (c)) and because long-form is the highest-credibility-per-word surface for the 50/50 claim.

**Independent Test**: A Cybersec Content repo PR exists (URL recorded in Issue #296), merged via self-review after a ≥24-hour hold (NFR-008). Article word count is 2400–3600 (~3000 ±20%) and contains the FR-003 §a–§e sections.

**Acceptance Scenarios**:

1. **Given** the Cybersec article PR is open, **When** the article body is word-counted (excluding YAML frontmatter, footnotes, and reference links), **Then** the count is 2400–3600.
2. **Given** the Cybersec article PR is open, **When** a reviewer inspects §a (framework-by-framework breakdown), **Then** §a contains all 6 separate buckets (LLM 10/10, Agentic 10/10, ML 10/10, Mobile 10/10, Web 10/10, API 10/10 = 60/60 broken down; restated as "five-slot 50/50" with combined Web/API slot made explicit) AND separate per-bucket anchor URLs (LLM 2025, Agentic 2026, ML 2023, Mobile 2024, **Web 2021 separate from API 2023**).
3. **Given** the Cybersec article PR is open, **When** a reviewer follows §b's verification walkthrough, **Then** §b cites 2–3 example architectures from `examples/` (e.g., `examples/web-app/` + `examples/agentic-app/` + one of `examples/predictive-ml-app/` or `examples/mobile-banking-app/` or `examples/maestro-reference/`) and demonstrates the per-framework `Coverage Attestation` page byte-deterministic reproducibility (running `/tachi.security-report` with `SOURCE_DATE_EPOCH=1700000000` set, matching the committed `.baseline` per-page bytes); narrative outputs are NOT used as the reproducibility anchor (Architect M1).
4. **Given** the Cybersec article PR is open, **When** a reviewer inspects §c (coverage matrix table), **Then** §c is derived from `docs/standards/OWASP_COVERAGE.md` (canonical anchor).
5. **Given** the Cybersec article PR is open, **When** a reviewer inspects §d (10/10 framing), **Then** §d explicitly states for each framework: which threats (catalog IDs), which detection agents, which ADRs (ADR-024 → ADR-037 + ADR-045 lineage).
6. **Given** the Cybersec article PR is open, **When** a reviewer inspects §e (closing link), **Then** §e contains a link back to the tachi repo.
7. **Given** the Cybersec article PR is open, **When** a reviewer inspects §f (contribution invitation, US-8), **Then** §f contains a closing paragraph (1–3 sentences) inviting prospective contributors with pointers to Discussions, Issues, and the F-260 / F-292 community-merge precedent.
8. **Given** the Cybersec article PR is open, **When** the maintainer checks the PR open-timestamp against self-merge timestamp, **Then** the delta is ≥24 hours (NFR-008 hold discipline).

---

### User Story 4 — GitHub Profile Flagship Refresh (Priority: P2)

A maintainer or contributor browsing the `davidmatousek/davidmatousek` GitHub profile sees tachi positioned as flagship with the 50/50 OWASP coverage tagline. The visitor discovers tachi via the profile and follows through to the repo.

**Why this priority**: Profile is a passive discovery surface — lower velocity than article or LinkedIn but durable (profile views accumulate over time). P2 because profile refresh is a low-friction, high-durability surface that the maintainer controls fully.

**Independent Test**: The `davidmatousek/davidmatousek` profile README has been updated (PR merged; URL recorded in Issue #296) such that tachi appears in a "flagship project" surface with: (a) the 50/50 OWASP coverage tagline, (b) a brief one-line description (STRIDE+AI threat modeling harness for Claude Code), (c) a link to the tachi repo. AOD-Kit remains visible in a secondary position. Profile renders correctly on github.com.

**Acceptance Scenarios**:

1. **Given** the profile README refresh PR is merged, **When** a viewer loads `github.com/davidmatousek`, **Then** the first viewport contains tachi in a flagship surface with the 50/50 tagline + one-line description + repo link.
2. **Given** the profile README refresh PR is merged, **When** a viewer reads the project ordering, **Then** tachi precedes AOD-Kit; AOD-Kit remains visible in a secondary position (not removed).
3. **Given** the profile README refresh PR is merged, **When** the maintainer checks the PR open-timestamp against self-merge timestamp, **Then** the delta is ≥24 hours (mirror NFR-008 discipline per PRD R4).
4. **Given** the profile README refresh PR is merged, **When** the refresh scope is reviewed against PRD Q7 lean, **Then** the refresh is minimal (flagship project table only; no "Now" section that creates ongoing maintenance burden) unless the maintainer explicitly overrides during `/aod.plan`.

---

### User Story 5 — Discussion #179 Closing with @armorer-labs Attribution (Priority: P2)

The first-time contributor `@armorer-labs`, who surfaced three pattern-catalog gaps via a 2026-05-12 comment on Discussion #179 (discussion **opened by maintainer davidmatousek 2026-04-17**, not by @armorer-labs), learns that their gap-analysis shipped via F-292 (PR #293, v4.36.0, 2026-05-14). The contributor knows the project ships against community asks and that their contribution chain is preserved publicly.

**Why this priority**: Honors the F-260 community-merge precedent and signals to future first-time contributors that the project converts thoughtful gap-analysis into shipped refinements with attribution. Doubles as an in-channel announcement to the BLP-02 community-feedback audience. P2 because the discussion close is independently valuable (separate from the article + LinkedIn surfaces) and time-sensitive within the 7-day SLA.

**Independent Test**: Discussion #179 receives a closing comment within 7 days of PRD sign-off (target 2026-06-04) citing F-292 PR (#293), v4.36.0 release notes anchor, ADR-045 line 133 anchor, and **explicit @armorer-labs gap-analysis attribution** for the three pattern-catalog gaps (vector-filter/search-DSL injection, package-manager/CI-workflow execution sinks, cross-agent handoff sinks). Discussion is closed with status reflecting "shipped". @armorer-labs receives a GitHub notification of the close.

**Acceptance Scenarios**:

1. **Given** the F-1 acceptance window opens at PRD sign-off (2026-05-28), **When** the closing comment is published on Discussion #179, **Then** the close-timestamp is within 7 calendar days of PRD sign-off (≤2026-06-04 23:59 UTC).
2. **Given** the Discussion #179 closing comment is published, **When** a reader inspects the comment body, **Then** the comment contains: (a) the F-292 PR link (#293), (b) the v4.36.0 release notes anchor, (c) the ADR-045 line 133 anchor, (d) explicit `@armorer-labs` attribution for the gap-analysis comment (2026-05-12) — framed as **gap-analysis commenter**, NOT "the requester" — surfacing the three pattern-catalog gaps (vector-filter/search-DSL injection, package-manager/CI-workflow execution sinks, cross-agent handoff sinks), (e) link to the CHANGELOG section attributing @armorer-labs in v4.36.0.
3. **Given** the Discussion #179 closing comment is published, **When** the comment opens with the lead sentence, **Then** the lead sentence attributes @armorer-labs's **gap-analysis comment** explicitly — example wording: "Thanks to @armorer-labs's gap-analysis comment surfacing three pattern-catalog gaps, we shipped F-292" — NOT "Thanks to @armorer-labs's request" (R5 tone discipline).
4. **Given** the Discussion #179 closing comment is published, **When** the discussion is closed via `gh discussion close 179`, **Then** the discussion status is closed with status reflecting "shipped" / "resolved".
5. **Given** the Discussion #179 closing comment is published, **When** `gh discussion view 179 --comments` is queried, **Then** @armorer-labs receives a GitHub notification (verifiable via @-mention rendering).

---

### User Story 6 — F-2 Sequencing Hold (Priority: P2)

The maintainer transitioning from F-1 close to F-2 start observes that F-2 (F-260b @north-echo asset-tag output wiring) remains unstarted until F-1 closes. Writing-voice (F-1) and code-voice (F-2) focus is preserved; the asset-tag announcement gets its own distribution moment without dilution.

**Why this priority**: Process / governance story. Independent of the technical artifacts but essential to honoring BLP-04 §3 Sequencing Discipline. P2 because the sequencing constraint runs throughout the F-1 acceptance window and is enforced via a binary SC check.

**Independent Test**: Between PRD sign-off (2026-05-28) and Issue #296 close timestamp, `git log --all --grep="F-2|F-260b|asset-tag wiring" --since="2026-05-28"` returns zero commits (after carving out false-positive incidental references per Architect L1). No `297-*` (or equivalent) F-2 branch exists in the repo.

**Acceptance Scenarios**:

1. **Given** the F-1 PRD is signed off on 2026-05-28, **When** `git branch --list 297-*` is run before Issue #296 close, **Then** no F-2 branch exists.
2. **Given** the F-1 PRD is signed off on 2026-05-28, **When** `git log --all --grep="F-2|F-260b|asset-tag wiring" --since="2026-05-28"` is run before Issue #296 close, **Then** the result is empty (after human review carves out false-positive matches per Architect L1 — e.g., incidental references in research notes or prior PR discussion).
3. **Given** the F-1 PRD is signed off on 2026-05-28, **When** any `/aod.discover`, `/aod.define`, `/aod.spec`, `/aod.plan`, `/aod.tasks`, or `/aod.build` invocation is attempted for F-2, **Then** the invocation does NOT occur before Issue #296 close timestamp.
4. **Given** Issue #296 closes, **When** F-2 kickoff begins, **Then** F-2 ships `feat:`-prefixed code by **2026-06-11** (Architect M2). If F-2 slips past 2026-06-11, the F-1 close-out comment is updated (post-close edit) to state the new release-cadence-restoration date.

---

### User Story 7 — Enterprise-Buyer BLP-03 Signal (Priority: P3)

An enterprise security buyer evaluating threat-modeling tools for their team encounters tachi via one of the five F-1 surfaces (most likely the article or LinkedIn). The buyer's evaluation triggers an inbound signal (star, watch, issue, discussion comment, or direct contact) that, when aggregated across F-1's distribution window, manufactures the enterprise-buyer signal that gates BLP-03 (signed updates).

**Why this priority**: Process / strategic story. Independent of the technical artifacts but essential to converting "manufactures the BLP-03 enterprise-buyer signal" from PRD strategic claim to a testable AC (PM M-1 resolution). P3 because the signal aggregation happens post-F-1 close in F-3 (BLP-04 Wave 2: adoption signal capture) — F-1's role is to publish the surfaces; F-3's role is to measure inbound.

**Independent Test**: At F-1 `/aod.deliver` close-out, the BLP-04 strategy doc (Q5 lean = author at F-1 close) explicitly records the enterprise-buyer-signal acceptance criteria for BLP-03 trigger (e.g., "≥3 inbound signals across stars/watches/issues/discussions/direct contacts that name enterprise-buyer evaluation context") so F-3 has a concrete signal definition to instrument against.

**Acceptance Scenarios**:

1. **Given** F-1 reaches the `/aod.deliver` close-out, **When** the BLP-04 strategy doc is authored (Q5 lean), **Then** the doc contains a section "Enterprise-buyer signal acceptance criteria" that defines: (a) what counts as an enterprise-buyer signal (≥1 inbound that names enterprise evaluation context, e.g., team/org name, evaluation rubric, SOC2 / FedRAMP / SLSA framing), (b) how the signal is captured (Issue label `signal:enterprise-buyer`, Discussion category, or maintainer-noted DM), (c) the aggregation threshold for BLP-03 trigger (≥3 signals across all 5 F-1 surfaces).
2. **Given** F-1 closes, **When** an enterprise-buyer-evaluating reader engages on any of the 5 F-1 surfaces (article comment, LinkedIn reply, GitHub star/watch/issue/discussion, profile-driven follow), **Then** F-3 (Wave 2: adoption signal capture) — when it launches — instruments against the BLP-04 strategy doc's signal definition. **[MANUAL-ONLY]** signal-capture mechanics are F-3 scope; F-1 only commits the definition.
3. **Given** F-1 closes, **When** the BLP-04 strategy doc is committed, **Then** the doc is referenced from the F-1 close-out commit and from Issue #296 closing comment.

---

### User Story 8 — Prospective Contributor On-Ramp (Priority: P3)

A prospective contributor reading the Cybersec article reaches the §f closing paragraph and sees an explicit invitation to contribute via Discussions, Issues, or the F-260 / F-292 community-merge precedent. The reader knows what shape of contribution converts to merged work.

**Why this priority**: Process / governance story (PM L-1 resolution). Folds into Cybersec article structure (FR-003 §f) rather than a standalone surface. P3 because the contribution invitation is durable and runs in parallel non-blocking with the rest of F-1.

**Independent Test**: The Cybersec article (FR-003) contains a closing §f paragraph (1–3 sentences) inviting prospective contributors with pointers to: (a) Discussions, (b) Issues, (c) the F-260 / F-292 community-merge precedent. The paragraph names the comment-first-give-choice path A default per project memory `feedback_external_contributor_collisions.md`.

**Acceptance Scenarios**:

1. **Given** the Cybersec article is published, **When** a reader reaches §f, **Then** §f contains 1–3 sentences inviting prospective contributors with the three pointers (Discussions, Issues, community-merge precedent) and naming the comment-first-give-choice default.

---

### Edge Cases

- **README hero diff exceeds 30 lines**: FR-011 escape hatch — the increment beyond 30 lines requires Architect sign-off in `/aod.plan`. Cited in the F-1 close-out commit and CHANGELOG entry. (Architect M4)
- **Cybersec article requires 3+ self-review iterations**: NFR-008 hold discipline bounds iteration; if revisions push past 2026-06-11 hard ceiling (NFR-007), scope-reduce to ~2000 words (drop one §) rather than slip the deadline (R3 mitigation).
- **LinkedIn account access disruption** (Day 4 R-edge): `/aod.deliver` shifts to Buffer-2 (Mon 2026-06-08). LinkedIn post URL may be deferred to a follow-up Issue if the disruption extends past 2026-06-11.
- **GitHub profile PR breaks unrelated sections** (R4): one-git-operation revert; retry after restructure with explicit before/after rendering review on github.com.
- **Discussion #179 close steals @armorer-labs's thunder** (R5): tone discipline encoded in US-5 AC-3 lead-sentence framing; CHANGELOG attribution + ADR-045 line 133 + Co-Authored-By trailer preserve attribution chain.
- **Material critique on published article or LinkedIn post** (R1): FR-009 + NFR-003 — correction-in-public (in-thread comment, follow-up Issue, errata section), NOT silent deletion. Pre-decide what counts as "material" (PM L-2): a critique is material if it (a) names a specific framework gap, (b) cites a verifiable counter-example, or (c) attracts ≥5 confirming reactions/replies from independent accounts. Cosmetic/snarky/non-substantive critique does NOT trigger FR-009.
- **F-2 work begins in parallel violating BLP-04 §3** (R7): SC-007 binary verification at F-1 close detects any commit referencing F-2 / F-260b / asset-tag wiring; offending commits are reverted or held until F-1 close.
- **Release-please skip on F-1 PR merge** (Architect M3): this is the **EXPECTED** behavior per `docs:` mapping in release-please-config.json. F-1 close-out MUST verify the absence of a release PR and record it as expected, NOT as a release-please incident requiring the empty-`feat(NNN):` marker-commit recovery flow from F-212.

## Requirements *(mandatory)*

> **Acceptance Criteria Rule**: Each AC must begin with **Given** and follow Given/When/Then structure. Use `[MANUAL-ONLY] <reason>` (reason ≥10 chars) inline to mark ACs that cannot be automated.

### Functional Requirements

- **FR-001**: `README.md` MUST include a hero block in the first viewport (above the `## What is tachi?` H2, currently line 17) listing five OWASP framework slots with 10/10 coverage status: LLM 2025, Agentic 2026, ML 2023, Mobile 2024, Web/API 2021/2023 (combined slot). Insertion point: between line 14 (divider `---`) and line 17 (`## What is tachi?` H2), preserving the existing `brand/posters/2026-05-08-cycle-outcomes-poster.jpg` reference at line 7. The block MUST link to `docs/standards/OWASP_COVERAGE.md` (canonical anchor authored at Wave 0) AND/OR a per-baseline `Coverage Attestation` page in `examples/*/sample-report/security-report.pdf` (byte-deterministic per ADR-021).
- **FR-001a**: The README hero block MUST include a footnote or per-bucket cell making the Web/API combined-slot framing explicit: "Web/API combined slot: OWASP Web Top 10:2021 (A01–A10) + OWASP API Security Top 10:2023 (API1–API10) — 20 items, 20/20." (Architect H1 resolution; pre-empts technically-literate readers who compute 6 buckets × 10 items = 60.)
- **FR-002**: A LinkedIn post MUST be published from the maintainer's LinkedIn (URL recorded in Issue #296) referencing Daniel Wood's 2026-05-02 thread by name or quoted excerpt with attribution, stating the 50/50 OWASP coverage milestone explicitly, providing CTA links to the tachi repo + Cybersec article (FR-003) + BLP-02 closure anchor (v4.36.0 release notes or PR #293). Post format respects 2026 LinkedIn algorithm patterns (native-first content; not link-in-comments-as-primary-CTA per research §4). Post timing: AFTER Cybersec article merges (PRD Q2 lean = (c)).
- **FR-003**: A Cybersecurity Content repo article MUST be published (PR merged via self-review after ≥24-hour hold per NFR-008; URL recorded in Issue #296) at length 2400–3600 words (~3000 ±20%) with sections:
  - **§a** framework-by-framework coverage breakdown with anchor links to OWASP canonical URLs, including separate links for Web 2021 (`https://owasp.org/Top10/`) AND API 2023 (`https://owasp.org/API-Security/`); per-bucket explicit counts (LLM 10/10, Agentic 10/10, ML 10/10, Mobile 10/10, Web 10/10, API 10/10 = 60/60 broken down; restated as "five-slot 50/50" with combined Web/API slot explicit)
  - **§b** verification walkthrough using `tachi.threat-model` / `/tachi.security-report` on 2–3 public `examples/` architectures (e.g., `examples/web-app/` + `examples/agentic-app/` + one of `examples/predictive-ml-app/`, `examples/mobile-banking-app/`, `examples/maestro-reference/`); reproducibility anchored to per-framework `Coverage Attestation` PAGE in `security-report.pdf` (byte-deterministic per ADR-021), NOT narrative outputs (LLM-variable per Architect M1)
  - **§c** coverage matrix table — derived from `docs/standards/OWASP_COVERAGE.md` (canonical anchor; FR-001)
  - **§d** explicit framing of "10/10" per framework — which threats (catalog IDs), which detection agents, which ADRs (ADR-024 → ADR-037 + ADR-045 lineage)
  - **§e** link back to tachi repo
  - **§f** contribution invitation paragraph (US-8; PM L-1 resolution) — 1–3 sentences with pointers to Discussions, Issues, F-260 / F-292 community-merge precedent, naming comment-first-give-choice path A default
- **FR-004**: The `davidmatousek/davidmatousek` GitHub profile README MUST be refreshed (PR merged after ≥24-hour hold mirror of NFR-008; URL recorded in Issue #296) such that tachi appears in a flagship project surface with the 50/50 coverage tagline, brief one-line description (STRIDE+AI threat modeling harness for Claude Code), and link to tachi repo. AOD-Kit MUST remain in a secondary position (not removed; positioned below tachi). Refresh scope: minimal — flagship project table only (PRD Q7 lean = no "Now" section).
- **FR-005**: Discussion #179 MUST receive a closing comment within 7 days of PRD sign-off (≤2026-06-04 23:59 UTC) citing F-292 PR (#293), v4.36.0 release notes anchor, ADR-045 line 133 anchor, and explicit @armorer-labs attribution for the **gap-analysis comment (2026-05-12)** that surfaced three pattern-catalog gaps (vector-filter/search-DSL injection, package-manager/CI-workflow execution sinks, cross-agent handoff sinks). Discussion MUST be closed with status reflecting "shipped". Framing MUST identify @armorer-labs as the **gap-analysis commenter**, NOT "the requester" or "the discussion-opener" (Discussion #179 was opened by maintainer davidmatousek 2026-04-17).
- **FR-006**: CHANGELOG.md MUST include an entry under "Unreleased" for the F-1 work using `docs:` prefix (NOT `feat:` — docs-only). The entry MUST cite Issue #296 and link to the BLP-04 strategy doc once it lands (post-F-1-close cross-reference per Q5 lean; PM M-3 resolution). Subsection example: `### OWASP Coverage Matrix Documentation (F-296)` with 2–3 bullets describing the README hero block + new `docs/standards/OWASP_COVERAGE.md` + cross-link to PRD #296.
- **FR-007 (Sequencing constraint)**: F-2 (F-260b @north-echo asset-tag output wiring) MUST NOT start until Issue #296 (F-1) is closed. No F-2 branch (`297-*` or similar), spec, plan, tasks, or commits MAY exist between F-1 PRD sign-off (2026-05-28) and F-1 close. Constraint is binding per BLP-04 §3 Sequencing Discipline. Additionally (Architect M2): F-2 MUST ship `feat:`-prefixed code by **2026-06-11** (NFR-005 window). If F-2 slips past 2026-06-11, the F-1 close-out comment MUST be updated (post-close edit) to state the new release-cadence-restoration date.
- **FR-008 (Narrative-defensibility pre-check)**: Before publishing the LinkedIn post (FR-002) or merging the Cybersec article (FR-003), the maintainer MUST validate the 50/50 (combined-slot) / 60/60 (per-bucket) claim against:
  - `docs/standards/OWASP_COVERAGE.md` (canonical coverage matrix anchor; FR-001)
  - `schemas/taxonomy/owasp.yaml` (machine-readable source-of-truth; 6 buckets × 10 items = 60 records)
  - Per-baseline `Coverage Attestation` pages in `examples/*/sample-report/security-report.pdf` (pipeline-generated; byte-deterministic per ADR-021)
  - OWASP framework canonical URL anchor tables (LLM 2025, ASI 2026, ML 2023, Mobile 2024, Web 2021, API 2023 — separate per-bucket links per Architect L3)
  Any framework gap = halt + scope-reduce the announcement to the verified subset; do NOT publish unverified claims. Pre-check evidence MUST be recorded in `specs/296-50-50-owasp-coverage-distribution-launch/notes/narrative-defensibility-check.md` dated BEFORE the LinkedIn post URL and Cybersec article PR merge timestamps (SC-009).
- **FR-009 (Public-artifact rollback plan)**: If a published post or article draws **material critique** (defined: a critique that (a) names a specific framework gap, (b) cites a verifiable counter-example, or (c) attracts ≥5 confirming reactions/replies from independent accounts — PM L-2 resolution), the maintainer MUST: (a) document the gap in a follow-up Issue, (b) respond in-thread (LinkedIn comment, article comment, Discussion comment as appropriate), (c) NOT delete or silently retract the post. Correction-in-public is stronger than silent retraction (NFR-003).
- **FR-010**: Issue #296 MUST be closed with all 5 artifact URLs cited in the closing comment: (a) README hero PR URL (this PR #297), (b) LinkedIn post URL, (c) Cybersec Content article PR URL, (d) GitHub profile PR URL, (e) Discussion #179 close URL.
- **FR-011 (No application code changes)**: Beyond the `README.md` hero block (≤30-line diff scoped near the top), the **CHANGELOG.md** entry, and the **`docs/standards/OWASP_COVERAGE.md`** canonical coverage anchor (≤80 lines, new file authored at `/aod.plan` Wave 0 per Architect H2 resolution), this feature MUST NOT modify `tachi.threat-model` agents, skills, schemas, scripts, or any other application code. F-1 is positioning, not capability. **Escape hatch (Architect M4)**: if the README hero diff exceeds 30 lines, the increment beyond 30 lines requires Architect sign-off in `/aod.plan` (cited in the F-1 close-out commit and CHANGELOG entry). The allowed file set is: `README.md`, `CHANGELOG.md`, `docs/standards/OWASP_COVERAGE.md`, `docs/product/02_PRD/296-*.md`, `specs/296-*/` (spec.md, plan.md, tasks.md, research.md, notes/), and `.aod/results/*.md` (review artifacts).
- **FR-012 (BLP-04 strategy doc authoring)**: At F-1 `/aod.deliver` close-out (PRD Q5 lean), the BLP-04 strategy doc (`docs/product/_internal/strategy/BLP-04-adoption-push.md` or equivalent) MUST be authored covering: (a) 4-feature sequencing rationale (F-1 → F-2 → F-3 → F-4), (b) BLP-03 trigger mechanics including enterprise-buyer-signal acceptance criteria (US-7), (c) §3 Sequencing Discipline narrative, (d) F-2 kickoff target (Fri 2026-06-05 AM or Mon 2026-06-08 AM at latest; Team-Lead M-3 resolution), (e) explicit "F-2 PRD/spec/plan/tasks may not be drafted before F-1 close timestamp" statement (Team-Lead M-1 resolution).
- **FR-013 (Memory carve-out)**: The project memory `feedback_aod_deliver_release_gate.md` MUST be updated before F-1 close-out (PM M-2 resolution + SC-013) to reflect the F-1-and-similar `docs:`-only carve-out — explicitly stating the conditions under which a `/aod.deliver` does NOT yield a release-please PR (docs-only feature + follow-on `feat:` within ~1 week).

### Key Entities

- **`docs/standards/OWASP_COVERAGE.md`** (new, ≤80 lines): canonical coverage matrix file. Composes per-bucket counts from `schemas/taxonomy/owasp.yaml` + ADR-024 → ADR-037 + ADR-045 lineage. Includes explicit Web/API combined-slot footnote. Back-links to per-baseline `Coverage Attestation` pages in `examples/*/sample-report/security-report.pdf` for byte-deterministic reproducibility. Indexed in `docs/standards/README.md`.
- **`README.md` hero block** (≤30-line diff): 5-framework coverage block + Web/API combined-slot footnote + canonical anchor link. Inserted between line 14 and line 17.
- **`CHANGELOG.md` entry** (Unreleased section, `docs:` prefix): subsection citing Issue #296 + BLP-04 strategy doc cross-link (post-F-1-close).
- **LinkedIn post** (external, maintainer-published): native-first format; references Daniel Wood 2026-05-02 thread; CTA to tachi repo + Cybersec article + BLP-02 closure.
- **Cybersecurity Content article** (external, ~3000 words): §a–§f sections; 2–3 example verification walkthroughs; per-bucket OWASP URLs.
- **GitHub profile refresh PR** (`davidmatousek/davidmatousek`, external): tachi flagship + AOD-Kit secondary; minimal scope.
- **Discussion #179 closing comment** (in-repo, GitHub Discussion): F-292 PR link + v4.36.0 anchor + ADR-045 line 133 anchor + @armorer-labs gap-analysis attribution.
- **`specs/296-50-50-owasp-coverage-distribution-launch/notes/narrative-defensibility-check.md`** (in-tree, pre-publication): evidence of FR-008 pre-check; dated before LinkedIn / article merge timestamps.
- **BLP-04 strategy doc** (`docs/product/_internal/strategy/BLP-04-adoption-push.md` or equivalent, authored at F-1 close): 4-feature sequencing rationale + BLP-03 trigger mechanics + §3 narrative + F-2 kickoff target + memory carve-out conditions.
- **Issue #296 closing comment**: all 5 artifact URLs + cross-link to BLP-04 strategy doc + memory carve-out reference.

### Non-Functional Requirements

- **NFR-001 (Narrative-defensibility)**: The 50/50 claim MUST be independently verifiable. FR-003 §b verification walkthrough MUST be reproducible by a reader using public `tachi.threat-model` output against worked examples with `SOURCE_DATE_EPOCH=1700000000` (ADR-021). The README hero block (FR-001) MUST link to the canonical anchor file or an output example — NOT make an unanchored claim.
- **NFR-002 (Authorship attribution preservation)**: @armorer-labs's contribution chain (Discussion #179 → F-292 ship → CHANGELOG entry → ADR-045 line 133) MUST be preserved in the Discussion #179 closing comment (FR-005). This follows the F-260 community-merged precedent.
- **NFR-003 (Public artifact discipline)**: Once published externally (LinkedIn post, Cybersec article PR), artifacts MUST NOT be silently deleted or retracted. Corrections happen in-public (comment threads, follow-up posts, errata sections). Tracked under FR-009.
- **NFR-004 (No `tachi.threat-model` capability regression)**: This feature MUST NOT alter `tachi.threat-model` behavior. Verified by NOT modifying any file under `.claude/agents/tachi/`, `.claude/skills/tachi-*/`, `schemas/`, or `.aod/scripts/` per FR-011. Any deviation requires Architect override in `/aod.plan`.
- **NFR-005 (Release-cadence break acknowledgment)**: F-1 ships as `docs:` (FR-006), NOT `feat:`. This breaks the established BLP-02 pattern of every `/aod.deliver` yielding a release-please PR (per project memory `feedback_aod_deliver_release_gate.md`). The cadence break MUST be: (a) explicitly noted in the F-1 `/aod.deliver` close-out, (b) mitigated by F-2 (F-260b asset-tag wiring) shipping `feat:`-eligible code immediately after F-1 close to restore release cadence within ~1 week (by 2026-06-11 per Architect M2), (c) cross-referenced in the BLP-04 strategy doc when it lands (Q5 lean — retroactively at F-1 close, not during build, per PM M-3), (d) recorded in updated project memory `feedback_aod_deliver_release_gate.md` carve-out (FR-013 + SC-013 per PM M-2). The absence of a release-please PR on F-1 PR merge is the **EXPECTED** behavior per `docs:` mapping in release-please-config.json — NOT a release-please skip incident requiring the F-212 empty-`feat(NNN):` marker-commit recovery flow (Architect M3).
- **NFR-006 (Writing-voice vs code-voice separation)**: Per BLP-04 §3 Sequencing Discipline (user directive 2026-05-28), F-1 MUST NOT be parallelized with F-2. Sequential execution preserves cognitive focus. Verified by FR-007 + SC-007.
- **NFR-007 (Time-sensitivity)**: 50/50 coverage fact is a stale-decaying asset. Target wall-clock for F-1 close: 5 working days from PRD sign-off (2026-05-28 → 2026-06-04 target, slack to 2026-06-11). Slack beyond 2 weeks triggers escalation (re-evaluate priority or reduce scope to highest-leverage surface only).
- **NFR-008 (Cybersec article PR self-review discipline)**: Cybersec article PR ships via self-review on a personal repo — no second maintainer available. PR MUST sit ≥24 hours after open before self-merge for fresh-eyes re-read. Self-review checklist MUST include: (a) framework citation accuracy, (b) coverage matrix accuracy, (c) verification walkthrough reproducibility, (d) link validity (no broken URLs), (e) ~3000-word target compliance (2400–3600 band), (f) **asset-tag mention NOT present** (Q4 + FR-007 enforcement per Team-Lead L-2).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: `README.md` hero block merged to main with 5-framework coverage block in first viewport.
  - **Verify**: `git log --oneline -1 README.md` shows the F-1 commit; the first 80 lines of `README.md` (rendered on github.com) include all five framework names with 10/10 status.
- **SC-002**: LinkedIn post published; URL recorded in Issue #296 closing comment.
  - **Verify**: Issue #296 closing comment contains a LinkedIn URL; URL resolves to a maintainer-authored post referencing Daniel Wood's 2026-05-02 thread. **[MANUAL-ONLY]** LinkedIn post URL validity is reviewer-confirmed.
- **SC-003**: Cybersec article PR merged; URL recorded in Issue #296.
  - **Verify**: Issue #296 closing comment contains the Cybersec Content PR URL; article word count is 2400–3600 (~3000 ±20%); article contains the 6 required sections (FR-003 §a–§f).
- **SC-004**: GitHub profile README refresh merged; URL recorded in Issue #296.
  - **Verify**: Issue #296 closing comment contains the profile PR URL; `davidmatousek/davidmatousek` README first viewport contains tachi as flagship with 50/50 tagline.
- **SC-005**: Discussion #179 closed with shipping comment within 7 days of PRD sign-off.
  - **Verify**: `gh discussion view 179` shows status closed; closing comment cites F-292 PR (#293), v4.36.0 release notes, ADR-045 line 133 anchor, and explicit @armorer-labs **gap-analysis** attribution.
- **SC-006**: CHANGELOG.md entry under Unreleased using `docs:` prefix.
  - **Verify**: `git log main -- CHANGELOG.md` shows a commit citing Issue #296; commit subject and CHANGELOG subsection use `docs:` prefix (NOT `feat:`). The squash-merge PR title is `docs(296): ...` per Architect M3.
- **SC-007**: F-1 → F-2 sequencing constraint honored.
  - **Verify**: Between PRD sign-off timestamp (2026-05-28) and Issue #296 close timestamp, `git log --all --grep="F-2|F-260b|asset-tag wiring" --since="2026-05-28"` returns zero commits AFTER human review carves out false-positive incidental references (Architect L1 — references in research notes or prior PR discussion that do NOT initiate F-2 work). No `297-*` (or equivalent) F-2 branch exists.
- **SC-008**: Issue #296 closed with all 5 artifact URLs cited.
  - **Verify**: `gh issue view 296 --comments` shows a maintainer-authored closing comment containing all 5 URLs (README PR, LinkedIn post, Cybersec article PR, profile PR, Discussion #179 close).
- **SC-009**: Narrative-defensibility pre-check completed before LinkedIn post and article publication.
  - **Verify**: `specs/296-50-50-owasp-coverage-distribution-launch/notes/narrative-defensibility-check.md` exists and documents the canonical-coverage-matrix verification, schema/taxonomy/owasp.yaml count verification, byte-deterministic Coverage Attestation page reproduction, and OWASP framework canonical URL anchor verification. Pre-check note's first commit timestamp is BEFORE LinkedIn post URL recording timestamp and Cybersec article PR merge timestamp.
- **SC-010**: No `tachi.threat-model` capability code modified.
  - **Verify**: `git diff main --name-only` against the F-1 feature branch shows zero files modified under `.claude/agents/tachi/`, `.claude/skills/tachi-*/`, `schemas/`, or `.aod/scripts/`. Allowed file set: `README.md`, `CHANGELOG.md`, `docs/standards/OWASP_COVERAGE.md`, `docs/standards/README.md` (index update), `docs/product/02_PRD/296-*.md`, `docs/product/02_PRD/INDEX.md` (registry update), `docs/product/_backlog/BACKLOG.md` (regen), `docs/product/_internal/strategy/BLP-04-adoption-push.md` (FR-012; post-build), `specs/296-*/` (spec.md, plan.md, tasks.md, research.md, notes/), `.aod/results/*.md` (review artifacts). Files outside this set = SC-010 violation.
- **SC-011**: README hero diff scope respected (≤30 lines).
  - **Verify**: `git diff main -- README.md | grep -E "^[+-]" | wc -l` returns ≤30 (changed lines, excluding context). If exceeded, an Architect sign-off in `/aod.plan` covering the increment is cited in the CHANGELOG entry and the F-1 close-out commit (FR-011 escape hatch per Architect M4).
- **SC-012 (Time-sensitivity)**: F-1 close timestamp is within 14 calendar days of PRD sign-off.
  - **Verify**: `gh issue view 296` shows close-timestamp ≤ 2026-06-11 23:59 UTC.
- **SC-013 (Memory carve-out documented)**: Project memory `feedback_aod_deliver_release_gate.md` is updated before F-1 `/aod.deliver` close-out to reflect the F-1-and-similar `docs:`-only carve-out.
  - **Verify**: Memory file `/Users/david/.claude/projects/-Users-david-Projects-tachi/memory/feedback_aod_deliver_release_gate.md` mtime is later than the F-1 PRD sign-off date (2026-05-28) and the file content explicitly documents the conditions under which a `/aod.deliver` does NOT yield a release-please PR (docs-only feature + follow-on `feat:` within ~1 week).
- **SC-014 (BLP-04 strategy doc landed)**: BLP-04 strategy doc is authored at F-1 close-out covering 5 required topics (FR-012 §a–§e).
  - **Verify**: `docs/product/_internal/strategy/BLP-04-adoption-push.md` (or equivalent path) exists; the doc contains the 4-feature sequencing rationale, BLP-03 trigger mechanics (including enterprise-buyer-signal acceptance criteria), §3 Sequencing Discipline narrative, F-2 kickoff target, and explicit no-pre-draft language. Doc is referenced from the F-1 close-out commit and Issue #296 closing comment.

## Assumptions

- **A-1**: `docs/standards/OWASP_COVERAGE.md` does not yet exist (verified at research time, 2026-05-28). It will be authored at `/aod.plan` Wave 0 (Architect H2 lean = Option B; ≤80 lines).
- **A-2**: The current `README.md` line numbers (Get-Started line 13, divider line 14, `## What is tachi?` H2 line 17, brand poster reference line 7) are accurate as of the F-1 branch creation. If the README is modified on `main` during F-1 development (unlikely given no in-flight feature branches per BACKLOG.md as of 2026-05-28), the insertion point and line counts re-anchor accordingly.
- **A-3**: `examples/*/sample-report/security-report.pdf.baseline` files are byte-deterministic when regenerated with `SOURCE_DATE_EPOCH=1700000000` set. Verified by ADR-021 + ADR-029 + ADR-037 D-11.
- **A-4**: Discussion #179 (`https://github.com/davidmatousek/tachi/discussions/179`) was opened by maintainer `davidmatousek` on 2026-04-17; `@armorer-labs` contributed the gap-analysis comment on 2026-05-12. Discussion is currently open as of 2026-05-28 (PRD sign-off date). FR-005 / SC-005 assume the discussion remains open until F-1 explicitly closes it.
- **A-5**: The maintainer's LinkedIn account is accessible during the F-1 acceptance window. If access is disrupted (R-edge), FR-002 may slip to Buffer-2 (2026-06-08) or be deferred to a follow-up Issue if disruption extends past 2026-06-11.
- **A-6**: The `davidmatousek/davidmatousek` profile repo + `davidmatousek/Cybersecurity-Content` repo are accessible and writable by the maintainer. PR self-merge after 24-hour hold is the standard flow.
- **A-7**: No new ADR is required for F-1 (positioning, not capability). `docs/standards/OWASP_COVERAGE.md` is a derivative composition of `schemas/taxonomy/owasp.yaml` + ADR-024 → ADR-037 + ADR-045 lineage, NOT an architecture decision (Architect findings).
- **A-8**: The 2026 LinkedIn algorithm pattern (research §4: link-in-comments suppressed up to 80%) is current and accurate. If LinkedIn algorithm changes mid-window, the FR-002 post format is updated at the maintainer's discretion within the same FR.
- **A-9**: BLP-02 is fully closed (memory: `project_blp02_enterprise_hardening.md`; 6/6 features delivered through v4.36.0 on 2026-05-14) — no in-flight BLP-02 work creates resource contention with F-1.
- **A-10**: F-2 (F-260b @north-echo asset-tag output wiring) has not been started (BACKLOG.md as of 2026-05-28 confirms; FR-007 makes the constraint binding for the F-1 window).
