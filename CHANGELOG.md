# Changelog

All notable changes to Agentic Oriented Development Kit (formerly Product-Led Spec Kit) will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### Feature 086 — Automated Release Tagging

**Added**
- Google's release-please GitHub Action for automated version tagging from conventional commits; workflow at `.github/workflows/release-please.yml`, config at `release-please-config.json`, manifest baseline v4.0.0 at `.release-please-manifest.json`; creates Release PRs with auto-generated CHANGELOG entries grouped by commit type; maintainer controls release timing via merge decision (`f1ad4ef`)
- README "Releases" section documenting the automated release process (`f1ad4ef`)

**Changed**
- Closed Feature 086 — updated product docs (PRD INDEX, OKRs), architecture docs (Tech Stack, System Design, CLAUDE.md), devops docs (CI_CD_GUIDE, staging/production READMEs), KB entry KB-020, delivery report (`f1ad4ef`)

### Feature 066 — Install Script and Version Tagging

**Added**
- Single-command install script (`scripts/install.sh`) replacing 6+ manual `cp` commands; supports `--source` override, `--version` pinned installs with trap-based cleanup, auto-detection from script location; machine-parseable manifest section in `INSTALL_MANIFEST.md`; Bash 3.2+ compatible with no external dependencies beyond git (`9ed2a7f`)
- First semantic version tag `v4.0.0` on main branch, enabling version-pinned installs and `git describe` version reporting

**Changed**
- README Quick Start Step 2 updated: scripted install as primary path, manual `cp -r` commands preserved in collapsible fallback section (`9ed2a7f`)
- Developer Guide install section updated to match README with scripted install primary (`9ed2a7f`)
- Closed Feature 066 — updated product docs (PRD INDEX, BACKLOG), architecture docs (Tech Stack, System Design, CLAUDE.md), KB entry PAT-019, delivery report (`65daf61`, `0dbf6ad`)

### Feature 078 — Agent Context Optimization

**Added**
- Restructured 6 tachi agents (orchestrator, risk-scorer, control-analyzer, report-assembler, threat-report, threat-infographic) from monolithic prompts to lean definitions with on-demand skill references; created 4 new skill directories (`tachi-orchestration`, `tachi-risk-scoring`, `tachi-report-assembly`, `tachi-shared`) with 25+ granular reference files; added explicit model fields to all 17 agents; shared severity bands, STRIDE+AI categories, finding format as single-source-of-truth; 40-60% prompt size reduction (`46fc7e6`)

**Changed**
- Closed Feature 078 — updated product docs (PRD INDEX, User Stories, OKRs), architecture docs (Tech Stack, System Design, Patterns, ADR-019, ADR-002), KB entry PAT-018, delivery report, BACKLOG regenerated (`7c47b0a`, `618b790`)

### Feature 074 — Baseline-Aware Pipeline

**Added**
- Baseline-aware threat detection pipeline with 4-phase correlation (detect → carry-forward → discover → merge+dedup), coverage checklists per component type, delta annotations ([NEW], [UNCHANGED], [UPDATED], [RESOLVED]), and SARIF baselineState properties; new `coverage-checklists.yaml` schema; extended `finding.yaml`, `risk-scoring.yaml`, `compensating-controls.yaml` with baseline fields; updated all 6 output templates; domain knowledge skills extended with baseline-correlation reference (`856f35e`)

**Changed**
- Closed Feature 074 — updated product docs (PRD INDEX, User Stories, OKRs), architecture docs (Tech Stack, System Design, ADR-018), KB entry PAT-017, delivery report, BACKLOG regenerated (`a300915`)

### Feature 075 — Tachi Agent Best Practices

**Added**
- Shared best practices document (`_TACHI_AGENT_BEST_PRACTICES.md`) with tier caps (Leaf ≤300, Report ≤800, Methodology ≤1,000), 8-criterion quality checklist, and compliance table for all 17 tachi agents; 3 domain knowledge skills (`tachi-orchestration`, `tachi-risk-scoring`, `tachi-control-analysis`) extracted from methodology agents with tiered on-demand loading (SKILL.md + references/) per ADR-002 (`cdf91e7`)

