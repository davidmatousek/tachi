# User Stories - tachi

**Last Updated**: 2026-04-29 (Feature 237 delivered — F-7 Mobile Top 10 Coverage Bundle [Tier 2] / five-agent enrichment of `spoofing` + `tampering` + `info-disclosure` + `privilege-escalation` + `repudiation` / fourth execution of Heuristic A enrichment branch after F-3 single-agent / F-5 two-agent / F-6 three-agent / first at four-or-five-agent scope / closes OWASP Mobile Top 10:2024 to 10/10 Covered and completes the OWASP four-framework total at 40/40 Covered — second framework family closure milestone)
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

### Feature 121: Rename Tachi Commands to tachi.* Namespace

**PRD**: [121-rename-tachi-commands-to-namespace](../02_PRD/121-rename-tachi-commands-to-namespace-2026-04-09.md)
**Delivered**: 2026-04-09 | **PR**: #122 | **Tasks**: 72/72 complete | **Stories**: 5/5 passing

- **US-121-1** (P0): Namespace-Prefixed Command Invocation - All 6 tachi pipeline commands (/tachi.threat-model, /tachi.risk-score, /tachi.compensating-controls, /tachi.infographic, /tachi.security-report, /tachi.architecture) invoke correctly under the tachi.* namespace
- **US-121-2** (P1): Command Discovery via Namespace - Typing `/tachi.` in IDE command palette reveals all 6 pipeline commands as completions
- **US-121-3** (P0): Cross-Reference Integrity - Zero references to old unprefixed command names remain across commands, agents, skills, docs, and templates (historical PRDs and specs excluded per immutability policy)
- **US-121-4** (P0): Clean Upgrade Without Duplicate Commands - Install script removes old command files (threat-model.md, risk-score.md, compensating-controls.md, infographic.md, security-report.md) from .claude/commands/ so only tachi.* prefixed commands exist
- **US-121-5** (P1): Migration Guidance for Existing Users - CHANGELOG contains clear old-to-new command name mapping for existing users transitioning to the new namespace

### Feature 136: MAESTRO Canonical Layer Correctness Fix

**PRD**: [136-maestro-canonical-layer-correctness-fix](../02_PRD/136-maestro-canonical-layer-correctness-fix-2026-04-10.md)
**Delivered**: 2026-04-10 | **PR**: #146 | **Tasks**: 45/45 complete | **Stories**: 8/8 passing

- **US-136-1** (P1): Canonical Shared Reference Alignment - Shared MAESTRO reference file (`.claude/skills/tachi-shared/references/maestro-layers-shared.md`) uses canonical CSA seven-layer taxonomy names with correct acronym expansion ("Multi-Agent Environment, Security, Threat, Risk, and Outcome") and keyword set that correctly separates observability (L5), security/compliance (L6), and agent-ecosystem + user-facing components (L7)
- **US-136-2** (P1): Observability Layer Classifies Detective Controls - Components like Audit Logger, behavioral monitoring, and anomaly detection now classify to "L5 — Evaluation and Observability" in threats.md, with a dedicated layer band in the PDF security report MAESTRO Findings section instead of being lost in Unclassified or misrouted to Security
- **US-136-3** (P1): Schema Enum and Downstream Migration - `schemas/finding.yaml` `maestro_layer` enum contains canonical values ("L5 — Evaluation and Observability", "L6 — Security and Compliance", "L7 — Agent Ecosystem"), schema version bumped 1.2 → 1.3, and CHANGELOG documents the old → new value mapping, acronym correction, and migration guidance for downstream adopters
- **US-136-4** (P1): Regenerated Example Outputs - All six example architectures (`examples/*`) regenerated with canonical layer names throughout threats.md, threat-report.md, infographic specs, and security-report.pdf.baseline; zero occurrences of old layer names ("L5 — Security", "L6 — Agent Ecosystem", "L6 — Integration Services", "L7 — User Interface") remain
- **US-136-5** (P1): Typst Template Canonical Alignment - `templates/tachi/security-report/maestro-findings.typ` fallback dictionary corrected to use canonical layer names (resolving pre-existing three-way divergence where template said "Integration Services" for L6); PDF security report MAESTRO Findings page now displays canonical labels for all seven layer bands
- **US-136-6** (P2): Pipeline Documentation and ADR Updates - Dispatch rules, finding format shared reference, README layer table, and ADR-020 (with Feature 136 revision note) all use canonical layer names; historical PRDs 084 and 091 preserved unchanged per immutability policy
- **US-136-7** (P2): Wave 0 Pre-Edit Discovery Report - Committed `specs/136-maestro-canonical-layer/discovery-report.md` documenting pre-edit grep sweep results with file-by-file match inventory, providing audit trail that every hardcoded layer name reference was found and addressed before editing began
- **US-136-8** (P1): Backward Compatibility Validation Gate - Five non-agentic-app example baselines (web-app, microservices, ascii-web-api, mermaid-agentic-app, free-text-microservice) regenerate byte-deterministically under `SOURCE_DATE_EPOCH=1700000000`; `test_backward_compatibility.py` passes against regenerated baselines with idempotency verified

### Feature 082: Threat Agent Skill References

**PRD**: [082-threat-agent-skill-references](../02_PRD/082-threat-agent-skill-references-2026-04-11.md)
**Delivered**: 2026-04-11 | **PR**: #151 | **Tasks**: 68/68 complete | **Stories**: 5/5 passing

- **US-082-1** (P0): Lean Agent Migration - All 11 threat detection agents (6 STRIDE + 5 AI) migrated from self-contained inline shape to lean + skill references pattern, with STRIDE agents at 50-54 lines and AI agents at 78-114 lines — every agent within FR-10 tier caps
- **US-082-2** (P0): Detection Pattern Skill References - 11 new companion skill directories created at `.claude/skills/tachi-<name>/references/` with `detection-patterns.md` reference files loaded via single `**MANDATORY**: Read` directive at detection start
- **US-082-3** (P0): Enrichment Floor Clearance - +30 new pattern categories added across the 11 agents against a >=22 aggregate floor, sourced from OWASP Top 10 2021, OWASP LLM Top 10 2025, MITRE ATT&CK v15+, MITRE ATLAS v5.1+, CWE Top 25 2024, and NIST AI 600-1
- **US-082-4** (P1): Shared Reference Consolidation - `finding-format-shared.md` gains "For Threat Agents" producer section (additive-only); OWASP 3x3 risk matrix canonicalized to single file (`severity-bands-shared.md`)
- **US-082-5** (P1): ADR-023 Detection Variant Documentation - New ADR records the sibling detection variant as a second documented lean-agent shape alongside the methodology variant

### Feature 130: Fix Attack Path Mermaid Rendering

**PRD**: [130-fix-attack-path-mermaid-rendering](../02_PRD/130-fix-attack-path-mermaid-rendering-2026-04-11.md)
**Delivered**: 2026-04-11 | **PR**: #131 | **Tasks**: 23/23 complete | **Stories**: 4/4 passing

- **US-130-1** (P0): Fail-Fast Preflight Gate - Shell-level preflight gate in `/tachi.security-report` and Python-level `shutil.which("mmdc")` raise in `extract-report-data.py` fire when attack trees contain Critical/High findings and mmdc is not installed
- **US-130-2** (P0): Mid-Render Failure Aggregation - `_render_single` returns structured `error_record` dicts; `render_mermaid_to_png()` collects failures and raises `RuntimeError` with per-finding failure list instead of silently marking `has_image=False`
- **US-130-3** (P0): Text Fallback Removal - Typst text-fallback branch deleted outright from `attack-path.typ`; silent text fallback is no longer a supported shipping mode
- **US-130-4** (P1): ADR-022 Hard Prerequisite Policy - New ADR establishes fail-loud posture for absent CLI prerequisites, gated on input detection (mmdc required only when attack trees present)

### Feature 128: Executive Threat Architecture Infographic

**PRD**: [128-executive-threat-architecture](../02_PRD/128-executive-threat-architecture-2026-04-09.md)
**Delivered**: 2026-04-10 | **PR**: #133 | **Tasks**: 51/51 complete | **Stories**: 4/4 passing

- **US-128-1** (P0): Executive Architecture Template - New `executive-architecture` infographic template groups components into architectural layers, filters Critical/High findings, and selects one callout per layer for CISO-ready visualization
- **US-128-2** (P0): Early-Page PDF Placement - Portrait JPEG output placed immediately after Executive Summary (pages 2-3) in the PDF security report using existing `infographic-page()` Typst function
- **US-128-3** (P1): Command Integration - `exec` alias dispatch and inclusion in `all` shorthand expansion in `/tachi.infographic` command
- **US-128-4** (P1): Graceful Degradation - Threat models with no qualifying Critical/High findings produce no executive-architecture infographic without errors

### Feature 120: Architecture Lifecycle Command

**PRD**: [120-architecture-lifecycle-command](../02_PRD/120-architecture-lifecycle-command-2026-04-09.md)
**Delivered**: 2026-04-09 | **PR**: #123 | **Tasks**: 28/28 complete | **Stories**: 4/4 passing

- **US-120-1** (P0): Version Tracking - YAML frontmatter (version, date, description, checksum, previous_version) added to generated architecture files
- **US-120-2** (P0): Archive Mechanism - Previous versions archived to `{parent_dir}/.archive/v{N}/architecture.md` before updates; legacy files archived as v0
- **US-120-3** (P1): Threat Model Snapshot - `/tachi.threat-model` copies architecture file verbatim into timestamped output folder
- **US-120-4** (P1): Guided Update Mode - Walks users through change categories (services, components, data flows, trust boundaries, external entities, AI capabilities)

### Feature 141: MAESTRO Phase 2 — Cross-Layer Attack Chain Analysis

**PRD**: [141-maestro-cross-layer-attack-chains](../02_PRD/141-maestro-cross-layer-attack-chains-2026-04-12.md)
**Delivered**: 2026-04-12 | **PR**: #159 | **Tasks**: 34/34 complete | **Stories**: 6/6 passing

