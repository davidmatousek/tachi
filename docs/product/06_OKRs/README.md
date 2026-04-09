# OKRs (Objectives and Key Results) - tachi

**Last Updated**: 2026-04-08
**Owner**: Product Manager (product-manager)
**Status**: Template - Complete after MVP launch

---

## When to Create This

**Create OKRs AFTER your MVP launches and you have baseline metrics.**

Before MVP:
- You don't have baseline numbers to improve
- Your key metrics may not be measurable yet
- Focus should be on shipping, not measuring

**Pre-MVP Goal**: Launch MVP
**Post-MVP**: Set quarterly OKRs based on real usage data

**First OKRs**: Typically set 4-6 weeks after MVP launch when you have initial metrics.

> **AOD Lifecycle Note**: OKR documents can be scaffolded via `/aod.okrs`, which
> generates a standard OKR template (Objective, Key Results, Initiatives) in this
> directory with PM sign-off. `/aod.define` reads current OKRs for PRD alignment,
> and `DOCS_TO_UPDATE_AFTER_NEW_FEATURE.md` includes OKR progress as a checklist
> item during `/aod.deliver`. You can still create and maintain OKR files manually.

---

## Overview

OKRs align the team around measurable goals. They answer:
- **Objective**: What do we want to achieve? (qualitative)
- **Key Results**: How do we know we achieved it? (quantitative)

---

## OKR Template

```markdown
# tachi OKRs - YYYY-QN

**Quarter**: [Q1/Q2/Q3/Q4] YYYY
**Status**: [Planning | In Progress | Complete]
**Review Date**: [YYYY-MM-DD]

## Objective 1: [Qualitative Goal]

**Why This Matters**: [Alignment with product vision]

### Key Result 1.1: [Measurable Outcome]
- **Baseline**: [Starting value]
- **Target**: [End of quarter goal]
- **Current**: [Current progress]
- **Status**: 🟢 On Track | 🟡 At Risk | 🔴 Off Track
- **Owner**: [Team member]

### Key Result 1.2: [Another Measurable Outcome]
[Same structure]

## Objective 2: [Another Qualitative Goal]
[Same structure]

---

## Progress Tracking

**Week of [Date]**:
- KR 1.1: [Update]
- KR 1.2: [Update]

**Risks**:
- [Risk 1]

**Actions**:
- [ ] [Action item to address risk]
```

---

## OKR Best Practices

### Objectives (Qualitative)
- ✅ Inspiring and motivational
- ✅ Aligned with product vision
- ✅ Achievable but ambitious
- ❌ Not a task list

**Example Good Objectives**:
- "Become the go-to platform for [user segment]"
- "Delight users with exceptional [experience]"
- "Establish market leadership in [category]"

### Key Results (Quantitative)
- ✅ Specific and measurable
- ✅ Time-bound (end of quarter)
- ✅ 70-80% achievable (stretch goal)
- ❌ Not activities (use metrics)

**Example Good Key Results**:
- "Increase active users from 1,000 to 5,000"
- "Achieve NPS score of 50+"
- "Reduce churn from 10% to 5%"

---

## Integration with Product Workflow

### OKRs Drive PRDs
- Each PRD should support at least one key result
- PRD success metrics align with OKR key results
- PRD prioritization based on OKR impact

### OKRs Inform Roadmap
- Roadmap phases deliver on quarterly OKRs
- Feature prioritization based on OKR contribution
- Roadmap adjusts if OKRs change

---

## Review Cadence

### Weekly Check-In (15 min)
- Update key result progress
- Identify blockers
- Adjust tactics if needed

### End of Quarter Review (2 hours)
- Score all key results (0.0 - 1.0 scale)
- Document learnings
- Plan next quarter OKRs

---

**Template Instructions**: Create a new OKR file each quarter (YYYY-QN.md). Delete this message after creating your first OKR document.

---

## Feature Delivery Log

> **Purpose**: Track feature deliveries for OKR alignment once quarterly OKRs are established.
> Features listed here should be mapped to Key Results when OKRs are created.

