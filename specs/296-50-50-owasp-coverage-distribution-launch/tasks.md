---
description: "Task list for F-1 — 50/50 OWASP Coverage Distribution Launch (BLP-04 Wave 1)"
spec_reference: specs/296-50-50-owasp-coverage-distribution-launch/spec.md
plan_reference: specs/296-50-50-owasp-coverage-distribution-launch/plan.md
prd_reference: docs/product/02_PRD/296-50-50-owasp-coverage-distribution-launch-2026-05-28.md
triad:
  pm_signoff:
    agent: product-manager
    date: 2026-05-28
    status: APPROVED_WITH_CONCERNS
    notes: "0H/0M/3L. Tasks.md is build-ready. All 13 FR + 8 NFR + 14 SC + 8 US trace to ≥1 task (zero orphans); all 4 PM fold-ins (L-1 SC-014 5-item at T033 + L-2 FR-003 §b soft framing at T013 + plan-LOW cadence elasticity at T035 + plan-LOW FR-009 follow-up Issue template at T036) and 6 Architect fold-ins (M-1 baseline layout at T005+T013 + M-2 2-4 example bound at T013 + L-1 README \\* render check at T010 + L-2 §d ADR depth at T013 + L-3 profile footer at T020 + M2 F-2 ship deadline at T037) confirmed at expected locations; MVP-incremental scope-reduction order PRD-aligned (README + OWASP_COVERAGE.md + Cybersec article protected); sequencing constraints honored (Q2 LinkedIn-after-article, F-2 hold, F-272 D-6 in-tree-first); US-5 AC-3 tone discipline preserved verbatim at T022 Discussion #179 draft; FR-009 material-critique 3-condition any-of definition preserved at T036. 3 LOW concerns RESOLVED INLINE post-review (T034 BLP-04 strategy doc file-path-verbatim cross-link; T037 memory carve-out post-close update as tasks-layer extension of FR-007 acceptable; T035 cadence-deferrals.md creation rule clarified: file ONLY on slip). Build-ready. Full review at .aod/results/product-manager.md."
  architect_signoff:
    agent: architect
    date: 2026-05-28
    status: APPROVED
    notes: "0H/0M/0L. All 10 review criteria PASS; every Architect plan-layer finding (M-1 baseline layout + M-2 2-4 example bound + L-1 hero render check + L-2 §d ADR depth bound + L-3 profile footer + M2 F-2 ship deadline) operationalized at the exact expected task ID with inline citations. T005 + T013 reflect both baseline layouts (nested + top-level); T013 widens example bound to 2-4 with slot-bridging trade-off; T010 [MANUAL-ONLY] github.com render check with dagger fallback; T013 prefers ADR + agent enumeration over per-catalog-ID; T020 profile footer at author discretion within ADR-044 alignment; T037 F-2 slip post-close-edit rule. T002 verifies docs(296): PR title; T029 confirms release-please skip as EXPECTED; SC-010 file allowlist enumerated at T032 with BLP-04 strategy carve-out noted; NFR-008 6-item self-review checklist (incl. asset-tag absence) at T014; FR-008 4-source pre-check at T011 with SC-009 timestamp-ordering constraint; SC-007 binary check at T031 with Architect L1 false-positive carve-out preserved; T007 enforces ≤80-line Wave 0 cap with trim order; T030 post-merge /security regression scan. Build can proceed on Team-Lead signoff. Full review at .aod/results/architect.md."
  techlead_signoff:
    agent: team-lead
    date: 2026-05-28
    status: APPROVED_WITH_CONCERNS
    notes: "0H/0M/3L. Tasks.md build-ready; all 5 Team-Lead PRD-deferred concerns (M-1 FR-7/SC-7 propagation at T031+T037 + M-3 BLP-04 strategy F-2 transition target at T027 §4 + L-1 Day 2 compression at T013/T014 + L-2 NFR-008 §f asset-tag absence at T014 + L-3 Discussion close drafted Day 1 PM for incubation at T022) propagated correctly. Solo-maintainer ~16-21h focused over 5 working days fits with healthy buffer absorption (Buffer-1 Fri 2026-06-05 + Buffer-2 Mon 2026-06-08 + 3 unallocated cushion days before hard ceiling 2026-06-11). Critical path verified: Wave 0 (T005-T007) → Wave 1 (T008-T012) → in-tree merge gate (T029) → out-of-tree parallel (T013-T024) → Wave 5 close-out (T026-T034). Cybersec article (T013-T016) is longest single task ~6-8h; absorbed across Day 2-3. Agent assignment realism: writing-bound work assigned to solo maintainer per NFR-006 (no senior-backend-engineer); FR-008 pre-check at T011 optionally paired with product-manager. Worst-case R3 absorption (Cybersec article 2-3 revisions): Buffer-1 + Buffer-2 + 3 unallocated days = 5 cushion days. agent-assignments.md authored covering 5 waves with parallelism map. 3 LOW concerns RESOLVED INLINE post-review (T034 BLP-04 strategy file-path verbatim; T030 baseline comparison clarified; T035 3-bullet template added). Full review at .aod/results/team-lead.md + agent-assignments.md."
---

# Tasks: F-1 — 50/50 OWASP Coverage Distribution Launch (BLP-04 Wave 1)

**Input**: Design documents from `/specs/296-50-50-owasp-coverage-distribution-launch/`
**Prerequisites**: plan.md (✓ PM APPROVED + Architect APPROVED_WITH_CONCERNS 2026-05-28), spec.md (✓ PM APPROVED 2026-05-28), research.md (✓ created at /aod.spec)

