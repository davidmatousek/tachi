# Attack Tree: LLM-5 — Risk Stratification Model Fine-Tuning Dataset Poisoning

**Component**: Risk Stratification Model | **Risk Level**: High | **Finding**: LLM-5

An adversary poisons the supervised fine-tuning dataset used to train the Risk Stratification Model, embedding adversarial patterns that cause the model to systematically misclassify high-risk patients as low-risk after re-training.

```mermaid
flowchart TD
    LLM5_root["Cause systematic high-risk patient misclassification via Risk Stratification Model fine-tuning dataset poisoning"]
    LLM5_or1{{"OR"}}
    LLM5_leaf1["Gain write access to fine-tuning dataset and inject adversarially mislabeled high-risk patient samples"]
    LLM5_leaf2["Exploit absent dataset integrity verification to inject poisoned samples before training run"]
    LLM5_leaf3["Wait for model re-training cycle to incorporate poisoned labels causing systematic classification drift"]

    LLM5_root --> LLM5_or1
    LLM5_or1 --> LLM5_leaf1
    LLM5_or1 --> LLM5_leaf2
    LLM5_or1 --> LLM5_leaf3

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class LLM5_root goal
    class LLM5_or1 orGate
    class LLM5_leaf1,LLM5_leaf2,LLM5_leaf3 leaf
```
