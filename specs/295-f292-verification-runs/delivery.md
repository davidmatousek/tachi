# Delivery Document: Feature 295 — F-292 Post-Merge Verification Runs (T017 + T026)

**Delivery Date**: 2026-07-04
**Branch**: `295-f292-verification-runs`
**PR**: #353 (squash-merged to `main` as `e6e8ef0`; release-please → v4.47.0 via #358)

---

## What Was Delivered

- **SC-003 (F-292 T017) empirically verified — PASS**: the output-integrity no-emission invariant on `examples/agentic-app/` now rests on a committed, fail-closed verification record instead of an untested claim. Attempt 1 (single-agent primary path) returned NO_FINDINGS and was correctly treated as a gate ERROR by the false-pass guard; attempt 2 (scoped-full fallback) produced a valid 4-finding OI subset matching the pre-292 anchor (`0629fa2~1` → OI-1..OI-4) on all D-1 gate fields.
- **SC-015 (F-292 T026) gate executed honestly — FAIL, honest-stop**: the Cat 6 Vector/Search-DSL Injection threat WAS detected on `examples/multi-tenant-rag-app/`, but orchestrator Phase-3 compilation absorbed the OI findings into the LLM-N ID sequence, dropping the `OI-` prefix and CWE-943 citations. Disposition per spec (fix-vs-file): defect #356 filed with full evidence; **no baseline artifacts committed** — that lands only after #356 is fixed.
- **Corrected OI extraction filter is now the authoritative mechanism** (`partialFingerprints["findingId/v1"]` prefix match), superseding the defective contract §3 procedure — both contract defects filed as #354.
- **FR-014 enabler shipped**: `scripts/generate-threats-sarif.py` derives the SARIF source URI from its input path (replacing the hardcoded agentic-app constant), with 4 covering assertions and agentic-app regeneration verified byte-unchanged; `tachi-pytest.yml` gained the lock-step trigger path.
- **Fix-vs-file follow-up surface filed during build**: #354 (contract §3/§6 defects), #355 (agentic-app sample-report duplicate LLM-5/6/7 vs OI-1/2/3 IDs), #356 (Phase-3 compilation defect — owns the T026 baseline + deferred US-3 CI check), #357 (enhancement: parameterize `generate-risk-scores-sarif.py`).
- **BLP-06 Wave 3 complete**: #295 was the initiative's last open item (deferred tail: #325).

---

## How to See & Test

1. Read the PASS record: `specs/295-f292-verification-runs/sc-003-verification-record.md` — Verdict PASS, anchor pinning, corrected filter, two-attempt narrative, D-1 gate evaluation, drift attribution.
2. Read the FAIL record: `specs/295-f292-verification-runs/sc-015-verification-record.md` — Verdict FAIL, three independent zero-checks, detection-vs-compilation evidence, #356 disposition.
3. Re-run the anchor extraction (expect exactly 4: OI-1..OI-4):
   ```bash
   git show 0629fa2~1:examples/agentic-app/sample-report/threats.sarif \
     | jq '[.runs[0].results[] | select(.partialFingerprints["findingId/v1"] // "" | startswith("OI-"))] | length'
   ```
4. Diff the committed OI subsets: `specs/295-f292-verification-runs/test-results/anchor-oi-subset.json` vs `fresh-oi-subset.json` — identical on {count, findingId set, sink/flow identity}.
5. Run the FR-014 assertions (in the CI-gated suite): `pytest tests/scripts/test_affected_assets_wiring.py -k fr014` — 4 tests green.
6. Confirm honest-stop wiring: issue #356 carries the T026 gate-FAIL evidence; #295 closed on the committed record with T017 checked and T026 recorded as FAIL→#356.

---

## Delivery Metrics

| Metric | Value |
|--------|-------|
| Estimated Duration | 1-2 days (Team-Lead feasibility: 0.5/1.0/2.0 eng-days, central 1.0) |
| Actual Duration | 1 day (branch created 2026-07-03 10:34 → merged 2026-07-04) |
| Variance | On-target — actual matched the 1.0 eng-day central estimate |

---

## Surprise Log

