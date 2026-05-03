---
schema_version: "1.1"
date: "2026-04-25"
input_format: "mermaid"
classification: "confidential"
---

# Threat Model: Clusters Multi Trust Levels Fixture

## 1. System Overview

### Components

| Component | Type | Description |
|-----------|------|-------------|
| Web UI | External Entity | Browser-based UI |
| API Gateway | Process | Public ingress |
| Backend | Process | Internal service |
| Database | Data Store | Primary store |

### Data Flows

| Source | Destination | Data | Protocol |
|--------|-------------|------|----------|
| Web UI | API Gateway | Login Request | HTTPS |

## 2. Trust Boundaries

### Trust Zones

| Zone | Trust Level | Components |
|------|-------------|------------|
| Untrusted Edge | Untrusted | Web UI, External Probe, alpha-probe |
| Trusted Core | Trusted | Database, Backend |
| Semi-Internal | Semi-Trusted | API Gateway |

### Boundary Crossings

| Crossing | From Zone | To Zone | Components | Controls |
|----------|-----------|---------|------------|----------|
| Public to App | Untrusted Edge | Semi-Internal | Web UI, API Gateway | TLS |

---

## 3. STRIDE Tables

### 3.1 Spoofing (S)

| ID | Component | Threat | Likelihood | Impact | Risk Level | Mitigation |
|----|-----------|--------|------------|--------|------------|------------|
| S-1 | API Gateway | Attacker forges credentials at the API Gateway entry point, because token binding is absent | HIGH | HIGH | Critical | Bind tokens to client fingerprint and enforce mTLS for upstream calls |
