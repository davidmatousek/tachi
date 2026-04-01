---
prd_reference: docs/product/02_PRD/074-baseline-aware-pipeline-2026-03-31.md
triad:
  pm_signoff:
    agent: product-manager
    date: 2026-03-31
    status: APPROVED_WITH_CONCERNS
    notes: "All 6 PRD user stories addressed (US-074-5 merged into US-2). All 4 core capabilities covered across 20 FRs. Success criteria aligned with PRD targets. Single low-severity concern: US-074-5 developer-persona delta summary test merged into US-2 — summary-level output format addressable during task decomposition."
  architect_signoff: null
  techlead_signoff: null
---

# Feature Specification: Baseline-Aware Pipeline

**Feature Branch**: `074-baseline-aware-pipeline`
**Created**: 2026-03-31
**Status**: Draft
**Input**: PRD 074 — Baseline-Aware Pipeline

## User Scenarios & Testing

### User Story 1 — Stable Re-Scan (Priority: P0)

A security engineer re-runs the tachi pipeline on a codebase with no changes since the last scan. Every finding in the output retains the exact same ID and risk score as the previous run. No phantom findings appear, and no findings disappear.

**Why this priority**: This is the foundational capability. Without stable re-scans, no other baseline feature (remediation tracking, SLA computation, delta reporting) is trustworthy. The observed 23% drift and complete ID remapping on unchanged code is the core problem statement.

**Independent Test**: Run the pipeline twice on the same architecture description with no changes between runs. Compare output files — finding IDs, scores, and counts must be identical.

**Acceptance Scenarios**:

1. **Given** a previous pipeline run produced `threats.md` with 39 findings, **When** the pipeline runs again with no code or architecture changes, **Then** the output contains exactly 39 findings with identical IDs and scores.
2. **Given** a previous run's `risk-scores.md` assigned finding S-3 a composite score of 7.2, **When** the pipeline re-runs on the same codebase, **Then** S-3 retains composite score 7.2 with zero drift.
3. **Given** a previous run's `compensating-controls.md` found control evidence for T-1, **When** the pipeline re-runs on the same codebase, **Then** T-1's control status and residual score are identical.

---

### User Story 2 — Remediation Verification (Priority: P0)

A developer fixes a vulnerability targeted by a specific finding. After the fix, they re-run the pipeline and see that specific finding marked as `[RESOLVED]` with its original ID preserved for audit traceability.

**Why this priority**: This directly enables the primary user workflow — proving that a fix actually resolved the threat it targeted. Without this, remediation verification requires manual comparison across reports.

**Independent Test**: Modify the architecture to remove the attack surface targeted by a specific finding, then re-run the pipeline. Verify the finding is marked `[RESOLVED]` with its original ID.

**Acceptance Scenarios**:

1. **Given** finding S-3 exists in the baseline, **When** the corresponding threat is no longer applicable in the current architecture, **Then** the output marks S-3 as `[RESOLVED]` retaining its original ID, description, and last-known score.
2. **Given** finding T-2 was partially fixed (reduces but does not eliminate the threat), **When** the pipeline re-runs, **Then** T-2 is marked `[UPDATED]` with a revised score, not `[RESOLVED]`.
3. **Given** a finding is marked `[RESOLVED]` in run N, **When** the same threat reappears in a future run N+2, **Then** it is assigned a new ID (not the previously resolved one).

---

### User Story 3 — New Threat Discovery (Priority: P0)

A team deploys a code change that introduces a new attack surface. The pipeline discovers genuinely new threats alongside carried-forward findings, without duplicating existing findings or being anchored by previous results.

**Why this priority**: Discovery quality must be maintained alongside stability. The pipeline must not trade fresh analysis for determinism — both are required simultaneously.

**Independent Test**: Add a new component to the architecture description, re-run the pipeline. Verify new findings appear with `[NEW]` annotation and sequential IDs, while existing findings retain their baseline IDs.

**Acceptance Scenarios**:

