---
prd:
  number: 074
  topic: baseline-aware-pipeline
  created: 2026-03-31
  status: Approved
  type: feature
triad:
  pm_signoff:
    agent: product-manager
    date: 2026-03-31
    status: APPROVED
    notes: "PRD authored by PM. Problem statement grounded in quantitative evidence (23% drift). User stories preserve GitHub Issue content verbatim. Strategic alignment to finding lifecycle management validated."
  architect_signoff:
    agent: architect
    date: 2026-03-31
    status: APPROVED_WITH_CONCERNS
    notes: "4-phase architecture technically sound. 5 spec-level clarifications: (1) baseline orchestration belongs in command layer, (2) primaryLocationLineHash should be primary correlation key, (3) score bounding applies to cvss_base dimension only, (4) AI component subtype detection via keyword matching, (5) deduplication similarity must use deterministic metric."
  techlead_signoff:
    agent: team-lead
    date: 2026-03-31
    status: APPROVED_WITH_CONCERNS
    notes: "Feasible at 4 waves. 3 concerns: (1) orchestrator complexity — recommend wrapper/extraction, (2) coverage checklist authoring in Wave 0, (3) US-074-3 must decompose into 3-4 sub-tasks. 2 risks: orchestrator context pressure, 2 open questions implementation-blocking."
source:
  idea_id: 74
  story_id: null
---

# Baseline-Aware Pipeline — Product Requirements Document

**Status**: Approved
**Created**: 2026-03-31
**Author**: product-manager
**Reviewers**: architect, team-lead
**Phase**: Phase 1
**Priority**: P1

---

## Executive Summary

### The One-Liner
Make tachi's security findings trackable across runs so teams can prove which threats they fixed.

### Problem Statement
All three tachi pipeline steps (`/threat-model`, `/risk-score`, `/compensating-controls`) are stateless — each run generates findings from scratch with zero awareness of previous runs. On an unchanged codebase (second-brain-mcp, Mar 25 vs Mar 31), this produced a 23% finding count drift, 0.2–0.6 score drift per finding, complete ID remapping, and 9 phantom "new" findings. This makes remediation tracking, stakeholder reporting, and compliance verification unreliable.

### Proposed Solution
An Enhanced Hybrid 4-phase baseline-aware pipeline that combines carry-forward stability with fresh discovery quality:
1. **Carry-Forward** — Load previous run as baseline, verify each finding, inherit stable IDs and scores
2. **Isolated Discovery** — Fresh agent discovers threats NOT already covered (no anchoring bias)
3. **Merge + Dedup** — Match new findings against baseline, duplicates discarded
4. **Coverage Gate** — Minimum threat checklist per component type ensures no blind spots

### Success Criteria
- Running the pipeline twice on an unchanged codebase produces identical finding IDs and scores (zero drift)
- Running after a fix correctly marks the targeted finding as `[RESOLVED]` by its stable ID
- Coverage gate flags when a required threat category is missing for a component
- Delta annotations (`[NEW]`, `[UNCHANGED]`, `[UPDATED]`, `[RESOLVED]`) present on every finding

### Timeline
Target: Phase 1 delivery within current development cycle. Foundation for #55 (Security Progression Summary).

---

## Strategic Alignment

### Product Vision Alignment
**Reference**: [product-vision.md](docs/product/01_Product_Vision/product-vision.md)

Transforms tachi from a point-in-time analysis tool into a **continuous finding lifecycle management platform**. This directly serves the vision of being "the default threat modeling toolkit for any team building agentic AI applications" — teams need trackable, verifiable security assessments, not one-shot reports.

### Roadmap Fit
**Dependencies**: Existing pipeline commands (`/threat-model`, `/risk-score`, `/compensating-controls`)
**Enables**: #55 (Security Progression Summary — requires stable finding IDs for trend computation)
**Related**: #71 (Deterministic Infographic Extraction), Feature 067 (Deterministic Report Data Extraction)

---

## Target Users & Personas

### Primary Persona: Security Engineer
- **Role**: Runs tachi pipeline on codebases, triages findings, tracks remediation
- **Experience**: Mid-to-senior security practitioner, comfortable with STRIDE/OWASP
- **Goals**: Verify that fixes resolved specific findings; produce reliable audit trails
- **Pain Points**: Finding IDs change between runs; can't track which threats were remediated; re-running produces phantom "new" findings on unchanged code

