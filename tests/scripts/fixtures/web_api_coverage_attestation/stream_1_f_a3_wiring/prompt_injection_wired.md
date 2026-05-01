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

# F-A3 Wave 2 Fixture — Prompt-Injection Host Populator Wiring

Validates that `tachi-prompt-injection` agent emits `source_attribution` arrays
with one `relationship: primary` entry plus ≥1 `relationship: related` CWE entry,
mirroring the F-1/F-2/F-4 net-new agent precedent per ADR-037 D-3. Cites
LLM01:2025 primary on direct-injection / indirect-injection / jailbreak findings
per Architect HIGH-A directive.

## 7. Recommended Actions

| Finding ID | Category | Pattern | Component | Threat | Risk Level | Mitigation |
|------------|----------|---------|-----------|--------|------------|------------|
| LLM-1 | llm | Direct Prompt Injection via Chat Interface | Customer Support Chatbot | User chat messages concatenated directly into LLM prompt without sanitization or boundary enforcement | Critical | Structured prompt templates + delimiter tokens + adversarial input classifier + output filtering |

## 9. Source Attribution

```yaml
LLM-1:
  - {taxonomy: owasp, id: "LLM01:2025", relationship: primary}
  - {taxonomy: cwe, id: "CWE-77", relationship: related}
  - {taxonomy: cwe, id: "CWE-94", relationship: related}
```
