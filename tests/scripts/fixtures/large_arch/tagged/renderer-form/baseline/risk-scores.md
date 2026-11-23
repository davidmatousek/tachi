---
schema_version: "1.1"
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

**12** threats scored | **0** Critical | **1** High | **11** Medium | **0** Low

**Highest-Risk Component**: audit-ledger — 2 finding(s), max composite 7.1

| Metric | Value |
|--------|-------|
| Scoring date | 2026-11-09 |
| Source file | `baseline/threats.md` |
| Schema version | 1.1 |

**Severity Distribution:**

| Severity | Count | Percentage |
|----------|-------|------------|
| Critical | 0 | 0.0% |
| High | 1 | 8.3% |
| Medium | 11 | 91.7% |
| Low | 0 | 0.0% |
| **Total** | **12** | **100%** |

> Trust zone data was available for every component, so no reachability value was defaulted.

---

## 2. Scored Threat Table

Findings sorted by Composite score descending (highest risk first). Boundary values map to the higher severity band.

| ID | Source | Component | Threat | CVSS | Exploit. | Scale. | Reach. | Composite | Severity | SLA | Disposition | Flags |
|----|--------|-----------|--------|------|----------|--------|--------|-----------|----------|-----|-------------|-------|
| T-7 | fresh | audit-ledger | An attacker who can write to the channel between... | 9.2 | 7.5 | 7.3 | 2.5 | 7.1 | High | 7d | Mitigate | — |
| T-5 | fresh | vector-store-a | Backups and exports of embedded documents and metadata on... | 8.6 | 8.5 | 5.3 | 2.5 | 6.9 | Medium | 30d | Review | — |
| S-1 | fresh | model-gateway | An attacker replays a captured model API key against... | 9.2 | 8.5 | 3.3 | 2.5 | 6.8 | Medium | 30d | Review | — |
| T-4 | fresh | vector-store-a | Serialised objects arriving from worker-2 are deserialised... | 7.5 | 7.8 | 8.8 | 2.5 | 6.8 | Medium | 30d | Review | — |
| T-6 | fresh | vector-store-a | Unsanitised embedded documents and metadata reach... | 7.2 | 8.5 | 8.3 | 2.5 | 6.8 | Medium | 14d | Review | — |
| D-2 | fresh | vector-store-a | Retry storms from worker-2 multiply the load on... | 8.8 | 6.3 | 5.5 | 2.5 | 6.3 | Medium | 30d | Review | — |
| T-1 | fresh | planner-agent | Unsanitised task plans and tool selections reach... | 6.4 | 8.0 | 6.0 | 2.5 | 6.0 | Medium | 30d | Review | — |
| T-3 | fresh | model-gateway | Configuration of model-gateway can be rewritten by any... | 7.6 | 7.0 | 4.3 | 2.5 | 5.9 | Medium | 30d | Review | — |
| D-1 | fresh | tool-server-1 | A burst of requests exhausts the connection pool of... | 8.6 | 4.3 | 6.3 | 2.5 | 5.7 | Medium | 30d | Review | — |
| E-1 | fresh | model-gateway | Role claims carried in the model API key presented to... | 9.9 | 3.0 | 3.0 | 2.5 | 5.3 | Medium | 30d | Review | — |
| D-3 | fresh | audit-ledger | Expensive queries over approval and tool call records can be... | 6.7 | 6.3 | 3.0 | 2.5 | 5.2 | Medium | 30d | Review | — |
| T-2 | fresh | planner-agent | An attacker who can write to the channel between... | 8.1 | 3.0 | 3.3 | 2.5 | 4.7 | Medium | 30d | Review | — |

> **Correlated findings**: for correlation groups (Section 4a of the source threat model), the primary finding is scored independently. Correlated peer findings inherit the primary's scores to keep the group consistent.

---

## 3. Dimensional Breakdown

Per-finding detail showing the scoring rationale for each dimension, in the order of Section 2.

### T-7 — audit-ledger

**Threat**: An attacker who can write to the channel between tool-server-1 and audit-ledger modifies approval and tool call records in transit because messages carry no integrity protection of their own.

**Category**: tampering | **Original Risk Level**: Note | **Composite**: 7.1 (High)

#### CVSS 3.1 Base

**Score**: 9.2 | **Vector**: `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:L/A:N`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Network | Reachable over the network |
| Attack Complexity (AC) | Low | No special conditions |
| Privileges Required (PR) | Low | A basic account is needed |
| User Interaction (UI) | None | No user action needed |
| Scope (S) | Changed | Impact crosses a boundary |
| Confidentiality (C) | High | Broad disclosure |
| Integrity (I) | Low | Limited modification |
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

