---
triad:
  pm_signoff:
    agent: product-manager
    date: 2026-04-24
    status: APPROVED
    notes: "All 3 PRD-stage PM concerns resolved. Phase breakdown delivers all 3 levels (L1 prompt, L2 callouts, L3 payload). Phase 4 validates all 8 SCs. F-128 preservation pinned exhaustively (FR-212-20..23 + SC-212-7). 1-week timeline preserved with Phase 1 widening to 3-5h justified. No scope creep. 0 blockers, 2 minor non-blocking observations. See .aod/results/pm-review-plan-212.md."
  architect_signoff:
    agent: architect
    date: 2026-04-24
    status: APPROVED
    notes: "All 4 PRD-stage Architect concerns resolved (H1 floor rule, M2 field-name lock, M3 sort determinism, L4 drift detection). Constitution Check passes all 10 principles. F-128 contracts preserved. ADR-017/021/028 correctly invoked. Scope discipline enforced. 0H/0M/0L + 4 FYI observations non-blocking. See .aod/results/architect-review-plan-212.md."
  techlead_signoff: null
---

# Implementation Plan: Improve Executive-Architecture Infographic

**Branch**: `212-improve-executive-architecture-infographic` | **Date**: 2026-04-24 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `specs/212-improve-executive-architecture-infographic/spec.md`

## Summary

Upgrade the `executive-architecture` infographic template from a text-label inventory to an OpenClaw-style system flow diagram across three incremental levels:

- **Level 1** — Rewrite the Gemini prompt to produce rounded-rectangle nodes, directional arrows, leader-lined callouts on specific nodes, dashed trust-zone clusters, and compact empty-layer badges.
- **Level 2** — Rework `_select_critical_high_callouts()` from per-layer-dedup to top 6–8 callouts system-wide, using Largest Remainder Method allocation with a per-layer floor-rule invariant (enforceable) and a 4-callout-per-layer ceiling.
- **Level 3** — Extend `_build_executive_architecture_payload()` with `flow_edges[]` (sourced from `parse_scope_data.data_flows[]`, field name `destination` not `target` — matches producer) and `clusters[]` (sourced from `parse_scope_data.trust_boundaries[]`, field `members` sourced from `components`). Update the Gemini prompt to consume the new fields. Add drift-guard test file.

Research completed at spec-phase and captured in [research.md](research.md). All F-128 contracts preserved: output filenames, PDF position (pages 2–3), skip behavior on zero Critical/High, portrait orientation, and all 5 other infographic templates untouched.

## Technical Context

**Language/Version**: Python 3.11+ (extractor), Markdown (skill references), Gemini API prompts (no new SDK).
**Primary Dependencies**:
- `scripts/tachi_parsers.py::parse_scope_data` (existing, stable — verified 2026-04-24)
- `scripts/extract-infographic-data.py::_build_executive_architecture_payload` (extended, not replaced)
- `scripts/extract-infographic-data.py::_select_critical_high_callouts` (rewritten)
- `.claude/skills/tachi-infographics/references/executive-architecture.md` (doc + prompt text)
- `.claude/skills/tachi-infographics/references/gemini-prompt-construction.md` (verbatim prompt block updated)
- `.claude/skills/tachi-infographics/references/visual-design-system.md` (palette source; no edits — consumed unchanged)
- Gemini API (image generation — existing production credentials; no SDK or model change)

**Storage**: None new. Consumes `threats.md` (markdown); emits `threat-executive-architecture-spec.md` (markdown) + `threat-executive-architecture.jpg` (binary). Paths unchanged from F-128.

**Testing**: pytest; new fixture matrix in `tests/scripts/test_extract_infographic_data.py` (per-layer floor rule) and new file `tests/scripts/test_executive_architecture_payload.py` (L3 schema drift guard with absent/empty/single/multi matrix).

**Target Platform**: Local developer + CI (GitHub Actions). Python script runs locally; Gemini image generation runs against the Google Cloud endpoint with existing credentials.

**Project Type**: Single repo (methodology template + companion scripts). No service deployment.

**Performance Goals**:
- Extractor runtime increase ≤10% on the reference dataset vs. pre-F-212 baseline (SC-212-8).
- Byte-identical payload JSON across two consecutive runs on identical input (SC-212-6, ADR-017).
- PDF byte-identity on zero-finding input (SC-212-7, ADR-021 under `SOURCE_DATE_EPOCH=1700000000`).

