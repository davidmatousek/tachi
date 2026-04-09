# User Stories - tachi

**Last Updated**: 2026-04-08
**Owner**: Product Manager (product-manager)
**Status**: Template - Complete after MVP launch

---

## When to Create This

**Create detailed user stories AFTER your MVP launches.**

Before MVP:
- High-level features in your PRD are sufficient
- Detailed stories emerge from real usage patterns
- You'll waste time on stories for features that change

**Pre-MVP**: Use PRD feature list → build MVP
**Post-MVP**: Break down backlog items into user stories based on actual needs

**Exception**: You can create user stories for complex MVP features that need detailed acceptance criteria.

> **AOD Lifecycle Note**: User stories generated during `/aod.discover` validation
> are stored in **GitHub Issue bodies**, not in this directory. GitHub Issues with
> `stage:*` labels are the source of truth for user stories. This directory serves
> as a reference for story format and prioritization guidance. See
> `docs/product/_backlog/BACKLOG.md` for the auto-generated backlog index.

---

## Overview

User stories describe features from the user's perspective. They follow the format:
> **As a** [persona], **I want** [capability], **so that** [benefit]

---

## User Story Template

```markdown
## US-NNN: [Story Title]

**As a** [persona from target-users.md],
**I want** [capability or action],
**so that** [business value or user benefit].

### Acceptance Criteria
- [ ] Given [context], when [action], then [expected result]
- [ ] Given [context], when [action], then [expected result]

### Related
- **Persona**: [Link to target-users.md]
- **PRD**: [Link to relevant PRD]
- **Priority**: [P0 Critical | P1 High | P2 Medium | P3 Low]

### Notes
[Additional context or constraints]
```

---

## User Story Prioritization

### P0 - Critical (Must Have)
- Blocks core user workflows
- Required for product to function
- Legal or security requirements

### P1 - High (Should Have)
- High user value
- Significant pain point resolution
- Competitive differentiation

### P2 - Medium (Nice to Have)
- Moderate user value
- Quality of life improvements
- Secondary workflows

### P3 - Low (Future)
- Low user value
- Edge cases
- Deferred for later phases

---

## Integration with PRDs

Each PRD should include relevant user stories:
- PRD functional requirements map to user stories
- User story acceptance criteria become PRD requirements
- User stories validated during spec creation

---

**Template Instructions**: Organize user stories by phase or feature area. Delete this message after creating your first user stories.

---

## Aggregated Feature Stories

> **Auto-populated by `/aod.deliver`**: When a feature is delivered, `/aod.deliver` extracts
> validated user stories from the feature's GitHub Issue body and appends them below under
> a `### Feature NNN: {feature-name}` heading. **GitHub Issues remain the source of truth**
> for user stories — this section provides a consolidated reference across delivered features.

<!-- Stories are appended below this line by /aod.deliver -->

### Feature 089: AOD Lifecycle Documentation Completeness

**PRD**: [089-aod-lifecycle-documentation-completeness](../02_PRD/089-aod-lifecycle-documentation-completeness-2026-03-12.md)
**Delivered**: 2026-03-12 | **PR**: #90 | **Tasks**: 16/16 complete | **Stories**: 7/7 passing

- **US-089-1** (P0): System Design Auto-Scaffolding from Plan - Auto-generate `docs/architecture/01_system_design/README.md` from approved plan.md content
- **US-089-2** (P0): Delivery File Change Validation - Validate that documentation agents produce actual file changes during `/aod.deliver`
- **US-089-3** (P1): User Story Export During Delivery - Extract validated user stories from GitHub Issues and append to `05_User_Stories/README.md`
- **US-089-4** (P1): Vision Placeholder Guard in Define - Warn on unresolved template placeholders in vision files during `/aod.define`
- **US-089-5** (P1): Template Placeholder Resolution in Scaffold - Auto-resolve `tachi` and `2026-03-21` in `docs/` after `/aod.stack scaffold`
- **US-089-6** (P1): Closure Summary Relocation - Write closure summaries to `.aod/closures/` instead of `docs/architecture/`
- **US-089-7** (P2): Quarterly Planning Scaffolds - New `/aod.roadmap` and `/aod.okrs` commands for planning document scaffolding

### Feature 091: Delivery Document Generation

**PRD**: [091-delivery-document-generation](../02_PRD/091-delivery-document-generation-2026-03-13.md)
**Delivered**: 2026-03-13 | **PR**: #92 | **Tasks**: 10/10 complete | **Stories**: 3/3 passing

