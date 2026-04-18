# Quickstart: Coverage Attestation Report Section

**Feature**: 194
**Phase**: 1 — Design & Contracts (verification walkthrough)
**Date**: 2026-04-18

This quickstart walks through verifying F-B after all 4 days of implementation work land. Each step is independently verifiable and matches a spec SC.

---

## Prerequisites

- tachi repository checked out on branch `194-coverage-attestation-report-section`
- Python 3.11 with `pyyaml` installed (already in `requirements.txt`)
- `pytest` installed (already in `requirements-dev.txt`)
- Typst installed (pre-existing requirement — `brew install typst` on macOS)
- `mmdc` NOT required for F-B verification (F-B produces no Mermaid content)

---

## Step 1 — Aggregator Unit Tests (Day 2 deliverable)

Verifies FR-002, FR-003, FR-007, FR-008, FR-011, SC-003, SC-005, SC-011.

```bash
cd /Users/david/Projects/tachi
pytest tests/scripts/test_coverage_attestation.py -v
```

**Expected output**: all unit tests green. Key tests:

- `test_has_source_attribution_false_on_empty_attribution_fixture` — empty fixture → `has_source_attribution: False`
- `test_has_source_attribution_true_on_one_primary_fixture` — one-primary fixture → `has_source_attribution: True`
- `test_coverage_percentage_arithmetic_matches_hand_computed` — multi-mixed fixture → hand-computed coverage percentages
- `test_partition_invariant_covered_plus_partial_plus_gap_equals_yaml_count` — partition invariant holds on every framework aggregate
- `test_coverage_percentage_na_on_zero_denominator` — synthetic zero-item YAML → `"N/A"`
- `test_coverage_percentage_zero_pct_on_zero_numerator` — N-item YAML, 0 findings match → `"0.00%"`
- `test_aggregator_fails_loud_on_malformed_yaml` — corrupt YAML → clear error bubbles up

---

## Step 2 — Backward-Compatibility Gate (Day 4 deliverable)

Verifies FR-003, FR-004, SC-002, SC-004. THE BLOCKER gate.

```bash
cd /Users/david/Projects/tachi
SOURCE_DATE_EPOCH=1700000000 pytest tests/scripts/test_backward_compatibility.py -v
```

**Expected output**: 5 of 5 non-agentic baselines regenerate byte-identical to their committed `.pdf.baseline` files:

- `examples/web-app/`
- `examples/microservices/`
- `examples/ascii-web-api/`
- `examples/free-text-microservice/`
- `examples/maestro-reference/`

If any baseline regenerates non-byte-identically, F-B cannot merge. Diagnostic: compare the generated PDF to the baseline using `diff` and inspect the failing `main.typ` render path.

---

## Step 3 — Typst Compile Smoke on Populated Fixture (Day 3 deliverable)

Verifies SC-001, SC-012, FR-001, FR-005, FR-007, FR-012.

```bash
cd /Users/david/Projects/tachi
# Regenerate report-data.typ from the multi-mixed fixture
python scripts/extract-report-data.py \
    --input tests/scripts/fixtures/coverage_attestation/multi_mixed_attribution.yaml \
    --output /tmp/report-data-mixed.typ

# Compile the security report using this data contract
typst compile \
    --input data-file=/tmp/report-data-mixed.typ \
    templates/tachi/security-report/main.typ \
    /tmp/security-report-mixed.pdf
```

**Expected output**:

- `typst compile` exits 0 (no compile errors)
- `/tmp/security-report-mixed.pdf` opens and displays the coverage-attestation section between MAESTRO-findings and compensating-controls
- Per-finding table renders with 7 columns (Finding ID | Title | Severity | OWASP refs | MITRE refs | NIST refs | CWE refs)
- `primary` citations render bold; `related`/`derived` citations render plain
- 5 per-framework pages render in order: OWASP, MITRE ATT&CK, MITRE ATLAS, NIST AI RMF, CWE
- Each per-framework page displays `Covered: K/N = X.XX% · Partial: P · Gap: G` with equal visual weight

---

## Step 4 — Pagination Smoke on 100-Finding Synthetic Fixture (Day 3 deliverable)

Verifies FR-012, SC-010, SC-012.

```bash
cd /Users/david/Projects/tachi
python tests/scripts/generate_pagination_fixture.py \
    --finding-count 100 --frameworks 5 \
    --output /tmp/pagination-smoke.yaml

python scripts/extract-report-data.py \
    --input /tmp/pagination-smoke.yaml \
    --output /tmp/report-data-pagination.typ

typst compile \
    --input data-file=/tmp/report-data-pagination.typ \
    templates/tachi/security-report/main.typ \
    /tmp/security-report-pagination.pdf
```

**Expected output**:

- `typst compile` exits 0
- `/tmp/security-report-pagination.pdf` renders acceptably on portrait US Letter:
  - Per-finding table paginates across multiple pages using Typst native row-break
  - No content clipped; no overflow into margins
  - Font size remains readable (no shrink-to-fit artifacts)
- Typst compile time adds ≤2s to the pipeline budget
- If pagination is unacceptable → activate landscape-orientation or per-severity-split fallback (pre-approved per FR-012)

---

## Step 5 — Default-Value Guard on Stale Data (Day 3 deliverable)

