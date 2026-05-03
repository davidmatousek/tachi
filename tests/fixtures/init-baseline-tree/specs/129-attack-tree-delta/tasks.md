---
triad:
  pm_signoff:
    agent: product-manager
    date: 2026-04-13
    status: APPROVED
    notes: "All 10 FRs covered. All 3 user stories mapped. Zero scope creep. 2 LOW observations. Details: .aod/results/pm-tasks-129.md"
  architect_signoff:
    agent: architect
    date: 2026-04-13
    status: APPROVED_WITH_CONCERNS
    notes: "4 findings (2 MEDIUM, 2 LOW): manifest annotation mapping, tachi registry update, naming convention preservation, schema_version field. Details: .aod/results/architect-tasks-129.md"
  techlead_signoff:
    agent: team-lead
    date: 2026-04-13
    status: APPROVED_WITH_CONCERNS
    notes: "4 findings (1 MEDIUM, 3 LOW): Wave 3 cross-story mixing, roster convention, baseline-present test gap, T008 refactor risk. Details: .aod/results/team-lead-tasks-129.md"
---

# Tasks: Attack Tree Delta Sub-Agent

**Input**: Design documents from `/specs/129-attack-tree-delta/`
**Prerequisites**: plan.md (required), spec.md (required), research.md

**Tests**: Not explicitly requested in spec. Backward compatibility verified via existing `test_backward_compatibility.py` suite.

**Organization**: Tasks grouped by user story to enable independent implementation and testing.

## Format: `[ID] [P?] [Story] Description`
- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

---

## Phase 1: Foundational (Reference Updates)

**Purpose**: Update reference files that the new sub-agent will load at workflow start. Must complete before sub-agent creation.

- [X] T001 [P] Add `## Baseline Reconciliation` section to `.claude/skills/tachi-threat-reporting/references/attack-tree-construction.md` with: Rule 3 structural similarity algorithm description, named constants (LEAF_MATCH_THRESHOLD=0.70, TREE_SIMILARITY_THRESHOLD=0.80, NODE_COUNT_VARIANCE=0.20), step-by-step instructions, and worked example showing two concrete tree comparisons (one similar at 0.92 overlap → carry forward, one different at 0.65 overlap with OR→AND gate change → use fresh). Reference the constrained node ID format (`{FindingID}_{type}{N}`) for leaf identification (`_leaf` prefix) and gate-type extraction (`_or`, `_and` prefixes). Specify tokenization rules: lowercase, strip punctuation, split on whitespace, treat hyphenated words as single tokens, no stop-word removal.

- [X] T002 [P] Add `## Section 5 Delta Annotations` section to `.claude/skills/tachi-threat-reporting/references/narrative-templates.md` with guidance on how to annotate regenerated trees in Section 5 inline content (e.g., _"Context changed since baseline — attack tree regenerated."_) and how to annotate carried-forward trees (e.g., _"Unchanged from baseline ({baseline_date})."_).

**Checkpoint**: Reference files updated — sub-agent can now load reconciliation guidance at workflow start.

---

## Phase 2: User Story 1 - Deterministic Attack Tree Carry-Forward (Priority: P1) MVP

**Goal**: Create the attack-tree-delta sub-agent that deterministically carries forward, generates, or reconciles attack trees based on delta rules.

**Independent Test**: Run tachi on an architecture with a baseline. Verify UNCHANGED trees use baseline versions when structurally similar; verify NEW findings get fresh trees; verify the manifest correctly records all decisions.

