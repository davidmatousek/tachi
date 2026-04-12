# Technology Stack - tachi

**Last Updated**: 2026-04-09
**Owner**: Architect

---

## Overview

This document defines the technology stack for tachi.

---

## Frontend

**Framework**: {{FRONTEND_FRAMEWORK}}
- Version: {{VERSION}}
- Why: {{RATIONALE}}

**UI Library**: {{UI_LIBRARY}}
- Examples: React, Vue, Svelte, Angular

**Styling**: {{STYLING_APPROACH}}
- Examples: Tailwind CSS, CSS Modules, Styled Components

**State Management**: {{STATE_MANAGEMENT}}
- Examples: Redux, Zustand, Jotai, Context API

**Build Tool**: {{BUILD_TOOL}}
- Examples: Vite, Webpack, Parcel

---

## Backend

**Runtime**: {{BACKEND_RUNTIME}}
- Examples: Node.js, Python, Go, Rust

**Framework**: {{BACKEND_FRAMEWORK}}
- Examples: Fastify, Express, FastAPI, Gin

**Language**: {{BACKEND_LANGUAGE}}
- Version: {{VERSION}}

**API Style**: {{API_STYLE}}
- Examples: REST, GraphQL, gRPC

---

## Database

**Primary Database**: {{DATABASE_TYPE}}
- Examples: PostgreSQL, MySQL, MongoDB

**Version**: {{VERSION}}
**Provider**: {{DATABASE_PROVIDER}}
- Examples: Self-hosted, AWS RDS, Neon, PlanetScale

**ORM/Query Builder**: {{ORM}}
- Examples: Prisma, Drizzle, TypeORM, SQLAlchemy

---

## Infrastructure

**Hosting Platform**: {{HOSTING_PLATFORM}}
- Examples: Vercel, AWS, Google Cloud, Railway

**Container Runtime**: {{CONTAINER_RUNTIME}}
- Examples: Docker, Kubernetes, None (serverless)

**CI/CD**: GitHub Actions
- `release-please` (googleapis/release-please-action@v4): Automated version tagging and CHANGELOG generation on merge to main (Feature 086)
- Configuration: `release-please-config.json` (changelog sections), `.release-please-manifest.json` (current version), `.github/workflows/release-please.yml` (workflow trigger)
- Release type: `simple` (no package manager integration; version tracked in manifest)
- Why: Convention-based release automation from Conventional Commits; eliminates manual `git tag` and CHANGELOG maintenance

---

## Monitoring & Observability

**Logging**: {{LOGGING_SOLUTION}}
**Metrics**: {{METRICS_SOLUTION}}
**Error Tracking**: {{ERROR_TRACKING}}

---

## Development Tools

**Package Manager**: {{PACKAGE_MANAGER}}
**Code Quality**: {{LINTING_TOOLS}}
**Testing**: {{TESTING_FRAMEWORKS}}

---

## AOD Kit Internal Tooling

