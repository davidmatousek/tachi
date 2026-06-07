# Deferred `superseded` Set — Disposition (F-182, FR-008)

**Feature**: [spec.md](spec.md) · **Date**: 2026-06-07 · **Survey task**: T007 · **Author task**: T008

## Outcome

**Authored `superseded` edges: 0.** This is an explicitly acceptable, documented outcome
(spec US2 Acceptance Scenario 3, Assumption A3) — not a failure. The value of US2 is the
honest audit + recorded deferral, not a volume floor.

## Why the authorable set is empty

A `superseded` edge expresses old-item → newer-item lineage and is authorable **only where
both endpoints already resolve under the current catalogs** (FR-007, referential integrity
FR-010). The T007 survey of the locked catalog snapshot (cwe 53 / mitre-attack 701 /
mitre-atlas 36 / owasp 60) found **no catalog-authorable deprecation/replacement pair**:

- No catalog record carries any deprecation/superseded/revoked/replacement metadata field
  (record shape is `{id, full_id, name, url[, cwe_refs, out_of_scope, out_of_scope_rationale]}`).
- No catalog record's `name` signals deprecation/revocation/obsolescence.
- The catalogs hold **current editions/revisions only** — the *old* endpoint of a supersession
  is, by construction, absent.

## Deferred classes (one line per class → follow-on)

| # | Deferred supersession class | Why not authorable now | Follow-on |
|---|------------------------------|------------------------|-----------|
| 1 | **OWASP edition-revision lineage** (e.g. Web `:2017` categories → `:2021`; LLM `:2023` → `:2025` renumbering) | Catalog holds only current editions (2021/2023/2024/2025/2026); the superseded *prior-edition* records do not exist as catalog endpoints | Add prior-edition OWASP records (catalog-expansion territory, BLP-05 Wave 2 / future), then author the lineage edges |
| 2 | **MITRE ATT&CK deprecated/revoked techniques → successors** (e.g. a deprecated technique split into current ones) | The 701-record catalog is the current ATT&CK set and carries no deprecation lineage; deprecated source IDs are not present as endpoints | Add the historical/deprecated ATT&CK records + revocation metadata, then author the lineage |
| 3 | **MITRE ATLAS technique revisions** (cross-version renames noted in `mitre-atlas.yaml`, e.g. AML.T0010 "ML…"→"AI Supply Chain Compromise" in v5.5) | These are *renames* of a stable ID, not supersessions of one ID by another; no deprecated ATLAS ID has a distinct in-catalog successor | None required (rename ≠ supersession); revisit only if ATLAS deprecates an ID in favor of a new one both present in-catalog |
| 4 | **CWE deprecated → replacement** (a deprecated CWE pointing to its replacement) | None of the 53 in-catalog CWEs is deprecated (all are active, commonly-cited weaknesses); no deprecated source endpoint resolves | Revisit if `cwe.yaml` expansion (#185) admits a deprecated CWE whose replacement is also in-catalog |

## Integrity note

Because the authored `superseded` set is empty, the `superseded` edge count in
`schemas/taxonomy/crosswalk.yaml` remains **0**; the integrity suite's referential-integrity
and uniqueness guarantees hold vacuously for this edge type. No deferred pair was silently
dropped — each class above is recorded with its follow-on (FR-008 satisfied).