1. **Given** a codebase change introduces a new LLM-integrated component, **When** the pipeline runs, **Then** new threats are discovered and annotated `[NEW]` with sequentially assigned IDs after the highest existing ID per category.
2. **Given** carried-forward findings exist from the baseline, **When** the fresh discovery phase runs, **Then** the discovery context receives only component names and covered threat categories — not full finding descriptions — to prevent anchoring bias.
3. **Given** new findings are discovered, **When** scored, **Then** each new finding's CVSS base score falls within +/- 1.0 of its category default as defined in the scoring schema.

---

### User Story 4 — Delta Annotations (Priority: P1)

A CISO reviewing quarterly security reports sees every finding annotated with its lifecycle status: `[NEW]`, `[UNCHANGED]`, `[UPDATED]`, or `[RESOLVED]`. This enables trend reporting and board-level communication without explaining LLM variance.

**Why this priority**: Annotations are the user-visible layer that makes baseline awareness actionable. Without clear delta status, users must manually diff reports to understand what changed.

**Independent Test**: Run the pipeline with a baseline, make targeted changes, re-run. Verify every finding in the output carries exactly one delta annotation.

**Acceptance Scenarios**:

1. **Given** a pipeline run with a baseline, **When** reviewing the output, **Then** every finding in the threats table has exactly one delta annotation: `[NEW]`, `[UNCHANGED]`, `[UPDATED]`, or `[RESOLVED]`.
2. **Given** a finding's description changed but its core threat remains the same, **When** the pipeline runs, **Then** the finding is annotated `[UPDATED]` with its original ID preserved.
3. **Given** a finding persists through runs N, N+1, and N+2, **When** reviewing the sequence, **Then** the finding's lifecycle is traceable: `[NEW]` in N, `[UNCHANGED]` in N+1 and N+2, with the same stable ID throughout.

---

### User Story 5 — Coverage Assurance (Priority: P1)

A security engineer runs the pipeline on a system with an LLM Process component. A coverage gate verifies that minimum required threat categories (e.g., prompt injection, data poisoning, model theft) were evaluated for that component type, preventing blind spots caused by LLM non-determinism.

**Why this priority**: Coverage assurance ensures pipeline reliability across runs — even when the LLM's attention varies, required threat categories are always evaluated.

**Independent Test**: Run the pipeline on an architecture with an LLM Process component. Remove prompt injection findings from the intermediate results. Verify the coverage gate flags the gap and triggers targeted re-analysis.

**Acceptance Scenarios**:

1. **Given** a component of type "LLM Process", **When** the coverage gate evaluates findings, **Then** it verifies prompt injection, data poisoning, and model theft categories are represented.
2. **Given** a required threat category is missing from combined results, **When** the coverage gate flags it, **Then** targeted re-analysis runs for that specific category and component only.
3. **Given** all required categories are covered for every component, **When** the coverage gate runs, **Then** it passes silently without additional analysis.

---

### User Story 6 — Remediation SLA Tracking (Priority: P1)

A compliance officer tracks remediation timelines across assessment cycles. Each finding retains a stable ID from discovery through resolution, and governance fields (risk owner, remediation SLA) are preserved across runs to enable time-to-remediate computation.

**Why this priority**: SLA tracking is a compliance requirement that depends on stable IDs and governance field persistence. Without these, time-to-remediate cannot be computed across assessment cycles.

**Independent Test**: Run the pipeline across three consecutive cycles (N, N+1, N+2). Verify that a finding discovered in run N retains its ID and governance fields through N+1 and N+2.

**Acceptance Scenarios**:

1. **Given** a finding discovered in run N has governance fields (risk_owner: "security-team", remediation_sla: "7d"), **When** it persists through runs N+1 and N+2, **Then** the same ID and governance fields are preserved in all runs.
2. **Given** delta annotations exist across runs, **When** reviewing a finding's history, **Then** the lifecycle is traceable: `[NEW]` → `[UNCHANGED]` → `[UPDATED]` → `[RESOLVED]`.

