---
schema_version: "1.4"
date: "2026-01-02"
input_format: "mermaid"
classification: "confidential"
run_id: "2026-01-02T01-00-00"
baseline:
  source: "threats.md"
  date: "2026-01-01"
  finding_count: 6
  run_id: "2026-01-01T00-00-00"
coverage_gate:
  status: "pass"
  gaps: []
---

# Threat Model: Synthetic Fixture — Legacy 4b Resolved Findings Twin (F-373 K12)

Same resolved-finding counts as `baseline_resolved_4c/threats.md`, under the legacy `## 4b.` heading, to prove the resolved count agrees on both spellings.

## 1. System Overview

### Components

| Component | Type | Description |
|-----------|------|-------------|
| API Gateway | Process | Synthetic request ingress service |
| Backend Service | Process | Synthetic business logic service |

---

## 4b. Resolved Findings

| ID | Component | Threat | Last Risk Level | Resolution Reason |
|----|-----------|--------|-----------------|-------------------|
| F-7 | Legacy Service | Synthetic threat no longer applicable | Medium | Component removed from architecture |
| F-8 | Legacy Service | Another synthetic resolved threat | Low | Threat category no longer applicable |
| — | Legacy Service | Placeholder row; must be skipped, not counted | Low | Placeholder |

---

## 7. Recommended Actions

| Finding ID | Status | Category | Pattern | Component | MAESTRO Layer | Threat | Risk Level | Mitigation |
|------------|--------|----------|---------|-----------|---------------|--------|------------|------------|
| F-1 | NEW | Spoofing | — | API Gateway | Unclassified | Synthetic spoofing threat | High | Apply mutual TLS |
| F-5 | UPDATED | Information Disclosure | — | API Gateway | Unclassified | Synthetic disclosure threat, context changed | Medium | Mask sensitive fields in logs |
| F-6 | UNCHANGED | Denial of Service | — | Backend Service | Unclassified | Synthetic DoS threat, unchanged since baseline | Low | Apply request throttling |