- **US-091-1** (P0): Automatic Delivery Document Generation - Auto-generate `specs/{NNN}-*/delivery.md` during `/aod.deliver` with all retrospective sections populated
- **US-091-2** (P0): Testing Instructions in Delivery Document - Step-by-step "How to See & Test" section with numbered verification steps mapping to acceptance criteria
- **US-091-3** (P1): Delivery Metrics Persistence - Estimated vs actual duration and variance in a consistent format across all delivery documents

### Feature 093: Relocate Governance Results

**PRD**: [093-relocate-governance-results](../02_PRD/093-relocate-governance-results-2026-03-19.md)
**Delivered**: 2026-03-19 | **PR**: #94 | **Tasks**: 16/16 complete | **Stories**: 2/2 passing

- **US-093-1** (P0): Uninterrupted Governance Reviews - Governance review results written to `.aod/results/` without triggering Claude Code permission prompts during `/aod.define`, `/aod.plan`, and `/aod.build`
- **US-093-2** (P0): Consistent Results Directory Convention - All agent/skill documentation references `.aod/results/` as the canonical results path in `_AGENT_BEST_PRACTICES.md` and `CLAUDE.md`

### Feature 001: Project Skeleton & Interface Contract

**PRD**: [001-project-skeleton-interface-contract](../02_PRD/001-project-skeleton-interface-contract-2026-03-21.md)
**Delivered**: 2026-03-21 | **PR**: #2 | **Tasks**: 33/33 complete | **Stories**: 5/5 passing

- **US-001** (P1): Navigable Repository Structure - All directories (`agents/`, `adapters/`, `templates/`, `examples/`, `docs/`, `schemas/`) have READMEs explaining purpose and conventions
- **US-002** (P1): Interface Contract for Integration - `docs/INTERFACE-CONTRACT.md` with 7 sections covering input formats, invocation protocol, output schema, STRIDE-per-Element normalization, and input sanitization guidance
- **US-003** (P1): Consistent Output Template - `templates/tachi/output-schemas/threats.md` canonical template with all 7 required sections (System Overview, Trust Boundaries, STRIDE Tables, AI Threat Tables, Coverage Matrix, Risk Summary, Recommended Actions)
- **US-004** (P2): Machine-Readable Schemas - `schemas/finding.yaml`, `schemas/input.yaml`, `schemas/output.yaml` defining IR, input validation, and output validation schemas
- **US-005** (P2): Example Inputs for Validation - 3 example threat models (`examples/ascii-web-api/`, `examples/mermaid-agentic-app/`, `examples/free-text-microservice/`) covering ASCII, Mermaid, and free-text input formats

### Feature 003: Orchestrator Agent

**PRD**: [003-orchestrator-agent](../02_PRD/003-orchestrator-agent-2026-03-21.md)
**Delivered**: 2026-03-21 | **PR**: #4 | **Tasks**: 35/35 complete | **Stories**: 6/6 passing

- **US-003-1** (P1): Parse Architecture into Component Inventory - Orchestrator parses any of 5 supported input formats (ASCII, free-text, Mermaid, PlantUML, C4), classifies components as DFD element types, identifies trust boundaries, and produces a structured System Overview
- **US-003-2** (P1): Dispatch to Correct Threat Agents - Dispatches each component to correct STRIDE and AI agents based on DFD element type (STRIDE-per-Element) and AI keyword matching, with full architecture context sent to each agent
- **US-003-3** (P1): Assemble Findings into Structured Threat Model - Collects agent findings, validates risk levels against OWASP 3x3 matrix, assembles 8 tables (6 STRIDE + 2 AI), generates coverage matrix, risk summary, and recommended actions into a complete threats.md
- **US-003-4** (P2): Handle Errors Gracefully - Returns correct error codes (UNSUPPORTED_FORMAT, NO_COMPONENTS, INVALID_FORMAT_VALUE) with actionable messages, defaults ambiguous classifications to Process, and flags non-conforming agent findings for review
- **US-003-5** (P2): Support Both Dispatch Modes - Documents both parallel (concurrent agent framework) and sequential (one-at-a-time) dispatch protocols for platform-neutral operation
- **US-003-6** (P2): Enforce Input Sanitization Boundary - Treats architecture input as data to be parsed (not instructions to follow), with clear separation between orchestrator instructions and user-provided content

### Feature 005: STRIDE Threat Agents

**PRD**: [005-stride-threat-agents](../02_PRD/005-stride-threat-agents-2026-03-21.md)
**Delivered**: 2026-03-22 | **PR**: #6 | **Tasks**: 41/41 complete | **Stories**: 4/4 passing

