---
prd:
  number: 296
  topic: 50-50-owasp-coverage-distribution-launch
  created: 2026-05-28
  status: Approved
  type: feature
triad:
  pm_signoff: {agent: product-manager, date: 2026-05-28, status: APPROVED_WITH_CONCERNS, notes: "PRD grounded in Issue #296 seed body — BLP-04 Wave 1 distribution launch converting 50/50 OWASP coverage from private win (BLP-01 closure 2026-05-01) to public marquee positioning across 5 highest-leverage adopter-facing surfaces (README hero, LinkedIn post, Cybersec article ~3000 words, GitHub profile refresh, Discussion #179 close). 1 HIGH resolved inline: H-1 (Discussion #179 attribution framing — @armorer-labs is the gap-analysis commenter on #179, NOT the original requester; discussion #179 opened by maintainer davidmatousek 2026-04-17). US-5 + FR-5 + Q3 + R5 reworded inline to make @armorer-labs's gap-analysis-commenter role explicit; close-comment tone discipline added. 3 MEDIUM (M-1 enterprise-buyer persona US-7 → /aod.plan; M-2 NFR-5(d) memory carve-out + SC-13 → /aod.plan; M-3 NFR-5(c) strategy doc timing copy edit → /aod.plan) + 2 LOW (L-1 optional contributor persona US-8; L-2 FR-9 material critique criterion) flow into /aod.plan. PM concurs all user-directive constraints: FR-7 sequencing (F-1 → F-2 sequential), Q4 asset-tag deferral, NFR-5 + FR-6 release-cadence break acceptable given F-2 mitigation, 5-surface scope cap (HN/Reddit/dev.to deferred to F-3+), Q3 attribution discipline. No veto triggers. Strategic alignment defensible — F-1 is precisely the work that bridges shipped capability (BLP-01 50/50 closure) to measurable success metrics. Full review at .aod/results/product-manager.md."}
  architect_signoff: {agent: architect, date: 2026-05-28, status: APPROVED_WITH_CONCERNS, notes: "0 BLOCKING / 2 HIGH / 4 MEDIUM / 3 LOW. H1 (Web/API 10/10 is a 2-bucket narrative compression — schemas/taxonomy/owasp.yaml carries 6 buckets × 10 items = 60; PRD's five-framework 50/50 compresses Web 2021 + API 2023 into one slot per ADR-037 D-2) + H2 (canonical coverage matrix file DOES NOT EXIST — only 5 distinct enumerations in schemas/taxonomy/owasp.yaml; no single human-readable matrix file) BOTH resolved inline. FR-1a added mandating explicit Web/API combined-slot footnote in README hero. FR-3 §a updated to require separate per-bucket links (Web 2021 + API 2023) AND explicit per-bucket counts (60/60 broken down; restated as five-slot 50/50). FR-3 §b reproducibility anchored to per-framework Coverage Attestation PAGE (byte-deterministic per ADR-021), NOT narrative outputs. FR-1 + FR-3 §c + FR-8 re-anchored to new `docs/standards/OWASP_COVERAGE.md` (≤80 lines, authored at /aod.plan Wave 0 per Architect Option B lean). FR-11 + SC-10 allowed-file-set extended. Coverage claims independently verified against schemas/taxonomy/owasp.yaml (LLM 10/10 + ASI 10/10 + ML 10/10 + Mobile 10/10 + Web 10/10 + API 10/10) + ADR lineage (ADR-030 → ADR-045 for LLM; ADR-035 for ML; ADR-036 for Mobile; ADR-037 for Web/API combined-slot framing). Release-prefix semantics correct per release-please-config.json (`docs:` hidden, no bump). ADR-045 line 133 already attributes @armorer-labs. Remaining: M1 FR-3 §b reproducibility clarification text → spec.md; M2 FR-7 F-2 ship deadline 2026-06-11; M3 PR title `docs(296):` prefix + release-please skip is EXPECTED behavior; M4 FR-11 escape hatch documentation if hero exceeds 30 lines; L1 SC-7 false-positive carve-out; L2 README hero insertion point lean (between Get-Started line and 'What is tachi?' H2); L3 FR-3 separate per-bucket OWASP URLs (Web 2021 + API 2023). Pre-Mortem lens applied — 4 failure modes identified, all mitigated. No ADR needed for F-1 (positioning, not capability; new docs/standards/OWASP_COVERAGE.md is derivative composition, not architecture decision). Full review at .aod/results/architect.md."}
  techlead_signoff: {agent: team-lead, date: 2026-05-28, status: APPROVED_WITH_CONCERNS, notes: "0 BLOCKING / 0 HIGH / 3 MEDIUM / 3 LOW. Independent calendar verification (cal 5 2026 + cal 6 2026): Day 0 2026-05-28 Thu ✓, Day 1 2026-05-29 Fri ✓, Day 2 2026-06-01 Mon (Sat 2026-05-30 + Sun 2026-05-31 weekend explicit in table) ✓, Day 3 2026-06-02 Tue ✓, Day 4 2026-06-03 Wed ✓, Day 5 2026-06-04 Thu ✓, Buffer-1 2026-06-05 Fri ✓, Buffer-2 2026-06-08 Mon (Sat 2026-06-06 + Sun 2026-06-07 weekend) ✓, hard ceiling 2026-06-11 Thu ✓. 14-day window confirmed. PRD #292 H1 weekend-placement defect NOT repeated. M-2 (Day 1 PM Wave-1 owner attribution mismatch — senior-backend-engineer doesn't belong in writing-bound F-1 per NFR-6 writing-voice/code-voice separation) resolved inline: timeline updated to 'maintainer (with optional product-manager pair on FR-8 pre-check; no senior-backend-engineer)'. Capacity reconciliation clean (zero in-flight feature branches; BLP-02 closed 2026-05-14; BLP-03 still PROPOSED gated by F-1 distribution; Issue #295 unowned non-blocking). Writing-bound work realism confirmed (~12-20h focused effort / 5 working days = 2.4-4 h/day; 24-hour NFR-8 hold is cognitive distance not idle time; parallelizes with Day 3 work). Worst-case absorption: Buffer-2 + 3 unallocated days = 5 cushion days before NFR-7 escalation. F-1 contributes 14-19% of BLP-04 wall-clock (5/26-35 working days); NOT a bottleneck. Remaining: M-1 FR-7/SC-7 constraint propagation explicitness (T-final tasks.md gate + BLP-04 strategy doc explicit no-pre-draft language); M-3 BLP-04 strategy doc F-2 transition target (Fri 2026-06-05 AM or Mon 2026-06-08 AM at latest); L-1 Day 2 drafting+self-review compression note; L-2 NFR-8 checklist asset-tag-absence item; L-3 optional Discussion #179 close earlier drafting for R5 de-risk. All M/L fold into /aod.plan. Full review at .aod/results/team-lead.md."}
source:
  idea_id: 296
  story_id: null
---

# F-1 — 50/50 OWASP Coverage Distribution Launch (BLP-04 Wave 1): Product Requirements Document