**Why This Matters**: Security engineers are the primary pipeline operators. Every re-scan currently invalidates their triage work — assigned owners, set priorities, and accepted risks all become meaningless when IDs remap.

### Secondary Persona: CISO / Security Leadership
- **Role**: Reviews quarterly security reports, presents risk posture to board
- **Experience**: Strategic security leadership, not running tools directly
- **Goals**: Stable metrics for board reporting; trust in trend data
- **Pain Points**: Finding counts and risk scores drift on unchanged code — "are we getting better or is the tool just giving different numbers?"

### Tertiary Persona: Compliance Officer
- **Role**: Tracks remediation SLAs, maintains audit evidence
- **Experience**: Compliance/audit background, relies on finding-level traceability
- **Goals**: Track time-to-remediate per finding from discovery through resolution
- **Pain Points**: Without stable IDs, SLA tracking is impossible across assessment cycles

### Tertiary Persona: Developer
- **Role**: Merges security fixes, wants confirmation the fix worked
- **Experience**: Software developer, not a security specialist
- **Goals**: Run pipeline after fix, see specific finding marked `[RESOLVED]`
- **Pain Points**: Pipeline produces completely new set of findings after every fix

---

## User Stories

### US-074-1: Remediation Verification
**When** I have fixed a vulnerability and re-run the tachi pipeline,
**I want to** see the specific finding marked as `[RESOLVED]` with the same ID it had when discovered,
**So I can** prove to auditors which specific threats were remediated.

**Acceptance Criteria**:
- **Given** a finding S-3 exists in the baseline, **when** the threat is no longer applicable in current architecture, **then** output marks S-3 as `[RESOLVED]`
- **Given** a finding is marked `[RESOLVED]`, **when** reviewing output, **then** the finding retains its original ID, description, and last-known score
- **Given** a resolved finding, **when** the same threat reappears in a later run, **then** it is assigned a NEW ID (not the old resolved one)

**Priority**: P0 | **Effort**: L

### US-074-2: Stable Reporting
**When** I re-run the pipeline on a codebase with no changes,
**I want to** get identical finding IDs and risk scores as the previous run,
**So I can** trust the numbers I present to the board without explaining LLM variance.

**Acceptance Criteria**:
- **Given** no code/architecture changes between runs, **when** pipeline executes twice, **then** finding IDs are identical
- **Given** no changes, **when** comparing risk scores, **then** composite scores are identical (zero drift)
- **Given** no changes, **when** comparing finding counts, **then** counts are identical (no phantom findings)

**Priority**: P0 | **Effort**: L

### US-074-3: New Threat Discovery
**When** I run the pipeline on a new code release,
**I want to** see genuinely new threats discovered alongside carried-forward findings,
**So I can** maintain discovery quality without sacrificing stability.

**Acceptance Criteria**:
- **Given** a codebase change introduces a new attack surface, **when** pipeline runs, **then** new threats are discovered and marked `[NEW]`
- **Given** carried-forward findings exist, **when** new discovery runs, **then** discovery agent operates without anchoring bias (architecture + coverage summary only, not full finding text)
- **Given** new findings are discovered, **when** scoring, **then** new finding scores are bounded within +/- 1.0 of category defaults from `schemas/risk-scoring.yaml`

**Priority**: P0 | **Effort**: XL

### US-074-4: Remediation SLA Tracking
**When** tracking remediation timelines across multiple assessment cycles,
**I want to** each finding to have a stable ID from discovery through resolution,
**So I can** compute time-to-remediate per finding for compliance reporting.

**Acceptance Criteria**:
- **Given** a finding is discovered in run N, **when** it persists through runs N+1, N+2, **then** the same ID is used in all runs
- **Given** a finding has governance fields (risk_owner, remediation_sla), **when** carried forward, **then** governance fields are preserved
- **Given** delta annotations exist, **when** reviewing history, **then** each finding's lifecycle is traceable: `[NEW]` → `[UNCHANGED]` → `[UPDATED]` → `[RESOLVED]`

**Priority**: P1 | **Effort**: M

### US-074-5: Fix Confirmation
**When** I have just merged a security fix targeting a specific finding,
**I want to** the next pipeline run to confirm my fix resolved that finding by its ID,
**So I can** close the remediation ticket with evidence.

