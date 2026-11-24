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

12 open findings were scored on 2026-11-09: 0 Critical, 1 High, 11 Medium and 0 Low.

**Highest-Risk Component**: audit-ledger — 2 finding(s), max composite 7.1

**Resolved findings** (Section 2a, outside the distribution below): 0

| Metric | Value |
|--------|-------|
| Scoring date | 2026-11-09 |
| Source file | `baseline/threats.md` |
| Schema version | 1.1 |

**Severity Distribution:**

| Severity | Count | Percentage |
|----------|-------|------------|
| Critical | 0 | 0% |
| High | 1 | 8% |
| Medium | 11 | 92% |
| Low | 0 | 0% |
| **Total** | **12** | **100%** |

> Trust zone data was available for every component, so no reachability value was defaulted.

---

## 2. Scored Threat Table

Findings sorted by Composite score descending (highest risk first), and by finding ID within equal scores. Boundary values map to the higher severity band (e.g., 7.0 = High, 9.0 = Critical).

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

> **Correlated findings**: For correlation groups (Section 4a of the source threat model), the primary finding is scored independently. A NEW or UPDATED peer takes its primary's assessment and is scored with its own asset tags. An UNCHANGED peer keeps its own score, and is flagged `divergent` when that score differs from its primary's.

---

## 3. Dimensional Breakdown

Per-finding detail showing the full scoring rationale for each dimension. One subsection per open finding, ordered by composite score descending (matching Section 2 sort order).

### T-7 — audit-ledger

**Threat**: An attacker who can write to the channel between tool-server-1 and audit-ledger modifies approval and tool call records in transit because messages carry no integrity protection of their own. The weakness sits at layer Security and Compliance of the stack, so every workflow that depends on approval and tool call records inherits the exposure. The change can persist across restarts and restores, which makes the original state difficult to prove and to recover. Rated LOW likelihood because the path needs several preconditions to line up, such as insider access or a rare timing window, and LOW impact because the effect is contained and easy to reverse once it is noticed.

**Category**: tampering | **MAESTRO Layer**: L6 — Security and Compliance | **Original Risk Level**: Note | **Composite**: 7.1 (High)

| Dimension | Score | Weight | Weighted |
|-----------|-------|--------|----------|
| CVSS Base | 9.2 | 0.35 | 3.22 |
| Exploitability | 7.5 | 0.30 | 2.25 |
| Scalability | 7.3 | 0.15 | 1.10 |
| Reachability | 2.5 | 0.20 | 0.50 |
| **Composite** | | | **7.1** |

#### CVSS 3.1 Base

**Score**: 9.2 | **Vector**: `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:L/A:N`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Network | — |
| Attack Complexity (AC) | Low | — |
| Privileges Required (PR) | Low | — |
| User Interaction (UI) | None | — |
| Scope (S) | Changed | — |
| Confidentiality (C) | High | — |
| Integrity (I) | Low | — |
| Availability (A) | None | — |

The vector follows the category default with a network attack path and the stated privileges.

#### Exploitability

**Score**: 7.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 8 | — |
| Attack Complexity | 8 | — |
| Tooling Availability | 7 | — |
| Skill Level | 7 | — |

The sub-scores reflect documented techniques and common tooling for this kind of weakness.

#### Scalability

**Score**: 7.3 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 8 | — |
| Target Scope | 7 | — |
| Resource Requirements | 7 | — |
| Detection Difficulty | 7 | — |

The weakness can be scripted and repeated across instances with modest resources.

#### Reachability

**Score**: 2.5 | **Trust Zone**: Operations Zone (Trusted)

The component sits in a trusted zone with no extra barriers recorded.

---

### T-5 — vector-store-a

**Threat**: Backups and exports of embedded documents and metadata on vector-store-a are writable by operators without a second approver, so a malicious change survives restores. The weakness sits at layer Data Operations of the stack, so every workflow that depends on embedded documents and metadata inherits the exposure. The change can persist across restarts and restores, which makes the original state difficult to prove and to recover. Rated MEDIUM likelihood because the path needs a foothold on a neighbouring service or a prepared request, and MEDIUM impact because the effect is bounded to one workflow or one tenant and can be corrected with effort.

**Category**: tampering | **MAESTRO Layer**: L2 — Data Operations | **Original Risk Level**: Medium | **Composite**: 6.9 (Medium)

