# Attack Tree: OI-4 — Server-Side Execution via Clinical Summary Content Injected into Orchestrator Tool Call

**Finding ID**: OI-4
**Risk Level**: High
**Component**: Clinical Advisory Sub-Agent
**Delta Status**: UNCHANGED

```mermaid
flowchart TD
    OI4_root["Achieve server-side execution at MCP Tool Server via adversarial clinical summary content injected into Tool Call Request"]
    OI4_and1{{"AND"}}
    OI4_sub1["Cause ClinAdvisor to return clinical summary containing injection payload"]
    OI4_sub2["Exploit Orchestrator incorporating clinical output into Tool Call Request without sanitization"]
    OI4_or1{{"OR"}}
    OI4_leaf1["Inject adversarial instruction via clinical query causing ClinAdvisor to emit injection payload"]
    OI4_leaf2["Poison KB document causing ClinAdvisor to retrieve and include injection payload in summary"]
    OI4_and2{{"AND"}}
    OI4_leaf3["Confirm Orchestrator interpolates ClinAdvisor output directly into JSON-RPC tool parameters"]
    OI4_leaf4["Confirm MCP Tool Server does not apply schema validation on parameters from Orchestrator"]
    OI4_leaf5["Injection executes at Tool Server backend with service account privileges via tool call sink"]

    OI4_root --> OI4_and1
    OI4_and1 --> OI4_sub1
    OI4_and1 --> OI4_sub2
    OI4_sub1 --> OI4_or1
    OI4_or1 --> OI4_leaf1
    OI4_or1 --> OI4_leaf2
    OI4_sub2 --> OI4_and2
    OI4_and2 --> OI4_leaf3
    OI4_and2 --> OI4_leaf4
    OI4_and2 --> OI4_leaf5

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef andGate fill:#ffa500,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef subGoal fill:#d5dbdb,stroke:#333,stroke-width:2px,color:#333
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class OI4_root goal
    class OI4_and1,OI4_and2 andGate
    class OI4_or1 orGate
    class OI4_sub1,OI4_sub2 subGoal
    class OI4_leaf1,OI4_leaf2,OI4_leaf3,OI4_leaf4,OI4_leaf5 leaf
```
