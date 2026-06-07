---
prd_reference: docs/product/02_PRD/182-crosswalk-related-superseded-edges-2026-06-07.md
triad:
  pm_signoff:
    agent: product-manager
    date: 2026-06-07
    status: APPROVED
    notes: "Full PRD-spec traceability confirmed — every v1.1 PRD requirement maps to spec FR-001..015 / SC-001..007 (≥80 related floor, 80-150 band + 150 hard ceiling, spike-conditional yield-tripwire, anti-drift-over-floor-hitting, catalog-gated superseded with documented deferral, README rubric extension, integrity 5/5 green, no schema/test/ADR change, ≥500 primary floor preserved at 542). Scope discipline honored: #182 standalone (#183 separate), all Out-of-Scope lines respected (catalog expansion=Wave 2, superseded remainder deferred, F-A2/F-B unchanged), zero scope creep, disjoint write-set (crosswalk.yaml + README.md + specs/182-* only). Material refinement check PASSED: the source-class audit (OWASP-LLM→CWE demoted to low/inferred as prose-only; OWASP-LLM→ATLAS added as published high/medium lane) is a sound in-bounds application of the PRD's own anti-drift posture resolving PRD Open Q1 — NOT an out-of-bounds scope change; no PRD amendment required (conservative: tightens the high/medium pool, never loosens; touches no frozen contract). Data claims verified live: 542 primary / 0 related / 0 superseded, 5 integrity test functions, EDGE_TYPE/CONFIDENCE enums + PRIMARY_EDGE_FLOOR=500, catalog counts (cwe 53/atlas 36/attack 701/owasp 60/nist 72/ctrl 8/stride 11), test_records_sorted catalog-only — all match. 7 SCs objectively measurable (SC-002/SC-003 correctly trace to [MANUAL-ONLY] FRs). 4 non-blocking observations: (1) US P0 vs spec P1/P2/P3 = same 3 stories, sequencing notation only; (2) optional v1.2 PRD changelog one-liner for the source-class audit; (3) deferred-superseded artifact must be checked in even if authored set=0 (FR-008/FR-012 cover it); (4) reference-edges.yaml (input) and deferred-superseded.md (output) are distinct artifacts, plan should carry both. Details: .aod/results/product-manager.md"
  architect_signoff: null  # Added by /aod.project-plan
  techlead_signoff: null   # Added by /aod.tasks
---

# Feature Specification: Crosswalk `related` + `superseded` Edge Expansion — First Tranche (F-182)

**Feature Branch**: `182-crosswalk-related-superseded-edges`
**Created**: 2026-06-07
**Status**: Draft
**PRD Reference**: `docs/product/02_PRD/182-crosswalk-related-superseded-edges-2026-06-07.md`
**Initiative**: BLP-05 Wave 3 (Crosswalk Integrity & Edges) · Priority P2 (Light)
**Input**: User description: "PRD: 182 - crosswalk-related-superseded-edges"

## User Scenarios & Testing *(mandatory)*

### User Story 1 — Traverse "what else relates to this?" (Priority: P1)

An adopter pivoting a tachi finding across frameworks (a downstream AI-security tool, SIEM, or compliance mapper) has the *primary* mapping for a taxonomy item but needs its *neighbourhood* — the additional cross-references the single best mapping omits. They query `crosswalk.yaml` for `edge_type: related` edges originating from (or pointing to) a given item and receive a connected set of authoritative, citable cross-framework relationships, so they can expand a finding into its full framework context instead of stopping at one edge.

**Why this priority**: This is the core deliverable and the gap #182 exists to close. F-180 shipped a primary-only graph (542 edges, one mapping per relationship); the `related` edge type was frozen authorized-but-unused for exactly this follow-on. Without it, the crosswalk answers "what is THE mapping" but not "what's the neighbourhood" — the traversal every downstream pivot wants. P1.

**Independent Test**: In a fresh Python 3.11 shell with `pyyaml`, `yaml.safe_load(open('schemas/taxonomy/crosswalk.yaml'))`, filter to `edge_type == 'related'`, and confirm the result is a non-empty set (committed floor ≥80, or the documented achievable floor) of edges whose endpoints all resolve in their named catalogs and whose `high`/`medium` confidence labels each carry a supporting citation — delivering value with no other story shipping.

