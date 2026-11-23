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

**110** threats scored | **0** Critical | **29** High | **73** Medium | **8** Low

**Highest-Risk Component**: edge-gateway — 10 finding(s), max composite 8.3

| Metric | Value |
|--------|-------|
| Scoring date | 2026-11-09 |
| Source file | `baseline/threats.md` |
| Schema version | 1.0 |

**Severity Distribution:**

| Severity | Count | Percentage |
|----------|-------|------------|
| Critical | 0 | 0.0% |
| High | 29 | 26.4% |
| Medium | 73 | 66.3% |
| Low | 8 | 7.3% |
| **Total** | **110** | **100%** |

> Trust zone data was available for every component, so no reachability value was defaulted.

---

## 2. Scored Threat Table

Findings sorted by Composite score descending (highest risk first). Boundary values map to the higher severity band.

| ID | Source | Component | Threat | CVSS | Exploit. | Scale. | Reach. | Composite | Severity | SLA | Disposition |
|----|--------|-----------|--------|------|----------|--------|--------|-----------|----------|-----|-------------|
| E-3 | fresh | auth-broker | Role claims carried in the refresh token presented to... | 9.6 | 7.0 | 7.0 | 9.0 | 8.3 | High | 7d | Mitigate |
| LLM-2 | fresh | edge-gateway | Prompt content logged by client-portal is later replayed to... | 8.3 | 9.0 | 8.5 | 7.0 | 8.3 | High | 7d | Mitigate |
| LLM-1 | fresh | edge-gateway | edge-gateway passes conversation history from earlier turns... | 4.6 | 9.0 | 8.5 | 7.0 | 8.0 | High | 7d | Mitigate |
| OI-5 | fresh | planner-agent | Structured output from planner-agent is trusted by... | 8.7 | 7.5 | 7.5 | 8.0 | 8.0 | High | 7d | Mitigate |
| S-3 | fresh | edge-gateway | A shared or long-lived bearer token on edge-gateway lets... | 8.9 | 7.5 | 8.0 | 6.5 | 7.9 | High | 7d | Mitigate |
| MI-3 | fresh | intake-agent | intake-agent states carrier rules and customs requirements... | 8.8 | 8.0 | 7.0 | 7.0 | 7.9 | High | 7d | Mitigate |
| S-11 | fresh | partner-sandbox | An unauthenticated callback or health route on... | 8.2 | 8.0 | 8.0 | 6.5 | 7.8 | High | 7d | Mitigate |
| D-2 | fresh | auth-broker | A single oversized or deeply nested payload makes... | 8.5 | 8.0 | 8.0 | 5.5 | 7.7 | High | 7d | Mitigate |
| MI-2 | fresh | intake-agent | Stale data in the knowledge base lets intake-agent present... | 10.0 | 7.0 | 7.5 | 3.0 | 7.7 | High | 7d | Mitigate |
| S-4 | fresh | auth-broker | A shared or long-lived refresh token on auth-broker lets... | 7.6 | 9.0 | 9.0 | 6.0 | 7.6 | High | 7d | Mitigate |
| S-9 | fresh | edge-gateway | An unauthenticated callback or health route on edge-gateway... | 7.1 | 8.5 | 8.5 | 5.5 | 7.6 | High | 7d | Mitigate |
| D-1 | fresh | edge-gateway | A dependency of edge-gateway becomes unavailable and the... | 6.2 | 9.0 | 8.0 | 5.5 | 7.6 | High | 7d | Mitigate |
| LLM-9 | fresh | vector-store-a | Anyone who can write to the ingestion path of vector-store-a... | 9.3 | 7.5 | 6.0 | 3.5 | 7.6 | High | 7d | Mitigate |
| E-1 | fresh | edge-gateway | Object identifiers in requests to edge-gateway are trusted... | 9.5 | 7.0 | 7.5 | 7.0 | 7.5 | High | 7d | Mitigate |
| I-2 | fresh | auth-broker | credential assertions and session grants held by auth-broker... | 5.4 | 9.0 | 7.5 | 7.0 | 7.4 | High | 7d | Mitigate |
| E-4 | fresh | auth-broker | An administrative interface of auth-broker is reachable from... | 7.9 | 7.0 | 8.0 | 6.5 | 7.4 | High | 7d | Mitigate |
| T-3 | fresh | auth-broker | Backups and exports of credential assertions and session... | 8.1 | 6.5 | 7.0 | 6.5 | 7.1 | High | 7d | Mitigate |
| I-1 | fresh | edge-gateway | Secrets such as the bearer token for edge-gateway appear in... | 5.7 | 8.0 | 8.5 | 7.0 | 7.1 | High | 7d | Mitigate |
| I-4 | fresh | planner-agent | A timing or size difference in the responses of... | 7.7 | 7.0 | 5.5 | 7.5 | 7.1 | High | 7d | Mitigate |
| AGP-07 | fresh | tool-server-1 | The intake and planning agents adjust to each other's... | 9.9 | 4.0 | 5.5 | 8.0 | 7.1 | High | 7d | Mitigate |
| MI-4 | fresh | intake-agent | Confident wording from intake-agent hides low retrieval... | 6.1 | 8.5 | 7.0 | 3.0 | 7.1 | High | 7d | Mitigate |
| MI-8 | fresh | intake-agent | intake-agent states carrier rules and customs requirements... | 9.3 | 7.5 | 7.5 | 2.5 | 7.1 | High | 7d | Mitigate |
| S-2 | fresh | client-portal | A compromised peer presents a forged service identity to... | 7.3 | 5.5 | 6.3 | 9.5 | 7.0 | High | 7d | Mitigate |
| D-8 | fresh | vector-store-a | Retry storms from worker-2 multiply the load on... | 9.1 | 7.5 | 5.5 | 2.0 | 6.9 | Medium | 30d | Review |
| TE-8 | fresh | intake-agent | intake-agent builds rapport over long sessions and starts to... | 9.9 | 3.5 | 5.0 | 8.0 | 6.9 | Medium | 30d | Review |
| R-1 | fresh | client-portal | Operators approve changes to operator requests and approval... | 5.2 | 6.0 | 6.0 | 8.0 | 6.8 | Medium | 30d | Review |
| E-2 | fresh | edge-gateway | Role claims carried in the bearer token presented to... | 7.2 | 7.0 | 7.5 | 5.5 | 6.8 | Medium | 30d | Review |
| LLM-8 | fresh | model-gateway | Model weights or adapters served by model-gateway are... | 8.2 | 8.0 | 7.0 | 2.5 | 6.8 | Medium | 30d | Review |
| OI-3 | fresh | intake-agent | Markdown or HTML produced by intake-agent contains remote... | 8.7 | 7.0 | 6.5 | 3.5 | 6.8 | High | 7d | Mitigate |
| MI-1 | fresh | intake-agent | intake-agent fabricates reference numbers and clause... | 8.3 | 7.5 | 6.5 | 3.5 | 6.8 | Medium | 30d | Review |
| MI-7 | fresh | intake-agent | Stale data in the knowledge base lets intake-agent present... | 8.2 | 8.0 | 7.0 | 2.5 | 6.8 | Medium | 30d | Review |
| OI-1 | fresh | intake-agent | intake-agent emits URLs that downstream services fetch, so... | 6.9 | 8.0 | 7.0 | 3.0 | 6.7 | Medium | 30d | Review |
| MI-9 | fresh | intake-agent | Confident wording from intake-agent hides low retrieval... | 8.0 | 8.0 | 6.5 | 2.5 | 6.7 | Medium | 30d | Review |
| MI-6 | fresh | intake-agent | intake-agent fabricates reference numbers and clause... | 8.8 | 6.5 | 7.0 | 2.5 | 6.6 | Low | 90d | Review |
| S-10 | fresh | model-gateway | An attacker replays a captured model API key against... | 8.2 | 7.0 | 6.0 | 3.0 | 6.5 | Medium | 30d | Review |
| I-9 | fresh | audit-ledger | approval and tool call records held by audit-ledger are... | 8.9 | 7.0 | 4.5 | 3.0 | 6.5 | Medium | 30d | Review |
| LLM-4 | fresh | planner-agent | Indirect injection through documents retrieved for... | 6.1 | 7.0 | 6.0 | 7.0 | 6.5 | Medium | 30d | Review |
| LLM-5 | fresh | worker-2 | worker-2 follows links and files named in work orders and... | 7.1 | 7.5 | 7.0 | 3.5 | 6.5 | Medium | 30d | Review |
| LLM-7 | fresh | model-gateway | Indirect injection through documents retrieved for... | 8.7 | 7.0 | 6.5 | 2.0 | 6.5 | Medium | 30d | Review |
| S-1 | fresh | client-portal | An attacker replays a captured session cookie against... | 7.1 | 7.5 | 8.5 | 2.0 | 6.4 | Medium | 30d | Review |
| E-8 | fresh | tool-server-1 | A confused-deputy path lets a low-privilege caller ask... | 8.8 | 4.5 | 5.5 | 3.5 | 6.4 | Medium | 30d | Review |
| AG-1 | fresh | intake-agent | Memory written by intake-agent is trusted on later runs, so... | 9.6 | 6.0 | 4.5 | 3.0 | 6.4 | Medium | 30d | Review |
| OI-2 | fresh | intake-agent | Structured output from intake-agent is trusted by... | 8.2 | 7.0 | 7.0 | 2.0 | 6.4 | Medium | 30d | Review |
| OI-4 | fresh | planner-agent | planner-agent emits URLs that downstream services fetch, so... | 8.3 | 6.5 | 6.5 | 3.0 | 6.4 | Medium | 30d | Review |
| OI-8 | fresh | model-gateway | Markdown or HTML produced by model-gateway contains remote... | 8.2 | 6.5 | 6.5 | 3.0 | 6.4 | Medium | 30d | Review |
| TE-6 | fresh | intake-agent | intake-agent adopts a persona that presents itself as a... | 8.5 | 6.0 | 5.5 | 3.5 | 6.3 | Medium | 30d | Review |
| T-1 | fresh | edge-gateway | An attacker who can write to the channel between... | 5.2 | 6.5 | 7.0 | 7.0 | 6.2 | Low | 90d | Review |
| I-8 | fresh | vector-store-a | embedded documents and metadata held by vector-store-a are... | 7.1 | 8.8 | 3.5 | 3.0 | 6.2 | Medium | 30d | Review |
| D-4 | fresh | planner-agent | A dependency of planner-agent becomes unavailable and the... | 8.2 | 6.5 | 6.0 | 2.5 | 6.2 | Low | 90d | Review |
| D-7 | fresh | model-gateway | Unbounded growth of stored prompts and completions on... | 5.3 | 7.0 | 5.5 | 7.0 | 6.2 | Medium | 30d | Review |
| S-5 | fresh | intake-agent | Session fixation against intake-agent lets an attacker... | 8.6 | 5.5 | 6.5 | 2.5 | 6.1 | Medium | 30d | Review |
| I-5 | fresh | worker-2 | Logs and traces emitted by worker-2 include raw work orders... | 7.5 | 7.5 | 6.0 | 1.5 | 6.1 | Medium | 30d | Review |
| D-5 | fresh | worker-2 | Retry storms from vector-store-a multiply the load on... | 7.2 | 7.5 | 6.0 | 2.0 | 6.1 | Medium | 30d | Review |
| E-5 | fresh | intake-agent | Role claims carried in the service token presented to... | 8.5 | 5.0 | 7.0 | 3.0 | 6.1 | Medium | 30d | Review |
| AG-3 | fresh | planner-agent | planner-agent runs without a budget on steps or spend, so a... | 9.9 | 4.5 | 6.0 | 2.0 | 6.1 | High | 7d | Mitigate |
| AG-4 | fresh | planner-agent | Delegation from model-gateway to planner-agent carries the... | 6.3 | 5.5 | 6.0 | 6.5 | 6.1 | Medium | 30d | Review |
| AG-9 | fresh | tool-server-1 | tool-server-1 invokes tools with arguments assembled from... | 7.9 | 4.0 | 5.5 | 3.0 | 6.1 | Medium | 30d | Review |
| LLM-3 | fresh | intake-agent | Encoded or multilingual payloads bypass the keyword filter... | 7.5 | 7.0 | 7.0 | 1.5 | 6.1 | Medium | 30d | Review |
| OI-9 | fresh | model-gateway | File paths or names produced by model-gateway are used to... | 7.1 | 7.0 | 7.0 | 2.5 | 6.1 | Medium | 30d | Review |
| TE-9 | fresh | intake-agent | intake-agent claims certainty it does not have when... | 8.9 | 5.5 | 4.5 | 3.5 | 6.1 | Medium | 30d | Review |
| T-8 | fresh | model-gateway | Configuration of model-gateway can be rewritten by any... | 8.9 | 5.5 | 5.5 | 2.0 | 6.0 | Medium | 30d | Review |
| R-2 | fresh | edge-gateway | Log entries from edge-gateway can be edited or deleted by... | 5.3 | 6.0 | 6.5 | 7.0 | 6.0 | Medium | 30d | Review |
| LLM-6 | fresh | tool-server-1 | Encoded or multilingual payloads bypass the keyword filter... | 7.1 | 7.0 | 7.5 | 1.5 | 6.0 | High | 7d | Mitigate |
| OI-7 | fresh | worker-2 | File paths or names produced by worker-2 are used to write... | 8.4 | 7.0 | 6.5 | 2.5 | 6.0 | Medium | 30d | Review |
| TE-5 | fresh | intake-agent | intake-agent speaks with an authoritative tone about customs... | 9.9 | 4.5 | 6.0 | 3.0 | 6.0 | Medium | 30d | Review |
| T-5 | fresh | planner-agent | Unsanitised task plans and tool selections reach... | 7.1 | 6.0 | 4.0 | 2.5 | 5.9 | Medium | 30d | Review |
| D-3 | fresh | intake-agent | A single oversized or deeply nested payload makes... | 6.5 | 7.5 | 6.0 | 2.5 | 5.9 | Medium | 30d | Review |
| E-7 | fresh | worker-2 | Role claims carried in the worker credential presented to... | 8.7 | 5.5 | 5.5 | 2.0 | 5.9 | High | 7d | Mitigate |
| E-9 | fresh | model-gateway | Role claims carried in the model API key presented to... | 8.9 | 5.0 | 6.0 | 2.0 | 5.9 | Medium | 30d | Review |
| TE-3 | fresh | intake-agent | intake-agent builds rapport over long sessions and starts to... | 9.1 | 5.0 | 4.5 | 2.5 | 5.9 | High | 7d | Mitigate |
| AGP-05 | fresh | worker-2 | Messages between the planner and its workers travel over a... | 9.9 | 4.0 | 5.5 | 1.5 | 5.8 | Medium | 30d | Review |
| MI-5 | fresh | intake-agent | Outputs from intake-agent flow into decisions without a... | 5.3 | 7.0 | 7.5 | 3.5 | 5.8 | Medium | 30d | Review |
| TE-4 | fresh | intake-agent | intake-agent claims certainty it does not have when... | 8.3 | 5.0 | 4.5 | 3.5 | 5.8 | Medium | 30d | Review |
| R-3 | fresh | auth-broker | Delegated actions performed by auth-broker on behalf of a... | 4.7 | 5.5 | 7.0 | 7.0 | 5.7 | Medium | 14d | Review |
| D-6 | fresh | tool-server-1 | A burst of requests exhausts the connection pool of... | 6.5 | 7.0 | 6.0 | 2.0 | 5.7 | Medium | 30d | Review |
| S-6 | fresh | planner-agent | An unauthenticated callback or health route on planner-agent... | 7.2 | 5.0 | 6.5 | 3.0 | 5.6 | Medium | 30d | Review |
| D-9 | fresh | audit-ledger | Expensive queries over approval and tool call records can be... | 5.9 | 6.5 | 6.0 | 3.5 | 5.6 | Medium | 30d | Accept |
| AGP-06 | fresh | tool-server-1 | Interacting planning and routing agents amplify each other's... | 8.9 | 4.5 | 5.5 | 1.5 | 5.6 | Medium | 30d | Review |
| S-8 | fresh | tool-server-1 | A shared or long-lived tool API key on tool-server-1 lets... | 7.1 | 5.5 | 6.0 | 2.5 | 5.5 | Low | 90d | Review |
| T-6 | fresh | worker-2 | An attacker who can write to the channel between... | 5.3 | 5.0 | 3.5 | 8.0 | 5.5 | Medium | 30d | Review |
| T-9 | fresh | vector-store-a | Serialised objects arriving from worker-2 are deserialised... | 6.5 | 5.5 | 7.5 | 2.5 | 5.5 | Medium | 30d | Review |
| I-6 | fresh | tool-server-1 | Cross-tenant filters on tool-server-1 are applied in... | 9.7 | 6.5 | 5.5 | 2.0 | 5.5 | Medium | 30d | Review |
| AG-2 | fresh | intake-agent | intake-agent retries failed actions on its own, repeating... | 8.3 | 4.0 | 4.5 | 1.5 | 5.5 | Medium | 30d | Review |
| AGP-04 | fresh | worker-2 | State persisted across runs lets a sleeper instruction... | 5.6 | 4.5 | 4.5 | 2.5 | 5.5 | Medium | 30d | Review |
| OI-6 | fresh | worker-2 | Markdown or HTML produced by worker-2 contains remote images... | 5.3 | 8.0 | 6.5 | 1.5 | 5.5 | Medium | 30d | Review |
| TE-1 | fresh | intake-agent | intake-agent adopts a persona that presents itself as a... | 8.9 | 4.5 | 5.0 | 1.5 | 5.5 | Medium | 30d | Review |
| TE-7 | fresh | intake-agent | Persuasive phrasing from intake-agent pushes operators to... | 7.9 | 5.0 | 6.5 | 1.5 | 5.5 | Medium | 30d | Review |
| T-4 | fresh | intake-agent | Replay of an earlier valid update to free-text shipment... | 6.9 | 5.0 | 5.0 | 1.5 | 5.4 | Medium | 30d | Review |
| AG-7 | fresh | worker-2 | Tool calls made by worker-2 are not tied to the end user, so... | 8.9 | 4.5 | 4.5 | 1.5 | 5.4 | Medium | 30d | Review |
| AG-8 | fresh | tool-server-1 | Memory written by tool-server-1 is trusted on later runs, so... | 7.5 | 5.5 | 5.0 | 2.0 | 5.4 | Medium | 30d | Review |
| AGP-01 | fresh | intake-agent | Operators and downstream agents start to accept worker... | 7.5 | 4.0 | 6.0 | 3.5 | 5.4 | High | 7d | Mitigate |
| AGP-03 | fresh | planner-agent | Several agents compete for the same carrier rate and booking... | 8.3 | 5.0 | 4.5 | 1.5 | 5.4 | Medium | 30d | Review |
| S-7 | fresh | worker-2 | A shared or long-lived worker credential on worker-2 lets... | 4.9 | 6.0 | 6.0 | 1.5 | 5.3 | Medium | 30d | Review |
| AG-6 | fresh | worker-2 | worker-2 retries failed actions on its own, repeating side... | 8.9 | 3.5 | 5.0 | 1.5 | 5.2 | Medium | 30d | Review |
| TE-2 | fresh | intake-agent | Persuasive phrasing from intake-agent pushes operators to... | 9.4 | 5.5 | 6.0 | 1.5 | 5.1 | Medium | 30d | Review |
| T-7 | fresh | tool-server-1 | An update to tool-server-1 is pulled without provenance... | 6.3 | 4.5 | 5.5 | 3.0 | 5.0 | Medium | 30d | Review |
| T-2 | fresh | vector-store-a | Backups and exports of embedded documents and metadata on... | 8.2 | 4.0 | 5.0 | 3.0 | 4.9 | Medium | 30d | Review |
| R-10 | fresh | partner-sandbox | Failed and rejected attempts against partner-sandbox are not... | 2.4 | 6.5 | 6.5 | 5.5 | 4.9 | Medium | 30d | Review |
| E-6 | fresh | planner-agent | planner-agent runs with broader permissions than its... | 5.8 | 5.0 | 5.5 | 2.5 | 4.9 | Medium | 30d | Review |
| R-8 | fresh | model-gateway | Failed and rejected attempts against model-gateway are not... | 6.5 | 3.5 | 6.0 | 3.0 | 4.8 | Medium | 30d | Review |
| AGP-02 | fresh | planner-agent | Worker agents coordinate through the shared message bus and... | 7.7 | 4.0 | 6.0 | 2.0 | 4.7 | Medium | 30d | Review |
| R-9 | fresh | audit-ledger | Log entries from audit-ledger can be edited or deleted by... | 3.5 | 3.0 | 6.0 | 8.0 | 4.6 | Medium | 30d | Review |
| I-3 | fresh | intake-agent | A timing or size difference in the responses of intake-agent... | 3.7 | 6.5 | 5.0 | 3.0 | 4.6 | Low | 90d | Review |
| T-10 | fresh | audit-ledger | An attacker who can write to the channel between... | 5.9 | 4.0 | 5.0 | 2.0 | 4.4 | Medium | 30d | Review |
| R-6 | fresh | worker-2 | Operators approve changes to work orders and route... | 6.1 | 3.0 | 4.5 | 2.0 | 4.1 | Medium | 30d | Review |
| I-7 | fresh | model-gateway | Cross-tenant filters on model-gateway are applied in... | 3.8 | 5.5 | 5.0 | 2.0 | 4.1 | Medium | 30d | Review |
| R-4 | fresh | intake-agent | Clock drift between intake-agent and edge-gateway leaves... | 4.3 | 3.0 | 5.5 | 2.0 | 3.6 | Medium | 30d | Review |
| AG-5 | fresh | planner-agent | planner-agent does not limit the rate or total number of... | 3.7 | 4.0 | 5.0 | 2.0 | 3.6 | Low | 90d | Review |
| R-7 | fresh | tool-server-1 | Operators approve changes to tool call arguments and results... | 3.5 | 3.0 | 5.0 | 2.0 | 3.3 | Low | 90d | Review |
| R-5 | fresh | planner-agent | Clock drift between planner-agent and model-gateway leaves... | 3.7 | 2.5 | 5.5 | 3.0 | 3.2 | Low | 90d | Review |