| Dimension | Score | Weight | Weighted |
|-----------|-------|--------|----------|
| CVSS Base | 8.6 | 0.35 | 3.01 |
| Exploitability | 8.5 | 0.30 | 2.55 |
| Scalability | 5.3 | 0.15 | 0.80 |
| Reachability | 2.5 | 0.20 | 0.50 |
| **Composite** | | | **6.9** |

#### CVSS 3.1 Base

**Score**: 8.6 | **Vector**: `CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:H/A:L`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Network | — |
| Attack Complexity (AC) | Low | — |
| Privileges Required (PR) | None | — |
| User Interaction (UI) | None | — |
| Scope (S) | Unchanged | — |
| Confidentiality (C) | Low | — |
| Integrity (I) | High | — |
| Availability (A) | Low | — |

The vector follows the category default with a network attack path and the stated privileges.

#### Exploitability

**Score**: 8.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 9 | — |
| Attack Complexity | 9 | — |
| Tooling Availability | 8 | — |
| Skill Level | 8 | — |

The sub-scores reflect documented techniques and common tooling for this kind of weakness.

#### Scalability

**Score**: 5.3 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 6 | — |
| Target Scope | 5 | — |
| Resource Requirements | 5 | — |
| Detection Difficulty | 5 | — |

The weakness can be scripted and repeated across instances with modest resources.

#### Reachability

**Score**: 2.5 | **Trust Zone**: Data Zone (Trusted)

The component sits in a trusted zone with no extra barriers recorded.

---

### S-1 — model-gateway

**Threat**: An attacker replays a captured model API key against model-gateway, which does not bind the credential to the session or channel it was issued for, so the replay is accepted as the original caller. The exposure follows from how model-gateway receives prompts and completions from planner-agent and hands them to the next stage without an independent check. A successful impersonation exposes every function the genuine caller may use and is hard to tell apart from normal traffic. Rated LOW likelihood because the path needs several preconditions to line up, such as insider access or a rare timing window, and MEDIUM impact because the effect is bounded to one workflow or one tenant and can be corrected with effort.

**Category**: spoofing | **MAESTRO Layer**: L1 — Foundation Model | **Original Risk Level**: Low | **Composite**: 6.8 (Medium)

| Dimension | Score | Weight | Weighted |
|-----------|-------|--------|----------|
| CVSS Base | 9.2 | 0.35 | 3.22 |
| Exploitability | 8.5 | 0.30 | 2.55 |
| Scalability | 3.3 | 0.15 | 0.50 |
| Reachability | 2.5 | 0.20 | 0.50 |
| **Composite** | | | **6.8** |

#### CVSS 3.1 Base

**Score**: 9.2 | **Vector**: `CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:C/C:N/I:N/A:L`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Adjacent | — |
| Attack Complexity (AC) | Low | — |
| Privileges Required (PR) | None | — |
| User Interaction (UI) | None | — |
| Scope (S) | Changed | — |
| Confidentiality (C) | None | — |
| Integrity (I) | None | — |
| Availability (A) | Low | — |

The vector follows the category default with a network attack path and the stated privileges.

#### Exploitability

**Score**: 8.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 9 | — |
| Attack Complexity | 9 | — |
| Tooling Availability | 8 | — |
| Skill Level | 8 | — |

The sub-scores reflect documented techniques and common tooling for this kind of weakness.

#### Scalability

**Score**: 3.3 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 4 | — |
| Target Scope | 3 | — |
| Resource Requirements | 3 | — |
| Detection Difficulty | 3 | — |

The weakness can be scripted and repeated across instances with modest resources.

#### Reachability

**Score**: 2.5 | **Trust Zone**: Agent Runtime Zone (Trusted)

The component sits in a trusted zone with no extra barriers recorded.

---

### T-4 — vector-store-a

**Threat**: Serialised objects arriving from worker-2 are deserialised by vector-store-a with permissive type handling, allowing crafted payloads to instantiate unintended behaviour. The weakness sits at layer Data Operations of the stack, so every workflow that depends on embedded documents and metadata inherits the exposure. Altered data is then treated as authoritative by every consumer, so the damage spreads before anyone compares it with the source. Rated MEDIUM likelihood because the path needs a foothold on a neighbouring service or a prepared request, and HIGH impact because the affected data or action is central to shipment handling and hard to reverse.

