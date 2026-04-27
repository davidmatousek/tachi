# Attack Tree: S-9 — Clinical Advisory Sub-Agent

**Risk Level**: Critical
**Component**: Clinical Advisory Sub-Agent
**Threat**: Rogue process injects crafted clinical queries impersonating Orchestrator

```mermaid
graph TD
    Goal["[GOAL] Cause ClinAdvisor to process unauthorized requests and return manipulated clinical summaries"]
    Goal --> A["[OR] Gain Application Zone access"]
    A --> A1["Compromise any service in Application Zone"]
    A --> A2["Exploit Orchestrator compromise (prompt injection)"]
    Goal --> B["[OR] Send JSON-RPC clinical query without sender attestation"]
    B --> B1["No signed caller token required on ClinAdvisor JSON-RPC endpoint"]
    B --> B2["No mTLS between Orchestrator and ClinAdvisor"]
    B --> B3["No nonce/replay prevention on clinical query messages"]
    Goal --> C["[AND] Manipulated clinical summary enters Orchestrator response path"]
    C --> C1["Orchestrator incorporates ClinAdvisor output without re-validation"]
    classDef critical fill:#d32f2f,color:#fff
    class Goal critical
```
