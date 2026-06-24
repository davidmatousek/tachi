# Adapters

This directory is the compatibility entrypoint for tachi.

It contains two things:

1. Canonical knowledge-system configuration used by the core installer
2. Platform adapter packs that render the same threat logic for specific harnesses

## Canonical Core Contract

The adapter layer does not own threat logic. The canonical contract remains:

- Prompt source: `agents/`
- Validation and scoring schemas: `schemas/`
- Output templates: `templates/`
- Install inventory: `INSTALL_MANIFEST.md`
- Stable user commands: `/tachi.threat-model`, `/tachi.risk-score`,
  `/tachi.compensating-controls`, `/tachi.infographic`,
  `/tachi.security-report`, and `/tachi.architecture`

Every adapter consumes that same payload shape. Only metadata, file extension,
install location, and launch metadata change.

## What Is Identical Across Platforms

- Threat categories and prompt bodies
- Command names
- Output filenames and artifact roles
- Validation rules and schema contracts
- The source-of-truth relationship to `agents/`

## What Differs by Platform

- Frontmatter or wrapper syntax
- File extension
- Installation path
- Activation model
- Size-splitting requirements for large agents

## Compatibility Matrix

| Harness | Support level | Adapter surface | Notes |
|---|---|---|---|
| Claude Code | Native adapter | `adapters/claude-code/agents/` | Active dispatch via the Agent tool. |
| Cursor | Native adapter | `adapters/cursor/rules/` | Passive context injection via rules. |
| Copilot | Native adapter | `adapters/copilot/agents/` and `adapters/copilot/instructions/` | Size-aware split for oversized agents. |
| GitHub Actions | Native adapter | `adapters/github-actions/tachi.threat-model.yml` | Runtime invocation plus SARIF upload. |
| Codex | Thin shim | `adapters/generic/prompts/` | Use the generic prompt pack with Codex launch docs. |
| OpenCode | Thin shim | `adapters/generic/prompts/` | Use the generic prompt pack with OpenCode launch docs. |
| Pi-style harnesses | Generic fallback | `adapters/generic/prompts/` | Best fit for constrained chat or API clients. |
| Termux | Thin shim | `adapters/generic/prompts/` | Shell-friendly launch path around the generic prompts. |
| Voltagent | Thin shim | `adapters/generic/prompts/` | Wrapper docs only; no unique threat logic. |
| Antigravity | Thin shim | `adapters/generic/prompts/` | Wrapper docs only; no unique threat logic. |

## Adapter Families

### Native adapters

Use the rendered pack that matches your harness when one exists:

- `claude-code/` for Claude Code
- `cursor/` for Cursor
- `copilot/` for GitHub Copilot
- `github-actions/` for GitHub Actions automation

### Generic fallback

Use `generic/` when a harness does not have a native pack or when you want the
same prompt sequence in a plain chat UI or API client.

### Knowledge-system configuration

These files support the core installer and the canonical prompt source:

- `ContextLoading.yaml`
- `ProjectMeta.yaml`
- `ScoringRubric.md`
- `Terms/`
- `Presets/`

## How to Use This Directory

1. Choose the harness support level in [docs/platform-compatibility.md](../docs/platform-compatibility.md).
2. Install the matching adapter pack or the generic fallback prompts.
3. Keep the same command names and output contract regardless of harness.
4. Regenerate adapter artifacts from `agents/` when the canonical prompts change.

## Notes

- Public-facing install guidance lives in `README.md`,
  `docs/platform-compatibility.md`, and `docs/guides/DEVELOPER_GUIDE_TACHI.md`.
- Release validation and publish gating live in the BOM and publish-readiness
  checklist.
