---
schema_version: "1.0"
date: "2026-10-20"
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

**42** threats scored | **0** Critical | **6** High | **35** Medium | **1** Low

**Highest-Risk Component**: edge-gateway — 6 finding(s), max composite 8.0

| Metric | Value |
|--------|-------|
| Scoring date | 2026-10-20 |
| Source file | `baseline/threats.md` |
| Schema version | 1.0 |

**Severity Distribution:**

| Severity | Count | Percentage |
|----------|-------|------------|
| Critical | 0 | 0.0% |
| High | 6 | 14.3% |
| Medium | 35 | 83.3% |
| Low | 1 | 2.4% |
| **Total** | **42** | **100%** |

> Trust zone data was available for every component, so no reachability value was defaulted.

---

## 2. Scored Threat Table

Findings sorted by Composite score descending (highest risk first). Boundary values map to the higher severity band.

| ID | Source | Component | Threat | CVSS | Exploit. | Scale. | Reach. | Composite | Severity | SLA | Disposition |
|----|--------|-----------|--------|------|----------|--------|--------|-----------|----------|-----|-------------|
| E-1 | fresh | edge-gateway | Object identifiers in requests to edge-gateway are trusted... | 9.1 | 7.0 | 8.5 | 7.0 | 8.0 | High | 7d | Mitigate |
| S-3 | fresh | auth-broker | A shared or long-lived refresh token on auth-broker lets... | 8.2 | 8.0 | 8.5 | 7.0 | 7.9 | High | 7d | Mitigate |
| S-1 | fresh | edge-gateway | A shared or long-lived bearer token on edge-gateway lets... | 7.1 | 8.5 | 8.5 | 6.5 | 7.6 | High | 7d | Mitigate |
| D-1 | fresh | edge-gateway | A dependency of edge-gateway becomes unavailable and the... | 5.9 | 9.0 | 8.5 | 6.5 | 7.3 | High | 7d | Mitigate |
| OI-1 | fresh | intake-agent | intake-agent emits URLs that downstream services fetch, so... | 9.9 | 7.0 | 6.5 | 3.0 | 7.1 | High | 7d | Mitigate |
| OI-2 | fresh | intake-agent | Structured output from intake-agent is trusted by... | 8.2 | 8.5 | 6.5 | 3.5 | 7.1 | High | 7d | Mitigate |
| I-1 | fresh | edge-gateway | Secrets such as the bearer token for edge-gateway appear in... | 5.4 | 8.0 | 8.0 | 7.0 | 6.9 | Medium | 30d | Review |
| LLM-1 | fresh | edge-gateway | edge-gateway passes conversation history from earlier turns... | 5.4 | 8.0 | 8.0 | 7.0 | 6.9 | Medium | 30d | Review |
| LLM-2 | fresh | edge-gateway | Prompt content logged by auth-broker is later replayed to... | 5.4 | 8.0 | 8.0 | 7.0 | 6.9 | Medium | 30d | Review |
| LLM-3 | fresh | intake-agent | Encoded or multilingual payloads bypass the keyword filter... | 9.3 | 7.5 | 5.5 | 3.0 | 6.9 | Medium | 30d | Review |
| MI-2 | fresh | intake-agent | Stale data in the knowledge base lets intake-agent present... | 9.3 | 7.0 | 6.0 | 2.5 | 6.8 | Medium | 30d | Review |
| T-4 | fresh | auth-broker | Unsanitised credential assertions and session grants reach... | 6.5 | 7.0 | 7.0 | 6.5 | 6.7 | Medium | 30d | Review |
| S-5 | fresh | tool-server-1 | An unauthenticated callback or health route on tool-server-1... | 8.2 | 7.0 | 6.0 | 3.5 | 6.6 | Medium | 30d | Review |
| LLM-4 | fresh | tool-server-1 | Encoded or multilingual payloads bypass the keyword filter... | 8.5 | 7.5 | 6.5 | 2.0 | 6.6 | Medium | 30d | Review |
| MI-1 | fresh | intake-agent | intake-agent fabricates reference numbers and clause... | 8.0 | 7.5 | 5.5 | 3.5 | 6.6 | Medium | 30d | Review |
| AG-4 | fresh | tool-server-1 | tool-server-1 retries failed actions on its own, repeating... | 9.1 | 5.5 | 5.0 | 3.5 | 6.3 | Medium | 30d | Review |
| AG-6 | fresh | planner-agent | planner-agent does not limit the rate or total number of... | 9.6 | 5.0 | 5.5 | 3.0 | 6.3 | Medium | 30d | Review |
| OI-3 | fresh | worker-2 | Markdown or HTML produced by worker-2 contains remote images... | 7.6 | 7.5 | 7.5 | 1.5 | 6.3 | Medium | 30d | Review |
| TE-2 | fresh | intake-agent | Persuasive phrasing from intake-agent pushes operators to... | 8.9 | 5.5 | 6.0 | 2.5 | 6.2 | Medium | 30d | Review |
| D-2 | fresh | intake-agent | A single oversized or deeply nested payload makes... | 7.5 | 7.0 | 5.0 | 3.0 | 6.1 | Medium | 30d | Review |
| T-1 | fresh | auth-broker | Backups and exports of credential assertions and session... | 4.2 | 7.0 | 8.0 | 6.0 | 6.0 | Medium | 30d | Review |
| AG-5 | fresh | tool-server-1 | tool-server-1 invokes tools with arguments assembled from... | 10.0 | 4.0 | 5.5 | 2.5 | 6.0 | Medium | 30d | Review |
| AGP-01 | fresh | worker-2 | Worker agents coordinate through the shared message bus and... | 9.9 | 4.5 | 5.0 | 2.0 | 6.0 | Medium | 30d | Review |
| S-4 | fresh | tool-server-1 | A shared or long-lived tool API key on tool-server-1 lets... | 7.0 | 6.5 | 6.0 | 3.0 | 5.9 | Medium | 30d | Review |
| I-5 | fresh | vector-store-a | embedded documents and metadata held by vector-store-a are... | 6.5 | 6.5 | 6.0 | 3.0 | 5.7 | Medium | 30d | Review |
| E-3 | fresh | planner-agent | planner-agent runs with broader permissions than its... | 8.4 | 5.5 | 5.0 | 2.0 | 5.7 | Medium | 30d | Review |
| AG-2 | fresh | planner-agent | planner-agent runs without a budget on steps or spend, so a... | 8.4 | 5.5 | 5.0 | 2.0 | 5.7 | Medium | 30d | Review |
| I-4 | fresh | model-gateway | Cross-tenant filters on model-gateway are applied in... | 5.9 | 5.5 | 7.0 | 3.0 | 5.4 | Medium | 30d | Review |
| LLM-5 | fresh | model-gateway | Indirect injection through documents retrieved for... | 5.9 | 5.5 | 7.0 | 3.0 | 5.4 | Medium | 30d | Review |
| D-3 | fresh | vector-store-a | Retry storms from worker-2 multiply the load on... | 5.3 | 6.5 | 6.0 | 3.0 | 5.3 | Medium | 30d | Review |
| T-2 | fresh | vector-store-a | Serialised objects arriving from worker-2 are deserialised... | 6.4 | 5.0 | 5.5 | 2.0 | 5.0 | Medium | 30d | Review |
| R-3 | fresh | tool-server-1 | Operators approve changes to tool call arguments and results... | 6.5 | 4.0 | 5.5 | 3.5 | 5.0 | Medium | 30d | Review |
| AG-3 | fresh | tool-server-1 | Memory written by tool-server-1 is trusted on later runs, so... | 6.5 | 4.0 | 5.5 | 3.5 | 5.0 | Medium | 30d | Review |
| LLM-6 | fresh | vector-store-a | Anyone who can write to the ingestion path of vector-store-a... | 6.4 | 5.0 | 5.5 | 2.0 | 5.0 | Medium | 30d | Review |
| I-3 | fresh | worker-2 | Logs and traces emitted by worker-2 include raw work orders... | 4.3 | 6.0 | 5.5 | 3.5 | 4.8 | Medium | 30d | Review |
| LLM-7 | fresh | worker-2 | worker-2 follows links and files named in work orders and... | 4.3 | 6.0 | 5.5 | 3.5 | 4.8 | Medium | 30d | Review |
| R-1 | fresh | intake-agent | Clock drift between intake-agent and edge-gateway leaves... | 6.8 | 3.0 | 6.0 | 2.0 | 4.6 | Medium | 30d | Review |
| E-2 | fresh | intake-agent | Role claims carried in the service token presented to... | 6.8 | 3.0 | 6.0 | 2.0 | 4.6 | Medium | 30d | Review |
| AG-1 | fresh | intake-agent | Memory written by intake-agent is trusted on later runs, so... | 6.8 | 3.0 | 6.0 | 2.0 | 4.6 | Medium | 30d | Review |
| TE-1 | fresh | intake-agent | intake-agent adopts a persona that presents itself as a... | 4.9 | 5.0 | 5.5 | 2.0 | 4.4 | Medium | 30d | Review |
| T-3 | fresh | audit-ledger | An attacker who can write to the channel between... | 5.0 | 5.0 | 3.5 | 2.0 | 4.2 | Medium | 30d | Review |
| R-4 | fresh | tool-server-1 | Actions taken through tool-server-1 are logged without the... | 5.3 | 3.0 | 3.5 | 2.0 | 3.7 | Low | 90d | Review |

