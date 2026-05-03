# Stack Packs

Stack Packs are pluggable, opinionated modules that encode stack-specific conventions, security patterns, agent personas, and project scaffolding into AOD. Each pack turns implementation agents into specialists in a specific technology stack.

## Pack Directory Structure

Every pack lives in its own directory under `stacks/`. Packs are self-contained — no cross-references between packs, no references from pack files to core `.claude/` or `.aod/` files.

```
stacks/{pack-name}/
├── STACK.md              # Convention contract (required, ≤500 lines)
├── agents/               # Persona supplements (required, ≤100 lines each)
│   ├── frontend-developer.md
│   ├── senior-backend-engineer.md
│   ├── security-analyst.md
│   ├── tester.md
│   ├── code-reviewer.md
│   ├── devops.md
│   ├── ux-ui-designer.md
│   └── debugger.md
├── rules/                # Stack-specific coding rules (required)
│   ├── conventions.md
│   └── security.md
├── scaffold/             # Project template files (optional)
│   └── [canonical file structure]
└── skills/               # Stack-specific skills (optional)
    └── [skill directories]
```

**Naming**: Pack directory names use kebab-case, lowercase (e.g., `nextjs-supabase`, `swiftui-cloudkit`). Persona files match agent names from `.claude/agents/`.

## Agent Tier Classification

Agents are classified into three tiers that determine how packs interact with them:

### Core (never modified by packs)

These agents are stack-agnostic. Pack activation has zero effect on their behavior.

| Agent | Role |
|-------|------|
| product-manager | Defines What & Why — scope, requirements, user value |
| architect | Defines How — technical decisions, architecture |
| team-lead | Defines When & Who — timeline, agent assignments |
| orchestrator | Lifecycle stage sequencing and governance gates |
| web-researcher | Research and information gathering |

### Specialized (persona supplements loaded from active pack)

These agents receive a persona supplement that layers stack-specific conventions, anti-patterns, and guardrails onto their core expertise.

| Agent | Supplement Focus |
|-------|-----------------|
| frontend-developer | UI framework patterns, component conventions, styling |
| senior-backend-engineer | Data access, server patterns, API conventions |
| security-analyst | OWASP mappings, auth patterns, data protection |
| tester | Test framework, coverage strategy, mocking patterns |
| code-reviewer | Code quality rules, pattern enforcement |
| devops | Deployment targets, CI/CD, environment management |

### Hybrid (universal methodology + stack-specific tooling)

These agents use universal methodologies but receive stack-specific tooling context.

| Agent | Supplement Focus |
|-------|-----------------|
| ux-ui-designer | Design system, component library, CSS approach |
| debugger | Stack-specific debugging tools, common failure modes |

## STACK.md Convention Contract

STACK.md is the central document of each pack. It is loaded as agent context on every invocation when a pack is active.

### Required Sections (in order)

| # | Section | Purpose | Guidelines |
|---|---------|---------|------------|
| 1 | **Summary** | Target audience, stack, use case, deployment, philosophy | Include `Target`, `Stack`, `Use Case`, `Deployment`, `Philosophy` fields |
| 2 | **Architecture Pattern** | Rendering strategy, data flow, state management, component model | Describe the application architecture decisively |
| 3 | **File Structure** | Canonical directory layout with annotations | Every directory has a purpose comment |
| 4 | **Naming Conventions** | Casing rules per file type | Cover components, utilities, routes, tests, types, configs |
| 5 | **Security Patterns** | Auth, validation, data access, middleware | Use imperative ALWAYS/NEVER format — zero exceptions |
| 6 | **Coding Standards** | Always-use patterns and never-use anti-patterns | Deterministic choices that eliminate ad-hoc decisions |
| 7 | **Testing Conventions** | Framework, location, naming, coverage, mocking | Define what to test at each level (unit, integration, E2E) |

Section 7 must also declare a machine-readable **stack pack test contract block** — see [`docs/stacks/TEST_COMMAND_CONTRACT.md`](../docs/stacks/TEST_COMMAND_CONTRACT.md) for the canonical reference on its schema, canonical examples, and lint exit codes.

### Optional Sections (after required)

- **Design Principles** — Philosophy behind technology choices
- **Deployment** — CI/CD pipeline, hosting setup, environment management
- **Upgrade Paths** — Documented alternatives for swappable components
- **Dependencies** — Package list with version constraints

### Validation Rules

| Rule | Constraint |
|------|-----------|
| Total length | ≤ 500 lines |
| Required sections | All 7 present, in specified order |
| Content style | Imperative rules, not tutorials |
| Technology references | Specific versions, not "latest" |
| Anti-patterns | Sourced from real failures, not hypotheticals |

## Persona Supplement Format

Persona supplements are compact documents (≤100 lines) that layer stack expertise onto specialized and hybrid agents. They encode conventions and anti-patterns — NOT framework tutorials.

### Required Format

