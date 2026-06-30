# NEXT-SESSION — Feature #338 (deliver-ready handoff)

**State**: `/aod.build` implementation COMPLETE + all build gates passed. **T009/T010 (deliver-stage) remain → run `/aod.deliver 338`.**
**Branch**: `338-restore-substitution-hardening` (NOT pushed — S-1 gate honored)
**Date**: 2026-06-30

## What landed (committed, local only)
| Commit | What |
|--------|------|
| `99507b2` | (pre-existing) FR-006 push gate + FR-007 xfail groundwork |
| `ff5da60` | checkpoint: plan artifacts |
| `18a39ed` | **the restore** — 3 scripts (byte-identical to `5b64f68`) + 5 `defaults.env` canonical-5 keys |
| `0ccd9a8` | security scan (PASSED, 0 findings) |
| `f0ec901` | build gates: tasks T001-T008 done, results.json/summary.json, economy-check.md |

## Verification done (all green)
- **T006** F-248/F-256 CI-gated 15-module suite **GREEN** on macOS bash 3.2.57 leg — 143 pass / 0 fail / 1 skip / 1 xfail (FR-007 baseline). Canary `AT&T→AT&T` ✓, malicious-pack rejected (no `/tmp/F-256-pwned`) ✓, missing-key rejected ✓, clone-timeout ✓.
- **T007** 3 script bodies byte-identical to `5b64f68` (empty diff).
- **T008** restore commit `18a39ed` = exactly 8 in-scope paths; all other branch deltas FR-008-named (#336 `scaffold/package.json`, FR-006/007 groundwork, plan artifacts); `update.sh`/manifest untouched.
- Final validation APPROVED · Design skipped (no UI) · **Security PASSED** · Economy PASSED (pure reuse).

## NEXT ACTIONS — `/aod.deliver 338`
1. **T009 — deliver gate (S-1)**: push the branch + open/ready PR ONLY now that the suite is green locally (S-1 satisfied). Merge to `main` **through devops** (deployment policy) with a Conventional-Commit PR title: **`fix(338): restore F-248/F-256 substitution hardening`** (release-triggering). This is where the ubuntu bash 5.x CI leg runs (SC-001 both-legs) — confirm green on the PR before squash-merge.
2. **T010 — release verify**: after squash-merge + `git push origin main`, confirm a release-please PR opened within ~30s (`gh pr list --state open --search "release-please" --limit 3`); if empty, push an empty `fix(338): … — release marker` commit (AOD deliver-release gate; see memory `feedback_aod_deliver_release_gate`).

## Gotcha to remember (KB-worthy)
The F-248/F-256 test harness (`init_sh_helpers.py:_clone_for_init`) **clones committed HEAD**, not the working tree — so the gated suite only reflects the restore AFTER it is committed. The first post-restore run showed 3 "failures" purely because the restore was still uncommitted; committing fixed all 3. (Also: the earlier "22 failures" in a full `tests/scripts/` run were 19 pre-existing out-of-gate failures unrelated to substitution + the 3 uncommitted-restore artifacts.)
