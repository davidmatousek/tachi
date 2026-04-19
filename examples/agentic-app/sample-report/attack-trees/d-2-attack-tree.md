---
finding_id: "D-2"
risk_level: "Critical"
component: "LLM Agent Orchestrator"
generated: "2026-04-19"
---

# Attack Tree: D-2 — LLM Agent Orchestrator Inference Pipeline Exhaustion

```mermaid
graph TD
    GOAL["GOAL: Exhaust Orchestrator inference capacity\nstarving legitimate user requests"]
    GOAL --> A["OR"]
    A --> B["High-token-count prompt flooding"]
    A --> C["Recursive tool invocation chain injection"]
    B --> B1["Attacker submits max-length context prompts\n[High / High]"]
    B --> B2["Adversarial context injection expanding\ntoken usage recursively\n[High / High]"]
    C --> C1["Prompt injection causing Orchestrator\nto invoke tools in recursive chains\n[High / High]"]
    C --> C2["Adversarial tool results triggering\nfurther tool invocations\n[Med / High]"]
    B1 --> D["AND"]
    B2 --> D
    C1 --> D
    C2 --> D
    D --> E["No per-session token budget enforced"]
    D --> F["No circuit breaker on tool invocation depth"]
    E --> G["Orchestrator capacity exhausted —\nlegitimate requests queued or rejected"]
    F --> G
```

**Chain-breaking control**: Implement per-session token budgets and hard context-window limits. Apply circuit breakers on tool invocation chains (maximum recursive depth per session). Use request queuing with priority tiers and capacity-based load shedding.
