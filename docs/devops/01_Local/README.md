# Local Development Environment - {{PROJECT_NAME}}

**Last Updated**: {{CURRENT_DATE}}
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
- **BATS** (`bats-core`): Bash test framework used by the shell test suite introduced in feature 129. Install via `brew install bats-core` (macOS), `apt-get install bats` (Linux), or as a git submodule (`git submodule add https://github.com/bats-core/bats-core.git tests/vendor/bats-core`). Only required if you will run or contribute to the bash test suite. See `CONTRIBUTING.md` for the authoritative setup guide.

### make init Personalization

`make init` personalizes the following template files by replacing `{{PROJECT_NAME}}` and other template variables with your project values at setup time:

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
cd {{PROJECT_NAME}}

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
DATABASE_URL=postgresql://localhost:{{DATABASE_PORT}}/{{PROJECT_NAME}}_dev
API_URL=http://localhost:{{BACKEND_PORT}}
FRONTEND_URL=http://localhost:{{FRONTEND_PORT}}
```

**Optional Variables**:
```
AOD_LOG_FILE=.aod/logs/aod.log
AOD_BOARD=3
CI=                      # when set, scripts/update.sh defaults to --dry-run
AOD_UPDATE_TMP_DIR=      # override staging dir for cross-filesystem environments
FORCE_RETAG=             # bypass the upstream retag tripwire (logs a WARN)
```

The `AOD_LOG_FILE` variable controls where the logging utility writes its output. If not specified, it defaults to `.aod/logs/aod.log`. You can override this to write logs to a different location.

The `AOD_BOARD` variable pins the GitHub Projects board number for issue-board sync. When set, `github-lifecycle.sh` skips title-based board discovery and targets this board directly. If not specified, the script discovers the board by matching the title pattern `{repo-name}-backlog` or `AOD Backlog`.

**Update-script variables** (feature 129 — downstream template update mechanism):

- `CI`: when set (any non-empty value), `scripts/update.sh` defaults to `--dry-run` as a safety guard. Explicit `--apply` is required to write in CI. Intended to prevent accidental writes from GitHub Actions, GitLab CI, and equivalent automation.
- `AOD_UPDATE_TMP_DIR`: overrides the default staging directory (`<adopter_root>/.aod/update-tmp`). Must live on the same filesystem as the project root — atomicity relies on `rename(2)` within the same mount. Primary use: containerized environments where the default path straddles a mount boundary.
- `FORCE_RETAG`: when `1`, suppresses the upstream retag tripwire. Use only when you have verified the upstream tag's content out-of-band. Logs a WARN and records the override in `.aod/aod-kit-version.json`.

**Bootstrap variables** (feature 134 — `make update-bootstrap` + `--check-placeholders`):

- `YES`: when set to `1`, `make update-bootstrap YES=1` engages `--yes` mode (non-interactive). Pass-through to `scripts/update.sh --bootstrap --yes`.
- `AOD_BOOTSTRAP_TECH_STACK_DATABASE`, `AOD_BOOTSTRAP_TECH_STACK_VECTOR`, `AOD_BOOTSTRAP_TECH_STACK_AUTH`, `AOD_BOOTSTRAP_CLOUD_PROVIDER`: required in `--yes` mode (always-prompt architecture values).
- `AOD_BOOTSTRAP_<FIELD>`: required in `--yes` mode for any auto-discovered field that falls back to low-confidence detection. Pattern `AOD_BOOTSTRAP_<UPPERCASE_FIELD_NAME>=<value>` (e.g., `AOD_BOOTSTRAP_PROJECT_NAME`).
- `AOD_UPSTREAM_URL`: fallback upstream URL when `CANONICAL_URL=...` is not findable in `scripts/sync-upstream.sh`. In `--yes` mode with no `CANONICAL_URL` discoverable, this env var is required.

See `docs/devops/CI_CD_GUIDE.md` → "Update-Script Environment Variables" and `docs/guides/DOWNSTREAM_UPDATE.md` for the full contract.

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

## Running checks locally

Template maintainers (not adopters) run these Make targets locally to pre-empt CI failures on `main`. Adopter projects do NOT need these targets unless you are extending the upstream template.

### Manifest Coverage (F129)

```bash
# Validate every tracked file is categorized in .aod/template-manifest.txt
scripts/check-manifest-coverage.sh
```

Exit `0` = clean. Exit `1` = uncategorized paths printed in compiler-diagnostic format.

### Extract Coverage (F128)

```bash
# Validate scripts/extract-classification.txt matches live MANIFEST_DIRS + .extractignore
make extract-check

