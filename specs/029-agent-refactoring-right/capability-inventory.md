# Capability Inventory: Agent Refactoring Right-Size

## Post-Refactoring Verification Results

**Date**: 2026-03-25 | **Branch**: 029-agent-refactoring-right

### Line Count Summary

| Agent | Before | After | Target | Deviation | Status |
|-------|--------|-------|--------|-----------|--------|
| Orchestrator | 2,085 | 1,273 | 1,100-1,200 | +73 above ceiling | Accepted — remaining content is irreducible specification |
| Report | 801 | 472 | 300-400 | +72 above ceiling | Accepted — remaining content is specification (tables, checklists, rules) |
| Infographic | 592 | 414 | 300-400 | +14 above ceiling | Accepted — remaining content is specification |

### Extraction Summary

| Reference Document | Lines | Source Agent | Load Condition |
|--------------------|-------|-------------|----------------|
| sarif-generation.md | 499 | orchestrator.md | Phase 4 completion |
| validation-checklist.md | 90 | orchestrator.md | Pipeline end |
| error-templates.md | 131 | orchestrator.md | Error condition |
| report-templates.md | 298 | threat-report.md | Attack tree generation |
| infographic-gemini-api.md | 148 | threat-infographic.md | Image generation |
| infographic-error-handling.md | 67 | threat-infographic.md | Error condition |
| **Total** | **1,233** | | |

### Zero-Regression Verification

- 11 threat agents: BYTE-IDENTICAL (all checksums match baseline)
- 2 infographic templates: UNCHANGED
- 6 schemas: UNCHANGED
- SARIF 2.1.0 structure: VALIDATED (33 results, all required fields present)
- All 6 reference documents: LOADABLE (frontmatter present, content intact)

### Deviations from Target

1. **Orchestrator (1,273 vs 1,200 target)**: The plan estimated ~1,206 post-extraction. Actual prose condensation yielded ~150 lines (vs ~200 estimated). Remaining content is Phase 1-6 specification, dispatch rules, output format definitions, and defensive specification (DFD classification, non-conforming finding handling, three-state cell model). Further reduction would require removing specification content.

2. **Report (472 vs 400 target)**: The plan acknowledged ~448 as a realistic floor. Prose condensation yielded ~65 lines. Remaining content is input contract tables, quality validation checklists, report generation methodology, and remediation roadmap specification. All specification-type content.

3. **Infographic (414 vs 400 target)**: Within tolerance. Remaining content is data extraction methodology, specification format tables, and quality standards. All specification-type content.

---

## Orchestrator Agent (`adapters/claude-code/agents/orchestrator.md`)

**Total Lines**: 2086
**File**: adapters/claude-code/agents/orchestrator.md
**Schema Version**: 1.2
**Category**: orchestrator
**Status**: active

---

### Capabilities

1. **Architecture Input Parsing** -- Detects input format (ASCII, free-text, Mermaid, PlantUML, C4) via heuristic or explicit declaration. Extracts components, data flows, trust boundaries, and technologies from architecture descriptions.

2. **DFD Element Classification** -- Classifies every extracted component as one of four Data Flow Diagram element types: External Entity, Process, Data Store, or Data Flow. Handles ambiguous classification by defaulting to Process with a human-review annotation.

3. **Trust Boundary Identification** -- Identifies trust zones, zone components, and boundary crossings from format-specific notation (subgraph, boundary blocks, dashed lines, section headers, C4 boundary functions).

4. **STRIDE-per-Element Normalization** -- Applies deterministic STRIDE category mapping based on DFD element type (External Entity: S,R; Process: S,T,R,I,D,E; Data Store: T,I,D; Data Flow: T,I,D).

5. **AI Keyword Dispatch** -- Evaluates component names and descriptions against LLM keywords (LLM, model, GPT, Claude) and AG keywords (agent, autonomous, orchestrator, MCP server, tool server, plugin) for additive AI-specific threat agent dispatch. Handles dual-dispatch and keyword ambiguity.

6. **Agent Invocation Protocol** -- Defines context payload assembly (target components, full architecture context, analysis scope) and two dispatch modes (parallel concurrent, sequential single-prompt).

7. **Risk Level Validation** -- Validates every agent-returned risk_level against the OWASP 3x3 matrix and applies correction protocol when mismatches are detected.

8. **STRIDE Table Assembly** -- Collects findings from 6 STRIDE agents, validates risk levels, assigns sequential IDs, and assembles into 6 structured tables for Section 3.

9. **AI Threat Table Assembly** -- Maps 5 AI agents (agent-autonomy, tool-abuse, prompt-injection, data-poisoning, model-theft) to 2 output tables (AG, LLM) for Section 4.

10. **Correlation Detection** -- Identifies cross-category finding pairs targeting the same component using 5 deterministic correlation rules (CR-1 through CR-5). Assembles correlation groups with merged risk levels for Section 4a.

11. **Coverage Matrix Generation** -- Produces component-vs-category cross-reference matrix with deduplicated finding counts, three-state cell model (count, em-dash, n/a), and Total row/column.

12. **Risk Summary Computation** -- Computes aggregate deduplicated counts per risk level with percentages, includes Risk Calibration Matrix subsection for transparency.

13. **Recommended Actions List** -- Produces prioritized remediation list sorted by risk severity (Critical first), referencing all raw findings from all 8 tables.

14. **SARIF 2.1.0 Output Generation** -- Transforms all findings into SARIF JSON format with: category-to-rule-ID mapping, severity mapping, tool metadata, dual-location (physical + logical), fingerprint computation (SHA-256 truncated), correlated finding mapping (primary + relatedLocations), and SARIF taxonomy declarations (OWASP, CWE).

