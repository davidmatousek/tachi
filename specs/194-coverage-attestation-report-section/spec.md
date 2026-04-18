---
prd_reference: docs/product/02_PRD/194-coverage-attestation-report-section-2026-04-18.md
triad:
  pm_signoff:
    agent: product-manager
    date: 2026-04-18
    status: APPROVED
    notes: "Faithful translation of PRD v1.1. All 8 PRD FRs map to 19 spec FRs (scope-boundary predicates FR-014 through FR-019 hoisted from PRD Won't-Have list into testable form). 3 user stories preserved verbatim with equal P1 priority. 12 SCs cover PRD's 9 plus 3 additive testability predicates. Q5 deferral handled via FR-010 + A6 pre-approved fallback. All resolved PRD questions (Q1-A, Q2-A, Q6-D) preserved — none reopened. 22-file zero-edit invariant, zero-crosswalk-JOIN, zero-schema-change, 3-value MVP classification all explicit. Ready for /aod.project-plan."
  architect_signoff: null  # Added by /aod.project-plan
  techlead_signoff: null   # Added by /aod.tasks
---

# Feature Specification: Coverage Attestation Report Section

**Feature Branch**: `194-coverage-attestation-report-section`
**Created**: 2026-04-18
**Status**: Draft
**Input**: User description: "PRD: 194 - coverage-attestation-report-section"
**PRD**: [docs/product/02_PRD/194-coverage-attestation-report-section-2026-04-18.md](../../docs/product/02_PRD/194-coverage-attestation-report-section-2026-04-18.md)
**BLP-01 Phase**: Coverage Attestation Reporting tier (consumer of F-A1 + F-A2 Foundation tier)

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Per-Finding Attribution Table (Priority: P1)

A security reviewer opens the PDF security report and wants to audit which OWASP / MITRE ATT&CK / MITRE ATLAS / NIST AI RMF / CWE items a specific finding cites. The reviewer sees a single paginated table with one row per finding and per-taxonomy citation columns, so the audit can complete without opening `threats.md` source or cross-referencing separate taxonomy files.

**Why this priority**: This is the primary adopter-visible surface of the F-B feature. Without the per-finding table, F-B delivers no value to the security-reviewer persona — the coverage matrix (Story 2) answers an aggregate question, but day-to-day review work is per-finding.

**Independent Test**: Given a fixture threats.md where findings carry populated `source_attribution` arrays, rendering the PDF produces a per-finding attribution table where every finding has a row, citations render in the correct columns, and `relationship: primary` citations render bold.

**Acceptance Scenarios**:

1. **Given** a fixture with findings carrying populated `source_attribution`, **When** the Typst template renders, **Then** the per-finding table contains columns `Finding ID | Title | Severity | OWASP refs | MITRE refs | NIST refs | CWE refs`, with the MITRE column grouping ATT&CK and ATLAS together using a per-ref prefix (e.g., `ATT&CK:T1070.001` vs `ATLAS:AML.T0051`).
2. **Given** a finding with `source_attribution: [{taxonomy: owasp, id: LLM05, relationship: primary}, {taxonomy: cwe, id: CWE-1426, relationship: related}]`, **When** its row renders, **Then** the OWASP cell reads `LLM05` in bold and the CWE cell reads `CWE-1426` plain, visually distinguishing `primary` from `related`/`derived`.
3. **Given** a finding with no `source_attribution` array OR an empty array, **When** its row renders, **Then** all four ref cells are blank and the row itself still renders (absence is visible, not hidden).
4. **Given** a fixture containing 100+ findings, **When** the per-finding table renders on portrait US Letter, **Then** the table paginates acceptably using Typst native row-break (single paginated table, not per-severity split).
5. **Given** the rendered PDF, **When** a color-blind reader inspects the `primary` vs `related`/`derived` visual distinction, **Then** the distinction is discernible without relying on color alone (e.g., bold vs. plain weight).

---

### User Story 2 - Aggregate Per-Framework Coverage Matrix (Priority: P1)

An adopter or evaluator wants to answer "what fraction of OWASP LLM Top 10 does this engagement cover, and which items are the gaps?" from the PDF alone. The adopter sees one page per framework (OWASP, MITRE ATT&CK, MITRE ATLAS, NIST AI RMF, CWE) with every item in the framework classified as Covered / Partial / Gap, a coverage percentage, and the Partial count surfaced alongside so the classification is visible at a glance.

