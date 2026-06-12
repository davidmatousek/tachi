# Disposition Verdict — 40 Missing CWE IDs (T006, Gate G0b)

Feature 185 (CWE Catalog Expansion) — architect disposition per spec FR-001 / US1 acceptance scenario 1. Published on GitHub Issue #185 **before** any catalog or crosswalk modification.

**GitHub comment**: https://github.com/davidmatousek/tachi/issues/185#issuecomment-4684526026 (verified via API: 40/40 disposition lines landed, ascending numeric order, all five format fields present).

## Totals

| Disposition | Count |
|---|---|
| add | **40** |
| reject | 0 |
| defer | 0 |

**Resulting add-set (40 IDs — all of FR-001's pinned set)**: CWE-16, 73, 201, 213, 255, 256, 259, 260, 295, 307, 311, 312, 319, 326, 327, 359, 489, 520, 521, 540, 565, 601, 611, 614, 693, 732, 798, 799, 829, 915, 916, 937, 1035, 1039, 1104, 1174, 1269, 1357, 1426, 1427.

Downstream sizing: catalog 53 → 93 records (T007); all 67 restorable edges unblocked (T011), including both #186-deferred edges (`T1070.006 → CWE-1269`, `T1562 → CWE-693`). Lead posture (add-all-40) applied as published in the spec; no deviation.

## Harvest verification

- 40/40 IDs present in `harvest-40.md`; ID set byte-matches the FR-001 list (scripted cross-check).
- Type counts: 4 Category (CWE-16/255/937/1035) + 1 Pillar (CWE-693) + 35 Weakness — matches spec expectation.
- Status counts: 21 Draft / 17 Incomplete / 2 Obsolete / **0 Deprecated** — the FR-001 Deprecated-never-add rule is satisfied with no exclusions.

## 8-sentinel live-page spot-checks (2026-06-11) — 8/8 PASS

All fetched from `https://cwe.mitre.org/data/definitions/<N>.html`; site serving v4.20 (matches the pinned corpus).

| ID | Type | Resolves | Name matches harvest | Note |
|---|---|---|---|---|
| CWE-16 | Category | yes | yes | Title carries "CWE CATEGORY:" page-type label (page furniture, not part of XML `Name`); page displays "Vulnerability Mapping: Prohibited — status is Obsolete" |
| CWE-255 | Category | yes | yes | "CWE CATEGORY:" label as above |
| CWE-937 | Category | yes | yes | "CWE CATEGORY:" label as above |
| CWE-1035 | Category | yes | yes | "CWE CATEGORY:" label as above |
| CWE-693 | Pillar | yes | yes | Plain weakness-style title (Pillar = Weakness abstraction level) |
| CWE-1426 | Weakness | yes | yes | — |
| CWE-1427 | Weakness | yes | yes | — |
| CWE-1039 | Weakness | yes | yes | Live page displays the **current v4.20 name** (post-v4.17 rename) — confirms the harvest name is the correct one |

## Obsolete-status call (CWE-16, CWE-937)

**Call: Obsolete does NOT block "add" — both receive "add".**

Rationale:
1. **Status semantics**: MITRE distinguishes Deprecated (withdrawn; consumers redirected to successors; invalid citation target) from Obsolete (no longer actively maintained but remains a real, canonical, resolvable record). FR-001's hard rule bars only Deprecated.
2. **Live resolution**: both canonical URLs resolve (spot-checked 2026-06-11, site v4.20).
3. **Purpose-fit**: the catalog is a citation-resolution layer; CWE-16 is the published target of 3 restored OWASP mappings (A05:2021, API8:2023, Mobile M8 — Security Misconfiguration family) and CWE-937 of 1 (A06:2021). Rejecting them would re-strand 4 of the 67 edges — the exact T029 regression this feature repairs.
4. **Counter-signal addressed**: CWE-16's page states "Vulnerability Mapping: Prohibited (status is Obsolete)." That guidance governs authoring **new** CVE→CWE root-cause mappings; it does not govern resolving citations OWASP has already published. The restored edges are byte-exact restorations of published mappings, not new mapping decisions by tachi.
5. **Traceability mitigation**: Obsolete status to be annotated in the `cwe.yaml` header provenance block (T008 / FR-007b) — consumers see the flag without altering the ADR-027 record shape `{id, full_id, name, url}`.

Consequence if either had been rejected (avoided): CWE-16 reject strands `owasp:A05/API8/M8 → CWE-16`; CWE-937 reject strands `owasp:A06 → CWE-937`.

## Category/Pillar call (CWE-16, 255, 937, 1035, 693)

All 5 receive "add" with explicit per-line rationale on the Issue comment. Common basis: OWASP publishes these Category/Pillar IDs directly in its official mappings (937/1035 were created by MITRE *as* OWASP Top Ten mapping anchors); the flat record shape carries no abstraction semantics; abstraction precedent already in the catalog — CWE-284 (itself a MITRE Pillar) and CWE-200 (Class) are among the existing 53. **CWE-693 consequence explicitly weighed**: any non-add disposition would re-strand the #186-deferred `T1562 → CWE-693` edge (plus `owasp:M7 → CWE-693`) — rejected; CWE-693 receives "add".

## Inputs (read-only grounding)

- `test-results/harvest-40.md` (T004 harvest, pinned `cwec_v4.20.xml`)
- `test-results/corpus-pin.md` (v4.20, released 2026-04-30, retrieved 2026-06-11, zip SHA-256 `3976f599e5e5200219a3108bb896d06e2a88fbb293369e1883cb423a5e9d7d50`)
- `restored-edges.yaml` (T005 artifact: 67 edges, 40 distinct `_blocked_on` targets — every ID in the 40-set has ≥1 citing edge)
- Live MITRE pages for the 8 sentinels (fetched 2026-06-11)

— architect, 2026-06-11. Gate G0b satisfied: catalog edits (T007+) are unblocked for the full 40-ID add-set.
