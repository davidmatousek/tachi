---
schema_version: "1.1"
date: "2026-04-25"
input_format: "mermaid"
classification: "confidential"
---

# Threat Model: Flow Edges Multi (Mixed Case) Fixture

## 1. System Overview

### Components

| Component | Type | Description |
|-----------|------|-------------|
| Web UI | External Entity | Browser-based UI |
| api-gateway | Process | Public ingress (kebab-case) |
| WEB_UI | External Entity | Alt-cased duplicate (sort fixture) |
| Backend | Process | Internal service |
| Database | Data Store | Primary store |

### Data Flows

| Source | Destination | Data | Protocol |
|--------|-------------|------|----------|
| zeta | alpha | Metrics | gRPC |
| Backend | Database | Persisted Records | TLS |
| api-gateway | Backend | Validated Request | HTTPS |
| WEB_UI | api-gateway | Login Request | HTTPS |
| Web UI | api-gateway | Login Request | HTTPS |

## 2. Trust Boundaries

### Trust Zones

| Zone | Trust Level | Components |
|------|-------------|------------|
| Public Zone | Untrusted | Web UI, WEB_UI |
| App Zone | Semi-Trusted | api-gateway, Backend |
| Data Zone | Trusted | Database |

### Boundary Crossings

| Crossing | From Zone | To Zone | Components | Controls |
|----------|-----------|---------|------------|----------|
| Public to App | Public Zone | App Zone | Web UI, api-gateway | TLS |
| App to Data | App Zone | Data Zone | Backend, Database | mTLS |

---

## 3. STRIDE Tables

### 3.1 Spoofing (S)

| ID | Component | Threat | Likelihood | Impact | Risk Level | Mitigation |
|----|-----------|--------|------------|--------|------------|------------|
| S-1 | api-gateway | Attacker forges credentials at the api-gateway entry point, because token binding is absent | HIGH | HIGH | Critical | Bind tokens to client fingerprint and enforce mTLS for upstream calls |
