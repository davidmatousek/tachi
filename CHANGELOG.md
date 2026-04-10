# Changelog

All notable changes to tachi will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [4.9.2](https://github.com/davidmatousek/tachi/compare/v4.9.1...v4.9.2) (2026-04-10)


### Bug Fixes

* **138:** lowercase attack tree PNG filenames to match convention ([#139](https://github.com/davidmatousek/tachi/issues/139)) ([1400e47](https://github.com/davidmatousek/tachi/commit/1400e478ff58a9f1357f69d42c62ea0437e0d4c8)), closes [#138](https://github.com/davidmatousek/tachi/issues/138)

## [4.9.1](https://github.com/davidmatousek/tachi/compare/v4.9.0...v4.9.1) (2026-04-10)


### Bug Fixes

* **134:** threat-report attack tree baseline, MAESTRO layer rendering, filename convention ([#135](https://github.com/davidmatousek/tachi/issues/135)) ([716df8e](https://github.com/davidmatousek/tachi/commit/716df8e9c98768eb5edf5d87be943833aab81ab1)), closes [#134](https://github.com/davidmatousek/tachi/issues/134)

## [4.9.0](https://github.com/davidmatousek/tachi/compare/v4.8.0...v4.9.0) (2026-04-10)


### Features

* **128:** add executive threat architecture infographic with early-page PDF positioning ([#131](https://github.com/davidmatousek/tachi/issues/131)) ([7b217fe](https://github.com/davidmatousek/tachi/commit/7b217fe2447ba758db770ec1be0ac428e23fa252))

## [4.8.0](https://github.com/davidmatousek/tachi/compare/v4.7.0...v4.8.0) (2026-04-09)


### Features

* **120:** add architecture lifecycle command ([#124](https://github.com/davidmatousek/tachi/issues/124)) ([f814c02](https://github.com/davidmatousek/tachi/commit/f814c027db03cf5424599b640bd99ac1aa8cd37e))

## [4.7.0](https://github.com/davidmatousek/tachi/compare/v4.6.0...v4.7.0) (2026-04-09)


### Features

* **121:** rename tachi commands to tachi.* dot-namespace ([#122](https://github.com/davidmatousek/tachi/issues/122)) ([7d0f968](https://github.com/davidmatousek/tachi/commit/7d0f9684166a8fd6af10517fcca3f1aa85abad73))

## [Unreleased]

### Added

- **Executive Threat Architecture Infographic** (Feature 128) — New `/tachi.infographic --template executive-architecture` (alias: `exec`) generates a layered architecture diagram with Critical/High finding callouts, designed for CISO-level readers. In the compiled PDF security report the new page lands immediately after the Executive Summary (pages 2–3 area) so executives see the visual threat narrative within their first-glance window. Included in the `all` shorthand expansion alongside the existing five templates. Backward compatible — example PDFs without a generated `threat-executive-architecture.jpg` render byte-identical to the pre-F-128 baseline. Ships with tachi's first project-level pytest harness (`pyproject.toml`, `requirements-dev.txt`, `tests/`) and five committed `.baseline` PDFs guarding backward compatibility against silent regressions.
- **Architecture Lifecycle Command** (Feature 120) — `/tachi.architecture` now tracks versions with YAML frontmatter (version, date, description, SHA-256 checksum), archives previous versions to `.archive/v{N}/`, and supports guided updates through change categories. `/tachi.threat-model` automatically snapshots the architecture file into each timestamped output folder for full traceability. Backward compatible with existing architecture files.

### Changed

- **Command Namespace Migration** (Feature 121) — All tachi pipeline commands renamed from unprefixed names to `tachi.*` namespace prefix. New `/tachi.architecture` command added. Install script now cleans up deprecated command files on upgrade. See migration table below.

#### Command Name Migration

| Old Command | New Command |
|-------------|-------------|
| `/threat-model` | `/tachi.threat-model` |
| `/risk-score` | `/tachi.risk-score` |
| `/compensating-controls` | `/tachi.compensating-controls` |
| `/infographic` | `/tachi.infographic` |
| `/security-report` | `/tachi.security-report` |
| *(new)* | `/tachi.architecture` |

Upgrading: Run `install.sh` — it automatically removes old unprefixed command files and installs the new `tachi.*` versions.

---

## [4.6.0](https://github.com/davidmatousek/tachi/compare/v4.5.0...v4.6.0) (2026-04-09)


### Features

* **119:** auto-polish release notes via Claude API after release ([a44127f](https://github.com/davidmatousek/tachi/commit/a44127fccd11aef959cc1939670158ac8dffabb6)), closes [#119](https://github.com/davidmatousek/tachi/issues/119)


### Bug Fixes

* **119:** move release notes polishing to local-only script ([0dd33fd](https://github.com/davidmatousek/tachi/commit/0dd33fd4c4fd686393207837485386afac16ad03))

## [4.5.0](https://github.com/davidmatousek/tachi/compare/v4.4.2...v4.5.0) (2026-04-09)

### Added

- **Attack Path Pages in PDF Reports** (Feature 112) — Each Critical and High finding with an attack tree now gets a dedicated page in the security report PDF, showing a rendered Mermaid diagram, plain-English narrative explaining the attack chain, and specific remediation steps. Pages are ordered by severity (Critical first) and introduced by an "Attack Path Analysis" section divider with TOC entry. Mermaid diagrams render to PNG at 2x resolution via `mmdc`; graceful text fallback when the tool is unavailable. Fully backward compatible — reports without attack trees generate identically to before.
- **Automated release notes polishing** (Feature 119) — Local script (`scripts/polish-release-notes.sh`) rewrites auto-generated release notes into user-facing language via Claude API. Run after merging a Release PR.
- **README refresh** — Updated with MAESTRO layer classification, `/security-report` command, baseline delta tracking, all 5 infographic templates, and 6 examples (was 3).

### Changed

- release-please now hides `docs`, `chore`, `refactor`, `test`, and `style` commits from auto-generated CHANGELOG entries. Only `feat`, `fix`, and `perf` appear.

---

## [4.4.2](https://github.com/davidmatousek/tachi/compare/v4.4.1...v4.4.2) (2026-04-09)

### Fixed

- MAESTRO heading detection now falls back gracefully when headings use inconsistent formatting in threat-report.md. Attack trees regenerated fresh for all 6 examples. MAESTRO Findings section now appears in all reports and PDF output.

---

## [4.4.1](https://github.com/davidmatousek/tachi/compare/v4.4.0...v4.4.1) (2026-04-09)

### Fixed

- Attack tree generation no longer includes RESOLVED findings. Previously, findings marked as resolved in a baseline comparison still produced attack trees, cluttering the report with irrelevant attack paths.

---

## [4.4.0](https://github.com/davidmatousek/tachi/compare/v4.3.4...v4.4.0) (2026-04-09)

### Added

- **Downstream Baseline Propagation** (Feature 104) — Baseline severity and status fields from `threats.md` now propagate through all pipeline stages: risk scoring, compensating controls, threat report, infographics, and PDF report. Delta annotations (NEW, UNCHANGED, UPDATED, RESOLVED) carry through the entire pipeline. New Section 8 (Delta Summary) in `threats.md` and `threat-report.md`. All 6 example outputs regenerated with baseline columns.

---

## [4.3.4](https://github.com/davidmatousek/tachi/compare/v4.3.3...v4.3.4) (2026-04-08)

### Fixed

- Baseline-aware pipeline now enforces mandatory Phase 2 discovery even when a baseline exists, preventing false confidence from carry-forward-only runs.

---

## [4.3.3](https://github.com/davidmatousek/tachi/compare/v4.3.2...v4.3.3) (2026-04-08)

### Fixed

- Baseline auto-detection now correctly resolves paths, and downstream commands (`/risk-score`, `/compensating-controls`) no longer exceed context limits when processing large baseline files.

---

## [4.3.2](https://github.com/davidmatousek/tachi/compare/v4.3.1...v4.3.2) (2026-04-08)

### Fixed

- Version reporting (`install.sh`) now fetches tags before checking the installed version, showing the correct tag instead of a commit hash.
- release-please respects `release-please-config.json` instead of using a hardcoded release type.

---

## [4.3.1](https://github.com/davidmatousek/tachi/compare/v4.3.0...v4.3.1) (2026-04-08)

### Fixed

- Version examples in README and `install.sh` now auto-bump via release-please extra-files configuration.

---

## [4.3.0](https://github.com/davidmatousek/tachi/compare/v4.2.1...v4.3.0) (2026-04-08)

### Added

- **MAESTRO Infographic Templates and PDF Report Section** (Feature 091) — Two new infographic templates for MAESTRO-aware threat visualization: `maestro-stack` (vertical seven-layer risk distribution diagram) and `maestro-heatmap` (component-by-layer severity grid). New MAESTRO Findings page in the PDF security report. `maestro` shorthand in `/infographic` generates both templates in one invocation. All gated by `has-maestro-data` for backward compatibility with non-agentic threat models.

---

## [4.2.1](https://github.com/davidmatousek/tachi/compare/v4.2.0...v4.2.1) (2026-04-08)

### Fixed

- release-please workflow now supports `workflow_dispatch` for manual re-runs.

---

## [4.2.0](https://github.com/davidmatousek/tachi/compare/v4.1.0...v4.2.0) (2026-04-08)

### Added

- **MAESTRO Layer Mapping** (Feature 084) — Every threat finding is now classified into the CSA MAESTRO seven-layer taxonomy (L1 Foundation Model through L7 User Interface). The orchestrator assigns layers via keyword classification in Phase 1, and the mapping propagates downstream through risk scoring, compensating controls, and the threat report. New `maestro_layer` field in the finding schema (v1.2), SARIF `maestro-layer` tags, and MAESTRO Layer columns in all output tables. All 6 example outputs regenerated.

---

## [4.1.0](https://github.com/davidmatousek/tachi/compare/v4.0.0...v4.1.0) (2026-04-07)

### Added

- **Automated Release Tagging** (Feature 086) — Releases are now automated via Google's release-please GitHub Action. Conventional commits on main trigger a Release PR with auto-generated CHANGELOG entries. Merging the Release PR creates the git tag and GitHub Release. New files: `.github/workflows/release-please.yml`, `release-please-config.json`, `.release-please-manifest.json`.

---

## 4.0.x — Pre-release-please Features

*These features shipped between v4.0.0 and v4.1.0, before release-please was adopted. They were not individually tagged.*

### Feature 112 context already captured in v4.5.0 above.

### Feature 078 — Agent Context Optimization

Restructured 6 tachi agents from monolithic prompts to lean definitions with on-demand skill references. Created 4 skill directories with 25+ granular reference files. Shared severity bands, STRIDE+AI categories, and finding format as single-source-of-truth. 40-60% prompt size reduction across methodology agents.

### Feature 075 — Tachi Agent Best Practices

Shared best practices document with tier caps (Leaf 300, Report 800, Methodology 1,000 lines), 8-criterion quality checklist. Extracted domain knowledge from orchestrator (-39%), report agent (-41%), and control-analyzer (-30%) into dedicated skills.

### Feature 074 — Baseline-Aware Pipeline

Baseline-aware threat detection with 4-phase correlation (detect, carry-forward, discover, merge+dedup), coverage checklists per component type, delta annotations (NEW, UNCHANGED, UPDATED, RESOLVED), and SARIF `baselineState` properties. Compare threat model runs to track risk posture changes over time.

### Feature 071 — Deterministic Infographic Data Extraction

Shared parser module (`scripts/tachi_parsers.py`) and deterministic extraction script (`scripts/extract-infographic-data.py`) replacing LLM-based markdown parsing for infographics. Largest Remainder Method for percentage rounding, deterministic tie-breaking, 4-tier risk funnel computation. Python 3.9+ stdlib only.

### Feature 067 — Deterministic Report Data Extraction

Deterministic Python parsing script (`scripts/extract-report-data.py`) replacing LLM-based markdown extraction for PDF report generation. 3-tier severity source selection, internal consistency validation, scope data extraction. Zero external dependencies.

### Feature 066 — Install Script and Version Tagging

Single-command install script (`scripts/install.sh`) replacing 6+ manual `cp` commands. Supports `--source` override, `--version` pinned installs with trap-based cleanup. First semantic version tag `v4.0.0`.

### Feature 060 — Professional PDF Security Report

Professional branded PDF with modular Typst template system: disclaimer, TOC, methodology, scope, theme, and report-config pages. `brand/` asset directory with logo variants. Extended `security-report.yaml` schema v1.1.

### Feature 054 — Security Assessment PDF Booklet

`/security-report` command and report-assembler agent for generating multi-page PDF security assessment booklets from tachi pipeline artifacts. 7 Typst templates, graceful degradation for partial pipelines, full-bleed landscape infographic pages.

### Feature 053 — Risk Reduction Funnel

4-tier risk reduction funnel infographic template with graceful degradation (4-tier/3-tier/1-tier modes), ghost tiers with CTAs, and metrics sidebar.

### Feature 048 — Infographic Tiered Pipeline Auto-Detection

Three-tier data source auto-detection for `/infographic` (compensating-controls.md > risk-scores.md > threats.md). Residual risk extraction, enhancement tips at each pipeline tier, risk label distinction across templates.

### Feature 045 — Developer Guide

Comprehensive developer guide covering tachi's command pipeline with step-by-step walkthrough, pipeline diagram, and command reference.

### Feature 039 — Standalone /infographic Command

`/infographic` as a standalone command with auto-detection, dual-path extraction, and template selection. Removed from `/threat-model` pipeline (now 5-phase only).

### Feature 036 — Compensating Controls Analysis

`/compensating-controls` command with 6-phase pipeline, 8 STRIDE + 2 AI control categories, effectiveness classification, residual risk calculation, and dual-format output (markdown + SARIF).

### Feature 035 — Quantitative Risk Scoring

`/risk-score` command with four-dimensional scoring (CVSS 3.1, exploitability, scalability, reachability), weighted composite scores, governance fields, and dual-format output (markdown + SARIF).

### Feature 029 — Agent Right-Sizing

Right-sized 3 threat agents via reference-extraction pattern: orchestrator (-39%), report (-41%), infographic (-30%). 6 reference docs extracted. Portable `.claude/agents/tachi/` agent set.

### Feature 024 — Example Threat Models

Three end-to-end examples: web-app (STRIDE), agentic-app (STRIDE + AI), microservices (cross-service STRIDE). Each with Mermaid architecture and schema v1.1 output.

### Feature 021 — Platform Adapters

Adapters for 5 targets: Claude Code, Generic, Cursor, Copilot, GitHub Actions (with SARIF upload).

### Feature 018 — Threat Infographic Agent

Visual risk spec generation with Gemini API image output. Integrated as orchestrator Phase 6.

### Feature 015 — Threat Report Agent & Attack Trees

Narrative threat report with STRIDE+AI attack trees (Mermaid). 7-section template with 12 attack tree examples.

### Feature 012 — SARIF Output Generation

SARIF 2.1.0 output with STRIDE+AI rule mapping, CVSS severity alignment, deterministic fingerprints, and optional OWASP/CWE taxonomies.

### Feature 010 — Deduplication & Risk Rating

Cross-agent finding correlation with 5 deterministic rules, three-state coverage matrix, and OWASP 3x3 risk calibration. Schema v1.1.

### Feature 007 — AI Threat Agents

5 AI threat agent prompts: prompt injection, data poisoning, tool abuse, model theft, agent autonomy.

### Feature 003 — Orchestrator Agent

Orchestrator with 4-phase OWASP workflow, 5-format input parsing, 11-agent dispatch, and structured output assembly.

### Feature 001 — Project Skeleton

Project skeleton with STRIDE + AI threat agent prompts, schemas, output template, interface contract, and 3 example inputs.

---

## [4.0.0](https://github.com/davidmatousek/tachi/compare/v3.0.0...v4.0.0) (2026-02-08)

### BREAKING CHANGES

- **AOD Rebranding** — `.specify/` directory renamed to `.aod/`, `docs/SPEC_KIT_TRIAD.md` renamed to `docs/AOD_TRIAD.md`, environment variables and log prefixes updated. Update any local scripts referencing `.specify/` paths.

### Added

- 3 new thinking lenses: Four Causes, Cargo Cult Detection, Golden Mean.

---

## [3.0.0](https://github.com/davidmatousek/tachi/compare/v2.1.0...v3.0.0) (2026-02-07)

### BREAKING CHANGES

- **SpecKit commands removed** — All `/speckit.*` commands consolidated into `/triad.*`. See [migration table in previous CHANGELOG](https://github.com/davidmatousek/tachi/blob/v3.0.0/CHANGELOG.md) for command mapping.

### Added

- 4 new triad commands: `/triad.clarify`, `/triad.analyze`, `/triad.checklist`, `/triad.constitution`.

### Removed

- All 8 `/speckit.*` command files and "Vanilla Commands" documentation.

---

## [2.1.0](https://github.com/davidmatousek/tachi/compare/v2.0.0...v2.1.0) (2026-01-31)

### Added

- Agent refactoring: all 12 agents restructured to consistent 8-section format (58% line reduction). Team-lead split into team-lead + orchestrator (13 agents). New thinking-lens skill.

---

## [2.0.0](https://github.com/davidmatousek/tachi/compare/v1.1.0...v2.0.0) (2026-01-24)

### Added

- **Parallel Triad Reviews** — PM + Architect reviews run simultaneously with context forking. Triple sign-off executes in parallel.
- Automatic Claude Code version detection with feature flags and graceful degradation.

---

## [1.1.0](https://github.com/davidmatousek/tachi/compare/v1.0.0...v1.1.0) (2025-12-15)

### Added

- Modular rules system: governance, git workflow, deployment, scope, commands, and context loading extracted from CLAUDE.md (192 → 70 lines).

---

## [1.0.0](https://github.com/davidmatousek/tachi/releases/tag/v1.0.0) (2025-12-04)

### Added

- Initial release: product-led governance template, SDLC Triad framework, 13 agents, 8 skills, triad + vanilla commands, documentation structure.
