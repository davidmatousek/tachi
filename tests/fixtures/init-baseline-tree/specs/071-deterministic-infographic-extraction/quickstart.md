# Quickstart: Deterministic Infographic Extraction

## Prerequisites

- Python 3.9+
- tachi repository cloned with example datasets

## Running the Script Directly

```bash
# Baseball card (Tier 1 — compensating-controls.md available)
python scripts/extract-infographic-data.py \
  --target-dir examples/agentic-app/sample-report \
  --template baseball-card \
  --output /tmp/baseball-card.json

# System architecture
python scripts/extract-infographic-data.py \
  --target-dir examples/agentic-app/sample-report \
  --template system-architecture \
  --output /tmp/system-architecture.json

# Risk funnel
python scripts/extract-infographic-data.py \
  --target-dir examples/agentic-app/sample-report \
  --template risk-funnel \
  --output /tmp/risk-funnel.json
```

## Verifying Determinism

```bash
# Run twice, diff should show zero differences
python scripts/extract-infographic-data.py \
  --target-dir examples/agentic-app/sample-report \
  --template baseball-card \
  --output /tmp/run1.json

python scripts/extract-infographic-data.py \
  --target-dir examples/agentic-app/sample-report \
  --template baseball-card \
  --output /tmp/run2.json

diff /tmp/run1.json /tmp/run2.json
# Expected: no output (files identical)
```

## Verifying Cross-Output Consistency

```bash
# Run both scripts on same input
python scripts/extract-report-data.py \
  --target-dir examples/agentic-app/sample-report \
  --output /tmp/report-data.typ \
  --template-dir templates/tachi/security-report

python scripts/extract-infographic-data.py \
  --target-dir examples/agentic-app/sample-report \
  --template baseball-card \
  --output /tmp/infographic.json

# Compare severity counts (manual inspection)
# report-data.typ: #let severity-critical = 5
# infographic.json: "severity_distribution"[0].count = 5
```

## Exit Codes

| Code | Meaning | Action |
|------|---------|--------|
| 0 | Success | JSON written to --output path |
| 1 | Missing required artifact | Check that threats.md exists in --target-dir |
| 2 | Validation failure | Check stderr for specific failure details |

## Testing All Tiers

```bash
# Tier 1 (compensating-controls.md present)
python scripts/extract-infographic-data.py \
  --target-dir examples/agentic-app/sample-report \
  --template baseball-card --output /tmp/tier1.json

# Tier 3 (threats.md only)
python scripts/extract-infographic-data.py \
  --target-dir examples/mermaid-agentic-app \
  --template baseball-card --output /tmp/tier3.json
```