> **Correlated findings**: for correlation groups (Section 4a of the source threat model), the primary finding is scored independently. Correlated peer findings inherit the primary's scores to keep the group consistent.

---

## 3. Dimensional Breakdown

Per-finding detail showing the scoring rationale for each dimension, in the order of Section 2.

### E-1 — edge-gateway

**Threat**: Object identifiers in requests to edge-gateway are trusted without an ownership check, so a caller can read or change inbound API requests that belong to others.

**Category**: privilege-escalation | **Original Risk Level**: High | **Composite**: 8.0 (High)

#### CVSS 3.1 Base

**Score**: 9.1 | **Vector**: `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:L/I:H/A:L`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Network | Reachable over the network |
| Attack Complexity (AC) | Low | No special conditions |
| Privileges Required (PR) | Low | A basic account is needed |
| User Interaction (UI) | None | No user action needed |
| Scope (S) | Changed | Impact crosses a boundary |
| Confidentiality (C) | Low | Limited disclosure |
| Integrity (I) | High | Broad modification |
| Availability (A) | Low | Degraded service |

#### Exploitability

**Score**: 7.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 9 | Documented and widely used |
| Attack Complexity | 6 | Needs some preparation |
| Tooling Availability | 5 | Tools need adaptation |
| Skill Level | 8 | Little skill needed |

#### Scalability

**Score**: 8.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 8 | Fully automatable |
| Target Scope | 8 | Every instance |
| Resource Requirements | 10 | Minimal resources |
| Detection Difficulty | 8 | Blends with normal use |

#### Reachability

**Score**: 7.0 | **Trust Zone**: Edge DMZ (Semi-trusted)

edge-gateway sits in the Edge DMZ. The zone baseline is 6.5 and the refinement for this finding gives 7.0.

---

### S-3 — auth-broker

**Threat**: A shared or long-lived refresh token on auth-broker lets anyone who obtains one copy authenticate as every tenant that uses the same deployment profile.

**Category**: spoofing | **Original Risk Level**: Medium | **Composite**: 7.9 (High)

#### CVSS 3.1 Base

**Score**: 8.2 | **Vector**: `CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:L/A:N`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Network | Reachable over the network |
| Attack Complexity (AC) | Low | No special conditions |
| Privileges Required (PR) | None | No privileges needed |
| User Interaction (UI) | None | No user action needed |
| Scope (S) | Unchanged | Impact stays in the component |
| Confidentiality (C) | High | Broad disclosure |
| Integrity (I) | Low | Limited modification |
| Availability (A) | None | No loss of service |

#### Exploitability

**Score**: 8.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 8 | Documented and widely used |
| Attack Complexity | 7 | A single step suffices |
| Tooling Availability | 9 | Common tools apply |
| Skill Level | 8 | Little skill needed |

#### Scalability

**Score**: 8.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 9 | Fully automatable |
| Target Scope | 7 | Every instance |
| Resource Requirements | 10 | Minimal resources |
| Detection Difficulty | 8 | Blends with normal use |

#### Reachability

**Score**: 7.0 | **Trust Zone**: Edge DMZ (Semi-trusted)

auth-broker sits in the Edge DMZ. The zone baseline is 6.5 and the refinement for this finding gives 7.0.

---

### S-1 — edge-gateway

**Threat**: A shared or long-lived bearer token on edge-gateway lets anyone who obtains one copy authenticate as every tenant that uses the same deployment profile.

**Category**: spoofing | **Original Risk Level**: Low | **Composite**: 7.6 (High)

#### CVSS 3.1 Base

**Score**: 7.1 | **Vector**: `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:L/A:N`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Network | Reachable over the network |
| Attack Complexity (AC) | Low | No special conditions |
| Privileges Required (PR) | Low | A basic account is needed |
| User Interaction (UI) | None | No user action needed |
| Scope (S) | Unchanged | Impact stays in the component |
| Confidentiality (C) | High | Broad disclosure |
| Integrity (I) | Low | Limited modification |
| Availability (A) | None | No loss of service |

#### Exploitability

**Score**: 8.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 9 | Documented and widely used |
| Attack Complexity | 10 | A single step suffices |
| Tooling Availability | 7 | Common tools apply |
| Skill Level | 8 | Little skill needed |

#### Scalability

**Score**: 8.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 10 | Fully automatable |
| Target Scope | 7 | Every instance |
| Resource Requirements | 8 | Minimal resources |
| Detection Difficulty | 9 | Blends with normal use |

#### Reachability

**Score**: 6.5 | **Trust Zone**: Edge DMZ (Semi-trusted)

edge-gateway sits in the Edge DMZ. The zone baseline is 6.5 and the refinement for this finding gives 6.5.

---

### D-1 — edge-gateway

**Threat**: A dependency of edge-gateway becomes unavailable and the failure cascades because edge-gateway waits on it synchronously for every request.

**Category**: denial-of-service | **Original Risk Level**: Medium | **Composite**: 7.3 (High)

#### CVSS 3.1 Base

