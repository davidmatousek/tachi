---
triad:
  pm_signoff:
    agent: product-manager
    date: 2026-03-28
    status: APPROVED
    notes: "16/16 FRs covered. All 3 user stories implemented. No scope creep. Phasing sound (command-first, then agent). Backward compatibility preserved through hierarchy insertion and graceful fallthrough."
  architect_signoff:
    agent: architect
    date: 2026-03-28
    status: APPROVED_WITH_CONCERNS
    notes: "ADR-010, ADR-014, ADR-016 verified PASS. Pattern consistency with Feature 039 PASS. 3 findings: (M) plan should specify compensating-controls frontmatter values for data_source_type and source_file; (L) Coverage Matrix actual column header is 'Residual Severity' not 'Residual Severity Band'; (L) STRIDE category derivation from finding ID prefix should be explicit in extraction step."
  techlead_signoff: null
---

# Implementation Plan: 048 — Infographic Tiered Pipeline Auto-Detection & Residual Risk

**Branch**: `048-infographic-tiered-detection` | **Date**: 2026-03-28 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `specs/048-infographic-tiered-detection/spec.md`

## Summary

Extend the `/infographic` command and its backing agent to support a three-tier data source auto-detection hierarchy (`compensating-controls.md` > `risk-scores.md` > `threats.md`). When `compensating-controls.md` is detected as the richest available source, the agent extracts residual risk scores instead of inherent scores. Enhancement tips guide users toward richer pipeline tiers. Risk labels distinguish "Residual Risk", "Inherent Risk", and "Severity" based on the detected source. This is a documentation/prompt-engineering feature — all deliverables are markdown files modifying existing command and agent specifications.

## Technical Context

**Language/Version**: Markdown (prompt specifications and agent instructions)
**Primary Dependencies**: None (no runtime dependencies — extends existing markdown prompt files)
**Storage**: Local filesystem — markdown files in `.claude/commands/` and `.claude/agents/tachi/`
**Testing**: Manual walkthrough validation (run `/infographic` at each tier)
**Target Platform**: Any LLM capable of following structured markdown prompts
**Project Type**: Documentation/prompt update (no application code)
**Performance Goals**: No additional latency beyond current command execution
**Constraints**: No breaking changes to existing `/infographic` behavior; fresh context isolation (ADR-010); spec-first with Gemini optional (ADR-014)
**Scale/Scope**: ~200-400 lines of changes across 2 primary files

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. General-Purpose Architecture | PASS | Extends existing detection pattern; domain-agnostic |
| II. API-First Design | N/A | No API changes |
| III. Backward Compatibility | PASS | All existing invocations produce identical output (FR-012) |
| IV. Concurrency & Data Integrity | N/A | No state changes |
| V. Privacy & Data Isolation | PASS | No PII in command/agent specifications |
| VI. Testing Excellence | PASS | Manual walkthrough validation per docs-only exception |
| VII. Definition of Done | PASS | Docs-only exception applies |
| VIII. Observability | N/A | No system changes |
| IX. Git Workflow | PASS | Feature branch `048-infographic-tiered-detection` |
| X. Product-Spec Alignment | PASS | PM approved spec; plan follows spec FRs |
| XI. SDLC Triad Collaboration | PASS | Standard Triad workflow in progress |

## Project Structure

### Documentation (this feature)

```
specs/048-infographic-tiered-detection/
├── plan.md              # This file
├── research.md          # Research phase output (completed during /aod.spec)
├── spec.md              # Feature specification (PM approved)
├── checklists/
│   └── requirements.md  # Spec quality checklist
└── tasks.md             # Task breakdown (/aod.tasks output)
```

### Source Files (files to modify)

```
.claude/
├── commands/
│   └── infographic.md           # PRIMARY: Add tier-1 detection, tips, error messages
└── agents/
    └── tachi/
        └── threat-infographic.md  # PRIMARY: Add compensating-controls extraction path, risk labels
```

No new files are created. No templates are modified structurally (data values and labels change, not layout).

## Implementation Approach

### Change 1: Infographic Command — Three-Tier Detection (`.claude/commands/infographic.md`)

**Current state**: Two-tier auto-detection (`risk-scores.md` > `threats.md`). Two content-based type detection rules for explicit paths. Co-location check for `threats.md` when risk-scores is primary. Single post-run tip when `threats.md` is the only source.

