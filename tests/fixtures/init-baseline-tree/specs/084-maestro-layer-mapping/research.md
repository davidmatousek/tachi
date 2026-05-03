# Research Summary: MAESTRO Layer Mapping

## Knowledge Base Findings
- No existing KB patterns found for MAESTRO layer mapping or taxonomy overlay functionality
- No prior bug fixes related to component classification or layer tagging

## Codebase Analysis

### Shared Reference File Pattern (Feature 078)
- **Location**: `.claude/skills/tachi-shared/references/`
- **Existing files**: `severity-bands-shared.md`, `stride-categories-shared.md`, `finding-format-shared.md`
- **Loading mechanism**: Agents use Read tool to load individual reference files on-demand
- **Pattern to follow**: Create `maestro-layers-shared.md` in same directory with YAML frontmatter (type, name, version, source_schema, consumers)

### Orchestrator Phase 1 Component Inventory
- **Agent**: `.claude/agents/tachi/orchestrator.md`
- **Phase 1 objectives**: Format detection, component extraction, DFD classification, trust boundary identification
- **Integration point**: After DFD classification, before dispatch table production
- **Intermediate output**: Component table (Name, DFD Type, Description) — MAESTRO Layer column added here

### AI Keyword Dispatch Pattern (Existing)
- **Reference**: `.claude/skills/tachi-orchestration/references/dispatch-rules.md` (lines 57-109)
- **LLM keywords**: "LLM", "model", "GPT", "Claude"
- **AG keywords**: "agent", "autonomous", "orchestrator", "MCP server", "tool server", "plugin"
- **Matching rules**: Case-insensitive, substring match against component name + description
- **MAESTRO follows same pattern**: Keyword matching against name, description, and DFD type; first-match-wins (L1-L7 ordered)

### Finding IR Schema
- **Schema file**: `schemas/finding.yaml`
- **Required fields**: id, category, component, threat, likelihood, impact, risk_level, mitigation
- **Optional fields**: references, dfd_element_type, delta_status, baseline_run_id, correlation_group, fingerprints
- **Extension point**: Add optional `maestro_layer` field (string enum, default "Unclassified")

### Output Formatters
- **STRIDE tables**: ID, [Status], Component, Threat, Likelihood, Impact, Risk Level, Mitigation
- **AI tables**: Same + OWASP Reference column
- **Output template**: `templates/tachi/output-schemas/threats.md`
- **SARIF**: `result.properties` object allows arbitrary fields (additive extension safe)

### Example Architectures
- 6 examples in `examples/` directory: web-app, agentic-app, microservices, ascii-web-api, free-text-microservice, mermaid-agentic-app
- All will need output regeneration with MAESTRO layer tags

## Architecture Constraints
- **Phase 1 integration** (CRITICAL): Layer classification after DFD extraction, uses same component inventory
- **Dispatch logic** (NO CHANGE): MAESTRO does not affect STRIDE-per-Element or AI keyword dispatch rules
- **Correlation detection** (NO CHANGE): 5 deterministic rules unchanged; layer is metadata only
- **Risk scoring** (NO CHANGE): Layer does not affect risk_level computation
- **Coverage gate** (NO CHANGE): Required categories unchanged; coverage matrix excludes MAESTRO (out of scope)
- **Backward compatibility** (CRITICAL): All new fields optional; existing output unchanged when no layers detected
- **Baseline mode**: Layer tag propagates through delta status; SARIF merge behavior deferred to plan
- **SARIF fingerprints**: findingId/v1 and primaryLocationLineHash NOT affected by layer assignment

## Industry Research
- **CSA MAESTRO**: Cloud Security Alliance seven-layer taxonomy for agentic AI architectures (published Feb 2025)
- **Adoption**: IriusRisk, Snyk Labs, and Practical DevSecOps have published MAESTRO integration content
- **Real-world application**: CSA published "Applying MAESTRO to Real-World Agentic AI Threat Models" (Feb 2026) demonstrating CI/CD pipeline integration
- **Layer taxonomy**: L1 Foundation Model, L2 Data Operations, L3 Agent Framework, L4 Deployment Infrastructure, L5 Security, L6 Agent Ecosystem, L7 User Interface
- **Key insight**: "Threats don't just exist at individual layers — they chain across layers" (CSA)

## Recommendations for Spec
- Follow the shared reference file pattern exactly (Feature 078) for MAESTRO layer definitions
- Reuse existing AI keyword dispatch matching logic for MAESTRO layer classification
- Keep layer assignment as passive metadata — no changes to agent detection, scoring, or dispatch
- First-match-wins ordering (L1-L7) is load-bearing — document rationale clearly
- "Unclassified" is the safe default for components that don't match any layer keywords
- Validate against all 6 example architectures to confirm >90% classification coverage
- SARIF extension is additive only — test with GitHub Code Scanning for compatibility