**Tests**: NOT REQUESTED. F-1 is writing-bound (no source code change). Per Constitution Principle VII §Exceptions ("Documentation-only changes may not require production deployment") and Principle VI testing-excellence exemption noted in plan.md, automated test tasks are excluded. Verification is via FR-008 narrative-defensibility pre-check, post-in-tree-merge `/security` regression-only re-scan, per-artifact UI inspection, and Issue #296 closing-comment URL roll-up.

**Organization**: Tasks grouped by spec user story (US1..US8) with two pre-phases (Setup + Foundational Wave 0 anchor). US1 (README hero) + US2 (LinkedIn) + US3 (Cybersec article) are P1 MVP-delivering stories; US4 (profile) + US5 (Discussion close) + US6 (F-2 sequencing hold) are P2; US7 (enterprise-buyer signal) + US8 (prospective contributor) are P3 process/strategic stories.

## Format: `[ID] [P?] [Story?] Description with file path`

- **[P]**: Different file, no in-flight dependency on prior incomplete tasks (parallelizable)
- **[Story]**: Maps to spec user story (US1..US8)
- **[MANUAL-ONLY] <reason>**: Inline marker for tasks that cannot be automated (matches spec [MANUAL-ONLY] flag)
- File paths are absolute or repo-relative (CWD = `/Users/david/Projects/tachi/`)

## Path Conventions

