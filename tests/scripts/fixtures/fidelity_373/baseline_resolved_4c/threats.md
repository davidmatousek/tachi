---
schema_version: "1.4"
date: "2026-01-02"
input_format: "mermaid"
classification: "confidential"
run_id: "2026-01-02T00-00-00"
baseline:
  source: "threats.md"
  date: "2026-01-01"
  finding_count: 6
  run_id: "2026-01-01T00-00-00"
coverage_gate:
  status: "pass"
  gaps: []
---

# Threat Model: Synthetic Fixture — 4c Resolved Findings + Bracketed Statuses (F-373 K12, N6)

## 1. System Overview

### Components

| Component | Type | Description |
|-----------|------|-------------|
| API Gateway | Process | Synthetic request ingress service |
| Backend Service | Process | Synthetic business logic service |

---

## 4c. Resolved Findings

| ID | Component | Threat | Last Risk Level | Resolution Reason |
|----|-----------|--------|-----------------|-------------------|
| F-7 | Legacy Service | Synthetic threat no longer applicable | Medium | Component removed from architecture |
| F-8 | Legacy Service | Another synthetic resolved threat | Low | Threat category no longer applicable |
| — | Legacy Service | Placeholder row; must be skipped, not counted | Low | Placeholder |

---

## 7. Recommended Actions

| Finding ID | Status | Category | Pattern | Component | MAESTRO Layer | Threat | Risk Level | Mitigation |
|------------|--------|----------|---------|-----------|---------------|--------|------------|------------|
| F-1 | NEW | Spoofing | — | API Gateway | Unclassified | Synthetic spoofing threat, bare NEW | High | Apply mutual TLS |
| F-2 | [NEW] | Spoofing | — | API Gateway | Unclassified | Synthetic spoofing threat, bracketed NEW | High | Apply mutual TLS |
| F-3 | **[NEW]** | Tampering | — | Backend Service | Unclassified | Synthetic tampering threat, bold-bracketed NEW | Medium | Validate all inputs |
| F-4 | `[NEW]` | Tampering | — | Backend Service | Unclassified | Synthetic tampering threat, code-bracketed NEW | Medium | Validate all inputs |
| F-5 | UPDATED | Information Disclosure | — | API Gateway | Unclassified | Synthetic disclosure threat, context changed | Medium | Mask sensitive fields in logs |
| F-6 | UNCHANGED | Denial of Service | — | Backend Service | Unclassified | Synthetic DoS threat, unchanged since baseline | Low | Apply request throttling |
