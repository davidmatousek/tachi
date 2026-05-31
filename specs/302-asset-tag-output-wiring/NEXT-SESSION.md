# NEXT-SESSION — Feature 302 (Asset-Tag Output Wiring, F-260b)

**Branch**: `302-asset-tag-output-wiring` | **Draft PR**: #303
**Handoff written**: 2026-05-31 | **Reason**: standalone 3-wave ceiling reached (build Step 4 sub-step 7) + high context
**Progress**: 6 / 22 tasks complete (T001–T006). P0 checkpoint APPROVED (GO).

---

## Next Actions (resume here)

Run `/aod.build 302` in a fresh conversation. It auto-resumes at the first unchecked task.
The next wave is **Wave 3** (the build will dispatch it):

- **T008** [US1] — add the shared `parse_affected_assets(threats_content) -> dict[finding_id, list[str]]` extractor to `scripts/sarif_common.py` (single source for the verification tier; mirrors the `parse_component_metadata` precedent). Agent: **senior-backend-engineer**. Depends on T004 (done).
- **T007** [P] [US2] — populator unit tests in `tests/scripts/test_affected_assets_wiring.py` (SC-003 all-6-tags, SC-005 empty-default, fuzzy match, Q4 no-op-modifier-still-listed, sorted/deduped, UNCHANGED/RESOLVED carry the field). Agent: **tester**. Depends on T005 (done). **First write to the shared test file.**

T007 ∥ T008 are parallel (different files: test file vs `sarif_common.py`).

> **CRITICAL serialize-on-write rule**: T007 (Wave 3) → T013 (Wave 5) → T017 (Wave 6) ALL append to
> `tests/scripts/test_affected_assets_wiring.py`. They land in separate waves by design — NEVER run them concurrently.

---

## What's done (T001–T006) — all committed, pushed to PR #303

| Task | Wave | What | Commit |
|------|------|------|--------|
| T002 | 1 | `affected_assets` field in `schemas/finding.yaml` (1.8→1.9, frozen 6-value enum, default []) | a39964c |
| T003 | 1 | `docs/architecture/02_ADRs/ADR-046-asset-tag-output-wiring.md` (thin, 113 ln) | a39964c |
| T004 | 1 | block contract in `finding-format-shared.md` + `threats.md` template (additive) | a39964c |
| T001 | 0 | SC-002 baseline snapshot → `test-results/wave-00-baseline-before/` | 36d7c96 |
| T005 | 2 | `scripts/populate-affected-assets.py` — deterministic value authority | 36d7c96 |
| T006 | 2 | populator wired into `tachi.threat-model.md` (Step 2.5) + `tachi.risk-score.md` (Step 1.5) | e703ccb |
| — | 2 | regression fix: `test_output_integrity.py` schema pin 1.8→1.9 | e57f1d9 |

**Populator verified** on the worked example: `[phi,pii]`×3 (KB), `[phi]`×12, `[safety]`×9, `[auth]`×3, `[]`×59 — all 4 example tags propagate; idempotent; stdlib-only.

---

## Gate status (verified, not assumed)

- **P0 architect checkpoint (Waves 0–2)**: APPROVED / GO. 0 BLOCKING / 0 HIGH / 1 MEDIUM / 3 LOW (all advisory). Full review: `.aod/results/architect.md`.
- **SC-011 frozen gate**: `git diff main -- schemas/risk-scoring.yaml scripts/tachi_parsers.py` = EMPTY. ✅
- **SC-002 discipline**: template + shared-ref pure-append (0 deletions). ✅
- **Post-Wave-2 tests** (`tests/scripts/`, full run 94.8s): 773 pass / 16 fail / 1 skip.
  - 1 regression (schema pin) — **FIXED** this session.
  - 15 pre-existing, NOT F-302 (agent-.md line-cap + OWASP-attestation on files F-302 never touched; byte-identical to main). Full classification: `test-results/wave-02/results.json`.
  - F-260b suite `test_asset_sensitivity_tags.py`: 26/26. ✅

---

## Architect advisories to honor in upcoming waves

- **MEDIUM (T002 retro)**: schema bump should have enumerated all `== "1.8"` pins. Swept — only `test_output_integrity` pinned it (fixtures legitimately retain 1.8 as authored-version data). Do a final grep before delivery.
- **LOW → T013**: assert the snake_case `affected_assets` **key string** byte-identity across surfaces, not just values.
- **LOW → T016**: baseline regen MUST run the populator so committed example baselines gain the block.
- **LOW → T007**: add a populator idempotency assertion.

---

## Remaining waves (from agent-assignments.md)

- **Wave 3**: T007 (tester) ∥ T008 (sbe)
- **Wave 4**: T009 ∥ T010 ∥ T011 ∥ T012 (SARIF emitters + production LLM authoring contracts) — all sbe
- **Wave 5**: T013 (tester, SC-006 cross-format) ∥ T014 ∥ T015 (docs)
- **Wave 6**: T016 (baseline regen) ∥ T017 (schema-doc/ceiling tests)
- **Wave 7**: T018 — `[MANUAL-ONLY]` live `tachi.threat-model` run (R9 gate)
- **Wave 8**: T019 (CHANGELOG @north-echo credit) ∥ T020 (CI wiring)
- **Wave 9**: T021 (frozen-constraint gate) → T022 (full quickstart acceptance)
- Then build Steps 5–8 (final reviews, security scan, completion report) → `/aod.deliver` → `/aod.document`

**Delivery-time tails (NOT build waves)**: Discussion #246 ack + offered `Co-Authored-By`; close #302 + #260 (#246→#262→#260→#302 chain); release-please verify (`feat(302):`).

---

## Resume prompt

```
Resume F-260b asset-tag output wiring (branch: 302-asset-tag-output-wiring).
Waves 0-2 complete (T001-T006), P0 checkpoint APPROVED. Run /aod.build 302 to continue at Wave 3 (T007 + T008).
```
