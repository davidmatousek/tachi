# Attack Tree: LLM-6 — Risk Stratification Model Membership Inference Privacy Attack

**Component**: Risk Stratification Model | **Risk Level**: High | **Finding**: LLM-6

An adversary conducts membership inference attacks against the Risk Stratification Model to determine which patients were included in the fine-tuning dataset, violating patient privacy even without direct data access.

```mermaid
flowchart TD
    LLM6_root["Determine patient training set membership via membership inference attack on Risk Stratification Model"]
    LLM6_or1{{"OR"}}
    LLM6_leaf1["Issue systematic inference queries for suspected training set patient records via API Gateway"]
    LLM6_leaf2["Measure model confidence differentials to distinguish training members from non-members"]
    LLM6_leaf3["Exploit absent differential privacy to extract definitive membership signals from model output patterns"]

    LLM6_root --> LLM6_or1
    LLM6_or1 --> LLM6_leaf1
    LLM6_or1 --> LLM6_leaf2
    LLM6_or1 --> LLM6_leaf3

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class LLM6_root goal
    class LLM6_or1 orGate
    class LLM6_leaf1,LLM6_leaf2,LLM6_leaf3 leaf
```
