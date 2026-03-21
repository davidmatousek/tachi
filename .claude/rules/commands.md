# Commands

<!-- Rule file for tachi -->
<!-- This file is referenced from CLAUDE.md using @-syntax -->

## Overview

tachi provides the **Triad Commands** with automatic governance, PM/Architect/Team-Lead sign-offs, and full SDLC workflow support.

---

## Triad Commands

Use Triad commands for governance, quality gates, and multi-agent collaboration.

### SDLC Workflow Commands

```bash
/aod.define <topic>         # Create PRD with Triad validation (includes optional vision workshop)
/aod.plan                   # Plan stage orchestrator: chains spec → project-plan → tasks with governance gates
/aod.build [--no-security]  # Execute with auto architect checkpoints; --no-security skips security scan (Step 6)
/aod.deliver {NNN}          # Close feature with parallel doc updates
/aod.document               # Human-driven quality review (code simplification, docstrings, CHANGELOG, API docs)
```

**Individual Plan sub-commands** (use `/aod.plan` unless you need to run steps separately):
```bash
/aod.spec                   # Create spec.md with auto PM sign-off
/aod.project-plan           # Create plan.md with auto PM + Architect sign-off
/aod.tasks                  # Create tasks.md with auto triple sign-off
```

### Utility Commands

```bash
/aod.clarify             # Ask clarification questions about current feature
/aod.analyze             # Verify spec/plan/task consistency
/aod.checklist           # Run Definition of Done checklist
/aod.constitution        # View or update governance constitution
/aod.kickstart           # POC kickstart — generate consumer guide with seed features from a project idea
/aod.roadmap             # Scaffold quarterly roadmap from completed PRDs with PM sign-off
/aod.okrs                # Scaffold OKR document with standard template and PM sign-off
```

**When to Use**:
- Production features requiring quality gates
- Multi-stakeholder projects needing sign-offs
- Complex features with architecture review requirements
- When you need documented governance trail
- Clarifying requirements or verifying consistency at any phase
- Kickstarting a new project with a structured seed feature backlog
- Post-delivery code quality review (code simplification, CHANGELOG, docstrings, API docs)

### Stack Pack Commands

```bash
/aod.stack use <pack>        # Activate a stack pack (copies rules, generates persona loader, persists state)
/aod.stack remove            # Deactivate the active pack (removes rules, deletes state)
/aod.stack list              # List available packs with active indicator
/aod.stack scaffold          # Scaffold project from active pack's template files
```

**When to Use**:
- Setting up a new project with a specific technology stack
- Switching between technology stacks during development
- Scaffolding the canonical project structure after activation
- Checking which packs are available and which is active

### Maintenance Commands

```bash
/aod.sync-upstream       # Sync template files to upstream agentic-oriented-development-kit repo
```

**When to Use**:
- Ad-hoc fixes, refactors, or direct commits to main that bypass `/aod.deliver`
- Any time template content changes and needs to be propagated upstream
- Standalone alternative to Step 8 of `/aod.deliver`

---

## PDL Commands (Optional Discovery)

Use PDL commands for lightweight product discovery before the Triad workflow. PDL is optional — you can start directly at `/aod.define` if you prefer.

```bash
/aod.discover <idea>            # Full discovery flow: capture → score → validate → backlog
/aod.discover --seed <idea>     # Fast-track pre-vetted ideas (auto ICE, skip prompts/PM)
/aod.discover <idea>           # Capture idea + ICE scoring
/aod.score #NNN            # Re-score an existing idea (NNN = GitHub Issue number)
/aod.validate #NNN         # PM validation gate + user story generation
```

**When to Use**:
- Capturing feature ideas during brainstorming or development
- Evaluating ideas with ICE scoring before committing to PRD creation
- Fast-tracking seed stories from a consumer guide (`--seed` flag)
- Maintaining a prioritized product backlog of validated user stories
- Running PM validation gates on ideas before heavy Triad governance
