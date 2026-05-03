# Smoke Test — Single-Issue Pipeline Validation

Quick validation that the full orchestration pipeline works end-to-end: spawn → worktree → build → push → PR. Runs a single issue instead of the full 6-issue blueprint.

**Time**: ~15-20 minutes
**Prerequisite**: Orchestrator installed and running (Steps 1-3 of [Path B](GETTING_STARTED_PATH_B.md))

---

## What This Tests

| Stage | What's Validated |
|-------|-----------------|
| Blueprint | Issue created on GitHub, synced to orchestrator with ICE scores |
| Spawn | TOS auto-accept, workspace trust, tmux session starts |
| Build | Claude Code runs `/aod.run` in isolated worktree |
| Preserve | Branch pushed to remote, PR created automatically |
| Cleanup | Worktree removed after PR creation (not before) |

---

## Step 1: Reset (if needed)

If you have a previous `hello-world-aod` project, clean it up first:

```bash
# Kill any lingering sessions
tmux ls 2>/dev/null | grep hello-world | cut -d: -f1 | xargs -I{} tmux kill-session -t {}

# Remove local project
cd ~/Projects
rm -rf hello-world-aod

# Delete GitHub repo (may need: gh auth refresh -h github.com -s delete_repo)
gh repo delete davidmatousek/hello-world-aod --yes 2>/dev/null || true

# Remove orchestrator records
PROJECT_ID=$(curl -s http://localhost:8000/api/v1/projects | python3 -c "
import sys, json
for p in json.load(sys.stdin):
    if p['name'] == 'hello-world-aod':
        print(p['id'])
" 2>/dev/null)
[ -n "$PROJECT_ID" ] && curl -X DELETE "http://localhost:8000/api/v1/projects/$PROJECT_ID" && echo "Deleted project $PROJECT_ID"
```

Skip this step if starting fresh.

## Step 2: Create Project

```bash
cd ~/Projects
git clone https://github.com/davidmatousek/agentic-oriented-development-kit.git hello-world-aod
cd hello-world-aod
git remote remove origin
gh repo create hello-world-aod --private --source=. --push
```

> **Note**: If `gh` reports a missing `project` OAuth scope, run `gh auth refresh -h github.com -s project` and retry.

```bash
make init
```

**When prompted:**

| Prompt | Value |
|--------|-------|
| Project Name | `hello-world-aod` |
| Description | `Hello World — AOD smoke test` |
| GitHub Org | *your GitHub username* |
| GitHub Repo | `hello-world-aod` |
| AI Agent | `1` (Claude Code) |
| Tech Stack | `1` (fastapi-react-local) |

```bash
make check
cp ../aod-orchestrator/docs/guides/HELLO_WORLD_STORIES.md docs/guides/
git add -A && git commit -m "chore: initialize AOD project"
git push
```

## Step 3: Configure MCP

Create `.mcp.json` in the `hello-world-aod` project root:

```json
{
  "mcpServers": {
    "aod-orchestrator": {
      "command": "uv",
      "args": ["--directory", "/Users/david/Projects/aod-orchestrator/backend", "run", "aod-mcp"],
      "env": { "AOD_API_URL": "http://localhost:8000" }
    }
  }
}
```

## Step 4: Blueprint

```bash
/aod.blueprint --demo
```

Wait for it to create 6 GitHub Issues and sync them.

## Step 5: Pre-flight

```bash
# Verify GITHUB_TOKEN is set
cd ~/Projects/aod-orchestrator/backend && grep "GITHUB_TOKEN=" .env | grep -v "^#"
# Should show: GITHUB_TOKEN=gho_... (not empty)

# Ensure orchestrator is running in stable mode
cd ~/Projects/aod-orchestrator
make start-stable
```

## Step 6: Run Single Issue

Back in the `hello-world-aod` Claude Code session:

```bash
/aod.orchestrate --issues 2
```

This runs only **Issue #2 (Backend: Greeting API)** — a standalone feature with no dependencies.

One wave, one session, one agent. Should take 10-15 minutes.

## Step 7: Verify

While the session runs, monitor from the dashboard at `http://localhost:5173` or:

```bash
# Watch the tmux session
tmux ls | grep hello-world
tmux attach -t <session_name>   # Ctrl+B, D to detach
```

**After the session completes, verify each stage:**

