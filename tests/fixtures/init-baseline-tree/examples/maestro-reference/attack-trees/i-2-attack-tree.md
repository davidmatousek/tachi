# Attack Tree: I-2 — Patient Summary Unauthorized PHI Disclosure

**Component**: Patient Summary Generator | **Risk Level**: High | **Finding**: I-2

Patient-facing summaries may inadvertently include sensitive clinical details beyond the authorized disclosure scope, or may be delivered to wrong patients due to missing identity validation.

```mermaid
flowchart TD
    I2_root["Disclose PHI beyond authorized scope via Patient Summary Generator delivery failure"]
    I2_or1{{"OR"}}
    I2_leaf1["Exploit absent patient identity verification to request summary for unauthorized patient"]
    I2_leaf2["Trigger summary generation including out-of-scope sensitive clinical details via crafted request"]
    I2_leaf3["Intercept summary delivery to wrong patient due to missing recipient identity binding"]

    I2_root --> I2_or1
    I2_or1 --> I2_leaf1
    I2_or1 --> I2_leaf2
    I2_or1 --> I2_leaf3

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class I2_root goal
    class I2_or1 orGate
    class I2_leaf1,I2_leaf2,I2_leaf3 leaf
```
