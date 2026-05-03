# PM Plan Review: Feature 120 -- Architecture Lifecycle Command

**Reviewer**: product-manager
**Date**: 2026-04-09
**Artifact**: `specs/120-architecture-lifecycle-command/plan.md`
**Verdict**: APPROVED_WITH_CONCERNS

---

## Review Summary

The plan is well-structured, correctly scoped, and faithfully implements all 22 functional requirements from the spec across 4 implementation phases. Two command files are modified, no scope creep is detected, and Out of Scope boundaries are respected. Two non-blocking concerns are documented below.

---

## 1. Spec Requirements Coverage (22 FRs)

| FR | Description | Plan Phase | Status |
|----|------------|------------|--------|
| FR-001 | Frontmatter schema (5 fields) | Phase 1, Step 3a | COVERED |
| FR-002 | Version starts at 1, increments by 1 | Phase 1, Step 3a | COVERED |
| FR-003 | SHA-256 of body only, sha256: prefix | Phase 1, Step 3a | COVERED |
| FR-004 | Explicit shasum -a 256 invocation | Phase 1, Step 3a + Tech Stack | COVERED |
| FR-005 | Legacy files treated as v0 | Phase 1, Steps 0/0a | COVERED |
| FR-006 | Archive before overwriting | Phase 1, Step 0a | COVERED |
| FR-007 | Archive preserves complete file | Phase 1, Step 0a item 3 | COVERED |
| FR-008 | Archive directory auto-created | Phase 1, Step 0a item 2 | COVERED |
| FR-009 | Archive append-only / idempotent | Phase 1, Step 0a | MINOR GAP -- see Concern 1 |
| FR-010 | No archive on first-time generation | Phase 1, Step 0 flow | COVERED |
| FR-011 | previous_version relative path or null | Phase 1, Step 3a | COVERED |
| FR-012 | Copy architecture into output folder | Phase 2, Step 1.4 item 2 | COVERED |
| FR-013 | Verbatim copy | Phase 2, Step 1.4 item 2 | COVERED |
| FR-014 | Snapshot filename matches source | Phase 2, Step 1.4 item 2 | COVERED |
| FR-015 | Skip silently if no architecture file | Phase 2, Step 1.4 item 3 | COVERED |
| FR-016 | Snapshot after Step 1.3, before Step 2 | Phase 2, Step 1.4 integration point | COVERED |
| FR-017 | Guided update with 6 categories | Phase 3, Step 0b | COVERED |
| FR-018 | No changes = file untouched | Phase 3, Step 0b item 5 | COVERED |
| FR-019 | Description summarizes changes | Phase 3, item 4 | COVERED |
| FR-020 | Archive path relative to parent dir | Phase 1, Step 0a item 1 | COVERED |
| FR-021 | Example files not modified | Phase 4, validation item 5 | COVERED |
| FR-022 | Downstream pipeline unaffected | Phase 4, validation item 6 | COVERED |

**Result**: 22/22 FRs addressed. 1 minor gap in explicit wording (FR-009).

---

## 2. User Story Coverage (4 Stories)

| Story | Priority | Plan Phase | Status |
|-------|----------|------------|--------|
| US-120-1: Version Tracking | P0 | Phase 1 (Steps 0, 0a, 3a) | COVERED -- all 4 spec acceptance scenarios addressed |
| US-120-2: Archive | P0 | Phase 1 (Step 0a) | COVERED -- all 4 spec acceptance scenarios addressed |
| US-120-3: Snapshot | P0 | Phase 2 (Step 1.4) | COVERED -- all 4 spec acceptance scenarios addressed |
| US-120-4: Guided Update | P1 | Phase 3 (Step 0b) | COVERED -- all 3 spec acceptance scenarios addressed |

**Result**: 4/4 user stories have corresponding implementation phases with complete acceptance coverage.

---

## 3. Scope Integrity

**Out of Scope items verified NOT in plan**:
- Architecture diff visualization: NOT present
- Automatic change detection from codebase: NOT present
- Architecture version pinning (--arch-version): NOT present
- Git history integration: NOT present
- Downstream pipeline awareness of architecture version: NOT present
- Modification of example files: NOT present (explicitly validated against)
- Bi-directional version reference in threats.md: NOT present

