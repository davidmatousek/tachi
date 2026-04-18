---
prd_reference: docs/product/02_PRD/189-source-attribution-schema-extension-2026-04-17.md
triad:
  pm_signoff:
    agent: product-manager
    date: 2026-04-17
    status: APPROVED
    notes: "1:1 PRD-to-spec mapping verified via mapping table (lines 185-197); all 3 US + 7 SC + 6 FR preserved and decomposed into spec FR-001..FR-016. Scope discipline clean: populators/F-A3 deferred, Q-P1 fixtures-not-examples honored in A5 + Out-of-Scope, 22-file zero-edit scope enumerated grep-auditably in FR-015. Q1/Q2 surface-and-phase-neutrality correctly handled via FR-007/FR-008/FR-010 so architect memo does not force spec revision. Every AC is Given/When/Then with concrete inputs. Edge cases surface empty-vs-absent and duplicate-record distinctions. User value traceability clean — every US ties to F-A3/F-B/ecosystem-integrator consumer. Ready for /aod.project-plan."
  architect_signoff: null  # Added by /aod.project-plan
  techlead_signoff: null   # Added by /aod.tasks
---

# Feature Specification: Source Attribution Schema Extension (F-A2)

**Feature Branch**: `189-source-attribution-schema-extension`
**Created**: 2026-04-17
**Status**: Draft
**Input**: User description: "PRD: 189 - source-attribution-schema-extension"

---

## Overview

Extend `schemas/finding.yaml` with an optional `source_attribution` field — an array of `{taxonomy, id, relationship}` records — that lets every tachi threat finding carry a machine-readable list of the external compliance-framework items it addresses. The feature ships the **data-shape contract** only: populators (F-A3) and the coverage attestation report (F-B) are explicit downstream scope boundaries.

This is the 2nd feature in the BLP-01 Foundation tier, immediately following F-A1 (Feature 180, delivered 2026-04-17). F-A1 shipped the machine-readable taxonomy catalogs; F-A2 ships the finding-side bridge to those catalogs. Together they make framework-coverage claims aggregable rather than free-text prose.

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 — Multi-Framework Citation on a Single Finding (Priority: P1)

A threat agent emits a finding that spans multiple compliance-framework items simultaneously — for example, an LLM output-handling threat that legitimately addresses OWASP LLM05, CWE-1426, and MITRE ATLAS AML.T0051. Today the agent can only cite these as free-text strings in `mitigation` or `references` prose. After F-A2, the agent can attach an ordered `source_attribution` array listing all three items in a single structured field, without duplicating the finding row.

**Why this priority**: Without the structured array, every adopter building a coverage dashboard must re-invent text-parsing to aggregate citations. The structured array is the contract every downstream consumer (F-A3 populators, F-B coverage attestation, ecosystem integrations) depends on.

**Independent Test**: Hand-author a fixture `threats.md` with one finding carrying three `source_attribution` records, run `parse_threats_findings`, and assert that all three records round-trip with the exact input order, taxonomy values, IDs, and relationship values. No other feature work is required to validate.

**Acceptance Scenarios**:

1. **Given** `schemas/finding.yaml` at head of the F-A2 PR, **when** a developer reads the `schema_version` line, **then** the value equals exactly `"1.5"` — a minor bump from the current head `"1.4"`.
2. **Given** a finding YAML document that omits `source_attribution`, **when** the document is validated against schema 1.5, **then** the document is valid (field is optional; absence is backward-compatible).
3. **Given** a finding YAML document that includes `source_attribution: [{taxonomy: owasp, id: LLM05, relationship: primary}, {taxonomy: cwe, id: CWE-1426, relationship: primary}, {taxonomy: mitre-atlas, id: AML.T0051, relationship: primary}]`, **when** the document is validated and parsed, **then** the three records are preserved in parser output in input order with all three fields per record intact.

---

### User Story 2 — Parser Round-Trip Preserves Backward Compatibility (Priority: P1)

A pipeline developer runs the full tachi pipeline against any of the 5 existing non-agentic example architectures (`web-app`, `microservices`, `ascii-web-api`, `mermaid-agentic-app`, `free-text-microservice`) and expects the regenerated PDF to be byte-identical to its committed baseline. None of these architectures carry `source_attribution` today, so the F-A2 change must be truly additive with zero cross-cutting side effects.

**Why this priority**: The byte-identity gate on 5 baselines is tachi's proven backward-compatibility harness per ADR-021. A regression here means F-A2 silently changed an output surface unrelated to its scope — the single most common failure mode for additive schema changes. This story is the guardrail that catches such regressions before merge.

