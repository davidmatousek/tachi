<!--
F-212 L2 fixture — `single-layer`
Exercises: 1 qualifying layer with 2 Critical/High findings.
Expected post-F-212 behavior: 2 callouts emitted (no synthetic inflation).
Per-layer floor: the single qualifying layer (Edge Zone) has >=1 callout.
Per-layer ceiling (4) not exercised here.
Layout: 1 trust zone (Edge Zone) with 2 components (Component A, Component B);
1 trusted zone (Core Zone) with no qualifying findings.
-->
---
schema_version: "1.1"
date: "2026-04-25"
input_format: "mermaid"
classification: "internal"
---

# Threat Model: F-212 Single-Layer Fixture

## 1. System Overview

### Components

| Component | Type | Description |
|-----------|------|-------------|
| Component A | Process | Edge ingress process |
| Component B | Process | Edge auth process |
| Component C | Process | Core backend process |

### Data Flows

| Source | Destination | Data | Protocol |
|--------|-------------|------|----------|
| Component A | Component B | Request | HTTPS |
| Component B | Component C | Validated Request | HTTPS |

---

## 2. Trust Boundaries

### Trust Zones

| Zone | Trust Level | Components |
|------|-------------|------------|
| Edge Zone | Untrusted | Component A, Component B |
| Core Zone | Trusted | Component C |

### Boundary Crossings

| Crossing | From Zone | To Zone | Components | Controls |
|----------|-----------|---------|------------|----------|
| Edge to Core | Edge Zone | Core Zone | Component B, Component C | mTLS |

---

## 3. STRIDE Tables

### 3.1 Spoofing (S)

| ID | Component | Threat | Likelihood | Impact | Risk Level | Mitigation |
|----|-----------|--------|------------|--------|------------|------------|
| S-1 | Component A | Spoof of edge identity | HIGH | HIGH | Critical | mTLS |
| S-2 | Component B | Spoof of auth identity | MEDIUM | HIGH | High | mTLS |

---

## 7. Recommended Actions

| Finding ID | Status | Component | Threat | Risk Level | Mitigation |
|------------|--------|-----------|--------|------------|------------|
| S-1 | NEW | Component A | Attacker spoofs edge identity by replaying credentials | Critical | Enforce mTLS and certificate pinning |
| S-2 | NEW | Component B | Attacker spoofs auth identity by forging tokens | High | Enforce mTLS and signed JWTs |