**Acceptance Criteria**:
- **Given** finding T-2 was the target of a fix, **when** pipeline runs after the fix, **then** T-2 is marked `[RESOLVED]` if the threat no longer applies
- **Given** T-2 is resolved, **when** reviewing output, **then** the delta summary shows "T-2: Tampering — RESOLVED"
- **Given** a partial fix that reduces but doesn't eliminate the threat, **when** pipeline runs, **then** T-2 is marked `[UPDATED]` with revised score (not `[RESOLVED]`)

**Priority**: P1 | **Effort**: M

### US-074-6: Coverage Assurance
**When** running the pipeline on any codebase,
**I want to** a coverage gate that ensures minimum threat categories are evaluated per component,
**So I can** have confidence the pipeline isn't missing obvious attack surfaces due to LLM non-determinism.

**Acceptance Criteria**:
- **Given** a component of type "LLM Process", **when** coverage gate runs, **then** it verifies prompt injection, data poisoning, and model theft categories are evaluated
- **Given** a required category is missing from combined results, **when** coverage gate flags it, **then** targeted re-analysis runs for that category only
- **Given** all required categories are covered, **when** coverage gate runs, **then** it passes silently

**Priority**: P1 | **Effort**: L

---

## Functional Requirements

### Core Capability 1: Baseline Loading & Carry-Forward (Phase 1)

**Description**: Pipeline commands detect and load the most recent previous output as a baseline, then verify each finding against the current architecture/code.

**Inputs**: Previous run's output files (`threats.md`, `risk-scores.md`, `compensating-controls.md`), current architecture description
**Processing**:
1. Detect baseline files in the output directory (most recent by date or explicit `--baseline` path)
2. Parse each finding from baseline, extracting ID, category, component, description, and score
3. Verify each finding against current architecture — classify as: keep (unchanged), update (modified), or resolve (no longer applicable)
4. Inherited findings retain their original ID and score (zero drift for unchanged findings)

**Outputs**: Carried-forward finding set with delta annotations (`[UNCHANGED]`, `[UPDATED]`, `[RESOLVED]`)

**Business Rules**:
- Baseline is optional — first run operates in stateless mode (backward compatible)
- `[UNCHANGED]` findings retain exact ID and score from baseline
- `[UPDATED]` findings retain ID but get revised description/score
- `[RESOLVED]` findings are included in output with `[RESOLVED]` annotation for audit trail
- SARIF `partialFingerprints.findingId/v1` is the primary correlation key

### Core Capability 2: Isolated Discovery (Phase 2)

**Description**: A fresh discovery agent runs in an isolated context to find threats NOT already covered, without anchoring bias from existing findings.

**Inputs**: Architecture description, coverage summary (component names + threat categories already covered from Phase 1)
**Processing**:
1. Spawn discovery in isolated context (separate agent invocation)
2. Agent receives architecture + coverage summary ONLY — not full finding descriptions
3. Agent discovers threats for uncovered component-category pairs
4. New findings scored with category-bounded CVSS: LLM adjusts +/- 1.0 from category defaults in `schemas/risk-scoring.yaml`

**Outputs**: New findings set with `[NEW]` annotation

**Business Rules**:
- Discovery agent MUST NOT receive full finding text from Phase 1 (prevents anchoring)
- Coverage summary format: list of `{component_name: [covered_categories]}`
- Score bounding enforced: `category_default - 1.0 ≤ new_score ≤ category_default + 1.0`
- If no gaps found, Phase 2 produces zero findings (valid outcome)

### Core Capability 3: Merge & Deduplication (Phase 3)

**Description**: Match Phase 2 discoveries against baseline to identify true duplicates vs. genuinely new findings.

**Inputs**: Phase 1 carried-forward set, Phase 2 discovery set
**Processing**:
1. For each Phase 2 finding, match against baseline by (component, threat_category, description_similarity)
2. Similarity threshold: >80% match = duplicate (baseline version wins, Phase 2 discarded)
3. Below threshold = genuinely new finding, assigned next available ID in its category
4. Merged set = Phase 1 findings + genuinely new Phase 2 findings

**Outputs**: Unified finding set with stable IDs and delta annotations

**Business Rules**:
- Baseline version ALWAYS wins on duplicate match (preserves score stability)
- New finding IDs are sequentially assigned AFTER the highest existing ID per category
- Example: If baseline has S-1 through S-5, new spoofing finding gets S-6
- SARIF fingerprints (`primaryLocationLineHash`) used as secondary correlation signal

### Core Capability 4: Coverage Gate (Phase 4)

