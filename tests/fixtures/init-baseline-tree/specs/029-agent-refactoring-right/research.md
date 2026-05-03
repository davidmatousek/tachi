# Research Summary: Agent Refactoring — Right-Size Orchestrator, Report, and Infographic Agents

## Knowledge Base Findings

- **PAT-001 (Wave-Based Parallelism)**: Content-only features (markdown/YAML) have high parallelism potential. Report + Infographic agents can be refactored in parallel (Wave 3).
- **PAT-002 (Parallel Agent Validation)**: Multiple independent domain artifacts can be validated in isolation. The 3 target agents are independent — refactoring one does not block another.
- **PAT-004 (SARIF Maps to STRIDE)**: SARIF generation is well-structured with clear IR-to-format mapping. This content is extractable because it is a self-contained specification block (~490 lines) consulted only at Phase 4 completion.
- **PAT-005 (Spec-First Architecture)**: Infographic agent already uses graceful degradation for Gemini API — extraction must preserve the six failure condition handling.
- Key lesson: Preservation-first approach (inventory all capabilities before changes) prevented functionality loss in Feature 003 agent refactoring.

## Codebase Analysis

### Target Agents (Confirmed Inventory)

| Agent | Lines | Category | Target |
|-------|-------|----------|--------|
| orchestrator.md | 2,085 | report/orchestration | ~1,100-1,200 |
| threat-report.md | 801 | report | ~300-400 |
| threat-infographic.md | 592 | report | ~300-400 |

### Orchestrator Content Breakdown (from agent-sizing-analysis.md)

| Content Type | ~Lines | Extractable? |
|---|---|---|
| Metadata + agent roster | 40 | No |
| Output format specification (7 sections + SARIF) | 580 | SARIF portion yes |
| Phase 1: Format detection + DFD classification | 260 | Partially |
| Phase 2: STRIDE-per-Element + AI dispatch rules | 270 | No |
| Phase 3: Risk validation + correlation | 200 | No |
| Phase 4: Coverage matrix + risk summary | 200 | No |
| SARIF generation (mapping, fingerprints, taxonomies) | 500 | Yes — reference doc |
| Phase 5-6 dispatch + opt-out | 120 | Somewhat |
| Error handling + validation checklist | 170 | Yes — reference doc |
| Verbose prose (redundant narration) | 200 | Delete |

**~1,400 lines irreducible. ~600 lines extractable or deletable.**

### Well-Sized Agents (No Changes Required)

All 11 threat agents (108-196 lines each): spoofing, tampering, repudiation, info-disclosure, denial-of-service, privilege-escalation, prompt-injection, data-poisoning, model-theft, agent-autonomy, tool-abuse.

### No Existing Reference Documents

`adapters/claude-code/agents/references/` does not exist — must be created as part of this feature.

### Patterns to Follow

- Agent best practices: 150-300 line ceiling, 8-section structure, preservation-first enhancement (11-step process)
- Feature 003 refactoring achieved 58% total line reduction across 13 agents
- Reference extraction pattern: move specification content to separate files, load on-demand via Read tool

## Architecture Constraints

### Key Documents

- `.claude/agents/_AGENT_BEST_PRACTICES.md` — 300-line ceiling, preservation-first 11-step process
- `docs/research/agent-sizing-analysis.md` — Detailed content breakdown and extraction targets
- `docs/product/02_PRD/029-agent-refactoring-right-size-2026-03-25.md` — Approved PRD

### Constraints

1. **No pipeline splitting**: Orchestrator phases are sequential with cumulative state. Splitting into phase-agents increases token cost (data transmitted twice at each handoff).
2. **Reference extraction only**: Move consultation-only content to separate files loaded on-demand. Core orchestration logic stays in the agent.
3. **Zero regression**: All 11 threat agents byte-identical. Output structure equivalent on regression test.
4. **Self-contained references**: No cross-references between reference documents.
5. **Error-on-missing**: If a reference document is missing, agent must fail with clear error (not silently produce incomplete output).

### Dependencies

- PRD 003 (Orchestrator Agent) — defines pipeline phases
- PRD 015 (Threat Report Agent) — defines report generation
- PRD 018 (Threat Infographic Agent) — defines infographic generation

## Industry Research

### Prompt Sizing Best Practices (2024-2026)

- **Chroma "Context Rot" (July 2025)**: Adding full context (~113K tokens) drops accuracy by 30% vs focused ~300-token version. Three compounding mechanisms: lost-in-the-middle effect, attention dilution, distractor interference.
- **Liu et al. (TACL 2024)**: Performance highest at beginning/end of input; degrades for middle content.
- **Anthropic guidance**: Use just-in-time retrieval; dynamically load data via tools rather than pre-loading. Put longform data at top, queries at end (30% quality improvement).
- **Claude 4.6**: More responsive to system prompts — may need LESS prompting for same compliance.
- **Production benchmark**: Claude Code system prompt ~14,328 tokens. Tachi orchestrator at ~28,000 tokens is 2x this benchmark.

### Reference Extraction Pattern

The just-in-time retrieval pattern is well-established in production LLM systems. Content consulted only at specific pipeline points lives in separate files loaded on-demand, reducing always-loaded context without adding orchestration overhead.

## Recommendations for Spec

- Structure user stories around the 3 target agents (orchestrator, report, infographic) plus a zero-regression validation story
- The orchestrator has clear extraction targets identified in the research: SARIF spec (~490 lines), validation checklist (~80 lines), error templates (~100 lines), plus ~200 lines of deletable prose
- Report and infographic agents need detailed content inventories during the Plan phase — the PRD research only provides granular analysis for the orchestrator
- Capability inventory must be committed as a deliverable before any extraction begins
- The PRD's error handling section distinction (pure error templates vs defensive specification content) is critical — spec must reflect this
- Regression testing should compare structural equivalence (finding count, risk distribution, section presence), not exact text match
