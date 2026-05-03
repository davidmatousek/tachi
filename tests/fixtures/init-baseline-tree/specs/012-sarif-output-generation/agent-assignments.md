# Agent Assignments: Feature 012 — SARIF Output Generation

**Feature**: 012-sarif-output-generation
**Date**: 2026-03-22
**Total Tasks**: 20 (T001-T020)
**Estimated Total Effort**: 3-4 hours
**Execution Strategy**: 5 waves, sequential within wave where tasks share files

---

## Agent Assignment Matrix

| Task | Description | Agent | Rationale |
|------|-------------|-------|-----------|
| T001 | Add SARIF reference to orchestrator frontmatter | senior-backend-engineer | Markdown/YAML file modification |
| T002 | Update Output Format Specification preamble | senior-backend-engineer | Markdown file modification (same file as T001) |
| T003 | Update SARIF Severity Mapping in output.yaml | senior-backend-engineer | YAML schema modification |
| T004 | Create SARIF 2.1.0 reference template | senior-backend-engineer | JSON template creation |
| T005 | Add SARIF Output Generation section header | senior-backend-engineer | Markdown prompt writing |
| T006 | Add Category to Rule ID Mapping Table | senior-backend-engineer | Markdown prompt writing |
| T007 | Add Severity Mapping Table | senior-backend-engineer | Markdown prompt writing |
| T008 | Add SARIF Tool Metadata instructions | senior-backend-engineer | Markdown prompt writing |
| T009 | Add Rule Definition Templates | senior-backend-engineer | Markdown prompt writing |
| T010 | Add Finding IR to SARIF Result Mapping | senior-backend-engineer | Markdown prompt writing |
| T011 | Add SARIF Schema Compliance Structure | senior-backend-engineer | Markdown prompt writing |
| T012 | Add JSON Structural Self-Check | senior-backend-engineer | Markdown prompt writing |
| T013 | Add Correlated Finding Mapping (US2) | senior-backend-engineer | Markdown prompt writing |
| T014 | Add Dual-Location Instructions (US3) | senior-backend-engineer | Markdown prompt writing |
| T015 | Add Fingerprint Computation Instructions (US4) | senior-backend-engineer | Markdown prompt writing |
| T016 | Validate SARIF — mermaid-agentic-app example | tester | Output validation |
| T017 | Validate SARIF — ascii-web-api example | tester | Output validation |
| T018 | Validate SARIF schema compliance | tester | Schema compliance verification |
| T019 | Add SARIF taxonomies support (P1) | senior-backend-engineer | Markdown prompt writing |
| T020 | Update orchestrator output self-check | senior-backend-engineer | Markdown prompt writing |

### Agent Workload Summary

| Agent | Tasks Assigned | Load % |
|-------|---------------|--------|
| senior-backend-engineer | 17 (T001-T015, T019, T020) | 75% |
| tester | 3 (T016-T018) | 25% |

---

## Parallel Execution Waves

### Wave 1: Setup (Phase 1)

**Execution**: Sequential (both tasks target `agents/orchestrator.md`)
**Estimated Time**: 20 minutes

| Task | Agent | Notes |
|------|-------|-------|
| T001 | senior-backend-engineer | Modify orchestrator frontmatter |
| T002 | senior-backend-engineer | Modify Output Format Specification preamble (same file) |

**Quality Gate W1**: Verify orchestrator.md frontmatter references `templates/threats.sarif` and preamble mentions dual output (threats.md + threats.sarif).

---

### Wave 2: Foundational (Phase 2)

**Execution**: Parallel (different files — no conflict)
**Estimated Time**: 30 minutes
**Prerequisite**: Wave 1 complete

| Task | Agent | Target File |
|------|-------|-------------|
| T003 | senior-backend-engineer | `schemas/output.yaml` |
| T004 | senior-backend-engineer | `templates/threats.sarif` (new file) |

**Quality Gate W2**: Verify output.yaml Note row reads `note | 0.1` (not `none | 0.0`). Verify threats.sarif is valid JSON with SARIF 2.1.0 schema URI, example rules[], results[], relatedLocations, and partialFingerprints. This gate BLOCKS all subsequent waves.

---

### Wave 3: US1 MVP (Phase 3)