15. **Report Agent Dispatch (Phase 5)** -- Invokes threat-report.md agent in fresh context with threats.md as sole input. Produces threat-report.md with 7 sections and attack-trees/ directory.

16. **Infographic Agent Dispatch (Phase 6)** -- Invokes threat-infographic.md agent in fresh context with threats.md as sole input. Produces threat-infographic-spec.md and conditionally threat-infographic.jpg via Gemini API.

17. **Output Structural Validation** -- Runs comprehensive validation checklist covering section completeness, frontmatter validation, finding ID validation, field completeness, risk level consistency, cross-section consistency, SARIF output, Phase 5 outputs, and Phase 6 outputs.

18. **Error Handling** -- Three terminal errors (UNSUPPORTED_FORMAT, NO_COMPONENTS, INVALID_FORMAT_VALUE) with structured YAML responses, plus two non-terminal handlers (ambiguous DFD classification, non-conforming findings).

19. **Input Sanitization** -- Treats architecture input as data-only within `<architecture-input>` boundaries. Rejects prompt injection attempts, mandates confidential classification on all outputs.

20. **Opt-Out Configuration** -- Supports `--skip-report`, `--skip-infographic`, `TACHI_SKIP_INFOGRAPHIC` environment variable, and `report`/`infographic` configuration parameters for selective phase execution.

---

### Workflows

| Phase | Name | OWASP Question | Lines | Purpose |
|-------|------|----------------|-------|---------|
| Phase 1 | Scope | "What are we working on?" | 269-531 | Parse input, extract components, classify DFD types, identify trust boundaries, produce System Overview and Trust Boundaries |
| Phase 2 | Determine Threats | "What can go wrong?" | 534-807 | Apply STRIDE-per-Element normalization, AI keyword dispatch, produce dispatch table, invoke threat agents |
| Phase 3 | Determine Countermeasures | "What are we going to do about it?" | 811-1008 | Collect findings, validate risk levels, assemble STRIDE and AI tables, run correlation detection |
| Phase 4 | Assess | "Did we do a good enough job?" | 1012-1715 | Generate coverage matrix, risk summary, recommended actions, validate output structure, generate SARIF |
| Phase 5 | Report | "Communicate findings to stakeholders" | 1719-1781 | Invoke report agent, generate narrative threat report with attack trees |
| Phase 6 | Infographic | "Visualize the risk landscape" | 1785-1854 | Invoke infographic agent, generate visual risk specification and optional image |

---

### Integration Points

#### Agent Dispatches

| Agent File | Category | Dispatch Trigger | Phase |
|------------|----------|------------------|-------|
| `spoofing.md` | STRIDE (S) | DFD type: External Entity, Process | Phase 2 |
| `tampering.md` | STRIDE (T) | DFD type: Process, Data Store, Data Flow | Phase 2 |
| `repudiation.md` | STRIDE (R) | DFD type: External Entity, Process | Phase 2 |
| `info-disclosure.md` | STRIDE (I) | DFD type: Process, Data Store, Data Flow | Phase 2 |
| `denial-of-service.md` | STRIDE (D) | DFD type: Process, Data Store, Data Flow | Phase 2 |
| `privilege-escalation.md` | STRIDE (E) | DFD type: Process | Phase 2 |
| `prompt-injection.md` | AI/LLM | Keyword match: LLM, model, GPT, Claude | Phase 2 |
| `data-poisoning.md` | AI/LLM | Keyword match: LLM, model, GPT, Claude | Phase 2 |
| `model-theft.md` | AI/LLM | Keyword match: LLM, model, GPT, Claude | Phase 2 |
| `agent-autonomy.md` | AI/AG | Keyword match: agent, autonomous, orchestrator, MCP server, tool server, plugin | Phase 2 |
| `tool-abuse.md` | AI/AG | Keyword match: agent, autonomous, orchestrator, MCP server, tool server, plugin | Phase 2 |
| `threat-report.md` | Report | Phase 5 enabled (default-on) | Phase 5 |
| `threat-infographic.md` | Infographic | Phase 6 enabled (default-on) | Phase 6 |

#### Schema References

| Schema | Path | Purpose |
|--------|------|---------|
| `finding.yaml` | `schemas/finding.yaml` | Finding schema for agent output validation |
| `input.yaml` | `schemas/input.yaml` | Input format and recognition patterns |
| `output.yaml` | `schemas/output.yaml` | Output structure and schema_version |
| `report.yaml` | `schemas/report.yaml` | Report output structure |
| `infographic.yaml` | `schemas/infographic.yaml` | Infographic output structure |

#### Template References

| Template | Path | Purpose |
|----------|------|---------|
| `threats.md` | `templates/threats.md` | Output document structural reference |
| `threats.sarif` | `templates/threats.sarif` | SARIF structural reference with example values |
| `threat-report.md` | `templates/threat-report.md` | Report output structural reference |

#### External Contract

| Document | Path | Purpose |
|----------|------|---------|
| Interface Contract | `docs/INTERFACE-CONTRACT.md` | Input/output interface specification |

#### External Tool Dependencies

| Tool / Service | Purpose | Conditional |
|----------------|---------|-------------|
| Google Gemini API | Infographic image generation (`threat-infographic.jpg`) | Yes -- requires `GEMINI_API_KEY` environment variable |

---

### Section Content Map

