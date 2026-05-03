# Attack Tree: AG-2 — Supervisor Orchestrator Delegation Authority Abuse

**Component**: Supervisor Orchestrator | **Risk Level**: Critical | **Finding**: AG-2

A compromised Supervisor Orchestrator abuses its privileged delegation authority to issue unauthorized tool calls or FHIR operations through specialist agents, circumventing per-agent access controls.

```mermaid
flowchart TD
    AG2_root["Circumvent per-agent access controls by abusing Supervisor Orchestrator delegation authority"]
    AG2_or1{{"OR"}}
    AG2_sub1["Delegate to specialist agent with broader permissions to perform unauthorized operation"]
    AG2_sub2["Issue unauthorized tool call allowlist bypass through compromised orchestrator"]
    AG2_and1{{"AND"}}
    AG2_and2{{"AND"}}
    AG2_leaf1["Compromise Supervisor Orchestrator service account or process"]
    AG2_leaf2["Identify specialist agent with broader FHIR permissions than the current query scope"]
    AG2_leaf3["Issue delegation command routing unauthorized operation through permissive specialist"]
    AG2_leaf4["Identify tool call pair blocked for one agent but permitted for another"]
    AG2_leaf5["Craft delegation chain routing restricted tool call through permissive specialist path"]
    AG2_leaf6["Verify absence of cross-agent audit trail linking delegation to originating command"]

    AG2_root --> AG2_or1
    AG2_or1 --> AG2_sub1
    AG2_or1 --> AG2_sub2
    AG2_sub1 --> AG2_and1
    AG2_and1 --> AG2_leaf1
    AG2_and1 --> AG2_leaf2
    AG2_and1 --> AG2_leaf3
    AG2_sub2 --> AG2_and2
    AG2_and2 --> AG2_leaf4
    AG2_and2 --> AG2_leaf5
    AG2_and2 --> AG2_leaf6

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef andGate fill:#ffa500,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef subGoal fill:#d5dbdb,stroke:#333,stroke-width:2px,color:#333
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class AG2_root goal
    class AG2_and1,AG2_and2 andGate
    class AG2_or1 orGate
    class AG2_sub1,AG2_sub2 subGoal
    class AG2_leaf1,AG2_leaf2,AG2_leaf3,AG2_leaf4,AG2_leaf5,AG2_leaf6 leaf
```
