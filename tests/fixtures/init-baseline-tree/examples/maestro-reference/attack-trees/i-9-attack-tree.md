# Attack Tree: I-9 — Risk Stratification Model Membership Inference Attack

**Component**: Risk Stratification Model | **Risk Level**: High | **Finding**: I-9

The Risk Stratification Model may leak patient cohort data from its fine-tuning training set through membership inference attacks or overfitted responses revealing individual patient characteristics.

```mermaid
flowchart TD
    I9_root["Determine fine-tuning training set membership to identify patients via Risk Stratification Model inference attack"]
    I9_or1{{"OR"}}
    I9_leaf1["Craft patient record queries matching suspected training samples and observe confidence scores"]
    I9_leaf2["Compare model output confidence differentials between training and non-training patient presentations"]
    I9_leaf3["Exploit overfitted model responses revealing individual patient characteristics from training data"]

    I9_root --> I9_or1
    I9_or1 --> I9_leaf1
    I9_or1 --> I9_leaf2
    I9_or1 --> I9_leaf3

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class I9_root goal
    class I9_or1 orGate
    class I9_leaf1,I9_leaf2,I9_leaf3 leaf
```