**Independent Test**: Run `tests/scripts/test_backward_compatibility.py` under `SOURCE_DATE_EPOCH=1700000000` against the 5 committed baselines. All 5 must match byte-for-byte. No synthetic attribution data is introduced into any example output.

**Acceptance Scenarios**:

1. **Given** a `threats.md` file that does NOT carry `source_attribution` on any finding, **when** `parse_threats_findings(content)` is called, **then** every returned finding object OMITS the `source_attribution` key entirely — no implicit `[]` default is injected (conditional-key precedent per Feature 104 `delta_status`).
2. **Given** a `threats.md` file that carries `source_attribution` on one or more findings via the serialization surface resolved in Q1, **when** `parse_threats_findings(content)` is called, **then** every affected finding object contains the `source_attribution` key with an array whose length, order, and per-record `{taxonomy, id, relationship}` structure match the input verbatim.
3. **Given** the 5 committed non-agentic example PDF baselines at `examples/{web-app,microservices,ascii-web-api,mermaid-agentic-app,free-text-microservice}/security-report.pdf.baseline`, **when** the full pipeline regenerates each PDF under `SOURCE_DATE_EPOCH=1700000000`, **then** all 5 regenerated PDFs are byte-identical to their baselines.

---

### User Story 3 — Closed-Enum `relationship` with Referential Integrity (Priority: P1)

