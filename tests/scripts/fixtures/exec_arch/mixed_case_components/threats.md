---
schema_version: "1.1"
date: "2026-04-09"
input_format: "mermaid"
classification: "internal"
---

# Threat Model: Synthetic Mixed Case Components

## 1. System Overview

### Components

| Component | Type | Description |
|-----------|------|-------------|
| API Gateway | api | Public API gateway service |
| Auth Service | service | Authentication microservice |
| Database | datastore | Primary datastore |

### Data Flows

| Source | Destination | Data | Protocol |
|--------|-------------|------|----------|
| API Gateway | Auth Service | Auth Request | HTTP |
| Auth Service | Database | User Lookup | TCP |

---

## 2. Trust Boundaries

### Trust Zones

| Zone | Trust Level | Components |
|------|-------------|------------|
| Edge | Untrusted | API Gateway |
| Application Zone | Semi-Trusted | Auth Service |
| Data Zone | Trusted | Database |

### Boundary Crossings

| Crossing | From Zone | To Zone | Components | Controls |
|----------|-----------|---------|------------|----------|
| Edge to App | Edge | Application Zone | API Gateway, Auth Service | TLS |

---

## 3. STRIDE Tables

### 3.1 Spoofing (S)

| ID | Component | Threat | Likelihood | Impact | Risk Level | Mitigation |
|----|-----------|--------|------------|--------|------------|------------|
| S-1 | api-gateway | Spoofing attack on the gateway | HIGH | HIGH | Critical | Enforce mTLS |

---

## 7. Recommended Actions

| Finding ID | Status | Component | Threat | Risk Level | Mitigation |
|------------|--------|-----------|--------|------------|------------|
| S-1 | NEW | api-gateway | Attacker spoofs the public gateway endpoint using kebab-case casing for the component name | Critical | Enforce mTLS and certificate pinning at the edge |
| T-1 | NEW | auth_service | Attacker tampers with auth service with underscore-cased component name | Critical | Sign all auth tokens with HMAC |
| I-1 | NEW | database | Attacker exfiltrates sensitive user data from the lowercase-named database | High | Encrypt data at rest and enforce row-level security |
