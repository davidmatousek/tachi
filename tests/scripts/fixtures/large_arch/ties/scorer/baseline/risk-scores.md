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

**9** threats scored | **1** Critical | **3** High | **4** Medium | **1** Low

**Highest-Risk Component**: edge-gateway — 7 finding(s), max composite 9.0

| Metric | Value |
|--------|-------|
| Scoring date | 2026-11-09 |
| Source file | `baseline/threats.md` |
| Schema version | 1.0 |

**Severity Distribution:**

| Severity | Count | Percentage |
|----------|-------|------------|
| Critical | 1 | 11.1% |
| High | 3 | 33.3% |
| Medium | 4 | 44.5% |
| Low | 1 | 11.1% |
| **Total** | **9** | **100%** |

> Trust zone data was available for every component, so no reachability value was defaulted.

---

## 2. Scored Threat Table

Findings sorted by Composite score descending (highest risk first). Boundary values map to the higher severity band.

| ID | Source | Component | Threat | CVSS | Exploit. | Scale. | Reach. | Composite | Severity | SLA | Disposition |
|----|--------|-----------|--------|------|----------|--------|--------|-----------|----------|-----|-------------|
| E-1 | fresh | edge-gateway | Object identifiers in requests to edge-gateway are trusted... | 9.6 | 9.8 | 10.0 | 6.0 | 9.0 | Critical | 24h | Mitigate |
| T-1 | fresh | edge-gateway | An attacker who can write to the channel between auth-broker... | 9.8 | 10.0 | 8.8 | 6.0 | 8.9 | High | 7d | Mitigate |
| LLM-1 | fresh | edge-gateway | edge-gateway passes conversation history from earlier turns... | 9.6 | 8.3 | 6.0 | 7.0 | 8.2 | High | 7d | Mitigate |
| D-1 | fresh | edge-gateway | A dependency of edge-gateway becomes unavailable and the... | 4.6 | 9.3 | 8.0 | 7.0 | 7.0 | High | 7d | Mitigate |
| S-1 | fresh | edge-gateway | A shared or long-lived bearer token on edge-gateway lets... | 8.3 | 4.5 | 9.3 | 6.5 | 6.9 | Medium | 30d | Review |
| I-1 | fresh | edge-gateway | Secrets such as the bearer token for edge-gateway appear in... | 7.5 | 4.5 | 8.5 | 6.0 | 6.4 | Medium | 30d | Review |
| R-1 | fresh | edge-gateway | Log entries from edge-gateway can be edited or deleted by... | 4.3 | 5.0 | 4.3 | 4.0 | 4.4 | Medium | 30d | Review |
| AG-1 | fresh | intake-agent | Memory written by intake-agent is trusted on later runs, so... | 5.5 | 4.0 | 4.5 | 1.0 | 4.0 | Medium | 30d | Review |
| MI-1 | fresh | intake-agent | intake-agent fabricates reference numbers and clause... | 5.1 | 4.8 | 3.5 | 1.0 | 3.9 | Low | 90d | Review |

> **Correlated findings**: for correlation groups (Section 4a of the source threat model), the primary finding is scored independently. Correlated peer findings inherit the primary's scores to keep the group consistent.

---

## 3. Dimensional Breakdown

Per-finding detail showing the scoring rationale for each dimension, in the order of Section 2.

### E-1 — edge-gateway

**Threat**: Object identifiers in requests to edge-gateway are trusted without an ownership check, so a caller can read or change inbound API requests that belong to others.

**Category**: privilege-escalation | **Original Risk Level**: High | **Composite**: 9.0 (Critical)

#### CVSS 3.1 Base

