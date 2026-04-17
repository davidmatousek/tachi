# Attack Tree: D-5 — Diagnostic Agent Resource Exhaustion via Tool Call Flood

**Component**: Diagnostic Agent | **Risk Level**: High | **Finding**: D-5

An attacker targets the Diagnostic Agent with resource-exhausting tool call floods or retrieval storms against the Clinical Guideline RAG Corpus, disrupting diagnostic capabilities for legitimate clinical queries.

```mermaid
flowchart TD
    D5_root["Disrupt Diagnostic Agent availability via tool call flood or guideline retrieval storm"]
    D5_or1{{"OR"}}
    D5_leaf1["Launch tool call flood targeting Diagnostic Agent without per-session rate limits"]
    D5_leaf2["Issue high-volume guideline retrieval requests exhausting RAG corpus query capacity"]
    D5_leaf3["Sustain resource exhaustion until Diagnostic Agent drops legitimate clinical query processing"]

    D5_root --> D5_or1
    D5_or1 --> D5_leaf1
    D5_or1 --> D5_leaf2
    D5_or1 --> D5_leaf3

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class D5_root goal
    class D5_or1 orGate
    class D5_leaf1,D5_leaf2,D5_leaf3 leaf
```
