# Delivery Document: Feature 311 — MAESTRO Matrix Model B (Clean vs. N/A)

**Delivery Date**: 2026-06-04
**Branch**: `311-maestro-matrix-model-b-clean-vs-na`
**PR**: #318

---

## What Was Delivered

- A zero-finding MAESTRO layer is now **unambiguous on every surface**: a reader can tell *analyzed-and-clean* (≥1 component maps, 0 findings) from *not-applicable* (no component maps, never in scope) on the `threats.md` matrix, the PDF "MAESTRO Layer Analysis" page, and the `maestro-stack` infographic — closing the ambiguity F-098 Model A left open (Issue #98 SC-006). *(US-1, P1)*
- The distinction is **machine-discernible**: a code-computed `coverage_state` enum (`findings | clean | not_applicable`) rides the infographic IR and the PDF group records, so a downstream tool no longer has to guess applicability — with **zero SARIF/schema change** (the emitted SARIF is byte-unchanged). *(US-2, P1)*
- Cross-surface consistency is **structural, not aspirational**: the orchestrator authors the state once into the Section-6 *Highest Severity* cell and both Python extractors inherit it; a new CI gate proves all three surfaces agree on every layer and fails naming the divergent layer + surface. *(US-3, P2)*
- A pure, Section-1-blind classifier `classify_maestro_coverage_state(finding_count, highest_severity)` in `scripts/tachi_parsers.py` is the single shared authority (ADR-047 D1/D2); the `maestro-heatmap.json` payload stays byte-unchanged behind the D3 fence.
- Five gated example baselines with genuine n/a layers (`microservices`, `web-app`, `free-text-microservice`, `mermaid-agentic-app`, `ascii-web-api`) were deterministically regenerated and re-frozen; all 6 byte-gated PDF baselines remain byte-identical and `BASELINE_EXAMPLES` is unchanged.
- **Delivery-time CI correction**: the `tachi-maestro-coverage.yml` job now installs `pyyaml` (its pytest invocation collects through `tests/scripts/conftest.py`, which imports yaml). This closed a latent gap from F-315 — the workflow had never actually executed until F-311's PR triggered it.

---

## How to See & Test

1. **Run the threat model on the fixture**: `/tachi.threat-model examples/microservices` (L2/L4 finding-bearing; L7 mapped-but-clean; L1/L3/L5/L6 unmapped). Open the generated `threats.md` and confirm the §6 "Risk by MAESTRO Layer" table shows L7 as `Analyzed — no findings this scan` (clean) and L1/L3/L5/L6 as `Not applicable — no components map to this layer` (n/a).
2. **PDF surface**: generate the PDF report (`/tachi.security-report`) and confirm the "MAESTRO Layer Analysis" page renders the n/a layers as `Not applicable — no components map to this layer. (out of scope)` with a muted treatment, visually distinct from the clean layer.
3. **Infographic surface**: inspect the generated `maestro-stack.json` and confirm each layer carries an explicit `coverage_state` (`findings | clean | not_applicable`) and that the rendered band shows an "N/A" label distinct from the clean dash.
4. **Cross-surface consistency gate**: `python3 -m pytest tests/scripts/test_maestro_cross_surface_consistency.py -v` — confirm both `test_microservices_three_surfaces_agree` (7/7 layers agree) and `test_forced_l7_divergence_is_caught` (negative test names L7 + the pdf surface) pass.
5. **7-layer + cross-surface CI**: confirm the `tachi maestro coverage` workflow is green on `main` (it runs both `test_maestro_coverage_invariant.py` and the cross-surface test, with `pyyaml` installed).
6. **No schema drift (SC-003)**: confirm the run's SARIF is byte-unchanged vs a Model-A baseline and `/aod.analyze` reports 0 blocking inconsistencies.

---

## Delivery Metrics

| Metric | Value |
|--------|-------|
| Estimated Duration | 1-2 days |
| Actual Duration | ~1 day (2026-06-03 19:10 → 2026-06-04) |
| Variance | On-target — single Plan→Build→Deliver cycle as Team-Lead scoped (S-sized) |

---

## Surprise Log

Smooth sailing — everything went roughly as planned; no major surprises. (The build's documented Decision-F baseline churn resolved within the session as designed, and the delivery-time `pyyaml` CI correction was a minor one-line fix.)

---

## Lessons Learned

| Category | Lesson | KB Entry |
|----------|--------|----------|
| — | None captured — routine delivery (no lesson recorded at retrospective). | N/A |

---

## Feedback Loop

**New Ideas**: None

---

## Source Artifacts

| Artifact | Path |
|----------|------|
| Specification | specs/311-maestro-matrix-model-b-clean-vs-na/spec.md |
| Implementation Plan | specs/311-maestro-matrix-model-b-clean-vs-na/plan.md |
| Task Breakdown | specs/311-maestro-matrix-model-b-clean-vs-na/tasks.md |
| PRD | docs/product/02_PRD/311-maestro-matrix-model-b-clean-vs-na-2026-06-03.md |
| ADR | docs/architecture/02_ADRs/ADR-047-maestro-coverage-state-authority.md |

---

## Test Evidence

### Test Scenarios (Living Documentation)

#### Acceptance Criteria Coverage

| AC ID | Given/When/Then | Scenario(s) | Status |
|-------|-----------------|-------------|--------|
| — | (Knowledge-system pack declares no E2E/Gherkin runner — verification is the build-wave pytest + byte-gate + cross-surface CI suite, see Execution Evidence) | — | — |

The `knowledge-system` stack pack defines no Playwright/E2E contract, so the Step-9 E2E gate short-circuits (status `skipped`). The feature's acceptance scenarios are validated by the deterministic pytest suite below, not by browser-driven E2E.

### Execution Evidence

#### E2E Validation Gate

| Field | Value |
|-------|-------|
| Status | skipped |
| Gate Mode | n/a (knowledge-system pack — no E2E runner) |
| Gate Result | skip |
| Tests Passed | N/A |
| Tests Failed | N/A |
| Tests Skipped | N/A |
| Duration | N/A |

**Failure Details**: N/A — E2E gate skipped (pack declares no E2E command).

#### Command

```bash
/aod.deliver FEATURE: 311 - MAESTRO Matrix Model B (clean vs n/a)
```

#### Build-Wave Test Results

| Wave | Phase | Tests | Passed | Failed | Status |
|------|-------|-------|--------|--------|--------|
| wave-1 | A — source contract (T003–T008) | 909 | 888 | 17* | pass |
| wave-2 | B — PDF ∥ infographic (T009–T014) | 71 | 69 | 0 | pass |
| wave-3 | C — cross-surface + CI gate (T015–T016) | 73 | 71 | 0 | pass |
| wave-4 | D — baseline regen + delivery (T017–T023) | 79 | 77 | 0 | pass |

**Build Summary**: 4/4 waves tested PASS (G1–G4), **0 regressions** across all waves. Final posture: F-311 unit area **71 passed + 2 skipped** (the 2 skips are intermediate-format sample reports with no MAESTRO table) AND byte-gate **6/6 green** = 77 distinct green checks. SC-003: 0 SARIF + 0 schema drift; `/aod.analyze` 0 blocking.

\* The 17 wave-1 failures are **pre-existing and out of F-311 scope** (`test_mobile_top_10_coverage_bundle_enrichment.py` + `test_tool_abuse_enrichment.py`) — confirmed identical on a clean-baseline worktree at HEAD with zero F-311 code. F-311 touched none of those files; its only shared change (`scripts/tachi_parsers.py`) is a purely-additive pure function. Per-wave totals are growing snapshots of the F-311 area, re-run each wave (not additive deltas).

**Archived Artifacts**:

| Artifact | Path | Summary |
|----------|------|---------|
| Build summary | test-results/summary.json | 5 waves, 4 tested + 1 baseline; 0 regressions |
| Per-wave results | test-results/wave-0{1..4}/results.json | Phase A–D gate decisions (all pass) |
| Wave-0 baseline | test-results/wave-00-baseline.md | Pre-change pytest reference |

**Notes**: Verification is stdlib pytest (markdown/PDF/infographic rendering + cross-surface consistency) plus deterministic byte-gated PDF baselines under `SOURCE_DATE_EPOCH=1700000000`. No browser/E2E artifacts apply to this feature.

---

## Documentation Updates

| Domain | Agent | Files Updated | Status |
|--------|-------|---------------|--------|
| Product | product-manager | 2 | APPROVED |
| Architecture | architect | 3 | APPROVED |
| DevOps | devops | 1 | pass |

Product: PRD INDEX.md (311 → Delivered), 311 PRD frontmatter. Architecture: architecture/README.md (ADR-047 index row), 03_patterns/README.md (author-once-inherit pattern), 00_Tech_Stack/README.md (CI-gate note). DevOps: CI_CD_GUIDE.md (MAESTRO coverage workflow — two invariants + pyyaml install).

---

## Cleanup

- [x] Feature branch deleted (local + remote, via squash-merge `--delete-branch`)
- [x] All tasks complete (23/23)
- [ ] No TBD/TODO in docs
- [x] Committed and pushed (PR #318 squash-merged to main as `0e5ee1c`)
- [ ] GitHub Issue closed (`stage:done`)

**Feature 311 is now officially CLOSED.**
