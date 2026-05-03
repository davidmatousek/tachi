---
prd:
  number: "010"
  topic: deduplication-risk-rating
  created: 2026-03-22
  status: Delivered
  type: feature
triad:
  pm_signoff: {agent: product-manager, date: 2026-03-22, status: approved, notes: "PRD drafted by PM via ~aod-define skill with GitHub Issue #10 user stories and consumer guide research as primary inputs"}
  architect_signoff: {agent: architect, date: 2026-03-22, status: approved_with_concerns, notes: "Technically feasible. 8 findings (0 critical, 2 high, 4 medium, 2 low). High: Correlated Findings should be subsection (4a) to preserve 7-section schema; coverage matrix cell model needs unification. All addressable in spec phase."}
  techlead_signoff: {agent: team-lead, date: 2026-03-22, status: approved_with_concerns, notes: "Feasible in 1 sprint (85% confidence, 3.0-3.5h). Effort sizing L/S/M accurate. 3-wave execution strategy. 2 medium concerns: orchestrator validation checklist update needed as explicit task; section numbering cascade strategy needed before tasks."}
source:
  idea_id: 10
  story_id: null
---

# Deduplication & Risk Rating - Product Requirements Document

**Status**: Delivered
**Created**: 2026-03-22
**Author**: product-manager
**Reviewers**: architect, team-lead
**Phase**: Phase 1 (Foundation)
**Priority**: P1 (High)

---

## Executive Summary

### The One-Liner
Enhance the orchestrator with cross-agent finding deduplication, correlation tracking, and a coverage matrix so that overlapping threats from multiple agents are merged into single correlated findings with calibrated risk ratings.

### Problem Statement
Developers running tachi's threat model against an agentic architecture receive findings from up to 11 agents (6 STRIDE + 5 AI). Several threat categories naturally overlap when targeting the same component — Tampering and Data-Poisoning both flag data integrity issues, Privilege-Escalation and Agent-Autonomy both flag excessive permissions, Information-Disclosure and Prompt-Injection both flag information leakage. Without deduplication, the same underlying vulnerability appears as multiple separate entries, inflating the finding count and making the threat model harder to triage.

The orchestrator (F-003, delivered) already validates risk levels against the OWASP 3×3 matrix and generates a coverage matrix. However, the coverage matrix counts all individual findings without detecting overlap, and no correlation logic exists. When the Tampering agent says "Unsanitized input causes data corruption on LLM Agent Orchestrator" and the Data-Poisoning agent says "Unvalidated data input enables poisoning on LLM Agent Orchestrator," these appear as two independent findings despite describing the same underlying attack surface.

The result: noisy output that obscures the real threat landscape. Security analysts must manually deduplicate findings to understand the actual risk posture, and coverage matrix counts overstate the analysis depth.

### Proposed Solution
Add a deduplication and correlation phase to the orchestrator's assembly step (Phase 3: Determine Countermeasures) that:

1. **Detects overlapping findings** — When two or more findings from different agents target the same component and describe semantically related threats (same attack surface, similar vulnerability class), they are flagged as correlated
2. **Correlates into grouped findings** — Correlated findings are grouped under a single primary finding that shows all contributing agent perspectives (e.g., "T-2 + LLM-1: unvalidated input on LLM Agent Orchestrator — Tampering perspective: data corruption risk; Data-Poisoning perspective: training data manipulation risk")
3. **Preserves originals for audit** — Individual findings remain in the per-agent tables (STRIDE and AI sections); correlation is shown in a new Correlated Findings section and reflected in the coverage matrix
4. **Enhances the coverage matrix** — Shows deduplicated finding counts per component per category, with zero-coverage cells highlighted as potential analysis gaps
5. **Formalizes risk rating documentation** — Although the OWASP 3×3 matrix validation is already implemented, this feature documents the matrix in the output and adds a risk calibration summary