**Category**: tampering | **MAESTRO Layer**: L2 — Data Operations | **Original Risk Level**: High | **Composite**: 6.8 (Medium)

| Dimension | Score | Weight | Weighted |
|-----------|-------|--------|----------|
| CVSS Base | 7.5 | 0.35 | 2.63 |
| Exploitability | 7.8 | 0.30 | 2.34 |
| Scalability | 8.8 | 0.15 | 1.32 |
| Reachability | 2.5 | 0.20 | 0.50 |
| **Composite** | | | **6.8** |

#### CVSS 3.1 Base

**Score**: 7.5 | **Vector**: `CVSS:3.1/AV:A/AC:L/PR:H/UI:N/S:C/C:L/I:H/A:L`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Adjacent | — |
| Attack Complexity (AC) | Low | — |
| Privileges Required (PR) | High | — |
| User Interaction (UI) | None | — |
| Scope (S) | Changed | — |
| Confidentiality (C) | Low | — |
| Integrity (I) | High | — |
| Availability (A) | Low | — |

The vector follows the category default with a network attack path and the stated privileges.

#### Exploitability

**Score**: 7.8 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 8 | — |
| Attack Complexity | 8 | — |
| Tooling Availability | 8 | — |
| Skill Level | 7 | — |

The sub-scores reflect documented techniques and common tooling for this kind of weakness.

#### Scalability

**Score**: 8.8 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 9 | — |
| Target Scope | 9 | — |
| Resource Requirements | 9 | — |
| Detection Difficulty | 8 | — |

The weakness can be scripted and repeated across instances with modest resources.

#### Reachability

**Score**: 2.5 | **Trust Zone**: Data Zone (Trusted)

The component sits in a trusted zone with no extra barriers recorded.

---

### T-6 — vector-store-a

**Threat**: Unsanitised embedded documents and metadata reach vector-store-a and are processed as trusted structure, so crafted input changes how later steps interpret the record. vector-store-a runs in the Data Zone and exchanges embedded documents and metadata with worker-2 over PostgreSQL over TLS, so anything able to reach worker-2 can also reach this weakness. The change can persist across restarts and restores, which makes the original state difficult to prove and to recover. Rated HIGH likelihood because the path needs no special position and uses interfaces that are exposed by design, and MEDIUM impact because the effect is bounded to one workflow or one tenant and can be corrected with effort.

**Category**: tampering | **MAESTRO Layer**: L2 — Data Operations | **Original Risk Level**: High | **Composite**: 6.8 (Medium)

| Dimension | Score | Weight | Weighted |
|-----------|-------|--------|----------|
| CVSS Base | 7.2 | 0.35 | 2.52 |
| Exploitability | 8.5 | 0.30 | 2.55 |
| Scalability | 8.3 | 0.15 | 1.25 |
| Reachability | 2.5 | 0.20 | 0.50 |
| **Composite** | | | **6.8** |

#### CVSS 3.1 Base

**Score**: 7.2 | **Vector**: `CVSS:3.1/AV:N/AC:H/PR:H/UI:N/S:C/C:L/I:H/A:L`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Network | — |
| Attack Complexity (AC) | High | — |
| Privileges Required (PR) | High | — |
| User Interaction (UI) | None | — |
| Scope (S) | Changed | — |
| Confidentiality (C) | Low | — |
| Integrity (I) | High | — |
| Availability (A) | Low | — |

The vector follows the category default with a network attack path and the stated privileges.

#### Exploitability

**Score**: 8.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 9 | — |
| Attack Complexity | 9 | — |
| Tooling Availability | 8 | — |
| Skill Level | 8 | — |

The sub-scores reflect documented techniques and common tooling for this kind of weakness.

#### Scalability

**Score**: 8.3 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 9 | — |
| Target Scope | 8 | — |
| Resource Requirements | 8 | — |
| Detection Difficulty | 8 | — |

The weakness can be scripted and repeated across instances with modest resources.

#### Reachability

**Score**: 2.5 | **Trust Zone**: Data Zone (Trusted)

The component sits in a trusted zone with no extra barriers recorded.

---

### D-2 — vector-store-a

**Threat**: Retry storms from worker-2 multiply the load on vector-store-a when it slows down, turning a brief delay into a sustained outage. Because vector-store-a serves the Data Zone, a single failure here reaches each consumer of embedded documents and metadata at once. The outage propagates to dependent agents, which stall or retry and prolong the disruption. Rated HIGH likelihood because the path needs no special position and uses interfaces that are exposed by design, and HIGH impact because the affected data or action is central to shipment handling and hard to reverse.

