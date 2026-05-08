# NEXT-SESSION.md — F-3 SECURITY.md and Private Disclosure Channel

**Feature**: 272 (BLP-02 Wave 3)
**Branch**: `272-security-md-disclosure`
**Generated**: 2026-05-08 (Session 2 — Waves 4-6 executed; build wave 1-6 of 15 complete)
**Reason**: `/aod.build` 3-wave ceiling reached (orchestrated == false)

---

## Status — Waves 1-6 Complete (12/25 tasks, 48%)

### Wave 1 — Setup ✅ (Session 1)
- **T001** ✅ Branch + artifact verification — `/Users/david/Projects/tachi/`, branch `272-security-md-disclosure`, all 4 spec artifacts present with Triad sign-offs.
- **T002** ✅ AC-2 cross-check — manifest 4.31.0, latest tag **v4.32.0**, no open release-please PR. State UNCHANGED → AC-14 follow-up still warranted.
- **T003** ✅ README confirmed — `## Community` line 40, security bullet line 44 (UNCHANGED).

### Wave 2 — US1 implementation ✅ (Session 1)
- **T004** ✅ Wrote 51-LOC SECURITY.md (5 sections per FR-001..FR-007; v4.32.0 worked example; D-3 R-2 footer verbatim; FR-005 SLA verbatim; credit clause preserved).

### Wave 3 — US1 verification ✅ (Session 1)
- **T005** ✅ All 3 US1 acceptance scenarios PASS — AC-1 button + fallback + prohibition; AC-2 What-to-include enumeration; AC-3 What-to-expect SLA bullets.

### Wave 4 — US2 toggle + evidence ✅ (Session 2)
- **T006** ✅ `[MANUAL-ONLY]` Maintainer enabled PVR toggle in `Settings → Code security and analysis → Advanced Security`. UI confirms enabled state (action button reads "Disable").
- **T007** ✅ `[MANUAL-ONLY]` Plain-text confirmation captured: `Toggle confirmed ON at 15:34 UTC 2026-05-08 via repo settings UI`. Screenshot captured by maintainer; **see N-1 below for screenshot durability action item before Wave 7**.

### Wave 5 — US2 UI verifications ✅ (Session 2)
- **T008** ✅ `[MANUAL-ONLY]` Maintainer confirmed *Report a vulnerability* button visible on `https://github.com/davidmatousek/tachi/security`. FR-011 satisfied.
- **T009** ✅ `[MANUAL-ONLY]` Maintainer confirmed `https://github.com/davidmatousek/tachi/security/advisories/new` form loads cleanly (no 404, no permission error); form not submitted per spec. FR-012 satisfied.

### P1 Checkpoint (end of Wave 5) — APPROVED_WITH_CONCERNS ✅
Architect P1 review verdict (full report at `.aod/results/architect.md`): **APPROVED_WITH_CONCERNS** — 3 minor non-blocking concerns:
- **N-1** Screenshot durability before T017 — recommendation: maintainer save the PVR-toggle screenshot to a known local path (e.g., `~/Desktop/pvr-toggle-2026-05-08.png` or `specs/272-security-md-disclosure/evidence/`) **before Wave 8/T017** so the screenshot survives session archival.
- **N-2** D-6 sequence variance — capture as IK note at /aod.deliver time (no code action).
- **N-3** F-212 recovery flow not yet exercised — execute T020 deliberately at Wave 8; do not skip the verification.

Zero blocking issues. SECURITY.md content verbatim-equivalent to plan blueprint. All 10 P1-relevant FRs satisfied.

### Wave 6 — US3 + US4 + US5 verifications ✅ (Session 2)
- **T010** ✅ US3 — Section 1 "Supported Versions" delivers all 3 acceptance scenarios (latest-minor policy verbatim line 5; v4.32.0 worked example line 7; pin-to-major recommendation line 7).
- **T011** ✅ US4 — Section 2 R-2 footer (line 24) verbatim per D-3; Section 3 SLA (line 28) verbatim per FR-005; honorable within single-maintainer cadence.
- **T012** ✅ US5 — CAIQ/SIG-Lite procurement rubric: vendor disclosure policy GREEN (channel + SLA + scope all present and concrete); supported versions GREEN (documented policy + worked example).

---

## Next Actions — Resume at Wave 7

### Pre-Wave-7 housekeeping (architect concern N-1)

**Before T013 starts**: maintainer should save the PVR-toggle screenshot from the build conversation to a known local path so it survives session archival and is reachable by T017. Suggested path: `specs/272-security-md-disclosure/evidence/pvr-toggle-2026-05-08.png` (commit-included) or `~/Downloads/pvr-toggle-2026-05-08.png` (out-of-tree). The plain-text fallback is durable in tasks.md result row regardless.

### Wave 7 — File appends (T013-T014, both `[P]`)

Two parallel markdown appends:

