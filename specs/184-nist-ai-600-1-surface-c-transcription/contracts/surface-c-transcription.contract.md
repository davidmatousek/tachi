# Build Contract: NIST AI 600-1 Surface C Transcription (F-184)

**Status**: BINDING — builders execute against this file; reviewers diff against it.
**Sources**: PRD-184 v1.2 (FR-1/FR-2/FR-3/FR-7 tables, Architect-verified 1:1 at HEAD `f57a9c1`); `.aod/results/architect.md` (M1×C4 normative inventory); Surface C table in `.claude/skills/tachi-shared/references/nist-ai-rmf-mapping.md` (verbatim source).

---

## C1 — Catalog records (`schemas/taxonomy/nist-ai-600-1.yaml`, exactly 12)

All records: `url: https://doi.org/10.6028/NIST.AI.600-1` · `cwe_refs: []` · ids **YAML-quoted strings** · file in publication order. Names verbatim from the Surface C table.

| id | full_id | name |
|---|---|---|
| `"2.1"` | NIST AI 600-1 §2.1 | CBRN Information or Capabilities |
| `"2.2"` | NIST AI 600-1 §2.2 | Confabulation |
| `"2.3"` | NIST AI 600-1 §2.3 | Dangerous, Violent, or Hateful Content |
| `"2.4"` | NIST AI 600-1 §2.4 | Data Privacy |
| `"2.5"` | NIST AI 600-1 §2.5 | Environmental Impacts |
| `"2.6"` | NIST AI 600-1 §2.6 | Harmful Bias or Homogenization |
| `"2.7"` | NIST AI 600-1 §2.7 | Human-AI Configuration |
| `"2.8"` | NIST AI 600-1 §2.8 | Information Integrity |
| `"2.9"` | NIST AI 600-1 §2.9 | Information Security |
| `"2.10"` | NIST AI 600-1 §2.10 | Intellectual Property |
| `"2.11"` | NIST AI 600-1 §2.11 | Obscene, Degrading, and/or Abusive Content |
| `"2.12"` | NIST AI 600-1 §2.12 | Value Chain and Component Integration |

Record template (shape identical to `nist-ai-rmf.yaml` posture):

```yaml
- id: "2.9"
  full_id: NIST AI 600-1 §2.9
  name: Information Security
  url: https://doi.org/10.6028/NIST.AI.600-1
  cwe_refs: []
```

Header comment MUST pin: source (NIST AI 600-1, July 2024, via the Surface C table of `nist-ai-rmf-mapping.md`) + retrieval/verification date (2026-06-10) + record shape + **"ids are quoted strings"** rule + publication-order sort convention + cwe_refs rationale + FR-024 transcription-discipline pointer.

**Known divergence (documented, not corrected here)**: NIST's PDF titles §2.6 "Harmful Bias **and** Homogenization"; the in-repo Surface C table says "**or**". Transcription follows the table (FR-024); the observation routes with the OQ-4 ADR-025 note at delivery.

## C2 — Edge ADD list (exactly 15; one coherent change-set with C3)

All edges: `edge_type: primary` · `confidence: high` · `citation: .claude/skills/tachi-shared/references/nist-ai-rmf-mapping.md` · target ids quoted.

| # | source.id (tachi-stride-ai-category) | target.id (nist-ai-600-1) | GAI Risk |
|---|---|---|---|
| 1 | info-disclosure | `"2.4"` | Data Privacy |
| 2 | tampering | `"2.9"` | Information Security |
| 3 | info-disclosure | `"2.9"` | Information Security |
| 4 | denial-of-service | `"2.9"` | Information Security |
| 5 | prompt-injection | `"2.9"` | Information Security |
| 6 | data-poisoning | `"2.9"` | Information Security |
| 7 | privilege-escalation | `"2.9"` | Information Security |
| 8 | model-theft | `"2.9"` | Information Security |
| 9 | agent-autonomy | `"2.9"` | Information Security |
| 10 | tool-abuse | `"2.9"` | Information Security |
| 11 | model-theft | `"2.10"` | Intellectual Property |
| 12 | info-disclosure | `"2.10"` | Intellectual Property |
| 13 | tool-abuse | `"2.12"` | Value Chain and Component Integration |
| 14 | tampering | `"2.12"` | Value Chain and Component Integration |
| 15 | data-poisoning | `"2.12"` | Value Chain and Component Integration |

Edge template:

```yaml
- source:
    taxonomy: tachi-stride-ai-category
    id: prompt-injection
  target:
    taxonomy: nist-ai-600-1
    id: "2.9"
  edge_type: primary
  confidence: high
  citation: .claude/skills/tachi-shared/references/nist-ai-rmf-mapping.md
```

Invariants: 15 distinct triples; 9 distinct sources (spoofing, repudiation unused — correct); 4 distinct targets; omit both Gap rows (§2.6 ×—; §2.9×Spoofing) and all 8 "No equivalent" rows.

## C3 — Edge REMOVE list (exactly 16; class `tachi-stride-ai-category → nist-ai-rmf`)

Removal by **class filter**, never line ranges. Pre-count MUST be 16 matching this list 1:1; post-filter MUST be empty.

