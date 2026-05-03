# Delivery Document: Feature 189 — F-A2 Source Attribution Schema Extension

**Delivery Date**: 2026-04-17
**Branch**: `189-source-attribution-schema-extension`
**PR**: #190 (squash-merged as commit `6d5d890c388af5f546246f4e39f8a4d61fe840b1`)

---

## What Was Delivered

- **`schemas/finding.yaml` schema bump 1.4 → 1.5** (minor, additive) under the ADR-026 Complex-Shape Addition Clarifier — extended by ADR-028 Decision 1 to cover list-of-RECORD fields under three additive-compatibility conditions (additive, has default, schema shape unchanged).
- **New optional `source_attribution` list-of-RECORD field** carrying machine-readable citations to external compliance frameworks. Per-record shape: `{taxonomy, id, relationship}` with closed 5-value `taxonomy` enum (`owasp`, `mitre-attack`, `mitre-atlas`, `nist-ai-rmf`, `cwe`) and closed 3-value `relationship` enum (`primary`, `related`, `derived`; default `primary`).
- **Parser round-trip** in `scripts/tachi_parsers.py` — new `_extract_source_attribution` helper reads the field with conditional-key emission per Feature 104 `delta_status` precedent (absent-vs-present-but-empty semantic preserved: absent → key omitted; present-but-empty → `[]` preserved).
- **Two-tier validation model**: (a) parser-tier V1/V2/V3/V5 enum + shape checks inline at parse time; (b) new `validate_source_attribution` V4 referential-integrity helper invokable from orchestrator Phase 4 that resolves every `{taxonomy, id}` pair against the F-A1 catalog YAMLs in `schemas/taxonomy/`. ValidationError dataclass is stdlib-only per Feature 128 runtime stdlib constraint.
- **New ADR-028** (`docs/architecture/02_ADRs/ADR-028-source-attribution-schema-extension.md`, Status: **Accepted** 2026-04-17) — records 7 numbered decisions: (1) ADR-026 extension to list-of-RECORD, (2) Q1-E conditional Section 9 serialization + Q1-B sidecar fallback, (3) 5-value taxonomy enum restricted to external frameworks, (4) 3-value relationship enum + default `primary`, (5) Q2-B two-tier validation with separate post-parse validator at orchestrator Phase 4, (6) 22-file zero-edit invariant on the detection tier per ADR-023 lineage, (7) Proposed → Accepted dual-commit governance mirroring ADR-027 / F-A1.
- **9 new pytest tests** in `tests/scripts/test_source_attribution.py` covering all 3 US acceptance criteria + FR-013 referential-integrity sweep; 7 new fixtures under `tests/scripts/fixtures/source_attribution/` (4 valid + 3 invalid).
- **Zero runtime dep changes**: empty diff on `pyproject.toml`, `requirements*.txt`, `package.json`. **22-file zero-edit invariant preserved** (ADR-023): empty diff on the 11 threat-detection agents + 11 skill-reference files.
- **SC-2 byte-identity preserved**: 6/6 baseline PDFs byte-identical under `SOURCE_DATE_EPOCH=1700000000` (5 non-agentic + `maestro-reference`). Final pytest: 284 passed, 1 skipped (pre-existing SC-003 narrowing).

---

## How to See & Test

1. **Verify schema version bump** (US-1 AS-1):
   ```bash
   grep "^schema_version:" schemas/finding.yaml
   ```
   Expect `schema_version: "1.5"`.

2. **Round-trip a multi-record citation** (US-1 AS-3):
   ```bash
   pytest tests/scripts/test_source_attribution.py::test_round_trip_multi_record -v
   ```
   Expect all three `{taxonomy, id, relationship}` records preserved in input order.

3. **Verify absent-vs-empty semantic distinction** (US-2 AS-1 / AS-2):
   ```bash
   pytest tests/scripts/test_source_attribution.py::test_absent_omits_key tests/scripts/test_source_attribution.py::test_empty_array_preserved -v
   ```
   Expect: absent → `source_attribution` key omitted entirely from parser output; present-but-empty → `source_attribution: []` preserved verbatim.

4. **Verify closed-enum rejection** (US-3 AS-1 / AS-2 / AS-3):
   ```bash
   pytest tests/scripts/test_source_attribution.py::test_invalid_taxonomy_rejected tests/scripts/test_source_attribution.py::test_invalid_relationship_rejected tests/scripts/test_source_attribution.py::test_relationship_defaults_to_primary -v
   ```
   Expect validation errors naming the bad value and the closed domain; missing `relationship` defaults to `primary`.

5. **Verify referential integrity against F-A1 catalogs** (US-3 AS-4 / FR-013):
   ```bash
   pytest tests/scripts/test_source_attribution.py::test_invalid_id_detected tests/scripts/test_source_attribution.py::test_fixtures_self_consistent -v
   ```
   Expect `{owasp, NOT-A-REAL-OWASP-ID}` to fail with an error citing the target YAML `schemas/taxonomy/owasp.yaml`; the self-consistency sweep verifies all valid fixtures resolve cleanly.