- **T013**: Append CHANGELOG entry to `/Users/david/Projects/tachi/CHANGELOG.md` under existing `## Unreleased → ### Features` per FR-009 + D-4. Use entry blueprint in plan.md lines 189–211 (subsection header `### SECURITY.md and private disclosure channel (BLP-02 F-3)`).
- **T014**: Append README pointer to `/Users/david/Projects/tachi/README.md` under `## Community` after the existing `**Security vulnerabilities** → [private advisory] …` line (PRD-time line 44 per T003). Insert: `- **Full security policy** → [SECURITY.md](SECURITY.md) (supported versions, response SLA, scope)`.

### Wave 8 — Stage + commit (T015)

Stage 3 files (SECURITY.md + CHANGELOG.md + README.md) and commit on the `272-security-md-disclosure` branch with conventional-commit message `feat(272): SECURITY.md and private disclosure channel`. Verify via `git log --oneline -1` that subject begins with `feat(272):` (release-please trigger).

### Wave 9 — Push + draft PR (T016)

`git push -u origin 272-security-md-disclosure && gh pr create --draft --title "feat(272): SECURITY.md and private disclosure channel"` with body heredoc per FR-014. Capture the PR# for downstream tasks.

### Wave 10 — PR description w/ evidence (T017)

`gh pr edit <PR#> --body-file <(...)` to attach the toggle-verification evidence captured in T007 (screenshot file path + plain-text "Toggle confirmed ON at 15:34 UTC 2026-05-08 via repo settings UI" string) per AC-6 + D-5.

### Wave 11 — PR ready (T018)

`gh pr ready <PR#>` and verify via `gh pr view <PR#> --json isDraft` that `isDraft` is `false`.

### Wave 12 — Squash-merge (T019)

`gh pr merge <PR#> --squash`; verify squash-commit subject on `main` retains `feat(272):` prefix via `git checkout main && git pull && git log --oneline -1`. (F-212 incident memory: non-conventional commit subject silently skips release-please.)

### Wave 13 — release-please verify (T020) — N-3 deliberate-execution checkpoint

`sleep 30 && gh pr list --state open --search "release-please" --limit 3`. **If empty**, push empty release-marker commit per F-212 recovery flow: `git commit --allow-empty -m "feat(272): SECURITY.md and private disclosure channel — release marker" && git push origin main`. Re-check until release-please PR appears.

### Wave 14 — Post-merge re-scan (T021) — Gate C

`/security` re-scan post-merge. Confirm `.aod/results/security-scan.md` records `TACHI-VULN-05abc41ad4cc → REMEDIATED` per FR-013. Confirm zero new HIGH/MEDIUM findings.

### Wave 15 — Follow-up Issues (T022 ‖ T023)

Two parallel `gh issue create` calls — AC-13 follow-up (PVR-toggle posture probe) and AC-14 follow-up (release-please manifest-vs-tag discrepancy). Capture Issue numbers for /aod.deliver retrospective.

### Deferred to `/aod.deliver`

- **T024**: INDEX.md row 272 status flip Approved → Delivered.
- **T025**: BLP-02 memory file Wave 3 → DELIVERED 3-of-5 update.
- **N-2** (architect IK note): Capture D-6 sequence-variance lesson — "User-story-organized task phases naturally cluster in-tree + out-of-tree work for a single story before moving to cross-cutting concerns."

---

## Resume Prompt

Start a new conversation and run:

```
/aod.build 272
```

The command will detect Waves 1-6 complete (12 tasks marked `[X]` in tasks.md) and resume at Wave 7 (T013-T014 file appends).

**Quick resume**:

```bash
claude "Resume F-3 implementation (branch: 272-security-md-disclosure). Waves 1-6 complete (T001-T012); SECURITY.md verified against US1/US3/US4/US5; PVR toggle ON; button + URL smoke-test PASS; P1 checkpoint APPROVED_WITH_CONCERNS. Run /aod.build to continue with Wave 7 (T013 CHANGELOG + T014 README appends)."
```

---

## Prerequisites for Wave 7

- [ ] Pre-Wave-7: maintainer saves PVR-toggle screenshot to a known local path (architect concern N-1)
- [ ] No special prerequisites — Waves 7-15 are all in-tree-doc + git/gh CLI work; no further browser-UI manual steps until Wave 14 post-merge `/security` re-scan
- [ ] ~1.5-2h focused time available for Waves 7-15 (most rapid: T013+T014 file appends ~10 min, T015 commit ~5 min, T016 push+draft-PR ~5 min, T017-T019 PR-flow ~10 min, T020-T021 post-merge verification ~10 min, T022-T023 follow-up Issues ~10 min)

---

## Architect P1 Concern Summary (for next-session awareness)

| Concern | Severity | Action surface | Recommended action |
|---------|----------|----------------|---------------------|
| N-1 Screenshot durability | Minor | Pre-Wave-7 / T017 | Save screenshot file to known local path before T017 |
| N-2 D-6 sequence variance (benign) | Minor | /aod.deliver | Capture as IK note in delivery retrospective |
| N-3 F-212 recovery flow not yet exercised | Minor | Wave 13 / T020 | Execute T020 deliberately; do not skip even if release-please appears auto-functional |

All three are non-blocking and have correct fall-through actions in the existing tasks.md task descriptions.
