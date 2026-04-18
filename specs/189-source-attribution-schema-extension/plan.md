---
triad:
  pm_signoff:
    agent: product-manager
    date: 2026-04-17
    status: APPROVED
    notes: "Scope boundaries clean — Data Flow diagram enumerates F-A3/F-B deferrals (risk-scorer, control-analyzer, threat-report, SARIF, Typst, extract-report-data.py ALL named as ignored in F-A2). 22-file zero-edit scope grep-auditably enumerated (6 STRIDE + 5 AI + 11 skill-reference files). All 6 Components trace to product requirements: C1→FR-001/002/003/004/005, C2→FR-006/007 + US-2, C3→FR-008/009 + US-3, C4→FR-014 + SC-005, C5→FR-011/013, C6 matches F-A1 two-link precedent. Q1/Q2 correctly surface-neutral and phase-neutral — C2 interface contract is surface-neutral, C3 two-tier structure accommodates Q2-B without forcing plan revision. Timeline envelope preserved: 2026-04-20 → 2026-04-22. SC-2 byte-identity BLOCKER-flagged in Constraints and R1 mitigation. Zero new runtime deps. No scope smuggling, no populator work, no 22-file violations, no hidden timeline expansion. Minor note: C3 optional CLI entry point is discretionary and correctly scoped."
  architect_signoff:
    agent: architect
    date: 2026-04-17
    status: APPROVED
    notes: "All accumulated ADR invariants preserved. ADR-026 minor-bump 1.4→1.5 correctly invokes 'Complex-Shape Addition Clarifier' extension for list-of-RECORD (C1, C4 body-item 1 mirrors spec FR-014). ADR-023 22-file zero-edit scope enumerated grep-auditably with MAESTRO-free boundary preserved (no orchestrator auto-populate per spec A6 / plan C1 rationale). ADR-021 determinism intact: C3 validator is pure-function, no HTTP, per-invocation cache scoped to call; SC-2 byte-identity harness reused unmodified. Feature 104 conditional-key precedent correctly inherited in C2 (None vs [] distinction; data-model V6). Q1/Q2 surface/phase-neutrality preserved: C2 accommodates Q1-E primary / Q1-B fallback; C3 two-tier design respects Q2-B without hard-wiring. ADR-028 governance correctly specifies Proposed → Accepted dual-commit per ADR-027 / F-A1 precedent with all 6 body items matching spec FR-014 1:1. 5-value taxonomy enum scope (external frameworks only) defended architecturally as distinct-scope subset of ADR-027 Decision 3. Phase 1 artifacts show zero drift from Components section. Risk R2 scope cut to F-A3 defensible. Five minor Day-1 hygiene observations in .aod/results/architect.md — none blocking."
  techlead_signoff: null  # Added by /aod.tasks
---

# Implementation Plan: Source Attribution Schema Extension (F-A2)

**Branch**: `189-source-attribution-schema-extension` | **Date**: 2026-04-17 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `specs/189-source-attribution-schema-extension/spec.md`

## Summary

Extend `schemas/finding.yaml` with an optional `source_attribution` field (array of `{taxonomy, id, relationship}` records), bump `schema_version` from 1.4 to 1.5, extend `parse_threats_findings` to round-trip the field (conditional-key shape per Feature 104 precedent), introduce enum + referential-integrity validation against the F-A1 framework YAMLs, and commit a public per-feature ADR under the Proposed → Accepted dual-commit governance pattern.

**Technical approach**: Data-contract-only feature. Zero edits to the 11 threat-detection agents or their 11 skill-reference files (22-file zero-edit invariant per ADR-023). Zero new runtime dependencies. Byte-identity preserved across the 5 non-agentic example PDFs under `SOURCE_DATE_EPOCH=1700000000` per ADR-021. Serialization surface (Q1) and referential-integrity phase (Q2) resolve in a Day 1 Wave 1 architect memo landing in the ADR Proposed commit.

## Technical Context