**Target state**: Three-tier auto-detection (`compensating-controls.md` > `risk-scores.md` > `threats.md`). Three content-based type detection rules. Co-location check for `threats.md` when either `compensating-controls.md` or `risk-scores.md` is primary. Enhancement tips at each tier. Updated error messages listing all three tiers.

**Specific changes**:

1. **Step 0 (Parse Arguments)**: No changes needed — explicit path parsing is data-source-agnostic.

2. **Step 1.2 (Detect data source — explicit path)**: Add a new detection rule before the existing two:
   - Contains `## 2. Coverage Matrix` AND the first table beneath it has a `Residual Score` column → type is `compensating-controls`
   - Update the "UNABLE TO DETECT" error message to list all three expected formats.

3. **Step 1.2 (Detect data source — auto-detect)**: Insert a new first scan step:
   - Scan for `compensating-controls.md` in cwd
   - If found: set `primary_file = compensating-controls.md`, type is `compensating-controls`
   - If not found: fall through to existing `risk-scores.md` scan
   - Update the "NO DATA SOURCE FILES FOUND" error to list all three tiers with their producing commands.

4. **Step 1.3 (Co-located threats.md check)**: Extend the existing check to trigger when type is `compensating-controls` (not just `risk-scores`). The logic is identical — `threats.md` is required in `data_source_dir` for structural data. `risk-scores.md` is NOT required when compensating-controls is primary.

5. **Step 1.5 (Display detection summary)**: Add type label for compensating-controls: `residual risk (compensating-controls.md)`.

6. **Step 2 (Run Infographic Agent)**: Add the compensating-controls data source type to the agent prompt template. Pass the same `primary_file` + `secondary_file` pattern already used for risk-scores.

7. **Step 3 (Report Results)**: Replace the single post-run tip with tiered enhancement tips:
   - `threats` detected → tip about `/risk-score`
   - `risk-scores` detected → tip about `/compensating-controls`
   - `compensating-controls` detected → full pipeline confirmation
   - Explicit path → no tip (suppressed)

### Change 2: Infographic Agent — Compensating Controls Extraction Path (`.claude/agents/tachi/threat-infographic.md`)

**Current state**: Two data source types (`threats`, `risk-scores`) with detection rules, extraction methodologies, and specification generation. The agent produces 6-section specs per `schemas/infographic.yaml`.

**Target state**: Three data source types (`compensating-controls`, `risk-scores`, `threats`) with the same detection → extraction → specification pattern. Risk labels adapt to source type. Baseball-card summary zone includes risk reduction percentage when compensating-controls is the source.

**Specific changes**:

1. **Metadata block**: Add `compensating-controls` to `data_source_types`:
   ```yaml
   compensating-controls:
     files: [compensating-controls.md, threats.md]
     description: "Residual risk extraction with control effectiveness (dual-file)"
   ```
   Add `compensating-controls` to `input_schemas`:
   ```yaml
   compensating-controls: ../../../schemas/compensating-controls.yaml
   ```

2. **Data Source Detection**: Add a new detection rule (checked BEFORE the existing two):
   - Contains `## 2. Coverage Matrix` AND the first table beneath it has a `Residual Score` column → type is `compensating-controls`
   - Add co-located file requirement: same pattern as risk-scores, require `threats.md` in same directory.

3. **New section: Data Extraction Methodology: compensating-controls.md**: Add a new extraction methodology parallel to the existing risk-scores path:

   **Step 1**: Parse `compensating-controls.md` Section 1 (Executive Summary) for metadata:
   - Total threats analyzed, coverage distribution (found/partial/missing percentages)
   - Risk reduction percentage (`{risk_reduction_pct}%` from the inherent → residual line)
   - Scan date and schema version (from frontmatter)

   **Step 2**: Parse `compensating-controls.md` Section 2 (Coverage Matrix) for per-finding residual data:
   - Iterate across all 4 sub-tables (Critical, High, Medium, Low residual severity)
   - For each finding row, extract: `id`, `component`, `threat`, `residual_score`, `residual_severity_band`, `control_status`
   - Compute residual severity distribution counts from the sub-table groupings
   - **Accuracy invariant**: residual severity distribution MUST exactly match the sub-table groupings (zero discrepancy)

   **Step 3**: Read co-located `threats.md` Section 1 for project metadata and component list (same as risk-scores path Step 3)

   **Step 4**: Read co-located `threats.md` Section 2 for spatial/structural data — trust zones, data flows (same as risk-scores path Step 4, used by system-architecture template)

   **Step 5**: Compute risk distribution using residual scores:
   - Map `residual_score` to severity bands using the same thresholds (Critical: 9.0-10.0, High: 7.0-8.9, Medium: 4.0-6.9, Low: 0.0-3.9)
   - Cross-tabulate component × STRIDE category using residual scores for heat map
   - Select top findings by highest `residual_score` (descending) for critical findings section
   - Aggregate per-component residual risk for architecture overlay

