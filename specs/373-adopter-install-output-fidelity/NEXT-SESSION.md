# NEXT-SESSION: Feature 373, `/aod.deliver` (Session 3)

**Written**: 2026-10-10, at the end of Session 2. This replaces the Session 1 handoff.

- **Feature**: #373, adopter install + output fidelity fixes (K1–K3, K9–K15, #370 folded in).
- **Branch**: `373-adopter-install-output-fidelity`.
- **Draft PR**: #375, `fix(373): adopter install + output fidelity fixes`.
- **Build: complete.** Ledger **40 of 40** `[X]`; waves 1–5 done.
- **The final code tip is `c2212fb`.** The commits after it are records only.
- **PR body**: refreshed with the pre-deliver security fixes and 10 follow-ups (T037, R-T1).

## Gate status

| Gate | Result | Record |
|---|---|---|
| T039 (W1 exit) | NO CARVE | `test-results/w1-exit-checkpoint.md` |
| P0 (W2) | APPROVED_WITH_CONCERNS; RC-1..RC-3 closed in W3 | `test-results/p0-architect-review.md` |
| TW-7 | not fired | `test-results/w2-exit-tw7.md` |
| W3 render session | K14 6/6 + fallback + exec-arch on one portrait PDF page; K15 7/7 pass on iteration 1; maintainer check PASS (2026-10-10); 2K kept | `test-results/k15-renders.md` |
| T035 oracle | 100% attributed; 0/0/0 at `729fa1b`, `eb5d3fe` and `c2212fb` | `oracle-diff.md` |
| T036 code review | 12/12 fixed + N-1; delta looks APPROVED_WITH_CONCERNS | `.aod/results/code-reviewer-373.md` (local) |
| P1 (W3) | APPROVED_WITH_CONCERNS, GO for W4 | `test-results/p1-architect-review.md` |
| P2 + Step 5 architecture | APPROVED_WITH_CONCERNS; E-1 applied (`6a1d6ff`) | `test-results/p2-architect-review.md` |
| Step 5 code review | APPROVED_WITH_CONCERNS; D-1..D-3 folded | `.aod/results/code-reviewer-373-final.md` (local) |
| Step 5 security review | APPROVED_WITH_CONCERNS; SEC-K3-07 fixed | `.aod/results/security-analyst-373-final.md` (local) |
| Step 6 design gate | Skipped (no UI files changed) | — |
| Step 7 security scan | **PASSED** at `c2212fb`; scan 1's HIGH (`tachi-VULN-217a46966920`, CWE-22) fixed | `security-scan.md`, `.security/` |
| Step 8 economy gate | 2 advisory findings, no carve-out shortened | `economy-check.md` |
| Tests | 1,478 passed / 0 failed / 6 skipped over 4 tested waves; 0 regressions | `test-results/summary.json` |

## Next actions (`/aod.deliver`), in order

0. **Pre-flight.**
   - CI must be green at the final tip, including both `tachi pytest` legs.
   - Check that the branch is current and that local `main` equals `origin/main`. Use a full-tree diff (KB 18).
   - Never use `git reset --hard`. Use `git checkout -B main origin/main`.
1. **Mark the PR ready** with `gh pr ready 375`.
   - The title is already `fix(373): …`. P2 ruled that it stays `fix`, so this is a patch release.
   - Squash-merge.
   - If release-please opens no PR, push an empty marker commit **`fix(373): … — release marker`**, not `feat`.
2. **Release notes** (quickstart §7):
   - Insert `release-notes-upgrading.md` into the release-please PR body's notes region, as the last action before merge.
   - After publish, run the `gh release edit` backstop.
   - Verify SC-6 with `gh release view`.
3. **Post the #364 handoff comment** from `issue-364-handoff.md`.
4. **File the follow-up issues.** Run `export AOD_REPO=davidmatousek/tachi` first. Use generic wording (NFR-6); the PM scopes each issue.
   1. `install.sh --version` leading-dash guard (SEC-K3-03).
   2. Extractors: accept the `## Section N: Title` heading form (P0 A-4).
   3. A stateless `baseline.source` is treated as a baseline (N7).
   4. The project-name parser misses em-dash H1 forms ("Unknown Project").
   5. maestro-stack template: dark text specified on its dark background (WCAG).
   6. The heat-map cell-level grid has no deterministic data source.
   7. Keep the Gemini key off `curl`'s argument list (CWE-214), together with the `.env` sourcing line's unquoted expansion.
   8. The Copilot, Cursor and generic adapters still send the rejected image request and name shut-down models (P2).
   9. `install.sh`: the project-path analog of D-1 (rated not a K3 bypass).
   10. `.security/scan-log.jsonl`: chain-hash break at entry 34 (F-338, 2026-06-30; pre-existing).

   Optional: one tidy-up issue for the 2 economy advisories and the code review's stale "EXPECTED RED" test notes.
5. **Release urgency** (P1 §7.1). On v4.48.0, adopters get no infographic images: every request is rejected, and the named models are shut down. Deliver promptly.

## Cleanup (the agent was permission-blocked; run it yourself)

- **Local lane branches and worktrees, all integrated:**
  - `373-w1-laneAp`, `373-w1-laneB1`, `373-w1-laneC1`;
  - `373-w2-A`, `373-w2-B2a`, `373-w2-B2b`, `373-w2-C2`, `373-w2-T`;
  - `373-w3-rc1`, `373-w3-sbe`, `373-w3-k3fix`, `373-w3-sbefix`, `373-w3-n1`, `373-w3-seck307`, `373-w3-vuln217`, `373-w3-d1`, `373-w3-d23`;
  - `373-w4-docs`.

  Run `git worktree prune` once the session scratchpad is gone (or `git worktree remove <path>`), then `git branch -D` on those names.
- **Three leftover files** from a CWE-22 test's pre-fix red run (fixed in D-3). They are safe to delete: `/var/folders/z8/4rm17hk17kxfz4_0cm4_qsq00000gn/T/pytest-of-david/escaped-ctf.mmd`, `escaped-ctf.png` and `escaped-ctf-attack-tree.png`.

## Facts the next session needs

- **Timeline.** Session 2 ran from 2026-10-06 to 2026-10-10. The render session was on 10-06; the maintainer's visual check came on 10-10.
- **Process note.** On a "resume" prod, run `ListAgents` before re-dispatching. In Session 2, a re-dispatch duplicated two live agents, and the duplicates had to be stopped.
- **Security-scan method.** Shell `grep` with a file list held in an unquoted zsh variable reads nothing, because zsh doesn't word-split it. Use Python, `xargs`, or `${=VAR}`. `security-scan.md` records the correction.

## Resume prompt

```
claude "Deliver Feature 373 (branch 373-adopter-install-output-fidelity, draft PR #375). /aod.build is complete (40/40; Step 7 PASSED at c2212fb). Run /aod.deliver; follow specs/373-adopter-install-output-fidelity/NEXT-SESSION.md."
```
