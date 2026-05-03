# Code Review: Feature 015 -- Threat Report Agent & Attack Trees

**Reviewer**: code-reviewer
**Date**: 2026-03-23
**Branch**: `015-threat-report-agent`
**Status**: APPROVED_WITH_CONCERNS
**Verdict**: 0 Critical, 3 Warning, 5 Suggestion

---

## Files Reviewed

| File | Type | Lines |
|------|------|-------|
| `agents/threat-report.md` | NEW | ~700 |
| `agents/orchestrator.md` | MODIFIED | +90 lines (Phase 5) |
| `schemas/report.yaml` | NEW | 124 |
| `templates/threat-report.md` | NEW | 229 |
| `examples/mermaid-agentic-app/threat-report.md` | NEW | ~737 |
| `examples/mermaid-agentic-app/attack-trees/*.md` | NEW | 12 files |
| `docs/architecture/01_system_design/README.md` | MODIFIED | +60 lines |
| `docs/product/02_PRD/INDEX.md` | MODIFIED | +1 line |
| `docs/product/_backlog/BACKLOG.md` | MODIFIED | +1 line |

---

## Findings

### WARNING-1: Color palette mismatch between template and agent/examples

**File**: `templates/threat-report.md` lines 168-171
**Issue**: The template defines a different color palette than the agent prompt and all example outputs. The template uses `#c0392b`, `#f39c12`, `#1abc9c`, `#2ecc71` (and different stroke colors) while the agent prompt (line 454-457) and all 12 standalone attack tree files use `#ff6b6b`, `#ffa500`, `#4ecdc4`, `#95e1d3` (with `stroke:#333`).

**Template values** (lines 168-171):
```
classDef goal fill:#ff6b6b,stroke:#c0392b,color:#fff
classDef andGate fill:#f39c12,stroke:#e67e22,color:#fff
classDef orGate fill:#1abc9c,stroke:#16a085,color:#fff
classDef leaf fill:#2ecc71,stroke:#27ae60,color:#fff
```

**Agent/example values** (consistent across agent and all outputs):
```
classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
classDef andGate fill:#ffa500,stroke:#333,stroke-width:2px,color:#fff
classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333
```

**Impact**: The template is the canonical structural reference. An LLM following the template would produce different colors than an LLM following the agent prompt. Three of four `fill` colors differ (`andGate`, `orGate`, `leaf`), all `stroke` colors differ, the template lacks `stroke-width`, and the leaf text color differs (`#fff` vs `#333`). This will cause visual inconsistency if anyone uses the template directly.

**Fix**: Align `templates/threat-report.md` lines 168-171 to match the agent prompt palette (`#ff6b6b`/`#ffa500`/`#4ecdc4`/`#95e1d3` with `stroke:#333,stroke-width:2px`). The agent prompt is the authority since it matches the validation checklist (line 522) and all generated outputs.

---

### WARNING-2: Attack tree file naming convention inconsistency between spec/PRD and agent/examples

**File**: `agents/threat-report.md` line 119, line 672; `specs/015-threat-report-agent/spec.md` line 58; `docs/product/02_PRD/015-threat-report-agent-attack-trees-2026-03-23.md` line 260
**Issue**: The spec (line 58) and PRD (line 260) use uppercase finding IDs in filenames (`AG-1-attack-tree.md`), while the agent prompt (line 672) explicitly specifies lowercase (`ag-1-attack-tree.md`), and all 12 example files use lowercase filenames. The agent prompt validation checklist (line 119) also cites the uppercase example (`AG-1-attack-tree.md`), contradicting its own line 672.

There is a self-contradiction within the agent file itself:
- Line 119: `e.g., AG-1-attack-tree.md` (uppercase)
- Line 672: `Examples: ag-1-attack-tree.md` (lowercase)

**Impact**: An LLM following the validation checklist (line 119) would name files differently from one following line 672. The actual generated examples use lowercase, consistent with kebab-case conventions.

