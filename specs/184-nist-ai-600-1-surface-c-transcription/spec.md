---
prd_reference: docs/product/02_PRD/184-nist-ai-600-1-surface-c-transcription-2026-06-10.md
triad:
  pm_signoff:
    agent: product-manager
    date: 2026-06-10
    status: APPROVED
    notes: "Spec is 1:1 faithful to PRD v1.2: FR mapping (PRD FR-1/2/3/7/4/5/6 → spec FR-001..FR-008), 15-pair add + 16-pair remove lists verbatim, 541/578 arithmetic, M1×C4 normative inventory, OQ-1/2/3/4 ratified conditions, C2 sweep exemptions all verified. 3 spec additions ruled in-spirit (EOF deferral-comment retirement; README line-11/20 stale counts on an FR-5 inventory surface; §2.6 or/and observation routed to the OQ-4 delivery note). 4 advisory findings, none gating — key forward-guard: tasks.md W2 gate must use 541/578, not team-lead.md's stale 557/594. Details: .aod/results/product-manager.md"
  architect_signoff: null  # Added by /aod.project-plan
  techlead_signoff: null   # Added by /aod.tasks
---

# Feature Specification: NIST AI 600-1 GAI Risk Taxonomy — Surface C Transcription (F-A1.1)

**Feature Branch**: `184-nist-ai-600-1-surface-c-transcription`
**Created**: 2026-06-10
**Status**: Approved (PM sign-off 2026-06-10)
**Input**: User description: "PRD: 184 - nist-ai-600-1-surface-c-transcription"
**PRD**: `docs/product/02_PRD/184-nist-ai-600-1-surface-c-transcription-2026-06-10.md` (v1.2 — PM APPROVED; Architect + Team-Lead APPROVED_WITH_CONCERNS, all concerns folded/ruled)
**Research**: `specs/184-nist-ai-600-1-surface-c-transcription/research.md`

Adds the NIST AI 600-1 GAI Risk taxonomy as the crosswalk's 8th catalog (12 records, §§2.1–2.12), expands the frozen 7-value `taxonomy` enum to 8, transcribes the 15 verified Surface C Overlap rows as `tachi-stride-ai-category → nist-ai-600-1` primary edges, and removes the 16 legacy wrong-direction drift edges (`tachi-stride-ai-category → nist-ai-rmf`) that survived F-180's T029 cleanup — completing the Surface C transcription Feature 180 deferred, with the ADR-027 governance trail closed on the record.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - The Crosswalk Gains the NIST AI 600-1 Catalog (Priority: P1)

A compliance consumer (GRC engineer, auditor, or downstream tool) consuming `schemas/taxonomy/` needs to resolve NIST AI 600-1 GAI Risk identifiers exactly like any other taxonomy in the contract: a `nist-ai-600-1.yaml` catalog carrying all 12 GAI Risk sections with the same record shape and integrity guarantees as the existing 7 catalogs.

**Why this priority**: Without the catalog and the enum value, no Surface C edge is formable — referential integrity requires both endpoints to resolve against catalog records. This is the structural foundation every other story depends on.

**Independent Test**: Parse `schemas/taxonomy/nist-ai-600-1.yaml` and run the integrity suite — the catalog loads, validates, and sorts without any edge work having landed.

**Acceptance Scenarios**:

1. **Given** the new catalog file, **When** it is parsed, **Then** it contains exactly 12 records (§§2.1–2.12), each shaped `{id, full_id, name, url, cwe_refs: []}`, with ids as YAML-quoted strings (`"2.1"`…`"2.12"`), `name` verbatim from the Surface C table, and `url` = `https://doi.org/10.6028/NIST.AI.600-1`.
2. **Given** the integrity test, **When** it runs, **Then** `nist-ai-600-1.yaml` is loaded via `CATALOG_FILENAMES`, validated by `test_framework_yamls_load`, and sort-checked in publication order (`"2.2"` precedes `"2.10"`) via the new section-numeric sort key.
3. **Given** the 8-value enum, **When** any edge references `taxonomy: nist-ai-600-1`, **Then** `test_crosswalk_referential_integrity` resolves it against the new catalog.

