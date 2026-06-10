# Data Model: NIST AI 600-1 Surface C Transcription (F-184)

**Feature**: [spec.md](spec.md) · **Date**: 2026-06-10

No new schema. The catalog record and crosswalk edge reuse the ADR-027-frozen shapes; this feature adds one catalog file, expands the closed `taxonomy` enum 7 → 8 at its single enforcement point, populates one new edge class, and empties one defective edge class. Listed for `/aod.tasks` traceability.

---

## Entity 1 — `nist-ai-600-1` catalog record (NEW catalog, 12 records)

A record in `schemas/taxonomy/nist-ai-600-1.yaml`, one per NIST AI 600-1 §2 GAI Risk section.

| Field | Type | Constraint |
|---|---|---|
| `id` | string (**YAML-quoted**) | `"2.1"`…`"2.12"` — bare section number, no `§` prefix. Quoting is load-bearing: unquoted `2.10` parses as float `2.1` (duplicate-id collision, sort `AttributeError`, string/float referential mismatch) |
| `full_id` | string | Fully-qualified human form: `NIST AI 600-1 §2.X` (PRD FR-1 contract) |
| `name` | string | **Verbatim** from the Surface C table (`.claude/skills/tachi-shared/references/nist-ai-rmf-mapping.md`) — see contract for all 12 |
| `url` | string | Shared DOI `https://doi.org/10.6028/NIST.AI.600-1` for all 12 (FR-033 canonical-URL convention; section anchors not stable across NIST revisions) |
| `cwe_refs` | list | `[]` for all 12 — test-required field on non-CWE catalogs; AI 600-1 publishes no direct CWE cross-references |

**Validation rules**:
- Exactly 12 records; ids unique (`test_framework_yamls_load`).
- File ordered in **publication order** `"2.1"` → `"2.12"`, enforced by the new `_sort_key_section` branch of `test_records_sorted`.
- House-style header comment (model: `nist-ai-rmf.yaml`): source + retrieval date, record shape, **quoted-id rule**, sort convention, cwe_refs rationale, FR-024 pointer.

## Entity 2 — Surface C primary edge (ADD class, exactly 15)

A `crosswalk.yaml` record, direction `tachi-stride-ai-category → nist-ai-600-1`.

| Field | Value / Constraint |
|---|---|
| `source.taxonomy` | `tachi-stride-ai-category` |
| `source.id` | one of 9 distinct STRIDE+AI slugs (canonical short forms; all resolve in `tachi-stride-ai-category.yaml`, 11 records) |
| `target.taxonomy` | `nist-ai-600-1` |
| `target.id` | **quoted** `"2.4"` \| `"2.9"` \| `"2.10"` \| `"2.12"` (4 distinct targets; resolve against Entity 1) |
| `edge_type` | `primary` |
| `confidence` | `high` (existing "NIST transcription" rubric class — README rubric already names Surface B or Surface C) |
| `citation` | `.claude/skills/tachi-shared/references/nist-ai-rmf-mapping.md` (repo-file form, Surface B precedent) |

**Validation rules**: exactly the 15 contract-enumerated pairs — no more, no fewer; all `{source, target, edge_type}` triples distinct; spoofing and repudiation correctly unused; both Gap rows and all "No equivalent" rows omitted (OQ-2); 30 endpoint references total, all quoted on the target side.

## Entity 3 — Legacy drift edge (REMOVE class, exactly 16)

The defective edge class shipped at F-180 that survived T029's Option (d) MIX.

| Selector | Value |
|---|---|
| `source.taxonomy` | `tachi-stride-ai-category` |
| `target.taxonomy` | `nist-ai-rmf` |

**Disposition rules**:
- Removal is by **edge-class filter** (the two selectors above), never line-range surgery (the 16 live in two regions: Day-1 Slice 4 + T016 Batch 5).
- Pre-removal count MUST equal 16 and match the contract pair-list 1:1 (Architect-verified at HEAD `f57a9c1`); post-removal filter MUST return empty.
- **Not in the class** (untouched): the `tachi-control-category → nist-ai-rmf` class (31 edges at baseline — 27 Surface B table cells + 4 legacy non-table extras routed to a follow-on, NOT removed here) and every other edge class.
- Post-change arithmetic: primary 542 − 16 + 15 = **541**; total 579 − 16 + 15 = **578**; composition **541 / 37 / 0**.

## Entity 4 — `taxonomy` enum (7 → 8 values)

Closed enum enforced solely by `tests/schemas/test_taxonomy_integrity.py`.

| Property | Value |
|---|---|
| New value | `nist-ai-600-1` (filename stem of the new catalog) |
| Enforcement edits | `CATALOG_FILENAMES` (L13) += `"nist-ai-600-1.yaml"`; `TAXONOMY_ENUM` (L23) += `"nist-ai-600-1"` |
| Sort handling | NEW `_sort_key_section` (`"2.10"` → `(2, 10)`) + NEW `elif filename == "nist-ai-600-1.yaml"` branch in `test_records_sorted` |
| Byte-untouched invariant | `_sort_key_nist` — code AND docstring — and the `nist-ai-rmf.yaml` sort path (M1×C4 ruling) |
| String hygiene | M1×C4 normative inventory: fixture docstring L82, `test_records_sorted` docstring L289, assert strings L241/L245, new `_sort_key_section` docstring |
| Governance | ADR-027 Decision 3 extension clause → Revision History entry (Entity 5) |

## Entity 5 — ADR-027 Revision History entry (governance instrument)

| Property | Constraint |
|---|---|
| Vehicle | Dated Revision History entry (OQ-3: no standalone ADR; T027 entry precedent) |
| Self-description | MUST self-describe as the Decision 3 extension-governance instrument |
| Citations | PRD-184, Issue #184, Architect sign-off, 8-value activation, 12-record catalog, 15-edge transcription, FR-022 direction correction, FR-7 16-edge removal disposition |
| Companions (same commit) | Decision 3 additive annotation ("Amended at F-184: enum extended to 8 values — see Revision History"); `docs/architecture/README.md` ~L54 blurb update |
| Invariant | Ratified Decision text above the annotation byte-unchanged |

## State Transition (crosswalk, single coherent change-set)

```
BEFORE (HEAD f57a9c1):  542 primary / 37 related / 0 superseded = 579
                        ├─ 16 × (tachi-stride-ai-category → nist-ai-rmf)   [defective, citation-unsupported]
                        └─  0 × (tachi-stride-ai-category → nist-ai-600-1)

AFTER (W2 gate):        541 primary / 37 related / 0 superseded = 578
                        ├─  0 × (tachi-stride-ai-category → nist-ai-rmf)   [class emptied]
                        └─ 15 × (tachi-stride-ai-category → nist-ai-600-1) [contract-exact]
```

Ordering invariant (spec FR-008): Entity 1 + Entity 4 land before/with the Entity 2/3 change-set so referential integrity never breaks mid-sequence.