**Acceptance Scenarios**:

1. **Given** `crosswalk.yaml` after this feature, **When** I count edges with `edge_type: related`, **Then** I find ≥80 edges (target band 80–150, never exceeding 150) — OR a documented achievable floor below 80 with a written yield-tripwire rationale if the high/medium core could not clear 80.
2. **Given** the set of new `related` edges, **When** I inspect the `source.taxonomy`/`target.taxonomy` of each, **Then** every edge is drawn from one of the audited published source classes (CWE↔CWE, OWASP-Web→CWE, ATLAS→ATT&CK, OWASP-LLM→ATLAS), and **zero** `high`/`medium` edges originate from the prose-only OWASP-LLM→CWE class.
3. **Given** every new `high` or `medium` related edge, **When** I read its `citation`, **Then** the citation explicitly supports the assigned confidence label (a one-sentence justification exists), per the anti-drift rule.
4. **Given** the full integrity suite, **When** I run `pytest tests/schemas/test_taxonomy_integrity.py`, **Then** all 5 functions pass and the `primary` edge count is unchanged at 542 (≥500 floor preserved).

---

### User Story 2 — Answer "what superseded what?" (Priority: P2)

A consumer auditing historical lineage ("which item replaced which?") queries `crosswalk.yaml` for `edge_type: superseded` edges. They receive every deprecation/replacement pair that is *authorable today* — i.e., where both the superseded item and its successor already exist as catalog records — plus a clear, recorded disposition of the pairs deferred because they need historical records the catalogs do not yet carry.

**Why this priority**: `superseded` expresses old→newer lineage, but under the referential-integrity gate it is only authorable where **both** endpoints resolve in current catalogs. The PRD established at definition that most superseded examples (OWASP :2023 revisions, deprecated ATT&CK techniques) need historical records that are catalog-expansion territory (BLP-05 Wave 2), so #182's authorable superseded set may be small or empty. The value is the audit + honest deferral, not a volume floor. P2.

**Independent Test**: Filter `crosswalk.yaml` to `edge_type == 'superseded'`; confirm every such edge's endpoints resolve in their catalogs; confirm a deferred-set disposition (one line per deferred class → follow-on) exists in the feature artifacts. Passes even if the authored set is empty, provided the deferral is documented.

**Acceptance Scenarios**:

1. **Given** the seven catalog YAMLs at their current record counts, **When** the catalogs are surveyed for deprecation/replacement pairs whose **both** endpoints resolve, **Then** each such pair is authored as a `superseded` edge with a supporting citation.
2. **Given** deprecation/replacement pairs whose endpoints do **not** both resolve under current catalogs, **When** the survey completes, **Then** each deferred class is recorded with a one-line rationale pointing to its follow-on (post catalog-expansion) — never silently dropped.
3. **Given** the authored `superseded` set is empty (no authorable pairs found), **When** the feature closes, **Then** the empty result is explicitly documented as an acceptable outcome with the deferral rationale, not treated as a failure.

---

### User Story 3 — Inherit a settled edge-authoring methodology (Priority: P3)

A future edge author (or external contributor) opening `schemas/taxonomy/README.md` finds the confidence/edge-authoring rubric extended with `related`/`superseded`-specific calibration examples and the authoritative-source list, so they can calibrate confidence and pick legitimate sources without re-deriving the methodology — and without falling into the OWASP-LLM→CWE drift trap.

**Why this priority**: F-180's README already documents the 3-value confidence rubric and the anti-drift rule for primary edges. Extending it with related/superseded examples turns a one-time authoring effort into a reusable, drift-resistant methodology. Valuable but dependent on US1/US2 having settled the patterns first. P3.

**Independent Test**: Read `schemas/taxonomy/README.md`; confirm a `related`/`superseded` calibration section exists with worked examples for each audited source class, the View-ID rule for CWE parents, and an explicit "OWASP-LLM→CWE is prose-only → low" caution. A reader can classify a new candidate edge's confidence using only the README.