---

### User Story 2 - Surface C Becomes 15 Correct Edges — and the 16 Wrong Ones Go (Priority: P1)

A consumer pivoting a tachi finding into the NIST GAI Risk framing needs every Surface C Overlap row transcribed verbatim as a `tachi-stride-ai-category → nist-ai-600-1` primary edge — and the 16 legacy `tachi-stride-ai-category → nist-ai-rmf` drift edges (citation-unsupported, wrong target taxonomy) removed, so no wrong-direction mapping cohabits with the correct ones.

**Why this priority**: This is the feature's value delivery AND the audit-credibility correction. The two move together by design (PM ruling Option A): adding the correct edges while leaving the wrong ones would half-close the audit defect and make the ADR's "direction corrected" record misleading.

**Independent Test**: Filter the crosswalk by edge class — `tachi-stride-ai-category → nist-ai-600-1` returns exactly the 15 enumerated pairs; `tachi-stride-ai-category → nist-ai-rmf` returns empty; the integrity suite passes 5/5.

**Acceptance Scenarios**:

1. **Given** the crosswalk after this feature, **When** filtering `source.taxonomy == 'tachi-stride-ai-category' AND target.taxonomy == 'nist-ai-600-1'`, **Then** exactly the 15 enumerated pairs (FR-003 table) exist, each `edge_type: primary`, `confidence: high`, `citation: .claude/skills/tachi-shared/references/nist-ai-rmf-mapping.md`, with quoted target ids.
2. **Given** the crosswalk after this feature, **When** filtering `source.taxonomy == 'tachi-stride-ai-category' AND target.taxonomy == 'nist-ai-rmf'`, **Then** the result is empty — all 16 FR-004 edges removed, and no other edge class touched (the `tachi-control-category → nist-ai-rmf` class — 31 edges at baseline — intact).
3. **Given** the transcription, **When** compared against the Surface C table row-by-row, **Then** it is verbatim — no invented, dropped, or re-authored rows; all 8 "No equivalent" rows omitted; both Gap rows omitted (OQ-2 ruling).
4. **Given** the full suite, **When** `/usr/bin/python3 -m pytest tests/schemas/test_taxonomy_integrity.py` runs, **Then** 5/5 pass: no dangling endpoint, no duplicate `{source, target, edge_type}` triple, primary floor ≥500 holds (541 after), citation shape valid.

---

### User Story 3 - The Schema Change Carries Its Governance Trail (Priority: P2)

A future maintainer or auditor asking "when and why did the taxonomy enum become 8-value, and where did the 16 drift edges go?" finds the answer in one hop: ADR-027 Revision History entry, Decision 3 annotation, README provenance, and CHANGELOG.

**Why this priority**: ADR-027 Decision 3 closed the enum "for F-A1" with extension governed by ADR amendment — the enum change is invalid without its governance instrument. Sequenced after the data work because the entry records what shipped.

**Independent Test**: Read ADR-027's Revision History, the README §3.8, and the CHANGELOG — each answers the activation + cleanup questions without consulting lore.

**Acceptance Scenarios**:

1. **Given** ADR-027, **When** reading its Revision History, **Then** a dated entry self-describes as the Decision 3 extension-governance instrument — citing PRD-184, Issue #184, the Architect sign-off, the 8-value activation, the 12-record catalog, the 15-edge transcription, the FR-022 direction correction, and the FR-7 16-edge removal disposition — and the Decision 3 heading carries the one-line additive annotation ("Amended at F-184: enum extended to 8 values — see Revision History").
2. **Given** the taxonomy README, **When** reading §3, **Then** §3.8 documents `nist-ai-600-1.yaml` provenance (DOI source, 12-record composition, retrieval date, cwe_refs rationale, quoted-id + sort convention, Gap-row omission note); the §1 snippet tuple lists 8 stems; the §2 harvest bullet carries the T027/F-184 amendment note; the edge-type composition reads 541/37/0.
3. **Given** live maintained docs, **When** grepping for "7-value" / "7 catalog", **Then** no stale count remains in the FR-006 update inventory — with the named exemptions (historical PRDs/specs, ratified ADR bodies, delivered-story records, `docs/architecture/01_system_design/README.md`) untouched.

