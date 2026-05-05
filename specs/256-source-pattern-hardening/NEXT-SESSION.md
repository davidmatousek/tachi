# Session Continuation: F-2 Source-Pattern Hardening (BLP-02 Wave 2)

**Generated**: 2026-05-05 13:58
**Branch**: `256-source-pattern-hardening`
**Last Commit**: `271f1ae` chore(256): wave 3 test artifacts + BACKLOG sync
**Draft PR**: [#257](https://github.com/davidmatousek/tachi/pull/257) — title `feat(256): harden source-pattern surface — bash source/eval → KV parser + clone timeout`

## Completed This Session

10 commits across Waves 1, 2, 3 + PM disposition + test artifacts:

```
271f1ae  chore(256): wave 3 test artifacts + BACKLOG sync
c9b2d36  docs(256): wave 3 final verification — Day-5 GREEN-LIGHT all 4 conditions
cd1ae4a  feat(256): wave 3 stream 3 ADR-040 Proposed (T042-T043)
cc18e84  fix(256): wave 3 site A — extend TECH_STACK to all 5 shipped packs (T019 follow-on)
f0d443b  feat(256): wave 3 stream 4 clone timeout + watchdog (T037-T041)
d106549  feat(256): wave 3 sites B+C+D refactor (T020-T036)
fbdd2ea  feat(256): wave 3 site A defaults.env refactor (T014-T019)
8280744  docs(256): PM Q-5 Option a disposition for NFR-004 >50% tier
ccd4579  feat(256): wave 2 stream 1 library bring-up (T009-T013)
a8eff4c  feat(256): wave 1 setup + foundational (T001-T008)
```

## Current State

- **Phase**: implement (Waves 1-3 of 6 active waves complete)
- **Uncommitted**: 0 files (clean — all pushed to origin/256-source-pattern-hardening)
- **Tasks**: 43/62 complete (T001-T043 marked `[X]`; T044-T062 pending)
- **Vuln_ids closed (engineering done; REMEDIATED events pending /aod.deliver)**: 5
  - TACHI-VULN-6f5a95085056 (HIGH) — Site A defaults.env
  - TACHI-VULN-bf5496e9fcdf (HIGH) — Site B aod-kit-version
  - TACHI-VULN-9a7512071b4a (MEDIUM) — Site C eval removal
  - TACHI-VULN-4dc6cf8f88ea (MEDIUM) — Site D TOCTOU collapse
  - TACHI-VULN-851fd6a21ba9 (LOW) — Stream 4 clone timeout

## Wave Status

| Wave | Tasks | Status | Notes |
|---|---|---|---|
| 1 — Setup + Foundational | T001-T008 | DONE | Library bring-up unblocked |
| 2 — Stream 1 Library Bring-Up | T009-T013 | DONE | 29/29 cases pass on `/bin/bash` 3.2.57 |
| **P0 Architect Checkpoint** | — | **APPROVED** (22/22) | Wave 3 GO |
| 3 — Sites A/B/C/D + Stream 4 + Stream 3 | T014-T043 | DONE | All 5 vuln_ids closed; ADR-040 Proposed |
| 4 — Day-5 Slip-Watch Checkpoint | T044 | **PENDING** | Gating decision; all 4 GREEN-LIGHT conditions met (per c9b2d36) |
| 5 — Stream 5 + Day-8 Checkpoint | T045-T048 | PENDING | Fixture regen + B-3 augmentation + Day-8 architect gate |
| 6 — Polish + Final | T049-T056 | PENDING | Full suite + NFR-002/005 verify + ADR-040 Accepted + CHANGELOG finalize |
| 7 — Post-Merge [MANUAL] | T057-T062 | PENDING (at `/aod.deliver`) | Closing operator |

## Day-5 Slip-Watch GREEN-LIGHT Conditions (already met, ready for T044)

| # | Condition | Status |
|---|---|---|
| 1 | ≥17/17 unit tests pass on macOS bash 3.2.57 | GREEN — 29/29 (T011) |
| 2 | Site A green on Linux | GREEN — 4/4 macOS pass; CI Linux deferred per T012 pattern |
| 3 | ADR-040 Proposed committed | GREEN — `cd1ae4a` |
| 4 | Clone timeout watchdog smoke-tests pass on macOS bash 3.2 | GREEN — 6/6 (T040) |

## Test Gate (Wave 3 post-wave regression)

- **Decision**: PASS (0 regressions)
- **Aggregate**: 767 passed, 16 failed, 1 skipped (385s)
- **15 pre-existing failures** on `main` (verified by re-running on main): unrelated to F-2 — threat modeling pipeline coverage attestation, line count caps, byte identity assertions on threat-modeling agents
- **1 expected drift**: `test_init_sh_substitution.py::test_personalized_tree_bytes_match_baseline` — F-2 legitimately modified 5 `stacks/*/defaults.env` (added TECH_STACK) + `.aod/scripts/bash/template-substitute.sh` (eval removal + escape pass removal). Baseline regen queued for T045 (Wave 5 fixture regen script) or T056 (Wave 6 final pre-merge).
- Artifacts: [`specs/256-source-pattern-hardening/test-results/wave-03/`](test-results/wave-03/)

## Outstanding Triad Decisions (queued, not blocking Wave 4)

1. **PM Q-5 Option a (NFR-004 >50% tier accept-and-document)**: APPROVED 2026-05-05 (recorded in [tasks-runlog.txt](tasks-runlog.txt)). Required ADR-040 §Consequences elaborations queued for T054 (Wave 6): methodology asymmetry, NFR-004 loosening with rationale, cost decomposition, awk micro-opt rejection.
2. **NUL-byte mechanism contract clarification**: original "regex implicitly rejects NUL" mechanism is unsound; library uses explicit Step 2b `wc -c` vs `tr -d '\000' | wc -c` size comparison. Fold into ADR-040 §Decision Item 1 at T054.

## Next Actions (Resume — Waves 4, 5, 6)

1. **Wave 4 (T044)** — Day-5 Slip-Watch Checkpoint. Single team-lead task: verify all 4 GREEN-LIGHT conditions (already met per status above) and record outcome in tasks-runlog.txt. Should be quick.
2. **Wave 5 (T045-T048)** — Stream 5 finalization + Day-8 architect checkpoint:
   - T045 [P]: author `tests/fixtures/regenerate-config-load-baseline.sh` + ALSO regenerate `test_init_sh_substitution.py` byte-identity baseline (the expected drift identified in Wave 3 regression check)
   - T046 [P]: run T045 → commit fixtures + new baseline
   - T047 [P]: B-3 cases 19-23 augmentation (if not already covered in T009 — verify)
   - T048: Day-8 secondary checkpoint (architect)
3. **Wave 6 (T049-T056)** — Final verification + polish:
   - T049: full pytest suite on macOS + Linux CI
   - T050-T052 [P]: NFR-002, NFR-005, SC-005 verifications
   - T053: CHANGELOG.md v4.x entry finalize (replace Wave 1 placeholder)
   - T054: ADR-040 Proposed → Accepted (fold T013 benchmark numbers + Q-5 Option a §Consequences elaborations + NUL-byte clarification per outstanding decisions above)
   - T055: SC-010 benchmark documentation completeness verify
   - T056: Final pre-merge verification

After Wave 6 → run `/aod.deliver 256` for Wave 7 closing-operator [MANUAL] tasks (T057-T062).

## Context Files (read on resume)

Required:
- [tasks.md](tasks.md) — full task list, T044-T062 pending
- [agent-assignments.md](agent-assignments.md) — Wave 4-7 task→agent mapping
- [plan.md](plan.md) — §Day-5 Slip-Watch + §Critical Path
- [tasks-runlog.txt](tasks-runlog.txt) — T005/T011/T012/T013 numbers + PM Q-5 disposition
- [.aod/results/wave-3-execution.md](../../.aod/results/wave-3-execution.md) — full Wave 3 detail
- [.aod/results/architect-p0-checkpoint.md](../../.aod/results/architect-p0-checkpoint.md) — P0 review

Conditional:
- [docs/architecture/02_ADRs/ADR-040-config-file-parsing-hardening.md](../../docs/architecture/02_ADRs/ADR-040-config-file-parsing-hardening.md) — Proposed; T054 promotes to Accepted with benchmark fold-in

## Resume Command

```bash
claude "Resume F-2 Source-Pattern Hardening implementation (branch: 256-source-pattern-hardening). Waves 1-3 complete; T001-T043 done (43/62). All 5 vuln_ids closed pending REMEDIATED events at /aod.deliver. P0 architect APPROVED 22/22. Day-5 GREEN-LIGHT all 4 conditions met. Run /aod.build 256 to continue with Wave 4 (T044 Day-5 slip-watch checkpoint), then Wave 5 (T045-T048 Stream 5 + Day-8 checkpoint), then Wave 6 (T049-T056 polish + final). Outstanding: regenerate test_init_sh_substitution.py byte-identity baseline at T045 (expected F-2 drift, not a regression)."
```
