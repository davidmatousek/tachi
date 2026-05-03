# Delivery Document: Feature 180 — F-A1 Taxonomy Crosswalk Collection

**Delivery Date**: 2026-04-17
**Branch**: `180-taxonomy-crosswalk-collection`
**PR**: #181

---

## What Was Delivered

- **New `schemas/taxonomy/` directory** (9 files): 7 catalog YAMLs (`owasp.yaml`, `mitre-attack.yaml`, `mitre-atlas.yaml`, `nist-ai-rmf.yaml`, `cwe.yaml`, `tachi-control-category.yaml`, `tachi-stride-ai-category.yaml`) + `crosswalk.yaml` + `README.md` — the first machine-readable taxonomy reference in tachi.
- **526 primary cross-framework edges** in `crosswalk.yaml` (≥500 floor per PRD Success Metric 2) with the closed 5-field edge shape `{source:{taxonomy,id}, target:{taxonomy,id}, edge_type, confidence, citation}` and 7-value closed taxonomy enum.
- **NIST AI RMF 1.0 full Subcategory catalog**: 72 records (GOVERN 19 + MAP 18 + MEASURE 22 + MANAGE 13) — primary-source correction from the PRD-era 68.
- **CWE catalog enrichment**: 41-CWE seed + 12 net-new CWE Top 25 2025 entries (≥53 records total).
- **MITRE ATLAS October 2025 agent techniques**: 7-technique seed + 5 net-new agent techniques (AML.T0058–AML.T0062).
- **New ADR-027** (`docs/architecture/02_ADRs/ADR-027-taxonomy-crosswalk-schema.md`, Status: **Accepted** 2026-04-17) — records the record/edge schema, the 7-value taxonomy enum, 3-value edge_type enum, 3-value confidence enum, and the Interpretation C transcription rationale.
- **New integrity test suite** (`tests/schemas/test_taxonomy_integrity.py`): 4+1 tests enforcing FR-027 through FR-032 (record shape, enum closure, referential integrity, URL/path citation, parse perf).
- **3 follow-on Issues filed** pre-delivery: F-A1.1 (Surface C STRIDE+AI → GAI Risk, ~0.5–1d), F-A1.2 (related/superseded edges), F-A1.3 (citation link-rot monitoring).
- **Zero runtime touch**: no orchestrator change, no agent change, no pipeline regression — the directory is additive and consumed by future F-A2 / F-B downstream features.

---

## How to See & Test

1. **Resolve a taxonomy record in one line** (US-180-1 acceptance):
   ```python
   python3 -c "import yaml; r = next(x for x in yaml.safe_load(open('schemas/taxonomy/owasp.yaml')) if x['id'] == 'LLM05'); print(r['full_id'], r['name'], r['url'])"
   ```
   Expect OWASP LLM05 record with 5-field shape resolved from a single file.

2. **Count the NIST AI RMF 1.0 Subcategory catalog** (US-180-1 AS-4):
   ```bash
   python3 -c "import yaml; data = yaml.safe_load(open('schemas/taxonomy/nist-ai-rmf.yaml')); print(len(data))"
   ```
   Expect exactly `72`.

3. **Confirm crosswalk primary-edge floor** (US-180-2 AS-6):
   ```bash
   python3 -c "import yaml; e = yaml.safe_load(open('schemas/taxonomy/crosswalk.yaml')); print(sum(1 for x in e if x['edge_type'] == 'primary'))"
   ```
   Expect `≥500` (delivered `526`).

4. **Filter crosswalk edges from LLM05** (US-180-2 independent test):
   ```bash
   python3 -c "import yaml; e = yaml.safe_load(open('schemas/taxonomy/crosswalk.yaml')); print([x for x in e if x['source']['taxonomy'] == 'owasp' and x['source']['id'] == 'LLM05'])"
   ```
   Expect a non-empty list with target taxonomy IDs + citations.

5. **Run the full integrity test suite** (US-180-4):
   ```bash
   pytest tests/schemas/test_taxonomy_integrity.py -v
   ```
   Expect 4+1 tests green (record shape, enum closure, referential integrity, URL/path citation, parse perf ≤500ms).