**Changed**
- Refactored orchestrator (2,000→769 lines), risk-scorer (1,419→994 lines), and control-analyzer (1,367→935 lines) by extracting domain knowledge into dedicated skills; all methodology agents now under 1,000-line cap (`cdf91e7`)
- Claude 4.6 tone audit across all 17 tachi agents — softened non-critical emphasis patterns, added tool restrictions to frontmatter, improved description fields for delegation routing, enforced data-top ordering (`cdf91e7`)
- Trimmed threat-report agent to ≤800-line Report tier cap (`cdf91e7`)
- Closed Feature 075 — updated product docs (PRD INDEX, User Stories, OKRs), architecture docs (Tech Stack, Patterns), KB entry PAT-016 (`e713251`, `e89a640`)

### Feature 071 — Deterministic Infographic Data Extraction

**Added**
- Shared parser module (`scripts/tachi_parsers.py`) extracted from `extract-report-data.py` — generic table parsers, frontmatter/metadata parsers, severity parsers, findings/scope parsers; enables cross-output consistency between security reports and infographics (`61df3d4`)
- Deterministic infographic extraction script (`scripts/extract-infographic-data.py`) — reads tachi pipeline markdown artifacts and outputs structured JSON for baseball-card, system-architecture, and risk-funnel templates; Largest Remainder Method for percentage rounding, deterministic tie-breaking (score desc, threat ID asc), component heat map cross-tabulation, 4-tier risk funnel computation; Python 3.9+ stdlib only (`61df3d4`)
- ADR-017 documenting deterministic extraction approach, shared parser module extraction, and Largest Remainder Method selection (`93a39c6`)

**Changed**
- Refactored `extract-report-data.py` to import shared parsers from `tachi_parsers.py` — zero behavior change, byte-identical output verified (`61df3d4`)
- Updated threat-infographic agent to invoke deterministic extraction script instead of LLM-based parsing (`61df3d4`)
- Updated `schemas/infographic.yaml` and baseball card template for structured data support (`61df3d4`)
- Closed Feature 071 — updated product docs (PRD INDEX, User Stories, OKRs), architecture docs (Tech Stack, System Design, Patterns, ADR-017), devops docs, KB entry PAT-015 (`93a39c6`, `faa2fb2`)

### Feature 067 — Deterministic Report Data Extraction

**Added**
- Deterministic Python parsing script (`scripts/extract-report-data.py`) replacing LLM-based markdown extraction for security report generation; 3-tier severity source selection (compensating-controls.md > risk-scores.md > threats.md), internal consistency validation (severity sums, duplicate IDs), scope data extraction (components, data flows, trust zones, boundary crossings), executive narrative and remediation action parsing; Python 3.9+ stdlib only, zero external dependencies (`7dc8b1c`)
- Tier 1 test fixture (`examples/agentic-app/sample-report/compensating-controls.md`) for validating full-pipeline Tier 1 output (`7dc8b1c`)

**Changed**
- Updated report-assembler agent to invoke Python script instead of inline LLM parsing; Steps 2-3 replaced with single script invocation step with exit code handling (`7dc8b1c`)
- Closed Feature 067 — updated product docs (PRD INDEX, User Stories, OKRs), architecture docs (Tech Stack — Python 3.9+, System Design), devops docs (local prerequisites), KB entry PAT-014 (`851ad2e`)

### Feature 060 — Professional PDF Security Assessment Report with tachi Branding

**Added**
- Professional branded PDF security report with modular Typst template system: 6 new pages (disclaimer, TOC, methodology, scope, theme, report-config), 6 updated templates, `brand/` asset directory with 8 logo variants, centralized theme tokens and shared utilities, extended `security-report.yaml` schema v1.1, updated report-assembler agent with brand-aware compilation (`c3cc8cf`)

**Changed**
- Closed Feature 060 — updated product docs (PRD INDEX), architecture docs (Tech Stack — Typst CLI), KB entry PAT-013, delivery report (`3f36ca5`)
- Exported user stories, regenerated BACKLOG.md (`331d6e2`)

