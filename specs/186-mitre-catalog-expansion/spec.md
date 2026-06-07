---
prd_reference: docs/product/02_PRD/186-mitre-catalog-expansion-2026-06-07.md
triad:
  pm_signoff:
    agent: product-manager
    date: 2026-06-07
    status: APPROVED
    notes: "0 blocking. Spec covers all 5 PRD FR-clusters 1:1 + adds enforceable FR-006 (must-not-restore) / FR-008 (no schema/ADR). 0 NEEDS CLARIFICATION. PM independently reproduced the architect PoC (restore 10 edges → integrity 5/5 green, 0 collisions, 526→536, tree left clean) and CONFIRMED the spec's refinement of the PRD: the 16-ID gap maps to exactly 16 edges (10 resolvable + 6 ATLAS-blocked); the 2 CWE-blocked edges (T1070.006→CWE-1269, T1562→CWE-693) reference NO gap ID → entirely out of #186 scope (not 'deferred to #185' as PRD v1.1 said) — spec is the more-correct artifact. 2 minor non-blocking: (1) cosmetic priority-label drift (PRD P0/P0/P0 vs spec P1/P2/P3 — spec ordering is correct); (2) PRD prose '9 atlas→attack' vs spec's exact 10-edge enumeration (follow FR-001 list). Carry-forward: FR-002 extract restore-set to checked-in artifact EARLY (dangling SHAs unreachable from main); FR-003 disposition gate tolerates empty add-set. Details: .aod/results/product-manager.md"
  architect_signoff: null  # Added by /aod.project-plan
  techlead_signoff: null   # Added by /aod.tasks
---

# Feature Specification: MITRE ATT&CK + ATLAS Catalog Expansion — Residual Drift-Edge Restoration (F-A1.3)

**Feature Branch**: `186-mitre-catalog-expansion`
**Created**: 2026-06-07
**Status**: Draft
**Input**: PRD 186 (BLP-05 Wave 2); Issue #186 (`follow-on-180`). Restore the MITRE crosswalk edges Feature 180's T029 cleanup removed and Feature 241 has since unblocked, and disposition the 6 ATLAS IDs still missing.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Restore the 10 Now-Resolvable MITRE Edges (Priority: P1)

A downstream consumer (analyst or tool) ingests tachi's framework crosswalk to map a finding onto MITRE ATT&CK/ATLAS techniques. Today, 16 MITRE edges that Feature 180 authored were removed at T029 because they referenced technique IDs absent from the then-frozen catalogs. Feature 241 has since added the catalog records for 10 of those edges' endpoints — but the edges were never put back. This story restores exactly those 10 edges so the crosswalk regains the MITRE connections it can legitimately carry.

**Why this priority**: This is the concrete, always-shippable deliverable. It is independent of the 6-ID disposition (US-2) and delivers the feature's core value (restored MITRE coverage) on its own — a viable MVP.

**Independent Test**: Restore the 10 enumerated edges from the recovered `e58f247` blob, run the taxonomy integrity suite, and confirm the crosswalk grows 526 → 536 with all endpoints resolving.

**Acceptance Scenarios**:

1. **Given** the 10 enumerated MITRE-scoped edges recovered byte-exact from commit `e58f247`, **When** they are added to `crosswalk.yaml`, **Then** the crosswalk contains 536 primary edges and every restored edge's `source.id`/`target.id` resolves in its catalog.
2. **Given** the restored crosswalk, **When** `test_crosswalk_referential_integrity` runs, **Then** it passes with zero dangling endpoints.
3. **Given** the restored crosswalk, **When** `test_crosswalk_loads` runs, **Then** no duplicate edge exists and the ≥500 primary-edge floor holds.
4. **Given** each restored edge, **When** its `edge_type`, `confidence`, and `citation` are compared to the `e58f247` original, **Then** they match byte-for-byte (no re-authoring).

---

### User Story 2 - Disposition the 6 Still-Missing ATLAS IDs (Priority: P2)

A maintainer (or future auditor) needs the open Feature-180 question — "what about the 6 ATLAS IDs T029 flagged?" — settled with an explicit, source-verified decision rather than silent omission. This story produces an add / reject / defer disposition for each of the 6 IDs, adds any "add"-disposition records, and restores any edge those additions unblock.

**Why this priority**: Decision-trail closure, not edge yield. Even adding all 6 unblocks at most 6 more edges, and F-241's phase-complete ATLAS expansion already excluded these 6 (biasing toward reject/defer). Valuable for auditability but secondary to US-1.

**Independent Test**: Verify each of the 6 IDs against the authoritative `atlas-data` source, record a disposition with rationale on Issue #186, and confirm any "add" record passes the catalog shape + sort tests.

