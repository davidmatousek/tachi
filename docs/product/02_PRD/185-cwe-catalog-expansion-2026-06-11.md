---
prd:
  number: "185"
  topic: cwe-catalog-expansion
  created: 2026-06-11
  status: Approved
  type: feature
triad:
  pm_signoff: { agent: product-manager, date: 2026-06-11, status: APPROVED, notes: "Author sign-off. Scope = Issue #185 (F-A1.2) upgraded from estimates to empirical counts via e58f247/991e1ee blob diff: exactly 67 CWE-blocked edges / 40 unique missing IDs; #186's 2-edge deferral contained and closed here. Last BLP-05 Wave-2 split-valve item, scoped standalone with disjoint write-set. v1.1 folds in all 4 architect + 5 in-scope team-lead corrections." }
  architect_signoff: { agent: architect, date: 2026-06-11, status: APPROVED_WITH_CONCERNS, notes: "Derivation re-run exact (67/40/0-collisions; blobs match git objects). No-schema/no-ADR verified (test enforces cwe_refs absence; no exact-count asserts; 5/5 green). Add-all-40 posture endorsed (CWE-200/284 precedent on disk); OQ-2: annotate Category status in header. 4 concerns (1 MED, 3 LOW), all folded into v1.1: C1 OWASP 6-family wording; C2 ADR-037 D-7 annotation (5/8 substitution CWEs in add-set); C3 cwec XML not per-view CSVs; C4 crosswalk header lineage line. No re-review needed before /aod.plan. Details: .aod/results/architect.md" }
  techlead_signoff: { agent: team-lead, date: 2026-06-11, status: APPROVED_WITH_CONCERNS, notes: "Feasible; deps verified merged (F-180/#186/#184/#182); e58f247/991e1ee present; no BLP-05 write-set conflicts. 6 concerns (1 MED, 5 LOW), 5 folded into v1.1: O/R/P 0.5/0.75/1.0d (floor needs scripted harvest); cwec XML pin; artifact extraction parallel to disposition; scripted all-40 name-diff in W2; #185 before #183. C6 (#182 frontmatter staleness) is out-of-PRD hygiene. Wave plan: W0 architect → W1 senior-backend-engineer → W2 tester ∥ code-reviewer. Details: .aod/results/team-lead.md" }
source:
  idea_id: 185
  story_id: null
---

# CWE Catalog Expansion — T029 Drift-Edge Restoration (F-A1.2)