**Description**: Verify minimum threat categories are evaluated per component type, preventing blind spots from LLM non-determinism.

**Inputs**: Merged finding set from Phase 3, coverage checklist definitions per component type
**Processing**:
1. For each component, determine its type (e.g., External Entity, Process, Data Store, LLM Process, MCP Server)
2. Look up required threat categories for that component type
3. Check merged findings for coverage of each required category
4. Flag uncovered categories → trigger targeted re-analysis for missing categories only

**Outputs**: Coverage report, any additional findings from targeted re-analysis

**Business Rules**:
- Coverage checklists defined in `schemas/` (new file: `coverage-checklists.yaml`)
- Coverage gate is a floor, not a ceiling — findings beyond the checklist are kept
- Targeted re-analysis findings follow Phase 2 scoring rules (category-bounded)
- Coverage gate pass/fail status included in output frontmatter

### Data Requirements

**Baseline Reference in Output Frontmatter**:
```yaml
baseline:
  source: "threats.md"          # or null for first run
  date: "2026-03-25"            # date of baseline run
  finding_count: 39             # baseline count for delta computation
  run_id: "2026-03-25T12-53-57" # unique run identifier
```

**Delta Annotations Per Finding**:
```
[NEW]        — First appearance in this run
[UNCHANGED]  — Exists in baseline with identical assessment
[UPDATED]    — Exists in baseline but description or score changed
[RESOLVED]   — Existed in baseline but no longer applicable
```

**Finding Registry** (SARIF fingerprints as primary tracking):
- `partialFingerprints.findingId/v1` — Stable finding ID (e.g., "S-3")
- `partialFingerprints.primaryLocationLineHash` — SHA-256(ruleId|component_name)
- `partialFingerprints.baselineRunId` — Reference to the run that first discovered this finding

### Integration Requirements

**Pipeline Command Changes**:
| Command | Changes Required |
|---------|-----------------|
| `/threat-model` | Baseline loading, 4-phase orchestration, delta annotations, coverage gate |
| `/risk-score` | Score inheritance for unchanged findings, bounded scoring for new, governance field carry-forward |
| `/compensating-controls` | Control status carry-forward, re-scan only changed files, residual risk inheritance |

**Schema Changes**:
| Schema | Changes Required |
|--------|-----------------|
| `schemas/finding.yaml` | Add `delta_status`, `baseline_run_id` fields |
| `schemas/risk-scoring.yaml` | Add `score_source` (inherited vs fresh), `score_bounds` |
| `schemas/compensating-controls.yaml` | Add `control_carry_forward`, `rescan_scope` |
| `schemas/coverage-checklists.yaml` | NEW — minimum threat categories per component type |

**Output Template Changes**:
| Template | Changes Required |
|----------|-----------------|
| `templates/tachi/output-schemas/threats.md` | Baseline frontmatter, delta column, coverage gate section |
| `templates/tachi/output-schemas/risk-scores.md` | Score source column, baseline reference |
| `templates/tachi/output-schemas/compensating-controls.md` | Control carry-forward status, rescan scope |

---

## Non-Functional Requirements

### Performance Requirements
- Baseline loading adds no more than 5 seconds to pipeline execution
- Phase 2 isolated discovery runs in parallel-capable context (same agent pool)
- Coverage gate evaluation completes in under 2 seconds per component
- Total pipeline overhead from baseline awareness: <15% increase in execution time

### Reliability Requirements
- Graceful degradation: if baseline file is corrupted or unparseable, fall back to stateless mode with warning
- If Phase 2 discovery fails, pipeline still produces Phase 1 carry-forward results
- Coverage gate failures are non-blocking warnings, not pipeline errors

### Backward Compatibility (Constitutional Requirement)
- First run without baseline operates identically to current stateless behavior
- Existing output formats remain valid — delta annotations and baseline frontmatter are additive
- No breaking changes to SARIF output structure — new fields added alongside existing
- Users who don't provide baselines see zero behavioral change

---

## Success Metrics

### Primary Metrics

**Finding ID Stability**:
- **Definition**: Percentage of findings that retain their ID across two runs on unchanged code
- **Baseline**: ~0% (IDs remap completely each run)
- **Target**: 100% on unchanged code

**Score Stability**:
- **Definition**: Maximum score drift across two runs on unchanged code
- **Baseline**: 0.2–0.6 per finding
- **Target**: 0.0 (zero drift for unchanged findings)

