# Enrichment Brief — agent-autonomy

**Agent type**: AI
**Primary threat category**: Agent Autonomy and Excessive Agency
**Created**: 2026-04-11
**Feature**: 082 — Threat Agent Skill References

## Candidate New Pattern Categories

### Category 1 — Excessive Agency (OWASP LLM06:2025)

- **Source**: OWASP Top 10 for LLM Applications v2025
- **Source citation**: `https://genai.owasp.org/llmrisk/llm06-excessive-agency/`
- **Source item**: LLM06:2025 Excessive Agency (sub-categories: Excessive Functionality, Excessive Permissions, Excessive Autonomy)
- **Why this category**: OWASP LLM06:2025 is the canonical coverage of agent autonomy threats, with three distinct sub-categories. Inline patterns under-cover the Excessive Functionality and Excessive Permissions sub-categories specifically.
- **Proposed detection signal**:
  - Agent has access to functionality not required for its declared user-visible purpose (e.g., chatbot with file-write tools)
  - Agent operates with broad permissions (admin-level, service-account-level) rather than user-level scoped permissions
  - No declared human-in-the-loop gate for irreversible actions (send, delete, publish, transfer, merge, deploy)
  - Agent plans and executes multi-step workflows without declared step-level authorization checks
- **False-positive risk**: Medium — autonomy scoping is often implicit in architecture descriptions
- **Taxonomy alignment**: AI Agent Autonomy; OWASP LLM06:2025 (all three sub-categories); MAESTRO L3 (Agent Frameworks) — mapping handled orchestrator-side

### Category 2 — Agent Context Poisoning (ATLAS AML.T0058 or related Oct 2025 technique)

- **Source**: MITRE ATLAS v5.1+ (Oct 2025 catalog update, cross-referenced with research.md §3.2 line 196)
- **Source citation**: `https://atlas.mitre.org/matrices/ATLAS`
- **Source item**: ATLAS Oct 2025 Agent Context Poisoning technique (research.md lists this under AML.T0058, which is also cited in tool-abuse brief for Plugin Compromise; Phase 3.2 must verify ATLAS catalog disambiguates these)
- **Why this category**: Multi-turn memory and long-running agent state can be corrupted by prompt-injected instructions that persist across sessions — a distinct threat from immediate prompt injection because the poisoning outlasts the injecting session.
- **Proposed detection signal**:
  - Agent maintains cross-session memory (user preferences, conversation history, learned facts) that is writable from user input
  - No declared sanitization or review gate when user input updates agent memory
  - Agent memory shared across users or tenants without isolation
  - Long-term memory backed by vector store that is also used for retrieval (recursive poisoning risk: past poisoned memory retrieves in future context)
- **False-positive risk**: Medium — memory architecture is often under-specified
- **Taxonomy alignment**: AI Agent Autonomy; ATLAS agent-context technique (Oct 2025); overlaps with data-poisoning via memory as a poisoning target

### Category 3 — Goal Drift and Unbounded Planning Loops

- **Source**: NIST AI 600-1 (Generative AI Profile) combined with OWASP LLM10:2025
- **Source citation**: `https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.600-1.pdf` and `https://genai.owasp.org/llmrisk/llm10-unbounded-consumption/`
- **Source item**: NIST AI 600-1 §2.1 (CBRN and Dangerous Information) and §2.3 (Confabulation) — agentic risk framing; OWASP LLM10:2025 Unbounded Consumption — cost/resource side of unbounded planning
- **Why this category**: Reasoning-agent loops (ReAct, Reflexion, self-ask) can run indefinitely, drift from original goals, or generate cascading tool calls. NIST AI 600-1 frames this as a governance risk; OWASP LLM10:2025 frames it as a consumption risk.
- **Proposed detection signal**:
  - Agent uses reasoning loop (ReAct, chain-of-thought with tool calls, planner-executor) without declared per-loop iteration cap
  - No declared token/cost budget enforcement per task or per conversation
  - Agent can spawn sub-agents or sub-tasks without declared depth limit
  - Termination condition is LLM-determined (the agent decides when to stop) without external watchdog
  - No declared periodic goal-consistency check against original user intent
- **False-positive risk**: Medium — loop bounds are often implicit or framework-default
- **Taxonomy alignment**: AI Agent Autonomy; NIST AI 600-1 §2.1; OWASP LLM10:2025

### Category 4 — Delegation Loop and Multi-Agent Collusion

- **Source**: OWASP AI Exchange combined with research literature referenced via OWASP AI Exchange
- **Source citation**: `https://owaspai.org/docs/ai_security_overview/`
- **Source item**: OWASP AI Exchange — Agentic AI chapter discussing multi-agent systems, delegation chains, and emergent behavior risks
- **Why this category**: Multi-agent systems where one agent delegates to or invokes another can form delegation loops, collusive task-splitting, or responsibility diffusion. Not covered in current inline patterns.
- **Proposed detection signal**:
  - DFD declares multi-agent architecture where Agent A can invoke Agent B and vice versa (cycle-forming delegation)
  - Agent-to-agent messages are trusted inputs without declared authentication or content verification
  - No declared centralized audit trail across multi-agent interactions (per-agent logs without correlation)
  - Shared task queue or shared memory across agents without per-agent isolation
  - Delegation graph can grow at runtime (agent dynamically spawning new agents)
- **False-positive risk**: Medium — multi-agent topology is often declared at a high level
- **Taxonomy alignment**: AI Agent Autonomy; OWASP AI Exchange; overlaps with tool-abuse via agent-as-tool

## Source Verification Notes

- OWASP LLM06:2025 is the flagship coverage for this agent and should drive the primary pattern structure.
- The Oct 2025 ATLAS agent-context-poisoning technique is referenced in research.md §3.2 line 196 — the exact technique ID may be AML.T0058 (which is cited in the tool-abuse brief for Plugin Compromise) or a nearby number; **Phase 3.2 extraction must disambiguate against the live ATLAS catalog** before citing.
- NIST AI 600-1 sections 2.1, 2.3, and 2.7 all touch agentic autonomy risks; cite the most specific section during extraction rather than the generic document URL.
- OWASP AI Exchange has rapidly-evolving Agentic AI content; URL is canonical but section structure changes. Verify during Phase 3.2.
- Checked but NOT used: CSA MAESTRO L3 (Agent Frameworks) — per approved source set, MAESTRO is for layer mapping only, handled separately via Feature 084.
- Checked but NOT used: academic agentic safety papers (Constitutional AI, AutoGPT post-mortems) — these are background context, not authoritative taxonomy sources for detection patterns.
