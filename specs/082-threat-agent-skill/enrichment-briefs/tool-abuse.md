# Enrichment Brief — tool-abuse

**Agent type**: AI
**Primary threat category**: Tool Abuse (Agent Tool Invocation Misuse)
**Created**: 2026-04-11
**Feature**: 082 — Threat Agent Skill References

> **HIGH-PRIORITY ENRICHMENT TARGET** — MITRE ATLAS v5.1+ (Oct 2025 catalog update) added five agent-specific techniques (**AML.T0058, AML.T0059, AML.T0060, AML.T0061, AML.T0062**) specifically for agentic tool-abuse. This agent should receive the largest enrichment among the 11 per research.md §3.2.

## Candidate New Pattern Categories

### Category 1 — LLM Plugin Compromise (AML.T0058)

- **Source**: MITRE ATLAS v5.1+ (Oct 2025 catalog update)
- **Source citation**: `https://atlas.mitre.org/techniques/AML.T0058`
- **Source item**: AML.T0058 LLM Plugin Compromise
- **Why this category**: Plugin-based agents (ChatGPT plugins, OpenAI function-calling, Anthropic tools, LangChain tools, MCP servers) expand the attack surface; compromised or malicious plugins deserve a dedicated pattern category. Not present in current inline patterns.
- **Proposed detection signal**:
  - DFD element registers tool/plugin from third-party source (plugin marketplace, third-party MCP server, remote tool manifest) without declared integrity verification
  - Tool definitions (names, descriptions, parameters) pulled at runtime from remote source — attacker can inject malicious tool descriptions that hijack invocation
  - No declared allowlist of permitted tools for the agent at each trust boundary
  - Tool-registration surface accepts new tools without review gate or cryptographic attestation
- **False-positive risk**: Low — third-party plugin ingestion without integrity checks is a concrete signal
- **Taxonomy alignment**: AI Tool Abuse; ATLAS AML.T0058; MAESTRO L3 (Agent Frameworks) — mapping handled orchestrator-side

### Category 2 — Agent Tool Chaining (AML.T0059)

- **Source**: MITRE ATLAS v5.1+ (Oct 2025 catalog update)
- **Source citation**: `https://atlas.mitre.org/techniques/AML.T0059`
- **Source item**: AML.T0059 Agent Tool Chaining (combining multiple benign tool calls to achieve malicious outcome)
- **Why this category**: Individual tool calls may each be authorized and benign, but their composition enables actions the agent should not perform (e.g., read internal doc + send external email = data exfiltration). Inline patterns treat tools as individual actors and miss chaining.
- **Proposed detection signal**:
  - Agent has simultaneous access to an ingress tool (read/fetch) and an egress tool (post/send/publish) without declared composition policy
  - Tool manifest includes both a data-reading tool and a communication tool in the same session
  - No declared inter-tool taint tracking or data flow labeling
  - Agent uses chain-of-thought to sequence tool calls with no declared per-step human-in-the-loop gate
- **False-positive risk**: Medium — tool composition is the purpose of agentic systems; pattern flags absence of composition constraints rather than presence of multi-tool access
- **Taxonomy alignment**: AI Tool Abuse; ATLAS AML.T0059; related OWASP LLM06:2025 Excessive Agency

### Category 3 — Capability Escalation via Tool (AML.T0060)

- **Source**: MITRE ATLAS v5.1+ (Oct 2025 catalog update)
- **Source citation**: `https://atlas.mitre.org/techniques/AML.T0060`
- **Source item**: AML.T0060 Capability Escalation via Tool
- **Why this category**: A tool may expose capabilities the user does not have directly (e.g., database admin tool available to read-only user via agent). This is a tool-enabled privilege escalation vector distinct from general privilege-escalation patterns.
- **Proposed detection signal**:
  - Agent tools run under a service account with higher privilege than the invoking user
  - Tool permissions granted at agent-registration time rather than per-invocation authorization
  - No declared privilege-scoping mechanism (user-token propagation, impersonation, per-request access check) in tool invocation
  - Agent tool interacts with admin API (Kubernetes kubectl, cloud-provider admin, DB admin) from a user-facing conversation context
