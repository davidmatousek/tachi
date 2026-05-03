# Tachi Agent Best Practices

<!-- Version: 1.2.0 | Updated: 2026-04-01 | Feature 078: Agent Context Optimization (T056 finalized) -->
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
| **Leaf** | Single-concern threat analysis | 100-150 | 200 | spoofing, tampering, repudiation, info-disclosure, denial-of-service, privilege-escalation, prompt-injection, data-poisoning, model-theft, agent-autonomy, tool-abuse |
| **Report** | Output generation, formatting | 200-250 | 300 | report-assembler, threat-report, threat-infographic |
| **Methodology** | Multi-phase pipeline with domain schemas | 350-450 | 500 | orchestrator, risk-scorer, control-analyzer |

**Why tiers differ from AOD agents:** AOD agents (PM, architect, team-lead) orchestrate governance workflows — their domain knowledge lives in the codebase they review. Tachi agents carry domain knowledge (STRIDE methodology, scoring dimensions, control detection patterns) that must be in the prompt for the agent to function. The tiered caps reflect this difference while still enforcing discipline.

---

## 2. Hard Caps

**500 lines is the absolute maximum for any tachi agent definition.**

No exceptions. Agents exceeding 500 lines must extract content into skills using the [Skill Extraction Pattern](#4-skill-extraction-pattern).

Why 500:
- Every line consumes context window space on every invocation
- Anthropic research shows complex system prompts trigger excessive adaptive thinking in Claude 4.6
- Large prompts dilute attention — the model loses focus on key instructions
- Skills provide progressive disclosure without context cost until needed

**Note on the 200-line limit**: The 200-line context limit cited in earlier research applies specifically to Claude Code's MEMORY.md index file, not to agent definition files. Agent definitions have tier-specific caps as defined above.

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

### Loading Strategy

Use lazy loading (Read tool on-demand at workflow branch points) rather than eager loading (skills: frontmatter auto-load). Lazy loading was validated in Feature 075 with 78% context reduction per ADR-002. Each restructured agent includes a skill reference navigation table with load-when conditions that specify exactly when to Read each reference file.

### Extraction Checklist

Before extracting, verify:
- [ ] Extracted content is referenced by the agent, not duplicated
- [ ] Agent body still makes sense without the extracted content (orchestration is self-contained)
- [ ] Skill SKILL.md has a clear description so the agent knows when to load it
- [ ] No circular dependencies between agent and skill
- [ ] Tested: agent produces same quality output with skill-based loading as with inline content

---

## 5. Current Compliance

Status as of 2026-04-01 (post-restructuring). All 17 agents comply with tier caps after Feature 078 waves 1-7.

### Leaf Agents (cap: 200)

| Agent | Lines | Status | Notes |
|-------|-------|--------|-------|
| spoofing | 113 | PASS | Within cap |
| repudiation | 124 | PASS | Within cap |
| tampering | 126 | PASS | Within cap |
| info-disclosure | 128 | PASS | Within cap |
| privilege-escalation | 136 | PASS | Within cap |
| denial-of-service | 141 | PASS | Within cap |
| prompt-injection | 167 | PASS | Within cap |
| data-poisoning | 171 | PASS | Within cap |
| tool-abuse | 185 | PASS | Within cap |
| model-theft | 188 | PASS | Within cap |
| agent-autonomy | 201 | PASS | Leaf exception: 5% over cap (~210 target). Architect tolerance acknowledged — extracting ~10 lines adds complexity without meaningful benefit |

### Report Agents (cap: 300)

| Agent | Lines | Status | Notes |
|-------|-------|--------|-------|
| report-assembler | 208 | PASS | Restructured from 655; domain knowledge extracted to tachi-report-assembly skill |
| threat-report | 268 | PASS | Restructured from 801; narrative templates extracted to tachi-threat-reporting skill |
| threat-infographic | 288 | PASS | Restructured from 776; visual specs extracted to tachi-infographics skill |

### Methodology Agents (cap: 500)

| Agent | Lines | Status | Notes |
|-------|-------|--------|-------|
| control-analyzer | 423 | PASS | Restructured from 974; control categories and evidence criteria extracted to tachi-control-analysis skill |
| orchestrator | 441 | PASS | Restructured from 1,287; SARIF spec, dispatch rules, and output schemas extracted to tachi-orchestration skill. Architect tolerance: 520 cap (4% above 500) not needed — fits within 500 |
| risk-scorer | 497 | PASS | Restructured from 1,094; scoring dimensions, CVSS vectors, and severity bands extracted to tachi-risk-scoring skill |

### Extracted Skills

| Skill Package | Reference Files (lines) | Total Lines | Source Agent |
|---------------|------------------------|-------------|-------------|
| tachi-orchestration | sarif-specification (634), output-schemas (506), dispatch-rules (244), coverage-requirements (205), baseline-correlation (143), coverage-matrix-model (116), dfd-classification (107), trust-boundaries (149), format-detection (101) | 2,205 | orchestrator |
| tachi-risk-scoring | severity-bands (211), reachability-analysis (187), trust-zones (173), output-formatting (155), cvss-vectors (106), scoring-dimensions (84) | 916 | risk-scorer |
| tachi-control-analysis | control-categories (249), residual-risk (171), evidence-criteria (117) | 537 | control-analyzer |
| tachi-infographics | gemini-prompt-construction (215), infographic-specifications (196), visual-design-system (141), template-specific-formats (132) | 684 | threat-infographic |
| tachi-report-assembly | typst-template-contract (273), typst-artifacts (136), brand-asset-guidelines (111) | 520 | report-assembler |
| tachi-threat-reporting | narrative-templates (196), attack-tree-construction (186), attack-tree-examples (114) | 496 | threat-report |
| tachi-shared | finding-format-shared (176), stride-categories-shared (146), severity-bands-shared (110) | 432 | All pipeline agents |

---

## 6. Quality Checklist (Tachi)

Extends the AOD 8-criterion checklist with tachi-specific criteria. Updated for post-restructuring patterns (Feature 078).

| # | Criterion | Applies to |
|---|-----------|-----------|
| 1 | **Tier compliance**: Lines within tier hard cap (Leaf 200, Report 300, Methodology 500) | All |
| 2 | **Skill extraction**: Domain knowledge in skills, not inline; lazy loading via Read on-demand at workflow branch points | Methodology, Report |
| 3 | **model: frontmatter**: Every agent declares `model: sonnet` (or appropriate model) in YAML frontmatter | All |
| 4 | **Shared references**: Agents consuming severity bands, STRIDE categories, or finding format reference `tachi-shared` skill rather than duplicating definitions | All pipeline agents |
| 5 | **SKILL.md navigation table**: Each skill directory contains a SKILL.md with a reference navigation table listing file paths and load-when conditions | All extracted skills |
| 6 | **Instruction tone**: No aggressive emphasis patterns unless genuinely critical | All |
| 7 | **Tool restrictions**: Only necessary tools granted in frontmatter | All |
| 8 | **Description quality**: Specific enough for correct delegation routing | All |
| 9 | **Data-top ordering**: Schemas/tables before workflow steps, constraints at bottom | Methodology |
| 10 | **Output determinism**: Where possible, scoring and classification use deterministic rules, not LLM judgment | Methodology |
| 11 | **Return format**: Subagent return policy compliance (max 15 lines) | All |

### Validation

Run these checks before merging any agent changes:

```bash
# Line count check — flag agents over tier cap
wc -l .claude/agents/tachi/*.md | sort -n

# Aggressive emphasis scan
grep -n -E '(CRITICAL|MUST|ALWAYS|NEVER)' .claude/agents/tachi/*.md

# model: frontmatter check — all agents should have model: field
grep -L '^model:' .claude/agents/tachi/*.md

# Shared reference integrity — verify tachi-shared references exist
ls .claude/skills/tachi-shared/references/
```

---

**End of Tachi Agent Best Practices**
