# Security Policy

## Supported Versions

Only the latest minor of `v4.x` receives security updates. Older minors are deprecated immediately on the next minor release.

**Worked example**: `v4.32.0` is the current latest minor (released 2026-05-07). Once `v4.33.0` ships, `v4.32.x` will be deprecated for security purposes immediately. Adopters consuming via `make update` should pin to the major line (`v4.x`) rather than a specific minor; adopters who require longer-than-rolling support windows for a specific minor should fork or adopt the same backport pattern themselves.

## Reporting a Vulnerability

Use the **Report a vulnerability** button on the [Security tab](https://github.com/davidmatousek/tachi/security) of this repo.

Or navigate directly to `https://github.com/davidmatousek/tachi/security/advisories/new` to open a private advisory.

Please do not open a public GitHub Issue for security vulnerabilities — public Issues broadcast the vulnerability before a fix is available.

### What to include

- Description of the vulnerability
- Steps to reproduce
- Affected components (agents, commands, schemas, templates, scripts)
- Potential impact

> **Maintainers: this channel relies on the GitHub Private Vulnerability Reporting toggle being enabled in repo Settings → Security.**

## What to expect

- **Acknowledgment** within 5 business days.
- **Assessment** within 1 week of acknowledgment.
- **Fix or mitigation** timeline communicated after assessment.
- **Credit** in the fix commit and release notes by default; anonymity available on request.

## Scope

In-scope for private vulnerability reports:

- **tachi codebase paths**: `.aod/scripts/bash/`, `.claude/agents/`, `.claude/commands/`, `.claude/skills/`, `stacks/`
- **Stack-pack scaffolds as shipped**: `stacks/*/scaffold/` — vulnerabilities in tachi's default scaffolded templates are in-scope.
- **Schema definitions**: `contracts/`, `schemas/`
- **Template content** that shapes report generation
- **tachi-shipped configuration files** that reference external services or credentials

## Out-of-scope

The following are not handled through this private disclosure channel:

- **Claude Code itself** → report to Anthropic.
- **Out-of-scope model behaviour** you observe as a member of an Anthropic program such as the Cyber Verification Program → report it to Anthropic through the program's own channel, the Verification Portal. The [runbook](docs/guides/ISOLATED_OPERATION_TACHI.md) lists the reporting routes, including any reporting address that a public Anthropic page names. A vulnerability in tachi itself still goes through the private advisory route above.
- **Third-party MCP servers** → report to their maintainers.
- **Adopter personalization data** (`.aod/personalization.env`, `brands/*/`) → adopter's responsibility.
- **Adopter-modified scaffold output** (post-`make scaffold` customizations) → adopter's responsibility.
- **Threat-model accuracy concerns** (false positives, missed threats) → file as regular [GitHub Issues](https://github.com/davidmatousek/tachi/issues), not security advisories.

## Data handling

Your Claude Code model provider receives the architecture description, the files tachi reads and the findings on every run. If you set `GEMINI_API_KEY` and run `/tachi.infographic`, Google's Gemini API (`generativelanguage.googleapis.com`) also receives image prompts made of tachi's fixed layout instructions and derived threat-model content, including names and descriptions taken from your architecture (the project name and assessment date; the names, types and short descriptions of components, trust zones, trust boundaries and data flows; finding IDs, descriptions, severities and risk scores; correlation groups of related findings and their descriptions; finding counts, severities and analysis coverage, overall and by component, zone, boundary, flow, threat category and MAESTRO layer; the overall risk posture; control-coverage and risk-reduction figures from compensating-control runs; counts of new, updated, unchanged and resolved findings since a baseline, with new findings marked; and, if a template cannot be loaded, a one-line system description). By design, tachi sends nothing else, but an AI agent following tachi's templates writes each prompt, and no code checks it against this list before it is sent. Claude Code's own operational traffic, such as usage metrics, error reports and feature-flag fetches, is separate from tachi; it is governed by Claude Code's [privacy and telemetry settings](https://code.claude.com/docs/en/data-usage#telemetry-services), and setting `CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC=1` turns these off.

The [isolated-operation runbook](docs/guides/ISOLATED_OPERATION_TACHI.md) covers running tachi in a sandbox: the egress profile, a session profile, write locations, retention and reporting routes.
