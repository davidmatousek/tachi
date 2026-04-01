# Research Summary: Agent Context Optimization (Feature 078)

## Knowledge Base Findings

### PAT-016: On-Demand Skill Extraction for Agent Complexity Management (Score: 9/10)
- **Source**: Feature 075 retrospective
- **Key lesson**: Extract domain knowledge (schemas, lookup tables, dispatch rules, scoring formulas) into skills with tiered loading (SKILL.md + references/ subdirectory). Agents retain workflow logic only.
- **Evidence**: Feature 075 reduced orchestrator 2,000→769, risk-scorer 1,419→994, control-analyzer 1,367→935 — identical pipeline output confirmed.
- **Applicability**: Directly applies — Feature 078 continues this extraction to reach tighter caps (500/300 vs current 1,000/800).

### PAT-017: Output Template Parity Requires Dedicated Validation Tasks (Score: 8/10)
- **Source**: Feature 074 retrospective
- **Key lesson**: When modifying schemas with downstream templates, add explicit template parity checks at each phase checkpoint — not just final validation.
- **Applicability**: Moderate — Feature 078 moves output templates to files but doesn't change their content. Template parity checks still relevant when verifying moved templates match originals.

## Codebase Analysis

### Current Agent Line Counts (wc -l)
| Agent | Lines | Tier | Cap | Status |
|-------|-------|------|-----|--------|
| orchestrator | 1,286 | Methodology | 500 (new) | Exceeds |
| risk-scorer | 1,093 | Methodology | 500 (new) | Exceeds |
| control-analyzer | 973 | Methodology | 500 (new) | Exceeds |
| threat-report | 800 | Report | 300 (new) | Exceeds |
| threat-infographic | 775 | Report | 300 (new) | Exceeds |
| report-assembler | 654 | Report | 300 (new) | Exceeds |
| agent-autonomy | 200 | Leaf | 200 (new) | At cap |
| model-theft | 187 | Leaf | 200 | Compliant |
| tool-abuse | 184 | Leaf | 200 | Compliant |
| data-poisoning | 170 | Leaf | 200 | Compliant |
| prompt-injection | 166 | Leaf | 200 | Compliant |
| denial-of-service | 140 | Leaf | 200 | Compliant |
| privilege-escalation | 135 | Leaf | 200 | Compliant |
| info-disclosure | 127 | Leaf | 200 | Compliant |
| tampering | 125 | Leaf | 200 | Compliant |
| repudiation | 123 | Leaf | 200 | Compliant |
| spoofing | 112 | Leaf | 200 | Compliant |

**Total**: 17 agents, 7,503 lines. 6 agents need restructuring. 0/17 have `model:` field.

### Existing Skill Infrastructure
Three skills already extracted (Feature 075):
- **tachi-orchestration**: SKILL.md (204 lines) + 4 reference files (1,423 lines)
- **tachi-risk-scoring**: SKILL.md (102 lines) + 3 reference files (525 lines)
- **tachi-control-analysis**: SKILL.md (74 lines) + 3 reference files (537 lines)

### Existing YAML Schema Files (schemas/)
9 schema files establishing conventions: finding.yaml, risk-scoring.yaml, compensating-controls.yaml, input.yaml, output.yaml, report.yaml, security-report.yaml, infographic.yaml, coverage-checklists.yaml. All use versioned YAML with enum types, defaults, and conditional required fields.

### Loading Pattern
All agents use explicit Read tool loading (not `skills:` frontmatter). Pattern: navigation table in SKILL.md + MANDATORY Read instructions at each workflow branch point. No agents use eager loading.

## Architecture Constraints

### Relevant ADRs
- **ADR-002 (Prompt Segmentation)**: Segmented monolithic skill (25,800 tokens) into core + on-demand references. 78% persistent context reduction. Establishes the reference segmentation pattern.
- **ADR-010 (Minimal Return)**: Subagent returns capped at 10 lines / ~200 tokens with file-based offloading.
- **ADR-018 (Baseline-Aware Pipeline)**: Deterministic fingerprint correlation — fingerprint algorithm, delta classification, and carry-forward rules are deterministic data suitable for YAML extraction.

### Best Practices Document (_TACHI_AGENT_BEST_PRACTICES.md, 253 lines)
- Current tier caps: Leaf 300, Report 800, Methodology 1,000
- New caps proposed: Leaf 200, Report 300, Methodology 500
- 8-item quality checklist for agent review
- Recommends data-top ordering (schemas/tables before workflow instructions)
- Compliance table exists but shows post-075 counts (stale — actual counts now higher due to Feature 074 additions)

### Agent Ordering Convention (Anthropic-Recommended)
1. Role identity (1-2 sentences)
2. Domain data (tables, schemas) — at top
3. Workflow steps — numbered procedure
4. Output format
5. Constraints — at bottom

## Industry Research

### Context Engineering Best Practices (2026)
- **Anthropic**: Contexts >100k tokens degrade reasoning quality. Stay under 40% context utilization.
- **JetBrains Research**: Observation masking (simpler) outperforms summarization (costlier) for context reduction. Simple strategies halve costs versus no management.
- **LogRocket**: Relevance-first approach — every token should serve a clear purpose.
- **Dynamic tool selection**: Models struggle past ~30 tools. Loading tools on-demand improves selection accuracy by 44%.
- **System prompt optimization**: Balance specificity (guides behavior) with flexibility (strong heuristics). Avoid over-specification.

Sources:
- [Anthropic: Effective Context Engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)
- [JetBrains: Efficient Context Management](https://blog.jetbrains.com/research/2025/12/efficient-context-management/)
- [LogRocket: LLM Context Problem 2026](https://blog.logrocket.com/llm-context-problem-strategies-2026)
- [Comet: Context Engineering Best Practices](https://www.comet.com/site/blog/context-engineering/)

## Recommendations for Spec

1. **Follow PAT-016 pattern exactly** — extract domain knowledge into skills with tiered loading. This is a proven pattern with regression-tested results from Feature 075.
2. **Prototype risk-scorer first** — it has the most structured extractable content (CVSS vectors, severity bands, scoring dimensions) and validates the deterministic YAML pattern before committing to all 6 agents.
3. **Use existing YAML conventions** from schemas/ directory for deterministic data files (versioning, enums, defaults, conditional required fields).
4. **Shared references for deduplicated content** — severity bands and STRIDE categories are used by multiple agents. Shared files reduce maintenance burden.
5. **Preserve explicit Read tool loading** — do not switch to `skills:` frontmatter (eager loading defeats the purpose).
6. **Add template parity checks** per PAT-017 when moving output templates to files.
7. **Model field: start with `sonnet` for all agents** per PRD architect recommendation, escalate to `opus` only if regression testing shows quality issues.
8. **Best practices document update** must include accurate wc -l counts and corrected research findings (200-line limit is MEMORY.md only, not agents).
