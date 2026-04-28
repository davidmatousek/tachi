---
finding: "D-11"
component: "Feast Feature Store"
category: "data-poisoning"
risk_level: "Critical"
pattern_category: 10
owasp_reference: "OWASP ML06:2023 (corpus-side, shared with D-10)"
classification: "confidential"
---

# Attack Tree — D-11: Feast Feature Store Mutation

**Goal**: Mutate engineered-feature values in the Feast Feature Store to skew inference outputs.

```mermaid
graph TD
    G[Goal: Mutate Feature Store Values]
    G --> A1[Compromise Service Account]
    G --> A2[Write Mutation]
    G --> A3[Read at Inference Without Verification]

    A1 --> B1[Stolen IAM credentials]
    A1 --> B2[Compromised CI runner]

    A2 --> C1[Mutate engineered feature value]
    A2 --> C2[No IAM-enforced write-audit]
    A2 --> C3[No promotion-gate review on feature tables]

    A3 --> D1[Prediction API queries Feast]
    A3 --> D2[Cached feature vector returned]
    A3 --> D3[No integrity verification on feature read]
    A3 --> D4[Inference uses tampered feature]

    style G fill:#d4183d,color:#fff
    style D4 fill:#ff6b6b
```

## Mitigations

- Apply IAM with per-write audit on the feature store.
- Verify feature-vector integrity at read time on the prediction API.
- Monitor for anomalous feature-distribution drift between writes.
- Require pull-request review for write-access grants on production feature tables.

## References

- OWASP ML06:2023 — AI Supply Chain Attacks (corpus-side facet)
- MITRE ATT&CK T1195 — Supply Chain Compromise
