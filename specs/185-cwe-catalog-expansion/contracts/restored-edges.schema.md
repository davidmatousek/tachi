# Contract: Restore-Set Artifact + Integrity Acceptance (F-A1.2)

**Feature**: 185 · **Date**: 2026-06-11 · Mirrors: `specs/186-mitre-catalog-expansion/contracts/restored-edges.schema.md`

This is a data-layer feature with no API. The contract is threefold: (1) the shape of the restore-set artifact, (2) the disposition→insertion mapping, and (3) the integrity-suite invariants that constitute acceptance.

## 1. Restore-Set Artifact Contract (`restored-edges.yaml`)

**Producer**: W0-b extraction — removed-edge set from `git show e58f247:schemas/taxonomy/crosswalk.yaml` minus `git show 991e1ee:schemas/taxonomy/crosswalk.yaml`, filtered to `target.taxonomy == cwe AND target.id ∉ frozen-53` (script: `scripts/extract_restore_set.py`).
**Consumer**: W1-2 insertion (subset whose `_blocked_on` ∈ the W0-a add-set).

**Guarantees**:
- Exactly **67** edges: **65** `owasp → cwe` (across all six tracked OWASP families: 22 Top 10 A0x, 14 Mobile, 12 LLM, 9 ML, 5 ASI, 3 API) + **2** `mitre-attack → cwe` (`T1070.006 → CWE-1269`, `T1562 → CWE-693` — exactly the pair PRD #186 FR-3 deferred to #185).
- Every edge carries `_blocked_on: <CWE-ID>` with the ID ∈ the 40-ID set pinned in spec FR-001; all 67 are blocked at extraction time (none of the 40 targets exist in the frozen 53).
- `edge_type` all `primary`; `confidence` distribution **34 high / 32 medium / 1 low**; `citation` all OWASP/MITRE URLs — each field byte-identical to the `e58f247` blob (no re-authoring, no upgrades — the single `low` edge stays `low`).
- The `_blocked_on` working annotation MUST be stripped before insertion (crosswalk forbids extra edge keys — `test_crosswalk_loads`).
- **Exclusions (MUST NOT appear in the artifact)**: the 1 cwe-target true-drift edge (its target exists today), the 20 non-CWE-target T029 removals, the 25 dedupe collapses.

**Header provenance block (required)**: blob SHAs (`e58f247` source / `991e1ee` control), filter definition, counts, extraction date, extraction script path, Issue #185 reference.

## 2. Disposition → Insertion Mapping

| W0-a verdict for `_blocked_on` ID | W1-2 action for the edge |
|---|---|
| `add` | insert byte-exact (annotation stripped) after the record lands in W1-1 |
| `reject` | edge stays out; rationale recorded on Issue #185 (no silent drop) |
| `defer` | edge stays out; future-tranche pointer recorded on Issue #185 |

Expected (add-all-40 lead posture): all 67 insert; crosswalk 578 → **645** (primary 541 → **608**). Any add-set ⊆ 40 is handled by the same mechanics without rework.

**Pre-insertion checks (W1-2, blocking)**: exact-tuple key `(source.taxonomy, source.id, target.taxonomy, target.id, edge_type)` and near-key (minus `edge_type`) — **0 collisions** against the live crosswalk (0 at definition 2026-06-11; re-verified at insertion).

## 3. Integrity Acceptance Contract (`tests/schemas/test_taxonomy_integrity.py`)

Acceptance = **all 5 functions pass after every commit touching `schemas/taxonomy/`** (not only at delivery):

| Function | Invariant the change must satisfy |
|----------|-----------------------------------|
| `test_framework_yamls_load` | every new CWE record is `{id, full_id, name, url}` with NO `cwe_refs` (cwe.yaml exception is test-enforced); unique ids; url-shaped |
| `test_records_sorted` | cwe.yaml remains lexicographically string-sorted by `id` (e.g., `CWE-1035 < CWE-1039 < … < CWE-16 < CWE-201`) |
| `test_crosswalk_loads` | no duplicate edge tuple; ≥500 primary floor (541 → 608 ≥ 500); no extra edge keys (annotations stripped) |
| `test_crosswalk_referential_integrity` | every restored edge's endpoints resolve — records (W1-1) strictly before edges (W1-2) in commit order |
| `test_citation_shape` | every restored citation is URL-shaped (passes by construction — byte-copied OWASP/MITRE URLs) |

**Pre-state**: 53 records / 578 edges (541 primary), 5/5 green (verified ~1s, 2026-06-11). **Post-state**: 53+|add| records / 578+|restored| edges, 5/5 green.

Name correctness is OUTSIDE this suite — covered by the W2-a `name_diff.py` gate (0 mismatches vs the pinned v4.20 harvest).