| Section | Lines | Range | Content Type |
|---------|-------|-------|--------------|
| YAML Frontmatter (agent metadata) | 39 | 1-39 | Specification -- agent name, description, version, schema/template/agent references |
| Introduction / Role Description | 18 | 43-57 | Narrative -- role definition, platform-neutral statement, 6-phase pipeline overview |
| Input Sanitization Boundary | 20 | 60-78 | Specification -- 5 mandatory rules for treating architecture input as data |
| Output Format Specification (preamble) | 12 | 82-93 | Specification -- enumerates the 6 output files (threats.md, threats.sarif, threat-report.md, attack-trees/, threat-infographic-spec.md, threat-infographic.jpg) |
| Frontmatter Definition | 13 | 95-114 | Specification -- YAML frontmatter fields (schema_version, date, input_format, classification) |
| Section 1: System Overview Definition | 20 | 115-136 | Specification -- Components, Data Flows, Technologies table structures |
| Section 2: Trust Boundaries Definition | 17 | 137-154 | Specification -- Trust Zones and Boundary Crossings table structures |
| Section 3: STRIDE Tables Definition | 44 | 155-199 | Specification -- 6 STRIDE tables, ID prefix convention, finding row fields, OWASP 3x3 risk matrix |
| Section 4: AI Threat Tables Definition | 29 | 201-229 | Specification -- 2 AI tables, 5-agent-to-2-table mapping, OWASP references |
| Section 5: Coverage Matrix Definition | 12 | 230-241 | Specification -- component-vs-category matrix, three-state cell model, deduplication rules |
| Section 6: Risk Summary Definition | 13 | 243-257 | Specification -- aggregate risk counts, deduplication display, percentage computation |
| Section 7: Recommended Actions Definition | 9 | 258-266 | Specification -- prioritized finding list, sorting rules, remediation guidance |
| Phase 1: Scope Overview | 15 | 269-283 | Specification -- phase objectives, prerequisites, intermediate output requirement |
| Format Detection | 64 | 286-350 | Specification -- heuristic detection algorithm, 5 format recognition patterns (ASCII, Free-text, Mermaid, PlantUML, C4), priority order, summary table |
| Component Extraction and DFD Classification | 49 | 353-402 | Specification -- 4 DFD element type definitions with classification signals, ambiguous classification rule |
| Format-Specific Extraction | 12 | 404-415 | Specification -- extraction instructions per format (ASCII, Free-text, Mermaid, PlantUML, C4) |
| Trust Boundary Identification | 23 | 418-441 | Specification -- format-specific trust boundary notation, no-boundary handling |
| System Overview Assembly | 56 | 444-501 | Specification -- Section 1 and Section 2 assembly instructions, table population rules |
| Component Inventory (Intermediate Output) | 30 | 504-531 | Specification -- intermediate artifact format, self-check minimum requirements |
| Phase 2: Determine Threats Overview | 17 | 534-551 | Specification -- phase objectives, prerequisites, two rule sets |
| STRIDE-per-Element Normalization | 47 | 554-599 | Specification -- YAML normalization mapping, quick reference table, dispatch logic |
| AI Keyword Dispatch Rules | 63 | 602-663 | Specification -- LLM keywords, AG keywords, matching rules, dual-dispatch, ambiguity handling, agent-to-table mapping |
| Agent Invocation Protocol | 44 | 666-709 | Specification -- context payload definition (target components, full architecture, analysis scope), payload assembly instructions |
| Dispatch Protocol | 38 | 712-748 | Specification -- parallel mode, sequential mode, category order, platform-neutral note |
| Dispatch Table (Intermediate Output) | 59 | 752-807 | Specification -- table format, example rows, summary metrics, self-check |
| Phase 3: Determine Countermeasures Overview | 16 | 811-826 | Specification -- phase objectives, prerequisites |
| Risk Level Validation | 42 | 828-869 | Specification -- OWASP 3x3 matrix, lookup table, correction protocol |
| STRIDE Table Assembly | 31 | 872-904 | Specification -- 6-table assembly order, finding row format, sequential ID assignment, empty category handling |
| AI Threat Table Assembly | 33 | 907-941 | Specification -- 5-agent-to-2-table mapping, assembly instructions, no-AI-dispatch handling |
| Correlation Detection | 57 | 944-999 | Specification -- 5 correlation rules (CR-1 to CR-5), detection algorithm, group assembly, self-check |
| Section 4a Assembly | 8 | 1001-1008 | Specification -- correlation group table format, zero-correlation handling |
| Phase 4: Assess Overview | 13 | 1012-1024 | Specification -- phase objectives |
| Coverage Matrix Generation | 43 | 1027-1070 | Specification -- matrix structure, cell values (three-state model), total column/row, footnote, self-check |
| Risk Calibration Matrix | 19 | 1078-1098 | Template -- markdown output block for risk calibration subsection |
| Risk Summary Computation | 23 | 1100-1121 | Specification -- computation rules (6 steps), deduplication, percentages, zero-finding handling |
| Recommended Actions | 14 | 1122-1135 | Specification -- sorting rules (primary: risk level, secondary: table order), raw count requirement |
| Output Structural Validation Checklist | 67 | 1138-1201 | Specification -- 30+ validation checks across section completeness, frontmatter, finding IDs, fields, risk levels, cross-section consistency, SARIF, Phase 5, Phase 6 |
| SARIF Output Generation (preamble) | 5 | 1224-1228 | Specification -- phase context, no additional analysis needed |
| SARIF Category to Rule ID Mapping | 22 | 1230-1249 | Reference -- 8-row mapping table from finding IR category to SARIF rule ID |
| SARIF Severity Mapping | 13 | 1251-1263 | Reference -- 5-row mapping table from Tachi risk level to SARIF level and security-severity |
| SARIF Tool Metadata | 8 | 1265-1272 | Specification -- tool.driver fields (name, semanticVersion, informationUri, rules) |
| SARIF Rule Definition Templates | 46 | 1274-1319 | Specification -- reportingDescriptor structure, tag constraints, security-severity on rules, 3 reference examples |
| SARIF Finding IR to Result Mapping | 41 | 1321-1361 | Specification -- 6-step mapping procedure, complete field mapping reference table |
| SARIF Correlated Finding Mapping | 90 | 1363-1446 | Specification -- 6-step correlation mapping, primary/peer distinction, relatedLocations assembly, JSON example |
| SARIF Dual-Location Instructions | 47 | 1448-1493 | Specification -- physicalLocation and logicalLocations requirements, kind mapping, JSON example |
| SARIF Fingerprint Computation | 47 | 1495-1541 | Specification -- primaryLocationLineHash (SHA-256 truncated), findingId/v1, correlationGroup (conditional), determinism requirements, JSON examples |
| SARIF Taxonomies | 66 | 1543-1664 | Specification -- taxonomy declarations (OWASP, CWE), supportedTaxonomies, rule relationships, category-to-taxonomy mapping table, JSON examples |
| SARIF Schema Compliance Structure | 35 | 1666-1700 | Specification -- top-level JSON structure, structural requirements |
| SARIF JSON Structural Self-Check | 15 | 1703-1715 | Specification -- 5 validation checks for SARIF output |
| Phase 5: Report Overview | 12 | 1719-1729 | Specification -- phase objectives, outputs |
| Phase 5 Dispatch | 32 | 1732-1763 | Specification -- opt-out check, fresh-context invocation, context isolation boundary, output placement |
| Phase 5 Opt-Out Configuration | 18 | 1767-1781 | Specification -- flag, configuration, backward compatibility |
| Phase 6: Infographic Overview | 14 | 1785-1798 | Specification -- phase objectives, pipeline isolation requirement |
| Phase 6 Dispatch | 33 | 1800-1832 | Specification -- opt-out check, fresh-context invocation, context isolation boundary, output placement |
| Phase 6 Opt-Out Configuration | 19 | 1836-1854 | Specification -- flag, environment variable, configuration, backward compatibility |
| Error Handling Overview | 6 | 1857-1861 | Specification -- consolidation statement, terminal vs non-terminal errors |
| UNSUPPORTED_FORMAT Error | 43 | 1863-1904 | Specification -- trigger, when-to-raise, YAML error response template, guidance text |
| NO_COMPONENTS Error | 42 | 1908-1945 | Specification -- trigger, when-to-raise, YAML error response template, guidance text |
| INVALID_FORMAT_VALUE Error | 42 | 1949-1987 | Specification -- trigger, when-to-raise, YAML error response template, guidance text |
| Error Evaluation Order | 8 | 1990-1999 | Specification -- 3-step priority order (INVALID_FORMAT_VALUE, UNSUPPORTED_FORMAT, NO_COMPONENTS) |
| Ambiguous DFD Classification Handling | 33 | 2002-2034 | Specification -- default classification rule, human review flag, AI keyword ambiguity ("model") |
| Non-Conforming Finding Handling | 29 | 2037-2066 | Specification -- detection criteria, 4-step handling protocol, rationale |
| Coverage Matrix: Three-State Cell Model | 20 | 2070-2086 | Specification -- three-state definitions (count, em-dash, n/a), consumer guidance |