---

### Edge Cases

- **YAML float-coercion on §2.X ids**: unquoted `id: 2.10` parses as float `2.1` → duplicate-id collision with §2.1, sort-key `AttributeError`, and string-vs-float referential mismatch. All 12 record ids AND all 30 edge endpoint references MUST be YAML-quoted strings; the rule is pinned in the catalog header comment. Failures are loud, but prevention is binding (Risk 184.5).
- **Sort order `"2.10"` vs `"2.2"`**: plain lexicographic sort puts `"2.10"` before `"2.2"`; `_sort_key_nist` cannot parse space-less `2.X` ids. A separate `_sort_key_section` key (`"2.10"` → `(2, 10)`) + a new `elif` branch handles the new file; `_sort_key_nist` and the `nist-ai-rmf.yaml` path stay byte-untouched (OQ-1 as refined by Team-Lead C4; M1×C4 ruling).
- **Gap rows**: §2.6 has no tachi-category endpoint (edge un-formable under referential integrity); §2.9×Spoofing would be the crosswalk's first `low`-confidence edge. Both omitted (OQ-2 ruling); documented in README §3.8, not transcribed.
- **"No equivalent" rows** (7 risk-level + §2.9×Repudiation): omitted by design — their absence is the deliberate scope boundary the reference instructs auditors to note.
- **Stale reference prose**: the reference's "§2.9 — 8 of 11 categories overlap" line is stale (table yields 9). Transcription follows the **table** (T027-re-verified 15 Overlap rows). The prose correction routes to a one-line ADR-025 amendment note at delivery (OQ-4) — never a silent reference edit here (FR-024).
- **§2.6 name "or"/"and" discrepancy**: NIST's PDF titles §2.6 "Harmful Bias **and** Homogenization"; the in-repo Surface C table (the verbatim source) says "**or**". The catalog transcribes the reference verbatim ("or", per FR-024 + the PRD FR-1 contract); the observation routes with the OQ-4 ADR-025 note at delivery.
- **Mid-sequence integrity**: an edge referencing `nist-ai-600-1` before the catalog + enum land would break referential integrity. Build ordering is binding: catalog + test surgery land before/with the edge change-set (FR-003 additions + FR-004 removals as one coherent change-set).
- **Baseline-fixture coupling**: `docs/architecture/01_system_design/README.md` ships byte-identically inside `tests/fixtures/init-baseline-tree/`; editing it without regenerating the baseline breaks `tests/scripts/test_init_sh_substitution.py`. It is **exempt** from the stale-count sweep (Architect C2) — its "7-value" statements are true statements about the past decision.
- **Crosswalk deferral comment**: `crosswalk.yaml` carries a mid-file "Surface C DEFERRED" NOTE unit (~lines 2002–2007, incl. the T028/T029 reconciliation sentence) explaining the missing enum value. It must be retired/superseded when the transcription lands, or it becomes the new stale prose.
- **Removal precision**: the FR-004 removal class is exactly `{source.taxonomy == tachi-stride-ai-category, target.taxonomy == nist-ai-rmf}` — execute as an edge-class filter verified by count (16) and pair-list match, never line-range surgery. Surface B (`tachi-control-category → nist-ai-rmf`) is a different class and stays.

## Requirements *(mandatory)*

### Functional Requirements

> **Acceptance Criteria Rule**: Each AC MUST begin with **Given** and follow Given/When/Then structure. Use `[MANUAL-ONLY] <reason>` (reason ≥10 chars) inline to mark ACs that cannot be automated.