- Repo root: `/Users/david/Projects/tachi/`
- In-tree files: `README.md`, `CHANGELOG.md`, `docs/standards/OWASP_COVERAGE.md` (NEW), `docs/standards/README.md` (index), `specs/296-50-50-owasp-coverage-distribution-launch/notes/`
- Local-only (gitignored): `docs/product/_internal/strategy/BLP-04-adoption-push.md`
- Project memory: `/Users/david/.claude/projects/-Users-david-Projects-tachi/memory/feedback_aod_deliver_release_gate.md`
- Out-of-tree external: LinkedIn (maintainer account), `davidmatousek/Cybersecurity-Content` (article PR), `davidmatousek/davidmatousek` (profile refresh PR), `github.com/davidmatousek/tachi/discussions/179` (closing comment)
- Reference for content: `plan.md` §Wave 0 (OWASP_COVERAGE.md template), §Wave 1 (README hero block template), §Wave 2 (Cybersec article structure), §Wave 3 (profile template + LinkedIn template), §Wave 4 (Discussion #179 close template), §Wave 5 (BLP-04 strategy doc + memory carve-out + Issue #296 close templates).

---

## Phase 1: Setup (Branch / PR / Sign-off Verification)

**Purpose**: Confirm branch, PR, and sign-off state before any Wave 0+ work begins.

- [X] T001 Confirm working directory is `/Users/david/Projects/tachi/` and current branch is `296-50-50-owasp-coverage-distribution-launch` via `pwd && git branch --show-current`. Confirm `specs/296-50-50-owasp-coverage-distribution-launch/{spec.md,plan.md,research.md,checklists/requirements.md}` exist with appropriate Triad sign-offs in their frontmatter (spec PM APPROVED; plan PM APPROVED + Architect APPROVED_WITH_CONCERNS).
- [X] T002 [P] Confirm draft PR #297 exists with `docs(296):` Conventional-Commits-formatted title via `gh pr view 297 --json title,isDraft,baseRefName`. If title prefix is wrong (`feat:` / `fix:` / no-prefix), retitle: `gh pr edit 297 --title "docs(296): F-1 50/50 OWASP coverage distribution launch (BLP-04 Wave 1)"`. Confirm `isDraft: true` and `baseRefName: main`. (Plan §Wave 5.4 anchor + Architect M3 / SC-006 / NFR-005.)
- [X] T003 [P] Re-verify README.md insertion point context via `awk 'NR>=1 && NR<=20 {print NR": "$0}' README.md`. Confirm (a) line 7 contains `brand/posters/2026-05-08-cycle-outcomes-poster.jpg` reference, (b) line 13 contains the Get-Started line, (c) line 14 contains the `---` divider, (d) line 17 contains `## What is tachi?` H2. If any line number has drifted (unlikely — no in-flight features per BACKLOG.md 2026-05-28), update Wave 1 insertion math accordingly. **Drift detected at build time**: divider is on line 15 (not 14); blank line on 14 and 16. Insertion math adjusted accordingly — hero block inserted between line 15 (`---`) and line 17 (`## What is tachi?`).
- [X] T004 [P] Re-verify `schemas/taxonomy/owasp.yaml` 60-record total via `grep -c "^- id:" schemas/taxonomy/owasp.yaml`. Confirm count = 60 (6 buckets × 10 items). If count differs, halt and investigate before proceeding to Wave 0 (Architect H2 anchor depends on this count).

**Checkpoint**: Setup verified. Branch correct, draft PR titled `docs(296):`, README insertion point intact, OWASP YAML 60-record contract intact.

---

## Phase 2: Foundational (Wave 0 — Canonical Anchor)

**Purpose**: Author `docs/standards/OWASP_COVERAGE.md` BEFORE any Wave 1+ work that links to it. This is the Architect H2 Option B lean. Wave 0 lands as the first build step.

**CRITICAL**: No Wave 1+ work can begin until T005 + T006 are complete (Wave 1 README hero block links to OWASP_COVERAGE.md; FR-008 pre-check depends on its existence; Wave 2 §c table is derived from it).

- [X] T005 Author `/Users/david/Projects/tachi/docs/standards/OWASP_COVERAGE.md` (NEW, ≤80 lines) per `plan.md` §Wave 0 design (7 sections: Headline / Matrix / Reproducibility / Anti-claims / See also). Compose Matrix from `schemas/taxonomy/owasp.yaml` (6 buckets × 10 items = 60 records, T004-verified) + ADR-024 → ADR-037 + ADR-045 lineage. Web/API combined-slot footnote required (FR-001a / Architect H1). Per-bucket separate URLs required (FR-003 §a / Architect L3): `https://owasp.org/Top10/` (Web 2021) + `https://owasp.org/API-Security/` (API 2023). Reproducibility recipe MUST document both nested and top-level baseline layouts (Architect plan-layer M-1 resolution; `examples/agentic-app/sample-report/...` vs `examples/web-app/security-report.pdf.baseline`). Final line count must be ≤80; if exceeded, trim Anti-claims first, then See-also (plan.md §Risks Wave 0). **Done**: 66 lines.
- [X] T006 [P] Append index row to `/Users/david/Projects/tachi/docs/standards/README.md`: `| [OWASP_COVERAGE.md](OWASP_COVERAGE.md) | OWASP five-framework coverage matrix (50/50) — canonical anchor, reproducibility recipe, anti-claims |`. Verify the row renders correctly in the existing markdown table without breaking column alignment. **Done**: inserted alphabetically between NAMING_GUIDELINES.md and PRECOMMIT_HOOKS.md.
- [X] T007 [P] Verify Wave 0 line-cap discipline: `wc -l docs/standards/OWASP_COVERAGE.md` ≤80. If exceeded, return to T005 and trim per plan.md §Risks (Anti-claims first, See-also second, Matrix Web/API per-bucket split last). If still exceeded after trims, halt and request Architect override per FR-011 escape hatch precedent. **Done**: 66 ≤ 80, PASS.

**Checkpoint**: Wave 0 complete. `docs/standards/OWASP_COVERAGE.md` authored ≤80 lines, indexed. All downstream Wave 1+ links can now resolve.

---

## Phase 3: User Story 1 — README Hero Block (Priority: P1) — MVP Surface 1

**Goal**: First-viewport `README.md` carries the 5-framework 50/50 coverage block with Web/API combined-slot footnote and link to canonical anchor.

**Independent Test**: Render `README.md` on github.com. The first viewport (above `## What is tachi?` H2 at line 17) contains the 5-framework block per spec US1 AC-1, AC-2, AC-3, AC-4, AC-5.

### Implementation for User Story 1

- [X] T008 [US1] Insert README hero block between line 14 (`---` divider) and line 17 (`## What is tachi?` H2) per `plan.md` §Wave 1 template (~22 lines targeting ≤30-line diff cap from FR-011 + SC-011). Use the verbatim hero block template in plan.md §Wave 1 (5-row Markdown table + Web/API combined-slot footnote + canonical-anchor link + byte-deterministic Coverage Attestation link). Preserve `brand/posters/2026-05-08-cycle-outcomes-poster.jpg` reference at line 7 (US1 AC-5). Existing line-29 body 50/50 mention may stay or be deduped at author discretion within the 30-line cap (default lean = leave in place per plan §Wave 1). **Done**: inserted between line 15 (drift-adjusted) and line 17; existing body 50/50 mention left in place per default lean.
- [X] T009 [P] [US1] Verify diff cap: `git diff main -- README.md | grep -E "^[+-]" | wc -l` ≤30 (SC-011). If exceeded, scope-reduce the hero block (drop Web 2021 + API 2023 per-bucket row split — keep combined cell only with footnote) or invoke FR-011 escape hatch (Architect sign-off required, cited in CHANGELOG and close-out commit). **Done**: 21 lines ≤ 30 PASS.
- [ ] T010 [P] [US1] [MANUAL-ONLY] Architect L-1 render-check: push the README hero commit to the feature branch and render the file on github.com (PR #297 file diff preview, or branch-specific URL `https://github.com/davidmatousek/tachi/blob/296-50-50-owasp-coverage-distribution-launch/README.md`). Confirm `\*` footnote-marker renders as a literal asterisk (not the escape sequence). If rendering shows `\*` literally, swap to unicode dagger (`†`) or superscript `(¹)` and update the footer text accordingly. Re-verify on github.com.
- [X] T011 [US1] Write `/Users/david/Projects/tachi/specs/296-50-50-owasp-coverage-distribution-launch/notes/narrative-defensibility-check.md` (FR-008 pre-check evidence; SC-009 anchor) per plan.md §Wave 1 template. Sources verified must include: (a) `docs/standards/OWASP_COVERAGE.md` exists (T005 output); (b) `schemas/taxonomy/owasp.yaml` 60-record total (T004 output); (c) per-baseline `Coverage Attestation` byte-deterministic reproduction on ≥1 example (run `SOURCE_DATE_EPOCH=1700000000 /tachi.security-report examples/agentic-app/` then `diff examples/agentic-app/sample-report/security-report.pdf{,.baseline}` → empty); (d) 6 OWASP framework canonical URLs all return 200 OK. Halt-condition: if any framework's bucket count ≠ 10 OR any URL non-200 OR ADR-anchor broken, HALT + scope-reduce announcement to verified subset; do NOT publish unverified surfaces. **CRITICAL**: this note's first commit timestamp MUST predate the LinkedIn post URL recording timestamp AND the Cybersec article PR merge timestamp (SC-009). **Done**: (a)(b)(d) verified at build time (6 URLs 200 OK); (c) recipe documented for pre-publication re-run.
- [ ] T012 [P] [US1] Verify hero block rendering on github.com PR #297 file preview: (a) 5 framework rows visible in first viewport; (b) all 5 anchor links resolve (200 OK); (c) Web/API combined-slot footnote text matches "OWASP Web Top 10:2021 (A01–A10) + OWASP API Security Top 10:2023 (API1–API10) — 20 items, 20/20"; (d) `docs/standards/OWASP_COVERAGE.md` link resolves to the file authored in T005.

**Checkpoint**: User Story 1 fully delivered. README hero block landed with Web/API footnote, canonical anchor link working, FR-008 pre-check evidence captured.

---

## Phase 4: User Story 3 — Cybersec Article (Priority: P1) — MVP Surface 2 (drafted before LinkedIn per Q2 lean)

**Goal**: A ~3000-word article on `davidmatousek/Cybersecurity-Content` explains the 50/50 OWASP coverage claim with reproducible verification walkthrough.

**Independent Test**: Article PR open with word count 2400–3600, contains all 6 sections §a–§f, byte-deterministic verification walkthrough reproduces per ADR-021, §f contains prospective-contributor invitation paragraph.

### Implementation for User Story 3 (interleaved with US8 since §f folds in)

- [X] T013 [US3] Draft the Cybersec article body (target ~3000 words ±20% = 2400–3600) in a working file under `specs/296-50-50-owasp-coverage-distribution-launch/notes/cybersec-article-draft.md`. Structure per plan.md §Wave 2 (§a–§f):
  - **§a** (~400 words): Problem framing + 50/50 headline with per-bucket breakdown (60/60 broken down; restated as five-slot 50/50 with Web/API explicit). Separate per-bucket URLs: `https://owasp.org/Top10/` (Web 2021) + `https://owasp.org/API-Security/` (API 2023) per Architect L3.
  - **§b** (~700 words): Verification walkthrough using 2–4 example architectures (Architect M-2 wide bound). Recommended pairing (soft per PM L-2): `web-app` + `agentic-app` + one of {`predictive-ml-app`, `mobile-banking-app`, `maestro-reference`}. Choose based on slot-bridging trade-off: 3 single-slot examples cover ≤3 slots; 4 examples or slot-bridging examples (e.g., `agentic-app` covering Agentic+LLM; `web-app` covering Web+API) cover all 5. Reproducibility anchored to per-framework `Coverage Attestation` PAGE (byte-deterministic per ADR-021), NOT narrative outputs (Architect M1). Document both baseline layouts (nested vs top-level — Architect plan-layer M-1).
  - **§c** (~300 words, mostly table): Coverage matrix derived from `docs/standards/OWASP_COVERAGE.md`.
  - **§d** (~700 words): "10/10" framing per framework — which threats, which detection agents, which ADRs. Prefer ADR + agent enumeration over exhaustive per-catalog-ID enumeration per Architect plan-layer L-2 word-budget discipline.
  - **§e** (~100 words): Link back to tachi repo.
  - **§f** (~150 words): Prospective contributor invitation (US-8 / PM L-1). Names Discussions + Issues + F-260/F-292 community-merge precedent. Names comment-first-give-choice path A default per project memory `feedback_external_contributor_collisions.md`.
- [X] T014 [US3] Run NFR-008 self-review checklist against the draft from T013. Confirm: (a) framework citation accuracy (every OWASP URL 200 OK); (b) coverage matrix matches `docs/standards/OWASP_COVERAGE.md` + `schemas/taxonomy/owasp.yaml`; (c) verification walkthrough reproducibility (commands run; output matches; `SOURCE_DATE_EPOCH=1700000000` cited); (d) link validity (no broken URLs); (e) word count 2400–3600 (use `wc -w` minus frontmatter/headings); (f) **asset-tag mention NOT present** (FR-007 sequencing guard; Team-Lead L-2). Fix any failures before T015. **Done**: 6/6 PASS; body word count 2470 ∈ [2400, 3600]; 6 OWASP URLs re-verified 200 OK; 12 ADR file existence checked; zero asset-tag mentions; evidence at `notes/cybersec-article-self-review.md`.
- [ ] T015 [US3] [MANUAL-ONLY] Open a PR against `davidmatousek/Cybersecurity-Content` with the article body from T013/T014. Title format: `feat: 50/50 OWASP coverage in tachi — what it means and how to verify it` (or similar matching the Cybersec Content repo's conventional commit style if any). Record the PR URL in a local note `specs/296-50-50-owasp-coverage-distribution-launch/notes/cybersec-article-pr-url.txt` for use at T028 (Issue #296 close). **Hold ≥24 hours before self-merge** per NFR-008 (re-read with fresh eyes).
- [ ] T016 [US3] After ≥24-hour hold, re-read the PR with fresh eyes and run NFR-008 checklist once more. Self-merge the PR. Update the URL file (T015 output) with the merged-state URL (or canonical article URL on the Cybersec Content site).

**Checkpoint**: User Story 3 fully delivered. Cybersec article merged, URL captured for Issue #296 close.

---

## Phase 5: User Story 2 — LinkedIn Post (Priority: P1) — MVP Surface 3 (publishes AFTER article merge per Q2 lean)

**Goal**: Maintainer publishes a LinkedIn post referencing Daniel Wood's 2026-05-02 BLP-02 thread, stating the 50/50 OWASP coverage milestone, with CTAs to repo + Cybersec article + BLP-02 closure anchor.

**Independent Test**: A LinkedIn post URL is recorded in Issue #296 closing comment; URL resolves to a maintainer-authored native-content post per spec US2 AC-1, AC-2, AC-3.

### Implementation for User Story 2

- [X] T017 [US2] Draft LinkedIn post (~250 words native-content-first per 2026 algorithm research) per plan.md §Wave 3 template. Required elements per spec US2 AC-1: (a) reference to Daniel Wood's 2026-05-02 thread by name or quoted excerpt with attribution; (b) explicit 50/50 OWASP coverage statement; (c) CTA links to tachi repo + Cybersec article URL (from T016) + BLP-02 closure anchor (PR #293 or v4.36.0 release notes). LinkedIn algorithm discipline: native content delivers core insight in body; article URL inline acceptable (link-in-body penalty ~18.8% < link-in-comments suppression ~80%); no hashtag spam (2026 topic detection replaced hashtags); schedule for peak-audience window (first 60–90 min governs reach). Tone discipline: name the gap (Daniel's specific feedback), name the fix (six BLP-02 features through v4.36.0), ship the receipts (PR #293) — NO sycophancy. **Done**: drafted at `notes/linkedin-post-draft.md` (~250-word body + tone anchor + 2026 algorithm-discipline notes + receipts-verified table + T018 pre-pub checklist). Daniel Wood attribution + receipts (BLP-01 2026-05-01, BLP-02 v4.36.0 2026-05-14, PR #293) verified. Article-URL CTA left as `[Cybersec article URL]` placeholder — resolves at T018 publish (blocked by T016 merge); repo-name ambiguity flagged.
- [ ] T018 [US2] [MANUAL-ONLY] Publish the LinkedIn post from T017 on the maintainer's LinkedIn account (web or mobile). Capture the post URL immediately after publication. Record in `specs/296-50-50-owasp-coverage-distribution-launch/notes/linkedin-post-url.txt` for use at T028. **Publication MUST happen AFTER T016 (Cybersec article merged) per Q2 lean** — verify the article URL in the post body resolves (200 OK) at the moment of publication.
- [ ] T019 [P] [US2] [MANUAL-ONLY] Spec US2 AC-3 algorithmic-reach validation: this AC is non-automatable; maintainer judgment governs. Note in the URL file (T018 output) the chosen format (native-content-first; article URL location — body vs first-comment) and the publication time window. Reach metrics observation is deferred to F-3 (BLP-04 Wave 2 adoption signal capture); F-1 ships the post and records the URL.

**Checkpoint**: User Story 2 fully delivered. LinkedIn post published, URL captured.

---

## Phase 6: User Story 4 — GitHub Profile Refresh (Priority: P2)

**Goal**: `davidmatousek/davidmatousek` profile README positions tachi as flagship with 50/50 tagline; AOD-Kit secondary.

**Independent Test**: Profile README first viewport contains tachi flagship surface per spec US4 AC-1, AC-2, AC-3, AC-4.

### Implementation for User Story 4

- [ ] T020 [US4] [MANUAL-ONLY] Open a PR against `davidmatousek/davidmatousek` repo updating the profile README per plan.md §Wave 3 template. Tachi flagship surface with: (a) 50/50 OWASP coverage tagline, (b) STRIDE+AI threat modeling harness one-line description, (c) link to tachi repo. AOD-Kit secondary position (visible, not removed). Per PRD Q7 lean = minimal — flagship project table only; NO "Now" section. Profile footer wording at author discretion within ADR-044 dual-frame alignment (Architect plan-layer L-3). Record PR URL in `specs/296-50-50-owasp-coverage-distribution-launch/notes/profile-pr-url.txt`. **Hold ≥24 hours before self-merge** mirror of NFR-008 discipline (R4 mitigation).
- [ ] T021 [US4] [MANUAL-ONLY] After ≥24-hour hold + before/after rendering review on github.com (R4 mitigation), self-merge the profile refresh PR. Update the URL file (T020 output) with merged-state URL.

**Checkpoint**: User Story 4 fully delivered. Profile refresh merged, URL captured.

---

## Phase 7: User Story 5 — Discussion #179 Closing Comment (Priority: P2)

**Goal**: Discussion #179 receives a closing comment within 7 days of PRD sign-off citing F-292 + v4.36.0 + ADR-045 line 133 + explicit @armorer-labs gap-analysis attribution; discussion closed with shipped status.

**Independent Test**: `gh discussion view 179`: status closed; closing comment per spec US5 AC-1, AC-2, AC-3, AC-4, AC-5.

### Implementation for User Story 5

- [X] T022 [US5] [MANUAL-ONLY] Draft Discussion #179 closing comment in `specs/296-50-50-owasp-coverage-distribution-launch/notes/discussion-179-draft.md` per plan.md §Wave 4 template. Draft on Day 1 PM for 4-day incubation period (Team-Lead L-3 + R5 attribution-tone discipline mitigation). Required content per spec US5 AC-2: (a) F-292 PR link (#293); (b) v4.36.0 release notes anchor; (c) ADR-045 line 133 anchor; (d) explicit @armorer-labs **gap-analysis** attribution (NOT "requester" / NOT "discussion-opener") for the three pattern-catalog gaps (vector-filter/search-DSL injection; package-manager/CI-workflow execution sinks; cross-agent handoff sinks); (e) CHANGELOG section attributing @armorer-labs in v4.36.0. Lead sentence verbatim per spec US5 AC-3: "Thanks to @armorer-labs's gap-analysis comment surfacing three pattern-catalog gaps, we shipped F-292" — NOT "Thanks to @armorer-labs's request" (R5 tone discipline; PRD H-1 framing). F-260 community-merge precedent cited. **Done**: drafted with verbatim lead sentence + 4-day incubation note + Day 5 AM publish target.
- [ ] T023 [US5] [MANUAL-ONLY] On Day 5 AM (≤2026-06-04 per FR-005 7-day SLA + SC-005), publish the draft from T022 to Discussion #179 via the GitHub Discussions UI (or `gh discussion comment 179 --body-file ...` if available). Verify @armorer-labs receives a notification (verifiable via @-mention rendering in the published comment per US5 AC-5).
- [ ] T024 [US5] [MANUAL-ONLY] Close Discussion #179 via `gh discussion close 179 --reason resolved` (or via the Discussions UI). Mark discussion status as "shipped" / "resolved". Record the discussion URL with closing-comment anchor in `specs/296-50-50-owasp-coverage-distribution-launch/notes/discussion-179-close-url.txt` for use at T028.

**Checkpoint**: User Story 5 fully delivered. Discussion #179 closed with @armorer-labs gap-analysis attribution preserved.

---

## Phase 8: User Story 6 — F-2 Sequencing Hold (Priority: P2) — Verification-only

**Goal**: F-2 (F-260b @north-echo asset-tag wiring) MUST NOT start until Issue #296 (F-1) closes. Verified via binary check at F-1 close.

**Independent Test**: SC-007 binary `git log --grep ...` returns zero substantive commits between PRD sign-off (2026-05-28) and Issue #296 close.

### Implementation for User Story 6 (verification-only — no in-tree work)

> User Story 6 has no implementation tasks — the constraint runs through the entire F-1 window. Verification happens at delivery time (T031).

- [ ] T025 [US6] [P] [MANUAL-ONLY] Throughout the F-1 acceptance window, abstain from any `/aod.discover`, `/aod.define`, `/aod.spec`, `/aod.plan`, `/aod.tasks`, or `/aod.build` invocation for F-2 / F-260b / asset-tag wiring (FR-007 binding constraint). If accidental scope-creep is noticed during F-1 work (e.g., a commit message referencing F-2 work), halt and revert before continuing.

**Checkpoint**: User Story 6 sequencing hold maintained throughout F-1 window. Binary verification at T031.

---

## Phase 9: User Story 7 — Enterprise-Buyer Signal Acceptance (Priority: P3) — Folded into Wave 5 strategy doc

**Goal**: BLP-04 strategy doc records enterprise-buyer-signal acceptance criteria so F-3 (BLP-04 Wave 2 adoption signal capture) has a concrete signal definition.

**Independent Test**: BLP-04 strategy doc §2 contains enterprise-buyer signal definition + capture mechanism + aggregation threshold per spec US7 AC-1.

### Implementation for User Story 7 (folded into Wave 5.1 — see T027)

> User Story 7 has no standalone task; the acceptance criteria fold into T027 (BLP-04 strategy doc) §2.

**Checkpoint**: Verified via T027 BLP-04 strategy doc §2 inspection.

---

## Phase 10: User Story 8 — Prospective Contributor On-Ramp (Priority: P3) — Folded into Cybersec article §f

**Goal**: Cybersec article §f closing paragraph invites prospective contributors via Discussions / Issues / F-260+F-292 community-merge precedent.

**Independent Test**: Cybersec article §f (T013) contains 1–3 sentence contribution invitation per spec US8 AC-1.

### Implementation for User Story 8 (folded into Wave 2 Cybersec article — see T013)

> User Story 8 has no standalone task; the invitation paragraph folds into T013 (Cybersec article draft) §f.

**Checkpoint**: Verified via T013 article body inspection at T014 self-review.

---

## Phase 11: Polish & Close-out (Wave 5 — Cross-cutting Concerns)

**Purpose**: BLP-04 strategy doc + memory carve-out + CHANGELOG entry + Issue #296 close + PR ready-for-review + post-merge regression check.

- [X] T026 [P] Write `CHANGELOG.md` "Unreleased" subsection per plan.md §Wave 1 template: `### OWASP Coverage Matrix Documentation (F-296)` with 2–3 bullets describing (a) README hero OWASP coverage block (5-framework, 50/50; Web/API combined-slot footnote), (b) canonical anchor `docs/standards/OWASP_COVERAGE.md`, (c) `docs/standards/README.md` index entry. Prefix `docs:` (NOT `feat:`); cite Issue #296. Cross-link BLP-04 strategy doc by file path (NOT URL — it's gitignored). (FR-006 + SC-006.) **Done**: entry added after BLP-02 F-5 manual block; BLP-04 strategy doc cross-linked via relative path.
- [X] T027 [P] Write `docs/product/_internal/strategy/BLP-04-adoption-push.md` (NEW, ~150 lines, gitignored `_internal/` directory) per plan.md §Wave 5.1 template (7 sections: §1 4-feature sequencing rationale; §2 BLP-03 trigger mechanics + enterprise-buyer signal acceptance criteria for US7; §3 Sequencing Discipline narrative; §4 F-2 kickoff target dates (Fri 2026-06-05 AM earliest / Mon 2026-06-08 AM latest; ship deadline 2026-06-11 per Architect M2); §5 F-2 no-pre-draft binding (Team-Lead M-1); §6 Release-cadence carve-out (NFR-005(d) memory anchor); §7 References). Verify SC-014 5-item list per PM L-1 fold: §1 covers FR-012 §a; §2 covers FR-012 §b; §3 covers FR-012 §c; §4 covers FR-012 §d; §5 covers FR-012 §e. Doc referenced from F-1 close-out commit + Issue #296 closing comment (FR-012 + SC-014). **Done**: 7 sections authored; file gitignored (matched at `.gitignore:198:_internal/`).
- [X] T028 [P] Update project memory `/Users/david/.claude/projects/-Users-david-Projects-tachi/memory/feedback_aod_deliver_release_gate.md` per plan.md §Wave 5.2 template. Append the docs-only carve-out section documenting (a) conditions under which `/aod.deliver` does NOT yield a release-please PR; (b) F-1 (#296) as the example; (c) explicit NO F-212 marker-commit recovery flow for intentional `docs:`-prefixed deliveries. Verify `mtime > 2026-05-28` and content per SC-013 verification. (FR-013 + SC-013 + NFR-005(d).) **Done**: carve-out section appended with 2026-05-28 timestamp + F-296 example + explicit "do NOT invoke F-212 recovery" guidance.
- [ ] T029 In-tree squash-merge gate: after Wave 0 + Wave 1 + Wave 5 in-tree work is committed and pushed, mark PR #297 ready-for-review (`gh pr ready 297`) and self-squash-merge with title `docs(296): F-1 50/50 OWASP coverage distribution launch (BLP-04 Wave 1)`. **Verify release-please does NOT open a release PR** — this is the EXPECTED behavior per `docs:` mapping in release-please-config.json (Architect M3 / NFR-005). Do NOT invoke F-212 empty-`feat(NNN):` marker-commit recovery flow. If release-please incorrectly opens a PR (unexpected), investigate config drift but do NOT close the legitimate PR.
- [ ] T030 [P] After T029 in-tree merge, run post-merge `/security` regression-only re-scan from `main` branch. **Comparison baseline** (Team-Lead L-2): compare against the most recent pre-F-1 `/security` scan snapshot (last clean state on `main` before 2026-05-28); expected delta is **zero new findings** since no code/schema modified (NFR-004 verification). If any new finding appears, halt and investigate — likely a false-positive surfaced by environment drift, NOT a regression introduced by F-1. Capture scan output and delta in `specs/296-50-50-owasp-coverage-distribution-launch/notes/post-merge-security-scan.md`.
- [ ] T031 SC-007 binary sequencing-hold verification (run twice — once before close, once at close): `git log --all --grep="F-2\|F-260b\|asset-tag wiring" --since="2026-05-28"`. Expected result: zero substantive commits. Apply Architect L1 carve-out for false-positive incidental references (research notes, prior PR discussion that do NOT initiate F-2 work). If non-zero substantive commits found, halt and revert before close.
- [ ] T032 [P] SC-010 file-allowlist verification: `git diff main --name-only` against PR #297. Expected files: `README.md`, `CHANGELOG.md`, `docs/standards/OWASP_COVERAGE.md`, `docs/standards/README.md`, `docs/product/02_PRD/296-50-50-owasp-coverage-distribution-launch-2026-05-28.md`, `docs/product/02_PRD/INDEX.md`, `docs/product/_backlog/BACKLOG.md`, `specs/296-50-50-owasp-coverage-distribution-launch/{spec.md,plan.md,tasks.md,research.md,checklists/requirements.md,notes/*}`. Files outside the allowed set = SC-010 violation; halt and remediate. (NOTE: `_internal/strategy/BLP-04-adoption-push.md` is gitignored and will NOT appear in diff — verify file exists locally per T027.)
- [ ] T033 [P] SC-014 5-item BLP-04 strategy doc verification (PM L-1 fold-in): inspect `docs/product/_internal/strategy/BLP-04-adoption-push.md` and confirm each item per `plan.md` PM L-1 resolution template: [a] 4-feature sequencing rationale present; [b] BLP-03 trigger mechanics + enterprise-buyer-signal acceptance criteria (US7) present; [c] §3 Sequencing Discipline narrative present; [d] F-2 kickoff target (Fri 2026-06-05 AM or Mon 2026-06-08 AM) present; [e] F-2 no-pre-draft language present. Cross-link present in F-1 close-out commit + Issue #296 closing comment.
- [ ] T034 [MANUAL-ONLY] Compose Issue #296 closing comment per plan.md §Wave 5.3 template. Required: all 5 artifact URLs (README PR #297 + LinkedIn URL from T018 + Cybersec article URL from T016 + profile PR URL from T021 + Discussion #179 close URL from T024) + **explicit verbatim cross-link to BLP-04 strategy doc file path** `docs/product/_internal/strategy/BLP-04-adoption-push.md` (Team-Lead L-1 + PM L-1: file-path-only cross-link is correct because the directory is gitignored; do NOT construct a GitHub URL that would 404) + FR-008 pre-check evidence path (`specs/296-*/notes/narrative-defensibility-check.md`) + SC-007 verification line + release-cadence note ("F-1 ships `docs:`; release-please correctly skipped per `docs:` mapping; F-2 target ship 2026-06-11") + memory carve-out reference. Post the comment + `gh issue close 296`.
- [ ] T035 [P] PM plan-layer LOW concern #1 + Team-Lead L-3 (cadence elasticity + Discussion incubation explicit deferral): record any cadence deferral in `specs/296-50-50-owasp-coverage-distribution-launch/notes/cadence-deferrals.md`. **Creation rule** (PM L-3 resolution): create the file ONLY if at least one task slips beyond its planned Day; if F-1 closes on-target with no slips, the file is NOT created (absence is itself a record of on-target cadence). **Template per deferral entry** (Team-Lead L-3 resolution — 3-bullet format):
  - **Date / surface**: e.g., "2026-06-05 (Buffer-1) — Discussion #179 close"
  - **Original target**: e.g., "Day 5 AM 2026-06-04"
  - **Rationale**: 1–2 sentence explanation (e.g., "Cybersec article required 3rd self-review pass; Discussion close drafted Day 1 PM but final attribution-tone polish slipped to Buffer-1 AM")

  If any out-of-tree task (LinkedIn, Cybersec article merge, profile merge, Discussion close) is deferred PAST 2026-06-11 hard ceiling, file a follow-up Issue per F-292 precedent (PR #293 close-out commit `a90146e` deferred T017+T026 to Issue #295) and update the F-1 close-out comment accordingly.
- [ ] T036 [P] PM plan-layer LOW concern #2 (FR-009 follow-up Issue template): create a draft template at `specs/296-50-50-owasp-coverage-distribution-launch/notes/material-critique-followup-issue-template.md` containing the title pattern (e.g., "F-1 distribution: material critique on [surface] — gap analysis"), body structure (link to critique + gap description + verification of critique against `docs/standards/OWASP_COVERAGE.md` + remediation plan or in-public correction reference per FR-009 + NFR-003), and labels (`signal:material-critique`, `f-296-followup`). Template is preemptive; only filed if FR-009 trigger fires (named gap OR verifiable counter-example OR ≥5 confirming independent reactions/replies).
- [ ] T037 [MANUAL-ONLY] If F-2 (F-260b @north-echo asset-tag wiring) slips past 2026-06-11 hard ceiling (FR-007 + Architect M2 + US6 AC-4), edit the Issue #296 closing comment (post-close edit allowed) to state the new release-cadence-restoration date. Update memory carve-out (T028 output) with the new restoration date as well.

**Checkpoint**: F-1 closed. All 5 artifact URLs in Issue #296 closing comment; SC-007 binary clean; SC-010 file-allowlist verified; SC-014 strategy doc verified; memory carve-out documented; PR #297 squash-merged with `docs(296):` prefix; release-please skipped as EXPECTED; F-2 cadence-restoration runway visible (target 2026-06-11).

---

## Dependencies & Ordering

```
Phase 1 Setup (T001-T004) → Phase 2 Wave 0 (T005-T007) → Phase 3 Wave 1 (T008-T012)
                                                              ↓
                                                       Phase 11 Wave 5
                                                       (T026 CHANGELOG,
                                                        T029 in-tree merge gate)
                                                              ↓
                            ┌─────────────────────────────────┼──────────────────────┐
                            ↓                                 ↓                      ↓
                  Phase 4 US3 Cybersec article    Phase 6 US4 GitHub profile   Phase 7 US5 Discussion close
                  (T013-T016)                     (T020-T021)                  (T022 draft Day 1 PM,
                                                                                T023 publish Day 5 AM,
                                                                                T024 close)
                            ↓
                  Phase 5 US2 LinkedIn (T017-T019)
                  [BLOCKED by T016 article merge per Q2 lean]
                            ↓
                  Phase 11 close-out (T027-T037)
                  [T027 BLP-04 strategy doc + T028 memory carve-out + T031 SC-007 + T032 SC-010 +
                   T033 SC-014 + T034 Issue #296 close + T035-T037 PM-LOW + Architect M2 follow-up]
```

**Sequencing constraints**:
- US6 sequencing hold runs throughout the F-1 window (T025 + T031 verification).
- US3 Cybersec article merge gates US2 LinkedIn publish (Q2 lean = (c)).
- Wave 0 + Wave 1 + Wave 5 in-tree work MUST complete before T029 in-tree squash-merge.
- T030 post-merge `/security` regression scan runs after T029.
- T034 Issue #296 close runs after all 5 artifact URLs captured (T012 README rendered + T018 LinkedIn URL + T016 article URL + T021 profile URL + T024 discussion close URL).
- T028 memory carve-out + T027 BLP-04 strategy doc MUST exist before T034 Issue #296 close (referenced from closing comment).

## Parallel Execution Opportunities

- Phase 1 Setup: T002 + T003 + T004 all parallel after T001.
- Phase 2 Wave 0: T006 + T007 parallel after T005.
- Phase 3 Wave 1: T009 + T010 + T012 parallel after T008; T011 parallel with T008.
- Phase 4-6: Wave 2 (T013-T016) + Wave 3 (T020-T021) + Wave 4 draft (T022) can begin in parallel after Wave 1 completes. Wave 5 LinkedIn (T017-T019) MUST wait for T016 article merge.
- Phase 11 Polish: T026 + T027 + T028 parallel; T030 + T031 + T032 + T033 parallel after T029 in-tree merge; T035 + T036 parallel anytime after planning.

## Implementation Strategy (MVP-incremental)

**MVP-1 (P1, in-tree only)**: T001 → T008 → T029 (README hero + Wave 0 anchor + CHANGELOG + in-tree merge). This alone delivers US1 — the README hero with 50/50 framing — without out-of-tree work. Provides immediate adopter-facing value if out-of-tree distribution slips.

**MVP-2 (P1 add)**: MVP-1 + T013-T016 (Cybersec article) + T017-T019 (LinkedIn) — delivers US3 + US2; the in-tree work backstops the article + post.

**MVP-3 (P2 add)**: MVP-2 + T020-T021 (profile) + T022-T024 (Discussion close).

**Full delivery (P3 add)**: MVP-3 + Phase 11 close-out (BLP-04 strategy doc T027 + memory carve-out T028 + Issue #296 close T034 + SC verifications T031-T033).

**Scope-reduction order if NFR-007 (2026-06-11 hard ceiling) approaches**:
1. Drop Discussion #179 close to follow-up Issue (PRD R3 mitigation).
2. Drop profile refresh to follow-up Issue.
3. Drop LinkedIn post (lowest reach surface per 2026 algorithm research).
4. NEVER drop README hero, OWASP_COVERAGE.md, or Cybersec article — these are the anchor surfaces.
