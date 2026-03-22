# Architect Review: tasks.md (Feature 003 - Orchestrator Agent)

**Reviewer**: architect
**Date**: 2026-03-21
**Artifact**: `specs/003-orchestrator-agent/tasks.md`
**Cross-references reviewed**: spec.md, plan.md, docs/INTERFACE-CONTRACT.md, schemas/finding.yaml, schemas/output.yaml, templates/threats.md, agents/ai/README.md, agents/orchestrator.md (placeholder)

---

## Overall Assessment

**STATUS: APPROVED_WITH_CONCERNS**

The tasks.md is architecturally sound. Dependency ordering is correct, parallel opportunities are safely identified, artifact references are accurate, and the single-file authoring strategy is well-suited to this deliverable. Two MEDIUM concerns and one LOW concern are documented below -- all are addressable during implementation without structural changes to the task breakdown.

---

## Evaluation Criteria

### 1. Dependency Ordering (Parse -> Dispatch -> Assembly)

**Verdict: CORRECT**

The dependency chain is properly ordered:

- **Phase 1 (Setup) -> Phase 2 (Foundational)**: T001 reads reference artifacts, T002 establishes prompt skeleton. T003-T004 create infrastructure sections (input boundary, output format). This is correct -- all subsequent OWASP phase sections reference these foundational elements.
- **Phase 3 (US1 Parse) -> Phase 4 (US2 Dispatch)**: Parse (T005-T010) produces the component inventory that dispatch (T011-T016) references. The tasks.md correctly marks this as a blocking dependency.
- **Phase 4 (US2 Dispatch) -> Phase 5 (US3 Assemble)**: Dispatch (T011-T016) produces the agent invocation targets that assembly (T017-T024) collects findings from. Correctly ordered.
- **Phase 6 (US4 Error Handling)**: Depends on US1 (Parse) because error conditions reference parsing and classification logic. Correctly identified as parallelizable with US2/US3 since error handling occupies a separate prompt section. The dependency on US1 (not US2) is appropriate -- errors fire during format detection and component classification, before dispatch.
- **Phase 7 (Polish)**: Correctly depends on all user stories being complete.

Within each phase, the internal ordering follows the correct pattern: preamble -> reference data -> logic -> intermediate output. This matches how the prompt will be consumed top-to-bottom by an LLM.

### 2. Parallel Opportunities

**Verdict: CORRECT -- no conflicting file edits**

All four identified parallel waves are safe:

| Wave | Tasks | Conflict Analysis |
|------|-------|-------------------|
| Foundational | T003, T004 | Different sections: Input Sanitization Boundary vs. Output Format Specification. No overlap. |
| Tables | T019, T020 | Different sections: STRIDE table assembly vs. AI table assembly. No content overlap. |
| Errors | T025, T026, T027 | Three independent error response sections. No shared content. |
| Validation | T030, T031, T032 | Read-only validation against different example inputs. No file edits. |

**US4 parallel with US2/US3**: The tasks.md correctly notes US4 can run in parallel with US2/US3 because error handling targets a different prompt section than dispatch and assembly. This is accurate -- the error handling section in the plan.md is positioned separately from the OWASP phase sections.

**Single-file caveat**: While the parallel opportunities are correctly identified at the section level, the Implementation Strategy section (line 207-213) correctly acknowledges that sequential execution by a single agent is most practical since all tasks target one file. The parallel annotations serve as documentation of logical independence rather than mandatory concurrency requirements. This is the right approach.

### 3. Artifact References

**Verdict: CORRECT -- all references verified against source artifacts**