> **Correlated findings**: for correlation groups (Section 4a of the source threat model), the primary finding is scored independently. Correlated peer findings inherit the primary's scores to keep the group consistent.

---

## 3. Dimensional Breakdown

Per-finding detail showing the scoring rationale for each dimension, in the order of Section 2.

### E-3 — auth-broker

**Threat**: Role claims carried in the refresh token presented to auth-broker are honoured without confirmation against the authoritative directory.

**Category**: privilege-escalation | **Original Risk Level**: Medium | **Composite**: 8.3 (High)

#### CVSS 3.1 Base

**Score**: 9.6 | **Vector**: `CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:L/A:H`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Network | Reachable over the network |
| Attack Complexity (AC) | Low | No special conditions |
| Privileges Required (PR) | None | No privileges needed |
| User Interaction (UI) | Required | A user must act |
| Scope (S) | Changed | Impact crosses a boundary |
| Confidentiality (C) | High | Broad disclosure |
| Integrity (I) | Low | Limited modification |
| Availability (A) | High | Loss of service |

#### Exploitability

**Score**: 7.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 8 | Documented and widely used |
| Attack Complexity | 9 | A single step suffices |
| Tooling Availability | 5 | Tools need adaptation |
| Skill Level | 6 | Intermediate skill |

#### Scalability

**Score**: 7.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 7 | Fully automatable |
| Target Scope | 6 | A class of targets |
| Resource Requirements | 8 | Minimal resources |
| Detection Difficulty | 7 | Blends with normal use |

#### Reachability

**Score**: 9.0 | **Trust Zone**: Edge DMZ (Semi-trusted)

auth-broker sits in the Edge DMZ. The zone baseline is 6.5 and the refinement for this finding gives 9.0.

---

### LLM-2 — edge-gateway

**Threat**: Prompt content logged by client-portal is later replayed to edge-gateway for evaluation, carrying planted instructions into a trusted context.

**Category**: llm | **Original Risk Level**: Medium | **Composite**: 8.3 (High)

#### CVSS 3.1 Base

**Score**: 8.3 | **Vector**: `CVSS:3.1/AV:L/AC:H/PR:N/UI:R/S:C/C:H/I:L/A:H`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Local | Needs local access |
| Attack Complexity (AC) | High | Needs specific conditions |
| Privileges Required (PR) | None | No privileges needed |
| User Interaction (UI) | Required | A user must act |
| Scope (S) | Changed | Impact crosses a boundary |
| Confidentiality (C) | High | Broad disclosure |
| Integrity (I) | Low | Limited modification |
| Availability (A) | High | Loss of service |

#### Exploitability

**Score**: 9.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 10 | Documented and widely used |
| Attack Complexity | 9 | A single step suffices |
| Tooling Availability | 7 | Common tools apply |
| Skill Level | 10 | Little skill needed |

#### Scalability

**Score**: 8.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 8 | Fully automatable |
| Target Scope | 10 | Every instance |
| Resource Requirements | 10 | Minimal resources |
| Detection Difficulty | 6 | Detectable with monitoring |

#### Reachability

**Score**: 7.0 | **Trust Zone**: Edge DMZ (Semi-trusted)

edge-gateway sits in the Edge DMZ. The zone baseline is 6.5 and the refinement for this finding gives 7.0.

---

### LLM-1 — edge-gateway

**Threat**: edge-gateway passes conversation history from earlier turns into the model unchanged, so an injection planted earlier keeps working in later turns.

**Category**: llm | **Original Risk Level**: High | **Composite**: 8.0 (High)

#### CVSS 3.1 Base

**Score**: 4.6 | **Vector**: `CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:C/C:L/I:H/A:N`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Network | Reachable over the network |
| Attack Complexity (AC) | High | Needs specific conditions |
| Privileges Required (PR) | None | No privileges needed |
| User Interaction (UI) | None | No user action needed |
| Scope (S) | Changed | Impact crosses a boundary |
| Confidentiality (C) | Low | Limited disclosure |
| Integrity (I) | High | Broad modification |
| Availability (A) | None | No loss of service |

#### Exploitability

**Score**: 9.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 10 | Documented and widely used |
| Attack Complexity | 10 | A single step suffices |
| Tooling Availability | 7 | Common tools apply |
| Skill Level | 9 | Little skill needed |

#### Scalability

**Score**: 8.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 8 | Fully automatable |
| Target Scope | 9 | Every instance |
| Resource Requirements | 9 | Minimal resources |
| Detection Difficulty | 8 | Blends with normal use |

#### Reachability

**Score**: 7.0 | **Trust Zone**: Edge DMZ (Semi-trusted)

edge-gateway sits in the Edge DMZ. The zone baseline is 6.5 and the refinement for this finding gives 7.0.

---

### OI-5 — planner-agent

**Threat**: Structured output from planner-agent is trusted by model-gateway as already validated, so a malformed field flows straight into business logic.

**Category**: llm | **Original Risk Level**: High | **Composite**: 8.0 (High)

#### CVSS 3.1 Base

**Score**: 8.7 | **Vector**: `CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:H/I:H/A:N`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Network | Reachable over the network |
| Attack Complexity (AC) | Low | No special conditions |
| Privileges Required (PR) | Low | A basic account is needed |
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
| Tooling Availability | 6 | Tools need adaptation |
| Skill Level | 10 | Little skill needed |

#### Scalability

**Score**: 7.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 7 | Fully automatable |
| Target Scope | 6 | A class of targets |
| Resource Requirements | 10 | Minimal resources |
| Detection Difficulty | 7 | Blends with normal use |

#### Reachability

**Score**: 8.0 | **Trust Zone**: Agent Runtime Zone (Trusted)

planner-agent sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 8.0.

---

### S-3 — edge-gateway

**Threat**: A shared or long-lived bearer token on edge-gateway lets anyone who obtains one copy authenticate as every tenant that uses the same deployment profile.

**Category**: spoofing | **Original Risk Level**: Medium | **Composite**: 7.9 (High)

#### CVSS 3.1 Base

**Score**: 8.9 | **Vector**: `CVSS:3.1/AV:N/AC:H/PR:H/UI:R/S:U/C:L/I:L/A:H`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Network | Reachable over the network |
| Attack Complexity (AC) | High | Needs specific conditions |
| Privileges Required (PR) | High | Administrative rights are needed |
| User Interaction (UI) | Required | A user must act |
| Scope (S) | Unchanged | Impact stays in the component |
| Confidentiality (C) | Low | Limited disclosure |
| Integrity (I) | Low | Limited modification |
| Availability (A) | High | Loss of service |

#### Exploitability

**Score**: 7.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 9 | Documented and widely used |
| Attack Complexity | 7 | A single step suffices |
| Tooling Availability | 7 | Common tools apply |
| Skill Level | 7 | Little skill needed |

#### Scalability

**Score**: 8.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 8 | Fully automatable |
| Target Scope | 7 | Every instance |
| Resource Requirements | 10 | Minimal resources |
| Detection Difficulty | 7 | Blends with normal use |

#### Reachability

**Score**: 6.5 | **Trust Zone**: Edge DMZ (Semi-trusted)

edge-gateway sits in the Edge DMZ. The zone baseline is 6.5 and the refinement for this finding gives 6.5.

---

### MI-3 — intake-agent

**Threat**: intake-agent states carrier rules and customs requirements as fact without grounding them in a cited source, so an operator may act on an invented rule.

**Category**: llm | **Original Risk Level**: Critical | **Composite**: 7.9 (High)

#### CVSS 3.1 Base

**Score**: 8.8 | **Vector**: `CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:L/A:L`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Network | Reachable over the network |
| Attack Complexity (AC) | Low | No special conditions |
| Privileges Required (PR) | None | No privileges needed |
| User Interaction (UI) | Required | A user must act |
| Scope (S) | Changed | Impact crosses a boundary |
| Confidentiality (C) | High | Broad disclosure |
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

**Score**: 7.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 5 | Partly automatable |
| Target Scope | 8 | Every instance |
| Resource Requirements | 10 | Minimal resources |
| Detection Difficulty | 5 | Detectable with monitoring |

#### Reachability

**Score**: 7.0 | **Trust Zone**: Agent Runtime Zone (Trusted)

intake-agent sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 7.0.

---

### S-11 — partner-sandbox

**Threat**: An unauthenticated callback or health route on partner-sandbox accepts requests that downstream code treats as if they had come from edge-gateway.

**Category**: spoofing | **Original Risk Level**: Low | **Composite**: 7.8 (High)

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
| Known Techniques | 7 | Documented and widely used |
| Attack Complexity | 8 | A single step suffices |
| Tooling Availability | 7 | Common tools apply |
| Skill Level | 10 | Little skill needed |

#### Scalability

**Score**: 8.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 8 | Fully automatable |
| Target Scope | 7 | Every instance |
| Resource Requirements | 10 | Minimal resources |
| Detection Difficulty | 7 | Blends with normal use |

#### Reachability

**Score**: 6.5 | **Trust Zone**: Partner Exchange (Semi-trusted)

partner-sandbox sits in the Partner Exchange. The zone baseline is 5.5 and the refinement for this finding gives 6.5.

---

### D-2 — auth-broker

**Threat**: A single oversized or deeply nested payload makes auth-broker spend disproportionate memory and CPU parsing credential assertions and session grants.

**Category**: denial-of-service | **Original Risk Level**: Critical | **Composite**: 7.7 (High)

#### CVSS 3.1 Base

**Score**: 8.5 | **Vector**: `CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Local | Needs local access |
| Attack Complexity (AC) | Low | No special conditions |
| Privileges Required (PR) | None | No privileges needed |
| User Interaction (UI) | None | No user action needed |
| Scope (S) | Changed | Impact crosses a boundary |
| Confidentiality (C) | High | Broad disclosure |
| Integrity (I) | High | Broad modification |
| Availability (A) | High | Loss of service |

#### Exploitability

**Score**: 8.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 8 | Documented and widely used |
| Attack Complexity | 8 | A single step suffices |
| Tooling Availability | 7 | Common tools apply |
| Skill Level | 9 | Little skill needed |

#### Scalability

**Score**: 8.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 10 | Fully automatable |
| Target Scope | 9 | Every instance |
| Resource Requirements | 7 | Minimal resources |
| Detection Difficulty | 6 | Detectable with monitoring |

#### Reachability

**Score**: 5.5 | **Trust Zone**: Edge DMZ (Semi-trusted)

auth-broker sits in the Edge DMZ. The zone baseline is 6.5 and the refinement for this finding gives 5.5.

---

### MI-2 — intake-agent

**Threat**: Stale data in the knowledge base lets intake-agent present superseded tariffs as current, causing wrong quotes.

**Category**: llm | **Original Risk Level**: Note | **Composite**: 7.7 (High)

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

**Score**: 7.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 7 | Documented and widely used |
| Attack Complexity | 7 | A single step suffices |
| Tooling Availability | 7 | Common tools apply |
| Skill Level | 7 | Little skill needed |

#### Scalability

**Score**: 7.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 10 | Fully automatable |
| Target Scope | 5 | A class of targets |
| Resource Requirements | 10 | Minimal resources |
| Detection Difficulty | 5 | Detectable with monitoring |

#### Reachability

**Score**: 3.0 | **Trust Zone**: Agent Runtime Zone (Trusted)

intake-agent sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 3.0.

---

### S-4 — auth-broker

**Threat**: A shared or long-lived refresh token on auth-broker lets anyone who obtains one copy authenticate as every tenant that uses the same deployment profile.

**Category**: spoofing | **Original Risk Level**: High | **Composite**: 7.6 (High)

#### CVSS 3.1 Base

**Score**: 7.6 | **Vector**: `CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:H/I:L/A:N`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Network | Reachable over the network |
| Attack Complexity (AC) | Low | No special conditions |
| Privileges Required (PR) | Low | A basic account is needed |
| User Interaction (UI) | Required | A user must act |
| Scope (S) | Changed | Impact crosses a boundary |
| Confidentiality (C) | High | Broad disclosure |
| Integrity (I) | Low | Limited modification |
| Availability (A) | None | No loss of service |

#### Exploitability

**Score**: 9.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 7 | Documented and widely used |
| Attack Complexity | 9 | A single step suffices |
| Tooling Availability | 10 | Common tools apply |
| Skill Level | 10 | Little skill needed |

#### Scalability

**Score**: 9.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 10 | Fully automatable |
| Target Scope | 8 | Every instance |
| Resource Requirements | 10 | Minimal resources |
| Detection Difficulty | 8 | Blends with normal use |

#### Reachability

**Score**: 6.0 | **Trust Zone**: Edge DMZ (Semi-trusted)

auth-broker sits in the Edge DMZ. The zone baseline is 6.5 and the refinement for this finding gives 6.0.

---

### S-9 — edge-gateway

**Threat**: An unauthenticated callback or health route on edge-gateway accepts requests that downstream code treats as if they had come from intake-agent.

**Category**: spoofing | **Original Risk Level**: High | **Composite**: 7.6 (High)

#### CVSS 3.1 Base

**Score**: 7.1 | **Vector**: `CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:L/A:N`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Network | Reachable over the network |
| Attack Complexity (AC) | Low | No special conditions |
| Privileges Required (PR) | None | No privileges needed |
| User Interaction (UI) | Required | A user must act |
| Scope (S) | Unchanged | Impact stays in the component |
| Confidentiality (C) | High | Broad disclosure |
| Integrity (I) | Low | Limited modification |
| Availability (A) | None | No loss of service |

#### Exploitability

**Score**: 8.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 7 | Documented and widely used |
| Attack Complexity | 8 | A single step suffices |
| Tooling Availability | 10 | Common tools apply |
| Skill Level | 9 | Little skill needed |

#### Scalability

**Score**: 8.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 9 | Fully automatable |
| Target Scope | 9 | Every instance |
| Resource Requirements | 9 | Minimal resources |
| Detection Difficulty | 7 | Blends with normal use |

#### Reachability

**Score**: 5.5 | **Trust Zone**: Edge DMZ (Semi-trusted)

edge-gateway sits in the Edge DMZ. The zone baseline is 6.5 and the refinement for this finding gives 5.5.

---

### D-1 — edge-gateway

**Threat**: A dependency of edge-gateway becomes unavailable and the failure cascades because edge-gateway waits on it synchronously for every request.

**Category**: denial-of-service | **Original Risk Level**: High | **Composite**: 7.6 (High)

#### CVSS 3.1 Base

**Score**: 6.2 | **Vector**: `CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H`

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

**Score**: 9.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 9 | Documented and widely used |
| Attack Complexity | 8 | A single step suffices |
| Tooling Availability | 10 | Common tools apply |
| Skill Level | 9 | Little skill needed |

#### Scalability

**Score**: 8.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 9 | Fully automatable |
| Target Scope | 10 | Every instance |
| Resource Requirements | 8 | Minimal resources |
| Detection Difficulty | 5 | Detectable with monitoring |

#### Reachability

**Score**: 5.5 | **Trust Zone**: Edge DMZ (Semi-trusted)

edge-gateway sits in the Edge DMZ. The zone baseline is 6.5 and the refinement for this finding gives 5.5.

---

### LLM-9 — vector-store-a

**Threat**: Anyone who can write to the ingestion path of vector-store-a can slip in documents that contradict authoritative sources.

**Category**: llm | **Original Risk Level**: High | **Composite**: 7.6 (High)

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
| Tooling Availability | 8 | Common tools apply |
| Skill Level | 7 | Little skill needed |

#### Scalability

**Score**: 6.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 7 | Fully automatable |
| Target Scope | 6 | A class of targets |
| Resource Requirements | 7 | Minimal resources |
| Detection Difficulty | 4 | Detectable with monitoring |

#### Reachability

**Score**: 3.5 | **Trust Zone**: Data Zone (Trusted)

vector-store-a sits in the Data Zone. The zone baseline is 2.5 and the refinement for this finding gives 3.5.

---

### E-1 — edge-gateway

**Threat**: Object identifiers in requests to edge-gateway are trusted without an ownership check, so a caller can read or change inbound API requests that belong to others.

**Category**: privilege-escalation | **Original Risk Level**: Low | **Composite**: 7.5 (High)

#### CVSS 3.1 Base

**Score**: 9.5 | **Vector**: `CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:C/C:L/I:H/A:L`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Network | Reachable over the network |
| Attack Complexity (AC) | Low | No special conditions |
| Privileges Required (PR) | High | Administrative rights are needed |
| User Interaction (UI) | None | No user action needed |
| Scope (S) | Changed | Impact crosses a boundary |
| Confidentiality (C) | Low | Limited disclosure |
| Integrity (I) | High | Broad modification |
| Availability (A) | Low | Degraded service |

#### Exploitability

**Score**: 7.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 7 | Documented and widely used |
| Attack Complexity | 6 | Needs some preparation |
| Tooling Availability | 7 | Common tools apply |
| Skill Level | 8 | Little skill needed |

#### Scalability

**Score**: 7.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 6 | Partly automatable |
| Target Scope | 7 | Every instance |
| Resource Requirements | 10 | Minimal resources |
| Detection Difficulty | 7 | Blends with normal use |

#### Reachability

**Score**: 7.0 | **Trust Zone**: Edge DMZ (Semi-trusted)

edge-gateway sits in the Edge DMZ. The zone baseline is 6.5 and the refinement for this finding gives 7.0.

---

### I-2 — auth-broker

**Threat**: credential assertions and session grants held by auth-broker are readable by any service in the Edge DMZ that shares the same network role, because access is granted by network position.

**Category**: info-disclosure | **Original Risk Level**: High | **Composite**: 7.4 (High)

#### CVSS 3.1 Base

**Score**: 5.4 | **Vector**: `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:N`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Network | Reachable over the network |
| Attack Complexity (AC) | Low | No special conditions |
| Privileges Required (PR) | Low | A basic account is needed |
| User Interaction (UI) | None | No user action needed |
| Scope (S) | Unchanged | Impact stays in the component |
| Confidentiality (C) | Low | Limited disclosure |
| Integrity (I) | Low | Limited modification |
| Availability (A) | None | No loss of service |

#### Exploitability

**Score**: 9.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 10 | Documented and widely used |
| Attack Complexity | 9 | A single step suffices |
| Tooling Availability | 9 | Common tools apply |
| Skill Level | 8 | Little skill needed |

#### Scalability

**Score**: 7.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 7 | Fully automatable |
| Target Scope | 7 | Every instance |
| Resource Requirements | 8 | Minimal resources |
| Detection Difficulty | 8 | Blends with normal use |

#### Reachability

**Score**: 7.0 | **Trust Zone**: Edge DMZ (Semi-trusted)

auth-broker sits in the Edge DMZ. The zone baseline is 6.5 and the refinement for this finding gives 7.0.

---

### E-4 — auth-broker

**Threat**: An administrative interface of auth-broker is reachable from the same network as ordinary callers and relies on a single shared password.

**Category**: privilege-escalation | **Original Risk Level**: Medium | **Composite**: 7.4 (High)

#### CVSS 3.1 Base

**Score**: 7.9 | **Vector**: `CVSS:3.1/AV:N/AC:H/PR:H/UI:N/S:C/C:H/I:L/A:H`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Network | Reachable over the network |
| Attack Complexity (AC) | High | Needs specific conditions |
| Privileges Required (PR) | High | Administrative rights are needed |
| User Interaction (UI) | None | No user action needed |
| Scope (S) | Changed | Impact crosses a boundary |
| Confidentiality (C) | High | Broad disclosure |
| Integrity (I) | Low | Limited modification |
| Availability (A) | High | Loss of service |

#### Exploitability

**Score**: 7.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 6 | Described in research |
| Attack Complexity | 8 | A single step suffices |
| Tooling Availability | 6 | Tools need adaptation |
| Skill Level | 8 | Little skill needed |

#### Scalability

**Score**: 8.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 8 | Fully automatable |
| Target Scope | 8 | Every instance |
| Resource Requirements | 9 | Minimal resources |
| Detection Difficulty | 7 | Blends with normal use |

#### Reachability

**Score**: 6.5 | **Trust Zone**: Edge DMZ (Semi-trusted)

auth-broker sits in the Edge DMZ. The zone baseline is 6.5 and the refinement for this finding gives 6.5.

---

### T-3 — auth-broker

**Threat**: Backups and exports of credential assertions and session grants on auth-broker are writable by operators without a second approver, so a malicious change survives restores.

**Category**: tampering | **Original Risk Level**: High | **Composite**: 7.1 (High)

#### CVSS 3.1 Base

**Score**: 8.1 | **Vector**: `CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:L/A:H`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Network | Reachable over the network |
| Attack Complexity (AC) | Low | No special conditions |
| Privileges Required (PR) | None | No privileges needed |
| User Interaction (UI) | Required | A user must act |
| Scope (S) | Unchanged | Impact stays in the component |
| Confidentiality (C) | High | Broad disclosure |
| Integrity (I) | Low | Limited modification |
| Availability (A) | High | Loss of service |

#### Exploitability

**Score**: 6.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 8 | Documented and widely used |
| Attack Complexity | 7 | A single step suffices |
| Tooling Availability | 6 | Tools need adaptation |
| Skill Level | 5 | Intermediate skill |

#### Scalability

**Score**: 7.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 6 | Partly automatable |
| Target Scope | 7 | Every instance |
| Resource Requirements | 9 | Minimal resources |
| Detection Difficulty | 6 | Detectable with monitoring |

#### Reachability

**Score**: 6.5 | **Trust Zone**: Edge DMZ (Semi-trusted)

auth-broker sits in the Edge DMZ. The zone baseline is 6.5 and the refinement for this finding gives 6.5.

---

### I-1 — edge-gateway

**Threat**: Secrets such as the bearer token for edge-gateway appear in process arguments and environment dumps that diagnostic tooling captures.

**Category**: info-disclosure | **Original Risk Level**: Low | **Composite**: 7.1 (High)

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

**Score**: 8.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 7 | Documented and widely used |
| Attack Complexity | 9 | A single step suffices |
| Tooling Availability | 8 | Common tools apply |
| Skill Level | 8 | Little skill needed |

#### Scalability

**Score**: 8.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 8 | Fully automatable |
| Target Scope | 9 | Every instance |
| Resource Requirements | 10 | Minimal resources |
| Detection Difficulty | 7 | Blends with normal use |

#### Reachability

**Score**: 7.0 | **Trust Zone**: Edge DMZ (Semi-trusted)

edge-gateway sits in the Edge DMZ. The zone baseline is 6.5 and the refinement for this finding gives 7.0.

---

### I-4 — planner-agent

**Threat**: A timing or size difference in the responses of planner-agent lets an observer infer whether specific records of task plans and tool selections exist.

**Category**: info-disclosure | **Original Risk Level**: High | **Composite**: 7.1 (High)

#### CVSS 3.1 Base

**Score**: 7.7 | **Vector**: `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:N/A:N`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Network | Reachable over the network |
| Attack Complexity (AC) | Low | No special conditions |
| Privileges Required (PR) | Low | A basic account is needed |
| User Interaction (UI) | None | No user action needed |
| Scope (S) | Changed | Impact crosses a boundary |
| Confidentiality (C) | High | Broad disclosure |
| Integrity (I) | None | No modification |
| Availability (A) | None | No loss of service |

#### Exploitability

**Score**: 7.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 6 | Described in research |
| Attack Complexity | 8 | A single step suffices |
| Tooling Availability | 7 | Common tools apply |
| Skill Level | 7 | Little skill needed |

#### Scalability

**Score**: 5.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 6 | Partly automatable |
| Target Scope | 5 | A class of targets |
| Resource Requirements | 6 | Moderate resources |
| Detection Difficulty | 5 | Detectable with monitoring |

#### Reachability

**Score**: 7.5 | **Trust Zone**: Agent Runtime Zone (Trusted)

planner-agent sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 7.5.

---

### AGP-07 — tool-server-1

**Threat**: The intake and planning agents adjust to each other's phrasing over many runs until requests are structured in ways no test covered, and the drift is invisible in any single exchange.

**Category**: agentic | **Original Risk Level**: Medium | **Composite**: 7.1 (High)

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

**Score**: 4.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 6 | Described in research |
| Attack Complexity | 3 | Needs chained steps |
| Tooling Availability | 2 | Needs custom tooling |
| Skill Level | 5 | Intermediate skill |

#### Scalability

**Score**: 5.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 5 | Partly automatable |
| Target Scope | 3 | One specific target |
| Resource Requirements | 9 | Minimal resources |
| Detection Difficulty | 5 | Detectable with monitoring |

#### Reachability

**Score**: 8.0 | **Trust Zone**: Agent Runtime Zone (Trusted)

tool-server-1 sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 8.0.

---

### MI-4 — intake-agent

**Threat**: Confident wording from intake-agent hides low retrieval quality, so operators cannot tell a grounded answer from a guess.

**Category**: llm | **Original Risk Level**: High | **Composite**: 7.1 (High)

#### CVSS 3.1 Base

**Score**: 6.1 | **Vector**: `CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:H/A:L`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Network | Reachable over the network |
| Attack Complexity (AC) | Low | No special conditions |
| Privileges Required (PR) | Low | A basic account is needed |
| User Interaction (UI) | Required | A user must act |
| Scope (S) | Changed | Impact crosses a boundary |
| Confidentiality (C) | Low | Limited disclosure |
| Integrity (I) | High | Broad modification |
| Availability (A) | Low | Degraded service |

#### Exploitability

**Score**: 8.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 8 | Documented and widely used |
| Attack Complexity | 9 | A single step suffices |
| Tooling Availability | 8 | Common tools apply |
| Skill Level | 9 | Little skill needed |

#### Scalability

**Score**: 7.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 6 | Partly automatable |
| Target Scope | 7 | Every instance |
| Resource Requirements | 8 | Minimal resources |
| Detection Difficulty | 7 | Blends with normal use |

#### Reachability

**Score**: 3.0 | **Trust Zone**: Agent Runtime Zone (Trusted)

intake-agent sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 3.0.

---

### MI-8 — intake-agent

**Threat**: intake-agent states carrier rules and customs requirements as fact without grounding them in a cited source, so an operator may act on an invented rule.

**Category**: llm | **Original Risk Level**: Medium | **Composite**: 7.1 (High)

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
| Known Techniques | 8 | Documented and widely used |
| Attack Complexity | 9 | A single step suffices |
| Tooling Availability | 7 | Common tools apply |
| Skill Level | 6 | Intermediate skill |

#### Scalability

**Score**: 7.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 6 | Partly automatable |
| Target Scope | 8 | Every instance |
| Resource Requirements | 10 | Minimal resources |
| Detection Difficulty | 6 | Detectable with monitoring |

#### Reachability

**Score**: 2.5 | **Trust Zone**: Agent Runtime Zone (Trusted)

intake-agent sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 2.5.

---

### S-2 — client-portal

**Threat**: A compromised peer presents a forged service identity to client-portal, and client-portal accepts the claim without verifying the signature chain back to the issuing authority.

**Category**: spoofing | **Original Risk Level**: Medium | **Composite**: 7.0 (High)

#### CVSS 3.1 Base

**Score**: 7.3 | **Vector**: `CVSS:3.1/AV:A/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Adjacent | Needs an adjacent network |
| Attack Complexity (AC) | Low | No special conditions |
| Privileges Required (PR) | Low | A basic account is needed |
| User Interaction (UI) | None | No user action needed |
| Scope (S) | Unchanged | Impact stays in the component |
| Confidentiality (C) | High | Broad disclosure |
| Integrity (I) | High | Broad modification |
| Availability (A) | None | No loss of service |

