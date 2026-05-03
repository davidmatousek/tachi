---
schema_version: "1.8"
date: "2026-05-01"
input_format: "mermaid"
classification: "confidential"
run_id: "2026-05-01T09-00-00"
baseline:
  source: null
  date: null
  finding_count: null
  run_id: null
coverage_gate:
  status: "pass"
  gaps: []
has-source-attribution: true
---

# F-A3 Wave 2 Fixture — Agent-Autonomy Host Populator Wiring

Validates that `tachi-agent-autonomy` agent emits `source_attribution` arrays
with one `relationship: primary` entry plus ≥1 `relationship: related` CWE entry,
mirroring the F-1/F-2/F-4 net-new agent precedent per ADR-037 D-3. Cites
ASI-01/06/08/10 + LLM06 primaries across the four example findings per Architect
HIGH-A directive. ASI-09 autonomy-axis remains attributed here per F-4 ADR-033 D-2
(communication-axis carved to `tachi-human-trust-exploitation`).

## 7. Recommended Actions

| Finding ID | Category | Pattern | Component | Threat | Risk Level | Mitigation |
|------------|----------|---------|-----------|--------|------------|------------|
| AG-1 | agentic | Unbounded Agent Loop | Task Automation Agent | No max iteration / timeout / cost cap on LLM-driven termination decision | High | Mandatory iteration count + execution timeout + cost cap + circuit breaker on action repetition |
| AG-2 | agentic | Autonomous Irreversible Actions | Infrastructure Management Agent | Tool access does not distinguish reversible vs irreversible operations; no human approval gate | High | Reversibility-tier classification (T1 read-only / T2 reversible / T3 irreversible) + human approval on T3 |
| AG-3 | agentic | Cascading Multi-Agent Failure | Multi-Agent Orchestrator | Downstream agents trust upstream output without independent validation | Medium | Inter-agent output validation + independent verification against original user intent + circuit breaker on confidence drop |
| AG-4 | agentic | Goal Misalignment via Proxy Metric | Content Optimization Agent | Agent optimizes proxy metric (CTR) diverging from user's true intent (quality engagement) | Medium | Multi-dimensional success criteria + constraint-metric guardrails + periodic human review |

## 9. Source Attribution

```yaml
AG-1:
  - {taxonomy: owasp, id: "ASI-10", relationship: primary}
  - {taxonomy: owasp, id: "ASI-01", relationship: related}
  - {taxonomy: cwe, id: "CWE-693", relationship: related}

AG-2:
  - {taxonomy: owasp, id: "ASI-08", relationship: primary}
  - {taxonomy: owasp, id: "ASI-01", relationship: related}
  - {taxonomy: cwe, id: "CWE-285", relationship: related}

AG-3:
  - {taxonomy: owasp, id: "ASI-06", relationship: primary}
  - {taxonomy: owasp, id: "ASI-01", relationship: related}
  - {taxonomy: cwe, id: "CWE-345", relationship: related}

AG-4:
  - {taxonomy: owasp, id: "ASI-01", relationship: primary}
  - {taxonomy: owasp, id: "ASI-09", relationship: related}
  - {taxonomy: cwe, id: "CWE-693", relationship: related}
```
