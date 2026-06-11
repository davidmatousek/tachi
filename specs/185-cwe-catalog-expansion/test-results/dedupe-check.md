# Dedupe Re-Check — T011 Pre-Insertion Gate (BLOCKING)

Feature 185 (Issue #185, F-A1.2) — re-verification of the contract §2 pre-insertion
checks immediately before edge insertion, per tasks.md T011 and
`contracts/restored-edges.schema.md` ("0 at definition 2026-06-11; re-verified at
insertion").

**Date**: 2026-06-11 (insertion time)
**Live crosswalk state**: 578 edges (post-US1 commit `6369ca6`, records already landed)
**Artifact**: `specs/185-cwe-catalog-expansion/restored-edges.yaml` (67 edges)

## Method

Scripted check (throwaway `/tmp/t185_restore_edges.py`, PyYAML parse of both files):

1. **Exact-tuple key** — for each of the 67 artifact edges (with the `_blocked_on`
   working annotation stripped), compute
   `(source.taxonomy, source.id, target.taxonomy, target.id, edge_type)`
   and test membership against the same key computed for all 578 live
   `schemas/taxonomy/crosswalk.yaml` edges.
2. **Near-key** — same comparison minus `edge_type`:
   `(source.taxonomy, source.id, target.taxonomy, target.id)`.
3. **Artifact-internal uniqueness** — the 67 exact-tuple keys are also checked
   for duplicates among themselves (insertion must not self-collide).

## Literal results

| Check | Collisions | Verdict |
|---|---|---|
| Exact-tuple (67 artifact vs 578 live) | **0** | PASS |
| Near-key (67 artifact vs 578 live) | **0** | PASS |
| Artifact-internal exact-tuple duplicates | **0** | PASS |

0 collisions on both blocking keys — insertion is unblocked (matches the
0-collision result at definition time recorded in the contract).
