# Attack Tree: T-9 — Risk Stratification Model Fine-Tuning Data Tampering

**Component**: Risk Stratification Model | **Risk Level**: High | **Finding**: T-9

An attacker tampers with fine-tuning data or inference inputs to the Risk Stratification Model, causing systematically biased risk scores leading to incorrect clinical decisions.

```mermaid
flowchart TD
    T9_root["Cause biased clinical risk scores via Risk Stratification Model fine-tuning data tampering"]
    T9_or1{{"OR"}}
    T9_leaf1["Gain write access to fine-tuning training dataset and inject adversarially labeled samples"]
    T9_leaf2["Tamper with inference inputs to model by intercepting API Gateway forwarding path"]
    T9_leaf3["Corrupt training labels for high-risk patient samples to cause systematic misclassification"]

    T9_root --> T9_or1
    T9_or1 --> T9_leaf1
    T9_or1 --> T9_leaf2
    T9_or1 --> T9_leaf3

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class T9_root goal
    class T9_or1 orGate
    class T9_leaf1,T9_leaf2,T9_leaf3 leaf
```
