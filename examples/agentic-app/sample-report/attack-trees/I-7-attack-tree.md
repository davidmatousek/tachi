---
finding_id: "I-7"
risk_level: "Critical"
component: "Audit Logger"
generated: "2026-04-19"
---

# Attack Tree: I-7 — Audit Logger Unauthorized Read Access

```mermaid
graph TD
    GOAL["GOAL: Unauthorized party reads full\nAudit Logger operational history"]
    GOAL --> A["OR"]
    A --> B["Misconfigured read access controls"]
    A --> C["Insider threat with log read access"]
    A --> D["Exploit service with log read capability"]
    B --> B1["Overly permissive IAM role on log store\n[Med / High]"]
    B --> B2["Default credentials on log infrastructure\n[Low / High]"]
    C --> C1["Privileged user abuses read access\n[Low / High]"]
    D --> D1["Compromise application service\nwith log read role\n[Med / High]"]
    B1 --> E["Read access to full Audit Logger\noperational history"]
    B2 --> E
    C1 --> E
    D1 --> E
    E --> F["Exposed data:\n- User prompts\n- Model decisions\n- Tool call parameters\n- Filtering rule triggers\n- Session identities"]
```

**Chain-breaking control**: Enforce strict read access controls on the Audit Logger: only designated incident-response and analytics service accounts should have read access. Encrypt log entries at rest with envelope encryption (per-batch keys in hardware-secured KMS). Audit all read access.