---

### Content Type Summary

| Content Type | Section Count | Approximate Lines |
|--------------|---------------|-------------------|
| Specification | 49 | ~1810 |
| Reference (lookup tables) | 2 | ~35 |
| Template (markdown output blocks) | 1 | ~19 |
| Narrative (role description) | 1 | ~18 |
| **Total** | **53** | **2086** |

---

### Correlation Rule Reference

| Rule | STRIDE Category | AI Category | Correlation Basis |
|------|----------------|-------------|-------------------|
| CR-1 | Tampering (T) | Data-Poisoning (LLM) | Data integrity |
| CR-2 | Privilege-Escalation (E) | Agent-Autonomy (AG) | Excessive permissions |
| CR-3 | Info-Disclosure (I) | Prompt-Injection (LLM) | Information leakage |
| CR-4 | Repudiation (R) | Agent-Autonomy (AG) | Accountability gaps |
| CR-5 | Denial-of-Service (D) | Tool-Abuse (AG) | Resource exhaustion |

---

### Error Response Reference

| Error Code | Type | Phase | Trigger |
|------------|------|-------|---------|
| INVALID_FORMAT_VALUE | Terminal | Phase 1 (pre-parse) | Format field contains invalid enum value |
| UNSUPPORTED_FORMAT | Terminal | Phase 1 (detection) | Auto-detection fails all 5 format patterns |
| NO_COMPONENTS | Terminal | Phase 1 (self-check) | Fewer than 1 component or 0 data flows extracted |
| Ambiguous DFD Classification | Non-terminal | Phase 1 (classification) | Component cannot be confidently classified |
| Non-Conforming Finding | Non-terminal | Phase 3 (collection) | Agent finding missing required fields or invalid values |

---

### Self-Check Points

The orchestrator defines 6 explicit self-check gates that halt progression until validation passes:

1. **Component Inventory Self-Check** (Phase 1, line ~521-530) -- Minimum 1 component and 1 data flow
2. **Dispatch Table Self-Check** (Phase 2, line ~798-807) -- All components present, STRIDE categories correct, AI categories valid, counts correct
3. **Correlation Self-Check** (Phase 3, line ~992-999) -- No duplicate finding IDs across groups, all referenced IDs exist, each group has minimum 2 categories, group risk level correct
4. **Coverage Matrix Self-Check** (Phase 4, line ~1059-1070) -- All components present, cell values reflect deduplication, totals correct
5. **Output Structural Validation Checklist** (Phase 4, line ~1138-1220) -- 30+ checks across all sections, frontmatter, finding IDs, fields, risk levels, cross-section consistency, SARIF, Phase 5, Phase 6
6. **SARIF JSON Structural Self-Check** (Phase 4, line ~1703-1715) -- Required JSON properties, result completeness, rule-result consistency, severity format, result count

---

## Threat-Report Agent (`adapters/claude-code/agents/threat-report.md`)

**Total Lines**: 802
**File**: adapters/claude-code/agents/threat-report.md

### Capabilities

1. **Input Validation** -- Validates threats.md structure (YAML frontmatter, 7 required sections plus Section 4a, minimum one finding)
2. **Executive Summary Generation** -- Produces a <=500-word summary with risk posture, top 3-5 threats by business impact, key recommendations, compliance relevance (SOC2, ISO 27001, CWE, OWASP), and remediation timeline tiers
3. **Architecture Overview Generation** -- Transforms Section 1 (System Overview) and Section 2 (Trust Boundaries) into narrative-form architecture context for non-technical readers
4. **Threat Analysis Generation** -- Produces agent-by-agent narrative organized by 8 threat categories (S, T, R, I, D, E, AG, LLM) with per-finding detail (ID, component, threat description, risk context, mitigation summary)
5. **Progressive Technical Depth** -- Scales narrative detail by severity: full analysis for Critical/High, standard for Medium, aggregate summaries for Low/Note
6. **Large Threat Model Handling** -- Special summarization rules when findings exceed 30
7. **Cross-Cutting Theme Detection** -- Identifies emergent patterns across findings using 4 detection criteria: component convergence, mitigation similarity, attack chain formation, component cluster density
8. **Correlation Group Handling** -- Consumes Section 4a correlation groups and applies unified narrative, attack tree cross-references, and consolidated roadmap treatment
9. **Attack Tree Construction** -- Generates Mermaid attack trees for every Critical and High finding using Bruce Schneier's methodology (root/intermediate/leaf nodes with AND/OR gates)
10. **Mermaid Diagram Generation** -- Produces syntactically valid Mermaid `flowchart TD` diagrams with strict node ID conventions, shape syntax, edge syntax, and color styling
11. **Mermaid Validation** -- Self-validates every tree against syntax safety, structural integrity, naming convention, styling, and readability checklists
12. **Dual Output Location** -- Emits each attack tree both inline in threat-report.md Section 5 and as standalone files in `attack-trees/`
13. **Remediation Roadmap Generation** -- Transforms findings into a prioritized, actionable table ordered by risk level and grouped by component within tiers
14. **Effort Estimation** -- Assigns qualitative effort (Low/Medium/High) to each roadmap item using keyword-based heuristics from mitigation text
15. **Correlation Consolidation for Roadmap** -- Merges correlated findings into single roadmap items with combined mitigation scope and correlation scope notes
16. **Finding Reference Appendix Generation** -- Produces a traceability mapping table ensuring every finding ID appears with all report sections where it is referenced
17. **Zero Finding Loss Validation** -- Self-checks that the appendix finding ID count matches the input threats.md finding ID count exactly
18. **Output Structural Validation** -- Runs a comprehensive checklist covering section completeness, finding traceability, attack tree completeness, Mermaid syntax integrity, and content quality

### Workflows

| Phase | Description | Lines |
|-------|-------------|-------|
| Input Validation | Parse and validate threats.md structure and required sections | 84-91 |
| Executive Summary Generation | Produce risk posture, top threats, recommendations, compliance mapping, timeline | 155-185 |
| Architecture Overview Generation | Narrative system context from Sections 1 and 2 | 188-209 |
| Threat Analysis Generation | Agent-by-agent finding narrative with progressive depth | 212-253 |
| Cross-Cutting Theme Detection | Pattern identification across findings using 4 criteria | 256-284 |
| Correlation Group Handling | Unified narrative, attack tree, and roadmap treatment for correlated findings | 288-314 |
| Attack Tree Construction | Mermaid tree generation for Critical/High findings | 349-390 |
| Mermaid Rendering | Syntax conventions, node shapes, edges, color styling | 393-479 |
| Mermaid Validation | Pre-output checklist for syntax, structure, naming, styling, readability | 482-529 |
| Dual Output | Inline embedding in Section 5 plus standalone files in attack-trees/ | 643-701 |
| Remediation Roadmap Generation | Priority-ordered, component-grouped actionable table | 704-744 |
| Effort Estimation | Qualitative complexity assessment for each roadmap item | 747-770 |
| Correlation Consolidation | Merge correlated findings into single roadmap items | 773-801 |
| Finding Reference Appendix | Traceability mapping table with zero-loss validation | 317-346 |
| Output Structural Validation | Final quality checklist across all sections | 95-149 |

### Integration Points