**Score**: 9.6 | **Vector**: `CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Adjacent | Needs an adjacent network |
| Attack Complexity (AC) | Low | No special conditions |
| Privileges Required (PR) | None | No privileges needed |
| User Interaction (UI) | None | No user action needed |
| Scope (S) | Changed | Impact crosses a boundary |
| Confidentiality (C) | High | Broad disclosure |
| Integrity (I) | High | Broad modification |
| Availability (A) | High | Loss of service |

#### Exploitability

**Score**: 9.8 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 10 | Documented and widely used |
| Attack Complexity | 10 | A single step suffices |
| Tooling Availability | 10 | Common tools apply |
| Skill Level | 9 | Little skill needed |

#### Scalability

**Score**: 10.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 10 | Fully automatable |
| Target Scope | 10 | Every instance |
| Resource Requirements | 10 | Minimal resources |
| Detection Difficulty | 10 | Blends with normal use |

#### Reachability

**Score**: 6.0 | **Trust Zone**: Edge DMZ (Semi-trusted)

edge-gateway sits in the Edge DMZ. The zone baseline is 6.5 and the refinement for this finding gives 6.0.

---

### T-1 — edge-gateway

**Threat**: An attacker who can write to the channel between auth-broker and edge-gateway modifies inbound API requests in transit because messages carry no integrity protection of their own.

**Category**: tampering | **Original Risk Level**: Medium | **Composite**: 8.9 (High)

#### CVSS 3.1 Base

**Score**: 9.8 | **Vector**: `CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Network | Reachable over the network |
| Attack Complexity (AC) | Low | No special conditions |
| Privileges Required (PR) | None | No privileges needed |
| User Interaction (UI) | None | No user action needed |
| Scope (S) | Unchanged | Impact stays in the component |
| Confidentiality (C) | High | Broad disclosure |
| Integrity (I) | High | Broad modification |
| Availability (A) | High | Loss of service |

#### Exploitability

**Score**: 10.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 10 | Documented and widely used |
| Attack Complexity | 10 | A single step suffices |
| Tooling Availability | 10 | Common tools apply |
| Skill Level | 10 | Little skill needed |

#### Scalability

**Score**: 8.8 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 9 | Fully automatable |
| Target Scope | 9 | Every instance |
| Resource Requirements | 9 | Minimal resources |
| Detection Difficulty | 8 | Blends with normal use |

#### Reachability

**Score**: 6.0 | **Trust Zone**: Edge DMZ (Semi-trusted)

edge-gateway sits in the Edge DMZ. The zone baseline is 6.5 and the refinement for this finding gives 6.0.

---

### LLM-1 — edge-gateway

**Threat**: edge-gateway passes conversation history from earlier turns into the model unchanged, so an injection planted earlier keeps working in later turns.

**Category**: llm | **Original Risk Level**: Medium | **Composite**: 8.2 (High)

#### CVSS 3.1 Base

**Score**: 9.6 | **Vector**: `CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:H/A:L`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Network | Reachable over the network |
| Attack Complexity (AC) | Low | No special conditions |
| Privileges Required (PR) | None | No privileges needed |
| User Interaction (UI) | Required | A user must act |
| Scope (S) | Changed | Impact crosses a boundary |
| Confidentiality (C) | High | Broad disclosure |
| Integrity (I) | High | Broad modification |
| Availability (A) | Low | Degraded service |

#### Exploitability

**Score**: 8.3 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 9 | Documented and widely used |
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

**Score**: 7.0 | **Trust Zone**: Edge DMZ (Semi-trusted)

edge-gateway sits in the Edge DMZ. The zone baseline is 6.5 and the refinement for this finding gives 7.0.

---

### D-1 — edge-gateway

**Threat**: A dependency of edge-gateway becomes unavailable and the failure cascades because edge-gateway waits on it synchronously for every request.

**Category**: denial-of-service | **Original Risk Level**: Medium | **Composite**: 7.0 (High)

#### CVSS 3.1 Base

**Score**: 4.6 | **Vector**: `CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:N/I:L/A:L`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Network | Reachable over the network |
| Attack Complexity (AC) | Low | No special conditions |
| Privileges Required (PR) | Low | A basic account is needed |
| User Interaction (UI) | Required | A user must act |
| Scope (S) | Unchanged | Impact stays in the component |
| Confidentiality (C) | None | No disclosure |
| Integrity (I) | Low | Limited modification |
| Availability (A) | Low | Degraded service |

#### Exploitability

**Score**: 9.3 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 10 | Documented and widely used |
| Attack Complexity | 9 | A single step suffices |
| Tooling Availability | 9 | Common tools apply |
| Skill Level | 9 | Little skill needed |

#### Scalability

**Score**: 8.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 8 | Fully automatable |
| Target Scope | 8 | Every instance |
| Resource Requirements | 8 | Minimal resources |
| Detection Difficulty | 8 | Blends with normal use |

#### Reachability

