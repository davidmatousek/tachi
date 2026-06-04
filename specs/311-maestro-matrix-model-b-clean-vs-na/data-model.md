# Data Model: MAESTRO Matrix Model B — Clean vs. N/A

**Feature**: 311 · **Phase**: 1 (Design) · **Spec**: [spec.md](./spec.md) · **ADR**: [ADR-047](../../docs/architecture/02_ADRs/ADR-047-maestro-coverage-state-authority.md)

This feature adds **no schema entity** (no `schemas/*.yaml` change, no SARIF change). It adds one authored **token** at the markdown source and one derived **enum** in the render IR. The "entities" below are render-layer contracts, not persisted schema.

---

## Entity 1 — MAESTRO layer coverage state (the authored token)

The Section-6 "Risk by MAESTRO Layer" table, `Highest Severity` cell, carries exactly one of three states per layer. All 7 canonical layers always present (F-098); canonical L1→L7 order.

| State | Precondition | `Finding Count` | `Highest Severity` cell token |
|-------|--------------|-----------------|-------------------------------|
| `findings` | ≥1 finding | N (>0) | severity label: `Critical` / `High` / `Medium` / `Low` / `Note` (unchanged) |
| `clean` | ≥1 component maps to the layer AND 0 findings | `0` | `Analyzed — no findings this scan` (**UNCHANGED**; U+2014; no trailing period) |
| `not_applicable` | 0 components map to the layer | `0` | `Not applicable — no components map to this layer` (**NEW**; U+2014; no trailing period) |

- **Authority**: authored once by the orchestrator (ADR-047 D1) from the Section-1 component→layer set; mirrored by `populate-maestro-coverage.py` on example regen.
- **Applicability rule**: a layer is in-scope iff ≥1 Section-1 component carries that layer code. `Unclassified` components do not make any L1–L7 layer in-scope.

## Entity 2 — `coverage_state` (the derived render-IR enum)

A per-layer enum derived from the authored token by the shared classifier and emitted into both render IRs.

```
coverage_state ∈ { "findings", "clean", "not_applicable" }
```

| Field | Type | Where emitted | Notes |
|-------|------|---------------|-------|
| `coverage_state` | string enum | `report-data.typ` (PDF), `maestro-stack.json` (infographic) | Additive render-IR field; existing consumers unaffected. Code-computed, deterministic (ADR-017 `sort_keys`). |

- **Producer**: `classify_maestro_coverage_state(finding_count, highest_severity)` in `scripts/tachi_parsers.py` (see `contracts/coverage-state-classifier.contract.md`).
- **Consumers**: `maestro-findings.typ` (PDF n/a branch), `infographic-maestro-stack.md` Gemini prompt (third band state).
- **Machine-discernibility (US-2)**: this enum is the explicit, parseable representation of the distinction for downstream tools.

## Entity 3 — per-layer render record (always 7)

The layer distribution each extractor builds, one record per canonical layer:

```
{ layer_id, layer_name, finding_count, highest_severity, coverage_state, top_findings? }
```

- `layer_id` ∈ `MAESTRO_LAYERS` (L1…L7, imported from `tachi_parsers.py`).
- `highest_severity` = the carried token (free-text, read at `extract-report-data.py:282` / `extract-infographic-data.py:1527`).
- `coverage_state` = classifier output (Entity 2).
- Backfill (table-less input): absent layers synthesized with `finding_count=0`, `coverage_state="clean"` default (ADR-047 D4); a **present** `not_applicable` token MUST survive the merge.

**Per-surface wiring (Architect HIGH-A — the field's home differs by surface):**
- **PDF**: `main.typ` passes only `maestro_findings_by_layer` (group records `{layer_id, layer_name, findings[]}`) to the MAESTRO page — NOT `maestro_layer_distribution`. So for the PDF, `coverage_state` MUST be threaded onto the **`maestro_findings_by_layer` group records** in `extract-report-data.py` (group pre-build ≈L366–370 + fallback ≈L383–388), set from the matching `parsed_layers`/`maestro_layer_distribution` row's classified token. `maestro_layer_distribution` may also carry it, but the *grouped* structure is the one the Typst page reads (`layer-group.at("coverage-state")`).
- **Infographic**: `coverage_state` rides `per_layer_summaries` (`extract-infographic-data.py:1988–1996`); the visible n/a band is emitted by the `{layer_bands_text}` builder keyed on it (template L191), not only static prose (Architect LOW-B).

## State transitions / invariants

- **Authority invariant (D1/D3)**: `coverage_state` for the three in-scope surfaces is a function of the Section-6 carried token ONLY. `parse_component_layer_mapping()` (Section-1-derived `component_layer_map`) feeds `maestro-heatmap` only and MUST NOT influence `maestro-stack` coverage_state.
- **Ordinal invariant (D5)**: `_SEVERITY_ORDINAL.get(token, 0)` returns 0 for both the clean and n/a tokens; `compute_most_exposed_layer` never selects a layer whose `coverage_state` ≠ `findings`.
- **Backward-compat invariant**: `findings` and `clean` rendering are byte-identical to Model A; only `not_applicable` is new. An all-in-scope example (no n/a) produces no spurious diff.
- **No-schema invariant (FR-014)**: no `schemas/*.yaml`, no SARIF schema or emitted-result change; zero-finding layers emit no SARIF result; scoring untouched.

## Fixture state map — `examples/microservices` (the regression anchor)

| Layer | Section-1 mapped? | Finding Count | Expected `coverage_state` |
|-------|-------------------|---------------|---------------------------|
| L1 Foundation Model | no | 0 | `not_applicable` |
| L2 Data Operations | yes (3 comps) | 8 | `findings` |
| L3 Agent Framework | no | 0 | `not_applicable` |
| L4 Deployment Infrastructure | yes (5 comps) | 14 | `findings` |
| L5 Evaluation & Observability | no | 0 | `not_applicable` |
| L6 Security & Compliance | no | 0 | `not_applicable` |
| L7 Agent Ecosystem | yes (Client Application) | 0 | `clean` |

→ 4 `not_applicable` + 1 `clean` + 2 `findings` = the ≥1-n/a AND ≥1-clean bar (SC-002), no synthetic fixture.