The deduplication logic is implemented as **orchestrator prompt instructions**, not application code. It extends the existing `agents/orchestrator.md` with correlation rules applied during the assembly phase. The approach uses deterministic, rule-based matching (same component + overlapping threat category pairs) rather than fuzzy semantic similarity, ensuring reproducible and auditable results.

### Success Criteria
- When multiple agents flag the same component for related threats, correlated findings appear in a dedicated Correlated Findings section with all contributing agent perspectives listed
- Original individual findings are preserved in their respective STRIDE and AI agent tables for audit trail
- Coverage matrix shows deduplicated counts (unique threats per component per category, not raw finding count)
- Zero-coverage cells in the coverage matrix are marked to highlight analysis gaps
- Risk summary counts reflect deduplicated findings, not raw counts
- The OWASP 3×3 risk matrix is documented in the output for transparency
- Running the orchestrator against `examples/mermaid-agentic-app/input.md` produces at least one correlated finding group (expected: Tampering+Data-Poisoning overlap on LLM components)
- Running against a traditional architecture with no AI components produces zero AI-category findings and no false correlations

### Timeline
Target: 1 development sprint (estimated during Team-Lead feasibility review)

---

## Strategic Alignment

### Product Vision Alignment
**Reference**: [product-vision.md](../01_Product_Vision/product-vision.md)

This feature directly supports the mission of being an "automated threat modeling toolkit" by making threat model output actionable rather than noisy. Deduplication transforms raw agent output into a curated threat landscape that developers can act on immediately. The coverage matrix gives teams confidence that all components have been analyzed across all 8 threat categories (6 STRIDE + 2 AI), while correlated findings show cross-cutting threats that single-agent analysis would miss.

Without deduplication, tachi produces accurate but redundant findings that require manual post-processing — undermining the "automated" promise. With deduplication, the output is a ready-to-triage threat model.

### Roadmap Fit
**Phase**: Phase 1 (Foundation)
**Dependencies**: F-001 (delivered) — repository skeleton, interface contract, schemas; F-003 (delivered) — orchestrator with dispatch, assembly, and risk validation; F-005 (delivered) — STRIDE agents producing component-specific findings; F-007 (delivered) — AI agents producing component-specific findings
**Blocks**: F-009 (Platform Adapters — wraps orchestrator+agents for specific platforms; benefits from cleaner deduplicated output)

This is the final Phase 1 feature that completes the core threat modeling pipeline. F-001 built the skeleton, F-003 built the orchestrator, F-005 validated STRIDE agents, and F-007 validated AI agents. This feature ensures the assembled output from all 11 agents is coherent, deduplicated, and actionable. After this, the core pipeline is complete and ready for platform adapter work (F-009).

---

## Target Users & Personas

### Primary Persona: AI Agent Developer
- **Role**: Software developer building agentic AI applications
- **Experience**: Proficient in code, new to threat modeling methodology
- **Pain Point**: Receives 15–25 findings from a single threat model run; many describe the same underlying issue from different angles. Must manually identify which findings overlap before they can prioritize remediation
- **Value**: Deduplicated output with correlated findings means they can go straight to remediation planning. Coverage matrix tells them which components need more analysis

### Secondary Persona: Security Analyst
- **Role**: Security professional reviewing threat models produced by development teams
- **Experience**: Deep security expertise, familiar with STRIDE and OWASP methodologies
- **Pain Point**: Raw finding lists without correlation make it difficult to assess the true risk posture. Risk ratings from different agents may feel inconsistent without visible calibration
- **Value**: Correlated findings show cross-cutting attack surfaces. The documented risk matrix and calibration summary provide confidence that risk ratings are consistently applied. Deduplicated counts in the coverage matrix give accurate metrics for security reporting

---

## User Stories

### US-1: Cross-Agent Finding Deduplication
**When** the orchestrator assembles findings from multiple agents that flagged the same component for related threats,
**I want to** see those overlapping findings correlated into a single grouped entry showing all agent perspectives,
**So I can** understand the full scope of each vulnerability without manually cross-referencing agent outputs.

