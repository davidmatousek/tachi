---
prd:
  number: 194
  topic: coverage-attestation-report-section
  created: 2026-04-18
  status: Delivered
  delivered: 2026-04-18
  pr: 195
  merge_sha: c4b8dc6
  type: feature
triad:
  pm_signoff: {agent: product-manager, date: 2026-04-18, status: APPROVED, notes: "Problem statement grounded in F-A2 delivery (Feature 189 same-day lineage). 3 user stories preserved verbatim from Issue #194 with job-story restructuring. 9 success criteria (SC-1 to SC-9). MVP classification narrowed to 3-value (Covered/Partial/Gap) per architect Q6-D; Out-of-Scope deferred to follow-on. PRD R2 factual error corrected in v1.1: MITRE ATT&CK is 38 records (F-A1 curated subset), not 600+; Q2 collapses to trivial Q2-A full YAML record count. Q-P1 resolved NO per Feature 189 precedent — sample records belong in test fixtures, not example outputs. Ready for /aod.plan."}
  architect_signoff: {agent: architect, date: 2026-04-18, status: APPROVED_WITH_CONCERNS, notes: "0 BLOCKING / 3 HIGH / 5 MEDIUM / 4 LOW. Precedent claims verified (Feature 141 has-attack-chains, Feature 128 new-Typst-page, parse_threats_findings round-trips source_attribution). SC-2 gate architecturally correct; SC-9 22-file zero-edit invariant preserved by design. HIGH findings absorbed inline: (H-1) default-value guard added to FR-4 for backward-compat with stale report-data.typ; (H-2) `.len() > 0` belt-and-suspenders check added to FR-4 per Feature 141 precedent; (H-3) R2 factual error corrected — MITRE ATT&CK is 38 records, not 600+; Q2 collapses to Q2-A. Open questions adjudicated: Q1-A (Partial=related/derived-only), Q2-A (full YAML record count), Q3-A (single paginated table), Q4 render-all-5, Q6-D (omit Out-of-Scope from MVP), Q7 confirmed placement, Q8 ADR-029, Q-P1 NO. 4 new risks surfaced (R6-R9) with mitigations. Q5 visual treatment defers to ux-ui-designer memo Day 2 AM."}
  techlead_signoff: {agent: team-lead, date: 2026-04-18, status: APPROVED_WITH_CONCERNS, notes: "0 BLOCKING / 1 HIGH / 3 MEDIUM / 2 LOW. Calendar verified correct (2026-04-20 Mon, 2026-04-23 Thu). Timeline: 4 days realistic planning baseline; 3 days aspirational, contingent on Q1-A + Q2-A + Q6-D path. Agent assignments valid against `.claude/agents/_README.md`; no over-parallelism; all agents ≤80% load per day. Concerns addressed inline: (H-1) Q2 schema-extension risk neutralized by architect Q2-A trivial-collapse resolution (H-3 factual correction); (M-1) Q6 scope expansion neutralized by Q6-D resolution; (M-2) Day 2 EOD F-A3 merge-order coordination check added to Phase Breakdown; (M-3) Wave 1.1 parallel scaffolding promoted to explicit Day 1 milestones; (L-1) Q5 due date shifted to Day 2 AM. F-A1 + F-A2 dependencies verified satisfied. Ready for /aod.plan."}
source:
  idea_id: 194
  story_id: null
---

# F-B — Coverage Attestation Report Section: Product Requirements Document

