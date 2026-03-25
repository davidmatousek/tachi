# Attack Tree: E-2 — Tool Permission Escalation via Model Manipulation

**Finding**: E-2 | **Component**: LLM Agent Orchestrator | **Risk Level**: Critical
**Correlation**: Part of CG-2. See also: AG-1.

```mermaid
flowchart TD
    E2_root["Escalate to elevated tool permissions\nvia model manipulation"]
    E2_or1{{"OR"}}
    E2_sub1["Manipulate model reasoning\nto request admin tools"]
    E2_sub2["Exploit missing permission\nboundary validation"]
    E2_leaf1["Inject prompt requesting\nelevated tool access"]
    E2_leaf2["Use indirect injection\nvia poisoned KB documents"]
    E2_leaf3["Call admin tool endpoint\ndirectly without role check"]
    E2_leaf4["Manipulate tool parameters\nto access restricted resources"]
    E2_root --> E2_or1
    E2_or1 --> E2_sub1
    E2_or1 --> E2_sub2
    E2_sub1 --> E2_leaf1
    E2_sub1 --> E2_leaf2
    E2_sub2 --> E2_leaf3
    E2_sub2 --> E2_leaf4
    classDef goal fill:#DC2626,stroke:#991B1B,color:#FFFFFF
    classDef orGate fill:#0D9488,stroke:#0F766E,color:#FFFFFF
    classDef leaf fill:#16A34A,stroke:#15803D,color:#FFFFFF
    classDef sub fill:#CA8A04,stroke:#A16207,color:#FFFFFF
    class E2_root goal
    class E2_or1 orGate
    class E2_sub1,E2_sub2 sub
    class E2_leaf1,E2_leaf2,E2_leaf3,E2_leaf4 leaf
```
