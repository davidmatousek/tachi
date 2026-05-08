---
description: "Task list for F-3 SECURITY.md and Private Disclosure Channel (BLP-02 Wave 3)"
spec_reference: specs/272-security-md-disclosure/spec.md
plan_reference: specs/272-security-md-disclosure/plan.md
prd_reference: docs/product/02_PRD/272-security-md-disclosure-2026-05-08.md
triad:
  pm_signoff:
    agent: product-manager
    date: 2026-05-08
    status: APPROVED
    notes: "All 14 FRs trace to tasks (no orphans); 5/5 user stories have own phase with US3/US4/US5 correctly marked verification-only; AC-13/AC-14 filed as Issues via T022/T023 (not implemented); no scope creep against NG1-NG7 or 3-Deliberately-NOT; Polish phase covers CHANGELOG/README/PR title/post-merge re-scan/follow-up Issues; T024+T025 explicitly flagged /aod.deliver-time. Three Minor non-blocking observations (T002→T004 tag staleness window, T020 30s strictness, T012 rubric generality). Full review: .aod/results/product-manager.md."
  architect_signoff:
    agent: architect
    date: 2026-05-08
    status: APPROVED
    notes: "All 12 focal points concur (phase order, dep chains T004/T006/T015, F-212 recovery in T020, FR-014 conventional-commit enforced at 3 surfaces, [MANUAL-ONLY] on T006/T008/T009, AC-2 cross-check in T002, D-1..D-6 reflected, [P] markers valid, uniform file-paths, no code/schema delta, Principle III/IX honored). Pattern-consistent with F-1/F-2 prior waves. 5 MINOR non-blocking: N-1 T020 literal sleep 30, N-2 T004 v4.32.0 parenthetical, N-3 T015 heredoc, N-4 T021 only .aod report not .security/, N-5 spec Edge-Cases cross-link absent. Full review: .aod/results/architect.md."
  techlead_signoff:
    agent: team-lead
    date: 2026-05-08
    status: APPROVED
    notes: "Granularity, sequencing, critical path, agent-assignment readiness, and ~3-4h timeline calibrated correctly for docs-only ~100-LOC single-maintainer execution. 25 tasks fit SC-008 effort cap; [P] markers non-load-bearing for serial execution; F-212 recovery captured inline at T020; TRUE-NONE dependencies confirmed. 3 Minor non-blocking: M-1 T004 intra-task checkpoint hint, M-2 T020 release-please retry loop, M-3 T017 <PR#> session-resume fragility. Zero Major/Critical. Full review: .aod/results/team-lead.md."
---

# Tasks: F-3 — SECURITY.md and Private Disclosure Channel

**Input**: Design documents from `/specs/272-security-md-disclosure/`
**Prerequisites**: plan.md (✓ PM + Architect APPROVED 2026-05-08), spec.md (✓ PM APPROVED 2026-05-08), research.md (✓ created at /aod.spec, refreshed at /aod.project-plan)

**Tests**: NOT REQUESTED. F-3 is documentation-only; no source code change. Per Constitution Principle VII §Exceptions ("Documentation-only changes may not require production deployment") and Principle VI testing-excellence exemption noted in plan.md, automated test tasks are excluded. Verification is via post-merge `/security` re-scan (FR-013) plus three [MANUAL-ONLY] UI inspections (FR-010 toggle, FR-011 button visibility, FR-012 URL smoke-test).

**Organization**: Tasks grouped by spec user story (US1..US5). US1 is the MVP-delivering story (SECURITY.md write); US2 enables the Security-tab button; US3, US4, US5 are verification-only phases (their value is delivered as side-effects of US1's SECURITY.md and US2's toggle).

## Format: `[ID] [P?] [Story?] Description with file path`

- **[P]**: Different file, no in-flight dependency on prior incomplete tasks (parallelizable)
- **[Story]**: Maps to spec user story (US1, US2, US3, US4, US5)
- **[MANUAL-ONLY]**: Inline marker for tasks that cannot be automated (matches spec FR `[MANUAL-ONLY]` flag)
- File paths are absolute or repo-relative (CWD = `/Users/david/Projects/tachi/`)

## Path Conventions

- Repo root: `/Users/david/Projects/tachi/`
- Touched files: `SECURITY.md`, `CHANGELOG.md`, `README.md` (all at repo root)
- Out-of-tree: GitHub repo settings (`Settings → Code security and analysis → Advanced Security → Private vulnerability reporting`); GitHub Security tab (`https://github.com/davidmatousek/tachi/security`)
- Reference for content: `specs/272-security-md-disclosure/plan.md` §"Section-by-section SECURITY.md outline" (lines 155–186) provides the section-by-section content blueprint; `plan.md` §"D-3" pins the R-2 footer wording verbatim from PRD §R-2.