**Constraints**:
- F-128 output-contract preservation (filenames, PDF position, skip behavior, Typst bindings, portrait orientation, other 5 templates untouched) — hard non-negotiable.
- Determinism (ADR-017) — re-running extractor on identical input produces byte-identical JSON.
- Additive schema extension (ADR-028) — new `flow_edges` / `clusters` keys always present, empty arrays (never `null`, never missing) when source sections absent.
- Prompt text locked VERBATIM in skill reference file — no runtime composition of aesthetic language.

**Scale/Scope**:
- Files changed: ~5 (two skill references, one Python script, two test files).
- LoC delta (estimated): ~200–300 (prompt rewrite ~60 lines; callout selection rewrite ~60 lines; payload extension ~40 lines; tests ~100 lines).
- Timeline: 1 week total across three levels (matches PRD); L1+L2 in first 3 days (primary quality win), L3 in following 4 days (architectural endgame).

## Constitution Check

*GATE: Must pass before Phase 0. Re-check after Phase 1 design.*

| Principle | Applicability | Status | Notes |
|-----------|---------------|--------|-------|
| **I. General-Purpose Architecture** | N/A | PASS | Template content is security-specific by scope (threat infographics), not a core architecture concern. |
| **II. API-First Design** | Limited | PASS | No new REST/MCP endpoints. Producer-consumer contract between `parse_scope_data` and `_build_executive_architecture_payload` is documented in [contracts/payload-schema.md](contracts/payload-schema.md). |
| **III. Backward Compatibility (NON-NEGOTIABLE)** | Critical | PASS | F-128 contracts preserved exhaustively (FR-212-20..23). PDF byte-identity on zero-finding input enforced via SC-212-7. Other 5 templates untouched (FR-212-21). Additive schema for Level 3 (ADR-028 pattern). |
| **IV. Concurrency & Data Integrity** | N/A | PASS | No concurrent state transitions — extractor is a sync CLI script. |
| **V. Privacy & Data Isolation** | N/A | PASS | No new data paths. Payload fields originate from existing `threats.md` input. |
| **VI. Testing Excellence (NON-NEGOTIABLE)** | Critical | PASS | Level 2: fixture matrix on `test_extract_infographic_data.py` enforces per-layer floor rule (SC-212-4). Level 3: new `test_executive_architecture_payload.py` with absent/empty/single/multi matrix (SC-212-5). Determinism test (SC-212-6). |
| **VII. Definition of Done (NON-NEGOTIABLE)** | Required | PASS | Plan Phase 4 explicitly maps to `/aod.deliver` — all three levels must pass DoD before closure. |
| **VIII. Observability & Root Cause Analysis** | Standard | PASS | Warnings logged on truncation (FR-212-17) and unknown-component flow edges (Edge Case 3). No new long-running processes. |
| **IX. Git Workflow (NON-NEGOTIABLE)** | Required | PASS | Feature branch `212-improve-executive-architecture-infographic` in use. Draft PR #213 open since plan stage start. |
| **X. Product-Spec Alignment (NON-NEGOTIABLE)** | Required | PASS | PRD approved-with-concerns by all three Triad roles; spec resolved all concerns and earned PM APPROVED. This plan triggers dual sign-off (PM + Architect) per Step 3 below. |

**Verdict**: No violations. No complexity-tracking exemptions needed. Proceed to Phase 0.

## Components

### Production code

| Component | File | Change Type | Level |
|-----------|------|-------------|-------|
| Callout-selection function | `scripts/extract-infographic-data.py::_select_critical_high_callouts` | Rewrite | L2 |
| Payload builder | `scripts/extract-infographic-data.py::_build_executive_architecture_payload` | Extend (additive keys) | L3 |
| Flow-edge derivation (new helper) | `scripts/extract-infographic-data.py::_build_flow_edges` | New | L3 |
| Cluster derivation (new helper) | `scripts/extract-infographic-data.py::_build_clusters` | New | L3 |
| Gemini prompt text — executive-architecture | `.claude/skills/tachi-infographics/references/executive-architecture.md` | Rewrite prompt block | L1, L3 |
| Gemini prompt construction | `.claude/skills/tachi-infographics/references/gemini-prompt-construction.md` | Minor edit — document verbatim-lock for exec template | L1 |

### Test code

| Component | File | Change Type | Level |
|-----------|------|-------------|-------|
| Per-layer floor-rule fixture matrix | `tests/scripts/test_extract_infographic_data.py` | Extend | L2 |
| Payload schema drift guard | `tests/scripts/test_executive_architecture_payload.py` | New | L3 |
| Determinism test | Included in above | New | L2+L3 |

