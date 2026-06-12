# Research Summary: CWE Catalog Expansion — T029 Drift-Edge Restoration (F-A1.2)

**Date**: 2026-06-11
**Feature**: [spec.md](spec.md) | PRD: [185-cwe-catalog-expansion-2026-06-11.md](../../docs/product/02_PRD/185-cwe-catalog-expansion-2026-06-11.md)
**Detailed findings**: `.aod/results/research-kb.md`, `research-codebase.md`, `research-architecture.md`, `research-web.md` (session artifacts)

## Knowledge Base Findings

- **KB Entry 13 (F-186)** — the proven restore playbook this feature mirrors: extract-first blocking task (restore-set artifact committed before any production edit), `_resolvable`/`_blocked_on` annotations in the restore-set stripped on insert, 5-function integrity suite as the sole structural oracle.
- **KB Entry 14 (F-182)** — related-edge tranche cadence; confirms net-new edge authoring to the 40 entering records belongs to a *future* tranche, not F-185.
- **F-180 R7 (commit `be18076`)** — name-contamination tripwire: harvest names ONLY from the authoritative MITRE source via scripted bulk download; never aggregators, never paraphrase. Names are not test-verified — failure is silent.
- **F-180 T029 Option (d) MIX** — the disposition that removed the 88 drift edges and filed Issue #185; pins the 67-edge / 40-ID scope against blobs `e58f247`/`991e1ee`.
- **F-184** — set current baseline (578 edges, 8 catalogs); established the stale-count-sweep and no-test-edit patterns.
- 7 of 14 KB entries relevant overall (13, 14 primary; 1, 2, 8, 9, 11 supporting).

## Codebase Analysis

- **Recovery source verified 2026-06-11**: `e58f247` and `991e1ee` are dangling **commits** (not blobs) — both present; `git show e58f247:schemas/taxonomy/crosswalk.yaml` resolves. Edge counts: e58f247 = 551, 991e1ee = 438, current = 578 (541 primary / 37 related). `cwe.yaml` = 53 records.
- **Restore set re-derived independently**: exactly **67 edges** (65 `owasp→cwe` + 2 `mitre-attack→cwe`), **40 distinct missing CWE IDs** (53+40 = 93), **0 collisions** vs current 578 — matches the PRD derivation.
- **Confidence flag**: 1 of the 67 (`T1070.006 → CWE-1269`) is `confidence: low` — it will be the crosswalk's **first** `low` edge. The enum permits it; byte-exact restoration preserves it. Not a blocker; note for reviewers.
- **Integrity suite baseline**: 5/5 green in ~1s via `/usr/bin/python3 -m pytest tests/schemas/test_taxonomy_integrity.py -q`. No exact-count assertions; ≥500 primary floor only; `test_records_sorted` enforces lexicographic string sort; cwe.yaml is the one catalog that must NOT carry `cwe_refs` (test lines 149–152).
- **#186 artifact contract**: `specs/186-mitre-catalog-expansion/restored-edges.yaml` + `contracts/restored-edges.schema.md` — F-185 mirrors both (header provenance block, edge list byte-copied from blob, schema contract doc).
- **F-180 trail**: `specs/180-taxonomy-crosswalk-collection/NEXT-SESSION.md` carries the T029 CWE-blocked residual and the F-186 resolution entry format F-185 must extend.

## Architecture Constraints