**Category**: denial-of-service | **MAESTRO Layer**: L2 — Data Operations | **Original Risk Level**: Critical | **Composite**: 6.3 (Medium)

| Dimension | Score | Weight | Weighted |
|-----------|-------|--------|----------|
| CVSS Base | 8.8 | 0.35 | 3.08 |
| Exploitability | 6.3 | 0.30 | 1.89 |
| Scalability | 5.5 | 0.15 | 0.83 |
| Reachability | 2.5 | 0.20 | 0.50 |
| **Composite** | | | **6.3** |

#### CVSS 3.1 Base

**Score**: 8.8 | **Vector**: `CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:C/C:L/I:H/A:L`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Adjacent | — |
| Attack Complexity (AC) | Low | — |
| Privileges Required (PR) | None | — |
| User Interaction (UI) | None | — |
| Scope (S) | Changed | — |
| Confidentiality (C) | Low | — |
| Integrity (I) | High | — |
| Availability (A) | Low | — |

The vector follows the category default with a network attack path and the stated privileges.

#### Exploitability

**Score**: 6.3 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 7 | — |
| Attack Complexity | 6 | — |
| Tooling Availability | 6 | — |
| Skill Level | 6 | — |

The sub-scores reflect documented techniques and common tooling for this kind of weakness.

#### Scalability

**Score**: 5.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 6 | — |
| Target Scope | 6 | — |
| Resource Requirements | 5 | — |
| Detection Difficulty | 5 | — |

The weakness can be scripted and repeated across instances with modest resources.

#### Reachability

**Score**: 2.5 | **Trust Zone**: Data Zone (Trusted)

The component sits in a trusted zone with no extra barriers recorded.

---

### T-1 — planner-agent

**Threat**: Unsanitised task plans and tool selections reach planner-agent and are processed as trusted structure, so crafted input changes how later steps interpret the record. The weakness sits at layer Agent Framework of the stack, so every workflow that depends on task plans and tool selections inherits the exposure. Altered data is then treated as authoritative by every consumer, so the damage spreads before anyone compares it with the source. Rated HIGH likelihood because the path needs no special position and uses interfaces that are exposed by design, and HIGH impact because the affected data or action is central to shipment handling and hard to reverse.

**Category**: tampering | **MAESTRO Layer**: L3 — Agent Framework | **Original Risk Level**: Critical | **Composite**: 6.0 (Medium)

| Dimension | Score | Weight | Weighted |
|-----------|-------|--------|----------|
| CVSS Base | 6.4 | 0.35 | 2.24 |
| Exploitability | 8.0 | 0.30 | 2.40 |
| Scalability | 6.0 | 0.15 | 0.90 |
| Reachability | 2.5 | 0.20 | 0.50 |
| **Composite** | | | **6.0** |

#### CVSS 3.1 Base

**Score**: 6.4 | **Vector**: `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:N/I:L/A:L`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Network | — |
| Attack Complexity (AC) | Low | — |
| Privileges Required (PR) | Low | — |
| User Interaction (UI) | None | — |
| Scope (S) | Changed | — |
| Confidentiality (C) | None | — |
| Integrity (I) | Low | — |
| Availability (A) | Low | — |

The vector follows the category default with a network attack path and the stated privileges.

#### Exploitability

**Score**: 8.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 8 | — |
| Attack Complexity | 8 | — |
| Tooling Availability | 8 | — |
| Skill Level | 8 | — |

The sub-scores reflect documented techniques and common tooling for this kind of weakness.

#### Scalability

**Score**: 6.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 6 | — |
| Target Scope | 6 | — |
| Resource Requirements | 6 | — |
| Detection Difficulty | 6 | — |

The weakness can be scripted and repeated across instances with modest resources.

#### Reachability

**Score**: 2.5 | **Trust Zone**: Agent Runtime Zone (Trusted)

The component sits in a trusted zone with no extra barriers recorded.

---

### T-3 — model-gateway