- [X] T003 [US1] Create new sub-agent definition at `.claude/agents/tachi/attack-tree-delta.md` (Leaf tier, target 100-150 lines, hard cap 200). Structure:
  1. **Frontmatter**: name `tachi-attack-tree-delta`, description, tools: [Read, Write, Glob, Grep], model: sonnet
  2. **Purpose section**: Single-concern attack tree generation and delta reconciliation
  3. **Inputs section**: Four atomic inputs (Critical/High findings list with delta_status, delta_counts from threats.md frontmatter, baseline directory path, output directory path)
  4. **MANDATORY Read**: `.claude/skills/tachi-threat-reporting/references/attack-tree-construction.md` at workflow start (detection variant pattern per ADR-023)
  5. **Rule dispatch**: Deterministic conditional on delta_counts — Rule 1 (all UNCHANGED, no NEW/UPDATED/RESOLVED) vs Rule 2 (any delta) vs no-baseline (baseline path missing/empty)
  6. **Rule 1 logic**: Read and copy baseline trees verbatim to `attack-trees/{finding-id}-attack-tree.md`. No fresh generation.
  7. **Rule 2 logic**: Generate fresh Mermaid attack trees for ALL Critical/High findings following `attack-tree-construction.md` structure/depth rules. Then apply Rule 3 to each UNCHANGED finding.
  8. **Rule 3 logic**: Structural similarity algorithm per FR-003 (parse Mermaid → node/edge/gate counts → extract leaf labels → token-level Jaccard per leaf pair at 0.70 → tree-level similarity at 0.80 → gate-type comparison → node-count 20% guard). If similar: copy baseline version. If different: keep fresh version, mark as `regenerated`.
  9. **No-baseline fallback**: If baseline directory doesn't exist or is empty, generate fresh for all (Rule 2 without reconciliation).
  10. **Edge cases**: Missing individual baseline tree → generate fresh for that finding only. Zero Critical/High findings → empty manifest. Invalid Mermaid in baseline → treat as materially different. All RESOLVED → empty manifest.
  11. **Manifest writing**: Write `attack-trees/.manifest.json` per FR-004 format (rule_applied, attack_tree_count, per-tree entries with finding_id/delta_status/action/similarity_score/file_path, summary counts).
  12. **Return format**: STATUS, RULE_APPLIED, TREES_GENERATED count, MANIFEST path (max 15 lines per subagent return policy).

- [X] T004 [US1] Externalize the structural similarity algorithm details into the `## Baseline Reconciliation` section of `attack-tree-construction.md` (added in T001) rather than inlining in the agent. Agent should reference: "Follow the structural similarity algorithm in the Baseline Reconciliation section of attack-tree-construction.md." This keeps the agent within Leaf tier line cap.

**Checkpoint**: Sub-agent created. Can be tested independently by spawning with test inputs.

---

## Phase 3: User Story 2 - Consistent Attack Tree Count Metric (Priority: P2)

**Goal**: Align `attack_tree_count` to a single canonical definition across all locations.

**Independent Test**: Verify the definition "total attack trees produced (fresh + carried-forward)" appears identically in schema, output template, and is what the manifest produces.

- [X] T005 [P] [US2] Update `attack_tree_count` description in `schemas/report.yaml` to: "Total attack trees produced (fresh + carried-forward), equal to the number of files in the attack-trees/ directory. Note: This reverses the Feature 104 definition which counted only NEW/UPDATED trees. Changed in Feature 129 because the total count is more useful to consumers and always equals the file count."

- [X] T006 [P] [US2] Update `attack_tree_count` description in `templates/tachi/output-schemas/threat-report.md` to match the canonical definition: "Total attack trees produced (fresh + carried-forward), equal to the number of `.md` files in the `attack-trees/` directory. Includes both freshly generated and baseline-carried-forward trees." Remove the Feature 104 language about "NEW or UPDATED only, UNCHANGED excluded."

**Checkpoint**: Schema aligned. The manifest's `attack_tree_count` field will always equal the file count.

---

## Phase 4: User Story 3 - Reduced Threat-Report Agent Complexity (Priority: P3)

**Goal**: Refactor threat-report agent to delegate Section 5 to the sub-agent, reducing line count below the 300-line Report tier cap.

**Independent Test**: After refactoring, verify threat-report agent spawns the sub-agent, receives manifest, and assembles Section 5 inline content correctly. Verify line count < 300.

- [X] T007 [US3] Add `Agent` to the `tools:` list in `.claude/agents/tachi/threat-report.md` frontmatter (currently has Read, Write, Glob, Grep — needs Agent for sub-agent spawning).

- [X] T008 [US3] Refactor `.claude/agents/tachi/threat-report.md` Section 5 logic:
  1. **Remove**: Rules 1-3 delta logic (lines ~218-229)
  2. **Remove**: Baseline file I/O for attack trees (read/copy logic within Section 5)
  3. **Remove**: Structural similarity comparison instructions
  4. **Add**: Sub-agent spawn instruction — use Agent tool to spawn `tachi-attack-tree-delta` with four atomic inputs: (a) Critical/High findings list with delta_status, (b) delta_counts from threats.md frontmatter, (c) baseline directory path derived from baseline.source, (d) output directory path
  5. **Add**: Manifest consumption — after sub-agent returns, read `attack-trees/.manifest.json` and assemble inline Section 5 content from standalone files using manifest ordering (Critical findings first alphabetical, then High findings alphabetical)
  6. **Preserve**: All narrative sections (1-4, 6-8) unchanged
  7. **Simplify**: Dual Output Location section — reference manifest ordering instead of re-deriving order. Standalone files are already written by sub-agent; inline assembly uses the manifest.
  8. **Clarify**: Add explicit note that correlation group cross-referencing (Section 4a) remains the threat-report agent's responsibility — the sub-agent manifest does not carry correlation data.
  9. **Verify**: Final line count is under 300-line Report tier hard cap.