**Score**: 5.9 | **Vector**: `CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Network | Reachable over the network |
| Attack Complexity (AC) | High | Needs specific conditions |
| Privileges Required (PR) | None | No privileges needed |
| User Interaction (UI) | None | No user action needed |
| Scope (S) | Unchanged | Impact stays in the component |
| Confidentiality (C) | None | No disclosure |
| Integrity (I) | None | No modification |
| Availability (A) | High | Loss of service |

#### Exploitability

**Score**: 9.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 8 | Documented and widely used |
| Attack Complexity | 8 | A single step suffices |
| Tooling Availability | 10 | Common tools apply |
| Skill Level | 10 | Little skill needed |

#### Scalability

**Score**: 8.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 10 | Fully automatable |
| Target Scope | 10 | Every instance |
| Resource Requirements | 8 | Minimal resources |
| Detection Difficulty | 6 | Detectable with monitoring |

#### Reachability

**Score**: 6.5 | **Trust Zone**: Edge DMZ (Semi-trusted)

edge-gateway sits in the Edge DMZ. The zone baseline is 6.5 and the refinement for this finding gives 6.5.

---

### OI-1 — intake-agent

**Threat**: intake-agent emits URLs that downstream services fetch, so an attacker can make internal addresses part of the output and trigger server-side requests.

**Category**: llm | **Original Risk Level**: Low | **Composite**: 7.1 (High)

#### CVSS 3.1 Base

**Score**: 9.9 | **Vector**: `CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:L/I:H/A:L`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Network | Reachable over the network |
| Attack Complexity (AC) | Low | No special conditions |
| Privileges Required (PR) | None | No privileges needed |
| User Interaction (UI) | None | No user action needed |
| Scope (S) | Changed | Impact crosses a boundary |
| Confidentiality (C) | Low | Limited disclosure |
| Integrity (I) | High | Broad modification |
| Availability (A) | Low | Degraded service |

#### Exploitability

**Score**: 7.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 6 | Described in research |
| Attack Complexity | 7 | A single step suffices |
| Tooling Availability | 7 | Common tools apply |
| Skill Level | 8 | Little skill needed |

#### Scalability

**Score**: 6.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 5 | Partly automatable |
| Target Scope | 6 | A class of targets |
| Resource Requirements | 8 | Minimal resources |
| Detection Difficulty | 7 | Blends with normal use |

#### Reachability

**Score**: 3.0 | **Trust Zone**: Agent Runtime Zone (Trusted)

intake-agent sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 3.0.

---

### OI-2 — intake-agent

**Threat**: Structured output from intake-agent is trusted by edge-gateway as already validated, so a malformed field flows straight into business logic.

**Category**: llm | **Original Risk Level**: Medium | **Composite**: 7.1 (High)

#### CVSS 3.1 Base

**Score**: 8.2 | **Vector**: `CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:H/A:N`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Network | Reachable over the network |
| Attack Complexity (AC) | Low | No special conditions |
| Privileges Required (PR) | None | No privileges needed |
| User Interaction (UI) | Required | A user must act |
| Scope (S) | Changed | Impact crosses a boundary |
| Confidentiality (C) | Low | Limited disclosure |
| Integrity (I) | High | Broad modification |
| Availability (A) | None | No loss of service |

#### Exploitability

**Score**: 8.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 7 | Documented and widely used |
| Attack Complexity | 9 | A single step suffices |
| Tooling Availability | 8 | Common tools apply |
| Skill Level | 10 | Little skill needed |

#### Scalability

**Score**: 6.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 8 | Fully automatable |
| Target Scope | 7 | Every instance |
| Resource Requirements | 7 | Minimal resources |
| Detection Difficulty | 4 | Detectable with monitoring |

#### Reachability

**Score**: 3.5 | **Trust Zone**: Agent Runtime Zone (Trusted)

intake-agent sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 3.5.

---

### I-1 — edge-gateway

**Threat**: Secrets such as the bearer token for edge-gateway appear in process arguments and environment dumps that diagnostic tooling captures.

**Category**: info-disclosure | **Original Risk Level**: High | **Composite**: 6.9 (Medium)

#### CVSS 3.1 Base

**Score**: 5.4 | **Vector**: `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:L`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Network | Reachable over the network |
| Attack Complexity (AC) | Low | No special conditions |
| Privileges Required (PR) | Low | A basic account is needed |
| User Interaction (UI) | None | No user action needed |
| Scope (S) | Unchanged | Impact stays in the component |
| Confidentiality (C) | Low | Limited disclosure |
| Integrity (I) | None | No modification |
| Availability (A) | Low | Degraded service |

#### Exploitability

**Score**: 8.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 9 | Documented and widely used |
| Attack Complexity | 7 | A single step suffices |
| Tooling Availability | 8 | Common tools apply |
| Skill Level | 8 | Little skill needed |

#### Scalability

**Score**: 8.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 9 | Fully automatable |
| Target Scope | 9 | Every instance |
| Resource Requirements | 9 | Minimal resources |
| Detection Difficulty | 5 | Detectable with monitoring |

#### Reachability

**Score**: 7.0 | **Trust Zone**: Edge DMZ (Semi-trusted)

edge-gateway sits in the Edge DMZ. The zone baseline is 6.5 and the refinement for this finding gives 7.0.

---

### LLM-1 — edge-gateway

**Threat**: edge-gateway passes conversation history from earlier turns into the model unchanged, so an injection planted earlier keeps working in later turns.

**Category**: llm | **Original Risk Level**: Critical | **Composite**: 6.9 (Medium)

**Correlation Group**: Scores inherited from primary finding I-1 (CG-1). Dimensional detail is recorded on the primary.

**Score**: 5.4 | **Vector**: `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:L`

---

### LLM-2 — edge-gateway

**Threat**: Prompt content logged by auth-broker is later replayed to edge-gateway for evaluation, carrying planted instructions into a trusted context.

**Category**: llm | **Original Risk Level**: High | **Composite**: 6.9 (Medium)

**Correlation Group**: Scores inherited from primary finding I-1 (CG-1). Dimensional detail is recorded on the primary.

**Score**: 5.4 | **Vector**: `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:L`

---

### LLM-3 — intake-agent

**Threat**: Encoded or multilingual payloads bypass the keyword filter in front of intake-agent, which only checks plain English text.

**Category**: llm | **Original Risk Level**: High | **Composite**: 6.9 (Medium)

#### CVSS 3.1 Base

**Score**: 9.3 | **Vector**: `CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:H/A:N`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Network | Reachable over the network |
| Attack Complexity (AC) | Low | No special conditions |
| Privileges Required (PR) | None | No privileges needed |
| User Interaction (UI) | Required | A user must act |
| Scope (S) | Changed | Impact crosses a boundary |
| Confidentiality (C) | High | Broad disclosure |
| Integrity (I) | High | Broad modification |
| Availability (A) | None | No loss of service |

#### Exploitability

**Score**: 7.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 6 | Described in research |
| Attack Complexity | 9 | A single step suffices |
| Tooling Availability | 6 | Tools need adaptation |
| Skill Level | 9 | Little skill needed |

#### Scalability

**Score**: 5.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 5 | Partly automatable |
| Target Scope | 5 | A class of targets |
| Resource Requirements | 7 | Minimal resources |
| Detection Difficulty | 5 | Detectable with monitoring |

#### Reachability

**Score**: 3.0 | **Trust Zone**: Agent Runtime Zone (Trusted)

intake-agent sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 3.0.

---

### MI-2 — intake-agent

**Threat**: Stale data in the knowledge base lets intake-agent present superseded tariffs as current, causing wrong quotes.

**Category**: llm | **Original Risk Level**: Low | **Composite**: 6.8 (Medium)

#### CVSS 3.1 Base

**Score**: 9.3 | **Vector**: `CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:H/A:N`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Network | Reachable over the network |
| Attack Complexity (AC) | Low | No special conditions |
| Privileges Required (PR) | None | No privileges needed |
| User Interaction (UI) | Required | A user must act |
| Scope (S) | Changed | Impact crosses a boundary |
| Confidentiality (C) | High | Broad disclosure |
| Integrity (I) | High | Broad modification |
| Availability (A) | None | No loss of service |

#### Exploitability

**Score**: 7.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 6 | Described in research |
| Attack Complexity | 7 | A single step suffices |
| Tooling Availability | 8 | Common tools apply |
| Skill Level | 7 | Little skill needed |

#### Scalability

**Score**: 6.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 6 | Partly automatable |
| Target Scope | 5 | A class of targets |
| Resource Requirements | 8 | Minimal resources |
| Detection Difficulty | 5 | Detectable with monitoring |

#### Reachability

**Score**: 2.5 | **Trust Zone**: Agent Runtime Zone (Trusted)

intake-agent sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 2.5.

---

### T-4 — auth-broker

**Threat**: Unsanitised credential assertions and session grants reach auth-broker and are processed as trusted structure, so crafted input changes how later steps interpret the record.

**Category**: tampering | **Original Risk Level**: Low | **Composite**: 6.7 (Medium)

#### CVSS 3.1 Base

**Score**: 6.5 | **Vector**: `CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:H/A:L`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Network | Reachable over the network |
| Attack Complexity (AC) | High | Needs specific conditions |
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
| Attack Complexity | 6 | Needs some preparation |
| Tooling Availability | 5 | Tools need adaptation |
| Skill Level | 9 | Little skill needed |

#### Scalability

**Score**: 7.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 8 | Fully automatable |
| Target Scope | 4 | A class of targets |
| Resource Requirements | 10 | Minimal resources |
| Detection Difficulty | 6 | Detectable with monitoring |

#### Reachability

**Score**: 6.5 | **Trust Zone**: Edge DMZ (Semi-trusted)

auth-broker sits in the Edge DMZ. The zone baseline is 6.5 and the refinement for this finding gives 6.5.

---

### S-5 — tool-server-1

**Threat**: An unauthenticated callback or health route on tool-server-1 accepts requests that downstream code treats as if they had come from audit-ledger.

**Category**: spoofing | **Original Risk Level**: Medium | **Composite**: 6.6 (Medium)

#### CVSS 3.1 Base

**Score**: 8.2 | **Vector**: `CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:L/A:N`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Network | Reachable over the network |
| Attack Complexity (AC) | Low | No special conditions |
| Privileges Required (PR) | None | No privileges needed |
| User Interaction (UI) | None | No user action needed |
| Scope (S) | Unchanged | Impact stays in the component |
| Confidentiality (C) | High | Broad disclosure |
| Integrity (I) | Low | Limited modification |
| Availability (A) | None | No loss of service |

#### Exploitability

**Score**: 7.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 8 | Documented and widely used |
| Attack Complexity | 8 | A single step suffices |
| Tooling Availability | 8 | Common tools apply |
| Skill Level | 4 | Intermediate skill |

#### Scalability

**Score**: 6.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 6 | Partly automatable |
| Target Scope | 6 | A class of targets |
| Resource Requirements | 6 | Moderate resources |
| Detection Difficulty | 6 | Detectable with monitoring |

#### Reachability

**Score**: 3.5 | **Trust Zone**: Agent Runtime Zone (Trusted)

tool-server-1 sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 3.5.

---

### LLM-4 — tool-server-1

**Threat**: Encoded or multilingual payloads bypass the keyword filter in front of tool-server-1, which only checks plain English text.

**Category**: llm | **Original Risk Level**: Low | **Composite**: 6.6 (Medium)

#### CVSS 3.1 Base

**Score**: 8.5 | **Vector**: `CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:C/C:H/I:H/A:L`

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

**Score**: 7.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 9 | Documented and widely used |
| Attack Complexity | 7 | A single step suffices |
| Tooling Availability | 7 | Common tools apply |
| Skill Level | 7 | Little skill needed |

#### Scalability

**Score**: 6.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 6 | Partly automatable |
| Target Scope | 6 | A class of targets |
| Resource Requirements | 9 | Minimal resources |
| Detection Difficulty | 5 | Detectable with monitoring |

#### Reachability

**Score**: 2.0 | **Trust Zone**: Agent Runtime Zone (Trusted)

tool-server-1 sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 2.0.

---

### MI-1 — intake-agent

**Threat**: intake-agent fabricates reference numbers and clause citations that look real, which operators then paste into official documents.

**Category**: llm | **Original Risk Level**: Low | **Composite**: 6.6 (Medium)

#### CVSS 3.1 Base

**Score**: 8.0 | **Vector**: `CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:C/C:H/I:H/A:N`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Network | Reachable over the network |
| Attack Complexity (AC) | High | Needs specific conditions |
| Privileges Required (PR) | None | No privileges needed |
| User Interaction (UI) | Required | A user must act |
| Scope (S) | Changed | Impact crosses a boundary |
| Confidentiality (C) | High | Broad disclosure |
| Integrity (I) | High | Broad modification |
| Availability (A) | None | No loss of service |

#### Exploitability

**Score**: 7.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 8 | Documented and widely used |
| Attack Complexity | 6 | Needs some preparation |
| Tooling Availability | 8 | Common tools apply |
| Skill Level | 8 | Little skill needed |

#### Scalability

**Score**: 5.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 5 | Partly automatable |
| Target Scope | 5 | A class of targets |
| Resource Requirements | 7 | Minimal resources |
| Detection Difficulty | 5 | Detectable with monitoring |

#### Reachability

**Score**: 3.5 | **Trust Zone**: Agent Runtime Zone (Trusted)

intake-agent sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 3.5.

---

### AG-4 — tool-server-1

**Threat**: tool-server-1 retries failed actions on its own, repeating side effects such as bookings or messages when the first attempt partly succeeded.

**Category**: agentic | **Original Risk Level**: Medium | **Composite**: 6.3 (Medium)

#### CVSS 3.1 Base

**Score**: 9.1 | **Vector**: `CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:C/C:H/I:H/A:H`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Network | Reachable over the network |
| Attack Complexity (AC) | Low | No special conditions |
| Privileges Required (PR) | High | Administrative rights are needed |
| User Interaction (UI) | None | No user action needed |
| Scope (S) | Changed | Impact crosses a boundary |
| Confidentiality (C) | High | Broad disclosure |
| Integrity (I) | High | Broad modification |
| Availability (A) | High | Loss of service |

#### Exploitability

**Score**: 5.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 5 | Described in research |
| Attack Complexity | 5 | Needs some preparation |
| Tooling Availability | 5 | Tools need adaptation |
| Skill Level | 7 | Little skill needed |

#### Scalability

**Score**: 5.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 5 | Partly automatable |
| Target Scope | 3 | One specific target |
| Resource Requirements | 6 | Moderate resources |
| Detection Difficulty | 6 | Detectable with monitoring |

#### Reachability

**Score**: 3.5 | **Trust Zone**: Agent Runtime Zone (Trusted)

tool-server-1 sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 3.5.

---

### AG-6 — planner-agent

**Threat**: planner-agent does not limit the rate or total number of tool calls per task, so abuse of a costly tool goes unnoticed until the invoice arrives.

**Category**: agentic | **Original Risk Level**: Medium | **Composite**: 6.3 (Medium)

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

**Score**: 5.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 4 | Described in research |
| Attack Complexity | 6 | Needs some preparation |
| Tooling Availability | 4 | Tools need adaptation |
| Skill Level | 6 | Intermediate skill |

#### Scalability

**Score**: 5.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 2 | Manual for each target |
| Target Scope | 3 | One specific target |
| Resource Requirements | 9 | Minimal resources |
| Detection Difficulty | 8 | Blends with normal use |

#### Reachability

**Score**: 3.0 | **Trust Zone**: Agent Runtime Zone (Trusted)

planner-agent sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 3.0.

---

### OI-3 — worker-2

**Threat**: Markdown or HTML produced by worker-2 contains remote images that leak data when a client renders it.

**Category**: llm | **Original Risk Level**: Note | **Composite**: 6.3 (Medium)

#### CVSS 3.1 Base

**Score**: 7.6 | **Vector**: `CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:L`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Network | Reachable over the network |
| Attack Complexity (AC) | Low | No special conditions |
| Privileges Required (PR) | Low | A basic account is needed |
| User Interaction (UI) | Required | A user must act |
| Scope (S) | Unchanged | Impact stays in the component |
| Confidentiality (C) | High | Broad disclosure |
| Integrity (I) | High | Broad modification |
| Availability (A) | Low | Degraded service |

#### Exploitability

**Score**: 7.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 6 | Described in research |
| Attack Complexity | 9 | A single step suffices |
| Tooling Availability | 5 | Tools need adaptation |
| Skill Level | 10 | Little skill needed |

#### Scalability

**Score**: 7.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 8 | Fully automatable |
| Target Scope | 8 | Every instance |
| Resource Requirements | 9 | Minimal resources |
| Detection Difficulty | 5 | Detectable with monitoring |

#### Reachability

**Score**: 1.5 | **Trust Zone**: Agent Runtime Zone (Trusted)

worker-2 sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 1.5.

---

### TE-2 — intake-agent

**Threat**: Persuasive phrasing from intake-agent pushes operators to approve proposals quickly, which reduces careful review.

**Category**: agentic | **Original Risk Level**: Low | **Composite**: 6.2 (Medium)

#### CVSS 3.1 Base

**Score**: 8.9 | **Vector**: `CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:H/I:H/A:L`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Network | Reachable over the network |
| Attack Complexity (AC) | Low | No special conditions |
| Privileges Required (PR) | Low | A basic account is needed |
| User Interaction (UI) | Required | A user must act |
| Scope (S) | Changed | Impact crosses a boundary |
| Confidentiality (C) | High | Broad disclosure |
| Integrity (I) | High | Broad modification |
| Availability (A) | Low | Degraded service |

#### Exploitability

**Score**: 5.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 6 | Described in research |
| Attack Complexity | 5 | Needs some preparation |
| Tooling Availability | 5 | Tools need adaptation |
| Skill Level | 6 | Intermediate skill |

#### Scalability

**Score**: 6.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 4 | Partly automatable |
| Target Scope | 4 | A class of targets |
| Resource Requirements | 9 | Minimal resources |
| Detection Difficulty | 7 | Blends with normal use |

#### Reachability

**Score**: 2.5 | **Trust Zone**: Agent Runtime Zone (Trusted)

intake-agent sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 2.5.

---

### D-2 — intake-agent

**Threat**: A single oversized or deeply nested payload makes intake-agent spend disproportionate memory and CPU parsing free-text shipment requests.

**Category**: denial-of-service | **Original Risk Level**: High | **Composite**: 6.1 (Medium)

#### CVSS 3.1 Base

**Score**: 7.5 | **Vector**: `CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Network | Reachable over the network |
| Attack Complexity (AC) | Low | No special conditions |
| Privileges Required (PR) | None | No privileges needed |
| User Interaction (UI) | None | No user action needed |
| Scope (S) | Unchanged | Impact stays in the component |
| Confidentiality (C) | None | No disclosure |
| Integrity (I) | None | No modification |
| Availability (A) | High | Loss of service |