Verifies FR-004, SC-004a.

```bash
cd /Users/david/Projects/tachi
# Simulate a stale report-data.typ (pre-F-B, missing has-source-attribution)
grep -v 'has-source-attribution\|per-finding-rows\|per-framework-aggregates' \
    /tmp/report-data-mixed.typ > /tmp/report-data-stale.typ

# Compile with stale data
typst compile \
    --input data-file=/tmp/report-data-stale.typ \
    templates/tachi/security-report/main.typ \
    /tmp/security-report-stale.pdf
```

**Expected output**:

- `typst compile` exits 0 — NO "variable not found" error
- `/tmp/security-report-stale.pdf` renders WITHOUT the coverage-attestation section (section entirely omitted by the default-value guard + conditional block)

---

## Step 6 — Zero-Edit Invariant Grep Audit (Ongoing / PR pre-merge)

Verifies FR-014, SC-009.

```bash
cd /Users/david/Projects/tachi
# 22-file scope: 11 agents + 11 skill-references
git diff --name-only main...HEAD | \
    grep -E '^\.claude/(agents/tachi/(stride|ai)/.*\.md|skills/tachi-.*/references/detection-patterns\.md)$' && \
    echo "VIOLATION — files in zero-edit scope were modified" || \
    echo "PASS — zero-edit invariant preserved"
```

**Expected output**: `PASS — zero-edit invariant preserved`

---

## Step 7 — Zero-Dependency Invariant (Ongoing / PR pre-merge)

Verifies FR-016, SC-008.

```bash
cd /Users/david/Projects/tachi
git diff main...HEAD -- pyproject.toml requirements.txt requirements-dev.txt package.json
```

**Expected output**: empty diff (no lines output). Any output indicates a dependency was added and F-B is violating FR-016.

---

## Step 8 — ADR-029 Governance (Day 1 + Day 4 deliverables)

Verifies FR-013, SC-007.

**Day 1** (Proposed commit):

```bash
cd /Users/david/Projects/tachi
head -5 docs/architecture/02_ADRs/ADR-029-coverage-attestation-report-section.md
```

**Expected**: Status line reads `Status: Proposed` and is committed on Day 1 Wave 1.0.

**Day 4** (Accepted commit, pre-merge):

```bash
head -5 docs/architecture/02_ADRs/ADR-029-coverage-attestation-report-section.md
```

**Expected**: Status line reads `Status: Accepted` with date `2026-04-23` (provisional) and a `<pending-post-merge-fill>` placeholder for merge SHA.

**Post-merge** (SHA fill commit directly to main):

```bash
git log -1 --format="%H" -- main
grep "merge-sha" docs/architecture/02_ADRs/ADR-029-coverage-attestation-report-section.md
```

**Expected**: ADR has the actual squash merge SHA filled in (replacing `<pending-post-merge-fill>`).

---

## Step 9 — End-to-End Sanity on a Baseline (No-op Check)

Verifies SC-002 from the consumer's perspective — running the full pipeline on any baseline produces a PDF with NO coverage-attestation section.

```bash
cd /Users/david/Projects/tachi
cd examples/web-app  # any of the 5 non-agentic baselines
SOURCE_DATE_EPOCH=1700000000 python ../../scripts/run-pipeline.py  # or the existing pipeline command
```

**Expected**:

- Pipeline exits 0
- Generated `security-report.pdf` is byte-identical to `security-report.pdf.baseline`
- Manual PDF inspection: no coverage-attestation section rendered (no page with title "Coverage Attestation", no per-finding attribution table, no per-framework matrix pages)

---

## Success Criteria Summary

After all 9 steps pass, F-B meets all 12 spec SCs:

| Step | Verifies |
|------|----------|
| 1 | SC-003, SC-005, SC-011 (aggregator correctness) |
| 2 | SC-002, SC-004 (byte-identity) |
| 3 | SC-001, FR-001, FR-005, FR-007 (Typst render) |
| 4 | SC-010, SC-012 (performance + pagination) |
| 5 | SC-004a (default-value guard) |
| 6 | SC-009 (22-file zero-edit) |
| 7 | SC-008 (zero dependencies) |
| 8 | SC-007 (ADR-029) |
| 9 | SC-002 (end-to-end byte-identity) |

SC-006 (color-blind accessibility) is verified visually against the ux-ui-designer memo and does not require a command-line step.

---

## Troubleshooting

**"Typst variable not found: has-source-attribution"** — The default-value guard in `main.typ` §2b is missing or malformed. Verify FR-004 / SC-004a edit landed correctly.

**"Baseline regenerated non-byte-identically"** — SC-002 BLOCKER regression. Run `diff` between the generated PDF and baseline; the diff typically indicates an accidental `main.typ` edit that emits bytes even when the gate is false. Inspect the `main.typ` conditional block and the `#import` statement for unconditional rendering.

**"Aggregator raises yaml.YAMLError"** — FR-011(c) fail-loud triggered. Inspect the reported framework YAML path and verify it's not corrupted. Expected behavior per ADR-022 — surface the error, don't silently emit empty aggregates.

**"Per-framework page shows 887 items for OWASP instead of 60"** — Aggregator is counting nested structure, not top-level records. Verify `len(yaml.safe_load(...))` is computed against the top-level list, not recursively.
