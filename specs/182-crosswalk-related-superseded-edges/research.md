# Research Summary: Crosswalk `related` + `superseded` Edge Expansion (F-182)

**Date**: 2026-06-07 · **Feature**: [spec.md](./spec.md) · **PRD**: `docs/product/02_PRD/182-crosswalk-related-superseded-edges-2026-06-07.md`

This research grounds the spec in the verified current state of the crosswalk subsystem and refines the PRD's source-class taxonomy with an authoritative-publication audit.

---

## Knowledge Base Findings

- **KB Entry 13 (F-186, 2026-06-07)** — *Extract recovery source to a checked-in artifact BEFORE any edit when restoration depends on unreachable history.* Applies if #182 references a pre-existing edge set; capture the harvested source relations to a checked-in artifact (e.g., `specs/182-*/reference-edges.yaml`) before editing `crosswalk.yaml`.
- **KB Entry 6 (F-292)** — *Pin each edge to the primary CWE that best matches the semantic relationship*, not inherited from a parent category; *document boundary navigation explicitly* when a `related` edge connects frameworks that both cite the same control.
- **KB Entry 4 (F-3)** — *CHANGELOG sibling-h3 cluster placement* for multi-feature initiatives → `### Crosswalk related/superseded edge expansion (BLP-05 F-3 #182)`.
- **F-180 lesson** — the `≥500 primary` floor and 5-test integrity suite were the merge gate; the `related`/`superseded` enum values were frozen authorized-but-unused for exactly this follow-on (no schema migration).

## Codebase Analysis

| Artifact | Path | Key fact |
|---|---|---|
| Crosswalk | `schemas/taxonomy/crosswalk.yaml` | **542 primary, 0 related, 0 superseded** (verified 2026-06-07) |
| Integrity test | `tests/schemas/test_taxonomy_integrity.py` | `EDGE_TYPE_ENUM` L33, `CONFIDENCE_ENUM` L35, `PRIMARY_EDGE_FLOOR=500` L47; 5 test functions |
| README rubric | `schemas/taxonomy/README.md` | confidence rubric L128–141, anti-drift rule L139 |
| ADR-027 | `docs/architecture/02_ADRs/ADR-027-taxonomy-crosswalk-schema.md` | freezes schema; `related`/`superseded` authorized-but-unused |
| F-180 contracts | `specs/180-taxonomy-crosswalk-collection/contracts/` | `crosswalk-edge.yaml`, `catalog-record.yaml` formal shapes |

**Edge shape** (per ADR-027 D2): `source{taxonomy, id}` → `target{taxonomy, id}` + `edge_type` + `confidence` + `citation`.
**Uniqueness key** (5-tuple, test L207–220): `(source.taxonomy, source.id, target.taxonomy, target.id, edge_type)` — `edge_type` is part of the key, so the same source→target pair may carry both a `primary` and a `related`/`superseded` edge.

**Catalog record counts** (the referential-integrity gate — every endpoint must resolve here):

| Catalog | Records | Catalog | Records |
|---|---|---|---|
| `owasp.yaml` | 60 | `mitre-attack.yaml` | 701 |
| `mitre-atlas.yaml` | 36 | `nist-ai-rmf.yaml` | 72 |
| `cwe.yaml` | **53** | `tachi-control-category.yaml` | 8 |
| `tachi-stride-ai-category.yaml` | 11 | | |

The **53-record `cwe.yaml`** is the binding constraint for CWE-targeted `related` edges: a published CWE↔CWE or OWASP→CWE relationship is only *authorable* if the target CWE is one of the 53 already in the catalog (FR-011 referential integrity). Catalog expansion to admit more CWEs is BLP-05 **Wave 2 #185** territory, not #182.

**5 integrity tests** (all must stay green; no test change): `test_crosswalk_loads` (uniqueness + ≥500 primary floor), `test_crosswalk_referential_integrity` (endpoints resolve, enums closed), `test_citation_shape` (non-empty, URL-shaped or resolvable repo path), `test_records_sorted` (catalogs lexicographically sorted by id), record-shape validation.

## Architecture Constraints

- **ADR-027 is frozen and additive-safe**: the 3-value `edge_type` enum and the integrity test already accept `related`/`superseded`. #182 is data-only — **no schema change, no test change, no new ADR** (consistent with F-186 FR-008).
- **≥500 primary floor is unaffected**: #182 only *adds* non-primary edges; it never downgrades an existing `primary` edge.
- **Catalog sort applies to catalogs, not the crosswalk**: `test_records_sorted` validates the 7 catalog YAMLs only; `crosswalk.yaml` is not sort-gated today. Uniqueness (the 5-tuple) is the real backstop against duplicate authoring.

## Industry Research — Authoritative-Publication Audit (refines PRD source classes)

The PRD names three `related` source classes. An audit of what each authority actually *publishes* refines the confidence ceilings and surfaces one asymmetry + one bonus lane:

| Edge class | Authoritative source | Published? | Confidence ceiling | Citation to capture |
|---|---|---|---|---|
| **CWE ↔ CWE** | cwe.mitre.org Relationships + XML/CSV views | **Yes** (view-dependent) | **high** | Nature + View ID (e.g., `CWE-89 ChildOf CWE-943, View-1000`) |
| **OWASP Web Top 10 → CWE** | owasp.org/Top10 category pages | **Yes** (explicit counted list) | **high** | category page (A03:2021 = 33 CWEs; A05:2025 = 37) |
| **OWASP LLM Top 10 → CWE** | genai.owasp.org pages | **NO** (prose only, no structured list) | **low / inferred** | none authoritative — community repos only |
| **OWASP LLM Top 10 → ATLAS** | genai.owasp.org "Reference Links" | **Yes** (ATLAS IDs cited) | **medium–high** | LLM page Reference Links (e.g., LLM01 → AML.T0051/T0054) |
| **MITRE ATLAS → ATT&CK** | atlas-data `ATT&CK-reference` field | **Yes** (first-class field, 34 techniques) | **high** | ATLAS id + `ATT&CK-reference.id` + dataset version |