**Execution**: Sequential (all tasks append to same section in `agents/orchestrator.md`)
**Estimated Time**: 90 minutes
**Prerequisite**: Wave 2 complete (schema fix + template must exist)

| Task | Agent | Section Added |
|------|-------|---------------|
| T005 | senior-backend-engineer | SARIF section header |
| T006 | senior-backend-engineer | Category to Rule ID Mapping Table |
| T007 | senior-backend-engineer | Severity Mapping Table |
| T008 | senior-backend-engineer | Tool Metadata instructions |
| T009 | senior-backend-engineer | Rule Definition Templates |
| T010 | senior-backend-engineer | Finding IR to SARIF Result Mapping |
| T011 | senior-backend-engineer | Schema Compliance Structure |
| T012 | senior-backend-engineer | JSON Structural Self-Check |

**Quality Gate W3 (MVP Checkpoint)**: Orchestrator SARIF section contains all 8 sub-sections (T005-T012). Category mapping covers all 8 STRIDE+AI categories. Severity table has 5 rows with correct CVSS strings. Tool metadata references Tachi. Self-check covers all 5 validation points. This is the MVP gate — feature is independently testable and deliverable after this point.

---

### Wave 4: US2-US4 Post-MVP (Phases 4-6)

**Execution**: Sequential within same file (safer — all append to `agents/orchestrator.md` SARIF section)
**Estimated Time**: 30 minutes
**Prerequisite**: Wave 3 complete (US1 MVP must be in place)

| Task | Agent | User Story | Section Added |
|------|-------|------------|---------------|
| T013 | senior-backend-engineer | US2 | Correlated Finding Mapping |
| T014 | senior-backend-engineer | US3 | Dual-Location Instructions |
| T015 | senior-backend-engineer | US4 | Fingerprint Computation |

**Quality Gate W4**: Verify T013 handles zero-correlation case. Verify T014 includes trust_zone cross-reference per Architect concern M-01. Verify T015 fingerprint hash is deterministic (SHA-256 truncated to 16 hex chars). All three sub-sections present and non-overlapping.

---

### Wave 5: Polish and Validation (Phase 7)

**Execution**: Mixed — parallel group then sequential follow-up
**Estimated Time**: 40 minutes
**Prerequisite**: Wave 4 complete (all user stories implemented)

#### Sub-wave 5a: Parallel (independent targets)

| Task | Agent | Notes |
|------|-------|-------|
| T016 | tester | Validate against mermaid-agentic-app example |
| T017 | tester | Validate against ascii-web-api example |
| T019 | senior-backend-engineer | Add taxonomies support (P1 enhancement, additive) |

#### Sub-wave 5b: Sequential (depends on 5a validation results)

| Task | Agent | Notes |
|------|-------|-------|
| T018 | tester | Schema compliance validation (uses outputs from T016/T017) |
| T020 | senior-backend-engineer | Update self-check section (final orchestrator update) |

**Quality Gate W5 (Final)**: Both example inputs produce valid SARIF. Schema compliance passes all 5 structural checks. Taxonomies section present with OWASP and CWE references. Self-check updated to verify dual output. All 20 tasks complete.

---

## Time Estimate Summary

| Wave | Tasks | Parallelism | Estimated Time |
|------|-------|-------------|----------------|
| Wave 1: Setup | T001-T002 | Sequential | 20 min |
| Wave 2: Foundational | T003-T004 | Parallel | 30 min |
| Wave 3: US1 MVP | T005-T012 | Sequential | 90 min |
| Wave 4: US2-US4 | T013-T015 | Sequential | 30 min |
| Wave 5: Polish | T016-T020 | Mixed | 40 min |
| **Total** | **20 tasks** | | **~3.5 hours** |

---

## Risk Notes

1. **Single-file contention**: 15 of 20 tasks modify `agents/orchestrator.md` — sequential execution within waves eliminates merge conflicts
2. **MVP gate at Wave 3**: Feature is testable and deliverable after Wave 3 — Waves 4-5 are incremental P1 enhancements
3. **Architect concern M-01**: T014 must cross-reference Phase 1 Trust Boundaries data for `fullyQualifiedName` — verify trust zone lookup path during Wave 4
4. **Architect concern M-02**: T003 must update ONLY the Note row in output.yaml — no other severity rows touched

---

**Approved by**: team-lead
**Date**: 2026-03-22
