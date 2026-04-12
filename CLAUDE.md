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
- **Feature 082**: Threat Agent Skill References — Detection Tier Lean Refactor
  - All 11 threat agents (6 STRIDE + 5 AI) migrated from self-contained inline shape to lean + skill references pattern, completing the lean-agent architecture for all 17 tachi agents. Pre-refactor: STRIDE 113-141 lines, AI 167-201 lines (3 AI agents over the 180-line hard cap). Post-refactor: STRIDE 50-54 lines, AI 78-114 lines — every agent within FR-10 tier caps (STRIDE ≤120, AI ≤150, hard cap ≤180).
  - 11 new companion skill directories created at `.claude/skills/tachi-<name>/references/` (spoofing, tampering, repudiation, info-disclosure, denial-of-service, privilege-escalation, prompt-injection, data-poisoning, model-theft, tool-abuse, agent-autonomy). Each hosts a `detection-patterns.md` reference file that is byte-preserved from the pre-refactor agent content plus enriched categories. Agent files load via a single `**MANDATORY**: Read` directive at detection start — no phase-gated loads (unlike the methodology variant used by control-analyzer), making this a new "detection variant" of the lean pattern.
  - **New ADR-023** (`docs/architecture/02_ADRs/ADR-023-threat-agent-skill-references-pattern.md`, Status: Accepted) — records the sibling detection variant as a second documented lean-agent shape. Four decisions: (1) detection variant is a sibling to the methodology variant, (2) MAESTRO classification remains orchestrator-owned with zero threat-agent involvement (FR-9 / INV-5), (3) shared reference edits are additive-only (no infra-agent regressions), (4) `finding-format-shared.md` gains a "For Threat Agents" producer section while preserving the existing consumer sections. Cross-references ADR-014 (optional external APIs), ADR-020 (MAESTRO classification), ADR-021 (determinism), ADR-022 (first CLI prerequisite ADR).
  - **Enrichment floor cleared**: +30 new pattern categories added across the 11 agents during Phase 4+5 rollout (Waves 9-11), against a ≥22 aggregate floor (SC-006 / FR-7) — +8 margin. Source attribution: OWASP Top 10 2021, OWASP LLM Top 10 2025 (LLM01-LLM10:2025), OWASP AI Exchange, MITRE ATT&CK v15+, MITRE ATLAS v5.1+ (including the October 2025 agent techniques AML.T0058-T0062 — context poisoning, memory corruption, agent-in-the-middle, excessive agency runtime, cascading agent failures), CWE Top 25 2024, and NIST AI 600-1. T048 security review flagged 5 categories for primary-source realignment; T048a (Wave 13.5) rebuilt all 5 preserving substance byte-verbatim. Zero de-scopes entered Phase 8.
  - **Shared reference additive consolidation** (Phase 6, Waves 12): `finding-format-shared.md` gains a new "For Threat Agents" producer section describing the finding construction responsibility for detection-tier agents, while the existing "For Risk Scorer / Control Analyzer / Threat Report" consumer sections remain untouched (additive-only invariant T046). All 11 threat agents' Skill References tables register the shared ref for load at detection start. Zero inline duplication: SC-004 Wave 16 cross-agent audit verified the OWASP 3×3 risk matrix lives in exactly one canonical file (`severity-bands-shared.md:72`, normalized to Unicode ×).
  - **Option B+ gate methodology**: Phase 1a / 1b (2-agent prototype) and Phase 3 (11-agent scale) regression gates used content-equivalence + DFD-vs-pattern matching rather than live orchestrator invocation. The method was ratified by the T021 joint architect + team-lead gate approval under the "±2 tolerance interpretation (b)" ruling: pre-existing pattern categories must delta=0, new categories can have any non-negative delta from enrichment. T050 full regression gate (Wave 15) used Option B+ to prove SC-005 for all 11 agents × 6 examples; 39+ new findings across the 6 examples were predicted from DFD-vs-pattern matching. T057 live regeneration on agentic-app (Wave 17) confirmed +8 new findings (22 baseline → 30) — consistent with the Option B+ prediction.
  - **Wave 16 SC-004 remediation**: T051 cross-agent grep audit caught 22 inline "OWASP 3×3" name mentions in agent prose (Skill References table row + Process Step 4). The matrix CONTENT was already extracted by Phase 6, but the NAME still appeared in agent files. Remediation: removed the branded phrase from all 22 locations (rephrased as "Risk matrix for finding severity computation" and "via the matrix in severity-bands-shared.md") and normalized `severity-bands-shared.md:72` header from ASCII `3x3` to Unicode `3×3` to match the SC-004 canonical-form grep test. The 5 ASCII mentions remaining in `finding-format-shared.md` are preserved (they describe the matrix rather than defining it, and match the 159-file ASCII consensus across the broader codebase).
  - **Byte-deterministic PDF re-baseline**: T056 confirmed no-op. Feature 082 is purely agent-behavior-facing — the PDF pipeline reads committed `threats.md` / `risk-scores.md` / `compensating-controls.md` / `attack-trees/` files from `examples/<name>/`, none of which are modified by Feature 082. Typst templates, `extract-report-data.py`, and `extract-infographic-data.py` are also untouched. Backward-compat pytest (`tests/scripts/test_backward_compatibility.py`) passes 5/5 byte-identical against the existing baselines under `SOURCE_DATE_EPOCH=1700000000`. The 6th example (agentic-app) was regenerated by T057 as the US2 AC-3 independent test.
  - **Governance**: PM + Architect + Team-Lead all signed off APPROVED_WITH_CONCERNS on tasks.md (4 LOW items addressed inline via T055a model frontmatter, T055b self-documenting review, T055c dependency diff, T055d ADR Accepted post-condition). Phase 1a / Phase 1b / Phase 1 Combined / Phase 3 full regression gates all passed. Phase 7 cross-agent overlap audit (T047) and aggregate enrichment tally (T049) passed.
  - **New CI integration**: none — all Wave 18 test work runs through the existing `tests/scripts/test_backward_compatibility.py` suite. Zero new runtime dependencies (SC-014 — empty diff on `pyproject.toml`, `requirements*.txt`, `package.json`). 18-wave build structure, 68 tasks total (67 originally + 4 inline additions T055a/b/c/d − 3 original count). ~25h realistic effort.