- [X] T009 [US3] Update agent roster at `.claude/agents/_README.md` — add `attack-tree-delta` entry with: tier (Leaf), description (Attack tree generation and delta reconciliation sub-agent), spawned by (threat-report), note (first pipeline agent sub-spawning pattern in tachi).

**Checkpoint**: Threat-report agent refactored. Sub-agent integration complete. Line count within tier cap.

---

## Phase 5: Polish & Validation

**Purpose**: Cross-cutting validation and backward compatibility confirmation.

- [X] T010 Verify backward compatibility: Run existing `test_backward_compatibility.py` suite with `SOURCE_DATE_EPOCH=1700000000`. All 5 baselines must be byte-identical. This validates that no-baseline reports produce identical output post-refactor (SC-004).

- [X] T011 Verify sub-agent line count is within Leaf tier (100-150 target, hard cap 200) per SC-005. If over target, externalize additional content to `attack-tree-construction.md` reference.

- [X] T012 Verify threat-report agent line count is under 300-line Report tier hard cap per SC-003. Count lines excluding frontmatter.

- [X] T013 [P] Cross-check `attack_tree_count` definition consistency: Verify the identical canonical definition appears in (a) `schemas/report.yaml`, (b) `templates/tachi/output-schemas/threat-report.md`, and (c) the sub-agent's manifest writing instructions per SC-002.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Foundational)**: No dependencies — reference updates can start immediately
- **Phase 2 (US1)**: Depends on Phase 1 — sub-agent loads references at workflow start
- **Phase 3 (US2)**: No dependencies on other phases — schema updates are independent
- **Phase 4 (US3)**: Depends on Phase 2 — threat-report refactor references the sub-agent name
- **Phase 5 (Polish)**: Depends on all previous phases

### User Story Dependencies

- **US1 (P1)**: Depends on Phase 1 foundational reference updates
- **US2 (P2)**: Independent — can start after Phase 1 or in parallel with Phase 2
- **US3 (P3)**: Depends on US1 (the sub-agent must exist before threat-report can reference it)

### Within Each Phase

- T001 and T002 are parallel (different files)
- T003 depends on T001 (loads the reference file)
- T004 depends on T001 and T003 (refines the reference externalization)
- T005 and T006 are parallel (different files)
- T007, T008, T009 are sequential (frontmatter → logic → roster)
- T010-T013 are validation tasks after all implementation

### Parallel Opportunities

**Wave 1** (parallel): T001, T002 — reference file updates
**Wave 2**: T003 — sub-agent creation (depends on T001)
**Wave 3** (parallel): T004, T005, T006 — externalization + schema alignment (T004 depends on T003; T005/T006 independent)
**Wave 4**: T007 — threat-report frontmatter update
**Wave 5**: T008 — threat-report Section 5 refactor
**Wave 6**: T009 — agent roster update
**Wave 7** (parallel): T010, T011, T012, T013 — validation checks

---

## Implementation Strategy

### MVP First (US1 Only)

1. Complete Phase 1: Reference updates (T001, T002)
2. Complete Phase 2: Sub-agent creation (T003, T004)
3. **STOP and VALIDATE**: The sub-agent can be tested independently by spawning it with test inputs

### Incremental Delivery

1. Phase 1 → Phase 2 → US1 functional (MVP)
2. Phase 3 → US2 functional (schema aligned)
3. Phase 4 → US3 functional (threat-report refactored)
4. Phase 5 → all validation checks pass

---

## Notes

- All "source files" are markdown agent definitions, not application code
- No new Python scripts or test files — agent-instruction-only changes
- The existing `test_backward_compatibility.py` suite provides the backward-compat safety net
- Architect plan review flagged: verify `.claude/agents/_README.md` is the correct roster path (confirmed: it is at `.claude/agents/_README.md`, NOT `.claude/agents/tachi/_README.md`)
- Architect plan review flagged: `Agent` must be added to threat-report.md tools frontmatter (T007)
