# Delivery Document: Feature 184 — NIST AI 600-1 GAI Risk Taxonomy — Surface C Transcription

**Delivery Date**: 2026-06-11
**Branch**: `184-nist-ai-600-1-surface-c-transcription`
**PR**: #324 (squash-merged to main as `db1bba5`)

---

## What Was Delivered

- **8th catalog**: `schemas/taxonomy/nist-ai-600-1.yaml` — all 12 NIST AI 600-1 GAI Risk sections (§§2.1–2.12) in publication order, DOI-sourced, with YAML-quoted string ids (`"2.1"`…`"2.12"`) guarding against float-coercion.
- **Enum activation**: the frozen 7-value `taxonomy` enum expanded to 8 values (`nist-ai-600-1`), governed by the ADR-027 Decision 3 amendment instrument.
- **Surface C transcribed**: 15 verified Overlap rows added as `tachi-stride-ai-category → nist-ai-600-1` primary edges (`confidence: high`, citation-backed) — the transcription Feature 180 deferred.
- **Drift correction**: all 16 legacy wrong-direction `tachi-stride-ai-category → nist-ai-rmf` edges removed; the `tachi-control-category → nist-ai-rmf` class (31 edges) untouched. Edge composition now **541 primary / 37 related / 0 superseded = 578 total**.
- **Test surgery (M1×C4 inventory)**: `tests/schemas/test_taxonomy_integrity.py` gained `_sort_key_section` (`"2.10"` → `(2, 10)`) + an 8-catalog-aware branch; `_sort_key_nist` verified byte-untouched via AST extraction.
- **Governance trail on the record**: ADR-027 Revision History entry + Decision 3 annotation, taxonomy README §3.8 provenance (incl. Gap-row omission note), CHANGELOG entry, stale 7-value/7-catalog counts swept from live maintained docs.

---

## How to See & Test

1. **Catalog integrity**: Run `/usr/bin/python3 -m pytest tests/schemas/test_taxonomy_integrity.py -v` → 5/5 pass; `nist-ai-600-1.yaml` loads via `CATALOG_FILENAMES`, validates, and sort-checks in publication order (`"2.2"` before `"2.10"`).
2. **Catalog shape**: Parse `schemas/taxonomy/nist-ai-600-1.yaml` → exactly 12 records shaped `{id, full_id, name, url, cwe_refs: []}`, ids as quoted strings, `url` = `https://doi.org/10.6028/NIST.AI.600-1`.
3. **Surface C edges**: Filter `schemas/taxonomy/crosswalk.yaml` for `source.taxonomy == 'tachi-stride-ai-category' AND target.taxonomy == 'nist-ai-600-1'` → exactly the 15 FR-003 pairs, each `edge_type: primary`, `confidence: high`.
4. **Drift removal**: Filter for `source.taxonomy == 'tachi-stride-ai-category' AND target.taxonomy == 'nist-ai-rmf'` → empty; `tachi-control-category → nist-ai-rmf` still 31 edges.
5. **Counts**: 542→541 primary is intentional (+15 new, −16 removed); 37 related, 0 superseded, 578 total.
6. **Governance**: Read `docs/architecture/02_ADRs/ADR-027-taxonomy-crosswalk-schema.md` Revision History (F-184 entry) + Decision 3 annotation; `schemas/taxonomy/README.md` §3.8; CHANGELOG `feat(184)` entry.
7. **Sort-key isolation**: `git diff main~1 -- tests/schemas/test_taxonomy_integrity.py` shows `_sort_key_nist` untouched (quickstart §5 AST check recorded in `test-results/w1-gate.txt`).

---

## Delivery Metrics

| Metric | Value |
|--------|-------|
| Estimated Duration | 1-2 days |
| Actual Duration | 1 day (first F-184 commit 2026-06-10 19:14 → merged 2026-06-11) |
| Variance | On-target — landed at the bottom of the estimate band |

---

## Surprise Log

Smooth sailing — everything went as planned: 15/15 tasks, 0 regressions across all build waves, integrity suite 5/5 at every commit boundary, delivered in 1 day.

---

## Lessons Learned

| Category | Lesson | KB Entry |
|----------|--------|----------|
| None | No new lesson captured — clean transcription delivery; existing KB patterns (quoted-id YAML rule, stale-count forward-guard) applied as designed | N/A (user declined; no KB entry written) |

---

## Feedback Loop

**New Ideas**: None

Known follow-up already tracked pre-delivery: Issue #325 (`tachi-control-category → nist-ai-rmf` 4 non-table extras) — explicitly out of scope for F-184.

---

## Source Artifacts

| Artifact | Path |
|----------|------|
| Specification | specs/184-nist-ai-600-1-surface-c-transcription/spec.md |
| Implementation Plan | specs/184-nist-ai-600-1-surface-c-transcription/plan.md |
| Task Breakdown | specs/184-nist-ai-600-1-surface-c-transcription/tasks.md |
| PRD | docs/product/02_PRD/184-nist-ai-600-1-surface-c-transcription-2026-06-10.md |
| Contract | specs/184-nist-ai-600-1-surface-c-transcription/contracts/surface-c-transcription.contract.md |