- **Feature 130**: Fix Attack Path Mermaid Rendering When mmdc Is Not Installed
  - Silent text-fallback replaced with loud fail-fast behavior at two enforcement points. Defense-in-depth: shell-level preflight gate in `.claude/commands/tachi.security-report.md` Step 1 + Python-level `shutil.which("mmdc")` raise in `scripts/extract-report-data.py::render_mermaid_to_png()`. Both fire only when `attack-trees/` contains Critical/High findings (gated — backward compatible for projects without attack trees).
  - Mid-render failure aggregator: `_render_single` now returns structured `error_record` dicts (keys: `id`, `file_path`, `failure_class` of `"exit:<code>"`/`"timeout"`/`"signal"`, `stderr_excerpt` first 200 bytes). `render_mermaid_to_png()` `as_completed` loop collects failures and raises `RuntimeError` with a per-finding failure list instead of silently marking `has_image=False`.
  - Text-fallback Typst branch deleted outright: `templates/tachi/security-report/attack-path.typ` lines 78-86 (the `else if mermaid-text != ""` block) removed — no placeholder, no "removed in 130" stub.
  - Documentation sync across 5 files: `README.md` (new `## Prerequisites` section naming `typst` + `@mermaid-js/mermaid-cli` with macOS/Linux/WSL install commands), `scripts/install.sh` (courtesy `command -v mmdc` warning), `docs/architecture/00_Tech_Stack/README.md` line 279 (rewritten as hard prerequisite with ADR-022 cross-ref), `specs/112-attack-path-pages/spec.md` SC-004 (inverted — text fallback is no longer a supported shipping mode), `specs/112-attack-path-pages/research.md` line 80 (pymmdc factual correction: GPL-3.0 Node.js wrapper, NOT a pure-Python renderer) plus a Durable Decision Rationale block.
  - **New ADR-022** (`docs/architecture/02_ADRs/ADR-022-mmdc-hard-prerequisite.md`) — the first ADR in tachi governing CLI-prerequisite posture. Establishes the new rule: **pipeline is fail-loud when a required CLI is absent, gated on input detection** (mmdc is required only when attack trees are present). Cross-references ADR-014 (optional external APIs) and ADR-021 (determinism). "Future Work" clause flags extraction of an `install.sh` prerequisite helper if a third CLI prerequisite is ever added.
  - **New CI workflow** (`.github/workflows/tachi-mmdc-preflight.yml`) — runs on `ubuntu-latest` (no mmdc preinstalled), installs Typst + Python 3.11, asserts the pipeline aborts non-zero on `examples/mermaid-agentic-app/` with all 3 canonical tokens in stderr (`@mermaid-js/mermaid-cli`, `npm install -g @mermaid-js/mermaid-cli`, `Attack path rendering`). Includes team-lead T4 enforcement assertion guarding against transitive mmdc install.
  - **New test file** `tests/scripts/test_mmdc_preflight.py` (9 tests: 4 preflight + 5 mid-render aggregator). Full pytest suite: 48/48 green. Backward-compatibility suite: 5/5 baselines byte-identical under `SOURCE_DATE_EPOCH=1700000000` (per ADR-021) — happy path (mmdc present) is byte-identical pre/post refactor.
  - **Seven-location canonical command consistency** (Architect refinement R4): the install command `npm install -g @mermaid-js/mermaid-cli` appears in exactly 7 enforcement locations (extract-report-data.py raise, tachi.security-report.md shell echo, install.sh warning, README Prerequisites, test_mmdc_preflight.py assertion, tachi-mmdc-preflight.yml grep, ADR-022 decision body). Verified via T023 grep consistency check.
  - **Breaking change (explicit, documented)**: silent text fallback is no longer a supported shipping mode. Previously-broken PDFs (Mermaid source dumped verbatim into PDF when mmdc was absent) now produce a loud preflight error instead. Deliberate correctness improvement — documented in spec 112 SC-004 (inverted) and the Feature 130 PRD Risk 130.2.
