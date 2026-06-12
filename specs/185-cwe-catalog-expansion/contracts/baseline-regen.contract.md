# Contract: Coverage Attestation Baseline Regeneration (F-A1.2 / spec FR-006)

**Feature**: 185 · **Date**: 2026-06-11 · Authority: ADR-037 D-9 (intentional CA-page baseline updates), ADR-021 (`SOURCE_DATE_EPOCH` determinism)

## Why this contract exists

`cwe` is a member of `ORDERED_FRAMEWORKS` (`scripts/extract-report-data.py:1076`); the cwe.yaml record count and per-record Covered/Partial/Gap rows render on the Coverage Attestation pages of every generated security report. Growing the catalog 53 → 93 therefore changes the CA pages of all regenerated reports, and `tests/scripts/test_backward_compatibility.py` byte-compares regenerated PDFs against committed baselines. (F-184 did not hit this: `nist-ai-600-1` is not in `ORDERED_FRAMEWORKS`.)

**Empirical pre-state (discovered at plan review, 2026-06-11, verified by both reviewers independently)**: the suite is **already red on main** — #186 grew `mitre-atlas` (also in `ORDERED_FRAMEWORKS`) 30 → 36 without baseline regen; a `pdftotext` page diff attributes 100% of the divergence to the ATLAS Coverage Attestation section (not typst drift). W1-3 is therefore a **repair**, not only protection: the regenerated baselines absorb the inherited ATLAS delta together with the F-185 CWE delta, restoring the suite red → green.

## Scope (Decision D2)

Regenerate exactly the **6 byte-identity-gated baselines** (`BASELINE_EXAMPLES`, test lines 37–44):

| Example | Baseline path |
|---|---|
| web-app | `examples/web-app/security-report.pdf.baseline` |
| microservices | `examples/microservices/security-report.pdf.baseline` |
| ascii-web-api | `examples/ascii-web-api/security-report.pdf.baseline` |
| mermaid-agentic-app | `examples/mermaid-agentic-app/security-report.pdf.baseline` |
| free-text-microservice | `examples/free-text-microservice/security-report.pdf.baseline` |
| maestro-reference | `examples/maestro-reference/security-report.pdf.baseline` |

**Explicitly untouched**: `examples/predictive-ml-app/sample-report/security-report.pdf.baseline` and `examples/mobile-banking-app/sample-report/security-report.pdf.baseline` — excluded from byte-identity gating as "regeneration mutation targets" (test docstring lines 15–23); no test compares their bytes; their CA staleness is recorded in the CHANGELOG entry.

## Regen recipe (per example — mirrors the test body exactly)

```bash
export SOURCE_DATE_EPOCH=1700000000   # MUST equal the test constant — do not change
python3 scripts/extract-report-data.py \
  --target-dir examples/{name} \
  --output templates/tachi/security-report/report-data.typ \
  --template-dir templates/tachi/security-report
typst compile templates/tachi/security-report/main.typ \
  examples/{name}/security-report.pdf.baseline --root .
```

Run sequentially per example (the shared `report-data.typ` is mutated per run — no parallel regen).

## D-9 invariants (verified BEFORE committing the new baselines)

1. **CA-page-only deltas**: per-page text-layer diff (e.g., `pdftotext -f N -l N` old vs new, or equivalent) shows changes confined to Coverage Attestation pages — expected deltas: (a) F-185: `cwe` denominator 53 → 93 (or 53+|add-set|) and +40 Gap rows; (b) **inherited #186 absorb**: `mitre-atlas` denominator 30 → 36 and +6 rows/badges; (c) possible CA pagination growth. Note: where an example's covered count is 0, the printed percentage may remain `0.00%` — the visible delta is denominators and Gap rows, not necessarily the percentage value.
2. **Non-CA pages content-identical**: zero text-layer diff on all non-CA pages. If ANY non-CA delta appears → **halt, do not commit**; first suspect is typst version drift vs the binary that produced the current baselines (Risk R6) — pin/match the version and re-run.
3. **Green restored** (not merely kept): pre-state on main is 6/6 FAIL (inherited #186 ATLAS drift); after committing, `tests/scripts/test_backward_compatibility.py` passes 6/6 (regenerate → byte-compare → green), proving the new baselines are reproducible under the pinned epoch.
4. **Same change-set**: catalog growth (W1-1/W1-2) and baseline regen (W1-3) merge in the same PR.
5. **No residue**: the recipe mutates the shared `templates/tachi/security-report/report-data.typ` — restore it (`git checkout -- templates/tachi/security-report/report-data.typ`) after the final regen so no transient extraction output is committed.

## Acceptance

- `test_backward_compatibility.py` 6/6 green at delivery (spec SC-005) — flipping main's current red.
- Page-diff evidence (CA-only deltas, both F-185 and inherited-#186 attributions) attached to the W1-3 task record / PR.
- CHANGELOG dual-attributes the regen: F-185 CWE growth + absorbed #186 ATLAS delta; the 2 untouched sample-report baselines noted as stale-by-design for CA counts.
