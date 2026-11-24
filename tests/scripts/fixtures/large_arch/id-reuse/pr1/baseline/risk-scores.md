---
schema_version: "1.0"
date: "2026-11-09"
source_file: "baseline/threats.md"
classification: "confidential"
scoring_weights:
  cvss_base: 0.35
  exploitability: 0.30
  scalability: 0.15
  reachability: 0.20
baseline:
  source: null
  inherited_count: null
  fresh_count: null
---

# Risk Scores Report

## 1. Executive Summary

**7** threats scored | **0** Critical | **4** High | **3** Medium | **0** Low

**Highest-Risk Component**: auth-broker — 2 finding(s), max composite 7.7

| Metric | Value |
|--------|-------|
| Scoring date | 2026-11-09 |
| Source file | `baseline/threats.md` |
| Schema version | 1.0 |

**Severity Distribution:**

| Severity | Count | Percentage |
|----------|-------|------------|
| Critical | 0 | 0.0% |
| High | 4 | 57.1% |
| Medium | 3 | 42.9% |
| Low | 0 | 0.0% |
| **Total** | **7** | **100%** |

> Trust zone data was available for every component, so no reachability value was defaulted.

---

## 2. Scored Threat Table

Findings sorted by Composite score descending (highest risk first). Boundary values map to the higher severity band.

| ID | Source | Component | Threat | CVSS | Exploit. | Scale. | Reach. | Composite | Severity | SLA | Disposition |
|----|--------|-----------|--------|------|----------|--------|--------|-----------|----------|-----|-------------|
| S-2 | fresh | auth-broker | A shared or long-lived refresh token on auth-broker lets... | 6.5 | 9.0 | 9.0 | 7.0 | 7.7 | High | 7d | Mitigate |
| S-1 | fresh | edge-gateway | A shared or long-lived bearer token on edge-gateway lets... | 8.1 | 7.5 | 8.5 | 5.5 | 7.5 | High | 7d | Mitigate |
| T-2 | fresh | auth-broker | Backups and exports of credential assertions and session... | 8.2 | 7.0 | 7.0 | 6.5 | 7.3 | High | 7d | Mitigate |
| T-4 | fresh | vector-store-a | Serialised objects arriving from worker-2 are deserialised... | 8.8 | 8.0 | 8.0 | 2.5 | 7.2 | High | 7d | Accept |
| T-1 | fresh | edge-gateway | An attacker who can write to the channel between auth-broker... | 7.6 | 6.5 | 6.5 | 5.5 | 6.7 | Medium | 30d | Review |
| T-3 | fresh | intake-agent | Replay of an earlier valid update to free-text shipment... | 8.2 | 5.5 | 4.5 | 1.5 | 5.5 | Medium | 30d | Review |
| I-1 | fresh | audit-ledger | approval and tool call records held by audit-ledger are... | 5.7 | 5.0 | 5.5 | 2.0 | 4.7 | Medium | 30d | Review |

> **Correlated findings**: for correlation groups (Section 4a of the source threat model), the primary finding is scored independently. Correlated peer findings inherit the primary's scores to keep the group consistent.

---

## 3. Dimensional Breakdown

Per-finding detail showing the scoring rationale for each dimension, in the order of Section 2.

### S-2 — auth-broker

**Threat**: A shared or long-lived refresh token on auth-broker lets anyone who obtains one copy authenticate as every tenant that uses the same deployment profile.

**Category**: spoofing | **Original Risk Level**: Medium | **Composite**: 7.7 (High)

#### CVSS 3.1 Base

