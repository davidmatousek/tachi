# Attack Tree: LLM-1 — Clinical LLM Prompt Injection via API Gateway

**Component**: Clinical LLM | **Risk Level**: Critical | **Finding**: LLM-1

An attacker injects adversarial prompts into the clinical context window passed to the Clinical LLM via the API Gateway, causing the model to generate harmful, false, or clinically dangerous completions incorporated into clinical recommendations.

```mermaid
flowchart TD
    LLM1_root["Cause Clinical LLM to generate clinically dangerous completions via prompt injection"]
    LLM1_or1{{"OR"}}
    LLM1_sub1["Inject adversarial instructions via clinical query through Physician Clinical Portal"]
    LLM1_sub2["Inject system-level instructions via compromised upstream agent context window"]
    LLM1_and1{{"AND"}}
    LLM1_and2{{"AND"}}
    LLM1_leaf1["Craft clinical query containing prompt injection payload embedded in clinical text"]
    LLM1_leaf2["Bypass input sanitization at API Gateway before forwarding to Clinical LLM"]
    LLM1_leaf3["Cause Clinical LLM to emit adversarial completion following injected instructions"]
    LLM1_leaf4["Compromise Supervisor Orchestrator or Diagnostic Agent context assembly"]
    LLM1_leaf5["Insert adversarial system-level instruction into assembled context before API Gateway"]
    LLM1_leaf6["Cause completion to contain embedded instructions or falsified clinical outputs"]

    LLM1_root --> LLM1_or1
    LLM1_or1 --> LLM1_sub1
    LLM1_or1 --> LLM1_sub2
    LLM1_sub1 --> LLM1_and1
    LLM1_and1 --> LLM1_leaf1
    LLM1_and1 --> LLM1_leaf2
    LLM1_and1 --> LLM1_leaf3
    LLM1_sub2 --> LLM1_and2
    LLM1_and2 --> LLM1_leaf4
    LLM1_and2 --> LLM1_leaf5
    LLM1_and2 --> LLM1_leaf6

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef andGate fill:#ffa500,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef subGoal fill:#d5dbdb,stroke:#333,stroke-width:2px,color:#333
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class LLM1_root goal
    class LLM1_and1,LLM1_and2 andGate
    class LLM1_or1 orGate
    class LLM1_sub1,LLM1_sub2 subGoal
    class LLM1_leaf1,LLM1_leaf2,LLM1_leaf3,LLM1_leaf4,LLM1_leaf5,LLM1_leaf6 leaf
```