- **US-005-1** (P0): Spoofing and Tampering Agents - Spoofing agent examines authentication mechanisms and produces S-prefixed findings; Tampering agent examines input validation and data integrity and produces T-prefixed findings, both referencing named components from input
- **US-005-2** (P0): Repudiation and Information Disclosure Agents - Repudiation agent examines logging and audit trail gaps with R-prefixed findings; Information Disclosure agent examines data classification and encryption with I-prefixed findings, with concrete mitigations tied to system technology stack
- **US-005-3** (P0): Denial of Service and Privilege Escalation Agents - DoS agent examines rate limiting and resource quotas with D-prefixed findings; Privilege Escalation agent examines RBAC/ABAC and permission boundaries with E-prefixed findings, following STRIDE-per-Element targeting
- **US-005-4** (P0): Consistent Table Format Output - All 6 agents produce findings conforming to schemas/finding.yaml with correct ID prefixes, component references, risk levels computed via OWASP 3x3 matrix, and framework-grounded references

### Feature 010: Deduplication & Risk Rating

**PRD**: [010-deduplication-risk-rating](../02_PRD/010-deduplication-risk-rating-2026-03-22.md)
**Delivered**: 2026-03-22 | **PR**: #11 | **Tasks**: 24/24 complete | **Stories**: 3/3 passing

- **US-010-1** (P0): Cross-Agent Finding Correlation - When multiple agents flag the same component for related threats, correlated findings appear in Section 4a with all agent perspectives grouped under CG-N IDs, using 5 deterministic correlation rules (STRIDE-to-AI category pairs)
- **US-010-2** (P0): Deduplicated Risk Summary and Coverage Matrix - Coverage matrix and risk summary reflect unique threats (deduplicated counts) rather than inflated raw counts, with three-state cell model (count, "---" for analyzed-but-clean, "n/a" for not-applicable) and deduplication footnote
- **US-010-3** (P1): Risk Calibration Documentation - OWASP 3x3 risk matrix documented in the Risk Summary section for reader verification of risk ratings, with all 9 likelihood x impact combinations visible

### Feature 012: SARIF Output Generation

**PRD**: [012-sarif-output-generation](../02_PRD/012-sarif-output-generation-2026-03-22.md)
**Delivered**: 2026-03-22 | **PR**: #13 | **Tasks**: 20/20 complete | **Stories**: 4/4 passing

- **US-012-1** (P0): Export Threat Findings as SARIF 2.1.0 - Orchestrator produces a `threats.sarif` file alongside `threats.md` during Phase 4 (Assess) that validates against the SARIF 2.1.0 JSON schema, with all findings mapped to SARIF results including severity levels, rule definitions, and OWASP/CWE references
- **US-012-2** (P1): Correlated Findings in SARIF - Correlation groups from F-010 deduplication are represented in SARIF using `relatedLocations` to link primary findings to correlated peers, with `partialFingerprints.correlationGroup` preserving group identity
- **US-012-3** (P1): Architecture Component Navigation in SARIF Viewers - SARIF results include both physical locations (input file URI) and logical locations (component name, trust zone path, DFD element type) for component-level navigation in GitHub Code Scanning and other SARIF viewers
- **US-012-4** (P1): Stable Finding Tracking Across Runs - Deterministic `partialFingerprints` using component+category hashing enables GitHub Code Scanning to track findings as persistent alerts across runs without creating duplicates

### Feature 015: Threat Report Agent & Attack Trees

**PRD**: [015-threat-report-agent-attack-trees](../02_PRD/015-threat-report-agent-attack-trees-2026-03-23.md)
**Delivered**: 2026-03-23 | **PR**: #16 | **Tasks**: 29/29 complete | **Stories**: 4/4 passing

- **US-015-1** (P1): Narrative Threat Report for Management - Report agent transforms structured threats.md into a narrative report with executive summary, cross-cutting theme identification, and compliance relevance notes comprehensible by non-technical audiences
- **US-015-2** (P1): Mermaid Attack Trees for Critical/High Findings - Mermaid flowchart TD attack trees generated for every Critical and High finding using Schneier methodology (AND/OR gates, root goals, sub-goals, leaf actions), embedded inline in threat-report.md and saved as standalone files in attack-trees/
- **US-015-3** (P2): Remediation Roadmap with Prioritization - Prioritized remediation roadmap listing all mitigations ordered by risk level (Critical first) with effort estimates (low/medium/high) and dependency notes, directly convertible to development tasks
- **US-015-4** (P1): Orchestrator Integration - Report agent integrated into orchestrator pipeline as Phase 5 (Report) running after Phase 4 (Assess), producing threat-report.md and attack-trees/ alongside existing threats.md and threats.sarif outputs

### Feature 018: Threat Infographic Agent

**PRD**: [018-threat-infographic-agent](../02_PRD/018-threat-infographic-agent-2026-03-23.md)
**Delivered**: 2026-03-23 | **PR**: #19 | **Tasks**: 18/18 complete | **Stories**: 4/4 passing

