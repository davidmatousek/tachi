---
schema_version: "1.4"
date: "2026-01-07"
input_format: "mermaid"
classification: "confidential"
run_id: "2026-01-07T00-00-00"
baseline:
  source: null
  date: null
  finding_count: null
  run_id: null
coverage_gate:
  status: "pass"
  gaps: []
---

# Threat Model: Synthetic Fixture — Tier 3 Empty Mitigation (F-373 K13.1)

No `risk-scores.md` and no `compensating-controls.md` are present in this
directory, so `determine_tier` selects data tier 3. `parse_threats_findings`
reads `mitigation` straight from this table's Mitigation column, with no
upstream join, so this is the minimal shape that exercises data-model.md
§7's tier-3 row directly: T-2's Mitigation cell is empty.

## 1. System Overview

### Components

| Component | Type | Description |
|-----------|------|-------------|
| API Gateway | Process | Synthetic request ingress service |
| Backend Service | Process | Synthetic business logic service |

---

## 7. Recommended Actions

| Finding ID | Status | Category | Pattern | Component | MAESTRO Layer | Threat | Risk Level | Mitigation |
|------------|--------|----------|---------|-----------|---------------|--------|------------|------------|
| T-1 | NEW | Denial of Service | — | API Gateway | Unclassified | Synthetic threat with a real mitigation | Critical | Apply per-IP rate limiting at the gateway |
| T-2 | NEW | Elevation of Privilege | — | Backend Service | Unclassified | Synthetic threat with no mitigation text at all | Low |  |
