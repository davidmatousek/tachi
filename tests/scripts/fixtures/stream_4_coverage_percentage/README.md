# Stream 4 Coverage-Percentage Fixtures (F-241 T048)

Synthetic finding fixtures + expected aggregate-shape YAML pairs exercising
the F-241 Stream 4 in-scope-only coverage-percentage computation
(per data-model.md §3 + finding-contract.md §2).

## Fixture Pair Inventory

| Finding Fixture | Expected Fixture | Scenario |
|---|---|---|
| `findings_in_scope_only.yaml` | `findings_in_scope_only.expected.yaml` | Finding cites only in-scope items |
| `findings_oos_only.yaml` | `findings_oos_only.expected.yaml` | Finding cites only Out-of-Scope items |
| `findings_mixed.yaml` | `findings_mixed.expected.yaml` | Finding cites mixed in-scope + OOS items |
| `findings_zero_against_all_oos.yaml` | `findings_zero_against_all_oos.expected.yaml` | Zero findings against all-OOS framework |

## Finding Shape

Each finding fixture matches `scripts/tachi_parsers.py::parse_threats_findings`
output — list of dicts with `id`, `component`, `threat`, `risk_level`,
`source_attribution` (list of `{taxonomy, id, relationship}` dicts).

## Expected Aggregate Shape

Each `*.expected.yaml` carries the per-framework aggregate dict shape per
data-model.md §3 / finding-contract.md §2:

```yaml
mitre-attack:
  yaml_record_count: <int>
  in_scope_yaml_record_count: <int>
  covered_count: <int>
  partial_count: <int>
  gap_count: <int>
  coverage_percentage: <"X.XX%" or "N/A">
```

The expected fixtures hand-compute the shape against the LIVE taxonomy YAMLs
(`schemas/taxonomy/*.yaml` post-T037/T038/T041 expansion). When the live
YAMLs change (additional taxonomy expansion or out-of-scope reclassification),
these expected fixtures must be re-derived.

## Used By

- `tests/scripts/test_coverage_attestation.py` (post-T048 expansion)
- (Future) `tests/scripts/test_coverage_percentage_computation.py` (T070,
  Wave 5.1) — independent cross-check that aggregator output matches
  hand-computed coverage percentages.

## F-A2 Referential-Integrity Preservation (T046)

Findings citing Out-of-Scope items render on the per-finding attribution
table for traceability (F-A2 contract) but DO NOT increment `covered_count`
in the aggregator math. The `findings_oos_only.yaml` and
`findings_mixed.yaml` fixtures + their expected pairs codify this contract
under the F-241 Stream 4 / T046 edge case.