**Score**: 6.5 | **Vector**: `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Network | Reachable over the network |
| Attack Complexity (AC) | Low | No special conditions |
| Privileges Required (PR) | Low | A basic account is needed |
| User Interaction (UI) | None | No user action needed |
| Scope (S) | Unchanged | Impact stays in the component |
| Confidentiality (C) | High | Broad disclosure |
| Integrity (I) | None | No modification |
| Availability (A) | None | No loss of service |

#### Exploitability

**Score**: 9.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 10 | Documented and widely used |
| Attack Complexity | 8 | A single step suffices |
| Tooling Availability | 9 | Common tools apply |
| Skill Level | 9 | Little skill needed |

#### Scalability

**Score**: 9.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 10 | Fully automatable |
| Target Scope | 9 | Every instance |
| Resource Requirements | 8 | Minimal resources |
| Detection Difficulty | 9 | Blends with normal use |

#### Reachability

**Score**: 7.0 | **Trust Zone**: Edge DMZ (Semi-trusted)

auth-broker sits in the Edge DMZ. The zone baseline is 6.5 and the refinement for this finding gives 7.0.

---

### S-1 — edge-gateway

**Threat**: A shared or long-lived bearer token on edge-gateway lets anyone who obtains one copy authenticate as every tenant that uses the same deployment profile.

**Category**: spoofing | **Original Risk Level**: High | **Composite**: 7.5 (High)

#### CVSS 3.1 Base

**Score**: 8.1 | **Vector**: `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Network | Reachable over the network |
| Attack Complexity (AC) | Low | No special conditions |
| Privileges Required (PR) | Low | A basic account is needed |
| User Interaction (UI) | None | No user action needed |
| Scope (S) | Unchanged | Impact stays in the component |
| Confidentiality (C) | High | Broad disclosure |
| Integrity (I) | High | Broad modification |
| Availability (A) | None | No loss of service |

#### Exploitability

**Score**: 7.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 8 | Documented and widely used |
| Attack Complexity | 8 | A single step suffices |
| Tooling Availability | 7 | Common tools apply |
| Skill Level | 7 | Little skill needed |

#### Scalability

**Score**: 8.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 8 | Fully automatable |
| Target Scope | 9 | Every instance |
| Resource Requirements | 9 | Minimal resources |
| Detection Difficulty | 8 | Blends with normal use |

#### Reachability

**Score**: 5.5 | **Trust Zone**: Edge DMZ (Semi-trusted)

edge-gateway sits in the Edge DMZ. The zone baseline is 6.5 and the refinement for this finding gives 5.5.

---

### T-2 — auth-broker

**Threat**: Backups and exports of credential assertions and session grants on auth-broker are writable by operators without a second approver, so a malicious change survives restores.

**Category**: tampering | **Original Risk Level**: High | **Composite**: 7.3 (High)

#### CVSS 3.1 Base

**Score**: 8.2 | **Vector**: `CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:L`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Network | Reachable over the network |
| Attack Complexity (AC) | Low | No special conditions |
| Privileges Required (PR) | None | No privileges needed |
| User Interaction (UI) | None | No user action needed |
| Scope (S) | Unchanged | Impact stays in the component |
| Confidentiality (C) | None | No disclosure |
| Integrity (I) | High | Broad modification |
| Availability (A) | Low | Degraded service |

#### Exploitability

**Score**: 7.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 8 | Documented and widely used |
| Attack Complexity | 8 | A single step suffices |
| Tooling Availability | 6 | Tools need adaptation |
| Skill Level | 6 | Intermediate skill |

#### Scalability

**Score**: 7.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 8 | Fully automatable |
| Target Scope | 6 | A class of targets |
| Resource Requirements | 10 | Minimal resources |
| Detection Difficulty | 4 | Detectable with monitoring |

#### Reachability

**Score**: 6.5 | **Trust Zone**: Edge DMZ (Semi-trusted)

auth-broker sits in the Edge DMZ. The zone baseline is 6.5 and the refinement for this finding gives 6.5.

---

### T-4 — vector-store-a

**Threat**: Serialised objects arriving from worker-2 are deserialised by vector-store-a with permissive type handling, allowing crafted payloads to instantiate unintended behaviour.

**Category**: tampering | **Original Risk Level**: Medium | **Composite**: 7.2 (High)

#### CVSS 3.1 Base