- **FR-001**: The system MUST gain `schemas/taxonomy/nist-ai-600-1.yaml` carrying exactly 12 records — one per NIST AI 600-1 §2 GAI Risk section (§2.1 CBRN Information or Capabilities · §2.2 Confabulation · §2.3 Dangerous, Violent, or Hateful Content · §2.4 Data Privacy · §2.5 Environmental Impacts · §2.6 Harmful Bias or Homogenization · §2.7 Human-AI Configuration · §2.8 Information Integrity · §2.9 Information Security · §2.10 Intellectual Property · §2.11 Obscene, Degrading, and/or Abusive Content · §2.12 Value Chain and Component Integration), names verbatim from the Surface C table.
  - Record shape `{id, full_id, name, url, cwe_refs: []}` (`cwe_refs` is test-required on non-CWE catalogs; AI 600-1 publishes no direct CWE cross-references).
  - Ids are **YAML-quoted strings** `"2.1"`…`"2.12"` — bare section number, no `§` prefix. The quoting is load-bearing (float-coercion), pinned in the header comment.
  - `full_id` carries the fully-qualified human form (e.g., `NIST AI 600-1 §2.9`).
  - `url` = shared DOI `https://doi.org/10.6028/NIST.AI.600-1` for all 12 records (FR-033 canonical-URL convention, mirroring `nist-ai-rmf.yaml`).
  - File ordered in publication order (`"2.1"` … `"2.12"`), enforced by FR-002's sort key.
  - House-style header comment (model: `nist-ai-rmf.yaml` lines 1–44): source + retrieval date, record shape, quoted-id rule, sort convention, cwe_refs rationale, FR-024 pointer.
  - **AC**: **Given** the catalog file, **When** parsed and validated by the integrity suite, **Then** 12 records load with the exact shape, quoted ids, verbatim names, DOI url, and publication order.

- **FR-002**: The integrity test `tests/schemas/test_taxonomy_integrity.py` MUST be expanded from the 7-catalog to the 8-catalog world — it is the enum's single enforcement point (Architect-verified: the only code surface hardcoding taxonomy stems).
  - `CATALOG_FILENAMES` (line 13) += `"nist-ai-600-1.yaml"`; `TAXONOMY_ENUM` (line 23) += `"nist-ai-600-1"`.
  - Sort handling (OQ-1 ruling, Option A as refined by Team-Lead C4): add a **separate** section-numeric sort-key function `_sort_key_section` (`"2.10"` → `(2, 10)`) plus a new `elif filename == "nist-ai-600-1.yaml"` branch in `test_records_sorted`.
  - **Normative stale-string inventory (M1×C4 ruling — binding, supersedes the PRD FR-2 sentence)**: (1) catalogs-fixture docstring line 82 ("Load all 7 catalog YAMLs") — update; (2) `test_records_sorted` docstring line 289 — update to name the new branch; (3) the two assert strings lines 241/245 ("not in 7-value enum") — update (8-value or count-agnostic); (4) the NEW `_sort_key_section` docstring — author; (5) `_sort_key_nist` — **code AND docstring byte-untouched**.
  - No new test functions; `edge_type`/`confidence` enums untouched.
  - **AC**: **Given** the expanded test, **When** the suite runs against the 8 catalogs, **Then** 5/5 pass, the diff to `_sort_key_nist` and the `nist-ai-rmf.yaml` sort path is empty, and no "7-value"/"7 catalog" string remains in the file.