#### Exploitability

**Score**: 5.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 6 | Described in research |
| Attack Complexity | 6 | Needs some preparation |
| Tooling Availability | 5 | Tools need adaptation |
| Skill Level | 5 | Intermediate skill |

#### Scalability

**Score**: 6.3 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 7 | Fully automatable |
| Target Scope | 6 | A class of targets |
| Resource Requirements | 6 | Moderate resources |
| Detection Difficulty | 6 | Detectable with monitoring |

#### Reachability

**Score**: 9.5 | **Trust Zone**: Public Internet (Untrusted)

client-portal sits in the Public Internet. The zone baseline is 9.0 and the refinement for this finding gives 9.5.

---

### D-8 — vector-store-a

**Threat**: Retry storms from worker-2 multiply the load on vector-store-a when it slows down, turning a brief delay into a sustained outage.

**Category**: denial-of-service | **Original Risk Level**: Critical | **Composite**: 6.9 (Medium)

#### CVSS 3.1 Base

**Score**: 9.1 | **Vector**: `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:L/I:L/A:H`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Network | Reachable over the network |
| Attack Complexity (AC) | Low | No special conditions |
| Privileges Required (PR) | Low | A basic account is needed |
| User Interaction (UI) | None | No user action needed |
| Scope (S) | Changed | Impact crosses a boundary |
| Confidentiality (C) | Low | Limited disclosure |
| Integrity (I) | Low | Limited modification |
| Availability (A) | High | Loss of service |

#### Exploitability

**Score**: 7.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 7 | Documented and widely used |
| Attack Complexity | 8 | A single step suffices |
| Tooling Availability | 6 | Tools need adaptation |
| Skill Level | 9 | Little skill needed |

#### Scalability

**Score**: 5.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 8 | Fully automatable |
| Target Scope | 7 | Every instance |
| Resource Requirements | 3 | Needs heavy infrastructure |
| Detection Difficulty | 4 | Detectable with monitoring |

#### Reachability

**Score**: 2.0 | **Trust Zone**: Data Zone (Trusted)

vector-store-a sits in the Data Zone. The zone baseline is 2.5 and the refinement for this finding gives 2.0.

---

### TE-8 — intake-agent

**Threat**: intake-agent builds rapport over long sessions and starts to share unprompted details about earlier operators.

**Category**: agentic | **Original Risk Level**: Critical | **Composite**: 6.9 (Medium)

#### CVSS 3.1 Base

**Score**: 9.9 | **Vector**: `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:L`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Network | Reachable over the network |
| Attack Complexity (AC) | Low | No special conditions |
| Privileges Required (PR) | Low | A basic account is needed |
| User Interaction (UI) | None | No user action needed |
| Scope (S) | Changed | Impact crosses a boundary |
| Confidentiality (C) | High | Broad disclosure |
| Integrity (I) | High | Broad modification |
| Availability (A) | Low | Degraded service |

#### Exploitability

**Score**: 3.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 5 | Described in research |
| Attack Complexity | 3 | Needs chained steps |
| Tooling Availability | 2 | Needs custom tooling |
| Skill Level | 4 | Intermediate skill |

#### Scalability

**Score**: 5.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 2 | Manual for each target |
| Target Scope | 4 | A class of targets |
| Resource Requirements | 9 | Minimal resources |
| Detection Difficulty | 5 | Detectable with monitoring |

#### Reachability

**Score**: 8.0 | **Trust Zone**: Agent Runtime Zone (Trusted)

intake-agent sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 8.0.

---

### R-1 — client-portal

**Threat**: Operators approve changes to operator requests and approval decisions through a chat message or ticket comment that is not bound to the executed change, so approvals can be disputed.

**Category**: repudiation | **Original Risk Level**: Low | **Composite**: 6.8 (Medium)

#### CVSS 3.1 Base

**Score**: 5.2 | **Vector**: `CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:H/A:N`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Network | Reachable over the network |
| Attack Complexity (AC) | Low | No special conditions |
| Privileges Required (PR) | None | No privileges needed |
| User Interaction (UI) | Required | A user must act |
| Scope (S) | Unchanged | Impact stays in the component |
| Confidentiality (C) | Low | Limited disclosure |
| Integrity (I) | High | Broad modification |
| Availability (A) | None | No loss of service |

#### Exploitability

**Score**: 6.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 7 | Documented and widely used |
| Attack Complexity | 6 | Needs some preparation |
| Tooling Availability | 4 | Tools need adaptation |
| Skill Level | 7 | Little skill needed |

#### Scalability

**Score**: 6.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 4 | Partly automatable |
| Target Scope | 3 | One specific target |
| Resource Requirements | 9 | Minimal resources |
| Detection Difficulty | 8 | Blends with normal use |

#### Reachability

**Score**: 8.0 | **Trust Zone**: Public Internet (Untrusted)

client-portal sits in the Public Internet. The zone baseline is 9.0 and the refinement for this finding gives 8.0.

---

### E-2 — edge-gateway

**Threat**: Role claims carried in the bearer token presented to edge-gateway are honoured without confirmation against the authoritative directory.

**Category**: privilege-escalation | **Original Risk Level**: High | **Composite**: 6.8 (Medium)

#### CVSS 3.1 Base

**Score**: 7.2 | **Vector**: `CVSS:3.1/AV:P/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:H`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Physical | Needs physical access |
| Attack Complexity (AC) | Low | No special conditions |
| Privileges Required (PR) | Low | A basic account is needed |
| User Interaction (UI) | None | No user action needed |
| Scope (S) | Unchanged | Impact stays in the component |
| Confidentiality (C) | Low | Limited disclosure |
| Integrity (I) | None | No modification |
| Availability (A) | High | Loss of service |

#### Exploitability

**Score**: 7.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 6 | Described in research |
| Attack Complexity | 7 | A single step suffices |
| Tooling Availability | 6 | Tools need adaptation |
| Skill Level | 9 | Little skill needed |

#### Scalability

**Score**: 7.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 9 | Fully automatable |
| Target Scope | 5 | A class of targets |
| Resource Requirements | 8 | Minimal resources |
| Detection Difficulty | 8 | Blends with normal use |

#### Reachability

**Score**: 5.5 | **Trust Zone**: Edge DMZ (Semi-trusted)

edge-gateway sits in the Edge DMZ. The zone baseline is 6.5 and the refinement for this finding gives 5.5.

---

### LLM-8 — model-gateway

**Threat**: Model weights or adapters served by model-gateway are readable by operators and by any process sharing the host.

**Category**: llm | **Original Risk Level**: Medium | **Composite**: 6.8 (Medium)

#### CVSS 3.1 Base

**Score**: 8.2 | **Vector**: `CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:L/A:N`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Network | Reachable over the network |
| Attack Complexity (AC) | Low | No special conditions |
| Privileges Required (PR) | None | No privileges needed |
| User Interaction (UI) | Required | A user must act |
| Scope (S) | Changed | Impact crosses a boundary |
| Confidentiality (C) | High | Broad disclosure |
| Integrity (I) | Low | Limited modification |
| Availability (A) | None | No loss of service |

#### Exploitability

**Score**: 8.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 9 | Documented and widely used |
| Attack Complexity | 8 | A single step suffices |
| Tooling Availability | 6 | Tools need adaptation |
| Skill Level | 9 | Little skill needed |

#### Scalability

**Score**: 7.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 7 | Fully automatable |
| Target Scope | 5 | A class of targets |
| Resource Requirements | 9 | Minimal resources |
| Detection Difficulty | 7 | Blends with normal use |

#### Reachability

**Score**: 2.5 | **Trust Zone**: Agent Runtime Zone (Trusted)

model-gateway sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 2.5.

---

### OI-3 — intake-agent

**Threat**: Markdown or HTML produced by intake-agent contains remote images that leak data when a client renders it.

**Category**: llm | **Original Risk Level**: Critical | **Composite**: 6.8 (High)

#### CVSS 3.1 Base

**Score**: 8.7 | **Vector**: `CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:H/I:H/A:N`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Network | Reachable over the network |
| Attack Complexity (AC) | Low | No special conditions |
| Privileges Required (PR) | Low | A basic account is needed |
| User Interaction (UI) | Required | A user must act |
| Scope (S) | Changed | Impact crosses a boundary |
| Confidentiality (C) | High | Broad disclosure |
| Integrity (I) | High | Broad modification |
| Availability (A) | None | No loss of service |

#### Exploitability

**Score**: 7.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 9 | Documented and widely used |
| Attack Complexity | 6 | Needs some preparation |
| Tooling Availability | 5 | Tools need adaptation |
| Skill Level | 8 | Little skill needed |

#### Scalability

**Score**: 6.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 6 | Partly automatable |
| Target Scope | 5 | A class of targets |
| Resource Requirements | 7 | Minimal resources |
| Detection Difficulty | 8 | Blends with normal use |

#### Reachability

**Score**: 3.5 | **Trust Zone**: Agent Runtime Zone (Trusted)

intake-agent sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 3.5.

---

### MI-1 — intake-agent

**Threat**: intake-agent fabricates reference numbers and clause citations that look real, which operators then paste into official documents.

**Category**: llm | **Original Risk Level**: High | **Composite**: 6.8 (Medium)

#### CVSS 3.1 Base

**Score**: 8.3 | **Vector**: `CVSS:3.1/AV:N/AC:H/PR:L/UI:R/S:C/C:L/I:L/A:H`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Network | Reachable over the network |
| Attack Complexity (AC) | High | Needs specific conditions |
| Privileges Required (PR) | Low | A basic account is needed |
| User Interaction (UI) | Required | A user must act |
| Scope (S) | Changed | Impact crosses a boundary |
| Confidentiality (C) | Low | Limited disclosure |
| Integrity (I) | Low | Limited modification |
| Availability (A) | High | Loss of service |

#### Exploitability

**Score**: 7.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 7 | Documented and widely used |
| Attack Complexity | 9 | A single step suffices |
| Tooling Availability | 8 | Common tools apply |
| Skill Level | 6 | Intermediate skill |

#### Scalability

**Score**: 6.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 5 | Partly automatable |
| Target Scope | 8 | Every instance |
| Resource Requirements | 7 | Minimal resources |
| Detection Difficulty | 6 | Detectable with monitoring |

#### Reachability

**Score**: 3.5 | **Trust Zone**: Agent Runtime Zone (Trusted)

intake-agent sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 3.5.

---

### MI-7 — intake-agent

**Threat**: Stale data in the knowledge base lets intake-agent present superseded tariffs as current, causing wrong quotes.

**Category**: llm | **Original Risk Level**: Medium | **Composite**: 6.8 (Medium)

#### CVSS 3.1 Base

**Score**: 8.2 | **Vector**: —

#### Exploitability

**Score**: 8.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 9 | Documented and widely used |
| Attack Complexity | 8 | A single step suffices |
| Tooling Availability | 8 | Common tools apply |
| Skill Level | 7 | Little skill needed |

#### Scalability

**Score**: 7.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 7 | Fully automatable |
| Target Scope | 6 | A class of targets |
| Resource Requirements | 7 | Minimal resources |
| Detection Difficulty | 8 | Blends with normal use |

#### Reachability

**Score**: 2.5 | **Trust Zone**: Agent Runtime Zone (Trusted)

intake-agent sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 2.5.

---

### OI-1 — intake-agent

**Threat**: intake-agent emits URLs that downstream services fetch, so an attacker can make internal addresses part of the output and trigger server-side requests.

**Category**: llm | **Original Risk Level**: Medium | **Composite**: 6.7 (Medium)

#### CVSS 3.1 Base

**Score**: 6.9 | **Vector**: `CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:C/C:H/I:L/A:N`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Network | Reachable over the network |
| Attack Complexity (AC) | High | Needs specific conditions |
| Privileges Required (PR) | None | No privileges needed |
| User Interaction (UI) | Required | A user must act |
| Scope (S) | Changed | Impact crosses a boundary |
| Confidentiality (C) | High | Broad disclosure |
| Integrity (I) | Low | Limited modification |
| Availability (A) | None | No loss of service |

#### Exploitability

**Score**: 8.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 9 | Documented and widely used |
| Attack Complexity | 9 | A single step suffices |
| Tooling Availability | 6 | Tools need adaptation |
| Skill Level | 8 | Little skill needed |

#### Scalability

**Score**: 7.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 7 | Fully automatable |
| Target Scope | 6 | A class of targets |
| Resource Requirements | 8 | Minimal resources |
| Detection Difficulty | 7 | Blends with normal use |

#### Reachability

**Score**: 3.0 | **Trust Zone**: Agent Runtime Zone (Trusted)