- **US-141-1** (P0): Cross-Layer Attack Chain Detection - Pipeline includes a cross-layer correlation phase that identifies attack chains by analyzing relationships between findings across different MAESTRO layers using component lineage, data flow dependencies, and layer adjacency; produces an attack-chains.md artifact enumerating chains with chain IDs, ordered finding references, layer progression, maximum severity, and causal narrative per transition
- **US-141-2** (P0): Attack Chain Narrative in Threat Report - Threat report includes an "Attack Chains" section (Section 6) with narrative walkthroughs for each Critical and High chain, describing initial exploit, intermediate cascade steps with layer transitions, and final business impact
- **US-141-3** (P0): Visual Chain Diagrams in PDF Security Report - PDF security report renders dedicated chain diagram pages showing vertical MAESTRO layer-stack progression with attack arrows, condensed narrative, and impacted finding references for board-ready executive communication
- **US-141-4** (P0): Chain-Breaking Control Recommendations - Each chain identifies chain-breaking controls — findings whose remediation would interrupt the chain progression — with structural centrality rationale and heuristic disclaimer
- **US-141-5** (P1): End-to-End Example Demonstration - At least one example architecture demonstrates a multi-layer attack chain end-to-end with attack chains artifact, threat report narrative, and PDF chain diagram pages
- **US-141-6** (P1): Canonical MAESTRO Deliverable - Chain narratives follow the canonical CSA MAESTRO worked example format with causal vocabulary ("enables," "triggers," "shifts," "manifests as") and visual layer-stack diagrams matching the canonical MAESTRO representation

### Feature 144: NIST AI RMF Integration Evaluation ADR

**PRD**: [144-nist-ai-rmf-evaluation-adr](../02_PRD/144-nist-ai-rmf-evaluation-adr-2026-04-15.md)
**Delivered**: 2026-04-16 | **PR**: #169 | **Tasks**: 43/43 complete (T027 N/A per FR-008 XOR) | **Stories**: 5/5 passing

- **US-144-1** (P1): Compliance Officer NIST Mapping Decision - A single ADR (ADR-025) whose Decision section names tachi's NIST AI RMF posture unambiguously in the first paragraph and whose Context section contains three labeled mapping surfaces (Functions × pipeline phases, Subcategories × compensating-control categories, GAI risks × STRIDE+AI) with every row annotated as Overlap, Gap, Conflict, or "No equivalent"
- **US-144-2** (P1): Security Engineer Procurement Justification - Exactly one ADR Decision section addresses NIST AI RMF; the tachi-control-analysis SKILL.md "NIST AI RMF Relationship" paragraph contains the same decision-noun phrase as ADR-025's Decision section (verbatim string-equality check, modulo case, per SC-007)
- **US-144-3** (P1): CISO Audit Preparation - A tachi-curated reference file at `.claude/skills/tachi-shared/references/nist-ai-rmf-mapping.md` ships either a complete Option A mapping table covering all 8 tachi compensating-control categories to NIST AI RMF Subcategory equivalents, or a relationship-only stub naming the wired-integration site and linking to a follow-on implementation Issue; links resolve on main via relative path
- **US-144-4** (P2): Maintainer Decision Traceability - ADR-025 Alternatives Considered enumerates ≥3 options (A/B/C) each with pros, cons, effort, compliance value, and "Why Chosen" or "Why Not Chosen"; Status reads "Accepted"; Related ADRs line cross-references ADR-024 (companion AIVSS evaluation) bidirectionally
- **US-144-5** (P1): Non-Disruption Guarantee for Unregulated Adopters - Zero drift on `schemas/`, `scripts/`, `.claude/agents/`, and `examples/` (SC-006 git-diff guard); backward-compatibility pytest 5/5 PASS byte-identical under SOURCE_DATE_EPOCH=1700000000 (ADR-021 baseline preserved); no new runtime dependencies or CLI prerequisites for adopters who do not need regulatory alignment

### Feature 142: MAESTRO Phase 3 — Agentic Threat Pattern Expansion

**PRD**: [142-maestro-agentic-pattern-expansion](../02_PRD/142-maestro-agentic-pattern-expansion-2026-04-16.md)
**Delivered**: 2026-04-16 | **PR**: #172 | **Tasks**: 33/33 complete | **Stories**: 6/6 passing

- **US-142-1** (P0): Agent Collusion as an Explicit Filter - Security engineers can filter threat model output by the "Agent Collusion" pattern; coordinated multi-agent attack findings are tagged distinctly from single-agent exploits via the `agentic_pattern` column in threats.md and `maestro-pattern:agent_collusion` SARIF tags, gated by the multi-agent predicate
- **US-142-2** (P0): Temporal Attack Detection - Threat modelers analyzing long-running agentic systems (persistent memory, fine-tuning loops, learning pipelines) see explicit Temporal Attack findings (sleeper agents, gradual corruption, seasonal exploitation, time-delayed activation) invisible to point-in-time STRIDE analysis, with threat descriptions naming the specific temporal vector class
- **US-142-3** (P1): Emergent Behavior Risks Called Out in Threat Report - CISOs reviewing the PDF security assessment see a dedicated "Agentic Pattern Analysis" section placed after Cross-Layer Attack Chains (Feature 141) and before Findings Detail, with per-pattern subsections containing canonical definition, severity counts, 100-200 word narrative, and impacted finding IDs; zero-finding subsections suppressed
- **US-142-4** (P1): Coverage Mapping Documentation - Adopters evaluating tachi's MAESTRO completeness read the coverage mapping table in `maestro-agentic-patterns-shared.md` with one row per canonical pattern and three constrained Coverage Strength values (Full / Partial / None — Coverage Required), with Partial assessments requiring a Gap justification preventing overclaiming
- **US-142-5** (P1): Pattern-Tagged Output for Downstream Tooling - MAESTRO practitioners integrating tachi output can rely on the `agentic_pattern` field being present on every finding with `none` as default (no null-safety logic needed); SARIF output exposes `maestro-pattern:<name>` tags for non-`none` patterns matching the existing `maestro-layer:` convention
- **US-142-6** (P0): End-to-End Multi-Agent Example - Designated multi-agent example demonstrates all three previously-uncovered patterns (Agent Collusion, Emergent Behavior, Temporal Attack) end-to-end with findings in threats.md, populated Agentic Pattern Analysis section in threat-report.md, and corresponding SARIF tags; 5 non-multi-agent baselines show zero new pattern findings under the multi-agent gate predicate

### Feature 145: MAESTRO Canonical Worked Example

**PRD**: [145-maestro-canonical-worked-example](../02_PRD/145-maestro-canonical-worked-example-2026-04-16.md)
**Delivered**: 2026-04-17 | **PR**: #175 | **Tasks**: 53/53 complete | **Stories**: 6/6 passing

- **US-145-1** (P0): New Adopter Canonical First-Read - A security engineer evaluating tachi opens `examples/README.md`, sees the canonical MAESTRO example called out as the recommended first read for MAESTRO users, opens the example's `README.md`, and gets an adopter-facing tour covering domain overview, MAESTRO layer coverage table, what to look for in the output, and how to read the accompanying files (threats.md, threat-report.md, PDF, infographics)
- **US-145-2** (P0): Evaluator Cross-Layer Attack Chain Demonstration - A security engineer performing a tools evaluation reads the example's generated `threat-report.md` and sees the Cross-Layer Attack Chains section (Feature 141) render at least one attack chain spanning three or more MAESTRO layers with a causal narrative comparable in shape to the CSA canonical financial-trading kill-chain; `attack-chains.md` confirms chain membership traces architectural data-flow lineage (not keyword coincidence)
- **US-145-3** (P0): Canonical Comparison Surface for Multi-Agent Threat Modeling - A CISO, security team lead, or MAESTRO practitioner reviews the example's `threat-report.md` Agentic Pattern Analysis section (Feature 142) and finds at least three of the six canonical agentic patterns populated with narratives; the README's MAESTRO layer coverage table maps every architecture component to one or more MAESTRO layers in a format directly comparable to the CSA canonical mapping
- **US-145-4** (P1): MAESTRO Regression Fixture for Maintainers - A tachi maintainer adding a new feature touching MAESTRO capability runs the backward-compatibility test suite and sees the canonical example regression-check the full MAESTRO surface (all seven layers populated, cross-layer chains surfaced, agentic patterns populated, infographics generated); PDF baseline regenerates byte-identical under `SOURCE_DATE_EPOCH=1700000000` (per ADR-021)
- **US-145-5** (P1): Purpose-Built Validation Target for Future MAESTRO Work - A developer implementing Phase 2 cross-layer chain logic, Phase 3 agentic pattern synthesis, or any follow-on MAESTRO phase has a regression target that naturally exercises multi-layer chains and multi-pattern findings without architectural contortion; seven-layer coverage, inter-agent data flows, persistent-state components, and emergent-behavior descriptions all pre-verified by the Pre-Execution Architecture Review Checklist
- **US-145-6** (P1): Adopter Compliance Framework Cross-References - An adopter reading the canonical MAESTRO example's README encounters a short compliance-posture section (approximately 100-150 words) summarizing tachi's AIVSS (ADR-024) and NIST AI RMF (ADR-025) posture with links to the authoritative ADRs; `examples/README.md` positions the canonical MAESTRO example as distinct from the existing six examples (baseline STRIDE, input-format fixtures, dual-dispatch demo)

### Feature 180: F-A1 Taxonomy Crosswalk Collection

**PRD**: [180-taxonomy-crosswalk-collection](../02_PRD/180-taxonomy-crosswalk-collection-2026-04-17.md)
**Delivered**: 2026-04-17 | **PR**: #181 | **Tasks**: 41/41 complete | **Stories**: 5/5 passing
**Spec**: [specs/180-taxonomy-crosswalk-collection/spec.md](../../../specs/180-taxonomy-crosswalk-collection/spec.md)