**Language/Version**: Python 3.11 (runtime via `scripts/*.py`; stdlib-only per Feature 128)
**Primary Dependencies**: None for runtime. Developer-only: `pyyaml>=6.0` + `pytest>=8.0` + `pytest-cov>=4.1` (all already declared in `requirements-dev.txt` per Feature 128)
**Storage**: Filesystem YAML/Markdown. `schemas/finding.yaml` schema declaration; `schemas/taxonomy/*.yaml` F-A1 reference data; `threats.md` pipeline output (serialization surface TBD per Q1)
**Testing**: `pytest` developer-only. New tests under `tests/scripts/test_source_attribution.py` + fixtures under `tests/scripts/fixtures/source_attribution/`. SC-2 integration via existing `tests/scripts/test_backward_compatibility.py` harness
**Target Platform**: macOS/Linux developer workstation + CI; pipeline is CLI-only (no server surface)
**Project Type**: Single (CLI + static-data project per tachi convention)
**Performance Goals**: Parse ≤5ms per finding with ≤10 records (informational, not CI-enforced); aggregate ≤500ms for threats.md with 100 findings × 3 records each
**Constraints**: Byte-identity on 5 non-agentic baselines (BLOCKER if regressed); 22-file zero-edit scope (BLOCKER if regressed); zero new runtime dependencies (empty diff on `pyproject.toml`, `requirements*.txt`, `package.json`)
**Scale/Scope**: Schema diff ≈40 lines in `schemas/finding.yaml`; parser diff ≈30-60 lines in `scripts/tachi_parsers.py`; new validator ≈80-120 lines; new ADR ≈400-600 lines; 2 new test files ≈300-500 lines total. Two-to-three working day implementation (2026-04-20 → 2026-04-22).

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Relevant principles from `.aod/memory/constitution.md`:

- **Principle III — Backward Compatibility (NON-NEGOTIABLE)**: Byte-identity on 5 non-agentic baselines is the primary gate. ✅ PASS — additive-only schema change, conditional-key parser emission, byte-identity test is SC-002. Constraint C1 in spec makes regression a BLOCKER.
- **Principle VI — Testing Excellence**: Unit + integration + referential-integrity tests required. ✅ PASS — FR-011 covers 3 round-trip + 3 validation paths; FR-012 wires SC-2 integration; FR-013 asserts referential integrity on sample fixtures. Existing pytest framework from Feature 128 used; no new test framework introduced.
- **Principle IX — Git Workflow (NON-NEGOTIABLE)**: Feature branch `189-source-attribution-schema-extension` ✅ created. PR-based workflow. No direct commits to main.
- **Principle X — Product-Spec Alignment (NON-NEGOTIABLE)**: Triad sign-off flow. ✅ PRD approved (PM + Architect + Team-Lead); spec approved (PM); plan.md in review.

**Gates Summary**: All principles PASS. No violations. No entries needed in Complexity Tracking.

## Components

### C1 — Schema Extension: `schemas/finding.yaml`

**Change**: Bump `schema_version: "1.4"` → `"1.5"` at line 13. Append a new optional field `source_attribution` as the last field under the top-level `finding:` key (after `baseline_run_id` at line 208 — inserted as a peer of the existing schema-1.4 fields).

**Shape (to be authored)**:
```yaml
source_attribution:
  type: list[record]
  # Optional additive field per ADR-026 extension ("Complex-Shape Addition Clarifier"
  # for list-of-RECORD fields). See ADR-NNN (F-A2) for the precedent claim.
  # Field is OMITTED when the finding cites no framework items — no implicit []
  # default is injected. This preserves the Feature 104 delta_status conditional-key
  # precedent used elsewhere in this schema.
  record:
    taxonomy:
      type: string
      enum: [owasp, mitre-attack, mitre-atlas, nist-ai-rmf, cwe]
    id:
      type: string
      description: Non-empty; resolves as a top-level id in schemas/taxonomy/{taxonomy}.yaml
    relationship:
      type: string
      enum: [primary, related, derived]
      default: primary
  description: >
    Machine-readable list of external compliance-framework items the finding
    addresses. Populated by downstream features (F-A3); F-A2 establishes the
    contract only. Optional — findings that cite no framework items omit the
    field entirely.
```

