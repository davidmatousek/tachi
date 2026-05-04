# Attack Tree: I-2 — Internal Context Leakage via Orchestrator Responses

**Finding**: I-2 | **Component**: LLM Agent Orchestrator | **Risk Level**: Critical
**Correlation**: Part of CG-3. See also: LLM-1.

```mermaid
flowchart TD
    I2_root["Extract sensitive internal context\nfrom Orchestrator responses"]
    I2_or1{{"OR"}}
    I2_sub1["Trigger system prompt\nleakage in response"]
    I2_sub2["Extract tool descriptions\nand API endpoints"]
    I2_sub3["Obtain Knowledge Base\nmetadata and schema"]
    I2_leaf1["Submit meta-instruction\nquery prompts"]
    I2_leaf2["Use role-play injection\nto bypass safety constraints"]
    I2_leaf3["Request tool listing\nvia crafted prompt"]
    I2_leaf4["Query for internal URL\npatterns in responses"]
    I2_leaf5["Craft retrieval queries\ntargeting schema metadata"]
    I2_root --> I2_or1
    I2_or1 --> I2_sub1
    I2_or1 --> I2_sub2
    I2_or1 --> I2_sub3
    I2_sub1 --> I2_leaf1
    I2_sub1 --> I2_leaf2
    I2_sub2 --> I2_leaf3
    I2_sub2 --> I2_leaf4
    I2_sub3 --> I2_leaf5
    classDef goal fill:#DC2626,stroke:#991B1B,color:#FFFFFF
    classDef orGate fill:#0D9488,stroke:#0F766E,color:#FFFFFF
    classDef leaf fill:#16A34A,stroke:#15803D,color:#FFFFFF
    classDef sub fill:#CA8A04,stroke:#A16207,color:#FFFFFF
    class I2_root goal
    class I2_or1 orGate
    class I2_sub1,I2_sub2,I2_sub3 sub
    class I2_leaf1,I2_leaf2,I2_leaf3,I2_leaf4,I2_leaf5 leaf
```