| Integration | Type | Reference |
|-------------|------|-----------|
| `../../../schemas/output.yaml` | Input schema | threats.md structure definition (v1.1) |
| `../../../schemas/report.yaml` | Output schema | Report structure definition |
| `../../../schemas/finding.yaml` | Data schema | Finding IR field definitions (v1.0) |
| `../../../templates/threat-report.md` | Template | Report section heading and layout template |
| `threats.md` | Runtime input | Produced by orchestrator Phase 4 (Assess) |
| `threat-report.md` | Primary output | 7-section narrative report |
| `attack-trees/{finding-id}-attack-tree.md` | Secondary output | Standalone attack tree files per Critical/High finding |

### Section Content Map

| Section | Lines | Range | Content Type |
|---------|-------|-------|--------------|
| YAML Frontmatter | 4 | 1-4 | Specification |
| Metadata (YAML block) | 16 | 6-22 | Specification |
| Core Mission | 16 | 24-38 | Specification |
| Input Contract | 52 | 40-91 | Specification |
| -- Required Input Sections (table) | 12 | 43-56 | Reference |
| -- Finding IR Fields Consumed (table) | 15 | 57-73 | Reference |
| -- Correlation Group Fields (table) | 9 | 74-83 | Reference |
| -- Input Validation (rules) | 5 | 84-91 | Specification |
| Quality Standards | 56 | 93-149 | Specification |
| -- Output Structural Validation Checklist | 33 | 95-141 | Specification |
| ---- Section Completeness | 4 | 99-103 | Specification |
| ---- Finding Traceability (Zero Loss Rule) | 4 | 105-109 | Specification |
| ---- Attack Tree Completeness | 6 | 111-117 | Specification |
| ---- Mermaid Syntax Integrity | 12 | 119-131 | Specification |
| ---- Content Quality | 8 | 133-141 | Specification |
| -- Edge Cases | 8 | 142-149 | Specification |
| Report Generation Methodology | 3 | 153-154 | Narrative (section header) |
| -- Executive Summary Generation | 31 | 155-185 | Specification |
| ---- 5 Required Elements | 21 | 159-178 | Specification |
| ---- Language Rules | 5 | 180-185 | Specification |
| -- Architecture Overview Generation | 21 | 188-209 | Specification |
| ---- System Context | 8 | 192-199 | Specification |
| ---- Trust Boundary Summary | 8 | 201-209 | Specification |
| -- Threat Analysis Generation | 42 | 212-253 | Specification |
| ---- Structure (8 category subsections) | 12 | 218-228 | Specification |
| ---- Per-Finding Narrative | 8 | 230-238 | Specification |
| ---- Progressive Technical Depth | 7 | 239-246 | Specification |
| ---- Large Threat Model Handling | 6 | 247-253 | Specification |
| -- Cross-Cutting Theme Detection | 28 | 256-284 | Specification |
| ---- 4 Detection Criteria | 12 | 260-271 | Specification |
| ---- Theme Presentation | 8 | 273-280 | Specification |
| ---- Minimum Thresholds | 4 | 281-284 | Specification |
| -- Correlation Group Handling | 27 | 288-314 | Specification |
| ---- Narrative Treatment (Section 3) | 5 | 292-297 | Specification |
| ---- Attack Tree Treatment (Section 5) | 5 | 298-303 | Specification |
| ---- Remediation Roadmap Treatment (Section 6) | 6 | 304-309 | Specification |
| ---- Missing Section 4a | 3 | 311-314 | Specification |
| -- Finding Reference Appendix Generation | 29 | 317-346 | Specification |
| ---- Zero Finding Loss Rule | 3 | 321-324 | Specification |
| ---- Mapping Table Structure | 12 | 325-337 | Specification / Template |
| ---- Completeness Self-Check | 6 | 339-346 | Specification |
| Attack Tree Construction Rules | 42 | 349-390 | Specification |
| -- Tree Structure (3 node types) | 10 | 355-364 | Specification |
| -- Minimum Depth Requirements (table) | 6 | 365-372 | Specification |
| -- Decomposition Stopping Rule | 8 | 374-382 | Specification |
| -- Asymmetry and Realism | 6 | 384-390 | Specification |
| Mermaid Conventions | 87 | 393-479 | Specification / Template |
| -- Orientation | 3 | 397-400 | Specification |
| -- Node ID Format (table + rules) | 16 | 401-418 | Specification |
| -- Node Shapes and Labels (table + rules) | 15 | 419-433 | Specification / Template |
| -- Edge Syntax (code block) | 10 | 434-445 | Template |
| -- Color Styling (code block + table) | 26 | 447-479 | Template |
| Mermaid Validation Checklist | 48 | 482-529 | Specification |
| -- Syntax Safety | 9 | 487-496 | Specification |
| -- Structural Integrity | 7 | 498-504 | Specification |
| -- Naming Convention | 5 | 506-512 | Specification |
| -- Styling | 8 | 514-521 | Specification |
| -- Readability | 5 | 523-529 | Specification |
| Example Attack Trees | 108 | 532-640 | Template / Narrative |
| -- Example 1: Critical AG-1 Pattern | 52 | 536-589 | Template |
| ---- Mermaid code block | 39 | 540-579 | Template |
| ---- Demonstration notes | 9 | 581-589 | Narrative |
| -- Example 2: High LLM-2 Pattern | 49 | 591-640 | Template |
| ---- Mermaid code block | 34 | 596-630 | Template |
| ---- Demonstration notes | 9 | 632-640 | Narrative |
| Dual Output Location | 60 | 643-701 | Specification |
| -- Location 1: Inline in threat-report.md | 18 | 647-668 | Specification / Template |
| -- Location 2: Standalone Files | 27 | 670-697 | Specification / Template |
| -- File Inventory | 3 | 698-701 | Specification |
| Remediation Roadmap Generation | 41 | 704-744 | Specification |
| -- Priority Ordering (table) | 10 | 710-719 | Specification |
| -- Roadmap Item Format (table + field rules) | 16 | 720-736 | Specification / Template |
| -- Section Introduction | 6 | 738-744 | Specification |
| Effort Estimation Heuristics | 25 | 747-770 | Specification |
| -- Effort Levels (table) | 6 | 752-758 | Specification |
| -- Assessment Rules (5 rules) | 12 | 759-770 | Specification |
| Correlation Consolidation for Roadmap | 31 | 773-801 | Specification |
| -- Consolidation Rules (5 rules) | 12 | 778-788 | Specification |
| -- Example (table) | 10 | 789-798 | Template |
| -- No Correlation Groups | 3 | 799-801 | Specification |