#### Exploitability

**Score**: 7.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 6 | Described in research |
| Attack Complexity | 7 | A single step suffices |
| Tooling Availability | 8 | Common tools apply |
| Skill Level | 7 | Little skill needed |

#### Scalability

**Score**: 5.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 8 | Fully automatable |
| Target Scope | 7 | Every instance |
| Resource Requirements | 3 | Needs heavy infrastructure |
| Detection Difficulty | 2 | Readily detected |

#### Reachability

**Score**: 3.0 | **Trust Zone**: Agent Runtime Zone (Trusted)

intake-agent sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 3.0.

---

### T-1 — auth-broker

**Threat**: Backups and exports of credential assertions and session grants on auth-broker are writable by operators without a second approver, so a malicious change survives restores.

**Category**: tampering | **Original Risk Level**: High | **Composite**: 6.0 (Medium)

#### CVSS 3.1 Base

**Score**: 4.2 | **Vector**: `CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:N/I:L/A:L`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Network | Reachable over the network |
| Attack Complexity (AC) | High | Needs specific conditions |
| Privileges Required (PR) | Low | A basic account is needed |
| User Interaction (UI) | None | No user action needed |
| Scope (S) | Unchanged | Impact stays in the component |
| Confidentiality (C) | None | No disclosure |
| Integrity (I) | Low | Limited modification |
| Availability (A) | Low | Degraded service |

