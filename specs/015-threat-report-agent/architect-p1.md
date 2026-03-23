# Architect P1 Review: Feature 015 -- Threat Report Agent & Attack Trees

**Reviewer**: Architect
**Date**: 2026-03-23
**Checkpoint**: P1 (Implementation Review)
**Branch**: `015-threat-report-agent`

## Review Scope

Files reviewed:

| File | Type | Lines |
|------|------|-------|
| `agents/threat-report.md` | NEW | ~630 |
| `agents/orchestrator.md` | MODIFIED | Phase 5 sections (~70 lines added) |
| `schemas/report.yaml` | NEW | 124 |
| `templates/threat-report.md` | NEW | 229 |
| `examples/mermaid-agentic-app/threat-report.md` | NEW | 737 |
| `examples/mermaid-agentic-app/attack-trees/*.md` | NEW | 12 files |

Reference documents: `specs/015-threat-report-agent/spec.md`, `specs/015-threat-report-agent/plan.md`

---

## Summary

The P1 implementation is architecturally sound and ready for merge with minor corrections. The report agent prompt, schema, template, orchestrator integration, and example outputs form a coherent, well-cross-referenced system that follows established tachi patterns. The Mermaid conventions are comprehensive and the example output demonstrates the methodology faithfully.

Two medium findings and three low findings were identified. Neither medium finding blocks the PR, but both should be addressed before merge to prevent downstream inconsistency when the agent is invoked at scale.

---

## Findings

### MEDIUM-1: Color palette inconsistency between template and agent/examples

**Files**: `templates/threat-report.md` (lines 168-171) vs `agents/threat-report.md` (lines 454-457) and all example files

The template defines one color palette:

```
classDef goal fill:#ff6b6b,stroke:#c0392b,color:#fff
classDef andGate fill:#f39c12,stroke:#e67e22,color:#fff
classDef orGate fill:#1abc9c,stroke:#16a085,color:#fff
classDef leaf fill:#2ecc71,stroke:#27ae60,color:#fff
```

The agent prompt and all examples use a different palette:

```
classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
classDef andGate fill:#ffa500,stroke:#333,stroke-width:2px,color:#fff
classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333
```

Differences:
- `goal`: stroke `#c0392b` (template) vs `#333` (agent/examples)
- `andGate`: fill `#f39c12` (template) vs `#ffa500` (agent/examples); stroke differs
- `orGate`: fill `#1abc9c` (template) vs `#4ecdc4` (agent/examples); stroke differs
- `leaf`: fill `#2ecc71` (template) vs `#95e1d3` (agent/examples); stroke and text color differ
- Template omits `stroke-width:2px` that agent/examples include

The agent prompt is the authoritative source (it contains the Mermaid Conventions section and the validation checklist that specifies exact hex values). The template should be updated to match.

**Impact**: An LLM following the template literally would produce trees with different colors than the agent prompt instructs. Since the agent prompt takes precedence in practice, the risk is that the template becomes misleading documentation.

**Recommendation**: Update `templates/threat-report.md` lines 168-171 to match the agent's canonical palette at lines 454-457. This is a 4-line edit.

---

### MEDIUM-2: `default` used as a Mermaid class name despite being listed as a reserved word

**Files**: `agents/threat-report.md` (lines 576, 625), `examples/mermaid-agentic-app/threat-report.md` (6 occurrences), all standalone attack tree files with sub-goal nodes (6 files)

The agent prompt explicitly lists `default` as a reserved word to avoid:

> Line 418: "Never use bare reserved words as node IDs: `end`, `default`, `graph`, `subgraph`, `click`, `style`, `linkStyle`"
>
> Line 490: "No bare reserved words used as node IDs: `end`, `default`, `graph`, `subgraph`, `click`, `style`, `linkStyle`, `classDef`, `class`"

However, the agent prompt's own example trees, the template, and all sample outputs assign sub-goal nodes to `class ... default`:

```
class AG1_sub1,AG1_sub2 default
```

