# Consumer Guide — Second Brain MCP Server (TypeScript, Supabase, pgvector, MCP SDK)

**Purpose**: A lightweight MCP server that gives every AI session persistent, cross-project developer memory backed by Supabase pgvector.
**What you're building**: A TypeScript MCP server that captures, embeds, and retrieves developer knowledge (preferences, subscriptions, architectural decisions, patterns, lessons learned) via semantic + full-text hybrid search. Every Claude Code session in every project connects to the same brain. Intake via MCP tools (primary), CLI, and Slack.
**Target user**: Solo developer managing multiple projects who wants persistent AI context across all sessions.
**Key constraints**:
- Supabase free/Pro tier as sole infrastructure (no Docker stacks, no additional services)
- MCP server must work as stdio transport for Claude Code and as remote HTTP for other clients
- Embeddings via Supabase built-in `gte-small` model (free, no API key needed)
- Personal dev tool — single-user, no multi-tenancy

**How to use this guide**: Work through each seed feature in order using the AOD lifecycle. Copy each feature block into `/aod.discover` to create a GitHub Issue, then run `/aod.define` through `/aod.deliver` to implement it.

---

## Prerequisites

- Claude Code installed (`claude` CLI)
- Node.js 20+ and Git installed
- npm (ships with Node.js)
- GitHub CLI (`gh`) installed and authenticated
- A GitHub account with repo creation permissions
- Supabase account ([supabase.com](https://supabase.com) — free tier works)
- Slack workspace with a private channel (for Slack intake)

---

## Phase 1: Clone & Initialize

Navigate to your projects directory (e.g., `~/Projects/` or `~/code/`) — the clone command will create a new subfolder here:

```bash
# Clone the public template
git clone https://github.com/davidmatousek/agentic-oriented-development-kit.git second-brain-mcp
cd second-brain-mcp

# Run interactive setup
make init
```

**When prompted, enter:**

| Prompt | Value |
|--------|-------|
| Project Name | `second-brain-mcp` |
| Description | `Supabase-backed MCP server for persistent developer memory across all projects` |
| GitHub Org | `davidmatousek` |
| GitHub Repo | `second-brain-mcp` |
| AI Agent | `1` (Claude Code) |
| Tech Stack | `Other` (custom stack — TypeScript + Supabase + pgvector) |

> **Note**: Select **Other** when prompted for tech stack — none of the bundled packs (nextjs-supabase, fastapi-react, etc.) match this project. After selecting Other, enter **PostgreSQL** for database and **Supabase** for cloud provider when prompted (no frontend, so Vercel isn't needed).

```bash
# Verify setup
make check
```

**Expected output:**
- All checks pass (green checkmarks)
- No pack active (custom stack)

### Post-Init Verification

Confirm that `make init` replaced all template placeholders:

```bash
# Should return NO results — all placeholders replaced
grep -rn '{{' .aod/memory/constitution.md
```

---

## Phase 2: Create GitHub Repo & Custom Stack Setup

```bash
# Create a GitHub repo (needed for issue tracking)
gh repo create davidmatousek/second-brain-mcp --private --source=. --push

# If you get "Unable to add remote origin" (origin exists from the clone), run:
git remote set-url origin https://github.com/davidmatousek/second-brain-mcp.git
git push -u origin main

# Set up GitHub Projects board (make init ran before the repo existed)
bash -c 'source .aod/scripts/bash/github-lifecycle.sh && aod_gh_setup_board'
```

Open Claude Code in your project directory:

```bash
claude
```

Create the project directory structure by typing this into Claude Code:

```
Create the project directory structure for a TypeScript MCP server with Supabase:
- src/ — MCP server source (tools, resources, prompts)
- supabase/ — migrations, Edge Functions, seed data
- cli/ — CLI tool source
- tests/ — integration and unit tests
- Add a tsconfig.json for ES module TypeScript with strict mode
- Add a .env.example with SUPABASE_URL, SUPABASE_SERVICE_KEY placeholders
```

> **Note**: No stack pack scaffold for this custom stack — the prompt above creates the base structure. Feature-specific files get added as you build each feature through the AOD lifecycle.

---

## Phase 3: Create Supabase Project & Install Dependencies

### 3a: Create Supabase Project

If you don't already have a Supabase project for this:

1. Go to [supabase.com/dashboard](https://supabase.com/dashboard)
2. Click **New Project**
3. Name it `second-brain-mcp`
4. Set a database password (save it — you'll need it later)
5. Choose a region close to you (e.g., `us-east-1`)
6. Click **Create new project** and wait for provisioning (~2 minutes)

Once created, collect these values from the dashboard:

| Value | Where to find it |
|-------|------------------|
| **Project Ref** | Settings → General → Reference ID (e.g., `abcdefghijkl`) |
| **Supabase URL** | Settings → API → Project URL (e.g., `https://abcdefghijkl.supabase.co`) |
| **Service Role Key** | Settings → API → `service_role` key (keep secret — bypasses RLS) |

> **Important**: The `service_role` key has full database access. Never commit it to git. Store it in environment variables or `~/.brain/config.json`.

### 3b: Install Dependencies

`make init` already installed core deps. Run these commands **in your project terminal** (not in Claude Code) to add the remaining packages:

Make sure you're in the project directory:

```bash
cd "/Users/david/Projects/Second Brain/second-brain-mcp"
```

Install runtime deps:

| Package | Purpose |
|---------|---------|
| `@supabase/supabase-js` | Talk to your Supabase database |
| `hono` | HTTP framework for Supabase Edge Functions |
| `@hono/mcp` | MCP protocol adapter for Hono |
| `zod` | Schema validation for MCP tool inputs |

```bash
npm install @supabase/supabase-js hono @hono/mcp zod
```

Install dev dep (Supabase CLI for local dev, migrations, and Edge Function deployment):

```bash
npm install -D supabase
```

You should see packages added to `package.json` under `dependencies` and `devDependencies`.

### 3c: Link to Supabase Project

This connects your local project to the remote Supabase project you created in step 3a.

First, authenticate with Supabase (opens browser):

```bash
npx supabase login
```

Then link your project:

```bash
npx supabase link --project-ref nsvpamlirnjgrouubrhi
```

When prompted for the database password, enter the password you set when creating the Supabase project in step 3a.

### 3d: Set Environment Variables

Collect your Supabase keys and create a `.env` file:

| Variable | Where to find it |
|----------|------------------|
| `SUPABASE_URL` | Already known: `https://nsvpamlirnjgrouubrhi.supabase.co` |
| `SUPABASE_SERVICE_KEY` | Supabase Dashboard → Settings → API → `service_role` key |

```bash
cat > .env << 'EOF'
SUPABASE_URL=https://nsvpamlirnjgrouubrhi.supabase.co
SUPABASE_SERVICE_KEY=<paste-service-role-key-here>
EOF
```

> **Important**: `.env` is already in `.gitignore` — your keys will not be committed to git.
>
> **No external API keys needed!** Embeddings use Supabase's built-in `gte-small` model (runs locally in Edge Functions, no API calls). Metadata extraction is deferred to a later feature and can optionally use OpenRouter when needed.

## Reference Architecture
Based on Nate B Jones' Open Brain (OB1) with key upgrades:
- **Same**: Supabase pgvector, Edge Functions (Deno), Slack intake
- **Simplified**: Embeddings via Supabase built-in `gte-small` (384 dims, free, no API key) instead of OpenAI via OpenRouter
- **Upgraded**: Hybrid search (semantic + full-text), developer context profile, cross-project MCP config, CLI tool, automatic embeddings via triggers + pgmq
- **Key deps**: `@modelcontextprotocol/sdk`, `hono` + `@hono/mcp` (Edge Function HTTP framework), `zod` (tool schemas)
- **Known gotcha**: Slack retries after 3s — must respond immediately and process async, dedup by `slack_ts`
- **Embedding model**: `gte-small` — 384 dimensions, English-only, 512 token max, MTEB 61.36 (within 1 point of OpenAI's 62.26). More than sufficient for short developer notes. Swap to OpenAI later if needed (one-line change).

---

## Feature Summary

| ID | Feature | Group | Stories | Depends On |
|----|---------|-------|---------|------------|
| F-001 | Supabase Schema & pgvector Setup | Foundation | 3 | — |
| F-002 | MCP Server Core with Store & Search Tools | Foundation | 3 | F-001 |
| F-003 | Hybrid Search (Semantic + Full-Text) | Core | 3 | F-001, F-002 |
| F-004 | Tagging, Metadata & Management Tools | Core | 3 | F-002 |
| F-005 | Developer Context Profile | Core | 3 | F-002, F-003 |
| F-006 | CLI Capture Tool | User-Facing | 2 | F-002 |
| F-007 | Slack Intake Bot | User-Facing | 3 | F-001, F-004 |
| F-008 | Browse, Stats & Manage Tools | User-Facing | 3 | F-002, F-003 |
| F-009 | Cross-Project MCP Configuration | Polish | 2 | F-002, F-005 |
| F-010 | Edge Function Deployment & Remote Transport | Polish | 3 | F-002, F-003, F-007 |

---

### Group 1: Foundation

#### F-001: Supabase Schema & pgvector Setup

**Goal**: Establish the database schema with pgvector extension, HNSW indexing, automatic embedding pipeline, and Row Level Security as the persistent storage layer for all knowledge.

**Stories**:

1. **As a developer, I want a `thoughts` table with vector embeddings column**, so that I can store knowledge as both text and mathematical meaning.
   - Enable extensions via migration: `pgvector`, `pgmq`, `pg_net`, `pg_cron`
   - Create `thoughts` table: id (uuid), content (text), embedding (vector(384)), metadata (jsonb), thought_type (text), created_at (timestamptz), updated_at (timestamptz)
   - Add HNSW index on embedding column using cosine distance operator (`<=>`)
   - Include GIN index on metadata jsonb for fast filtering

2. **As a developer, I want embeddings generated automatically when thoughts are inserted**, so that I don't need an external API key for embeddings.
   - Deploy `embed` Edge Function using Supabase built-in `gte-small` model (384 dims, no API key)
   - Create `pgmq` queue (`embedding_jobs`) for async embedding processing
   - Create SQL triggers on `thoughts` table: queue embedding job on INSERT and UPDATE
   - Schedule `pg_cron` job to process embedding queue every 10 seconds
   - Embeddings populate asynchronously (~10s after insert)
   - Add `tsvector` generated column from `content` field for full-text search
   - Create GIN index on the tsvector column

3. **As a developer, I want Row Level Security scoped to service role**, so that my data is protected even if the Supabase URL is exposed.
   - Enable RLS on `thoughts` table
   - Create policy allowing full CRUD for `service_role` only
   - Verify anon key cannot read or write thoughts

**Interface Contract (produces)**:
- `thoughts` table with vector(384) + tsvector columns, HNSW + GIN indexes
- `embed` Edge Function using `Supabase.ai.Session('gte-small')`
- Automatic embedding pipeline: triggers → pgmq → pg_cron → Edge Function
- Supabase migration files in `supabase/migrations/`
- RLS policies active

**Definition of Done**: Migrations apply cleanly, inserting a thought auto-generates its embedding within ~10 seconds, pgvector similarity queries return results, full-text search returns ranked results, anon key is blocked by RLS. No external API keys required.

---

#### F-002: MCP Server Core with Store & Search Tools

**Goal**: Build the TypeScript MCP server exposing `store_thought` and `search_thoughts` tools that any MCP-compatible client can call.

**Stories**:

1. **As a developer, I want an MCP server that runs via stdio transport**, so that I can add it to Claude Code with `claude mcp add`.
   - Implement MCP server using `@modelcontextprotocol/sdk` with stdio transport
   - Register `store_thought` tool: accepts content (string), optional type and tags
   - Register `search_thoughts` tool: accepts query (string), optional limit and filters
   - Server starts cleanly and lists tools on capability negotiation

2. **As a developer, I want `store_thought` to persist to Supabase with automatic embedding**, so that every captured thought becomes searchable without manual embedding calls.
   - Insert content + metadata into `thoughts` table via Supabase client
   - Embedding generates automatically via the F-001 trigger pipeline (~10s async)
   - Return confirmation with thought ID and timestamp
   - Handle errors gracefully (Supabase unreachable)

3. **As a developer, I want `search_thoughts` to return semantically relevant results**, so that I can find knowledge even without exact keyword matches.
   - Generate query embedding using `gte-small` via the `embed` Edge Function
   - Query Supabase using `<=>` cosine distance operator, ordered by similarity
   - Return top N results (default 5) with content, metadata, similarity score, and created_at
   - Support `limit` parameter (1-20)

**Interface Contract (produces)**:
- MCP server binary runnable via `npx tsx src/index.ts`
- `store_thought` tool (content: string, type?: string, tags?: string[]) → ThoughtResponse
- `search_thoughts` tool (query: string, limit?: number) → ThoughtResult[]
- Environment variables: `SUPABASE_URL`, `SUPABASE_SERVICE_KEY`

**Definition of Done**: Server starts via stdio, Claude Code can call both tools, stored thoughts are retrievable by semantic search, error cases return helpful messages.

---

### Group 2: Core

#### F-003: Hybrid Search (Semantic + Full-Text)

**Goal**: Upgrade search from pure vector to weighted hybrid (semantic + full-text), proven to outperform pure vector search in personal knowledge retrieval.

**Stories**:

1. **As a developer, I want search to combine semantic similarity with keyword matching**, so that exact terms and conceptual matches both surface relevant results.
   - Implement hybrid search RPC function in Supabase (`match_thoughts_hybrid`)
   - Weighted scoring: 0.7 * semantic_score + 0.3 * keyword_score (configurable)
   - Fall back to pure semantic search when no keyword matches exist
   - Return combined score alongside individual semantic and keyword scores

2. **As a developer, I want to filter search results by metadata**, so that I can scope queries to specific types, tags, or date ranges.
   - Support filters: `type` (exact match), `tags` (array contains), `after` (date), `before` (date)
   - Filters apply as WHERE clauses before scoring
   - Update `search_thoughts` MCP tool schema to accept optional filters object

3. **As a developer, I want a `search_by_text` tool for pure keyword searches**, so that I can find thoughts by exact terms when I know what I'm looking for.
   - Register `search_by_text` MCP tool using PostgreSQL full-text search only
   - Support phrase matching and boolean operators via `to_tsquery`
   - Return results ranked by `ts_rank` with highlighted matching fragments

**Interface Contract (produces)**:
- `match_thoughts_hybrid` Supabase RPC function
- Updated `search_thoughts` tool with hybrid scoring and metadata filters
- New `search_by_text` tool for keyword-only search
- Configurable weight ratio for semantic vs keyword scoring

**Definition of Done**: Hybrid search returns better results than pure vector for queries with specific terms, metadata filters narrow results correctly, keyword search finds exact matches that semantic search might miss.

---

#### F-004: Tagging, Metadata & Management Tools

**Goal**: Support manual tagging and metadata on thoughts, with an `update_thought` tool for corrections, and lay the groundwork for optional LLM-powered auto-extraction later.

**Stories**:

1. **As a developer, I want to tag and classify thoughts on capture**, so that I can filter by category (decision, preference, pattern, lesson, reference, idea).
   - `store_thought` accepts optional `type` and `tags` parameters
   - Store type in `thought_type` column, tags in `metadata.tags` array
   - If no type provided, default to `note`
   - Regex-based auto-tagging: extract URLs → `metadata.references[]`, detect code blocks → tag as `code`

2. **As a developer, I want to edit metadata after capture**, so that I can correct or enrich classifications.
   - Register `update_thought` MCP tool: accepts thought_id and partial metadata updates
   - Merge provided fields with existing metadata (not full replace)
   - Re-index tsvector if content changes

3. **As a developer, I want an optional LLM extraction pipeline I can enable later**, so that metadata extraction can be upgraded when I add an API key.
   - Define metadata schema: `{ type, topics, people, action_items, tags, confidence }`
   - Create `extract-metadata` Edge Function stub that accepts thought_id and returns extracted metadata
   - When `OPENROUTER_API_KEY` env var is set, auto-extraction activates (calls gpt-4o-mini or claude-haiku)
   - When not set, extraction is skipped — manual tagging only
   - LLM prompt template stored in `src/prompts/extract-metadata.ts`

**Interface Contract (produces)**:
- `store_thought` with optional type/tags parameters
- `update_thought` MCP tool for metadata corrections
- Metadata schema: `{ type, topics, people, action_items, tags, confidence }`
- Optional `extract-metadata` Edge Function (activated by `OPENROUTER_API_KEY`)

**Definition of Done**: Manual tagging works on capture and via update tool, regex auto-tagging catches URLs and code blocks, metadata is searchable via filters, LLM extraction is wired but optional (zero API keys required for base functionality).

---

#### F-005: Developer Context Profile

**Goal**: Store and serve a persistent developer profile (subscriptions, tools, preferences, deployment targets) that any AI session can query to personalize its behavior.

**Stories**:

1. **As a developer, I want to store my tool subscriptions and accounts as structured context**, so that every AI session knows I have Claude Code Max, Gemini Pro, Vercel Pro, Railway, and Supabase.
   - Register `set_profile` MCP tool: accepts key-value pairs for profile sections
   - Store profile in a dedicated `developer_profile` table (key: text, value: jsonb, updated_at)
   - Predefined sections: subscriptions, tools, preferences, deployment_targets, conventions
   - Profile entries are upserted (not duplicated) on repeated calls

2. **As a developer, I want AI sessions to retrieve my profile automatically**, so that context is available without me repeating it.
   - Register `get_profile` MCP tool: returns full profile or specific section
   - Register MCP resource `developer://profile` for passive context injection
   - Profile is lightweight enough to include in system prompts (< 2KB target)

3. **As a developer, I want to store project-specific preferences that override global defaults**, so that different projects can have different conventions.
   - Support `project` scope on profile entries (global vs project-specific)
   - Project scope keyed by project name or directory
   - `get_profile` merges global + project-specific, with project taking precedence

**Interface Contract (produces)**:
- `developer_profile` table in Supabase
- `set_profile` tool (section: string, data: object, scope?: "global" | "project") → ProfileResponse
- `get_profile` tool (section?: string, project?: string) → ProfileData
- `developer://profile` MCP resource for passive context loading

**Definition of Done**: Profile stores and retrieves subscriptions/tools/preferences, project-specific overrides work, profile is accessible as both tool call and MCP resource, data fits within 2KB for system prompt injection.

---

### Group 3: User-Facing

#### F-006: CLI Capture Tool

**Goal**: Provide a command-line tool for quick thought capture from the terminal, fitting naturally into developer workflows.

**Stories**:

1. **As a developer, I want to capture thoughts from the terminal with a one-liner**, so that I can log knowledge without leaving my workflow.
   - `brain store "my thought here"` — stores thought, embedding auto-generates via Supabase
   - `brain store --type decision "chose pgvector over Qdrant"` — stores with explicit type
   - `brain store --tags "supabase,architecture" "content here"` — stores with explicit tags
   - Reads `SUPABASE_URL`, `SUPABASE_SERVICE_KEY` from env or `~/.brain/config.json`

2. **As a developer, I want to search my brain from the terminal**, so that I can quickly look up past decisions and patterns.
   - `brain search "deployment strategy"` — hybrid search, prints top 5 results
   - `brain search --type preference --limit 10 "tools"` — filtered search
   - Output: formatted table with score, type, snippet, date
   - `brain profile` — displays current developer profile

**Interface Contract (produces)**:
- `brain` CLI binary (via `npx tsx cli/index.ts` or compiled with `pkg`/`esbuild`)
- Commands: `store`, `search`, `profile`, `config`
- Config file: `~/.brain/config.json`

**Definition of Done**: CLI stores and searches thoughts, output is clean and readable in terminal, config file persists credentials, works on macOS (bash 3.2 compatible scripts if any shell wrappers).

---

#### F-007: Slack Intake Bot

**Goal**: Capture thoughts by messaging a private Slack channel, with automatic embedding happening via the Supabase trigger pipeline.

**Stories**:

1. **As a developer, I want to DM a Slack channel to capture thoughts**, so that I can log ideas from my phone or any device with Slack.
   - Create Slack app with Event Subscriptions (message.channels scope)
   - Deploy `ingest-thought` Supabase Edge Function as the webhook endpoint
   - Edge Function receives Slack event, extracts message text, inserts into `thoughts` table (embedding auto-generates via trigger pipeline)
   - Respond immediately to Slack (within 3s) to prevent retries, process async
   - Dedup by `slack_ts` to prevent duplicate entries on Slack retries
   - Responds with a Slack reaction (checkmark) on successful capture

2. **As a developer, I want Slack messages with attachments to capture the text content**, so that links and snippets are preserved.
   - Extract URLs from messages and store in metadata.references[]
   - Handle code blocks (triple-backtick) by preserving formatting in content
   - Ignore bot messages and thread replies (only capture top-level human messages)

3. **As a developer, I want the Slack bot to acknowledge with a summary**, so that I know the thought was captured and classified correctly.
   - Reply in-thread with: "Captured as {type}. Tags: {tags}. ID: {short_id}"
   - Include a "Fix" button that opens a modal to edit metadata (optional, stretch goal)
   - Rate limit: max 60 messages/minute to stay within Supabase Edge Function free tier

**Interface Contract (produces)**:
- `ingest-thought` Supabase Edge Function in `supabase/functions/ingest-thought/`
- Slack App manifest for Event Subscriptions
- Webhook URL: `https://<project-ref>.supabase.co/functions/v1/ingest-thought`

**Definition of Done**: Messaging the Slack channel stores a thought (embedding auto-generates via trigger), Slack reaction confirms capture, rate limits prevent overuse, Edge Function deploys cleanly via `supabase functions deploy`.

---

#### F-008: Browse, Stats & Manage Tools

**Goal**: Expose MCP tools for browsing recent thoughts, viewing usage statistics, and managing (editing/deleting) stored knowledge.

**Stories**:

1. **As a developer, I want to browse my recent thoughts**, so that I can review what I've captured without searching.
   - Register `browse_thoughts` MCP tool: returns recent thoughts sorted by created_at desc
   - Support pagination (offset + limit), type filter, and tag filter
   - Return content, type, tags, and created_at for each result

2. **As a developer, I want usage statistics about my brain**, so that I can see how much knowledge is stored and what categories dominate.
   - Register `brain_stats` MCP tool: returns total count, count by type, count by tag (top 10), date range, storage size estimate
   - Include "last captured" timestamp and "most active day" stat
   - Lightweight query using Supabase aggregations

3. **As a developer, I want to delete outdated or incorrect thoughts**, so that my brain stays clean and relevant.
   - Register `delete_thought` MCP tool: accepts thought_id, returns confirmation
   - Register `bulk_delete` MCP tool: accepts filter criteria (type, tags, date range), returns count deleted
   - Soft delete (mark as deleted, exclude from search) with option for hard delete

**Interface Contract (produces)**:
- `browse_thoughts` tool (limit?: number, offset?: number, type?: string, tag?: string) → ThoughtResult[]
- `brain_stats` tool () → BrainStats
- `delete_thought` tool (id: string, hard?: boolean) → DeleteConfirmation
- `bulk_delete` tool (filter: FilterCriteria, hard?: boolean) → BulkDeleteResult

**Definition of Done**: Browse returns paginated results, stats reflect actual database state, delete removes thoughts from search results, bulk delete works with filter criteria.

---

### Group 4: Polish

#### F-009: Cross-Project MCP Configuration

**Goal**: Make the MCP server trivially addable to any project via a single command or config snippet, with documentation for team sharing.

**Stories**:

1. **As a developer, I want to add the brain to any project with one command**, so that every Claude Code session has access.
   - Document `claude mcp add` command with all required env vars
   - Create `.mcp.json` template for project-level sharing (with env var placeholders)
   - Support `--scope user` for global availability across all projects
   - Provide setup script: `brain setup` that configures Claude Code MCP integration

2. **As a developer, I want the brain to include project context automatically**, so that searches are aware of which project I'm working in.
   - Detect current working directory and project name from git remote or package.json
   - Include project context in search results ranking (boost thoughts from current project)
   - Auto-tag stored thoughts with current project name when captured via MCP tool

**Interface Contract (produces)**:
- `claude mcp add` command documentation
- `.mcp.json` template file
- `brain setup` CLI command
- Project-aware context injection in MCP server

**Definition of Done**: One command adds brain to a new project, project context influences search ranking, `.mcp.json` works for team sharing with env var substitution.

---

#### F-010: Edge Function Deployment & Remote Transport

**Goal**: Deploy the MCP server as a Supabase Edge Function with HTTP transport, enabling access from any MCP-compatible client (Claude Desktop, ChatGPT, Gemini) beyond just Claude Code stdio.

**Stories**:

1. **As a developer, I want the MCP server accessible via HTTP**, so that Claude Desktop, ChatGPT, and other clients can connect remotely.
   - Deploy MCP server as Supabase Edge Function (`open-brain-mcp`) using Hono + `@hono/mcp`
   - Implement streamable HTTP transport (POST for tool calls, GET for server-sent events)
   - Authentication via API key in query parameter (`?key=`) or `x-brain-key` header
   - Single URL: `https://<ref>.supabase.co/functions/v1/open-brain-mcp?key=<key>`

2. **As a developer, I want both stdio and HTTP transports from the same codebase**, so that I maintain one server, not two.
   - Abstract transport layer — shared tool handlers, configurable transport at startup
   - `MODE=stdio npx tsx src/index.ts` for Claude Code local use
   - Edge Function entry point wraps the same handlers with HTTP transport
   - Shared test suite validates both transports

3. **As a developer, I want a health check and connection test endpoint**, so that I can verify the remote server is working.
   - `GET /health` returns server status, tool count, and database connectivity
   - `brain ping` CLI command tests both stdio and HTTP endpoints
   - Connection errors return helpful diagnostics (wrong key, Supabase unreachable, etc.)

**Interface Contract (produces)**:
- `open-brain-mcp` Supabase Edge Function in `supabase/functions/open-brain-mcp/`
- HTTP transport endpoint URL
- Shared tool handler layer used by both stdio and HTTP transports
- `brain ping` CLI command

**Definition of Done**: HTTP endpoint responds to MCP tool calls from remote clients, stdio transport continues to work for Claude Code, single codebase serves both transports, health check confirms connectivity.

---

## Phase 4: AOD Lifecycle (Governance)

Start with F-001 (the foundation). Type this into Claude Code:

```
/aod.discover Supabase Schema & pgvector Setup — Establish the database schema with pgvector extension, HNSW indexing, automatic embedding pipeline (gte-small via triggers + pgmq + pg_cron), and Row Level Security. Includes thoughts table with vector(384) embeddings, tsvector full-text column, HNSW + GIN indexes, embed Edge Function, and RLS scoped to service_role. Zero external API keys needed.
```

Then run the full Triad workflow:

```
/aod.define
/aod.spec
/aod.project-plan
/aod.tasks
/aod.build
/aod.deliver
```

### Subsequent Features

For each remaining feature (F-002 through F-010), copy the feature block from the guide below (from `#### F-NNN:` to `---`) and paste it into `/aod.discover`. Then repeat the Triad workflow (`/aod.define` → `/aod.deliver`).

**Example for F-002:**
```
/aod.discover MCP Server Core with Store & Search Tools — Build the TypeScript MCP server exposing store_thought and search_thoughts tools via stdio transport. Uses @modelcontextprotocol/sdk, persists to Supabase pgvector with automatic embeddings (gte-small, no API key). Runnable via npx tsx src/index.ts, connectable with claude mcp add.
```

## Feature Completion Tracker

| ID | Feature | Status |
|----|---------|--------|
| F-001 | Supabase Schema & pgvector Setup | [ ] |
| F-002 | MCP Server Core with Store & Search Tools | [ ] |
| F-003 | Hybrid Search (Semantic + Full-Text) | [ ] |
| F-004 | Tagging, Metadata & Management Tools | [ ] |
| F-005 | Developer Context Profile | [ ] |
| F-006 | CLI Capture Tool | [ ] |
| F-007 | Slack Intake Bot | [ ] |
| F-008 | Browse, Stats & Manage Tools | [ ] |
| F-009 | Cross-Project MCP Configuration | [ ] |
| F-010 | Edge Function Deployment & Remote Transport | [ ] |

## Success Criteria
- All 10 features implemented and delivered
- Each feature independently demonstrable
- Valid dependency chain maintained throughout
- MCP server connectable from Claude Code in any project via `claude mcp add`
- Hybrid search returns better results than pure vector search for developer queries
- Developer profile accessible from every connected AI session
- Slack intake captures thoughts with embedding auto-generated within ~10 seconds
- Zero external API keys required for core functionality (embeddings, search, storage)
- CLI provides fast capture without leaving the terminal
