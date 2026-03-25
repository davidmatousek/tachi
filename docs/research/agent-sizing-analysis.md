# Agent Sizing Analysis: Research & Findings

> **Date**: 2026-03-25
> **Context**: Evaluating tachi agent sizes against best practices and current research
> **Triggered by**: Orchestrator at 2,093 lines — 7x over 300-line best practices ceiling

---

## 1. Agent Inventory

### Statistical Summary

| Metric | Value |
|--------|-------|
| Total Agent Count | 14 (11 threat + 3 report/orchestration) |
| Total Template Count | 2 |
| Total Lines (All Agents) | 5,103 |
| Average Lines per Threat Agent | 151 |
| Average Lines per Report Agent | 826 |
| Largest Agent | orchestrator (2,085 lines) |
| Smallest Agent | spoofing (108 lines) |
| Agents > 300 Lines | 3 (orchestrator, threat-report, threat-infographic) |

### Full Inventory (sorted by line count descending)

| Agent | Lines | Category | Status |
|-------|-------|----------|--------|
| orchestrator.md | 2,085 | report/orchestration | **7x over ceiling** |
| threat-report.md | 801 | report | **2.7x over ceiling** |
| threat-infographic.md | 592 | report | **2x over ceiling** |
| agent-autonomy.md | 196 | AI/agentic | Good |
| model-theft.md | 183 | AI/agentic | Good |
| tool-abuse.md | 180 | AI/agentic | Good |
| data-poisoning.md | 166 | AI/agentic | Good |
| prompt-injection.md | 162 | AI/agentic | Good |
| denial-of-service.md | 136 | STRIDE | Good |
| privilege-escalation.md | 131 | STRIDE | Good |
| info-disclosure.md | 123 | STRIDE | Good |
| tampering.md | 121 | STRIDE | Good |
| repudiation.md | 119 | STRIDE | Good |
| spoofing.md | 108 | STRIDE | Good |

### Templates

| Template | Lines |
|----------|-------|
| infographic-system-architecture.md | 304 |
| infographic-baseball-card.md | 220 |

---

## 2. Web Research: LLM Agent Prompt Sizing (2024-2026)

### Key Findings

#### "Lost in the Middle" is real and persistent
- **Chroma "Context Rot" study (July 2025)**: Tested 18 state-of-the-art models (Claude Opus 4, Sonnet 4, GPT-4.1, Gemini 2.5 Pro, Qwen3-235B). Adding full conversation history (~113K tokens) can drop accuracy by 30% compared to focused ~300-token version. Three compounding mechanisms: lost-in-the-middle effect, attention dilution, distractor interference.
- **Liu et al. (TACL 2024)**: Performance highest when relevant information at beginning or end of input; degrades significantly for middle content. Persists across all models tested in 2025.

#### Production Benchmarks

| System | Prompt Size | Notes |
|--------|-------------|-------|
| Claude Code system prompt | ~14,328 tokens | Production agent, loaded every call |
| Claude 3.7 conversational | ~24,000 tokens | Includes all safety, tools, personality |
| Average LLM prompt (2025) | ~5,400 tokens | Tripled since 2023; programming 3-4x higher |
| Tachi orchestrator | ~28,000 tokens | 2x Claude Code benchmark |
| Boris Cherny CLAUDE.md target | <100 lines (~2,500 tokens) | Per-file; eagerly loaded |

#### Multi-Agent Tradeoffs

| Finding | Source |
|---------|--------|
| Multi-agent: 42.68% success vs 2.92% single-agent on complex tasks | Cornell study (Dataiku) |
| Multi-agent incident response: 80x improvement in solution correctness | arxiv 2511.15755 |
| BUT: Unstructured multi-agent networks amplify errors up to 17.2x | arxiv 2503.13657 |
| Difficulty-guided orchestration: 11.21% accuracy gain at 64% cost | arxiv 2509.11079 |

#### Anthropic's Guidance
- "Minimal does not necessarily mean short; you still need to give the agent sufficient information"
- Put longform data at the top, queries at the end (30% quality improvement)
- Use just-in-time retrieval; dynamically load data via tools rather than pre-loading
- Sub-agent pattern: each uses "tens of thousands of tokens" but returns only "1,000-2,000 tokens"
- Claude 4.6 is more responsive to system prompts — may need LESS prompting for same compliance