**Score**: 8.8 | **Vector**: `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Network | Reachable over the network |
| Attack Complexity (AC) | Low | No special conditions |
| Privileges Required (PR) | Low | A basic account is needed |
| User Interaction (UI) | None | No user action needed |
| Scope (S) | Unchanged | Impact stays in the component |
| Confidentiality (C) | High | Broad disclosure |
| Integrity (I) | High | Broad modification |
| Availability (A) | High | Loss of service |

#### Exploitability

**Score**: 8.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 8 | Documented and widely used |
| Attack Complexity | 8 | A single step suffices |
| Tooling Availability | 8 | Common tools apply |
| Skill Level | 8 | Little skill needed |

#### Scalability

**Score**: 8.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 8 | Fully automatable |
| Target Scope | 8 | Every instance |
| Resource Requirements | 8 | Minimal resources |
| Detection Difficulty | 8 | Blends with normal use |

#### Reachability

**Score**: 2.5 | **Trust Zone**: Data Zone (Trusted)

vector-store-a sits in the Data Zone. The zone baseline is 2.5 and the refinement for this finding gives 2.5.

---

### T-1 — edge-gateway

**Threat**: An attacker who can write to the channel between auth-broker and edge-gateway modifies inbound API requests in transit because messages carry no integrity protection of their own.

**Category**: tampering | **Original Risk Level**: Critical | **Composite**: 6.7 (Medium)

#### CVSS 3.1 Base

**Score**: 7.6 | **Vector**: `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:H/A:L`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Network | Reachable over the network |
| Attack Complexity (AC) | Low | No special conditions |
| Privileges Required (PR) | Low | A basic account is needed |
| User Interaction (UI) | None | No user action needed |
| Scope (S) | Unchanged | Impact stays in the component |
| Confidentiality (C) | Low | Limited disclosure |
| Integrity (I) | High | Broad modification |
| Availability (A) | Low | Degraded service |

#### Exploitability

**Score**: 6.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 6 | Described in research |
| Attack Complexity | 6 | Needs some preparation |
| Tooling Availability | 7 | Common tools apply |
| Skill Level | 7 | Little skill needed |

#### Scalability

**Score**: 6.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 8 | Fully automatable |
| Target Scope | 6 | A class of targets |
| Resource Requirements | 7 | Minimal resources |
| Detection Difficulty | 5 | Detectable with monitoring |

#### Reachability

**Score**: 5.5 | **Trust Zone**: Edge DMZ (Semi-trusted)

edge-gateway sits in the Edge DMZ. The zone baseline is 6.5 and the refinement for this finding gives 5.5.

---

### T-3 — intake-agent

**Threat**: Replay of an earlier valid update to free-text shipment requests reaches intake-agent because updates carry no nonce or expiry, restoring a state the owner already corrected.

**Category**: tampering | **Original Risk Level**: Medium | **Composite**: 5.5 (Medium)

#### CVSS 3.1 Base

**Score**: 8.2 | **Vector**: `CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:L`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Network | Reachable over the network |
| Attack Complexity (AC) | Low | No special conditions |
| Privileges Required (PR) | None | No privileges needed |
| User Interaction (UI) | None | No user action needed |
| Scope (S) | Unchanged | Impact stays in the component |
| Confidentiality (C) | None | No disclosure |
| Integrity (I) | High | Broad modification |
| Availability (A) | Low | Degraded service |

#### Exploitability

**Score**: 5.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 6 | Described in research |
| Attack Complexity | 6 | Needs some preparation |
| Tooling Availability | 4 | Tools need adaptation |
| Skill Level | 6 | Intermediate skill |

#### Scalability

**Score**: 4.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 4 | Partly automatable |
| Target Scope | 3 | One specific target |
| Resource Requirements | 6 | Moderate resources |
| Detection Difficulty | 5 | Detectable with monitoring |

#### Reachability

**Score**: 1.5 | **Trust Zone**: Agent Runtime Zone (Trusted)

intake-agent sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 1.5.

---

### I-1 — audit-ledger

**Threat**: approval and tool call records held by audit-ledger are readable by any service in the Operations Zone that shares the same network role, because access is granted by network position.

**Category**: info-disclosure | **Original Risk Level**: Medium | **Composite**: 4.7 (Medium)

#### CVSS 3.1 Base

**Score**: 5.7 | **Vector**: `CVSS:3.1/AV:A/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Adjacent | Needs an adjacent network |
| Attack Complexity (AC) | Low | No special conditions |
| Privileges Required (PR) | Low | A basic account is needed |
| User Interaction (UI) | None | No user action needed |
| Scope (S) | Unchanged | Impact stays in the component |
| Confidentiality (C) | High | Broad disclosure |
| Integrity (I) | None | No modification |
| Availability (A) | None | No loss of service |