# Regenerate the snapshot after a legitimate manifest change
# (maintainer acknowledgement step — review the diff, then commit)
make extract-classify
git diff scripts/extract-classification.txt
git add scripts/extract-classification.txt
```

Emergency CI override: include `[skip extract-check]` in the head commit message to bypass the CI workflow for a single commit (FR-018). The workflow logs a `::warning::` annotation. Use sparingly — PM guidance caps routine use at once per quarter.

### Stack Contract (F130)

```bash
# Validate every app-stack pack's STACK.md contract block (matches CI exactly)
bash .aod/scripts/bash/stack-contract-lint.sh --all

# Validate a single pack — fastest while iterating on one STACK.md
bash .aod/scripts/bash/stack-contract-lint.sh stacks/<pack>/STACK.md

# Print usage + exit-code table
bash .aod/scripts/bash/stack-contract-lint.sh --help
```

Exit `0` = VALID. Non-zero exits use the stable code table (1 RUNTIME_ERROR, 2 MISSING_TEST_COMMAND, 3 XOR_VIOLATION, 4 UNKNOWN_KEY, 5 MISSING_BLOCK). In `--all` mode the script exits with the numerically lowest non-zero code across all non-allowlisted packs. The content-pack allowlist (currently `knowledge-system`) is skipped only in `--all` mode; single-file mode lints any path you hand it. Contract authoring guide: `docs/stacks/TEST_COMMAND_CONTRACT.md`.

All three validators run inside the upstream CI's `bash:3.2` Docker image; locally they run against your workstation shell. Because macOS ships `/bin/bash` 3.2.57, local + CI behaviour is identical (see KB Entry 6).

### BATS test suite

```bash
# Run all unit + integration shell tests
bats tests/unit/ tests/integration/
```

See `docs/devops/CI_CD_GUIDE.md` → "BATS Test Harness Setup" for install guidance.

---

## Pre-commit Secret-Scanning Hook (Feature 282 / F-5)

**Added in Feature 282 / F-5** (BLP-02 Wave 4+, merged 2026-05-10 at `18378bd`). Tachi ships a default-secure pre-commit gitleaks hook that scans staged content on every `git commit` and refuses commits containing credential-shaped strings (AWS keys, GitHub PATs, OpenAI/Anthropic API keys, RSA/SSH/PGP private key blocks, ~150+ patterns from the upstream gitleaks default ruleset). A CI parity workflow (`.github/workflows/gitleaks.yml`) provides a back-stop for `git commit --no-verify` deliberate bypass.

### Installation paths

**Path 1 — New tachi adopter via `scripts/init.sh`**: init prompts at first-run with default `Y` in TTY contexts. Pressing `<Enter>` accepts; typing `n` skips. Two CLI flag overrides bypass the prompt: `--precommit` forces install regardless of TTY/answer; `--no-precommit` forces skip. Non-TTY contexts (`</dev/null`, CI, scripted invocation) skip the prompt silently.

```bash
scripts/init.sh                  # default-Y prompt (TTY)
scripts/init.sh --precommit      # force-install regardless of TTY/answer
scripts/init.sh --no-precommit   # force-skip regardless of TTY/answer
```

**Path 2 — Existing tachi adopter via `pre-commit install`** (after `git pull` / `make update` brings in F-5): the F-5 update is **opt-in** for existing adopters (FR-010). Pulling F-5 does NOT auto-install the hook. To opt in:

```bash
brew install pre-commit
cd <your-tachi-clone>
pre-commit install             # opts into the hook
```

**Prerequisite**: `pre-commit` framework version >= **3.5.0** (Architect CONCERN-3 floor). If installed but below the floor, init.sh logs a WARN with upgrade guidance and continues (does NOT abort). Verify with:

```bash
pre-commit --version           # expected: pre-commit 3.5.0 or newer
```

### What gets scanned

The hook runs `gitleaks git --pre-commit --redact --staged --verbose --config=.gitleaks.toml` against **staged content only** (not the working tree, not unstaged changes, not committed history). Ruleset:

- Upstream gitleaks default ruleset (via `[extend] useDefault = true` in `.gitleaks.toml`) — covers AWS access keys, GitHub PATs, OpenAI/Anthropic API keys, generic high-entropy strings, RSA/SSH/PGP private key blocks, and ~150+ other credential patterns
- Three tachi allow-lists (additive — env-var placeholders, convention paths, vendored/generated/archived content)
- Two tachi custom rules (additive, both `warn-only`) — `tachi-personalization-env` defense-in-depth and `tachi-security-exceptions-jsonl` manual-edit detector

Full per-rule rationale catalog: `docs/standards/PRECOMMIT_HOOKS.md` §3.

### Bypass mechanisms

```bash
# Single-commit bypass (recommended — only the named hook is skipped):
SKIP=gitleaks git commit -m "docs: add OPENAI_API_KEY=sk-... example to tutorial"

