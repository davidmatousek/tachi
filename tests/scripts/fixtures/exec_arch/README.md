# Executive Architecture Test Fixtures

Fixtures for `tests/scripts/test_extract_infographic_data.py` covering the
`executive-architecture` template in `scripts/extract-infographic-data.py`.

Each subdirectory is a self-contained `--target-dir` argument for the
extraction script.

## Fixtures

| Fixture | Contains | Tests |
|---------|----------|-------|
| `agentic_app/` | Verbatim copies of `threats.md`, `risk-scores.md`, `compensating-controls.md` from `examples/agentic-app/sample-report/` | Happy path (12+ layers + callouts), tier detection (risk-scores, compensating-controls), determinism |
| `no_critical_high/` | Synthetic `threats.md` with only Medium/Low/Note severity findings | `skip_image == True` branch |
| `no_trust_zones/` | Synthetic `threats.md` with populated Section 1 components (DFD type field set) but empty Section 2 Trust Zones table | DFD type fallback (`source_kind == "dfd_type"`, `fallback_used == True`) |
| `no_scope_data/` | Synthetic `threats.md` with both Section 1 AND Section 2 tables empty | Exit code 2 (validation failure) |
| `mixed_case_components/` | Synthetic `threats.md` where trust zones list `API Gateway` while findings reference `api-gateway`, `auth_service`, `database` | Architect L-1: component name normalization |
| `orphaned_finding/` | Synthetic `threats.md` with one Critical finding referencing `Component D` which is not in any trust zone or component table | Architect L-1: orphaned findings dropped from callouts |
| `multiple_per_layer/` | Synthetic `threats.md` with one trust zone containing 5 components, each with a Critical finding | Per-layer dedup tie-break (one callout per layer, selected by severity desc → composite score desc → finding ID asc) |

## Notes on Synthetic Fixtures

- Frontmatter matches the `schema_version: "1.1"` format used in existing `examples/`.
- Section headings (Sections 1, 2, 3, 7) match `parse_scope_data()` and `parse_threats_findings()` in `scripts/tachi_parsers.py`.
- Synthetic fixtures contain a minimal but parseable structure — they are not meant to represent realistic threat models.
