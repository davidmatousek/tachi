# Contract: `reference-edges.yaml` Artifact + Integrity Acceptance (F-182)

**Feature**: [../spec.md](../spec.md) · **Date**: 2026-06-07

Two contracts: (A) the shape of the checked-in harvest artifact, and (B) the acceptance invariants the production edits must satisfy.

---

## A. `reference-edges.yaml` artifact shape (FR-012)

A checked-in capture of harvested candidate relations + citations, produced **before** any `crosswalk.yaml` edit. It is the audit evidence base (FR-014) and the authoring source for Wave 1.

```yaml
# specs/182-crosswalk-related-superseded-edges/reference-edges.yaml
survey:
  date: "2026-06-..."                      # harvest date
  catalog_snapshot:                        # the catalog counts authoring is gated against (A1)
    cwe: 53
    mitre-atlas: 36
    mitre-attack: 701
    owasp: 60
  yield:                                   # FR-002 survey result, per source class
    cwe_cwe:            { high: N, medium: N }
    owasp_web_cwe:      { high: N, medium: N }
    atlas_attack:       { high: N, medium: N }
    owasp_llm_atlas:    { high: N, medium: N }
  high_medium_core_total: N                # the floor-eligible total
  tripwire_fired: false                    # true if core < 80 → documented achievable floor
candidates:
  - source: { taxonomy: cwe, id: CWE-89 }
    target: { taxonomy: cwe, id: CWE-943 }
    edge_type: related
    confidence: high
    source_class: cwe_cwe
    citation: "https://cwe.mitre.org/data/definitions/89.html"   # Nature=ChildOf, View-1000
    disposition: authored                  # authored | downgraded | deferred | rejected
```

**Artifact rules**:
- Every `candidate` carries a `source_class` (one of the Entity-3 lanes) and a `disposition`.
- `disposition: deferred` entries cross-reference the per-class rationale in `deferred-superseded.md`.
- The artifact MAY carry annotation keys (`source_class`, `disposition`) that the production `crosswalk.yaml` MUST NOT (the crosswalk allows no extra keys per ADR-027) — strip annotation keys when promoting a candidate to `crosswalk.yaml`.

## B. Integrity acceptance contract (the invariants `crosswalk.yaml` MUST satisfy after edits)

Enforced by `tests/schemas/test_taxonomy_integrity.py` (structural) + the FR-014 audit (content):

| # | Invariant | Enforced by | FR |
|---|---|---|---|
| 1 | Every `source.id`/`target.id` resolves in the catalog named by its taxonomy | `test_crosswalk_referential_integrity` | FR-010 |
| 2 | `edge_type ∈ {primary, related, superseded}`; `confidence ∈ {high, medium, low}`; taxonomies in closed 7-value enum | `test_crosswalk_referential_integrity` | FR-010 |
| 3 | 5-tuple `(src.tax, src.id, tgt.tax, tgt.id, edge_type)` unique across the whole file | `test_crosswalk_loads` | FR-010 |
| 4 | `primary` count ≥ 500 (stays 542 — no primary downgraded) | `test_crosswalk_loads` | FR-011 |
| 5 | Every `citation` non-empty, URL-shaped or resolvable repo path | `test_citation_shape` | FR-010 |
| 6 | Catalogs lexicographically sorted (crosswalk NOT sort-gated) | `test_records_sorted` | A4 |
| 7 | `related` count ∈ [80, 150] (or documented achievable floor) | manual count / SC-001 | FR-001/002 |
| 8 | Every `high`/`medium` edge's citation supports its label; 0 high/medium from OWASP-LLM→CWE | **FR-014 anti-drift audit** (content, not shape) | FR-003/004/014 |
| 9 | No schema/test/ADR file modified | diff review | FR-011 |

**Acceptance command**:
```bash
pytest tests/schemas/test_taxonomy_integrity.py -q   # MUST report 5 passed
```

**No API contracts** — data-layer feature, no endpoints, no UI surface. The crosswalk *is* the machine-readable contract; its shape is unchanged.
