---
prd_reference: docs/product/02_PRD/185-cwe-catalog-expansion-2026-06-11.md
triad:
  pm_signoff:
    agent: product-manager
    date: 2026-06-11
    status: APPROVED_WITH_CONCERNS
    notes: "Spec fully traces PRD v1.1 — all 5 PRD FRs covered by FR-001..FR-008, 40-ID list byte-matches, all 9 Triad-folded concerns carried, SCs measurable, US coverage and scope fences intact. FR-006 (Coverage Attestation baseline regen) ACCEPTED as consequence-scope required by the PRD's own DoD, not creep — independently verified cwe in ORDERED_FRAMEWORKS + byte-identity suite mechanics + ADR-037 D-9 lane. Conditions: architect ratifies C2-interpretation at plan sign-off; team-lead re-validates O/R/P at tasks; PRD v1.2 errata at docs wave. 3 minor concerns, none blocking. Details: .aod/results/product-manager.md"
  architect_signoff: null  # Added by /aod.project-plan
  techlead_signoff: null   # Added by /aod.tasks
---

# Feature Specification: CWE Catalog Expansion — T029 Drift-Edge Restoration (F-A1.2)

**Feature Branch**: `185-cwe-catalog-expansion`
**Created**: 2026-06-11
**Status**: Draft
**Input**: User description: "PRD: 185 - cwe-catalog-expansion"
**PRD**: [docs/product/02_PRD/185-cwe-catalog-expansion-2026-06-11.md](../../docs/product/02_PRD/185-cwe-catalog-expansion-2026-06-11.md) (v1.1, Triad-approved 2026-06-11)
**Research**: [research.md](research.md)

## User Scenarios & Testing *(mandatory)*

### User Story 1 - The Catalog Gains the Missing CWE Records (Priority: P1)

A consumer resolving any CWE ID cited in tachi's output or crosswalk — including the AI-domain CWEs (CWE-1427 prompt injection, CWE-1426 GenAI output validation, CWE-1039 adversarial perturbations) — finds a catalog record with the exact MITRE-published name and canonical URL. The architect first dispositions each of the 40 missing IDs (add / reject / defer) against the authoritative MITRE CWE v4.20 corpus, with the Category/Pillar policy call documented; every "add" ID then lands in `schemas/taxonomy/cwe.yaml`.

**Why this priority**: The records are the referential-integrity prerequisite for everything else — no edge can be restored before its target resolves (FR-030). Standalone, a complete citation-resolution catalog already delivers value (AI CWEs become citable).

**Independent Test**: Add the records alone (no edge changes) — the integrity suite stays 5/5 green, the catalog grows 53 → 93 (add-all expectation), and every new ID resolves at its canonical URL with a name byte-matching the v4.20 dictionary.

**Acceptance Scenarios**:

1. **Given** the 40 missing CWE IDs pinned in the PRD, **When** the architect completes the disposition pass against the comprehensive `cwec_v4.20.xml` dictionary, **Then** Issue #185 carries one add/reject/defer line per ID (40/40) including explicit rationale for the 4 Category entries (CWE-16, 255, 937, 1035) and 1 Pillar entry (CWE-693), and no deprecated entry receives "add".
2. **Given** the architect's add-set, **When** records are inserted into `cwe.yaml`, **Then** each record carries shape `{id, full_id, name, url}` with no `cwe_refs` key, `name` exactly as published in the v4.20 dictionary, `url` of the form `https://cwe.mitre.org/data/definitions/<N>.html`, and correct lexicographic position.
3. **Given** the expanded catalog, **When** a scripted all-40 name-diff runs against the `cwec_v4.20.xml` harvest, **Then** 0 mismatches are reported (including CWE-1039, renamed by MITRE at v4.17 — the current name must be used).
4. **Given** a reject or defer disposition for any ID, **When** the feature closes, **Then** that ID is absent from the catalog and its rationale is recorded on Issue #185 (no silent drop).

---

### User Story 2 - The 67 CWE-Blocked Edges Return (Priority: P2)

