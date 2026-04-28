---
finding: "LLM-1"
component: "FraudDetectionML Prediction API"
category: "model-theft"
risk_level: "Critical"
pattern_category: 12
owasp_reference: "OWASP ML03:2023"
classification: "confidential"
---

# Attack Tree — LLM-1: Model Inversion via Prediction-API Confidence Outputs

**Goal**: Reconstruct training-set inputs by black-box optimization against the FraudDetectionML Prediction API.

```mermaid
graph TD
    G[Goal: Reconstruct Training-Set Merchant Transactions]
    G --> A1[Register API Access]
    G --> A2[Black-Box Optimization Campaign]
    G --> A3[Reconstruct Sensitive Features]

    A1 --> B1[Acquire developer credentials]
    A1 --> B2[Bypass per-tenant query throttling absent]

    A2 --> C1[Iterate gradient-free queries]
    A2 --> C2[Maximize confidence for target class]
    A2 --> C3[Exploit deterministic confidence outputs]

    A3 --> D1[Reconstructed inputs preserve geographic-distance distribution]
    A3 --> D2[Reconstructed inputs preserve transaction-amount distribution]
    A3 --> D3[Reconstructed inputs preserve time-delta distribution]
    A3 --> D4[Identify training-set merchants]

    style G fill:#d4183d,color:#fff
    style D4 fill:#ff6b6b
```

## Attack Steps

1. **Acquire access**: Attacker registers a developer merchant account.
2. **Optimize**: Attacker performs ~200k black-box optimization queries iterating against the prediction endpoint, exploiting deterministic confidence outputs (no output-perturbation noise). Query-rate throttling is absent. Extraction-pattern detection is absent.
3. **Reconstruct**: After convergence, the synthetic inputs that maximize predicted fraud probability for a target class preserve merchant-identifying features (geographic-distance, amount, time-delta distributions of training-set merchants).
4. **Identify**: Attacker correlates reconstructed inputs with public merchant data to identify which specific merchants and transactions were in the training set.

## Mitigations

- Apply differential privacy on training (DP-SGD) with bounded ε ≤ 8.0 — bounds per-example gradient leakage.
- Install output-perturbation noise injection at inference time — calibrated Gaussian/Laplace noise defeats reconstruction.
- Enforce query-rate throttling per tenant — limits sustained optimization campaigns.
- Implement model-extraction-pattern detection — query-entropy tracking, near-duplicate detection, high-coverage sampling-pattern detection.

## References

- OWASP ML03:2023 — Model Inversion Attack
- MITRE ATLAS AML.T0024 — Exfiltration via ML Inference API
