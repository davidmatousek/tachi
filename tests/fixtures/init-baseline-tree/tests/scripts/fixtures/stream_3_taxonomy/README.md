# Stream 3 Taxonomy Fixtures (F-241 T048)

Synthetic taxonomy YAML subsets exercising the F-241 Stream 3 record-shape
extension (`out_of_scope: bool` + `out_of_scope_rationale: string` per ADR-037
D-7). These fixtures are scoped to validating the `_load_framework_yaml_records`
filter behavior at `scripts/extract-report-data.py` line 1073 and the in-scope
denominator semantic at line 1144 (`_build_per_framework_aggregate`).

## Fixture Inventory

| Fixture File | Purpose | Record Mix |
|---|---|---|
| `mixed_in_scope_and_oos.yaml` | Mixed `out_of_scope: true` + `out_of_scope: false` records | 5 records: 3 in-scope, 2 OOS |
| `omits_oos_field.yaml` | Pre-F-241 backward-compat — records that omit `out_of_scope` entirely (treated as in-scope) | 4 records, none with the field |
| `with_rationale.yaml` | Records with `out_of_scope_rationale` populated (verbatim T040 + derived patterns) | 4 records: 2 verbatim, 2 derived |
| `empty_yaml.yaml` | Empty YAML (zero-denominator case) | 0 records |
| `all_oos.yaml` | Entirely-Out-of-Scope framework (coverage_percentage = "N/A") | 3 records, all OOS |

## Record Shape (per `schemas/finding.yaml` v1.8 / data-model.md §2)

Each record carries:
- `id` — short canonical ID
- `full_id` — framework-prefixed ID
- `name` — verbatim canonical name
- `url` — retrievable URL
- `cwe_refs` — list of CWE IDs (empty for ATT&CK/ATLAS)
- `out_of_scope` (optional) — `bool`, default `false`
- `out_of_scope_rationale` (optional) — `string`, default `""`

## Used By

- `tests/scripts/test_coverage_attestation.py` (post-T048 expansion)

## Conventions

These fixtures are SYNTHETIC — IDs do not necessarily match real OWASP /
ATT&CK / ATLAS catalog entries. The intent is to exercise the filter
semantics at the loader level, not catalog correctness. Real-catalog
fidelity is exercised by the live taxonomy YAMLs at `schemas/taxonomy/*.yaml`.
