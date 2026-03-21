# Technology Stack - tachi

**Last Updated**: 2026-03-21
**Owner**: Architect

---

## Overview

This document defines the technology stack for tachi.

---

## Frontend

**Framework**: {{FRONTEND_FRAMEWORK}}
- Version: {{VERSION}}
- Why: {{RATIONALE}}

**UI Library**: {{UI_LIBRARY}}
- Examples: React, Vue, Svelte, Angular

**Styling**: {{STYLING_APPROACH}}
- Examples: Tailwind CSS, CSS Modules, Styled Components

**State Management**: {{STATE_MANAGEMENT}}
- Examples: Redux, Zustand, Jotai, Context API

**Build Tool**: {{BUILD_TOOL}}
- Examples: Vite, Webpack, Parcel

---

## Backend

**Runtime**: {{BACKEND_RUNTIME}}
- Examples: Node.js, Python, Go, Rust

**Framework**: {{BACKEND_FRAMEWORK}}
- Examples: Fastify, Express, FastAPI, Gin

**Language**: {{BACKEND_LANGUAGE}}
- Version: {{VERSION}}

**API Style**: {{API_STYLE}}
- Examples: REST, GraphQL, gRPC

---

## Database

**Primary Database**: {{DATABASE_TYPE}}
- Examples: PostgreSQL, MySQL, MongoDB

**Version**: {{VERSION}}
**Provider**: {{DATABASE_PROVIDER}}
- Examples: Self-hosted, AWS RDS, Neon, PlanetScale

**ORM/Query Builder**: {{ORM}}
- Examples: Prisma, Drizzle, TypeORM, SQLAlchemy

---

## Infrastructure

**Hosting Platform**: {{HOSTING_PLATFORM}}
- Examples: Vercel, AWS, Google Cloud, Railway

**Container Runtime**: {{CONTAINER_RUNTIME}}
- Examples: Docker, Kubernetes, None (serverless)

**CI/CD**: {{CICD_PLATFORM}}
- Examples: GitHub Actions, GitLab CI, CircleCI

---

## Monitoring & Observability

**Logging**: {{LOGGING_SOLUTION}}
**Metrics**: {{METRICS_SOLUTION}}
**Error Tracking**: {{ERROR_TRACKING}}

---

## Development Tools

**Package Manager**: {{PACKAGE_MANAGER}}
**Code Quality**: {{LINTING_TOOLS}}
**Testing**: {{TESTING_FRAMEWORKS}}

---

## AOD Kit Internal Tooling

