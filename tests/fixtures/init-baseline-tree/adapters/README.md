# adapters/

This directory serves two purposes:

1. **Knowledge-system configuration** — Files that control how tachi's threat modeling agents load context, score threats, and format output
2. **Platform adapters** — Subdirectories that package tachi's 14 core threat agents into native formats for specific AI coding platforms

## Knowledge-System Configuration

- `ContextLoading.yaml` — Defines when and how agents load context (architecture inputs, reference data, terms)
- `ScoringRubric.md` — Threat severity scoring criteria (likelihood, impact, risk rating)
- `ProjectMeta.yaml` — Project-level metadata (name, version, default output format)
- `Terms/` — Domain terminology files for consistent threat language
- `Presets/` — Output presets for different audiences (security team, executive summary, compliance)

## Platform Adapters

Each adapter transforms tachi's core agents (`agents/`) into the native format required by the target platform. All file-transformation adapters preserve 100% of prompt content — only metadata and path references change.

| Adapter | Directory | Format | Priority | Install Target |
|---------|-----------|--------|----------|----------------|
| Claude Code | `claude-code/` | `.md` with `name`/`description` frontmatter | P0 | `.claude/agents/tachi/` |
| Generic | `generic/` | Numbered `.md` prompt files (no frontmatter) | P0 | Any LLM chat UI or API |
| Cursor | `cursor/` | `.mdc` rule files with `alwaysApply`/`description` | P1 | `.cursor/rules/tachi/` |
| Copilot | `copilot/` | `.agent.md` + `.instructions.md` for oversized agents | P1 | `.github/agents/tachi/` |
| GitHub Actions | `github-actions/` | Workflow YAML with SARIF output | P1 | `.github/workflows/` |

Each adapter includes:
- **README.md** — Installation instructions and platform prerequisites
- **VERSION** — Source commit SHA and file checksums for traceability

See individual adapter READMEs for installation and usage instructions.