# Inline allow-list comment (long-term suppression on a single line):
# gitleaks:allow
api_key = "sk-PLACEHOLDER1234567890abcdefghij"  # tutorial example

# Last-resort full bypass (CI parity workflow will still scan at PR time):
git commit --no-verify

# Full opt-out (uninstall the hook entirely):
pre-commit uninstall
```

The `gitleaks.yml` CI parity workflow runs a full-repo scan on every `pull_request` against `main` as a back-stop for the `--no-verify` path. Findings appear in the GitHub Security tab → Code Scanning under category `gitleaks`. Full contract: `docs/devops/CI_CD_GUIDE.md` → "Gitleaks CI Parity Workflow (F-282 / F-5)".

### When the hook refuses a commit

The wrapper script (`.aod/scripts/bash/precommit-wrap.sh`) augments gitleaks' default stderr with a four-item structured contract:

```text
──────────────────────────────────────────────────────────────
Commit refused: secret-scanning hook (gitleaks) found a match.

  Rule ID and file:line — see gitleaks output above.

  Bypass for a known-good case (e.g., a placeholder-only fixture):
      SKIP=gitleaks git commit ...

  Full bypass / opt-out / remediation guide:
      docs/standards/PRECOMMIT_HOOKS.md
──────────────────────────────────────────────────────────────
```

The wrapper preserves gitleaks' exit code verbatim (FM-5 exit-code-capture pattern — `rc=$?` is captured BEFORE the augmentation block runs, so a failure inside the augmentation cannot mask gitleaks' own rc). Bash 3.2 compatible — runs cleanly on macOS-stock `/bin/bash` 3.2.57.

### Tooling versions

| Tool | Version | Pin location | Bump cadence |
|------|---------|--------------|--------------|
| `pre-commit` framework | >= 3.5.0 | Floor enforced by `scripts/init.sh` (warn-and-continue on mismatch) | At adopter discretion (no hard pin) |
| `gitleaks` binary | v8.30.1 | `.pre-commit-config.yaml` `rev:` (replaced with pinned commit SHA via `pre-commit autoupdate --freeze`) + `.github/workflows/gitleaks.yml` `GITLEAKS_VERSION` constant | Each minor release with empirical re-test against `tests/fixtures/gitleaks-rule-interaction/` per ADR-042 §Consequences |
| Tarball SHA256 | `551f6fc83ea457d62a0d98237cbad105af8d557003051f41f3e7ca7b3f2470eb` | `.github/workflows/gitleaks.yml` `GITLEAKS_SHA256` constant | Re-derived from upstream `gitleaks_<VERSION>_checksums.txt` on every bump |

### Full reference

Authoritative policy doc + per-rule rationale catalog + complete bypass walkthrough: `docs/standards/PRECOMMIT_HOOKS.md`. ADR: `docs/architecture/02_ADRs/ADR-042-pre-commit-secret-scanning-default.md`. PRD: `docs/product/02_PRD/282-pre-commit-secret-scanning-defaults-2026-05-09.md`. Spec + tasks: `specs/282-pre-commit-secret-scanning-defaults/`.

---

## Pre-F129 Adopter Bootstrap (Feature 134)

**Applies to**: adopters who cloned AOD-kit before Feature 129 (`/aod.update` mechanism) shipped on 2026-04-19. If your project has no `.aod/aod-kit-version` pin and no `.aod/personalization.env` file, you are in this group. Authoritative walkthrough: `docs/guides/DOWNSTREAM_UPDATE.md` → "Bootstrap pre-F129 adopters".

### One-shot bootstrap

```bash
# Auto-discover 8 of 12 canonical placeholder values, prompt for 4 architecture values,
# write both prerequisite files atomically. Refuses if .aod/aod-kit-version already exists.
make update-bootstrap

