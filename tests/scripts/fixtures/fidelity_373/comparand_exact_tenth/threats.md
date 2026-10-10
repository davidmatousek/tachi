<!--
F-373 L-4 fixture — `comparand_exact_tenth`
Exercises: _funnel_section1_comparand_warnings' "differs by more than 0.1"
tolerance (data-model.md §4.5). Paired with this directory's
compensating-controls.md (1 row, inherent 26.9 / residual 10.0 -> row-derived
V2=26.9, V4=10.0, risk_reduction=62.8%). That fixture's Section 1 prose
states inherent=27.0 (exact 0.1 above the row-derived 26.9 -- must NOT warn)
and residual=10.11 (0.11 above the row-derived 10.0 -- must warn), with
risk_reduction stated to match the derived 62.8% exactly (silent, so the
test isolates to just the two engineered fields).
-->
---
schema_version: "1.1"
date: "2026-04-25"
input_format: "mermaid"
classification: "internal"
---

# Threat Model: F-373 L-4 Comparand-Tolerance Fixture

## 1. System Overview

### Components

| Component | Type | Description |
|-----------|------|-------------|
| API | Process | Public API endpoint |

---

## 3. STRIDE Tables

### 3.1 Spoofing (S)

| ID | Component | Threat | Likelihood | Impact | Risk Level | Mitigation |
|----|-----------|--------|------------|--------|------------|------------|
| W-1 | API | Synthetic threat W-1 | HIGH | HIGH | Critical | Synthetic mitigation |

---

## 7. Recommended Actions

| Finding ID | Status | Component | Threat | Risk Level | Mitigation |
|------------|--------|-----------|--------|------------|------------|
| W-1 | NEW | API | Synthetic threat W-1 | Critical | Synthetic mitigation |
