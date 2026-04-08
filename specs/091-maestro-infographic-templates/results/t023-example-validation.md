# T023: Example Architecture Validation Results

**Date**: 2026-04-08
**Status**: PASS
**Examples tested**: 6 (+ 1 pre-MAESTRO degradation test)
**Total extraction runs**: 14 (6 examples x 2 templates + 2 sample-report)

## Summary

All 6 example architectures produce valid MAESTRO JSON for both `maestro-stack` and `maestro-heatmap` templates. The pre-MAESTRO sample-report degrades gracefully with empty fields and no errors.

## Results by Example

| Example | MAESTRO Data | Layers | Stack Exit | Heatmap Exit | Findings | most_exposed_layer |
|---------|-------------|--------|------------|-------------|----------|-------------------|
| agentic-app | Yes | 5 | 0 | 0 | 22 | L1 -- Foundation Model |
| ascii-web-api | Yes | 4 | 0 | 0 | 11 | L5 -- Security |
| free-text-microservice | Yes | 3 | 0 | 0 | 15 | L4 -- Deployment Infrastructure |
| mermaid-agentic-app | Yes | 4 | 0 | 0 | 19 | L1 -- Foundation Model |
| microservices | Yes | 3 | 0 | 0 | 23 | L4 -- Deployment Infrastructure |
| web-app | Yes | 4 | 0 | 0 | 16 | L4 -- Deployment Infrastructure |

### Pre-MAESTRO Graceful Degradation

| Test | has_maestro_data | layer_distribution | most_exposed_layer | Exit |
|------|-----------------|-------------------|-------------------|------|
| agentic-app/sample-report (stack) | false | [] | "" | 0 |
| agentic-app/sample-report (heatmap) | false | [] | N/A | 0 |

Note: sample-report is Tier 1 (compensating-controls.md present) with schema_version 1.1 (pre-Feature 084). Warnings about residual severity band mismatches are expected and do not affect MAESTRO extraction.

## Validations Performed

1. **Exit codes**: All 14 runs exited with code 0 (success)
2. **JSON validity**: All 14 outputs parse as valid JSON
3. **Field presence**: All template_data fields present (has_maestro_data, maestro_layer_distribution, most_exposed_layer/maestro_heatmap)
4. **Structural integrity**:
   - Stack: layer dicts have layer_id, layer_name, finding_count, highest_severity
   - Stack: per_layer_summaries have top_findings with id and threat (max 2 per layer)
   - Heatmap: each row has component and layers dict with all L1-L7 keys
5. **Cross-check (SC-005)**: Layer distribution finding counts match Section 6 "Risk by MAESTRO Layer" in threats.md for all 6 examples
6. **Graceful degradation**: Pre-MAESTRO output returns has_maestro_data=false, empty distributions, empty most_exposed_layer, no errors

## Acceptance Criteria Coverage

| Criterion | Status |
|-----------|--------|
| SC-005: most_exposed_layer matches Section 6 | PASS |
| SC-006: All 6 examples compile with updated pipeline | PASS |
| AC 8.2: Pre-084 output defaults to empty/null without errors | PASS |
| FR-007: MAESTRO sections gated by data-presence flag | PASS |
