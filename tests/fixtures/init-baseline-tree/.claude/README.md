# Claude Agent Infrastructure

This directory contains the complete agent orchestration infrastructure for tachi, including 13 specialized agents, 24 automation skills, 23 slash commands, and 6 design archetypes for streamlined feature development.

## Overview

The infrastructure is organized into four main components:

1. **Agents** (`agents/`) - 13 specialized AI agents for different development roles
2. **Skills** (`skills/`) - 24 reusable automation capabilities
3. **Commands** (`commands/`) - 23 slash commands for workflow automation
4. **Design** (`design/`) - 6 design archetypes for brand identity generation

---

## Agents (`agents/`)

### Core Development Team (7 agents)

| Agent | Role | Primary Responsibilities |
|-------|------|-------------------------|
| **product-manager** | Product Manager | Product specifications, user stories, requirements gathering, stakeholder communication |
| **architect** | Technical Architect | System design, architecture review, technical decision documentation, baseline infrastructure analysis |
| **team-lead** | Development Lead | Governance sign-offs, feasibility validation, capacity management, agent assignments |
| **orchestrator** | Workflow Executor | Multi-agent coordination, parallel wave execution, progress monitoring, task dispatch |
| **senior-backend-engineer** | Backend Developer | API implementation, business logic, database design, server-side code |
| **frontend-developer** | Frontend Developer | UI components, client-side logic, design system implementation |
| **tester** | QA Engineer | BDD tests, integration tests, test coverage, quality assurance |

### Specialized Support Team (6 agents)

| Agent | Role | Primary Responsibilities |
|-------|------|-------------------------|
| **devops** | DevOps Engineer | Infrastructure, deployment, CI/CD, environment management |
| **code-reviewer** | Code Quality | Code review, architecture validation, security review, quality gates |
| **debugger** | Troubleshooter | Root cause analysis, complex debugging, issue resolution |
| **web-researcher** | Research Specialist | Technical research, best practices, library evaluation, documentation analysis |
| **ux-ui-designer** | UX/UI Designer | Design systems, user experience, interface specifications, mockups |
| **security-analyst** | Security Expert | Security analysis, vulnerability assessment, threat modeling, dependency scanning |

### Agent Customization

All agents are **templatized** with the following variables for project-specific customization:

```
tachi          - Your project name (e.g., "my-saas-app")
{{BACKEND_FRAMEWORK}}     - Backend framework (e.g., "Express", "Fastify", "NestJS")
{{FRONTEND_FRAMEWORK}}    - Frontend framework (e.g., "React", "Vue", "Svelte")
{{DATABASE}}              - Database system (e.g., "PostgreSQL", "MySQL", "MongoDB")
{{DATABASE_PROVIDER}}     - Database provider (e.g., "Supabase", "Neon", "AWS RDS")
Not yet defined        - Cloud platform (e.g., "Vercel", "AWS", "Railway")
{{BACKEND_PATH}}          - Backend source path (e.g., "backend/src", "server/src")
{{FRONTEND_PATH}}         - Frontend source path (e.g., "frontend/src", "client/src")
```

**To customize agents for your project:**
1. Search and replace template variables in `.claude/agents/*.md`
2. Update tech stack references to match your choices
3. Adjust file path patterns to match your project structure

---

## Skills (`skills/`)

Skills are reusable automation capabilities that agents can invoke to perform specialized tasks.

### Lifecycle & Orchestration Skills

| Skill | Purpose | When to Use |
|-------|---------|-------------|
| **~aod-plan** *(internal)* | Plan stage orchestrator: chains spec → project-plan → tasks | Invoked automatically — use `/aod.plan` instead |
| **~aod-run** *(internal)* | Full lifecycle orchestrator: chains all 6 stages | Invoked automatically — use `/aod.run` instead |
| **~aod-deliver** *(internal)* | Structured delivery retrospective and feature closure | Invoked automatically — use `/aod.deliver` instead |
| **~aod-status** *(internal)* | Backlog snapshot and lifecycle stage summary | Invoked automatically — use `/aod.status` instead |
| **aod-orchestrate** | Multi-feature wave execution from blueprint output | After `/aod.blueprint`, executing features in priority waves |
| **triad** | Triad governance coordination for sign-off workflows | Internal governance helper for PM/Architect/Team-Lead reviews |

### Product & Planning Skills

| Skill | Purpose | When to Use |
|-------|---------|-------------|
| **~aod-define** *(internal)* | PRD content generation (called by `/aod.define`) | Invoked automatically — use `/aod.define` instead |
| **~aod-discover** *(internal)* | Feature idea capture with ICE scoring and PM validation | Invoked automatically — use `/aod.discover` instead |
| **~aod-score** *(internal)* | Re-score existing idea's ICE rating | Invoked automatically — use `/aod.score` instead |
| **~aod-kickstart** *(internal)* | POC kickstart: transforms project idea into sequenced consumer guide | Invoked automatically — use `/aod.kickstart` instead |
| **~aod-blueprint** *(internal)* | Unified project setup and story generation with deduplication | Invoked automatically — use `/aod.blueprint` instead |
| **~aod-build** | Create implementation checkpoints for long features | Mid-feature progress tracking, wave completion |