### Feature 054 — Security Assessment PDF Booklet

**Added**
- `/security-report` command + report-assembler agent for generating professional multi-page PDF security assessment booklets from tachi pipeline artifacts; 7 Typst templates (cover, executive summary, findings detail, remediation roadmap, control coverage, full-bleed infographic, main orchestrator), `schemas/security-report.yaml` validation schema, graceful degradation for partial pipelines, full-bleed landscape infographic pages (`053eba9`)

**Changed**
- Closed Feature 054 — updated product docs (PRD INDEX), devops docs (Typst dependency), KB entry PAT-012 (`ed481a1`)
- Exported user stories from GitHub Issue #54, regenerated BACKLOG.md (`678da2f`)

### Feature 053 — Risk Reduction Funnel

**Added**
- 4-tier risk reduction funnel infographic template with graceful degradation (4-tier/3-tier/1-tier modes), ghost tiers with CTAs, metrics sidebar, and Gemini 3D prompt; registered in agent + command (`48b3c06`)

**Changed**
- Closed Feature 053 — updated product docs (PRD INDEX, User Stories, OKRs), architecture docs (Tech Stack), KB entry PAT-011 (`a09c3ff`)
- Regenerated BACKLOG.md after issue closure (`d1d133d`)

### Feature 048 — Infographic Tiered Pipeline Auto-Detection & Residual Risk

**Added**
- Three-tier data source auto-detection for `/infographic` (compensating-controls.md > risk-scores.md > threats.md), residual risk extraction from Coverage Matrix, enhancement tips at each pipeline tier, risk label distinction (Residual Risk / Inherent Risk / Severity) across both templates (`e67de32`)

**Changed**
- Closed Feature 048 — updated product docs (PRD INDEX, User Stories, OKRs), architecture docs (Tech Stack, System Design), developer guide, KB-010 (`8e8cab9`)
- Regenerated BACKLOG.md after issue closure (`a2d4ac9`)

### Feature 045 — End-to-End tachi Instruction Manual

**Added**
- Comprehensive developer guide covering tachi's 4-command threat modeling pipeline with step-by-step walkthrough, pipeline diagram, and command reference (`33db77b`)

**Changed**
- Closed Feature 045 — updated product docs, architecture docs, lifecycle overview diagram (`372ff26`)
- Replaced lifecycle overview with tachi pipeline diagram (`d631522`)

### Feature 039 — Standalone /infographic Command

**Added**
- Standalone `/infographic` command with auto-detection of richest data source, dual-path extraction, template selection, and explicit file override; Phase 6 removed from `/threat-model` pipeline (5-phase only); all platform adapters updated (`45ba448`)

**Changed**
- Closed Feature 039 — updated product docs (PRD INDEX, User Stories, OKRs), architecture docs (System Design, ADR-014 addendum, ADR-016), KB entry PAT-008 (`9ba6f07`)
- Delivery retrospective and backlog sync (`c291b42`)

### Feature 036 — Compensating Controls Analysis

**Added**
- `/compensating-controls` command + control-analyzer agent with 6-phase pipeline, 8 STRIDE + 2 AI control categories, effectiveness classification, recommendations with effort estimates, residual risk calculation, coverage matrix, and dual-format output (compensating-controls.md + compensating-controls.sarif) (`9a84115`)

**Changed**
- Closed Feature 036 — updated product docs (PRD INDEX), architecture docs (Tech Stack), KB entry PAT-007 (`d7370e8`)
- Exported user stories from GitHub Issue #36 (`5069c9f`)

### Feature 035 — Quantitative Risk Scoring

**Added**
- `/risk-score` command + risk-scorer agent with four-dimensional quantitative scoring (CVSS 3.1, exploitability, scalability, reachability), weighted composite scores, governance fields, and dual-format output (risk-scores.md + risk-scores.sarif) (`4afbe77`)