#### Exploitability

**Score**: 5.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 5 | Described in research |
| Attack Complexity | 5 | Needs some preparation |
| Tooling Availability | 6 | Tools need adaptation |
| Skill Level | 4 | Intermediate skill |

#### Scalability

**Score**: 5.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 7 | Fully automatable |
| Target Scope | 6 | A class of targets |
| Resource Requirements | 6 | Moderate resources |
| Detection Difficulty | 3 | Readily detected |

#### Reachability

**Score**: 2.0 | **Trust Zone**: Operations Zone (Trusted)

audit-ledger sits in the Operations Zone. The zone baseline is 2.5 and the refinement for this finding gives 2.0.

---

## 4. Governance Fields

Remediation tracking metadata for each scored finding. Defaults are severity-driven and intended for manual override during risk review.

| ID | Severity | Owner | SLA | Disposition | Review Date |
|----|----------|-------|-----|-------------|-------------|
| S-2 | High | Unassigned | 7d | Mitigate | 2026-11-16 |
| S-1 | High | Unassigned | 7d | Mitigate | 2026-11-16 |
| T-2 | High | Unassigned | 7d | Mitigate | 2026-11-16 |
| T-4 | High | platform-team | 7d | Accept | 2026-11-16 |
| T-1 | Medium | Unassigned | 30d | Review | 2026-12-09 |
| T-3 | Medium | Unassigned | 30d | Review | 2026-12-09 |
| I-1 | Medium | Unassigned | 30d | Review | 2026-12-09 |

---

## 5. Scoring Methodology

This section documents the quantitative scoring model behind the scores in this report.

### 5.1 Scoring Dimensions

| Dimension | Weight | What It Measures |
|-----------|--------|------------------|
| **CVSS Base** | 35% | Intrinsic severity from the CVSS 3.1 base metrics, with the full vector shown for each finding. |
| **Exploitability** | 30% | Practical feasibility from known techniques, complexity, tooling and skill. |
| **Scalability** | 15% | Potential for automated, large-scale use from scriptability, scope, resources and detection difficulty. |
| **Reachability** | 20% | Exposure of the component within the trust boundary architecture, derived from its trust zone. |

### 5.2 Composite Score Formula

```
Composite = (0.35 x CVSS Base) + (0.30 x Exploitability) + (0.15 x Scalability) + (0.20 x Reachability)
```

The composite is rounded to one decimal place and falls in the range 0.0 to 10.0.

### 5.3 Severity Band Mapping

| Severity | Composite Score Range | Default SLA | Default Disposition |
|----------|-----------------------|-------------|---------------------|
| **Critical** | 9.0 -- 10.0 | 24 hours | Mitigate |
| **High** | 7.0 -- 8.9 | 7 days | Mitigate |
| **Medium** | 4.0 -- 6.9 | 30 days | Review |
| **Low** | 0.0 -- 3.9 | 90 days | Review |

Boundary values map to the higher band.

### 5.4 Data Sources

- **Threat findings**: parsed from `threats.md`. All original metadata is preserved.
- **Trust zone data**: taken from the trust zone table of `threats.md` for reachability scoring.
- **Category default vectors**: CVSS 3.1 baselines per threat category, refined for each finding.

### 5.5 Reproducibility

The composite formula, weights and band mapping are deterministic. Each dimension score carries a tolerance of +/- 0.5 between runs.