### Reference assets (read-only consumers)

| Component | File | Change Type |
|-----------|------|-------------|
| Visual design system | `.claude/skills/tachi-infographics/references/visual-design-system.md` | No change (palette inherited) |
| F-128 spec + plan + contracts | `specs/128-*/` | No change (preservation reference only) |
| Reference image (OpenClaw) | `openclaw-agent-threat-model-infographic.jpg` (external) | No change (human-review target only) |

## Data Flow

```
threats.md
    │
    ▼
scripts/tachi_parsers.py::parse_scope_data()
    │  returns: {
    │    data_flows: [{source, destination, data, protocol}],
    │    trust_boundaries: [{zone, trust-level, components}],
    │    boundary_crossings: [{crossing, from-zone, to-zone, components, controls}]
    │  }
    ▼
scripts/extract-infographic-data.py
    │
    ├─→ _compute_trust_zones()       → layers[]             (existing)
    ├─→ _compute_data_flows()         → (internal use)       (existing)
    ├─→ _compute_boundary_crossings() → (internal use)       (existing)
    ├─→ _select_critical_high_callouts() → callouts[]        (L2 REWRITE)
    ├─→ _build_flow_edges()           → flow_edges[]         (L3 NEW)
    ├─→ _build_clusters()             → clusters[]           (L3 NEW)
    │
    ▼
_build_executive_architecture_payload() →
    {
      metadata:           {...},                    (existing)
      layers:             [...],                    (existing — may add layer_overflow field, L2)
      callouts:           [...6-8 items, weighted], (L2 EXTENDED)
      severity_distribution: {...},                 (existing)
      flow_edges:         [...or []],               (L3 NEW — always present)
      clusters:           [...or []]                (L3 NEW — always present)
    }
    │
    ▼
threat-executive-architecture-spec.md
    │
    ▼
tachi-infographic agent (consumes .md spec)
    │
    ▼
Gemini API (image generation with VERBATIM-locked prompt from executive-architecture.md)
    │
    ▼
threat-executive-architecture.jpg
    │
    ▼
Typst PDF assembly (has-executive-architecture binding — F-128 contract, unchanged)
    │
    ▼
Final PDF (pages 2–3 position — F-128 contract, unchanged)
```

## Tech Stack

- **Language**: Python 3.11+
- **Test runner**: pytest
- **Markdown parser**: existing `scripts/tachi_parsers.py` (no new dependency)
- **Image generation**: Google Gemini API (existing; model `gemini-2.5-flash-image` default with fallback chain — no change)
- **PDF assembler**: Typst (existing; no change — binding consumers unchanged)
- **Determinism**: `SOURCE_DATE_EPOCH=1700000000` per ADR-021 (existing convention; applied to regression test runs)
- **No new dependencies added**. No new libraries. No new API endpoints. No new deployment surfaces.

## Project Structure

### Documentation (this feature)

```
specs/212-improve-executive-architecture-infographic/
├── spec.md                          # Feature spec (PM-approved 2026-04-24)
├── plan.md                          # This file
├── research.md                      # Spec-phase research (reused as Phase 0)
├── data-model.md                    # Schema additions (L3 payload extensions)
├── quickstart.md                    # How to regenerate + validate reference image locally
├── contracts/
│   └── payload-schema.md            # Producer/consumer contract between parse_scope_data and executive-architecture payload
├── checklists/
│   └── requirements.md              # Spec quality checklist (already created)
└── tasks.md                         # (generated by /aod.tasks)
```

### Source Code (repository root)

```
scripts/
├── extract-infographic-data.py      # EDIT — rewrite _select_critical_high_callouts, extend _build_executive_architecture_payload, add _build_flow_edges + _build_clusters
└── tachi_parsers.py                 # READ-ONLY — parse_scope_data is consumed, not modified

.claude/skills/tachi-infographics/references/
├── executive-architecture.md        # EDIT — rewrite Gemini prompt block VERBATIM; document new L3 payload fields
├── gemini-prompt-construction.md    # EDIT (minor) — note verbatim-lock for exec template
└── visual-design-system.md          # READ-ONLY — palette source

tests/scripts/
├── test_extract_infographic_data.py           # EDIT — add per-layer floor-rule fixture matrix
├── test_executive_architecture_payload.py     # NEW — L3 schema drift guard (absent/empty/single/multi matrix)
└── fixtures/exec_arch/agentic_app/threats.md  # READ-ONLY — in-repo fallback dataset for CI
```