**Score**: 7.3 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 8 | Fully automatable |
| Target Scope | 7 | Every instance |
| Resource Requirements | 7 | Minimal resources |
| Detection Difficulty | 7 | Blends with normal use |

#### Reachability

**Score**: 2.5 | **Trust Zone**: Operations Zone (Trusted)

audit-ledger sits in the Operations Zone. The zone baseline is 2.5 and the refinement for this finding gives 2.5.

---

### T-5 — vector-store-a

**Threat**: Backups and exports of embedded documents and metadata on vector-store-a are writable by operators without a second approver, so a malicious change survives restores.

**Category**: tampering | **Original Risk Level**: Medium | **Composite**: 6.9 (Medium)

#### CVSS 3.1 Base

**Score**: 8.6 | **Vector**: `CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:H/A:L`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Network | Reachable over the network |
| Attack Complexity (AC) | Low | No special conditions |
| Privileges Required (PR) | None | No privileges needed |
| User Interaction (UI) | None | No user action needed |
| Scope (S) | Unchanged | Impact stays in the component |
| Confidentiality (C) | Low | Limited disclosure |
| Integrity (I) | High | Broad modification |
| Availability (A) | Low | Degraded service |

#### Exploitability

**Score**: 8.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 9 | Documented and widely used |
| Attack Complexity | 9 | A single step suffices |
| Tooling Availability | 8 | Common tools apply |
| Skill Level | 8 | Little skill needed |

#### Scalability

**Score**: 5.3 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 6 | Partly automatable |
| Target Scope | 5 | A class of targets |
| Resource Requirements | 5 | Moderate resources |
| Detection Difficulty | 5 | Detectable with monitoring |

#### Reachability

**Score**: 2.5 | **Trust Zone**: Data Zone (Trusted)

vector-store-a sits in the Data Zone. The zone baseline is 2.5 and the refinement for this finding gives 2.5.

---

### S-1 — model-gateway

**Threat**: An attacker replays a captured model API key against model-gateway, which does not bind the credential to the session or channel it was issued for, so the replay is accepted as the original caller.

**Category**: spoofing | **Original Risk Level**: Low | **Composite**: 6.8 (Medium)

#### CVSS 3.1 Base

**Score**: 9.2 | **Vector**: `CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:C/C:N/I:N/A:L`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Adjacent | Needs an adjacent network |
| Attack Complexity (AC) | Low | No special conditions |
| Privileges Required (PR) | None | No privileges needed |
| User Interaction (UI) | None | No user action needed |
| Scope (S) | Changed | Impact crosses a boundary |
| Confidentiality (C) | None | No disclosure |
| Integrity (I) | None | No modification |
| Availability (A) | Low | Degraded service |

#### Exploitability

**Score**: 8.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 9 | Documented and widely used |
| Attack Complexity | 9 | A single step suffices |
| Tooling Availability | 8 | Common tools apply |
| Skill Level | 8 | Little skill needed |

#### Scalability

**Score**: 3.3 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 4 | Partly automatable |
| Target Scope | 3 | One specific target |
| Resource Requirements | 3 | Needs heavy infrastructure |
| Detection Difficulty | 3 | Readily detected |

#### Reachability

**Score**: 2.5 | **Trust Zone**: Agent Runtime Zone (Trusted)

model-gateway sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 2.5.

---

### T-4 — vector-store-a

**Threat**: Serialised objects arriving from worker-2 are deserialised by vector-store-a with permissive type handling, allowing crafted payloads to instantiate unintended behaviour.

**Category**: tampering | **Original Risk Level**: High | **Composite**: 6.8 (Medium)

#### CVSS 3.1 Base

**Score**: 7.5 | **Vector**: `CVSS:3.1/AV:A/AC:L/PR:H/UI:N/S:C/C:L/I:H/A:L`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Adjacent | Needs an adjacent network |
| Attack Complexity (AC) | Low | No special conditions |
| Privileges Required (PR) | High | Administrative rights are needed |
| User Interaction (UI) | None | No user action needed |
| Scope (S) | Changed | Impact crosses a boundary |
| Confidentiality (C) | Low | Limited disclosure |
| Integrity (I) | High | Broad modification |
| Availability (A) | Low | Degraded service |

#### Exploitability

**Score**: 7.8 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 8 | Documented and widely used |
| Attack Complexity | 8 | A single step suffices |
| Tooling Availability | 8 | Common tools apply |
| Skill Level | 7 | Little skill needed |

#### Scalability

**Score**: 8.8 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 9 | Fully automatable |
| Target Scope | 9 | Every instance |
| Resource Requirements | 9 | Minimal resources |
| Detection Difficulty | 8 | Blends with normal use |

#### Reachability

**Score**: 2.5 | **Trust Zone**: Data Zone (Trusted)

