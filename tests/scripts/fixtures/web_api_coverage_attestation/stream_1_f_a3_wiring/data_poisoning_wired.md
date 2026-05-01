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

# F-A3 Wave 2 Fixture — Data-Poisoning Host Populator Wiring

Validates that `tachi-data-poisoning` agent emits `source_attribution` arrays
with one `relationship: primary` entry plus ≥1 `relationship: related` CWE entry,
mirroring the F-1/F-2/F-4 net-new agent precedent per ADR-037 D-3. Cites ML06
primary on the predictive-ML supply chain corpus-side finding per F-6 ADR-035
corpus-side lineage.

## 7. Recommended Actions

| Finding ID | Category | Pattern | Component | Threat | Risk Level | Mitigation |
|------------|----------|---------|-----------|--------|------------|------------|
| LLM-3 | llm | Predictive-ML Public Dataset Supply Chain Completeness Gap (Cat 10) | Public Dataset Repository | Public-repository dataset ingestion without checksum manifest, signed-publisher attestation, or integrity check | High | Pin dataset versions by content-hash digest + sigstore publisher attestation + label-distribution drift detection |

## 9. Source Attribution

```yaml
LLM-3:
  - {taxonomy: owasp, id: "ML06:2023", relationship: primary}
  - {taxonomy: cwe, id: "CWE-494", relationship: related}
  - {taxonomy: cwe, id: "CWE-1395", relationship: related}
```
