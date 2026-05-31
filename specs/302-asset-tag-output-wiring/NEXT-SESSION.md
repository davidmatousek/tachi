# NEXT-SESSION — Feature 302 (Asset-Tag Output Wiring, F-260b)

**Branch**: `302-asset-tag-output-wiring` | **Draft PR**: #303
**Handoff written**: 2026-05-31 | **Reason**: standalone 3-wave ceiling reached (build Step 4 sub-step 7) — Waves 3, 4, 5 executed this session
**Progress**: 15 / 22 tasks complete (T001–T015). **P0 checkpoint APPROVED (GO)** + **P1 checkpoint APPROVED (GO)**.

---

## Next Actions (resume here)

Run `/aod.build 302` in a fresh conversation. It auto-resumes at the first unchecked task.
The next wave is **Wave 6** (the build will dispatch it):

- **T016** [US4] — regenerate the no-tag example baselines under `SOURCE_DATE_EPOCH=1700000000`; verify `git diff` shows ONLY the additive `affected_assets` block/property, all existing rows byte-identical (SC-002, AD-2). Agent: **tester**. Depends on T005/T006/T011/T012 (all done).
- **T017** [US4] — schema-doc accuracy test (SC-007) + ceiling-preservation test (SC-004: a tagged finding clamps at 9.2, `affected_assets` populated regardless) in `tests/scripts/test_affected_assets_wiring.py`. Agent: **tester**. Depends on T014 (done).

T016 ∥ T017 are parallel (different files: example baselines vs the test file).

> **CRITICAL serialize-on-write rule**: T017 is the **THIRD and final** append to
> `tests/scripts/test_affected_assets_wiring.py` (T007 Wave 3 → T013 Wave 5 → **T017 Wave 6**).
> T007 and T013 are both fully committed, so T017 can safely append — but it MUST be the only
> writer to that file in Wave 6. Add it under a new `# ===== SC-007/SC-004 (T017) =====` banner at EOF.

---

## What's done this session (T007–T015) — all committed, pushed to PR #303

| Task | Wave | What | Commit |
|------|------|------|--------|
| T007 | 3 | populator unit tests (22) in `tests/scripts/test_affected_assets_wiring.py` (1st write; incl. idempotency — P0 LOW discharged) | e4e8f94 |
| T008 | 3 | `parse_affected_assets(threats_content)->dict[id,list]` extractor in `scripts/sarif_common.py` (inverse of populator; verification-tier single source) | e4e8f94 |
| — | 3 | Step 4.6: 30 extractor edge-case tests in `tests/scripts/test_sarif_common_affected_assets.py` (separate file — keeps serialize-on-write file for T013/T017) | e4e8f94 |
| T009 | 4 | `result.properties.affected_assets` (snake_case) in `scripts/generate-threats-sarif.py`, sourced from the extractor | 96ea137 |
| T010 | 4 | same in `scripts/generate-risk-scores-sarif.py` (byte-identical key) | 96ea137 |
| T011 | 4 | orchestrator production authoring contract — `sarif-specification.md` (threats.sarif copies the block verbatim) | 96ea137 |
| T012 | 4 | risk-scorer production authoring contract — `risk-scorer.md` §10g.1 (risk-scores.sarif verbatim; §3.5 + 9.2 ceiling byte-UNCHANGED) | 96ea137 |
| T013 | 5 | **SC-006 cross-format equality** test (+4 cases) — `test_affected_assets_wiring.py:744`; 3-way per-finding equality + snake_case key-string identity (P0 LOW discharged) | 9ba8ea6 |
| T014 | 5 | `asset-modifiers.md` Output Contract section + stale `9.5`→`9.2` fix at the T-2 example | 9ba8ea6 |
| T015 | 5 | `schemas/README.md` `affected_assets` contract pointer | 9ba8ea6 |

**New F-260b tests: 56 total (T007 22 + extractor 30 + T013 SC-006 4) — all green.**

---

## Gate status (verified, not assumed)

