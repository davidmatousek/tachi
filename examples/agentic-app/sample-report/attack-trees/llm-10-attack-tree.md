# Attack Tree: LLM-10 — Server-Side Injection via Tool Result Incorporation into Subsequent Tool Calls

**Finding ID**: LLM-10
**Risk Level**: High
**Component**: Specialist Agent
**Delta Status**: UNCHANGED

```mermaid
flowchart TD
    LLM10_root["Achieve server-side injection at Tool Server via malicious tool results incorporated into Specialist subsequent tool calls"]
    LLM10_and1{{"AND"}}
    LLM10_sub1["Cause MCP Tool Server to return tool result containing injection payload"]
    LLM10_sub2["Specialist incorporates result into next tool call parameters without sanitization"]
    LLM10_or1{{"OR"}}
    LLM10_leaf1["Influence External API to return adversarial content in tool result via BGP or DNS attack"]
    LLM10_leaf2["Compromise External API provider to return injection payload in API response"]
    LLM10_and2{{"AND"}}
    LLM10_leaf3["Confirm Specialist does not sanitize tool results before using them in subsequent tool invocations"]
    LLM10_leaf4["Confirm Tool Server does not apply allowlist validation on parameters regardless of source"]
    LLM10_leaf5["Injection payload from tool result executes at Tool Server or External API via second-order injection"]

    LLM10_root --> LLM10_and1
    LLM10_and1 --> LLM10_sub1
    LLM10_and1 --> LLM10_sub2
    LLM10_sub1 --> LLM10_or1
    LLM10_or1 --> LLM10_leaf1
    LLM10_or1 --> LLM10_leaf2
    LLM10_sub2 --> LLM10_and2
    LLM10_and2 --> LLM10_leaf3
    LLM10_and2 --> LLM10_leaf4
    LLM10_and2 --> LLM10_leaf5

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef andGate fill:#ffa500,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef subGoal fill:#d5dbdb,stroke:#333,stroke-width:2px,color:#333
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class LLM10_root goal
    class LLM10_and1,LLM10_and2 andGate
    class LLM10_or1 orGate
    class LLM10_sub1,LLM10_sub2 subGoal
    class LLM10_leaf1,LLM10_leaf2,LLM10_leaf3,LLM10_leaf4,LLM10_leaf5 leaf
```
