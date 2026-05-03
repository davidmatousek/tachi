---
prd:
  number: 189
  topic: source-attribution-schema-extension
  created: 2026-04-17
  status: Approved
  type: feature
triad:
  pm_signoff: {agent: product-manager, date: 2026-04-17, status: APPROVED, notes: "Problem statement grounded in F-A1 delivery (Feature 180 same-day), 3 user stories preserved verbatim from Issue #189 with job-story restructuring, 7 success criteria (SC-1 to SC-7), scope line clear on contract-only (F-A2) vs populators (F-A3). Stale 1.3→1.4 wording from Issue body corrected to 1.4→1.5. Q-P1 resolved: NO demonstration on examples — sample records belong in test fixtures per team-lead. Q4 resolved: schema bump 1.4→1.5. Ready for /aod.plan."}
  architect_signoff: {agent: architect, date: 2026-04-17, status: APPROVED_WITH_CONCERNS, notes: "0 BLOCKING / 0 HIGH / 3 MEDIUM / 2 LOW. Scope discipline is sound, 5-value taxonomy cut correct, SC-7 zero-edit holds, SC-2 not chicken-and-egg (baselines exercise absent-path). Concerns addressed inline: (1) Q1-E added (new Section 9 YAML block gated like Feature 141 has-attack-chains) as architect-recommended surface; Q1-A and Q1-D rejected. (2) Q2 narrowed to Q2-B (separate validation phase, orchestrator Phase 4 caller). (3) First-list-of-record framing corrected — references:list[string] is list-typed precedent, F-A2 is first list-of-RECORD; named Complex-Shape Addition Clarifier under ADR-026. (4) Risk R2 upsized to High (combinatorial across SARIF/Typst/extract-report-data). (5) FR-6/SC-7 enumerated 11 agent files + 11 skill-reference files per ADR-023. Conditional on Q1+Q2 memo landing Day 1 Wave 1 before schema YAML authoring."}
  techlead_signoff: {agent: team-lead, date: 2026-04-17, status: APPROVED_WITH_CONCERNS, notes: "0 BLOCKING / 0 HIGH / 2 MEDIUM / 1 LOW. 2-3 day timeline defensible; midpoint 3 days, 2-day floor only if Q1 resolves to Q1-B sidecar. Concerns addressed inline: (1) Calendar fix — 2026-04-18 is Saturday, Day 1 = 2026-04-20 Monday, delivery 2026-04-22 Wednesday. (2) Agent assignment — tester primary for SC-2 regression, senior-backend-engineer secondary for failure diagnostics. (3) Q1 pre-narrowed to Q1-B/C/E (Q1-A and Q1-D eliminated per Won't-Have scope line on Section 7 column). (4) Q-P1 resolved NO (sample records belong in test fixtures, not example outputs). Partial parallelism: enum-validation and schema YAML authoring can run parallel to Q1/Q2 memo on Day 1 Wave 1 (~0.25d savings). ADR Proposed→Accepted overhead (~0.5d architect load) baked into estimate. Ready for /aod.plan."}
source:
  idea_id: 189
  story_id: null
---

# F-A2 — Source Attribution Schema Extension: Product Requirements Document

**Status**: Draft
**Created**: 2026-04-17
**Author**: product-manager
**Reviewers**: architect, team-lead
**Phase**: BLP-01 Foundation tier (2nd of 3 foundation features: F-A1 → **F-A2** → F-A3)
**Priority**: P1

---

## 📋 Executive Summary

### The One-Liner

Let every tachi threat finding carry a machine-readable list of the compliance-framework items it addresses, so coverage stops being a manual claim and starts being an aggregable data property of findings.

### Problem Statement

Today, when tachi produces a threat finding (e.g., "LLM05 improper output handling in the Response Sanitizer component"), the finding's relationship to external compliance frameworks — OWASP LLM Top 10, MITRE ATT&CK, MITRE ATLAS, NIST AI RMF, CWE — lives only in free-text prose inside the `mitigation` or `references` fields of `schemas/finding.yaml`. An adopter who wants to answer **"which findings address OWASP LLM05?"** or **"what's our coverage of MITRE ATLAS AML.T0051?"** has to either text-parse agent markdown prose or maintain the coverage claim by hand.

Feature 180 (F-A1, delivered 2026-04-17) shipped the machine-readable taxonomy catalogs and the 526-edge crosswalk that make per-item lookups possible — but the *findings themselves* still do not cite those IDs in a structured way. F-A1 is a one-sided bridge: the framework-vocabulary end is built, but the finding end is not yet wired. Until it is, downstream consumers (F-B coverage attestation report section, ecosystem integrations for SIEMs and compliance dashboards) have nothing to aggregate from.

### Proposed Solution

Extend `schemas/finding.yaml` with a single additive optional field — `source_attribution` — whose value is an array of `{taxonomy, id, relationship}` records. `taxonomy` keys into one of the 5 external F-A1 framework YAMLs (`owasp`, `mitre-attack`, `mitre-atlas`, `nist-ai-rmf`, `cwe`); `id` is the taxonomy-internal identifier (e.g., `LLM05`, `AML.T0051`, `MEASURE 2.7`, `CWE-1426`); `relationship` is a closed 3-value enum (`primary | related | derived`, default `primary`). Update `scripts/tachi_parsers.py::parse_threats_findings` to round-trip the field. Ship a public per-feature ADR documenting the additive-compatibility rationale under the ADR-026 minor-bump rule.

