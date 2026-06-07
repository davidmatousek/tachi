# Delivery Document: Feature 182 — Crosswalk `related` + `superseded` Edge Expansion (First Tranche)

**Delivery Date**: 2026-06-07
**Branch**: `182-crosswalk-related-superseded-edges`
**PR**: #323 (squash-merged to main as `349e160`)
**Initiative**: BLP-05 Wave 3 (Crosswalk Integrity & Edges) · the #182 edges piece alongside #183 (citation link-rot)

---

## What Was Delivered

- The crosswalk is now **traversable, not just primary**: `crosswalk.yaml` carries **37 `related` edges** (22 `high` / 15 `medium`) connecting taxonomy items beyond their single best mapping, so a downstream pivot can expand a finding into its full cross-framework neighbourhood instead of stopping at one edge. *(US-1, P1 — MVP)*
- The `related` floor was set **honestly under the anti-drift rule**: the build-start yield survey (T002) found the achievable `high`/`medium` core was 37, not the ≥80 the PRD planned — so the **FR-002 yield-tripwire fired** and the architect (T003) authorized the **documented achievable floor of 37** rather than padding to 80 with `low`-confidence edges. All 37 are `high`/`medium`; **0** `high`/`medium` edges originate from the prose-only OWASP-LLM→CWE class (FR-004). *(US-1)*
- The `superseded` question was answered with an **honest empty set + recorded deferral**: the survey (T007) found **0** catalog-authorable deprecation/replacement pairs (the catalogs hold current editions only, so the *old* endpoint of every supersession is absent), and `deferred-superseded.md` dispositions **4 deferred classes** — each with a one-line rationale pointing to its post-catalog-expansion follow-on, never silently dropped. *(US-2, P2)*
- The edge-authoring methodology is now **drift-resistant and inheritable**: `schemas/taxonomy/README.md` gained a `related`/`superseded` calibration section with a worked example per audited source class, the **CWE View-ID rule** (parents are view-dependent), and an explicit **"OWASP-LLM→CWE is prose-only → `low`/inferred" caution**, so a future author can calibrate confidence from the README alone. *(US-3, P3)*
- **Zero migration surface**: no schema change, no integrity-test change, no new ADR, no change to ADR-027; the **≥500 primary floor is preserved** (primary count unchanged at 542). Final crosswalk: **542 primary / 37 related / 0 superseded = 579 edges**.

---

## How to See & Test

1. **Traverse `related` edges (US-1)**: in a Python 3.11 shell with `pyyaml`:
   ```python
   import yaml
   edges = yaml.safe_load(open('schemas/taxonomy/crosswalk.yaml'))
   related = [e for e in edges if e['edge_type'] == 'related']
   print(len(related))   # 37
   ```
   Confirm every endpoint resolves in its named catalog and every `high`/`medium` edge carries a supporting citation.
2. **Confirm the floor + provenance**: read the `# ─── F-182` provenance note at the top of `schemas/taxonomy/crosswalk.yaml` (mirrors the F-186 convention) — it records the tripwire outcome (floor = 37) and the per-class split (CWE↔CWE 22 · ATLAS→ATT&CK 7 · OWASP-LLM→ATLAS 8 · OWASP-Web→CWE 0).
3. **Superseded deferral (US-2)**: filter to `edge_type == 'superseded'` → empty set; confirm `specs/182-crosswalk-related-superseded-edges/deferred-superseded.md` records the 4 deferred classes with follow-ons.
4. **README rubric (US-3)**: open `schemas/taxonomy/README.md` §4.1 and confirm the `related`/`superseded` calibration section, the CWE View-ID rule, and the OWASP-LLM→CWE caution are present and self-sufficient.
5. **Integrity gate (SC-005)**: `python3 -m pytest tests/schemas/test_taxonomy_integrity.py -q` → `5 passed`; `primary` count unchanged at 542.
6. **No-migration diff guard (FR-011)**: `git show --stat 349e160` touches only `crosswalk.yaml`, `schemas/taxonomy/README.md`, `CHANGELOG.md`, the PRD, and `specs/182-*` — **0** changes to any catalog YAML, the integrity test, `schema_version`, or any ADR.

---

## Delivery Metrics

| Metric | Value |
|--------|-------|
| Estimated Duration | 1.5–2.5 days (PRD concern C1; Team-Lead ~2.0d for an ≥80 floor) |
| Actual Duration | ~same-day (2026-06-07 15:55 → 2026-06-07 ~22:38, single Plan→Build→Deliver session) |
| Variance | **Under estimate** — the FR-002 yield-tripwire capped `related` authoring at 37 (vs the ≥80 planned) and the `superseded` set was empty (audit + deferral only), roughly halving the heavy per-edge authoring task (T004). |

---

## Surprise Log

The ≥80 `related`-edge floor was unreachable: the yield-tripwire fired at **37** because F-180 had already authored *every* in-catalog CWE cross-reference as a `primary` edge (OWASP-Web→CWE yielded **0** beyond-primary edges), so only a thin residue of beyond-primary relationships remained to harvest. This is the spec-sanctioned outcome (FR-002 "anti-drift over floor-hitting"; Assumption A2), architect-authorized at T003 — not a failure.

---

## Lessons Learned

