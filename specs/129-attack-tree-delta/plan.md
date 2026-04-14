---
triad:
  pm_signoff:
    agent: product-manager
    date: 2026-04-13
    status: APPROVED
    notes: "All 10 spec FRs covered. All 3 user stories served. Zero scope creep. 2 LOW observations. Details: .aod/results/pm-plan-129.md"
  architect_signoff:
    agent: architect
    date: 2026-04-13
    status: APPROVED_WITH_CONCERNS
    notes: "7 findings (2 MEDIUM, 5 LOW): tokenization rules, manifest schema evolution, reference externalization, roster path, Agent tool frontmatter. Details: .aod/results/architect-plan-129.md"
  techlead_signoff: null
---

# Implementation Plan: Attack Tree Delta Sub-Agent

**Branch**: `129-attack-tree-delta` | **Date**: 2026-04-13 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/129-attack-tree-delta/spec.md`

## Summary

Extract attack tree generation and delta reconciliation (Rules 1-3) from the overloaded threat-report agent (337 lines) into a dedicated attack-tree-delta sub-agent. The sub-agent receives atomic inputs (findings list, delta counts, baseline path), executes deterministic rules with a concrete structural similarity algorithm, writes standalone files and a JSON manifest, and returns a structured summary. The threat-report agent spawns the sub-agent for Section 5 and assembles inline content from the manifest.

## Technical Context

**Language/Version**: Markdown (Claude Code agent definitions) — no application code
**Primary Dependencies**: Existing tachi agent framework (Agent tool for spawning, subagent return policy)
**Storage**: Markdown files (.md) + JSON manifest (.manifest.json) in `attack-trees/` directory
**Testing**: Existing `test_backward_compatibility.py` pytest suite (5 baselines, SOURCE_DATE_EPOCH=1700000000 per ADR-021)
**Target Platform**: Claude Code agent runtime (any OS)
**Project Type**: Knowledge system (agent definitions, not application code)
**Performance Goals**: N/A — sub-agent overhead negligible (single spawn per report)
**Constraints**: Sub-agent must fit Leaf tier (100-150 lines, hard cap 200). Threat-report must fit Report tier (200-250, hard cap 300 post-extraction). Backward compatible with no-baseline runs.
**Scale/Scope**: 7 files (1 new, 6 modifications)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Gate | Status |
|-----------|------|--------|
| III. Backward Compatibility | No-baseline reports produce identical output | PASS — SC-004 enforces byte-identical baselines |
| VI. Testing Excellence | Test coverage for core features | PASS — leverages existing backward-compat suite; no new Python code |
| VII. Definition of Done | Three-step validation | PASS — SC-001 through SC-006 provide measurable criteria |
| IX. Git Workflow | Feature branch, conventional commits | PASS — branch `129-attack-tree-delta` |
| X. Product-Spec Alignment | PRD → spec traceability | PASS — spec traces all 10 FRs to PRD FR-1 through FR-5 |

No violations. No complexity justifications needed.

## Project Structure

### Documentation (this feature)

```
specs/129-attack-tree-delta/
├── plan.md              # This file
├── research.md          # Research phase output (completed)
├── spec.md              # Feature specification (PM approved)
└── checklists/
    └── requirements.md  # Quality checklist (all green)
```

### Source Files (repository root)

Since this is a knowledge-system project (agent definitions, not application code), the "source" is markdown files:

```
.claude/agents/tachi/
├── attack-tree-delta.md       # NEW — sub-agent definition (Leaf tier)
├── threat-report.md           # MODIFY — extract Section 5, add spawn logic
└── _README.md                 # MODIFY — add new agent to roster

.claude/skills/tachi-threat-reporting/references/
├── attack-tree-construction.md  # MODIFY — add reconciliation section + worked example
└── narrative-templates.md       # MODIFY — add delta annotation guidance for Section 5

schemas/
└── report.yaml                  # MODIFY — align attack_tree_count description