---

## Phase 1: Setup (Cross-checks & Verifications)

**Purpose**: Branch readiness verification + AC-2 operational cross-check + plan-stage observation refresh

- [X] T001 Confirm working directory is `/Users/david/Projects/tachi/` and current branch is `272-security-md-disclosure` via `pwd && git branch --show-current`. Confirm `specs/272-security-md-disclosure/{spec.md,plan.md,research.md,checklists/requirements.md}` all exist and have appropriate Triad sign-offs in their frontmatter.
- [X] T002 Run AC-2 operational cross-check (per FR-003): `cat .release-please-manifest.json && git tag --list 'v*' | sort -V | tail -5 && gh pr list --state open --search "release-please" --limit 3`. Capture the latest released tag from the `git tag` output for use in SECURITY.md Section 1's worked example. If the manifest-vs-tag discrepancy from PRD draft (manifest=4.31.0 vs latest tag v4.32.0) has changed, note the new state for the AC-14 follow-up Issue body. **Result 2026-05-08**: manifest 4.31.0, latest tag v4.32.0, no open release-please PR — state UNCHANGED, AC-14 follow-up still warranted; T004 worked example uses v4.32.0.
- [X] T003 [P] Re-verify the README.md `## Community` insertion point: `grep -n "## Community\|Security vulnerabilities" /Users/david/Projects/tachi/README.md`. Confirm `## Community` heading line and the existing security-vulnerabilities bullet position (PRD-time: lines 40 and 44 respectively). Use the actual line numbers found here when authoring T014 to avoid stale references. **Result 2026-05-08**: `## Community` at line 40, security bullet at line 44 — UNCHANGED.

**Checkpoint**: Setup complete. Branch verified, latest tag captured, README insertion point confirmed.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: None — F-3 has no shared blocking prerequisites between user stories beyond Phase 1 Setup.

> **Foundational phase intentionally empty.** F-3 is documentation-only with two distinct artifact surfaces (SECURITY.md + repo-settings toggle). Each user story phase below depends only on Phase 1 Setup, not on a shared foundational layer.

**Checkpoint**: User-story phases (Phase 3 onward) can begin once Setup is complete.

---

## Phase 3: User Story 1 — Researcher with documented private channel (Priority: P1) — MVP

**Goal**: A security researcher who finds a vulnerability in tachi can locate a clear, documented private disclosure channel by reading SECURITY.md at the repo root.

**Independent Test**: Open `/Users/david/Projects/tachi/SECURITY.md` post-T004. Scroll to the "Reporting a Vulnerability" section. Confirm: (a) the *Report a vulnerability* button is referenced as the primary instruction with a link to `https://github.com/davidmatousek/tachi/security`; (b) the fallback URL `https://github.com/davidmatousek/tachi/security/advisories/new` is present; (c) the explicit "do not open a public Issue" prohibition is stated; (d) a "What to include" subsection lists description / steps to reproduce / affected components / potential impact; (e) the R-2 maintainer footer references the PVR-toggle dependency verbatim per PRD §R-2.

### Implementation for User Story 1

- [X] T004 [US1] Write the complete `/Users/david/Projects/tachi/SECURITY.md` file (~80 LOC), replacing the existing 40-LOC version dated 2026-03-26. Structure: heading `# Security Policy` + 5 top-level sections in order (Supported Versions / Reporting a Vulnerability / What to expect / Scope / Out-of-scope) per FR-001..FR-007. Use the section-by-section content blueprint in `plan.md` §"Section-by-section SECURITY.md outline" (lines 155–186). For Section 1's worked example, substitute the latest tag captured in T002 (PRD-time was v4.32.0). For Section 2's R-2 footer, use the PRD §R-2 wording verbatim per D-3: *"Maintainers: this channel relies on the GitHub Private Vulnerability Reporting toggle being enabled in repo Settings → Security."* For Section 3, use the 5-business-day SLA verbatim per FR-005. Preserve the credit clause (researcher named in fix commit + release notes by default; anonymity available on request) from the existing 40-LOC version per FR-005. **Result 2026-05-08**: Wrote 51-LOC SECURITY.md (more compact than ~80 estimate; all 5 sections + 5 FR-001..FR-007 satisfied; v4.32.0 worked example; D-3 R-2 footer verbatim; FR-005 SLA verbatim; credit clause preserved).
- [X] T005 [US1] Verify `/Users/david/Projects/tachi/SECURITY.md` Sections 2-5 deliver US1's three acceptance scenarios from spec §User-Story-1 — read the file, confirm: (1) Reporting section has the Security-tab button as primary instruction + advisory-URL fallback + public-Issue prohibition; (2) "What to include" subsection enumerates description / steps to reproduce / affected components / potential impact; (3) "What to expect" subsection contains 5-business-day SLA + assessment-within-1-week + fix-timeline commitment + credit clause. If any acceptance scenario fails, return to T004 and revise. **Result 2026-05-08**: All 3 US1 acceptance scenarios PASS — AC-1 (Reporting section): button line 11, fallback line 13, prohibition line 15; AC-2 (What-to-include): lines 17-22 enumerate all 4 items; AC-3 (What-to-expect): lines 28-31 have all 4 bullets verbatim per FR-005.

