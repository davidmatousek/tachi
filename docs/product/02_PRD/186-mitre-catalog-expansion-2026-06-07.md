---
prd:
  number: "186"
  topic: mitre-catalog-expansion
  created: 2026-06-07
  status: Approved
  type: feature
triad:
  pm_signoff: { agent: product-manager, date: 2026-06-07, status: APPROVED, notes: "Author sign-off. Scope matches Issue #186 (F-A1.3) restated against current catalog reality and the Triad's empirical findings: F-241 already added all 3 ATT&CK IDs + 7 of 13 ATLAS IDs, so the concrete deliverable is the 10 now-resolvable MITRE-scoped T029 drift edges + an architect add/reject/defer disposition for 6 still-missing ATLAS IDs. Scoped standalone (not bundled with #184/#185) per the user's /aod.define 186 invocation and the BLP-05 split-valve sanction. v1.1 folds in all three architect + three team-lead corrections." }
  architect_signoff: { agent: architect, date: 2026-06-07, status: APPROVED_WITH_CONCERNS, notes: "Mechanism empirically proven — restored the 10 MITRE-scoped edges to a temp copy, integrity suite 5/5 green, 0 collisions. 'No schema change / no ADR' verified true. 3 must-fix-at-plan precision fixes (all folded into v1.1): (A) suite is 5 functions not 6; (B) F-180 squash-merged — recover from dangling SHAs e58f247/991e1ee, extract restore-set to a checked-in artifact early; (C) T029 removed ~113 edges (multi-cause) not 16, MITRE-scoped=18, now-resolvable=10, residual=6 ATLAS-blocked + 2 CWE-blocked (defer #185). No design defects; no re-review required before /aod.plan. Details: .aod/results/architect.md" }
  techlead_signoff: { agent: team-lead, date: 2026-06-07, status: APPROVED_WITH_CONCERNS, notes: "Feasible; deps verified clear (F-180 + F-241 both DELIVERED; siblings #184/#185 disjoint write-sets; #311 closed). Revised effort 0.25-0.5 -> 0.4-0.75 day (0.25 floor unrealistic — reconstruction filtering is ~1-2h). 3 concerns (1 MED, 2 LOW): C1 reconstruction under-described (pin commit e58f247, filter to the MITRE-ID edges, exclude the ~97 semantic-drift/dedupe removals); C2 baseline numbers (526 edges confirmed, 5 test functions); C3 add-set likely small (already handled). Agent plan: W0 architect gate -> W1 senior-backend-engineer -> W2 tester+code-reviewer. Details: .aod/results/team-lead.md" }
source:
  idea_id: 186
  story_id: null
---

# MITRE ATT&CK + ATLAS Catalog Expansion — Residual Drift-Edge Restoration (F-A1.3)

