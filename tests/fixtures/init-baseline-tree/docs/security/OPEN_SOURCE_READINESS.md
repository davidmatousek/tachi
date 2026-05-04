# Open-Source Readiness: Security Review

**Assessment Date**: 2026-03-25
**Scope**: Full repository scan for secrets, PII, internal references, and configuration issues
**Overall Posture**: BLOCKED — 1 Critical, 4 High, 3 Medium findings require remediation before public release

---

## Findings Summary

| Priority | ID | Finding | Status |
|----------|----|---------|--------|
| CRITICAL | C-1 | Live Gemini API key on disk | [x] |
| HIGH | H-1 | Hardcoded `/Users/david/` absolute paths in tracked files | [x] |
| HIGH | H-2 | References to private project "CISO_Agent" | [x] |
| HIGH | H-3 | References to private repo "product-led-spec-kit" | [x] |
| HIGH | H-4 | `.claude/settings.json` contains machine-specific paths | [x] |
| MEDIUM | M-1 | `SECRET_KEY` default in scaffold `config.py` | [x] |
| MEDIUM | M-2 | `support@ai-security-scanner.com` reference — verify if public | [x] |
| MEDIUM | M-3 | macOS-specific example paths in `mcp-config.json` | [x] |

---

## CRITICAL

### C-1: Live Gemini API Key on Disk

- **File**: `.env` (line 2)
- **Content**: `GEMINI_API_KEY=AIzaSy...` (live Google Gemini API key)
- **Git status**: NOT tracked (`.gitignore` is correct), NOT in git history
- **Risk**: If the repo is archived as a tarball, or `.gitignore` is accidentally modified, the key leaks. The `.gitignore` only protects against `git add`, not against tools like `tar`, `rsync`, or GitHub's "Download ZIP" of the working directory.