**Why this priority**: This is the aggregate-view answer to the coverage question. Without it, adopters cannot form the "does this toolkit cover my frameworks?" gestalt the BLP-01 initiative was chartered to deliver. Priority is equal to Story 1 — both are P0 in the PRD — because both are required for MVP.

**Independent Test**: Given a fixture with known `source_attribution` citations across multiple frameworks, rendering the PDF produces 5 per-framework pages where each framework item is classified correctly (Covered / Partial / Gap), the coverage percentage matches a hand-computed ratio, and Gap items are visually highlighted with color + icon.

**Acceptance Scenarios**:

1. **Given** the full finding set and the 5-value taxonomy enum (owasp, mitre-attack, mitre-atlas, nist-ai-rmf, cwe), **When** the aggregate matrix renders, **Then** there is exactly one page per framework — all 5 pages render when `has-source-attribution: true`, including framework pages where every item is a Gap (0% coverage is a valid and expected answer).
2. **Given** a framework YAML with N items and a finding set where K items carry ≥1 `primary` attribution, **When** the coverage percentage renders, **Then** it equals `K / N` where N is the authoritative top-level record count from `schemas/taxonomy/{framework}.yaml` (computed once per framework at data-extraction time).
3. **Given** a framework item with `relationship: primary` attribution on ≥1 finding, **When** it renders on the framework page, **Then** it is classified **Covered**.
4. **Given** a framework item with `relationship: related` or `relationship: derived` attributions but zero `primary`, **When** it renders, **Then** it is classified **Partial**, styled distinctly from Covered and Gap.
5. **Given** a framework item with zero attributions on any finding, **When** it renders, **Then** it is classified **Gap** and visually highlighted with a color + icon distinction (WCAG AA color-blind accessible — color alone insufficient).
6. **Given** the rendered per-framework page, **When** it shows the coverage percentage, **Then** the Partial count is rendered alongside with equal visual weight (e.g., `Covered: 12/38 = 31.6% · Partial: 3 · Gap: 23`) so the full 3-value classification is visible at a glance.
7. **Given** the 5-value taxonomy enum from ADR-028, **When** the matrix renders, **Then** the 2 internal taxonomies (`tachi-control-category`, `tachi-stride-ai-category`) are NOT rendered as framework pages — matrix covers external frameworks only.

---

### User Story 3 - Conditional Inclusion Preserves Backward Compatibility (Priority: P1)

