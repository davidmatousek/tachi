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

**9** threats scored | **0** Critical | **5** High | **4** Medium | **0** Low

**Highest-Risk Component**: client-portal — 1 finding(s), max composite 8.1

| Metric | Value |
|--------|-------|
| Scoring date | 2026-11-09 |
| Source file | `baseline/threats.md` |
| Schema version | 1.0 |

**Severity Distribution:**

| Severity | Count | Percentage |
|----------|-------|------------|
| Critical | 0 | 0.0% |
| High | 5 | 55.6% |
| Medium | 4 | 44.4% |
| Low | 0 | 0.0% |
| **Total** | **9** | **100%** |

> Trust zone data was available for every component, so no reachability value was defaulted.

---

## 2. Scored Threat Table

Findings sorted by Composite score descending (highest risk first). Boundary values map to the higher severity band.

| ID | Source | Component | Threat | CVSS | Exploit. | Scale. | Reach. | Composite | Severity | SLA | Disposition |
|----|--------|-----------|--------|------|----------|--------|--------|-----------|----------|-----|-------------|
| S-1 | fresh | client-portal | An attacker replays a captured session cookie against... | 7.3 | 8.0 | 8.0 | 9.5 | 8.1 | High | 7d | Mitigate |
| S-2 | fresh | auth-broker | A shared or long-lived refresh token on auth-broker lets... | 7.5 | 8.5 | 8.0 | 7.0 | 7.8 | High | 7d | Mitigate |
| I-1 | fresh | edge-gateway | Secrets such as the bearer token for edge-gateway appear in... | 4.6 | 9.0 | 9.0 | 7.0 | 7.1 | High | 7d | Mitigate |
| E-1 | fresh | edge-gateway | Object identifiers in requests to edge-gateway are trusted... | 9.6 | 4.3 | 8.8 | 5.5 | 7.1 | High | 7d | Mitigate |
| LLM-1 | fresh | edge-gateway | edge-gateway passes conversation history from earlier turns... | 4.6 | 9.0 | 9.0 | 7.0 | 7.1 | High | 7d | Mitigate |
| T-1 | fresh | edge-gateway | An attacker who can write to the channel between auth-broker... | 5.4 | 8.5 | 7.0 | 5.5 | 6.6 | Medium | 30d | Review |
| T-2 | fresh | vector-store-a | Serialised objects arriving from worker-2 are deserialised... | 5.5 | 5.5 | 3.5 | 1.5 | 4.4 | Medium | 30d | Review |
| R-1 | fresh | intake-agent | Clock drift between intake-agent and edge-gateway leaves... | 3.7 | 5.0 | 4.5 | 3.0 | 4.1 | Medium | 30d | Review |
| AG-1 | fresh | intake-agent | Memory written by intake-agent is trusted on later runs, so... | 3.7 | 5.0 | 4.5 | 3.0 | 4.1 | Medium | 30d | Review |

> **Correlated findings**: for correlation groups (Section 4a of the source threat model), the primary finding is scored independently. Correlated peer findings inherit the primary's scores to keep the group consistent.

---

## 3. Dimensional Breakdown

Per-finding detail showing the scoring rationale for each dimension, in the order of Section 2.

### S-1 — client-portal

**Threat**: An attacker replays a captured session cookie against client-portal, which does not bind the credential to the session or channel it was issued for, so the replay is accepted as the original caller.

**Category**: spoofing | **Original Risk Level**: High | **Composite**: 8.1 (High)

#### CVSS 3.1 Base