---

### Edge Cases

- **No baseline available (first run)**: Pipeline operates in stateless mode, producing output identical to current behavior. All findings annotated `[NEW]`. No degradation in quality or format.
- **Corrupted or unparseable baseline file**: Pipeline falls back to stateless mode with a warning message. Output is still produced — baseline awareness degrades gracefully, never blocks execution.
- **Baseline from a different architecture version (components renamed/removed)**: Findings referencing removed components are classified as `[RESOLVED]`. Findings referencing renamed components are matched by threat category and similarity — if below threshold, treated as `[RESOLVED]` (old) + `[NEW]` (renamed).
- **Phase 2 discovery failure**: Pipeline still produces Phase 1 carry-forward results. Discovery failure is a non-blocking warning, not a pipeline error.
- **Coverage gate finds multiple gaps**: Targeted re-analysis runs once per gap. If re-analysis also fails to produce findings for a required category, the gap is reported as a warning — the coverage gate does not loop.
- **Extremely large finding sets (100+ findings)**: Deduplication and coverage gate must handle large sets without significant performance degradation. Baseline loading adds no more than 5 seconds.
- **Score bounding at extremes**: If a category default CVSS is 9.5, bounded range is 8.5–10.0 (capped at 10.0). If default is 1.0, bounded range is 0.0–2.0 (floored at 0.0).

## Requirements

### Functional Requirements

- **FR-001**: System MUST detect and load the most recent previous pipeline output as a baseline when present in the output directory, or accept an explicit baseline path.
- **FR-002**: System MUST verify each baseline finding against the current architecture and classify it as unchanged, updated, or resolved.
- **FR-003**: System MUST inherit the original ID and score for findings classified as unchanged — zero drift for unchanged findings.
- **FR-004**: System MUST preserve the original ID for findings classified as updated, while allowing revised description and score.
- **FR-005**: System MUST retain resolved findings in the output with `[RESOLVED]` annotation and their original ID, description, and last-known score for audit traceability.
- **FR-006**: System MUST run fresh threat discovery in an isolated context that receives only the architecture description and a coverage summary (component names + covered threat categories) — not full finding descriptions.
- **FR-007**: System MUST bound new finding scores within +/- 1.0 of the category default CVSS base score from the scoring schema.
- **FR-008**: System MUST deduplicate Phase 2 discoveries against the baseline using component, threat category, and description similarity. Matches above 80% similarity are duplicates — the baseline version wins.
- **FR-009**: System MUST assign new finding IDs sequentially after the highest existing ID per category (e.g., if baseline has S-1 through S-5, a new spoofing finding gets S-6).
- **FR-010**: System MUST annotate every finding with exactly one delta status: `[NEW]`, `[UNCHANGED]`, `[UPDATED]`, or `[RESOLVED]`.
- **FR-011**: System MUST include baseline reference metadata in output frontmatter: source file, date, finding count, and run identifier.
- **FR-012**: System MUST use SARIF `partialFingerprints.findingId/v1` as the primary finding correlation key across runs.
- **FR-013**: System MUST verify minimum required threat categories are evaluated per component type using a coverage checklist.
- **FR-014**: System MUST trigger targeted re-analysis for component-category pairs flagged as missing by the coverage gate.
- **FR-015**: System MUST carry forward control status and residual risk for unchanged findings in compensating controls output.
- **FR-016**: System MUST re-scan only changed or new files when evaluating compensating controls, while preserving control evidence for unchanged findings.
- **FR-017**: System MUST carry forward governance fields (risk_owner, remediation_sla, risk_disposition, review_date) for findings that persist across runs.
- **FR-018**: System MUST operate identically to current stateless behavior when no baseline is available (first run or baseline not found).
- **FR-019**: System MUST include coverage gate pass/fail status in output frontmatter.
- **FR-020**: System MUST produce valid SARIF output with `partialFingerprints` containing `findingId/v1`, `primaryLocationLineHash`, and `baselineRunId` for every finding.