**Fix**: Standardize on lowercase everywhere. Update line 119 of `agents/threat-report.md` to use `ag-1-attack-tree.md`. Update the spec (line 58) and PRD (line 260) examples to match. Lowercase is the correct choice per kebab-case file naming conventions.

---

### WARNING-3: `default` used as a Mermaid class name despite being listed as a reserved word

**File**: `agents/threat-report.md` lines 576, 625; all example attack tree files with sub-goal nodes (12 instances total)
**Issue**: The agent prompt explicitly warns against using `default` as a bare node ID (lines 126, 418, 490) listing it among reserved words: `end`, `default`, `graph`, `subgraph`, etc. However, all example attack trees in both the agent file and the example outputs use `class {nodes} default` to assign sub-goal styling. While `default` is used as a *class name* (not a node ID), the inconsistency between the stated prohibition and the demonstrated usage creates ambiguity for the generating LLM.

Example from `agents/threat-report.md` line 576:
```
class AG1_sub1,AG1_sub2 default
```

The agent's prose on line 472 explains this is intentional: "Sub-goal nodes do not receive a custom class -- they use the default Mermaid styling." However, the `class X default` syntax explicitly names the Mermaid built-in `default` class. While this works in practice (Mermaid treats it as an explicit assignment of the default theme class), it is technically fragile. A future Mermaid version could change behavior of `class X default`.

**Impact**: Low risk of actual breakage today, but the contradiction between "never use `default` as a reserved word" and using `default` as a class name assignment could confuse an LLM during generation.

**Fix**: Either (a) define an explicit `classDef subGoal` with the desired neutral styling and use `class {nodes} subGoal` throughout, or (b) add a clarifying note to the reserved words list that `default` is prohibited as a *node ID* but permitted in `class` assignments. Option (a) is cleaner.

---

### SUGGESTION-1: Architecture docs section structure description is inaccurate

**File**: `docs/architecture/01_system_design/README.md` line 650
**Issue**: The architecture documentation describes the agent prompt as having an "8-Section Structure: Core Mission, Input Contract, Report Generation Methodology, Attack Tree Construction Rules, Mermaid Conventions, Executive Summary Template, Correlation Group Handling, Quality Standards / Validation Checklist." The actual agent file has 10 top-level `##` sections: Core Mission, Input Contract, Quality Standards, Report Generation Methodology, Attack Tree Construction Rules, Mermaid Conventions, Mermaid Validation Checklist, Example Attack Trees, Dual Output Location, Remediation Roadmap Generation.

**Impact**: Documentation inaccuracy. Readers of the architecture docs will expect a different structure than what they find in the actual file.

**Fix**: Update the architecture section description to reflect the actual 10-section structure.

---

### SUGGESTION-2: Remediation roadmap ordering in the example deviates from the spec

**File**: `examples/mermaid-agentic-app/threat-report.md` lines 641-661
**Issue**: The spec and template state the roadmap should be "ordered by risk level (Critical first, then High, Medium, Low). Within the same risk level, items are grouped by component." In the example, Critical items (AG-1, AG-2, LLM-1) appear first correctly, but High items are not grouped by component -- they appear in the order AG-3, D-1, E-1, I-1, I-2, LLM-2, LLM-3, S-1, T-2. The LLM Agent Orchestrator findings (D-1, E-1, I-2, LLM-2) are interspersed with other components rather than grouped together.

**Impact**: Minor. The example would be a better teaching reference if it precisely followed the spec's within-severity grouping rule. LLMs learning from the example may reproduce alphabetical-by-finding-ID ordering instead of component grouping.

**Fix**: Reorder the High findings in the example to group by component: LLM Agent Orchestrator (D-1, E-1, I-2, LLM-2), Knowledge Base (I-1, LLM-3), MCP Tool Server (AG-3), User (S-1), then Medium findings similarly.

---

### SUGGESTION-3: T-1 listed in cross-cutting theme but not in the contributing theme

