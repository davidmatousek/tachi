---
schema_version: "1.1"
date: "2026-04-25"
input_format: "mermaid"
classification: "confidential"
---

# Threat Model: Flow Edges Absent Fixture

## 1. System Overview

### Components

| Component | Type | Description |
|-----------|------|-------------|
| Web UI | External Entity | Browser-based UI |
| API Gateway | Process | Public ingress |

## 2. Trust Boundaries

### Trust Zones

| Zone | Trust Level | Components |
|------|-------------|------------|
| Public Zone | Untrusted | Web UI |
| App Zone | Semi-Trusted | API Gateway |

### Boundary Crossings

| Crossing | From Zone | To Zone | Components | Controls |
|----------|-----------|---------|------------|----------|
| Public to App | Public Zone | App Zone | Web UI, API Gateway | TLS |

---

## 3. STRIDE Tables

### 3.1 Spoofing (S)

| ID | Component | Threat | Likelihood | Impact | Risk Level | Mitigation |
|----|-----------|--------|------------|--------|------------|------------|
| S-1 | API Gateway | Attacker forges credentials at the API Gateway entry point, because token binding is absent | HIGH | HIGH | Critical | Bind tokens to client fingerprint and enforce mTLS for upstream calls |