**Changed**
- Closed Feature 035 — updated product docs (PRD INDEX, User Stories), architecture docs (Tech Stack), KB entry PAT-006 (`a71337a`)
- Exported user stories from GitHub Issue #35 (`939d17f`)

### Feature 029 — Agent Refactoring Right-Size

**Added**
- Right-sized 3 threat agents via reference-extraction pattern: orchestrator (2,085→1,273 lines, -39%), report (801→472, -41%), infographic (592→414, -30%); 6 reference docs in `adapters/claude-code/agents/references/`; portable `.claude/agents/tachi/` agent set for non-Claude-Code adapters (`cde4cc8`)

**Changed**
- Closed Feature 029 — updated product docs (PRD INDEX, User Stories), architecture docs (Tech Stack, Patterns, README) (`5a8a127`)
- Regenerated BACKLOG.md after issue closure (`64e5e4a`)

### Feature 024 — Example Threat Models

**Added**
- Three end-to-end example threat models: web-app (STRIDE + OWASP Web 2025), agentic-app (STRIDE + AI agents + OWASP Agentic/MCP), microservices (cross-service STRIDE); each with Mermaid architecture diagram and schema v1.1 compliant threat model output (`f411944`)

**Changed**
- Closed Feature 024 — updated product docs (PRD INDEX, OKRs, User Stories), architecture docs (CLAUDE.md, Tech Stack), delivery report (`68c9e47`)
- Exported user stories from GitHub Issue #24 to aggregated reference (`38db6fc`)

### Feature 021 — Platform Adapters

**Added**
- Platform adapters for 5 targets: Claude Code (`.claude/agents/`), Generic (numbered prompts), Cursor (`.mdc` rules), Copilot (`.agent.md` with size-split), GitHub Actions (workflow YAML with SARIF upload); VERSION script for drift detection (`c4331f4`)

**Changed**
- Closed Feature 021 — updated product docs (INDEX, BACKLOG, User Stories), architecture docs (Tech Stack, System Design, ADR-015), DevOps docs (README, Local, CI/CD Guide) (`71f22b8`)
- Regenerated BACKLOG.md after issue closure (`4b5c244`)

### Feature 018 — Threat Infographic Agent

**Added**
- Threat infographic agent with 6-section visual risk spec, Gemini API image generation, output schema, orchestrator Phase 6 integration, and sample output (`24ba12b`)

**Changed**
- Closed Feature 018 — updated product docs (INDEX, User Stories, OKRs), architecture docs (Tech Stack, System Design, ADR-014), DevOps docs, KB entry PAT-005 (`a9cffc8`)
- Regenerated BACKLOG.md after issue closure (`25329b4`)

### Feature 015 — Threat Report Agent & Attack Trees

**Added**
- Threat report agent with STRIDE+AI attack trees, report schema, 7-section template, 12 Mermaid attack tree examples, and orchestrator Phase 5 integration (`f59783f`)

**Changed**
- Closed Feature 015 — updated product docs (INDEX, User Stories), architecture docs (Tech Stack, System Design) (`16fd4f1`)
- Regenerated BACKLOG.md after issue closure (`60780c6`)

### Feature 012 — SARIF Output Generation

**Added**
- SARIF 2.1.0 output generation with STRIDE+AI rule mapping, CVSS severity alignment, correlated findings, dual locations, deterministic fingerprints, and optional OWASP/CWE taxonomies (`9f84fad`)

**Changed**
- Closed Feature 012 — updated product docs, architecture docs (ADR-013), tech stack, KB entry PAT-004 (`64cb30a`)
- Regenerated BACKLOG.md after issue closure (`bbaabb3`)

### Feature 010 — Deduplication & Risk Rating

**Added**
- Cross-agent finding correlation with 5 deterministic rules, deduplicated risk summaries, three-state coverage matrix, and OWASP 3x3 risk calibration matrix; schema v1.1 (`2eac145`)

**Changed**
- Closed Feature 010 — updated product docs, architecture docs (ADR-012), patterns, KB entry PAT-003 (`87eeb89`)
- Regenerated BACKLOG.md after issue closure (`d147318`)