**Structure Decision**: Single-project layout (tachi is a methodology template repo; scripts live at `scripts/`, tests at `tests/scripts/`, skill references at `.claude/skills/tachi-infographics/references/`). No new top-level directories.

## Phase 0 — Research

Research was conducted during the spec phase and is captured in [research.md](research.md). Summary:

- **Codebase analysis** confirmed `parse_scope_data` output shape (field names: `source`/`destination`/`data`/`protocol` on `data_flows[]`; `zone`/`trust-level`/`components` on `trust_boundaries[]`). This resolves Architect MEDIUM-2 concern and validates R3 risk from PRD.
- **KB findings** identified three relevant precedents: F-128 contract preservation, F-189 additive-schema pattern with empty-array-when-absent, F-209 drift-guard test file per new producer/consumer pair.
- **Architecture docs** confirmed ADR-017 (deterministic extraction), ADR-021 (SOURCE_DATE_EPOCH), ADR-028 (additive schema extension) all apply.
- **Industry research** validated: (a) Gemini prompt patterns — directive structured prompts with "schematic diagram with shapes and arrows" preamble defeat text-only failure mode; (b) callout density 6–8 is within cognitive-load guidance (Miller's 7±2 refined to 3–5 working-memory items with 9 upper bound); (c) Largest Remainder Method is canonical for weighted-from-K-groups allocation with quota rule satisfying the per-layer floor rule.

**Phase 0 output**: `research.md` (existing — reused).

**No open NEEDS CLARIFICATION markers remain at Phase 0 exit.**

## Phase 1 — Design & Contracts

### Data Model

See [data-model.md](data-model.md) for the full schema. Summary of Level 3 additions to `_build_executive_architecture_payload()` return dict:

**`flow_edges[]`** (new key, always present):
- `source`: string (component name, required, matches producer)
- `destination`: string (component name, required — **field name matches producer; NOT `target`**)
- `data`: string (optional — from producer)
- `protocol`: string (optional — from producer)

**`clusters[]`** (new key, always present):
- `name`: string (from `trust_boundaries[].zone`)
- `members`: list of strings (from `trust_boundaries[].components`)
- `trust_level`: string (from `trust_boundaries[].trust-level`, one of `trusted`/`semi-trusted`/`untrusted`)

Sort order on `flow_edges[]`: `(source.lower(), destination.lower())` ascending. Sort order on `clusters[]`: `(_TRUST_LEVEL_ORDER[trust_level] default 99, name.lower())` ascending. `members` within each cluster: ascending case-insensitive. Sort pattern mirrors `_compute_trust_zones` at `scripts/extract-infographic-data.py:784`.

**`callouts[]`** (existing key, L2 rewritten logic — same field shape):
- Existing fields: `layer_name`, `finding_id`, `severity`, `raw_description`, `composite_score`, `affected_component`.
- L2 changes: 6–8 items total (down from up-to-one-per-layer), weighted-per-layer distribution.

**`layers[]`** (existing key, L2 minor extension):
- New optional field: `layer_overflow: str | None` — populated with `"+ N more in this layer"` when callout count for layer exceeds 4.

### Contracts

See [contracts/payload-schema.md](contracts/payload-schema.md) for the full producer/consumer contract. Summary:

- **Producer**: `scripts/tachi_parsers.py::parse_scope_data()` — producer is locked (F-212 does not modify it); its output shape is the source of truth for field names.
- **Consumer 1 (extractor)**: `scripts/extract-infographic-data.py::_build_executive_architecture_payload()` — consumes producer output; emits extended payload dict. Contract validated by new `test_executive_architecture_payload.py` fixture matrix.
- **Consumer 2 (Gemini prompt)**: VERBATIM-locked prompt block in `executive-architecture.md` consumes `flow_edges[]` and `clusters[]` by name.
- **Consumer 3 (Typst assembler)**: Unchanged — consumes existing bindings only (`has-executive-architecture`, `executive-architecture-image-path`). F-128 contract preserved.

### Quickstart

See [quickstart.md](quickstart.md) for local regeneration + validation workflow.

### Agent Context

No updates needed. This feature does not introduce new technologies, frameworks, or domain vocabulary that require agent context refresh.

## Testing Strategy

### Level 1 (Gemini prompt rewrite)

- **Primary validation**: human side-by-side comparison of regenerated reference image against `openclaw-agent-threat-model-infographic.jpg` on 4 structural criteria (SC-212-1).
- **Iteration budget**: up to 3 prompt iterations per Risk R1 (Team-Lead MODERATE-1 concern — Phase 1 estimate widened to 3–5h).
- **Regression gate**: PDF byte-identity on zero-finding input (SC-212-7). No automated visual regression in scope.

### Level 2 (callout-selection rework)

- **Primary**: per-layer floor-rule fixture matrix (`tests/scripts/test_extract_infographic_data.py::test_per_layer_floor_invariant`) — absent / 1-qualifying-layer / 2-qualifying-layer / 3-qualifying-layer / all-layers-qualifying fixtures. Enforces SC-212-4.
- **Determinism**: two consecutive runs produce byte-identical `callouts[]` (covered by existing harness + explicit `test_callouts_deterministic`).
- **Performance**: extractor wall-clock ≤10% regression on reference dataset (SC-212-8, timed measurement).
- **Regression against old logic**: superset check — every layer that had a qualifying finding under the old per-layer-dedup logic appears in new `callouts[]` with ≥1 entry when total-cap permits (programmatic ID-superset check — Team-Lead LOW-2 resolution).

### Level 3 (payload schema extension)

- **Primary**: `tests/scripts/test_executive_architecture_payload.py` with fixture matrix — absent / empty / single / multi. Covers SC-212-5.
- **Determinism**: two consecutive runs produce byte-identical `flow_edges[]` and `clusters[]` (SC-212-6).
- **Drift guard**: assertions on field names (`destination` not `target`; `members` populated from `components`), sort order, and empty-array-when-absent semantics.
- **Prompt co-landing enforcement**: test asserts that the prompt text in `executive-architecture.md` contains the strings `"flow_edges"` and `"clusters"` (addresses FR-212-18 — prevents orphaned payload fields).

## Phases (scheduling)

| Phase | Scope | Wall-clock budget | Owner (team-lead to assign) | Gates |
|-------|-------|-------------------|-----------------------------|-------|
| **Phase 1 — L1 prompt rewrite** | Rewrite Gemini prompt block; regenerate reference image; validate M1 structural criteria | 3–5h (widened from PRD 2h per Team-Lead MODERATE-1) | senior-backend-engineer + ux-ui-designer (image review) | PDF byte-identity on zero-finding input; M1 3/4 PASS minimum, 4/4 target |
| **Phase 2 — L2 callout selection** | Rewrite `_select_critical_high_callouts`; add per-layer floor-rule fixture matrix; regression against old logic | Day 2–3, ~4h | senior-backend-engineer + tester | All fixtures PASS; superset check PASS; determinism PASS |
| **Phase 3 — L3 payload extension** | Add `flow_edges[]` / `clusters[]`; update prompt to reference them; add drift-guard test file | Day 4–7, ~1–2 days | senior-backend-engineer + tester | All fixtures PASS; determinism PASS; prompt co-landing PASS |
| **Phase 4 — Integration + delivery** | End-to-end regeneration on reference dataset; human side-by-side review; `/aod.deliver` DoD | Day 7, ~2h | orchestrator + product-manager (visual sign-off) | SC-212-1 through SC-212-8 all PASS |

**Total budget**: 1 week (matches PRD timeline). Phase 1 widening absorbs from Phase 4 slack. Risk R1 contingency (if Phase 1 cannot reach 3/4 M1 criteria): re-prioritize L3 ahead of L1, accept slower time-to-first-quality-win.

## Risks

All three PRD risks apply; mitigation approaches confirmed in plan:

- **R1 (Gemini prompt fragility, likelihood medium)**: Phase 1 budget widened to 3–5h with 3-iteration cap. Contingency documented. L3 reduces Gemini inference surface.
- **R2 (backward-compat break, likelihood low / impact high)**: FR-212-20 through FR-212-23 enumerate every F-128 contract. SC-212-7 enforces PDF byte-identity on zero-finding input as a hard gate. All 5 other templates untouched (FR-212-21).
- **R3 (parse_scope_data output mismatch, likelihood low / impact medium)**: RESOLVED — codebase research verified exact field names 2026-04-24. Plan aligned to producer (Architect MEDIUM-2).

Plan-level addition:
- **R4 (scope-bleed into PR — F-128 lesson KB-026)**: Mitigation — scope files enumerated in plan Components table. No bundling of unrelated fixes. If a related defect is discovered mid-flight, file a separate issue and defer.

## Complexity Tracking

*None required — no Constitution gate violations.*

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|--------------------------------------|
| *(none)* | *(none)* | *(none)* |