#### Exploitability

**Score**: 7.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 9 | Documented and widely used |
| Attack Complexity | 7 | A single step suffices |
| Tooling Availability | 7 | Common tools apply |
| Skill Level | 5 | Intermediate skill |

#### Scalability

**Score**: 8.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 8 | Fully automatable |
| Target Scope | 6 | A class of targets |
| Resource Requirements | 10 | Minimal resources |
| Detection Difficulty | 8 | Blends with normal use |

#### Reachability

**Score**: 6.0 | **Trust Zone**: Edge DMZ (Semi-trusted)

auth-broker sits in the Edge DMZ. The zone baseline is 6.5 and the refinement for this finding gives 6.0.

---

### AG-5 — tool-server-1

**Threat**: tool-server-1 invokes tools with arguments assembled from model output, so an attacker who shapes the output can call a tool with parameters the designer never allowed.

**Category**: agentic | **Original Risk Level**: Medium | **Composite**: 6.0 (Medium)

#### CVSS 3.1 Base

**Score**: 10.0 | **Vector**: `CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:L`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Network | Reachable over the network |
| Attack Complexity (AC) | Low | No special conditions |
| Privileges Required (PR) | None | No privileges needed |
| User Interaction (UI) | None | No user action needed |
| Scope (S) | Changed | Impact crosses a boundary |
| Confidentiality (C) | High | Broad disclosure |
| Integrity (I) | High | Broad modification |
| Availability (A) | Low | Degraded service |

#### Exploitability

**Score**: 4.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 6 | Described in research |
| Attack Complexity | 3 | Needs chained steps |
| Tooling Availability | 3 | Needs custom tooling |
| Skill Level | 4 | Intermediate skill |

#### Scalability

**Score**: 5.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 3 | Manual for each target |
| Target Scope | 3 | One specific target |
| Resource Requirements | 9 | Minimal resources |
| Detection Difficulty | 7 | Blends with normal use |

