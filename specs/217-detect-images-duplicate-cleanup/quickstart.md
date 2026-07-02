# Quickstart: Detect-Images Duplicate Cleanup (F-217)

## Normal (safe default — no cleanup)

```bash
python3 scripts/extract-report-data.py \
  --target-dir <assessment-dir> \
  --template-dir templates/tachi/security-report \
  --output /tmp/report-data.typ
# Mislabeled/corrected pairs are tolerated; nothing is deleted. Byte-identical to pre-F-217 behavior.
```

## Opt-in cleanup of mislabeled duplicates

```bash
python3 scripts/extract-report-data.py \
  --target-dir <assessment-dir> \
  --template-dir templates/tachi/security-report \
  --output /tmp/report-data.typ \
  --cleanup-mislabeled-images
# Deletes a mislabeled image ONLY when a byte-identical correctly-labeled counterpart exists.
# One stderr line per deletion; failures log to stderr and never fail the run.
```

## Verify path-invariance (the US-2 safety proof)

```bash
python3 scripts/extract-report-data.py --target-dir <dir> --template-dir <tpl> --output /tmp/before.typ
python3 scripts/extract-report-data.py --target-dir <dir> --template-dir <tpl> --output /tmp/after.typ --cleanup-mislabeled-images
diff /tmp/before.typ /tmp/after.typ && echo "path-invariant ✓"
```

## Run the tests (local-only suites — not in the CI pytest gate)

```bash
python3 -m pytest tests/scripts/test_extract_report_data.py tests/scripts/test_extractor_contract_fixes.py -v
```

Build-stage reminders: record pre-state pytest totals before touching code (KB Entry 15); commit before running the gated 15-module subset (harness clones committed HEAD).

## In-repo dogfood target (US-2)

`examples/agentic-app/test-output/2026-04-19T03-20-30/` — 6 mislabeled `.jpg` (PNG bytes) + byte-identical `.png` pairs, ~6.75 MB reclaimable.
