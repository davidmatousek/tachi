# Stack Pack Consumer Guide — FastAPI + React (AOD Agent Orchestrator)

**Purpose**: Build the AOD Agent Orchestrator — a standalone, product-led AI agent orchestrator with a web UI — using the `fastapi-react-local` stack pack (SQLite, zero external dependencies). This guide covers project setup and seeds the backlog with epics and stories for iterative, governed development.

**What you're building**: A web-based orchestrator that manages a swarm of AI coding agent sessions (Claude, Gemini, Codex, etc.) through the full AOD lifecycle (Discover → Define → Plan → Build → Deliver → Document) with Triad governance, real-time monitoring, wave-based parallel execution, and agent-driven orchestration (a lead agent can drive the swarm via CLI or MCP).

**Target user**: A solo developer operating a swarm of AI agents to build complex projects. You are the PM, Architect, and Team-Lead — the orchestrator gives you visibility and control over many agents working in parallel, with governance as a quality forcing function and audit trail, not bureaucratic overhead.

**Key constraints**:
- Local-first (SQLite default, PostgreSQL optional via Docker)
- Claude Code as the primary agent driver (others in future epics)
- tmux + git worktrees for process isolation
- AOD Kit methodology baked in during `make init`
- No authentication for MVP (localhost only)
- Rate-limit-aware session scheduling (respect agent provider limits)

**How to use this guide**: Phases 1-3 set up the project. Phase 4 seeds the backlog with epics. Each epic is then built using the full AOD lifecycle (`/aod.define` → `/aod.deliver`) in its own session. Report issues and learnings back to `product-led-spec-kit`.

---

## Governance Architecture

The orchestrator operates with **two layers of governance**:

### Layer 1: Orchestrator Lifecycle Governance

The orchestrator manages *which* features to build and *what stage* each is in. This is the outer loop:

```
GitHub Issues (ICE-scored)
    → Discover → Define → Plan → Build → Deliver → Document
```

The orchestrator enforces stage gates: you can't advance from Plan to Build without triple sign-off on `tasks.md`. This layer is visible in the dashboard's lifecycle and governance panels.

### Layer 2: Agent-Internal AOD Governance

Each spawned agent session runs its own AOD Triad internally. When an agent executes `/aod.spec`, it invokes PM, Architect, and Team-Lead review agents *within its own session*. The orchestrator doesn't control these internal reviews — the agent handles them autonomously.

**What this means for the orchestrator**:
- Layer 1 gates are enforced by the orchestrator's lifecycle engine (F-008)
- Layer 2 reviews happen inside each agent's context window — the orchestrator only sees the outcome (session completed/failed)
- The governance panel (F-009) surfaces Layer 1 status by parsing `.aod/` artifacts from worktrees
- Agent-internal governance quality depends on the AOD Kit methodology, not the orchestrator

### Methodology Pluggability