While `default` in this context is a class *name* argument to the `class` keyword (not a node ID), it is still a Mermaid keyword. In Mermaid, `default` is a special classDef name that applies styling to all nodes without an explicit class assignment. Using `class X default` assigns nodes to Mermaid's built-in default styling, which may or may not be the intended behavior across different Mermaid rendering engines (GitHub, Mermaid Live Editor, VS Code).

The agent's own text at line 472 states: "Sub-goal nodes do not receive a custom class -- they use the default Mermaid styling." This is an intentional design choice, but it creates a contradiction with the validation checklist at line 517: "`class` assignments applied to every node in the tree" -- because explicitly assigning `default` is different from "not assigning a class."

**Impact**: Potential rendering inconsistency across Mermaid implementations. The validation checklist contradiction could confuse an LLM generating trees.

**Recommendation**: Either (a) define a `subGoal` classDef with a distinct neutral color (e.g., `fill:#ddd,stroke:#333,stroke-width:2px,color:#333`) and assign sub-goal nodes to it, or (b) remove the `class ... default` line entirely so sub-goal nodes are truly unclassed, and update the validation checklist to say "class assignments applied to all nodes except sub-goal nodes."

---

### LOW-1: Remediation Roadmap ordering does not strictly follow the stated rule

**File**: `examples/mermaid-agentic-app/threat-report.md` (lines 641-661)

The template and agent both specify: "Prioritized table of all findings ordered by risk level (Critical first, then High, Medium, Low). Within the same risk level, items are grouped by component."

The example Remediation Roadmap lists findings in this order:
- Critical: AG-1, AG-2, LLM-1 (correct)
- High: AG-3, D-1, E-1, I-1, I-2, LLM-2, LLM-3, S-1, T-2

Within the High tier, items are ordered alphabetically by finding ID rather than grouped by component. For example, AG-3 (MCP Tool Server) and D-1 (LLM Agent Orchestrator) are adjacent, then E-1 (LLM Agent Orchestrator) follows, rather than having all LLM Agent Orchestrator items grouped together.

Then Medium findings are listed: AG-4, D-2, LLM-4, R-1, R-2, S-2, T-1 -- again alphabetically by finding ID rather than grouped by component.

**Impact**: Minor example fidelity issue. The example demonstrates finding-ID alphabetical ordering rather than the component-grouped ordering specified in the methodology. An LLM learning from this example would reproduce the wrong ordering convention.

**Recommendation**: Re-order the High and Medium sections to group by component. For High: group all LLM Agent Orchestrator findings together (D-1, E-1, I-2, LLM-2), then Knowledge Base (I-1, LLM-3, T-2), then MCP Tool Server (AG-3), then User (S-1).

---

### LOW-2: Report frontmatter in example uses bare `---` fencing instead of proper YAML frontmatter

**File**: `examples/mermaid-agentic-app/threat-report.md` (lines 1-18)

The example report wraps its frontmatter in a fenced code block:

```
---

\`\`\`yaml
---
schema_version: "1.0"
...
---
\`\`\`

---
```

The template (`templates/threat-report.md` lines 17-32) specifies the same pattern. This is fine as a rendering choice (displaying the frontmatter as a visible YAML block), but it means the frontmatter is not machine-parseable as actual YAML frontmatter. A tool validating against `schemas/report.yaml` would need to extract the YAML from inside the code fence rather than using standard frontmatter parsing.

**Impact**: Low. The schema specifies frontmatter is required, but since this is prompt-generated content (not application code), the rendering format is a stylistic choice. However, if any downstream automation is added for report validation, the non-standard frontmatter format would require custom parsing.

**Recommendation**: Document in `schemas/report.yaml` that the frontmatter is rendered as a fenced YAML code block in the output (not as standard YAML frontmatter delimited by bare `---`), so any future validation tooling knows to expect this format.

---

### LOW-3: Appendix Finding Reference includes findings in Cross-Cutting Themes that are not explicitly cited in theme text

**File**: `examples/mermaid-agentic-app/threat-report.md`

