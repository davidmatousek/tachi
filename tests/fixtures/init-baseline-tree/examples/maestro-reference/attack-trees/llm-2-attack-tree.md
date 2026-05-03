# Attack Tree: LLM-2 — Clinical LLM Training Data Poisoning via Learning Loop

**Component**: Clinical LLM | **Risk Level**: High | **Finding**: LLM-2

An adversary poisons the training data or fine-tuning feedback incorporated into the Clinical LLM via the Outcomes Telemetry learning loop, causing the model to produce systematically biased or manipulated clinical completions after re-training.

```mermaid
flowchart TD
    LLM2_root["Cause Clinical LLM systematic output bias via training data poisoning through Outcomes Telemetry learning loop"]
    LLM2_or1{{"OR"}}
    LLM2_leaf1["Inject adversarial physician-override signals into Outcomes Telemetry to corrupt learning loop feedback"]
    LLM2_leaf2["Tamper with fine-tuning dataset before learning loop re-training cycle to embed adversarial patterns"]
    LLM2_leaf3["Exploit absent behavioral baselining to deploy poisoned model without drift detection triggering"]

    LLM2_root --> LLM2_or1
    LLM2_or1 --> LLM2_leaf1
    LLM2_or1 --> LLM2_leaf2
    LLM2_or1 --> LLM2_leaf3

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class LLM2_root goal
    class LLM2_or1 orGate
    class LLM2_leaf1,LLM2_leaf2,LLM2_leaf3 leaf
```