intake-agent sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 3.0.

---

### MI-9 — intake-agent

**Threat**: Confident wording from intake-agent hides low retrieval quality, so operators cannot tell a grounded answer from a guess.

**Category**: llm | **Original Risk Level**: Medium | **Composite**: 6.7 (Medium)

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

**Score**: 8.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 7 | Documented and widely used |
| Attack Complexity | 9 | A single step suffices |
| Tooling Availability | 6 | Tools need adaptation |
| Skill Level | 10 | Little skill needed |

#### Scalability

**Score**: 6.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 6 | Partly automatable |
| Target Scope | 8 | Every instance |
| Resource Requirements | 8 | Minimal resources |
| Detection Difficulty | 4 | Detectable with monitoring |

#### Reachability

**Score**: 2.5 | **Trust Zone**: Agent Runtime Zone (Trusted)

intake-agent sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 2.5.

---

### MI-6 — intake-agent

**Threat**: intake-agent fabricates reference numbers and clause citations that look real, which operators then paste into official documents.

**Category**: llm | **Original Risk Level**: Critical | **Composite**: 6.6 (Low)

#### CVSS 3.1 Base

**Score**: 8.8 | **Vector**: `CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:H/A:L`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Network | Reachable over the network |
| Attack Complexity (AC) | Low | No special conditions |
| Privileges Required (PR) | None | No privileges needed |
| User Interaction (UI) | Required | A user must act |
| Scope (S) | Changed | Impact crosses a boundary |
| Confidentiality (C) | Low | Limited disclosure |
| Integrity (I) | High | Broad modification |
| Availability (A) | Low | Degraded service |

#### Exploitability

**Score**: 6.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 8 | Documented and widely used |
| Attack Complexity | 7 | A single step suffices |
| Tooling Availability | 5 | Tools need adaptation |
| Skill Level | 6 | Intermediate skill |

#### Scalability

**Score**: 7.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 8 | Fully automatable |
| Target Scope | 7 | Every instance |
| Resource Requirements | 7 | Minimal resources |
| Detection Difficulty | 6 | Detectable with monitoring |

#### Reachability

**Score**: 2.5 | **Trust Zone**: Agent Runtime Zone (Trusted)

intake-agent sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 2.5.

---

### S-10 — model-gateway

**Threat**: An attacker replays a captured model API key against model-gateway, which does not bind the credential to the session or channel it was issued for, so the replay is accepted as the original caller.

**Category**: spoofing | **Original Risk Level**: High | **Composite**: 6.5 (Medium)

#### CVSS 3.1 Base

**Score**: 8.2 | **Vector**: —

#### Exploitability

**Score**: 7.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 7 | Documented and widely used |
| Attack Complexity | 8 | A single step suffices |
| Tooling Availability | 7 | Common tools apply |
| Skill Level | 6 | Intermediate skill |

#### Scalability

**Score**: 6.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 6 | Partly automatable |
| Target Scope | 6 | A class of targets |
| Resource Requirements | 8 | Minimal resources |
| Detection Difficulty | 4 | Detectable with monitoring |

#### Reachability

**Score**: 3.0 | **Trust Zone**: Agent Runtime Zone (Trusted)

model-gateway sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 3.0.

---

### I-9 — audit-ledger

**Threat**: approval and tool call records held by audit-ledger are readable by any service in the Operations Zone that shares the same network role, because access is granted by network position.

**Category**: info-disclosure | **Original Risk Level**: Low | **Composite**: 6.5 (Medium)

#### CVSS 3.1 Base

**Score**: 8.9 | **Vector**: `CVSS:3.1/AV:P/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:L`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Physical | Needs physical access |
| Attack Complexity (AC) | Low | No special conditions |
| Privileges Required (PR) | Low | A basic account is needed |
| User Interaction (UI) | Required | A user must act |
| Scope (S) | Unchanged | Impact stays in the component |
| Confidentiality (C) | High | Broad disclosure |
| Integrity (I) | High | Broad modification |
| Availability (A) | Low | Degraded service |

#### Exploitability

**Score**: 7.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 8 | Documented and widely used |
| Attack Complexity | 8 | A single step suffices |
| Tooling Availability | 7 | Common tools apply |
| Skill Level | 5 | Intermediate skill |

#### Scalability

**Score**: 4.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 5 | Partly automatable |
| Target Scope | 4 | A class of targets |
| Resource Requirements | 7 | Minimal resources |
| Detection Difficulty | 2 | Readily detected |

#### Reachability

**Score**: 3.0 | **Trust Zone**: Operations Zone (Trusted)

audit-ledger sits in the Operations Zone. The zone baseline is 2.5 and the refinement for this finding gives 3.0.

---

### LLM-4 — planner-agent

**Threat**: Indirect injection through documents retrieved for planner-agent lets the author of a retrieved page steer the answer without ever talking to the system.

**Category**: llm | **Original Risk Level**: Critical | **Composite**: 6.5 (Medium)

#### CVSS 3.1 Base

**Score**: 6.1 | **Vector**: `CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Network | Reachable over the network |
| Attack Complexity (AC) | Low | No special conditions |
| Privileges Required (PR) | None | No privileges needed |
| User Interaction (UI) | Required | A user must act |
| Scope (S) | Changed | Impact crosses a boundary |
| Confidentiality (C) | Low | Limited disclosure |
| Integrity (I) | Low | Limited modification |
| Availability (A) | None | No loss of service |

#### Exploitability

**Score**: 7.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 6 | Described in research |
| Attack Complexity | 6 | Needs some preparation |
| Tooling Availability | 7 | Common tools apply |
| Skill Level | 9 | Little skill needed |

#### Scalability

**Score**: 6.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 5 | Partly automatable |
| Target Scope | 5 | A class of targets |
| Resource Requirements | 8 | Minimal resources |
| Detection Difficulty | 6 | Detectable with monitoring |

#### Reachability

**Score**: 7.0 | **Trust Zone**: Agent Runtime Zone (Trusted)

planner-agent sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 7.0.

---

### LLM-5 — worker-2

**Threat**: worker-2 follows links and files named in work orders and route candidates, which turns a harmless-looking request into a fetch of attacker-controlled content.

**Category**: llm | **Original Risk Level**: High | **Composite**: 6.5 (Medium)

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

**Score**: 7.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 6 | Described in research |
| Attack Complexity | 8 | A single step suffices |
| Tooling Availability | 7 | Common tools apply |
| Skill Level | 9 | Little skill needed |

#### Scalability

**Score**: 7.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 6 | Partly automatable |
| Target Scope | 7 | Every instance |
| Resource Requirements | 7 | Minimal resources |
| Detection Difficulty | 8 | Blends with normal use |

#### Reachability

**Score**: 3.5 | **Trust Zone**: Agent Runtime Zone (Trusted)

worker-2 sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 3.5.

---

### LLM-7 — model-gateway

**Threat**: Indirect injection through documents retrieved for model-gateway lets the author of a retrieved page steer the answer without ever talking to the system.

**Category**: llm | **Original Risk Level**: Medium | **Composite**: 6.5 (Medium)

#### CVSS 3.1 Base

**Score**: 8.7 | **Vector**: —

#### Exploitability

**Score**: 7.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 6 | Described in research |
| Attack Complexity | 9 | A single step suffices |
| Tooling Availability | 5 | Tools need adaptation |
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

**Score**: 2.0 | **Trust Zone**: Agent Runtime Zone (Trusted)

model-gateway sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 2.0.

---

### S-1 — client-portal

**Threat**: An attacker replays a captured session cookie against client-portal, which does not bind the credential to the session or channel it was issued for, so the replay is accepted as the original caller.

**Category**: spoofing | **Original Risk Level**: Critical | **Composite**: 6.4 (Medium)

#### CVSS 3.1 Base

**Score**: 7.1 | **Vector**: `CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:L/A:N`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Network | Reachable over the network |
| Attack Complexity (AC) | Low | No special conditions |
| Privileges Required (PR) | None | No privileges needed |
| User Interaction (UI) | Required | A user must act |
| Scope (S) | Unchanged | Impact stays in the component |
| Confidentiality (C) | High | Broad disclosure |
| Integrity (I) | Low | Limited modification |
| Availability (A) | None | No loss of service |

#### Exploitability

**Score**: 7.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 8 | Documented and widely used |
| Attack Complexity | 7 | A single step suffices |
| Tooling Availability | 9 | Common tools apply |
| Skill Level | 6 | Intermediate skill |

#### Scalability

**Score**: 8.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 9 | Fully automatable |
| Target Scope | 6 | A class of targets |
| Resource Requirements | 10 | Minimal resources |
| Detection Difficulty | 9 | Blends with normal use |

#### Reachability

**Score**: 2.0 | **Trust Zone**: Public Internet (Untrusted)

client-portal sits in the Public Internet. The zone baseline is 9.0 and the refinement for this finding gives 2.0.

---

### E-8 — tool-server-1

**Threat**: A confused-deputy path lets a low-privilege caller ask tool-server-1 to act on tool call arguments and results using the privileges of audit-ledger.

**Category**: privilege-escalation | **Original Risk Level**: Low | **Composite**: 6.4 (Medium)

#### CVSS 3.1 Base

**Score**: 8.8 | **Vector**: `CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:H`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Network | Reachable over the network |
| Attack Complexity (AC) | Low | No special conditions |
| Privileges Required (PR) | None | No privileges needed |
| User Interaction (UI) | Required | A user must act |
| Scope (S) | Changed | Impact crosses a boundary |
| Confidentiality (C) | Low | Limited disclosure |
| Integrity (I) | Low | Limited modification |
| Availability (A) | High | Loss of service |

#### Exploitability

**Score**: 4.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 7 | Documented and widely used |
| Attack Complexity | 4 | Needs some preparation |
| Tooling Availability | 3 | Needs custom tooling |
| Skill Level | 4 | Intermediate skill |

#### Scalability

**Score**: 5.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 5 | Partly automatable |
| Target Scope | 5 | A class of targets |
| Resource Requirements | 9 | Minimal resources |
| Detection Difficulty | 3 | Readily detected |

#### Reachability

**Score**: 3.5 | **Trust Zone**: Agent Runtime Zone (Trusted)

tool-server-1 sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 3.5.

---

### AG-1 — intake-agent

**Threat**: Memory written by intake-agent is trusted on later runs, so one poisoned entry changes the behaviour of every future task.

**Category**: agentic | **Original Risk Level**: Medium | **Composite**: 6.4 (Medium)

#### CVSS 3.1 Base

**Score**: 9.6 | **Vector**: —

#### Exploitability

**Score**: 6.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 7 | Documented and widely used |
| Attack Complexity | 6 | Needs some preparation |
| Tooling Availability | 5 | Tools need adaptation |
| Skill Level | 6 | Intermediate skill |

#### Scalability

**Score**: 4.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 2 | Manual for each target |
| Target Scope | 4 | A class of targets |
| Resource Requirements | 7 | Minimal resources |
| Detection Difficulty | 5 | Detectable with monitoring |

#### Reachability

**Score**: 3.0 | **Trust Zone**: Agent Runtime Zone (Trusted)

intake-agent sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 3.0.

---

### OI-2 — intake-agent

**Threat**: Structured output from intake-agent is trusted by edge-gateway as already validated, so a malformed field flows straight into business logic.

**Category**: llm | **Original Risk Level**: High | **Composite**: 6.4 (Medium)

#### CVSS 3.1 Base

**Score**: 8.2 | **Vector**: —

#### Exploitability

**Score**: 7.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 7 | Documented and widely used |
| Attack Complexity | 6 | Needs some preparation |
| Tooling Availability | 6 | Tools need adaptation |
| Skill Level | 9 | Little skill needed |

#### Scalability

**Score**: 7.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 6 | Partly automatable |
| Target Scope | 8 | Every instance |
| Resource Requirements | 8 | Minimal resources |
| Detection Difficulty | 6 | Detectable with monitoring |

#### Reachability

**Score**: 2.0 | **Trust Zone**: Agent Runtime Zone (Trusted)

intake-agent sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 2.0.

---

### OI-4 — planner-agent

**Threat**: planner-agent emits URLs that downstream services fetch, so an attacker can make internal addresses part of the output and trigger server-side requests.

**Category**: llm | **Original Risk Level**: Medium | **Composite**: 6.4 (Medium)

#### CVSS 3.1 Base

**Score**: 8.3 | **Vector**: `CVSS:3.1/AV:P/AC:L/PR:L/UI:N/S:C/C:N/I:H/A:H`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Physical | Needs physical access |
| Attack Complexity (AC) | Low | No special conditions |
| Privileges Required (PR) | Low | A basic account is needed |
| User Interaction (UI) | None | No user action needed |
| Scope (S) | Changed | Impact crosses a boundary |
| Confidentiality (C) | None | No disclosure |
| Integrity (I) | High | Broad modification |
| Availability (A) | High | Loss of service |

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
| Scriptability | 6 | Partly automatable |
| Target Scope | 6 | A class of targets |
| Resource Requirements | 7 | Minimal resources |
| Detection Difficulty | 7 | Blends with normal use |

#### Reachability

**Score**: 3.0 | **Trust Zone**: Agent Runtime Zone (Trusted)

planner-agent sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 3.0.

---

### OI-8 — model-gateway

**Threat**: Markdown or HTML produced by model-gateway contains remote images that leak data when a client renders it.

**Category**: llm | **Original Risk Level**: High | **Composite**: 6.4 (Medium)

#### CVSS 3.1 Base

**Score**: 8.2 | **Vector**: `CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:L/A:N`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Network | Reachable over the network |
| Attack Complexity (AC) | Low | No special conditions |
| Privileges Required (PR) | None | No privileges needed |
| User Interaction (UI) | Required | A user must act |
| Scope (S) | Changed | Impact crosses a boundary |
| Confidentiality (C) | High | Broad disclosure |
| Integrity (I) | Low | Limited modification |
| Availability (A) | None | No loss of service |

#### Exploitability

**Score**: 6.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 6 | Described in research |
| Attack Complexity | 8 | A single step suffices |
| Tooling Availability | 6 | Tools need adaptation |
| Skill Level | 6 | Intermediate skill |

#### Scalability

**Score**: 6.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 8 | Fully automatable |
| Target Scope | 6 | A class of targets |
| Resource Requirements | 7 | Minimal resources |
| Detection Difficulty | 5 | Detectable with monitoring |

#### Reachability

**Score**: 3.0 | **Trust Zone**: Agent Runtime Zone (Trusted)

model-gateway sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 3.0.

---

### TE-6 — intake-agent

**Threat**: intake-agent adopts a persona that presents itself as a named colleague, so operators trust its suggestions more than its accuracy warrants.

**Category**: agentic | **Original Risk Level**: High | **Composite**: 6.3 (Medium)

#### CVSS 3.1 Base

**Score**: 8.5 | **Vector**: `CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:C/C:H/I:H/A:H`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Network | Reachable over the network |
| Attack Complexity (AC) | High | Needs specific conditions |
| Privileges Required (PR) | Low | A basic account is needed |
| User Interaction (UI) | None | No user action needed |
| Scope (S) | Changed | Impact crosses a boundary |
| Confidentiality (C) | High | Broad disclosure |
| Integrity (I) | High | Broad modification |
| Availability (A) | High | Loss of service |

#### Exploitability

**Score**: 6.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 7 | Documented and widely used |
| Attack Complexity | 6 | Needs some preparation |
| Tooling Availability | 5 | Tools need adaptation |
| Skill Level | 6 | Intermediate skill |

#### Scalability

**Score**: 5.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 3 | Manual for each target |
| Target Scope | 6 | A class of targets |
| Resource Requirements | 6 | Moderate resources |
| Detection Difficulty | 7 | Blends with normal use |

#### Reachability

**Score**: 3.5 | **Trust Zone**: Agent Runtime Zone (Trusted)

intake-agent sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 3.5.

---

### T-1 — edge-gateway

**Threat**: An attacker who can write to the channel between partner-sandbox and edge-gateway modifies inbound API requests in transit because messages carry no integrity protection of their own.

**Category**: tampering | **Original Risk Level**: Medium | **Composite**: 6.2 (Low)

#### CVSS 3.1 Base

**Score**: 5.2 | **Vector**: `CVSS:3.1/AV:N/AC:L/PR:H/UI:R/S:U/C:N/I:H/A:L`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Network | Reachable over the network |
| Attack Complexity (AC) | Low | No special conditions |
| Privileges Required (PR) | High | Administrative rights are needed |
| User Interaction (UI) | Required | A user must act |
| Scope (S) | Unchanged | Impact stays in the component |
| Confidentiality (C) | None | No disclosure |
| Integrity (I) | High | Broad modification |
| Availability (A) | Low | Degraded service |

#### Exploitability

**Score**: 6.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 9 | Documented and widely used |
| Attack Complexity | 6 | Needs some preparation |
| Tooling Availability | 5 | Tools need adaptation |
| Skill Level | 6 | Intermediate skill |

#### Scalability

**Score**: 7.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 7 | Fully automatable |
| Target Scope | 5 | A class of targets |
| Resource Requirements | 8 | Minimal resources |
| Detection Difficulty | 8 | Blends with normal use |

#### Reachability

**Score**: 7.0 | **Trust Zone**: Edge DMZ (Semi-trusted)

edge-gateway sits in the Edge DMZ. The zone baseline is 6.5 and the refinement for this finding gives 7.0.

---

### I-8 — vector-store-a

**Threat**: embedded documents and metadata held by vector-store-a are readable by any service in the Data Zone that shares the same network role, because access is granted by network position.

**Category**: info-disclosure | **Original Risk Level**: Medium | **Composite**: 6.2 (Medium)

#### CVSS 3.1 Base

**Score**: 7.1 | **Vector**: `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:L`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Network | Reachable over the network |
| Attack Complexity (AC) | Low | No special conditions |
| Privileges Required (PR) | Low | A basic account is needed |
| User Interaction (UI) | None | No user action needed |
| Scope (S) | Unchanged | Impact stays in the component |
| Confidentiality (C) | High | Broad disclosure |
| Integrity (I) | None | No modification |
| Availability (A) | Low | Degraded service |

#### Exploitability

**Score**: 8.8 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 9 | Documented and widely used |
| Attack Complexity | 9 | A single step suffices |
| Tooling Availability | 9 | Common tools apply |
| Skill Level | 8 | Little skill needed |

#### Scalability

**Score**: 3.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 4 | Partly automatable |
| Target Scope | 4 | A class of targets |
| Resource Requirements | 3 | Needs heavy infrastructure |
| Detection Difficulty | 3 | Readily detected |

#### Reachability

**Score**: 3.0 | **Trust Zone**: Data Zone (Trusted)

vector-store-a sits in the Data Zone. The zone baseline is 2.5 and the refinement for this finding gives 3.0.

---

### D-4 — planner-agent

**Threat**: A dependency of planner-agent becomes unavailable and the failure cascades because planner-agent waits on it synchronously for every request.

**Category**: denial-of-service | **Original Risk Level**: Critical | **Composite**: 6.2 (Low)

#### CVSS 3.1 Base

**Score**: 8.2 | **Vector**: `CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:H`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Network | Reachable over the network |
| Attack Complexity (AC) | Low | No special conditions |
| Privileges Required (PR) | None | No privileges needed |
| User Interaction (UI) | None | No user action needed |
| Scope (S) | Unchanged | Impact stays in the component |
| Confidentiality (C) | Low | Limited disclosure |
| Integrity (I) | None | No modification |
| Availability (A) | High | Loss of service |

#### Exploitability

**Score**: 6.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 9 | Documented and widely used |
| Attack Complexity | 6 | Needs some preparation |
| Tooling Availability | 5 | Tools need adaptation |
| Skill Level | 6 | Intermediate skill |

#### Scalability

**Score**: 6.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 8 | Fully automatable |
| Target Scope | 9 | Every instance |
| Resource Requirements | 4 | Moderate resources |
| Detection Difficulty | 3 | Readily detected |

#### Reachability

**Score**: 2.5 | **Trust Zone**: Agent Runtime Zone (Trusted)

planner-agent sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 2.5.

---

### D-7 — model-gateway

**Threat**: Unbounded growth of stored prompts and completions on model-gateway fills its volume, after which writes fail for every other consumer.

**Category**: denial-of-service | **Original Risk Level**: High | **Composite**: 6.2 (Medium)

#### CVSS 3.1 Base

**Score**: 5.3 | **Vector**: `CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Network | Reachable over the network |
| Attack Complexity (AC) | Low | No special conditions |
| Privileges Required (PR) | None | No privileges needed |
| User Interaction (UI) | None | No user action needed |
| Scope (S) | Unchanged | Impact stays in the component |
| Confidentiality (C) | None | No disclosure |
| Integrity (I) | None | No modification |
| Availability (A) | Low | Degraded service |