---

## Threat-Infographic Agent (`adapters/claude-code/agents/threat-infographic.md`)

**Total Lines**: 593
**File**: adapters/claude-code/agents/threat-infographic.md

### Capabilities

1. **Threat model data extraction** -- Parses structured `threats.md` output (conforming to `schemas/output.yaml` v1.1) to extract severity counts, component risk profiles, and finding details across STRIDE and AI threat categories.
2. **Multi-template infographic specification generation** -- Produces self-contained markdown specification files (`threat-{template-name}-spec.md`) with 6 required sections conforming to `schemas/infographic.yaml`.
3. **Baseball Card template** -- Compact risk summary dashboard with donut chart, STRIDE+AI heat map, critical finding cards, and architecture overlay strip.
4. **System Architecture template** -- Annotated architecture diagram with trust zones, components with attack surface badges, data flow arrows colored by severity, and finding IDs overlaid.
5. **Template aliasing** -- Maps `corporate-white` alias to `baseball-card`; supports `all` keyword to generate both templates sequentially.
6. **Risk distribution computation** -- Extracts aggregate severity counts from Section 6 (authoritative source) with fallback to direct enumeration from Sections 3, 4, and 4a with deduplication.
7. **Component x Risk Level cross-tabulation** -- Builds heat map matrix (rows = components, columns = severity levels), sorted descending by total, capped at 8 named rows plus "Other" aggregation.
8. **Top Critical Findings selection** -- Selects up to 5 findings prioritizing Critical then High, with edge case handling for absence of Critical/High findings.
9. **Per-component risk weight classification** -- Computes weighted risk scores (Critical=4, High=3, Medium=2, Low=1) and classifies components as High/Medium/Low risk weight.
10. **Spatial layout extraction** (System Architecture only) -- Parses trust zones, orders by trust level, places components within zones, maps data flows with severity-colored arrows, and maps boundary crossings with finding IDs.
11. **Gemini API image generation** -- Constructs narrative prompts from design templates, calls Gemini image generation API, parses base64 image responses, and saves JPEG output.
12. **API key management** -- Checks `GEMINI_API_KEY` environment variable with `.env` file fallback sourcing.
13. **Fallback model retry** -- Attempts `gemini-3.1-flash-image-preview` if default model (`gemini-3-pro-image-preview`) returns 404/model unavailability.
14. **Graceful degradation** -- Handles 6 error conditions (missing API key, rate limit, timeout, content policy rejection, missing Section 6, empty threat model) without blocking pipeline; specification always preserved.
15. **Input validation** -- Validates `threats.md` contains YAML frontmatter with `schema_version`, at least Sections 3 or 4 with findings.
16. **Output structural validation** -- 14-point checklist covering section completeness, data accuracy, component integrity, finding selection, and visual design correctness.
17. **Prompt safety framing** -- Uses business-oriented language ("risk assessment summary", "security posture overview") to minimize Gemini content policy rejections; avoids attack-specific terminology.
18. **Note severity exclusion** -- Excludes Note-level findings from visual risk distribution and heat map for executive clarity while including them in total finding count.

### Workflows

1. **Data Extraction Phase** (5 steps)
   - Step 1: Parse YAML frontmatter for metadata (date, schema_version, classification, project name, component count)
   - Step 2: Extract Section 6 for risk distribution (severity counts, percentages) with fallback computation
   - Step 3: Cross-tabulate Component x Risk Level for heat map (matrix build, sorting, 8-row cap with "Other" aggregation)
   - Step 4: Select top 5 findings for Critical Findings section (priority: Critical > High > Medium)
   - Step 5: Aggregate per-component risk for Architecture Overlay (weighted scoring, risk weight classification)
   - Step 5b: Spatial layout extraction for System Architecture template (trust zones, component placement, data flows, boundary crossings)

2. **Specification Generation Phase** (6 sections)
   - Section 1: Metadata (project name, scan date, analysis agents, total findings, risk posture)
   - Section 2: Risk Distribution (severity table with counts, percentages, hex colors)
   - Section 3: Coverage Heat Map (component x severity matrix)
   - Section 4: Top Critical Findings (up to 5 entries with ID, component, threat summary, risk level)
   - Section 5: Architecture Threat Overlay (tabular for baseball-card, spatial for system-architecture)
   - Section 6: Visual Design Directives (loaded from design template file or fallback directives)

3. **Gemini Prompt Construction Phase**
   - Load design template from `.claude/agents/tachi/templates/infographic-{name}.md`
   - Replace placeholders with extracted data
   - Frame prompt with aesthetic intent first, data content second
   - Apply business-oriented language (prompt safety)

4. **API Call Phase**
   - Check GEMINI_API_KEY (env var then .env fallback)
   - POST to Gemini generateContent endpoint with constructed prompt
   - Parse response for base64 inline_data image
   - Save decoded JPEG
   - Attempt fallback model on 404