These are tools used by the AOD Kit itself (not the adopter's application stack).

### Threat Modeling Schemas (Feature 001)

**Directory**: `schemas/` (machine-readable data contracts for threat analysis pipeline)
- Architecture: Hub-and-spoke content model -- `agents/` (hub) produces findings conforming to schemas, `templates/` (format) consumes them, `adapters/` serves dual role: knowledge-system configuration (scoring/context) and platform distribution (Feature 021) translating 15 hub agents into native formats for 5 target platforms
- Interface contract: `docs/INTERFACE-CONTRACT.md` -- single integration reference for input formats, dispatch rules, and output structure

| Schema | Purpose | Key Fields |
|--------|---------|------------|
| `schemas/finding.yaml` | Intermediate Representation (IR) -- data contract between agents and templates; optional `scored_finding` extension for quantitative risk scoring (Feature 035); baseline-aware fields `delta_status` and `baseline_run_id` (Feature 074); MAESTRO layer classification `maestro_layer` (Feature 084); canonical CSA layer names for L5/L6/L7 (Feature 136) | 13 fields: id, category, component, threat, likelihood, impact, risk_level, mitigation, references, dfd_element_type, maestro_layer (L1-L7 canonical CSA names or Unclassified, default Unclassified — L5 Evaluation and Observability, L6 Security and Compliance, L7 Agent Ecosystem per Feature 136), delta_status (NEW/UNCHANGED/UPDATED/RESOLVED), baseline_run_id (nullable); schema_version 1.3 (bumped 1.2 to 1.3 in Feature 136 for enum-value-only breaking change per ADR-020 Revision History rule); see `schemas/risk-scoring.yaml` for extension fields |
| `schemas/input.yaml` | Input validation -- accepted architecture description formats | 5 formats: ASCII, free-text, Mermaid, PlantUML, C4; includes recognition patterns and `format: auto` heuristic detection |
| `schemas/output.yaml` | Output structure -- sections required in generated threat model; includes SARIF severity mapping (Feature 012) | 8 sections + Section 4a/4b: System Overview, Trust Boundaries, STRIDE Tables, AI Threat Tables, **Correlated Findings (4a)**, **Resolved Findings (4b)** (Feature 074), Coverage Matrix, Risk Summary, Recommended Actions, **Delta Summary (8)** (Feature 104); SARIF severity mapping comment block with CVSS alignment (Feature 012) |
| `schemas/report.yaml` | Report output structure -- sections required in generated threat report (Feature 015, extended Feature 104) | 8 sections: Executive Summary, Architecture Overview, Threat Analysis, Cross-Cutting Themes, Attack Trees, Remediation Roadmap, Appendix: Finding Reference, **Delta Summary (8)** (Feature 104); schema_version 1.1; attack tree file naming convention `{finding-id}-attack-tree.md`; finding reference completeness rules; baseline frontmatter fields (baseline_source, baseline_date, delta_counts) |
| `schemas/infographic.yaml` | Infographic output structure -- sections required in generated threat infographic specification (Feature 018) | 6 sections: Metadata, Risk Distribution, Coverage Heat Map, Top Critical Findings, Architecture Threat Overlay, Visual Design Directives; CVSS color palette (#DC2626/#F97316/#EAB308/#4169E1/#6B7280); 16:9 landscape layout with three-zone structure |
| `schemas/risk-scoring.yaml` | Scored finding schema extending `finding.yaml` with quantitative risk scoring (Feature 035); baseline-aware fields `score_source` and `score_bounds` (Feature 074) | 4 scoring dimensions (cvss_base, exploitability, scalability, reachability), composite weights (0.35/0.30/0.15/0.20), 8 category CVSS defaults, 4 severity bands with SLA/disposition mapping, governance fields (risk_owner, remediation_sla, risk_disposition, review_date), score_source (inherited/fresh), score_bounds (min/max per category for NEW findings) |
| `schemas/compensating-controls.yaml` | Control finding IR extending `risk-scoring.yaml` with compensating control fields (Feature 036); baseline-aware fields `control_carry_forward` and `rescan_scope` (Feature 074) | 10 control categories (8 STRIDE-mapped + 2 AI-specific), effectiveness ratings (Strong/Moderate/Weak/None), residual risk calculation fields, control evidence and gap tracking, coverage matrix dimensions, control_carry_forward (boolean), rescan_scope (full/incremental) |
| `schemas/coverage-checklists.yaml` | Coverage gate configuration -- required threat categories per DFD element type and AI subtype (Feature 074) | 6 component types (external_entity, process, data_store, data_flow, llm_process, mcp_server), per-type required STRIDE/AI categories, AI subtype keyword detection (LLM/MCP), category-to-agent mapping table, validation rules (precedence, minimum requirements, targeted re-analysis) |

**Threat agent prompts**: `agents/` (11 agent prompt files + orchestrator + report agent + infographic agent + risk-scorer agent + control-analyzer agent); distributed to 5 target platforms via `adapters/` hub-and-spoke pattern (Feature 021). Right-sized in Feature 029: orchestrator (2,085->1,273 lines, -39%), report (801->472 lines, -41%), infographic (592->414 lines, -30%) via reference-extraction pattern -- consultation-only content moved to co-located reference files loaded on-demand via Read tool. Further domain knowledge extraction in Feature 075: orchestrator (1,273->769 lines), risk-scorer and control-analyzer reduced to under 1,000 lines each via skill extraction -- domain reference tables moved to standalone `.claude/skills/tachi-*` skill files with tiered loading (SKILL.md + references/). Baseline-aware pipeline extensions in Feature 074: orchestrator, risk-scorer, and control-analyzer agents enhanced with delta-aware logic (carry-forward, isolated discovery, merge+dedup, coverage gate); new baseline-correlation reference added to `tachi-orchestration` skill. Agent context optimization in Feature 078: all 6 methodology and report agents restructured from monolithic prompts to lean definitions with on-demand skill references, 4 new skill directories created (tachi-orchestration extended, tachi-report-assembly, tachi-threat-reporting, tachi-infographics), shared definitions extracted to `tachi-shared` skill (severity bands, STRIDE+AI categories, finding format), explicit `model: sonnet` field added to all 17 agent YAML frontmatter for intentional model-to-task matching, 40-60% prompt size reduction across all restructured agents. Detection tier lean refactor in Feature 082: all 11 threat agents (6 STRIDE + 5 AI) migrated to the lean + skill references pattern, aligning with the infrastructure tier established in Features 029/075/078. Each threat agent file drops from 113-201 lines to 50-114 lines (all STRIDE ≤120, all AI ≤150, hard cap FR-10 ≤180) with a single `**MANDATORY**: Read` directive at detection start that loads its companion `.claude/skills/tachi-<name>/references/detection-patterns.md` file. 11 new companion skill directories host the externalized pattern catalogs. Catalog enrichment: +30 new pattern categories added across the 11 agents during the refactor (22-category aggregate floor cleared with +8 margin), drawing from OWASP Top 10 2021, OWASP LLM Top 10 2025, OWASP AI Exchange, MITRE ATT&CK v15+, MITRE ATLAS v5.1+ (including the October 2025 agent techniques AML.T0058-T0062), CWE Top 25 2024, and NIST AI 600-1. Shared reference additive consolidation in `finding-format-shared.md` adds a "For Threat Agents" producer section. Feature 082 introduces ADR-023 recording the **sibling detection variant** of the lean pattern — tachi now documents two lean-agent shapes: the **methodology variant** (phase-gated `**MANDATORY**: Read` directives at each pipeline phase, used by the 6 infrastructure agents) and the **detection variant** (single-point load at detection start, used by the 11 threat agents). All 17 agents are now on the lean + skill references pattern.
| Subdirectory | Count | Scope | Status |
|-------------|-------|-------|--------|
| `agents/stride/` | 6 agents | STRIDE categories: Spoofing, Tampering, Repudiation, Info Disclosure, Denial of Service, Privilege Escalation | Validated end-to-end (Feature 005) |
| `agents/ai/` | 5 agents | AI-specific threats: Prompt Injection, Tool Abuse, Data Poisoning, Model Theft, Agent Autonomy; two-layer keyword dispatch (AG-prefixed agentic, LLM-prefixed LLM categories) | Validated end-to-end (Feature 007) |
| `agents/orchestrator.md` | 1 agent | Central orchestrator implementing OWASP 4-phase workflow (Scope, Determine Threats, Determine Countermeasures, Assess) with Phase 5 (Report) integration, STRIDE-per-Element dispatch, AI keyword dispatch (Feature 003), cross-agent correlation detection with deduplicated coverage matrix and risk summary (Feature 010), SARIF 2.1.0 output generation for GitHub Code Scanning integration (Feature 012), and narrative report dispatch with Mermaid attack trees (Feature 015). Infographic generation extracted to standalone `/tachi.infographic` command (Feature 039). Baseline-aware pipeline (Feature 074): Phase 0 baseline detection and finding registry extraction, carry-forward with delta classification (NEW/UNCHANGED/UPDATED/RESOLVED), isolated discovery with coverage-only context, merge+dedup with fingerprint matching, and coverage gate using `schemas/coverage-checklists.yaml`. MAESTRO layer classification (Feature 084): Phase 1 keyword-based component classification using CSA seven-layer taxonomy, MAESTRO Layer column in Component Inventory and Dispatch Table, finding inheritance in Phase 3, "Risk by MAESTRO Layer" subsection in Risk Summary, MAESTRO tags in SARIF output. Right-sized to 1,273 lines with 3 reference documents (Feature 029); domain knowledge extracted to `tachi-orchestration` skill (769 lines, Feature 075; extended with baseline-correlation reference, Feature 074) | Complete |
| `agents/threat-report.md` | 1 agent | Report generation agent transforming `threats.md` into narrative threat report with executive summary, Mermaid attack trees for Critical/High findings, prioritized remediation roadmap with effort estimates, and complete finding traceability (Feature 015). Delta-aware narrative generation (Feature 104): adapts executive summary and threat analysis to highlight baseline changes, generates Section 8 Delta Summary with lifecycle counts and remediation proof, populates baseline frontmatter fields. Right-sized to 472 lines with 1 reference document (Feature 029) | Validated end-to-end (Feature 015) |
| `agents/threat-infographic.md` | 1 agent | Infographic agent transforming threat model output into visual infographic specifications and images via Gemini API. Data extraction delegated to deterministic Python script (`scripts/extract-infographic-data.py`, Feature 071) replacing LLM-based parsing. Supports three-tier data source input: `compensating-controls.md` (residual risk), `risk-scores.md` (inherent risk), or `threats.md` (qualitative severity). Supports multiple templates: Baseball Card (risk summary dashboard), System Architecture (annotated architecture diagram with attack surface badges), Risk Funnel (4-tier progressive risk reduction), MAESTRO Stack (layered stack diagram), and MAESTRO Heatmap (layer x severity heat map). MAESTRO templates gated by `has-maestro-data` for backward compatibility; `maestro` shorthand dispatches both MAESTRO templates (Feature 091). Delta-aware extraction (Feature 104): extraction script reads baseline metadata and delta lifecycle fields from source artifacts, enabling infographic templates to display baseline comparison data. Risk labels adapt to data source type ("Residual Risk" / "Inherent Risk" / "Severity"). Right-sized to 414 lines with 2 reference documents (Feature 029, updated Feature 048, Feature 071) | Complete |
| `agents/tachi/risk-scorer.md` | 1 agent | Risk scoring agent applying four-dimensional quantitative assessment (CVSS 3.1 base, exploitability, scalability, reachability) to threat findings with weighted composite calculation, severity band mapping, and governance field assignment. Delta-aware scoring (Feature 074): inherits all scores for UNCHANGED findings (zero drift), re-scores UPDATED findings fresh, bounds NEW finding CVSS base scores within +/-1.0 of category defaults, and carries forward governance fields for persisting findings. MAESTRO layer propagation (Feature 084): passively reads and includes `maestro_layer` field in scored output. Produces dual output: `risk-scores.md` (human-readable) and `risk-scores.sarif` (machine-readable). Invoked via `/tachi.risk-score` command (Feature 035). Domain knowledge extracted to `tachi-risk-scoring` skill (994 lines, Feature 075; extended with baseline scoring rules, Feature 074) | Complete |
| `agents/tachi/control-analyzer.md` | 1 agent | Compensating controls analysis agent implementing 6-phase pipeline (parse, discover, detect, classify, recommend, output) to scan target codebases against scored threats. Detects existing security controls across 10 categories (8 STRIDE-mapped + 2 AI-specific), classifies effectiveness, recommends missing controls, calculates residual risk, and produces dual output: `compensating-controls.md` (human-readable) and `compensating-controls.sarif` (machine-readable). Delta-aware control analysis (Feature 074): carries forward control status, evidence, and residual risk for UNCHANGED findings; incremental re-scan scopes to NEW and UPDATED findings only. MAESTRO layer propagation (Feature 084): passively reads and includes `maestro_layer` field in control output. Invoked via `/tachi.compensating-controls` command (Feature 036). Domain knowledge extracted to `tachi-control-analysis` skill (935 lines, Feature 075; extended with carry-forward rules, Feature 074) | Complete |

**Agent reference documents** (Feature 029): Consultation-only content extracted from agent prompts into co-located reference files. Agents load references on-demand via Read tool at specific pipeline phases, keeping core prompts focused on always-needed execution logic. Applies the [On-Demand Reference File Segmentation](../03_patterns/README.md#pattern-on-demand-reference-file-segmentation) pattern at the agent level.

| Reference | Agent | Path | Loaded When |
|-----------|-------|------|-------------|
| SARIF Generation | orchestrator, risk-scorer | `adapters/claude-code/agents/references/sarif-generation.md` | Phase 4 completion; risk scoring SARIF generation (Feature 035 addendum: scored SARIF diff specification) |
| Validation Checklist | orchestrator | `adapters/claude-code/agents/references/validation-checklist.md` | Pipeline end |
| Error Templates | orchestrator | `adapters/claude-code/agents/references/error-templates.md` | Error condition |
| Report Templates | threat-report | `adapters/claude-code/agents/references/report-templates.md` | Attack tree generation |
| Gemini API Integration | threat-infographic | `adapters/claude-code/agents/references/infographic-gemini-api.md` | Image generation phase |
| Error Handling | threat-infographic | `adapters/claude-code/agents/references/infographic-error-handling.md` | Error condition |

**Tachi domain knowledge skills** (Feature 075, extended Feature 078): Domain reference tables and specifications extracted from methodology and report agents into standalone skill files using Read-tool loading per [ADR-002](../02_ADRs/ADR-002-prompt-segmentation.md). Each skill uses a tiered loading structure: SKILL.md (Level 2 metadata and loading table) plus references/ directory (Level 3 domain data loaded on-demand at specific pipeline phases). This extends the [On-Demand Reference File Segmentation](../03_patterns/README.md#pattern-on-demand-reference-file-segmentation) pattern to a third application level: agent-to-skill extraction. Feature 078 expanded scope from 3 methodology-agent skills to 7 skills covering all pipeline agents, plus a shared definitions skill consumed by multiple agents.

| Skill | Agent | References | Content |
|-------|-------|------------|---------|
| `.claude/skills/tachi-orchestration/` | orchestrator | `dispatch-rules.md`, `output-schemas.md`, `sarif-specification.md`, `baseline-correlation.md` (Feature 074), `format-detection.md`, `dfd-classification.md`, `trust-boundaries.md`, `coverage-requirements.md`, `coverage-matrix-model.md` (Feature 078) | STRIDE-per-Element dispatch tables, AI keyword mappings, output format specs, SARIF generation templates, validation checklists, error handling, baseline file detection, finding registry extraction, fingerprint correlation algorithm, delta classification rules, input format detection heuristics, DFD element classification rules, trust boundary notation, coverage requirements per component type, coverage matrix model |
| `.claude/skills/tachi-risk-scoring/` | risk-scorer | `cvss-vectors.md`, `scoring-dimensions.md`, `severity-bands.md`, `output-formatting.md`, `reachability-analysis.md`, `trust-zones.md` (Feature 078) | CVSS 3.1 base vector mappings, exploitability/scalability/reachability criteria, composite formulas, severity band thresholds, governance field derivation, scored output formatting rules, reachability analysis methodology, trust zone classification |
| `.claude/skills/tachi-control-analysis/` | control-analyzer | `control-categories.md`, `evidence-criteria.md`, `residual-risk.md` | 10 control category definitions with detection patterns, effectiveness classification criteria, residual risk calculation formulas, recommendation templates |
| `.claude/skills/tachi-report-assembly/` | report-assembler | `brand-asset-guidelines.md`, `typst-artifacts.md`, `typst-template-contract.md` (Feature 078) | Brand asset location and fallback rules, Typst artifact detection patterns with tier selection, Typst data variable contract with type specifications and image path resolution |
| `.claude/skills/tachi-threat-reporting/` | threat-report | `narrative-templates.md`, `attack-tree-construction.md`, `attack-tree-examples.md` (Feature 078) | Executive summary structure, per-category narrative templates, attack tree construction rules with Mermaid syntax, reference attack tree examples |
| `.claude/skills/tachi-infographics/` | threat-infographic | `infographic-specifications.md`, `template-specific-formats.md`, `gemini-prompt-construction.md`, `visual-design-system.md` (Feature 078) | Infographic specification formats, template-specific section layouts (Baseball Card, System Architecture, Risk Funnel, MAESTRO Stack, MAESTRO Heatmap -- Feature 091), Gemini API prompt construction rules, visual design system tokens |
| `.claude/skills/tachi-shared/` | orchestrator, risk-scorer, control-analyzer, threat-report, all threat agents | `severity-bands-shared.md`, `stride-categories-shared.md`, `finding-format-shared.md` (Feature 078), `maestro-layers-shared.md` (Feature 084, corrected Feature 136) | Canonical severity band definitions (thresholds, SLA, disposition), STRIDE+AI category definitions (8 categories with DFD element applicability), finding IR format specification, CSA MAESTRO seven-layer taxonomy with keyword-to-layer mappings for component classification -- single-source-of-truth consumed by multiple agents to prevent cross-agent drift. Feature 136 corrected L5/L6/L7 layer names to canonical CSA names (L5 Evaluation and Observability, L6 Security and Compliance, L7 Agent Ecosystem), corrected the MAESTRO acronym expansion, reassigned keyword tables accordingly, and established the enum-value-only minor-bump rule for schema versioning (see ADR-020 Revision History) |

**Infographic templates** (Feature 029, extended Feature 091): Template files for multi-template infographic generation, co-located with the portable agent set.

| Template | Path | Purpose |
|----------|------|---------|
| Baseball Card | `templates/tachi/infographics/infographic-baseball-card.md` | Risk summary dashboard with key metrics |
| System Architecture | `templates/tachi/infographics/infographic-system-architecture.md` | Annotated architecture diagram with attack surface badges |
| Risk Funnel | `templates/tachi/infographics/infographic-risk-funnel.md` | 4-tier vertical funnel showing progressive risk reduction through tachi pipeline (Feature 053) |
| MAESTRO Stack | `templates/tachi/infographics/infographic-maestro-stack.md` | Layered stack diagram mapping findings to CSA MAESTRO seven-layer taxonomy (Feature 091) |
| MAESTRO Heatmap | `templates/tachi/infographics/infographic-maestro-heatmap.md` | Layer x severity heat map showing finding density across MAESTRO layers (Feature 091) |

**Portable agent set** (Feature 029, extended Feature 035, Feature 036, Feature 053, Feature 091): `.claude/agents/tachi/` contains the complete threat agent set (11 threat agents + orchestrator + report + infographic + risk-scorer + control-analyzer + 5 infographic templates) in Claude Code native format. This set is the Claude Code platform adapter output, installed at `.claude/agents/tachi/` for direct invocation. The portable set mirrors the `adapters/claude-code/agents/` content with paths adjusted for the installation depth.

**STRIDE agent capabilities** (Feature 005):
- Each agent enforces STRIDE-per-Element matrix targeting (DFD element type filtering)
- AI-specific threat patterns included per agent (e.g., credential theft of API keys for LLM services, model poisoning via tampered training data)
- OWASP API Security 2023 cross-references (API1-API10) alongside OWASP Top 10 2021, CWE, and MITRE ATT&CK
- Finding ID convention: S-N (Spoofing), T-N (Tampering), R-N (Repudiation), I-N (Info Disclosure), D-N (DoS), E-N (Privilege Escalation)
- Component-specific findings enforced -- generic/untargeted threats rejected by agent prompts

**Standards**: OWASP 3x3 risk matrix (likelihood x impact), STRIDE-per-Element methodology (DFD element mapping), OWASP API Security 2023 (API1-API10), OWASP Top 10 2021 (A01-A10), OWASP references (ASI-xx, MCP-xx, LLM0x:2025 for AI agents), CWE and MITRE ATT&CK cross-references, SARIF 2.1.0 (OASIS standard for static analysis results interchange, Feature 012; baseline correlation via `baselineState` property, Feature 074), Mermaid `flowchart TD` syntax (attack tree visualization, Feature 015), CVSS severity color palette (infographic visual encoding, Feature 018), CVSS 3.1 base scoring (quantitative risk scoring with full vector string auditability, Feature 035), CSA MAESTRO (Multi-Agent Environment, Security, Threat, Risk, and Outcome -- seven-layer taxonomy for agentic AI component classification, Feature 084; canonical layer names for L5 Evaluation and Observability, L6 Security and Compliance, L7 Agent Ecosystem aligned with Ken Huang's authoritative CSA definition in Feature 136).

**Output templates** (all under `templates/tachi/`):
- `templates/tachi/output-schemas/threats.md` -- canonical 8-section + Section 4a/4b threat model template with `schema_version: "1.3"` frontmatter (bumped from 1.2 in Feature 136 for canonical MAESTRO layer rename). Section 4a (Correlated Findings) added in Feature 010. Coverage matrix uses three-state cell model (deduplicated count, "---" analyzed-but-clean, "n/a" not-applicable). Risk summary shows deduplicated counts with raw count parenthetical when different. Baseline-aware extensions (Feature 074): baseline frontmatter block (baseline_source, baseline_date, baseline_finding_count), delta_status column in all threat tables, RESOLVED findings section (Section 4b), and coverage gate results section. Downstream propagation extensions (Feature 104): Section 7 Recommended Actions gains Status column carrying delta_status for downstream parser consumption; new Section 8 Delta Summary with finding lifecycle counts (NEW/UNCHANGED/UPDATED/RESOLVED), remediation proof, and baseline reference table.
- `templates/tachi/output-schemas/threats.sarif` -- SARIF 2.1.0 reference template for structural documentation (Feature 012). Complete JSON structure with placeholder values demonstrating rule definitions, result mapping, dual locations, relatedLocations for correlated findings, and partialFingerprints for stable tracking. Baseline correlation properties (Feature 074): `baselineRunId` in `partialFingerprints`, `baselineState` property per result (new/unchanged/updated/absent).
- `templates/tachi/output-schemas/threat-report.md` -- canonical 8-section narrative threat report template with `schema_version: "1.1"` frontmatter (Feature 015, extended Feature 104). Sections: Executive Summary, Architecture Overview, Threat Analysis (agent-by-agent narrative), Cross-Cutting Themes, Attack Trees (Mermaid `flowchart TD` with inline rendering and standalone file references), Remediation Roadmap (prioritized with effort estimates), Appendix: Finding Reference (complete traceability table), Delta Summary (baseline lifecycle breakdown with remediation proof). Baseline-aware extensions (Feature 104): frontmatter gains `baseline_source`, `baseline_date`, and `delta_counts` (new/unchanged/updated/resolved) fields; delta-aware narrative generation adapts executive summary and threat analysis to highlight changes since baseline; Section 8 Delta Summary with finding lifecycle table and baseline reference. Schema version bumped 1.0 to 1.1. Validated against `schemas/report.yaml`.
- `templates/tachi/output-schemas/risk-scores.md` -- scored threat model template with executive summary (highest/average composite, severity distribution), scored threat table (all 4 dimensions + composite + governance per finding), and methodology section documenting scoring weights and severity bands (Feature 035). Baseline-aware extensions (Feature 074): score_source column (inherited/fresh), baseline reference in frontmatter. Validated against `schemas/risk-scoring.yaml`.
- `templates/tachi/output-schemas/risk-scores.sarif` -- SARIF 2.1.0 scored output template extending `threats.sarif` structure with per-finding composite scores in `properties` bag, per-rule MAX composite in `security-severity`, and governance fields (Feature 035). Baseline-aware extensions (Feature 074): `score_source` property per result. Fingerprints preserved from source for GitHub Code Scanning alert supersession.
- `templates/tachi/output-schemas/compensating-controls.md` -- compensating controls analysis template with executive summary (control coverage percentage, residual risk), per-finding control inventory (detected controls with effectiveness rating, gaps, recommendations), coverage matrix (10 control categories x components), and residual risk summary (Feature 036). Baseline-aware extensions (Feature 074): control_carry_forward column, rescan_scope in frontmatter. Validated against `schemas/compensating-controls.yaml`.
- `templates/tachi/output-schemas/compensating-controls.sarif` -- SARIF 2.1.0 compensating controls output template extending `risk-scores.sarif` structure with control detection results, effectiveness classifications, and residual risk scores in `properties` bag (Feature 036). Baseline-aware extensions (Feature 074): `carry_forward` property per result. Fingerprints preserved from source for GitHub Code Scanning alert chain continuity.

**SARIF output** (Feature 012, extended Feature 074, Feature 084): The orchestrator produces `threats.sarif` alongside `threats.md` during Phase 4 (Assess). SARIF generation maps all finding IR data to SARIF 2.1.0 format with CVSS-aligned severity (Critical=error/9.0, High=error/8.0, Medium=warning/5.0, Low=note/2.0, Note=note/0.1), deterministic fingerprints (SHA-256 of ruleId + component_name) for stable GitHub Code Scanning alert tracking, dual physical/logical locations for component navigation, and optional OWASP/CWE taxonomy references. 8 rule IDs map to the combined STRIDE + AI category set (`tachi/stride/*` and `tachi/ai/*`). Baseline correlation (Feature 074): `baselineRunId` in `partialFingerprints` links findings to their baseline origin; `baselineState` property (new/unchanged/updated/absent) on each result enables cross-run tracking in SARIF-compatible tools. MAESTRO layer tags (Feature 084): `maestro-layer:{layer-id}` tag in `properties.tags[]` per result for layer-based filtering in SARIF-compatible tools.

**Report output** (Feature 015, extended Feature 104): After Phase 4, the orchestrator dispatches Phase 5 (Report, default-on, opt-out via `--skip-report` flag or `report: false` configuration) to the report agent (`agents/threat-report.md`). Phase 5 produces `threat-report.md` (8-section narrative report, schema_version 1.1) and `attack-trees/` (standalone Mermaid `flowchart TD` files, one per Critical/High finding). The report agent receives only `threats.md` as input in a fresh context (context isolation boundary). Downstream baseline propagation (Feature 104): the report agent reads baseline metadata and delta lifecycle counts from `threats.md` frontmatter and Section 8 Delta Summary, populates `threat-report.md` frontmatter with `baseline_source`, `baseline_date`, and `delta_counts` fields, and generates delta-aware narrative in the executive summary, threat analysis, and a new Section 8 Delta Summary.

**Infographic output** (Feature 018, updated Feature 039, Feature 048, Feature 071): Infographic generation is a standalone `/tachi.infographic` command, no longer part of the orchestrator pipeline. Data extraction is delegated to a deterministic Python script (`scripts/extract-infographic-data.py`, Feature 071) that replaces LLM-based parsing, producing byte-identical JSON output for identical inputs. The script uses the shared `tachi_parsers.py` module for cross-output consistency with the security report pipeline. The `/tachi.infographic` command auto-detects the richest available data source using a three-tier priority hierarchy: `compensating-controls.md` (residual risk) > `risk-scores.md` (inherent risk) > `threats.md` (qualitative severity). Supports explicit file override with content-based type detection and template selection (`--template baseball-card|system-architecture|risk-funnel|maestro-stack|maestro-heatmap|maestro|all`). The `maestro` shorthand dispatches both MAESTRO templates (maestro-stack + maestro-heatmap); MAESTRO templates are gated by `has-maestro-data` and silently skipped when MAESTRO layer data is absent (Feature 091). The infographic agent invokes the extraction script, reads the resulting JSON, and generates the specification. Percentage values use the Largest Remainder Method to guarantee integer percentages summing to exactly 100. Risk labels adapt to source type: "Residual Risk" (compensating-controls), "Inherent Risk" (risk-scores), "Severity" (threats). Enhancement tips guide users toward richer pipeline tiers during auto-detection. Produces `threat-infographic-spec.md` (6-section visual risk specification conforming to `schemas/infographic.yaml`) and optionally `threat-infographic.jpg` (presentation-ready image via Google Gemini API, conditional on `GEMINI_API_KEY`). The specification is the primary deliverable; the image is best-effort with graceful degradation on API errors, rate limits, content policy rejections, or missing API key. See [ADR-014](../02_ADRs/ADR-014-gemini-api-optional-image-generation.md) for the external API integration decision and [ADR-017](../02_ADRs/ADR-017-deterministic-infographic-extraction.md) for the deterministic extraction decision.

**Risk scoring output** (Feature 035): The `/tachi.risk-score` command invokes the risk-scorer agent (`agents/tachi/risk-scorer.md`) as a standalone post-pipeline step. The risk-scorer parses `threats.md` (canonical) or `threats.sarif` (fallback), applies four-dimensional quantitative scoring per finding (CVSS 3.1 base, exploitability, scalability, reachability), calculates a weighted composite (0.35/0.30/0.15/0.20), maps to severity bands aligned with `output.yaml`, and assigns governance fields (risk_owner, remediation_sla, risk_disposition, review_date). Produces `risk-scores.md` (human-readable scored threat table) and `risk-scores.sarif` (machine-readable, supersedes `threats.sarif` in GitHub Code Scanning via preserved fingerprints). Schema: `schemas/risk-scoring.yaml`. The SARIF generation reference (`adapters/claude-code/agents/references/sarif-generation.md`) documents the structural differences between `threats.sarif` and `risk-scores.sarif`.

**Compensating controls output** (Feature 036): The `/tachi.compensating-controls` command invokes the control-analyzer agent (`agents/tachi/control-analyzer.md`) as the third stage of the threat analysis pipeline. The control-analyzer accepts `--target` (codebase path to scan), `--input` (risk-scores.md or risk-scores.sarif), and `--output-dir` flags. It executes a 6-phase pipeline: (1) parse scored threats, (2) discover target codebase structure, (3) detect existing security controls per component using 10 categories (8 STRIDE-mapped: authentication, integrity, audit-logging, data-protection, availability, access-control, input-validation, encryption-in-transit; 2 AI-specific: prompt-safety, agent-guardrails), (4) classify control effectiveness (Strong/Moderate/Weak/None), (5) recommend missing controls and calculate residual risk, (6) output dual-format results. Produces `compensating-controls.md` (human-readable control inventory with coverage matrix) and `compensating-controls.sarif` (machine-readable, supersedes `risk-scores.sarif` in GitHub Code Scanning alert chain). Schema: `schemas/compensating-controls.yaml`.

**Full pipeline output**: `threats.md` + `threats.sarif` (Phase 4) + `threat-report.md` + `attack-trees/*.md` (Phase 5). **Post-pipeline**: `risk-scores.md` + `risk-scores.sarif` (via `/tachi.risk-score` command, Feature 035) + `compensating-controls.md` + `compensating-controls.sarif` (via `/tachi.compensating-controls` command, Feature 036) + `threat-infographic-spec.md` + `threat-infographic.jpg` (via `/tachi.infographic` command, Feature 039; image conditional on Gemini API key). **Baseline-aware mode** (Feature 074): When a baseline `threats.md` exists (auto-detected or via `--baseline` flag), all pipeline outputs include delta annotations (NEW/UNCHANGED/UPDATED/RESOLVED), inherited scores and control status for stable findings, and coverage gate results. First-run behavior (no baseline) is identical to the stateless pipeline. **Downstream baseline propagation** (Feature 104): Baseline metadata (source, date, finding count, run ID) and delta lifecycle counts from `threats.md` Section 8 are propagated through all downstream stages -- `threat-report.md` (delta-aware narrative, Section 8 Delta Summary), extraction scripts (`extract-report-data.py` Typst variables, `extract-infographic-data.py` JSON fields), and commands (`/tachi.infographic` and `/tachi.security-report` baseline data display). Parser functions in `tachi_parsers.py` (`parse_baseline_frontmatter`, `parse_resolved_findings`) provide the shared extraction layer.

**Example threat models**: `examples/` contains 3 standardized reference implementations (web-app, agentic-app, microservices) pairing Mermaid architecture diagrams with complete schema v1.1 threat model outputs (Feature 024). See `examples/README.md` for usage instructions and framework mapping.

---

### Python Scripts

**Python 3.9+** (stdlib only, no external dependencies)
- All `scripts/*.py` files must use only Python standard library modules
- Why: Zero-dependency deterministic processing; avoids pip/virtualenv overhead for adopters
- Constraints: No third-party packages, no f-strings requiring >3.9, pathlib-based paths

**Key scripts**:
| Script | Purpose | Added |
|--------|---------|-------|
| `scripts/tachi_parsers.py` | Shared parser module (~815 lines) providing deterministic parsers for markdown tables, YAML frontmatter, severity distributions, findings, scope data, compensating controls, and baseline metadata. Extracted from `extract-report-data.py` to enable cross-script consistency -- both report and infographic extraction scripts import the same parsing functions, guaranteeing identical interpretation of the same source artifacts. Baseline-aware extensions (Feature 104): `parse_baseline_frontmatter()` extracts baseline metadata from nested YAML frontmatter block, `parse_resolved_findings()` parses Section 4b Resolved Findings table, `parse_threats_findings()` extended with optional `delta_status` field extraction from Status column. Attack tree detection (Feature 112): `detect_artifacts()` extended to detect `attack-trees/` directory and return `has_attack_trees` boolean with directory path. | Feature 071 (extracted from Feature 067), extended Feature 104, extended Feature 112 |
| `scripts/extract-report-data.py` | Deterministic extraction of structured data from tachi pipeline markdown artifacts (threats.md, risk-scores.md, compensating-controls.md, threat-report.md) into Typst data file (report-data.typ). Replaces LLM-based markdown parsing in the report-assembler agent. Supports 3-tier severity source hierarchy, validates internal consistency (severity sums, scope counts, unique finding IDs), and produces byte-identical output on identical inputs. MAESTRO data extraction (Feature 091): emits `has-maestro-data` boolean flag and per-layer finding variables for conditional `maestro-findings.typ` page inclusion. Baseline data extraction (Feature 104): emits baseline metadata variables (source, date, finding count, run ID) and delta lifecycle counts (new, unchanged, updated, resolved) from threats.md frontmatter and Section 8 Delta Summary; emits `has-baseline-data` boolean flag for conditional report section inclusion. Attack path extraction (Feature 112): `parse_attack_trees()` scans `attack-trees/` directory for Mermaid attack tree files, extracts metadata and cross-references findings; `render_mermaid_to_png()` converts Mermaid to PNG via `mmdc` subprocess (graceful fallback to raw text when `mmdc` unavailable); emits `has-attack-trees` boolean flag and structured attack tree array for conditional `attack-path.typ` page inclusion. Imports shared parsers from `tachi_parsers.py`. | Feature 067, refactored Feature 071, extended Feature 091, extended Feature 104, extended Feature 112 |
| `scripts/extract-infographic-data.py` | Deterministic extraction of structured infographic data (~1,100 lines) from tachi pipeline markdown artifacts into JSON data files for infographic templates (baseball-card, system-architecture, risk-funnel, maestro-stack, maestro-heatmap). Replaces LLM-based data extraction in the threat-infographic agent. Auto-detects richest data source (compensating-controls.md > risk-scores.md > threats.md), uses Largest Remainder Method for integer percentage rounding, and produces byte-identical JSON output on identical inputs. MAESTRO layer parsing extracts per-layer finding counts and severity distributions from `maestro_layer` field in source artifacts; gated by `has-maestro-data` flag (Feature 091). Baseline data extraction (Feature 104): extracts baseline metadata and delta lifecycle counts for infographic delta annotations; emits baseline fields in JSON output when baseline data is present. Imports shared parsers from `tachi_parsers.py`. | Feature 071, extended Feature 091, extended Feature 104 |

### Python Test Infrastructure (Feature 128)

**pytest 8.0+** (developer-only; not required by end users or the runtime pipeline)
- First-time addition of a Python test harness to tachi. Prior to Feature 128, `scripts/*.py` modules had no automated test coverage — ad-hoc manual verification only. Feature 128 bootstrapped the harness to cover the extraction pipeline (`extract-infographic-data.py`, `extract-report-data.py`, `tachi_parsers.py`) as part of the `executive-architecture` infographic template work.
- Why pytest (not `unittest`): fixture ergonomics, parametrized tests (one-to-many fixture coverage), rich assertion introspection, and `pytest-cov` coverage reporting — all standard choices for modern Python test suites. `unittest` would have required substantially more boilerplate for the same coverage.
- Why developer-only: runtime constraint from the Python Scripts section above (`scripts/*.py` must be stdlib-only, zero-dependency). The test harness lives outside runtime — adopters running `/tachi.threat-model`, `/tachi.security-report`, or `/tachi.infographic` do NOT install pytest. The harness is exclusively for tachi contributors verifying the extraction pipeline locally or in CI.

**Configuration files** (all added in Feature 128):

| File | Purpose |
|------|---------|
| `pyproject.toml` | Project config and `[tool.pytest.ini_options]` section; sets `testpaths = ["tests"]`, `python_files = ["test_*.py"]`, `addopts = "-ra --strict-markers"`. Non-disruptive to existing `scripts/*.py` runtime (no runtime imports of `pyproject.toml`). |
| `requirements-dev.txt` | Developer dependencies: `pytest>=8.0`, `pytest-cov>=4.1`. Installed via `pip install -r requirements-dev.txt`. |
| `Makefile` | `test:` target added in Feature 128 Wave 1 for `python3 -m pytest tests/` one-liner invocation. |
| `.gitignore` | Python patterns added in Feature 128 Wave 1 (`__pycache__/`, `.pytest_cache/`, `.coverage`, `htmlcov/`). |

**Test tree structure** (new in Feature 128):

| Path | Purpose |
|------|---------|
| `tests/conftest.py` | Shared pytest fixtures for all test modules |
| `tests/scripts/` | Test modules for `scripts/*.py` (6 test files, 150+ tests covering extraction, parsing, and output-shape contracts) |
| `tests/scripts/fixtures/exec_arch/` | Input fixtures for the executive-architecture template (8 variations: with/without findings, single/multi-component scopes, tier-upgrade sources) |
| `tests/scripts/fixtures/report_data/` | Input fixtures for `extract-report-data.py` variants |
| `tests/scripts/fixtures/golden/` | Expected JSON payloads (5 golden files) for byte-identical regression testing |

**Running tests**:
```bash
pip install -r requirements-dev.txt      # one-time setup
make test                                  # or: python3 -m pytest tests/
python3 -m pytest tests/scripts/test_extract_infographic.py -v   # single module
python3 -m pytest tests/ --cov=scripts    # with coverage
```

**Backward-compatibility harness** (Feature 128 Wave 4): `tests/scripts/test_backward_compatibility.py` is a parametrized test that compiles the 5 unmodified example projects through the full PDF pipeline and compares the output byte-for-byte against committed `examples/*/security-report.pdf.baseline` files. The test sets `SOURCE_DATE_EPOCH=1700000000` before `typst compile` to neutralize PDF metadata timestamps — see [ADR-021](../02_ADRs/ADR-021-source-date-epoch-for-deterministic-pdf-comparison.md) for the reproducible-builds rationale.

### Shell Scripts

**Bash 3.2** (macOS default `/bin/bash`)
- All `.aod/scripts/bash/*.sh` files must be Bash 3.2 compatible
- Why: macOS ships Bash 3.2.57 due to GPLv3 licensing; portability is mandatory
- Constraints: No associative arrays, no `${var^^}`, no `readarray`/`mapfile`

**Key scripts**:
| Script | Purpose | Added |
|--------|---------|-------|
| `.aod/scripts/bash/logging.sh` | Simple logging utility for timestamped log entries; provides `aod_log` function with configurable output path and graceful error handling | Feature 049 |
| `.aod/scripts/bash/run-state.sh` | Atomic read/write/validate for orchestrator state (`.aod/run-state.json`); includes compound helpers for incremental reads and governance caching | Feature 022, extended Feature 030 |
| `.aod/scripts/bash/github-lifecycle.sh` | GitHub Issue label management for stage transitions | Pre-022 |
| `.aod/scripts/bash/backlog-regenerate.sh` | Regenerate product backlog from GitHub Issues | Pre-022 |
| `scripts/generate-adapter-version.sh` | Generate `VERSION` manifest for platform adapters with source commit SHA, timestamp, and per-agent SHA-256 checksums for drift detection | Feature 021 |
| `scripts/install.sh` | Bash 3.2+ install script that copies all distributable files from tachi source to target project using INSTALL_MANIFEST.md machine-parseable section; supports `--source`, `--version` (git tag checkout with trap cleanup), and `--help` flags | Feature 066 |

### CLI Dependencies

| Tool | Required By | Purpose | Install |
|------|-------------|---------|---------|
| `jq` | `run-state.sh` | JSON parsing and atomic state manipulation | `brew install jq` (macOS) / `apt-get install jq` (Linux) |
| `gh` | `github-lifecycle.sh`, `run-state.sh` (optional), `scripts/init.sh` (optional) | GitHub Issue/label management, Projects board creation during init | `brew install gh` / `gh auth login` |
| `python3` | `scripts/extract-report-data.py` (invoked by report-assembler agent) | Deterministic markdown-to-Typst data extraction for security report pipeline; stdlib only, no pip dependencies (Feature 067) | Pre-installed on macOS; `apt-get install python3` (Linux) |
| `typst` | `/tachi.security-report` command (report-assembler agent) | PDF compilation from modular `.typ` templates; renders security assessment reports with brand assets, auto-generated TOC, and conditional page inclusion (Feature 054, extended Feature 060); MAESTRO Findings page conditionally included via `has-maestro-data` flag (Feature 091); Attack Path pages conditionally included via `has-attack-trees` flag (Feature 112) | `brew install typst` (macOS) / `cargo install typst-cli` / [typst.app](https://github.com/typst/typst/releases) |
| `mmdc` | `scripts/extract-report-data.py` (invoked by report-assembler agent) | Mermaid CLI for rendering attack tree Mermaid diagrams to PNG images for PDF report embedding; hard prerequisite as of Feature 130 when `attack-trees/` contains Critical/High findings — see [ADR-022](../02_ADRs/ADR-022-mmdc-hard-prerequisite.md) (introduced Feature 112, posture changed Feature 130) | `npm install -g @mermaid-js/mermaid-cli` |
| `pytest` | `tests/scripts/*.py` (developer-only; not runtime) | Python test runner for the `scripts/*.py` extraction pipeline and `tachi_parsers.py` shared module; invoked via `make test` or `python3 -m pytest tests/` (Feature 128) | `pip install -r requirements-dev.txt` |

**Note**: `gh` degrades gracefully -- the orchestrator falls back to artifact-only detection when `gh` is unavailable or unauthenticated. Similarly, `scripts/init.sh` skips GitHub Projects board creation when `gh` is missing, unauthenticated, or lacks the `project` OAuth scope, reporting status in the init summary with remediation guidance.

**Note**: `typst` is required only for PDF report generation. The `/tachi.security-report` command validates Typst installation before compilation and reports a clear error if unavailable. All other tachi commands operate without Typst.

**Note**: `mmdc` (Mermaid CLI) is a **hard prerequisite** when `attack-trees/` contains Critical/High findings. The `/tachi.security-report` pipeline aborts at preflight with a non-zero exit code and a canonical three-line error message (naming the missing tool, the reason, and the exact install command `npm install -g @mermaid-js/mermaid-cli`) if `mmdc` is not on `PATH`. Projects without attack trees continue to work without `mmdc` — the gate fires only when attack-tree artifacts are present. See [ADR-022](../02_ADRs/ADR-022-mmdc-hard-prerequisite.md) for the rationale and the silent-fallback-to-loud-failure migration (Feature 130).

### External API Dependencies (Optional)

| API | Required By | Purpose | Authentication | Graceful Degradation |
|-----|-------------|---------|----------------|----------------------|
| Google Gemini API (`gemini-3-pro-image-preview`) | `agents/threat-infographic.md` (via `/tachi.infographic` command) | Optional image generation for threat infographic visualization | `GEMINI_API_KEY` environment variable | Spec always produced; image skipped if API key missing, rate limited (429), timed out (60s), or content policy rejected. Fallback model: `gemini-3.1-flash-image-preview`. See [ADR-014](../02_ADRs/ADR-014-gemini-api-optional-image-generation.md). |

**Note**: The Gemini API is entirely optional. The `/tachi.infographic` command produces the infographic specification (`threat-infographic-spec.md`) regardless of API availability. The specification is self-contained and can be used by a designer to render the infographic manually. Image generation is a best-effort enhancement.

### Template Variables

`scripts/init.sh` performs `sed` substitution on user-facing template files during `make init`. The following placeholders are replaced at init time:

| Placeholder | Replaced With | Scope |
|-------------|---------------|-------|
| `tachi` | Adopter's project name (entered at `make init` prompt) | 12 template files (Feature 061) |
| `2026-03-21` | Current date at init time | Select files |

**`tachi` is a first-class template variable** (Feature 061). All user-facing template files in `.claude/`, `docs/`, `CLAUDE.md`, and `README.md` use this placeholder rather than hardcoding "Agentic Oriented Development Kit". After `make init`, adopters see their own project name throughout.

When adding a new user-facing template file to the kit, use `tachi` wherever the project name should appear and confirm the file is included in the `scripts/init.sh` substitution loop. See [ADR-009](../02_ADRs/ADR-009-template-variable-expansion-scope.md) and the [Template Variable Expansion pattern](../03_patterns/README.md#pattern-template-variable-expansion).

---

### Subagent Results Directory

**Directory**: `.aod/results/` (ephemeral session artifacts, gitignored)
- Architecture: File-based offloading for minimal subagent returns (Feature 073)
- Convention: Each subagent writes detailed findings to `.aod/results/{agent-name}.md` before returning
- Return policy: Subagents return only STATUS + ITEMS count + DETAILS path to the main context (max 10 lines / ~200 tokens)
- Overwrite semantics: Each invocation overwrites the prior results file for the same agent
- Initialization: Subagents create the directory if absent (self-healing, no pre-init required)
- See [ADR-010](../02_ADRs/ADR-010-minimal-return-architecture.md) for the design decision
- See [Minimal-Return Subagent pattern](../03_patterns/README.md#pattern-minimal-return-subagent) for implementation guidance

**Context budget impact**: A full Triad review cycle (3 reviewers) consumes less than 600 tokens in the main context (down from 1,500-6,000 tokens), enabling 90+ minute sustained orchestration sessions.

---

### Stack Packs System

**Directory**: `stacks/` (convention contracts, persona supplements, scaffold templates, rules)
- Architecture: Dual-surface injection pattern (Feature 058)
- Management skill: `.claude/skills/aod-stack/SKILL.md` (`/aod.stack use|remove|list|scaffold`)
- State file: `.aod/stack-active.json` (JSON, tracks active pack name and activation timestamp)
- Runtime rules surface: `.claude/rules/stack/` (copied on activation, cleaned on removal)
- See ADR-007 for the design decision behind dual-surface injection

**Shipped packs**:
| Pack | Status | Purpose |
|------|--------|---------|
| `stacks/nextjs-supabase/` | Full | Next.js + TypeScript + Supabase + Prisma + Vercel conventions |
| `stacks/fastapi-react/` | Full | Python FastAPI + SQLAlchemy 2.0 async + React 19 + TypeScript + Vite + Docker Compose (Feature 078) |
| `stacks/fastapi-react-local/` | Full | Python FastAPI + SQLAlchemy 2.0 async + aiosqlite + React 19 + Vite + Tailwind CSS 4 — zero external dependencies, local-first variant (Feature 085) |
| `stacks/swiftui-cloudkit/` | Skeleton | SwiftUI + CloudKit native iOS conventions |
| `stacks/knowledge-system/` | Full | Markdown + YAML + Claude Code for knowledge-intensive content systems (Feature 064) |

**Pack anatomy** (each pack directory):
| Path | Purpose |
|------|---------|
| `STACK.md` | Convention contract (required, ≤500 lines) |
| `agents/*.md` | Persona supplements for specialized/hybrid agents (≤100 lines each) |
| `rules/*.md` | Stack-specific coding rules (copied to `.claude/rules/stack/` on activation) |
| `scaffold/` | Project template files (optional, used by `/aod.stack scaffold`) |
| `skills/` | Stack-specific skills (optional, reserved for future use) |

**Context budget enforcement**:
| Component | Max Lines | Loaded When |
|-----------|-----------|-------------|
| STACK.md | 500 | Every agent invocation (if pack active) |
| Persona supplement | 100 | Specialized/hybrid agent invocations only |
| Stack rules (all files combined) | 200 | Every agent invocation (via rules discovery) |
| Total pack overhead | 800 | Maximum per invocation |

### Kickstart Skill

**Skill file**: `.claude/skills/~aod-kickstart/SKILL.md` (`/aod.kickstart`)
- Architecture: Three-stage interactive workflow (Idea Intake → Stack Selection → Guide Generation) (Feature 085)
- Output: `docs/guides/CONSUMER_GUIDE_{PROJECT_NAME}.md` — sequenced consumer guide with 6-10 seed features
- Stack detection: Reads `.aod/stack-active.json` to auto-detect active pack; falls back to manual selection
- Seed features structured for direct copy-paste into `/aod.discover`
- No infrastructure dependencies; pure methodology/template skill

### Orchestrator Skill Architecture

**Skill file**: `.claude/skills/~aod-run/SKILL.md` (~405 lines, core execution loop)
- Architecture: Segmented prompt with on-demand reference loading (Feature 030)
- Core file contains routing, state machine loop, and stage mapping
- Reference files loaded via Read tool only when needed:

| Reference File | Purpose | Loaded When |
|----------------|---------|-------------|
| `references/governance.md` | Governance gate detection, tiers, rejection handling | Governance cache miss |
| `references/entry-modes.md` | New-idea, issue, resume, status entry handlers | Mode routing |
| `references/dry-run.md` | Read-only preview handler | `--dry-run` flag |
| `references/error-recovery.md` | Corrupted state and lifecycle complete handlers | Error or completion |

- See ADR-002 for the design decision behind prompt segmentation

### Orchestrator State

**State file**: `.aod/run-state.json`
- Format: JSON (managed via `jq`)
- Atomicity: Write-then-rename pattern (`write to .tmp`, then `mv`) for crash safety
- Schema version: `1.0`
- Governance cache: Verdicts stored in `governance_cache` object to eliminate redundant artifact reads (Feature 030)
- Compound helpers: `aod_state_get_multi`, `aod_state_get_loop_context`, `aod_state_get_governance_cache` for incremental reads (Feature 030)
- See ADR-001 for the design decision behind atomic state management
- See ADR-006 for the design decision behind non-fatal error handling in observability operations

---

### Platform Adapter Output Formats (Feature 021)

**Directory**: `adapters/` (5 platform-specific subdirectories)
- Architecture: Hub-and-spoke distribution -- `agents/` is the immutable source of truth; each adapter transforms agents into a platform-native format
- See [ADR-015](../02_ADRs/ADR-015-platform-adapter-hub-and-spoke-distribution.md) for the design decision

| Adapter | Output Format | File Extension | Key Format Characteristics |
|---------|---------------|----------------|---------------------------|
| Claude Code | Markdown with Claude Code frontmatter | `.md` | `name` and `description` fields in YAML frontmatter; tachi metadata in `## Metadata` body section |
| Generic | Self-contained numbered markdown prompts | `.md` | No frontmatter; `{{ARCHITECTURE_INPUT}}` placeholder; sequential numbering (`00-` through `13-`) |
| Cursor | Cursor rule files | `.mdc` | `alwaysApply: true` (orchestrator) or Agent Requested (threat agents); `description` field for activation |
| Copilot | Copilot agent files | `.agent.md` | Size-split pattern for agents >30K chars: compact `.agent.md` + `.github/instructions/*.md` companion |
| GitHub Actions | GitHub Actions workflow | `.yml` | Workflow YAML triggering on architecture file changes; `codeql/upload-sarif@v3` for Code Scanning integration |

**SARIF integration** (GitHub Actions adapter): The CI workflow produces `threats.sarif` (SARIF 2.1.0 format, see Feature 012 / ADR-013) and uploads it to GitHub Code Scanning via the official `codeql/upload-sarif@v3` action. Findings appear as security alerts with CVSS-aligned severity.

**Drift detection**: Each adapter includes a `VERSION` manifest file (YAML format) containing source commit SHA, generation timestamp, and per-agent SHA-256 checksums. Generated by `scripts/generate-adapter-version.sh` (Bash 3.2 compatible).

---

**Template Instructions**: Replace all `{{TEMPLATE_VARIABLES}}` with your actual technology choices. Document the "Why" for each major decision.
