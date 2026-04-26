# Attack Tree: OI-3 — SSRF via LLM-Synthesized URL in Tool Call Request to MCP Tool Server

**Finding ID**: OI-3
**Risk Level**: High
**Component**: LLM Agent Orchestrator
**Delta Status**: UNCHANGED

```mermaid
flowchart TD
    OI3_root["Cause MCP Tool Server to fetch internal cloud-metadata or RFC 1918 URLs via SSRF in Tool Call Request"]
    OI3_and1{{"AND"}}
    OI3_sub1["Prime Orchestrator to emit internal or private-range URL in Tool Call Request parameter"]
    OI3_sub2["Exploit Tool Server fetching URL without allowlist or egress firewall protection"]
    OI3_or1{{"OR"}}
    OI3_leaf1["Craft user prompt instructing Orchestrator to include metadata endpoint URL in tool parameter"]
    OI3_leaf2["Poison KB document causing Orchestrator to retrieve and emit internal URL in tool invocation"]
    OI3_and2{{"AND"}}
    OI3_leaf3["Confirm MCP Tool Server performs no URL allowlist check on outbound HTTP fetch targets"]
    OI3_leaf4["Confirm no egress firewall rule blocks RFC 1918 or cloud-metadata address ranges"]
    OI3_leaf5["Tool Server fetches internal resource with its IAM role exposing credentials or metadata"]

    OI3_root --> OI3_and1
    OI3_and1 --> OI3_sub1
    OI3_and1 --> OI3_sub2
    OI3_sub1 --> OI3_or1
    OI3_or1 --> OI3_leaf1
    OI3_or1 --> OI3_leaf2
    OI3_sub2 --> OI3_and2
    OI3_and2 --> OI3_leaf3
    OI3_and2 --> OI3_leaf4
    OI3_and2 --> OI3_leaf5

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef andGate fill:#ffa500,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef subGoal fill:#d5dbdb,stroke:#333,stroke-width:2px,color:#333
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class OI3_root goal
    class OI3_and1,OI3_and2 andGate
    class OI3_or1 orGate
    class OI3_sub1,OI3_sub2 subGoal
    class OI3_leaf1,OI3_leaf2,OI3_leaf3,OI3_leaf4,OI3_leaf5 leaf
```