The appendix maps several findings to Section 4 (Cross-Cutting Themes) -- for example, T-1 is mapped to Cross-Cutting Themes (line 675). Checking Theme 1 text (lines 149-159), T-1 is indeed listed in the contributing findings for Theme 1 ("Contributing findings: T-1, R-2, I-2, D-1, E-1, AG-1, AG-4, LLM-1, LLM-2, LLM-4").

After cross-checking all 19 findings against the appendix: the mapping is consistent. Every finding that appears in a theme's contributing findings list has a corresponding Section 4 row in the appendix. No discrepancies found.

This is actually a **positive validation** -- the zero-finding-loss rule is upheld. Downgrading to informational.

**Impact**: None. This finding is closed as validated.

---

## Criteria Assessment

### 1. Architecture Consistency

**PASS**. The report agent follows tachi's established patterns:
- YAML frontmatter with `agent_name`, `category`, `status`, `version`, `description`, `input_schema`, `output_schema`, `output_files`, `references` -- consistent with STRIDE agents while adding fields appropriate to the report agent's multi-output nature.
- Agent prompt structure (Core Mission, Input Contract, methodology sections, validation checklists) follows the pattern established by `agents/stride/spoofing.md` and peers, adapted for the report generation domain.
- Schema structure (`schemas/report.yaml`) follows the same YAML documentation pattern as `schemas/output.yaml` and `schemas/finding.yaml`, with consistent field definitions and producer/consumer annotations.
- Template (`templates/threat-report.md`) mirrors the `templates/threats.md` pattern with HTML comment header documenting schema version, producer, consumer, and contract references.

### 2. Cross-Reference Integrity

**PASS with note**. Cross-references are correct throughout:
- Agent frontmatter references `schemas/output.yaml` (input) and `schemas/report.yaml` (output) correctly.
- Template header references `schemas/report.yaml` and the spec correctly.
- Schema correctly names the output file as `threat-report.md` and references the agent as producer.
- Orchestrator frontmatter adds `schemas/report.yaml` to the references block and `agents/threat-report.md` to the agents block.
- The color palette inconsistency (MEDIUM-1) is the one cross-reference integrity issue.

### 3. Orchestrator Integration

**PASS**. Phase 5 integration is well-executed:
- Phase 5 is added as a new section following the structural pattern of Phases 1-4.
- Fresh-context isolation is explicitly specified with clear positive and negative constraints (what to pass, what NOT to pass).
- The `<report-input>` content boundary mirrors the existing `<architecture-input>` boundary from Phase 1 -- consistent pattern.
- Opt-out configuration provides two mechanisms (`--skip-report` flag, `report: false` config).
- The validation checklist is extended with a dedicated "Phase 5 Outputs" section that only runs when Phase 5 is enabled.
- The orchestrator description, references, and output format specification are all updated to reflect Phase 5.
- Backward compatibility is preserved: when Phase 5 is skipped, the pipeline completes identically to pre-feature behavior.

### 4. Mermaid Conventions

**PASS with note**. The Mermaid conventions section in the agent prompt is comprehensive:
- Node ID format, shapes, edge syntax, and color styling are well-specified.
- The validation checklist (4 sections, ~30 checks) covers syntax safety, structural integrity, naming conventions, styling, and readability.
- Reserved word list is thorough (including `classDef` and `class` themselves).
- The `default` class name issue (MEDIUM-2) is the one concern.
- Two worked examples (Critical 3-level, High 2-level) with annotated explanations provide strong guidance for LLM generation.

### 5. Data Flow

**PASS**. The Input Contract section in the agent prompt correctly maps all 7+1 sections of `threats.md`:
- Every section of `threats.md` (per `schemas/output.yaml`) is mapped to the report sections that consume it.
- All Finding IR fields from `schemas/finding.yaml` are enumerated with their usage in the report.
- Correlation group fields from Section 4a are separately documented.
- The agent explicitly specifies that `mitigation` text is preserved verbatim (not reinterpreted).
- The Coverage Matrix (Section 5) and Risk Summary (Section 6) from `threats.md` are correctly mapped to Executive Summary context.

### 6. Example Quality

