# Project Standards

**Location**: `docs/standards/`
**Purpose**: Centralized repository for development standards, conventions, and quality criteria.

## Standards Index

| Document | Purpose |
|----------|---------|
| [CLAUDE_MD_ORGANIZATION.md](CLAUDE_MD_ORGANIZATION.md) | CLAUDE.md structure and organization |
| [CLAUDE_PERMISSIONS.md](CLAUDE_PERMISSIONS.md) | Self-contained policy decision log for the curated four-category `.claude/settings.json` Claude Code permissions baseline — per-rule rationale, audit-policy framing for SecOps reviewers, settings-precedence with worked examples (within-file + cross-file), three opt-out paths (Path 1 per-tool disable / Path 2 fork-and-edit / Path 3 `.claude/settings.local.json` personal allows), known limitations (Bash pattern fragility R-8, read-only built-in shadow R-10), built-in read-only set maintenance contract. Cross-linked one-to-one with the rules in `.claude/settings.json` via the AC-2 cross-check script. Companion to [ADR-041](../architecture/02_ADRs/ADR-041-claude-permissions-baseline.md) (Feature 277 — F-4 Claude Permissions Baseline, BLP-02 Wave 4) |
| [DEFINITION_OF_DONE.md](DEFINITION_OF_DONE.md) | 3-step validation for feature completion |
| [EVAL_CONVENTIONS.md](EVAL_CONVENTIONS.md) | Eval suite authoring, schema, execution, and grading for Claude Code skills (Feature 083) |
| [FILE_HEADER_STANDARDS.md](FILE_HEADER_STANDARDS.md) | Standard headers for documentation files |
| [FIVE_WHYS_METHODOLOGY.md](FIVE_WHYS_METHODOLOGY.md) | Root cause analysis methodology |
| [GIT_WORKFLOW.md](GIT_WORKFLOW.md) | Git branching, commits, and PR standards |
| [NAMING_GUIDELINES.md](NAMING_GUIDELINES.md) | Naming conventions for files and code |
| [PRECOMMIT_HOOKS.md](PRECOMMIT_HOOKS.md) | Pre-commit secret-scanning configuration, gitleaks rule customization for tachi conventions, install/opt-out/bypass paths, and adopter troubleshooting (Feature 282 — F-5 Pre-commit Secret-Scanning Defaults, BLP-02 Wave 4+). Companion to [ADR-042](../architecture/02_ADRs/ADR-042-pre-commit-secret-scanning-default.md). |
| [PRODUCT_SPEC_ALIGNMENT.md](PRODUCT_SPEC_ALIGNMENT.md) | Product-specification alignment process |
| [SDLC_ORCHESTRATION.md](SDLC_ORCHESTRATION.md) | Development lifecycle coordination |
| [TRIAD_COLLABORATION.md](TRIAD_COLLABORATION.md) | PM/Architect/Team-Lead governance |

## Quick Reference

### Definition of Done

3-step validation for all features:
1. **Pushed to Production** - Code deployed and operational
2. **Playwright MCP Tested** - Browser automation validates workflows
3. **User Validated** - Real-world usage confirmed

### Triad Governance

| Role | Defines | Authority |
|------|---------|-----------|
| PM | What & Why | Scope & requirements |
| Architect | How | Technical decisions |
| Team-Lead | When & Who | Timeline & resources |

## Related Documentation

- [Core Principles](../core_principles/) - Thinking lenses (5 Whys, Pre-Mortem, etc.)
- [Constitution](../../.aod/memory/constitution.md) - Governance principles