| Task | Referenced Artifact | Section/Field | Verified |
|------|-------------------|---------------|----------|
| T004 | `templates/threats.md` | 7-section output structure | YES -- 7 required sections confirmed in template |
| T006 | `docs/INTERFACE-CONTRACT.md` Section 1 | Heuristic priority order | YES -- ASCII(1) -> free-text(2) -> Mermaid(3) -> PlantUML(4) -> C4(5) matches |
| T007 | DFD classification | 4 element types | YES -- External Entity, Process, Data Store, Data Flow per INTERFACE-CONTRACT.md Section 2 |
| T008 | Format-specific trust boundary notation | 5 notations | YES -- subgraph(Mermaid), dashed lines(ASCII), boundary(PlantUML), System_Boundary(C4), section headers(free-text) all match INTERFACE-CONTRACT.md Section 1 |
| T009 | `templates/threats.md` Section 1 | Components, Data Flows, Technologies tables | YES -- all 3 tables present in template Section 1 |
| T012 | `docs/INTERFACE-CONTRACT.md` Section 2 | STRIDE-per-Element normalization table | YES -- External Entity(S,R), Process(S,T,R,I,D,E), Data Store(T,I,D), Data Flow(T,I,D) matches verbatim |
| T013 | `docs/INTERFACE-CONTRACT.md` Section 3 | AI keyword dispatch rules | YES -- LLM keywords (LLM, model, GPT, Claude) and AG keywords (agent, autonomous, orchestrator, MCP server, tool server, plugin) match |
| T018 | `schemas/finding.yaml` | OWASP 3x3 matrix | YES -- matrix values match (HIGH/HIGH=Critical, HIGH/MEDIUM=High, etc.) |
| T019 | `templates/threats.md` Section 3 | STRIDE table field definitions | YES -- ID, Component, Threat, Likelihood, Impact, Risk Level, Mitigation confirmed |
| T020 | `agents/ai/README.md` | 5-to-2 table mapping | YES -- agent-autonomy+tool-abuse=AG, prompt-injection+data-poisoning+model-theft=LLM confirmed |
| T024 | Finding ID pattern | `{CATEGORY_PREFIX}-{N}` | YES -- matches `schemas/finding.yaml` pattern `^(S|T|R|I|D|E|AG|LLM)-\\d+$` |
| T025-T027 | `docs/INTERFACE-CONTRACT.md` Section 7 | Error codes and responses | YES -- all 3 error conditions (UNSUPPORTED_FORMAT, NO_COMPONENTS, INVALID_FORMAT_VALUE) match verbatim |

No missing or incorrect references found.

### 4. Plan Architect Concerns Addressed

The plan.md architect sign-off noted two concerns:

#### Concern 1 (MEDIUM): Agent Context Payload Format -- T014

**Plan concern**: "Agent context payload format" -- how the orchestrator communicates parsed architecture context to each threat agent.

**T014 text**: "Author agent invocation protocol specifying that each agent receives full parsed architecture context (all components, data flows, trust boundaries) and is told which specific component(s) to analyze"

**Assessment**: T014 addresses the *what* (full architecture context + targeted component) but does not specify the *format* of the payload. The interface contract (Section 5) defines the input format (content, format, context fields) but does not prescribe how the orchestrator structures context when invoking subordinate agents. This is a prompt-authoring decision, not an interface contract gap.

**Concern status**: PARTIALLY ADDRESSED. T014 covers the requirement (FR-008: send full parsed architecture context) but the implementer will need to decide on the structural format of the context payload within the prompt. This is acceptable for a task-level description -- the format decision is an implementation detail that the prompt author will resolve during T014 execution. However, the task could benefit from a brief note acknowledging that the payload structure (e.g., inline markdown tables vs. structured YAML block vs. reference to intermediate artifact) needs to be decided during authoring.

**Severity**: MEDIUM -- correct implementation depends on this decision, but it is within the prompt author's discretion and does not require a task restructure.

#### Concern 2 (LOW): Component Name Sanitization -- T028

**Plan concern**: "Component name output sanitization" -- how the orchestrator handles component names that contain special characters or ambiguous content.

**T028 text**: "Author ambiguous classification handling: default to Process for uncertain DFD types, flag for human review; include AI keyword ambiguity notes (e.g., 'model' as data model vs LLM)"

**Assessment**: T028 addresses *classification* ambiguity (DFD type uncertainty, keyword ambiguity) but does not address *output sanitization* of component names. Consider: a component named `User | Admin` or `API Gateway (v2)` could break markdown table rendering. The plan's concern about "component name output sanitization" is not explicitly covered by any task.

**Concern status**: NOT ADDRESSED. No task covers sanitization of component names for safe inclusion in markdown tables. Component names from user input could contain pipe characters (`|`), which would break markdown table syntax in the output.