```markdown
# {Agent Name} — {Pack Name} Supplement

## Stack Context
[What this agent needs to know about the stack — tools, versions, key patterns]

## Conventions
[Stack-specific patterns this agent MUST follow — imperative, deterministic]

## Anti-Patterns
[What this agent MUST NOT do with this stack — sourced from real failures]

## Guardrails
[Boundaries and constraints specific to this stack]
```

### Writing Guidelines

- **DO** encode deterministic decisions: "ALWAYS use Server Components for data fetching"
- **DO** list specific anti-patterns: "NEVER use CSS modules — use Tailwind utilities"
- **DO** reference stack-specific tooling: "Use Prisma query events for debugging"
- **DO NOT** explain what the framework is — agents already know from training data
- **DO NOT** include tutorials or getting-started content
- **DO NOT** repeat content from STACK.md — supplements are additive, role-specific context
- **DO NOT** exceed 100 lines — brevity forces precision

## Content Sourcing Process

Pack content MUST be grounded in community consensus, not individual opinion.

### Three-Tier Process

1. **Curate** — Gather 5-10 community convention files (CLAUDE.md, .cursorrules, etc.) for the target stack. Extract patterns that appear in the majority of sources. Discard outliers.

2. **Research** — Map OWASP Top 10 guidelines to stack-specific security mitigations. Study idiomatic open-source projects for naming conventions, file structure, and testing patterns. Reference official documentation for recommended patterns.

3. **Iterate** — Test the pack on real projects. Audit agent output for convention gaps (places where agents make ad-hoc decisions instead of following pack rules). Strengthen weak patterns and add missing anti-patterns.

### Quality Signals

- Conventions appear in 3+ independent community sources → strong signal
- Pattern is in official documentation → strong signal
- Pattern is only in one blog post → weak signal, needs more evidence
- Anti-pattern caused real bugs in production → include with high confidence
- Anti-pattern is theoretical → include only if sourced from multiple reports

## Context Budget

Pack content is loaded into agent context at runtime. Staying within budget is critical for agent performance.

| Component | Max Lines | Loaded When |
|-----------|-----------|-------------|
| STACK.md | 500 | Every agent invocation (if pack active) |
| Persona supplement | 100 | Specialized/hybrid agent invocations only |
| Stack rules (all files combined) | 200 | Every agent invocation (via rules discovery) |
| **Total pack overhead** | **800** | **Maximum per invocation** |

This budget is *incremental* — additive to the base agent context and existing governance rules. Only one persona supplement loads per agent invocation (the one matching the dispatched agent).

## Commands

| Command | Description |
|---------|-------------|
| `/aod.stack list` | Show available packs and active status |
| `/aod.stack use {pack}` | Activate a pack (copies rules, writes state) |
| `/aod.stack remove` | Deactivate the active pack (cleans all state) |
| `/aod.stack scaffold` | Create project structure from active pack's scaffold |

## Activation Mechanics

When `/aod.stack use {pack}` runs:

1. Pack rules (`stacks/{pack}/rules/*.md`) are **copied** to `.claude/rules/stack/`
2. A persona-loader rule is generated in `.claude/rules/stack/` instructing specialized/hybrid agents to read their persona supplement
3. Activation state is written to `.aod/stack-active.json`
4. During `/aod.build`, the build command reads `stack-active.json` and injects persona supplement read instructions into dispatched agent prompts

Core agent files in `.claude/agents/` are **never modified** by activation. Governance behavior is **identical** with or without an active pack.

## Core-Agent Supplement Pattern

Some domain-specific packs (e.g., `knowledge-system`) provide **informational supplements** for Core-tier agents (product-manager, architect, team-lead). These supplements add domain awareness context that Core agents can reference during reviews — they do NOT modify governance methodology, decision-making authority, or sign-off criteria.

### How It Works

- The pack's `agents/` directory includes supplement files named after Core agents (e.g., `agents/product-manager.md`)
- Each Core-agent supplement opens with an explicit **informational overlay** disclaimer stating it does not override the agent's core behavior
- The supplement follows the standard 4-section format (Stack Context, Conventions, Anti-Patterns, Guardrails)
- The Guardrails section reinforces the agent's existing authority boundaries

### What Core-Agent Supplements Provide

| Agent | Domain Awareness |
|-------|-----------------|
| product-manager | Domain-specific product concerns (e.g., command inventory completeness, audience analysis) |
| architect | Domain-specific architecture concerns (e.g., orchestration patterns, context loading design) |
| team-lead | Domain-specific scheduling concerns (e.g., content dependency ordering, parallel build opportunities) |

### What Core-Agent Supplements Do NOT Change

- Review methodology or checklists
- Decision-making authority or scope ownership
- Sign-off criteria or governance gates
- Core agent files in `.claude/agents/` (never modified)

### When to Use This Pattern

Use Core-agent supplements when a domain introduces concepts that Core agents would otherwise miss during reviews. For example, a knowledge-system pack adds awareness of orchestration design so the PM can validate command inventory coverage — a concern absent from standard product reviews.

Do NOT use this pattern to:
- Override how Core agents make decisions
- Add new sign-off requirements
- Modify governance workflows
- Change the Triad authority model
