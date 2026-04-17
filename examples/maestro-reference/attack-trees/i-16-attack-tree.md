# Attack Tree: I-16 — Outcomes Telemetry Store Clinical Pattern Disclosure

**Component**: Outcomes Telemetry and Physician Override Audit Store | **Risk Level**: High | **Finding**: I-16

Physician override telemetry may contain implicit patient data. Unauthorized access to the Outcomes Telemetry store could disclose sensitive clinical patterns or enable re-identification of de-identified training data.

```mermaid
flowchart TD
    I16_root["Disclose sensitive clinical patterns or re-identify patients via Outcomes Telemetry store access"]
    I16_or1{{"OR"}}
    I16_leaf1["Obtain unauthorized read access to Outcomes Telemetry store"]
    I16_leaf2["Extract physician override patterns correlated with specific patient presentation types"]
    I16_leaf3["Use telemetry signals to re-identify de-identified patients in model training data"]

    I16_root --> I16_or1
    I16_or1 --> I16_leaf1
    I16_or1 --> I16_leaf2
    I16_or1 --> I16_leaf3

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class I16_root goal
    class I16_or1 orGate
    class I16_leaf1,I16_leaf2,I16_leaf3 leaf
```