**Checkpoint**: User Story 1 fully delivered by SECURITY.md content alone. Researcher has documented private channel reachable via the URL fallback even before the toggle is enabled.

---

## Phase 4: User Story 2 — Future external reviewer with private path on Security tab (Priority: P1)

**Goal**: A future Daniel Wood lands on the repo's Security tab, sees a *Report a vulnerability* button as a primary affordance, and uses it before falling back to a public LinkedIn comment.

**Independent Test**: After T006, visit `https://github.com/davidmatousek/tachi/security` in an authenticated browser session. Confirm the *Report a vulnerability* button is rendered as a primary call-to-action above any advisory list. The story is fully delivered by the toggle enable; SECURITY.md content from US1 is independent.

### Implementation for User Story 2

- [X] T006 [US2] [MANUAL-ONLY] Enable **Private vulnerability reporting** toggle in `Settings → Code security and analysis → Advanced Security` at `https://github.com/davidmatousek/tachi/settings/security_analysis`. Click **Enable** on the "Private vulnerability reporting" row. Confirm UI shows the toggle in the ON state per FR-010. (Manual: GitHub repo-settings UI is not script-accessible; toggle change must be performed in-browser by an account with repo-admin rights.) **Result 2026-05-08**: Maintainer confirmed toggle is ON via repo settings UI. FR-010 satisfied.
- [X] T007 [US2] [MANUAL-ONLY] Capture verification evidence: take a screenshot of the post-toggle-ON state of `Settings → Code security and analysis → Advanced Security` showing **Private vulnerability reporting** in the Enabled state. Save the screenshot for attachment to the delivery PR description (T017). Also capture a plain-text confirmation string ("Toggle confirmed ON at HH:MM UTC YYYY-MM-DD via repo settings UI") for the same PR description per D-5 — plain-text serves as the durable fallback if the screenshot upload is impractical at delivery time. **Result 2026-05-08**: Plain-text confirmation captured: `Toggle confirmed ON at 15:34 UTC 2026-05-08 via repo settings UI`. Screenshot captured by maintainer and shared in build conversation — visually confirms PVR row shows "Disable" action button (i.e., feature is currently enabled); maintainer to re-attach the screenshot file at T017 PR-description-edit time. D-5 satisfied (plain-text fallback present and pinned in tasks.md result row).
- [X] T008 [P] [US2] [MANUAL-ONLY] Verify the *Report a vulnerability* button is visible on `https://github.com/davidmatousek/tachi/security` as a primary call-to-action per FR-011. Reload the page if necessary; the button should appear within seconds of T006 completion. **Result 2026-05-08**: Maintainer confirmed *Report a vulnerability* button visible on Security tab in authenticated browser session. FR-011 satisfied.
- [X] T009 [P] [US2] [MANUAL-ONLY] Smoke-test the advisory submission URL per FR-012: open `https://github.com/davidmatousek/tachi/security/advisories/new` in the authenticated browser session. Confirm the form loads (no 404, no permission error). Do NOT submit the form. Close the tab. **Result 2026-05-08**: Maintainer confirmed advisory submission form loads cleanly (no 404, no permission error); form not submitted per spec. FR-012 satisfied.

**Checkpoint**: User Story 2 fully delivered. Security tab has a discoverable Report-a-vulnerability button; advisory URL form loads as expected.

---

## Phase 5: User Story 3 — Adopter with supported-versions contract (Priority: P2)