**Score**: 7.0 | **Trust Zone**: Edge DMZ (Semi-trusted)

edge-gateway sits in the Edge DMZ. The zone baseline is 6.5 and the refinement for this finding gives 7.0.

---

### S-1 — edge-gateway

**Threat**: A shared or long-lived bearer token on edge-gateway lets anyone who obtains one copy authenticate as every tenant that uses the same deployment profile.

**Category**: spoofing | **Original Risk Level**: Critical | **Composite**: 6.9 (Medium)

#### CVSS 3.1 Base

**Score**: 8.3 | **Vector**: `CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:L`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Network | Reachable over the network |
| Attack Complexity (AC) | Low | No special conditions |
| Privileges Required (PR) | None | No privileges needed |
| User Interaction (UI) | Required | A user must act |
| Scope (S) | Unchanged | Impact stays in the component |
| Confidentiality (C) | High | Broad disclosure |
| Integrity (I) | High | Broad modification |
| Availability (A) | Low | Degraded service |

#### Exploitability

**Score**: 4.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 5 | Described in research |
| Attack Complexity | 5 | Needs some preparation |
| Tooling Availability | 4 | Tools need adaptation |
| Skill Level | 4 | Intermediate skill |

#### Scalability

**Score**: 9.3 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 10 | Fully automatable |
| Target Scope | 9 | Every instance |
| Resource Requirements | 9 | Minimal resources |
| Detection Difficulty | 9 | Blends with normal use |

#### Reachability

**Score**: 6.5 | **Trust Zone**: Edge DMZ (Semi-trusted)

edge-gateway sits in the Edge DMZ. The zone baseline is 6.5 and the refinement for this finding gives 6.5.

---

### I-1 — edge-gateway

**Threat**: Secrets such as the bearer token for edge-gateway appear in process arguments and environment dumps that diagnostic tooling captures.

**Category**: info-disclosure | **Original Risk Level**: High | **Composite**: 6.4 (Medium)

#### CVSS 3.1 Base