**File**: `examples/mermaid-agentic-app/threat-report.md` line 155
**Issue**: Finding T-1 appears in Theme 1 "Concentrated Risk in the LLM Agent Orchestrator" contributing findings list (line 155). However, Theme 2 "Input Validation and Sanitization as a Systemic Gap" (lines 161-171) identifies T-2 (not T-1) as a contributing finding. T-1 is about communication channel tampering (internal channel integrity), not input validation. This is correctly categorized. No actual issue -- noting this was verified during review.

**Impact**: None. This was verified as correct during review -- T-1 relates to orchestrator-to-tool-server communication integrity, which is appropriately categorized under Theme 1 (orchestrator risk concentration).

---

### SUGGESTION-4: Missing `threat_summary` in standalone attack tree header versus schema definition

**File**: `schemas/report.yaml` lines 110-114; standalone attack tree files
**Issue**: The schema defines `required_header_fields` for standalone files as: `finding_id`, `component`, `risk_level`, `threat_summary`. The actual standalone files use a table with a `Threat` column (not `threat_summary`). The agent prompt (lines 677-685) uses `Threat` as the label. This is a semantic alignment issue: the schema says `threat_summary` but the template and all outputs use `Threat`.

**Impact**: Low. The field content matches; only the label differs. However, any programmatic validation of standalone files against the schema would need to know `Threat` maps to `threat_summary`.

**Fix**: Either align the schema field name to `threat` to match the output label, or add a note in the schema that the display label is `Threat`.

---

### SUGGESTION-5: Architecture docs data flow diagram labels subsections that do not exist in the agent

**File**: `docs/architecture/01_system_design/README.md` (new section, line ~660)
**Issue**: The Mermaid data flow diagram in the architecture docs labels internal processing steps as "Parse threats.md Sections 1-7 + 4a", "Executive Summary (~500 words)", "Threat Analysis (Agent-by-Agent)", etc. These labels are accurate descriptions of what the agent does, but the diagram shows them inside a "Report Agent Processing" subgraph that implies they are discrete, sequential stages. The actual agent prompt processes these as sections of a single report generation pass, not as discrete stages with separate invocations.

**Impact**: Negligible. The diagram is directionally correct for documentation purposes.

**Fix**: No change required. This is an accurate simplification for architectural documentation.

---

## Cross-Reference Integrity Check

| Reference | Source | Target | Status |
|-----------|--------|--------|--------|
| `input_schema: schemas/output.yaml` | agent frontmatter | schemas/output.yaml | PASS (existing file) |
| `output_schema: schemas/report.yaml` | agent frontmatter | schemas/report.yaml | PASS (new file, exists) |
| `templates: report: templates/threat-report.md` | agent frontmatter | templates/threat-report.md | PASS (new file, exists) |
| `references: finding: schemas/finding.yaml` | agent frontmatter | schemas/finding.yaml | PASS (existing file) |
| `report: schemas/report.yaml` | orchestrator frontmatter | schemas/report.yaml | PASS |
| `threat_report: templates/threat-report.md` | orchestrator frontmatter | templates/threat-report.md | PASS |
| `report: agents/threat-report.md` | orchestrator frontmatter | agents/threat-report.md | PASS |
| Schema `required_sections` headings | schemas/report.yaml | templates/threat-report.md | PASS (all 7 match) |
| Agent section structure | agent prompt | schema sections | PASS (all 7 generated) |

---

## Orchestrator Integration Assessment

Phase 5 integration follows the established pattern of Phases 1-4:

1. **Phase heading style**: "Phase 5: Report -- 'Communicate findings to stakeholders'" matches the existing pattern ("Phase 1: Scope -- 'What are we working on?'", etc.). PASS.
2. **Section placement**: Phase 5 is placed after the SARIF output section and before Error Handling, consistent with the pipeline flow. PASS.
3. **Backward compatibility**: Opt-out configuration (`--skip-report` flag and `report: false`) preserves Phase 1-4 behavior. PASS.
4. **Context isolation**: Fresh-context invocation boundary is clearly specified, preventing accumulated pipeline state from entering Phase 5. PASS.
5. **Validation checklist**: Phase 5 validation items added to the existing Output Structural Validation Checklist section (lines 1196-1209) with proper conditional gating ("when Phase 5 is enabled"). PASS.