templates/tachi/output-schemas/
└── threat-report.md             # MODIFY — align attack_tree_count definition
```

**No new directories created.** All files are in existing locations.

## Components

### Component 1: Attack Tree Delta Sub-Agent (NEW)

**File**: `.claude/agents/tachi/attack-tree-delta.md`
**Tier**: Leaf (target 100-150 lines, hard cap 200)
**Pattern**: Detection variant (single-pass, single `**MANDATORY**: Read` at workflow start)

**Responsibilities**:
- Receive atomic inputs from threat-report parent: Critical/High findings with delta_status, delta_counts, baseline directory path, output directory path
- Determine which rule applies (Rule 1, 2, or no-baseline)
- Execute the selected rule deterministically
- Write standalone files to `attack-trees/{finding-id}-attack-tree.md`
- Write manifest to `attack-trees/.manifest.json`
- Return structured summary (max 15 lines) per subagent return policy

**Internal Structure**:
1. **Inputs section**: Document the four atomic inputs and their types
2. **Rule dispatch**: Deterministic conditional — check delta_counts to select Rule 1 vs Rule 2 vs no-baseline
3. **Rule 1 logic**: Read and copy baseline trees verbatim. No generation.
4. **Rule 2 logic**: Generate fresh trees for ALL Critical/High findings, then apply Rule 3 reconciliation per UNCHANGED finding.
5. **Rule 3 logic**: Structural similarity algorithm (FR-003) — parse Mermaid, count nodes/edges/gates, extract leaf labels, compute token-level Jaccard, apply thresholds. Named constants: `LEAF_MATCH_THRESHOLD = 0.70`, `TREE_SIMILARITY_THRESHOLD = 0.80`, `NODE_COUNT_VARIANCE = 0.20`.
6. **Manifest writing**: JSON with rule_applied, attack_tree_count, per-tree entries, summary counts.
7. **Return format**: STATUS, RULE_APPLIED, TREES count, MANIFEST path.

**Skill references loaded**:
- `**MANDATORY**: Read .claude/skills/tachi-threat-reporting/references/attack-tree-construction.md` (at workflow start — provides tree structure rules, Mermaid syntax, node ID format, validation checklist)

**Edge case handling**:
- Missing baseline directory → fall back to fresh generation for all (Rule 2 without reconciliation)
- Missing individual baseline tree → generate fresh for that finding only
- Zero Critical/High findings → empty manifest, immediate return
- Invalid Mermaid syntax in baseline → treat as materially different, use fresh
- All findings RESOLVED → empty manifest

### Component 2: Threat-Report Agent Refactor (MODIFY)

**File**: `.claude/agents/tachi/threat-report.md`
**Current**: 337 lines (exceeds Report tier 300-line hard cap)
**Target**: < 300 lines (within Report tier cap)

**Changes**:
1. **Remove**: Rules 1-3 delta logic (lines ~218-229)
2. **Remove**: Baseline file I/O for attack trees (read/copy logic)
3. **Remove**: Structural similarity comparison logic
4. **Add**: Sub-agent spawn instruction — spawn `attack-tree-delta` agent with four atomic inputs:
   - Critical/High findings list with delta_status
   - delta_counts from threats.md frontmatter
   - Baseline directory path (derived from baseline.source)
   - Output directory path
5. **Add**: Manifest consumption — read `.manifest.json`, assemble inline Section 5 content from standalone files using manifest ordering (Critical alphabetical, then High alphabetical)
6. **Preserve**: All narrative sections (1-4, 6-8) unchanged
7. **Preserve**: Dual Output Location section (lines 302-330) for inline assembly instructions — but simplify to reference manifest ordering instead of re-deriving ordering
8. **Clarify**: Correlation group cross-referencing (Section 4a) remains threat-report's responsibility — sub-agent manifest does not carry correlation data

**Net reduction**: ~100+ lines removed (delta rules + baseline I/O), ~20 lines added (spawn + manifest consumption) = net ~80+ line reduction.

### Component 3: Schema Alignment (MODIFY)

**Files**: `schemas/report.yaml`, `templates/tachi/output-schemas/threat-report.md`

**Change**: Align `attack_tree_count` to single canonical definition:
> "Total attack trees produced (fresh + carried-forward), equal to the number of files in the `attack-trees/` directory."

**Deliberate reversal**: Feature 104 defined `attack_tree_count` as "NEW or UPDATED only, UNCHANGED excluded." This PRD reverses that decision because:
- Consumers want to know how many attack trees are in the report, not how many were freshly generated
- "Fresh only" count produced inconsistent numbers (baseline 21, new run 16, files written 22)
- "Total produced" always equals the file count — simple, verifiable, unambiguous

**Documentation**: Add a revision note to `schemas/report.yaml` description referencing the Feature 104 → Feature 129 reversal.

### Component 4: Reference File Updates (MODIFY)

**File 1**: `.claude/skills/tachi-threat-reporting/references/attack-tree-construction.md`
- **Add section**: `## Baseline Reconciliation` (after existing Validation section)
- **Content**: Rule 3 structural similarity algorithm description, named constants, step-by-step instructions
- **Worked example**: Two concrete trees compared — one similar (leaf overlap 0.92, same gates, node count delta 5% → carry forward baseline), one different (leaf overlap 0.65, OR→AND gate change → use fresh)

**File 2**: `.claude/skills/tachi-threat-reporting/references/narrative-templates.md`
- **Add section**: `## Section 5 Delta Annotations`
- **Content**: How to annotate regenerated trees in Section 5 inline content (e.g., _"Context changed since baseline — attack tree regenerated."_)

### Component 5: Agent Roster Update (MODIFY)

**File**: `.claude/agents/tachi/_README.md`
- Add `attack-tree-delta` to the agent roster table
- Classification: Leaf tier, spawned by threat-report
- Note: First pipeline agent sub-spawning pattern in tachi