### Architecture & Validation Skills

| Skill | Purpose | When to Use |
|-------|---------|-------------|
| **~aod-project-plan** | Validate architectural decisions and consistency | Before finalizing plan.md, after major design changes |
| **~aod-spec** | Validate spec.md, plan.md, tasks.md consistency | Before PRs, after task generation |

### Knowledge Management Skills

| Skill | Purpose | When to Use |
|-------|---------|-------------|
| **kb-create** | Create structured knowledge base articles | Documenting patterns, bugs, architectural decisions |
| **kb-query** | Query knowledge base for similar solutions | Before implementing, when stuck on problems |

### Development Support Skills

| Skill | Purpose | When to Use |
|-------|---------|-------------|
| **~aod-bugfix** | One-shot governed bug fix loop (diagnose → plan → implement → verify → document) | When a bug is reported, error message/stack trace pasted, or fix is needed |
| **root-cause-analyzer** | Perform 5 Whys root cause analysis | Complex bugs, recurring issues, workflow blockers |
| **code-execution-helper** | Execute code for quota checks, API validation | Pre-flight quota checks, resource validation |
| **git-workflow-helper** | Git workflow automation (commits, PRs, branches) | Creating commits, managing branches, PR creation |

### Stack & Design Skills

| Skill | Purpose | When to Use |
|-------|---------|-------------|
| **aod-stack** | Manage stack packs (activate, remove, list, scaffold) | Setting up stack-specific conventions, scaffolding projects |
| **aod-foundation** | Guided post-init workshop (vision + design identity) | After `make init`, establishing product vision and brand identity |

### Security Skills

| Skill | Purpose | When to Use |
|-------|---------|-------------|
| **security** | SAST/SCA security scan — OWASP Top 10 + CVE patterns, audit artifacts, severity gate | Invoked automatically as the Security Scan step (Step 7) of `/aod.build`; run standalone via `/security` for ad-hoc scans |

### Thinking & Analysis Skills

| Skill | Purpose | When to Use |
|-------|---------|-------------|
| **aod-lens** | Apply structured thinking methodologies | Systematic analysis, risk assessment, decision-making |

**Skills are domain-agnostic** and require minimal customization beyond `tachi` substitution.

---

## Commands (`commands/`)

> **Commands vs Skills**: Commands (`.claude/commands/`) are user-invocable via `/command-name`. Skills (`.claude/skills/`) provide reusable automation -- some are user-invocable (e.g., `/aod.foundation`, `/aod.stack`, `/security`), while others prefixed with `~` are internal-only (e.g., `~aod-discover`).

### Triad Commands (Recommended - Automatic Governance)

The **SDLC Triad** ensures Product-Architecture-Engineering alignment with automatic sign-offs:

| Command | Purpose | Auto Sign-offs |
|---------|---------|----------------|
| `/aod.define <topic>` | Create PRD with PM + Architect + Tech-Lead validation | 3-way (PM, Architect, Tech-Lead) |
| `/aod.plan` | Plan stage: chains spec → project-plan → tasks | PM → PM+Architect → Triple |
| `/aod.build` | Execute with architect checkpoints | Architect checkpoints at milestones |
| `/aod.foundation` | Guided workshop — product vision + design identity | — |
| `/aod.deliver {NNN}` | Close feature with parallel doc updates | Automatic documentation |
| `/aod.document` | Code quality review (simplify, docstrings, CHANGELOG) | — |

**Plan sub-commands** (invoked by `/aod.plan`; use individually only if needed):

| Command | Purpose | Auto Sign-offs |
|---------|---------|----------------|
| `/aod.spec` | Create spec.md with PM sign-off | 1-way (PM) |
| `/aod.project-plan` | Create plan.md with PM + Architect sign-off | 2-way (PM, Architect) |
| `/aod.tasks` | Create tasks.md with triple sign-off | 3-way (PM, Architect, Tech-Lead) |

### Stack Pack Commands

| Command | Purpose | Governance |
|---------|---------|-----------|
| `/aod.stack use <pack>` | Activate a stack pack | N/A |
| `/aod.stack remove` | Deactivate the active pack | N/A |
| `/aod.stack list` | List available packs | N/A |
| `/aod.stack scaffold` | Scaffold project from active pack | N/A |

### Security Commands

