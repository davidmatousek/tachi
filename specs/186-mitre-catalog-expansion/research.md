# Research Summary: MITRE ATT&CK + ATLAS Catalog Expansion (F-A1.3)

**Feature**: 186 · **Branch**: `186-mitre-catalog-expansion` · **Date**: 2026-06-07
**PRD**: `docs/product/02_PRD/186-mitre-catalog-expansion-2026-06-07.md` (v1.1, APPROVED)

This research was conducted at the spec stage and **supersedes the PRD's edge accounting with the exact, empirically-extracted restore-set** (the PRD carried the architect's slightly-broad estimate; the precise data is below).

## Knowledge Base / Prior-Art Findings
- **Feature 180 (F-A1, PR #181)** built `crosswalk.yaml` + 7 frozen catalogs + the FR-030 referential-integrity test. T029 ran a multi-cause cleanup. Squash-merged to `8b7c7bf`.
- **F-180 R7 tripwire** (documented in `schemas/taxonomy/mitre-atlas.yaml` header): `atlas.mitre.org` per-technique pages 404 via WebFetch (client-side anti-bot gating). Authoritative ATLAS source is the `mitre-atlas/atlas-data` repo. **Confirmed again 2026-06-07**: both a `curl` and a `WebFetch` attempt to the atlas-data raw YAML failed (404/empty) from this environment — so the FR-1 ATLAS-source verification is a genuine build-time architect task, not a spec-time shortcut.
- **F-180 name-contamination lesson** (R7): earlier ATLAS authoring introduced speculative/aggregated-search names that didn't match the canonical publication. Any FR-1 "add" must take names byte-exact from `atlas-data`.
- **Lesson — decision-trail integrity** (F-180 architect C2 pattern): close the 6-ID question with an explicit, cited disposition, not silent omission.

## Codebase Analysis (the load-bearing research)
**Recovery source** (F-180 squash-merged → dangling task-commits, SHAs in `specs/180-*/NEXT-SESSION.md`, both confirmed present in the local object DB):
- `e58f247` "fix(180): T029 normalize format drift (74 edges) + sort cwe.yaml" — **pre-semantic-removal, 551 edges** (recovery source).
- `991e1ee` "fix(180): T029 remove semantic drift (88 edges) + dedupe (25 duplicates)" — **post-removal, 438 edges**.

**Exact extraction** (`e58f247` minus `991e1ee`, then filtered to the 16 gap IDs; via `yaml.safe_load` diff):
- T029 removed **88 edges** total (551→438), multi-cause (semantic-drift + dedupe).
- The **MITRE-gap-scoped removed set is exactly 16 edges** (15 `mitre-atlas→mitre-attack` + 1 `mitre-attack→cwe`).

**THE 10 NOW-RESOLVABLE EDGES** (both endpoints exist in current catalogs — the concrete deliverable; matches the architect PoC of "10 edges → suite 5/5 green, 0 collisions"). All `edge_type: primary`, `confidence: medium`, citations recoverable byte-exact from `e58f247`:

| # | source | target | unblocked by |
|---|--------|--------|--------------|
| 1 | mitre-attack:T1190 | cwe:CWE-20 | T1190 added by F-241 (CWE-20 always existed) |
| 2 | mitre-atlas:AML.T0059 | mitre-attack:T1565.001 | T1565.001 added by F-241 (T0059 already present) |
| 3 | mitre-atlas:AML.T0060 | mitre-attack:T1557 | T1557 added by F-241 (T0060 already present) |
| 4 | mitre-atlas:AML.T0000 | mitre-attack:T1213 | T0000 added by F-241 |
| 5 | mitre-atlas:AML.T0003 | mitre-attack:T1195.002 | T0003 added by F-241 |
| 6 | mitre-atlas:AML.T0011 | mitre-attack:T1005 | T0011 added by F-241 |
| 7 | mitre-atlas:AML.T0016 | mitre-attack:T1195.002 | T0016 added by F-241 |
| 8 | mitre-atlas:AML.T0029 | mitre-attack:T1499 | T0029 added by F-241 |
| 9 | mitre-atlas:AML.T0034 | mitre-attack:T1565 | T0034 added by F-241 |
| 10 | mitre-atlas:AML.T0040 | mitre-attack:T1068 | T0040 added by F-241 |

**THE 6 STILL-BLOCKED EDGES** (all blocked on the 6 missing ATLAS *source* IDs — gated on the FR-1 disposition):

| source (missing) | target (resolves) |
|---|---|
| mitre-atlas:AML.T0001 | mitre-attack:T1213 |
| mitre-atlas:AML.T0005 | mitre-attack:T1213 |
| mitre-atlas:AML.T0025 | mitre-attack:T1005 |
| mitre-atlas:AML.T0037 | mitre-attack:T1213 |
| mitre-atlas:AML.T0043 | mitre-attack:T1190 (dual — ATT&CK end now resolves; blocked only on T0043) |
| mitre-atlas:AML.T0048 | mitre-attack:T1499 |

**Correction to the PRD**: the PRD (carrying the architect's broader estimate) said "MITRE-scoped removed = 18; residual = 6 ATLAS-blocked + 2 CWE-blocked deferred to #185 (T1070.006→CWE-1269, T1562→CWE-693)." The exact extraction shows the **16-ID-scoped set is 16 edges (10 resolvable + 6 ATLAS-blocked)**. The 2 CWE-blocked edges **do NOT reference any of the 16 gap IDs** — they are separate T029 removals (MITRE-sourced, CWE-target-blocked) that belong to #185's domain and are **entirely out of #186 scope** (not merely "deferred"). The spec reflects the precise 16/10/6 accounting.

**Record shape** (`schemas/taxonomy/mitre-atlas.yaml`, 30 records): `{id: AML.TXXXX, full_id: ATLAS-AML.TXXXX, name, url: https://atlas.mitre.org/techniques/AML.TXXXX, cwe_refs: [], out_of_scope: false, out_of_scope_rationale: ""}`. Lexicographically sorted by `id`.

**Integrity test** (`tests/schemas/test_taxonomy_integrity.py`, **5 functions**, `5 passed` on main): `test_framework_yamls_load` (record shape, unique ids, url-shape, cwe_refs regex), `test_records_sorted` (lexicographic), `test_crosswalk_loads` (no dup edges, ≥500 primary floor — currently 526), `test_crosswalk_referential_integrity` (every endpoint resolves; enums closed), `test_citation_shape` (url-or-repo-file).

## Architecture Constraints
- **FR-030** (F-180 spec): referential-integrity strictness — every edge endpoint MUST resolve. This is the hard gate restored edges must satisfy.
- **ADR-027** (Taxonomy Crosswalk Schema): defines the 7-value `taxonomy` enum (`mitre-atlas`/`mitre-attack` already members) and record/edge shapes. **Unchanged by #186** — additive records + previously-present edges only. **No new ADR** (contrast #184, which expands the enum 7→8).
- **Determinism**: static YAML; edge reconstruction is byte-exact recovery, not re-authoring.

## Industry Research
- **MITRE ATLAS** authoritative source: `mitre-atlas/atlas-data` repo (canonical `techniques.yaml`). Per the F-180 R7 note and re-confirmed here, the public per-technique web pages are not WebFetch-accessible; the repo YAML is the source of truth. Latest ATLAS release is v5.x.
- **MITRE ATT&CK** source: `https://attack.mitre.org/techniques/T<N>/` (URL pattern only; regex-validated, no fetch).
- **Preliminary FR-1 signal**: inconclusive (source fetch failed from this environment). Low-confidence prior: F-241's *phase-complete* `atlas-data` expansion deliberately excluded these 6, which biases the disposition toward reject/defer — but `AML.T0043` (Craft Adversarial Data) and `AML.T0048` (External Harms) are plausible legitimate adds the architect must verify. **No disposition asserted here; FR-1 is the authoritative gate.**

## Recommendations for Spec
- **Primary deliverable = restore the explicit 10 edges** (table above), reconstructed byte-exact from `e58f247`, extracted to a checked-in artifact early (de-risk dangling-object loss). This is independent of the FR-1 outcome → always shippable.
- **FR-1 (6-ID disposition)** is a build-time architect gate; the spec's success criteria must be disposition-agnostic (handle 0–6 adds) and treat the 6-ID exercise primarily as decision-trail closure.
- **Scope the restore to exactly the 16-ID set** — never the full 88-edge removal (would re-introduce the semantic-drift/dedupe edges T029 correctly removed). The 2 CWE-blocked edges are out of scope (#185).
- **Integrity suite (5/5) is the acceptance gate.** No schema/ADR change.
- Add catalog-header provenance note (F-A1.3) mirroring the F-241 note; update F-180 `NEXT-SESSION.md` decision trail at close.
