# NEXT-SESSION Handoff — Feature 098 (MAESTRO 7-Layer Coverage Matrix)

**Branch**: `098-maestro-7-layer` · **Issue**: #98 · BLP-04 Wave 4 · `feat(098)` · **Draft PR**: #310
**Stopped at**: standalone 3-wave ceiling (this session ran Waves 2→4)
**Resume at**: **Wave 5 / T013** (Polish, gates & PR)

---

## Status: Waves 0–4 COMPLETE (T001–T012), verified. Wave 5 remains (T013–T017). 12/17 tasks (71%).

### Issue #98 functional close-gate is MET
**G3 (Model A) PASSED** — US-1 (all 7 layers visible) + US-2 (zero-finding phrase parity md↔PDF) both demonstrably pass on regenerated examples. The remaining Wave 5 work is polish/gates/PR, not feature behavior.

### Done this session (Waves 2–4, committed)
| Task | What | Evidence | Commit |
|------|------|----------|--------|
| T006 | Ran populator over 9 in-scope files; 3 h3→h4 normalized (Architect HIGH gate G2) | all 9 now `#### `; agentic-app 7 canonical rows incl. L4; `--check` exit 0; U+2014 confirmed by codepoint; 2 table-less reports + test-output/ untouched | `656539b` |
| T007 | US-1 acceptance | agentic-app 7 rows L1→L7 + L4; spot-checks microservices + maestro-reference canonical | `656539b` |
| — | **P0 architect checkpoint (blocking)** | **APPROVED** — CONCERN-1 (h3→h4) resolved; SC-003 (no canonical seeding, populator unwired) structurally guaranteed; cleared for T011. `.aod/results/architect.md` | — |
| T008 | US-2 cross-format parity (G3 close-gate) | md cell (no period) + PDF prose page 14 (with period) both carry `Analyzed — no findings this scan`; U+2014 both; asserted on phrase not punctuation (PM OBS-2); temp render, clean tree. `.aod/results/tester.md` | `da1bb45` |
| T009 | unit assert in `test_extract_report_data.py` | `maestro_findings_by_layer` len==7 + zero-finding layer keeps empty `findings`; guards T003 filter removal; 13 passed | `da1bb45` |
| T010 | new `test_maestro_coverage_invariant.py` | heading-agnostic discovery (`^#{3,4}` or bare substring, NOT ####-anchored), all 7 L-IDs per table-bearing example, 2 table-less skipped; 9 passed/2 skip; mutation-proven | `da1bb45` |
| T011 | regenerated **6 gated PDF baselines** under `SOURCE_DATE_EPOCH=1700000000` | 5 changed (gained zero-finding rows); maestro-reference byte-identical (extractor re-sorts → order-only markdown change = no PDF delta) | `da1bb45` |
| T012 | G4 gate | backward-compat 6 baselines byte-identical (13 passed/1 skip) + both new files green → **35 passed, 3 skipped** | `da1bb45` |

### Gates passed: G0 ✓ · G1 ✓ · G2 ✓ · **G3 (close-gate) ✓** · G4 ✓ · P0 checkpoint ✓

---

## IMPORTANT scope decision carried into Wave 5 (T017 must reflect this)
**Non-gated example PDFs were deliberately NOT regenerated.** The byte-gate (`test_backward_compatibility.py:BASELINE_EXAMPLES`) is exactly the 6 {web-app, microservices, ascii-web-api, mermaid-agentic-app, free-text-microservice, maestro-reference} — all regenerated. The other committed PDFs derived from the 9 changed markdown files were checked empirically and **carry PRE-EXISTING `.pdf`↔`.baseline` divergences unrelated to #98** (maestro-reference `security-report.pdf` ≈307KB off its baseline; agentic-app/sample-report `.baseline` ≈365KB off its `.pdf`; mobile-banking-app/sample-report ≈8KB clean-098 delta but is F-7's example). Per **PM OBS-1** ("expect ONLY matrix row/order churn") + the prior out-of-scope guidance, regenerating them would inject non-098 binary churn. The committed render-path fix (orchestrator directive + extract filter + Typst literal) guarantees **all future** PDF generations show 7 layers. **Refreshing historical non-gated example PDFs is a separate artifact-hygiene task — do NOT bundle it into #98.** (Candidate follow-up issue if desired.)

The expected PR diff is therefore: **9 example `threats.md` (matrix rows/order/annotation) + 5 changed `.pdf.baseline` + 2 test files + tasks.md/results.json**. The agentic-app `threats.md` diff = added L4 row + Unclassified relocating to bottom + non-empty rows re-sorting to canonical order (PM OBS-1, expected churn, NOT content drift).

---

## Next actions — Wave 5 (Polish, gates & PR) — T013–T017
Per `agent-assignments.md` §3: T013 [P] + T015 [P] + T016 [P] independent; T014 then T017 close the wave (T017 strictly last).

- **T013** [P] (tester) — Verify **no SARIF/schema change** (FR-010): `git diff --stat main...HEAD` shows nothing under SARIF emitters or `schemas/`; confirm no `.sarif`/schema files in the diff.
- **T015** [P] (senior-backend-engineer) — CHANGELOG.md entry: `feat(098): MAESTRO coverage matrix always shows all 7 layers (Issue #98)`.
- **T016** [P] (senior-backend-engineer) — Create **2 follow-up GitHub issues** via `gh`: (a) FR-011 Model B clean-vs-`n/a` two-state annotation (needs `component_layer_map` from `extract-infographic-data.py`); (b) FR-012 `maestro-stack` infographic completeness. Both P1 follow-ups, NOT close-gates. **Consider a 3rd**: the non-gated example-PDF artifact-hygiene refresh (above) + the Architect's non-blocking residual (wire `test_maestro_coverage_invariant.py` into CI as a drift-gate).
- **T014** (tester) — Run `/aod.analyze`; confirm no cross-artifact inconsistencies (SC-005).
- **T017** (code-reviewer) — Assemble PR description; verify the agentic-app diff shows ONLY matrix rows/order churn (Risk 98.3, PM OBS-1); state the non-gated-PDF scope decision above; note the F-302 remedy (if `tests/fixtures/init-baseline-tree` fails on unrelated doc-drift, run `tests/fixtures/regenerate-baseline.sh` after verifying substitution semantics — separate fixture from the PDF `.baseline` gate). **PR title MUST be `feat(098): …`** (release-please gate).

### After Wave 5 (this is the LAST wave → build proceeds to final completion in the SAME run)
`/aod.build` will continue past Wave 5 to: **Step 5** Final Validation (architect + code-reviewer; this is the P1 boundary review) → **Step 6** Design Quality Gate (will record "Skipped — no UI files changed") → **Step 7** Security Scan (likely "Skipped — no code/manifest changed" beyond the additive test .py; if it runs, no auth/secrets touched) → **Step 8** completion report + `summary.json`.
Then: `/aod.deliver 098` (squash-merge PR #310 with `feat(098):` title; verify release-please PR opens, push empty `feat(098):` marker if it skips — see [[feedback_aod_deliver_release_gate]]).

---

## Hard constraints (unchanged)
1. **No canonical seeding** in `extract-report-data.py` (SC-003) — already honored; do not add.
2. **Determinism** — any further PDF (re)gen + the backward-compat test under `SOURCE_DATE_EPOCH=1700000000`.
3. **Annotation parity asserts the phrase, not the punctuation** (PM OBS-2).
4. **PR title** = `feat(098): …` (release-please gate).
5. **Do NOT chase the 15 pre-existing test failures** (coverage_attestation_audit, *_enrichment, tool_abuse_enrichment, mobile_top_10) — branch-level, unrelated to #98. Run pytest with `--ignore=tests/fixtures` (F-302 init-baseline-tree collection error).

## Test state
- Feature tests: **35 passed, 3 skipped** (`test_backward_compatibility` 13/1, `test_extract_report_data` 13/0, `test_maestro_coverage_invariant` 9/2). Artifacts in `specs/098-maestro-7-layer/test-results/wave-04/results.json`.
- 15 pre-existing failures persist branch-wide (out of scope, documented).

## Resume prompt
```
claude "Resume Feature 098 (MAESTRO 7-layer) on branch 098-maestro-7-layer. Waves 0–4 done (T001–T012), Issue #98 close-gate (US-1+US-2) MET. Read specs/098-maestro-7-layer/NEXT-SESSION.md and run /aod.build 098 to continue from Wave 5/T013 (polish, gates, PR) through to final completion."
```
