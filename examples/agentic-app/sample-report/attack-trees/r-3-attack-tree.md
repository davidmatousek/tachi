---
finding_id: "R-3"
risk_level: "Critical"
component: "LLM Agent Orchestrator"
generated: "2026-04-19"
---

# Attack Tree: R-3 — LLM Agent Orchestrator Action Repudiation

```mermaid
graph TD
    GOAL["GOAL: Orchestrator denies having issued\nspecific delegation or tool call actions"]
    GOAL --> A["AND"]
    A --> B["No per-action logging with content hashes"]
    A --> C["No service key signatures on log entries"]
    B --> B1["Delegation messages not logged\nbefore execution\n[High / High]"]
    B --> B2["Tool call requests not logged\nwith content hash\n[High / High]"]
    C --> C1["Log entries unsigned — not\nattributable to Orchestrator\n[High / High]"]
    B1 --> D["Orchestrator executes undisclosed action"]
    B2 --> D
    C1 --> D
    D --> E["Incident response cannot prove\nOrchestrator issued specific action"]
    E --> F["Attacker or Orchestrator operator\ndenies unauthorized action occurred"]
```

**Chain-breaking control**: Log every Orchestrator action with action type, content hash, session/request ID, monotonic sequence number, and service key signature. Actions MUST be logged before execution, not after.