- **US-018-1** (P0): Visual Threat Infographic Specification - Infographic agent transforms structured threats.md into a visual risk specification (threat-infographic-spec.md) with risk distribution, coverage heat map data, top critical findings summary, and CVSS color palette for executive communication
- **US-018-2** (P0): Automated Image Generation via Gemini API - When Gemini API is available, the agent produces a presentation-ready threat-infographic.jpg from the infographic specification; when unavailable, the spec is saved as a standalone markdown document for manual rendering
- **US-018-3** (P0): Optional and Configurable Infographic Generation - Infographic generation is opt-out via orchestrator configuration, ensuring all tachi features remain fully functional without Gemini API access
- **US-018-4** (P0): Pipeline Integration as Phase 6 - Infographic agent integrated into orchestrator pipeline as Phase 6 (Infographic) running after Phase 5 (Report), with output validation and opt-out support

### Feature 021: Platform Adapters

**PRD**: [021-platform-adapters](../02_PRD/021-platform-adapters-2026-03-23.md)
**Delivered**: 2026-03-23 | **PR**: #22 | **Tasks**: 40/40 complete | **Stories**: 5/5 passing

- **US-021-1** (P0): Claude Code Adapter - Claude Code adapter maps orchestrator + 13 threat agents into `.claude/agents/tachi/` format with parallel dispatch via Agent tool and single `cp -r` installation
- **US-021-2a** (P1): Cursor Adapter - Cursor adapter maps agents to `.cursor/rules/` format with full prompt content preserved and platform-specific conventions followed
- **US-021-2b** (P1): Copilot Adapter - Copilot adapter maps agents to `.github/copilot/` format with full prompt content preserved and platform-specific conventions followed
- **US-021-3** (P1): GitHub Actions Adapter - GitHub Actions workflow triggers on architecture file changes, invokes agents via LLM API, generates `threats.md` and `threats.sarif`, and uploads SARIF to GitHub Code Scanning
- **US-021-4** (P0): Generic Adapter - Generic adapter provides standalone prompt files with sequential (chat UI) and programmatic (LLM API) invocation instructions requiring no platform-specific tooling

### Feature 024: Example Threat Models

**PRD**: [024-example-threat-models](../02_PRD/024-example-threat-models-2026-03-23.md)
**Delivered**: 2026-03-23 | **PR**: #25 | **Tasks**: 50/50 complete | **Stories**: 3/3 passing

- **US-024-1** (P1): Web Application Example - As a new user, I want a web application example, so that I can see what Tachi produces for a traditional architecture before running it on my own system
- **US-024-2** (P1): Agentic Application Example - As an AI developer, I want an agentic application example, so that I can see how the +AI agents add value beyond standard STRIDE
- **US-024-3** (P1): Microservices Example - As a platform engineer, I want a microservices example, so that I can see how Tachi handles complex multi-service architectures with many trust boundaries

### Feature 029: Agent Refactoring — Right-Size

**PRD**: [029-agent-refactoring-right-size](../02_PRD/029-agent-refactoring-right-size-2026-03-25.md)
**Delivered**: 2026-03-25 | **PR**: #30 | **Tasks**: 27/27 complete | **Stories**: 4/4 passing

- **US-029-1** (P0): Orchestrator Right-Sizing - Orchestrator reduced to ~1,100-1,200 lines (from 2,085) with SARIF generation spec, validation checklist, and error templates extracted to on-demand reference documents
- **US-029-2** (P0): Report Agent Right-Sizing - Threat-report agent reduced to ~300-400 lines (from 801) with output templates and verbose examples extracted to reference documents
- **US-029-3** (P0): Infographic Agent Right-Sizing - Threat-infographic agent reduced to ~300-400 lines (from 592) with Gemini API specification and error handling extracted to reference documents
- **US-029-4** (P0): Zero Regression on Threat Agents - All 11 STRIDE/AI threat agents byte-identical before and after refactoring, SARIF 2.1.0 validated, output structure equivalent on example architecture

### Feature 035: Quantitative Risk Scoring

**PRD**: [035-quantitative-risk-scoring](../02_PRD/035-quantitative-risk-scoring-2026-03-27.md)
**Delivered**: 2026-03-27 | **PR**: #37 | **Tasks**: 29/29 complete | **Stories**: 4/4 passing

- **US-035-1** (P0): Quantitative Threat Scoring - As a security engineer, each threat scored with CVSS base + exploitability + scalability + reachability, producing composite score (0.0–10.0) with dimensional breakdown for quantitative remediation prioritization
- **US-035-2** (P0): Risk Governance Fields - As a security manager, risk governance fields (owner, SLA, disposition, review date) attached to each scored threat for remediation tracking and risk acceptance decisions
- **US-035-3** (P0): Dual Output Formats - As a security manager, scored output in both human-readable (risk-scores.md) and machine-readable (risk-scores.sarif) formats for reporting and GRC tooling integration
- **US-035-4** (P1): Reachability-Aware Scoring - As an architect, reachability analysis accounts for trust boundaries from architecture diagrams, scoring internet-facing components higher than well-protected internal components

