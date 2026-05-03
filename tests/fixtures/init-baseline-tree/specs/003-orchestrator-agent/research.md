# Research Summary: Orchestrator Agent (F-002)

## Knowledge Base Findings
- No existing KB entries found (KB not yet established for this project)
- No prior patterns or bug fixes to reference

## Codebase Analysis

### Existing Components (F-001 Delivered)
- **Orchestrator placeholder**: `agents/orchestrator.md` — 20-line stub, status: placeholder
- **STRIDE agents (6)**: `agents/stride/{spoofing,tampering,repudiation,info-disclosure,denial-of-service,privilege-escalation}.md` — All implemented (~100+ lines each) with frontmatter fields: agent_name, category, threat_class, dfd_targets, owasp_references, output_schema
- **AI agents (5)**: `agents/ai/{prompt-injection,data-poisoning,model-theft,agent-autonomy,tool-abuse}.md` — All implemented (~100+ lines each) with same frontmatter structure
- **5-to-2 table mapping**: AG table (agent-autonomy, tool-abuse) + LLM table (prompt-injection, data-poisoning, model-theft) per `agents/ai/README.md`

### Schemas & Templates (Stable v1.0)
- **Finding IR schema**: `schemas/finding.yaml` — 10 fields (id, category, component, threat, likelihood, impact, risk_level, mitigation, references, dfd_element_type) with OWASP 3x3 risk matrix embedded
- **Input schema**: `schemas/input.yaml` — 5 format definitions with recognition patterns and trust boundary notation per format
- **Output schema**: `schemas/output.yaml` — 7 required sections, frontmatter requirements, section ordering
- **Output template**: `templates/threats.md` — Canonical 7-section structure with table formats for STRIDE (6), AI (2), coverage matrix, risk summary, recommended actions

### Example Inputs (Validation References)
- `examples/ascii-web-api/input.md` — ASCII format, 4 components (External User, API Gateway, Auth Service, User DB)
- `examples/mermaid-agentic-app/input.md` — Mermaid format, 5 components with dual-dispatch demo (LLM Agent Orchestrator triggers both LLM+AG)
- `examples/free-text-microservice/input.md` — Prose narrative format

### Interface Contract (docs/INTERFACE-CONTRACT.md)
- **Section 1**: Input format detection (priority-ordered: ASCII → free-text → Mermaid → PlantUML → C4)
- **Section 2**: STRIDE-per-Element normalization table (4 DFD types → applicable STRIDE categories)
- **Section 3**: AI dispatch rules (LLM keywords, AG keywords, dual-dispatch)
- **Section 4**: Output specification (frontmatter, 7 sections)
- **Section 5**: Invocation protocol (format, content, context fields)
- **Section 6**: Input sanitization guidance (data-not-instructions boundary)
- **Section 7**: Error conditions (UNSUPPORTED_FORMAT, NO_COMPONENTS, INVALID_FORMAT_VALUE)

## Architecture Constraints
- **Knowledge system**: Markdown + YAML files only, no runtime code, no compiled dependencies
- **Hub-and-spoke model**: Orchestrator consumes immutable F-001 artifacts, produces output conforming to template
- **Platform-neutral**: No platform-specific syntax (Claude Code, Cursor, etc.) — adapters are F-009 scope
- **Content-as-data**: Architecture input treated as data, not instructions (sanitization boundary)
- **F-001 spec pattern**: Frontmatter with triad sign-offs, user stories with P1/P2 priority, Given/When/Then acceptance criteria

### Dependencies
- **Depends on**: F-001 (delivered) — repo structure, interface contract, schemas, templates, examples, agent stubs
- **Blocks**: F-003 (STRIDE Agents), F-004 (AI Agents), F-005 (Dedup & Risk Rating), F-009 (Platform Adapters)

## Industry Research
- **OWASP Threat Modeling Process**: Four-step methodology (Scope, Determine Threats, Determine Countermeasures, Assess) — well-established, stable
- **STRIDE-per-Element**: Microsoft (MSDN 2006) — maps DFD element types to applicable threat categories, deterministic dispatch
- **OWASP LLM Top 10 v2025**: Published, stable — covers prompt injection, data poisoning, model theft
- **OWASP Agentic Top 10 (2026 draft)**: Covers agent autonomy, tool abuse — may evolve
- **OWASP MCP Top 10 v0.1 Beta**: Early draft — affects AG keyword list
- **Automated threat model generation**: Emerging field — most tools use structured input (DFD diagrams) and deterministic dispatch rules

## Recommendations for Spec
- Leverage F-001 artifacts verbatim — do not redefine dispatch rules or schema fields
- Spec should focus on WHAT the orchestrator does (parse, classify, dispatch, assemble) not HOW the prompt is structured
- User stories should map 1:1 to the PRD's 3 user stories (US-001 parse, US-002 dispatch, US-003 assemble)
- Success criteria should reference the mermaid example as the primary validation input
- Note that agents are implemented (not stubs) — spec should account for real agent output
- Address Architect concerns from PRD review: FR-5 agent communication mechanism and component name sanitization
- Address open questions from PRD: classification confidence, finding count limits, prompt modularity, Mermaid sequence diagrams
