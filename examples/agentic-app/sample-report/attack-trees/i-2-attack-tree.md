---
finding_id: "I-2"
risk_level: "Critical"
component: "LLM Agent Orchestrator"
generated: "2026-04-19"
---

# Attack Tree: I-2 — LLM Agent Orchestrator Context Window Leakage

```mermaid
graph TD
    GOAL["GOAL: Orchestrator leaks sensitive context\nwindow data in HTTPS response to User"]
    GOAL --> A["OR"]
    A --> B["Prompt injection causing context leakage"]
    A --> C["Model hallucination producing\nsystem data in output"]
    B --> B1["Direct prompt injection via User input\n[High / High]"]
    B --> B2["Indirect injection via adversarial KB document\n[High / High]"]
    C --> C1["Model reproduces system prompt\npreamble in response\n[Med / High]"]
    C --> C2["Model includes KB document identifiers\nor tool metadata in response\n[Med / High]"]
    B1 --> D["AND"]
    B2 --> D
    C1 --> D
    C2 --> D
    D --> E["No output scrubbing before\nHTTPS response transmission"]
    E --> F["Sensitive data sent to User:\n- System prompt contents\n- KB document identifiers\n- Tool response metadata\n- Internal configuration"]
```

**Chain-breaking control**: Implement output scrubbing on the Orchestrator's response before transmission to the User: detect and redact content pattern-matching against known sensitive-data markers. Apply a separate "response auditor" step that reviews the output before sending.