### Feature 036: Compensating Controls Analysis

**PRD**: [036-compensating-controls](../02_PRD/036-compensating-controls-2026-03-27.md)
**Delivered**: 2026-03-28 | **PR**: #40 | **Tasks**: 21/21 complete | **Stories**: 5/5 passing

- **US-036-1** (P0): Codebase Control Detection - As a developer, scan codebase for existing controls that address identified threats, classifying each as Control Found (with file:line evidence), Partial Control, or No Control Found
- **US-036-2** (P0): Compensating Control Recommendations - As a security engineer, actionable compensating control recommendations for each unmitigated threat, prioritized by risk score, with implementation guidance and effort estimates (Low/Medium/High)
- **US-036-3** (P0): Coverage Matrix - As a security manager, coverage matrix showing control status across all threats with summary statistics (% covered, % partial, % unmitigated) for at-a-glance security posture assessment
- **US-036-4** (P0): Residual Risk Calculation - As a security manager, residual risk calculated for each threat accounting for existing controls, with total inherent vs. total residual risk summary
- **US-036-5** (P0): Control Effectiveness Assessment - As an architect, control effectiveness assessed beyond mere existence — evaluating whether controls are adequate or need hardening

### Feature 039: Standalone /tachi.infographic Command

**PRD**: [039-standalone-infographic-command](../02_PRD/039-standalone-infographic-command-2026-03-28.md)
**Delivered**: 2026-03-28 | **PR**: #42 | **Tasks**: 30/30 complete | **Stories**: 5/5 passing

- **US-039-1** (P0): Auto-Select Richest Data Source - Run `/tachi.infographic` and have it automatically choose the best available data source (`risk-scores.md` preferred over `threats.md`) for the most accurate visual risk picture without remembering which file to pass
- **US-039-2** (P0): Explicit Data Source Override - Pass an explicit file path to `/tachi.infographic` to control exactly which data is visualized, regardless of what files exist in the directory
- **US-039-3** (P0): Template Selection - Select which template(s) to generate (`--template baseball-card|system-architecture|all`) to produce exactly the output needed
- **US-039-4** (P1): Regenerate After Enrichment - Regenerate infographics after running `/tachi.compensating-controls` or `/tachi.risk-score` to reflect quantitative composite scores and residual risk rather than inherent risk
- **US-039-5** (P0): Pipeline Cleanup - `/tachi.threat-model` pipeline produces phases 1-5 only (Phase 6 removed), with all platform adapter documentation updated to reflect the 5-phase pipeline

### Feature 048: Infographic Tiered Pipeline Auto-Detection & Residual Risk

**PRD**: [048-infographic-tiered-detection-residual-risk](../02_PRD/048-infographic-tiered-detection-residual-risk-2026-03-28.md)
**Delivered**: 2026-03-28 | **PR**: #49 | **Tasks**: 27/27 complete | **Stories**: 3/3 passing

- **US-048-1** (P0): Tiered Auto-Detection with Residual Risk - Auto-detect `compensating-controls.md` as the richest data source in a 3-tier hierarchy (compensating-controls.md > risk-scores.md > threats.md), extracting residual risk scores from the Coverage Matrix for infographics that reflect actual security posture after existing defenses
- **US-048-2** (P0): Enhancement Tips at Each Pipeline Tier - Display progressive enhancement tips at each detection tier informing users which pipeline command would upgrade their visualization to the next tier, with tips suppressed when an explicit file path is provided
- **US-048-3** (P1): Risk Labels and Template Adaptations - Distinguish risk labels across data sources (Residual Risk / Inherent Risk / Severity) in both baseball-card and system-architecture templates, with residual severity distribution and risk reduction percentage in the baseball-card summary zone

### Feature 045: End-to-End tachi Instruction Manual

**PRD**: [045-instruction-manual](../02_PRD/045-instruction-manual-2026-03-28.md)
**Delivered**: 2026-03-28 | **PR**: #47 | **Tasks**: 31/31 complete | **Stories**: 3/3 passing

- **US-045-1** (P0): Complete Workflow Guide - Step-by-step instruction manual walking users through the complete 4-command workflow (`/tachi.threat-model` -> `/tachi.risk-score` -> `/tachi.compensating-controls` -> `/tachi.infographic`) from architecture description to visual infographics, producing all 12+ output artifacts
- **US-045-2** (P0): Output Interpretation - Each command's output explained with annotated examples covering all 7 threats.md sections plus Section 4a, 4 risk scoring dimensions, residual risk calculation, and missing control recommendations
- **US-045-3** (P0): Quick Start - Quick Start section at the top of the guide gets a new user from zero to first threat model in 5 steps under 5 minutes, with copy-pasteable commands and clear pointers to comprehensive guide sections