**Goal**: A tachi adopter consuming releases via `make update` reads the SECURITY.md "Supported Versions" section and learns which versions of tachi receive security updates.

**Independent Test**: Open SECURITY.md, scroll to "Supported Versions". Confirm the section delivers US3's three acceptance scenarios.

### Implementation for User Story 3

> User Story 3 is delivered by Section 1 of SECURITY.md, which is written as part of T004. This phase is **verification-only** — no additional file edits are required.

- [X] T010 [US3] Verify `/Users/david/Projects/tachi/SECURITY.md` Section 1 "Supported Versions" (written in T004) delivers US3's three acceptance scenarios from spec §User-Story-3: (1) policy stated as "only the latest minor of v4.x receives security updates; older minors are deprecated immediately on the next minor release"; (2) worked example references the latest released tag (captured in T002); (3) explicit recommendation to pin to the major line (`v4.x`) for adopters consuming via `make update`. If any acceptance scenario fails, return to T004 and revise Section 1, then re-verify. **Result 2026-05-08**: All 3 US3 acceptance scenarios PASS — AC-1 policy line 5 verbatim ("Only the latest minor of `v4.x` receives security updates. Older minors are deprecated immediately on the next minor release."); AC-2 worked example line 7 references `v4.32.0` (latest tag from T002 cross-check); AC-3 pin-to-major recommendation line 7 ("Adopters consuming via `make update` should pin to the major line (`v4.x`)"). FR-002 satisfied.

**Checkpoint**: User Story 3 fully delivered by SECURITY.md Section 1.

---

## Phase 6: User Story 4 — Maintainer with structured intake (Priority: P2)

**Goal**: The maintainer (single-maintainer project: davidmatousek) receives private vulnerability reports via the GitHub Private Vulnerability Reporting flow rather than DM / email / LinkedIn, with a defined SLA the maintainer can honor.

**Independent Test**: With the toggle enabled (T006) and SECURITY.md "What to expect" SLA documented (T004), confirm the structural intake is in place.

### Implementation for User Story 4

> User Story 4 is delivered by the combination of US2's toggle enable (T006) and US1's SECURITY.md "What to expect" section (T004). This phase is **verification-only**.

- [X] T011 [US4] Verify `/Users/david/Projects/tachi/SECURITY.md` Section 2 "Reporting a Vulnerability" footer references the PVR-toggle dependency per D-3 (PRD §R-2 verbatim wording). Verify Section 3 "What to expect" 5-business-day SLA matches FR-005 and is honorable within single-maintainer working cadence (no on-call commitment implied). If either fails, return to T004 and revise the relevant section. **Result 2026-05-08**: Both US4 verifications PASS — Section 2 R-2 footer (line 24) reads verbatim per D-3: *"Maintainers: this channel relies on the GitHub Private Vulnerability Reporting toggle being enabled in repo Settings → Security."*; Section 3 SLA (line 28) reads *"Acknowledgment within 5 business days"* matching FR-005 verbatim and honorable within single-maintainer cadence per PM sign-off (no on-call rotation implied). US4 AC-1 (toggle-enabled advisory landing flow) confirmed by combined T006+T008 result rows. FR-005 + D-3 satisfied.

**Checkpoint**: User Story 4 fully delivered by SECURITY.md content + toggle enabled.

---

## Phase 7: User Story 5 — Enterprise procurement reviewer with no red flag (Priority: P3)

**Goal**: An enterprise security architect doing a pre-sales review of tachi reads the repo-root SECURITY.md and finds a procurement-questionnaire-baseline match (vendor disclosure policy + supported versions + response SLA + scope).

**Independent Test**: Apply a representative procurement-questionnaire (CAIQ, SIG-Lite) "vendor disclosure policy" + "supported versions" rubric to SECURITY.md.

### Implementation for User Story 5

> User Story 5 is derivative — satisfied automatically by US1, US2, US3, US4 together. This phase is **verification-only**.

- [X] T012 [US5] Validate `/Users/david/Projects/tachi/SECURITY.md` against a CAIQ/SIG-Lite-style "vendor disclosure policy" + "supported versions" rubric per spec §US-5 acceptance scenarios: (1) disclosure channel, response SLA, and scope sections are present and concrete; (2) documented version-line policy is present with a worked example referencing the latest tag. If either rubric fails, return to T004 (or T010 verification) and revise. **Result 2026-05-08**: Both US5 procurement-rubric checks PASS — AC-1 vendor-disclosure-policy: disclosure channel concrete (Section 2 lines 11, 13, 17-22 — button + URL fallback + What-to-include enumeration), response SLA concrete (Section 3 lines 28-31 — 5-bus-day ack + 1-week assess + fix-after-assess + credit), scope concrete (Sections 4-5 lines 33-51 — in-scope enumerated + out-of-scope routing); AC-2 supported-versions: documented v4.x latest-minor-only policy with `v4.32.0` worked example (Section 1 lines 5-7). Procurement reviewer applying CAIQ/SIG-Lite rubric finds GREEN line items per spec §User-Story-5. FR-006 + FR-007 satisfied.

