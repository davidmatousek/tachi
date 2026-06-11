---
prd:
  number: "184"
  topic: nist-ai-600-1-surface-c-transcription
  created: 2026-06-10
  status: Delivered
  delivered: 2026-06-11
  pr: 324
  merge_commit: db1bba5
  release: 4.43.0
  type: feature
triad:
  pm_signoff: { agent: product-manager, date: 2026-06-10, status: APPROVED, notes: "Author sign-off (v1.1). Scope = BLP-05 Wave 2 (#184), standalone per the user's /aod.define 184 invocation (split-valve; #185 stays a sibling). Completes F-180's deferred Surface C under the T027 Option (c) follow-on contract: 8th catalog (12 GAI Risk records), 7→8 enum expansion, FR-022 direction correction, 15 verbatim primary edges — PLUS the FR-7 disposition the Architect's C1 surfaced: the 16 wrong-direction drift edges were never removed at T029 (Option (d) MIX normalized them); PM rules Option A, remove in-scope (541 primary / 578 total after). Five issue-body corrections (C-a–C-e) verified. This PRD is the PM re-sign vehicle for the FR-022 direction amendment AND the drift-edge removal disclosure." }
  architect_signoff: { agent: architect, date: 2026-06-10, status: APPROVED_WITH_CONCERNS, notes: "Re-review of v1.1 after v1.0 CHANGES_REQUESTED: all prior requirements verified folded (C1 a–d incl. FR-7 Option A disposition + 541/578 recompute, C2 sweep exemptions, M1–M3, OQ-1/2/3/4 ratification conditions); FR-7's 16-edge removal list verified 1:1 exact via fresh YAML parse at HEAD f57a9c1 (all primary/high; 0 pre-existing nist-ai-600-1 edges; 0 low-confidence edges); no stale 557/594 figures; Team-Lead C4 refinement of OQ-1 Option A ACCEPTED (separate _sort_key_section + new elif; RMF path zero-regression). 1 concern, ruled and folded into v1.2: M1×C4 docstring tension — byte-untouched wins, _sort_key_nist docstring NOT updated; normative stale-string inventory in .aod/results/architect.md; encode at /aod.plan. No further cycle needed. Details: .aod/results/architect.md" }
  techlead_signoff: { agent: team-lead, date: 2026-06-10, status: APPROVED_WITH_CONCERNS, notes: "Feasibility APPROVED, no timeline/capacity veto. Envelope 0.75–1.25 d accepted; realistic point 0.75–1.0 d (expect same-day actual per #186/#182 anchors); +0.1–0.15 d for FR-7 Option A stays inside the ceiling. 5 advisory concerns all folded into v1.1: (1) realistic-point calibration; (2) serialize #185 — crosswalk/README/CHANGELOG are shared surfaces, disjoint only at catalog-file level; (3) YAML float-coercion — quote all §2.X ids (2.10 parses as float 2.1 unquoted); (4) OQ-1 Option A via separate sort-key fn + new elif, leave _sort_key_nist/RMF path byte-untouched; (5) interpreter pin /usr/bin/python3 at W0 (default python3 lacks pytest; baseline verified 5/5 in 1.02s). Agent plan W0–W4 single senior-backend-engineer + checkpoint gates, ~12–14 tasks, ready for agent-assignments.md. Details: .aod/results/team-lead.md" }
source:
  idea_id: 184
  story_id: null
---

# NIST AI 600-1 GAI Risk Taxonomy Addition — Surface C Transcription (F-A1.1 Follow-on)