**Status**: Approved (with concerns folded inline; remaining M/L → `/aod.plan`)
**Created**: 2026-05-28
**Spec**: TBD (will land at `specs/296-50-50-owasp-coverage-distribution-launch/spec.md` after `/aod.plan`)
**Author**: product-manager
**Reviewers**: architect, team-lead
**Phase**: BLP-04 Adoption Push, Wave 1 (Distribution Launch)
**Priority**: P1
**Parent Initiative**: BLP-04 Adoption Push (proposed 2026-05-28; 4-feature initiative)
**Source**: Seed Issue [#296](https://github.com/davidmatousek/tachi/issues/296) (captured 2026-05-28; pre-vetted in BLP-04 blueprint planning)

---

## 📋 Executive Summary

### The One-Liner

Move the **OWASP five-framework 50/50 coverage** fact (LLM 2025 10/10 + Agentic 2026 10/10 + ML 2023 10/10 + Mobile 2024 10/10 + Web/API 2021/2023 10/10) from "private win" to "public marquee positioning" across **five highest-leverage adopter-facing surfaces** — README hero, LinkedIn post, Cybersecurity Content long-form article (~3000 words), GitHub profile README refresh, and Discussion #179 closing comment — converting a stale-decaying positioning asset into discovery channels and manufacturing the enterprise-buyer signal that gates BLP-03.

### Problem Statement

BLP-01 (Threat Coverage initiative) **closed 2026-05-01** with 11/11 features delivered, lifting tachi's OWASP coverage to **50/50 across five frameworks**: LLM 2025 (10/10) + Agentic 2026 (10/10) + ML 2023 (10/10) + Mobile 2024 (10/10) + Web/API 2021/2023 (10/10). BLP-02 (Enterprise Hardening initiative) **closed 2026-05-14** at v4.36.0 with 6/6 features delivered (LinkedIn-thread punch-list 3/3 + Wave 5 community-feedback gap-set 3/3). Both initiatives shipped **without corresponding public distribution**.

As of 2026-05-28, the **50/50 coverage milestone is not publicly discoverable** on any high-leverage adopter-facing surface:
- `README.md` hero predates 2026-05-01 and contains no coverage block.
- davidmatousek's GitHub profile README shows tachi + AOD-Kit only — no flagship framing for either.
- The Cybersecurity Content public repo is underutilized and predates the milestone (no article references the 50/50 coverage).
- LinkedIn has **no post yet** referencing BLP-01 or BLP-02 closure, despite Daniel Wood's public LinkedIn thread on 2026-05-02 being the **origin signal that triggered the entire BLP-02 enterprise-hardening punch-list**. A response post would close the social loop and serve as a natural distribution channel.
- Discussion [#179](https://github.com/davidmatousek/tachi/discussions/179) ("Detect when LLM outputs become injection vectors downstream (LLM05)"), whose feature request was shipped via F-292 (output-integrity cross-sink refinement, v4.36.0, 2026-05-14), remains open — closing it with a shipping comment doubles as an in-channel announcement.

**BLP-03 trigger condition #2 (enterprise-buyer signal) remains unmet** — distribution work is the most direct path to manufacture that signal. The 50/50 coverage fact is a **stale-decaying asset**: every week it remains private, the marketing leverage compounds against tachi (the milestone gets older, competing tools ship, the "first to 50/50" framing erodes). Conversion of the asset to public surfaces is **time-sensitive**.

### Proposed Solution

**Five published artifacts** spanning two distribution categories — **in-repo** (README hero + GitHub profile refresh, code) and **external** (LinkedIn post, Cybersecurity Content article, Discussion #179 close, writing):

1. **`README.md` hero block** (code, in-repo): new section near top with **OWASP coverage block** — five frameworks listed with 10/10 status; link to canonical coverage matrix or `tachi.threat-model` output examples. Renders locally; links resolve; no broken anchors.

2. **LinkedIn post** (writing, external): single thread; subject = "50/50 OWASP coverage milestone"; references Daniel Wood's BLP-02 origin thread (2026-05-02); CTA = link to tachi repo + Cybersecurity Content article. Published from maintainer's LinkedIn; URL recorded in feature Issue.

3. **Cybersecurity Content repo article** (writing, external): **~3000 words long-form**; title pattern "Mapping OWASP Top-10 to LLM/Agentic threat modeling — what 50/50 means and how to verify it"; includes coverage matrix, framework anchor links, verification walkthrough (run `tachi.threat-model` on a worked architecture, observe the per-framework hit list). Ships as a **PR against the Cybersecurity Content repo** for self-review before merge. URL recorded in feature Issue.

4. **GitHub profile README refresh** (code, external): tachi positioned as **flagship**; AOD-Kit kept as secondary. Pull request against the davidmatousek profile repo. URL recorded in feature Issue.

5. **Discussion #179 closing comment** (writing, in-repo discussion): cite F-292 (output-integrity cross-sink refinement) shipping, v4.36.0 release, ADR-045 anchor; thank original requester @armorer-labs (attribution already preserved in BLP-02 close per F-260 community-merge precedent). URL recorded in feature Issue. **Doubles as in-channel announcement** to BLP-02 community-feedback audience.

**Long-form-over-short-form rationale**: Short-form social content competes in noise; long-form gets shared, linked, and indexed. The ~3000-word article is the **anchor asset** that the LinkedIn post + Discussion #179 close + README hero all back-link to.

**Asset-tag mention deliberately deferred to F-2's announcement** — F-1 stays focused on **coverage** (the 50/50 framework total). F-2 (F-260b @north-echo asset-tag output wiring) will get its own distribution moment when it ships and merits its own announcement surface; mixing the two messages in F-1 dilutes both.

### Scope

**In Scope (this feature)**:
- `README.md` hero block refresh (in-repo code change; ≤30-line diff scoped near the top)
- GitHub profile README refresh PR against davidmatousek/davidmatousek profile repo (external)
- LinkedIn post published from maintainer's LinkedIn; URL recorded in Issue #296
- Cybersecurity Content article PR against davidmatousek/Cybersecurity-Content repo (external); ~3000 words
- Discussion #179 closing comment with F-292 + ADR-045 + v4.36.0 references + @armorer-labs attribution
- CHANGELOG entry for README hero refresh (`docs:` prefix — non-`feat:`, docs-only)
- Feature Issue #296 closed with all 5 artifact URLs cited
- Narrative-defensibility pre-check before publication (canonical coverage matrix verification)

**Out of Scope (deferred / belongs elsewhere)**:
- **F-2 (F-260b asset-tag output wiring)** — explicitly deferred per BLP-04 §3 Sequencing Discipline. F-2 starts ONLY after F-1 closes. See US-6 + Sequencing Constraint section.
- **F-3 (adoption signal capture)** — Wave 2 of BLP-04; converts F-1 inbound (page views, stars, replies, discussion engagement) into a measurable signal. Out of scope here.
- **F-4 (MAESTRO 7-layer announcement)** — Wave 3 of BLP-04; separate technical positioning surface. Out of scope here.
- Additional distribution surfaces (Hacker News, Reddit, Twitter/X, dev.to crossposts) — F-1 caps at 5 highest-leverage surfaces; broader fan-out is F-3+ scope.
- `tachi.threat-model` capability changes — F-1 is positioning, not capability. Zero application code modifications beyond the README hero block.

**Deferred (may be follow-on)**:
- Mid-form crossposts (dev.to, Medium re-hosting of the Cybersec article) — depends on F-3 adoption-signal capture to justify additional distribution effort.
- Multi-language coverage messaging (Spanish, Mandarin, French) — depends on F-3 adoption-signal capture indicating non-English audience.
- Conference talk submissions referencing the 50/50 milestone — depends on F-3 + F-4 closure to anchor the talk's narrative arc.

---

## 🎯 User Stories

**US-1 (Security architect evaluating threat-modeling tools, README hero anchor)**:
> **When** I'm a security architect evaluating threat-modeling tools and I land on the tachi `README.md` for the first time, **I want** to immediately see tachi's OWASP coverage on the hero, **so that** I can assess fit without reading the full docs.

**Acceptance**: The first viewport of `README.md` (above the first H2 collapse) includes a five-framework coverage block listing LLM 2025 / Agentic 2026 / ML 2023 / Mobile 2024 / Web/API 2021/2023 with 10/10 status per framework. The block links to either the canonical coverage matrix file or a `tachi.threat-model` output example demonstrating the per-framework hit list. The block renders correctly on github.com (no broken anchors, no broken links, no truncated tables).

**US-2 (SecOps practitioner browsing LinkedIn, LinkedIn post anchor)**:
> **When** I'm a SecOps practitioner browsing LinkedIn and I previously engaged with Daniel Wood's 2026-05-02 enterprise-hardening thread, **I want** to discover tachi via a response thread that closes that loop, **so that** I see the project as responsive to community feedback and worth a deeper look.

**Acceptance**: The maintainer's LinkedIn feed contains a published post (URL recorded in Issue #296) referencing Daniel Wood's 2026-05-02 thread by name (or by quoted excerpt with attribution), stating the 50/50 OWASP coverage milestone explicitly, and providing a CTA link to (a) the tachi repo, (b) the Cybersecurity Content article, and (c) the BLP-02 closure (v4.36.0 release notes or PR #293 anchor). Post is dated within the F-1 wall-clock window (target 2026-05-28 → 2026-06-04, slack to 2026-06-11).

**US-3 (Cybersecurity content reader, article anchor)**:
> **When** I'm a security researcher or practitioner who follows long-form content in the cybersecurity space, **I want** an article explaining what 50/50 OWASP coverage actually means and how to independently verify it on my own architecture, **so that** I can evaluate the claim without trusting marketing language.

**Acceptance**: The Cybersecurity Content repo contains a published article (URL recorded in Issue #296), ~3000 words (±20%), with the following sections at minimum: (a) framework-by-framework coverage breakdown with anchor links to OWASP canonical URLs (LLM 2025, Agentic 2026, ML 2023, Mobile 2024, Web/API 2021/2023); (b) verification walkthrough running `tachi.threat-model` on a worked architecture description; (c) coverage matrix table; (d) explicit framing of what "10/10" means per framework (which threats, which detection agents); (e) link back to the tachi repo. Article merged via PR self-review (no maintainer-only commit). PR title uses conventional commits format.

**US-4 (Maintainer-profile browser, GitHub profile anchor)**:
> **When** I'm a maintainer or contributor browsing davidmatousek's GitHub profile, **I want** tachi positioned as flagship, **so that** the project is discoverable beyond direct repo links and beyond search.

**Acceptance**: The davidmatousek/davidmatousek profile README has been updated (PR merged; URL recorded in Issue #296) such that tachi appears in a "flagship project" surface with: (a) the 50/50 OWASP coverage tagline; (b) a brief one-line description of what tachi is (STRIDE+AI threat modeling harness for Claude Code); (c) a link to the tachi repo. AOD-Kit remains visible in a secondary position (existing flagship demotion does not erase the project — it just positions tachi above). Profile renders correctly on github.com.

**US-5 (First-time contributor @armorer-labs, Discussion #179 anchor)**:
> **When** I'm @armorer-labs, the **first-time contributor who surfaced three pattern-catalog gaps via a 2026-05-12 comment on discussion #179** (discussion opened by maintainer davidmatousek 2026-04-17), whose **gap-analysis** shipped via F-292 (PR #293, v4.36.0, 2026-05-14), **I want** to learn that the gap-analysis has shipped, **so that** I know the project ships against community asks and that my contribution chain is preserved publicly.

**Acceptance**: Discussion #179 receives a closing comment within 7 days of PRD sign-off (target 2026-06-04) that includes: (a) the F-292 PR link (#293); (b) the v4.36.0 release notes anchor; (c) the ADR-045 anchor (line 133 already attributes @armorer-labs); (d) **explicit @armorer-labs attribution for the gap-analysis comment (2026-05-12) that surfaced the three pattern-catalog gaps** (vector-filter/search-DSL injection, package-manager/CI-workflow execution sinks, cross-agent handoff sinks); (e) link to the CHANGELOG section attributing @armorer-labs in v4.36.0. Discussion closed with status reflecting "shipped". @armorer-labs receives a GitHub notification of the close. **Framing precision**: @armorer-labs is the **gap-analysis commenter**, NOT the discussion-opener — mislabeling weakens credibility and undersells the gap-surfacing contribution.

**US-6 (F-2 sequencing handoff, BLP-04 §3 anchor)**:
> **When** I'm the maintainer transitioning from F-1 close to F-2 start, **I want** F-2 (F-260b @north-echo asset-tag output wiring) to remain unstarted until F-1 closes, **so that** writing-voice (F-1) and code-voice (F-2) focus is preserved and the asset-tag announcement gets its own distribution moment without dilution.

**Acceptance**: No F-2 branch is opened, no F-2 spec/plan/tasks are generated, and no F-2 code is committed before the Issue #296 (F-1) close timestamp. F-2 kickoff (separate `/aod.discover` capture or direct `/aod.define` invocation) begins **only after** F-1 close. Sequencing constraint is explicitly recorded in this PRD (FR-7) and in the BLP-04 strategy doc (to be authored). Violation gate: any `git log` entry between F-1 PRD sign-off and F-1 close referencing F-2 / F-260b / asset-tag wiring is a sequencing violation and must be reverted or held until F-1 close.

---

## ✅ Functional Requirements

**FR-1**: `README.md` MUST include a hero block in the first viewport (before the first H2 collapse on github.com) listing five OWASP framework slots with 10/10 coverage status: LLM 2025, Agentic 2026, ML 2023, Mobile 2024, Web/API 2021/2023 (combined slot). The block MUST link to **`docs/standards/OWASP_COVERAGE.md`** (the canonical coverage matrix file, to be authored at `/aod.plan` Wave 0 per Architect H2 resolution — ≤80 lines, composing per-framework counts from `schemas/taxonomy/owasp.yaml` + ADR-024 → ADR-037 + ADR-045 lineage) AND/OR a `tachi.threat-model` output example demonstrating the per-framework hit list (e.g., per-baseline `Coverage Attestation` page in `examples/*/sample-report/security-report.pdf`, byte-deterministic per ADR-021).

**FR-1a (Web/API combined-slot footnote — Architect H1 resolution)**: The hero block MUST include a footnote or per-bucket cell making the **combined-slot framing explicit**: "Web/API combined slot: OWASP Web Top 10:2021 (A01–A10) + OWASP API Security Top 10:2023 (API1–API10) — 20 items, 20/20." This pre-empts the technically-literate reader who computes 6 buckets × 10 items = 60 and accuses the hero of undercounting. `schemas/taxonomy/owasp.yaml` carries 6 framework buckets at 10 items each (LLM + ASI + ML + Mobile + A0x-Web 2021 + APIn-API 2023); the "five-framework 50/50" hero framing combines Web + API into one slot per ADR-037 D-2 narrative.

**FR-2**: A LinkedIn post MUST be published from the maintainer's LinkedIn (URL recorded in Issue #296) referencing Daniel Wood's 2026-05-02 thread by name or quoted excerpt with attribution, stating the 50/50 OWASP coverage milestone explicitly, and providing CTA links to (a) tachi repo, (b) Cybersecurity Content article (FR-3), (c) BLP-02 closure anchor (v4.36.0 release notes or PR #293).

**FR-3**: A Cybersecurity Content repo article MUST be published (PR merged; URL recorded in Issue #296) at length ~3000 words (±20%) with sections:
- **§a** framework-by-framework coverage breakdown with anchor links to OWASP canonical URLs, including **separate links for Web 2021 (`https://owasp.org/Top10/`) AND API 2023 (`https://owasp.org/API-Security/`)** — the article CANNOT finesse the Web/API combined-slot framing the way the README hero can (Architect L3); per-bucket explicit counts must be shown (LLM 10/10, Agentic 10/10, ML 10/10, Mobile 10/10, Web 10/10, API 10/10 = 60/60 broken down; restated as "five-slot 50/50" with combined Web/API slot explicitly)
- **§b** verification walkthrough using `tachi.threat-model` on **one or more** public `examples/` architectures — reproducibility is anchored to the per-framework `Coverage Attestation` PAGE of `security-report.pdf` (byte-deterministic per ADR-021), NOT narrative outputs (LLM-variable per Architect M1); a single-architecture walkthrough cannot exercise all framework slots simultaneously, so the article MAY pair 2–3 example runs (e.g., `examples/web-app/` for Web/API + `examples/agentic-app/` for LLM + ASI + `examples/maestro-reference/` for ML/Mobile if extended)
- **§c** coverage matrix table — derived from `docs/standards/OWASP_COVERAGE.md` (the canonical anchor; see FR-1)
- **§d** explicit framing of "10/10" per framework (which threats, which detection agents, which ADRs)
- **§e** link back to tachi repo

Article ships via PR self-review (no maintainer-only direct commit; NFR-8 24-hour hold discipline applies).

**FR-4**: The davidmatousek/davidmatousek GitHub profile README MUST be refreshed (PR merged; URL recorded in Issue #296) such that tachi appears in a "flagship project" surface with the 50/50 coverage tagline, a brief description, and a link to the tachi repo. AOD-Kit MUST remain in a secondary position (not removed; positioned below tachi).

**FR-5**: Discussion #179 MUST receive a closing comment within 7 days of PRD sign-off citing F-292 PR (#293), v4.36.0 release notes anchor, ADR-045 anchor (line 133 already attributes @armorer-labs), and **explicit @armorer-labs attribution for the gap-analysis comment (2026-05-12) that surfaced the three pattern-catalog gaps** (vector-filter/search-DSL injection, package-manager/CI-workflow execution sinks, cross-agent handoff sinks). Discussion MUST be closed with status reflecting "shipped". Framing MUST identify @armorer-labs as the **gap-analysis commenter**, NOT the discussion-opener (discussion #179 was opened by maintainer davidmatousek 2026-04-17).

**FR-6**: CHANGELOG.md MUST include an entry under v{next-minor or next-patch} for the README hero refresh using `docs:` prefix (non-`feat:` — docs-only). The CHANGELOG entry MUST cite Issue #296 and link to the BLP-04 strategy doc once it lands.

**FR-7 (Sequencing constraint)**: F-2 (F-260b @north-echo asset-tag output wiring) MUST NOT start until Issue #296 (F-1) is closed. No F-2 branch, spec, plan, tasks, or commits MAY exist between F-1 PRD sign-off and F-1 close. This constraint is binding per BLP-04 §3 Sequencing Discipline — preserves writing-voice (F-1) vs code-voice (F-2) focus and prevents asset-tag announcement dilution.

**FR-8 (Narrative-defensibility pre-check)**: Before publishing the LinkedIn post (FR-2) or merging the Cybersecurity Content article (FR-3), the maintainer MUST validate the 50/50 (combined-slot) / 60/60 (per-bucket) claim against:
- **`docs/standards/OWASP_COVERAGE.md`** (canonical coverage matrix anchor; FR-1)
- **`schemas/taxonomy/owasp.yaml`** (machine-readable source-of-truth; 6 buckets × 10 items)
- **Per-baseline `Coverage Attestation` pages** in `examples/*/sample-report/security-report.pdf` (pipeline-generated; byte-deterministic per ADR-021)
- **OWASP framework canonical URL anchor tables** (LLM 2025, ASI 2026, ML 2023, Mobile 2024, Web 2021, API 2023 — separate per-bucket links)

Any framework gap = halt + scope-reduce the announcement to the verified subset; do NOT publish unverified claims. Pre-check evidence MUST be recorded in a pre-publication note under the feature branch (e.g., `notes/narrative-defensibility-check.md` or in the spec.md research phase artifact) dated BEFORE the LinkedIn post URL and Cybersec article PR merge timestamps (SC-9).

**FR-9 (Public-artifact rollback plan)**: If a published post or article draws material critique (e.g., "but you don't cover [X]"), the maintainer MUST: (a) document the gap in a follow-up Issue, (b) respond in-thread (LinkedIn comment, article comment, Discussion comment as appropriate), (c) NOT delete or silently retract the post. Correction-in-public is stronger than silent retraction. Rationale recorded in NFR-3.

**FR-10**: Issue #296 MUST be closed with all 5 artifact URLs cited in the closing comment: (a) README hero PR (in-repo, this PRD's PR), (b) LinkedIn post URL, (c) Cybersecurity Content article PR URL, (d) GitHub profile PR URL, (e) Discussion #179 close URL.

**FR-11 (No application code changes)**: Beyond the `README.md` hero block (≤30-line diff scoped near the top), the **CHANGELOG.md** entry, and the **`docs/standards/OWASP_COVERAGE.md`** canonical coverage anchor (≤80 lines, new file authored at `/aod.plan` Wave 0 per Architect H2 resolution), this feature MUST NOT modify `tachi.threat-model` agents, skills, schemas, scripts, or any other application code. F-1 is positioning, not capability. If the README hero diff exceeds 30 lines, the increment beyond 30 lines requires Architect sign-off in `/aod.plan` (escape hatch per Architect M4). The allowed file set is: `README.md`, `CHANGELOG.md`, `docs/standards/OWASP_COVERAGE.md`, `docs/product/02_PRD/296-*.md`, `specs/296-*/` (spec.md, plan.md, tasks.md, research.md, notes/), and `.aod/results/*.md` (review artifacts).

---

## 🚧 Non-Functional Requirements

**NFR-1 (Narrative-defensibility)**: The 50/50 claim MUST be **independently verifiable**. The Cybersecurity Content article's verification walkthrough (FR-3 §b) MUST be reproducible by a reader using public `tachi.threat-model` output against a worked architecture. The README hero block (FR-1) MUST link to either the canonical coverage matrix or an output example — NOT make an unanchored claim.

**NFR-2 (Authorship attribution preservation)**: @armorer-labs's contribution chain (discussion #179 → F-292 ship → CHANGELOG entry) MUST be preserved in the Discussion #179 closing comment (FR-5). This follows the F-260 community-merged precedent (PR #262, @north-echo, v4.31.0) — explicit thanks + attribution + cross-link to the shipped PR.

**NFR-3 (Public artifact discipline)**: Once published externally (LinkedIn post, Cybersecurity Content article PR), artifacts MUST NOT be silently deleted or retracted. Corrections happen in-public (comment threads, follow-up posts, errata sections). Silent retraction erodes trust; correction-in-public reinforces it. Tracked under FR-9.

**NFR-4 (No `tachi.threat-model` capability regression)**: This feature MUST NOT alter `tachi.threat-model` behavior. Verified by NOT modifying any file under `.claude/agents/tachi/`, `.claude/skills/tachi-*/`, `schemas/`, or `.aod/scripts/` per FR-11. Any deviation from "README hero block only" requires Architect override in `/aod.plan`.

**NFR-5 (Release-cadence break acknowledgment)**: F-1 ships as `docs:` (FR-6), NOT `feat:`. This breaks the established BLP-02 pattern of every `/aod.deliver` yielding a release-please PR (per project memory `feedback_aod_deliver_release_gate.md`). The cadence break MUST be: (a) explicitly noted in the F-1 `/aod.deliver` close-out, (b) mitigated by F-2 (F-260b asset-tag wiring) shipping `feat:`-eligible code immediately after F-1 close to restore release cadence within ~1 week, (c) cross-referenced in the BLP-04 strategy doc when it lands. See FR-7 sequencing constraint.

**NFR-6 (Writing-voice vs code-voice separation)**: Per BLP-04 §3 Sequencing Discipline (user directive in `/aod.define` invocation 2026-05-28), F-1 MUST NOT be parallelized with F-2. The cognitive cost of context-switching between writing-voice work (LinkedIn post drafting, article structure, social copy) and code-voice work (asset-tag SARIF wiring, populator changes) erodes quality on both. Sequential execution preserves focus. Verified by FR-7.

**NFR-7 (Time-sensitivity)**: The 50/50 coverage fact is a stale-decaying asset (every week public, marketing leverage compounds; every week private, the framing erodes). Target wall-clock for F-1 close is **5 working days from PRD sign-off** (2026-05-28 sign-off → target close 2026-06-04, slack to 2026-06-11). Slack beyond 2 weeks triggers escalation to user (re-evaluate priority or reduce scope to highest-leverage surface only).

**NFR-8 (Cybersec Content repo PR self-review discipline)**: The Cybersecurity Content article PR (FR-3) ships via self-review on a personal repo — no second maintainer is available. The PR MUST sit for at least 24 hours after open before self-merge to allow re-read with fresh eyes. The self-review checklist MUST include: (a) framework citation accuracy, (b) coverage matrix accuracy, (c) verification walkthrough reproducibility, (d) link validity (no broken URLs), (e) ~3000-word target compliance.

---

## 🎯 Success Criteria

**SC-1**: `README.md` hero block merged to main with 5-framework coverage block in first viewport.
- **Verify**: `git log --oneline -1 README.md` shows the F-1 commit; first 80 lines of `README.md` (rendered on github.com) include all five framework names with 10/10 status.

**SC-2**: LinkedIn post published; URL recorded in Issue #296 closing comment.
- **Verify**: Issue #296 closing comment contains a LinkedIn URL; URL resolves to a maintainer-authored post referencing Daniel Wood's 2026-05-02 thread.

**SC-3**: Cybersecurity Content article PR merged; URL recorded in Issue #296.
- **Verify**: Issue #296 closing comment contains the Cybersecurity Content PR URL; article word count is ≥2400 and ≤3600 (~3000 ±20%); article contains the 5 required sections (FR-3 §a–e).

**SC-4**: GitHub profile README refresh merged; URL recorded in Issue #296.
- **Verify**: Issue #296 closing comment contains the profile PR URL; davidmatousek/davidmatousek README first viewport contains tachi as flagship with 50/50 tagline.

**SC-5**: Discussion #179 closed with shipping comment within 7 days of PRD sign-off.
- **Verify**: `gh discussion view 179` shows status closed; closing comment cites F-292 PR (#293), v4.36.0 release notes, ADR-045 anchor, and explicit @armorer-labs attribution.

**SC-6**: CHANGELOG.md entry under v{next} using `docs:` prefix.
- **Verify**: `git log main -- CHANGELOG.md` shows a commit citing Issue #296; commit subject and CHANGELOG entry use `docs:` prefix (NOT `feat:`).

**SC-7**: F-1 → F-2 sequencing constraint honored.
- **Verify**: Between PRD sign-off timestamp and Issue #296 close timestamp, `git log --all --grep="F-2|F-260b|asset-tag wiring"` returns zero commits on any branch. No F-2 branch (`297-*` or similar) exists in the repo.

**SC-8**: Issue #296 closed with all 5 artifact URLs cited.
- **Verify**: `gh issue view 296 --comments` shows a maintainer-authored closing comment containing all 5 URLs (README PR, LinkedIn post, Cybersec article PR, profile PR, Discussion #179 close).

**SC-9**: Narrative-defensibility pre-check completed before LinkedIn post and article publication.
- **Verify**: A pre-publication note in the feature spec (or in a `notes/` artifact under the feature branch) documents the canonical-coverage-matrix verification and OWASP anchor-table verification. Pre-publication note dated BEFORE the LinkedIn post URL and Cybersec article PR merge timestamps.

**SC-10**: No `tachi.threat-model` capability code modified.
- **Verify**: `git diff main --name-only` against the F-1 feature branch shows zero files modified under `.claude/agents/tachi/`, `.claude/skills/tachi-*/`, `schemas/`, `.aod/scripts/`. The **allowed file set** is: `README.md`, `CHANGELOG.md`, `docs/standards/OWASP_COVERAGE.md` (new, ≤80 lines per Architect H2), `docs/product/02_PRD/296-*.md`, `specs/296-*/` (spec.md/plan.md/tasks.md/research.md/notes/), `.aod/results/*.md` (review artifacts). Files outside this set = SC-10 violation.

**SC-11**: README hero diff scope respected (≤30 lines).
- **Verify**: `git diff main -- README.md | grep -E "^[+-]" | wc -l` returns ≤30 (changed lines, excluding context). If exceeded, an Architect sign-off in `/aod.plan` covering the increment must be cited in the CHANGELOG entry.

**SC-12 (Time-sensitivity)**: F-1 close timestamp is within 14 calendar days of PRD sign-off (2026-05-28 → 2026-06-11 hard ceiling; 2026-06-04 target).
- **Verify**: `gh issue view 296` shows close-timestamp ≤ 2026-06-11 23:59 UTC.

---

## ❓ Open Questions (Architect-Owned, Resolve in `/aod.plan`)

**Q1 (Cybersec article length)**: Target ~3000 words. Is the ±20% band (2400–3600) the right tolerance, or should it tighten to ±10% (2700–3300) to discipline scope?
- **Lean**: ±20% — long-form articles benefit from elasticity to follow the verification walkthrough wherever the worked architecture leads. Tightening to ±10% could force premature truncation of the framework breakdown sections.
- **Counter-argument for ±10%**: Discipline. A 3000-word target with ±10% prevents bloat; ±20% allows up to 3600 words which is meaningfully longer.
- **Decision criterion**: Architect's call on word-count discipline vs. content elasticity. Default = ±20% (FR-3 lean).

**Q2 (LinkedIn post timing)**: Publish the LinkedIn post (a) before, (b) simultaneous with, or (c) after the Cybersecurity Content article merges?
- **Lean**: **(c) after**. The LinkedIn post CTA includes a link to the Cybersec article; the article must exist before the post can link to it. Sequencing prevents broken-link risk.
- **Counter-argument for (b) simultaneous**: Maximize same-day attention by coupling the two announcements.
- **Counter-argument for (a) before**: Builds anticipation; the article lands as the "promised long-form."
- **Decision criterion**: Default = (c). Deviate only if the maintainer can guarantee article-merge timing precisely.

**Q3 (Discussion #179 close-comment authorship)**: Maintainer authors the close comment, OR does @armorer-labs (the **gap-analysis commenter on #179, NOT the discussion-opener**) get offered a chance to co-author or comment first per F-260 precedent?
- **Lean**: **Maintainer authors with explicit attribution to the gap-analysis comment**. F-260 community-merged precedent (PR #262, @north-echo) is for **shipping refinement** authorship (gap-surfacing → PR authorship choice). The Discussion #179 closing comment is a **maintainer responsibility** (it cites F-292's shipping); @armorer-labs's attribution is preserved in the CHANGELOG and in the F-292 PR's `Co-authored-by:` trailer (already shipped via PRD #292 §7 + memory `feedback_external_contributor_collisions.md`). The closing comment tone MUST lead with attribution: "Thanks to @armorer-labs's gap-analysis comment surfacing three pattern-catalog gaps, we shipped F-292" — NOT "Thanks to @armorer-labs's request."
- **Counter-argument**: Offering @armorer-labs co-authorship of the close comment is a stronger gesture. But it requires another round-trip and may delay close past the 7-day SLA.
- **Decision criterion**: Default = maintainer authors with attribution. Deviate only if @armorer-labs has explicitly engaged on discussion #179 since 2026-05-12 and signaled willingness.

**Q4 (Asset-tag mention deferral confirmation)**: User directive in `/aod.define` invocation (2026-05-28) confirms F-1 stays focused on coverage; asset-tag (F-260 + F-2 F-260b) NOT mentioned. Is this firm, or do we want to fold a 1-sentence "asset-tag wiring coming soon" teaser into the article and/or LinkedIn post?
- **Lean**: **No mention of asset-tag in F-1**. Per user directive: F-1 → F-2 sequential preserves writing-voice vs code-voice focus AND preserves the asset-tag announcement's distinct moment in F-2. Mixing dilutes both.
- **Counter-argument**: A 1-sentence teaser drives anticipation and gives F-2 launch a built-in audience.
- **Decision criterion**: User directive is firm. Default = no asset-tag mention. Deviate only with explicit user override during `/aod.plan`.

**Q5 (BLP-04 strategy doc authorship)**: Seed Issue body references `../_internal/strategy/BLP-04-adoption-push.md` which does not yet exist. Author the strategy doc as part of F-1 close-out, OR carve it out as a separate artifact (e.g., F-0 BLP-04 strategy authoring) ahead of F-1?
- **Lean**: **Author at F-1 close-out** as part of `/aod.deliver` documentation flow. The strategy doc captures the 4-feature sequencing rationale (F-1 → F-2 → F-3 → F-4), BLP-03 trigger mechanics, and §3 Sequencing Discipline narrative. F-1 close-out is the natural moment because Wave 1 results inform Wave 2+ sequencing.
- **Counter-argument**: Authoring the strategy doc upfront (pre-F-1) provides a North Star for F-2 + F-3 + F-4 PRDs. But authoring before F-1 close is premature — we don't yet know how F-1 lands.
- **Decision criterion**: Default = author at F-1 close. Deviate only if the maintainer has clear conviction on F-2+ sequencing before F-1 close.

**Q6 (CHANGELOG `docs:` prefix release-please impact)**: Per FR-6 + NFR-5, F-1 ships as `docs:` (non-`feat:`). Release-please will NOT open a release PR on this `docs:` commit. Is this acceptable for the 1-week gap before F-2 ships, OR should we use `chore:` or some other prefix that still doesn't bump but signals work?
- **Lean**: **`docs:` is correct**. F-1 IS docs-only (README hero refresh + CHANGELOG). `docs:` is semantically accurate per release-please config (`docs:`, `chore:`, `refactor:`, `test:`, `style:` are all "hidden, no bump"). F-2 (F-260b asset-tag wiring) ships `feat:` ~1 week later and restores release cadence.
- **Counter-argument**: Use `feat:` to trigger a release PR even though the change is docs-heavy (precedent: F-272 SECURITY.md shipped `feat:`-prefixed to trigger v4.33.0 release). This breaks semantic accuracy but maintains the cadence-yields-release pattern.
- **Decision criterion**: Architect's call on semantic accuracy vs cadence discipline. **Lean = `docs:` per FR-6** (cadence break explicitly acknowledged in NFR-5; F-2 restores within 1 week). If Architect overrides to `feat:`, update FR-6 + NFR-5 + SC-6 accordingly.

**Q7 (GitHub profile README scope)**: Should the profile README refresh add a "Now" section with current focus (BLP-04 adoption), OR keep it minimal (just flagship project table with tachi + AOD-Kit)?
- **Lean**: **Minimal — flagship project table only**. Profile READMEs decay quickly; adding a "Now" section creates an ongoing maintenance burden (memory `reference_github_profile.md` shows current profile is already underutilized).
- **Counter-argument**: A "Now" section signals an active maintainer and engages potential contributors.
- **Decision criterion**: Default = minimal. Deviate only if maintainer has explicit conviction to maintain a "Now" section ongoing.

---

## ⚠️ Risks & Mitigations

**R1 (Material critique on public posts)**: A LinkedIn commenter or article reader argues "but you don't cover [X framework gap]" — either factually correct (we missed a sub-coverage detail) or factually incorrect (misreading the coverage claim).
- **Likelihood**: MEDIUM (50/50 framing invites scrutiny; the more reach a post gets, the higher the probability of critique)
- **Impact**: MEDIUM (an unanswered or poorly-handled critique erodes positioning; a well-handled one reinforces credibility)
- **Mitigation**: FR-8 (narrative-defensibility pre-check) catches verifiable gaps before publication. FR-9 (public-artifact rollback plan) governs response — document the gap, respond in-thread, file a follow-up Issue, do NOT delete. NFR-3 reinforces the discipline.

**R2 (LinkedIn post draws too little engagement)**: The post is published, but reach is minimal — no replies, few impressions, no inbound to the article.
- **Likelihood**: MEDIUM (LinkedIn organic reach is unreliable; depends on audience, timing, hashtag use, post format)
- **Impact**: LOW (the LinkedIn post is one of 5 surfaces; low engagement on one doesn't gate the others)
- **Mitigation**: F-3 (adoption signal capture, BLP-04 Wave 2) is the systemic answer — if F-1 produces low signal, F-3's instrumentation will surface that and inform F-4 (MAESTRO 7-layer announcement) sequencing. F-1 doesn't need to optimize for LinkedIn reach; it needs to publish the artifact.

**R3 (Cybersec article requires multiple revisions)**: The ~3000-word article goes through 2–3 self-review cycles before merge, extending wall-clock past target.
- **Likelihood**: MEDIUM (long-form writing is iterative)
- **Impact**: MEDIUM (extends wall-clock; competing with NFR-7 time-sensitivity)
- **Mitigation**: NFR-8 (self-review discipline) bounds the iteration — PR sits 24 hours before self-merge, single self-review checklist. NFR-7 sets hard ceiling at 2026-06-11. If revisions push past 2026-06-11, scope-reduce the article (drop one section, ship ~2000 words) rather than slip the deadline.

**R4 (GitHub profile refresh disrupts existing layout)**: The profile README has existing content (current state per memory: shows tachi + AOD-Kit only); adding flagship framing may require restructuring that breaks unrelated sections.
- **Likelihood**: LOW (profile is minimal; restructuring scope is small)
- **Impact**: LOW (worst case: revert and try again)
- **Mitigation**: PR against the profile repo with explicit before/after rendering review on github.com. PR sits 24 hours before self-merge (mirror NFR-8 discipline). Revert is one git operation.

**R5 (Discussion #179 close steals @armorer-labs's thunder)**: Maintainer-authored close comment could read as taking credit for the work that @armorer-labs's **gap-analysis comment** surfaced.
- **Likelihood**: LOW (Q3 lean specifies explicit gap-analysis attribution; CHANGELOG already attributes @armorer-labs via F-292's `Co-authored-by:` trailer; ADR-045 line 133 attributes @armorer-labs's gap-analysis)
- **Impact**: MEDIUM (eroded trust with a productive first-time contributor)
- **Mitigation**: Q3 explicit **gap-analysis** attribution + F-260 precedent referenced + Co-authored-by trailer preserved + ADR-045 line 133 anchor cited. The close comment leads with attribution to @armorer-labs's **gap-analysis comment**, then cites the ship. Tone matters: "Thanks to @armorer-labs's **gap-analysis comment** surfacing three pattern-catalog gaps, we shipped F-292" beats "We shipped X (thanks @armorer-labs)". Critically: NEVER frame @armorer-labs as "the requester" — they are the gap-surfacing commenter; the discussion itself was opened by maintainer davidmatousek.

**R6 (Release-cadence break confuses adopters)**: BLP-02 closed with v4.36.0; F-1 ships `docs:` and yields no release PR; F-2 ships ~1 week later and triggers v4.37.0. Adopters tracking releases may notice the gap.
- **Likelihood**: LOW (most adopters consume via SemVer-pinned dependencies; a 1-week gap with no release is normal cadence)
- **Impact**: LOW (NFR-5 explicitly documents the cadence break and the F-2 mitigation timeline)
- **Mitigation**: F-1 `/aod.deliver` close-out notes that "next release ships with F-2 within ~1 week". Optionally cross-link the BLP-04 strategy doc when it lands. Memory `feedback_aod_deliver_release_gate.md` is updated to reflect the F-1 carve-out (docs-only feature explicitly exempt from "every /aod.deliver yields a release-please PR").

**R7 (F-2 starts in parallel violating BLP-04 §3)**: Despite user directive, F-2 work begins before F-1 closes (maintainer enthusiasm, agent over-eagerness, accidental scope creep).
- **Likelihood**: LOW (FR-7 + SC-7 binary check; user directive is explicit)
- **Impact**: MEDIUM (writing-voice vs code-voice context-switching erodes quality on both; asset-tag announcement dilution)
- **Mitigation**: FR-7 makes the constraint binding. SC-7 binary verification at F-1 close. Any commit referencing F-2 / F-260b / asset-tag wiring between PRD sign-off and Issue #296 close is a violation — revert or hold until F-1 close.

---

## 📅 Estimated Timeline

**Schedule policy**: Weekday-anchored cadence per project convention. F-1 is writing-bound (not code-bound) — wall-clock is dominated by drafting and self-review iterations, not by implementation cycles. Working-day effort estimate: ~3 focused working days. Wall-clock target: 5 working days (slack to 10).

| Day | Date | Activity | Owner |
|---|---|---|---|
| Day 0 | 2026-05-28 (Thu) | `/aod.define` — this PRD; parallel Triad reviews | product-manager + architect + team-lead |
| Day 1 AM | 2026-05-29 (Fri) | `/aod.plan` — spec.md + plan.md + tasks.md with Q1–Q7 decisions | product-manager + architect + team-lead |
| Day 1 PM | 2026-05-29 (Fri) | `/aod.build` Wave 0 — **Author `docs/standards/OWASP_COVERAGE.md`** (≤80 lines per Architect H2; canonical coverage matrix anchor) + README hero block draft (FR-1 + FR-1a Web/API footnote) + narrative-defensibility pre-check (FR-8) | maintainer (with optional product-manager pair on FR-8 pre-check; **no senior-backend-engineer** per Team-Lead M-2 — F-1 is writing-bound, not code-bound, per NFR-6) |
| — | 2026-05-30 (Sat) — 2026-05-31 (Sun) | Weekend (maintainer break) | — |
| Day 2 AM | 2026-06-01 (Mon) | `/aod.build` Wave 2 — Cybersec article draft (target ~3000 words; FR-3 §a–e) | maintainer |
| Day 2 PM | 2026-06-01 (Mon) | `/aod.build` Wave 2 (continued) — Cybersec article self-review pass 1 | maintainer |
| Day 3 AM | 2026-06-02 (Tue) | `/aod.build` Wave 3 — GitHub profile README refresh PR + LinkedIn post draft | maintainer |
| Day 3 PM | 2026-06-02 (Tue) | Cybersec article 24-hour hold complete; PR self-merge (NFR-8) | maintainer |
| Day 4 AM | 2026-06-03 (Wed) | LinkedIn post publishes (FR-2; per Q2 lean = after article merges) | maintainer |
| Day 4 PM | 2026-06-03 (Wed) | GitHub profile PR self-merge (after 24-hour hold) | maintainer |
| Day 5 AM | 2026-06-04 (Thu) | `/aod.build` Wave 4 — Discussion #179 closing comment authored & published (FR-5) | maintainer |
| Day 5 PM | 2026-06-04 (Thu) | `/aod.deliver` — README hero PR ready-for-review → squash-merge (`docs:` prefix); Issue #296 closed with 5 artifact URLs; BLP-04 strategy doc authored (Q5 lean) | product-manager + maintainer |
| **Buffer-1** | 2026-06-05 (Fri) | Slip buffer for Cybersec article revision iterations OR Discussion #179 close delay | maintainer |
| **Buffer-2** | 2026-06-08 (Mon) | Slip buffer for unforeseen blocker (LinkedIn account issues, repo PR review delays) | — |
| **Hard ceiling** | 2026-06-11 (Thu) | NFR-7 escalation: if F-1 has not closed by 2026-06-11, escalate to user (re-evaluate priority or scope-reduce) | — |

**Total wall-clock**: 5 working days target (~3 focused working days of effort). Hard ceiling at 14 calendar days (2026-06-11).

**Critical path**:
1. Day 1 AM `/aod.plan` resolves Q1–Q7 AND Wave 0 prerequisites (author `docs/standards/OWASP_COVERAGE.md` per Architect H2; FR-1a Web/API combined-slot footnote framing per Architect H1) → unlocks Wave 1.
2. Day 1 PM Wave 0 (OWASP_COVERAGE.md anchor) + Wave 1 (README hero + pre-check) — small surface, all writing-bound; parallelizable with Day 2 article drafting if maintainer prefers.
3. Day 2 Cybersec article drafting is the **longest single task** (long-form writing is iterative; ~3000 words ≈ 4–6 hours focused drafting + 1–2 hours self-review).
4. Day 3 GitHub profile + LinkedIn draft can parallelize with article 24-hour hold.
5. Day 4 LinkedIn publishes AFTER article merge (Q2 lean = (c)).
6. Day 5 Discussion #179 close + `/aod.deliver` close-out + Issue #296 close + BLP-04 strategy doc authoring.

**F-2 kickoff gate**: F-2 (F-260b @north-echo asset-tag output wiring) `/aod.discover` or `/aod.define` invocation MUST occur **after** Issue #296 close timestamp. Earliest F-2 start: 2026-06-05 (Buffer-1 day if F-1 closes on Day 5 target). Latest F-2 start gated by F-1 close — no F-2 work before then.

**Worst-case path**: If Cybersec article requires 2–3 revision cycles (R3) AND LinkedIn account issues block Day 4 publication (R-edge), `/aod.deliver` shifts to Buffer-2 (Mon 2026-06-08). PRD's two-buffer-day allocation + hard-ceiling escalation prevents indefinite slip.

---

## 🔗 Dependencies

**Hard dependencies (must be in place before this PRD's branch opens)**:
- **BLP-01 closure (11/11 features delivered, 2026-05-01)** — provides the 50/50 OWASP coverage fact. **CLOSED ✓** (memory: `project_blp01_threat_coverage.md`).
- **BLP-02 closure (6/6 features delivered, v4.36.0, 2026-05-14)** — provides the BLP-02 narrative arc that anchors the LinkedIn post (Daniel Wood thread response). **CLOSED ✓** (memory: `project_blp02_enterprise_hardening.md`).
- **F-292 shipped (output-integrity cross-sink refinement, PR #293, v4.36.0)** — provides the discussion #179 closing material. **SHIPPED ✓**.
- **F-260 community-merged precedent (@north-echo, PR #262, v4.31.0, 2026-05-06)** — establishes the community-attribution pattern for Discussion #179 close comment. **MERGED ✓** (memory: `project_f260_asset_tags.md`).
- **Canonical coverage matrix file (in-repo)** — **DOES NOT YET EXIST** per Architect H2; will be authored at `/aod.plan` Wave 0 as `docs/standards/OWASP_COVERAGE.md` (≤80 lines, composing per-bucket counts from `schemas/taxonomy/owasp.yaml` + ADR-024 → ADR-037 + ADR-045 lineage, with explicit Web/API combined-slot footnote, back-links to per-baseline `Coverage Attestation` pages). This file is the canonical anchor for FR-1 README hero link AND FR-8 narrative-defensibility pre-check AND FR-3 §c article coverage matrix table.

**Soft dependencies (informational; may inform `/aod.plan` decisions)**:
- **BLP-04 strategy doc** (`docs/product/_internal/strategy/BLP-04-adoption-push.md` or similar) — does NOT yet exist as of 2026-05-28. Q5 lean = author at F-1 close (no blocking dependency for F-1 build).
- **F-2 (F-260b @north-echo asset-tag output wiring)** — NOT YET STARTED by FR-7 mandate. F-1 close is the gate for F-2 start. No code dependency between F-1 and F-2.
- **F-3 (BLP-04 adoption signal capture)** — NOT YET STARTED; depends on F-1 + F-2 close. Informs whether F-1 distribution surfaces generated measurable inbound.
- **F-4 (BLP-04 MAESTRO 7-layer announcement)** — NOT YET STARTED; depends on F-3 signal evidence.

**External dependencies (out-of-repo systems)**:
- **LinkedIn account access** (maintainer's personal LinkedIn) — for FR-2 publication. No automation; manual post.
- **davidmatousek/Cybersecurity-Content repo** (public GitHub repo) — for FR-3 article PR + merge. Self-merge after 24-hour hold (NFR-8). Memory `reference_cybersecurity_content_repo.md` references this repo as underutilized.
- **davidmatousek/davidmatousek profile repo** (public GitHub repo) — for FR-4 profile README PR + merge. Self-merge after 24-hour hold. Memory `reference_github_profile.md` references current profile state.
- **github.com Discussions #179** (in-repo) — for FR-5 closing comment. `gh discussion close` after comment.

**No dependencies on**:
- BLP-03 (signed updates) F-1 / F-2 — BLP-03 is gated by F-1 distribution + enterprise-buyer signal. F-1 IS the trigger work for BLP-03.
- Any in-flight feature branches — BACKLOG.md as of 2026-05-28 shows no active feature branches; F-1 is the next feature in line.

---

## 📚 References

- **Seed Issue #296**: [50/50 OWASP Coverage Distribution Launch (BLP-04 F-1)](https://github.com/davidmatousek/tachi/issues/296) (2026-05-28)
- **BLP-04 Adoption Push initiative memory**: `project_blp04_adoption_push.md` (4-feature initiative, PROPOSED 2026-05-28)
- **BLP-01 Threat Coverage initiative memory**: `project_blp01_threat_coverage.md` (CLOSED 2026-05-01; 11/11 delivered; OWASP 5-framework total 50/50)
- **BLP-02 Enterprise Hardening initiative memory**: `project_blp02_enterprise_hardening.md` (CLOSED 2026-05-14; 6/6 delivered; v4.36.0)
- **PRD #292** — F-292 Output-Integrity Cross-Sink Refinement (sets discussion #179 close material): `docs/product/02_PRD/292-output-integrity-cross-sink-refinement-2026-05-14.md`
- **PRD #260** — F-260 Asset-Sensitivity Tags (community-merged precedent, @north-echo): seed Issue #260 + memory `project_f260_asset_tags.md`
- **Discussion #179**: https://github.com/davidmatousek/tachi/discussions/179 (to be closed via FR-5)
- **F-292 PR #293** (referenced in Discussion #179 close): https://github.com/davidmatousek/tachi/pull/293
- **Memory: External contributor PR collisions** (Discussion #179 close authorship discipline): `feedback_external_contributor_collisions.md`
- **Memory: AOD deliver must release** (NFR-5 release-cadence break acknowledgment): `feedback_aod_deliver_release_gate.md`
- **Memory: GitHub profile README** (current state for FR-4): `reference_github_profile.md`
- **Memory: Cybersecurity Content repo** (current state for FR-3): `reference_cybersecurity_content_repo.md`
- **Memory: Tachi source-of-truth positioning** (anchors article framing): `project_tachi_source_of_truth.md`
- **Memory: CONSUMER_GUIDE_TACHI.md is immutable** (FR-1 scope guard — don't touch CONSUMER_GUIDE): `feedback_consumer_guide_immutable.md`
- **Memory: CLAUDE.md Recent Changes stays slim** (CHANGELOG entry for FR-6): `feedback_claude_md_no_recent_changes.md`
- **CHANGELOG.md** — for FR-6 entry placement
- **Canonical coverage matrix** — location TBD in `/aod.plan` research phase (likely `docs/standards/`, `docs/architecture/`, or `examples/coverage-matrix.md`)
- **OWASP framework anchors** (FR-8 pre-check):
  - OWASP Top 10 for LLM Applications 2025
  - OWASP Agentic Security Initiative (ASI) 2026
  - OWASP Machine Learning Security Top 10 (2023)
  - OWASP Mobile Top 10 (2024)
  - OWASP API Security Top 10 (2023) + OWASP Top 10 (2021)

---

## 📋 Triad Review Disposition

Four HIGH-level findings were resolved inline at the PRD layer before sign-off (matching PRD #292 precedent):

| Finding | Source | Resolution |
|---|---|---|
| H-1 (PM) | Discussion #179 attribution framing imprecise — @armorer-labs is the **gap-analysis commenter** on #179, NOT the original requester (discussion #179 was opened by maintainer davidmatousek 2026-04-17) | US-5 + FR-5 + Q3 + R5 reworded inline to make @armorer-labs's gap-analysis-commenter role explicit. Close-comment tone discipline added ("Thanks to @armorer-labs's gap-analysis comment surfacing three pattern-catalog gaps, we shipped F-292"). |
| H1 (Architect) | Web/API "10/10" is a combined-slot narrative compression — `schemas/taxonomy/owasp.yaml` carries 6 buckets × 10 items = 60; PRD's "five-framework 50/50" compresses Web 2021 + API 2023 into one slot | **FR-1a added** mandating explicit Web/API combined-slot footnote in README hero ("OWASP Web Top 10:2021 (A01–A10) + OWASP API Security Top 10:2023 (API1–API10) — 20 items, 20/20"). FR-3 §a updated to require separate per-bucket links AND explicit per-bucket counts (60/60 broken down; restated as "five-slot 50/50" with combined Web/API slot explicit). FR-3 article CANNOT finesse the framing — must use separate Web 2021 + API 2023 anchor URLs per Architect L3. |
| H2 (Architect) | "Canonical coverage matrix" file referenced by FR-1 + FR-8 + Dependencies **DOES NOT EXIST** — only 5 distinct enumerations in `schemas/taxonomy/owasp.yaml`; no single human-readable matrix file | **Architect Option B lean adopted**: author `docs/standards/OWASP_COVERAGE.md` at `/aod.plan` Wave 0 (≤80 lines, composing per-bucket counts from `schemas/taxonomy/owasp.yaml` + ADR-024 → ADR-037 + ADR-045 lineage). FR-1 + FR-3 §c + FR-8 all re-anchored to this file. FR-11 + SC-10 allowed-file-set extended to include it. Wave 0 added to Day 1 PM timeline before Wave 1 README hero work begins. |
| M-2 (Team-Lead) | Day 1 PM Wave-1 owner cites `senior-backend-engineer (docs)` which contradicts NFR-6 writing-voice/code-voice separation thesis (writing-bound F-1 has no code agent role) | Timeline Day 1 PM owner column updated: "maintainer (with optional product-manager pair on FR-8 pre-check; **no senior-backend-engineer** per Team-Lead M-2 — F-1 is writing-bound, not code-bound, per NFR-6)". Wave 0 prerequisite for `docs/standards/OWASP_COVERAGE.md` authoring also assigned to maintainer (no code agent). |

Remaining MEDIUM/LOW findings flow into `/aod.plan` for spec.md / plan.md / tasks.md resolution:

**Architect (remaining)**:
- **M1**: FR-3 §b acceptance clarification — reproducibility anchored to per-framework Coverage Attestation PAGE (byte-deterministic per ADR-021), not narrative outputs (LLM-variable). May use 2–3 example runs to demonstrate all framework slots; single-architecture reproducibility is impossible by construction. (Partially addressed in FR-3 §b inline update; final clarification text lands in spec.md.)
- **M2**: Add to FR-7: "F-2 MUST ship `feat:`-prefixed by 2026-06-11 (NFR-5 window). If F-2 slips past the window, F-1 close-out comment MUST state the new release-cadence-restoration date." → `/aod.plan` spec.md
- **M3**: Add to FR-6 or NFR-5: "F-1 PR title MUST use `docs(296):` prefix; release-please will NOT open a release PR (per `docs:` mapping); F-1 close-out MUST verify the absence of a release PR is the EXPECTED behavior, NOT a release-please skip incident." → `/aod.plan` spec.md
- **M4**: Note FR-11's escape hatch may be needed if hero block + Web/API footnote + markdown table format exceeds 30 lines. Document escape-hatch usage in `/aod.plan` if exceeded.
- **L1**: Add SC-7 carve-out: "Matching commits require human review to confirm they ARE F-2 work; false positives on incidental references are not violations." → `/aod.plan` tasks.md
- **L2**: `/aod.plan` Wave 1 explicitly chooses README hero insertion point. Lean: between Get-Started line and "What is tachi?" H2 (around current README line 13–19).
- **L3**: Partially addressed in FR-3 §a inline update; final separate per-bucket URL list lands in spec.md.

**Product Manager (remaining)**:
- **M-1**: Recommend adding US-7 (enterprise-buyer persona, BLP-03 signal anchor) during `/aod.plan` spec.md authoring. Without this story, "manufactures the BLP-03 enterprise-buyer signal" remains a strategic claim with no acceptance criterion.
- **M-2**: Add NFR-5(d) memory carve-out as hard requirement: "Memory `feedback_aod_deliver_release_gate.md` MUST be updated to reflect the F-1-and-similar `docs:`-only carve-out — explicitly stating conditions (docs-only feature + follow-on `feat:` within ~1 week)." Add SC-13: "Memory carve-out documented before F-1 close-out." → `/aod.plan` spec.md
- **M-3**: NFR-5(c) BLP-04 strategy doc timing — minor copy edit: cross-reference happens retroactively at F-1 close (Q5 lean), not during build. → `/aod.plan` spec.md
- **L-1**: Optional US-8 prospective-contributor persona — fold into Cybersec article structure (FR-3 §f) as a single closing paragraph on contribution invitation.
- **L-2**: FR-9 material critique criterion — pre-decide what constitutes "material" to reduce in-the-moment decision burden under public pressure. → `/aod.plan` spec.md

**Team-Lead (remaining)**:
- **M-1**: FR-7/SC-7 constraint propagation explicitness — `/aod.plan` tasks.md adds T-final: "Verify SC-7 binary check passes before `/aod.deliver` invocation. If non-zero F-2 commits detected, revert before close." BLP-04 strategy doc (Q5 lean) explicitly states "F-2 PRD/spec/plan/tasks may not be drafted before F-1 close timestamp."
- **M-3**: BLP-04 strategy doc F-2 transition target — strategy doc includes "F-2 kickoff target: Fri 2026-06-05 AM or Mon 2026-06-08 AM at latest" to prevent passive slip.
- **L-1**: Day 2 drafting+self-review compression — explicit note that "self-review pass 1" can slip to Day 3 AM if drafting consumes the full day, with the article hold-period still ending Day 3 PM. → `/aod.plan` tasks.md
- **L-2**: NFR-8 self-review checklist add item: "(f) Asset-tag mention NOT present (Q4 + FR-7 enforcement)." Catches accidental scope-creep at publication gate. → `/aod.plan` spec.md
- **L-3**: Optional optimization — Discussion #179 close drafted Day 1 PM (15–30 min task) for incubation against R5 attribution-tone risk; publish Day 5 AM.

**Full review artifacts**:
- product-manager: `.aod/results/product-manager.md` (1H/3M/2L, APPROVED_WITH_CONCERNS)
- architect: `.aod/results/architect.md` (2H/4M/3L, APPROVED_WITH_CONCERNS)
- team-lead: `.aod/results/team-lead.md` (0H/3M/3L, APPROVED_WITH_CONCERNS)

**Calendar verification (Team-Lead §1)**: Independently verified via `cal 5 2026` + `cal 6 2026`. All weekday claims confirmed correct (Day 0 Thu 2026-05-28 → Day 5 Thu 2026-06-04; Buffer-1 Fri 2026-06-05; Buffer-2 Mon 2026-06-08; hard ceiling Thu 2026-06-11). **PRD #292 H1 weekend-placement defect NOT repeated** — weekend rows are explicit in the timeline table.

---

## 🤝 Sequencing Constraint (BLP-04 §3 Discipline Anchor)

This PRD anchors **BLP-04 §3 Sequencing Discipline** as a binding constraint:

**Constraint**: F-1 → F-2 sequential. F-2 (F-260b @north-echo asset-tag output wiring) MUST NOT start until F-1 (Issue #296) closes.

**Rationale**:
1. **Writing-voice vs code-voice focus preservation**: F-1 is dominated by long-form writing (LinkedIn post, ~3000-word article, Discussion close comment) and visual asset refresh (README hero, GitHub profile). F-2 is dominated by SARIF schema wiring, `risk-scorer` agent populator changes, and `finding.yaml` `affected_assets[]` plumbing. Context-switching between writing-voice and code-voice within a single working session erodes quality on both. Sequential execution preserves cognitive focus.

2. **Asset-tag announcement distinctness**: F-2 (asset-tag output wiring) merits its own distribution moment when it ships. Mentioning asset-tag mid-F-1 dilutes both the 50/50 coverage announcement (F-1 anchor) and the future asset-tag announcement (F-2 anchor). Per Q4 lean — no asset-tag mention in F-1 artifacts.

3. **Release cadence restoration**: F-1 ships `docs:` (no release PR per release-please config). F-2 ships `feat:`-eligible code (asset-tag wiring restores `feat:` cadence). Sequencing F-1 → F-2 means the release-cadence break (NFR-5) lasts ~1 week, not multiple weeks.

**Enforcement** (FR-7 + SC-7):
- No F-2 branch (`297-*` or similar) created before Issue #296 close timestamp.
- No commits on any branch referencing F-2 / F-260b / asset-tag wiring before Issue #296 close.
- No `/aod.discover` capture or `/aod.define` invocation for F-2 before Issue #296 close.
- SC-7 binary verification: `git log --all --grep="F-2|F-260b|asset-tag wiring" --since="2026-05-28"` returns zero commits before Issue #296 close timestamp.

**User directive (2026-05-28)**: "Per BLP-04 §3 Sequencing Discipline, do not start F-2 in parallel — sequence F-1 → F-2 to preserve writing-voice vs code-voice focus."

This directive is binding for the duration of F-1.
