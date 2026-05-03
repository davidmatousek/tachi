---
prd:
  number: 129
  topic: attack-tree-delta-sub-agent
  created: 2026-04-13
  delivered: 2026-04-14
  status: Delivered
  type: feature
  pr: 162
  spec: specs/129-attack-tree-delta/spec.md
triad:
  pm_signoff: { agent: product-manager, date: 2026-04-13, status: APPROVED, notes: "PRD author — problem well-evidenced, scope contained" }
  architect_signoff: { agent: architect, date: 2026-04-13, status: APPROVED_WITH_CONCERNS, notes: "5 items (3 MEDIUM, 2 LOW): leaf label matching granularity, gate-type detection, attack_tree_count reversal framing. Details: .aod/results/architect-prd-129.md" }
  techlead_signoff: { agent: team-lead, date: 2026-04-13, status: APPROVED_WITH_CONCERNS, notes: "4 items (3 LOW, 1 INFO): file count underestimate (7 not 3-5), worked example needed, agent roster update. Details: .aod/results/team-lead-prd-129.md" }
source:
  idea_id: 129
  story_id: null
---

# Attack Tree Delta Sub-Agent - Product Requirements Document

**Status**: Delivered
**Created**: 2026-04-13
**Delivered**: 2026-04-14 (PR #162 squash-merged to main)
**Author**: product-manager
**Reviewers**: architect, team-lead
**Priority**: P1 (ICE: 24/30)

---

## Executive Summary

### The One-Liner

Extract attack tree generation from the overloaded threat-report agent into a focused sub-agent so that delta reconciliation actually works.

### Problem Statement

The threat-report agent (337 lines) handles narrative generation (Sections 1-4, 6-8), attack trees (Section 5), delta handling, formatting, dual output, correlation groups, and MAESTRO passthrough. The three-rule attack tree delta logic (Rules 1-3) is ~4 lines buried in the middle of this cognitive noise, and **Rule 3 (reconciliation) never fires in practice**.

Evidence from session investigation (2026-04-09) against `second-brain-mcp` threat model run:

1. **Contradictory instructions**: Rule 2 says "generate fresh for ALL when delta > 0", but per-finding logic elsewhere says "skip UNCHANGED findings and output carry-forward note only" -- these cancel each other out.
2. **Zero reinforcement**: `attack-tree-construction.md`, `narrative-templates.md`, and `attack-tree-examples.md` contain zero mentions of baseline comparison or reconciliation.
3. **Schema conflict**: `schemas/report.yaml` defines `attack_tree_count` as "one per Critical/High", but `templates/tachi/output-schemas/threat-report.md` says "NEW or UPDATED only, UNCHANGED excluded".
4. **Broken count metric**: Baseline reported `attack_tree_count: 21`, new run reported `16` despite generating 22 files.
5. **Observed structural drift**: Every UNCHANGED attack tree was materially regenerated with different node labels, added AND gates, and restructured decomposition -- no evidence reconciliation was attempted.
6. **No concrete heuristics**: Rule 3's "structurally similar vs materially different" has no comparison algorithm.

### Proposed Solution

Extract attack tree generation into a dedicated `attack-tree-delta` sub-agent spawned by the threat-report agent for Section 5. The sub-agent receives atomic inputs (findings list, delta counts, baseline path), executes deterministic rules, writes standalone files, and returns a structured manifest. The threat-report agent assembles Section 5 inline content from the manifest.

### Success Criteria

- Rule 3 reconciliation fires correctly when UNCHANGED findings have structurally similar baseline trees
- `attack_tree_count` definition is consistent across schema, template, and agent
- Threat-report agent line count decreases by ~40% (attack tree logic extracted)
- Backward compatible: reports without baselines produce identical output

### Timeline

Single-phase implementation. Low-medium effort -- 7 files (1 new agent + 6 modifications), no structural schema changes, no pipeline changes, contained blast radius.

---

## Strategic Alignment

### Product Vision Alignment
**Reference**: `docs/product/01_Product_Vision/product-vision.md`

tachi's vision is to be the default threat modeling toolkit for agentic AI applications. Reliable delta reconciliation is essential for iterative threat modeling -- teams re-run tachi as their architecture evolves and expect consistent, trustworthy output when nothing has changed.

### Roadmap Fit

This is a correctness fix for an existing feature (baseline-aware pipeline, Feature 074) that was delivered 2026-04-01. The attack tree delta logic shipped as part of the threat-report agent but never worked as designed. This PRD addresses the root cause: cognitive overload in a monolithic agent.

---

## Target Users & Personas

### Primary Persona: Security-Aware Developer

**Role**: Developer building AI agents who runs tachi iteratively as architecture evolves
**Experience**: Moderate security knowledge, relies on tachi for threat modeling guidance
**Goals**: Get accurate, consistent threat models across architecture iterations
**Pain Points**: When re-running tachi after minor changes, attack trees are completely regenerated even for unchanged findings, making it impossible to track what actually changed

**Why This Matters**: Without reliable reconciliation, developers cannot trust that "UNCHANGED" means unchanged -- they must manually diff every attack tree, defeating the purpose of automated delta tracking.

---

## User Stories

### US-1: Deterministic Attack Tree Carry-Forward

**When** I re-run tachi on an architecture that has minor changes (some findings NEW, most UNCHANGED),
**I want to** see UNCHANGED findings retain their baseline attack trees verbatim,
**So I can** trust that only genuinely affected attack trees were regenerated.

**Acceptance Criteria**:
- **Given** a baseline with 20 attack trees and a new run with 2 NEW findings and 18 UNCHANGED, **when** the sub-agent executes Rule 1 (all UNCHANGED) or Rule 2 (mixed delta), **then** UNCHANGED trees are byte-identical to baseline copies
- **Given** Rule 2 applies (mixed delta), **when** the sub-agent compares a fresh UNCHANGED tree against its baseline, **then** "structurally similar" is determined by a concrete algorithm (node count + edge count + leaf label overlap >= 80%), not subjective judgment
- **Given** the sub-agent completes, **when** the threat-report agent receives the manifest, **then** Section 5 inline content is assembled from standalone files without re-reading all trees

### US-2: Consistent Attack Tree Count

**When** I review the threat report metadata,
**I want to** see `attack_tree_count` reflect a single, unambiguous definition,
**So I can** cite the count in security reviews without footnotes about what it means.

**Acceptance Criteria**:
- **Given** the schema, template, and agent all define `attack_tree_count`, **when** the sub-agent writes the manifest, **then** the count matches a single canonical definition: total attack trees produced (both fresh and carried-forward)
- **Given** a run with 22 attack tree files written, **when** the report metadata is populated, **then** `attack_tree_count` equals 22

### US-3: Reduced Threat-Report Agent Complexity

**When** the threat-report agent generates a report,
**I want** attack tree logic to be delegated to a focused sub-agent,
**So that** the narrative generation and attack tree generation don't interfere with each other.

**Acceptance Criteria**:
- **Given** the current threat-report agent is 337 lines, **when** the refactor is complete, **then** attack tree rules, baseline file I/O, and comparison logic are in the sub-agent (threat-report agent decreases by ~100+ lines)
- **Given** the sub-agent is spawned by the threat-report agent, **when** the sub-agent returns, **then** the return follows the 15-line subagent return policy with a structured manifest file on disk

---

## Functional Requirements

### FR-1: Attack Tree Delta Sub-Agent

**Description**: New agent at `.claude/agents/tachi/attack-tree-delta.md` that owns all attack tree generation logic.

**Inputs** (passed by threat-report agent):
- List of Critical/High findings with `delta_status` (NEW, UNCHANGED, UPDATED, RESOLVED)
- `delta_counts` from `threats.md` frontmatter
- Baseline directory path (derived from `baseline.source`)
- Output directory path

**Processing** (deterministic rules):

| Rule | Condition | Behavior |
|------|-----------|----------|
| Rule 1 | All findings UNCHANGED (`delta_counts.new == 0 && delta_counts.updated == 0 && delta_counts.resolved == 0`) | Read and copy baseline trees verbatim. No generation. |
| Rule 2 | Any NEW, UPDATED, or RESOLVED findings | Generate fresh trees for ALL Critical/High findings, then reconcile UNCHANGED against baseline (Rule 3). |
| Rule 3 | Per-finding reconciliation (within Rule 2) | Compare fresh tree against baseline using structural similarity algorithm. If similar: use baseline. If different: use fresh. |

**Structural Similarity Algorithm** (concrete, deterministic):
1. Parse both Mermaid trees into node count and edge count
2. Extract leaf node labels (terminal attack steps)
3. Compute overlap: `similarity = matching_leaf_labels / max(baseline_leaves, fresh_leaves)`
4. Threshold: similarity >= 0.80 -> use baseline; < 0.80 -> use fresh
5. Tie-breaking: if node count differs by >20%, use fresh regardless of label overlap

**Outputs**:
- Standalone files: `attack-trees/{finding-id}-attack-tree.md`
- Manifest file: `attack-trees/.manifest.json`

### FR-2: Structured Manifest Format

**Description**: JSON manifest written to `attack-trees/.manifest.json` enabling the threat-report agent to assemble Section 5 without re-reading individual trees.

```json
{
  "rule_applied": "Rule 2",
  "attack_tree_count": 22,
  "trees": [
    {
      "finding_id": "S-1",
      "delta_status": "UNCHANGED",
      "action": "carried_forward",
      "similarity_score": 0.95,
      "file_path": "attack-trees/S-1-attack-tree.md"
    },
    {
      "finding_id": "D-9",
      "delta_status": "NEW",
      "action": "generated_fresh",
      "similarity_score": null,
      "file_path": "attack-trees/D-9-attack-tree.md"
    }
  ],
  "summary": {
    "fresh": 3,
    "carried_forward": 18,
    "regenerated": 1
  }
}
```

### FR-3: Threat-Report Agent Refactor

**Description**: Refactor the threat-report agent to delegate Section 5 to the sub-agent.

**Changes**:
- Remove Rules 1-3 logic from `threat-report.md` (lines ~218-229)
- Remove baseline file I/O for attack trees
- Add sub-agent spawn instruction with atomic inputs
- Add manifest consumption logic for Section 5 inline assembly
- Preserve all other sections (1-4, 6-8) unchanged

### FR-4: Schema Alignment

**Description**: Align `attack_tree_count` definition across all locations.

**Canonical definition**: Total attack trees produced (fresh + carried-forward). Equals the number of files in `attack-trees/` directory.

**Locations to align**:
- `schemas/report.yaml` -- update description
- `templates/tachi/output-schemas/threat-report.md` -- update Section 5 schema
- Sub-agent manifest -- use canonical definition

### FR-5: Reference File Updates

**Description**: Update attack tree reference files with reconciliation guidance.

**Files**:
- `.claude/skills/tachi-threat-reporting/references/attack-tree-construction.md` -- add section on baseline comparison with worked example
- `.claude/skills/tachi-threat-reporting/references/narrative-templates.md` -- add delta annotation guidance for Section 5

---

## Non-Functional Requirements

### Backward Compatibility

- Reports without baselines (first-run) produce identical output to current behavior
- Sub-agent handles missing baseline directory gracefully (falls back to fresh generation for all)
- Manifest file is additive -- existing consumers of `attack-trees/` directory are unaffected
- No changes to pipeline orchestrator, risk-scorer, control-analyzer, or report-assembler

### Performance

- Sub-agent overhead: negligible -- spawns once per report, returns structured manifest
- No additional API calls or external dependencies

### Determinism

- Same inputs produce same outputs (per ADR-021)
- Structural similarity algorithm is purely arithmetic -- no LLM judgment in comparison
- Manifest JSON is deterministic (sorted keys, stable ordering)

---

## Scope & Boundaries

### In Scope (MVP)

- New `.claude/agents/tachi/attack-tree-delta.md` agent definition
- Refactor `threat-report.md` to spawn sub-agent and consume manifest
- Structured `.manifest.json` format in `attack-trees/` directory
- Concrete structural similarity algorithm (node count + edge count + leaf label overlap)
- Align `attack_tree_count` definition across schema and template
- Update `attack-tree-construction.md` with reconciliation guidance and worked example
- Update `narrative-templates.md` with delta annotation guidance

### Out of Scope

- Pipeline orchestrator changes (sub-agent is internal to threat-report step)
- Schema-level changes to `schemas/finding.yaml` or `schemas/report.yaml` structure (only description updates)
- Downstream impact on risk-scorer, control-analyzer, report-assembler, infographics (they consume `threats.md`, not attack trees)
- Mermaid rendering changes (Feature 130 scope)
- Attack chain correlation changes (Feature 141 scope)

### Assumptions

- The sub-agent pattern (spawn + structured return) is proven in tachi and works reliably
- Structural similarity at 80% threshold is sufficient for reconciliation decisions -- may need tuning based on real-world data
- `attack_tree_count` should count all produced trees (canonical definition A from the investigation)

---

## Risks & Dependencies

### Technical Risks

**Risk 129.1**: Structural similarity threshold (80%) may be too aggressive or too lenient
- **Likelihood**: Medium
- **Impact**: Low (threshold is a single constant, trivially adjustable)
- **Mitigation**: Document the threshold as configurable. Test against all 6 example attack-tree sets.

**Risk 129.2**: Mermaid parse complexity for node/edge counting
- **Likelihood**: Low
- **Impact**: Medium
- **Mitigation**: Mermaid flowchart syntax is well-defined. Node count = lines matching `[label]` or `(label)`. Edge count = lines containing `-->`.

**Risk 129.3**: Sub-agent manifest may be too large for complex threat models
- **Likelihood**: Low
- **Impact**: Low (manifest is metadata only, not tree content)
- **Mitigation**: Cap manifest to essential fields. Tree content stays in standalone files.

### Dependencies

**Internal Dependencies**:
- Feature 074 (Baseline-Aware Pipeline) -- delivered, provides `delta_status` and `delta_counts`
- Feature 112 (Attack Path Pages) -- delivered, provides `attack-trees/` directory structure
- Feature 130 (mmdc Hard Prerequisite) -- delivered, provides fail-fast behavior for missing mmdc

**No external dependencies**.

---

## Open Questions

- [ ] Should the manifest include inline Mermaid content for Section 5 assembly, or should the threat-report agent read standalone files? -- architect -- 2026-04-13 -- Open (Architect recommends: file reads only, manifest metadata only)
- [ ] Should the similarity threshold be exposed as a configurable parameter in the sub-agent, or hardcoded? -- architect -- 2026-04-13 -- Open (Architect recommends: hardcoded with named constant)
- [ ] Should the sub-agent handle dual output (inline + standalone), or only produce standalone files with threat-report handling inline assembly? -- architect -- 2026-04-13 -- Open (Architect recommends: standalone only, threat-report assembles inline)
- [ ] How is the Dual Output Location section (threat-report.md lines 302-330) split between parent and sub-agent after refactoring? -- architect -- 2026-04-13 -- Open
- [ ] Explicit confirmation that mmdc validation is NOT the sub-agent's concern (sub-agent produces Mermaid source, not rendered PNGs) -- architect -- 2026-04-13 -- Open (Architect recommends: out of scope for sub-agent)

---

## References

### Product Documentation
- Product Vision: `docs/product/01_Product_Vision/product-vision.md`
- Related PRDs: Feature 074 (Baseline-Aware Pipeline), Feature 112 (Attack Path Pages), Feature 130 (mmdc Hard Prerequisite)

### Technical Documentation
- Constitution: `.aod/memory/constitution.md`
- ADR-021: SOURCE_DATE_EPOCH for deterministic PDF comparison
- ADR-022: mmdc Hard Prerequisite

### Source Investigation
- GitHub Issue #129: Attack Tree Delta Sub-Agent
- Session investigation (2026-04-09): `second-brain-mcp` threat model delta run analysis
