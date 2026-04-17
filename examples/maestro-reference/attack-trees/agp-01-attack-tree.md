# Attack Tree: AGP-01 — Multi-Agent Coordination Enabling Coordinated Malicious Action

**Component**: Inter-Agent Communication Channel | **Risk Level**: Critical | **Finding**: AGP-01

Multi-agent coordination over the Inter-Agent Communication Channel creates potential for coordinated malicious action across specialist agents, where compromised agents can jointly execute operations that individually fall below per-agent detection thresholds.

```mermaid
flowchart TD
    AGP01_root["Execute coordinated malicious action across specialist agents via inter-agent channel exploitation"]
    AGP01_or1{{"OR"}}
    AGP01_sub1["Coordinate compromised agents to jointly exfiltrate PHI across shared channel"]
    AGP01_sub2["Split prohibited FHIR operation across multiple agents to stay below per-agent rate limits"]
    AGP01_and1{{"AND"}}
    AGP01_and2{{"AND"}}
    AGP01_leaf1["Compromise two or more specialist agents via independent attack vectors"]
    AGP01_leaf2["Establish covert coordination channel within legitimate inter-agent message flow"]
    AGP01_leaf3["Issue coordinated PHI exfiltration requests split to evade per-agent detection thresholds"]
    AGP01_leaf4["Identify FHIR operation sequence blocked at per-agent quota individually"]
    AGP01_leaf5["Distribute operation sub-tasks across Diagnostic Agent and Treatment Planner Agent"]
    AGP01_leaf6["Aggregate results via legitimate channel to complete prohibited operation collectively"]

    AGP01_root --> AGP01_or1
    AGP01_or1 --> AGP01_sub1
    AGP01_or1 --> AGP01_sub2
    AGP01_sub1 --> AGP01_and1
    AGP01_and1 --> AGP01_leaf1
    AGP01_and1 --> AGP01_leaf2
    AGP01_and1 --> AGP01_leaf3
    AGP01_sub2 --> AGP01_and2
    AGP01_and2 --> AGP01_leaf4
    AGP01_and2 --> AGP01_leaf5
    AGP01_and2 --> AGP01_leaf6

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef andGate fill:#ffa500,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef subGoal fill:#d5dbdb,stroke:#333,stroke-width:2px,color:#333
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class AGP01_root goal
    class AGP01_and1,AGP01_and2 andGate
    class AGP01_or1 orGate
    class AGP01_sub1,AGP01_sub2 subGoal
    class AGP01_leaf1,AGP01_leaf2,AGP01_leaf3,AGP01_leaf4,AGP01_leaf5,AGP01_leaf6 leaf
```