### Key Entities

- **Finding**: A discovered security threat with a stable ID, category, component, description, risk assessment, and lifecycle delta status. Persists across pipeline runs via SARIF fingerprints.
- **Baseline**: The previous pipeline output used as reference for the current run. Contains finding set, scores, and metadata. Identified by run date and unique run identifier.
- **Delta Annotation**: Lifecycle classification of a finding relative to the baseline: `[NEW]`, `[UNCHANGED]`, `[UPDATED]`, or `[RESOLVED]`.
- **Coverage Checklist**: Per-component-type definition of minimum required threat categories. Used by the coverage gate to detect blind spots.
- **Coverage Summary**: Lightweight representation of Phase 1 results (component names + covered categories) provided to the isolated discovery phase to prevent anchoring bias.

## Success Criteria

### Measurable Outcomes

- **SC-001**: Running the pipeline twice on an unchanged codebase produces 100% identical finding IDs (baseline: ~0%).
- **SC-002**: Running the pipeline twice on an unchanged codebase produces zero score drift across all findings (baseline: 0.2-0.6 per finding).
- **SC-003**: Running the pipeline twice on an unchanged codebase produces identical finding counts with zero phantom findings (baseline: +23% drift).
- **SC-004**: Every `[NEW]` finding in a delta run corresponds to an actual code or architecture change — no phantom new findings on unchanged code.
- **SC-005**: 100% of required threat categories are evaluated per component type when the coverage gate is active.
- **SC-006**: A finding resolved by a targeted fix is correctly marked `[RESOLVED]` by its stable ID within one re-run of the pipeline.
- **SC-007**: Baseline loading adds no more than 5 seconds to pipeline execution time.
- **SC-008**: Total pipeline overhead from baseline awareness is less than 15% increase in execution time compared to stateless mode.
- **SC-009**: Coverage gate evaluation completes in under 2 seconds per component.

### Assumptions

- SARIF `partialFingerprints` provide sufficient uniqueness for cross-run correlation. The combination of `findingId/v1` and `primaryLocationLineHash` is deterministic given the same inputs.
- LLM-based similarity matching at >80% threshold produces acceptable deduplication accuracy. False positive rate (duplicate classified as new) below 5%.
- Coverage checklists can be authored per component type (External Entity, Process, Data Store, Data Flow, LLM Process, MCP Server) without excessive maintenance burden.
- Users store pipeline outputs in a consistent location between runs, enabling automatic baseline detection.
- The scoring schema category defaults in `schemas/risk-scoring.yaml` are stable and represent reasonable center points for score bounding.
- Pipeline commands continue to be LLM agent invocations — score bounding is enforced through prompt instructions, not hard system constraints.

### Constraints

- All state is file-based with no external database — constitutional requirement for local-first operation.
- Existing output formats must remain valid — delta annotations and baseline frontmatter are additive, not breaking.
- No breaking changes to SARIF output structure — new fingerprint fields added alongside existing.
- Users who do not provide baselines see zero behavioral change from current pipeline behavior.
- Coverage checklists must be generic enough to apply across diverse architectures while specific enough to catch blind spots for known component types.

### Dependencies

- Existing pipeline commands (`/threat-model`, `/risk-score`, `/compensating-controls`) and their skill/agent definitions.
- `schemas/risk-scoring.yaml` — category-default CVSS vectors used for score bounding.
- `schemas/finding.yaml` — finding ID pattern and required fields.
- `schemas/compensating-controls.yaml` — control status and residual risk fields.
- SARIF 2.1.0 fingerprint specification — correlation mechanism.
- Blocks #55 (Security Progression Summary) — requires stable finding IDs for trend computation.

### Out of Scope

- Trend visualization across runs (deferred to #55).
- Persistent finding database — files only, no external storage.
- Cross-project finding correlation.
- Automated remediation suggestions based on finding history.
- UI for finding lifecycle management.