**Acceptance Scenarios**:

1. **Given** the 6 IDs (T0001, T0005, T0025, T0037, T0043, T0048), **When** the architect verifies each against `mitre-atlas/atlas-data`, **Then** each receives a documented `add`/`reject`/`defer` decision with a one-line rationale on Issue #186. `[MANUAL-ONLY]` external-source verification + architect judgment.
2. **Given** an "add" disposition, **When** the record is inserted into `mitre-atlas.yaml`, **Then** it carries shape `{id, full_id, name, url, cwe_refs}`, its name matches the `atlas-data` publication, and it sits in correct lexicographic position (`test_framework_yamls_load` + `test_records_sorted` pass).
3. **Given** an "add" disposition that unblocks a previously-blocked edge, **When** that edge is restored from `e58f247`, **Then** referential integrity still holds.
4. **Given** a "reject" or "defer" disposition, **When** the feature closes, **Then** the corresponding edge remains absent and the rationale is recorded (no silent drop).

---

### User Story 3 - No Drift Re-Introduced, Integrity Stays Green (Priority: P3)

A reviewer must be confident the restoration put back only the legitimate MITRE-gap edges and did not re-introduce any of the semantic-drift or duplicate edges T029 correctly removed, and that the structural integrity gate stays green throughout.

**Why this priority**: A correctness guardrail over US-1/US-2. The restore source (`e58f247`) contains all 88 removed edges; restoring more than the scoped 16-ID set would re-break the crosswalk.

**Independent Test**: Diff the post-change crosswalk against the pre-change one and confirm only the intended edges were added; run the full integrity suite.

**Acceptance Scenarios**:

1. **Given** the change set, **When** the crosswalk diff is inspected, **Then** only the 10 (or 10 + FR-1-unblocked) MITRE-gap edges are added and none of the other ~72 T029-removed edges (semantic-drift, dedupe, non-MITRE) reappear.
2. **Given** the final state, **When** `tests/schemas/test_taxonomy_integrity.py` runs, **Then** all 5 test functions pass.
3. **Given** the final state, **When** `/aod.analyze` runs, **Then** it reports no inconsistency.

---

### Edge Cases

- **All 6 IDs reject/defer**: feature degenerates to exactly the 10-edge restore with zero record additions — a valid, complete outcome.
- **Some IDs add**: each "add" that has a blocked edge also restores that edge (crosswalk → 536 + k).
- **Dangling commits GC'd before extraction**: `e58f247`/`991e1ee` are unreachable from `main` and unpushed; the restore-set must be extracted to a checked-in artifact before any `git gc` or the recovery becomes impossible.
- **Restored edge collides with an existing edge**: dedupe on `(source.tax, source.id, target.tax, target.id, edge_type)` (0 collisions confirmed at spec time, but the guard must hold).
- **"Add" ID name differs from pre-T029 authoring**: use the `atlas-data` canonical name (F-180 R7 name-contamination lesson), not the value in the historical blob.
- **ATLAS source unreachable for FR-1**: if `atlas-data` cannot be fetched, the 6-ID disposition cannot be completed authoritatively — block US-2 (not US-1) and record the obstruction rather than guessing.

## Requirements *(mandatory)*

### Functional Requirements

> Each AC begins with **Given** and follows Given/When/Then. `[MANUAL-ONLY]` marks ACs that cannot be automated.

