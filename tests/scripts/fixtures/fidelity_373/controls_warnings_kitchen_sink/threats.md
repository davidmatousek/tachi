---
schema_version: "1.4"
date: "2026-01-13"
input_format: "mermaid"
classification: "confidential"
run_id: "2026-01-13T00-00-00"
baseline:
  source: null
  date: null
  finding_count: null
  run_id: null
coverage_gate:
  status: "pass"
  gaps: []
---

# Threat Model: Synthetic Fixture — Controls Warnings Kitchen Sink (F-373)

Ten synthetic findings (W-1..W-10) covering: control-status variants
(`Missing`, empty, unrecognized, `Partially Found`, `None found`),
unparseable scores (`—`, `8.5 (High)`, `NaN`), a residual-above-inherent
clamp, a Section 1 comparand mismatch, and (via the sibling `risk-scores.md`)
a controls/risk-scores row-count mismatch. See the fixtures README for the
full hand-computed expected values.

## 1. System Overview

### Components

| Component | Type | Description |
|-----------|------|-------------|
| Audit Service | Process | Synthetic service under review across all ten findings |

---

## 7. Recommended Actions

| Finding ID | Status | Category | Pattern | Component | MAESTRO Layer | Threat | Risk Level | Mitigation |
|------------|--------|----------|---------|-----------|---------------|--------|------------|------------|
| W-1 | NEW | Denial of Service | — | Audit Service | Unclassified | Synthetic threat W-1, status "Missing" | Medium | Apply request throttling |
| W-2 | NEW | Denial of Service | — | Audit Service | Unclassified | Synthetic threat W-2, empty status | Medium | Apply request throttling |
| W-3 | NEW | Denial of Service | — | Audit Service | Unclassified | Synthetic threat W-3, unrecognized status | Medium | Apply request throttling |
| W-4 | NEW | Denial of Service | — | Audit Service | Unclassified | Synthetic threat W-4, status "Partially Found" | Medium | Apply request throttling |
| W-5 | NEW | Denial of Service | — | Audit Service | Unclassified | Synthetic threat W-5, status "None found" | Medium | Apply request throttling |
| W-6 | NEW | Denial of Service | — | Audit Service | Unclassified | Synthetic threat W-6, unparseable residual (em dash) | High | Apply request throttling |
| W-7 | NEW | Denial of Service | — | Audit Service | Unclassified | Synthetic threat W-7, unparseable residual (trailing text) | High | Apply request throttling |
| W-8 | NEW | Denial of Service | — | Audit Service | Unclassified | Synthetic threat W-8, unparseable inherent (NaN) | Medium | Apply request throttling |
| W-9 | NEW | Denial of Service | — | Audit Service | Unclassified | Synthetic threat W-9, residual exceeds inherent | High | Apply request throttling |
| W-10 | NEW | Denial of Service | — | Audit Service | Unclassified | Synthetic threat W-10, clean control (anchor row) | Low | Apply request throttling |
