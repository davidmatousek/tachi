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

# F-A3 Wave 2 Fixture — Model-Theft Host Populator Wiring

Validates that `tachi-model-theft` agent emits `source_attribution` arrays with
one `relationship: primary` entry plus ≥1 `relationship: related` CWE entry,
mirroring the F-1/F-2/F-4 net-new agent precedent per ADR-037 D-3. Cites ML03
primary on the API-extraction finding (Model Inversion / Cat 12) and ML06
primary on the artifact-side supply chain finding per F-6 ADR-035 lineage.

## 7. Recommended Actions

| Finding ID | Category | Pattern | Component | Threat | Risk Level | Mitigation |
|------------|----------|---------|-----------|--------|------------|------------|
| LLM-2 | llm | Model Inversion via Logprob-Exposing Inference API (Cat 12) | Model Inference API | API returns full log-probability distributions enabling distillation extraction | High | Restrict API output to top-k predictions + per-API-key query budgets + watermark outputs |
| LLM-4 | llm | Predictive-ML Artifact Supply Chain — Unsigned Weight Promotion (Cat 14) | MLflow Model Registry | Manual UI promotion without signed-artifact policy, no signature/checksum/lineage on production-promoted weights | High | Sigstore-signed weight binaries + dual-control on production promotion + versioned audit log tied to training-run lineage |

## 9. Source Attribution

```yaml
LLM-2:
  - {taxonomy: owasp, id: "ML03:2023", relationship: primary}
  - {taxonomy: cwe, id: "CWE-200", relationship: related}

LLM-4:
  - {taxonomy: owasp, id: "ML06:2023", relationship: primary}
  - {taxonomy: cwe, id: "CWE-494", relationship: related}
  - {taxonomy: cwe, id: "CWE-345", relationship: related}
```