**Finding Count Stability**:
- **Definition**: Delta in finding count across two runs on unchanged code
- **Baseline**: +23% (39 → 48)
- **Target**: 0% (identical counts)

### Secondary Metrics

**Discovery Quality**:
- **Definition**: Number of genuinely new findings discovered on changed code (not phantom)
- **Baseline**: Cannot distinguish new from phantom currently
- **Target**: Every `[NEW]` finding corresponds to an actual code/architecture change

**Coverage Completeness**:
- **Definition**: Percentage of required threat categories covered per component
- **Baseline**: Unknown (no coverage tracking)
- **Target**: 100% of required categories evaluated per component type

---

## Scope & Boundaries

### In Scope (Phase 1)

**Must Have (P0)**:
- Baseline loading and carry-forward for `/threat-model` with stable IDs
- Score inheritance for `/risk-score` on unchanged findings
- Control status carry-forward for `/compensating-controls`
- Delta annotations (`[NEW]`, `[UNCHANGED]`, `[UPDATED]`, `[RESOLVED]`) on all outputs
- SARIF fingerprints as primary finding correlation mechanism
- Baseline reference in output frontmatter
- Backward compatibility — first run without baseline works identically to today

**Should Have (P1)**:
- Isolated discovery context (Phase 2) with anchoring-bias prevention
- Merge & deduplication (Phase 3) with >80% similarity threshold
- Coverage gate (Phase 4) with per-component-type checklists
- Category-bounded scoring for new findings (+/- 1.0 from `schemas/risk-scoring.yaml` defaults)
- Coverage checklist schema (`schemas/coverage-checklists.yaml`)

### Out of Scope (Future)

**Deferred to #55 (Security Progression Summary)**:
- Trend visualization across runs
- Remediation velocity dashboards
- Historical finding timeline charts

**Won't Have**:
- Persistent finding database (files-only, no external storage)
- Cross-project finding correlation
- Automated remediation suggestions based on finding history
- UI for finding lifecycle management

### Assumptions
- SARIF `partialFingerprints` provide sufficient uniqueness for cross-run correlation
- LLM-based similarity matching at >80% threshold produces acceptable deduplication accuracy
- Coverage checklists can be authored per component type without excessive maintenance burden
- Users store pipeline outputs in a consistent location between runs

### Constraints

**Technical Constraints**:
- All state is file-based (no external database) — constitutional requirement for local-first
- Pipeline commands are LLM agent invocations — scoring bounds are advisory, not hard-enforced at a system level
- Coverage checklists must be generic enough to apply across diverse architectures

**Dependencies**:
- Existing pipeline commands (`/threat-model`, `/risk-score`, `/compensating-controls`) and their agent/skill definitions
- `schemas/risk-scoring.yaml` category-default CVSS vectors (for bounded scoring)
- SARIF 2.1.0 fingerprint specification (for correlation)

---

## Risks & Dependencies

### Technical Risks

**Risk 1**: LLM similarity matching produces false positives/negatives in deduplication
- **Likelihood**: Medium
- **Impact**: Medium (false positive = lost new finding; false negative = duplicate in output)
- **Mitigation**: Use SARIF fingerprints (deterministic) as primary match, LLM similarity as secondary; tunable threshold
- **Contingency**: Fall back to fingerprint-only matching if similarity is unreliable

**Risk 2**: Isolated discovery context receives too little information, under-discovers
- **Likelihood**: Low
- **Impact**: High (defeats the purpose of fresh discovery)
- **Mitigation**: Coverage gate (Phase 4) catches blind spots; iterative calibration of coverage summary detail level
- **Contingency**: Expand coverage summary to include threat descriptions (accepts some anchoring risk)

**Risk 3**: Coverage checklists become stale or incomplete for new component types
- **Likelihood**: Medium
- **Impact**: Low (coverage gate is a floor — findings beyond checklist are preserved)
- **Mitigation**: Schema-driven checklists in `schemas/coverage-checklists.yaml` — easy to update
- **Contingency**: Coverage gate logs warnings for unknown component types, doesn't block

**Risk 4**: Score bounding constrains legitimate high/low scores for unusual findings
- **Likelihood**: Low
- **Impact**: Low (1.0 range is generous for most categories)
- **Mitigation**: Bounds apply only to new findings from Phase 2; Phase 1 inherited scores are unbounded
- **Contingency**: Configurable bound range per category in schema

