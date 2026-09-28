---
schema_version: "1.4"
date: "2026-01-10"
input_format: "mermaid"
classification: "confidential"
run_id: "2026-01-10T00-00-00"
baseline:
  source: null
  date: null
  finding_count: null
  run_id: null
coverage_gate:
  status: "pass"
  gaps: []
---

# Threat Model: Synthetic Fixture — K11 Funnel, threats-only degraded mode (F-373)

No `risk-scores.md` and no `compensating-controls.md` are present in this
directory, so `determine_tier` selects data tier 3 (threats-only funnel mode):
Tier 1 is real (from this file's Section 7), Tiers 2-4 are all ghost.

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
| T-1 | NEW | Denial of Service | — | API Gateway | Unclassified | Synthetic threat T-1 | Critical | Apply per-IP rate limiting |
| T-2 | NEW | Elevation of Privilege | — | Backend Service | Unclassified | Synthetic threat T-2 | Low | Apply least-privilege access control |
