# Data Model: CWE Catalog Expansion — T029 Drift-Edge Restoration (F-A1.2)

**Feature**: 185 · **Date**: 2026-06-11 · **Plan**: [plan.md](plan.md)

All entities are flat-file YAML/Markdown — no database, no API. Shapes are frozen by ADR-027; this feature adds instances, never fields.

## 1. CWE Catalog Record (`schemas/taxonomy/cwe.yaml`)

| Field | Type | Validation (enforced by `test_framework_yamls_load`) |
|---|---|---|
| `id` | string `CWE-<N>` | unique within catalog; sort key |
| `full_id` | string | `CWE-<N>` convention (matches existing 53) |
| `name` | string | verbatim v4.20 published name — no paraphrase (R7); verified by `name_diff.py`, NOT by tests |
| `url` | string | `https://cwe.mitre.org/data/definitions/<N>.html` |

**Forbidden**: `cwe_refs` (ADR-027 Decision 1 — test-enforced for cwe.yaml only); `out_of_scope`/`out_of_scope_rationale` (D3 — entering records are in-scope); any abstraction/category field (schema change — header-comment annotation instead).

**Ordering**: lexicographic string sort on `id` (FR-032 / `test_records_sorted`): `CWE-1035 < CWE-1039 < CWE-1104 < … < CWE-16 < CWE-201 < …`.

**Cardinality**: 53 → 53 + |add-set| (93 if add-all-40).

**State transitions** (per missing ID):
```
missing (edge target unresolvable)
  → dispositioned (add | reject | defer — W0-a, Issue #185 line)
      add    → added (W1-1 record insert; in lexicographic position)
      reject → recorded-out (rationale on Issue #185; dependent edges stay out)
      defer  → recorded-out (same; future tranche)
```

## 2. Crosswalk Edge (`schemas/taxonomy/crosswalk.yaml`)

| Field | Type | Validation |
|---|---|---|
| `source.taxonomy` / `source.id` | enum member / string | must resolve in its catalog (`test_crosswalk_referential_integrity`) |
| `target.taxonomy` / `target.id` | enum member / string | same |
| `edge_type` | enum | all 67 restored edges: `primary` |
| `confidence` | enum `high\|medium\|low` | restored distribution: 34 high / 32 medium / 1 low — byte-preserved; the 1 `low` (`T1070.006 → CWE-1269`) is the crosswalk's first |
| `citation` | URL string | OWASP/MITRE URLs; shape-checked by `test_citation_shape` (no HTTP fetch) |

**Keys**: exact-tuple dedupe key = `(source.taxonomy, source.id, target.taxonomy, target.id, edge_type)`; near-key (cross-type duplicate guard) = same minus `edge_type`. Both re-checked against the live crosswalk at W1-2 (0 collisions required; 0 at definition).

**Cardinality**: 578 → 578 + |restored| (645 if add-all; primary 541 → 608; ≥500 floor never at risk).

**State transitions** (per T029-removed CWE-blocked edge):
```
removed-at-T029 (present only in e58f247 blob)
  → extracted (W0-b: restored-edges.yaml entry with _blocked_on annotation)
      target dispositioned "add"           → restored (W1-2: annotations stripped, byte-exact insert)
      target dispositioned "reject"/"defer" → recorded-out (stays in artifact; rationale on Issue #185)
```

## 3. Restore-Set Artifact (`specs/185-cwe-catalog-expansion/restored-edges.yaml`)

Working artifact (committed W0-b, before any production-data edit) — see [contracts/restored-edges.schema.md](contracts/restored-edges.schema.md).

| Element | Rule |
|---|---|
| header comment | provenance: blob SHAs (`e58f247` source / `991e1ee` control), filter definition, counts (67 = 65 owasp→cwe + 2 mitre-attack→cwe), extraction date, script path |
| edge entries | byte-copied from blob (`edge_type`/`confidence`/`citation` unmodified) |
| `_blocked_on` | per-edge working annotation = the missing target CWE ID (∈ the 40); MUST be stripped on insert (crosswalk forbids extra keys) |

**Invariant**: artifact ∪ {1 other-drift cwe-target edge, 20 non-CWE-target removals, 25 dedupe collapses} = the full T029 removal set; the artifact contains ONLY the 67.

## 4. Disposition Record (Issue #185 comment)

One line per ID × 40: `CWE-<N> — add|reject|defer — <name from v4.20> — <type: Weakness|Category|Pillar> — <rationale if not plain add>`. The 5 Category/Pillar entries (CWE-16, 255, 937, 1035 Categories; CWE-693 Pillar) carry the fidelity-first policy rationale. Aggregate: add-set ⊆ 40 sizes W1.

## 5. Coverage Attestation Baseline (`examples/{6}/security-report.pdf.baseline`)

| Input | Value |
|---|---|
| generator | `scripts/extract-report-data.py` (unchanged) + `typst compile` (unchanged) |
| determinism pin | `SOURCE_DATE_EPOCH=1700000000` (ADR-021) |
| changing input | `schemas/taxonomy/cwe.yaml` record count + per-record CA rows (`cwe` ∈ `ORDERED_FRAMEWORKS`) |
| invariant | deltas confined to Coverage Attestation pages (D-9); verified per [contracts/baseline-regen.contract.md](contracts/baseline-regen.contract.md) |
| scope | exactly the 6 `BASELINE_EXAMPLES` (D2); the 2 F-241 sample-report baselines untouched |

## Relationships

```
40 missing CWE IDs ──disposition (W0-a)──→ add-set ⊆ 40
        │                                      │
        └──── targets of ────┐                 ▼
                             │      cwe.yaml records (W1-1)  ──┐
67 removed edges ──extract──→ restored-edges.yaml (W0-b)       │ referential
                             │                                 │ integrity
                             └──restore if target added (W1-2)─┘
                                              │
                                              ▼
                              crosswalk.yaml (578 → 645)
                                              │
                                              ▼
                          6 CA baselines regenerated (W1-3)
```