**Acceptance Criteria**:
- **Given** the Tampering agent and Data-Poisoning agent both flag "LLM Agent Orchestrator" for data integrity issues, **when** the orchestrator assembles findings, **then** a correlated finding appears showing both perspectives with IDs of contributing findings (e.g., "T-2 + LLM-1")
- **Given** correlated findings exist, **when** viewing the STRIDE and AI agent tables, **then** the original individual findings are still present with their original IDs for audit trail
- **Given** two findings on different components, **when** the orchestrator checks for correlation, **then** they are NOT correlated (correlation requires same component)

**Priority**: P0
**Effort**: L (primary new logic)

### US-2: Consistent Risk Ratings with Documented Matrix
**When** I review the threat model output,
**I want to** see risk ratings calibrated using a documented likelihood × impact matrix,
**So I can** trust that severity is consistent across all agents and understand how each risk level was computed.

**Acceptance Criteria**:
- **Given** any finding in the output, **when** I check its risk level, **then** it matches the OWASP 3×3 matrix computation (e.g., HIGH likelihood × HIGH impact = Critical)
- **Given** the assembled threat model, **when** I view the Risk Summary section, **then** Critical/High/Medium/Low/Note counts are computed from deduplicated findings, not raw counts
- **Given** the output, **when** I look for risk calibration documentation, **then** the OWASP 3×3 matrix is included in the output for transparency

**Priority**: P0
**Effort**: S (risk validation already implemented; this adds documentation and dedup-aware counting)

### US-3: Coverage Matrix Across All Threat Categories
**When** I view the coverage matrix,
**I want to** see which components have been analyzed across all 8 threat categories with deduplicated finding counts,
**So I can** identify blind spots where components lack coverage.

**Acceptance Criteria**:
- **Given** a completed threat model, **when** I view the coverage matrix, **then** it shows Component × [S, T, R, I, D, E, AG, LLM] with finding counts per cell reflecting deduplicated (not raw) counts
- **Given** a cell in the coverage matrix with zero findings, **when** I view it, **then** it is visually marked (e.g., "—" with a note) to highlight the coverage gap
- **Given** a component that is only analyzed by STRIDE agents (not AI-applicable), **when** I view its AI columns, **then** they show "n/a" (not applicable) rather than "0" (analyzed but no findings)

**Priority**: P1
**Effort**: M (extends existing coverage matrix with dedup awareness and gap highlighting)

---

## Functional Requirements

### FR-1: Correlation Detection Algorithm

**Description**: Rule-based algorithm that identifies when findings from different agents describe the same underlying threat on the same component.

**Correlation Rules** (applied during orchestrator Phase 3 assembly):

| Rule | Agent Pair | Condition | Rationale |
|------|------------|-----------|-----------|
| CR-1 | Tampering + Data-Poisoning | Same component, both flag data integrity | Data corruption from different lenses |
| CR-2 | Privilege-Escalation + Agent-Autonomy | Same component, both flag excessive access/permissions | Permission abuse from different lenses |
| CR-3 | Information-Disclosure + Prompt-Injection | Same component, both flag information leakage | Data exfiltration from different lenses |
| CR-4 | Repudiation + Agent-Autonomy | Same component, both flag logging/accountability gaps | Audit trail gaps from different lenses |
| CR-5 | Denial-of-Service + Tool-Abuse | Same component, both flag resource exhaustion | Resource abuse from different lenses |

**Processing**:
1. After all agents produce findings, group findings by target component
2. Within each component group, check each finding pair against correlation rules
3. When a correlation is detected, create a correlation group linking the finding IDs
4. A finding may belong to at most one correlation group (no transitive chaining)

**Edge Cases**:
- **Same-category findings**: Two findings from the same agent category (e.g., two Tampering findings on the same component) are NOT correlated — dedup only applies across different agents
- **Multi-agent correlations**: If three agents flag the same component and two pairs match correlation rules, they form one correlation group containing all three findings
- **No match**: Findings that don't match any correlation rule remain independent

### FR-2: Correlated Findings Output Section

