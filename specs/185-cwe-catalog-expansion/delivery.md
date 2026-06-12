# Delivery Document: Feature 185 — CWE Catalog Expansion (T029 Drift-Edge Restoration, F-A1.2)

**Delivery Date**: 2026-06-12
**Branch**: `185-cwe-catalog-expansion`
**PR**: #328

---

## What Was Delivered

- **US1 — The catalog gains the 40 missing CWE records**: `schemas/taxonomy/cwe.yaml` grew **53 → 93 records**. All 40 T029 drift-edge target CWEs were dispositioned **add** (40/40, 0 reject/defer, published on Issue #185), names harvested byte-exact from MITRE `cwec_v4.20.xml`. The AI-domain CWEs **CWE-1427** (prompt injection), **CWE-1426** (GenAI output validation), and **CWE-1039** (adversarial input) are now resolvable with canonical MITRE names + URLs.
- **US2 — The 67 CWE-blocked edges return**: `schemas/taxonomy/crosswalk.yaml` grew **578 → 645 edges** (**608 primary** / 37 related / 0 superseded) by restoring the 67 published-mapping edges (65 `owasp→cwe` across all 6 OWASP families + 2 `mitre-attack→cwe`) byte-exact from F-180's dangling `e58f247` blob — preserving original `edge_type`/`confidence`/`citation` (including the crosswalk's first `confidence: low` edge, `T1070.006 → CWE-1269`). This **closes PRD #186's 2-edge deferral**.
- **US3 — Integrity, report baselines, and the decision trail stay intact**: the taxonomy integrity suite stayed 5/5 green at every commit; the 6 example security-report PDF baselines were intentionally regenerated (ADR-037 D-9 lane, `SOURCE_DATE_EPOCH=1700000000`) with deltas confined to Coverage-Attestation pages; the full decision trail closed (CHANGELOG `feat(185)`, `cwe.yaml` provenance header, `crosswalk.yaml` lineage block, `schemas/taxonomy/README.md` §3.5, ADR-037 D-7 annotation, and `specs/180-*/NEXT-SESSION.md` T029 residual marked resolved).
- **No schema / ADR / enum change**: ADR-027 record/edge shapes unchanged (`cwe.yaml` records stay 4-field `{id, full_id, name, url}`, no `cwe_refs`); ADR-037 D-7 received an annotation only.

---

## How to See & Test

1. **Taxonomy integrity** (5/5): `/usr/bin/python3 -m pytest tests/schemas/test_taxonomy_integrity.py -q` → all 5 functions pass (load/shape/URL, lexicographic sort, referential integrity, no-dupes + ≥500-primary floor, citation shape).
2. **Record count** (53 → 93): `grep -c '^- id:' schemas/taxonomy/cwe.yaml` → 93 records.
3. **Edge count** (578 → 645): inspect `schemas/taxonomy/crosswalk.yaml` — 645 total edges, 608 `primary`.
4. **Name fidelity** (0 mismatches): `/usr/bin/python3 specs/185-cwe-catalog-expansion/scripts/name_diff.py` against the pinned `cwec_v4.20` harvest → 0 mismatches across all 40.
5. **Byte-identity baselines** (red→green): `/usr/bin/python3 -m pytest tests/scripts/test_backward_compatibility.py -q` → green; per-page diffs confined to Coverage-Attestation pages.
6. **AI-CWE citability**: confirm `CWE-1427`, `CWE-1426`, `CWE-1039` resolve in `cwe.yaml`, each with the MITRE-published name and `https://cwe.mitre.org/data/definitions/<N>.html` URL.
7. **Restored deferral edges**: confirm `T1070.006 → CWE-1269` (`confidence: low`, preserved as-is) and `T1562 → CWE-693` are present in `crosswalk.yaml`.
8. **Disposition trail**: Issue #185 carries 40/40 add/reject/defer lines (all `add`), verified at T019.

---

## Delivery Metrics

| Metric | Value |
|--------|-------|
| Estimated Duration | O/R/P 0.75 / 1.0 / 1.5 days (realistic ~1 day; revised up from 0.5/0.75/1.0 at tasks stage once consequence-scope was understood) |
| Actual Duration | ~1 day (branch 2026-06-11 → delivered 2026-06-12) |
| Variance | **On-target** (actual ~1d ≈ realistic 1d) |

---

## Surprise Log

What looked like a pure-data change (`cwe.yaml` 53→93, `crosswalk.yaml` 578→645) carried two late-discovered render/test couplings — CA-page PDF baseline regeneration and a coverage-percentage test pin — because `cwe` ∈ `ORDERED_FRAMEWORKS` (`scripts/extract-report-data.py`). Compounding it, sibling feature **F-186 had left the byte-identity baseline suite silently RED on `main`** (inherited `mitre-atlas` 30→36 drift with no regen), surfaced only at F-185 plan review because that suite is local-only and never wired into CI. The catalog edit was mechanical; the depth of the consequence-scope was the surprise.

---

## Lessons Learned

| Category | Lesson | KB Entry |
|----------|--------|----------|
| Process | A consequence-coupled data feature delivers clean only when the couplings (baseline regen + test-pin sweep) are surfaced as first-class scope and the literal pre-state is recorded at T001 — the catalog edit itself is the easy part. Membership in `ORDERED_FRAMEWORKS` is the single predicate separating "data-only" growth (F-184 `nist-ai-600-1`) from "ships-with-a-regen-lane" growth (F-185 `cwe`, F-186 `mitre-atlas`). | Entry 16 (delivery) + Entry 15 (build-stage mechanics) in INSTITUTIONAL_KNOWLEDGE.md |