## Data Flow

```
threat-report agent
  │
  ├─ Sections 1-4, 6-8: narrative generation (unchanged)
  │
  └─ Section 5: spawn attack-tree-delta sub-agent
       │
       ├─ Inputs: findings[], delta_counts, baseline_dir, output_dir
       │
       ├─ Rule dispatch (deterministic)
       │    ├─ Rule 1: all UNCHANGED → copy baseline verbatim
       │    └─ Rule 2: any delta → fresh ALL, then Rule 3 reconcile UNCHANGED
       │         └─ Rule 3: structural similarity → carry_forward | regenerated
       │
       ├─ Outputs:
       │    ├─ attack-trees/{id}-attack-tree.md (standalone files)
       │    └─ attack-trees/.manifest.json (structured metadata)
       │
       └─ Return: STATUS + RULE + COUNT + MANIFEST_PATH (≤15 lines)
              │
              └─ threat-report reads manifest → assembles inline Section 5
```

## Tech Stack

| Layer | Technology | Purpose |
|-------|------------|---------|
| Agent runtime | Claude Code Agent tool | Sub-agent spawning and return |
| Agent definitions | Markdown (.md) | Instruction files consumed by LLM |
| Manifest format | JSON (.manifest.json) | Structured metadata for Section 5 assembly |
| Tree syntax | Mermaid flowchart TD | Attack tree visualization format |
| Testing | pytest + SOURCE_DATE_EPOCH | Backward compatibility validation |

## Design Decisions

### DD-1: Sub-Agent vs. Skill Extraction

**Decision**: Sub-agent (spawned by threat-report), not skill reference extraction.

**Rationale**: Skill references are for domain knowledge (patterns, examples, schemas). The attack tree delta logic requires active decision-making (rule dispatch, baseline file I/O, comparison, manifest writing). This is control flow, not domain knowledge — it belongs in an agent, not a reference file.

### DD-2: Manifest on Disk vs. Inline Return

**Decision**: Manifest written to `attack-trees/.manifest.json` on disk. Sub-agent returns only a summary.

**Rationale**: Per ADR-010 (Minimal-Return Architecture), sub-agents offload detailed results to disk. The manifest contains per-tree metadata that would exceed the 15-line return cap. The threat-report agent reads the manifest file to assemble Section 5.

### DD-3: Standalone Files Only (Sub-Agent Scope)

**Decision**: Sub-agent writes standalone files in `attack-trees/` only. Does not produce inline Section 5 content.

**Rationale**: Inline Section 5 content requires correlation group cross-references (from threats.md Section 4a) that the sub-agent doesn't receive. The threat-report agent already has this context. Clean separation: sub-agent produces trees, threat-report assembles the narrative.

### DD-4: Token-Level Jaccard for Leaf Label Matching

**Decision**: Per-label matching uses token-level Jaccard similarity (word overlap after lowercasing, threshold >= 0.70) rather than exact string matching.

**Rationale**: LLM-generated Mermaid labels will have minor wording variations across runs ("Identify high-stakes tool operations" vs. "Identify high-stakes tool operation exposed by orchestrator"). Exact matching would classify these as different, defeating reconciliation. Token-level Jaccard is robust to minor variation while preserving semantic sensitivity. Named constant makes the threshold trivially adjustable.

### DD-5: Gate-Type Comparison Step

**Decision**: Ordered gate-type list comparison as a hard structural guard, overriding leaf similarity.

**Rationale**: An OR→AND gate change fundamentally alters the threat model (disjunctive vs. conjunctive attack paths) even when leaf labels are identical. The algorithm must detect this. Gate types are extracted from Mermaid node IDs (`_or`, `_and` prefixes) — reliable with the constrained ID format from `attack-tree-construction.md`.

### DD-6: attack_tree_count Reversal

**Decision**: Redefine `attack_tree_count` as "total trees produced (fresh + carried-forward)" rather than "fresh only."

**Rationale**: Reverses Feature 104 decision. The "fresh only" definition produced inconsistent numbers (baseline 21, new run 16, files 22). "Total produced" always equals the file count — simple, verifiable, unambiguous. Consumers want to know the total, not the generation effort. Documented as deliberate reversal in schema description.

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| Similarity thresholds too aggressive/lenient | Named constants (0.70 per-label, 0.80 tree-level, 0.20 node-count) trivially adjustable. Validated against 2 example sets. |
| LLM miscounts nodes/edges | Constrained Mermaid ID format (`{FindingID}_{type}{N}`) makes counting reliable. 80% threshold provides generous error margin. |
| Sub-agent exceeds Leaf tier cap | Algorithm details externalized to `attack-tree-construction.md` reference. Agent retains dispatch logic only. |
| Backward compatibility regression | SC-004 enforces byte-identical baselines via existing test suite. No new test infrastructure needed. |