**Description**: New output section in `threats.md` between the AI Agent tables and the Coverage Matrix.

**Format**:
```markdown
## Correlated Findings

| Group | Findings | Component | Threat Summary | Risk Level |
|-------|----------|-----------|----------------|------------|
| CG-1 | T-2, LLM-1 | LLM Agent Orchestrator | Unvalidated input — Tampering: data corruption risk; Data-Poisoning: training data manipulation risk | High |
```

- **Group ID**: `CG-N` (Correlation Group, sequential)
- **Findings**: Comma-separated list of original finding IDs from contributing agents
- **Component**: The shared target component
- **Threat Summary**: Concatenation of each agent's perspective, prefixed by category name
- **Risk Level**: Highest risk level among correlated findings (conservative merge)

### FR-3: Deduplicated Coverage Matrix

**Description**: Enhanced coverage matrix that counts unique threats per cell, not raw findings.

**Changes from current implementation**:
- When correlated findings exist for a component+category pair, the cell count reflects the deduplicated count (correlation group = 1 finding)
- Zero-coverage cells show "—" instead of empty
- Non-applicable cells (e.g., AI columns for non-AI components) show "n/a"
- Total row and column reflect deduplicated counts
- A footnote shows: "Counts reflect deduplicated findings. N correlation groups merged M individual findings."

### FR-4: Risk Calibration Documentation

**Description**: Include the OWASP 3×3 risk matrix in the output for transparency.

**Format** (new subsection in Risk Summary):
```markdown
### Risk Calibration Matrix

| | Impact: LOW | Impact: MEDIUM | Impact: HIGH |
|---|---|---|---|
| **Likelihood: HIGH** | Medium | High | Critical |
| **Likelihood: MEDIUM** | Low | Medium | High |
| **Likelihood: LOW** | Note | Low | Medium |

Risk summary counts below reflect deduplicated findings.
```

### FR-5: Updated Risk Summary

**Description**: Risk summary counts reflect deduplicated findings.

**Changes from current implementation**:
- Count column uses deduplicated finding count (correlation groups count as 1)
- A parenthetical shows raw count if different: e.g., "5 (7 raw)"
- Percentage column based on deduplicated total

---

## Non-Functional Requirements

### Correctness
- Correlation rules must be deterministic: same input always produces same correlations
- No legitimate findings may be dropped — deduplication correlates, it does not remove
- Risk level of correlation group must equal the highest risk level among its members

### Transparency
- Every correlation must be traceable: the Correlated Findings table links back to original finding IDs visible in agent tables
- The risk matrix must be documented in the output so readers can verify any risk level computation

### Backward Compatibility
- Orchestrator output format remains valid against `schemas/output.yaml` (new sections are additive)
- Existing example outputs (`examples/ascii-web-api/threats.md`) continue to be valid
- If zero correlations are detected, the Correlated Findings section shows "No cross-agent correlations detected" rather than being omitted

---

## Scope & Boundaries

### In Scope (This Feature)

**Must Have (P0)**:
- Correlation detection algorithm with 5 defined rules (FR-1)
- Correlated Findings output section (FR-2)
- Deduplicated coverage matrix (FR-3)
- Risk calibration matrix in output (FR-4)
- Deduplicated risk summary counts (FR-5)

**Should Have (P1)**:
- Zero-coverage gap highlighting in coverage matrix
- Non-applicable cell marking ("n/a") for AI columns on non-AI components

### Out of Scope

- **Fuzzy semantic similarity matching**: Correlation uses deterministic rule-based matching, not NLP or embedding-based similarity. This keeps the feature auditable and reproducible.
- **SARIF/CVSS output mapping**: SARIF integration with security-severity scores is F-006 scope. This feature focuses on the human-readable `threats.md` output.
- **Interactive dedup configuration**: Users cannot customize correlation rules in this phase. Rules are hardcoded in the orchestrator prompt.
- **Cross-component correlation**: Correlation only applies to findings targeting the same component. Systemic threats spanning multiple components are a future consideration.
- **NIST SP 800-30 5-level matrix**: Research identified this as an alternative, but the OWASP 3×3 matrix is the established standard for tachi and is already implemented.

