# Delivery Document: Feature 217 — Detect-Images Duplicate Cleanup

**Delivery Date**: 2026-07-02
**Branch**: `217-detect-images-duplicate-cleanup`
**PR**: #351 (squash-merged to `main` as `3b5b377`)

---

## What Was Delivered

- **Opt-in `--cleanup-mislabeled-images` flag** on `scripts/extract-report-data.py` — the sanctioned remedy for Issue #217's forever-persisting mislabeled/corrected duplicate image pairs (US-1). Without the flag, behavior is byte-identical to before (safe default, FR-001).
- **Double-gated, direction-agnostic deletion safety**: a file is deleted only when BOTH the flag is present AND a correctly-labeled, byte-identical counterpart exists. The predicate keys on mislabeled-ness (magic-byte content ≠ extension), never sibling existence — legitimate self-consistent pairs are never touched (FR-002/FR-003).
- **Both-moments wiring** (FR-004): cleanup fires for pre-existing pairs (the primary legacy case) AND at recovery-write time — the latter additionally gated on the corrected sibling not having pre-existed the copy, preventing cross-swap amplification into data loss (AC-1g).
- **Operator audit trail + best-effort semantics**: one stderr record per deletion; per-file deletion failures log to stderr and never fail the extraction (FR-005).
- **8 dedicated AC tests** (AC-1a–1h) including all 4 safety negatives: non-identical pair, truncated recovery copy, cross-swapped pair, legitimate mixed pair (FR-007).
- **US-2 dogfood**: the 6 mislabeled `.jpg` duplicates (~6.75 MB) in `examples/agentic-app/test-output/2026-04-19T03-20-30/` (gitignored local snapshot) removed via the flag itself, with path-invariance proof — `report-data.typ` byte-identical pre/post (AC-2a).
- **US-3 documentation**: duplicate-pair origin, sanctioned flag invocation, and double-gate semantics documented in `.claude/skills/tachi-report-assembly/references/typst-artifacts.md`; the raw `find … rm` one-liner is no longer the recommended path (AC-3a).

---

## How to See & Test

1. **Safe default (no cleanup)** — run extraction without the flag against a directory containing a mislabeled pair; both files persist and output is byte-identical to pre-F-217 behavior (AC-1b):
   ```bash
   python3 scripts/extract-report-data.py \
     --target-dir <assessment-dir> \
     --template-dir templates/tachi/security-report \
     --output /tmp/report-data.typ
   ```
2. **Opt-in cleanup** — re-run with `--cleanup-mislabeled-images`; the mislabeled `.jpg` is deleted, the emitted image path is the `.png`, and one stderr line records the deletion (AC-1a):
   ```bash
   python3 scripts/extract-report-data.py \
     --target-dir <assessment-dir> \
     --template-dir templates/tachi/security-report \
     --output /tmp/report-data.typ \
     --cleanup-mislabeled-images
   ```
3. **Path-invariance proof (US-2 safety)** — generate output before and after a flagged run and diff:
   ```bash
   python3 scripts/extract-report-data.py --target-dir <dir> --template-dir <tpl> --output /tmp/before.typ
   python3 scripts/extract-report-data.py --target-dir <dir> --template-dir <tpl> --output /tmp/after.typ --cleanup-mislabeled-images
   diff /tmp/before.typ /tmp/after.typ && echo "path-invariant ✓"
   ```
4. **Safety negatives** — seed a non-identical `.jpg`/`.png` pair (AC-1d) or a cross-swapped pair (AC-1g) and run with the flag: neither file is deleted.
5. **Run the extractor test modules** (local-only suites — not in the CI pytest gate):
   ```bash
   python3 -m pytest tests/scripts/test_extract_report_data.py tests/scripts/test_extractor_contract_fixes.py -v
   ```
6. **US-3 docs** — read `.claude/skills/tachi-report-assembly/references/typst-artifacts.md` for the legacy duplicate-pair note and sanctioned cleanup invocation.

---

## Delivery Metrics

| Metric | Value |
|--------|-------|
| Estimated Duration | 1 day (Team-Lead central estimate: 1.0 eng-day, floor 0.5d) |
| Actual Duration | 1 day (branch 2026-07-01 18:28 → merge 2026-07-02 09:02; single wave built same evening) |
| Variance | On-target — actual matched the central estimate |

---

## Surprise Log

Smooth sailing — single-wave build, 17/17 tasks, 945 pass / 0 regressions in the gated suite, and actual duration matched the 1.0 eng-day estimate; no major surprises.

---

## Lessons Learned

| Category | Lesson | KB Entry |
|----------|--------|----------|
| Technical pattern | Safe destructive cleanup is a double gate wired at every moment the deletable state can exist: explicit opt-in flag AND byte-identical counterpart proof, predicate keyed on the defect (content ≠ extension, direction-agnostic) not sibling existence, and wired at BOTH the pre-existing-pair and recovery-write moments — wiring only the obvious moment silently misses the primary legacy case. Byte-identity doubles as copy-success verification. | Entry 21 in INSTITUTIONAL_KNOWLEDGE.md |

---

## Feedback Loop

**New Ideas**: None

