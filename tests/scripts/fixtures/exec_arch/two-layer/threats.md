<!--
F-212 L2 fixture — `two-layer`
Exercises: 2 qualifying layers with 3+2 Critical/High findings (5 total).
Expected post-F-212 behavior: 5 callouts (under total-cap of 8); both
qualifying layers have >=1 callout (per-layer floor); no layer exceeds 4.
Layout: 2 trust zones (Edge Zone with 3 components / 3 findings, Core Zone
with 2 components / 2 findings); plus 1 trusted zone with no findings.
-->
---
schema_version: "1.1"
date: "2026-04-25"
input_format: "mermaid"
classification: "internal"
---

# Threat Model: F-212 Two-Layer Fixture

## 1. System Overview

### Components

| Component | Type | Description |
|-----------|------|-------------|
| Component A | Process | Edge ingress |
| Component B | Process | Edge auth |
| Component C | Process | Edge router |
| Component D | Process | Core orchestrator |
| Component E | Process | Core dispatcher |
| Component F | Data Store | Audit data store |

### Data Flows

| Source | Destination | Data | Protocol |
|--------|-------------|------|----------|
| Component A | Component B | Prompt | HTTPS |
| Component B | Component C | Validated Prompt | HTTPS |
| Component C | Component D | Routed Request | HTTPS |
| Component D | Component E | Dispatched Action | HTTPS |
| Component D | Component F | Audit Entry | TCP |

---

## 2. Trust Boundaries

### Trust Zones

| Zone | Trust Level | Components |
|------|-------------|------------|
| Edge Zone | Untrusted | Component A, Component B, Component C |
| Core Zone | Semi-Trusted | Component D, Component E |
| Audit Zone | Trusted | Component F |

### Boundary Crossings

| Crossing | From Zone | To Zone | Components | Controls |
|----------|-----------|---------|------------|----------|
| Edge to Core | Edge Zone | Core Zone | Component C, Component D | mTLS |
| Core to Audit | Core Zone | Audit Zone | Component D, Component F | mTLS |

---

## 3. STRIDE Tables

### 3.1 Spoofing (S)

| ID | Component | Threat | Likelihood | Impact | Risk Level | Mitigation |
|----|-----------|--------|------------|--------|------------|------------|
| S-1 | Component A | Spoof of edge ingress | HIGH | HIGH | Critical | mTLS |
| S-2 | Component B | Spoof of edge auth | MEDIUM | HIGH | High | mTLS |
| S-3 | Component C | Spoof of edge router | MEDIUM | HIGH | High | mTLS |

### 3.2 Tampering (T)

| ID | Component | Threat | Likelihood | Impact | Risk Level | Mitigation |
|----|-----------|--------|------------|--------|------------|------------|
| T-1 | Component D | Tamper of orchestrator | HIGH | HIGH | Critical | HMAC sign |
| T-2 | Component E | Tamper of dispatcher | MEDIUM | HIGH | High | HMAC sign |

---

## 7. Recommended Actions

| Finding ID | Status | Component | Threat | Risk Level | Mitigation |
|------------|--------|-----------|--------|------------|------------|
| S-1 | NEW | Component A | Attacker spoofs edge ingress identity | Critical | Enforce mTLS and certificate pinning |
| S-2 | NEW | Component B | Attacker spoofs edge auth identity | High | Enforce mTLS and signed JWTs |
| S-3 | NEW | Component C | Attacker spoofs edge router identity | High | Enforce mTLS |
| T-1 | NEW | Component D | Attacker tampers with orchestrator inputs | Critical | Enforce HMAC signing |
| T-2 | NEW | Component E | Attacker tampers with dispatcher inputs | High | Enforce HMAC signing |
