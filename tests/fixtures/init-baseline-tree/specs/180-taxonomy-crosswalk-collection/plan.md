---
spec_reference: specs/180-taxonomy-crosswalk-collection/spec.md
prd_reference: docs/product/02_PRD/180-taxonomy-crosswalk-collection-2026-04-17.md
triad:
  pm_signoff:
    agent: product-manager
    date: 2026-04-17
    status: APPROVED
    notes: "Plan fully preserves all 41 FRs + 13 SCs from spec.md with no lost traceability. Phase 2 preview maps accurately to PRD Phase Breakdown (Days 1-5, 3-agent parallel). Scope claims (zero runtime diff, zero new deps, additive-only under schemas/taxonomy/ + tests/schemas/ + 1 ADR + 2 README link edits) match FR-035/FR-037 exactly. SC-007 (H-PM-1 Metric 7) preserved via quickstart.md §1 runnable-snippet validation. FR-033 'What F-A1 does NOT give you today' (H-PM-2) preserved via README §What F-A1 does NOT subsection in quickstart.md §3. Constitutional gates sound; no user-value concern missed. R7 and R8 accurately scoped. Pre-Mortem lens surfaces 3 /aod.tasks-time items (non-blocking): Day 1 spike tier-decision assignee, R7 architect Day-2 bandwidth, FR-033 README subsection as discrete content-review task — all task-level concerns for tasks.md authoring."
  architect_signoff:
    agent: architect
    date: 2026-04-17
    status: APPROVED_WITH_CONCERNS
    notes: "Technically sound. 7 review dimensions pass: Technical Context (Python 3.11 + pyyaml/pytest/pytest-cov verified in requirements-dev.txt); Constitution III/VI ✅ PASS (FR-035 additive invariant + FR-036 byte-identity tautologically safe given zero runtime touch); data-model.md complete (2 entities + 3 enums + 11 validation rules); contracts cover all 7 taxonomy values in examples; integrity-test-contract.md signatures implementable; ADR-027 Proposed→Accepted matches ADR-021/023/025 precedent; R3 tier-escalation math sound; pytest subdirectory bootstrap matches tests/scripts/ convention. 4 non-blocking concerns addressed inline: (F1) integrity-test-contract.md uniqueness tuple harmonized with data-model.md 3-tuple wording; (F2) cwe_refs required with `[]` allowed on 6 non-cwe catalogs clarified in data-model.md; (F3) plan.md Phase 4 explicitly sequences integrity-test authoring AFTER all 8 YAMLs committed; (F4) data-model.md CWE→CWE example annotated as illustrative-only (superseded out-of-F-A1-scope). No ADR cross-ref missing; no constitutional gate miscarriage; no infra baseline violation. Approved for progression to /aod.tasks."
  techlead_signoff: null  # Added by /aod.tasks
---

# Implementation Plan: F-A1 Taxonomy Crosswalk Collection

