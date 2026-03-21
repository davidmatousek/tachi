# Local Development Environment - tachi

**Last Updated**: 2026-03-21
**Owner**: DevOps Agent

---

## Prerequisites

### Required Software
- **Docker Desktop**: Version {{VERSION}}+
- **Node.js**: Version {{VERSION}} (LTS recommended)
- **Git**: Version {{VERSION}}+

### Optional Software
- **VS Code**: Recommended IDE
- **Postman/Insomnia**: API testing
- **jq**: JSON processor, required by `.aod/scripts/bash/run-state.sh` for the Full Lifecycle Orchestrator (`brew install jq` on macOS, `apt-get install jq` on Linux)
- **GitHub CLI (`gh`)**: Used by `make init` to auto-create a GitHub Projects board for backlog tracking. Requires the `project` OAuth scope (`gh auth refresh -s project`). If not installed or not authenticated, init continues without creating the board. Install via `brew install gh` on macOS or see [cli.github.com](https://cli.github.com)

### make init Personalization

`make init` personalizes the following template files by replacing `tachi` and other template variables with your project values at setup time:

- `CLAUDE.md`
- `README.md`
- `.claude/README.md`
- `.claude/agents/_README.md`
- `.claude/rules/commands.md`
- `.claude/rules/context-loading.md`
- `.claude/rules/deployment.md`
- `.claude/rules/git-workflow.md`
- `.claude/rules/governance.md`
- `.claude/rules/scope.md`
- `docs/product/02_PRD/INDEX.md`

No manual edits to these files are needed before running `make init`. After initialization, these files will contain your project name and description in place of template placeholders.

---

## Quick Start

```bash
# Clone repository
git clone {{REPOSITORY_URL}}
cd tachi

# Install dependencies
npm install

# Start development environment
docker-compose up -d

# Run database migrations
npm run migrate

# Start development servers
npm run dev
```

---

## Docker Compose Services

```yaml
# docker-compose.yml structure
services:
  frontend:
    # Frontend development server with hot reload
    ports: ["{{FRONTEND_PORT}}:{{FRONTEND_PORT}}"]

  backend:
    # Backend API server
    ports: ["{{BACKEND_PORT}}:{{BACKEND_PORT}}"]

  database:
    # PostgreSQL (or your database)
    ports: ["{{DATABASE_PORT}}:{{DATABASE_PORT}}"]
```

---

## Environment Variables

Copy `.env.example` to `.env`:

```bash
cp .env.example .env
```

**Required Variables**:
```
DATABASE_URL=postgresql://localhost:{{DATABASE_PORT}}/tachi_dev
API_URL=http://localhost:{{BACKEND_PORT}}
FRONTEND_URL=http://localhost:{{FRONTEND_PORT}}
```

**Optional Variables**:
```
AOD_LOG_FILE=.aod/logs/aod.log
```

The `AOD_LOG_FILE` variable controls where the logging utility writes its output. If not specified, it defaults to `.aod/logs/aod.log`. You can override this to write logs to a different location.

---

## Common Commands

```bash
# Start all services
docker-compose up -d

# Stop all services
docker-compose down

# View logs
docker-compose logs -f [service-name]

# Rebuild after changes
docker-compose up --build

# Reset database
docker-compose down -v
docker-compose up -d
npm run migrate
```

---

## Troubleshooting

### Port Already in Use
```bash
# Find process using port
lsof -i :{{PORT}}

# Kill process
kill -9 <PID>
```

### Database Connection Failed
```bash
# Check database is running
docker-compose ps

# Check logs
docker-compose logs database

# Reset database
docker-compose down -v && docker-compose up -d
```

### Hot Reload Not Working
- Ensure volumes are mounted correctly in docker-compose.yml
- Check file watcher limits (Linux: `sudo sysctl fs.inotify.max_user_watches=524288`)

---

**Template Instructions**: Replace all `{{TEMPLATE_VARIABLES}}` with your actual configuration.