- **ADR-027** (`docs/architecture/02_ADRs/ADR-027-taxonomy-crosswalk-schema.md`): `cwe` in the taxonomy enum since v1; record shape `{id, full_id, name, url}`; Decision 1 excludes `cwe_refs` on CWE records. **No amendment required** (no enum/shape change). F-184's annotation-not-new-ADR precedent at lines 83 + 373.
- **ADR-037 D-7** (lines 123–150): CWE substitution table (8 CWEs) at lines 129–138. F-185 adds 5 of them (CWE-307, 311, 319, 326, 732) to the catalog → annotate D-7 (blockquote + Revision History table row, docs-only). Color: 4 of the 5 appear in owasp.yaml published `cwe_refs`; CWE-732's demand came from baseline attribution.
- **CRITICAL — Coverage Attestation baseline impact (not in the PRD)**: `cwe` is in `ORDERED_FRAMEWORKS` (`scripts/extract-report-data.py:1076`); record counts and per-record Covered/Partial/Gap rows render on the Coverage Attestation PDF pages (`coverage-attestation.typ:164,183`). `tests/scripts/test_backward_compatibility.py::test_unmodified_examples_byte_identical_pdfs` regenerates report-data + compiles under `SOURCE_DATE_EPOCH=1700000000` and byte-compares against committed `.baseline` PDFs. Growing cwe.yaml 53→93 changes the CA denominators and adds 40 Gap rows ⇒ **byte-identity tests fail unless F-185 intentionally regenerates the example baselines in the same change-set** (ADR-037 D-9 lane: CA pages change, non-CA pages stay byte-identical). F-184 dodged this only because `nist-ai-600-1` is NOT in `ORDERED_FRAMEWORKS`; `cwe` IS. The PRD's "no baseline regeneration" line (FR-5/architect C2) scoped the D-7 *annotation* — the catalog growth itself triggers the D-9 regen lane regardless.
- **Edge-resolution mechanics**: owasp.yaml `cwe_refs` are shape-checked only (need not resolve); crosswalk edges DO require resolution — this is exactly why the 67 were removed under FR-030 and why records must land before edges.

## Industry Research (MITRE CWE source)

- **Corpus pin**: CWE **v4.20** (released 2026-04-30). Comprehensive dictionary: `https://cwe.mitre.org/data/xml/cwec_v4.20.xml.zip` (also `cwec_latest.xml.zip`). Confirmed to include all 422 Categories + 10 Pillars; per-view CSVs confirmed to EXCLUDE them (validates architect C3 — CSVs would false-reject CWE-16/255/937/1035).
- **XML structure for scripted harvest**: `<Weakness ID Name>`, `<Category ID Name>`, `<View ID Name>` elements under `<Weakness_Catalog Version="4.20">` — sufficient for an all-40 name harvest + name-diff script.
- **Spot-check 8/8 verified, none deprecated**: CWE-1427, CWE-1426 (AI CWEs) confirmed; **CWE-1039 was RENAMED at v4.17 (2025-04-03)** — current name is "Inadequate Detection or Handling of Adversarial Input Perturbations in Automated Recognition Mechanism" (informal pre-4.17 word order is stale — scripted harvest from v4.20 is mandatory, validating team-lead C4). Types confirmed: CWE-16/255/937/1035 = Categories (mapping-Prohibited), CWE-693 = Pillar-class Weakness.
- **Mapping guidance**: MITRE discourages/prohibits Categories for *CVE root-cause mapping*; tachi's catalog is a citation-resolution layer, OWASP publishes these IDs verbatim, and the catalog holds CWE-200 (Class) / CWE-284 (Pillar) precedent — fidelity-first add rationale holds.
- **No anti-bot tripwire** on cwe.mitre.org (unlike the OWASP/R7 incident); single ~50 MB zip download is the polite path.

## Recommendations for Spec

1. **Adopt the #186 playbook verbatim** where applicable: extract-first restore-set artifact, schema contract doc, integrity suite as gate at every commit.
2. **Add the Coverage Attestation baseline regeneration as an explicit in-scope requirement** (FR + SC) — the one material delta vs the PRD; without it the delivery lands red on `test_backward_compatibility.py`. Per D-9: regenerate committed example baselines in the same change-set, CA-page-only deltas, `SOURCE_DATE_EPOCH=1700000000`.
3. **Pin the harvest to cwec v4.20** (record the version + retrieval date in the cwe.yaml header provenance block) and make the all-40 scripted name-diff a success criterion (0 mismatches).
4. **Record names use CURRENT v4.20 published names** (CWE-1039 rename proves the point); edges are name-free so blob byte-exactness is unaffected.
5. **Surface the first-`low`-confidence-edge fact** in the spec edge cases so reviewers don't flag it as drift at build review.
6. Keep out-of-scope fences from the PRD: 1 other-drift edge, 20 non-CWE removals, 25 dedupe collapses, net-new edge authoring, `cwe_refs` population, Top 25 refresh, #183 link-rot.

---

## Phase 0 Decisions (plan stage, 2026-06-11)

