# Quickstart / Verification Runbook: F-315

How to verify each story. All commands run from repo root.

## Story 1 — maestro-stack infographic completeness (US-2 / #312)

**Goal**: all 7 layer bands + deterministic counts.

1. **Unit/golden**:
   ```bash
   python -m pytest tests/scripts/test_extract_infographic_data.py -v
   ```
   Confirms the `maestro-stack` `template_data` includes `layers_with_findings`, `empty_layers`, `layer_count`, that `layers_with_findings + empty_layers == 7`, and that the values are correct on a fixture with ≥1 empty layer.

2. **Empty-layer behavior**: generate the maestro-stack spec data for an example whose MAESTRO distribution has <7 finding-bearing layers and confirm the JSON contains all 7 layers (zeros backfilled) and the correct empty count. (e.g. run `scripts/extract-infographic-data.py --template maestro-stack` against such an example and inspect the JSON.)

3. **Determinism**: run the extraction twice on identical input; the JSON payloads are byte-identical (ADR-017).

4. **Heatmap untouched**: confirm `maestro-heatmap` output is unchanged for identical input (FR-004).

## Story 2 — CI durability + non-gated PDF refresh (US-3 / #313)

**Goal**: regressions caught in CI; example PDFs current; gated baselines intact.

1. **Invariant green locally**:
   ```bash
   python -m pytest tests/scripts/test_maestro_coverage_invariant.py -v
   ```
   Passes against the current example set.

2. **Force a regression** (negative test): in a scratch copy of an example `threats.md`, delete one canonical layer row from the "Risk by MAESTRO Layer" table, re-run the invariant test, and confirm it **fails naming the missing layer ID**. Discard the scratch change.

3. **Dedicated job triggers correctly**: confirm `.github/workflows/tachi-maestro-coverage.yml` fires on a MAESTRO-surface path change and that an unrelated change does NOT trigger it (and leaves `tachi-pytest.yml` untouched).

4. **Non-gated PDF refresh** (per Decision C target):
   ```bash
   # normalize the upstream table (idempotent), then regenerate deterministically
   python scripts/populate-maestro-coverage.py examples/<target>/.../threats.md
   SOURCE_DATE_EPOCH=1700000000 <regenerate the PDF via the report pipeline>
   ```
   Then **manually diff** (`[MANUAL-ONLY]`) the regenerated PDF/baseline vs the prior — confirm only MAESTRO row/order churn, no unrelated binary drift.

5. **Gated baselines intact**:
   ```bash
   python -m pytest tests/scripts/test_backward_compatibility.py -v
   ```
   Stays green — the 6 byte-gated baselines are byte-identical and the gated set is unchanged.

## Done when

- SC-001…SC-007 (spec) all verified: all-7 infographic with correct deterministic counts; dedicated CI job fails+names on regression and doesn't cross-fire; non-gated PDFs refreshed with only MAESTRO churn; 6 baselines byte-identical; heatmap/schema/SARIF unchanged; each story independently deliverable.
