---
prd:
  number: 104
  topic: downstream-baseline-propagation
  created: 2026-04-08
  status: Approved
  type: feature
triad:
  pm_signoff: {agent: product-manager, date: 2026-04-08, status: APPROVED, notes: "PRD authored by PM — self-approved as drafter"}
  architect_signoff: {agent: architect, date: 2026-04-08, status: APPROVED_WITH_CONCERNS, notes: "4 findings (0 blocking): tachi_parsers.py unlisted, baseline detection sentinel, carry-forward UX, Section 8 producer ambiguity — all resolvable in spec"}
  techlead_signoff: {agent: team-lead, date: 2026-04-08, status: APPROVED_WITH_CONCERNS, notes: "3 concerns: tachi_parsers.py as 10th file, RESOLVED section decision needed before Wave 3, validation needs no-baseline regression test"}
source:
  idea_id: 104
  story_id: null
---

# Downstream Baseline Propagation - Product Requirements Document

**Status**: Approved
**Created**: 2026-04-08
**Author**: product-manager
**Reviewers**: architect, team-lead
**Priority**: P1
**Parent Feature**: 074 (Baseline-Aware Pipeline)

---

## Executive Summary

### The One-Liner
Make threat reports, infographics, and PDF security assessments aware of what changed since the last scan, so users see new threats highlighted and resolved threats acknowledged.

### Problem Statement
Feature 074 delivered baseline-aware behavior to the tachi pipeline: every finding is annotated with `delta_status` (`[NEW]`, `[UNCHANGED]`, `[UPDATED]`, `[RESOLVED]`), and upstream consumers (orchestrator, risk-scorer, control-analyzer) already use these annotations for score inheritance and incremental rescanning. However, all downstream consumers -- the threat-report agent, infographic agent, report-assembler agent, extraction scripts, and output templates -- are completely unaware of baseline data. This creates three concrete problems:

1. **RESOLVED findings leak into outputs**: Threats that have been remediated still appear in attack trees, infographics, and PDF reports, inflating threat counts and undermining user confidence in remediation tracking.
2. **UNCHANGED attack trees are regenerated**: Stable findings produce identical attack trees on every run instead of being carried forward, wasting compute and cluttering reports with redundant content.
3. **No delta visibility**: Users cannot distinguish new threats from carried-forward findings in any output format, defeating the purpose of baseline comparison.

### Proposed Solution
Propagate `delta_status` awareness to all nine downstream components: three agent instruction files, two extraction scripts, two command files, and two output schema templates. Each component will parse, filter, and annotate findings by delta status, enabling reports that communicate finding lifecycle (new discoveries, stable threats, resolved items).

### Success Criteria
- RESOLVED findings excluded from active threat counts in all output formats
- New findings visually distinguished from unchanged findings in reports and infographics
- Delta Summary section present in threat-report output
- Extraction scripts parse and expose delta_status fields to downstream consumers

### Timeline
Single implementation phase targeting completion within the current development cycle.

---

## Strategic Alignment

### Product Vision Alignment
**Reference**: [product-vision.md](../01_Product_Vision/product-vision.md)

Baseline-aware reporting directly supports tachi's mission as an automated threat modeling toolkit. Security teams run threat models iteratively -- each scan should communicate *what changed*, not just *what exists*. Without delta propagation, tachi's baseline feature (074) delivers half its value: upstream pipeline benefits from delta awareness, but the user-facing outputs (reports, infographics, PDFs) that security teams actually read do not.

### Dependency Context
This feature completes the baseline story started in Feature 074. The upstream pipeline (orchestrator, risk-scorer, control-analyzer) already produces `delta_status` annotations -- this PRD addresses the downstream gap.

---

## Target Users & Personas

### Primary Persona: Security Engineer
- **Role**: Runs periodic threat model scans on evolving architectures
- **Goal**: Quickly identify *new* attack surfaces introduced since last scan
- **Pain Point**: Current reports show all findings uniformly -- no way to tell what's new vs. what was already known, or what's been fixed

### Secondary Persona: Engineering Manager / CISO
- **Role**: Reviews security assessment PDFs for compliance and progress tracking
- **Goal**: Verify that remediation efforts are reducing risk over time
- **Pain Point**: PDF reports inflate threat counts with resolved findings, making it impossible to track remediation progress

---

## User Stories

### US-001: Delta-Aware Threat Report
**When** I run a baseline-compared threat model and review the narrative report,
**I want to** see findings grouped by lifecycle status (new, unchanged, updated, resolved),
**So I can** focus my remediation effort on genuinely new threats and confirm that resolved items are acknowledged.

**Acceptance Criteria**:
- **Given** a threats.md with delta_status annotations, **when** threat-report agent generates output, **then** the executive summary includes delta counts (e.g., "5 new, 12 unchanged, 2 updated, 3 resolved")
- **Given** findings with `delta_status: RESOLVED`, **when** attack trees are generated, **then** RESOLVED findings are excluded from attack tree generation
- **Given** findings with `delta_status: UNCHANGED`, **when** attack trees are generated, **then** UNCHANGED findings reuse baseline attack trees (carried forward) rather than regenerating
- **Given** a baseline-compared run, **when** the threat report is generated, **then** a Delta Summary section (Section 8) is present with lifecycle breakdown