**Two things the solution is deliberately NOT:**
1. It is **not** a wiring of threat-detection agents to *populate* `source_attribution`. This PRD establishes the field and its contract; downstream populators (threat agents choosing to cite IDs during detection) are scope boundaries, to be addressed as separate features.
2. It is **not** a coverage report or aggregation engine. F-B is the feature that consumes `source_attribution` to produce the coverage attestation. F-A2 is the data shape F-B requires.

### Success Criteria

- **SC-1** — Schema version is exactly `"1.5"` in `schemas/finding.yaml` head (currently `"1.4"`; see P1 correction in Open Questions).
- **SC-2** — The 5 existing non-agentic example PDFs (`web-app`, `microservices`, `ascii-web-api`, `mermaid-agentic-app`, `free-text-microservice`) regenerate **byte-identically** under `SOURCE_DATE_EPOCH=1700000000` per ADR-021.
- **SC-3** — `parse_threats_findings` returns `source_attribution` when present on a finding and omits the key when absent — no implicit default array injection.
- **SC-4** — Referential-integrity test passes: every sample-fixture `taxonomy` value keys into one of the 5 F-A1 framework YAMLs; every sample-fixture `id` resolves as a record in the named YAML; every `relationship` value is a member of the closed 3-value enum.
- **SC-5** — A public per-feature ADR is committed (Proposed → Accepted dual-commit pattern per Feature 180 precedent) documenting the additive-compatibility decision and the serialization-surface choice resolved per Open Question Q1.
- **SC-6** — Zero new runtime dependencies — empty diff on `pyproject.toml`, `requirements*.txt`, `package.json`.
- **SC-7** — Zero edits to the 11 STRIDE+AI threat-detection agents (`.claude/agents/tachi/{stride,ai}/*.md`) preserving the zero-edit invariant established in Feature 082 under ADR-023.

### Timeline

Target: **2-3 working days** of active implementation (schema + parser + test-fixture authoring), plus a brief PR/governance cycle. Delivery window **2026-04-20 (Monday) → 2026-04-22 (Wednesday)** — 2026-04-18 is a Saturday; Day 1 = first working day after PRD approval. Serialization-surface decision in Q1 (Architect) is the timing-critical prerequisite: it must land on Day 1 Wave 1 so that the schema YAML and the parser-test fixtures can be authored in parallel on Days 1-2. Partial parallelism opportunity: enum-validation scaffolding and schema YAML authoring are Q1-independent and can run parallel to architect's Q1/Q2 memo on Day 1 Wave 1 (~0.25 day savings).

---

## 🎯 Strategic Alignment

### Product Vision Alignment

**Reference**: `docs/product/01_Product_Vision/product-vision.md`

tachi's vision — "Automated threat modeling that gives security engineers a complete, compliance-aware picture in minutes, not days" — is undermined by coverage claims that are manual prose rather than aggregable data. F-A2 closes the last structural gap between tachi findings and the compliance frameworks adopters actually care about. Without it, tachi produces *good threat prose* but not *compliance-aggregable output*.

### BLP-01 Initiative Fit