---

## Test Evidence

### Test Scenarios (Living Documentation)

This subsection answers: *"What scenarios exist?"* This is a data/schema feature verified by the pytest integrity suite and wave-gate evidence, not Gherkin E2E scenarios — the E2E gate short-circuited at contract lint (see Execution Evidence).

#### Acceptance Criteria Coverage

| AC ID | Given/When/Then | Scenario(s) | Status |
|-------|-----------------|-------------|--------|
| — | (No Gherkin scenarios declared — gate errored at Step 9a before AC-coverage parse; spec ACs verified via integrity suite + wave gates below) | — | — |

<details>
<summary>Full Gherkin</summary>

_(No scenarios declared — E2E gate did not run for this feature)_

</details>

### Execution Evidence

This subsection answers: *"What happened when they ran?"*

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

**Failure Details**: Contract lint exit 5 — `stacks/knowledge-system/STACK.md` has no `aod-test-contract` block (Section 7 sentinel-bracketed YAML absent). Non-fatal per ADR-006; gate bypassed, evidence collection proceeded.

#### Per-Scenario Results

| Scenario | Status | Duration |
|----------|--------|----------|
| — | — | — |

#### Command

```bash
/aod.deliver FEATURE: 184 - nist-ai-600-1-surface-c-transcription
```

#### Build-Wave Test Results

| Wave | Tests | Passed | Failed | Status |
|------|-------|--------|--------|--------|
| wave-02 (W1 feature wave) | 7 | 6 | 1 | warn (pre-existing only) |
| wave-03 (W2 feature wave) | 7 | 6 | 1 | warn (pre-existing only) |

**Build Summary**: 12/14 passed, **0 regressions, 0 new failures** — both failures are the same single pre-existing test (`tests/scripts/test_init_sh_substitution.py::test_personalized_tree_bytes_match_baseline`), red on main since F-302/F-305, architect-accepted at P0 with re-scoped gate (mismatch set pinned at exactly 3 files, verified at W3 and T015). Waves W0/W3/W4/final-gate had no code-file changes (skip rule 5a) — their gates ran the integrity suite directly: **5/5 at every commit boundary**.

#### Artifacts

| Artifact | Path | Summary |
|----------|------|---------|
| Baseline pin | test-results/w0-baseline.txt | Suite 5/5 green; counts pinned 542/37/0=579, drift class = 16 |
| W1 gate | test-results/w1-gate.txt | Catalog lands: 8 catalogs, 12 records, AST check `_sort_key_nist` byte-identical |
| W2 gate | test-results/w2-gate.txt | Edges land: 541/37/0=578; 15 added, 16 removed; suite 5/5 |
| W3 fidelity | test-results/w3-fidelity.md | Row-by-row Surface C verbatim audit |
| W4 sweep | test-results/w4-sweep.txt | Stale-count sweep of live docs with named exemptions |
| Final gate | test-results/final-gate.txt | T015 full-suite evidence |
| Wave results | test-results/wave-02/results.json, wave-03/results.json | Per-wave runner output (gate_mode soft, decision warn) |
| Build summary | test-results/summary.json | Aggregate: 12 pass / 2 fail / 0 regressions across 6 waves |

**Archived Artifact Metrics**:
- Tests Run: 14 (across 2 tested waves; 4 waves doc-only, skip rule 5a)
- Passed: 12
- Failed: 2 (1 unique pre-existing, architect-accepted)
- Coverage: N/A (no coverage tooling configured)

**Notes**: Integrity suite (`tests/schemas/test_taxonomy_integrity.py`) via `/usr/bin/python3 -m pytest` (Team-Lead C5 interpreter pin) — 5/5 at every commit boundary. All artifacts were archived in-branch during the build and merged with PR #324.

---

## Documentation Updates

| Domain | Agent | Files Updated | Status |
|--------|-------|---------------|--------|
| Product | product-manager | 4 (PRD INDEX row+header, PRD 184 status, User_Stories header, OKRs header) | APPROVED |
| Architecture | architect | 2 (architecture/README.md, 00_Tech_Stack/README.md) | APPROVED |
| DevOps | devops | 0 (data-only schema change — zero DevOps surface, verified against `db1bba5`) | PASS (no changes needed) |

Agent detail files: `.aod/results/product-manager.md`, `.aod/results/architect.md`, `.aod/results/devops.md`.

---

## Cleanup

- [x] Feature branch deleted (local + remote, via `gh pr merge --squash --delete-branch`)
- [x] All tasks complete (15/15)
- [x] No blocking TBD/TODO in delivered docs
- [x] Committed and pushed (PR #324 squash-merged to main as `db1bba5`; docs-close commit follows)
- [x] GitHub Issue #184 closed (`stage:done`)

**Feature 184 is now officially CLOSED.**