### Dependencies

**Internal Dependencies**:
- Existing pipeline skill definitions (`.claude/skills/tachi-orchestration/`, `tachi-risk-scoring/`, `tachi-control-analysis/`)
- Existing agent definitions (`.claude/agents/tachi/orchestrator.md`, `risk-scorer.md`, `control-analyzer.md`)
- Existing schemas (`schemas/finding.yaml`, `risk-scoring.yaml`, `compensating-controls.yaml`)
- SARIF fingerprint handling in output templates

**Dependency Graph**:
```
[074 Baseline-Aware Pipeline]
  ├─ Depends on: Existing /threat-model pipeline
  ├─ Depends on: Existing /risk-score pipeline
  ├─ Depends on: Existing /compensating-controls pipeline
  ├─ Depends on: schemas/risk-scoring.yaml (category defaults)
  ├─ Depends on: SARIF fingerprint spec (correlation)
  └─ Blocks: #55 (Security Progression Summary)
```

---

## Open Questions

- [ ] Should `[RESOLVED]` findings be included in the main findings table or in a separate "Resolved" section? — product-manager — Open
- [ ] What is the maximum number of targeted re-analysis iterations the coverage gate should trigger before accepting gaps? — architect — Open
- [ ] Should the `--baseline` flag accept a directory path (auto-detect files) or require individual file paths? — architect — Open
- [ ] How should the pipeline handle a baseline from a different architecture version (e.g., components renamed/removed)? — architect — Open

---

## References

### Product Documentation
- Product Vision: [product-vision.md](docs/product/01_Product_Vision/product-vision.md)

### Technical Documentation
- Constitution: [constitution.md](.aod/memory/constitution.md)
- Architecture: [README.md](docs/architecture/README.md)
- Scoring Schema: [risk-scoring.yaml](schemas/risk-scoring.yaml)
- Finding Schema: [finding.yaml](schemas/finding.yaml)
- Controls Schema: [compensating-controls.yaml](schemas/compensating-controls.yaml)

### Research & Analysis
- Option Analysis: [baseline-aware-pipeline-research.md](docs/planning/baseline-aware-pipeline-research.md)
- Variance Evidence: second-brain-mcp run comparison (Mar 25 vs Mar 31)

### Related Features
- #55: Security Progression Summary (blocked by this feature)
- #71: Deterministic Infographic Extraction
- Feature 067: Deterministic Report Data Extraction

---

## Evidence

- **Observed variance**: second-brain-mcp Mar 25 vs Mar 31 — 23% finding count drift, 0.2–0.6 score drift, ID remapping, all with zero code changes
- **Customer impact**: Cannot track remediation progress when finding IDs change between runs
- **Related work**: Feature 067 proved deterministic extraction eliminates variance at the output layer; this applies analogous thinking at the analysis layer
- **Foundation for #55**: Security Progression Summary requires stable finding IDs to compute meaningful deltas
- **SARIF precedent**: `partialFingerprints` already exist in pipeline output for GitHub Code Scanning correlation — this promotes them to primary tracking mechanism

---

## Definition of Done

- [ ] `/threat-model` reads previous `threats.md` as baseline when present
- [ ] Phase 1 carries forward findings with stable IDs and inherited risk levels
- [ ] Phase 2 runs discovery in isolated context (architecture + coverage summary only)
- [ ] Phase 2 findings scored with category-bounded CVSS (+/- 1.0 from `schemas/risk-scoring.yaml` defaults)
- [ ] Phase 3 deduplicates Phase 2 findings against baseline (baseline version wins on match)
- [ ] Phase 4 coverage gate checks minimum threat categories per component type
- [ ] `/risk-score` inherits scores for unchanged findings, scores only new findings fresh
- [ ] `/compensating-controls` carries forward control status, re-scans only changed files
- [ ] Output includes delta annotations: `[NEW]`, `[UNCHANGED]`, `[UPDATED]`, `[RESOLVED]`
- [ ] Output frontmatter includes `baseline_source` and `baseline_date`
- [ ] SARIF fingerprints used as primary finding correlation mechanism
- [ ] Running pipeline twice on unchanged codebase produces identical finding IDs and scores
- [ ] Running pipeline after a fix correctly marks the targeted finding as `[RESOLVED]`
- [ ] Coverage gate flags when a required threat category is missing for a component
- [ ] Tested against second-brain-mcp (real-world variance case) and agentic-app example
