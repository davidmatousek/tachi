# Research: LLM Agent Prompt Sizing and Reference Extraction Patterns

> **Date**: 2026-03-25
> **Researcher**: web-researcher
> **Purpose**: Inform specification for refactoring oversized AI agents
> **Companion**: See also `docs/research/agent-sizing-analysis.md` for tachi-specific sizing data

---

## Context

The tachi project contains agents ranging from 108 lines (well-sized) to 2,085 lines (7x over the project's 300-line ceiling). Before specifying a refactoring approach, we need evidence-based answers to four questions:

1. What are recommended maximum sizes for system prompts / agent instructions?
2. What does current research say about LLM attention degradation in long prompts?
3. What patterns exist for managing large instruction sets?
4. What does Anthropic specifically recommend for Claude Code agent structuring?

---

## 1. Prompt Sizing Best Practices (2025-2026)

### No Universal Token Threshold Exists

The research community has not converged on a single "maximum system prompt size." Instead, findings cluster around several practical boundaries.

**Reasoning degradation onset (~3,000 tokens)**:
Research identified degradation in LLM reasoning performance at approximately 3,000 tokens, well below context window maximums. This represents a threshold where the model begins losing focus on core instructions, not a hard cliff but a performance gradient. (Source: MLOps Community prompt bloat analysis)

**Practical instruction window (150-500 words / ~200-700 tokens)**:
For moderately complex tasks, optimal prompt length typically falls between 150 and 300 words. Beyond the 500-word threshold, diminishing returns and prompt bloat begin to degrade performance. This applies to task-specific instructions, not reference data or specification content. (Source: MLOps Community)

**Safe context utilization (70-80% of window)**:
As a general rule, staying within 70-80% of the total context window capacity prevents accuracy drops. For Claude's 200K context window, this means ~140K-160K tokens total (prompt + conversation + output). (Source: DEV Community analysis)

**Production benchmarks for comparison**:

| System | Approximate Size | Notes |
|--------|-----------------|-------|
| Claude Code system prompt | ~14,328 tokens | Production agent, loaded every invocation |
| Claude 3.7 full conversational prompt | ~24,000 tokens | Includes safety, tools, personality |
| Average LLM prompt (2025 industry) | ~5,400 tokens | Tripled since 2023 |
| Boris Cherny CLAUDE.md recommendation | <100 lines (~2,500 tokens) | Per-file, eagerly loaded |
| tachi orchestrator.md | ~28,000 tokens | 2x the Claude Code benchmark |

(Sources: OpenRouter State of AI 2025, Piebald-AI claude-code-system-prompts, agent-sizing-analysis.md)

### Anthropic's Position

Anthropic does not publish a specific token limit for system prompts. Their guidance is qualitative:

- "Minimal does not necessarily mean short; you still need to give the agent sufficient information."
- Start with "a minimal prompt with the best model available" and iteratively add instructions based on failure modes.
- Context is "a precious, finite resource" -- performance shows "reduced precision for information retrieval and long-range reasoning" at longer context lengths, described as "a performance gradient rather than a hard cliff."

(Source: Anthropic Engineering, "Effective context engineering for AI agents")

### Claude Code Documentation Position

Anthropic's Claude Code best practices documentation is more direct:

- "Most best practices are based on one constraint: Claude's context window fills up fast, and performance degrades as it fills."
- On CLAUDE.md files: "Keep it concise. For each line, ask: 'Would removing this cause Claude to make mistakes?' If not, cut it. Bloated CLAUDE.md files cause Claude to ignore your actual instructions!"
- "If Claude keeps doing something you don't want despite having a rule against it, the file is probably too long and the rule is getting lost."
- Anti-pattern identified: "The over-specified CLAUDE.md. If your CLAUDE.md is too long, Claude ignores half of it because important rules get lost in the noise."

(Source: Claude Code Docs, "Best Practices for Claude Code")

### Synthesis: Sizing Recommendations

| Content Type | Recommended Range | Rationale |
|-------------|-------------------|-----------|
| Heuristic guidance (PM, architect, review agents) | 150-300 lines / ~2,000-4,000 tokens | Standard instruction-following territory |
| Specification-heavy agents (orchestrators, generators) | 800-1,200 lines / ~10,000-15,000 tokens | Irreducible specification content; use reference extraction for the rest |
| Always-loaded context (CLAUDE.md, rules) | <100 lines per file / <2,500 tokens | Loaded every session; bloat compounds |
| Reference documents (loaded on-demand) | No hard limit | Consumed in isolation at specific pipeline points |

---

## 2. "Lost in the Middle" Effect

### The Foundational Paper

**Liu et al. (2024), "Lost in the Middle: How Language Models Use Long Contexts"**, published in Transactions of the Association for Computational Linguistics, is the seminal work. Key findings:

- Performance follows a **U-shaped curve**: models perform best when relevant information is at the beginning or end of input context, and significantly worse when it appears in the middle.
- **30%+ accuracy drop** measured on multi-document question answering when the answer document moved from position 1 to position 10 in a 20-document context.
- Effect persists across both standard and explicitly long-context models.
- The pattern mirrors the human cognitive "serial position effect" (primacy and recency bias).

(Source: Liu et al., arXiv:2307.03172, published TACL 2024)

### The Problem Persists in 2025-2026

Despite larger context windows and architectural improvements:

- **Chroma "Context Rot" study (July 2025)**: Tested 18 state-of-the-art models including Claude Opus 4, Sonnet 4, GPT-4.1, Gemini 2.5 Pro. Adding full conversation history (~113K tokens) dropped accuracy by 30% compared to a focused ~300-token version. Three compounding mechanisms identified: lost-in-the-middle effect, attention dilution, and distractor interference.
- **Recency bias**: Transformer models weight recent tokens more heavily, meaning critical information from early in a long prompt gets undervalued. A 10,000-token prompt might effectively operate on just the last 2,000 tokens for decision-making.

(Sources: Chroma blog, PromptLayer analysis)

### The "Identification Without Exclusion" Problem

A particularly relevant finding for agent design: LLMs can often identify irrelevant details within a prompt but struggle to ignore them during response generation. Even when the model recognizes certain parts of the input as unimportant, those irrelevant details still influence the output. This means adding "just in case" content to agent prompts actively degrades performance -- it is not neutral overhead.

(Source: MLOps Community, "The Impact of Prompt Bloat on LLM Output Quality")

### Instruction Dilution

Long or noisy instructions create "instruction dilution" -- the more instructions present, the less weight any individual instruction receives. This is distinct from the lost-in-the-middle effect (which is about position) and represents a volume problem. The practical implication: an agent with 50 rules will follow each one less reliably than an agent with 15 rules, even if all 50 rules are well-written.

(Source: Medium, "Why Long System Prompts Hurt Context Windows")

### Practical Implications for Agent Design

1. **Position matters**: Place the most critical behavioral instructions at the very beginning and very end of agent definitions. Middle sections should contain reference data that is looked up, not behavioral rules that must be followed.
2. **Volume matters independently of position**: Reducing total instruction count improves compliance with remaining instructions.
3. **Irrelevant content is actively harmful**: Content that "might be useful" degrades performance on content that is definitely needed.
4. **The problem is not solved by bigger context windows**: 2025 models with 1M+ token windows still exhibit these effects.

---

## 3. Context Engineering Patterns

### Anthropic's Four-Bucket Framework

Anthropic's engineering team categorizes context management into four strategies. This is the most authoritative framework for Claude-based agent design.

**Write**: Save context outside the context window for later retrieval. Example: Anthropic's multi-agent researcher has the LeadResearcher save its plan to a Memory store. The plan persists but does not consume context window space until needed.

**Select**: Pull relevant context into the window at the right moment. This is the "just-in-time retrieval" pattern. Instead of pre-loading all data, agents maintain lightweight identifiers (file paths, stored queries, web links) and retrieve data autonomously when needed.

**Compress**: Retain only the tokens required for the current task. Compaction (summarizing a conversation nearing context limits and restarting with the summary) is the first lever. Anthropic warns against overly aggressive compaction that risks "losing subtle context whose importance emerges later."

**Isolate**: Split context across sub-agents. Each subagent "might explore extensively, using tens of thousands of tokens or more, but returns only a condensed, distilled summary of its work (often 1,000-2,000 tokens)." This is the pattern tachi already uses for STRIDE/AI threat agents.

Performance result: Combining all four techniques, Anthropic's multi-agent system outperformed a single Claude Opus 4 agent by 90.2% on breadth-first research tasks.

(Source: Anthropic Engineering, "Effective context engineering for AI agents")

### Pattern 1: Just-in-Time Retrieval (Select)

**What it is**: Rather than pre-loading all reference material into the agent prompt, store references as file paths or identifiers and load them on-demand using tool calls (Read, WebFetch, etc.).

**When to use**: Content that is only needed at specific pipeline stages. Example: SARIF generation specification needed only at Phase 4, validation checklists needed only at pipeline end.

**Implementation in Claude Code**: Agents can use the Read tool to load reference documents at the appropriate workflow step. The agent prompt contains a file path reference and a rule like "At Phase 4 completion, read `/path/to/sarif-spec.md` before generating SARIF output."

**Trade-off**: Adds one tool call per reference load. Negligible latency cost compared to the context quality improvement from removing thousands of tokens from the always-loaded prompt.

**Evidence**: RAG-MCP research (May 2025) showed that dynamically retrieving only relevant tool descriptions (rather than loading all) cut prompt tokens by over 50% and more than tripled tool selection accuracy (43.13% vs 13.62% baseline).

(Sources: Anthropic Engineering; Gao et al., arXiv:2505.03275)

### Pattern 2: Modular Prompt Composition

**What it is**: Decompose a monolithic agent prompt into a core instruction file plus loadable modules. The core file contains behavioral rules and workflow structure. Modules contain specification content, examples, templates, and reference data.

**When to use**: Agents that combine behavioral guidance with large volumes of reference specification (orchestrators, generators, report builders).

**Implementation in Claude Code**: The `@path/to/import` syntax in CLAUDE.md files allows importing additional files. For agents, the Skills system (`skills` frontmatter field) allows preloading specific skill content into a subagent's context at startup.

**Trade-off**: Requires clear documentation of which modules load when. Adds architectural complexity but dramatically improves signal-to-noise ratio in the always-loaded prompt.

(Source: Claude Code Docs, "Best Practices"; Claude Code Docs, "Create custom subagents")

### Pattern 3: Reference Extraction

**What it is**: A specific application of just-in-time retrieval where specification content (schemas, templates, lookup tables, examples) is extracted from an agent prompt into standalone reference documents. The agent retains a pointer ("read X when doing Y") but not the content itself.

**When to use**: Content that is deterministic (not heuristic), used at a specific pipeline stage (not throughout), and large enough to materially affect prompt size.

**Extraction decision framework**:

| Question | If Yes | If No |
|----------|--------|-------|
| Is this content used at every step? | Keep inline | Candidate for extraction |
| Would the agent produce wrong output without it? | Keep inline or load at start | Extract with on-demand load |
| Is this content >50 lines? | Strong extraction candidate | Marginal benefit |
| Is this a lookup table or schema? | Extract to reference doc | Probably heuristic, keep inline |

**Evidence**: A well-structured 16K-token prompt with retrieval-augmented generation outperformed a monolithic 128K-token prompt in both accuracy and relevance.

(Source: PromptLayer, "Disadvantage of Long Prompt for LLM")

### Pattern 4: Sub-Agent Isolation (Isolate)

**What it is**: Delegate focused tasks to sub-agents that run in their own context windows. Each sub-agent loads only the context relevant to its specific task.

**When to use**: Tasks that are stateless (do not depend on accumulated pipeline state), tasks that produce large intermediate output, tasks that require specialized expertise.

**Implementation in Claude Code**: Subagents defined in `.claude/agents/` with YAML frontmatter. Each gets its own context window, custom tool access, and independent permissions. Key constraint: subagents cannot spawn other subagents.

**Anti-pattern**: Splitting a sequential pipeline into phase-agents. When phases consume the previous phase's output, splitting requires passing the FULL accumulated state at each handoff. Net token cost increases because data is transmitted twice (agent prompt + passed input).

**When NOT to use**: Sequential pipelines where each phase needs the full accumulated state from prior phases (like tachi's orchestrator Phase 1-4 pipeline).

(Sources: Claude Code Docs, "Create custom subagents"; agent-sizing-analysis.md)

### Pattern 5: Prompt Compression

**What it is**: Automated reduction of prompt content while preserving semantic meaning. Ranges from simple summarization to sophisticated token-level compression.

**Tools available**:
- **LLMLingua / LLMLingua-2** (Microsoft): Up to 20x compression with minimal quality loss
- **ScaleDown**: Scans prompts to identify and remove irrelevant context
- **DSPy**: Automates optimization via few-shot example generation
- **PCToolkit**: Unified framework integrating five compression methods

**When to use**: Runtime prompt optimization for dynamic content. Less applicable to static agent definitions where manual editing achieves better results.

**Trade-off**: Compression is lossy. For specification content (schemas, lookup tables), lossy compression risks producing incorrect outputs.

(Sources: NAACL 2025, "Prompt Compression for Large Language Models: A Survey"; Microsoft LLMLingua, arXiv:2310.05736)

---

## 4. Anthropic Claude Code Agent Patterns

### Official Subagent Design Guidance

From Claude Code documentation, the recommended approach for agent design:

**Design focused subagents**: "Each subagent should excel at one specific task." The description field is critical -- Claude uses it to decide when to delegate.

**Limit tool access**: "Grant only necessary permissions for security and focus." Use `tools` (allowlist) or `disallowedTools` (denylist) to restrict capabilities.

**Use skills for domain knowledge**: "CLAUDE.md is loaded every session, so only include things that apply broadly. For domain knowledge or workflows that are only relevant sometimes, use skills instead. Claude loads them on demand without bloating every conversation."

**Preload skills into subagents**: The `skills` frontmatter field injects skill content into a subagent's context at startup, giving domain knowledge without requiring discovery and loading during execution.

(Source: Claude Code Docs, "Create custom subagents")

### CLAUDE.md Anti-Bloat Guidance

Anthropic is explicit about the risks of oversized instruction files:

- "For each line, ask: 'Would removing this cause Claude to make mistakes?' If not, cut it."
- "Bloated CLAUDE.md files cause Claude to ignore your actual instructions!"
- "If Claude keeps doing something you don't want despite having a rule against it, the file is probably too long and the rule is getting lost."
- "If Claude asks you questions that are answered in CLAUDE.md, the phrasing might be ambiguous."
- "Treat CLAUDE.md like code: review it when things go wrong, prune it regularly, and test changes by observing whether Claude's behavior actually shifts."

(Source: Claude Code Docs, "Best Practices for Claude Code")

### Subagent Context Architecture

Key architectural properties from official documentation:

1. **Subagents receive only their system prompt** (plus basic environment details like working directory), NOT the full Claude Code system prompt.
2. **The only channel from parent to subagent is the Agent tool's prompt string** -- include any file paths, error messages, or decisions the subagent needs directly in that prompt.
3. **Subagents cannot spawn other subagents** -- prevents infinite nesting.
4. **Sub-agent compaction**: Auto-compaction triggers at approximately 95% capacity. Can be tuned via `CLAUDE_AUTOCOMPACT_PCT_OVERRIDE`.

(Source: Claude Code Docs, "Create custom subagents")

### The Skills System as Reference Extraction Mechanism

Claude Code's Skills system is architecturally aligned with the reference extraction pattern:

- Skills are "folders of instructions, scripts, and resources that Claude can dynamically discover and load."
- Each Skill is defined in a `SKILL.md` file with optional bundled files under `/scripts`, `/references`, and `/assets`.
- Skills can be preloaded into subagents via the `skills` frontmatter field.
- Skills load on demand, not every session.

This means reference documents extracted from oversized agents can be structured as skills or as plain files loaded via Read tool calls, depending on whether they need the skill discovery mechanism or are always loaded at predictable pipeline stages.

(Source: Anthropic, "The Complete Guide to Building Skills for Claude"; Claude Code Docs)

---

## Comparative Analysis

| Criteria | Keep Inline | Reference Extraction | Sub-Agent Split | Skill Extraction |
|----------|-------------|---------------------|-----------------|------------------|
| **Best for** | Behavioral rules, workflow structure | Schemas, templates, lookup tables | Stateless parallel tasks | Reusable domain knowledge |
| **Context cost** | Always loaded | On-demand (1 tool call) | Isolated window | On-demand or preloaded |
| **Pipeline state** | Full access | Full access (loaded into same window) | Must be passed explicitly | Full access |
| **Maintenance** | Single file | Multiple files, clear ownership | Multiple agents, dispatch logic | Skill directory structure |
| **Risk** | Bloat, instruction dilution | Forgotten references, stale docs | State passing overhead, doubled tokens | Over-fragmentation |
| **tachi orchestrator fit** | Core workflow (Phases 1-4) | SARIF spec, validation, errors | NOT recommended (sequential pipeline) | Possibly for shared patterns |

---

## Recommendation

**Recommended approach**: Reference Extraction for specification-heavy agents, with the following priorities:

1. **Orchestrator (2,085 lines)**: Extract SARIF generation spec (~490 lines), validation checklist (~80 lines), and error templates (~130 lines) to reference documents loaded via Read tool at specific pipeline stages. Delete ~200 lines of verbose prose. Target: ~1,100-1,200 lines.

2. **Threat-report (801 lines)**: Extract output templates and extended examples to reference documents. Target: ~300-400 lines.

3. **Threat-infographic (592 lines)**: Extract Gemini API specification and error handling to reference documents. Target: ~300-400 lines.

4. **All 11 threat agents (108-196 lines)**: No changes needed. Already well within best-practice boundaries.

**Do NOT split the orchestrator into phase-agents**. The sequential pipeline architecture means phase-splitting increases net token cost due to state passing overhead.

**Alternative scenario**: If future testing reveals that the orchestrator's ~1,100-line core still causes instruction-following issues, consider restructuring using the Claude Code `skills` frontmatter to preload specific specification content at agent startup rather than embedding it inline.

**Further research needed**:
- Empirical testing of instruction-following quality at the 1,100-line level versus 300-line level for specification-heavy prompts
- Whether Claude 4.6's improved system prompt responsiveness reduces the need for verbose specification
- Evaluation of the Skills system as a reference extraction mechanism for non-reusable, agent-specific content

---

## Sources

### Tier 1 (Official Documentation)
- [Anthropic: Effective context engineering for AI agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)
- [Claude Code Docs: Best Practices for Claude Code](https://code.claude.com/docs/en/best-practices)
- [Claude Code Docs: Create custom subagents](https://code.claude.com/docs/en/sub-agents)
- [Anthropic: The Complete Guide to Building Skills for Claude](https://resources.anthropic.com/hubfs/The-Complete-Guide-to-Building-Skill-for-Claude.pdf)
- [Anthropic: Prompting best practices](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices)

### Tier 1 (Peer-Reviewed Research)
- [Liu et al. (2024): Lost in the Middle: How Language Models Use Long Contexts (TACL)](https://aclanthology.org/2024.tacl-1.9/)
- [Gao et al. (2025): RAG-MCP: Mitigating Prompt Bloat in LLM Tool Selection (arXiv:2505.03275)](https://arxiv.org/abs/2505.03275)
- [NAACL 2025: Prompt Compression for Large Language Models: A Survey](https://aclanthology.org/2025.naacl-long.368/)
- [Microsoft LLMLingua: Compressing Prompts for Accelerated Inference (arXiv:2310.05736)](https://arxiv.org/abs/2310.05736)

### Tier 2 (Community Expertise)
- [MLOps Community: The Impact of Prompt Bloat on LLM Output Quality](https://mlops.community/the-impact-of-prompt-bloat-on-llm-output-quality/)
- [PromptLayer: Disadvantage of Long Prompt for LLM](https://blog.promptlayer.com/disadvantage-of-long-prompt-for-llm/)
- [Winder.AI: LLM Prompt Best Practices for Large Context Windows](https://winder.ai/llm-prompt-best-practices-large-context-windows/)
- [DEV Community: Prompt Length vs. Context Window](https://dev.to/superorange0707/prompt-length-vs-context-window-the-real-limits-behind-llm-performance-3h20)
- [Morph: Context Engineering: Why More Tokens Makes Agents Worse](https://www.morphllm.com/context-engineering)
- [Medium: Why Long System Prompts Hurt Context Windows](https://medium.com/data-science-collective/why-long-system-prompts-hurt-context-windows-and-how-to-fix-it-7a3696e1cdf9)
- [LangChain: Context Engineering for Agents](https://blog.langchain.com/context-engineering-for-agents/)
- [Piebald-AI: claude-code-system-prompts (GitHub)](https://github.com/Piebald-AI/claude-code-system-prompts)

### Tier 2 (Curated Guides)
- [7 Claude Code best practices for 2026](https://www.eesel.ai/blog/claude-code-best-practices)
- [Claude Agent Skills: A First Principles Deep Dive](https://leehanchung.github.io/blogs/2025/10/26/claude-skills-deep-dive/)
- [Redis: LLM Token Optimization 2026](https://redis.io/blog/llm-token-optimization-speed-up-apps/)

### Internal
- [tachi: agent-sizing-analysis.md](docs/research/agent-sizing-analysis.md) -- companion sizing inventory and first-principles analysis