### D1 — Harvest source: pinned `cwec_v4.20.xml.zip`
- **Decision**: Bulk-harvest the 40 record names/types/statuses from MITRE's comprehensive dictionary `https://cwe.mitre.org/data/xml/cwec_v4.20.xml.zip` (v4.20, 2026-04-30), recorded in the cwe.yaml provenance header.
- **Rationale**: Single authoritative source; includes all 422 Categories + 10 Pillars; one polite download; scriptable name-diff; CWE-1039's v4.17 rename proves per-memory transcription is unsafe.
- **Alternatives considered**: per-view CSVs (REJECTED — omit Category entries, would false-reject CWE-16/255/937/1035); per-page scraping as primary (REJECTED — 40 fetches, R7-class fragility; retained only as 8-sentinel spot-check).

### D2 — Baseline regeneration scope: the 6 `BASELINE_EXAMPLES` only
- **Decision**: Regenerate exactly the 6 byte-identity-gated baselines (`web-app`, `microservices`, `ascii-web-api`, `mermaid-agentic-app`, `free-text-microservice`, `maestro-reference`). Leave the 2 F-241 sample-report baselines (`predictive-ml-app`, `mobile-banking-app`) untouched.
- **Rationale**: Only the 6 are enforced by `test_backward_compatibility.py`; the 2 net-new are excluded by its docstring as "regeneration mutation targets … not expected to match a pre-existing baseline", and no test byte-compares them. Regenerating them adds blast radius with zero gating benefit; their CA-page staleness is the already-documented status of those artifacts.
- **Alternatives considered**: regen all 8 per the D-9 canonical count (REJECTED — touches other features' mutation surfaces ungated; can be picked up by their owning features or a follow-on). **Architect ratified at plan review (2026-06-11).**
- **Plan-review addendum (empirical, both reviewers independently)**: the byte-identity suite is ALREADY RED on main — #186 grew `mitre-atlas` (∈ `ORDERED_FRAMEWORKS`) 30→36 without regen; page diff attributes 100% of divergence to the ATLAS CA section. W1-3 is a repair (red→green), absorbing the inherited ATLAS delta with dual attribution in CHANGELOG. Process lesson queued for KB: any catalog-growth feature must check `ORDERED_FRAMEWORKS` membership at definition.

### D3 — Entering records are in-scope (no `out_of_scope` keys)
- **Decision**: The 40 records land with the frozen 4-field shape only; CA-page `cwe` coverage denominators grow 53 → 93 and percentages drop accordingly on regenerated baselines.
- **Rationale**: Honest attestation — the existing 53 carry no out-of-scope flags either; flags exist for genuinely out-of-scope records, not for protecting percentages.
- **Alternatives considered**: flag the 40 `out_of_scope` to preserve coverage optics (REJECTED — data falsification; would also contradict the records' purpose as citable, coverable CWEs).

### D4 — Helper scripts committed under `specs/185-cwe-catalog-expansion/scripts/`
- **Decision**: `harvest_cwe_names.py`, `extract_restore_set.py`, `name_diff.py` are committed feature-local (regeneration-only tier, no production caller).
- **Rationale**: Reproducibility of the derivation without dangling-object or `/tmp` dependencies; matches the repo's existing regeneration-script tier.
- **Alternatives considered**: `/tmp` ephemeral scripts as at PRD derivation (REJECTED — not reproducible post-delivery); `scripts/` production dir (REJECTED — implies a production caller that doesn't exist).

### D5 — Restore-set extraction parallel to disposition (W0 twin tracks)
- **Decision**: W0-b extraction + artifact commit runs immediately, not gated on the W0-a architect disposition.
- **Rationale**: Extraction is disposition-independent (the filter is mechanical); the early commit closes the dangling-object window (Risk 185.1) — team-lead C3, proven by #186.
- **Alternatives considered**: disposition-first sequencing (REJECTED — leaves the only copy of the 67 edges in GC-able dangling objects longer for no benefit).

### D6 — Wave shape: W0 (∥) → W1 (sequential data) → W2 (verification ∥ docs)
- **Decision**: W0-a disposition ∥ W0-b extraction → W1-1 records → W1-2 edges → W1-3 baselines → W2-a name-diff/test ∥ W2-b review sweep → W2-c docs closure.
- **Rationale**: FR-030 forces records-before-edges; baselines must capture final data; verification parallelizes; matches the PRD team-lead wave proposal with the FR-006 lane appended.
- **Alternatives considered**: single linear wave (REJECTED — wastes the disposition/extraction parallelism and the W2 tester∥reviewer split).
