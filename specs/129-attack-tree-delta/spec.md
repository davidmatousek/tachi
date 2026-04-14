---
prd_reference: docs/product/02_PRD/129-attack-tree-delta-sub-agent-2026-04-13.md
triad:
  pm_signoff:
    agent: product-manager
    date: 2026-04-13
    status: APPROVED_WITH_CONCERNS
    notes: "3 items (1 MEDIUM, 2 LOW): SC-001 coverage boundary note, correlation_group design decision, OQ resolution trace. Details: .aod/results/pm-spec-129.md"
  architect_signoff: null
  techlead_signoff: null
---

# Feature Specification: Attack Tree Delta Sub-Agent

**Feature Branch**: `129-attack-tree-delta`
**Created**: 2026-04-13
**Status**: Approved
**PRD**: `docs/product/02_PRD/129-attack-tree-delta-sub-agent-2026-04-13.md`
**Input**: Extract attack tree generation and delta reconciliation from threat-report agent into a focused sub-agent

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Deterministic Attack Tree Carry-Forward (Priority: P1)

When a developer re-runs tachi on an architecture with minor changes, UNCHANGED findings must retain their baseline attack trees verbatim. This is the core value proposition: developers trust that "UNCHANGED" means the attack tree is byte-identical to the baseline, and only genuinely affected trees are regenerated.

**Why this priority**: Without reliable carry-forward, developers cannot trust delta reports. They must manually diff every attack tree, defeating the purpose of automated baseline comparison (Feature 074).

**Independent Test**: Run tachi on an architecture with a baseline, introduce one NEW finding while leaving others UNCHANGED. Verify UNCHANGED trees are byte-identical to baseline copies. Verify the NEW finding gets a fresh tree.

**Acceptance Scenarios**:

1. **Given** a baseline run with 20 attack trees and a new run where all findings are UNCHANGED (delta_counts: new=0, updated=0, resolved=0), **When** the sub-agent executes, **Then** all 20 trees are copied verbatim from baseline (byte-identical) and no fresh generation occurs (Rule 1).

2. **Given** a baseline with 20 trees and a new run with 2 NEW findings and 18 UNCHANGED, **When** the sub-agent executes Rule 2, **Then** fresh trees are generated for all 20 Critical/High findings, and the sub-agent applies per-finding reconciliation (Rule 3) to the 18 UNCHANGED findings.

3. **Given** Rule 3 reconciliation runs on an UNCHANGED finding, **When** the fresh tree has the same leaf labels (>= 80% token-level overlap), same gate types (AND/OR), and node count within 20%, **Then** the baseline version is used for consistency.

4. **Given** Rule 3 reconciliation runs on an UNCHANGED finding, **When** the fresh tree differs materially (leaf overlap < 80%, or gate types changed, or node count differs by > 20%), **Then** the fresh version is used and annotated as regenerated.

---

### User Story 2 - Consistent Attack Tree Count Metric (Priority: P2)

When a developer reviews threat report metadata, the `attack_tree_count` field must reflect a single, unambiguous definition that is consistent across all locations where it appears (schema, output template, agent output).

**Why this priority**: Inconsistent counts undermine report credibility. A developer citing "16 attack trees" in a security review when the actual count is 22 creates confusion and erodes trust.

**Independent Test**: Generate a threat report with a baseline (mixed delta). Verify `attack_tree_count` in the report frontmatter equals the number of attack tree files in the `attack-trees/` directory.

**Acceptance Scenarios**:

1. **Given** a run that produces 22 attack tree files (3 fresh + 19 carried-forward), **When** the report frontmatter is populated, **Then** `attack_tree_count` equals 22.

2. **Given** the `attack_tree_count` definition in `schemas/report.yaml`, the output template, and the sub-agent manifest, **When** compared, **Then** all three define it identically as "total attack trees produced (fresh + carried-forward)".

3. **Given** this definition reverses the Feature 104 decision (which counted only NEW/UPDATED trees), **When** the schema description is updated, **Then** the change is documented as a deliberate reversal with rationale.

---

### User Story 3 - Reduced Threat-Report Agent Complexity (Priority: P3)