**Branch**: `180-taxonomy-crosswalk-collection` | **Date**: 2026-04-17 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/180-taxonomy-crosswalk-collection/spec.md`

## Summary

Ship a new `schemas/taxonomy/` directory containing **9 files** (5 external framework YAMLs + 2 tachi pseudo-taxonomy YAMLs + `crosswalk.yaml` + `README.md`) that make every OWASP / MITRE ATT&CK / MITRE ATLAS / NIST AI RMF / CWE ID tachi cites machine-readable. Authoritative per-item records carry shape `{id, full_id, name, url, cwe_refs}` (except `cwe.yaml` which omits `cwe_refs`); authoritative cross-framework edges live in `crosswalk.yaml` with shape `{source: {taxonomy, id}, target: {taxonomy, id}, edge_type, confidence, citation}`. The crosswalk ships with ≥500 primary edges at F-A1 (Risk R3 Tier 1 default); `related` and `superseded` edges are a follow-on Issue. A pytest-based integrity test suite (`tests/schemas/test_taxonomy_integrity.py`) enforces referential integrity at CI time; a public ADR (ADR-027) documents the schema decisions.

**Technical approach**: pure data-authoring feature. Zero runtime script changes. Zero agent/orchestrator/template modifications. Zero new runtime dependencies. Additive-only under `schemas/taxonomy/` + `tests/schemas/` + one new ADR + exactly 2 cross-reference links (top-level README.md + docs/architecture/00_Tech_Stack/README.md). Backward-compat invariant preserved automatically because no runtime code is touched; the 5 non-agentic example PDFs regenerate byte-identically under `SOURCE_DATE_EPOCH=1700000000` per ADR-021.

## Technical Context

**Language/Version**: Python 3.11 (for the integrity test harness only — via existing Feature 128 pytest bootstrap). YAML is the data authoring format (not a runtime dependency of tachi).
**Primary Dependencies**: `pyyaml>=6.0` (already declared in `requirements-dev.txt` — Q7 resolved at spec time); `pytest>=8.0` + `pytest-cov>=4.1` (Feature 128 bootstrap). No runtime tachi CLI touches these YAMLs in F-A1; runtime integration begins in F-A2.
**Storage**: Flat YAML files on disk under `schemas/taxonomy/`. No database, no serialization beyond `yaml.safe_load` at integrity-test time. Total data size estimate: ~500-800 item records across 7 catalog YAMLs + ≥500 edges in `crosswalk.yaml`.
**Testing**: pytest via existing `tests/scripts/` harness pattern. New `tests/schemas/` subdirectory bootstrapped with `__init__.py` + `test_taxonomy_integrity.py` (4+1 test functions). Backward-compat test `tests/scripts/test_backward_compatibility.py` stays green in PR CI (FR-036).
**Target Platform**: Repo filesystem only (no runtime dispatch). The YAMLs are consumed offline by downstream integrations / F-A2+ features.
**Project Type**: Single project (existing tachi repo). F-A1 is additive to the `schemas/` directory.
**Performance Goals**: `yaml.safe_load` <100ms per catalog YAML; `crosswalk.yaml` <500ms (informational bound, not CI-enforced — SC-013).
**Constraints**: (a) zero runtime pipeline modification (FR-035); (b) zero new runtime dependencies (FR-037); (c) the 5 non-agentic example PDFs byte-identical under `SOURCE_DATE_EPOCH=1700000000` (FR-036); (d) ≥500 primary edges at F-A1 merge (FR-025); (e) verbatim FR-022 transcription contract on NIST Surface B/C rows.
**Scale/Scope**: 9 files × 1 new directory + 1 new ADR + 1 new test file + 2 cross-ref link edits + 1 new test subdirectory. ~500-800 authored item records. ≥500 primary crosswalk edges. Implementation: 4-5 working days via 3-agent parallel execution (senior-backend-engineer + web-researcher + architect), R6 fallback to 5-6 days for single-agent execution.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

**Applicable principles** (from `.aod/memory/constitution.md`):

| Principle | Applicability | Gate Status | Notes |
|-----------|---------------|-------------|-------|
| I. General-Purpose Architecture | N/A | — | F-A1 is content-authoring; no core code touch. |
| II. API-First Design | N/A | — | No API; data files only. |
| III. Backward Compatibility (NON-NEGOTIABLE) | **YES** | ✅ PASS | FR-035 additive-only + FR-036 byte-identical PDFs + FR-037 zero new deps. Preserves 100% local-first `.aod/` compatibility because F-A1 adds files under `schemas/taxonomy/` with no impact on any existing command or agent. |
| IV. Concurrency & Data Integrity | N/A | — | No state transitions; no concurrent writes. YAMLs are authored via PR review only. |
| V. Privacy & Data Isolation | N/A | — | Public-domain taxonomy data; no PII; no user-data boundaries. |
| VI. Testing Excellence | **YES** | ✅ PASS | FR-027 through FR-032: integrity test suite covering 4 mandatory test functions + 1 optional sort-order test. CI-gated per FR-036. |
| VII. Definition of Done (NON-NEGOTIABLE) | **YES** | ✅ PASS | 3-step validation applies at `/aod.deliver` time: (1) ADR-027 Accepted, (2) CI green, (3) SC-001 through SC-013 verified. |
| VIII. Product-Spec Alignment | **YES** | ✅ PASS | spec.md PM sign-off APPROVED_WITH_CONCERNS; all concerns addressed inline (H-PM-2 via FR-033, AML tripwire via FR-016, SC-013 clarification). |

**Gate decision**: ✅ PASS — no violations; no Complexity Tracking entries needed.

## Project Structure

### Documentation (this feature)

```
specs/180-taxonomy-crosswalk-collection/
├── plan.md                              # This file (/aod.project-plan output)
├── research.md                          # Research phase output (spec-phase grounding)
├── spec.md                              # Feature specification (/aod.spec output)
├── data-model.md                        # Design artifact: record shapes + enum domains
├── quickstart.md                        # Design artifact: adopter & maintainer resolution walkthrough
├── checklists/
│   └── requirements.md                  # Spec quality checklist
├── contracts/
│   ├── catalog-record.yaml              # Contract for 7 catalog YAML record shape
│   ├── crosswalk-edge.yaml              # Contract for crosswalk.yaml edge shape
│   └── integrity-test-contract.md       # Contract for FR-027–FR-032 test function signatures
└── tasks.md                             # Task breakdown (/aod.tasks output — Phase 2)
```

### Source Code (repository root — additive-only)

```
tachi/
├── schemas/
│   └── taxonomy/                        # NEW directory (FR-001)
│       ├── owasp.yaml                   # ≥60 items across 6 OWASP lists
│       ├── mitre-attack.yaml            # 38 seed ATT&CK techniques
│       ├── mitre-atlas.yaml             # 7 seed + 5 curated (AML.T0058–T0062) = ≥12 records
│       ├── nist-ai-rmf.yaml             # 68 Subcategory catalog (exact)
│       ├── cwe.yaml                     # 41 seed + 12 net-new (Top 25 2025) = ≥53 records
│       ├── tachi-control-category.yaml  # 8 records (exact)
│       ├── tachi-stride-ai-category.yaml # 11 records (exact)
│       ├── crosswalk.yaml               # ≥500 primary edges (R3 Tier 1 default)
│       └── README.md                    # Curation documentation + runnable Python snippet
│
├── tests/
│   └── schemas/                         # NEW subdirectory (FR-027)
│       ├── __init__.py                  # Empty file (bootstraps the subdirectory)
│       └── test_taxonomy_integrity.py   # 4+1 test functions (FR-028 through FR-032)
│
├── docs/
│   └── architecture/
│       └── 02_ADRs/
│           └── ADR-027-taxonomy-crosswalk-schema.md  # NEW (FR-039); Proposed → Accepted
│
├── README.md                            # +1 cross-reference link to schemas/taxonomy/README.md (FR-038a)
└── docs/architecture/00_Tech_Stack/README.md  # +1 cross-reference link (FR-038b)
```

**Structure Decision**: Additive-only layout under existing `schemas/` + `tests/` + `docs/architecture/02_ADRs/` + two cross-reference link edits on existing READMEs. No new top-level directories beyond `schemas/taxonomy/` and `tests/schemas/`. This matches the PRD's FR-9 additive invariant and the ADR-021 byte-identity determinism pattern.

---

## Phase 0: Outline & Research

### 0.1 Research grounding (already completed at spec-phase)

Research conducted during `/aod.spec` Step 2 produced `research.md` containing:
- Assumption A1 validation via grep (38 ATT&CK / 7 ATLAS / 41 CWE confirmed; AML.T0058–T0062 recategorized to external curation)
- Assumption A2 validation (no ADR-025 amendment in flight)
- Assumption A3 update (CWE Top 25 2025 is current, not 2024)
- NIST edge count re-count (27 Surface B + 14 Surface C = 41 edges; PRD estimated ~54)
- Codebase conventions (existing 10 schemas/, 8 control-category slugs, 11 STRIDE+AI slugs, ADR template, pytest bootstrap)
- Q6 (Day 1 spike composition) + Q7 (pyyaml already in requirements-dev.txt) resolved

No further Phase 0 research is needed; spec.md frontmatter decisions all have grounding.

### 0.2 Open technical decisions resolved at plan time

| Decision | Resolution | Rationale | Alternatives |
|----------|------------|-----------|--------------|
| YAML style (flow vs block) | Block style with 2-space indent | Matches existing `schemas/finding.yaml` / `schemas/attack-chain.yaml` / `schemas/report.yaml` conventions (Grep-confirmed in research.md §2.1). Block style is PR-review-friendly. | Flow style: rejected (dense, harder to diff). |
| YAML file header comment | Multi-line comment block declaring Producers / Consumers / Version / ADR cross-ref | Matches existing `schemas/*.yaml` convention. `schema_version` field at top of each file. | No header: rejected (loses lineage). |
| Record ordering within catalog YAMLs | Alphabetical by `id` | Deterministic; supports stable PR diffs; FR-032 optional test enforces | By appearance / list order: rejected (non-deterministic on re-authorship) |
| Crosswalk edge ordering | Lexicographic on `{source.taxonomy, source.id, target.taxonomy, target.id}` | Deterministic; supports stable PR diffs; FR-032 optional test enforces | By authoring order: rejected (non-deterministic) |
| `tachi-control-category.yaml` `url` field | Relative repo path `.claude/skills/tachi-control-analysis/references/control-categories.md` | FR-007 pseudo-taxonomy-path convention; supports FR-028 file-path-or-URL validation | External pseudo-URL: rejected (no external source for tachi concepts) |
| `tachi-stride-ai-category.yaml` `url` field | Relative repo path `.claude/skills/tachi-shared/references/stride-categories-shared.md` | Same as above | Same as above |
| NIST Subcategory `url` field | NIST DOI-based URL pattern per FR-033 README canonical-URL convention | Stable; NIST DOIs have long-term persistence guarantees | Direct publication URL: rejected (rot-prone) |
| Integrity-test file-path validation | `pathlib.Path(citation).is_file()` relative to repo root | Stdlib-only; no filesystem walk required | Full glob resolution: rejected (out of scope) |
| Crosswalk edge authoring scale | Day 1 50-edge spike → projection; R3 Tier 1 default | Per PRD Risk R3; tripwire at 38.4s/edge | Straight-through authoring: rejected (no calibration) |
| ADR-027 authoring sequence | Proposed at end of Day 1 → Accepted at PR merge | Per PRD FR-10 Q5 resolution | Accept at start: rejected (premature commitment) |
| pytest subdirectory bootstrap | Empty `__init__.py` file at `tests/schemas/__init__.py` | Matches existing `tests/scripts/__init__.py` convention | Conftest-only: rejected (breaks pytest collection semantics) |

All Phase 0 decisions are additive-only. No runtime script modifications required.

---

## Phase 1: Design & Contracts

**Prerequisites**: `research.md` complete ✅

### 1.1 Data Model

**Location**: `specs/180-taxonomy-crosswalk-collection/data-model.md`

Documents two record shapes and three enum domains authoritative for F-A1:

**Catalog record shape** (per FR-003):
```yaml
- id: <short_canonical_id>           # string, required, unique within file
  full_id: <framework_prefixed_id>   # string, required
  name: <canonical_source_name>      # string, required, verbatim from source
  url: <retrievable_url_or_path>     # string, required, URL or internal path
  cwe_refs: [CWE-<N>, ...]           # list of strings, optional (omitted on cwe.yaml)
```

**Crosswalk edge shape** (per FR-009):
```yaml
- source:
    taxonomy: <7-value_enum>
    id: <id_in_source_catalog>
  target:
    taxonomy: <7-value_enum>
    id: <id_in_target_catalog>
  edge_type: <primary|related|superseded>
  confidence: <high|medium|low>
  citation: <non_empty_URL_or_path>
```

**Enum domains**:
- `taxonomy` (7 values): `owasp`, `mitre-attack`, `mitre-atlas`, `nist-ai-rmf`, `cwe`, `tachi-control-category`, `tachi-stride-ai-category`
- `edge_type` (3 values): `primary`, `related`, `superseded`
- `confidence` (3 values): `high`, `medium`, `low`

**Field-level validation rules** derived from spec.md FR-003 through FR-014 and encoded as integrity-test assertions (FR-027 through FR-032).

### 1.2 Contracts

**Location**: `specs/180-taxonomy-crosswalk-collection/contracts/`

Three contract artifacts specify the authored shape at byte precision:

1. **`catalog-record.yaml`** — Reference YAML demonstrating the per-item record shape with annotated comments (serves as a canonical example authors paste-and-adapt from)
2. **`crosswalk-edge.yaml`** — Reference YAML demonstrating the per-edge record shape with annotated comments
3. **`integrity-test-contract.md`** — Prose contract specifying the 4+1 test function signatures: `test_framework_yamls_load()`, `test_crosswalk_loads()`, `test_crosswalk_referential_integrity()`, `test_citation_shape()`, (optional) `test_records_sorted()`. Includes expected assertion messages for each failure mode per FR-028 edge-case acceptance scenario 4.6.

### 1.3 Quickstart

**Location**: `specs/180-taxonomy-crosswalk-collection/quickstart.md`

Step-by-step walkthrough for three audiences (mapping 1:1 to the 3 primary personas in spec.md):

1. **Adopter quickstart** — runnable Python snippet: `import yaml; records = yaml.safe_load(open('schemas/taxonomy/owasp.yaml')); llm05 = next(r for r in records if r['id'] == 'LLM05'); print(llm05['cwe_refs'])`. Demonstrates US-180-1 independent test.
2. **Maintainer quickstart** — grep over `crosswalk.yaml`: filter edges where `source.taxonomy == 'owasp' && source.id == 'LLM05'`; discover all cross-framework mappings; demonstrates US-180-2 independent test.
3. **Reviewer quickstart** — navigate README.md: §Purpose → §Provenance → §Calibration → §Update procedure; demonstrates US-180-3 independent test.

### 1.4 Agent Context Update (N/A for F-A1)

This feature does not modify any agent or command. No `agent script` invocation needed. If CLAUDE.md needs an update post-merge, it is handled by `/aod.deliver` (not `/aod.project-plan`).

### 1.5 Constitution Re-check (post-design)

✅ PASS (unchanged from pre-design). Design is 100% additive-only; no new violations surface.

---

## Phase 2: Task Breakdown (OUT OF SCOPE — `/aod.tasks`)

Task sequencing for F-A1 is generated by `/aod.tasks` into `tasks.md`. **Preview** of the 5-phase breakdown (per PRD Phase Breakdown):

- **Phase 1 (Day 1, parallel)**: schema freeze (architect) + ADR-027 Proposed (architect) + `owasp.yaml` authoring (senior-backend-engineer) + 50-edge crosswalk spike (web-researcher) + `tests/schemas/__init__.py` bootstrap (senior-backend-engineer)
- **Phase 2 (Day 2, parallel)**: MITRE ATT&CK + ATLAS + CWE + 2 pseudo-taxonomy YAMLs (senior-backend-engineer) + `nist-ai-rmf.yaml` catalog start (senior-backend-engineer) + continue crosswalk citation discovery (web-researcher) + README.md draft + 2 cross-reference link edits (architect)
- **Phase 3 (Day 3, parallel)**: complete `nist-ai-rmf.yaml` + author ~41 NIST-derived Surface B/C edges + assemble crosswalk records (senior-backend-engineer) + continue citation harvest toward ≥500 (web-researcher) + finalize README (architect)
- **Phase 4 (Day 4)**: author FR-027–FR-032 integrity tests (senior-backend-engineer) — **sequencing constraint per Architect F3**: integrity-test authoring MUST occur AFTER all 8 YAMLs are committed (not interleaved with authoring days) to avoid transient CI-fail on referential integrity + backward-compat byte-identity verification (code-reviewer) + ADR-027 Proposed→Accepted (architect) + PR opened
- **Phase 5 (Day 5, buffer)**: PR review cycle + ADR review iteration + crosswalk edge-count completion if Day 3 fell short + merge

Task-level DAG, agent assignments, and wave structure are deferred to `/aod.tasks`.

---

## Complexity Tracking

*Fill ONLY if Constitution Check has violations that must be justified*

**No violations detected**. F-A1 is content-authoring within additive constraints; all 7 applicable constitutional principles pass without justification.

---

## Risks & Mitigations (Plan-level)

Derived from PRD Risks + spec-phase refinements:

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| R1: crosswalk citation rate >38.4s/edge (PRD) | Medium | Medium | Day 1 50-edge spike; R3 Tier 2/3 fallback pre-authorized |
| R2: framework revision mid-flight (PRD) | Low | Low-Med | README pins version snapshot; CWE Top 25 2025 already current |
| R3: further scope reduction on crosswalk (PRD) | Low-Med | Low | Tier 1 ≥500 is default; Tier 2 ≥300 team-lead-authorizable |
| R4: NIST mapping latent error (PRD) | Low | Low | FR-024: file separate ADR-025 amendment Issue; do not silent-correct |
| R5: curation quality judged insufficient (PRD) | Low-Med | Medium | README FR-033 anti-drift rule; first-pass default `confidence: medium` |
| R6: single-agent execution extends to 5-6d (PRD) | Low-Med | Low | tasks.md explicitly declares 3-agent wave structure; fallback budget acceptable |
| **R7 (new, spec-phase)**: AML.T0059–T0062 unstable citations | Low | Low | FR-016 Day-2 tripwire — architect authorizes descope to ≥8 (seed + AML.T0058 only); <8 requires PRD amendment |
| **R8 (new, plan-phase)**: YAML authoring scale triggers pre-commit hook timeouts | Low | Low | Commit in batches (e.g., 1 YAML file per commit); pre-commit hooks operate per-file |

---

## Approval & Sign-Off (Plan-level)

**Required sign-offs** (per `.claude/rules/governance.md`):
- PM sign-off (product scope alignment with spec.md + PRD)
- Architect sign-off (technical approach soundness, constitutional compliance)

Sign-offs are written to this file's YAML frontmatter at the top of the document when the `/aod.project-plan` command completes its dual-review step.
