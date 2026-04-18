# Research Summary: F-A2 Source Attribution Schema Extension (Feature 189)

**Date**: 2026-04-17
**Feature**: 189 — Source Attribution Schema Extension
**Author**: spec authoring phase
**Purpose**: Ground the spec in codebase reality, ADR precedent, and verified file paths — so no FR references a surface that has drifted since the PRD was drafted.

---

## Codebase Analysis — Verified File Paths & Line Numbers

### Current schema head: [schemas/finding.yaml](../../schemas/finding.yaml)

- **Line 13**: `schema_version: "1.4"` — current head, confirms PRD assumption A2. Target for F-A2 is `"1.5"` per PRD SC-1 / FR-1.
- **Lines 101-110** (`references: list[string]`): the existing list-typed precedent. Single scalar value per element (plain strings).
- **Lines 147-178** (`agentic_pattern`): Feature 142 enum-field-addition precedent with 8-value enum + `default: none`. Documents the ADR-026 minor-bump rationale inline.
- **Lines 182-208** (`delta_status` + `baseline_run_id`): Feature 104 baseline-aware field pattern with `required_when: baseline_present`.

**Key distinction**: `references` is list-of-STRING; F-A2's `source_attribution` is list-of-RECORD (nested 3-field shape per element). PRD §ADR Lineage calls this the first "list-of-RECORD" field — verified correct.

### Parser round-trip: [scripts/tachi_parsers.py:621-677](../../scripts/tachi_parsers.py#L621-L677)

Function `parse_threats_findings(content: str) -> list` lives at line 621. Two patterns of interest:

- **Lines 644-648**: Column-key detection pattern (`pattern_key`) — case-insensitive scan of `rows[0].keys()`. This is the shape F-A2 will follow if Q1-A cell-string were chosen (rejected per PRD) or Q1-E (conditional Section 9 YAML block — section existence check rather than column-key check).
- **Lines 672-676** (`delta_status` conditional-key injection):
  ```python
  # Delta fields: include only when present (backward compatible)
  status = row.get("Status", "").strip()
  if status:
      finding["delta_status"] = status
  ```
  This is the Feature 104 precedent PRD AC for US-189-2 cites — key omitted when absent, not defaulted to null/empty. **F-A2 MUST follow this pattern** for `source_attribution` to preserve backward compatibility.

- **Line 670** (`agentic_pattern`): always-injected pattern (even when column missing, defaults to `"none"`). F-A2 must NOT adopt this always-inject shape — the PRD AC is explicit: `source_attribution` is conditional-key, not always-injected.

### F-A1 taxonomy YAMLs: [schemas/taxonomy/](../../schemas/taxonomy/)

Verified present 2026-04-17 (per F-A1 / Feature 180 merge `8b7c7bf`):
- `owasp.yaml`, `mitre-attack.yaml`, `mitre-atlas.yaml`, `nist-ai-rmf.yaml`, `cwe.yaml` — **5 external-framework catalogs** (F-A2 `taxonomy` enum scope)
- `tachi-control-category.yaml`, `tachi-stride-ai-category.yaml` — 2 internal catalogs (F-A2 enum EXCLUDES these per PRD FR-1)
- `crosswalk.yaml` — 526 edges (downstream consumer target, not F-A2 scope)
- `README.md` — curation methodology

Record shape (verbatim from [schemas/taxonomy/owasp.yaml:25-30](../../schemas/taxonomy/owasp.yaml)):
```yaml
- id: A01
  full_id: OWASP-2021-A01
  name: Broken Access Control
  url: https://owasp.org/Top10/2021/A01_2021-Broken_Access_Control/
  cwe_refs: [CWE-22, CWE-23, CWE-35]
```

F-A2 referential integrity: every `source_attribution[].id` MUST resolve as a top-level `id` key in the matching `schemas/taxonomy/{taxonomy}.yaml`.

### Test fixture pattern: [tests/scripts/](../../tests/scripts/)

