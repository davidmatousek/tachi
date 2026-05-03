---
schema_version: "1.1"
date: "2026-04-25"
input_format: "mermaid"
classification: "confidential"
---

# Threat Model: Flow Edges Overflow Fixture (55 entries)

## 1. System Overview

### Components

| Component | Type | Description |
|-----------|------|-------------|
| svc-001 | Process | Synthetic source component |
| dest-001 | Process | Synthetic destination component |

### Data Flows

| Source | Destination | Data | Protocol |
|--------|-------------|------|----------|
| svc-001 | dest-001 | payload-001 | HTTPS |
| svc-002 | dest-002 | payload-002 | HTTPS |
| svc-003 | dest-003 | payload-003 | HTTPS |
| svc-004 | dest-004 | payload-004 | HTTPS |
| svc-005 | dest-005 | payload-005 | HTTPS |
| svc-006 | dest-006 | payload-006 | HTTPS |
| svc-007 | dest-007 | payload-007 | HTTPS |
| svc-008 | dest-008 | payload-008 | HTTPS |
| svc-009 | dest-009 | payload-009 | HTTPS |
| svc-010 | dest-010 | payload-010 | HTTPS |
| svc-011 | dest-011 | payload-011 | HTTPS |
| svc-012 | dest-012 | payload-012 | HTTPS |
| svc-013 | dest-013 | payload-013 | HTTPS |
| svc-014 | dest-014 | payload-014 | HTTPS |
| svc-015 | dest-015 | payload-015 | HTTPS |
| svc-016 | dest-016 | payload-016 | HTTPS |
| svc-017 | dest-017 | payload-017 | HTTPS |
| svc-018 | dest-018 | payload-018 | HTTPS |
| svc-019 | dest-019 | payload-019 | HTTPS |
| svc-020 | dest-020 | payload-020 | HTTPS |
| svc-021 | dest-021 | payload-021 | HTTPS |
| svc-022 | dest-022 | payload-022 | HTTPS |
| svc-023 | dest-023 | payload-023 | HTTPS |
| svc-024 | dest-024 | payload-024 | HTTPS |
| svc-025 | dest-025 | payload-025 | HTTPS |
| svc-026 | dest-026 | payload-026 | HTTPS |
| svc-027 | dest-027 | payload-027 | HTTPS |
| svc-028 | dest-028 | payload-028 | HTTPS |
| svc-029 | dest-029 | payload-029 | HTTPS |
| svc-030 | dest-030 | payload-030 | HTTPS |
| svc-031 | dest-031 | payload-031 | HTTPS |
| svc-032 | dest-032 | payload-032 | HTTPS |
| svc-033 | dest-033 | payload-033 | HTTPS |
| svc-034 | dest-034 | payload-034 | HTTPS |
| svc-035 | dest-035 | payload-035 | HTTPS |
| svc-036 | dest-036 | payload-036 | HTTPS |
| svc-037 | dest-037 | payload-037 | HTTPS |
| svc-038 | dest-038 | payload-038 | HTTPS |
| svc-039 | dest-039 | payload-039 | HTTPS |
| svc-040 | dest-040 | payload-040 | HTTPS |
| svc-041 | dest-041 | payload-041 | HTTPS |
| svc-042 | dest-042 | payload-042 | HTTPS |
| svc-043 | dest-043 | payload-043 | HTTPS |
| svc-044 | dest-044 | payload-044 | HTTPS |
| svc-045 | dest-045 | payload-045 | HTTPS |
| svc-046 | dest-046 | payload-046 | HTTPS |
| svc-047 | dest-047 | payload-047 | HTTPS |
| svc-048 | dest-048 | payload-048 | HTTPS |
| svc-049 | dest-049 | payload-049 | HTTPS |
| svc-050 | dest-050 | payload-050 | HTTPS |
| svc-051 | dest-051 | payload-051 | HTTPS |
| svc-052 | dest-052 | payload-052 | HTTPS |
| svc-053 | dest-053 | payload-053 | HTTPS |
| svc-054 | dest-054 | payload-054 | HTTPS |
| svc-055 | dest-055 | payload-055 | HTTPS |

## 2. Trust Boundaries

### Trust Zones

| Zone | Trust Level | Components |
|------|-------------|------------|
| Synthetic Zone | Untrusted | svc-001, dest-001 |

### Boundary Crossings

| Crossing | From Zone | To Zone | Components | Controls |
|----------|-----------|---------|------------|----------|
| Synthetic | Synthetic Zone | Synthetic Zone | svc-001, dest-001 | TLS |

---

## 3. STRIDE Tables

### 3.1 Spoofing (S)

| ID | Component | Threat | Likelihood | Impact | Risk Level | Mitigation |
|----|-----------|--------|------------|--------|------------|------------|
| S-1 | svc-001 | Attacker forges credentials at the svc-001 entry point, because token binding is absent | HIGH | HIGH | Critical | Bind tokens to client fingerprint |