**Priority**: P0
**Effort**: L

### US-002: Delta-Aware Infographics
**When** I generate threat infographics from a baseline-compared scan,
**I want to** see severity counts that exclude resolved findings and highlight new discoveries,
**So I can** present accurate, current-state threat posture visuals.

**Acceptance Criteria**:
- **Given** a threats.md with RESOLVED findings, **when** extract-infographic-data.py runs, **then** RESOLVED findings are excluded from severity distribution counts
- **Given** a threats.md with NEW findings, **when** infographic data is extracted, **then** the output includes a delta breakdown (new vs. unchanged vs. updated counts)
- **Given** a baseline-compared run, **when** the infographic command orchestrates generation, **then** Gemini prompts include delta context for visual emphasis

**Priority**: P0
**Effort**: M

### US-003: Delta-Aware PDF Security Report
**When** I generate a PDF security assessment from a baseline-compared scan,
**I want to** see finding detail pages that distinguish new threats from carried-forward ones and exclude resolved findings from active tables,
**So I can** deliver professional reports that accurately reflect the current threat landscape and remediation progress.

**Acceptance Criteria**:
- **Given** a threats.md with delta_status annotations, **when** extract-report-data.py runs, **then** the Typst data file includes delta_status per finding
- **Given** RESOLVED findings in the dataset, **when** the PDF is assembled, **then** RESOLVED findings appear in a separate "Resolved" section (not in active findings tables)
- **Given** NEW findings in the dataset, **when** the PDF is assembled, **then** NEW findings are visually badged or annotated in the findings table

**Priority**: P1
**Effort**: M

### US-004: Output Schema Delta Support
**When** downstream agents and scripts process threat model output,
**I want to** have standardized schema structures for delta data,
**So that** all consumers parse delta information consistently.

**Acceptance Criteria**:
- **Given** the threats.md output schema template, **when** a baseline-compared run completes, **then** Section 8 (Delta Summary) structure is defined with required fields
- **Given** the threat-report.md output schema template, **when** a baseline-compared report is generated, **then** baseline handling guidance is included

**Priority**: P0
**Effort**: S

---

## Functional Requirements

### FR-001: Threat-Report Agent Delta Awareness
**Description**: The threat-report agent must parse `delta_status` from input findings and produce delta-aware narrative output.

**Behavior by delta_status**:
- `NEW`: Generate fresh attack tree; highlight in narrative as new discovery
- `UNCHANGED`: Carry forward baseline attack tree (do not regenerate); note as stable in narrative
- `UPDATED`: Generate fresh attack tree; note changed context in narrative
- `RESOLVED`: Exclude from attack tree generation; include in Delta Summary section as remediated

**Output changes**:
- Executive Summary: Include delta counts
- Section 3 (Threat Analysis): Group findings by delta status
- Section 8 (Delta Summary): New section with lifecycle breakdown and remediation proof

### FR-002: Infographic Extraction Script Delta Parsing
**Description**: `extract-infographic-data.py` must parse `delta_status` from finding rows and expose delta-aware metrics.

**Output changes**:
- Severity distribution: Exclude RESOLVED from active counts
- Delta breakdown: Add `new_count`, `unchanged_count`, `updated_count`, `resolved_count` fields
- Top findings: Include `delta_status` field per finding

### FR-003: Report Extraction Script Delta Parsing
**Description**: `extract-report-data.py` must parse `delta_status` and include it in Typst data variables.

**Output changes**:
- Per-finding data: Include `delta_status` field
- Summary counts: Add delta-aware severity counts (active vs. resolved)
- Separate RESOLVED findings into their own list for distinct rendering

### FR-004: Infographic Agent & Command Delta Directives
**Description**: The infographic agent instruction file and command file must include baseline-aware directives for Gemini prompt construction and data interpretation.

**Behavior**:
- When delta data is present, infographic prompts emphasize new attack surfaces
- Severity badge coloring can optionally distinguish new vs. unchanged
- RESOLVED findings excluded from visual threat counts

### FR-005: Report Assembler & Command Delta Awareness
**Description**: The report-assembler agent and security-report command must handle delta-annotated data for PDF generation.

**Behavior**:
- Finding detail pages include delta status column/badge
- RESOLVED findings rendered in a separate section (not mixed with active findings)
- Executive summary page includes delta counts when available

### FR-006: Shared Parser Delta Support
**Description**: `scripts/tachi_parsers.py` contains `parse_threats_findings()` which hardcodes a fixed field set that excludes `delta_status`. This shared parser feeds both extraction scripts and must be updated first.

