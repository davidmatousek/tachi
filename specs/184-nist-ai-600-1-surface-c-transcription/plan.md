---
triad:
  pm_signoff:
    agent: product-manager
    date: 2026-06-10
    status: APPROVED
    notes: "0 blocking. All 8 spec FRs wave-traced (FR → Wave matrix complete); US-1/US-2 land at W1/W2 as the shippable MVP increment, US-3 at W4; 541/578 arithmetic everywhere with team-lead.md's stale 557/594 explicitly superseded (plan wave-plan preamble + quickstart hard assert); contract 15-add/16-remove lists verified 1:1; write-set = PRD (6 modified + 1 new), exemptions held (01_system_design README, ADR-028, #185 serialize); deliver-time items correctly excluded from build waves. Forward to /aod.tasks: carry the #185 serialize directive into agent-assignments.md; wave gates use 541/578 only. Details: .aod/results/product-manager.md"
  architect_signoff:
    agent: architect
    date: 2026-06-10
    status: APPROVED
    notes: "APPROVED_WITH_CONCERNS instrument (.aod/results/architect.md) recorded as APPROVED per its sign-off position, with the F1/F2 binding conditions APPLIED in-line before /aod.tasks (re-verify at tasks sign-off). All PRD-stage rulings verified correctly encoded: M1×C4 inventory exact vs live file (contract C4, 8 sites, _sort_key_nist byte-untouched); OQ-1 separate _sort_key_section + elif; OQ-2 both Gap rows omitted; OQ-3 same-commit conditions; FR-7 16-pair class-filter removal fresh-verified at 7cd58b2. Arithmetic 541/578 consistent everywhere. F1 (binding, applied): control→rmf class is 31 at baseline (27 Surface B table cells + 4 legacy non-table extras — quickstart/contract/data-model/spec/plan W0+W2 gates corrected; follow-on filed: Issue #325; do NOT fold into FR-7). F2 (binding, applied): quickstart §5 diff-grep replaced with AST extraction comparison (grep false-FAILs on context lines). F3/F4 (minor/nit, applied): sweep grep extended (taxonomy (7), 542, (14) — one expected F-186 lineage survivor); README anchor L13; deferral NOTE is mid-file ~L2002–2007. Details: .aod/results/architect.md"
  techlead_signoff: null  # Added by /aod.tasks
---

# Implementation Plan: NIST AI 600-1 GAI Risk Taxonomy — Surface C Transcription (F-184)