#### Exploitability

**Score**: 7.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 6 | Described in research |
| Attack Complexity | 7 | A single step suffices |
| Tooling Availability | 6 | Tools need adaptation |
| Skill Level | 9 | Little skill needed |

#### Scalability

**Score**: 5.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 10 | Fully automatable |
| Target Scope | 8 | Every instance |
| Resource Requirements | 3 | Needs heavy infrastructure |
| Detection Difficulty | 1 | Readily detected |

#### Reachability

**Score**: 7.0 | **Trust Zone**: Agent Runtime Zone (Trusted)

model-gateway sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 7.0.

---

### S-5 — intake-agent

**Threat**: Session fixation against intake-agent lets an attacker pre-seed an identifier and reuse the session after the victim authenticates.

**Category**: spoofing | **Original Risk Level**: High | **Composite**: 6.1 (Medium)

#### CVSS 3.1 Base

**Score**: 8.6 | **Vector**: `CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:L/A:L`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Network | Reachable over the network |
| Attack Complexity (AC) | Low | No special conditions |
| Privileges Required (PR) | None | No privileges needed |
| User Interaction (UI) | None | No user action needed |
| Scope (S) | Unchanged | Impact stays in the component |
| Confidentiality (C) | High | Broad disclosure |
| Integrity (I) | Low | Limited modification |
| Availability (A) | Low | Degraded service |

#### Exploitability

**Score**: 5.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 7 | Documented and widely used |
| Attack Complexity | 5 | Needs some preparation |
| Tooling Availability | 5 | Tools need adaptation |
| Skill Level | 5 | Intermediate skill |

#### Scalability

**Score**: 6.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 8 | Fully automatable |
| Target Scope | 6 | A class of targets |
| Resource Requirements | 9 | Minimal resources |
| Detection Difficulty | 3 | Readily detected |

#### Reachability

**Score**: 2.5 | **Trust Zone**: Agent Runtime Zone (Trusted)

intake-agent sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 2.5.

---

### I-5 — worker-2

**Threat**: Logs and traces emitted by worker-2 include raw work orders and route candidates, so anyone with access to the logging pipeline can read content meant for one tenant.

**Category**: info-disclosure | **Original Risk Level**: High | **Composite**: 6.1 (Medium)

#### CVSS 3.1 Base

**Score**: 7.5 | **Vector**: `CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:C/C:H/I:N/A:H`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Local | Needs local access |
| Attack Complexity (AC) | Low | No special conditions |
| Privileges Required (PR) | None | No privileges needed |
| User Interaction (UI) | Required | A user must act |
| Scope (S) | Changed | Impact crosses a boundary |
| Confidentiality (C) | High | Broad disclosure |
| Integrity (I) | None | No modification |
| Availability (A) | High | Loss of service |

#### Exploitability

**Score**: 7.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 8 | Documented and widely used |
| Attack Complexity | 8 | A single step suffices |
| Tooling Availability | 7 | Common tools apply |
| Skill Level | 7 | Little skill needed |

#### Scalability

**Score**: 6.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 6 | Partly automatable |
| Target Scope | 6 | A class of targets |
| Resource Requirements | 9 | Minimal resources |
| Detection Difficulty | 3 | Readily detected |

#### Reachability

**Score**: 1.5 | **Trust Zone**: Agent Runtime Zone (Trusted)

worker-2 sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 1.5.

---

### D-5 — worker-2

**Threat**: Retry storms from vector-store-a multiply the load on worker-2 when it slows down, turning a brief delay into a sustained outage.

**Category**: denial-of-service | **Original Risk Level**: Low | **Composite**: 6.1 (Medium)

#### CVSS 3.1 Base

**Score**: 7.2 | **Vector**: `CVSS:3.1/AV:A/AC:H/PR:H/UI:N/S:C/C:H/I:N/A:L`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Adjacent | Needs an adjacent network |
| Attack Complexity (AC) | High | Needs specific conditions |
| Privileges Required (PR) | High | Administrative rights are needed |
| User Interaction (UI) | None | No user action needed |
| Scope (S) | Changed | Impact crosses a boundary |
| Confidentiality (C) | High | Broad disclosure |
| Integrity (I) | None | No modification |
| Availability (A) | Low | Degraded service |

#### Exploitability

**Score**: 7.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 6 | Described in research |
| Attack Complexity | 8 | A single step suffices |
| Tooling Availability | 8 | Common tools apply |
| Skill Level | 8 | Little skill needed |

#### Scalability

**Score**: 6.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 8 | Fully automatable |
| Target Scope | 8 | Every instance |
| Resource Requirements | 6 | Moderate resources |
| Detection Difficulty | 2 | Readily detected |

#### Reachability

**Score**: 2.0 | **Trust Zone**: Agent Runtime Zone (Trusted)

worker-2 sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 2.0.

---

### E-5 — intake-agent

**Threat**: Role claims carried in the service token presented to intake-agent are honoured without confirmation against the authoritative directory.

**Category**: privilege-escalation | **Original Risk Level**: Critical | **Composite**: 6.1 (Medium)

#### CVSS 3.1 Base

**Score**: 8.5 | **Vector**: —

#### Exploitability

**Score**: 5.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 7 | Documented and widely used |
| Attack Complexity | 4 | Needs some preparation |
| Tooling Availability | 3 | Needs custom tooling |
| Skill Level | 6 | Intermediate skill |

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

intake-agent sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 3.0.

---

### AG-3 — planner-agent

**Threat**: planner-agent runs without a budget on steps or spend, so a loop or an adversarial task keeps it acting long after it stopped being useful.

**Category**: agentic | **Original Risk Level**: Critical | **Composite**: 6.1 (High)

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

**Score**: 4.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 6 | Described in research |
| Attack Complexity | 3 | Needs chained steps |
| Tooling Availability | 4 | Tools need adaptation |
| Skill Level | 5 | Intermediate skill |

#### Scalability

**Score**: 6.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 5 | Partly automatable |
| Target Scope | 6 | A class of targets |
| Resource Requirements | 6 | Moderate resources |
| Detection Difficulty | 7 | Blends with normal use |

#### Reachability

**Score**: 2.0 | **Trust Zone**: Agent Runtime Zone (Trusted)

planner-agent sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 2.0.

---

### AG-4 — planner-agent

**Threat**: Delegation from model-gateway to planner-agent carries the full authority of the original session, so a low-trust sub-task can use high-trust rights.

**Category**: agentic | **Original Risk Level**: Critical | **Composite**: 6.1 (Medium)

#### CVSS 3.1 Base

**Score**: 6.3 | **Vector**: `CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:L/I:H/A:N`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Network | Reachable over the network |
| Attack Complexity (AC) | Low | No special conditions |
| Privileges Required (PR) | Low | A basic account is needed |
| User Interaction (UI) | Required | A user must act |
| Scope (S) | Unchanged | Impact stays in the component |
| Confidentiality (C) | Low | Limited disclosure |
| Integrity (I) | High | Broad modification |
| Availability (A) | None | No loss of service |

#### Exploitability

**Score**: 5.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 7 | Documented and widely used |
| Attack Complexity | 3 | Needs chained steps |
| Tooling Availability | 5 | Tools need adaptation |
| Skill Level | 7 | Little skill needed |

#### Scalability

**Score**: 6.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 5 | Partly automatable |
| Target Scope | 3 | One specific target |
| Resource Requirements | 8 | Minimal resources |
| Detection Difficulty | 8 | Blends with normal use |

#### Reachability

**Score**: 6.5 | **Trust Zone**: Agent Runtime Zone (Trusted)

planner-agent sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 6.5.

---

### AG-9 — tool-server-1

**Threat**: tool-server-1 invokes tools with arguments assembled from model output, so an attacker who shapes the output can call a tool with parameters the designer never allowed.

**Category**: agentic | **Original Risk Level**: Medium | **Composite**: 6.1 (Medium)

#### CVSS 3.1 Base

**Score**: 7.9 | **Vector**: `CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:N`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Network | Reachable over the network |
| Attack Complexity (AC) | Low | No special conditions |
| Privileges Required (PR) | None | No privileges needed |
| User Interaction (UI) | None | No user action needed |
| Scope (S) | Changed | Impact crosses a boundary |
| Confidentiality (C) | High | Broad disclosure |
| Integrity (I) | High | Broad modification |
| Availability (A) | None | No loss of service |

#### Exploitability

**Score**: 4.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 5 | Described in research |
| Attack Complexity | 4 | Needs some preparation |
| Tooling Availability | 2 | Needs custom tooling |
| Skill Level | 5 | Intermediate skill |

#### Scalability

**Score**: 5.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 5 | Partly automatable |
| Target Scope | 4 | A class of targets |
| Resource Requirements | 7 | Minimal resources |
| Detection Difficulty | 6 | Detectable with monitoring |

#### Reachability

**Score**: 3.0 | **Trust Zone**: Agent Runtime Zone (Trusted)

tool-server-1 sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 3.0.

---

### LLM-3 — intake-agent

**Threat**: Encoded or multilingual payloads bypass the keyword filter in front of intake-agent, which only checks plain English text.

**Category**: llm | **Original Risk Level**: High | **Composite**: 6.1 (Medium)

#### CVSS 3.1 Base

**Score**: 7.5 | **Vector**: `CVSS:3.1/AV:A/AC:H/PR:H/UI:N/S:C/C:H/I:H/A:H`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Adjacent | Needs an adjacent network |
| Attack Complexity (AC) | High | Needs specific conditions |
| Privileges Required (PR) | High | Administrative rights are needed |
| User Interaction (UI) | None | No user action needed |
| Scope (S) | Changed | Impact crosses a boundary |
| Confidentiality (C) | High | Broad disclosure |
| Integrity (I) | High | Broad modification |
| Availability (A) | High | Loss of service |

#### Exploitability

**Score**: 7.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 6 | Described in research |
| Attack Complexity | 6 | Needs some preparation |
| Tooling Availability | 7 | Common tools apply |
| Skill Level | 9 | Little skill needed |

#### Scalability

**Score**: 7.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 6 | Partly automatable |
| Target Scope | 6 | A class of targets |
| Resource Requirements | 10 | Minimal resources |
| Detection Difficulty | 6 | Detectable with monitoring |

#### Reachability

**Score**: 1.5 | **Trust Zone**: Agent Runtime Zone (Trusted)

intake-agent sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 1.5.

---

### OI-9 — model-gateway

**Threat**: File paths or names produced by model-gateway are used to write files, letting crafted output reach locations outside the intended directory.

**Category**: llm | **Original Risk Level**: High | **Composite**: 6.1 (Medium)

#### CVSS 3.1 Base

**Score**: 7.1 | **Vector**: `CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:C/C:L/I:H/A:N`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Network | Reachable over the network |
| Attack Complexity (AC) | High | Needs specific conditions |
| Privileges Required (PR) | Low | A basic account is needed |
| User Interaction (UI) | None | No user action needed |
| Scope (S) | Changed | Impact crosses a boundary |
| Confidentiality (C) | Low | Limited disclosure |
| Integrity (I) | High | Broad modification |
| Availability (A) | None | No loss of service |

#### Exploitability

**Score**: 7.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 6 | Described in research |
| Attack Complexity | 7 | A single step suffices |
| Tooling Availability | 5 | Tools need adaptation |
| Skill Level | 10 | Little skill needed |

#### Scalability

**Score**: 7.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 6 | Partly automatable |
| Target Scope | 6 | A class of targets |
| Resource Requirements | 10 | Minimal resources |
| Detection Difficulty | 6 | Detectable with monitoring |

#### Reachability

**Score**: 2.5 | **Trust Zone**: Agent Runtime Zone (Trusted)

model-gateway sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 2.5.

---

### TE-9 — intake-agent

**Threat**: intake-agent claims certainty it does not have when summarising shipment risk, and customers rely on the stated confidence.

**Category**: agentic | **Original Risk Level**: High | **Composite**: 6.1 (Medium)

#### CVSS 3.1 Base

**Score**: 8.9 | **Vector**: `CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:L/A:H`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Local | Needs local access |
| Attack Complexity (AC) | Low | No special conditions |
| Privileges Required (PR) | None | No privileges needed |
| User Interaction (UI) | Required | A user must act |
| Scope (S) | Unchanged | Impact stays in the component |
| Confidentiality (C) | None | No disclosure |
| Integrity (I) | Low | Limited modification |
| Availability (A) | High | Loss of service |

#### Exploitability

**Score**: 5.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 7 | Documented and widely used |
| Attack Complexity | 6 | Needs some preparation |
| Tooling Availability | 3 | Needs custom tooling |
| Skill Level | 6 | Intermediate skill |

#### Scalability

**Score**: 4.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 2 | Manual for each target |
| Target Scope | 4 | A class of targets |
| Resource Requirements | 6 | Moderate resources |
| Detection Difficulty | 6 | Detectable with monitoring |

#### Reachability

**Score**: 3.5 | **Trust Zone**: Agent Runtime Zone (Trusted)

intake-agent sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 3.5.

---

### T-8 — model-gateway

**Threat**: Configuration of model-gateway can be rewritten by any service that holds the shared deployment credential, silently changing how prompts and completions are handled.

**Category**: tampering | **Original Risk Level**: High | **Composite**: 6.0 (Medium)

#### CVSS 3.1 Base

**Score**: 8.9 | **Vector**: `CVSS:3.1/AV:A/AC:L/PR:L/UI:N/S:C/C:L/I:L/A:L`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Adjacent | Needs an adjacent network |
| Attack Complexity (AC) | Low | No special conditions |
| Privileges Required (PR) | Low | A basic account is needed |
| User Interaction (UI) | None | No user action needed |
| Scope (S) | Changed | Impact crosses a boundary |
| Confidentiality (C) | Low | Limited disclosure |
| Integrity (I) | Low | Limited modification |
| Availability (A) | Low | Degraded service |

#### Exploitability

**Score**: 5.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 5 | Described in research |
| Attack Complexity | 6 | Needs some preparation |
| Tooling Availability | 4 | Tools need adaptation |
| Skill Level | 7 | Little skill needed |

#### Scalability

**Score**: 5.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 6 | Partly automatable |
| Target Scope | 5 | A class of targets |
| Resource Requirements | 8 | Minimal resources |
| Detection Difficulty | 3 | Readily detected |

#### Reachability

**Score**: 2.0 | **Trust Zone**: Agent Runtime Zone (Trusted)

model-gateway sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 2.0.

---

### R-2 — edge-gateway

**Threat**: Log entries from edge-gateway can be edited or deleted by the same operators who administer it, so evidence of misuse can be removed after the fact.

**Category**: repudiation | **Original Risk Level**: Note | **Composite**: 6.0 (Medium)

#### CVSS 3.1 Base

**Score**: 5.3 | **Vector**: `CVSS:3.1/AV:L/AC:H/PR:H/UI:R/S:C/C:L/I:N/A:H`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Local | Needs local access |
| Attack Complexity (AC) | High | Needs specific conditions |
| Privileges Required (PR) | High | Administrative rights are needed |
| User Interaction (UI) | Required | A user must act |
| Scope (S) | Changed | Impact crosses a boundary |
| Confidentiality (C) | Low | Limited disclosure |
| Integrity (I) | None | No modification |
| Availability (A) | High | Loss of service |

#### Exploitability

**Score**: 6.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 6 | Described in research |
| Attack Complexity | 6 | Needs some preparation |
| Tooling Availability | 5 | Tools need adaptation |
| Skill Level | 7 | Little skill needed |

#### Scalability

**Score**: 6.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 3 | Manual for each target |
| Target Scope | 6 | A class of targets |
| Resource Requirements | 8 | Minimal resources |
| Detection Difficulty | 9 | Blends with normal use |

#### Reachability

**Score**: 7.0 | **Trust Zone**: Edge DMZ (Semi-trusted)

edge-gateway sits in the Edge DMZ. The zone baseline is 6.5 and the refinement for this finding gives 7.0.

---

### LLM-6 — tool-server-1

**Threat**: Encoded or multilingual payloads bypass the keyword filter in front of tool-server-1, which only checks plain English text.

**Category**: llm | **Original Risk Level**: Medium | **Composite**: 6.0 (High)

#### CVSS 3.1 Base

**Score**: 7.1 | **Vector**: `CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:L/A:N`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Network | Reachable over the network |
| Attack Complexity (AC) | Low | No special conditions |
| Privileges Required (PR) | None | No privileges needed |
| User Interaction (UI) | Required | A user must act |
| Scope (S) | Unchanged | Impact stays in the component |
| Confidentiality (C) | High | Broad disclosure |
| Integrity (I) | Low | Limited modification |
| Availability (A) | None | No loss of service |

#### Exploitability

**Score**: 7.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 8 | Documented and widely used |
| Attack Complexity | 7 | A single step suffices |
| Tooling Availability | 5 | Tools need adaptation |
| Skill Level | 8 | Little skill needed |

#### Scalability

**Score**: 7.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 8 | Fully automatable |
| Target Scope | 6 | A class of targets |
| Resource Requirements | 8 | Minimal resources |
| Detection Difficulty | 8 | Blends with normal use |

#### Reachability

**Score**: 1.5 | **Trust Zone**: Agent Runtime Zone (Trusted)

tool-server-1 sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 1.5.

---

### OI-7 — worker-2

**Threat**: File paths or names produced by worker-2 are used to write files, letting crafted output reach locations outside the intended directory.

**Category**: llm | **Original Risk Level**: High | **Composite**: 6.0 (Medium)

#### CVSS 3.1 Base

**Score**: 8.4 | **Vector**: `CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:C/C:H/I:L/A:N`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Network | Reachable over the network |
| Attack Complexity (AC) | High | Needs specific conditions |
| Privileges Required (PR) | None | No privileges needed |
| User Interaction (UI) | Required | A user must act |
| Scope (S) | Changed | Impact crosses a boundary |
| Confidentiality (C) | High | Broad disclosure |
| Integrity (I) | Low | Limited modification |
| Availability (A) | None | No loss of service |

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
| Target Scope | 5 | A class of targets |
| Resource Requirements | 9 | Minimal resources |
| Detection Difficulty | 7 | Blends with normal use |

#### Reachability

**Score**: 2.5 | **Trust Zone**: Agent Runtime Zone (Trusted)

worker-2 sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 2.5.

---

### TE-5 — intake-agent

**Threat**: intake-agent speaks with an authoritative tone about customs and legal matters, and operators may defer to it without checking.

**Category**: agentic | **Original Risk Level**: Critical | **Composite**: 6.0 (Medium)

#### CVSS 3.1 Base

**Score**: 9.9 | **Vector**: `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:L`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Network | Reachable over the network |
| Attack Complexity (AC) | Low | No special conditions |
| Privileges Required (PR) | Low | A basic account is needed |
| User Interaction (UI) | None | No user action needed |
| Scope (S) | Changed | Impact crosses a boundary |
| Confidentiality (C) | High | Broad disclosure |
| Integrity (I) | High | Broad modification |
| Availability (A) | Low | Degraded service |

#### Exploitability

**Score**: 4.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 6 | Described in research |
| Attack Complexity | 4 | Needs some preparation |
| Tooling Availability | 3 | Needs custom tooling |
| Skill Level | 5 | Intermediate skill |

#### Scalability

**Score**: 6.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 5 | Partly automatable |
| Target Scope | 5 | A class of targets |
| Resource Requirements | 8 | Minimal resources |
| Detection Difficulty | 6 | Detectable with monitoring |

#### Reachability

**Score**: 3.0 | **Trust Zone**: Agent Runtime Zone (Trusted)

intake-agent sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 3.0.

---

### T-5 — planner-agent

**Threat**: Unsanitised task plans and tool selections reach planner-agent and are processed as trusted structure, so crafted input changes how later steps interpret the record.

**Category**: tampering | **Original Risk Level**: High | **Composite**: 5.9 (Medium)

#### CVSS 3.1 Base

**Score**: 7.1 | **Vector**: `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:L`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Network | Reachable over the network |
| Attack Complexity (AC) | Low | No special conditions |
| Privileges Required (PR) | Low | A basic account is needed |
| User Interaction (UI) | None | No user action needed |
| Scope (S) | Unchanged | Impact stays in the component |
| Confidentiality (C) | None | No disclosure |
| Integrity (I) | High | Broad modification |
| Availability (A) | Low | Degraded service |

#### Exploitability

**Score**: 6.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 7 | Documented and widely used |
| Attack Complexity | 7 | A single step suffices |
| Tooling Availability | 5 | Tools need adaptation |
| Skill Level | 5 | Intermediate skill |

#### Scalability

**Score**: 4.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 3 | Manual for each target |
| Target Scope | 5 | A class of targets |
| Resource Requirements | 5 | Moderate resources |
| Detection Difficulty | 3 | Readily detected |