**Three calibration takeaways for the README rubric extension and anti-drift discipline:**
1. **OWASP-LLM→CWE is the drift trap.** It *feels* publishable (blogs widely repeat "LLM05 → CWE-79/89/78") but OWASP itself publishes no structured CWE list on the LLM pages. Such edges must be marked `low`/inferred — this is exactly where invented-but-plausible edges sneak in. OWASP-**Web**→CWE, by contrast, is a high-confidence lane (explicit counted lists).
2. **CWE parent edges are view-dependent** (CWE-89's parent is CWE-943 in View-1000 vs CWE-74 in View-1003). The citation MUST record the View ID, or two "correct" citations will appear to contradict.
3. **Bonus high-confidence lane:** OWASP-LLM→ATLAS edges are published in the LLM pages' Reference Links — a citable bridge into the AI-specific framework that the original three source classes didn't name.

## Recommendations for Spec

- **Frame the floor as survey-conditional with a yield-tripwire** (PRD §Proposed Solution): committed floor `≥80`, target band `80–150`, `150` hard ceiling. If the high/medium core cannot clear 80, document the achievable floor with rationale rather than pad with `low` edges (anti-drift over floor-hitting). Triad high-conf core estimate ≈ 65.
- **Constrain `related` edges to the five audited published source classes**, with confidence ceilings per the audit above; forbid `high`/`medium` where no one-sentence citation supports it (FR-013 anti-drift).
- **Make `superseded` opportunistic, not floored:** author only pairs whose *both* endpoints already resolve under current catalogs; document the catalog-gated deferred set (one line per deferred class → follow-on). The set may be small or empty.
- **Extend the README rubric** with `related`/`superseded` calibration examples + the authoritative-source list (incl. the OWASP-LLM→CWE trap and the View-ID rule).
- **Keep the 5-test suite green; no schema/test/ADR change; ≥500 primary floor preserved.** Mirror F-186 FR-008's no-migration discipline.
- **Capture the harvested source relations to a checked-in artifact** before editing `crosswalk.yaml` (KB Entry 13).

---

## Plan Phase: Decisions (Phase 0)

Decisions resolving every Technical-Context unknown. Format: Decision / Rationale / Alternatives rejected.

- **D1 — Constrain `related` edges to four audited published source classes** (CWE↔CWE, OWASP-Web→CWE, ATLAS→ATT&CK, OWASP-LLM→ATLAS). *Rationale*: each is a citable, published relation that satisfies the anti-drift rule's `high`/`medium` bar; the publication audit confirmed their status. *Alternatives rejected*: (a) include OWASP-LLM→CWE at `high`/`medium` — rejected, prose-only on official pages (drift trap); (b) free-form curator-judged edges — rejected, violates "harvest, don't invent."
- **D2 — Survey-first, spike-conditional floor with a yield-tripwire** (FR-002). *Rationale*: the achievable `high`/`medium` yield is catalog-gated and not knowable until the source classes are harvested against the 53-record `cwe.yaml` / 36-record `mitre-atlas.yaml`; committing a fixed count before the survey risks either padding (anti-drift breach) or a missed floor. *Alternatives rejected*: a hard ≥120 floor (PRD v1.0) — lowered to ≥80 because the high-confidence core estimate is ~65; a no-floor "author what you find" — rejected, gives no committed deliverable.
- **D3 — Capture harvested candidates to a checked-in `reference-edges.yaml` before any `crosswalk.yaml` edit** (FR-012, KB Entry 13). *Rationale*: makes authoring reproducible and audit-traceable; the survey output is the audit's evidence base. *Alternatives rejected*: author directly from live web fetches — rejected, non-reproducible and un-auditable.
- **D4 — `superseded` is opportunistic, not floored** (FR-007/008). *Rationale*: referential integrity (FR-010) only admits pairs whose both endpoints already resolve; most lineage pairs need historical records that are catalog-expansion (Wave 2) territory. *Alternatives rejected*: add historical records to author more superseded edges — rejected, out of scope (catalog expansion = #184/#185); silently drop the deferred set — rejected, FR-008 requires recorded disposition.
- **D5 — Pure additive data change: no schema/test/ADR/ADR-027 change** (FR-011). *Rationale*: the `edge_type` enum and the 5-test integrity suite already authorize `related`/`superseded` (ADR-027 frozen); the `≥500 primary` floor is untouched (only non-primary edges added). *Alternatives rejected*: extend the test to enforce a `related` floor — rejected, scope creep + couples data volume to the structural gate; bump `schema_version` — rejected, no shape change.
- **D6 — CWE↔CWE citations record Nature + View ID** (FR-006). *Rationale*: CWE parents are view-dependent (CWE-89→CWE-943 in View-1000 vs CWE-74 in View-1003); omitting the view makes two correct citations look contradictory. *Alternatives rejected*: cite only the CWE page URL — rejected, ambiguous across views.

**Unknowns remaining**: 1 — the exact achievable `high`/`medium` count and per-class composition. Modeled as a **build-start survey gate (FR-002)**, not a planning blocker; the plan tolerates a yield-tripwire outcome (documented achievable floor) without rework.
