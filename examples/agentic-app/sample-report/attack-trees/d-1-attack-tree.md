---
finding_id: "D-1"
risk_level: "Critical"
component: "Guardrails Service"
generated: "2026-04-19"
---

# Attack Tree: D-1 — Guardrails Service Resource Exhaustion

```mermaid
graph TD
    GOAL["GOAL: Exhaust Guardrails Service resources\nto collapse the filtering pipeline"]
    GOAL --> A["AND"]
    A --> B["No per-IP/session rate limiting before Guardrails"]
    A --> C["No computational complexity budget per prompt"]
    B --> B1["Attacker submits high-volume prompt requests\n[High / High]"]
    C --> C1["Adversarially crafted prompts maximize\nregex evaluation cost\n[High / High]"]
    B1 --> D["High-rate complex prompt storm\nreaches Guardrails Service"]
    C1 --> D
    D --> E["OR"]
    E --> E1["Guardrails Service CPU exhaustion\nand crash"]
    E --> E2["Guardrails Service response latency\nexceeds SLA — timeout cascade"]
    E1 --> F["Guardrails unavailable — pipeline blocked\nor prompts bypass filtering"]
    E2 --> F
```

**Chain-breaking control**: Implement per-IP and per-session rate limiting at the network ingress (before the Guardrails Service). Apply a computational complexity budget per prompt evaluation; reject prompts that exceed the budget. Use asynchronous processing queues with backpressure.
