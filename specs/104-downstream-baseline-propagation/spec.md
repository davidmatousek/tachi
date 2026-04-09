---
prd_reference: docs/product/02_PRD/104-downstream-baseline-propagation-2026-04-08.md
triad:
  pm_signoff:
    agent: product-manager
    date: 2026-04-08
    status: APPROVED
    notes: "All 7 PRD functional requirements covered (FR-001–FR-007 mapped to 15 spec FRs). All 4 PRD user stories addressed with expanded acceptance criteria. Success criteria measurable and aligned. Architect concerns from PRD review resolved: tachi_parsers.py addressed as FR-001/FR-002, carry-forward UX clarified in US-001 scenario 3, Section 8 structure defined in FR-013."
  architect_signoff: null
  techlead_signoff: null
---

# Feature Specification: Downstream Baseline Propagation

**Feature Branch**: `104-downstream-baseline-propagation`
**Created**: 2026-04-08
**Status**: Draft
**PRD Reference**: `docs/product/02_PRD/104-downstream-baseline-propagation-2026-04-08.md`

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Delta-Aware Threat Report (Priority: P0)

A security engineer runs a baseline-compared threat model on an evolving architecture. When they open the narrative threat report, they see findings grouped by lifecycle status: new discoveries are highlighted for immediate attention, unchanged findings are noted as stable, and resolved findings are acknowledged as remediated. The executive summary includes delta counts so the engineer can instantly assess what changed. A dedicated Delta Summary section provides a lifecycle breakdown with remediation proof.

**Why this priority**: The threat report is the primary user-facing output. Without delta awareness here, users cannot distinguish new attack surfaces from known threats, defeating the purpose of baseline comparison. This is the highest-impact gap identified in Feature 074 delivery testing.

**Independent Test**: Run a baseline-compared threat model on second-brain-mcp (April 8 vs March 31 runs). Open the generated threat-report.md and verify delta counts in the executive summary, lifecycle grouping in threat analysis, attack tree carry-forward for UNCHANGED findings, and Section 8 Delta Summary presence.

**Acceptance Scenarios**:

1. **Given** a threats.md with delta_status annotations across all four statuses, **When** the threat-report agent generates output, **Then** the executive summary includes delta counts (e.g., "5 new, 12 unchanged, 2 updated, 3 resolved")
2. **Given** findings with `delta_status: RESOLVED`, **When** attack trees are generated, **Then** RESOLVED findings are excluded from attack tree generation
3. **Given** findings with `delta_status: UNCHANGED`, **When** attack trees are generated, **Then** UNCHANGED findings note "carried forward from baseline" rather than regenerating an identical attack tree
4. **Given** findings with `delta_status: UPDATED`, **When** attack trees are generated, **Then** UPDATED findings receive fresh attack trees with a note indicating changed context
5. **Given** a baseline-compared run, **When** the threat report is generated, **Then** a Delta Summary section is present with finding lifecycle breakdown and baseline reference
6. **Given** a run with no baseline (first scan), **When** the threat report is generated, **Then** the output is identical to current behavior (no delta sections, no grouping)

---

### User Story 2 - Delta-Aware Infographics (Priority: P0)

A security engineer generates threat infographics from a baseline-compared scan to present to stakeholders. The severity distribution accurately reflects the current threat posture by excluding resolved findings from active counts. New discoveries are emphasized so stakeholders can see what requires immediate attention. A delta breakdown provides new, unchanged, updated, and resolved counts.

**Why this priority**: Infographics are the primary visual communication tool for non-technical stakeholders. Inflated severity counts from resolved findings undermine credibility and misrepresent the current threat posture.

**Independent Test**: Run the infographic pipeline on a threats.md file containing RESOLVED findings. Verify the severity distribution excludes RESOLVED findings from active counts and the delta breakdown fields are present in the extracted data.

**Acceptance Scenarios**:

1. **Given** a threats.md with RESOLVED findings, **When** the infographic extraction script runs, **Then** RESOLVED findings are excluded from severity distribution counts
2. **Given** a threats.md with NEW findings, **When** infographic data is extracted, **Then** the output includes delta breakdown fields (new_count, unchanged_count, updated_count, resolved_count)
3. **Given** a baseline-compared run, **When** the infographic command orchestrates generation, **Then** prompts include delta context for visual emphasis of new attack surfaces
4. **Given** a run with no baseline, **When** the infographic pipeline runs, **Then** output is identical to current behavior (all findings counted in severity distribution, no delta breakdown)