A consumer mapping OWASP categories (across all six tracked families: Top 10, Mobile, LLM, ML, ASI, API) or MITRE techniques T1070.006/T1562 onto CWE finds the published mappings that Feature 180's T029 cleanup removed solely because their target records were absent. The 67 edges are reconstructed byte-exact from the pre-removal blob (`e58f247`) via an early checked-in restore-set artifact, and restored for every target ID the architect approved — closing PRD #186's 2-edge deferral in the process.

**Why this priority**: This is the feature's core value (published-mapping coverage restored at the crosswalk's highest-fan-out node), but it is referentially dependent on User Story 1 — records must land before edges.

**Independent Test**: With the add-set records in place, restore the edges — `test_crosswalk_referential_integrity` and `test_crosswalk_loads` pass, the crosswalk grows 578 → 645 (541 → 608 primary, add-all expectation), and a field-level diff of each restored edge against the `e58f247` blob shows byte-identity.

**Acceptance Scenarios**:

1. **Given** dangling commit `e58f247` (verified present 2026-06-11), **When** the restore-set is extracted, **Then** it contains exactly the 67 target-CWE-missing edges (65 `owasp→cwe` + 2 `mitre-attack→cwe`; the 1 other-drift cwe-target edge, 20 non-CWE-target removals, and 25 dedupe collapses are excluded) and is committed as `specs/185-cwe-catalog-expansion/restored-edges.yaml` with a schema contract, **before** any catalog or crosswalk edit.
2. **Given** the restore-set and the architect's add-set, **When** edges are inserted into `crosswalk.yaml`, **Then** only edges whose target ID received "add" are restored, each byte-identical to the blob in `edge_type` (all `primary`), `confidence` (34 high / 32 medium / 1 low), and `citation`.
3. **Given** the restored crosswalk, **When** the dedupe checks run (exact tuple key and same-endpoint near-key), **Then** 0 collisions are found against the pre-restoration edge set (0 verified at definition; re-verified at build).
4. **Given** restoration completes, **Then** the 2 edges PRD #186 deferred (`T1070.006 → CWE-1269`, `T1562 → CWE-693`) are present, and the `confidence: low` edge (`T1070.006 → CWE-1269`) — the crosswalk's first `low` edge — is preserved as-is, not upgraded.

---

### User Story 3 - Integrity, Report Baselines, and the Decision Trail Stay Intact (Priority: P3)

A maintainer auditing the change finds: the taxonomy integrity suite green at every commit, the Coverage Attestation report surfaces regenerated intentionally (not silently broken), and a complete decision trail — per-ID dispositions on Issue #185, provenance headers, lineage entries, and the F-180/#186 residual trail closed.

**Why this priority**: Governance and verification wrap the data work; they cannot ship without User Stories 1–2 but the feature is not done without them.

**Independent Test**: Run the full verification set (taxonomy integrity suite, backward-compatibility byte-identity suite, scripted name-diff, `/aod.analyze`) — all green; inspect Issue #185, `cwe.yaml` header, `crosswalk.yaml` lineage block, README §3.5, ADR-037 D-7, and F-180's NEXT-SESSION for the required trail entries.

**Acceptance Scenarios**:

1. **Given** any commit touching `schemas/taxonomy/`, **When** `tests/schemas/test_taxonomy_integrity.py` runs, **Then** all 5 functions pass (load/shape, sort, referential integrity, no-dupes + ≥500 primary floor, citation shape).
2. **Given** the catalog grew (53 → add-set size), **When** the committed example security-report baselines are regenerated in the same change-set under `SOURCE_DATE_EPOCH=1700000000`, **Then** `tests/scripts/test_backward_compatibility.py` byte-identity tests pass, with deltas confined to Coverage Attestation pages (ADR-037 D-9 lane) — non-CA pages byte-identical.
3. **Given** delivery, **When** the trail is inspected, **Then** CHANGELOG carries `feat(185)`, `cwe.yaml`'s header carries the F-A1.2 provenance block (source, Issue #185, v4.20 retrieval date, Category/Pillar annotations for CWE-16/255/937/1035/693), `crosswalk.yaml`'s "Edit lineage" block carries the F-185 line, README §3.5 reflects the new composition and count, ADR-037 D-7 is annotated (5/8 substitution CWEs now cataloged), and `specs/180-*/NEXT-SESSION.md` marks the T029 CWE-blocked residual resolved.
4. **Given** the feature closes, **When** `/aod.analyze` runs, **Then** no spec/plan/tasks inconsistency is reported, and Issue #185 is closed `stage:done`.

