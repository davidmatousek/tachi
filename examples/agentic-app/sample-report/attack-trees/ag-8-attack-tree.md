# Attack Tree: AG-8 — Inter-Agent Communication Channel

**Risk Level**: Critical
**Component**: Inter-Agent Communication Channel
**Threat**: Insecure inter-agent communication enables agent-in-the-middle attacks (OWASP ASI07:2026)

```mermaid
graph TD
    Goal["[GOAL] Achieve agent-in-the-middle takeover via insecure inter-agent channel (ASI07:2026)"]
    Goal --> A["[OR] Intercept and replay delegation messages"]
    A --> A1["No nonce-based replay prevention on channel messages"]
    A --> A2["No timestamp-bound replay window enforcement"]
    A --> A3["No HMAC or asymmetric envelope signature on messages"]
    Goal --> B["[OR] Inject forged messages impersonating Orchestrator"]
    B --> B1["No mutual TLS on inter-agent channel endpoints"]
    B --> B2["No per-message sender authentication verified at receiver"]
    Goal --> C["[OR] Exploit taint propagation gap on Orchestrator relay to ClinAdvisor"]
    C --> C1["Orchestrator relay outputs do not carry upstream sender authority labels"]
    C --> C2["ClinAdvisor cannot detect tampering via relay without authority labels"]
    Goal --> D["[AND] Unauthorized instructions delivered to Specialist or ClinAdvisor"]
    D --> D1["Task redirection via forged delegation message"]
    D --> D2["Clinical query injection via forged JSON-RPC relay"]
    classDef critical fill:#d32f2f,color:#fff
    class Goal critical
```
