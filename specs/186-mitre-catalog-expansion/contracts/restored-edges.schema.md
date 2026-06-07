# Contract: Restore-Set Artifact + Integrity Acceptance (F-A1.3)

**Feature**: 186 · **Date**: 2026-06-07

This is a data-layer feature with no API. The "contract" is twofold: (1) the shape of the FR-002 restore-set artifact, and (2) the integrity-suite invariants that constitute acceptance.

## 1. Restore-Set Artifact Contract (`restored-edges.yaml`)

**Producer**: Wave 1.1 extraction from `git show e58f247:schemas/taxonomy/crosswalk.yaml`, filtered to edges referencing the 16 gap IDs.
**Consumer**: Wave 1.2 (insert resolvable) + Wave 1.4 (insert FR-005-unblocked).

**Guarantees**:
- Exactly **16** edges (15 `mitre-atlas→mitre-attack` + 1 `mitre-attack→cwe`).
- Exactly **10** carry `_resolvable: true`; exactly **6** carry `_resolvable: false` with `_blocked_on` ∈ the 6 missing ATLAS IDs.
- Each edge's `edge_type`/`confidence`/`citation` are byte-identical to `e58f247` (no re-authoring).
- The `_resolvable`/`_blocked_on` annotation keys MUST be stripped before insertion (crosswalk forbids extra edge keys).

**The 10 resolvable edges (the deliverable — `crosswalk.yaml` additions):**

| source | target | edge_type | confidence |
|--------|--------|-----------|------------|
| mitre-attack / T1190 | cwe / CWE-20 | primary | medium |
| mitre-atlas / AML.T0059 | mitre-attack / T1565.001 | primary | medium |
| mitre-atlas / AML.T0060 | mitre-attack / T1557 | primary | medium |
| mitre-atlas / AML.T0000 | mitre-attack / T1213 | primary | medium |
| mitre-atlas / AML.T0003 | mitre-attack / T1195.002 | primary | medium |
| mitre-atlas / AML.T0011 | mitre-attack / T1005 | primary | medium |
| mitre-atlas / AML.T0016 | mitre-attack / T1195.002 | primary | medium |
| mitre-atlas / AML.T0029 | mitre-attack / T1499 | primary | medium |
| mitre-atlas / AML.T0034 | mitre-attack / T1565 | primary | medium |
| mitre-atlas / AML.T0040 | mitre-attack / T1068 | primary | medium |

**The 6 blocked edges (restore only if FR-003 dispositions the source "add"):**

| source (missing) | target | _blocked_on |
|------------------|--------|-------------|
| mitre-atlas / AML.T0001 | mitre-attack / T1213 | AML.T0001 |
| mitre-atlas / AML.T0005 | mitre-attack / T1213 | AML.T0005 |
| mitre-atlas / AML.T0025 | mitre-attack / T1005 | AML.T0025 |
| mitre-atlas / AML.T0037 | mitre-attack / T1213 | AML.T0037 |
| mitre-atlas / AML.T0043 | mitre-attack / T1190 | AML.T0043 |
| mitre-atlas / AML.T0048 | mitre-attack / T1499 | AML.T0048 |

## 2. Integrity Acceptance Contract (`tests/schemas/test_taxonomy_integrity.py`)

Acceptance = **all 5 functions pass** after the change set:

| Function | Invariant the change must satisfy |
|----------|-----------------------------------|
| `test_framework_yamls_load` | any new ATLAS record has `{id, full_id, name, url}` + `cwe_refs[]`; unique id; url-shaped |
| `test_records_sorted` | ATLAS records remain lexicographically sorted by `id` |
| `test_crosswalk_loads` | no duplicate edge; ≥500 primary floor (536 ≥ 500); no extra edge keys |
| `test_crosswalk_referential_integrity` | every restored edge's `source.id`/`target.id` resolves; enums closed |
| `test_citation_shape` | every restored edge's citation is URL-shaped or a repo file |

**Pre-state**: 526 primary edges, 5/5 green. **Post-state**: 536 (+k) primary edges, 5/5 green.