### Sources
- Anthropic: Effective Context Engineering for AI Agents (anthropic.com)
- Anthropic: Claude 4.6 Prompting Best Practices (docs.anthropic.com)
- Chroma: Context Rot - How Increasing Input Tokens Impacts LLM Performance (July 2025)
- Liu et al.: Lost in the Middle - How Language Models Use Long Contexts (TACL 2024)
- OpenRouter State of AI 2025
- Where Do Your Claude Code Tokens Actually Go? (dev.to)
- Dataiku: Single-Agent vs Multi-Agent Systems (Cornell study)
- Multi-Agent LLM Orchestration for Incident Response (arxiv 2511.15755)
- Why Do Multi-Agent LLM Systems Fail? (arxiv 2503.13657)
- Difficulty-Aware Agent Orchestration (arxiv 2509.11079)

---

## 3. First Principles Analysis

### The Core Distinction: Heuristic vs Specification Content

| Property | Heuristic Guidance | Deterministic Specification |
|----------|---|---|
| Example | "ensure alignment between artifacts" | OWASP 3x3 risk matrix lookup table |
| Compressible? | Yes — condense to principles | No — the table IS the content |
| Cost of omission | Suboptimal judgment | **Incorrect output** |
| Agents | PM, architect, team-lead | orchestrator, STRIDE agents |

### Orchestrator Content Breakdown

| Content Type | ~Lines | Compressible? |
|---|---|---|
| Metadata + agent roster | 40 | No (reference data) |
| Output format specification (7 sections + SARIF) | 580 | No (schema definition) |
| Phase 1: Format detection + DFD classification | 260 | Partially |
| Phase 2: STRIDE-per-Element + AI dispatch rules | 270 | No (deterministic rules) |
| Phase 3: Risk validation + correlation | 200 | No (algorithm specification) |
| Phase 4: Coverage matrix + risk summary | 200 | No (computation rules) |
| SARIF generation (mapping, fingerprints, taxonomies) | 500 | Partially (extract to reference) |
| Phase 5-6 dispatch + opt-out | 120 | Somewhat |
| Error handling + validation checklist | 170 | Extract to reference |
| Verbose prose (redundant narration) | 200 | Delete |

**~1,400 lines are irreducible specification. ~600 lines are compressible or extractable.**

### Why Splitting Into Phase-Agents HURTS

The orchestrator phases are a sequential pipeline where each phase consumes the previous phase's output:
- Phase 1 → component inventory → Phase 2
- Phase 2 → dispatch table → Phase 3
- Phase 3 → findings + correlation groups → Phase 4
- Phase 4 → validated findings → SARIF generation

Splitting into separate agents means passing the FULL accumulated state at each handoff. Net token cost INCREASES because data is transmitted twice (agent prompt + passed input). The STRIDE/AI threat agents work as split agents because they are STATELESS.

### Why Reference Extraction HELPS

Content consulted only at specific pipeline points can live in separate files loaded on-demand:
- SARIF spec (~490 lines): loaded at Phase 4 completion only
- Validation checklist (~80 lines): loaded at pipeline end only
- Error templates (~130 lines): loaded on error only

This reduces always-loaded context without adding orchestration overhead.

---

## 4. Recommended Strategy

### Agents Needing Work

| Agent | Current | Target | Approach |
|-------|---------|--------|----------|
| orchestrator.md | 2,085 | ~1,100-1,200 | Extract SARIF, validation, errors to reference docs; condense prose |
| threat-report.md | 801 | ~300-400 | Extract output templates, examples to reference docs |
| threat-infographic.md | 592 | ~300-400 | Extract Gemini API spec, error handling to reference docs |

### Agents Already Well-Sized (No Changes)

All 11 threat agents (108-196 lines each): spoofing, tampering, repudiation, info-disclosure, denial-of-service, privilege-escalation, prompt-injection, data-poisoning, model-theft, agent-autonomy, tool-abuse.

### Extraction Targets for Orchestrator

| Extract To Reference Doc | ~Lines Saved | When Loaded |
|--------------------------|-------------|-------------|
| SARIF generation specification | 490 | Phase 4 completion |
| Validation checklist | 80 | Pipeline end |
| Error handling templates | 130 | On error |
| Verbose prose deletion | 200 | Never (remove) |
| **Total reduction** | **~900** | |

### The Meta-Principle

> The 150-300 line target is correct for agents that provide GUIDANCE.
> It should not be applied mechanically to agents that provide SPECIFICATION.
> The goal is maximizing the ratio of specification content to prose content
> in the model's context window.