**Acceptance Scenarios**:

1. **Given** the extended README, **When** a new author evaluates a candidate CWE↔CWE edge, **Then** the rubric tells them to cite the relationship Nature + the CWE View ID and assign `high` only if the relationship is published in that view.
2. **Given** the extended README, **When** a new author considers an OWASP-LLM→CWE edge, **Then** the rubric explicitly warns the relationship is prose-only on official pages and must be `low`/inferred (or `medium` only against a named, pinned community source).

---

### Edge Cases

- **Yield-tripwire fires** (high/medium core < 80): the achievable floor is committed with a written rationale; the band is **not** padded with `low`-confidence edges to reach 80 (anti-drift over floor-hitting).
- **Hard ceiling pressure** (>150 high-confidence candidates surveyed): authoring stops at 150 (balloon valve); the surplus is recorded as available headroom for a follow-on, not authored past the ceiling.
- **View-dependent CWE parent** (e.g., CWE-89 → CWE-943 in View-1000 vs CWE-74 in View-1003): the edge records the View ID in its citation; the two views are not treated as contradictory duplicates.
- **Concurrent #185 cwe.yaml expansion**: if #185 lands during #182, the CWE pool #182 draws from changes mid-flight — author against a frozen catalog snapshot or sequence the two (run in series).
- **Duplicate-with-different-edge-type**: a `related` edge for a source→target pair that already has a `primary` edge is permitted (the 5-tuple uniqueness key includes `edge_type`); a second `related` edge for the same pair is a forbidden duplicate.
- **Citation resolves but doesn't support the label**: caught by the anti-drift citation audit (a `high` edge whose citation is a blog, not an authoritative listing, is downgraded), not by the (shape-only) integrity test.

## Requirements *(mandatory)*

### Functional Requirements

> **Acceptance Criteria Rule**: ACs above use Given/When/Then. `[MANUAL-ONLY]` marks requirements that cannot be fully automated (external-source harvest + curator judgment).