vector-store-a sits in the Data Zone. The zone baseline is 2.5 and the refinement for this finding gives 2.5.

---

### T-6 — vector-store-a

**Threat**: Unsanitised embedded documents and metadata reach vector-store-a and are processed as trusted structure, so crafted input changes how later steps interpret the record.

**Category**: tampering | **Original Risk Level**: High | **Composite**: 6.8 (Medium)

#### CVSS 3.1 Base

**Score**: 7.2 | **Vector**: `CVSS:3.1/AV:N/AC:H/PR:H/UI:N/S:C/C:L/I:H/A:L`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Network | Reachable over the network |
| Attack Complexity (AC) | High | Needs specific conditions |
| Privileges Required (PR) | High | Administrative rights are needed |
| User Interaction (UI) | None | No user action needed |
| Scope (S) | Changed | Impact crosses a boundary |
| Confidentiality (C) | Low | Limited disclosure |
| Integrity (I) | High | Broad modification |
| Availability (A) | Low | Degraded service |

#### Exploitability

**Score**: 8.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 9 | Documented and widely used |
| Attack Complexity | 9 | A single step suffices |
| Tooling Availability | 8 | Common tools apply |
| Skill Level | 8 | Little skill needed |

#### Scalability

**Score**: 8.3 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 9 | Fully automatable |
| Target Scope | 8 | Every instance |
| Resource Requirements | 8 | Minimal resources |
| Detection Difficulty | 8 | Blends with normal use |

#### Reachability

**Score**: 2.5 | **Trust Zone**: Data Zone (Trusted)

vector-store-a sits in the Data Zone. The zone baseline is 2.5 and the refinement for this finding gives 2.5.

---

### D-2 — vector-store-a

**Threat**: Retry storms from worker-2 multiply the load on vector-store-a when it slows down, turning a brief delay into a sustained outage.

**Category**: denial-of-service | **Original Risk Level**: Critical | **Composite**: 6.3 (Medium)

#### CVSS 3.1 Base

**Score**: 8.8 | **Vector**: `CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:C/C:L/I:H/A:L`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Adjacent | Needs an adjacent network |
| Attack Complexity (AC) | Low | No special conditions |
| Privileges Required (PR) | None | No privileges needed |
| User Interaction (UI) | None | No user action needed |
| Scope (S) | Changed | Impact crosses a boundary |
| Confidentiality (C) | Low | Limited disclosure |
| Integrity (I) | High | Broad modification |
| Availability (A) | Low | Degraded service |

#### Exploitability

**Score**: 6.3 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 7 | Documented and widely used |
| Attack Complexity | 6 | Needs some preparation |
| Tooling Availability | 6 | Tools need adaptation |
| Skill Level | 6 | Intermediate skill |

#### Scalability

**Score**: 5.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 6 | Partly automatable |
| Target Scope | 6 | A class of targets |
| Resource Requirements | 5 | Moderate resources |
| Detection Difficulty | 5 | Detectable with monitoring |

#### Reachability

**Score**: 2.5 | **Trust Zone**: Data Zone (Trusted)

vector-store-a sits in the Data Zone. The zone baseline is 2.5 and the refinement for this finding gives 2.5.

---

### T-1 — planner-agent

**Threat**: Unsanitised task plans and tool selections reach planner-agent and are processed as trusted structure, so crafted input changes how later steps interpret the record.

**Category**: tampering | **Original Risk Level**: Critical | **Composite**: 6.0 (Medium)

#### CVSS 3.1 Base

**Score**: 6.4 | **Vector**: `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:N/I:L/A:L`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Network | Reachable over the network |
| Attack Complexity (AC) | Low | No special conditions |
| Privileges Required (PR) | Low | A basic account is needed |
| User Interaction (UI) | None | No user action needed |
| Scope (S) | Changed | Impact crosses a boundary |
| Confidentiality (C) | None | No disclosure |
| Integrity (I) | Low | Limited modification |
| Availability (A) | Low | Degraded service |

#### Exploitability

**Score**: 8.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 8 | Documented and widely used |
| Attack Complexity | 8 | A single step suffices |
| Tooling Availability | 8 | Common tools apply |
| Skill Level | 8 | Little skill needed |

#### Scalability

**Score**: 6.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 6 | Partly automatable |
| Target Scope | 6 | A class of targets |
| Resource Requirements | 6 | Moderate resources |
| Detection Difficulty | 6 | Detectable with monitoring |

#### Reachability

**Score**: 2.5 | **Trust Zone**: Agent Runtime Zone (Trusted)

planner-agent sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 2.5.

---

### T-3 — model-gateway

**Threat**: Configuration of model-gateway can be rewritten by any service that holds the shared deployment credential, silently changing how prompts and completions are handled.

