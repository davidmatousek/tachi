---
schema_version: "1.4"
date: "2026-01-14"
input_format: "mermaid"
classification: "confidential"
run_id: "2026-01-14T00-00-00"
baseline:
  source: null
  date: null
  finding_count: null
  run_id: null
coverage_gate:
  status: "pass"
  gaps: []
---

# Threat Model: Synthetic Fixture — Posture, mmdc-free run (F-373 K13-posture, LOW-9)

No attack-chains.md and no attack-trees/ directory accompany this run, and no
finding's Mitigation text embeds a Mermaid block, so `extract-report-data.py`
can run against this directory without `mmdc` installed. Intended for T025's
stale-`report-data.typ` contract test.

## 1. System Overview

### Components

| Component | Type | Description |
|-----------|------|-------------|
| API Gateway | Process | Synthetic request ingress service |
| Backend Service | Process | Synthetic business logic service |
| Batch Worker | Process | Synthetic background processing service |

---

## 7. Recommended Actions

| Finding ID | Status | Category | Pattern | Component | MAESTRO Layer | Threat | Risk Level | Mitigation |
|------------|--------|----------|---------|-----------|---------------|--------|------------|------------|
| T-1 | NEW | Denial of Service | — | API Gateway | Unclassified | Synthetic threat T-1 | High | Apply per-IP rate limiting |
| T-2 | NEW | Elevation of Privilege | — | Backend Service | Unclassified | Synthetic threat T-2 | Medium | Apply least-privilege access control |
| T-3 | NEW | Information Disclosure | — | Batch Worker | Unclassified | Synthetic threat T-3 | Low | Mask sensitive fields in logs |
