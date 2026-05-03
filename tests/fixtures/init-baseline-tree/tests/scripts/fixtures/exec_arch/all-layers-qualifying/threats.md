<!--
F-212 L2 fixture — `all-layers-qualifying`
Exercises: 5 qualifying layers, >=1 qualifying finding per layer, total >8.
Stresses the total-cap=8 ceiling alongside the per-layer floor:
qualifying_layer_count=5 (<= 8) so every layer must be represented; total
qualifying findings=11 (> 8) so the cap binds. Expected post-F-212: exactly
8 callouts spread across 5 layers with each represented >=1.
Per-layer ceiling (4) is not stressed here (largest layer has 3 findings).
Layout: 5 zones with mixed trust levels:
  - Layer One (Untrusted): 3 components / 3 findings
  - Layer Two (Untrusted): 2 components / 2 findings
  - Layer Three (Semi-Trusted): 3 components / 3 findings
  - Layer Four (Semi-Trusted): 2 components / 2 findings
  - Layer Five (Trusted): 1 component / 1 finding
Total: 11 components / 11 Critical/High findings.
-->
---
schema_version: "1.1"
date: "2026-04-25"
input_format: "mermaid"
classification: "internal"
---

# Threat Model: F-212 All-Layers-Qualifying Fixture

## 1. System Overview

### Components

| Component | Type | Description |
|-----------|------|-------------|
| Component A | Process | L1 ingress |
| Component B | Process | L1 auth |
| Component C | Process | L1 router |
| Component D | Process | L2 entry |
| Component E | Process | L2 splitter |
| Component F | Process | L3 orchestrator |
| Component G | Process | L3 dispatcher |
| Component H | Process | L3 scheduler |
| Component I | Process | L4 worker |
| Component J | Process | L4 publisher |
| Component K | Data Store | L5 archive |

### Data Flows

| Source | Destination | Data | Protocol |
|--------|-------------|------|----------|
| Component A | Component B | Prompt | HTTPS |
| Component B | Component C | Validated Prompt | HTTPS |
| Component C | Component D | Forwarded Request | HTTPS |
| Component D | Component E | Split Request | HTTPS |
| Component E | Component F | Routed Request | HTTPS |
| Component F | Component G | Dispatched Action | HTTPS |
| Component G | Component H | Scheduled Task | HTTPS |
| Component H | Component I | Worker Job | HTTPS |
| Component I | Component J | Publish Event | HTTPS |
| Component J | Component K | Archive Entry | TCP |

---

## 2. Trust Boundaries

### Trust Zones

| Zone | Trust Level | Components |
|------|-------------|------------|
| Layer One | Untrusted | Component A, Component B, Component C |
| Layer Two | Untrusted | Component D, Component E |
| Layer Three | Semi-Trusted | Component F, Component G, Component H |
| Layer Four | Semi-Trusted | Component I, Component J |
| Layer Five | Trusted | Component K |

### Boundary Crossings

| Crossing | From Zone | To Zone | Components | Controls |
|----------|-----------|---------|------------|----------|
| L1 to L2 | Layer One | Layer Two | Component C, Component D | TLS |
| L2 to L3 | Layer Two | Layer Three | Component E, Component F | mTLS |
| L3 to L4 | Layer Three | Layer Four | Component H, Component I | mTLS |
| L4 to L5 | Layer Four | Layer Five | Component J, Component K | mTLS |

---

## 3. STRIDE Tables

### 3.1 Spoofing (S)

| ID | Component | Threat | Likelihood | Impact | Risk Level | Mitigation |
|----|-----------|--------|------------|--------|------------|------------|
| S-1 | Component A | Spoof of L1 ingress | HIGH | HIGH | Critical | mTLS |
| S-2 | Component B | Spoof of L1 auth | MEDIUM | HIGH | High | mTLS |
| S-3 | Component C | Spoof of L1 router | MEDIUM | HIGH | High | mTLS |
| S-4 | Component D | Spoof of L2 entry | HIGH | HIGH | Critical | mTLS |
| S-5 | Component E | Spoof of L2 splitter | MEDIUM | HIGH | High | mTLS |

### 3.2 Tampering (T)

| ID | Component | Threat | Likelihood | Impact | Risk Level | Mitigation |
|----|-----------|--------|------------|--------|------------|------------|
| T-1 | Component F | Tamper of L3 orchestrator | HIGH | HIGH | Critical | HMAC sign |
| T-2 | Component G | Tamper of L3 dispatcher | MEDIUM | HIGH | High | HMAC sign |
| T-3 | Component H | Tamper of L3 scheduler | MEDIUM | HIGH | High | HMAC sign |
| T-4 | Component I | Tamper of L4 worker | HIGH | HIGH | Critical | HMAC sign |
| T-5 | Component J | Tamper of L4 publisher | MEDIUM | HIGH | High | HMAC sign |

### 3.4 Information Disclosure (I)

| ID | Component | Threat | Likelihood | Impact | Risk Level | Mitigation |
|----|-----------|--------|------------|--------|------------|------------|
| I-1 | Component K | Leak from L5 archive | HIGH | HIGH | Critical | Field-level access controls |

---

## 7. Recommended Actions

| Finding ID | Status | Component | Threat | Risk Level | Mitigation |
|------------|--------|-----------|--------|------------|------------|
| S-1 | NEW | Component A | Attacker spoofs L1 ingress identity | Critical | Enforce mTLS |
| S-2 | NEW | Component B | Attacker spoofs L1 auth identity | High | Enforce mTLS |
| S-3 | NEW | Component C | Attacker spoofs L1 router identity | High | Enforce mTLS |
| S-4 | NEW | Component D | Attacker spoofs L2 entry identity | Critical | Enforce mTLS |
| S-5 | NEW | Component E | Attacker spoofs L2 splitter identity | High | Enforce mTLS |
| T-1 | NEW | Component F | Attacker tampers L3 orchestrator | Critical | Enforce HMAC signing |
| T-2 | NEW | Component G | Attacker tampers L3 dispatcher | High | Enforce HMAC signing |
| T-3 | NEW | Component H | Attacker tampers L3 scheduler | High | Enforce HMAC signing |
| T-4 | NEW | Component I | Attacker tampers L4 worker | Critical | Enforce HMAC signing |
| T-5 | NEW | Component J | Attacker tampers L4 publisher | High | Enforce HMAC signing |
| I-1 | NEW | Component K | Attacker exfiltrates L5 archive | Critical | Field-level access controls |
