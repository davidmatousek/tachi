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
- Draft PR opened at plan stage, marked ready at delivery
- Branch format: `NNN-descriptive-name` (e.g., `021-feature-name` for Issue #21)

## Project Structure
```
tachi/
├── .claude/           → Agents, skills, commands, design archetypes
├── .aod/              → Active feature workspace (spec.md, plan.md, tasks.md)
├── brands/            → Brand identity assets (vision + design tokens)
├── specs/             → Archived feature artifacts (per-feature history)
├── docs/              → Product, architecture, devops docs
├── scripts/           → init.sh, check.sh
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
- `/aod.discover` → `/aod.score`

**Post-init** (recommended after `make init`):
- `/aod.foundation` — Guided workshop: product vision + design identity

**Triad workflow**:
- `/aod.define` → `/aod.plan` → `/aod.build [--no-security] [--no-design-check]`
- (`/aod.plan` chains: spec → project-plan → tasks automatically)

**Post-delivery**:
- `/aod.deliver` — Close completed feature
- `/aod.document [--autonomous]` — Quality review: simplify, docstrings, CHANGELOG, API docs (--autonomous for orchestrator-driven runs)

**Downstream Updates** (adopter-side template sync):
- `/aod.update` — Apply upstream PLSK template updates to your project. Direction: `PLSK → user`. See `docs/guides/DOWNSTREAM_UPDATE.md`.
- `/aod.sync-upstream` — Push local template improvements back to the public PLSK repo. Direction: `user → PLSK`.

**Terminology**: `sync-upstream` = `user → PLSK` (contribute back). `update` = `PLSK → user` (pull updates). These are opposite-direction commands — do not confuse them.

**Supporting commands**:
- `/aod.clarify` — Resolve spec ambiguities
- `/aod.analyze` — Cross-artifact consistency check
- `/aod.checklist` — Generate quality checklist
- `/aod.constitution` — Manage governance principles
- `/aod.kickstart` — POC kickstart: generate consumer guide with seed features
- `/aod.blueprint` — Multi-feature story generation from consumer guide
- `/aod.status` — View backlog and lifecycle stage summary
- `/aod.roadmap` — Scaffold quarterly roadmap from completed PRDs
- `/aod.okrs` — Scaffold OKR document with standard template
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
- **Feature 206** (2026-04-24): `misinformation` threat agent (OWASP LLM09:2025)
  - New AI-tier detection agent `.claude/agents/tachi/misinformation.md` + companion skill `tachi-misinformation/` — 5 factual-integrity pattern categories (Ungrounded Factual Emission / Citation Fabrication / Overreliance-Missing-HITL / Retrieval-Grounding Gap / Confidence-Calibration Absence)
  - BLP-01 Tier 1 F-2 — 2nd Tier-1 feature after F-1 (Feature 201); closes LLM09:2025 on the Coverage Matrix (Planned → Covered)
  - ADR-031 (Accepted) cross-refs ADR-030 Decision 1 (Heuristic A inheritance — factual-integrity carve-out) and ADR-030 Decision 8 (regex-alternation minor-bump rule — 2nd application)
  - Schema `finding.yaml` 1.6 → 1.7 — `MI` prefix added to `id.pattern` regex alternation (11 values now: `S|T|R|I|D|E|AG|LLM|AGP|OI|MI`) under the additive-compatibility conditions of ADR-026 extended by ADR-030 D8
  - Three-signal-class discipline: `LLM-{N}` (input-side, LLM01) / `OI-{N}` (output sanitization, LLM05) / `MI-{N}` (factual integrity, LLM09) render adjacent with distinct `source_attribution` primaries
  - 24-file zero-edit invariant preserved (22 original + F-1's 2) — F-2 is a net-new addition, not a refactor
  - F-2 is the **second net-new producer** of `source_attribution` (F-1 was first) — F-A2 referential-integrity contract proven against two independent populators
- **v2.0.0**: Anthropic Claude Code v2.1.16 Integration
  - Parallel Triad reviews, context forking, version detection
  - See `docs/devops/MIGRATION.md` for upgrade guide
- **v1.1.0**: Modular rules system
