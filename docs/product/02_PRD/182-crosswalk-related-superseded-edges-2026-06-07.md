---
prd:
  number: "182"
  topic: crosswalk-related-superseded-edges
  created: 2026-06-07
  status: Approved
  type: feature
triad:
  pm_signoff: { agent: product-manager, date: 2026-06-07, status: APPROVED, notes: "Author sign-off. Scope = BLP-05 Wave 3 (#182), bounded first tranche: a committed floor of high-confidence `related` edges from authoritative published relations + the `superseded` edges authorable under current catalogs (FR-011-gated; may be small/empty, deferral documented). Establishes the edge-authoring pattern + extends the confidence rubric in README; defers the long tail. Standalone (#182 only) per the user's /aod.define 182 invocation; #183 link-rot stays a separate Wave-3 sibling. Honors F-180 Tier-1 discipline + BLP-05 bounding guidance. v1.1 folds in all Triad corrections (both APPROVED_WITH_CONCERNS): baseline 543->542, related floor 120->80 (spike-conditional + yield-tripwire), test_records_sorted is catalog-only (uniqueness is the crosswalk backstop), superseded survey is external-source-driven, #185 CWE-pool sequencing, effort 1-2->1.5-2.5d." }
  architect_signoff: { agent: architect, date: 2026-06-07, status: APPROVED_WITH_CONCERNS, notes: "Architecture sound — additive-only within frozen ADR-027; 'no schema/enum/integrity-test/ADR change' CONFIRMED structurally (enum frozen ADR-027 D4 + test line 33; floor is primary-only; README owns the rubric). 5 accuracy/calibration fixes (all folded into v1.1), none blocking: C1 baseline=542 not 543 (comment-line false positive); C2 test_records_sorted checks only the 7 catalogs, never the crosswalk (crosswalk unsorted today) — uniqueness (edge_type in key) is the real backstop, sort is convention-only; C3 >=120 floor at risk (high-conf core ~65) -> lowered to >=80 + spike-conditional; C4 superseded survey is external-deprecation-source-driven, not a local catalog field scan; C5 number propagation. No design defects; no re-review required before /aod.plan. Details: .aod/results/architect.md" }
  techlead_signoff: { agent: team-lead, date: 2026-06-07, status: APPROVED_WITH_CONCERNS, notes: "Feasible; deps clear (F-180/F-186/F-241 DELIVERED; #184/#185 disjoint write-sets — #182 touches only crosswalk.yaml + README). Effort revised 1-2 -> 1.5-2.5 day (realistic 2.0): #182 is net-new cited authoring (~12x #186's volume @ ~5 min/edge), not #186's byte-exact git-blob reconstruction. 4 concerns (2 MED, 2 LOW, all fix-at-plan): C1 estimate floor; C2 >=120 tight (all 542 existing edges are high/medium, 0 low) -> quota'd floor + survey-checkpoint yield-tripwire, no anti-drift padding; C3 #185 enlarges the CWE pool #182's richest vein draws from -> run in series or freeze a catalog snapshot; C4 make the band-ceiling a hard upward stop. Agent plan: W0 architect (ADR gate) -> W1a web-researcher (harvest) || W1b senior-backend-engineer (author quota'd) -> W2 tester + code-reviewer (integrity 5/5 + anti-drift citation audit). Details: .aod/results/team-lead.md" }
source:
  idea_id: 182
  story_id: null
---

# Crosswalk `related` + `superseded` Edge Expansion — First Tranche (F-A1 Follow-on)