**Rationale**: Mirrors the `agentic_pattern` (Feature 142, schema 1.4) and `maestro_layer` (Feature 084, schema 1.2) additive-field precedents. Unlike those fields, `source_attribution` has no orchestrator-populated path in F-A2 — all findings in the 5 non-agentic baselines have absent `source_attribution`.

### C2 — Parser Round-Trip: `scripts/tachi_parsers.py::parse_threats_findings`

**Change**: Extend the existing function (line 621) to read `source_attribution` records from the serialization surface resolved by Q1. Emit the key on returned finding objects only when the input carries attribution data; omit the key otherwise.

**Interface contract** (serialization-surface-neutral):
- INPUT: `content: str` (full `threats.md` text; if Q1-B sidecar is selected, a companion YAML file path)
- OUTPUT: `list[dict]` where each dict MAY contain the key `"source_attribution": list[dict]`. Each inner dict has keys `{"taxonomy": str, "id": str, "relationship": str}`.
- The `"relationship"` key is always present on emitted records (default `"primary"` injected by the parser when absent from input).
- The top-level `"source_attribution"` key is absent on findings without attribution input.

**Implementation shape** (following the `delta_status` precedent at lines 672-676):
```python
# After existing field extraction, conditional attribution injection:
attribution = _extract_source_attribution(row_or_document, finding_id)
if attribution is not None:  # None = absent input; [] = present-but-empty
    finding["source_attribution"] = attribution
```

Where `_extract_source_attribution` is a new helper that reads from the Q1-resolved surface. If Q1-E (conditional Section 9 YAML block) wins, the helper searches for `## 9. Source Attribution` and parses a YAML code fence keyed by finding ID. If Q1-B (sidecar file) wins, the helper reads `threats-attribution.yaml` co-located with `threats.md`.

**Backward-compat**: When no attribution data exists (no Section 9 AND no sidecar file), the helper returns None for every finding. No existing finding shape changes.

### C3 — Validation: Enum + Referential Integrity

**Two-tier validation** to respect Q2 architect preference (Q2-B separate validation phase):

1. **Parser-tier enum validation** (inline in `parse_threats_findings`): on every record read, verify `taxonomy` ∈ 5-value enum and `relationship` ∈ 3-value enum. Malformed records raise `ValueError` with finding ID + bad value + closed-domain.

2. **Referential-integrity validator** (new function, separate phase): `validate_source_attribution(findings: list[dict], taxonomy_dir: Path = Path("schemas/taxonomy")) -> list[ValidationError]`. For every finding with `source_attribution`, for every record, load `taxonomy_dir/{record.taxonomy}.yaml` and assert `record.id` matches a top-level `id:` key. Returns empty list on success or structured error list on failure (empty list semantics — callers can `if errors: raise`).

**Caller**: per PRD Q2-B preference, the canonical caller is orchestrator Phase 4 ("Assess"). The validator is imported from `scripts/tachi_parsers.py` but invoked outside the parser's hot path. A CLI entry point `scripts/validate_source_attribution.py` may be exposed but is optional (not in F-A2 scope if the orchestrator's direct invocation suffices).

**Caching**: Within a single `validate_source_attribution` call, cache F-A1 YAML loads in a local dict keyed by taxonomy name. Mitigates PRD Risk R3 (parse-time bloat from repeated F-A1 YAML reads).

### C4 — ADR (Public, Per-Feature)

**File**: `docs/architecture/02_ADRs/ADR-028-source-attribution-schema-extension.md` (number confirmed mechanically at Proposed commit; ADR-028 is next unused unless another ADR lands first per Q3).

