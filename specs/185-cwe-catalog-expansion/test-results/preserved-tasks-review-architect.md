# Architect Review — tasks.md (F-185 CWE Catalog Expansion, T029 Drift-Edge Restoration)

**Reviewer**: architect
**Date**: 2026-06-11
**Artifact**: `specs/185-cwe-catalog-expansion/tasks.md` (T001–T020), against plan.md (dual-signed, all 4 ratifications granted), spec.md FR-001..FR-008/SC-001..SC-006, contracts/ (restored-edges.schema.md, baseline-regen.contract.md), quickstart.md, and the live codebase.
**Verdict**: **APPROVED_WITH_CONCERNS** — 4 LOW + 2 INFO/cosmetic. No structural change to the task graph required; all items foldable at task-execution time. No re-review needed.

---

## 1. Dependency Ordering under FR-030 — CORRECT

- **Extraction before any production edit**: T005 (extract + commit `restored-edges.yaml`) is explicitly declared blocking ("T005 commit blocks all production-data edits"), sits on the critical path before T007, and Phase 2's checkpoint gates Phase 3 entry. T005 ∥ T006 correctly honors FR-003's "parallel with — not gated on — the FR-001 disposition" (plan D5 twin tracks). Risk 185.1 closes at the right moment.
- **Records strictly before edges**: T011 declared "after T010 (records before edges — FR-030)". Records commit at the T010 gate; edges insert at T011 and commit at the T013 gate. The integrity suite's referential check is edge→record directional, so the 40 unreferenced records at T010 are trivially green — verified consistent with my plan-stage R4 analysis.
- **Baselines after final data**: T014 declared "after T013 (baselines capture final data)" — correct; sequential per-example regen (shared `report-data.typ`) carried from the contract.
- **Disposition gates inserts**: T007 after T006 + T002 — correct (FR-001 "before any catalog or crosswalk modification lands"). T006's 8 sentinels enumerate to exactly 8 (CWE-16/255/937/1035/693 + 1426/1427/1039) and include the CWE-693 re-stranding consequence note from the spec edge case.
- **Critical path** (T001→T003→T005→(T006)→T007→T010→T011→T013→T014→T015→T018→T019→T020) is internally consistent; T016/T017 correctly off-path.

## 2. Tasks-Stage Folds (my plan-review C1–C5) — LANDED

| Fold | Where | Status |
|---|---|---|
| C1 (MED) dual expected-delta | T014: "BOTH expected attributions (cwe 53→93 + inherited mitre-atlas 30→36)"; contract invariant 1(b) amended at plan stage | LANDED |
| C1 pre-existing-red evidence | T001: records EXPECTED RED pre-state, ATLAS-CA attribution, "do NOT fix anything here" | LANDED |
| C1 restores-green framing | T015: "red→green flip vs T001 pre-state"; contract invariant 3 | LANDED |
| C1 dual-attribute CHANGELOG | T018: "dual-attributing baseline regen: F-185 CWE growth + absorbed #186 ATLAS delta" | LANDED |
| C2 (LOW) 0.00% wording | T014: "percentages may stay 0.00% — denominators/Gap rows are the visible delta" | LANDED |
| C3 (LOW) prospective-only D-7 | T018: "prospective-only wording, 5/8 substitution CWEs now cataloged: 307/311/319/326/732" | LANDED (core) — see Concern N3 for the secondary clause |
| C5 (LOW) report-data.typ restore | T014 + contract invariant 5 | LANDED |
| C4 (LOW, optional) line-number drift | baseline-regen.contract.md still cites test lines 37–44 / 15–23 (actual 45–52 / 15–24) | NOT FIXED — was optional; cosmetic, symbols also cited |

## 3. Parallel Markers — SAFE (pairwise-disjoint write sets, verified)

- **T001 ∥ T002**: `test-results/pre-state.md` vs `test-results/corpus-pin.md`. Disjoint.
- **T003 ∥ T004**: two different scripts, two different outputs. Disjoint.
- **T005 ∥ T006**: `restored-edges.yaml` + commit vs Issue #185 comment + `disposition.md`. Disjoint; extraction is disposition-independent (D5).
- **T016 ∥ T017 ∥ (T014→T015)**: T014 writes `examples/*/security-report.pdf.baseline` ×6 + transient `report-data.typ` + `baseline-diff.md`; T016 writes `scripts/name_diff.py` + `name-diff.md` (reads cwe.yaml records + XML); T017 writes `review-sweep.md` + possibly stale-count doc lines in docs//schemas (not cwe.yaml record entries; a header-comment touch cannot affect T016's record parse). No intersection with T014's files. Safe.
- Note: T017 is labeled "read-only sweep" in the dependency notes but its description permits doc edits ("update any found") — the write set is still disjoint from its parallel peers, so the [P] is safe; the label is just loose (cosmetic).

## 4. Gate Sufficiency — SUFFICIENT (every commit green)

