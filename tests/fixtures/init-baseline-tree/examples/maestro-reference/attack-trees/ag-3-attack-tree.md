# Attack Tree: AG-3 — Diagnostic Agent Unauthorized FHIR Write Autonomy

**Component**: Diagnostic Agent | **Risk Level**: High | **Finding**: AG-3

The Diagnostic Agent autonomously executes FHIR write operations via the Clinical MCP Tool Server beyond its authorized clinical scope, persisting adversarial or erroneous diagnostic data to patient records without physician authorization.

```mermaid
flowchart TD
    AG3_root["Persist unauthorized clinical data to patient FHIR records via Diagnostic Agent autonomous FHIR write"]
    AG3_or1{{"OR"}}
    AG3_leaf1["Compromise or manipulate Diagnostic Agent to trigger unauthorized FHIR write without physician approval gate"]
    AG3_leaf2["Exploit absent write-access restrictions to issue FHIR write for resource types beyond authorized scope"]
    AG3_leaf3["Persist erroneous diagnostic output directly to patient record via autonomous agent action"]

    AG3_root --> AG3_or1
    AG3_or1 --> AG3_leaf1
    AG3_or1 --> AG3_leaf2
    AG3_or1 --> AG3_leaf3

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class AG3_root goal
    class AG3_or1 orGate
    class AG3_leaf1,AG3_leaf2,AG3_leaf3 leaf
```