### Feature 007 — AI Threat Agents

**Added**
- AI threat agent prompts for 5 agentic threat categories: prompt injection, data poisoning, tool abuse, model theft, agent autonomy (`eaa0439`)

**Changed**
- Closed Feature 007 — updated product docs, archived specs, regenerated backlog (`2ca4a19`, `71206e8`)

### Feature 003 — Orchestrator Agent

**Added**
- Orchestrator agent prompt for STRIDE + AI threat modeling with 4-phase OWASP workflow, 5-format input parsing, 11-agent dispatch, and structured output assembly (`5f18934`)

**Changed**
- Closed Feature 003 — updated product docs, archived specs, regenerated backlog (`ddd7699`, `d7acf41`)

### Feature 001 — Project Skeleton & Interface Contract

**Added**
- Project skeleton with STRIDE + AI threat agent prompts, machine-readable schemas, output template, interface contract, and 3 example inputs (`b398249`)

**Changed**
- Closed Feature 001 — updated product docs, archived specs, regenerated backlog (`d706b89`, `edd9f43`)

---

## [4.0.0] - 2026-02-08

### BREAKING CHANGES

#### AOD Rebranding — Renamed .specify/ to .aod/ and Replaced All Spec Kit Branding

The project has been rebranded from "Product-Led Spec Kit" to "Agentic Oriented Development Kit" (AOD Kit). This is a comprehensive rename affecting directory structure, branding text, and file names across the repository.

**Structural Changes:**
- `.specify/` directory renamed to `.aod/` (git history preserved via `git mv`)
- `docs/SPEC_KIT_TRIAD.md` renamed to `docs/AOD_TRIAD.md`
- Environment variables: `SPECIFY_FEATURE` → `AOD_FEATURE`, `SPECIFY_DIR` → `AOD_DIR`
- Log prefixes: `[specify]` → `[aod]`

**Branding Replacements:**
- `Product-Led Spec Kit` → `Agentic Oriented Development Kit`
- `SPEC_KIT` → `AOD` (constant-case identifiers)
- `Spec Kit` → `AOD Kit` (user-facing text)
- `spec-kit` → `aod` (kebab-case identifiers)
- All `spec-kit-ops` upstream references removed from active files

**Preserved:**
- `/triad.specify` command name (unchanged — "specify" is a verb, not branding)
- Historical specs (001-007) and their artifacts
- Historical planning documents and prior CHANGELOG entries

**Migration**: Update any local scripts or documentation referencing `.specify/` paths to `.aod/`. Update any references to `docs/SPEC_KIT_TRIAD.md` to `docs/AOD_TRIAD.md`.

### Added - 3 New Thinking Lenses (Feature 009)

Added three new structured thinking lenses to `docs/core_principles/` and updated the thinking-lens skill:

- **Four Causes** (`four_causes.md`) - Aristotelian causal analysis examining Material, Formal, Efficient, and Final causes to understand why something exists or happens
- **Cargo Cult Detection** (`cargo_cult_detection.md`) - Identifies practices copied without understanding, helping teams distinguish genuine best practices from superficial mimicry
- **Golden Mean** (`golden_mean.md`) - Aristotelian balance-finding framework for navigating engineering trade-offs between extremes

**Details:**
- Content-only addition (no code, API, or infrastructure changes)
- Updated `docs/core_principles/README.md` lens registry with all three lenses
- Updated `.claude/skills/thinking-lens/SKILL.md` to reference new lenses
- PR: #8 (upstream development repo)
- Tasks completed: 26/26

---

## [3.0.0] - 2026-02-07

### BREAKING CHANGES

#### SpecKit Commands Removed — Unified Triad Workflow

All `/speckit.*` commands have been removed and consolidated into the `/triad.*` command set. The dual command architecture (Triad + Vanilla) has been replaced with a single, unified workflow.

**Command Mapping:**

