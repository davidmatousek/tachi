# Agentic Oriented Development Kit (AOD Kit)

**SDLC Triad governance template for AI agent-assisted development.**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)](CHANGELOG.md)

---

## tachi — Automated Threat Modeling

tachi is an automated threat modeling toolkit that extends STRIDE with AI-specific threat agents for agentic applications. It provides a structured approach to threat analysis with machine-readable schemas, consistent output templates, and support for 5 architecture input formats.

### Integration Quickstart

| What | Where | Purpose |
|------|-------|---------|
| **Interface Contract** | [`docs/INTERFACE-CONTRACT.md`](docs/INTERFACE-CONTRACT.md) | Single document covering input formats, invocation protocol, output structure, and side effects |
| **Output Template** | [`templates/threats.md`](templates/threats.md) | Canonical output structure with all 7 required sections and example values |
| **Schemas** | [`schemas/`](schemas/) | Machine-readable contracts: [`finding.yaml`](schemas/finding.yaml) (IR schema), [`input.yaml`](schemas/input.yaml) (input validation), [`output.yaml`](schemas/output.yaml) (output structure) |
| **Examples** | [`examples/`](examples/) | Sample inputs and expected outputs: [ASCII web API](examples/ascii-web-api/), [Mermaid agentic app](examples/mermaid-agentic-app/), [free-text microservice](examples/free-text-microservice/) |
| **Threat Agents** | [`agents/stride/`](agents/stride/) (6 STRIDE) + [`agents/ai/`](agents/ai/) (5 AI) | Agent prompt definitions for threat detection |

### Supported Input Formats

| Priority | Format | Example |
|----------|--------|---------|
| 1 | ASCII | Box-drawing diagrams with `+--+`, `\|`, `[...]` |
| 2 | Free-text | Prose architecture descriptions |
| 3 | Mermaid | `flowchart`, `graph`, `sequenceDiagram` |
| 4 | PlantUML | `@startuml` / `@enduml` blocks |
| 5 | C4 | `Person`, `System`, `Container` declarations |

See the [Interface Contract](docs/INTERFACE-CONTRACT.md) for full format details, recognition patterns, and invocation protocol.

---

## What is AOD Kit?

The Agentic Oriented Development Kit (AOD Kit) is a governance template that brings structured software development lifecycle (SDLC) practices to AI agent-assisted workflows. It uses the **AOD Triad** -- a three-role governance methodology involving a Product Manager, Architect, and Team Lead -- to enforce sign-offs and quality gates at every phase of development. AOD Kit works with any AI coding agent and provides the scaffolding for turning product ideas into well-governed implementations. Whether you are a solo developer or a team, the Triad ensures nothing ships without proper review.

> **Naming Note**: "AOD Triad" refers to the governance methodology (the three-role sign-off process). "AOD Kit" refers to this template repository that implements the methodology.

---

## Quick Start

```bash
# 1. Clone the template
git clone https://github.com/your-org/agentic-oriented-development-kit.git my-project
cd my-project

# 2. Initialize your project
make init

# 3. Verify the setup
make check

# 4. Start your first feature
/triad.prd my-first-feature
```

That's it. The Triad workflow will guide you through PRD creation, specification, planning, task breakdown, and implementation -- with governance at every step.

---

## Solo Developer Quick Start

**The Triad roles are three hats you wear, not three people.**

As a solo developer, you play all three roles. The governance framework still provides value by forcing you to think through product (Why?), architecture (How?), and execution (When?) before writing code.

**When to use the full workflow**: Features that touch multiple systems, require careful planning, or have non-obvious technical decisions.

**When to use the light workflow**: Small fixes, documentation updates, or well-understood changes where a quick `/triad.prd` and `/triad.specify` are sufficient.

```bash
# Full workflow (recommended for new features)
/triad.prd user-authentication    # Wear the PM hat: define what and why
/triad.specify                     # Research and write the spec
/triad.plan                        # Wear the Architect hat: define how
/triad.tasks                       # Wear the Team-Lead hat: define when
/triad.implement                   # Execute with checkpoints

# Light workflow (for smaller changes)
/triad.prd quick-bugfix           # Brief PRD
/triad.specify                     # Spec + implement
```

---

## What's Included

```
agentic-oriented-development-kit/
├── .claude/              # Agent definitions, skills, and commands
│   ├── agents/           # PM, Architect, Team-Lead, and specialist agents
│   ├── commands/         # Triad workflow commands (/triad.*)
│   ├── rules/            # Governance rules and context loading
│   └── skills/           # Reusable agent skills
├── .aod/             # Source of truth for current feature
│   ├── spec.md           # Feature specification (created by /triad.specify)
│   ├── plan.md           # Implementation plan (created by /triad.plan)
│   ├── tasks.md          # Task breakdown (created by /triad.tasks)
│   ├── memory/           # Constitution and institutional knowledge
│   ├── scripts/          # Governance automation scripts
│   └── templates/        # Document templates
├── docs/                 # Product, architecture, standards, and guides
│   ├── product/          # Product vision, PRDs, user stories
│   ├── architecture/     # System design and deployment docs
│   ├── standards/        # Definition of Done, naming, collaboration
│   ├── core_principles/  # Thinking lenses (5 Whys, Pre-Mortem, etc.)
│   └── guides/           # Workflow and onboarding guides
├── specs/                # Feature-specific specs, research, and artifacts
├── scripts/              # Setup and validation scripts (init.sh, check.sh)
├── CLAUDE.md             # AI agent context and project instructions
├── Makefile              # Common commands (init, check, review-spec, etc.)
└── README.md             # This file
```

---

## The SDLC Triad

The AOD Triad is a lightweight governance framework ensuring Product-Architecture-Engineering alignment.

| Role | Defines | Authority | Key Questions |
|------|---------|-----------|---------------|
| **PM (Product Manager)** | What & Why | Scope and requirements | What problem are we solving? Why now? |
| **Architect** | How | Technical decisions | How should this be built? What are the constraints? |
| **Team-Lead** | When & Who | Timeline and assignments | When can we deliver? Who works on what? |

### Sign-off Requirements

| Artifact | Required Sign-offs |
|----------|-------------------|
| `spec.md` | PM |
| `plan.md` | PM + Architect |
| `tasks.md` | PM + Architect + Team-Lead |

No artifact proceeds to the next phase without the required approvals.

---

## Using with Other AI Agents

AOD Kit is optimized for Claude Code but the AOD Triad methodology works with any AI coding agent. The governance principles -- product-led thinking, structured sign-offs, and quality gates -- are universal patterns that improve AI-assisted development regardless of the tool.

For **Cursor**, **GitHub Copilot**, or **Windsurf**: The `.aod/` directory structure and governance documents serve as context that any agent can read. You can adapt the Triad workflow by providing the relevant spec, plan, or task files as context to your agent of choice. The key is maintaining the sign-off discipline, even if the automation looks different.

If you are migrating from another agent workflow, start by adopting the `.aod/` file structure and the three-role review process. The specific commands (`/triad.*`) are Claude Code integrations, but the underlying methodology -- define What/Why, then How, then When/Who -- works everywhere. See the `docs/guides/` directory for adaptation examples.

---

## Template Variables Reference

AOD Kit uses template variables that you customize during setup. See [`.claude/README.md`](.claude/README.md) for the complete list of variables and configuration options.

---

## Contributing

We welcome contributions. See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on filing issues, submitting pull requests, and our code of conduct.

---

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.