When the threat-report agent generates a report, attack tree logic must be delegated to a focused sub-agent so that narrative generation (Sections 1-4, 6-8) and attack tree generation (Section 5) do not interfere with each other.

**Why this priority**: The threat-report agent at 337 lines exceeds its Report tier hard cap (300 lines). Extracting attack tree logic (~100+ lines) brings it back within compliance and isolates the delta reconciliation concern where it can receive focused attention.

**Independent Test**: After refactoring, verify the threat-report agent delegates Section 5 to the sub-agent, receives a structured manifest back, and assembles inline content from standalone files.

**Acceptance Scenarios**:

1. **Given** the current threat-report agent is 337 lines, **When** the refactor is complete, **Then** the threat-report agent is under the 300-line Report tier hard cap.

2. **Given** the sub-agent completes its work, **When** it returns to the threat-report agent, **Then** the return follows the subagent return policy (max 15 lines / ~200 tokens) and a structured manifest file exists on disk.

3. **Given** a report generated without a baseline (first run), **When** compared to the same report generated before the refactor, **Then** the output is identical (backward compatible).

---

### Edge Cases

- **Missing baseline directory**: Sub-agent receives a baseline path that does not exist or is empty. Must fall back to fresh generation for all Critical/High findings (effectively Rule 2 without reconciliation).
- **Missing individual baseline tree**: Rule 1 applies (all UNCHANGED) but one baseline tree file is missing. Sub-agent must generate fresh for that finding only, carry forward all others.
- **Zero Critical/High findings**: No attack trees needed. Sub-agent writes an empty manifest and returns immediately.
- **Baseline tree has invalid Mermaid syntax**: Sub-agent cannot parse node/edge counts. Must treat as "materially different" and use fresh version.
- **All findings are RESOLVED**: No Critical/High findings remain. Sub-agent writes empty manifest.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST provide a dedicated sub-agent that owns all attack tree generation and delta reconciliation logic, separate from the threat-report narrative agent.

- **FR-002**: The sub-agent MUST implement three deterministic rules for attack tree handling:
  - **Rule 1** (all UNCHANGED): Copy baseline trees verbatim with no fresh generation.
  - **Rule 2** (any NEW/UPDATED/RESOLVED): Generate fresh trees for ALL Critical/High findings, then apply Rule 3 to each UNCHANGED finding.
  - **Rule 3** (per-finding reconciliation): Compare fresh tree against baseline using the structural similarity algorithm defined in FR-003.

- **FR-003**: The structural similarity algorithm MUST be deterministic and use these steps:
  1. Parse both Mermaid trees to extract node count, edge count, and gate types (AND/OR)
  2. Extract leaf node labels (nodes with `_leaf` in their ID)
  3. For each leaf label pair, compute token-level Jaccard similarity (word overlap after lowercasing and stripping punctuation); a per-label match threshold of >= 0.70 counts as a match
  4. Compute tree-level similarity: `matched_leaf_pairs / max(baseline_leaves, fresh_leaves)`
  5. Compare ordered gate-type lists: if any gate type differs (AND vs OR or vice versa), treat as materially different regardless of leaf similarity
  6. Threshold: tree-level similarity >= 0.80 AND gate types identical AND node count within 20% -> use baseline; otherwise use fresh

- **FR-004**: The sub-agent MUST write a structured manifest file at `attack-trees/.manifest.json` containing:
  - Which rule was applied (Rule 1, Rule 2, or no-baseline)
  - Total attack tree count
  - Per-tree entry: finding ID, delta status, action taken (carried_forward / generated_fresh / regenerated), similarity score (when Rule 3 applies), file path
  - Summary counts: fresh, carried_forward, regenerated

- **FR-005**: The sub-agent MUST write standalone attack tree files to `attack-trees/{finding-id}-attack-tree.md` following the existing naming convention (always lowercase).

- **FR-006**: The threat-report agent MUST delegate Section 5 generation to the sub-agent by spawning it with atomic inputs (findings list, delta counts, baseline path, output path) and consuming the manifest to assemble inline Section 5 content.

