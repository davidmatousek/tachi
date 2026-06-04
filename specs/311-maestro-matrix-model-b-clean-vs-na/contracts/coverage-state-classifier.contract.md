# Contract: `classify_maestro_coverage_state` (shared token classifier)

**Feature**: 311 · **Surface**: `scripts/tachi_parsers.py` (shared parser; imported by both extractors) · **ADR**: [ADR-047](../../../docs/architecture/02_ADRs/ADR-047-maestro-coverage-state-authority.md) D2

A **pure, side-effect-free** function that classifies the Section-6 carried token into the `coverage_state` enum. It is the single inheritance point — both extractors call it; neither re-derives applicability.

## Signature

```python
def classify_maestro_coverage_state(finding_count: int, highest_severity: str) -> str:
    """Classify a MAESTRO layer row into its coverage state from the carried cell.

    Reads ONLY the already-authored Section-6 values. Does NOT read Section 1,
    does NOT decide applicability — it classifies the orchestrator's decision.

    Returns exactly one of: "findings" | "clean" | "not_applicable".
    """
```

## Mapping table (the only behavior)

| `finding_count` | `highest_severity` (trimmed) | returns |
|-----------------|------------------------------|---------|
| `> 0` | (any) | `"findings"` |
| `0` | matches the **n/a** token `Not applicable — no components map to this layer` (em- or en-dash tolerated on read) | `"not_applicable"` |
| `0` | matches the **clean** token `Analyzed — no findings this scan` (em- or en-dash tolerated) | `"clean"` |
| `0` | empty / unrecognized (table-less backfill default) | `"clean"` |

## Invariants

- **INV-1 (pure)**: no I/O, no Section-1 read, no global state; output is a function of the two arguments only.
- **INV-2 (dash tolerance)**: match the phrase, tolerating U+2014 (em) and U+2013 (en) and surrounding whitespace — mirrors the populator's read-robustness; do NOT key on trailing punctuation (markdown has none; Typst adds a period downstream).
- **INV-3 (ordinal-0, D5)**: the n/a and clean tokens are NOT added to `_SEVERITY_ORDINAL`; `_SEVERITY_ORDINAL.get(token, 0) == 0` for both. A `coverage_state != "findings"` layer is never selected by `compute_most_exposed_layer`.
- **INV-4 (zero-finding default)**: any `finding_count == 0` with an unrecognized severity classifies as `clean` (never silently `findings`), preserving Model-A behavior for table-less/legacy input.

## Tests (test-first — author before wiring extractors)

- T-1: `(8, "Critical") → "findings"`; `(2, "High") → "findings"`.
- T-2: `(0, "Analyzed — no findings this scan") → "clean"`.
- T-3: `(0, "Not applicable — no components map to this layer") → "not_applicable"`.
- T-4: `(0, "") → "clean"` (backfill default); `(0, "n/a-ish unknown") → "clean"`.
- T-5 (en-dash tolerance): n/a token with U+2013 → `"not_applicable"`.
- T-6 (ordinal-0): `_SEVERITY_ORDINAL.get("<n/a token>", 0) == 0` and `... get("<clean token>", 0) == 0`.

## Anti-requirements (what this MUST NOT do)

- MUST NOT import or call `parse_component_layer_mapping()` or read the Section-1 Components table (ADR-047 D3).
- MUST NOT mutate the input row or any shared structure.
- MUST NOT be the place applicability is *decided* — that is the orchestrator's at authoring time (D1).
