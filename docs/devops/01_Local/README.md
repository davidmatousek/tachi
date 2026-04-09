# Local Development Environment - tachi

**Last Updated**: 2026-04-09
**Owner**: DevOps Agent

---

## Prerequisites

### Required Software
- **Docker Desktop**: Version {{VERSION}}+
- **Node.js**: Version {{VERSION}} (LTS recommended)
- **Git**: Version {{VERSION}}+

### Optional Software
- **Python**: Version 3.9+ (stdlib only, no external packages). Required by the deterministic data extraction scripts in `scripts/`: `extract-report-data.py` (security report data for `/tachi.security-report`), `extract-infographic-data.py` (infographic template data for `/tachi.infographic`), and the shared `tachi_parsers.py` module. Most macOS and Linux systems include Python 3.9+ by default; verify with `python3 --version`
- **VS Code**: Recommended IDE
- **Postman/Insomnia**: API testing
- **jq**: JSON processor, required by `.aod/scripts/bash/run-state.sh` for the Full Lifecycle Orchestrator (`brew install jq` on macOS, `apt-get install jq` on Linux)
- **GitHub CLI (`gh`)**: Used by `make init` to auto-create a GitHub Projects board for backlog tracking. Requires the `project` OAuth scope (`gh auth refresh -s project`). If not installed or not authenticated, init continues without creating the board. Install via `brew install gh` on macOS or see [cli.github.com](https://cli.github.com)
- **Typst CLI**: Required by `/tachi.security-report` for PDF generation. Install via `brew install typst` on macOS, `cargo install typst-cli` on Linux, or `winget install typst` on Windows. If not installed, the `/tachi.security-report` command displays platform-specific install instructions and halts. See `templates/tachi/security-report/` for Typst template sources
- **Mermaid CLI (`mmdc`)**: Optional. Used by `scripts/extract-report-data.py` to render Mermaid attack tree diagrams to PNG for the Attack Path Pages section of the PDF security report (Feature 112). Requires Node.js. Install via `npm install -g @mermaid-js/mermaid-cli`. If not installed, the extraction script logs a warning and the attack path pages omit rendered diagram images while retaining narrative and remediation content. Only relevant when the scanned project contains an `attack-trees/` directory

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
GEMINI_API_KEY=your-gemini-api-key
```

The `AOD_LOG_FILE` variable controls where the logging utility writes its output. If not specified, it defaults to `.aod/logs/aod.log`. You can override this to write logs to a different location.

The `GEMINI_API_KEY` variable enables AI-generated threat infographic images via the Gemini API (`gemini-3-pro-image-preview` model). This is used by the threat infographic agent when invoked via the standalone `/tachi.infographic` command. If not set, the agent produces Mermaid-based visual specifications without rasterized image output. No local infrastructure is required -- the agent calls the external Gemini API directly.

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

## Platform Adapter Testing (Local)

Feature 021 introduced platform adapters in `adapters/`. To test an adapter locally, copy its files into a test project that uses the target platform.

### Testing File-Transformation Adapters

File-transformation adapters (Claude Code, Cursor, Copilot, Generic) contain static files. Testing means verifying the files are correctly recognized by the target platform.

```bash
# Claude Code adapter: copy agents into a test project
mkdir -p /path/to/test-project/.claude/agents/tachi
cp adapters/claude-code/agents/*.md /path/to/test-project/.claude/agents/tachi/

# Cursor adapter: copy rules into a test project
mkdir -p /path/to/test-project/.cursor/rules/tachi
cp adapters/cursor/rules/*.mdc /path/to/test-project/.cursor/rules/tachi/

# Copilot adapter: copy agents and instructions into a test project
mkdir -p /path/to/test-project/.github/agents/tachi
cp adapters/copilot/agents/*.agent.md /path/to/test-project/.github/agents/tachi/
cp adapters/copilot/instructions/*.instructions.md /path/to/test-project/.github/agents/tachi/
```

### Testing the GitHub Actions Adapter

The GitHub Actions adapter requires a GitHub repository with Actions enabled. To test locally before pushing:

1. Copy the workflow file:
   ```bash
   mkdir -p /path/to/test-project/.github/workflows
   cp adapters/github-actions/tachi-threat-model.yml /path/to/test-project/.github/workflows/
   ```

2. Validate the YAML syntax:
   ```bash
   # Requires yq or a YAML linter
   yq eval '.' adapters/github-actions/tachi-threat-model.yml > /dev/null && echo "YAML valid"
   ```

3. Set the `LLM_API_KEY` repository secret in the test repository (Settings > Secrets and variables > Actions).

4. Trigger the workflow by opening a PR that modifies files under `docs/architecture/`, or use manual dispatch from the Actions tab.

### Verifying VERSION Files

After modifying source agents, regenerate and verify VERSION files:

```bash
# Regenerate VERSION for a specific adapter
./scripts/generate-adapter-version.sh adapters/claude-code

# Verify the VERSION file contents
cat adapters/claude-code/VERSION
```

The VERSION file contains the source commit SHA, generation date, and SHA-256 checksums of each source agent file. Use it to confirm adapter files are derived from the expected source version.

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
