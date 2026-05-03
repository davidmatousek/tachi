---
schema_version: "1.1"
date: "2026-04-09"
input_format: "mermaid"
classification: "internal"
---

# Threat Model: Synthetic Orphaned Finding

## 1. System Overview

### Components

| Component | Type | Description |
|-----------|------|-------------|
| Component A | api | API service A |
| Component B | service | Backend service B |
| Component C | datastore | Data store C |

### Data Flows

| Source | Destination | Data | Protocol |
|--------|-------------|------|----------|
| Component A | Component B | Request | HTTP |
| Component B | Component C | Query | TCP |

---

## 2. Trust Boundaries

### Trust Zones

| Zone | Trust Level | Components |
|------|-------------|------------|
| Edge Zone | Untrusted | Component A |
| Application Zone | Semi-Trusted | Component B |
| Data Zone | Trusted | Component C |

### Boundary Crossings

| Crossing | From Zone | To Zone | Components | Controls |
|----------|-----------|---------|------------|----------|
| Edge to App | Edge Zone | Application Zone | Component A, Component B | TLS |

---

## 3. STRIDE Tables

### 3.1 Spoofing (S)

| ID | Component | Threat | Likelihood | Impact | Risk Level | Mitigation |
|----|-----------|--------|------------|--------|------------|------------|
| S-1 | Component A | Spoofing attack on Component A | HIGH | HIGH | Critical | Enforce mTLS |

---

## 7. Recommended Actions

| Finding ID | Status | Component | Threat | Risk Level | Mitigation |
|------------|--------|-----------|--------|------------|------------|
| S-1 | NEW | Component A | Spoofing attack on the edge Component A endpoint | Critical | Enforce mTLS and certificate pinning |
| S-2 | NEW | Component D | Attacker targets orphaned Component D which is not in any trust zone | Critical | Document Component D in the trust boundary table before mitigation |
