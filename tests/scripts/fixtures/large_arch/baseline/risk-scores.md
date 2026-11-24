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

**408** threats scored | **1** Critical | **38** High | **336** Medium | **33** Low

**Highest-Risk Component**: partner-feed — 3 finding(s), max composite 9.1

| Metric | Value |
|--------|-------|
| Scoring date | 2026-10-20 |
| Source file | `baseline/threats.md` |
| Schema version | 1.0 |

**Severity Distribution:**

| Severity | Count | Percentage |
|----------|-------|------------|
| Critical | 1 | 0.2% |
| High | 38 | 9.3% |
| Medium | 336 | 82.4% |
| Low | 33 | 8.1% |
| **Total** | **408** | **100%** |

> Trust zone data was available for every component, so no reachability value was defaulted.

---

## 2. Scored Threat Table

Findings sorted by Composite score descending (highest risk first). Boundary values map to the higher severity band.

| ID | Source | Component | Threat | CVSS | Exploit. | Scale. | Reach. | Composite | Severity | SLA | Disposition |
|----|--------|-----------|--------|------|----------|--------|--------|-----------|----------|-----|-------------|
| S-3 | fresh | partner-feed | A shared or long-lived webhook signature on partner-feed... | 9.1 | 9.0 | 9.0 | 9.5 | 9.1 | Critical | 24h | Mitigate |
| S-1 | fresh | client-portal | An attacker replays a captured session cookie against... | 9.9 | 7.5 | 7.5 | 8.5 | 8.5 | High | 7d | Mitigate |
| S-2 | fresh | partner-feed | A compromised peer presents a forged service identity to... | 7.6 | 8.0 | 7.5 | 10.0 | 8.2 | High | 7d | Mitigate |
| S-4 | fresh | edge-gateway | A shared or long-lived bearer token on edge-gateway lets... | 8.1 | 8.5 | 8.5 | 7.0 | 8.1 | High | 7d | Mitigate |
| LLM-3 | fresh | edge-gateway | An attacker splits a payload across several messages so that... | 8.2 | 8.5 | 9.0 | 6.5 | 8.1 | High | 7d | Mitigate |
| E-3 | fresh | edge-gateway | An administrative interface of edge-gateway is reachable... | 9.3 | 7.0 | 8.0 | 7.0 | 8.0 | High | 7d | Mitigate |
| E-4 | fresh | edge-gateway | edge-gateway runs with broader permissions than its function... | 9.9 | 7.5 | 7.5 | 6.0 | 8.0 | High | 7d | Mitigate |
| D-1 | fresh | edge-gateway | A dependency of edge-gateway becomes unavailable and the... | 8.2 | 9.5 | 7.0 | 5.5 | 7.9 | High | 7d | Mitigate |
| S-5 | fresh | auth-broker | A shared or long-lived refresh token on auth-broker lets... | 7.4 | 9.0 | 8.0 | 5.5 | 7.6 | High | 7d | Mitigate |
| E-5 | fresh | auth-broker | Role claims carried in the refresh token presented to... | 9.0 | 7.5 | 7.5 | 5.5 | 7.6 | High | 7d | Mitigate |
| T-1 | fresh | edge-gateway | An attacker who can write to the channel between... | 8.6 | 7.0 | 6.5 | 7.0 | 7.5 | High | 7d | Mitigate |
| E-1 | fresh | edge-gateway | Object identifiers in requests to edge-gateway are trusted... | 8.2 | 7.5 | 7.0 | 6.5 | 7.5 | High | 7d | Mitigate |
| E-2 | fresh | edge-gateway | Role claims carried in the bearer token presented to... | 9.1 | 7.0 | 7.0 | 6.0 | 7.5 | High | 7d | Mitigate |
| LLM-34 | fresh | memory-store | A delayed trigger planted in task history and operator... | 9.3 | 8.5 | 6.5 | 3.5 | 7.5 | High | 7d | Mitigate |
| I-4 | fresh | auth-broker | credential assertions and session grants held by auth-broker... | 6.5 | 8.5 | 8.0 | 7.0 | 7.4 | High | 7d | Mitigate |
| D-3 | fresh | auth-broker | Retry storms from edge-gateway multiply the load on... | 6.3 | 9.0 | 8.0 | 6.5 | 7.4 | High | 7d | Mitigate |
| LLM-50 | fresh | eval-runner | Records written into eval-runner by low-trust sources are... | 10.0 | 8.0 | 7.5 | 2.0 | 7.4 | High | 7d | Mitigate |
| LLM-11 | fresh | router-agent | Prompt content logged by planner-agent is later replayed to... | 8.7 | 8.5 | 6.5 | 3.5 | 7.3 | High | 7d | Mitigate |
| D-2 | fresh | auth-broker | A single oversized or deeply nested payload makes... | 6.4 | 9.0 | 7.0 | 6.0 | 7.2 | High | 7d | Mitigate |
| OI-8 | fresh | intake-agent | Structured output from intake-agent is trusted by... | 9.3 | 7.5 | 7.0 | 3.0 | 7.2 | High | 7d | Mitigate |
| OI-12 | fresh | planner-agent | File paths or names produced by planner-agent are used to... | 9.3 | 8.5 | 6.5 | 2.0 | 7.2 | High | 7d | Mitigate |
| S-40 | fresh | edge-gateway | An unauthenticated callback or health route on edge-gateway... | 6.5 | 8.5 | 8.0 | 5.5 | 7.1 | High | 7d | Mitigate |
| I-1 | fresh | edge-gateway | Secrets such as the bearer token for edge-gateway appear in... | 6.3 | 9.0 | 7.5 | 5.5 | 7.1 | High | 7d | Mitigate |
| I-2 | fresh | edge-gateway | Verbose error responses from edge-gateway reveal internal... | 6.3 | 9.0 | 7.5 | 5.5 | 7.1 | High | 7d | Mitigate |
| I-43 | fresh | edge-gateway | Logs and traces emitted by edge-gateway include raw inbound... | 6.3 | 7.5 | 8.0 | 7.0 | 7.1 | High | 7d | Mitigate |
| LLM-1 | fresh | edge-gateway | edge-gateway passes conversation history from earlier turns... | 6.3 | 9.0 | 7.5 | 5.5 | 7.1 | High | 7d | Mitigate |
| LLM-2 | fresh | edge-gateway | Prompt content logged by client-portal is later replayed to... | 6.3 | 9.0 | 7.5 | 5.5 | 7.1 | High | 7d | Mitigate |
| LLM-18 | fresh | tool-server-1 | tool-server-1 passes conversation history from earlier turns... | 9.3 | 7.0 | 7.0 | 3.5 | 7.1 | High | 7d | Mitigate |
| LLM-41 | fresh | trace-collector | A user message crafted to look like a system directive... | 9.3 | 7.5 | 7.0 | 2.5 | 7.1 | High | 7d | Mitigate |
| LLM-47 | fresh | eval-runner | Anyone who can write to the ingestion path of eval-runner... | 8.7 | 7.5 | 7.0 | 4.0 | 7.1 | High | 7d | Mitigate |
| LLM-48 | fresh | eval-runner | Evaluation labels consumed from eval-runner are produced by... | 9.9 | 6.5 | 6.5 | 3.5 | 7.1 | High | 7d | Mitigate |
| OI-6 | fresh | intake-agent | Text generated by intake-agent is placed into a database... | 8.2 | 8.0 | 7.5 | 3.5 | 7.1 | High | 7d | Mitigate |
| OI-15 | fresh | worker-2 | File paths or names produced by worker-2 are used to write... | 8.8 | 7.5 | 7.0 | 3.5 | 7.1 | High | 7d | Mitigate |
| OI-16 | fresh | worker-2 | Model output from worker-2 is inserted into a rendered page... | 8.9 | 7.5 | 7.5 | 3.0 | 7.1 | High | 7d | Mitigate |
| OI-18 | fresh | model-gateway | Markdown or HTML produced by model-gateway contains remote... | 8.2 | 8.0 | 7.5 | 3.5 | 7.1 | High | 7d | Mitigate |
| OI-20 | fresh | model-gateway | Model output from model-gateway is inserted into a rendered... | 8.9 | 7.5 | 7.5 | 3.0 | 7.1 | High | 7d | Mitigate |
| OI-21 | fresh | summarizer-llm | Text generated by summarizer-llm is placed into a database... | 8.7 | 7.5 | 7.0 | 4.0 | 7.1 | High | 7d | Mitigate |
| OI-26 | fresh | planner-agent | Text generated by planner-agent is placed into a database... | 8.2 | 7.5 | 8.0 | 4.0 | 7.1 | High | 7d | Mitigate |
| OI-28 | fresh | summarizer-llm | Model output from summarizer-llm is inserted into a rendered... | 10.0 | 7.5 | 7.0 | 1.5 | 7.1 | High | 7d | Mitigate |
| S-33 | fresh | trace-collector | A shared or long-lived collector token on trace-collector... | 8.2 | 8.0 | 6.5 | 3.5 | 6.9 | Medium | 30d | Review |
| LLM-5 | fresh | intake-agent | intake-agent passes conversation history from earlier turns... | 8.7 | 7.5 | 6.5 | 3.0 | 6.9 | Medium | 30d | Review |
| LLM-10 | fresh | router-agent | router-agent passes conversation history from earlier turns... | 8.9 | 7.0 | 7.0 | 3.0 | 6.9 | Medium | 30d | Review |
| LLM-57 | fresh | summarizer-llm | Instructions hidden in shipment records fed into summaries... | 8.9 | 7.5 | 7.0 | 2.5 | 6.9 | Medium | 30d | Review |
| LLM-58 | fresh | summarizer-llm | A user message crafted to look like a system directive... | 8.2 | 8.0 | 6.5 | 3.5 | 6.9 | Medium | 30d | Review |
| OI-7 | fresh | intake-agent | intake-agent emits URLs that downstream services fetch, so... | 8.5 | 8.5 | 7.0 | 1.5 | 6.9 | Medium | 30d | Review |
| OI-14 | fresh | worker-2 | Markdown or HTML produced by worker-2 contains remote images... | 8.2 | 8.0 | 7.0 | 3.0 | 6.9 | Medium | 30d | Review |
| MI-4 | fresh | intake-agent | Confident wording from intake-agent hides low retrieval... | 9.3 | 7.0 | 8.0 | 1.5 | 6.9 | Medium | 30d | Review |
| MI-9 | fresh | reviewer-agent | reviewer-agent fabricates reference numbers and clause... | 8.2 | 7.5 | 7.0 | 3.5 | 6.9 | Medium | 30d | Review |
| MI-10 | fresh | summarizer-llm | summarizer-llm fabricates reference numbers and clause... | 8.7 | 8.0 | 7.0 | 2.0 | 6.9 | Medium | 30d | Review |
| LLM-6 | fresh | intake-agent | Prompt content logged by edge-gateway is later replayed to... | 9.6 | 7.0 | 7.0 | 1.5 | 6.8 | Medium | 30d | Review |
| LLM-27 | fresh | summarizer-llm | Evaluation labels consumed from summarizer-llm are produced... | 9.3 | 7.0 | 7.0 | 2.0 | 6.8 | Medium | 30d | Review |
| OI-9 | fresh | planner-agent | planner-agent emits URLs that downstream services fetch, so... | 9.3 | 7.0 | 7.0 | 2.0 | 6.8 | Medium | 30d | Review |
| OI-22 | fresh | summarizer-llm | summarizer-llm emits URLs that downstream services fetch, so... | 8.2 | 8.0 | 6.5 | 3.0 | 6.8 | Medium | 30d | Review |
| MI-2 | fresh | intake-agent | Stale data in the knowledge base lets intake-agent present... | 9.3 | 7.0 | 6.0 | 2.5 | 6.8 | Medium | 30d | Review |
| MI-8 | fresh | reviewer-agent | Outputs from reviewer-agent flow into decisions without a... | 8.0 | 8.0 | 6.5 | 3.0 | 6.8 | Medium | 30d | Review |
| D-36 | fresh | auth-broker | A slow-read attack holds connections to auth-broker open and... | 5.3 | 8.0 | 7.5 | 6.5 | 6.7 | Medium | 30d | Review |
| LLM-43 | fresh | trace-collector | A delayed trigger planted in prompts, completions and tool... | 9.3 | 7.0 | 7.0 | 1.5 | 6.7 | Medium | 30d | Review |
| OI-4 | fresh | intake-agent | File paths or names produced by intake-agent are used to... | 8.1 | 8.0 | 7.0 | 2.0 | 6.7 | Medium | 30d | Review |
| MI-11 | fresh | summarizer-llm | Stale data in the knowledge base lets summarizer-llm present... | 9.3 | 6.0 | 7.0 | 3.0 | 6.7 | Medium | 30d | Review |
| S-9 | fresh | planner-agent | Session fixation against planner-agent lets an attacker... | 9.3 | 7.0 | 6.5 | 1.5 | 6.6 | Medium | 30d | Review |
| I-3 | fresh | edge-gateway | inbound API requests held by edge-gateway are readable by... | 5.5 | 7.5 | 7.0 | 7.0 | 6.6 | Medium | 30d | Review |
| I-5 | fresh | auth-broker | Logs and traces emitted by auth-broker include raw... | 5.5 | 7.5 | 7.5 | 6.5 | 6.6 | Medium | 30d | Review |
| D-7 | fresh | planner-agent | A dependency of planner-agent becomes unavailable and the... | 8.2 | 7.0 | 6.0 | 3.5 | 6.6 | Medium | 30d | Review |
| D-8 | fresh | planner-agent | Expensive queries over task plans and tool selections can be... | 7.5 | 7.5 | 7.0 | 3.5 | 6.6 | Medium | 30d | Review |
| D-27 | fresh | feature-store-2 | A single oversized or deeply nested payload makes... | 8.5 | 8.0 | 5.5 | 2.0 | 6.6 | Medium | 30d | Review |
| LLM-53 | fresh | policy-engine | Instructions hidden in guardrail rules and approval... | 8.0 | 8.0 | 7.5 | 1.5 | 6.6 | Medium | 30d | Review |
| OI-10 | fresh | planner-agent | Structured output from planner-agent is trusted by... | 8.1 | 7.0 | 6.5 | 3.5 | 6.6 | Medium | 30d | Review |
| OI-25 | fresh | summarizer-llm | File paths or names produced by summarizer-llm are used to... | 9.6 | 6.5 | 6.5 | 1.5 | 6.6 | Medium | 30d | Review |
| MI-1 | fresh | intake-agent | intake-agent fabricates reference numbers and clause... | 9.3 | 7.0 | 6.5 | 1.5 | 6.6 | Medium | 30d | Review |
| MI-18 | fresh | eval-runner | eval-runner fabricates reference numbers and clause... | 8.7 | 6.5 | 7.0 | 3.0 | 6.6 | Medium | 30d | Review |
| TE-4 | fresh | intake-agent | intake-agent claims certainty it does not have when... | 9.9 | 5.0 | 6.0 | 3.5 | 6.6 | Medium | 30d | Review |
| S-41 | fresh | reviewer-agent | An attacker replays a captured reviewer session against... | 8.2 | 7.0 | 7.0 | 2.5 | 6.5 | Medium | 30d | Review |
| D-20 | fresh | model-gateway | Expensive queries over prompts and completions can be... | 7.5 | 7.5 | 6.0 | 3.5 | 6.5 | Medium | 30d | Review |
| D-31 | fresh | scheduler-1 | Unbounded growth of stored recurring planning triggers on... | 7.5 | 8.0 | 5.0 | 3.5 | 6.5 | Medium | 30d | Review |
| E-22 | fresh | embed-service-2 | embed-service-2 runs with broader permissions than its... | 9.9 | 5.0 | 6.0 | 3.0 | 6.5 | Medium | 30d | Review |
| E-34 | fresh | eval-runner | A confused-deputy path lets a low-privilege caller ask... | 9.9 | 4.5 | 6.5 | 3.5 | 6.5 | Medium | 30d | Review |
| AGP-02 | fresh | worker-2 | Worker agents coordinate through the shared message bus and... | 9.9 | 4.5 | 6.5 | 3.5 | 6.5 | Medium | 30d | Review |
| AGP-03 | fresh | scheduler-1 | State persisted across runs lets a sleeper instruction... | 9.9 | 5.5 | 6.0 | 2.5 | 6.5 | Medium | 30d | Review |
| LLM-35 | fresh | memory-store | Records written into memory-store by low-trust sources are... | 8.0 | 7.5 | 7.0 | 2.0 | 6.5 | Medium | 30d | Review |
| OI-11 | fresh | planner-agent | Markdown or HTML produced by planner-agent contains remote... | 8.7 | 7.0 | 6.5 | 2.0 | 6.5 | Medium | 30d | Review |
| OI-23 | fresh | summarizer-llm | Structured output from summarizer-llm is trusted by... | 8.7 | 6.5 | 7.0 | 2.5 | 6.5 | Medium | 30d | Review |
| MI-13 | fresh | summarizer-llm | Confident wording from summarizer-llm hides low retrieval... | 7.6 | 8.0 | 7.0 | 2.0 | 6.5 | Medium | 30d | Review |
| S-32 | fresh | trace-collector | A compromised peer presents a forged service identity to... | 8.2 | 6.0 | 7.5 | 3.0 | 6.4 | Medium | 30d | Review |
| E-15 | fresh | worker-3 | Object identifiers in requests to worker-3 are trusted... | 9.9 | 5.0 | 6.0 | 2.5 | 6.4 | Medium | 30d | Review |
| E-29 | fresh | trace-collector | A privileged maintenance task of trace-collector can be... | 9.9 | 5.0 | 5.5 | 3.0 | 6.4 | Medium | 30d | Review |
| AG-18 | fresh | worker-2 | The goal or instruction set of worker-2 can be changed... | 9.9 | 5.5 | 5.5 | 2.5 | 6.4 | Medium | 30d | Review |
| AG-26 | fresh | reviewer-agent | reviewer-agent retries failed actions on its own, repeating... | 9.9 | 5.0 | 5.5 | 3.0 | 6.4 | Medium | 30d | Review |
| LLM-8 | fresh | router-agent | Indirect injection through documents retrieved for... | 8.2 | 7.0 | 6.0 | 2.5 | 6.4 | Medium | 30d | Review |
| LLM-15 | fresh | worker-3 | worker-3 follows links and files named in work orders and... | 8.3 | 7.5 | 6.0 | 1.5 | 6.4 | Medium | 30d | Review |
| LLM-28 | fresh | summarizer-llm | Model weights or adapters served by summarizer-llm are... | 7.6 | 8.0 | 6.0 | 2.0 | 6.4 | Medium | 30d | Review |
| MI-7 | fresh | reviewer-agent | Confident wording from reviewer-agent hides low retrieval... | 6.5 | 8.0 | 7.0 | 3.5 | 6.4 | Medium | 30d | Review |
| MI-15 | fresh | summarizer-llm | summarizer-llm fabricates reference numbers and clause... | 7.6 | 7.5 | 7.0 | 2.0 | 6.4 | Medium | 30d | Review |
| TE-9 | fresh | reviewer-agent | reviewer-agent claims certainty it does not have when... | 9.9 | 5.0 | 5.5 | 3.0 | 6.4 | Medium | 30d | Review |
| S-7 | fresh | intake-agent | Certificate or DNS spoofing between embed-service-2 and... | 8.2 | 7.5 | 6.0 | 1.5 | 6.3 | Medium | 30d | Review |
| D-6 | fresh | intake-agent | Retry storms from trace-collector multiply the load on... | 8.2 | 7.0 | 6.0 | 2.0 | 6.3 | Medium | 30d | Review |
| D-17 | fresh | tool-server-1 | A slow-read attack holds connections to tool-server-1 open... | 7.1 | 8.0 | 6.0 | 2.5 | 6.3 | Medium | 30d | Review |
| D-22 | fresh | summarizer-llm | A single oversized or deeply nested payload makes... | 8.2 | 7.5 | 5.0 | 2.0 | 6.3 | Medium | 30d | Review |
| D-34 | fresh | policy-engine | Expensive queries over guardrail rules and approval... | 7.5 | 8.0 | 6.0 | 2.0 | 6.3 | Medium | 30d | Review |
| E-23 | fresh | summarizer-llm | Object identifiers in requests to summarizer-llm are trusted... | 9.9 | 4.5 | 6.0 | 3.0 | 6.3 | Medium | 30d | Review |
| E-30 | fresh | eval-runner | eval-runner runs with broader permissions than its function... | 9.1 | 5.5 | 5.5 | 3.0 | 6.3 | Medium | 30d | Review |
| AG-27 | fresh | tool-server-1 | Memory written by tool-server-1 is trusted on later runs, so... | 10.0 | 4.5 | 5.5 | 3.0 | 6.3 | Medium | 30d | Review |
| LLM-9 | fresh | router-agent | Encoded or multilingual payloads bypass the keyword filter... | 6.9 | 8.0 | 6.0 | 3.0 | 6.3 | Medium | 30d | Review |
| LLM-21 | fresh | model-gateway | Verbose responses from model-gateway expose token... | 8.7 | 6.5 | 7.0 | 1.5 | 6.3 | Medium | 30d | Review |
| LLM-31 | fresh | kb-index | Records written into kb-index by low-trust sources are later... | 8.7 | 6.5 | 7.0 | 1.5 | 6.3 | Medium | 30d | Review |
| LLM-36 | fresh | memory-store | Fine-tuning data assembled from memory-store is not checked... | 7.5 | 7.0 | 8.0 | 2.0 | 6.3 | Medium | 30d | Review |
| OI-1 | fresh | intake-agent | intake-agent emits URLs that downstream services fetch, so... | 8.2 | 7.0 | 7.0 | 1.5 | 6.3 | Medium | 30d | Review |
| MI-16 | fresh | eval-runner | Confident wording from eval-runner hides low retrieval... | 8.1 | 7.0 | 7.0 | 1.5 | 6.3 | Medium | 30d | Review |
| MI-19 | fresh | worker-3 | worker-3 fabricates reference numbers and clause citations... | 6.9 | 8.0 | 7.0 | 2.0 | 6.3 | Medium | 30d | Review |
| TE-1 | fresh | intake-agent | intake-agent adopts a persona that presents itself as a... | 9.9 | 5.0 | 5.5 | 2.5 | 6.3 | Medium | 30d | Review |
| S-15 | fresh | worker-3 | Low-entropy identifiers accepted by worker-3 double as... | 8.2 | 6.5 | 6.0 | 2.5 | 6.2 | Medium | 30d | Review |
| S-23 | fresh | embed-service-2 | An attacker replays a captured service credential against... | 6.8 | 7.0 | 6.5 | 3.5 | 6.2 | Medium | 30d | Review |
| S-31 | fresh | scheduler-1 | A compromised peer presents a forged service identity to... | 8.5 | 6.5 | 6.5 | 1.5 | 6.2 | Medium | 30d | Review |
| R-2 | fresh | partner-feed | Clock drift between partner-feed and edge-gateway leaves... | 3.5 | 6.0 | 8.0 | 10.0 | 6.2 | Medium | 30d | Review |
| R-31 | fresh | auth-broker | Operators approve changes to credential assertions and... | 5.4 | 7.0 | 7.0 | 6.0 | 6.2 | Medium | 30d | Review |
| AG-33 | fresh | tool-server-1 | Delegation from worker-3 to tool-server-1 carries the full... | 8.9 | 5.0 | 6.0 | 3.5 | 6.2 | Medium | 30d | Review |
| LLM-52 | fresh | policy-engine | policy-engine follows links and files named in guardrail... | 7.1 | 7.0 | 6.0 | 3.5 | 6.2 | Medium | 30d | Review |
| MI-3 | fresh | intake-agent | intake-agent states carrier rules and customs requirements... | 8.0 | 7.0 | 6.5 | 1.5 | 6.2 | Medium | 30d | Review |
| MI-20 | fresh | worker-3 | Stale data in the knowledge base lets worker-3 present... | 7.1 | 7.0 | 6.0 | 3.5 | 6.2 | Medium | 30d | Review |
| S-6 | fresh | intake-agent | Session fixation against intake-agent lets an attacker... | 6.5 | 7.5 | 6.0 | 3.5 | 6.1 | Medium | 30d | Review |
| S-10 | fresh | router-agent | A shared or long-lived routing token on router-agent lets... | 8.2 | 6.0 | 6.0 | 2.5 | 6.1 | Medium | 30d | Review |
| S-42 | fresh | reviewer-agent | A compromised peer presents a forged service identity to... | 8.5 | 6.0 | 6.0 | 2.0 | 6.1 | Medium | 30d | Review |
| T-25 | fresh | memory-store | Backups and exports of task history and operator preferences... | 9.4 | 5.5 | 5.5 | 1.5 | 6.1 | Medium | 30d | Review |
| D-35 | fresh | audit-ledger | Expensive queries over approval and tool call records can be... | 7.1 | 7.5 | 5.0 | 3.0 | 6.1 | Medium | 30d | Review |
| E-17 | fresh | reviewer-agent | Multi-tenant separation in reviewer-agent depends on a... | 9.9 | 5.0 | 5.5 | 1.5 | 6.1 | Medium | 30d | Review |
| E-28 | fresh | trace-collector | Multi-tenant separation in trace-collector depends on a... | 9.9 | 4.5 | 6.0 | 2.0 | 6.1 | Medium | 30d | Review |
| E-32 | fresh | planner-agent | Multi-tenant separation in planner-agent depends on a... | 9.9 | 5.0 | 4.5 | 2.5 | 6.1 | Medium | 30d | Review |
| LLM-33 | fresh | memory-store | Evaluation labels consumed from memory-store are produced by... | 6.9 | 7.5 | 6.0 | 2.5 | 6.1 | Medium | 30d | Review |
| OI-2 | fresh | intake-agent | Structured output from intake-agent is trusted by queue-a2... | 8.0 | 6.5 | 7.0 | 1.5 | 6.1 | Medium | 30d | Review |
| OI-3 | fresh | intake-agent | Markdown or HTML produced by intake-agent contains remote... | 8.2 | 6.5 | 6.5 | 1.5 | 6.1 | Medium | 30d | Review |
| MI-5 | fresh | intake-agent | Outputs from intake-agent flow into decisions without a... | 7.5 | 7.0 | 7.0 | 1.5 | 6.1 | Medium | 30d | Review |
| MI-12 | fresh | summarizer-llm | summarizer-llm states carrier rules and customs requirements... | 6.1 | 7.5 | 6.5 | 3.5 | 6.1 | Medium | 30d | Review |
| TE-3 | fresh | intake-agent | intake-agent builds rapport over long sessions and starts to... | 9.1 | 5.0 | 5.5 | 3.0 | 6.1 | Medium | 30d | Review |
| TE-5 | fresh | intake-agent | intake-agent speaks with an authoritative tone about customs... | 9.9 | 5.0 | 5.5 | 1.5 | 6.1 | Medium | 30d | Review |
| TE-10 | fresh | reviewer-agent | reviewer-agent speaks with an authoritative tone about... | 9.9 | 4.5 | 5.5 | 2.5 | 6.1 | Medium | 30d | Review |
| TE-17 | fresh | reviewer-agent | Persuasive phrasing from reviewer-agent pushes operators to... | 9.6 | 5.0 | 5.0 | 2.5 | 6.1 | Medium | 30d | Review |
| S-13 | fresh | worker-2 | An unauthenticated callback or health route on worker-2... | 7.1 | 6.0 | 6.5 | 3.5 | 6.0 | Medium | 30d | Review |
| S-36 | fresh | eval-runner | Low-entropy identifiers accepted by eval-runner double as... | 7.1 | 6.5 | 7.0 | 2.5 | 6.0 | Medium | 30d | Review |
| T-2 | fresh | auth-broker | Backups and exports of credential assertions and session... | 4.6 | 7.5 | 6.0 | 6.0 | 6.0 | Medium | 30d | Review |
| R-1 | fresh | client-portal | Operators approve changes to operator requests and approval... | 4.3 | 6.0 | 7.0 | 8.0 | 6.0 | Medium | 30d | Review |
| D-16 | fresh | tool-server-1 | Retry storms from audit-ledger multiply the load on... | 5.9 | 8.0 | 6.0 | 3.0 | 6.0 | Medium | 30d | Review |
| E-19 | fresh | tool-server-1 | Multi-tenant separation in tool-server-1 depends on a... | 9.0 | 5.0 | 6.5 | 2.0 | 6.0 | Medium | 30d | Review |
| E-20 | fresh | tool-server-1 | A privileged maintenance task of tool-server-1 can be... | 8.0 | 6.0 | 4.5 | 3.5 | 6.0 | Medium | 30d | Review |
| AG-3 | fresh | intake-agent | intake-agent can start further agents or processes on... | 9.1 | 4.5 | 5.0 | 3.5 | 6.0 | Medium | 30d | Review |
| AG-31 | fresh | tool-server-1 | The goal or instruction set of tool-server-1 can be changed... | 9.9 | 4.0 | 5.5 | 2.5 | 6.0 | Medium | 30d | Review |
| LLM-26 | fresh | summarizer-llm | Anyone who can write to the ingestion path of summarizer-llm... | 6.9 | 6.0 | 7.5 | 3.5 | 6.0 | Medium | 30d | Review |
| LLM-55 | fresh | model-gateway | model-gateway passes conversation history from earlier turns... | 6.1 | 8.0 | 7.0 | 2.0 | 6.0 | Medium | 30d | Review |
| LLM-56 | fresh | embed-service-2 | Model weights or adapters served by embed-service-2 are... | 6.1 | 8.0 | 7.5 | 1.5 | 6.0 | Medium | 30d | Review |
| OI-5 | fresh | intake-agent | Model output from intake-agent is inserted into a rendered... | 6.1 | 8.5 | 6.0 | 2.0 | 6.0 | Medium | 30d | Review |
| MI-6 | fresh | worker-3 | Outputs from worker-3 flow into decisions without a review... | 7.4 | 7.0 | 7.0 | 1.5 | 6.0 | Medium | 30d | Review |
| MI-17 | fresh | eval-runner | Outputs from eval-runner flow into decisions without a... | 7.1 | 7.0 | 6.5 | 2.0 | 6.0 | Medium | 30d | Review |
| TE-11 | fresh | reviewer-agent | reviewer-agent adopts a persona that presents itself as a... | 9.9 | 4.5 | 5.5 | 2.0 | 6.0 | Medium | 30d | Review |
| S-8 | fresh | planner-agent | An unauthenticated callback or health route on planner-agent... | 7.1 | 7.0 | 5.5 | 2.5 | 5.9 | Medium | 30d | Review |
| S-24 | fresh | embed-service-2 | A compromised peer presents a forged service identity to... | 7.1 | 6.5 | 6.0 | 3.0 | 5.9 | Medium | 30d | Review |
| S-39 | fresh | policy-engine | A compromised peer presents a forged service identity to... | 7.1 | 6.5 | 6.0 | 3.0 | 5.9 | Medium | 30d | Review |
| T-26 | fresh | memory-store | Unsanitised task history and operator preferences reach... | 8.2 | 5.5 | 4.5 | 3.5 | 5.9 | Medium | 30d | Review |
| R-5 | fresh | edge-gateway | Clock drift between edge-gateway and client-portal leaves... | 5.0 | 5.5 | 7.5 | 7.0 | 5.9 | Medium | 30d | Review |
| I-9 | fresh | planner-agent | Cross-tenant filters on planner-agent are applied in... | 7.1 | 6.0 | 6.5 | 3.0 | 5.9 | Medium | 30d | Review |
| I-34 | fresh | queue-a2 | Data in transit between scheduler-1 and queue-a2 is... | 6.5 | 7.0 | 7.0 | 2.5 | 5.9 | Medium | 30d | Review |
| D-26 | fresh | s3-archive | Retry storms from trace-collector multiply the load on... | 7.5 | 7.0 | 6.0 | 1.5 | 5.9 | Medium | 30d | Review |
| D-29 | fresh | scheduler-1 | Retry storms from queue-a2 multiply the load on scheduler-1... | 7.1 | 6.5 | 5.5 | 3.0 | 5.9 | Medium | 30d | Review |
| D-32 | fresh | trace-collector | Expensive queries over prompts, completions and tool traces... | 6.5 | 8.5 | 5.0 | 1.5 | 5.9 | Medium | 30d | Review |
| D-33 | fresh | eval-runner | A dependency of eval-runner becomes unavailable and the... | 6.5 | 8.0 | 5.0 | 2.5 | 5.9 | Medium | 30d | Review |
| E-25 | fresh | summarizer-llm | An administrative interface of summarizer-llm is reachable... | 8.2 | 5.5 | 6.5 | 2.0 | 5.9 | Medium | 30d | Review |
| AG-29 | fresh | tool-server-1 | tool-server-1 can start further agents or processes on... | 7.5 | 6.0 | 6.0 | 3.0 | 5.9 | Medium | 30d | Review |
| AG-30 | fresh | tool-server-1 | tool-server-1 can act on tool call arguments and results... | 8.6 | 5.5 | 5.0 | 2.5 | 5.9 | Medium | 30d | Review |
| AG-37 | fresh | queue-a2 | queue-a2 does not limit the rate or total number of tool... | 10.0 | 4.0 | 4.5 | 2.5 | 5.9 | Medium | 30d | Review |
| AG-43 | fresh | queue-a2 | Tool calls made by queue-a2 are not tied to the end user, so... | 8.4 | 5.0 | 6.0 | 3.0 | 5.9 | Medium | 30d | Review |
| LLM-20 | fresh | model-gateway | Model weights or adapters served by model-gateway are... | 6.1 | 7.0 | 6.5 | 3.5 | 5.9 | Medium | 30d | Review |
| LLM-30 | fresh | kb-index | A delayed trigger planted in carrier tariffs and customs... | 6.1 | 7.5 | 6.5 | 2.5 | 5.9 | Medium | 30d | Review |
| OI-17 | fresh | worker-2 | Text generated by worker-2 is placed into a database query... | 6.1 | 6.5 | 7.5 | 3.5 | 5.9 | Medium | 30d | Review |
| OI-24 | fresh | summarizer-llm | Markdown or HTML produced by summarizer-llm contains remote... | 6.9 | 7.0 | 6.5 | 2.0 | 5.9 | Medium | 30d | Review |
| TE-14 | fresh | summarizer-llm | summarizer-llm adopts a persona that presents itself as a... | 9.9 | 4.5 | 5.5 | 1.5 | 5.9 | Medium | 30d | Review |
| S-12 | fresh | worker-2 | A shared or long-lived worker credential on worker-2 lets... | 6.5 | 6.5 | 6.0 | 3.5 | 5.8 | Medium | 30d | Review |
| S-16 | fresh | worker-3 | An attacker replays a captured worker credential against... | 7.6 | 6.5 | 5.5 | 2.0 | 5.8 | Medium | 30d | Review |
| S-22 | fresh | model-gateway | An attacker replays a captured model API key against... | 7.1 | 7.0 | 6.0 | 1.5 | 5.8 | Medium | 30d | Review |
| S-30 | fresh | scheduler-1 | An attacker replays a captured scheduler credential against... | 6.5 | 6.5 | 6.0 | 3.5 | 5.8 | Medium | 30d | Review |
| T-32 | fresh | feature-store-2 | A race between concurrent writers lets an attacker overwrite... | 8.2 | 5.0 | 5.0 | 3.5 | 5.8 | Medium | 30d | Review |
| T-41 | fresh | policy-engine | Backups and exports of guardrail rules and approval... | 8.6 | 5.5 | 5.0 | 2.0 | 5.8 | Medium | 30d | Review |
| R-6 | fresh | auth-broker | Delegated actions performed by auth-broker on behalf of a... | 4.3 | 6.5 | 7.0 | 6.5 | 5.8 | Medium | 30d | Review |
| D-30 | fresh | scheduler-1 | A slow-read attack holds connections to scheduler-1 open and... | 6.8 | 7.0 | 5.0 | 3.0 | 5.8 | Medium | 30d | Review |
| E-13 | fresh | worker-2 | An administrative interface of worker-2 is reachable from... | 7.7 | 5.0 | 6.0 | 3.5 | 5.8 | Medium | 30d | Review |
| E-14 | fresh | worker-2 | worker-2 runs with broader permissions than its function... | 8.3 | 5.0 | 5.0 | 3.0 | 5.8 | Medium | 30d | Review |
| E-18 | fresh | tool-server-1 | A confused-deputy path lets a low-privilege caller ask... | 8.8 | 5.0 | 5.5 | 2.0 | 5.8 | Medium | 30d | Review |
| AG-41 | fresh | intake-agent | intake-agent can act on free-text shipment requests without... | 8.9 | 5.5 | 5.0 | 1.5 | 5.8 | Medium | 30d | Review |
| OI-13 | fresh | planner-agent | Model output from planner-agent is inserted into a rendered... | 6.3 | 7.0 | 7.0 | 2.0 | 5.8 | Medium | 30d | Review |
| OI-27 | fresh | model-gateway | Text generated by model-gateway is placed into a database... | 7.7 | 6.5 | 6.0 | 1.5 | 5.8 | Medium | 30d | Review |
| MI-14 | fresh | summarizer-llm | Outputs from summarizer-llm flow into decisions without a... | 5.8 | 7.0 | 7.0 | 3.0 | 5.8 | Medium | 30d | Review |
| TE-15 | fresh | summarizer-llm | Persuasive phrasing from summarizer-llm pushes operators to... | 8.7 | 4.5 | 6.0 | 2.5 | 5.8 | Medium | 30d | Review |
| S-11 | fresh | router-agent | An unauthenticated callback or health route on router-agent... | 6.8 | 6.5 | 7.0 | 1.5 | 5.7 | Medium | 30d | Review |
| S-21 | fresh | tool-server-1 | Certificate or DNS spoofing between audit-ledger and... | 6.4 | 6.0 | 7.5 | 2.5 | 5.7 | Medium | 30d | Review |
| R-7 | fresh | auth-broker | Failed and rejected attempts against auth-broker are not... | 3.7 | 7.0 | 6.5 | 6.5 | 5.7 | Medium | 30d | Review |
| R-23 | fresh | queue-a2 | Failed and rejected attempts against queue-a2 are not... | 8.6 | 4.5 | 4.5 | 3.5 | 5.7 | Medium | 30d | Review |
| I-47 | fresh | policy-engine | Data in transit between audit-ledger and policy-engine is... | 7.2 | 5.0 | 6.5 | 3.5 | 5.7 | Medium | 30d | Review |
| D-13 | fresh | reviewer-agent | Expensive queries over drafted proposals awaiting review can... | 6.3 | 6.5 | 5.5 | 3.5 | 5.7 | Medium | 30d | Review |
| D-18 | fresh | model-gateway | Unbounded growth of stored prompts and completions on... | 5.7 | 7.5 | 6.0 | 3.0 | 5.7 | Medium | 30d | Review |
| D-24 | fresh | kb-index | A dependency of kb-index becomes unavailable and the failure... | 5.9 | 7.0 | 6.5 | 3.0 | 5.7 | Medium | 30d | Review |
| D-28 | fresh | queue-a2 | A burst of requests exhausts the connection pool of... | 8.6 | 4.5 | 4.5 | 3.5 | 5.7 | Medium | 30d | Review |
| D-39 | fresh | queue-a2 | A single oversized or deeply nested payload makes queue-a2... | 8.6 | 4.5 | 4.5 | 3.5 | 5.7 | Medium | 30d | Review |
| E-26 | fresh | queue-a2 | A privileged maintenance task of queue-a2 can be triggered... | 8.6 | 4.5 | 4.5 | 3.5 | 5.7 | Medium | 30d | Review |
| E-33 | fresh | queue-a2 | Object identifiers in requests to queue-a2 are trusted... | 8.6 | 4.5 | 4.5 | 3.5 | 5.7 | Medium | 30d | Review |
| AG-23 | fresh | worker-3 | An attacker chains two individually safe tools through... | 7.7 | 5.5 | 6.0 | 2.5 | 5.7 | Medium | 30d | Review |
| AG-28 | fresh | tool-server-1 | tool-server-1 retries failed actions on its own, repeating... | 9.6 | 4.0 | 5.0 | 2.0 | 5.7 | Medium | 30d | Review |
| AG-35 | fresh | queue-a2 | queue-a2 can start further agents or processes on request... | 8.6 | 4.5 | 4.5 | 3.5 | 5.7 | Medium | 30d | Review |
| AG-36 | fresh | queue-a2 | An attacker chains two individually safe tools through... | 8.6 | 4.5 | 4.5 | 3.5 | 5.7 | Medium | 30d | Review |
| LLM-49 | fresh | eval-runner | A delayed trigger planted in replayed traces and judge... | 5.4 | 7.5 | 6.5 | 3.0 | 5.7 | Medium | 30d | Review |
| OI-19 | fresh | model-gateway | File paths or names produced by model-gateway are used to... | 6.1 | 7.5 | 6.5 | 1.5 | 5.7 | Medium | 30d | Review |
| TE-13 | fresh | summarizer-llm | summarizer-llm speaks with an authoritative tone about... | 8.2 | 5.0 | 5.0 | 3.0 | 5.7 | Medium | 30d | Review |
| T-23 | fresh | kb-index | A race between concurrent writers lets an attacker overwrite... | 8.3 | 5.5 | 5.0 | 1.5 | 5.6 | Medium | 30d | Review |
| I-25 | fresh | vector-store-a | embedded documents and metadata held by vector-store-a are... | 5.7 | 7.0 | 5.5 | 3.5 | 5.6 | Medium | 30d | Review |
| I-28 | fresh | kb-index | Logs and traces emitted by kb-index include raw carrier... | 7.7 | 5.5 | 5.5 | 2.0 | 5.6 | Medium | 30d | Review |
| D-23 | fresh | vector-store-a | Retry storms from embed-service-2 multiply the load on... | 6.5 | 7.0 | 5.0 | 2.5 | 5.6 | Medium | 30d | Review |
| AG-6 | fresh | planner-agent | Memory written by planner-agent is trusted on later runs, so... | 8.4 | 4.5 | 5.0 | 3.0 | 5.6 | Medium | 30d | Review |
| AG-9 | fresh | planner-agent | Tool calls made by planner-agent are not tied to the end... | 8.2 | 5.5 | 4.5 | 2.0 | 5.6 | Medium | 30d | Review |
| AG-10 | fresh | planner-agent | planner-agent invokes tools with arguments assembled from... | 8.2 | 4.0 | 6.5 | 3.0 | 5.6 | Medium | 30d | Review |
| AG-14 | fresh | router-agent | router-agent does not limit the rate or total number of tool... | 7.7 | 4.5 | 6.0 | 3.5 | 5.6 | Medium | 30d | Review |
| AG-17 | fresh | worker-2 | worker-2 can act on work orders and route candidates without... | 8.2 | 4.0 | 5.5 | 3.5 | 5.6 | Medium | 30d | Review |
| LLM-29 | fresh | kb-index | Evaluation labels consumed from kb-index are produced by a... | 8.3 | 5.5 | 5.0 | 1.5 | 5.6 | Medium | 30d | Review |
| TE-8 | fresh | reviewer-agent | reviewer-agent builds rapport over long sessions and starts... | 8.1 | 5.5 | 5.0 | 2.0 | 5.6 | Medium | 30d | Review |
| S-20 | fresh | tool-server-1 | Session fixation against tool-server-1 lets an attacker... | 5.9 | 7.0 | 6.5 | 2.0 | 5.5 | Medium | 30d | Review |
| S-43 | fresh | model-gateway | A compromised peer presents a forged service identity to... | 5.8 | 7.0 | 7.0 | 1.5 | 5.5 | Medium | 30d | Review |
| T-19 | fresh | summarizer-llm | An attacker who can write to the channel between... | 7.1 | 5.5 | 4.5 | 3.5 | 5.5 | Medium | 30d | Review |
| T-35 | fresh | scheduler-1 | Configuration of scheduler-1 can be rewritten by any service... | 8.1 | 5.5 | 5.0 | 1.5 | 5.5 | Medium | 30d | Review |
| I-10 | fresh | router-agent | A timing or size difference in the responses of router-agent... | 7.7 | 6.0 | 5.0 | 1.5 | 5.5 | Medium | 30d | Review |
| I-31 | fresh | s3-archive | Data in transit between trace-collector and s3-archive is... | 6.5 | 6.0 | 6.0 | 2.5 | 5.5 | Medium | 30d | Review |
| I-42 | fresh | audit-ledger | Logs and traces emitted by audit-ledger include raw approval... | 6.1 | 6.0 | 7.0 | 2.5 | 5.5 | Medium | 30d | Review |
| E-21 | fresh | model-gateway | Role claims carried in the model API key presented to... | 8.5 | 5.0 | 5.0 | 1.5 | 5.5 | Medium | 30d | Review |
| E-31 | fresh | policy-engine | Multi-tenant separation in policy-engine depends on a... | 8.5 | 4.5 | 4.5 | 2.5 | 5.5 | Medium | 30d | Review |
| AG-21 | fresh | worker-3 | The goal or instruction set of worker-3 can be changed... | 8.2 | 5.0 | 5.0 | 2.0 | 5.5 | Medium | 30d | Review |
| AG-42 | fresh | tool-server-1 | Memory written by tool-server-1 is trusted on later runs, so... | 8.4 | 4.5 | 4.0 | 3.0 | 5.5 | Medium | 30d | Review |
| LLM-23 | fresh | embed-service-2 | Systematic queries against embed-service-2 let an attacker... | 5.4 | 7.0 | 7.5 | 2.0 | 5.5 | Medium | 30d | Review |
| TE-2 | fresh | intake-agent | Persuasive phrasing from intake-agent pushes operators to... | 9.2 | 4.0 | 5.0 | 1.5 | 5.5 | Medium | 30d | Review |
| S-14 | fresh | worker-3 | Certificate or DNS spoofing between trace-collector and... | 5.9 | 6.5 | 6.5 | 2.0 | 5.4 | Medium | 30d | Review |
| S-25 | fresh | embed-service-2 | A shared or long-lived service credential on embed-service-2... | 6.3 | 6.5 | 6.5 | 1.5 | 5.4 | Medium | 30d | Review |
| S-38 | fresh | policy-engine | An attacker replays a captured policy token against... | 6.5 | 5.5 | 6.5 | 2.5 | 5.4 | Medium | 30d | Review |
| T-7 | fresh | reviewer-agent | An attacker who can write to the channel between... | 6.5 | 6.0 | 4.0 | 3.5 | 5.4 | Medium | 30d | Review |
| T-8 | fresh | reviewer-agent | An update to reviewer-agent is pulled without provenance... | 8.5 | 4.5 | 4.0 | 2.5 | 5.4 | Medium | 30d | Review |
| T-24 | fresh | memory-store | Serialised objects arriving from planner-agent are... | 6.5 | 6.0 | 5.0 | 3.0 | 5.4 | Medium | 30d | Review |
| T-39 | fresh | policy-engine | Replay of an earlier valid update to guardrail rules and... | 7.6 | 5.0 | 5.0 | 2.5 | 5.4 | Medium | 30d | Review |
| D-21 | fresh | embed-service-2 | Unbounded growth of stored document chunks and query... | 5.3 | 7.0 | 7.0 | 2.0 | 5.4 | Medium | 30d | Review |
| D-38 | fresh | summarizer-llm | Retry storms from feature-store-2 multiply the load on... | 5.1 | 8.0 | 6.0 | 1.5 | 5.4 | Medium | 30d | Review |
| AG-7 | fresh | planner-agent | planner-agent retries failed actions on its own, repeating... | 7.9 | 4.5 | 6.0 | 2.0 | 5.4 | Medium | 30d | Review |
| LLM-32 | fresh | memory-store | Anyone who can write to the ingestion path of memory-store... | 6.5 | 6.0 | 5.0 | 3.0 | 5.4 | Medium | 30d | Review |
| S-29 | fresh | queue-a2 | An attacker replays a captured broker credential against... | 5.9 | 6.5 | 6.5 | 1.5 | 5.3 | Medium | 30d | Review |
| S-37 | fresh | eval-runner | An attacker replays a captured evaluation credential against... | 5.4 | 7.0 | 5.5 | 2.5 | 5.3 | Medium | 30d | Review |
| T-3 | fresh | intake-agent | Replay of an earlier valid update to free-text shipment... | 7.1 | 5.0 | 4.5 | 3.0 | 5.3 | Medium | 30d | Review |
| T-16 | fresh | summarizer-llm | Backups and exports of shipment records fed into summaries... | 7.1 | 5.0 | 4.0 | 3.5 | 5.3 | Medium | 30d | Review |
| T-17 | fresh | summarizer-llm | Unsanitised shipment records fed into summaries reach... | 7.1 | 5.0 | 4.0 | 3.5 | 5.3 | Medium | 30d | Review |
| T-30 | fresh | feature-store-2 | An update to feature-store-2 is pulled without provenance... | 6.3 | 6.0 | 4.5 | 3.0 | 5.3 | Medium | 30d | Review |
| T-31 | fresh | feature-store-2 | Configuration of feature-store-2 can be rewritten by any... | 6.3 | 6.0 | 4.5 | 3.0 | 5.3 | Medium | 30d | Review |
| T-42 | fresh | audit-ledger | An attacker who can write to the channel between... | 7.1 | 5.0 | 4.0 | 3.5 | 5.3 | Medium | 30d | Review |
| T-45 | fresh | worker-3 | An update to worker-3 is pulled without provenance checks... | 7.6 | 5.0 | 4.0 | 2.5 | 5.3 | Medium | 30d | Review |
| I-16 | fresh | tool-server-1 | Cross-tenant filters on tool-server-1 are applied in... | 5.5 | 6.5 | 5.0 | 3.5 | 5.3 | Medium | 30d | Review |
| I-17 | fresh | tool-server-1 | Secrets such as the tool API key for tool-server-1 appear in... | 5.5 | 6.5 | 5.0 | 3.5 | 5.3 | Medium | 30d | Review |
| I-24 | fresh | summarizer-llm | Logs and traces emitted by summarizer-llm include raw... | 7.1 | 5.0 | 4.0 | 3.5 | 5.3 | Medium | 30d | Review |
| I-40 | fresh | policy-engine | Logs and traces emitted by policy-engine include raw... | 5.7 | 6.5 | 6.0 | 2.5 | 5.3 | Medium | 30d | Review |
| I-41 | fresh | audit-ledger | approval and tool call records held by audit-ledger are... | 5.4 | 6.0 | 6.0 | 3.5 | 5.3 | Medium | 30d | Review |
| D-14 | fresh | tool-server-1 | A burst of requests exhausts the connection pool of... | 5.5 | 6.5 | 5.0 | 3.5 | 5.3 | Medium | 30d | Review |
| D-15 | fresh | tool-server-1 | A single oversized or deeply nested payload makes... | 5.5 | 6.5 | 5.0 | 3.5 | 5.3 | Medium | 30d | Review |
| E-11 | fresh | router-agent | Multi-tenant separation in router-agent depends on a request... | 6.6 | 5.5 | 5.5 | 2.5 | 5.3 | Medium | 30d | Review |
| AG-34 | fresh | tool-server-1 | tool-server-1 invokes tools with arguments assembled from... | 5.5 | 6.5 | 5.0 | 3.5 | 5.3 | Medium | 30d | Review |
| LLM-17 | fresh | tool-server-1 | Encoded or multilingual payloads bypass the keyword filter... | 5.5 | 6.5 | 5.0 | 3.5 | 5.3 | Medium | 30d | Review |
| LLM-24 | fresh | summarizer-llm | summarizer-llm follows links and files named in shipment... | 7.1 | 5.0 | 4.0 | 3.5 | 5.3 | Medium | 30d | Review |
| LLM-25 | fresh | summarizer-llm | Embeddings stored by summarizer-llm can be crowded with... | 7.1 | 5.0 | 4.0 | 3.5 | 5.3 | Medium | 30d | Review |
| LLM-39 | fresh | feature-store-2 | Fine-tuning data assembled from feature-store-2 is not... | 6.3 | 6.0 | 4.5 | 3.0 | 5.3 | Medium | 30d | Review |
| TE-7 | fresh | reviewer-agent | Persuasive phrasing from reviewer-agent pushes operators to... | 7.7 | 4.0 | 5.0 | 3.5 | 5.3 | Medium | 30d | Review |
| S-27 | fresh | summarizer-llm | An attacker replays a captured inference credential against... | 5.9 | 6.0 | 5.5 | 2.5 | 5.2 | Medium | 30d | Review |
| T-33 | fresh | queue-a2 | A race between concurrent writers lets an attacker overwrite... | 7.1 | 5.0 | 5.0 | 2.5 | 5.2 | Medium | 30d | Review |
| I-45 | fresh | s3-archive | A timing or size difference in the responses of s3-archive... | 5.8 | 5.5 | 6.0 | 3.0 | 5.2 | Medium | 30d | Review |
| D-5 | fresh | intake-agent | A single oversized or deeply nested payload makes... | 4.8 | 8.0 | 5.5 | 1.5 | 5.2 | Medium | 30d | Review |
| D-19 | fresh | model-gateway | A dependency of model-gateway becomes unavailable and the... | 5.0 | 7.5 | 6.0 | 1.5 | 5.2 | Medium | 30d | Review |
| AG-8 | fresh | planner-agent | planner-agent does not limit the rate or total number of... | 8.2 | 4.0 | 5.0 | 2.0 | 5.2 | Medium | 30d | Review |
| TE-12 | fresh | summarizer-llm | summarizer-llm claims certainty it does not have when... | 7.6 | 4.0 | 5.5 | 2.5 | 5.2 | Medium | 30d | Review |
| S-18 | fresh | tool-server-1 | A shared or long-lived tool API key on tool-server-1 lets... | 5.0 | 6.0 | 7.0 | 2.5 | 5.1 | Medium | 30d | Review |
| T-9 | fresh | tool-server-1 | An update to tool-server-1 is pulled without provenance... | 6.6 | 5.0 | 4.0 | 3.5 | 5.1 | Medium | 30d | Review |
| T-11 | fresh | model-gateway | Configuration of model-gateway can be rewritten by any... | 5.9 | 6.0 | 5.0 | 2.5 | 5.1 | Medium | 30d | Review |
| T-29 | fresh | s3-archive | Unsanitised archived transcripts and training corpora reach... | 7.1 | 4.5 | 4.5 | 3.0 | 5.1 | Medium | 30d | Review |
| T-37 | fresh | eval-runner | Serialised objects arriving from trace-collector are... | 7.4 | 5.0 | 5.0 | 1.5 | 5.1 | Medium | 30d | Review |
| T-38 | fresh | eval-runner | Backups and exports of replayed traces and judge verdicts on... | 7.4 | 5.0 | 5.0 | 1.5 | 5.1 | Medium | 30d | Review |
| T-43 | fresh | router-agent | Unsanitised subtask assignments reach router-agent and are... | 6.4 | 5.5 | 5.0 | 2.5 | 5.1 | Medium | 30d | Review |
| R-3 | fresh | edge-gateway | Log entries from edge-gateway can be edited or deleted by... | 3.1 | 5.5 | 7.0 | 6.5 | 5.1 | Medium | 30d | Review |
| I-46 | fresh | eval-runner | Verbose error responses from eval-runner reveal internal... | 7.4 | 5.0 | 5.0 | 1.5 | 5.1 | Medium | 30d | Review |
| D-25 | fresh | memory-store | A dependency of memory-store becomes unavailable and the... | 4.3 | 7.5 | 6.5 | 2.0 | 5.1 | Medium | 30d | Review |
| E-24 | fresh | summarizer-llm | Role claims carried in the inference credential presented to... | 7.4 | 5.0 | 5.0 | 1.5 | 5.1 | Medium | 30d | Review |
| AG-32 | fresh | tool-server-1 | tool-server-1 runs without a budget on steps or spend, so a... | 7.4 | 4.5 | 5.0 | 2.0 | 5.1 | Medium | 30d | Review |
| LLM-44 | fresh | eval-runner | A user message crafted to look like a system directive... | 7.4 | 5.0 | 5.0 | 1.5 | 5.1 | Medium | 30d | Review |
| LLM-45 | fresh | eval-runner | Indirect injection through documents retrieved for... | 7.4 | 5.0 | 5.0 | 1.5 | 5.1 | Medium | 30d | Review |
| LLM-46 | fresh | eval-runner | Embeddings stored by eval-runner can be crowded with... | 7.4 | 5.0 | 5.0 | 1.5 | 5.1 | Medium | 30d | Review |
| T-4 | fresh | planner-agent | Unsanitised task plans and tool selections reach... | 7.1 | 4.5 | 3.5 | 3.0 | 5.0 | Medium | 30d | Review |
| T-10 | fresh | tool-server-1 | Configuration of tool-server-1 can be rewritten by any... | 6.5 | 5.0 | 4.0 | 3.0 | 5.0 | Medium | 30d | Review |
| T-12 | fresh | model-gateway | A race between concurrent writers lets an attacker overwrite... | 6.0 | 5.5 | 5.0 | 2.5 | 5.0 | Medium | 30d | Review |
| T-13 | fresh | model-gateway | Replay of an earlier valid update to prompts and completions... | 6.9 | 5.0 | 4.5 | 2.0 | 5.0 | Medium | 30d | Review |
| T-34 | fresh | scheduler-1 | An update to scheduler-1 is pulled without provenance... | 6.3 | 4.5 | 5.5 | 3.0 | 5.0 | Medium | 30d | Review |
| I-8 | fresh | planner-agent | Backups of task plans and tool selections taken from... | 4.6 | 6.5 | 5.5 | 3.0 | 5.0 | Medium | 30d | Review |
| I-36 | fresh | scheduler-1 | Cross-tenant filters on scheduler-1 are applied in... | 5.4 | 6.0 | 6.5 | 1.5 | 5.0 | Medium | 30d | Review |
| E-7 | fresh | intake-agent | An administrative interface of intake-agent is reachable... | 6.8 | 4.5 | 4.5 | 3.0 | 5.0 | Medium | 30d | Review |
| TE-6 | fresh | intake-agent | intake-agent adopts a persona that presents itself as a... | 8.1 | 3.5 | 4.5 | 2.0 | 5.0 | Medium | 30d | Review |
| S-26 | fresh | summarizer-llm | Low-entropy identifiers accepted by summarizer-llm double as... | 4.2 | 7.0 | 6.0 | 2.0 | 4.9 | Medium | 30d | Review |
| T-14 | fresh | embed-service-2 | Replay of an earlier valid update to document chunks and... | 6.3 | 4.5 | 5.0 | 3.0 | 4.9 | Medium | 30d | Review |
| T-15 | fresh | embed-service-2 | Serialised objects arriving from intake-agent are... | 6.3 | 4.5 | 5.0 | 3.0 | 4.9 | Medium | 30d | Review |
| T-44 | fresh | worker-2 | An attacker who can write to the channel between... | 7.1 | 4.5 | 5.0 | 1.5 | 4.9 | Medium | 30d | Review |
| I-23 | fresh | embed-service-2 | Secrets such as the service credential for embed-service-2... | 5.5 | 5.5 | 5.5 | 2.5 | 4.9 | Medium | 30d | Review |
| I-30 | fresh | memory-store | Cross-tenant filters on memory-store are applied in... | 4.6 | 7.5 | 5.0 | 1.5 | 4.9 | Medium | 30d | Review |
| D-37 | fresh | worker-2 | A slow-read attack holds connections to worker-2 open and... | 4.2 | 7.0 | 5.5 | 2.5 | 4.9 | Medium | 30d | Review |
| LLM-22 | fresh | embed-service-2 | Records written into embed-service-2 by low-trust sources... | 6.3 | 4.5 | 5.0 | 3.0 | 4.9 | Medium | 30d | Review |
| T-36 | fresh | trace-collector | An update to trace-collector is pulled without provenance... | 5.2 | 6.5 | 5.0 | 1.5 | 4.8 | Medium | 30d | Review |
| I-26 | fresh | vector-store-a | Logs and traces emitted by vector-store-a include raw... | 3.5 | 7.0 | 6.5 | 2.5 | 4.8 | Medium | 30d | Review |
| I-37 | fresh | trace-collector | Logs and traces emitted by trace-collector include raw... | 5.2 | 6.5 | 5.0 | 1.5 | 4.8 | Medium | 30d | Review |
| I-38 | fresh | trace-collector | Data in transit between planner-agent and trace-collector is... | 5.2 | 6.5 | 5.0 | 1.5 | 4.8 | Medium | 30d | Review |
| AGP-01 | fresh | planner-agent | Interacting planning and routing agents amplify each other's... | 6.4 | 4.5 | 4.5 | 2.5 | 4.8 | Medium | 30d | Review |
| LLM-40 | fresh | trace-collector | Instructions hidden in prompts, completions and tool traces... | 5.2 | 6.5 | 5.0 | 1.5 | 4.8 | Medium | 30d | Review |
| LLM-42 | fresh | trace-collector | Evaluation labels consumed from trace-collector are produced... | 5.2 | 6.5 | 5.0 | 1.5 | 4.8 | Medium | 30d | Review |
| S-17 | fresh | worker-3 | A compromised peer presents a forged service identity to... | 4.8 | 5.5 | 6.5 | 2.0 | 4.7 | Medium | 30d | Review |
| S-19 | fresh | tool-server-1 | An unauthenticated callback or health route on tool-server-1... | 4.2 | 6.5 | 6.5 | 1.5 | 4.7 | Medium | 30d | Review |
| S-34 | fresh | trace-collector | An unauthenticated callback or health route on... | 4.6 | 6.0 | 5.5 | 2.5 | 4.7 | Medium | 30d | Review |
| T-27 | fresh | s3-archive | Serialised objects arriving from kb-index are deserialised... | 6.3 | 4.5 | 5.0 | 2.0 | 4.7 | Medium | 30d | Review |
| T-28 | fresh | s3-archive | Backups and exports of archived transcripts and training... | 6.3 | 4.5 | 5.0 | 2.0 | 4.7 | Medium | 30d | Review |
| I-13 | fresh | worker-2 | Logs and traces emitted by worker-2 include raw work orders... | 3.8 | 7.0 | 6.0 | 2.0 | 4.7 | Medium | 30d | Review |
| I-18 | fresh | tool-server-1 | Verbose error responses from tool-server-1 reveal internal... | 5.4 | 5.0 | 6.5 | 1.5 | 4.7 | Medium | 30d | Review |
| I-21 | fresh | model-gateway | Secrets such as the model API key for model-gateway appear... | 4.5 | 5.5 | 6.0 | 3.0 | 4.7 | Medium | 30d | Review |
| I-22 | fresh | model-gateway | Verbose error responses from model-gateway reveal internal... | 4.2 | 5.5 | 6.5 | 3.0 | 4.7 | Medium | 30d | Review |
| I-29 | fresh | memory-store | Backups of task history and operator preferences taken from... | 4.9 | 5.5 | 5.0 | 3.0 | 4.7 | Medium | 30d | Review |
| D-10 | fresh | worker-2 | Retry storms from tool-server-1 multiply the load on... | 3.8 | 7.0 | 6.0 | 2.0 | 4.7 | Medium | 30d | Review |
| E-12 | fresh | worker-2 | Role claims carried in the worker credential presented to... | 3.8 | 7.0 | 6.0 | 2.0 | 4.7 | Medium | 30d | Review |
| AG-15 | fresh | worker-2 | worker-2 retries failed actions on its own, repeating side... | 3.8 | 7.0 | 6.0 | 2.0 | 4.7 | Medium | 30d | Review |
| AG-16 | fresh | worker-2 | worker-2 can start further agents or processes on request... | 3.8 | 7.0 | 6.0 | 2.0 | 4.7 | Medium | 30d | Review |
| AG-19 | fresh | worker-2 | Tool calls made by worker-2 are not tied to the end user, so... | 3.8 | 7.0 | 6.0 | 2.0 | 4.7 | Medium | 30d | Review |
| LLM-13 | fresh | worker-2 | worker-2 follows links and files named in work orders and... | 3.8 | 7.0 | 6.0 | 2.0 | 4.7 | Medium | 30d | Review |
| LLM-37 | fresh | s3-archive | A delayed trigger planted in archived transcripts and... | 6.3 | 4.5 | 5.0 | 2.0 | 4.7 | Medium | 30d | Review |
| LLM-38 | fresh | s3-archive | Records written into s3-archive by low-trust sources are... | 6.3 | 4.5 | 5.0 | 2.0 | 4.7 | Medium | 30d | Review |
| TE-16 | fresh | intake-agent | Persuasive phrasing from intake-agent pushes operators to... | 6.0 | 5.0 | 5.5 | 1.5 | 4.7 | Medium | 30d | Review |
| S-28 | fresh | summarizer-llm | A compromised peer presents a forged service identity to... | 5.4 | 5.0 | 6.0 | 1.5 | 4.6 | Medium | 30d | Review |
| T-5 | fresh | planner-agent | An attacker who can write to the channel between... | 6.3 | 4.5 | 5.0 | 1.5 | 4.6 | Medium | 30d | Review |
| T-21 | fresh | vector-store-a | Backups and exports of embedded documents and metadata on... | 6.3 | 4.0 | 4.0 | 3.0 | 4.6 | Medium | 30d | Review |
| T-47 | fresh | eval-runner | Unsanitised replayed traces and judge verdicts reach... | 5.4 | 5.5 | 5.0 | 1.5 | 4.6 | Medium | 30d | Review |
| I-19 | fresh | model-gateway | Cross-tenant filters on model-gateway are applied in... | 5.5 | 4.5 | 5.5 | 2.5 | 4.6 | Medium | 30d | Review |
| I-32 | fresh | feature-store-2 | Secrets such as the pipeline credential for feature-store-2... | 4.4 | 5.5 | 6.5 | 2.0 | 4.6 | Medium | 30d | Review |
| LLM-19 | fresh | model-gateway | Indirect injection through documents retrieved for... | 5.5 | 4.5 | 5.5 | 2.5 | 4.6 | Medium | 30d | Review |
| LLM-54 | fresh | model-gateway | Encoded or multilingual payloads bypass the keyword filter... | 5.5 | 4.5 | 5.5 | 2.5 | 4.6 | Medium | 30d | Review |
| T-6 | fresh | worker-3 | An attacker who can write to the channel between... | 5.9 | 4.5 | 4.5 | 2.0 | 4.5 | Medium | 30d | Review |
| R-18 | fresh | reviewer-agent | Delegated actions performed by reviewer-agent on behalf of a... | 5.3 | 4.5 | 5.0 | 2.5 | 4.5 | Medium | 30d | Review |
| R-27 | fresh | eval-runner | Clock drift between eval-runner and trace-collector leaves... | 6.5 | 3.0 | 5.0 | 3.0 | 4.5 | Medium | 30d | Review |
| I-11 | fresh | router-agent | Backups of subtask assignments taken from router-agent are... | 4.3 | 5.0 | 5.5 | 3.5 | 4.5 | Medium | 30d | Review |
| I-15 | fresh | reviewer-agent | Cross-tenant filters on reviewer-agent are applied in... | 5.3 | 4.5 | 5.0 | 2.5 | 4.5 | Medium | 30d | Review |
| I-27 | fresh | kb-index | carrier tariffs and customs rules held by kb-index are... | 4.1 | 6.0 | 6.5 | 1.5 | 4.5 | Medium | 30d | Review |
| E-16 | fresh | reviewer-agent | A confused-deputy path lets a low-privilege caller ask... | 5.3 | 4.5 | 5.0 | 2.5 | 4.5 | Medium | 30d | Review |
| AG-24 | fresh | reviewer-agent | Delegation from edge-gateway to reviewer-agent carries the... | 5.3 | 4.5 | 5.0 | 2.5 | 4.5 | Medium | 30d | Review |
| AG-25 | fresh | reviewer-agent | Memory written by reviewer-agent is trusted on later runs... | 5.3 | 4.5 | 5.0 | 2.5 | 4.5 | Medium | 30d | Review |
| LLM-16 | fresh | reviewer-agent | Encoded or multilingual payloads bypass the keyword filter... | 5.3 | 4.5 | 5.0 | 2.5 | 4.5 | Medium | 30d | Review |
| T-46 | fresh | reviewer-agent | Configuration of reviewer-agent can be rewritten by any... | 5.9 | 4.0 | 5.5 | 1.5 | 4.4 | Medium | 30d | Review |
| I-35 | fresh | queue-a2 | A timing or size difference in the responses of queue-a2... | 4.7 | 5.5 | 5.0 | 2.0 | 4.4 | Medium | 30d | Review |
| T-20 | fresh | vector-store-a | Serialised objects arriving from worker-2 are deserialised... | 4.2 | 4.5 | 5.0 | 3.5 | 4.3 | Medium | 30d | Review |
| R-30 | fresh | audit-ledger | Log entries from audit-ledger can be edited or deleted by... | 4.3 | 4.5 | 5.0 | 3.5 | 4.3 | Medium | 30d | Review |
| LLM-59 | fresh | vector-store-a | Anyone who can write to the ingestion path of vector-store-a... | 4.2 | 4.5 | 5.0 | 3.5 | 4.3 | Medium | 30d | Review |
| R-8 | fresh | intake-agent | Clock drift between intake-agent and edge-gateway leaves... | 5.4 | 4.0 | 4.0 | 2.5 | 4.2 | Medium | 30d | Review |
| R-22 | fresh | summarizer-llm | Actions taken through summarizer-llm are logged without the... | 4.1 | 4.5 | 5.0 | 3.5 | 4.2 | Medium | 30d | Review |
| I-6 | fresh | intake-agent | A timing or size difference in the responses of intake-agent... | 5.4 | 4.0 | 4.0 | 2.5 | 4.2 | Medium | 30d | Review |
| I-44 | fresh | intake-agent | Backups of free-text shipment requests taken from... | 5.4 | 4.0 | 4.0 | 2.5 | 4.2 | Medium | 30d | Review |
| E-6 | fresh | intake-agent | Role claims carried in the service token presented to... | 5.4 | 4.0 | 4.0 | 2.5 | 4.2 | Medium | 30d | Review |
| AG-1 | fresh | intake-agent | Memory written by intake-agent is trusted on later runs, so... | 5.4 | 4.0 | 4.0 | 2.5 | 4.2 | Medium | 30d | Review |
| AG-2 | fresh | intake-agent | intake-agent retries failed actions on its own, repeating... | 5.4 | 4.0 | 4.0 | 2.5 | 4.2 | Medium | 30d | Review |
| LLM-4 | fresh | intake-agent | Encoded or multilingual payloads bypass the keyword filter... | 5.4 | 4.0 | 4.0 | 2.5 | 4.2 | Medium | 30d | Review |
| T-22 | fresh | vector-store-a | Unsanitised embedded documents and metadata reach... | 2.2 | 6.0 | 5.0 | 4.0 | 4.1 | Medium | 30d | Review |
| T-40 | fresh | policy-engine | Serialised objects arriving from audit-ledger are... | 4.9 | 4.0 | 4.0 | 3.0 | 4.1 | Medium | 30d | Review |
| R-12 | fresh | planner-agent | Operators approve changes to task plans and tool selections... | 4.3 | 4.0 | 4.5 | 3.5 | 4.1 | Medium | 30d | Review |
| R-15 | fresh | router-agent | Log entries from router-agent can be edited or deleted by... | 4.1 | 4.0 | 5.0 | 3.5 | 4.1 | Medium | 30d | Review |
| R-26 | fresh | trace-collector | Operators approve changes to prompts, completions and tool... | 4.6 | 4.5 | 4.5 | 2.5 | 4.1 | Medium | 30d | Review |
| R-28 | fresh | policy-engine | Operators approve changes to guardrail rules and approval... | 5.0 | 3.5 | 4.5 | 3.0 | 4.1 | Medium | 30d | Review |
| R-29 | fresh | policy-engine | Actions taken through policy-engine are logged without the... | 5.0 | 3.5 | 4.5 | 3.0 | 4.1 | Medium | 30d | Review |
| R-33 | fresh | trace-collector | Actions taken through trace-collector are logged without the... | 4.7 | 4.5 | 3.5 | 3.0 | 4.1 | Medium | 30d | Review |
| I-12 | fresh | router-agent | Cross-tenant filters on router-agent are applied in... | 2.7 | 6.0 | 6.5 | 2.0 | 4.1 | Medium | 30d | Review |
| I-33 | fresh | queue-a2 | Logs and traces emitted by queue-a2 include raw task and... | 2.4 | 6.5 | 6.5 | 1.5 | 4.1 | Medium | 30d | Review |
| I-39 | fresh | policy-engine | guardrail rules and approval decisions held by policy-engine... | 5.0 | 3.5 | 4.5 | 3.0 | 4.1 | Medium | 30d | Review |
| AG-39 | fresh | policy-engine | policy-engine retries failed actions on its own, repeating... | 5.0 | 3.5 | 4.5 | 3.0 | 4.1 | Medium | 30d | Review |
| AG-40 | fresh | policy-engine | policy-engine can start further agents or processes on... | 5.0 | 3.5 | 4.5 | 3.0 | 4.1 | Medium | 30d | Review |
| LLM-51 | fresh | policy-engine | An attacker splits a payload across several messages so that... | 5.0 | 3.5 | 4.5 | 3.0 | 4.1 | Medium | 30d | Review |
| R-16 | fresh | worker-2 | Operators approve changes to work orders and route... | 4.8 | 3.5 | 5.0 | 2.0 | 3.9 | Low | 90d | Review |
| R-10 | fresh | planner-agent | Delegated actions performed by planner-agent on behalf of a... | 4.3 | 4.0 | 4.5 | 2.0 | 3.8 | Low | 90d | Review |
| R-9 | fresh | planner-agent | Clock drift between planner-agent and router-agent leaves... | 3.4 | 4.0 | 4.5 | 3.0 | 3.7 | Low | 90d | Review |
| R-14 | fresh | router-agent | Actions taken through router-agent are logged without the... | 3.5 | 3.5 | 5.0 | 3.5 | 3.7 | Low | 90d | Review |
| R-20 | fresh | embed-service-2 | Clock drift between embed-service-2 and vector-store-a... | 2.7 | 5.0 | 5.0 | 2.5 | 3.7 | Low | 90d | Review |
| I-7 | fresh | planner-agent | A timing or size difference in the responses of... | 3.4 | 4.0 | 4.5 | 3.0 | 3.7 | Low | 90d | Review |
| E-8 | fresh | planner-agent | planner-agent runs with broader permissions than its... | 3.4 | 4.0 | 4.5 | 3.0 | 3.7 | Low | 90d | Review |
| E-9 | fresh | planner-agent | A confused-deputy path lets a low-privilege caller ask... | 3.4 | 4.0 | 4.5 | 3.0 | 3.7 | Low | 90d | Review |
| AG-4 | fresh | planner-agent | planner-agent runs without a budget on steps or spend, so a... | 3.4 | 4.0 | 4.5 | 3.0 | 3.7 | Low | 90d | Review |
| AG-5 | fresh | planner-agent | Delegation from trace-collector to planner-agent carries the... | 3.4 | 4.0 | 4.5 | 3.0 | 3.7 | Low | 90d | Review |
| LLM-7 | fresh | planner-agent | Indirect injection through documents retrieved for... | 3.4 | 4.0 | 4.5 | 3.0 | 3.7 | Low | 90d | Review |
| R-11 | fresh | planner-agent | Failed and rejected attempts against planner-agent are not... | 4.3 | 3.5 | 5.0 | 1.5 | 3.6 | Low | 90d | Review |
| R-21 | fresh | embed-service-2 | Delegated actions performed by embed-service-2 on behalf of... | 4.3 | 3.5 | 5.0 | 1.5 | 3.6 | Low | 90d | Review |
| R-32 | fresh | tool-server-1 | Operators approve changes to tool call arguments and results... | 4.4 | 3.5 | 5.0 | 1.5 | 3.6 | Low | 90d | Review |
| R-13 | fresh | router-agent | Operators approve changes to subtask assignments through a... | 3.5 | 3.5 | 5.5 | 2.0 | 3.5 | Low | 90d | Review |
| R-19 | fresh | model-gateway | Failed and rejected attempts against model-gateway are not... | 3.5 | 4.0 | 4.5 | 2.0 | 3.5 | Low | 90d | Review |
| D-9 | fresh | router-agent | Retry storms from worker-2 multiply the load on router-agent... | 3.5 | 3.5 | 5.5 | 2.0 | 3.5 | Low | 90d | Review |
| E-10 | fresh | router-agent | A confused-deputy path lets a low-privilege caller ask... | 3.5 | 3.5 | 5.5 | 2.0 | 3.5 | Low | 90d | Review |
| AG-11 | fresh | router-agent | router-agent can start further agents or processes on... | 3.5 | 3.5 | 5.5 | 2.0 | 3.5 | Low | 90d | Review |
| AG-12 | fresh | router-agent | router-agent can act on subtask assignments without a human... | 3.5 | 3.5 | 5.5 | 2.0 | 3.5 | Low | 90d | Review |
| AG-13 | fresh | router-agent | An attacker chains two individually safe tools through... | 3.5 | 3.5 | 5.5 | 2.0 | 3.5 | Low | 90d | Review |
| R-24 | fresh | scheduler-1 | Clock drift between scheduler-1 and queue-a2 leaves events... | 3.1 | 3.0 | 4.5 | 3.5 | 3.4 | Low | 90d | Review |
| R-25 | fresh | scheduler-1 | Delegated actions performed by scheduler-1 on behalf of a... | 3.1 | 3.0 | 4.5 | 3.5 | 3.4 | Low | 90d | Review |
| E-27 | fresh | scheduler-1 | Multi-tenant separation in scheduler-1 depends on a request... | 3.1 | 3.0 | 4.5 | 3.5 | 3.4 | Low | 90d | Review |
| AG-38 | fresh | scheduler-1 | scheduler-1 can start further agents or processes on... | 3.1 | 3.0 | 4.5 | 3.5 | 3.4 | Low | 90d | Review |
| AG-44 | fresh | scheduler-1 | scheduler-1 can act on recurring planning triggers without a... | 3.1 | 3.0 | 4.5 | 3.5 | 3.4 | Low | 90d | Review |
| R-17 | fresh | worker-3 | Operators approve changes to work orders and draft documents... | 2.4 | 3.5 | 6.0 | 2.0 | 3.2 | Low | 90d | Review |
| I-14 | fresh | worker-3 | A timing or size difference in the responses of worker-3... | 2.4 | 3.5 | 6.0 | 2.0 | 3.2 | Low | 90d | Review |
| D-11 | fresh | worker-3 | Retry storms from router-agent multiply the load on worker-3... | 2.4 | 3.5 | 6.0 | 2.0 | 3.2 | Low | 90d | Review |
| D-12 | fresh | worker-3 | A slow-read attack holds connections to worker-3 open and... | 2.4 | 3.5 | 6.0 | 2.0 | 3.2 | Low | 90d | Review |
| AG-20 | fresh | worker-3 | worker-3 can act on work orders and draft documents without... | 2.4 | 3.5 | 6.0 | 2.0 | 3.2 | Low | 90d | Review |
| AG-22 | fresh | worker-3 | Tool results returned to worker-3 are fed back into the next... | 2.4 | 3.5 | 6.0 | 2.0 | 3.2 | Low | 90d | Review |
| LLM-14 | fresh | worker-3 | An attacker splits a payload across several messages so that... | 2.4 | 3.5 | 6.0 | 2.0 | 3.2 | Low | 90d | Review |

> **Correlated findings**: for correlation groups (Section 4a of the source threat model), the primary finding is scored independently. Correlated peer findings inherit the primary's scores to keep the group consistent.

---

## 3. Dimensional Breakdown

Per-finding detail showing the scoring rationale for each dimension, in the order of Section 2.

### S-3 — partner-feed

**Threat**: A shared or long-lived webhook signature on partner-feed lets anyone who obtains one copy authenticate as every tenant that uses the same deployment profile.

**Category**: spoofing | **Original Risk Level**: High | **Composite**: 9.1 (Critical)

#### CVSS 3.1 Base

**Score**: 9.1 | **Vector**: `CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Network | Reachable over the network |
| Attack Complexity (AC) | Low | No special conditions |
| Privileges Required (PR) | None | No privileges needed |
| User Interaction (UI) | None | No user action needed |
| Scope (S) | Unchanged | Impact stays in the component |
| Confidentiality (C) | High | Broad disclosure |
| Integrity (I) | High | Broad modification |
| Availability (A) | None | No loss of service |

#### Exploitability

**Score**: 9.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 8 | Documented and widely used |
| Attack Complexity | 9 | A single step suffices |
| Tooling Availability | 10 | Common tools apply |
| Skill Level | 9 | Little skill needed |

#### Scalability

**Score**: 9.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 10 | Fully automatable |
| Target Scope | 9 | Every instance |
| Resource Requirements | 9 | Minimal resources |
| Detection Difficulty | 8 | Blends with normal use |

#### Reachability

**Score**: 9.5 | **Trust Zone**: Public Internet (Untrusted)

partner-feed sits in the Public Internet. The zone baseline is 9.0 and the refinement for this finding gives 9.5.

---

### S-1 — client-portal

**Threat**: An attacker replays a captured session cookie against client-portal, which does not bind the credential to the session or channel it was issued for, so the replay is accepted as the original caller.

**Category**: spoofing | **Original Risk Level**: Medium | **Composite**: 8.5 (High)

#### CVSS 3.1 Base

**Score**: 9.9 | **Vector**: `CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:L/A:L`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Network | Reachable over the network |
| Attack Complexity (AC) | Low | No special conditions |
| Privileges Required (PR) | None | No privileges needed |
| User Interaction (UI) | None | No user action needed |
| Scope (S) | Changed | Impact crosses a boundary |
| Confidentiality (C) | High | Broad disclosure |
| Integrity (I) | Low | Limited modification |
| Availability (A) | Low | Degraded service |

#### Exploitability

**Score**: 7.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 8 | Documented and widely used |
| Attack Complexity | 8 | A single step suffices |
| Tooling Availability | 7 | Common tools apply |
| Skill Level | 7 | Little skill needed |

#### Scalability

**Score**: 7.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 8 | Fully automatable |
| Target Scope | 6 | A class of targets |
| Resource Requirements | 8 | Minimal resources |
| Detection Difficulty | 8 | Blends with normal use |

#### Reachability

**Score**: 8.5 | **Trust Zone**: Public Internet (Untrusted)

client-portal sits in the Public Internet. The zone baseline is 9.0 and the refinement for this finding gives 8.5.

---

### S-2 — partner-feed

**Threat**: A compromised peer presents a forged service identity to partner-feed, and partner-feed accepts the claim without verifying the signature chain back to the issuing authority.

**Category**: spoofing | **Original Risk Level**: Medium | **Composite**: 8.2 (High)

#### CVSS 3.1 Base

**Score**: 7.6 | **Vector**: `CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:L/A:L`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Network | Reachable over the network |
| Attack Complexity (AC) | Low | No special conditions |
| Privileges Required (PR) | None | No privileges needed |
| User Interaction (UI) | Required | A user must act |
| Scope (S) | Unchanged | Impact stays in the component |
| Confidentiality (C) | High | Broad disclosure |
| Integrity (I) | Low | Limited modification |
| Availability (A) | Low | Degraded service |

#### Exploitability

**Score**: 8.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 8 | Documented and widely used |
| Attack Complexity | 8 | A single step suffices |
| Tooling Availability | 7 | Common tools apply |
| Skill Level | 9 | Little skill needed |

#### Scalability

**Score**: 7.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 9 | Fully automatable |
| Target Scope | 6 | A class of targets |
| Resource Requirements | 8 | Minimal resources |
| Detection Difficulty | 7 | Blends with normal use |

#### Reachability

**Score**: 10.0 | **Trust Zone**: Public Internet (Untrusted)

partner-feed sits in the Public Internet. The zone baseline is 9.0 and the refinement for this finding gives 10.0.

---

### S-4 — edge-gateway

**Threat**: A shared or long-lived bearer token on edge-gateway lets anyone who obtains one copy authenticate as every tenant that uses the same deployment profile.

**Category**: spoofing | **Original Risk Level**: Medium | **Composite**: 8.1 (High)

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

**Score**: 8.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 7 | Documented and widely used |
| Attack Complexity | 8 | A single step suffices |
| Tooling Availability | 9 | Common tools apply |
| Skill Level | 10 | Little skill needed |

#### Scalability

**Score**: 8.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 9 | Fully automatable |
| Target Scope | 8 | Every instance |
| Resource Requirements | 10 | Minimal resources |
| Detection Difficulty | 7 | Blends with normal use |

#### Reachability

**Score**: 7.0 | **Trust Zone**: Edge DMZ (Semi-trusted)

edge-gateway sits in the Edge DMZ. The zone baseline is 6.5 and the refinement for this finding gives 7.0.

---

### LLM-3 — edge-gateway

**Threat**: An attacker splits a payload across several messages so that no single message trips the filter in front of edge-gateway.

**Category**: llm | **Original Risk Level**: Medium | **Composite**: 8.1 (High)

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
| Known Techniques | 8 | Documented and widely used |
| Attack Complexity | 8 | A single step suffices |
| Tooling Availability | 8 | Common tools apply |
| Skill Level | 10 | Little skill needed |

#### Scalability

**Score**: 9.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 9 | Fully automatable |
| Target Scope | 10 | Every instance |
| Resource Requirements | 10 | Minimal resources |
| Detection Difficulty | 7 | Blends with normal use |

#### Reachability

**Score**: 6.5 | **Trust Zone**: Edge DMZ (Semi-trusted)

edge-gateway sits in the Edge DMZ. The zone baseline is 6.5 and the refinement for this finding gives 6.5.

---

### E-3 — edge-gateway

**Threat**: An administrative interface of edge-gateway is reachable from the same network as ordinary callers and relies on a single shared password.

**Category**: privilege-escalation | **Original Risk Level**: Critical | **Composite**: 8.0 (High)

#### CVSS 3.1 Base

**Score**: 9.3 | **Vector**: `CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H`

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

**Score**: 7.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 8 | Documented and widely used |
| Attack Complexity | 8 | A single step suffices |
| Tooling Availability | 6 | Tools need adaptation |
| Skill Level | 6 | Intermediate skill |

#### Scalability

**Score**: 8.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 9 | Fully automatable |
| Target Scope | 5 | A class of targets |
| Resource Requirements | 10 | Minimal resources |
| Detection Difficulty | 8 | Blends with normal use |

#### Reachability

**Score**: 7.0 | **Trust Zone**: Edge DMZ (Semi-trusted)

edge-gateway sits in the Edge DMZ. The zone baseline is 6.5 and the refinement for this finding gives 7.0.

---

### E-4 — edge-gateway

**Threat**: edge-gateway runs with broader permissions than its function needs, so a flaw in handling inbound API requests yields access to unrelated resources.

**Category**: privilege-escalation | **Original Risk Level**: High | **Composite**: 8.0 (High)

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

**Score**: 7.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 9 | Documented and widely used |
| Attack Complexity | 9 | A single step suffices |
| Tooling Availability | 5 | Tools need adaptation |
| Skill Level | 7 | Little skill needed |

#### Scalability

**Score**: 7.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 7 | Fully automatable |
| Target Scope | 7 | Every instance |
| Resource Requirements | 8 | Minimal resources |
| Detection Difficulty | 8 | Blends with normal use |

#### Reachability

**Score**: 6.0 | **Trust Zone**: Edge DMZ (Semi-trusted)

edge-gateway sits in the Edge DMZ. The zone baseline is 6.5 and the refinement for this finding gives 6.0.

---

### D-1 — edge-gateway

**Threat**: A dependency of edge-gateway becomes unavailable and the failure cascades because edge-gateway waits on it synchronously for every request.

**Category**: denial-of-service | **Original Risk Level**: High | **Composite**: 7.9 (High)

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

**Score**: 9.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 10 | Documented and widely used |
| Attack Complexity | 9 | A single step suffices |
| Tooling Availability | 9 | Common tools apply |
| Skill Level | 10 | Little skill needed |

#### Scalability

**Score**: 7.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 8 | Fully automatable |
| Target Scope | 8 | Every instance |
| Resource Requirements | 6 | Moderate resources |
| Detection Difficulty | 6 | Detectable with monitoring |

#### Reachability

**Score**: 5.5 | **Trust Zone**: Edge DMZ (Semi-trusted)

edge-gateway sits in the Edge DMZ. The zone baseline is 6.5 and the refinement for this finding gives 5.5.

---

### S-5 — auth-broker

**Threat**: A shared or long-lived refresh token on auth-broker lets anyone who obtains one copy authenticate as every tenant that uses the same deployment profile.

**Category**: spoofing | **Original Risk Level**: Low | **Composite**: 7.6 (High)

#### CVSS 3.1 Base

**Score**: 7.4 | **Vector**: `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:L/I:L/A:L`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Network | Reachable over the network |
| Attack Complexity (AC) | Low | No special conditions |
| Privileges Required (PR) | Low | A basic account is needed |
| User Interaction (UI) | None | No user action needed |
| Scope (S) | Changed | Impact crosses a boundary |
| Confidentiality (C) | Low | Limited disclosure |
| Integrity (I) | Low | Limited modification |
| Availability (A) | Low | Degraded service |

#### Exploitability

**Score**: 9.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 8 | Documented and widely used |
| Attack Complexity | 10 | A single step suffices |
| Tooling Availability | 9 | Common tools apply |
| Skill Level | 9 | Little skill needed |

#### Scalability

**Score**: 8.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 10 | Fully automatable |
| Target Scope | 6 | A class of targets |
| Resource Requirements | 9 | Minimal resources |
| Detection Difficulty | 7 | Blends with normal use |

#### Reachability

**Score**: 5.5 | **Trust Zone**: Edge DMZ (Semi-trusted)

auth-broker sits in the Edge DMZ. The zone baseline is 6.5 and the refinement for this finding gives 5.5.

---

### E-5 — auth-broker

**Threat**: Role claims carried in the refresh token presented to auth-broker are honoured without confirmation against the authoritative directory.

**Category**: privilege-escalation | **Original Risk Level**: High | **Composite**: 7.6 (High)

#### CVSS 3.1 Base

**Score**: 9.0 | **Vector**: `CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:H/I:H/A:H`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Network | Reachable over the network |
| Attack Complexity (AC) | Low | No special conditions |
| Privileges Required (PR) | Low | A basic account is needed |
| User Interaction (UI) | Required | A user must act |
| Scope (S) | Changed | Impact crosses a boundary |
| Confidentiality (C) | High | Broad disclosure |
| Integrity (I) | High | Broad modification |
| Availability (A) | High | Loss of service |

#### Exploitability

**Score**: 7.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 6 | Described in research |
| Attack Complexity | 9 | A single step suffices |
| Tooling Availability | 6 | Tools need adaptation |
| Skill Level | 9 | Little skill needed |

#### Scalability

**Score**: 7.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 10 | Fully automatable |
| Target Scope | 7 | Every instance |
| Resource Requirements | 8 | Minimal resources |
| Detection Difficulty | 5 | Detectable with monitoring |

#### Reachability

**Score**: 5.5 | **Trust Zone**: Edge DMZ (Semi-trusted)

auth-broker sits in the Edge DMZ. The zone baseline is 6.5 and the refinement for this finding gives 5.5.

---

### T-1 — edge-gateway

**Threat**: An attacker who can write to the channel between client-portal and edge-gateway modifies inbound API requests in transit because messages carry no integrity protection of their own.

**Category**: tampering | **Original Risk Level**: Medium | **Composite**: 7.5 (High)

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
| Scriptability | 8 | Fully automatable |
| Target Scope | 5 | A class of targets |
| Resource Requirements | 7 | Minimal resources |
| Detection Difficulty | 6 | Detectable with monitoring |

#### Reachability

**Score**: 7.0 | **Trust Zone**: Edge DMZ (Semi-trusted)

edge-gateway sits in the Edge DMZ. The zone baseline is 6.5 and the refinement for this finding gives 7.0.

---

### E-1 — edge-gateway

**Threat**: Object identifiers in requests to edge-gateway are trusted without an ownership check, so a caller can read or change inbound API requests that belong to others.

**Category**: privilege-escalation | **Original Risk Level**: Low | **Composite**: 7.5 (High)

#### CVSS 3.1 Base

**Score**: 8.2 | **Vector**: `CVSS:3.1/AV:A/AC:L/PR:L/UI:N/S:C/C:L/I:H/A:L`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Adjacent | Needs an adjacent network |
| Attack Complexity (AC) | Low | No special conditions |
| Privileges Required (PR) | Low | A basic account is needed |
| User Interaction (UI) | None | No user action needed |
| Scope (S) | Changed | Impact crosses a boundary |
| Confidentiality (C) | Low | Limited disclosure |
| Integrity (I) | High | Broad modification |
| Availability (A) | Low | Degraded service |

#### Exploitability

**Score**: 7.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 8 | Documented and widely used |
| Attack Complexity | 9 | A single step suffices |
| Tooling Availability | 5 | Tools need adaptation |
| Skill Level | 8 | Little skill needed |

#### Scalability

**Score**: 7.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 7 | Fully automatable |
| Target Scope | 7 | Every instance |
| Resource Requirements | 8 | Minimal resources |
| Detection Difficulty | 6 | Detectable with monitoring |

#### Reachability

**Score**: 6.5 | **Trust Zone**: Edge DMZ (Semi-trusted)

edge-gateway sits in the Edge DMZ. The zone baseline is 6.5 and the refinement for this finding gives 6.5.

---

### E-2 — edge-gateway

**Threat**: Role claims carried in the bearer token presented to edge-gateway are honoured without confirmation against the authoritative directory.

**Category**: privilege-escalation | **Original Risk Level**: Medium | **Composite**: 7.5 (High)

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

**Score**: 7.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 8 | Documented and widely used |
| Attack Complexity | 6 | Needs some preparation |
| Tooling Availability | 8 | Common tools apply |
| Skill Level | 6 | Intermediate skill |

#### Scalability

**Score**: 7.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 7 | Fully automatable |
| Target Scope | 5 | A class of targets |
| Resource Requirements | 9 | Minimal resources |
| Detection Difficulty | 7 | Blends with normal use |

#### Reachability

**Score**: 6.0 | **Trust Zone**: Edge DMZ (Semi-trusted)

edge-gateway sits in the Edge DMZ. The zone baseline is 6.5 and the refinement for this finding gives 6.0.

---

### LLM-34 — memory-store

**Threat**: A delayed trigger planted in task history and operator preferences on memory-store changes behaviour only after a date or phrase, so pre-release testing never sees it.

**Category**: llm | **Original Risk Level**: Medium | **Composite**: 7.5 (High)

#### CVSS 3.1 Base

**Score**: 9.3 | **Vector**: `CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:L/I:H/A:N`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Network | Reachable over the network |
| Attack Complexity (AC) | Low | No special conditions |
| Privileges Required (PR) | None | No privileges needed |
| User Interaction (UI) | None | No user action needed |
| Scope (S) | Changed | Impact crosses a boundary |
| Confidentiality (C) | Low | Limited disclosure |
| Integrity (I) | High | Broad modification |
| Availability (A) | None | No loss of service |

#### Exploitability

**Score**: 8.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 9 | Documented and widely used |
| Attack Complexity | 9 | A single step suffices |
| Tooling Availability | 6 | Tools need adaptation |
| Skill Level | 10 | Little skill needed |

#### Scalability

**Score**: 6.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 7 | Fully automatable |
| Target Scope | 6 | A class of targets |
| Resource Requirements | 9 | Minimal resources |
| Detection Difficulty | 4 | Detectable with monitoring |

#### Reachability

**Score**: 3.5 | **Trust Zone**: Data Zone (Trusted)

memory-store sits in the Data Zone. The zone baseline is 2.5 and the refinement for this finding gives 3.5.

---

### I-4 — auth-broker

**Threat**: credential assertions and session grants held by auth-broker are readable by any service in the Edge DMZ that shares the same network role, because access is granted by network position.

**Category**: info-disclosure | **Original Risk Level**: Low | **Composite**: 7.4 (High)

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

**Score**: 8.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 10 | Documented and widely used |
| Attack Complexity | 7 | A single step suffices |
| Tooling Availability | 7 | Common tools apply |
| Skill Level | 10 | Little skill needed |

#### Scalability

**Score**: 8.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 10 | Fully automatable |
| Target Scope | 8 | Every instance |
| Resource Requirements | 9 | Minimal resources |
| Detection Difficulty | 5 | Detectable with monitoring |

#### Reachability

**Score**: 7.0 | **Trust Zone**: Edge DMZ (Semi-trusted)

auth-broker sits in the Edge DMZ. The zone baseline is 6.5 and the refinement for this finding gives 7.0.

---

### D-3 — auth-broker

**Threat**: Retry storms from edge-gateway multiply the load on auth-broker when it slows down, turning a brief delay into a sustained outage.

**Category**: denial-of-service | **Original Risk Level**: Low | **Composite**: 7.4 (High)

#### CVSS 3.1 Base

**Score**: 6.3 | **Vector**: `CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:L/I:N/A:H`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Network | Reachable over the network |
| Attack Complexity (AC) | Low | No special conditions |
| Privileges Required (PR) | Low | A basic account is needed |
| User Interaction (UI) | Required | A user must act |
| Scope (S) | Unchanged | Impact stays in the component |
| Confidentiality (C) | Low | Limited disclosure |
| Integrity (I) | None | No modification |
| Availability (A) | High | Loss of service |

#### Exploitability

**Score**: 9.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 10 | Documented and widely used |
| Attack Complexity | 10 | A single step suffices |
| Tooling Availability | 7 | Common tools apply |
| Skill Level | 9 | Little skill needed |

#### Scalability

**Score**: 8.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 10 | Fully automatable |
| Target Scope | 10 | Every instance |
| Resource Requirements | 6 | Moderate resources |
| Detection Difficulty | 6 | Detectable with monitoring |

#### Reachability

**Score**: 6.5 | **Trust Zone**: Edge DMZ (Semi-trusted)

auth-broker sits in the Edge DMZ. The zone baseline is 6.5 and the refinement for this finding gives 6.5.

---

### LLM-50 — eval-runner

**Threat**: Records written into eval-runner by low-trust sources are later used as ground truth, so an attacker who plants entries shifts model answers.

**Category**: llm | **Original Risk Level**: Medium | **Composite**: 7.4 (High)

#### CVSS 3.1 Base

**Score**: 10.0 | **Vector**: `CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:N`

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

**Score**: 8.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 9 | Documented and widely used |
| Attack Complexity | 8 | A single step suffices |
| Tooling Availability | 8 | Common tools apply |
| Skill Level | 7 | Little skill needed |

#### Scalability

**Score**: 7.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 8 | Fully automatable |
| Target Scope | 8 | Every instance |
| Resource Requirements | 9 | Minimal resources |
| Detection Difficulty | 5 | Detectable with monitoring |

#### Reachability

**Score**: 2.0 | **Trust Zone**: Operations Zone (Trusted)

eval-runner sits in the Operations Zone. The zone baseline is 2.5 and the refinement for this finding gives 2.0.

---

### LLM-11 — router-agent

**Threat**: Prompt content logged by planner-agent is later replayed to router-agent for evaluation, carrying planted instructions into a trusted context.

**Category**: llm | **Original Risk Level**: Critical | **Composite**: 7.3 (High)

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

**Score**: 8.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 9 | Documented and widely used |
| Attack Complexity | 7 | A single step suffices |
| Tooling Availability | 8 | Common tools apply |
| Skill Level | 10 | Little skill needed |

#### Scalability

**Score**: 6.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 8 | Fully automatable |
| Target Scope | 6 | A class of targets |
| Resource Requirements | 8 | Minimal resources |
| Detection Difficulty | 4 | Detectable with monitoring |

#### Reachability

**Score**: 3.5 | **Trust Zone**: Agent Runtime Zone (Trusted)

router-agent sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 3.5.

---

### D-2 — auth-broker

**Threat**: A single oversized or deeply nested payload makes auth-broker spend disproportionate memory and CPU parsing credential assertions and session grants.

**Category**: denial-of-service | **Original Risk Level**: Low | **Composite**: 7.2 (High)

#### CVSS 3.1 Base

**Score**: 6.4 | **Vector**: `CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:L/I:L/A:H`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Network | Reachable over the network |
| Attack Complexity (AC) | High | Needs specific conditions |
| Privileges Required (PR) | None | No privileges needed |
| User Interaction (UI) | Required | A user must act |
| Scope (S) | Unchanged | Impact stays in the component |
| Confidentiality (C) | Low | Limited disclosure |
| Integrity (I) | Low | Limited modification |
| Availability (A) | High | Loss of service |

#### Exploitability

**Score**: 9.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 8 | Documented and widely used |
| Attack Complexity | 10 | A single step suffices |
| Tooling Availability | 8 | Common tools apply |
| Skill Level | 10 | Little skill needed |

#### Scalability

**Score**: 7.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 10 | Fully automatable |
| Target Scope | 9 | Every instance |
| Resource Requirements | 5 | Moderate resources |
| Detection Difficulty | 4 | Detectable with monitoring |

#### Reachability

**Score**: 6.0 | **Trust Zone**: Edge DMZ (Semi-trusted)

auth-broker sits in the Edge DMZ. The zone baseline is 6.5 and the refinement for this finding gives 6.0.

---

### OI-8 — intake-agent

**Threat**: Structured output from intake-agent is trusted by edge-gateway as already validated, so a malformed field flows straight into business logic.

**Category**: llm | **Original Risk Level**: Medium | **Composite**: 7.2 (High)

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
| Known Techniques | 7 | Documented and widely used |
| Attack Complexity | 8 | A single step suffices |
| Tooling Availability | 8 | Common tools apply |
| Skill Level | 7 | Little skill needed |

#### Scalability

**Score**: 7.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 5 | Partly automatable |
| Target Scope | 8 | Every instance |
| Resource Requirements | 8 | Minimal resources |
| Detection Difficulty | 7 | Blends with normal use |

#### Reachability

**Score**: 3.0 | **Trust Zone**: Agent Runtime Zone (Trusted)

intake-agent sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 3.0.

---

### OI-12 — planner-agent

**Threat**: File paths or names produced by planner-agent are used to write files, letting crafted output reach locations outside the intended directory.

**Category**: llm | **Original Risk Level**: Medium | **Composite**: 7.2 (High)

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

**Score**: 8.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 9 | Documented and widely used |
| Attack Complexity | 9 | A single step suffices |
| Tooling Availability | 6 | Tools need adaptation |
| Skill Level | 10 | Little skill needed |

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

planner-agent sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 2.0.

---

### S-40 — edge-gateway

**Threat**: An unauthenticated callback or health route on edge-gateway accepts requests that downstream code treats as if they had come from auth-broker.

**Category**: spoofing | **Original Risk Level**: High | **Composite**: 7.1 (High)

#### CVSS 3.1 Base

**Score**: 6.5 | **Vector**: `CVSS:3.1/AV:N/AC:H/PR:L/UI:R/S:C/C:H/I:L/A:N`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Network | Reachable over the network |
| Attack Complexity (AC) | High | Needs specific conditions |
| Privileges Required (PR) | Low | A basic account is needed |
| User Interaction (UI) | Required | A user must act |
| Scope (S) | Changed | Impact crosses a boundary |
| Confidentiality (C) | High | Broad disclosure |
| Integrity (I) | Low | Limited modification |
| Availability (A) | None | No loss of service |

#### Exploitability

**Score**: 8.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 8 | Documented and widely used |
| Attack Complexity | 9 | A single step suffices |
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

**Score**: 5.5 | **Trust Zone**: Edge DMZ (Semi-trusted)

edge-gateway sits in the Edge DMZ. The zone baseline is 6.5 and the refinement for this finding gives 5.5.

---

### I-1 — edge-gateway

**Threat**: Secrets such as the bearer token for edge-gateway appear in process arguments and environment dumps that diagnostic tooling captures.

**Category**: info-disclosure | **Original Risk Level**: Low | **Composite**: 7.1 (High)

#### CVSS 3.1 Base

**Score**: 6.3 | **Vector**: `CVSS:3.1/AV:A/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:L`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Adjacent | Needs an adjacent network |
| Attack Complexity (AC) | Low | No special conditions |
| Privileges Required (PR) | Low | A basic account is needed |
| User Interaction (UI) | None | No user action needed |
| Scope (S) | Unchanged | Impact stays in the component |
| Confidentiality (C) | High | Broad disclosure |
| Integrity (I) | None | No modification |
| Availability (A) | Low | Degraded service |

#### Exploitability

**Score**: 9.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 10 | Documented and widely used |
| Attack Complexity | 8 | A single step suffices |
| Tooling Availability | 9 | Common tools apply |
| Skill Level | 9 | Little skill needed |

#### Scalability

**Score**: 7.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 7 | Fully automatable |
| Target Scope | 9 | Every instance |
| Resource Requirements | 9 | Minimal resources |
| Detection Difficulty | 5 | Detectable with monitoring |

#### Reachability

**Score**: 5.5 | **Trust Zone**: Edge DMZ (Semi-trusted)

edge-gateway sits in the Edge DMZ. The zone baseline is 6.5 and the refinement for this finding gives 5.5.

---

### I-2 — edge-gateway

**Threat**: Verbose error responses from edge-gateway reveal internal paths, query text and identifiers of inbound API requests to any caller who can trigger a failure.

**Category**: info-disclosure | **Original Risk Level**: Medium | **Composite**: 7.1 (High)

**Correlation Group**: Scores inherited from primary finding I-1 (CG-1). Dimensional detail is recorded on the primary.

**Score**: 6.3 | **Vector**: `CVSS:3.1/AV:A/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:L`

---

### I-43 — edge-gateway

**Threat**: Logs and traces emitted by edge-gateway include raw inbound API requests, so anyone with access to the logging pipeline can read content meant for one tenant.

**Category**: info-disclosure | **Original Risk Level**: High | **Composite**: 7.1 (High)

#### CVSS 3.1 Base

**Score**: 6.3 | **Vector**: `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:L`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Network | Reachable over the network |
| Attack Complexity (AC) | Low | No special conditions |
| Privileges Required (PR) | Low | A basic account is needed |
| User Interaction (UI) | None | No user action needed |
| Scope (S) | Unchanged | Impact stays in the component |
| Confidentiality (C) | Low | Limited disclosure |
| Integrity (I) | Low | Limited modification |
| Availability (A) | Low | Degraded service |

#### Exploitability

**Score**: 7.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 7 | Documented and widely used |
| Attack Complexity | 7 | A single step suffices |
| Tooling Availability | 9 | Common tools apply |
| Skill Level | 7 | Little skill needed |

#### Scalability

**Score**: 8.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 10 | Fully automatable |
| Target Scope | 9 | Every instance |
| Resource Requirements | 8 | Minimal resources |
| Detection Difficulty | 5 | Detectable with monitoring |

#### Reachability

**Score**: 7.0 | **Trust Zone**: Edge DMZ (Semi-trusted)

edge-gateway sits in the Edge DMZ. The zone baseline is 6.5 and the refinement for this finding gives 7.0.

---

### LLM-1 — edge-gateway

**Threat**: edge-gateway passes conversation history from earlier turns into the model unchanged, so an injection planted earlier keeps working in later turns.

**Category**: llm | **Original Risk Level**: Medium | **Composite**: 7.1 (High)

**Correlation Group**: Scores inherited from primary finding I-1 (CG-1). Dimensional detail is recorded on the primary.

**Score**: 6.3 | **Vector**: `CVSS:3.1/AV:A/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:L`

---

### LLM-2 — edge-gateway

**Threat**: Prompt content logged by client-portal is later replayed to edge-gateway for evaluation, carrying planted instructions into a trusted context.

**Category**: llm | **Original Risk Level**: Medium | **Composite**: 7.1 (High)

**Correlation Group**: Scores inherited from primary finding I-1 (CG-1). Dimensional detail is recorded on the primary.

**Score**: 6.3 | **Vector**: `CVSS:3.1/AV:A/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:L`

---

### LLM-18 — tool-server-1

**Threat**: tool-server-1 passes conversation history from earlier turns into the model unchanged, so an injection planted earlier keeps working in later turns.

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

**Score**: 7.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 7 | Documented and widely used |
| Attack Complexity | 6 | Needs some preparation |
| Tooling Availability | 8 | Common tools apply |
| Skill Level | 7 | Little skill needed |

#### Scalability

**Score**: 7.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 8 | Fully automatable |
| Target Scope | 5 | A class of targets |
| Resource Requirements | 9 | Minimal resources |
| Detection Difficulty | 6 | Detectable with monitoring |

#### Reachability

**Score**: 3.5 | **Trust Zone**: Agent Runtime Zone (Trusted)

tool-server-1 sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 3.5.

---

### LLM-41 — trace-collector

**Threat**: A user message crafted to look like a system directive persuades trace-collector to disclose its configuration or ignore its rules.

**Category**: llm | **Original Risk Level**: High | **Composite**: 7.1 (High)

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
| Known Techniques | 9 | Documented and widely used |
| Attack Complexity | 8 | A single step suffices |
| Tooling Availability | 7 | Common tools apply |
| Skill Level | 6 | Intermediate skill |

#### Scalability

**Score**: 7.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 5 | Partly automatable |
| Target Scope | 7 | Every instance |
| Resource Requirements | 9 | Minimal resources |
| Detection Difficulty | 7 | Blends with normal use |

#### Reachability

**Score**: 2.5 | **Trust Zone**: Operations Zone (Trusted)

trace-collector sits in the Operations Zone. The zone baseline is 2.5 and the refinement for this finding gives 2.5.

---

### LLM-47 — eval-runner

**Threat**: Anyone who can write to the ingestion path of eval-runner can slip in documents that contradict authoritative sources.

**Category**: llm | **Original Risk Level**: Critical | **Composite**: 7.1 (High)

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
| Known Techniques | 9 | Documented and widely used |
| Attack Complexity | 6 | Needs some preparation |
| Tooling Availability | 6 | Tools need adaptation |
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

**Score**: 4.0 | **Trust Zone**: Operations Zone (Trusted)

eval-runner sits in the Operations Zone. The zone baseline is 2.5 and the refinement for this finding gives 4.0.

---

### LLM-48 — eval-runner

**Threat**: Evaluation labels consumed from eval-runner are produced by a judge model that can itself be influenced by planted traces.

**Category**: llm | **Original Risk Level**: Critical | **Composite**: 7.1 (High)

#### CVSS 3.1 Base

**Score**: 9.9 | **Vector**: `CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:L/A:L`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Network | Reachable over the network |
| Attack Complexity (AC) | Low | No special conditions |
| Privileges Required (PR) | None | No privileges needed |
| User Interaction (UI) | None | No user action needed |
| Scope (S) | Changed | Impact crosses a boundary |
| Confidentiality (C) | High | Broad disclosure |
| Integrity (I) | Low | Limited modification |
| Availability (A) | Low | Degraded service |

#### Exploitability

**Score**: 6.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 7 | Documented and widely used |
| Attack Complexity | 6 | Needs some preparation |
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

**Score**: 3.5 | **Trust Zone**: Operations Zone (Trusted)

eval-runner sits in the Operations Zone. The zone baseline is 2.5 and the refinement for this finding gives 3.5.

---

### OI-6 — intake-agent

**Threat**: Text generated by intake-agent is placed into a database query or shell argument without parameterisation, allowing the model to be steered into injection.

**Category**: llm | **Original Risk Level**: High | **Composite**: 7.1 (High)

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

**Score**: 8.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 8 | Documented and widely used |
| Attack Complexity | 8 | A single step suffices |
| Tooling Availability | 6 | Tools need adaptation |
| Skill Level | 10 | Little skill needed |

#### Scalability

**Score**: 7.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 8 | Fully automatable |
| Target Scope | 5 | A class of targets |
| Resource Requirements | 9 | Minimal resources |
| Detection Difficulty | 8 | Blends with normal use |

#### Reachability

**Score**: 3.5 | **Trust Zone**: Agent Runtime Zone (Trusted)

intake-agent sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 3.5.

---

### OI-15 — worker-2

**Threat**: File paths or names produced by worker-2 are used to write files, letting crafted output reach locations outside the intended directory.

**Category**: llm | **Original Risk Level**: Critical | **Composite**: 7.1 (High)

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

**Score**: 7.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 8 | Documented and widely used |
| Attack Complexity | 8 | A single step suffices |
| Tooling Availability | 8 | Common tools apply |
| Skill Level | 6 | Intermediate skill |

#### Scalability

**Score**: 7.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 5 | Partly automatable |
| Target Scope | 8 | Every instance |
| Resource Requirements | 9 | Minimal resources |
| Detection Difficulty | 6 | Detectable with monitoring |

#### Reachability

**Score**: 3.5 | **Trust Zone**: Agent Runtime Zone (Trusted)

worker-2 sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 3.5.

---

### OI-16 — worker-2

**Threat**: Model output from worker-2 is inserted into a rendered page without encoding, so crafted output executes script in an operator's browser.

**Category**: llm | **Original Risk Level**: Medium | **Composite**: 7.1 (High)

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

**Score**: 7.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 8 | Documented and widely used |
| Attack Complexity | 7 | A single step suffices |
| Tooling Availability | 7 | Common tools apply |
| Skill Level | 8 | Little skill needed |

#### Scalability

**Score**: 7.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 8 | Fully automatable |
| Target Scope | 7 | Every instance |
| Resource Requirements | 7 | Minimal resources |
| Detection Difficulty | 8 | Blends with normal use |

#### Reachability

**Score**: 3.0 | **Trust Zone**: Agent Runtime Zone (Trusted)

worker-2 sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 3.0.

---

### OI-18 — model-gateway

**Threat**: Markdown or HTML produced by model-gateway contains remote images that leak data when a client renders it.

**Category**: llm | **Original Risk Level**: High | **Composite**: 7.1 (High)

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
| Known Techniques | 8 | Documented and widely used |
| Attack Complexity | 7 | A single step suffices |
| Tooling Availability | 7 | Common tools apply |
| Skill Level | 10 | Little skill needed |

#### Scalability

**Score**: 7.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 8 | Fully automatable |
| Target Scope | 5 | A class of targets |
| Resource Requirements | 9 | Minimal resources |
| Detection Difficulty | 8 | Blends with normal use |

#### Reachability

**Score**: 3.5 | **Trust Zone**: Agent Runtime Zone (Trusted)

model-gateway sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 3.5.

---

### OI-20 — model-gateway

**Threat**: Model output from model-gateway is inserted into a rendered page without encoding, so crafted output executes script in an operator's browser.

**Category**: llm | **Original Risk Level**: Medium | **Composite**: 7.1 (High)

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

**Score**: 7.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 7 | Documented and widely used |
| Attack Complexity | 9 | A single step suffices |
| Tooling Availability | 7 | Common tools apply |
| Skill Level | 7 | Little skill needed |

#### Scalability

**Score**: 7.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 7 | Fully automatable |
| Target Scope | 8 | Every instance |
| Resource Requirements | 7 | Minimal resources |
| Detection Difficulty | 8 | Blends with normal use |

#### Reachability

**Score**: 3.0 | **Trust Zone**: Agent Runtime Zone (Trusted)

model-gateway sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 3.0.

---

### OI-21 — summarizer-llm

**Threat**: Text generated by summarizer-llm is placed into a database query or shell argument without parameterisation, allowing the model to be steered into injection.

**Category**: llm | **Original Risk Level**: Low | **Composite**: 7.1 (High)

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
| Known Techniques | 7 | Documented and widely used |
| Attack Complexity | 8 | A single step suffices |
| Tooling Availability | 8 | Common tools apply |
| Skill Level | 7 | Little skill needed |

#### Scalability

**Score**: 7.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 6 | Partly automatable |
| Target Scope | 7 | Every instance |
| Resource Requirements | 7 | Minimal resources |
| Detection Difficulty | 8 | Blends with normal use |

#### Reachability

**Score**: 4.0 | **Trust Zone**: Agent Runtime Zone (Trusted)

summarizer-llm sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 4.0.

---

### OI-26 — planner-agent

**Threat**: Text generated by planner-agent is placed into a database query or shell argument without parameterisation, allowing the model to be steered into injection.

**Category**: llm | **Original Risk Level**: High | **Composite**: 7.1 (High)

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

**Score**: 7.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 8 | Documented and widely used |
| Attack Complexity | 6 | Needs some preparation |
| Tooling Availability | 8 | Common tools apply |
| Skill Level | 8 | Little skill needed |

#### Scalability

**Score**: 8.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 8 | Fully automatable |
| Target Scope | 7 | Every instance |
| Resource Requirements | 10 | Minimal resources |
| Detection Difficulty | 7 | Blends with normal use |

#### Reachability

**Score**: 4.0 | **Trust Zone**: Agent Runtime Zone (Trusted)

planner-agent sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 4.0.

---

### OI-28 — summarizer-llm

**Threat**: Model output from summarizer-llm is inserted into a rendered page without encoding, so crafted output executes script in an operator's browser.

**Category**: llm | **Original Risk Level**: High | **Composite**: 7.1 (High)

#### CVSS 3.1 Base

**Score**: 10.0 | **Vector**: `CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:N`

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

**Score**: 7.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 7 | Documented and widely used |
| Attack Complexity | 7 | A single step suffices |
| Tooling Availability | 8 | Common tools apply |
| Skill Level | 8 | Little skill needed |

#### Scalability

**Score**: 7.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 8 | Fully automatable |
| Target Scope | 7 | Every instance |
| Resource Requirements | 8 | Minimal resources |
| Detection Difficulty | 5 | Detectable with monitoring |

#### Reachability

**Score**: 1.5 | **Trust Zone**: Agent Runtime Zone (Trusted)

summarizer-llm sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 1.5.

---

### S-33 — trace-collector

**Threat**: A shared or long-lived collector token on trace-collector lets anyone who obtains one copy authenticate as every tenant that uses the same deployment profile.

**Category**: spoofing | **Original Risk Level**: Note | **Composite**: 6.9 (Medium)

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
| Attack Complexity | 8 | A single step suffices |
| Tooling Availability | 8 | Common tools apply |
| Skill Level | 8 | Little skill needed |

#### Scalability

**Score**: 6.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 9 | Fully automatable |
| Target Scope | 6 | A class of targets |
| Resource Requirements | 6 | Moderate resources |
| Detection Difficulty | 5 | Detectable with monitoring |

#### Reachability

**Score**: 3.5 | **Trust Zone**: Operations Zone (Trusted)

trace-collector sits in the Operations Zone. The zone baseline is 2.5 and the refinement for this finding gives 3.5.

---

### LLM-5 — intake-agent

**Threat**: intake-agent passes conversation history from earlier turns into the model unchanged, so an injection planted earlier keeps working in later turns.

**Category**: llm | **Original Risk Level**: Medium | **Composite**: 6.9 (Medium)

#### CVSS 3.1 Base

**Score**: 8.7 | **Vector**: `CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:C/C:H/I:H/A:N`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Network | Reachable over the network |
| Attack Complexity (AC) | High | Needs specific conditions |
| Privileges Required (PR) | None | No privileges needed |
| User Interaction (UI) | None | No user action needed |
| Scope (S) | Changed | Impact crosses a boundary |
| Confidentiality (C) | High | Broad disclosure |
| Integrity (I) | High | Broad modification |
| Availability (A) | None | No loss of service |

#### Exploitability

**Score**: 7.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 9 | Documented and widely used |
| Attack Complexity | 6 | Needs some preparation |
| Tooling Availability | 8 | Common tools apply |
| Skill Level | 7 | Little skill needed |

#### Scalability

**Score**: 6.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 7 | Fully automatable |
| Target Scope | 5 | A class of targets |
| Resource Requirements | 9 | Minimal resources |
| Detection Difficulty | 5 | Detectable with monitoring |

#### Reachability

**Score**: 3.0 | **Trust Zone**: Agent Runtime Zone (Trusted)

intake-agent sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 3.0.

---

### LLM-10 — router-agent

**Threat**: router-agent passes conversation history from earlier turns into the model unchanged, so an injection planted earlier keeps working in later turns.

**Category**: llm | **Original Risk Level**: Medium | **Composite**: 6.9 (Medium)

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

**Score**: 7.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 7 | Documented and widely used |
| Attack Complexity | 7 | A single step suffices |
| Tooling Availability | 7 | Common tools apply |
| Skill Level | 7 | Little skill needed |

#### Scalability

**Score**: 7.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 5 | Partly automatable |
| Target Scope | 8 | Every instance |
| Resource Requirements | 9 | Minimal resources |
| Detection Difficulty | 6 | Detectable with monitoring |

#### Reachability

**Score**: 3.0 | **Trust Zone**: Agent Runtime Zone (Trusted)

router-agent sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 3.0.

---

### LLM-57 — summarizer-llm

**Threat**: Instructions hidden in shipment records fed into summaries reach the prompt of summarizer-llm and override its system guidance, because content and instructions share one context.

**Category**: llm | **Original Risk Level**: Critical | **Composite**: 6.9 (Medium)

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

**Score**: 7.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 7 | Documented and widely used |
| Attack Complexity | 9 | A single step suffices |
| Tooling Availability | 8 | Common tools apply |
| Skill Level | 6 | Intermediate skill |

#### Scalability

**Score**: 7.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 5 | Partly automatable |
| Target Scope | 6 | A class of targets |
| Resource Requirements | 10 | Minimal resources |
| Detection Difficulty | 7 | Blends with normal use |

#### Reachability

**Score**: 2.5 | **Trust Zone**: Agent Runtime Zone (Trusted)

summarizer-llm sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 2.5.

---

### LLM-58 — summarizer-llm

**Threat**: A user message crafted to look like a system directive persuades summarizer-llm to disclose its configuration or ignore its rules.

**Category**: llm | **Original Risk Level**: High | **Composite**: 6.9 (Medium)

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

**Score**: 8.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 7 | Documented and widely used |
| Attack Complexity | 8 | A single step suffices |
| Tooling Availability | 7 | Common tools apply |
| Skill Level | 10 | Little skill needed |

#### Scalability

**Score**: 6.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 6 | Partly automatable |
| Target Scope | 5 | A class of targets |
| Resource Requirements | 8 | Minimal resources |
| Detection Difficulty | 7 | Blends with normal use |

#### Reachability

**Score**: 3.5 | **Trust Zone**: Agent Runtime Zone (Trusted)

summarizer-llm sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 3.5.

---

### OI-7 — intake-agent

**Threat**: intake-agent emits URLs that downstream services fetch, so an attacker can make internal addresses part of the output and trigger server-side requests.

**Category**: llm | **Original Risk Level**: Medium | **Composite**: 6.9 (Medium)

#### CVSS 3.1 Base

**Score**: 8.5 | **Vector**: `CVSS:3.1/AV:A/AC:L/PR:N/UI:R/S:C/C:H/I:H/A:N`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Adjacent | Needs an adjacent network |
| Attack Complexity (AC) | Low | No special conditions |
| Privileges Required (PR) | None | No privileges needed |
| User Interaction (UI) | Required | A user must act |
| Scope (S) | Changed | Impact crosses a boundary |
| Confidentiality (C) | High | Broad disclosure |
| Integrity (I) | High | Broad modification |
| Availability (A) | None | No loss of service |

#### Exploitability

**Score**: 8.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 9 | Documented and widely used |
| Attack Complexity | 7 | A single step suffices |
| Tooling Availability | 8 | Common tools apply |
| Skill Level | 10 | Little skill needed |

#### Scalability

**Score**: 7.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 5 | Partly automatable |
| Target Scope | 8 | Every instance |
| Resource Requirements | 9 | Minimal resources |
| Detection Difficulty | 6 | Detectable with monitoring |

#### Reachability

**Score**: 1.5 | **Trust Zone**: Agent Runtime Zone (Trusted)

intake-agent sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 1.5.

---

### OI-14 — worker-2

**Threat**: Markdown or HTML produced by worker-2 contains remote images that leak data when a client renders it.

**Category**: llm | **Original Risk Level**: Medium | **Composite**: 6.9 (Medium)

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

**Score**: 8.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 8 | Documented and widely used |
| Attack Complexity | 9 | A single step suffices |
| Tooling Availability | 5 | Tools need adaptation |
| Skill Level | 10 | Little skill needed |

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

worker-2 sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 3.0.

---

### MI-4 — intake-agent

**Threat**: Confident wording from intake-agent hides low retrieval quality, so operators cannot tell a grounded answer from a guess.

**Category**: llm | **Original Risk Level**: Critical | **Composite**: 6.9 (Medium)

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
| Tooling Availability | 7 | Common tools apply |
| Skill Level | 8 | Little skill needed |

#### Scalability

**Score**: 8.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 7 | Fully automatable |
| Target Scope | 8 | Every instance |
| Resource Requirements | 10 | Minimal resources |
| Detection Difficulty | 7 | Blends with normal use |

#### Reachability

**Score**: 1.5 | **Trust Zone**: Agent Runtime Zone (Trusted)

intake-agent sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 1.5.

---

### MI-9 — reviewer-agent

**Threat**: reviewer-agent fabricates reference numbers and clause citations that look real, which operators then paste into official documents.

**Category**: llm | **Original Risk Level**: High | **Composite**: 6.9 (Medium)

#### CVSS 3.1 Base

**Score**: 8.2 | **Vector**: `CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:C/C:H/I:H/A:N`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Local | Needs local access |
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
| Attack Complexity | 8 | A single step suffices |
| Tooling Availability | 6 | Tools need adaptation |
| Skill Level | 10 | Little skill needed |

#### Scalability

**Score**: 7.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 6 | Partly automatable |
| Target Scope | 7 | Every instance |
| Resource Requirements | 10 | Minimal resources |
| Detection Difficulty | 5 | Detectable with monitoring |

#### Reachability

**Score**: 3.5 | **Trust Zone**: Agent Runtime Zone (Trusted)

reviewer-agent sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 3.5.

---

### MI-10 — summarizer-llm

**Threat**: summarizer-llm fabricates reference numbers and clause citations that look real, which operators then paste into official documents.

**Category**: llm | **Original Risk Level**: High | **Composite**: 6.9 (Medium)

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

**Score**: 8.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 9 | Documented and widely used |
| Attack Complexity | 9 | A single step suffices |
| Tooling Availability | 5 | Tools need adaptation |
| Skill Level | 9 | Little skill needed |

#### Scalability

**Score**: 7.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 7 | Fully automatable |
| Target Scope | 6 | A class of targets |
| Resource Requirements | 9 | Minimal resources |
| Detection Difficulty | 6 | Detectable with monitoring |

#### Reachability

**Score**: 2.0 | **Trust Zone**: Agent Runtime Zone (Trusted)

summarizer-llm sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 2.0.

---

### LLM-6 — intake-agent

**Threat**: Prompt content logged by edge-gateway is later replayed to intake-agent for evaluation, carrying planted instructions into a trusted context.

**Category**: llm | **Original Risk Level**: Medium | **Composite**: 6.8 (Medium)

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

**Score**: 7.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 7 | Documented and widely used |
| Attack Complexity | 7 | A single step suffices |
| Tooling Availability | 7 | Common tools apply |
| Skill Level | 7 | Little skill needed |

#### Scalability

**Score**: 7.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 8 | Fully automatable |
| Target Scope | 5 | A class of targets |
| Resource Requirements | 8 | Minimal resources |
| Detection Difficulty | 7 | Blends with normal use |

#### Reachability

**Score**: 1.5 | **Trust Zone**: Agent Runtime Zone (Trusted)

intake-agent sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 1.5.

---

### LLM-27 — summarizer-llm

**Threat**: Evaluation labels consumed from summarizer-llm are produced by a judge model that can itself be influenced by planted traces.

**Category**: llm | **Original Risk Level**: Critical | **Composite**: 6.8 (Medium)

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
| Known Techniques | 7 | Documented and widely used |
| Attack Complexity | 6 | Needs some preparation |
| Tooling Availability | 6 | Tools need adaptation |
| Skill Level | 9 | Little skill needed |

#### Scalability

**Score**: 7.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 5 | Partly automatable |
| Target Scope | 7 | Every instance |
| Resource Requirements | 10 | Minimal resources |
| Detection Difficulty | 6 | Detectable with monitoring |

#### Reachability

**Score**: 2.0 | **Trust Zone**: Agent Runtime Zone (Trusted)

summarizer-llm sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 2.0.

---

### OI-9 — planner-agent

**Threat**: planner-agent emits URLs that downstream services fetch, so an attacker can make internal addresses part of the output and trigger server-side requests.

**Category**: llm | **Original Risk Level**: Critical | **Composite**: 6.8 (Medium)

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
| Attack Complexity | 6 | Needs some preparation |
| Tooling Availability | 8 | Common tools apply |
| Skill Level | 8 | Little skill needed |

#### Scalability

**Score**: 7.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 8 | Fully automatable |
| Target Scope | 5 | A class of targets |
| Resource Requirements | 7 | Minimal resources |
| Detection Difficulty | 8 | Blends with normal use |

#### Reachability

**Score**: 2.0 | **Trust Zone**: Agent Runtime Zone (Trusted)

planner-agent sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 2.0.

---

### OI-22 — summarizer-llm

**Threat**: summarizer-llm emits URLs that downstream services fetch, so an attacker can make internal addresses part of the output and trigger server-side requests.

**Category**: llm | **Original Risk Level**: High | **Composite**: 6.8 (Medium)

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
| Known Techniques | 7 | Documented and widely used |
| Attack Complexity | 9 | A single step suffices |
| Tooling Availability | 8 | Common tools apply |
| Skill Level | 8 | Little skill needed |

#### Scalability

**Score**: 6.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 5 | Partly automatable |
| Target Scope | 8 | Every instance |
| Resource Requirements | 7 | Minimal resources |
| Detection Difficulty | 6 | Detectable with monitoring |

#### Reachability

**Score**: 3.0 | **Trust Zone**: Agent Runtime Zone (Trusted)

summarizer-llm sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 3.0.

---

### MI-2 — intake-agent

**Threat**: Stale data in the knowledge base lets intake-agent present superseded tariffs as current, causing wrong quotes.

**Category**: llm | **Original Risk Level**: Medium | **Composite**: 6.8 (Medium)

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
| Known Techniques | 7 | Documented and widely used |
| Attack Complexity | 9 | A single step suffices |
| Tooling Availability | 5 | Tools need adaptation |
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

### MI-8 — reviewer-agent

**Threat**: Outputs from reviewer-agent flow into decisions without a review step, so one wrong answer is repeated across many shipments.

**Category**: llm | **Original Risk Level**: Note | **Composite**: 6.8 (Medium)

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
| Known Techniques | 9 | Documented and widely used |
| Attack Complexity | 9 | A single step suffices |
| Tooling Availability | 7 | Common tools apply |
| Skill Level | 7 | Little skill needed |

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

reviewer-agent sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 3.0.

---

### D-36 — auth-broker

**Threat**: A slow-read attack holds connections to auth-broker open and ties up the workers handling credential assertions and session grants until none remain for real requests.

**Category**: denial-of-service | **Original Risk Level**: High | **Composite**: 6.7 (Medium)

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

**Score**: 8.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 8 | Documented and widely used |
| Attack Complexity | 8 | A single step suffices |
| Tooling Availability | 7 | Common tools apply |
| Skill Level | 9 | Little skill needed |

#### Scalability

**Score**: 7.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 10 | Fully automatable |
| Target Scope | 8 | Every instance |
| Resource Requirements | 8 | Minimal resources |
| Detection Difficulty | 4 | Detectable with monitoring |

#### Reachability

**Score**: 6.5 | **Trust Zone**: Edge DMZ (Semi-trusted)

auth-broker sits in the Edge DMZ. The zone baseline is 6.5 and the refinement for this finding gives 6.5.

---

### LLM-43 — trace-collector

**Threat**: A delayed trigger planted in prompts, completions and tool traces on trace-collector changes behaviour only after a date or phrase, so pre-release testing never sees it.

**Category**: llm | **Original Risk Level**: Medium | **Composite**: 6.7 (Medium)

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
| Attack Complexity | 6 | Needs some preparation |
| Tooling Availability | 7 | Common tools apply |
| Skill Level | 9 | Little skill needed |

#### Scalability

**Score**: 7.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 7 | Fully automatable |
| Target Scope | 7 | Every instance |
| Resource Requirements | 9 | Minimal resources |
| Detection Difficulty | 5 | Detectable with monitoring |

#### Reachability

**Score**: 1.5 | **Trust Zone**: Operations Zone (Trusted)

trace-collector sits in the Operations Zone. The zone baseline is 2.5 and the refinement for this finding gives 1.5.

---

### OI-4 — intake-agent

**Threat**: File paths or names produced by intake-agent are used to write files, letting crafted output reach locations outside the intended directory.

**Category**: llm | **Original Risk Level**: Note | **Composite**: 6.7 (Medium)

#### CVSS 3.1 Base

**Score**: 8.1 | **Vector**: `CVSS:3.1/AV:A/AC:L/PR:L/UI:R/S:C/C:H/I:H/A:N`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Adjacent | Needs an adjacent network |
| Attack Complexity (AC) | Low | No special conditions |
| Privileges Required (PR) | Low | A basic account is needed |
| User Interaction (UI) | Required | A user must act |
| Scope (S) | Changed | Impact crosses a boundary |
| Confidentiality (C) | High | Broad disclosure |
| Integrity (I) | High | Broad modification |
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
| Scriptability | 6 | Partly automatable |
| Target Scope | 7 | Every instance |
| Resource Requirements | 9 | Minimal resources |
| Detection Difficulty | 6 | Detectable with monitoring |

#### Reachability

**Score**: 2.0 | **Trust Zone**: Agent Runtime Zone (Trusted)

intake-agent sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 2.0.

---

### MI-11 — summarizer-llm

**Threat**: Stale data in the knowledge base lets summarizer-llm present superseded tariffs as current, causing wrong quotes.

**Category**: llm | **Original Risk Level**: Critical | **Composite**: 6.7 (Medium)

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

**Score**: 6.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 6 | Described in research |
| Attack Complexity | 6 | Needs some preparation |
| Tooling Availability | 5 | Tools need adaptation |
| Skill Level | 7 | Little skill needed |

#### Scalability

**Score**: 7.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 7 | Fully automatable |
| Target Scope | 6 | A class of targets |
| Resource Requirements | 10 | Minimal resources |
| Detection Difficulty | 5 | Detectable with monitoring |

#### Reachability

**Score**: 3.0 | **Trust Zone**: Agent Runtime Zone (Trusted)

summarizer-llm sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 3.0.

---

### S-9 — planner-agent

**Threat**: Session fixation against planner-agent lets an attacker pre-seed an identifier and reuse the session after the victim authenticates.

**Category**: spoofing | **Original Risk Level**: High | **Composite**: 6.6 (Medium)

#### CVSS 3.1 Base

**Score**: 9.3 | **Vector**: `CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:L/A:N`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Network | Reachable over the network |
| Attack Complexity (AC) | Low | No special conditions |
| Privileges Required (PR) | None | No privileges needed |
| User Interaction (UI) | None | No user action needed |
| Scope (S) | Changed | Impact crosses a boundary |
| Confidentiality (C) | High | Broad disclosure |
| Integrity (I) | Low | Limited modification |
| Availability (A) | None | No loss of service |

#### Exploitability

**Score**: 7.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 8 | Documented and widely used |
| Attack Complexity | 7 | A single step suffices |
| Tooling Availability | 7 | Common tools apply |
| Skill Level | 6 | Intermediate skill |

#### Scalability

**Score**: 6.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 9 | Fully automatable |
| Target Scope | 5 | A class of targets |
| Resource Requirements | 6 | Moderate resources |
| Detection Difficulty | 6 | Detectable with monitoring |

#### Reachability

**Score**: 1.5 | **Trust Zone**: Agent Runtime Zone (Trusted)

planner-agent sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 1.5.

---

### I-3 — edge-gateway

**Threat**: inbound API requests held by edge-gateway are readable by any service in the Edge DMZ that shares the same network role, because access is granted by network position.

**Category**: info-disclosure | **Original Risk Level**: Medium | **Composite**: 6.6 (Medium)

#### CVSS 3.1 Base

**Score**: 5.5 | **Vector**: `CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Local | Needs local access |
| Attack Complexity (AC) | Low | No special conditions |
| Privileges Required (PR) | Low | A basic account is needed |
| User Interaction (UI) | None | No user action needed |
| Scope (S) | Unchanged | Impact stays in the component |
| Confidentiality (C) | High | Broad disclosure |
| Integrity (I) | None | No modification |
| Availability (A) | None | No loss of service |

#### Exploitability

**Score**: 7.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 7 | Documented and widely used |
| Attack Complexity | 7 | A single step suffices |
| Tooling Availability | 9 | Common tools apply |
| Skill Level | 7 | Little skill needed |

#### Scalability

**Score**: 7.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 7 | Fully automatable |
| Target Scope | 8 | Every instance |
| Resource Requirements | 9 | Minimal resources |
| Detection Difficulty | 4 | Detectable with monitoring |

#### Reachability

**Score**: 7.0 | **Trust Zone**: Edge DMZ (Semi-trusted)

edge-gateway sits in the Edge DMZ. The zone baseline is 6.5 and the refinement for this finding gives 7.0.

---

### I-5 — auth-broker

**Threat**: Logs and traces emitted by auth-broker include raw credential assertions and session grants, so anyone with access to the logging pipeline can read content meant for one tenant.

**Category**: info-disclosure | **Original Risk Level**: High | **Composite**: 6.6 (Medium)

#### CVSS 3.1 Base

**Score**: 5.5 | **Vector**: `CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Local | Needs local access |
| Attack Complexity (AC) | Low | No special conditions |
| Privileges Required (PR) | Low | A basic account is needed |
| User Interaction (UI) | None | No user action needed |
| Scope (S) | Unchanged | Impact stays in the component |
| Confidentiality (C) | High | Broad disclosure |
| Integrity (I) | None | No modification |
| Availability (A) | None | No loss of service |

#### Exploitability

**Score**: 7.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 7 | Documented and widely used |
| Attack Complexity | 8 | A single step suffices |
| Tooling Availability | 7 | Common tools apply |
| Skill Level | 8 | Little skill needed |

#### Scalability

**Score**: 7.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 7 | Fully automatable |
| Target Scope | 6 | A class of targets |
| Resource Requirements | 10 | Minimal resources |
| Detection Difficulty | 7 | Blends with normal use |

#### Reachability

**Score**: 6.5 | **Trust Zone**: Edge DMZ (Semi-trusted)

auth-broker sits in the Edge DMZ. The zone baseline is 6.5 and the refinement for this finding gives 6.5.

---

### D-7 — planner-agent

**Threat**: A dependency of planner-agent becomes unavailable and the failure cascades because planner-agent waits on it synchronously for every request.

**Category**: denial-of-service | **Original Risk Level**: Medium | **Composite**: 6.6 (Medium)

#### CVSS 3.1 Base

**Score**: 8.2 | **Vector**: `CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:H`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Network | Reachable over the network |
| Attack Complexity (AC) | Low | No special conditions |
| Privileges Required (PR) | None | No privileges needed |
| User Interaction (UI) | None | No user action needed |
| Scope (S) | Unchanged | Impact stays in the component |
| Confidentiality (C) | None | No disclosure |
| Integrity (I) | Low | Limited modification |
| Availability (A) | High | Loss of service |

#### Exploitability

**Score**: 7.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 7 | Documented and widely used |
| Attack Complexity | 8 | A single step suffices |
| Tooling Availability | 5 | Tools need adaptation |
| Skill Level | 8 | Little skill needed |

#### Scalability

**Score**: 6.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 8 | Fully automatable |
| Target Scope | 9 | Every instance |
| Resource Requirements | 4 | Moderate resources |
| Detection Difficulty | 3 | Readily detected |

#### Reachability

**Score**: 3.5 | **Trust Zone**: Agent Runtime Zone (Trusted)

planner-agent sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 3.5.

---

### D-8 — planner-agent

**Threat**: Expensive queries over task plans and tool selections can be triggered by any authorised caller of planner-agent, so one user can degrade the service for all.

**Category**: denial-of-service | **Original Risk Level**: Critical | **Composite**: 6.6 (Medium)

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

**Score**: 7.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 8 | Documented and widely used |
| Attack Complexity | 7 | A single step suffices |
| Tooling Availability | 8 | Common tools apply |
| Skill Level | 7 | Little skill needed |

#### Scalability

**Score**: 7.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 10 | Fully automatable |
| Target Scope | 7 | Every instance |
| Resource Requirements | 6 | Moderate resources |
| Detection Difficulty | 5 | Detectable with monitoring |

#### Reachability

**Score**: 3.5 | **Trust Zone**: Agent Runtime Zone (Trusted)

planner-agent sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 3.5.

---

### D-27 — feature-store-2

**Threat**: A single oversized or deeply nested payload makes feature-store-2 spend disproportionate memory and CPU parsing ranking and fine-tuning features.

**Category**: denial-of-service | **Original Risk Level**: High | **Composite**: 6.6 (Medium)

#### CVSS 3.1 Base

**Score**: 8.5 | **Vector**: `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:N/I:L/A:H`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Network | Reachable over the network |
| Attack Complexity (AC) | Low | No special conditions |
| Privileges Required (PR) | Low | A basic account is needed |
| User Interaction (UI) | None | No user action needed |
| Scope (S) | Changed | Impact crosses a boundary |
| Confidentiality (C) | None | No disclosure |
| Integrity (I) | Low | Limited modification |
| Availability (A) | High | Loss of service |

#### Exploitability

**Score**: 8.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 9 | Documented and widely used |
| Attack Complexity | 9 | A single step suffices |
| Tooling Availability | 5 | Tools need adaptation |
| Skill Level | 9 | Little skill needed |

#### Scalability

**Score**: 5.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 7 | Fully automatable |
| Target Scope | 9 | Every instance |
| Resource Requirements | 4 | Moderate resources |
| Detection Difficulty | 2 | Readily detected |

#### Reachability

**Score**: 2.0 | **Trust Zone**: Data Zone (Trusted)

feature-store-2 sits in the Data Zone. The zone baseline is 2.5 and the refinement for this finding gives 2.0.

---

### LLM-53 — policy-engine

**Threat**: Instructions hidden in guardrail rules and approval decisions reach the prompt of policy-engine and override its system guidance, because content and instructions share one context.

**Category**: llm | **Original Risk Level**: High | **Composite**: 6.6 (Medium)

#### CVSS 3.1 Base

**Score**: 8.0 | **Vector**: `CVSS:3.1/AV:A/AC:L/PR:N/UI:R/S:C/C:L/I:H/A:L`

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

**Score**: 8.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 6 | Described in research |
| Attack Complexity | 9 | A single step suffices |
| Tooling Availability | 7 | Common tools apply |
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

**Score**: 1.5 | **Trust Zone**: Operations Zone (Trusted)

policy-engine sits in the Operations Zone. The zone baseline is 2.5 and the refinement for this finding gives 1.5.

---

### OI-10 — planner-agent

**Threat**: Structured output from planner-agent is trusted by router-agent as already validated, so a malformed field flows straight into business logic.

**Category**: llm | **Original Risk Level**: Critical | **Composite**: 6.6 (Medium)

#### CVSS 3.1 Base

**Score**: 8.1 | **Vector**: `CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:N`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Network | Reachable over the network |
| Attack Complexity (AC) | Low | No special conditions |
| Privileges Required (PR) | None | No privileges needed |
| User Interaction (UI) | Required | A user must act |
| Scope (S) | Unchanged | Impact stays in the component |
| Confidentiality (C) | High | Broad disclosure |
| Integrity (I) | High | Broad modification |
| Availability (A) | None | No loss of service |

#### Exploitability

**Score**: 7.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 8 | Documented and widely used |
| Attack Complexity | 8 | A single step suffices |
| Tooling Availability | 6 | Tools need adaptation |
| Skill Level | 6 | Intermediate skill |

#### Scalability

**Score**: 6.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 6 | Partly automatable |
| Target Scope | 5 | A class of targets |
| Resource Requirements | 9 | Minimal resources |
| Detection Difficulty | 6 | Detectable with monitoring |

#### Reachability

**Score**: 3.5 | **Trust Zone**: Agent Runtime Zone (Trusted)

planner-agent sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 3.5.

---

### OI-25 — summarizer-llm

**Threat**: File paths or names produced by summarizer-llm are used to write files, letting crafted output reach locations outside the intended directory.

**Category**: llm | **Original Risk Level**: High | **Composite**: 6.6 (Medium)

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

**Score**: 6.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 7 | Documented and widely used |
| Attack Complexity | 6 | Needs some preparation |
| Tooling Availability | 7 | Common tools apply |
| Skill Level | 6 | Intermediate skill |

#### Scalability

**Score**: 6.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 6 | Partly automatable |
| Target Scope | 6 | A class of targets |
| Resource Requirements | 9 | Minimal resources |
| Detection Difficulty | 5 | Detectable with monitoring |

#### Reachability

**Score**: 1.5 | **Trust Zone**: Agent Runtime Zone (Trusted)

summarizer-llm sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 1.5.

---

### MI-1 — intake-agent

**Threat**: intake-agent fabricates reference numbers and clause citations that look real, which operators then paste into official documents.

**Category**: llm | **Original Risk Level**: Medium | **Composite**: 6.6 (Medium)

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
| Known Techniques | 8 | Documented and widely used |
| Attack Complexity | 6 | Needs some preparation |
| Tooling Availability | 7 | Common tools apply |
| Skill Level | 7 | Little skill needed |

#### Scalability

**Score**: 6.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 5 | Partly automatable |
| Target Scope | 5 | A class of targets |
| Resource Requirements | 10 | Minimal resources |
| Detection Difficulty | 6 | Detectable with monitoring |

#### Reachability

**Score**: 1.5 | **Trust Zone**: Agent Runtime Zone (Trusted)

intake-agent sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 1.5.

---

### MI-18 — eval-runner

**Threat**: eval-runner fabricates reference numbers and clause citations that look real, which operators then paste into official documents.

**Category**: llm | **Original Risk Level**: High | **Composite**: 6.6 (Medium)

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

**Score**: 6.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 6 | Described in research |
| Attack Complexity | 8 | A single step suffices |
| Tooling Availability | 5 | Tools need adaptation |
| Skill Level | 7 | Little skill needed |

#### Scalability

**Score**: 7.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 6 | Partly automatable |
| Target Scope | 8 | Every instance |
| Resource Requirements | 7 | Minimal resources |
| Detection Difficulty | 7 | Blends with normal use |

#### Reachability

**Score**: 3.0 | **Trust Zone**: Operations Zone (Trusted)

eval-runner sits in the Operations Zone. The zone baseline is 2.5 and the refinement for this finding gives 3.0.

---

### TE-4 — intake-agent

**Threat**: intake-agent claims certainty it does not have when summarising shipment risk, and customers rely on the stated confidence.

**Category**: agentic | **Original Risk Level**: Medium | **Composite**: 6.6 (Medium)

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

**Score**: 5.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 7 | Documented and widely used |
| Attack Complexity | 6 | Needs some preparation |
| Tooling Availability | 3 | Needs custom tooling |
| Skill Level | 4 | Intermediate skill |

#### Scalability

**Score**: 6.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 5 | Partly automatable |
| Target Scope | 5 | A class of targets |
| Resource Requirements | 6 | Moderate resources |
| Detection Difficulty | 8 | Blends with normal use |

#### Reachability

**Score**: 3.5 | **Trust Zone**: Agent Runtime Zone (Trusted)

intake-agent sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 3.5.

---

### S-41 — reviewer-agent

**Threat**: An attacker replays a captured reviewer session against reviewer-agent, which does not bind the credential to the session or channel it was issued for, so the replay is accepted as the original caller.

**Category**: spoofing | **Original Risk Level**: High | **Composite**: 6.5 (Medium)

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
| Known Techniques | 7 | Documented and widely used |
| Attack Complexity | 6 | Needs some preparation |
| Tooling Availability | 8 | Common tools apply |
| Skill Level | 7 | Little skill needed |

#### Scalability

**Score**: 7.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 9 | Fully automatable |
| Target Scope | 7 | Every instance |
| Resource Requirements | 7 | Minimal resources |
| Detection Difficulty | 5 | Detectable with monitoring |

#### Reachability

**Score**: 2.5 | **Trust Zone**: Agent Runtime Zone (Trusted)

reviewer-agent sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 2.5.

---

### D-20 — model-gateway

**Threat**: Expensive queries over prompts and completions can be triggered by any authorised caller of model-gateway, so one user can degrade the service for all.

**Category**: denial-of-service | **Original Risk Level**: Low | **Composite**: 6.5 (Medium)

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

**Score**: 7.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 8 | Documented and widely used |
| Attack Complexity | 7 | A single step suffices |
| Tooling Availability | 6 | Tools need adaptation |
| Skill Level | 9 | Little skill needed |

#### Scalability

**Score**: 6.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 8 | Fully automatable |
| Target Scope | 9 | Every instance |
| Resource Requirements | 3 | Needs heavy infrastructure |
| Detection Difficulty | 4 | Detectable with monitoring |

#### Reachability

**Score**: 3.5 | **Trust Zone**: Agent Runtime Zone (Trusted)

model-gateway sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 3.5.

---

### D-31 — scheduler-1

**Threat**: Unbounded growth of stored recurring planning triggers on scheduler-1 fills its volume, after which writes fail for every other consumer.

**Category**: denial-of-service | **Original Risk Level**: Medium | **Composite**: 6.5 (Medium)

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

**Score**: 8.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 9 | Documented and widely used |
| Attack Complexity | 9 | A single step suffices |
| Tooling Availability | 6 | Tools need adaptation |
| Skill Level | 8 | Little skill needed |

#### Scalability

**Score**: 5.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 9 | Fully automatable |
| Target Scope | 6 | A class of targets |
| Resource Requirements | 4 | Moderate resources |
| Detection Difficulty | 1 | Readily detected |

#### Reachability

**Score**: 3.5 | **Trust Zone**: Agent Runtime Zone (Trusted)

scheduler-1 sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 3.5.

---

### E-22 — embed-service-2

**Threat**: embed-service-2 runs with broader permissions than its function needs, so a flaw in handling document chunks and query embeddings yields access to unrelated resources.

**Category**: privilege-escalation | **Original Risk Level**: High | **Composite**: 6.5 (Medium)

#### CVSS 3.1 Base

**Score**: 9.9 | **Vector**: `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:L/I:H/A:H`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Network | Reachable over the network |
| Attack Complexity (AC) | Low | No special conditions |
| Privileges Required (PR) | Low | A basic account is needed |
| User Interaction (UI) | None | No user action needed |
| Scope (S) | Changed | Impact crosses a boundary |
| Confidentiality (C) | Low | Limited disclosure |
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

**Score**: 6.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 6 | Partly automatable |
| Target Scope | 5 | A class of targets |
| Resource Requirements | 9 | Minimal resources |
| Detection Difficulty | 4 | Detectable with monitoring |

#### Reachability

**Score**: 3.0 | **Trust Zone**: Agent Runtime Zone (Trusted)

embed-service-2 sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 3.0.

---

### E-34 — eval-runner

**Threat**: A confused-deputy path lets a low-privilege caller ask eval-runner to act on replayed traces and judge verdicts using the privileges of trace-collector.

**Category**: privilege-escalation | **Original Risk Level**: Medium | **Composite**: 6.5 (Medium)

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
| Known Techniques | 4 | Described in research |
| Attack Complexity | 6 | Needs some preparation |
| Tooling Availability | 3 | Needs custom tooling |
| Skill Level | 5 | Intermediate skill |

#### Scalability

**Score**: 6.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 7 | Fully automatable |
| Target Scope | 6 | A class of targets |
| Resource Requirements | 8 | Minimal resources |
| Detection Difficulty | 5 | Detectable with monitoring |

#### Reachability

**Score**: 3.5 | **Trust Zone**: Operations Zone (Trusted)

eval-runner sits in the Operations Zone. The zone baseline is 2.5 and the refinement for this finding gives 3.5.

---

### AGP-02 — worker-2

**Threat**: Worker agents coordinate through the shared message bus and memory so that each stays under its individual limits while together they exceed the authority intended for any one of them, and no single-agent control observes the combined behaviour.

**Category**: agentic | **Original Risk Level**: Medium | **Composite**: 6.5 (Medium)

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
| Known Techniques | 4 | Described in research |
| Attack Complexity | 3 | Needs chained steps |
| Tooling Availability | 4 | Tools need adaptation |
| Skill Level | 7 | Little skill needed |

#### Scalability

**Score**: 6.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 5 | Partly automatable |
| Target Scope | 5 | A class of targets |
| Resource Requirements | 9 | Minimal resources |
| Detection Difficulty | 7 | Blends with normal use |

#### Reachability

**Score**: 3.5 | **Trust Zone**: Agent Runtime Zone (Trusted)

worker-2 sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 3.5.

---

### AGP-03 — scheduler-1

**Threat**: State persisted across runs lets a sleeper instruction written today change the behaviour of a scheduled run weeks later, after the original entry has left review and the context that explained it is gone.

**Category**: agentic | **Original Risk Level**: Medium | **Composite**: 6.5 (Medium)

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

**Score**: 5.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 7 | Documented and widely used |
| Attack Complexity | 5 | Needs some preparation |
| Tooling Availability | 4 | Tools need adaptation |
| Skill Level | 6 | Intermediate skill |

#### Scalability

**Score**: 6.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 2 | Manual for each target |
| Target Scope | 5 | A class of targets |
| Resource Requirements | 9 | Minimal resources |
| Detection Difficulty | 8 | Blends with normal use |

#### Reachability

**Score**: 2.5 | **Trust Zone**: Agent Runtime Zone (Trusted)

scheduler-1 sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 2.5.

---

### LLM-35 — memory-store

**Threat**: Records written into memory-store by low-trust sources are later used as ground truth, so an attacker who plants entries shifts model answers.

**Category**: llm | **Original Risk Level**: Medium | **Composite**: 6.5 (Medium)

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
| Attack Complexity | 7 | A single step suffices |
| Tooling Availability | 6 | Tools need adaptation |
| Skill Level | 9 | Little skill needed |

#### Scalability

**Score**: 7.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 8 | Fully automatable |
| Target Scope | 5 | A class of targets |
| Resource Requirements | 10 | Minimal resources |
| Detection Difficulty | 5 | Detectable with monitoring |

#### Reachability

**Score**: 2.0 | **Trust Zone**: Data Zone (Trusted)

memory-store sits in the Data Zone. The zone baseline is 2.5 and the refinement for this finding gives 2.0.

---

### OI-11 — planner-agent

**Threat**: Markdown or HTML produced by planner-agent contains remote images that leak data when a client renders it.

**Category**: llm | **Original Risk Level**: High | **Composite**: 6.5 (Medium)

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
| Known Techniques | 7 | Documented and widely used |
| Attack Complexity | 6 | Needs some preparation |
| Tooling Availability | 6 | Tools need adaptation |
| Skill Level | 9 | Little skill needed |

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

planner-agent sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 2.0.

---

### OI-23 — summarizer-llm

**Threat**: Structured output from summarizer-llm is trusted by feature-store-2 as already validated, so a malformed field flows straight into business logic.

**Category**: llm | **Original Risk Level**: High | **Composite**: 6.5 (Medium)

#### CVSS 3.1 Base

**Score**: 8.7 | **Vector**: `CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:C/C:H/I:H/A:N`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Network | Reachable over the network |
| Attack Complexity (AC) | High | Needs specific conditions |
| Privileges Required (PR) | None | No privileges needed |
| User Interaction (UI) | None | No user action needed |
| Scope (S) | Changed | Impact crosses a boundary |
| Confidentiality (C) | High | Broad disclosure |
| Integrity (I) | High | Broad modification |
| Availability (A) | None | No loss of service |

#### Exploitability

**Score**: 6.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 7 | Documented and widely used |
| Attack Complexity | 6 | Needs some preparation |
| Tooling Availability | 5 | Tools need adaptation |
| Skill Level | 8 | Little skill needed |

#### Scalability

**Score**: 7.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 7 | Fully automatable |
| Target Scope | 6 | A class of targets |
| Resource Requirements | 9 | Minimal resources |
| Detection Difficulty | 6 | Detectable with monitoring |

#### Reachability

**Score**: 2.5 | **Trust Zone**: Agent Runtime Zone (Trusted)

summarizer-llm sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 2.5.

---

### MI-13 — summarizer-llm

**Threat**: Confident wording from summarizer-llm hides low retrieval quality, so operators cannot tell a grounded answer from a guess.

**Category**: llm | **Original Risk Level**: Critical | **Composite**: 6.5 (Medium)

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

**Score**: 8.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 9 | Documented and widely used |
| Attack Complexity | 8 | A single step suffices |
| Tooling Availability | 5 | Tools need adaptation |
| Skill Level | 10 | Little skill needed |

#### Scalability

**Score**: 7.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 5 | Partly automatable |
| Target Scope | 7 | Every instance |
| Resource Requirements | 10 | Minimal resources |
| Detection Difficulty | 6 | Detectable with monitoring |

#### Reachability

**Score**: 2.0 | **Trust Zone**: Agent Runtime Zone (Trusted)

summarizer-llm sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 2.0.

---

### S-32 — trace-collector

**Threat**: A compromised peer presents a forged service identity to trace-collector, and trace-collector accepts the claim without verifying the signature chain back to the issuing authority.

**Category**: spoofing | **Original Risk Level**: High | **Composite**: 6.4 (Medium)

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

**Score**: 6.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 8 | Documented and widely used |
| Attack Complexity | 7 | A single step suffices |
| Tooling Availability | 5 | Tools need adaptation |
| Skill Level | 4 | Intermediate skill |

#### Scalability

**Score**: 7.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 9 | Fully automatable |
| Target Scope | 6 | A class of targets |
| Resource Requirements | 8 | Minimal resources |
| Detection Difficulty | 7 | Blends with normal use |

#### Reachability

**Score**: 3.0 | **Trust Zone**: Operations Zone (Trusted)

trace-collector sits in the Operations Zone. The zone baseline is 2.5 and the refinement for this finding gives 3.0.

---

### E-15 — worker-3

**Threat**: Object identifiers in requests to worker-3 are trusted without an ownership check, so a caller can read or change work orders and draft documents that belong to others.

**Category**: privilege-escalation | **Original Risk Level**: High | **Composite**: 6.4 (Medium)

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

**Score**: 5.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 7 | Documented and widely used |
| Attack Complexity | 6 | Needs some preparation |
| Tooling Availability | 3 | Needs custom tooling |
| Skill Level | 4 | Intermediate skill |

#### Scalability

**Score**: 6.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 7 | Fully automatable |
| Target Scope | 4 | A class of targets |
| Resource Requirements | 9 | Minimal resources |
| Detection Difficulty | 4 | Detectable with monitoring |

#### Reachability

**Score**: 2.5 | **Trust Zone**: Agent Runtime Zone (Trusted)

worker-3 sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 2.5.

---

### E-29 — trace-collector

**Threat**: A privileged maintenance task of trace-collector can be triggered through a queue message that any producer on the bus may publish.

**Category**: privilege-escalation | **Original Risk Level**: High | **Composite**: 6.4 (Medium)

#### CVSS 3.1 Base

**Score**: 9.9 | **Vector**: `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:L/I:H/A:H`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Network | Reachable over the network |
| Attack Complexity (AC) | Low | No special conditions |
| Privileges Required (PR) | Low | A basic account is needed |
| User Interaction (UI) | None | No user action needed |
| Scope (S) | Changed | Impact crosses a boundary |
| Confidentiality (C) | Low | Limited disclosure |
| Integrity (I) | High | Broad modification |
| Availability (A) | High | Loss of service |

#### Exploitability

**Score**: 5.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 5 | Described in research |
| Attack Complexity | 4 | Needs some preparation |
| Tooling Availability | 5 | Tools need adaptation |
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

**Score**: 3.0 | **Trust Zone**: Operations Zone (Trusted)

trace-collector sits in the Operations Zone. The zone baseline is 2.5 and the refinement for this finding gives 3.0.

---

### AG-18 — worker-2

**Threat**: The goal or instruction set of worker-2 can be changed through content it reads, steering it toward actions its operators never intended.

**Category**: agentic | **Original Risk Level**: High | **Composite**: 6.4 (Medium)

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
| Scriptability | 5 | Partly automatable |
| Target Scope | 6 | A class of targets |
| Resource Requirements | 6 | Moderate resources |
| Detection Difficulty | 5 | Detectable with monitoring |

#### Reachability

**Score**: 2.5 | **Trust Zone**: Agent Runtime Zone (Trusted)

worker-2 sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 2.5.

---

### AG-26 — reviewer-agent

**Threat**: reviewer-agent retries failed actions on its own, repeating side effects such as bookings or messages when the first attempt partly succeeded.

**Category**: agentic | **Original Risk Level**: High | **Composite**: 6.4 (Medium)

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

**Score**: 5.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 7 | Documented and widely used |
| Attack Complexity | 6 | Needs some preparation |
| Tooling Availability | 3 | Needs custom tooling |
| Skill Level | 4 | Intermediate skill |

#### Scalability

**Score**: 5.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 4 | Partly automatable |
| Target Scope | 5 | A class of targets |
| Resource Requirements | 8 | Minimal resources |
| Detection Difficulty | 5 | Detectable with monitoring |

#### Reachability

**Score**: 3.0 | **Trust Zone**: Agent Runtime Zone (Trusted)

reviewer-agent sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 3.0.

---

### LLM-8 — router-agent

**Threat**: Indirect injection through documents retrieved for router-agent lets the author of a retrieved page steer the answer without ever talking to the system.

**Category**: llm | **Original Risk Level**: Low | **Composite**: 6.4 (Medium)

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

**Score**: 7.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 8 | Documented and widely used |
| Attack Complexity | 9 | A single step suffices |
| Tooling Availability | 5 | Tools need adaptation |
| Skill Level | 6 | Intermediate skill |

#### Scalability

**Score**: 6.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 7 | Fully automatable |
| Target Scope | 6 | A class of targets |
| Resource Requirements | 7 | Minimal resources |
| Detection Difficulty | 4 | Detectable with monitoring |

#### Reachability

**Score**: 2.5 | **Trust Zone**: Agent Runtime Zone (Trusted)

router-agent sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 2.5.

---

### LLM-15 — worker-3

**Threat**: worker-3 follows links and files named in work orders and draft documents, which turns a harmless-looking request into a fetch of attacker-controlled content.

**Category**: llm | **Original Risk Level**: Medium | **Composite**: 6.4 (Medium)

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

**Score**: 7.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 6 | Described in research |
| Attack Complexity | 8 | A single step suffices |
| Tooling Availability | 7 | Common tools apply |
| Skill Level | 9 | Little skill needed |

#### Scalability

**Score**: 6.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 7 | Fully automatable |
| Target Scope | 6 | A class of targets |
| Resource Requirements | 7 | Minimal resources |
| Detection Difficulty | 4 | Detectable with monitoring |

#### Reachability

**Score**: 1.5 | **Trust Zone**: Agent Runtime Zone (Trusted)

worker-3 sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 1.5.

---

### LLM-28 — summarizer-llm

**Threat**: Model weights or adapters served by summarizer-llm are readable by operators and by any process sharing the host.

**Category**: llm | **Original Risk Level**: Critical | **Composite**: 6.4 (Medium)

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

**Score**: 8.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 9 | Documented and widely used |
| Attack Complexity | 9 | A single step suffices |
| Tooling Availability | 6 | Tools need adaptation |
| Skill Level | 8 | Little skill needed |

#### Scalability

**Score**: 6.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 5 | Partly automatable |
| Target Scope | 8 | Every instance |
| Resource Requirements | 7 | Minimal resources |
| Detection Difficulty | 4 | Detectable with monitoring |

#### Reachability

**Score**: 2.0 | **Trust Zone**: Agent Runtime Zone (Trusted)

summarizer-llm sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 2.0.

---

### MI-7 — reviewer-agent

**Threat**: Confident wording from reviewer-agent hides low retrieval quality, so operators cannot tell a grounded answer from a guess.

**Category**: llm | **Original Risk Level**: High | **Composite**: 6.4 (Medium)

#### CVSS 3.1 Base

**Score**: 6.5 | **Vector**: `CVSS:3.1/AV:N/AC:H/PR:L/UI:R/S:C/C:L/I:H/A:N`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Network | Reachable over the network |
| Attack Complexity (AC) | High | Needs specific conditions |
| Privileges Required (PR) | Low | A basic account is needed |
| User Interaction (UI) | Required | A user must act |
| Scope (S) | Changed | Impact crosses a boundary |
| Confidentiality (C) | Low | Limited disclosure |
| Integrity (I) | High | Broad modification |
| Availability (A) | None | No loss of service |

#### Exploitability

**Score**: 8.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 9 | Documented and widely used |
| Attack Complexity | 9 | A single step suffices |
| Tooling Availability | 7 | Common tools apply |
| Skill Level | 7 | Little skill needed |

#### Scalability

**Score**: 7.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 8 | Fully automatable |
| Target Scope | 8 | Every instance |
| Resource Requirements | 7 | Minimal resources |
| Detection Difficulty | 5 | Detectable with monitoring |

#### Reachability

**Score**: 3.5 | **Trust Zone**: Agent Runtime Zone (Trusted)

reviewer-agent sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 3.5.

---

### MI-15 — summarizer-llm

**Threat**: summarizer-llm fabricates reference numbers and clause citations that look real, which operators then paste into official documents.

**Category**: llm | **Original Risk Level**: Low | **Composite**: 6.4 (Medium)

#### CVSS 3.1 Base

**Score**: 7.6 | **Vector**: `CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:L/A:L`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Network | Reachable over the network |
| Attack Complexity (AC) | Low | No special conditions |
| Privileges Required (PR) | None | No privileges needed |
| User Interaction (UI) | Required | A user must act |
| Scope (S) | Unchanged | Impact stays in the component |
| Confidentiality (C) | High | Broad disclosure |
| Integrity (I) | Low | Limited modification |
| Availability (A) | Low | Degraded service |

#### Exploitability

**Score**: 7.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 9 | Documented and widely used |
| Attack Complexity | 8 | A single step suffices |
| Tooling Availability | 5 | Tools need adaptation |
| Skill Level | 8 | Little skill needed |

#### Scalability

**Score**: 7.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 7 | Fully automatable |
| Target Scope | 6 | A class of targets |
| Resource Requirements | 10 | Minimal resources |
| Detection Difficulty | 5 | Detectable with monitoring |

#### Reachability

**Score**: 2.0 | **Trust Zone**: Agent Runtime Zone (Trusted)

summarizer-llm sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 2.0.

---

### TE-9 — reviewer-agent

**Threat**: reviewer-agent claims certainty it does not have when summarising shipment risk, and customers rely on the stated confidence.

**Category**: agentic | **Original Risk Level**: Low | **Composite**: 6.4 (Medium)

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

**Score**: 5.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 7 | Documented and widely used |
| Attack Complexity | 5 | Needs some preparation |
| Tooling Availability | 5 | Tools need adaptation |
| Skill Level | 3 | Needs deep expertise |

#### Scalability

**Score**: 5.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 4 | Partly automatable |
| Target Scope | 4 | A class of targets |
| Resource Requirements | 7 | Minimal resources |
| Detection Difficulty | 7 | Blends with normal use |

#### Reachability

**Score**: 3.0 | **Trust Zone**: Agent Runtime Zone (Trusted)

reviewer-agent sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 3.0.

---

### S-7 — intake-agent

**Threat**: Certificate or DNS spoofing between embed-service-2 and intake-agent lets an attacker terminate the connection and present a lookalike endpoint when pinning is absent.

**Category**: spoofing | **Original Risk Level**: Low | **Composite**: 6.3 (Medium)

#### CVSS 3.1 Base

**Score**: 8.2 | **Vector**: `CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:L`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Network | Reachable over the network |
| Attack Complexity (AC) | Low | No special conditions |
| Privileges Required (PR) | None | No privileges needed |
| User Interaction (UI) | None | No user action needed |
| Scope (S) | Unchanged | Impact stays in the component |
| Confidentiality (C) | High | Broad disclosure |
| Integrity (I) | None | No modification |
| Availability (A) | Low | Degraded service |

#### Exploitability

**Score**: 7.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 8 | Documented and widely used |
| Attack Complexity | 8 | A single step suffices |
| Tooling Availability | 6 | Tools need adaptation |
| Skill Level | 8 | Little skill needed |

#### Scalability

**Score**: 6.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 7 | Fully automatable |
| Target Scope | 5 | A class of targets |
| Resource Requirements | 8 | Minimal resources |
| Detection Difficulty | 4 | Detectable with monitoring |

#### Reachability

**Score**: 1.5 | **Trust Zone**: Agent Runtime Zone (Trusted)

intake-agent sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 1.5.

---

### D-6 — intake-agent

**Threat**: Retry storms from trace-collector multiply the load on intake-agent when it slows down, turning a brief delay into a sustained outage.

**Category**: denial-of-service | **Original Risk Level**: Medium | **Composite**: 6.3 (Medium)

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

**Score**: 7.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 6 | Described in research |
| Attack Complexity | 7 | A single step suffices |
| Tooling Availability | 6 | Tools need adaptation |
| Skill Level | 9 | Little skill needed |

#### Scalability

**Score**: 6.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 9 | Fully automatable |
| Target Scope | 6 | A class of targets |
| Resource Requirements | 5 | Moderate resources |
| Detection Difficulty | 4 | Detectable with monitoring |

#### Reachability

**Score**: 2.0 | **Trust Zone**: Agent Runtime Zone (Trusted)

intake-agent sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 2.0.

---

### D-17 — tool-server-1

**Threat**: A slow-read attack holds connections to tool-server-1 open and ties up the workers handling tool call arguments and results until none remain for real requests.

**Category**: denial-of-service | **Original Risk Level**: Low | **Composite**: 6.3 (Medium)

#### CVSS 3.1 Base

**Score**: 7.1 | **Vector**: `CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:H`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Adjacent | Needs an adjacent network |
| Attack Complexity (AC) | Low | No special conditions |
| Privileges Required (PR) | None | No privileges needed |
| User Interaction (UI) | None | No user action needed |
| Scope (S) | Unchanged | Impact stays in the component |
| Confidentiality (C) | Low | Limited disclosure |
| Integrity (I) | None | No modification |
| Availability (A) | High | Loss of service |

#### Exploitability

**Score**: 8.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 9 | Documented and widely used |
| Attack Complexity | 8 | A single step suffices |
| Tooling Availability | 7 | Common tools apply |
| Skill Level | 8 | Little skill needed |

#### Scalability

**Score**: 6.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 7 | Fully automatable |
| Target Scope | 7 | Every instance |
| Resource Requirements | 6 | Moderate resources |
| Detection Difficulty | 4 | Detectable with monitoring |

#### Reachability

**Score**: 2.5 | **Trust Zone**: Agent Runtime Zone (Trusted)

tool-server-1 sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 2.5.

---

### D-22 — summarizer-llm

**Threat**: A single oversized or deeply nested payload makes summarizer-llm spend disproportionate memory and CPU parsing shipment records fed into summaries.

**Category**: denial-of-service | **Original Risk Level**: High | **Composite**: 6.3 (Medium)

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

**Score**: 7.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 6 | Described in research |
| Attack Complexity | 8 | A single step suffices |
| Tooling Availability | 8 | Common tools apply |
| Skill Level | 8 | Little skill needed |

#### Scalability

**Score**: 5.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 8 | Fully automatable |
| Target Scope | 7 | Every instance |
| Resource Requirements | 4 | Moderate resources |
| Detection Difficulty | 1 | Readily detected |

#### Reachability

**Score**: 2.0 | **Trust Zone**: Agent Runtime Zone (Trusted)

summarizer-llm sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 2.0.

---

### D-34 — policy-engine

**Threat**: Expensive queries over guardrail rules and approval decisions can be triggered by any authorised caller of policy-engine, so one user can degrade the service for all.

**Category**: denial-of-service | **Original Risk Level**: Critical | **Composite**: 6.3 (Medium)

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

**Score**: 8.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 8 | Documented and widely used |
| Attack Complexity | 8 | A single step suffices |
| Tooling Availability | 7 | Common tools apply |
| Skill Level | 9 | Little skill needed |

#### Scalability

**Score**: 6.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 9 | Fully automatable |
| Target Scope | 8 | Every instance |
| Resource Requirements | 3 | Needs heavy infrastructure |
| Detection Difficulty | 4 | Detectable with monitoring |

#### Reachability

**Score**: 2.0 | **Trust Zone**: Operations Zone (Trusted)

policy-engine sits in the Operations Zone. The zone baseline is 2.5 and the refinement for this finding gives 2.0.

---

### E-23 — summarizer-llm

**Threat**: Object identifiers in requests to summarizer-llm are trusted without an ownership check, so a caller can read or change shipment records fed into summaries that belong to others.

**Category**: privilege-escalation | **Original Risk Level**: Critical | **Composite**: 6.3 (Medium)

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
| Known Techniques | 7 | Documented and widely used |
| Attack Complexity | 4 | Needs some preparation |
| Tooling Availability | 4 | Tools need adaptation |
| Skill Level | 3 | Needs deep expertise |

#### Scalability

**Score**: 6.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 5 | Partly automatable |
| Target Scope | 6 | A class of targets |
| Resource Requirements | 7 | Minimal resources |
| Detection Difficulty | 6 | Detectable with monitoring |

#### Reachability

**Score**: 3.0 | **Trust Zone**: Agent Runtime Zone (Trusted)

summarizer-llm sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 3.0.

---

### E-30 — eval-runner

**Threat**: eval-runner runs with broader permissions than its function needs, so a flaw in handling replayed traces and judge verdicts yields access to unrelated resources.

**Category**: privilege-escalation | **Original Risk Level**: Low | **Composite**: 6.3 (Medium)

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

**Score**: 5.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 5 | Described in research |
| Attack Complexity | 6 | Needs some preparation |
| Tooling Availability | 6 | Tools need adaptation |
| Skill Level | 5 | Intermediate skill |

#### Scalability

**Score**: 5.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 5 | Partly automatable |
| Target Scope | 5 | A class of targets |
| Resource Requirements | 8 | Minimal resources |
| Detection Difficulty | 4 | Detectable with monitoring |

#### Reachability

**Score**: 3.0 | **Trust Zone**: Operations Zone (Trusted)

eval-runner sits in the Operations Zone. The zone baseline is 2.5 and the refinement for this finding gives 3.0.

---

### AG-27 — tool-server-1

**Threat**: Memory written by tool-server-1 is trusted on later runs, so one poisoned entry changes the behaviour of every future task.

**Category**: agentic | **Original Risk Level**: High | **Composite**: 6.3 (Medium)

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

**Score**: 4.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 6 | Described in research |
| Attack Complexity | 3 | Needs chained steps |
| Tooling Availability | 4 | Tools need adaptation |
| Skill Level | 5 | Intermediate skill |

#### Scalability

**Score**: 5.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 5 | Partly automatable |
| Target Scope | 3 | One specific target |
| Resource Requirements | 7 | Minimal resources |
| Detection Difficulty | 7 | Blends with normal use |

#### Reachability

**Score**: 3.0 | **Trust Zone**: Agent Runtime Zone (Trusted)

tool-server-1 sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 3.0.

---

### LLM-9 — router-agent

**Threat**: Encoded or multilingual payloads bypass the keyword filter in front of router-agent, which only checks plain English text.

**Category**: llm | **Original Risk Level**: Medium | **Composite**: 6.3 (Medium)

#### CVSS 3.1 Base

**Score**: 6.9 | **Vector**: `CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:C/C:L/I:H/A:N`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Network | Reachable over the network |
| Attack Complexity (AC) | High | Needs specific conditions |
| Privileges Required (PR) | None | No privileges needed |
| User Interaction (UI) | Required | A user must act |
| Scope (S) | Changed | Impact crosses a boundary |
| Confidentiality (C) | Low | Limited disclosure |
| Integrity (I) | High | Broad modification |
| Availability (A) | None | No loss of service |

#### Exploitability

**Score**: 8.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 8 | Documented and widely used |
| Attack Complexity | 9 | A single step suffices |
| Tooling Availability | 7 | Common tools apply |
| Skill Level | 8 | Little skill needed |

#### Scalability

**Score**: 6.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 5 | Partly automatable |
| Target Scope | 6 | A class of targets |
| Resource Requirements | 8 | Minimal resources |
| Detection Difficulty | 5 | Detectable with monitoring |

#### Reachability

**Score**: 3.0 | **Trust Zone**: Agent Runtime Zone (Trusted)

router-agent sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 3.0.

---

### LLM-21 — model-gateway

**Threat**: Verbose responses from model-gateway expose token probabilities and intermediate scores that speed up extraction.

**Category**: llm | **Original Risk Level**: Medium | **Composite**: 6.3 (Medium)

#### CVSS 3.1 Base

**Score**: 8.7 | **Vector**: `CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:C/C:H/I:H/A:N`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Network | Reachable over the network |
| Attack Complexity (AC) | High | Needs specific conditions |
| Privileges Required (PR) | None | No privileges needed |
| User Interaction (UI) | None | No user action needed |
| Scope (S) | Changed | Impact crosses a boundary |
| Confidentiality (C) | High | Broad disclosure |
| Integrity (I) | High | Broad modification |
| Availability (A) | None | No loss of service |

#### Exploitability

**Score**: 6.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 6 | Described in research |
| Attack Complexity | 9 | A single step suffices |
| Tooling Availability | 5 | Tools need adaptation |
| Skill Level | 6 | Intermediate skill |

#### Scalability

**Score**: 7.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 7 | Fully automatable |
| Target Scope | 6 | A class of targets |
| Resource Requirements | 9 | Minimal resources |
| Detection Difficulty | 6 | Detectable with monitoring |

#### Reachability

**Score**: 1.5 | **Trust Zone**: Agent Runtime Zone (Trusted)

model-gateway sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 1.5.

---

### LLM-31 — kb-index

**Threat**: Records written into kb-index by low-trust sources are later used as ground truth, so an attacker who plants entries shifts model answers.

**Category**: llm | **Original Risk Level**: Medium | **Composite**: 6.3 (Medium)

#### CVSS 3.1 Base

**Score**: 8.7 | **Vector**: `CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:C/C:H/I:H/A:N`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Network | Reachable over the network |
| Attack Complexity (AC) | High | Needs specific conditions |
| Privileges Required (PR) | None | No privileges needed |
| User Interaction (UI) | None | No user action needed |
| Scope (S) | Changed | Impact crosses a boundary |
| Confidentiality (C) | High | Broad disclosure |
| Integrity (I) | High | Broad modification |
| Availability (A) | None | No loss of service |

#### Exploitability

**Score**: 6.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 6 | Described in research |
| Attack Complexity | 7 | A single step suffices |
| Tooling Availability | 6 | Tools need adaptation |
| Skill Level | 7 | Little skill needed |

#### Scalability

**Score**: 7.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 8 | Fully automatable |
| Target Scope | 5 | A class of targets |
| Resource Requirements | 9 | Minimal resources |
| Detection Difficulty | 6 | Detectable with monitoring |

#### Reachability

**Score**: 1.5 | **Trust Zone**: Data Zone (Trusted)

kb-index sits in the Data Zone. The zone baseline is 2.5 and the refinement for this finding gives 1.5.

---

### LLM-36 — memory-store

**Threat**: Fine-tuning data assembled from memory-store is not checked for outliers or duplicates, so a small batch of crafted examples changes model behaviour.

**Category**: llm | **Original Risk Level**: High | **Composite**: 6.3 (Medium)

#### CVSS 3.1 Base

**Score**: 7.5 | **Vector**: `CVSS:3.1/AV:A/AC:H/PR:L/UI:R/S:C/C:H/I:H/A:L`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Adjacent | Needs an adjacent network |
| Attack Complexity (AC) | High | Needs specific conditions |
| Privileges Required (PR) | Low | A basic account is needed |
| User Interaction (UI) | Required | A user must act |
| Scope (S) | Changed | Impact crosses a boundary |
| Confidentiality (C) | High | Broad disclosure |
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

**Score**: 8.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 9 | Fully automatable |
| Target Scope | 8 | Every instance |
| Resource Requirements | 8 | Minimal resources |
| Detection Difficulty | 7 | Blends with normal use |

#### Reachability

**Score**: 2.0 | **Trust Zone**: Data Zone (Trusted)

memory-store sits in the Data Zone. The zone baseline is 2.5 and the refinement for this finding gives 2.0.

---

### OI-1 — intake-agent

**Threat**: intake-agent emits URLs that downstream services fetch, so an attacker can make internal addresses part of the output and trigger server-side requests.

**Category**: llm | **Original Risk Level**: Low | **Composite**: 6.3 (Medium)

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

**Score**: 7.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 6 | Described in research |
| Attack Complexity | 9 | A single step suffices |
| Tooling Availability | 6 | Tools need adaptation |
| Skill Level | 7 | Little skill needed |

#### Scalability

**Score**: 7.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 8 | Fully automatable |
| Target Scope | 5 | A class of targets |
| Resource Requirements | 9 | Minimal resources |
| Detection Difficulty | 6 | Detectable with monitoring |

#### Reachability

**Score**: 1.5 | **Trust Zone**: Agent Runtime Zone (Trusted)

intake-agent sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 1.5.

---

### MI-16 — eval-runner

**Threat**: Confident wording from eval-runner hides low retrieval quality, so operators cannot tell a grounded answer from a guess.

**Category**: llm | **Original Risk Level**: Medium | **Composite**: 6.3 (Medium)

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
| Scriptability | 5 | Partly automatable |
| Target Scope | 7 | Every instance |
| Resource Requirements | 8 | Minimal resources |
| Detection Difficulty | 8 | Blends with normal use |

#### Reachability

**Score**: 1.5 | **Trust Zone**: Operations Zone (Trusted)

eval-runner sits in the Operations Zone. The zone baseline is 2.5 and the refinement for this finding gives 1.5.

---

### MI-19 — worker-3

**Threat**: worker-3 fabricates reference numbers and clause citations that look real, which operators then paste into official documents.

**Category**: llm | **Original Risk Level**: Medium | **Composite**: 6.3 (Medium)

#### CVSS 3.1 Base

**Score**: 6.9 | **Vector**: `CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:C/C:L/I:H/A:N`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Network | Reachable over the network |
| Attack Complexity (AC) | High | Needs specific conditions |
| Privileges Required (PR) | None | No privileges needed |
| User Interaction (UI) | Required | A user must act |
| Scope (S) | Changed | Impact crosses a boundary |
| Confidentiality (C) | Low | Limited disclosure |
| Integrity (I) | High | Broad modification |
| Availability (A) | None | No loss of service |

#### Exploitability

**Score**: 8.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 8 | Documented and widely used |
| Attack Complexity | 9 | A single step suffices |
| Tooling Availability | 5 | Tools need adaptation |
| Skill Level | 10 | Little skill needed |

#### Scalability

**Score**: 7.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 6 | Partly automatable |
| Target Scope | 5 | A class of targets |
| Resource Requirements | 10 | Minimal resources |
| Detection Difficulty | 7 | Blends with normal use |

#### Reachability

**Score**: 2.0 | **Trust Zone**: Agent Runtime Zone (Trusted)

worker-3 sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 2.0.

---

### TE-1 — intake-agent

**Threat**: intake-agent adopts a persona that presents itself as a named colleague, so operators trust its suggestions more than its accuracy warrants.

**Category**: agentic | **Original Risk Level**: High | **Composite**: 6.3 (Medium)

#### CVSS 3.1 Base

**Score**: 9.9 | **Vector**: `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:L/I:H/A:H`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Network | Reachable over the network |
| Attack Complexity (AC) | Low | No special conditions |
| Privileges Required (PR) | Low | A basic account is needed |
| User Interaction (UI) | None | No user action needed |
| Scope (S) | Changed | Impact crosses a boundary |
| Confidentiality (C) | Low | Limited disclosure |
| Integrity (I) | High | Broad modification |
| Availability (A) | High | Loss of service |

#### Exploitability

**Score**: 5.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 5 | Described in research |
| Attack Complexity | 4 | Needs some preparation |
| Tooling Availability | 5 | Tools need adaptation |
| Skill Level | 6 | Intermediate skill |

#### Scalability

**Score**: 5.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 4 | Partly automatable |
| Target Scope | 4 | A class of targets |
| Resource Requirements | 7 | Minimal resources |
| Detection Difficulty | 7 | Blends with normal use |

#### Reachability

**Score**: 2.5 | **Trust Zone**: Agent Runtime Zone (Trusted)

intake-agent sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 2.5.

---

### S-15 — worker-3

**Threat**: Low-entropy identifiers accepted by worker-3 double as credentials, so an attacker who enumerates them submits requests under a victim's identity.

**Category**: spoofing | **Original Risk Level**: High | **Composite**: 6.2 (Medium)

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

**Score**: 6.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 6 | Described in research |
| Attack Complexity | 7 | A single step suffices |
| Tooling Availability | 8 | Common tools apply |
| Skill Level | 5 | Intermediate skill |

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

worker-3 sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 2.5.

---

### S-23 — embed-service-2

**Threat**: An attacker replays a captured service credential against embed-service-2, which does not bind the credential to the session or channel it was issued for, so the replay is accepted as the original caller.

**Category**: spoofing | **Original Risk Level**: Medium | **Composite**: 6.2 (Medium)

#### CVSS 3.1 Base

**Score**: 6.8 | **Vector**: `CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:H/I:L/A:N`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Local | Needs local access |
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
| Known Techniques | 7 | Documented and widely used |
| Attack Complexity | 6 | Needs some preparation |
| Tooling Availability | 8 | Common tools apply |
| Skill Level | 7 | Little skill needed |

#### Scalability

**Score**: 6.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 9 | Fully automatable |
| Target Scope | 4 | A class of targets |
| Resource Requirements | 7 | Minimal resources |
| Detection Difficulty | 6 | Detectable with monitoring |

#### Reachability

**Score**: 3.5 | **Trust Zone**: Agent Runtime Zone (Trusted)

embed-service-2 sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 3.5.

---

### S-31 — scheduler-1

**Threat**: A compromised peer presents a forged service identity to scheduler-1, and scheduler-1 accepts the claim without verifying the signature chain back to the issuing authority.

**Category**: spoofing | **Original Risk Level**: Low | **Composite**: 6.2 (Medium)

#### CVSS 3.1 Base

**Score**: 8.5 | **Vector**: `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:L/I:H/A:N`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Network | Reachable over the network |
| Attack Complexity (AC) | Low | No special conditions |
| Privileges Required (PR) | Low | A basic account is needed |
| User Interaction (UI) | None | No user action needed |
| Scope (S) | Changed | Impact crosses a boundary |
| Confidentiality (C) | Low | Limited disclosure |
| Integrity (I) | High | Broad modification |
| Availability (A) | None | No loss of service |

#### Exploitability

**Score**: 6.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 7 | Documented and widely used |
| Attack Complexity | 6 | Needs some preparation |
| Tooling Availability | 5 | Tools need adaptation |
| Skill Level | 8 | Little skill needed |

#### Scalability

**Score**: 6.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 9 | Fully automatable |
| Target Scope | 6 | A class of targets |
| Resource Requirements | 7 | Minimal resources |
| Detection Difficulty | 4 | Detectable with monitoring |

#### Reachability

**Score**: 1.5 | **Trust Zone**: Agent Runtime Zone (Trusted)

scheduler-1 sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 1.5.

---

### R-2 — partner-feed

**Threat**: Clock drift between partner-feed and edge-gateway leaves events in inconsistent order, so the sequence of actions on signed carrier manifests cannot be reconstructed reliably.

**Category**: repudiation | **Original Risk Level**: Low | **Composite**: 6.2 (Medium)

#### CVSS 3.1 Base

**Score**: 3.5 | **Vector**: `CVSS:3.1/AV:A/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:L`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Adjacent | Needs an adjacent network |
| Attack Complexity (AC) | Low | No special conditions |
| Privileges Required (PR) | Low | A basic account is needed |
| User Interaction (UI) | None | No user action needed |
| Scope (S) | Unchanged | Impact stays in the component |
| Confidentiality (C) | None | No disclosure |
| Integrity (I) | None | No modification |
| Availability (A) | Low | Degraded service |

#### Exploitability

**Score**: 6.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 6 | Described in research |
| Attack Complexity | 7 | A single step suffices |
| Tooling Availability | 4 | Tools need adaptation |
| Skill Level | 7 | Little skill needed |

#### Scalability

**Score**: 8.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 7 | Fully automatable |
| Target Scope | 6 | A class of targets |
| Resource Requirements | 10 | Minimal resources |
| Detection Difficulty | 9 | Blends with normal use |

#### Reachability

**Score**: 10.0 | **Trust Zone**: Public Internet (Untrusted)

partner-feed sits in the Public Internet. The zone baseline is 9.0 and the refinement for this finding gives 10.0.

---

### R-31 — auth-broker

**Threat**: Operators approve changes to credential assertions and session grants through a chat message or ticket comment that is not bound to the executed change, so approvals can be disputed.

**Category**: repudiation | **Original Risk Level**: High | **Composite**: 6.2 (Medium)

#### CVSS 3.1 Base

**Score**: 5.4 | **Vector**: `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:L`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Network | Reachable over the network |
| Attack Complexity (AC) | Low | No special conditions |
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
| Known Techniques | 7 | Documented and widely used |
| Attack Complexity | 8 | A single step suffices |
| Tooling Availability | 6 | Tools need adaptation |
| Skill Level | 7 | Little skill needed |

#### Scalability

**Score**: 7.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 5 | Partly automatable |
| Target Scope | 6 | A class of targets |
| Resource Requirements | 9 | Minimal resources |
| Detection Difficulty | 8 | Blends with normal use |

#### Reachability

**Score**: 6.0 | **Trust Zone**: Edge DMZ (Semi-trusted)

auth-broker sits in the Edge DMZ. The zone baseline is 6.5 and the refinement for this finding gives 6.0.

---

### AG-33 — tool-server-1

**Threat**: Delegation from worker-3 to tool-server-1 carries the full authority of the original session, so a low-trust sub-task can use high-trust rights.

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

**Score**: 5.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 4 | Described in research |
| Attack Complexity | 6 | Needs some preparation |
| Tooling Availability | 5 | Tools need adaptation |
| Skill Level | 5 | Intermediate skill |

#### Scalability

**Score**: 6.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 2 | Manual for each target |
| Target Scope | 5 | A class of targets |
| Resource Requirements | 9 | Minimal resources |
| Detection Difficulty | 8 | Blends with normal use |

#### Reachability

**Score**: 3.5 | **Trust Zone**: Agent Runtime Zone (Trusted)

tool-server-1 sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 3.5.

---

### LLM-52 — policy-engine

**Threat**: policy-engine follows links and files named in guardrail rules and approval decisions, which turns a harmless-looking request into a fetch of attacker-controlled content.

**Category**: llm | **Original Risk Level**: Medium | **Composite**: 6.2 (Medium)

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
| Known Techniques | 7 | Documented and widely used |
| Attack Complexity | 6 | Needs some preparation |
| Tooling Availability | 8 | Common tools apply |
| Skill Level | 7 | Little skill needed |

#### Scalability

**Score**: 6.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 5 | Partly automatable |
| Target Scope | 5 | A class of targets |
| Resource Requirements | 9 | Minimal resources |
| Detection Difficulty | 5 | Detectable with monitoring |

#### Reachability

**Score**: 3.5 | **Trust Zone**: Operations Zone (Trusted)

policy-engine sits in the Operations Zone. The zone baseline is 2.5 and the refinement for this finding gives 3.5.

---

### MI-3 — intake-agent

**Threat**: intake-agent states carrier rules and customs requirements as fact without grounding them in a cited source, so an operator may act on an invented rule.

**Category**: llm | **Original Risk Level**: Critical | **Composite**: 6.2 (Medium)

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

**Score**: 7.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 7 | Documented and widely used |
| Attack Complexity | 8 | A single step suffices |
| Tooling Availability | 6 | Tools need adaptation |
| Skill Level | 7 | Little skill needed |

#### Scalability

**Score**: 6.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 8 | Fully automatable |
| Target Scope | 5 | A class of targets |
| Resource Requirements | 9 | Minimal resources |
| Detection Difficulty | 4 | Detectable with monitoring |

#### Reachability

**Score**: 1.5 | **Trust Zone**: Agent Runtime Zone (Trusted)

intake-agent sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 1.5.

---

### MI-20 — worker-3

**Threat**: Stale data in the knowledge base lets worker-3 present superseded tariffs as current, causing wrong quotes.

**Category**: llm | **Original Risk Level**: Medium | **Composite**: 6.2 (Medium)

#### CVSS 3.1 Base

**Score**: 7.1 | **Vector**: `CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:C/C:H/I:L/A:N`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Local | Needs local access |
| Attack Complexity (AC) | Low | No special conditions |
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
| Known Techniques | 8 | Documented and widely used |
| Attack Complexity | 6 | Needs some preparation |
| Tooling Availability | 7 | Common tools apply |
| Skill Level | 7 | Little skill needed |

#### Scalability

**Score**: 6.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 5 | Partly automatable |
| Target Scope | 6 | A class of targets |
| Resource Requirements | 8 | Minimal resources |
| Detection Difficulty | 5 | Detectable with monitoring |

#### Reachability

**Score**: 3.5 | **Trust Zone**: Agent Runtime Zone (Trusted)

worker-3 sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 3.5.

---

### S-6 — intake-agent

**Threat**: Session fixation against intake-agent lets an attacker pre-seed an identifier and reuse the session after the victim authenticates.

**Category**: spoofing | **Original Risk Level**: High | **Composite**: 6.1 (Medium)

#### CVSS 3.1 Base

**Score**: 6.5 | **Vector**: `CVSS:3.1/AV:N/AC:H/PR:L/UI:R/S:C/C:H/I:L/A:N`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Network | Reachable over the network |
| Attack Complexity (AC) | High | Needs specific conditions |
| Privileges Required (PR) | Low | A basic account is needed |
| User Interaction (UI) | Required | A user must act |
| Scope (S) | Changed | Impact crosses a boundary |
| Confidentiality (C) | High | Broad disclosure |
| Integrity (I) | Low | Limited modification |
| Availability (A) | None | No loss of service |

#### Exploitability

**Score**: 7.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 8 | Documented and widely used |
| Attack Complexity | 7 | A single step suffices |
| Tooling Availability | 8 | Common tools apply |
| Skill Level | 7 | Little skill needed |

#### Scalability

**Score**: 6.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 9 | Fully automatable |
| Target Scope | 4 | A class of targets |
| Resource Requirements | 6 | Moderate resources |
| Detection Difficulty | 5 | Detectable with monitoring |

#### Reachability

**Score**: 3.5 | **Trust Zone**: Agent Runtime Zone (Trusted)

intake-agent sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 3.5.

---

### S-10 — router-agent

**Threat**: A shared or long-lived routing token on router-agent lets anyone who obtains one copy authenticate as every tenant that uses the same deployment profile.

**Category**: spoofing | **Original Risk Level**: Medium | **Composite**: 6.1 (Medium)

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

**Score**: 6.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 5 | Described in research |
| Attack Complexity | 5 | Needs some preparation |
| Tooling Availability | 8 | Common tools apply |
| Skill Level | 6 | Intermediate skill |

#### Scalability

**Score**: 6.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 8 | Fully automatable |
| Target Scope | 5 | A class of targets |
| Resource Requirements | 7 | Minimal resources |
| Detection Difficulty | 4 | Detectable with monitoring |

#### Reachability

**Score**: 2.5 | **Trust Zone**: Agent Runtime Zone (Trusted)

router-agent sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 2.5.

---

### S-42 — reviewer-agent

**Threat**: A compromised peer presents a forged service identity to reviewer-agent, and reviewer-agent accepts the claim without verifying the signature chain back to the issuing authority.

**Category**: spoofing | **Original Risk Level**: Low | **Composite**: 6.1 (Medium)

#### CVSS 3.1 Base

**Score**: 8.5 | **Vector**: `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:N/A:L`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Network | Reachable over the network |
| Attack Complexity (AC) | Low | No special conditions |
| Privileges Required (PR) | Low | A basic account is needed |
| User Interaction (UI) | None | No user action needed |
| Scope (S) | Changed | Impact crosses a boundary |
| Confidentiality (C) | High | Broad disclosure |
| Integrity (I) | None | No modification |
| Availability (A) | Low | Degraded service |

#### Exploitability

**Score**: 6.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 7 | Documented and widely used |
| Attack Complexity | 5 | Needs some preparation |
| Tooling Availability | 6 | Tools need adaptation |
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

**Score**: 2.0 | **Trust Zone**: Agent Runtime Zone (Trusted)

reviewer-agent sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 2.0.

---

### T-25 — memory-store

**Threat**: Backups and exports of task history and operator preferences on memory-store are writable by operators without a second approver, so a malicious change survives restores.

**Category**: tampering | **Original Risk Level**: Critical | **Composite**: 6.1 (Medium)

#### CVSS 3.1 Base

**Score**: 9.4 | **Vector**: `CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:H/A:H`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Network | Reachable over the network |
| Attack Complexity (AC) | Low | No special conditions |
| Privileges Required (PR) | None | No privileges needed |
| User Interaction (UI) | None | No user action needed |
| Scope (S) | Unchanged | Impact stays in the component |
| Confidentiality (C) | Low | Limited disclosure |
| Integrity (I) | High | Broad modification |
| Availability (A) | High | Loss of service |

#### Exploitability

**Score**: 5.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 4 | Described in research |
| Attack Complexity | 5 | Needs some preparation |
| Tooling Availability | 6 | Tools need adaptation |
| Skill Level | 7 | Little skill needed |

#### Scalability

**Score**: 5.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 4 | Partly automatable |
| Target Scope | 5 | A class of targets |
| Resource Requirements | 8 | Minimal resources |
| Detection Difficulty | 5 | Detectable with monitoring |

#### Reachability

**Score**: 1.5 | **Trust Zone**: Data Zone (Trusted)

memory-store sits in the Data Zone. The zone baseline is 2.5 and the refinement for this finding gives 1.5.

---

### D-35 — audit-ledger

**Threat**: Expensive queries over approval and tool call records can be triggered by any authorised caller of audit-ledger, so one user can degrade the service for all.

**Category**: denial-of-service | **Original Risk Level**: Note | **Composite**: 6.1 (Medium)

#### CVSS 3.1 Base

**Score**: 7.1 | **Vector**: `CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:N/A:H`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Network | Reachable over the network |
| Attack Complexity (AC) | Low | No special conditions |
| Privileges Required (PR) | None | No privileges needed |
| User Interaction (UI) | Required | A user must act |
| Scope (S) | Unchanged | Impact stays in the component |
| Confidentiality (C) | Low | Limited disclosure |
| Integrity (I) | None | No modification |
| Availability (A) | High | Loss of service |

#### Exploitability

**Score**: 7.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 8 | Documented and widely used |
| Attack Complexity | 8 | A single step suffices |
| Tooling Availability | 6 | Tools need adaptation |
| Skill Level | 8 | Little skill needed |

#### Scalability

**Score**: 5.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 7 | Fully automatable |
| Target Scope | 6 | A class of targets |
| Resource Requirements | 4 | Moderate resources |
| Detection Difficulty | 3 | Readily detected |

#### Reachability

**Score**: 3.0 | **Trust Zone**: Operations Zone (Trusted)

audit-ledger sits in the Operations Zone. The zone baseline is 2.5 and the refinement for this finding gives 3.0.

---

### E-17 — reviewer-agent

**Threat**: Multi-tenant separation in reviewer-agent depends on a request header that clients can set, allowing one tenant to act in another's scope.

**Category**: privilege-escalation | **Original Risk Level**: Medium | **Composite**: 6.1 (Medium)

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

**Score**: 5.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 6 | Described in research |
| Attack Complexity | 4 | Needs some preparation |
| Tooling Availability | 6 | Tools need adaptation |
| Skill Level | 4 | Intermediate skill |

#### Scalability

**Score**: 5.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 7 | Fully automatable |
| Target Scope | 3 | One specific target |
| Resource Requirements | 6 | Moderate resources |
| Detection Difficulty | 6 | Detectable with monitoring |

#### Reachability

**Score**: 1.5 | **Trust Zone**: Agent Runtime Zone (Trusted)

reviewer-agent sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 1.5.

---

### E-28 — trace-collector

**Threat**: Multi-tenant separation in trace-collector depends on a request header that clients can set, allowing one tenant to act in another's scope.

**Category**: privilege-escalation | **Original Risk Level**: Medium | **Composite**: 6.1 (Medium)

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
| Known Techniques | 6 | Described in research |
| Attack Complexity | 4 | Needs some preparation |
| Tooling Availability | 3 | Needs custom tooling |
| Skill Level | 5 | Intermediate skill |

#### Scalability

**Score**: 6.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 5 | Partly automatable |
| Target Scope | 4 | A class of targets |
| Resource Requirements | 9 | Minimal resources |
| Detection Difficulty | 6 | Detectable with monitoring |

#### Reachability

**Score**: 2.0 | **Trust Zone**: Operations Zone (Trusted)

trace-collector sits in the Operations Zone. The zone baseline is 2.5 and the refinement for this finding gives 2.0.

---

### E-32 — planner-agent

**Threat**: Multi-tenant separation in planner-agent depends on a request header that clients can set, allowing one tenant to act in another's scope.

**Category**: privilege-escalation | **Original Risk Level**: Low | **Composite**: 6.1 (Medium)

#### CVSS 3.1 Base

**Score**: 9.9 | **Vector**: `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:L/I:H/A:H`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Network | Reachable over the network |
| Attack Complexity (AC) | Low | No special conditions |
| Privileges Required (PR) | Low | A basic account is needed |
| User Interaction (UI) | None | No user action needed |
| Scope (S) | Changed | Impact crosses a boundary |
| Confidentiality (C) | Low | Limited disclosure |
| Integrity (I) | High | Broad modification |
| Availability (A) | High | Loss of service |

#### Exploitability

**Score**: 5.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 6 | Described in research |
| Attack Complexity | 5 | Needs some preparation |
| Tooling Availability | 6 | Tools need adaptation |
| Skill Level | 3 | Needs deep expertise |

#### Scalability

**Score**: 4.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 4 | Partly automatable |
| Target Scope | 5 | A class of targets |
| Resource Requirements | 6 | Moderate resources |
| Detection Difficulty | 3 | Readily detected |

#### Reachability

**Score**: 2.5 | **Trust Zone**: Agent Runtime Zone (Trusted)

planner-agent sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 2.5.

---

### LLM-33 — memory-store

**Threat**: Evaluation labels consumed from memory-store are produced by a judge model that can itself be influenced by planted traces.

**Category**: llm | **Original Risk Level**: Critical | **Composite**: 6.1 (Medium)

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
| Scriptability | 5 | Partly automatable |
| Target Scope | 5 | A class of targets |
| Resource Requirements | 9 | Minimal resources |
| Detection Difficulty | 5 | Detectable with monitoring |

#### Reachability

**Score**: 2.5 | **Trust Zone**: Data Zone (Trusted)

memory-store sits in the Data Zone. The zone baseline is 2.5 and the refinement for this finding gives 2.5.

---

### OI-2 — intake-agent

**Threat**: Structured output from intake-agent is trusted by queue-a2 as already validated, so a malformed field flows straight into business logic.

**Category**: llm | **Original Risk Level**: High | **Composite**: 6.1 (Medium)

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

**Score**: 6.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 7 | Documented and widely used |
| Attack Complexity | 7 | A single step suffices |
| Tooling Availability | 5 | Tools need adaptation |
| Skill Level | 7 | Little skill needed |

#### Scalability

**Score**: 7.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 7 | Fully automatable |
| Target Scope | 6 | A class of targets |
| Resource Requirements | 9 | Minimal resources |
| Detection Difficulty | 6 | Detectable with monitoring |

#### Reachability

**Score**: 1.5 | **Trust Zone**: Agent Runtime Zone (Trusted)

intake-agent sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 1.5.

---

### OI-3 — intake-agent

**Threat**: Markdown or HTML produced by intake-agent contains remote images that leak data when a client renders it.

**Category**: llm | **Original Risk Level**: High | **Composite**: 6.1 (Medium)

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

**Score**: 6.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 8 | Documented and widely used |
| Attack Complexity | 6 | Needs some preparation |
| Tooling Availability | 6 | Tools need adaptation |
| Skill Level | 6 | Intermediate skill |

#### Scalability

**Score**: 6.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 8 | Fully automatable |
| Target Scope | 5 | A class of targets |
| Resource Requirements | 9 | Minimal resources |
| Detection Difficulty | 4 | Detectable with monitoring |

#### Reachability

**Score**: 1.5 | **Trust Zone**: Agent Runtime Zone (Trusted)

intake-agent sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 1.5.

---

### MI-5 — intake-agent

**Threat**: Outputs from intake-agent flow into decisions without a review step, so one wrong answer is repeated across many shipments.

**Category**: llm | **Original Risk Level**: High | **Composite**: 6.1 (Medium)

#### CVSS 3.1 Base

**Score**: 7.5 | **Vector**: `CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:C/C:H/I:L/A:N`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Network | Reachable over the network |
| Attack Complexity (AC) | High | Needs specific conditions |
| Privileges Required (PR) | None | No privileges needed |
| User Interaction (UI) | None | No user action needed |
| Scope (S) | Changed | Impact crosses a boundary |
| Confidentiality (C) | High | Broad disclosure |
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

**Score**: 7.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 7 | Fully automatable |
| Target Scope | 7 | Every instance |
| Resource Requirements | 9 | Minimal resources |
| Detection Difficulty | 5 | Detectable with monitoring |

#### Reachability

**Score**: 1.5 | **Trust Zone**: Agent Runtime Zone (Trusted)

intake-agent sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 1.5.

---

### MI-12 — summarizer-llm

**Threat**: summarizer-llm states carrier rules and customs requirements as fact without grounding them in a cited source, so an operator may act on an invented rule.

**Category**: llm | **Original Risk Level**: Medium | **Composite**: 6.1 (Medium)

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
| Scriptability | 6 | Partly automatable |
| Target Scope | 5 | A class of targets |
| Resource Requirements | 9 | Minimal resources |
| Detection Difficulty | 6 | Detectable with monitoring |

#### Reachability

**Score**: 3.5 | **Trust Zone**: Agent Runtime Zone (Trusted)

summarizer-llm sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 3.5.

---

### TE-3 — intake-agent

**Threat**: intake-agent builds rapport over long sessions and starts to share unprompted details about earlier operators.

**Category**: agentic | **Original Risk Level**: Low | **Composite**: 6.1 (Medium)

#### CVSS 3.1 Base

**Score**: 9.1 | **Vector**: `CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Network | Reachable over the network |
| Attack Complexity (AC) | Low | No special conditions |
| Privileges Required (PR) | None | No privileges needed |
| User Interaction (UI) | None | No user action needed |
| Scope (S) | Unchanged | Impact stays in the component |
| Confidentiality (C) | High | Broad disclosure |
| Integrity (I) | High | Broad modification |
| Availability (A) | None | No loss of service |

#### Exploitability

**Score**: 5.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 7 | Documented and widely used |
| Attack Complexity | 3 | Needs chained steps |
| Tooling Availability | 4 | Tools need adaptation |
| Skill Level | 6 | Intermediate skill |

#### Scalability

**Score**: 5.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 4 | Partly automatable |
| Target Scope | 3 | One specific target |
| Resource Requirements | 9 | Minimal resources |
| Detection Difficulty | 6 | Detectable with monitoring |

#### Reachability

**Score**: 3.0 | **Trust Zone**: Agent Runtime Zone (Trusted)

intake-agent sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 3.0.

---

### TE-5 — intake-agent

**Threat**: intake-agent speaks with an authoritative tone about customs and legal matters, and operators may defer to it without checking.

**Category**: agentic | **Original Risk Level**: Medium | **Composite**: 6.1 (Medium)

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

**Score**: 5.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 6 | Described in research |
| Attack Complexity | 5 | Needs some preparation |
| Tooling Availability | 2 | Needs custom tooling |
| Skill Level | 7 | Little skill needed |

#### Scalability

**Score**: 5.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 2 | Manual for each target |
| Target Scope | 5 | A class of targets |
| Resource Requirements | 8 | Minimal resources |
| Detection Difficulty | 7 | Blends with normal use |

#### Reachability

**Score**: 1.5 | **Trust Zone**: Agent Runtime Zone (Trusted)

intake-agent sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 1.5.

---

### TE-10 — reviewer-agent

**Threat**: reviewer-agent speaks with an authoritative tone about customs and legal matters, and operators may defer to it without checking.

**Category**: agentic | **Original Risk Level**: Low | **Composite**: 6.1 (Medium)

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
| Known Techniques | 4 | Described in research |
| Attack Complexity | 4 | Needs some preparation |
| Tooling Availability | 3 | Needs custom tooling |
| Skill Level | 7 | Little skill needed |

#### Scalability

**Score**: 5.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 3 | Manual for each target |
| Target Scope | 4 | A class of targets |
| Resource Requirements | 8 | Minimal resources |
| Detection Difficulty | 7 | Blends with normal use |

#### Reachability

**Score**: 2.5 | **Trust Zone**: Agent Runtime Zone (Trusted)

reviewer-agent sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 2.5.

---

### TE-17 — reviewer-agent

**Threat**: Persuasive phrasing from reviewer-agent pushes operators to approve proposals quickly, which reduces careful review.

**Category**: agentic | **Original Risk Level**: Medium | **Composite**: 6.1 (Medium)

#### CVSS 3.1 Base

**Score**: 9.6 | **Vector**: `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:N`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Network | Reachable over the network |
| Attack Complexity (AC) | Low | No special conditions |
| Privileges Required (PR) | Low | A basic account is needed |
| User Interaction (UI) | None | No user action needed |
| Scope (S) | Changed | Impact crosses a boundary |
| Confidentiality (C) | High | Broad disclosure |
| Integrity (I) | High | Broad modification |
| Availability (A) | None | No loss of service |

#### Exploitability

**Score**: 5.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 7 | Documented and widely used |
| Attack Complexity | 5 | Needs some preparation |
| Tooling Availability | 5 | Tools need adaptation |
| Skill Level | 3 | Needs deep expertise |

#### Scalability

**Score**: 5.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 2 | Manual for each target |
| Target Scope | 6 | A class of targets |
| Resource Requirements | 7 | Minimal resources |
| Detection Difficulty | 5 | Detectable with monitoring |

#### Reachability

**Score**: 2.5 | **Trust Zone**: Agent Runtime Zone (Trusted)

reviewer-agent sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 2.5.

---

### S-13 — worker-2

**Threat**: An unauthenticated callback or health route on worker-2 accepts requests that downstream code treats as if they had come from trace-collector.

**Category**: spoofing | **Original Risk Level**: High | **Composite**: 6.0 (Medium)

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

**Score**: 6.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 7 | Documented and widely used |
| Attack Complexity | 5 | Needs some preparation |
| Tooling Availability | 6 | Tools need adaptation |
| Skill Level | 6 | Intermediate skill |

#### Scalability

**Score**: 6.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 6 | Partly automatable |
| Target Scope | 6 | A class of targets |
| Resource Requirements | 7 | Minimal resources |
| Detection Difficulty | 7 | Blends with normal use |

#### Reachability

**Score**: 3.5 | **Trust Zone**: Agent Runtime Zone (Trusted)

worker-2 sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 3.5.

---

### S-36 — eval-runner

**Threat**: Low-entropy identifiers accepted by eval-runner double as credentials, so an attacker who enumerates them submits requests under a victim's identity.

**Category**: spoofing | **Original Risk Level**: Critical | **Composite**: 6.0 (Medium)

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

**Score**: 6.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 7 | Documented and widely used |
| Attack Complexity | 8 | A single step suffices |
| Tooling Availability | 5 | Tools need adaptation |
| Skill Level | 6 | Intermediate skill |

#### Scalability

**Score**: 7.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 6 | Partly automatable |
| Target Scope | 7 | Every instance |
| Resource Requirements | 8 | Minimal resources |
| Detection Difficulty | 7 | Blends with normal use |

#### Reachability

**Score**: 2.5 | **Trust Zone**: Operations Zone (Trusted)

eval-runner sits in the Operations Zone. The zone baseline is 2.5 and the refinement for this finding gives 2.5.

---

### T-2 — auth-broker

**Threat**: Backups and exports of credential assertions and session grants on auth-broker are writable by operators without a second approver, so a malicious change survives restores.

**Category**: tampering | **Original Risk Level**: High | **Composite**: 6.0 (Medium)

#### CVSS 3.1 Base

**Score**: 4.6 | **Vector**: `CVSS:3.1/AV:A/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:L`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Adjacent | Needs an adjacent network |
| Attack Complexity (AC) | Low | No special conditions |
| Privileges Required (PR) | Low | A basic account is needed |
| User Interaction (UI) | None | No user action needed |
| Scope (S) | Unchanged | Impact stays in the component |
| Confidentiality (C) | None | No disclosure |
| Integrity (I) | Low | Limited modification |
| Availability (A) | Low | Degraded service |

#### Exploitability

**Score**: 7.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 7 | Documented and widely used |
| Attack Complexity | 9 | A single step suffices |
| Tooling Availability | 6 | Tools need adaptation |
| Skill Level | 8 | Little skill needed |

#### Scalability

**Score**: 6.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 7 | Fully automatable |
| Target Scope | 4 | A class of targets |
| Resource Requirements | 8 | Minimal resources |
| Detection Difficulty | 5 | Detectable with monitoring |

#### Reachability

**Score**: 6.0 | **Trust Zone**: Edge DMZ (Semi-trusted)

auth-broker sits in the Edge DMZ. The zone baseline is 6.5 and the refinement for this finding gives 6.0.

---

### R-1 — client-portal

**Threat**: Operators approve changes to operator requests and approval decisions through a chat message or ticket comment that is not bound to the executed change, so approvals can be disputed.

**Category**: repudiation | **Original Risk Level**: Low | **Composite**: 6.0 (Medium)

#### CVSS 3.1 Base

**Score**: 4.3 | **Vector**: `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Network | Reachable over the network |
| Attack Complexity (AC) | Low | No special conditions |
| Privileges Required (PR) | Low | A basic account is needed |
| User Interaction (UI) | None | No user action needed |
| Scope (S) | Unchanged | Impact stays in the component |
| Confidentiality (C) | None | No disclosure |
| Integrity (I) | Low | Limited modification |
| Availability (A) | None | No loss of service |

#### Exploitability

**Score**: 6.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 6 | Described in research |
| Attack Complexity | 7 | A single step suffices |
| Tooling Availability | 4 | Tools need adaptation |
| Skill Level | 7 | Little skill needed |

#### Scalability

**Score**: 7.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 6 | Partly automatable |
| Target Scope | 4 | A class of targets |
| Resource Requirements | 10 | Minimal resources |
| Detection Difficulty | 8 | Blends with normal use |

#### Reachability

**Score**: 8.0 | **Trust Zone**: Public Internet (Untrusted)

client-portal sits in the Public Internet. The zone baseline is 9.0 and the refinement for this finding gives 8.0.

---

### D-16 — tool-server-1

**Threat**: Retry storms from audit-ledger multiply the load on tool-server-1 when it slows down, turning a brief delay into a sustained outage.

**Category**: denial-of-service | **Original Risk Level**: Low | **Composite**: 6.0 (Medium)

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

**Score**: 8.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 8 | Documented and widely used |
| Attack Complexity | 9 | A single step suffices |
| Tooling Availability | 7 | Common tools apply |
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

**Score**: 3.0 | **Trust Zone**: Agent Runtime Zone (Trusted)

tool-server-1 sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 3.0.

---

### E-19 — tool-server-1

**Threat**: Multi-tenant separation in tool-server-1 depends on a request header that clients can set, allowing one tenant to act in another's scope.

**Category**: privilege-escalation | **Original Risk Level**: Critical | **Composite**: 6.0 (Medium)

#### CVSS 3.1 Base

**Score**: 9.0 | **Vector**: `CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:H/I:H/A:H`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Network | Reachable over the network |
| Attack Complexity (AC) | Low | No special conditions |
| Privileges Required (PR) | Low | A basic account is needed |
| User Interaction (UI) | Required | A user must act |
| Scope (S) | Changed | Impact crosses a boundary |
| Confidentiality (C) | High | Broad disclosure |
| Integrity (I) | High | Broad modification |
| Availability (A) | High | Loss of service |

#### Exploitability

**Score**: 5.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 4 | Described in research |
| Attack Complexity | 4 | Needs some preparation |
| Tooling Availability | 6 | Tools need adaptation |
| Skill Level | 6 | Intermediate skill |

#### Scalability

**Score**: 6.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 9 | Fully automatable |
| Target Scope | 4 | A class of targets |
| Resource Requirements | 8 | Minimal resources |
| Detection Difficulty | 5 | Detectable with monitoring |

#### Reachability

**Score**: 2.0 | **Trust Zone**: Agent Runtime Zone (Trusted)

tool-server-1 sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 2.0.

---

### E-20 — tool-server-1

**Threat**: A privileged maintenance task of tool-server-1 can be triggered through a queue message that any producer on the bus may publish.

**Category**: privilege-escalation | **Original Risk Level**: Medium | **Composite**: 6.0 (Medium)

#### CVSS 3.1 Base

**Score**: 8.0 | **Vector**: `CVSS:3.1/AV:N/AC:H/PR:L/UI:R/S:C/C:H/I:H/A:H`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Network | Reachable over the network |
| Attack Complexity (AC) | High | Needs specific conditions |
| Privileges Required (PR) | Low | A basic account is needed |
| User Interaction (UI) | Required | A user must act |
| Scope (S) | Changed | Impact crosses a boundary |
| Confidentiality (C) | High | Broad disclosure |
| Integrity (I) | High | Broad modification |
| Availability (A) | High | Loss of service |

#### Exploitability

**Score**: 6.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 6 | Described in research |
| Attack Complexity | 7 | A single step suffices |
| Tooling Availability | 5 | Tools need adaptation |
| Skill Level | 6 | Intermediate skill |

#### Scalability

**Score**: 4.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 5 | Partly automatable |
| Target Scope | 3 | One specific target |
| Resource Requirements | 6 | Moderate resources |
| Detection Difficulty | 4 | Detectable with monitoring |

#### Reachability

**Score**: 3.5 | **Trust Zone**: Agent Runtime Zone (Trusted)

tool-server-1 sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 3.5.

---

### AG-3 — intake-agent

**Threat**: intake-agent can start further agents or processes on request, so a compromised prompt can multiply its reach beyond the intended scope.

**Category**: agentic | **Original Risk Level**: High | **Composite**: 6.0 (Medium)

#### CVSS 3.1 Base

**Score**: 9.1 | **Vector**: `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:L/A:L`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Network | Reachable over the network |
| Attack Complexity (AC) | Low | No special conditions |
| Privileges Required (PR) | Low | A basic account is needed |
| User Interaction (UI) | None | No user action needed |
| Scope (S) | Changed | Impact crosses a boundary |
| Confidentiality (C) | High | Broad disclosure |
| Integrity (I) | Low | Limited modification |
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

**Score**: 5.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 2 | Manual for each target |
| Target Scope | 6 | A class of targets |
| Resource Requirements | 7 | Minimal resources |
| Detection Difficulty | 5 | Detectable with monitoring |

#### Reachability

**Score**: 3.5 | **Trust Zone**: Agent Runtime Zone (Trusted)

intake-agent sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 3.5.

---

### AG-31 — tool-server-1

**Threat**: The goal or instruction set of tool-server-1 can be changed through content it reads, steering it toward actions its operators never intended.

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

**Score**: 4.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 4 | Described in research |
| Attack Complexity | 3 | Needs chained steps |
| Tooling Availability | 4 | Tools need adaptation |
| Skill Level | 5 | Intermediate skill |

#### Scalability

**Score**: 5.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 2 | Manual for each target |
| Target Scope | 6 | A class of targets |
| Resource Requirements | 7 | Minimal resources |
| Detection Difficulty | 7 | Blends with normal use |

#### Reachability

**Score**: 2.5 | **Trust Zone**: Agent Runtime Zone (Trusted)

tool-server-1 sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 2.5.

---

### LLM-26 — summarizer-llm

**Threat**: Anyone who can write to the ingestion path of summarizer-llm can slip in documents that contradict authoritative sources.

**Category**: llm | **Original Risk Level**: High | **Composite**: 6.0 (Medium)

#### CVSS 3.1 Base

**Score**: 6.9 | **Vector**: `CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:C/C:L/I:H/A:N`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Network | Reachable over the network |
| Attack Complexity (AC) | High | Needs specific conditions |
| Privileges Required (PR) | None | No privileges needed |
| User Interaction (UI) | Required | A user must act |
| Scope (S) | Changed | Impact crosses a boundary |
| Confidentiality (C) | Low | Limited disclosure |
| Integrity (I) | High | Broad modification |
| Availability (A) | None | No loss of service |

#### Exploitability

**Score**: 6.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 6 | Described in research |
| Attack Complexity | 6 | Needs some preparation |
| Tooling Availability | 6 | Tools need adaptation |
| Skill Level | 6 | Intermediate skill |

#### Scalability

**Score**: 7.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 7 | Fully automatable |
| Target Scope | 8 | Every instance |
| Resource Requirements | 10 | Minimal resources |
| Detection Difficulty | 5 | Detectable with monitoring |

#### Reachability

**Score**: 3.5 | **Trust Zone**: Agent Runtime Zone (Trusted)

summarizer-llm sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 3.5.

---

### LLM-55 — model-gateway

**Threat**: model-gateway passes conversation history from earlier turns into the model unchanged, so an injection planted earlier keeps working in later turns.

**Category**: llm | **Original Risk Level**: Medium | **Composite**: 6.0 (Medium)

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

**Score**: 8.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 9 | Documented and widely used |
| Attack Complexity | 8 | A single step suffices |
| Tooling Availability | 5 | Tools need adaptation |
| Skill Level | 10 | Little skill needed |

#### Scalability

**Score**: 7.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 7 | Fully automatable |
| Target Scope | 8 | Every instance |
| Resource Requirements | 8 | Minimal resources |
| Detection Difficulty | 5 | Detectable with monitoring |

#### Reachability

**Score**: 2.0 | **Trust Zone**: Agent Runtime Zone (Trusted)

model-gateway sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 2.0.

---

### LLM-56 — embed-service-2

**Threat**: Model weights or adapters served by embed-service-2 are readable by operators and by any process sharing the host.

**Category**: llm | **Original Risk Level**: Critical | **Composite**: 6.0 (Medium)

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

**Score**: 8.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 8 | Documented and widely used |
| Attack Complexity | 9 | A single step suffices |
| Tooling Availability | 8 | Common tools apply |
| Skill Level | 7 | Little skill needed |

#### Scalability

**Score**: 7.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 6 | Partly automatable |
| Target Scope | 8 | Every instance |
| Resource Requirements | 9 | Minimal resources |
| Detection Difficulty | 7 | Blends with normal use |

#### Reachability

**Score**: 1.5 | **Trust Zone**: Agent Runtime Zone (Trusted)

embed-service-2 sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 1.5.

---

### OI-5 — intake-agent

**Threat**: Model output from intake-agent is inserted into a rendered page without encoding, so crafted output executes script in an operator's browser.

**Category**: llm | **Original Risk Level**: Medium | **Composite**: 6.0 (Medium)

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

**Score**: 8.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 9 | Documented and widely used |
| Attack Complexity | 9 | A single step suffices |
| Tooling Availability | 6 | Tools need adaptation |
| Skill Level | 10 | Little skill needed |

#### Scalability

**Score**: 6.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 5 | Partly automatable |
| Target Scope | 5 | A class of targets |
| Resource Requirements | 7 | Minimal resources |
| Detection Difficulty | 7 | Blends with normal use |

#### Reachability

**Score**: 2.0 | **Trust Zone**: Agent Runtime Zone (Trusted)

intake-agent sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 2.0.

---

### MI-6 — worker-3

**Threat**: Outputs from worker-3 flow into decisions without a review step, so one wrong answer is repeated across many shipments.

**Category**: llm | **Original Risk Level**: High | **Composite**: 6.0 (Medium)

#### CVSS 3.1 Base

**Score**: 7.4 | **Vector**: `CVSS:3.1/AV:A/AC:L/PR:N/UI:R/S:C/C:L/I:H/A:N`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Adjacent | Needs an adjacent network |
| Attack Complexity (AC) | Low | No special conditions |
| Privileges Required (PR) | None | No privileges needed |
| User Interaction (UI) | Required | A user must act |
| Scope (S) | Changed | Impact crosses a boundary |
| Confidentiality (C) | Low | Limited disclosure |
| Integrity (I) | High | Broad modification |
| Availability (A) | None | No loss of service |

#### Exploitability

**Score**: 7.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 6 | Described in research |
| Attack Complexity | 8 | A single step suffices |
| Tooling Availability | 6 | Tools need adaptation |
| Skill Level | 8 | Little skill needed |

#### Scalability

**Score**: 7.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 8 | Fully automatable |
| Target Scope | 5 | A class of targets |
| Resource Requirements | 8 | Minimal resources |
| Detection Difficulty | 7 | Blends with normal use |

#### Reachability

**Score**: 1.5 | **Trust Zone**: Agent Runtime Zone (Trusted)

worker-3 sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 1.5.

---

### MI-17 — eval-runner

**Threat**: Outputs from eval-runner flow into decisions without a review step, so one wrong answer is repeated across many shipments.

**Category**: llm | **Original Risk Level**: High | **Composite**: 6.0 (Medium)

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
| Known Techniques | 7 | Documented and widely used |
| Attack Complexity | 7 | A single step suffices |
| Tooling Availability | 7 | Common tools apply |
| Skill Level | 7 | Little skill needed |

#### Scalability

**Score**: 6.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 5 | Partly automatable |
| Target Scope | 8 | Every instance |
| Resource Requirements | 7 | Minimal resources |
| Detection Difficulty | 6 | Detectable with monitoring |

#### Reachability

**Score**: 2.0 | **Trust Zone**: Operations Zone (Trusted)

eval-runner sits in the Operations Zone. The zone baseline is 2.5 and the refinement for this finding gives 2.0.

---

### TE-11 — reviewer-agent

**Threat**: reviewer-agent adopts a persona that presents itself as a named colleague, so operators trust its suggestions more than its accuracy warrants.

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
| Attack Complexity | 5 | Needs some preparation |
| Tooling Availability | 2 | Needs custom tooling |
| Skill Level | 5 | Intermediate skill |

#### Scalability

**Score**: 5.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 4 | Partly automatable |
| Target Scope | 6 | A class of targets |
| Resource Requirements | 6 | Moderate resources |
| Detection Difficulty | 6 | Detectable with monitoring |

#### Reachability

**Score**: 2.0 | **Trust Zone**: Agent Runtime Zone (Trusted)

reviewer-agent sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 2.0.

---

### S-8 — planner-agent

**Threat**: An unauthenticated callback or health route on planner-agent accepts requests that downstream code treats as if they had come from trace-collector.

**Category**: spoofing | **Original Risk Level**: Critical | **Composite**: 5.9 (Medium)

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

**Score**: 7.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 8 | Documented and widely used |
| Attack Complexity | 7 | A single step suffices |
| Tooling Availability | 8 | Common tools apply |
| Skill Level | 5 | Intermediate skill |

#### Scalability

**Score**: 5.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 8 | Fully automatable |
| Target Scope | 5 | A class of targets |
| Resource Requirements | 6 | Moderate resources |
| Detection Difficulty | 3 | Readily detected |

#### Reachability

**Score**: 2.5 | **Trust Zone**: Agent Runtime Zone (Trusted)

planner-agent sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 2.5.

---

### S-24 — embed-service-2

**Threat**: A compromised peer presents a forged service identity to embed-service-2, and embed-service-2 accepts the claim without verifying the signature chain back to the issuing authority.

**Category**: spoofing | **Original Risk Level**: High | **Composite**: 5.9 (Medium)

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

**Score**: 6.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 8 | Documented and widely used |
| Attack Complexity | 6 | Needs some preparation |
| Tooling Availability | 6 | Tools need adaptation |
| Skill Level | 6 | Intermediate skill |

#### Scalability

**Score**: 6.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 6 | Partly automatable |
| Target Scope | 6 | A class of targets |
| Resource Requirements | 6 | Moderate resources |
| Detection Difficulty | 6 | Detectable with monitoring |

#### Reachability

**Score**: 3.0 | **Trust Zone**: Agent Runtime Zone (Trusted)

embed-service-2 sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 3.0.

---

### S-39 — policy-engine

**Threat**: A compromised peer presents a forged service identity to policy-engine, and policy-engine accepts the claim without verifying the signature chain back to the issuing authority.

**Category**: spoofing | **Original Risk Level**: Critical | **Composite**: 5.9 (Medium)

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

**Score**: 6.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 5 | Described in research |
| Attack Complexity | 8 | A single step suffices |
| Tooling Availability | 6 | Tools need adaptation |
| Skill Level | 7 | Little skill needed |

#### Scalability

**Score**: 6.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 9 | Fully automatable |
| Target Scope | 4 | A class of targets |
| Resource Requirements | 7 | Minimal resources |
| Detection Difficulty | 4 | Detectable with monitoring |

#### Reachability

**Score**: 3.0 | **Trust Zone**: Operations Zone (Trusted)

policy-engine sits in the Operations Zone. The zone baseline is 2.5 and the refinement for this finding gives 3.0.

---

### T-26 — memory-store

**Threat**: Unsanitised task history and operator preferences reach memory-store and are processed as trusted structure, so crafted input changes how later steps interpret the record.

**Category**: tampering | **Original Risk Level**: Medium | **Composite**: 5.9 (Medium)

#### CVSS 3.1 Base

**Score**: 8.2 | **Vector**: `CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:C/C:N/I:H/A:H`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Network | Reachable over the network |
| Attack Complexity (AC) | High | Needs specific conditions |
| Privileges Required (PR) | Low | A basic account is needed |
| User Interaction (UI) | None | No user action needed |
| Scope (S) | Changed | Impact crosses a boundary |
| Confidentiality (C) | None | No disclosure |
| Integrity (I) | High | Broad modification |
| Availability (A) | High | Loss of service |

#### Exploitability

**Score**: 5.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 6 | Described in research |
| Attack Complexity | 6 | Needs some preparation |
| Tooling Availability | 5 | Tools need adaptation |
| Skill Level | 5 | Intermediate skill |

#### Scalability

**Score**: 4.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 6 | Partly automatable |
| Target Scope | 3 | One specific target |
| Resource Requirements | 7 | Minimal resources |
| Detection Difficulty | 2 | Readily detected |

#### Reachability

**Score**: 3.5 | **Trust Zone**: Data Zone (Trusted)

memory-store sits in the Data Zone. The zone baseline is 2.5 and the refinement for this finding gives 3.5.

---

### R-5 — edge-gateway

**Threat**: Clock drift between edge-gateway and client-portal leaves events in inconsistent order, so the sequence of actions on inbound API requests cannot be reconstructed reliably.

**Category**: repudiation | **Original Risk Level**: Low | **Composite**: 5.9 (Medium)

#### CVSS 3.1 Base

**Score**: 5.0 | **Vector**: `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:N/I:L/A:N`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Network | Reachable over the network |
| Attack Complexity (AC) | Low | No special conditions |
| Privileges Required (PR) | Low | A basic account is needed |
| User Interaction (UI) | None | No user action needed |
| Scope (S) | Changed | Impact crosses a boundary |
| Confidentiality (C) | None | No disclosure |
| Integrity (I) | Low | Limited modification |
| Availability (A) | None | No loss of service |

#### Exploitability

**Score**: 5.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 5 | Described in research |
| Attack Complexity | 6 | Needs some preparation |
| Tooling Availability | 4 | Tools need adaptation |
| Skill Level | 7 | Little skill needed |

#### Scalability

**Score**: 7.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 5 | Partly automatable |
| Target Scope | 6 | A class of targets |
| Resource Requirements | 9 | Minimal resources |
| Detection Difficulty | 10 | Blends with normal use |

#### Reachability

**Score**: 7.0 | **Trust Zone**: Edge DMZ (Semi-trusted)

edge-gateway sits in the Edge DMZ. The zone baseline is 6.5 and the refinement for this finding gives 7.0.

---

### I-9 — planner-agent

**Threat**: Cross-tenant filters on planner-agent are applied in application code only, so one missing predicate exposes another tenant's task plans and tool selections.

**Category**: info-disclosure | **Original Risk Level**: Medium | **Composite**: 5.9 (Medium)

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

**Score**: 6.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 7 | Documented and widely used |
| Attack Complexity | 6 | Needs some preparation |
| Tooling Availability | 6 | Tools need adaptation |
| Skill Level | 5 | Intermediate skill |

#### Scalability

**Score**: 6.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 8 | Fully automatable |
| Target Scope | 4 | A class of targets |
| Resource Requirements | 9 | Minimal resources |
| Detection Difficulty | 5 | Detectable with monitoring |

#### Reachability

**Score**: 3.0 | **Trust Zone**: Agent Runtime Zone (Trusted)

planner-agent sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 3.0.

---

### I-34 — queue-a2

**Threat**: Data in transit between scheduler-1 and queue-a2 is protected only on the outer hop, which leaves task and result messages readable on the internal segment after termination.

**Category**: info-disclosure | **Original Risk Level**: High | **Composite**: 5.9 (Medium)

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

**Score**: 7.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 7 | Documented and widely used |
| Attack Complexity | 8 | A single step suffices |
| Tooling Availability | 5 | Tools need adaptation |
| Skill Level | 8 | Little skill needed |

#### Scalability

**Score**: 7.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 7 | Fully automatable |
| Target Scope | 7 | Every instance |
| Resource Requirements | 9 | Minimal resources |
| Detection Difficulty | 5 | Detectable with monitoring |

#### Reachability

**Score**: 2.5 | **Trust Zone**: Agent Runtime Zone (Trusted)

queue-a2 sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 2.5.

---

### D-26 — s3-archive

**Threat**: Retry storms from trace-collector multiply the load on s3-archive when it slows down, turning a brief delay into a sustained outage.

**Category**: denial-of-service | **Original Risk Level**: Low | **Composite**: 5.9 (Medium)

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
| Known Techniques | 8 | Documented and widely used |
| Attack Complexity | 6 | Needs some preparation |
| Tooling Availability | 6 | Tools need adaptation |
| Skill Level | 8 | Little skill needed |

#### Scalability

**Score**: 6.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 10 | Fully automatable |
| Target Scope | 6 | A class of targets |
| Resource Requirements | 6 | Moderate resources |
| Detection Difficulty | 2 | Readily detected |

#### Reachability

**Score**: 1.5 | **Trust Zone**: Data Zone (Trusted)

s3-archive sits in the Data Zone. The zone baseline is 2.5 and the refinement for this finding gives 1.5.

---

### D-29 — scheduler-1

**Threat**: Retry storms from queue-a2 multiply the load on scheduler-1 when it slows down, turning a brief delay into a sustained outage.

**Category**: denial-of-service | **Original Risk Level**: Medium | **Composite**: 5.9 (Medium)

#### CVSS 3.1 Base

**Score**: 7.1 | **Vector**: `CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:L/A:H`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Network | Reachable over the network |
| Attack Complexity (AC) | Low | No special conditions |
| Privileges Required (PR) | None | No privileges needed |
| User Interaction (UI) | Required | A user must act |
| Scope (S) | Unchanged | Impact stays in the component |
| Confidentiality (C) | None | No disclosure |
| Integrity (I) | Low | Limited modification |
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

**Score**: 5.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 8 | Fully automatable |
| Target Scope | 8 | Every instance |
| Resource Requirements | 3 | Needs heavy infrastructure |
| Detection Difficulty | 3 | Readily detected |

#### Reachability

**Score**: 3.0 | **Trust Zone**: Agent Runtime Zone (Trusted)

scheduler-1 sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 3.0.

---

### D-32 — trace-collector

**Threat**: Expensive queries over prompts, completions and tool traces can be triggered by any authorised caller of trace-collector, so one user can degrade the service for all.

**Category**: denial-of-service | **Original Risk Level**: Low | **Composite**: 5.9 (Medium)

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

**Score**: 8.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 9 | Documented and widely used |
| Attack Complexity | 9 | A single step suffices |
| Tooling Availability | 8 | Common tools apply |
| Skill Level | 8 | Little skill needed |

#### Scalability

**Score**: 5.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 7 | Fully automatable |
| Target Scope | 8 | Every instance |
| Resource Requirements | 3 | Needs heavy infrastructure |
| Detection Difficulty | 2 | Readily detected |

#### Reachability

**Score**: 1.5 | **Trust Zone**: Operations Zone (Trusted)

trace-collector sits in the Operations Zone. The zone baseline is 2.5 and the refinement for this finding gives 1.5.

---

### D-33 — eval-runner

**Threat**: A dependency of eval-runner becomes unavailable and the failure cascades because eval-runner waits on it synchronously for every request.

**Category**: denial-of-service | **Original Risk Level**: High | **Composite**: 5.9 (Medium)

#### CVSS 3.1 Base

**Score**: 6.5 | **Vector**: `CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:L`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Network | Reachable over the network |
| Attack Complexity (AC) | Low | No special conditions |
| Privileges Required (PR) | None | No privileges needed |
| User Interaction (UI) | None | No user action needed |
| Scope (S) | Unchanged | Impact stays in the component |
| Confidentiality (C) | Low | Limited disclosure |
| Integrity (I) | None | No modification |
| Availability (A) | Low | Degraded service |

#### Exploitability

**Score**: 8.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 7 | Documented and widely used |
| Attack Complexity | 9 | A single step suffices |
| Tooling Availability | 6 | Tools need adaptation |
| Skill Level | 10 | Little skill needed |

#### Scalability

**Score**: 5.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 7 | Fully automatable |
| Target Scope | 6 | A class of targets |
| Resource Requirements | 4 | Moderate resources |
| Detection Difficulty | 3 | Readily detected |

#### Reachability

**Score**: 2.5 | **Trust Zone**: Operations Zone (Trusted)

eval-runner sits in the Operations Zone. The zone baseline is 2.5 and the refinement for this finding gives 2.5.

---

### E-25 — summarizer-llm

**Threat**: An administrative interface of summarizer-llm is reachable from the same network as ordinary callers and relies on a single shared password.

**Category**: privilege-escalation | **Original Risk Level**: High | **Composite**: 5.9 (Medium)

#### CVSS 3.1 Base

**Score**: 8.2 | **Vector**: `CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:C/C:H/I:L/A:L`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Network | Reachable over the network |
| Attack Complexity (AC) | Low | No special conditions |
| Privileges Required (PR) | High | Administrative rights are needed |
| User Interaction (UI) | None | No user action needed |
| Scope (S) | Changed | Impact crosses a boundary |
| Confidentiality (C) | High | Broad disclosure |
| Integrity (I) | Low | Limited modification |
| Availability (A) | Low | Degraded service |

#### Exploitability

**Score**: 5.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 5 | Described in research |
| Attack Complexity | 6 | Needs some preparation |
| Tooling Availability | 6 | Tools need adaptation |
| Skill Level | 5 | Intermediate skill |

#### Scalability

**Score**: 6.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 7 | Fully automatable |
| Target Scope | 6 | A class of targets |
| Resource Requirements | 7 | Minimal resources |
| Detection Difficulty | 6 | Detectable with monitoring |

#### Reachability

**Score**: 2.0 | **Trust Zone**: Agent Runtime Zone (Trusted)

summarizer-llm sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 2.0.

---

### AG-29 — tool-server-1

**Threat**: tool-server-1 can start further agents or processes on request, so a compromised prompt can multiply its reach beyond the intended scope.

**Category**: agentic | **Original Risk Level**: Medium | **Composite**: 5.9 (Medium)

#### CVSS 3.1 Base

**Score**: 7.5 | **Vector**: `CVSS:3.1/AV:N/AC:L/PR:H/UI:R/S:C/C:H/I:L/A:L`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Network | Reachable over the network |
| Attack Complexity (AC) | Low | No special conditions |
| Privileges Required (PR) | High | Administrative rights are needed |
| User Interaction (UI) | Required | A user must act |
| Scope (S) | Changed | Impact crosses a boundary |
| Confidentiality (C) | High | Broad disclosure |
| Integrity (I) | Low | Limited modification |
| Availability (A) | Low | Degraded service |

#### Exploitability

**Score**: 6.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 6 | Described in research |
| Attack Complexity | 6 | Needs some preparation |
| Tooling Availability | 5 | Tools need adaptation |
| Skill Level | 7 | Little skill needed |

#### Scalability

**Score**: 6.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 5 | Partly automatable |
| Target Scope | 6 | A class of targets |
| Resource Requirements | 9 | Minimal resources |
| Detection Difficulty | 4 | Detectable with monitoring |

#### Reachability

**Score**: 3.0 | **Trust Zone**: Agent Runtime Zone (Trusted)

tool-server-1 sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 3.0.

---

### AG-30 — tool-server-1

**Threat**: tool-server-1 can act on tool call arguments and results without a human approval step, so a manipulated plan executes high-impact actions with no checkpoint.

**Category**: agentic | **Original Risk Level**: Low | **Composite**: 5.9 (Medium)

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

**Score**: 5.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 7 | Documented and widely used |
| Attack Complexity | 5 | Needs some preparation |
| Tooling Availability | 4 | Tools need adaptation |
| Skill Level | 6 | Intermediate skill |

#### Scalability

**Score**: 5.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 2 | Manual for each target |
| Target Scope | 5 | A class of targets |
| Resource Requirements | 7 | Minimal resources |
| Detection Difficulty | 6 | Detectable with monitoring |

#### Reachability

**Score**: 2.5 | **Trust Zone**: Agent Runtime Zone (Trusted)

tool-server-1 sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 2.5.

---

### AG-37 — queue-a2

**Threat**: queue-a2 does not limit the rate or total number of tool calls per task, so abuse of a costly tool goes unnoticed until the invoice arrives.

**Category**: agentic | **Original Risk Level**: Low | **Composite**: 5.9 (Medium)

#### CVSS 3.1 Base

**Score**: 10.0 | **Vector**: `CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:L/I:H/A:H`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Network | Reachable over the network |
| Attack Complexity (AC) | Low | No special conditions |
| Privileges Required (PR) | None | No privileges needed |
| User Interaction (UI) | None | No user action needed |
| Scope (S) | Changed | Impact crosses a boundary |
| Confidentiality (C) | Low | Limited disclosure |
| Integrity (I) | High | Broad modification |
| Availability (A) | High | Loss of service |

#### Exploitability

**Score**: 4.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 5 | Described in research |
| Attack Complexity | 3 | Needs chained steps |
| Tooling Availability | 3 | Needs custom tooling |
| Skill Level | 5 | Intermediate skill |

#### Scalability

**Score**: 4.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 2 | Manual for each target |
| Target Scope | 3 | One specific target |
| Resource Requirements | 6 | Moderate resources |
| Detection Difficulty | 7 | Blends with normal use |

#### Reachability

**Score**: 2.5 | **Trust Zone**: Agent Runtime Zone (Trusted)

queue-a2 sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 2.5.

---

### AG-43 — queue-a2

**Threat**: Tool calls made by queue-a2 are not tied to the end user, so the tool server cannot tell whose authority a request carries.

**Category**: agentic | **Original Risk Level**: High | **Composite**: 5.9 (Medium)

#### CVSS 3.1 Base

**Score**: 8.4 | **Vector**: `CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:C/C:L/I:H/A:H`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Network | Reachable over the network |
| Attack Complexity (AC) | High | Needs specific conditions |
| Privileges Required (PR) | Low | A basic account is needed |
| User Interaction (UI) | None | No user action needed |
| Scope (S) | Changed | Impact crosses a boundary |
| Confidentiality (C) | Low | Limited disclosure |
| Integrity (I) | High | Broad modification |
| Availability (A) | High | Loss of service |

#### Exploitability

**Score**: 5.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 5 | Described in research |
| Attack Complexity | 6 | Needs some preparation |
| Tooling Availability | 3 | Needs custom tooling |
| Skill Level | 6 | Intermediate skill |

#### Scalability

**Score**: 6.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 3 | Manual for each target |
| Target Scope | 5 | A class of targets |
| Resource Requirements | 8 | Minimal resources |
| Detection Difficulty | 8 | Blends with normal use |

#### Reachability

**Score**: 3.0 | **Trust Zone**: Agent Runtime Zone (Trusted)

queue-a2 sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 3.0.

---

### LLM-20 — model-gateway

**Threat**: Model weights or adapters served by model-gateway are readable by operators and by any process sharing the host.

**Category**: llm | **Original Risk Level**: Critical | **Composite**: 5.9 (Medium)

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
| Known Techniques | 8 | Documented and widely used |
| Attack Complexity | 6 | Needs some preparation |
| Tooling Availability | 6 | Tools need adaptation |
| Skill Level | 8 | Little skill needed |

#### Scalability

**Score**: 6.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 8 | Fully automatable |
| Target Scope | 6 | A class of targets |
| Resource Requirements | 7 | Minimal resources |
| Detection Difficulty | 5 | Detectable with monitoring |

#### Reachability

**Score**: 3.5 | **Trust Zone**: Agent Runtime Zone (Trusted)

model-gateway sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 3.5.

---

### LLM-30 — kb-index

**Threat**: A delayed trigger planted in carrier tariffs and customs rules on kb-index changes behaviour only after a date or phrase, so pre-release testing never sees it.

**Category**: llm | **Original Risk Level**: High | **Composite**: 5.9 (Medium)

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

**Score**: 7.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 8 | Documented and widely used |
| Attack Complexity | 7 | A single step suffices |
| Tooling Availability | 5 | Tools need adaptation |
| Skill Level | 10 | Little skill needed |

#### Scalability

**Score**: 6.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 8 | Fully automatable |
| Target Scope | 5 | A class of targets |
| Resource Requirements | 8 | Minimal resources |
| Detection Difficulty | 5 | Detectable with monitoring |

#### Reachability

**Score**: 2.5 | **Trust Zone**: Data Zone (Trusted)

kb-index sits in the Data Zone. The zone baseline is 2.5 and the refinement for this finding gives 2.5.

---

### OI-17 — worker-2

**Threat**: Text generated by worker-2 is placed into a database query or shell argument without parameterisation, allowing the model to be steered into injection.

**Category**: llm | **Original Risk Level**: Medium | **Composite**: 5.9 (Medium)

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

**Score**: 6.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 7 | Documented and widely used |
| Attack Complexity | 6 | Needs some preparation |
| Tooling Availability | 7 | Common tools apply |
| Skill Level | 6 | Intermediate skill |

#### Scalability

**Score**: 7.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 8 | Fully automatable |
| Target Scope | 6 | A class of targets |
| Resource Requirements | 9 | Minimal resources |
| Detection Difficulty | 7 | Blends with normal use |

#### Reachability

**Score**: 3.5 | **Trust Zone**: Agent Runtime Zone (Trusted)

worker-2 sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 3.5.

---

### OI-24 — summarizer-llm

**Threat**: Markdown or HTML produced by summarizer-llm contains remote images that leak data when a client renders it.

**Category**: llm | **Original Risk Level**: High | **Composite**: 5.9 (Medium)

#### CVSS 3.1 Base

**Score**: 6.9 | **Vector**: `CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:C/C:L/I:H/A:N`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Network | Reachable over the network |
| Attack Complexity (AC) | High | Needs specific conditions |
| Privileges Required (PR) | None | No privileges needed |
| User Interaction (UI) | Required | A user must act |
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
| Tooling Availability | 6 | Tools need adaptation |
| Skill Level | 9 | Little skill needed |

#### Scalability

**Score**: 6.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 5 | Partly automatable |
| Target Scope | 7 | Every instance |
| Resource Requirements | 8 | Minimal resources |
| Detection Difficulty | 6 | Detectable with monitoring |

#### Reachability

**Score**: 2.0 | **Trust Zone**: Agent Runtime Zone (Trusted)

summarizer-llm sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 2.0.

---

### TE-14 — summarizer-llm

**Threat**: summarizer-llm adopts a persona that presents itself as a named colleague, so operators trust its suggestions more than its accuracy warrants.

**Category**: agentic | **Original Risk Level**: Medium | **Composite**: 5.9 (Medium)

#### CVSS 3.1 Base

**Score**: 9.9 | **Vector**: `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:L/I:H/A:H`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Network | Reachable over the network |
| Attack Complexity (AC) | Low | No special conditions |
| Privileges Required (PR) | Low | A basic account is needed |
| User Interaction (UI) | None | No user action needed |
| Scope (S) | Changed | Impact crosses a boundary |
| Confidentiality (C) | Low | Limited disclosure |
| Integrity (I) | High | Broad modification |
| Availability (A) | High | Loss of service |

#### Exploitability

**Score**: 4.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 6 | Described in research |
| Attack Complexity | 4 | Needs some preparation |
| Tooling Availability | 3 | Needs custom tooling |
| Skill Level | 5 | Intermediate skill |

#### Scalability

**Score**: 5.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 4 | Partly automatable |
| Target Scope | 5 | A class of targets |
| Resource Requirements | 8 | Minimal resources |
| Detection Difficulty | 5 | Detectable with monitoring |

#### Reachability

**Score**: 1.5 | **Trust Zone**: Agent Runtime Zone (Trusted)

summarizer-llm sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 1.5.

---

### S-12 — worker-2

**Threat**: A shared or long-lived worker credential on worker-2 lets anyone who obtains one copy authenticate as every tenant that uses the same deployment profile.

**Category**: spoofing | **Original Risk Level**: High | **Composite**: 5.8 (Medium)

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

**Score**: 6.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 8 | Documented and widely used |
| Attack Complexity | 7 | A single step suffices |
| Tooling Availability | 5 | Tools need adaptation |
| Skill Level | 6 | Intermediate skill |

#### Scalability

**Score**: 6.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 7 | Fully automatable |
| Target Scope | 4 | A class of targets |
| Resource Requirements | 6 | Moderate resources |
| Detection Difficulty | 7 | Blends with normal use |

#### Reachability

**Score**: 3.5 | **Trust Zone**: Agent Runtime Zone (Trusted)

worker-2 sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 3.5.

---

### S-16 — worker-3

**Threat**: An attacker replays a captured worker credential against worker-3, which does not bind the credential to the session or channel it was issued for, so the replay is accepted as the original caller.

**Category**: spoofing | **Original Risk Level**: Note | **Composite**: 5.8 (Medium)

#### CVSS 3.1 Base

**Score**: 7.6 | **Vector**: `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:L/A:L`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Network | Reachable over the network |
| Attack Complexity (AC) | Low | No special conditions |
| Privileges Required (PR) | Low | A basic account is needed |
| User Interaction (UI) | None | No user action needed |
| Scope (S) | Unchanged | Impact stays in the component |
| Confidentiality (C) | High | Broad disclosure |
| Integrity (I) | Low | Limited modification |
| Availability (A) | Low | Degraded service |

#### Exploitability

**Score**: 6.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 6 | Described in research |
| Attack Complexity | 8 | A single step suffices |
| Tooling Availability | 6 | Tools need adaptation |
| Skill Level | 6 | Intermediate skill |

#### Scalability

**Score**: 5.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 6 | Partly automatable |
| Target Scope | 4 | A class of targets |
| Resource Requirements | 9 | Minimal resources |
| Detection Difficulty | 3 | Readily detected |

#### Reachability

**Score**: 2.0 | **Trust Zone**: Agent Runtime Zone (Trusted)

worker-3 sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 2.0.

---

### S-22 — model-gateway

**Threat**: An attacker replays a captured model API key against model-gateway, which does not bind the credential to the session or channel it was issued for, so the replay is accepted as the original caller.

**Category**: spoofing | **Original Risk Level**: High | **Composite**: 5.8 (Medium)

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

**Score**: 7.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 8 | Documented and widely used |
| Attack Complexity | 8 | A single step suffices |
| Tooling Availability | 7 | Common tools apply |
| Skill Level | 5 | Intermediate skill |

#### Scalability

**Score**: 6.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 6 | Partly automatable |
| Target Scope | 7 | Every instance |
| Resource Requirements | 6 | Moderate resources |
| Detection Difficulty | 5 | Detectable with monitoring |

#### Reachability

**Score**: 1.5 | **Trust Zone**: Agent Runtime Zone (Trusted)

model-gateway sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 1.5.

---

### S-30 — scheduler-1

**Threat**: An attacker replays a captured scheduler credential against scheduler-1, which does not bind the credential to the session or channel it was issued for, so the replay is accepted as the original caller.

**Category**: spoofing | **Original Risk Level**: Critical | **Composite**: 5.8 (Medium)

#### CVSS 3.1 Base

**Score**: 6.5 | **Vector**: `CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:H/A:N`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Network | Reachable over the network |
| Attack Complexity (AC) | High | Needs specific conditions |
| Privileges Required (PR) | None | No privileges needed |
| User Interaction (UI) | None | No user action needed |
| Scope (S) | Unchanged | Impact stays in the component |
| Confidentiality (C) | Low | Limited disclosure |
| Integrity (I) | High | Broad modification |
| Availability (A) | None | No loss of service |

#### Exploitability

**Score**: 6.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 6 | Described in research |
| Attack Complexity | 8 | A single step suffices |
| Tooling Availability | 8 | Common tools apply |
| Skill Level | 4 | Intermediate skill |

#### Scalability

**Score**: 6.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 6 | Partly automatable |
| Target Scope | 7 | Every instance |
| Resource Requirements | 6 | Moderate resources |
| Detection Difficulty | 5 | Detectable with monitoring |

#### Reachability

**Score**: 3.5 | **Trust Zone**: Agent Runtime Zone (Trusted)

scheduler-1 sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 3.5.

---

### T-32 — feature-store-2

**Threat**: A race between concurrent writers lets an attacker overwrite ranking and fine-tuning features on feature-store-2 after validation but before use, defeating the earlier check.

**Category**: tampering | **Original Risk Level**: High | **Composite**: 5.8 (Medium)

#### CVSS 3.1 Base

**Score**: 8.2 | **Vector**: `CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:H/A:N`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Network | Reachable over the network |
| Attack Complexity (AC) | Low | No special conditions |
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
| Known Techniques | 5 | Described in research |
| Attack Complexity | 4 | Needs some preparation |
| Tooling Availability | 5 | Tools need adaptation |
| Skill Level | 6 | Intermediate skill |

#### Scalability

**Score**: 5.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 4 | Partly automatable |
| Target Scope | 3 | One specific target |
| Resource Requirements | 8 | Minimal resources |
| Detection Difficulty | 5 | Detectable with monitoring |

#### Reachability

**Score**: 3.5 | **Trust Zone**: Data Zone (Trusted)

feature-store-2 sits in the Data Zone. The zone baseline is 2.5 and the refinement for this finding gives 3.5.

---

### T-41 — policy-engine

**Threat**: Backups and exports of guardrail rules and approval decisions on policy-engine are writable by operators without a second approver, so a malicious change survives restores.

**Category**: tampering | **Original Risk Level**: High | **Composite**: 5.8 (Medium)

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

**Score**: 5.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 7 | Documented and widely used |
| Attack Complexity | 4 | Needs some preparation |
| Tooling Availability | 6 | Tools need adaptation |
| Skill Level | 5 | Intermediate skill |

#### Scalability

**Score**: 5.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 6 | Partly automatable |
| Target Scope | 2 | One specific target |
| Resource Requirements | 6 | Moderate resources |
| Detection Difficulty | 6 | Detectable with monitoring |

#### Reachability

**Score**: 2.0 | **Trust Zone**: Operations Zone (Trusted)

policy-engine sits in the Operations Zone. The zone baseline is 2.5 and the refinement for this finding gives 2.0.

---

### R-6 — auth-broker

**Threat**: Delegated actions performed by auth-broker on behalf of a user are recorded under the service identity alone, hiding who authorised them.

**Category**: repudiation | **Original Risk Level**: Low | **Composite**: 5.8 (Medium)

#### CVSS 3.1 Base

**Score**: 4.3 | **Vector**: `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Network | Reachable over the network |
| Attack Complexity (AC) | Low | No special conditions |
| Privileges Required (PR) | Low | A basic account is needed |
| User Interaction (UI) | None | No user action needed |
| Scope (S) | Unchanged | Impact stays in the component |
| Confidentiality (C) | None | No disclosure |
| Integrity (I) | Low | Limited modification |
| Availability (A) | None | No loss of service |

#### Exploitability

**Score**: 6.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 5 | Described in research |
| Attack Complexity | 8 | A single step suffices |
| Tooling Availability | 6 | Tools need adaptation |
| Skill Level | 7 | Little skill needed |

#### Scalability

**Score**: 7.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 6 | Partly automatable |
| Target Scope | 5 | A class of targets |
| Resource Requirements | 10 | Minimal resources |
| Detection Difficulty | 7 | Blends with normal use |

#### Reachability

**Score**: 6.5 | **Trust Zone**: Edge DMZ (Semi-trusted)

auth-broker sits in the Edge DMZ. The zone baseline is 6.5 and the refinement for this finding gives 6.5.

---

### D-30 — scheduler-1

**Threat**: A slow-read attack holds connections to scheduler-1 open and ties up the workers handling recurring planning triggers until none remain for real requests.

**Category**: denial-of-service | **Original Risk Level**: High | **Composite**: 5.8 (Medium)

#### CVSS 3.1 Base

**Score**: 6.8 | **Vector**: `CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:L/I:L/A:H`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Network | Reachable over the network |
| Attack Complexity (AC) | Low | No special conditions |
| Privileges Required (PR) | Low | A basic account is needed |
| User Interaction (UI) | Required | A user must act |
| Scope (S) | Unchanged | Impact stays in the component |
| Confidentiality (C) | Low | Limited disclosure |
| Integrity (I) | Low | Limited modification |
| Availability (A) | High | Loss of service |

#### Exploitability

**Score**: 7.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 8 | Documented and widely used |
| Attack Complexity | 6 | Needs some preparation |
| Tooling Availability | 6 | Tools need adaptation |
| Skill Level | 8 | Little skill needed |

#### Scalability

**Score**: 5.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 8 | Fully automatable |
| Target Scope | 6 | A class of targets |
| Resource Requirements | 5 | Moderate resources |
| Detection Difficulty | 1 | Readily detected |

#### Reachability

**Score**: 3.0 | **Trust Zone**: Agent Runtime Zone (Trusted)

scheduler-1 sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 3.0.

---

### E-13 — worker-2

**Threat**: An administrative interface of worker-2 is reachable from the same network as ordinary callers and relies on a single shared password.

**Category**: privilege-escalation | **Original Risk Level**: Medium | **Composite**: 5.8 (Medium)

#### CVSS 3.1 Base

**Score**: 7.7 | **Vector**: `CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:C/C:L/I:H/A:L`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Network | Reachable over the network |
| Attack Complexity (AC) | High | Needs specific conditions |
| Privileges Required (PR) | Low | A basic account is needed |
| User Interaction (UI) | None | No user action needed |
| Scope (S) | Changed | Impact crosses a boundary |
| Confidentiality (C) | Low | Limited disclosure |
| Integrity (I) | High | Broad modification |
| Availability (A) | Low | Degraded service |

#### Exploitability

**Score**: 5.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 7 | Documented and widely used |
| Attack Complexity | 4 | Needs some preparation |
| Tooling Availability | 6 | Tools need adaptation |
| Skill Level | 3 | Needs deep expertise |

#### Scalability

**Score**: 6.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 7 | Fully automatable |
| Target Scope | 6 | A class of targets |
| Resource Requirements | 8 | Minimal resources |
| Detection Difficulty | 3 | Readily detected |

#### Reachability

**Score**: 3.5 | **Trust Zone**: Agent Runtime Zone (Trusted)

worker-2 sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 3.5.

---

### E-14 — worker-2

**Threat**: worker-2 runs with broader permissions than its function needs, so a flaw in handling work orders and route candidates yields access to unrelated resources.

**Category**: privilege-escalation | **Original Risk Level**: Medium | **Composite**: 5.8 (Medium)

#### CVSS 3.1 Base

**Score**: 8.3 | **Vector**: `CVSS:3.1/AV:A/AC:L/PR:H/UI:N/S:C/C:H/I:H/A:L`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Adjacent | Needs an adjacent network |
| Attack Complexity (AC) | Low | No special conditions |
| Privileges Required (PR) | High | Administrative rights are needed |
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
| Tooling Availability | 5 | Tools need adaptation |
| Skill Level | 5 | Intermediate skill |

#### Scalability

**Score**: 5.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 5 | Partly automatable |
| Target Scope | 5 | A class of targets |
| Resource Requirements | 6 | Moderate resources |
| Detection Difficulty | 4 | Detectable with monitoring |

#### Reachability

**Score**: 3.0 | **Trust Zone**: Agent Runtime Zone (Trusted)

worker-2 sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 3.0.

---

### E-18 — tool-server-1

**Threat**: A confused-deputy path lets a low-privilege caller ask tool-server-1 to act on tool call arguments and results using the privileges of worker-2.

**Category**: privilege-escalation | **Original Risk Level**: Low | **Composite**: 5.8 (Medium)

#### CVSS 3.1 Base

**Score**: 8.8 | **Vector**: `CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Local | Needs local access |
| Attack Complexity (AC) | Low | No special conditions |
| Privileges Required (PR) | Low | A basic account is needed |
| User Interaction (UI) | None | No user action needed |
| Scope (S) | Changed | Impact crosses a boundary |
| Confidentiality (C) | High | Broad disclosure |
| Integrity (I) | High | Broad modification |
| Availability (A) | High | Loss of service |

#### Exploitability

**Score**: 5.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 5 | Described in research |
| Attack Complexity | 4 | Needs some preparation |
| Tooling Availability | 6 | Tools need adaptation |
| Skill Level | 5 | Intermediate skill |

#### Scalability

**Score**: 5.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 7 | Fully automatable |
| Target Scope | 3 | One specific target |
| Resource Requirements | 9 | Minimal resources |
| Detection Difficulty | 3 | Readily detected |

#### Reachability

**Score**: 2.0 | **Trust Zone**: Agent Runtime Zone (Trusted)

tool-server-1 sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 2.0.

---

### AG-41 — intake-agent

**Threat**: intake-agent can act on free-text shipment requests without a human approval step, so a manipulated plan executes high-impact actions with no checkpoint.

**Category**: agentic | **Original Risk Level**: Critical | **Composite**: 5.8 (Medium)

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
| Known Techniques | 7 | Documented and widely used |
| Attack Complexity | 6 | Needs some preparation |
| Tooling Availability | 3 | Needs custom tooling |
| Skill Level | 6 | Intermediate skill |

#### Scalability

**Score**: 5.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 3 | Manual for each target |
| Target Scope | 3 | One specific target |
| Resource Requirements | 9 | Minimal resources |
| Detection Difficulty | 5 | Detectable with monitoring |

#### Reachability

**Score**: 1.5 | **Trust Zone**: Agent Runtime Zone (Trusted)

intake-agent sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 1.5.

---

### OI-13 — planner-agent

**Threat**: Model output from planner-agent is inserted into a rendered page without encoding, so crafted output executes script in an operator's browser.

**Category**: llm | **Original Risk Level**: Medium | **Composite**: 5.8 (Medium)

#### CVSS 3.1 Base

**Score**: 6.3 | **Vector**: `CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:H/I:L/A:N`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Network | Reachable over the network |
| Attack Complexity (AC) | Low | No special conditions |
| Privileges Required (PR) | Low | A basic account is needed |
| User Interaction (UI) | Required | A user must act |
| Scope (S) | Unchanged | Impact stays in the component |
| Confidentiality (C) | High | Broad disclosure |
| Integrity (I) | Low | Limited modification |
| Availability (A) | None | No loss of service |

#### Exploitability

**Score**: 7.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 9 | Documented and widely used |
| Attack Complexity | 8 | A single step suffices |
| Tooling Availability | 5 | Tools need adaptation |
| Skill Level | 6 | Intermediate skill |

#### Scalability

**Score**: 7.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 8 | Fully automatable |
| Target Scope | 5 | A class of targets |
| Resource Requirements | 8 | Minimal resources |
| Detection Difficulty | 7 | Blends with normal use |

#### Reachability

**Score**: 2.0 | **Trust Zone**: Agent Runtime Zone (Trusted)

planner-agent sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 2.0.

---

### OI-27 — model-gateway

**Threat**: Text generated by model-gateway is placed into a database query or shell argument without parameterisation, allowing the model to be steered into injection.

**Category**: llm | **Original Risk Level**: Critical | **Composite**: 5.8 (Medium)

#### CVSS 3.1 Base

**Score**: 7.7 | **Vector**: `CVSS:3.1/AV:N/AC:H/PR:L/UI:R/S:C/C:H/I:H/A:N`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Network | Reachable over the network |
| Attack Complexity (AC) | High | Needs specific conditions |
| Privileges Required (PR) | Low | A basic account is needed |
| User Interaction (UI) | Required | A user must act |
| Scope (S) | Changed | Impact crosses a boundary |
| Confidentiality (C) | High | Broad disclosure |
| Integrity (I) | High | Broad modification |
| Availability (A) | None | No loss of service |

#### Exploitability

**Score**: 6.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 8 | Documented and widely used |
| Attack Complexity | 6 | Needs some preparation |
| Tooling Availability | 6 | Tools need adaptation |
| Skill Level | 6 | Intermediate skill |

#### Scalability

**Score**: 6.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 5 | Partly automatable |
| Target Scope | 5 | A class of targets |
| Resource Requirements | 7 | Minimal resources |
| Detection Difficulty | 7 | Blends with normal use |

#### Reachability

**Score**: 1.5 | **Trust Zone**: Agent Runtime Zone (Trusted)

model-gateway sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 1.5.

---

### MI-14 — summarizer-llm

**Threat**: Outputs from summarizer-llm flow into decisions without a review step, so one wrong answer is repeated across many shipments.

**Category**: llm | **Original Risk Level**: Medium | **Composite**: 5.8 (Medium)

#### CVSS 3.1 Base

**Score**: 5.8 | **Vector**: `CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:C/C:L/I:L/A:L`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Network | Reachable over the network |
| Attack Complexity (AC) | High | Needs specific conditions |
| Privileges Required (PR) | None | No privileges needed |
| User Interaction (UI) | Required | A user must act |
| Scope (S) | Changed | Impact crosses a boundary |
| Confidentiality (C) | Low | Limited disclosure |
| Integrity (I) | Low | Limited modification |
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

**Score**: 7.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 5 | Partly automatable |
| Target Scope | 6 | A class of targets |
| Resource Requirements | 10 | Minimal resources |
| Detection Difficulty | 7 | Blends with normal use |

#### Reachability

**Score**: 3.0 | **Trust Zone**: Agent Runtime Zone (Trusted)

summarizer-llm sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 3.0.

---

### TE-15 — summarizer-llm

**Threat**: Persuasive phrasing from summarizer-llm pushes operators to approve proposals quickly, which reduces careful review.

**Category**: agentic | **Original Risk Level**: Low | **Composite**: 5.8 (Medium)

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

**Score**: 4.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 5 | Described in research |
| Attack Complexity | 5 | Needs some preparation |
| Tooling Availability | 3 | Needs custom tooling |
| Skill Level | 5 | Intermediate skill |

#### Scalability

**Score**: 6.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 2 | Manual for each target |
| Target Scope | 5 | A class of targets |
| Resource Requirements | 9 | Minimal resources |
| Detection Difficulty | 8 | Blends with normal use |

#### Reachability

**Score**: 2.5 | **Trust Zone**: Agent Runtime Zone (Trusted)

summarizer-llm sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 2.5.

---

### S-11 — router-agent

**Threat**: An unauthenticated callback or health route on router-agent accepts requests that downstream code treats as if they had come from worker-3.

**Category**: spoofing | **Original Risk Level**: Note | **Composite**: 5.7 (Medium)

#### CVSS 3.1 Base

**Score**: 6.8 | **Vector**: `CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:H/I:L/A:L`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Network | Reachable over the network |
| Attack Complexity (AC) | Low | No special conditions |
| Privileges Required (PR) | Low | A basic account is needed |
| User Interaction (UI) | Required | A user must act |
| Scope (S) | Unchanged | Impact stays in the component |
| Confidentiality (C) | High | Broad disclosure |
| Integrity (I) | Low | Limited modification |
| Availability (A) | Low | Degraded service |

#### Exploitability

**Score**: 6.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 8 | Documented and widely used |
| Attack Complexity | 6 | Needs some preparation |
| Tooling Availability | 6 | Tools need adaptation |
| Skill Level | 6 | Intermediate skill |

#### Scalability

**Score**: 7.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 9 | Fully automatable |
| Target Scope | 6 | A class of targets |
| Resource Requirements | 9 | Minimal resources |
| Detection Difficulty | 4 | Detectable with monitoring |

#### Reachability

**Score**: 1.5 | **Trust Zone**: Agent Runtime Zone (Trusted)

router-agent sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 1.5.

---

### S-21 — tool-server-1

**Threat**: Certificate or DNS spoofing between audit-ledger and tool-server-1 lets an attacker terminate the connection and present a lookalike endpoint when pinning is absent.

**Category**: spoofing | **Original Risk Level**: High | **Composite**: 5.7 (Medium)

#### CVSS 3.1 Base

**Score**: 6.4 | **Vector**: `CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:L/A:L`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Network | Reachable over the network |
| Attack Complexity (AC) | High | Needs specific conditions |
| Privileges Required (PR) | None | No privileges needed |
| User Interaction (UI) | Required | A user must act |
| Scope (S) | Unchanged | Impact stays in the component |
| Confidentiality (C) | High | Broad disclosure |
| Integrity (I) | Low | Limited modification |
| Availability (A) | Low | Degraded service |

#### Exploitability

**Score**: 6.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 8 | Documented and widely used |
| Attack Complexity | 6 | Needs some preparation |
| Tooling Availability | 5 | Tools need adaptation |
| Skill Level | 5 | Intermediate skill |

#### Scalability

**Score**: 7.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 9 | Fully automatable |
| Target Scope | 7 | Every instance |
| Resource Requirements | 7 | Minimal resources |
| Detection Difficulty | 7 | Blends with normal use |

#### Reachability

**Score**: 2.5 | **Trust Zone**: Agent Runtime Zone (Trusted)

tool-server-1 sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 2.5.

---

### R-7 — auth-broker

**Threat**: Failed and rejected attempts against auth-broker are not logged, so probing of credential assertions and session grants leaves no trace that an investigator could use.

**Category**: repudiation | **Original Risk Level**: Medium | **Composite**: 5.7 (Medium)

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

**Score**: 7.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 6 | Described in research |
| Attack Complexity | 8 | A single step suffices |
| Tooling Availability | 6 | Tools need adaptation |
| Skill Level | 8 | Little skill needed |

#### Scalability

**Score**: 6.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 4 | Partly automatable |
| Target Scope | 3 | One specific target |
| Resource Requirements | 10 | Minimal resources |
| Detection Difficulty | 9 | Blends with normal use |

#### Reachability

**Score**: 6.5 | **Trust Zone**: Edge DMZ (Semi-trusted)

auth-broker sits in the Edge DMZ. The zone baseline is 6.5 and the refinement for this finding gives 6.5.

---

### R-23 — queue-a2

**Threat**: Failed and rejected attempts against queue-a2 are not logged, so probing of task and result messages leaves no trace that an investigator could use.

**Category**: repudiation | **Original Risk Level**: Medium | **Composite**: 5.7 (Medium)

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

**Score**: 4.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 4 | Described in research |
| Attack Complexity | 4 | Needs some preparation |
| Tooling Availability | 4 | Tools need adaptation |
| Skill Level | 6 | Intermediate skill |

#### Scalability

**Score**: 4.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 2 | Manual for each target |
| Target Scope | 1 | One specific target |
| Resource Requirements | 8 | Minimal resources |
| Detection Difficulty | 7 | Blends with normal use |

#### Reachability

**Score**: 3.5 | **Trust Zone**: Agent Runtime Zone (Trusted)

queue-a2 sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 3.5.

---

### I-47 — policy-engine

**Threat**: Data in transit between audit-ledger and policy-engine is protected only on the outer hop, which leaves guardrail rules and approval decisions readable on the internal segment after termination.

**Category**: info-disclosure | **Original Risk Level**: High | **Composite**: 5.7 (Medium)

#### CVSS 3.1 Base

**Score**: 7.2 | **Vector**: `CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:L/I:N/A:L`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Network | Reachable over the network |
| Attack Complexity (AC) | Low | No special conditions |
| Privileges Required (PR) | None | No privileges needed |
| User Interaction (UI) | None | No user action needed |
| Scope (S) | Changed | Impact crosses a boundary |
| Confidentiality (C) | Low | Limited disclosure |
| Integrity (I) | None | No modification |
| Availability (A) | Low | Degraded service |

#### Exploitability

**Score**: 5.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 5 | Described in research |
| Attack Complexity | 5 | Needs some preparation |
| Tooling Availability | 4 | Tools need adaptation |
| Skill Level | 6 | Intermediate skill |

#### Scalability

**Score**: 6.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 8 | Fully automatable |
| Target Scope | 7 | Every instance |
| Resource Requirements | 7 | Minimal resources |
| Detection Difficulty | 4 | Detectable with monitoring |

#### Reachability

**Score**: 3.5 | **Trust Zone**: Operations Zone (Trusted)

policy-engine sits in the Operations Zone. The zone baseline is 2.5 and the refinement for this finding gives 3.5.

---

### D-13 — reviewer-agent

**Threat**: Expensive queries over drafted proposals awaiting review can be triggered by any authorised caller of reviewer-agent, so one user can degrade the service for all.

**Category**: denial-of-service | **Original Risk Level**: Medium | **Composite**: 5.7 (Medium)

#### CVSS 3.1 Base

**Score**: 6.3 | **Vector**: `CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:L/I:N/A:H`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Network | Reachable over the network |
| Attack Complexity (AC) | Low | No special conditions |
| Privileges Required (PR) | Low | A basic account is needed |
| User Interaction (UI) | Required | A user must act |
| Scope (S) | Unchanged | Impact stays in the component |
| Confidentiality (C) | Low | Limited disclosure |
| Integrity (I) | None | No modification |
| Availability (A) | High | Loss of service |

#### Exploitability

**Score**: 6.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 7 | Documented and widely used |
| Attack Complexity | 6 | Needs some preparation |
| Tooling Availability | 7 | Common tools apply |
| Skill Level | 6 | Intermediate skill |

#### Scalability

**Score**: 5.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 9 | Fully automatable |
| Target Scope | 7 | Every instance |
| Resource Requirements | 3 | Needs heavy infrastructure |
| Detection Difficulty | 3 | Readily detected |

#### Reachability

**Score**: 3.5 | **Trust Zone**: Agent Runtime Zone (Trusted)

reviewer-agent sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 3.5.

---

### D-18 — model-gateway

**Threat**: Unbounded growth of stored prompts and completions on model-gateway fills its volume, after which writes fail for every other consumer.

**Category**: denial-of-service | **Original Risk Level**: Medium | **Composite**: 5.7 (Medium)

#### CVSS 3.1 Base

**Score**: 5.7 | **Vector**: `CVSS:3.1/AV:A/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Adjacent | Needs an adjacent network |
| Attack Complexity (AC) | Low | No special conditions |
| Privileges Required (PR) | None | No privileges needed |
| User Interaction (UI) | Required | A user must act |
| Scope (S) | Unchanged | Impact stays in the component |
| Confidentiality (C) | None | No disclosure |
| Integrity (I) | None | No modification |
| Availability (A) | High | Loss of service |

#### Exploitability

**Score**: 7.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 9 | Documented and widely used |
| Attack Complexity | 8 | A single step suffices |
| Tooling Availability | 6 | Tools need adaptation |
| Skill Level | 7 | Little skill needed |

#### Scalability

**Score**: 6.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 8 | Fully automatable |
| Target Scope | 9 | Every instance |
| Resource Requirements | 6 | Moderate resources |
| Detection Difficulty | 1 | Readily detected |

#### Reachability

**Score**: 3.0 | **Trust Zone**: Agent Runtime Zone (Trusted)

model-gateway sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 3.0.

---

### D-24 — kb-index

**Threat**: A dependency of kb-index becomes unavailable and the failure cascades because kb-index waits on it synchronously for every request.

**Category**: denial-of-service | **Original Risk Level**: Low | **Composite**: 5.7 (Medium)

#### CVSS 3.1 Base

**Score**: 5.9 | **Vector**: `CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:L/I:N/A:H`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Network | Reachable over the network |
| Attack Complexity (AC) | High | Needs specific conditions |
| Privileges Required (PR) | None | No privileges needed |
| User Interaction (UI) | Required | A user must act |
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

**Score**: 6.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 10 | Fully automatable |
| Target Scope | 8 | Every instance |
| Resource Requirements | 4 | Moderate resources |
| Detection Difficulty | 4 | Detectable with monitoring |

#### Reachability

**Score**: 3.0 | **Trust Zone**: Data Zone (Trusted)

kb-index sits in the Data Zone. The zone baseline is 2.5 and the refinement for this finding gives 3.0.

---

### D-28 — queue-a2

**Threat**: A burst of requests exhausts the connection pool of queue-a2, which queues work without a bound and blocks legitimate use of task and result messages.

**Category**: denial-of-service | **Original Risk Level**: High | **Composite**: 5.7 (Medium)

**Correlation Group**: Scores inherited from primary finding R-23 (CG-17). Dimensional detail is recorded on the primary.

**Score**: 8.6 | **Vector**: `CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:H/A:L`

---

### D-39 — queue-a2

**Threat**: A single oversized or deeply nested payload makes queue-a2 spend disproportionate memory and CPU parsing task and result messages.

**Category**: denial-of-service | **Original Risk Level**: Medium | **Composite**: 5.7 (Medium)

**Correlation Group**: Scores inherited from primary finding R-23 (CG-17). Dimensional detail is recorded on the primary.

**Score**: 8.6 | **Vector**: `CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:H/A:L`

---

### E-26 — queue-a2

**Threat**: A privileged maintenance task of queue-a2 can be triggered through a queue message that any producer on the bus may publish.

**Category**: privilege-escalation | **Original Risk Level**: High | **Composite**: 5.7 (Medium)

**Correlation Group**: Scores inherited from primary finding R-23 (CG-17). Dimensional detail is recorded on the primary.

**Score**: 8.6 | **Vector**: `CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:H/A:L`

---

### E-33 — queue-a2

**Threat**: Object identifiers in requests to queue-a2 are trusted without an ownership check, so a caller can read or change task and result messages that belong to others.

**Category**: privilege-escalation | **Original Risk Level**: High | **Composite**: 5.7 (Medium)

**Correlation Group**: Scores inherited from primary finding R-23 (CG-17). Dimensional detail is recorded on the primary.

**Score**: 8.6 | **Vector**: `CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:H/A:L`

---

### AG-23 — worker-3

**Threat**: An attacker chains two individually safe tools through worker-3 to reach an outcome neither was approved for, such as an export followed by an upload.

**Category**: agentic | **Original Risk Level**: High | **Composite**: 5.7 (Medium)

#### CVSS 3.1 Base

**Score**: 7.7 | **Vector**: `CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:C/C:H/I:L/A:L`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Network | Reachable over the network |
| Attack Complexity (AC) | High | Needs specific conditions |
| Privileges Required (PR) | Low | A basic account is needed |
| User Interaction (UI) | None | No user action needed |
| Scope (S) | Changed | Impact crosses a boundary |
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

**Score**: 6.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 4 | Partly automatable |
| Target Scope | 5 | A class of targets |
| Resource Requirements | 9 | Minimal resources |
| Detection Difficulty | 6 | Detectable with monitoring |

#### Reachability

**Score**: 2.5 | **Trust Zone**: Agent Runtime Zone (Trusted)

worker-3 sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 2.5.

---

### AG-28 — tool-server-1

**Threat**: tool-server-1 retries failed actions on its own, repeating side effects such as bookings or messages when the first attempt partly succeeded.

**Category**: agentic | **Original Risk Level**: Low | **Composite**: 5.7 (Medium)

#### CVSS 3.1 Base

**Score**: 9.6 | **Vector**: `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:N`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Network | Reachable over the network |
| Attack Complexity (AC) | Low | No special conditions |
| Privileges Required (PR) | Low | A basic account is needed |
| User Interaction (UI) | None | No user action needed |
| Scope (S) | Changed | Impact crosses a boundary |
| Confidentiality (C) | High | Broad disclosure |
| Integrity (I) | High | Broad modification |
| Availability (A) | None | No loss of service |

#### Exploitability

**Score**: 4.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 4 | Described in research |
| Attack Complexity | 4 | Needs some preparation |
| Tooling Availability | 4 | Tools need adaptation |
| Skill Level | 4 | Intermediate skill |

#### Scalability

**Score**: 5.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 3 | Manual for each target |
| Target Scope | 3 | One specific target |
| Resource Requirements | 9 | Minimal resources |
| Detection Difficulty | 5 | Detectable with monitoring |

#### Reachability

**Score**: 2.0 | **Trust Zone**: Agent Runtime Zone (Trusted)

tool-server-1 sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 2.0.

---

### AG-35 — queue-a2

**Threat**: queue-a2 can start further agents or processes on request, so a compromised prompt can multiply its reach beyond the intended scope.

**Category**: agentic | **Original Risk Level**: High | **Composite**: 5.7 (Medium)

**Correlation Group**: Scores inherited from primary finding R-23 (CG-17). Dimensional detail is recorded on the primary.

**Score**: 8.6 | **Vector**: `CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:H/A:L`

---

### AG-36 — queue-a2

**Threat**: An attacker chains two individually safe tools through queue-a2 to reach an outcome neither was approved for, such as an export followed by an upload.

**Category**: agentic | **Original Risk Level**: Critical | **Composite**: 5.7 (Medium)

**Correlation Group**: Scores inherited from primary finding R-23 (CG-17). Dimensional detail is recorded on the primary.

**Score**: 8.6 | **Vector**: `CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:H/A:L`

---

### LLM-49 — eval-runner

**Threat**: A delayed trigger planted in replayed traces and judge verdicts on eval-runner changes behaviour only after a date or phrase, so pre-release testing never sees it.

**Category**: llm | **Original Risk Level**: Low | **Composite**: 5.7 (Medium)

#### CVSS 3.1 Base

**Score**: 5.4 | **Vector**: `CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Network | Reachable over the network |
| Attack Complexity (AC) | Low | No special conditions |
| Privileges Required (PR) | Low | A basic account is needed |
| User Interaction (UI) | Required | A user must act |
| Scope (S) | Changed | Impact crosses a boundary |
| Confidentiality (C) | Low | Limited disclosure |
| Integrity (I) | Low | Limited modification |
| Availability (A) | None | No loss of service |

#### Exploitability

**Score**: 7.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 6 | Described in research |
| Attack Complexity | 6 | Needs some preparation |
| Tooling Availability | 8 | Common tools apply |
| Skill Level | 10 | Little skill needed |

#### Scalability

**Score**: 6.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 6 | Partly automatable |
| Target Scope | 6 | A class of targets |
| Resource Requirements | 9 | Minimal resources |
| Detection Difficulty | 5 | Detectable with monitoring |

#### Reachability

**Score**: 3.0 | **Trust Zone**: Operations Zone (Trusted)

eval-runner sits in the Operations Zone. The zone baseline is 2.5 and the refinement for this finding gives 3.0.

---

### OI-19 — model-gateway

**Threat**: File paths or names produced by model-gateway are used to write files, letting crafted output reach locations outside the intended directory.

**Category**: llm | **Original Risk Level**: High | **Composite**: 5.7 (Medium)

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

**Score**: 7.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 9 | Documented and widely used |
| Attack Complexity | 8 | A single step suffices |
| Tooling Availability | 6 | Tools need adaptation |
| Skill Level | 7 | Little skill needed |

#### Scalability

**Score**: 6.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 5 | Partly automatable |
| Target Scope | 6 | A class of targets |
| Resource Requirements | 10 | Minimal resources |
| Detection Difficulty | 5 | Detectable with monitoring |

#### Reachability

**Score**: 1.5 | **Trust Zone**: Agent Runtime Zone (Trusted)

model-gateway sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 1.5.

---

### TE-13 — summarizer-llm

**Threat**: summarizer-llm speaks with an authoritative tone about customs and legal matters, and operators may defer to it without checking.

**Category**: agentic | **Original Risk Level**: High | **Composite**: 5.7 (Medium)

#### CVSS 3.1 Base

**Score**: 8.2 | **Vector**: `CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:C/C:L/I:H/A:L`

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

**Score**: 5.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 5 | Described in research |
| Attack Complexity | 4 | Needs some preparation |
| Tooling Availability | 5 | Tools need adaptation |
| Skill Level | 6 | Intermediate skill |

#### Scalability

**Score**: 5.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 3 | Manual for each target |
| Target Scope | 6 | A class of targets |
| Resource Requirements | 6 | Moderate resources |
| Detection Difficulty | 5 | Detectable with monitoring |

#### Reachability

**Score**: 3.0 | **Trust Zone**: Agent Runtime Zone (Trusted)

summarizer-llm sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 3.0.

---

### T-23 — kb-index

**Threat**: A race between concurrent writers lets an attacker overwrite carrier tariffs and customs rules on kb-index after validation but before use, defeating the earlier check.

**Category**: tampering | **Original Risk Level**: Low | **Composite**: 5.6 (Medium)

#### CVSS 3.1 Base

**Score**: 8.3 | **Vector**: `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:H/A:H`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Network | Reachable over the network |
| Attack Complexity (AC) | Low | No special conditions |
| Privileges Required (PR) | Low | A basic account is needed |
| User Interaction (UI) | None | No user action needed |
| Scope (S) | Unchanged | Impact stays in the component |
| Confidentiality (C) | Low | Limited disclosure |
| Integrity (I) | High | Broad modification |
| Availability (A) | High | Loss of service |

#### Exploitability

**Score**: 5.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 6 | Described in research |
| Attack Complexity | 4 | Needs some preparation |
| Tooling Availability | 6 | Tools need adaptation |
| Skill Level | 6 | Intermediate skill |

#### Scalability

**Score**: 5.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 5 | Partly automatable |
| Target Scope | 4 | A class of targets |
| Resource Requirements | 7 | Minimal resources |
| Detection Difficulty | 4 | Detectable with monitoring |

#### Reachability

**Score**: 1.5 | **Trust Zone**: Data Zone (Trusted)

kb-index sits in the Data Zone. The zone baseline is 2.5 and the refinement for this finding gives 1.5.

---

### I-25 — vector-store-a

**Threat**: embedded documents and metadata held by vector-store-a are readable by any service in the Data Zone that shares the same network role, because access is granted by network position.

**Category**: info-disclosure | **Original Risk Level**: Note | **Composite**: 5.6 (Medium)

#### CVSS 3.1 Base

**Score**: 5.7 | **Vector**: `CVSS:3.1/AV:A/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:N`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Adjacent | Needs an adjacent network |
| Attack Complexity (AC) | Low | No special conditions |
| Privileges Required (PR) | None | No privileges needed |
| User Interaction (UI) | Required | A user must act |
| Scope (S) | Unchanged | Impact stays in the component |
| Confidentiality (C) | High | Broad disclosure |
| Integrity (I) | None | No modification |
| Availability (A) | None | No loss of service |

#### Exploitability

**Score**: 7.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 7 | Documented and widely used |
| Attack Complexity | 7 | A single step suffices |
| Tooling Availability | 7 | Common tools apply |
| Skill Level | 7 | Little skill needed |

#### Scalability

**Score**: 5.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 6 | Partly automatable |
| Target Scope | 5 | A class of targets |
| Resource Requirements | 7 | Minimal resources |
| Detection Difficulty | 4 | Detectable with monitoring |

#### Reachability

**Score**: 3.5 | **Trust Zone**: Data Zone (Trusted)

vector-store-a sits in the Data Zone. The zone baseline is 2.5 and the refinement for this finding gives 3.5.

---

### I-28 — kb-index

**Threat**: Logs and traces emitted by kb-index include raw carrier tariffs and customs rules, so anyone with access to the logging pipeline can read content meant for one tenant.

**Category**: info-disclosure | **Original Risk Level**: Medium | **Composite**: 5.6 (Medium)

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
| Scriptability | 5 | Partly automatable |
| Target Scope | 6 | A class of targets |
| Resource Requirements | 7 | Minimal resources |
| Detection Difficulty | 4 | Detectable with monitoring |

#### Reachability

**Score**: 2.0 | **Trust Zone**: Data Zone (Trusted)

kb-index sits in the Data Zone. The zone baseline is 2.5 and the refinement for this finding gives 2.0.

---

### D-23 — vector-store-a

**Threat**: Retry storms from embed-service-2 multiply the load on vector-store-a when it slows down, turning a brief delay into a sustained outage.

**Category**: denial-of-service | **Original Risk Level**: Note | **Composite**: 5.6 (Medium)

#### CVSS 3.1 Base

**Score**: 6.5 | **Vector**: `CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Network | Reachable over the network |
| Attack Complexity (AC) | Low | No special conditions |
| Privileges Required (PR) | None | No privileges needed |
| User Interaction (UI) | Required | A user must act |
| Scope (S) | Unchanged | Impact stays in the component |
| Confidentiality (C) | None | No disclosure |
| Integrity (I) | None | No modification |
| Availability (A) | High | Loss of service |

#### Exploitability

**Score**: 7.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 7 | Documented and widely used |
| Attack Complexity | 7 | A single step suffices |
| Tooling Availability | 5 | Tools need adaptation |
| Skill Level | 9 | Little skill needed |

#### Scalability

**Score**: 5.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 8 | Fully automatable |
| Target Scope | 7 | Every instance |
| Resource Requirements | 3 | Needs heavy infrastructure |
| Detection Difficulty | 2 | Readily detected |

#### Reachability

**Score**: 2.5 | **Trust Zone**: Data Zone (Trusted)

vector-store-a sits in the Data Zone. The zone baseline is 2.5 and the refinement for this finding gives 2.5.

---

### AG-6 — planner-agent

**Threat**: Memory written by planner-agent is trusted on later runs, so one poisoned entry changes the behaviour of every future task.

**Category**: agentic | **Original Risk Level**: High | **Composite**: 5.6 (Medium)

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

**Score**: 4.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 5 | Described in research |
| Attack Complexity | 3 | Needs chained steps |
| Tooling Availability | 3 | Needs custom tooling |
| Skill Level | 7 | Little skill needed |

#### Scalability

**Score**: 5.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 4 | Partly automatable |
| Target Scope | 4 | A class of targets |
| Resource Requirements | 8 | Minimal resources |
| Detection Difficulty | 4 | Detectable with monitoring |

#### Reachability

**Score**: 3.0 | **Trust Zone**: Agent Runtime Zone (Trusted)

planner-agent sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 3.0.

---

### AG-9 — planner-agent

**Threat**: Tool calls made by planner-agent are not tied to the end user, so the tool server cannot tell whose authority a request carries.

**Category**: agentic | **Original Risk Level**: Critical | **Composite**: 5.6 (Medium)

#### CVSS 3.1 Base

**Score**: 8.2 | **Vector**: `CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:H/I:L/A:L`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Network | Reachable over the network |
| Attack Complexity (AC) | Low | No special conditions |
| Privileges Required (PR) | Low | A basic account is needed |
| User Interaction (UI) | Required | A user must act |
| Scope (S) | Changed | Impact crosses a boundary |
| Confidentiality (C) | High | Broad disclosure |
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

**Score**: 4.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 3 | Manual for each target |
| Target Scope | 3 | One specific target |
| Resource Requirements | 8 | Minimal resources |
| Detection Difficulty | 4 | Detectable with monitoring |

#### Reachability

**Score**: 2.0 | **Trust Zone**: Agent Runtime Zone (Trusted)

planner-agent sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 2.0.

---

### AG-10 — planner-agent

**Threat**: planner-agent invokes tools with arguments assembled from model output, so an attacker who shapes the output can call a tool with parameters the designer never allowed.

**Category**: agentic | **Original Risk Level**: High | **Composite**: 5.6 (Medium)

#### CVSS 3.1 Base

**Score**: 8.2 | **Vector**: `CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:H/A:L`

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

**Score**: 4.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 5 | Described in research |
| Attack Complexity | 6 | Needs some preparation |
| Tooling Availability | 2 | Needs custom tooling |
| Skill Level | 3 | Needs deep expertise |

#### Scalability

**Score**: 6.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 4 | Partly automatable |
| Target Scope | 6 | A class of targets |
| Resource Requirements | 9 | Minimal resources |
| Detection Difficulty | 7 | Blends with normal use |

#### Reachability

**Score**: 3.0 | **Trust Zone**: Agent Runtime Zone (Trusted)

planner-agent sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 3.0.

---

### AG-14 — router-agent

**Threat**: router-agent does not limit the rate or total number of tool calls per task, so abuse of a costly tool goes unnoticed until the invoice arrives.

**Category**: agentic | **Original Risk Level**: Medium | **Composite**: 5.6 (Medium)

#### CVSS 3.1 Base

**Score**: 7.7 | **Vector**: `CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:L`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Network | Reachable over the network |
| Attack Complexity (AC) | High | Needs specific conditions |
| Privileges Required (PR) | None | No privileges needed |
| User Interaction (UI) | None | No user action needed |
| Scope (S) | Unchanged | Impact stays in the component |
| Confidentiality (C) | High | Broad disclosure |
| Integrity (I) | High | Broad modification |
| Availability (A) | Low | Degraded service |

#### Exploitability

**Score**: 4.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 5 | Described in research |
| Attack Complexity | 4 | Needs some preparation |
| Tooling Availability | 2 | Needs custom tooling |
| Skill Level | 7 | Little skill needed |

#### Scalability

**Score**: 6.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 3 | Manual for each target |
| Target Scope | 6 | A class of targets |
| Resource Requirements | 8 | Minimal resources |
| Detection Difficulty | 7 | Blends with normal use |

#### Reachability

**Score**: 3.5 | **Trust Zone**: Agent Runtime Zone (Trusted)

router-agent sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 3.5.

---

### AG-17 — worker-2

**Threat**: worker-2 can act on work orders and route candidates without a human approval step, so a manipulated plan executes high-impact actions with no checkpoint.

**Category**: agentic | **Original Risk Level**: Medium | **Composite**: 5.6 (Medium)

#### CVSS 3.1 Base

**Score**: 8.2 | **Vector**: `CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:H/A:L`

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

**Score**: 4.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 5 | Described in research |
| Attack Complexity | 5 | Needs some preparation |
| Tooling Availability | 2 | Needs custom tooling |
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

**Score**: 3.5 | **Trust Zone**: Agent Runtime Zone (Trusted)

worker-2 sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 3.5.

---

### LLM-29 — kb-index

**Threat**: Evaluation labels consumed from kb-index are produced by a judge model that can itself be influenced by planted traces.

**Category**: llm | **Original Risk Level**: Critical | **Composite**: 5.6 (Medium)

**Correlation Group**: Scores inherited from primary finding T-23 (CG-13). Dimensional detail is recorded on the primary.

**Score**: 8.3 | **Vector**: `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:H/A:H`

---

### TE-8 — reviewer-agent

**Threat**: reviewer-agent builds rapport over long sessions and starts to share unprompted details about earlier operators.

**Category**: agentic | **Original Risk Level**: Medium | **Composite**: 5.6 (Medium)

#### CVSS 3.1 Base

**Score**: 8.1 | **Vector**: `CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:C/C:H/I:H/A:L`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Local | Needs local access |
| Attack Complexity (AC) | Low | No special conditions |
| Privileges Required (PR) | High | Administrative rights are needed |
| User Interaction (UI) | None | No user action needed |
| Scope (S) | Changed | Impact crosses a boundary |
| Confidentiality (C) | High | Broad disclosure |
| Integrity (I) | High | Broad modification |
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

**Score**: 5.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 4 | Partly automatable |
| Target Scope | 3 | One specific target |
| Resource Requirements | 7 | Minimal resources |
| Detection Difficulty | 6 | Detectable with monitoring |

#### Reachability

**Score**: 2.0 | **Trust Zone**: Agent Runtime Zone (Trusted)

reviewer-agent sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 2.0.

---

### S-20 — tool-server-1

**Threat**: Session fixation against tool-server-1 lets an attacker pre-seed an identifier and reuse the session after the victim authenticates.

**Category**: spoofing | **Original Risk Level**: Medium | **Composite**: 5.5 (Medium)

#### CVSS 3.1 Base

**Score**: 5.9 | **Vector**: `CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:L/A:N`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Network | Reachable over the network |
| Attack Complexity (AC) | High | Needs specific conditions |
| Privileges Required (PR) | Low | A basic account is needed |
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
| Attack Complexity | 6 | Needs some preparation |
| Tooling Availability | 8 | Common tools apply |
| Skill Level | 6 | Intermediate skill |

#### Scalability

**Score**: 6.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 8 | Fully automatable |
| Target Scope | 5 | A class of targets |
| Resource Requirements | 9 | Minimal resources |
| Detection Difficulty | 4 | Detectable with monitoring |

#### Reachability

**Score**: 2.0 | **Trust Zone**: Agent Runtime Zone (Trusted)

tool-server-1 sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 2.0.

---

### S-43 — model-gateway

**Threat**: A compromised peer presents a forged service identity to model-gateway, and model-gateway accepts the claim without verifying the signature chain back to the issuing authority.

**Category**: spoofing | **Original Risk Level**: Medium | **Composite**: 5.5 (Medium)

#### CVSS 3.1 Base

**Score**: 5.8 | **Vector**: `CVSS:3.1/AV:L/AC:H/PR:N/UI:R/S:U/C:H/I:L/A:L`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Local | Needs local access |
| Attack Complexity (AC) | High | Needs specific conditions |
| Privileges Required (PR) | None | No privileges needed |
| User Interaction (UI) | Required | A user must act |
| Scope (S) | Unchanged | Impact stays in the component |
| Confidentiality (C) | High | Broad disclosure |
| Integrity (I) | Low | Limited modification |
| Availability (A) | Low | Degraded service |

#### Exploitability

**Score**: 7.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 6 | Described in research |
| Attack Complexity | 8 | A single step suffices |
| Tooling Availability | 7 | Common tools apply |
| Skill Level | 7 | Little skill needed |

#### Scalability

**Score**: 7.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 9 | Fully automatable |
| Target Scope | 4 | A class of targets |
| Resource Requirements | 9 | Minimal resources |
| Detection Difficulty | 6 | Detectable with monitoring |

#### Reachability

**Score**: 1.5 | **Trust Zone**: Agent Runtime Zone (Trusted)

model-gateway sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 1.5.

---

### T-19 — summarizer-llm

**Threat**: An attacker who can write to the channel between feature-store-2 and summarizer-llm modifies shipment records fed into summaries in transit because messages carry no integrity protection of their own.

**Category**: tampering | **Original Risk Level**: Medium | **Composite**: 5.5 (Medium)

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

**Score**: 5.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 7 | Documented and widely used |
| Attack Complexity | 7 | A single step suffices |
| Tooling Availability | 5 | Tools need adaptation |
| Skill Level | 3 | Needs deep expertise |

#### Scalability

**Score**: 4.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 4 | Partly automatable |
| Target Scope | 3 | One specific target |
| Resource Requirements | 7 | Minimal resources |
| Detection Difficulty | 4 | Detectable with monitoring |

#### Reachability

**Score**: 3.5 | **Trust Zone**: Agent Runtime Zone (Trusted)

summarizer-llm sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 3.5.

---

### T-35 — scheduler-1

**Threat**: Configuration of scheduler-1 can be rewritten by any service that holds the shared deployment credential, silently changing how recurring planning triggers are handled.

**Category**: tampering | **Original Risk Level**: Medium | **Composite**: 5.5 (Medium)

#### CVSS 3.1 Base

**Score**: 8.1 | **Vector**: `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:H`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Network | Reachable over the network |
| Attack Complexity (AC) | Low | No special conditions |
| Privileges Required (PR) | Low | A basic account is needed |
| User Interaction (UI) | None | No user action needed |
| Scope (S) | Unchanged | Impact stays in the component |
| Confidentiality (C) | None | No disclosure |
| Integrity (I) | High | Broad modification |
| Availability (A) | High | Loss of service |

#### Exploitability

**Score**: 5.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 6 | Described in research |
| Attack Complexity | 6 | Needs some preparation |
| Tooling Availability | 5 | Tools need adaptation |
| Skill Level | 5 | Intermediate skill |

#### Scalability

**Score**: 5.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 5 | Partly automatable |
| Target Scope | 4 | A class of targets |
| Resource Requirements | 6 | Moderate resources |
| Detection Difficulty | 5 | Detectable with monitoring |

#### Reachability

**Score**: 1.5 | **Trust Zone**: Agent Runtime Zone (Trusted)

scheduler-1 sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 1.5.

---

### I-10 — router-agent

**Threat**: A timing or size difference in the responses of router-agent lets an observer infer whether specific records of subtask assignments exist.

**Category**: info-disclosure | **Original Risk Level**: Medium | **Composite**: 5.5 (Medium)

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

**Score**: 6.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 5 | Described in research |
| Attack Complexity | 6 | Needs some preparation |
| Tooling Availability | 7 | Common tools apply |
| Skill Level | 6 | Intermediate skill |

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

router-agent sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 1.5.

---

### I-31 — s3-archive

**Threat**: Data in transit between trace-collector and s3-archive is protected only on the outer hop, which leaves archived transcripts and training corpora readable on the internal segment after termination.

**Category**: info-disclosure | **Original Risk Level**: Critical | **Composite**: 5.5 (Medium)

#### CVSS 3.1 Base

**Score**: 6.5 | **Vector**: `CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:L`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Network | Reachable over the network |
| Attack Complexity (AC) | Low | No special conditions |
| Privileges Required (PR) | None | No privileges needed |
| User Interaction (UI) | None | No user action needed |
| Scope (S) | Unchanged | Impact stays in the component |
| Confidentiality (C) | Low | Limited disclosure |
| Integrity (I) | None | No modification |
| Availability (A) | Low | Degraded service |

#### Exploitability

**Score**: 6.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 5 | Described in research |
| Attack Complexity | 8 | A single step suffices |
| Tooling Availability | 6 | Tools need adaptation |
| Skill Level | 5 | Intermediate skill |

#### Scalability

**Score**: 6.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 6 | Partly automatable |
| Target Scope | 7 | Every instance |
| Resource Requirements | 6 | Moderate resources |
| Detection Difficulty | 5 | Detectable with monitoring |

#### Reachability

**Score**: 2.5 | **Trust Zone**: Data Zone (Trusted)

s3-archive sits in the Data Zone. The zone baseline is 2.5 and the refinement for this finding gives 2.5.

---

### I-42 — audit-ledger

**Threat**: Logs and traces emitted by audit-ledger include raw approval and tool call records, so anyone with access to the logging pipeline can read content meant for one tenant.

**Category**: info-disclosure | **Original Risk Level**: High | **Composite**: 5.5 (Medium)

#### CVSS 3.1 Base

**Score**: 6.1 | **Vector**: `CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:L/A:N`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Local | Needs local access |
| Attack Complexity (AC) | Low | No special conditions |
| Privileges Required (PR) | Low | A basic account is needed |
| User Interaction (UI) | None | No user action needed |
| Scope (S) | Unchanged | Impact stays in the component |
| Confidentiality (C) | High | Broad disclosure |
| Integrity (I) | Low | Limited modification |
| Availability (A) | None | No loss of service |

#### Exploitability

**Score**: 6.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 6 | Described in research |
| Attack Complexity | 8 | A single step suffices |
| Tooling Availability | 5 | Tools need adaptation |
| Skill Level | 5 | Intermediate skill |

#### Scalability

**Score**: 7.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 7 | Fully automatable |
| Target Scope | 6 | A class of targets |
| Resource Requirements | 9 | Minimal resources |
| Detection Difficulty | 6 | Detectable with monitoring |

#### Reachability

**Score**: 2.5 | **Trust Zone**: Operations Zone (Trusted)

audit-ledger sits in the Operations Zone. The zone baseline is 2.5 and the refinement for this finding gives 2.5.

---

### E-21 — model-gateway

**Threat**: Role claims carried in the model API key presented to model-gateway are honoured without confirmation against the authoritative directory.

**Category**: privilege-escalation | **Original Risk Level**: Medium | **Composite**: 5.5 (Medium)

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

**Score**: 5.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 4 | Described in research |
| Attack Complexity | 6 | Needs some preparation |
| Tooling Availability | 4 | Tools need adaptation |
| Skill Level | 6 | Intermediate skill |

#### Scalability

**Score**: 5.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 5 | Partly automatable |
| Target Scope | 3 | One specific target |
| Resource Requirements | 8 | Minimal resources |
| Detection Difficulty | 4 | Detectable with monitoring |

#### Reachability

**Score**: 1.5 | **Trust Zone**: Agent Runtime Zone (Trusted)

model-gateway sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 1.5.

---

### E-31 — policy-engine

**Threat**: Multi-tenant separation in policy-engine depends on a request header that clients can set, allowing one tenant to act in another's scope.

**Category**: privilege-escalation | **Original Risk Level**: High | **Composite**: 5.5 (Medium)

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

**Score**: 4.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 4 | Described in research |
| Attack Complexity | 5 | Needs some preparation |
| Tooling Availability | 4 | Tools need adaptation |
| Skill Level | 5 | Intermediate skill |

#### Scalability

**Score**: 4.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 4 | Partly automatable |
| Target Scope | 4 | A class of targets |
| Resource Requirements | 6 | Moderate resources |
| Detection Difficulty | 4 | Detectable with monitoring |

#### Reachability

**Score**: 2.5 | **Trust Zone**: Operations Zone (Trusted)

policy-engine sits in the Operations Zone. The zone baseline is 2.5 and the refinement for this finding gives 2.5.

---

### AG-21 — worker-3

**Threat**: The goal or instruction set of worker-3 can be changed through content it reads, steering it toward actions its operators never intended.

**Category**: agentic | **Original Risk Level**: Critical | **Composite**: 5.5 (Medium)

#### CVSS 3.1 Base

**Score**: 8.2 | **Vector**: `CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:C/C:L/I:H/A:L`

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

**Score**: 5.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 5 | Described in research |
| Attack Complexity | 5 | Needs some preparation |
| Tooling Availability | 3 | Needs custom tooling |
| Skill Level | 7 | Little skill needed |

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

worker-3 sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 2.0.

---

### AG-42 — tool-server-1

**Threat**: Memory written by tool-server-1 is trusted on later runs, so one poisoned entry changes the behaviour of every future task.

**Category**: agentic | **Original Risk Level**: High | **Composite**: 5.5 (Medium)

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

**Score**: 4.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 7 | Documented and widely used |
| Attack Complexity | 4 | Needs some preparation |
| Tooling Availability | 2 | Needs custom tooling |
| Skill Level | 5 | Intermediate skill |

#### Scalability

**Score**: 4.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 3 | Manual for each target |
| Target Scope | 3 | One specific target |
| Resource Requirements | 6 | Moderate resources |
| Detection Difficulty | 4 | Detectable with monitoring |

#### Reachability

**Score**: 3.0 | **Trust Zone**: Agent Runtime Zone (Trusted)

tool-server-1 sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 3.0.

---

### LLM-23 — embed-service-2

**Threat**: Systematic queries against embed-service-2 let an attacker approximate the behaviour of the model and train a copy.

**Category**: llm | **Original Risk Level**: Critical | **Composite**: 5.5 (Medium)

#### CVSS 3.1 Base

**Score**: 5.4 | **Vector**: `CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Network | Reachable over the network |
| Attack Complexity (AC) | Low | No special conditions |
| Privileges Required (PR) | Low | A basic account is needed |
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

**Score**: 7.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 7 | Fully automatable |
| Target Scope | 8 | Every instance |
| Resource Requirements | 10 | Minimal resources |
| Detection Difficulty | 5 | Detectable with monitoring |

#### Reachability

**Score**: 2.0 | **Trust Zone**: Agent Runtime Zone (Trusted)

embed-service-2 sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 2.0.

---

### TE-2 — intake-agent

**Threat**: Persuasive phrasing from intake-agent pushes operators to approve proposals quickly, which reduces careful review.

**Category**: agentic | **Original Risk Level**: Critical | **Composite**: 5.5 (Medium)

#### CVSS 3.1 Base

**Score**: 9.2 | **Vector**: `CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:L`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Local | Needs local access |
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
| Known Techniques | 5 | Described in research |
| Attack Complexity | 6 | Needs some preparation |
| Tooling Availability | 2 | Needs custom tooling |
| Skill Level | 3 | Needs deep expertise |

#### Scalability

**Score**: 5.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 3 | Manual for each target |
| Target Scope | 4 | A class of targets |
| Resource Requirements | 7 | Minimal resources |
| Detection Difficulty | 6 | Detectable with monitoring |

#### Reachability

**Score**: 1.5 | **Trust Zone**: Agent Runtime Zone (Trusted)

intake-agent sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 1.5.

---

### S-14 — worker-3

**Threat**: Certificate or DNS spoofing between trace-collector and worker-3 lets an attacker terminate the connection and present a lookalike endpoint when pinning is absent.

**Category**: spoofing | **Original Risk Level**: Medium | **Composite**: 5.4 (Medium)

#### CVSS 3.1 Base

**Score**: 5.9 | **Vector**: `CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Network | Reachable over the network |
| Attack Complexity (AC) | High | Needs specific conditions |
| Privileges Required (PR) | None | No privileges needed |
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
| Attack Complexity | 5 | Needs some preparation |
| Tooling Availability | 5 | Tools need adaptation |
| Skill Level | 8 | Little skill needed |

#### Scalability

**Score**: 6.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 7 | Fully automatable |
| Target Scope | 6 | A class of targets |
| Resource Requirements | 7 | Minimal resources |
| Detection Difficulty | 6 | Detectable with monitoring |

#### Reachability

**Score**: 2.0 | **Trust Zone**: Agent Runtime Zone (Trusted)

worker-3 sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 2.0.

---

### S-25 — embed-service-2

**Threat**: A shared or long-lived service credential on embed-service-2 lets anyone who obtains one copy authenticate as every tenant that uses the same deployment profile.

**Category**: spoofing | **Original Risk Level**: Critical | **Composite**: 5.4 (Medium)

#### CVSS 3.1 Base

**Score**: 6.3 | **Vector**: `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:L`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Network | Reachable over the network |
| Attack Complexity (AC) | Low | No special conditions |
| Privileges Required (PR) | Low | A basic account is needed |
| User Interaction (UI) | None | No user action needed |
| Scope (S) | Unchanged | Impact stays in the component |
| Confidentiality (C) | Low | Limited disclosure |
| Integrity (I) | Low | Limited modification |
| Availability (A) | Low | Degraded service |

#### Exploitability

**Score**: 6.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 5 | Described in research |
| Attack Complexity | 7 | A single step suffices |
| Tooling Availability | 6 | Tools need adaptation |
| Skill Level | 8 | Little skill needed |

#### Scalability

**Score**: 6.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 7 | Fully automatable |
| Target Scope | 6 | A class of targets |
| Resource Requirements | 8 | Minimal resources |
| Detection Difficulty | 5 | Detectable with monitoring |

#### Reachability

**Score**: 1.5 | **Trust Zone**: Agent Runtime Zone (Trusted)

embed-service-2 sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 1.5.

---

### S-38 — policy-engine

**Threat**: An attacker replays a captured policy token against policy-engine, which does not bind the credential to the session or channel it was issued for, so the replay is accepted as the original caller.

**Category**: spoofing | **Original Risk Level**: High | **Composite**: 5.4 (Medium)

#### CVSS 3.1 Base

**Score**: 6.5 | **Vector**: `CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:C/C:L/I:L/A:L`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Network | Reachable over the network |
| Attack Complexity (AC) | High | Needs specific conditions |
| Privileges Required (PR) | None | No privileges needed |
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
| Attack Complexity | 5 | Needs some preparation |
| Tooling Availability | 7 | Common tools apply |
| Skill Level | 5 | Intermediate skill |

#### Scalability

**Score**: 6.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 9 | Fully automatable |
| Target Scope | 7 | Every instance |
| Resource Requirements | 6 | Moderate resources |
| Detection Difficulty | 4 | Detectable with monitoring |

#### Reachability

**Score**: 2.5 | **Trust Zone**: Operations Zone (Trusted)

policy-engine sits in the Operations Zone. The zone baseline is 2.5 and the refinement for this finding gives 2.5.

---

### T-7 — reviewer-agent

**Threat**: An attacker who can write to the channel between summarizer-llm and reviewer-agent modifies drafted proposals awaiting review in transit because messages carry no integrity protection of their own.

**Category**: tampering | **Original Risk Level**: High | **Composite**: 5.4 (Medium)

#### CVSS 3.1 Base

**Score**: 6.5 | **Vector**: `CVSS:3.1/AV:N/AC:H/PR:L/UI:R/S:C/C:N/I:H/A:L`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Network | Reachable over the network |
| Attack Complexity (AC) | High | Needs specific conditions |
| Privileges Required (PR) | Low | A basic account is needed |
| User Interaction (UI) | Required | A user must act |
| Scope (S) | Changed | Impact crosses a boundary |
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
| Target Scope | 2 | One specific target |
| Resource Requirements | 8 | Minimal resources |
| Detection Difficulty | 3 | Readily detected |

#### Reachability

**Score**: 3.5 | **Trust Zone**: Agent Runtime Zone (Trusted)

reviewer-agent sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 3.5.

---

### T-8 — reviewer-agent

**Threat**: An update to reviewer-agent is pulled without provenance checks, so a poisoned package can alter how drafted proposals awaiting review are handled at run time.

**Category**: tampering | **Original Risk Level**: Low | **Composite**: 5.4 (Medium)

#### CVSS 3.1 Base

**Score**: 8.5 | **Vector**: `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:N/I:H/A:L`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Network | Reachable over the network |
| Attack Complexity (AC) | Low | No special conditions |
| Privileges Required (PR) | Low | A basic account is needed |
| User Interaction (UI) | None | No user action needed |
| Scope (S) | Changed | Impact crosses a boundary |
| Confidentiality (C) | None | No disclosure |
| Integrity (I) | High | Broad modification |
| Availability (A) | Low | Degraded service |

#### Exploitability

**Score**: 4.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 5 | Described in research |
| Attack Complexity | 6 | Needs some preparation |
| Tooling Availability | 3 | Needs custom tooling |
| Skill Level | 4 | Intermediate skill |

#### Scalability

**Score**: 4.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 3 | Manual for each target |
| Target Scope | 4 | A class of targets |
| Resource Requirements | 5 | Moderate resources |
| Detection Difficulty | 4 | Detectable with monitoring |

#### Reachability

**Score**: 2.5 | **Trust Zone**: Agent Runtime Zone (Trusted)

reviewer-agent sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 2.5.

---

### T-24 — memory-store

**Threat**: Serialised objects arriving from planner-agent are deserialised by memory-store with permissive type handling, allowing crafted payloads to instantiate unintended behaviour.

**Category**: tampering | **Original Risk Level**: Medium | **Composite**: 5.4 (Medium)

#### CVSS 3.1 Base

**Score**: 6.5 | **Vector**: `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Network | Reachable over the network |
| Attack Complexity (AC) | Low | No special conditions |
| Privileges Required (PR) | Low | A basic account is needed |
| User Interaction (UI) | None | No user action needed |
| Scope (S) | Unchanged | Impact stays in the component |
| Confidentiality (C) | None | No disclosure |
| Integrity (I) | High | Broad modification |
| Availability (A) | None | No loss of service |

#### Exploitability

**Score**: 6.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 7 | Documented and widely used |
| Attack Complexity | 7 | A single step suffices |
| Tooling Availability | 5 | Tools need adaptation |
| Skill Level | 5 | Intermediate skill |

#### Scalability

**Score**: 5.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 4 | Partly automatable |
| Target Scope | 5 | A class of targets |
| Resource Requirements | 8 | Minimal resources |
| Detection Difficulty | 3 | Readily detected |

#### Reachability

**Score**: 3.0 | **Trust Zone**: Data Zone (Trusted)

memory-store sits in the Data Zone. The zone baseline is 2.5 and the refinement for this finding gives 3.0.

---

### T-39 — policy-engine

**Threat**: Replay of an earlier valid update to guardrail rules and approval decisions reaches policy-engine because updates carry no nonce or expiry, restoring a state the owner already corrected.

**Category**: tampering | **Original Risk Level**: Medium | **Composite**: 5.4 (Medium)

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

**Score**: 5.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 4 | Described in research |
| Attack Complexity | 7 | A single step suffices |
| Tooling Availability | 3 | Needs custom tooling |
| Skill Level | 6 | Intermediate skill |

#### Scalability

**Score**: 5.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 6 | Partly automatable |
| Target Scope | 4 | A class of targets |
| Resource Requirements | 6 | Moderate resources |
| Detection Difficulty | 4 | Detectable with monitoring |

#### Reachability

**Score**: 2.5 | **Trust Zone**: Operations Zone (Trusted)

policy-engine sits in the Operations Zone. The zone baseline is 2.5 and the refinement for this finding gives 2.5.

---

### D-21 — embed-service-2

**Threat**: Unbounded growth of stored document chunks and query embeddings on embed-service-2 fills its volume, after which writes fail for every other consumer.

**Category**: denial-of-service | **Original Risk Level**: Medium | **Composite**: 5.4 (Medium)

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
| Known Techniques | 7 | Documented and widely used |
| Attack Complexity | 7 | A single step suffices |
| Tooling Availability | 7 | Common tools apply |
| Skill Level | 7 | Little skill needed |

#### Scalability

**Score**: 7.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 9 | Fully automatable |
| Target Scope | 9 | Every instance |
| Resource Requirements | 5 | Moderate resources |
| Detection Difficulty | 5 | Detectable with monitoring |

#### Reachability

**Score**: 2.0 | **Trust Zone**: Agent Runtime Zone (Trusted)

embed-service-2 sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 2.0.

---

### D-38 — summarizer-llm

**Threat**: Retry storms from feature-store-2 multiply the load on summarizer-llm when it slows down, turning a brief delay into a sustained outage.

**Category**: denial-of-service | **Original Risk Level**: Critical | **Composite**: 5.4 (Medium)

#### CVSS 3.1 Base

**Score**: 5.1 | **Vector**: `CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:L`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Local | Needs local access |
| Attack Complexity (AC) | Low | No special conditions |
| Privileges Required (PR) | None | No privileges needed |
| User Interaction (UI) | None | No user action needed |
| Scope (S) | Unchanged | Impact stays in the component |
| Confidentiality (C) | None | No disclosure |
| Integrity (I) | Low | Limited modification |
| Availability (A) | Low | Degraded service |

#### Exploitability

**Score**: 8.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 9 | Documented and widely used |
| Attack Complexity | 7 | A single step suffices |
| Tooling Availability | 7 | Common tools apply |
| Skill Level | 9 | Little skill needed |

#### Scalability

**Score**: 6.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 7 | Fully automatable |
| Target Scope | 9 | Every instance |
| Resource Requirements | 3 | Needs heavy infrastructure |
| Detection Difficulty | 5 | Detectable with monitoring |

#### Reachability

**Score**: 1.5 | **Trust Zone**: Agent Runtime Zone (Trusted)

summarizer-llm sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 1.5.

---

### AG-7 — planner-agent

**Threat**: planner-agent retries failed actions on its own, repeating side effects such as bookings or messages when the first attempt partly succeeded.

**Category**: agentic | **Original Risk Level**: Medium | **Composite**: 5.4 (Medium)

#### CVSS 3.1 Base

**Score**: 7.9 | **Vector**: `CVSS:3.1/AV:N/AC:H/PR:L/UI:R/S:C/C:H/I:H/A:L`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Network | Reachable over the network |
| Attack Complexity (AC) | High | Needs specific conditions |
| Privileges Required (PR) | Low | A basic account is needed |
| User Interaction (UI) | Required | A user must act |
| Scope (S) | Changed | Impact crosses a boundary |
| Confidentiality (C) | High | Broad disclosure |
| Integrity (I) | High | Broad modification |
| Availability (A) | Low | Degraded service |

#### Exploitability

**Score**: 4.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 7 | Documented and widely used |
| Attack Complexity | 5 | Needs some preparation |
| Tooling Availability | 2 | Needs custom tooling |
| Skill Level | 4 | Intermediate skill |

#### Scalability

**Score**: 6.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 4 | Partly automatable |
| Target Scope | 5 | A class of targets |
| Resource Requirements | 9 | Minimal resources |
| Detection Difficulty | 6 | Detectable with monitoring |

#### Reachability

**Score**: 2.0 | **Trust Zone**: Agent Runtime Zone (Trusted)

planner-agent sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 2.0.

---

### LLM-32 — memory-store

**Threat**: Anyone who can write to the ingestion path of memory-store can slip in documents that contradict authoritative sources.

**Category**: llm | **Original Risk Level**: High | **Composite**: 5.4 (Medium)

**Correlation Group**: Scores inherited from primary finding T-24 (CG-14). Dimensional detail is recorded on the primary.

**Score**: 6.5 | **Vector**: `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N`

---

### S-29 — queue-a2

**Threat**: An attacker replays a captured broker credential against queue-a2, which does not bind the credential to the session or channel it was issued for, so the replay is accepted as the original caller.

**Category**: spoofing | **Original Risk Level**: Low | **Composite**: 5.3 (Medium)

#### CVSS 3.1 Base

**Score**: 5.9 | **Vector**: `CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:L/A:N`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Network | Reachable over the network |
| Attack Complexity (AC) | High | Needs specific conditions |
| Privileges Required (PR) | Low | A basic account is needed |
| User Interaction (UI) | None | No user action needed |
| Scope (S) | Unchanged | Impact stays in the component |
| Confidentiality (C) | High | Broad disclosure |
| Integrity (I) | Low | Limited modification |
| Availability (A) | None | No loss of service |

#### Exploitability

**Score**: 6.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 8 | Documented and widely used |
| Attack Complexity | 7 | A single step suffices |
| Tooling Availability | 7 | Common tools apply |
| Skill Level | 4 | Intermediate skill |

#### Scalability

**Score**: 6.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 8 | Fully automatable |
| Target Scope | 5 | A class of targets |
| Resource Requirements | 7 | Minimal resources |
| Detection Difficulty | 6 | Detectable with monitoring |

#### Reachability

**Score**: 1.5 | **Trust Zone**: Agent Runtime Zone (Trusted)

queue-a2 sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 1.5.

---

### S-37 — eval-runner

**Threat**: An attacker replays a captured evaluation credential against eval-runner, which does not bind the credential to the session or channel it was issued for, so the replay is accepted as the original caller.

**Category**: spoofing | **Original Risk Level**: High | **Composite**: 5.3 (Medium)

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

**Score**: 7.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 8 | Documented and widely used |
| Attack Complexity | 5 | Needs some preparation |
| Tooling Availability | 8 | Common tools apply |
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

**Score**: 2.5 | **Trust Zone**: Operations Zone (Trusted)

eval-runner sits in the Operations Zone. The zone baseline is 2.5 and the refinement for this finding gives 2.5.

---

### T-3 — intake-agent

**Threat**: Replay of an earlier valid update to free-text shipment requests reaches intake-agent because updates carry no nonce or expiry, restoring a state the owner already corrected.

**Category**: tampering | **Original Risk Level**: Medium | **Composite**: 5.3 (Medium)

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

**Score**: 5.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 5 | Described in research |
| Attack Complexity | 4 | Needs some preparation |
| Tooling Availability | 5 | Tools need adaptation |
| Skill Level | 6 | Intermediate skill |

#### Scalability

**Score**: 4.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 5 | Partly automatable |
| Target Scope | 5 | A class of targets |
| Resource Requirements | 5 | Moderate resources |
| Detection Difficulty | 3 | Readily detected |

#### Reachability

**Score**: 3.0 | **Trust Zone**: Agent Runtime Zone (Trusted)

intake-agent sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 3.0.

---

### T-16 — summarizer-llm

**Threat**: Backups and exports of shipment records fed into summaries on summarizer-llm are writable by operators without a second approver, so a malicious change survives restores.

**Category**: tampering | **Original Risk Level**: Note | **Composite**: 5.3 (Medium)

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

**Score**: 5.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 5 | Described in research |
| Attack Complexity | 5 | Needs some preparation |
| Tooling Availability | 6 | Tools need adaptation |
| Skill Level | 4 | Intermediate skill |

#### Scalability

**Score**: 4.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 3 | Manual for each target |
| Target Scope | 3 | One specific target |
| Resource Requirements | 6 | Moderate resources |
| Detection Difficulty | 4 | Detectable with monitoring |

#### Reachability

**Score**: 3.5 | **Trust Zone**: Agent Runtime Zone (Trusted)

summarizer-llm sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 3.5.

---

### T-17 — summarizer-llm

**Threat**: Unsanitised shipment records fed into summaries reach summarizer-llm and are processed as trusted structure, so crafted input changes how later steps interpret the record.

**Category**: tampering | **Original Risk Level**: Low | **Composite**: 5.3 (Medium)

**Correlation Group**: Scores inherited from primary finding T-16 (CG-11). Dimensional detail is recorded on the primary.

**Score**: 7.1 | **Vector**: `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:L`

---

### T-30 — feature-store-2

**Threat**: An update to feature-store-2 is pulled without provenance checks, so a poisoned package can alter how ranking and fine-tuning features are handled at run time.

**Category**: tampering | **Original Risk Level**: Medium | **Composite**: 5.3 (Medium)

#### CVSS 3.1 Base

**Score**: 6.3 | **Vector**: `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:L`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Network | Reachable over the network |
| Attack Complexity (AC) | Low | No special conditions |
| Privileges Required (PR) | Low | A basic account is needed |
| User Interaction (UI) | None | No user action needed |
| Scope (S) | Unchanged | Impact stays in the component |
| Confidentiality (C) | Low | Limited disclosure |
| Integrity (I) | Low | Limited modification |
| Availability (A) | Low | Degraded service |

#### Exploitability

**Score**: 6.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 7 | Documented and widely used |
| Attack Complexity | 6 | Needs some preparation |
| Tooling Availability | 6 | Tools need adaptation |
| Skill Level | 5 | Intermediate skill |

#### Scalability

**Score**: 4.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 5 | Partly automatable |
| Target Scope | 3 | One specific target |
| Resource Requirements | 7 | Minimal resources |
| Detection Difficulty | 3 | Readily detected |

#### Reachability

**Score**: 3.0 | **Trust Zone**: Data Zone (Trusted)

feature-store-2 sits in the Data Zone. The zone baseline is 2.5 and the refinement for this finding gives 3.0.

---

### T-31 — feature-store-2

**Threat**: Configuration of feature-store-2 can be rewritten by any service that holds the shared deployment credential, silently changing how ranking and fine-tuning features are handled.

**Category**: tampering | **Original Risk Level**: High | **Composite**: 5.3 (Medium)

**Correlation Group**: Scores inherited from primary finding T-30 (CG-16). Dimensional detail is recorded on the primary.

**Score**: 6.3 | **Vector**: `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:L`

---

### T-42 — audit-ledger

**Threat**: An attacker who can write to the channel between reviewer-agent and audit-ledger modifies approval and tool call records in transit because messages carry no integrity protection of their own.

**Category**: tampering | **Original Risk Level**: Note | **Composite**: 5.3 (Medium)

#### CVSS 3.1 Base

**Score**: 7.1 | **Vector**: `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:H/A:N`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Network | Reachable over the network |
| Attack Complexity (AC) | Low | No special conditions |
| Privileges Required (PR) | Low | A basic account is needed |
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
| Tooling Availability | 3 | Needs custom tooling |
| Skill Level | 6 | Intermediate skill |

#### Scalability

**Score**: 4.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 3 | Manual for each target |
| Target Scope | 2 | One specific target |
| Resource Requirements | 6 | Moderate resources |
| Detection Difficulty | 5 | Detectable with monitoring |

#### Reachability

**Score**: 3.5 | **Trust Zone**: Operations Zone (Trusted)

audit-ledger sits in the Operations Zone. The zone baseline is 2.5 and the refinement for this finding gives 3.5.

---

### T-45 — worker-3

**Threat**: An update to worker-3 is pulled without provenance checks, so a poisoned package can alter how work orders and draft documents are handled at run time.

**Category**: tampering | **Original Risk Level**: Medium | **Composite**: 5.3 (Medium)

#### CVSS 3.1 Base

**Score**: 7.6 | **Vector**: `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:H`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Network | Reachable over the network |
| Attack Complexity (AC) | Low | No special conditions |
| Privileges Required (PR) | Low | A basic account is needed |
| User Interaction (UI) | None | No user action needed |
| Scope (S) | Unchanged | Impact stays in the component |
| Confidentiality (C) | Low | Limited disclosure |
| Integrity (I) | Low | Limited modification |
| Availability (A) | High | Loss of service |

#### Exploitability

**Score**: 5.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 7 | Documented and widely used |
| Attack Complexity | 4 | Needs some preparation |
| Tooling Availability | 6 | Tools need adaptation |
| Skill Level | 3 | Needs deep expertise |

#### Scalability

**Score**: 4.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 6 | Partly automatable |
| Target Scope | 2 | One specific target |
| Resource Requirements | 6 | Moderate resources |
| Detection Difficulty | 2 | Readily detected |

#### Reachability

**Score**: 2.5 | **Trust Zone**: Agent Runtime Zone (Trusted)

worker-3 sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 2.5.

---

### I-16 — tool-server-1

**Threat**: Cross-tenant filters on tool-server-1 are applied in application code only, so one missing predicate exposes another tenant's tool call arguments and results.

**Category**: info-disclosure | **Original Risk Level**: Medium | **Composite**: 5.3 (Medium)

#### CVSS 3.1 Base

**Score**: 5.5 | **Vector**: `CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Local | Needs local access |
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
| Known Techniques | 7 | Documented and widely used |
| Attack Complexity | 8 | A single step suffices |
| Tooling Availability | 6 | Tools need adaptation |
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

**Score**: 3.5 | **Trust Zone**: Agent Runtime Zone (Trusted)

tool-server-1 sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 3.5.

---

### I-17 — tool-server-1

**Threat**: Secrets such as the tool API key for tool-server-1 appear in process arguments and environment dumps that diagnostic tooling captures.

**Category**: info-disclosure | **Original Risk Level**: Medium | **Composite**: 5.3 (Medium)

**Correlation Group**: Scores inherited from primary finding I-16 (CG-8). Dimensional detail is recorded on the primary.

**Score**: 5.5 | **Vector**: `CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N`

---

### I-24 — summarizer-llm

**Threat**: Logs and traces emitted by summarizer-llm include raw shipment records fed into summaries, so anyone with access to the logging pipeline can read content meant for one tenant.

**Category**: info-disclosure | **Original Risk Level**: Low | **Composite**: 5.3 (Medium)

**Correlation Group**: Scores inherited from primary finding T-16 (CG-11). Dimensional detail is recorded on the primary.

**Score**: 7.1 | **Vector**: `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:L`

---

### I-40 — policy-engine

**Threat**: Logs and traces emitted by policy-engine include raw guardrail rules and approval decisions, so anyone with access to the logging pipeline can read content meant for one tenant.

**Category**: info-disclosure | **Original Risk Level**: Medium | **Composite**: 5.3 (Medium)

#### CVSS 3.1 Base

**Score**: 5.7 | **Vector**: `CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:H/I:N/A:N`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Network | Reachable over the network |
| Attack Complexity (AC) | Low | No special conditions |
| Privileges Required (PR) | Low | A basic account is needed |
| User Interaction (UI) | Required | A user must act |
| Scope (S) | Unchanged | Impact stays in the component |
| Confidentiality (C) | High | Broad disclosure |
| Integrity (I) | None | No modification |
| Availability (A) | None | No loss of service |

#### Exploitability

**Score**: 6.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 8 | Documented and widely used |
| Attack Complexity | 6 | Needs some preparation |
| Tooling Availability | 6 | Tools need adaptation |
| Skill Level | 6 | Intermediate skill |

#### Scalability

**Score**: 6.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 6 | Partly automatable |
| Target Scope | 7 | Every instance |
| Resource Requirements | 8 | Minimal resources |
| Detection Difficulty | 3 | Readily detected |

#### Reachability

**Score**: 2.5 | **Trust Zone**: Operations Zone (Trusted)

policy-engine sits in the Operations Zone. The zone baseline is 2.5 and the refinement for this finding gives 2.5.

---

### I-41 — audit-ledger

**Threat**: approval and tool call records held by audit-ledger are readable by any service in the Operations Zone that shares the same network role, because access is granted by network position.

**Category**: info-disclosure | **Original Risk Level**: Medium | **Composite**: 5.3 (Medium)

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

**Score**: 6.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 6 | Described in research |
| Attack Complexity | 5 | Needs some preparation |
| Tooling Availability | 5 | Tools need adaptation |
| Skill Level | 8 | Little skill needed |

#### Scalability

**Score**: 6.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 8 | Fully automatable |
| Target Scope | 4 | A class of targets |
| Resource Requirements | 7 | Minimal resources |
| Detection Difficulty | 5 | Detectable with monitoring |

#### Reachability

**Score**: 3.5 | **Trust Zone**: Operations Zone (Trusted)

audit-ledger sits in the Operations Zone. The zone baseline is 2.5 and the refinement for this finding gives 3.5.

---

### D-14 — tool-server-1

**Threat**: A burst of requests exhausts the connection pool of tool-server-1, which queues work without a bound and blocks legitimate use of tool call arguments and results.

**Category**: denial-of-service | **Original Risk Level**: Medium | **Composite**: 5.3 (Medium)

**Correlation Group**: Scores inherited from primary finding I-16 (CG-8). Dimensional detail is recorded on the primary.

**Score**: 5.5 | **Vector**: `CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N`

---

### D-15 — tool-server-1

**Threat**: A single oversized or deeply nested payload makes tool-server-1 spend disproportionate memory and CPU parsing tool call arguments and results.

**Category**: denial-of-service | **Original Risk Level**: Low | **Composite**: 5.3 (Medium)

**Correlation Group**: Scores inherited from primary finding I-16 (CG-8). Dimensional detail is recorded on the primary.

**Score**: 5.5 | **Vector**: `CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N`

---

### E-11 — router-agent

**Threat**: Multi-tenant separation in router-agent depends on a request header that clients can set, allowing one tenant to act in another's scope.

**Category**: privilege-escalation | **Original Risk Level**: High | **Composite**: 5.3 (Medium)

#### CVSS 3.1 Base

**Score**: 6.6 | **Vector**: `CVSS:3.1/AV:L/AC:H/PR:L/UI:R/S:C/C:L/I:H/A:L`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Local | Needs local access |
| Attack Complexity (AC) | High | Needs specific conditions |
| Privileges Required (PR) | Low | A basic account is needed |
| User Interaction (UI) | Required | A user must act |
| Scope (S) | Changed | Impact crosses a boundary |
| Confidentiality (C) | Low | Limited disclosure |
| Integrity (I) | High | Broad modification |
| Availability (A) | Low | Degraded service |

#### Exploitability

**Score**: 5.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 4 | Described in research |
| Attack Complexity | 7 | A single step suffices |
| Tooling Availability | 5 | Tools need adaptation |
| Skill Level | 6 | Intermediate skill |

#### Scalability

**Score**: 5.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 4 | Partly automatable |
| Target Scope | 6 | A class of targets |
| Resource Requirements | 8 | Minimal resources |
| Detection Difficulty | 4 | Detectable with monitoring |

#### Reachability

**Score**: 2.5 | **Trust Zone**: Agent Runtime Zone (Trusted)

router-agent sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 2.5.

---

### AG-34 — tool-server-1

**Threat**: tool-server-1 invokes tools with arguments assembled from model output, so an attacker who shapes the output can call a tool with parameters the designer never allowed.

**Category**: agentic | **Original Risk Level**: Low | **Composite**: 5.3 (Medium)

**Correlation Group**: Scores inherited from primary finding I-16 (CG-8). Dimensional detail is recorded on the primary.

**Score**: 5.5 | **Vector**: `CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N`

---

### LLM-17 — tool-server-1

**Threat**: Encoded or multilingual payloads bypass the keyword filter in front of tool-server-1, which only checks plain English text.

**Category**: llm | **Original Risk Level**: Medium | **Composite**: 5.3 (Medium)

**Correlation Group**: Scores inherited from primary finding I-16 (CG-8). Dimensional detail is recorded on the primary.

**Score**: 5.5 | **Vector**: `CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N`

---

### LLM-24 — summarizer-llm

**Threat**: summarizer-llm follows links and files named in shipment records fed into summaries, which turns a harmless-looking request into a fetch of attacker-controlled content.

**Category**: llm | **Original Risk Level**: Critical | **Composite**: 5.3 (Medium)

**Correlation Group**: Scores inherited from primary finding T-16 (CG-11). Dimensional detail is recorded on the primary.

**Score**: 7.1 | **Vector**: `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:L`

---

### LLM-25 — summarizer-llm

**Threat**: Embeddings stored by summarizer-llm can be crowded with near-duplicate vectors that win similarity searches for chosen queries.

**Category**: llm | **Original Risk Level**: High | **Composite**: 5.3 (Medium)

**Correlation Group**: Scores inherited from primary finding T-16 (CG-11). Dimensional detail is recorded on the primary.

**Score**: 7.1 | **Vector**: `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:L`

---

### LLM-39 — feature-store-2

**Threat**: Fine-tuning data assembled from feature-store-2 is not checked for outliers or duplicates, so a small batch of crafted examples changes model behaviour.

**Category**: llm | **Original Risk Level**: High | **Composite**: 5.3 (Medium)

**Correlation Group**: Scores inherited from primary finding T-30 (CG-16). Dimensional detail is recorded on the primary.

**Score**: 6.3 | **Vector**: `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:L`

---

### TE-7 — reviewer-agent

**Threat**: Persuasive phrasing from reviewer-agent pushes operators to approve proposals quickly, which reduces careful review.

**Category**: agentic | **Original Risk Level**: Low | **Composite**: 5.3 (Medium)

#### CVSS 3.1 Base

**Score**: 7.7 | **Vector**: `CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:C/C:H/I:L/A:L`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Network | Reachable over the network |
| Attack Complexity (AC) | High | Needs specific conditions |
| Privileges Required (PR) | Low | A basic account is needed |
| User Interaction (UI) | None | No user action needed |
| Scope (S) | Changed | Impact crosses a boundary |
| Confidentiality (C) | High | Broad disclosure |
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
| Scriptability | 3 | Manual for each target |
| Target Scope | 3 | One specific target |
| Resource Requirements | 9 | Minimal resources |
| Detection Difficulty | 5 | Detectable with monitoring |

#### Reachability

**Score**: 3.5 | **Trust Zone**: Agent Runtime Zone (Trusted)

reviewer-agent sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 3.5.

---

### S-27 — summarizer-llm

**Threat**: An attacker replays a captured inference credential against summarizer-llm, which does not bind the credential to the session or channel it was issued for, so the replay is accepted as the original caller.

**Category**: spoofing | **Original Risk Level**: High | **Composite**: 5.2 (Medium)

#### CVSS 3.1 Base

**Score**: 5.9 | **Vector**: `CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:L/A:N`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Network | Reachable over the network |
| Attack Complexity (AC) | High | Needs specific conditions |
| Privileges Required (PR) | None | No privileges needed |
| User Interaction (UI) | Required | A user must act |
| Scope (S) | Unchanged | Impact stays in the component |
| Confidentiality (C) | High | Broad disclosure |
| Integrity (I) | Low | Limited modification |
| Availability (A) | None | No loss of service |

#### Exploitability

**Score**: 6.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 5 | Described in research |
| Attack Complexity | 8 | A single step suffices |
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

**Score**: 2.5 | **Trust Zone**: Agent Runtime Zone (Trusted)

summarizer-llm sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 2.5.

---

### T-33 — queue-a2

**Threat**: A race between concurrent writers lets an attacker overwrite task and result messages on queue-a2 after validation but before use, defeating the earlier check.

**Category**: tampering | **Original Risk Level**: Medium | **Composite**: 5.2 (Medium)

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

**Score**: 5.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 7 | Documented and widely used |
| Attack Complexity | 5 | Needs some preparation |
| Tooling Availability | 3 | Needs custom tooling |
| Skill Level | 5 | Intermediate skill |

#### Scalability

**Score**: 5.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 5 | Partly automatable |
| Target Scope | 5 | A class of targets |
| Resource Requirements | 8 | Minimal resources |
| Detection Difficulty | 2 | Readily detected |

#### Reachability

**Score**: 2.5 | **Trust Zone**: Agent Runtime Zone (Trusted)

queue-a2 sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 2.5.

---

### I-45 — s3-archive

**Threat**: A timing or size difference in the responses of s3-archive lets an observer infer whether specific records of archived transcripts and training corpora exist.

**Category**: info-disclosure | **Original Risk Level**: Medium | **Composite**: 5.2 (Medium)

#### CVSS 3.1 Base

**Score**: 5.8 | **Vector**: `CVSS:3.1/AV:N/AC:H/PR:L/UI:R/S:C/C:H/I:N/A:N`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Network | Reachable over the network |
| Attack Complexity (AC) | High | Needs specific conditions |
| Privileges Required (PR) | Low | A basic account is needed |
| User Interaction (UI) | Required | A user must act |
| Scope (S) | Changed | Impact crosses a boundary |
| Confidentiality (C) | High | Broad disclosure |
| Integrity (I) | None | No modification |
| Availability (A) | None | No loss of service |

#### Exploitability

**Score**: 5.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 7 | Documented and widely used |
| Attack Complexity | 6 | Needs some preparation |
| Tooling Availability | 4 | Tools need adaptation |
| Skill Level | 5 | Intermediate skill |

#### Scalability

**Score**: 6.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 6 | Partly automatable |
| Target Scope | 6 | A class of targets |
| Resource Requirements | 9 | Minimal resources |
| Detection Difficulty | 3 | Readily detected |

#### Reachability

**Score**: 3.0 | **Trust Zone**: Data Zone (Trusted)

s3-archive sits in the Data Zone. The zone baseline is 2.5 and the refinement for this finding gives 3.0.

---

### D-5 — intake-agent

**Threat**: A single oversized or deeply nested payload makes intake-agent spend disproportionate memory and CPU parsing free-text shipment requests.

**Category**: denial-of-service | **Original Risk Level**: High | **Composite**: 5.2 (Medium)

#### CVSS 3.1 Base

**Score**: 4.8 | **Vector**: `CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:L/A:L`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Network | Reachable over the network |
| Attack Complexity (AC) | High | Needs specific conditions |
| Privileges Required (PR) | None | No privileges needed |
| User Interaction (UI) | None | No user action needed |
| Scope (S) | Unchanged | Impact stays in the component |
| Confidentiality (C) | None | No disclosure |
| Integrity (I) | Low | Limited modification |
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

**Score**: 5.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 7 | Fully automatable |
| Target Scope | 9 | Every instance |
| Resource Requirements | 3 | Needs heavy infrastructure |
| Detection Difficulty | 3 | Readily detected |

#### Reachability

**Score**: 1.5 | **Trust Zone**: Agent Runtime Zone (Trusted)

intake-agent sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 1.5.

---

### D-19 — model-gateway

**Threat**: A dependency of model-gateway becomes unavailable and the failure cascades because model-gateway waits on it synchronously for every request.

**Category**: denial-of-service | **Original Risk Level**: High | **Composite**: 5.2 (Medium)

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

**Score**: 7.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 7 | Documented and widely used |
| Attack Complexity | 7 | A single step suffices |
| Tooling Availability | 8 | Common tools apply |
| Skill Level | 8 | Little skill needed |

#### Scalability

**Score**: 6.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 10 | Fully automatable |
| Target Scope | 7 | Every instance |
| Resource Requirements | 6 | Moderate resources |
| Detection Difficulty | 1 | Readily detected |

#### Reachability

**Score**: 1.5 | **Trust Zone**: Agent Runtime Zone (Trusted)

model-gateway sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 1.5.

---

### AG-8 — planner-agent

**Threat**: planner-agent does not limit the rate or total number of tool calls per task, so abuse of a costly tool goes unnoticed until the invoice arrives.

**Category**: agentic | **Original Risk Level**: Medium | **Composite**: 5.2 (Medium)

#### CVSS 3.1 Base

**Score**: 8.2 | **Vector**: `CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:H/A:L`

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

**Score**: 4.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 4 | Described in research |
| Attack Complexity | 6 | Needs some preparation |
| Tooling Availability | 2 | Needs custom tooling |
| Skill Level | 4 | Intermediate skill |

#### Scalability

**Score**: 5.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 3 | Manual for each target |
| Target Scope | 4 | A class of targets |
| Resource Requirements | 8 | Minimal resources |
| Detection Difficulty | 5 | Detectable with monitoring |

#### Reachability

**Score**: 2.0 | **Trust Zone**: Agent Runtime Zone (Trusted)

planner-agent sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 2.0.

---

### TE-12 — summarizer-llm

**Threat**: summarizer-llm claims certainty it does not have when summarising shipment risk, and customers rely on the stated confidence.

**Category**: agentic | **Original Risk Level**: Low | **Composite**: 5.2 (Medium)

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
| Target Scope | 4 | A class of targets |
| Resource Requirements | 6 | Moderate resources |
| Detection Difficulty | 7 | Blends with normal use |

#### Reachability

**Score**: 2.5 | **Trust Zone**: Agent Runtime Zone (Trusted)

summarizer-llm sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 2.5.

---

### S-18 — tool-server-1

**Threat**: A shared or long-lived tool API key on tool-server-1 lets anyone who obtains one copy authenticate as every tenant that uses the same deployment profile.

**Category**: spoofing | **Original Risk Level**: Medium | **Composite**: 5.1 (Medium)

#### CVSS 3.1 Base

**Score**: 5.0 | **Vector**: `CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:L/I:L/A:L`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Network | Reachable over the network |
| Attack Complexity (AC) | High | Needs specific conditions |
| Privileges Required (PR) | Low | A basic account is needed |
| User Interaction (UI) | None | No user action needed |
| Scope (S) | Unchanged | Impact stays in the component |
| Confidentiality (C) | Low | Limited disclosure |
| Integrity (I) | Low | Limited modification |
| Availability (A) | Low | Degraded service |

#### Exploitability

**Score**: 6.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 6 | Described in research |
| Attack Complexity | 6 | Needs some preparation |
| Tooling Availability | 6 | Tools need adaptation |
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

**Score**: 2.5 | **Trust Zone**: Agent Runtime Zone (Trusted)

tool-server-1 sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 2.5.

---

### T-9 — tool-server-1

**Threat**: An update to tool-server-1 is pulled without provenance checks, so a poisoned package can alter how tool call arguments and results are handled at run time.

**Category**: tampering | **Original Risk Level**: High | **Composite**: 5.1 (Medium)

#### CVSS 3.1 Base

**Score**: 6.6 | **Vector**: `CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:L/I:H/A:L`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Local | Needs local access |
| Attack Complexity (AC) | Low | No special conditions |
| Privileges Required (PR) | Low | A basic account is needed |
| User Interaction (UI) | None | No user action needed |
| Scope (S) | Unchanged | Impact stays in the component |
| Confidentiality (C) | Low | Limited disclosure |
| Integrity (I) | High | Broad modification |
| Availability (A) | Low | Degraded service |

#### Exploitability

**Score**: 5.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 5 | Described in research |
| Attack Complexity | 5 | Needs some preparation |
| Tooling Availability | 5 | Tools need adaptation |
| Skill Level | 5 | Intermediate skill |

#### Scalability

**Score**: 4.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 4 | Partly automatable |
| Target Scope | 2 | One specific target |
| Resource Requirements | 6 | Moderate resources |
| Detection Difficulty | 4 | Detectable with monitoring |

#### Reachability

**Score**: 3.5 | **Trust Zone**: Agent Runtime Zone (Trusted)

tool-server-1 sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 3.5.

---

### T-11 — model-gateway

**Threat**: Configuration of model-gateway can be rewritten by any service that holds the shared deployment credential, silently changing how prompts and completions are handled.

**Category**: tampering | **Original Risk Level**: Medium | **Composite**: 5.1 (Medium)

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

**Score**: 6.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 7 | Documented and widely used |
| Attack Complexity | 6 | Needs some preparation |
| Tooling Availability | 5 | Tools need adaptation |
| Skill Level | 6 | Intermediate skill |

#### Scalability

**Score**: 5.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 4 | Partly automatable |
| Target Scope | 3 | One specific target |
| Resource Requirements | 8 | Minimal resources |
| Detection Difficulty | 5 | Detectable with monitoring |

#### Reachability

**Score**: 2.5 | **Trust Zone**: Agent Runtime Zone (Trusted)

model-gateway sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 2.5.

---

### T-29 — s3-archive

**Threat**: Unsanitised archived transcripts and training corpora reach s3-archive and are processed as trusted structure, so crafted input changes how later steps interpret the record.

**Category**: tampering | **Original Risk Level**: High | **Composite**: 5.1 (Medium)

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

**Score**: 4.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 6 | Described in research |
| Attack Complexity | 4 | Needs some preparation |
| Tooling Availability | 3 | Needs custom tooling |
| Skill Level | 5 | Intermediate skill |

#### Scalability

**Score**: 4.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 5 | Partly automatable |
| Target Scope | 2 | One specific target |
| Resource Requirements | 5 | Moderate resources |
| Detection Difficulty | 6 | Detectable with monitoring |

#### Reachability

**Score**: 3.0 | **Trust Zone**: Data Zone (Trusted)

s3-archive sits in the Data Zone. The zone baseline is 2.5 and the refinement for this finding gives 3.0.

---

### T-37 — eval-runner

**Threat**: Serialised objects arriving from trace-collector are deserialised by eval-runner with permissive type handling, allowing crafted payloads to instantiate unintended behaviour.

**Category**: tampering | **Original Risk Level**: Critical | **Composite**: 5.1 (Medium)

#### CVSS 3.1 Base

**Score**: 7.4 | **Vector**: `CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:H/A:H`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Network | Reachable over the network |
| Attack Complexity (AC) | High | Needs specific conditions |
| Privileges Required (PR) | None | No privileges needed |
| User Interaction (UI) | None | No user action needed |
| Scope (S) | Unchanged | Impact stays in the component |
| Confidentiality (C) | None | No disclosure |
| Integrity (I) | High | Broad modification |
| Availability (A) | High | Loss of service |

#### Exploitability

**Score**: 5.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 6 | Described in research |
| Attack Complexity | 4 | Needs some preparation |
| Tooling Availability | 3 | Needs custom tooling |
| Skill Level | 7 | Little skill needed |

#### Scalability

**Score**: 5.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 3 | Manual for each target |
| Target Scope | 4 | A class of targets |
| Resource Requirements | 7 | Minimal resources |
| Detection Difficulty | 6 | Detectable with monitoring |

#### Reachability

**Score**: 1.5 | **Trust Zone**: Operations Zone (Trusted)

eval-runner sits in the Operations Zone. The zone baseline is 2.5 and the refinement for this finding gives 1.5.

---

### T-38 — eval-runner

**Threat**: Backups and exports of replayed traces and judge verdicts on eval-runner are writable by operators without a second approver, so a malicious change survives restores.

**Category**: tampering | **Original Risk Level**: High | **Composite**: 5.1 (Medium)

**Correlation Group**: Scores inherited from primary finding T-37 (CG-20). Dimensional detail is recorded on the primary.

**Score**: 7.4 | **Vector**: `CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:H/A:H`

---

### T-43 — router-agent

**Threat**: Unsanitised subtask assignments reach router-agent and are processed as trusted structure, so crafted input changes how later steps interpret the record.

**Category**: tampering | **Original Risk Level**: Low | **Composite**: 5.1 (Medium)

#### CVSS 3.1 Base

**Score**: 6.4 | **Vector**: `CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:L/I:H/A:L`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Network | Reachable over the network |
| Attack Complexity (AC) | High | Needs specific conditions |
| Privileges Required (PR) | Low | A basic account is needed |
| User Interaction (UI) | None | No user action needed |
| Scope (S) | Unchanged | Impact stays in the component |
| Confidentiality (C) | Low | Limited disclosure |
| Integrity (I) | High | Broad modification |
| Availability (A) | Low | Degraded service |

#### Exploitability

**Score**: 5.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 5 | Described in research |
| Attack Complexity | 7 | A single step suffices |
| Tooling Availability | 5 | Tools need adaptation |
| Skill Level | 5 | Intermediate skill |

#### Scalability

**Score**: 5.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 5 | Partly automatable |
| Target Scope | 5 | A class of targets |
| Resource Requirements | 7 | Minimal resources |
| Detection Difficulty | 3 | Readily detected |

#### Reachability

**Score**: 2.5 | **Trust Zone**: Agent Runtime Zone (Trusted)

router-agent sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 2.5.

---

### R-3 — edge-gateway

**Threat**: Log entries from edge-gateway can be edited or deleted by the same operators who administer it, so evidence of misuse can be removed after the fact.

**Category**: repudiation | **Original Risk Level**: Medium | **Composite**: 5.1 (Medium)

#### CVSS 3.1 Base

**Score**: 3.1 | **Vector**: `CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:N/I:L/A:N`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Network | Reachable over the network |
| Attack Complexity (AC) | High | Needs specific conditions |
| Privileges Required (PR) | Low | A basic account is needed |
| User Interaction (UI) | None | No user action needed |
| Scope (S) | Unchanged | Impact stays in the component |
| Confidentiality (C) | None | No disclosure |
| Integrity (I) | Low | Limited modification |
| Availability (A) | None | No loss of service |

#### Exploitability

**Score**: 5.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 6 | Described in research |
| Attack Complexity | 7 | A single step suffices |
| Tooling Availability | 4 | Tools need adaptation |
| Skill Level | 5 | Intermediate skill |

#### Scalability

**Score**: 7.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 4 | Partly automatable |
| Target Scope | 5 | A class of targets |
| Resource Requirements | 10 | Minimal resources |
| Detection Difficulty | 9 | Blends with normal use |

#### Reachability

**Score**: 6.5 | **Trust Zone**: Edge DMZ (Semi-trusted)

edge-gateway sits in the Edge DMZ. The zone baseline is 6.5 and the refinement for this finding gives 6.5.

---

### I-46 — eval-runner

**Threat**: Verbose error responses from eval-runner reveal internal paths, query text and identifiers of replayed traces and judge verdicts to any caller who can trigger a failure.

**Category**: info-disclosure | **Original Risk Level**: Low | **Composite**: 5.1 (Medium)

**Correlation Group**: Scores inherited from primary finding T-37 (CG-20). Dimensional detail is recorded on the primary.

**Score**: 7.4 | **Vector**: `CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:H/A:H`

---

### D-25 — memory-store

**Threat**: A dependency of memory-store becomes unavailable and the failure cascades because memory-store waits on it synchronously for every request.

**Category**: denial-of-service | **Original Risk Level**: Medium | **Composite**: 5.1 (Medium)

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

**Score**: 7.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 8 | Documented and widely used |
| Attack Complexity | 9 | A single step suffices |
| Tooling Availability | 5 | Tools need adaptation |
| Skill Level | 8 | Little skill needed |

#### Scalability

**Score**: 6.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 10 | Fully automatable |
| Target Scope | 8 | Every instance |
| Resource Requirements | 3 | Needs heavy infrastructure |
| Detection Difficulty | 5 | Detectable with monitoring |

#### Reachability

**Score**: 2.0 | **Trust Zone**: Data Zone (Trusted)

memory-store sits in the Data Zone. The zone baseline is 2.5 and the refinement for this finding gives 2.0.

---

### E-24 — summarizer-llm

**Threat**: Role claims carried in the inference credential presented to summarizer-llm are honoured without confirmation against the authoritative directory.

**Category**: privilege-escalation | **Original Risk Level**: High | **Composite**: 5.1 (Medium)

#### CVSS 3.1 Base

**Score**: 7.4 | **Vector**: `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:L/I:L/A:L`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Network | Reachable over the network |
| Attack Complexity (AC) | Low | No special conditions |
| Privileges Required (PR) | Low | A basic account is needed |
| User Interaction (UI) | None | No user action needed |
| Scope (S) | Changed | Impact crosses a boundary |
| Confidentiality (C) | Low | Limited disclosure |
| Integrity (I) | Low | Limited modification |
| Availability (A) | Low | Degraded service |

#### Exploitability

**Score**: 5.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 6 | Described in research |
| Attack Complexity | 4 | Needs some preparation |
| Tooling Availability | 6 | Tools need adaptation |
| Skill Level | 4 | Intermediate skill |

#### Scalability

**Score**: 5.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 5 | Partly automatable |
| Target Scope | 6 | A class of targets |
| Resource Requirements | 6 | Moderate resources |
| Detection Difficulty | 3 | Readily detected |

#### Reachability

**Score**: 1.5 | **Trust Zone**: Agent Runtime Zone (Trusted)

summarizer-llm sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 1.5.

---

### AG-32 — tool-server-1

**Threat**: tool-server-1 runs without a budget on steps or spend, so a loop or an adversarial task keeps it acting long after it stopped being useful.

**Category**: agentic | **Original Risk Level**: High | **Composite**: 5.1 (Medium)

#### CVSS 3.1 Base

**Score**: 7.4 | **Vector**: `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:L/I:L/A:L`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Network | Reachable over the network |
| Attack Complexity (AC) | Low | No special conditions |
| Privileges Required (PR) | Low | A basic account is needed |
| User Interaction (UI) | None | No user action needed |
| Scope (S) | Changed | Impact crosses a boundary |
| Confidentiality (C) | Low | Limited disclosure |
| Integrity (I) | Low | Limited modification |
| Availability (A) | Low | Degraded service |

#### Exploitability

**Score**: 4.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 4 | Described in research |
| Attack Complexity | 3 | Needs chained steps |
| Tooling Availability | 4 | Tools need adaptation |
| Skill Level | 7 | Little skill needed |

#### Scalability

**Score**: 5.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 3 | Manual for each target |
| Target Scope | 4 | A class of targets |
| Resource Requirements | 8 | Minimal resources |
| Detection Difficulty | 5 | Detectable with monitoring |

#### Reachability

**Score**: 2.0 | **Trust Zone**: Agent Runtime Zone (Trusted)

tool-server-1 sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 2.0.

---

### LLM-44 — eval-runner

**Threat**: A user message crafted to look like a system directive persuades eval-runner to disclose its configuration or ignore its rules.

**Category**: llm | **Original Risk Level**: Critical | **Composite**: 5.1 (Medium)

**Correlation Group**: Scores inherited from primary finding T-37 (CG-20). Dimensional detail is recorded on the primary.

**Score**: 7.4 | **Vector**: `CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:H/A:H`

---

### LLM-45 — eval-runner

**Threat**: Indirect injection through documents retrieved for eval-runner lets the author of a retrieved page steer the answer without ever talking to the system.

**Category**: llm | **Original Risk Level**: Medium | **Composite**: 5.1 (Medium)

**Correlation Group**: Scores inherited from primary finding T-37 (CG-20). Dimensional detail is recorded on the primary.

**Score**: 7.4 | **Vector**: `CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:H/A:H`

---

### LLM-46 — eval-runner

**Threat**: Embeddings stored by eval-runner can be crowded with near-duplicate vectors that win similarity searches for chosen queries.

**Category**: llm | **Original Risk Level**: Critical | **Composite**: 5.1 (Medium)

**Correlation Group**: Scores inherited from primary finding T-37 (CG-20). Dimensional detail is recorded on the primary.

**Score**: 7.4 | **Vector**: `CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:H/A:H`

---

### T-4 — planner-agent

**Threat**: Unsanitised task plans and tool selections reach planner-agent and are processed as trusted structure, so crafted input changes how later steps interpret the record.

**Category**: tampering | **Original Risk Level**: High | **Composite**: 5.0 (Medium)

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

**Score**: 4.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 5 | Described in research |
| Attack Complexity | 5 | Needs some preparation |
| Tooling Availability | 3 | Needs custom tooling |
| Skill Level | 5 | Intermediate skill |

#### Scalability

**Score**: 3.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 3 | Manual for each target |
| Target Scope | 2 | One specific target |
| Resource Requirements | 6 | Moderate resources |
| Detection Difficulty | 3 | Readily detected |

#### Reachability

**Score**: 3.0 | **Trust Zone**: Agent Runtime Zone (Trusted)

planner-agent sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 3.0.

---

### T-10 — tool-server-1

**Threat**: Configuration of tool-server-1 can be rewritten by any service that holds the shared deployment credential, silently changing how tool call arguments and results are handled.

**Category**: tampering | **Original Risk Level**: Critical | **Composite**: 5.0 (Medium)

#### CVSS 3.1 Base

**Score**: 6.5 | **Vector**: `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Network | Reachable over the network |
| Attack Complexity (AC) | Low | No special conditions |
| Privileges Required (PR) | Low | A basic account is needed |
| User Interaction (UI) | None | No user action needed |
| Scope (S) | Unchanged | Impact stays in the component |
| Confidentiality (C) | None | No disclosure |
| Integrity (I) | High | Broad modification |
| Availability (A) | None | No loss of service |

#### Exploitability

**Score**: 5.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 5 | Described in research |
| Attack Complexity | 6 | Needs some preparation |
| Tooling Availability | 6 | Tools need adaptation |
| Skill Level | 3 | Needs deep expertise |

#### Scalability

**Score**: 4.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 3 | Manual for each target |
| Target Scope | 4 | A class of targets |
| Resource Requirements | 6 | Moderate resources |
| Detection Difficulty | 3 | Readily detected |

#### Reachability

**Score**: 3.0 | **Trust Zone**: Agent Runtime Zone (Trusted)

tool-server-1 sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 3.0.

---

### T-12 — model-gateway

**Threat**: A race between concurrent writers lets an attacker overwrite prompts and completions on model-gateway after validation but before use, defeating the earlier check.

**Category**: tampering | **Original Risk Level**: Low | **Composite**: 5.0 (Medium)

#### CVSS 3.1 Base

**Score**: 6.0 | **Vector**: `CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:L/I:H/A:L`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Network | Reachable over the network |
| Attack Complexity (AC) | Low | No special conditions |
| Privileges Required (PR) | High | Administrative rights are needed |
| User Interaction (UI) | None | No user action needed |
| Scope (S) | Unchanged | Impact stays in the component |
| Confidentiality (C) | Low | Limited disclosure |
| Integrity (I) | High | Broad modification |
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

**Score**: 5.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 4 | Partly automatable |
| Target Scope | 5 | A class of targets |
| Resource Requirements | 7 | Minimal resources |
| Detection Difficulty | 4 | Detectable with monitoring |

#### Reachability

**Score**: 2.5 | **Trust Zone**: Agent Runtime Zone (Trusted)

model-gateway sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 2.5.

---

### T-13 — model-gateway

**Threat**: Replay of an earlier valid update to prompts and completions reaches model-gateway because updates carry no nonce or expiry, restoring a state the owner already corrected.

**Category**: tampering | **Original Risk Level**: High | **Composite**: 5.0 (Medium)

#### CVSS 3.1 Base

**Score**: 6.9 | **Vector**: `CVSS:3.1/AV:N/AC:L/PR:H/UI:R/S:C/C:N/I:H/A:L`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Network | Reachable over the network |
| Attack Complexity (AC) | Low | No special conditions |
| Privileges Required (PR) | High | Administrative rights are needed |
| User Interaction (UI) | Required | A user must act |
| Scope (S) | Changed | Impact crosses a boundary |
| Confidentiality (C) | None | No disclosure |
| Integrity (I) | High | Broad modification |
| Availability (A) | Low | Degraded service |

#### Exploitability

**Score**: 5.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 6 | Described in research |
| Attack Complexity | 5 | Needs some preparation |
| Tooling Availability | 4 | Tools need adaptation |
| Skill Level | 5 | Intermediate skill |

#### Scalability

**Score**: 4.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 6 | Partly automatable |
| Target Scope | 2 | One specific target |
| Resource Requirements | 7 | Minimal resources |
| Detection Difficulty | 3 | Readily detected |

#### Reachability

**Score**: 2.0 | **Trust Zone**: Agent Runtime Zone (Trusted)

model-gateway sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 2.0.

---

### T-34 — scheduler-1

**Threat**: An update to scheduler-1 is pulled without provenance checks, so a poisoned package can alter how recurring planning triggers are handled at run time.

**Category**: tampering | **Original Risk Level**: Medium | **Composite**: 5.0 (Medium)

#### CVSS 3.1 Base

**Score**: 6.3 | **Vector**: `CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:N/I:H/A:L`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Network | Reachable over the network |
| Attack Complexity (AC) | Low | No special conditions |
| Privileges Required (PR) | Low | A basic account is needed |
| User Interaction (UI) | Required | A user must act |
| Scope (S) | Unchanged | Impact stays in the component |
| Confidentiality (C) | None | No disclosure |
| Integrity (I) | High | Broad modification |
| Availability (A) | Low | Degraded service |

#### Exploitability

**Score**: 4.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 4 | Described in research |
| Attack Complexity | 7 | A single step suffices |
| Tooling Availability | 4 | Tools need adaptation |
| Skill Level | 3 | Needs deep expertise |

#### Scalability

**Score**: 5.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 5 | Partly automatable |
| Target Scope | 4 | A class of targets |
| Resource Requirements | 8 | Minimal resources |
| Detection Difficulty | 5 | Detectable with monitoring |

#### Reachability

**Score**: 3.0 | **Trust Zone**: Agent Runtime Zone (Trusted)

scheduler-1 sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 3.0.

---

### I-8 — planner-agent

**Threat**: Backups of task plans and tool selections taken from planner-agent are stored unencrypted in a shared location that wider operations staff can read.

**Category**: info-disclosure | **Original Risk Level**: Note | **Composite**: 5.0 (Medium)

#### CVSS 3.1 Base

**Score**: 4.6 | **Vector**: `CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:C/C:L/I:N/A:L`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Local | Needs local access |
| Attack Complexity (AC) | Low | No special conditions |
| Privileges Required (PR) | High | Administrative rights are needed |
| User Interaction (UI) | None | No user action needed |
| Scope (S) | Changed | Impact crosses a boundary |
| Confidentiality (C) | Low | Limited disclosure |
| Integrity (I) | None | No modification |
| Availability (A) | Low | Degraded service |

#### Exploitability

**Score**: 6.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 7 | Documented and widely used |
| Attack Complexity | 6 | Needs some preparation |
| Tooling Availability | 6 | Tools need adaptation |
| Skill Level | 7 | Little skill needed |

#### Scalability

**Score**: 5.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 5 | Partly automatable |
| Target Scope | 6 | A class of targets |
| Resource Requirements | 7 | Minimal resources |
| Detection Difficulty | 4 | Detectable with monitoring |

#### Reachability

**Score**: 3.0 | **Trust Zone**: Agent Runtime Zone (Trusted)

planner-agent sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 3.0.

---

### I-36 — scheduler-1

**Threat**: Cross-tenant filters on scheduler-1 are applied in application code only, so one missing predicate exposes another tenant's recurring planning triggers.

**Category**: info-disclosure | **Original Risk Level**: High | **Composite**: 5.0 (Medium)

#### CVSS 3.1 Base

**Score**: 5.4 | **Vector**: `CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:N/A:L`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Network | Reachable over the network |
| Attack Complexity (AC) | Low | No special conditions |
| Privileges Required (PR) | None | No privileges needed |
| User Interaction (UI) | Required | A user must act |
| Scope (S) | Unchanged | Impact stays in the component |
| Confidentiality (C) | Low | Limited disclosure |
| Integrity (I) | None | No modification |
| Availability (A) | Low | Degraded service |

#### Exploitability

**Score**: 6.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 6 | Described in research |
| Attack Complexity | 5 | Needs some preparation |
| Tooling Availability | 7 | Common tools apply |
| Skill Level | 6 | Intermediate skill |

#### Scalability

**Score**: 6.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 7 | Fully automatable |
| Target Scope | 6 | A class of targets |
| Resource Requirements | 8 | Minimal resources |
| Detection Difficulty | 5 | Detectable with monitoring |

#### Reachability

**Score**: 1.5 | **Trust Zone**: Agent Runtime Zone (Trusted)

scheduler-1 sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 1.5.

---

### E-7 — intake-agent

**Threat**: An administrative interface of intake-agent is reachable from the same network as ordinary callers and relies on a single shared password.

**Category**: privilege-escalation | **Original Risk Level**: High | **Composite**: 5.0 (Medium)

#### CVSS 3.1 Base

**Score**: 6.8 | **Vector**: `CVSS:3.1/AV:A/AC:H/PR:H/UI:N/S:C/C:L/I:H/A:L`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Adjacent | Needs an adjacent network |
| Attack Complexity (AC) | High | Needs specific conditions |
| Privileges Required (PR) | High | Administrative rights are needed |
| User Interaction (UI) | None | No user action needed |
| Scope (S) | Changed | Impact crosses a boundary |
| Confidentiality (C) | Low | Limited disclosure |
| Integrity (I) | High | Broad modification |
| Availability (A) | Low | Degraded service |

#### Exploitability

**Score**: 4.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 6 | Described in research |
| Attack Complexity | 4 | Needs some preparation |
| Tooling Availability | 5 | Tools need adaptation |
| Skill Level | 3 | Needs deep expertise |

#### Scalability

**Score**: 4.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 4 | Partly automatable |
| Target Scope | 3 | One specific target |
| Resource Requirements | 6 | Moderate resources |
| Detection Difficulty | 5 | Detectable with monitoring |

#### Reachability

**Score**: 3.0 | **Trust Zone**: Agent Runtime Zone (Trusted)

intake-agent sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 3.0.

---

### TE-6 — intake-agent

**Threat**: intake-agent adopts a persona that presents itself as a named colleague, so operators trust its suggestions more than its accuracy warrants.

**Category**: agentic | **Original Risk Level**: Medium | **Composite**: 5.0 (Medium)

#### CVSS 3.1 Base

**Score**: 8.1 | **Vector**: `CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:C/C:L/I:H/A:H`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Local | Needs local access |
| Attack Complexity (AC) | Low | No special conditions |
| Privileges Required (PR) | High | Administrative rights are needed |
| User Interaction (UI) | None | No user action needed |
| Scope (S) | Changed | Impact crosses a boundary |
| Confidentiality (C) | Low | Limited disclosure |
| Integrity (I) | High | Broad modification |
| Availability (A) | High | Loss of service |

#### Exploitability

**Score**: 3.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 6 | Described in research |
| Attack Complexity | 3 | Needs chained steps |
| Tooling Availability | 2 | Needs custom tooling |
| Skill Level | 3 | Needs deep expertise |

#### Scalability

**Score**: 4.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 2 | Manual for each target |
| Target Scope | 4 | A class of targets |
| Resource Requirements | 6 | Moderate resources |
| Detection Difficulty | 6 | Detectable with monitoring |

#### Reachability

**Score**: 2.0 | **Trust Zone**: Agent Runtime Zone (Trusted)

intake-agent sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 2.0.

---

### S-26 — summarizer-llm

**Threat**: Low-entropy identifiers accepted by summarizer-llm double as credentials, so an attacker who enumerates them submits requests under a victim's identity.

**Category**: spoofing | **Original Risk Level**: High | **Composite**: 4.9 (Medium)

#### CVSS 3.1 Base

**Score**: 4.2 | **Vector**: `CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:L/I:L/A:N`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Network | Reachable over the network |
| Attack Complexity (AC) | High | Needs specific conditions |
| Privileges Required (PR) | None | No privileges needed |
| User Interaction (UI) | Required | A user must act |
| Scope (S) | Unchanged | Impact stays in the component |
| Confidentiality (C) | Low | Limited disclosure |
| Integrity (I) | Low | Limited modification |
| Availability (A) | None | No loss of service |

#### Exploitability

**Score**: 7.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 5 | Described in research |
| Attack Complexity | 7 | A single step suffices |
| Tooling Availability | 8 | Common tools apply |
| Skill Level | 8 | Little skill needed |

#### Scalability

**Score**: 6.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 9 | Fully automatable |
| Target Scope | 5 | A class of targets |
| Resource Requirements | 6 | Moderate resources |
| Detection Difficulty | 4 | Detectable with monitoring |

#### Reachability

**Score**: 2.0 | **Trust Zone**: Agent Runtime Zone (Trusted)

summarizer-llm sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 2.0.

---

### T-14 — embed-service-2

**Threat**: Replay of an earlier valid update to document chunks and query embeddings reaches embed-service-2 because updates carry no nonce or expiry, restoring a state the owner already corrected.

**Category**: tampering | **Original Risk Level**: High | **Composite**: 4.9 (Medium)

#### CVSS 3.1 Base

**Score**: 6.3 | **Vector**: `CVSS:3.1/AV:A/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:L`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Adjacent | Needs an adjacent network |
| Attack Complexity (AC) | Low | No special conditions |
| Privileges Required (PR) | Low | A basic account is needed |
| User Interaction (UI) | None | No user action needed |
| Scope (S) | Unchanged | Impact stays in the component |
| Confidentiality (C) | None | No disclosure |
| Integrity (I) | High | Broad modification |
| Availability (A) | Low | Degraded service |

#### Exploitability

**Score**: 4.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 4 | Described in research |
| Attack Complexity | 4 | Needs some preparation |
| Tooling Availability | 4 | Tools need adaptation |
| Skill Level | 6 | Intermediate skill |

#### Scalability

**Score**: 5.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 6 | Partly automatable |
| Target Scope | 5 | A class of targets |
| Resource Requirements | 5 | Moderate resources |
| Detection Difficulty | 4 | Detectable with monitoring |

#### Reachability

**Score**: 3.0 | **Trust Zone**: Agent Runtime Zone (Trusted)

embed-service-2 sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 3.0.

---

### T-15 — embed-service-2

**Threat**: Serialised objects arriving from intake-agent are deserialised by embed-service-2 with permissive type handling, allowing crafted payloads to instantiate unintended behaviour.

**Category**: tampering | **Original Risk Level**: Medium | **Composite**: 4.9 (Medium)

**Correlation Group**: Scores inherited from primary finding T-14 (CG-10). Dimensional detail is recorded on the primary.

**Score**: 6.3 | **Vector**: `CVSS:3.1/AV:A/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:L`

---

### T-44 — worker-2

**Threat**: An attacker who can write to the channel between trace-collector and worker-2 modifies work orders and route candidates in transit because messages carry no integrity protection of their own.

**Category**: tampering | **Original Risk Level**: Low | **Composite**: 4.9 (Medium)

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

**Score**: 4.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 6 | Described in research |
| Attack Complexity | 5 | Needs some preparation |
| Tooling Availability | 4 | Tools need adaptation |
| Skill Level | 3 | Needs deep expertise |

#### Scalability

**Score**: 5.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 6 | Partly automatable |
| Target Scope | 2 | One specific target |
| Resource Requirements | 7 | Minimal resources |
| Detection Difficulty | 5 | Detectable with monitoring |

#### Reachability

**Score**: 1.5 | **Trust Zone**: Agent Runtime Zone (Trusted)

worker-2 sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 1.5.

---

### I-23 — embed-service-2

**Threat**: Secrets such as the service credential for embed-service-2 appear in process arguments and environment dumps that diagnostic tooling captures.

**Category**: info-disclosure | **Original Risk Level**: Low | **Composite**: 4.9 (Medium)

#### CVSS 3.1 Base

**Score**: 5.5 | **Vector**: `CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:N`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Local | Needs local access |
| Attack Complexity (AC) | Low | No special conditions |
| Privileges Required (PR) | None | No privileges needed |
| User Interaction (UI) | Required | A user must act |
| Scope (S) | Unchanged | Impact stays in the component |
| Confidentiality (C) | High | Broad disclosure |
| Integrity (I) | None | No modification |
| Availability (A) | None | No loss of service |

#### Exploitability

**Score**: 5.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 6 | Described in research |
| Attack Complexity | 5 | Needs some preparation |
| Tooling Availability | 5 | Tools need adaptation |
| Skill Level | 6 | Intermediate skill |

#### Scalability

**Score**: 5.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 6 | Partly automatable |
| Target Scope | 5 | A class of targets |
| Resource Requirements | 9 | Minimal resources |
| Detection Difficulty | 2 | Readily detected |

#### Reachability

**Score**: 2.5 | **Trust Zone**: Agent Runtime Zone (Trusted)

embed-service-2 sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 2.5.

---

### I-30 — memory-store

**Threat**: Cross-tenant filters on memory-store are applied in application code only, so one missing predicate exposes another tenant's task history and operator preferences.

**Category**: info-disclosure | **Original Risk Level**: Medium | **Composite**: 4.9 (Medium)

#### CVSS 3.1 Base

**Score**: 4.6 | **Vector**: `CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:L/I:L/A:N`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Network | Reachable over the network |
| Attack Complexity (AC) | Low | No special conditions |
| Privileges Required (PR) | Low | A basic account is needed |
| User Interaction (UI) | Required | A user must act |
| Scope (S) | Unchanged | Impact stays in the component |
| Confidentiality (C) | Low | Limited disclosure |
| Integrity (I) | Low | Limited modification |
| Availability (A) | None | No loss of service |

#### Exploitability

**Score**: 7.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 8 | Documented and widely used |
| Attack Complexity | 8 | A single step suffices |
| Tooling Availability | 6 | Tools need adaptation |
| Skill Level | 8 | Little skill needed |

#### Scalability

**Score**: 5.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 5 | Partly automatable |
| Target Scope | 4 | A class of targets |
| Resource Requirements | 6 | Moderate resources |
| Detection Difficulty | 5 | Detectable with monitoring |

#### Reachability

**Score**: 1.5 | **Trust Zone**: Data Zone (Trusted)

memory-store sits in the Data Zone. The zone baseline is 2.5 and the refinement for this finding gives 1.5.

---

### D-37 — worker-2

**Threat**: A slow-read attack holds connections to worker-2 open and ties up the workers handling work orders and route candidates until none remain for real requests.

**Category**: denial-of-service | **Original Risk Level**: Low | **Composite**: 4.9 (Medium)

#### CVSS 3.1 Base

**Score**: 4.2 | **Vector**: `CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:L/I:N/A:L`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Network | Reachable over the network |
| Attack Complexity (AC) | High | Needs specific conditions |
| Privileges Required (PR) | None | No privileges needed |
| User Interaction (UI) | Required | A user must act |
| Scope (S) | Unchanged | Impact stays in the component |
| Confidentiality (C) | Low | Limited disclosure |
| Integrity (I) | None | No modification |
| Availability (A) | Low | Degraded service |

#### Exploitability

**Score**: 7.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 7 | Documented and widely used |
| Attack Complexity | 6 | Needs some preparation |
| Tooling Availability | 6 | Tools need adaptation |
| Skill Level | 9 | Little skill needed |

#### Scalability

**Score**: 5.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 7 | Fully automatable |
| Target Scope | 8 | Every instance |
| Resource Requirements | 3 | Needs heavy infrastructure |
| Detection Difficulty | 4 | Detectable with monitoring |

#### Reachability

**Score**: 2.5 | **Trust Zone**: Agent Runtime Zone (Trusted)

worker-2 sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 2.5.

---

### LLM-22 — embed-service-2

**Threat**: Records written into embed-service-2 by low-trust sources are later used as ground truth, so an attacker who plants entries shifts model answers.

**Category**: llm | **Original Risk Level**: Medium | **Composite**: 4.9 (Medium)

**Correlation Group**: Scores inherited from primary finding T-14 (CG-10). Dimensional detail is recorded on the primary.

**Score**: 6.3 | **Vector**: `CVSS:3.1/AV:A/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:L`

---

### T-36 — trace-collector

**Threat**: An update to trace-collector is pulled without provenance checks, so a poisoned package can alter how prompts, completions and tool traces are handled at run time.

**Category**: tampering | **Original Risk Level**: High | **Composite**: 4.8 (Medium)

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
| Known Techniques | 7 | Documented and widely used |
| Attack Complexity | 7 | A single step suffices |
| Tooling Availability | 6 | Tools need adaptation |
| Skill Level | 6 | Intermediate skill |

#### Scalability

**Score**: 5.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 6 | Partly automatable |
| Target Scope | 2 | One specific target |
| Resource Requirements | 7 | Minimal resources |
| Detection Difficulty | 5 | Detectable with monitoring |

#### Reachability

**Score**: 1.5 | **Trust Zone**: Operations Zone (Trusted)

trace-collector sits in the Operations Zone. The zone baseline is 2.5 and the refinement for this finding gives 1.5.

---

### I-26 — vector-store-a

**Threat**: Logs and traces emitted by vector-store-a include raw embedded documents and metadata, so anyone with access to the logging pipeline can read content meant for one tenant.

**Category**: info-disclosure | **Original Risk Level**: Medium | **Composite**: 4.8 (Medium)

#### CVSS 3.1 Base

**Score**: 3.5 | **Vector**: `CVSS:3.1/AV:A/AC:L/PR:H/UI:N/S:U/C:L/I:L/A:N`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Adjacent | Needs an adjacent network |
| Attack Complexity (AC) | Low | No special conditions |
| Privileges Required (PR) | High | Administrative rights are needed |
| User Interaction (UI) | None | No user action needed |
| Scope (S) | Unchanged | Impact stays in the component |
| Confidentiality (C) | Low | Limited disclosure |
| Integrity (I) | Low | Limited modification |
| Availability (A) | None | No loss of service |

#### Exploitability

**Score**: 7.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 7 | Documented and widely used |
| Attack Complexity | 8 | A single step suffices |
| Tooling Availability | 6 | Tools need adaptation |
| Skill Level | 7 | Little skill needed |

#### Scalability

**Score**: 6.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 8 | Fully automatable |
| Target Scope | 6 | A class of targets |
| Resource Requirements | 8 | Minimal resources |
| Detection Difficulty | 4 | Detectable with monitoring |

#### Reachability

**Score**: 2.5 | **Trust Zone**: Data Zone (Trusted)

vector-store-a sits in the Data Zone. The zone baseline is 2.5 and the refinement for this finding gives 2.5.

---

### I-37 — trace-collector

**Threat**: Logs and traces emitted by trace-collector include raw prompts, completions and tool traces, so anyone with access to the logging pipeline can read content meant for one tenant.

**Category**: info-disclosure | **Original Risk Level**: Low | **Composite**: 4.8 (Medium)

**Correlation Group**: Scores inherited from primary finding T-36 (CG-19). Dimensional detail is recorded on the primary.

**Score**: 5.2 | **Vector**: `CVSS:3.1/AV:N/AC:L/PR:H/UI:R/S:U/C:N/I:H/A:L`

---

### I-38 — trace-collector

**Threat**: Data in transit between planner-agent and trace-collector is protected only on the outer hop, which leaves prompts, completions and tool traces readable on the internal segment after termination.

**Category**: info-disclosure | **Original Risk Level**: Note | **Composite**: 4.8 (Medium)

**Correlation Group**: Scores inherited from primary finding T-36 (CG-19). Dimensional detail is recorded on the primary.

**Score**: 5.2 | **Vector**: `CVSS:3.1/AV:N/AC:L/PR:H/UI:R/S:U/C:N/I:H/A:L`

---

### AGP-01 — planner-agent

**Threat**: Interacting planning and routing agents amplify each other's outputs through feedback until their combined behaviour diverges from what any single agent was tested for, and per-agent safety checks never see the divergence.

**Category**: agentic | **Original Risk Level**: Medium | **Composite**: 4.8 (Medium)

#### CVSS 3.1 Base

**Score**: 6.4 | **Vector**: `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:L/I:L/A:N`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Network | Reachable over the network |
| Attack Complexity (AC) | Low | No special conditions |
| Privileges Required (PR) | Low | A basic account is needed |
| User Interaction (UI) | None | No user action needed |
| Scope (S) | Changed | Impact crosses a boundary |
| Confidentiality (C) | Low | Limited disclosure |
| Integrity (I) | Low | Limited modification |
| Availability (A) | None | No loss of service |

#### Exploitability

**Score**: 4.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 6 | Described in research |
| Attack Complexity | 5 | Needs some preparation |
| Tooling Availability | 2 | Needs custom tooling |
| Skill Level | 5 | Intermediate skill |

#### Scalability

**Score**: 4.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 2 | Manual for each target |
| Target Scope | 3 | One specific target |
| Resource Requirements | 6 | Moderate resources |
| Detection Difficulty | 7 | Blends with normal use |

#### Reachability

**Score**: 2.5 | **Trust Zone**: Agent Runtime Zone (Trusted)

planner-agent sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 2.5.

---

### LLM-40 — trace-collector

**Threat**: Instructions hidden in prompts, completions and tool traces reach the prompt of trace-collector and override its system guidance, because content and instructions share one context.

**Category**: llm | **Original Risk Level**: Critical | **Composite**: 4.8 (Medium)

**Correlation Group**: Scores inherited from primary finding T-36 (CG-19). Dimensional detail is recorded on the primary.

**Score**: 5.2 | **Vector**: `CVSS:3.1/AV:N/AC:L/PR:H/UI:R/S:U/C:N/I:H/A:L`

---

### LLM-42 — trace-collector

**Threat**: Evaluation labels consumed from trace-collector are produced by a judge model that can itself be influenced by planted traces.

**Category**: llm | **Original Risk Level**: Low | **Composite**: 4.8 (Medium)

**Correlation Group**: Scores inherited from primary finding T-36 (CG-19). Dimensional detail is recorded on the primary.

**Score**: 5.2 | **Vector**: `CVSS:3.1/AV:N/AC:L/PR:H/UI:R/S:U/C:N/I:H/A:L`

---

### S-17 — worker-3

**Threat**: A compromised peer presents a forged service identity to worker-3, and worker-3 accepts the claim without verifying the signature chain back to the issuing authority.

**Category**: spoofing | **Original Risk Level**: High | **Composite**: 4.7 (Medium)

#### CVSS 3.1 Base

**Score**: 4.8 | **Vector**: `CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:L/A:N`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Network | Reachable over the network |
| Attack Complexity (AC) | High | Needs specific conditions |
| Privileges Required (PR) | None | No privileges needed |
| User Interaction (UI) | None | No user action needed |
| Scope (S) | Unchanged | Impact stays in the component |
| Confidentiality (C) | Low | Limited disclosure |
| Integrity (I) | Low | Limited modification |
| Availability (A) | None | No loss of service |

#### Exploitability

**Score**: 5.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 5 | Described in research |
| Attack Complexity | 8 | A single step suffices |
| Tooling Availability | 5 | Tools need adaptation |
| Skill Level | 4 | Intermediate skill |

#### Scalability

**Score**: 6.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 6 | Partly automatable |
| Target Scope | 6 | A class of targets |
| Resource Requirements | 8 | Minimal resources |
| Detection Difficulty | 6 | Detectable with monitoring |

#### Reachability

**Score**: 2.0 | **Trust Zone**: Agent Runtime Zone (Trusted)

worker-3 sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 2.0.

---

### S-19 — tool-server-1

**Threat**: An unauthenticated callback or health route on tool-server-1 accepts requests that downstream code treats as if they had come from worker-2.

**Category**: spoofing | **Original Risk Level**: Low | **Composite**: 4.7 (Medium)

#### CVSS 3.1 Base

**Score**: 4.2 | **Vector**: `CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:L/I:L/A:N`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Network | Reachable over the network |
| Attack Complexity (AC) | High | Needs specific conditions |
| Privileges Required (PR) | None | No privileges needed |
| User Interaction (UI) | Required | A user must act |
| Scope (S) | Unchanged | Impact stays in the component |
| Confidentiality (C) | Low | Limited disclosure |
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

**Score**: 6.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 9 | Fully automatable |
| Target Scope | 6 | A class of targets |
| Resource Requirements | 6 | Moderate resources |
| Detection Difficulty | 5 | Detectable with monitoring |

#### Reachability

**Score**: 1.5 | **Trust Zone**: Agent Runtime Zone (Trusted)

tool-server-1 sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 1.5.

---

### S-34 — trace-collector

**Threat**: An unauthenticated callback or health route on trace-collector accepts requests that downstream code treats as if they had come from intake-agent.

**Category**: spoofing | **Original Risk Level**: Note | **Composite**: 4.7 (Medium)

#### CVSS 3.1 Base

**Score**: 4.6 | **Vector**: `CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:L/I:L/A:N`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Network | Reachable over the network |
| Attack Complexity (AC) | Low | No special conditions |
| Privileges Required (PR) | Low | A basic account is needed |
| User Interaction (UI) | Required | A user must act |
| Scope (S) | Unchanged | Impact stays in the component |
| Confidentiality (C) | Low | Limited disclosure |
| Integrity (I) | Low | Limited modification |
| Availability (A) | None | No loss of service |

#### Exploitability

**Score**: 6.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 5 | Described in research |
| Attack Complexity | 8 | A single step suffices |
| Tooling Availability | 6 | Tools need adaptation |
| Skill Level | 5 | Intermediate skill |

#### Scalability

**Score**: 5.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 6 | Partly automatable |
| Target Scope | 4 | A class of targets |
| Resource Requirements | 7 | Minimal resources |
| Detection Difficulty | 5 | Detectable with monitoring |

#### Reachability

**Score**: 2.5 | **Trust Zone**: Operations Zone (Trusted)

trace-collector sits in the Operations Zone. The zone baseline is 2.5 and the refinement for this finding gives 2.5.

---

### T-27 — s3-archive

**Threat**: Serialised objects arriving from kb-index are deserialised by s3-archive with permissive type handling, allowing crafted payloads to instantiate unintended behaviour.

**Category**: tampering | **Original Risk Level**: Critical | **Composite**: 4.7 (Medium)

#### CVSS 3.1 Base

**Score**: 6.3 | **Vector**: `CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:N/I:H/A:L`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Network | Reachable over the network |
| Attack Complexity (AC) | Low | No special conditions |
| Privileges Required (PR) | Low | A basic account is needed |
| User Interaction (UI) | Required | A user must act |
| Scope (S) | Unchanged | Impact stays in the component |
| Confidentiality (C) | None | No disclosure |
| Integrity (I) | High | Broad modification |
| Availability (A) | Low | Degraded service |

#### Exploitability

**Score**: 4.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 5 | Described in research |
| Attack Complexity | 7 | A single step suffices |
| Tooling Availability | 3 | Needs custom tooling |
| Skill Level | 3 | Needs deep expertise |

#### Scalability

**Score**: 5.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 6 | Partly automatable |
| Target Scope | 3 | One specific target |
| Resource Requirements | 5 | Moderate resources |
| Detection Difficulty | 6 | Detectable with monitoring |

#### Reachability

**Score**: 2.0 | **Trust Zone**: Data Zone (Trusted)

s3-archive sits in the Data Zone. The zone baseline is 2.5 and the refinement for this finding gives 2.0.

---

### T-28 — s3-archive

**Threat**: Backups and exports of archived transcripts and training corpora on s3-archive are writable by operators without a second approver, so a malicious change survives restores.

**Category**: tampering | **Original Risk Level**: Low | **Composite**: 4.7 (Medium)

**Correlation Group**: Scores inherited from primary finding T-27 (CG-15). Dimensional detail is recorded on the primary.

**Score**: 6.3 | **Vector**: `CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:N/I:H/A:L`

---

### I-13 — worker-2

**Threat**: Logs and traces emitted by worker-2 include raw work orders and route candidates, so anyone with access to the logging pipeline can read content meant for one tenant.

**Category**: info-disclosure | **Original Risk Level**: Medium | **Composite**: 4.7 (Medium)

#### CVSS 3.1 Base

**Score**: 3.8 | **Vector**: `CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:L/I:N/A:L`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Network | Reachable over the network |
| Attack Complexity (AC) | Low | No special conditions |
| Privileges Required (PR) | High | Administrative rights are needed |
| User Interaction (UI) | None | No user action needed |
| Scope (S) | Unchanged | Impact stays in the component |
| Confidentiality (C) | Low | Limited disclosure |
| Integrity (I) | None | No modification |
| Availability (A) | Low | Degraded service |

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
| Scriptability | 5 | Partly automatable |
| Target Scope | 7 | Every instance |
| Resource Requirements | 6 | Moderate resources |
| Detection Difficulty | 6 | Detectable with monitoring |

#### Reachability

**Score**: 2.0 | **Trust Zone**: Agent Runtime Zone (Trusted)

worker-2 sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 2.0.

---

### I-18 — tool-server-1

**Threat**: Verbose error responses from tool-server-1 reveal internal paths, query text and identifiers of tool call arguments and results to any caller who can trigger a failure.

**Category**: info-disclosure | **Original Risk Level**: Medium | **Composite**: 4.7 (Medium)

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

**Score**: 5.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 6 | Described in research |
| Attack Complexity | 6 | Needs some preparation |
| Tooling Availability | 4 | Tools need adaptation |
| Skill Level | 4 | Intermediate skill |

#### Scalability

**Score**: 6.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 7 | Fully automatable |
| Target Scope | 6 | A class of targets |
| Resource Requirements | 9 | Minimal resources |
| Detection Difficulty | 4 | Detectable with monitoring |

#### Reachability

**Score**: 1.5 | **Trust Zone**: Agent Runtime Zone (Trusted)

tool-server-1 sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 1.5.

---

### I-21 — model-gateway

**Threat**: Secrets such as the model API key for model-gateway appear in process arguments and environment dumps that diagnostic tooling captures.

**Category**: info-disclosure | **Original Risk Level**: Medium | **Composite**: 4.7 (Medium)

#### CVSS 3.1 Base

**Score**: 4.5 | **Vector**: `CVSS:3.1/AV:N/AC:L/PR:H/UI:R/S:U/C:H/I:N/A:N`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Network | Reachable over the network |
| Attack Complexity (AC) | Low | No special conditions |
| Privileges Required (PR) | High | Administrative rights are needed |
| User Interaction (UI) | Required | A user must act |
| Scope (S) | Unchanged | Impact stays in the component |
| Confidentiality (C) | High | Broad disclosure |
| Integrity (I) | None | No modification |
| Availability (A) | None | No loss of service |

#### Exploitability

**Score**: 5.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 8 | Documented and widely used |
| Attack Complexity | 5 | Needs some preparation |
| Tooling Availability | 4 | Tools need adaptation |
| Skill Level | 5 | Intermediate skill |

#### Scalability

**Score**: 6.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 10 | Fully automatable |
| Target Scope | 5 | A class of targets |
| Resource Requirements | 6 | Moderate resources |
| Detection Difficulty | 3 | Readily detected |

#### Reachability

**Score**: 3.0 | **Trust Zone**: Agent Runtime Zone (Trusted)

model-gateway sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 3.0.

---

### I-22 — model-gateway

**Threat**: Verbose error responses from model-gateway reveal internal paths, query text and identifiers of prompts and completions to any caller who can trigger a failure.

**Category**: info-disclosure | **Original Risk Level**: High | **Composite**: 4.7 (Medium)

#### CVSS 3.1 Base

**Score**: 4.2 | **Vector**: `CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:L/I:L/A:N`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Network | Reachable over the network |
| Attack Complexity (AC) | High | Needs specific conditions |
| Privileges Required (PR) | Low | A basic account is needed |
| User Interaction (UI) | None | No user action needed |
| Scope (S) | Unchanged | Impact stays in the component |
| Confidentiality (C) | Low | Limited disclosure |
| Integrity (I) | Low | Limited modification |
| Availability (A) | None | No loss of service |

#### Exploitability

**Score**: 5.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 6 | Described in research |
| Attack Complexity | 5 | Needs some preparation |
| Tooling Availability | 6 | Tools need adaptation |
| Skill Level | 5 | Intermediate skill |

#### Scalability

**Score**: 6.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 5 | Partly automatable |
| Target Scope | 7 | Every instance |
| Resource Requirements | 9 | Minimal resources |
| Detection Difficulty | 5 | Detectable with monitoring |

#### Reachability

**Score**: 3.0 | **Trust Zone**: Agent Runtime Zone (Trusted)

model-gateway sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 3.0.

---

### I-29 — memory-store

**Threat**: Backups of task history and operator preferences taken from memory-store are stored unencrypted in a shared location that wider operations staff can read.

**Category**: info-disclosure | **Original Risk Level**: Low | **Composite**: 4.7 (Medium)

#### CVSS 3.1 Base

**Score**: 4.9 | **Vector**: `CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:N/A:N`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Network | Reachable over the network |
| Attack Complexity (AC) | Low | No special conditions |
| Privileges Required (PR) | High | Administrative rights are needed |
| User Interaction (UI) | None | No user action needed |
| Scope (S) | Unchanged | Impact stays in the component |
| Confidentiality (C) | High | Broad disclosure |
| Integrity (I) | None | No modification |
| Availability (A) | None | No loss of service |

#### Exploitability

**Score**: 5.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 5 | Described in research |
| Attack Complexity | 5 | Needs some preparation |
| Tooling Availability | 7 | Common tools apply |
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

**Score**: 3.0 | **Trust Zone**: Data Zone (Trusted)

memory-store sits in the Data Zone. The zone baseline is 2.5 and the refinement for this finding gives 3.0.

---

### D-10 — worker-2

**Threat**: Retry storms from tool-server-1 multiply the load on worker-2 when it slows down, turning a brief delay into a sustained outage.

**Category**: denial-of-service | **Original Risk Level**: Low | **Composite**: 4.7 (Medium)

**Correlation Group**: Scores inherited from primary finding I-13 (CG-5). Dimensional detail is recorded on the primary.

**Score**: 3.8 | **Vector**: `CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:L/I:N/A:L`

---

### E-12 — worker-2

**Threat**: Role claims carried in the worker credential presented to worker-2 are honoured without confirmation against the authoritative directory.

**Category**: privilege-escalation | **Original Risk Level**: High | **Composite**: 4.7 (Medium)

**Correlation Group**: Scores inherited from primary finding I-13 (CG-5). Dimensional detail is recorded on the primary.

**Score**: 3.8 | **Vector**: `CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:L/I:N/A:L`

---

### AG-15 — worker-2

**Threat**: worker-2 retries failed actions on its own, repeating side effects such as bookings or messages when the first attempt partly succeeded.

**Category**: agentic | **Original Risk Level**: Medium | **Composite**: 4.7 (Medium)

**Correlation Group**: Scores inherited from primary finding I-13 (CG-5). Dimensional detail is recorded on the primary.

**Score**: 3.8 | **Vector**: `CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:L/I:N/A:L`

---

### AG-16 — worker-2

**Threat**: worker-2 can start further agents or processes on request, so a compromised prompt can multiply its reach beyond the intended scope.

**Category**: agentic | **Original Risk Level**: High | **Composite**: 4.7 (Medium)

**Correlation Group**: Scores inherited from primary finding I-13 (CG-5). Dimensional detail is recorded on the primary.

**Score**: 3.8 | **Vector**: `CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:L/I:N/A:L`

---

### AG-19 — worker-2

**Threat**: Tool calls made by worker-2 are not tied to the end user, so the tool server cannot tell whose authority a request carries.

**Category**: agentic | **Original Risk Level**: High | **Composite**: 4.7 (Medium)

**Correlation Group**: Scores inherited from primary finding I-13 (CG-5). Dimensional detail is recorded on the primary.

**Score**: 3.8 | **Vector**: `CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:L/I:N/A:L`

---

### LLM-13 — worker-2

**Threat**: worker-2 follows links and files named in work orders and route candidates, which turns a harmless-looking request into a fetch of attacker-controlled content.

**Category**: llm | **Original Risk Level**: Medium | **Composite**: 4.7 (Medium)

**Correlation Group**: Scores inherited from primary finding I-13 (CG-5). Dimensional detail is recorded on the primary.

**Score**: 3.8 | **Vector**: `CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:L/I:N/A:L`

---

### LLM-37 — s3-archive

**Threat**: A delayed trigger planted in archived transcripts and training corpora on s3-archive changes behaviour only after a date or phrase, so pre-release testing never sees it.

**Category**: llm | **Original Risk Level**: High | **Composite**: 4.7 (Medium)

**Correlation Group**: Scores inherited from primary finding T-27 (CG-15). Dimensional detail is recorded on the primary.

**Score**: 6.3 | **Vector**: `CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:N/I:H/A:L`

---

### LLM-38 — s3-archive

**Threat**: Records written into s3-archive by low-trust sources are later used as ground truth, so an attacker who plants entries shifts model answers.

**Category**: llm | **Original Risk Level**: Critical | **Composite**: 4.7 (Medium)

**Correlation Group**: Scores inherited from primary finding T-27 (CG-15). Dimensional detail is recorded on the primary.

**Score**: 6.3 | **Vector**: `CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:N/I:H/A:L`

---

### TE-16 — intake-agent

**Threat**: Persuasive phrasing from intake-agent pushes operators to approve proposals quickly, which reduces careful review.

**Category**: agentic | **Original Risk Level**: High | **Composite**: 4.7 (Medium)

#### CVSS 3.1 Base

**Score**: 6.0 | **Vector**: `CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:C/C:L/I:L/A:L`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Network | Reachable over the network |
| Attack Complexity (AC) | High | Needs specific conditions |
| Privileges Required (PR) | Low | A basic account is needed |
| User Interaction (UI) | None | No user action needed |
| Scope (S) | Changed | Impact crosses a boundary |
| Confidentiality (C) | Low | Limited disclosure |
| Integrity (I) | Low | Limited modification |
| Availability (A) | Low | Degraded service |

#### Exploitability

**Score**: 5.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 5 | Described in research |
| Attack Complexity | 4 | Needs some preparation |
| Tooling Availability | 5 | Tools need adaptation |
| Skill Level | 6 | Intermediate skill |

#### Scalability

**Score**: 5.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 3 | Manual for each target |
| Target Scope | 3 | One specific target |
| Resource Requirements | 9 | Minimal resources |
| Detection Difficulty | 7 | Blends with normal use |

#### Reachability

**Score**: 1.5 | **Trust Zone**: Agent Runtime Zone (Trusted)

intake-agent sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 1.5.

---

### S-28 — summarizer-llm

**Threat**: A compromised peer presents a forged service identity to summarizer-llm, and summarizer-llm accepts the claim without verifying the signature chain back to the issuing authority.

**Category**: spoofing | **Original Risk Level**: Low | **Composite**: 4.6 (Medium)

#### CVSS 3.1 Base

**Score**: 5.4 | **Vector**: `CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:C/C:L/I:L/A:N`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Network | Reachable over the network |
| Attack Complexity (AC) | High | Needs specific conditions |
| Privileges Required (PR) | None | No privileges needed |
| User Interaction (UI) | None | No user action needed |
| Scope (S) | Changed | Impact crosses a boundary |
| Confidentiality (C) | Low | Limited disclosure |
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

**Score**: 6.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 7 | Fully automatable |
| Target Scope | 6 | A class of targets |
| Resource Requirements | 7 | Minimal resources |
| Detection Difficulty | 4 | Detectable with monitoring |

#### Reachability

**Score**: 1.5 | **Trust Zone**: Agent Runtime Zone (Trusted)

summarizer-llm sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 1.5.

---

### T-5 — planner-agent

**Threat**: An attacker who can write to the channel between policy-engine and planner-agent modifies task plans and tool selections in transit because messages carry no integrity protection of their own.

**Category**: tampering | **Original Risk Level**: Medium | **Composite**: 4.6 (Medium)

#### CVSS 3.1 Base

**Score**: 6.3 | **Vector**: `CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:N/I:H/A:L`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Network | Reachable over the network |
| Attack Complexity (AC) | Low | No special conditions |
| Privileges Required (PR) | Low | A basic account is needed |
| User Interaction (UI) | Required | A user must act |
| Scope (S) | Unchanged | Impact stays in the component |
| Confidentiality (C) | None | No disclosure |
| Integrity (I) | High | Broad modification |
| Availability (A) | Low | Degraded service |

#### Exploitability

**Score**: 4.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 4 | Described in research |
| Attack Complexity | 5 | Needs some preparation |
| Tooling Availability | 3 | Needs custom tooling |
| Skill Level | 6 | Intermediate skill |

#### Scalability

**Score**: 5.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 5 | Partly automatable |
| Target Scope | 5 | A class of targets |
| Resource Requirements | 7 | Minimal resources |
| Detection Difficulty | 3 | Readily detected |

#### Reachability

**Score**: 1.5 | **Trust Zone**: Agent Runtime Zone (Trusted)

planner-agent sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 1.5.

---

### T-21 — vector-store-a

**Threat**: Backups and exports of embedded documents and metadata on vector-store-a are writable by operators without a second approver, so a malicious change survives restores.

**Category**: tampering | **Original Risk Level**: Medium | **Composite**: 4.6 (Medium)

#### CVSS 3.1 Base

**Score**: 6.3 | **Vector**: `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:L`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Network | Reachable over the network |
| Attack Complexity (AC) | Low | No special conditions |
| Privileges Required (PR) | Low | A basic account is needed |
| User Interaction (UI) | None | No user action needed |
| Scope (S) | Unchanged | Impact stays in the component |
| Confidentiality (C) | Low | Limited disclosure |
| Integrity (I) | Low | Limited modification |
| Availability (A) | Low | Degraded service |

#### Exploitability

**Score**: 4.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 4 | Described in research |
| Attack Complexity | 6 | Needs some preparation |
| Tooling Availability | 3 | Needs custom tooling |
| Skill Level | 3 | Needs deep expertise |

#### Scalability

**Score**: 4.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 6 | Partly automatable |
| Target Scope | 2 | One specific target |
| Resource Requirements | 5 | Moderate resources |
| Detection Difficulty | 3 | Readily detected |

#### Reachability

**Score**: 3.0 | **Trust Zone**: Data Zone (Trusted)

vector-store-a sits in the Data Zone. The zone baseline is 2.5 and the refinement for this finding gives 3.0.

---

### T-47 — eval-runner

**Threat**: Unsanitised replayed traces and judge verdicts reach eval-runner and are processed as trusted structure, so crafted input changes how later steps interpret the record.

**Category**: tampering | **Original Risk Level**: Medium | **Composite**: 4.6 (Medium)

#### CVSS 3.1 Base

**Score**: 5.4 | **Vector**: `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:L`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Network | Reachable over the network |
| Attack Complexity (AC) | Low | No special conditions |
| Privileges Required (PR) | Low | A basic account is needed |
| User Interaction (UI) | None | No user action needed |
| Scope (S) | Unchanged | Impact stays in the component |
| Confidentiality (C) | None | No disclosure |
| Integrity (I) | Low | Limited modification |
| Availability (A) | Low | Degraded service |

#### Exploitability

**Score**: 5.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 5 | Described in research |
| Attack Complexity | 7 | A single step suffices |
| Tooling Availability | 4 | Tools need adaptation |
| Skill Level | 6 | Intermediate skill |

#### Scalability

**Score**: 5.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 6 | Partly automatable |
| Target Scope | 3 | One specific target |
| Resource Requirements | 6 | Moderate resources |
| Detection Difficulty | 5 | Detectable with monitoring |

#### Reachability

**Score**: 1.5 | **Trust Zone**: Operations Zone (Trusted)

eval-runner sits in the Operations Zone. The zone baseline is 2.5 and the refinement for this finding gives 1.5.

---

### I-19 — model-gateway

**Threat**: Cross-tenant filters on model-gateway are applied in application code only, so one missing predicate exposes another tenant's prompts and completions.

**Category**: info-disclosure | **Original Risk Level**: Low | **Composite**: 4.6 (Medium)

#### CVSS 3.1 Base

**Score**: 5.5 | **Vector**: `CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:N/A:L`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Network | Reachable over the network |
| Attack Complexity (AC) | Low | No special conditions |
| Privileges Required (PR) | High | Administrative rights are needed |
| User Interaction (UI) | None | No user action needed |
| Scope (S) | Unchanged | Impact stays in the component |
| Confidentiality (C) | High | Broad disclosure |
| Integrity (I) | None | No modification |
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

**Score**: 5.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 8 | Fully automatable |
| Target Scope | 4 | A class of targets |
| Resource Requirements | 7 | Minimal resources |
| Detection Difficulty | 3 | Readily detected |

#### Reachability

**Score**: 2.5 | **Trust Zone**: Agent Runtime Zone (Trusted)

model-gateway sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 2.5.

---

### I-32 — feature-store-2

**Threat**: Secrets such as the pipeline credential for feature-store-2 appear in process arguments and environment dumps that diagnostic tooling captures.

**Category**: info-disclosure | **Original Risk Level**: Medium | **Composite**: 4.6 (Medium)

#### CVSS 3.1 Base

**Score**: 4.4 | **Vector**: `CVSS:3.1/AV:N/AC:H/PR:H/UI:N/S:U/C:H/I:N/A:N`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Network | Reachable over the network |
| Attack Complexity (AC) | High | Needs specific conditions |
| Privileges Required (PR) | High | Administrative rights are needed |
| User Interaction (UI) | None | No user action needed |
| Scope (S) | Unchanged | Impact stays in the component |
| Confidentiality (C) | High | Broad disclosure |
| Integrity (I) | None | No modification |
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

**Score**: 6.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 7 | Fully automatable |
| Target Scope | 5 | A class of targets |
| Resource Requirements | 9 | Minimal resources |
| Detection Difficulty | 5 | Detectable with monitoring |

#### Reachability

**Score**: 2.0 | **Trust Zone**: Data Zone (Trusted)

feature-store-2 sits in the Data Zone. The zone baseline is 2.5 and the refinement for this finding gives 2.0.

---

### LLM-19 — model-gateway

**Threat**: Indirect injection through documents retrieved for model-gateway lets the author of a retrieved page steer the answer without ever talking to the system.

**Category**: llm | **Original Risk Level**: Critical | **Composite**: 4.6 (Medium)

**Correlation Group**: Scores inherited from primary finding I-19 (CG-9). Dimensional detail is recorded on the primary.

**Score**: 5.5 | **Vector**: `CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:N/A:L`

---

### LLM-54 — model-gateway

**Threat**: Encoded or multilingual payloads bypass the keyword filter in front of model-gateway, which only checks plain English text.

**Category**: llm | **Original Risk Level**: High | **Composite**: 4.6 (Medium)

**Correlation Group**: Scores inherited from primary finding I-19 (CG-9). Dimensional detail is recorded on the primary.

**Score**: 5.5 | **Vector**: `CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:N/A:L`

---

### T-6 — worker-3

**Threat**: An attacker who can write to the channel between tool-server-1 and worker-3 modifies work orders and draft documents in transit because messages carry no integrity protection of their own.

**Category**: tampering | **Original Risk Level**: Low | **Composite**: 4.5 (Medium)

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

**Score**: 4.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 5 | Described in research |
| Attack Complexity | 4 | Needs some preparation |
| Tooling Availability | 3 | Needs custom tooling |
| Skill Level | 6 | Intermediate skill |

#### Scalability

**Score**: 4.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 4 | Partly automatable |
| Target Scope | 3 | One specific target |
| Resource Requirements | 5 | Moderate resources |
| Detection Difficulty | 6 | Detectable with monitoring |

#### Reachability

**Score**: 2.0 | **Trust Zone**: Agent Runtime Zone (Trusted)

worker-3 sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 2.0.

---

### R-18 — reviewer-agent

**Threat**: Delegated actions performed by reviewer-agent on behalf of a user are recorded under the service identity alone, hiding who authorised them.

**Category**: repudiation | **Original Risk Level**: Medium | **Composite**: 4.5 (Medium)

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

**Score**: 4.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 5 | Described in research |
| Attack Complexity | 5 | Needs some preparation |
| Tooling Availability | 3 | Needs custom tooling |
| Skill Level | 5 | Intermediate skill |

#### Scalability

**Score**: 5.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 4 | Partly automatable |
| Target Scope | 1 | One specific target |
| Resource Requirements | 7 | Minimal resources |
| Detection Difficulty | 8 | Blends with normal use |

#### Reachability

**Score**: 2.5 | **Trust Zone**: Agent Runtime Zone (Trusted)

reviewer-agent sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 2.5.

---

### R-27 — eval-runner

**Threat**: Clock drift between eval-runner and trace-collector leaves events in inconsistent order, so the sequence of actions on replayed traces and judge verdicts cannot be reconstructed reliably.

**Category**: repudiation | **Original Risk Level**: Note | **Composite**: 4.5 (Medium)

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

**Score**: 3.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 3 | Not described outside research |
| Attack Complexity | 5 | Needs some preparation |
| Tooling Availability | 1 | Needs custom tooling |
| Skill Level | 3 | Needs deep expertise |

#### Scalability

**Score**: 5.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 5 | Partly automatable |
| Target Scope | 1 | One specific target |
| Resource Requirements | 8 | Minimal resources |
| Detection Difficulty | 6 | Detectable with monitoring |

#### Reachability

**Score**: 3.0 | **Trust Zone**: Operations Zone (Trusted)

eval-runner sits in the Operations Zone. The zone baseline is 2.5 and the refinement for this finding gives 3.0.

---

### I-11 — router-agent

**Threat**: Backups of subtask assignments taken from router-agent are stored unencrypted in a shared location that wider operations staff can read.

**Category**: info-disclosure | **Original Risk Level**: Medium | **Composite**: 4.5 (Medium)

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

**Score**: 5.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 5 | Described in research |
| Attack Complexity | 5 | Needs some preparation |
| Tooling Availability | 4 | Tools need adaptation |
| Skill Level | 6 | Intermediate skill |

#### Scalability

**Score**: 5.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 6 | Partly automatable |
| Target Scope | 5 | A class of targets |
| Resource Requirements | 8 | Minimal resources |
| Detection Difficulty | 3 | Readily detected |

#### Reachability

**Score**: 3.5 | **Trust Zone**: Agent Runtime Zone (Trusted)

router-agent sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 3.5.

---

### I-15 — reviewer-agent

**Threat**: Cross-tenant filters on reviewer-agent are applied in application code only, so one missing predicate exposes another tenant's drafted proposals awaiting review.

**Category**: info-disclosure | **Original Risk Level**: Medium | **Composite**: 4.5 (Medium)

**Correlation Group**: Scores inherited from primary finding R-18 (CG-7). Dimensional detail is recorded on the primary.

**Score**: 5.3 | **Vector**: `CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N`

---

### I-27 — kb-index

**Threat**: carrier tariffs and customs rules held by kb-index are readable by any service in the Data Zone that shares the same network role, because access is granted by network position.

**Category**: info-disclosure | **Original Risk Level**: Medium | **Composite**: 4.5 (Medium)

#### CVSS 3.1 Base

**Score**: 4.1 | **Vector**: `CVSS:3.1/AV:N/AC:H/PR:H/UI:N/S:U/C:L/I:L/A:L`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Network | Reachable over the network |
| Attack Complexity (AC) | High | Needs specific conditions |
| Privileges Required (PR) | High | Administrative rights are needed |
| User Interaction (UI) | None | No user action needed |
| Scope (S) | Unchanged | Impact stays in the component |
| Confidentiality (C) | Low | Limited disclosure |
| Integrity (I) | Low | Limited modification |
| Availability (A) | Low | Degraded service |

#### Exploitability

**Score**: 6.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 7 | Documented and widely used |
| Attack Complexity | 6 | Needs some preparation |
| Tooling Availability | 6 | Tools need adaptation |
| Skill Level | 5 | Intermediate skill |

#### Scalability

**Score**: 6.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 8 | Fully automatable |
| Target Scope | 7 | Every instance |
| Resource Requirements | 6 | Moderate resources |
| Detection Difficulty | 5 | Detectable with monitoring |

#### Reachability

**Score**: 1.5 | **Trust Zone**: Data Zone (Trusted)

kb-index sits in the Data Zone. The zone baseline is 2.5 and the refinement for this finding gives 1.5.

---

### E-16 — reviewer-agent

**Threat**: A confused-deputy path lets a low-privilege caller ask reviewer-agent to act on drafted proposals awaiting review using the privileges of edge-gateway.

**Category**: privilege-escalation | **Original Risk Level**: Medium | **Composite**: 4.5 (Medium)

**Correlation Group**: Scores inherited from primary finding R-18 (CG-7). Dimensional detail is recorded on the primary.

**Score**: 5.3 | **Vector**: `CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N`

---

### AG-24 — reviewer-agent

**Threat**: Delegation from edge-gateway to reviewer-agent carries the full authority of the original session, so a low-trust sub-task can use high-trust rights.

**Category**: agentic | **Original Risk Level**: High | **Composite**: 4.5 (Medium)

**Correlation Group**: Scores inherited from primary finding R-18 (CG-7). Dimensional detail is recorded on the primary.

**Score**: 5.3 | **Vector**: `CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N`

---

### AG-25 — reviewer-agent

**Threat**: Memory written by reviewer-agent is trusted on later runs, so one poisoned entry changes the behaviour of every future task.

**Category**: agentic | **Original Risk Level**: Medium | **Composite**: 4.5 (Medium)

**Correlation Group**: Scores inherited from primary finding R-18 (CG-7). Dimensional detail is recorded on the primary.

**Score**: 5.3 | **Vector**: `CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N`

---

### LLM-16 — reviewer-agent

**Threat**: Encoded or multilingual payloads bypass the keyword filter in front of reviewer-agent, which only checks plain English text.

**Category**: llm | **Original Risk Level**: High | **Composite**: 4.5 (Medium)

**Correlation Group**: Scores inherited from primary finding R-18 (CG-7). Dimensional detail is recorded on the primary.

**Score**: 5.3 | **Vector**: `CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N`

---

### T-46 — reviewer-agent

**Threat**: Configuration of reviewer-agent can be rewritten by any service that holds the shared deployment credential, silently changing how drafted proposals awaiting review are handled.

**Category**: tampering | **Original Risk Level**: Medium | **Composite**: 4.4 (Medium)

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

**Score**: 5.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 6 | Partly automatable |
| Target Scope | 5 | A class of targets |
| Resource Requirements | 6 | Moderate resources |
| Detection Difficulty | 5 | Detectable with monitoring |

#### Reachability

**Score**: 1.5 | **Trust Zone**: Agent Runtime Zone (Trusted)

reviewer-agent sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 1.5.

---

### I-35 — queue-a2

**Threat**: A timing or size difference in the responses of queue-a2 lets an observer infer whether specific records of task and result messages exist.

**Category**: info-disclosure | **Original Risk Level**: Note | **Composite**: 4.4 (Medium)

#### CVSS 3.1 Base

**Score**: 4.7 | **Vector**: `CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:N/A:N`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Local | Needs local access |
| Attack Complexity (AC) | High | Needs specific conditions |
| Privileges Required (PR) | Low | A basic account is needed |
| User Interaction (UI) | None | No user action needed |
| Scope (S) | Unchanged | Impact stays in the component |
| Confidentiality (C) | High | Broad disclosure |
| Integrity (I) | None | No modification |
| Availability (A) | None | No loss of service |

#### Exploitability

**Score**: 5.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 5 | Described in research |
| Attack Complexity | 6 | Needs some preparation |
| Tooling Availability | 5 | Tools need adaptation |
| Skill Level | 6 | Intermediate skill |

#### Scalability

**Score**: 5.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 6 | Partly automatable |
| Target Scope | 4 | A class of targets |
| Resource Requirements | 6 | Moderate resources |
| Detection Difficulty | 4 | Detectable with monitoring |

#### Reachability

**Score**: 2.0 | **Trust Zone**: Agent Runtime Zone (Trusted)

queue-a2 sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 2.0.

---

### T-20 — vector-store-a

**Threat**: Serialised objects arriving from worker-2 are deserialised by vector-store-a with permissive type handling, allowing crafted payloads to instantiate unintended behaviour.

**Category**: tampering | **Original Risk Level**: Medium | **Composite**: 4.3 (Medium)

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

**Score**: 4.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 5 | Described in research |
| Attack Complexity | 4 | Needs some preparation |
| Tooling Availability | 4 | Tools need adaptation |
| Skill Level | 5 | Intermediate skill |

#### Scalability

**Score**: 5.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 5 | Partly automatable |
| Target Scope | 5 | A class of targets |
| Resource Requirements | 6 | Moderate resources |
| Detection Difficulty | 4 | Detectable with monitoring |

#### Reachability

**Score**: 3.5 | **Trust Zone**: Data Zone (Trusted)

vector-store-a sits in the Data Zone. The zone baseline is 2.5 and the refinement for this finding gives 3.5.

---

### R-30 — audit-ledger

**Threat**: Log entries from audit-ledger can be edited or deleted by the same operators who administer it, so evidence of misuse can be removed after the fact.

**Category**: repudiation | **Original Risk Level**: Medium | **Composite**: 4.3 (Medium)

#### CVSS 3.1 Base

**Score**: 4.3 | **Vector**: `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Network | Reachable over the network |
| Attack Complexity (AC) | Low | No special conditions |
| Privileges Required (PR) | Low | A basic account is needed |
| User Interaction (UI) | None | No user action needed |
| Scope (S) | Unchanged | Impact stays in the component |
| Confidentiality (C) | None | No disclosure |
| Integrity (I) | Low | Limited modification |
| Availability (A) | None | No loss of service |

#### Exploitability

**Score**: 4.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 4 | Described in research |
| Attack Complexity | 6 | Needs some preparation |
| Tooling Availability | 4 | Tools need adaptation |
| Skill Level | 4 | Intermediate skill |

#### Scalability

**Score**: 5.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 3 | Manual for each target |
| Target Scope | 1 | One specific target |
| Resource Requirements | 7 | Minimal resources |
| Detection Difficulty | 9 | Blends with normal use |

#### Reachability

**Score**: 3.5 | **Trust Zone**: Operations Zone (Trusted)

audit-ledger sits in the Operations Zone. The zone baseline is 2.5 and the refinement for this finding gives 3.5.

---

### LLM-59 — vector-store-a

**Threat**: Anyone who can write to the ingestion path of vector-store-a can slip in documents that contradict authoritative sources.

**Category**: llm | **Original Risk Level**: Critical | **Composite**: 4.3 (Medium)

**Correlation Group**: Scores inherited from primary finding T-20 (CG-12). Dimensional detail is recorded on the primary.

**Score**: 4.2 | **Vector**: `CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:N/I:L/A:L`

---

### R-8 — intake-agent

**Threat**: Clock drift between intake-agent and edge-gateway leaves events in inconsistent order, so the sequence of actions on free-text shipment requests cannot be reconstructed reliably.

**Category**: repudiation | **Original Risk Level**: Medium | **Composite**: 4.2 (Medium)

#### CVSS 3.1 Base

**Score**: 5.4 | **Vector**: `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:L`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Network | Reachable over the network |
| Attack Complexity (AC) | Low | No special conditions |
| Privileges Required (PR) | Low | A basic account is needed |
| User Interaction (UI) | None | No user action needed |
| Scope (S) | Unchanged | Impact stays in the component |
| Confidentiality (C) | None | No disclosure |
| Integrity (I) | Low | Limited modification |
| Availability (A) | Low | Degraded service |

#### Exploitability

**Score**: 4.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 3 | Not described outside research |
| Attack Complexity | 5 | Needs some preparation |
| Tooling Availability | 3 | Needs custom tooling |
| Skill Level | 5 | Intermediate skill |

#### Scalability

**Score**: 4.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 2 | Manual for each target |
| Target Scope | 1 | One specific target |
| Resource Requirements | 7 | Minimal resources |
| Detection Difficulty | 6 | Detectable with monitoring |

#### Reachability

**Score**: 2.5 | **Trust Zone**: Agent Runtime Zone (Trusted)

intake-agent sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 2.5.

---

### R-22 — summarizer-llm

**Threat**: Actions taken through summarizer-llm are logged without the authenticated principal or a request identifier, so a caller can deny having submitted a change to shipment records fed into summaries.

**Category**: repudiation | **Original Risk Level**: Low | **Composite**: 4.2 (Medium)

#### CVSS 3.1 Base

**Score**: 4.1 | **Vector**: `CVSS:3.1/AV:A/AC:L/PR:L/UI:N/S:C/C:N/I:L/A:N`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Adjacent | Needs an adjacent network |
| Attack Complexity (AC) | Low | No special conditions |
| Privileges Required (PR) | Low | A basic account is needed |
| User Interaction (UI) | None | No user action needed |
| Scope (S) | Changed | Impact crosses a boundary |
| Confidentiality (C) | None | No disclosure |
| Integrity (I) | Low | Limited modification |
| Availability (A) | None | No loss of service |

#### Exploitability

**Score**: 4.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 5 | Described in research |
| Attack Complexity | 6 | Needs some preparation |
| Tooling Availability | 1 | Needs custom tooling |
| Skill Level | 6 | Intermediate skill |

#### Scalability

**Score**: 5.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 2 | Manual for each target |
| Target Scope | 3 | One specific target |
| Resource Requirements | 8 | Minimal resources |
| Detection Difficulty | 7 | Blends with normal use |

#### Reachability

**Score**: 3.5 | **Trust Zone**: Agent Runtime Zone (Trusted)

summarizer-llm sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 3.5.

---

### I-6 — intake-agent

**Threat**: A timing or size difference in the responses of intake-agent lets an observer infer whether specific records of free-text shipment requests exist.

**Category**: info-disclosure | **Original Risk Level**: High | **Composite**: 4.2 (Medium)

**Correlation Group**: Scores inherited from primary finding R-8 (CG-2). Dimensional detail is recorded on the primary.

**Score**: 5.4 | **Vector**: `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:L`

---

### I-44 — intake-agent

**Threat**: Backups of free-text shipment requests taken from intake-agent are stored unencrypted in a shared location that wider operations staff can read.

**Category**: info-disclosure | **Original Risk Level**: Medium | **Composite**: 4.2 (Medium)

**Correlation Group**: Scores inherited from primary finding R-8 (CG-2). Dimensional detail is recorded on the primary.

**Score**: 5.4 | **Vector**: `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:L`

---

### E-6 — intake-agent

**Threat**: Role claims carried in the service token presented to intake-agent are honoured without confirmation against the authoritative directory.

**Category**: privilege-escalation | **Original Risk Level**: Low | **Composite**: 4.2 (Medium)

**Correlation Group**: Scores inherited from primary finding R-8 (CG-2). Dimensional detail is recorded on the primary.

**Score**: 5.4 | **Vector**: `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:L`

---

### AG-1 — intake-agent

**Threat**: Memory written by intake-agent is trusted on later runs, so one poisoned entry changes the behaviour of every future task.

**Category**: agentic | **Original Risk Level**: Critical | **Composite**: 4.2 (Medium)

**Correlation Group**: Scores inherited from primary finding R-8 (CG-2). Dimensional detail is recorded on the primary.

**Score**: 5.4 | **Vector**: `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:L`

---

### AG-2 — intake-agent

**Threat**: intake-agent retries failed actions on its own, repeating side effects such as bookings or messages when the first attempt partly succeeded.

**Category**: agentic | **Original Risk Level**: Critical | **Composite**: 4.2 (Medium)

**Correlation Group**: Scores inherited from primary finding R-8 (CG-2). Dimensional detail is recorded on the primary.

**Score**: 5.4 | **Vector**: `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:L`

---

### LLM-4 — intake-agent

**Threat**: Encoded or multilingual payloads bypass the keyword filter in front of intake-agent, which only checks plain English text.

**Category**: llm | **Original Risk Level**: Critical | **Composite**: 4.2 (Medium)

**Correlation Group**: Scores inherited from primary finding R-8 (CG-2). Dimensional detail is recorded on the primary.

**Score**: 5.4 | **Vector**: `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:L`

---

### T-22 — vector-store-a

**Threat**: Unsanitised embedded documents and metadata reach vector-store-a and are processed as trusted structure, so crafted input changes how later steps interpret the record.

**Category**: tampering | **Original Risk Level**: High | **Composite**: 4.1 (Medium)

#### CVSS 3.1 Base

**Score**: 2.2 | **Vector**: `CVSS:3.1/AV:N/AC:H/PR:H/UI:N/S:U/C:N/I:L/A:N`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Network | Reachable over the network |
| Attack Complexity (AC) | High | Needs specific conditions |
| Privileges Required (PR) | High | Administrative rights are needed |
| User Interaction (UI) | None | No user action needed |
| Scope (S) | Unchanged | Impact stays in the component |
| Confidentiality (C) | None | No disclosure |
| Integrity (I) | Low | Limited modification |
| Availability (A) | None | No loss of service |

#### Exploitability

**Score**: 6.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 5 | Described in research |
| Attack Complexity | 7 | A single step suffices |
| Tooling Availability | 5 | Tools need adaptation |
| Skill Level | 7 | Little skill needed |

#### Scalability

**Score**: 5.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 3 | Manual for each target |
| Target Scope | 5 | A class of targets |
| Resource Requirements | 6 | Moderate resources |
| Detection Difficulty | 6 | Detectable with monitoring |

#### Reachability

**Score**: 4.0 | **Trust Zone**: Data Zone (Trusted)

vector-store-a sits in the Data Zone. The zone baseline is 2.5 and the refinement for this finding gives 4.0.

---

### T-40 — policy-engine

**Threat**: Serialised objects arriving from audit-ledger are deserialised by policy-engine with permissive type handling, allowing crafted payloads to instantiate unintended behaviour.

**Category**: tampering | **Original Risk Level**: High | **Composite**: 4.1 (Medium)

#### CVSS 3.1 Base

**Score**: 4.9 | **Vector**: `CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:N/I:H/A:N`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Network | Reachable over the network |
| Attack Complexity (AC) | Low | No special conditions |
| Privileges Required (PR) | High | Administrative rights are needed |
| User Interaction (UI) | None | No user action needed |
| Scope (S) | Unchanged | Impact stays in the component |
| Confidentiality (C) | None | No disclosure |
| Integrity (I) | High | Broad modification |
| Availability (A) | None | No loss of service |

#### Exploitability

**Score**: 4.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 4 | Described in research |
| Attack Complexity | 4 | Needs some preparation |
| Tooling Availability | 4 | Tools need adaptation |
| Skill Level | 4 | Intermediate skill |

#### Scalability

**Score**: 4.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 3 | Manual for each target |
| Target Scope | 3 | One specific target |
| Resource Requirements | 7 | Minimal resources |
| Detection Difficulty | 3 | Readily detected |

#### Reachability

**Score**: 3.0 | **Trust Zone**: Operations Zone (Trusted)

policy-engine sits in the Operations Zone. The zone baseline is 2.5 and the refinement for this finding gives 3.0.

---

### R-12 — planner-agent

**Threat**: Operators approve changes to task plans and tool selections through a chat message or ticket comment that is not bound to the executed change, so approvals can be disputed.

**Category**: repudiation | **Original Risk Level**: Medium | **Composite**: 4.1 (Medium)

#### CVSS 3.1 Base

**Score**: 4.3 | **Vector**: `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Network | Reachable over the network |
| Attack Complexity (AC) | Low | No special conditions |
| Privileges Required (PR) | Low | A basic account is needed |
| User Interaction (UI) | None | No user action needed |
| Scope (S) | Unchanged | Impact stays in the component |
| Confidentiality (C) | None | No disclosure |
| Integrity (I) | Low | Limited modification |
| Availability (A) | None | No loss of service |

#### Exploitability

**Score**: 4.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 2 | Not described outside research |
| Attack Complexity | 7 | A single step suffices |
| Tooling Availability | 2 | Needs custom tooling |
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

**Score**: 3.5 | **Trust Zone**: Agent Runtime Zone (Trusted)

planner-agent sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 3.5.

---

### R-15 — router-agent

**Threat**: Log entries from router-agent can be edited or deleted by the same operators who administer it, so evidence of misuse can be removed after the fact.

**Category**: repudiation | **Original Risk Level**: High | **Composite**: 4.1 (Medium)

#### CVSS 3.1 Base

**Score**: 4.1 | **Vector**: `CVSS:3.1/AV:N/AC:H/PR:H/UI:N/S:U/C:L/I:L/A:L`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Network | Reachable over the network |
| Attack Complexity (AC) | High | Needs specific conditions |
| Privileges Required (PR) | High | Administrative rights are needed |
| User Interaction (UI) | None | No user action needed |
| Scope (S) | Unchanged | Impact stays in the component |
| Confidentiality (C) | Low | Limited disclosure |
| Integrity (I) | Low | Limited modification |
| Availability (A) | Low | Degraded service |

#### Exploitability

**Score**: 4.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 2 | Not described outside research |
| Attack Complexity | 7 | A single step suffices |
| Tooling Availability | 1 | Needs custom tooling |
| Skill Level | 6 | Intermediate skill |

#### Scalability

**Score**: 5.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 3 | Manual for each target |
| Target Scope | 1 | One specific target |
| Resource Requirements | 9 | Minimal resources |
| Detection Difficulty | 7 | Blends with normal use |

#### Reachability

**Score**: 3.5 | **Trust Zone**: Agent Runtime Zone (Trusted)

router-agent sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 3.5.

---

### R-26 — trace-collector

**Threat**: Operators approve changes to prompts, completions and tool traces through a chat message or ticket comment that is not bound to the executed change, so approvals can be disputed.

**Category**: repudiation | **Original Risk Level**: High | **Composite**: 4.1 (Medium)

#### CVSS 3.1 Base

**Score**: 4.6 | **Vector**: `CVSS:3.1/AV:A/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:N`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Adjacent | Needs an adjacent network |
| Attack Complexity (AC) | Low | No special conditions |
| Privileges Required (PR) | Low | A basic account is needed |
| User Interaction (UI) | None | No user action needed |
| Scope (S) | Unchanged | Impact stays in the component |
| Confidentiality (C) | Low | Limited disclosure |
| Integrity (I) | Low | Limited modification |
| Availability (A) | None | No loss of service |

#### Exploitability

**Score**: 4.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 4 | Described in research |
| Attack Complexity | 7 | A single step suffices |
| Tooling Availability | 2 | Needs custom tooling |
| Skill Level | 5 | Intermediate skill |

#### Scalability

**Score**: 4.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 2 | Manual for each target |
| Target Scope | 4 | A class of targets |
| Resource Requirements | 7 | Minimal resources |
| Detection Difficulty | 5 | Detectable with monitoring |

#### Reachability

**Score**: 2.5 | **Trust Zone**: Operations Zone (Trusted)

trace-collector sits in the Operations Zone. The zone baseline is 2.5 and the refinement for this finding gives 2.5.

---

### R-28 — policy-engine

**Threat**: Operators approve changes to guardrail rules and approval decisions through a chat message or ticket comment that is not bound to the executed change, so approvals can be disputed.

**Category**: repudiation | **Original Risk Level**: Medium | **Composite**: 4.1 (Medium)

#### CVSS 3.1 Base

**Score**: 5.0 | **Vector**: `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:L/I:N/A:N`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Network | Reachable over the network |
| Attack Complexity (AC) | Low | No special conditions |
| Privileges Required (PR) | Low | A basic account is needed |
| User Interaction (UI) | None | No user action needed |
| Scope (S) | Changed | Impact crosses a boundary |
| Confidentiality (C) | Low | Limited disclosure |
| Integrity (I) | None | No modification |
| Availability (A) | None | No loss of service |

#### Exploitability

**Score**: 3.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 2 | Not described outside research |
| Attack Complexity | 7 | A single step suffices |
| Tooling Availability | 3 | Needs custom tooling |
| Skill Level | 2 | Needs deep expertise |

#### Scalability

**Score**: 4.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 4 | Partly automatable |
| Target Scope | 3 | One specific target |
| Resource Requirements | 6 | Moderate resources |
| Detection Difficulty | 5 | Detectable with monitoring |

#### Reachability

**Score**: 3.0 | **Trust Zone**: Operations Zone (Trusted)

policy-engine sits in the Operations Zone. The zone baseline is 2.5 and the refinement for this finding gives 3.0.

---

### R-29 — policy-engine

**Threat**: Actions taken through policy-engine are logged without the authenticated principal or a request identifier, so a caller can deny having submitted a change to guardrail rules and approval decisions.

**Category**: repudiation | **Original Risk Level**: Medium | **Composite**: 4.1 (Medium)

**Correlation Group**: Scores inherited from primary finding R-28 (CG-21). Dimensional detail is recorded on the primary.

**Score**: 5.0 | **Vector**: `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:L/I:N/A:N`

---

### R-33 — trace-collector

**Threat**: Actions taken through trace-collector are logged without the authenticated principal or a request identifier, so a caller can deny having submitted a change to prompts, completions and tool traces.

**Category**: repudiation | **Original Risk Level**: Low | **Composite**: 4.1 (Medium)

#### CVSS 3.1 Base

**Score**: 4.7 | **Vector**: `CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:N/A:N`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Network | Reachable over the network |
| Attack Complexity (AC) | Low | No special conditions |
| Privileges Required (PR) | None | No privileges needed |
| User Interaction (UI) | Required | A user must act |
| Scope (S) | Changed | Impact crosses a boundary |
| Confidentiality (C) | Low | Limited disclosure |
| Integrity (I) | None | No modification |
| Availability (A) | None | No loss of service |

#### Exploitability

**Score**: 4.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 4 | Described in research |
| Attack Complexity | 4 | Needs some preparation |
| Tooling Availability | 4 | Tools need adaptation |
| Skill Level | 6 | Intermediate skill |

#### Scalability

**Score**: 3.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 2 | Manual for each target |
| Target Scope | 1 | One specific target |
| Resource Requirements | 6 | Moderate resources |
| Detection Difficulty | 5 | Detectable with monitoring |

#### Reachability

**Score**: 3.0 | **Trust Zone**: Operations Zone (Trusted)

trace-collector sits in the Operations Zone. The zone baseline is 2.5 and the refinement for this finding gives 3.0.

---

### I-12 — router-agent

**Threat**: Cross-tenant filters on router-agent are applied in application code only, so one missing predicate exposes another tenant's subtask assignments.

**Category**: info-disclosure | **Original Risk Level**: Medium | **Composite**: 4.1 (Medium)

#### CVSS 3.1 Base

**Score**: 2.7 | **Vector**: `CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:L/I:N/A:N`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Network | Reachable over the network |
| Attack Complexity (AC) | Low | No special conditions |
| Privileges Required (PR) | High | Administrative rights are needed |
| User Interaction (UI) | None | No user action needed |
| Scope (S) | Unchanged | Impact stays in the component |
| Confidentiality (C) | Low | Limited disclosure |
| Integrity (I) | None | No modification |
| Availability (A) | None | No loss of service |

#### Exploitability

**Score**: 6.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 5 | Described in research |
| Attack Complexity | 7 | A single step suffices |
| Tooling Availability | 4 | Tools need adaptation |
| Skill Level | 8 | Little skill needed |

#### Scalability

**Score**: 6.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 8 | Fully automatable |
| Target Scope | 4 | A class of targets |
| Resource Requirements | 9 | Minimal resources |
| Detection Difficulty | 5 | Detectable with monitoring |

#### Reachability

**Score**: 2.0 | **Trust Zone**: Agent Runtime Zone (Trusted)

router-agent sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 2.0.

---

### I-33 — queue-a2

**Threat**: Logs and traces emitted by queue-a2 include raw task and result messages, so anyone with access to the logging pipeline can read content meant for one tenant.

**Category**: info-disclosure | **Original Risk Level**: High | **Composite**: 4.1 (Medium)

#### CVSS 3.1 Base

**Score**: 2.4 | **Vector**: `CVSS:3.1/AV:A/AC:L/PR:H/UI:N/S:U/C:L/I:N/A:N`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Adjacent | Needs an adjacent network |
| Attack Complexity (AC) | Low | No special conditions |
| Privileges Required (PR) | High | Administrative rights are needed |
| User Interaction (UI) | None | No user action needed |
| Scope (S) | Unchanged | Impact stays in the component |
| Confidentiality (C) | Low | Limited disclosure |
| Integrity (I) | None | No modification |
| Availability (A) | None | No loss of service |

#### Exploitability

**Score**: 6.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 8 | Documented and widely used |
| Attack Complexity | 5 | Needs some preparation |
| Tooling Availability | 6 | Tools need adaptation |
| Skill Level | 7 | Little skill needed |

#### Scalability

**Score**: 6.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 5 | Partly automatable |
| Target Scope | 7 | Every instance |
| Resource Requirements | 9 | Minimal resources |
| Detection Difficulty | 5 | Detectable with monitoring |

#### Reachability

**Score**: 1.5 | **Trust Zone**: Agent Runtime Zone (Trusted)

queue-a2 sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 1.5.

---

### I-39 — policy-engine

**Threat**: guardrail rules and approval decisions held by policy-engine are readable by any service in the Operations Zone that shares the same network role, because access is granted by network position.

**Category**: info-disclosure | **Original Risk Level**: Medium | **Composite**: 4.1 (Medium)

**Correlation Group**: Scores inherited from primary finding R-28 (CG-21). Dimensional detail is recorded on the primary.

**Score**: 5.0 | **Vector**: `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:L/I:N/A:N`

---

### AG-39 — policy-engine

**Threat**: policy-engine retries failed actions on its own, repeating side effects such as bookings or messages when the first attempt partly succeeded.

**Category**: agentic | **Original Risk Level**: Medium | **Composite**: 4.1 (Medium)

**Correlation Group**: Scores inherited from primary finding R-28 (CG-21). Dimensional detail is recorded on the primary.

**Score**: 5.0 | **Vector**: `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:L/I:N/A:N`

---

### AG-40 — policy-engine

**Threat**: policy-engine can start further agents or processes on request, so a compromised prompt can multiply its reach beyond the intended scope.

**Category**: agentic | **Original Risk Level**: High | **Composite**: 4.1 (Medium)

**Correlation Group**: Scores inherited from primary finding R-28 (CG-21). Dimensional detail is recorded on the primary.

**Score**: 5.0 | **Vector**: `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:L/I:N/A:N`

---

### LLM-51 — policy-engine

**Threat**: An attacker splits a payload across several messages so that no single message trips the filter in front of policy-engine.

**Category**: llm | **Original Risk Level**: Medium | **Composite**: 4.1 (Medium)

**Correlation Group**: Scores inherited from primary finding R-28 (CG-21). Dimensional detail is recorded on the primary.

**Score**: 5.0 | **Vector**: `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:L/I:N/A:N`

---

### R-16 — worker-2

**Threat**: Operators approve changes to work orders and route candidates through a chat message or ticket comment that is not bound to the executed change, so approvals can be disputed.

**Category**: repudiation | **Original Risk Level**: Critical | **Composite**: 3.9 (Low)

#### CVSS 3.1 Base

**Score**: 4.8 | **Vector**: `CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:L/A:L`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Network | Reachable over the network |
| Attack Complexity (AC) | High | Needs specific conditions |
| Privileges Required (PR) | None | No privileges needed |
| User Interaction (UI) | None | No user action needed |
| Scope (S) | Unchanged | Impact stays in the component |
| Confidentiality (C) | None | No disclosure |
| Integrity (I) | Low | Limited modification |
| Availability (A) | Low | Degraded service |

#### Exploitability

**Score**: 3.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 2 | Not described outside research |
| Attack Complexity | 5 | Needs some preparation |
| Tooling Availability | 2 | Needs custom tooling |
| Skill Level | 5 | Intermediate skill |

#### Scalability

**Score**: 5.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 4 | Partly automatable |
| Target Scope | 2 | One specific target |
| Resource Requirements | 7 | Minimal resources |
| Detection Difficulty | 7 | Blends with normal use |

#### Reachability

**Score**: 2.0 | **Trust Zone**: Agent Runtime Zone (Trusted)

worker-2 sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 2.0.

---

### R-10 — planner-agent

**Threat**: Delegated actions performed by planner-agent on behalf of a user are recorded under the service identity alone, hiding who authorised them.

**Category**: repudiation | **Original Risk Level**: Note | **Composite**: 3.8 (Low)

#### CVSS 3.1 Base

**Score**: 4.3 | **Vector**: `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Network | Reachable over the network |
| Attack Complexity (AC) | Low | No special conditions |
| Privileges Required (PR) | Low | A basic account is needed |
| User Interaction (UI) | None | No user action needed |
| Scope (S) | Unchanged | Impact stays in the component |
| Confidentiality (C) | None | No disclosure |
| Integrity (I) | Low | Limited modification |
| Availability (A) | None | No loss of service |

#### Exploitability

**Score**: 4.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 5 | Described in research |
| Attack Complexity | 7 | A single step suffices |
| Tooling Availability | 1 | Needs custom tooling |
| Skill Level | 3 | Needs deep expertise |

#### Scalability

**Score**: 4.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 1 | Manual for each target |
| Target Scope | 4 | A class of targets |
| Resource Requirements | 6 | Moderate resources |
| Detection Difficulty | 7 | Blends with normal use |

#### Reachability

**Score**: 2.0 | **Trust Zone**: Agent Runtime Zone (Trusted)

planner-agent sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 2.0.

---

### R-9 — planner-agent

**Threat**: Clock drift between planner-agent and router-agent leaves events in inconsistent order, so the sequence of actions on task plans and tool selections cannot be reconstructed reliably.

**Category**: repudiation | **Original Risk Level**: Medium | **Composite**: 3.7 (Low)

#### CVSS 3.1 Base

**Score**: 3.4 | **Vector**: `CVSS:3.1/AV:A/AC:H/PR:L/UI:R/S:U/C:L/I:L/A:N`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Adjacent | Needs an adjacent network |
| Attack Complexity (AC) | High | Needs specific conditions |
| Privileges Required (PR) | Low | A basic account is needed |
| User Interaction (UI) | Required | A user must act |
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
| Tooling Availability | 1 | Needs custom tooling |
| Skill Level | 5 | Intermediate skill |

#### Scalability

**Score**: 4.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 1 | Manual for each target |
| Target Scope | 2 | One specific target |
| Resource Requirements | 7 | Minimal resources |
| Detection Difficulty | 8 | Blends with normal use |

#### Reachability

**Score**: 3.0 | **Trust Zone**: Agent Runtime Zone (Trusted)

planner-agent sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 3.0.

---

### R-14 — router-agent

**Threat**: Actions taken through router-agent are logged without the authenticated principal or a request identifier, so a caller can deny having submitted a change to subtask assignments.

**Category**: repudiation | **Original Risk Level**: Note | **Composite**: 3.7 (Low)

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

**Score**: 3.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 3 | Not described outside research |
| Attack Complexity | 4 | Needs some preparation |
| Tooling Availability | 3 | Needs custom tooling |
| Skill Level | 4 | Intermediate skill |

#### Scalability

**Score**: 5.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 1 | Manual for each target |
| Target Scope | 3 | One specific target |
| Resource Requirements | 7 | Minimal resources |
| Detection Difficulty | 9 | Blends with normal use |

#### Reachability

**Score**: 3.5 | **Trust Zone**: Agent Runtime Zone (Trusted)

router-agent sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 3.5.

---

### R-20 — embed-service-2

**Threat**: Clock drift between embed-service-2 and vector-store-a leaves events in inconsistent order, so the sequence of actions on document chunks and query embeddings cannot be reconstructed reliably.

**Category**: repudiation | **Original Risk Level**: Low | **Composite**: 3.7 (Low)

#### CVSS 3.1 Base

**Score**: 2.7 | **Vector**: `CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:L/I:N/A:N`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Network | Reachable over the network |
| Attack Complexity (AC) | Low | No special conditions |
| Privileges Required (PR) | High | Administrative rights are needed |
| User Interaction (UI) | None | No user action needed |
| Scope (S) | Unchanged | Impact stays in the component |
| Confidentiality (C) | Low | Limited disclosure |
| Integrity (I) | None | No modification |
| Availability (A) | None | No loss of service |

#### Exploitability

**Score**: 5.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 4 | Described in research |
| Attack Complexity | 6 | Needs some preparation |
| Tooling Availability | 4 | Tools need adaptation |
| Skill Level | 6 | Intermediate skill |

#### Scalability

**Score**: 5.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 2 | Manual for each target |
| Target Scope | 3 | One specific target |
| Resource Requirements | 9 | Minimal resources |
| Detection Difficulty | 6 | Detectable with monitoring |

#### Reachability

**Score**: 2.5 | **Trust Zone**: Agent Runtime Zone (Trusted)

embed-service-2 sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 2.5.

---

### I-7 — planner-agent

**Threat**: A timing or size difference in the responses of planner-agent lets an observer infer whether specific records of task plans and tool selections exist.

**Category**: info-disclosure | **Original Risk Level**: Medium | **Composite**: 3.7 (Low)

**Correlation Group**: Scores inherited from primary finding R-9 (CG-3). Dimensional detail is recorded on the primary.

**Score**: 3.4 | **Vector**: `CVSS:3.1/AV:A/AC:H/PR:L/UI:R/S:U/C:L/I:L/A:N`

---

### E-8 — planner-agent

**Threat**: planner-agent runs with broader permissions than its function needs, so a flaw in handling task plans and tool selections yields access to unrelated resources.

**Category**: privilege-escalation | **Original Risk Level**: Medium | **Composite**: 3.7 (Low)

**Correlation Group**: Scores inherited from primary finding R-9 (CG-3). Dimensional detail is recorded on the primary.

**Score**: 3.4 | **Vector**: `CVSS:3.1/AV:A/AC:H/PR:L/UI:R/S:U/C:L/I:L/A:N`

---

### E-9 — planner-agent

**Threat**: A confused-deputy path lets a low-privilege caller ask planner-agent to act on task plans and tool selections using the privileges of model-gateway.

**Category**: privilege-escalation | **Original Risk Level**: High | **Composite**: 3.7 (Low)

**Correlation Group**: Scores inherited from primary finding R-9 (CG-3). Dimensional detail is recorded on the primary.

**Score**: 3.4 | **Vector**: `CVSS:3.1/AV:A/AC:H/PR:L/UI:R/S:U/C:L/I:L/A:N`

---

### AG-4 — planner-agent

**Threat**: planner-agent runs without a budget on steps or spend, so a loop or an adversarial task keeps it acting long after it stopped being useful.

**Category**: agentic | **Original Risk Level**: High | **Composite**: 3.7 (Low)

**Correlation Group**: Scores inherited from primary finding R-9 (CG-3). Dimensional detail is recorded on the primary.

**Score**: 3.4 | **Vector**: `CVSS:3.1/AV:A/AC:H/PR:L/UI:R/S:U/C:L/I:L/A:N`

---

### AG-5 — planner-agent

**Threat**: Delegation from trace-collector to planner-agent carries the full authority of the original session, so a low-trust sub-task can use high-trust rights.

**Category**: agentic | **Original Risk Level**: High | **Composite**: 3.7 (Low)

**Correlation Group**: Scores inherited from primary finding R-9 (CG-3). Dimensional detail is recorded on the primary.

**Score**: 3.4 | **Vector**: `CVSS:3.1/AV:A/AC:H/PR:L/UI:R/S:U/C:L/I:L/A:N`

---

### LLM-7 — planner-agent

**Threat**: Indirect injection through documents retrieved for planner-agent lets the author of a retrieved page steer the answer without ever talking to the system.

**Category**: llm | **Original Risk Level**: Medium | **Composite**: 3.7 (Low)

**Correlation Group**: Scores inherited from primary finding R-9 (CG-3). Dimensional detail is recorded on the primary.

**Score**: 3.4 | **Vector**: `CVSS:3.1/AV:A/AC:H/PR:L/UI:R/S:U/C:L/I:L/A:N`

---

### R-11 — planner-agent

**Threat**: Failed and rejected attempts against planner-agent are not logged, so probing of task plans and tool selections leaves no trace that an investigator could use.

**Category**: repudiation | **Original Risk Level**: Low | **Composite**: 3.6 (Low)

#### CVSS 3.1 Base

**Score**: 4.3 | **Vector**: `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Network | Reachable over the network |
| Attack Complexity (AC) | Low | No special conditions |
| Privileges Required (PR) | Low | A basic account is needed |
| User Interaction (UI) | None | No user action needed |
| Scope (S) | Unchanged | Impact stays in the component |
| Confidentiality (C) | None | No disclosure |
| Integrity (I) | Low | Limited modification |
| Availability (A) | None | No loss of service |

#### Exploitability

**Score**: 3.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 2 | Not described outside research |
| Attack Complexity | 7 | A single step suffices |
| Tooling Availability | 1 | Needs custom tooling |
| Skill Level | 4 | Intermediate skill |

#### Scalability

**Score**: 5.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 2 | Manual for each target |
| Target Scope | 4 | A class of targets |
| Resource Requirements | 8 | Minimal resources |
| Detection Difficulty | 6 | Detectable with monitoring |

#### Reachability

**Score**: 1.5 | **Trust Zone**: Agent Runtime Zone (Trusted)

planner-agent sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 1.5.

---

### R-21 — embed-service-2

**Threat**: Delegated actions performed by embed-service-2 on behalf of a user are recorded under the service identity alone, hiding who authorised them.

**Category**: repudiation | **Original Risk Level**: Note | **Composite**: 3.6 (Low)

#### CVSS 3.1 Base

**Score**: 4.3 | **Vector**: `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Network | Reachable over the network |
| Attack Complexity (AC) | Low | No special conditions |
| Privileges Required (PR) | Low | A basic account is needed |
| User Interaction (UI) | None | No user action needed |
| Scope (S) | Unchanged | Impact stays in the component |
| Confidentiality (C) | None | No disclosure |
| Integrity (I) | Low | Limited modification |
| Availability (A) | None | No loss of service |

#### Exploitability

**Score**: 3.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 4 | Described in research |
| Attack Complexity | 4 | Needs some preparation |
| Tooling Availability | 4 | Tools need adaptation |
| Skill Level | 2 | Needs deep expertise |

#### Scalability

**Score**: 5.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 2 | Manual for each target |
| Target Scope | 2 | One specific target |
| Resource Requirements | 7 | Minimal resources |
| Detection Difficulty | 9 | Blends with normal use |

#### Reachability

**Score**: 1.5 | **Trust Zone**: Agent Runtime Zone (Trusted)

embed-service-2 sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 1.5.

---

### R-32 — tool-server-1

**Threat**: Operators approve changes to tool call arguments and results through a chat message or ticket comment that is not bound to the executed change, so approvals can be disputed.

**Category**: repudiation | **Original Risk Level**: Note | **Composite**: 3.6 (Low)

#### CVSS 3.1 Base

**Score**: 4.4 | **Vector**: `CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:N`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Local | Needs local access |
| Attack Complexity (AC) | Low | No special conditions |
| Privileges Required (PR) | Low | A basic account is needed |
| User Interaction (UI) | None | No user action needed |
| Scope (S) | Unchanged | Impact stays in the component |
| Confidentiality (C) | Low | Limited disclosure |
| Integrity (I) | Low | Limited modification |
| Availability (A) | None | No loss of service |

#### Exploitability

**Score**: 3.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 3 | Not described outside research |
| Attack Complexity | 4 | Needs some preparation |
| Tooling Availability | 3 | Needs custom tooling |
| Skill Level | 4 | Intermediate skill |

#### Scalability

**Score**: 5.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 3 | Manual for each target |
| Target Scope | 1 | One specific target |
| Resource Requirements | 7 | Minimal resources |
| Detection Difficulty | 9 | Blends with normal use |

#### Reachability

**Score**: 1.5 | **Trust Zone**: Agent Runtime Zone (Trusted)

tool-server-1 sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 1.5.

---

### R-13 — router-agent

**Threat**: Operators approve changes to subtask assignments through a chat message or ticket comment that is not bound to the executed change, so approvals can be disputed.

**Category**: repudiation | **Original Risk Level**: Low | **Composite**: 3.5 (Low)

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

**Score**: 3.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 3 | Not described outside research |
| Attack Complexity | 6 | Needs some preparation |
| Tooling Availability | 1 | Needs custom tooling |
| Skill Level | 4 | Intermediate skill |

#### Scalability

**Score**: 5.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 4 | Partly automatable |
| Target Scope | 4 | A class of targets |
| Resource Requirements | 7 | Minimal resources |
| Detection Difficulty | 7 | Blends with normal use |

#### Reachability

**Score**: 2.0 | **Trust Zone**: Agent Runtime Zone (Trusted)

router-agent sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 2.0.

---

### R-19 — model-gateway

**Threat**: Failed and rejected attempts against model-gateway are not logged, so probing of prompts and completions leaves no trace that an investigator could use.

**Category**: repudiation | **Original Risk Level**: High | **Composite**: 3.5 (Low)

#### CVSS 3.1 Base

**Score**: 3.5 | **Vector**: `CVSS:3.1/AV:N/AC:L/PR:H/UI:R/S:U/C:N/I:L/A:L`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Network | Reachable over the network |
| Attack Complexity (AC) | Low | No special conditions |
| Privileges Required (PR) | High | Administrative rights are needed |
| User Interaction (UI) | Required | A user must act |
| Scope (S) | Unchanged | Impact stays in the component |
| Confidentiality (C) | None | No disclosure |
| Integrity (I) | Low | Limited modification |
| Availability (A) | Low | Degraded service |

#### Exploitability

**Score**: 4.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 5 | Described in research |
| Attack Complexity | 4 | Needs some preparation |
| Tooling Availability | 2 | Needs custom tooling |
| Skill Level | 5 | Intermediate skill |

#### Scalability

**Score**: 4.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 1 | Manual for each target |
| Target Scope | 2 | One specific target |
| Resource Requirements | 8 | Minimal resources |
| Detection Difficulty | 7 | Blends with normal use |

#### Reachability

**Score**: 2.0 | **Trust Zone**: Agent Runtime Zone (Trusted)

model-gateway sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 2.0.

---

### D-9 — router-agent

**Threat**: Retry storms from worker-2 multiply the load on router-agent when it slows down, turning a brief delay into a sustained outage.

**Category**: denial-of-service | **Original Risk Level**: Critical | **Composite**: 3.5 (Low)

**Correlation Group**: Scores inherited from primary finding R-13 (CG-4). Dimensional detail is recorded on the primary.

**Score**: 3.5 | **Vector**: `CVSS:3.1/AV:A/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N`

---

### E-10 — router-agent

**Threat**: A confused-deputy path lets a low-privilege caller ask router-agent to act on subtask assignments using the privileges of worker-2.

**Category**: privilege-escalation | **Original Risk Level**: Low | **Composite**: 3.5 (Low)

**Correlation Group**: Scores inherited from primary finding R-13 (CG-4). Dimensional detail is recorded on the primary.

**Score**: 3.5 | **Vector**: `CVSS:3.1/AV:A/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N`

---

### AG-11 — router-agent

**Threat**: router-agent can start further agents or processes on request, so a compromised prompt can multiply its reach beyond the intended scope.

**Category**: agentic | **Original Risk Level**: Note | **Composite**: 3.5 (Low)

**Correlation Group**: Scores inherited from primary finding R-13 (CG-4). Dimensional detail is recorded on the primary.

**Score**: 3.5 | **Vector**: `CVSS:3.1/AV:A/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N`

---

### AG-12 — router-agent

**Threat**: router-agent can act on subtask assignments without a human approval step, so a manipulated plan executes high-impact actions with no checkpoint.

**Category**: agentic | **Original Risk Level**: High | **Composite**: 3.5 (Low)

**Correlation Group**: Scores inherited from primary finding R-13 (CG-4). Dimensional detail is recorded on the primary.

**Score**: 3.5 | **Vector**: `CVSS:3.1/AV:A/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N`

---

### AG-13 — router-agent

**Threat**: An attacker chains two individually safe tools through router-agent to reach an outcome neither was approved for, such as an export followed by an upload.

**Category**: agentic | **Original Risk Level**: Critical | **Composite**: 3.5 (Low)

**Correlation Group**: Scores inherited from primary finding R-13 (CG-4). Dimensional detail is recorded on the primary.

**Score**: 3.5 | **Vector**: `CVSS:3.1/AV:A/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N`

---

### R-24 — scheduler-1

**Threat**: Clock drift between scheduler-1 and queue-a2 leaves events in inconsistent order, so the sequence of actions on recurring planning triggers cannot be reconstructed reliably.

**Category**: repudiation | **Original Risk Level**: High | **Composite**: 3.4 (Low)

#### CVSS 3.1 Base

**Score**: 3.1 | **Vector**: `CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:N/I:L/A:N`

| Metric | Value | Rationale |
|--------|-------|-----------|
| Attack Vector (AV) | Network | Reachable over the network |
| Attack Complexity (AC) | High | Needs specific conditions |
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
| Attack Complexity | 4 | Needs some preparation |
| Tooling Availability | 3 | Needs custom tooling |
| Skill Level | 3 | Needs deep expertise |

#### Scalability

**Score**: 4.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 1 | Manual for each target |
| Target Scope | 3 | One specific target |
| Resource Requirements | 8 | Minimal resources |
| Detection Difficulty | 6 | Detectable with monitoring |

#### Reachability

**Score**: 3.5 | **Trust Zone**: Agent Runtime Zone (Trusted)

scheduler-1 sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 3.5.

---

### R-25 — scheduler-1

**Threat**: Delegated actions performed by scheduler-1 on behalf of a user are recorded under the service identity alone, hiding who authorised them.

**Category**: repudiation | **Original Risk Level**: Medium | **Composite**: 3.4 (Low)

**Correlation Group**: Scores inherited from primary finding R-24 (CG-18). Dimensional detail is recorded on the primary.

**Score**: 3.1 | **Vector**: `CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:N/I:L/A:N`

---

### E-27 — scheduler-1

**Threat**: Multi-tenant separation in scheduler-1 depends on a request header that clients can set, allowing one tenant to act in another's scope.

**Category**: privilege-escalation | **Original Risk Level**: High | **Composite**: 3.4 (Low)

**Correlation Group**: Scores inherited from primary finding R-24 (CG-18). Dimensional detail is recorded on the primary.

**Score**: 3.1 | **Vector**: `CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:N/I:L/A:N`

---

### AG-38 — scheduler-1

**Threat**: scheduler-1 can start further agents or processes on request, so a compromised prompt can multiply its reach beyond the intended scope.

**Category**: agentic | **Original Risk Level**: High | **Composite**: 3.4 (Low)

**Correlation Group**: Scores inherited from primary finding R-24 (CG-18). Dimensional detail is recorded on the primary.

**Score**: 3.1 | **Vector**: `CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:N/I:L/A:N`

---

### AG-44 — scheduler-1

**Threat**: scheduler-1 can act on recurring planning triggers without a human approval step, so a manipulated plan executes high-impact actions with no checkpoint.

**Category**: agentic | **Original Risk Level**: Critical | **Composite**: 3.4 (Low)

**Correlation Group**: Scores inherited from primary finding R-24 (CG-18). Dimensional detail is recorded on the primary.

**Score**: 3.1 | **Vector**: `CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:N/I:L/A:N`

---

### R-17 — worker-3

**Threat**: Operators approve changes to work orders and draft documents through a chat message or ticket comment that is not bound to the executed change, so approvals can be disputed.

**Category**: repudiation | **Original Risk Level**: Medium | **Composite**: 3.2 (Low)

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

**Score**: 3.5 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Known Techniques | 3 | Not described outside research |
| Attack Complexity | 4 | Needs some preparation |
| Tooling Availability | 4 | Tools need adaptation |
| Skill Level | 3 | Needs deep expertise |

#### Scalability

**Score**: 6.0 (average of sub-dimensions)

| Sub-Dimension | Score | Rationale |
|---------------|-------|-----------|
| Scriptability | 3 | Manual for each target |
| Target Scope | 3 | One specific target |
| Resource Requirements | 9 | Minimal resources |
| Detection Difficulty | 9 | Blends with normal use |

#### Reachability

**Score**: 2.0 | **Trust Zone**: Agent Runtime Zone (Trusted)

worker-3 sits in the Agent Runtime Zone. The zone baseline is 2.5 and the refinement for this finding gives 2.0.

---

### I-14 — worker-3

**Threat**: A timing or size difference in the responses of worker-3 lets an observer infer whether specific records of work orders and draft documents exist.

**Category**: info-disclosure | **Original Risk Level**: High | **Composite**: 3.2 (Low)

**Correlation Group**: Scores inherited from primary finding R-17 (CG-6). Dimensional detail is recorded on the primary.

**Score**: 2.4 | **Vector**: `CVSS:3.1/AV:N/AC:L/PR:H/UI:R/S:U/C:N/I:L/A:N`

---

### D-11 — worker-3

**Threat**: Retry storms from router-agent multiply the load on worker-3 when it slows down, turning a brief delay into a sustained outage.

**Category**: denial-of-service | **Original Risk Level**: Medium | **Composite**: 3.2 (Low)

**Correlation Group**: Scores inherited from primary finding R-17 (CG-6). Dimensional detail is recorded on the primary.

**Score**: 2.4 | **Vector**: `CVSS:3.1/AV:N/AC:L/PR:H/UI:R/S:U/C:N/I:L/A:N`

---

### D-12 — worker-3

**Threat**: A slow-read attack holds connections to worker-3 open and ties up the workers handling work orders and draft documents until none remain for real requests.

**Category**: denial-of-service | **Original Risk Level**: Medium | **Composite**: 3.2 (Low)

**Correlation Group**: Scores inherited from primary finding R-17 (CG-6). Dimensional detail is recorded on the primary.

**Score**: 2.4 | **Vector**: `CVSS:3.1/AV:N/AC:L/PR:H/UI:R/S:U/C:N/I:L/A:N`

---

### AG-20 — worker-3

**Threat**: worker-3 can act on work orders and draft documents without a human approval step, so a manipulated plan executes high-impact actions with no checkpoint.

**Category**: agentic | **Original Risk Level**: Medium | **Composite**: 3.2 (Low)

**Correlation Group**: Scores inherited from primary finding R-17 (CG-6). Dimensional detail is recorded on the primary.

**Score**: 2.4 | **Vector**: `CVSS:3.1/AV:N/AC:L/PR:H/UI:R/S:U/C:N/I:L/A:N`

---

### AG-22 — worker-3

**Threat**: Tool results returned to worker-3 are fed back into the next prompt without sanitising, so a result can carry instructions for the agent.

**Category**: agentic | **Original Risk Level**: Low | **Composite**: 3.2 (Low)

**Correlation Group**: Scores inherited from primary finding R-17 (CG-6). Dimensional detail is recorded on the primary.

**Score**: 2.4 | **Vector**: `CVSS:3.1/AV:N/AC:L/PR:H/UI:R/S:U/C:N/I:L/A:N`

---

### LLM-14 — worker-3

**Threat**: An attacker splits a payload across several messages so that no single message trips the filter in front of worker-3.

**Category**: llm | **Original Risk Level**: High | **Composite**: 3.2 (Low)

**Correlation Group**: Scores inherited from primary finding R-17 (CG-6). Dimensional detail is recorded on the primary.

**Score**: 2.4 | **Vector**: `CVSS:3.1/AV:N/AC:L/PR:H/UI:R/S:U/C:N/I:L/A:N`

---

## 4. Governance Fields

Remediation tracking metadata for each scored finding. Defaults are severity-driven and intended for manual override during risk review.

| ID | Severity | Owner | SLA | Disposition | Review Date |
|----|----------|-------|-----|-------------|-------------|
| S-3 | Critical | Unassigned | 24h | Mitigate | 2026-10-21 |
| S-1 | High | Unassigned | 7d | Mitigate | 2026-10-27 |
| S-2 | High | Unassigned | 7d | Mitigate | 2026-10-27 |
| S-4 | High | Unassigned | 7d | Mitigate | 2026-10-27 |
| LLM-3 | High | Unassigned | 7d | Mitigate | 2026-10-27 |
| E-3 | High | Unassigned | 7d | Mitigate | 2026-10-27 |
| E-4 | High | Unassigned | 7d | Mitigate | 2026-10-27 |
| D-1 | High | Unassigned | 7d | Mitigate | 2026-10-27 |
| S-5 | High | Unassigned | 7d | Mitigate | 2026-10-27 |
| E-5 | High | Unassigned | 7d | Mitigate | 2026-10-27 |
| T-1 | High | Unassigned | 7d | Mitigate | 2026-10-27 |
| E-1 | High | Unassigned | 7d | Mitigate | 2026-10-27 |
| E-2 | High | Unassigned | 7d | Mitigate | 2026-10-27 |
| LLM-34 | High | Unassigned | 7d | Mitigate | 2026-10-27 |
| I-4 | High | Unassigned | 7d | Mitigate | 2026-10-27 |
| D-3 | High | Unassigned | 7d | Mitigate | 2026-10-27 |
| LLM-50 | High | Unassigned | 7d | Mitigate | 2026-10-27 |
| LLM-11 | High | Unassigned | 7d | Mitigate | 2026-10-27 |
| D-2 | High | Unassigned | 7d | Mitigate | 2026-10-27 |
| OI-8 | High | Unassigned | 7d | Mitigate | 2026-10-27 |
| OI-12 | High | Unassigned | 7d | Mitigate | 2026-10-27 |
| S-40 | High | Unassigned | 7d | Mitigate | 2026-10-27 |
| I-1 | High | Unassigned | 7d | Mitigate | 2026-10-27 |
| I-2 | High | Unassigned | 7d | Mitigate | 2026-10-27 |
| I-43 | High | Unassigned | 7d | Mitigate | 2026-10-27 |
| LLM-1 | High | Unassigned | 7d | Mitigate | 2026-10-27 |
| LLM-2 | High | Unassigned | 7d | Mitigate | 2026-10-27 |
| LLM-18 | High | Unassigned | 7d | Mitigate | 2026-10-27 |
| LLM-41 | High | Unassigned | 7d | Mitigate | 2026-10-27 |
| LLM-47 | High | Unassigned | 7d | Mitigate | 2026-10-27 |
| LLM-48 | High | Unassigned | 7d | Mitigate | 2026-10-27 |
| OI-6 | High | Unassigned | 7d | Mitigate | 2026-10-27 |
| OI-15 | High | Unassigned | 7d | Mitigate | 2026-10-27 |
| OI-16 | High | Unassigned | 7d | Mitigate | 2026-10-27 |
| OI-18 | High | Unassigned | 7d | Mitigate | 2026-10-27 |
| OI-20 | High | Unassigned | 7d | Mitigate | 2026-10-27 |
| OI-21 | High | Unassigned | 7d | Mitigate | 2026-10-27 |
| OI-26 | High | Unassigned | 7d | Mitigate | 2026-10-27 |
| OI-28 | High | Unassigned | 7d | Mitigate | 2026-10-27 |
| S-33 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| LLM-5 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| LLM-10 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| LLM-57 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| LLM-58 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| OI-7 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| OI-14 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| MI-4 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| MI-9 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| MI-10 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| LLM-6 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| LLM-27 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| OI-9 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| OI-22 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| MI-2 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| MI-8 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| D-36 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| LLM-43 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| OI-4 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| MI-11 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| S-9 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| I-3 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| I-5 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| D-7 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| D-8 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| D-27 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| LLM-53 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| OI-10 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| OI-25 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| MI-1 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| MI-18 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| TE-4 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| S-41 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| D-20 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| D-31 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| E-22 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| E-34 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| AGP-02 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| AGP-03 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| LLM-35 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| OI-11 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| OI-23 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| MI-13 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| S-32 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| E-15 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| E-29 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| AG-18 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| AG-26 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| LLM-8 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| LLM-15 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| LLM-28 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| MI-7 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| MI-15 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| TE-9 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| S-7 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| D-6 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| D-17 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| D-22 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| D-34 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| E-23 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| E-30 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| AG-27 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| LLM-9 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| LLM-21 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| LLM-31 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| LLM-36 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| OI-1 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| MI-16 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| MI-19 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| TE-1 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| S-15 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| S-23 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| S-31 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| R-2 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| R-31 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| AG-33 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| LLM-52 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| MI-3 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| MI-20 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| S-6 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| S-10 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| S-42 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| T-25 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| D-35 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| E-17 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| E-28 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| E-32 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| LLM-33 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| OI-2 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| OI-3 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| MI-5 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| MI-12 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| TE-3 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| TE-5 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| TE-10 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| TE-17 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| S-13 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| S-36 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| T-2 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| R-1 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| D-16 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| E-19 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| E-20 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| AG-3 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| AG-31 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| LLM-26 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| LLM-55 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| LLM-56 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| OI-5 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| MI-6 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| MI-17 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| TE-11 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| S-8 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| S-24 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| S-39 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| T-26 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| R-5 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| I-9 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| I-34 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| D-26 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| D-29 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| D-32 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| D-33 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| E-25 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| AG-29 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| AG-30 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| AG-37 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| AG-43 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| LLM-20 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| LLM-30 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| OI-17 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| OI-24 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| TE-14 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| S-12 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| S-16 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| S-22 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| S-30 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| T-32 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| T-41 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| R-6 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| D-30 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| E-13 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| E-14 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| E-18 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| AG-41 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| OI-13 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| OI-27 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| MI-14 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| TE-15 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| S-11 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| S-21 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| R-7 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| R-23 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| I-47 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| D-13 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| D-18 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| D-24 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| D-28 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| D-39 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| E-26 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| E-33 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| AG-23 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| AG-28 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| AG-35 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| AG-36 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| LLM-49 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| OI-19 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| TE-13 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| T-23 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| I-25 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| I-28 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| D-23 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| AG-6 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| AG-9 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| AG-10 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| AG-14 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| AG-17 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| LLM-29 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| TE-8 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| S-20 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| S-43 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| T-19 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| T-35 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| I-10 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| I-31 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| I-42 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| E-21 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| E-31 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| AG-21 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| AG-42 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| LLM-23 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| TE-2 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| S-14 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| S-25 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| S-38 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| T-7 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| T-8 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| T-24 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| T-39 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| D-21 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| D-38 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| AG-7 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| LLM-32 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| S-29 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| S-37 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| T-3 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| T-16 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| T-17 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| T-30 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| T-31 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| T-42 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| T-45 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| I-16 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| I-17 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| I-24 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| I-40 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| I-41 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| D-14 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| D-15 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| E-11 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| AG-34 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| LLM-17 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| LLM-24 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| LLM-25 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| LLM-39 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| TE-7 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| S-27 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| T-33 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| I-45 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| D-5 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| D-19 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| AG-8 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| TE-12 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| S-18 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| T-9 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| T-11 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| T-29 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| T-37 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| T-38 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| T-43 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| R-3 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| I-46 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| D-25 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| E-24 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| AG-32 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| LLM-44 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| LLM-45 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| LLM-46 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| T-4 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| T-10 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| T-12 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| T-13 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| T-34 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| I-8 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| I-36 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| E-7 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| TE-6 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| S-26 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| T-14 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| T-15 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| T-44 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| I-23 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| I-30 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| D-37 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| LLM-22 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| T-36 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| I-26 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| I-37 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| I-38 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| AGP-01 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| LLM-40 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| LLM-42 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| S-17 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| S-19 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| S-34 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| T-27 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| T-28 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| I-13 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| I-18 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| I-21 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| I-22 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| I-29 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| D-10 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| E-12 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| AG-15 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| AG-16 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| AG-19 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| LLM-13 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| LLM-37 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| LLM-38 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| TE-16 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| S-28 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| T-5 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| T-21 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| T-47 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| I-19 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| I-32 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| LLM-19 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| LLM-54 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| T-6 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| R-18 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| R-27 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| I-11 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| I-15 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| I-27 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| E-16 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| AG-24 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| AG-25 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| LLM-16 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| T-46 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| I-35 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| T-20 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| R-30 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| LLM-59 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| R-8 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| R-22 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| I-6 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| I-44 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| E-6 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| AG-1 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| AG-2 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| LLM-4 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| T-22 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| T-40 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| R-12 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| R-15 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| R-26 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| R-28 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| R-29 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| R-33 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| I-12 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| I-33 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| I-39 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| AG-39 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| AG-40 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| LLM-51 | Medium | Unassigned | 30d | Review | 2026-11-19 |
| R-16 | Low | Unassigned | 90d | Review | 2027-01-18 |
| R-10 | Low | Unassigned | 90d | Review | 2027-01-18 |
| R-9 | Low | Unassigned | 90d | Review | 2027-01-18 |
| R-14 | Low | Unassigned | 90d | Review | 2027-01-18 |
| R-20 | Low | Unassigned | 90d | Review | 2027-01-18 |
| I-7 | Low | Unassigned | 90d | Review | 2027-01-18 |
| E-8 | Low | Unassigned | 90d | Review | 2027-01-18 |
| E-9 | Low | Unassigned | 90d | Review | 2027-01-18 |
| AG-4 | Low | Unassigned | 90d | Review | 2027-01-18 |
| AG-5 | Low | Unassigned | 90d | Review | 2027-01-18 |
| LLM-7 | Low | Unassigned | 90d | Review | 2027-01-18 |
| R-11 | Low | Unassigned | 90d | Review | 2027-01-18 |
| R-21 | Low | Unassigned | 90d | Review | 2027-01-18 |
| R-32 | Low | Unassigned | 90d | Review | 2027-01-18 |
| R-13 | Low | Unassigned | 90d | Review | 2027-01-18 |
| R-19 | Low | Unassigned | 90d | Review | 2027-01-18 |
| D-9 | Low | Unassigned | 90d | Review | 2027-01-18 |
| E-10 | Low | Unassigned | 90d | Review | 2027-01-18 |
| AG-11 | Low | Unassigned | 90d | Review | 2027-01-18 |
| AG-12 | Low | Unassigned | 90d | Review | 2027-01-18 |
| AG-13 | Low | Unassigned | 90d | Review | 2027-01-18 |
| R-24 | Low | Unassigned | 90d | Review | 2027-01-18 |
| R-25 | Low | Unassigned | 90d | Review | 2027-01-18 |
| E-27 | Low | Unassigned | 90d | Review | 2027-01-18 |
| AG-38 | Low | Unassigned | 90d | Review | 2027-01-18 |
| AG-44 | Low | Unassigned | 90d | Review | 2027-01-18 |
| R-17 | Low | Unassigned | 90d | Review | 2027-01-18 |
| I-14 | Low | Unassigned | 90d | Review | 2027-01-18 |
| D-11 | Low | Unassigned | 90d | Review | 2027-01-18 |
| D-12 | Low | Unassigned | 90d | Review | 2027-01-18 |
| AG-20 | Low | Unassigned | 90d | Review | 2027-01-18 |
| AG-22 | Low | Unassigned | 90d | Review | 2027-01-18 |
| LLM-14 | Low | Unassigned | 90d | Review | 2027-01-18 |

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
