# PM Spec Review: Feature 120 — Architecture Lifecycle Command

**Reviewer**: product-manager
**Date**: 2026-04-09
**Artifact**: `specs/120-architecture-lifecycle-command/spec.md`
**PRD Reference**: `docs/product/02_PRD/120-architecture-lifecycle-command-2026-04-09.md`
**Verdict**: APPROVED

---

## 1. PRD User Story Coverage

| PRD User Story | Spec User Story | Status | Notes |
|---------------|----------------|--------|-------|
| US-120-1: Architecture Version Tracking (P0) | User Story 1 (P0) | COVERED | All 3 PRD acceptance criteria present. Spec adds a 4th scenario (first-time generation, no existing file) which is a valid edge case derived from PRD FR-1 business rules. |
| US-120-2: Architecture Archive (P0) | User Story 2 (P0) | COVERED | All 3 PRD acceptance criteria present. Spec adds a 4th scenario (first-time generation, no archive created) derived from PRD FR-2 business rules. |
| US-120-3: Automatic Architecture Snapshot (P0) | User Story 3 (P0) | COVERED | All 3 PRD acceptance criteria present. Spec adds a 4th scenario (custom output directory) matching PRD AC-3. All 3 PRD ACs map directly to spec scenarios 1, 2, and 3. |
| US-120-4: Guided Architecture Update (P1) | User Story 4 (P1) | COVERED | All 3 PRD acceptance criteria present and mapped 1:1 to spec scenarios 1, 2, and 3. |

**Assessment**: All 4 PRD user stories are fully addressed. The spec adds supplementary acceptance scenarios (Story 1 scenario 4, Story 2 scenarios 3-4) that are derived from PRD business rules and strengthen testability. No user stories are missing or misrepresented.

---

## 2. Functional Requirements Coverage

| PRD FR | Description | Spec FR(s) | Status | Notes |
|--------|-------------|-----------|--------|-------|
| FR-1: Architecture Frontmatter Schema | YAML frontmatter with version, date, description, checksum, previous_version | FR-001, FR-002, FR-003, FR-004, FR-005, FR-011 | COVERED | PRD FR-1 decomposed into 6 granular spec FRs. FR-004 (explicit `shasum` tool invocation) addresses the team-lead concern from PRD review. FR-011 specifies `previous_version` as relative path. |
| FR-2: Archive Mechanism | Archive to `.archive/vN/` before overwrite | FR-006, FR-007, FR-008, FR-009, FR-010, FR-020 | COVERED | PRD FR-2 decomposed into 5 spec FRs. FR-009 adds idempotent retry semantics (overwrite same version). FR-020 codifies relative path derivation. |
| FR-3: Architecture Snapshot in Threat Model | Copy architecture into timestamped output folder | FR-012, FR-013, FR-014, FR-015, FR-016 | COVERED | PRD FR-3 decomposed into 5 spec FRs. FR-016 specifies the exact integration point (after Step 1.3, before Step 2) per architect concern in PRD review. |
| FR-4: Guided Update Mode | Walk user through change categories when existing file detected | FR-017, FR-018, FR-019 | COVERED | PRD FR-4 decomposed into 3 spec FRs. All 6 update categories from PRD preserved verbatim. |

**Additional Spec FRs (not directly in PRD FRs but derived from PRD scope/constraints)**:
- FR-021: Example files remain unmodified (from PRD Out of Scope: "Modification of existing example architecture files")
- FR-022: Downstream pipeline stages unaffected (from PRD Non-Functional Requirements: compatibility)

**Assessment**: All 4 PRD functional requirements are fully decomposed into 22 spec-level FRs. The decomposition is faithful — no PRD requirement is dropped, weakened, or contradicted. The 2 additional FRs (021, 022) codify explicit PRD boundary statements, which is good practice.

---

## 3. Success Criteria Alignment

| PRD Success Criteria | Spec Success Criteria | Status | Notes |
|---------------------|----------------------|--------|-------|
| Traceability: 100% of threat model output folders contain architecture snapshot | SC-003 | MATCH | Verbatim match. |
| Version Continuity: Version increments correctly across consecutive updates | SC-002 | MATCH | Spec strengthens with explicit formula: "N times produces N-1 archive entries." |
| Archive Integrity: Archived versions match original content (checksum verification) | SC-005 | MATCH | Spec targets checksum re-computation validation. |
| Architecture files contain YAML frontmatter with version, date, description | SC-001 | MATCH | Spec adds "all five required fields" — more precise than PRD. |
| Running `/tachi.architecture` on existing file preserves version history | SC-002 | MATCH | Covered by the consecutive-run archive count. |
| Downstream pipeline stages unaffected | SC-006 | MATCH | Verbatim match. |

**Additional Spec Success Criteria**:
- SC-004: Legacy/example files work without frontmatter (from PRD compatibility requirements)
- SC-007: Guided update `description` reflects session changes (from PRD US-120-4 AC)

**Assessment**: All 5 PRD success criteria are reflected in the spec. The spec adds 2 additional measurable outcomes (SC-004, SC-007) derived from PRD content. All criteria are measurable and testable.

---

## 4. Scope Integrity

### In Scope Comparison