**Scope creep check**: Plan modifies exactly 2 command files (tachi.architecture.md, tachi.threat-model.md). No new files created in command structure. No agent files modified. No parser files modified. No schema changes.

**Result**: CLEAN -- no scope creep detected. All Out of Scope items respected.

---

## 4. Phase/Priority Alignment

| PRD Priority | Spec Priority | Plan Phase | Alignment |
|--------------|--------------|------------|-----------|
| P0: Frontmatter, archive, snapshot, legacy handling | P0: FR-001 to FR-016, FR-020 to FR-022 | Phases 1, 2, 4 | ALIGNED |
| P1: Guided update, description auto-population | P1: FR-017 to FR-019 | Phase 3 | ALIGNED |

No P1 items promoted to P0. No P0 items deferred.

**Result**: ALIGNED across PRD, spec, and plan.

---

## 5. Success Criteria Coverage (7 Criteria)

| Criterion | Plan Validation Item | Status |
|-----------|---------------------|--------|
| SC-001: 100% of files have valid frontmatter | Item 1: first-time produces v1 | COVERED |
| SC-002: N runs produce N-1 archive entries | Item 2: update produces vN+1 | PARTIALLY COVERED -- see Concern 2 |
| SC-003: 100% threat model folders contain snapshot | Item 4: snapshot in output folder | COVERED |
| SC-004: Legacy files work without errors | Item 5: 3 examples work without frontmatter | COVERED |
| SC-005: Checksum matches recomputation | Item 7: checksum verification | COVERED |
| SC-006: No downstream pipeline changes | Item 6: downstream unaffected | COVERED |
| SC-007: Guided update produces accurate description | Not explicitly listed in Phase 4 | MINOR GAP -- see Concern 2 |

**Result**: 5/7 fully covered, 2/7 with minor gaps in explicit validation coverage.

---

## 6. Risk Coverage

| Spec Risk | Plan Risk | Alignment |
|-----------|-----------|-----------|
| Frontmatter breaks orchestrator (Low/Medium) | Present with identical mitigation | ALIGNED |
| Archive directory conflicts (Low/Low) | Present with identical mitigation | ALIGNED |
| Platform tool availability (Low/Low) | Present -- additive risk from plan | GOOD ADDITION |
| -- | Guided update complexity (Medium/Low) | GOOD ADDITION |

**Result**: All spec risks present in plan. Plan adds 2 additional risks with mitigations. No spec risks missing.

---

## Concerns (Non-Blocking)

### Concern 1: FR-009 Idempotency Not Explicit in Step 0a (Low)

**FR-009** states: "The archive MUST be append-only -- previous archive entries are never modified by subsequent operations (overwrite is permitted only for the same version number to support idempotent retries)."

Plan Step 0a describes the copy operation but does not explicitly address the idempotent retry case. The spec's edge case section covers this ("Attempting to archive v3 but .archive/v3/ already exists... Overwrite the existing archive entry"), and the plan's copy semantics would naturally overwrite, so the behavior is correct by implementation. However, the plan would benefit from an explicit note in Step 0a acknowledging this idempotent overwrite behavior.

**Recommendation**: Add a brief note to Step 0a: "If the archive version directory already exists (retry scenario), overwrite the existing entry (idempotent per version number)."

### Concern 2: Phase 4 Validation Missing SC-002 Multi-Run Test and SC-007 (Low)

Phase 4 validation item 2 tests a single update (vN to vN+1) but SC-002 requires validating that "N consecutive runs produce N-1 archive entries." The single-update test is necessary but not sufficient for full SC-002 coverage. Additionally, SC-007 (guided update description accuracy) is not listed as a Phase 4 validation item -- it is implied by Phase 3 acceptance but should be an explicit validation step.

**Recommendation**: Add to Phase 4 validation:
- "Run `/tachi.architecture` 3 times consecutively on the same file; verify archive contains v1 and v2 entries with correct content from each version" (covers SC-002).
- "Verify guided update mode produces a description field that accurately reflects the changes made" (covers SC-007).

---

## Verdict

**APPROVED_WITH_CONCERNS** -- The plan is product-aligned, correctly scoped, and ready for tasks generation. Two non-blocking concerns should be addressed during implementation but do not require plan revision.

**Sign-off**:
- Reviewer: product-manager
- Date: 2026-04-09
- Status: APPROVED_WITH_CONCERNS