A tachi maintainer regenerates the 5 non-agentic example PDFs and expects byte-identical output under `SOURCE_DATE_EPOCH=1700000000` because no finding carries `source_attribution` yet (F-A3 populators haven't shipped). The `has-source-attribution` boolean gate suppresses the entire coverage-attestation section — no blank page, no section header, no divider, no empty table — so the baselines remain truly additive-when-absent.

**Why this priority**: Byte-identity regression on the 5 baselines is a BLOCKER per SC-002. Without this story, F-B cannot merge — the feature must be additive-only until F-A3 populates findings. Equal-priority to Stories 1 and 2 because it gates the entire feature.

**Independent Test**: Running the pipeline on any architecture whose findings carry no `source_attribution` produces a PDF byte-identical to the pre-F-B baseline under `SOURCE_DATE_EPOCH=1700000000`.

**Acceptance Scenarios**:

1. **Given** a threats.md file where no finding carries a non-empty `source_attribution` array, **When** the extraction step runs, **Then** the Typst data contract emits `#let has-source-attribution = false`.
2. **Given** a threats.md file where ≥1 finding carries a non-empty `source_attribution` array, **When** the extraction step runs, **Then** the Typst data contract emits `#let has-source-attribution = true` and emits the per-finding records + per-framework aggregate records.
3. **Given** a `report-data.typ` regenerated against stale data that does NOT declare `has-source-attribution`, **When** `main.typ` renders, **Then** the default-value guard in the §2b defaults block forces the variable to `false` and the coverage-attestation section is omitted — no Typst "variable not found" compile error.
4. **Given** `has-source-attribution: false`, **When** `main.typ` renders, **Then** the coverage-attestation section is entirely omitted: no page break, no section header, no divider, no empty table shell.
5. **Given** the 5 non-agentic example baselines referenced by the backward-compatibility test harness, **When** the pipeline re-runs under `SOURCE_DATE_EPOCH=1700000000`, **Then** all 5 regenerated PDFs are byte-identical to their committed `.pdf.baseline` files.
6. **Given** the 6th example (`agentic-app`), **When** the pipeline re-runs, **Then** per Feature 128 convention, the baseline either regenerates byte-identically (if F-A3 has not populated attributions) or may be re-baselined as a coordinated follow-on once F-A3 populates findings — out of scope for F-B.

---

### Edge Cases

- **Zero-item framework YAML**: if a framework YAML is accidentally empty (zero top-level records), coverage is mathematically undefined. The aggregator MUST render the page with `N/A` for coverage percentage (not `0/0` or a divide-by-zero error).
- **Zero-finding match**: if the finding set is non-empty but no finding cites any framework item, the framework page MUST render with `Covered: 0/N = 0.00% · Partial: 0 · Gap: N` — the 0% coverage answer is valid.
- **Malformed framework YAML**: if `yaml.safe_load` fails on any `schemas/taxonomy/{framework}.yaml`, the aggregator MUST fail loud with a clear error (per ADR-022 fail-loud pattern), not silently emit empty aggregates.
- **Partial-only item with mixed `related` and `derived`**: if a framework item has attributions on multiple findings — some `related`, some `derived`, zero `primary` — it classifies as Partial (Q1-A rule). The distinction between `related` and `derived` is NOT surfaced at the coverage-matrix tier; it remains visible on the per-finding table (bold-vs-plain rendering).
- **Finding cites an ID that doesn't resolve in the YAML**: F-A2's referential-integrity validator (ADR-028 Decision 5) catches this upstream of F-B. The spec TRUSTS the parsed finding list and does NOT re-validate at aggregator time.
- **Large per-finding table (100+ rows, 7 columns)**: Typst native row-break handles pagination; landscape-orientation fallback is pre-approved if portrait-orientation smoke test fails.
- **F-A3 ships during F-B authoring**: the Day 2 EOD coordination check detects this. Serialization decision: whoever merges second re-baselines (~0.5-1d cost absorbed by second merger).
- **Adopter reads 0% coverage and misreads it as "tachi has zero coverage"**: the gate suppresses the section entirely when `has-source-attribution: false`, so adopters see no coverage surface until F-A3 populates findings. Dormant risk until F-A3.

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The pipeline MUST render a new coverage-attestation section in the PDF security report containing (a) a per-finding attribution table and (b) one per-framework coverage matrix page per external framework in the 5-value taxonomy enum from ADR-028 (owasp, mitre-attack, mitre-atlas, nist-ai-rmf, cwe).
- **FR-002**: The pipeline MUST emit a new boolean flag `has-source-attribution` in the Typst data contract. The flag is `true` iff ≥1 finding in the current threat model carries a non-empty `source_attribution` array; `false` otherwise.
- **FR-003**: The coverage-attestation section MUST render ONLY when `has-source-attribution` is `true` AND the per-finding-record count is greater than zero. When either condition is false, the entire section (header, divider, table, framework pages) MUST be omitted from the rendered PDF.
- **FR-004**: The pipeline MUST carry a default-value guard for `has-source-attribution` in the defaults block of `main.typ`, mirroring the existing default-value guards for `has-maestro-data`, `has-attack-trees`, `has-attack-chains`, and peers. The guard MUST set `has-source-attribution` to `false` when the variable is absent from the Typst data contract — preventing Typst "variable not found" compile errors on stale `report-data.typ` files.
- **FR-005**: The per-finding attribution table MUST contain columns in this order: `Finding ID | Title | Severity | OWASP refs | MITRE refs | NIST refs | CWE refs`. The MITRE column MUST group ATT&CK and ATLAS with a per-ref prefix distinguishing the two (e.g., `ATT&CK:T1070.001` vs `ATLAS:AML.T0051`).
- **FR-006**: In the per-finding table, citations with `relationship: primary` MUST render with visually stronger weight (bold or equivalent) than citations with `relationship: related` or `relationship: derived`. Findings with empty or absent `source_attribution` MUST render their row with blank ref cells — the row itself is NOT suppressed.
- **FR-007**: For each of the 5 external frameworks, the pipeline MUST classify every top-level record in the framework YAML as one of Covered / Partial / Gap using the following rules:
  - **Covered** — ≥1 finding cites this item with `relationship: primary`.
  - **Partial** — zero findings cite this item with `relationship: primary`, AND ≥1 finding cites this item with `relationship: related` or `relationship: derived`.
  - **Gap** — zero findings cite this item with any relationship value.
- **FR-008**: Each per-framework page MUST display Covered count, Partial count, Gap count, and coverage percentage. The coverage percentage numerator MUST use Covered count only (primary-only); Partial count MUST be rendered alongside with equal visual weight (e.g., `Covered: 12/38 = 31.6% · Partial: 3 · Gap: 23`).
- **FR-009**: For each framework, the coverage-percentage denominator (`yaml_record_count`) MUST equal the total number of top-level records in `schemas/taxonomy/{framework}.yaml` at extraction time, computed once per framework and pinned in the emitted Typst data contract.
- **FR-010**: Gap framework items MUST render with a color + icon distinction that is WCAG AA color-blind accessible (color alone is insufficient). The exact visual treatment is owned by the ux-ui-designer memo (due Day 2 AM per PRD).
- **FR-011**: The aggregator function MUST handle three edges gracefully:
  - (a) Zero items in a framework YAML → coverage percentage renders as `N/A`.
  - (b) Zero findings matching any item in a framework YAML → coverage percentage renders as `0.00%`; page still renders.
  - (c) Malformed framework YAML (safe_load failure) → aggregator fails loud with a clear error (per ADR-022), bubbling an actionable error through `extract-report-data.py`.
- **FR-012**: The pipeline MUST paginate the per-finding table using Typst native row-break mechanics. If the Day 3 pagination smoke test on a 100-finding × 5-framework fixture shows unacceptable output on portrait US Letter, a landscape-orientation fallback or a per-severity split is pre-approved as a contingency.
- **FR-013**: The feature MUST commit a public per-feature ADR (ADR-029) under the Proposed → Accepted dual-commit pattern (Feature 180 / 189 precedent). The ADR MUST document (a) the new Typst template + aggregator + `has-source-attribution` boolean pattern cross-referenced to Feature 141 precedent, (b) the 3-value classification with Q1-A rule, (c) the denominator-authority convention (Q2-A), (d) the zero-crosswalk-JOIN scope line, (e) the Out-of-Scope deferral (Q6-D), (f) the 22-file zero-edit invariant preservation (ADR-023 / ADR-028 lineage), (g) the Partial disclosure rule.
- **FR-014**: The feature MUST preserve the 22-file zero-edit invariant: zero modifications to any file under `.claude/agents/tachi/stride/*.md` (6 files), `.claude/agents/tachi/ai/*.md` (5 files), or `.claude/skills/tachi-{agent-name}/references/detection-patterns.md` (11 files). F-B reads whatever `source_attribution` findings carry; populator wiring is strictly F-A3 scope.
- **FR-015**: The feature MUST NOT modify `schemas/finding.yaml` or any file under `schemas/taxonomy/`. F-B is purely a renderer + aggregator over already-landed schemas.
- **FR-016**: The feature MUST NOT introduce new runtime dependencies. `pyproject.toml`, `requirements.txt`, `requirements-dev.txt`, and `package.json` all MUST carry empty diffs relative to the pre-feature state (excepting developer-tier dev-only additions if strictly required).
- **FR-017**: The feature MUST NOT consult `schemas/taxonomy/crosswalk.yaml`. F-B's coverage matrix is intra-framework only; cross-framework JOIN via the crosswalk is deferred to a follow-on feature.
- **FR-018**: The feature MUST NOT render framework pages for the 2 internal taxonomies (`tachi-control-category`, `tachi-stride-ai-category`) even though they are members of the F-A1 7-value catalog enum. These are internal vocabulary, not external frameworks tachi attests coverage against.
- **FR-019**: The feature MUST NOT surface a 4th "Out-of-Scope" classification in MVP. All non-cited items classify as Gap. The Out-of-Scope question-space is deferred to a follow-on feature per PRD Q6-D resolution.

### Key Entities

- **Finding** (existing entity; F-A2): A security finding parsed from `threats.md`. Carries 0..N `source_attribution` records under the list-of-record contract from ADR-028. F-B reads but does not modify findings.
- **Source Attribution Record** (existing entity; F-A2): A `{taxonomy, id, relationship}` record citing a single framework item. `taxonomy` is a 5-value closed enum (owasp, mitre-attack, mitre-atlas, nist-ai-rmf, cwe). `relationship` is a 3-value closed enum (primary, related, derived) with `primary` as the default.
- **Framework Catalog Record** (existing entity; F-A1): A top-level record in `schemas/taxonomy/{framework}.yaml`. Identified by `id` field (e.g., `LLM05`, `T1070.001`, `AML.T0051`, `MAP 4.2`, `CWE-1426`). F-B reads the record count and the `id` set per framework.
- **Per-Finding Attribution Row** (new F-B entity): One record per finding emitted by the aggregator function. Shape: `{id, title, severity, owasp_refs, mitre_refs, nist_refs, cwe_refs}` where each `*_refs` is an array of `{id, relationship}` items. Consumed by the Typst per-finding table.
- **Per-Framework Aggregate Record** (new F-B entity): One record per external framework emitted by the aggregator function. Shape: `{framework, yaml_record_count, covered_count, partial_count, gap_count, coverage_percentage}`. Consumed by the Typst per-framework page.
- **`has-source-attribution` Boolean** (new F-B entity): A single Typst-data-contract boolean gating the entire coverage-attestation section. Value = `true` iff ≥1 finding carries a non-empty `source_attribution` array.

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: The new Typst page template exists, compiles without errors on a populated fixture, and renders both the per-finding table and the 5 per-framework coverage matrix pages.
- **SC-002**: The 5 non-agentic example baselines referenced by `tests/scripts/test_backward_compatibility.py` regenerate byte-identically under `SOURCE_DATE_EPOCH=1700000000` per ADR-021 (zero-impact-when-absent invariant).
- **SC-003**: The `has-source-attribution` boolean is emitted in the Typst data contract with value `true` iff ≥1 finding carries a non-empty `source_attribution` array, and `false` otherwise — no implicit defaults that would silently invert the gate.
- **SC-004**: `main.typ` (a) adds a default-value guard block for `has-source-attribution` mirroring the existing default guards, AND (b) invokes the coverage-attestation page only inside a conditional block gated on both `has-source-attribution == true` AND per-finding row count > 0. Zero template output when either predicate is false.
- **SC-005**: Per-framework coverage percentage equals `(items with ≥1 primary attribution across the full finding set) / (F-A1 framework YAML top-level record count)`, verified against a manual-sampled cross-check on ≥1 fixture example. The denominator matches the count produced by `len(yaml.safe_load(schemas/taxonomy/{framework}.yaml))` at extraction time.
- **SC-006**: Gap framework items render with a visible color + icon distinction from Covered and Partial items (WCAG AA color-blind accessible — color alone is insufficient). Partial count renders alongside the coverage percentage on every per-framework page with equal visual weight.
- **SC-007**: Public per-feature ADR-029 is committed under the Proposed → Accepted dual-commit pattern. Proposed committed Day 1 Wave 1.0 (unblocks Wave 1.1 parallel scaffolding); Accepted committed Day 4 at PR pre-merge with `<pending-post-merge-fill>` for merge SHA; SHA fill committed post-merge directly to main.
- **SC-008**: Zero new runtime dependencies — empty diff on `pyproject.toml`, `requirements.txt`, `requirements-dev.txt`, and `package.json` (excepting developer-tier test-only additions already declared per Feature 128 precedent).
- **SC-009**: Zero edits to the 22-file F-A2 zero-edit scope: 11 threat-detection agents under `.claude/agents/tachi/stride/*.md` and `.claude/agents/tachi/ai/*.md`, and 11 skill-reference `detection-patterns.md` files under `.claude/skills/tachi-{agent-name}/references/`. Verified by grep audit at PR pre-merge.
- **SC-010**: The aggregator runtime on a 100-finding × 5-attribution fixture completes in under 1 second on commodity hardware (informational floor, not CI-enforced). Typst compile time for the coverage-attestation section on a 100-finding × 5-framework fixture adds no more than 2 seconds to the PDF render budget.
- **SC-011**: Unit tests for the aggregator function cover (a) empty finding-set fixture, (b) one-finding-one-primary fixture, (c) multi-finding multi-relationship multi-framework fixture, asserting `has-source-attribution` boolean correctness, per-framework count arithmetic, coverage-percentage arithmetic, zero-denominator edge (`N/A`), and zero-numerator edge (`0.00%`).
- **SC-012**: Day 3 pagination smoke test on a synthetic 100-finding × 5-framework fixture validates the per-finding table renders acceptably on portrait US Letter. If unacceptable, the landscape-orientation or per-severity-split fallback activates and is documented in the PR.

---

## Assumptions

- **A1**: Feature 180 (F-A1 taxonomy YAMLs) and Feature 189 (F-A2 `source_attribution` schema contract) are merged to main as of 2026-04-17 (verified via `git log` — squash commits `8b7c7bf` and `6d5d890`).
- **A2**: `has-source-attribution` evaluates to `false` on every committed example baseline pre-F-A3 — no finding across any committed example currently carries a populated `source_attribution` array. This is the default state of every fresh pipeline run until F-A3 ships populators.
- **A3**: The parser `parse_threats_findings` in `scripts/tachi_parsers.py` round-trips `source_attribution` correctly on findings that carry it (per F-A2 FR-2). F-B trusts the parsed finding list as-is and does NOT re-run referential-integrity validation.
- **A4**: The Feature 141 `has-attack-chains` pattern + Feature 128 new-Typst-page + `extract-report-data.py` boolean pattern are the correct architectural precedents for F-B. No novel template architecture is introduced.
- **A5**: All 5 external-framework YAMLs are modestly scaled (OWASP 60, MITRE ATT&CK 38, MITRE ATLAS 12, NIST AI RMF 72, CWE 53; total 235 items). F-A1 already curated representative subsets per its FR-003 spec. No "large denominator" problem exists and no `coverage_scope` schema extension is required (corrects PRD v1.0 R2 factual error; see PRD v1.1).
- **A6**: The ux-ui-designer memo specifying Q5 visual treatment (color + icon for Covered / Partial / Gap) lands Day 2 AM. If the memo slips, the architect-recommended default (Covered = green check, Partial = yellow half-circle, Gap = red X with red fill) is a pre-approved fallback.
- **A7**: F-A3 (threat-agent populators) is not filed as an Issue during F-B Days 1-2. The Day 2 EOD coordination check detects this; if F-A3 is filed, a serialization decision is escalated.

---

## Constraints

- **Technical**: Python stdlib + existing declared deps only; no new npm / Node.js dependencies; no new Typst language version requirement.
- **Backward-compatibility**: SC-002 (5 baselines byte-identical under `SOURCE_DATE_EPOCH=1700000000`) is a BLOCKER.
- **Governance**: Public per-feature ADR-029 on merge under the Proposed → Accepted dual-commit pattern; the ADR governs the decision surfaces enumerated in FR-013.
- **Scope discipline**: SC-009 (22-file zero-edit invariant) is a BLOCKER. FR-015 (zero schema changes) is a BLOCKER. FR-017 (no crosswalk JOIN) is a scope boundary; any cross-framework reasoning is deferred.
- **Timeline**: 4 working days is the realistic planning baseline (2026-04-20 Mon → 2026-04-23 Thu). 3 days is aspirational contingent on the Q1-A + Q2-A + Q6-D happy path and Q5 landing Day 2 AM.

---

## Dependencies

- **F-A1 (Feature 180)** — Taxonomy YAMLs supply the coverage-percentage denominators. **SATISFIED** as of 2026-04-17.
- **F-A2 (Feature 189)** — `source_attribution` field on findings supplies the raw data F-B reads. **SATISFIED** as of 2026-04-17.
- **ADR-021** (byte-determinism under `SOURCE_DATE_EPOCH`) — SC-002 gate uses this harness. **SATISFIED**.
- **ADR-022** (CLI-prerequisite fail-loud pattern) — Aggregator malformed-YAML handling follows this. **SATISFIED**.
- **ADR-023** (skill-references pattern / 22-file zero-edit invariant) — Preserved by F-B. **SATISFIED**.
- **ADR-028** (F-A2 schema contract) — Provides the `relationship` enum and referential-integrity contract F-B trusts. **SATISFIED**.
- **Feature 141 precedent** (`has-attack-chains` pattern) — Architectural template verified at `scripts/extract-report-data.py:1426` and `templates/tachi/security-report/main.typ:246`. **SATISFIED**.
- **Feature 128 precedent** (new-Typst-page + `extract-report-data.py` boolean) — Architectural template verified at `scripts/extract-report-data.py:1362` and `templates/tachi/security-report/main.typ:89`. **SATISFIED**.
- **F-A3 (threat-agent populators)** — **NOT required** for F-B to ship. The `has-source-attribution` gate means F-B is a no-op PDF-wise on any architecture whose findings carry no attributions.

---

## Out of Scope

- **Out-of-Scope as a 4th classification** — MVP classification is 3-value (Covered / Partial / Gap) per PRD Q6-D. Adopter-visible Out-of-Scope treatment is deferred to a follow-on feature once demand is visible.
- **Cross-framework JOIN via `crosswalk.yaml`** — Composite coverage claims spanning multiple frameworks (e.g., "OWASP LLM05 ↔ MITRE ATLAS AML.T0051 via crosswalk") are deferred. F-B's matrix is intra-framework only.
- **Interactive coverage export (CSV / JSON)** — F-B emits structured data to the Typst data contract; exporting the aggregator output as a separate adopter-facing artifact is a follow-on.
- **Time-series coverage delta** — Feature 104 baseline-delta pattern applied to coverage (showing coverage change between baseline and current run) is deferred until F-A3 populator wiring settles.
- **Per-finding coverage infographic template** — A Feature 128-style JPEG infographic rendering the coverage matrix visually is a follow-on; F-B ships the PDF section only.
- **Threat-agent populator wiring** — F-A3 scope, preserved by the 22-file zero-edit invariant (FR-014, SC-009).
- **Editing or enriching `source_attribution` during F-B rendering** — F-B is read-only over the finding list.
- **Tachi-internal taxonomy matrix pages** — `tachi-control-category` and `tachi-stride-ai-category` are NOT rendered as framework pages (internal vocabulary, not external framework coverage).
- **Breaking schema changes** — `schemas/finding.yaml` and `schemas/taxonomy/*.yaml` are NOT modified.
- **SARIF `source_attribution` propagation** — SARIF exporter continues to treat `source_attribution` as post-F-A2 (absent from SARIF output). Separate follow-on.
- **F-A1 YAML `coverage_scope` field extension** (PRD Q2-B) — Rejected on scope-expansion grounds; all 5 YAMLs are modestly scaled.
- **Populated-fixture demonstration on `agentic-app` example** (PRD Q-P1) — Sample `source_attribution` records belong in test fixtures under `tests/scripts/fixtures/`, not in example outputs. Follows Feature 189 precedent verbatim.

---

## References

### PRD
- `docs/product/02_PRD/194-coverage-attestation-report-section-2026-04-18.md` (PRD v1.1, Triple Sign-off Approved 2026-04-18)

### Research
- `specs/194-coverage-attestation-report-section/research.md` (file:line citations, KB findings, precedent audit)

### Precedent PRDs
- Feature 180 (F-A1 — taxonomy YAMLs): `docs/product/02_PRD/180-taxonomy-crosswalk-collection-2026-04-17.md`
- Feature 189 (F-A2 — `source_attribution` contract): `docs/product/02_PRD/189-source-attribution-schema-extension-2026-04-17.md`
- Feature 141 (cross-layer attack chains — direct `has-attack-chains` precedent)
- Feature 128 (executive architecture infographic — direct new-Typst-page precedent)

### ADRs
- ADR-021: `SOURCE_DATE_EPOCH` determinism
- ADR-022: CLI-prerequisite fail-loud pattern
- ADR-023: Skill-references pattern (22-file zero-edit invariant)
- ADR-027 (F-A1): Taxonomy crosswalk schema
- ADR-028 (F-A2): Source-attribution schema contract
- ADR-029 (this feature): To be authored Day 1, transitioned Accepted Day 4

### Code References (Verified)
- `schemas/finding.yaml:212` — `source_attribution` field (schema v1.5)
- `scripts/tachi_parsers.py:796` — `parse_threats_findings` round-trips `source_attribution`
- `scripts/extract-report-data.py:1362` — `has-maestro-data` emission precedent
- `scripts/extract-report-data.py:1426` — `has-attack-chains` emission precedent
- `templates/tachi/security-report/main.typ:47` — `attack-chain.typ` import precedent
- `templates/tachi/security-report/main.typ:89-107` — §2b defaults block (default guards)
- `templates/tachi/security-report/main.typ:103` — `has-attack-chains` default guard
- `templates/tachi/security-report/main.typ:246` — `has-attack-chains` conditional block precedent
- `templates/tachi/security-report/main.typ:348` — end of MAESTRO-findings block (F-B insertion point ↑)
- `templates/tachi/security-report/main.typ:398` — start of compensating-controls block (F-B insertion point ↓)
- `tests/scripts/test_backward_compatibility.py:38-45` — authoritative baseline list (5 non-agentic baselines)

### GitHub
- Issue [#194](https://github.com/davidmatousek/tachi/issues/194)