### Assumptions
- All 11 agents (6 STRIDE + 5 AI) are validated and producing component-specific findings (confirmed: F-005 and F-007 delivered)
- The OWASP 3×3 risk validation logic in the orchestrator is correct (confirmed: implemented in orchestrator lines 804–844)
- The 5 correlation rules (CR-1 through CR-5) cover the primary overlap scenarios between STRIDE and AI agents

### Constraints
- **Prompt-only implementation**: All logic is expressed as orchestrator prompt instructions, not application code
- **Deterministic matching**: No probabilistic or LLM-based similarity — rules must be explicit and reproducible
- **Single-pass assembly**: Correlation detection runs once during Phase 3 assembly, not iteratively

---

## Risks & Dependencies

### Technical Risks

**Risk 1**: Correlation rules may miss legitimate overlaps or create false correlations
- **Likelihood**: Medium
- **Impact**: Medium
- **Mitigation**: Start with 5 conservative, well-defined rules. Validate against the example architecture. False correlations are worse than missed correlations — err on the side of fewer correlations.

**Risk 2**: Prompt complexity — adding deduplication logic may push the orchestrator prompt beyond effective instruction-following length
- **Likelihood**: Low
- **Impact**: High
- **Mitigation**: Dedup logic is a focused addition to Phase 3 (assembly). It doesn't affect Phase 1 (scope) or Phase 2 (dispatch). The orchestrator prompt is already ~1000 lines; this adds ~100 lines.

### Dependencies

**Internal Dependencies (all delivered)**:
- **F-001**: Repository skeleton, schemas, interface contract
- **F-003**: Orchestrator with dispatch, assembly, risk validation
- **F-005**: STRIDE agents producing validated findings
- **F-007**: AI agents producing validated findings

**Dependency Graph**:
```
F-008 (Deduplication & Risk Rating)
  ├─ Depends on: F-001 (delivered)
  ├─ Depends on: F-003 (delivered)
  ├─ Depends on: F-005 (delivered)
  ├─ Depends on: F-007 (delivered)
  └─ Blocks: F-009 (Platform Adapters — benefits from cleaner output)
```

---

## Open Questions

- [x] Is the OWASP 3×3 matrix the right choice? — Answered: Yes, already implemented and validated in F-003
- [x] Should correlation be transitive (A~B and B~C implies A~C)? — Answered: Yes, multi-agent correlations form one group, but a finding belongs to at most one group
- [ ] Should the interface contract (`docs/INTERFACE-CONTRACT.md`) be updated to specify deduplication behavior? — Owner: architect — Due: spec phase
- [ ] Should the `schemas/output.yaml` be extended with a Correlated Findings section schema? — Owner: architect — Due: spec phase

---

## References

### Product Documentation
- Product Vision: [product-vision.md](../01_Product_Vision/product-vision.md)
- Consumer Guide: [CONSUMER_GUIDE_TACHI.md](../../guides/CONSUMER_GUIDE_TACHI.md) §F-005
- Research: [CONSUMER_GUIDE_TACHI_RESEARCH.md](../../guides/CONSUMER_GUIDE_TACHI_RESEARCH.md) §8 (Risk Matrices), §10 (CVSS Alignment)

### Technical Documentation
- Orchestrator: [orchestrator.md](../../agents/orchestrator.md) — Phase 3 assembly, risk validation (lines 804–844)
- Finding Schema: [finding.yaml](../../schemas/finding.yaml)
- Output Schema: [output.yaml](../../schemas/output.yaml)
- Output Template: [threats.md](../../templates/threats.md)
- Interface Contract: [INTERFACE-CONTRACT.md](../../docs/INTERFACE-CONTRACT.md) — Section 3 (AI dispatch dedup note)

### Source
- GitHub Issue: #10 — Feature 008: Deduplication & Risk Rating
- Consumer Guide: §F-005 — Deduplication & Risk Rating
