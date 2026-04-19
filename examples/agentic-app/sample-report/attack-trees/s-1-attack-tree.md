---
finding_id: "S-1"
risk_level: "Critical"
component: "User"
generated: "2026-04-19"
---

# Attack Tree: S-1 — User Identity Spoofing

```mermaid
graph TD
    GOAL["GOAL: Attacker impersonates legitimate user\nat User→Guardrails boundary"]
    GOAL --> A["OR"]
    A --> B["Replay stolen session token"]
    A --> C["Forge identity credentials"]
    B --> B1["Steal session token via XSS\n[High / High]"]
    B --> B2["Intercept token in transit\n[Med / High]"]
    B --> B3["Extract token from client storage\n[Med / High]"]
    C --> C1["Obtain victim credentials via phishing\n[High / High]"]
    C --> C2["Credential stuffing from breach data\n[Med / High]"]
    B1 --> X["Bypass authentication at\nUser→Guardrails boundary"]
    B2 --> X
    B3 --> X
    C1 --> X
    C2 --> X
    X --> Y["Access system under victim identity"]
```

**Chain-breaking control**: Implement short-lived JWT tokens with binding to client IP/device fingerprint. Enforce MFA for all user sessions. Use token revocation lists and refresh-token rotation with binding checks.
