# GitHub Actions Adapter

This adapter provides a GitHub Actions workflow that runs tachi threat analysis on pull requests when architecture files change. Unlike file-transformation adapters (Claude Code, Cursor, Copilot), this workflow does not copy or transform agent files. Instead, it reads the source agents from the `agents/` directory at runtime and invokes them via LLM API.

## How It Differs

| Adapter | Approach |
|---------|----------|
| Claude Code, Cursor, Copilot, Generic | **File transformation** -- copies and reformats agent markdown files into platform-specific directories |
| GitHub Actions | **Runtime invocation** -- reads source agent prompts from the repository and sends them to an LLM API as system instructions |

The workflow ships as a single `.yml` file. All 14 tachi agents (orchestrator, 6 STRIDE, 5 AI/LLM, 2 report) are referenced from their canonical source paths in `agents/` at execution time.

## Prerequisites

- GitHub repository with Actions enabled
- LLM API key (supports Anthropic Claude)
- tachi repository with source agents in the `agents/` directory
- GitHub Advanced Security enabled (for SARIF upload to Code Scanning)

## Installation

Copy the workflow file into your repository's GitHub Actions directory:

```bash
cp adapters/github-actions/tachi-threat-model.yml .github/workflows/
```

Then add your LLM API key as a repository secret:

1. Go to **Settings > Secrets and variables > Actions**
2. Click **New repository secret**
3. Name: `LLM_API_KEY`
4. Value: Your Anthropic API key

## Configuration

### Repository Secret

| Secret | Required | Description |
|--------|----------|-------------|
| `LLM_API_KEY` | Yes | Anthropic API key (or compatible provider key) |

### Trigger Paths

The workflow triggers automatically on pull requests that modify architecture files. Default paths:

- `docs/architecture/**`
- `**/*.mermaid`
- `**/*.puml`
- `**/*.drawio`

To customize, edit the `paths` array under the `pull_request` trigger in the workflow file.

### Workflow Dispatch Inputs

The workflow also supports manual dispatch (`workflow_dispatch`) with configurable inputs:

| Input | Default | Description |
|-------|---------|-------------|
| `architecture-path` | `docs/architecture/` | Path to architecture file(s) to analyze |
| `llm-provider` | `anthropic` | LLM provider identifier |
| `llm-model` | `claude-sonnet-4-20250514` | Model identifier (must support 200K+ context) |
| `max-tokens` | `16384` | Maximum tokens for LLM response |

### Permissions

The workflow requests the following GitHub token permissions:

| Permission | Level | Purpose |
|------------|-------|---------|
| `contents` | read | Checkout repository and read architecture files |
| `security-events` | write | Upload SARIF to Code Scanning |
| `pull-requests` | read | Access PR metadata for diff detection |

## Context Window Requirements

The orchestrator agent prompt is approximately 30K tokens. Combined with architecture input, the model must support a context window of **200K+ tokens**. The workflow warns if architecture input exceeds 75% of the estimated context capacity (~600K bytes).

## Supported LLM Providers

| Provider | Status | Configuration |
|----------|--------|---------------|
| Anthropic (Claude) | Supported | Set `LLM_API_KEY` secret, use default provider |
| Others | Extensible | Requires adding a provider block in the LLM invocation step |

## Outputs

The workflow produces two artifacts:

### threats.md

Full threat model analysis in markdown format. Contains structured findings with threat IDs, severity ratings, affected components, descriptions, and mitigations. Uploaded as a downloadable workflow artifact under the name `tachi-threat-model`.

### threats.sarif

SARIF 2.1.0 (Static Analysis Results Interchange Format) file containing all parsed threat findings. Uploaded to GitHub Code Scanning, making findings visible in the repository's **Security > Code scanning alerts** tab.

Each finding includes:
- Rule ID mapped to tachi threat categories (e.g., `tachi/stride/spoofing`, `tachi/ai/prompt-injection`)
- Severity mapped to SARIF levels (`error` for Critical/High, `warning` for Medium, `note` for Low)
- Security severity scores for GitHub's severity classification
- Logical location identifying the affected component

## Error Handling

The workflow handles failure conditions with actionable error messages:

| Condition | Behavior |
|-----------|----------|
| Missing `LLM_API_KEY` | Fails with instructions to configure the secret |
| Authentication failure (401/403) | Fails with message to verify the API key |
| Rate limiting (429) | Retries once after 60-second backoff, then fails with rate limit guidance |
| Request timeout | Fails with suggestion to reduce architecture input size |
| Empty LLM response | Fails with message indicating possible model refusal |
| No architecture files changed | Skips analysis, posts informational job summary |
| No structured findings parsed | Creates an informational SARIF entry so the upload remains valid |

## SARIF Deduplication

The workflow generates deterministic fingerprints for each finding using SHA-256 of `rule_id:title:component`. This ensures:

- The same threat on the same component produces the same fingerprint across workflow runs
- GitHub Code Scanning deduplicates identical findings instead of creating duplicate alerts
- Findings are stable across re-runs unless the underlying threat or component changes

Each finding also includes a `findingId/v1` partial fingerprint containing the tachi threat ID (e.g., `S-1`, `PI-2`) for traceability back to the markdown output.

## Verification

1. **Install the workflow**:
   ```bash
   cp adapters/github-actions/tachi-threat-model.yml .github/workflows/
   ```

2. **Set the API key** as a repository secret (`LLM_API_KEY`).

3. **Trigger a run** by either:
   - Opening a pull request that modifies a file under `docs/architecture/`
   - Manually dispatching the workflow from **Actions > tachi-threat-model > Run workflow**

4. **Check the workflow run** in the **Actions** tab. The job summary shows finding count, model used, and artifact links.

5. **Download artifacts** from the workflow run page to review `threats.md` and `threats.sarif`.

6. **View Code Scanning alerts** in the **Security > Code scanning alerts** tab. SARIF findings appear as security alerts with severity classification.

## Workflow Steps

| Step | Description |
|------|-------------|
| Checkout repository | Full clone with history for PR diff detection |
| Detect architecture files | Identifies changed files (PR mode) or uses input path (dispatch mode) |
| Read architecture input | Concatenates architecture file contents into a single input |
| Read orchestrator prompt | Loads the orchestrator agent prompt and extracts tool version |
| Invoke LLM API | Sends architecture input to the LLM with the orchestrator as system prompt |
| Parse output | Saves LLM response as `threats.md` |
| Generate SARIF | Parses structured findings from markdown and assembles SARIF 2.1.0 document |
| Upload SARIF | Uploads to GitHub Code Scanning via `github/codeql-action/upload-sarif@v3` |
| Upload artifacts | Uploads `threats.md` and `threats.sarif` as downloadable workflow artifacts |
| Job summary | Posts finding count and links to the workflow summary |

## Uninstallation

Remove the workflow file from your repository:

```bash
rm .github/workflows/tachi-threat-model.yml
```

Existing Code Scanning alerts from previous runs will remain in the Security tab until manually dismissed.

## VERSION File

The `VERSION` file in this adapter directory contains the source commit SHA, generation date, and SHA-256 checksum of the workflow file. Use it to verify which version of the workflow you have installed.