**Score**: 7.5 | **Vector**: `CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Network | Reachable over the network |
| Attack Complexity (AC) | Low | No special conditions |
| Privileges Required (PR) | None | No privileges needed |
| User Interaction (UI) | None | No user action needed |
| Scope (S) | Unchanged | Impact stays in the component |
| Confidentiality (C) | High | Broad disclosure |
| Integrity (I) | None | No modification |
| Availability (A) | None | No loss of service |

#### Exploitability

**Score**: 4.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 5 | Described in research |
| Attack Complexity | 5 | Needs some preparation |
| Tooling Availability | 4 | Tools need adaptation |
| Skill Level | 4 | Intermediate skill |

#### Scalability

**Score**: 8.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 9 | Fully automatable |
| Target Scope | 9 | Every instance |
| Resource Requirements | 8 | Minimal resources |
| Detection Difficulty | 8 | Blends with normal use |

#### Reachability

**Score**: 6.0 | **Trust Zone**: Edge DMZ (Semi-trusted)

edge-gateway sits in the Edge DMZ. The zone baseline is 6.5 and the refinement for this finding gives 6.0.

---

### R-1 — edge-gateway

**Threat**: Log entries from edge-gateway can be edited or deleted by the same operators who administer it, so evidence of misuse can be removed after the fact.

**Category**: repudiation | **Original Risk Level**: Low | **Composite**: 4.4 (Medium)

#### CVSS 3.1 Base

**Score**: 4.3 | **Vector**: `CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:L/A:N`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Network | Reachable over the network |
| Attack Complexity (AC) | Low | No special conditions |
| Privileges Required (PR) | None | No privileges needed |
| User Interaction (UI) | Required | A user must act |
| Scope (S) | Unchanged | Impact stays in the component |
| Confidentiality (C) | None | No disclosure |
| Integrity (I) | Low | Limited modification |
| Availability (A) | None | No loss of service |

#### Exploitability

**Score**: 5.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 5 | Described in research |
| Attack Complexity | 5 | Needs some preparation |
| Tooling Availability | 5 | Tools need adaptation |
| Skill Level | 5 | Intermediate skill |

#### Scalability

**Score**: 4.3 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 5 | Partly automatable |
| Target Scope | 4 | A class of targets |
| Resource Requirements | 4 | Moderate resources |
| Detection Difficulty | 4 | Detectable with monitoring |

#### Reachability

**Score**: 4.0 | **Trust Zone**: Edge DMZ (Semi-trusted)

edge-gateway sits in the Edge DMZ. The zone baseline is 6.5 and the refinement for this finding gives 4.0.

---

### AG-1 — intake-agent

**Threat**: Memory written by intake-agent is trusted on later runs, so one poisoned entry changes the behaviour of every future task.

**Category**: agentic | **Original Risk Level**: High | **Composite**: 4.0 (Medium)

#### CVSS 3.1 Base

**Score**: 5.5 | **Vector**: `CVSS:3.1/AV:N/AC:H/PR:H/UI:N/S:U/C:L/I:L/A:H`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Network | Reachable over the network |
| Attack Complexity (AC) | High | Needs specific conditions |
| Privileges Required (PR) | High | Administrative rights are needed |
| User Interaction (UI) | None | No user action needed |
| Scope (S) | Unchanged | Impact stays in the component |
| Confidentiality (C) | Low | Limited disclosure |
| Integrity (I) | Low | Limited modification |
| Availability (A) | High | Loss of service |

#### Exploitability

**Score**: 4.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 4 | Described in research |
| Attack Complexity | 4 | Needs some preparation |
| Tooling Availability | 4 | Tools need adaptation |
| Skill Level | 4 | Intermediate skill |

#### Scalability

**Score**: 4.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 5 | Partly automatable |
| Target Scope | 5 | A class of targets |
| Resource Requirements | 4 | Moderate resources |
| Detection Difficulty | 4 | Detectable with monitoring |

#### Reachability

**Score**: 1.0 | **Trust Zone**: Agent Runtime Zone (Trusted)

intake-agent sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 1.0.

---

### MI-1 — intake-agent

**Threat**: intake-agent fabricates reference numbers and clause citations that look real, which operators then paste into official documents.

**Category**: llm | **Original Risk Level**: Critical | **Composite**: 3.9 (Low)

#### CVSS 3.1 Base

**Score**: 5.1 | **Vector**: `CVSS:3.1/AV:A/AC:H/PR:L/UI:R/S:U/C:L/I:H/A:N`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Adjacent | Needs an adjacent network |
| Attack Complexity (AC) | High | Needs specific conditions |
| Privileges Required (PR) | Low | A basic account is needed |
| User Interaction (UI) | Required | A user must act |
| Scope (S) | Unchanged | Impact stays in the component |
| Confidentiality (C) | Low | Limited disclosure |
| Integrity (I) | High | Broad modification |
| Availability (A) | None | No loss of service |

#### Exploitability

**Score**: 4.8 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 5 | Described in research |
| Attack Complexity | 5 | Needs some preparation |
| Tooling Availability | 5 | Tools need adaptation |
| Skill Level | 4 | Intermediate skill |

#### Scalability

**Score**: 3.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 4 | Partly automatable |
| Target Scope | 4 | A class of targets |
| Resource Requirements | 3 | Needs heavy infrastructure |
| Detection Difficulty | 3 | Readily detected |

#### Reachability

**Score**: 1.0 | **Trust Zone**: Agent Runtime Zone (Trusted)

intake-agent sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 1.0.

---

## 4. Governance Fields

Remediation tracking metadata for each scored finding. Defaults are severity-driven and intended for manual override during risk review.

| ID | Severity | Owner | SLA | Disposition | Review Date |
|----|----------|-------|-----|-------------|-------------|
| E-1 | Critical | Unassigned | 24h | Mitigate | 2026-11-10 |
| T-1 | High | Unassigned | 7d | Mitigate | 2026-11-16 |
| LLM-1 | High | Unassigned | 7d | Mitigate | 2026-11-16 |
| D-1 | High | Unassigned | 7d | Mitigate | 2026-11-16 |
| S-1 | Medium | Unassigned | 30d | Review | 2026-12-09 |
| I-1 | Medium | Unassigned | 30d | Review | 2026-12-09 |
| R-1 | Medium | Unassigned | 30d | Review | 2026-12-09 |
| AG-1 | Medium | Unassigned | 30d | Review | 2026-12-09 |
| MI-1 | Low | Unassigned | 90d | Review | 2027-02-07 |

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
