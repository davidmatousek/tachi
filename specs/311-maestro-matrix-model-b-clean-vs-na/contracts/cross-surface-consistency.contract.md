# Contract: Cross-surface MAESTRO coverage-state consistency

**Feature**: 311 · **Surface**: `tests/scripts/test_maestro_cross_surface_consistency.py` (new dedicated module, run in the existing `tachi maestro coverage` CI job alongside the F-098 7-layer invariant — keeps that invariant test single-concern) · **Spec**: FR-010/FR-011 / SC-001/SC-002

The structural guarantee (ADR-047) is **test-checked, not structural** in the LLM-authored markdown tier (the `maestro_layer` / ADR-037 posture). This contract is therefore the required, non-optional guard that the three surfaces agree.

## Assertion

For a given run/example, for **every** canonical layer L1…L7, the coverage state MUST be identical across the three surfaces:

```
state(threats.md Section-6 cell)  ==  state(report-data.typ coverage_state)  ==  state(maestro-stack.json coverage_state)
```

where `state(...)` ∈ `{ findings, clean, not_applicable }`, derived for the markdown surface via `classify_maestro_coverage_state` (the same classifier), and read directly from the `coverage_state` field for the two render IRs.

- **On disagreement**: fail and name the offending **layer ID(s)** and the divergent surface(s) (self-explaining in the CI check UI).
- **Existing invariant unchanged**: the all-7-rows-present check (`test_maestro_coverage_invariant.py`) stays; this is an **added** assertion in the same job.

## Fixture expected-state table — `examples/microservices`

| Layer | Expected state | All three surfaces agree |
|-------|----------------|--------------------------|
| L1 | `not_applicable` | ✓ |
| L2 | `findings` | ✓ |
| L3 | `not_applicable` | ✓ |
| L4 | `findings` | ✓ |
| L5 | `not_applicable` | ✓ |
| L6 | `not_applicable` | ✓ |
| L7 | `clean` | ✓ |

→ proves SC-002 (≥1 n/a AND ≥1 clean rendered + consistent across all three) on a single committed example.

## Negative test (forced disagreement)

- **Given** the `microservices` fixture, **When** one surface's L7 is forced to `not_applicable` (or the infographic is forced to re-derive from Section 1), **Then** the consistency assertion fails naming `L7` — proving the gate catches divergence (FR-010 AC-3 / ADR-047 D3).

## Determinism

- The infographic `coverage_state` is code-computed and emitted under `json.dumps(sort_keys=True)` (ADR-017) — deterministic across runs.
- The PDF `coverage_state` in `report-data.typ` is byte-deterministic under `SOURCE_DATE_EPOCH=1700000000` (ADR-021).