---

### Edge Cases

- **Architect rejects or defers some IDs (add-set ⊂ 40)**: edges targeting rejected/deferred IDs stay out with recorded rationale; record/edge counts adjust (53+N records, 578+M edges); the plan handles any add-set ⊆ 40 without rework. Rejecting CWE-693 would re-strand a #186-deferred edge — the disposition must address this consequence explicitly.
- **Dangling commits GC'd or unavailable (fresh clone) before extraction**: mitigated by extracting and committing `restored-edges.yaml` as the first build task — after that commit, no step depends on the dangling objects (proven #186 pattern).
- **CWE name drift since the blob era**: records carry the **current** v4.20 published names (CWE-1039 was renamed at v4.17); edges carry no name fields, so blob byte-exactness is unaffected by renames.
- **First `low`-confidence edge in the crosswalk**: `T1070.006 → CWE-1269` restores with `confidence: low`. The schema enum permits it and byte-exactness requires it — reviewers must not "fix" it to medium.
- **Crosswalk baseline shifts between plan and build** (another feature lands on `crosswalk.yaml`): re-derive the removed-edge filter and re-run the 0-collision check from the blobs + live file at build before insertion.
- **MITRE source unavailable at build**: the harvest pins `cwec_v4.20.xml.zip` (single download, no anti-bot tripwire known for cwe.mitre.org); if unreachable, the record-insertion wave blocks rather than falling back to aggregator sources (F-180 R7 lesson).
- **Mid-sequence integrity**: edges must never land before their target records in commit order — `test_crosswalk_referential_integrity` green at every intermediate commit, not just at delivery.

## Requirements *(mandatory)*

### Functional Requirements

> **Acceptance Criteria Rule**: Each AC MUST begin with **Given** and follow Given/When/Then structure. Use `[MANUAL-ONLY] <reason>` (reason ≥10 chars) inline to mark ACs that cannot be automated.

- **FR-001**: The architect MUST disposition all 40 missing CWE IDs (the exact set pinned in PRD FR-1: CWE-16, 73, 201, 213, 255, 256, 259, 260, 295, 307, 311, 312, 319, 326, 327, 359, 489, 520, 521, 540, 565, 601, 611, 614, 693, 732, 798, 799, 829, 915, 916, 937, 1035, 1039, 1104, 1174, 1269, 1357, 1426, 1427) against the comprehensive MITRE `cwec_v4.20.xml` dictionary — one add/reject/defer line per ID published on Issue #185 — **before** any catalog or crosswalk modification lands. Lead posture: add all 40, with fidelity-first rationale for the 4 Categories + 1 Pillar (citation-resolution layer, OWASP publishes these IDs, CWE-200/CWE-284 precedent). A deprecated entry MUST NOT receive "add" (none expected at v4.20).

- **FR-002**: For each "add" ID, the system MUST gain a `cwe.yaml` record with shape `{id, full_id, name, url}` — no `cwe_refs` key (ADR-027 Decision 1), `name` harvested verbatim from the pinned `cwec_v4.20.xml` (scripted bulk harvest, not per-page transcription; no paraphrase), `url` = `https://cwe.mitre.org/data/definitions/<N>.html`, inserted in lexicographic `id` order (Python string-sort semantics). Expected outcome with add-all: 53 → 93 records.

- **FR-003**: The restore-set MUST be extracted from `git show e58f247:schemas/taxonomy/crosswalk.yaml` by the filter "removed at T029 AND `target.taxonomy == cwe` AND target ID outside the frozen 53" (yielding exactly 67 edges), and committed as `specs/185-cwe-catalog-expansion/restored-edges.yaml` plus a schema contract (mirroring `specs/186-mitre-catalog-expansion/contracts/restored-edges.schema.md`) **as the first build task**, in parallel with — not gated on — the FR-001 disposition. The 1 other-drift cwe-target edge, 20 non-CWE-target removals, and 25 dedupe collapses MUST be excluded.