**Severity**: LOW -- this is an edge case that the prompt author can handle as part of output format specification (T004) or output structural validation (T024). Adding a brief note to T024's validation checklist ("verify component names are escaped for markdown table compatibility") would resolve this.

### 5. Single-File Authoring Strategy

**Verdict: TECHNICALLY SOUND**

The strategy of authoring all sections into a single `agents/orchestrator.md` file is well-justified:

- **Self-contained prompt**: The deliverable must be a single prompt file that works with any LLM platform. Splitting into multiple files would require multi-file loading, which contradicts the platform-neutrality constraint (SC-010).
- **No token limit concerns**: The plan.md explicitly notes "no token limit issues observed" for single-file approach. Given that individual agent files (e.g., `agents/stride/spoofing.md`) are already implemented as single files, scaling to an orchestrator prompt of similar or moderately larger size is reasonable.
- **Sequential authoring is natural**: The OWASP 4-step process has inherent sequential dependencies (Scope -> Determine Threats -> Countermeasures -> Assess). Authoring sections in this order maps directly to the data flow.
- **Validation-by-example is feasible**: T030-T032 validate the complete prompt against 3 example inputs. A single file simplifies this -- no assembly step is needed before testing.
- **Incremental delivery mitigates risk**: The MVP-first strategy (Phase 1-3 delivers a working parser before dispatch/assembly) means the file can be validated incrementally rather than only at the end.

**One consideration**: The Implementation Strategy section correctly notes that "sequential execution by a single agent is most practical" (line 209). This is consistent with the single-file target. However, the parallel opportunity annotations (T003/T004, T019/T020, T025-T027) are still valuable as documentation of logical independence, even if not exploited during implementation.

---

## Findings Summary

### MEDIUM Concerns (2)

| # | Finding | Task(s) | Recommendation |
|---|---------|---------|----------------|
| M-1 | Agent context payload format not specified | T014 | Add a note to T014: "Decide payload structure (inline markdown vs. structured block) during authoring. Ensure consistency with individual agent prompt input expectations." |
| M-2 | Component name output sanitization not covered | None (gap) | Add a note to T024's validation checklist: "Verify component names are escaped for markdown table compatibility (pipe characters, special characters)." Alternatively, add this to T004 (Output Format Specification). |

### LOW Concerns (1)

| # | Finding | Task(s) | Recommendation |
|---|---------|---------|----------------|
| L-1 | US5 and US6 coverage is implicit | T015, T003 | Line 149-150 notes US5 is covered within T015 and US6 within T003. This is architecturally correct but the tasks themselves (T015, T003) do not explicitly reference their user story coverage. The Dependencies section documents this mapping, which is sufficient. No action needed. |

### Positive Observations

1. **Correct phase-to-OWASP mapping**: Tasks cleanly map to OWASP phases (Scope=US1, Determine Threats=US2, Countermeasures+Assess=US3). This preserves the methodology's integrity.
2. **Independent tests per user story**: Each phase includes a concrete independent test with expected values (e.g., "5 components classified with correct DFD types"). This enables incremental validation.
3. **Intermediate output requirements**: T010 and T016 require visible intermediate artifacts (component inventory, dispatch table) before proceeding. This is good prompt engineering -- it forces the LLM to show its work before acting on it.
4. **Error handling parallelism**: T025-T027 are correctly identified as independently authorable error response sections.
5. **Polish phase is comprehensive**: T030-T035 cover example validation, platform neutrality check, interface contract compliance, and readability review. This is thorough.
6. **Task count is appropriate**: 35 tasks for a single-file deliverable with 9 prompt sections is well-granulated -- neither too coarse (missing detail) nor too fine (artificial splitting).

---

## Sign-off

**STATUS**: APPROVED_WITH_CONCERNS
**Concerns**: 2 MEDIUM, 1 LOW (all addressable during implementation)
**Blocking**: None -- no structural changes required to task breakdown
**Recommendation**: Address M-1 and M-2 by adding brief notes to T014 and T024 respectively. These can be resolved during implementation without re-review.
