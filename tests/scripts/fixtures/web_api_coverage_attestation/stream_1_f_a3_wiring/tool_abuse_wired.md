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

# F-A3 Wave 2 Fixture — Tool-Abuse Host Populator Wiring

Validates that `tachi-tool-abuse` agent emits `source_attribution` arrays with
one `relationship: primary` entry plus ≥1 `relationship: related` CWE entry,
mirroring the F-1/F-2/F-4 net-new agent precedent per ADR-037 D-3. Cites ASI-07
primary on the inter-agent communication finding per F-3 ADR-032 lineage.

## 7. Recommended Actions

| Finding ID | Category | Pattern | Component | Threat | Risk Level | Mitigation |
|------------|----------|---------|-----------|--------|------------|------------|
| AG-4 | agentic | Insecure Inter-Agent Communication (Cat 9) | Inter-Agent Communication Channel | Two specialized agents communicate via MCP-to-MCP bridge that propagates tool capabilities without per-message authentication | High | Per-message HMAC/mTLS authentication + per-bridge capability scoping + multi-hop trust-chain validation |

## 9. Source Attribution

```yaml
AG-4:
  - {taxonomy: owasp, id: "ASI-07", relationship: primary}
  - {taxonomy: cwe, id: "CWE-287", relationship: related}
  - {taxonomy: cwe, id: "CWE-345", relationship: related}
```