- **US-180-1** (P1): Machine-Readable Taxonomy Records - An adopter integrating tachi output into downstream vulnerability manager / SIEM / compliance tooling loads any of 7 catalog YAMLs under `schemas/taxonomy/` (owasp, mitre-attack, mitre-atlas, nist-ai-rmf, cwe, tachi-control-category, tachi-stride-ai-category) via `yaml.safe_load` in a fresh Python 3.11 environment with only `pyyaml` installed and resolves any taxonomy ID (OWASP / MITRE ATT&CK / ATLAS / NIST AI RMF / CWE) to a stable record containing canonical id, full_id, name, url, and cross-framework references without consulting any other file
- **US-180-2** (P1): Single Authoritative Crosswalk - A tachi maintainer or future downstream-feature author queries `crosswalk.yaml` to find all cross-framework edges for a given taxonomy item (e.g., `source.taxonomy == 'owasp' && source.id == 'LLM05'`) and retrieves edges with closed `edge_type` enum (primary/related/superseded), `confidence` enum (high/medium/low), and per-edge citation — 526 primary edges at merge time (exceeding ≥500 Tier 1 floor), including verbatim transcription of 27 NIST AI RMF Surface B mapping rows per FR-022
- **US-180-3** (P2): Documented Curation Methodology - A reviewer or future maintainer opens `schemas/taxonomy/README.md` alone and finds §Purpose with runnable Python snippet demonstrating the resolution pattern for all 7 catalog YAMLs, 7 per-framework provenance sections, 3-level confidence calibration rubric with anti-drift rule, canonical-URL conventions per framework, 5 per-framework update procedures, and explicit "What F-A1 does NOT give you today" subsection naming deferred downstream-feature capabilities
- **US-180-4** (P1): Referential Integrity Test Suite - A code reviewer or CI system runs `pytest tests/schemas/test_taxonomy_integrity.py` on a freshly-cloned repo and all 5 tests pass green (`test_framework_yamls_load`, `test_crosswalk_loads`, `test_crosswalk_referential_integrity`, `test_citation_shape`, plus optional sort test); integrity suite enforces FR-027 through FR-032 including referential integrity (every edge's source.id and target.id resolve to catalog records), closed-enum membership (7-value taxonomy, 3-value edge_type, 3-value confidence), and citation shape (URL-regex or existing file path)
- **US-180-5** (P2): Public ADR on Merge - A future tachi contributor opens `docs/architecture/02_ADRs/ADR-027-taxonomy-crosswalk-schema.md` at Status: Accepted, reads per-item record shape, per-edge record shape, 7-value taxonomy enum rationale, 3-value edge_type enum rationale, 3-value confidence enum rationale, scope-exception rationale for shipping F-A1 as a single PRD despite aggregating 9 files, and cross-references to ADR-020 / ADR-021 / ADR-023 / ADR-024 / ADR-025; three follow-on Issues filed (F-A1.1 Surface C deferred per architect Option (c), F-A1.2 related/superseded edges, F-A1.3 citation link-rot)

### Feature 189: F-A2 Source Attribution Schema Extension

**PRD**: [189-source-attribution-schema-extension](../02_PRD/189-source-attribution-schema-extension-2026-04-17.md)
**Delivered**: 2026-04-17 | **PR**: #190 | **Tasks**: 36/36 complete | **Stories**: 3/3 passing
**Spec**: [specs/189-source-attribution-schema-extension/spec.md](../../../specs/189-source-attribution-schema-extension/spec.md)

- **US-189-1** (P0): Multi-Framework Citation on a Single Finding - When a threat agent emits a finding that addresses multiple compliance-framework items simultaneously (e.g., LLM05 improper output handling spans OWASP LLM05, CWE-1426, and MITRE ATLAS AML.T0051), cite all three items on the single finding without duplicating finding rows — the finding's semantic unit remains intact while every cited item becomes programmatically aggregable. `schemas/finding.yaml` `schema_version` exactly `"1.5"` (minor bump from 1.4 per ADR-026 additive-field rule); `source_attribution` field optional (field-absent on findings that don't cite anything, NOT defaulted to empty array); multi-record arrays preserve input order
- **US-189-2** (P0): Parser Round-Trip Preserves Backward Compatibility - When the pipeline parses the Section 7 table in `threats.md` on any of the 5 existing non-agentic example baselines, get back the same finding objects as pre-F-A2 — no extra keys, no dropped keys — so F-A2 is truly additive and the SC-2 byte-deterministic regeneration gate passes. `scripts/tachi_parsers.py::parse_threats_findings` omits `source_attribution` key when absent from source (no implicit default array injection — preserves Feature 104 `delta_status`-style conditional-key precedent); 5 non-agentic example PDF baselines (`web-app`, `microservices`, `ascii-web-api`, `mermaid-agentic-app`, `free-text-microservice`) regenerate byte-identically under `SOURCE_DATE_EPOCH=1700000000`
- **US-189-3** (P0): Closed-Enum `relationship` with Referential Integrity - When a coverage auditor reads a finding's `source_attribution` array downstream, knows from the `relationship` value whether the cited item is the primary item the finding addresses, a related item, or a derived item, so F-B coverage attestation can weight primary citations differently from related or derived ones. Two-tier validation architecture: V1/V2/V3/V5 enum validation at parse time (closed 5-value `taxonomy` enum `{owasp, mitre-attack, mitre-atlas, nist-ai-rmf, cwe}` excluding 2 tachi-internal taxonomies, closed 3-value `relationship` enum `{primary, related, derived}` with `primary` default); V4 referential-integrity validation as separate callable phase resolving each `{taxonomy, id}` against `schemas/taxonomy/{taxonomy}.yaml` catalog records from Feature 180

### Feature 194: F-B Coverage Attestation Report Section

**PRD**: [194-coverage-attestation-report-section](../02_PRD/194-coverage-attestation-report-section-2026-04-18.md)
**Delivered**: 2026-04-18 | **PR**: #195 | **Tasks**: 45/46 complete (T044 post-merge SHA fill deliberately pending for direct commit to main after `/aod.deliver`) | **Stories**: 3/3 passing
**Spec**: [specs/194-coverage-attestation-report-section/spec.md](../../../specs/194-coverage-attestation-report-section/spec.md)

