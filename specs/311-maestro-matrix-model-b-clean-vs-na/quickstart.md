# Quickstart / Verification Runbook: MAESTRO Matrix Model B

**Feature**: 311 · **Spec**: [spec.md](./spec.md) · **Plan**: [plan.md](./plan.md)

Verifies the clean-vs-n/a distinction renders identically on all three surfaces, the CI gate catches divergence, and determinism is preserved. Run from repo root.

## Pre-req

```bash
export SOURCE_DATE_EPOCH=1700000000        # PDF byte-determinism pin (ADR-021)
python3 -c "import pytest"                  # pytest available
# Typst + mmdc toolchain available for the PDF regen step (ADR-022)
git tag | grep -q v4.40.0 || echo "WARN: v4.40.0 tag not local yet (confirm before /aod.deliver)"
```

## 1. The classifier (unit — fastest signal)

```bash
python3 -m pytest tests/scripts/ -k "coverage_state or classify" -v
```
Expect: clean token → `clean`; n/a token → `not_applicable`; `>0` → `findings`; empty → `clean`; ordinal-0 for both zero-finding tokens.

## 2. threats.md source (the authored token) — `microservices`

```bash
grep -A10 "Risk by MAESTRO Layer" examples/microservices/threats.md
```
Expect (after build): L1/L3/L5/L6 → `Not applicable — no components map to this layer`; L7 → `Analyzed — no findings this scan`; L2/L4 → `Critical`.

## 3. PDF surface parity

```bash
python3 scripts/extract-report-data.py --target-dir examples/microservices \
  --output templates/tachi/security-report/report-data.typ \
  --template-dir templates/tachi/security-report
grep -i "coverage_state\|not applicable\|Analyzed" templates/tachi/security-report/report-data.typ
```
Expect: per-layer `coverage_state` present; L7=`clean`, L1/L3/L5/L6=`not_applicable`. Then `typst compile templates/tachi/security-report/main.typ /tmp/ms.pdf --root .` and confirm the MAESTRO page shows a **distinct** n/a line vs the clean line.

## 4. Infographic surface parity

```bash
python3 scripts/extract-infographic-data.py --target-dir examples/microservices \
  --template maestro-stack --output /tmp/maestro-stack.json
python3 -c "import json;d=json.load(open('/tmp/maestro-stack.json'));print([(l['layer_id'],l.get('coverage_state')) for l in d['template_data']['per_layer_summaries']])"
```
Expect: `[(L1,not_applicable),(L2,findings),(L3,not_applicable),(L4,findings),(L5,not_applicable),(L6,not_applicable),(L7,clean)]` — agrees with the PDF (step 3). Confirm `component_layer_map` did NOT drive this (D3 fence).

## 5. Cross-surface consistency gate (the regression anchor)

```bash
python3 -m pytest tests/scripts/test_maestro_coverage_invariant.py \
  tests/scripts/test_maestro_cross_surface_consistency.py -v
```
Expect green: the invariant test asserts all-7-rows present; the dedicated `test_maestro_cross_surface_consistency.py` module asserts all three surfaces agree on every layer for `microservices` (threats.md classifier == PDF IR == infographic IR).

**Negative check** (prove the gate bites): `test_forced_l7_divergence_is_caught` automates this — it tampers one surface's L7 to `not_applicable` and asserts the consistency check fails **naming L7** (and only L7). To exercise it manually, re-route the stack to `component_layer_map` and confirm the failure names `L7`, then revert.

## 6. Determinism / baseline (SC-004)

```bash
SOURCE_DATE_EPOCH=1700000000 python3 -m pytest tests/scripts/test_backward_compatibility.py -v
```
Expect: 6 byte-gated baselines byte-identical **after** intentional re-freeze. For each n/a-bearing example, regenerate and confirm the diff is **annotation-only** ([MANUAL-ONLY]).

## 7. No schema drift (SC-003)

```bash
git diff --stat -- '**/*.sarif' schemas/   # expect: no changes
/aod.analyze                                # expect: 0 inconsistencies
```

## Done when

- [ ] Steps 1–5 green; step 5 negative check fails on L7 then reverts clean.
- [ ] Step 6: gated baselines byte-identical post-refreeze; n/a diffs annotation-only.
- [ ] Step 7: zero SARIF/schema changes; `/aod.analyze` clean.
- [ ] All three surfaces show L7=clean, L1/L3/L5/L6=n/a for `microservices`.
