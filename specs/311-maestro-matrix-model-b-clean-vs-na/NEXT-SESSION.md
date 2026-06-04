# NEXT-SESSION — F-311 MAESTRO Matrix Model B (clean vs. n/a)

**Branch**: `311-maestro-matrix-model-b-clean-vs-na` · **Date stopped**: 2026-06-04
**Stopped because**: standalone 3-wave ceiling (`/aod.build`, `orchestrated == false`). Waves 0–2 done; Waves 3–4 remain.

## Progress: 14/23 tasks (Phase A + Phase B COMPLETE)

| Wave | Phase | Tasks | Status |
|------|-------|-------|--------|
| 0 | Setup | T001, T002 | ✅ done (G0 PASS — baseline green) |
| 1 | A — source contract | T003–T008 | ✅ done (G1 PASS) |
| 2 | B — PDF ∥ infographic | T009–T014 | ✅ done (G2 PASS) |
| 3 | C — fixture + CI | T015, T016 | ⏳ NEXT |
| 4 | D — baseline regen + delivery | T017–T023 | ⏳ pending |

**What landed**: pure `classify_maestro_coverage_state` classifier (`tachi_parsers.py`, INV-1 pure, INV-3 ordinal-0); orchestrator Section-6 two-state directive (sole production authority) + docs (`output-schemas.md`, `coverage-matrix-model.md`); populator option-(a) examples-regen Section-1 read (D3-fenced); PDF `coverage_state` on `maestro_findings_by_layer` group records + Typst n/a branch; infographic `coverage_state` in `per_layer_summaries` + `{layer_bands_text}` n/a band; D3 fence verified (heatmap.json byte-unchanged). **F-311 test area: 69 passed, 2 skipped, 0 regressions.**

---

## ⚠️ CRITICAL — do this FIRST in Wave 3 (both Wave-2 agents flagged it)

**The committed `examples/microservices/threats.md` still carries Model-A CLEAN tokens on L1/L3/L5/L6** (verified — all five zero-finding layers read `Analyzed — no findings this scan`). So classifying the live example *today* yields `clean` (not `not_applicable`) for L1/L3/L5/L6.

T015's expected map (`L1·L3·L5·L6 = not_applicable`) therefore **cannot hold until `microservices/threats.md` is regenerated to Model-B**. The task plan sequences T018 (which regenerates threats.md) *after* T015 — a real ordering coupling.

**Resolution (recommended — option a):** At the START of Wave 3, regenerate the microservices fixture to Model-B before T015:
```bash
python3 scripts/populate-maestro-coverage.py examples/microservices/threats.md   # heading-normalize is built in
```
The populator (option-a, already verified) produces exactly the data-model map: **L7=clean, L1/L3/L5/L6=n/a, L2/L4=findings**. Then T015 asserts that map across all three surfaces.

**Coupling to remember**: regenerating `microservices/threats.md` changes content (clean→n/a on 4 layers) — this is the intended Phase-D churn (Decision F). `microservices` is one of the **6 byte-gated PDF baselines**, so T018 must deterministically re-freeze its `.pdf.baseline` (`SOURCE_DATE_EPOCH=1700000000`) and T020's byte-gate must re-freeze it deliberately (BASELINE_EXAMPLES set unchanged). Wave-3 fixture regen and Wave-4 PDF re-freeze are coupled for microservices.

*Alternative (option b)*: leave the committed threats.md as-is and have T015 run the populator on an in-memory copy at test time. Less clean — the fixture wouldn't reflect Model-B. Prefer (a).

**Test harness already built for you**: the PDF track added `_load_extract_module()` + a `parse_maestro_data(content)` harness and a `_SYNTHETIC_THREATS_MICROSERVICES_STATE_MAP` post-regen fixture in `tests/scripts/test_extract_report_data.py` — T015 can reuse this pattern to obtain PDF state at test time (Architect MEDIUM-A: PDF render IR is regenerated, not committed). The infographic side mirrors `_maestro_stack_template_data`.