**Governance**: Proposed → Accepted dual-commit, mirroring Feature 180 / F-A1's ADR-027 precedent exactly.
- Day 1 Wave 1 schema-lock commit: authored with `Status: Proposed`. Contains the Q1 + Q2 memo resolutions.
- Day 3 Wave 3 pre-merge: transitioned to `Status: Accepted` with provisional merge date; `Accepted-commit-SHA: <pending-post-merge-fill>` placeholder.
- Post-merge: SHA placeholder replaced with actual squash-merge commit SHA.

**Required body content** (per spec FR-014):
1. Additive-optional-field decision and ADR-026 lineage — naming the "Complex-Shape Addition Clarifier" extension for list-of-RECORD fields
2. Serialization-surface choice resolved per Q1 (Q1-E primary or Q1-B fallback)
3. Referential-integrity phase resolved per Q2 (Q2-B preferred)
4. 5-value `taxonomy` enum scope restriction (external frameworks only) with rationale
5. 3-value `relationship` enum with default-to-`primary` rule
6. Zero-edit invariant on 11 threat-detection agents + 11 companion skill-reference files (22-file scope per ADR-023)

### C5 — Tests

**New test file**: `tests/scripts/test_source_attribution.py` covering:
- Three round-trip paths (FR-011): absent, single-record, multi-record
- Three validation paths (FR-011): bad `taxonomy`, bad `relationship`, bad `id`
- Referential-integrity on sample fixtures (FR-013): all fixtures' `taxonomy`, `id`, `relationship` values resolve
- Edge cases from spec §Edge Cases: empty array vs absent field, duplicates, default `relationship`, whitespace/case rejection

**New fixture directory**: `tests/scripts/fixtures/source_attribution/` containing:
- `valid_single_record.md` — one finding with one attribution record
- `valid_multi_record.md` — one finding with three attribution records spanning 3 distinct taxonomies
- `valid_absent.md` — no findings carry attribution (round-trip to absent-key)
- `valid_empty_array.md` — a finding with `source_attribution: []` (present-but-empty semantic)
- `invalid_taxonomy.md` — `taxonomy: not-a-real-taxonomy`
- `invalid_relationship.md` — `relationship: fabricated_value`
- `invalid_id.md` — `taxonomy: owasp, id: NOT-A-REAL-OWASP-ID`

**Integration**: `tests/scripts/test_backward_compatibility.py` is NOT modified in F-A2 (existing test covers the 5 baselines). SC-2 gate is reused as-is — the F-A2 change must not regress any existing test.

### C6 — Documentation Updates (Minimal)

Two cross-reference updates matching the F-A1 two-link precedent:
- `README.md` top-level: add a one-line note under Recent Changes naming F-A2 and linking to the ADR.
- `docs/architecture/00_Tech_Stack/README.md` Standards section: add F-A2 under the finding-schema evolution timeline (schema 1.5 entry).

**No other documentation edits.** Specifically: `CLAUDE.md` Recent Changes bullet added post-merge via `/aod.deliver`, not in the implementation PR itself.

## Data Flow

```
                    ┌──────────────────────────────────────────────┐
                    │          schemas/finding.yaml (v1.5)         │
                    │   {source_attribution: optional list-record} │
                    └──────────────┬───────────────────────────────┘
                                   │ declares contract
                                   ▼
                      ┌────────────────────────────┐
                      │  threats.md output         │
                      │  (Q1 surface: Section 9    │
                      │   YAML block OR sidecar)   │
                      └────────────┬───────────────┘
                                   │ read at parse time
                                   ▼
                      ┌────────────────────────────┐
                      │  parse_threats_findings    │
                      │  (scripts/tachi_parsers.py)│
                      │  • enum validation inline  │
                      │  • conditional-key emit    │
                      └────────────┬───────────────┘
                                   │ returns list[dict] (MAY include source_attribution)
                                   ▼
               ┌──────────────────────────────────────────────┐
               │  validate_source_attribution (new helper)    │
               │  Phase: orchestrator Phase 4 (Q2-B)          │
               │  Reads: schemas/taxonomy/{taxonomy}.yaml × 5 │
               │  Emits: list[ValidationError] on failure     │
               └──────────────────────────────────────────────┘

F-A2 scope ENDS HERE. The following are F-A3 / F-B scope:
                                   │
                                   ▼
   • risk-scorer: ignores source_attribution in F-A2
   • control-analyzer: ignores source_attribution in F-A2
   • threat-report: ignores source_attribution in F-A2
   • SARIF exporter: ignores source_attribution in F-A2
   • Typst PDF templates: ignore source_attribution in F-A2
   • F-B coverage attestation: JOINs source_attribution × schemas/taxonomy/crosswalk.yaml (future)
```

