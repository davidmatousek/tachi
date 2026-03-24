# Research Summary: Example Threat Models (Feature 024)

## Knowledge Base Findings

- **PAT-001** (Wave-Based Parallelism): All 3 examples can be built in parallel since they have no cross-dependencies until the validation phase. Directly applicable to PRD 024's 4-wave build strategy.
- **PAT-004** (SARIF Maps to STRIDE): When the intermediate representation is well-structured, adding new output formats is straightforward. Design the IR first, then map mechanically — applies to example creation.
- **PAT-005** (Spec-First Architecture): Local-first pattern applies — examples must work without external dependencies.
- 5 of 20 KB entries populated. No bug fixes recorded yet.

## Codebase Analysis

### Existing Examples (all schema v1.0)
| Directory | Input Format | Components | AI Findings | Notes |
|-----------|-------------|------------|-------------|-------|
| `examples/ascii-web-api/` | ASCII box-drawing | 4 (User, API Gateway, Auth Service, User DB) | None (correct) | `input.md` + `threats.md` |
| `examples/free-text-microservice/` | Free-text prose | 7 (API GW, Order Svc, Payment Svc, Inventory DB, MQ, Stripe, Clients) | None (correct) | `input.md` + `threats.md` |
| `examples/mermaid-agentic-app/` | Mermaid flowchart | 5 (User, LLM Orchestrator, MCP Tool Server, KB, External API) | AG + LLM (both) | `input.md` + `threats.md` + threat-report + infographic-spec + 12 attack trees |

### Output Schema v1.1 Structure
- 7 required sections + Section 4a (Correlated Findings)
- Finding ID patterns: `{S|T|R|I|D|E}-{N}` for STRIDE, `AG-{N}` / `LLM-{N}` for AI
- AI threat tables add `owasp_reference` field not present in STRIDE tables
- Coverage matrix: three-state cells (integer count, `---` for clean, `n/a` for not-applicable)
- 5 deterministic correlation rules: CR-1 through CR-5

### Patterns to Follow
- Mermaid flowchart with subgraph blocks for trust zones
- Descriptive arrow labels showing data/action types
- Component names trigger AI dispatch (e.g., "LLM Agent Orchestrator" triggers both LLM + AG keywords)
- STRIDE-per-Element rules determine n/a cells in coverage matrix

### Key File Paths
- Output schema: `schemas/output.yaml` (v1.1)
- Canonical template: `templates/threats.md` (v1.1)
- Interface contract: `docs/INTERFACE-CONTRACT.md` (v1.1)
- Finding IR: `schemas/finding.yaml` (v1.0)
- STRIDE agents: `agents/stride/` (6 agents)
- AI agents: `agents/ai/` (5 agents: agent-autonomy, tool-abuse, prompt-injection, data-poisoning, model-theft)

## Architecture Constraints

### Schema Migration (v1.0 → v1.1)
- Section 4a (Correlated Findings) is required even when empty — show "No cross-agent correlations detected."
- Coverage Matrix uses deduplicated counts when correlations exist
- Risk Summary uses parenthetical notation for raw vs deduplicated counts

### AI Agent Dispatch Rules
- LLM keywords: "LLM", "model", "GPT", "Claude"
- Agentic keywords: "agent", "autonomous", "orchestrator", "MCP server", "tool server", "plugin"
- Web-app (no AI components): AI sections must show "No AI components detected" (empty results, not omitted)

### OWASP Cross-Reference Mechanism (PRD FR-004)
- Implemented as **appendix mapping table** within each `threats.md`
- NOT as schema field additions to `output.yaml`
- Avoids global impact while demonstrating framework coverage

### Interface Contract Constraints
- No side effects; outputs immutable once generated
- Minimum input: 1 component + 1 data flow
- Classification defaults to `confidential`

## Industry Research

### OWASP Top 10 Web 2025 (A01-A10)
| ID | Category |
|----|----------|
| A01:2025 | Broken Access Control |
| A02:2025 | Security Misconfiguration |
| A03:2025 | Software Supply Chain Failures |
| A04:2025 | Cryptographic Failures |
| A05:2025 | Injection |
| A06:2025 | Insecure Design |
| A07:2025 | Authentication Failures |
| A08:2025 | Software or Data Integrity Failures |
| A09:2025 | Security Logging and Alerting Failures |
| A10:2025 | Mishandling of Exceptional Conditions |

### OWASP Agentic Top 10 2026 (ASI01-ASI10)
| ID | Category |
|----|----------|
| ASI01 | Agent Goal Hijack |
| ASI02 | Tool Misuse and Exploitation |
| ASI03 | Identity and Privilege Abuse |
| ASI04 | Agentic Supply Chain Vulnerabilities |
| ASI05 | Unexpected Code Execution (RCE) |
| ASI06 | Memory and Context Poisoning |
| ASI07 | Insecure Inter-Agent Communication |
| ASI08 | Cascading Failures |
| ASI09 | Human-Agent Trust Exploitation |
| ASI10 | Rogue Agents |

### OWASP MCP Top 10 2025 (MCP01-MCP10)
| ID | Category |
|----|----------|
| MCP01:2025 | Token Mismanagement and Secret Exposure |
| MCP02:2025 | Privilege Escalation via Scope Creep |
| MCP03:2025 | Tool Poisoning |
| MCP04:2025 | Software Supply Chain Attacks and Dependency Tampering |
| MCP05:2025 | Command Injection and Execution |
| MCP06:2025 | Intent Flow Subversion (Prompt Injection via Contextual Payloads) |
| MCP07:2025 | Insufficient Authentication and Authorization |
| MCP08:2025 | Lack of Audit and Telemetry |
| MCP09:2025 | Shadow MCP Servers |
| MCP10:2025 | Context Injection and Over-Sharing |

### Cross-Framework Overlap
| Theme | OWASP Web | OWASP Agentic | OWASP MCP |
|-------|-----------|---------------|-----------|
| Access control | A01 | ASI03 | MCP07 |
| Injection | A05 | ASI01 | MCP05, MCP06 |
| Supply chain | A03 | ASI04 | MCP04 |
| Logging | A09 | — | MCP08 |
| Data integrity | A08 | ASI06 | MCP10 |

### Best Practices
- Use structured methodology (STRIDE-per-Element) — avoid ad-hoc identification
- Include concrete attack scenarios and actionable mitigations for each threat
- Prioritize by risk using consistent calibration matrix
- Make examples self-explanatory without requiring additional documentation

## Recommendations for Spec

- **Create fresh examples** under standardized naming (`web-app`, `agentic-app`, `microservices`) rather than adapting existing ones — the format conversion (ASCII/free-text → Mermaid) plus schema migration (v1.0 → v1.1) plus OWASP cross-references is more effort than starting fresh
- **Retain existing examples** as format-specific test fixtures (they validate ASCII and free-text input handling)
- **Mermaid diagrams** should use subgraph blocks for trust zones, descriptive arrow labels, and component names that trigger correct AI dispatch
- **OWASP appendix tables** should map finding IDs to framework category IDs with category names for readability
- **Web-app AI sections** must show "No AI components detected" — this is a key demo of selective dispatch
- **Agentic-app** should exercise all 5 correlation rules (CR-1 through CR-5) to showcase Section 4a
- **Microservices** should emphasize cross-service trust boundaries and service-to-service authentication
- **Framework relationship hierarchy** in README should show STRIDE as the base methodology with OWASP frameworks as classification overlays