These are tools used by the AOD Kit itself (not the adopter's application stack).

### Shell Scripts

**Bash 3.2** (macOS default `/bin/bash`)
- All `.aod/scripts/bash/*.sh` files must be Bash 3.2 compatible
- Why: macOS ships Bash 3.2.57 due to GPLv3 licensing; portability is mandatory
- Constraints: No associative arrays, no `${var^^}`, no `readarray`/`mapfile`

**Key scripts**:
| Script | Purpose | Added |
|--------|---------|-------|
| `.aod/scripts/bash/logging.sh` | Simple logging utility for timestamped log entries; provides `aod_log` function with configurable output path and graceful error handling | Feature 049 |
| `.aod/scripts/bash/run-state.sh` | Atomic read/write/validate for orchestrator state (`.aod/run-state.json`); includes compound helpers for incremental reads and governance caching | Feature 022, extended Feature 030 |
| `.aod/scripts/bash/github-lifecycle.sh` | GitHub Issue label management for stage transitions | Pre-022 |
| `.aod/scripts/bash/backlog-regenerate.sh` | Regenerate product backlog from GitHub Issues | Pre-022 |

### CLI Dependencies

| Tool | Required By | Purpose | Install |
|------|-------------|---------|---------|
| `jq` | `run-state.sh` | JSON parsing and atomic state manipulation | `brew install jq` (macOS) / `apt-get install jq` (Linux) |
| `gh` | `github-lifecycle.sh`, `run-state.sh` (optional), `scripts/init.sh` (optional) | GitHub Issue/label management, Projects board creation during init | `brew install gh` / `gh auth login` |

**Note**: `gh` degrades gracefully -- the orchestrator falls back to artifact-only detection when `gh` is unavailable or unauthenticated. Similarly, `scripts/init.sh` skips GitHub Projects board creation when `gh` is missing, unauthenticated, or lacks the `project` OAuth scope, reporting status in the init summary with remediation guidance.

### Template Variables

`scripts/init.sh` performs `sed` substitution on user-facing template files during `make init`. The following placeholders are replaced at init time:

| Placeholder | Replaced With | Scope |
|-------------|---------------|-------|
| `tachi` | Adopter's project name (entered at `make init` prompt) | 12 template files (Feature 061) |
| `2026-03-21` | Current date at init time | Select files |

**`tachi` is a first-class template variable** (Feature 061). All user-facing template files in `.claude/`, `docs/`, `CLAUDE.md`, and `README.md` use this placeholder rather than hardcoding "Agentic Oriented Development Kit". After `make init`, adopters see their own project name throughout.

When adding a new user-facing template file to the kit, use `tachi` wherever the project name should appear and confirm the file is included in the `scripts/init.sh` substitution loop. See [ADR-009](../02_ADRs/ADR-009-template-variable-expansion-scope.md) and the [Template Variable Expansion pattern](../03_patterns/README.md#pattern-template-variable-expansion).

---

### Subagent Results Directory

**Directory**: `.aod/results/` (ephemeral session artifacts, gitignored)
- Architecture: File-based offloading for minimal subagent returns (Feature 073)
- Convention: Each subagent writes detailed findings to `.aod/results/{agent-name}.md` before returning
- Return policy: Subagents return only STATUS + ITEMS count + DETAILS path to the main context (max 10 lines / ~200 tokens)
- Overwrite semantics: Each invocation overwrites the prior results file for the same agent
- Initialization: Subagents create the directory if absent (self-healing, no pre-init required)
- See [ADR-010](../02_ADRs/ADR-010-minimal-return-architecture.md) for the design decision
- See [Minimal-Return Subagent pattern](../03_patterns/README.md#pattern-minimal-return-subagent) for implementation guidance

**Context budget impact**: A full Triad review cycle (3 reviewers) consumes less than 600 tokens in the main context (down from 1,500-6,000 tokens), enabling 90+ minute sustained orchestration sessions.

---

### Stack Packs System

**Directory**: `stacks/` (convention contracts, persona supplements, scaffold templates, rules)
- Architecture: Dual-surface injection pattern (Feature 058)
- Management skill: `.claude/skills/aod-stack/SKILL.md` (`/aod.stack use|remove|list|scaffold`)
- State file: `.aod/stack-active.json` (JSON, tracks active pack name and activation timestamp)
- Runtime rules surface: `.claude/rules/stack/` (copied on activation, cleaned on removal)
- See ADR-007 for the design decision behind dual-surface injection

**Shipped packs**:
| Pack | Status | Purpose |
|------|--------|---------|
| `stacks/nextjs-supabase/` | Full | Next.js + TypeScript + Supabase + Prisma + Vercel conventions |
| `stacks/fastapi-react/` | Full | Python FastAPI + SQLAlchemy 2.0 async + React 19 + TypeScript + Vite + Docker Compose (Feature 078) |
| `stacks/fastapi-react-local/` | Full | Python FastAPI + SQLAlchemy 2.0 async + aiosqlite + React 19 + Vite + Tailwind CSS 4 — zero external dependencies, local-first variant (Feature 085) |
| `stacks/swiftui-cloudkit/` | Skeleton | SwiftUI + CloudKit native iOS conventions |
| `stacks/knowledge-system/` | Full | Markdown + YAML + Claude Code for knowledge-intensive content systems (Feature 064) |

**Pack anatomy** (each pack directory):
| Path | Purpose |
|------|---------|
| `STACK.md` | Convention contract (required, ≤500 lines) |
| `agents/*.md` | Persona supplements for specialized/hybrid agents (≤100 lines each) |
| `rules/*.md` | Stack-specific coding rules (copied to `.claude/rules/stack/` on activation) |
| `scaffold/` | Project template files (optional, used by `/aod.stack scaffold`) |
| `skills/` | Stack-specific skills (optional, reserved for future use) |

**Context budget enforcement**:
| Component | Max Lines | Loaded When |
|-----------|-----------|-------------|
| STACK.md | 500 | Every agent invocation (if pack active) |
| Persona supplement | 100 | Specialized/hybrid agent invocations only |
| Stack rules (all files combined) | 200 | Every agent invocation (via rules discovery) |
| Total pack overhead | 800 | Maximum per invocation |

### Kickstart Skill

**Skill file**: `.claude/skills/~aod-kickstart/SKILL.md` (`/aod.kickstart`)
- Architecture: Three-stage interactive workflow (Idea Intake → Stack Selection → Guide Generation) (Feature 085)
- Output: `docs/guides/CONSUMER_GUIDE_{PROJECT_NAME}.md` — sequenced consumer guide with 6-10 seed features
- Stack detection: Reads `.aod/stack-active.json` to auto-detect active pack; falls back to manual selection
- Seed features structured for direct copy-paste into `/aod.discover`
- No infrastructure dependencies; pure methodology/template skill

### Orchestrator Skill Architecture

**Skill file**: `.claude/skills/~aod-run/SKILL.md` (~405 lines, core execution loop)
- Architecture: Segmented prompt with on-demand reference loading (Feature 030)
- Core file contains routing, state machine loop, and stage mapping
- Reference files loaded via Read tool only when needed:

| Reference File | Purpose | Loaded When |
|----------------|---------|-------------|
| `references/governance.md` | Governance gate detection, tiers, rejection handling | Governance cache miss |
| `references/entry-modes.md` | New-idea, issue, resume, status entry handlers | Mode routing |
| `references/dry-run.md` | Read-only preview handler | `--dry-run` flag |
| `references/error-recovery.md` | Corrupted state and lifecycle complete handlers | Error or completion |

- See ADR-002 for the design decision behind prompt segmentation

### Orchestrator State

**State file**: `.aod/run-state.json`
- Format: JSON (managed via `jq`)
- Atomicity: Write-then-rename pattern (`write to .tmp`, then `mv`) for crash safety
- Schema version: `1.0`
- Governance cache: Verdicts stored in `governance_cache` object to eliminate redundant artifact reads (Feature 030)
- Compound helpers: `aod_state_get_multi`, `aod_state_get_loop_context`, `aod_state_get_governance_cache` for incremental reads (Feature 030)
- See ADR-001 for the design decision behind atomic state management
- See ADR-006 for the design decision behind non-fatal error handling in observability operations

---

**Template Instructions**: Replace all `{{TEMPLATE_VARIABLES}}` with your actual technology choices. Document the "Why" for each major decision.