## Tech Stack

- **Runtime**: Python 3.11 stdlib-only. No new imports beyond `yaml` (already imported transitively via existing parser code paths where needed).
- **Developer-tier**: pyyaml ≥6.0 (YAML load in validator), pytest ≥8.0 (test suite), pytest-cov ≥4.1 (coverage reporting). All three already declared in `requirements-dev.txt` per Feature 128 — no diff.
- **Build/CI**: existing `Makefile test:` target. New tests auto-discovered under `tests/scripts/`. Backward-compat integration reuses existing harness under `SOURCE_DATE_EPOCH=1700000000` per ADR-021.
- **Determinism**: All F-A2 additions are pure functions of input documents. No HTTP fetches, no timestamps, no env reads beyond `SOURCE_DATE_EPOCH` (existing Typst harness). ADR-021 determinism preserved.

## Project Structure

### Documentation (this feature)

```
specs/189-source-attribution-schema-extension/
├── plan.md                  # This file (/aod.project-plan output)
├── spec.md                  # Feature specification with PM sign-off
├── research.md              # Research phase output (written in /aod.spec)
├── data-model.md            # Phase 1 design artifact (generated below)
├── quickstart.md            # Phase 1 design artifact (generated below)
├── contracts/               # Phase 1 API/schema contracts (generated below)
│   ├── finding-schema-1.5.yaml
│   └── source-attribution-record.yaml
├── checklists/
│   └── requirements.md      # Spec quality checklist
└── tasks.md                 # Task breakdown (/aod.tasks output, next stage)
```

### Source Code (repository root)

Files touched in this feature:

```
schemas/
└── finding.yaml             # MODIFIED: schema_version 1.4 → 1.5; new source_attribution field

scripts/
└── tachi_parsers.py         # MODIFIED: extend parse_threats_findings + new validate_source_attribution helper

docs/architecture/02_ADRs/
└── ADR-028-source-attribution-schema-extension.md  # NEW: public per-feature ADR (Proposed→Accepted)

tests/scripts/
├── test_source_attribution.py      # NEW: 3 round-trip + 3 validation + edge cases
└── fixtures/source_attribution/    # NEW: 7 fixture files (4 valid + 3 invalid)
    ├── valid_single_record.md
    ├── valid_multi_record.md
    ├── valid_absent.md
    ├── valid_empty_array.md
    ├── invalid_taxonomy.md
    ├── invalid_relationship.md
    └── invalid_id.md

README.md                    # MODIFIED: one-line Recent Changes note (+ link to ADR)
docs/architecture/00_Tech_Stack/README.md  # MODIFIED: schema-evolution timeline entry
```

**Files NOT touched (enforced by FR-015 / SC-007)** — the 22-file zero-edit scope:

```
.claude/agents/tachi/stride/         # 6 files: spoofing, tampering, repudiation, info-disclosure, denial-of-service, privilege-escalation
.claude/agents/tachi/ai/             # 5 files: prompt-injection, data-poisoning, model-theft, tool-abuse, agent-autonomy
.claude/skills/tachi-{agent-name}/references/detection-patterns.md  # 11 files, one per agent above
```

Additional NOT-touched surfaces: `risk-scorer`, `control-analyzer`, `threat-report`, `threat-infographic`, `report-assembler`, `extract-report-data.py`, `extract-infographic-data.py`, all Typst templates, `schemas/taxonomy/*` (F-A1 reference data is consumed read-only), all `examples/*` outputs.