**Category**: tampering | **Original Risk Level**: Low | **Composite**: 5.9 (Medium)

#### CVSS 3.1 Base

**Score**: 7.6 | **Vector**: `CVSS:3.1/AV:A/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:L`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Adjacent | Needs an adjacent network |
| Attack Complexity (AC) | Low | No special conditions |
| Privileges Required (PR) | None | No privileges needed |
| User Interaction (UI) | Required | A user must act |
| Scope (S) | Unchanged | Impact stays in the component |
| Confidentiality (C) | High | Broad disclosure |
| Integrity (I) | High | Broad modification |
| Availability (A) | Low | Degraded service |

#### Exploitability

**Score**: 7.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 7 | Documented and widely used |
| Attack Complexity | 7 | A single step suffices |
| Tooling Availability | 7 | Common tools apply |
| Skill Level | 7 | Little skill needed |

#### Scalability

**Score**: 4.3 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 5 | Partly automatable |
| Target Scope | 4 | A class of targets |
| Resource Requirements | 4 | Moderate resources |
| Detection Difficulty | 4 | Detectable with monitoring |

#### Reachability

**Score**: 2.5 | **Trust Zone**: Agent Runtime Zone (Trusted)

model-gateway sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 2.5.

---

### D-1 — tool-server-1

**Threat**: A burst of requests exhausts the connection pool of tool-server-1, which queues work without a bound and blocks legitimate use of tool call arguments and results.

**Category**: denial-of-service | **Original Risk Level**: High | **Composite**: 5.7 (Medium)

#### CVSS 3.1 Base

**Score**: 8.6 | **Vector**: `CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:C/C:H/I:H/A:L`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Local | Needs local access |
| Attack Complexity (AC) | Low | No special conditions |
| Privileges Required (PR) | None | No privileges needed |
| User Interaction (UI) | Required | A user must act |
| Scope (S) | Changed | Impact crosses a boundary |
| Confidentiality (C) | High | Broad disclosure |
| Integrity (I) | High | Broad modification |
| Availability (A) | Low | Degraded service |

#### Exploitability

**Score**: 4.3 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 5 | Described in research |
| Attack Complexity | 4 | Needs some preparation |
| Tooling Availability | 4 | Tools need adaptation |
| Skill Level | 4 | Intermediate skill |

#### Scalability

**Score**: 6.3 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 7 | Fully automatable |
| Target Scope | 6 | A class of targets |
| Resource Requirements | 6 | Moderate resources |
| Detection Difficulty | 6 | Detectable with monitoring |

#### Reachability

**Score**: 2.5 | **Trust Zone**: Agent Runtime Zone (Trusted)

tool-server-1 sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 2.5.

---

### E-1 — model-gateway

**Threat**: Role claims carried in the model API key presented to model-gateway are honoured without confirmation against the authoritative directory.

**Category**: privilege-escalation | **Original Risk Level**: High | **Composite**: 5.3 (Medium)

#### CVSS 3.1 Base