| Command | Purpose | Governance |
|---------|---------|-----------|
| `/security` | SAST/SCA scan — OWASP Top 10 + CVE analysis, audit artifacts, severity gate | Invoked as Step 7 of `/aod.build`; opt-out via `--no-security` |

> **Note**: `/security` is implemented as a skill (`.claude/skills/security/`) rather than a command, but is user-invocable as a slash command for standalone ad-hoc scans.

Key outputs: `specs/{NNN}-*/security-scan.md` (human-readable), `.security/scan-log.jsonl`, `.security/vulnerabilities.jsonl`, `.security/reports/*.sarif` (SARIF 2.1.0), `.security/reports/sca-*.cdx.json` (CycloneDX 1.5 SBOM). Blocks on CRITICAL/HIGH findings until acknowledged or fixed.

### Utility Commands

| Command | Purpose | Governance |
|---------|---------|-----------|
| `/aod.clarify` | Ask 5 clarification questions | N/A |
| `/aod.analyze` | Cross-artifact consistency check | N/A |
| `/aod.checklist` | Generate custom task checklist | N/A |
| `/aod.constitution` | Create/update project constitution | N/A |
| `/aod.kickstart` | POC kickstart — generate consumer guide with seed features | N/A |
| `/aod.blueprint` | Unified project setup and story generation from consumer guide | N/A |
| `/aod.status` | Regenerate BACKLOG.md and show lifecycle stage summary | N/A |
| `/aod.roadmap` | Scaffold quarterly roadmap from completed PRDs | PM sign-off |
| `/aod.okrs` | Scaffold OKR document with standard template | PM sign-off |

### Orchestration Commands

| Command | Purpose | Use Case |
|---------|---------|----------|
| `/aod.run` | Full lifecycle orchestrator — chains all 6 stages with governance gates | End-to-end feature development |
| `/aod.orchestrate` | Multi-feature wave execution from blueprint output | Batch feature execution in priority waves |
| `/execute` | Execute any task with optimal agent orchestration | General-purpose task execution |
| `/continue` | Generate session continuation prompt | Long features spanning multiple sessions |

### Maintenance Commands

| Command | Purpose | Governance |
|---------|---------|-----------|
| `/aod.sync-upstream` | Sync template files to upstream agentic-oriented-development-kit repo | N/A |

---

## Workflow Examples

### Example 1: Full Feature Development (Triad Workflow)

```bash
# 1. Create PRD with automatic validation
/aod.define "User authentication with OAuth2"

# 2. Plan — chains spec → project-plan → tasks with governance gates
/aod.plan

# 3. Execute implementation with architect checkpoints
/aod.build

# 4. Close feature with documentation updates
/aod.deliver 001

# 5. Code quality review (optional)
/aod.document
```

**Automatic Sign-offs**: PM approves product requirements, Architect approves technical design, Tech-Lead optimizes task assignment for parallel execution. `/aod.plan` handles all three Plan sub-steps with their respective governance gates.

---

## Customization Guide

### 1. Replace Template Variables

Search and replace in all `.claude/agents/*.md` files:

```bash
# Example: Customize for Express + Vue + MySQL project
sed -i 's/{{BACKEND_FRAMEWORK}}/Express/g' .claude/agents/*.md
sed -i 's/{{FRONTEND_FRAMEWORK}}/Vue/g' .claude/agents/*.md
sed -i 's/{{DATABASE}}/MySQL/g' .claude/agents/*.md
sed -i 's/Not yet defined/AWS/g' .claude/agents/*.md
sed -i 's/tachi/my-project/g' .claude/agents/*.md .claude/skills/**/*.md .claude/commands/*.md
```

### 2. Adjust File Paths

Update `{{BACKEND_PATH}}` and `{{FRONTEND_PATH}}` to match your project structure:

```bash
# Example: Backend in "server/src", frontend in "app/src"
sed -i 's/{{BACKEND_PATH}}/server\/src/g' .claude/agents/*.md
sed -i 's/{{FRONTEND_PATH}}/app\/src/g' .claude/agents/*.md
```

### 3. Add Project-Specific Context

Edit individual agent files to add:
- Project-specific conventions (naming, patterns)
- Team-specific processes
- Technology-specific best practices

---

## Agent Invocation Patterns

### Using the Task Tool (Recommended)

```
Task: "Implement authentication module per spec.md"
Agent: senior-backend-engineer
Context: .aod/spec.md, .aod/plan.md
Expected Output: backend/src/auth/* implementation
```

### Using SlashCommand Tool

```
SlashCommand: /aod.tasks
Context: .aod/spec.md and plan.md must exist
Expected Output: .aod/tasks.md with dependency-ordered tasks
```

### Parallel Agent Invocation

```python
# Launch 3 agents in parallel (SINGLE message)
Task(subagent_type="senior-backend-engineer", prompt="Implement T010-T020")
Task(subagent_type="frontend-developer", prompt="Implement T030-T040")
Task(subagent_type="tester", prompt="Implement T050-T060")
```

