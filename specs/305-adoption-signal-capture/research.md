# Research Summary: Adoption Signal Capture (F-3, BLP-04 Wave 3)

**Feature**: 305 — Adoption Signal Capture
**PRD**: [docs/product/02_PRD/305-adoption-signal-capture-2026-06-01.md](../../docs/product/02_PRD/305-adoption-signal-capture-2026-06-01.md)
**Date**: 2026-06-01

## Knowledge Base Findings

- **KB Entry 4 (F-3 SECURITY.md, 2026-05-08) — Docs-only DoD + CHANGELOG cluster.** A markdown/policy/platform-config feature with no executable surface maps DoD to manual inspection + post-merge instrumentation; record `waves_tested: 0` with an explicit `skip_reason` (Constitution Principle VII §Exceptions) in `test-results/summary.json` — never silently skip. For BLP-04 use a sibling `### {title} (BLP-04 Wave 3)` CHANGELOG heading.
- **KB Entry 8 (F-296 BLP-04 F-1, 2026-05-30) — two load-bearing lessons.** (1) Internal strategy docs have exactly ONE canonical home: repo-root `_internal/`. F-296 mistakenly created a `docs/product/_internal/...` copy that had to be consolidated — so FR-6's signal log MUST extend the canonical `_internal/strategy/BLP-03-signed-updates.md`, never a `docs/`-side copy. (2) A skipped release is correct for docs-only; F-305 differs because the submission path + channel are user-visible capability → `feat(305):` is justified and a release SHOULD open (verify post-merge).
- **KB Entry 9 (F-302, 2026-06-01) — baseline drift.** New `docs/*.md` files that fall under a `tachi-pytest.yml` `paths:` filter re-trigger `test_personalized_tree_bytes_match_baseline`. If a build touches a CI-filtered path, regenerate the baseline in lock-step. The gitignored `_internal/` log carries zero baseline risk.
- **KB Entry 7 (F-292, 2026-05-14) — post-merge tail.** SLA/calendar-anchored community work (≥3 outreach sends, AIVSS watch) executes only after merge; capture residual MANUAL-ONLY tasks in a follow-up Issue at deliver time.
- **KB Entry 6 — community-merge attribution playbook** (comment-first-give-choice) governs how adopter submissions get processed once they arrive. Consistent with memory `feedback_external_contributor_collisions.md`.
- No KB entry covers warm-outreach anti-spam or append-only signal-log design directly — net-new; governed by NFR-1/R2 and memory `user_linkedin_voice.md`.

## Codebase Analysis

- **`docs/adopters/` absent** (verified) — greenfield; no existing ADOPTERS / case-study / community doc anywhere.
- **`_internal/strategy/BLP-03-signed-updates.md`** exists; carries a "Re-evaluation log" table with columns `Date | Condition #1 (BLP-02 CLOSED) | Condition #2 (enterprise-buyer signal) | Decision` (one entry, 2026-05-10). This is a **2-condition gate-decision** shape, different from FR-6's `date · source · signal-type · decision`. → Recommend a **new append-only subsection**, not folding into this table (Q3).
- **`_internal/CLAUDE.md`** enforces 7-letter file-prefix naming + a hard public/private privacy table (no Cloud/Layer-2, pricing/tiers, named competitors, business-model terms, or scale framing in public `docs/`). Commercial track moved out entirely (2026-04-22) to a separate private workspace.
- **`.gitignore:198`** = `_internal/`; `git ls-files _internal/` returns 0 → repo cleanliness (NFR-2) is structurally guaranteed.
- **CHANGELOG.md** = Keep-a-Changelog; entries are `### {Title + Feature/Wave label}` with discursive narrative + **What shipped** bullets + **Reference** links; community **Credit** subsection where applicable.
- **docs/standards/ house style**: HTML-comment header (File/Description/Author/Created/Last Updated), `#`/`##`/`###` nesting, tables for reference matrices, imperative tone.
- **README Community section (lines 59–68)** already links "In the Wild" ("tell me how you're using tachi, anonymized is fine"). Natural cross-link target for the adopters index.
- **`.github/`** has PR + bug/feature issue templates; no Discussion template yet. A structured adoption-story discussion template is an option (plan-level).

## Architecture Constraints

- All four mandated current-state claims **verified** against the live repo (matches architect sign-off).
- **Live pin state**: global pinned discussions 3/4 (#176/#177/#178); issue pins 0/3.
- **GitHub pin pools are independent**: up to 4 global AND up to 4 per-category (category pins added 2022-11-14). A category-level pin inside "In the Wild" uses that category's own 0/4 pool — **zero global-slot cost**. Editing the category description costs no pin at all. (Refines NFR-4/Q5.)
- **ADR-044 (Dual-Frame Public Positioning, Accepted)** sets the precedent that public-surface/positioning work proceeds without a code-impacting ADR → confirms PRD's **No new ADR** call. ADR-024 is the prior AIVSS-evaluation record FR-5 references.

## Industry Research

- **CNCF/Microcks ADOPTERS pattern** (de-facto OSS standard): core fields = Organization (linked), Contact, Adopter type (end user / consultancy / service provider / project), Description of Use + public-reference link (blog/slides/video) as the credibility anchor. **Consent is baked into the submission flow** (Microcks requires an explicit name/logo grant) — validates FR-1's required Consent block as best practice, not over-engineering.
- **GitHub Discussions**: pinned-discussion cap = 4 (confirmed), global and per-category pools independent; category descriptions are separate metadata.
- **Warm-outreach etiquette**: proactive outreach to *previously-engaged* contacts is established practice (Jupyter precedent); appreciation-first, "here's what shipped" framing (no CTA), ≥1-week gap before a second follow-up, keep substantive conversation public. Aligns with R2 + memory `user_linkedin_voice.md`.

## Recommendations for Spec

1. Resolve **Q2** → single all-in-one template (minimize friction, NFR-5).
2. Resolve **Q3** → new append-only subsection in the canonical `_internal/strategy/BLP-03-signed-updates.md`; never a `docs/`-side copy (KB Entry 8 Lesson 1).
3. Adopt CNCF/Microcks field set for FR-1; keep the required Consent block + an optional public-reference link.
4. **Q5** → prefer a category-level pin (In the Wild's 0/4 pool) or category-description edit over consuming the last global slot; exact mechanic is plan-level. NFR-4 risk = slot-pressure/un-pin, not commit-loss.
5. State the `feat(305):` rationale in-spec; require post-merge release-please verification (memory `feedback_aod_deliver_release_gate.md`).
6. Plan a baseline regen step only if a new `docs/adopters/*.md` falls under a `tachi-pytest.yml` `paths:` filter (KB Entry 9).
7. **Q4** → enumerable "previously-engaged" rule (prior Discussion comment / issue / PR / direct reply / logged inbound; no cold or first-degree-network sends) + named pre-send tone-review gate vs David's house voice.
8. Close F-305 on endogenous SC-1…SC-9; keep SC-10 (case-study/≥3-signal capture) a measurability assertion, never a close gate.

**Avoid**: a redundant "Adopter stories" category (Q1 — "In the Wild" already serves it); any commercial/pricing/competitor/scale framing in public docs; a new ADR; consuming the last global pin slot when a category surface is free.