#### Reachability

**Score**: 2.5 | **Trust Zone**: Agent Runtime Zone (Trusted)

tool-server-1 sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 2.5.

---

### AGP-01 — worker-2

**Threat**: Worker agents coordinate through the shared message bus and memory so that each stays under its individual limits while together they exceed the authority intended for any one of them, and no single-agent control observes the combined behaviour.

**Category**: agentic | **Original Risk Level**: Medium | **Composite**: 6.0 (Medium)

#### CVSS 3.1 Base

**Score**: 9.9 | **Vector**: `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:L/A:H`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Network | Reachable over the network |
| Attack Complexity (AC) | Low | No special conditions |
| Privileges Required (PR) | Low | A basic account is needed |
| User Interaction (UI) | None | No user action needed |
| Scope (S) | Changed | Impact crosses a boundary |
| Confidentiality (C) | High | Broad disclosure |
| Integrity (I) | Low | Limited modification |
| Availability (A) | High | Loss of service |

#### Exploitability

**Score**: 4.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 4 | Described in research |
| Attack Complexity | 5 | Needs some preparation |
| Tooling Availability | 5 | Tools need adaptation |
| Skill Level | 4 | Intermediate skill |

#### Scalability

**Score**: 5.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 5 | Partly automatable |
| Target Scope | 3 | One specific target |
| Resource Requirements | 8 | Minimal resources |
| Detection Difficulty | 4 | Detectable with monitoring |

#### Reachability

**Score**: 2.0 | **Trust Zone**: Agent Runtime Zone (Trusted)

worker-2 sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 2.0.

---

### S-4 — tool-server-1

**Threat**: A shared or long-lived tool API key on tool-server-1 lets anyone who obtains one copy authenticate as every tenant that uses the same deployment profile.

**Category**: spoofing | **Original Risk Level**: High | **Composite**: 5.9 (Medium)

#### CVSS 3.1 Base

**Score**: 7.0 | **Vector**: `CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:L/A:L`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Network | Reachable over the network |
| Attack Complexity (AC) | High | Needs specific conditions |
| Privileges Required (PR) | None | No privileges needed |
| User Interaction (UI) | None | No user action needed |
| Scope (S) | Unchanged | Impact stays in the component |
| Confidentiality (C) | High | Broad disclosure |
| Integrity (I) | Low | Limited modification |
| Availability (A) | Low | Degraded service |

#### Exploitability

**Score**: 6.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 7 | Documented and widely used |
| Attack Complexity | 7 | A single step suffices |
| Tooling Availability | 5 | Tools need adaptation |
| Skill Level | 7 | Little skill needed |

#### Scalability

**Score**: 6.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 8 | Fully automatable |
| Target Scope | 4 | A class of targets |
| Resource Requirements | 6 | Moderate resources |
| Detection Difficulty | 6 | Detectable with monitoring |

#### Reachability

**Score**: 3.0 | **Trust Zone**: Agent Runtime Zone (Trusted)

tool-server-1 sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 3.0.

---

### I-5 — vector-store-a

**Threat**: embedded documents and metadata held by vector-store-a are readable by any service in the Data Zone that shares the same network role, because access is granted by network position.

**Category**: info-disclosure | **Original Risk Level**: Critical | **Composite**: 5.7 (Medium)

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

**Score**: 6.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 8 | Documented and widely used |
| Attack Complexity | 8 | A single step suffices |
| Tooling Availability | 5 | Tools need adaptation |
| Skill Level | 5 | Intermediate skill |

#### Scalability

**Score**: 6.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 5 | Partly automatable |
| Target Scope | 6 | A class of targets |
| Resource Requirements | 9 | Minimal resources |
| Detection Difficulty | 4 | Detectable with monitoring |

#### Reachability

**Score**: 3.0 | **Trust Zone**: Data Zone (Trusted)

vector-store-a sits in the Data Zone. The zone baseline is 2.5 and the refinement for this finding gives 3.0.

---

### E-3 — planner-agent

**Threat**: planner-agent runs with broader permissions than its function needs, so a flaw in handling task plans and tool selections yields access to unrelated resources.

**Category**: privilege-escalation | **Original Risk Level**: High | **Composite**: 5.7 (Medium)

#### CVSS 3.1 Base

**Score**: 8.4 | **Vector**: `CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:C/C:H/I:H/A:L`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Network | Reachable over the network |
| Attack Complexity (AC) | High | Needs specific conditions |
| Privileges Required (PR) | Low | A basic account is needed |
| User Interaction (UI) | None | No user action needed |
| Scope (S) | Changed | Impact crosses a boundary |
| Confidentiality (C) | High | Broad disclosure |
| Integrity (I) | High | Broad modification |
| Availability (A) | Low | Degraded service |

#### Exploitability

**Score**: 5.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 7 | Documented and widely used |
| Attack Complexity | 5 | Needs some preparation |
| Tooling Availability | 6 | Tools need adaptation |
| Skill Level | 4 | Intermediate skill |

#### Scalability

**Score**: 5.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 5 | Partly automatable |
| Target Scope | 4 | A class of targets |
| Resource Requirements | 6 | Moderate resources |
| Detection Difficulty | 5 | Detectable with monitoring |

#### Reachability

**Score**: 2.0 | **Trust Zone**: Agent Runtime Zone (Trusted)

planner-agent sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 2.0.

---

### AG-2 — planner-agent

**Threat**: planner-agent runs without a budget on steps or spend, so a loop or an adversarial task keeps it acting long after it stopped being useful.

**Category**: agentic | **Original Risk Level**: Critical | **Composite**: 5.7 (Medium)

**Correlation Group**: Scores inherited from primary finding E-3 (CG-3). Dimensional detail is recorded on the primary.

**Score**: 8.4 | **Vector**: `CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:C/C:H/I:H/A:L`

---

### I-4 — model-gateway

**Threat**: Cross-tenant filters on model-gateway are applied in application code only, so one missing predicate exposes another tenant's prompts and completions.

**Category**: info-disclosure | **Original Risk Level**: High | **Composite**: 5.4 (Medium)

#### CVSS 3.1 Base

**Score**: 5.9 | **Vector**: `CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:N/A:L`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Network | Reachable over the network |
| Attack Complexity (AC) | High | Needs specific conditions |
| Privileges Required (PR) | Low | A basic account is needed |
| User Interaction (UI) | None | No user action needed |
| Scope (S) | Unchanged | Impact stays in the component |
| Confidentiality (C) | High | Broad disclosure |
| Integrity (I) | None | No modification |
| Availability (A) | Low | Degraded service |

#### Exploitability

**Score**: 5.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 8 | Documented and widely used |
| Attack Complexity | 5 | Needs some preparation |
| Tooling Availability | 4 | Tools need adaptation |
| Skill Level | 5 | Intermediate skill |

#### Scalability

**Score**: 7.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 8 | Fully automatable |
| Target Scope | 6 | A class of targets |
| Resource Requirements | 9 | Minimal resources |
| Detection Difficulty | 5 | Detectable with monitoring |

#### Reachability

**Score**: 3.0 | **Trust Zone**: Agent Runtime Zone (Trusted)

model-gateway sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 3.0.

---

### LLM-5 — model-gateway

**Threat**: Indirect injection through documents retrieved for model-gateway lets the author of a retrieved page steer the answer without ever talking to the system.