5. **Validation Phase**
   - Run 14-point output structural validation checklist
   - Verify section completeness, data accuracy, component integrity, finding selection, visual design

### Integration Points

**Input schemas**:
- `schemas/output.yaml` (v1.1) -- Input contract for `threats.md` structure
- `schemas/finding.yaml` (v1.0) -- Individual finding IR field definitions (id, component, threat, risk_level)
- `schemas/infographic.yaml` -- Output schema for generated specification

**Design templates**:
- `.claude/agents/tachi/templates/infographic-baseball-card.md` -- Baseball Card design template with Gemini prompt template
- `.claude/agents/tachi/templates/infographic-system-architecture.md` -- System Architecture design template with spatial Section 5 schema

**External API**:
- Gemini Image Generation API: `POST https://generativelanguage.googleapis.com/v1beta/models/{model_id}:generateContent`
- Default model: `gemini-3-pro-image-preview`
- Fallback model: `gemini-3.1-flash-image-preview`
- Auth: `x-goog-api-key` header from `GEMINI_API_KEY` environment variable
- Response modalities: TEXT + IMAGE, aspect ratio 16:9, resolution 2K

**Environment variables**:
- `GEMINI_API_KEY` -- Required for image generation; sourced from env or `.env` file

**Architecture references**:
- ADR-002 -- Context isolation (agent runs in fresh context with only `threats.md`)
- ADR-010 -- Context isolation (referenced alongside ADR-002)

**Output files**:
- `threat-{template-name}-spec.md` -- Primary deliverable (always produced)
- `threat-{template-name}.jpg` -- Conditional deliverable (requires GEMINI_API_KEY and successful API call)

### Section Content Map

| Section | Lines | Range | Content Type |
|---------|-------|-------|--------------|
| YAML Frontmatter | 4 | 1-4 | Specification |
| Metadata (embedded YAML) | 17 | 6-25 | Specification |
| Core Mission | 36 | 27-62 | Narrative |
| Core Mission > Available Templates | 11 | 39-49 | Reference |
| Core Mission > Output | 9 | 51-59 | Specification |
| Input Contract | 38 | 63-100 | Specification |
| Input Contract > Required Input Sections | 12 | 69-81 | Reference |
| Input Contract > Finding IR Fields Consumed | 10 | 82-92 | Reference |
| Input Contract > Input Validation | 5 | 93-99 | Specification |
| Data Extraction Methodology | 82 | 101-183 | Specification |
| Data Extraction > Step 1: Parse Frontmatter | 11 | 106-116 | Specification |
| Data Extraction > Step 2: Extract Section 6 | 17 | 117-133 | Specification |
| Data Extraction > Step 3: Cross-Tabulate Heat Map | 12 | 134-145 | Specification |
| Data Extraction > Step 4: Select Top 5 Findings | 12 | 146-158 | Specification |
| Data Extraction > Step 5: Aggregate Per-Component Risk | 10 | 159-169 | Specification |
| Data Extraction > Step 5b: Spatial Layout Extraction | 12 | 170-183 | Specification |
| Infographic Specification Format | 155 | 184-338 | Template |
| Spec Format > YAML Frontmatter | 11 | 190-201 | Template |
| Spec Format > Section 1: Metadata | 15 | 202-216 | Template |
| Spec Format > Section 2: Risk Distribution | 17 | 217-233 | Template |
| Spec Format > Section 3: Coverage Heat Map | 17 | 234-251 | Template |
| Spec Format > Section 4: Top Critical Findings | 16 | 252-268 | Template |
| Spec Format > Section 5: Architecture Threat Overlay | 17 | 269-288 | Template |
| Spec Format > Section 6: Visual Design Directives | 46 | 289-338 | Template |
| Quality Standards | 50 | 339-387 | Specification |
| Quality Standards > Output Structural Validation Checklist | 30 | 345-377 | Specification |
| Quality Standards > Edge Cases | 8 | 378-386 | Specification |
| Gemini API Prompt Construction | 47 | 388-443 | Specification |
| Prompt Construction > Design Template | 5 | 392-396 | Specification |
| Prompt Construction > Prompt Framing | 3 | 398-401 | Narrative |
| Prompt Construction > Design Philosophy | 7 | 403-409 | Narrative |
| Prompt Construction > Prompt Structure | 18 | 410-431 | Template |
| Prompt Construction > Color Specification | 9 | 433-443 | Reference |
| Gemini API Integration | 107 | 444-593 | Specification |
| API Integration > Configuration | 14 | 446-461 | Specification |
| API Integration > API Key Check | 10 | 462-474 | Specification |
| API Integration > API Request | 22 | 475-511 | Specification |
| API Integration > Response Parsing | 12 | 512-525 | Specification |
| API Integration > Fallback Model Attempt | 3 | 527-529 | Specification |
| Error Handling and Graceful Degradation | 62 | 531-593 | Specification |
| Error Handling > Condition 1: Missing API Key | 5 | 537-541 | Specification |
| Error Handling > Condition 2: Rate Limit (429) | 6 | 543-549 | Specification |
| Error Handling > Condition 3: API Timeout | 5 | 551-555 | Specification |
| Error Handling > Condition 4: Content Policy Rejection | 6 | 557-562 | Specification |
| Error Handling > Condition 5: Missing Section 6 | 6 | 564-568 | Specification |
| Error Handling > Condition 6: Empty Threat Model | 13 | 570-582 | Specification |
| Error Handling > Degradation Summary Table | 11 | 583-593 | Reference |
