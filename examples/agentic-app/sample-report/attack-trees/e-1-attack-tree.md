---
finding_id: "E-1"
risk_level: "Critical"
component: "Guardrails Service"
generated: "2026-04-19"
---

# Attack Tree: E-1 — Guardrails Service Prompt Injection Bypass Privilege Escalation

```mermaid
graph TD
    GOAL["GOAL: Attacker's prompt reaches Orchestrator\nwith trusted-caller privilege level"]
    GOAL --> A["AND"]
    A --> B["Crafted prompt evades Guardrails detection"]
    A --> C["Orchestrator treats Guardrails-passed\nInput as implicitly trusted"]
    B --> B1["Adversarial jailbreak technique bypasses\ncontent filtering rules\n[High / High]"]
    B --> B2["Obfuscation: encoding, Unicode tricks,\ntoken fragmentation\n[High / High]"]
    C --> C1["Orchestrator has no independent\ninput validation layer\n[High / High]"]
    B1 --> D["Attacker prompt transits Guardrails\nwithout triggering rejection"]
    B2 --> D
    C1 --> D
    D --> E["Orchestrator acts on attacker prompt\nas if from a trusted user"]
    E --> F["Privilege escalation from\nunauthenticated user → trusted caller"]
    F --> G["Enables subsequent:\n- KB corpus exfiltration\n- Cross-scope tool invocations\n- Unauthorized delegation messages"]
```

**Chain-breaking control**: Layer defense-in-depth: the Orchestrator MUST apply its own input validation independently of Guardrails. Do not treat Guardrails-passed inputs as implicitly trusted. Implement Orchestrator-level prompt injection detection as a separate control.