- **False-positive risk**: Low — agent-service-account privilege gaps are concrete architectural signals
- **Taxonomy alignment**: AI Tool Abuse; ATLAS AML.T0060; overlaps with STRIDE privilege-escalation via agent mediation

### Category 4 — Unauthorized Tool Invocation (AML.T0061)

- **Source**: MITRE ATLAS v5.1+ (Oct 2025 catalog update)
- **Source citation**: `https://atlas.mitre.org/techniques/AML.T0061`
- **Source item**: AML.T0061 Unauthorized Tool Invocation (agent called a tool it should not have, via prompt-injected instruction or goal misinterpretation)
- **Why this category**: An agent may invoke an authorized-to-it-but-not-authorized-for-this-request tool when manipulated. Distinct from plugin compromise because the tool itself is legitimate.
- **Proposed detection signal**:
  - Agent has broad tool registration without per-request intent verification
  - No declared mapping from user intent to permitted tool set for the current conversation
  - Tool invocation does not require confirmation for destructive or sensitive actions (delete, send, transact, publish)
  - Rate limits on tool invocation are per-agent rather than per-user-session
- **False-positive risk**: Medium — intent-to-tool mapping is rarely declared at architecture level
- **Taxonomy alignment**: AI Tool Abuse; ATLAS AML.T0061; related OWASP LLM06:2025 Excessive Agency

### Category 5 — MCP Server Poisoning (AML.T0062)

- **Source**: MITRE ATLAS v5.1+ (Oct 2025 catalog update)
- **Source citation**: `https://atlas.mitre.org/techniques/AML.T0062`
- **Source item**: AML.T0062 MCP Server Poisoning (Model Context Protocol server compromise leading to cross-agent tool-environment corruption)
- **Why this category**: MCP (Model Context Protocol) is rapidly becoming the standard agent-tool bridge; compromised or malicious MCP servers enable cross-agent attack propagation. Brand-new technique added Oct 2025 — not in any inline patterns.
- **Proposed detection signal**:
  - DFD element uses MCP protocol to connect to remote server outside the immediate trust zone
  - MCP server URL is user-configurable or comes from third-party directory
  - Tool discovery via MCP happens at runtime without declared manifest pinning or signature verification
  - Single MCP server provides tools to multiple agents or users without per-client isolation
  - No declared audit trail of MCP server responses (tool results, metadata, errors)
- **False-positive risk**: Low — remote MCP server usage without integrity verification is a concrete signal
- **Taxonomy alignment**: AI Tool Abuse; ATLAS AML.T0062; MAESTRO L3 (Agent Frameworks) — mapping handled orchestrator-side

## Source Verification Notes

- **ATLAS Oct 2025 additions (AML.T0058-T0062)**: These are the five agent-specific techniques referenced in research.md §3.2. Technique IDs and names should be verified against the current ATLAS catalog at `https://atlas.mitre.org/matrices/ATLAS` during Phase 3.2 extraction since ATLAS occasionally renames or re-numbers.
- AML.T0061 appears in research.md §3.2 under two slightly different names (research line 195 calls T0061 "AI Agent Tools" and line 196 calls T0062 "Exfiltration via AI Agent Tool Invocation"); the Oct 2025 update positioned them as listed in this brief, but verify exact naming during extraction.
- OWASP LLM06:2025 Excessive Agency is the canonical OWASP coverage of tool-abuse themes and should be cross-referenced with each ATLAS technique.
- **This agent is expected to produce 5 candidate categories (vs. 2-4 for other agents)** because the Oct 2025 ATLAS update specifically targets agentic tool abuse and all five techniques are directly applicable.
- Checked but NOT used: LangChain, LangGraph, AutoGPT documentation — framework-specific references, not taxonomy sources.