---

## Directory Structure

```
.claude/
├── agents/           → 13 specialized agents
│   ├── product-manager.md
│   ├── architect.md
│   ├── team-lead.md
│   ├── orchestrator.md
│   ├── senior-backend-engineer.md
│   ├── frontend-developer.md
│   ├── tester.md
│   ├── devops.md
│   ├── code-reviewer.md
│   ├── debugger.md
│   ├── web-researcher.md
│   ├── ux-ui-designer.md
│   └── security-analyst.md
│
├── skills/           → 24 automation capabilities
│   ├── ~aod-blueprint/
│   ├── ~aod-bugfix/
│   ├── ~aod-build/
│   ├── ~aod-define/
│   ├── ~aod-deliver/
│   ├── ~aod-discover/
│   ├── ~aod-kickstart/
│   ├── ~aod-plan/
│   ├── ~aod-project-plan/
│   ├── ~aod-run/
│   ├── ~aod-score/
│   ├── ~aod-spec/
│   ├── ~aod-status/
│   ├── aod-foundation/
│   ├── aod-lens/
│   ├── aod-orchestrate/
│   ├── aod-stack/
│   ├── code-execution-helper/
│   ├── git-workflow-helper/
│   ├── kb-create/
│   ├── kb-query/
│   ├── root-cause-analyzer/
│   ├── security/
│   └── triad/
│
├── design/           → 6 design archetypes
│   └── archetypes/
│       ├── boldness.md
│       ├── playful.md
│       ├── precision.md
│       ├── sophistication.md
│       ├── technical.md
│       └── warmth.md
│
├── commands/         → 23 slash commands
│   ├── aod.analyze.md
│   ├── aod.blueprint.md
│   ├── aod.build.md
│   ├── aod.checklist.md
│   ├── aod.clarify.md
│   ├── aod.constitution.md
│   ├── aod.define.md
│   ├── aod.deliver.md
│   ├── aod.discover.md
│   ├── aod.document.md
│   ├── aod.kickstart.md
│   ├── aod.okrs.md
│   ├── aod.plan.md
│   ├── aod.project-plan.md
│   ├── aod.roadmap.md
│   ├── aod.run.md
│   ├── aod.score.md
│   ├── aod.spec.md
│   ├── aod.status.md
│   ├── aod.sync-upstream.md
│   ├── aod.tasks.md
│   ├── continue.md
│   └── execute.md
│
└── README.md         → This file
```

---

## Key Principles

1. **Triad Workflow** - Use `/aod.*` commands for automatic governance (PM + Architect + Tech-Lead sign-offs)
2. **Parallel Execution** - Team-lead orchestrates agents working on different files simultaneously
3. **Constitutional Compliance** - All agents respect `.aod/memory/constitution.md` principles
4. **Knowledge Capture** - Use KB skills to document patterns, bugs, and architectural decisions
5. **Quality Gates** - Code-reviewer validates before deployment, architect checkpoints during implementation

---

## Tips

- **Start with Triad**: Use `/aod.*` commands for all features (automatic governance)
- **Parallel Orchestration**: Use `/aod.build` for features with architect checkpoints
- **Research First**: Use `web-researcher` agent before implementing with unfamiliar libraries
- **Checkpoint Long Features**: Use `~aod-build` skill for features spanning multiple sessions
- **Review Before Deploy**: Always invoke `code-reviewer` agent in Phase 5 before production deployment

---

## Recent Changes

- **2026-03-28**: Feature 100 — Added `/aod.foundation` workshop skill for post-init vision and design identity setup
  - New skill: `aod-foundation` (two-part guided workshop)
  - Pre-flight validation added to `/aod.build` for session resumption
- **2026-03-27**: Feature 097 — Added design quality system
  - 6 design archetypes in `.claude/design/archetypes/`
  - Design quality rules (`.claude/rules/design-quality.md`)
  - Design context loader (`.claude/rules/design-context-loader.md`)
  - Design quality gate in `/aod.build` pipeline (Step 6, opt-out via `--no-design-check`)
  - Brand identity system (`brands/` directory structure)
- **2026-01-31**: Removed unused commands (_triad-init, team-lead.implement, triad.architect-baseline, triad.feasibility)
- **2025-12-04**: Initial infrastructure setup for agentic-oriented-development-kit template
  - Initial infrastructure: 12 agents, 9 skills, 15 commands
  - Applied templatization with 8 template variables
  - Created comprehensive README documentation

---

## Support

For detailed documentation on:
- **Triad Workflow**: See `docs/AOD_TRIAD.md`
- **Constitution**: See `.aod/memory/constitution.md`
- **Methodology**: See `docs/core_principles/`
- **Agent Details**: See individual agent files in `agents/`