A coverage auditor consuming a `source_attribution` array downstream needs to distinguish primary citations (the finding's canonical framework mapping) from related or derived citations (adjacent mappings that add context but should not be weighted equally in coverage-percentage computations). The `relationship` enum makes this distinction data-shaped. In parallel, a referential-integrity check guarantees every cited `{taxonomy, id}` pair actually resolves to a record in F-A1's catalog YAMLs.

**Why this priority**: Closed enums plus referential integrity are what turn the field from "a list of strings that happen to look structured" into "a contract downstream consumers can trust." Without the enum, every consumer re-invents relationship vocabulary. Without referential integrity, citations can drift away from F-A1 catalogs silently and coverage claims become aspirational rather than verifiable.

**Independent Test**: Hand-author three fixture findings — one with a bad `taxonomy` value, one with a bad `relationship` value, one with a bad `id` value that does not resolve in the referenced taxonomy YAML. Run validation. Each fixture must produce a clear error naming the finding ID, the bad value, and the closed-domain or target-YAML context.

**Acceptance Scenarios**:

1. **Given** a finding with `source_attribution: [{taxonomy: owasp, id: LLM05}]` (no `relationship` field), **when** parsed, **then** the returned record has `relationship` defaulted to `primary`.
2. **Given** a finding with `source_attribution: [{taxonomy: owasp, id: LLM05, relationship: fabricated_value}]`, **when** parsed, **then** a validation error surfaces identifying the finding ID, the bad `relationship` value, and the closed domain `{primary, related, derived}`.
3. **Given** a finding with `source_attribution: [{taxonomy: not-a-real-taxonomy, id: X}]`, **when** parsed, **then** a validation error surfaces identifying the finding ID, the bad `taxonomy` value, and the closed domain `{owasp, mitre-attack, mitre-atlas, nist-ai-rmf, cwe}`.
4. **Given** a finding with `source_attribution: [{taxonomy: owasp, id: NOT-A-REAL-OWASP-ID}]` AND referential-integrity check enabled per Q2 resolution, **when** validated, **then** an error surfaces identifying the finding ID, the bad `id`, and the YAML file in `schemas/taxonomy/` that was searched (`schemas/taxonomy/owasp.yaml`).

---

### Edge Cases

- **Empty array vs absent field**: `source_attribution: []` (present but empty) MUST round-trip as an empty array (no coercion to absent-key); absent field MUST round-trip as absent-key (no coercion to `[]`). These are two distinct states with different semantic meaning: "explicitly no attribution claimed" vs "no claim made."
- **Duplicate records within a single finding**: two records with identical `{taxonomy, id, relationship}` in the same `source_attribution` array — parser preserves both verbatim (no silent deduplication). If product policy wants deduplication, it lives in a future F-A3 populator contract, not in F-A2's parser.
- **Very large arrays**: >10 records per finding. Performance floor is informational (≤5ms per finding with ≤10 records), not CI-enforced. Arrays larger than 10 are not prohibited but are outside the measured performance profile.
- **Mixed populated/empty findings in one threats.md**: some findings carry `source_attribution`, others do not. Per US-2 AC-1, parser omits the key on absent-path findings and includes it on present-path findings — no global "all or none" convention.
- **Whitespace and case in enum values**: all enum values (taxonomy and relationship) are lowercase-hyphen-separated per the F-A1 convention. Values like `OWASP` or `Primary` or `mitre_attack` fail validation with the standard closed-domain error.
- **Referential-integrity with empty array**: if `source_attribution: []`, no record exists to check — validation passes trivially.
- **Unknown vs stale taxonomy IDs**: "stale" IDs (valid yesterday, removed from F-A1 catalog today) produce the same error as "never existed" IDs — the referential-integrity check is state-based, not history-aware.
- **`agentic-app` example regeneration**: the 6th example follows the Feature 128 convention — it may regenerate byte-identically or may be re-baselined if the agentic-app extensions surface `source_attribution` via a follow-on populator. Out of scope for F-A2 MVP.

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: `schemas/finding.yaml` MUST declare `schema_version: "1.5"` at its head, a minor bump from the current `"1.4"`.
- **FR-002**: `schemas/finding.yaml` MUST define a new optional field `source_attribution` whose type is an array of records. Each record MUST have exactly three string fields: `taxonomy`, `id`, `relationship`.
- **FR-003**: The `taxonomy` field MUST accept only values from the closed 5-value enum `{owasp, mitre-attack, mitre-atlas, nist-ai-rmf, cwe}` — the external-framework subset of F-A1's 7-value taxonomy enum (internal taxonomies `tachi-control-category` and `tachi-stride-ai-category` are deliberately excluded).
- **FR-004**: The `relationship` field MUST accept only values from the closed 3-value enum `{primary, related, derived}`. When the field is omitted on a record, the parser MUST default it to `primary`.
- **FR-005**: The `id` field MUST be a non-empty string. Format validation is performed by the referential-integrity lookup (FR-008), not by a regex or other syntactic rule on this field in isolation.
- **FR-006**: The `source_attribution` field MUST be optional at the field level. A finding that does not cite any framework item MUST NOT carry the field at all — no implicit default of `[]` is injected when absent. This preserves the Feature 104 conditional-key precedent used for `delta_status`.
- **FR-007**: `scripts/tachi_parsers.py::parse_threats_findings` MUST round-trip the `source_attribution` field. When the field is absent from input, the parser MUST omit the key on the returned finding object. When the field is present, the parser MUST emit it with the array's length, order, and per-record structure preserved.
- **FR-008**: The pipeline MUST provide referential-integrity validation that asserts every `source_attribution` record's `id` resolves as a top-level `id` in `schemas/taxonomy/{taxonomy}.yaml`. The **phase** at which this validation runs — inline in the parser, or as a separate validation helper invoked post-parse — is resolved by architect Open Question Q2. The spec is neutral on the phase; FR-008 fixes the contract.
- **FR-009**: Parser-level enum validation MUST surface a clear, actionable error for each invalid value it encounters. Error messages MUST identify (a) the affected finding ID, (b) the bad value, and (c) the closed-domain list for the field. Referential-integrity errors MUST additionally name the target YAML path in `schemas/taxonomy/`.
- **FR-010**: The serialization surface — where in `threats.md` (or a co-emitted artifact) `source_attribution` is carried so that `parse_threats_findings` can round-trip it — is resolved by architect Open Question Q1. The spec is neutral on the surface; FR-007 and the SC-2 byte-identity gate constrain the acceptable shape (the surface MUST NOT regress the 5 non-agentic baselines).
- **FR-011**: Unit-test coverage MUST include three round-trip paths (field absent, field present with single record, field present with multi-record) and three validation paths (bad `taxonomy`, bad `relationship`, bad `id`).
- **FR-012**: An integration test MUST enforce the SC-2 byte-identity invariant across the 5 non-agentic example baselines under `SOURCE_DATE_EPOCH=1700000000` per ADR-021.
- **FR-013**: Referential-integrity test coverage MUST assert that every sample-fixture `taxonomy` value keys into one of the 5 F-A1 framework YAMLs AND every sample-fixture `id` resolves as a record in the named YAML AND every sample-fixture `relationship` value is a member of the closed 3-value enum.
- **FR-014**: A new per-feature ADR MUST be committed following the Feature 180 / F-A1 **Proposed → Accepted dual-commit** pattern: authored Proposed at Day 1 Wave 1 schema-lock; transitioned Accepted at PR merge with provisional merge-date; merge-commit SHA fill post-merge. The ADR MUST document six items — the additive-optional-field decision and its ADR-026 lineage (naming the Complex-Shape Addition Clarifier extension for list-of-RECORD fields); the serialization-surface choice resolved per Q1; the 5-value `taxonomy` enum scope restriction and its rationale; the `relationship` 3-value enum with default-to-`primary`; the referential-integrity contract with `schemas/taxonomy/`; and the zero-edit invariant on the 11 threat-detection agents plus their 11 companion skill-reference files.
- **FR-015**: The F-A2 PR MUST NOT edit any file under `.claude/agents/tachi/stride/` (6 files) or `.claude/agents/tachi/ai/` (5 files) or any file under `.claude/skills/tachi-{stride-or-ai-agent-name}/references/detection-patterns.md` (11 files). **Total zero-edit scope: 22 files** per ADR-023 governance. F-A2 is the contract feature; F-A3 is the populator feature that may edit these surfaces.
- **FR-016**: The F-A2 PR MUST NOT add any runtime dependency. `pyproject.toml`, `requirements.txt`, `requirements-dev.txt`, and `package.json` diffs MUST all be empty (`pyyaml` and `pytest` are already declared in `requirements-dev.txt` per Feature 128; no other additions are permitted).

### Key Entities

- **Finding (extended)**: The atomic unit of threat analysis output, defined in `schemas/finding.yaml`. In schema 1.5, each Finding gains an optional `source_attribution` field. All existing fields are preserved unchanged; no field is removed, renamed, or reshaped.
- **SourceAttributionRecord (new)**: A three-field record `{taxonomy, id, relationship}`. `taxonomy` identifies which F-A1 framework catalog the citation points into. `id` is the taxonomy-internal identifier. `relationship` characterizes how the finding relates to the cited item — primary (the canonical mapping), related (an adjacent mapping), or derived (a mapping inferred from another citation).
- **Taxonomy (external reference to F-A1)**: One of 5 F-A1 catalog YAMLs (`schemas/taxonomy/owasp.yaml`, `mitre-attack.yaml`, `mitre-atlas.yaml`, `nist-ai-rmf.yaml`, `cwe.yaml`). F-A2 does not modify these files; it references them for referential-integrity validation.

---

## Assumptions

- **A1 — F-A1 shipped**: Feature 180 merged to main 2026-04-17 (commit `8b7c7bf`). The 7 taxonomy YAMLs at `schemas/taxonomy/*.yaml` are present and authoritative.
- **A2 — Schema head is 1.4**: `schemas/finding.yaml:13` currently reads `schema_version: "1.4"` per Feature 142. F-A2's minor bump target is `1.5`.
- **A3 — ADR-026 minor-bump rule extends to list-of-RECORD**: The rule's three conditions (additive, has default, schema shape unchanged) hold for `source_attribution` because the field is optional (default state is "absent"), per-record `relationship` has default `primary`, and the schema document's top-level shape is unchanged.
- **A4 — 5-value `taxonomy` enum is the right scope**: F-A2 cites *external* frameworks only. Internal taxonomies (`tachi-control-category`, `tachi-stride-ai-category`) are tachi's own published vocabulary — they are the recipient side of F-A1 crosswalk edges, not frameworks tachi claims coverage of.
- **A5 — Fixtures, not examples**: Sample `source_attribution` records live under `tests/scripts/fixtures/source_attribution/` per Feature 142 precedent. Example outputs at `examples/` remain byte-deterministic and do not mix F-A2 contract work with F-A3 populator work (PRD Q-P1 resolution).
- **A6 — Orchestrator does NOT auto-populate**: Unlike ADR-020's `maestro_layer` passive overlay, F-A2 does NOT add orchestrator Phase 1 auto-classification. The orchestrator reads `source_attribution` as-provided by threat agents in F-A3; in F-A2 no agent provides it, so all findings in the 5 non-agentic baselines have absent `source_attribution`.
- **A7 — ADR number**: Mechanical assignment at Proposed commit. F-A1 claimed ADR-027 (merged 2026-04-17); F-A2 is ADR-028 unless another ADR lands first.

## Constraints

- **C1 — SC-2 byte-identity regression is a BLOCKER**: any regression in the 5 non-agentic baselines halts merge until resolved.
- **C2 — SC-7 zero-edit invariant is a BLOCKER**: any edit to the 22 files named in FR-015 halts merge until reverted or re-scoped.
- **C3 — Python stdlib-only runtime**: `pyyaml` and `pytest` remain developer-only; no new runtime dependencies.
- **C4 — Governance**: per-feature ADR is public (not sidecar), following the F-A1 Proposed → Accepted dual-commit pattern and documenting six required items per FR-014.
- **C5 — Q1 and Q2 are architect-authority**: the spec does not prejudge Q1 (serialization surface) or Q2 (referential-integrity phase). Both resolve in the Day 1 architect memo and land in the ADR Proposed commit.

---

## Dependencies

**Internal (all SATISFIED)**:
- F-A1 / Feature 180 — `schemas/taxonomy/` directory: delivered 2026-04-17.
- ADR-026 minor-bump rule (Feature 142): Accepted 2026-04-16.
- ADR-021 byte-determinism harness: Accepted (prior feature precedent).
- ADR-023 zero-edit invariant on 11 threat-detection agents + 11 skill references: Accepted (Feature 082).

**External**: None. F-A2 introduces zero runtime or test-runtime dependencies beyond what is already declared.

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: `schemas/finding.yaml` head contains the exact string `schema_version: "1.5"` at the F-A2 PR merge commit.
- **SC-002**: All 5 non-agentic example PDF baselines regenerate byte-identically under `SOURCE_DATE_EPOCH=1700000000`. Measured by `tests/scripts/test_backward_compatibility.py` passing with 5/5 baseline matches.
- **SC-003**: `parse_threats_findings` returns `source_attribution` on a finding only when the input carries it, and omits the key on the returned object when the input does not. Measured by unit tests covering three round-trip paths (absent, single-record, multi-record).
- **SC-004**: Referential-integrity validation surfaces an actionable error for each of the three fixture-authored invalid inputs: bad `taxonomy`, bad `relationship`, bad `id`. Each error names the affected finding ID and the closed-domain (or target YAML path for `id`).
- **SC-005**: A public per-feature ADR is committed with the **Proposed → Accepted dual-commit** pattern. Measured by (a) the ADR body documenting all six required items per FR-014, (b) the ADR status line transitioning from Proposed at Day 1 to Accepted at PR merge, (c) the merge-commit SHA filled in post-merge.
- **SC-006**: Zero new runtime dependencies. Measured by empty diffs on `pyproject.toml`, `requirements.txt`, `requirements-dev.txt`, and `package.json` in the F-A2 PR.
- **SC-007**: Zero edits to the 22-file zero-edit scope (11 agent files + 11 skill-reference files) defined in FR-015. Measured by a grep audit asserting empty diff over the set `.claude/agents/tachi/{stride,ai}/*.md` ∪ `.claude/skills/tachi-{spoofing,tampering,repudiation,info-disclosure,denial-of-service,privilege-escalation,prompt-injection,data-poisoning,model-theft,tool-abuse,agent-autonomy}/references/detection-patterns.md`.

---

## Out of Scope (Deferred)

The following are **not** in F-A2 and are explicitly deferred to downstream features:

- **Populators (F-A3)**: threat-detection agents emitting `source_attribution` values during detection. F-A2 ships the contract; F-A3 wires the producers. Deferred to preserve the 22-file zero-edit invariant (C2 / FR-015).
- **Downstream consumer propagation (F-A3)**: `risk-scorer`, `control-analyzer`, `threat-report`, SARIF exporter, Typst templates all ignore `source_attribution` after F-A2 merges. The PRD Risk R2 captures the combinatorial design surface for these three consumers — each needs a distinct design decision in F-A3, not in F-A2.
- **Coverage aggregation report (F-B)**: the feature that JOINs `source_attribution` against F-A1 crosswalk to produce per-framework coverage narrative.
- **Bi-directional internal-taxonomy references**: the 2 internal F-A1 taxonomies are deliberately excluded from F-A2's 5-value `taxonomy` enum per FR-003.
- **Section 7 column additions in `threats.md`**: the highest-visibility output surface is NOT changed in F-A2. Any visual-surface change is a separate decision from the data-contract decision F-A2 establishes. (Q1-E adds a conditional *new* Section 9 YAML block — architecturally distinct from modifying the existing §7 table.)
- **Schema-rename or enum-value-change breaking changes** on existing schema 1.4 fields. F-A2 is additive-only.
- **Sample `source_attribution` records in example outputs**: deferred to future consideration per PRD Q-P1 (sample records live in test fixtures, not example outputs).

---

## Open Questions

Carried forward from the PRD. **Q1 and Q2 are architect-owned** and resolve in the Day 1 Wave 1 architect memo that lands in the ADR Proposed commit. Spec FR-007, FR-008, and FR-010 are deliberately surface-neutral and phase-neutral so they remain valid regardless of Q1 / Q2 resolution.

- **Q1 (architect)**: Serialization surface for `source_attribution` in the threats.md-related artifact set. PRD narrowed options to **Q1-E (primary: new conditional Section 9 YAML block gated like Feature 141 `has-attack-chains`)** and **Q1-B (fallback: YAML sidecar file)**. Q1-A (cell-string) and Q1-D (new Section 8 rendered in PDF) are rejected per PRD. Due: 2026-04-20 (Day 1).
- **Q2 (architect)**: Referential-integrity validation phase. PRD narrowed to **Q2-B (separate validation phase; parser stays thin; orchestrator Phase 4 is the canonical caller)**. Due: 2026-04-20 (Day 1).
- **Q3 (architect, mechanical)**: ADR number assignment at Proposed commit. Expected ADR-028 unless another ADR lands first. Due: 2026-04-20 (Day 1).

---

## Relationship to PRD

This spec implements PRD 189 (F-A2 Source Attribution Schema Extension) with 1:1 mapping:

| PRD Element | Spec Element |
|-------------|--------------|
| US-189-1 Multi-Framework Citation | User Story 1 (P1) |
| US-189-2 Parser Round-Trip | User Story 2 (P1) |
| US-189-3 Closed-Enum `relationship` | User Story 3 (P1) |
| PRD FR-1 Schema 1.5 | Spec FR-001 (schema_version) + FR-002 (field shape) + FR-003 (taxonomy enum) + FR-004 (relationship enum) + FR-005 (id field) |
| PRD FR-2 Parser Round-Trip | Spec FR-006 (conditional key) + FR-007 (round-trip) + FR-010 (Q1 neutrality) |
| PRD FR-3 Validation Rules | Spec FR-008 (referential integrity) + FR-009 (error messages) |
| PRD FR-4 Test Coverage | Spec FR-011 (unit tests) + FR-012 (integration) + FR-013 (referential integrity) |
| PRD FR-5 Per-Feature ADR | Spec FR-014 |
| PRD FR-6 Zero-Edit Invariant | Spec FR-015 (22 files enumerated) |
| PRD SC-1 through SC-7 | Spec SC-001 through SC-007 (1:1 numeric mapping) |

All three PRD user stories ship as P1 because they are co-dependent for MVP: without US-1, there is no schema shape; without US-2, backward compatibility regresses; without US-3, the field cannot be trusted by downstream consumers. Each, however, is independently testable (see User Story sections' Independent Test descriptors).

---

## References

- **PRD**: `docs/product/02_PRD/189-source-attribution-schema-extension-2026-04-17.md`
- **GitHub Issue**: [#189](https://github.com/davidmatousek/tachi/issues/189)
- **Research**: `specs/189-source-attribution-schema-extension/research.md`
- **F-A1 baseline**: `docs/product/02_PRD/180-taxonomy-crosswalk-collection-2026-04-17.md`
- **ADR-020** (MAESTRO layer — additive-optional-field precedent): `docs/architecture/02_ADRs/ADR-020-maestro-layer-classification.md`
- **ADR-021** (SOURCE_DATE_EPOCH determinism): `docs/architecture/02_ADRs/ADR-021-source-date-epoch-for-deterministic-pdf-comparison.md`
- **ADR-023** (zero-edit invariant for 11 threat agents + 11 skill references): `docs/architecture/02_ADRs/ADR-023-threat-agent-skill-references-pattern.md`
- **ADR-026** (minor-bump rule for NEW enum-typed field additions): `docs/architecture/02_ADRs/ADR-026-pattern-classification-mechanism.md`
- **ADR-027** (F-A1 taxonomy schema): `docs/architecture/02_ADRs/ADR-027-taxonomy-crosswalk-schema.md`
- **Schema head**: `schemas/finding.yaml` (currently 1.4)
- **Parser target**: `scripts/tachi_parsers.py::parse_threats_findings` (line 621)
- **F-A1 YAMLs**: `schemas/taxonomy/{owasp,mitre-attack,mitre-atlas,nist-ai-rmf,cwe}.yaml`
- **Backward-compat harness**: `tests/scripts/test_backward_compatibility.py`
