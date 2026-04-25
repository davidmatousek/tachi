<!--
F-212 L2 fixture — `absent`
Exercises: zero qualifying Critical/High findings across all layers.
Expected post-F-212 behavior: skip_image=True, callouts=[]; the per-layer
floor-rule invariant test asserts skip-image short-circuit semantics.
Layout: 2 layers (Component A in Untrusted Zone, Component B in Trusted
Zone) with only Medium/Low findings — qualifying_layer_count is 0.
-->
---
schema_version: "1.1"
date: "2026-04-25"
input_format: "mermaid"
classification: "internal"
---

# Threat Model: F-212 Absent Fixture

## 1. System Overview

### Components

| Component | Type | Description |
|-----------|------|-------------|
| Component A | Process | Untrusted ingress process |
| Component B | Process | Trusted backend process |

### Data Flows

| Source | Destination | Data | Protocol |
|--------|-------------|------|----------|
| Component A | Component B | Request | HTTPS |

---

## 2. Trust Boundaries

### Trust Zones

| Zone | Trust Level | Components |
|------|-------------|------------|
| Untrusted Zone | Untrusted | Component A |
| Trusted Zone | Trusted | Component B |

### Boundary Crossings

| Crossing | From Zone | To Zone | Components | Controls |
|----------|-----------|---------|------------|----------|
| Edge to Core | Untrusted Zone | Trusted Zone | Component A, Component B | TLS |

---

## 3. STRIDE Tables

### 3.1 Spoofing (S)

| ID | Component | Threat | Likelihood | Impact | Risk Level | Mitigation |
|----|-----------|--------|------------|--------|------------|------------|
| S-1 | Component A | Cosmetic banner spoofing | LOW | LOW | Low | Style guidance |

---

## 7. Recommended Actions

| Finding ID | Status | Component | Threat | Risk Level | Mitigation |
|------------|--------|-----------|--------|------------|------------|
| S-1 | NEW | Component A | Cosmetic banner spoofing that does not affect user trust | Low | Style guidance |
| I-1 | NEW | Component B | Verbose log line reveals minor diagnostic detail | Medium | Redact diagnostic detail |