- **FR-001**: The system MUST author a committed floor of **≥80** `high`/`medium`-confidence `related` edges into `schemas/taxonomy/crosswalk.yaml`, within a target band of **80–150**, with **150 as a hard ceiling** (no authoring past 150).
- **FR-002**: A build-start survey MUST validate the achievable `high`/`medium` yield from the source classes before bulk authoring. If the achievable `high`/`medium` core cannot clear 80, the system MUST commit the **documented achievable floor with a written yield-tripwire rationale** rather than pad the count with `low`-confidence edges. `[MANUAL-ONLY]` survey requires external-source harvest and curator judgment.
- **FR-003**: `related` edges counted toward the floor MUST be drawn ONLY from these audited published source classes: (a) **CWE↔CWE** published relationships (both endpoints in the 53-record `cwe.yaml`); (b) **OWASP-Web Top 10 → CWE** published category-page cross-references (target CWE in `cwe.yaml`); (c) **ATLAS → ATT&CK** `ATT&CK-reference` field relations (ATLAS id in `mitre-atlas.yaml`, ATT&CK id in `mitre-attack.yaml`); (d) **OWASP-LLM Top 10 → ATLAS** published "Reference Links" relations (ATLAS id in `mitre-atlas.yaml`).
- **FR-004**: The system MUST NOT assign `high` or `medium` confidence to any **OWASP-LLM → CWE** edge (the relationship is prose-only on official OWASP pages, not a published structured list). Such edges are admissible only as `low`/inferred against a named non-authoritative citation and MUST be excluded from the FR-001 floor count.
- **FR-005**: Each `related` edge MUST carry a `confidence` value assigned per the anti-drift rule (F-180 FR-013 / README confidence rubric): `high` only where the authoritative source explicitly lists the target; `medium` for an inferred one-hop citable to a single authoritative document; `low` for two-hop or thematic relations.
- **FR-006**: CWE↔CWE edge citations MUST record both the relationship **Nature** (e.g., `ChildOf`, `PeerOf`, `CanPrecede`) and the CWE **View ID** (parents are view-dependent), so two view-specific citations are not mistaken for a contradiction.
- **FR-007**: The system MUST author the `superseded` edges whose **both** endpoints already resolve under current catalogs (e.g., a deprecated CWE and its replacement both present in `cwe.yaml`; an ATT&CK deprecation pair both present in `mitre-attack.yaml`). This set MAY be small or empty.
- **FR-008**: The system MUST document the catalog-gated **deferred** `superseded` set — one line per deferred class with a rationale pointing to its follow-on (post catalog-expansion). Deferred pairs MUST NOT be silently dropped.
- **FR-009**: The system MUST extend `schemas/taxonomy/README.md` with `related`/`superseded`-specific calibration examples and the authoritative-source list, including (i) the View-ID rule for CWE parents and (ii) an explicit caution that OWASP-LLM→CWE is prose-only and must be `low`/inferred.
- **FR-010**: Every new edge MUST satisfy the existing referential-integrity gate: `source.id` and `target.id` each resolve to a record in the catalog named by their `taxonomy`; `edge_type ∈ {primary, related, superseded}`; `confidence ∈ {high, medium, low}`; `source.taxonomy`/`target.taxonomy` in the closed 7-value enum; the 5-tuple `(source.taxonomy, source.id, target.taxonomy, target.id, edge_type)` is unique; `citation` is non-empty and URL-shaped or a resolvable repo-relative path.
- **FR-011**: The feature MUST make **no schema change, no integrity-test change, no new ADR, and no change to ADR-027** — the enum and the test already authorize `related`/`superseded`. The **≥500 primary floor MUST be preserved** (only non-primary edges are added; no existing `primary` edge is downgraded; primary count stays 542).
- **FR-012**: Before editing `crosswalk.yaml`, the system MUST capture the harvested source relations to a checked-in artifact (e.g., `specs/182-crosswalk-related-superseded-edges/reference-edges.yaml`), so authoring does not depend on un-checked-in survey state (KB Entry 13 discipline).
- **FR-013**: After all changes, the taxonomy integrity suite (`tests/schemas/test_taxonomy_integrity.py`, all 5 functions) MUST pass (5/5 green).
- **FR-014**: An **anti-drift citation audit** MUST verify, for every `high`/`medium` edge, that the cited source supports the assigned label; any edge failing the audit MUST be downgraded to the weaker label (this is a content check beyond the shape-only `test_citation_shape`). `[MANUAL-ONLY]` requires reading the cited source.
- **FR-015**: The feature MUST add a `feat(182)` CHANGELOG entry (BLP-05 F-3 sibling-h3 cluster placement), a `crosswalk.yaml` header provenance note mirroring the F-186 convention, and close Issue #182 `stage:done` on delivery.

### Key Entities *(include if feature involves data)*

- **`related` edge**: A `crosswalk.yaml` record with `edge_type: related` connecting two taxonomy items beyond their primary mapping. Same shape as any edge (`source{taxonomy,id}` → `target{taxonomy,id}`, `confidence`, `citation`); distinguished only by `edge_type` and by being drawn from a published cross-reference rather than the single canonical mapping.
- **`superseded` edge**: A `crosswalk.yaml` record with `edge_type: superseded` expressing old-item → newer-item lineage; authorable only where both endpoints resolve in current catalogs.
- **Audited source class**: A category of authoritative published relation (CWE↔CWE, OWASP-Web→CWE, ATLAS→ATT&CK, OWASP-LLM→ATLAS) with a known publication status and confidence ceiling; the legitimate provenance for floor-counted `related` edges.
- **Reference-edges artifact**: A checked-in survey output (`specs/182-*/reference-edges.yaml`) capturing the harvested candidate relations and their citations before any `crosswalk.yaml` edit.
- **Deferred-set disposition**: A recorded, per-class rationale for each `superseded` (or `related`) relationship class that cannot be authored under current catalogs, pointing to its follow-on.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: `crosswalk.yaml` carries **≥80** `related` edges within the 80–150 band (never >150) — OR a documented achievable floor with a written yield-tripwire rationale if the high/medium core could not clear 80.
- **SC-002**: **100%** of `high`/`medium` `related` edges have a citation that explicitly supports the assigned confidence label (anti-drift citation audit passes with zero un-downgraded violations).
- **SC-003**: **100%** of floor-counted `related` edges originate from the four audited published source classes; **0** `high`/`medium` edges originate from the prose-only OWASP-LLM→CWE class.
- **SC-004**: The authored `superseded` set equals the full catalog-authorable set discovered by the survey, and **every** deferred class has a one-line recorded disposition (an empty authored set with documented deferral satisfies this).
- **SC-005**: The integrity suite is **5/5 green**; the `primary` edge count is unchanged (542); **0** schema files, **0** test files, and **0** ADRs are modified.
- **SC-006**: `schemas/taxonomy/README.md` contains a `related`/`superseded` calibration section with a worked example per audited source class, the View-ID rule, and the OWASP-LLM→CWE caution — sufficient for a new author to calibrate confidence from the README alone.
- **SC-007**: **0** duplicate edges (the 5-tuple uniqueness holds across the whole file) and **100%** of new-edge endpoints resolve in their named catalogs.