**Status**: Approved
**Created**: 2026-06-07
**Author**: product-manager
**Reviewers**: architect, team-lead
**Priority**: P1 (Moderate) — BLP-05 Wave 2 (Crosswalk Catalog Expansion)
**Evidence**: Issue [#186](https://github.com/davidmatousek/tachi/issues/186) (`follow-on-180`), filed at Feature 180 T034. Root analysis: F-180 `specs/180-taxonomy-crosswalk-collection/` (T029 drift disposition, `NEXT-SESSION.md`, spec FR-030). Empirical Triad verification (2026-06-07): see `.aod/results/architect.md` + `.aod/results/team-lead.md`. Strategic home: `_internal/strategy/BLP-05-framework-mapping-and-output-fidelity.md` §Wave 2 / F-2.

---

## Executive Summary

### The One-Liner
Restore the **10 MITRE-scoped crosswalk edges** that Feature 180's T029 cleanup removed and whose endpoints F-241 has since made resolvable, and give the architect an explicit add/reject/defer disposition for the **6 ATLAS technique IDs still missing** from `mitre-atlas.yaml` — so `crosswalk.yaml` regains its restorable MITRE coverage without ever breaking the referential-integrity gate.

### Problem Statement
Feature 180 (F-A1, Taxonomy Crosswalk Collection, PR #181) shipped `crosswalk.yaml` plus seven frozen taxonomy catalogs, gated by `tests/schemas/test_taxonomy_integrity.py`. At **T029** the engineer ran a multi-cause cleanup that removed **~113 primary edges** (≈88 semantic-drift + ≈25 dedupe, per the F-180 task record). A subset of those removals existed *because* the edges referenced technique IDs absent from the frozen MITRE catalogs: per **FR-030** (referential-integrity strictness — every edge's `source.id`/`target.id` MUST resolve in the catalog named by its `taxonomy`), those edges were removed rather than allowed to dangle. The union of missing IDs that triggered the *MITRE-endpoint* removals was **16 IDs**:

- **13 ATLAS IDs**: `AML.T0000, T0001, T0003, T0005, T0011, T0016, T0025, T0029, T0034, T0037, T0040, T0043, T0048`
- **3 ATT&CK IDs**: `T1190, T1565.001, T1557`
- (with `AML.T0043 → T1190` a *dual-dangling* edge — both endpoints missing)

> **Precision note (Triad-verified):** "16" is an **ID count**, not an edge count. The MITRE-scoped removed-edge set is **18 edges** (15 `mitre-atlas → mitre-attack` + 3 `mitre-attack → cwe`). Earlier framing that conflated "16" with the edge count is corrected here.

Issue #186 was filed to expand the two catalogs and restore those edges. **The catalog landscape has since changed materially.** Feature **241** (web-api-coverage-attestation, delivered 2026-05-01) independently expanded both MITRE catalogs against the authoritative MITRE source:

- **ATLAS: 12 → 30 records** (T038/T039 — phase-complete expansion from `mitre-atlas/atlas-data`)
- **ATT&CK: → 701 records** (T040–T043 — tactical-grouping expansion)

Cross-referencing the 16-ID gap against the **current** catalogs (verified 2026-06-07):

| Original gap | Count | Status now |
|---|---|---|
| ATT&CK IDs (T1190, T1565.001, T1557) | 3 | ✅ **all present** in `mitre-attack.yaml` |
| ATLAS IDs (T0000, T0003, T0011, T0016, T0029, T0034, T0040) | 7 | ✅ **present** in `mitre-atlas.yaml` |
| ATLAS IDs (T0001, T0005, T0025, T0037, T0043, T0048) | 6 | ❌ **still missing** |

So **most of the catalog-record gap is already closed** — but **F-241 added catalog *records*, not crosswalk *edges*.** `crosswalk.yaml` still sits at **526 primary edges** (88 ATLAS edges, 174 ATT&CK edges) and **none of the 18 MITRE-scoped T029-removed edges has been restored**. Resolving the 18 against today's catalogs (architect PoC, 2026-06-07):

- **10 edges are now resolvable** — both endpoints exist (9 of the 15 `atlas→attack` whose ATLAS source F-241 added, + 1 of the 3 `attack→cwe`). **This is the concrete #186 deliverable** (architect restored them to a temp copy → 536 edges, integrity suite 5/5 green, 0 collisions).
- **8 edges remain blocked**: **6** by the still-missing ATLAS IDs (gated on the FR-1 disposition; includes the `T0043 → T1190` dual, whose ATT&CK end already resolves), and **2** by missing **CWE** targets (`T1070.006 → CWE-1269`, `T1562 → CWE-693`) — these depend on **#185 (cwe.yaml)**, not on the 6 ATLAS IDs, and are **deferred to #185**.

Left unaddressed, the crosswalk under-connects exactly the framework — MITRE ATT&CK/ATLAS — that downstream AI-security tooling pivots through, undercutting BLP-05's "machine-readable source-of-truth" thesis. And the open 6-ID question lingers as un-closed F-180 decision-trail debt.

### Proposed Solution
A small, integrity-gated, data-layer feature in two ordered moves:

1. **Architect ID disposition (gate before any edit).** The architect re-verifies each of the **6 still-missing ATLAS IDs** against the authoritative MITRE ATLAS source (`mitre-atlas/atlas-data` `techniques.yaml` — the same source F-241 used; note `atlas.mitre.org` per-technique pages 404 via WebFetch per the F-180 R7 tripwire) and publishes an ID-by-ID **add / reject / defer** disposition as a comment on Issue #186. **Expected outcome skews reject/defer** — F-241's phase-complete `atlas-data` expansion *deliberately excluded* these 6 — so the 6-ID exercise is primarily about **decision-trail closure**, not edge yield. Implementation proceeds on the "add" set only.
2. **Catalog + crosswalk update.** Add any approved ATLAS records to `mitre-atlas.yaml` (preserving record shape, the seed/external grouping, and lexicographic sort). Then **restore exactly the 10 now-resolvable MITRE-scoped edges** (plus any unblocked by step 1), reconstructed **byte-exact from F-180 git history** so original `edge_type`/`confidence`/`citation` are preserved.

The integrity suite (**5 functions**: `test_framework_yamls_load`, `test_crosswalk_loads`, `test_crosswalk_referential_integrity`, `test_citation_shape`, `test_records_sorted`) must stay **5/5 green** at every step — it is the structural guarantee that no edge dangles and no record breaks shape/sort. **No schema change and no ADR**: `mitre-atlas`/`mitre-attack` are already in the 7-value taxonomy enum, so this is purely additive records + edge restoration (contrast #184, which expands the enum and touches ADR-027).

### Success Criteria
- Each of the 6 still-missing ATLAS IDs has a documented add/reject/defer disposition on Issue #186, verified against the authoritative `atlas-data` source.
- Every "add"-disposition ATLAS record is present in `mitre-atlas.yaml` with full record shape (`id, full_id, name, url, cwe_refs`) and in correct lexicographic position.
- The **10 now-resolvable MITRE-scoped edges** are restored to `crosswalk.yaml` (reconstructed from F-180 git history → 526 grows to ≥536); the 2 CWE-blocked edges remain out (deferred to #185); reject/defer-ID edges remain out with rationale recorded.
- `tests/schemas/test_taxonomy_integrity.py` is **5/5 green**: referential integrity holds, records stay sorted, the ≥500 primary-edge floor holds, no duplicate edges.
- `/aod.analyze` passes; CHANGELOG carries a `feat(186)` entry; Issue #186 closed with its decision trail intact.

### Timeline
Estimated **0.4–0.75 day** (revised up from a 0.25–0.5 day draft per Team-Lead review — the 0.25-day floor is unrealistic once the edge-reconstruction *filtering* is done correctly). The cost is dominated by (a) the architect's 6-ID verification against `atlas-data` (~1.5–2.5h) and (b) **filtering** the 10 MITRE-scoped edges out of the ~113-edge T029 removal and reconstructing them byte-exact (~1–2h). The actual file edits are small; the integrity test makes correctness self-checking (~1s feedback loop).

---

## Strategic Alignment

### Product Vision Alignment
**Reference**: [product-vision.md](docs/product/01_Product_Vision/product-vision.md)

Tachi's differentiator is reasoning over architecture for both STRIDE and AI-specific threats, and emitting that reasoning as machine-readable artifacts (SARIF, the framework crosswalk). The crosswalk is what lets a tachi finding pivot to an authoritative MITRE ATT&CK or ATLAS technique ID — the lingua franca other security tools already speak. A crosswalk with silently-removed MITRE edges quietly narrows that pivot surface. Restoring the resolvable edges (and closing the 6-ID decision) makes the differentiator more *connected* without adding any new surface to maintain.

### Roadmap Fit
This is **Wave 2 of BLP-05 (Framework Mapping & Output Fidelity)** — specifically one of the three split-valve components of **F-2 (Taxonomy Catalog Expansion)**, alongside #184 (NIST AI 600-1 GAI Risk) and #185 (`cwe.yaml` expansion). BLP-05's thesis: tachi's output becomes more *precise* (Wave 1, MAESTRO Model B #311 — delivered v4.41.0), more *connected* (Wave 2, this), and *integrity-gated* (Wave 3, #182/#183). Per the blueprint, the three Wave-2 taxonomies are independent and parallelizable, and catalog expansion is "the most likely split candidate." **This PRD honors that split: it scopes #186 (MITRE) standalone** — disjoint write set from #184 (`nist-ai-rmf` + ADR-027) and #185 (`cwe.yaml`), so all three are genuinely parallelizable.

### Predecessor Relationship
| Feature / Issue | Relationship |
|---|---|
| 180 (F-A1 Taxonomy Crosswalk Collection, PR #181) | Built `crosswalk.yaml` + frozen catalogs + the FR-030 integrity test; **T029 removed the edges this PRD restores**. Squash-merged to `8b7c7bf` — recovery is from dangling task-commits (FR-3). Parent of #186. |
| 241 (web-api-coverage-attestation) | Independently expanded ATLAS 12→30 (T038/T039) and ATT&CK→701 (T040–T043) from authoritative MITRE source — **made 10 of the 18 MITRE-scoped edges resolvable** and proved the `atlas-data` harvesting path this PRD reuses. |
| ADR-027 (Taxonomy Crosswalk Schema) | Defines the 7-value taxonomy enum and record/edge shape. **Unchanged by #186** (additive records within the existing `mitre-atlas`/`mitre-attack` enum values). |
| 311 (BLP-05 Wave 1, MAESTRO Model B) | Sibling wave; the MAESTRO output thread. Independent — closed, never touched `crosswalk.yaml`. |
| 184 / 185 (BLP-05 Wave 2 siblings) | The other two split-valve taxonomies. **#185 owns the 2 CWE-blocked edges** this PRD defers. Independent; scoped to separate PRDs. |

---

## Target Users & Personas

### Primary Persona: Downstream AI-Security Tool / Analyst Consuming the Crosswalk
- **Role**: An engineer or tool that ingests tachi's framework crosswalk to map a finding onto MITRE ATT&CK/ATLAS technique IDs.
- **Goal**: Pivot reliably from a tachi finding to the authoritative MITRE technique catalog and onward (detections, mitigations, reporting).
- **Pain Point**: T029-removed edges mean some legitimate MITRE pivots silently don't exist in the crosswalk — the consumer can't tell "no such relationship" from "removed for integrity."

**Why This Matters**: BLP-05 positions tachi as the upstream machine-readable contract. Missing edges in the *most widely-consumed* framework (MITRE) erode that contract precisely where adopters lean on it most.

### Secondary Persona: Tachi Taxonomy Steward / Maintainer
- **Role**: Maintainer responsible for crosswalk integrity and the F-180 decision trail.
- **Goal**: Close the open T029 follow-on cleanly — every removed MITRE edge either restored or explicitly, durably dispositioned (reject/defer with rationale).
- **Pain Point**: The 6-ID question is unresolved F-180 debt; without an explicit add/reject/defer record it resurfaces on every future crosswalk audit.

**Why This Matters**: A documented disposition converts a recurring "are these IDs real?" question into a settled, cited decision — the maintainability win (and the main value of the 6-ID exercise, since it likely yields few or zero edges).

---

## User Stories

### US-1: Crosswalk Regains Its Resolvable MITRE Edges
**When** I consume `crosswalk.yaml` to map a tachi finding onto MITRE ATT&CK/ATLAS,
**I want** the T029-removed MITRE edges whose endpoints now exist to be present again,
**So I can** rely on the crosswalk's MITRE coverage rather than hit silent gaps left by an integrity cleanup.

**Acceptance Criteria**:
- **Given** the catalogs as they stand today, **when** the feature completes, **then** exactly the **10 now-resolvable MITRE-scoped edges** are restored to `crosswalk.yaml` (not the broader ~113-edge T029 removal — see FR-3).
- **Given** the restored crosswalk, **when** `test_crosswalk_referential_integrity` runs, **then** it passes (no dangling endpoint).
- **Given** the restored crosswalk, **when** `test_crosswalk_loads` runs, **then** the primary-edge floor (≥500) still holds and no duplicate edge is introduced.

**Priority**: P0 | **Effort**: S

### US-2: The 6 Missing ATLAS IDs Get an Explicit Disposition
**When** I (or a future auditor) ask "what happened to the 6 ATLAS IDs T029 flagged?",
**I want** an ID-by-ID add/reject/defer decision verified against the authoritative ATLAS source,
**So I can** trust that the gap is settled, not silently ignored.

**Acceptance Criteria**:
- **Given** the 6 IDs (T0001, T0005, T0025, T0037, T0043, T0048), **when** the architect verifies each against `mitre-atlas/atlas-data`, **then** each receives a documented disposition (add / reject / defer) with a one-line rationale on Issue #186. *(Expected: mostly reject/defer, given F-241's phase-complete expansion excluded them.)*
- **Given** an "add" disposition, **when** the record is added, **then** it carries full shape (`id, full_id, name, url, cwe_refs`) and sits in correct lexicographic order (`test_framework_yamls_load` + `test_records_sorted` pass).
- **Given** a "reject"/"defer" disposition, **when** the feature closes, **then** its edge stays removed and the rationale is recorded (no silent drop).

**Priority**: P0 | **Effort**: S

### US-3: Integrity Stays Green Throughout
**When** records are added and edges restored,
**I want** the taxonomy integrity suite to remain the gate,
**So that** the crosswalk can never regress into a dangling-edge state.

**Acceptance Criteria**:
- **Given** every change in this feature, **when** `tests/schemas/test_taxonomy_integrity.py` runs, **then** all **5** test functions pass.
- **Given** the final state, **when** `/aod.analyze` runs, **then** it reports no inconsistency.

**Priority**: P0 | **Effort**: S

---

## Functional Requirements

### FR-1: Architect ID-by-ID Disposition for the 6 Missing ATLAS IDs (Gate)
**Description**: Before any file edit, the architect verifies each still-missing ATLAS ID against the authoritative source and publishes an add/reject/defer disposition. **Lead posture: verify-and-expect-reject/defer**, not "add" — F-241 already excluded these 6 from a phase-complete `atlas-data` expansion.

**Scope**:
- IDs in scope (exactly these 6, verified missing on 2026-06-07): `AML.T0001, AML.T0005, AML.T0025, AML.T0037, AML.T0043, AML.T0048`.
- Authoritative source: `https://raw.githubusercontent.com/mitre-atlas/atlas-data/main/data/techniques.yaml` (primary; the same source F-241 used). MISP-galaxy as secondary. **Do not rely on `atlas.mitre.org` per-technique pages** — they 404 via WebFetch (F-180 R7 tripwire, client-side anti-bot gating, not URL instability).
- Output: an Issue #186 comment with one line per ID: `add` (resolvable on `atlas-data`) / `reject` (invented or mistranscribed pre-T029) / `defer` (legitimate but not yet published).

**Business Rules**:
- The "add" set may be empty (→ feature is purely the 10-edge restoration) or up to 6. The plan must handle the full range without rework.
- Even adding all 6 unblocks at most 6 more `atlas→attack` edges; the value of this requirement is **decision-trail closure / auditability** (US-2), not edge yield.
- `AML.T0043` and its `T0043 → T1190` dual edge: the ATT&CK endpoint `T1190` already resolves, so this edge's restorability hinges solely on the T0043 disposition.

### FR-2: Add Approved ATLAS Records to `mitre-atlas.yaml`
**Description**: For each "add"-disposition ID, add a catalog record harvested from `atlas-data`.

**Changes**:
- `schemas/taxonomy/mitre-atlas.yaml` — insert records with shape `{id, full_id, name, url, cwe_refs}`. `full_id` follows the `ATLAS-AML.TXXXX` convention; `cwe_refs: []` (ATLAS publishes no direct CWE refs); `url` is `https://atlas.mitre.org/techniques/AML.TXXXX` (regex-valid per the test; no HTTP fetch performed). The optional F-241 fields (`out_of_scope`, `out_of_scope_rationale`) are permitted but not required — the record-shape test allows extras on catalog records.
- Insert in **lexicographic `id` order** (`test_records_sorted`), and extend the catalog header comment to record the F-A1.3 expansion provenance (mirroring the existing F-241 expansion note).

**Business Rules**:
- Names must match the authoritative `atlas-data` publication exactly (the F-180 R7 note documents a prior name-contamination incident — do not re-introduce speculative labels).
- No re-titling of the existing 30 records (a separate name-reverification follow-on already exists per the ATLAS header note — out of scope here).

### FR-3: Restore the 10 Now-Resolvable MITRE-Scoped Edges to `crosswalk.yaml`
**Description**: Reconstruct and restore **only** the 10 MITRE-scoped T029-removed edges whose `source` and `target` now both resolve — **filtered out of** the broader ~113-edge T029 removal. Restoring the full T029 diff would re-introduce the exact semantic-drift the cleanup fixed.

**Scope (Triad-pinned to remove ambiguity)**:
- **Recovery source**: F-180 was squash-merged (`8b7c7bf` is the only `crosswalk.yaml` commit on `main`). The pre-removal state is recoverable **only from the dangling task-commits** in the local object DB, whose SHAs are in `specs/180-taxonomy-crosswalk-collection/NEXT-SESSION.md`:
  - `e58f247` — pre-semantic-removal blob (the recovery *source*, where the 16-ID edges still exist)
  - `991e1ee` — post-removal blob
- **Extraction = filter, not full diff**: from the `e58f247` blob, select **only** edges whose `source.id`/`target.id` is in the 16-ID set **and** now resolves in its catalog — yielding the **10** edges (9 `atlas→attack` + 1 `attack→cwe`). Preserve original `edge_type`, `confidence`, `citation` byte-exact. Do **not** restore the ~97 non-MITRE / semantic-drift / dedupe removals, and do **not** restore the 70 `owasp→cwe`/`control→nist` removed edges.
- **Mitigation against object-DB loss**: extract the 10-edge restore-set into a **checked-in artifact** (e.g., `specs/186-*/restored-edges.yaml`) **early in the build**, so FR-3 no longer depends on dangling objects surviving a `git gc` or a fresh clone.
- **Residual (explicitly out)**: 6 ATLAS-blocked edges (gated on FR-1) + **2 CWE-blocked edges** (`T1070.006 → CWE-1269`, `T1562 → CWE-693`) — the latter **deferred to #185**, not restorable by #186.

**Business Rules**:
- Restored edges must not collide with existing edges (dedupe key: `source.taxonomy + source.id + target.taxonomy + target.id + edge_type`) — architect PoC confirmed **0 collisions** against the current 526.
- No edge may be restored with a dangling endpoint — `test_crosswalk_referential_integrity` is the hard gate.
- Restoration only *increases* the edge count (526 → ~536); the ≥500 floor is unaffected.

### FR-4: Keep the Taxonomy Integrity Suite Green
**Description**: `tests/schemas/test_taxonomy_integrity.py` is the structural acceptance gate; it must pass after every change.

**Scope** (the **5** enforced invariants / test functions):
- `test_framework_yamls_load` — every new record has `{id, full_id, name, url}` + `cwe_refs` (list of `^CWE-\d+$`), unique `id`, URL-shaped `url`.
- `test_records_sorted` — ATLAS records remain lexicographically sorted by `id`.
- `test_crosswalk_referential_integrity` — every restored edge's endpoints resolve; enums closed.
- `test_crosswalk_loads` — no duplicate edges; ≥500 primary-edge floor holds; no extra fields.
- `test_citation_shape` — restored edges' citations are URL-shaped or resolve to a repo file.

### FR-5: Documentation & Closure
**Description**: Record the decision trail and close the issue cleanly.

**Scope**:
- CHANGELOG `feat(186)` entry summarizing records added (likely 0–few) and the 10 edges restored.
- Issue #186 carries the FR-1 disposition comment; close `stage:done` on delivery.
- Update the F-180 engineer handoff (`specs/180-.../NEXT-SESSION.md`) to point at the #186 resolution (F-180 decision-trail integrity, per the F-180 architect's C2 concern pattern), and note the 2 CWE-blocked edges as #185 scope.

---

## Non-Functional Requirements

### Backward Compatibility
- **No schema change, no ADR.** `mitre-atlas`/`mitre-attack` already exist in the 7-value taxonomy enum (verified against the test's `TAXONOMY_ENUM` and ADR-027); this is additive records + previously-present edges. Existing crosswalk consumers see *more* edges, never different shapes.
- Adding optional ATLAS records and restoring removed edges is monotonic — no existing record or edge is altered or deleted.

### Determinism
- Catalog and crosswalk are static YAML data; no generation step. Edge reconstruction from the `e58f247` blob is exact (byte-recoverable), not re-authored — verified lossless on `edge_type`/`confidence`/`citation`.

### Integrity (the core NFR)
- The crosswalk must **never** be left in a state where `test_crosswalk_referential_integrity` fails — FR-030 strictness is preserved end to end. This is the same guarantee that motivated the original T029 removal; #186 restores edges *only* as their endpoints resolve.

### Maintainability
- The 6-ID disposition closes a recurring audit question with a cited, durable decision.
- The checked-in restore-set artifact (FR-3) makes the reconstruction reproducible without depending on dangling git objects.
- Catalog header provenance note (FR-2) keeps the expansion lineage legible alongside the existing seed/F-241 notes.

---

## Success Metrics
- **Disposition completeness**: 6/6 missing ATLAS IDs carry a documented, source-verified add/reject/defer decision.
- **Edge restoration**: exactly the 10 now-resolvable MITRE-scoped edges restored; 0 dangling edges introduced; 0 semantic-drift/dedupe edges re-introduced.
- **Integrity**: `tests/schemas/test_taxonomy_integrity.py` **5/5** green; `/aod.analyze` clean.
- **No regression**: edge count grows from 526 to ≥536; ≥500 primary floor intact.

---

## Scope & Boundaries

### In Scope (P0)
- Architect add/reject/defer disposition for the 6 still-missing ATLAS IDs (FR-1).
- Adding the "add"-set ATLAS records to `mitre-atlas.yaml` (FR-2).
- Restoring the **10 now-resolvable MITRE-scoped** T029-removed edges to `crosswalk.yaml`, reconstructed from the `e58f247` blob and extracted to a checked-in artifact (FR-3).
- Keeping the integrity suite 5/5 green (FR-4).
- CHANGELOG entry + Issue #186 decision-trail closure (FR-5).

### Out of Scope
- **#184 (NIST AI 600-1) and #185 (`cwe.yaml`)** — the other two BLP-05 Wave-2 split-valve taxonomies; each gets its own PRD. This PRD is MITRE-only.
- **The 2 CWE-target-blocked edges** (`T1070.006 → CWE-1269`, `T1562 → CWE-693`) — MITRE-*sourced* but blocked on missing CWE records → **deferred to #185**, not restorable here.
- **The ~97 non-MITRE / semantic-drift / dedupe edges** T029 removed — those removals were correct; restoring them would re-break the crosswalk.
- **ATT&CK record additions** — all 3 originally-missing ATT&CK IDs already exist (F-241); no `mitre-attack.yaml` record change. (Edges *referencing* them are restored under FR-3.)
- **Re-titling / name re-verification of the existing 30 ATLAS or 701 ATT&CK records** — a separate follow-on already tracks v5.5 ATLAS re-titling; not reopened here.
- **Schema / ADR-027 changes, new enum values, new taxonomies** — none required (contrast #184).
- **Net-new related/superseded edge authoring** — this is restoration, not expansion beyond the T029-removed MITRE set.
- **`atlas.mitre.org` live-fetch tooling** — verification uses the `atlas-data` repo; the 404 behavior is a known WebFetch limitation, not a defect to fix here.

### Assumptions
- The `e58f247`/`991e1ee` dangling commits remain in the local object DB at build time; the FR-3 checked-in-artifact step removes this dependency early. *(If absent on a fresh clone, the restore-set must be re-derived before the objects are GC'd.)*
- The 7 F-241-added ATLAS IDs and 3 ATT&CK IDs are correct as published (F-241 verified them against `atlas-data`); #186 trusts F-241's records.
- `mitre-atlas/atlas-data` `techniques.yaml` remains the authoritative, fetchable ATLAS source.

### Constraints
- FR-030 referential integrity is inviolable at every step.
- Record shape, lexicographic sort, and the ≥500 primary-edge floor are test-enforced.

---

## Risks & Dependencies

### Technical Risks

**Risk 186.1 — The "add" set is empty (record work evaporates).**
- **Likelihood**: Medium-High | **Impact**: Low — this is a *good* outcome, not a failure. The concrete deliverable is the **10-edge restoration**, which is independent of the 6-ID outcome.
- **Mitigation**: FR-3 (the 10 edges) is the guaranteed deliverable regardless. The 6-ID disposition is valuable as a documented decision even when the answer is "reject/defer all 6." No rework risk.

**Risk 186.2 — Over-restoring the full T029 diff re-introduces drift (the primary build risk).**
- **Likelihood**: Medium | **Impact**: Medium — T029 removed ~113 edges for *multiple* reasons; a naive "pre minus post" diff would pull in ~97 edges that were correctly removed (semantic drift + dedupe + non-MITRE), re-breaking the crosswalk.
- **Mitigation**: FR-3 mandates **filtering to the 10 MITRE-ID-endpoint edges** from the `e58f247` blob, not the full diff. `test_crosswalk_referential_integrity` catches dangling re-restores; a `code-reviewer` pass confirms no semantic-drift edge returns. *(Team-Lead C1 — folded into FR-3.)*

**Risk 186.3 — Dangling-commit recovery fails on a fresh clone / post-`git gc`.**
- **Likelihood**: Low-Medium | **Impact**: High (FR-3 becomes impossible) — `e58f247`/`991e1ee` are unreachable from `main` (squash-merge) and are not pushed.
- **Mitigation**: Pin the SHAs in `plan.md`/`tasks.md` and **extract the 10-edge restore-set to a checked-in artifact early in the build** (FR-3), before any `gc`. After that, FR-3 no longer depends on the objects surviving. *(Architect Concern B — folded into FR-3.)*

**Risk 186.4 — A restored edge collides with a current edge.**
- **Likelihood**: Low | **Impact**: Low — architect PoC verified **0 collisions** against the current 526; `test_crosswalk_loads` dedupe check is the backstop.
- **Mitigation**: Diff the reconstructed 10 against the current 526 before insertion; skip any already-present tuple.

### Dependencies
- **Internal**: Feature 180 (the crosswalk + integrity test + dangling-commit history) — DELIVERED. Feature 241 (the catalog records that unblock the 10 edges) — DELIVERED. **#185** owns the 2 deferred CWE-blocked edges.
- **External**: `mitre-atlas/atlas-data` `techniques.yaml` (authoritative ATLAS source); `pyyaml` + pytest (existing toolchain). No new tooling.

---

## Definition of Done
- [ ] Architect has published an add/reject/defer disposition for all 6 missing ATLAS IDs on Issue #186, verified against `atlas-data` (FR-1).
- [ ] Every "add"-set ATLAS record is in `mitre-atlas.yaml` with correct shape, `full_id`, `url`, `cwe_refs`, and lexicographic position (FR-2).
- [ ] The catalog header provenance note records the F-A1.3 expansion (FR-2).
- [ ] The **10 now-resolvable MITRE-scoped edges** are restored to `crosswalk.yaml`, reconstructed byte-exact from `e58f247` and extracted to a checked-in restore-set artifact; the 2 CWE-blocked edges are **not** restored (deferred to #185); reject/defer-ID edges remain out with recorded rationale (FR-3).
- [ ] No semantic-drift or dedupe edge from the broader T029 removal is re-introduced (`code-reviewer` verified).
- [ ] `tests/schemas/test_taxonomy_integrity.py` passes **5/5**: referential integrity, sort, ≥500 floor, no duplicates, citation shape, record shape (FR-4).
- [ ] No `mitre-attack.yaml` record change (all 3 ATT&CK IDs already present); no schema/ADR change (verified).
- [ ] `/aod.analyze` passes with no inconsistencies.
- [ ] CHANGELOG entry: `feat(186): restore 10 MITRE drift edges + residual ATLAS disposition (Issue #186, F-A1.3)`.
- [ ] F-180 `NEXT-SESSION.md` decision-trail updated to point at the #186 resolution; 2 CWE-blocked edges noted as #185 scope (FR-5).
- [ ] Issue #186 closed `stage:done`.

---

## Open Questions

- [ ] **Exact "add" set** — resolved by FR-1 at `/aod.plan`/`/aod.build` (architect verification of the 6 IDs against `atlas-data`). — architect — Open (gate before edits).
- [x] **Edge-reconstruction mechanism** — **RESOLVED by Triad review**: recover from dangling blob `e58f247` (pre-removal), filter to the MITRE-ID-endpoint edges (the 10), extract to a checked-in artifact early; do **not** diff the full ~113-edge removal. *(Architect Concern B + Team-Lead C1.)*
- [x] **Bundling** — **resolved**: scoped standalone (#186 MITRE only), not bundled with #184/#185, per the user's `/aod.define 186` invocation and the BLP-05 split-valve guidance.

### Resolved at Definition
- [x] **Catalog landscape** → cross-referenced 2026-06-07: all 3 ATT&CK IDs + 7/13 ATLAS IDs already present (F-241); MITRE-scoped removed = 18; now-resolvable = 10; residual = 6 ATLAS-blocked + 2 CWE-blocked.
- [x] **Edge vs ID count** → "16" is the missing-ID set; T029 removed ~113 primary edges (multi-cause); the deliverable is the 10 now-resolvable MITRE edges. *(Architect Concern C + Team-Lead C2.)*
- [x] **Test-suite size** → **5** functions (not 6); `5 passed` on `main`. *(Architect Concern A + Team-Lead C2.)*
- [x] **Baseline edge count** → **526** primary edges (confirmed via `yaml.safe_load`). *(Team-Lead C2.)*
- [x] **Schema/ADR impact** → none; `mitre-atlas`/`mitre-attack` already in the enum (contrast #184).
- [x] **ATT&CK scope** → no record change needed; edge-restoration only.

---

## References

### Product Documentation
- Product Vision: [product-vision.md](docs/product/01_Product_Vision/product-vision.md)
- GitHub Issue: [#186](https://github.com/davidmatousek/tachi/issues/186)
- Strategy: `_internal/strategy/BLP-05-framework-mapping-and-output-fidelity.md` §Wave 2 / F-2 *(internal, gitignored)*
- Triad review records: `.aod/results/architect.md`, `.aod/results/team-lead.md`

### Related PRDs / Features
- Feature 180 — Taxonomy Crosswalk Collection (F-A1), PR #181 — `specs/180-taxonomy-crosswalk-collection/` (recovery SHAs in `NEXT-SESSION.md`)
- Feature 241 — Web/API Coverage Attestation (ATLAS 12→30, ATT&CK→701) — `specs/241-web-api-coverage-attestation/`
- Sibling Wave-2 issues: [#184](https://github.com/davidmatousek/tachi/issues/184) (NIST AI 600-1), [#185](https://github.com/davidmatousek/tachi/issues/185) (cwe.yaml — owns the 2 deferred CWE-blocked edges)

### Technical Documentation
- ADR-027 — Taxonomy Crosswalk Schema (7-value enum, record/edge shape) — *referenced, unchanged*
- Integrity test: `tests/schemas/test_taxonomy_integrity.py` (FR-030 enforcement: referential integrity, sort, floor, citation/record shape — **5 functions**)
- Catalogs: `schemas/taxonomy/mitre-atlas.yaml` (30 records), `schemas/taxonomy/mitre-attack.yaml` (701 records), `schemas/taxonomy/crosswalk.yaml` (526 primary edges)
- F-180 spec FR-030: `specs/180-taxonomy-crosswalk-collection/spec.md`
- Authoritative ATLAS source: `https://raw.githubusercontent.com/mitre-atlas/atlas-data/main/data/techniques.yaml`

---

## Approval & Sign-Off

| Role | Name | Status | Date | Comments |
|------|------|--------|------|----------|
| Product Manager | product-manager | Approved | 2026-06-07 | Author sign-off; scope restated against current catalog reality; standalone (#186 MITRE only); v1.1 folds in all Triad corrections |
| Architect | architect | Approved with Concerns | 2026-06-07 | Mechanism empirically proven (10 edges restored → 5/5 green); no schema/ADR; 3 precision fixes (5 functions, dangling-SHA recovery, ~113-edge/10-resolvable framing) folded into v1.1; no re-review required |
| Team Lead | team-lead | Approved with Concerns | 2026-06-07 | Feasible; deps clear; effort 0.4–0.75 day (0.25 floor unrealistic); C1 reconstruction-filtering + C2 baseline numbers folded into v1.1 |

---

## Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-06-07 | product-manager | Initial PRD (BLP-05 Wave 2, F-A1.3). Scope restated against post-F-241 catalog reality: residual = 6 ATLAS IDs + edge restoration. |
| 1.1 | 2026-06-07 | product-manager | Folded in Triad review (both APPROVED_WITH_CONCERNS): test suite 6→**5** functions; "16 edges"→**~113 removed / 18 MITRE-scoped / 10 now-resolvable**; recovery from dangling SHAs `e58f247`/`991e1ee` (squash-merge) with early checked-in restore-set; FR-3 scoped to filter the 10 (not the full diff); **2 CWE-blocked edges deferred to #185**; baseline 526 edges confirmed; effort 0.25–0.5 → **0.4–0.75 day**. |