- **FR-007**: The sub-agent MUST NOT produce inline Section 5 content. It writes standalone files only. The threat-report agent reads standalone files using the manifest and assembles inline content.

- **FR-008**: The `attack_tree_count` definition MUST be aligned to a single canonical meaning across all locations: "total attack trees produced (fresh + carried-forward), equal to the number of files in the `attack-trees/` directory." This reverses the Feature 104 decision (which counted only NEW/UPDATED) and must be documented as a deliberate change.

- **FR-009**: The sub-agent MUST NOT validate mmdc availability or render Mermaid to PNG. It produces Mermaid source only. Rendering is a downstream concern (report-assembler / security-report command).

- **FR-010**: The attack tree reference file (`attack-tree-construction.md`) MUST be updated with reconciliation guidance including a worked example showing the structural similarity algorithm applied to a concrete pair of trees (one similar, one different).

### Key Entities

- **Attack Tree Manifest**: Structured metadata describing the result of sub-agent execution -- rule applied, per-tree decisions, summary counts. Written to `attack-trees/.manifest.json`.
- **Structural Similarity Score**: A numeric value (0.0 to 1.0) representing how closely a fresh tree matches its baseline, computed from leaf label overlap, gate types, and node counts.
- **Delta Rule**: One of three deterministic rules (Rule 1, 2, or 3) governing whether attack trees are carried forward, freshly generated, or reconciled.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Rule 3 reconciliation correctly identifies structurally similar trees (leaf overlap >= 80%, identical gate types, node count within 20%) and carries forward the baseline version. Verified by running against the 2 example sets with attack trees (`mermaid-agentic-app` and `agentic-app`).

- **SC-002**: `attack_tree_count` is numerically identical across the manifest, the report frontmatter, and the number of files in `attack-trees/` for all 6 example outputs.

- **SC-003**: Threat-report agent line count is under the 300-line Report tier hard cap after extraction.

- **SC-004**: Reports generated without a baseline produce output identical to pre-refactor behavior (backward compatibility). Verified via existing `test_backward_compatibility.py` suite -- 5 baselines byte-identical under `SOURCE_DATE_EPOCH=1700000000`.

- **SC-005**: The sub-agent targets Leaf tier (100-150 lines, hard cap 200 lines).

- **SC-006**: The sub-agent return follows the subagent return policy: max 15 lines / ~200 tokens, with detailed results in the manifest file on disk.

## Assumptions

- The sub-agent pattern (spawn + structured return) works reliably when the threat-report agent is the parent. No existing precedent for pipeline agent spawning pipeline agent in tachi, but the mechanism (Agent tool) is the same as orchestrator-to-threat-agent dispatching.
- Token-level Jaccard similarity at 0.70 per-label and 0.80 tree-level thresholds are sufficient for LLM-generated Mermaid labels. These are named constants, trivially adjustable if real-world data reveals they need tuning.
- The `attack_tree_count` canonical definition ("total produced") is more useful to consumers than the Feature 104 definition ("fresh only"). This is a deliberate product decision reversing a prior architectural choice.
- Mermaid `flowchart TD` syntax is sufficiently structured for node/edge/leaf/gate-type parsing by an LLM following explicit counting instructions with the constrained ID format defined in `attack-tree-construction.md`.

## Scope Boundaries

**In scope**:
- New sub-agent definition (`.claude/agents/tachi/attack-tree-delta.md`)
- Threat-report agent refactor (extract Section 5 logic, add sub-agent spawning)
- Structured manifest format (`.manifest.json`)
- Structural similarity algorithm with token-level Jaccard, gate-type comparison, and node-count guard
- Schema description alignment (`schemas/report.yaml`, `templates/output-schemas/threat-report.md`)
- Reference file updates (`attack-tree-construction.md` reconciliation guidance + worked example)
- Agent roster update (`_README.md`)

**Out of scope**:
- Pipeline orchestrator changes
- Schema structure changes (only description text updates)
- Downstream agent changes (risk-scorer, control-analyzer, report-assembler, infographics)
- Mermaid rendering or mmdc validation
- Attack chain correlation (Feature 141)
- New Python scripts or test files (agent-instruction-only changes)