- **FR-003**: The crosswalk MUST gain exactly 15 Surface C primary edges, direction `tachi-stride-ai-category → nist-ai-600-1`, transcribed verbatim from the Surface C Overlap rows (the FR-022 direction correction this feature's PRD ratifies). The pre-enumerated contract (Architect-verified 1:1 against the table):

  | # | source.id | target.id | GAI Risk |
  |---|---|---|---|
  | 1 | info-disclosure | "2.4" | Data Privacy |
  | 2 | tampering | "2.9" | Information Security |
  | 3 | info-disclosure | "2.9" | Information Security |
  | 4 | denial-of-service | "2.9" | Information Security |
  | 5 | prompt-injection | "2.9" | Information Security |
  | 6 | data-poisoning | "2.9" | Information Security |
  | 7 | privilege-escalation | "2.9" | Information Security |
  | 8 | model-theft | "2.9" | Information Security |
  | 9 | agent-autonomy | "2.9" | Information Security |
  | 10 | tool-abuse | "2.9" | Information Security |
  | 11 | model-theft | "2.10" | Intellectual Property |
  | 12 | info-disclosure | "2.10" | Intellectual Property |
  | 13 | tool-abuse | "2.12" | Value Chain and Component Integration |
  | 14 | tampering | "2.12" | Value Chain and Component Integration |
  | 15 | data-poisoning | "2.12" | Value Chain and Component Integration |

  - Every edge: `edge_type: primary`, `confidence: high` (existing "NIST transcription" rubric class — README line 136 already names Surface B or Surface C), `citation: .claude/skills/tachi-shared/references/nist-ai-rmf-mapping.md`, target ids quoted.
  - All 15 `{source, target, edge_type}` triples distinct; 9 distinct source ids (spoofing and repudiation correctly unused); 4 distinct targets; 30 endpoint references total.
  - "No equivalent" rows and both Gap rows omitted (OQ-2).
  - **AC**: **Given** the crosswalk, **When** filtering the new edge class, **Then** exactly these 15 pairs exist with the exact field values, and a row-by-row comparison against the Surface C table shows verbatim fidelity.

- **FR-004**: The 16 legacy drift edges MUST be removed in the same change-set (PRD FR-7, PM ruling Option A — completes the standing T027 removal directive that T029's Option (d) MIX left unfinished). The removal class is exactly `{source.taxonomy == tachi-stride-ai-category, target.taxonomy == nist-ai-rmf}` — 16 edges, no more, no fewer (Architect-verified 1:1 at HEAD `f57a9c1`): prompt-injection → MEASURE 2.6, MEASURE 2.7 · data-poisoning → MEASURE 2.7, MEASURE 2.8 · spoofing → MEASURE 2.7 · tampering → MEASURE 2.7, MEASURE 2.8 · repudiation → MEASURE 2.8 · info-disclosure → MEASURE 2.7, MEASURE 2.10 · denial-of-service → MEASURE 2.7 · privilege-escalation → MEASURE 2.7 · model-theft → MEASURE 2.7, MEASURE 2.10 · tool-abuse → MEASURE 2.7 · agent-autonomy → MEASURE 2.7.
  - The `tachi-control-category → nist-ai-rmf` class (31 edges at baseline: 27 Surface B table cells + 4 legacy non-table extras routed to a follow-on discovery item — Architect plan-review F1) and every other edge class untouched.
  - Net arithmetic: primary 542 − 16 + 15 = **541** (≥500 floor holds, 41 headroom); total 579 − 16 + 15 = **578**; composition 541/37/0.
  - Disclosure (Constitution III): CHANGELOG names the removal explicitly; the ADR-027 revision entry records the disposition; the PRD's PM sign-off is the re-sign. Correction of defective shipped data, disclosed — not a silent compatibility break.
  - **AC**: **Given** the crosswalk after the change-set, **When** filtering `tachi-stride-ai-category → nist-ai-rmf`, **Then** the result is empty, the removed set matches the 16-pair list exactly, and total counts are 541 primary / 37 related / 0 superseded.

- **FR-005**: ADR-027 MUST be amended via its Revision History (OQ-3 ruling — no standalone ADR), with three binding conditions in the same commit:
  - One dated Revision History entry at the F-184 merge that **self-describes as the Decision 3 extension-governance instrument**, citing: PRD-184, Issue #184, the Architect sign-off, the 8-value enum activation, the 12-record catalog, the 15 Surface C edges, the FR-022 direction correction, and the FR-7 16-edge removal disposition.
  - A one-line additive annotation under the Decision 3 heading: "Amended at F-184: enum extended to 8 values — see Revision History" (additive pointer; ratified Decision 3 text not retro-edited).
  - The ADR-027 index blurb at `docs/architecture/README.md` (line ~54) updated ("extended to 8 values at F-184, see Revision History").
  - **AC**: **Given** ADR-027 and the index, **When** read after merge, **Then** the entry, annotation, and blurb answer the activation + cleanup questions in one hop, and ADR-027's ratified Decision text above the annotation is byte-unchanged.

- **FR-006**: Documentation MUST reach the 8-catalog world on every live, maintained surface — and ONLY those (sweep inventory Architect-verified):
  - `schemas/taxonomy/crosswalk.yaml` header comment: taxonomy list 8 values; counts 541/37/0; retire the mid-file "Surface C DEFERRED" NOTE unit (~lines 2002–2007).
  - `schemas/taxonomy/README.md`: new §3.8 provenance (DOI source, 12-record composition, retrieval date, cwe_refs rationale, quoted-id + sort convention, Gap-row omission note); §1 snippet tuple → 8 stems; §2 harvest bullet 3 amendment note (Surface C deferred at F-180; transcribed here as 15 edges with direction corrected; 16 legacy drift edges removed — corrects the stale "(14) … 41 edges" text); edge-type composition (line ~243) → 541/37/0; "seven taxonomies" (line 13) and "9 files" (line 20) counts → 8 taxonomies / 10 files.
  - Integrity-test strings/docstrings per FR-002's inventory.
  - `docs/architecture/README.md:~54` blurb per FR-005.
  - **Exempt (do not touch)**: `docs/architecture/01_system_design/README.md` (historical narrative + init.sh baseline-fixture byte-identity coupling — Architect C2); `specs/180-*` historical records; delivered-story records; ratified ADR bodies (ADR-027's own Decision 3 table text included); historical PRDs; release-please CHANGELOG sections and lingering Unreleased entries (dual-CHANGELOG model).
  - **AC**: **Given** the FR-006 inventory surfaces, **When** grepping "7-value" / "7 catalog" / "seven taxonomies" / stale counts (542/579), **Then** zero stale hits remain on inventory surfaces and zero diffs exist on exempt surfaces.

- **FR-007**: The change MUST be disclosed and closed: CHANGELOG hand-curated Unreleased section gains a `feat(184)` entry naming BOTH the additions (8th catalog, 15 edges) and the 16-edge removal; Issue #184 closes `stage:done` at delivery with the OQ-4 ADR-025 prose-note disposition recorded (one-line amendment note: "8 of 11" → "9 of 11" arithmetic + Gap-granularity clarification + §2.6 and/or naming observation). [MANUAL-ONLY: issue closure and ADR-025 note are delivery-stage actions outside the build diff]

- **FR-008**: The integrity suite MUST stay green throughout: `/usr/bin/python3 -m pytest tests/schemas/test_taxonomy_integrity.py` (interpreter pin — Team-Lead C5: default `python3` lacks pytest/pyyaml; baseline 5/5 in ~1s) passes 5/5 at every commit boundary. Build ordering binding: catalog + test surgery land before/with the edge change-set (FR-003 + FR-004 as one coherent change-set) so referential integrity never breaks mid-sequence.
  - **AC**: **Given** any commit on the feature branch after the catalog lands, **When** the suite runs, **Then** 5/5 pass — including the 8-catalog load, the ≥500 primary floor (541), all 30 new endpoint resolutions, citation shape, and publication-order sort.

### Key Entities

- **Taxonomy catalog record**: `{id, full_id, name, url, cwe_refs}` — one per GAI Risk section; `id` is a quoted string `"2.X"`; joins the 7 existing catalogs under identical integrity guarantees.
- **Crosswalk edge**: `{source: {taxonomy, id}, target: {taxonomy, id}, edge_type, confidence, citation}` — 15 added (`tachi-stride-ai-category → nist-ai-600-1`, primary/high), 16 removed (`tachi-stride-ai-category → nist-ai-rmf`).
- **Taxonomy enum**: closed 8-value set enforced solely by `tests/schemas/test_taxonomy_integrity.py`; extension governed by ADR-027 Decision 3 + Revision History.
- **ADR-027 Revision History entry**: the governance instrument for the enum change — self-describing, dated, citing the full activation + cleanup record.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: `schemas/taxonomy/nist-ai-600-1.yaml` exists with exactly 12 records, 5-field shape, quoted-string ids, shared DOI URL, publication order, house-style header.
- **SC-002**: The `taxonomy` enum is 8-value at its single enforcement point; the M1×C4 stale-string inventory is fully applied; `_sort_key_nist` (code + docstring) and the `nist-ai-rmf.yaml` sort path are byte-untouched.
- **SC-003**: Crosswalk filter `tachi-stride-ai-category → nist-ai-600-1` returns exactly the 15 enumerated pairs (primary/high, reference citation, quoted ids); filter `tachi-stride-ai-category → nist-ai-rmf` returns empty.
- **SC-004**: Edge arithmetic holds: 541 primary / 37 related / 0 superseded = 578 total; ≥500 primary floor with 41 headroom; 0 dangling endpoints; 0 duplicate triples.
- **SC-005**: `/usr/bin/python3 -m pytest tests/schemas/test_taxonomy_integrity.py` → 5/5 green; `/aod.analyze` passes.
- **SC-006**: ADR-027 Revision History entry + Decision 3 additive annotation + `docs/architecture/README.md` blurb land in the same commit; ratified Decision text byte-unchanged.
- **SC-007**: README §3.8 + §1 snippet (8 stems) + §2 amendment + composition (541/37/0) complete; zero stale "7-value"/"7 catalog" hits on FR-006 inventory surfaces; zero diffs on exempt surfaces (byte-identity test for the baseline fixture still green).
- **SC-008**: CHANGELOG `feat(184)` names additions AND removal; Issue #184 closed `stage:done` with the OQ-4 disposition recorded at delivery.

## Assumptions

- The Surface C table in `nist-ai-rmf-mapping.md` is the verbatim source of truth (15 Overlap / 2 Gap / 8 No-equivalent — re-verified by both reviewers 2026-06-10); no re-verification against the NIST PDF is in scope (ADR-025 maintenance triggers govern).
- NIST AI 600-1 (July 2024) remains the current revision (web-verified 2026-06-10); the DOI is citation-only, never fetched (ADR-021 determinism).
- No consumer outside the integrity test hardcodes the 7-value enum (Architect-verified across .py/.sh/.json; SARIF generator scripts have no production caller).
- F-180 (parent), F-186, F-182 are DELIVERED; #182's deferral trail routes nothing here; zero open PRs collide with the write-set (Team-Lead-verified).

## Out of Scope

- **#185 (`cwe.yaml` expansion)** — sibling, separate PRD; **serialize, don't interleave** (shared crosswalk/README/CHANGELOG surfaces — Team-Lead C2).
- **#183 (citation link-rot monitoring)** — Wave-3 tooling.
- **Surface A / Surface B changes** — Surface B's 27 edges shipped at F-180, untouched.
- **Re-authoring Surface C content** — FR-024 discipline; factual corrections route to the OQ-4 ADR-025 amendment note.
- **`related`/`superseded` edges** — F-182's arc; both Gap rows omitted (no first-`low` edge authored).
- **ADR-028's `source_attribution` enum** — NOT extended (Architect M2).
- **New standalone ADR** — ruled out (OQ-3); the ADR-027 revision-entry instrument governs.
- **`docs/architecture/01_system_design/README.md`** — sweep-exempt (Architect C2).
- **New test functions, schema scripts, web-researcher or security-analyst lanes** — data-layer YAML change with existing suite as the acceptance oracle.