### Feature 053: Risk Reduction Funnel

**PRD**: [053-risk-reduction-funnel](../02_PRD/053-risk-reduction-funnel-2026-03-28.md)
**Delivered**: 2026-03-28 | **PR**: #56 | **Tasks**: 24/24 complete | **Stories**: 4/4 passing

- **US-053-1** (P0): Full Pipeline Funnel (4 Tiers) - Run `/tachi.infographic --template risk-funnel` with `compensating-controls.md` as data source to render a 4-tier funnel showing threats identified, inherent risk scored, controls applied, and residual risk with progressively narrowing widths
- **US-053-2** (P0): Partial Pipeline Funnel (3 Tiers) - Run `/tachi.infographic --template risk-funnel` with `risk-scores.md` to render 3 solid tiers plus a ghost tier with CTA to run `/tachi.compensating-controls` for the full funnel
- **US-053-3** (P0): Minimal Pipeline Funnel (1 Tier) - Run `/tachi.infographic --template risk-funnel` with only `threats.md` to render a single wide tier with 3 grayed-out ghost tiers showing pipeline commands needed to unlock them
- **US-053-4** (P1): Funnel Metrics Sidebar - Key metrics (total threats, risk reduction %, control coverage %) displayed alongside the funnel, adapting to the available tier mode

### Feature 054: Security Assessment PDF Booklet

**PRD**: [054-security-assessment-pdf-booklet](../02_PRD/054-security-assessment-pdf-booklet-2026-03-28.md)
**Delivered**: 2026-03-28 | **PR**: #58 | **Tasks**: 34/34 complete | **Stories**: 4/4 passing

- **US-054-1** (P0): Single PDF for Board Distribution - As a CISO, a single PDF combining all security analysis visuals and findings, so I can distribute one document to the board instead of multiple files
- **US-054-2** (P0): Structured Audit Evidence - As a compliance officer, a structured security assessment report with cover page, executive summary, and detailed findings, so I can include it in audit evidence packages
- **US-054-3** (P1): Professional Client Deliverable - As a security consultant, generate a professional, branded PDF deliverable from tachi's output, so I can deliver polished reports to clients
- **US-054-4** (P1): Auto-Assembly from Available Artifacts - As a developer, the PDF auto-assembles from whatever artifacts exist in my security output directory, so I don't need to manually curate pages

### Feature 060: Professional PDF Security Assessment Report with tachi Branding

**PRD**: [060-professional-pdf-security-report-branding](../02_PRD/060-professional-pdf-security-report-branding-2026-03-29.md)
**Delivered**: 2026-03-29 | **PR**: #61 | **Tasks**: 45/45 complete | **Stories**: 6/6 passing

- **US-060-1** (P0): Branded Cover Page and Running Headers - As a security consultant, the tachi logo appears on the cover page and consistent branded headers on every text page, conveying professional quality without post-generation reformatting
- **US-060-2** (P0): Disclaimer and Table of Contents - As a compliance officer, a legal disclaimer on page 2 sets expectations about automated assessment methodology, followed by a table of contents enabling quick navigation to any section
- **US-060-3** (P0): Risk Methodology and Assessment Scope Pages - As a CISO, the methodology page explains how threats were identified and scored, and the scope page shows exactly which components, data flows, and trust boundaries were assessed
- **US-060-4** (P1): Modular Theme Architecture - As a developer extending tachi, a single `theme.typ` file change for colors and logo path propagates to every page automatically via centralized token system
- **US-060-5** (P1): Enhanced Findings Detail with Severity Visualization - As a security engineer, individual finding cards with severity color-coding, component badges, and structured recommendation sections replace flat table rows
- **US-060-6** (P2): Remediation Roadmap with Effort Estimates - As a project manager, the remediation roadmap groups recommendations by effort tier (Quick Wins, Medium, High) with estimated implementation effort for sprint planning

### Feature 067: Deterministic Report Data Extraction

**PRD**: [067-deterministic-report-data-extraction](../02_PRD/067-deterministic-report-data-extraction-2026-03-30.md)
**Delivered**: 2026-03-30 | **PR**: #68 | **Tasks**: 32/32 complete | **Stories**: 6/6 passing

