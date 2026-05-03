# Attack Tree: T-2 — Patient Summary Tampering

**Component**: Patient Summary Generator | **Risk Level**: High | **Finding**: T-2

An attacker with access to the summary generation pipeline tampers with patient-facing summaries, injecting dangerous or false clinical guidance into patient communications.

```mermaid
flowchart TD
    T2_root["Inject dangerous clinical guidance into patient communications via summary tampering"]
    T2_or1{{"OR"}}
    T2_leaf1["Gain access to summary generation pipeline and modify summary content before delivery"]
    T2_leaf2["Intercept summary in transit between generator and patient endpoint"]
    T2_leaf3["Modify summary payload to include false clinical instructions or contraindicated guidance"]

    T2_root --> T2_or1
    T2_or1 --> T2_leaf1
    T2_or1 --> T2_leaf2
    T2_or1 --> T2_leaf3

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class T2_root goal
    class T2_or1 orGate
    class T2_leaf1,T2_leaf2,T2_leaf3 leaf
```