---

### User Story 3 - Delta-Aware PDF Security Report (Priority: P1)

An engineering manager generates a PDF security assessment to share with leadership or compliance reviewers. The PDF finding tables distinguish new threats from carried-forward ones. Resolved findings appear in a separate section for audit trail rather than inflating active threat counts. The executive summary page includes delta counts when available.

**Why this priority**: PDF reports are the formal compliance deliverable. While still critical, this builds on the extraction script changes from US-002 and extends them to the PDF rendering layer.

**Independent Test**: Generate a PDF security report from a threats.md with delta_status annotations. Verify RESOLVED findings appear in a separate section, NEW findings are visually badged, and the executive summary includes delta counts.

**Acceptance Scenarios**:

1. **Given** a threats.md with delta_status annotations, **When** the report extraction script runs, **Then** the Typst data file includes delta_status per finding
2. **Given** RESOLVED findings in the dataset, **When** the PDF is assembled, **Then** RESOLVED findings appear in a separate "Resolved Findings" section, not in active findings tables
3. **Given** NEW findings in the dataset, **When** the PDF is assembled, **Then** NEW findings are visually annotated or badged in the findings table
4. **Given** delta data available, **When** the PDF executive summary page is rendered, **Then** delta counts are included
5. **Given** no baseline data, **When** the PDF is generated, **Then** output is identical to current behavior (no resolved section, no delta badges)

---

### User Story 4 - Shared Parser and Schema Delta Support (Priority: P0)

A developer extending the tachi pipeline relies on the shared parser (`tachi_parsers.py`) and output schema templates to understand finding data structures. The shared parser exposes delta_status and baseline_run_id fields when present, and the output schema templates define the Section 8 (Delta Summary) structure so all consumers parse delta information consistently.

**Why this priority**: The shared parser is the critical dependency for both extraction scripts. Without this, no downstream consumer can access delta data. Schema templates define the contract that all agents and scripts follow.

**Independent Test**: Call `parse_threats_findings()` on a threats.md containing delta_status annotations. Verify the returned finding dictionaries include delta_status and baseline_run_id fields. Call it on a pre-074 threats.md and verify identical behavior to current output.

**Acceptance Scenarios**:

1. **Given** a threats.md with delta_status columns, **When** `parse_threats_findings()` is called, **Then** returned finding dictionaries include `delta_status` and `baseline_run_id` fields
2. **Given** a threats.md without delta_status columns (pre-074), **When** `parse_threats_findings()` is called, **Then** returned finding dictionaries are identical to current output (no delta fields)
3. **Given** the threats.md output schema template, **When** reviewed, **Then** Section 8 (Delta Summary) structure is defined with required fields (lifecycle counts, baseline reference, remediation proof)
4. **Given** the threat-report.md output schema template, **When** reviewed, **Then** baseline handling guidance and delta section format are included

---

### Edge Cases

