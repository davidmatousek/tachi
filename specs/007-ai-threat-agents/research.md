# Research Summary: AI Threat Agents (Feature 007)

## Knowledge Base Findings

- **PAT-002 (Parallel Agent Validation)**: Three-layer validation framework from F-005 directly applies — Layer 1: Structural Audit (frontmatter, sections), Layer 2: Content Quality (detection patterns, component specificity), Layer 3: Integration Validation (orchestrator end-to-end)
- **F-005 Delivery Report**: 41 tasks completed in ~1 day with 3-way parallelism using a 5-wave execution pattern. Same strategy applies to F-007's 5 agents
- **ADR-003 (STRIDE-per-Element Dispatch)**: Defines the deterministic dispatch model — DFD type → STRIDE categories + AI keyword matching → AI agent categories
- **Anti-patterns to avoid**: Generic findings without component references, missing framework grounding (CWE/OWASP), inconsistent risk scoring, LLM variability in output

## Codebase Analysis

### Existing STRIDE Agent Pattern (agents/stride/)
- 6 agents (102-130 lines each) with consistent structure:
  - YAML frontmatter (6 fields: agent_name, category, threat_class, dfd_targets, owasp_references, output_schema)
  - Sections: Purpose → Detection Scope → Patterns and Indicators → Finding Template → Risk Level Computation → References
- All reference `schemas/finding.yaml` as output schema

### Current AI Agent Files (agents/ai/)
- 5 agents already exist and are content-complete (134-168 lines each):
  - `prompt-injection.md` (134 lines) — LLM01:2025 — targets Process
  - `data-poisoning.md` (143 lines) — LLM03:2025/LLM04:2025 — targets Data Store, Data Flow
  - `model-theft.md` (147 lines) — LLM10:2025 — targets Data Store, Process
  - `agent-autonomy.md` (168 lines) — ASI01 — targets Process
  - `tool-abuse.md` (139 lines) — MCP03:2025 — targets Process
- Follow identical structure to STRIDE agents with AI-specific frontmatter

### Finding Schema (schemas/finding.yaml)
- 10 required fields: id, category, component, threat, likelihood, impact, risk_level, mitigation, references, dfd_element_type
- AI categories supported: `agentic`, `llm`
- ID pattern: `^(S|T|R|I|D|E|AG|LLM)-\d+$`

### Orchestrator Dispatch (agents/orchestrator.md)
- Four-phase OWASP workflow: Scope → Determine Threats → Determine Countermeasures → Assess
- Two-layer AI dispatch: Layer 1 (orchestrator keywords) → Layer 2 (per-agent detection scope)
- Supports parallel and sequential dispatch modes

### Sample Architecture (examples/mermaid-agentic-app/input.md)
- Contains: LLM Agent Orchestrator (dual-dispatch), MCP Tool Server (AG-dispatch), Knowledge Base, External API, User
- Expected: 11 threat categories for LLM Agent Orchestrator, 8 for MCP Tool Server

## Architecture Constraints

- **docs/architecture/README.md**: ADR authority governs technical decisions; pattern catalog for reusable patterns
- **docs/standards/DEFINITION_OF_DONE.md**: 3-step DoD validation (pushed to production, tested, user validated). For documentation/prompt-file features, DoD may adapt
- **docs/standards/TRIAD_COLLABORATION.md**: Feature PRD follows parallel review (PM + Architect + Tech-Lead)
- **ADR-003**: STRIDE-per-Element normalization + AI keyword dispatch is the canonical dispatch model

## Industry Research

### OWASP Frameworks (Official Reference IDs)

**OWASP LLM Top 10 v2025** (format: `LLM{NN}:2025`):
- LLM01:2025 — Prompt Injection
- LLM02:2025 — Sensitive Information Disclosure
- LLM03:2025 — Supply Chain
- LLM04:2025 — Data and Model Poisoning
- LLM05:2025 — Improper Output Handling
- LLM06:2025 — Excessive Agency
- LLM07:2025 — System Prompt Leakage (new in 2025)
- LLM08:2025 — Vector and Embedding Weaknesses (new in 2025)
- LLM09:2025 — Misinformation
- LLM10:2025 — Unbounded Consumption

**OWASP Agentic Top 10 2026** (format: `ASI{NN}`):
- ASI01 — Agent Goal Hijack
- ASI02 — Tool Misuse and Exploitation
- ASI03 — Identity and Privilege Abuse
- ASI04 — Agentic Supply Chain Vulnerabilities
- ASI05 — Unexpected Code Execution
- ASI06 — Memory and Context Poisoning
- ASI07 — Insecure Inter-Agent Communication
- ASI08 — Cascading Failures
- ASI09 — Human-Agent Trust Exploitation
- ASI10 — Rogue Agents

**OWASP MCP Top 10 2025** (format: `MCP{NN}:2025`):
- MCP01:2025 — Token Mismanagement and Secret Exposure
- MCP02:2025 — Privilege Escalation via Scope Creep
- MCP03:2025 — Tool Poisoning
- MCP04:2025 — Software Supply Chain Attacks
- MCP05:2025 — Command Injection and Execution
- MCP06:2025 — Prompt Injection via Contextual Payloads
- MCP07:2025 — Insufficient Authentication and Authorization
- MCP08:2025 — Lack of Audit and Telemetry
- MCP09:2025 — Shadow MCP Servers
- MCP10:2025 — Context Injection and Over-Sharing

### Threat Category Cross-References
| Pattern | LLM Top 10 | Agentic Top 10 | MCP Top 10 |
|---------|------------|-----------------|------------|
| Prompt Injection | LLM01:2025 | ASI01 | MCP06:2025 |
| Supply Chain | LLM03:2025 | ASI04 | MCP04:2025 |
| Excessive Autonomy | LLM06:2025 | ASI02, ASI10 | MCP02:2025 |
| Data/Context Poisoning | LLM04:2025, LLM08:2025 | ASI06 | MCP03:2025 |
| Code Execution | LLM05:2025 | ASI05 | MCP05:2025 |

### Complementary Frameworks
- **MAESTRO** (Cloud Security Alliance): Seven-layer agentic AI reference architecture
- **ASTRIDE** (arXiv 2512.04785): Extends STRIDE with "A" category for AI agent-specific attacks
- **MITRE ATLAS**: Adversarial AI attack taxonomy with techniques mapped to AI lifecycle

## Recommendations for Spec

- **Follow F-005 spec structure exactly**: Same user story organization (5 stories, P0/P1/P2), acceptance scenarios (Given/When/Then), success criteria pattern
- **Emphasize validation over creation**: All 5 AI agent files exist and are content-complete — the spec should focus on validating correctness, not authoring from scratch
- **Three-layer validation**: Structural audit → Content quality → Integration validation (proven in F-005)
- **Component specificity as hard requirement**: 100% of findings must reference named components from input — zero tolerance for generic findings
- **DFD element targeting compliance**: Each agent targets only its declared DFD types — no out-of-scope findings
- **OWASP reference accuracy**: Use official ID formats (LLM{NN}:2025, ASI{NN}, MCP{NN}:2025) — verify against published lists
- **Empty results for non-AI architectures**: Critical edge case — agents must produce zero findings for traditional-only architectures
- **Wave-based parallel execution**: Independent agents can be validated in parallel (LLM agents vs. Agentic agents)
