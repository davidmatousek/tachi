---
prd:
  number: 217
  topic: detect-images-duplicate-cleanup
  created: 2026-07-01
  status: Approved
  type: feature
triad:
  pm_signoff: {agent: product-manager, date: 2026-07-01, status: APPROVED, notes: "PM author — decision (c)+(a) per Issue #217 reporter recommendation; safe default preserved"}
  architect_signoff: {agent: architect, date: 2026-07-01, status: APPROVED_WITH_CONCERNS, notes: "All technical claims verified; OQ-2 resolved CLEAN (US-2 proceeds); deletion must land in BOTH code locations; AC-2a re-anchored to path-invariance; truncated-copy/cross-swap/mixed-pair tests added; defaulted-kwarg signature. Details: .aod/results/architect.md"}
  techlead_signoff: {agent: team-lead, date: 2026-07-01, status: APPROVED_WITH_CONCERNS, notes: "Estimate 0.5/1.0/2.0 eng-days independently confirmed; single wave; senior-backend-engineer authors code+tests (tester is BDD-focused); R-1 overstated — no test consumes the snapshot. Details: .aod/results/team-lead.md"}
source:
  idea_id: 217
  story_id: null
---

# Detect-Images Duplicate Cleanup — Opt-In Mislabeled-Image Removal - PRD (Quick Start)

**Status**: Approved (v1.1 — both reviewer correction sets folded)
**Created**: 2026-07-01
**Author**: product-manager
**Reviewers**: architect, team-lead
**Priority**: P2 (BLP-06 Wave 3 — maintenance/consolidation tail)
**Source**: [Issue #217](https://github.com/davidmatousek/tachi/issues/217) (follow-on to #215 / PR #216)

## Problem

Since #215/PR #216, `detect_images` in `scripts/extract-report-data.py` self-heals mislabeled infographic images — a `.jpg` whose bytes are PNG, the signature of the `gemini-2.5-flash-image` fallback era — by writing a corrected sibling via `shutil.copyfile` (deliberately non-destructive). The consequence tracked by Issue #217: **both the mislabeled original and the byte-identical corrected sibling persist forever**, roughly 2× image storage per affected stem (up to 6 stems per assessment directory) plus path ambiguity for humans and downstream references.

Verified bounds (PM code-read, 2026-07-01):
- **The population is frozen.** The producer (`tachi-threat-infographic` agent) is already fixed; only *legacy* assessment directories are affected. Bounded at one extra file per stem — not unbounded over re-runs.
- **This is not a correctness bug and does not spam warnings.** Selection prefers the correctly-labeled candidate; the mismatch warning fires only when *no* correctly-labeled candidate exists (i.e., exactly once, on the recovery run). Residual harm is storage + directory ambiguity only.
- **In-repo evidence**: `examples/agentic-app/test-output/2026-04-19T03-20-30/` holds all **6 stems** as mislabeled-`.jpg` + corrected-`.png` pairs. Note: that directory is a frozen test snapshot backing `security-report.pdf.baseline` (see R-1).

## Solution (Decision — Issue #217 acceptance: "decision documented")

Ship **option (c)**: an explicit opt-in `--cleanup-mislabeled-images` flag on `extract-report-data.py`, **plus option (a)'s documentation** — with the tested flag (not the issue's raw `find … rm` one-liner) as the sanctioned cleanup path. **Option (b) (`shutil.copyfile` → `shutil.move`) is rejected**: a silently destructive default could orphan external references (baseline trackers, manual indexes, archived links).

Deletion is **double-gated** — it happens only when (1) the flag is present AND (2) a correctly-labeled counterpart exists whose content is **byte-identical** (`filecmp.cmp(..., shallow=False)`) to the mislabeled file. The rule is direction-agnostic (a `.png` holding JPEG bytes is handled the same way) and covers both moments:
- **Recovery-write time**: write the corrected sibling, verify byte-identity, only then delete the mislabeled original.
- **Pre-existing pairs** (legacy dirs where the sibling already exists from an earlier run): probe candidates, delete the mislabeled one only when its correctly-labeled counterpart is byte-identical.

Without the flag, behavior is byte-identical to today (safe default preserved). Cleanup is best-effort: a per-file deletion failure is logged to stderr and never fails the extraction itself.