- What happens when a threats.md has some findings with delta_status and others without? Each finding is treated independently; findings without delta_status default to NEW behavior.
- What happens when baseline.source is present in frontmatter but no findings have delta_status annotations? Treat as a stateless run with a warning — the baseline was detected but findings were not annotated.
- What happens when delta_status contains an unrecognized value? Treat the finding as NEW with a warning logged, preserving forward compatibility.
- What happens when the shared parser is updated but extraction scripts are not yet modified? The parser exposes delta fields; extraction scripts that do not use them simply ignore the extra fields — no breakage.
- What happens when only some downstream consumers are updated? Each consumer operates independently — partial updates do not break the pipeline. Consumers that lack delta awareness continue to behave as they do today.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The shared parser (`parse_threats_findings()`) MUST include `delta_status` and `baseline_run_id` in returned finding dictionaries when those fields are present in the input
- **FR-002**: The shared parser MUST return identical output to current behavior when delta fields are absent in the input (backward compatibility)
- **FR-003**: The threat-report agent MUST parse `delta_status` from input findings and branch behavior accordingly: generate fresh attack trees for NEW and UPDATED findings, carry forward baseline notation for UNCHANGED findings, and exclude RESOLVED findings from attack tree generation
- **FR-004**: The threat-report agent MUST include delta counts in the executive summary when delta data is present
- **FR-005**: The threat-report agent MUST produce a Delta Summary section (Section 8) with lifecycle breakdown when delta data is present
- **FR-006**: The infographic extraction script MUST exclude RESOLVED findings from active severity distribution counts
- **FR-007**: The infographic extraction script MUST output delta breakdown fields (new_count, unchanged_count, updated_count, resolved_count) when delta data is present
- **FR-008**: The infographic agent and command MUST include delta context in generation prompts when delta data is present, emphasizing new attack surfaces
- **FR-009**: The report extraction script MUST include delta_status per finding in Typst data variables
- **FR-010**: The report extraction script MUST separate RESOLVED findings into a distinct list for separate rendering
- **FR-011**: The report-assembler agent and command MUST render RESOLVED findings in a separate section, not in active findings tables
- **FR-012**: The report-assembler agent and command MUST visually annotate NEW findings in the findings table
- **FR-013**: The threats.md output schema template MUST define Section 8 (Delta Summary) structure with required fields
- **FR-014**: The threat-report.md output schema template MUST include baseline handling guidance and delta section format
- **FR-015**: All ten components MUST maintain current behavior when no baseline data is present (no delta_status fields in input)

### Key Entities

- **Finding**: A single threat finding with lifecycle metadata. Key attributes: finding ID, component, threat description, risk level, delta_status (NEW/UNCHANGED/UPDATED/RESOLVED), baseline_run_id
- **Delta Summary**: Aggregated lifecycle breakdown of findings. Key attributes: new count, unchanged count, updated count, resolved count, baseline reference, remediation proof
- **Baseline**: Reference point for comparison. Key attributes: source file, date, finding count, run ID

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Zero RESOLVED findings appear in active threat counts across all three output formats (threat report, infographic, PDF) — 100% accuracy
- **SC-002**: All three output formats include delta annotations (executive summary counts, delta breakdown, lifecycle grouping) when baseline data is present
- **SC-003**: Section 8 (Delta Summary) is present in threat-report output for every baseline-compared run
- **SC-004**: NEW findings are visually distinguished from UNCHANGED findings in all output formats
- **SC-005**: Running the pipeline without a baseline produces output identical to pre-Feature-104 behavior (backward compatibility regression test passes)
- **SC-006**: The second-brain-mcp baseline comparison test case (April 8 vs March 31 runs) produces correct delta annotations across all output formats

## Assumptions

- Feature 074 (Baseline-Aware Pipeline) is fully delivered and stable (confirmed delivered 2026-04-01)
- The finding schema v1.2 includes `delta_status` and `baseline_run_id` fields (confirmed in `schemas/finding.yaml`)
- Baseline presence is detected via `baseline.source` in frontmatter (not per-finding scanning), following ADR-018 guidance
- The delta-driven branching pattern established in Feature 074 (risk-scorer and control-analyzer agents) is the canonical pattern to follow
- RESOLVED findings should appear in a dedicated "Resolved" section (not fully excluded) for audit trail purposes
- SARIF delta output is out of scope (separate future feature)
- Attack tree "carry-forward" for UNCHANGED findings means noting "carried forward from baseline" rather than embedding full baseline tree content

## Scope Boundaries

### In Scope
- Ten downstream components: 3 agent instruction files, 2 extraction scripts, 2 command files, 2 output schema templates, 1 shared parser
- Delta-driven branching (NEW, UNCHANGED, UPDATED, RESOLVED) in all ten components
- Backward compatibility when no baseline data is present
- Section 8 (Delta Summary) in threat-report output and schema templates

### Out of Scope
- Upstream pipeline changes (orchestrator, risk-scorer, control-analyzer — already handled by Feature 074)
- SARIF delta output format changes
- Interactive delta comparison UI
- Baseline storage and management (handled by orchestrator)
- Changes to the finding schema itself (v1.2 already includes delta fields)

## Dependencies

- **Feature 074** (Baseline-Aware Pipeline): Must be stable and complete (confirmed)
- **Finding schema v1.2**: delta_status and baseline_run_id fields must be present (confirmed)
- **tachi-shared skill**: Downstream consumers reference shared definitions for severity bands, STRIDE categories, and finding format
