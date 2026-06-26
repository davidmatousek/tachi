# Platform Compatibility

**Status**: Active public compatibility matrix
**Last Updated**: 2026-06-23
**Purpose**: map harness support to native adapters, thin shims, and generic fallback
**Scope**: install paths, first-run entrypoints, and fallback behavior

## Core Contract

tachi keeps one canonical threat logic source and renders it into multiple
delivery shapes:

- Canonical source: `agents/`, `schemas/`, `templates/`, and
  `INSTALL_MANIFEST.md`
- Stable commands: `/tachi.threat-model`, `/tachi.risk-score`,
  `/tachi.compensating-controls`, `/tachi.infographic`,
  `/tachi.security-report`, and `/tachi.architecture`
- Stable outputs: `threats.md`, `threats.sarif`, `threat-report.md`, and the
  infographic/report artifacts described by the docs
- Stable install layout: platform adapters under `adapters/<platform>/`, the
  GitHub Actions workflow file under `adapters/github-actions/`, and the
  generic prompt pack under `adapters/generic/prompts/`

Adapters only repackage the same payload. They do not fork the threat model
logic.

## Standalone MCP Server

The standalone MCP server is the transport-neutral alternative to the harness
packs. It exposes the canonical analysis commands over stdio while keeping the
same output names and artifact paths.

Build and run it with:

```bash
cargo build -p tachi-mcp --features stdio
cargo run -p tachi-mcp --features stdio -- --stdio
```

The same canonical tool names apply:

| Tool | Canonical artifact |
|---|---|
| `tachi.coverage-audit` | `target/mcp/coverage-audit.txt` |
| `tachi.infographic-data` | `target/mcp/infographic-data.json` |
| `tachi.report-data` | `target/mcp/report-data.typ` |
| `tachi.risk-scores-sarif` | `target/mcp/risk-scores-sarif.sarif` |
| `tachi.threats-sarif` | `target/mcp/threats-sarif.sarif` |

Validation:

```bash
cargo test -p tachi-mcp --test contract_snapshot --test schema_snapshot --test tools_registration --test session_policy --test stdio
```

## Support Levels

| Level | Meaning |
|---|---|
| Native adapter | Dedicated rendered package for a specific harness or runtime. |
| Thin shim | Harness-specific launch docs or a tiny wrapper around the generic prompt pack. |
| Generic fallback | Use the generic prompt pack directly; no harness-specific packaging. |

## Compatibility Matrix

| Harness | Support level | Install surface | First-run entrypoint | Notes |
|---|---|---|---|---|
| Claude Code | Native adapter | `adapters/claude-code/agents/` | `/tachi.threat-model` | Active agent dispatch through Claude Code's Agent tool. |
| Cursor | Native adapter | `adapters/cursor/rules/` | Ask Cursor to run a complete tachi threat model | Passive context injection through Cursor rules. |
| Copilot | Native adapter | `adapters/copilot/agents/` and `adapters/copilot/instructions/` | `@tachi-orchestrator` | Oversized agents use split agent + instructions files. |
| GitHub Actions | Native adapter | `adapters/github-actions/tachi.threat-model.yml` | Pull request or manual dispatch | Runtime LLM invocation plus SARIF upload. |
| Codex | Thin shim | `adapters/generic/prompts/` | Paste `00-orchestrator.md`, then run prompts in order | Use the same canonical prompt payload without a Codex-specific agent pack. |
| OpenCode | Thin shim | `adapters/generic/prompts/` | Paste `00-orchestrator.md`, then run prompts in order | Same generic prompt pack, different chat or CLI wrapper. |
| Pi-style harnesses | Generic fallback | `adapters/generic/prompts/` | Paste the numbered prompts in sequence | Best fit for constrained or minimalist LLM shells. |
| Termux | Thin shim | `adapters/generic/prompts/` | Copy the prompt files into the shell and run them in order | Shell-friendly launch path, but no native agent format. |
| Voltagent | Thin shim | `adapters/generic/prompts/` | Feed the generic prompts through the harness wrapper | Keeps the same payload shape while adapting launch metadata. |
| Antigravity | Thin shim | `adapters/generic/prompts/` | Feed the generic prompts through the harness wrapper | Same core contract, different packaging and launch metadata. |
| Unsupported client | Generic fallback | `adapters/generic/prompts/` | Paste or API-call the numbered prompts | If the harness is not listed, use the generic pack. |

## Setup Recipes

### Native adapters

Use the platform pack that matches your harness:

```bash
# Claude Code
cp -r adapters/claude-code/agents/ .claude/agents/tachi/

# Cursor
cp -r adapters/cursor/rules/ .cursor/rules/tachi/

# Copilot
mkdir -p .github/agents/tachi .github/instructions
cp adapters/copilot/agents/*.agent.md .github/agents/tachi/
cp adapters/copilot/instructions/*.instructions.md .github/instructions/

# GitHub Actions
cp adapters/github-actions/tachi.threat-model.yml .github/workflows/
```

### Generic fallback

Use the numbered prompt pack when no native adapter exists:

```bash
cp -r adapters/generic/prompts/ ~/tachi-prompts/
```

Then run the prompts in order:

1. `00-orchestrator.md`
2. `01-spoofing.md` through `11-tool-abuse.md`
3. `12-threat-report.md`
4. `13-threat-infographic.md`

Replace `{{ARCHITECTURE_INPUT}}` in the orchestrator prompt with your actual
architecture description before you run it.

## Fallback Behavior

If a harness does not have a native adapter:

1. Use the generic prompt pack.
2. Keep the prompt order unchanged.
3. Preserve the stable command names and output filenames.
4. Do not add new threat logic to the wrapper.

That fallback path is intentional. It keeps the core contract stable even when
the surrounding harness cannot load native agent files.

## Known Limitations

- Native adapters preserve the harness's own activation model; thin shims and
  generic fallback do not.
- Termux and Pi-style harnesses are launch-environment constrained, so the
  generic prompt pack is the supported path there.
- The adapter layer does not add new threat logic. If a harness needs a new
  package shape, it should still consume the same prompts, commands, and
  artifacts.
