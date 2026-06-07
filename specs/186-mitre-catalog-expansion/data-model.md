# Data Model: MITRE ATT&CK + ATLAS Catalog Expansion (F-A1.3)

**Feature**: 186 · **Date**: 2026-06-07

This feature touches existing data shapes (defined by ADR-027) and introduces one build artifact. No schema changes.

## Entity 1 — Crosswalk Edge (existing, ADR-027 / `crosswalk.yaml`)

```yaml
- source:  { taxonomy: <enum>, id: <string> }
  target:  { taxonomy: <enum>, id: <string> }
  edge_type:  primary | related | superseded
  confidence: high | medium | low
  citation:   <https URL or repo-relative file path>
```

- **taxonomy enum (7, closed)**: `owasp, mitre-attack, mitre-atlas, nist-ai-rmf, cwe, tachi-control-category, tachi-stride-ai-category`.
- **Validation** (`test_crosswalk_*`): `source.id` resolves in `{source.taxonomy}.yaml`; `target.id` resolves in `{target.taxonomy}.yaml`; all enums closed; no extra keys; no duplicate on `(source.tax, source.id, target.tax, target.id, edge_type)`; citation URL-shaped or a repo file.
- **In-scope instances**: the 10 resolvable edges (all `primary`/`medium`) + ≤6 conditional. Recovered byte-exact from `e58f247` — values are **not** authored fresh.

## Entity 2 — ATLAS Catalog Record (existing, `mitre-atlas.yaml`)

```yaml
- id: AML.TXXXX                                  # used as crosswalk endpoint id
  full_id: ATLAS-AML.TXXXX
  name: <byte-exact from atlas-data>
  url: https://atlas.mitre.org/techniques/AML.TXXXX
  cwe_refs: []                                   # ATLAS publishes no direct CWE refs
  out_of_scope: false                            # optional (F-241/ADR-037); permitted, not required
  out_of_scope_rationale: ""                     # optional
```

- **Validation** (`test_framework_yamls_load`, `test_records_sorted`): required `{id, full_id, name, url}` + `cwe_refs` (list of `^CWE-\d+$`); unique `id`; `url` matches `^https?://`; records lexicographically sorted by `id`.
- **In-scope instances**: 0–6 new records, one per "add"-disposition ID (FR-004). Inserted in sort position.

## Entity 3 — Restore-Set Artifact (NEW build output, FR-002)

`specs/186-mitre-catalog-expansion/restored-edges.yaml` — the durable, checked-in extraction of the in-scope removed edges from `e58f247`, decoupling restoration from dangling-commit survival.

```yaml
# Extracted from git commit e58f247 (pre-T029-removal, 551 edges) on 2026-06-07.
# The 16 MITRE-gap-scoped edges T029 removed. resolvable=true → restore now (FR-001).
# resolvable=false → blocked on a missing ATLAS source id; restore only if FR-003 dispositions it "add" (FR-005).
- source: { taxonomy: ..., id: ... }
  target: { taxonomy: ..., id: ... }
  edge_type: ...
  confidence: ...
  citation: ...
  _resolvable: true|false        # annotation only — STRIPPED before insertion into crosswalk.yaml
  _blocked_on: AML.TXXXX         # annotation only (for the 6 blocked)
```

- **Note**: the `_resolvable`/`_blocked_on` keys are extraction annotations; `crosswalk.yaml` forbids extra edge keys, so they MUST be stripped on insertion. The artifact is provenance/recovery, not a direct copy target.

## Entity 4 — ID Disposition (FR-003, recorded on Issue #186)

| Field | Values | Meaning |
|-------|--------|---------|
| id | `AML.T0001/T0005/T0025/T0037/T0043/T0048` | the 6 still-missing ATLAS IDs |
| disposition | `add` / `reject` / `defer` | add → resolvable on atlas-data; reject → invented/mistranscribed pre-T029; defer → legitimate but unpublished |
| rationale | one line | cited justification |

- **Authority**: architect, verified against `mitre-atlas/atlas-data`. Lives as an Issue #186 comment (the durable decision trail); summarized in the CHANGELOG/close note.

## Relationships

- A blocked edge (Entity 3, `resolvable=false`) → restorable **iff** its `_blocked_on` ATLAS id gets an "add" disposition (Entity 4) → triggers a new ATLAS record (Entity 2) → then the edge (Entity 1) restores.
- The `AML.T0043 → T1190` edge: ATT&CK target `T1190` already resolves; restorability depends solely on the `AML.T0043` disposition.
- The 10 resolvable edges have **no** dependency on Entity 4 — they restore unconditionally (the MVP).