**PASS with notes**. The sample output is high quality:
- All 7 required sections present with substantive content.
- 19 findings from the sample `threats.md` are all accounted for.
- 12 attack trees generated (3 Critical + 9 High = 12) -- matches the frontmatter `attack_tree_count: 12`.
- 12 standalone attack tree files in `attack-trees/` match the 12 inline trees.
- Critical findings (AG-1, AG-2, LLM-1) have 3-level trees; High findings have 2-level trees (minimum depth met).
- Cross-cutting themes identify 4 themes with cited finding IDs, using all 4 detection criteria.
- Appendix has 19 unique finding IDs with multi-row traceability. Completeness self-check included.
- Minor ordering issue in Remediation Roadmap (LOW-1).

---

## FR Coverage Verification

| FR | Addressed By | Status |
|----|-------------|--------|
| FR-001 | `agents/threat-report.md` exists with complete methodology | PASS |
| FR-002 | Template defines 7 sections; example contains all 7 | PASS |
| FR-003 | Executive Summary generation methodology with 5 elements, 500-word cap, language rules | PASS |
| FR-004 | Threat Analysis generation with per-finding narrative structure and 8 subsections | PASS |
| FR-005 | Cross-Cutting Theme Detection with 4 criteria (a-d), minimum thresholds | PASS |
| FR-006 | Attack Tree Construction Rules with Schneier methodology, depth requirements | PASS |
| FR-007 | Mermaid Conventions section with node ID format, shapes, styling | PASS (see MEDIUM-2) |
| FR-008 | Dual output specified: inline in report + standalone files in `attack-trees/` | PASS |
| FR-009 | Remediation Roadmap methodology with 5 required fields, priority tiers | PASS |
| FR-010 | Correlation Group Handling section with narrative/tree/roadmap treatment | PASS |
| FR-011 | Finding Reference Appendix with zero-loss rule and completeness self-check | PASS |
| FR-012 | Orchestrator Phase 5 with fresh-context isolation, opt-out, validation | PASS |
| FR-013 | Mermaid Validation Checklist with 30+ checks across 4 categories | PASS |
| FR-014 | `schemas/report.yaml` defines sections, naming, completeness rule | PASS |

---

## SC Coverage Verification

| SC | Verification | Status |
|----|-------------|--------|
| SC-001 | Example `threat-report.md` has all 7 sections with non-empty content | PASS |
| SC-002 | Executive summary methodology specifies non-technical audience; example demonstrates | PASS |
| SC-003 | 12/12 Critical+High findings have inline + standalone trees | PASS |
| SC-004 | Mermaid validation checklist ensures rendering correctness; manual spot-check of examples passes | PASS |
| SC-005 | Appendix lists 19/19 finding IDs; self-check confirms zero loss | PASS |
| SC-006 | Roadmap lists all 19 findings with effort estimates | PASS (see LOW-1 on ordering) |
| SC-007 | 4 cross-cutting themes identified using all 4 detection criteria | PASS |
| SC-008 | Orchestrator Phase 5 integration specified with output placement | PASS |
| SC-009 | Opt-out configuration preserves Phase 1-4 behavior | PASS |

---

## Verdict

**STATUS: APPROVED_WITH_CONCERNS**

| Severity | Count | Finding IDs |
|----------|-------|-------------|
| High | 0 | -- |
| Medium | 2 | MEDIUM-1 (color palette), MEDIUM-2 (`default` class name) |
| Low | 2 | LOW-1 (roadmap ordering), LOW-2 (frontmatter format) |
| Informational | 1 | LOW-3 (validated, closed) |

The two medium findings are correctable with small edits (4-line template update for MEDIUM-1; class name change or checklist clarification for MEDIUM-2). Neither requires architectural rework or plan restructuring. The implementation is architecturally sound, follows established tachi patterns, and satisfies all 14 FRs and all 9 SCs.

**Recommendation**: Address MEDIUM-1 and MEDIUM-2 before merge. LOW-1 and LOW-2 can be addressed in the same PR or deferred to a follow-up.
