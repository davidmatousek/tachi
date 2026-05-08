# NEXT-SESSION.md — F-3 SECURITY.md and Private Disclosure Channel

**Feature**: 272 (BLP-02 Wave 3)
**Branch**: `272-security-md-disclosure`
**Generated**: 2026-05-08
**Reason**: `/aod.build` 3-wave ceiling reached (orchestrated == false)

---

## Status — Waves 1-3 Complete (5/25 tasks)

### Wave 1 — Setup ✅
- **T001** ✅ CWD `/Users/david/Projects/tachi/`, branch `272-security-md-disclosure` verified; all 4 spec artifacts present with appropriate Triad sign-offs.
- **T002** ✅ AC-2 cross-check: manifest 4.31.0, latest tag **v4.32.0**, no open release-please PR. State UNCHANGED from PRD draft → AC-14 follow-up still warranted.
- **T003** ✅ README confirmed: `## Community` line 40, security bullet line 44 (UNCHANGED).

### Wave 2 — US1 implementation ✅
- **T004** ✅ Wrote 51-LOC SECURITY.md (compact relative to ~80 estimate; full FR-001..FR-007 satisfied). 5 sections in order: Supported Versions / Reporting a Vulnerability / What to expect / Scope / Out-of-scope. v4.32.0 worked example; D-3 R-2 footer verbatim per PRD §R-2; FR-005 SLA verbatim; credit clause preserved.

### Wave 3 — US1 verification ✅
- **T005** ✅ All 3 US1 acceptance scenarios PASS — AC-1 (Reporting section): button line 11, fallback line 13, prohibition line 15; AC-2 (What-to-include): lines 17-22 enumerate all 4 items; AC-3 (What-to-expect): lines 28-31 have all 4 bullets verbatim.

---

## Next Actions — Resume at Wave 4

### Wave 4 — US2 toggle + evidence (T006-T007) `[MANUAL-ONLY]`

**Maintainer action required** — these tasks cannot be automated. Open the GitHub repo settings UI in an authenticated browser session.

- **T006**: Visit `https://github.com/davidmatousek/tachi/settings/security_analysis` → click **Enable** on the **Private vulnerability reporting** row → confirm UI shows the toggle ON per FR-010.
- **T007**: Capture (a) screenshot of post-toggle-ON state, (b) plain-text confirmation string `"Toggle confirmed ON at HH:MM UTC 2026-05-08 via repo settings UI"` for the PR description per D-5.

### Wave 5 — US2 UI verifications (T008-T009) `[MANUAL-ONLY]`

- **T008**: Visit `https://github.com/davidmatousek/tachi/security` — confirm *Report a vulnerability* button is visible per FR-011.
- **T009**: Visit `https://github.com/davidmatousek/tachi/security/advisories/new` — confirm form loads (no 404, no permission error). Do NOT submit.

### Wave 6 — US3-US5 verifications (T010-T012)

Read-and-confirm reviews of the SECURITY.md just written. Quick (~10-15 min total).

### Wave 7 — File appends (T013-T014)

- **T013**: Append CHANGELOG entry to `## Unreleased → ### Features` per plan.md lines 189–211.
- **T014**: Append README sibling bullet under `## Community` after line 44: `- **Full security policy** → [SECURITY.md](SECURITY.md) (supported versions, response SLA, scope)`.

### Waves 8-15 — Commit, PR, merge, post-merge verification, follow-up Issues

- **T015**: Stage 3 files, commit with `feat(272): SECURITY.md and private disclosure channel` heredoc message.
- **T016**: Push branch, open draft PR via `gh pr create --draft --title "feat(272): …"`.
- **T017**: Edit PR description with T007 screenshot + plain-text confirmation evidence.
- **T018**: `gh pr ready <PR#>`.
- **T019**: `gh pr merge <PR#> --squash`; verify squash subject begins with `feat(272):`.
- **T020**: Verify release-please PR opens within ~30s; F-212 recovery flow inline if empty.
- **T021**: `/security` re-scan post-merge; confirm TACHI-VULN-05abc41ad4cc → REMEDIATED per FR-013.
- **T022-T023**: File AC-13 + AC-14 follow-up Issues.

### Deferred to `/aod.deliver`

- **T024**: INDEX.md row 272 status flip Approved → Delivered.
- **T025**: BLP-02 memory file Wave 3 → DELIVERED 3-of-5 update.

---

## Resume Prompt

Start a new conversation and run:

```
/aod.build 272
```

The command will detect Waves 1-3 complete (5 tasks marked `[X]` in tasks.md) and resume at Wave 4 (T006).

**Quick resume**:

```bash
claude "Resume F-3 implementation (branch: 272-security-md-disclosure). Waves 1-3 complete (T001-T005); SECURITY.md written and US1-verified. Run /aod.build to continue with Wave 4 (T006 PVR toggle enable)."
```

---

## Prerequisites for Wave 4

- [ ] Authenticated GitHub session in browser (account with repo-admin rights for `davidmatousek/tachi`)
- [ ] ~10-15 min for toggle-enable + evidence capture
- [ ] Screenshot tool ready (macOS Cmd+Shift+4 or equivalent)