**Score**: 7.3 | **Vector**: `CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Network | Reachable over the network |
| Attack Complexity (AC) | Low | No special conditions |
| Privileges Required (PR) | None | No privileges needed |
| User Interaction (UI) | None | No user action needed |
| Scope (S) | Unchanged | Impact stays in the component |
| Confidentiality (C) | Low | Limited disclosure |
| Integrity (I) | Low | Limited modification |
| Availability (A) | Low | Degraded service |

#### Exploitability

**Score**: 8.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 8 | Documented and widely used |
| Attack Complexity | 7 | A single step suffices |
| Tooling Availability | 10 | Common tools apply |
| Skill Level | 7 | Little skill needed |

#### Scalability

**Score**: 8.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 10 | Fully automatable |
| Target Scope | 6 | A class of targets |
| Resource Requirements | 10 | Minimal resources |
| Detection Difficulty | 6 | Detectable with monitoring |

#### Reachability

**Score**: 9.5 | **Trust Zone**: Public Internet (Untrusted)

client-portal sits in the Public Internet. The zone baseline is 9.0 and the refinement for this finding gives 9.5.

---

### S-2 — auth-broker

**Threat**: A shared or long-lived refresh token on auth-broker lets anyone who obtains one copy authenticate as every tenant that uses the same deployment profile.

**Category**: spoofing | **Original Risk Level**: Note | **Composite**: 7.8 (High)

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

**Score**: 8.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 10 | Documented and widely used |
| Attack Complexity | 7 | A single step suffices |
| Tooling Availability | 9 | Common tools apply |
| Skill Level | 8 | Little skill needed |

#### Scalability

**Score**: 8.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 9 | Fully automatable |
| Target Scope | 6 | A class of targets |
| Resource Requirements | 10 | Minimal resources |
| Detection Difficulty | 7 | Blends with normal use |

#### Reachability

**Score**: 7.0 | **Trust Zone**: Edge DMZ (Semi-trusted)

auth-broker sits in the Edge DMZ. The zone baseline is 6.5 and the refinement for this finding gives 7.0.

---

### I-1 — edge-gateway

**Threat**: Secrets such as the bearer token for edge-gateway appear in process arguments and environment dumps that diagnostic tooling captures.

**Category**: info-disclosure | **Original Risk Level**: Low | **Composite**: 7.1 (High)

#### CVSS 3.1 Base

**Score**: 4.6 | **Vector**: `CVSS:3.1/AV:A/AC:H/PR:L/UI:N/S:U/C:L/I:L/A:L`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Adjacent | Needs an adjacent network |
| Attack Complexity (AC) | High | Needs specific conditions |
| Privileges Required (PR) | Low | A basic account is needed |
| User Interaction (UI) | None | No user action needed |
| Scope (S) | Unchanged | Impact stays in the component |
| Confidentiality (C) | Low | Limited disclosure |
| Integrity (I) | Low | Limited modification |
| Availability (A) | Low | Degraded service |

#### Exploitability

**Score**: 9.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 9 | Documented and widely used |
| Attack Complexity | 9 | A single step suffices |
| Tooling Availability | 9 | Common tools apply |
| Skill Level | 9 | Little skill needed |

#### Scalability

**Score**: 9.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 9 | Fully automatable |
| Target Scope | 9 | Every instance |
| Resource Requirements | 9 | Minimal resources |
| Detection Difficulty | 9 | Blends with normal use |

#### Reachability

**Score**: 7.0 | **Trust Zone**: Edge DMZ (Semi-trusted)

edge-gateway sits in the Edge DMZ. The zone baseline is 6.5 and the refinement for this finding gives 7.0.

---

### E-1 — edge-gateway

**Threat**: Object identifiers in requests to edge-gateway are trusted without an ownership check, so a caller can read or change inbound API requests that belong to others.

**Category**: privilege-escalation | **Original Risk Level**: High | **Composite**: 7.1 (High)

#### CVSS 3.1 Base

**Score**: 9.6 | **Vector**: `CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:C/C:H/I:L/A:H`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Adjacent | Needs an adjacent network |
| Attack Complexity (AC) | Low | No special conditions |
| Privileges Required (PR) | None | No privileges needed |
| User Interaction (UI) | None | No user action needed |
| Scope (S) | Changed | Impact crosses a boundary |
| Confidentiality (C) | High | Broad disclosure |
| Integrity (I) | Low | Limited modification |
| Availability (A) | High | Loss of service |

#### Exploitability

**Score**: 4.3 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 5 | Described in research |
| Attack Complexity | 4 | Needs some preparation |
| Tooling Availability | 4 | Tools need adaptation |
| Skill Level | 4 | Intermediate skill |

#### Scalability

**Score**: 8.8 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 9 | Fully automatable |
| Target Scope | 9 | Every instance |
| Resource Requirements | 9 | Minimal resources |
| Detection Difficulty | 8 | Blends with normal use |

#### Reachability

**Score**: 5.5 | **Trust Zone**: Edge DMZ (Semi-trusted)

edge-gateway sits in the Edge DMZ. The zone baseline is 6.5 and the refinement for this finding gives 5.5.

---

### LLM-1 — edge-gateway

**Threat**: edge-gateway passes conversation history from earlier turns into the model unchanged, so an injection planted earlier keeps working in later turns.

**Category**: llm | **Original Risk Level**: Medium | **Composite**: 7.1 (High)

**Correlation Group**: Scores inherited from primary finding I-1 (CG-1). Dimensional detail is recorded on the primary.

**Score**: 4.6 | **Vector**: `CVSS:3.1/AV:A/AC:H/PR:L/UI:N/S:U/C:L/I:L/A:L`

---

### T-1 — edge-gateway

**Threat**: An attacker who can write to the channel between auth-broker and edge-gateway modifies inbound API requests in transit because messages carry no integrity protection of their own.

**Category**: tampering | **Original Risk Level**: Medium | **Composite**: 6.6 (Medium)

#### CVSS 3.1 Base

**Score**: 5.4 | **Vector**: `CVSS:3.1/AV:A/AC:L/PR:L/UI:N/S:C/C:L/I:L/A:N`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Adjacent | Needs an adjacent network |
| Attack Complexity (AC) | Low | No special conditions |
| Privileges Required (PR) | Low | A basic account is needed |
| User Interaction (UI) | None | No user action needed |
| Scope (S) | Changed | Impact crosses a boundary |
| Confidentiality (C) | Low | Limited disclosure |
| Integrity (I) | Low | Limited modification |
| Availability (A) | None | No loss of service |

#### Exploitability

**Score**: 8.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 9 | Documented and widely used |
| Attack Complexity | 9 | A single step suffices |
| Tooling Availability | 8 | Common tools apply |
| Skill Level | 8 | Little skill needed |

#### Scalability

**Score**: 7.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 7 | Fully automatable |
| Target Scope | 7 | Every instance |
| Resource Requirements | 7 | Minimal resources |
| Detection Difficulty | 7 | Blends with normal use |

#### Reachability

**Score**: 5.5 | **Trust Zone**: Edge DMZ (Semi-trusted)

edge-gateway sits in the Edge DMZ. The zone baseline is 6.5 and the refinement for this finding gives 5.5.

---

### T-2 — vector-store-a

**Threat**: Serialised objects arriving from worker-2 are deserialised by vector-store-a with permissive type handling, allowing crafted payloads to instantiate unintended behaviour.

**Category**: tampering | **Original Risk Level**: Low | **Composite**: 4.4 (Medium)

#### CVSS 3.1 Base

**Score**: 5.5 | **Vector**: `CVSS:3.1/AV:A/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:L`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Adjacent | Needs an adjacent network |
| Attack Complexity (AC) | Low | No special conditions |
| Privileges Required (PR) | Low | A basic account is needed |
| User Interaction (UI) | None | No user action needed |
| Scope (S) | Unchanged | Impact stays in the component |
| Confidentiality (C) | Low | Limited disclosure |
| Integrity (I) | Low | Limited modification |
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

**Score**: 3.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 3 | Manual for each target |
| Target Scope | 3 | One specific target |
| Resource Requirements | 6 | Moderate resources |
| Detection Difficulty | 2 | Readily detected |

#### Reachability

**Score**: 1.5 | **Trust Zone**: Data Zone (Trusted)

vector-store-a sits in the Data Zone. The zone baseline is 2.5 and the refinement for this finding gives 1.5.

---

### R-1 — intake-agent

**Threat**: Clock drift between intake-agent and edge-gateway leaves events in inconsistent order, so the sequence of actions on free-text shipment requests cannot be reconstructed reliably.

**Category**: repudiation | **Original Risk Level**: Medium | **Composite**: 4.1 (Medium)

#### CVSS 3.1 Base

**Score**: 3.7 | **Vector**: `CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:L/A:N`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Network | Reachable over the network |
| Attack Complexity (AC) | High | Needs specific conditions |
| Privileges Required (PR) | None | No privileges needed |
| User Interaction (UI) | None | No user action needed |
| Scope (S) | Unchanged | Impact stays in the component |
| Confidentiality (C) | None | No disclosure |
| Integrity (I) | Low | Limited modification |
| Availability (A) | None | No loss of service |

#### Exploitability

**Score**: 5.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 5 | Described in research |
| Attack Complexity | 6 | Needs some preparation |
| Tooling Availability | 4 | Tools need adaptation |
| Skill Level | 5 | Intermediate skill |

#### Scalability

**Score**: 4.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 4 | Partly automatable |
| Target Scope | 2 | One specific target |
| Resource Requirements | 7 | Minimal resources |
| Detection Difficulty | 5 | Detectable with monitoring |

#### Reachability

**Score**: 3.0 | **Trust Zone**: Agent Runtime Zone (Trusted)

intake-agent sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 3.0.

---

### AG-1 — intake-agent

**Threat**: Memory written by intake-agent is trusted on later runs, so one poisoned entry changes the behaviour of every future task.

**Category**: agentic | **Original Risk Level**: Critical | **Composite**: 4.1 (Medium)

**Correlation Group**: Scores inherited from primary finding R-1 (CG-2). Dimensional detail is recorded on the primary.

**Score**: 3.7 | **Vector**: `CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:L/A:N`

---

## 4. Governance Fields

Remediation tracking metadata for each scored finding. Defaults are severity-driven and intended for manual override during risk review.

| ID | Severity | Owner | SLA | Disposition | Review Date |
|----|----------|-------|-----|-------------|-------------|
| S-1 | High | Unassigned | 7d | Mitigate | 2026-11-16 |
| S-2 | High | Unassigned | 7d | Mitigate | 2026-11-16 |
| I-1 | High | Unassigned | 7d | Mitigate | 2026-11-16 |
| E-1 | High | appsec-team | 7d | Mitigate | 2026-11-16 |
| LLM-1 | High | Unassigned | 7d | Mitigate | 2026-11-16 |
| T-1 | Medium | Unassigned | 30d | Review | 2026-12-09 |
| T-2 | Medium | Unassigned | 30d | Review | 2026-12-09 |
| R-1 | Medium | Unassigned | 30d | Review | 2026-12-09 |
| AG-1 | Medium | Unassigned | 30d | Review | 2026-12-09 |

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
