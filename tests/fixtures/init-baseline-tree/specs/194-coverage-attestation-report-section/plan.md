---
triad:
  pm_signoff:
    agent: product-manager
    date: 2026-04-18
    status: APPROVED
    notes: "Plan faithfully translates PRD v1.1 through spec.md. All 19 FRs and 12 SCs traceable; Success Criteria Mapping ties every SC to a day-level deliverable. All 3 P1 user stories have concrete phase ownership. PRD-resolved questions (Q1-A, Q2-A, Q6-D) preserved verbatim. Out-of-Scope preserved (no crosswalk JOIN, no internal taxonomy pages, no schema changes). Risk table correctly lists R1, R3-R9 (R2 eliminated per v1.1). Timeline honest: 4-day baseline preserved. Touch surface minimal and precedent-matched to Feature 141 + Feature 128."
  architect_signoff:
    agent: architect
    date: 2026-04-18
    status: APPROVED_WITH_CONCERNS
    notes: "Architecturally sound. Feature 141 pattern mirror verified (main.typ:47 import, :103 default guard, :246 dual-predicate conditional). Data contract additive-only with proper guards; classification rule (Q1-A) correctly encoded; partition invariant enforced. All 4 BLOCKER invariants preserved (SC-002, SC-009, FR-015, FR-017). ADR-029 dual-commit pattern correct. 3 fixtures sufficient; 100-finding pagination smoke correctly sized. 3 MEDIUM + 3 LOW findings absorbed inline: M-1 insertion-point refined from :348/:398 to post-findings-detail (~:393) before compensating-controls (:398); L-1 Edit 1 expanded to enumerate all 3 default guards as single atomic block. M-2 (F-A3 coordination as explicit task), M-3 (zero-denominator synthetic fixture), L-2 (MITRE per-finding merged vs per-framework split), L-3 (ADR cross-ref F128/F141) deferred to tasks.md enumeration."
  techlead_signoff: null  # Added by /aod.tasks
---

# Implementation Plan: Coverage Attestation Report Section