**Score**: 9.9 | **Vector**: `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Network | Reachable over the network |
| Attack Complexity (AC) | Low | No special conditions |
| Privileges Required (PR) | Low | A basic account is needed |
| User Interaction (UI) | None | No user action needed |
| Scope (S) | Changed | Impact crosses a boundary |
| Confidentiality (C) | High | Broad disclosure |
| Integrity (I) | High | Broad modification |
| Availability (A) | High | Loss of service |

#### Exploitability

**Score**: 3.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 3 | Not described outside research |
| Attack Complexity | 3 | Needs chained steps |
| Tooling Availability | 3 | Needs custom tooling |
| Skill Level | 3 | Needs deep expertise |

#### Scalability

**Score**: 3.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 3 | Manual for each target |
| Target Scope | 3 | One specific target |
| Resource Requirements | 3 | Needs heavy infrastructure |
| Detection Difficulty | 3 | Readily detected |

#### Reachability

**Score**: 2.5 | **Trust Zone**: Agent Runtime Zone (Trusted)

model-gateway sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 2.5.

---

### D-3 — audit-ledger

**Threat**: Expensive queries over approval and tool call records can be triggered by any authorised caller of audit-ledger, so one user can degrade the service for all.

**Category**: denial-of-service | **Original Risk Level**: Medium | **Composite**: 5.2 (Medium)

#### CVSS 3.1 Base

**Score**: 6.7 | **Vector**: `CVSS:3.1/AV:P/AC:H/PR:L/UI:N/S:C/C:H/I:N/A:N`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Physical | Needs physical access |
| Attack Complexity (AC) | High | Needs specific conditions |
| Privileges Required (PR) | Low | A basic account is needed |
| User Interaction (UI) | None | No user action needed |
| Scope (S) | Changed | Impact crosses a boundary |
| Confidentiality (C) | High | Broad disclosure |
| Integrity (I) | None | No modification |
| Availability (A) | None | No loss of service |

#### Exploitability

**Score**: 6.3 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 7 | Documented and widely used |
| Attack Complexity | 6 | Needs some preparation |
| Tooling Availability | 6 | Tools need adaptation |
| Skill Level | 6 | Intermediate skill |

#### Scalability

**Score**: 3.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 3 | Manual for each target |
| Target Scope | 3 | One specific target |
| Resource Requirements | 3 | Needs heavy infrastructure |
| Detection Difficulty | 3 | Readily detected |

#### Reachability

**Score**: 2.5 | **Trust Zone**: Operations Zone (Trusted)

audit-ledger sits in the Operations Zone. The zone baseline is 2.5 and the refinement for this finding gives 2.5.

---

### T-2 — planner-agent

**Threat**: An attacker who can write to the channel between model-gateway and planner-agent modifies task plans and tool selections in transit because messages carry no integrity protection of their own.

**Category**: tampering | **Original Risk Level**: High | **Composite**: 4.7 (Medium)

#### CVSS 3.1 Base

**Score**: 8.1 | **Vector**: `CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:L/I:H/A:H`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Local | Needs local access |
| Attack Complexity (AC) | Low | No special conditions |
| Privileges Required (PR) | Low | A basic account is needed |
| User Interaction (UI) | None | No user action needed |
| Scope (S) | Changed | Impact crosses a boundary |
| Confidentiality (C) | Low | Limited disclosure |
| Integrity (I) | High | Broad modification |
| Availability (A) | High | Loss of service |

#### Exploitability

**Score**: 3.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 3 | Not described outside research |
| Attack Complexity | 3 | Needs chained steps |
| Tooling Availability | 3 | Needs custom tooling |
| Skill Level | 3 | Needs deep expertise |

#### Scalability

**Score**: 3.3 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 4 | Partly automatable |
| Target Scope | 3 | One specific target |
| Resource Requirements | 3 | Needs heavy infrastructure |
| Detection Difficulty | 3 | Readily detected |

#### Reachability

**Score**: 2.5 | **Trust Zone**: Agent Runtime Zone (Trusted)

planner-agent sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 2.5.

---

## 4. Governance Fields

Remediation tracking metadata for each scored finding. Defaults are severity-driven and intended for manual override during risk review.

| ID | Severity | Owner | SLA | Disposition | Review Date |
|----|----------|-------|-----|-------------|-------------|
| T-7 | High | Unassigned | 7d | Mitigate | 2026-11-16 |
| T-5 | Medium | Unassigned | 30d | Review | 2026-10-28 |
| S-1 | Medium | Unassigned | 30d | Review | 2026-12-09 |
| T-4 | Medium | Unassigned | 30d | Review | 2026-12-09 |
| T-6 | Medium | platform-team | 14d | Review | 2026-11-23 |
| D-2 | Medium | Unassigned | 30d | Review | 2026-12-09 |
| T-1 | Medium | Unassigned | 30d | Review | 2026-12-09 |
| T-3 | Medium | Unassigned | 30d | Review | 2026-12-09 |
| D-1 | Medium | Unassigned | 30d | Review | 2026-12-09 |
| E-1 | Medium | Unassigned | 30d | Review | 2026-12-09 |
| D-3 | Medium | Unassigned | 30d | Review | 2026-12-09 |
| T-2 | Medium | Unassigned | 30d | Review | 2026-12-09 |

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


---

## 6. Score Integrity

What the renderer changed or could not check, and the inputs it scored from. The next run reads its carried inputs from the last table.

### Integrity Summary

| Kind | Count |
|------|-------|
| corrected | 0 |
| retagged | 0 |
| unchecked | 0 |
| normalized | 0 |

### Score Flags

| ID | Flag | Field | Stored | Rendered | Cause |
|----|------|-------|--------|----------|-------|

### Input Issues

| ID | Field | Cause | Detail |
|----|-------|-------|--------|

### Scoring Inputs

| ID | Field | Value |
|----|-------|-------|
| S-1 | cvss_vector | CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:C/C:N/I:N/A:L |
| S-1 | exploitability.known_techniques | 9 |
| S-1 | exploitability.attack_complexity | 9 |
| S-1 | exploitability.tooling_availability | 8 |
| S-1 | exploitability.skill_level | 8 |
| S-1 | scalability.scriptability | 4 |
| S-1 | scalability.target_scope | 3 |
| S-1 | scalability.resource_requirements | 3 |
| S-1 | scalability.detection_difficulty | 3 |
| S-1 | reachability.zone | Agent Runtime Zone |
| S-1 | reachability.trust_level | Trusted |
| S-1 | reachability.auth_barriers | 0 |
| S-1 | reachability.network_boundaries | 0 |
| S-1 | rationale.cvss | The vector follows the category default with a network attack path and the stated privileges. |
| S-1 | rationale.exploitability | The sub-scores reflect documented techniques and common tooling for this kind of weakness. |
| S-1 | rationale.scalability | The weakness can be scripted and repeated across instances with modest resources. |
| S-1 | rationale.reachability | The component sits in a trusted zone with no extra barriers recorded. |
| S-1 | tags | secrets |
| S-1 | scored_on | 2026-11-09 |
| T-1 | cvss_vector | CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:N/I:L/A:L |
| T-1 | exploitability.known_techniques | 8 |
| T-1 | exploitability.attack_complexity | 8 |
| T-1 | exploitability.tooling_availability | 8 |
| T-1 | exploitability.skill_level | 8 |
| T-1 | scalability.scriptability | 6 |
| T-1 | scalability.target_scope | 6 |
| T-1 | scalability.resource_requirements | 6 |
| T-1 | scalability.detection_difficulty | 6 |
| T-1 | reachability.zone | Agent Runtime Zone |
| T-1 | reachability.trust_level | Trusted |
| T-1 | reachability.auth_barriers | 0 |
| T-1 | reachability.network_boundaries | 0 |
| T-1 | rationale.cvss | The vector follows the category default with a network attack path and the stated privileges. |
| T-1 | rationale.exploitability | The sub-scores reflect documented techniques and common tooling for this kind of weakness. |
| T-1 | rationale.scalability | The weakness can be scripted and repeated across instances with modest resources. |
| T-1 | rationale.reachability | The component sits in a trusted zone with no extra barriers recorded. |
| T-1 | tags |  |
| T-1 | scored_on | 2026-11-09 |
| T-2 | cvss_vector | CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:L/I:H/A:H |
| T-2 | exploitability.known_techniques | 3 |
| T-2 | exploitability.attack_complexity | 3 |
| T-2 | exploitability.tooling_availability | 3 |
| T-2 | exploitability.skill_level | 3 |
| T-2 | scalability.scriptability | 4 |
| T-2 | scalability.target_scope | 3 |
| T-2 | scalability.resource_requirements | 3 |
| T-2 | scalability.detection_difficulty | 3 |
| T-2 | reachability.zone | Agent Runtime Zone |
| T-2 | reachability.trust_level | Trusted |
| T-2 | reachability.auth_barriers | 0 |
| T-2 | reachability.network_boundaries | 0 |
| T-2 | rationale.cvss | The vector follows the category default with a network attack path and the stated privileges. |
| T-2 | rationale.exploitability | The sub-scores reflect documented techniques and common tooling for this kind of weakness. |
| T-2 | rationale.scalability | The weakness can be scripted and repeated across instances with modest resources. |
| T-2 | rationale.reachability | The component sits in a trusted zone with no extra barriers recorded. |
| T-2 | score_bounds | 6.1,8.1 |
| T-2 | tags |  |
| T-2 | scored_on | 2026-11-09 |
| T-3 | cvss_vector | CVSS:3.1/AV:A/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:L |
| T-3 | exploitability.known_techniques | 7 |
| T-3 | exploitability.attack_complexity | 7 |
| T-3 | exploitability.tooling_availability | 7 |
| T-3 | exploitability.skill_level | 7 |
| T-3 | scalability.scriptability | 5 |
| T-3 | scalability.target_scope | 4 |
| T-3 | scalability.resource_requirements | 4 |
| T-3 | scalability.detection_difficulty | 4 |
| T-3 | reachability.zone | Agent Runtime Zone |
| T-3 | reachability.trust_level | Trusted |
| T-3 | reachability.auth_barriers | 0 |
| T-3 | reachability.network_boundaries | 0 |
| T-3 | rationale.cvss | The vector follows the category default with a network attack path and the stated privileges. |
| T-3 | rationale.exploitability | The sub-scores reflect documented techniques and common tooling for this kind of weakness. |
| T-3 | rationale.scalability | The weakness can be scripted and repeated across instances with modest resources. |
| T-3 | rationale.reachability | The component sits in a trusted zone with no extra barriers recorded. |
| T-3 | tags | secrets |
| T-3 | scored_on | 2026-11-09 |
| T-4 | cvss_vector | CVSS:3.1/AV:A/AC:L/PR:H/UI:N/S:C/C:L/I:H/A:L |
| T-4 | exploitability.known_techniques | 8 |
| T-4 | exploitability.attack_complexity | 8 |
| T-4 | exploitability.tooling_availability | 8 |
| T-4 | exploitability.skill_level | 7 |
| T-4 | scalability.scriptability | 9 |
| T-4 | scalability.target_scope | 9 |
| T-4 | scalability.resource_requirements | 9 |
| T-4 | scalability.detection_difficulty | 8 |
| T-4 | reachability.zone | Data Zone |
| T-4 | reachability.trust_level | Trusted |
| T-4 | reachability.auth_barriers | 0 |
| T-4 | reachability.network_boundaries | 0 |
| T-4 | rationale.cvss | The vector follows the category default with a network attack path and the stated privileges. |
| T-4 | rationale.exploitability | The sub-scores reflect documented techniques and common tooling for this kind of weakness. |
| T-4 | rationale.scalability | The weakness can be scripted and repeated across instances with modest resources. |
| T-4 | rationale.reachability | The component sits in a trusted zone with no extra barriers recorded. |
| T-4 | tags |  |
| T-4 | scored_on | 2026-11-09 |
| T-5 | cvss_vector | CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:H/A:L |
| T-5 | exploitability.known_techniques | 9 |
| T-5 | exploitability.attack_complexity | 9 |
| T-5 | exploitability.tooling_availability | 8 |
| T-5 | exploitability.skill_level | 8 |
| T-5 | scalability.scriptability | 6 |
| T-5 | scalability.target_scope | 5 |
| T-5 | scalability.resource_requirements | 5 |
| T-5 | scalability.detection_difficulty | 5 |
| T-5 | reachability.zone | Data Zone |
| T-5 | reachability.trust_level | Trusted |
| T-5 | reachability.auth_barriers | 0 |
| T-5 | reachability.network_boundaries | 0 |
| T-5 | rationale.cvss | The vector follows the category default with a network attack path and the stated privileges. |
| T-5 | rationale.exploitability | The sub-scores reflect documented techniques and common tooling for this kind of weakness. |
| T-5 | rationale.scalability | The weakness can be scripted and repeated across instances with modest resources. |
| T-5 | rationale.reachability | The component sits in a trusted zone with no extra barriers recorded. |
| T-5 | tags |  |
| T-5 | scored_on | 2026-09-28 |
| T-6 | cvss_vector | CVSS:3.1/AV:N/AC:H/PR:H/UI:N/S:C/C:L/I:H/A:L |
| T-6 | exploitability.known_techniques | 9 |
| T-6 | exploitability.attack_complexity | 9 |
| T-6 | exploitability.tooling_availability | 8 |
| T-6 | exploitability.skill_level | 8 |
| T-6 | scalability.scriptability | 9 |
| T-6 | scalability.target_scope | 8 |
| T-6 | scalability.resource_requirements | 8 |
| T-6 | scalability.detection_difficulty | 8 |
| T-6 | reachability.zone | Data Zone |
| T-6 | reachability.trust_level | Trusted |
| T-6 | reachability.auth_barriers | 0 |
| T-6 | reachability.network_boundaries | 0 |
| T-6 | rationale.cvss | The vector follows the category default with a network attack path and the stated privileges. |
| T-6 | rationale.exploitability | The sub-scores reflect documented techniques and common tooling for this kind of weakness. |
| T-6 | rationale.scalability | The weakness can be scripted and repeated across instances with modest resources. |
| T-6 | rationale.reachability | The component sits in a trusted zone with no extra barriers recorded. |
| T-6 | tags |  |
| T-6 | scored_on | 2026-11-09 |
| T-7 | cvss_vector | CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:L/A:N |
| T-7 | exploitability.known_techniques | 8 |
| T-7 | exploitability.attack_complexity | 8 |
| T-7 | exploitability.tooling_availability | 7 |
| T-7 | exploitability.skill_level | 7 |
| T-7 | scalability.scriptability | 8 |
| T-7 | scalability.target_scope | 7 |
| T-7 | scalability.resource_requirements | 7 |
| T-7 | scalability.detection_difficulty | 7 |
| T-7 | reachability.zone | Operations Zone |
| T-7 | reachability.trust_level | Trusted |
| T-7 | reachability.auth_barriers | 0 |
| T-7 | reachability.network_boundaries | 0 |
| T-7 | rationale.cvss | The vector follows the category default with a network attack path and the stated privileges. |
| T-7 | rationale.exploitability | The sub-scores reflect documented techniques and common tooling for this kind of weakness. |
| T-7 | rationale.scalability | The weakness can be scripted and repeated across instances with modest resources. |
| T-7 | rationale.reachability | The component sits in a trusted zone with no extra barriers recorded. |
| T-7 | tags | financial |
| T-7 | scored_on | 2026-11-09 |
| D-1 | cvss_vector | CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:C/C:H/I:H/A:L |
| D-1 | exploitability.known_techniques | 5 |
| D-1 | exploitability.attack_complexity | 4 |
| D-1 | exploitability.tooling_availability | 4 |
| D-1 | exploitability.skill_level | 4 |
| D-1 | scalability.scriptability | 7 |
| D-1 | scalability.target_scope | 6 |
| D-1 | scalability.resource_requirements | 6 |
| D-1 | scalability.detection_difficulty | 6 |
| D-1 | reachability.zone | Agent Runtime Zone |
| D-1 | reachability.trust_level | Trusted |
| D-1 | reachability.auth_barriers | 0 |
| D-1 | reachability.network_boundaries | 0 |
| D-1 | rationale.cvss | The vector follows the category default with a network attack path and the stated privileges. |
| D-1 | rationale.exploitability | The sub-scores reflect documented techniques and common tooling for this kind of weakness. |
| D-1 | rationale.scalability | The weakness can be scripted and repeated across instances with modest resources. |
| D-1 | rationale.reachability | The component sits in a trusted zone with no extra barriers recorded. |
| D-1 | tags | safety |
| D-1 | scored_on | 2026-11-09 |
| D-2 | cvss_vector | CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:C/C:L/I:H/A:L |
| D-2 | exploitability.known_techniques | 7 |
| D-2 | exploitability.attack_complexity | 6 |
| D-2 | exploitability.tooling_availability | 6 |
| D-2 | exploitability.skill_level | 6 |
| D-2 | scalability.scriptability | 6 |
| D-2 | scalability.target_scope | 6 |
| D-2 | scalability.resource_requirements | 5 |
| D-2 | scalability.detection_difficulty | 5 |
| D-2 | reachability.zone | Data Zone |
| D-2 | reachability.trust_level | Trusted |
| D-2 | reachability.auth_barriers | 0 |
| D-2 | reachability.network_boundaries | 0 |
| D-2 | rationale.cvss | The vector follows the category default with a network attack path and the stated privileges. |
| D-2 | rationale.exploitability | The sub-scores reflect documented techniques and common tooling for this kind of weakness. |
| D-2 | rationale.scalability | The weakness can be scripted and repeated across instances with modest resources. |
| D-2 | rationale.reachability | The component sits in a trusted zone with no extra barriers recorded. |
| D-2 | tags |  |
| D-2 | scored_on | 2026-11-09 |
| D-3 | cvss_vector | CVSS:3.1/AV:P/AC:H/PR:L/UI:N/S:C/C:H/I:N/A:N |
| D-3 | exploitability.known_techniques | 7 |
| D-3 | exploitability.attack_complexity | 6 |
| D-3 | exploitability.tooling_availability | 6 |
| D-3 | exploitability.skill_level | 6 |
| D-3 | scalability.scriptability | 3 |
| D-3 | scalability.target_scope | 3 |
| D-3 | scalability.resource_requirements | 3 |
| D-3 | scalability.detection_difficulty | 3 |
| D-3 | reachability.zone | Operations Zone |
| D-3 | reachability.trust_level | Trusted |
| D-3 | reachability.auth_barriers | 0 |
| D-3 | reachability.network_boundaries | 0 |
| D-3 | rationale.cvss | The vector follows the category default with a network attack path and the stated privileges. |
| D-3 | rationale.exploitability | The sub-scores reflect documented techniques and common tooling for this kind of weakness. |
| D-3 | rationale.scalability | The weakness can be scripted and repeated across instances with modest resources. |
| D-3 | rationale.reachability | The component sits in a trusted zone with no extra barriers recorded. |
| D-3 | tags | financial |
| D-3 | scored_on | 2026-11-09 |
| E-1 | cvss_vector | CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H |
| E-1 | exploitability.known_techniques | 3 |
| E-1 | exploitability.attack_complexity | 3 |
| E-1 | exploitability.tooling_availability | 3 |
| E-1 | exploitability.skill_level | 3 |
| E-1 | scalability.scriptability | 3 |
| E-1 | scalability.target_scope | 3 |
| E-1 | scalability.resource_requirements | 3 |
| E-1 | scalability.detection_difficulty | 3 |
| E-1 | reachability.zone | Agent Runtime Zone |
| E-1 | reachability.trust_level | Trusted |
| E-1 | reachability.auth_barriers | 0 |
| E-1 | reachability.network_boundaries | 0 |
| E-1 | rationale.cvss | The vector follows the category default with a network attack path and the stated privileges. |
| E-1 | rationale.exploitability | The sub-scores reflect documented techniques and common tooling for this kind of weakness. |
| E-1 | rationale.scalability | The weakness can be scripted and repeated across instances with modest resources. |
| E-1 | rationale.reachability | The component sits in a trusted zone with no extra barriers recorded. |
| E-1 | tags | secrets |
| E-1 | scored_on | 2026-11-09 |