4. **Risk Labels**: Add a source-type-aware label mapping used in specification generation:
   - `compensating-controls` → "Residual Risk"
   - `risk-scores` → "Inherent Risk"
   - `threats` → "Severity"
   The label appears in: spec Section 1 metadata, Section 2 chart title, Section 4 finding card headers, and Section 6 visual design directives header.

5. **Baseball Card Template Adaptation**: When source type is `compensating-controls`:
   - Donut chart: residual severity distribution (from extraction Step 2)
   - Finding cards: residual score and residual severity band
   - Summary zone: add "Risk Reduction: {risk_reduction_pct}%" line (from extraction Step 1)
   - Header label: "Residual Risk" (from risk label mapping)

6. **System Architecture Template Adaptation**: When source type is `compensating-controls`:
   - Component boxes: border color from residual severity (not inherent)
   - Badge: residual finding count and severity
   - Finding legend: grouped by residual severity band
   - Header label: "Residual Risk"

7. **Error Handling**:
   - Detection-level failure (file lacks `## 2. Coverage Matrix` or `Residual Score` column): fall through to `risk-scores` detection (graceful)
   - Extraction-level failure (detection succeeds but rows malformed/empty mid-extraction): halt with warning, do NOT silently fall through

### Change Summary

| File | Lines Changed (est.) | Change Type |
|------|---------------------|-------------|
| `.claude/commands/infographic.md` | ~80-100 | Extend detection, add tips, update errors |
| `.claude/agents/tachi/threat-infographic.md` | ~120-200 | Add extraction path, risk labels, template adaptations |
| **Total** | ~200-300 | |

### What Does NOT Change

- Template files (`infographic-baseball-card.md`, `infographic-system-architecture.md`) — structural layout is locked; only data values and labels change via agent instructions
- Schema files (`infographic.yaml`, `compensating-controls.yaml`) — no schema changes needed
- Other commands or agents — no cross-command dependencies
- Existing behavior for `risk-scores.md` and `threats.md` paths — backward compatible

## Error Handling Strategy

| Error Type | Condition | Behavior |
|------------|-----------|----------|
| Detection-level failure | `compensating-controls.md` exists but no `## 2. Coverage Matrix` or no `Residual Score` column | Fall through to `risk-scores.md` tier (graceful degradation) |
| Extraction-level failure | Coverage Matrix detected but rows are malformed or empty | Halt with warning; do NOT fall through (prevent misrepresentation) |
| Missing co-located `threats.md` | `compensating-controls.md` primary but no `threats.md` in same directory | Halt with error listing expected path |
| No data sources found | None of the three files exist in cwd | Exit with error listing all three files + producing commands |
| Unrecognized explicit path | File at explicit path matches no detection markers | Exit with error listing expected formats |

## Phasing

### Phase 1: Command Detection & Tips

Update `.claude/commands/infographic.md`:
- Three-tier auto-detection hierarchy
- Content-based type detection for explicit paths
- Co-location enforcement
- Enhancement tips at each tier
- Updated error messages

### Phase 2: Agent Extraction & Labels

Update `.claude/agents/tachi/threat-infographic.md`:
- Metadata additions
- Detection rule for compensating-controls
- Data extraction methodology (5 steps)
- Risk label mapping
- Template adaptations (baseball-card + system-architecture)
- Error handling (detection vs extraction level)

### Phase 3: Validation

- Manual walkthrough at each tier
- Verify backward compatibility
- Verify count accuracy (residual counts match source)
- Verify enhancement tips display/suppression

## Dependencies

All dependencies are delivered and available:

| Dependency | Status | Required For |
|------------|--------|-------------|
| PRD-039 (Standalone /infographic) | Delivered | Command structure, auto-detection framework |
| PRD-036 (Compensating Controls) | Delivered | `compensating-controls.md` output format |
| PRD-035 (Risk Scoring) | Delivered | `risk-scores.md` (tier 2 data source) |
| ADR-010 (Fresh Context Isolation) | Accepted | Agent isolation constraint |
| ADR-014 (Spec-First / Gemini Optional) | Accepted | Graceful degradation |
