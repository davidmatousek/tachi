# Tachi Agent Best Practices

<!-- Version: 1.0.0 | Created: 2026-03-31 -->
<!-- Aligned with Anthropic Claude 4.6 agent design recommendations -->

Best practices for tachi threat analysis agents. These extend (not replace) the AOD `_AGENT_BEST_PRACTICES.md` with tachi-specific guidance, Anthropic alignment, and the skill extraction pattern for methodology-heavy agents.

---

## Table of Contents

1. [Agent Tiers](#1-agent-tiers)
2. [Hard Caps](#2-hard-caps)
3. [Anthropic Alignment (Claude 4.6)](#3-anthropic-alignment-claude-46)
4. [Skill Extraction Pattern](#4-skill-extraction-pattern)
5. [Current Compliance](#5-current-compliance)
6. [Quality Checklist (Tachi)](#6-quality-checklist-tachi)

---

## 1. Agent Tiers

Tachi agents are classified into three tiers based on their role in the pipeline. Each tier has different line budgets reflecting the amount of domain knowledge the agent needs at invocation time.

| Tier | Role | Target | Hard Cap | Agents |
|------|------|--------|----------|--------|
| **Leaf** | Single-concern threat analysis | 100-200 | 300 | spoofing, tampering, repudiation, info-disclosure, denial-of-service, privilege-escalation, prompt-injection, data-poisoning, model-theft, agent-autonomy, tool-abuse |
| **Report** | Output generation, formatting | 400-600 | 800 | report-assembler, threat-report, threat-infographic |
| **Methodology** | Multi-phase pipeline with domain schemas | 500-800 | 1,000 | orchestrator, risk-scorer, control-analyzer |

**Why tiers differ from AOD agents:** AOD agents (PM, architect, team-lead) orchestrate governance workflows — their domain knowledge lives in the codebase they review. Tachi agents carry domain knowledge (STRIDE methodology, scoring dimensions, control detection patterns) that must be in the prompt for the agent to function. The tiered caps reflect this difference while still enforcing discipline.

---

## 2. Hard Caps

**1,000 lines is the absolute maximum for any tachi agent definition.**

No exceptions. Agents exceeding 1,000 lines must extract content into skills using the [Skill Extraction Pattern](#4-skill-extraction-pattern).

Why 1,000:
- Every line consumes context window space on every invocation
- Anthropic research shows complex system prompts trigger excessive adaptive thinking in Claude 4.6
- Large prompts dilute attention — the model loses focus on key instructions
- Skills provide progressive disclosure without context cost until needed

---

## 3. Anthropic Alignment (Claude 4.6)

These practices come from Anthropic's published guidance on agent design, prompt engineering, and context engineering. Sources listed at the end of this section.

### 3.1 Instruction Tone

Claude 4.6 is more responsive to system prompts than previous models. Aggressive emphasis causes overtriggering.

```markdown
# Avoid (causes overtriggering in Claude 4.6)
CRITICAL: You MUST ALWAYS use this tool when analyzing threats.
NEVER skip this step under ANY circumstances.

# Prefer (normal language, same compliance)
Use this tool when analyzing threats.
Do not skip this step.
```

Remove `CRITICAL`, `MUST`, `ALWAYS`, `NEVER` patterns unless the instruction genuinely requires emphasis (e.g., security constraints). Use them sparingly — if everything is critical, nothing is.

### 3.2 Progressive Disclosure via Skills

Anthropic's three-level skill loading model:

| Level | What loads | When | Context cost |
|-------|-----------|------|-------------|
| 1 | Skill name + description | Session start | Minimal (~50 tokens) |
| 2 | Full SKILL.md body | When Claude decides the skill applies | Moderate |
| 3 | Linked reference files | On-demand during execution | Only what's needed |

Agent definitions should contain orchestration logic (what to do, in what order). Domain knowledge (scoring schemas, detection patterns, output templates) belongs in skills that load only when needed.

### 3.3 Agent Definition Structure

Anthropic recommends this ordering for agent system prompts:

1. **Role identity** (1-2 sentences) — who the agent is
2. **Domain data** (tables, schemas) — reference material at the top
3. **Workflow steps** ("When invoked:") — numbered procedure
4. **Output format** — structure of expected deliverable
5. **Constraints** — what not to do, boundaries

Long-form data at the top, instructions at the bottom. Anthropic testing shows queries/instructions at the end improve response quality by up to 30%.

### 3.4 Tool Restrictions

Grant only the tools each agent needs. Read-only agents should not have Edit/Write. Research agents should not have Bash unless required.

```yaml
# In agent frontmatter
tools:
  - Read
  - Glob
  - Grep
  - Agent
```

### 3.5 Description Field

The `description` frontmatter field is how Claude decides when to delegate to a subagent. It matters more than the prompt body for correct routing. Write it like a docstring for a junior developer — specific, with examples of when to use and when not to.

### 3.6 Subagent Returns

Anthropic recommends 1,000-2,000 token return summaries from subagents. Tachi's existing Subagent Return Policy (max 15 lines / ~200 tokens) is stricter — keep it. Concise returns protect the parent conversation's context window.

### Sources

- Anthropic: "Building Effective Agents" — six workflow patterns, graduated complexity
- Anthropic: "Effective Context Engineering for AI Agents" — context as precious resource, progressive disclosure
- Anthropic: "Claude 4.6 Best Practices" — instruction tone, overtriggering, adaptive thinking
- Anthropic: "Equipping Agents with Agent Skills" — three-level disclosure, SKILL.md structure
- Anthropic: "Writing Effective Tools for AI Agents" — tool description design, poka-yoke
- Anthropic: "Long Context Prompting Tips" — data-at-top, query-at-bottom ordering

---

## 4. Skill Extraction Pattern

When an agent exceeds its tier cap, extract domain content into skills. The agent definition retains orchestration logic; the skill holds domain knowledge that loads on-demand.

### What to Extract

| Extract into skill | Keep in agent definition |
|--------------------|------------------------|
| Scoring schemas, dimension definitions, weight tables | Scoring workflow steps (parse → score → output) |
| Detection patterns, evidence criteria, control categories | Detection workflow (discover → detect → classify) |
| Output templates, section specifications | Output structure summary (sections list, ordering) |
| STRIDE dispatch rules, correlation matrices | Dispatch workflow (scope → dispatch → assess) |
| CVSS base vectors, severity band definitions | Composite formula and calculation steps |
| Example outputs, sample findings | Validation rules (what makes output correct) |

### Skill File Structure

```
.claude/skills/tachi-{agent-name}/
  SKILL.md              # Metadata + summary (Level 2 — loads when skill is invoked)
  references/
    scoring-schema.md   # Level 3 — loads on-demand
    detection-patterns.md
    output-template.md
```

### How to Reference

In the agent frontmatter:
```yaml
skills:
  - tachi-risk-scoring    # Loads scoring dimensions, CVSS defaults, weight tables
```

In the agent body:
```markdown
## 3. Dimensional Scoring

Load scoring dimensions and CVSS base vectors from the `tachi-risk-scoring` skill.
Apply the composite formula: (CVSS x 0.35) + (Exploitability x 0.30) + ...
```

### Extraction Checklist

Before extracting, verify:
- [ ] Extracted content is referenced by the agent, not duplicated
- [ ] Agent body still makes sense without the extracted content (orchestration is self-contained)
- [ ] Skill SKILL.md has a clear description so the agent knows when to load it
- [ ] No circular dependencies between agent and skill
- [ ] Tested: agent produces same quality output with skill-based loading as with inline content

---

## 5. Current Compliance

Status as of 2026-03-31. Updated post-Feature 075 refactoring (skill extraction + tone audit).

### Leaf Agents (cap: 300)

| Agent | Lines | Status | Notes |
|-------|-------|--------|-------|
| spoofing | 112 | Compliant | +4 (tools: frontmatter added) |
| repudiation | 123 | Compliant | +4 (tools: frontmatter added) |
| tampering | 125 | Compliant | +4 (tools: frontmatter added) |
| info-disclosure | 127 | Compliant | +4 (tools: frontmatter added) |
| privilege-escalation | 135 | Compliant | +4 (tools: frontmatter added) |
| denial-of-service | 140 | Compliant | +4 (tools: frontmatter added) |
| prompt-injection | 166 | Compliant | +4 (tools: frontmatter added) |
| data-poisoning | 170 | Compliant | +4 (tools: frontmatter added) |
| tool-abuse | 184 | Compliant | +4 (tools: frontmatter added) |
| model-theft | 187 | Compliant | +4 (tools: frontmatter added) |
| agent-autonomy | 200 | Compliant | +4 (tools: frontmatter added) |

### Report Agents (cap: 800)

| Agent | Lines | Status | Notes |
|-------|-------|--------|-------|
| report-assembler | 654 | Compliant | +6 (tools: frontmatter added) |
| threat-infographic | 775 | Compliant | +6 (tools: frontmatter added, tone softened) |
| threat-report | 800 | Compliant | -1 trim + tools: added (net 0). At cap. |

### Methodology Agents (cap: 1,000)

| Agent | Lines | Status | Notes |
|-------|-------|--------|-------|
| orchestrator | 769 | Compliant | -1,231 via `tachi-orchestration` skill extraction |
| control-analyzer | 935 | Compliant | -432 via `tachi-control-analysis` skill extraction |
| risk-scorer | 994 | Compliant | -425 via `tachi-risk-scoring` skill extraction |

### Extracted Skills

| Skill Package | Reference Files | Total Lines | Source Agent |
|---------------|----------------|-------------|-------------|
| tachi-orchestration | sarif-specification (498), dispatch-rules (244), output-schemas (498) | 1,240 | orchestrator |
| tachi-risk-scoring | scoring-dimensions (256), cvss-vectors (74), severity-bands (195) | 525 | risk-scorer |
| tachi-control-analysis | control-categories (249), evidence-criteria (117), residual-risk (171) | 537 | control-analyzer |

---

## 6. Quality Checklist (Tachi)

Extends the AOD 8-criterion checklist with tachi-specific criteria.

| # | Criterion | Applies to |
|---|-----------|-----------|
| 1 | **Tier compliance**: Lines within tier hard cap | All |
| 2 | **Skill extraction**: Domain knowledge in skills, not inline (if over target) | Methodology, Report |
| 3 | **Instruction tone**: No aggressive emphasis patterns unless genuinely critical | All |
| 4 | **Tool restrictions**: Only necessary tools granted in frontmatter | All |
| 5 | **Description quality**: Specific enough for correct delegation routing | All |
| 6 | **Data-top ordering**: Schemas/tables before workflow steps, constraints at bottom | Methodology |
| 7 | **Output determinism**: Where possible, scoring and classification use deterministic rules, not LLM judgment | Methodology |
| 8 | **Return format**: Subagent return policy compliance (max 15 lines) | All |

### Validation

Run this check before merging any agent changes:

```bash
# Line count check — flag agents over tier cap
wc -l .claude/agents/tachi/*.md | sort -n

# Aggressive emphasis scan
grep -n -E '(CRITICAL|MUST|ALWAYS|NEVER)' .claude/agents/tachi/*.md
```

---

**End of Tachi Agent Best Practices**