- Commit points T005/T010/T013/T015/T018/T020: T005 touches only `specs/` (outside the integrity suite's load set); T010 and T013 run the 5-function integrity suite *before* their commits (FR-005/SC-004 honored at every `schemas/taxonomy/`-touching commit); T015 commits baselines only after the byte-identity suite is green; T018 is docs-only; T020 runs full pytest + quickstart walkthrough before push.
- **Byte-exactness verification (T013)**: correctly placed at the US2 gate — a data property checked *before* the expensive T014 regen, so an edge mutation can't invalidate a finished regen run.
- **R7 name gate (T016)**: well-placed; dependencies correctly allow it to start as soon as T007+T004 exist. Recommendation (N4): start it before or alongside T014 — a name fix to cwe.yaml after baselines regen would force a re-regen (CA pages render per-record content).
- Byte-identity red at intermediate branch commits (T010/T013) is correctly tolerated — atomicity scoped to main via single PR #328 (contract invariant 4; PR verified live: OPEN, draft, title `feat(185): cwe.yaml expansion + 67 drift-edge restoration (F-A1.2)`).
- HALT condition on non-CA delta (R6) carried into T014. Both recovery commits verified present today (`git cat-file -t` → commit ×2), so T001 will pass as written.

## 5. Executability — GOOD, with three precision findings

Verified against the live repo: record count grep `grep -c "^- id: "` → 53 ✓; YAML-parse edge counts 578 total / 541 primary / 0 low ✓ (matches every artifact); `ORDERED_FRAMEWORKS` at extract-report-data.py:1077 contains both `cwe` and `mitre-atlas` ✓; integrity suite = 5 functions ✓; task arithmetic 2+3+5+3+6+1 = 20 ✓; FR→task coverage complete (FR-007(g) issue closure correctly deferred to `/aod.deliver`; SC-006's `/aod.analyze` deliver-stage owned).

### N1 (LOW) — grep edge-count method over-counts by +1; quickstart §0 erratum
`grep -c "edge_type:"` matches header comments: current file prints **579** (true 578), `e58f247` blob prints **552** (true 551), `991e1ee` prints **439** (true 438). Quickstart §0's own documented command therefore outputs 552 while its inline comment says `# 551` — an implementer at T001 hits an immediate expected-vs-actual contradiction on the feature's very first verification (erratum carried from plan stage; my plan-review derivation used YAML parse, which is why it reported 551/438/578 exactly). **Fold at T001/T013 execution**: count via YAML parse (or rely on the integrity suite, which parses) and record both numbers with the +1-comment-offset explanation in pre-state.md; optionally fix the quickstart §0 comment to 552. The authoritative pytest gates are unaffected.

### N2 (LOW) — "6/6" shorthand vs literal pytest totals
`tests/scripts/test_backward_compatibility.py` collects **14** tests (6 parametrized byte-identity + 8 F-142 invariant/gate tests). T001's "6/6 FAIL" will literally print `6 failed, 8 passed`; T015's "6/6 green" prints `14 passed`. Meaning is correct (the byte-identity parametrized set is the flip set); record the literal totals in pre-state.md / the T015 evidence so the "8 passed" lines aren't mistaken for a partial fix at T001 or the "14" for scope creep at T015.

### N3 (LOW) — T018 omits C3's secondary clause
T018 carries the prospective-only D-7 wording (core of C3) but not the second sentence I required: the annotation should also record that **F-185 adds a third catalog-growth trigger (crosswalk-restoration evidence) alongside D-7's "detection-tier evidence, NOT attestation-baseline runs" dichotomy — the trigger taxonomy is extended, not contradicted**. Restated here for durability (the plan-stage review file is overwritten by this one); fold into the annotation text at T018 execution. Also include: the 12 historical substitutions in committed baseline Section 9 blocks are NOT retro-rewritten.

### N4 (LOW) — FR-008 spot-check traceability
The 8-sentinel live-page spot-checks moved from the plan's verification wave (W2-a, tester) to T006 (architect, pre-insertion). This is strictly better placement — names/status verified before records land — but FR-008's parenthetical attaches the spot-checks to the verification wave, so T016's `name-diff.md` evidence should cross-reference T006's sentinel results to keep FR-008 traceable. Additionally, schedule T016 before/alongside T014 (its dependencies already permit it — needs only T007+T004) so an improbable name fix cannot invalidate a completed regen.

### N5 (INFO) — `/aod.analyze` not in T020
SC-006 requires a clean `/aod.analyze`; T020 doesn't run it. House workflow owns it at the deliver stage (CLAUDE.md "before PRs"; quickstart §7 lists it under done criteria), and Issue closure is likewise deliver-owned per the tasks Notes — acceptable, but adding it to T020 would make the final gate self-contained. Optional.

### N6 (COSMETIC)
(a) C4 line drift persists in baseline-regen.contract.md (37–44 → actual 45–52; 15–23 → actual 15–24; contract header cites extract-report-data.py:1076 → actual 1077) — prefer symbols, leave or fix opportunistically. (b) T017's grep pattern includes bare `578`, false-positive-prone in docs/ (quickstart §6 omits it; T017 is the safer superset — implementer judgment flagged). (c) T018's stale-by-design CHANGELOG note should cite the test docstring's F-6/F-7 exclusion attribution (per plan-review R2 note (a)) to avoid F-241 attribution confusion. (d) T016/T017 evidence files and any T017 doc fixes have no named commit — they ride into T018/T020; harmless (cannot affect suites) but the T018 committer should sweep them deliberately.

## 6. Sign-off

**Architect: APPROVED_WITH_CONCERNS.** Task graph, FR-030 sequencing, [P] safety, and gate placement are all correct as written; every fold I deferred to tasks stage landed except one sentence of C3 (N3, restated above). N1–N4 are execution-time folds requiring no tasks.md restructure. Implementation may proceed.