**Implementation constraints (Architect review, 2026-07-01)**:
- The "two moments" are **two distinct code locations** — the first-loop self-consistent branch (pre-existing pairs, the primary real case including the entire US-2 target) AND the `if chosen is None:` recovery branch. Deletion MUST be wired into both; recovery-only wiring silently misses the primary case.
- The deletion predicate keys on **mislabeled**, not "a sibling exists": delete X iff `_file_format(X)` ≠ X's extension AND a correctly-labeled counterpart Y exists with `filecmp.cmp(X, Y, shallow=False)` identical. A legitimate self-consistent `.jpg`+`.png` pair of different images is never touched (AC-1h).
- In the recovery-write path, deletion is additionally gated on the corrected sibling **not having pre-existed** the copy (`pre_existed` recorded before `copyfile`) — prevents the cross-swap edge (both files mislabeled in opposite directions) from amplifying the pre-existing overwrite behavior into data loss (AC-1g).
- The flag threads into `detect_images` as a **defaulted kwarg** (`cleanup: bool = False`): `tests/scripts/test_extractor_contract_fixes.py:200` calls it with two positional args, and all no-flag callers must stay byte-identical.

## User Stories

1. **US-1 (P0)** — When I run the report pipeline against a legacy assessment directory containing mislabeled/corrected duplicate pairs, I want an explicit opt-in cleanup that removes the mislabeled originals, so I can reclaim the duplicate storage and remove path ambiguity without hand-rolled `rm` one-liners.
   - AC-1a: Given `threat-baseball-card.jpg` with PNG bytes and a byte-identical `threat-baseball-card.png`, when run with `--cleanup-mislabeled-images`, then the `.jpg` is deleted, the emitted image path is the `.png`, and one stderr line records the deletion.
   - AC-1b: Given the same directory, when run WITHOUT the flag, then both files persist and emitted output is byte-identical to current behavior.
   - AC-1c: Given a mislabeled `.jpg` with no sibling yet, when run with the flag, then the corrected sibling is written first and the original deleted only after byte-identity verification of the written sibling.
   - AC-1d: Given a `.jpg` and `.png` that are NOT byte-identical, when run with the flag, then neither file is deleted (never guess which is authoritative).
   - AC-1e: Given a directory with only correctly-labeled images, when run with the flag, then no deletions occur and no cleanup output is emitted.
   - AC-1f: Given a truncated/failed sibling copy in the recovery path (forced short `copyfile`), when run with the flag, then the mislabeled original is NOT deleted and the run still exits 0 (byte-identity doubles as copy-success verification).
   - AC-1g: Given a cross-swapped pair (`.jpg` holds PNG bytes AND `.png` holds JPEG bytes), when run with the flag, then no file is deleted (recovery-path deletion fires only when the corrected sibling did not pre-exist the copy).
   - AC-1h: Given a self-consistent `.jpg` and `.png` that are different legitimate images, when run with the flag, then neither is deleted (predicate keys on mislabeled, not sibling-existence).