The lifecycle engine (F-008) should be designed with a methodology abstraction layer, even though MVP ships AOD-only. The interface should allow swapping governance methodology (like agtx's TOML plugin system supports "Spec-kit", "GSD", and "OpenSpec"). However, AOD's specialized agents (PM, Architect, Team-Lead) are tightly coupled to the methodology — true pluggability may require defining a standard agent protocol for governance roles. If this proves impractical, the orchestrator adopts an AOD-only position.

**MVP decision**: AOD-only, with the lifecycle engine interface designed for future extensibility.

---

## Prerequisites

- Claude Code installed (`claude` CLI)
- Python 3.12+ and `uv` installed
- Node.js 20+ and npm installed
- Git and GitHub CLI (`gh`) installed and authenticated
- tmux installed (`brew install tmux` on macOS)
- Docker Desktop (optional — not needed for local-first SQLite development)

---

## Phase 1: Clone & Initialize

Navigate to your projects directory (e.g., `~/Projects/`):

```bash
# Clone the public template
git clone https://github.com/davidmatousek/agentic-oriented-development-kit.git aod-orchestrator
cd aod-orchestrator

# Run interactive setup
make init
```

**When prompted, enter:**

| Prompt | Value |
|--------|-------|
| Project Name | `aod-orchestrator` |
| Description | `Product-led AI agent orchestrator with web UI, Triad governance, and multi-agent session management` |
| GitHub Org | `davidmatousek` |
| GitHub Repo | `aod-orchestrator` |
| AI Agent | `1` (Claude Code) |
| Tech Stack | Select `fastapi-react-local` — "Python FastAPI + React (Local)" |

```bash
# Verify setup
make check
```

**Expected output:**
- All checks pass (green checkmarks)
- 5 stack packs available
- No pack active

### Post-Init Verification

```bash
# Should return NO results — all placeholders replaced
grep -rn '{{' .aod/memory/constitution.md
```

---

## Phase 2: Activate Stack Pack & Scaffold

Open Claude Code in your project directory:

```bash
claude
```

Run these commands inside Claude Code:

```
# List available packs
/aod.stack list

# Activate the local-first FastAPI + React pack (SQLite, no Docker)
/aod.stack use fastapi-react-local

# Scaffold the project structure
/aod.stack scaffold
```

### Verification Checklist

After activation:
- [ ] `.aod/stack-active.json` exists with `"pack": "fastapi-react-local"`
- [ ] `.claude/rules/stack/` contains `conventions.md`, `security.md`, `persona-loader.md`
- [ ] Activation summary shows loaded rules and available persona supplements

After scaffold:
- [ ] `backend/app/main.py` exists (FastAPI app factory)
- [ ] `backend/app/api/v1/router.py` exists
- [ ] `backend/app/db/session.py` exists (async SQLAlchemy)
- [ ] `backend/pyproject.toml` exists with FastAPI, SQLAlchemy, aiosqlite deps
- [ ] `frontend/src/main.tsx` exists (React root)
- [ ] `frontend/src/api/client.ts` exists (typed fetch wrapper)
- [ ] `frontend/package.json` exists with React 19, TanStack Query, Tailwind
- [ ] `.env.example` exists with SQLite `DATABASE_URL` default

---

## Phase 3: Install Dependencies & Create Repo

```bash
# Copy environment file (must be done before starting backend)
cp .env.example .env

# Backend
cd backend && uv sync && cd ..

# Frontend
cd frontend && npm install && cd ..

# Verify backend starts (SQLite — no Docker needed)
cd backend && uv run uvicorn app.main:app --reload &
# Should see: Uvicorn running on http://127.0.0.1:8000
# Verify health: curl http://localhost:8000/health
kill %1 && cd ..

# Verify frontend starts
cd frontend && npm run dev &
# Should see: Local: http://localhost:5173/
kill %1 && cd ..
```

```bash
# Create GitHub repo
gh repo create davidmatousek/aod-orchestrator --private --source=. --push
```

```bash
# Set up GitHub Projects board (make init ran before the repo existed)
bash -c 'source .aod/scripts/bash/github-lifecycle.sh && aod_gh_setup_board'
```

> **Note**: If you see a "missing 'project' OAuth scope" error, run `gh auth refresh -s project` first.

### AOD Methodology Updates

The AOD governance methodology (`.aod/`, `.claude/`, `docs/`) was baked in during `make init`. To pull methodology updates from the upstream template in the future, cherry-pick changes from the [agentic-oriented-development-kit](https://github.com/davidmatousek/agentic-oriented-development-kit) repo or re-run `make init` on a fresh clone and diff.

Review the seeded product vision:

```bash
cat docs/product/01_Product_Vision/product-vision.md
```

---

## Requirements

> **No action needed** — review the requirements and feature list below for context. These trace to the features you'll build starting in Phase 4.

### Functional Requirements

| ID | Requirement | Features |
|----|------------|----------|
| FR-01 | Register and manage multiple projects with active project selection | F-002b, F-007b |
| FR-02 | Spawn agent sessions in isolated tmux + git worktree environments | F-003 |
| FR-03 | Monitor agent session status (running/completed/failed/cancelled) in real-time | F-003, F-005 |
| FR-04 | Cancel running sessions and retry failed sessions | F-004 |
| FR-05 | Persist full session output beyond tmux session lifetime | F-004 |
| FR-06 | Pluggable agent driver abstraction (Claude first, others later) | F-004 |
| FR-07 | Web dashboard with session, task, and governance panels | F-005 |
| FR-08 | Real-time dashboard updates via WebSocket | F-005 |
| FR-09 | Desktop notifications on session completion/failure | Deferred (post-MVP) |
| FR-10 | Full-text search across past session logs | Deferred (post-MVP) |
| FR-25 | Create tasks from Task Board UI and select tasks in Spawn Modal | F-007a |
| FR-26 | Create, edit, activate, and delete projects from the dashboard UI | F-007b |
| FR-11 | Read GitHub Issues with ICE score parsing and local caching | F-007 |
| FR-12 | AOD lifecycle engine mapping issues to stages with gate enforcement | F-007 |
| FR-13 | Trigger AOD governance commands (`/aod.define`, `/aod.spec`, etc.) from dashboard | F-008 |
| FR-14 | Display Triad sign-off status and trigger reviews from UI | F-009 |
| FR-15 | Parse `agent-assignments.md` and dispatch parallel sessions | F-010a |
| FR-16 | Architect checkpoints at priority boundaries between waves | F-010b |
| FR-17 | Auto-create PRs from completed agent sessions with task-based descriptions | F-011 |
| FR-18 | Review diffs and merge agent PRs from dashboard | F-011 |
| FR-19 | Sync governance artifacts (`.aod/` files) from worktrees back to main branch | F-011 |
| FR-20 | Detect and surface agent context limit warnings (build AND governance sessions) | F-004 |
| FR-21 | CLI interface for session spawning, status checking, and full orchestration | F-003, F-004, F-012 |
| FR-22 | Configuration file (`.aod-orchestrator.toml`) for agent timeouts, retry policies, concurrent limits, prompt templates | F-001 |
| FR-23 | Resource and capacity monitoring (worktrees, tmux sessions, disk, ptys) with spawn refusal at thresholds | F-001, F-004 |
| FR-24 | Rate-limit-aware session scheduler that queues sessions and respects concurrent limits per agent provider | F-003 |
| FR-27 | MCP server exposing orchestrator operations as native agent tools | F-012 |
| FR-28 | Lead agent autonomous wave orchestration (spawn, monitor, retry, advance) | F-012 |
| FR-29 | Lead agent activity visible in dashboard alongside human-initiated sessions | F-012, F-005 |

### Non-Functional Requirements

| ID | Requirement | Target |
|----|------------|--------|
| NFR-01 | Local-first operation | SQLite (WAL mode) default; no external services required. PostgreSQL optional via Docker |
| NFR-02 | Dashboard responsiveness | Status updates within 3s of state change |
| NFR-03 | Session state durability | State survives backend restart (persisted in DB) |
| NFR-04 | No authentication for MVP | Localhost only; defer auth to multi-user version |
| NFR-05 | Agent driver extensibility | New agent = new driver class, no core changes |
| NFR-06 | Concurrent session capacity | Support 10+ parallel agent sessions (subject to provider rate limits) |
| NFR-07 | Stack compliance | All code follows fastapi-react-local stack pack conventions |
| NFR-08 | Test coverage | 80%+ on services and API layers |
| NFR-09 | Structured logging | JSON logs; health endpoint with dependency and resource status |
| NFR-10 | Data integrity | Atomic state changes; no orphaned worktrees on failure |
| NFR-11 | System resource documentation | Document minimum requirements for running N parallel sessions (ptys, FDs, disk, memory) |

---

## Feature List

Each feature is one AOD item — a single `/aod.discover` → `/aod.deliver` cycle. Use `--seed` flag to fast-track seed stories (skips ICE prompts, evidence, and PM validation). Features are organized into groups for readability, but groups have no governance meaning. Execute features in order; each builds on the previous.

**Important**: Each feature spec MUST include an **Interface Contract** section documenting the exact API shapes, event names, DB schemas, and conventions it consumes from dependencies and produces for dependents. This is the cross-session handshake that prevents integration failures when features are built by different agent sessions.

| ID | Feature | Group | Stories | Depends On |
|----|---------|-------|---------|------------|
| F-001 | Project Skeleton & Health Check | 1. Foundation | 4 | — |
| F-002a | Domain Models & Migrations | 2. Data Layer | 3 | F-001 |
| F-002b | REST API, Services & Tests | 2. Data Layer | 3 | F-002a |
| F-003 | Agent Session Spawning & Scheduling | 3. Execution | 3 | F-002b |
| F-004 | Session Lifecycle & Driver Abstraction | 3. Execution | 5 | F-003 |
| F-005 | Dashboard Core with WebSocket | 4. Dashboard | 5 | F-002b, F-004 |
| F-007 | GitHub Issues + Lifecycle Engine | 5. Lifecycle | 4 | F-002b |
| F-007a | Task Creation & Spawn Task Selector | 4. Dashboard | 4 | F-005, F-002b |
| F-007b | Project Management UI | 4. Dashboard | 4 | F-005, F-002b |
| F-008 | Stage Gates & Governance Triggers | 5. Lifecycle | 3 | F-007, F-003 |
| F-009 | Governance & Sign-off Panel | 6. Governance | 3 | F-008, F-005 |
| F-010a | Parallel Session Spawning | 7. Orchestration | 2 | F-003 |
| F-010b | Wave Pipeline & Pipeline Dashboard | 7. Orchestration | 5 | F-010a, F-008, F-005 |
| F-011 | PR Workflow & Artifact Merge-Back | 8. Integration | 4 | F-003, F-005 |
| F-012 | CLI & MCP — Agent-Driven Orchestration | 9. Agent Interface | 5 | F-010b |

**Constraint**: The orchestrator must not orchestrate itself for MVP. Self-orchestration creates governance recursion (a Strange Loop) that is extremely hard to debug. Scope the orchestrator to managing *other* projects. The lead agent pattern (F-012) enables a Claude Code session to drive the orchestrator — but the orchestrator manages worker agents on a *different* project, not itself.

---

## Phase 4: Seed the Backlog

Each feature below is one AOD item. For each feature, copy the **entire block** (goal, stories, interface contract, and Definition of Done) and paste it into `/aod.discover --seed`. The `--seed` flag fast-tracks pre-vetted ideas — it auto-assigns P1 ICE defaults and skips scoring prompts, evidence, and PM validation. This feeds the detailed stories into the lifecycle so that downstream commands (`/aod.define`, `/aod.spec`, etc.) build on them rather than generating from scratch.

After discovering all features, execute the full lifecycle (`/aod.define` → `/aod.deliver`) for each feature in its own session, in dependency order.

---

### Group 1: Foundation

#### F-001: Project Skeleton & Health Check

**Goal**: Backend serves a health endpoint with resource checks, frontend renders a dashboard shell, Alembic migrations run against SQLite, and the configuration file is established.

**Stories**:

1. **As a developer, I want the backend to start with SQLite (WAL mode) and serve a health endpoint**, so that I can develop locally with zero external dependencies.
   - SQLite database at `{project_root}/data/app.db` with WAL mode enabled (scaffold default)
   - Move scaffold's `/health` endpoint to `/api/v1/health` and enhance: return `{ "status": "healthy", "database": "connected", "version": "0.1.0" }`
   - Checks actual database connectivity (not just a static response)

2. **As a developer, I want the React frontend to display a dashboard shell with navigation**, so that I have a working UI foundation to build on.
   - App shell with sidebar navigation (Dashboard, Sessions, Tasks, Governance)
   - Dashboard page shows health status fetched from `/api/v1/health`
   - Tailwind + clean layout (no component library needed yet)
   - Frontend proxies `/api` requests to backend (Vite config)

3. **As a developer, I want Alembic migrations configured for async SQLite with a baseline migration**, so that schema changes are versioned from the start.
   - Async Alembic env.py configured for SQLite with `render_as_batch=True`
   - Empty baseline migration proves the pipeline works
   - `uv run alembic upgrade head` succeeds against SQLite

4. **As a developer, I want a configuration file (`.aod-orchestrator.toml`) with sensible defaults**, so that orchestrator behavior is configurable without code changes.
   - Agent timeout defaults, retry policies, concurrent session limits per provider
   - Worktree root path, log directory, database path
   - Resource thresholds (max worktrees, max tmux sessions, min disk space)
   - Startup routine reads config, validates, and logs effective settings

**Interface Contract (produces)**:
- `GET /api/v1/health` → `{ status, database, version, resources: { worktrees, tmux_sessions, disk_free_gb } }`
- Config model: `OrchestratorConfig` (Pydantic BaseSettings from TOML + env vars)
- Database: SQLite at `data/app.db` (WAL mode, scaffold default)

**Definition of Done**: Backend starts with SQLite, health endpoint returns resource status, frontend shows dashboard shell, Alembic migration runs, config file loads with defaults. Startup prunes orphaned worktrees and checks system resources (ptys, FDs, disk).

---

### Group 2: Data Layer

#### F-002a: Domain Models & Migrations

**Goal**: Core data models (Project, AgentSession, Task) with Alembic migrations and seed data.

**Stories**:

1. **As a developer, I want Project, AgentSession, and Task ORM models**, so that the orchestrator has a persistent data backbone.
   - Project: id, name, repo_url, worktree_root, aod_kit_path, is_active, created_at, updated_at
   - AgentSession: id, project_id (FK), agent_type, tmux_session_name, worktree_path, status (pending/queued/running/completed/failed/cancelled), task_description, started_at, completed_at, exit_code, output_summary, retry_of (FK, nullable), context_warning (bool)
   - Task: id, project_id (FK), session_id (FK, nullable), title, description, priority (P0/P1/P2), wave_number, status, depends_on (JSON array)
   - Status enums with clear state machine transitions

2. **As a developer, I want Alembic migrations for all models**, so that schema changes are versioned and reproducible.
   - Migration creates all three tables with proper indexes and foreign keys
   - `uv run alembic upgrade head` succeeds on fresh SQLite database
   - `uv run alembic downgrade -1` cleanly reverses

3. **As a developer, I want a project registration seed script**, so that I can quickly register the target project.
   - `POST /api/v1/projects` endpoint (create only — full CRUD in F-002b)
   - Script or CLI command: `uv run python -m app.cli register --name "my-project" --repo-url "..." --worktree-root "..."`
   - Validates repo exists and is a git repository

**Interface Contract (produces)**:
- ORM models: `Project`, `AgentSession`, `Task` with SQLAlchemy 2.0 mapped columns
- Enums: `SessionStatus` (pending, queued, running, completed, failed, cancelled), `TaskStatus`, `Priority`
- State machine: valid transitions documented (e.g., pending → queued → running → completed|failed)

**Definition of Done**: All three models defined, migration creates tables on SQLite, project can be registered via API or CLI.

---

#### F-002b: REST API, Services & Tests

**Goal**: Full CRUD endpoints for all models with service-layer architecture, multi-project selection, and integration tests.

**Stories**:

1. **As a developer, I want full CRUD REST endpoints for Projects, Sessions, and Tasks**, so that the frontend and CLI tools can manage orchestrator state.
   - `POST/GET/PATCH/DELETE /api/v1/projects`
   - `POST/GET/PATCH /api/v1/sessions` (no delete — sessions are historical)
   - `POST/GET/PATCH /api/v1/tasks` with filtering by project, wave, status
   - Pydantic schemas per lifecycle: Base → Create → Update → Response
   - Proper error responses (404, 422) with consistent error schema

2. **As a developer, I want service-layer business logic separated from route handlers**, so that the codebase follows the stack pack's layered architecture.
   - ProjectService, SessionService, TaskService
   - Routes call services, services call ORM
   - All business rules (e.g., valid status transitions) live in services
   - `PATCH /api/v1/projects/{id}/activate` sets active project (deactivates previous)
   - `GET /api/v1/projects/active` returns currently active project
   - All session/task endpoints filter by active project by default

3. **As a developer, I want integration tests for all CRUD endpoints**, so that regressions are caught early.
   - Async test fixtures (NullPool, rollback, AsyncClient)
   - Tests for success and error paths (404, 422, invalid state transitions)
   - Test project activation/deactivation

**Interface Contract (produces)**:
- REST endpoints: full paths, request/response Pydantic schemas, error schema
- Services: `ProjectService.activate(id)`, `SessionService.create(...)`, `TaskService.list(project_id, wave?, status?)`
- Active project filter: all list endpoints accept optional `project_id` param, default to active project

**Definition of Done**: All CRUD endpoints return correct data, service layer handles business logic, multi-project selection works, tests pass.

---

### Group 3: Execution

#### F-003: Agent Session Spawning & Scheduling

**Goal**: Spawn a Claude Code session in an isolated tmux + git worktree environment via API and CLI, with rate-limit-aware scheduling.

**Stories**:

1. **As a developer, I want git worktree creation and cleanup for each agent session**, so that agents work in isolated branches without interference.
   - Creates worktree at `{worktree_root}/.worktrees/{session_id}`
   - Checks out a new branch: `agent/{session_id}`
   - Cleanup removes worktree when session completes or is cancelled
   - Resource check before creation: refuse if max worktrees exceeded or disk below threshold

2. **As a developer, I want to spawn a Claude Code process in a named tmux session**, so that agent execution is isolated and observable.
   - `tmux new-session -d -s {session_name} "claude -p '{task_prompt}' --worktree {path}"`
   - Session name pattern: `aod-{project}-{session_id}`
   - `POST /api/v1/sessions/spawn` with project_id, task_id, agent_type
   - Creates worktree, spawns tmux session, returns session info
   - Validates: project exists, task is unassigned, agent_type is supported, resources available

3. **As a developer, I want a rate-limit-aware session scheduler**, so that spawning respects agent provider concurrency limits.
   - Sessions enter `queued` status when spawn is requested but concurrency limit reached
   - Scheduler dequeues and spawns when a slot opens (session completes/fails/cancels)
   - Concurrent limits configurable per agent_type in `.aod-orchestrator.toml`
   - CLI: `aod-orch spawn --task-id {id}` and `aod-orch status` for headless operation

**Interface Contract (produces)**:
- `POST /api/v1/sessions/spawn` → `SessionResponse` (includes queue position if queued)
- CLI commands: `aod-orch spawn`, `aod-orch status`, `aod-orch list`
- tmux session naming: `aod-{project_name}-{session_id}`
- Worktree path: `{worktree_root}/.worktrees/{session_id}`
- Branch naming: `agent/{session_id}`
- Event: `session.spawned`, `session.queued` (for downstream WebSocket)

**Definition of Done**: API call or CLI command spawns Claude in tmux with worktree isolation, scheduler queues sessions at concurrency limits, resource checks prevent overcommitment.

---

#### F-004: Session Lifecycle & Driver Abstraction

**Goal**: Cancel stuck sessions, retry failed ones, persist full output, detect context warnings, and establish the pluggable driver abstraction with background monitoring.

**Stories**:

1. **As a user, I want to cancel a running agent session**, so that I can stop stuck or misbehaving agents without killing tmux manually.
   - `POST /api/v1/sessions/{id}/cancel` sends interrupt to tmux session
   - Graceful shutdown: sends `C-c`, waits 5s, then kills if still running
   - Session status transitions to `cancelled`
   - Worktree is preserved (not cleaned up) for inspection
   - CLI: `aod-orch cancel {session_id}`

2. **As a user, I want to retry a failed or cancelled session**, so that transient failures don't require manual re-setup.
   - `POST /api/v1/sessions/{id}/retry` spawns a new session with the same task and config
   - Reuses existing worktree (or creates fresh one if corrupted)
   - Links new session to original (`retry_of` field) for history tracking
   - Subject to rate-limit scheduler (enters queue if at limit)

3. **As a user, I want full session output persisted to disk**, so that I can review agent work after tmux sessions end.
   - Capture full tmux pane output on session completion (not just last N lines)
   - Store as files on disk at `{project_root}/.orchestrator/logs/{session_id}.log`
   - DB stores file path reference
   - `GET /api/v1/sessions/{id}/logs` returns full output

4. **As a developer, I want a Claude driver abstraction with a pluggable registry**, so that adding new agents later is straightforward.
   - `AgentDriver` protocol/ABC: `spawn(task, worktree_path) -> process_info`, `check_status(session) -> status`, `get_output(session) -> str`
   - `ClaudeDriver` implements using `claude -p`
   - Driver registry maps agent_type string → driver class

5. **As a developer, I want a background poller that monitors all active tmux sessions and detects context warnings**, so that status updates and alerts happen automatically.
   - Async background task (started in lifespan) polls every 3s
   - Updates session status, captures output on completion
   - Handles tmux session crashes gracefully (marks as failed)
   - Scans tmux output for context limit indicators (e.g., "conversation compressed", "context window")
   - Surface warning in session status: `context_warning: true`
   - Emits events for downstream WebSocket: `session.status_changed`, `session.context_warning`
   - Applies to ALL sessions including governance sessions (not just build sessions)

**Interface Contract (produces)**:
- `POST /api/v1/sessions/{id}/cancel` → `SessionResponse`
- `POST /api/v1/sessions/{id}/retry` → `SessionResponse`
- `GET /api/v1/sessions/{id}/logs` → plain text output
- `AgentDriver` protocol: documented ABC for future drivers
- Events emitted: `session.status_changed`, `session.context_warning`, `session.completed`, `session.failed`
- Log file path convention: `.orchestrator/logs/{session_id}.log`

**Definition of Done**: Cancel gracefully stops sessions, retry re-spawns with same config, full output persisted to disk, driver abstraction exists with Claude implementation, background poller monitors all sessions and detects context warnings.

---

### Group 4: Dashboard

#### F-005: Dashboard Core with WebSocket

**Goal**: React dashboard with sessions panel, task board, session output viewer, spawn modal, and WebSocket live updates — the primary monitoring interface for the swarm.

**Stories**:

1. **As a user, I want a Sessions panel showing all active and recent agent sessions**, so that I can see what my agent swarm is doing at a glance.
   - List view with: agent type, task description, status badge, duration, worktree branch, queue position (if queued)
   - Color-coded status: running (blue), completed (green), failed (red), pending (gray), cancelled (yellow), queued (orange)
   - Context warning indicator on sessions approaching token limits

2. **As a user, I want a Task Board showing tasks organized by status**, so that I can see overall progress across waves.
   - Columns: Backlog, In Progress, Completed, Failed
   - Cards show: title, priority badge, wave number, assigned agent (if any)
   - Filter by wave number

3. **As a user, I want to click a session to see its live output**, so that I can observe what an agent is doing without switching to a terminal.
   - Session detail panel with scrollable output area
   - Output fetched from backend (live tmux capture or persisted logs)
   - Auto-scroll to bottom with "follow" toggle

4. **As a user, I want to spawn, cancel, and retry agent sessions from the dashboard**, so that I don't need curl or the CLI.
   - "New Session" button → modal with task and agent type selectors
   - Spawns via `POST /api/v1/sessions/spawn`
   - Cancel and retry buttons on session cards
   - Queue position visible for queued sessions

5. **As a user, I want WebSocket-based live updates for session status changes**, so that the dashboard reflects reality without polling delay.
   - WebSocket endpoint at `/ws/events`
   - Backend publishes events on session status transitions and context warnings
   - Frontend subscribes on mount, updates TanStack Query cache on message
   - Graceful fallback to polling if WebSocket disconnects

**Interface Contract (consumes)**:
- All REST endpoints from F-002b
- Events from F-004: `session.status_changed`, `session.context_warning`, `session.completed`, `session.failed`

**Interface Contract (produces)**:
- WebSocket client connection pattern (for reuse by F-009, F-010b)
- TanStack Query key factory: `sessionKeys`, `taskKeys`, `projectKeys`
- Dashboard layout: sidebar + main panel + detail drawer

**Definition of Done**: Dashboard shows sessions list and task board, session output viewable, sessions can be spawned/cancelled/retried from UI, WebSocket delivers live updates with polling fallback.

---

### Group 5: Lifecycle

#### F-007: GitHub Issues + Lifecycle Engine

**Goal**: Read GitHub Issues, parse ICE scores, cache locally, map issues to AOD lifecycle stages, and display on dashboard with stage indicators.

**Stories**:

1. **As a user, I want the orchestrator to read GitHub Issues for a project**, so that my backlog drives agent work.
   - `GET /api/v1/projects/{id}/issues` fetches issues via `gh` CLI or GitHub API
   - Parses ICE scores from issue body (Impact/Confidence/Effort format)
   - Caches issues in DB to avoid rate limits (refresh on demand or on interval)
   - Filters by label (e.g., `stage:discovery`, `type:idea`)

2. **As a user, I want a lifecycle engine that maps issues to AOD stages**, so that the orchestrator tracks where each item is in the pipeline.
   - Stage detection from GitHub labels: `stage:discovery`, `stage:define`, `stage:plan`, `stage:build`, `stage:done`
   - Stage model: IssueLifecycle (issue_number, current_stage, stage_history JSON, timestamps)
   - API endpoint to advance stage: `POST /api/v1/lifecycle/{issue}/advance`
   - Methodology abstraction: lifecycle stages defined in config, not hardcoded (AOD stages as default)

3. **As a user, I want issues displayed on the dashboard sorted by ICE score with lifecycle stage indicators**, so that I can see priorities and progress.
   - Issues panel with sortable columns: title, ICE score, stage, labels
   - Visual indicator for current lifecycle stage (color-coded badge)
   - Click to view full issue body in a detail panel
   - "Refresh" button triggers re-fetch from GitHub with last-synced timestamp

4. **As a user, I want to refresh issues on demand and see sync status**, so that I know the dashboard reflects current GitHub state.
   - Last-synced timestamp displayed
   - Sync errors surfaced (e.g., rate limit, auth failure)
   - Auto-refresh interval configurable in `.aod-orchestrator.toml`

**Interface Contract (produces)**:
- `GET /api/v1/projects/{id}/issues` → `IssueResponse[]` (with ICE scores and stage)
- `POST /api/v1/lifecycle/{issue}/advance` → `LifecycleResponse`
- `IssueLifecycle` model with stage history
- Lifecycle stage enum (configurable, AOD default: discovery, define, plan, build, deliver, document, done)

**Definition of Done**: Issues load from GitHub, display with ICE scores and stage indicators, lifecycle engine tracks stages, cache avoids rate limits, manual refresh works.

---

#### F-007a: Task Creation & Spawn Task Selector

**Goal**: Enable task creation directly from the Task Board UI and wire the Spawn Modal's task selector to pending tasks, unblocking the full create-task → spawn-session E2E flow.

**Stories**:

1. **As a user, I want to create tasks directly from the Task Board UI**, so that I can quickly add ad-hoc work items without needing to use the API or run the full `/aod.tasks` workflow.
   - "Create Task" button on the Task Board page
   - Opens a modal with fields: title (required), description, project (pre-selected if active project exists), wave (optional), agent type (optional)
   - On submit, calls `POST /api/v1/tasks` and invalidates the task list query to refresh the board

2. **As a user, I want the new task to appear on the Task Board immediately after creation**, so that I have confidence the task was saved and can act on it.
   - TanStack Query cache invalidation on `taskKeys` after successful POST
   - New task appears in the Backlog column with correct metadata
   - Toast/notification confirms creation success or surfaces API errors

3. **As a user, I want the Spawn Session modal to include a task selector dropdown**, so that I can associate a session with a specific pending task instead of a hardcoded `task_id: 0`.
   - When a project is selected in the Spawn Modal, fetch pending tasks for that project via `GET /api/v1/tasks?project_id={id}&status=pending`
   - Task dropdown populates with pending tasks (title + wave badge)
   - Selected task ID is passed to `POST /api/v1/sessions/spawn`

4. **As a user, I want guidance when no pending tasks exist for the selected project**, so that I know to create a task before spawning a session.
   - When the task dropdown is empty, display an inline message: "No pending tasks. Create a task first."
   - Optionally link/button to open the Create Task modal directly from the Spawn Modal

**Interface Contract (consumes)**:
- `POST /api/v1/tasks` from F-002b
- `GET /api/v1/tasks` with query params from F-002b
- `POST /api/v1/sessions/spawn` from F-003
- TanStack Query key factory (`taskKeys`) from F-005
- Dashboard layout and modal patterns from F-005

**Interface Contract (produces)**:
- `CreateTaskModal` component (reusable from Task Board and Spawn Modal)
- Enhanced `SpawnModal` with task selector dropdown
- Task creation → spawn session E2E flow

**Definition of Done**: Tasks can be created from the Task Board UI via modal, new tasks appear immediately, Spawn Modal includes a task selector populated from pending tasks, empty state guides user to create a task first.

---

#### F-007b: Project Management UI

**Goal**: Enable full project lifecycle management from the dashboard — create projects with GitHub repo linking, switch the active project, edit project settings, and delete empty projects — so users never need to use curl or the CLI to manage projects.

**Stories**:

1. **As a user, I want to create a project from the dashboard**, so that I can register a new GitHub repo to orchestrate without using the CLI or API.
   - "Add Project" button in the Sidebar projects list (or a dedicated Projects page)
   - Opens a modal with fields: name (required, max 100 chars), GitHub owner (optional), GitHub repo (optional), repo URL (optional), worktree root (required for spawning — inline hint: "Path to a git repo. Required to spawn agent sessions."), AOD kit path (optional)
   - On submit, calls `POST /api/v1/projects` and invalidates `projectKeys.lists()` to refresh all project dropdowns
   - First project created is auto-activated
   - On success, modal closes and the new project appears in the sidebar

2. **As a user, I want to switch the active project from the sidebar**, so that I can quickly change context between projects without navigating to a settings page.
   - Click a project in the sidebar to activate it
   - Calls `PATCH /api/v1/projects/{id}/activate`
   - Active project is visually highlighted
   - Switching active project refreshes all project-scoped views (Task Board, Sessions, Issues, Spawn Modal)
   - Cache invalidation on `projectKeys`, `taskKeys`, `sessionKeys`, and `issueKeys` after activation

3. **As a user, I want to edit a project's settings**, so that I can update the GitHub repo link or worktree path after initial setup.
   - Click an edit icon on the active project (or project list item)
   - Opens a modal pre-filled with current values
   - On submit, calls `PATCH /api/v1/projects/{id}` with changed fields only
   - Validates name is non-empty and ≤100 chars
   - Validates `worktree_root` points to a valid git repository when provided (backend returns 422 if path is not a git repo)
   - On success, modal closes and project details refresh

4. **As a user, I want to delete an empty project**, so that I can clean up test or abandoned projects.
   - Delete button with confirmation dialog ("This will permanently delete the project. Are you sure?")
   - Calls `DELETE /api/v1/projects/{id}`
   - Backend returns 409 if project has child sessions or tasks — surface this as an inline error: "Cannot delete project with existing tasks or sessions"
   - On success, project disappears from sidebar; if it was active, the next project (if any) becomes active
   - On empty state (no projects), show "Add your first project" prompt

**Interface Contract (consumes)**:
- `POST /api/v1/projects` from F-002b (create)
- `GET /api/v1/projects` from F-002b (list)
- `GET /api/v1/projects/active` from F-002b (active project)
- `PATCH /api/v1/projects/{id}` from F-002b (update)
- `PATCH /api/v1/projects/{id}/activate` from F-002b (activate)
- `DELETE /api/v1/projects/{id}` from F-002b (delete, 409 on children)
- TanStack Query key factory (`projectKeys`) from F-005
- Dashboard layout, sidebar, and modal patterns from F-005

**Interface Contract (produces)**:
- `CreateProjectModal` component (reusable for onboarding flow)
- `EditProjectModal` component
- `useCreateProject()` mutation hook
- `useUpdateProject()` mutation hook
- `useActivateProject()` mutation hook
- `useDeleteProject()` mutation hook
- `ProjectCreateData` and `ProjectUpdateData` TypeScript types
- Active project switching triggers cross-domain cache invalidation

**Integration with existing features**:
- **F-007a** (Task Creation): Project dropdown in CreateTaskModal auto-refreshes when projects change
- **F-007** (Issues): Issues panel re-fetches when active project switches
- **SpawnModal**: Project dropdown reflects new/edited/deleted projects immediately via shared `projectKeys` cache
- **Sidebar**: Active project indicator syncs with all views
- **F-003** (Spawning): The spawn endpoint requires `worktree_root` to point to a valid git repository — without it, `git worktree add` fails with a 500 error. Create/Edit modals must surface this requirement with inline guidance, and the backend should validate the path is a git repo on save (return 422 if not). The Spawn Modal should also show a clear error when the active project has no `worktree_root` configured, directing the user to edit the project first.

**Definition of Done**: Projects can be created, activated, edited, and deleted from the UI. All project dropdowns across the dashboard refresh on changes. Delete is blocked when children exist. Backend validates `worktree_root` is a valid git repo on create/update (422 if not). Spawn Modal shows a clear error when the active project has no `worktree_root`, directing the user to edit the project. E2E test: create project with `worktree_root` → create task → spawn session succeeds. Tests cover all CRUD operations and cross-component cache invalidation.

---

#### F-008: Stage Gates & Governance Triggers

**Goal**: Enforce governance gates at each lifecycle transition and trigger governance commands from the dashboard.

**Stories**:

1. **As a user, I want stage gates that enforce governance requirements**, so that issues can't skip required sign-offs.
   - Define → Plan requires: `.aod/spec.md` exists with PM sign-off
   - Plan → Build requires: `.aod/tasks.md` exists with triple sign-off
   - Build → Deliver requires: all tasks in completed/merged status
   - API returns clear error with unmet conditions when gate fails
   - Gate rules configurable per methodology (AOD rules as default)

2. **As a user, I want to trigger governance commands for an issue from the dashboard**, so that I can run `/aod.define`, `/aod.spec`, etc. without switching to a terminal.
   - "Run Governance" action spawns a dedicated governance session in tmux
   - Governance session runs the appropriate AOD command for the current stage
   - Session output shows governance progress (sign-off requests, approvals)
   - Stage auto-advances when governance session completes successfully

3. **As a user, I want governance sessions to be monitored like build sessions**, so that context warnings and failures are caught.
   - Governance sessions use the same AgentDriver, poller, and event system as build sessions
   - Tagged as `session_type: governance` vs `session_type: build`
   - Context warnings especially critical for governance (Triad reviews consume significant context)
   - Dashboard distinguishes governance sessions visually

**Interface Contract (consumes)**:
- Lifecycle engine from F-007
- Session spawning from F-003
- Background poller from F-004

**Interface Contract (produces)**:
- `POST /api/v1/lifecycle/{issue}/advance` now enforces gates (extends F-007)
- Gate check API: `GET /api/v1/lifecycle/{issue}/gate-status` → `{ met: bool, conditions: [...] }`
- Governance session spawn: `POST /api/v1/governance/{issue}/run` → `SessionResponse`
- Session type tag: `governance` | `build`

**Definition of Done**: Stage gates enforce sign-off requirements, governance commands trigger from dashboard as monitored sessions, stages advance on successful governance completion.

---

### Group 6: Governance

#### F-009: Governance & Sign-off Panel

**Goal**: Dashboard panel showing Triad sign-off status for all governance artifacts across the swarm, with ability to trigger reviews.

**Stories**:

1. **As a user, I want to see sign-off status for each governance artifact**, so that I know which approvals are pending across all my features.
   - Parse `.aod/spec.md`, `plan.md`, `tasks.md` from project worktree for sign-off blocks
   - Display: artifact name, required reviewers, approval status per reviewer
   - Status: pending, approved, changes-requested

2. **As a user, I want a Governance Panel in the dashboard showing all artifacts and their approval state**, so that I have a single view of governance health across the swarm.
   - Panel grouped by feature/issue
   - Traffic light indicators: green (all approved), yellow (pending), red (changes requested)
   - Summary counts: N features approved, N pending, N blocked

3. **As a user, I want to trigger Triad reviews from the dashboard**, so that I don't have to manually invoke review agents.
   - "Request Review" button per artifact
   - Spawns PM, Architect, and/or Team-Lead review sessions (per governance rules)
   - Review results update the governance panel via WebSocket events
   - Reviews use the rate-limit-aware scheduler (queued if at capacity)

**Interface Contract (consumes)**:
- WebSocket from F-005
- Session spawning from F-003
- Lifecycle stages from F-007
- Gate status from F-008

**Definition of Done**: Governance panel displays sign-off status parsed from AOD artifacts, reviews can be triggered from UI, panel updates in real-time via WebSocket.

---

### Group 7: Orchestration

#### F-010a: Parallel Session Spawning

**Goal**: Spawn multiple agent sessions in parallel for independent tasks, verify they don't interfere, and track group progress.

**Stories**:

1. **As a user, I want to spawn multiple agent sessions simultaneously**, so that independent tasks execute in parallel.
   - `POST /api/v1/sessions/spawn-batch` accepts array of task assignments
   - Each task gets its own worktree and tmux session
   - Subject to rate-limit scheduler (excess sessions queued)
   - Validates: no circular dependencies, all tasks exist, resources available

2. **As a user, I want batch session status tracked as a group**, so that I know when a set of parallel tasks is complete.
   - Batch model: id, session_ids[], status (running/completed/partial_failure/failed)
   - Batch completes when all sessions complete; partial_failure if some fail
   - `GET /api/v1/batches/{id}` returns aggregate status
   - Dashboard shows batch grouping in sessions panel

**Interface Contract (produces)**:
- `POST /api/v1/sessions/spawn-batch` → `BatchResponse`
- `GET /api/v1/batches/{id}` → `BatchResponse` with session statuses
- Batch model: `SessionBatch` (id, status, session_ids, created_at, completed_at)

**Definition of Done**: Batch spawn creates parallel sessions with worktree isolation, batch status tracks group progress, sessions don't interfere with each other, rate limits respected.

---

#### F-010b: Wave Pipeline & Pipeline Dashboard

**Goal**: Parse `agent-assignments.md`, dispatch agents in sequential waves, auto-advance between waves, enforce architect checkpoints, and visualize the full pipeline.

**Stories**:

1. **As a user, I want the orchestrator to parse `agent-assignments.md` into executable waves**, so that tasks run in the correct order with proper dependencies.
   - Parser reads wave definitions, task assignments, and dependency chains
   - Produces: `Wave[]` with tasks, assigned agent types, and dependency graph
   - Validates: no circular dependencies, all referenced tasks exist

2. **As a user, I want to start orchestration and have waves execute sequentially with parallel tasks per wave**, so that dependent work happens in order.
   - `POST /api/v1/orchestrate/{project}/start` parses assignments and begins Wave 1
   - Each wave spawns tasks as a batch (F-010a)
   - Wave completes when batch completes
   - If all succeeded: auto-advance to next wave (or pause for approval if configured)
   - If any failed: pause and surface failures for review
   - Failure policy configurable: after N retries, escalate with options (skip task, abort wave, manual fix)

3. **As a user, I want architect checkpoints at P0/P1 task boundaries**, so that critical work gets reviewed before less critical work begins.
   - After all P0 tasks complete: spawn architect review session before P1 tasks
   - Checkpoint status shown in dashboard (pending review, approved, blocked)
   - Checkpoint review gates next wave

4. **As a user, I want wave and orchestration state persisted**, so that orchestration survives restarts.
   - Wave model: id, project_id, wave_number, status (pending/running/completed/failed/paused), started_at, completed_at
   - WaveTask join: wave_id, task_id, session_id, batch_id
   - Orchestration resumes from last completed wave on restart

5. **As a user, I want a pipeline dashboard showing all waves, checkpoints, and overall progress**, so that I can see the big picture.
   - Visual pipeline: Wave 1 → Checkpoint → Wave 2 → Checkpoint → Wave 3 → Done
   - Per-wave: task count, completion %, duration, failure count
   - Overall: total progress bar, elapsed time, blocked items
   - Click wave → shows tasks and sessions; click checkpoint → shows architect review
   - Failed sessions highlighted in red; blocked checkpoints visually prominent
   - "Resume" action on paused waves after failures are addressed

**Interface Contract (consumes)**:
- Batch spawning from F-010a
- Session lifecycle from F-004
- Dashboard WebSocket from F-005
- Gate checks from F-008

**Definition of Done**: Waves parse from agent-assignments.md, sequential wave execution with parallel tasks per wave, auto-advance with failure handling, architect checkpoints gate boundaries, state persists, pipeline dashboard visualizes everything.

---

### Group 8: Integration

#### F-011: PR Workflow & Artifact Merge-Back

**Goal**: Auto-create PRs from completed agent sessions, review diffs in dashboard, merge with cleanup, and sync governance artifacts back from worktrees.

**Stories**:

1. **As a user, I want the orchestrator to auto-create a PR when an agent session completes successfully**, so that completed work enters the review pipeline without manual git commands.
   - Detects session completion with exit code 0
   - Runs `gh pr create` from the agent's worktree branch targeting the feature branch
   - PR title and description generated from the task description in `tasks.md` (not AI-generated — uses the structured task data already available)
   - PR URL stored in session record

2. **As a user, I want to review agent PRs in the dashboard with a diff viewer**, so that I don't have to context-switch to GitHub for every agent's output.
   - PR detail panel showing: diff stats, changed files list, PR description
   - Inline diff viewer (unified format) for changed files via `git diff` parsing
   - Link to full PR on GitHub for complex reviews or commenting

3. **As a user, I want to merge an approved agent PR from the dashboard**, so that I can integrate completed work without leaving the orchestrator.
   - "Merge" button (squash merge by default)
   - Post-merge: clean up worktree and agent branch
   - Update task status to "merged" and session status to "integrated"
   - Conflict detection: surface merge conflicts before attempting merge
   - Semantic conflict pre-check: warn if other merged PRs from the same batch touched the same files

4. **As a user, I want governance artifacts copied back from worktrees to the main branch**, so that spec/plan/task updates from governance sessions are preserved.
   - After governance session completes, detect changes to `.aod/` directory
   - Auto-copy `.aod/spec.md`, `plan.md`, `tasks.md` back to main working tree
   - Conflict resolution: prompt user if main copy has diverged
   - Copy-back paths configurable per project

**Definition of Done**: PRs auto-created from completed sessions with task-based descriptions, reviewable with diff viewer, mergeable with cleanup and conflict detection, governance artifacts sync back.

---

### Group 9: Agent Interface

#### F-012: CLI & MCP — Agent-Driven Orchestration

**Goal**: Provide CLI and MCP interfaces to the orchestrator so that a coding agent (e.g., Claude Code with Opus) can act as **team lead** — reading tasks, spawning worker sessions, monitoring progress, reacting to failures, and coordinating wave execution — enabling fully autonomous multi-agent orchestration with human oversight via the dashboard and governance gates.

**Why this matters**: The dashboard is built for humans watching agents. The CLI and MCP are built for agents driving agents. This is the unlock that turns the orchestrator from a monitoring tool into an autonomous execution platform. A lead agent reading `.aod/tasks.md` can spawn a swarm of workers, coordinate dependencies between them, retry failures with adjusted prompts, and advance through waves — all while governance gates ensure quality and the dashboard gives the human full visibility.

**Architecture**:

```
You → Claude Code (Opus) ← lead agent / team lead session
       │
       ├─ reads .aod/tasks.md → decides what to spawn
       ├─ aod spawn --agent claude --task "Implement auth" --issue 42
       ├─ aod spawn --agent gemini --task "Write API tests" --issue 42
       ├─ aod status --watch → monitors all sessions
       ├─ aod logs --session 3 → diagnoses failure, adjusts prompt
       ├─ aod retry --session 3 → retries with refined prompt
       └─ aod wave start --project 1 → kicks off next wave

Orchestrator (FastAPI + SQLite) ← running as background service
  ├─ REST API ← all interfaces connect here
  ├─ CLI (aod) ← lead agent calls via Bash tool
  ├─ MCP Server ← lead agent calls as native tool
  └─ tmux sessions ← worker agents (full agents, NOT subagents)
       ├─ claude code (Opus) → task 1 (can use subagents)
       ├─ gemini CLI → task 2 (via GeminiDriver)
       └─ claude code (Opus) → task 3 (can use subagents)
```

**Critical design point**: Spawned worker sessions are **top-level agent processes** in their own tmux sessions, not Claude Code subagents. This means workers retain full tool access, can spawn their own subagents, and have their own complete context window. The orchestrator is Python infrastructure code — it manages process lifecycle, not inference.

**Stories**:

1. **As a lead agent, I want a CLI tool (`aod`) that wraps the orchestrator REST API**, so that I can drive orchestration from a Claude Code session via the Bash tool.
   - `aod spawn --project <id> --task <id> --agent <type>` → spawns session, returns session ID and status
   - `aod status [--project <id>] [--watch]` → lists sessions with status, optional continuous polling
   - `aod logs --session <id> [--tail <n>]` → retrieves session output (live or persisted)
   - `aod cancel --session <id>` → graceful cancel with output capture
   - `aod retry --session <id>` → retries failed session with retry chain
   - `aod wave start --project <id>` → starts next pending wave from F-010b
   - `aod wave status --project <id>` → shows wave pipeline progress
   - `aod gate status --project <id> --issue <num>` → shows gate conditions (met/unmet)
   - `aod lifecycle advance --project <id> --issue <num>` → advances stage if gates met
   - All commands output structured JSON (`--json` flag) for agent parsing, human-readable table by default
   - Exit codes: 0 success, 1 API error, 2 validation error — agents react to exit codes
   - Implemented as a Python CLI (`uv run aod`) using `click` or `typer`, calling the REST API via `httpx`

2. **As a lead agent, I want an MCP server that exposes orchestrator operations as tools**, so that I can interact with the orchestrator natively without shelling out to a CLI.
   - MCP tools mirror CLI commands: `spawn_session`, `list_sessions`, `get_logs`, `cancel_session`, `retry_session`, `start_wave`, `get_wave_status`, `get_gate_status`, `advance_lifecycle`
   - Each tool returns structured JSON matching the REST API response schemas
   - MCP server connects to the orchestrator REST API (thin client, no direct DB access)
   - Configurable via Claude Code's MCP settings: `"aod-orchestrator": { "command": "uv run aod-mcp", "args": ["--api-url", "http://localhost:8000"] }`
   - MCP resources expose read-only views: `tasks://project/{id}`, `sessions://project/{id}`, `waves://project/{id}`

3. **As a lead agent, I want to orchestrate a full wave pipeline autonomously**, so that I can read tasks, spawn workers, monitor completion, and advance through waves without human intervention.
   - Lead agent reads `.aod/tasks.md` and `agent-assignments.md` to understand the plan
   - Spawns Wave 1 tasks in parallel via CLI/MCP
   - Polls session status until wave completes
   - On failure: reads logs, determines if task should be retried with adjusted prompt or escalated to human
   - On wave completion: checks for architect checkpoint, triggers governance review if needed
   - Auto-advances to next wave when checkpoint clears
   - Surfaces blocking issues to human via dashboard events (the human sees real-time updates)
   - Governance gates remain enforced — the lead agent cannot bypass sign-offs

4. **As a user, I want to see lead agent activity in the dashboard**, so that I have full visibility into what the lead agent is doing on my behalf.
   - Lead agent session visible in sessions panel (tagged as `session_type: lead` or identifiable by task description)
   - Wave progress visible in pipeline dashboard (F-010b) regardless of whether initiated by human or lead agent
   - All governance gates and sign-offs still require human approval in the dashboard (or governance agent approval per current flow)
   - Human can cancel lead agent session or any worker session from dashboard at any time

5. **As a developer, I want documentation and prompt templates for the lead agent pattern**, so that I can configure a Claude Code session to act as team lead effectively.
   - Lead agent prompt template: reads tasks, spawns workers, monitors, coordinates
   - Example CLAUDE.md additions for projects using the lead agent pattern
   - Troubleshooting guide: common issues (API not running, concurrency limits, stale tasks)
   - Security considerations: `--dangerously-skip-permissions` on worker sessions, localhost-only for MVP

**Interface Contract (consumes)**:
- All REST API endpoints from F-001 through F-010b
- Wave pipeline API from F-010b (`POST /orchestrate/{project}/start`, `GET /waves`)
- Gate status API from F-008 (`GET /lifecycle/{issue}/gate-status`)
- Session spawn/cancel/retry from F-003, F-004
- WebSocket events from F-005 (for MCP server event forwarding)

**Interface Contract (produces)**:
- CLI binary: `aod` (installed via `uv run aod` or `pip install aod-orchestrator[cli]`)
- MCP server: `aod-mcp` (installed via `uv run aod-mcp`)
- CLI commands: spawn, status, logs, cancel, retry, wave start/status, gate status, lifecycle advance
- MCP tools: spawn_session, list_sessions, get_logs, cancel_session, retry_session, start_wave, get_wave_status, get_gate_status, advance_lifecycle
- MCP resources: tasks://, sessions://, waves://
- Lead agent prompt template in docs/
- JSON output format for all CLI commands (`--json` flag)

**Definition of Done**: CLI tool wraps all orchestrator API operations with JSON output, MCP server exposes equivalent tools, lead agent can autonomously orchestrate a wave pipeline (spawn → monitor → retry → advance), all activity visible in dashboard, governance gates still enforced, documentation and prompt templates provided. E2E test: lead agent session reads tasks, spawns 3 workers via CLI, monitors completion, retries one failure, advances wave.

---

## How to Execute Each Feature

Each feature is one AOD item. Use `/aod.discover --seed` to fast-track it into the backlog, then run the full lifecycle in a dedicated session.

```
# 1. Capture the feature (from this project — product-led-spec-kit)
#    Copy the feature goal and stories into the discover prompt
#    --seed skips ICE prompts, evidence, and PM validation
/aod.discover --seed <feature goal summary>

# 2. In the orchestrator project, open a new session
claude

# 3. Run the governed lifecycle
/aod.define <feature goal — paste from this guide>
/aod.spec    # MUST include Interface Contract section
/aod.project-plan
/aod.tasks
/aod.build
/aod.deliver
```

### Interface Contract Discipline

**Critical for cross-session success**: Each feature's spec (`/aod.spec`) MUST include an Interface Contract section that documents:

1. **Consumes**: Exact API paths, Pydantic schema names, event names, and DB models from dependencies
2. **Produces**: Exact API paths, schema names, events, and models this feature creates
3. **Conventions**: Naming patterns, file paths, and configuration keys used

The agent building feature N reads the Interface Contract from feature N-1's spec to understand the actual implementation. Without this, cross-session integration failures are inevitable.

### Between Features

- **Report back**: File issues on `product-led-spec-kit` for stack pack bugs, missing conventions, or governance friction
- **Update this guide**: Mark completed features, add lessons learned
- **Validate**: Run the app after each feature to confirm cumulative functionality
- **Commit**: Each feature produces a PR on its own branch (`NNN-feature-name`)
- **Integration test**: After features with many dependents (F-002b, F-003, F-004), manually verify the interface contracts hold

---

## Feature Completion Tracker

| ID | Feature | Phase | Status | Branch | Issue | Notes |
|----|---------|-------|--------|--------|-------|-------|
| F-001 | Project Skeleton & Health Check | 1 | Not started | | | |
| F-002a | Domain Models & Migrations | 2 | Not started | | | |
| F-002b | REST API, Services & Tests | 2 | Not started | | | |
| F-003 | Agent Session Spawning & Scheduling | 3 | Not started | | | |
| F-004 | Session Lifecycle & Driver Abstraction | 3 | Not started | | | |
| F-005 | Dashboard Core with WebSocket | 4 | Not started | | | |
| F-007 | GitHub Issues + Lifecycle Engine | 5 | Not started | | | |
| F-007a | Task Creation & Spawn Task Selector | 4 | Not started | | | |
| F-007b | Project Management UI | 4 | Not started | | | |
| F-008 | Stage Gates & Governance Triggers | 5 | Not started | | | |
| F-009 | Governance & Sign-off Panel | 6 | Not started | | | |
| F-010a | Parallel Session Spawning | 7 | Not started | | | |
| F-010b | Wave Pipeline & Pipeline Dashboard | 7 | Not started | | | |
| F-011 | PR Workflow & Artifact Merge-Back | 8 | Not started | | | |
| F-012 | CLI & MCP — Agent-Driven Orchestration | 9 | Not started | | | |

---

## Open Questions (Resolve During Features)

| Question | Resolve In | Current Lean |
|----------|-----------|--------------|
| WebSocket vs SSE for live updates? | F-005 | WebSocket (bidirectional, session control) |
| Agent output streaming — live or status only? | F-005 | Live output via tmux capture, polled or streamed |
| Authentication for MVP? | Defer | No — localhost only, add in post-MVP |
| Methodology plugin system? | F-008 | Design interface for extensibility; MVP is AOD-only. Evaluate feasibility of abstracting specialized agents |
| Project name? | F-001 | `aod-orchestrator` (working name) |
| Git submodule vs copied methodology files? | Resolved | Baked in at init; cherry-pick from upstream for updates |
| SQLite busy timeout for concurrent writes? | F-001 | WAL mode + 5s busy timeout; monitor for SQLITE_BUSY in testing |
| tmux `wait-for` vs polling for status? | F-004 | Start with polling (simpler); evaluate event-driven if I/O becomes a concern |

---

## Deferred Features (Post-MVP)

| Feature | Original ID | Reason for Deferral |
|---------|-------------|-------------------|
| Desktop notifications on session completion/failure | FR-09 | Browser tab title changes suffice for MVP; user is at their computer |
| Full-text search across past session logs | FR-10 | `grep` on log files works at MVP scale (<100 sessions) |
| ~~Project switcher in dashboard sidebar~~ | ~~F-006 Story 2~~ | Promoted to F-007b (Project Management UI) — no longer deferred |

---

## Success Criteria

| ID | Criterion | Target |
|----|-----------|--------|
| SC-001 | Stack pack scaffold to running app | < 15 minutes (no Docker required for SQLite mode) |
| SC-002 | Each feature through full AOD lifecycle | Complete governance trail per feature |
| SC-003 | Security patterns enforced | Pydantic validation, async sessions, no raw SQL |
| SC-004 | Cumulative functionality after each feature | App works end-to-end at every milestone |
| SC-005 | Agent spawning works | Claude runs in tmux + worktree via API, CLI, and MCP |
| SC-006 | Dashboard shows real-time state | Sessions, tasks, governance visible with WebSocket updates |
| SC-007 | 12 features deliverable independently | Each feature testable without future features |
| SC-008 | Interface contracts maintained | Each feature spec documents consumed/produced APIs |
| SC-009 | Rate limits respected | Scheduler queues sessions at provider concurrency limits |
| SC-010 | Swarm of 10+ agents manageable | Dashboard, CLI, MCP, and scheduler handle concurrent load |
| SC-011 | Lead agent can drive full wave pipeline | Lead agent spawns workers, monitors, retries failures, advances waves via CLI or MCP |

---

## Troubleshooting

| Issue | Resolution |
|-------|------------|
| `make init` fails | Ensure Python 3.12+, Node.js 20+, and Git are installed |
| `/aod.stack use` says pack not found | Verify `stacks/fastapi-react-local/STACK.md` exists |
| SQLite `SQLITE_BUSY` errors | WAL mode should be enabled; increase busy timeout in config |
| Docker Compose fails (optional PostgreSQL mode) | Ensure Docker Desktop is running; check port conflicts (5432). Not needed for SQLite mode |
| `uv sync` fails | Ensure `uv` is installed (`curl -LsSf https://astral.sh/uv/install.sh \| sh`) |
| tmux sessions not spawning | Ensure tmux is installed (`tmux -V`); check for existing sessions (`tmux ls`); check pty limit (`sysctl kern.tty.ptmx_max`) |
| Alembic migration fails | Check DATABASE_URL in `.env`; ensure database file/server is accessible |
| Governance sign-off loops | Address reviewer feedback, re-submit until APPROVED |
| Sessions stuck in `queued` | Check concurrent session limits in `.aod-orchestrator.toml`; verify running sessions haven't stalled |
| Orphaned worktrees | Restart backend — startup routine prunes orphaned worktrees automatically |
| Context limit warnings | Session approaching token limit; consider splitting task or restarting with narrower scope |
| MCP server not connecting | Ensure orchestrator API is running on expected port; check MCP config in Claude Code settings |
| CLI `aod` command not found | Install via `uv run aod` or ensure `aod-orchestrator[cli]` is installed; check PATH |
| Lead agent not advancing waves | Verify governance gates are met (`aod gate status`); check that architect checkpoint is approved |

---

## Notes

- This guide uses the **public template** repo, not the private `product-led-spec-kit`
- The orchestrator is a **separate project** — `product-led-spec-kit` provides the methodology only
- AOD Kit methodology is baked in during `make init` — cherry-pick from upstream for updates
- Stack pack conventions are enforced through rules files (passive) and `/aod.build` prompt injection (active)
- Core governance agents (PM, Architect, Team-Lead) are **not** affected by stack packs
- Report stack pack issues, governance bugs, or convention gaps back to `product-led-spec-kit`
- **Self-orchestration constraint**: Do not use the orchestrator to orchestrate its own development for MVP. This creates governance recursion that is extremely hard to debug.
