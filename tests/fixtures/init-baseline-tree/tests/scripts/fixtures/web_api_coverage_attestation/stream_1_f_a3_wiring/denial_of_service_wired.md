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

# F-A3 Wave 2 Fixture — Denial-of-Service Host Populator Wiring

Validates that `tachi-denial-of-service` agent emits `source_attribution` arrays
with one `relationship: primary` entry plus ≥1 `relationship: related` CWE entry,
mirroring the F-1/F-2/F-4 net-new agent precedent per ADR-037 D-3. Cites
LLM10:2025 primary on the LLM inference-exhaustion finding per F-5 ADR-034
lineage.

## 7. Recommended Actions

| Finding ID | Category | Pattern | Component | Threat | Risk Level | Mitigation |
|------------|----------|---------|-----------|--------|------------|------------|
| D-3 | denial-of-service | LLM Inference-Request Flooding (Cat 12) | LLM Inference Service | Public-facing LLM inference endpoint accepts unbounded prompt sizes and concurrent inference requests | Critical | Per-tenant rate limits + token budgets + concurrency caps + cost-per-tenant alerts |

## 9. Source Attribution

```yaml
D-3:
  - {taxonomy: owasp, id: "LLM10:2025", relationship: primary}
  - {taxonomy: cwe, id: "CWE-770", relationship: related}
  - {taxonomy: cwe, id: "CWE-400", relationship: related}
```