| Category | Lesson | KB Entry |
|----------|--------|----------|
| Process | A "floor" on a derived-edge feature is a survey-gated estimate of the achievable, not a guarantee — survey yield at PLAN time when a predecessor has already consumed the dense relationships; the anti-drift rule (commit the documented achievable floor, never `low`-pad) preserves quality over vanity metrics. | [Entry 14](../../docs/INSTITUTIONAL_KNOWLEDGE.md) |

---

## Feedback Loop

**New Ideas**: None new. The remaining work is already dispositioned — the 4 deferred `superseded` classes in `deferred-superseded.md` and the `related`-edge headroom both point to the existing BLP-05 Wave 2 catalog-expansion follow-ons (#184 / #185); the link-rot sibling is the already-open #183. No new backlog item is warranted (avoids duplicate issues).

---

## Source Artifacts

| Artifact | Path |
|----------|------|
| Specification | specs/182-crosswalk-related-superseded-edges/spec.md |
| Implementation Plan | specs/182-crosswalk-related-superseded-edges/plan.md |
| Task Breakdown | specs/182-crosswalk-related-superseded-edges/tasks.md |
| PRD | docs/product/02_PRD/182-crosswalk-related-superseded-edges-2026-06-07.md |
| Harvest / reference edges | specs/182-crosswalk-related-superseded-edges/reference-edges.yaml |
| Deferred superseded disposition | specs/182-crosswalk-related-superseded-edges/deferred-superseded.md |
| ADR | None — FR-011 explicitly forbids any ADR change (ADR-027 frozen; the `edge_type` enum already authorizes `related`/`superseded`). |

---

## Test Evidence

### Test Scenarios (Living Documentation)

#### Acceptance Criteria Coverage

| AC ID | Given/When/Then | Scenario(s) | Status |
|-------|-----------------|-------------|--------|
| — | (Knowledge-system pack declares no E2E/Gherkin runner — verification is the deterministic taxonomy integrity suite, see Execution Evidence) | — | — |

The `knowledge-system` stack pack defines no Playwright/E2E contract, so the Step-9 E2E gate short-circuits (status `skipped`). This is a **data/doc-only** feature (YAML + Markdown; no source-code extensions changed), so the feature's acceptance scenarios are validated by the 5-function `tests/schemas/test_taxonomy_integrity.py` suite (the structural acceptance oracle: dangling-endpoint, enum, 5-tuple-uniqueness, citation-shape, catalog-sort) plus the manual anti-drift citation audit (T005, FR-014) — not by browser-driven E2E.

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

**Failure Details**: N/A — E2E gate skipped (pack declares no E2E command).

#### Command

```bash
/aod.deliver 182
```

#### Build-Wave Test Results

| Wave | Phase | Tests | Passed | Failed | Status |
|------|-------|-------|--------|--------|--------|
| W0–W4 | Setup → Foundational → US1 → US2 → US3 → Polish | 0 | 0 | 0 | skip (no-code-change) |

**Build Summary**: Data/doc-only feature — no wave changed a source-code extension (`.py`/`.ts`/etc.), so the build's post-wave auto test-execution never triggered (all 5 waves = no-code-change skips, per `test-results/summary.json`). The **taxonomy integrity suite is the acceptance oracle** and passed **5/5** at the explicit task gates T006 (US1), T009 (US2), and T014 (final), and again on the delivery-time re-run (`5 passed in 1.03s`). `primary` count 542 preserved end-to-end; **0 regressions**. Coverage tooling N/A (no source code).

**Archived Artifacts**:

| Artifact | Path | Summary |
|----------|------|---------|
| Build summary | specs/182-crosswalk-related-superseded-edges/test-results/summary.json | 5 waves, 0 tested + 5 no-code-change skips; 0 regressions |
| Acceptance oracle | tests/schemas/test_taxonomy_integrity.py | 5/5 green at T006/T009/T014 + delivery-time re-run |

**Notes**: Verification is the deterministic stdlib pytest integrity suite over `schemas/taxonomy/`; no browser/E2E artifacts apply. The anti-drift citation audit (FR-014) is a manual content gate the shape-only suite cannot enforce — completed at T005 (0 un-downgraded violations).

---

## Documentation Updates

| Domain | Agent | Files Updated | Status |
|--------|-------|---------------|--------|
| Product | (direct) | 2 | done |
| Architecture | — | 0 | n/a — no new tech/dependency and no ADR (FR-011 forbids any ADR/schema change) |
| DevOps | — | 0 | n/a — no infrastructure, CI, or environment change |

Product: `docs/product/02_PRD/INDEX.md` (F-182 row → Delivered + PR #323 / spec links; header headline refreshed PRD-APPROVED → DELIVERED) and `docs/product/05_User_Stories/README.md` (user-story export). The doc surface was narrow and the Architecture/DevOps domains were structurally no-op (verified against the actual feature diff), so the updates were made directly rather than via parallel doc agents.

---

## Cleanup

- [x] Feature branch deleted (local + remote, via squash-merge `--delete-branch` + `git remote prune`)
- [x] All tasks complete (15/15 — T015 closed deliver-time by this run)
- [x] No blocking TBD/TODO in delivered docs (deferred items are explicitly dispositioned in `deferred-superseded.md`)
- [x] Committed and pushed (PR #323 squash-merged to main as `349e160`)
- [x] GitHub Issue #182 closed (`stage:done`)

**Feature 182 is now officially CLOSED.**