### 7a. Session completed

```bash
curl -s http://localhost:8000/api/v1/sessions | python3 -c "
import sys, json
for s in json.load(sys.stdin):
    if 'hello-world' in s.get('worktree_path',''):
        print(f'S{s[\"id\"]}: status={s[\"status\"]} exit={s.get(\"exit_code\")} pr_status={s.get(\"pr_status\")} pr_url={s.get(\"pr_url\",\"none\")}')
"
```

**Expected**: `status=completed`, `pr_status=created`, `pr_url=https://github.com/...`

### 7b. Branch pushed

```bash
cd ~/Projects/hello-world-aod
git fetch --all
git branch -r | grep agent
```

**Expected**: `origin/agent/<session_id>` branch exists on remote.

### 7c. PR created

```bash
gh pr list --repo davidmatousek/hello-world-aod --state open
```

**Expected**: One open PR targeting `main`.

### 7d. Worktree cleaned up

```bash
ls ~/Projects/hello-world-aod/.worktrees/
```

**Expected**: Empty or directory doesn't exist (cleaned up after PR creation).

### 7e. Dashboard shows PR

Open `http://localhost:5173` — the session should show a PR link in the Pipeline view.

## Step 8: Merge & Validate Deliverables

Review the PR on GitHub, then merge it:

```bash
gh pr list --repo davidmatousek/hello-world-aod --state open
gh pr view <number> --repo davidmatousek/hello-world-aod
gh pr merge <number> --repo davidmatousek/hello-world-aod --merge
```

Pull the merged code and verify the deliverables landed:

```bash
cd ~/Projects/hello-world-aod
git pull origin main
```

**Check that Issue #2 (Backend: Greeting API) produced actual code and docs:**

```bash
# Application code
ls backend/app/                    # FastAPI app structure
ls backend/app/models/             # SQLAlchemy models (Greeting)
ls backend/app/schemas/            # Pydantic schemas (GreetingCreate, GreetingResponse)
ls backend/app/api/                # API routes (/greet, /greetings, /health)

# Database
ls backend/alembic/versions/       # Alembic migration(s)

# Documentation
cat .aod/spec.md                   # Feature specification
cat .aod/plan.md                   # Technical plan
ls specs/002-*/                    # Archived feature artifacts
```

**Functional test** (if the backend is runnable):

```bash
cd ~/Projects/hello-world-aod/backend
uv run uvicorn app.main:app --port 8001 &
sleep 2

# Health check
curl -s http://localhost:8001/health | python3 -m json.tool

# Create a greeting
curl -s -X POST http://localhost:8001/api/v1/greet \
  -H "Content-Type: application/json" \
  -d '{"name": "Smoke Test"}' | python3 -m json.tool

# List greetings
curl -s http://localhost:8001/api/v1/greetings | python3 -m json.tool

# Cleanup
kill %1
```

**Expected**: Code merged into `main`, API endpoints respond, greeting stored and returned.

## Pass / Fail

| Check | Pass | Fail |
|-------|------|------|
| Session status = completed | Pipeline detected session completion | Check `tail -20 /tmp/aod-backend.log` for errors |
| pr_status = created | Branch pushed + PR created automatically | Check logs for `create_pr` or `git push` errors |
| PR visible on GitHub | End-to-end pipeline works | Check if branch exists on remote (`git branch -r`) |
| Worktree cleaned up | Cleanup deferred correctly until after PR | If still present, cleanup may have failed — check logs |
| Code merged into main | Deliverables landed in hello-world-aod | Check PR merge status on GitHub |
| API responds (optional) | Feature is functional | Check backend logs, dependency setup |

**All pass?** → Run the full pipeline:

```bash
/aod.orchestrate
```

**Any fail?** → Check backend logs, fix the issue, then re-run:

```bash
tail -50 /tmp/aod-backend.log | grep -i "error\|fail\|create_pr\|git push"
```

---

## Quick Reference

| Command | Purpose |
|---------|---------|
| `/aod.orchestrate --issues 2` | Run single issue |
| `/aod.orchestrate --dry-run` | Preview wave plan |
| `/aod.orchestrate` | Run all issues |
| `tmux ls` | List active agent sessions |
| `tail -f /tmp/aod-backend.log` | Watch backend logs |
| `make restart` | Restart backend + frontend |
