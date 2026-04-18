# Contract: Typst Data Contract — Coverage Attestation Section

**Feature**: 194
**Phase**: 1 — Design & Contracts
**Date**: 2026-04-18
**Scope**: Single external contract emitted by `extract-report-data.py` and consumed by `main.typ` + `coverage-attestation.typ`.

## Contract Type

**Producer**: `scripts/extract-report-data.py` — writes a `report-data.typ` fragment to disk.
**Consumer**: `templates/tachi/security-report/main.typ` (gate + default-guard) → `coverage-attestation.typ` (renderer).

**Format**: Typst source fragment (`#let` declarations concatenated into the existing `report-data.typ`).

**Schema backward-compat**: additive-only. Existing consumers of `report-data.typ` (for MAESTRO, attack-chains, attack-trees, executive-architecture, etc.) MUST remain unaffected — F-B only **appends** new `#let` declarations, never modifies or removes existing ones.

---

## Contract Declarations

### Declaration 1 — `has-source-attribution` Boolean (required)

```typst
#let has-source-attribution = true
// OR
#let has-source-attribution = false
```

**Producer obligations**:

- MUST emit this declaration on every `extract-report-data.py` invocation (no conditional emission).
- Value is `true` iff ≥1 finding in the current threat model carries a non-empty `source_attribution` array; `false` otherwise.
- No implicit defaults — the value is always explicitly derived from the finding set.

**Consumer obligations**:

- `main.typ` §2b defaults block MUST carry a default-value guard:
  ```typst
  #let has-source-attribution = if has-source-attribution != none { has-source-attribution } else { false }
  ```
  This guards against stale `report-data.typ` files that predate F-B (e.g., generated from a pre-F-B pipeline snapshot).
- Conditional inclusion block in `main.typ` MUST gate on both predicates:
  ```typst
  #if has-source-attribution and per-finding-rows.len() > 0 { ... }
  ```
  The `.len() > 0` belt-and-suspenders check mirrors Feature 141 precedent (`main.typ:246`).

### Declaration 2 — `per-finding-rows` Array (required when `has-source-attribution == true`; empty array otherwise)

```typst
#let per-finding-rows = (
  (
    id: "S-001",
    title: "Weak authentication on admin API",
    severity: "high",
    owasp-refs: (
      (id: "LLM05", relationship: "primary"),
    ),
    mitre-refs: (
      (id: "ATT&CK:T1070.001", relationship: "related"),
      (id: "ATLAS:AML.T0051", relationship: "primary"),
    ),
    nist-refs: (),
    cwe-refs: (
      (id: "CWE-1426", relationship: "related"),
    ),
  ),
  (
    id: "S-002",
    title: "...",
    severity: "medium",
    owasp-refs: (),
    mitre-refs: (),
    nist-refs: (),
    cwe-refs: (),
  ),
  // ... one record per finding in input order
)
```

**Producer obligations**:

- Emit exactly one record per finding in the input list, in input order (no re-sort).
- All 4 `*-refs` keys MUST be present on every record (may be empty arrays `()`).
- When `has-source-attribution == false`, emit `#let per-finding-rows = ()` (empty array) to preserve consumer `.len() > 0` check.

**Consumer obligations**:

- `coverage-attestation.typ` renders one row per record.
- For each record, iterate `owasp-refs` / `mitre-refs` / `nist-refs` / `cwe-refs`; render each entry's `id`; apply bold styling when `relationship == "primary"`, plain styling otherwise (`related` / `derived`).
- For records where all 4 `*-refs` are empty, the row still renders with blank ref cells (per FR-006).

### Declaration 3 — `per-framework-aggregates` Array (required when `has-source-attribution == true`; empty array otherwise)

```typst
#let per-framework-aggregates = (
  (
    framework: "owasp",
    yaml-record-count: 60,
    covered-count: 12,
    partial-count: 3,
    gap-count: 45,
    coverage-percentage: "20.00%",
    items: (
      (id: "LLM01", classification: "covered"),
      (id: "LLM02", classification: "partial"),
      (id: "LLM03", classification: "gap"),
      // ... 60 items total in YAML order
    ),
  ),
  (
    framework: "mitre-attack",
    yaml-record-count: 38,
    covered-count: 0,
    partial-count: 0,
    gap-count: 38,
    coverage-percentage: "0.00%",
    items: (
      // ... 38 items, all classified "gap"
    ),
  ),
  (
    framework: "mitre-atlas",
    yaml-record-count: 12,
    covered-count: 2,
    partial-count: 1,
    gap-count: 9,
    coverage-percentage: "16.67%",
    items: ( ... ),
  ),
  (
    framework: "nist-ai-rmf",
    yaml-record-count: 72,
    covered-count: 0,
    partial-count: 4,
    gap-count: 68,
    coverage-percentage: "0.00%",
    items: ( ... ),
  ),
  (
    framework: "cwe",
    yaml-record-count: 53,
    covered-count: 1,
    partial-count: 0,
    gap-count: 52,
    coverage-percentage: "1.89%",
    items: ( ... ),
  ),
)
```

**Producer obligations**:

- Emit exactly 5 records (one per external framework) in the fixed order: `owasp`, `mitre-attack`, `mitre-atlas`, `nist-ai-rmf`, `cwe`.
- `yaml-record-count` equals `len(yaml.safe_load(schemas/taxonomy/{framework}.yaml))` at invocation time (computed once, cached per-run).
- Partition invariant: `covered-count + partial-count + gap-count == yaml-record-count`.
- `coverage-percentage` format: `"X.XX%"` for finite percentages; `"N/A"` when `yaml-record-count == 0`.
- `items` preserves YAML iteration order.
- When `has-source-attribution == false`, emit `#let per-framework-aggregates = ()` (empty array).

**Consumer obligations**:

- `coverage-attestation.typ` renders one page per record (always 5 pages when `has-source-attribution == true`, per Q4 resolution).
- Per-framework page renders: framework title, coverage summary (`"Covered: K/N = X.XX% · Partial: P · Gap: G"`), and the 3 item-group visualizations.
- Gap items highlighted with WCAG AA color + icon (color alone insufficient — FR-010).

---

## Boolean / Type Mapping (Python → Typst)

| Python value | Typst emission |
|--------------|----------------|
| `True` | `true` |
| `False` | `false` |
| `int` | `42` (numeric literal) |
| `str` | `"..."` (quoted string, with Typst-escape of `"` and `\`) |
| `list[T]` | `(...)` (Typst array) |
| `dict[str, T]` | `(key: value, ...)` (Typst dictionary) |
| `None` | NOT emitted — consumer uses default-value guard |

---

## Backward Compatibility

**Pre-F-B consumers** (stale `report-data.typ` generated against older `extract-report-data.py`):

- `has-source-attribution` is absent from the data file
- `main.typ` default-value guard catches this → forces `has-source-attribution = false`
- `per-finding-rows` and `per-framework-aggregates` may also be absent; a matching guard block ensures empty-array default:
  ```typst
  #let per-finding-rows = if per-finding-rows != none { per-finding-rows } else { () }
  #let per-framework-aggregates = if per-framework-aggregates != none { per-framework-aggregates } else { () }
  ```
- Net effect: stale `report-data.typ` compiles without error and omits the coverage-attestation section entirely — preserving pre-F-B PDF output (SC-004a).

**Consumer (`main.typ`) migration**: 3 coordinated edits required to land simultaneously at F-B merge. No gradual rollout — `main.typ` MUST ship with all 3 edits (default guard + `#import` + conditional block) in the same PR to avoid intermediate broken states.

---

## Validation & Testing

Contract validation is covered by aggregator unit tests:

- **Test fixture A (empty)** — finding list with zero findings carrying `source_attribution`:
  - Asserts `has-source-attribution == false`
  - Asserts `per-finding-rows` emits empty array
  - Asserts `per-framework-aggregates` emits empty array (or is entirely omitted — producer choice, consumer is guarded)

- **Test fixture B (one-primary)** — finding list with exactly one finding carrying one `primary` attribution:
  - Asserts `has-source-attribution == true`
  - Asserts `per-finding-rows` has exactly one row
  - Asserts `per-framework-aggregates` has exactly 5 records
  - Asserts one framework has `covered-count: 1, partial-count: 0, gap-count: N-1, coverage-percentage: "1/N as percentage"`
  - Asserts other 4 frameworks have `covered-count: 0, partial-count: 0, gap-count: N, coverage-percentage: "0.00%"`

- **Test fixture C (multi-mixed)** — finding list with multiple findings, mixed `primary`/`related`/`derived` across ≥2 frameworks:
  - Asserts `covered-count` / `partial-count` / `gap-count` partition invariant holds
  - Asserts classification rules (Q1-A: Partial = `related`/`derived`-only)
  - Asserts `coverage_percentage` arithmetic matches hand-computed expected values

Integration test (SC-002): byte-identity on 5 non-agentic baselines under `SOURCE_DATE_EPOCH=1700000000`.

---

## Invariants Enforced at Contract Boundary

| Invariant | Producer | Consumer |
|-----------|----------|----------|
| `has-source-attribution` is always emitted | ✓ (unconditional) | ✓ (default-value guard catches stale data) |
| `per-finding-rows` order matches finding input order | ✓ | — (renders in emitted order) |
| `per-framework-aggregates` always 5 records in fixed order | ✓ (when has-source-attribution == true) | ✓ (renders 1 page per record) |
| Partition invariant on Covered + Partial + Gap | ✓ (asserted in unit tests) | — (presentational) |
| Primary-only numerator in `coverage-percentage` | ✓ | — (displays as given) |
| Gap items rendered with color + icon (WCAG AA) | — | ✓ (Q5 memo → Typst styling) |
| Entire section omitted when either gate predicate is false | — | ✓ (conditional block) |

---

## References

- FR-002 through FR-012 (contract semantics)
- SC-003, SC-004 (boolean + guard + conditional block correctness)
- SC-005 (coverage-percentage arithmetic)
- SC-006 (visual treatment)
- data-model.md (entity shapes)
- Feature 141 precedent: `main.typ:246`, `extract-report-data.py:1426`
- Feature 128 precedent: `main.typ:89`, `extract-report-data.py:1362`
