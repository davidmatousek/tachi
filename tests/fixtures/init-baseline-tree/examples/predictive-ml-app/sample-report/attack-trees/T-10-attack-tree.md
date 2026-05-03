---
finding: "T-10"
component: "FraudDetectionML Prediction API"
category: "tampering"
risk_level: "Critical"
pattern_category: 10
owasp_reference: "OWASP ML01:2023"
classification: "confidential"
---

# Attack Tree — T-10: Adversarial Input Manipulation Against Deployed Predictive Classifier

**Goal**: Evade fraud detection by submitting adversarially-crafted transaction features to the FraudDetectionML Prediction API.

```mermaid
graph TD
    G[Goal: Evade Fraud Detection]
    G --> A1[Probe Decision Boundary]
    G --> A2[Craft Adversarial Perturbation]
    G --> A3[Submit Adversarial Transaction]
    G --> A4[Sustained Evasion at Scale]

    A1 --> B1[Submit candidate transactions; observe confidence outputs]
    A1 --> B2[Use response confidence to map decision boundary]

    A2 --> C1[FGSM-style gradient approximation]
    A2 --> C2[Black-box optimization against API output]
    A2 --> C3[Physical-world adversarial pattern]

    A3 --> D1[Submit perturbed transaction]
    D1 --> E1[Receive low fraud score]
    D1 --> E2[Transaction routed as legitimate]

    A4 --> F1[Distribute attacks across merchant accounts]
    F1 --> F2[Avoid per-merchant rate-limit triggers]
    F2 --> F3[Launder fraudulent volume undetected]

    style G fill:#d4183d,color:#fff
    style E2 fill:#ff6b6b
    style F3 fill:#ff6b6b
```

## Attack Steps

1. **Probe**: Attacker registers merchant developer account; iterates queries against `/predict` endpoint observing returned confidence values.
2. **Craft**: Using observed confidences, attacker computes feature-space perturbations (small modifications to `geo_distance`, `time_delta`) calibrated against the classifier's decision boundary.
3. **Evade**: Attacker submits the perturbed transaction; the deployed classifier (trained without adversarial training, no input-validation barrier, no statistical-anomaly detection on inputs) misclassifies as legitimate.
4. **Scale**: Attacker repeats across distributed accounts; per-merchant rate limits do not catch the cross-account attack pattern.

## Mitigations (Map to Attack Steps)

- **Probe** → query-rate throttling per tenant; model-extraction-pattern detection (cross-references with LLM-1 mitigation).
- **Craft** → adversarial training (FGSM/PGD) on the model side reduces decision-boundary exploitability.
- **Evade** → statistical-anomaly detection at the input boundary; ensemble disagreement detection on safety-critical decisions.
- **Scale** → cross-account anomaly detection; confidence-thresholding HITL escalation on borderline predictions.

## References

- OWASP ML01:2023 — Input Manipulation Attack
- CWE-20 — Improper Input Validation
- CWE-1039 — Inadequate Detection or Handling of Adversarial Input Perturbations
- MITRE ATLAS AML.T0015 — Evade ML Model (text-only cross-reference; not catalog-resolvable)