- **US-067-1** (P0): Reproducible Report Generation - Running `/tachi.security-report` on identical input artifacts produces byte-identical `report-data.typ` and PDF output every time, enabling compliance and executive communication use cases
- **US-067-2** (P0): Validated Severity Counts - Parsing script validates internal consistency (critical + high + medium + low == total) across all three severity source tiers (compensating-controls.md, risk-scores.md, threats.md)
- **US-067-3** (P0): Deterministic Scope Data Extraction - Script extracts exact component and data flow counts from threats.md Section 1, matching source file counts every time
- **US-067-4** (P0): Agent Prompt Update - Report-assembler agent updated to invoke deterministic Python script instead of LLM-based inline parsing for Steps 2-3
- **US-067-5** (P1): Consistent Recommendation Formatting - Finding recommendations preserved verbatim from source artifacts with uniform formatting across all severity levels
- **US-067-6** (P1): Testing Against Example Datasets - Script validated against both OpenClaw and agentic-app example datasets for regression coverage

### Feature 071: Deterministic Infographic Extraction

**PRD**: [071-deterministic-infographic-extraction](../02_PRD/071-deterministic-infographic-extraction-2026-03-30.md)
**Delivered**: 2026-03-30 | **PR**: #72 | **Tasks**: 46/46 complete | **Stories**: 4/4 passing

- **US-071-1** (P0): Deterministic Baseball Card Specification - Running `/tachi.infographic --template baseball-card` on identical input produces byte-identical spec files with consistent severity counts, heat map values, and top findings
- **US-071-2** (P0): Deterministic System Architecture Specification - Running `/tachi.infographic --template system-architecture` on identical input produces byte-identical spec files with consistent component annotations, data flow severity coloring, and finding overlays
- **US-071-3** (P0): Deterministic Risk Funnel Specification - Running `/tachi.infographic --template risk-funnel` on identical input produces byte-identical spec files with consistent tier counts and reduction percentages
- **US-071-4** (P0): Cross-Output Consistency - Security report and infographic severity counts match exactly when generated from the same threat model artifacts, enabling side-by-side use in briefings

### Feature 075: Tachi Agent Best Practices

**PRD**: [075-tachi-agent-best-practices](../02_PRD/075-tachi-agent-best-practices-2026-03-31.md)
**Delivered**: 2026-03-31 | **PR**: #76 | **Tasks**: 29/29 complete | **Stories**: 4/4 passing

- **US-075-1** (P1): Skill Extraction for Methodology Agents - Domain knowledge (scoring schemas, detection patterns, dispatch rules) extracted from orchestrator, risk-scorer, and control-analyzer into on-demand skill files, bringing all three methodology agents to or below the 1,000-line cap
- **US-075-2** (P2): Claude 4.6 Tone Audit - All 17 tachi agents audited for aggressive emphasis patterns, tool restrictions added to frontmatter, description fields reviewed for delegation routing quality, and data-top ordering verified
- **US-075-3** (P2): Threat-Report Trim - Threat-report agent trimmed to at or below the 800-line Report tier cap
- **US-075-4** (P3): Best Practices Guide and Compliance Table - Shared _TACHI_AGENT_BEST_PRACTICES.md created with tier definitions (Leaf 300, Report 800, Methodology 1,000), extraction checklist, 8-criterion quality checklist, and post-refactor compliance table confirming all agents within caps

### Feature 074: Baseline-Aware Pipeline

**PRD**: [074-baseline-aware-pipeline](../02_PRD/074-baseline-aware-pipeline-2026-03-31.md)
**Delivered**: 2026-04-01 | **PR**: #79 | **Tasks**: 36/36 complete | **Stories**: 6/6 passing

- **US-074-1** (P0): Stable Re-Scan - Re-running the pipeline on an unchanged codebase produces identical finding IDs, risk scores, and finding counts with zero drift and no phantom findings
- **US-074-2** (P0): Remediation Verification - After fixing a vulnerability, the targeted finding is marked `[RESOLVED]` with its original ID preserved for audit traceability; partial fixes produce `[UPDATED]` with revised scores
- **US-074-3** (P0): New Threat Discovery - Fresh discovery phase finds genuinely new threats alongside carried-forward findings without anchoring bias, with category-bounded CVSS scoring (+/- 1.0 from schema defaults)
- **US-074-4** (P1): Delta Annotations - Every finding annotated with exactly one lifecycle status (`[NEW]`, `[UNCHANGED]`, `[UPDATED]`, `[RESOLVED]`) enabling trend reporting and board-level communication
- **US-074-5** (P1): Coverage Assurance - Coverage gate verifies minimum required threat categories are evaluated per component type, triggering targeted re-analysis for missing categories to prevent blind spots from LLM non-determinism
- **US-074-6** (P1): Remediation SLA Tracking - Stable finding IDs and governance field preservation (risk_owner, remediation_sla) across assessment cycles enable time-to-remediate computation for compliance reporting