- **P0 architect (Waves 0–2)**: APPROVED_WITH_CONCERNS / GO. Both MEDIUMs now **closed** by this session.
- **P1 architect (Waves 3–5)**: **APPROVED / GO** for Waves 6–9. 0 BLOCKING / 0 HIGH / 0 MEDIUM / 2 LOW. Both P0 LOW advisories **discharged**. Full review: `.aod/results/architect.md` → "## P1 Checkpoint Review".
- **SC-011 frozen gate**: `git diff main -- schemas/risk-scoring.yaml scripts/tachi_parsers.py` = EMPTY. ✅ `risk-scorer.md` §3.5 + 9.2 ceiling byte-unchanged (T012 additive-only); T014 did NOT touch `risk-scoring.yaml`.
- **Regression gate (all 3 waves)**: 0 regressions. Wave 3 822P/16F/2S → Wave 4 852P → Wave 5 856P (pass growth = the 34 new tests; failure set **byte-identical** across waves). `test-results/wave-0{3,4,5}/results.json`.
- **The 16 failures are F-302-independent** (do NOT chase them as F-302 bugs): 15 = pre-existing wave-02 cluster (agent-`.md` line-caps + OWASP attestation + `tool_abuse`; test files byte-identical to main); 1 = `test_init_sh_substitution.py::test_personalized_tree_bytes_match_baseline` (slow init test deselected at wave-02; fails on a **stale `tests/fixtures/init-baseline-tree/` snapshot** — drifted `docs/` files, 4 byte-identical to main + 1 planning-stage doc; NOT in F-302 scope — T016 regenerates EXAMPLE baselines, a different fixture).

---

## Architect advisories to honor in Waves 6–9

- **L-2 (load-bearing — Wave 6/7)**: production `threats.sarif`/`risk-scores.sarif` are **LLM-authored** (the `generate-*-sarif.py` scripts have NO production caller — regeneration/test-only). SC-006 (T013, green) only guards the **regeneration** path. The **production** cross-format guarantee rests on T016 (baseline snapshot) + T018 (live run). **T016 MUST run the populator and assert the snake_case `affected_assets` key + `[]`-default + 3-way equality on the regenerated EXAMPLE baselines.** Do NOT treat green SC-006 as proof of the production surfaces.
- **L-1 (cosmetic)**: tidy any prose that says SC-006 was "appended to the shared test file" — it's correct and lives at `test_affected_assets_wiring.py:744`; the 30 extractor edge cases are the separate `test_sarif_common_affected_assets.py`. No behavioral effect.
- **P0 carry (delivery-time)**: before `/aod.deliver`, do a final grep for any remaining `== "1.8"` `finding.yaml` schema pins (the bump was 1.8→1.9; only `test_output_integrity` pinned it — fixtures legitimately retain 1.8 as authored-version data).

---

## Remaining waves (from agent-assignments.md)

- **Wave 6**: T016 (tester, baseline regen SC-002) ∥ T017 (tester, SC-007 schema-doc + SC-004 ceiling)
- **Wave 7**: T018 — `[MANUAL-ONLY]` live `tachi.threat-model` run on `examples/agentic-app/architecture-with-asset-tags.md`; confirm `affected_assets` in `threats.md` + `threats.sarif` + `risk-scores.sarif` (R9 gate)
- **Wave 8**: T019 (sbe, CHANGELOG `feat(302):` + @north-echo prototype-author credit, NEVER "surfaced by") ∥ T020 (sbe, CI wiring — both test files into `tachi-pytest.yml` `paths:` + invocation, lock-step)
- **Wave 9**: T021 (tester, SC-011 frozen binary diff) → T022 (tester, full `quickstart.md` SC-001…SC-012 + NFR-2 score-equivalence)
- Then build **Steps 5–8** (final Architect+Code+Security reviews; Design Gate is N/A — no UI; **Security Scan Step 7 applies** to the new populator/extractor; completion report) → `/aod.deliver` → `/aod.document`

**Delivery-time tails (NOT build waves)**: FR-011c Discussion #246 ack + offered `Co-Authored-By`; FR-012 close #302 + parent #260 (completing #246→#262→#260→#302 chain); FR-010/SC-009 release-please verify (`feat(302):` squash-merge → release PR within ~30s).

---

## Resume prompt

```
Resume F-260b asset-tag output wiring (branch: 302-asset-tag-output-wiring).
Waves 0–5 complete (T001–T015), P0 + P1 checkpoints APPROVED. Run /aod.build 302 to continue at Wave 6 (T016 + T017).
Honor architect L-2: T016/T018 are the production runtime check; T017 is the final append to test_affected_assets_wiring.py.
```