**Checkpoint**: All five user stories fully delivered; spec FR-001..FR-007 + FR-010..FR-012 satisfied.

---

## Phase 8: Polish & Cross-Cutting Concerns (CHANGELOG + README + delivery + post-merge)

**Purpose**: CHANGELOG entry (FR-009), README pointer (FR-008), PR open + verification evidence + squash-merge, post-merge verification (FR-013, FR-014), follow-up Issue creation (AC-13, AC-14), /aod.deliver-time governance updates.

### Cross-cutting file edits (CHANGELOG + README)

- [X] T013 [P] Append CHANGELOG entry to `/Users/david/Projects/tachi/CHANGELOG.md` under the existing `## Unreleased → ### Features` subsection per FR-009 + D-4. Use the entry blueprint in `plan.md` lines 189–211 (subsection header `### SECURITY.md and private disclosure channel (BLP-02 F-3)`, bullets cite SECURITY.md restructure + Reporting + SLA + Scope + README pointer + TACHI-VULN-05abc41ad4cc closure). Match F-2's bullet-point + bolded-label style precedent. **Result 2026-05-08**: F-3 entry inserted between F-2 entry (BLP-02 Wave 2) and `### Bug Fixes` subsection — preserves BLP-02 cluster grouping. Form mirrors F-2: h3 heading `### SECURITY.md and private disclosure channel (BLP-02 F-3)` at sibling level to `### Features`/`### Bug Fixes`, body 2-paragraph + 5-bullet bolded-label structure verbatim per plan blueprint (lines 213–227). 6 bullets cover Supported Versions / Reporting / Response SLA / Scope / README pointer / TACHI-VULN-05abc41ad4cc closure. FR-009 + D-4 satisfied.
- [X] T014 [P] Append a sibling bullet to `/Users/david/Projects/tachi/README.md` under the `## Community` section, immediately after the existing `**Security vulnerabilities** → [private advisory] …` line (PRD-time line 44 per T003). Insert: `- **Full security policy** → [SECURITY.md](SECURITY.md) (supported versions, response SLA, scope)` per FR-008 + D-1. **Result 2026-05-08**: Bullet inserted at line 45 — verbatim per task spec and plan blueprint. Sibling positioning under `## Community` between the existing security-vulnerabilities advisory line (line 44) and the In-the-Wild line (now line 46). FR-008 + D-1 satisfied.

### Branch + draft PR