**Threat**: Configuration of model-gateway can be rewritten by any service that holds the shared deployment credential, silently changing how prompts and completions are handled. model-gateway runs in the Agent Runtime Zone and exchanges prompts and completions with planner-agent over HTTPS (TLS 1.3), so anything able to reach planner-agent can also reach this weakness. Altered data is then treated as authoritative by every consumer, so the damage spreads before anyone compares it with the source. Rated LOW likelihood because the path needs several preconditions to line up, such as insider access or a rare timing window, and MEDIUM impact because the effect is bounded to one workflow or one tenant and can be corrected with effort.

**Category**: tampering | **MAESTRO Layer**: L1 — Foundation Model | **Original Risk Level**: Low | **Composite**: 5.9 (Medium)

| Dimension | Score | Weight | Weighted |
|-----------|-------|--------|----------|
| CVSS Base | 7.6 | 0.35 | 2.66 |
| Exploitability | 7.0 | 0.30 | 2.10 |
| Scalability | 4.3 | 0.15 | 0.65 |
| Reachability | 2.5 | 0.20 | 0.50 |
| **Composite** | | | **5.9** |

#### CVSS 3.1 Base

**Score**: 7.6 | **Vector**: `CVSS:3.1/AV:A/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:L`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Adjacent | — |
| Attack Complexity (AC) | Low | — |
| Privileges Required (PR) | None | — |
| User Interaction (UI) | Required | — |
| Scope (S) | Unchanged | — |
| Confidentiality (C) | High | — |
| Integrity (I) | High | — |
| Availability (A) | Low | — |

The vector follows the category default with a network attack path and the stated privileges.

#### Exploitability

**Score**: 7.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 7 | — |
| Attack Complexity | 7 | — |
| Tooling Availability | 7 | — |
| Skill Level | 7 | — |

The sub-scores reflect documented techniques and common tooling for this kind of weakness.

#### Scalability

**Score**: 4.3 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 5 | — |
| Target Scope | 4 | — |
| Resource Requirements | 4 | — |
| Detection Difficulty | 4 | — |

The weakness can be scripted and repeated across instances with modest resources.

#### Reachability

**Score**: 2.5 | **Trust Zone**: Agent Runtime Zone (Trusted)

The component sits in a trusted zone with no extra barriers recorded.

---

### D-1 — tool-server-1

**Threat**: A burst of requests exhausts the connection pool of tool-server-1, which queues work without a bound and blocks legitimate use of tool call arguments and results. Because tool-server-1 serves the Agent Runtime Zone, a single failure here reaches each consumer of tool call arguments and results at once. Operators lose the ability to book or amend shipments while the condition lasts, and recovery depends on manual intervention. Rated MEDIUM likelihood because the path needs a foothold on a neighbouring service or a prepared request, and HIGH impact because the affected data or action is central to shipment handling and hard to reverse.

**Category**: denial-of-service | **MAESTRO Layer**: L3 — Agent Framework | **Original Risk Level**: High | **Composite**: 5.7 (Medium)

| Dimension | Score | Weight | Weighted |
|-----------|-------|--------|----------|
| CVSS Base | 8.6 | 0.35 | 3.01 |
| Exploitability | 4.3 | 0.30 | 1.29 |
| Scalability | 6.3 | 0.15 | 0.95 |
| Reachability | 2.5 | 0.20 | 0.50 |
| **Composite** | | | **5.7** |

#### CVSS 3.1 Base

**Score**: 8.6 | **Vector**: `CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:C/C:H/I:H/A:L`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Local | — |
| Attack Complexity (AC) | Low | — |
| Privileges Required (PR) | None | — |
| User Interaction (UI) | Required | — |
| Scope (S) | Changed | — |
| Confidentiality (C) | High | — |
| Integrity (I) | High | — |
| Availability (A) | Low | — |

The vector follows the category default with a network attack path and the stated privileges.

#### Exploitability

**Score**: 4.3 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 5 | — |
| Attack Complexity | 4 | — |
| Tooling Availability | 4 | — |
| Skill Level | 4 | — |

The sub-scores reflect documented techniques and common tooling for this kind of weakness.

#### Scalability

**Score**: 6.3 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 7 | — |
| Target Scope | 6 | — |
| Resource Requirements | 6 | — |
| Detection Difficulty | 6 | — |

The weakness can be scripted and repeated across instances with modest resources.

#### Reachability

**Score**: 2.5 | **Trust Zone**: Agent Runtime Zone (Trusted)

The component sits in a trusted zone with no extra barriers recorded.

---

### E-1 — model-gateway

