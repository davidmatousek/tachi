# Team-Lead Review — tasks.md (Feature 185: CWE Catalog Expansion, F-A1.2)

**Reviewer**: team-lead | **Date**: 2026-06-11 | **Artifact**: `specs/185-cwe-catalog-expansion/tasks.md`
**Verdict**: APPROVED_WITH_CONCERNS (0 blocking; 1 MED folded by this review's explicit re-pin; 4 LOW notes)
**Revised O/R/P**: **0.75 / 1.0 / 1.5 days** (supersedes the PRD v1.1 pin of 0.5/0.75/1.0)

---

## 1. Timeline Re-Validation (PM condition) — REVISED

The PRD v1.1 pin (0.5/0.75/1.0d) was set **before** plan stage added two cost centers:

1. **FR-006 baseline-regen lane (T014/T015)** — 6 sequential extract+typst-compile runs (shared `report-data.typ` mutation forbids parallel regen, per contract), per-page `pdftotext` diff old-vs-new across 6 PDFs (1.3–7.0 MB; maestro-reference is the 7 MB outlier), evidence write-up, `report-data.typ` restore, suite gate + binary commit. Note the regen cycle actually runs **three times** end-to-end: T014 (regen), T015 (suite regenerates again to byte-compare), T020 (full pytest regenerates a third time). Compile mechanics ≈ 5–15 min/cycle; the diff scripting + evidence dominates. Incremental: **+1.5–2.0h realistic; +2.5–3h if the R6 halt path fires** (non-CA delta → typst pin investigation → re-run).
2. **Red-main discovery ripple** — T001 expected-red pre-state recording (+0.25h); T018/T019 expansion: dual-attribution CHANGELOG, ADR-037 D-7 annotation, PRD v1.2 errata, KB process-lesson (+0.5–0.75h vs the original docs-closure scope).

**Arithmetic** (8h day): O = 0.5d + ~1.5h best-case regen → **0.75d**. R = 0.75d + ~2.25h → **1.0d**. P = 1.0d + ~3.5h (R6 halt + name-diff remediation tail) → **1.5d**.

**Floor conditions updated**: the 0.75 floor now requires (a) scripted harvest (T004, unchanged from PRD), AND (b) first-pass-clean CA-only page diffs at T014 (no R6 halt). Confidence: HIGH — mechanism proven by #186; regen lane empirically de-risked (§5.1).

**Action**: tasks.md §Estimated Effort (line 144) still cites the stale 0.5/0.75/1.0 pin — refresh to 0.75/1.0/1.5 at sign-off application; T019's PRD v1.2 errata MUST carry the revised pin (this satisfies the PM condition).

## 2. Granularity — PASS

20 tasks (2 setup + 3 foundational + 5 US1 + 3 US2 + 6 US3 + 1 polish); every task is single-agent, single-sitting. T014 is the chunkiest but appropriately atomic — the regen contract makes it deterministic and the HALT instruction correctly bounds the failure mode rather than splitting prematurely. T006 properly isolates the only judgment work. T018/T019 doc bundles are each one sitting. No task needs splitting or merging.

## 3. Critical Path & Parallelization — PASS (one timing observation)

Stated path T001→T003→T005→(T006)→T007→T010→T011→T013→T014→T015→T018→T019→T020 is **topologically correct** (T005's commit blocks all production-data edits; FR-030 forces records→edges→baselines). Observation: the **timing-dominant entry leg into T007 is T002→T004→T006** (~2–3h: download+pin, harvest script, 40-ID disposition + 8 spot-checks + Issue posting) vs T001→T003→T005 (~1.5–2h). tasks.md acknowledges this ("T002/T004 feed it early"); both lanes run concurrently so no schedule change — but T006, not T005, is the start-side pacing item. Watch it first.

Parallelization is maximized: T001∥T002, T003∥T004, T005∥T006 (plan D5 twin tracks), T016∥T017∥(T014→T015) — file-disjointness verified for the US3 fan-out (baselines vs name-diff script vs read-only sweep). Sequential regen inside T014 is contract-mandated (shared typ file), not a missed opportunity. Minor: T009 (README) could carry [P] alongside T008 (cwe.yaml header) — ~15 min upside, not required.

## 4. Wave→Agent Assignments — APPROVED (all names registry-valid per `.claude/agents/_README.md`)

| Wave | Tasks | Agent |
|---|---|---|
| W0 (setup+foundational) | T001, T002, T003, T004, T005 | senior-backend-engineer (T001/T002 included) |
| W0 (disposition, ∥) | T006 | architect |
| W1 (data, sequential) | T007–T015 | senior-backend-engineer |
| W2 (verification, ∥) | T016 | tester |
| W2 (verification, ∥) | T017 | code-reviewer |
| W2 (closure) | T018, T019 | senior-backend-engineer |
| W2 (final gate) | T020 | **tester (recommended)** — final-gate independence from the data author; senior-backend-engineer acceptable for the push/PR mechanics |

Moving T004 harvest scripting from plan W0-a (architect) to SBE is a correct refinement — architect stays judgment-only and consumes `harvest-40.md`. SBE carries 14/20 tasks; heavy but inherent to a strictly-sequenced data feature — tasks are short, no parallel overload. Fits the /aod.build 3-wave ceiling in one session: W0 → W1 → W2.

## 5. Risk Assessment

1. **T014 typst availability — VERIFIED CLEAR**: `typst 0.14.2` at `/opt/homebrew/bin/typst`; all 6 baselines present. Baselines were last regenerated 2026-06-02/04 (file mtimes) — almost certainly by this same binary, and the plan review's pdftotext finding (100% of red-main delta attributable to ATLAS CA pages, zero typst drift) empirically deflates R6 to LOW. Sequential wall-clock (~20–45 min cumulative across 3 regen cycles) is absorbed in the revised estimate.
2. **T006 disposition turnaround — LOW**: in-session architect agent (~1–1.5h), not a human-latency gate. External deps: cwe.mitre.org spot-checks (8 pages; F-180 fetched 53 from the same source with no anti-bot tripwire) + `gh` Issue posting. Any add-set ⊆ 40 shrinks T007/T011 without rework (Risk 185.3 design holds).
3. **Red-main exposure — CONTAINED, one residual**: T001's expected-red recording with attribution guards against masking unrelated regressions under the inherited #186 drift. Residual: verified **no CI workflow runs `test_backward_compatibility.py`** — the red→green flip is locally enforced only (explains how #186's drift went unnoticed). T020 full-pytest is the enforcement point; the T019 KB lesson (`ORDERED_FRAMEWORKS` check at definition time) is the systemic fix — confirm it lands.
4. **T017/T018 surface overlap — LOW**: T017's stale-count fixes could touch docs files near T018's edits; in practice T017 (∥ T014–15) completes before T018 (after T015). If T017 finds counts in CHANGELOG/ADR-037-adjacent files, defer those specific fixes to T018's commit.
5. **Binary churn — accepted**: T015 commits ~14 MB of regenerated PDFs in the single-PR delivery (contract invariant 4); matches prior regen-commit precedent.

## 6. Conditions & Sign-off

- **C1 (MED, folded by this review)**: Revised O/R/P 0.75/1.0/1.5d is the pin of record — update tasks.md §Estimated Effort and carry into T019's PRD v1.2 errata.
- **C2 (LOW)**: T020 → tester preferred for gate independence.
- **C3 (LOW)**: Orchestrator should treat T006 as the start-side pacing item (launch T002→T004 immediately at session start).
- **C4 (LOW)**: T017 defers count-fixes on T018-owned files to T018.

**Team-Lead sign-off: APPROVED_WITH_CONCERNS** — tasks.md is feasible, correctly granulated, correctly pathed, and registry-valid in its assignments. Proceed to `/aod.build` once the effort line is refreshed; no re-review needed.