**Category**: llm | **Original Risk Level**: High | **Composite**: 5.4 (Medium)

**Correlation Group**: Scores inherited from primary finding I-4 (CG-6). Dimensional detail is recorded on the primary.

**Score**: 5.9 | **Vector**: `CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:N/A:L`

---

### D-3 — vector-store-a

**Threat**: Retry storms from worker-2 multiply the load on vector-store-a when it slows down, turning a brief delay into a sustained outage.

**Category**: denial-of-service | **Original Risk Level**: Medium | **Composite**: 5.3 (Medium)

#### CVSS 3.1 Base

**Score**: 5.3 | **Vector**: `CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:N/I:N/A:H`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Network | Reachable over the network |
| Attack Complexity (AC) | High | Needs specific conditions |
| Privileges Required (PR) | Low | A basic account is needed |
| User Interaction (UI) | None | No user action needed |
| Scope (S) | Unchanged | Impact stays in the component |
| Confidentiality (C) | None | No disclosure |
| Integrity (I) | None | No modification |
| Availability (A) | High | Loss of service |

#### Exploitability

**Score**: 6.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 7 | Documented and widely used |
| Attack Complexity | 6 | Needs some preparation |
| Tooling Availability | 6 | Tools need adaptation |
| Skill Level | 7 | Little skill needed |

#### Scalability

**Score**: 6.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 9 | Fully automatable |
| Target Scope | 9 | Every instance |
| Resource Requirements | 4 | Moderate resources |
| Detection Difficulty | 2 | Readily detected |

#### Reachability

**Score**: 3.0 | **Trust Zone**: Data Zone (Trusted)

vector-store-a sits in the Data Zone. The zone baseline is 2.5 and the refinement for this finding gives 3.0.

---

### T-2 — vector-store-a

**Threat**: Serialised objects arriving from worker-2 are deserialised by vector-store-a with permissive type handling, allowing crafted payloads to instantiate unintended behaviour.

**Category**: tampering | **Original Risk Level**: Low | **Composite**: 5.0 (Medium)

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

**Score**: 5.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 4 | Described in research |
| Attack Complexity | 5 | Needs some preparation |
| Tooling Availability | 5 | Tools need adaptation |
| Skill Level | 6 | Intermediate skill |

#### Scalability

**Score**: 5.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 6 | Partly automatable |
| Target Scope | 4 | A class of targets |
| Resource Requirements | 7 | Minimal resources |
| Detection Difficulty | 5 | Detectable with monitoring |

#### Reachability

**Score**: 2.0 | **Trust Zone**: Data Zone (Trusted)

vector-store-a sits in the Data Zone. The zone baseline is 2.5 and the refinement for this finding gives 2.0.

---

### R-3 — tool-server-1

**Threat**: Operators approve changes to tool call arguments and results through a chat message or ticket comment that is not bound to the executed change, so approvals can be disputed.

**Category**: repudiation | **Original Risk Level**: Low | **Composite**: 5.0 (Medium)

#### CVSS 3.1 Base

**Score**: 6.5 | **Vector**: `CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Network | Reachable over the network |
| Attack Complexity (AC) | Low | No special conditions |
| Privileges Required (PR) | None | No privileges needed |
| User Interaction (UI) | None | No user action needed |
| Scope (S) | Unchanged | Impact stays in the component |
| Confidentiality (C) | Low | Limited disclosure |
| Integrity (I) | Low | Limited modification |
| Availability (A) | None | No loss of service |

#### Exploitability

**Score**: 4.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 3 | Not described outside research |
| Attack Complexity | 7 | A single step suffices |
| Tooling Availability | 3 | Needs custom tooling |
| Skill Level | 3 | Needs deep expertise |

#### Scalability

**Score**: 5.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 3 | Manual for each target |
| Target Scope | 4 | A class of targets |
| Resource Requirements | 9 | Minimal resources |
| Detection Difficulty | 6 | Detectable with monitoring |

#### Reachability

**Score**: 3.5 | **Trust Zone**: Agent Runtime Zone (Trusted)

tool-server-1 sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 3.5.

---

### AG-3 — tool-server-1

**Threat**: Memory written by tool-server-1 is trusted on later runs, so one poisoned entry changes the behaviour of every future task.

**Category**: agentic | **Original Risk Level**: Critical | **Composite**: 5.0 (Medium)

**Correlation Group**: Scores inherited from primary finding R-3 (CG-5). Dimensional detail is recorded on the primary.

**Score**: 6.5 | **Vector**: `CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N`

---

### LLM-6 — vector-store-a

**Threat**: Anyone who can write to the ingestion path of vector-store-a can slip in documents that contradict authoritative sources.

**Category**: llm | **Original Risk Level**: Critical | **Composite**: 5.0 (Medium)

**Correlation Group**: Scores inherited from primary finding T-2 (CG-7). Dimensional detail is recorded on the primary.

**Score**: 6.4 | **Vector**: `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:N/I:L/A:L`

---

### I-3 — worker-2

**Threat**: Logs and traces emitted by worker-2 include raw work orders and route candidates, so anyone with access to the logging pipeline can read content meant for one tenant.

**Category**: info-disclosure | **Original Risk Level**: Medium | **Composite**: 4.8 (Medium)

#### CVSS 3.1 Base

**Score**: 4.3 | **Vector**: `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Network | Reachable over the network |
| Attack Complexity (AC) | Low | No special conditions |
| Privileges Required (PR) | Low | A basic account is needed |
| User Interaction (UI) | None | No user action needed |
| Scope (S) | Unchanged | Impact stays in the component |
| Confidentiality (C) | Low | Limited disclosure |
| Integrity (I) | None | No modification |
| Availability (A) | None | No loss of service |

#### Exploitability

**Score**: 6.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 8 | Documented and widely used |
| Attack Complexity | 6 | Needs some preparation |
| Tooling Availability | 4 | Tools need adaptation |
| Skill Level | 6 | Intermediate skill |

#### Scalability

**Score**: 5.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 5 | Partly automatable |
| Target Scope | 7 | Every instance |
| Resource Requirements | 8 | Minimal resources |
| Detection Difficulty | 2 | Readily detected |

#### Reachability

**Score**: 3.5 | **Trust Zone**: Agent Runtime Zone (Trusted)

worker-2 sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 3.5.

---

### LLM-7 — worker-2

**Threat**: worker-2 follows links and files named in work orders and route candidates, which turns a harmless-looking request into a fetch of attacker-controlled content.

**Category**: llm | **Original Risk Level**: Critical | **Composite**: 4.8 (Medium)

**Correlation Group**: Scores inherited from primary finding I-3 (CG-4). Dimensional detail is recorded on the primary.

**Score**: 4.3 | **Vector**: `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N`

---

### R-1 — intake-agent

**Threat**: Clock drift between intake-agent and edge-gateway leaves events in inconsistent order, so the sequence of actions on free-text shipment requests cannot be reconstructed reliably.

**Category**: repudiation | **Original Risk Level**: Medium | **Composite**: 4.6 (Medium)

#### CVSS 3.1 Base

**Score**: 6.8 | **Vector**: `CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:L/I:H/A:N`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Local | Needs local access |
| Attack Complexity (AC) | Low | No special conditions |
| Privileges Required (PR) | None | No privileges needed |
| User Interaction (UI) | None | No user action needed |
| Scope (S) | Unchanged | Impact stays in the component |
| Confidentiality (C) | Low | Limited disclosure |
| Integrity (I) | High | Broad modification |
| Availability (A) | None | No loss of service |