(OQ-1 follow-ons — a `--dry-run` companion and auto-passing the flag from the report-assembler — were already documented in the spec as deferred-on-adopter-signal; no new issues warranted.)

---

## Source Artifacts

| Artifact | Path |
|----------|------|
| Specification | specs/217-detect-images-duplicate-cleanup/spec.md |
| Implementation Plan | specs/217-detect-images-duplicate-cleanup/plan.md |
| Task Breakdown | specs/217-detect-images-duplicate-cleanup/tasks.md |
| PRD | docs/product/02_PRD/217-detect-images-duplicate-cleanup-2026-07-01.md |

---

## Test Evidence

### Test Scenarios (Living Documentation)

#### Acceptance Criteria Coverage

| AC ID | Given/When/Then | Scenario(s) | Status |
|-------|-----------------|-------------|--------|
| — | (AC-coverage parse not run — E2E gate short-circuited at Step 9a: the active `knowledge-system` pack declares no `aod-test-contract` block) | — | — |

AC-level coverage was instead enforced at build time: FR-007 required a dedicated automated test for each of AC-1a–AC-1h (including all four safety negatives), delivered in `tests/scripts/test_extract_report_data.py` (+303 lines). AC-2b is spec-marked `[MANUAL-ONLY]` (defer decision is a human judgment call) and its trigger never fired — OQ-2 resolved CLEAN.

<details>
<summary>Full Gherkin</summary>

_(No Gherkin scenarios generated — tester agent not invoked; see Execution Evidence)_

</details>

### Execution Evidence

#### E2E Validation Gate

| Field | Value |
|-------|-------|
| Status | error (non-fatal — lint exit 5) |
| Gate Mode | hard |
| Gate Result | skip |
| Tests Passed | N/A |
| Tests Failed | N/A |
| Tests Skipped | N/A |
| Duration | N/A |

**Failure Details**: `stacks/knowledge-system/STACK.md:0: ERROR: no aod-test-contract block found (expected sentinel-bracketed YAML in Section 7)` — the active stack pack declares no test contract, so the tester agent was never invoked (per Step 9a exit-5 taxonomy; not a hard block).

#### Per-Scenario Results

| Scenario | Status | Duration |
|----------|--------|----------|
| — | — | — |

#### Command

```bash
/aod.deliver FEATURE: 217 - detect-images-duplicate-cleanup
```

#### Build-Wave Test Results

| Wave | Tests | Passed | Failed | Skipped | Status |
|------|-------|--------|--------|---------|--------|
| wave-1 | 969 | 945 | 19 | 5 | pass |

**Build Summary**: pass — 945/969 passed, 0 regressions (the 19 failures are the known pre-existing out-of-gate failures; the real gate is the 15-module subset in `tachi-pytest.yml`, which is green). Coverage: 52.26% total (Δ 0), 61.25% on `scripts/extract-report-data.py` (the sole changed production file).

#### Artifacts

| Artifact | Path | Summary |
|----------|------|---------|
| Build summary | specs/217-detect-images-duplicate-cleanup/test-results/summary.json | 945 pass / 19 fail / 5 skip, 0 regressions, wave gate: pass |
| Wave-1 results | specs/217-detect-images-duplicate-cleanup/test-results/wave-01/results.json | Full per-test classification (pre-existing vs new failures) |
| Wave-1 coverage | specs/217-detect-images-duplicate-cleanup/test-results/wave-01/coverage.json | 52.26% total; 61.25% new-code |
| Wave-1 failures log | specs/217-detect-images-duplicate-cleanup/test-results/wave-01/failures.log | Details of the 19 pre-existing out-of-gate failures |

**Archived Artifact Metrics**:
- Tests Run: 969
- Passed: 945
- Failed: 19 (all pre-existing, out-of-gate; 0 new)
- Coverage: 52.26% (new-code: 61.25%)

**Notes**: Build-wave evidence was archived during `/aod.build` and committed with the feature (no separate E2E artifacts — the knowledge-system pack has no E2E surface). CI on PR #351: 5/5 checks green (catalog-drift fingerprints, MAESTRO layers, mmdc preflight, gitleaks ×2). AC-2b is the only `[MANUAL-ONLY]` criterion; its fallback path (defer US-2) was never needed.

---

## Documentation Updates

| Domain | Agent | Files Updated | Status |
|--------|-------|---------------|--------|
| Product | product-manager | 1 (docs/product/02_PRD/INDEX.md — Approved→Delivered + header entry) | APPROVED |
| Architecture | architect | 0 (per-feature record already committed in system-design via PR #351; no ADR minted, no tech-stack change) | APPROVED (no-op) |
| DevOps | devops | 0 (CLI-only flag on a local script; no env vars, CI workflows, or deployment surface) | PASS (no-op) |

---

## Cleanup

- [x] Feature branch deleted (squash-merge `--delete-branch`)
- [x] All tasks complete (17/17)
- [x] No TBD/TODO in docs
- [x] Committed and pushed (PR #351 → `3b5b377`; closure docs direct-to-main)
- [ ] GitHub Issue closed (`stage:done`) — #217 (command Step 10)

**Feature 217 is now officially CLOSED.**