**Status**: Delivered (2026-06-11 — PR [#324](https://github.com/davidmatousek/tachi/pull/324) squash-merged as `db1bba5`; release-please PR #326 → v4.43.0; Issue #184 closed. Triad at approval: PM ✓ / Architect ⚠ / Team-Lead ⚠, v1.1/v1.2 fold all corrections)
**Created**: 2026-06-10
**Author**: product-manager
**Reviewers**: architect, team-lead
**Priority**: P2 (Light) — BLP-05 Wave 2 (Crosswalk Catalog Expansion)
**Evidence**: Issue [#184](https://github.com/davidmatousek/tachi/issues/184) (`follow-on-180`), filed at Feature 180 T034 per the Architect's T027 Option (c) decision. Source scope: ADR-027 Revision History (T027 Surface C amendment) + F-180 spec SC-008 amendment + `pm_signoff_amendment_2`. Strategic home: `_internal/strategy/BLP-05-framework-mapping-and-output-fidelity.md` §Wave 2.

---

## Executive Summary

### The One-Liner
Add the **NIST AI 600-1 GAI Risk taxonomy** as the crosswalk's **8th catalog** (12 records, §§2.1–2.12), expand the frozen 7-value `taxonomy` enum to **8 values**, transcribe the **15 verified Surface C Overlap rows** as `tachi-stride-ai-category → nist-ai-600-1` primary edges — and **retire the 16 wrong-direction drift edges** that survived T029 — completing the Surface C transcription Feature 180 deferred, in the semantically correct direction and with the legacy drift finally cleared.

### Problem Statement
Feature 180 (F-A1 Taxonomy Crosswalk Collection, PR #181) shipped with **Surface C transcription deferred**. At T027, implementation surfaced a structural blocker: Surface C of `nist-ai-rmf-mapping.md` maps tachi STRIDE+AI categories to **NIST AI 600-1 §2.X GAI Risk identifiers** — a *distinct taxonomy* from the AI RMF 1.0 Subcategories that `nist-ai-rmf.yaml` carries. The closed 7-value `taxonomy` enum had no `nist-ai-600-1` value, and 16 pre-existing Surface C edges had **drifted to the wrong target taxonomy** (`tachi-stride-ai-category → nist-ai-rmf`).

The problem at HEAD is therefore **two-sided** (Correction C-e):

1. **The correct mapping is absent.** The reference file's own audit guidance says *"For regulatory audit: cite the Surface C Overlap rows for §§2.4, 2.9, 2.10, 2.12"* — but those rows exist only as prose. A compliance consumer pivoting tachi findings to the NIST Generative AI Profile finds no crosswalk edges and no catalog records to resolve them against.
2. **The wrong mapping is present.** T027 ordered "REMOVE all 16 Surface C drifted edges" at T029 — but T029 actually executed the Architect's **Option (d) MIX** (normalize → remove-unresolvable → dedupe). The 22 Surface B drifted edges died as post-normalize duplicates of canonical twins; the 16 Surface C drifted edges had **no canonical twins** (Surface C was deferred), so normalization made them *resolvable* and they survived every gate. **Verified live at HEAD (YAML parse, 2026-06-10): 16 `tachi-stride-ai-category → nist-ai-rmf` edges, all `primary`/`high`, all citing `nist-ai-rmf-mapping.md` — which contains no surface mapping STRIDE+AI categories to AI RMF Subcategories.** They are citation-unsupported drift (FR-013 violation) with a standing removal directive against them. A consumer filtering `prompt-injection → nist-*` today gets `MEASURE 2.7` — a mapping the cited source does not support.

### Proposed Solution
Five bounded parts, honoring F-180's verbatim-transcription discipline (FR-024: transcription, not re-authorship):

1. **8th catalog**: `schemas/taxonomy/nist-ai-600-1.yaml` — 12 records, one per GAI Risk section §§2.1–2.12, shaped `{id, full_id, name, url, cwe_refs: []}`, ids as **YAML-quoted strings** `"2.1"`…`"2.12"`, `url` = the NIST DOI `https://doi.org/10.6028/NIST.AI.600-1` (FR-033 canonical pattern, mirroring `nist-ai-rmf.yaml`).
2. **Enum expansion 7 → 8**: add `nist-ai-600-1` to the closed `taxonomy` enum in the integrity test (its single enforcement point). Additive schema-minor change under ADR-027 Decision 3's extension-governance clause, recorded via an **ADR-027 Revision History entry** at merge (OQ-3 ruling: no standalone ADR).
3. **FR-022 direction correction**: Surface C edges transcribe as `tachi-stride-ai-category → nist-ai-600-1`, superseding F-180 FR-022's conflated `→ nist-ai-rmf` direction. **This PRD is the PM re-sign vehicle** the issue's governance section requires.
4. **Verbatim transcription**: the 15 Surface C Overlap rows (T027-re-verified count) become 15 `primary` edges with `confidence: high` and `citation: .claude/skills/tachi-shared/references/nist-ai-rmf-mapping.md` (Surface B precedent).
5. **Legacy-drift disposition (FR-7, PM ruling: Option A)**: remove the 16 surviving wrong-direction edges in the same change-set, completing the standing T027 removal directive. Disclosed via CHANGELOG + the ADR-027 revision entry + this PRD's PM re-sign (Constitution III analysis: correction of defective shipped data, not a compatibility break).

### Corrections to the Issue Body (Discovered at Definition + Architect Review)
Five claims in Issue #184 do not survive contact with the current codebase. C-a–C-d were surfaced at definition and **verified accurate by the Architect**; C-e was surfaced by the Architect's C1 and verified by direct YAML parse:

| # | Issue claim | Verified reality (2026-06-10) |
|---|---|---|
| C-a | "Integrity test already covers the new catalog file via FR-030's **generic catalog-loading pattern**" | **False.** `tests/schemas/test_taxonomy_integrity.py` hardcodes both `CATALOG_FILENAMES` (line 13) and `TAXONOMY_ENUM` (line 23). Both MUST be edited or the new taxonomy fails referential integrity and the new file is never validated. Two "7-value enum" assert strings (lines ~240/244), the "Load all 7 catalog YAMLs" fixture docstring, and (M1) the `test_records_sorted` + `_sort_key_nist` docstrings also go stale. |
| C-b | Records shaped "`{id, full_id, name, url}` per FR-2" | **Incomplete.** `test_framework_yamls_load` REQUIRES `cwe_refs` on every non-CWE catalog record (empty list passes). Shape is 5-field: `{id, full_id, name, url, cwe_refs: []}` — same posture as `nist-ai-rmf.yaml`. |
| C-c | ID convention "follows the §2.X section anchors" (silent on ordering) | **Sort decision required.** `test_records_sorted` applies plain lexicographic sort to non-RMF catalogs (`2.10` before `2.2`), and `_sort_key_nist` cannot parse space-less `2.X` ids (falls back to string sort). Ruled at review — see Resolved OQ-1. |
| C-d | "Optional: **2 Gap rows** may be transcribed as `edge_type: related`" | **Overstated by one.** §2.6's tachi-category column is "No equivalent" — no source endpoint exists, the edge is un-formable under referential integrity. Only §2.9 × Spoofing is edge-formable. Ruled at review: omit both — see Resolved OQ-2. |
| C-e | "Option (c) … **removed the 16 drifted Surface C edges at T029**" | **False — they are live at HEAD.** T029 executed Option (d) MIX: normalization made the 16 resolvable (no canonical twins to dedupe against, since Surface C was deferred) and they survived. Verified by YAML parse: 16 `tachi-stride-ai-category → nist-ai-rmf` primary/high edges (2 in Day-1 Slice 4; 14 in the T016 Batch 5 block). F-186/F-182 never touched them. Dispositioned by FR-7 (Option A: remove in-scope). |

### Success Criteria
- `schemas/taxonomy/nist-ai-600-1.yaml` exists with exactly **12 records** (§§2.1–2.12), 5-field shape, quoted-string ids, DOI URL, house-style header comment.
- The `taxonomy` enum is **8-value** in the integrity test (`CATALOG_FILENAMES` + `TAXONOMY_ENUM` + string/docstring hygiene), with sort handling per the OQ-1 ruling (separate section-numeric sort key; RMF path untouched).
- **15 Surface C primary edges** in `crosswalk.yaml`, direction `tachi-stride-ai-category → nist-ai-600-1`, `confidence: high`, citation to the mapping reference — and **0 `tachi-stride-ai-category → nist-ai-rmf` edges remain** (FR-7 removal complete).
- Edge arithmetic: primary 542 − 16 + 15 = **541** (≥500 floor holds); total 579 − 16 + 15 = **578**; composition 541 primary / 37 related / 0 superseded.
- **ADR-027 Revision History entry** at merge: 8-value activation, 15-edge transcription, FR-022 direction correction, 16-edge removal disposition; plus the one-line additive annotation under the Decision 3 heading and the `docs/architecture/README.md` index-blurb update (OQ-3 conditions).
- README updated (§3.8 provenance, §1 snippet tuple → 8 stems, §2 harvest-note amendment, composition 541/37/0); `crosswalk.yaml` header counts current; stale "7-value / 7 catalog" counts swept in **live maintained** surfaces only — `docs/architecture/01_system_design/README.md` is **exempt** (historical narrative + init.sh baseline-fixture coupling, Architect C2).
- `tests/schemas/test_taxonomy_integrity.py` **5/5 green** (via `/usr/bin/python3`); `/aod.analyze` passes; CHANGELOG carries `feat(184)`; Issue #184 closed `stage:done` with the OQ-4 ADR-025 prose-note disposition recorded.

### Timeline
Envelope **0.75–1.25 days**; realistic point **~1.0 day** with FR-7 folded (Team-Lead calibration: 0.75–1.0 d for the v1.0 scope, both sibling anchors delivered same-day; Architect: +0.1–0.15 d for the Option A removals, which are mechanical and pre-located). Expect same-day Plan→Build→Deliver. The cost centers are the governance/doc trail and test surgery, not the data authoring (15 pre-enumerated verbatim edges ≈ 0.5 h). Do not promise the 0.5 d optimistic floor — the governance trail makes it not credible (Team-Lead ruling).

---

## Strategic Alignment

### Product Vision Alignment
**Reference**: [product-vision.md](docs/product/01_Product_Vision/product-vision.md)

Tachi's positioning is the **upstream machine-readable contract** that AI-security tooling consumes. NIST AI 600-1 is the Generative AI Profile — the taxonomy compliance teams cite when asking "where does this AI risk sit in NIST's GAI framing?" Today tachi answers that question only in prose while simultaneously carrying 16 machine-readable edges that answer it **wrong**. After #184, every Surface C Overlap row is a resolvable, citable edge and the wrong answers are gone — the "more *connected*" leg of BLP-05's thesis, applied with the audit-credibility bar the contract positioning demands.

### Roadmap Fit
**Wave 2 of BLP-05 (Framework Mapping & Output Fidelity)** — catalog expansion. Wave status: #186 (MITRE ATT&CK + ATLAS) DELIVERED 2026-06-07 (v4.42.0); **#184 (this) + #185 (`cwe.yaml`) remain**, standalone-runnable per the blueprint's split-valve guidance. Scoped **standalone (#184 only)** per the user's `/aod.define 184` invocation. **Scheduling directive (Team-Lead C2): serialize the siblings** — `crosswalk.yaml`, `schemas/taxonomy/README.md`, and `CHANGELOG.md` are shared surfaces with the future #185 (disjoint only at the catalog-file level); do not start #185's build mid-#184. Either order is fine; #185 has no PRD yet, so this costs nothing.

### Predecessor Relationship
| Feature / Issue | Relationship |
|---|---|
| 180 (F-A1, PR #181) | **Parent.** Deferred Surface C at T027 Option (c); T029 executed Option (d) MIX — Surface B drift died as post-normalize duplicates, the 16 Surface C drift edges survived (C-e); filed #184 at T034. This feature completes the deferral AND the unfinished removal directive. |
| 186 (Wave-2 sibling, delivered) | Record-expansion precedent — **contrast**: #186 added records to *existing* catalogs (no enum change, no ADR per its FR-008); #184 adds a *new taxonomy* (enum change → ADR-027 revision entry + Architect re-sign). F-186 did not touch the 16 drift edges (verified). |
| 182 (Wave-3 sibling, delivered) | Its `deferred-superseded.md` trail routes **nothing to #184** (verified). No inherited `superseded` obligations; the new taxonomy has no historical records. F-182 did not touch the 16 drift edges (verified). |
| ADR-025 (NIST AI RMF evaluation) | Surface C structure source — **unchanged** (FR-024: corrections route to ADR-025 amendment notes/Issues; OQ-4 ruling routes the stale "8 of 11" prose there at delivery). |
| ADR-027 (Taxonomy crosswalk schema) | The enum-expansion vehicle. Decision 3 closed the enum "for F-A1" and governs extension; the T027 revision entry pre-scoped exactly this follow-on. Amended by a Revision History entry + Decision 3 inline annotation at merge (OQ-3 ruling). |
| ADR-028 (source-attribution schema) | **Explicitly untouched** (Architect M2): its 5-value `source_attribution` taxonomy enum is a *different* enum; `nist-ai-600-1` joining finding-level attribution is a separate future decision. Named here to preempt implementer/consumer confusion. |

---

## Target Users & Personas

### Primary Persona: Compliance / Regulatory-Audit Consumer
- **Role**: A GRC engineer or auditor mapping tachi findings onto the NIST Generative AI Profile (AI 600-1) for procurement responses or regulatory audit.
- **Goal**: Cite a machine-resolvable edge from a tachi STRIDE+AI category to the GAI Risk section it addresses (§2.4 Data Privacy, §2.9 Information Security, §2.10 Intellectual Property, §2.12 Value Chain).
- **Pain Point**: The correct mapping exists only in a prose reference file — while the crosswalk their tooling actually consumes carries 16 high-confidence edges to the **wrong NIST taxonomy tier**, unsupported by their own citation.

**Why This Matters**: AI 600-1 §2.9 *explicitly names* "prompt injection" and "data poisoning" — the strongest AI-specific cross-mapping tachi has to any NIST taxonomy. Leaving it out of the contract while wrong-direction edges cohabit undercuts exactly the audience BLP-05 targets.

### Secondary Persona: Downstream Tool / Crosswalk Consumer
- **Role**: An AI-security tool, SIEM enrichment, or compliance mapper traversing `crosswalk.yaml`.
- **Goal**: Resolve `nist-ai-600-1` endpoints programmatically — closed-enum filterable, referentially intact, zero interpretation logic.
- **Pain Point**: A taxonomy referenced in tachi's docs but absent from the enum is unresolvable by construction; a `→ nist-ai-rmf` result for a STRIDE+AI category is silently misleading.

### Tertiary Persona: Taxonomy Steward / Maintainer
- **Role**: Maintainer of the F-180 decision trail and ADR-027 schema governance.
- **Goal**: Close the T027/T029/T034 loop with the enum expansion AND the drift removal recorded in the ADR's Revision History — deferral → follow-on → activation + cleanup, continuous on the record.
- **Pain Point**: An open `follow-on-180` Issue carrying five stale technical claims (C-a–C-e) invites a future implementer to start from wrong assumptions — including believing a cleanup happened that didn't.

---

## User Stories

### US-1: The Crosswalk Gains the NIST AI 600-1 Catalog (8th Taxonomy)
**When** I consume `schemas/taxonomy/` to resolve framework identifiers,
**I want** a `nist-ai-600-1.yaml` catalog carrying all 12 GAI Risk sections with the same record shape and integrity guarantees as the existing 7 catalogs,
**So I can** resolve AI 600-1 endpoints exactly like any other taxonomy in the contract.

**Acceptance Criteria**:
- **Given** the catalog file, **when** I parse it, **then** it contains exactly 12 records (§§2.1–2.12), each shaped `{id, full_id, name, url, cwe_refs: []}` with ids as quoted strings (`"2.1"`…`"2.12"`), `name` verbatim from the Surface C table, and `url` the NIST DOI.
- **Given** the integrity test, **when** it runs, **then** `nist-ai-600-1.yaml` is loaded via `CATALOG_FILENAMES`, validated by `test_framework_yamls_load`, and sort-checked in publication order (`"2.2"` precedes `"2.10"`) via the new section-numeric sort key.
- **Given** the 8-value enum, **when** any edge references `taxonomy: nist-ai-600-1`, **then** `test_crosswalk_referential_integrity` resolves it against the new catalog.

**Priority**: P0 | **Effort**: S

### US-2: Surface C Becomes 15 Correct Edges — and the 16 Wrong Ones Go
**When** I pivot a tachi finding into the NIST GAI Risk framing,
**I want** every Surface C Overlap row transcribed verbatim as a `tachi-stride-ai-category → nist-ai-600-1` primary edge, and the legacy `→ nist-ai-rmf` drift edges removed,
**So I can** cite a machine-readable mapping the source actually supports — with no wrong-direction cohabitation.

**Acceptance Criteria**:
- **Given** the crosswalk after this feature, **when** I filter `source.taxonomy == 'tachi-stride-ai-category' AND target.taxonomy == 'nist-ai-600-1'`, **then** exactly the 15 enumerated pairs (FR-3 table) exist, each `edge_type: primary`, `confidence: high`, `citation: .claude/skills/tachi-shared/references/nist-ai-rmf-mapping.md`.
- **Given** the crosswalk after this feature, **when** I filter `source.taxonomy == 'tachi-stride-ai-category' AND target.taxonomy == 'nist-ai-rmf'`, **then** the result is **empty** (all 16 FR-7 edges removed; no other edge class touched).
- **Given** the transcription, **when** compared against the Surface C table, **then** it is verbatim (no invented, dropped, or re-authored rows; "No equivalent" rows omitted; both Gap rows omitted per the OQ-2 ruling).
- **Given** the full suite, **when** `pytest tests/schemas/test_taxonomy_integrity.py` runs (via `/usr/bin/python3`), **then** 5/5 pass: no dangling endpoint, no duplicate triple, primary floor ≥500 (now 541), citation shape valid.

**Priority**: P0 | **Effort**: S

### US-3: The Schema Change Carries Its Governance Trail
**When** a future maintainer (or auditor) asks "when and why did the taxonomy enum become 8-value, and where did the 16 drift edges go?",
**I want** the ADR-027 Revision History entry, Decision 3 annotation, README provenance, and CHANGELOG to answer in one hop,
**So that** the F-180 deferral → #184 activation + cleanup loop is closed on the record, not in lore.

**Acceptance Criteria**:
- **Given** ADR-027, **when** I read its Revision History, **then** a dated entry self-describes as the Decision 3 extension-governance instrument — citing this PRD, Issue #184, the Architect sign-off, the 8-value activation, the 15-edge transcription, the FR-022 direction correction, and the FR-7 16-edge removal — and the Decision 3 heading carries the one-line additive annotation ("Amended at F-184: enum extended to 8 values — see Revision History").
- **Given** the README, **when** I read §3, **then** §3.8 documents `nist-ai-600-1.yaml` provenance (DOI source, 12-record composition, retrieval date, cwe_refs rationale, Gap-row omission note) and the §1 snippet tuple lists 8 stems; the edge-type composition reads 541/37/0.
- **Given** live maintained docs, **when** I grep for "7-value" / "7 catalog", **then** no stale count remains in the FR-5 update inventory — with the named exemptions (historical PRDs/specs, ratified ADR bodies, delivered-story records, and `docs/architecture/01_system_design/README.md` per Architect C2) untouched.

**Priority**: P0 | **Effort**: S

---

## Functional Requirements

### FR-1: Author `schemas/taxonomy/nist-ai-600-1.yaml` (12 Records)
**Description**: One record per NIST AI 600-1 §2 GAI Risk section, transcribed from the Surface C table (which carries the canonical names).

**Record composition** (12, verbatim names):
§2.1 CBRN Information or Capabilities · §2.2 Confabulation · §2.3 Dangerous, Violent, or Hateful Content · §2.4 Data Privacy · §2.5 Environmental Impacts · §2.6 Harmful Bias or Homogenization · §2.7 Human-AI Configuration · §2.8 Information Integrity · §2.9 Information Security · §2.10 Intellectual Property · §2.11 Obscene, Degrading, and/or Abusive Content · §2.12 Value Chain and Component Integration

**Business Rules**:
- Shape `{id, full_id, name, url, cwe_refs: []}` (C-b — `cwe_refs` is test-required on non-CWE catalogs; AI 600-1 publishes no direct CWE cross-references).
- **Ids are YAML-quoted strings** `"2.1"`…`"2.12"` — bare section number, no `§` prefix (ASCII-greppable, mirrors the no-prefix convention of the other catalogs). **The quoting is load-bearing, not style** (Architect M3 + Team-Lead C3): unquoted `id: 2.10` parses as float `2.1` → duplicate-id collision with §2.1, `AttributeError` in the sort key, and string-vs-float referential mismatch. The house-style header comment MUST pin "ids are quoted strings"; crosswalk edge target ids must be quoted identically (30 endpoint references).
- `full_id` carries the fully-qualified human form (e.g., `NIST AI 600-1 §2.9`).
- `url`: shared DOI `https://doi.org/10.6028/NIST.AI.600-1` per the FR-033 canonical-URL convention (section anchors not stable across NIST revisions — the documented `nist-ai-rmf.yaml` rationale).
- File ordered in **publication order** (`"2.1"`, `"2.2"`, … `"2.12"`), enforced by the FR-2 sort key.
- House-style header comment: source + retrieval date, record shape, quoted-id rule, sort convention, cwe_refs rationale, FR-024 pointer.

### FR-2: Expand the Integrity Test to the 8-Value Enum (C-a)
**Description**: `tests/schemas/test_taxonomy_integrity.py` is the enum's single enforcement point (verified: the only code surface hardcoding taxonomy stems); it hardcodes the 7-catalog world and MUST be edited.

**Scope** (small, bounded diff):
- `CATALOG_FILENAMES` += `"nist-ai-600-1.yaml"`; `TAXONOMY_ENUM` += `"nist-ai-600-1"`.
- **Sort handling (OQ-1 ruling, Option A as refined by Team-Lead C4)**: add a **separate** section-numeric sort-key function (e.g., `_sort_key_section`: `"2.10"` → `(2, 10)`) plus a new `elif filename == "nist-ai-600-1.yaml"` branch in `test_records_sorted` — leaving `_sort_key_nist` and the `nist-ai-rmf.yaml` path **byte-untouched** (zero RMF-path regression surface). Publication order (`"2.2"` < `"2.10"`) holds in file layout.
- Hygiene (C-a + M1, per the re-review M1×C4 ruling): the two `"not in 7-value enum"` assert strings and the `"Load all 7 catalog YAMLs"` fixture docstring become 8-value/8-catalog (or count-agnostic); the `test_records_sorted` docstring (the *test's* docstring, which names the sort branches) is updated to name the new branch. **`_sort_key_nist` — including its docstring — stays byte-untouched** (C4 zero-regression wins over M1's broader sweep); the normative stale-string inventory lives in `.aod/results/architect.md` and is encoded as tasks at `/aod.plan`.
- No new test functions; `edge_type`/`confidence` enums untouched.

### FR-3: Transcribe the 15 Surface C Overlap Rows as Primary Edges
**Description**: Verbatim transcription, direction `tachi-stride-ai-category → nist-ai-600-1` (the FR-022 direction correction this PRD's PM sign-off ratifies). Pre-enumerated to pin the contract — **Architect-verified 1:1 exact** against the Surface C table (15 Overlap / 2 Gap / 8 No-equivalent rows across the 25-row table):

| # | source.id (tachi-stride-ai-category) | target.id (nist-ai-600-1) | GAI Risk |
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

All 15 `{source, target, edge_type}` triples distinct; 9 distinct source ids (spoofing and repudiation correctly unused); 4 distinct targets resolving against FR-1's records; 30 endpoint references total.

**Business Rules**:
- `edge_type: primary`, `confidence: high` (existing rubric class — "NIST transcription" explicitly names Surface B **or Surface C**), `citation: .claude/skills/tachi-shared/references/nist-ai-rmf-mapping.md` (Surface B precedent, repo-file citation form). Target ids quoted (FR-1 rule).
- "No equivalent" rows (7 risk-level + §2.9×Repudiation) are **omitted by design** — their absence is the deliberate scope boundary the reference instructs auditors to note. **Both Gap rows omitted** per the OQ-2 ruling.
- **Known stale prose, not transcribed**: the reference's Surface C observation says "§2.9 — 8 of 11 categories overlap"; the table yields **9** (and the corrected arithmetic 9+1+1=11 fixes the line's own sum). Transcription follows the **table** (T027-re-verified 15). Per FR-024 and the OQ-4 ruling, a one-line ADR-025 amendment note lands at delivery — never a silent reference-file edit here.

### FR-7: Remove the 16 Legacy Drift Edges (C-e Disposition — PM Ruling: Option A)
**Description**: Remove all 16 surviving `tachi-stride-ai-category → nist-ai-rmf` edges in the same change-set as the FR-3 additions, completing the standing T027 removal directive that T029's Option (d) MIX left unfinished.

**The 16 edges** (verified by YAML parse at HEAD; 2 from Day-1 Slice 4 + 14 from the T016 Batch 5 block; all `primary`/`high` citing `nist-ai-rmf-mapping.md`):
prompt-injection → MEASURE 2.6, MEASURE 2.7 · data-poisoning → MEASURE 2.7, MEASURE 2.8 · spoofing → MEASURE 2.7 · tampering → MEASURE 2.7, MEASURE 2.8 · repudiation → MEASURE 2.8 · info-disclosure → MEASURE 2.7, MEASURE 2.10 · denial-of-service → MEASURE 2.7 · privilege-escalation → MEASURE 2.7 · model-theft → MEASURE 2.7, MEASURE 2.10 · tool-abuse → MEASURE 2.7 · agent-autonomy → MEASURE 2.7

**Business Rules**:
- Removal scope is **exactly** the `{source.taxonomy == tachi-stride-ai-category, target.taxonomy == nist-ai-rmf}` edge class — 16 edges, no more, no fewer. Surface B (`tachi-control-category → nist-ai-rmf`) and every other edge class are untouched.
- **Why removal is correct** (Architect C1 analysis, PM concurrence): the cited reference contains **no** surface mapping STRIDE+AI categories to AI RMF Subcategories — these are `confidence: high` edges whose citation does not support them (FR-013 anti-drift violation); T027 ordered their removal; cohabitation with the correct §2.X edges would leave the audit-credibility defect half-closed and make the ADR's "direction corrected" entry misleading.
- **Disclosure** (Constitution III): CHANGELOG `feat(184)` names the removal explicitly; the ADR-027 revision entry records the disposition; this PRD's PM sign-off is the re-sign. This is correction of defective shipped data, disclosed — not a silent compatibility break.
- Net arithmetic: primary 542 → **541**; total 579 → **578**. The ≥500 floor holds with 41 edges of headroom.

### FR-4: Record the Schema Change in ADR-027 (Revision History Entry — OQ-3 Ruling)
**Description**: ADR-027 Decision 3 closed the enum "for F-A1" with extension under ADR governance. Ruled at review: the Revision History entry is the established amendment instrument (the T027 entry is itself a Decision-level amendment); a standalone ADR would be a content-free duplicate of the already-authored T027 options analysis.

**Scope** (the OQ-3 ratification conditions are binding):
- One dated Revision History entry at the F-184 merge that **self-describes as the Decision 3 extension-governance instrument**, citing: this PRD, Issue #184, the Architect sign-off, the 8-value enum activation, the 12-record catalog, the 15 Surface C edges, the FR-022 direction correction, and the FR-7 16-edge removal disposition.
- A one-line **additive annotation under the Decision 3 heading**: "Amended at F-184: enum extended to 8 values — see Revision History" (an additive pointer, not retro-editing of ratified text).
- Update the maintained ADR-027 index blurb at `docs/architecture/README.md` (line ~54) in the same commit ("extended to 8 values at F-184, see Revision History").

### FR-5: Documentation + Stale-Count Sweep (C2-Bounded)
**Description**: Bring every **live, maintained** surface to the 8-catalog world; leave historical artifacts untouched. The sweep inventory below is Architect-verified by repo-wide grep.

**Update inventory**:
- Integrity-test strings/docstrings (FR-2's items).
- `schemas/taxonomy/crosswalk.yaml` header comment: edge counts (541/37/0) + taxonomy list.
- `schemas/taxonomy/README.md`: new **§3.8** provenance (DOI source, 12-record composition, retrieval date, cwe_refs rationale, quoted-id + sort convention, Gap-row omission note); §1 runnable-snippet tuple → 8 stems; §2 harvest-methodology bullet gains the T027/F-184 amendment note (Surface C deferred at F-180; transcribed here as 15 edges with direction corrected; 16 legacy drift edges removed); edge-type composition → 541/37/0.
- `docs/architecture/README.md:~54` ADR-027 index blurb (FR-4's item).
- CHANGELOG: `feat(184): add NIST AI 600-1 GAI Risk taxonomy (8th catalog) + 15 Surface C crosswalk edges; remove 16 legacy wrong-direction Surface C drift edges (Issue #184, F-A1.1 follow-on)`. The hand-curated Unreleased prose section gains the entry; release-please sections and lingering Unreleased entries are **not** "fixed" (dual-CHANGELOG model).
- Issue #184 closed `stage:done` at delivery with the OQ-4 disposition recorded.

**Exempt (named, do not touch)**:
- `docs/architecture/01_system_design/README.md` — **historical F-180 decision narrative AND init.sh baseline-fixture-coupled** (Architect C2: it ships inside `tests/fixtures/init-baseline-tree/`; editing the live file without regenerating the baseline breaks `tests/scripts/test_init_sh_substitution.py` byte-identity). Its "7-value" statements are true statements about the past decision.
- `specs/180-*` (historical feature record), `docs/product/05_User_Stories/README.md` delivered-story records, ratified ADR bodies (ADR-027's own Decision 3 table text included — the annotation + revision entry supersede; ADR-028/030/033 untouched), historical PRDs.

### FR-6: Integrity Suite Green Throughout
**Description**: `pytest tests/schemas/test_taxonomy_integrity.py` (via **`/usr/bin/python3`** — Team-Lead C5: the default `python3` lacks pytest/pyyaml; baseline verified 5/5 in 1.02 s) is the structural acceptance gate at every step.

**Scope**: 5/5 pass post-change: `test_framework_yamls_load` (8 catalogs), `test_crosswalk_loads` (uniqueness; ≥500 primary floor — 541 after; no extras), `test_crosswalk_referential_integrity` (8-value enum; all 30 new endpoint references resolve), `test_citation_shape` (repo-file citation resolves), `test_records_sorted` (publication order via the new section-numeric key; RMF path untouched). Build ordering: catalog + test surgery land before/with the edge changes (FR-3 additions + FR-7 removals in one coherent change-set) so referential integrity never breaks mid-sequence.

---

## Non-Functional Requirements

### Backward Compatibility (Constitution III)
- **Additive for all valid data**: no existing *catalog record* is modified or removed; all 7 existing catalogs and the 563 non-drift edges are untouched; consumers filtering the 7 known taxonomy values over valid edges see identical results; `nist-ai-600-1` appears only on new records/edges. The enum change is the ADR-027 "enum-additive-minor-bump" discipline (F-136/F-142 precedent) applied to the taxonomy enum for the first time since the F-180 freeze.
- **Disclosed correction, not silent break (FR-7)**: the only removals are the 16 citation-unsupported drift edges under a standing T027 removal directive — defective shipped data, corrected with full disclosure (CHANGELOG + ADR-027 revision entry + PM re-sign in this PRD). Net edge delta −1 (579 → 578); a consumer pinned to the wrong-direction edges loses mappings the cited source never supported and gains the correct ones.

### Determinism
- Static YAML; no generation step; citation/URL validation stays regex-only (no HTTP fetch — ADR-021).

### Integrity (Core NFR)
- Referential integrity is inviolable: every new edge endpoint resolves; the enum stays closed (now at 8); the integrity test MUST fail on any unknown value — the Decision 3 guarantee carries forward unchanged.
- **Honest limit (per C1)**: referential integrity blocks *unresolvable* targets (a §2.X id aimed at `nist-ai-rmf` fails — those ids don't exist there) but **cannot catch wrong-but-resolvable mappings** — the 16 surviving drift edges are the existence proof. Semantic correctness is guarded by FR-3's pre-enumeration, FR-7's removal, and the build-stage transcription-fidelity review gate.

### Maintainability
- The ADR-027 revision entry + Decision 3 annotation + README §3.8 + pre-enumerated edge tables (FR-3 add-list AND FR-7 remove-list) make the activation and cleanup auditable in one hop and drift-resistant.

---

## Success Metrics
- **Catalog**: `nist-ai-600-1.yaml` with exactly 12 records, 5-field shape, quoted-string ids, DOI URL — loaded and validated by the integrity suite in publication order.
- **Enum**: 8-value `taxonomy` enum enforced by the test; zero stale "7-value" strings in the FR-5 update inventory; named exemptions untouched.
- **Edges**: exactly the 15 enumerated Surface C primary edges present; exactly 0 `tachi-stride-ai-category → nist-ai-rmf` edges remaining; primary 541; total 578; 0 dangling endpoints; 0 duplicate triples.
- **Governance**: ADR-027 revision entry + Decision 3 annotation + index-blurb update at merge; PM re-sign (this PRD) + Architect re-sign on record; OQ-4 ADR-025 prose-note dispositioned at delivery.
- **Gate**: integrity suite 5/5 (via `/usr/bin/python3`); `/aod.analyze` clean; CHANGELOG `feat(184)` naming both the additions and the removal; Issue #184 `stage:done`.

---

## Scope & Boundaries

### In Scope (P0)
- `nist-ai-600-1.yaml` catalog — 12 records, quoted ids (FR-1).
- Integrity-test enum expansion + separate section-numeric sort key + string/docstring hygiene (FR-2).
- 15 Surface C primary edges, correct direction, enumerated contract (FR-3).
- **Removal of the 16 legacy drift edges** (FR-7, Option A).
- ADR-027 Revision History entry + Decision 3 annotation + index blurb (FR-4).
- README §3.8 + snippet + composition; C2-bounded stale-count sweep; CHANGELOG; issue closure (FR-5, FR-6).

### Out of Scope
- **#185 (`cwe.yaml` expansion)** — the other Wave-2 sibling; separate PRD. **Serialize, don't interleave** (shared crosswalk/README/CHANGELOG surfaces — Team-Lead C2).
- **#183 (citation link-rot monitoring)** — Wave-3 tooling discipline.
- **Surface A / Surface B changes** — Surface B's 27 `tachi-control-category → nist-ai-rmf` edges shipped at F-180 and are untouched (FR-7's removal class is precisely scoped to `tachi-stride-ai-category` sources).
- **Re-authoring Surface C content** — FR-024 discipline: the reference file is the verbatim source; factual corrections (the stale "8 of 11" prose) route to the OQ-4 ADR-025 amendment note, never silent edits here.
- **`related`/`superseded` edge expansion** — #182 (delivered) owns that arc; its deferral trail routes nothing to #184 (verified). Both Gap rows omitted per OQ-2 (no `related`/`low` edge authored — it would be the crosswalk's first `low`, against the F-182 anti-drift precedent, for rows auditors are told not to cite).
- **Prior-edition / historical records** (OWASP :2023, deprecated ATT&CK techniques) — #182's deferred-superseded classes route to #185/follow-ons, not this taxonomy.
- **ADR-028's `source_attribution` enum** — NOT extended (Architect M2); finding-level attribution is a separate future decision.
- **New standalone ADR** — ruled out at review (OQ-3); the ADR-027 revision-entry instrument governs.
- **`docs/architecture/01_system_design/README.md`** — exempt from the sweep (historical + baseline-fixture-coupled, Architect C2).

### Assumptions
- The Surface C table in `nist-ai-rmf-mapping.md` is the verbatim source of truth; its 15-Overlap count was re-verified at T027 and re-confirmed by both reviewers 2026-06-10. No re-verification against the NIST PDF is in scope (ADR-025's maintenance triggers govern re-evaluation on a new AI 600-1 revision).
- NIST AI 600-1 (July 2024 edition) remains the current revision; the DOI resolves (citation-only; never fetched).
- No consumer outside `tests/schemas/test_taxonomy_integrity.py` hardcodes the 7-value enum — **Architect-verified** across .py/.sh/.json surfaces; the SARIF generator scripts have no production caller (output-authoring-tiers record).

### Constraints
- FR-024 transcription-not-re-authorship discipline (binding).
- Referential integrity + `{source, target, edge_type}` uniqueness + citation shape + ≥500 primary floor (test-enforced, inherited unchanged).
- ADR-027 extension governance: enum change requires the ADR revision entry + Architect re-sign (the issue's own governance requirements).
- Test invocation via `/usr/bin/python3` (W0 interpreter pin — Team-Lead C5).

---

## Risks & Dependencies

### Technical Risks

**Risk 184.1 — Test-surgery under-scope (the issue's stale "no test change" claim).**
- **Likelihood**: Resolved | **Impact**: Low (now) — would have been Medium if discovered at build.
- **Mitigation**: C-a scopes the exact edits; Team-Lead independently verified every hardcode; bounded diff.

**Risk 184.2 — Sort-key regression on the `nist-ai-rmf` path.**
- **Likelihood**: Low | **Impact**: Low — loud failure (`test_records_sorted` on the RMF file), never silent.
- **Mitigation**: OQ-1 ruling refined per Team-Lead C4 — a **separate** `_sort_key_section` function + new `elif` branch; `_sort_key_nist` and the RMF path stay byte-untouched.

**Risk 184.3 — Direction-drift recurrence (the C-e history: wrong-direction Surface C edges shipped once and *survived their ordered removal*).**
- **Likelihood**: Low | **Impact**: Medium — a second drift would burn the same cleanup cost and audit credibility.
- **Mitigation (restated honestly per Architect C1)**: referential integrity is **not** the guard — it blocks unresolvable targets but passes wrong-but-resolvable mappings (the 16 survivors prove it). The guards are: FR-3's pre-enumerated 15-pair contract (Architect-verified 1:1), FR-7's pre-enumerated 16-edge removal list, and the build-stage code-reviewer transcription-fidelity + diff drift-guard gate (only intended additions/removals in the diff).

**Risk 184.4 — Hidden 7-value consumers outside the test.**
- **Likelihood**: Low (Architect-verified: none found) | **Impact**: Low — additive enum degrades gracefully for naive consumers.
- **Mitigation**: FR-5 named-inventory sweep; C2 exemptions prevent the sweep itself from breaking the baseline-fixture test.

**Risk 184.5 — YAML float-coercion on §2.X ids (Team-Lead C3).**
- **Likelihood**: High if unquoted | **Impact**: Low — loud failures (duplicate-id assert, sort-key `AttributeError`, dangling-endpoint mismatch), trivially avoided.
- **Mitigation**: FR-1's binding quoted-string rule across all 12 record ids + 30 edge endpoint references; pinned in the catalog header comment.

### Dependencies
- **Internal**: Feature 180 (catalogs, crosswalk, integrity test, ADR-027) — DELIVERED (PR #181, `8b7c7bf5`). Reference file (Feature 144 / ADR-025) — stable, unchanged. No dependency on #185/#183 (no inbound constraint; outbound serialize directive only). Zero open PRs; no in-flight collision (Team-Lead-verified).
- **External**: NIST AI 600-1 DOI (citation/URL only — regex-validated, never fetched); pytest + pyyaml via `/usr/bin/python3` (verified green). No new tooling, no web-researcher lane (verbatim transcription — external re-verification out of scope).

---

## Definition of Done
- [ ] `schemas/taxonomy/nist-ai-600-1.yaml` authored: 12 records §§2.1–2.12, `{id, full_id, name, url, cwe_refs: []}`, **quoted-string ids**, DOI URL, publication order, house-style header (FR-1).
- [ ] Integrity test expanded: `CATALOG_FILENAMES` + `TAXONOMY_ENUM` carry `nist-ai-600-1`; separate `_sort_key_section` + new `elif` branch; "7-value"/"7 catalog" assert strings, the catalogs-fixture docstring, and the `test_records_sorted` docstring updated — `_sort_key_nist` (incl. its docstring) byte-untouched per the M1×C4 ruling (FR-2).
- [ ] 15 Surface C primary edges authored exactly per the FR-3 table — direction `tachi-stride-ai-category → nist-ai-600-1`, `confidence: high`, citation to the mapping reference, quoted target ids (FR-3).
- [ ] **All 16 FR-7 drift edges removed** — post-change filter `tachi-stride-ai-category → nist-ai-rmf` returns empty; no other edge class touched; primary = 541, total = 578 (FR-7).
- [ ] Both Gap rows omitted (OQ-2); no "No equivalent" row transcribed; OQ-4 ADR-025 prose-note disposition recorded at delivery (FR-3).
- [ ] ADR-027 Revision History entry (self-describing, per the OQ-3 conditions) + Decision 3 additive annotation + `docs/architecture/README.md` index-blurb update, in the same commit (FR-4).
- [ ] README §3.8 + §1 snippet (8 stems) + §2 amendment note + composition (541/37/0); crosswalk header current; C2-bounded sweep complete with named exemptions untouched (FR-5).
- [ ] `pytest tests/schemas/test_taxonomy_integrity.py` **5/5 green** via `/usr/bin/python3`; `/aod.analyze` passes (FR-6).
- [ ] CHANGELOG `feat(184)` entry naming the additions AND the 16-edge removal; Issue #184 closed `stage:done`.

---

## Open Questions

*None open — all four definition-time OQs were ratified at the 2026-06-10 Architect review; the C-e disposition was ruled by PM at v1.1. Implementation-detail latitude (exact header-comment wording, ADR entry prose) rests with `/aod.plan`/`/aod.build` within the FR constraints.*

### Resolved at Definition / Review
- [x] **OQ-1 (sort + id format) — RATIFIED Option A**: separate section-numeric sort key (`"2.10"` → `(2, 10)`) + new `elif` branch; `_sort_key_nist`/RMF path byte-untouched (Team-Lead C4 refinement); ids = bare quoted strings `"2.1"`…`"2.12"`, no `§` prefix; quoting load-bearing (float-coercion: unquoted `2.10` → `2.1`). Option B (lexicographic layout) rejected — would make this the repo's only non-publication-ordered GAI listing to dodge a one-time small test edit.
- [x] **OQ-2 (Gap rows) — RATIFIED omit both**: §2.6 is endpoint-less (un-formable); §2.9×Spoofing would be the crosswalk's **first** `low` edge (verified: 255 high / 324 medium / 0 low) — against the F-182 anti-drift precedent, for a row auditors are explicitly told not to cite. Gap rows stay documented in the reference + README §3.8.
- [x] **OQ-3 (ADR vehicle) — RATIFIED revision entry, no standalone ADR**: the T027 entry precedent makes Revision History the established Decision-level amendment instrument; the extension rationale was already authored at T027 (Option (a) = this feature). Conditions binding: self-describing entry + Decision 3 additive annotation + index-blurb update (FR-4).
- [x] **OQ-4 (stale prose routing) — RATIFIED one-line ADR-025 amendment note at delivery** (no micro-issue): correcting "8 of 11" → "9 of 11" also repairs the line's own arithmetic (8+1+1=10≠11; 9+1+1=11 ✓); clarify Gap granularity (risk-level vs row-level) — clarify, don't rewrite.
- [x] **C-e disposition — PM RULING: Option A (remove the 16 in-scope, FR-7)**: F-184 is the designated Surface C completion vehicle; completes the standing T027 directive; citation-unsupported `high` edges violate FR-013; cohabitation would half-close the audit defect and make the ADR entry misleading. Disclosed per Constitution III. (Option B — ship-then-follow-on — was acceptable to the Architect only with explicit cohabitation disclosure; PM rejects: the disclosure cost ≈ the removal cost, with none of the benefit.)
- [x] **Issue-body corrections C-a–C-e** verified (C-a–C-d at definition, Architect-confirmed; C-e at review, YAML-parse-confirmed).
- [x] **Current state** → crosswalk = 542 primary / 37 related / 0 superseded = 579 total; **16 live `tachi-stride-ai-category → nist-ai-rmf` drift edges** (2 Day-1 Slice 4 + 14 T016 Batch 5); 7 catalogs / 7-value enum hardcoded in the test; 0 `low`-confidence edges.
- [x] **#182 deferral-trail routing** → nothing routes to #184; no inherited `superseded` obligations.
- [x] **Citation + confidence pattern** → Surface B precedent: repo-file citation, `confidence: high` under the "NIST transcription" rubric class (which already names Surface C).
- [x] **Standalone scoping** → #184 solo per the user's invocation + split-valve guidance; serialize vs #185 (shared surfaces).
- [x] **PM re-sign on FR-022 direction + FR-7 removal** → carried by this PRD's pm_signoff.

---

## References

### Product Documentation
- Product Vision: [product-vision.md](docs/product/01_Product_Vision/product-vision.md)
- GitHub Issue: [#184](https://github.com/davidmatousek/tachi/issues/184) (`follow-on-180`, filed at F-180 T034)
- Strategy: `_internal/strategy/BLP-05-framework-mapping-and-output-fidelity.md` §Wave 2 *(internal, gitignored)*
- Triad review records: `.aod/results/architect.md` (C1/C2/M1–M3 + OQ rulings), `.aod/results/team-lead.md` (effort calibration + W0–W4 agent plan + concerns 1–5)

### Related PRDs / Features
- Feature 180 — Taxonomy Crosswalk Collection (F-A1), PR #181 — parent; T027 Option (c) deferral; T029 Option (d) MIX execution (Surface B drift deduped, Surface C drift survived); T034 follow-on filing
- Feature 186 — MITRE Catalog Expansion — record-expansion sibling (contrast: no enum change there)
- Feature 182 — Crosswalk `related`/`superseded` Edges — Wave-3 sibling (deferral trail routes nothing here; 0 `low` edges precedent)
- Sibling Wave-2 issue: [#185](https://github.com/davidmatousek/tachi/issues/185) (`cwe.yaml` expansion — separate PRD; serialize)

### Technical Documentation
- ADR-027 — Taxonomy Crosswalk Schema (Decision 3 enum closure + extension governance; T027 revision entry pre-scoping this follow-on) — *amended by revision entry + Decision 3 annotation at merge*
- ADR-025 — NIST AI RMF Evaluation (Surface C structure source; FR-024 correction routing; OQ-4 note lands here) — *one-line amendment note at delivery*
- ADR-028 — Source-Attribution Schema (5-value `source_attribution` enum) — *explicitly NOT extended (M2)*
- Surface C source: `.claude/skills/tachi-shared/references/nist-ai-rmf-mapping.md` §Surface C (15 Overlap + 2 Gap + 8 No-equivalent rows across 12 GAI risks) — *unchanged*
- Integrity test: `tests/schemas/test_taxonomy_integrity.py` (CATALOG_FILENAMES line 13; TAXONOMY_ENUM line 23; `_sort_key_nist` line 63; `test_records_sorted` line 288; 5 test functions)
- Crosswalk: `schemas/taxonomy/crosswalk.yaml` (542 primary / 37 related / 0 superseded → **541/37/0** after FR-3+FR-7)
- F-180 task records: `specs/180-taxonomy-crosswalk-collection/tasks.md` §T023/T024/T027/T029/T034 (the C-e paper trail)
- NIST AI 600-1: `https://doi.org/10.6028/NIST.AI.600-1` (Generative AI Profile, July 2024)

---

## Approval & Sign-Off

| Role | Name | Status | Date | Comments |
|------|------|--------|------|----------|
| Product Manager | product-manager | Approved | 2026-06-10 | Author sign-off (v1.1); completes F-180's Surface C deferral + the unfinished T029 removal directive; carries the FR-022 direction-correction re-sign + FR-7 Option A ruling; 5 issue-body corrections surfaced |
| Architect | architect | Approved with Concerns | 2026-06-10 | Re-review: all v1.0 requirements verified folded; FR-7 16-edge list 1:1 exact at HEAD; TL-C4 sort-key refinement ratified; 1 concern (M1×C4 docstring tension) ruled byte-untouched-wins and folded into v1.2 |
| Team Lead | team-lead | Approved with Concerns | 2026-06-10 | Feasibility approved, no veto; envelope 0.75–1.25 d (realistic 0.75–1.0, +0.1–0.15 for FR-7); 5 advisory concerns all folded; W0–W4 agent plan ready for /aod.tasks |

---

## Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-06-10 | product-manager | Initial PRD (BLP-05 Wave 2, F-A1.1 follow-on). 8th catalog (12 GAI Risk records), 7→8 enum expansion via integrity test, FR-022 direction correction, 15 pre-enumerated Surface C primary edges, ADR-027 revision-entry governance. Issue-body corrections C-a–C-d surfaced and scoped. |
| 1.1 | 2026-06-10 | product-manager | Folded in Triad review. **Architect (CHANGES_REQUESTED → resolved)**: **C1/C-e** — the 16 drifted Surface C edges were NEVER removed (T029 ran Option (d) MIX; normalization made them resolvable; verified live by YAML parse) → new **FR-7** removal disposition (PM ruling: Option A), arithmetic recomputed **557/594 → 541/578**, Risk 184.3 mitigation restated honestly (referential integrity passes wrong-but-resolvable mappings), NFR reframed as additive + disclosed correction; **C2** — `docs/architecture/01_system_design/README.md` named exempt from the FR-5 sweep (init.sh baseline-fixture byte-identity coupling) + Architect-verified sweep update/exempt inventory adopted; **M1** sort-test docstrings into FR-2 hygiene; **M2** ADR-028 enum explicitly out-of-scope; **M3** quoted-id rule pinned in FR-1. **OQ-1/2/3/4 ratified** (separate sort-key fn per Team-Lead C4; omit both Gap rows; ADR-027 revision entry with self-describing + annotation + index-blurb conditions; ADR-025 one-line note at delivery). **Team-Lead (APPROVED_WITH_CONCERNS)**: realistic point 0.75–1.0 d (envelope unchanged; FR-7 +0.1–0.15 d); serialize #185 (shared crosswalk/README/CHANGELOG surfaces); YAML float-coercion quoting rule (Risk 184.5); interpreter pin `/usr/bin/python3` at W0; W0–W4 single-engineer agent plan recorded. |
| 1.2 | 2026-06-10 | product-manager | Architect bounded re-review recorded: **APPROVED_WITH_CONCERNS** — all v1.0 requirements verified folded; FR-7's 16-edge list verified 1:1 exact at HEAD `f57a9c1`; TL-C4 refinement of OQ-1 Option A formally ratified; no stale 557/594 figures. Sole concern resolved in-place: **M1×C4 docstring tension** — byte-untouched wins; `_sort_key_nist` (incl. docstring) is NOT edited; the `test_records_sorted` docstring is the one that names the new branch; normative stale-string inventory in `.aod/results/architect.md`, encoded at `/aod.plan` (FR-2 + DoD wording corrected). Status → **Approved**; all three Triad sign-offs recorded in frontmatter. |