Smooth sailing — no major surprises. The honest-FAIL disposition path (T026 gate FAIL → defect #356, close on the record) was designed-for in the spec, so executing it was the plan working, not a deviation.

---

## Lessons Learned

| Category | Lesson | KB Entry |
|----------|--------|----------|
| Technical pattern | Gate verification on the compiled artifact adopters consume, never on intermediate agent output: fail-closed gates surfaced two otherwise-invisible defect classes — dispatch-tier under-triggering (T017 attempt 1) and compilation-tier ID mangling (T026 → #356) — both of which agent-level evidence would have masked. | Entry 22 in INSTITUTIONAL_KNOWLEDGE.md |

---

## Feedback Loop

**New Ideas**: None at retrospective — the follow-up surface was fully filed during the build:

- Defect #354 — cross-link-no-emission-contract.md §3/§6 broken filter + non-executable invocation (type:defect, filed at build)
- Defect #355 — agentic-app sample-report duplicate legacy LLM-5/6/7 vs current OI-1/2/3 IDs (filed at build)
- Defect #356 — orchestrator Phase-3 compilation absorbs OI findings into LLM-N sequence (T026 gate FAIL owner; also owns US-2 baseline + deferred US-3 CI check)
- Enhancement #357 — parameterize `generate-risk-scores-sarif.py` for additional example baselines

---

## Source Artifacts

| Artifact | Path |
|----------|------|
| Specification | specs/295-f292-verification-runs/spec.md |
| Implementation Plan | specs/295-f292-verification-runs/plan.md |
| Task Breakdown | specs/295-f292-verification-runs/tasks.md |
| PRD | docs/product/02_PRD/295-f292-verification-runs-2026-07-02.md |
| Verification Records | specs/295-f292-verification-runs/sc-003-verification-record.md, sc-015-verification-record.md |

---

## Test Evidence

### Test Scenarios (Living Documentation)

#### Acceptance Criteria Coverage

| AC ID | Given/When/Then | Scenario(s) | Status |
|-------|-----------------|-------------|--------|
| — | (No AC-coverage map generated — E2E gate short-circuited at Step 9a before AC parsing; spec ACs for the live pipeline runs are `[MANUAL-ONLY]` by design) | — | — |

<details>
<summary>Full Gherkin</summary>

_(No scenarios declared — the E2E tester stage was not entered; see Execution Evidence.)_

</details>

### Execution Evidence

#### E2E Validation Gate

| Field | Value |
|-------|-------|
| Status | error |
| Gate Mode | hard |
| Gate Result | skip |
| Tests Passed | N/A |
| Tests Failed | N/A |
| Tests Skipped | N/A |
| Duration | N/A |

**Failure Details**: Stack-contract lint exit 5 — `stacks/knowledge-system/STACK.md` has no `aod-test-contract` block (no declared E2E runner for this pack). Non-fatal per ADR-006; gate bypassed deterministically.

#### Command

```bash
/aod.deliver FEATURE: 295 - f292-verification-runs
```

#### Build-Wave Test Results

| Wave | Tests | Passed | Failed | Status |
|------|-------|--------|--------|--------|
| wave-1 | 81 | 78 | 0 | pass |

**Build Summary**: pass — 78/81 passed (3 pre-existing skips, documented in pre-state.md; 0 regressions; sole delta vs baseline = +4 passing FR-014 assertions from commit `995359f`)

#### Artifacts

| Artifact | Path | Summary |
|----------|------|---------|
| Build summary | specs/295-f292-verification-runs/test-results/summary.json | 1 wave, gate pass, 78p/0f/3s, 0 regressions |
| Wave results | specs/295-f292-verification-runs/test-results/wave-01/results.json | D-E suite set (5 modules), soft gate pass |
| Pre/post state | specs/295-f292-verification-runs/test-results/pre-state.md, post-state.md | Literal baseline 74p/3s/0f → 78p/3s/0f, delta attributed |
| T017 evidence | specs/295-f292-verification-runs/test-results/{anchor,fresh}-oi-subset.json, t017-*.md/.yaml/.sarif | Anchor + fresh OI extractions, dispatch payload, fallback artifacts |
| T026 evidence | specs/295-f292-verification-runs/test-results/t026-attempt1-orphan-oi-return.md | Attempt-1 orphaned sub-agent return (corroborating counter-evidence for #356) |

**Archived Artifact Metrics**:
- Tests Run: 81
- Passed: 78
- Failed: 0
- Coverage: N/A (no pytest-cov configuration — capture skipped per opportunistic policy)

**Notes**: Test evidence was committed during the build (the feature's deliverable IS the verification evidence) — nothing new to archive at deliver time; `.aod/test-results/` contained only a stale empty directory from April. The spec's live-pipeline ACs (US-1 scenario 1, US-2 scenario 1) are marked `[MANUAL-ONLY] live LLM pipeline dispatch, session-initiated; not CI-repeatable` and were executed session-initiated during the build with their outputs committed under `test-results/`.

---

## Documentation Updates

| Domain | Agent | Files Updated | Status |
|--------|-------|---------------|--------|
| Product | product-manager | 4 (PRD INDEX, PRD 295, OKRs header, User-Stories header) | APPROVED |
| Architecture | architect | 1 (architecture/01_system_design/README.md) | APPROVED_WITH_CONCERNS (concerns = #356 debt, not doc blockers) |
| DevOps | devops | 2 (CI_CD_GUIDE.md, environment-variables.md) | pass |

---

## Cleanup

- [x] Feature branch deleted (local + remote, via squash-merge `--delete-branch`)
- [x] All tasks complete (16/16)
- [x] No TBD/TODO in docs (swept at close)
- [x] Committed and pushed (closure docs commit on `main`)
- [x] GitHub Issue closed (`stage:done`)

**Feature 295 is now officially CLOSED.**