2. **US-2 (P1, gated)** — When I maintain tachi itself, I want the in-repo legacy snapshot pairs cleaned via the new flag (dogfood), so the repo stops carrying 6 duplicate images and demonstrates the sanctioned cleanup path.
   - AC-2a: Given `examples/agentic-app/test-output/2026-04-19T03-20-30/`, when the flag runs, then the 6 mislabeled `.jpg` files are removed and the safety proof is **path-invariance**: `report-data.typ` generated for that directory is byte-identical before and after cleanup (the `.png` is already selected today with the `.jpg` present), plus the extractor test module green. (The backward-compat/byte-identity suites exclude this dir — they are hygiene, not proof.)
   - AC-2b (fallback only — default is CLEAN per OQ-2): if plan/build-stage verification surfaces a consumer of the snapshot images, defer US-2 with documented rationale (Issue #217 comment) — do not force.

3. **US-3 (P1)** — When I read the report-assembly docs as an adopter with legacy directories, I want the duplicate-pair expectation and the sanctioned cleanup command documented, so I know the duplicates are expected and how to remove them safely.
   - AC-3a: Given the report-assembly reference docs, when I look up legacy image handling, then the duplicate-pair origin (gemini-2.5-flash-image fallback era), the flag invocation, and the double-gate safety semantics are documented; the raw `find … rm` one-liner is NOT the recommended path.

**Issue #217 acceptance mapping**: "Decision documented" → this PRD + closing Issue comment; "(c): flag implemented + tested" → US-1; "(a): callers' guide updated" → US-3.

## Success Metrics

- **SC-1 Cleanup efficacy**: duplicate mislabeled pairs in a flagged run: N → 0 (in-repo target: 6 → 0, subject to the US-2 gate).
- **SC-2 Zero default-path regression**: without the flag, `tests/scripts/test_extract_report_data.py` green and emitted `report-data.typ` byte-identical on the frozen snapshot.
- **SC-3 Deletion safety (test-enforced)**: no code path deletes a file without BOTH the flag and byte-identity proof; AC-1d, AC-1f (truncated copy), AC-1g (cross-swap), and AC-1h (mixed self-consistent pair) each covered by a dedicated test.

## Scope

**In (P0)**: `--cleanup-mislabeled-images` flag in `build_parser()` + double-gated deletion in `detect_images` (threaded via `main`); stderr logging per deletion; best-effort error handling (cleanup failure never fails extraction); new test cases in `tests/scripts/test_extract_report_data.py` covering AC-1a–AC-1h; flag threads as a defaulted kwarg (no-flag callers byte-identical).
**In (P1)**: US-2 in-repo dogfood cleanup (gated per AC-2b); US-3 docs update in the report-assembly reference surface.
**Out**:
- Option (b) — changing `copyfile` to `move` or any destructive-by-default behavior.
- Producer-side changes (`tachi-threat-infographic` agent — already fixed by #215/PR #216).
- Cleanup of anything beyond the 6 known stems in the target directory (no generic directory janitor).
- Auto-passing the flag from the `tachi-report-assembler` agent — deletion stays a human opt-in decision (revisit on adopter signal; OQ-1).
- A standalone cleanup script (code economy: the magic-byte probe already lives in `extract-report-data.py`).

## Timeline

Derived from the team-lead estimate in `specs/217-detect-images-duplicate-cleanup/feasibility-check.md` (`estimate.planning_days`): **1.0 eng-day central (0.5 floor / 2.0 ceiling)**, independently confirmed bottom-up by the Team-Lead review (2026-07-01) — single build wave: flag + deletion logic + tests (~0.5d), US-2 gated dogfood + byte-identity verification (~0.25d), US-3 docs (~0.25d). Dev Complete target: 1 working day from plan approval.

## Risks

- **R-1 Frozen-snapshot mutation (US-2) — DOWNGRADED at review**: both reviewers independently verified the feared failure mode ("silently redden the byte-identity suite," the KB-15 pattern) does not hold — no test consumes the snapshot's images (`agentic-app` is excluded from `BASELINE_EXAMPLES`; `test-output/` is globbed out of the MAESTRO invariant; the suite is local-only, wired into no CI), and the emitted path is invariant under deletion (the `.png` is selected today with the `.jpg` present). Residual risk is historical-fixture integrity only; resolved by OQ-2 = CLEAN with AC-2a's targeted path-invariance assertion as the positive proof.
- **R-2 Orphaned external references** to a deleted mislabeled path. *Mitigation*: opt-in flag (never default), byte-identity guard means the content still exists under the corrected name, and US-3 documents the rename mapping.
- **R-3 Filesystem edge cases** (permissions, races) during deletion. *Mitigation*: per-file try/except; log to stderr and continue; extraction result is identical whether cleanup succeeds or not.

## Open Questions

- [ ] OQ-1: Should the `tachi-report-assembler` agent ever auto-pass the flag? Default NO (opt-in only) — revisit on adopter signal. — Owner: PM — Status: Answered (default NO)
- [x] OQ-2: US-2 frozen-snapshot disposition — clean (dogfood) vs preserve-as-fixture. — Owner: Architect — Status: **Answered 2026-07-01: CLEAN, proceed with US-2** (no test consumes the snapshot's images; emitted path invariant under deletion; AC-2b defer path retained as documented fallback only)

## References

- [Issue #217](https://github.com/davidmatousek/tachi/issues/217) · parent [#215](https://github.com/davidmatousek/tachi/issues/215) / [PR #216](https://github.com/davidmatousek/tachi/pull/216)
- Code: `scripts/extract-report-data.py` — `detect_images` (L1463–1530; recovery branch proper L1512–1525; single call site L2164), `build_parser()` (L2020)
- Tests: `tests/scripts/test_extract_report_data.py:242` (existing recovery-path coverage)
- Governance: `.aod/memory/constitution.md` (VI Testing Excellence), `.claude/rules/code-economy.md` (safety carve-outs: error handling, one runnable check)
- Initiative: BLP-06 integrity & hardening — Wave 3

## Approval & Sign-Off

| Role | Name | Status | Date | Comments |
|------|------|--------|------|----------|
| Product Manager | product-manager | ✅ Approved | 2026-07-01 | PM author — decision (c)+(a), option (b) rejected |
| Architect | architect | 🟡 Approved with Comments | 2026-07-01 | 6 non-blocking (2 MED / 3 LOW / 1 NIT); OQ-2 = CLEAN; both-locations wiring; details `.aod/results/architect.md` |
| Engineering Lead | team-lead | 🟡 Approved with Comments | 2026-07-01 | Estimate 0.5/1.0/2.0 confirmed; single wave; senior-backend-engineer authors code+tests; details `.aod/results/team-lead.md` |

Legend: ✅ Approved | 🟡 Approved with Comments | ❌ Rejected | 📋 Pending

## Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-07-01 | product-manager | Initial PRD from Issue #217 (decision: option (c) + (a)) |
| 1.1 | 2026-07-01 | product-manager | Folds Triad corrections: OQ-2 = CLEAN, AC-2a → path-invariance, R-1 downgraded, AC-1f/1g/1h added, both-locations + defaulted-kwarg constraints |
