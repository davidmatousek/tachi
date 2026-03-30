# Quickstart: Deterministic Report Data Extraction

## What Changed

The `/security-report` command now uses a deterministic Python script instead of LLM-based parsing to extract data from threat model artifacts. Identical inputs always produce identical output.

## Running the Script Directly

```bash
python3 scripts/extract-report-data.py \
  --target-dir examples/agentic-app/sample-report \
  --output report-data.typ \
  --template-dir templates/tachi/security-report/
```

### Optional: Title Override
```bash
python3 scripts/extract-report-data.py \
  --target-dir examples/agentic-app/sample-report \
  --output report-data.typ \
  --template-dir templates/tachi/security-report/ \
  --title "My Custom Report Title"
```

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success — `report-data.typ` written |
| 1 | Missing required artifact (threats.md) |
| 2 | Validation failure (severity sum mismatch, duplicate IDs, etc.) |

## Verifying Determinism

```bash
# Run twice
python3 scripts/extract-report-data.py --target-dir examples/agentic-app/sample-report --output /tmp/run1.typ --template-dir templates/tachi/security-report/
python3 scripts/extract-report-data.py --target-dir examples/agentic-app/sample-report --output /tmp/run2.typ --template-dir templates/tachi/security-report/

# Compare
diff /tmp/run1.typ /tmp/run2.typ
# Expected: no output (files are identical)
```

## Using via /security-report (unchanged)

The command works exactly the same as before — the script invocation is handled internally by the report-assembler agent:

```
/security-report examples/agentic-app/sample-report
```

## Prerequisites

- Python 3.9+
- Typst (for PDF compilation)
- At minimum, a `threats.md` file in the target directory