| Date | Feature | PRD | Impact |
|------|---------|-----|--------|
| 2026-03-21 | F-001: Project Skeleton & Interface Contract | [001](../02_PRD/001-project-skeleton-interface-contract-2026-03-21.md) | Foundation layer complete: 11 threat agent prompts, interface contract, output template, 3 schemas, 3 examples. Unblocks F-002 through F-010. |
| 2026-03-21 | F-003: Orchestrator Agent | [003](../02_PRD/003-orchestrator-agent-2026-03-21.md) | Central orchestrator agent prompt: parses 5 architecture formats, dispatches to STRIDE and AI threat agents via STRIDE-per-Element and keyword matching, assembles structured threats.md output. Unblocks F-003 (STRIDE Agents), F-004 (AI Agents), F-005 (Dedup & Risk Rating), F-009 (Platform Adapters). |
| 2026-03-22 | F-005: STRIDE Threat Agents | [005](../02_PRD/005-stride-threat-agents-2026-03-21.md) | 6 validated STRIDE threat agents (spoofing, tampering, repudiation, info-disclosure, denial-of-service, privilege-escalation) with AI-specific threat patterns, STRIDE-per-Element matrix targeting, and OWASP/CWE/MITRE ATT&CK references. Updated 3 example threat models. Unblocks F-004 (AI Agents). |
| 2026-03-22 | F-010: Deduplication & Risk Rating | [010](../02_PRD/010-deduplication-risk-rating-2026-03-22.md) | Cross-agent finding correlation with 5 deterministic rules (STRIDE-to-AI pairs), deduplicated coverage matrix with three-state cell model, OWASP 3x3 risk calibration matrix in output, schema v1.1. Completes Phase 1 Foundation pipeline. Unblocks F-009 (Platform Adapters). |
| 2026-03-22 | F-012: SARIF Output Generation | [012](../02_PRD/012-sarif-output-generation-2026-03-22.md) | SARIF 2.1.0 output co-generated with threats.md during Phase 4 (Assess). Finding IR mapped to SARIF results with 8 rule definitions (6 STRIDE + 2 AI), CVSS-aligned severity levels, correlated finding representation via relatedLocations, component navigation via logicalLocations, and stable partialFingerprints for cross-run tracking. Enables GitHub Code Scanning, VS Code SARIF Viewer, and Azure DevOps integration. Unblocks F-009 (Platform Adapters — SARIF upload automation). |
| 2026-03-23 | F-015: Threat Report Agent & Attack Trees | [015](../02_PRD/015-threat-report-agent-attack-trees-2026-03-23.md) | Narrative threat report with executive summary, Mermaid attack trees for Critical/High findings, remediation roadmap. Phase 5 (Report) in orchestrator pipeline. |
| 2026-03-23 | F-018: Threat Infographic Agent | [018](../02_PRD/018-threat-infographic-agent-2026-03-23.md) | Visual infographic agent producing threat-infographic-spec.md with risk distribution, coverage heat map, top findings summary, and CVSS color palette. Optional Gemini API image generation. Phase 6 (Infographic) in orchestrator pipeline with opt-out support. Completes the reporting layer: structured analysis (F-005/F-007) -> narrative report (F-015) -> visual communication (F-018). |
| 2026-03-23 | F-024: Example Threat Models | [024](../02_PRD/024-example-threat-models-2026-03-23.md) | 3 end-to-end example threat models (web-app, agentic-app, microservices) with architecture diagrams and complete threat model outputs matching schema v1.1. Demonstrates STRIDE, AI threat agents, and OWASP cross-references. 5 user stories delivered. |
| 2026-03-27 | F-035: Quantitative Risk Scoring | [035](../02_PRD/035-quantitative-risk-scoring-2026-03-27.md) | Four-dimensional quantitative risk scoring (CVSS base + exploitability + scalability + reachability) with composite scores, governance fields, dual output formats (risk-scores.md + risk-scores.sarif). |
| 2026-03-28 | F-036: Compensating Controls Analysis | [036](../02_PRD/036-compensating-controls-2026-03-27.md) | Codebase control detection with file:line evidence, compensating control recommendations, coverage matrix, residual risk calculation, and control effectiveness assessment. |
| 2026-03-28 | F-039: Standalone /tachi.infographic Command | [039](../02_PRD/039-standalone-infographic-command-2026-03-28.md) | Standalone `/tachi.infographic` command with auto-detection of richest data source (risk-scores.md preferred), explicit file path override, template selection. Phase 6 removed from `/tachi.threat-model` pipeline. All platform adapters updated to 5-phase pipeline. |
| 2026-03-28 | F-045: End-to-End tachi Instruction Manual | [045](../02_PRD/045-instruction-manual-2026-03-28.md) | Comprehensive developer guide covering the full 4-command pipeline (`/tachi.threat-model` -> `/tachi.risk-score` -> `/tachi.compensating-controls` -> `/tachi.infographic`). Includes Quick Start (first threat model in 5 minutes), pipeline walkthrough with OpenClaw worked example, output interpretation for all 12+ artifacts, and prompt spec for consistent regeneration. First documentation-focused deliverable after core pipeline completion. |
| 2026-03-28 | F-048: Infographic Tiered Detection & Residual Risk | [048](../02_PRD/048-infographic-tiered-detection-residual-risk-2026-03-28.md) | Three-tier data source auto-detection for `/tachi.infographic` (compensating-controls.md > risk-scores.md > threats.md), residual risk extraction from compensating controls Coverage Matrix, progressive enhancement tips at each pipeline tier, and risk label distinction (Residual Risk / Inherent Risk / Severity) across both infographic templates. Completes the visualization layer of the composable pipeline. |
| 2026-03-28 | F-053: Risk Reduction Funnel | [053](../02_PRD/053-risk-reduction-funnel-2026-03-28.md) | New `risk-funnel` infographic template visualizing progressive risk reduction through the tachi pipeline as a 4-tier vertical funnel (threats identified -> inherent risk scored -> controls applied -> residual risk). Supports graceful degradation: 4-tier from compensating-controls.md, 3-tier from risk-scores.md, 1-tier from threats.md. Metrics sidebar with risk reduction percentage and control coverage. |
| 2026-03-30 | F-067: Deterministic Report Data Extraction | [067](../02_PRD/067-deterministic-report-data-extraction-2026-03-30.md) | Replaced LLM-based markdown parsing with deterministic Python script (scripts/extract-report-data.py) for `/tachi.security-report` data extraction. 3-tier severity source selection, internal consistency validation, scope data extraction. Report-assembler agent updated to invoke script instead of inline parsing. Fixes non-deterministic output where identical inputs produced varying severity counts (0-20 Critical) and risk levels (HIGH/CRITICAL). |
| 2026-03-30 | F-071: Deterministic Infographic Extraction | [071](../02_PRD/071-deterministic-infographic-extraction-2026-03-30.md) | Replaced LLM-based data extraction in threat-infographic agent with deterministic Python script (scripts/extract-infographic-data.py). Shared tachi_parsers.py module extracted from extract-report-data.py. Produces byte-identical JSON output for baseball card, system architecture, and risk funnel templates. Ensures cross-output consistency between infographics and security reports. Completes deterministic extraction across all tachi pipelines. |
| 2026-03-31 | F-075: Tachi Agent Best Practices | [075](../02_PRD/075-tachi-agent-best-practices-2026-03-31.md) | Extracted domain knowledge from 3 methodology agents (orchestrator, risk-scorer, control-analyzer) into on-demand skill files (tachi-orchestration, tachi-risk-scoring, tachi-control-analysis). Audited all 17 tachi agents for Claude 4.6 prompting best practices. Created shared _TACHI_AGENT_BEST_PRACTICES.md with tier caps and compliance table. Trimmed threat-report to 800-line cap. Unblocks #74 (baseline-aware pipeline). |
| 2026-04-01 | F-074: Baseline-Aware Pipeline | [074](../02_PRD/074-baseline-aware-pipeline-2026-03-31.md) | Baseline-aware threat detection pipeline with 4-phase orchestration (carry-forward, isolated discovery, merge/dedup, coverage gate). Correlates findings across runs with stable IDs via SARIF fingerprints. Delta annotations (`[NEW]`, `[UNCHANGED]`, `[UPDATED]`, `[RESOLVED]`) on all outputs. Coverage checklists per STRIDE category. Extended orchestrator, risk-scorer, and control-analyzer agents. New coverage-checklists schema. Updated all output templates and SARIF properties. Unblocks #55 (Security Progression Summary). |
| 2026-04-02 | F-078: Agent Context Optimization | [078](../02_PRD/078-agent-context-optimization-2026-04-01.md) | Restructured 6 tachi agents (orchestrator, risk-scorer, control-analyzer, report-assembler, threat-report, threat-infographic) from monolithic prompts to lean definitions with on-demand skill references. Created 4 skill directories (tachi-orchestration, tachi-risk-scoring, tachi-report-assembly, tachi-shared) with 25+ granular reference files. Added explicit model fields to all 17 agent definitions. Reduced agent prompt sizes by 40-60%. Zero regression on threat model outputs. |
| 2026-04-06 | F-086: Automated Release Tagging via GitHub Actions | [086](../02_PRD/086-automated-release-tagging-via-github-actions-2026-04-06.md) | Google release-please GitHub Action for automated version tagging from conventional commits. Deliverables: release-please.yml workflow, release-please-config.json, .release-please-manifest.json (baseline v4.0.0), README Releases section. Eliminates manual `git tag` commands; maintainer controls release timing via Release PR merge. |
| 2026-04-08 | F-084: MAESTRO Layer Mapping | [084](../02_PRD/084-maestro-layer-mapping-2026-04-07.md) | CSA MAESTRO seven-layer taxonomy overlay for all threat findings. New schema field, shared reference, orchestrator keyword classification in Phase 1, SARIF tags, downstream agent propagation, layer-based risk summary. All 6 example outputs regenerated. 4 user stories delivered. |
| 2026-04-08 | F-104: Downstream Baseline Propagation | [104](../02_PRD/104-downstream-baseline-propagation-2026-04-08.md) | Propagates baseline delta_status downstream through threat-report, infographic, and PDF report pipelines. RESOLVED findings excluded from active counts, NEW findings highlighted, Delta Summary section in reports. Shared parser updated for delta extraction. Completes the baseline story started in F-074. 4 user stories delivered. |
| 2026-04-09 | F-112: Attack Path Pages in Security Report PDF | [112](../02_PRD/112-attack-path-pages-in-pdf-2026-04-09.md) | Dedicated attack path visualization pages in PDF security reports. Extraction pipeline parses attack trees, renders Mermaid diagrams to PNG, feeds structured data to Typst template. Conditional inclusion gated by has-attack-trees boolean. Backward compatible with existing reports. 4 user stories delivered. |
