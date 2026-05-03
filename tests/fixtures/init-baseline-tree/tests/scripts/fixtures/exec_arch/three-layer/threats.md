<!--
F-212 L2 fixture — `three-layer`
Exercises: 3 qualifying layers with 4+3+2 Critical/High findings (9 total).
Expected post-F-212 behavior: 6-8 callouts (Largest Remainder Method against
total-cap 8); every qualifying layer has >=1 callout (per-layer floor) given
qualifying_layer_count=3 <= 8; no layer exceeds 4 (per-layer ceiling).
Pre-F-212 baseline: 3 callouts (one per layer under per-layer-dedup).
This is the primary fixture for the superset-invariant and determinism
tests.
Layout: 3 zones: Edge (Untrusted, 4 components / 4 findings), Core
(Semi-Trusted, 3 components / 3 findings), Data (Trusted, 2 components / 2
findings).
-->
---
schema_version: "1.1"
date: "2026-04-25"
input_format: "mermaid"
classification: "internal"
---

# Threat Model: F-212 Three-Layer Fixture

## 1. System Overview

### Components

| Component | Type | Description |
|-----------|------|-------------|
| Component A | Process | Edge ingress |
| Component B | Process | Edge auth |
| Component C | Process | Edge router |
| Component D | Process | Edge classifier |
| Component E | Process | Core orchestrator |
| Component F | Process | Core dispatcher |
| Component G | Process | Core scheduler |
| Component H | Data Store | Primary database |
| Component I | Data Store | Audit log store |

### Data Flows

| Source | Destination | Data | Protocol |
|--------|-------------|------|----------|
| Component A | Component B | Prompt | HTTPS |
| Component B | Component C | Validated Prompt | HTTPS |
| Component C | Component E | Routed Request | HTTPS |
| Component E | Component F | Dispatched Action | HTTPS |
| Component F | Component G | Scheduled Task | HTTPS |
| Component E | Component H | Persisted State | TCP |
| Component E | Component I | Audit Entry | TCP |

---

## 2. Trust Boundaries

### Trust Zones

| Zone | Trust Level | Components |
|------|-------------|------------|
| Edge Zone | Untrusted | Component A, Component B, Component C, Component D |
| Core Zone | Semi-Trusted | Component E, Component F, Component G |
| Data Zone | Trusted | Component H, Component I |

### Boundary Crossings

| Crossing | From Zone | To Zone | Components | Controls |
|----------|-----------|---------|------------|----------|
| Edge to Core | Edge Zone | Core Zone | Component C, Component E | mTLS |
| Core to Data | Core Zone | Data Zone | Component E, Component H | mTLS |

---

## 3. STRIDE Tables

### 3.1 Spoofing (S)

| ID | Component | Threat | Likelihood | Impact | Risk Level | Mitigation |
|----|-----------|--------|------------|--------|------------|------------|
| S-1 | Component A | Spoof of ingress | HIGH | HIGH | Critical | mTLS |
| S-2 | Component B | Spoof of auth | MEDIUM | HIGH | High | mTLS |
| S-3 | Component C | Spoof of router | MEDIUM | HIGH | High | mTLS |
| S-4 | Component D | Spoof of classifier | MEDIUM | HIGH | High | mTLS |

### 3.2 Tampering (T)

| ID | Component | Threat | Likelihood | Impact | Risk Level | Mitigation |
|----|-----------|--------|------------|--------|------------|------------|
| T-1 | Component E | Tamper of orchestrator | HIGH | HIGH | Critical | HMAC sign |
| T-2 | Component F | Tamper of dispatcher | MEDIUM | HIGH | High | HMAC sign |
| T-3 | Component G | Tamper of scheduler | MEDIUM | HIGH | High | HMAC sign |

### 3.4 Information Disclosure (I)

| ID | Component | Threat | Likelihood | Impact | Risk Level | Mitigation |
|----|-----------|--------|------------|--------|------------|------------|
| I-1 | Component H | Leak from primary database | HIGH | HIGH | Critical | Field-level access controls |
| I-2 | Component I | Leak from audit log store | MEDIUM | HIGH | High | Log access tier restrictions |

---

## 7. Recommended Actions

| Finding ID | Status | Component | Threat | Risk Level | Mitigation |
|------------|--------|-----------|--------|------------|------------|
| S-1 | NEW | Component A | Attacker spoofs ingress identity | Critical | Enforce mTLS |
| S-2 | NEW | Component B | Attacker spoofs auth identity | High | Enforce mTLS |
| S-3 | NEW | Component C | Attacker spoofs router identity | High | Enforce mTLS |
| S-4 | NEW | Component D | Attacker spoofs classifier identity | High | Enforce mTLS |
| T-1 | NEW | Component E | Attacker tampers orchestrator inputs | Critical | Enforce HMAC signing |
| T-2 | NEW | Component F | Attacker tampers dispatcher inputs | High | Enforce HMAC signing |
| T-3 | NEW | Component G | Attacker tampers scheduler inputs | High | Enforce HMAC signing |
| I-1 | NEW | Component H | Attacker exfiltrates primary database | Critical | Field-level access controls |
| I-2 | NEW | Component I | Attacker exfiltrates audit log store | High | Log access tier restrictions |