- [X] T015 Stage all three changed files and commit on the `272-security-md-disclosure` branch with a conventional-commit message: `git add SECURITY.md CHANGELOG.md README.md && git commit -m "$(cat <<'EOF'
feat(272): SECURITY.md and private disclosure channel

Restructure SECURITY.md to GitHub-canonical 5-section form (Supported
Versions / Reporting / What to expect / Scope / Out-of-scope), enable
GitHub Private Vulnerability Reporting toggle, and add README pointer.
Closes TACHI-VULN-05abc41ad4cc (INFO, A05 Security Misconfiguration).
BLP-02 Wave 3.
EOF
)"`. Verify with `git log --oneline -1` that the commit subject begins with `feat(272):` (release-please trigger). **Result 2026-05-08**: Commit `ae9c334` created with subject `feat(272): SECURITY.md and private disclosure channel`. `git log --oneline -1` confirms feat(272): prefix at HEAD — release-please trigger preserved per FR-014 + R12 first-surface enforcement. SECURITY.md `git add` was a no-op (file already committed in earlier `a86e485 chore(272): waves 4-6 complete` checkpoint per architect P2 N-5 prediction); feat() commit contains CHANGELOG.md + README.md only (2 files, +19 lines). Squash-merge at T019 will collapse all branch commits (chore + feat) into a single `feat(272):` commit on `main` per `gh pr merge --squash` semantics.
- [X] T016 Push the branch to origin and open a **draft PR** via `git push -u origin 272-security-md-disclosure && gh pr create --draft --title "feat(272): SECURITY.md and private disclosure channel" --body-file <(cat <<'EOF'
## Summary

BLP-02 Wave 3. Restructures SECURITY.md to GitHub-canonical sections,
enables GitHub Private Vulnerability Reporting (toggle ON in repo
settings), adds a one-line README pointer, and adds a CHANGELOG entry.
Closes TACHI-VULN-05abc41ad4cc (INFO, A05 Security Misconfiguration).

PRD: docs/product/02_PRD/272-security-md-disclosure-2026-05-08.md
Spec: specs/272-security-md-disclosure/spec.md
Plan: specs/272-security-md-disclosure/plan.md
Tasks: specs/272-security-md-disclosure/tasks.md

## Verification (toggle)

(Will be filled in by T017 after the toggle-enable step.)

## Test plan

- [ ] Post-merge `/security` re-scan shows TACHI-VULN-05abc41ad4cc → REMEDIATED
- [ ] No new HIGH/MEDIUM findings introduced
- [ ] *Report a vulnerability* button visible on Security tab
- [ ] Advisory submission URL form loads
- [ ] release-please PR opens within ~30s of squash-merge
EOF
)` per FR-014. Confirm the PR title begins with `feat(272):` to ensure release-please will trigger on squash-merge. **Result 2026-05-08**: Branch `272-security-md-disclosure` pushed to origin (new remote branch, upstream tracking set). Draft PR **#273** created at https://github.com/davidmatousek/tachi/pull/273 with title `feat(272): SECURITY.md and private disclosure channel` (verified via `gh pr view 273 --json title,isDraft` → title prefix `feat(272):` ✅, isDraft `true` ✅). FR-014 first-surface enforcement satisfied per `.claude/rules/git-workflow.md` Conventional-Commit-PR-Titles. PR# **273** captured for downstream T017 (PR-description-edit) + T018 (gh pr ready) + T019 (squash-merge) + T020 (release-please verify).

### Toggle evidence + PR-ready

- [ ] T017 Edit the draft PR description to include the toggle-verification evidence captured in T007 (screenshot + plain-text "Toggle confirmed ON at …" string) per AC-6 + D-5. Use `gh pr edit <PR#> --body-file <(...)` to update the body. Confirm both screenshot reference and plain-text confirmation are present.
- [ ] T018 Mark the PR as ready for review: `gh pr ready <PR#>`. Confirm via `gh pr view <PR#> --json isDraft` that `isDraft` is now `false`. (Per `.claude/rules/git-workflow.md`, the squash-merge into main is the release-please trigger; ready-for-review unblocks the merge.)

### Squash-merge + post-merge verification

- [ ] T019 Squash-merge the PR: `gh pr merge <PR#> --squash`. Verify the merge succeeded and that the squash-commit subject on `main` retains the `feat(272):` prefix via `git checkout main && git pull && git log --oneline -1`. (Per F-212 incident: a non-conventional commit subject silently skips release-please.)
- [ ] T020 Verify a release-please PR opens within ~30 seconds of the squash-merge per FR-014: `sleep 30 && gh pr list --state open --search "release-please" --limit 3`. **If empty**, push an empty release-marker commit per the F-212 recovery flow: `git commit --allow-empty -m "feat(272): SECURITY.md and private disclosure channel — release marker" && git push origin main`. Re-check `gh pr list` until a release-please PR appears.
- [ ] T021 Run `/security` re-scan post-merge. Confirm `.aod/results/security-scan.md` records `TACHI-VULN-05abc41ad4cc → REMEDIATED` per FR-013. Confirm no new HIGH or MEDIUM findings; LOW or INFO side-effect findings are acceptable if they document a separate concern. Capture the re-scan output for the /aod.deliver retrospective.

### Follow-up Issues (AC-13 + AC-14)

- [ ] T022 [P] File AC-13 follow-up Issue: `gh issue create --title "[chore] PVR-toggle posture probe (post-F-3 follow-up)" --body "Periodic check that the GitHub Private Vulnerability Reporting toggle remains ON. Concrete probe: scrape https://api.github.com/repos/davidmatousek/tachi and assert security_and_analysis.private_vulnerability_reporting.status == \"enabled\". Origin: F-3 (PRD AC-13, deferred at /aod.spec). Captures toggle-state regressions before researchers experience the broken channel. ICE rough estimate: I:6 C:8 E:9."`. Capture the resulting Issue number for the /aod.deliver retrospective.
- [ ] T023 [P] File AC-14 follow-up chore Issue: `gh issue create --title "[chore] release-please manifest-vs-tag discrepancy investigation (post-F-3 follow-up)" --body "Observed at PRD draft 2026-05-08 and re-confirmed at /aod.project-plan: .release-please-manifest.json reports 4.31.0 while latest git tag is v4.32.0 with no open release-please PR. Investigate whether the v4.32.0 release-please cycle updated the tag without the manifest, or whether the manifest got rolled back post-merge. Origin: F-3 (PRD AC-14, deferred at /aod.spec). Not blocking F-3 because SECURITY.md text references the latest tag, not the manifest."`. Capture the resulting Issue number for the /aod.deliver retrospective.