#### Reachability

**Score**: 2.5 | **Trust Zone**: Agent Runtime Zone (Trusted)

planner-agent sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 2.5.

---

### D-3 — intake-agent

**Threat**: A single oversized or deeply nested payload makes intake-agent spend disproportionate memory and CPU parsing free-text shipment requests.

**Category**: denial-of-service | **Original Risk Level**: Medium | **Composite**: 5.9 (Medium)

#### CVSS 3.1 Base

**Score**: 6.5 | **Vector**: `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Network | Reachable over the network |
| Attack Complexity (AC) | Low | No special conditions |
| Privileges Required (PR) | Low | A basic account is needed |
| User Interaction (UI) | None | No user action needed |
| Scope (S) | Unchanged | Impact stays in the component |
| Confidentiality (C) | None | No disclosure |
| Integrity (I) | None | No modification |
| Availability (A) | High | Loss of service |

#### Exploitability

**Score**: 7.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 7 | Documented and widely used |
| Attack Complexity | 6 | Needs some preparation |
| Tooling Availability | 8 | Common tools apply |
| Skill Level | 9 | Little skill needed |

#### Scalability

**Score**: 6.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 10 | Fully automatable |
| Target Scope | 7 | Every instance |
| Resource Requirements | 4 | Moderate resources |
| Detection Difficulty | 3 | Readily detected |

#### Reachability

**Score**: 2.5 | **Trust Zone**: Agent Runtime Zone (Trusted)

intake-agent sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 2.5.

---

### E-7 — worker-2

**Threat**: Role claims carried in the worker credential presented to worker-2 are honoured without confirmation against the authoritative directory.

**Category**: privilege-escalation | **Original Risk Level**: Critical | **Composite**: 5.9 (High)

#### CVSS 3.1 Base

**Score**: 8.7 | **Vector**: `CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:L/I:H/A:H`

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

**Score**: 5.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 6 | Described in research |
| Attack Complexity | 5 | Needs some preparation |
| Tooling Availability | 6 | Tools need adaptation |
| Skill Level | 5 | Intermediate skill |

#### Scalability

**Score**: 5.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 7 | Fully automatable |
| Target Scope | 4 | A class of targets |
| Resource Requirements | 6 | Moderate resources |
| Detection Difficulty | 5 | Detectable with monitoring |

#### Reachability

**Score**: 2.0 | **Trust Zone**: Agent Runtime Zone (Trusted)

worker-2 sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 2.0.

---

### E-9 — model-gateway

**Threat**: Role claims carried in the model API key presented to model-gateway are honoured without confirmation against the authoritative directory.

**Category**: privilege-escalation | **Original Risk Level**: Medium | **Composite**: 5.9 (Medium)

#### CVSS 3.1 Base

**Score**: 8.9 | **Vector**: `CVSS:3.1/AV:P/AC:L/PR:H/UI:N/S:U/C:N/I:H/A:N`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Physical | Needs physical access |
| Attack Complexity (AC) | Low | No special conditions |
| Privileges Required (PR) | High | Administrative rights are needed |
| User Interaction (UI) | None | No user action needed |
| Scope (S) | Unchanged | Impact stays in the component |
| Confidentiality (C) | None | No disclosure |
| Integrity (I) | High | Broad modification |
| Availability (A) | None | No loss of service |

#### Exploitability

**Score**: 5.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 4 | Described in research |
| Attack Complexity | 7 | A single step suffices |
| Tooling Availability | 5 | Tools need adaptation |
| Skill Level | 4 | Intermediate skill |

#### Scalability

**Score**: 6.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 5 | Partly automatable |
| Target Scope | 6 | A class of targets |
| Resource Requirements | 8 | Minimal resources |
| Detection Difficulty | 5 | Detectable with monitoring |

#### Reachability

**Score**: 2.0 | **Trust Zone**: Agent Runtime Zone (Trusted)

model-gateway sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 2.0.

---

### TE-3 — intake-agent

**Threat**: intake-agent builds rapport over long sessions and starts to share unprompted details about earlier operators.

**Category**: agentic | **Original Risk Level**: Note | **Composite**: 5.9 (High)

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

**Score**: 5.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 4 | Described in research |
| Attack Complexity | 6 | Needs some preparation |
| Tooling Availability | 5 | Tools need adaptation |
| Skill Level | 5 | Intermediate skill |

#### Scalability

**Score**: 4.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 2 | Manual for each target |
| Target Scope | 3 | One specific target |
| Resource Requirements | 8 | Minimal resources |
| Detection Difficulty | 5 | Detectable with monitoring |

#### Reachability

**Score**: 2.5 | **Trust Zone**: Agent Runtime Zone (Trusted)

intake-agent sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 2.5.

---

### AGP-05 — worker-2

**Threat**: Messages between the planner and its workers travel over a shared channel with no per-sender signature, so a compromised participant can forge or replay instructions that other agents act on.

**Category**: agentic | **Original Risk Level**: Medium | **Composite**: 5.8 (Medium)

#### CVSS 3.1 Base

**Score**: 9.9 | **Vector**: —

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
| Scriptability | 2 | Manual for each target |
| Target Scope | 4 | A class of targets |
| Resource Requirements | 8 | Minimal resources |
| Detection Difficulty | 8 | Blends with normal use |

#### Reachability

**Score**: 1.5 | **Trust Zone**: Agent Runtime Zone (Trusted)

worker-2 sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 1.5.

---

### MI-5 — intake-agent

**Threat**: Outputs from intake-agent flow into decisions without a review step, so one wrong answer is repeated across many shipments.

**Category**: llm | **Original Risk Level**: Medium | **Composite**: 5.8 (Medium)

#### CVSS 3.1 Base

**Score**: 5.3 | **Vector**: `CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Adjacent | Needs an adjacent network |
| Attack Complexity (AC) | Low | No special conditions |
| Privileges Required (PR) | None | No privileges needed |
| User Interaction (UI) | None | No user action needed |
| Scope (S) | Unchanged | Impact stays in the component |
| Confidentiality (C) | High | Broad disclosure |
| Integrity (I) | High | Broad modification |
| Availability (A) | None | No loss of service |

#### Exploitability

**Score**: 7.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 7 | Documented and widely used |
| Attack Complexity | 6 | Needs some preparation |
| Tooling Availability | 7 | Common tools apply |
| Skill Level | 8 | Little skill needed |

#### Scalability

**Score**: 7.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 7 | Fully automatable |
| Target Scope | 6 | A class of targets |
| Resource Requirements | 9 | Minimal resources |
| Detection Difficulty | 8 | Blends with normal use |

#### Reachability

**Score**: 3.5 | **Trust Zone**: Agent Runtime Zone (Trusted)

intake-agent sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 3.5.

---

### TE-4 — intake-agent

**Threat**: intake-agent claims certainty it does not have when summarising shipment risk, and customers rely on the stated confidence.

**Category**: agentic | **Original Risk Level**: High | **Composite**: 5.8 (Medium)

#### CVSS 3.1 Base

**Score**: 8.3 | **Vector**: `CVSS:3.1/AV:L/AC:H/PR:N/UI:N/S:U/C:L/I:H/A:N`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Local | Needs local access |
| Attack Complexity (AC) | High | Needs specific conditions |
| Privileges Required (PR) | None | No privileges needed |
| User Interaction (UI) | None | No user action needed |
| Scope (S) | Unchanged | Impact stays in the component |
| Confidentiality (C) | Low | Limited disclosure |
| Integrity (I) | High | Broad modification |
| Availability (A) | None | No loss of service |

#### Exploitability

**Score**: 5.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 7 | Documented and widely used |
| Attack Complexity | 4 | Needs some preparation |
| Tooling Availability | 4 | Tools need adaptation |
| Skill Level | 5 | Intermediate skill |

#### Scalability

**Score**: 4.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 2 | Manual for each target |
| Target Scope | 4 | A class of targets |
| Resource Requirements | 8 | Minimal resources |
| Detection Difficulty | 4 | Detectable with monitoring |

#### Reachability

**Score**: 3.5 | **Trust Zone**: Agent Runtime Zone (Trusted)

intake-agent sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 3.5.

---

### R-3 — auth-broker

**Threat**: Delegated actions performed by auth-broker on behalf of a user are recorded under the service identity alone, hiding who authorised them.

**Category**: repudiation | **Original Risk Level**: Low | **Composite**: 5.7 (Medium)

#### CVSS 3.1 Base

**Score**: 4.7 | **Vector**: `CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:L/I:L/A:L`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Network | Reachable over the network |
| Attack Complexity (AC) | Low | No special conditions |
| Privileges Required (PR) | High | Administrative rights are needed |
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
| Attack Complexity | 7 | A single step suffices |
| Tooling Availability | 5 | Tools need adaptation |
| Skill Level | 4 | Intermediate skill |

#### Scalability

**Score**: 7.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 3 | Manual for each target |
| Target Scope | 6 | A class of targets |
| Resource Requirements | 10 | Minimal resources |
| Detection Difficulty | 9 | Blends with normal use |

#### Reachability

**Score**: 7.0 | **Trust Zone**: Edge DMZ (Semi-trusted)

auth-broker sits in the Edge DMZ. The zone baseline is 6.5 and the refinement for this finding gives 7.0.

---

### D-6 — tool-server-1

**Threat**: A burst of requests exhausts the connection pool of tool-server-1, which queues work without a bound and blocks legitimate use of tool call arguments and results.

**Category**: denial-of-service | **Original Risk Level**: Low | **Composite**: 5.7 (Medium)

#### CVSS 3.1 Base

**Score**: 6.5 | **Vector**: —

#### Exploitability

**Score**: 7.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 7 | Documented and widely used |
| Attack Complexity | 8 | A single step suffices |
| Tooling Availability | 6 | Tools need adaptation |
| Skill Level | 7 | Little skill needed |

#### Scalability

**Score**: 6.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 7 | Fully automatable |
| Target Scope | 8 | Every instance |
| Resource Requirements | 5 | Moderate resources |
| Detection Difficulty | 4 | Detectable with monitoring |

#### Reachability

**Score**: 2.0 | **Trust Zone**: Agent Runtime Zone (Trusted)

tool-server-1 sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 2.0.

---

### S-6 — planner-agent

**Threat**: An unauthenticated callback or health route on planner-agent accepts requests that downstream code treats as if they had come from model-gateway.

**Category**: spoofing | **Original Risk Level**: Low | **Composite**: 5.6 (Medium)

#### CVSS 3.1 Base

**Score**: 7.2 | **Vector**: `CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:N/A:N`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Network | Reachable over the network |
| Attack Complexity (AC) | High | Needs specific conditions |
| Privileges Required (PR) | None | No privileges needed |
| User Interaction (UI) | Required | A user must act |
| Scope (S) | Unchanged | Impact stays in the component |
| Confidentiality (C) | High | Broad disclosure |
| Integrity (I) | None | No modification |
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

**Score**: 6.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 7 | Fully automatable |
| Target Scope | 6 | A class of targets |
| Resource Requirements | 7 | Minimal resources |
| Detection Difficulty | 6 | Detectable with monitoring |

#### Reachability

**Score**: 3.0 | **Trust Zone**: Agent Runtime Zone (Trusted)

planner-agent sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 3.0.

---

### D-9 — audit-ledger

**Threat**: Expensive queries over approval and tool call records can be triggered by any authorised caller of audit-ledger, so one user can degrade the service for all.

**Category**: denial-of-service | **Original Risk Level**: Low | **Composite**: 5.6 (Medium)

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
| Scriptability | 9 | Fully automatable |
| Target Scope | 7 | Every instance |
| Resource Requirements | 5 | Moderate resources |
| Detection Difficulty | 3 | Readily detected |

#### Reachability

**Score**: 3.5 | **Trust Zone**: Operations Zone (Trusted)

audit-ledger sits in the Operations Zone. The zone baseline is 2.5 and the refinement for this finding gives 3.5.

---

### AGP-06 — tool-server-1

**Threat**: Interacting planning and routing agents amplify each other's outputs through feedback until their combined behaviour diverges from what any single agent was tested for, and per-agent safety checks never see the divergence.

**Category**: agentic | **Original Risk Level**: Medium | **Composite**: 5.6 (Medium)

#### CVSS 3.1 Base

**Score**: 8.9 | **Vector**: `CVSS:3.1/AV:A/AC:H/PR:L/UI:R/S:U/C:H/I:H/A:N`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Adjacent | Needs an adjacent network |
| Attack Complexity (AC) | High | Needs specific conditions |
| Privileges Required (PR) | Low | A basic account is needed |
| User Interaction (UI) | Required | A user must act |
| Scope (S) | Unchanged | Impact stays in the component |
| Confidentiality (C) | High | Broad disclosure |
| Integrity (I) | High | Broad modification |
| Availability (A) | None | No loss of service |

#### Exploitability

**Score**: 4.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 5 | Described in research |
| Attack Complexity | 3 | Needs chained steps |
| Tooling Availability | 5 | Tools need adaptation |
| Skill Level | 5 | Intermediate skill |

#### Scalability

**Score**: 5.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 5 | Partly automatable |
| Target Scope | 5 | A class of targets |
| Resource Requirements | 6 | Moderate resources |
| Detection Difficulty | 6 | Detectable with monitoring |

#### Reachability

**Score**: 1.5 | **Trust Zone**: Agent Runtime Zone (Trusted)

tool-server-1 sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 1.5.

---

### S-8 — tool-server-1

**Threat**: A shared or long-lived tool API key on tool-server-1 lets anyone who obtains one copy authenticate as every tenant that uses the same deployment profile.

**Category**: spoofing | **Original Risk Level**: High | **Composite**: 5.5 (Low)

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

**Score**: 5.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 5 | Described in research |
| Attack Complexity | 5 | Needs some preparation |
| Tooling Availability | 8 | Common tools apply |
| Skill Level | 4 | Intermediate skill |

#### Scalability

**Score**: 6.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 7 | Fully automatable |
| Target Scope | 4 | A class of targets |
| Resource Requirements | 8 | Minimal resources |
| Detection Difficulty | 5 | Detectable with monitoring |

#### Reachability

**Score**: 2.5 | **Trust Zone**: Agent Runtime Zone (Trusted)

tool-server-1 sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 2.5.

---

### T-6 — worker-2

**Threat**: An attacker who can write to the channel between vector-store-a and worker-2 modifies work orders and route candidates in transit because messages carry no integrity protection of their own.

**Category**: tampering | **Original Risk Level**: Low | **Composite**: 5.5 (Medium)

#### CVSS 3.1 Base

**Score**: 5.3 | **Vector**: `CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:N/I:H/A:L`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Local | Needs local access |
| Attack Complexity (AC) | High | Needs specific conditions |
| Privileges Required (PR) | Low | A basic account is needed |
| User Interaction (UI) | None | No user action needed |
| Scope (S) | Unchanged | Impact stays in the component |
| Confidentiality (C) | None | No disclosure |
| Integrity (I) | High | Broad modification |
| Availability (A) | Low | Degraded service |

#### Exploitability

**Score**: 5.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 5 | Described in research |
| Attack Complexity | 7 | A single step suffices |
| Tooling Availability | 4 | Tools need adaptation |
| Skill Level | 4 | Intermediate skill |

#### Scalability

**Score**: 3.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 5 | Partly automatable |
| Target Scope | 2 | One specific target |
| Resource Requirements | 5 | Moderate resources |
| Detection Difficulty | 2 | Readily detected |

#### Reachability

**Score**: 8.0 | **Trust Zone**: Agent Runtime Zone (Trusted)

worker-2 sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 8.0.

---

### T-9 — vector-store-a

**Threat**: Serialised objects arriving from worker-2 are deserialised by vector-store-a with permissive type handling, allowing crafted payloads to instantiate unintended behaviour.

**Category**: tampering | **Original Risk Level**: High | **Composite**: 5.5 (Medium)

#### CVSS 3.1 Base

**Score**: 6.5 | **Vector**: `CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:L`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Network | Reachable over the network |
| Attack Complexity (AC) | Low | No special conditions |
| Privileges Required (PR) | None | No privileges needed |
| User Interaction (UI) | None | No user action needed |
| Scope (S) | Unchanged | Impact stays in the component |
| Confidentiality (C) | None | No disclosure |
| Integrity (I) | Low | Limited modification |
| Availability (A) | Low | Degraded service |

#### Exploitability

**Score**: 5.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 6 | Described in research |
| Attack Complexity | 6 | Needs some preparation |
| Tooling Availability | 5 | Tools need adaptation |
| Skill Level | 5 | Intermediate skill |

#### Scalability

**Score**: 7.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 8 | Fully automatable |
| Target Scope | 8 | Every instance |
| Resource Requirements | 7 | Minimal resources |
| Detection Difficulty | 7 | Blends with normal use |

#### Reachability

**Score**: 2.5 | **Trust Zone**: Data Zone (Trusted)

vector-store-a sits in the Data Zone. The zone baseline is 2.5 and the refinement for this finding gives 2.5.

---

### I-6 — tool-server-1

**Threat**: Cross-tenant filters on tool-server-1 are applied in application code only, so one missing predicate exposes another tenant's tool call arguments and results.

**Category**: info-disclosure | **Original Risk Level**: Low | **Composite**: 5.5 (Medium)

#### CVSS 3.1 Base

**Score**: 9.7 | **Vector**: `CVSS:3.1/AV:N/AC:H/PR:H/UI:N/S:C/C:H/I:L/A:N`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Network | Reachable over the network |
| Attack Complexity (AC) | High | Needs specific conditions |
| Privileges Required (PR) | High | Administrative rights are needed |
| User Interaction (UI) | None | No user action needed |
| Scope (S) | Changed | Impact crosses a boundary |
| Confidentiality (C) | High | Broad disclosure |
| Integrity (I) | Low | Limited modification |
| Availability (A) | None | No loss of service |

#### Exploitability

**Score**: 6.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 5 | Described in research |
| Attack Complexity | 8 | A single step suffices |
| Tooling Availability | 7 | Common tools apply |
| Skill Level | 6 | Intermediate skill |

#### Scalability

**Score**: 5.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 5 | Partly automatable |
| Target Scope | 5 | A class of targets |
| Resource Requirements | 8 | Minimal resources |
| Detection Difficulty | 4 | Detectable with monitoring |

#### Reachability

**Score**: 2.0 | **Trust Zone**: Agent Runtime Zone (Trusted)

tool-server-1 sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 2.0.

---

### AG-2 — intake-agent

**Threat**: intake-agent retries failed actions on its own, repeating side effects such as bookings or messages when the first attempt partly succeeded.

**Category**: agentic | **Original Risk Level**: Critical | **Composite**: 5.5 (Medium)

#### CVSS 3.1 Base

**Score**: 8.3 | **Vector**: `CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:L/I:L/A:L`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Network | Reachable over the network |
| Attack Complexity (AC) | Low | No special conditions |
| Privileges Required (PR) | None | No privileges needed |
| User Interaction (UI) | None | No user action needed |
| Scope (S) | Changed | Impact crosses a boundary |
| Confidentiality (C) | Low | Limited disclosure |
| Integrity (I) | Low | Limited modification |
| Availability (A) | Low | Degraded service |

#### Exploitability

**Score**: 4.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 6 | Described in research |
| Attack Complexity | 3 | Needs chained steps |
| Tooling Availability | 2 | Needs custom tooling |
| Skill Level | 5 | Intermediate skill |

#### Scalability

**Score**: 4.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 3 | Manual for each target |
| Target Scope | 3 | One specific target |
| Resource Requirements | 7 | Minimal resources |
| Detection Difficulty | 5 | Detectable with monitoring |

#### Reachability

**Score**: 1.5 | **Trust Zone**: Agent Runtime Zone (Trusted)

intake-agent sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 1.5.

---

### AGP-04 — worker-2

**Threat**: State persisted across runs lets a sleeper instruction written today change the behaviour of a scheduled run weeks later, after the original entry has left review and the context that explained it is gone.

**Category**: agentic | **Original Risk Level**: Medium | **Composite**: 5.5 (Medium)

#### CVSS 3.1 Base

**Score**: 5.6 | **Vector**: `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:L/A:N`

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

**Score**: 4.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 5 | Described in research |
| Attack Complexity | 3 | Needs chained steps |
| Tooling Availability | 5 | Tools need adaptation |
| Skill Level | 5 | Intermediate skill |

#### Scalability

**Score**: 4.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 2 | Manual for each target |
| Target Scope | 4 | A class of targets |
| Resource Requirements | 6 | Moderate resources |
| Detection Difficulty | 6 | Detectable with monitoring |

#### Reachability

**Score**: 2.5 | **Trust Zone**: Agent Runtime Zone (Trusted)

worker-2 sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 2.5.

---

### OI-6 — worker-2