**Status**: Approved (2026-06-07 — PM author sign-off + Architect & Team-Lead APPROVED_WITH_CONCERNS; v1.1 folds in all Triad corrections)
**Created**: 2026-06-07
**Author**: product-manager
**Reviewers**: architect, team-lead
**Priority**: P2 (Light) — BLP-05 Wave 3 (Crosswalk Integrity & Edges)
**Evidence**: Issue [#182](https://github.com/davidmatousek/tachi/issues/182) (`follow-on-180`), filed at Feature 180 T034. Source scope: F-180 spec FR-025 (related/superseded deferral) + PRD §Out of Scope. Strategic home: `_internal/strategy/BLP-05-framework-mapping-and-output-fidelity.md` §Wave 3 / F-3.

---

## Executive Summary

### The One-Liner
Author the **first tranche of `related` edges** (and the `superseded` edges authorable under today's catalogs) into `crosswalk.yaml` — connecting taxonomy items *beyond* their single primary mapping — so the crosswalk answers "what else relates to this?" and "what superseded what?", not just "what is THE primary mapping," all under the existing referential-integrity gate with **no schema and no test change**.

### Problem Statement
Feature 180 (F-A1, Taxonomy Crosswalk Collection, PR #181) shipped `crosswalk.yaml` as a **primary-only** graph. Per **Risk R3 Tier 1**, F-180 scoped itself to the `edge_type: primary` floor (`FR-025`: "≥500 primary edges at merge time; `related` and `superseded` expansion is a follow-on Issue filed on F-A1 PR merge, not part of F-A1 scope") and deferred the other two-thirds of the edge model. Today (verified 2026-06-07):

| `edge_type` | Count |
|---|---|
| `primary` | **542** |
| `related` | **0** |
| `superseded` | **0** |

The `edge_type` enum (`{primary, related, superseded}`) was **frozen at F-180** (ADR-027 / spec FR-012) and `tests/schemas/test_taxonomy_integrity.py` **already validates all three values** — `related` and `superseded` are authorized-but-unused. So the crosswalk's relationship graph is structurally complete but **semantically thin**: it carries exactly one mapping per relationship and cannot express the *additional* cross-references ("OWASP LLM05 also relates to CWE-116, not just its primary CWE-79") or the *historical lineage* ("technique X superseded technique Y") that a richer framework crosswalk provides.

For a consumer pivoting a tachi finding across frameworks, a primary-only crosswalk under-connects the graph: it answers the single best mapping but cannot answer "what's the neighbourhood of related concepts?" — exactly the traversal a downstream AI-security tool, SIEM, or compliance mapper wants when expanding a finding into its full framework context. That under-connection is the gap #182 closes, and it is the lightest of BLP-05's three waves.

### A Material Constraint Discovered at Definition: `superseded` is Catalog-Gated
The integrity test's **referential-integrity rule (F-180 FR-030 / FR-011)** requires that **both** `source.id` and `target.id` of every edge resolve to a record in the catalog YAML named by its `taxonomy` — no dangling endpoints. The seven catalogs hold the **current published item set** of each framework (e.g., `owasp.yaml` carries OWASP LLM Top 10 **:2025**, not :2023; `cwe.yaml` carries 53 records; `mitre-atlas.yaml` 30; `mitre-attack.yaml` 701).

A `superseded` edge expresses *old item → newer item*. Under FR-011, it is **only authorable where both the superseded item and its successor already exist as catalog records.** The issue's own superseded examples — "OWASP list revisions, ATT&CK technique renaming" — predominantly need **historical records that the catalogs do not carry** (OWASP :2023 items, deprecated ATT&CK techniques). Adding those records is **catalog expansion** — the explicit territory of BLP-05 Wave 2 (#184 NIST AI 600-1, #185 `cwe.yaml`, #186 MITRE — delivered), **not** #182 ("purely data-authoring… no schema migration required").

**Consequence**: the bulk of #182's authorable value lives in **`related`** edges. `superseded` edges are authored opportunistically — only the set whose both endpoints already resolve under current catalogs (e.g., a deprecated CWE and its replacement both present in the 53-record `cwe.yaml`; an ATT&CK deprecation pair both present in the 701-record `mitre-attack.yaml`). The catalog-gated remainder is **deferred** to a follow-on (post catalog-expansion), with an explicit, recorded disposition — never silently dropped.

### Proposed Solution
A small, integrity-gated, **data-layer** feature — the bounded "Tier-1" parallel of F-180's own primary-edge floor:

1. **Author a committed floor of `related` edges (the core deliverable).** A committed floor of **≥80** with a target band of **80–150 high-confidence `related` edges** (150 = hard ceiling / balloon valve), drawn from **authoritative published relations** (not invented): CWE↔CWE published relationships (`ChildOf`/`PeerOf`/`CanPrecede` from MITRE CWE data, both ends in the 53-record catalog), OWASP→CWE *beyond-primary* cross-references published on the OWASP category pages, and MITRE ATLAS→ATT&CK technique-realization references published in `atlas-data`. Each edge carries `confidence` per the **anti-drift rule** (FR-013): `high`/`medium` only where a one-sentence citation supports it, else `low`; default `medium` for an inferred one-hop, `low` for two-hop/thematic. The floor is **Day-1-spike-conditional**: a build-start survey validates the achievable high/medium yield from the source classes (Triad estimate: high-confidence core ~65 — CWE↔CWE ~36 + ATLAS→ATT&CK ~15 + OWASP-beyond-primary), and a **yield-tripwire** governs the floor — if the high/medium core cannot clear 80, the achievable floor is documented with rationale rather than padded with low-confidence edges (anti-drift over floor-hitting).
2. **Author the `superseded` edges authorable under current catalogs.** Survey the catalogs for deprecation/replacement pairs where **both** endpoints already resolve; author those as `superseded` edges. Document the catalog-gated deferred set (the "needs historical records" remainder) with a one-line rationale per deferred class → follow-on.
3. **Extend the README confidence/edge-authoring rubric.** F-180's README already documents the 3-value `confidence` rubric + anti-drift rule (FR-031); extend it with **`related`/`superseded`-specific calibration examples** and the authoritative-source list — so future edge authors inherit a settled methodology.
4. **Keep the integrity suite 5/5 green throughout.** No schema change, no new test, no ADR-027 change: the enum and the test already support `related`/`superseded`. The **≥500 primary floor is unaffected** (we only add non-primary edges); uniqueness (`{source, target, edge_type}`) and lexicographic sort must hold at every step.

### Success Criteria
- `crosswalk.yaml` carries **≥80 `related` edges** (committed floor; band 80–150), each sourced from an authoritative published relation, with `confidence` assigned per the anti-drift rule — or, if the high/medium yield falls short of 80, the achievable floor is documented with rationale (anti-drift over padding).
- Every authorable-today `superseded` edge (both endpoints already resolving) is authored; the catalog-gated deferred set is documented with a per-class rationale and a filed follow-on (no silent drop).
- The README confidence/edge-authoring rubric is extended with `related`/`superseded` calibration examples + the authoritative-source list.
- `tests/schemas/test_taxonomy_integrity.py` is **5/5 green**: referential integrity holds (no dangling endpoint), records/edges stay sorted, the ≥500 primary-edge floor holds, no duplicate `{source, target, edge_type}` triple.
- `/aod.analyze` passes; CHANGELOG carries a `feat(182)` entry; Issue #182 closed with its disposition trail intact.

### Timeline
Estimated **1.5–2.5 days** (realistic **2.0**; revised up from a 1–2 day draft per Team-Lead review — #182 is **net-new cited authoring** at ~12× #186's edge volume, ~5 min/edge across harvest → resolve-check → calibrate → cite → sort-insert, ≈10 h + ~5.5 h fixed; #186's 0.4–0.75-day anchor was a byte-exact git-blob reconstruction, the wrong shape to bound net-new authoring). The cost is dominated by **edge sourcing + citation** — harvesting the published CWE/OWASP/ATLAS relations, mapping them onto resolvable catalog IDs, and assigning calibrated `confidence` with a citation per edge. The file edits are mechanical and the integrity test makes correctness self-checking (~1 s feedback loop); the effort is curation, not code.

---

## Strategic Alignment

### Product Vision Alignment
**Reference**: [product-vision.md](docs/product/01_Product_Vision/product-vision.md)

Tachi's differentiator is reasoning over architecture for STRIDE + AI threats and emitting that reasoning as machine-readable artifacts — the framework crosswalk among them. The crosswalk is what lets a tachi finding pivot to an authoritative framework ID. A primary-only crosswalk supports a *single-hop* pivot; `related`/`superseded` edges turn it into a **traversable graph** — the consumer can expand a finding into its full framework neighbourhood and follow historical lineage. That makes the differentiator more *connected* without adding any new agent or surface to maintain.

### Roadmap Fit
This is **Wave 3 of BLP-05 (Framework Mapping & Output Fidelity)** — the integrity/edges wave, F-3. BLP-05's thesis: tachi's output becomes more *precise* (Wave 1, MAESTRO Model B #311 — delivered v4.41.0), more *connected* (Wave 2, catalog expansion — #186 delivered v4.42.0; #184/#185 remain), and *integrity-gated* (Wave 3 — **this**, #182 edges + #183 link-rot). Per the blueprint, Wave 3 is "the lightest wave," independent of Wave 1 and interleavable with Wave 2 — and "cleaning/connecting the collection before expanding it is also valid." This PRD honors the split-valve guidance: it scopes **#182 (edges) standalone**, leaving **#183 (citation link-rot monitoring)** as its own Wave-3 sibling — a distinct discipline (tooling/CI vs data authoring).

### Predecessor Relationship
| Feature / Issue | Relationship |
|---|---|
| 180 (F-A1 Taxonomy Crosswalk Collection, PR #181) | Built `crosswalk.yaml` (primary-only), froze the 3-value `edge_type` enum (ADR-027 / FR-012), and shipped the integrity test that **already validates `related`/`superseded`**. **FR-025 explicitly deferred these edges to this follow-on.** Parent of #182. |
| 241 (web-api-coverage-attestation) | Expanded `mitre-atlas` 12→30 and `mitre-attack`→701 records — **enlarging the resolvable-ID space** from which `related`/`superseded` MITRE edges can be authored. |
| 186 (BLP-05 Wave 2, MITRE catalog expansion) | Sibling wave; restored 16 MITRE *primary* drift edges + dispositioned 6 ATLAS IDs (`mitre-atlas` 30→36, `crosswalk` 526→**542**). Independent; **primary-only** — no overlap with #182's `related`/`superseded` write set. Establishes the "disposition + checked-in artifact" pattern #182 reuses for its deferred-set trail. |
| 184 / 185 (BLP-05 Wave 2 siblings, open) | Catalog (record) expansion. **They add the historical/old records that the catalog-gated `superseded` remainder needs** — so #182's deferred superseded set naturally pairs with them. Independent write sets; scoped to separate PRDs. |
| ADR-027 (Taxonomy Crosswalk Schema) | Defines the 7-value taxonomy enum, the 3-value `edge_type` enum, and record/edge shape. **Unchanged by #182** (uses the already-frozen `related`/`superseded` enum values — additive edges only). |

---

## Target Users & Personas

### Primary Persona: Downstream AI-Security Tool / Analyst Traversing the Crosswalk
- **Role**: An engineer or tool that ingests tachi's framework crosswalk to expand a finding across frameworks.
- **Goal**: Move from a finding's *primary* mapping to its full neighbourhood of related concepts (additional CWEs, sibling techniques, cross-framework analogues) and its historical lineage.
- **Pain Point**: A primary-only crosswalk answers "the one best mapping" but goes silent on "what else relates" — forcing the consumer to re-derive the relationship graph tachi already has the data to express.

**Why This Matters**: BLP-05 positions tachi as the upstream machine-readable contract. A richer, well-cited relationship graph is exactly the higher-order value a single-hop mapping can't provide — and the differentiator the OSS positioning rests on.

### Secondary Persona: Tachi Taxonomy Steward / Maintainer
- **Role**: Maintainer responsible for crosswalk integrity, the F-180 decision trail, and the edge-authoring methodology.
- **Goal**: Close F-180's deferred-edge follow-on cleanly — author the high-confidence/authorable edges now, and leave a documented, cited rubric + a recorded deferral trail for what catalog-gating pushes downstream.
- **Pain Point**: Without a settled `related`/`superseded` calibration rubric and a recorded deferred-set disposition, every future edge-authoring pass re-litigates "what counts as `related` vs `low`-confidence?" and "why aren't the superseded list-revision edges here?"

**Why This Matters**: A documented rubric + disposition converts recurring authoring questions into a settled, cited methodology — the maintainability win, mirroring #186's ID-disposition pattern.

---

## User Stories

### US-1: The Crosswalk Gains a Traversable `related` Graph
**When** I consume `crosswalk.yaml` to expand a tachi finding across frameworks,
**I want** `related` edges connecting each item to its additional, authoritatively-published cross-references (beyond the single primary mapping),
**So I can** traverse the framework neighbourhood of a finding instead of re-deriving it.

**Acceptance Criteria**:
- **Given** the crosswalk after this feature, **when** I filter `edge_type == 'related'` and count, **then** the total is **≥80** (committed floor; band 80–150) — or the achievable high/medium floor is documented with rationale if the yield-tripwire fires.
- **Given** any `related` edge, **when** I inspect it, **then** `source.id`/`target.id` both resolve to catalog records, `confidence` is assigned per the anti-drift rule, and `citation` is a non-empty URL/file that supports the relationship.
- **Given** the crosswalk, **when** `test_crosswalk_referential_integrity` and `test_crosswalk_loads` run, **then** both pass (no dangling endpoint, no duplicate `{source, target, edge_type}` triple, ≥500 primary floor intact).

**Priority**: P0 | **Effort**: M

### US-2: `superseded` Lineage Is Authored Where Authorable, Deferred Where Catalog-Gated
**When** I (or a future auditor) ask "where are the `superseded` edges, and why aren't there more?",
**I want** every authorable-today supersession (both endpoints already records) authored, and the catalog-gated remainder explicitly dispositioned,
**So I can** trust the superseded set is complete *given current catalogs*, not silently thin.

**Acceptance Criteria**:
- **Given** the current catalogs, **when** the feature surveys for deprecation/replacement pairs whose both endpoints resolve, **then** each such pair is authored as a `superseded` edge with a supporting citation.
- **Given** a supersession whose old/new record is **not** in the catalogs, **when** the feature closes, **then** it is recorded in a documented deferred set (per-class rationale: "needs historical records → #184/#185 / follow-on"), not dropped.
- **Given** the authored `superseded` set may be small or empty, **when** that is the outcome, **then** it is a **documented, acceptable** result (the constraint is structural), and US-1 remains the guaranteed deliverable.

**Priority**: P0 | **Effort**: S

### US-3: A Settled Edge-Authoring Rubric + a Green Integrity Gate
**When** edges are authored and a future contributor extends them,
**I want** the README to carry a `related`/`superseded` calibration rubric + authoritative-source list, and the integrity suite to stay the gate,
**So that** edge authoring is reproducible and the crosswalk can never regress into a dangling-edge state.

**Acceptance Criteria**:
- **Given** the README, **when** I look for edge-authoring guidance, **then** I find `related`/`superseded`-specific `confidence` calibration examples and the list of authoritative published-relation sources (extending the existing FR-031 rubric).
- **Given** every change in this feature, **when** `tests/schemas/test_taxonomy_integrity.py` runs, **then** all **5** test functions pass.
- **Given** the final state, **when** `/aod.analyze` runs, **then** it reports no inconsistency.

**Priority**: P0 | **Effort**: S

---

## Functional Requirements

### FR-1: Author the `related`-Edge First Tranche (Core Deliverable)
**Description**: Add `related` edges to `crosswalk.yaml`, sourced from authoritative published relations, to a committed floor of **≥80** (target band 80–150; **150 = hard ceiling**, the upward balloon valve). The floor is **Day-1-spike-conditional + yield-tripwired** (see Business Rules) — the Triad high-confidence core estimate is ~65 edges, so the floor is deliberately set below the 120 first draft to stay clear of anti-drift padding.

**Authoritative source classes** (harvest, do not invent — the F-180 curation discipline):
- **CWE↔CWE published relationships** — `ChildOf` / `PeerOf` / `CanPrecede` / `CanFollow` relations published in MITRE CWE data, where **both** CWEs are among the 53 `cwe.yaml` records. (`confidence: high` — MITRE-published.)
- **OWASP→CWE beyond-primary** — the additional "Mapped CWEs" published on each OWASP category page beyond the one already carried as a `primary` edge, where the CWE resolves in `cwe.yaml`. (`confidence: high`/`medium`.)
- **MITRE ATLAS→ATT&CK realizations** — ATLAS technique → parent/realizing ATT&CK technique references published in `atlas-data`, where both resolve. (`confidence: medium`.)
- **Thematic cross-framework** (OWASP↔ATT&CK/ATLAS, NIST AI RMF↔OWASP) — inferred one-hop (`confidence: medium`) or two-hop/thematic (`confidence: low`), each with a one-sentence-citable rationale.

**Business Rules**:
- **Day-1 spike + yield-tripwire (Team-Lead C2 + Architect C3)**: a build-start survey enumerates the achievable high/medium edges from the source classes. The **quota'd floor** prioritizes the high-confidence core (CWE↔CWE published + ATLAS→ATT&CK + OWASP-beyond-primary); thematic `low`-confidence edges are **capped**, never the bulk. If the survey shows the high/medium core cannot clear **80**, the achievable floor is **documented with rationale** (mirrors F-180's tier-fallback discipline) — the floor flexes down, it is **never** met by padding.
- **Anti-drift rule (FR-013) is binding**: if the author cannot articulate a one-sentence citation supporting `high`/`medium`, downgrade to the weaker label. Note (Team-Lead C2): all 542 *existing* edges are `high`/`medium` (0 `low`) — introducing a `low` band is new for the crosswalk, so `low`-confidence edges must be the deliberate exception, not the floor-filler.
- A `related` edge MUST connect to a target **not already covered by a `primary` edge** for that source (related = *additional* cross-reference), OR express a genuinely distinct relationship; it MUST NOT duplicate an existing `{source, target, edge_type}` triple (uniqueness is the hard, test-enforced backstop — see FR-4).
- Each `related` edge carries the full FR-009 shape `{source: {taxonomy, id}, target: {taxonomy, id}, edge_type: related, confidence, citation}`. (Crosswalk edge ordering is convention-only, **not** test-enforced — see FR-4 C2 note — so insertion position is a readability nicety, not a gate.)

### FR-2: Author Authorable-Today `superseded` Edges; Disposition the Deferred Set
**Description**: Survey the catalogs for supersession pairs authorable under FR-011, author those, and record the catalog-gated remainder.

**Scope**:
- **Survey is external-source-driven (Architect C4)**: catalog records carry **no deprecation field**, so the authorable-supersession set is found by cross-referencing **external deprecation notices** (MITRE CWE deprecation/`ReplacedBy` data; ATT&CK revoked/deprecated-technique notices on `attack.mitre.org`) against the resolvable catalog IDs — *not* by a local scan of catalog YAML fields. A pair qualifies only when the external notice names both an old and a new item **and both already resolve** as catalog records.
- **Author**: every such qualifying supersession (deprecated/renamed item → replacement) where **both** endpoints already resolve in their catalog — e.g., a deprecated CWE + its replacement both in `cwe.yaml`; an ATT&CK deprecation pair both in the 701-record `mitre-attack.yaml`. `edge_type: superseded`, `confidence` per the rule, citation to the authoritative deprecation notice.
- **Disposition (defer)**: for each supersession whose old/new record is **absent** from the catalogs (OWASP :2023→:2025 list revisions, deprecated ATT&CK techniques not in the catalog, etc.), record a one-line entry in a **checked-in deferred-set artifact** (e.g., `specs/182-*/deferred-superseded.md`) with the class, the missing record(s), and the routing (→ #184/#185 catalog expansion, or a new follow-on). Mirrors #186's checked-in disposition trail.

**Business Rules**:
- The authored `superseded` set MAY be **empty** — that is an acceptable, documented outcome (the constraint is structural, not a failure). US-1 (`related`) is the guaranteed deliverable.
- No `superseded` edge may be authored with a dangling endpoint — `test_crosswalk_referential_integrity` is the hard gate.
- If the deferred set is non-trivial and not already covered by #184/#185, file a follow-on Issue (`follow-on-180` label) capturing it — do not lose the trail.

### FR-3: Extend the README Edge-Authoring + Confidence Rubric
**Description**: Extend `schemas/taxonomy/README.md` (which already documents the 3-value `confidence` rubric + anti-drift rule per F-180 FR-031) with `related`/`superseded`-specific guidance.

**Scope**:
- Add `related`/`superseded` **`confidence` calibration examples** (when `medium` vs `low`; the "additional cross-reference vs duplicate-of-primary" rule; the both-endpoints-must-resolve constraint for `superseded`).
- Add the **authoritative-source list** (the FR-1 source classes) so future edge authors inherit the methodology.
- Record the **edge-type composition** after this feature (primary / related / superseded counts) in the README provenance section, mirroring the existing per-framework provenance notes.

### FR-4: Keep the Taxonomy Integrity Suite Green
**Description**: `tests/schemas/test_taxonomy_integrity.py` is the structural acceptance gate; it must pass after every change. **No test, schema, enum, or ADR change.**

**Scope** (the **5** enforced invariants / test functions, all inherited unchanged from F-180):
- `test_crosswalk_referential_integrity` — every new edge's `source.id`/`target.id` resolves; enums (`taxonomy`/`edge_type`/`confidence`) stay closed. **This is the primary #182 gate** (it catches any dangling `related`/`superseded` endpoint).
- `test_crosswalk_loads` — **no duplicate `{source, target, edge_type}` triple** (the real, test-enforced uniqueness backstop — and because `edge_type` is in the key, a `related` edge MAY legally share source+target with an existing `primary` edge); **≥500 primary floor holds** (unaffected — only non-primary edges are added); no extra per-edge fields.
- `test_citation_shape` — every new edge's `citation` is non-empty and URL-shaped or resolves to a repo file (regex-only; no HTTP fetch — ADR-021 determinism).
- `test_records_sorted` — **iterates the 7 catalog YAMLs only; it does NOT touch `crosswalk.yaml`** (Architect C2, file-verified). The crosswalk is **not sort-enforced** today and is not required to be sorted by #182 — edge ordering is a readability convention, not a gate. (Unaffected by #182 regardless, since no catalog *record* changes.)
- `test_framework_yamls_load` — unaffected (no catalog record change in #182).

> **Correction (Architect C2)**: the v1.0 draft wrongly named `test_records_sorted` as a crosswalk-sort backstop. It is catalog-only. The test-enforced crosswalk invariants are **referential integrity** + **`{source, target, edge_type}` uniqueness** + **citation shape** + **≥500 primary floor** — sort is convention-only.

### FR-5: Documentation & Closure
**Description**: Record the disposition trail and close the issue cleanly.

**Scope**:
- CHANGELOG `feat(182)` entry summarizing the `related` count added, the `superseded` count (incl. "0, deferred" if so), and the README rubric extension.
- Issue #182 carries the deferred-superseded disposition summary; close `stage:done` on delivery.
- If a non-trivial deferred set exists and isn't covered by #184/#185, a `follow-on-180` Issue is filed and linked.

---

## Non-Functional Requirements

### Backward Compatibility
- **No schema change, no enum change, no ADR.** `related`/`superseded` are already in the frozen `edge_type` enum (ADR-027 / FR-012) and already validated by the integrity test. This is purely additive edges. Existing crosswalk consumers see *more* edges of *already-defined* types, never different shapes; a `primary`-only consumer that filters `edge_type == 'primary'` is wholly unaffected.
- Additive-only: no existing edge is altered or removed (monotonic edge-count growth).

### Determinism
- The crosswalk is static YAML; no generation step. Citation validation is regex-only (no HTTP fetch), preserving ADR-021 determinism.

### Integrity (the core NFR)
- The crosswalk must **never** be left in a state where `test_crosswalk_referential_integrity` fails. Every `related`/`superseded` edge is authored only where both endpoints already resolve — the same FR-030 strictness that motivated F-180's primary-only Tier-1 floor, now applied to the new edge types.

### Maintainability
- The README rubric extension (FR-3) settles the `related`/`superseded` calibration question with cited examples.
- The checked-in deferred-set artifact (FR-2) makes the catalog-gated remainder reproducible and routable, not lore.
- The anti-drift rule keeps `confidence` honest — no inflation to hit a floor.

---

## Success Metrics
- **`related` connectivity**: ≥80 `related` edges authored (band 80–150; or documented achievable floor if the yield-tripwire fires), each from an authoritative published relation with a calibrated `confidence` + supporting citation; 0 dangling endpoints introduced.
- **`superseded` completeness-given-catalogs**: every authorable-today supersession authored; the catalog-gated remainder dispositioned in a checked-in artifact (no silent drop).
- **Rubric**: README carries `related`/`superseded` calibration examples + authoritative-source list + post-feature edge-type composition.
- **Integrity**: `tests/schemas/test_taxonomy_integrity.py` **5/5** green; `/aod.analyze` clean; ≥500 primary floor intact; no duplicate triple.

---

## Scope & Boundaries

### In Scope (P0)
- Authoring ≥80 high-confidence `related` edges (band 80–150) from authoritative published relations (FR-1).
- Authoring the authorable-today `superseded` edges + dispositioning the catalog-gated remainder in a checked-in artifact (FR-2).
- Extending the README confidence/edge-authoring rubric with `related`/`superseded` guidance + source list (FR-3).
- Keeping the integrity suite 5/5 green — no schema/test/enum/ADR change (FR-4).
- CHANGELOG entry + Issue #182 disposition-trail closure (FR-5).

### Out of Scope
- **#183 (citation-URL link-rot monitoring)** — the other BLP-05 Wave-3 component; a tooling/CI discipline (a link checker), distinct from data authoring. Its own scope; not bundled here per the user's `/aod.define 182` invocation.
- **Catalog (record) expansion** — adding new framework *records* is #184 (NIST AI 600-1), #185 (`cwe.yaml`), #186 (MITRE — delivered). #182 only authors *edges* between records that **already exist**.
- **The catalog-gated `superseded` remainder** — supersessions needing historical/old records the catalogs don't carry (OWASP list revisions, deprecated-technique renames) — **deferred** to pair with catalog expansion (#184/#185) or a filed follow-on. Dispositioned, not authored.
- **The full 1,000–2,000-edge aspiration in one feature** — the issue restates it, but BLP-05's risk register names this the balloon risk; #182 is the bounded first tranche (floor ≥80 related, ceiling 150), with the long tail deferred (the F-180 Tier-1 parallel).
- **Schema / ADR-027 / enum / integrity-test changes** — none required (the enum + test already support `related`/`superseded`).
- **Migrating detection-agent inline citations to cite crosswalk edges** — a separate F-180-noted follow-on (README §"What F-A1 does NOT give you today" #3); not reopened here.

### Assumptions
- The 7 catalog YAMLs are stable at build time; #182 authors edges against the **current** record set. **Sequencing (Team-Lead C3)**: #185 (`cwe.yaml` expansion) enlarges the CWE record pool from which #182's *richest* `related` vein (CWE↔CWE, OWASP→CWE-beyond-primary) draws. To avoid the target pool shifting mid-authoring, **run #182 before #185, OR freeze a catalog snapshot at #182's build-start** and re-survey only if #185 lands first. Write sets are file-disjoint (#182 → `crosswalk.yaml` + `README.md`; #185 → `cwe.yaml`), so they never merge-conflict — the constraint is *yield stability*, not write contention.
- Authoritative published relations (CWE relationship data, OWASP page "Mapped CWEs", `atlas-data` technique references) remain retrievable for citation.
- The ≥80 floor is achievable from the high/medium-confidence source classes (Triad high-conf core estimate ~65 + a modest cited-medium band); if not, the achievable floor is documented with rationale (anti-drift over floor-padding).

### Constraints
- FR-011 / FR-030 referential integrity is inviolable — both endpoints of every edge must resolve.
- Uniqueness (`{source, target, edge_type}`), lexicographic sort, citation shape, and the ≥500 primary floor are all test-enforced and inherited unchanged.
- `confidence` assignment is governed by the binding anti-drift rule.

---

## Risks & Dependencies

### Technical Risks

**Risk 182.1 — Scope creep / edge-count balloon (the primary risk, per BLP-05).**
- **Likelihood**: Medium | **Impact**: Medium — "author more edges" has no natural ceiling; chasing the 1,000–2,000 aspiration would balloon effort and dilute confidence quality.
- **Mitigation**: Bounded floor (≥80) with a target band (80–150, **hard ceiling 150** as the upward balloon valve — Team-Lead C4); the anti-drift rule caps low-confidence padding; the long tail is explicitly deferred. Split-valve at `/aod.plan` if even the band proves heavy. *(F-180 Tier-1 + BLP-05 bounding discipline.)*

**Risk 182.2 — `superseded` authorable set is empty/trivial (record work evaporates).**
- **Likelihood**: Medium-High | **Impact**: Low — this is a *documented, acceptable* outcome, not a failure: the catalogs are current-item sets, so few supersession pairs both resolve.
- **Mitigation**: US-1 (`related`) is the guaranteed deliverable; FR-2's value is the **disposition trail** even when the authored count is 0. No rework risk.

**Risk 182.3 — `confidence` drift / unsupported edges (quality risk).**
- **Likelihood**: Medium | **Impact**: Medium — inferred/thematic edges invite over-confident labels or uncited "relationships."
- **Mitigation**: Binding anti-drift rule (FR-013); every edge requires a one-sentence-citable rationale; `code-reviewer` pass on a sample of `medium`/`low` edges for citation support; `test_citation_shape` enforces non-empty citations.

**Risk 182.4 — Uniqueness collision from same-source/target edges.**
- **Likelihood**: Low | **Impact**: Low — a `related` edge sharing source+target with an existing `primary` edge is legal *only because* `edge_type` is part of the uniqueness key; an edge_type-blind author could think it collides (it doesn't) or could author a true duplicate triple.
- **Mitigation**: Uniqueness key is `{source, target, edge_type}` — coexistence of a `related` and a `primary` edge between the same nodes is explicitly legal; `test_crosswalk_loads` is the hard, test-enforced backstop against a genuine duplicate triple. *(Crosswalk sort is convention-only — not a gate; see FR-4 C2.)*

### Dependencies
- **Internal**: Feature 180 (crosswalk + frozen enum + integrity test) — DELIVERED. Feature 241 + Feature 186 (enlarged MITRE record space) — DELIVERED. **#184/#185** own the historical records the deferred `superseded` remainder needs (independent; disjoint write sets).
- **External**: MITRE CWE relationship data, OWASP category pages, `mitre-atlas/atlas-data` (for citations); `pyyaml` + pytest (existing toolchain). No new tooling.

---

## Definition of Done
- [ ] **≥80 `related` edges** authored in `crosswalk.yaml` (band 80–150, hard ceiling 150), each from an authoritative published relation with calibrated `confidence` + supporting `citation` (FR-1).
- [ ] Day-1 spike + yield-tripwire applied: quota'd to the high/medium core; anti-drift rule honored — no low-confidence padding to hit the floor; if the high/medium set fell short of 80, the achievable floor is documented with rationale (FR-1).
- [ ] Every authorable-today `superseded` edge authored (both endpoints resolving); the catalog-gated remainder dispositioned in a checked-in `specs/182-*/deferred-superseded.md` artifact (FR-2).
- [ ] README extended with `related`/`superseded` `confidence` calibration examples, the authoritative-source list, and the post-feature edge-type composition (FR-3).
- [ ] `tests/schemas/test_taxonomy_integrity.py` passes **5/5**: referential integrity, sort, ≥500 primary floor, no duplicate triple, citation shape (FR-4).
- [ ] **No schema / enum / integrity-test / ADR-027 change** (verified).
- [ ] `/aod.analyze` passes with no inconsistencies.
- [ ] CHANGELOG entry: `feat(182): add crosswalk related + authorable superseded edges (first tranche, Issue #182, F-A1 follow-on)`.
- [ ] If a non-trivial deferred `superseded` set exists outside #184/#185, a `follow-on-180` Issue is filed and linked (FR-5).
- [ ] Issue #182 closed `stage:done` with its disposition trail intact.

---

## Open Questions

- [ ] **Exact `related` source composition + final count** — resolved at `/aod.plan`/`/aod.build` via the Day-1 spike (harvest the published CWE/OWASP/ATLAS relations, map onto resolvable IDs, calibrate confidence). The ≥80 floor is the commitment (yield-tripwired); the band 80–150 (ceiling 150) is the target. — engineer/architect — Open.
- [ ] **`superseded` authorable yield** — resolved at build by surveying the catalogs for resolvable deprecation/replacement pairs. Lead posture: **expect small/empty**, value is the disposition trail. — engineer — Open.
- [ ] **ADR needed?** — Lead position: **no** — ADR-027 already froze the `edge_type` enum and the README already owns the confidence rubric (extended here, not newly decided). Architect to confirm at `/aod.plan` whether the authoring *methodology* warrants a light ADR or is sufficiently covered by ADR-027 + the README extension. — architect — Open (lean no).

### Resolved at Definition
- [x] **Edge-type state** → `crosswalk.yaml` is **542 primary / 0 related / 0 superseded** (verified 2026-06-07 — the "543" a grep false-positive on the header comment line; #186 delivered 526→542); enum + integrity test already support all three.
- [x] **`superseded` catalog-gating** → FR-011 requires both endpoints to be records; catalogs hold current items, so most list-revision supersessions need historical records (→ catalog expansion #184/#185). `related` carries the bulk of #182's value.
- [x] **Schema/test/ADR impact** → none; `related`/`superseded` already in the frozen enum and validated (contrast #184, which expands the enum).
- [x] **Floor unaffected** → the ≥500 *primary* floor is independent of added non-primary edges.
- [x] **Bundling** → scoped standalone (#182 edges only), not bundled with #183 (link-rot tooling), per the user's `/aod.define 182` invocation + BLP-05 split-valve guidance.

---

## References

### Product Documentation
- Product Vision: [product-vision.md](docs/product/01_Product_Vision/product-vision.md)
- GitHub Issue: [#182](https://github.com/davidmatousek/tachi/issues/182)
- Strategy: `_internal/strategy/BLP-05-framework-mapping-and-output-fidelity.md` §Wave 3 / F-3 *(internal, gitignored)*
- Triad review records: `.aod/results/architect.md`, `.aod/results/team-lead.md`

### Related PRDs / Features
- Feature 180 — Taxonomy Crosswalk Collection (F-A1), PR #181 — `specs/180-taxonomy-crosswalk-collection/` (FR-025 defers these edges)
- Feature 186 — MITRE Catalog Expansion (F-A1.3) — `specs/186-mitre-catalog-expansion/` (sibling; primary-only; disposition-trail pattern)
- Sibling Wave-3 issue: [#183](https://github.com/davidmatousek/tachi/issues/183) (citation link-rot monitoring)
- Sibling Wave-2 issues: [#184](https://github.com/davidmatousek/tachi/issues/184) (NIST AI 600-1), [#185](https://github.com/davidmatousek/tachi/issues/185) (`cwe.yaml` — adds historical records the deferred `superseded` set needs)

### Technical Documentation
- ADR-027 — Taxonomy Crosswalk Schema (7-value taxonomy enum, 3-value `edge_type`/`confidence` enums, record/edge shape) — *referenced, unchanged*
- Integrity test: `tests/schemas/test_taxonomy_integrity.py` (FR-030 enforcement — **5 functions**; already validates `related`/`superseded`)
- Crosswalk: `schemas/taxonomy/crosswalk.yaml` (542 primary / 0 related / 0 superseded)
- Catalogs: `schemas/taxonomy/{owasp,mitre-attack,mitre-atlas,nist-ai-rmf,cwe,tachi-control-category,tachi-stride-ai-category}.yaml`
- Edge-authoring rubric: `schemas/taxonomy/README.md` (FR-031 confidence rubric + anti-drift rule — extended by FR-3)
- F-180 spec FR-025 (deferral) / FR-013 (anti-drift rule) / FR-030 (referential integrity): `specs/180-taxonomy-crosswalk-collection/spec.md`

---

## Approval & Sign-Off

| Role | Name | Status | Date | Comments |
|------|------|--------|------|----------|
| Product Manager | product-manager | Approved | 2026-06-07 | Author sign-off; bounded first tranche (≥80 related floor + authorable superseded); standalone (#182 edges only); honors F-180 Tier-1 + BLP-05 bounding; v1.1 folds in all Triad corrections |
| Architect | architect | Approved with Concerns | 2026-06-07 | Additive-only within frozen ADR-027; "no schema/test/ADR change" CONFIRMED; 5 accuracy/calibration fixes folded into v1.1 (542 baseline, test_records_sorted catalog-only, floor 120→80, external superseded survey); no re-review required |
| Team Lead | team-lead | Approved with Concerns | 2026-06-07 | Feasible; deps clear; write-sets disjoint; effort 1.5–2.5 day (realistic 2.0, was 1–2); C2 quota'd floor + tripwire, C3 #185 CWE-pool sequencing, C4 hard ceiling — folded into v1.1 |

---

## Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-06-07 | product-manager | Initial PRD (BLP-05 Wave 3, F-A1 follow-on). Bounded first tranche: ≥120 `related` floor + authorable-today `superseded` + deferred-set disposition. Surfaced the FR-011 `superseded` catalog-gating constraint. No schema/test/ADR change. |
| 1.1 | 2026-06-07 | product-manager | Folded in Triad review (both APPROVED_WITH_CONCERNS). **Architect**: C1 baseline **543→542** (comment-line false positive; #186 delivered 526→542); C2 **`test_records_sorted` is catalog-only** — crosswalk is not sort-enforced, **`{source,target,edge_type}` uniqueness** is the real backstop (FR-4 + Risk 182.4 restated); C3 related floor **120→80** + Day-1-spike-conditional (high-conf core ~65); C4 `superseded` survey is **external-deprecation-source-driven**, not a local catalog field scan. **Team-Lead**: effort **1–2 → 1.5–2.5 day** (realistic 2.0; net-new cited authoring ≠ #186 git-blob reconstruction); quota'd floor + **yield-tripwire** (0 `low` edges exist today); **#185 CWE-pool sequencing** (run #182 first or freeze snapshot); **hard ceiling 150** (upward balloon valve). "No schema/enum/test/ADR change" reconfirmed. |