---

## Next Actions (in order)

1. **Regen microservices fixture to Model-B** (the CRITICAL prerequisite above).
2. **T015** (`tester` + SBE) — cross-surface consistency test (new `tests/scripts/test_maestro_cross_surface_consistency.py` or a case in `test_maestro_coverage_invariant.py`): assert `state(threats.md §6 via classify_maestro_coverage_state) == state(report-data.typ coverage_state) == state(maestro-stack.json coverage_state)` for all 7 layers (L7=clean, L1·L3·L5·L6=not_applicable, L2·L4=findings). Obtain PDF state via `parse_maestro_data` at test time. Add the negative test: force one surface's L7 → not_applicable ⇒ assertion fails naming **L7**.
3. **T016** (`devops`) — wire T015 into `.github/workflows/tachi-maestro-coverage.yml` in **F-250 lock-step** (`on.pull_request.paths` AND the pytest invocation in the SAME commit); reclassify the 5 regression-necessary paths (`extract-report-data.py`, `extract-infographic-data.py`, `maestro-findings.typ`, `infographic-maestro-stack.md`, `orchestrator.md`). Do NOT touch `tachi-pytest.yml`.
4. **T017–T023** (Wave 4): drift audit (DROP no-drift, enumerate churn set in PR body) → deterministic baseline regen (heading-normalize first; `SOURCE_DATE_EPOCH=1700000000`; needs Typst+mmdc — both present) → [MANUAL-ONLY] annotation-only diff → byte-gate (`test_backward_compatibility.py` green, BASELINE_EXAMPLES unchanged) → CHANGELOG `feat(311)` → SC-003 no-schema-drift + `/aod.analyze` → quickstart e2e + deliver-gate.
5. **Step 5 Final Validation** (architect + code-reviewer + security-analyst on the full feature), **Step 6 Design Quality Gate** (likely "skipped — no UI files changed": no `*.css/*.jsx/*.tsx/*.html` changed; Typst + markdown templates fall outside the grep checks — verify), **Step 7 Security Scan** (`/security` skill), **Step 8** completion report + `summary.json`.

---

## Carry-forward facts

- **T008 MEDIUM-B → OPTION (a) RATIFIED** (PM+Architect+Team-Lead endorsed). **Record in PR body**: "T008: chose option (a) — examples-local Section-1 read + present-row re-decision in `populate-maestro-coverage.py`, fenced EXAMPLES-REGENERATION-ONLY (ADR-047 D3), reuses `classify_maestro_coverage_state`."
- **17 PRE-EXISTING test failures** in `test_mobile_top_10_coverage_bundle_enrichment.py` + `test_tool_abuse_enrichment.py` (line-count caps, M8 presence, byte-identity-against-main, source-attribution). CONFIRMED pre-existing via clean-baseline worktree at HEAD (zero F-311 code → same failures). **NOT F-311 regressions** — flag for separate triage; do not let them block F-311 gates. F-311 area is fully green.
- **`v4.40.0` git tag MISSING locally** — run `git fetch --tags` and confirm before `/aod.deliver` (T023 deliver-gate / Team-Lead R7). Release-please bases the next release on it.
- **Deliver-gate**: PR squash title MUST be `feat(311):` (release-please); verify a release-please PR opens post-merge.
- **Gates so far**: G0 ✅ G1 ✅ G2 ✅. G3 (consistency) + G4 (byte-gate) remain.
- Work is **committed locally** (Phase A+B checkpoint). Not yet pushed.

## Resume

```
claude "Resume F-311 MAESTRO Model B (branch: 311-maestro-matrix-model-b-clean-vs-na). Waves 0-2 complete (T001-T014). Run /aod.build to continue at Wave 3 — but FIRST read specs/311-maestro-matrix-model-b-clean-vs-na/NEXT-SESSION.md (critical microservices/threats.md regen prerequisite for T015)."
```
`/aod.build` auto-detects [X] tasks and resumes at Wave 3 (T015).