- **FR-004**: Every restored edge MUST be byte-identical to its `e58f247` blob form in `edge_type`, `confidence`, and `citation` (any `_resolvable`-style working annotations stripped on insert, per the #186 pattern); only edges whose target ID received "add" are restored; records MUST land before their dependent edges in commit sequence; the exact-tuple and same-endpoint dedupe checks MUST be re-run against the live crosswalk immediately before insertion (0 collisions required). Expected outcome with add-all: 578 → 645 edges (541 → 608 primary), including the 2 #186-deferred edges.

- **FR-005**: `tests/schemas/test_taxonomy_integrity.py` (5 functions) MUST pass at every commit that touches `schemas/taxonomy/` — load/shape/URL, lexicographic sort, referential integrity, duplicate prevention + ≥500-primary floor, citation shape. No test edit is required or permitted to make counts pass (the suite has no exact-count assertions).

- **FR-006**: Because `cwe` participates in the Coverage Attestation pipeline (`ORDERED_FRAMEWORKS` in `scripts/extract-report-data.py`), the committed example security-report baselines MUST be intentionally regenerated in the same change-set as the catalog growth, under `SOURCE_DATE_EPOCH=1700000000`, following the ADR-037 D-9 lane: deltas confined to Coverage Attestation pages, non-CA pages byte-identical, and `tests/scripts/test_backward_compatibility.py` green at delivery. *(Research-driven addition — see Assumptions for the PRD delta rationale.)*

- **FR-007**: The decision trail MUST close: (a) CHANGELOG `feat(185)` entry; (b) `cwe.yaml` header F-A1.2 provenance block — source, Issue #185, cwec v4.20 + retrieval date, Category/Pillar annotations for CWE-16/255/937/1035/693; (c) `schemas/taxonomy/README.md` §3.5 composition/count update plus a grep sweep for other stale count-bearing lines; (d) `crosswalk.yaml` header "Edit lineage" F-185 line; (e) ADR-037 D-7 annotation (blockquote + Revision History row, docs-only) noting 5 of 8 substitution CWEs now cataloged; (f) `specs/180-taxonomy-crosswalk-collection/NEXT-SESSION.md` T029 CWE-blocked residual marked resolved (F-A1.2 entry alongside the F-A1.3 one); (g) Issue #185 closed `stage:done` with the disposition comment. `[MANUAL-ONLY] GitHub issue closure and board state are external-service actions verified by inspection.`

- **FR-008**: A scripted all-40 name-diff of the inserted records against the `cwec_v4.20.xml` harvest MUST run in the verification wave and report 0 mismatches (supplemented by per-page spot-checks for the 5 Category/Pillar and 3 AI CWEs). The R7 failure mode (silent name contamination) is the target — names are not covered by the integrity suite.

### Key Entities *(include if feature involves data)*

- **CWE catalog record**: one entry in `schemas/taxonomy/cwe.yaml` — `{id, full_id, name, url}`, lexicographically sorted, never carries `cwe_refs`. Grows 53 → 93 (add-all expectation).
- **Crosswalk edge**: one `source → target` mapping in `schemas/taxonomy/crosswalk.yaml` with `edge_type`, `confidence`, `citation`; both endpoints must resolve in their catalogs. Grows 578 → 645 (add-all).
- **Restore-set artifact**: `specs/185-cwe-catalog-expansion/restored-edges.yaml` — the 67 filtered edges byte-copied from the `e58f247` blob, plus schema contract; the durable replacement for the dangling-object dependency.
- **Disposition record**: per-ID add/reject/defer line on Issue #185 with rationale — the governance gate output that sizes the add-set.
- **Coverage Attestation baseline**: committed `security-report.pdf.baseline` per example — regenerated intentionally because catalog record counts render on CA pages.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 40/40 CWE IDs carry a documented, source-verified add/reject/defer disposition on Issue #185, including explicit Category/Pillar rationale — 0 silent drops.
- **SC-002**: `cwe.yaml` holds 53 + |add-set| records (93 if add-all), sorted, shape-clean, and the scripted all-40 name-diff vs `cwec_v4.20.xml` reports 0 mismatches.
- **SC-003**: `crosswalk.yaml` holds 578 + |restored| edges (645 / 608 primary if add-all) with 0 dangling endpoints, 0 duplicate tuples, the 2 #186-deferred edges present, and 0 excluded T029 edges (other-drift, non-CWE, dedupe) re-introduced.
- **SC-004**: `tests/schemas/test_taxonomy_integrity.py` 5/5 green at delivery and at every intermediate commit touching the data files.
- **SC-005**: `tests/scripts/test_backward_compatibility.py` byte-identity tests green at delivery with regenerated baselines; PDF deltas confined to Coverage Attestation pages.
- **SC-006**: `/aod.analyze` reports no inconsistency; Issue #185 closed `stage:done`; all seven FR-007 trail surfaces updated.

## Assumptions

- **Add-all-40 is the lead expectation** (architect-endorsed at PRD review); the spec and plan handle any add-set ⊆ 40 without rework — counts in SC-002/SC-003 scale with the actual add-set.
- **Coverage Attestation baseline regeneration is in scope** — a research-driven delta vs the PRD. The PRD's "no baseline regeneration" (FR-5, architect C2) scoped the ADR-037 D-7 *annotation*, which remains docs-only and regen-free. The catalog growth itself, however, mechanically changes CA-page record counts/rows (cwe is in `ORDERED_FRAMEWORKS`; F-184's "0 regressions" precedent does not transfer because `nist-ai-600-1` is not), so the D-9 intentional-regen lane applies. Without it, delivery lands red on the byte-identity suite — contradicting the PRD's own DoD (tests green).
- **Dangling commits `e58f247`/`991e1ee` remain available until `restored-edges.yaml` is committed** (verified present 2026-06-11; the artifact commit then removes the dependency).
- **`cwe.mitre.org` and the v4.20 zip remain fetchable at build**; no anti-bot behavior observed. The harvest pins v4.20 — if MITRE ships a newer corpus before build, the build re-pins and re-runs the name-diff against the version actually used, recording it in the provenance header.
- **Citation URLs on the 67 edges** pass `test_citation_shape` by construction (URL-shape check only; #183 owns link-rot).
- **Existing toolchain suffices**: pytest + pyyaml via the project's verified invocation (`/usr/bin/python3 -m pytest …` ran 5/5 in ~1s on 2026-06-11), `typst` for baseline regeneration — no new tooling.

## Dependencies

- **F-180** (delivered): blobs `e58f247`/`991e1ee`, integrity suite, NEXT-SESSION SHAs, R7 lesson.
- **#186 / F-A1.3** (delivered, v4.42.0): restore mechanism, artifact + schema-contract pattern, the 2-edge deferral this feature closes.
- **#184 / F-A1.1** (delivered, v4.43.0): current 8-catalog / 578-edge baseline.
- **#182** (delivered, v4.42.0): the 37 `related` edges — 0 endpoint overlap with the 67 (verified).
- **ADR-027** (unchanged): taxonomy enum, record/edge shapes, Decision 1 no-`cwe_refs`.
- **ADR-037** (annotated only): D-7 substitution table; D-9 baseline-regeneration precedent.
- **External**: MITRE CWE v4.20 corpus (`cwec_v4.20.xml.zip`); GitHub Issue #185 for the disposition trail.
- **Sequencing**: F-185 lands before #183 (link-rot) so the rot sweep covers the expanded catalog and restored citations in one pass.

## Out of Scope

- The 1 cwe-target other-drift edge and 20 non-CWE-target T029 removals (correctly removed or #186 territory).
- The 25 dedupe collapses (duplicates by definition).
- Net-new edge authoring beyond the 67 (e.g., `related`/`superseded` edges to the 40 entering records, CWE↔CWE hierarchy edges — future tranche per the #182 cadence).
- `cwe_refs` population on CWE records (permanently excluded by ADR-027 Decision 1).
- Re-verification or re-titling of the existing 53 records; CWE Top 25 2026 refresh (README §6 playbook owns it).
- #183 citation link-rot checking.
- Schema changes, ADR amendments, new enum values, new taxonomies, `abstraction`/category fields on records (header-comment annotation at most).
- Any change to detection patterns, threat agents, or report templates beyond the regenerated baselines.
