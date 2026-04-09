# CLAUDE.md - tachi

<!-- Context Budget: Target <100 lines (justified: 10-line return policy saves 9K-36K tokens/session) -->

## Core Constraints
- **Product-Led**: Start with product vision, PRDs, and user stories
- **Source of Truth**: `.aod/spec.md`
- **Validation Required**: Run `/aod.analyze` before PRs
- **Local-First**: Always supports local `.aod/` file workflows

## Git Workflow
**Always use feature branches**: `git checkout -b NNN-feature-name`
- **NNN** = GitHub Issue number, zero-padded to 3 digits
- Never commit to main directly
- Create PR for review before merge
- Branch format: `NNN-descriptive-name` (e.g., `021-feature-name` for Issue #21)

## Project Structure
```
tachi/
├── .claude/           → Agents, skills, commands
├── .aod/              → Active feature workspace (spec.md, plan.md, tasks.md)
├── examples/          → Reference threat models (architecture + threats.md pairs)
├── specs/             → Archived feature artifacts (per-feature history)
├── docs/              → Product, architecture, devops docs
├── scripts/           → init.sh, check.sh, install.sh
├── stacks/            → Stack packs (conventions, personas, scaffolds)
└── CLAUDE.md          → AI agent context
```

**Note**: Template provides methodology only. Users bring their own code.

## Context Discovery
- **Thinking Lenses**: `docs/core_principles/README.md` (5 Whys, Pre-Mortem, etc.)
- **Project Standards**: `docs/standards/README.md` (DoD, naming, git)
- **Product Docs**: `docs/product/README.md`
- **Architecture**: `docs/architecture/README.md`
- **Triad Guide**: `docs/AOD_TRIAD.md`
- **Constitution**: `.aod/memory/constitution.md`

## Commands
**PDL workflow** (optional, before Triad):
- `/aod.discover` → `/aod.discover` → `/aod.score` → `/aod.validate`

**Triad workflow**:
- `/aod.define` → `/aod.plan` → `/aod.build [--no-security]`
- (`/aod.plan` chains: spec → project-plan → tasks automatically)

**Post-delivery**:
- `/aod.deliver` — Close completed feature
- `/aod.document` — Human-driven quality review (simplify, docstrings, CHANGELOG, API docs)

**Supporting commands**:
- `/aod.clarify` — Resolve spec ambiguities
- `/aod.analyze` — Cross-artifact consistency check
- `/aod.checklist` — Generate quality checklist
- `/aod.constitution` — Manage governance principles
- `/aod.kickstart` — POC kickstart: generate consumer guide with seed features from a project idea
- `/aod.stack` — Manage stack packs (activate, remove, list, scaffold)

## SDLC Triad Governance
| Role | Defines | Authority |
|------|---------|-----------|
| PM | What & Why | Scope & requirements |
| Architect | How | Technical decisions |
| Team-Lead | When & Who | Timeline & resources |

**Sign-off Requirements**:
- `spec.md`: PM sign-off
- `plan.md`: PM + Architect sign-off
- `tasks.md`: PM + Architect + Team-Lead sign-off

## Deployment Policy
All deployments must go through the devops agent. Never deploy without verification.

## Subagent Return Policy
When invoked as a subagent (via Agent tool), return ONLY:
1. **Status** (APPROVED / CHANGES_REQUESTED / BLOCKED / pass / fail)
2. **Item count** (if applicable)
3. **File path** to `.aod/results/{agent-name}.md` with full details
- Write detailed findings to results file BEFORE returning
- Max return: 15 lines / ~200 tokens
- NEVER return code snippets, file contents, or multi-paragraph explanations
- Policy applies to subagent→main returns only, not user-facing output

## Key Principles
- **Vision First**: `/aod.define` (includes vision) → `/aod.plan` (spec → plan → tasks)
- **Triple Sign-off**: PM + Architect + Team-Lead approval on tasks.md
- **Definition of Done**: 3-step validation before marking complete

## Context Boundaries
**EXCLUDE**: `archive/`, `node_modules/`, `.git/`, `*.log`
**FOCUS**: `.aod/`, `docs/`, `.claude/`, current feature branch

## Tips
- Use `make review-spec` or `make review-plan` for manual governance checks
- Search `docs/core_principles/` for thinking methodologies
- Review `agent-assignments.md` for workload distribution

## Recent Changes
- **Feature 120**: Architecture Lifecycle Command
  - Version tracking: `/tachi.architecture` adds YAML frontmatter (version, date, description, checksum, previous_version) to generated architecture files
  - Archive mechanism: previous versions archived to `{parent_dir}/.archive/v{N}/architecture.md` before updates; legacy files (no frontmatter) archived as v0
  - Threat model snapshot: `/tachi.threat-model` copies architecture file verbatim into timestamped output folder (Step 1.4)
  - Guided update mode: walks users through change categories (services, components, data flows, trust boundaries, external entities, AI capabilities)
  - Two-pass checksum: SHA-256 computed on body content via `shasum -a 256` before frontmatter injection
  - Backward compatible: example architecture files unchanged, downstream pipeline stages unaffected
- **Feature 121**: Rename Tachi Commands to `tachi.*` Namespace
  - All 6 pipeline commands renamed: `/threat-model` to `/tachi.threat-model`, `/risk-score` to `/tachi.risk-score`, `/compensating-controls` to `/tachi.compensating-controls`, `/infographic` to `/tachi.infographic`, `/security-report` to `/tachi.security-report`
  - New `/tachi.architecture` command added for generating architecture descriptions
  - Cross-references updated across entire codebase (agents, schemas, templates, docs, examples, adapters)
  - Install script (`scripts/install.sh`) handles cleanup of old command files
  - GitHub Actions workflow renamed: `tachi-threat-model.yml` to `tachi.threat-model.yml`
  - No new dependencies or architectural changes -- naming/namespace migration only
- **Feature 112**: Attack Path Pages in Security Report PDF
  - New Typst page template `templates/tachi/security-report/attack-path.typ` for attack path visualization pages
  - New functions in `scripts/extract-report-data.py`: `parse_attack_trees()`, `render_mermaid_to_png()`, narrative/remediation builders
  - Updated `scripts/tachi_parsers.py`: `detect_artifacts()` now detects `attack-trees/` directory
  - Updated `templates/tachi/security-report/main.typ`: import, defaults, conditional page sequencing after Executive Summary
  - Updated `.claude/commands/tachi.security-report.md` and `.claude/agents/tachi/report-assembler.md`: artifact detection tables
  - Conditional inclusion gated by `has-attack-trees` boolean; backward compatible with existing reports
  - All 6 examples validated (2 with attack trees, 4 without)
- **Feature 104**: Downstream Baseline Propagation
  - Propagates baseline severity and status fields from `threats.md` downstream through all pipeline stages
  - New parser functions in `scripts/tachi_parsers.py`: `parse_baseline_frontmatter`, `parse_resolved_findings`, updated `parse_threats_findings` with delta fields
  - Updated output schemas: `threats.md` (Section 8 Delta Summary, Status column in Section 7), `threat-report.md` (schema_version 1.0 to 1.1, Section 8 Delta Summary, baseline frontmatter fields)
  - Updated agents: `threat-report` (delta-aware narrative), `threat-infographic` (delta-aware extraction), `report-assembler` (baseline data assembly)
  - Updated scripts: `extract-report-data.py`, `extract-infographic-data.py` (baseline field extraction)
  - Updated commands: `tachi.infographic.md`, `tachi.security-report.md` (baseline data display)
  - All 6 example outputs regenerated with baseline columns
- **Feature 084**: MAESTRO Layer Mapping (CSA seven-layer taxonomy for agentic AI)
  - New `maestro_layer` field in `schemas/finding.yaml` (schema_version 1.1 to 1.2)
  - Orchestrator Phase 1 keyword classification, finding inheritance, SARIF tags
  - Downstream propagation: risk-scorer, control-analyzer, threat-report
  - New shared reference: `.claude/skills/tachi-shared/references/maestro-layers-shared.md`
  - All 6 example outputs regenerated with MAESTRO layer columns
- **Feature 091**: MAESTRO Infographic Templates and PDF Report Section
  - Two new MAESTRO-aware infographic templates: `maestro-stack` (layered stack diagram) and `maestro-heatmap` (layer x severity heat map)
  - New Typst page `maestro-findings.typ` for MAESTRO Findings section in PDF security report
  - MAESTRO data extraction in `extract-infographic-data.py` and `extract-report-data.py`
  - `maestro` shorthand dispatch in `/tachi.infographic` command; all gated by `has-maestro-data` for backward compatibility
- **Feature 086**: Automated Release Tagging via GitHub Actions
  - release-please workflow for version tagging and CHANGELOG generation on merge to main
  - New files: `.github/workflows/release-please.yml`, `release-please-config.json`, `.release-please-manifest.json`
- **v2.0.0**: Anthropic Claude Code v2.1.16 Integration
  - Parallel Triad reviews, context forking, version detection
  - See `docs/devops/MIGRATION.md` for upgrade guide
- **v1.1.0**: Modular rules system