### Feature 078: Agent Context Optimization

**PRD**: [078-agent-context-optimization](../02_PRD/078-agent-context-optimization-2026-04-01.md)
**Delivered**: 2026-04-02 | **PR**: #81 | **Tasks**: 58/58 complete | **Stories**: 5/5 passing

- **US-078-1** (P0): Methodology Agent Restructuring - Orchestrator, risk-scorer, and control-analyzer restructured from monolithic prompts to lean agent definitions with on-demand skill references, reducing prompt sizes by 40-60%
- **US-078-2** (P0): Report Agent Restructuring - Report-assembler, threat-report, and threat-infographic agents restructured to lean definitions with extracted skill reference files for brand assets, Typst contracts, and template specifications
- **US-078-3** (P1): Model Field Assignment - All 17 tachi agent definitions updated with explicit model fields for optimal delegation routing across agent tiers (Leaf, Report, Methodology)
- **US-078-4** (P1): Best Practices Documentation Update - Shared _TACHI_AGENT_BEST_PRACTICES.md updated with restructuring patterns, skill reference conventions, and compliance verification for all 17 agents
- **US-078-5** (P0): Zero Regression Validation - All restructured agents validated against example threat models with equivalent output structure, severity counts, and SARIF compliance preserved

### Feature 084: MAESTRO Layer Mapping

**PRD**: [084-maestro-layer-mapping](../02_PRD/084-maestro-layer-mapping-2026-04-07.md)
**Delivered**: 2026-04-08 | **PR**: #92 | **Tasks**: 22/22 complete | **Stories**: 4/4 passing

- **US-084-1** (P0): Layer-Tagged Threat Findings - Each finding in STRIDE and AI threat tables includes a MAESTRO Layer column, derived from component classification in Phase 1 with "Unclassified" default for unmatched components
- **US-084-2** (P0): Phase 1 Component Classification - Orchestrator classifies each component by MAESTRO layer using keyword matching against name, description, and DFD type during Phase 1 (Scope), with dispatch table showing MAESTRO Layer column
- **US-084-3** (P0): SARIF Layer Tags - SARIF results include `maestro-layer:{layer-name}` in properties.tags array and `maestro-layer` key in properties for security tooling filtering
- **US-084-4** (P1): Layer-Based Risk Summary - Risk summary in threats.md includes "Risk by MAESTRO Layer" subsection showing finding count and highest severity per layer, omitting layers with zero findings

### Feature 104: Downstream Baseline Propagation

**PRD**: [104-downstream-baseline-propagation](../02_PRD/104-downstream-baseline-propagation-2026-04-08.md)
**Delivered**: 2026-04-08 | **PR**: #107 | **Tasks**: 18/18 complete | **Stories**: 4/4 passing

- **US-104-1** (P0): Delta-Aware Threat Report - Threat-report agent parses delta_status from findings, groups by lifecycle status (new, unchanged, updated, resolved), excludes RESOLVED from attack trees, carries forward UNCHANGED attack trees, and produces Delta Summary section
- **US-104-2** (P0): Delta-Aware Infographics - Infographic extraction script excludes RESOLVED findings from severity distribution counts, includes delta breakdown (new vs. unchanged vs. updated), and passes delta context to Gemini prompts
- **US-104-3** (P1): Delta-Aware PDF Security Report - Report extraction script includes delta_status per finding in Typst data, RESOLVED findings appear in separate section, NEW findings visually badged in findings table
- **US-104-4** (P0): Output Schema Delta Support - Standardized delta structures in threats.md Section 8 (Delta Summary) and threat-report.md output schema templates for consistent downstream parsing

### Feature 112: Attack Path Pages in Security Report PDF

**PRD**: [112-attack-path-pages-in-pdf](../02_PRD/112-attack-path-pages-in-pdf-2026-04-09.md)
**Delivered**: 2026-04-09 | **PR**: #115 | **Tasks**: 18/18 complete | **Stories**: 4/4 passing

- **US-112-1** (P1): View Attack Path Page in PDF Report - Each Critical and High finding with an attack tree gets a dedicated page in the PDF with rendered diagram image, narrative explanation, and remediation steps; reports without attack trees generate without errors
- **US-112-2** (P1): Attack Path Page Ordering - Attack path pages ordered by severity (Critical first, then High) and by finding ID within the same severity for focused reading
- **US-112-3** (P1): Mermaid Diagram Rendering - Mermaid attack tree code blocks rendered to PNG images at 2x resolution via mmdc; graceful fallback to preformatted text when rendering tool is unavailable
- **US-112-4** (P2): Section Header and TOC Integration - Attack path section introduced by "Attack Path Analysis" divider page and included in table of contents for clear navigation
