# Quickstart / Runbook: MAESTRO 7-Layer Coverage (Feature 098)

A short operational runbook for implementing and verifying Feature 098. Assumes repo root `/Users/david/Projects/tachi` and the existing tachi toolchain (`python3`, `typst`, `pytest`).

## Canonical constants (pin these — do not re-derive)
- **Canonical layers**: import `MAESTRO_LAYERS = ["L1".."L7"]` from `scripts/tachi_parsers.py` (also re-exported as `_MAESTRO_LAYERS` in `extract-report-data.py`). Never hard-code a second list.
- **Zero-finding annotation (Decision A)**: `Analyzed — no findings this scan` (markdown cell; PDF literal adds a trailing period).
- **Determinism epoch (ADR-021)**: `SOURCE_DATE_EPOCH=1700000000` for every PDF (re)generation and the backward-compat test.
- **In-scope tables (9)**: the carries-a-MAESTRO-table set in plan.md Decision E. Exclude the 2 table-less sample-reports and all `test-output/` snapshots.

## 1. Production-surface edits (4 points)
```
.claude/agents/tachi/orchestrator.md         # ~line 718: omit→always-7, severity-desc→canonical L1→L7, + annotation
.claude/skills/tachi-orchestration/references/output-schemas.md  # ~237-238: Ordering + Omission bullets + annotation in cell schema
scripts/extract-report-data.py               # line 407: drop the `if layer_groups[lid]["findings"]` clause
templates/tachi/security-report/maestro-findings.typ  # line 154: literal → "Analyzed — no findings this scan."
```

## 2. Build the populator
`scripts/populate-maestro-coverage.py` (stdlib-only, modeled on `scripts/populate-affected-assets.py`; **examples-regeneration only — never wire into a command/orchestrator phase**):
- Discover the table **heading-level-agnostically** (`^#{3,4}\s+Risk by MAESTRO Layer`) — 3 in-scope files use `### ` (h3), 6 use `#### ` (h4). **Normalize h3 → `#### `** on write (the PDF extractor substring-matches `#### `, so an h3 heading parses to 0 layers).
- Parse the table → map `layer_id → (count, severity)`.
- Emit all 7 canonical layers in L1→L7 order; present layers keep `(count, severity)`; absent layers → `0` + annotation (U+2014 em dash).
- Preserve a trailing conditional `Unclassified` row (move it to the bottom if currently mid-table).
- Idempotent regex upsert of the table block; `--check` mode exits non-zero on drift.
```bash
# regenerate one file
python3 scripts/populate-maestro-coverage.py --threats examples/agentic-app/threats.md
# verify no drift (CI / regression)
python3 scripts/populate-maestro-coverage.py --check examples/agentic-app/threats.md
```

## 3. Regenerate the 9 example tables
Run the populator over each in-scope file (see plan.md Decision E for the list). `maestro-reference` is re-order-only.

## 4. Regenerate the 6 gated PDF baselines (deterministic)
The exact two-step pipeline `tests/scripts/test_backward_compatibility.py:88-120` validates against. For each example in {web-app, microservices, ascii-web-api, mermaid-agentic-app, free-text-microservice, maestro-reference}:
```bash
SOURCE_DATE_EPOCH=1700000000 python3 scripts/extract-report-data.py \
  --target-dir examples/<ex> \
  --output templates/tachi/security-report/report-data.typ \
  --template-dir templates/tachi/security-report
SOURCE_DATE_EPOCH=1700000000 typst compile \
  templates/tachi/security-report/main.typ \
  examples/<ex>/security-report.pdf.baseline --root .
rm -f templates/tachi/security-report/report-data.typ
```
Confirm only matrix rows/order changed — review the `examples/agentic-app/` diff in the PR.

## 5. Tests
```bash
pytest tests/scripts/test_extract_report_data.py          # filter-removal: 7-row table → 7 retained, zero-finding group empty
pytest tests/scripts/test_maestro_coverage_invariant.py   # NEW: every examples/**/threats.md (excl. test-output/) with a MAESTRO table has all 7 L-IDs
pytest tests/scripts/test_backward_compatibility.py       # 6 baselines byte-identical under SOURCE_DATE_EPOCH=1700000000
```

## 6. Gate + close
```bash
# /aod.analyze must pass (no SARIF/schema drift)
# CHANGELOG.md: feat(098): MAESTRO coverage matrix always shows all 7 layers (Issue #98)
```

## Troubleshooting
- **`init-baseline-tree` test fails on unrelated doc-drift** (F-302 transitive risk): run `tests/fixtures/regenerate-baseline.sh` after confirming placeholder-substitution semantics are intact (INSTITUTIONAL_KNOWLEDGE Entry 9). This is a separate fixture from the PDF `.baseline` gate.
- **A sample-report has no MAESTRO table** (`predictive-ml-app`, `consumer-agent-app`): correct — do NOT add one. The invariant test skips files without the table.
- **PDF shows more/fewer than 7**: confirm the markdown table has exactly 7 canonical rows first (PDF derives from markdown; never add canonical seeding to `extract-report-data.py`).
