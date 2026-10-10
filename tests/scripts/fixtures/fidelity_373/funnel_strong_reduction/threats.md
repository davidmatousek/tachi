---
schema_version: "1.4"
date: "2026-01-08"
input_format: "mermaid"
classification: "confidential"
run_id: "2026-01-08T00-00-00"
baseline:
  source: null
  date: null
  finding_count: null
  run_id: null
coverage_gate:
  status: "pass"
  gaps: []
---

# Threat Model: Synthetic Fixture — K11 Funnel, Strong Reduction / FLOOR-bound (F-373)

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
| T-1 | NEW | Denial of Service | — | API Gateway | Unclassified | Synthetic threat T-1 | Medium | Apply per-IP rate limiting |
| T-2 | NEW | Elevation of Privilege | — | Backend Service | Unclassified | Synthetic threat T-2 | Medium | Apply least-privilege access control |
