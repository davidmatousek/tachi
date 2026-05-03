# Getting Started — Path B (CLI-Driven)

Test the full orchestration pipeline using the CLI-driven path. The orchestrator creates tasks, spawns agents in parallel waves, and manages the lifecycle — you just watch.

---

## Step 1: Install the Orchestrator

```bash
git clone https://github.com/davidmatousek/aod-orchestrator.git
cd aod-orchestrator
make quickstart
```

Wait for it to finish. Verify:

```bash
curl -s http://localhost:8000/health | python3 -m json.tool
# Should show: "status": "healthy"
```

Open `http://localhost:5173` — dashboard should load.

## Step 2: Create a New Project from the AOD Kit Template

Create a **separate repo** for the Hello World demo app. It should be a sibling to `aod-orchestrator` in your projects folder, not inside it.

```bash
# Navigate to your projects folder (sibling to aod-orchestrator)
cd ~/Projects

# Clone the public template
git clone https://github.com/davidmatousek/agentic-oriented-development-kit.git hello-world-aod
cd hello-world-aod

# Replace the template origin with your own private repo
git remote remove origin
gh repo create hello-world-aod --private --source=. --push
```

> **Note**: If `gh` reports a missing `project` OAuth scope, run `gh auth refresh -h github.com -s project` and retry.

```bash
# Run interactive setup
make init
```

**When prompted, enter:**

| Prompt | Value |
|--------|-------|
| Project Name | `hello-world-aod` |
| Description | `Hello World Greeting Dashboard — AOD demo app` |
| GitHub Org | *your GitHub username or org* |
| GitHub Repo | `hello-world-aod` |
| AI Agent | `1` (Claude Code) |
| Tech Stack | `1` (fastapi-react-local) |

```bash
# Verify setup
make check

# (Optional) Establish product vision and design identity
# /aod.foundation

# Copy the demo stories from aod-orchestrator
cp ../aod-orchestrator/docs/guides/HELLO_WORLD_STORIES.md docs/guides/

# Commit and push the initialized project
git add -A && git commit -m "chore: initialize AOD project"
git push
```

## Step 3: Configure MCP Connection

From inside the `hello-world-aod` directory, open Claude Code and configure the MCP connection to the running orchestrator.

**Option A — Paste a prompt** (recommended):

```text
Create a .mcp.json file in the project root to connect to the AOD orchestrator. Use "uv" as the command, with args ["--directory", "<absolute-path-to-aod-orchestrator>/backend", "run", "aod-mcp"] and env AOD_API_URL set to "http://localhost:8000".
```

> **Tip**: Claude Code will resolve the absolute path and create the file for you.

**Option B — Create manually**:

Create `.mcp.json` in the project root, replacing `/path/to/aod-orchestrator` with the actual absolute path:

```json
{
  "mcpServers": {
    "aod-orchestrator": {
      "command": "uv",
      "args": ["--directory", "/path/to/aod-orchestrator/backend", "run", "aod-mcp"],
      "env": { "AOD_API_URL": "http://localhost:8000" }
    }
  }
}
```

## Step 4: Blueprint

Run:

```bash
/aod.blueprint --demo
```

This single command:
1. Registers the `hello-world-aod` project in the orchestrator
2. Creates 6 GitHub Issues (3 Build + 2 Test + 1 Security)
3. Syncs issues to the orchestrator
4. Creates tasks and agent assignments (3 waves)
5. Generates `docs/guides/BLUEPRINT_HELLO_WORLD_AOD.md`

## Step 5: Pre-flight Check

Before orchestrating, verify the backend can reach GitHub and all prerequisites are met:

```bash
# Ensure GITHUB_TOKEN is set in the orchestrator's backend .env
# (required for issue sync — the backend can't use your local gh CLI auth)
cd ~/Projects/aod-orchestrator/backend
grep GITHUB_TOKEN .env
# If empty, set it:
# gh auth token   ← copy this value
# Then edit .env: GITHUB_TOKEN=<paste-token>
```

```bash
# Use start-stable (no hot-reload) to prevent WebSocket drops during orchestration
cd ~/Projects/aod-orchestrator
make restart        # picks up .env changes
# Or for first start: make start-stable
```

See [Orchestration Safe Operation Guide](ORCHESTRATION_SAFE_OPERATION.md) for details on `make start-stable` vs `make start`.

## Step 6: Orchestrate

**Preview the wave plan first** (recommended):

```bash
/aod.orchestrate --dry-run
```

This displays the wave plan without creating tasks or spawning sessions. Verify the waves look correct, then run for real:

```bash
/aod.orchestrate
```

This auto-detects the project, fetches synced issues, groups them by ICE priority into waves, and runs the full pipeline:

| Wave | Focus | Agents | What Happens |
|------|-------|--------|-------------|
| 1 (P0) | Build | 3 parallel | Backend API, Frontend Form, Frontend History — each in its own worktree |
| **Checkpoint** | | | Governance gate at P0→P1 boundary — review results before proceeding |
| 2 (P1) | Test | 2 parallel | Backend tests, Frontend tests |
| **Checkpoint** | | | Governance gate at P1→P2 boundary |
| 3 (P2) | Secure | 1 | OWASP security review |

