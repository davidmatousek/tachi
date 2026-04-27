# Attack Tree: OI-3 — LLM Agent Orchestrator

**Risk Level**: High
**Component**: LLM Agent Orchestrator
**Threat**: SSRF via LLM-synthesized URL in Tool Call Request to MCP Tool Server (OWASP LLM05:2025)

```mermaid
graph TD
    Goal["[GOAL] Access internal network resources via SSRF in LLM-synthesized Tool Call URL (OWASP LLM05:2025)"]
    Goal --> A["[OR] Cause Orchestrator to emit internal URL as tool parameter"]
    A --> A1["Prompt injection instructs Orchestrator to fetch specific internal URL"]
    A --> A2["RAG poisoning embeds internal URL in retrieved context driving tool call"]
    Goal --> B["[AND] Tool Server fetches URL without allowlist check"]
    B --> B1["No URL allowlisting on MCP Tool Server outbound HTTP calls"]
    B --> B2["No egress firewall blocking 10.x/172.x/192.168.x/169.254.x ranges"]
    B --> B3["No DNS pinning resolving to private IP detection"]
    Goal --> C["[AND] Internal resource accessed with Tool Server IAM role"]
    C --> C1["Cloud metadata 169.254.169.254 returns IAM credentials"]
    C --> C2["Internal admin API accessed via Tool Server network role"]
    classDef high fill:#e65100,color:#fff
    class Goal high
```