**Status**: Approved (2026-06-11 — PM + Architect + Team-Lead; both reviewer sign-offs APPROVED_WITH_CONCERNS, all in-scope concerns folded into v1.1)
**Created**: 2026-06-11
**Author**: product-manager
**Reviewers**: architect, team-lead
**Priority**: P1 (Moderate) — BLP-05 Wave 2 (Crosswalk Catalog Expansion; **last of the three split-valve taxonomies**)
**Evidence**: Issue [#185](https://github.com/davidmatousek/tachi/issues/185) (`follow-on-180`), filed at Feature 180 T034. Root analysis: F-180 `specs/180-taxonomy-crosswalk-collection/` (T029 drift disposition, `NEXT-SESSION.md` recovery SHAs). Sibling deferral: PRD #186 FR-3 (2 CWE-blocked edges → #185). **Empirical derivation (2026-06-11, this PRD)**: pre/post-T029 blob diff from dangling commits `e58f247`/`991e1ee` — exact counts below. Strategic home: `_internal/strategy/BLP-05-framework-mapping-and-output-fidelity.md` §Wave 2 / F-2.

---

## Executive Summary

### The One-Liner
Add the **40 missing CWE records** that Feature 180's T029 cleanup orphaned, then restore the **67 crosswalk edges** that were removed only because those records were absent — completing BLP-05 Wave 2 and giving tachi's catalog the canonical AI CWEs (CWE-1427 prompt injection, CWE-1426 GenAI output validation) it currently cannot cite.

### Problem Statement
Feature 180 (F-A1, Taxonomy Crosswalk Collection, PR #181) authored **551 primary edges**, then at **T029** removed **88 semantic-drift edges** (+25 dedupe → 438 primary; later topped back up). Of those 88, **67 edges were not semantically wrong** — they were transcribed from published OWASP "List of Mapped CWEs" sections and MITRE ATT&CK technique pages, but their **target CWE IDs fell outside the frozen 53-record `cwe.yaml`**. Per **FR-030** referential-integrity strictness (every edge endpoint MUST resolve in its catalog), they were removed rather than left dangling. The architect's T029 disposition explicitly chose REMOVE over RESTORE *because* record expansion was outside the F-A1 freeze, and filed this Issue to preserve the path back.

**Empirically re-derived 2026-06-11** (blob diff `e58f247` → `991e1ee` → current, script `/tmp/derive185.py`):

| Fact | Value |
|---|---|
| Edges removed at T029 (semantic-drift, by tuple key) | **88** (+25 dedupe collapses) |
| └─ Removed **only for missing CWE target** (this PRD's scope) | **67** (65 `owasp→cwe` + 2 `mitre-attack→cwe`) |
| └─ The 65 OWASP-sourced edges span **all six OWASP families** tachi tracks | Top 10 A0x = 22, Mobile = 14, LLM = 12, ML = 9, ASI = 5, API = 3 *(architect-verified v1.1 correction — not Top 10:2021 alone)* |
| └─ Removed cwe-target edges whose target exists today (true drift — stays out) | 1 |
| └─ Removed non-CWE-target edges (MITRE-scoped etc. — #186 territory, stays out) | 20 |
| Unique missing CWE IDs referenced by the 67 | **40** (issue estimated "40+") |
| The 2 `mitre-attack→cwe` edges | **exactly the pair PRD #186 FR-3 deferred to #185** (`T1070.006 → CWE-1269`, `T1562 → CWE-693`) ✅ |
| Edge attributes of the 67 | all `edge_type: primary`; confidence 34 high / 32 medium / 1 low |
| Source endpoints that fail to resolve in today's catalogs | **0** |
| Exact-tuple or same-endpoint collisions vs today's crosswalk (578 edges) | **0** |

Two product consequences while this stays open:
1. **The crosswalk under-represents OWASP→CWE coverage** — 65 published OWASP CWE mappings that tachi already transcribed, spanning **all six tracked OWASP families** (Top 10:2021, Mobile, LLM, ML, ASI, API), are silently absent — eroding the "machine-readable source-of-truth" contract exactly where downstream tools pivot (CWE is the lingua franca of SAST/SCA tooling).
2. **`cwe.yaml` lacks the canonical AI CWEs.** An AI threat-modeling tool whose CWE catalog cannot cite **CWE-1427** (Improper Neutralization of Input Used for LLM Prompting), **CWE-1426** (Improper Validation of Generative AI Output), or **CWE-1039** (adversarial input perturbations) has a credibility gap in its home domain.

### Proposed Solution
Mirror the proven #186 playbook — disposition gate, then integrity-gated data restoration:

1. **Architect per-ID disposition (gate before any edit).** The architect reviews the **40 missing CWE IDs** against the authoritative MITRE CWE source and publishes an ID-by-ID **add / reject / defer** disposition on Issue #185. **Lead posture: add all 40** — every ID is a real, published, currently-resolvable CWE entry (none deprecated as of drafting), and the edges citing them are OWASP/MITRE-published mappings, not inventions. The one genuine policy call: **4 Category-type entries** (CWE-16, CWE-255, CWE-937, CWE-1035) **+ 1 Pillar** (CWE-693) are "mapping-discouraged/prohibited" under MITRE's *CVE-mapping* guidance — but tachi's catalog is a **citation-resolution layer, not a CVE-mapping recommender**, the source OWASP lists publish these IDs verbatim, and the catalog already contains discouraged-class precedent (CWE-200 Class, CWE-284 Pillar). Rejecting CWE-693 would also re-strand a #186-deferred edge.
2. **Catalog + crosswalk update.** Add the approved records to `schemas/taxonomy/cwe.yaml` (shape `{id, full_id, name, url}` — **no `cwe_refs`**, per the FR-003/ADR-027 Decision 1 exclusion; names harvested **exactly** from the MITRE CWE publication; lexicographic insert per FR-032). Then restore **exactly the 67 edges** (or the subset whose target ID got an "add"), reconstructed **byte-exact from the `e58f247` blob** — original `edge_type`/`confidence`/`citation` preserved — via an **early checked-in restore-set artifact** (`specs/185-*/restored-edges.yaml`, mirroring #186).

The integrity suite (5 functions) stays **5/5 green at every step**. **No schema change, no ADR**: `cwe` has been in the taxonomy enum since ADR-027 v1, the record shape is untouched, and edge restoration is monotonic (mirrors #186's verified "no schema / no ADR" pattern; contrast #184, which expanded the enum).

### Success Criteria
- Each of the 40 missing CWE IDs carries a documented add/reject/defer disposition on Issue #185, verified against the MITRE CWE source.
- Every "add"-disposition record is present in `cwe.yaml` with exact published name, canonical URL, correct lexicographic position (expected: **53 → 93 records** if add-all).
- The 67 CWE-blocked edges are restored to `crosswalk.yaml` byte-exact for every added target ID (expected: **578 → 645 edges; 541 → 608 primary**); rejected/deferred-ID edges stay out with recorded rationale; the 2 #186-deferred edges are restored (closing #186's residual).
- `tests/schemas/test_taxonomy_integrity.py` **5/5 green**; no T029 drift/dedupe edge re-introduced.
- CHANGELOG `feat(185)` entry; README §3.5 + catalog header provenance updated; Issue #185 closed with decision trail.

### Timeline
**O/R/P = 0.5 / 0.75 / 1.0 day** (optimistic / realistic / pessimistic — team-lead-pinned v1.1; the 0.5 floor holds **only with a scripted `cwec_latest.xml` harvest**, not per-page fetching). Cost is dominated by (a) harvesting 40 exact record names/URLs from the comprehensive cwec XML (~1.5–2.5h scripted incl. spot-checks), (b) the disposition pass (~1h — lighter than #186's: all IDs are known-real), and (c) blob-filter reconstruction + artifact (~1h, mechanism already proven by #186). Integrity test gives a ~1s correctness loop.

---

## Strategic Alignment

### Product Vision Alignment
**Reference**: [product-vision.md](docs/product/01_Product_Vision/product-vision.md)

Tachi's differentiator is emitting threat reasoning as machine-readable artifacts, and CWE is the most universally-consumed identifier system in that contract — it's how tachi findings join to SAST/SCA output, CVE data, and GitHub Code Scanning. Restoring 65 published OWASP→CWE mappings widens the highest-traffic pivot surface, and adding CWE-1426/1427/1039 lets tachi cite the CWEs that define its own home domain (prompt injection, GenAI output handling, adversarial ML).

### Roadmap Fit
**BLP-05 (Framework Mapping & Output Fidelity) Wave 2 — final item.** The three split-valve taxonomies of F-2: #186 (MITRE) delivered v4.42.0, #184 (NIST AI 600-1) delivered v4.43.0, **#185 (CWE) is the last** — delivering it completes Wave 2, leaving only #183 (link-rot) in Wave 3. Disjoint write-set from both siblings (touches only `cwe.yaml` + `crosswalk.yaml` + docs), exactly as the blueprint's parallelization analysis assumed. **Sequencing: #185 lands before #183**, so the link-rot sweep covers the expanded catalog (40 new URLs + 67 restored citations) in a single pass *(team-lead C5, folded v1.1)*.

### Predecessor Relationship
| Feature / Issue | Relationship |
|---|---|
| 180 (F-A1, PR #181) | Authored the 67 edges, then removed them at T029 under FR-030; froze cwe.yaml at 53 records. Squash-merged — recovery is from dangling commits `e58f247`/`991e1ee` (SHAs pinned in `specs/180-.../NEXT-SESSION.md`; **verified present 2026-06-11**). Parent of #185. |
| 186 (F-A1.3, v4.42.0) | Proved the restore mechanism (blob-filter → checked-in artifact → integrity-gated insert) and **explicitly deferred the 2 CWE-blocked edges to #185** (its FR-3 / Out-of-Scope). #185 closes that residual. |
| 184 (F-A1.x, v4.43.0) | Sibling Wave-2 taxonomy; set the current baseline (578 edges, 8 catalogs). Disjoint files; no interaction. |
| 182 (related/superseded tranche 1, v4.42.0) | Added the 37 `related` edges. **0 endpoint overlap with the 67** (verified) — no cross-type duplicate risk. |
| ADR-027 (Taxonomy Crosswalk Schema) | Defines enum + shapes. **Unchanged by #185** (`cwe` in enum since v1; Decision 1 excludes `cwe_refs` on CWE records). |

---

## Target Users & Personas

### Primary Persona: Downstream Tool / Analyst Consuming the Crosswalk
- **Role**: Engineer or tool ingesting tachi's crosswalk to join findings with CWE-keyed ecosystems (SAST, SCA, CVE/NVD, GitHub Code Scanning).
- **Goal**: Pivot from a tachi finding through OWASP/ATT&CK to CWE reliably.
- **Pain Point**: 67 published mappings silently absent — the consumer cannot distinguish "no such relationship" from "removed for catalog-freeze reasons"; AI-specific CWEs unciteable entirely.

**Why This Matters**: CWE is the highest-fan-out node in the crosswalk graph; gaps here cost more than gaps in any other taxonomy.

### Secondary Persona: Tachi Taxonomy Steward / Maintainer
- **Role**: Maintainer of crosswalk integrity and the F-180 decision trail.
- **Goal**: Close the largest remaining T029 follow-on with every removed edge either restored or durably dispositioned.
- **Pain Point**: The 40-ID gap is standing F-180 debt; #186's 2-edge deferral keeps a cross-feature loose end open.

**Why This Matters**: #185 is the last restoration-class follow-on — closing it retires the T029 debt entirely and completes the #186 decision trail.

---

## User Stories

### US-1: The Catalog Gains the 40 Missing CWE Records
**When** I resolve a CWE ID cited anywhere in tachi's output or crosswalk,
**I want** every referenced CWE — including the AI-specific ones — to resolve to a catalog record with its exact published name and canonical URL,
**So I can** trust `cwe.yaml` as a complete citation-resolution layer.

**Acceptance Criteria**:
- **Given** the architect's add-set (lead expectation: all 40), **when** records are added, **then** each carries shape `{id, full_id, name, url}` with **no `cwe_refs` key** (FR-003 exclusion), name matching the MITRE publication exactly, URL `https://cwe.mitre.org/data/definitions/<N>.html`.
- **Given** the expanded catalog, **when** `test_records_sorted` and `test_framework_yamls_load` run, **then** both pass (lexicographic order per FR-032; unique IDs; valid shape).
- **Given** a reject/defer disposition, **when** the feature closes, **then** that ID is absent from the catalog and the rationale is on Issue #185 (no silent drop).

**Priority**: P0 | **Effort**: M

### US-2: The 67 CWE-Blocked Edges Return
**When** I consume `crosswalk.yaml` to map OWASP categories — across any of the six tracked lists — (or T1070.006/T1562) onto CWE,
**I want** the T029-removed CWE-target edges restored byte-exact for every added target record,
**So I can** rely on the crosswalk's published-mapping coverage instead of hitting freeze-era gaps.

**Acceptance Criteria**:
- **Given** the `e58f247` blob, **when** the restore-set is extracted, **then** it contains exactly the 67 target-CWE-missing edges (filter, not full diff — the 1 other-drift edge, 20 non-CWE-target edges, and 25 dedupe collapses stay out) and is committed as `specs/185-*/restored-edges.yaml` **before** catalog edits.
- **Given** the restored crosswalk, **when** `test_crosswalk_referential_integrity` and `test_crosswalk_loads` run, **then** both pass (no dangling endpoint, no duplicate tuple, ≥500 primary floor — expected 541 → 608 primary).
- **Given** restoration, **then** original `edge_type`/`confidence`/`citation` are byte-identical to the pre-removal blob, and the 2 #186-deferred edges are present.

**Priority**: P0 | **Effort**: S

### US-3: Integrity and Decision Trail Stay Intact
**When** records are added and edges restored,
**I want** the integrity suite green at every step and every ID disposition recorded,
**So that** the crosswalk never regresses into a dangling state and no audit question is left open.

**Acceptance Criteria**:
- **Given** every change, **when** `tests/schemas/test_taxonomy_integrity.py` runs, **then** all **5** functions pass.
- **Given** the 40 IDs, **when** the feature closes, **then** 40/40 have an add/reject/defer line on Issue #185, including the Category/Pillar policy rationale.
- **Given** the final state, **when** `/aod.analyze` runs, **then** no inconsistency is reported.

**Priority**: P0 | **Effort**: S

---

## Functional Requirements

### FR-1: Architect Per-ID Disposition for the 40 Missing CWE IDs (Gate)
**Description**: Before any file edit, the architect verifies each ID against the authoritative MITRE CWE source and publishes an add/reject/defer disposition on Issue #185. **Lead posture: add all 40** (verified-real, published IDs backing published mappings).

**Scope**:
- IDs (exactly these 40, derived 2026-06-11 from the blob diff): `CWE-16, 73, 201, 213, 255, 256, 259, 260, 295, 307, 311, 312, 319, 326, 327, 359, 489, 520, 521, 540, 565, 601, 611, 614, 693, 732, 798, 799, 829, 915, 916, 937, 1035, 1039, 1104, 1174, 1269, 1357, 1426, 1427`.
- Authoritative source: `https://cwe.mitre.org/data/definitions/<N>.html` (FR-8 canonical URL convention). Bulk name harvest MUST use the **comprehensive `cwec_latest.xml` dictionary download** (the full CWE corpus) — NOT per-view CSVs (e.g., View-1000/Top-25 exports), which **omit Category entries** and would false-reject CWE-16/255/937/1035 *(architect C3 + team-lead C2, folded v1.1)*. Per-page spot-checks supplement.
- Output: one line per ID — `add` / `reject` (mistranscribed or deprecated) / `defer` — on Issue #185.

**Business Rules**:
- **Category/Pillar policy** (the one real decision): CWE-16, CWE-255, CWE-937, CWE-1035 are Categories; CWE-693 is a Pillar. Default = **add with fidelity-first rationale** (catalog = citation-resolution layer; OWASP publishes these IDs; CWE-200/CWE-284 precedent in the existing 53; rejecting CWE-693 re-strands a #186-deferred edge). If the architect instead rejects any, the corresponding edges stay out and Success Criteria adjust — the plan MUST handle any add-set ⊆ 40 without rework.
- A `deprecated` CWE entry (none expected) → reject or defer, never added.
- Record shape stays frozen — no `abstraction`/category annotation field (that would be a schema change); Category status MAY be noted in the catalog header comment.

### FR-2: Add Approved Records to `cwe.yaml`
**Description**: For each "add" ID, insert a record harvested from the MITRE CWE publication.

**Changes**:
- `schemas/taxonomy/cwe.yaml` — records with shape `{id, full_id, name, url}`; **`cwe_refs` omitted entirely** (FR-003 / ADR-027 Decision 1: CWE→CWE relations live only in `crosswalk.yaml`); `full_id` follows the existing `CWE-<N>` convention used by the current 53; `name` exactly as published (no paraphrase — F-180 R7 name-contamination tripwire); `url` = `https://cwe.mitre.org/data/definitions/<N>.html`.
- Insert in **lexicographic `id` order** (FR-032 Python string-sort semantics: e.g., `CWE-1035 < CWE-1039 < … < CWE-16 < CWE-201`); `test_records_sorted` enforces.
- **Name verification is scripted, not sampled**: an all-40 name-diff of the inserted records against the `cwec_latest.xml` harvest runs in the verification wave (code-reviewer), supplementing per-page spot-checks — the R7 failure mode is silent (names aren't test-verified) *(team-lead C4, folded v1.1)*.
- Extend the `cwe.yaml` header comment with an F-A1.2 provenance block (mirroring the existing 41+11+1 composition note): source = T029 drift-edge targets, Issue #185, retrieval date — **including Category/Pillar status annotations** for CWE-16/255/937/1035/693 (architect's OQ-2 resolution).
- Update `schemas/taxonomy/README.md` §3.5 (composition, final record count 53 → 93 or actual add-set size, retrieval date) and any other count-bearing lines found by grep at build.

### FR-3: Restore the 67 CWE-Blocked Edges to `crosswalk.yaml`
**Description**: Reconstruct and restore **only** the 67 target-CWE-missing edges from the pre-removal blob — filter, never the full T029 diff.

**Scope (empirically pinned at definition)**:
- **Recovery source**: dangling commit `e58f247` (`git show e58f247:schemas/taxonomy/crosswalk.yaml` — post-normalize, pre-removal; verified present 2026-06-11). `991e1ee` is the post-removal reference for the diff.
- **Filter**: removed-edge set (88) → keep only `target.taxonomy == cwe` AND `target.id` ∉ current 53 → **67 edges** (65 `owasp→cwe`, 2 `mitre-attack→cwe`). Restore the subset whose target ID is in the FR-1 add-set (expected: all 67).
- **Byte-exact**: original `edge_type` (all `primary`), `confidence` (34h/32m/1l), `citation` preserved unmodified.
- **Checked-in artifact first**: commit the extracted restore-set as `specs/185-cwe-catalog-expansion/restored-edges.yaml` (schema contract mirroring `specs/186-.../contracts/restored-edges.schema.md`) **as the first build task, in parallel with — not gated on — the FR-1 disposition** (extraction is disposition-independent; running it immediately closes the dangling-object window) *(team-lead C3, folded v1.1)*.
- **Explicitly NOT restored**: the 1 cwe-target other-drift edge, the 20 non-CWE-target removals, the 25 dedupe collapses, and any edge whose target ID got reject/defer.

**Business Rules**:
- 0 tuple collisions and 0 same-endpoint cross-type duplicates verified against today's 578 (2026-06-11); **re-verify at build** before insertion (dedupe key: `source.taxonomy+source.id+target.taxonomy+target.id+edge_type`; near-key: same minus edge_type).
- No edge restored before its target record lands — sequencing inside the build must keep `test_crosswalk_referential_integrity` green at every commit.
- Monotonic: edge count only grows (578 → ~645; primary 541 → ~608; ≥500 floor untouched).

### FR-4: Keep the Taxonomy Integrity Suite Green
**Description**: `tests/schemas/test_taxonomy_integrity.py` (**5 functions**) is the structural acceptance gate after every change: `test_framework_yamls_load` (shape/uniqueness/URL — accommodates the cwe.yaml no-`cwe_refs` exception), `test_records_sorted`, `test_crosswalk_referential_integrity`, `test_crosswalk_loads` (no dupes; ≥500 primary floor), `test_citation_shape` (restored citations are OWASP/MITRE URLs — pass by construction).

### FR-5: Documentation & Closure
**Scope**:
- CHANGELOG: `feat(185): cwe.yaml expansion + 67 drift-edge restoration (F-A1.2)`.
- Issue #185: FR-1 disposition comment; close `stage:done` at delivery.
- `specs/180-.../NEXT-SESSION.md`: mark the T029 CWE-blocked residual resolved by #185 (completing the trail #186 started); note the F-A1.2 entry alongside the existing F-A1.3 note.
- README §3.5 + cwe.yaml header per FR-2.
- **`crosswalk.yaml` header "Edit lineage" block**: append the F-185 restoration line (mirroring the existing T029/F-186/F-184 lineage entries) *(architect C4, folded v1.1)*.
- **ADR-037 D-7 annotation**: 5 of the 8 CWEs in ADR-037's D-7 substitution table (CWE-307, 311, 319, 326, 732) enter the catalog with this feature — annotate D-7 that the substitution rationale is partially superseded (annotation only; **no baseline regeneration**) *(architect C2, folded v1.1)*.

---

## Non-Functional Requirements

### Backward Compatibility
- **No schema change, no ADR.** `cwe` is in the taxonomy enum since ADR-027 v1; record shape `{id, full_id, name, url}` and the no-`cwe_refs` rule are untouched; restoration is monotonic — consumers see more records and more edges, never different shapes. (Mirrors #186's verified pattern; contrast #184's enum expansion.)

### Determinism
- Records are transcriptions of published MITRE data (no generation); edges are byte-recovered from the `e58f247` blob, not re-authored. The restore-set artifact makes the reconstruction reproducible without dangling objects.

### Integrity (core NFR)
- FR-030 referential-integrity strictness is inviolable at every intermediate state — the same guarantee that motivated the original removal governs the restoration sequencing (records before edges).

### Maintainability
- The 40-ID disposition converts the largest open T029 question into a settled, cited decision; header + README provenance keeps the 53→93 lineage legible next to the seed/Top-25 notes.

---

## Success Metrics
- **Disposition completeness**: 40/40 IDs with documented, source-verified decisions on Issue #185.
- **Catalog**: `cwe.yaml` 53 → 93 records (add-all expectation; otherwise 53 + add-set), exact published names, sorted, shape-clean.
- **Crosswalk**: +67 edges (578 → 645 total; 541 → 608 primary; ≥500 floor intact); 0 dangling; 0 drift/dedupe re-introduction; the 2 #186-deferred edges restored.
- **Integrity**: 5/5 test functions green; `/aod.analyze` clean.
- **Trail closure**: Issue #185 closed; F-180 NEXT-SESSION updated; #186 residual marked complete.

---

## Scope & Boundaries

### In Scope (P0)
- Architect 40-ID disposition incl. the Category/Pillar policy call (FR-1).
- Adding the add-set records to `cwe.yaml` + header/README provenance (FR-2).
- Restoring the 67 CWE-blocked edges byte-exact via early checked-in restore-set (FR-3).
- Integrity suite green throughout (FR-4); CHANGELOG + trail closure (FR-5).

### Out of Scope
- **The 1 cwe-target other-drift edge and 20 non-CWE-target T029 removals** — correctly removed or already dispositioned by #186; restoring them would re-introduce drift.
- **The 25 dedupe collapses** — duplicates by definition.
- **Net-new edge authoring** beyond the 67 (e.g., `related`/`superseded` edges *to* the 40 new records, or ChildOf/PeerOf CWE↔CWE hierarchy edges) — future tranche per the #182 cadence; Issue #185's "future related/superseded expansion" framing points there, not here.
- **`cwe_refs` population on CWE records** — permanently excluded by FR-003/ADR-027 Decision 1, not deferred.
- **Re-verification or re-titling of the existing 53 records**; **CWE Top 25 2026 refresh** (README §6 maintenance playbook owns that); **#183 link-rot checking**.
- **Schema/ADR changes, new enum values, new taxonomies** — none required.
- **`abstraction`/Category-annotation fields on records** — would be a schema change; header-comment note at most.

### Assumptions
- Dangling commits `e58f247`/`991e1ee` remain in the local object DB until the restore-set artifact is committed (verified present 2026-06-11; the artifact step then removes the dependency — same mitigation #186 used).
- `cwe.mitre.org` definition pages / list download remain fetchable at build time (F-180 retrieved all 53 from the same source 2026-04-17; no R7-style anti-bot tripwire known for CWE pages).
- The OWASP citation URLs on the 67 edges are still live enough for `test_citation_shape` (URL-shape check only — no HTTP fetch; #183 owns link-rot).

### Constraints
- FR-030 referential integrity at every step; FR-032 lexicographic sort; ≥500 primary floor; frozen record shape; F-180 R7 exact-name discipline.

---

## Risks & Dependencies

### Technical Risks

**Risk 185.1 — Dangling-commit recovery fails (objects GC'd / fresh clone) before extraction.**
- **Likelihood**: Low (verified present 2026-06-11) | **Impact**: High (FR-3 source lost)
- **Mitigation**: Extract and commit `restored-edges.yaml` as the **first build task** (proven #186 pattern). After that commit, FR-3 has no dangling-object dependency.

**Risk 185.2 — Name contamination on 40 harvested records (the F-180 R7 failure mode).**
- **Likelihood**: Medium | **Impact**: Medium (catalog credibility; silent test pass — names aren't test-verified)
- **Mitigation**: Single-source bulk harvest from the comprehensive `cwec_latest.xml`; **scripted all-40 name-diff** of inserted records vs the XML in the verification wave (code-reviewer) — not a sample; per-page spot-checks for the 5 Category/Pillar + 3 AI CWEs on top; no paraphrasing *(strengthened per team-lead C4)*.

**Risk 185.3 — Category/Pillar policy reversal shrinks the add-set and strands edges.**
- **Likelihood**: Low | **Impact**: Medium (up to ~10 of the 67 edges stay out; CWE-693 rejection would re-strand a #186-deferred edge)
- **Mitigation**: FR-1 lead posture (fidelity-first, CWE-200/284 precedent) with explicit rationale; plan handles any add-set ⊆ 40 without rework; rejected-ID edges get recorded rationale (no silent drop).

**Risk 185.4 — Over-restore re-introduces T029 drift (the #186 R2 analog).**
- **Likelihood**: Low | **Impact**: Medium
- **Mitigation**: FR-3 mandates the 67-edge filter (not the 88/113 diff); the 1 other-drift + 20 non-CWE edges are named exclusions; build re-runs the collision check (0 today); code-reviewer confirms no excluded edge returns.

**Risk 185.5 — Baseline shift between definition and build (another feature lands on `crosswalk.yaml`).**
- **Likelihood**: Low (Wave 2 siblings done; #183 touches no edges) | **Impact**: Low
- **Mitigation**: Build re-derives the diff and collision check from the blobs + live files (script pattern preserved in the PRD evidence); numbers are re-pinned at plan.

### Dependencies
- **Internal (all DELIVERED)**: F-180 (blobs + integrity test + NEXT-SESSION SHAs), #186 (restore mechanism + artifact contract + the 2-edge deferral), #184 (current 8-catalog baseline), #182 (the 37 `related` edges — 0 overlap verified).
- **External**: `cwe.mitre.org` (record names/URLs at build); `pyyaml` + pytest (existing toolchain; note system python lacks pyyaml — use `uv run --no-project --with pyyaml` or the test venv). No new tooling.

---

## Definition of Done
- [ ] 40/40 IDs dispositioned on Issue #185 (add/reject/defer + Category/Pillar rationale), verified against MITRE CWE (FR-1).
- [ ] Add-set records in `cwe.yaml`: exact published names, canonical URLs, no `cwe_refs` key, lexicographic position; header provenance block added (FR-2).
- [ ] `schemas/taxonomy/README.md` §3.5 updated (composition + count + retrieval date) (FR-2).
- [ ] `specs/185-cwe-catalog-expansion/restored-edges.yaml` committed **before** catalog/crosswalk edits, containing exactly the 67 filtered edges + schema contract (FR-3).
- [ ] All add-set-target edges restored byte-exact; 2 #186-deferred edges present; rejected/deferred-ID edges out with rationale; 0 excluded T029 edges re-introduced (FR-3).
- [ ] `tests/schemas/test_taxonomy_integrity.py` 5/5 green at delivery (and at every build commit touching the data files) (FR-4).
- [ ] No schema/ADR change (verified); record shape and enum untouched.
- [ ] Scripted all-40 name-diff vs `cwec_latest.xml` run clean in the verification wave (FR-2).
- [ ] `crosswalk.yaml` header "Edit lineage" carries the F-185 line; ADR-037 D-7 annotated (5/8 substitution CWEs now cataloged; no baseline regen) (FR-5).
- [ ] `/aod.analyze` passes; CHANGELOG `feat(185)` entry present.
- [ ] F-180 `NEXT-SESSION.md` trail updated; #186 residual (2 edges) marked closed (FR-5).
- [ ] Issue #185 closed `stage:done`.

---

## Open Questions
- [ ] **Final add-set** — resolved by FR-1 architect disposition at `/aod.plan`/`/aod.build` (lead expectation: 40/40 add; **posture endorsed by architect at definition review**). — architect — Open (gate before edits).
- [x] **Header annotation for Category-type records** — **RESOLVED at definition review (architect)**: annotate Category/Pillar status for CWE-16/255/937/1035/693 in the cwe.yaml header comment (folded into FR-2).

### Resolved at Definition (empirical derivation 2026-06-11)
- [x] **Exact counts** → 88 T029 semantic removals; **67** CWE-blocked (65 owasp + 2 mitre-attack); **40** unique missing IDs; 1 other-drift + 20 non-CWE excluded.
- [x] **#186 deferral containment** → both `T1070.006 → CWE-1269` and `T1562 → CWE-693` are in the 67.
- [x] **Restorability** → 0 unresolvable sources, 0 tuple collisions, 0 cross-type near-collisions vs today's 578.
- [x] **Edge attributes** → all primary; 34 high / 32 medium / 1 low confidence; citations OWASP/MITRE URLs.
- [x] **Recovery viability** → `e58f247`/`991e1ee` present in object DB 2026-06-11; filter mechanism proven by #186.
- [x] **Schema/ADR impact** → none (enum + shape untouched; no-`cwe_refs` rule preserved).
- [x] **Test surface** → 5 functions; only floor assertion (≥500 primary) — no exact-count assertions to update.
- [x] **Baseline** → 578 edges (541 primary + 37 related), 8 catalogs, cwe.yaml 53 records.

---

## References

### Product Documentation
- Product Vision: [product-vision.md](docs/product/01_Product_Vision/product-vision.md)
- GitHub Issue: [#185](https://github.com/davidmatousek/tachi/issues/185)
- Strategy: `_internal/strategy/BLP-05-framework-mapping-and-output-fidelity.md` §Wave 2 / F-2 *(internal, gitignored)*
- Triad review records: `.aod/results/architect.md`, `.aod/results/team-lead.md` (2026-06-11)
- Sibling PRDs: [186-mitre-catalog-expansion](186-mitre-catalog-expansion-2026-06-07.md) (mechanism + deferral), [184-nist-ai-600-1-surface-c-transcription](184-nist-ai-600-1-surface-c-transcription-2026-06-10.md) (baseline)

### Technical Documentation
- ADR-027 — Taxonomy Crosswalk Schema (enum, record/edge shape, Decision 1 no-`cwe_refs`) — *referenced, unchanged*
- Integrity test: `tests/schemas/test_taxonomy_integrity.py` (5 functions; ≥500 primary floor)
- Catalogs: `schemas/taxonomy/cwe.yaml` (53), `schemas/taxonomy/crosswalk.yaml` (578: 541p/37r), `schemas/taxonomy/README.md` §3.5
- F-180 recovery record: `specs/180-taxonomy-crosswalk-collection/NEXT-SESSION.md` (SHAs `e58f247`/`991e1ee`)
- #186 artifact pattern: `specs/186-mitre-catalog-expansion/restored-edges.yaml` + `contracts/restored-edges.schema.md`
- Authoritative CWE source: `https://cwe.mitre.org/data/definitions/<N>.html`

---

## Approval & Sign-Off

| Role | Name | Status | Date | Comments |
|------|------|--------|------|----------|
| Product Manager | product-manager | ✅ Approved | 2026-06-11 | Author sign-off; empirical 67/40 derivation; standalone (last Wave-2 item); v1.1 folds in all Triad corrections |
| Architect | architect | 🟡 Approved with Concerns | 2026-06-11 | Derivation re-verified exact; no-schema/no-ADR true; add-all-40 endorsed; 4 concerns (OWASP 6-family wording, ADR-037 D-7, cwec XML source, header lineage) folded into v1.1; no re-review before /aod.plan |
| Team Lead | team-lead | 🟡 Approved with Concerns | 2026-06-11 | Deps verified merged; O/R/P 0.5/0.75/1.0d; 5 in-scope concerns folded into v1.1; W0→W1→W2 wave plan proposed |

---

## Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-06-11 | product-manager | Initial PRD (BLP-05 Wave 2, F-A1.2). Issue #185 estimates upgraded to empirical counts via `e58f247`/`991e1ee` blob diff: 67 edges / 40 IDs exact; #186 2-edge deferral containment verified; 0-collision restorability verified. |
| 1.1 | 2026-06-11 | product-manager | Folded in Triad review (both APPROVED_WITH_CONCERNS). Architect: 65 OWASP edges span **6 families** (22 A0x / 14 Mobile / 12 LLM / 9 ML / 5 ASI / 3 API), not Top 10:2021 alone; ADR-037 D-7 annotation added to FR-5; harvest source pinned to comprehensive `cwec_latest.xml` (per-view CSVs omit Categories); crosswalk header lineage line added; OQ-2 resolved (annotate Category status). Team-Lead: timeline → O/R/P **0.5/0.75/1.0 day** (floor requires scripted harvest); restore-set extraction parallel to disposition; scripted all-40 name-diff in verification wave; #185 sequenced before #183. |