- **Feature 136**: MAESTRO Canonical Layer Correctness Fix
  - Renamed MAESTRO L5/L6/L7 to canonical CSA names per Ken Huang authoritative definition: L5 "Security" → "Evaluation and Observability", L6 "Agent Ecosystem" → "Security and Compliance", L7 "User Interface" → "Agent Ecosystem". Corrected MAESTRO acronym expansion to "Multi-Agent Environment, Security, Threat, Risk, and Outcome".
  - Schema bump: `schemas/finding.yaml` `maestro_layer` enum values renamed; `schema_version` bumped 1.2 to 1.3. Establishes new **enum-value-only minor-bump rule**: enum-value-only breaking changes warrant a minor schema bump (x.y+1), not major, provided schema shape and required fields unchanged. Rule documented in ADR-020 Revision History as precedent for future enum corrections.
  - Pipeline is fully data-driven — zero Python script changes required. All 14 foundation files touched are content-only: shared reference (`maestro-layers-shared.md` with verbatim Ordering Rationale explaining L5-before-L6 specificity gradient), schema, Typst templates (`maestro-findings.typ` prose + fallback dict fix for pre-existing "Integration Services" bug), pipeline docs (`dispatch-rules.md`, `output-schemas.md`, `finding-format-shared.md`), output schemas (`threats.md`), infographic templates (`infographic-maestro-stack.md`, `infographic-maestro-heatmap.md`), `README.md`, `docs/architecture/00_Tech_Stack/README.md`, ADR-020.
  - **Latent Feature 128 bug fixed** (scope expansion inside PR): `templates/tachi/security-report/full-bleed.typ` `infographic-page()` function now constrains image height to 7.5in with `fit: "contain"` to handle portrait-aspect infographics that would otherwise overflow the page.
  - All 6 example outputs regenerated with canonical layer names. 5 byte-deterministic PDF baselines regenerated via `SOURCE_DATE_EPOCH=1700000000` (per ADR-021); agentic-app excluded per Feature 128 convention. 2 MAESTRO golden fixtures (`maestro-heatmap.json`, `maestro-stack.json`) confirmed frozen pre-MAESTRO schema — no regeneration needed.
  - Release v4.10.0 auto-cut by release-please on merge to main (PR #146, squash commit 31356fb).
  - Known follow-up items: (1) agentic-app sample-report JPEGs to be re-rendered via Gemini in housekeeping PR, (2) infographic extract tier-selection bug when source is compensating-controls.md.
- **Feature 128**: Executive Threat Architecture Infographic
  - New `executive-architecture` template (6th infographic template) in `scripts/extract-infographic-data.py`; groups components into architectural layers via existing `_compute_trust_zones()`, filters Critical/High findings, selects one callout per layer
  - Portrait JPEG output: `threat-executive-architecture.jpg` generated via existing Gemini integration (no new API calls or dependencies)
  - PDF integration via `scripts/extract-report-data.py` `detect_images()` and `templates/tachi/security-report/main.typ`: new page placed immediately after Executive Summary (pages 2-3) using existing `infographic-page()` Typst function -- NO new template function
  - Schema additions in `schemas/infographic.yaml` (executive-architecture template enum entry with section structure and visual directive constants)
  - Command updates in `.claude/commands/tachi.infographic.md`: `exec` alias dispatch + inclusion in `all` shorthand expansion
  - New reference doc: `.claude/skills/tachi-infographics/references/executive-architecture.md`
  - **pytest bootstrap** (first-time addition of Python test infrastructure to tachi): new `pyproject.toml`, `requirements-dev.txt` (pytest>=8.0, pytest-cov>=4.1), `tests/` directory with `conftest.py` and `tests/scripts/` containing 6 test files covering 150+ tests across the extraction pipeline. `Makefile` gains `test:` target. Developer-only — runtime `scripts/*.py` remain stdlib-only per zero-dependency constraint.
  - New fixtures and golden files: `tests/scripts/fixtures/exec_arch/` (8 variations), `tests/scripts/fixtures/report_data/`, `tests/scripts/fixtures/golden/` (5 golden JSON files)
  - Baseline PDFs for backward-compatibility test: `examples/{web-app,microservices,ascii-web-api,mermaid-agentic-app,free-text-microservice}/security-report.pdf.baseline` (committed; use `SOURCE_DATE_EPOCH=1700000000` per ADR-021 for byte-deterministic comparison)
  - New ADR-021: SOURCE_DATE_EPOCH for deterministic PDF comparison (reproducible-builds convention for the backward-compatibility test; production pipeline unchanged)
  - Backward compatible: 5 example PDFs byte-identical without the new executive-architecture JPEG present; the 6th example (agentic-app) is intentionally regenerated as the feature demonstration
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