#### Exploitability

**Score**: 3.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 3 | Not described outside research |
| Attack Complexity | 4 | Needs some preparation |
| Tooling Availability | 2 | Needs custom tooling |
| Skill Level | 3 | Needs deep expertise |

#### Scalability

**Score**: 6.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 2 | Manual for each target |
| Target Scope | 4 | A class of targets |
| Resource Requirements | 9 | Minimal resources |
| Detection Difficulty | 9 | Blends with normal use |

#### Reachability

**Score**: 2.0 | **Trust Zone**: Agent Runtime Zone (Trusted)

intake-agent sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 2.0.

---

### E-2 — intake-agent

**Threat**: Role claims carried in the service token presented to intake-agent are honoured without confirmation against the authoritative directory.

**Category**: privilege-escalation | **Original Risk Level**: Medium | **Composite**: 4.6 (Medium)

**Correlation Group**: Scores inherited from primary finding R-1 (CG-2). Dimensional detail is recorded on the primary.

**Score**: 6.8 | **Vector**: `CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:L/I:H/A:N`

---

### AG-1 — intake-agent

**Threat**: Memory written by intake-agent is trusted on later runs, so one poisoned entry changes the behaviour of every future task.

**Category**: agentic | **Original Risk Level**: Critical | **Composite**: 4.6 (Medium)

**Correlation Group**: Scores inherited from primary finding R-1 (CG-2). Dimensional detail is recorded on the primary.

**Score**: 6.8 | **Vector**: `CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:L/I:H/A:N`

---

### TE-1 — intake-agent

**Threat**: intake-agent adopts a persona that presents itself as a named colleague, so operators trust its suggestions more than its accuracy warrants.

**Category**: agentic | **Original Risk Level**: Medium | **Composite**: 4.4 (Medium)

#### CVSS 3.1 Base

**Score**: 4.9 | **Vector**: `CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:C/C:L/I:L/A:N`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Network | Reachable over the network |
| Attack Complexity (AC) | High | Needs specific conditions |
| Privileges Required (PR) | Low | A basic account is needed |
| User Interaction (UI) | None | No user action needed |
| Scope (S) | Changed | Impact crosses a boundary |
| Confidentiality (C) | Low | Limited disclosure |
| Integrity (I) | Low | Limited modification |
| Availability (A) | None | No loss of service |

#### Exploitability

**Score**: 5.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 6 | Described in research |
| Attack Complexity | 5 | Needs some preparation |
| Tooling Availability | 5 | Tools need adaptation |
| Skill Level | 4 | Intermediate skill |

#### Scalability

**Score**: 5.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 5 | Partly automatable |
| Target Scope | 6 | A class of targets |
| Resource Requirements | 6 | Moderate resources |
| Detection Difficulty | 5 | Detectable with monitoring |

#### Reachability

**Score**: 2.0 | **Trust Zone**: Agent Runtime Zone (Trusted)

intake-agent sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 2.0.

---

### T-3 — audit-ledger

**Threat**: An attacker who can write to the channel between tool-server-1 and audit-ledger modifies approval and tool call records in transit because messages carry no integrity protection of their own.

**Category**: tampering | **Original Risk Level**: Low | **Composite**: 4.2 (Medium)

#### CVSS 3.1 Base

**Score**: 5.0 | **Vector**: `CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:L/I:L/A:L`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Network | Reachable over the network |
| Attack Complexity (AC) | High | Needs specific conditions |
| Privileges Required (PR) | None | No privileges needed |
| User Interaction (UI) | Required | A user must act |
| Scope (S) | Unchanged | Impact stays in the component |
| Confidentiality (C) | Low | Limited disclosure |
| Integrity (I) | Low | Limited modification |
| Availability (A) | Low | Degraded service |

#### Exploitability

**Score**: 5.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 4 | Described in research |
| Attack Complexity | 7 | A single step suffices |
| Tooling Availability | 4 | Tools need adaptation |
| Skill Level | 5 | Intermediate skill |

#### Scalability

**Score**: 3.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 4 | Partly automatable |
| Target Scope | 2 | One specific target |
| Resource Requirements | 5 | Moderate resources |
| Detection Difficulty | 3 | Readily detected |

#### Reachability

**Score**: 2.0 | **Trust Zone**: Operations Zone (Trusted)

audit-ledger sits in the Operations Zone. The zone baseline is 2.5 and the refinement for this finding gives 2.0.

---

### R-4 — tool-server-1

**Threat**: Actions taken through tool-server-1 are logged without the authenticated principal or a request identifier, so a caller can deny having submitted a change to tool call arguments and results.

**Category**: repudiation | **Original Risk Level**: Medium | **Composite**: 3.7 (Low)

#### CVSS 3.1 Base

**Score**: 5.3 | **Vector**: `CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Network | Reachable over the network |
| Attack Complexity (AC) | Low | No special conditions |
| Privileges Required (PR) | None | No privileges needed |
| User Interaction (UI) | None | No user action needed |
| Scope (S) | Unchanged | Impact stays in the component |
| Confidentiality (C) | None | No disclosure |
| Integrity (I) | Low | Limited modification |
| Availability (A) | None | No loss of service |

#### Exploitability

**Score**: 3.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 3 | Not described outside research |
| Attack Complexity | 4 | Needs some preparation |
| Tooling Availability | 1 | Needs custom tooling |
| Skill Level | 4 | Intermediate skill |

#### Scalability

**Score**: 3.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 2 | Manual for each target |
| Target Scope | 1 | One specific target |
| Resource Requirements | 6 | Moderate resources |
| Detection Difficulty | 5 | Detectable with monitoring |

#### Reachability

**Score**: 2.0 | **Trust Zone**: Agent Runtime Zone (Trusted)

tool-server-1 sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 2.0.

---

## 4. Governance Fields

Remediation tracking metadata for each scored finding. Defaults are severity-driven and intended for manual override during risk review.

| ID | Severity | Owner | SLA | Disposition | Review Date |
|----|----------|-------|-----|-------------|-------------|
| E-1 | High | Unassigned | 7d | Mitigate | 2026-10-27 |
| S-3 | High | Unassigned | 7d | Mitigate | 2026-10-27 |
| S-1 | High | Unassigned | 7d | Mitigate | 2026-10-27 |
| D-1 | High | Unassigned | 7d | Mitigate | 2026-10-27 |
| OI-1 | High | Unassigned | 7d | Mitigate | 2026-10-27 |
| OI-2 | High | Unassigned | 7d | Mitigate | 2026-10-27 |
| I-1 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| LLM-1 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| LLM-2 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| LLM-3 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| MI-2 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| T-4 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| S-5 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| LLM-4 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| MI-1 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| AG-4 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| AG-6 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| OI-3 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| TE-2 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| D-2 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| T-1 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| AG-5 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| AGP-01 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| S-4 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| I-5 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| E-3 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| AG-2 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| I-4 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| LLM-5 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| D-3 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| T-2 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| R-3 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| AG-3 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| LLM-6 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| I-3 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| LLM-7 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| R-1 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| E-2 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| AG-1 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| TE-1 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| T-3 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| R-4 | Low | Unassigned | 90d | Review | 2027-01-18 |

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
