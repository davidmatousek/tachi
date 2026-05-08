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
- **Third-party MCP servers** → report to their maintainers.
- **Adopter personalization data** (`.aod/personalization.env`, `brands/*/`) → adopter's responsibility.
- **Adopter-modified scaffold output** (post-`make scaffold` customizations) → adopter's responsibility.
- **Threat-model accuracy concerns** (false positives, missed threats) → file as regular [GitHub Issues](https://github.com/davidmatousek/tachi/issues), not security advisories.
