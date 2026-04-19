---
finding_id: "AG-3"
risk_level: "Critical"
component: "Specialist Agent"
generated: "2026-04-19"
---

# Attack Tree: AG-3 — Specialist Agent Cumulative Prohibited Tool Call Sequence

```mermaid
graph TD
    GOAL["GOAL: Specialist executes cumulative prohibited\ntool call sequence via adversarial delegation"]
    GOAL --> A["AND"]
    A --> B["Adversarially crafted delegation message\nreaches Specialist"]
    A --> C["No task-level intent verification\nor tool call budget"]
    B --> B1["Tampered delegation message\nvia Channel interception\n[High / High]"]
    B --> B2["Compromised Orchestrator issues\nmalicious delegation\n[High / High]"]
    C --> C1["Specialist does not verify each\ntool call against task objective\n[High / High]"]
    C --> C2["No maximum tool calls\nper task enforcement\n[High / High]"]
    B1 --> D["Specialist receives adversarial task\ndirecting multi-tool sequence"]
    B2 --> D
    C1 --> D
    C2 --> D
    D --> E["Each individual tool call appears permitted"]
    E --> F["Cumulative sequence achieves\nprohibited compound action:\n- Data exfiltration via chained reads\n- Permission escalation across tool chain\n- External API abuse via coordinated calls"]
```

**Chain-breaking control**: Implement task-level intent verification: the Specialist MUST check that each tool invocation in a task sequence is consistent with the task's stated objective. Apply a budget on tool calls per task (maximum N calls); require re-authorization from the Orchestrator for task extensions.