- **FR-001**: The system MUST restore exactly these 10 MITRE-scoped edges (recovered byte-exact from commit `e58f247`) to `crosswalk.yaml`, all `edge_type: primary`, `confidence: medium`: `T1190→CWE-20`, `AML.T0059→T1565.001`, `AML.T0060→T1557`, `AML.T0000→T1213`, `AML.T0003→T1195.002`, `AML.T0011→T1005`, `AML.T0016→T1195.002`, `AML.T0029→T1499`, `AML.T0034→T1565`, `AML.T0040→T1068`.
- **FR-002**: The restore-set MUST be extracted from `e58f247` into a checked-in artifact (e.g., `specs/186-*/restored-edges.yaml`) before any catalog/crosswalk edit, so restoration does not depend on the dangling commits surviving a `git gc` or fresh clone.
- **FR-003**: An architect MUST verify each of the 6 still-missing ATLAS IDs (`AML.T0001, T0005, T0025, T0037, T0043, T0048`) against the authoritative `mitre-atlas/atlas-data` source and record an `add`/`reject`/`defer` disposition with a one-line rationale on Issue #186 before any ATLAS record is added. `[MANUAL-ONLY]` requires external-source verification and architect judgment.
- **FR-004**: For each "add"-disposition ID, the system MUST add a record to `mitre-atlas.yaml` with shape `{id, full_id: ATLAS-AML.TXXXX, name (byte-exact from atlas-data), url: https://atlas.mitre.org/techniques/AML.TXXXX, cwe_refs: []}`, inserted in lexicographic `id` order.
- **FR-005**: For each "add" that unblocks one of the 6 blocked edges (`AML.T0001→T1213`, `T0005→T1213`, `T0025→T1005`, `T0037→T1213`, `T0043→T1190`, `T0048→T1499`), the system MUST also restore that edge byte-exact from `e58f247`.
- **FR-006**: The system MUST NOT restore any other T029-removed edge — neither the ~72 non-MITRE-gap removals (semantic-drift, dedupe, owasp→cwe, control→nist) nor the 2 CWE-target-blocked edges (`T1070.006→CWE-1269`, `T1562→CWE-693`, which belong to #185 and do not reference any of the 16 gap IDs).
- **FR-007**: After all changes, the taxonomy integrity suite (`tests/schemas/test_taxonomy_integrity.py`, all 5 functions) MUST pass: referential integrity (no dangling endpoint), record shape, lexicographic sort, no duplicate edges, ≥500 primary-edge floor, citation shape.
- **FR-008**: The system MUST NOT change any catalog `schema_version`, MUST NOT add a new ADR, and MUST NOT modify `mitre-attack.yaml` (all 3 originally-missing ATT&CK IDs already exist; only edges referencing them are restored).
- **FR-009**: The system MUST add an F-A1.3 provenance note to the `mitre-atlas.yaml` header (mirroring the F-241 note), add a `feat(186)` CHANGELOG entry, update the Feature-180 `NEXT-SESSION.md` decision trail to point at the #186 resolution, and close Issue #186 `stage:done`.

### Key Entities *(include if feature involves data)*

- **Crosswalk edge**: a directed relationship `{source: {taxonomy, id}, target: {taxonomy, id}, edge_type, confidence, citation}`. The 10 in-scope edges plus any FR-5 additions.
- **ATLAS catalog record**: `{id, full_id, name, url, cwe_refs[, out_of_scope, out_of_scope_rationale]}` in `mitre-atlas.yaml`. New records only for "add"-disposition IDs.
- **Restore-set artifact**: the checked-in extraction of the in-scope removed edges from `e58f247` (FR-002), the durable input to FR-001/FR-005.
- **ID disposition record**: per-ID `add`/`reject`/`defer` + rationale, published on Issue #186 (FR-003).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: `crosswalk.yaml` grows from 526 to **536** primary edges (the 10 restored), or 536 + k where k = edges unblocked by FR-1 "add" dispositions; the exact 10 edges of FR-001 are all present.
- **SC-002**: All **5** functions in `tests/schemas/test_taxonomy_integrity.py` pass; **0** dangling endpoints introduced.
- **SC-003**: **6/6** missing ATLAS IDs carry a documented, source-verified `add`/`reject`/`defer` disposition on Issue #186.
- **SC-004**: **0** of the ~72 out-of-scope T029-removed edges (semantic-drift/dedupe/non-MITRE) and **0** of the 2 CWE-blocked edges are present in the final crosswalk.
- **SC-005**: **0** catalog `schema_version` changes; **0** new ADRs; `mitre-attack.yaml` remains at 701 records (byte-unchanged).
- **SC-006**: `/aod.analyze` reports no inconsistency; a `feat(186)` CHANGELOG entry exists; Issue #186 is closed `stage:done`.

## Assumptions

- The dangling commits `e58f247` (pre-removal, 551 edges) and `991e1ee` (post-removal, 438 edges) remain in the local object DB until FR-002 captures the restore-set; their SHAs are recorded in `specs/180-*/NEXT-SESSION.md`.
- The 10 resolvable edges' endpoints (Feature-241-added catalog records) are correct as published; #186 trusts F-241's records and does not re-verify them.
- `mitre-atlas/atlas-data` is the authoritative ATLAS source for FR-003; per the F-180 R7 tripwire, `atlas.mitre.org` per-technique pages are not WebFetch-accessible (re-confirmed 2026-06-07).

## Dependencies

- **Feature 180** (PR #181) — the crosswalk, the integrity test, and the recoverable git history. DELIVERED.
- **Feature 241** — the ATLAS/ATT&CK catalog records that make the 10 edges resolvable. DELIVERED.
- **#185** (cwe.yaml expansion) — owns the 2 CWE-target-blocked edges; out of #186 scope.