6. **Open the curation README** (US-180-3 independent test):
   ```bash
   cat schemas/taxonomy/README.md
   ```
   Expect §Purpose, per-framework provenance (7 sections), confidence calibration rubric with anti-drift rule, canonical-URL conventions, 5-framework update procedures, and the "What F-A1 does NOT give you today" subsection.

7. **Verify ADR-027 Accepted** (US-180-5):
   ```bash
   grep -E "^(Status|Date):" docs/architecture/02_ADRs/ADR-027-taxonomy-crosswalk-schema.md
   ```
   Expect `Status: Accepted` with date `2026-04-17` and merge SHA filled in.

---

## Delivery Metrics

| Metric | Value |
|--------|-------|
| Estimated Duration | 1-2 days |
| Actual Duration | 1 day (same-day delivery session 2026-04-17) |
| Variance | On-target (well inside the original 5-day PRD Phase Breakdown estimate; same-day with wave-based parallelism) |

---

## Surprise Log

Smooth sailing — everything went roughly as planned, no major surprises. The two primary-source corrections (NIST 68→72, Surface C 41→27) were caught on-schedule via architect first-principles review and absorbed as in-place PRD amendments with scoped PM re-signoff; both were within the pre-authorized amendment path, not out-of-plan surprises.

---

## Lessons Learned

| Category | Lesson | KB Entry |
|----------|--------|----------|
| Process improvement | Primary-source-correction discipline protects spec integrity under time pressure: when mid-feature harvests diverge from PRD-era cited values, amend the PRD/spec in place with a scoped PM re-signoff (architect concurrence logged) rather than shipping stale values or deferring the feature — narrow the amendment to drift-only and record the authoritative source URL + fetch date in the signoff notes | KB-035 in INSTITUTIONAL_KNOWLEDGE.md |

---

## Feedback Loop

**New Ideas**: None

Three follow-on Issues were filed pre-delivery as part of T034 (out-of-scope work cleanly captured):
- F-A1.1 — Surface C STRIDE+AI → GAI Risk 8th enum value + 15 edges (~0.5–1d, schema-minor additive)
- F-A1.2 — `related` / `superseded` edges curation (out-of-scope for F-A1 per PRD)
- F-A1.3 — Citation link-rot monitoring (out-of-scope for F-A1 per PRD)

The retrospective did not surface additional net-new ideas beyond these.

---

## Source Artifacts

| Artifact | Path |
|----------|------|
| Specification | specs/180-taxonomy-crosswalk-collection/spec.md |
| Implementation Plan | specs/180-taxonomy-crosswalk-collection/plan.md |
| Task Breakdown | specs/180-taxonomy-crosswalk-collection/tasks.md |
| PRD | docs/product/02_PRD/180-taxonomy-crosswalk-collection-2026-04-17.md |
| ADR | docs/architecture/02_ADRs/ADR-027-taxonomy-crosswalk-schema.md |
| Integrity tests | tests/schemas/test_taxonomy_integrity.py |

---

## Documentation Updates

| Domain | Agent | Files Updated | Status |
|--------|-------|---------------|--------|
| Product | product-manager | 2 | APPROVED (docs/product/05_User_Stories/README.md, docs/product/06_OKRs/README.md; INDEX.md already showed Delivered) |
| Architecture | architect | 3 | APPROVED (docs/architecture/00_Tech_Stack/README.md, docs/architecture/01_system_design/README.md, CLAUDE.md) |
| DevOps | devops | 2 | APPROVED (docs/devops/01_Local/README.md, docs/devops/CI_CD_GUIDE.md; staging/production N/A) |

---

## Cleanup

- [ ] Feature branch deleted
- [x] All tasks complete (41/41)
- [ ] No TBD/TODO in docs
- [ ] Committed and pushed
- [ ] GitHub Issue closed (`stage:done`)

**Feature 180 is now officially CLOSED upon cleanup completion.**
