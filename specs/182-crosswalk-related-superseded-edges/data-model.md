# Data Model: Crosswalk `related` + `superseded` Edge Expansion (F-182)

**Feature**: [spec.md](spec.md) · **Date**: 2026-06-07

No new schema. All entities reuse the ADR-027-frozen crosswalk-edge shape; this feature only populates two already-authorized `edge_type` values and adds two feature-local artifacts. Listed here for `/aod.tasks` traceability.

---

## Entity 1 — `related` edge (production payload)

A `crosswalk.yaml` record with `edge_type: related` connecting two taxonomy items beyond their primary mapping.

| Field | Type | Constraint |
|---|---|---|
| `source.taxonomy` | enum(7) | closed 7-value taxonomy enum (ADR-027 D3) |
| `source.id` | string | MUST resolve to a record in the catalog named by `source.taxonomy` |
| `target.taxonomy` | enum(7) | closed 7-value taxonomy enum |
| `target.id` | string | MUST resolve in the catalog named by `target.taxonomy` |
| `edge_type` | const | `related` |
| `confidence` | enum(3) | `high` \| `medium` \| `low`, assigned per anti-drift rule (FR-005) |
| `citation` | string | non-empty; URL-shaped (`^https?://`) or resolvable repo-relative path |

**Validation rules**:
- Endpoints resolve (FR-010 referential integrity).
- Drawn only from an audited source class (Entity 3); floor-counted edges exclude OWASP-LLM→CWE (FR-003/FR-004).
- `high`/`medium` only with a one-sentence supporting citation (FR-005, FR-014); else `low`.
- CWE↔CWE citations carry Nature + View ID (FR-006).
- 5-tuple `(source.taxonomy, source.id, target.taxonomy, target.id, edge_type)` unique (FR-010). A `related` edge for a pair that already has a `primary` edge is allowed (edge_type differs); a duplicate `related` for the same pair is forbidden.

**Count constraint**: ≥80, band 80–150, 150 hard ceiling (FR-001) — or documented achievable floor (FR-002).

## Entity 2 — `superseded` edge (production payload, opportunistic)

A `crosswalk.yaml` record with `edge_type: superseded` expressing old-item → newer-item lineage. Same field shape as Entity 1 with `edge_type: superseded`.

**Validation rules**:
- Authorable ONLY where **both** endpoints already resolve under current catalogs (FR-007).
- Set MAY be empty — an empty authored set with documented deferral is a valid outcome (US2-AC3, SC-004).
- Catalog-gated remainder recorded in the deferred-set disposition (Entity 5).

## Entity 3 — Audited source class (curation methodology)

A provenance category for `related` edges with a known publication status and confidence ceiling. Documented in the README rubric extension (FR-009); not a data record.

| Source class | Published? | Confidence ceiling | Endpoint catalogs (both must resolve) |
|---|---|---|---|
| CWE ↔ CWE | yes (view-dependent) | `high` | `cwe.yaml` ↔ `cwe.yaml` |
| OWASP-Web Top 10 → CWE | yes (counted list) | `high` | `owasp.yaml` → `cwe.yaml` |
| ATLAS → ATT&CK | yes (`ATT&CK-reference`) | `high` | `mitre-atlas.yaml` → `mitre-attack.yaml` |
| OWASP-LLM Top 10 → ATLAS | yes (Reference Links) | `medium`–`high` | `owasp.yaml` → `mitre-atlas.yaml` |
| OWASP-LLM Top 10 → CWE | **no** (prose only) | `low` (excluded from floor) | `owasp.yaml` → `cwe.yaml` |

## Entity 4 — Reference-edges artifact (build input, checked-in)

`specs/182-crosswalk-related-superseded-edges/reference-edges.yaml` — the harvested candidate relations + citations captured **before** any `crosswalk.yaml` edit (FR-012). Shape defined in [contracts/reference-edges.schema.md](contracts/reference-edges.schema.md). The audit evidence base for FR-014.

## Entity 5 — Deferred-set disposition (build output, checked-in)

`specs/182-crosswalk-related-superseded-edges/deferred-superseded.md` — one line per deferred relationship class (superseded, and any deferred related class) with a rationale pointing to its follow-on (FR-008). MUST exist even if the authored `superseded` set is empty.

---

## State transitions (candidate relation lifecycle)

```
harvested (reference-edges.yaml)
   ├─► authored      → written to crosswalk.yaml (edges resolve, confidence calibrated)
   ├─► downgraded    → authored at a weaker confidence (anti-drift audit, FR-014)
   ├─► deferred      → recorded in deferred-superseded.md (endpoints don't both resolve)
   └─► rejected      → excluded (e.g., OWASP-LLM→CWE at high/medium; >150 ceiling surplus)
```

## Acceptance oracle

The 5-function `tests/schemas/test_taxonomy_integrity.py` suite is the structural gate (FR-013): `test_framework_yamls_load`, `test_crosswalk_loads` (uniqueness + ≥500 primary floor), `test_crosswalk_referential_integrity` (endpoints resolve, enums closed), `test_citation_shape` (shape only), `test_records_sorted` (catalogs only — not the crosswalk). The anti-drift citation audit (FR-014) is the **content** gate that the shape-only suite cannot enforce.