Fixture subdirectories present: `exec_arch/`, `finding_pattern_parser/`, `golden/`, `pattern_extraction/`, `pattern_synthesis/`, `report_data/`.

Backward-compat harness: [tests/scripts/test_backward_compatibility.py:36](../../tests/scripts/test_backward_compatibility.py#L36) pins `SOURCE_DATE_EPOCH = "1700000000"` at line 36; applied via `pipeline_env = {**os.environ, "SOURCE_DATE_EPOCH": SOURCE_DATE_EPOCH}` at line 78. This is the SC-2 gate harness.

**Fixture convention for F-A2**: test fixtures live under `tests/scripts/fixtures/source_attribution/` (new subdirectory per Feature 142 pattern). Sample records MUST NOT land in `examples/` outputs per PRD Q-P1 resolution.

### Feature 141 `has-attack-chains` precedent

Feature 141 introduced conditional Section 6 in `threat-report.md` gated by `has-attack-chains: true` boolean. Architecturally: orchestrator Phase 3.5 determines if chains exist → sets the boolean → downstream consumers (threat-report, extract-report-data) check the boolean and render/skip the section.

**Q1-E inherits this exact shape**: a new `has-source-attribution: true` boolean (or equivalent flag) gates a new conditional Section 9 YAML block in `threats.md`. When no finding carries `source_attribution`, Section 9 is omitted entirely — preserving SC-2 byte-identity on the 5 current baselines.

### Output schema: [templates/tachi/output-schemas/threats.md](../../templates/tachi/output-schemas/threats.md)

Current canonical structure (713 lines):
- §1 System Overview, §2 Trust Boundaries, §3 STRIDE Tables, §4 AI Threat Tables
- §4a Correlated Findings, §4b Findings by Agentic Pattern (conditional), §4c Resolved Findings (conditional)
- §5-§7 existing assessment sections
- §8 Delta Summary (conditional on baseline)

**No Section 9 exists today** — F-A2 Q1-E would add it as a new conditional section, landing after §8 Delta Summary in the reading order. Gating precedent: Feature 142's §4b and Feature 104's §4c both use the conditional-section-header-and-body-omitted shape.

---

## Architecture Constraints

### ADR Lineage — Verified All Present

- **[ADR-020](../../docs/architecture/02_ADRs/ADR-020-maestro-layer-classification.md)**: `maestro_layer` passive-overlay precedent — additive optional scalar enum classified at orchestrator Phase 1. F-A2 inherits the *additive-optional* half but NOT the *orchestrator-populated* half (F-A2 defers populators to F-A3).
- **[ADR-021](../../docs/architecture/02_ADRs/ADR-021-source-date-epoch-for-deterministic-pdf-comparison.md)**: `SOURCE_DATE_EPOCH=1700000000` harness for byte-deterministic PDF regression. SC-2 gate uses this exact convention.
- **[ADR-023](../../docs/architecture/02_ADRs/ADR-023-threat-agent-skill-references-pattern.md)**: zero-edit invariant on 11 threat-detection agents + 11 companion skill-reference files. SC-7 / FR-6 cite this ADR for the 22-file zero-edit scope. Decision 2 explicitly extends the MAESTRO-free boundary to the threat-agent tier — same boundary logic applies to F-A2's scope discipline.
- **[ADR-026](../../docs/architecture/02_ADRs/ADR-026-pattern-classification-mechanism.md)**: minor-bump rule for NEW enum-typed field additions under three conditions (additive, has default, schema shape unchanged). F-A2 extends this rule to a **list-of-RECORD field** — the PRD names this the "Complex-Shape Addition Clarifier" and the F-A2 ADR must document the extension explicitly.
- **[ADR-027](../../docs/architecture/02_ADRs/ADR-027-taxonomy-crosswalk-schema.md)**: 7-value `taxonomy` enum in F-A1 crosswalk. F-A2's 5-value `taxonomy` enum is the **external-framework subset** (excludes `tachi-control-category`, `tachi-stride-ai-category`) — PRD §FR-1 rationale verified against ADR-027 Decision 3.

### Key Technical Constraints

1. **Python stdlib-only runtime** per Feature 128 precedent — `pyyaml` + `pytest` already in `requirements-dev.txt`.
2. **Zero new runtime dependencies** per PRD SC-6 — verified empty-diff expectation on `pyproject.toml`, `requirements*.txt`, `package.json`.
3. **Byte-identity SC-2 regression** — 5 non-agentic baselines (`web-app`, `microservices`, `ascii-web-api`, `mermaid-agentic-app`, `free-text-microservice`) under `SOURCE_DATE_EPOCH=1700000000`. 6th baseline (`agentic-app`) follows Feature 128 convention — may regenerate.
4. **ADR Proposed → Accepted dual-commit governance** (ADR-027 Decision 8 / F-A1 precedent): ADR authored Proposed at Day 1 Wave 1 schema-lock; transitioned Accepted at PR merge; SHA fill post-merge.

---

## Industry Research

Skipped heavy web research — this is an internal schema contract extension with no external best-practices surface beyond what the PRD already references (ADR-026, ADR-027, F-A1 YAMLs, CSA MAESTRO framework via prior features). Terminology-level references (OWASP LLM05, MITRE ATLAS AML.T0051, CWE-1426, NIST MEASURE 2.7) are preserved from F-A1 verbatim-transcription standards.

---

## Knowledge Base Findings

Relevant KB patterns from recent feature memory:
- **Feature 180 (F-A1) delivery**: verified 2026-04-17 merge — dependency SATISFIED.
- **Feature 142 schema bump (1.3 → 1.4)**: exact shape for F-A2's 1.4 → 1.5 bump. Additive-only, default value for new field, no shape breakage.
- **Feature 104 conditional-key pattern**: `delta_status` injection only when Status column present. F-A2 `source_attribution` MUST adopt this exact shape (not the `agentic_pattern` always-inject pattern).
- **Feature 082 / ADR-023 zero-edit invariant**: 11 agents + 11 skill-ref files = **22 files** that MUST NOT change in F-A2 PR.

---

## Recommendations for Spec

- **FR numbering**: preserve PRD FR-1..FR-6 mapping 1:1 to spec FR — no renumbering. PRD spec semantic parity is valuable for traceability.
- **SC numbering**: preserve PRD SC-1..SC-7 mapping 1:1 to spec SC. PRD SCs are already measurable.
- **Q1 / Q2**: these are **architect-owned** and remain unresolved at spec time. Spec FR-2 and FR-3 MUST be written in a serialization-surface-agnostic way (refer to Q1 resolution without pinning to any option). The spec is NOT the place to resolve Q1 or Q2.
- **User stories**: three US from PRD translate directly — independent, testable, MVP-capable per AC formulation.
- **Edge cases**: empty `source_attribution: []` (distinct from absent field), multiple records with same `{taxonomy, id}` (deduplication or preserve), `relationship` omitted (defaults to `primary`), very large arrays.
- **Key entities**: Finding (extended), SourceAttributionRecord (new), Taxonomy (external reference to F-A1 catalogs).
- **Fixture discipline**: per PRD Q-P1 resolution, sample records live in `tests/scripts/fixtures/source_attribution/`, NOT in `examples/` outputs.
- **ADR plan**: single new ADR (ADR-028 unless another ADR lands first) per PRD FR-5. Dual-commit pattern per F-A1 precedent.

---

## Open Questions Carried Forward (Architect-Owned)

- **Q1**: serialization surface (Q1-E primary, Q1-B fallback) — Day 1 architect memo.
- **Q2**: referential-integrity phase (Q2-B separate validation phase preferred) — Day 1 architect memo.
- **Q3**: ADR number (mechanical assignment, likely ADR-028).

All three are architect-authority per Constitution Principle X; spec FR text abstracts these cleanly without prejudging.