**Branch**: `184-nist-ai-600-1-surface-c-transcription` | **Date**: 2026-06-10 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `specs/184-nist-ai-600-1-surface-c-transcription/spec.md`
**Initiative**: BLP-05 Wave 2 (Crosswalk Catalog Expansion) · P2 (Light) · F-A1.1 follow-on (Issue #184, filed at F-180 T034)

## Summary

Add `schemas/taxonomy/nist-ai-600-1.yaml` as the crosswalk's **8th catalog** (12 GAI Risk records, §§2.1–2.12, quoted-string ids, shared DOI), expand the frozen 7-value `taxonomy` enum to **8** at its single enforcement point (`tests/schemas/test_taxonomy_integrity.py` — `CATALOG_FILENAMES` + `TAXONOMY_ENUM` + a **separate** `_sort_key_section` sort key + new `elif` branch, `_sort_key_nist` byte-untouched), transcribe the **15 verified Surface C Overlap rows** as `tachi-stride-ai-category → nist-ai-600-1` primary edges, and **remove the 16 legacy wrong-direction drift edges** (`tachi-stride-ai-category → nist-ai-rmf`) in the same change-set. Close the governance loop with an ADR-027 Revision History entry + Decision 3 annotation + index-blurb update, README §3.8 provenance, and a C2-bounded stale-count sweep. Edge arithmetic: primary 542 − 16 + 15 = **541** (≥500 floor, 41 headroom); total **578**; composition **541/37/0**. Pure data + test-surgery change: no new test functions, no schema scripts, no standalone ADR.

## Technical Context

**Language/Version**: Python 3.x via `/usr/bin/python3` (test oracle only — Team-Lead C5: default `python3` lacks pytest/pyyaml; baseline 5/5 in ~1.0s verified). The feature payload is static YAML data + one test-file edit + docs.
**Primary Dependencies**: `pyyaml`, `pytest` (existing; no new tooling). NIST AI 600-1 DOI is citation-only — never fetched (ADR-021 determinism).
**Storage**: static YAML — `schemas/taxonomy/nist-ai-600-1.yaml` (NEW), `schemas/taxonomy/crosswalk.yaml` (edges + header)
**Testing**: `/usr/bin/python3 -m pytest tests/schemas/test_taxonomy_integrity.py` (5 functions; structural acceptance gate at every commit boundary — spec FR-008)
**Target Platform**: repo data files + CI (`tachi-pytest.yml`)
**Project Type**: single (data-layer change in the existing repo)
**Performance Goals**: N/A (static data; suite ~1s)
**Constraints**: referential integrity inviolable (closed enum, now 8); `{source, target, edge_type}` uniqueness; ≥500 primary floor; citation shape (repo-file form); **YAML-quoted `"2.X"` ids everywhere** (12 records + 30 edge endpoints — float-coercion Risk 184.5); `_sort_key_nist` code AND docstring byte-untouched (M1×C4); FR-024 transcription-not-re-authorship; C2 sweep exemptions (baseline-fixture coupling); build ordering — catalog + test surgery land before/with the edge change-set
**Scale/Scope**: +1 catalog (12 records), +15 / −16 edges (net 578 total), 1 test file surgically edited, 4 doc surfaces updated, 1 ADR amended via revision entry
**Unknowns**: **0** — all four definition-time OQs (sort/id format, Gap rows, ADR vehicle, stale-prose routing) plus the C-e drift-edge disposition were ratified at PRD review (v1.1/v1.2). No `NEEDS CLARIFICATION` markers exist in the spec.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Verdict | Rationale |
|-----------|---------|-----------|
| I. General-Purpose Architecture | PASS | Taxonomy data + its integrity test; no new domain coupling, no runtime code. |
| II. API-First Design | N/A | No API/UI surface. The crosswalk IS the machine-readable contract; shape unchanged (ADR-027-frozen edge shape; 5-field record shape). |
| III. Backward Compatibility (NON-NEGOTIABLE) | PASS | Additive for all valid data: 7 existing catalogs + 563 non-drift edges untouched; enum change is the established additive-minor discipline. The only removals are the 16 citation-unsupported drift edges under a standing T027 removal directive — **disclosed correction of defective shipped data** (CHANGELOG + ADR-027 revision entry + PM re-sign carried by PRD-184), not a silent break. |
| IV. Concurrency & Data Integrity | PASS (by-test) | Static YAML, no runtime state. Referential integrity + uniqueness + floor enforced by the suite; FR-008 ordering keeps integrity green at every commit boundary. |
| V. Privacy & Data Isolation | N/A | Public framework identifiers + public DOI; no PII/secrets (data-layer YAML — no security-analyst lane needed per Team-Lead Q3). |
| VI. Testing Excellence | PASS | Existing 5-function suite is the acceptance oracle (spec FR-008); test surgery is scoped by the M1×C4 normative inventory — no new test functions, zero RMF-path regression surface. |
| VII. Definition of Done (NON-NEGOTIABLE) | DEFERRED | Satisfied at `/aod.deliver` (DoD checklist in spec/PRD; OQ-4 ADR-025 note is a delivery-stage action). |
| VIII. Product-Spec Alignment (NON-NEGOTIABLE) | PASS | PRD v1.2 Triad-approved; spec.md PM-approved (APPROVED, 2026-06-10); this command obtains plan.md PM + Architect dual sign-off. |
| IX. Git Workflow (NON-NEGOTIABLE) | PASS | On feature branch `184-nist-ai-600-1-surface-c-transcription`; draft PR #324 open with conventional title `feat(184): …`. |

**Result: PASS — no violations. Complexity Tracking not required.**

## Project Structure

### Documentation (this feature)

```
specs/184-nist-ai-600-1-surface-c-transcription/
├── plan.md              # This file (/aod.project-plan output)
├── research.md          # Research phase output (spec stage; plan-phase decisions appended)
├── data-model.md        # Entities: catalog record, edge add/remove classes, enum, ADR entry
├── quickstart.md        # Verification quickstart (interpreter-pinned commands + filters)
├── contracts/
│   └── surface-c-transcription.contract.md   # Binding data contract: 12 records, 15-edge add list, 16-edge remove list, test-surgery inventory
├── checklists/
│   └── requirements.md  # Spec quality checklist (complete)
└── tasks.md             # Task breakdown (/aod.tasks output — next)
```

### Source Code (repository root) — the complete write-set

```
schemas/taxonomy/
├── nist-ai-600-1.yaml        # NEW — 12 records, quoted ids, DOI, publication order, house-style header
├── crosswalk.yaml            # +15 Surface C edges / −16 drift edges; header counts → 541/37/0 + 8-value taxonomy list; mid-file deferral NOTE (~L2002–2007) retired
└── README.md                 # §3.8 provenance (new), §1 snippet → 8 stems, §2 bullet-3 amendment, composition → 541/37/0, L13 "seven taxonomies" / L20 "9 files" → 8 taxonomies / 10 files

tests/schemas/
└── test_taxonomy_integrity.py  # CATALOG_FILENAMES + TAXONOMY_ENUM += nist-ai-600-1; NEW _sort_key_section + elif branch; M1×C4 stale-string inventory applied; _sort_key_nist byte-untouched

docs/architecture/
├── 02_ADRs/ADR-027-taxonomy-crosswalk-schema.md  # Revision History entry + Decision 3 additive annotation (ratified text untouched)
└── README.md                                      # ADR-027 index blurb (~line 54) updated

CHANGELOG.md                  # hand-curated Unreleased: feat(184) entry naming additions AND the 16-edge removal
```

**Structure Decision**: single-project data-layer change. Six files modified + one created. **Exempt surfaces (do NOT touch)**: `docs/architecture/01_system_design/README.md` (baseline-fixture byte-identity, Architect C2), `specs/180-*`, ratified ADR bodies, historical PRDs, delivered-story records, release-please CHANGELOG sections.

## Phase 0: Research

`research.md` was produced at the spec stage (four parallel lanes: KB, codebase, architecture, web) and contains **zero unresolved unknowns** — all decisions were ratified at PRD review. Key plan-binding decisions, in Decision/Rationale/Alternatives form:

| Decision | Rationale | Alternatives considered |
|---|---|---|
| Separate `_sort_key_section` fn + new `elif` branch (OQ-1 + TL-C4) | Two genuinely different id grammars (`MEASURE 2.7` vs bare `"2.10"`); zero RMF-path regression surface; `_sort_key_nist` byte-untouched | Generalize `_sort_key_nist` in place (rejected: touches the RMF path); lexicographic file layout (rejected: only non-publication-ordered GAI listing to dodge a small test edit) |
| Ids = bare quoted strings `"2.1"`…`"2.12"` | Float-coercion: unquoted `2.10` parses as `2.1` → duplicate-id collision + sort `AttributeError` + string/float referential mismatch; ASCII-greppable, mirrors no-prefix convention | `§`-prefixed ids (rejected: non-ASCII, breaks grep ergonomics); unquoted (rejected: Risk 184.5) |
| Omit both Gap rows (OQ-2) | §2.6 endpoint-less (un-formable); §2.9×Spoofing would be the crosswalk's first `low` edge against F-182 anti-drift precedent, for a row auditors are told not to cite | Transcribe as `related`/`low` (rejected) |
| ADR-027 Revision History entry, no standalone ADR (OQ-3) | T027 entry precedent = established Decision-level amendment instrument; extension rationale already authored at T027 | Standalone ADR (rejected: content-free duplicate) |
| Remove all 16 drift edges in-scope (C-e/FR-7, PM ruling Option A) | Completes standing T027 directive; citation-unsupported `high` edges violate FR-013; cohabitation half-closes the audit defect | Ship-then-follow-on (rejected: disclosure cost ≈ removal cost, none of the benefit) |
| Removal by edge-class filter, verified by count + pair-list | Line-range surgery is brittle (16 edges live in two regions: Day-1 Slice 4 + T016 Batch 5) | Line-based deletion (rejected) |
| Single-commit edge change-set (FR-3 + FR-7 together) | 31 net edge lines ≪ F-180's ~50-edge pre-commit-timeout batching threshold (Risk R8); keeps add+remove atomic and auditable | Split commits (unnecessary; would separate the paired correction) |
| Stale reference prose ("8 of 11"; §2.6 "or/and") routes to delivery-time ADR-025 one-line note (OQ-4) | FR-024: transcription, never silent reference edits | Edit reference in-feature (rejected) |

**Output**: [research.md](research.md) — complete, 0 `NEEDS CLARIFICATION`.

## Phase 1: Design Artifacts

- **[data-model.md](data-model.md)** — entities + validation rules: catalog record (12, quoted ids), Surface C primary edge (add class, 15), legacy drift edge (remove class, 16), 8-value taxonomy enum, ADR-027 revision entry.
- **[contracts/surface-c-transcription.contract.md](contracts/surface-c-transcription.contract.md)** — the binding build contract: all 12 catalog records fully enumerated (id/full_id/name/url), the 15-edge add list, the 16-edge remove list, the M1×C4 test-surgery inventory, and the doc-surface update inventory with exemptions. Builders execute against this file; reviewers diff against it.
- **[quickstart.md](quickstart.md)** — interpreter-pinned verification commands: suite run, edge-class filters (add class = 15, remove class = empty), count assertions (541/37/0 = 578), `_sort_key_nist` byte-untouched check, exempt-surface no-diff check.
- **Agent context update**: `.aod/scripts/bash/update-agent-context.sh` is absent in this repo (known gotcha) — skipped gracefully; no agent context file requires new technology entries (no new tech introduced).

**Post-design Constitution re-check: PASS** — design artifacts introduce no new violations (no schema change, no new code paths, additive + disclosed-correction posture unchanged).

## Implementation Strategy — Wave Plan (W0–W4)

Single senior-backend-engineer + checkpoint gates (Team-Lead Q3; #186 precedent: single-session builds serialize on the executor — model independence for MVP isolation, not speedup). Expected ~12–14 tasks at `/aod.tasks`. **Wave-gate arithmetic uses 541/578** (PRD v1.1 FR-7 fold-in; the figures 557/594 in `.aod/results/team-lead.md` Q3 predate FR-7 and are superseded).

| Wave | Scope | Agent(s) | Gate |
|------|-------|----------|------|
| **W0 Setup** | Baseline: suite 5/5 via `/usr/bin/python3`; count baseline (542 primary / 37 related / 0 superseded = 579; exactly 16 `tachi-stride-ai-category → nist-ai-rmf` edges present; 0 `→ nist-ai-600-1` edges; `tachi-control-category → nist-ai-rmf` class = 31 — do NOT touch) | senior-backend-engineer | **STOP-gate** if baseline red or counts drift from PRD-verified state |
| **W1 Foundational** | `nist-ai-600-1.yaml` (12 records per contract) + FR-002 test surgery (enum 7→8, `_sort_key_section` + `elif`, M1×C4 inventory) — same wave/commit | senior-backend-engineer | Suite 5/5 with 8 catalogs loaded (0 new edges yet is valid); `_sort_key_nist` diff empty |
| **W2 MVP** (US-1 + US-2) | Edge change-set as ONE coherent change: remove 16 drift edges (class filter) + append 15 Surface C edges (per contract) + crosswalk header (counts 541/37/0, 8-value taxonomy list incl. header L6 enum line) + retire the mid-file "Surface C DEFERRED" NOTE unit (~L2002–2007) | senior-backend-engineer → tester | Suite 5/5; primary **541**, total **578**; `tachi-stride-ai-category → nist-ai-rmf` filter **empty**; `tachi-control-category → nist-ai-rmf` still **31**; all 30 new endpoints resolve; no duplicate triples. **Shippable increment.** |
| **W3 Verify** | Transcription-fidelity review: 15 pairs vs Surface C table (direction, confidence, citation, quoted ids) + 16 removals vs contract list + **diff drift-guard** (only intended additions/removals in the crosswalk diff; Surface B untouched) | code-reviewer → tester | Fidelity check clean; final suite 5/5; `/aod.analyze` pass. The Risk-184.3 mitigation gate. |
| **W4 Polish** `[P]` | ADR-027 Revision History entry + Decision 3 annotation + `docs/architecture/README.md` blurb (one commit); taxonomy README §3.8 + §1 snippet (8 stems) + §2 amendment + composition + line-11/20 counts; stale-count sweep (inventory surfaces only); CHANGELOG `feat(184)` | senior-backend-engineer (architect reviews ADR entry text) | Sweep greps clean on inventory surfaces; zero diffs on exempt surfaces; ADR ratified-text byte-unchanged above the annotation |
| **Deliver-time** (not build) | Issue #184 `stage:done`; OQ-4 ADR-025 one-line note (incl. §2.6 "or/and" observation); PR ready + squash-merge | product-manager / architect | `/aod.deliver` |

### FR → Wave Traceability

| Spec FR | Wave | Notes |
|---|---|---|
| FR-001 catalog (12 records) | W1 | Contract-enumerated |
| FR-002 test surgery (8-value enum + sort key + M1×C4 inventory) | W1 | Same commit as catalog |
| FR-003 15 Surface C edges | W2 | One change-set with FR-004 |
| FR-004 16-edge removal | W2 | Class filter; verified by pair-list |
| FR-005 ADR-027 entry + annotation + blurb | W4 | Same commit (binding OQ-3 condition) |
| FR-006 doc surfaces + sweep (with exemptions) | W2 (crosswalk header) + W4 (README, sweep) | C2 exemptions enforced at W3/W4 gates |
| FR-007 CHANGELOG + issue closure | W4 (CHANGELOG) + Deliver | feat(184) names additions AND removal |
| FR-008 suite green throughout + ordering | W0–W4 gates | Interpreter-pinned |

## Risks (carried from PRD, plan-stage posture)

| Risk | Posture |
|---|---|
| 184.1 test-surgery under-scope | Resolved at definition (C-a); FR-002 inventory is exact (M1×C4) |
| 184.2 sort-key regression on RMF path | Eliminated by design: separate fn + new branch; W1 gate checks `_sort_key_nist` diff empty |
| 184.3 direction-drift recurrence | Guards: pre-enumerated 15-pair + 16-pair contract lists + W3 fidelity/diff-drift gate (referential integrity passes wrong-but-resolvable mappings — NOT the guard) |
| 184.4 hidden 7-value consumers | Architect-verified none; FR-006 named-inventory sweep; C2 exemptions prevent the sweep breaking the baseline-fixture test |
| 184.5 YAML float-coercion | Quoted-string rule binding on all 42 id sites (12 records + 30 endpoints); pinned in catalog header; loud failure if violated |

## Complexity Tracking

*No Constitution Check violations — table not required.*

## Note on System Design Generation

This plan intentionally carries no canonical `## Components` / `## Data Flow` / `## Tech Stack` sections: F-184 is a data-contract change with no new system components, and the system-design README (`docs/architecture/01_system_design/README.md`) is **C2-exempt** (baseline-fixture byte-identity coupling) — appending to it would break `tests/scripts/test_init_sh_substitution.py`. Step 6 system-design generation skips gracefully by design (F-182 precedent).