| # | source.id | target.id (nist-ai-rmf) |
|---|---|---|
| 1 | prompt-injection | MEASURE 2.6 |
| 2 | prompt-injection | MEASURE 2.7 |
| 3 | data-poisoning | MEASURE 2.7 |
| 4 | data-poisoning | MEASURE 2.8 |
| 5 | spoofing | MEASURE 2.7 |
| 6 | tampering | MEASURE 2.7 |
| 7 | tampering | MEASURE 2.8 |
| 8 | repudiation | MEASURE 2.8 |
| 9 | info-disclosure | MEASURE 2.7 |
| 10 | info-disclosure | MEASURE 2.10 |
| 11 | denial-of-service | MEASURE 2.7 |
| 12 | privilege-escalation | MEASURE 2.7 |
| 13 | model-theft | MEASURE 2.7 |
| 14 | model-theft | MEASURE 2.10 |
| 15 | tool-abuse | MEASURE 2.7 |
| 16 | agent-autonomy | MEASURE 2.7 |

**NOT in the class** (untouched): the entire `tachi-control-category → nist-ai-rmf` class — **31 edges at baseline** (27 Surface B table cells + 4 legacy non-table extras: `access-control → MEASURE 2.8`, `authentication → MEASURE 2.10`, `logging-audit → GOVERN 4.1`, `logging-audit → MANAGE 4.1` — citation-unsupported survivors of the same T029 mechanism, **out of F-184 scope, see follow-on discovery item**; do NOT remove) — and every other edge class (563 non-drift edges).

**Arithmetic gate**: primary 542 − 16 + 15 = **541** · total 579 − 16 + 15 = **578** · composition **541 / 37 / 0** · floor ≥500 holds (headroom 41).

## C4 — Test surgery (`tests/schemas/test_taxonomy_integrity.py`) — M1×C4 normative inventory

| # | Site (line @ HEAD) | Action |
|---|---|---|
| 1 | `CATALOG_FILENAMES` (L13) | += `"nist-ai-600-1.yaml"` |
| 2 | `TAXONOMY_ENUM` (L23) | += `"nist-ai-600-1"` |
| 3 | NEW `_sort_key_section` | Author: `"2.10"` → `(2, 10)` section-numeric key + docstring |
| 4 | `test_records_sorted` dispatch | NEW `elif filename == "nist-ai-600-1.yaml"` branch using `_sort_key_section` |
| 5 | Catalogs-fixture docstring (L82, "Load all 7 catalog YAMLs") | Update (8 or count-agnostic) |
| 6 | `test_records_sorted` docstring (L289) | Update to name the new branch |
| 7 | Assert strings (L241, L245, "not in 7-value enum") | Update (8-value or count-agnostic) |
| 8 | `_sort_key_nist` (L63–77) — code AND docstring | **BYTE-UNTOUCHED** (binding invariant) |

No new test functions. `edge_type`/`confidence` enums untouched. `PRIMARY_EDGE_FLOOR` (500) unchanged.

## C5 — Doc-surface inventory (update) + exemptions (do not touch)

**Update**:
| Surface | Change |
|---|---|
| `schemas/taxonomy/crosswalk.yaml` header | taxonomy enum list → 8 values (header L6 `taxonomy (7):` included in sweep); counts → 541 primary / 37 related / 0 superseded; retire the mid-file "Surface C DEFERRED" NOTE unit (~L2002–2007, incl. the T028/T029 reconciliation sentence) |
| `schemas/taxonomy/README.md` | NEW §3.8 provenance (DOI, 12 records, retrieval date 2026-06-10, cwe_refs rationale, quoted-id + sort convention, Gap-row omission note); §1 snippet tuple → 8 stems; §2 bullet 3 amendment note (Surface C deferred at F-180, transcribed at F-184 as 15 edges direction-corrected, 16 drift edges removed — corrects stale "(14) … 41 edges"); composition statement → 541/37/0; L13 "seven taxonomies" → eight; L20 "9 files" → 10 |
| `docs/architecture/02_ADRs/ADR-027-taxonomy-crosswalk-schema.md` | Revision History entry (self-describing, dated, full citation set) + Decision 3 additive annotation — ratified text byte-unchanged |
| `docs/architecture/README.md` (~L54) | ADR-027 blurb: "extended to 8 values at F-184, see Revision History" |
| `CHANGELOG.md` (hand-curated Unreleased) | `feat(184)` entry naming the 8th catalog + 15 edges AND the 16-edge removal |

**Exempt (zero diffs — verified at W3/W4 gates)**: `docs/architecture/01_system_design/README.md` (baseline-fixture byte-identity — Architect C2) · `specs/180-*` · ratified ADR bodies (incl. ADR-027 Decision 3 table text; ADR-025 body — its note lands at delivery; ADR-028 untouched per M2) · historical PRDs · delivered-story records · release-please CHANGELOG sections + lingering Unreleased entries.

## C6 — Acceptance oracle

`/usr/bin/python3 -m pytest tests/schemas/test_taxonomy_integrity.py` → **5/5** at every commit boundary, plus the quickstart filter/count checks (see [quickstart.md](../quickstart.md)).
