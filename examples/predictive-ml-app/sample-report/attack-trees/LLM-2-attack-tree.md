---
finding: "LLM-2"
component: "FraudDetectionML Prediction API"
category: "model-theft"
risk_level: "Critical"
pattern_category: 13
owasp_reference: "OWASP ML04:2023"
classification: "confidential"
---

# Attack Tree — LLM-2: Membership Inference via Confidence-Thresholding

**Goal**: Determine whether specific candidate transactions were used to train the FraudDetectionML classifier.

```mermaid
graph TD
    G[Goal: Determine Training-Set Membership]
    G --> A1[Acquire Candidate List]
    G --> A2[Submit Each Candidate]
    G --> A3[Confidence-Threshold Attack]
    G --> A4[Identify Training Members]

    A1 --> B1[Breach external transaction database]
    A1 --> B2[Compile candidate transaction list]

    A2 --> C1[Submit candidate to /predict endpoint]
    A2 --> C2[Receive full-precision confidence value]

    A3 --> D1[Train shadow model on similar public data]
    A3 --> D2[Compare confidence patterns]
    A3 --> D3[Apply threshold rule on confidence delta]

    A4 --> E1[Training members return high-confidence scores]
    A4 --> E2[Identify which merchants flagged in training]
    A4 --> E3[Expose private fraud-investigation status]

    style G fill:#d4183d,color:#fff
    style E3 fill:#ff6b6b
```

## Attack Steps

1. **Acquire candidates**: Attacker obtains list of candidate transactions from a separate breach.
2. **Submit each**: For each candidate, attacker submits to `/predict` endpoint and observes returned confidence.
3. **Threshold attack**: Attacker trains shadow models on similar public fraud data; compares production-API confidence patterns; applies confidence-thresholding to determine training-set membership.
4. **Identify**: Members return characteristic high-confidence scores (model memorizes training examples without DP-SGD or training-data minimization). Attacker now knows which merchants and which specific transactions were in the training set.

## Mitigations

- Apply differential privacy on training (DP-SGD) with bounded ε ≤ 8.0.
- Apply confidence-output truncation (round to 1–2 decimal places) — defeats threshold attacks.
- Enable label-only response mode for sensitive endpoints.
- Enforce query-rate throttling per tenant — limits large-scale candidate enumeration.
- Apply training-data minimization — redact or aggregate sensitive subsets.

## References

- OWASP ML04:2023 — Membership Inference Attack
- MITRE ATLAS AML.T0024 — Exfiltration via ML Inference API