`/aod.orchestrate` manages the waves automatically — spawning parallel agents, polling for completion, and pausing at checkpoints for your review.

**Other options**:

| Flag | Effect |
|------|--------|
| `--dry-run` | Preview wave plan, no execution |
| `--issues N,N,N` | Orchestrate a subset of issues |
| `--yes` | Skip confirmation prompt |

**Alternative — single-issue execution**: If you only need to run one issue at a time, use `/aod.run` instead. `/aod.orchestrate` is the recommended approach for executing the full blueprint.

## Step 7: Monitor

**Dashboard** (recommended): Open `http://localhost:5173` and find `hello-world-aod` in the sidebar. The Pipeline page shows wave progress, session status, and PR links in real time.

**Watch a live agent** (optional):

```bash
tmux ls                              # See running sessions
tmux attach -t <session_name>        # Watch live (Ctrl+B, D to detach)
```

## Step 8: Resume After Checkpoints

`/aod.orchestrate` handles checkpoints interactively — when a governance gate pauses execution between priority tiers, it displays a structured summary of completed wave results and prompts you with options:

- **Continue** — advance to the next wave
- **Review on dashboard** — open the Pipeline page to inspect results before deciding
- **Abort** — stop orchestration and display a partial completion summary

If you are not running `/aod.orchestrate` interactively, you can also resume from the dashboard — click **Resume** on the Pipeline page.

## Step 9: Merge Results

After all waves complete, review and merge PRs from the dashboard or GitHub:

1. Open the **Pipeline** page on the dashboard (`http://localhost:5173`)
2. Each completed session shows a PR link — click to review the diff on GitHub
3. Merge PRs in wave order to minimize conflicts

Alternatively, use `gh` from your project directory:

```bash
gh pr list
gh pr view <number>
gh pr merge <number>
```

## Troubleshooting

| Problem | Fix |
|---------|-----|
| Backend not running | `cd ~/Projects/aod-orchestrator && make start-stable` |
| Port 8000 already in use | `make restart` (auto-kills orphans), or manually: `lsof -ti:8000 \| xargs kill -9` |
| Issue sync returns empty `[]` | Check `GITHUB_TOKEN` in `backend/.env` — must be non-empty. Check logs: `tail -20 /tmp/aod-backend.log` for sync errors |
| Dashboard shows "Reconnecting..." | Backend restarted (hot-reload or manual). Use `make start-stable` to prevent this during orchestration. Dashboard auto-reconnects. |
| Session stuck at TOS prompt | Should auto-accept. If not, attach: `tmux attach -t <session>`, press Down then Enter to accept bypass permissions |
| Sessions complete but no PRs | Check `exit_code` in session API — `None` is treated as eligible. Check backend logs for `create_pr` errors |
| Wave paused at checkpoint | Click **Resume** on dashboard Pipeline page, or respond to the interactive prompt if running `/aod.orchestrate` |
| Check backend logs | `tail -f /tmp/aod-backend.log` |

## What to Expect

- Each agent gets its own git worktree (`agent/{session_id}` branch) and tmux session
- Dashboard shows real-time updates via WebSocket — use `make start-stable` to avoid disconnections
- Sessions auto-accept the Claude Code bypass permissions TOS prompt and workspace trust prompt
- When a session completes, the orchestrator automatically pushes the branch and creates a PR
- Wave 1 agents work independently — their branches may have merge conflicts when merging PRs (this is expected)
- On a 16GB Mac Mini, 3 concurrent agents run comfortably

## Next Step

**First time?** Run the [Smoke Test](SMOKE_TEST.md) first — it validates the full pipeline with a single issue before committing to all 6.

Once Path B works, try [Path C (MCP Lead Agent)](GETTING_STARTED_PATH_C.md) for the autonomous version.

---

## Appendix A: Reset to Step 2

If something goes wrong and you need to start fresh from Step 2, follow these steps to clean up everything and try again.

### 1. Close any active sessions

```bash
# From aod-orchestrator, kill any tmux sessions for hello-world-aod
tmux ls 2>/dev/null | grep hello-world | cut -d: -f1 | xargs -I{} tmux kill-session -t {}
```

### 2. Remove the local project

```bash
cd ~/Projects
rm -rf hello-world-aod
```

### 3. Delete the GitHub repo

```bash
# May need: gh auth refresh -h github.com -s delete_repo
gh repo delete davidmatousek/hello-world-aod --yes
```

### 4. Remove the GitHub Projects board (if created)

Check [github.com/davidmatousek?tab=projects](https://github.com/davidmatousek?tab=projects) and delete any `hello-world-aod` project board manually.

### 5. Clean up orchestrator records (if registered)

```bash
# Check if the project was registered
curl -s http://localhost:8000/api/v1/projects | python3 -m json.tool
```

If `hello-world-aod` appears, note its `id` (e.g., `2`) and delete it via the API:

```bash
# Replace <id> with the project id from above
curl -X DELETE http://localhost:8000/api/v1/projects/<id>

# Verify it's gone
curl -s http://localhost:8000/api/v1/projects | python3 -m json.tool
```

### 6. Start over

Go back to [Step 2: Create a New Project](#step-2-create-a-new-project-from-the-aod-kit-template) and follow the guide from there.