---

## Feedback Loop

**New Ideas**: 1

- Evaluate wiring the byte-identity baseline suite into CI (or a lighter catalog-count drift guard) to prevent silent red-main after `ORDERED_FRAMEWORKS` catalog growth — Issue #329 (type:retro)

---

## Source Artifacts

| Artifact | Path |
|----------|------|
| Specification | specs/185-cwe-catalog-expansion/spec.md |
| Implementation Plan | specs/185-cwe-catalog-expansion/plan.md |
| Task Breakdown | specs/185-cwe-catalog-expansion/tasks.md |
| PRD | docs/product/02_PRD/185-cwe-catalog-expansion-2026-06-11.md (v1.2) |
| Restore-set artifact | specs/185-cwe-catalog-expansion/restored-edges.yaml |
| Baseline-regen contract | specs/185-cwe-catalog-expansion/contracts/baseline-regen.contract.md |

---

## Test Evidence

### Test Scenarios (Living Documentation)

| AC ID | Given/When/Then | Scenario(s) | Status |
|-------|-----------------|-------------|--------|
| — | Data-layer feature (YAML taxonomy + regenerated PDF baselines); no UI/E2E surface. Acceptance verified by pytest suites, not Gherkin scenarios. | `tests/schemas/test_taxonomy_integrity.py`, `tests/scripts/test_backward_compatibility.py`, `specs/185-*/scripts/name_diff.py` | Covered (pytest) |

_No Gherkin scenarios declared — the `knowledge-system` stack pack has no E2E contract; the taxonomy integrity + byte-identity pytest suites are the acceptance oracle._

### Execution Evidence

#### E2E Validation Gate

| Field | Value |
|-------|-------|
| Status | skipped |
| Gate Mode | n/a (no E2E contract) |
| Gate Result | skip |
| Tests Passed | N/A |
| Tests Failed | N/A |
| Tests Skipped | N/A |
| Duration | N/A |

**Failure Details**: N/A — the active `knowledge-system` stack pack declares no E2E/Playwright contract (`stacks/knowledge-system/STACK.md`); skill Step 9a resolves to a non-fatal skip for this markdown/YAML data feature. Verification ran via the build-wave pytest suites below.

#### Build-Wave Test Results

| Wave | Tests | Passed | Failed | Status |
|------|-------|--------|--------|--------|
| wave-0 | 922 | 893 | 25 | warn |
| wave-1 | 922 | 891 | 27 | warn |
| wave-2 | 922 | 899 | 19 | pass |

**Build Summary**: **PASS** — final gate (wave-2, independent tester verification): 899/922 passed, **19/19 failures documented pre-existing** (out-of-scope on `main` at branch point), **0 in-scope failures, 0 regressions**. The 6 `test_backward_compatibility.py` byte-identity tests were intentionally flipped red→green by the F-185 D-9 baseline regen (T014/T015); the `test_coverage_attestation.py::test_coverage_percentage_arithmetic` pin was refreshed (1.89%=1/53 → 1.08%=1/93, architect-approved) and re-verified green. wave-1's 2 flagged regressions were both dispositioned (1 data-coupled pin refresh → green at wave-2; 1 confirmed suite-order flake). Coverage trend not captured (disproportionate for a data-only feature).

#### Artifacts

| Artifact | Path | Summary |
|----------|------|---------|
| Build summary | specs/185-cwe-catalog-expansion/test-results/summary.json | 3 waves, final gate PASS |
| Per-wave results | specs/185-cwe-catalog-expansion/test-results/wave-{00,01,02}/results.json | per-wave pass/fail + classification |
| Pre-state baseline | specs/185-cwe-catalog-expansion/test-results/pre-state.md | literal pre-change pytest totals (red→green anchor) |
| Name-diff | specs/185-cwe-catalog-expansion/test-results/name-diff.md | 0 mismatches vs cwec v4.20 |
| Baseline diff | specs/185-cwe-catalog-expansion/test-results/baseline-diff.md | CA-page-only PDF deltas |
| Final gate | specs/185-cwe-catalog-expansion/test-results/final-gate.md | T020 independent gate evidence |

**Archived Artifact Metrics**:
- Tests Run: 922 (full suite, wave-2)
- Passed: 899
- Failed: 19 (all documented pre-existing / out-of-scope; 0 in-scope, 0 regressions)
- Coverage: N/A (not captured — data-only feature)

**Notes**: Unit/integration via pytest (`/usr/bin/python3 -m pytest`). Taxonomy integrity 5/5; byte-identity backward-compat green after intentional D-9 regen. No Playwright E2E (data feature; no UI surface).

---

## Documentation Updates

| Domain | Agent | Files Updated | Status |
|--------|-------|---------------|--------|
| Product | product-manager | 3 (PRD INDEX.md, 05_User_Stories/README.md, 06_OKRs/README.md) | complete |
| Architecture | architect | 1 (00_Tech_Stack/README.md — F-185 lineage stamp + F-241 forward-pointer resolved) | complete |
| DevOps | devops | 0 (no changes needed — data-only feature, no env/CI/infra change; verified, matches #184/#186 precedent) | complete |

---

## Cleanup

- [x] Feature branch deleted (squash-merge `--delete-branch`)
- [x] All tasks complete (20/20)
- [x] No TBD/TODO in docs
- [x] Committed and pushed (PR #328 squash-merged `2aa1bf5`; closure docs committed to main)
- [x] GitHub Issue closed (`stage:done`)

**Feature 185 is now officially CLOSED.**