| Former Command | New Command | Notes |
|----------------|-------------|-------|
| `/speckit.specify` | `/triad.specify` | Logic inlined with research + PM sign-off |
| `/speckit.plan` | `/triad.plan` | Logic inlined with PM + Architect sign-off |
| `/speckit.tasks` | `/triad.tasks` | Logic inlined with triple sign-off |
| `/speckit.implement` | `/triad.implement` | Logic inlined with Architect checkpoints |
| `/speckit.clarify` | `/triad.clarify` | Direct transfer with reference updates |
| `/speckit.analyze` | `/triad.analyze` | Direct transfer with reference updates |
| `/speckit.checklist` | `/triad.checklist` | Direct transfer with reference updates |
| `/speckit.constitution` | `/triad.constitution` | Direct transfer with reference updates |

**Migration**: Replace all `/speckit.*` commands with their `/triad.*` equivalents. No other changes needed.

### Added
- 4 new triad commands: `/triad.clarify`, `/triad.analyze`, `/triad.checklist`, `/triad.constitution`
- Archive tag `v2.0.0-pre-speckit-removal` preserves historical state

### Removed
- All 8 `/speckit.*` command files
- "Vanilla Commands" sections from all documentation
- `compatible_with_speckit` and `last_tested_with_speckit` frontmatter from all command files

### Changed
- 4 core triad commands now self-contained (no Skill tool coupling to speckit commands)
- All documentation, rules, skills, and agents reference only `/triad.*` commands
- CLAUDE.md updated with unified command set (10 triad commands)
- Renamed `speckit-validator` skill to `spec-validator` (removes speckit branding)

---

## [2.1.0] - 2026-01-31

### Added - Agent Refactoring (Feature 003)

**Agent Best Practices Documentation**
- Created `_AGENT_BEST_PRACTICES.md` with 8 core principles for agent design
- Created `_README.md` agent directory overview and quick reference

**Agent Refactoring**
- Refactored all 12 agents to consistent 8-section structure (58% line reduction)
- Split team-lead into team-lead + orchestrator (13 agents total)
- Standardized YAML frontmatter across all agents (version, changelog, boundaries, triad-governance)

**New Skill**
- Added thinking-lens skill for structured analysis methodologies

**Key Metrics**
- Tasks completed: 140
- Total agent line reduction: 58% (7,885 → ~3,300 lines)
- All 12 agents now follow standardized 8-section structure
- 100% YAML frontmatter standardization

---

## [2.0.0] - 2026-01-24

### Added - Anthropic Claude Code v2.1.16 Integration

**Parallel Triad Reviews**
- PM + Architect reviews now run simultaneously with context forking
- Triple sign-off (PM + Architect + Team-Lead) executes in parallel for tasks.md
- Review results merge automatically using severity ranking (Critical > Warning > Suggestion)

**Version Detection & Feature Flags**
- Automatic Claude Code version detection at session start
- Feature flags system (`.claude/config/feature-flags.json`) for capability management
- Graceful degradation for older Claude Code versions (sequential fallback)

**New Libraries**
- `.claude/lib/version/detect.sh` - Version detection utilities
- `.claude/lib/version/feature-gate.sh` - Feature gating logic
- `.claude/lib/version/degradation.sh` - Graceful fallback handling
- `.claude/lib/triad/merge-results.sh` - Parallel review result merging
- `.claude/lib/triad/timing-metrics.sh` - Performance measurement
- `.claude/lib/dependencies/` - Task dependency resolution system

**New Skills**
- `.claude/skills/triad/pm-review.md` - PM review skill for parallel execution
- `.claude/skills/triad/architect-review.md` - Architect review skill
- `.claude/skills/triad/teamlead-review.md` - Team-Lead review skill

**Documentation**
- `docs/devops/FEATURE_MATRIX.md` - Feature compatibility by Claude Code version
- `docs/devops/MIGRATION.md` - DevOps migration guide
- PRD-002: Anthropic Updates Integration specification

**Test Fixtures**
- `specs/002-anthropic-updates-integration/test-fixtures/` - Comprehensive test suite
  - Version detection tests
  - Parallel execution tests
  - Context forking tests
  - Degradation tests
  - Dependency resolution tests

