# Agent Best Practices

<!-- Reference: Feature 003 - Agent Refactoring -->
<!-- Version: 2.0.0 | Created: 2026-01-31 -->

This document provides comprehensive guidance for designing, customizing, and maintaining agents in Agentic Oriented Development Kit.

---

## Table of Contents

1. [Core Principles](#1-core-principles)
2. [Standard Agent Structure](#2-standard-agent-structure)
3. [Metadata Specification](#3-metadata-specification)
4. [Quality Checklist](#4-quality-checklist)
5. [Preservation-First Enhancement](#5-preservation-first-enhancement)
6. [Template Variables](#6-template-variables)
7. [Common Patterns](#7-common-patterns)
8. [Examples](#8-examples)

---

## 1. Core Principles

All agents in Agentic Oriented Development Kit follow eleven core principles. Principles 1-8 are foundational. Principles 9-11 are inspired by the [12-Factor Agents](https://github.com/humanlayer/12-factor-agents) methodology and target production resilience.

### Principle 1: Conciseness

**Target**: 150-250 lines optimal, 300 lines maximum (with documented justification)

**Why**: Large agent files cause slow context loading and high token consumption. Concise agents load faster and respond more quickly.

**How to achieve**:
- Remove redundant explanations
- Replace verbose paragraphs with bullet points
- Move code examples to skill references
- Eliminate obvious or self-explanatory content

**Example**:
```markdown
# Bad (verbose)
When you need to review the architecture of a system, you should first
carefully examine all the components and understand how they interact
with each other. This involves looking at the database layer, the API
layer, the frontend components, and any external services.

# Good (concise)
Architecture review steps:
- Examine component interactions (database, API, frontend, external services)
- Identify integration points
- Validate against system requirements
```

### Principle 2: Structure

**Target**: All agents use identical 8-section format

**Why**: Consistent structure enables predictable navigation, easier customization, and automated validation. Template adopters know exactly where to find information.

**Required Sections** (in order):
1. Core Mission
2. Role Definition
3. When to Use
4. Workflow Steps
5. Quality Standards
6. Triad Governance
7. Tools & Skills
8. Success Criteria

**See**: [Section 2: Standard Agent Structure](#2-standard-agent-structure) for detailed template.

### Principle 3: Boundaries

**Target**: Every agent explicitly documents what it does NOT do

**Why**: Clear scope limits prevent confusion, reduce overlap between agents, and help template adopters select the right agent for each task.

**How to document**:
```yaml
boundaries:
  does_not_handle:
    - Code implementation (use senior-backend-engineer or frontend-developer)
    - Security audits (use security-analyst)
    - Testing strategy (use tester)
```

**Example boundary statements**:
- architect: "Does not write production code - delegates to engineering agents"
- product-manager: "Does not make technical decisions - defers to architect"
- debugger: "Does not implement fixes - identifies root cause only"

### Principle 4: Context Efficiency

**Target**: Reference skills instead of embedding code; minimize inline examples

**Why**: Embedded code examples inflate agent size without adding value. Skills provide reusable patterns that can be updated independently.

**Preferred approach**:
```markdown
# Bad (embedded code)
When creating a FastAPI endpoint, use this pattern:
[50 lines of code example]

# Good (skill reference)
For API endpoint patterns, invoke skill: `api-patterns`
Reference: .claude/skills/api-patterns/
```

**When inline examples are acceptable**:
- Brief format examples (3-5 lines max)
- Markdown/YAML structure templates
- Output format specifications

### Principle 5: Versioning

**Target**: All agents have semantic version numbers and changelog entries

**Why**: Version tracking enables change history, rollback capability, and clear communication about agent evolution.

**Format**: MAJOR.MINOR.PATCH
- MAJOR: Breaking changes to agent behavior or structure
- MINOR: New capabilities added (backward compatible)
- PATCH: Bug fixes, documentation improvements

**Changelog format**:
```yaml
changelog:
  - version: 2.0.0
    date: 2026-01-31
    changes:
      - Refactored per best practices
      - Applied 8-section structure
      - Reduced from 1,026 to 250 lines (77% reduction)
  - version: 1.0.0
    date: 2025-06-15
    changes:
      - Initial agent creation
```

### Principle 6: Triad Integration

**Target**: Every agent documents its governance participation clearly

**Why**: The SDLC Triad (PM, Architect, Team-Lead) governs quality gates. Agents must clearly state their role in sign-offs and when they defer to other roles.

**Governance documentation**:
```yaml
triad_governance:
  participates_in:
    - plan.md sign-off (architect review)
    - Technical decisions (architecture authority)
  veto_authority:
    - Technology stack choices
    - System design patterns
  defers_to:
    - product-manager: Product scope decisions
    - team-lead: Timeline and resource allocation
```

### Principle 7: Skill Delegation

**Target**: Delegate specialized work to skills; agents orchestrate, skills execute

**Why**: Skills are reusable, testable, and can be updated independently. Agents should focus on decision-making and workflow, not detailed execution.

**When to delegate**:
- Code generation patterns
- Testing strategies
- Deployment procedures
- Research methodologies

**Agent vs Skill responsibilities**:
| Agent | Skill |
|-------|-------|
| Decides what to build | Provides code patterns |
| Orchestrates workflow | Executes specific tasks |
| Makes judgment calls | Follows defined procedures |
| Validates outcomes | Generates artifacts |

### Principle 8: Preservation-First Enhancement

**Target**: When refactoring, inventory capabilities BEFORE making changes

**Why**: Aggressive refactoring can inadvertently remove critical capabilities. Preservation-first ensures all functionality is retained.

**Process summary**:
1. Read and document all current capabilities
2. Categorize content (Keep/Condense/Reference/Remove)
3. Apply changes systematically
4. Validate all capabilities preserved

**See**: [Section 5: Preservation-First Enhancement](#5-preservation-first-enhancement) for full 11-step process.

### Principle 9: Error Compaction

**Target**: When an agent encounters errors, summarize failure context concisely before retrying or escalating

**Why**: Raw error traces consume excessive context tokens. Agents that blindly append full stack traces degrade their own reasoning quality on subsequent turns. Compact error summaries preserve context budget for productive work. *(Ref: 12-Factor Agents, Factor 9)*

**How to achieve**:
- Extract the actionable signal: what failed, why, what was tried
- Discard redundant stack frames and verbose boilerplate
- Format as a structured summary (cause → attempted fix → outcome)
- When retrying, pass the compact summary — not the raw error — into context

**Example**:
```markdown
# Bad (raw dump in context)
[48 lines of stack trace pasted verbatim]

# Good (compact summary)
Error: DB connection timeout after 30s (host: db-prod-1, pool exhausted)
Attempted: Connection pool increase from 10→25 — still failing
Root cause: Upstream migration lock held by deploy process
```

### Principle 10: State Transparency

**Target**: Agents must be explicit about what state they read, produce, and depend on

**Why**: Implicit state creates hidden coupling between agents and makes pause/resume unreliable. When an agent's inputs and outputs are transparent, any agent (or human) can pick up where it left off. *(Ref: 12-Factor Agents, Factors 5 and 12)*

**How to achieve**:
- Document state dependencies in the agent's **Workflow Steps** section (what files/artifacts are read)
- Document state outputs (what files/artifacts are written or modified)
- Prefer `.aod/` artifacts as the single source of truth — not in-memory assumptions
- Treat each agent invocation as a pure transform: read state → do work → write state

**State contract format**:
```yaml
state:
  reads:
    - .aod/spec.md        # Feature requirements
    - .aod/plan.md         # Technical design
  writes:
    - .aod/tasks.md        # Generated work items
    - .aod/results/team-lead.md  # Review output
```

### Principle 11: Session Resilience

**Target**: Agents should produce durable artifacts at each meaningful step, not just at the end

**Why**: Long-running agent workflows can be interrupted by context limits, network issues, or user pauses. If intermediate progress lives only in the conversation, it's lost. Durable checkpoints enable the `/continue` handoff pattern to work reliably. *(Ref: 12-Factor Agents, Factor 6)*

**How to achieve**:
- Write artifacts to disk at each workflow phase, not just at completion
- Use `.aod/results/` or `.aod/` for intermediate outputs
- Prefer append-safe formats (markdown with clear section boundaries)
- When resuming, read the last written artifact to determine where to continue — don't rely on conversation history

**Anti-pattern**:
```markdown
# Bad: all work in memory, single write at end
1. Research → (in memory)
2. Draft spec → (in memory)
3. Review → (in memory)
4. Write spec.md ← only durable artifact

# Good: checkpoint at each phase
1. Research → write specs/NNN/research.md
2. Draft spec → write .aod/spec.md (draft)
3. Review → write .aod/results/pm-review.md
4. Finalize → update .aod/spec.md (approved)
```

---

## 2. Standard Agent Structure

All agents use this 8-section template. Copy this structure when creating new agents or refactoring existing ones.

### Template

```markdown
---
version: 1.0.0
changelog:
  - version: 1.0.0
    date: YYYY-MM-DD
    changes:
      - Initial creation per best practices
boundaries:
  does_not_handle:
    - [List what this agent does NOT do]
    - [Help template adopters understand scope limits]
triad_governance:
  participates_in:
    - [List Triad workflow stages]
  veto_authority:
    - [Domains where agent has veto power]
  defers_to:
    - [Other agents/roles for specific decisions]
---

# Agent Name

<!-- One-line description of agent purpose -->

---

## 1. Core Mission

[2-3 sentences describing what this agent does and why it exists]

**Primary Objective**: [Single clear statement]

---

## 2. Role Definition

**Position in Workflow**: [Where agent fits in SDLC]

**Expertise Areas**:
- [Area 1]
- [Area 2]
- [Area 3]

**Collaboration**:
- Works with: [List agents this one collaborates with]
- Hands off to: [List agents that receive work from this one]
- Receives from: [List agents that hand work to this one]

---

## 3. When to Use

**Invoke this agent when**:
- [Trigger condition 1]
- [Trigger condition 2]
- [Trigger condition 3]

**Trigger phrases**:
- "[Example user request 1]"
- "[Example user request 2]"
- "[Example user request 3]"

**Do NOT invoke when**:
- [Anti-pattern 1 - use X agent instead]
- [Anti-pattern 2 - use Y agent instead]

---

## 4. Workflow Steps

### Standard Workflow

1. **[Step Name]**
   - [Action 1]
   - [Action 2]
   - Output: [What this step produces]

2. **[Step Name]**
   - [Action 1]
   - [Action 2]
   - Output: [What this step produces]

3. **[Step Name]**
   - [Action 1]
   - [Action 2]
   - Output: [What this step produces]

### Alternative Flows

**[Scenario Name]**: [Brief description of when this applies]
- [Modified steps]

---

## 5. Quality Standards

### Acceptance Criteria

All outputs must meet:
- [ ] [Criterion 1]
- [ ] [Criterion 2]
- [ ] [Criterion 3]

### Output Format

[Describe expected output format, structure, or template]

### Validation Rules

- [Rule 1]
- [Rule 2]
- [Rule 3]

---

## 6. Triad Governance

### Sign-off Participation

| Artifact | Role | Authority |
|----------|------|-----------|
| [artifact] | [role] | [APPROVE/REVIEW/INFORM] |

### Veto Authority

This agent can veto:
- [Domain 1]: [Reason]
- [Domain 2]: [Reason]

### Deference

This agent defers to:
- **[Role]**: For [decision type]
- **[Role]**: For [decision type]

---

## 7. Tools & Skills

### Available Tools

- **[Tool Name]**: [Purpose]
- **[Tool Name]**: [Purpose]

### Skills to Invoke

| Skill | When to Use |
|-------|-------------|
| [skill-name] | [Trigger condition] |
| [skill-name] | [Trigger condition] |

### Integration Points

- [External system 1]: [How agent interacts]
- [External system 2]: [How agent interacts]

---

## 8. Success Criteria

### Task Completion

A task is complete when:
- [ ] [Completion criterion 1]
- [ ] [Completion criterion 2]
- [ ] [Completion criterion 3]

### Performance Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| [Metric] | [Target] | [How measured] |

### Anti-Patterns

Avoid:
- [Anti-pattern 1]
- [Anti-pattern 2]
- [Anti-pattern 3]
```

### Section Descriptions

| Section | Purpose | Typical Length |
|---------|---------|----------------|
| Core Mission | What agent does | 3-5 lines |
| Role Definition | Position in workflow | 10-15 lines |
| When to Use | Trigger conditions | 10-15 lines |
| Workflow Steps | Step-by-step process | 30-50 lines |
| Quality Standards | Acceptance criteria | 15-20 lines |
| Triad Governance | Sign-off participation | 15-20 lines |
| Tools & Skills | Available capabilities | 10-15 lines |
| Success Criteria | Completion measures | 10-15 lines |

---

## 3. Metadata Specification

All agents require YAML frontmatter with these fields.

### Required Fields

```yaml
---
version: MAJOR.MINOR.PATCH     # Semantic version
changelog:                      # Version history
  - version: X.Y.Z
    date: YYYY-MM-DD
    changes:
      - Change description 1
      - Change description 2
boundaries:                     # Scope limits
  does_not_handle:
    - Excluded responsibility 1
    - Excluded responsibility 2
triad_governance:               # Governance participation
  participates_in:
    - Workflow stage 1
  veto_authority:
    - Domain 1
  defers_to:
    - Role: Decision type
---
```

### Field Specifications

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| version | string | Yes | Semantic version (MAJOR.MINOR.PATCH) |
| changelog | array | Yes | List of version entries with dates and changes |
| boundaries.does_not_handle | array | Yes | Explicit scope exclusions |
| triad_governance.participates_in | array | Yes | Governance stages this agent participates in |
| triad_governance.veto_authority | array | Conditional | Domains where agent can block decisions |
| triad_governance.defers_to | array | Conditional | Roles agent defers to for specific decisions |

### Version Numbering

| Change Type | Version Increment | Example |
|-------------|-------------------|---------|
| Breaking change | MAJOR (X.0.0) | Restructure workflow |
| New capability | MINOR (x.Y.0) | Add new skill integration |
| Bug fix/docs | PATCH (x.y.Z) | Fix typo, clarify wording |

---

## 4. Quality Checklist

Use this checklist to validate any agent. Criteria 1-8 must all pass. Criteria 9-11 are recommended for production-grade agents.

### Checklist Template

```markdown
## Agent Quality Checklist

**Agent**: [agent-name.md]
**Evaluator**: [name/agent]
**Date**: [YYYY-MM-DD]

### Criteria (8/8 required + 3 recommended)

| # | Criterion | Pass | Notes |
|---|-----------|------|-------|
| 1 | **Conciseness**: ≤300 lines (≤250 preferred) | [ ] | Lines: ___ |
| 2 | **Structure**: Uses 8-section template | [ ] | Missing: ___ |
| 3 | **Boundaries**: Scope limits documented | [ ] | |
| 4 | **Context Efficiency**: Skill refs, minimal code | [ ] | Inline code lines: ___ |
| 5 | **Versioning**: Has version + changelog | [ ] | Current version: ___ |
| 6 | **Triad Integration**: Governance documented | [ ] | |
| 7 | **Skill Delegation**: Appropriate delegation | [ ] | Skills used: ___ |
| 8 | **Preservation**: All capabilities intact | [ ] | Tested: ___ |
| 9 | **Error Compaction**: Compact error summaries | [ ] | _Recommended_ |
| 10 | **State Transparency**: I/O state documented | [ ] | _Recommended_ |
| 11 | **Session Resilience**: Checkpoints at phases | [ ] | _Recommended_ |

### Result

- [ ] **PASS** (8/8 required met)
- [ ] **PASS+** (11/11 met — production-grade)
- [ ] **FAIL** (Criteria failed: ___)

### Notes
[Any exceptions, justifications, or observations]
```

### Criterion Details

**1. Conciseness**
- Count total lines including YAML frontmatter
- 250 lines is optimal; 300 is maximum
- Exceeding 300 requires documented justification in changelog

**2. Structure**
- All 8 sections present in correct order
- Section headers match template exactly
- YAML frontmatter at top of file

**3. Boundaries**
- `does_not_handle` array has 2+ entries
- Exclusions are specific (not vague like "other things")
- Points to correct alternative agents

**4. Context Efficiency**
- No inline code blocks >10 lines
- Complex patterns reference skills
- Examples are format-only (not implementation)

**5. Versioning**
- Version follows MAJOR.MINOR.PATCH
- Changelog has at least one entry
- Date format is YYYY-MM-DD

**6. Triad Integration**
- `participates_in` lists relevant workflow stages
- Veto authority clearly defined (if applicable)
- Deference relationships documented

**7. Skill Delegation**
- Skills section lists available skills
- Agent focuses on orchestration, not execution
- No duplicated skill content in agent

**8. Preservation**
- All original capabilities still present
- Tested with representative tasks
- No functionality removed without justification

---

## 5. Preservation-First Enhancement

When refactoring agents, follow this 11-step process to ensure no capabilities are lost.

### The 11-Step Process

#### Phase A: Inventory

**Step 1: Read Original**
- Open the current agent file
- Read completely without modification
- Note overall structure and length

**Step 2: Extract Capabilities**
- List every function/capability the agent provides
- Document each workflow the agent supports
- Identify all integration points

**Step 3: Document Dependencies**
- List skills the agent invokes
- List other agents it collaborates with
- Note external tools or systems

#### Phase B: Categorize

**Step 4: Create Content Categories**

| Category | Action | Criteria |
|----------|--------|----------|
| **Keep** | Retain as-is | Core functionality, essential workflows |
| **Condense** | Shorten | Verbose explanations, redundant text |
| **Reference** | Move to skill | Code examples, detailed procedures |
| **Remove** | Delete | Redundant, obvious, or outdated content |

**Step 5: Assign Each Section**
- Walk through agent section by section
- Assign category to each paragraph/list
- Document reasoning for removals

#### Phase C: Transform

**Step 6: Apply Structure Template**
- Copy 8-section template
- Map existing content to new sections
- Fill in required metadata

**Step 7: Condense Verbose Content**
- Convert paragraphs to bullet points
- Remove obvious explanations
- Tighten language (active voice, fewer words)

**Step 8: Create Skill References**
- Move code examples to skills (if not exists, note for future)
- Replace inline code with skill invocation
- Keep only format/structure examples

**Step 9: Add Metadata**
- Create YAML frontmatter
- Set version to 2.0.0 (major refactor)
- Document changes in changelog
- Define boundaries

#### Phase D: Validate

**Step 10: Run Quality Checklist**
- Complete 8-criterion checklist
- Address any failures
- Document any exceptions

**Step 11: Test with Representative Tasks**
- Run 3-5 typical tasks the agent handles
- Verify all capabilities work
- Compare output quality to original

### Quick Reference Card

```
PRESERVATION-FIRST REFACTORING

BEFORE CHANGES:
1. Read entire agent
2. List all capabilities
3. Document all dependencies

CATEGORIZE:
4. Keep / Condense / Reference / Remove
5. Assign each section

TRANSFORM:
6. Apply 8-section template
7. Condense verbose text
8. Move code to skills
9. Add YAML metadata

VALIDATE:
10. Run quality checklist (8/8)
11. Test representative tasks
```

---

## 6. Template Variables

Template variables enable customization for different tech stacks while maintaining consistent methodology.

### When to Use Template Variables

| Use Template Variable | Use Concrete Value |
|-----------------------|-------------------|
| Technology choices (framework, database) | Methodology (Triad, 5 Whys) |
| Cloud provider specifics | Agentic Oriented Development Kit processes |
| Tech stack configurations | Governance workflows |
| Environment-specific values | Quality standards |

### Standard Template Variables

| Variable | Example Values | Usage |
|----------|----------------|-------|
| `{{FRONTEND_FRAMEWORK}}` | React, Vue, Angular | Frontend agent tech references |
| `{{BACKEND_FRAMEWORK}}` | FastAPI, Express, Django | Backend agent tech references |
| `{{DATABASE}}` | PostgreSQL, MongoDB, MySQL | Data layer references |
| `Not yet defined` | GCP, AWS, Azure | Infrastructure references |
| `{{TEST_FRAMEWORK}}` | pytest, Jest, Vitest | Testing references |
| `{{CI_PLATFORM}}` | GitHub Actions, GitLab CI | DevOps references |

### Examples

**Correct usage**:
```markdown
# Technology (use variable)
Deploy to Not yet defined using the configured CI/CD pipeline.
Use {{FRONTEND_FRAMEWORK}} component patterns.

# Methodology (use concrete)
Follow the Triad governance process for sign-offs.
Apply 5 Whys methodology for root cause analysis.
```

**Incorrect usage**:
```markdown
# Wrong: Variable for methodology
Follow the {{GOVERNANCE_PROCESS}} for sign-offs.

# Wrong: Concrete for tech choice
Deploy to Google Cloud Platform using Cloud Run.
```

---

## 7. Common Patterns

Reusable patterns for common agent scenarios.

### Governance Sign-off Pattern

```markdown
## Triad Governance

### Sign-off Participation

| Artifact | This Agent's Role | Authority |
|----------|-------------------|-----------|
| spec.md | Reviewer | APPROVE required |
| plan.md | Primary reviewer | APPROVE required |
| tasks.md | Informed | INFORM only |

### Sign-off Workflow

1. Receive artifact for review
2. Evaluate against quality criteria
3. Provide verdict: APPROVED or CHANGES REQUESTED
4. Document reasoning in sign-off notes
```

### Handoff Pattern

```markdown
## Handoff Protocol

### Receiving Work

When receiving from [source-agent]:
- Expect: [artifact description]
- Validate: [validation criteria]
- Proceed if: [conditions for proceeding]

### Delivering Work

When handing to [target-agent]:
- Provide: [artifact description]
- Include: [required context]
- Notify: [communication method]
```

### Return Format Pattern

Add this section to agents invoked as subagents (via the Agent tool) to prevent context overflow. Full details are offloaded to a results file; the parent receives only a minimal status summary.

**When to apply**: Governance reviewers, quality checkers, diagnostic agents — any agent whose full output would exhaust the parent's context window.

**Template** — insert before `## 8. Success Criteria`, replace `{agent-name}` with the agent's filename (e.g., `product-manager`):

```markdown
## Return Format (STRICT)

When invoked as a **subagent** (via the Agent tool), you MUST:

1. Write your full review to `.aod/results/{agent-name}.md` (overwrite, do not append)
2. Return to the caller ONLY:
    STATUS: [APPROVED | APPROVED_WITH_CONCERNS | CHANGES_REQUESTED | BLOCKED]
    ITEMS: [N findings/concerns]
    DETAILS: .aod/results/{agent-name}.md

Maximum return: 10 lines. No review rationale, code snippets, or file contents.
Subagent-only restriction — provide full output when invoked directly by the user.
```

**Examples by agent type**:
- **Governance reviewer** (product-manager, architect, team-lead): APPROVED/CHANGES_REQUESTED
- **Explorer** (debugger, security-analyst): pass/fail + findings count
- **Tester**: pass/fail + test count

**Custom agent guidance**: See CLAUDE.md "Subagent Return Policy" for project-wide context.

---

### Error Escalation Pattern

```markdown
## Error Handling

### Escalation Levels

1. **Self-resolve**: Minor issues, retry with different approach
2. **Peer consult**: Invoke related agent for input
3. **User escalation**: Block on critical decision, request clarification

### When to Escalate

| Situation | Action |
|-----------|--------|
| Missing requirements | Escalate to product-manager |
| Technical conflict | Escalate to architect |
| Resource constraint | Escalate to team-lead |
```

---

## 8. Examples

### Example: Minimal Agent (150 lines)

Agents that primarily orchestrate or have narrow scope can achieve 150 lines.

**Characteristics**:
- Single primary workflow
- Few integration points
- Limited governance participation
- Delegates most work to skills

**Agents in this category**: web-researcher, frontend-developer

### Example: Standard Agent (200-250 lines)

Most agents fall in this range with balanced responsibilities.

**Characteristics**:
- 2-3 workflows
- Multiple integration points
- Clear governance role
- Mix of orchestration and light execution

**Agents in this category**: tester, devops, security-analyst

### Example: Complex Agent (250-300 lines)

Agents with significant governance or orchestration responsibilities.

**Characteristics**:
- Multiple complex workflows
- Many integration points
- Heavy governance participation
- Coordinates other agents

**Agents in this category**: architect, product-manager, orchestrator

### Example: Agent Requiring Split

When an agent exceeds 300 lines despite best efforts, consider splitting by concern.

**Indicators**:
- Two distinct responsibility areas
- Users invoke for very different purposes
- Separate concerns could work independently

**Split pattern** (team-lead example from Feature 003):
```
team-lead.md (1,346 lines - BEFORE)
         │
         ├── Governance concerns
         │   └── team-lead.md (210 lines - AFTER)
         │
         └── Orchestration concerns
             └── orchestrator.md (255 lines - NEW)

Result: 84% reduction in team-lead.md, clear separation of concerns
```

---

## 9. Lessons Learned (Feature 003)

Key insights from the agent refactoring effort (Feature 003, 2026-01-31):

### What Worked Well

1. **Preservation-First Approach**: Inventorying capabilities before refactoring prevented functionality loss. All 12 original agents retained their capabilities.

2. **8-Section Template**: Consistent structure made agents predictable and easier to navigate. 100% adoption achieved across all 13 agents.

3. **Split Decision for team-lead**: Separating governance (team-lead) from execution (orchestrator) resolved scope creep and reduced complexity. Combined 1,346 lines became 465 lines (210 + 255).

4. **Parallel Quality Audits**: Running structure audits, metadata audits, and line count checks in parallel accelerated validation.

### Metrics Achieved

| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| Total Lines | 7,885 | 3,287 | 58% reduction |
| Largest Agent | 1,346 | 291 | 78% reduction |
| Agents Over 300 Lines | 4 | 0 | 100% compliance |
| Average Lines | 657 | 253 | 61% reduction |

### Recommendations for Future Refactoring

1. **Create backup branch first**: `003-agent-backup` saved original state for rollback capability.
2. **Batch similar agents**: Refactoring agents in groups (e.g., all Quality agents) identified shared patterns.
3. **Update cross-references last**: Wave 6.3 (cross-reference validation) caught 8+ files needing updates.
4. **Test with representative tasks**: Each agent should be validated with 2-3 typical use cases post-refactoring.

---

## Quick Reference

### Line Targets

| Category | Target | Maximum |
|----------|--------|---------|
| Simple agent | 150 | 200 |
| Standard agent | 200 | 250 |
| Complex agent | 250 | 300 |

### Checklist Summary

1. Conciseness: ≤300 lines
2. Structure: 8 sections
3. Boundaries: Scope documented
4. Context efficiency: Skill refs
5. Versioning: Semantic version
6. Triad: Governance role
7. Delegation: Skills used
8. Preservation: Capabilities intact
9. Error compaction: Compact summaries *(recommended)*
10. State transparency: I/O documented *(recommended)*
11. Session resilience: Phase checkpoints *(recommended)*

### Template Variable Summary

- Tech choices: `{{VARIABLE}}`
- Methodology: Concrete values
- Agentic Oriented Development Kit: Always concrete

### Return Format Pattern

For agents invoked as subagents: write full output to `.aod/results/{agent-name}.md`, return only STATUS / ITEMS / DETAILS (≤10 lines). See Section 7 Common Patterns → Return Format Pattern for full template.

---

**End of Agent Best Practices**