**Branch**: `194-coverage-attestation-report-section` | **Date**: 2026-04-18 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/194-coverage-attestation-report-section/spec.md`
**PRD**: [docs/product/02_PRD/194-coverage-attestation-report-section-2026-04-18.md](../../docs/product/02_PRD/194-coverage-attestation-report-section-2026-04-18.md)

## Summary

Add a conditional coverage-attestation section to the tachi PDF security report rendering (a) a per-finding attribution table and (b) one per-framework coverage matrix page per external framework in the 5-value taxonomy enum (OWASP, MITRE ATT&CK, MITRE ATLAS, NIST AI RMF, CWE). The feature is gated on a single new `has-source-attribution` boolean in the Typst data contract — `true` iff ≥1 finding carries a non-empty `source_attribution` array. When `false`, the entire section is omitted from the PDF (zero runtime impact, 5 non-agentic baselines byte-identical).

**Architectural approach**: Mirror the Feature 141 `has-attack-chains` pattern verbatim (new Typst page + boolean emission + conditional `main.typ` block with default-value guard and `.len() > 0` belt-and-suspenders check). New aggregator function in `scripts/extract-report-data.py` consumes the parsed finding list from `parse_threats_findings` (F-A2 round-trip verified at `scripts/tachi_parsers.py:796`), classifies every top-level record in each framework YAML as Covered / Partial / Gap, and emits per-finding rows + per-framework aggregates to the Typst contract.

**Touch points**: 1 new Typst template, 1 new aggregator function, 3 coordinated edits to `main.typ`, 1 new ADR, new test fixtures + aggregator unit tests. Zero schema changes, zero agent edits, zero skill edits.

## Technical Context

**Language/Version**: Python 3.11 (existing — stdlib + `pyyaml`); Typst (template language — existing runtime, no version bump required)
**Primary Dependencies**: `pyyaml` (runtime, already declared), `pytest` + `pytest-cov` (dev-only, already declared per Feature 128 precedent); no new runtime or dev dependencies
**Storage**: File-based; reads `schemas/taxonomy/*.yaml` (F-A1 catalogs) + parsed findings (F-A2 `source_attribution` field); writes Typst data-contract fragment consumed by `main.typ`
**Testing**: pytest (existing harness at `tests/scripts/`) + backward-compatibility test `tests/scripts/test_backward_compatibility.py` under `SOURCE_DATE_EPOCH=1700000000` (ADR-021)
**Target Platform**: Command-line Python tooling (macOS/Linux/WSL); PDF rendering via Typst + Mermaid CLI (mmdc) — neither added nor upgraded by this feature
**Project Type**: Single project (Python scripts + Typst templates + schema YAMLs in a unified repo); no frontend/backend split
**Performance Goals**: Aggregator <1s on 100-finding × 5-attribution fixture (informational floor, not CI-enforced); Typst compile time +≤2s on 100-finding × 5-framework fixture (falls within existing `tachi.security-report` budget)
**Constraints**: (a) SC-002 byte-identity on 5 non-agentic baselines under `SOURCE_DATE_EPOCH=1700000000` is a BLOCKER; (b) SC-009 22-file zero-edit invariant on 11 threat agents + 11 skill references is a BLOCKER; (c) FR-015 zero schema changes is a BLOCKER; (d) FR-017 no crosswalk JOIN is a scope boundary
**Scale/Scope**: 235 total framework YAML records (OWASP 60, MITRE ATT&CK 38, MITRE ATLAS 12, NIST AI RMF 72, CWE 53); pre-F-A3 baseline finding counts ~10-60 per example — F-B test smoke on synthetic 100-finding × 5-framework fixture bounds realistic scale

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Evaluated against `.aod/memory/constitution.md`:

| Principle | Status | Notes |
|-----------|--------|-------|
| I. General-Purpose Architecture | ✅ PASS | F-B is domain-agnostic renderer logic over a generic finding/taxonomy contract; no hardcoded project-type assumptions |
| II. API-First Design | N/A | No REST/GraphQL surface introduced; F-B is file-based CLI tooling (consistent with tachi pipeline convention) |
| III. Backward Compatibility (NON-NEGOTIABLE) | ✅ PASS | `has-source-attribution: false` default + default-value guard in `main.typ` + conditional gate → 5 baselines byte-identical. Local `.aod/` workflows unaffected |
| IV. Concurrency & Data Integrity | N/A | F-B is single-process, read-only over findings; no shared state, no locking required |
| V. Privacy & Data Isolation | ✅ PASS | Framework IDs are public vocabulary (OWASP / MITRE / NIST / CWE); no PII / secrets introduced |
| VI. Testing Excellence (MANDATORY) | ✅ PASS | Unit tests on aggregator (3 fixtures: empty, one-primary, multi-mixed); integration test on SC-002 byte-identity; Typst compile smoke on 100-finding fixture; Day 3 pagination smoke |
| VII. Definition of Done (NON-NEGOTIABLE) | ✅ PASS | PRD-defined SCs map to testable predicates; SC-002 + SC-009 are BLOCKER-level gates |
| VIII. Product-Spec Alignment | ✅ PASS | Approved PRD 194 exists; spec.md has PM APPROVED sign-off |
| IX. Documentation Standards | ✅ PASS | Public ADR-029 per Proposed → Accepted dual-commit pattern (FR-013); references to ADR-021/022/023/027/028 |
| X. Zero-Edit Invariant (ADR-023 / ADR-028 lineage) | ✅ PASS | FR-014 / SC-009 explicit; grep audit at PR pre-merge |

**Gate verdict**: No violations. No Complexity Tracking entries required.

## Project Structure

### Documentation (this feature)

```
specs/194-coverage-attestation-report-section/
├── plan.md                  # This file (/aod.project-plan output)
├── research.md              # Phase 0 output (already populated by /aod.spec)
├── data-model.md            # Phase 1 output — entity schemas
├── contracts/
│   └── typst-data-contract.md   # Typst-data-contract fragment spec
├── quickstart.md            # Phase 1 output — verification walkthrough
├── checklists/
│   └── requirements.md      # Spec quality checklist (already populated)
├── spec.md                  # PM-approved spec
└── tasks.md                 # Task breakdown (/aod.tasks output)
```

### Source Code (repository root)

```
tachi/
├── scripts/
│   └── extract-report-data.py        # MODIFY — new aggregator + has-source-attribution emission
│
├── templates/
│   └── tachi/
│       └── security-report/
│           ├── coverage-attestation.typ   # NEW — Typst page template (per-finding + 5 matrix pages)
│           └── main.typ                    # MODIFY — 3 coordinated edits: default guard, #import, conditional block
│
├── schemas/
│   ├── finding.yaml                  # UNCHANGED (FR-015 BLOCKER)
│   └── taxonomy/                     # UNCHANGED — read-only source of denominator counts
│       ├── owasp.yaml
│       ├── mitre-attack.yaml
│       ├── mitre-atlas.yaml
│       ├── nist-ai-rmf.yaml
│       └── cwe.yaml
│
├── docs/
│   └── architecture/
│       └── 02_ADRs/
│           └── ADR-029-coverage-attestation-report-section.md   # NEW — per-feature ADR
│
├── tests/
│   └── scripts/
│       ├── test_coverage_attestation.py   # NEW — aggregator unit tests
│       ├── test_backward_compatibility.py  # UNCHANGED — 5 baselines byte-identity gate (existing harness)
│       └── fixtures/
│           └── coverage_attestation/       # NEW — 3 fixtures (empty, one-primary, multi-mixed)
│               ├── empty_attribution.yaml
│               ├── one_primary_attribution.yaml
│               └── multi_mixed_attribution.yaml
│
├── examples/
│   ├── web-app/                      # UNCHANGED (5 non-agentic baselines — SC-002)
│   ├── microservices/
│   ├── ascii-web-api/
│   ├── free-text-microservice/
│   ├── maestro-reference/
│   └── agentic-app/                   # 6th example — may regenerate per Feature 128 convention (follow-on coordination with F-A3)
│
└── .claude/
    ├── agents/                        # UNCHANGED (FR-014 / SC-009 BLOCKER — 22-file zero-edit invariant)
    │   └── tachi/
    │       ├── stride/                # 6 files
    │       └── ai/                    # 5 files
    └── skills/                        # UNCHANGED (FR-014 / SC-009 BLOCKER)
        └── tachi-{agent-name}/
            └── references/
                └── detection-patterns.md   # 11 files
```

**Structure Decision**: Single-project layout (existing tachi repo structure). No new top-level directories. All changes confined to `scripts/`, `templates/tachi/security-report/`, `docs/architecture/02_ADRs/`, `tests/scripts/`. Follows Feature 141 + Feature 128 precedent verbatim.

## System Design

### Components

**New components (F-B-owned)**:

1. **Coverage Attestation Aggregator** (`scripts/extract-report-data.py` — new function)
   - Reads parsed finding list (from F-A2's `parse_threats_findings` at `scripts/tachi_parsers.py:796`)
   - Loads 5 external-framework YAMLs (`schemas/taxonomy/{owasp,mitre-attack,mitre-atlas,nist-ai-rmf,cwe}.yaml`) via `yaml.safe_load` — computes `yaml_record_count` ONCE per framework
   - Emits per-finding rows + per-framework aggregates to the Typst data contract
   - Emits `has-source-attribution` boolean flag
   - Invoked from `extract-report-data.py`'s main `extract()` pathway after findings are parsed; output joins the Typst data contract alongside existing `has-maestro-data` / `has-attack-chains` / `has-attack-trees` flags

2. **Coverage Attestation Typst Template** (`templates/tachi/security-report/coverage-attestation.typ` — new file)
   - Single exported function `coverage-attestation-page(per-finding-rows, per-framework-aggregates)` (name canonical per precedent; final name implementation-owned)
   - Renders per-finding attribution table (single paginated table, Typst native row-break, 7 columns)
   - Renders 5 per-framework pages (one per external framework) with Covered / Partial / Gap classification, coverage percentage, and Partial count disclosure
   - Reuses existing `templates/tachi/security-report/` styling conventions (severity colors, branded headers/footers, page layout)

3. **Main Template Integration** (`templates/tachi/security-report/main.typ` — 3 coordinated edits)
   - Edit 1 (default-value guards — **single atomic edit block** per architect L-1): in the §2b defaults block (around lines 89-107), add three coordinated guards mirroring the existing defaults for `has-attack-chains` et al.:
     ```typst
     #let has-source-attribution = if has-source-attribution != none { has-source-attribution } else { false }
     #let per-finding-rows = if per-finding-rows != none { per-finding-rows } else { () }
     #let per-framework-aggregates = if per-framework-aggregates != none { per-framework-aggregates } else { () }
     ```
     Prevents "variable not found" on stale `report-data.typ` snapshots (FR-004, SC-4a). All 3 guards land as a single atomic block; partial landings would leave `main.typ` in a broken intermediate state.
   - Edit 2 (import): at the top of `main.typ` (existing imports around line 43-47), add `#import "coverage-attestation.typ": coverage-attestation-page`. Unconditional import is byte-identical on the 5 baselines (precedent: `main.typ:47`).
   - Edit 3 (conditional inclusion): insert AFTER the always-rendered findings-detail-page (~`main.typ:393`) and BEFORE the compensating-controls block (`main.typ:398`) — **architect M-1 insertion-point refinement**. The original `:348` citation is the *opening* of the MAESTRO block (closes at `:366`); between `:366` and `:398` sit the Detailed Findings section divider (`:370`) and the always-rendered findings-detail-page (`:388`). Coverage attestation belongs AFTER detailed findings (logical "per-finding-enhancement" ordering) and BEFORE mitigation-tier content. Insert:
     ```typst
     #if has-source-attribution and per-finding-rows.len() > 0 {
       coverage-attestation-page(per-finding-rows: per-finding-rows, per-framework-aggregates: per-framework-aggregates)
     }
     ```
     The `.len() > 0` check mirrors `main.typ:246` (Feature 141 precedent).

4. **ADR-029** (`docs/architecture/02_ADRs/ADR-029-coverage-attestation-report-section.md` — new file)
   - Proposed → Accepted dual-commit pattern (Feature 180 / 189 precedent)
   - Documents 7 decision surfaces (enumerated in FR-013 / SC-007)
   - Cross-references ADR-021 / 022 / 023 / 027 / 028 lineage

**Touched-but-unchanged components** (read-only dependencies, zero-edit):

- `scripts/tachi_parsers.py::parse_threats_findings` (F-A2 round-trip at line 796)
- `schemas/finding.yaml` (schema v1.5, `source_attribution` field at line 212 — unchanged)
- `schemas/taxonomy/*.yaml` (5 external + 2 internal catalogs — unchanged; read-only source of YAML record counts)

**Explicitly not touched** (BLOCKER-level zero-edit scope per FR-014 / SC-009):

- All 11 threat-agent files under `.claude/agents/tachi/stride/*.md` (6) and `.claude/agents/tachi/ai/*.md` (5)
- All 11 skill-reference `detection-patterns.md` files under `.claude/skills/tachi-{agent-name}/references/`
- `schemas/taxonomy/crosswalk.yaml` (FR-017 — no cross-framework JOIN)
- `schemas/finding.yaml` (FR-015 — no schema changes)

### Data Flow

```
┌────────────────────────────────────────────────────────────────────────┐
│                     Tachi Pipeline (unchanged upstream)                │
│                                                                        │
│  threats.md  ─┬─▶  parse_threats_findings  ─▶  finding list            │
│               │    (tachi_parsers.py:796                               │
│               │     round-trips source_attribution)                    │
│               │                                                        │
│               └─▶  Section 9 YAML block (ADR-028 Decision 2)           │
└────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│              NEW — Coverage Attestation Aggregator (F-B)               │
│              (scripts/extract-report-data.py)                          │
│                                                                        │
│  Input:   finding list (F-A2 parsed; zero schema changes required)    │
│                                                                        │
│  Step 1:  Scan findings for any non-empty source_attribution array   │
│           → sets has_source_attribution = True/False                   │
│                                                                        │
│  Step 2:  For each of 5 external frameworks, load                      │
│           schemas/taxonomy/{framework}.yaml via yaml.safe_load        │
│           → compute yaml_record_count = len(top-level list)           │
│           → cache once per-invocation (per-run dict, no module state)│
│                                                                        │
│  Step 3:  For each finding with source_attribution, group by           │
│           taxonomy: owasp_refs, mitre_refs, nist_refs, cwe_refs       │
│           → MITRE column merges mitre-attack + mitre-atlas with        │
│             per-ref prefix                                             │
│                                                                        │
│  Step 4:  For each framework YAML record, classify:                    │
│           - Covered  → ≥1 finding cites id with relationship=primary  │
│           - Partial  → zero primary AND ≥1 related/derived            │
│           - Gap      → zero attributions                              │
│                                                                        │
│  Step 5:  Compute per-framework aggregates:                           │
│           {framework, yaml_record_count, covered_count,               │
│            partial_count, gap_count, coverage_percentage}             │
│           coverage_percentage = covered_count / yaml_record_count     │
│                                                                        │
│  Edge handling:                                                        │
│    - yaml_record_count == 0 → coverage_percentage = "N/A"            │
│    - covered_count == 0 → coverage_percentage = "0.00%"              │
│    - yaml.safe_load raises → fail loud (ADR-022), bubble up           │
└────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│       Typst Data Contract (Generated — extract-report-data.py)         │
│                                                                        │
│  #let has-source-attribution = true|false                              │
│  #let per-finding-rows = (                                             │
│    (id: "...", title: "...", severity: "...",                         │
│     owasp-refs: (...), mitre-refs: (...),                             │
│     nist-refs: (...), cwe-refs: (...)),                               │
│    ...                                                                 │
│  )                                                                     │
│  #let per-framework-aggregates = (                                     │
│    (framework: "owasp", yaml-record-count: 60,                        │
│     covered-count: K, partial-count: P, gap-count: G,                 │
│     coverage-percentage: "X.XX%"|"N/A",                                │
│     items: ((id: "...", classification: "covered"|"partial"|"gap"),   │
│             ...)),                                                     │
│    ... 5 records total                                                 │
│  )                                                                     │
└────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                NEW — Coverage Attestation Typst Template               │
│                (templates/tachi/security-report/coverage-attestation)  │
│                                                                        │
│  Gated by main.typ:                                                    │
│    #if has-source-attribution and per-finding-rows.len() > 0 {        │
│      coverage-attestation-page(...)                                    │
│    }                                                                   │
│                                                                        │
│  Renders:                                                              │
│    1. Section divider + header                                         │
│    2. Per-finding attribution table (single paginated, 7 cols)        │
│    3. 5 × per-framework matrix pages (always-5 per Q4 resolution)     │
│       - Covered items (bold / primary-signaled)                        │
│       - Partial items (distinct secondary styling)                    │
│       - Gap items (color + icon, WCAG AA color-blind)                 │
│       - Coverage summary: "Covered: K/N = X.XX% · Partial: P · Gap: G"│
└────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
                              PDF Output
                         (via Typst compile step)
                         Byte-identical on 5
                         baselines when gate=false.
```

### Tech Stack

**Runtime (no changes)**:
- Python 3.11 (existing)
- `pyyaml` (existing runtime dep, declared in `requirements.txt` / `requirements-dev.txt`)
- Typst (existing — template language; no version bump)

**Developer tooling (no new additions)**:
- `pytest` + `pytest-cov` (existing, dev-only per Feature 128 precedent)
- `mmdc` (Mermaid CLI — unused by F-B; F-B does NOT add Mermaid-rendered attack-tree content)

**No npm / Node.js additions**. **No new Typst imports outside the new local module**. **No new external HTTP dependencies**.

## Phase 0: Research (Already Complete)

Phase 0 research was completed during `/aod.spec` execution and persisted to `specs/194-coverage-attestation-report-section/research.md`. Findings summary:

- **KB validation**: 8 KB entries directly applicable (KB-031 phase-insertion, KB-034 byte-identity, KB-023 centralized parser, PAT-013 Typst hub-first, KB-022 template parity, KB-029 no silent fallbacks, KB-036 ADR dual-commit, PAT-017 template parity audit).
- **Codebase audit**: All PRD line-number citations verified (`main.typ:47`, `:89-107`, `:103`, `:246`, `:348`, `:398`; `extract-report-data.py:1362`, `:1426`; `tachi_parsers.py:796`; `finding.yaml:212`).
- **Taxonomy record counts verified**: OWASP 60, MITRE ATT&CK 38, MITRE ATLAS 12, NIST AI RMF 72, CWE 53 = 235 total (matches PRD A5; Explore agent's 887 count was a line-count artifact, not YAML record count).
- **Backward-compat harness**: `tests/scripts/test_backward_compatibility.py:38-45` enumerates the 5 non-agentic baselines. Spec correctly references the harness directly rather than hardcoding the list (PRD v1.1 listed `mermaid-agentic-app` but the actual harness contains `maestro-reference` per F145 delivery).

**NEEDS CLARIFICATION count**: 0. All 8 PRD questions resolved (Q1-A through Q8); Q5 has a pre-approved architect fallback if the ux-ui-designer memo slips.

**Output**: `research.md` (already populated).

## Phase 1: Design & Contracts

### Entities (to be enumerated in `data-model.md`)

- **Finding** (existing; F-A2 schema-level) — read-only input
- **Source Attribution Record** (existing; F-A2) — read-only input
- **Framework Catalog Record** (existing; F-A1) — read-only input
- **Per-Finding Attribution Row** (new — F-B aggregator output, Typst-consumed)
- **Per-Framework Aggregate Record** (new — F-B aggregator output, Typst-consumed)
- **Framework Item Classification** (new — per-item triad value: covered | partial | gap)
- **Coverage Percentage** (new — string, format `"X.XX%"` or `"N/A"`)

Detailed schemas, field types, and validation rules in `data-model.md`.

### Contracts (to be enumerated in `contracts/typst-data-contract.md`)

F-B's single external contract is the **Typst data contract** emitted by `extract-report-data.py` and consumed by `main.typ` + `coverage-attestation.typ`. No REST/GraphQL surface introduced.

Contract artifacts:

1. `#let has-source-attribution = true|false` — single boolean
2. `#let per-finding-rows = ( … )` — array of records (per-finding)
3. `#let per-framework-aggregates = ( … )` — array of 5 records (one per external framework)

Detailed record shapes, field enumeration, Typst value-type mapping (string / int / array / dictionary), and consumer-side contract obligations in `contracts/typst-data-contract.md`.

### Quickstart

Verification walkthrough (to be enumerated in `quickstart.md`):

1. Checkout feature branch
2. Run `pytest tests/scripts/test_coverage_attestation.py` — aggregator unit tests pass
3. Run `SOURCE_DATE_EPOCH=1700000000 pytest tests/scripts/test_backward_compatibility.py` — 5 baselines byte-identical
4. Run pipeline on the `one_primary_attribution.yaml` fixture — PDF contains the coverage-attestation section with populated table + 5 framework pages
5. Run pipeline on an un-attributed architecture (any of the 5 baselines) — PDF omits the section entirely (confirmed by grep / byte-comparison against baseline)
6. Render smoke fixture on 100-finding × 5-framework synthetic fixture — Day 3 pagination smoke visual check

Detailed commands + expected outputs in `quickstart.md`.

### Agent Context Update

No explicit agent context update is required for F-B:

- No new runtime technology (Python, Typst, pyyaml all pre-established)
- No new test framework (pytest pre-established per Feature 128)
- No new CLI prerequisites (mmdc is unused by F-B; Typst is pre-established per Feature 112)

The existing `CLAUDE.md` + `.claude/rules/` already describe all technologies F-B touches. An explicit `update-agent-context.sh` run produces a no-op diff; skipping preserves that invariant.

## Constitution Re-Check (Post-Design)

Re-evaluated after Phase 1 design:

| Principle | Status | Notes |
|-----------|--------|-------|
| I. General-Purpose Architecture | ✅ PASS | Design remains domain-agnostic |
| III. Backward Compatibility | ✅ PASS | Data contract + default-value guard keep 5 baselines byte-identical |
| VI. Testing Excellence | ✅ PASS | 3 fixtures, aggregator unit tests, byte-identity regression, pagination smoke |
| VII. Definition of Done | ✅ PASS | 12 SCs all testable; SC-002 + SC-009 BLOCKER-level |
| X. Zero-Edit Invariant | ✅ PASS | 22-file audit at PR pre-merge (SC-009) |

**Post-design verdict**: No new violations introduced. Complexity Tracking remains empty.

## Complexity Tracking

*No Constitution Check violations — table intentionally empty.*

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| _(none)_ | _(none)_ | _(none)_ |

## Risks & Mitigations (from PRD + research)

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| R1 — Typst table pagination ugly on 100+ rows | Low | Low | Day 3 pagination smoke on 100-finding fixture; per-severity split + landscape-orientation fallbacks pre-approved |
| R3 — F-A3 ships during F-B authoring | Low | Medium | Day 2 EOD coordination check; second-merger re-baselines (~0.5-1d absorbed cost) |
| R4 — Coverage-percentage arithmetic edges | Low | Low | FR-011 handles zero-denominator (`N/A`), zero-numerator (`0.00%`), malformed YAML (fail loud per ADR-022) |
| R5 — Adopter misreads 0% as "tachi has no coverage" | Certain (dormant) | Low | Gate suppresses section entirely when `false`; risk activates only if F-A3 populates findings with 0% coverage — F-A3 PRD will address UX |
| R6 — Typst compile time on 235-item × 5-page render | Low | Low | 235 × ~50 bytes = ~12KB table data; Typst renders <200ms; 2s budget ample |
| R7 — Hierarchical MITRE records complicate aggregator | Medium | Low | MITRE YAML is flat (38 top-level records, dotted IDs are string-opaque); no traversal required |
| R8 — Per-finding table font/width issues (7 cols portrait) | Medium | Low | Day 3 pagination smoke catches; landscape-orientation fallback pre-approved |
| R9 — Partial blending into coverage percentage misreads | Certain | Low | MED-3 resolution: Partial count rendered alongside percentage with equal visual weight |

## Timeline Outline (PRD-aligned)

**Day 1 (2026-04-20 Mon) — Design Lock + Wave 1.1 Parallel Scaffolding**

- Wave 1.0 (architect): ADR-029 Proposed commit; Q5 ux-ui-designer handoff
- Wave 1.1 (parallel): aggregator test fixtures (tester); Typst skeleton (senior-backend-engineer); `has-source-attribution` boolean emission wiring (Q-independent)

**Day 2 (2026-04-21 Tue) — Aggregator + Q5 Landing**

- Q5 ux-ui-designer memo lands (color + icon spec)
- Aggregator function complete + unit tests green (senior-backend-engineer + tester)
- Day 2 EOD coordination check: F-A3 filed-as-Issue status (team-lead)

**Day 3 (2026-04-22 Wed) — Typst Finalization + Integration**

- `coverage-attestation.typ` complete on populated fixture
- `main.typ` 3 coordinated edits (default guard, `#import`, conditional block)
- Day 3 pagination smoke + `#import` byte-identity smoke (senior-backend-engineer)

**Day 4 (2026-04-23 Thu) — Backward-Compat + ADR Accepted**

- SC-002 byte-identity regression green (tester primary, senior-backend-engineer secondary)
- ADR-029 transitioned Proposed → Accepted (architect)
- PR submitted, triple sign-off

## Success Criteria Mapping (Plan ↔ Spec)

Plan phase coverage of spec SCs:

- SC-001 (Typst template compiles): Day 3 deliverable — Typst compile smoke
- SC-002 (5 baselines byte-identical): Day 4 deliverable — SC-002 regression
- SC-003 (`has-source-attribution` boolean correctness): Day 2 deliverable — aggregator unit tests
- SC-004 (3 `main.typ` edits correct): Day 3 deliverable — manual inspection + SC-002 gate
- SC-005 (coverage-percentage arithmetic): Day 2 deliverable — aggregator unit tests
- SC-006 (WCAG AA color + icon distinction): Day 2 deliverable (Q5 memo) + Day 3 deliverable (Typst rendering)
- SC-007 (ADR-029 committed): Day 1 Proposed + Day 4 Accepted
- SC-008 (zero new deps): diff check at PR pre-merge (ongoing verification)
- SC-009 (22-file zero-edit): grep audit at PR pre-merge (ongoing verification)
- SC-010 (performance bounds): Day 3 pagination smoke (informational)
- SC-011 (unit test coverage): Day 2 deliverable
- SC-012 (Day 3 pagination smoke): explicit Day 3 deliverable

## References

- [spec.md](./spec.md) — PM-approved feature specification
- [research.md](./research.md) — Phase 0 research (KB findings, code citations, precedent audit)
- [data-model.md](./data-model.md) — Phase 1 entity schemas (generated alongside this plan)
- [contracts/typst-data-contract.md](./contracts/typst-data-contract.md) — Phase 1 contract spec (generated alongside this plan)
- [quickstart.md](./quickstart.md) — Phase 1 verification walkthrough (generated alongside this plan)
- PRD v1.1: `docs/product/02_PRD/194-coverage-attestation-report-section-2026-04-18.md`
- ADR-021 / 022 / 023 / 027 / 028 lineage: `docs/architecture/02_ADRs/`
- Feature 141 precedent (`has-attack-chains`): `specs/141-maestro-phase-2-*/`
- Feature 128 precedent (new Typst page + boolean): `specs/128-executive-architecture-infographic/`