**Status**: Delivered
**Created**: 2026-04-18
**Delivered**: 2026-04-18 (PR [#195](https://github.com/davidmatousek/tachi/pull/195), squash commit `c4b8dc6`)
**Spec**: [specs/194-coverage-attestation-report-section/spec.md](../../../specs/194-coverage-attestation-report-section/spec.md)
**Author**: product-manager
**Reviewers**: architect, team-lead
**Phase**: BLP-01 Coverage Attestation Reporting tier — first downstream demand-side consumer of the Foundation tier (F-A1 + F-A2)
**Priority**: P1

---

## 📋 Executive Summary

### The One-Liner

Render tachi's OWASP / MITRE ATT&CK / MITRE ATLAS / NIST AI RMF / CWE coverage directly inside the PDF security report — per-finding citation table plus per-framework coverage matrix with gap highlighting — so adopters see attested coverage *and* gaps without reading `threats.md` source or hand-maintaining a spreadsheet.

### Problem Statement

Feature 180 (F-A1, delivered 2026-04-17) shipped the machine-readable taxonomy vocabulary. Feature 189 (F-A2, delivered 2026-04-17) shipped the finding-level `source_attribution` contract. Together the two foundation features give every tachi finding a machine-readable way to cite OWASP / MITRE / NIST / CWE items, and give every taxonomy a machine-readable record of its items. **But adopters looking at tachi's flagship adopter-facing artifact — the PDF security report — still see nothing about coverage.** The citations are in `threats.md` YAML (Section 9, F-A2 Decision 2). The taxonomy denominators are in `schemas/taxonomy/*.yaml`. Nothing joins them for a PDF reader.

An adopter or security reviewer today must open `threats.md`, cross-reference `schemas/taxonomy/owasp.yaml`, and compute per-framework coverage by hand — the exact ad-hoc audit pattern the BLP-01 §6 "Coverage Matrix" was drafted to replace. Worse, **gaps** (taxonomy items with zero attributions) are invisible unless the reviewer already knows what to look for.

F-B is the demand-side consumer that closes this gap by rendering the join inside the PDF.

### Proposed Solution

Add a new conditional Typst page template `templates/tachi/security-report/coverage-attestation.typ` that renders two views in the PDF:

1. **Per-finding attribution table** — one row per finding, columns `Finding ID | Title | Severity | OWASP refs | MITRE refs | NIST refs | CWE refs`. Each ref cell lists that finding's `source_attribution` IDs per taxonomy, with `relationship: primary` rendered bold and `related`/`derived` plain. Findings with no `source_attribution` render as blank cells — visible absence, not hidden.
2. **Aggregate per-framework coverage matrix** — one page per framework (OWASP / MITRE ATT&CK / MITRE ATLAS / NIST AI RMF / CWE). Each page shows every item in the framework YAML as **Covered** (≥1 primary attribution), **Partial** (only related or derived attributions — no primary), or **Gap** (zero attributions). Per-framework coverage percentage = (items with ≥1 primary attribution) / (total items in the framework YAML). Partial count is rendered alongside the percentage so adopters see the full classification at a glance (e.g., "Covered: 12/38 = 31.6% · Partial: 3 · Gap: 23"). **Gap items** are visually highlighted with color + icon to preserve color-blind accessibility (Q5, ux-ui-designer-owned memo).

The whole section is gated on a single new boolean in `scripts/extract-report-data.py` — `has-source-attribution` — set `true` iff ≥1 finding carries a non-empty `source_attribution` array. When `false`, `main.typ` omits `coverage-attestation.typ` entirely — **zero runtime impact**. This is the direct Feature 141 `has-attack-chains` pattern: new conditional section + new boolean + absence-means-byte-identical-PDF.

**Three things the solution is deliberately NOT:**
1. It is **not** a wiring of threat-detection agents to *populate* `source_attribution`. That is F-A3. F-B reads whatever the findings carry; if they carry nothing, the section is omitted.
2. It is **not** a cross-framework reasoning surface (e.g., "OWASP LLM05 maps to MITRE ATLAS AML.T0051 via `crosswalk.yaml` — here's the composite coverage"). The crosswalk JOIN is out of scope for F-B MVP; the F-B matrix is **intra-framework only**.
3. It is **not** a 4-value classification with Out-of-Scope as a first-class category. Architect Q6-D narrowed MVP to 3 values (Covered / Partial / Gap). Out-of-Scope handling deferred to a follow-on feature once adopter demand is visible. All non-cited items classify as Gap.

### Success Criteria

- **SC-1** — `templates/tachi/security-report/coverage-attestation.typ` exists, compiles without Typst errors, and renders both views when invoked with a populated fixture.
- **SC-2** — The 5 existing non-agentic example PDFs (`web-app`, `microservices`, `ascii-web-api`, `mermaid-agentic-app`, `free-text-microservice`) regenerate **byte-identically** under `SOURCE_DATE_EPOCH=1700000000` per ADR-021 (zero-impact-when-absent invariant).
- **SC-3** — `scripts/extract-report-data.py` emits `has-source-attribution` in the Typst data contract with value `true` iff ≥1 finding carries a non-empty `source_attribution` array; otherwise `false` — no implicit defaults.
- **SC-4** — `templates/tachi/security-report/main.typ` (a) adds a default-value guard block `#let has-source-attribution = if has-source-attribution != none { has-source-attribution } else { false }` in the §2b defaults block mirroring the 6 existing default guards, AND (b) invokes `coverage-attestation.typ` only inside `#if has-source-attribution and per-finding-rows.len() > 0 { ... }` — zero template output when `false` or when the data contract carries zero per-finding rows.
- **SC-5** — Per-framework coverage percentage formula `(items with ≥1 primary attribution) / (F-A1 framework YAML record count)` matches a manual-sampled cross-check on ≥1 fixture example. The denominator traces to an authoritative F-A1 YAML record count computed once per framework at data-extraction time. All 5 taxonomy YAMLs are modest in scale — F-A1 already curated representative subsets (OWASP 60 records, MITRE ATT&CK 38, MITRE ATLAS 12, NIST AI RMF 72, CWE 53; total 235 items).
- **SC-6** — Gap items render with a visible color+icon distinction from Covered and Partial items (color-blind accessible per WCAG AA — color alone is insufficient). Partial count is rendered alongside the coverage percentage on every per-framework page so adopters see the full classification at a glance.
- **SC-7** — Public per-feature ADR-029 is committed (Proposed → Accepted dual-commit pattern, mirrors Feature 180/189 precedent) documenting the new Typst template, the aggregator-function contract, the `has-source-attribution` conditional-inclusion pattern, the 3-value classification for MVP (Covered / Partial / Gap), the Out-of-Scope deferral, and the zero-crosswalk-JOIN scope line.
- **SC-8** — Zero new runtime dependencies — empty diff on `pyproject.toml`, `requirements*.txt`, `package.json`.
- **SC-9** — Zero edits to the 22-file F-A2 zero-edit-invariant scope (11 threat-detection agents + 11 skill-reference `detection-patterns.md` files) preserved per ADR-023 + ADR-028 governance.

### Timeline

Target: **4 working days** of active implementation (Typst page + aggregator + fixtures + tests + ADR) as the realistic planning baseline, with **3 days aspirational** contingent on the Q1-A + Q2-A + Q6-D happy path and Q5 (ux-ui-designer memo) landing Day 2 AM. Delivery window **2026-04-20 (Monday) → 2026-04-23 (Thursday)** — 2026-04-18 is Saturday; Day 1 = first working day after PRD approval. Team-lead review verified the calendar; all weekday labels (Mon/Tue/Wed/Thu) are correct. The Wave 1.1 parallel scaffolding stream (tester fixture authoring + senior-backend-engineer Typst template skeleton) proceeds Q-independently on Day 1 AM, saving ~0.25-0.5 day wall-clock time.

---

## 🎯 Strategic Alignment

### Product Vision Alignment

**Reference**: `docs/product/01_Product_Vision/product-vision.md`

tachi's vision — "Automated threat modeling toolkit extending STRIDE with AI-specific threat agents for agentic applications" — is fulfilled *at the detection tier* and *at the data tier* but fails at the *adopter-facing reporting tier* without F-B. An adopter evaluating "does tachi give me the coverage story I need for my compliance program?" reads the PDF first, not `threats.md` YAML. The PDF is where vision translates to adoption; F-B is where coverage translates to PDF.

### BLP-01 Initiative Fit

**Reference**: `BLP-01 threat coverage` memory — F-B is the downstream demand-side consumer closing the BLP-01 Foundation tier; it is the feature that justifies the foundation investment by giving adopters a visible product surface that reads from it.

F-B's place in the BLP-01 chain:

```
F-A1 (Feature 180, delivered 2026-04-17)
  │  Supply side: 7 framework YAML catalogs + 526-edge crosswalk
  ▼
F-A2 (Feature 189, delivered 2026-04-17)
  │  Demand contract: source_attribution field on findings
  ▼
F-A3 (follow-on, not yet delivered)
  │  Populators: 11 threat agents cite IDs during detection
  ▼
F-B (this PRD, #194)
  │  Adopter-facing renderer: per-finding table + per-framework coverage matrix in PDF
  ▼
(Ecosystem integrations / dashboards — out-of-tachi consumer tier)
```

**F-B may merge before F-A3 ships.** The `has-source-attribution` gate ensures the section is omitted when findings carry no attributions — which is the current state of every baseline and every freshly-run pipeline pre-F-A3. F-B's correctness is verifiable against any fixture whose findings carry populated attributions, independent of F-A3 shipping. This is an explicit design choice per Issue #194 body: "F-B MAY be authored before F-A3 ships — the boolean gate means absent attributions produce a no-op PDF."

### Recent ADR Lineage

- **ADR-028** (Feature 189, Accepted 2026-04-17): establishes the 5-value `taxonomy` enum, the `relationship` 3-value enum with `primary` default, the referential-integrity contract, and the Q1-E Section 9 YAML-block serialization surface. F-B consumes all four — the 5-value enum becomes the 5 coverage-matrix pages, the `relationship` enum becomes the Covered/Partial discrimination rule, the referential-integrity contract is already enforced at parse time (F-B trusts it), and the Section 9 YAML block is the data surface F-B reads via `parse_threats_findings`.
- **ADR-027** (Feature 180, Accepted 2026-04-17): establishes the 7-value taxonomy catalog. F-B reads 5 of the 7 (external frameworks only, matching the ADR-028 subset). The 2 internal taxonomies (`tachi-control-category`, `tachi-stride-ai-category`) are excluded from F-B for the same reason they are excluded from F-A2: they are internal vocabulary, not an external framework tachi claims coverage of.
- **ADR-021** (byte-determinism under `SOURCE_DATE_EPOCH`): SC-2 regression gate uses this harness.
- **Feature 141 precedent** (attack chains): the `has-attack-chains` boolean + new conditional Typst page pattern is the architectural template F-B copies. Same gate shape, same zero-impact-when-absent semantics, same additive-inclusion-block in `main.typ`, including the `.len() > 0` belt-and-suspenders check (main.typ:246-263).
- **Feature 128 precedent** (executive architecture infographic): the "new Typst page + extract-report-data.py boolean + conditional main.typ inclusion + 5 baselines byte-identical / 6th may regenerate" pattern is the direct precedent F-B follows.

### Roadmap Fit

- **Phase**: BLP-01 Coverage Attestation Reporting tier (Q2 2026 roadmap)
- **Week**: Week of 2026-04-20 — immediate follow-on to Feature 189 (F-A2) delivery
- **Dependencies**:
  - F-A1 (Feature 180, taxonomy YAMLs supply denominator counts) — **SATISFIED** as of 2026-04-17 (verified: `schemas/taxonomy/` contains all 7 YAMLs + crosswalk.yaml + README.md)
  - F-A2 (Feature 189, `source_attribution` schema contract) — **SATISFIED** as of 2026-04-17 (verified: `schemas/finding.yaml:212` carries the field; `scripts/tachi_parsers.py:796` round-trips it)
  - F-A3 (populators) — **NOT required for F-B to ship**. The `has-source-attribution` gate means F-B is a no-op PDF-wise on any architecture whose findings carry no attributions.

---

## 🧑‍💼 Target Users & Personas

### Primary Persona: **Security Reviewer**

- **Role**: Engineer or consultant auditing tachi output against a compliance framework (OWASP LLM Top 10, NIST AI RMF, MITRE ATT&CK, etc.)
- **Goal**: Answer "which OWASP / MITRE / NIST / CWE items does a specific finding cite, and which are gaps across the full engagement?" using the PDF alone
- **Pain Point Today**: Must open `threats.md`, parse Section 9 YAML, cross-reference `schemas/taxonomy/*.yaml`, and compute per-framework coverage by hand
- **Value Delivered**: Inline per-finding citation table answers the first question in one page; per-framework coverage matrix with gap highlighting answers the second across 5 framework pages

### Secondary Persona: **Adopter / Evaluator**

- **Role**: Prospective tachi user evaluating whether tachi's coverage matches their compliance program
- **Goal**: Read the PDF and form a fast gestalt: "Does this toolkit cover the frameworks I care about? Where are the holes?"
- **Pain Point Today**: No coverage story in the PDF — coverage claims live in the BLP-01 strategic-plan memory, which adopters do not see
- **Value Delivered**: The coverage attestation section turns tachi's ongoing BLP-01 investment into a visible product surface — adopters see the actual coverage of their *specific* engagement, not a marketing claim

### Tertiary Persona: **Maintainer**

- **Role**: tachi maintainer preserving backward compatibility and byte-identity on baselines
- **Goal**: Ship F-B without regressing the 5 non-agentic baselines and without coupling F-B's correctness to F-A3's delivery timeline
- **Pain Point Today**: New report surfaces are high-risk — a PDF template change that renders on every run can break baselines if absent-data handling is subtle
- **Value Delivered**: The `has-source-attribution` boolean gate makes absence first-class — baselines with zero attributions skip the section entirely, byte-identically. The default-value guard in `main.typ` (SC-4a) ensures backward-compat with older `report-data.typ` files regenerated against stale data snapshots.

---

## 📖 User Stories

All three user stories are preserved from GitHub Issue #194 (which sourced them from BLP-01 §7, F-B). Job-story restructuring applied; acceptance criteria preserved verbatim where they provide specific testable predicates. Out-of-Scope treatment removed from AC per Q6-D resolution (architect-owned decision).

### US-194-1: Per-Finding Attribution Table

**When** a security reviewer opens the PDF and wants to audit which OWASP / MITRE / NIST / CWE items a specific finding cites,
**I want to** see one table row per finding with the citations inlined by taxonomy column,
**So I can** audit a single finding's coverage citations without opening `threats.md` or cross-referencing separate taxonomy files.

**Acceptance Criteria**:
- **Given** a fixture with findings that carry populated `source_attribution`, **when** the Typst template renders, **then** the per-finding table contains columns `Finding ID | Title | Severity | OWASP refs | MITRE refs | NIST refs | CWE refs`. The MITRE column groups ATT&CK and ATLAS together with a per-ref prefix (e.g., `ATT&CK:T1070.001` vs `ATLAS:AML.T0051`) so readers can disambiguate.
- **Given** a finding with `source_attribution: [{taxonomy: owasp, id: LLM05, relationship: primary}, {taxonomy: cwe, id: CWE-1426, relationship: related}]`, **when** its row renders, **then** the OWASP cell reads `LLM05` in bold and the CWE cell reads `CWE-1426` plain.
- **Given** a finding with no `source_attribution` array OR an empty array, **when** its row renders, **then** all four ref cells are blank — the row itself still renders (absence is visible, not hidden).
- **Given** the full finding set for the current threat model, **when** `has-source-attribution` is `false` OR the per-finding row count is zero, **then** this table is NOT rendered — the entire coverage-attestation section is omitted (SC-4b).
- **Given** the rendered table on a 7-column portrait US Letter page, **when** the fixture contains 100+ findings, **then** the table paginates acceptably (Q3-A single paginated table with Typst native row-break). Landscape-orientation fallback is pre-approved by architect IF portrait fails the Day 3 pagination smoke test (R8 mitigation).

**Priority**: P0
**Effort**: M

### US-194-2: Aggregate Per-Framework Coverage Matrix

**When** an adopter wants to answer "what fraction of OWASP LLM Top 10 does this engagement cover, and which items are the gaps?",
**I want to** see one page per framework with the framework's items labeled Covered / Partial / Gap, plus a coverage percentage and Partial count alongside,
**So I can** form a one-glance coverage gestalt directly from the PDF without a spreadsheet.

**Acceptance Criteria**:
- **Given** the full finding set, **when** the aggregate matrix renders, **then** there is one page per framework from the 5-value taxonomy enum: OWASP, MITRE ATT&CK, MITRE ATLAS, NIST AI RMF, CWE. All 5 framework pages render when `has-source-attribution: true` (Q4 resolution — adopter asks "what's my coverage of OWASP?"; a page even when the answer is "0% — all items are Gaps" is the correct answer).
- **Given** a framework YAML with N items, **when** the coverage percentage renders, **then** it equals `(items with ≥1 primary attribution across the full finding set) / N` — where N is the authoritative top-level record count from the F-A1 framework YAML (e.g., `len(yaml.safe_load(schemas/taxonomy/owasp.yaml))`), computed once at data-extraction time, traced to a pinned field in the extracted data contract.
- **Given** a framework item with `relationship: primary` attribution on ≥1 finding, **when** it renders, **then** it is classified **Covered** and styled accordingly.
- **Given** a framework item with `relationship: related` or `relationship: derived` attributions but zero `primary`, **when** it renders, **then** it is classified **Partial** (Q1-A resolution — preserves ADR-028 3-value enum signal density) and styled distinctly from Covered.
- **Given** a framework item with zero attributions across the full finding set, **when** it renders, **then** it is classified **Gap** and visually highlighted with color + icon (Q5 resolution, ux-ui-designer memo Day 2 AM — color-blind accessible per WCAG AA; color alone insufficient).
- **Given** the rendered per-framework page, **when** it shows the coverage percentage, **then** it also shows the Partial count with equal visual weight (e.g., "Covered: 12/38 = 31.6% · Partial: 3 · Gap: 23" — MED-3 / R9 resolution). Partial is NOT blended into the coverage percentage (FR-5 preserves primary-only numerator).

**Priority**: P0
**Effort**: L

### US-194-3: Conditional Inclusion Preserves Backward Compatibility

**When** the pipeline runs on any of the 5 existing non-agentic example baselines (or on any freshly-run architecture whose findings carry no `source_attribution`),
**I want to** get back the same PDF I got before F-B — byte-identical under `SOURCE_DATE_EPOCH=1700000000`,
**So I can** be certain F-B is truly additive-when-absent and the `has-source-attribution` gate correctly suppresses the section.

**Acceptance Criteria**:
- **Given** a threats.md file where no finding carries a non-empty `source_attribution` array, **when** `extract-report-data.py` runs, **then** it emits `has-source-attribution: false` in the Typst data contract.
- **Given** a threats.md file where ≥1 finding carries a non-empty `source_attribution` array, **when** `extract-report-data.py` runs, **then** it emits `has-source-attribution: true` and emits the aggregator output (per-finding records + per-framework aggregates) in the Typst data contract.
- **Given** a `report-data.typ` regenerated against stale data that does NOT declare `has-source-attribution`, **when** `main.typ` renders, **then** the default-value guard `#let has-source-attribution = if has-source-attribution != none { has-source-attribution } else { false }` (SC-4a) forces the variable to `false` and the coverage-attestation section is omitted — no Typst "variable not found" compilation error.
- **Given** `has-source-attribution: false`, **when** `main.typ` renders, **then** the coverage-attestation section is entirely omitted — no blank page, no section header, no empty table shell.
- **Given** the 5 existing non-agentic example PDF baselines, **when** the pipeline re-runs under `SOURCE_DATE_EPOCH=1700000000`, **then** all 5 regenerated PDFs are byte-identical to their committed baselines (SC-2 regression).
- **Given** the 6th example (`agentic-app`), **when** the pipeline re-runs, **then** per Feature 128 convention, the baseline may regenerate byte-identically or may be re-baselined if and only if F-A3 has also landed and populated `agentic-app` findings with `source_attribution` — out of scope for F-B; tracked as a follow-on.

**Priority**: P0
**Effort**: S

---

## ⚙️ Functional Requirements

### FR-1 — New Typst Page Template `coverage-attestation.typ`

- New file `templates/tachi/security-report/coverage-attestation.typ`.
- Exposes one top-level function accepting the aggregator output (see FR-2) and rendering the two-view section: per-finding table page(s) followed by per-framework matrix page(s).
- Uses existing `templates/tachi/security-report/` styling conventions (severity colors, Typst table, page layout, branded headers/footers).
- Table row overflow across pages is handled by Typst's native table row-break mechanics — single paginated table (Q3-A); per-severity grouped fallback available if smoke-test pagination is unacceptable. Landscape-orientation fallback pre-approved for the per-finding table IF portrait fails (R8 mitigation; shadow of attack-path landscape precedent).
- Per-framework page MUST render Covered count + coverage percentage + Partial count + Gap count with equal visual weight (e.g., "Covered: 12/38 = 31.6% · Partial: 3 · Gap: 23") — MED-3 / R9 resolution.

### FR-2 — New Aggregator Function in `scripts/extract-report-data.py`

- New function consuming the parsed finding list from `parse_threats_findings` and emitting a structured aggregate consumed by `coverage-attestation.typ`. Name is implementation-owned; signature conforms to the extracted-data contract style used by the existing `has-attack-chains` (line 1426) / `has-maestro-data` (line 1362) aggregators.
- Per-finding records: one record per finding containing `{id, title, severity, owasp_refs, mitre_refs, nist_refs, cwe_refs}` where each `*_refs` is an array of `{id, relationship}` items (rendering decides bold vs. plain via `relationship`). The MITRE column groups ATT&CK and ATLAS together; per-ref prefix disambiguates.
- Per-framework aggregates: one record per framework containing `{framework, yaml_record_count, covered_count, partial_count, gap_count, coverage_percentage}`. Partial count is exposed to the Typst template per MED-3.
- **Denominator authority** (Q2-A trivial resolution): for each framework, `yaml_record_count` is computed once by counting top-level records in `schemas/taxonomy/{framework}.yaml` — the F-A1 authoritative source. All 5 taxonomy YAMLs are modestly scaled (OWASP 60, MITRE ATT&CK 38, MITRE ATLAS 12, NIST AI RMF 72, CWE 53; total 235 items) — F-A1 already curated representative subsets per its FR-003 spec. No schema extension required; no Q2-B `coverage_scope` field; no Q2-C dynamic denominator.
- Caching scoped to a single extraction run (per-invocation dict, no module-level state, per the F-A2 parser convention).
- Graceful edges: zero-item framework YAML → coverage undefined, render as `N/A`; zero-finding match → coverage 0.00%; malformed YAML → aggregator fails loud per ADR-022 fail-loud pattern (bubbles a clear error up through `extract-report-data.py`).

### FR-3 — New Conditional Boolean `has-source-attribution` in Typst Data Contract

- `extract-report-data.py` emits `#let has-source-attribution = true|false` in the generated Typst data file.
- Value is `true` iff ≥1 finding in the current threat model carries a non-empty `source_attribution` array.
- Default on absence: `false` (matches the `has-attack-chains` precedent).

### FR-4 — Conditional Inclusion in `main.typ` (Three Coordinated Edits)

`templates/tachi/security-report/main.typ` gains three coordinated additions:

1. **Default-value guard** (HIGH-1): in the §2b defaults block (around lines 89-107, mirroring the 6 existing default guards for `has-maestro-data`, `has-attack-trees`, `has-attack-chains`, etc.), add:
   ```typst
   #let has-source-attribution = if has-source-attribution != none { has-source-attribution } else { false }
   ```
   Guards backward-compat with older `report-data.typ` files that do not declare the variable — prevents "variable not found" Typst compilation errors when adopters regenerate the PDF from a stale data snapshot.

2. **Import statement** (MED-5): a new `#import "coverage-attestation.typ": coverage-attestation-page` declaration at the top of `main.typ`. Day 3 smoke test verifies that adding the `#import` is byte-identical on the 5 baselines under `SOURCE_DATE_EPOCH=1700000000` (existing precedent: the unconditional `#import "attack-chain.typ"` at `main.typ:47` produces byte-identical baselines today).

3. **Conditional inclusion block** (HIGH-2): placed after the MAESTRO-findings block (line 348) and before the compensating-controls block (line 398) — Q7 placement verified. Block shape follows Feature 141 precedent verbatim:
   ```typst
   #if has-source-attribution and per-finding-rows.len() > 0 {
     coverage-attestation-page(per-finding-rows: per-finding-rows, per-framework-aggregates: per-framework-aggregates)
   }
   ```
   The `.len() > 0` belt-and-suspenders check mirrors `main.typ:246` (`has-attack-chains and attack-chains.len() > 0`) per Feature 141 precedent.

Zero output when `has-source-attribution` is `false` OR when the per-finding row count is zero — no divider, no section header, no blank page.

### FR-5 — Coverage Classification Rules (3-Value MVP per Q6-D)

- **Covered**: framework item with ≥1 finding carrying `source_attribution` where `{taxonomy, id}` match the item AND `relationship: primary`.
- **Partial**: framework item with ≥1 finding carrying `source_attribution` where `{taxonomy, id}` match the item AND `relationship ∈ {related, derived}` — AND zero findings carrying `primary` (Q1-A resolution — preserves ADR-028 3-value enum signal density).
- **Gap**: framework item with zero findings carrying any `source_attribution` matching the item.
- **Out-of-Scope is NOT an MVP classification** (Q6-D resolution). All non-cited items classify as Gap. Out-of-Scope treatment deferred to a follow-on feature once adopter demand is visible.
- Coverage percentage uses **Covered** in the numerator (primary-only, not Partial). Rationale: Partial is signaled separately as a second-tier classification alongside the percentage (MED-3); blending Partial into coverage percentage hides the distinction.

### FR-6 — Test Coverage

- Unit tests for the aggregator function in `tests/scripts/`:
  - 3 finding-set fixtures: (a) empty (no `source_attribution` anywhere), (b) one finding carries one `primary`, (c) multi-finding with mixed `primary`/`related`/`derived` across ≥2 frameworks.
  - Assertions: `has-source-attribution` boolean correctness, per-framework `covered_count`/`partial_count`/`gap_count` counts, `coverage_percentage` arithmetic (including zero-denominator N/A edge and zero-numerator 0.00% edge).
- Integration test: SC-2 byte-identity check against the 5 non-agentic example baselines runs green under `SOURCE_DATE_EPOCH=1700000000`. This SC-2 test directly exercises the `#import` byte-identity claim (MED-5).
- Typst compile test: a minimal fixture that exercises the template renders without compile errors. Day 3 pagination smoke test on a synthetic 100-finding × 5-framework fixture validates R1/R8 assumptions.

### FR-7 — Per-Feature ADR (ADR-029)

A public `docs/architecture/02_ADRs/ADR-029-coverage-attestation-report-section.md` is committed per Feature 180/189 precedent: **Proposed at Day 1 Wave 1** (unblocks parallel Typst + aggregator work), **Accepted at Day 4** with a provisional merge-date, **SHA fill** at post-merge.

ADR body MUST document:
1. The new Typst template + aggregator-function + `has-source-attribution` boolean pattern, cross-referencing Feature 141 `has-attack-chains` as the architectural precedent and the default-value-guard + `.len() > 0` belt-and-suspenders check.
2. The 3-value coverage classification for MVP (Covered / Partial / Gap) with the Q1-A rule (Partial = `related`/`derived`-only, zero `primary`).
3. The denominator-authority convention (Q2-A): each framework's denominator is `len(yaml.safe_load(schemas/taxonomy/{framework}.yaml))`. All 5 taxonomies are modestly scaled; F-A1 already curated representative subsets. No schema extension required; Q2-B (`coverage_scope` field) and Q2-C (dynamic denominator) explicitly rejected.
4. The zero-crosswalk-JOIN scope line — F-B matrix is intra-framework only; `schemas/taxonomy/crosswalk.yaml` is NOT consulted.
5. The Out-of-Scope deferral (Q6-D): 3-value MVP classification; all non-cited items are Gap; Out-of-Scope treatment deferred to a follow-on feature. Q6-A/B/C (schema extension, sidecar, inline Section 10) explicitly considered and rejected on scope-expansion grounds.
6. The zero-edit invariant on the 22-file F-A2 scope (11 threat-detection agents + 11 skill-reference files), preserving ADR-023 + ADR-028 lineage.
7. R9 / MED-3 disclosure rule: Partial count rendered alongside coverage percentage on every per-framework page.

### FR-8 — Zero-Edit Invariant on 22-File F-A2 Scope

Preserved per ADR-023 and extended by ADR-028:
- **11 agent files**: No file under `.claude/agents/tachi/stride/*.md` (6) or `.claude/agents/tachi/ai/*.md` (5) is modified in the F-B PR.
- **11 skill-reference files**: No file under `.claude/skills/tachi-{agent-name}/references/detection-patterns.md` is modified.

F-B reads whatever `source_attribution` findings carry. Populator wiring remains F-A3 scope. Keeping F-B additive-read-only on the detection tier preserves the Feature 082 / F-A2 zero-edit invariant. Architect verified: F-B's 5 touch points (new aggregator, new `coverage-attestation.typ`, 3 edits to `main.typ`, new tests, no schema changes) are all outside the 22-file scope.

---

## 🚀 Non-Functional Requirements

### Performance

- Aggregator function runtime on a threat model with 100 findings × 5 attributions each MUST complete in <1s on commodity hardware (informational floor — not CI-enforced).
- Typst compile time of `coverage-attestation.typ` on a 100-finding × 5-framework fixture MUST NOT add more than 2s to the PDF render — falls within the existing `tachi.security-report` budget. Architect estimate: 235 items × ~50 bytes/row is ~12KB table data; Typst renders this in <200ms on commodity hardware (R6).

### Reliability

- SC-2 (5 non-agentic baselines byte-identical) is a BLOCKER if regressed.
- The 6th example (`agentic-app`) follows the Feature 128 convention — may regenerate byte-identically or may be re-baselined if F-A3 has also landed; tracked as a follow-on.
- Graceful absence: findings without `source_attribution` cause the aggregator to emit `has-source-attribution: false` and zero aggregate records — no error.

### Security

- No security-relevant data introduced. The coverage-attestation section cites *public* framework IDs; no secrets, credentials, or PII.
- Gap highlighting MUST NOT leak engagement-internal detail. Gaps are rendered as taxonomy labels only; rationale is absent in MVP (Q6-D — Out-of-Scope rationale surface deferred).

### Accessibility (surfaced by Q5 / architect LOW-3)

- Gap vs. Partial vs. Covered distinctions MUST be color-blind accessible per WCAG AA — color alone is insufficient. Q5 ux-ui-designer memo (Day 2 AM) specifies color + icon combinations (architect recommendation: Covered = green check, Partial = yellow half-circle, Gap = red X with red fill).

### Compatibility

- Python stdlib + existing declared deps only. `pyyaml` and `pytest` already declared (Feature 128 precedent).
- No npm / Node.js dependency additions.
- Typst language version: whatever the current `tachi.security-report` pipeline uses; no new Typst version requirement.

---

## 📊 Success Metrics

### Primary (Leading)

- **Metric 1 — Template compile gate**: `coverage-attestation.typ` compiles on a populated fixture without errors.
- **Metric 2 — Backward-compat gate**: SC-2 byte-identity regression test green across 5 baselines (includes the default-value guard + `#import` byte-identity validation).
- **Metric 3 — Aggregator correctness gate**: per-framework classification counts and coverage percentage match a manually-verified fixture computation.
- **Metric 4 — Conditional-inclusion gate**: `has-source-attribution: false` produces zero template output; `main.typ` renders no section header, no blank page.
- **Metric 5 — ADR gate**: public per-feature ADR-029 committed with Proposed → Accepted dual-commit pattern.

### Secondary (Lagging — Measured Post-Delivery)

- **Metric 6 — Adopter resolution path**: a security reviewer can answer "what fraction of OWASP LLM Top 10 does this engagement cover?" from the PDF alone, without opening `threats.md` or `schemas/taxonomy/*.yaml`.
- **Metric 7 — F-A3 enablement**: when F-A3 ships populators, the existing F-B rendering produces coverage content immediately on the first run against a populated architecture, with no further template work required.

---

## 🔍 Scope & Boundaries

### In Scope (MVP)

**Must Have (P0)**:
- ✅ New `coverage-attestation.typ` Typst page template with per-finding table + per-framework matrix views (5 framework pages).
- ✅ New aggregator function in `extract-report-data.py` emitting per-finding records, per-framework aggregates (including Partial count per MED-3), and `has-source-attribution` boolean.
- ✅ Three coordinated `main.typ` edits: default-value guard (HIGH-1), `#import` statement (MED-5), conditional `#if has-source-attribution and per-finding-rows.len() > 0` inclusion block (HIGH-2) placed after MAESTRO-findings and before compensating-controls.
- ✅ 3-value coverage classification (Covered / Partial / Gap) with `primary`-only numerator for coverage percentage; Partial count surfaced separately.
- ✅ Unit tests (aggregator) + integration test (SC-2 byte-identity) + Typst compile smoke test (including Day 3 pagination smoke on 100-finding fixture).
- ✅ Public per-feature ADR-029.

### Out of Scope (Deferred)

**Could Have (P2) — Deferred to Follow-On Features**:
- 🔮 **Out-of-Scope 4th classification** (Q6-D). Deferred to a follow-on feature once adopter demand is visible. Q6-A (YAML field extension), Q6-B (sidecar), Q6-C (inline Section 10) were considered and rejected on scope-expansion grounds — each option would require its own ADR rationale and schema/surface extension.
- 🔮 **Cross-framework JOIN via crosswalk.yaml** — answering "OWASP LLM05 and MITRE ATLAS AML.T0051 both cite this finding via the F-A1 crosswalk; composite coverage is X%". Deferred because intra-framework coverage is the correct first deliverable, and the crosswalk JOIN adds a materially different design question (how to avoid double-counting when the same finding covers crosswalked items on two frameworks).
- 🔮 **Interactive coverage export** (CSV, JSON) — a machine-readable form of the aggregator output for downstream tools. The aggregator itself emits structured data to the Typst contract; exporting it as a separate artifact is a follow-on.
- 🔮 **Time-series coverage delta** (coverage change between baseline and current run) — Feature 104 baseline-delta pattern applied to coverage. Deferred because F-A3 populator wiring must settle before baseline-delta on attribution is meaningful.
- 🔮 **Per-finding coverage infographic template** — a Feature 128-style infographic rendering the coverage matrix visually. F-B ships the PDF section; the infographic variant is a follow-on.

**Won't Have — Explicitly Excluded**:
- ❌ **Editing or enriching `source_attribution` during F-B** — F-B is read-only over the finding list. All population logic is F-A3.
- ❌ **Tachi-internal taxonomy matrix pages** — `tachi-control-category` and `tachi-stride-ai-category` (the 2 internal taxonomies of F-A1's 7-value catalog) are NOT rendered. They are internal vocabulary; adopters do not claim coverage against them. Same scope line as F-A2's 5-value external-framework enum.
- ❌ **Breaking schema changes** — `schemas/finding.yaml` is NOT modified; `schemas/taxonomy/*.yaml` is NOT modified. F-B is purely a renderer + aggregator.
- ❌ **Threat-agent populator wiring** — F-A3 scope; explicitly preserved by the SC-9 zero-edit invariant on the 22-file scope.
- ❌ **SARIF `source_attribution` propagation** — the SARIF exporter continues to treat `source_attribution` as it does post-F-A2 (absent from SARIF output). SARIF propagation is a separate follow-on.
- ❌ **F-A1 YAML `coverage_scope` field extension (Q2-B)** — rejected on scope-expansion and "no real problem to solve" grounds (architect: all 5 taxonomies are modestly scaled; no need for curated-subset machinery).

### Assumptions

- **A1**: F-A1 (Feature 180) and F-A2 (Feature 189) are committed to main (verified 2026-04-17 via `git log` — squash commits `8b7c7bf` and `6d5d890`).
- **A2**: `has-source-attribution: false` on every baseline pre-F-A3 — no finding across any committed example carries a populated `source_attribution` array. This is the default for every fresh pipeline run until F-A3 ships populators.
- **A3**: `parse_threats_findings` round-trips `source_attribution` correctly on findings that carry it (per F-A2 FR-2); F-B trusts the parsed finding list as-is. Architect verified: `scripts/tachi_parsers.py:796` stores `source_attribution` records on the finding dict when present.
- **A4**: Feature 141 `has-attack-chains` + Feature 128 new-Typst-page patterns are the right architectural precedents to mirror; no novel template-architecture pattern introduced. Architect verified.
- **A5**: All 5 taxonomy YAMLs are modestly scaled (OWASP 60, MITRE ATT&CK 38, MITRE ATLAS 12, NIST AI RMF 72, CWE 53). F-A1 already curated representative subsets; no "large denominator" problem exists. (Architect correction of PRD v1.0 R2 factual error.)

### Constraints

- **Technical**: Python stdlib + existing declared deps only; no new npm/Node deps; no new Typst-version requirement.
- **Backward-compat**: SC-2 (5 baselines byte-identical) is a BLOCKER. The default-value guard (SC-4a) is the backward-compat insurance against stale `report-data.typ` files.
- **Governance**: public per-feature ADR-029 on merge, Proposed → Accepted dual-commit pattern (Feature 180/189 precedent).
- **Scope discipline**: SC-9 zero-edit invariant on 22-file F-A2 scope is a BLOCKER.

---

## 🛣️ Timeline & Milestones

### Phase Breakdown

**Day 1 (2026-04-20 Monday) — Design Lock + Wave 1.1 Parallel Scaffolding**

*Wave 1.0 (architect, critical path)*:
- Q5 ux-ui-designer memo specification published (color + icon spec for Covered/Partial/Gap — due Day 2 AM, architect coordinates the handoff).
- ADR-029 Proposed commit (architect). Body documents Q1-A / Q2-A / Q6-D resolutions verbatim.

*Wave 1.1 (parallel, Q-independent per M-3 resolution)*:
- Aggregator test-fixture authoring (tester) — fixture shapes (empty, one-primary, multi-mixed) are classification-rule-independent.
- Typst template skeleton (senior-backend-engineer) — page scaffolding, header, footer, section title, empty table shell — Q1/Q2/Q5-independent structural work.
- `has-source-attribution` boolean emission wiring scaffolded in `extract-report-data.py` — Q-independent (only depends on F-A2's `source_attribution` array presence).

**Day 2 (2026-04-21 Tuesday) — Aggregator Implementation + Q5 Landing**

- Q5 ux-ui-designer memo lands Day 2 AM (color + icon spec for Covered/Partial/Gap; WCAG AA color-blind accessible).
- `extract-report-data.py` aggregator function completed (senior-backend-engineer) per Q1-A / Q2-A resolutions — per-finding records + per-framework aggregates with `covered_count`/`partial_count`/`gap_count`/`coverage_percentage`.
- Aggregator unit tests green (tester + senior-backend-engineer).
- **Team-lead Day 2 EOD coordination check (M-2)**: verify F-A3 has not been filed as an Issue during Days 1-2. If filed, escalate to serialization decision (hold F-B PR for F-A3 merge, OR advance F-B and accept F-A3 re-baseline cost).

**Day 3 (2026-04-22 Wednesday) — Typst Template Finalization + Integration**

- `coverage-attestation.typ` template completed on populated fixture (per-finding table, 5 per-framework matrix pages, gap highlighting, Partial disclosure alongside coverage percentage).
- `main.typ` three coordinated edits: default-value guard, `#import`, conditional inclusion block.
- Typst compile-smoke test green on 100-finding × 5-framework fixture (R1/R8 pagination smoke).
- Day 3 unused-`#import` byte-identity smoke on 5 baselines (MED-5 — verifies adding `#import "coverage-attestation.typ"` to `main.typ` when gate is false is byte-identical).

**Day 4 (2026-04-23 Thursday) — Backward-Compat + ADR Accepted**

- SC-2 byte-identity regression green across 5 baselines (tester primary, senior-backend-engineer secondary for failure diagnostics).
- ADR-029 transitioned Proposed → Accepted (architect).
- Quality checklist pass, PR submitted.

### Key Milestones

| Milestone | Target Date | Owner | Status |
|-----------|-------------|-------|--------|
| PRD Approval | 2026-04-18 (Sat) | product-manager | ✅ In Review |
| **Wave 1.0** — ADR-029 Proposed + Q1-A/Q2-A/Q6-D recorded | 2026-04-20 (Mon, Day 1 AM) | architect | 📋 Pending |
| **Wave 1.1** — Fixture authoring begins (parallel) | 2026-04-20 (Mon, Day 1 AM) | tester | 📋 Pending |
| **Wave 1.1** — Typst template skeleton (parallel) | 2026-04-20 (Mon, Day 1) | senior-backend-engineer | 📋 Pending |
| Q5 Visual Treatment Memo | 2026-04-21 (Tue, Day 2 AM) | ux-ui-designer | 📋 Pending |
| Aggregator + Unit Tests Complete | 2026-04-21 (Tue, Day 2) | senior-backend-engineer | 📋 Pending |
| F-A3 Merge-Order Coordination Check | 2026-04-21 (Tue, Day 2 EOD) | team-lead | 📋 Pending |
| Typst Template + `main.typ` 3 Edits | 2026-04-22 (Wed, Day 3) | senior-backend-engineer | 📋 Pending |
| Day 3 Pagination + `#import` Byte-Identity Smoke | 2026-04-22 (Wed, Day 3 PM) | senior-backend-engineer | 📋 Pending |
| SC-2 Regression Green (5 baselines) | 2026-04-23 (Thu, Day 4 AM) | **tester** (primary), senior-backend-engineer (secondary) | 📋 Pending |
| ADR-029 Accepted + PR Merged | 2026-04-23 (Thu, Day 4 PM) | architect | 📋 Pending |

---

## ⚠️ Risks & Dependencies

### Technical Risks

**Risk R1 — Typst table pagination regresses or looks ugly on real-world finding counts (50-200 rows)**
- **Likelihood**: Low (architect-resized from Medium — existing findings-detail handles comparable row counts).
- **Impact**: Low (delivery delay, not blocker — Typst native table break usually works acceptably).
- **Mitigation**: Day 3 Typst compile smoke test on a synthetic 100-finding fixture validates pagination quality.
- **Contingency**: Per-severity split (Critical/High page 1, Medium page 2, Low page 3) available as fallback. Landscape-orientation also pre-approved for the per-finding table per R8.

**Risk R2 — ELIMINATED.** The PRD v1.0 claim that MITRE ATT&CK is "enterprise-scale matrix (~600 techniques)" was factually incorrect. `schemas/taxonomy/mitre-attack.yaml` is 38 records — F-A1 already curated a subset at spec-time per its FR-003 / A1 seed list. All 5 taxonomy YAMLs are modestly scaled (OWASP 60, ATT&CK 38, ATLAS 12, NIST AI RMF 72, CWE 53). Q2-A (trivial full YAML record count) is the correct denominator. No schema extension required. No R2-contingency scope absorbed. (Architect HIGH-3 finding; corrected in v1.1.)

**Risk R3 — F-A3 populators ship before F-B merges, changing the baseline finding set**
- **Likelihood**: Low (F-A3 not yet filed as an Issue; 9 BLP-01 features remaining as of 2026-04-18).
- **Impact**: Medium (architect-resized from High — re-baseline is ADR-021-mechanical, not a design rework). F-B baseline assumptions inverted — all baselines would have populated attributions, triggering the coverage-attestation section on every baseline run. SC-2 becomes "baselines regenerate with the coverage-attestation section included, byte-identically against new F-A3-era baselines".
- **Mitigation**: The `has-source-attribution` gate is the correct architecture for this scenario. **Team-lead Day 2 EOD coordination check (M-2)** confirms F-A3 has not been filed as an Issue during Days 1-2. If filed, escalate to serialization decision.
- **Contingency**: Explicit coordination with F-A3 author — whoever merges second re-baselines (~0.5-1d cost absorbed by the second merger).

**Risk R4 — Coverage percentage arithmetic edges (zero items in framework YAML, zero findings, framework YAML is malformed)**
- **Likelihood**: Low
- **Impact**: Low
- **Mitigation**: Aggregator MUST handle the three edges gracefully: (a) zero items in YAML → coverage undefined, render as `N/A` with a note, (b) zero findings matching any item → coverage 0.00%, (c) malformed YAML → aggregator fails loud per ADR-022 fail-loud pattern (bubbles a clear error up through `extract-report-data.py`).

**Risk R5 — F-B ships before F-A3; adopters see an empty coverage-attestation section on their first run and misread it as "tachi has zero coverage"**
- **Likelihood**: Certain by design (the gate omits the section; no empty section renders)
- **Impact**: Low — the gate hides the section when absent, so adopters see no new output until F-A3 populates findings. The risk is dormant until F-A3 ships.
- **Mitigation**: The ADR explicitly frames F-B as the renderer + aggregator; the F-A3 PRD (when written) will document the expected UX of the first populated run. No adopter confusion possible on F-B MVP pre-F-A3.
- **Contingency**: None needed. The architecture prevents the failure mode.

### New Risks (architect-surfaced)

**Risk R6 (NEW) — Typst compile time on fixture with N=235 items × 5 pages**
- **Likelihood**: Low. **Impact**: Low. 235 items × ~50 bytes/row is ~12KB table data; Typst renders this in <200ms on commodity hardware. NFR 2s budget is ample. No mitigation required beyond Day 3 smoke test.

**Risk R7 (NEW) — Aggregator complexity for hierarchical MITRE records (Tactics + Techniques + Sub-techniques)**
- **Likelihood**: Medium. **Impact**: Low. MITRE ATT&CK YAML records are flat (38 top-level keys, no nested Tactic→Technique hierarchy). Each record has an `id` like `T1070.001` where the dotted component is string-only, not structural. The aggregator treats each ID as an opaque string matching `finding.source_attribution[i].id` one-to-one. **No hierarchical-traversal complexity.** Parent techniques and sub-techniques are listed as independent top-level records in the F-A1 YAML.

**Risk R8 (NEW) — Font/table-width issues on the per-finding table (7 columns)**
- **Likelihood**: Medium. **Impact**: Low. 7 columns (Finding ID | Title | Severity | OWASP refs | MITRE refs | NIST refs | CWE refs) is wider than the existing findings-detail table (5 columns). In portrait US Letter this may require reduced font size or column-prioritization (truncate Title, wrap refs).
- **Mitigation**: Day 1 Typst skeleton includes a paginated-table smoke test per FR-1 — same smoke test catches font-width issues.
- **Contingency**: Landscape-orientation fallback pre-approved for the per-finding table IFF portrait is unacceptable (shadowing attack-path landscape precedent).

**Risk R9 (NEW) — Partial in coverage percentage: rendering disclosure**
- **Likelihood**: Certain. **Impact**: Low. FR-5 correctly excludes Partial from the coverage percentage numerator. BUT adopters reading "34% coverage" may expect Partial items to count fractionally.
- **Mitigation (MED-3)**: the per-framework page MUST render the Partial count separately alongside the coverage percentage (e.g., "Covered: 12/38 = 31.6% · Partial: 3 · Gap: 23"). FR-1 and FR-2 enforce; Q5 visual treatment ensures the Partial count has equal visual weight.

### Dependencies

**Internal**:
- **F-A1 (Feature 180) — schemas/taxonomy/**: **SATISFIED** as of 2026-04-17 (team-lead verified: 7 YAMLs + crosswalk.yaml + README.md all present).
- **F-A2 (Feature 189) — `source_attribution` field + parser round-trip**: **SATISFIED** as of 2026-04-17 (architect verified: `schemas/finding.yaml:212` + `scripts/tachi_parsers.py:796`).
- **ADR-021** (byte-determinism): SATISFIED — SC-2 gate uses the harness.
- **ADR-028** (F-A2 schema contract): SATISFIED — provides the referential-integrity and enum-closure contracts F-B trusts.
- **Feature 141 precedent** (`has-attack-chains` pattern): SATISFIED — architectural template (verified at `extract-report-data.py:1426` + `main.typ:246`).
- **Feature 128 precedent** (new-Typst-page + extract-report-data.py boolean): SATISFIED — architectural template.

**External**: None. F-B introduces no runtime dependencies.

---

## ❓ Open Questions

### Technical Questions (Pre-Resolved Per Architect Review)

- [x] **Q1 — Partial classification rule.** **Resolved Q1-A** (architect): Partial = `related`/`derived`-only, zero `primary`. Rationale: preserves ADR-028 3-value `relationship` enum's full expressive power in the coverage matrix. Q1-B (merging related/derived into Partial) discards the primary/related/derived distinction at the coverage-matrix surface. Q1-C (Partial = derived-only) arbitrarily promotes `related` to Covered, contradicting ADR-028 Decision 4. Owner: architect — Status: **Resolved** 2026-04-18.

- [x] **Q2 — Denominator authority.** **Resolved Q2-A** (architect): full `len(yaml.safe_load(schemas/taxonomy/{framework}.yaml))` record count. All 5 taxonomy YAMLs are modestly scaled (235 items total); F-A1 already curated representative subsets. Q2-B (`coverage_scope` field extension) rejected — premature abstraction, no real problem to solve. Q2-C (dynamic denominator) rejected — violates ADR-021 determinism. **This resolution corrects PRD v1.0 R2 factual error** (architect HIGH-3). Owner: architect — Status: **Resolved** 2026-04-18.

- [x] **Q3 — Per-severity pagination of the per-finding table.** **Resolved Q3-A** (architect): single paginated mega-table with Typst row-break; per-severity split available as fallback only if Day 3 smoke-test shows poor pagination. Rationale: Typst native table pagination works acceptably up to ~200 rows at standard font sizes. Owner: architect — Status: **Resolved** 2026-04-18.

- [x] **Q4 — Empty-framework page suppression.** **Resolved render-all-5** (architect): always render all 5 framework pages when `has-source-attribution: true`. Rationale: "0% coverage, all Gaps" is the correct answer when an engagement doesn't cite a framework; suppressing hides meaningful information. Owner: architect — Status: **Resolved** 2026-04-18.

- [ ] **Q5 — Gap and Partial visual treatment.** **Pending ux-ui-designer memo** (Day 2 AM). Architect recommendation: distinct color + icon per classification (WCAG AA color-blind accessible). Covered = green check, Partial = yellow half-circle, Gap = red X with red fill. Owner: ux-ui-designer — Due: 2026-04-21 Day 2 AM — Status: Pending.

- [x] **Q6 — Out-of-Scope source of truth.** **Resolved Q6-D** (architect): omit Out-of-Scope from F-B MVP; all non-cited items classify as Gap. Q6-A (new taxonomy YAML field) rejected — premature F-A1 schema extension for speculative demand. Q6-B (sidecar YAML per engagement) rejected — new engagement-scoped configuration file with no declared lifecycle contract. Q6-C (inline Section 10 YAML in threats.md) rejected — extends the F-A2 serialization surface and would itself require an ADR-028-successor governance decision. FR-5 simplifies to 3-value classification; Out-of-Scope deferred to follow-on once adopter demand is visible. Owner: architect — Status: **Resolved** 2026-04-18.

- [x] **Q7 — `main.typ` placement.** **Resolved** (architect): after MAESTRO-findings block (line 348) and before compensating-controls block (line 398). Rationale: coverage-attestation is a reporting-tier artifact that belongs between detection findings (findings-detail, MAESTRO findings) and mitigation tier (control coverage, remediation roadmap). Owner: architect — Status: **Resolved** 2026-04-18.

- [x] **Q8 — ADR number assignment.** **Resolved ADR-029** (architect mechanical assignment at Proposed commit; no conflict expected). Owner: architect — Status: **Resolved** 2026-04-18.

### Process Questions (Resolved)

- [x] **Q-P1 — Demonstrate populated attribution on `agentic-app` example?** **Resolved NO** (product-manager, adopting Feature 189 precedent verbatim). Sample `source_attribution` records belong in test fixtures under `tests/scripts/fixtures/`, not in example outputs. F-A3 handles population. If adopter confusion surfaces post-merge, track as a follow-on feature. Owner: product-manager — Status: **Resolved** 2026-04-18.

---

## 📚 References

### Product Documentation

- Vision: `docs/product/01_Product_Vision/product-vision.md`
- BLP-01 initiative memory: `/Users/david/.claude/projects/-Users-david-Projects-tachi/memory/project_blp01_threat_coverage.md`
- GitHub Issue: [#194](https://github.com/davidmatousek/tachi/issues/194)

### Precedent PRDs

- Feature 180 (F-A1, delivered 2026-04-17 — taxonomy YAMLs supply F-B denominators): `docs/product/02_PRD/180-taxonomy-crosswalk-collection-2026-04-17.md`
- Feature 189 (F-A2, delivered 2026-04-17 — supplies `source_attribution` contract): `docs/product/02_PRD/189-source-attribution-schema-extension-2026-04-17.md`
- Feature 141 (cross-layer attack chains — direct `has-attack-chains` precedent F-B mirrors)
- Feature 128 (executive architecture infographic — direct new-Typst-page + extract-report-data.py boolean precedent)

### Technical References

- Schema head: `schemas/finding.yaml` (current `schema_version: "1.5"`, `source_attribution` on line 212)
- Parser target: `scripts/tachi_parsers.py::parse_threats_findings` (line 796 stores `source_attribution` records on the finding dict)
- F-A1 framework YAMLs: `schemas/taxonomy/{owasp,mitre-attack,mitre-atlas,nist-ai-rmf,cwe}.yaml` — 235 items total (60+38+12+72+53)
- Aggregator insertion point: `scripts/extract-report-data.py` (existing `has-attack-chains` at line 1426, `has-maestro-data` at line 1362)
- Conditional-inclusion insertion point: `templates/tachi/security-report/main.typ` (default-value guard block lines 89-107; `#if has-attack-chains and attack-chains.len() > 0` at line 246; placement between MAESTRO-findings line 348 and compensating-controls line 398)
- Backward-compat harness: `tests/scripts/test_backward_compatibility.py`

### ADR Lineage

- ADR-021: `SOURCE_DATE_EPOCH` determinism convention (SC-2 gate)
- ADR-022: CLI-prerequisite fail-loud pattern (aggregator malformed-YAML handling per FR-2 graceful edges)
- ADR-023: Skill-references pattern (22-file zero-edit invariant — preserved here)
- ADR-027 (F-A1, Feature 180): Taxonomy crosswalk schema
- ADR-028 (F-A2, Feature 189): Source-attribution schema contract — directly upstream
- ADR-029 (this PRD): To be authored at Day 1 Wave 1.0

---

## ✅ Approval & Sign-Off

### Approval Status

| Role | Name | Status | Date | Comments |
|------|------|--------|------|----------|
| Product Manager | product-manager | ✅ Approved | 2026-04-18 | Q-P1 resolved NO; all 3 user stories preserved verbatim from Issue #194; 9 SCs measurable; 3-value MVP classification per Q6-D. |
| Architect | architect | 🟡 Approved with Concerns | 2026-04-18 | 0 BLOCKING / 3 HIGH / 5 MEDIUM / 4 LOW. HIGH-1/2/3 absorbed inline (default-value guard, `.len() > 0`, R2 factual correction). Q1-A / Q2-A / Q3-A / Q4 / Q6-D / Q7 / Q8 resolved; Q5 awaits ux-ui-designer memo Day 2 AM. R2 eliminated; R3 resized Medium; R6-R9 new risks surfaced. |
| Engineering Lead | team-lead | 🟡 Approved with Concerns | 2026-04-18 | 0 BLOCKING / 1 HIGH / 3 MEDIUM / 2 LOW. Calendar correct; 4 days baseline (3 days aspirational). H-1 neutralized by architect Q2-A trivial resolution. M-1 neutralized by Q6-D. M-2 Day 2 EOD F-A3 merge-order check added. M-3 Wave 1.1 parallel scaffolding promoted to explicit milestones. L-1 Q5 shifted to Day 2 AM. All agent assignments validated ≤80% load. |

---

## 📝 Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-04-18 | product-manager | Initial PRD — 3 user stories sourced from Issue #194; BLP-01 Foundation tier closure framing; `has-source-attribution` boolean gate mirroring Feature 141 `has-attack-chains`; 8 open questions with Q1/Q2/Q6 proposed as Day 1 critical-path architect decisions. |
| 1.1 | 2026-04-18 | product-manager | Post-Triad inline absorption — (a) **R2 factual correction** (architect HIGH-3): MITRE ATT&CK is 38 records, not 600+; F-A1 already curated representative subsets across all 5 taxonomies (235 items total). Q2 collapses to trivial Q2-A full YAML record count. (b) **Q6-D adopted** (architect + team-lead): drop Out-of-Scope from MVP; 3-value classification (Covered/Partial/Gap); Q6-A/B/C rejected on scope-expansion grounds. (c) **HIGH-1**: default-value guard `#let has-source-attribution = if has-source-attribution != none { has-source-attribution } else { false }` added to FR-4 for backward-compat with stale `report-data.typ`. (d) **HIGH-2**: `.len() > 0` belt-and-suspenders check added to FR-4 per Feature 141 precedent. (e) **MED-3 / R9**: Partial count rendered alongside coverage percentage on every per-framework page. (f) **MED-4 / R8**: landscape-orientation fallback pre-approved for per-finding table. (g) **MED-5**: Day 3 `#import` byte-identity smoke test added. (h) **Risk re-sizing**: R1 Medium→Low, R2 eliminated, R3 Impact High→Medium. **Four new risks** R6-R9 (Typst compile perf, MITRE hierarchical records, font/table-width, Partial disclosure) surfaced with mitigations. (i) **Milestones**: Wave 1.1 parallel scaffolding (fixtures + Typst skeleton) promoted to explicit Day 1 milestones per team-lead M-3. (j) **Day 2 EOD F-A3 coordination check** added per team-lead M-2. (k) **Q5 due date** shifted to Day 2 AM per team-lead L-1. (l) **Timeline**: 4 days realistic baseline; 3 days aspirational — contingent on Q1-A + Q2-A + Q6-D happy path. (m) Q1-A, Q2-A, Q3-A, Q4, Q6-D, Q7, Q8, Q-P1 all pre-resolved; Q5 remains open pending Day 2 AM ux-ui-designer memo. |