6. **Confirm backward-compatibility byte-identity** (US-2 AS-3 / SC-002):
   ```bash
   SOURCE_DATE_EPOCH=1700000000 pytest tests/scripts/test_backward_compatibility.py -v
   ```
   Expect 6/6 baselines byte-identical (5 non-agentic + `maestro-reference`).

7. **Verify ADR-028 Accepted with SHA filled** (SC-005):
   ```bash
   grep -E "^\*\*(Status|Accepted-commit-SHA)" docs/architecture/02_ADRs/ADR-028-source-attribution-schema-extension.md
   ```
   Expect `Status: Accepted` + `Accepted-commit-SHA: 6d5d890c388af5f546246f4e39f8a4d61fe840b1`.

8. **Run the full pytest suite**:
   ```bash
   SOURCE_DATE_EPOCH=1700000000 pytest tests/ --timeout=300
   ```
   Expect 284 passed, 1 skipped.

---

## Delivery Metrics

| Metric | Value |
|--------|-------|
| Estimated Duration | 2-3 days (2026-04-20 → 2026-04-22 per plan.md Technical Context) |
| Actual Duration | 1 day (same-day delivery session 2026-04-17) |
| Variance | Delivered ahead of estimate — full 6-wave build + 1 interim checkpoint (5.5) + T036 post-merge fill, all same-day after F-A1 / Feature 180 merged earlier the same day |

---

## Surprise Log

Smooth execution. F-A2 followed the F-A1 / ADR-027 governance pattern directly with zero structural divergence: single-day dual-commit (Proposed at Day 1 Wave 1.1 schema-lock; Accepted at Wave 6.1 pre-merge; post-merge SHA fill at T036). The Q1-E primary serialization surface was resolved cleanly at Wave 1.1 architect memo time; the Q1-B sidecar fallback path was pre-authorized but did not need to be exercised. Checkpoint 5.5 interim pytest gate (team-lead concern #4 discharge) added one test pass 279 → 280 without incident before the ADR status flip.

The only minor note: the conditional-key absent-vs-empty semantic preservation (FR-011 / US-2 AS-1+AS-2) required the Feature 104 `delta_status` precedent to be invoked explicitly in the parser helper — a reminder that contract surfaces need the distinction called out at fixture-authoring time (4 valid fixtures cover the 2 × 2 matrix of absent/single/multi/empty exhaustively).

---

## Lessons Learned

| Category | Lesson | KB Entry |
|----------|--------|----------|
| Governance precedent reuse | Dual-commit Proposed → Accepted ADR governance (ADR-027 / F-A1) is now a reusable pattern — F-A2 / ADR-028 reused it structurally identically (Decision 7 mirrors ADR-027 Decision 8), enabling same-day delivery for foundation-tier schema extensions. Future foundation features that ship a new ADR + schema bump should adopt this pattern by default. | KB-036 in `docs/INSTITUTIONAL_KNOWLEDGE.md` |

---

## Feedback Loop

**New Ideas**: None net-new. The BLP-01 Foundation-tier continuation is already captured in the existing backlog:

- **F-A3** — Populator wiring (8 threat agents emit `source_attribution` against F-A1 catalogs) — explicit downstream scope boundary per F-A2 PRD
- **F-B** — Coverage attestation report section using the F-A1 crosswalk + F-A2 per-finding citations

No new ideas surfaced during the retrospective. The F-A2 PRD's explicit scope boundaries (populators deferred to F-A3; coverage report deferred to F-B) are holding cleanly — no scope drift to capture as follow-on.

---

## Source Artifacts

| Artifact | Path |
|----------|------|
| Specification | specs/189-source-attribution-schema-extension/spec.md |
| Implementation Plan | specs/189-source-attribution-schema-extension/plan.md |
| Task Breakdown | specs/189-source-attribution-schema-extension/tasks.md |
| PRD | docs/product/02_PRD/189-source-attribution-schema-extension-2026-04-17.md |
| ADR | docs/architecture/02_ADRs/ADR-028-source-attribution-schema-extension.md |
| Schema contract | specs/189-source-attribution-schema-extension/contracts/finding-schema-1.5.yaml |
| Record contract | specs/189-source-attribution-schema-extension/contracts/source-attribution-record.yaml |
| New tests | tests/scripts/test_source_attribution.py |
| Parser changes | scripts/tachi_parsers.py (lines 621-977) |
| Schema change | schemas/finding.yaml (schema_version 1.5) |

---

## Documentation Updates

| Domain | Agent | Files Updated | Status |
|--------|-------|---------------|--------|
| Product | product-manager | 3 | APPROVED (docs/product/02_PRD/INDEX.md, docs/product/05_User_Stories/README.md, docs/product/06_OKRs/README.md) |
| Architecture | architect | 2 | APPROVED (docs/architecture/01_system_design/README.md, CLAUDE.md; 00_Tech_Stack/README.md already reflected F-A2 from build waves) |
| DevOps | devops | 1 | APPROVED (docs/devops/CI_CD_GUIDE.md) |

---

## Cleanup

- [x] Feature branch deleted (local + remote)
- [x] All tasks complete (36/36)
- [ ] No TBD/TODO in docs (verified during closure commit)
- [ ] Committed and pushed (closure commit pending)
- [ ] GitHub Issue closed (`stage:done`) (pending)

**Feature 189 is now officially CLOSED upon cleanup completion.**