**Remediation**: See [Fix Instructions: C-1](#fix-instructions-c-1-secrets-management-with-1password) below.

---

## HIGH

### H-1: Hardcoded Absolute Paths Referencing Local Username

Multiple tracked files contain `/Users/david/` paths, leaking the developer's macOS username and directory structure.

| File | Path References |
|------|----------------|
| `.claude/settings.json:33` | `/Users/david/Projects/tachi/adapters/claude-code/agents/templates/*.md` |
| `.claude/settings.json:36-37` | `/Users/david/Projects/tachi/.claude/agents/tachi`, `.claude/commands` |
| `.claude/skills/code-execution-helper/references/api-wrapper.md:436,465-467` | `/Users/david/Documents/GitHub/CISO_Agent/...` |
| `.claude/skills/~aod-build/USAGE.md:258-259` | `/Users/david/Documents/GitHub/tachi/specs/001-tachi/...` |
| `.claude/INFRASTRUCTURE_SETUP_SUMMARY.md:379` | `/Users/david/Documents/GitHub/agentic-oriented-development-kit/.claude/` |
| `docs/standards/CLAUDE_MD_ORGANIZATION.md:32,41,56` | `/Users/david/Projects/CISO_Agent/src/api/` |
| `specs/007-ai-threat-agents/wave2-trackA-results.md:25-27` | `/Users/david/Projects/tachi/...` |
| `specs/007-ai-threat-agents/wave2-trackB-results.md:127-130` | `/Users/david/Projects/tachi/...` |
| `specs/007-ai-threat-agents/wave3-consistency-results.md:34-36` | `/Users/david/Projects/tachi/...` |

**Fix**: Replace all absolute paths with relative paths from the project root, or use placeholders like `/path/to/project/`.

### H-2: References to Private Project "CISO_Agent"

Reveals the existence of a separate private project, its internal structure, and its relationship to tachi.

| File | Reference |
|------|-----------|
| `.claude/agents/devops.md:9` | "Refactored per CISO_Agent best practices" |
| `.claude/agents/senior-backend-engineer.md:9` | "Refactored per CISO_Agent best practices" |
| `.claude/agents/product-manager.md:9` | "Refactored per CISO_Agent best practices" |
| `.claude/agents/architect.md:9` | "Refactored per CISO_Agent best practices" |
| `.claude/skills/code-execution-helper/references/api-wrapper.md:436,465-467` | Full paths to CISO_Agent files |
| `docs/standards/CLAUDE_MD_ORGANIZATION.md:32,41,56` | CISO_Agent directory structure as examples |

**Fix**: Replace "CISO_Agent" references with generic terms ("prior project" or "internal best practices") and replace path examples with generic placeholders.

### H-3: References to Private Repository "product-led-spec-kit"

Exposes the private repository name, its relationship to tachi, and the development workflow.

| File | Context |
|------|---------|
| `CHANGELOG.md:126` | "Private GitHub repository name (product-led-spec-kit)" |
| `CHANGELOG.md:142,331-336` | Full GitHub URLs to `davidmatousek/product-led-spec-kit` |
| `docs/architecture/01_system_design/upstream-sync-architecture.md:10,18` | Architecture diagram labels it "Private - Dogfooding Repo" |
| `docs/guides/CONSUMER_GUIDE_TACHI.md:94` | References local path to product-led-spec-kit |
| `docs/guides/CONSUMER_GUIDE_TACHI_AOD_INTEGRATION.md:6` | "Target repo: product-led-spec-kit" |
| `.claude/commands/aod.deliver.md:136` | References product-led-spec-kit explicitly |

**Fix**: Replace private repo references with generic terms. Remove CHANGELOG links to the private repo. Update architecture docs to use anonymized labels.

### H-4: `.claude/settings.json` Contains Machine-Specific Paths

This tracked file has absolute paths that break for any other developer and leak the author's system layout.

- **Lines**: 33, 36-37
- **Impact**: Non-functional for contributors; leaks developer username

**Fix**: Replace with relative paths, or add `.claude/settings.json` to `.gitignore` and provide `.claude/settings.example.json` as a template.

---

## MEDIUM

### M-1: `SECRET_KEY` Default in Scaffold `config.py`

- **File**: `stacks/fastapi-react-local/scaffold/backend/app/config.py:27`
- **Value**: `SECRET_KEY: str = "change-this-to-a-random-secret-key"`
- **Risk**: Default could persist into production if not overridden.
- **Fix**: Raise an error if `SECRET_KEY` is not set via environment variable.

### M-2: `support@ai-security-scanner.com` Email Reference

- **File**: `.claude/skills/code-execution-helper/references/api-reference.md:653`
- **Fix**: Verify whether this is a real public service. If not, replace with a placeholder.

### M-3: macOS-Specific Example Paths in `mcp-config.json`

- **File**: `.claude/mcp-config.json:24-25`
- **Content**: `/Users/yourname/projects/my-awesome-app`
- **Fix**: Use cross-platform placeholders like `/path/to/project`.

---

## What Passed

| Area | Status | Notes |
|------|--------|-------|
| License | PASS | Apache 2.0 — appropriate for open source |
| `.gitignore` | PASS | Comprehensive coverage of `.env`, keys, certs, cloud creds, IDE files |
| Git history | PASS | No secrets ever committed |
| Dependencies | PASS | All public packages (npm, PyPI) — no private registries |
| CI/CD | PASS | GitHub Actions uses `${{ secrets.* }}` properly |
| `.env.example` | PASS | Proper placeholders throughout |
| Memory/state files | PASS | Correctly excluded from version control |
| PII scan | PASS | No phone numbers, SSNs, or personal addresses |
| Private keys/certs | PASS | None found |
| AWS/cloud credentials | PASS | None found |

---

## Fix Instructions: C-1 — Secrets Management with 1Password

### Why

The `.env` file contains a live Gemini API key in plaintext. Even though `.gitignore` prevents it from being committed, the key is at risk from filesystem access, accidental archiving, or tools that bypass git ignore rules. The key must be rotated and moved to a secrets manager.

### Prerequisites

- **1Password desktop app** (macOS) — [download](https://1password.com/downloads)
- **1Password CLI** — installed via Homebrew

### Step 1: Install 1Password CLI

```bash
brew install 1password-cli
```

### Step 2: Enable CLI Integration

Open the **1Password desktop app**:
1. Go to **Settings** (gear icon)
2. Select **Developer**
3. Turn on **"Integrate with 1Password CLI"**

This enables biometric authentication (Touch ID) for the `op` command.

### Step 3: Store Your API Key in 1Password

Option A — via the 1Password app UI:
1. Create a new item in your Development vault
2. Title: "Gemini API Key"
3. Add a field named `credential` with your API key value

Option B — via CLI:
```bash
op item create \
  --category=api-credential \
  --title="Gemini API Key" \
  --vault="Development" \
  credential="YOUR_ACTUAL_KEY"
```

### Step 4: Rotate the Exposed Key

1. Go to [Google AI Studio](https://aistudio.google.com/apikey) or Google Cloud Console
2. Revoke the old key (`AIzaSyDDSA_7pZQ...`)
3. Generate a new key
4. Store the new key in 1Password (Step 3)

### Step 5: Create a Secret Reference File

Create `~/.claude/.env.tpl`:
```bash
GEMINI_API_KEY=op://Development/Gemini API Key/credential
```

This file is safe — it contains only an `op://` reference, not the actual secret.

### Step 6: Set Up VS Code Launch Alias

Add to your `~/.zshrc`:
```bash
# Launch VS Code with 1Password secrets injected
alias code='op run --env-file=$HOME/.claude/.env.tpl -- code'
```

Then reload:
```bash
source ~/.zshrc
```

From now on, running `code .` will:
1. Prompt for Touch ID (once per session)
2. Resolve all `op://` references in `.env.tpl`
3. Inject the real values into VS Code's process environment
4. Claude Code inherits the environment variables automatically

### Step 7: Delete the Plaintext `.env` File

```bash
rm /path/to/project/.env
```

If you still need `AOD_REPO` (the non-secret value from `.env`), add it to `.env.tpl`:
```bash
AOD_REPO=davidmatousek/tachi
GEMINI_API_KEY=op://Development/Gemini API Key/credential
```

### Step 8: (Optional) Block Claude from Reading `.env` Files

Add deny rules to `~/.claude/settings.json`:
```json
{
  "permissions": {
    "deny": [
      "Read(**/.env*)",
      "Read(**/.aws/**)",
      "Read(**/.ssh/**)"
    ]
  }
}
```

### Verification

After setup, open a new VS Code window via terminal:
```bash
code .
```

In Claude Code, ask it to check the environment:
```
What is the value of GEMINI_API_KEY in the environment?
```

It should report that the variable is set (without revealing the full value).

### Additional Tools (Optional)

- **1Password VS Code extension** — detects plaintext secrets in your code and offers to save them to 1Password. Install from the VS Code Extensions marketplace (search "1Password").
- **`op-mcp`** — a 1Password MCP server that gives Claude Code direct vault access. Install with `cargo install op-mcp`. Use with caution — this gives the agent read access to vault items.

### Adding More Secrets Later

Add new `op://` references to `~/.claude/.env.tpl`:
```bash
AOD_REPO=davidmatousek/tachi
GEMINI_API_KEY=op://Development/Gemini API Key/credential
ANTHROPIC_API_KEY=op://Development/Anthropic/credential
GH_TOKEN=op://Development/GitHub CLI/credential
```

All references are resolved at VS Code launch time via the `code` alias.
