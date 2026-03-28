# Technology Stack - tachi

**Last Updated**: 2026-03-27
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

**CI/CD**: {{CICD_PLATFORM}}
- Examples: GitHub Actions, GitLab CI, CircleCI

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
| `schemas/finding.yaml` | Intermediate Representation (IR) -- data contract between agents and templates; optional `scored_finding` extension for quantitative risk scoring (Feature 035) | 10 fields: id, category, component, threat, likelihood, impact, risk_level, mitigation, references, dfd_element_type; see `schemas/risk-scoring.yaml` for extension fields |
| `schemas/input.yaml` | Input validation -- accepted architecture description formats | 5 formats: ASCII, free-text, Mermaid, PlantUML, C4; includes recognition patterns and `format: auto` heuristic detection |
| `schemas/output.yaml` | Output structure -- sections required in generated threat model; includes SARIF severity mapping (Feature 012) | 7 sections + Section 4a: System Overview, Trust Boundaries, STRIDE Tables, AI Threat Tables, **Correlated Findings (4a)**, Coverage Matrix, Risk Summary, Recommended Actions (Feature 010); SARIF severity mapping comment block with CVSS alignment (Feature 012) |
| `schemas/report.yaml` | Report output structure -- sections required in generated threat report (Feature 015) | 7 sections: Executive Summary, Architecture Overview, Threat Analysis, Cross-Cutting Themes, Attack Trees, Remediation Roadmap, Appendix: Finding Reference; attack tree file naming convention `{finding-id}-attack-tree.md`; finding reference completeness rules |
| `schemas/infographic.yaml` | Infographic output structure -- sections required in generated threat infographic specification (Feature 018) | 6 sections: Metadata, Risk Distribution, Coverage Heat Map, Top Critical Findings, Architecture Threat Overlay, Visual Design Directives; CVSS color palette (#DC2626/#F97316/#EAB308/#4169E1/#6B7280); 16:9 landscape layout with three-zone structure |
| `schemas/risk-scoring.yaml` | Scored finding schema extending `finding.yaml` with quantitative risk scoring (Feature 035) | 4 scoring dimensions (cvss_base, exploitability, scalability, reachability), composite weights (0.35/0.30/0.15/0.20), 8 category CVSS defaults, 4 severity bands with SLA/disposition mapping, governance fields (risk_owner, remediation_sla, risk_disposition, review_date) |
| `schemas/compensating-controls.yaml` | Control finding IR extending `risk-scoring.yaml` with compensating control fields (Feature 036) | 10 control categories (8 STRIDE-mapped + 2 AI-specific), effectiveness ratings (Strong/Moderate/Weak/None), residual risk calculation fields, control evidence and gap tracking, coverage matrix dimensions |

**Threat agent prompts**: `agents/` (11 agent prompt files + orchestrator + report agent + infographic agent + risk-scorer agent + control-analyzer agent); distributed to 5 target platforms via `adapters/` hub-and-spoke pattern (Feature 021). Right-sized in Feature 029: orchestrator (2,085->1,273 lines, -39%), report (801->472 lines, -41%), infographic (592->414 lines, -30%) via reference-extraction pattern -- consultation-only content moved to co-located reference files loaded on-demand via Read tool.
| Subdirectory | Count | Scope | Status |
|-------------|-------|-------|--------|
| `agents/stride/` | 6 agents | STRIDE categories: Spoofing, Tampering, Repudiation, Info Disclosure, Denial of Service, Privilege Escalation | Validated end-to-end (Feature 005) |
| `agents/ai/` | 5 agents | AI-specific threats: Prompt Injection, Tool Abuse, Data Poisoning, Model Theft, Agent Autonomy; two-layer keyword dispatch (AG-prefixed agentic, LLM-prefixed LLM categories) | Validated end-to-end (Feature 007) |
| `agents/orchestrator.md` | 1 agent | Central orchestrator implementing OWASP 4-phase workflow (Scope, Determine Threats, Determine Countermeasures, Assess) with Phase 5 (Report) integration, STRIDE-per-Element dispatch, AI keyword dispatch (Feature 003), cross-agent correlation detection with deduplicated coverage matrix and risk summary (Feature 010), SARIF 2.1.0 output generation for GitHub Code Scanning integration (Feature 012), and narrative report dispatch with Mermaid attack trees (Feature 015). Infographic generation extracted to standalone `/infographic` command (Feature 039). Right-sized to 1,273 lines with 3 reference documents (Feature 029) | Complete |
| `agents/threat-report.md` | 1 agent | Report generation agent transforming `threats.md` into narrative threat report with executive summary, Mermaid attack trees for Critical/High findings, prioritized remediation roadmap with effort estimates, and complete finding traceability (Feature 015). Right-sized to 472 lines with 1 reference document (Feature 029) | Validated end-to-end (Feature 015) |
| `agents/threat-infographic.md` | 1 agent | Infographic agent transforming `threats.md` into visual infographic specifications and images via Gemini API. Supports multiple templates: Baseball Card (risk summary dashboard) and System Architecture (annotated architecture diagram with attack surface badges). Right-sized to 414 lines with 2 reference documents (Feature 029) | Validated end-to-end (Feature 018) |
| `agents/tachi/risk-scorer.md` | 1 agent | Risk scoring agent applying four-dimensional quantitative assessment (CVSS 3.1 base, exploitability, scalability, reachability) to threat findings with weighted composite calculation, severity band mapping, and governance field assignment. Produces dual output: `risk-scores.md` (human-readable) and `risk-scores.sarif` (machine-readable). Invoked via `/risk-score` command (Feature 035) | Complete |
| `agents/tachi/control-analyzer.md` | 1 agent | Compensating controls analysis agent implementing 6-phase pipeline (parse, discover, detect, classify, recommend, output) to scan target codebases against scored threats. Detects existing security controls across 10 categories (8 STRIDE-mapped + 2 AI-specific), classifies effectiveness, recommends missing controls, calculates residual risk, and produces dual output: `compensating-controls.md` (human-readable) and `compensating-controls.sarif` (machine-readable). Invoked via `/compensating-controls` command (Feature 036) | Complete |

**Agent reference documents** (Feature 029): Consultation-only content extracted from agent prompts into co-located reference files. Agents load references on-demand via Read tool at specific pipeline phases, keeping core prompts focused on always-needed execution logic. Applies the [On-Demand Reference File Segmentation](../03_patterns/README.md#pattern-on-demand-reference-file-segmentation) pattern at the agent level.

| Reference | Agent | Path | Loaded When |
|-----------|-------|------|-------------|
| SARIF Generation | orchestrator, risk-scorer | `adapters/claude-code/agents/references/sarif-generation.md` | Phase 4 completion; risk scoring SARIF generation (Feature 035 addendum: scored SARIF diff specification) |
| Validation Checklist | orchestrator | `adapters/claude-code/agents/references/validation-checklist.md` | Pipeline end |
| Error Templates | orchestrator | `adapters/claude-code/agents/references/error-templates.md` | Error condition |
| Report Templates | threat-report | `adapters/claude-code/agents/references/report-templates.md` | Attack tree generation |
| Gemini API Integration | threat-infographic | `adapters/claude-code/agents/references/infographic-gemini-api.md` | Image generation phase |
| Error Handling | threat-infographic | `adapters/claude-code/agents/references/infographic-error-handling.md` | Error condition |

**Infographic templates** (Feature 029): Template files for multi-template infographic generation, co-located with the portable agent set.

| Template | Path | Purpose |
|----------|------|---------|
| Baseball Card | `.claude/agents/tachi/templates/infographic-baseball-card.md` | Risk summary dashboard with key metrics |
| System Architecture | `.claude/agents/tachi/templates/infographic-system-architecture.md` | Annotated architecture diagram with attack surface badges |

**Portable agent set** (Feature 029, extended Feature 035, Feature 036): `.claude/agents/tachi/` contains the complete threat agent set (11 threat agents + orchestrator + report + infographic + risk-scorer + control-analyzer + 2 infographic templates) in Claude Code native format. This set is the Claude Code platform adapter output, installed at `.claude/agents/tachi/` for direct invocation. The portable set mirrors the `adapters/claude-code/agents/` content with paths adjusted for the installation depth.

**STRIDE agent capabilities** (Feature 005):
- Each agent enforces STRIDE-per-Element matrix targeting (DFD element type filtering)
- AI-specific threat patterns included per agent (e.g., credential theft of API keys for LLM services, model poisoning via tampered training data)
- OWASP API Security 2023 cross-references (API1-API10) alongside OWASP Top 10 2021, CWE, and MITRE ATT&CK
- Finding ID convention: S-N (Spoofing), T-N (Tampering), R-N (Repudiation), I-N (Info Disclosure), D-N (DoS), E-N (Privilege Escalation)
- Component-specific findings enforced -- generic/untargeted threats rejected by agent prompts

**Standards**: OWASP 3x3 risk matrix (likelihood x impact), STRIDE-per-Element methodology (DFD element mapping), OWASP API Security 2023 (API1-API10), OWASP Top 10 2021 (A01-A10), OWASP references (ASI-xx, MCP-xx, LLM0x:2025 for AI agents), CWE and MITRE ATT&CK cross-references, SARIF 2.1.0 (OASIS standard for static analysis results interchange, Feature 012), Mermaid `flowchart TD` syntax (attack tree visualization, Feature 015), CVSS severity color palette (infographic visual encoding, Feature 018), CVSS 3.1 base scoring (quantitative risk scoring with full vector string auditability, Feature 035).

**Output templates**:
- `templates/threats.md` -- canonical 7-section + Section 4a threat model template with `schema_version: "1.1"` frontmatter. Section 4a (Correlated Findings) added in Feature 010. Coverage matrix uses three-state cell model (deduplicated count, "---" analyzed-but-clean, "n/a" not-applicable). Risk summary shows deduplicated counts with raw count parenthetical when different.
- `templates/threats.sarif` -- SARIF 2.1.0 reference template for structural documentation (Feature 012). Complete JSON structure with placeholder values demonstrating rule definitions, result mapping, dual locations, relatedLocations for correlated findings, and partialFingerprints for stable tracking.
- `templates/threat-report.md` -- canonical 7-section narrative threat report template with `schema_version: "1.0"` frontmatter (Feature 015). Sections: Executive Summary, Architecture Overview, Threat Analysis (agent-by-agent narrative), Cross-Cutting Themes, Attack Trees (Mermaid `flowchart TD` with inline rendering and standalone file references), Remediation Roadmap (prioritized with effort estimates), Appendix: Finding Reference (complete traceability table). Validated against `schemas/report.yaml`.
- `templates/risk-scores.md` -- scored threat model template with executive summary (highest/average composite, severity distribution), scored threat table (all 4 dimensions + composite + governance per finding), and methodology section documenting scoring weights and severity bands (Feature 035). Validated against `schemas/risk-scoring.yaml`.
- `templates/risk-scores.sarif` -- SARIF 2.1.0 scored output template extending `threats.sarif` structure with per-finding composite scores in `properties` bag, per-rule MAX composite in `security-severity`, and governance fields (Feature 035). Fingerprints preserved from source for GitHub Code Scanning alert supersession.
- `templates/compensating-controls.md` -- compensating controls analysis template with executive summary (control coverage percentage, residual risk), per-finding control inventory (detected controls with effectiveness rating, gaps, recommendations), coverage matrix (10 control categories x components), and residual risk summary (Feature 036). Validated against `schemas/compensating-controls.yaml`.
- `templates/compensating-controls.sarif` -- SARIF 2.1.0 compensating controls output template extending `risk-scores.sarif` structure with control detection results, effectiveness classifications, and residual risk scores in `properties` bag (Feature 036). Fingerprints preserved from source for GitHub Code Scanning alert chain continuity.

**SARIF output** (Feature 012): The orchestrator produces `threats.sarif` alongside `threats.md` during Phase 4 (Assess). SARIF generation maps all finding IR data to SARIF 2.1.0 format with CVSS-aligned severity (Critical=error/9.0, High=error/8.0, Medium=warning/5.0, Low=note/2.0, Note=note/0.1), deterministic fingerprints (SHA-256 of ruleId + component_name) for stable GitHub Code Scanning alert tracking, dual physical/logical locations for component navigation, and optional OWASP/CWE taxonomy references. 8 rule IDs map to the combined STRIDE + AI category set (`tachi/stride/*` and `tachi/ai/*`).

**Report output** (Feature 015): After Phase 4, the orchestrator dispatches Phase 5 (Report, default-on, opt-out via `--skip-report` flag or `report: false` configuration) to the report agent (`agents/threat-report.md`). Phase 5 produces `threat-report.md` (7-section narrative report) and `attack-trees/` (standalone Mermaid `flowchart TD` files, one per Critical/High finding). The report agent receives only `threats.md` as input in a fresh context (context isolation boundary).

**Infographic output** (Feature 018, updated Feature 039): Infographic generation is a standalone `/infographic` command, no longer part of the orchestrator pipeline. The `/infographic` command auto-detects the richest available data source (`risk-scores.md` preferred over `threats.md`), supports explicit file override and template selection (`--template baseball-card|system-architecture|all`). The infographic agent (`agents/threat-infographic.md`) supports dual-path data extraction: when `risk-scores.md` is primary, it reads quantitative composite scores from risk-scores and structural/spatial data from co-located `threats.md`. Produces `threat-infographic-spec.md` (6-section visual risk specification conforming to `schemas/infographic.yaml`) and optionally `threat-infographic.jpg` (presentation-ready image via Google Gemini API, conditional on `GEMINI_API_KEY`). The specification is the primary deliverable; the image is best-effort with graceful degradation on API errors, rate limits, content policy rejections, or missing API key. See [ADR-014](../02_ADRs/ADR-014-gemini-api-optional-image-generation.md) for the external API integration decision.

**Risk scoring output** (Feature 035): The `/risk-score` command invokes the risk-scorer agent (`agents/tachi/risk-scorer.md`) as a standalone post-pipeline step. The risk-scorer parses `threats.md` (canonical) or `threats.sarif` (fallback), applies four-dimensional quantitative scoring per finding (CVSS 3.1 base, exploitability, scalability, reachability), calculates a weighted composite (0.35/0.30/0.15/0.20), maps to severity bands aligned with `output.yaml`, and assigns governance fields (risk_owner, remediation_sla, risk_disposition, review_date). Produces `risk-scores.md` (human-readable scored threat table) and `risk-scores.sarif` (machine-readable, supersedes `threats.sarif` in GitHub Code Scanning via preserved fingerprints). Schema: `schemas/risk-scoring.yaml`. The SARIF generation reference (`adapters/claude-code/agents/references/sarif-generation.md`) documents the structural differences between `threats.sarif` and `risk-scores.sarif`.

**Compensating controls output** (Feature 036): The `/compensating-controls` command invokes the control-analyzer agent (`agents/tachi/control-analyzer.md`) as the third stage of the threat analysis pipeline. The control-analyzer accepts `--target` (codebase path to scan), `--input` (risk-scores.md or risk-scores.sarif), and `--output-dir` flags. It executes a 6-phase pipeline: (1) parse scored threats, (2) discover target codebase structure, (3) detect existing security controls per component using 10 categories (8 STRIDE-mapped: authentication, integrity, audit-logging, data-protection, availability, access-control, input-validation, encryption-in-transit; 2 AI-specific: prompt-safety, agent-guardrails), (4) classify control effectiveness (Strong/Moderate/Weak/None), (5) recommend missing controls and calculate residual risk, (6) output dual-format results. Produces `compensating-controls.md` (human-readable control inventory with coverage matrix) and `compensating-controls.sarif` (machine-readable, supersedes `risk-scores.sarif` in GitHub Code Scanning alert chain). Schema: `schemas/compensating-controls.yaml`.

**Full pipeline output**: `threats.md` + `threats.sarif` (Phase 4) + `threat-report.md` + `attack-trees/*.md` (Phase 5). **Post-pipeline**: `risk-scores.md` + `risk-scores.sarif` (via `/risk-score` command, Feature 035) + `compensating-controls.md` + `compensating-controls.sarif` (via `/compensating-controls` command, Feature 036) + `threat-infographic-spec.md` + `threat-infographic.jpg` (via `/infographic` command, Feature 039; image conditional on Gemini API key).

**Example threat models**: `examples/` contains 3 standardized reference implementations (web-app, agentic-app, microservices) pairing Mermaid architecture diagrams with complete schema v1.1 threat model outputs (Feature 024). See `examples/README.md` for usage instructions and framework mapping.

---

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

### CLI Dependencies

| Tool | Required By | Purpose | Install |
|------|-------------|---------|---------|
| `jq` | `run-state.sh` | JSON parsing and atomic state manipulation | `brew install jq` (macOS) / `apt-get install jq` (Linux) |
| `gh` | `github-lifecycle.sh`, `run-state.sh` (optional), `scripts/init.sh` (optional) | GitHub Issue/label management, Projects board creation during init | `brew install gh` / `gh auth login` |

**Note**: `gh` degrades gracefully -- the orchestrator falls back to artifact-only detection when `gh` is unavailable or unauthenticated. Similarly, `scripts/init.sh` skips GitHub Projects board creation when `gh` is missing, unauthenticated, or lacks the `project` OAuth scope, reporting status in the init summary with remediation guidance.

### External API Dependencies (Optional)

| API | Required By | Purpose | Authentication | Graceful Degradation |
|-----|-------------|---------|----------------|----------------------|
| Google Gemini API (`gemini-3-pro-image-preview`) | `agents/threat-infographic.md` (via `/infographic` command) | Optional image generation for threat infographic visualization | `GEMINI_API_KEY` environment variable | Spec always produced; image skipped if API key missing, rate limited (429), timed out (60s), or content policy rejected. Fallback model: `gemini-3.1-flash-image-preview`. See [ADR-014](../02_ADRs/ADR-014-gemini-api-optional-image-generation.md). |

**Note**: The Gemini API is entirely optional. The `/infographic` command produces the infographic specification (`threat-infographic-spec.md`) regardless of API availability. The specification is self-contained and can be used by a designer to render the infographic manually. Image generation is a best-effort enhancement.

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
