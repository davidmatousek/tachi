---
schema_version: "1.0"
source_file: "baseline/threats.md"
classification: "confidential"
scoring_weights:
  cvss_base: 0.35
  exploitability: 0.30
  scalability: 0.15
  reachability: 0.20
---

# Risk Scores Report

## 1. Executive Summary

**4** threats scored | **0** Critical | **0** High | **3** Medium | **1** Low

## 2. Scored Threat Table

| ID | Component | Threat | CVSS | Exploit | Scale | Reach | Composite | Severity | SLA | Disposition |
|----|-----------|--------|------|---------|-------|-------|-----------|----------|-----|-------------|
| S-1 | edge-gateway | A shared or long-lived bearer token on edge-gateway lets... | 7.1 | 7.5 | 8.5 | 6.5 | 7.3 | Medium | — | Review |
| R-1 | edge-gateway | Log entries from edge-gateway can be edited or deleted by... | 7.2 | 6.5 | 6.5 | 6.0 | 6.2 | Medium | 30d | Review |
| T-1 | intake-agent | Replay of an earlier valid update to free-text shipment... | 7.1 | 6.5 | 4.0 | 2.0 | 5.4 | Low | — | Review |
| I-1 | vector-store-a | embedded documents and metadata held by vector-store-a are... | 6.5 | 6.0 | 5.0 | 2.0 | 5.2 | Medium | 30d | Review |

## 3. Dimensional Breakdown

### S-1: edge-gateway

**Threat**: A shared or long-lived bearer token on edge-gateway lets anyone who obtains one copy authenticate as every tenant that uses the same deployment profile.

**Score**: 7.1 | **Vector**: `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:L/A:N`

### R-1: edge-gateway

**Threat**: Log entries from edge-gateway can be edited or deleted by the same operators who administer it, so evidence of misuse can be removed after the fact.

**Score**: 7.2 | **Vector**: `CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:L/I:L/A:N`

### T-1: intake-agent

**Threat**: Replay of an earlier valid update to free-text shipment requests reaches intake-agent because updates carry no nonce or expiry, restoring a state the owner already corrected.

**CVSS Vector**: `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:L`

### I-1: vector-store-a

**Threat**: embedded documents and metadata held by vector-store-a are readable by any service in the Data Zone that shares the same network role, because access is granted by network position.

**Score**: 6.5 | **Vector**: `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N`

## 4. Governance Fields

| ID | Severity | Owner | SLA | Disp | Review Date |
|----|----------|-------|-----|------|-------------|
| S-1 | Medium | Unassigned | — | Review | 2026-12-09 |
| R-1 | Medium | Unassigned | 30d | Review | 2026-12-09 |
| T-1 | Low | Unassigned | — | Review | — |
| I-1 | Medium | Unassigned | 30d | Review | 2026-12-09 |