### Changed
- Triad commands now auto-detect version and use parallel execution when available
- `_triad-init.md` command initializes version detection at session start
- Review workflows use isolated contexts to prevent cross-contamination

### Migration
See [MIGRATION.md](MIGRATION.md) for detailed upgrade instructions from v1.x to v2.0.0.

---

## [1.1.0] - 2025-12-15

### Added - Modular Rules System

**Modular Governance Rules**
- `.claude/rules/governance.md` - Sign-off requirements, Triad workflow
- `.claude/rules/git-workflow.md` - Branch naming, PR policies
- `.claude/rules/deployment.md` - DevOps agent policy
- `.claude/rules/scope.md` - Project boundaries
- `.claude/rules/commands.md` - Triad + Vanilla command reference
- `.claude/rules/context-loading.md` - Context loading guide

**Documentation**
- `MIGRATION.md` - Guide for customizing modular rules

### Changed
- Refactored CLAUDE.md from 192 to 70 lines using @-references
- Instant context loading (<1 second vs 5-10 seconds with manual `cat` commands)
- Topic-specific editing without merge conflicts

---

## [1.0.0] - 2025-12-04

### Added - Initial Release

**Core Governance**
- Product-led governance template
- SDLC Triad collaboration framework (PM + Architect + Tech-Lead)
- Templatized constitution with `{{PLACEHOLDERS}}` for easy customization

**Agents**
- 13 specialized agents for different roles
- Product Manager, Architect, Team-Lead, and implementation agents

**Skills**
- 8 automation capabilities
- PRD creation, specification, planning, task generation, implementation

**Commands**
- Triad commands with governance (sign-offs required)
- Vanilla commands for fast prototyping (no governance)

**Documentation**
- Constitution template (`.specify/memory/constitution.md`)
- Product documentation structure (`docs/product/`)
- Architecture documentation (`docs/architecture/`)
- Core principles (`docs/core_principles/`)

---

## Version Comparison

| Feature | v1.0.0 | v1.1.0 | v2.0.0 | v2.1.0 | v3.0.0 | v4.0.0 |
|---------|--------|--------|--------|--------|--------|--------|
| Command Set | Triad + Vanilla | Triad + Vanilla | Triad + Vanilla | Triad + Vanilla | Triad only (10 commands) | Triad only (10 commands) |
| Triad Governance | Sequential | Sequential | Parallel | Parallel | Parallel | Parallel |
| CLAUDE.md Size | 192 lines | 70 lines | 70 lines | 70 lines | ~80 lines | ~80 lines |
| Context Loading | Manual | @-references | @-references | @-references | @-references | @-references |
| Version Detection | - | - | Automatic | Automatic | Automatic | Automatic |
| Feature Flags | - | - | Supported | Supported | Supported | Supported |
| Degradation | - | - | Graceful | Graceful | Graceful | Graceful |
| Agent Count | 13 | 13 | 13 | 13 (refactored) | 13 | 13 |
| Agent Line Reduction | - | - | - | 58% | 58% | 58% |
| Skill Tool Coupling | - | - | 3 cross-calls | 3 cross-calls | 0 (self-contained) | 0 (self-contained) |
| Branding | Spec Kit | Spec Kit | Spec Kit | Spec Kit | Spec Kit | AOD Kit |
| Thinking Lenses | 5 | 5 | 5 | 5 | 5 | 8 |

---

[4.0.0]: https://github.com/davidmatousek/tachi/compare/v3.0.0...v4.0.0
[3.0.0]: https://github.com/davidmatousek/tachi/compare/v2.1.0...v3.0.0
[2.1.0]: https://github.com/davidmatousek/tachi/compare/v2.0.0...v2.1.0
[2.0.0]: https://github.com/davidmatousek/tachi/compare/v1.1.0...v2.0.0
[1.1.0]: https://github.com/davidmatousek/tachi/compare/v1.0.0...v1.1.0
[1.0.0]: https://github.com/davidmatousek/tachi/releases/tag/v1.0.0