**Reference**: `BLP-01 threat coverage` memory — F-A2 is the 2nd of 11 features in the BLP-01 multi-taxonomy coverage initiative; Foundation tier (F-A1, F-A2, F-A3); F-A1 delivered as Feature 180 on 2026-04-17 (same-day merge, PR #181, commit `8b7c7bf`).

F-A2's place in the 3-feature foundation chain:

```
F-A1 (Feature 180, delivered 2026-04-17)
  │  Ships 7 framework YAML catalogs + 526-edge crosswalk — the framework-vocabulary end
  ▼
F-A2 (this PRD, #189)
  │  Ships the `source_attribution` field — the finding end of the bridge
  ▼
F-A3 (follow-on)
  │  Wires populators and aggregators — the bridge traffic
  ▼
F-B (mid-term)
  Coverage attestation report section — reads `source_attribution` values, joins against F-A1 crosswalk, produces aggregate per-framework coverage narrative
```

F-A2 is the **data-shape contract that F-A3 and F-B both depend on**. Misshape it and both downstream features carry the debt.

### Recent ADR Lineage

- **ADR-026** (Feature 142, Accepted 2026-04-16): establishes the minor-bump rule for *NEW enum-typed field additions* under three additive-compatibility conditions (additive, has default, schema shape unchanged). The existing `references: list[string]` field (schema 1.0+, `schemas/finding.yaml:101-110`) establishes the list-typed-field precedent; F-A2 is the **first list-of-RECORD field** (nested shape per element). The F-A2 ADR will name this extension as a "Complex-Shape Addition Clarifier" under ADR-026 — schema-document shape unchanged, but consumer traversal complexity grows (a nested iteration rather than a scalar read). The minor-bump remains defensible under ADR-026 provided the clarifier is explicit.
- **ADR-020** (Feature 084, revised through 2026-04-16): established the `maestro_layer` passive-overlay pattern — an additive optional scalar enum classified at orchestrator Phase 1 and propagated through downstream phases. F-A2 inherits the *additive optional* half of the pattern but NOT the *orchestrator-populated* half: `source_attribution` is populated by threat-detection agents (or left empty), not by the orchestrator.
- **ADR-021** (byte-determinism under `SOURCE_DATE_EPOCH`): SC-2 regression gate uses this harness.

### Roadmap Fit

- **Phase**: BLP-01 Foundation tier (Q2 2026 roadmap)
- **Week**: Week of 2026-04-13 — immediate follow-on to Feature 180 merge
- **Dependencies**: F-A1 (Feature 180) — **SATISFIED** as of 2026-04-17

---

## 🧑‍💼 Target Users & Personas

### Primary Persona: **tachi Pipeline Developer**

- **Role**: Engineer maintaining `scripts/tachi_parsers.py`, schema files, Typst templates, and SARIF/YAML output producers
- **Goal**: Extend the finding IR without regressing any of the 5 existing non-agentic example baselines
- **Pain Point Today**: Framework cross-references live in free-text `mitigation`/`references` fields; adding machine-readable cross-references means defining a new field and resolving the YAML-vs-markdown-cell serialization tension
- **Value Delivered**: A schema-defined, parser-round-tripped array field with a precedent-setting serialization choice documented in an ADR; a referential-integrity test template for future taxonomy-citing features to reuse

### Secondary Persona: **Downstream Feature Author (F-A3 / F-B)**

- **Role**: Future engineer building F-A3 populators or the F-B coverage attestation report section
- **Goal**: Aggregate per-framework coverage from findings without re-parsing free-text
- **Pain Point Today**: No stable programmatic surface to read citations from
- **Value Delivered**: A stable `source_attribution` field contract they can depend on; the F-A1 framework YAMLs they can join against

### Tertiary Persona: **Ecosystem Integrator**

- **Role**: Third-party vendor maintaining a tachi → SIEM / vulnerability-manager / compliance-dashboard adapter
- **Goal**: Resolve a tachi finding to a specific OWASP/ATT&CK/ATLAS/NIST/CWE ID programmatically
- **Pain Point Today**: Must text-parse agent markdown prose
- **Value Delivered**: Direct `yaml.safe_load` → `[f for f in findings if any(a['taxonomy'] == 'owasp' for a in f.get('source_attribution', []))]`

---

## 📖 User Stories

All three user stories are preserved from GitHub Issue #189 (which sourced them from BLP-01 §7, F-A2). Job-story restructuring applied; acceptance criteria preserved verbatim where they provide specific testable predicates.

### US-189-1: Multi-Framework Citation on a Single Finding

**When** a threat agent emits a finding that addresses multiple compliance-framework items simultaneously (e.g., LLM05 improper output handling spans OWASP LLM05, CWE-1426, and MITRE ATLAS AML.T0051),
**I want to** cite all three items on the single finding without duplicating finding rows,
**So I can** keep the finding's semantic unit intact while making every cited item programmatically aggregable.

**Acceptance Criteria**:
- **Given** `schemas/finding.yaml` head, **when** I read `schema_version`, **then** it equals exactly `"1.5"` — the minor bump from the current head value of `1.4` per the ADR-026 additive-field rule. *(Note: Issue #189 body specifies `1.3 → 1.4`; this is a stale baseline — the current head is 1.4 from Feature 142's `agentic_pattern`. Corrected in this PRD; see Open Question Q4.)*
- **Given** a finding YAML document, **when** the document omits `source_attribution`, **then** it is valid against schema 1.5 (backward-compatible: field is optional).
- **Given** a finding YAML document, **when** the document includes `source_attribution: [{taxonomy: owasp, id: LLM05, relationship: primary}, {taxonomy: cwe, id: CWE-1426, relationship: primary}, {taxonomy: mitre-atlas, id: AML.T0051, relationship: primary}]`, **then** it is valid and the three records are preserved in parser output order.

**Priority**: P0
**Effort**: S

### US-189-2: Parser Round-Trip Preserves Backward Compatibility

**When** the pipeline parses the Section 7 table in `threats.md` on any of the 5 existing non-agentic example baselines,
**I want to** get back the same finding objects I got before F-A2 — no extra keys, no dropped keys,
**So I can** be certain F-A2 is truly additive and the SC-2 byte-deterministic regeneration gate passes.

**Acceptance Criteria**:
- **Given** a threats.md file that does NOT carry `source_attribution` on any finding, **when** I call `parse_threats_findings(content)`, **then** returned finding objects do NOT contain a `source_attribution` key (no implicit default array injected — preserves the Feature 104 precedent for `delta_status`-style conditional keys).
- **Given** a threats.md file that carries `source_attribution` on one or more findings (via the serialization surface selected in Q1), **when** I call `parse_threats_findings(content)`, **then** returned finding objects contain the `source_attribution` key with an array whose length, order, and per-record `{taxonomy, id, relationship}` structure match the input.
- **Given** the 5 existing non-agentic example PDF baselines (`examples/{web-app,microservices,ascii-web-api,mermaid-agentic-app,free-text-microservice}/security-report.pdf.baseline`), **when** I re-run the full pipeline under `SOURCE_DATE_EPOCH=1700000000`, **then** all 5 regenerated PDFs are byte-identical to their committed baselines (SC-2 regression).

**Priority**: P0
**Effort**: S

### US-189-3: Closed-Enum `relationship` with Referential Integrity

**When** a coverage auditor reads a finding's `source_attribution` array downstream,
**I want to** know from the `relationship` value whether the cited item is the primary item the finding addresses, a related item, or a derived item,
**So I can** weight primary citations differently from related or derived ones when F-B computes per-framework coverage percentages.

**Acceptance Criteria**:
- **Given** a finding with `source_attribution: [{taxonomy: owasp, id: LLM05}]` (no `relationship` set), **when** parsed, **then** the `relationship` defaults to `primary`.
- **Given** a finding with `source_attribution: [{taxonomy: owasp, id: LLM05, relationship: fabricated_value}]`, **when** parsed, **then** a validation error surfaces identifying the finding ID, the bad `relationship` value, and the closed-enum domain `{primary, related, derived}`.
- **Given** a finding with `source_attribution: [{taxonomy: not-a-real-taxonomy, id: X}]`, **when** parsed, **then** a validation error surfaces identifying the finding ID, the bad `taxonomy` value, and the closed 5-value domain `{owasp, mitre-attack, mitre-atlas, nist-ai-rmf, cwe}`.
- **Given** a finding with `source_attribution: [{taxonomy: owasp, id: NOT-A-REAL-OWASP-ID}]`, **when** parsed AND a referential-integrity check is enabled, **then** a validation error surfaces identifying the finding ID, the bad `id`, and the YAML file in `schemas/taxonomy/` that was searched. *(Q2 decides whether the referential-integrity check runs at parse time or at a separate validation phase — see Open Questions.)*

**Priority**: P0
**Effort**: S

---

## ⚙️ Functional Requirements

### FR-1 — Schema 1.5 Adds `source_attribution` (Optional, Array of Records)

- `schemas/finding.yaml` head: `schema_version: "1.5"` (correcting the stale `1.3 → 1.4` wording in Issue #189's body).
- New field `source_attribution`:
  - Type: `list[record]`
  - Optional (field-level); defaulted to *absent* (NOT to empty array) on findings that do not cite anything.
  - Per-record shape: `{taxonomy: string, id: string, relationship: string}`.
  - `taxonomy` is a closed 5-value enum: `{owasp, mitre-attack, mitre-atlas, nist-ai-rmf, cwe}` — the 5 *external* frameworks from F-A1's 7-value catalog enum. The 2 tachi-internal taxonomies (`tachi-control-category`, `tachi-stride-ai-category`) are deliberately **excluded** — they are internal vocabulary, not an external framework tachi claims coverage of.
  - `id` is a non-empty string. Format validation is deferred to the per-YAML record lookup in Q2.
  - `relationship` is a closed 3-value enum: `{primary, related, derived}`. Default: `primary`.

### FR-2 — `parse_threats_findings` Round-Trip Support

- `scripts/tachi_parsers.py::parse_threats_findings` accepts the new field when present, omits the key when absent.
- No implicit default array injection when absent (AC-1 of US-189-2 — preserves Feature 104 `delta_status` precedent for conditional keys).
- Serialization surface is resolved in Q1.

### FR-3 — Validation Rules

- Parser-level rules:
  - Unknown `taxonomy` value → validation error surfacing finding ID + bad value + closed-domain list.
  - Unknown `relationship` value → validation error surfacing finding ID + bad value + closed-domain list.
- Referential-integrity rule (may be parser-level or separate validation phase — Q2):
  - Unknown `id` (value that does not resolve as a record in `schemas/taxonomy/{taxonomy}.yaml`) → validation error surfacing finding ID + bad `id` + target YAML path.

### FR-4 — Test Coverage

- Unit tests for `parse_threats_findings` round-trip: 3 paths (field absent, field present with single record, field present with multi-record).
- Unit tests for validation: 3 paths (bad `taxonomy`, bad `relationship`, bad `id`).
- Integration test: SC-2 byte-identity check against the 5 non-agentic example baselines runs green under `SOURCE_DATE_EPOCH=1700000000`.
- Referential-integrity test (FR-3 last bullet): sample-fixture `taxonomy` values all resolve; sample-fixture `id`s all resolve.

### FR-5 — Per-Feature ADR

- A public `docs/architecture/02_ADRs/ADR-NNN-source-attribution-schema-extension.md` is committed per Feature 180 precedent: **Proposed at Day 1 Wave 1 schema-lock**, **Accepted at Day 2-3** with a provisional merge-date, **SHA fill** at post-merge.
- ADR body MUST document:
  1. The additive-optional-field decision and its ADR-026 lineage (including the first-array-of-records precedent claim).
  2. The serialization-surface choice from Q1 (cell-string vs YAML sidecar vs frontmatter vs new section).
  3. The 5-value `taxonomy` enum scope restriction (exclude tachi-internal taxonomies) and its rationale.
  4. The `relationship` 3-value enum and its default-to-`primary` rule.
  5. The referential-integrity contract with `schemas/taxonomy/`.
  6. The zero-edit invariant on the 11 threat-detection agents (SC-7).

### FR-6 — Zero-Edit Invariant on Threat Agents + Skill References (SC-7 Guard)

Per the ADR-023 governance scope, the "zero-edit invariant" covers **both** the agent files and the companion skill-reference files:

- **11 agent files**: No file under `.claude/agents/tachi/stride/` (6 files: spoofing, tampering, repudiation, info-disclosure, denial-of-service, privilege-escalation) or `.claude/agents/tachi/ai/` (5 files: prompt-injection, data-poisoning, model-theft, tool-abuse, agent-autonomy) is modified in the F-A2 PR.
- **11 skill-reference files**: No file under `.claude/skills/tachi-{agent-name}/references/detection-patterns.md` (one per agent) is modified in the F-A2 PR.

F-A2 establishes the *schema contract*. F-A3 is where threat agents and their skill references gain instructions to populate `source_attribution`. Keeping these concerns in separate features preserves the Feature 082 zero-edit invariant across both the agent-file tier and the skill-reference tier, and makes F-A2 independently reviewable.

---

## 🚀 Non-Functional Requirements

### Performance

- Parse-time overhead of reading `source_attribution` on a finding with ≤10 records MUST NOT exceed 5ms per finding (informational floor — matches Feature 180 SC-013 parse-perf bound style). Not CI-enforced.
- Aggregate: parsing a threats.md with 100 findings each carrying 3 `source_attribution` records MUST complete in <500ms on commodity hardware.

### Reliability

- Backward compatibility: 5 existing non-agentic example PDFs byte-identical (SC-2).
- The 6th example (`agentic-app`) follows the Feature 128 convention — may regenerate byte-identically or may be re-baselined with the agentic-app multi-agent extensions; out of scope for F-A2.
- Graceful absence: findings without `source_attribution` remain valid schema-1.5 documents.

### Security

- No security-relevant data introduced. The `source_attribution` field cites *public* framework IDs; it introduces no secrets, credentials, or PII.
- Validation-error messages MUST NOT leak fixture content beyond the finding ID and the bad value + closed-domain.

### Compatibility

- Python stdlib-only runtime (per Feature 128 precedent). `pyyaml` and `pytest` are already declared in `requirements-dev.txt` per Feature 128.
- No npm / Node.js dependency additions.

---

## 📊 Success Metrics

### Primary (Leading)

- **Metric 1 — Schema adoption gate**: `schemas/finding.yaml` head contains `schema_version: "1.5"`.
- **Metric 2 — Parser round-trip gate**: unit tests for absent/present/multi-record paths all green.
- **Metric 3 — Backward-compat gate**: SC-2 byte-identity regression test green across 5 baselines.
- **Metric 4 — Referential-integrity gate**: sample-fixture `taxonomy` values all resolve into F-A1 catalogs.
- **Metric 5 — ADR gate**: public per-feature ADR committed with Proposed → Accepted dual-commit pattern (mirrors F-A1 Feature 180 precedent).

### Secondary (Lagging — Measured in F-A3 / F-B)

- **Metric 6 — Downstream consumption readiness**: F-A3 and F-B authors can reference `source_attribution` as a stable contract surface without asking clarifying questions about shape, optionality, or validation semantics.
- **Metric 7 — Adopter resolution path**: an adopter who asks "which findings address OWASP LLM05?" can answer it with a single `yaml.safe_load` + list-comprehension against `source_attribution`, no markdown prose parsing required. (Measured when F-A3 wires populators — F-A2 ships the field-shape F-A3 needs.)

---

## 🔍 Scope & Boundaries

### In Scope (MVP)

**Must Have (P0)**:
- ✅ `schema_version: "1.5"` bump in `schemas/finding.yaml`.
- ✅ New optional `source_attribution` field, array-of-records shape, 5-value `taxonomy` enum, 3-value `relationship` enum.
- ✅ `parse_threats_findings` round-trip support (present/absent/multi-record paths).
- ✅ Parser-level enum validation (bad `taxonomy`, bad `relationship` → clear errors).
- ✅ Referential-integrity validation against F-A1 YAMLs (phase TBD per Q2).
- ✅ Unit tests (round-trip + validation).
- ✅ Backward-compat integration test (SC-2).
- ✅ Public per-feature ADR.

### Out of Scope (Deferred)

**Could Have (P2) — Deferred to F-A3**:
- 🔮 **Populators** — threat-detection agents emitting `source_attribution` values during detection. F-A2 establishes the contract; F-A3 wires the producers. Deferred because SC-7 requires zero edits to the 11 threat agents in F-A2 to preserve the Feature 082 zero-edit invariant.
- 🔮 **Downstream consumer propagation** — `risk-scorer`, `control-analyzer`, `threat-report`, SARIF exporter, Typst templates all ignore `source_attribution` after F-A2 merges. F-A3 wires them. Deferred because the *first-array-of-records precedent* needs to settle in the ADR before we commit to a propagation pattern.
- 🔮 **Coverage aggregation report** — F-B is the feature that JOINs `source_attribution` against F-A1 crosswalk to produce per-framework coverage narrative.

**Won't Have — Explicitly Excluded**:
- ❌ Bi-directional framework references (i.e., the 2 tachi-internal taxonomies from F-A1). Rationale: F-A2's `taxonomy` enum is 5-value (external frameworks only). Internal tachi taxonomies are the *recipient* side of F-A1's crosswalk edges, not a framework tachi claims coverage of. Adding them would leak internal vocabulary into adopters' coverage claims.
- ❌ SARIF exporter changes. Deferred to F-A3 — the SARIF rendering of `source_attribution` is a separate design question (tag vs property vs nested object) that benefits from a populated corpus to test against.
- ❌ Typst PDF report rendering changes. Same rationale as SARIF.
- ❌ `threats.md` Section 7 column additions. The Section 7 table is the *highest-visibility surface*; changing it is a visual-change decision separate from the data-contract decision F-A2 establishes.
- ❌ Schema-rename or enum-value-change breaking changes on existing 1.4 fields. F-A2 is additive-only.

### Assumptions

- **A1**: F-A1 (Feature 180) is committed to main and the 7 taxonomy YAMLs are in `schemas/taxonomy/` (verified 2026-04-17 via `git log` — squash commit `8b7c7bf`).
- **A2**: `agentic_pattern` (Feature 142, schema 1.4) is the current head; F-A2 is the next schema bump (1.4 → 1.5).
- **A3**: ADR-026's minor-bump rule extends cleanly from scalar-enum fields (its Feature 142 origin) to array-of-records fields; the F-A2 ADR will name this extension explicitly as a precedent.
- **A4**: The 5-value `taxonomy` enum (external frameworks only) is the right scope restriction; the 2 tachi-internal taxonomies are excluded by design.

### Constraints

- **Technical**: Python stdlib-only runtime. No new npm/Node dependencies.
- **Backward-compat**: SC-2 (5 baselines byte-identical) is a BLOCKER if regressed.
- **Governance**: Option C per SDR-001 — public per-feature ADR on merge, mirroring F-A1/Feature 180's Proposed → Accepted dual-commit pattern.
- **Scope discipline**: SC-7 zero-edit invariant on threat-detection agents is a BLOCKER if regressed.

---

## 🛣️ Timeline & Milestones

### Phase Breakdown

**Day 1 (2026-04-20 Monday) — Schema Lock + Serialization Decision**
- Q1 + Q2 resolution memo lands (architect) in ADR Proposed commit
- `schemas/finding.yaml` 1.4 → 1.5 diff authored (senior-backend-engineer — partial parallelism, Q1-independent scaffolding)
- Unit-test fixture authoring begins (tester)

**Day 2 (2026-04-21 Tuesday) — Parser + Validation**
- `parse_threats_findings` round-trip implementation (senior-backend-engineer)
- Parser-level enum validation (bad `taxonomy`, bad `relationship`)
- Referential-integrity implementation per Q2 resolution (senior-backend-engineer + architect)

**Day 3 (2026-04-22 Wednesday) — Integration + ADR Accepted**
- SC-2 byte-identity regression test green across 5 baselines (**tester primary**, senior-backend-engineer secondary for failure diagnostics)
- ADR transitioned Proposed → Accepted (architect)
- Quality checklist pass, PR submitted

### Key Milestones

| Milestone | Target Date | Owner | Status |
|-----------|-------------|-------|--------|
| PRD Approval | 2026-04-17 (Friday) | product-manager | 🟡 In Review |
| Spec Complete | 2026-04-20 (Mon, Day 1 AM) | architect | 📋 Pending |
| ADR-NNN Proposed + Q1/Q2 Memo | 2026-04-20 (Mon, Day 1) | architect | 📋 Pending |
| Schema + Parser Implementation | 2026-04-21 (Tue, Day 2) | senior-backend-engineer | 📋 Pending |
| SC-2 Regression Green (5 baselines) | 2026-04-22 (Wed, Day 3 AM) | **tester** (primary), senior-backend-engineer (secondary) | 📋 Pending |
| ADR-NNN Accepted + PR Merged | 2026-04-22 (Wed, Day 3 PM) | architect | 📋 Pending |

---

## ⚠️ Risks & Dependencies

### Technical Risks

**Risk R1 — Serialization-surface choice regresses SC-2**
- **Likelihood**: Medium
- **Impact**: High (blocks delivery until resolved)
- **Mitigation**: Q1 resolves the serialization-surface choice **before** schema YAML authoring begins. The cell-string option (Q1-A) and the sidecar option (Q1-B) have materially different SC-2 impact footprints — cell-string adds a column to the Section 7 markdown table (which the 5 baselines' rendered PDFs reflect byte-identically only if the column is absent from empty-attribution findings and added only when populated). Sidecar has zero rendered-PDF impact but introduces a new artifact file per run.
- **Contingency**: If Q1-A (cell-string) is chosen and SC-2 regresses, fall back to Q1-B (sidecar) mid-flight with a spec amendment — precedent for mid-flight scope amendments: Feature 180 pm_signoff_amendment_2.

**Risk R2 — List-of-RECORD is the first of its kind; downstream consumers carry latent assumptions that only scalar fields or list-of-STRING fields exist**
- **Likelihood**: Medium
- **Impact**: **High** (aggregated across SARIF tag-shape, Typst rendering, and `extract-report-data.py`'s data-variable contract — three independent surfaces each needing a design decision in F-A3)
- **Mitigation**: The F-A2 ADR names the Complex-Shape Addition Clarifier under ADR-026 (per FR-1 framing), and F-A3 PRD will carry a dedicated design section for each of the 3 downstream surfaces: SARIF (tag-list vs `result.properties` nested object), Typst PDF (how does the report render a multi-framework citation?), and `extract-report-data.py` (how does the data variable carry the nested list?). The list-of-STRING precedent (`references: list[string]` since schema 1.0) partially mitigates — SARIF already has a strategy for list-typed fields.
- **Contingency**: If F-A3 surfaces a consumer that cannot trivially handle list-of-records, F-A3 may introduce a projection helper (`flatten_source_attribution(finding) → str`) without requiring a schema re-shape in F-A2. Sizing High rather than Medium here is deliberate — Medium undersized the combinatorial effort across 3 independent consumer surfaces.

**Risk R3 — Referential-integrity validation bloats parse-time by loading all 7 F-A1 YAMLs on every finding**
- **Likelihood**: Low
- **Impact**: Low
- **Mitigation**: Q2 resolution either (a) defers referential-integrity to a separate validation phase (parser is fast; validation is a separate pass), or (b) caches F-A1 YAML loads across findings in a single parser invocation.

**Risk R4 — Issue body specifies `schema_version 1.3 → 1.4` but current head is 1.4**
- **Likelihood**: Certain — this is a documented fact from reading `schemas/finding.yaml` head
- **Impact**: Low — caught before spec authoring
- **Mitigation**: PRD corrects the version-bump wording to `1.4 → 1.5` (Open Question Q4). ADR will document the correction explicitly.
- **Contingency**: None needed; pre-spec correction.

### Business Risks

**Risk R5 — F-A2 ships without populators; adopters see schema 1.5 but no populated `source_attribution` in example outputs**
- **Likelihood**: Certain by scope design (populators are F-A3, not F-A2)
- **Impact**: Medium — may generate "what's this for?" confusion if adopters see schema 1.5 without data in example outputs
- **Mitigation**: The per-feature ADR explicitly frames F-A2 as the contract-only feature, with F-A3 as the populator. The `examples/` baselines continue producing empty `source_attribution` (or absent — per FR-2 precedent) until F-A3 wires populators.
- **Contingency**: Consider hand-authoring 2-3 sample `source_attribution` records on the agentic-app example as an illustrative demonstration. Out of scope for F-A2 MVP; track as a follow-on Issue if adopter confusion surfaces.

### Dependencies

**Internal**:
- **F-A1 (Feature 180) — schemas/taxonomy/**: **SATISFIED** as of 2026-04-17.
- **ADR-026** (Feature 142): SATISFIED — provides the minor-bump rule F-A2 extends.
- **ADR-021** (byte-determinism): SATISFIED — SC-2 regression gate uses the harness.

**External**: None. F-A2 introduces no runtime dependencies.

---

## ❓ Open Questions

### Product Questions

- [x] **Q-P1 — Demonstrate `source_attribution` on at least one example?** — **Resolved: NO** (per team-lead review). Sample records belong in test fixtures under `tests/scripts/fixtures/`, not in example outputs. Example outputs are shipped byte-deterministically under `SOURCE_DATE_EPOCH=1700000000`; introducing sample `source_attribution` data into an example output would mix the F-A2 contract-only feature with the F-A3 populator feature. If adopter confusion surfaces post-merge, track as a follow-on Issue. — Owner: product-manager — Status: **Resolved** 2026-04-17.

### Technical Questions (Critical — Block Spec Authoring)

- [ ] **Q1 — Serialization surface for `source_attribution` in `threats.md`.** The parser currently reads Section 7 as a markdown table; a single cell cannot natively hold a list-of-records.

  **Options narrowed post-architect-review** (Q1-A cell-string and Q1-D new-Section-8-that-modifies-rendered-PDF are **REJECTED** — they violate the Won't-Have scope line on Section 7 column changes and/or trigger SC-2 regression):
  - ~~Q1-A (cell-string)~~: REJECTED — brittle string parsing, violates Won't-Have scope.
  - **Q1-B (YAML sidecar)**: New file `threats-attribution.yaml` co-emitted with `threats.md`. Pro: clean data surface, zero-PDF-impact; Con: new artifact file, parser reads two files.
  - **Q1-C (frontmatter)**: Embed as a YAML block at the top of `threats.md`. Pro: one file; Con: frontmatter is already used for baseline metadata (Feature 104); nesting attribution under baseline frontmatter or as a sibling block needs a design choice.
  - ~~Q1-D (new Section 8 rendering in PDF)~~: REJECTED — triggers SC-2 regression.
  - **Q1-E (architect-recommended — new Section 9 YAML block keyed by finding ID)**: Add a new conditional Section 9 to `threats.md` that contains a YAML code-fence block keyed by finding ID (e.g., ````yaml\nS-1:\n  - {taxonomy: owasp, id: LLM05}\n```). Gated like Feature 141's `has-attack-chains` boolean — the section is omitted when zero findings have `source_attribution`, preserving SC-2 on the 5 current baselines. Pro: threats.md remains single source of truth, parses via `yaml.safe_load` on the fenced block, zero-PDF-impact when gated-off, gating precedent matches Feature 141. Con: adds a new section to the output schema (but conditionally — no baseline regression).

  **Recommendation** (architect-owned, per the architect-review):
  - **Q1-E (primary)**: new Section 9 YAML block gated like Feature 141's `has-attack-chains`. Fallback: **Q1-B (YAML sidecar)**.
  - Owner: **architect** — Due: **2026-04-20** (Day 1 schema lock) — Status: Awaiting architect decision memo.

- [ ] **Q2 — Referential-integrity check phase.** **Q2-B (separate validation phase) is architect-preferred per review.** Parser stays thin (enum membership only); a separate `validate_source_attribution(findings)` helper performs F-A1 YAML lookups. Orchestrator Phase 4 is the canonical caller for the validation pass. Decision still requires Day 1 architect memo to formalize. — Owner: **architect** — Due: 2026-04-20 — Status: Architect-preferred option identified (Q2-B); memo pending.

- [ ] **Q3 — ADR number assignment.** The F-A1 ADR is ADR-027. F-A2's ADR will be ADR-028 unless another ADR lands between now and F-A2 PR. — Owner: architect — Due: 2026-04-20 — Status: TBD (mechanical assignment at Proposed commit).

### Process Questions

- [x] **Q4 — Schema version bump wording.** Issue #189 body says `1.3 → 1.4`; current head is `1.4`. **Resolved in this PRD**: target is `1.4 → 1.5`. ADR MUST document the correction. — Owner: product-manager — Status: **Resolved** (flagged in US-189-1 AC-1 and FR-1).

---

## 📚 References

### Product Documentation

- Vision: `docs/product/01_Product_Vision/product-vision.md`
- BLP-01 initiative memory: `/Users/david/.claude/projects/-Users-david-Projects-tachi/memory/project_blp01_threat_coverage.md`
- GitHub Issue: [#189](https://github.com/davidmatousek/tachi/issues/189)

### Precedent PRDs

- Feature 180 (F-A1, delivered 2026-04-17): `docs/product/02_PRD/180-taxonomy-crosswalk-collection-2026-04-17.md`
- Feature 142 (schema 1.3 → 1.4 minor bump for `agentic_pattern`): `docs/product/02_PRD/142-maestro-agentic-pattern-expansion-2026-04-16.md`
- Feature 084 (schema 1.1 → 1.2, `maestro_layer` precedent for additive optional fields): `docs/product/02_PRD/084-maestro-layer-mapping-2026-04-07.md`
- Feature 104 (backward-compat baseline field pattern): `docs/product/02_PRD/104-downstream-baseline-propagation-2026-04-08.md`

### Technical References

- Schema head: `schemas/finding.yaml` (current `schema_version: "1.4"`)
- Parser target: `scripts/tachi_parsers.py::parse_threats_findings` (line 621)
- F-A1 framework YAMLs: `schemas/taxonomy/{owasp,mitre-attack,mitre-atlas,nist-ai-rmf,cwe,tachi-control-category,tachi-stride-ai-category}.yaml`
- F-A1 crosswalk: `schemas/taxonomy/crosswalk.yaml` (526 edges)
- Backward-compat harness: `tests/scripts/test_backward_compatibility.py`

### ADR Lineage

- ADR-020: MAESTRO layer classification (additive optional scalar enum precedent)
- ADR-021: `SOURCE_DATE_EPOCH` determinism convention
- ADR-023: Skill-references pattern for agents
- ADR-026: Minor-bump rule for NEW enum-typed field additions (extends to array-of-records in F-A2)
- ADR-027 (F-A1, Feature 180): Taxonomy crosswalk schema + single-feature cadence exception

---

## ✅ Approval & Sign-Off

### PRD Review Checklist

**Product Manager**:
- [x] Problem statement is clear and user-focused
- [x] User stories have measurable acceptance criteria
- [x] Success metrics are defined and measurable (SC-1 through SC-7)
- [x] Scope is realistic for 2-3 day timeline
- [x] Risks and dependencies identified
- [x] Aligns with BLP-01 initiative and product vision
- [x] Stale Issue-body `schema_version` wording corrected (Q4)
- [x] Zero-edit invariant on threat agents explicitly preserved (SC-7, FR-6)

**Architect**:
- [ ] Technical requirements are clear
- [ ] Q1 (serialization surface) has a defensible resolution
- [ ] Q2 (referential-integrity phase) has a defensible resolution
- [ ] First-array-of-records precedent is named in ADR
- [ ] Parser round-trip design is sound
- [ ] SC-2 regression approach is sound

**Engineering Lead** (team-lead):
- [ ] 2-3 day timeline is realistic
- [ ] Q1 resolution is on critical path (Day 1)
- [ ] Team capacity is available
- [ ] Risks have mitigation plans

### Approval Status

| Role | Name | Status | Date | Comments |
|------|------|--------|------|----------|
| Product Manager | product-manager | ✅ Approved | 2026-04-17 | Q4/Q-P1 resolved; Issue-body 1.3→1.4 wording corrected to 1.4→1.5 |
| Architect | architect | 🟡 Approved with Concerns | 2026-04-17 | Q1-E added, Q2-B narrowed, list-of-record framing corrected, Risk R2 upsized, SC-7 enumeration expanded |
| Engineering Lead | team-lead | 🟡 Approved with Concerns | 2026-04-17 | Calendar fix to 2026-04-20, tester primary for SC-2 regression, Q1-A/D eliminated |

---

## 📝 Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-04-17 | product-manager | Initial PRD — 3 user stories sourced from Issue #189 body; stale `1.3 → 1.4` wording corrected to `1.4 → 1.5`; serialization-surface design question surfaced as Q1 (architect-owned, Day 1 critical path); first-list-of-record precedent noted for ADR. |
| 1.1 | 2026-04-17 | product-manager | Post-review inline absorption — (a) Q1-E added (new Section 9 YAML block gated like Feature 141 `has-attack-chains`) as architect-recommended surface; Q1-A (cell-string) and Q1-D (new Section 8 rendered in PDF) rejected; (b) Q2 narrowed to Q2-B (separate validation phase, orchestrator Phase 4 caller); (c) list-of-record framing corrected — `references: list[string]` is the list-typed precedent, F-A2 is first list-of-RECORD; Complex-Shape Addition Clarifier named under ADR-026; (d) Risk R2 impact upsized Medium → High (combinatorial across SARIF / Typst / `extract-report-data.py` in F-A3); (e) FR-6/SC-7 enumerated 11 agent files + 11 skill-reference files per ADR-023 governance scope; (f) calendar fix — Day 1 = 2026-04-20 Monday (not 2026-04-18 Saturday); (g) Milestones table — tester primary for SC-2 regression, senior-backend-engineer secondary for failure diagnostics; (h) Q-P1 resolved NO (sample records belong in test fixtures, not example outputs). |