**Changes**:
- Add `delta_status` and `baseline_run_id` to the parsed field set
- Ensure parsed finding dictionaries include delta fields when present in input
- Maintain backward compatibility when delta fields are absent

### FR-007: Output Schema Template Updates
**Description**: Update output schema templates to define delta structures.

**Changes**:
- `threats.md` template: Add Section 8 (Delta Summary) with required structure
- `threat-report.md` template: Add baseline handling guidance and delta section format

### Backward Compatibility
All changes must be **backward compatible**. When no baseline is present (no `delta_status` fields in input), all components must behave exactly as they do today. Delta awareness activates only when delta data is detected.

---

## Non-Functional Requirements

### Backward Compatibility
- All nine affected files must maintain current behavior when no baseline data is present
- No breaking changes to existing output formats -- delta information is additive
- Extraction scripts must handle both baseline-aware and non-baseline inputs gracefully

### Consistency
- Delta-driven branching pattern must follow the precedent established in risk-scorer and control-analyzer (Feature 074)
- All downstream consumers must use the same `delta_status` enum values: `NEW`, `UNCHANGED`, `UPDATED`, `RESOLVED`

---

## Success Metrics

### Primary Metrics

**Metric 1**: Delta accuracy in outputs
- **Definition**: RESOLVED findings correctly excluded from active threat counts across all output formats
- **Target**: 100% accuracy (zero RESOLVED findings in active counts)

**Metric 2**: Delta visibility in reports
- **Definition**: Presence of delta annotations (section 8, delta counts, lifecycle grouping) in threat-report output when baseline data exists
- **Target**: All three output formats (report, infographic, PDF) include delta information

### Validation
- Run baseline-compared threat model on second-brain-mcp (same test case that uncovered the gap)
- Compare output before/after: verify RESOLVED findings excluded, NEW findings highlighted, Delta Summary present

---

## Scope & Boundaries

### In Scope (P0/P1)

- **Threat-report agent**: Delta-aware narrative, attack tree carry-forward, Section 8 Delta Summary
- **Infographic agent + command**: Delta-filtered severity counts, delta context in Gemini prompts
- **Report-assembler agent + command**: Delta column in PDF tables, RESOLVED separation
- **Extraction scripts**: `delta_status` parsing in both `extract-infographic-data.py` and `extract-report-data.py`
- **Output schema templates**: Section 8 structure in threats.md, baseline guidance in threat-report.md

### Out of Scope

- **Upstream pipeline changes**: Orchestrator, risk-scorer, control-analyzer already handle delta (Feature 074)
- **SARIF delta output**: SARIF format changes for delta awareness (separate future feature)
- **Interactive delta comparison UI**: Visual diff between baseline and current run
- **Baseline storage/management**: How baselines are stored and retrieved (already handled by orchestrator)

### Assumptions
- Feature 074 is fully delivered and stable (confirmed: delivered 2026-04-01)
- `delta_status` field is present in finding schema v1.2 (confirmed)
- Extraction scripts can detect baseline presence by checking for `delta_status` fields in input

---

## Risks & Dependencies

### Technical Risks

**Risk 1**: Attack tree carry-forward complexity
- **Likelihood**: Medium
- **Impact**: Medium
- **Mitigation**: Start with simple approach -- skip regeneration for UNCHANGED findings and note "carried forward from baseline" rather than embedding full baseline tree content

**Risk 2**: Extraction script backward compatibility
- **Likelihood**: Low
- **Impact**: High
- **Mitigation**: Guard all delta logic behind presence checks (`if delta_status in row`)

### Dependencies

**Internal Dependencies**:
- **Feature 074 (Baseline-Aware Pipeline)**: Must be stable and complete (confirmed delivered)
- **Finding schema v1.2**: `delta_status` and `baseline_run_id` fields must be in schema (confirmed)

**Dependency Graph**:
```
Feature 074 (Baseline-Aware Pipeline) [DELIVERED]
  └─ Feature 104 (Downstream Baseline Propagation) [THIS PRD]
       ├─ Threat-report agent
       ├─ Infographic agent + extraction script
       └─ Report-assembler agent + extraction script
```

---

## Open Questions

- [x] Which test case validates the fix? → second-brain-mcp baseline comparison (April 8 vs March 31 runs)
- [ ] Should RESOLVED findings appear in a dedicated "Remediated" section in PDF, or be fully excluded? (Recommendation: dedicated section for audit trail) - product-manager - 2026-04-10

---

## References

### Product Documentation
- Product Vision: [product-vision.md](../01_Product_Vision/product-vision.md)
- Parent PRD: [074 - Baseline-Aware Pipeline](074-baseline-aware-pipeline-2026-03-31.md)

### Technical Documentation
- Constitution: [constitution.md](../../../.aod/memory/constitution.md)
- Finding Schema: `schemas/finding.yaml` (v1.2, includes `delta_status` field)

### Source
- GitHub Issue: #104 — uncovered during user testing of Feature 074 delivery
- Evidence: April 8 vs March 31 threat model runs on second-brain-mcp

---