**Structure Decision**: Single-project layout (Option 1) matching tachi's existing conventions. No new top-level directories. No backend/frontend split (tachi is a CLI + static-data project, not a web application).

## Phase 0 — Outline & Research

Phase 0 research was completed during `/aod.spec` and persisted at `specs/189-source-attribution-schema-extension/research.md`. Key findings relevant to implementation:

- Current `schema_version: "1.4"` at [schemas/finding.yaml:13](../../schemas/finding.yaml#L13) — confirms the 1.4 → 1.5 bump target.
- `parse_threats_findings` lives at [scripts/tachi_parsers.py:621-677](../../scripts/tachi_parsers.py#L621-L677) — the conditional-key precedent (`delta_status`) is at lines 672-676.
- `schemas/taxonomy/` directory verified present 2026-04-17 via F-A1 / Feature 180 merge — all 5 external-framework YAMLs + 2 internal catalogs + crosswalk + README present.
- Feature 141 `has-attack-chains` conditional-section gating is the direct precedent for Q1-E resolution.
- ADR-023 22-file zero-edit scope enumerated verbatim — `.claude/agents/tachi/{stride,ai}/*.md` ∪ `.claude/skills/tachi-{11-agents}/references/detection-patterns.md`.

**Decisions carried into Phase 1**:
- **Decision**: Conditional-key parser emission (NOT always-inject with `[]` default). **Rationale**: Preserves Feature 104 `delta_status` precedent for absent-vs-present-but-empty semantic distinction. **Alternatives**: Always-inject (rejected — breaks AC-1 of US-189-2); always-inject with `None` sentinel (rejected — loses present-but-empty semantic).
- **Decision**: 5-value `taxonomy` enum (external frameworks only). **Rationale**: Internal tachi taxonomies are the recipient side of F-A1 crosswalk edges, not frameworks tachi claims coverage of. **Alternatives**: 7-value enum matching F-A1 crosswalk (rejected — leaks internal vocabulary into adopter coverage claims); 6-value enum including only one internal taxonomy (rejected — asymmetric, no semantic basis for including one not the other).
- **Decision**: Two-tier validation (enum inline in parser + referential integrity in separate phase). **Rationale**: Parser stays thin; referential integrity is an orchestrator-phase concern (Q2-B). **Alternatives**: All-in-parser (rejected — bloats parse-time, couples parser to filesystem layout); all-in-validator (rejected — enum errors should surface at parse time to fail fast).
- **Decision**: ADR-028 (next unused number). **Rationale**: F-A1 claimed ADR-027. **Alternatives**: None (mechanical assignment).
- **Decision**: Proposed → Accepted dual-commit ADR governance. **Rationale**: Direct F-A1 precedent; ADR body needs to be schema-lock authoritative at Day 1 to unblock parallel authoring. **Alternatives**: Single-commit-at-merge (rejected — loses Day 1 schema-lock signal); sidecar memo (rejected — PRD FR-5 explicitly requires a public per-feature ADR).

Research phase is complete. All unknowns resolved modulo Q1 (serialization surface) and Q2 (referential-integrity phase), which are architect-authority and resolve in the Day 1 Wave 1 architect memo landing in the ADR Proposed commit. Plan FRs are surface-neutral and phase-neutral to accommodate any Q1/Q2 resolution within the PRD-narrowed option set (Q1-E or Q1-B for surface; Q2-B for phase).

**Output**: `research.md` was authored during `/aod.spec` and contains all NEEDS CLARIFICATION resolution. No further research tasks pending.

## Phase 1 — Design & Contracts

### Data Model (see `data-model.md`)

Two entities are relevant to F-A2:

1. **Finding (extended from schema 1.4)**
   - All existing schema 1.4 fields unchanged (id, category, component, threat, likelihood, impact, risk_level, mitigation, references, dfd_element_type, maestro_layer, agentic_pattern, delta_status, baseline_run_id).
   - **NEW optional field**: `source_attribution: list[SourceAttributionRecord] | absent`
   - Field is OMITTED when finding cites no framework items; present as a (possibly empty) list otherwise.
   - No existing field is removed, renamed, or re-typed.

2. **SourceAttributionRecord (new)**
   - `taxonomy: string` — closed 5-value enum {owasp, mitre-attack, mitre-atlas, nist-ai-rmf, cwe}
   - `id: string` — non-empty; must resolve as a top-level `id:` key in `schemas/taxonomy/{taxonomy}.yaml`
   - `relationship: string` — closed 3-value enum {primary, related, derived}; default `primary` when absent from input

**Validation rules**:
- (V1) Parser-tier: `taxonomy` enum membership
- (V2) Parser-tier: `relationship` enum membership
- (V3) Parser-tier: `id` non-empty string
- (V4) Validator-tier: `id` resolves in `schemas/taxonomy/{taxonomy}.yaml`
- (V5) Parser-tier: record has exactly 2 or 3 keys (`relationship` optional); no extra keys

**State transitions**: N/A (data contract feature; no state machine).

### Contracts (see `contracts/`)

Two YAML contract files capture the data shape that downstream consumers (F-A3, F-B) will integrate against:

- `contracts/finding-schema-1.5.yaml` — the full finding schema at version 1.5, mirroring `schemas/finding.yaml`'s final shape (authored as a copy for contract-testing purposes if F-A3 adopts this pattern — NOT a replacement for `schemas/finding.yaml` itself, which remains the source of truth).
- `contracts/source-attribution-record.yaml` — the standalone 3-field record contract for F-A3 / F-B integration reference.

### Quickstart (see `quickstart.md`)

A short walkthrough showing an F-A3 developer how to:
1. Read `schemas/finding.yaml` to understand the new field
2. Parse a `threats.md` with attribution-carrying findings via `parse_threats_findings`
3. Validate attribution references via `validate_source_attribution`
4. Write their own populator logic (teaser only — F-A3 is the feature that actually wires it)

### Agent Context Update

Running `.aod/scripts/bash/update-agent-context.sh claude` will append new technology markers (schema 1.5, `source_attribution` field, Q1-E conditional Section 9 pattern if adopted) to the claude agent context. Invoked during Phase 1 execution.

**Output**: data-model.md, contracts/, quickstart.md (all generated in the `/aod.project-plan` flow post-approval — or deferred to `/aod.tasks` if team-lead prefers lean plan.md). CLAUDE.md Recent Changes bullet added via `/aod.deliver` after merge, not in the implementation PR.

## Re-check Constitution Post-Design

Post-design Constitution re-check confirms no violations:

- **Principle III (Backward Compatibility)**: ✅ PRESERVED — additive-only schema, conditional-key parser, 5 baselines gate.
- **Principle VI (Testing Excellence)**: ✅ PRESERVED — new pytest file + 7 fixtures + SC-2 integration via existing harness.
- **Principle IX (Git Workflow)**: ✅ PRESERVED — feature branch, PR workflow, no direct commits to main.
- **Principle X (Product-Spec Alignment)**: ✅ PRESERVED — full Triad flow (PRD approved; spec PM-approved; plan.md pending dual sign-off).

No justified violations. Complexity Tracking table remains empty.

## Complexity Tracking

No Constitution violations. Table intentionally empty.

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| _(none)_ | _(n/a)_ | _(n/a)_ |

## Risks (from spec + PRD)

- **R1 — Serialization surface regresses SC-2** (Medium likelihood × High impact): Q1 resolution is the critical-path item. Mitigation: Q1-E gating precedent (Feature 141 `has-attack-chains`) ensures the new Section 9 is omitted when no finding carries attribution — baseline findings have absent attribution, so no Section 9 is rendered, so no byte-level diff.
- **R2 — List-of-RECORD downstream impact** (Medium × High): F-A3 must design 3 distinct surfaces (SARIF, Typst, extract-report-data.py) for nested-record handling. Mitigation: F-A2 ADR names the Complex-Shape Addition Clarifier precedent; F-A3 PRD will carry per-surface design sections. F-A2 scope is unaffected.
- **R3 — Referential-integrity parse-time bloat** (Low × Low): Q2-B (separate validation phase with per-invocation cache) resolves. F-A1 YAML loads are cached within a single `validate_source_attribution` call.
- **R4 — Schema version wording drift**: PRD Issue-body said 1.3 → 1.4 stale. RESOLVED in PRD Q4 and spec FR-001; ADR documents the correction.
- **R5 — Empty example outputs post-merge**: Certain by design. F-A2 ships the contract; F-A3 populates. Mitigation: ADR-028 frames F-A2 as contract-only; follow-on F-A3 Issue filed on F-A2 PR merge.

## Delivery Milestones

Calendar dates from PRD (2026-04-18 is Saturday → Day 1 = 2026-04-20 Monday):

- **Day 1 (Mon 2026-04-20)** — Schema Lock + Architect Memo
  - Q1 + Q2 memo lands in ADR-028 Proposed commit
  - `schemas/finding.yaml` 1.4 → 1.5 diff authored (partial parallelism with memo — Q1-independent)
  - Test fixture authoring begins (Q1-independent)

- **Day 2 (Tue 2026-04-21)** — Parser + Validation
  - `parse_threats_findings` round-trip implementation
  - Parser-level enum validation
  - `validate_source_attribution` helper implementation
  - Referential-integrity test wiring

- **Day 3 (Wed 2026-04-22)** — Integration + ADR Accepted
  - SC-2 byte-identity regression green across 5 baselines
  - ADR-028 transitioned Proposed → Accepted (provisional merge date)
  - PR submitted for review
  - Post-merge: ADR SHA fill

**Post-merge**: `/aod.deliver` triggers CLAUDE.md Recent Changes bullet, BACKLOG regen, GitHub Issue `stage:done` transition, follow-on Issue filing for F-A3 populators.

## Open Questions (Architect-Owned, Day 1 Resolution)

- **Q1**: Serialization surface. Primary: Q1-E (conditional Section 9 YAML block, gated like Feature 141 `has-attack-chains`). Fallback: Q1-B (YAML sidecar file). Decision due 2026-04-20.
- **Q2**: Referential-integrity phase. Preferred: Q2-B (separate validation helper invoked by orchestrator Phase 4). Decision due 2026-04-20.
- **Q3**: ADR number. Expected ADR-028 (next unused). Mechanical assignment at Proposed commit.

Plan FRs are deliberately surface-neutral and phase-neutral so that any architect resolution within the PRD-narrowed option set does NOT require plan revision.

---

## References

- **Spec**: [spec.md](spec.md)
- **Research**: [research.md](research.md)
- **PRD**: `docs/product/02_PRD/189-source-attribution-schema-extension-2026-04-17.md`
- **F-A1 baseline**: `docs/product/02_PRD/180-taxonomy-crosswalk-collection-2026-04-17.md`
- **ADR-021** (SOURCE_DATE_EPOCH determinism): `docs/architecture/02_ADRs/ADR-021-source-date-epoch-for-deterministic-pdf-comparison.md`
- **ADR-023** (22-file zero-edit invariant): `docs/architecture/02_ADRs/ADR-023-threat-agent-skill-references-pattern.md`
- **ADR-026** (minor-bump rule): `docs/architecture/02_ADRs/ADR-026-pattern-classification-mechanism.md`
- **ADR-027** (F-A1 taxonomy schema): `docs/architecture/02_ADRs/ADR-027-taxonomy-crosswalk-schema.md`
- **Schema head**: `schemas/finding.yaml`
- **Parser target**: `scripts/tachi_parsers.py::parse_threats_findings` (line 621)
- **F-A1 YAMLs**: `schemas/taxonomy/{owasp,mitre-attack,mitre-atlas,nist-ai-rmf,cwe}.yaml`
- **Backward-compat harness**: `tests/scripts/test_backward_compatibility.py`
