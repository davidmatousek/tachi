# Attack Tree: S-6 — Application Zone Process Spoofs Agent to Submit Unauthorized Tool Calls

**Finding ID**: S-6
**Risk Level**: Critical
**Component**: MCP Tool Server
**Delta Status**: UNCHANGED

```mermaid
flowchart TD
    S6_root["Invoke unauthorized tools using MCP Tool Server credentials by spoofing agent identity"]
    S6_and1{{"AND"}}
    S6_sub1["Gain Application Zone process access with JSON-RPC endpoint reach"]
    S6_sub2["Submit tool call request with forged agent identity"]
    S6_or1{{"OR"}}
    S6_leaf1["Compromise Specialist Agent or lateral-move to its network segment"]
    S6_leaf2["Exploit misconfigured internal network allowing direct JSON-RPC access"]
    S6_and2{{"AND"}}
    S6_leaf3["Confirm Tool Server accepts unauthenticated or weakly authenticated callers"]
    S6_leaf4["Craft JSON-RPC request impersonating Orchestrator or Specialist identity"]
    S6_leaf5["Execute tool with Tool Server service credentials and external API access"]

    S6_root --> S6_and1
    S6_and1 --> S6_sub1
    S6_and1 --> S6_sub2
    S6_sub1 --> S6_or1
    S6_or1 --> S6_leaf1
    S6_or1 --> S6_leaf2
    S6_sub2 --> S6_and2
    S6_and2 --> S6_leaf3
    S6_and2 --> S6_leaf4
    S6_and2 --> S6_leaf5

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef andGate fill:#ffa500,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef subGoal fill:#d5dbdb,stroke:#333,stroke-width:2px,color:#333
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class S6_root goal
    class S6_and1,S6_and2 andGate
    class S6_or1 orGate
    class S6_sub1,S6_sub2 subGoal
    class S6_leaf1,S6_leaf2,S6_leaf3,S6_leaf4,S6_leaf5 leaf
```