**Threat**: Role claims carried in the model API key presented to model-gateway are honoured without confirmation against the authoritative directory. The weakness sits at layer Foundation Model of the stack, so every workflow that depends on prompts and completions inherits the exposure. Once the boundary is crossed the attacker can reach administrative functions and persist there. Rated MEDIUM likelihood because the path needs a foothold on a neighbouring service or a prepared request, and HIGH impact because the affected data or action is central to shipment handling and hard to reverse.

**Category**: privilege-escalation | **MAESTRO Layer**: L1 — Foundation Model | **Original Risk Level**: High | **Composite**: 5.3 (Medium)

| Dimension | Score | Weight | Weighted |
|-----------|-------|--------|----------|
| CVSS Base | 9.9 | 0.35 | 3.47 |
| Exploitability | 3.0 | 0.30 | 0.90 |
| Scalability | 3.0 | 0.15 | 0.45 |
| Reachability | 2.5 | 0.20 | 0.50 |
| **Composite** | | | **5.3** |

#### CVSS 3.1 Base

**Score**: 9.9 | **Vector**: `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Network | — |
| Attack Complexity (AC) | Low | — |
| Privileges Required (PR) | Low | — |
| User Interaction (UI) | None | — |
| Scope (S) | Changed | — |
| Confidentiality (C) | High | — |
| Integrity (I) | High | — |
| Availability (A) | High | — |

The vector follows the category default with a network attack path and the stated privileges.

#### Exploitability

**Score**: 3.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 3 | — |
| Attack Complexity | 3 | — |
| Tooling Availability | 3 | — |
| Skill Level | 3 | — |

The sub-scores reflect documented techniques and common tooling for this kind of weakness.

#### Scalability

**Score**: 3.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 3 | — |
| Target Scope | 3 | — |
| Resource Requirements | 3 | — |
| Detection Difficulty | 3 | — |

The weakness can be scripted and repeated across instances with modest resources.

#### Reachability

**Score**: 2.5 | **Trust Zone**: Agent Runtime Zone (Trusted)

The component sits in a trusted zone with no extra barriers recorded.

---

### D-3 — audit-ledger

**Threat**: Expensive queries over approval and tool call records can be triggered by any authorised caller of audit-ledger, so one user can degrade the service for all. Because audit-ledger serves the Operations Zone, a single failure here reaches each consumer of approval and tool call records at once. The outage propagates to dependent agents, which stall or retry and prolong the disruption. Rated MEDIUM likelihood because the path needs a foothold on a neighbouring service or a prepared request, and MEDIUM impact because the effect is bounded to one workflow or one tenant and can be corrected with effort.

**Category**: denial-of-service | **MAESTRO Layer**: L6 — Security and Compliance | **Original Risk Level**: Medium | **Composite**: 5.2 (Medium)

| Dimension | Score | Weight | Weighted |
|-----------|-------|--------|----------|
| CVSS Base | 6.7 | 0.35 | 2.35 |
| Exploitability | 6.3 | 0.30 | 1.89 |
| Scalability | 3.0 | 0.15 | 0.45 |
| Reachability | 2.5 | 0.20 | 0.50 |
| **Composite** | | | **5.2** |

#### CVSS 3.1 Base

**Score**: 6.7 | **Vector**: `CVSS:3.1/AV:P/AC:H/PR:L/UI:N/S:C/C:H/I:N/A:N`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Physical | — |
| Attack Complexity (AC) | High | — |
| Privileges Required (PR) | Low | — |
| User Interaction (UI) | None | — |
| Scope (S) | Changed | — |
| Confidentiality (C) | High | — |
| Integrity (I) | None | — |
| Availability (A) | None | — |

The vector follows the category default with a network attack path and the stated privileges.

#### Exploitability

**Score**: 6.3 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 7 | — |
| Attack Complexity | 6 | — |
| Tooling Availability | 6 | — |
| Skill Level | 6 | — |

The sub-scores reflect documented techniques and common tooling for this kind of weakness.

#### Scalability

**Score**: 3.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 3 | — |
| Target Scope | 3 | — |
| Resource Requirements | 3 | — |
| Detection Difficulty | 3 | — |

The weakness can be scripted and repeated across instances with modest resources.

#### Reachability

**Score**: 2.5 | **Trust Zone**: Operations Zone (Trusted)

The component sits in a trusted zone with no extra barriers recorded.

---

### T-2 — planner-agent

**Threat**: An attacker who can write to the channel between model-gateway and planner-agent modifies task plans and tool selections in transit because messages carry no integrity protection of their own. planner-agent runs in the Agent Runtime Zone and exchanges task plans and tool selections with model-gateway over HTTPS (TLS 1.3), so anything able to reach model-gateway can also reach this weakness. Altered data is then treated as authoritative by every consumer, so the damage spreads before anyone compares it with the source. Rated HIGH likelihood because the path needs no special position and uses interfaces that are exposed by design, and MEDIUM impact because the effect is bounded to one workflow or one tenant and can be corrected with effort.

**Category**: tampering | **MAESTRO Layer**: L3 — Agent Framework | **Original Risk Level**: High | **Composite**: 4.7 (Medium)

| Dimension | Score | Weight | Weighted |
|-----------|-------|--------|----------|
| CVSS Base | 8.1 | 0.35 | 2.84 |
| Exploitability | 3.0 | 0.30 | 0.90 |
| Scalability | 3.3 | 0.15 | 0.50 |
| Reachability | 2.5 | 0.20 | 0.50 |
| **Composite** | | | **4.7** |

#### CVSS 3.1 Base

**Score**: 8.1 | **Vector**: `CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:L/I:H/A:H`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Local | — |
| Attack Complexity (AC) | Low | — |
| Privileges Required (PR) | Low | — |
| User Interaction (UI) | None | — |
| Scope (S) | Changed | — |
| Confidentiality (C) | Low | — |
| Integrity (I) | High | — |
| Availability (A) | High | — |

The vector follows the category default with a network attack path and the stated privileges.

#### Exploitability

**Score**: 3.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 3 | — |
| Attack Complexity | 3 | — |
| Tooling Availability | 3 | — |
| Skill Level | 3 | — |

The sub-scores reflect documented techniques and common tooling for this kind of weakness.

#### Scalability

**Score**: 3.3 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 4 | — |
| Target Scope | 3 | — |
| Resource Requirements | 3 | — |
| Detection Difficulty | 3 | — |

The weakness can be scripted and repeated across instances with modest resources.

#### Reachability

**Score**: 2.5 | **Trust Zone**: Agent Runtime Zone (Trusted)

The component sits in a trusted zone with no extra barriers recorded.

---

## 4. Governance Fields

Remediation tracking metadata for each scored finding. Default values are severity-driven and intended for manual override by security managers during risk review.

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

This section documents the quantitative scoring model used to produce the risk scores in this report. All scores are derived from the threat findings identified during threat modeling and are intended to replace qualitative risk ratings with data-backed, reproducible numeric assessments.

### 5.1 Scoring Dimensions

Each threat finding is assessed across four independent dimensions, each producing a score on a 0.0 to 10.0 scale.

| Dimension | Weight | What It Measures |
|-----------|--------|------------------|
| **CVSS Base** | 35% | Intrinsic severity of the vulnerability using CVSS 3.1 base metrics: attack vector, attack complexity, privileges required, user interaction, scope, and confidentiality/integrity/availability impact. Each finding includes the full CVSS vector string for auditability. |
| **Exploitability** | 30% | Practical likelihood of exploitation based on known attack techniques, tooling availability, required skill level, and attack complexity. Higher scores indicate threats with well-documented exploit paths and readily available tooling. |
| **Scalability** | 15% | Potential for automated, large-scale exploitation based on scriptability, breadth of target scope, resource requirements for the attacker, and difficulty of detection. Higher scores indicate threats that can be weaponized across many targets with minimal effort. |
| **Reachability** | 20% | Exposure of the targeted component within the system's trust boundary architecture. Derived from trust zone data in the threat model and supplemented by architecture documentation when available. Higher scores indicate components directly exposed to untrusted networks. |

### 5.2 Default Weights and Rationale

The default weight allocation reflects the following priorities:

- **CVSS Base (35%)** receives the highest weight because intrinsic vulnerability severity is the strongest predictor of potential damage. CVSS 3.1 is an industry-standard metric with well-understood interpretation.
- **Exploitability (30%)** is weighted second because a severe vulnerability that is difficult to exploit in practice poses less immediate risk than one with known, tooled attack paths.
- **Reachability (20%)** accounts for architectural context. A critical vulnerability behind multiple trust boundaries and authentication layers presents less operational risk than the same vulnerability on an internet-facing endpoint.
- **Scalability (15%)** receives the lowest weight because while automation potential increases aggregate risk, it is less deterministic than the other dimensions and often correlates with exploitability.

These weights are fixed for this scoring run and are recorded in the report frontmatter for reproducibility.

### 5.3 Composite Score Formula

The composite risk score for each finding is calculated as a weighted sum of the four dimension scores:

```
Composite = (0.35 x CVSS Base) + (0.30 x Exploitability) + (0.15 x Scalability) + (0.20 x Reachability)
```

The sum runs over the stored one-decimal values and is rounded half up to one decimal (a composite of 4.55 is 4.6). The composite score is bounded to the 0.0-10.0 range. Because each dimension is independently scored on a 0.0-10.0 scale and the weights sum to 1.0, the composite inherently falls within this range.

### 5.4 Severity Band Mapping

Composite scores are mapped to severity bands that drive default governance actions:

| Severity | Composite Score Range | Default SLA | Default Disposition |
|----------|-----------------------|-------------|---------------------|
| **Critical** | 9.0 -- 10.0 | 24 hours | Mitigate |
| **High** | 7.0 -- 8.9 | 7 days | Mitigate |
| **Medium** | 4.0 -- 6.9 | 30 days | Review |
| **Low** | 0.0 -- 3.9 | 90 days | Review |

Boundary values map to the higher band (e.g., a composite score of exactly 7.0 maps to High, not Medium). These bands are aligned with the severity classifications defined in `schemas/output.yaml` to maintain backward compatibility with existing tachi threat model output.

### 5.5 Data Sources

Scoring draws on the following inputs:

- **Threat findings**: Parsed from `threats.md` (markdown table format) or `threats.sarif` (SARIF 2.1.0 JSON). All original threat metadata (ID, component, category, description, likelihood, impact) is preserved through the scoring pipeline.
- **Trust zone data**: Extracted from `threats.md` Section 2 (trust zone table) as the primary source for reachability scoring. Components in Untrusted/External zones score 8.0-10.0 reachability; Semi-Trusted/Application zones score 4.0-7.0; Trusted/Internal zones score 1.0-4.0.
- **Architecture documentation**: When `architecture.md` is available, it provides supplementary context such as authentication barriers and network exposure details that refine the baseline reachability score derived from trust zones.
- **Category default vectors**: CVSS 3.1 baseline vectors are defined per STRIDE threat category in `schemas/risk-scoring.yaml`. This includes tachi-specific defaults for AI threat categories (agentic and LLM) that lack standard CVSS mappings. Per-threat analysis may refine these baselines based on the specific threat description.
- **The baseline**: When a baseline `risk-scores.md` is available, a carried finding's inputs (its vector, sub-scores, reachability inputs and human governance fields) come from it, and Section 6 records which baseline was used.

When trust zone data is unavailable (no Section 2 in `threats.md` and no `architecture.md`), a default reachability score of 5.0 is applied with a warning in the output.

### 5.6 Reproducibility

The scorer's assessments (the CVSS vector, the eight sub-scores and the reachability inputs) are produced by an LLM at temperature 0. For the same threat model input, each of them is expected to be reproducible within a **+/- 0.5 tolerance** across runs. This tolerance reflects the inherent variability in LLM-based analysis and is considered acceptable for risk prioritization purposes.

Everything the renderer computes from those assessments is deterministic: the averages, the CVSS base score, the composite, the severity band, the SLA and the review date. The renderer uses exact decimal arithmetic and takes the date as an input, so the same parts and the same date give the same file, byte for byte. The composite formula, weights, and severity band mappings carry no tolerance.

---

## 6. Score Integrity

What the renderer checked, corrected or could not check, and the inputs it scored from. A first run with no baseline has nothing to correct, so its Score Flags table is empty.

### Integrity Summary

| Kind | Cause | Count |
|------|-------|-------|

**Normalized (rounding only)**: 0

**Baseline source**: none

**Tag source**: block

### Score Flags

| ID | Flag | Field | Stored | Rendered | Cause |
|----|------|-------|--------|----------|-------|

### Input Issues

None.

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

<!-- tachi-provenance: renderer=render-risk-scores.py; version=4.48.4; input-digest=sha256:04153ce1af3f854dc240db027e7b9ba99ed11b316652bd0bd63feb6b790d7557 -->