| PRD In Scope Item | Spec In Scope | Status |
|-------------------|--------------|--------|
| Architecture frontmatter schema (P0) | Present (P0) | MATCH |
| Archive mechanism (P0) | Present (P0) | MATCH |
| Automatic snapshot in threat model (P0) | Present (P0) | MATCH |
| Legacy file handling (P0) | Present (P0) | MATCH |
| Guided update mode (P1) | Present (P1) | MATCH |
| Change description auto-population (P1) | Present (P1) | MATCH |

**Spec additions to In Scope**: "Backward compatibility validation against example architecture files" — this is derived from PRD Non-Functional Requirements (Example Compatibility) and codifies it as an explicit scope item. This is a legitimate refinement, not scope creep.

### Out of Scope Comparison

| PRD Out of Scope Item | Spec Out of Scope | Status |
|----------------------|-------------------|--------|
| Architecture diff visualization | Present | MATCH |
| Automatic architecture change detection from codebase | Present | MATCH |
| Architecture version pinning (--arch-version 3) | Present | MATCH |
| Integration with git history | Present | MATCH |
| Downstream pipeline awareness of architecture version | Present | MATCH |
| Modification of existing example architecture files | Present | MATCH |

**Spec additions to Out of Scope**: "Bi-directional architecture version reference in threats.md frontmatter (future enhancement)" — this is a proactive boundary that prevents scope creep during implementation. It was not in the PRD but is a reasonable forward-looking exclusion.

**Assessment**: No scope creep detected. All PRD scope boundaries are preserved. The spec adds one proactive Out of Scope item (bi-directional version reference) and one explicit In Scope item (backward compatibility validation), both of which are legitimate refinements derived from PRD content.

---

## 5. User Story Quality Assessment

### Testability
All acceptance scenarios follow Given/When/Then format and specify concrete, verifiable outcomes:
- File paths are specific (e.g., `docs/security/.archive/v3/architecture.md`)
- Version numbers are concrete (e.g., "version: 3" becomes "version: 4")
- Behaviors are binary (file exists or not, frontmatter present or not)

### Completeness
Each user story includes:
- Narrative context (who, what, why)
- Priority rationale explaining dependency order
- Independent test description for isolation testing
- Multiple acceptance scenarios covering happy path and boundary conditions

### PRD Alignment
Acceptance scenarios map 1:1 to PRD acceptance criteria with the following enhancements:
- Story 1 adds scenario 4 (first-time generation) — valid edge case from FR-1 business rules
- Story 2 adds scenario 3 (legacy file archived as v0) — valid from FR-2 business rules
- Story 2 adds scenario 4 (first-time generation, no archive) — valid from FR-2 business rules
- Story 3 scenario 3 addresses missing-file case that PRD AC did not specify but FR-3 business rules require

All additions strengthen the spec without contradicting or weakening PRD intent.

---

## 6. Priority Alignment

| Priority | PRD Assignment | Spec Assignment | Status |
|----------|---------------|----------------|--------|
| P0 | US-120-1, US-120-2, US-120-3 | Stories 1, 2, 3 | MATCH |
| P1 | US-120-4 | Story 4 | MATCH |
| P0 scope | Frontmatter, archive, snapshot, legacy handling | Same items | MATCH |
| P1 scope | Guided update, change description | Same items | MATCH |

**Assessment**: Priority assignments are identical between PRD and spec. The P0/P1 split is consistent with the dependency analysis: P0 items are foundational (versioning, archiving, snapshotting) and P1 items enhance the experience (guided updates).

---

## 7. Edge Cases

The spec includes 7 edge cases not explicitly enumerated in the PRD:
1. Concurrent updates (last-write-wins)
2. Corrupted frontmatter (treat as legacy)
3. Missing parent directory (create it)
4. Empty architecture file (treat as legacy)
5. Archive directory already has the version (idempotent overwrite)
6. Non-default architecture file path (relative archive path)
7. Very large architecture files (linear scaling)

All are reasonable derivations from PRD business rules and constraints. None introduce new scope or contradict PRD boundaries.

---

## 8. Triad Review Concerns Addressed

The spec incorporates feedback from the PRD's architect and team-lead reviews:

| PRD Review Concern | Addressed In Spec | Status |
|-------------------|-------------------|--------|
| Architect: Snapshot integration point needs precision (Medium) | FR-016: "after Step 1.3, before Step 2" | ADDRESSED |
| Architect: Archive inherits parent .gitignore status (Low) | Not explicitly in FRs but covered in Assumptions | ADDRESSED (implicitly) |
| Team-Lead: SHA-256 needs explicit tool invocation (Medium) | FR-004: "shasum -a 256 on macOS/Linux" | ADDRESSED |
| Team-Lead: Archive path must be relative to file parent dir (Low) | FR-020: explicit relative path derivation | ADDRESSED |
| Team-Lead: Fixed convention for MVP (Low) | Assumptions: ".archive/ convention acceptable" | ADDRESSED |
| Team-Lead: Validate examples without frontmatter (Info) | SC-004, FR-021 | ADDRESSED |

---

## Verdict

**STATUS: APPROVED**

The spec faithfully decomposes all PRD requirements into implementable, testable specifications. All 4 user stories are covered with strengthened acceptance scenarios. All 4 functional requirements are decomposed into 22 granular FRs without loss. All success criteria are measurable. Scope boundaries match exactly with two legitimate additions (backward compatibility validation in-scope, bi-directional version reference out-of-scope). Priority alignment is exact. Triad review concerns from the PRD phase are incorporated.

No blocking issues. No changes requested.