**Threat**: Markdown or HTML produced by worker-2 contains remote images that leak data when a client renders it.

**Category**: llm | **Original Risk Level**: Critical | **Composite**: 5.5 (Medium)

#### CVSS 3.1 Base

**Score**: 5.3 | **Vector**: `CVSS:3.1/AV:A/AC:L/PR:H/UI:N/S:C/C:H/I:H/A:N`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Adjacent | Needs an adjacent network |
| Attack Complexity (AC) | Low | No special conditions |
| Privileges Required (PR) | High | Administrative rights are needed |
| User Interaction (UI) | None | No user action needed |
| Scope (S) | Changed | Impact crosses a boundary |
| Confidentiality (C) | High | Broad disclosure |
| Integrity (I) | High | Broad modification |
| Availability (A) | None | No loss of service |

#### Exploitability

**Score**: 8.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 8 | Documented and widely used |
| Attack Complexity | 8 | A single step suffices |
| Tooling Availability | 7 | Common tools apply |
| Skill Level | 9 | Little skill needed |

#### Scalability

**Score**: 6.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 5 | Partly automatable |
| Target Scope | 7 | Every instance |
| Resource Requirements | 7 | Minimal resources |
| Detection Difficulty | 7 | Blends with normal use |

#### Reachability

**Score**: 1.5 | **Trust Zone**: Agent Runtime Zone (Trusted)

worker-2 sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 1.5.

---

### TE-1 — intake-agent

**Threat**: intake-agent adopts a persona that presents itself as a named colleague, so operators trust its suggestions more than its accuracy warrants.

**Category**: agentic | **Original Risk Level**: Medium | **Composite**: 5.5 (Medium)

#### CVSS 3.1 Base

**Score**: 8.9 | **Vector**: `CVSS:3.1/AV:A/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:L`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Adjacent | Needs an adjacent network |
| Attack Complexity (AC) | Low | No special conditions |
| Privileges Required (PR) | Low | A basic account is needed |
| User Interaction (UI) | None | No user action needed |
| Scope (S) | Changed | Impact crosses a boundary |
| Confidentiality (C) | High | Broad disclosure |
| Integrity (I) | High | Broad modification |
| Availability (A) | Low | Degraded service |

#### Exploitability

**Score**: 4.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 7 | Documented and widely used |
| Attack Complexity | 3 | Needs chained steps |
| Tooling Availability | 2 | Needs custom tooling |
| Skill Level | 6 | Intermediate skill |

#### Scalability

**Score**: 5.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 3 | Manual for each target |
| Target Scope | 4 | A class of targets |
| Resource Requirements | 6 | Moderate resources |
| Detection Difficulty | 7 | Blends with normal use |

#### Reachability

**Score**: 1.5 | **Trust Zone**: Agent Runtime Zone (Trusted)

intake-agent sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 1.5.

---

### TE-7 — intake-agent

**Threat**: Persuasive phrasing from intake-agent pushes operators to approve proposals quickly, which reduces careful review.

**Category**: agentic | **Original Risk Level**: Medium | **Composite**: 5.5 (Medium)

#### CVSS 3.1 Base

**Score**: 7.9 | **Vector**: —

#### Exploitability

**Score**: 5.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 6 | Described in research |
| Attack Complexity | 6 | Needs some preparation |
| Tooling Availability | 2 | Needs custom tooling |
| Skill Level | 6 | Intermediate skill |

#### Scalability

**Score**: 6.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 3 | Manual for each target |
| Target Scope | 6 | A class of targets |
| Resource Requirements | 9 | Minimal resources |
| Detection Difficulty | 8 | Blends with normal use |

#### Reachability

**Score**: 1.5 | **Trust Zone**: Agent Runtime Zone (Trusted)

intake-agent sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 1.5.

---

### T-4 — intake-agent

**Threat**: Replay of an earlier valid update to free-text shipment requests reaches intake-agent because updates carry no nonce or expiry, restoring a state the owner already corrected.

**Category**: tampering | **Original Risk Level**: High | **Composite**: 5.4 (Medium)

#### CVSS 3.1 Base

**Score**: 6.9 | **Vector**: `CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:H/A:L`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Network | Reachable over the network |
| Attack Complexity (AC) | Low | No special conditions |
| Privileges Required (PR) | Low | A basic account is needed |
| User Interaction (UI) | Required | A user must act |
| Scope (S) | Changed | Impact crosses a boundary |
| Confidentiality (C) | Low | Limited disclosure |
| Integrity (I) | High | Broad modification |
| Availability (A) | Low | Degraded service |

#### Exploitability

**Score**: 5.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 5 | Described in research |
| Attack Complexity | 7 | A single step suffices |
| Tooling Availability | 3 | Needs custom tooling |
| Skill Level | 5 | Intermediate skill |

#### Scalability

**Score**: 5.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 5 | Partly automatable |
| Target Scope | 4 | A class of targets |
| Resource Requirements | 8 | Minimal resources |
| Detection Difficulty | 3 | Readily detected |

#### Reachability

**Score**: 1.5 | **Trust Zone**: Agent Runtime Zone (Trusted)

intake-agent sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 1.5.

---

### AG-7 — worker-2

**Threat**: Tool calls made by worker-2 are not tied to the end user, so the tool server cannot tell whose authority a request carries.

**Category**: agentic | **Original Risk Level**: Medium | **Composite**: 5.4 (Medium)

#### CVSS 3.1 Base

**Score**: 8.9 | **Vector**: `CVSS:3.1/AV:A/AC:L/PR:N/UI:R/S:C/C:L/I:H/A:L`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Adjacent | Needs an adjacent network |
| Attack Complexity (AC) | Low | No special conditions |
| Privileges Required (PR) | None | No privileges needed |
| User Interaction (UI) | Required | A user must act |
| Scope (S) | Changed | Impact crosses a boundary |
| Confidentiality (C) | Low | Limited disclosure |
| Integrity (I) | High | Broad modification |
| Availability (A) | Low | Degraded service |

#### Exploitability

**Score**: 4.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 7 | Documented and widely used |
| Attack Complexity | 3 | Needs chained steps |
| Tooling Availability | 3 | Needs custom tooling |
| Skill Level | 5 | Intermediate skill |

#### Scalability

**Score**: 4.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 3 | Manual for each target |
| Target Scope | 4 | A class of targets |
| Resource Requirements | 7 | Minimal resources |
| Detection Difficulty | 4 | Detectable with monitoring |

#### Reachability

**Score**: 1.5 | **Trust Zone**: Agent Runtime Zone (Trusted)

worker-2 sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 1.5.

---

### AG-8 — tool-server-1

**Threat**: Memory written by tool-server-1 is trusted on later runs, so one poisoned entry changes the behaviour of every future task.

**Category**: agentic | **Original Risk Level**: Medium | **Composite**: 5.4 (Medium)

#### CVSS 3.1 Base

**Score**: 7.5 | **Vector**: `CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:C/C:H/I:L/A:H`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Network | Reachable over the network |
| Attack Complexity (AC) | High | Needs specific conditions |
| Privileges Required (PR) | Low | A basic account is needed |
| User Interaction (UI) | None | No user action needed |
| Scope (S) | Changed | Impact crosses a boundary |
| Confidentiality (C) | High | Broad disclosure |
| Integrity (I) | Low | Limited modification |
| Availability (A) | High | Loss of service |

#### Exploitability

**Score**: 5.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 6 | Described in research |
| Attack Complexity | 5 | Needs some preparation |
| Tooling Availability | 5 | Tools need adaptation |
| Skill Level | 6 | Intermediate skill |

#### Scalability

**Score**: 5.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 2 | Manual for each target |
| Target Scope | 4 | A class of targets |
| Resource Requirements | 7 | Minimal resources |
| Detection Difficulty | 7 | Blends with normal use |

#### Reachability

**Score**: 2.0 | **Trust Zone**: Agent Runtime Zone (Trusted)

tool-server-1 sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 2.0.

---

### AGP-01 — intake-agent

**Threat**: Operators and downstream agents start to accept worker output without checking it because earlier results were reliable, so one confidently stated wrong result passes straight into shipments and documents.

**Category**: agentic | **Original Risk Level**: Medium | **Composite**: 5.4 (High)

#### CVSS 3.1 Base

**Score**: 7.5 | **Vector**: `CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Network | Reachable over the network |
| Attack Complexity (AC) | High | Needs specific conditions |
| Privileges Required (PR) | Low | A basic account is needed |
| User Interaction (UI) | None | No user action needed |
| Scope (S) | Unchanged | Impact stays in the component |
| Confidentiality (C) | High | Broad disclosure |
| Integrity (I) | High | Broad modification |
| Availability (A) | High | Loss of service |

#### Exploitability

**Score**: 4.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 6 | Described in research |
| Attack Complexity | 4 | Needs some preparation |
| Tooling Availability | 2 | Needs custom tooling |
| Skill Level | 4 | Intermediate skill |

#### Scalability

**Score**: 6.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 6 | Partly automatable |
| Target Scope | 5 | A class of targets |
| Resource Requirements | 7 | Minimal resources |
| Detection Difficulty | 6 | Detectable with monitoring |

#### Reachability

**Score**: 3.5 | **Trust Zone**: Agent Runtime Zone (Trusted)

intake-agent sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 3.5.

---

### AGP-03 — planner-agent

**Threat**: Several agents compete for the same carrier rate and booking tools, and the heaviest user starves the others, so low priority work stalls or is retried until a limit is hit.

**Category**: agentic | **Original Risk Level**: Medium | **Composite**: 5.4 (Medium)

#### CVSS 3.1 Base

**Score**: 8.3 | **Vector**: `CVSS:3.1/AV:A/AC:H/PR:H/UI:R/S:C/C:L/I:N/A:N`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Adjacent | Needs an adjacent network |
| Attack Complexity (AC) | High | Needs specific conditions |
| Privileges Required (PR) | High | Administrative rights are needed |
| User Interaction (UI) | Required | A user must act |
| Scope (S) | Changed | Impact crosses a boundary |
| Confidentiality (C) | Low | Limited disclosure |
| Integrity (I) | None | No modification |
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
| Scriptability | 3 | Manual for each target |
| Target Scope | 5 | A class of targets |
| Resource Requirements | 6 | Moderate resources |
| Detection Difficulty | 4 | Detectable with monitoring |

#### Reachability

**Score**: 1.5 | **Trust Zone**: Agent Runtime Zone (Trusted)

planner-agent sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 1.5.

---

### S-7 — worker-2

**Threat**: A shared or long-lived worker credential on worker-2 lets anyone who obtains one copy authenticate as every tenant that uses the same deployment profile.

**Category**: spoofing | **Original Risk Level**: High | **Composite**: 5.3 (Medium)

#### CVSS 3.1 Base

**Score**: 4.9 | **Vector**: `CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:L/A:N`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Network | Reachable over the network |
| Attack Complexity (AC) | High | Needs specific conditions |
| Privileges Required (PR) | None | No privileges needed |
| User Interaction (UI) | None | No user action needed |
| Scope (S) | Unchanged | Impact stays in the component |
| Confidentiality (C) | High | Broad disclosure |
| Integrity (I) | Low | Limited modification |
| Availability (A) | None | No loss of service |

#### Exploitability

**Score**: 6.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 8 | Documented and widely used |
| Attack Complexity | 6 | Needs some preparation |
| Tooling Availability | 6 | Tools need adaptation |
| Skill Level | 4 | Intermediate skill |

#### Scalability

**Score**: 6.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 8 | Fully automatable |
| Target Scope | 5 | A class of targets |
| Resource Requirements | 6 | Moderate resources |
| Detection Difficulty | 5 | Detectable with monitoring |

#### Reachability

**Score**: 1.5 | **Trust Zone**: Agent Runtime Zone (Trusted)

worker-2 sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 1.5.

---

### AG-6 — worker-2

**Threat**: worker-2 retries failed actions on its own, repeating side effects such as bookings or messages when the first attempt partly succeeded.

**Category**: agentic | **Original Risk Level**: High | **Composite**: 5.2 (Medium)

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

**Score**: 3.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 5 | Described in research |
| Attack Complexity | 3 | Needs chained steps |
| Tooling Availability | 3 | Needs custom tooling |
| Skill Level | 3 | Needs deep expertise |

#### Scalability

**Score**: 5.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 2 | Manual for each target |
| Target Scope | 4 | A class of targets |
| Resource Requirements | 6 | Moderate resources |
| Detection Difficulty | 8 | Blends with normal use |

#### Reachability

**Score**: 1.5 | **Trust Zone**: Agent Runtime Zone (Trusted)

worker-2 sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 1.5.

---

### TE-2 — intake-agent

**Threat**: Persuasive phrasing from intake-agent pushes operators to approve proposals quickly, which reduces careful review.

**Category**: agentic | **Original Risk Level**: Medium | **Composite**: 5.1 (Medium)

#### CVSS 3.1 Base

**Score**: 9.4 | **Vector**: `CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:L/A:L`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Network | Reachable over the network |
| Attack Complexity (AC) | Low | No special conditions |
| Privileges Required (PR) | None | No privileges needed |
| User Interaction (UI) | Required | A user must act |
| Scope (S) | Unchanged | Impact stays in the component |
| Confidentiality (C) | Low | Limited disclosure |
| Integrity (I) | Low | Limited modification |
| Availability (A) | Low | Degraded service |

#### Exploitability

**Score**: 5.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 7 | Documented and widely used |
| Attack Complexity | 6 | Needs some preparation |
| Tooling Availability | 2 | Needs custom tooling |
| Skill Level | 7 | Little skill needed |

#### Scalability

**Score**: 6.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 5 | Partly automatable |
| Target Scope | 6 | A class of targets |
| Resource Requirements | 6 | Moderate resources |
| Detection Difficulty | 7 | Blends with normal use |

#### Reachability

**Score**: 1.5 | **Trust Zone**: Agent Runtime Zone (Trusted)

intake-agent sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 1.5.

---

### T-7 — tool-server-1

**Threat**: An update to tool-server-1 is pulled without provenance checks, so a poisoned package can alter how tool call arguments and results are handled at run time.

**Category**: tampering | **Original Risk Level**: Critical | **Composite**: 5.0 (Medium)

#### CVSS 3.1 Base

**Score**: 6.3 | **Vector**: —

#### Exploitability

**Score**: 4.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 4 | Described in research |
| Attack Complexity | 5 | Needs some preparation |
| Tooling Availability | 6 | Tools need adaptation |
| Skill Level | 3 | Needs deep expertise |

#### Scalability

**Score**: 5.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 6 | Partly automatable |
| Target Scope | 4 | A class of targets |
| Resource Requirements | 7 | Minimal resources |
| Detection Difficulty | 5 | Detectable with monitoring |

#### Reachability

**Score**: 3.0 | **Trust Zone**: Agent Runtime Zone (Trusted)

tool-server-1 sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 3.0.

---

### T-2 — vector-store-a

**Threat**: Backups and exports of embedded documents and metadata on vector-store-a are writable by operators without a second approver, so a malicious change survives restores.

**Category**: tampering | **Original Risk Level**: Medium | **Composite**: 4.9 (Medium)

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

**Score**: 4.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 4 | Described in research |
| Attack Complexity | 4 | Needs some preparation |
| Tooling Availability | 3 | Needs custom tooling |
| Skill Level | 5 | Intermediate skill |

#### Scalability

**Score**: 5.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 6 | Partly automatable |
| Target Scope | 3 | One specific target |
| Resource Requirements | 6 | Moderate resources |
| Detection Difficulty | 5 | Detectable with monitoring |

#### Reachability

**Score**: 3.0 | **Trust Zone**: Data Zone (Trusted)

vector-store-a sits in the Data Zone. The zone baseline is 2.5 and the refinement for this finding gives 3.0.

---

### R-10 — partner-sandbox

**Threat**: Failed and rejected attempts against partner-sandbox are not logged, so probing of trial manifests and recorded webhooks leaves no trace that an investigator could use.

**Category**: repudiation | **Original Risk Level**: Medium | **Composite**: 4.9 (Medium)

#### CVSS 3.1 Base

**Score**: 2.4 | **Vector**: `CVSS:3.1/AV:N/AC:L/PR:H/UI:R/S:U/C:N/I:L/A:N`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Network | Reachable over the network |
| Attack Complexity (AC) | Low | No special conditions |
| Privileges Required (PR) | High | Administrative rights are needed |
| User Interaction (UI) | Required | A user must act |
| Scope (S) | Unchanged | Impact stays in the component |
| Confidentiality (C) | None | No disclosure |
| Integrity (I) | Low | Limited modification |
| Availability (A) | None | No loss of service |

#### Exploitability

**Score**: 6.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 6 | Described in research |
| Attack Complexity | 6 | Needs some preparation |
| Tooling Availability | 6 | Tools need adaptation |
| Skill Level | 8 | Little skill needed |

#### Scalability

**Score**: 6.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 4 | Partly automatable |
| Target Scope | 6 | A class of targets |
| Resource Requirements | 8 | Minimal resources |
| Detection Difficulty | 8 | Blends with normal use |

#### Reachability

**Score**: 5.5 | **Trust Zone**: Partner Exchange (Semi-trusted)

partner-sandbox sits in the Partner Exchange. The zone baseline is 5.5 and the refinement for this finding gives 5.5.

---

### E-6 — planner-agent

**Threat**: planner-agent runs with broader permissions than its function needs, so a flaw in handling task plans and tool selections yields access to unrelated resources.

**Category**: privilege-escalation | **Original Risk Level**: Medium | **Composite**: 4.9 (Medium)

#### CVSS 3.1 Base

**Score**: 5.8 | **Vector**: `CVSS:3.1/AV:A/AC:H/PR:N/UI:N/S:C/C:H/I:H/A:L`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Adjacent | Needs an adjacent network |
| Attack Complexity (AC) | High | Needs specific conditions |
| Privileges Required (PR) | None | No privileges needed |
| User Interaction (UI) | None | No user action needed |
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
| Scriptability | 4 | Partly automatable |
| Target Scope | 5 | A class of targets |
| Resource Requirements | 9 | Minimal resources |
| Detection Difficulty | 4 | Detectable with monitoring |

#### Reachability

**Score**: 2.5 | **Trust Zone**: Agent Runtime Zone (Trusted)

planner-agent sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 2.5.

---

### R-8 — model-gateway

**Threat**: Failed and rejected attempts against model-gateway are not logged, so probing of prompts and completions leaves no trace that an investigator could use.

**Category**: repudiation | **Original Risk Level**: Medium | **Composite**: 4.8 (Medium)

#### CVSS 3.1 Base

**Score**: 6.5 | **Vector**: —

#### Exploitability

**Score**: 3.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 4 | Described in research |
| Attack Complexity | 4 | Needs some preparation |
| Tooling Availability | 3 | Needs custom tooling |
| Skill Level | 3 | Needs deep expertise |

#### Scalability

**Score**: 6.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 6 | Partly automatable |
| Target Scope | 3 | One specific target |
| Resource Requirements | 6 | Moderate resources |
| Detection Difficulty | 9 | Blends with normal use |

#### Reachability

**Score**: 3.0 | **Trust Zone**: Agent Runtime Zone (Trusted)

model-gateway sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 3.0.

---

### AGP-02 — planner-agent

**Threat**: Worker agents coordinate through the shared message bus and memory so that each stays under its individual limits while together they exceed the authority intended for any one of them, and no single-agent control observes the combined behaviour.

**Category**: agentic | **Original Risk Level**: Medium | **Composite**: 4.7 (Medium)

#### CVSS 3.1 Base

**Score**: 7.7 | **Vector**: `CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:C/C:H/I:H/A:L`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Local | Needs local access |
| Attack Complexity (AC) | High | Needs specific conditions |
| Privileges Required (PR) | Low | A basic account is needed |
| User Interaction (UI) | None | No user action needed |
| Scope (S) | Changed | Impact crosses a boundary |
| Confidentiality (C) | High | Broad disclosure |
| Integrity (I) | High | Broad modification |
| Availability (A) | Low | Degraded service |

#### Exploitability

**Score**: 4.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 5 | Described in research |
| Attack Complexity | 4 | Needs some preparation |
| Tooling Availability | 3 | Needs custom tooling |
| Skill Level | 4 | Intermediate skill |

#### Scalability

**Score**: 6.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 4 | Partly automatable |
| Target Scope | 6 | A class of targets |
| Resource Requirements | 9 | Minimal resources |
| Detection Difficulty | 5 | Detectable with monitoring |

#### Reachability

**Score**: 2.0 | **Trust Zone**: Agent Runtime Zone (Trusted)

planner-agent sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 2.0.

---

### R-9 — audit-ledger

**Threat**: Log entries from audit-ledger can be edited or deleted by the same operators who administer it, so evidence of misuse can be removed after the fact.

**Category**: repudiation | **Original Risk Level**: Medium | **Composite**: 4.6 (Medium)

#### CVSS 3.1 Base

**Score**: 3.5 | **Vector**: `CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:N/I:L/A:N`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Network | Reachable over the network |
| Attack Complexity (AC) | Low | No special conditions |
| Privileges Required (PR) | Low | A basic account is needed |
| User Interaction (UI) | Required | A user must act |
| Scope (S) | Unchanged | Impact stays in the component |
| Confidentiality (C) | None | No disclosure |
| Integrity (I) | Low | Limited modification |
| Availability (A) | None | No loss of service |

#### Exploitability

**Score**: 3.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 2 | Not described outside research |
| Attack Complexity | 5 | Needs some preparation |
| Tooling Availability | 1 | Needs custom tooling |
| Skill Level | 4 | Intermediate skill |

#### Scalability

**Score**: 6.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 6 | Partly automatable |
| Target Scope | 2 | One specific target |
| Resource Requirements | 9 | Minimal resources |
| Detection Difficulty | 7 | Blends with normal use |

#### Reachability

**Score**: 8.0 | **Trust Zone**: Operations Zone (Trusted)

audit-ledger sits in the Operations Zone. The zone baseline is 2.5 and the refinement for this finding gives 8.0.

---

### I-3 — intake-agent

**Threat**: A timing or size difference in the responses of intake-agent lets an observer infer whether specific records of free-text shipment requests exist.

**Category**: info-disclosure | **Original Risk Level**: Critical | **Composite**: 4.6 (Low)

#### CVSS 3.1 Base

**Score**: 3.7 | **Vector**: `CVSS:3.1/AV:N/AC:H/PR:L/UI:R/S:U/C:L/I:N/A:L`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Network | Reachable over the network |
| Attack Complexity (AC) | High | Needs specific conditions |
| Privileges Required (PR) | Low | A basic account is needed |
| User Interaction (UI) | Required | A user must act |
| Scope (S) | Unchanged | Impact stays in the component |
| Confidentiality (C) | Low | Limited disclosure |
| Integrity (I) | None | No modification |
| Availability (A) | Low | Degraded service |

#### Exploitability

**Score**: 6.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 8 | Documented and widely used |
| Attack Complexity | 6 | Needs some preparation |
| Tooling Availability | 7 | Common tools apply |
| Skill Level | 5 | Intermediate skill |

#### Scalability

**Score**: 5.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 5 | Partly automatable |
| Target Scope | 7 | Every instance |
| Resource Requirements | 6 | Moderate resources |
| Detection Difficulty | 2 | Readily detected |

#### Reachability

**Score**: 3.0 | **Trust Zone**: Agent Runtime Zone (Trusted)

intake-agent sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 3.0.

---

### T-10 — audit-ledger

**Threat**: An attacker who can write to the channel between tool-server-1 and audit-ledger modifies approval and tool call records in transit because messages carry no integrity protection of their own.

**Category**: tampering | **Original Risk Level**: High | **Composite**: 4.4 (Medium)

#### CVSS 3.1 Base

**Score**: 5.9 | **Vector**: `CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:N/I:H/A:L`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Network | Reachable over the network |
| Attack Complexity (AC) | High | Needs specific conditions |
| Privileges Required (PR) | Low | A basic account is needed |
| User Interaction (UI) | None | No user action needed |
| Scope (S) | Unchanged | Impact stays in the component |
| Confidentiality (C) | None | No disclosure |
| Integrity (I) | High | Broad modification |
| Availability (A) | Low | Degraded service |

#### Exploitability

**Score**: 4.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 5 | Described in research |
| Attack Complexity | 4 | Needs some preparation |
| Tooling Availability | 3 | Needs custom tooling |
| Skill Level | 4 | Intermediate skill |

#### Scalability

**Score**: 5.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 6 | Partly automatable |
| Target Scope | 4 | A class of targets |
| Resource Requirements | 5 | Moderate resources |
| Detection Difficulty | 5 | Detectable with monitoring |

#### Reachability

**Score**: 2.0 | **Trust Zone**: Operations Zone (Trusted)

audit-ledger sits in the Operations Zone. The zone baseline is 2.5 and the refinement for this finding gives 2.0.

---

### R-6 — worker-2

**Threat**: Operators approve changes to work orders and route candidates through a chat message or ticket comment that is not bound to the executed change, so approvals can be disputed.

**Category**: repudiation | **Original Risk Level**: Medium | **Composite**: 4.1 (Medium)

#### CVSS 3.1 Base

**Score**: 6.1 | **Vector**: `CVSS:3.1/AV:N/AC:L/PR:H/UI:R/S:C/C:N/I:N/A:N`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Network | Reachable over the network |
| Attack Complexity (AC) | Low | No special conditions |
| Privileges Required (PR) | High | Administrative rights are needed |
| User Interaction (UI) | Required | A user must act |
| Scope (S) | Changed | Impact crosses a boundary |
| Confidentiality (C) | None | No disclosure |
| Integrity (I) | None | No modification |
| Availability (A) | None | No loss of service |

#### Exploitability

**Score**: 3.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 4 | Described in research |
| Attack Complexity | 4 | Needs some preparation |
| Tooling Availability | 1 | Needs custom tooling |
| Skill Level | 3 | Needs deep expertise |

#### Scalability

**Score**: 4.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 4 | Partly automatable |
| Target Scope | 1 | One specific target |
| Resource Requirements | 8 | Minimal resources |
| Detection Difficulty | 5 | Detectable with monitoring |

#### Reachability

**Score**: 2.0 | **Trust Zone**: Agent Runtime Zone (Trusted)

worker-2 sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 2.0.

---

### I-7 — model-gateway

**Threat**: Cross-tenant filters on model-gateway are applied in application code only, so one missing predicate exposes another tenant's prompts and completions.

**Category**: info-disclosure | **Original Risk Level**: Note | **Composite**: 4.1 (Medium)

#### CVSS 3.1 Base

**Score**: 3.8 | **Vector**: —

#### Exploitability

**Score**: 5.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 5 | Described in research |
| Attack Complexity | 6 | Needs some preparation |
| Tooling Availability | 6 | Tools need adaptation |
| Skill Level | 5 | Intermediate skill |

#### Scalability

**Score**: 5.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 5 | Partly automatable |
| Target Scope | 4 | A class of targets |
| Resource Requirements | 7 | Minimal resources |
| Detection Difficulty | 4 | Detectable with monitoring |

#### Reachability

**Score**: 2.0 | **Trust Zone**: Agent Runtime Zone (Trusted)

model-gateway sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 2.0.

---

### R-4 — intake-agent

**Threat**: Clock drift between intake-agent and edge-gateway leaves events in inconsistent order, so the sequence of actions on free-text shipment requests cannot be reconstructed reliably.

**Category**: repudiation | **Original Risk Level**: High | **Composite**: 3.6 (Medium)

#### CVSS 3.1 Base

**Score**: 4.3 | **Vector**: `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:L`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Network | Reachable over the network |
| Attack Complexity (AC) | Low | No special conditions |
| Privileges Required (PR) | Low | A basic account is needed |
| User Interaction (UI) | None | No user action needed |
| Scope (S) | Unchanged | Impact stays in the component |
| Confidentiality (C) | None | No disclosure |
| Integrity (I) | None | No modification |
| Availability (A) | Low | Degraded service |

#### Exploitability

**Score**: 3.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 4 | Described in research |
| Attack Complexity | 4 | Needs some preparation |
| Tooling Availability | 1 | Needs custom tooling |
| Skill Level | 3 | Needs deep expertise |

#### Scalability

**Score**: 5.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 4 | Partly automatable |
| Target Scope | 1 | One specific target |
| Resource Requirements | 8 | Minimal resources |
| Detection Difficulty | 9 | Blends with normal use |

#### Reachability

**Score**: 2.0 | **Trust Zone**: Agent Runtime Zone (Trusted)

intake-agent sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 2.0.

---

### AG-5 — planner-agent

**Threat**: planner-agent does not limit the rate or total number of tool calls per task, so abuse of a costly tool goes unnoticed until the invoice arrives.

**Category**: agentic | **Original Risk Level**: High | **Composite**: 3.6 (Low)

#### CVSS 3.1 Base

**Score**: 3.7 | **Vector**: `CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:C/C:L/I:L/A:L`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Network | Reachable over the network |
| Attack Complexity (AC) | Low | No special conditions |
| Privileges Required (PR) | High | Administrative rights are needed |
| User Interaction (UI) | None | No user action needed |
| Scope (S) | Changed | Impact crosses a boundary |
| Confidentiality (C) | Low | Limited disclosure |
| Integrity (I) | Low | Limited modification |
| Availability (A) | Low | Degraded service |

#### Exploitability

**Score**: 4.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 4 | Described in research |
| Attack Complexity | 3 | Needs chained steps |
| Tooling Availability | 4 | Tools need adaptation |
| Skill Level | 5 | Intermediate skill |

#### Scalability

**Score**: 5.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 2 | Manual for each target |
| Target Scope | 6 | A class of targets |
| Resource Requirements | 7 | Minimal resources |
| Detection Difficulty | 5 | Detectable with monitoring |

#### Reachability

**Score**: 2.0 | **Trust Zone**: Agent Runtime Zone (Trusted)

planner-agent sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 2.0.

---

### R-7 — tool-server-1

**Threat**: Operators approve changes to tool call arguments and results through a chat message or ticket comment that is not bound to the executed change, so approvals can be disputed.

**Category**: repudiation | **Original Risk Level**: Low | **Composite**: 3.3 (Low)

#### CVSS 3.1 Base

**Score**: 3.5 | **Vector**: `CVSS:3.1/AV:A/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Adjacent | Needs an adjacent network |
| Attack Complexity (AC) | Low | No special conditions |
| Privileges Required (PR) | Low | A basic account is needed |
| User Interaction (UI) | None | No user action needed |
| Scope (S) | Unchanged | Impact stays in the component |
| Confidentiality (C) | None | No disclosure |
| Integrity (I) | Low | Limited modification |
| Availability (A) | None | No loss of service |