## Assumptions

- **A1**: The seven catalog YAMLs remain at their current record counts (`cwe.yaml` 53, `mitre-atlas.yaml` 36, `mitre-attack.yaml` 701, `owasp.yaml` 60, `nist-ai-rmf.yaml` 72, control-category 8, stride-ai-category 11) for the duration of #182. If #185 (cwe.yaml expansion) lands first or concurrently, authoring runs against a frozen catalog snapshot or is sequenced after #185.
- **A2**: The achievable `high`/`medium` yield is survey-determined. The Triad planning estimate (high-confidence core ≈ 65: CWE↔CWE ≈ 36 + ATLAS→ATT&CK ≈ 15 + OWASP-beyond-primary ≈ 14) is a planning figure that the FR-002 survey validates, not a guarantee.
- **A3**: The `superseded` authorable set may legitimately be small or empty; that is an acceptable, documented outcome, not a failure (US2).
- **A4**: `crosswalk.yaml` is not lexicographically sort-gated (the `test_records_sorted` check covers only the 7 catalogs). New edges may be appended/grouped; the 5-tuple uniqueness key is the integrity backstop.

## Dependencies

- **F-180 Taxonomy Crosswalk Collection (DELIVERED, PR #181)** — provides `crosswalk.yaml`, the 5-test integrity suite, and the README confidence rubric this feature extends.
- **F-186 MITRE ATT&CK + ATLAS Catalog Expansion (DELIVERED)** — establishes `mitre-atlas.yaml` (36) and `mitre-attack.yaml` (701) at the counts that gate ATLAS→ATT&CK authorability; provides the no-migration / provenance-note convention (FR-011, FR-015).
- **F-241 (DELIVERED)** — prior crosswalk provenance convention referenced for header notes.
- **#185 cwe.yaml expansion (BLP-05 Wave 2)** — sequencing dependency: #185 enlarges the CWE pool #182's richest vein draws from; run #182 in series after #185 or against a frozen snapshot (A1).
- **Disjoint write-sets**: #182 touches only `schemas/taxonomy/crosswalk.yaml`, `schemas/taxonomy/README.md`, and `specs/182-*` artifacts — disjoint from #184/#185 catalog edits.

## Out of Scope

- **Catalog expansion** (adding new CWE/ATLAS/ATT&CK/OWASP records) — BLP-05 Wave 2 (#184/#185/#186). #182 authors edges only against records that already exist.
- **The catalog-gated `superseded` remainder** (pairs needing historical records the catalogs do not carry) — deferred with recorded disposition to a post-catalog-expansion follow-on.
- **Citation-URL link-rot monitoring** — #183, the separate Wave-3 sibling.
- **Finding-level citation, coverage attestation, and agent-reference migration** (F-A2 / F-B) — deferred since F-180; unchanged here.
- **Bulk authoring of `low`-confidence edges to reach the floor** — forbidden by the anti-drift rule (FR-002).
- **Any change to schema, integrity tests, or ADR-027** — explicitly excluded (FR-011).
