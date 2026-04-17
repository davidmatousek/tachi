# Attack Tree: I-8 — Clinical LLM Training Data PHI Memorization

**Component**: Clinical LLM | **Risk Level**: High | **Finding**: I-8

The Clinical LLM may memorize and surface sensitive training data including patient records in its completions, disclosing PHI to agents that did not have authorization to access it.

```mermaid
flowchart TD
    I8_root["Extract patient PHI from Clinical LLM training data via completion-based memorization attack"]
    I8_or1{{"OR"}}
    I8_leaf1["Craft targeted query designed to trigger memorized patient-specific clinical training data"]
    I8_leaf2["Issue systematic extraction queries to identify PHI-containing completions via API Gateway"]
    I8_leaf3["Collect PHI surfaced in completion responses lacking differential privacy protection"]

    I8_root --> I8_or1
    I8_or1 --> I8_leaf1
    I8_or1 --> I8_leaf2
    I8_or1 --> I8_leaf3

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class I8_root goal
    class I8_or1 orGate
    class I8_leaf1,I8_leaf2,I8_leaf3 leaf
```