#### Exploitability

**Score**: 3.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 2 | Not described outside research |
| Attack Complexity | 5 | Needs some preparation |
| Tooling Availability | 1 | Needs custom tooling |
| Skill Level | 4 | Intermediate skill |

#### Scalability

**Score**: 5.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 3 | Manual for each target |
| Target Scope | 2 | One specific target |
| Resource Requirements | 7 | Minimal resources |
| Detection Difficulty | 8 | Blends with normal use |

#### Reachability

**Score**: 2.0 | **Trust Zone**: Agent Runtime Zone (Trusted)

tool-server-1 sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 2.0.

---

### R-5 — planner-agent

**Threat**: Clock drift between planner-agent and model-gateway leaves events in inconsistent order, so the sequence of actions on task plans and tool selections cannot be reconstructed reliably.

**Category**: repudiation | **Original Risk Level**: Low | **Composite**: 3.2 (Low)

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

**Score**: 2.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 2 | Not described outside research |
| Attack Complexity | 4 | Needs some preparation |
| Tooling Availability | 1 | Needs custom tooling |
| Skill Level | 3 | Needs deep expertise |

#### Scalability

**Score**: 5.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 4 | Partly automatable |
| Target Scope | 1 | One specific target |
| Resource Requirements | 9 | Minimal resources |
| Detection Difficulty | 8 | Blends with normal use |

#### Reachability

**Score**: 3.0 | **Trust Zone**: Agent Runtime Zone (Trusted)

planner-agent sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 3.0.

---

## 4. Governance Fields

Remediation tracking metadata for each scored finding. Defaults are severity-driven and intended for manual override during risk review.

| ID | Severity | Owner | SLA | Disposition | Review Date |
|----|----------|-------|-----|-------------|-------------|
| E-3 | High | Unassigned | 7d | Mitigate | 2026-11-16 |
| LLM-2 | High | Unassigned | 7d | Mitigate | 2026-11-16 |
| LLM-1 | High | Unassigned | 7d | Mitigate | 2026-11-16 |
| OI-5 | High | Unassigned | 7d | Mitigate | 2026-11-16 |
| S-3 | High | Unassigned | 7d | Mitigate | 2026-11-16 |
| MI-3 | High | Unassigned | 7d | Mitigate | 2026-11-16 |
| S-11 | High | Unassigned | 7d | Mitigate | 2026-11-16 |
| D-2 | High | Unassigned | 7d | Mitigate | 2026-11-16 |
| MI-2 | High | Unassigned | 7d | Mitigate | 2026-11-16 |
| S-4 | High | Unassigned | 7d | Mitigate | 2026-11-16 |
| S-9 | High | Unassigned | 7d | Mitigate | 2026-11-16 |
| D-1 | High | Unassigned | 7d | Mitigate | 2026-11-16 |
| LLM-9 | High | Unassigned | 7d | Mitigate | 2026-11-16 |
| E-1 | High | Unassigned | 7d | Mitigate | 2026-11-16 |
| I-2 | High | Unassigned | 7d | Mitigate | 2026-11-16 |
| E-4 | High | Unassigned | 7d | Mitigate | 2026-11-16 |
| T-3 | High | Unassigned | 7d | Mitigate | 2026-11-16 |
| I-1 | High | Unassigned | 7d | Mitigate | 2026-11-16 |
| I-4 | High | Unassigned | 7d | Mitigate | 2026-11-16 |
| AGP-07 | High | Unassigned | 7d | Mitigate | 2026-11-16 |
| MI-4 | High | Unassigned | 7d | Mitigate | 2026-11-16 |
| MI-8 | High | Unassigned | 7d | Mitigate | 2026-11-16 |
| S-2 | High | Unassigned | 7d | Mitigate | 2026-11-16 |
| D-8 | Medium | Unassigned | 30d | Review | 2026-12-09 |
| TE-8 | Medium | Unassigned | 30d | Review | 2026-12-09 |
| R-1 | Medium | Unassigned | 30d | Review | 2026-12-09 |
| E-2 | Medium | Unassigned | 30d | Review | 2026-12-09 |
| LLM-8 | Medium | Unassigned | 30d | Review | 2026-12-09 |
| OI-3 | High | Unassigned | 7d | Mitigate | 2026-11-16 |
| MI-1 | Medium | Unassigned | 30d | Review | 2026-12-09 |
| MI-7 | Medium | Unassigned | 30d | Review | 2026-12-09 |
| OI-1 | Medium | Unassigned | 30d | Review | 2026-12-09 |
| MI-9 | Medium | Unassigned | 30d | Review | 2026-12-09 |
| MI-6 | Low | Unassigned | 90d | Review | 2027-02-07 |
| S-10 | Medium | Unassigned | 30d | Review | 2026-12-09 |
| I-9 | Medium | Unassigned | 30d | Review | 2026-12-09 |
| LLM-4 | Medium | Unassigned | 30d | Review | 2026-12-09 |
| LLM-5 | Medium | Unassigned | 30d | Review | 2026-12-09 |
| LLM-7 | Medium | Unassigned | 30d | Review | 2026-12-09 |
| S-1 | Medium | Unassigned | 30d | Review | 2026-12-09 |
| E-8 | Medium | Unassigned | 30d | Review | 2026-12-09 |
| AG-1 | Medium | Unassigned | 30d | Review | 2026-12-09 |
| OI-2 | Medium | Unassigned | 30d | Review | 2026-12-09 |
| OI-4 | Medium | Unassigned | 30d | Review | 2026-12-09 |
| OI-8 | Medium | Unassigned | 30d | Review | 2026-12-09 |
| TE-6 | Medium | Unassigned | 30d | Review | 2026-12-09 |
| T-1 | Low | Unassigned | 90d | Review | 2027-02-07 |
| I-8 | Medium | Unassigned | 30d | Review | 2026-12-09 |
| D-4 | Low | Unassigned | 90d | Review | 2027-02-07 |
| D-7 | Medium | Unassigned | 30d | Review | 2026-12-09 |
| S-5 | Medium | Unassigned | 30d | Review | 2026-12-09 |
| I-5 | Medium | Unassigned | 30d | Review | 2026-12-09 |
| D-5 | Medium | Unassigned | 30d | Review | 2026-12-09 |
| E-5 | Medium | Unassigned | 30d | Review | 2026-12-09 |
| AG-3 | High | Unassigned | 7d | Mitigate | 2026-11-16 |
| AG-4 | Medium | Unassigned | 30d | Review | 2026-12-09 |
| AG-9 | Medium | Unassigned | 30d | Review | 2026-12-09 |
| LLM-3 | Medium | Unassigned | 30d | Review | 2026-12-09 |
| OI-9 | Medium | Unassigned | 30d | Review | 2026-12-09 |
| TE-9 | Medium | Unassigned | 30d | Review | 2026-12-09 |
| T-8 | Medium | Unassigned | 30d | Review | 2026-12-09 |
| R-2 | Medium | Unassigned | 30d | Review | 2026-12-09 |
| LLM-6 | High | Unassigned | 7d | Mitigate | 2026-11-16 |
| OI-7 | Medium | Unassigned | 30d | Review | 2026-12-09 |
| TE-5 | Medium | Unassigned | 30d | Review | 2026-12-09 |
| T-5 | Medium | Unassigned | 30d | Review | 2026-12-09 |
| D-3 | Medium | Unassigned | 30d | Review | 2026-12-09 |
| E-7 | High | Unassigned | 7d | Mitigate | 2026-11-16 |
| E-9 | Medium | Unassigned | 30d | Review | 2026-12-09 |
| TE-3 | High | Unassigned | 7d | Mitigate | 2026-11-16 |
| AGP-05 | Medium | Unassigned | 30d | Review | 2026-12-09 |
| MI-5 | Medium | Unassigned | 30d | Review | 2026-12-09 |
| TE-4 | Medium | Unassigned | 30d | Review | 2026-12-09 |
| R-3 | Medium | platform-team | 14d | Review | 2026-11-23 |
| D-6 | Medium | Unassigned | 30d | Review | 2026-12-09 |
| S-6 | Medium | Unassigned | 30d | Review | 2026-12-09 |
| D-9 | Medium | risk-office | 30d | Accept | 2026-12-09 |
| AGP-06 | Medium | Unassigned | 30d | Review | 2026-12-09 |
| S-8 | Low | Unassigned | 90d | Review | 2027-02-07 |
| T-6 | Medium | Unassigned | 30d | Review | 2026-12-09 |
| T-9 | Medium | Unassigned | 30d | Review | 2026-12-09 |
| I-6 | Medium | Unassigned | 30d | Review | 2026-12-09 |
| AG-2 | Medium | Unassigned | 30d | Review | 2026-12-09 |
| AGP-04 | Medium | Unassigned | 30d | Review | 2026-12-09 |
| OI-6 | Medium | Unassigned | 30d | Review | 2026-12-09 |
| TE-1 | Medium | Unassigned | 30d | Review | 2026-12-09 |
| TE-7 | Medium | Unassigned | 30d | Review | 2026-12-09 |
| T-4 | Medium | Unassigned | 30d | Review | 2026-12-09 |
| AG-7 | Medium | Unassigned | 30d | Review | 2026-12-09 |
| AG-8 | Medium | Unassigned | 30d | Review | 2026-12-09 |
| AGP-01 | High | Unassigned | 7d | Mitigate | 2026-11-16 |
| AGP-03 | Medium | Unassigned | 30d | Review | 2026-12-09 |
| S-7 | Medium | Unassigned | 30d | Review | 2026-12-09 |
| AG-6 | Medium | Unassigned | 30d | Review | 2026-12-09 |
| TE-2 | Medium | Unassigned | 30d | Review | 2026-12-09 |
| T-7 | Medium | Unassigned | 30d | Review | 2026-12-09 |
| T-2 | Medium | Unassigned | 30d | Review | 2026-12-09 |
| R-10 | Medium | Unassigned | 30d | Review | 2026-12-09 |
| E-6 | Medium | Unassigned | 30d | Review | 2026-12-09 |
| R-8 | Medium | Unassigned | 30d | Review | 2026-12-09 |
| AGP-02 | Medium | Unassigned | 30d | Review | 2026-12-09 |
| R-9 | Medium | Unassigned | 30d | Review | 2026-12-09 |
| I-3 | Low | Unassigned | 90d | Review | 2027-02-07 |
| T-10 | Medium | Unassigned | 30d | Review | 2026-12-09 |
| R-6 | Medium | Unassigned | 30d | Review | 2026-12-09 |
| I-7 | Medium | Unassigned | 30d | Review | 2026-12-09 |
| R-4 | Medium | Unassigned | 30d | Review | 2026-12-09 |
| AG-5 | Low | Unassigned | 90d | Review | 2027-02-07 |
| R-7 | Low | Unassigned | 90d | Review | 2027-02-07 |
| R-5 | Low | Unassigned | 90d | Review | 2027-02-07 |

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
