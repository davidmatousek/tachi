---
finding: "D-10"
component: "Model Training Pipeline"
category: "data-poisoning"
risk_level: "Critical"
pattern_category: 10
owasp_reference: "OWASP ML06:2023 (corpus-side facet)"
classification: "confidential"
---

# Attack Tree — D-10: Predictive-ML Corpus Supply Chain

**Goal**: Inject biased or backdoored training signal into the production fraud-detection model via any of three corpus-side surfaces.

```mermaid
graph TD
    G[Goal: Compromise Training Corpus]
    G --> A1[Vector 1: Public Dataset Repository]
    G --> A2[Vector 2: Internal Merchant History]
    G --> A3[Vector 3: Feast Feature Store]

    A1 --> B1[Publish poisoned-update of dataset]
    A1 --> B2[No checksum manifest verification]
    A1 --> B3[No SHA-256 digest comparison]

    A2 --> C1[Compromise internal training corpus write path]
    A2 --> C2[No IAM-enforced write-audit]
    A2 --> C3[Multiple service accounts with write access]

    A3 --> D1[Mutate engineered feature value]
    A3 --> D2[No IAM-enforced write-audit on feature store]
    A3 --> D3[No promotion-gate review]

    G --> E1[Training Pipeline Ingests Compromised Data]
    E1 --> E2[Backdoored model trained]
    E1 --> E3[Promoted to production via MLflow]
    E1 --> E4[Backdoor activates in production inference]

    style G fill:#d4183d,color:#fff
    style E4 fill:#ff6b6b
```

## Mitigations

- Maintain dataset-checksum manifest with reproducibility verification.
- Apply IAM-enforced write-audit on feature stores and training corpus.
- Require model-card review as a promotion gate.
- Enforce signed-artifact policy at the MLOps registry boundary (cross-references LLM-3).

## References

- OWASP ML06:2023 — AI Supply Chain Attacks (corpus-side facet per ADR-035 Decision 4)
- MITRE ATT&CK T1195 + T1195.001 + T1195.002 — Supply Chain Compromise