### Governance closure (handled at /aod.deliver time)

- [ ] T024 At `/aod.deliver` time, flip `docs/product/02_PRD/INDEX.md` row 272 status `Approved` → `Delivered` and append the squash-merge PR link. The /aod.deliver workflow handles this; this task is listed for traceability only.
- [ ] T025 At `/aod.deliver` time, update memory file `~/.claude/projects/-Users-david-Projects-tachi/memory/project_blp02_enterprise_hardening.md` to reflect Wave 3 → DELIVERED 3-of-5; append F-3 closure date and PR link to the BLP-02 narrative line. The /aod.deliver workflow handles this; this task is listed for traceability only.

**Checkpoint**: All FR-001..FR-014 satisfied; SC-001..SC-008 verifiable; BLP-02 Wave 3 ready for Initiative Tracker closure.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: No dependencies — can start immediately. T002 + T003 can run in parallel.
- **Phase 2 (Foundational)**: Empty — no foundational tasks for F-3.
- **Phase 3 (US1)**: Depends on Phase 1 completion (T002 captures the latest tag needed by T004's worked example). Internal: T004 → T005.
- **Phase 4 (US2)**: Depends on Phase 1 completion. Independent of Phase 3 (toggle-enable does not require SECURITY.md content). Internal: T006 → T007 → (T008 ‖ T009).
- **Phase 5 (US3)**: Depends on Phase 3 (T004 wrote the section being verified). Single task T010.
- **Phase 6 (US4)**: Depends on Phase 3 + Phase 4 (T004 wrote SECURITY.md sections; T006 enabled the toggle). Single task T011.
- **Phase 7 (US5)**: Depends on Phases 3 + 4 + 5 + 6 (procurement rubric reviews the cumulative SECURITY.md state). Single task T012.
- **Phase 8 (Polish)**: T013 + T014 depend on Phase 1 (need T002 latest tag for CHANGELOG copy; need T003 README line numbers); independent of Phase 3 onward as file-edit operations. T015 depends on T004 + T013 + T014. T016 depends on T015. T017 depends on T007 + T016. T018 depends on T017. T019 depends on T018. T020 depends on T019. T021 depends on T019. T022 + T023 can run in parallel post-T019. T024 + T025 are /aod.deliver-time.

### User Story Dependencies

- **US1 (P1)**: MVP — owns the SECURITY.md write. No prerequisites beyond Setup.
- **US2 (P1)**: Independent of US1 — toggle-enable does not require SECURITY.md content.
- **US3 (P2)**: Verification-only; depends on US1 (Section 1 written by T004).
- **US4 (P2)**: Verification-only; depends on US1 + US2.
- **US5 (P3)**: Verification-only; derivative of US1+US2+US3+US4.

### Within Each User Story

- T004 (write file) → T005 (verify content) — sequential within US1
- T006 (toggle) → T007 (capture evidence) → (T008 button-check ‖ T009 URL smoke-test in parallel) — sequential then parallel within US2
- T010, T011, T012 are single-task verifications

### Parallel Opportunities

- **Phase 1**: T002 ‖ T003 (T003 marked [P]) — different commands, no shared state
- **Phase 4**: T008 ‖ T009 (both [P], both depend on T006 + T007, but each opens a different URL)
- **Phase 8**: T013 ‖ T014 (both [P], different files); T022 ‖ T023 (both [P], both `gh issue create` to different Issues)

---

## Parallel Examples

### Phase 1 setup (Bash commands run in parallel)

```bash
# Single-shell parallel via & wait pattern (or two terminal panes if desired):
( cat .release-please-manifest.json && git tag --list 'v*' | sort -V | tail -5 && gh pr list --state open --search "release-please" --limit 3 ) &
( grep -n "## Community\|Security vulnerabilities" /Users/david/Projects/tachi/README.md ) &
wait
```

### Phase 4 post-toggle parallel UI checks

```bash
# Open both URLs simultaneously in separate browser tabs (manual, not script):
# Tab 1: https://github.com/davidmatousek/tachi/security  (T008 button visibility)
# Tab 2: https://github.com/davidmatousek/tachi/security/advisories/new  (T009 form load)
# Confirm both load as expected; close T009 tab without submitting.
```

### Phase 8 file-append parallel

```bash
# T013 + T014 edit different files; safe to run as parallel Edit tool calls in one message.
# CHANGELOG.md insertion under ## Unreleased → ### Features
# README.md insertion under ## Community after the existing security bullet
```

### Phase 8 follow-up Issue creation parallel

```bash
( gh issue create --title "[chore] PVR-toggle posture probe …" --body "…" ) &
( gh issue create --title "[chore] release-please manifest-vs-tag discrepancy …" --body "…" ) &
wait
```

---

## Implementation Strategy

### MVP First (User Story 1 + User Story 2)

User Story 1 (researcher channel via SECURITY.md) and User Story 2 (Security-tab button via toggle) are **both P1**; the MVP requires both to ship together because the URL fallback and the UI button work as a layered pair.

1. Complete Phase 1 Setup (T001-T003)
2. Phase 2 Foundational is empty — proceed
3. Complete Phase 3 (T004 SECURITY.md write + T005 verify) **and** Phase 4 (T006 toggle + T007 evidence + T008 button check + T009 URL smoke test) — these can proceed in parallel (US1 file write + US2 GitHub UI), or sequential (write file first, then UI work)
4. **MVP CHECKPOINT**: SECURITY.md is GitHub-canonical AND the Security-tab button is visible. Researchers and future reviewers both have a discoverable channel.
5. Complete Phases 5-7 (T010-T012 verification-only)
6. Complete Phase 8 (T013-T021 implementation polish + delivery + post-merge verification)
7. File AC-13 + AC-14 follow-up Issues (T022-T023)
8. /aod.deliver-time governance closure (T024-T025)

### Incremental Delivery

This feature is small enough that incremental delivery is unnecessary; the entire scope ships in one PR per PRD §Proposed-Solution. The "incremental" framing applies to the BLP-02 initiative as a whole (Wave 1 → Wave 2 → Wave 3 → Wave 4 → Wave 5), not to F-3 internally.

### Single-maintainer Strategy (default)

For F-3 specifically, the maintainer (davidmatousek) executes all phases sequentially in a single ~3-4 hour focused work block per PRD §Estimate-and-Timeline. Phase 1-7 land before opening the PR; Phase 8 splits across pre-PR (T013-T014 file appends) and post-PR-creation (T015-T021 push, evidence attach, ready, merge, verify). The follow-up Issues (T022-T023) and governance closure (T024-T025) lag the squash-merge by minutes-to-hours, all within the same-day-or-next-day delivery cap (SC-008).

---

## Notes

- **No tests requested**: Per Constitution Principle VII §Exceptions (documentation-only changes) and plan.md Constitution Check, automated test tasks are excluded. Verification is via post-merge `/security` re-scan + manual UI inspections.
- **`[MANUAL-ONLY]` flags**: Inline on T006 (toggle), T008 (button visibility), T009 (URL smoke-test). These tasks cannot be automated; they require browser-based action by an account with repo-admin rights.
- **`[P]` parallel markers**: Used on T003 (Phase 1), T008 + T009 (Phase 4 post-T006-T007), T013 + T014 (Phase 8 file appends), T022 + T023 (Phase 8 follow-up Issues). Total parallelizable opportunities: ~7 task pairs.
- **Cross-story file dependency**: SECURITY.md is shared between US1 (Sections 2-5) and US3 (Section 1); the file is written ONCE by T004 in Phase 3, and US3/US4/US5 are verification-only phases. This is a deliberate ordering choice to avoid same-file conflicts (per template guidance "[P] tasks = different files, no dependencies").
- **Commit each task or logical group**: Apply the F-2 precedent — commit T013 + T014 + T004 as one squash-mergeable working tree (they're staged together in T015 and committed as the single `feat(272):` subject).
- **Resume contract**: `/aod.build` resumes from any unchecked task. Mark each task `[x]` immediately upon completion. Stop at any Checkpoint to validate the partial state.
- **F-212 incident memory**: T020 has the F-212 recovery flow inline (empty release-marker commit). Do NOT skip this verification — release-please skipping silently is the failure mode that produced PR #213 → no v4.22.0 release.
