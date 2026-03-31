---
name: tachi-orchestration
description: "Domain knowledge for the tachi orchestrator agent: SARIF 2.1.0 generation specification, STRIDE-per-Element and AI keyword dispatch rules, cross-agent correlation matrices, output schema tables for threats.md, structural validation checklist, and error handling templates. Loaded on-demand by the orchestrator during specific pipeline phases."
---

# Tachi Orchestration Skill

Domain knowledge extracted from the tachi orchestrator agent to support the OWASP four-step threat modeling pipeline. This skill provides reference material that the orchestrator loads on-demand at specific workflow phases, keeping the agent definition focused on orchestration logic.

## Domain Coverage

This skill contains three categories of domain knowledge:

1. **SARIF Specification** -- Complete SARIF 2.1.0 generation specification including category-to-rule mappings, severity mapping tables, tool metadata templates, finding-to-result transformation rules, correlated finding mapping, dual-location strategy, fingerprint computation, taxonomy declarations, schema compliance structure, and JSON structural self-check.

2. **Dispatch Rules** -- STRIDE-per-Element normalization table mapping DFD element types to applicable threat categories, AI keyword dispatch rules with keyword-to-category mappings and matching semantics, dispatch table format specification, and the five correlation rules with detection algorithm and group assembly instructions.

3. **Output Schemas** -- Output format specification for threats.md (frontmatter fields, all 7 required sections plus Section 4a), structural validation checklist covering section completeness and cross-section consistency, error handling templates (UNSUPPORTED_FORMAT, NO_COMPONENTS, INVALID_FORMAT_VALUE), and edge-case handlers for ambiguous classification, non-conforming findings, and the three-state coverage matrix cell model.

## Loading Table

| Reference File | Load Condition | Workflow Phase |
|----------------|----------------|----------------|
| `references/dispatch-rules.md` | Entering Phase 2 (Determine Threats) | After Phase 1 component inventory is produced, before agent dispatch |
| `references/output-schemas.md` | Entering Phase 1 (Scope) for output format awareness; Phase 3 (Determine Countermeasures) for table assembly; Phase 4 (Assess) for validation | Before assembling Section 1, and before running the structural validation checklist |
| `references/sarif-specification.md` | Entering SARIF generation step in Phase 4 | After threats.md structural validation passes, before writing threats.sarif |

## Loading Mechanism

The orchestrator agent uses the Read tool to load reference files on-demand per ADR-002. Each reference file is self-contained and can be loaded independently at the workflow phase indicated above. Content is evictable from context after the relevant phase completes.

```markdown
# Example loading instruction in orchestrator agent body:
Read `.claude/skills/tachi-orchestration/references/sarif-specification.md`
when entering the SARIF generation step in Phase 4.
```