- **US-194-1** (P1): Per-Finding Attribution Table - A security reviewer opens the PDF security report and wants to audit which OWASP / MITRE ATT&CK / MITRE ATLAS / NIST AI RMF / CWE items a specific finding cites, seeing a single paginated table with one row per finding and per-taxonomy citation columns (`Finding ID | Title | Severity | OWASP refs | MITRE refs | NIST refs | CWE refs`), with `relationship: primary` citations rendered bold and `related`/`derived` plain (WCAG AA color-blind accessible — bold vs plain weight, not color alone), MITRE column grouping ATT&CK and ATLAS together with per-ref prefix (`ATT&CK:T1070.001` vs `ATLAS:AML.T0051`) — audit completes without opening `threats.md` source or cross-referencing separate taxonomy files
- **US-194-2** (P1): Aggregate Per-Framework Coverage Matrix - An adopter or evaluator wants to answer "what fraction of OWASP LLM Top 10 does this engagement cover, and which items are the gaps?" from the PDF alone, seeing exactly one page per external framework (OWASP, MITRE ATT&CK, MITRE ATLAS, NIST AI RMF, CWE — all 5 rendered, including framework pages where every item is a Gap per 0% coverage valid-answer rule) with every item classified as Covered (≥1 `primary` attribution) / Partial (zero `primary` AND ≥1 `related`/`derived`) / Gap (zero attributions), coverage percentage `K / N` where `N = len(yaml.safe_load(schemas/taxonomy/{framework}.yaml))` (authoritative F-A1 YAML record count computed once at extraction time per ADR-029 Q2-A), Partial count rendered alongside with equal visual weight (`Covered: 12/38 = 31.6% · Partial: 3 · Gap: 23`), Gap items highlighted with color + icon distinction (WCAG AA color-blind accessible); matrix is intra-framework only (zero `crosswalk.yaml` JOIN per FR-017) and excludes 2 internal taxonomies (`tachi-control-category`, `tachi-stride-ai-category`) per FR-018
- **US-194-3** (P1): Conditional Inclusion Preserves Backward Compatibility - A tachi maintainer regenerates the 5 non-agentic example PDFs (`web-app`, `microservices`, `ascii-web-api`, `mermaid-agentic-app`, `free-text-microservice`) and expects byte-identical output under `SOURCE_DATE_EPOCH=1700000000` per ADR-021 because no finding carries `source_attribution` yet (F-A3 populators haven't shipped); `scripts/extract-report-data.py::compute_has_source_attribution` emits `#let has-source-attribution = false` to the Typst data contract, `templates/tachi/security-report/main.typ` §2b defaults block carries a default-value guard preventing "variable not found" compile errors on stale `report-data.typ` files, and the `#if has-source-attribution and per-finding-rows.len() > 0 { ... }` conditional block omits the entire coverage-attestation section (no page break, no section header, no divider, no empty table) when either predicate is false — SC-002 regression gate green, 5/5 baselines byte-identical post-F-B

### Feature 201: F-1 Output Integrity Threat Agent (OWASP LLM05:2025)

**PRD**: [201-output-integrity-threat-agent](../02_PRD/201-output-integrity-threat-agent-2026-04-18.md)
**Delivered**: 2026-04-19 | **PR**: #202 | **Tasks**: 55/55 complete | **Stories**: 3/3 passing
**Spec**: [specs/201-output-integrity-threat-agent/spec.md](../../../specs/201-output-integrity-threat-agent/spec.md)

- **US-201-1** (P1): LLM-Output-to-Downstream-Sink Detection - A security analyst threat-models an architecture where LLM output flows into a browser, SQL query, shell, template engine, file write, or outbound HTTP client without post-model sanitization and expects tachi to flag those components with concrete `OI-{N}` findings citing OWASP LLM05:2025 so the XSS / SQLi / SSRF / template-injection / path-traversal surface (which input-side `prompt-injection` detection does not cover) is surfaced with the same rigor as the input side. Given an architecture containing an LLM Process whose output flows into at least one downstream execution sink, running `/tachi.threat-model` emits ≥1 `OI-{N}` finding with `category: llm`, OWASP LLM05:2025 in `references`, and a populated `source_attribution` array containing `{taxonomy: owasp, id: LLM05, relationship: primary}` plus the applicable CWE related entry; given an architecture with no such flow, the agent emits **zero** findings (two-part emission gate enforced per FR-011: keyword match AND structural indicator of a downstream execution sink both required)
- **US-201-2** (P1): Stack-Specific Mitigation Guidance - A developer reading an `OI-{N}` finding needs to address the issue in a codebase and expects the `mitigation` field to name specific encodings, libraries, or patterns matched to the detected sink type so the fix can be applied without re-deriving the output-handling pattern from primary OWASP / CWE sources. For every emitted `OI-{N}` finding, the `mitigation` field names at least one specific encoding mechanism, library, or defensive pattern matched to the sink type — client-side execution: `textContent` (not `innerHTML`) / React `{value}` (not `dangerouslySetInnerHTML`) / Django `{{ value }}` (not `|safe`) / CSP `script-src 'self' 'nonce-<nonce>'`; server-side execution: SQLAlchemy `text(sql).bindparams()` / psycopg2 parametrized `cursor.execute(sql, params)` / `subprocess.run([cmd, arg1, arg2], shell=False)`; SSRF: URL allowlist + egress firewall blocking `169.254.169.254`; template injection: Jinja2 `SandboxedEnvironment`; path traversal: `pathlib.Path(filename).resolve().is_relative_to(allowlisted_output_dir)` — no generic "sanitize output" prose (T021 Wave 2 specificity check green)
- **US-201-3** (P1): Heuristic A Resolution for ASI09 Scope - An adopter runs tachi on an agentic application where an LLM-bearing agent uses misleading tone, overconfident claims, false authority signaling, or manipulative persuasion against a human downstream consumer and expects ADR-030 to make an explicit Heuristic A determination on whether ASI09 Human-Agent Trust Exploitation is covered by `output-integrity` (Outcome A) or by a future `trust-exploitation` agent shipped as F-4 (Outcome B). ADR-030 Decision 2 resolves **Outcome B (split)** with justification referencing GUIDE-threat-coverage-research §11 Heuristic A signal-class taxonomy: F-1 owns encoding/sanitization signal class (bytes / strings / syntax primitives on machine-victim output handling); F-4 reserved for psychology/linguistics signal class (manipulative tone, fabricated authority, absence of uncertainty disclaimers). F-1's `## Purpose` section explicitly forward-references `trust-exploitation` (F-4) as the future owner and lists ASI09 as out-of-scope; BLP-01 §8 blocking gate for F-4 `/aod.discover` invocation satisfied on F-1 merge

### Feature 206: F-2 Misinformation Threat Agent (OWASP LLM09:2025)

**PRD**: [206-misinformation-threat-agent](../02_PRD/206-misinformation-threat-agent-2026-04-23.md)
**Delivered**: 2026-04-24 | **PR**: #207 | **Tasks**: 62/62 complete | **Stories**: 3/3 passing
**Spec**: [specs/206-misinformation-threat-agent/spec.md](../../../specs/206-misinformation-threat-agent/spec.md)

- **US-206-1** (P1): Ungrounded-Factual-Output Detection - A security analyst threat-models an architecture where an LLM emits factual, citation-bearing, or decision-critical output without a declared grounding, verification, or confidence-calibration mechanism and expects tachi to flag those components with concrete `MI-{N}` findings citing OWASP LLM09:2025 so the misinformation risk surface — which neither input-side `prompt-injection` nor output-side `output-integrity` covers — is surfaced before the output reaches end users, downstream automated decisions, or regulatory-exposed systems. Given an architecture containing an LLM Process whose output exhibits factual-output indicators (factual claims, citations, recommendation/decision outputs, or high-stakes domain signals) without declared grounding, running `/tachi.threat-model` emits ≥1 `MI-{N}` finding with `category: llm`, OWASP LLM09:2025 in `references`, and a populated `source_attribution` array containing `{taxonomy: owasp, id: LLM09, relationship: primary}` plus `{taxonomy: cwe, id: CWE-345, relationship: related}`; given an architecture with no qualifying Process or only purely-stylistic LLM output, the agent emits **zero** findings (two-part emission gate per FR-011: LLM keyword match AND factual-output indicator both required; keyword-only match produces no finding to prevent false positives on stylistic-only LLM Processes)
- **US-206-2** (P1): Named Grounding / Verification Mitigation Guidance - A developer reading an `MI-{N}` finding needs to address it in their application and expects the `mitigation` field to name specific grounding, verification, HITL, or calibration mechanisms matched to the detected pattern category so the fix can be applied without inventing a mitigation pattern from scratch or re-deriving from primary OWASP / NIST / ATLAS sources. For each emitted `MI-{N}` finding, the `mitigation` field names at least one specific grounding, verification, HITL, or calibration mechanism matched to the finding's pattern category — ungrounded factual emission → `mandatory RAG grounding with per-claim source attribution` / `retrieval-strength metric declaration (hit-rate, recall@k)` / `confidence-calibration layer (temperature scaling + ECE monitor)`; citation fabrication → `output-time citation verification against retrieved source URIs` / `strict citation-token constraint on decoder output`; overreliance / missing HITL → `human-in-the-loop review queue on decision-critical output` with consumer-facing-high-stakes (HIGH/CRITICAL) vs internal-low-stakes (MEDIUM or below) distinction; retrieval-grounding gaps → `retrieval-strength metric (hit-rate, recall@k)` / `per-query retrieval-score threshold` / `versioned retrieval corpus with staleness policy`; confidence-calibration absence → `calibration layer (temperature scaling + ECE monitor)` / `refusal pattern for low-confidence queries` / `calibrated-confidence exposure on output`. Every finding's `references` array includes `OWASP LLM09:2025` primary and `source_attribution` carries it at `relationship: primary`; supporting references (`MITRE ATLAS AML.T0042 Verify Attack`, `NIST AI 600-1 §2.4 Hallucination`) appear as prose inside the pattern catalog's Primary Sources list because the referential-integrity validator requires catalog-resolvable IDs and those two entries are absent at PRD time
- **US-206-3** (P1): Factual-Integrity as a First-Class Distinct Threat Class - An adopter runs tachi on an AI-assisted medical, legal, financial, or decision-critical application and expects misinformation to be surfaced as a first-class threat class **distinct from both `prompt-injection` and `output-integrity`** so the adopter-facing report separates "attacker-induced wrong output" (prompt-injection / LLM01), "output crosses unsanitized boundary into execution sink" (output-integrity / LLM05), and "ungrounded wrong output" (misinformation / LLM09). **ADR-031** records the Heuristic A signal-class rationale cross-referencing ADR-030's Decision 1 scope boundary — three scope boundaries explicitly resolved: (a) distinct from `prompt-injection` (input-side attacker-controlled injection — machine-attacker, input primitives), (b) distinct from `output-integrity` (output-sanitization per ADR-030 Decision 1 — machine-victim, bytes/strings/syntax primitives), (c) scoped to factual-integrity (grounding, verification, HITL, calibration — human-victim and decision-cascade-victim, factual-content primitives). The regenerated `agentic-app` example exercising all three surfaces renders `LLM-{N}`, `OI-{N}`, and `MI-{N}` findings adjacent (not synthesized) in the `category: llm` section of `threat-report.md` — each finding's ID prefix preserves its signal-class origin and each finding carries its own `source_attribution` primary (LLM01, LLM05, LLM09 respectively); three-agent simultaneous emission on a single LLM Process is correct behavior, not duplication

### Feature 212: Improve Executive-Architecture Infographic

**PRD**: [212-improve-executive-architecture-infographic](../02_PRD/212-improve-executive-architecture-infographic-2026-04-24.md)
**Delivered**: 2026-04-25 | **PR**: #213 | **Tasks**: 37/37 complete | **Stories**: 3/3 passing
**Spec**: [specs/212-improve-executive-architecture-infographic/spec.md](../../../specs/212-improve-executive-architecture-infographic/spec.md)

- **US-212-1** (P1): OpenClaw-Style Rendering - A security consultant generating a tachi PDF security report regenerates the PDF on a realistic threat-model dataset (≥3 Critical/High findings across ≥2 layers) and sees the executive-architecture page render as a proper system flow diagram — every component is a rounded-rectangle node with a colored border, directional arrows connect layers top-to-bottom, ≥5 callouts appear with leader lines pointing to specific nodes, and qualifying layers with zero Critical/High findings render as a compact factual badge sized to ≤15% of page height (not a full-band placeholder). PRD #128 skip behavior preserved (zero Critical/High findings → template skipped, PDF byte-identical to pre-F-212 baseline). Locked verbatim Gemini prompt in `.claude/skills/tachi-infographics/references/gemini-prompt-construction.md` instructs `schematic diagram with shapes and arrows` directive plus per-layer border-accent colors inheriting severity palette from `visual-design-system.md`.
- **US-212-2** (P1): Denser, System-Wide Callout Distribution - A security consultant delivering a PDF whose client has 8+ qualifying Critical/High findings sees the page show 6–8 callouts distributed across layers with weighted distribution (Largest Remainder Method applied to qualifying-findings-per-layer) so the reader perceives the page as a comprehensive diagnosis rather than a one-per-layer sampler. `_select_critical_high_callouts()` returns 6–8 callouts drawn system-wide (not one per layer): per-layer floor rule guarantees every qualifying layer with ≥1 Critical/High finding gets ≥1 callout; per-layer ceiling caps any single layer at 4 callouts with a compact "+ N more in this layer" annotation absorbing the remainder; total-floor short-circuits to all qualifying findings when system-wide qualifying count < 6 (no synthetic inflation). Stable tie-break via deterministic sort produces byte-identical `callouts[]` arrays across reruns on identical input. Pytest invariant on a fixture matrix enforces the per-layer floor as a regression gate.
- **US-212-3** (P2): Structural Data in the Payload - A tachi maintainer inspecting the executive-architecture payload JSON sees `flow_edges[]` and `clusters[]` populated directly from `parse_scope_data` (the shared scope parser's `data_flows` and `trust_boundaries` sections) so Gemini draws arrows and group boundaries from structured data rather than inferring them from component names — and so any future infographic change can reuse the structure without re-parsing. `_build_executive_architecture_payload()` includes `flow_edges[]` (each entry `{source, destination}` aligned to producer field name `destination` not `target`) sorted by `(source.lower(), destination.lower())` and truncated to 50 entries after sort with logged warning; `clusters[]` (each entry `{name, members}` derived from `trust_boundaries[].zone` and `trust_boundaries[].components`) sorted by `(_TRUST_LEVEL_ORDER, name.lower())` with case-insensitive `members` ordering matching `_compute_trust_zones`. Empty-source fixtures emit empty arrays (not `null`, not missing keys); the Gemini prompt updated in the same Level 3 landing references `flow_edges` and `clusters` by name and no longer instructs Gemini to infer flow or clustering from component names alone.

### Feature 219: F-3 ASI07 Tool-Abuse Agent Enrichment (OWASP ASI07:2026)

**PRD**: [219-asi07-tool-abuse-enrichment](../02_PRD/219-asi07-tool-abuse-enrichment-2026-04-25.md)
**Delivered**: 2026-04-26 | **PR**: #220 | **Tasks**: 63/67 complete (4 intentional post-merge: T031 SHA fill, T062 internal BLP-01 update, T063 release-please verification, T064 contingent buffer) | **Stories**: 3/3 passing
**Spec**: [specs/219-asi07-tool-abuse-enrichment/spec.md](../../../specs/219-asi07-tool-abuse-enrichment/spec.md)

- **US-219-1** (P1): Inter-Agent Channel Detection (A2A) - A security analyst threat-models a multi-agent architecture where two or more agent Process components communicate over a channel — direct RPC, message bus, shared queue, MCP-to-MCP bridge, named pipe, or IPC — without declared mutual authentication, message signing, replay protection, or taint propagation, and expects tachi to flag those channels with concrete `AG-{N}` findings citing OWASP ASI07:2026 so inter-agent spoofing, tampering, and replay surfaces are surfaced before they reach runtime, alongside the existing Categories 1-8 findings on individual agents. Given an architecture containing ≥2 agent Process components connected by a communication channel without declared mutual authentication, running `/tachi.threat-model` emits ≥1 new `AG-{N}` finding with `category: agentic`, OWASP ASI07:2026 in `references`, and a populated `source_attribution` array containing `{taxonomy: owasp, id: ASI07, relationship: primary}` plus `{taxonomy: cwe, id: CWE-287, relationship: related}`; given an architecture with exactly one agent (no inter-agent channel), Pattern Category 9 emits **zero findings** — Categories 1-8 fire as they do today. Multi-agent topology gate per FR-011 prevents speculation on hypothetical second agents. AG-8 [NEW] surfaced on regenerated `agentic-app` example flagging the Inter-Agent Communication Channel component with full ASI-07 + CWE-287 + AML.T0060 source_attribution chain.
- **US-219-2** (P1): MCP-to-MCP Trust Propagation Detection - A developer operating a multi-MCP agent fleet where Agent → MCP-A → MCP-B forms a multi-hop trust chain expects tachi to surface MCP-to-MCP trust-propagation risks distinct from single-agent MCP poisoning (Categories 5-8 cover MCP server endpoints; Category 10 covers the **bridge** between two or more MCP servers) so the cross-MCP trust boundary can be hardened with concrete per-hop attestation, signed-capability handoff, and trust-chain validator mechanisms. Given an architecture where an agent dispatches to a remote MCP server which in turn dispatches to a secondary MCP server without declared trust-chain attestation, `/tachi.threat-model` emits ≥1 new `AG-{N}` finding citing OWASP ASI07:2026 primary + CWE-345 related + (where applicable) OWASP LLM03:2025 related (inheriting the supply-chain vocabulary established by existing Category 6); given an architecture with exactly one MCP server (no MCP-to-MCP relay), Pattern Category 10 emits zero findings — single-MCP architectures continue to receive Categories 5-8 findings as they do today. **Pattern Category Disambiguation contract** (formalized as ADR-032 Decision 7) carves Category 6 (upstream ingestion of plugins/tools/MCP servers at registration time) from Category 10 (runtime trust propagation between already-registered MCP servers at invocation time): both findings emit on architectures exhibiting both signals — they are not duplicates and MUST NOT be merged.
- **US-219-3** (P1): Cohesive Agentic-Category Rendering with Heuristic A Enrichment Pattern - An adopter of a multi-agent canonical example runs `/tachi.threat-model` and expects existing tool-abuse findings (Categories 1-8) plus the new ASI07 findings (Categories 9-10) rendered cohesively in the same `category: agentic` section of `threats.md` and `threat-report.md` so the report does not fragment agentic threats across two artificial categories that would emerge if ASI07 were a new agent. The Heuristic A consolidation rationale documented in public ADR-032 (Proposed → Accepted dual-commit pattern per ADR-027/028/029/030/031 precedent) so the enrichment-vs-new-agent decision is auditable. ADR-032 (Status: Accepted at PR #220 merge) records 7 numbered Decisions: D1 enrichment-vs-new-agent (extend `tool-abuse` rather than spawn `asi07-inter-agent-communication`); D2 additive-only edits (3 anchor points: metadata `owasp_references`, `## Purpose`, Detection Workflow Step 5); D3 no-schema-bump asymmetry to ADR-031 D8 (no new `id.pattern` prefix; reuses `AG` family); D4 zero consumer edits (24-file invariant preserved); D5 zero functional orchestrator edit (cosmetic Q2 annotation only); D6 public-only governance (no internal docs changed); D7 Pattern Category Disambiguation (explicit boundary-marking subsection vs. Categories 1-8 to prevent dispatch-mode confusion). The regenerated `examples/agentic-app/` exercises Categories 1-8 + 9-10 simultaneously: AG-8 [NEW] from Category 9 renders adjacent with Categories 1-8 findings in §3.7 "Agentic Threats (AG-1 through AG-8)" — single Agentic-category section (no fragmentation), single-namespace `AG-{N}` ID space. BLP-01 Coverage Matrix transitions ASI07:2026 Planned → Covered (sixth OWASP Agentic Top 10:2026 entry covered out of 10).

### Feature 224: F-4 ASI09 Human-Agent Trust Exploitation (OWASP ASI09:2026 Communication Axis)

**PRD**: [224-trust-exploitation-threat-agent](../02_PRD/224-trust-exploitation-threat-agent-2026-04-26.md)
**Delivered**: 2026-04-27 | **PR**: #225 | **Tasks**: 67/71 complete (4 intentional post-merge: T022 ADR-Accepted flip, T024 verification companion, T025 SHA fill, T067 SHA companion) | **Stories**: 3/3 passing
**Spec**: [specs/224-trust-exploitation-threat-agent/spec.md](../../../specs/224-trust-exploitation-threat-agent/spec.md)

- **US-224-1** (P0): Human-Trust Communication-Axis Detection on Consumer-Facing AI Agents - A security analyst threat-models an architecture where an AI agent emits content directly to end users without architectural mechanisms preventing impersonation, over-persuasion, or undisclosed AI authorship and expects tachi to flag those components with concrete `TE-{N}` findings citing OWASP ASI09:2026 so the trust-exploitation communication-axis risk surface — which neither output-sanitization (F-1 `output-integrity`), factual-integrity (F-2 `misinformation`), nor agent-autonomy/HITL (`agent-autonomy` autonomy axis) covers — is surfaced before the agent reaches end users in production. Given an architecture containing an AI Process matching consumer-facing AI keywords (e.g., `chatbot`, `assistant`, `advisor`, `companion`, `coach`) AND exhibiting at least one human-user-facing emission indicator (outgoing Data Flow to a human-named External Entity like "Customer" / "Patient" / "User" / "Student", OR Process description containing human-user-facing emission keywords), running `/tachi.threat-model` emits ≥1 `TE-{N}` finding with `category: agentic`, OWASP ASI09:2026 in `references`, and a populated `source_attribution` array containing `{taxonomy: owasp, id: ASI09, relationship: primary}` plus `{taxonomy: cwe, id: CWE-223, relationship: related}`; given an architecture with no qualifying Process or with only backend-only AI processing, the agent emits **zero findings** — no speculation. Two-part emission gate per FR-013 (AI keyword match AND human-user-facing emission indicator both required). On the new `examples/consumer-agent-app/` baseline (mental-health/wellness companion archetype), all 5 ASI09 communication-axis pattern categories fired simultaneously (TE-1 undisclosed AI authorship → TE-2 authority-claim emission → TE-3 persuasive-tone manipulation → TE-4 persona-boundary violation → TE-5 synthetic-relationship exploitation), validating the 5-category catalog density on a single realistic consumer-facing AI architecture.
- **US-224-2** (P0): Named Human-Trust Mitigation Guidance Specific to ASI09 Communication Axis - A developer reading a `TE-{N}` finding needs to address it in their consumer-facing AI agent and expects the `mitigation` field to name specific AI-disclosure, confidence-calibration, refusal-pattern, persona-boundary, or synthetic-relationship-safeguard mechanisms matched to the detected pattern category — distinct from output-sanitization (F-1), factual-grounding (F-2), or HITL/autonomy mitigations (`agent-autonomy` autonomy axis) — so the fix can be applied without inventing a mitigation pattern from scratch or re-deriving from primary OWASP / FTC / FDA / ABA / SEC sources. Each emitted `TE-{N}` finding's `mitigation` field names at least one specific mechanism: undisclosed AI authorship → `mandatory AI-generation disclosure banner` / `pre-conversation AI-disclosure splash` / `per-message AI-source label`; authority-claim emission → `confidence-threshold gate with confidence display` / `source-attestation requirement with citation rendered to user` / `refusal pattern for authority claims below confidence threshold`; persuasive-tone manipulation → `uncertainty-disclosure layer` / `temperature-bounded decoder for high-stakes responses` / `persuasion-pattern classifier with refusal`; persona-boundary violations → `persona-memory timeout` / `identity-impersonation refusal pattern` / `persona-anchor declaration`; synthetic-relationship exploitation → `session-length cap with mandatory break / escalation-to-human path` / `emotional-support disclosure on first turn` / `dependency-risk classifier` plus **vulnerable-population safeguards layer** (mental health / eldercare / minors / cognitive-impairment users get additional safeguards: escalation-to-human on high-emotional-distress detection, mandatory professional-care referral, parental-consent for minors, session-context expiry). Every finding's `references` array includes `OWASP ASI09:2026` primary; supporting references (FTC, FDA, ABA, SEC, state-level chatbot disclosure laws, AARP eldercare advocacy) appear in pattern-catalog prose framed per NFR-6 safe-language patterns ("Hypothetical:" prefix, "for context, not legal interpretation", non-clinical distress framing, no real institutional names) — `source_attribution` carries only catalog-resolvable IDs per the F-A2 referential-integrity validator.
- **US-224-3** (P0): Trust-Exploitation Communication-Axis as a First-Class Distinct Threat Class with Stable ADR Crosswalk - An adopter runs tachi on a consumer-facing AI application (customer-support chatbot, mental-health companion, eldercare coach, financial-advisory assistant, AI tutor) and expects human-trust-exploitation to be surfaced as a first-class threat class **distinct from `output-integrity`, `misinformation`, AND the autonomy axis of `agent-autonomy`**, with ASI09 communication-axis binding captured in a stable ADR so downstream compliance mapping is stable across runs. **ADR-033** (Status: Accepted at PR #225 merge per Proposed → Accepted dual-commit lifecycle; 7th consecutive ADR per ADR-027/028/029/030/031/032/033 lineage) records 10 numbered body items: D1-D8 PRD-original (new-agent adoption, Heuristic A signal-class partition resolving four scope boundaries plus the ASI09 sub-scope carve-up between agent-autonomy autonomy axis and human-trust-exploitation communication axis, lean-agent ADR-023 detection-variant conformance, regex-alternation Complex-Shape Clarifier 3rd application, 26-file zero-edit invariant preservation including critical zero-diff on `agent-autonomy.md` despite ASI09 sub-scope carve-up, Proposed → Accepted dual-commit governance), D9 **Naming Disambiguation** (HIGH-1 — explicit `human-trust-exploitation` agent name hyphen-cased / agent-to-human ASI09 scope vs. existing `agentic_pattern: "trust_exploitation"` schema-enum value underscore-cased / agent-to-agent multi-agent-topology scope per Feature 142 / `maestro-agentic-patterns-shared.md` R-04), D10 **DFD Target Decision** (BLOCKING-1 — `dfd_targets: [Process]` only, mirroring F-1 / F-2 single-target precedent; no External Entity declaration; future AI-tier agents wishing to declare External Entity must update this ADR). Schema bump `schemas/finding.yaml` 1.7 → 1.8 (minor, additive) — `id.pattern` extended from `^(S|T|R|I|D|E|AG|LLM|AGP|OI|MI)-\d+$` to `^(S|T|R|I|D|E|AG|LLM|AGP|OI|MI|TE)-\d+$` (12-prefix family); 3rd application of ADR-030 D8 regex-alternation rule. Three-prefix-family discipline within agentic surface (`AG` autonomy-axis / `AGP` multi-agent-topology / `TE` communication-axis) plus three-prefix-family discipline within LLM surface (`LLM` input-side / `OI` output-sanitization / `MI` factual-integrity) yields a **6-prefix-family AI threat surface** with Heuristic A signal-class boundary preservation across both AI-tier sub-categories. **BLP-01 Coverage Matrix transition**: ASI09:2026 communication axis transitions Planned → Covered with F-4 (Feature 224); autonomy axis remains attributed to `agent-autonomy`. Post-F-4 BLP-01 progress: 7/11 features delivered (Foundation + F-1 + F-2 + F-3 + F-4); Tier 1 at 4/5 (F-5 LLM10 remains). OWASP Agentic Top 10:2026 framework row coverage now 10/10 (ASI-01, ASI-02, ASI-04, MCP-03, MCP-05, ASI-07, ASI-09 communication axis covered with autonomy axis already covered); LLM Top 10:2025 framework row at 9/10 (LLM10 remains).

### Feature 229: F-5 LLM10 Unbounded Consumption Verification (OWASP LLM10:2025)

**PRD**: [229-llm10-unbounded-consumption-verification](../02_PRD/229-llm10-unbounded-consumption-verification-2026-04-27.md)
**Delivered**: 2026-04-27 | **PR**: #230 | **Tasks**: 85/85 complete | **Stories**: 3/3 passing
**Spec**: [specs/229-llm10-unbounded-consumption-verification/spec.md](../../../specs/229-llm10-unbounded-consumption-verification/spec.md)

- **US-229-1** (P0): Full LLM10 Surface Coverage via Two-Agent Enrichment - A security analyst threat-models an LLM-serving architecture (consumer chatbot, RAG advisory assistant, agentic orchestrator with LLM-backed worker agents, multi-tenant LLM API gateway, LLM-fronted SaaS) and expects tachi to surface findings covering the **full LLM10 surface** (inference-request flooding, token-budget exhaustion, context-window exhaustion, cost amplification, denial-of-wallet) through the existing `denial-of-service` and `model-theft` agents — without a new agent, without fragmenting findings across more dispatch surfaces, and without scope creep on the host agents' existing surfaces. Given an LLM-serving architecture exhibiting one or more LLM10 sub-pattern indicators (inference endpoint without per-tenant rate limit, recursive-prompt capability without depth limit, multi-tenant LLM-serving without per-tenant token budget), running `/tachi.threat-model` emits ≥1 new `D-{N}` finding citing OWASP LLM10:2025 in its prose-level `references:` array AND ≥1 new `LLM-{N}` finding citing OWASP LLM10:2025 in its prose-level `references:` array; given an architecture with **no LLM-serving topology**, the new Pattern Categories emit **zero findings** — Cat 1–11 (DoS) and Cat 1–9 (model-theft) fire as they do today. **Q1 SPLIT cross-agent vector decomposition** at the F-5 layer: Cat 13 Context-Window Exhaustion bifurcates into Vector A (latency-DoS, owned by `denial-of-service`) and Vector B (cost-DoW, owned by `model-theft`). **Q3 severity-floor 2-condition CRITICAL rule** on Cat 11 (Denial-of-Wallet): defaults to HIGH; CRITICAL only fires when (a) multi-tenant freemium structure is structurally evident AND (b) BOTH per-tenant token budget AND cost alerting are absent — first BLP-01 finding-emission rule with a **2-condition gated severity floor**. On the regenerated `examples/agentic-app/` baseline, 4 new findings emerged: D-10 (Cat 12 Inference-Flooding, Critical), D-11 (Cat 13 Context-Window Latency Vector A, Critical), LLM-15 (Cat 10 Cost-Amplification, Critical), LLM-16 (Cat 11 Denial-of-Wallet Vector B, High per Q3 default — single-tenant); cohesive category rendering preserved (single Section 3.5 DoS + single Section 3.8 LLM in `threat-report.md` with no fragmentation; correlation group CG-8 binds all 4 in Theme 5 of regenerated narrative).
- **US-229-2** (P0): LLM-Specific Mitigation Naming on All New Findings - A developer reading a Cat-12/13 `D-{N}` finding or a Cat-10/11 `LLM-{N}` finding needs to address it in their LLM-serving architecture and expects the `mitigation` field to name **specific LLM-API gateway, token-budget, output-token-cap, recursive-depth-limit, denial-of-wallet detection, and cost-velocity monitoring mechanisms** matched to the detected pattern category — distinct from the host agents' generic infrastructure DoS or model-extraction mitigations — so the fix can be applied without inventing a mitigation pattern from scratch or re-deriving from primary OWASP LLM10:2025 sources. Each emitted finding's `mitigation` field names at least one specific LLM-aware mechanism: **Cat 12 inference-request flooding** → `per-tenant queries-per-second rate limit on the LLM API gateway` / `prompt-size cap at API gateway` / `token-budget per request` / `request-timeout enforcement on inference endpoint`; **Cat 13 context-window latency** → `max-context-window enforcement at API gateway` / `context-window monitoring with anomaly alerting` / `per-tenant context-window cap`; **Cat 10 cost amplification** → `per-query output-token cap` / `per-tenant cost-per-query p99 alerting` / `recursive-prompt depth limit` / `output-amplification-ratio monitoring`; **Cat 11 denial-of-wallet** → `per-tenant token budget with hard cap` / `cost-per-query p99 alerting` / `denial-of-wallet anomaly detection (cost-velocity monitoring)` / `automated tenant suspension on budget breach`. Every emitted Cat-12/13 finding's `references` array includes `OWASP LLM10:2025`, `CWE-400 Uncontrolled Resource Consumption`, and where applicable `CWE-770 Allocation of Resources Without Limits or Throttling` (both CWEs verified present in `schemas/taxonomy/cwe.yaml`); every emitted Cat-10/11 finding's `references` array includes `OWASP LLM10:2025`, and where applicable `OWASP LLM03:2025` for the cost-flow-through-third-party-models adjacency. **MITRE ATT&CK T1496 Resource Hijacking** named in the worked-example narrative on Cat 10/11 as a cost-amplification cross-reference but explicitly absent from any `references` array entry across both companions and all 5 fixtures (T1496 is not catalog-resolvable per `schemas/taxonomy/mitre-attack.yaml`; ADR-034 D6 fixes the rule — 2 prose mentions / 0 references-array entries verified across the full corpus). F-5 deliberately does **not** extend `source_attribution` populator wiring on the host agents — that scope belongs to F-A3 (deferred per `schemas/finding.yaml` lines 230–238 and ADR-028 Decision 6); LLM10 citations live in the prose-level `references:` array (existing field present in finding YAML schema since v1.0).
- **US-229-3** (P0): Audit-Confirmed Additive-Only Transition with Canonical Mapping Table - An adopter runs tachi on an LLM-serving application and expects the LLM10 transition Partial → Covered to be **audit-traceable** through a canonical sub-pattern → owning-agent mapping table that prevents duplicate detection across the two host agents and documents the Heuristic A enrichment-branch consolidation rationale. **ADR-034** (Status: Accepted at squash commit `e086d31` per Proposed → Accepted dual-commit lifecycle; 8th consecutive ADR per ADR-027/028/029/030/031/032/033/034 lineage) records 9 numbered Decisions: D1 enrichment-vs-new-agent at two-agent scope (signal-class identity rationale per Heuristic A — infrastructure-resource-exhaustion same-class as `denial-of-service` availability-degradation surface; extraction-driven-resource-abuse same-class as `model-theft` Category 6 unbounded-inference-consumption surface; spawning a hypothetical `unbounded-consumption` agent would fragment LLM10 findings across three locations); D2 additive-only edits across **4 host files** (`denial-of-service.md` + companion `detection-patterns.md` + `model-theft.md` + companion `detection-patterns.md`) — extending F-3's 2-edit single-host pattern to multi-host enrichment branch; D3 **canonical 5-row LLM10 sub-pattern → owning-agent mapping table populated COMPLETE with severity-hint annotation column** (audit deliverable per team-lead MEDIUM-1: Inference flooding/Cat 12 → DoS Critical; Context-window latency/Cat 13 Vector A → DoS Critical; Cost amplification/Cat 10 → model-theft Critical; Denial-of-wallet/Cat 11 Vector B → model-theft HIGH default + CRITICAL on Q3 2-condition; Context-window cost-amplification cross-vector → model-theft Cat 11 sub-pattern); D4 **no schema bump** (second BLP-01 detection feature reusing existing `D` and `LLM` prefixes after F-3; first at two-agent scope; explicit asymmetry to F-1 / F-2 / F-4 minor bumps; explicit asymmetry to ADR-031 D8 regex-alternation rule which does NOT apply when enrichment reuses existing prefixes; ADR-032 lines 84+182 forecast that F-5 will not need a schema bump — **fulfilled**); D5 no consumers-list edit (24-file zero-edit invariant on the 24 non-target detection-tier files preserved per ADR-023 lineage); D6 no functional orchestrator/dispatch edit (cosmetic Q2 annotation default-NO; both agents already fully registered in `dispatch-rules.md` and `orchestrator.md`); D7 **Pattern Category Disambiguation across two companion catalogs** (DoS Cat 9 vs Cat 12/13 boundary + model-theft Cat 6 vs Cat 10/11 boundary — explicit subsections in both companions to prevent dispatch-mode confusion); D8 no `source_attribution` populator wiring extension (F-A3 deferral); D9 public-only governance per SDR-001 Option C. **22-file zero-edit invariant** preserved (12 other agents + 7 infrastructure consumers + `human-trust-exploitation.md` + `tool-abuse.md` NOT-edit); F-5 = 28 detection-tier files post-F-4 inventory + 4 file edits + 0 net-new = 28 files post-merge. **F-5 strategic significance — BLP-01 Tier 1 5th feature delivered (after F-1..F-4); LLM10:2025 transitions Partial → Covered; OWASP LLM Top 10:2025 framework now 10/10 fully closed (combined with F-4's ASI09 closure: 20/20 OWASP AI top-10 entries covered across both LLM and Agentic frameworks); BLP-01 progress 8/11 features delivered (Foundation + F-1 + F-2 + F-3 + F-4 + F-5); Tier 1 fully delivered at 5/5; remaining 3 features are Tier 2 ML-extraction + Mobile bundles + post-Tier-1 follow-ons.** Heuristic A enrichment-branch second-execution at two-agent scope establishes the 5/5-dimension reduction stability across single-agent and two-agent scopes; load-bearing reuse signal for downstream Tier 2 features F-6 (ML attacks) + F-7 (Mobile attacks) where target taxonomies may also map cleanly to existing detection agents at multi-agent scope.

### Feature 241: F-8 + F-A3 Web/API Coverage Attestation + Populator Wiring [Tier 3] (Eleventh and Final BLP-01 Feature)

**PRD**: [241-web-api-coverage-attestation](../02_PRD/241-web-api-coverage-attestation-2026-04-29.md)
**Delivered**: 2026-05-01 | **PR**: #242 | **Tasks**: 84/84 complete (77 build + 7 close-out) | **Stories**: 3/3 passing
**Spec**: [specs/241-web-api-coverage-attestation/spec.md](../../../specs/241-web-api-coverage-attestation/spec.md)

- **US-241-1** (P0): Per-Finding Source Attribution Across Five Frameworks - As a tachi adopter reviewing a generated `tachi.security-report` PDF, I want each finding in my report to carry machine-readable source attribution across OWASP Top 10 / API Top 10 / MITRE ATT&CK / MITRE ATLAS / CWE so my stakeholders (CISOs, auditors, risk committees) can trace tachi findings back to the frameworks their compliance programs already use without me re-authoring the mapping. **Delivered**: every finding surfaced in the PDF report's `9. Coverage Attestation` section now renders its `source_attribution` entries as a per-finding attribution table (Finding ID, Title, Severity, OWASP refs, MITRE refs, NIST refs, CWE refs); the aggregate Coverage Attestation matrix renders a per-taxonomy view with %-coverage numbers and visual distinction for Covered / Partial / Planned / Out-of-Scope items, computed programmatically from `source_attribution` across all findings against the taxonomy inventory in `schemas/taxonomy/*.yaml`; running `/tachi.security-report` on any architecture that produces findings yields a non-empty Coverage Attestation section without any hand-curated input. **F-A3 populator-wiring debt CLOSED** across all 11 detection-tier hosts (`spoofing` + `tampering` + `info-disclosure` + `privilege-escalation` + `repudiation` + `denial-of-service` + `tool-abuse` + `data-poisoning` + `model-theft` + `prompt-injection` + `agent-autonomy` per Architect HIGH-A 11-host expansion). 8 baselines validated (`web-app` + `microservices` + `ascii-web-api` + `mermaid-agentic-app` + `free-text-microservice` + `maestro-reference` + new `mobile-banking-app/sample-report` + new `predictive-ml-app/sample-report`) all render the new pipeline-generated `9. Coverage Attestation` page with non-empty per-finding `source_attribution` rows and non-zero OWASP coverage percentages.
- **US-241-2** (P0): Six Partial Items Closed with Citation Evidence - As a tachi maintainer closing the BLP-01 blueprint, I want the six Partial items across OWASP Top 10:2021 and OWASP API Top 10:2023 to be re-classified with citation evidence so the coverage matrix has zero unexplained Partial items and every Covered item cites at least one agent plus one detection-pattern category per BLP-01 §8 Success Criteria. **Delivered**: A05 (Security Misconfiguration), A06 (Vulnerable and Outdated Components), API6 (Unrestricted Access to Sensitive Business Flows), API8 (Security Misconfiguration), API9 (Improper Inventory Management), API10 (Unsafe Consumption of APIs) — all six closed to Covered with pointers to concrete pattern categories inside skill-reference `detection-patterns.md` files plus citation-grounded Primary Source blocks. Each newly-closed Partial item produces at least one representative finding on a representative example architecture whose `source_attribution` resolves to the OWASP Top 10 or API Top 10 id in `schemas/taxonomy/owasp.yaml`. **CWE substitution rule** codified per ADR-037 D-7 extension: 8-CWE canonical mapping table for catalog-absent CWE-307/204/311/319/326/913/451/732 (12 distinct substitutions across T053+T054+T055 with 0 F-A2 referential-integrity errors). The completeness-verification commits are additive against existing skill reference files — no new agents, no schema changes beyond what F-A2 already landed. **OWASP five-framework total = 50/50 Covered** at F-241 close: LLM Top 10:2025 (10/10 from F-2 + F-5) + Agentic Top 10:2026 (10/10 from F-3 + F-4) + ML Top 10:2023 (10/10 from F-6) + Mobile Top 10:2024 (10/10 from F-7) + Web/API combined (10/10 from F-241).
- **US-241-3** (P0): Pipeline-Generated Coverage Percentages Replace Hand-Curated Matrix - As a tachi maintainer and future contributor, I want the §6 Coverage Matrix to become a historical artifact and the pipeline to publish MITRE ATT&CK and MITRE ATLAS coverage percentages as a first-class report artifact so future coverage claims are data-driven and auditable rather than hand-maintained blueprint prose. **Delivered**: the `9. Coverage Attestation` section renders per-framework coverage percentages for OWASP Top 10, OWASP API Top 10, OWASP LLM Top 10, OWASP Agentic Top 10, OWASP Mobile Top 10, OWASP ML Top 10, MITRE ATT&CK (Enterprise), MITRE ATLAS, NIST AI RMF, and CWE Top 25 — all computed at pipeline time from `source_attribution` across findings against the taxonomy inventory in `schemas/taxonomy/*.yaml`. **MITRE ATT&CK Enterprise expansion** 38 → 701 records (323 in-scope + 378 OOS via 7 verbatim T040 tactical-grouping rationale strings TA0005/7/8/9/10/11/40 + 2 derived TA0112+TA0043 curator extensions for post-spec STIX 2.1 update + 1 T1078.004 per-item OOS override). **MITRE ATLAS expansion** 12 → 30 records (all 30 in-scope). **Stream 4 aggregator extension** at `scripts/extract-report-data.py:_load_framework_yaml_records()` line 1073 (NOT line 1144 per Architect M-2 carry-forward) plus dual-emission `yaml_record_count` raw + `in_scope_yaml_record_count` filtered counters. **Stdlib-only module-load invariant preserved** by AST walk in `tests/scripts/test_pyyaml_deferred_import.py` (KB-042 codified). BLP-01 §6 Coverage Matrix annotated "historical — superseded by pipeline-generated attestation" at T061 Wave 6.2. **ADR-037** (Status: Accepted at squash commit `e8a5370` per Proposed → Accepted dual-commit lifecycle; SHA backfilled at Wave 6.3 T068 commit `8432cb5`) records 13 numbered Decisions D-1..D-13 documenting the 11-host F-A3 wiring scope, six Partial→Covered closures, ATT&CK/ATLAS expansion strategy, taxonomy YAML record-shape extension with `out_of_scope: bool` + `out_of_scope_rationale: str` fields, Stream 4 aggregator line 1073 anchor, KB-042 stdlib-only AST regression guard, KB-041 surgical Section 9 backfill asymmetric pattern (~60% wall-clock cost reduction vs full pipeline regen), zero schema bump (5th BLP-01 detection feature; first at 11-host scope), and dual-commit governance protocol third execution. **Heuristic A enrichment-branch saturation proof at 11-host scope (KB-039 extended)**: 5/5-dimension reduction confirmed at single-agent (F-3) → 2-agent (F-5) → 3-agent (F-6) → 4-or-5-agent (F-7) → 11-host (F-241; maximum tested). **F-241 strategic significance — BLP-01 11-feature initiative CLOSES at 11/11 features delivered; OWASP five-framework total reaches 50/50 Covered; F-A3 populator-wiring debt across ADR-032 + ADR-034 D-8 + ADR-035 D-10 + ADR-036 D-10 (four-feature deferral chain) closed in single 11-host wave; per-host edit cost remained linear (~1 file edit per host) at 11x scope, fulfilling ADR-035 + ADR-036 closing forward-scope-marker forecasts verbatim.** Future threat-coverage features inherit this attestation surface for free — any new pattern category added to any `detection-patterns.md` with a Primary Source block automatically feeds the Coverage Attestation section, so coverage expansion no longer requires blueprint-level bookkeeping.

### Feature 237: F-7 Mobile Top 10 Coverage Bundle [Tier 2] (OWASP Mobile Top 10:2024)

**PRD**: [237-mobile-top-10-coverage-bundle](../02_PRD/237-mobile-top-10-coverage-bundle-2026-04-28.md)
**Delivered**: 2026-04-29 | **PR**: #238 | **Tasks**: 73 build-phase tasks complete (close-out tasks T074-T082 executing post-merge per `/aod.deliver` flow) | **Stories**: 3/3 passing
**Spec**: [specs/237-mobile-top-10-coverage-bundle/spec.md](../../../specs/237-mobile-top-10-coverage-bundle/spec.md)

- **US-237-1** (P0): Mobile Threat Coverage Across Five Existing Host Agents - A security analyst threat-models a mobile-banking app, mobile-IoT companion app, mobile patient-records app, or hybrid web/mobile commerce application and expects tachi to surface findings covering the **full OWASP Mobile Top 10:2024 surface** (M1 improper credential usage, M2 inadequate supply chain security, M3 insecure authentication/authorization, M4 insufficient input/output validation, M5 insecure communication, M6 inadequate privacy controls, M7 insufficient binary protections, M8 security misconfiguration, M9 insecure data storage, M10 insufficient cryptography) through the existing `spoofing` (M1+M3), `tampering` (M2+M4+M7), `info-disclosure` (M5+M6+M9+M10), `privilege-escalation` (M8 privilege-gain variant), and `repudiation` (M8 accountability-loss variant) host agents — without a new mobile-platform agent, without fragmenting findings across eleven adjacencies, and without scope creep on the host agents' existing surfaces. Given a mobile-tier architecture exhibiting one or more Mobile Top 10 sub-pattern indicators (mobile credential storage in cleartext on local device, third-party mobile SDKs without checksum verification, exposed Activity/Service receivers, missing certificate pinning, PII in device-local caches, missing root/jailbreak detection, exposed debug endpoints in production builds, unencrypted SQLite, weak key derivation on PINs), running `/tachi.threat-model` emits ≥1 new finding per Mobile Top 10 row across the appropriate host agents (`S-{N}`/`T-{N}`/`I-{N}`/`E-{N}`/`R-{N}` IDs preserve STRIDE-tier prefix continuity); given a non-mobile architecture, the new Pattern Categories emit **zero findings** — pre-existing Pattern Categories on each host fire as they do today. **M8 dual-host disjoint architectural-tells operationalized** at the F-7 layer per ADR-036 D-4: privilege-gain variant (exposed admin/debug interfaces in production, default permissive ContentProvider exports, missing app-attestation enabling tampered-binary execution) routes to `privilege-escalation` host; accountability-loss variant (missing audit logging, disabled crash reporting, debug log leakage in production, missing tamper-evident timestamping) routes to `repudiation` host — same OWASP catalog entry surfaces with disjoint mitigation vocabularies on two distinct STRIDE-tier hosts. **M4 cross-agent boundary with F-1 `output-integrity`** operationalized per ADR-036 D-5: mobile IPC validation (Android Intent injection, iOS URL-scheme injection, deep-link parameter tampering, exposed ContentProvider) routes to `tampering` Category 12; LLM-output sanitization (XSS/SQLi/SSRF on LLM output flowing into execution sinks) remains owned by F-1's `output-integrity` agent — disjoint surface boundary prevents duplicate detection on hybrid LLM-plus-mobile architectures. On the new `examples/mobile-banking-app/` baseline (mobile-banking archetype with 4 FR-006 mobile-tier indicators engaged: mobile client process, credential-handling component using SharedPreferences/NSUserDefaults, secure-storage data store, mobile-backend API process, third-party mobile SDK integration, exposed debug endpoint), **16 net-new mobile-tier findings emerged on regen** spanning all 10 Mobile Top 10 rows across all 5 host agents — cohesive category rendering preserved (each finding renders in its STRIDE host's category section without fragmentation; M8 dual-host findings render adjacent in `privilege-escalation` and `repudiation` sections respectively).
- **US-237-2** (P0): Lean Enrichment Discipline Across Five Host Agents - A developer reading any new Mobile Top 10 finding (`S-{N}`/`T-{N}`/`I-{N}`/`E-{N}`/`R-{N}`) needs to address it in their mobile architecture and expects the `mitigation` field to name **specific platform-managed Keystore/Keychain mechanisms, certificate pinning libraries, mobile-IPC validation patterns, RASP integration, MASTG/MASVS-aligned secure-storage primitives, and mobile-cryptography APIs** matched to the detected Pattern Category — distinct from the host agents' generic web/server-tier mitigations — so the fix can be applied without inventing a mobile mitigation pattern from scratch or re-deriving from primary OWASP Mobile / MASTG / MASVS sources. Each emitted Mobile-tier finding's `mitigation` field names at least one specific mobile-aware mechanism: **M1 improper credential usage** → `Android Keystore / iOS Keychain platform-managed secure storage` / `biometric-bound key release for sensitive operations` / `no hardcoded secrets in shipped binaries`; **M2 mobile supply chain integrity** → `SDK signature verification` / `dependency manifest pinning with reproducible builds` / `app-store-only distribution` / `supplier-provenance review gate before SDK adoption`; **M3 insecure mobile authentication** → `server-side authorization enforcement` / `certificate pinning with rotation` / `refresh-token binding to device` / `biometric step-up on high-risk operations`; **M4 mobile IPC validation** → `explicit Intent component routing` / `URL-scheme allowlist with parameter validation` / `Android App Links / iOS Universal Links claim verification` / `ContentProvider permission scoping`; **M5 insecure mobile communication** → `cleartext-traffic prohibition in network security config` / `certificate pinning with backup-pin rotation` / `TLS 1.3 with strict cipher allowlist` / `HSTS-equivalent enforcement at app-level`; **M6 inadequate mobile privacy** → `data-minimization on caches with TTL enforcement` / `consent-gated telemetry with opt-out` / `FLAG_SECURE / equivalent screenshot prevention on PII screens` / `just-in-time permission prompts with graceful denial paths`; **M7 insufficient binary protections** → `root/jailbreak detection with policy-based response` / `RASP integration with attestation` / `ProGuard/R8 obfuscation on Android` / `bitcode + symbol-stripping on iOS` / `emulator-detection on payment and KYC flows`; **M8 security misconfiguration** (privilege-gain variant) → `production-build flag stripping debug code paths` / `ContentProvider/Activity export scoping with Android signature-level permissions` / `Play Integrity / DeviceCheck attestation gating` / `root-detection on security-critical UI flows`; **M8 security misconfiguration** (accountability-loss variant) → `structured audit logging on security-relevant mobile events with server-side persistence` / `production-build log-statement stripping (ProGuard/R8 rules)` / `tamper-evident timestamping on audit records` / `crash-reporting enablement with PII redaction`; **M9 insecure mobile data storage** → `SQLCipher / Realm encryption with platform-keyring-derived keys` / `EncryptedSharedPreferences (Android Jetpack) / Keychain-stored secrets (iOS)` / `allowBackup="false" on Android with sensitive data partitioning` / `internal-storage-only writes for sensitive files`; **M10 insufficient mobile cryptography** → `platform-provided key derivation (Argon2id / scrypt / PBKDF2 with ≥600k iterations)` / `platform crypto APIs only (no custom algorithms)` / `key derivation from platform-keyring-bound material` / `SecureRandom for all cryptographic randomness` / `AES-GCM and SHA-256+ as the minimum baseline`. Every emitted Mobile-tier finding's `references` array includes the appropriate `OWASP M{N}:2024` plus `MASTG-{section}` and `MASVS-{section}` (section-level granularity per Q4 default) where applicable. **MITRE ATT&CK Mobile catalog gap propagation**: 3 of 3 cited ATT&CK Mobile techniques (T1474 Supply Chain Compromise on M2, T1626 Abuse Elevation Control Mechanism on M7/M8 privilege-gain, T1398 Boot or Logon Initialization Scripts on M3 and M8 accountability-loss) are NOT in `schemas/taxonomy/mitre-attack.yaml` and ship as **prose-only** worked-example narratives explicitly absent from any `references` array entry across all 10 Pattern Categories and all 5 fixtures (3-of-3 prose-only worst-case scale per F-A2 referential-integrity contract; ADR-036 codifies the rule per F-5 T1496 + F-6 ATLAS-gap precedents). F-7 deliberately does **not** extend `source_attribution` populator wiring on the host agents — that scope belongs to F-A3 (deferred per `schemas/finding.yaml` lines 230-238 and ADR-028 Decision 6); Mobile Top 10 citations live in the prose-level `references:` array (existing field present in finding YAML schema since v1.0).
- **US-237-3** (P0): Backward Compatibility Preservation Under Largest BLP-01 Enrichment Scope - An adopter runs tachi on a non-mobile architecture (web app, traditional microservices, ASCII-format API description, Mermaid agentic app, free-text microservice, MAESTRO reference) and expects **byte-identical PDF output under `SOURCE_DATE_EPOCH=1700000000`** per ADR-021 invariant — F-7 must not regress any non-mobile baseline despite enriching 5 host agents simultaneously (the largest cross-agent enrichment scope in BLP-01 history). The mobile-tier topology gate per FR-006 (mobile client process AND mobile-tier indicator pair both required) guarantees zero Mobile Pattern Category emissions on non-mobile architectures, which guarantees unchanged downstream artifacts (`threats.md`, `risk-scores.md`, `compensating-controls.md`, `threat-report.md`, `threats.sarif`, all 6 infographic JPEGs, the assembled security-report PDF). **ADR-036** (Status: Accepted at squash commit `e962a0e` per Proposed → Accepted dual-commit lifecycle; 9th consecutive ADR per ADR-027/028/029/030/031/032/033/034/035/036 lineage) records 9-or-10 numbered Decisions covering D-1 enrichment-vs-new-agent at four-or-five-agent scope, D-2 additive-only edits across 10 host files (5 agent files + 5 companion `detection-patterns.md` files), D-3 canonical Mobile Top 10 sub-pattern → owning-agent mapping table populated COMPLETE with severity-hint annotation column (per ADR-035 D-3 precedent), D-4 M8 dual-host split decision (privilege-gain vs accountability-loss disjoint architectural-tells across `privilege-escalation` + `repudiation` hosts; second BLP-01 sub-pattern with cross-agent decomposition after F-5's Q1 SPLIT vector axis and F-6's ML06 corpus-vs-artifact axis — first at architectural-tell axis), D-5 M4 cross-agent boundary with F-1 `output-integrity` (mobile-IPC-input-side on `tampering` Cat 12 vs LLM-output-side on `output-integrity`; disjoint-tells preventing duplicate detection on hybrid LLM-plus-mobile architectures), D-6 **no schema bump** (fourth BLP-01 detection feature reusing existing `S` `T` `I` `E` `R` STRIDE prefixes after F-3 single-agent / F-5 two-agent / F-6 three-agent; first at four-or-five-agent scope; explicit asymmetry to F-1 / F-2 / F-4 minor bumps; explicit asymmetry to ADR-031 D8 regex-alternation rule which does NOT apply when enrichment reuses existing prefixes; ADR-035 closing forward-scope marker forecast that F-7 will not need a schema bump — **fulfilled**), D-7 ATT&CK Mobile catalog gap rule (3-of-3 prose-only at worst-case scale per F-A2 referential-integrity contract), D-8 Pattern Category Disambiguation across 5 companion catalogs (spoofing Cat N+1/N+2 vs Cat 1-N + tampering Cat 11/12/13 vs Cat 1-9 + info-disclosure Cat N+1..N+4 vs Cat 1-N + privilege-escalation Cat N+1 vs Cat 1-N + repudiation Cat N+1 vs Cat 1-N), D-9 no `source_attribution` populator wiring extension (F-A3 deferral), D-10 (if 10-decision structure adjudicated at plan day per architect MEDIUM-2) public-only governance per SDR-001 Option C. **F-7 strategic significance — BLP-01 Tier 2 second feature delivered + OWASP Mobile Top 10:2024 row 10/10 closure + OWASP four-framework total 40/40 milestone**: F-7 closes Mobile Top 10:2024 on the BLP-01 Coverage Matrix (10 rows transition Planned → Covered in a single bundle); BLP-01 progress: **10/11 features delivered** (Foundation + F-1 + F-2 + F-3 + F-4 + F-5 + F-6 + F-7); OWASP Mobile Top 10:2024 framework row coverage now **10/10**. Combined with F-4's OWASP Agentic Top 10:2026 row 10/10 + F-5's OWASP LLM Top 10:2025 row 10/10 + F-6's OWASP ML Top 10:2023 row 10/10, F-7 yields **OWASP four-framework total = 40/40 fully Covered** — the **second framework family closure milestone** after the AI-security family (LLM + Agentic + ML at 30/30 post-F-6). 6/6 byte-identical baselines preserved (`web-app`, `microservices`, `ascii-web-api`, `mermaid-agentic-app`, `free-text-microservice`, `maestro-reference`) under `SOURCE_DATE_EPOCH=1700000000` per ADR-021. Heuristic A enrichment-branch fourth execution at four-or-five-agent scope establishes the 5/5-dimension reduction stability across single-agent (F-3), two-agent (F-5), three-agent (F-6), and four-or-five-agent (F-7) scopes; only F-8 Web/API Tier 3 remains in the BLP-01 11-feature initiative.