# Non-interactive (CI / Ansible / fleet rollout): set required env vars first
export AOD_BOOTSTRAP_TECH_STACK_DATABASE=Postgres
export AOD_BOOTSTRAP_TECH_STACK_VECTOR=pgvector
export AOD_BOOTSTRAP_TECH_STACK_AUTH=JWT
export AOD_BOOTSTRAP_CLOUD_PROVIDER=Vercel
make update-bootstrap YES=1
```

After bootstrap completes, the standard `make update` flow becomes available:

```bash
make update --dry-run     # preview upstream changes
make update --apply       # apply updates
```

### Drift detection — `--check-placeholders`

After bootstrap, scan the working tree for legacy `{{...}}` placeholders not in the canonical 12-member set:

```bash
make update --check-placeholders
```

Exit `0` = clean. Exit `13` = placeholder drift detected — stdout lists every occurrence in `<file>:<line>: {{<name>}}` form followed by a migration-guide table mapping legacy names to canonical replacements.

The scan does NOT run as part of the default `make update` happy path (FR-010 — explicit-only invocation). Use it for one-time drift cleanup after bootstrapping a pre-F129 repo, or periodically to catch regressions during template upgrades.

Full adopter walkthrough including troubleshooting and the dual-repo model (PLSK meta-template vs AOD-kit downstream upstream): `docs/guides/DOWNSTREAM_UPDATE.md`.

---

## Archived Legacy Guidance

Archived legacy guidance for the old FastAPI stack packs lives in `docs/guides/Archive/STACK_PACK_CONSUMER_GUIDE_FASTAPI_REACT.md`. The active local-dev guide no longer treats those packs as current setup paths.

---

## `/aod.deliver` Local Runtime State (Feature 139)

**Added in Feature 139** (2026-04-23). `/aod.deliver` now enforces test verification as a hard gate before closing a feature. The skill writes a small set of runtime artifacts under `.aod/` that you may see locally while iterating. Most are gitignored and ephemeral — the audit log is the single exception.

### Filesystem surface

| Path | Tracked? | Purpose |
|------|----------|---------|
| `.aod/audit/deliver-opt-outs.jsonl` | **Yes — committed** | Append-only JSONL audit log. One record per `--no-tests=<reason>` invocation. Intentionally version-controlled so the audit trail survives branch churn. |
| `.aod/state/deliver-{NNN}.halt.json` | No (gitignored) | Halt record written when `/aod.deliver` exits with code 10 (halt-for-review). Read by orchestrators to reconstruct halt context. |
| `.aod/state/deliver-{NNN}.state.json` | No (gitignored) | Ephemeral per-invocation state + crash-recovery sentinel. Presence on re-run without a clean prior exit triggers exit code 12 (abandoned-sentinel). |
| `.aod/locks/deliver-{NNN}.lock` | No (gitignored) | Per-feature lockfile. Blocks concurrent `/aod.deliver {NNN}` invocations with exit code 11 (lock-conflict). |
| `.aod/config.json` | **Optional** | Project-wide AOD configuration, schema v1. Not auto-created. See "Configuration" below. |

The `.gitignore` rules covering these paths are already in place (`.aod/state/*.json`, `.aod/locks/*.lock`).

### Configuration (`.aod/config.json`)

The live file is **not** auto-generated. When absent, all defaults apply. To customise, start from the committed example:

```bash
cp .aod/config.json.example .aod/config.json
# edit fields as needed, then commit (the live file is tracked)
```

| Field | Default | Purpose |
|-------|---------|---------|
| `version` | `1` | Schema version (const `1`). Bump only on breaking changes. |
| `deliver.heal_attempts` | `2` | Max bounded auto-fix loop attempts before escalating to a heal-PR. Set to `0` to disable the loop (every failure routes straight to heal-PR). |
| `deliver.heal_max_timeout_multiplier` | `1.5` | Upper bound on how much the auto-fix loop may inflate an existing test timeout. Raise (e.g. `2.0`) for slower CI. |

Full field documentation: `.aod/config.json.example.md`. Reader-contract spec: `specs/139-delivery-verified-not-documented/contracts/config-schema.md`.

### Abandoned-sentinel recovery (exit 12)

If `/aod.deliver {NNN}` exits with code 12, a prior invocation crashed before cleaning up. The sentinel is intentionally **not** auto-cleared — inspect it first:

```bash
cat .aod/state/deliver-{NNN}.state.json   # review what the prior run was doing
# if safe to resume, delete the sentinel and re-run:
rm .aod/state/deliver-{NNN}.state.json
/aod.deliver {NNN}
```

### Heal-PR / halt-review (exit 10)

When the verification gate trips, `/aod.deliver` writes `.aod/state/deliver-{NNN}.halt.json` and opens (or idempotently updates) a heal-PR. Treat exit code 10 as a human-review handoff — your feature is not closed, but the delivery skill did its job by surfacing the failure. Full taxonomy in `docs/devops/CI_CD_GUIDE.md` → `/aod.deliver` Exit-Code Contract.

Adopter migration walkthrough: `docs/guides/DELIVERY_HARD_GATE_MIGRATION.md`. AC-coverage migration (for legacy prose specs): `docs/guides/AC_COVERAGE_MIGRATION.md`.

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