No breaking changes to existing Phase 1-4 structure detected.

---

## Mermaid Syntax Spot Check

Checked 5 attack trees in detail: AG-1, LLM-1, S-1, E-1, D-1.

| Check | AG-1 | LLM-1 | S-1 | E-1 | D-1 |
|-------|------|-------|-----|-----|-----|
| `flowchart TD` | PASS | PASS | PASS | PASS | PASS |
| Node ID format | PASS | PASS | PASS | PASS | PASS |
| Labels quoted | PASS | PASS | PASS | PASS | PASS |
| No reserved word IDs | PASS | PASS | PASS | PASS | PASS |
| AND/OR gates present | PASS | PASS | PASS | PASS | PASS |
| classDef styling | PASS | PASS | PASS | PASS | PASS |
| No orphan nodes | PASS | PASS | PASS | PASS | PASS |
| No loops | PASS | PASS | PASS | PASS | PASS |
| Depth (Critical >= 3) | PASS (3) | PASS (3) | N/A | N/A | N/A |
| Depth (High >= 2) | N/A | N/A | PASS (2) | PASS (3) | PASS (2) |
| Inline matches standalone | PASS | PASS | PASS | PASS | PASS |

All 5 trees render valid Mermaid syntax. No structural issues detected.

---

## Naming Convention Check

| File | Convention | Status |
|------|-----------|--------|
| `agents/threat-report.md` | kebab-case | PASS |
| `schemas/report.yaml` | kebab-case | PASS |
| `templates/threat-report.md` | kebab-case | PASS |
| `examples/mermaid-agentic-app/threat-report.md` | kebab-case | PASS |
| `examples/mermaid-agentic-app/attack-trees/*.md` | kebab-case | PASS |
| `attack-trees/` directory | kebab-case | PASS |

All new files follow kebab-case naming. No PascalCase issues.

---

## Duplication Assessment

The AG-1 and LLM-1 example attack trees appear in three locations:
1. `agents/threat-report.md` (Example Attack Trees section)
2. `examples/mermaid-agentic-app/threat-report.md` (inline in Section 5)
3. `examples/mermaid-agentic-app/attack-trees/ag-1-attack-tree.md` and `llm-1-attack-tree.md` (standalone)

Locations 2 and 3 are required by the spec (inline + standalone). Location 1 is intentional as reference examples within the agent prompt, serving a different purpose (teaching the LLM the correct pattern). This is not problematic duplication -- it is spec-compliant dual-output plus agent-level examples.

No other content duplication identified.

---

## Summary

| Severity | Count | IDs |
|----------|-------|-----|
| CRITICAL | 0 | -- |
| WARNING | 3 | W-1 (color palette mismatch), W-2 (filename case inconsistency), W-3 (`default` class usage) |
| SUGGESTION | 5 | S-1 (architecture section count), S-2 (roadmap ordering), S-3 (verified OK), S-4 (schema field label), S-5 (diagram simplification) |

**Verdict**: APPROVED_WITH_CONCERNS

The implementation is well-structured and thorough. The agent prompt is clear, actionable, and comprehensive. Cross-references between agent, schema, template, and orchestrator are intact. Mermaid syntax is consistently correct across all checked trees. The Phase 5 orchestrator integration follows established patterns without breaking backward compatibility.

The three WARNING-level findings involve internal consistency issues that should be resolved before merging to prevent confusion during report generation:
- W-1 (template color palette) is the most impactful since it creates a direct contradiction between the template and the agent prompt.
- W-2 (filename casing) creates a self-contradiction within the agent file.
- W-3 (`default` class) is a minor but real ambiguity.

None of these block merge, but all three represent places where an LLM generating output could receive contradictory instructions and produce inconsistent results.
