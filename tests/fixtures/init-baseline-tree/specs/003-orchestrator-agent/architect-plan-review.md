# Architect Review: plan.md (Feature 003 - Orchestrator Agent)

**Reviewer**: architect
**Date**: 2026-03-21
**Artifact**: `specs/003-orchestrator-agent/plan.md`
**Cross-references reviewed**: spec.md, PRD 003, INTERFACE-CONTRACT.md, templates/threats.md, schemas/finding.yaml, schemas/output.yaml, schemas/input.yaml, agents/ai/README.md, agents/orchestrator.md (placeholder), .aod/memory/constitution.md, examples/mermaid-agentic-app/input.md

---

## Review Summary

The plan is architecturally sound. It correctly translates the spec into an implementable design for a single-file orchestrator prompt. The OWASP 4-step phase mapping, dispatch rule embedding, data flow diagram, and knowledge system alignment are all well-executed. Two concerns warrant attention but are non-blocking.

**Verdict**: APPROVED_WITH_CONCERNS (2 concerns, 0 blockers)

---

## Evaluation by Review Criteria

### 1. Prompt Architecture Soundness (Single File, OWASP 4-Step)

**Rating**: SOUND

The plan's Component 1 table (lines 90-100) maps prompt sections to OWASP phases correctly:

| Plan Section | OWASP Phase | Assessment |
|---|---|---|
| Phase 1: Scope | Scope | Correct -- covers format detection, component extraction, DFD classification, trust boundary identification, System Overview assembly |
| Phase 2: Determine Threats | Determine Threats | Correct -- covers STRIDE-per-Element normalization, AI keyword dispatch, agent invocation protocol |
| Phase 3: Determine Countermeasures | Determine Countermeasures | Correct -- covers finding collection, risk_level validation, table assembly |
| Phase 4: Assess | Assess | Correct -- covers coverage matrix, risk summary, recommended actions |

The single-file decision (Key Design Decisions table) is appropriate for this deliverable. The rationale is valid: no token limit issues have been observed with the existing 11 agent files (5-10KB each), and single-file avoids multi-file coordination complexity. The contingency (split into phased prompts if needed) is documented.

The supplementary sections (Frontmatter, Role & Purpose, Input Sanitization Boundary, Error Handling, Output Validation) correctly bracket the OWASP phases with necessary metadata and safety controls.

### 2. Dispatch Rules Correctness (STRIDE-per-Element + AI Keywords)

**Rating**: SOUND

The data flow diagram (lines 128-134) correctly represents the STRIDE-per-Element dispatch:

- External Entity -> S, R (matches INTERFACE-CONTRACT.md Section 2)
- Process -> S, T, R, I, D, E (matches)
- Data Store -> T, I, D (matches)
- Data Flow -> T, I, D (matches)

AI keyword dispatch (lines 135-138) correctly represents the four dispatch outcomes:

- LLM keywords -> prompt-injection, data-poisoning, model-theft (matches INTERFACE-CONTRACT.md Section 3)
- AG keywords -> agent-autonomy, tool-abuse (matches)
- Both -> Dual-dispatch (matches)
- None -> STRIDE only (matches)

The plan correctly states that AI dispatch is additive to STRIDE (not replacing it), which aligns with the interface contract Section 3 ("AI dispatch is additive").

Keyword lists are not enumerated in the plan body, but the plan references the interface contract as the source. The spec (FR-006) enumerates them explicitly. This is acceptable -- the plan delegates to the authoritative source rather than duplicating.

### 3. Data Flow Diagram Accuracy and Completeness

**Rating**: SOUND WITH ONE MINOR OBSERVATION

The Mermaid flowchart (lines 120-150) accurately represents the end-to-end data flow:

- Input -> Format Detection (auto vs explicit) -> Component Extraction -> Trust Boundary Identification -> System Overview -- correctly models Phase 1
- System Overview -> STRIDE dispatch -> AI keyword dispatch -> Agent Invocation -> Finding Collection -- correctly models Phase 2 and 3
- Finding Collection -> Tables -> Coverage Matrix -> Risk Summary -> Recommended Actions -> Output -- correctly models Phase 4
- Error paths (NO_COMPONENTS, UNSUPPORTED_FORMAT, INVALID_FORMAT_VALUE) are correctly branched

**Minor observation**: The diagram shows STRIDE dispatch feeding into AI keyword dispatch sequentially (H -> I/J/K/L -> M), which is the correct logical flow (STRIDE categories are determined first, then AI categories are added). However, in the actual prompt execution, both determinations happen per-component before dispatch. The diagram represents the logical decision flow, not the execution order. This is acceptable for a plan-level diagram but the implementation should ensure both dispatch decisions are resolved per-component before any agent invocation begins.

### 4. Validation Plan Coverage

**Rating**: ADEQUATE

The validation plan (lines 185-193) covers 7 test scenarios across the critical paths:

| Critical Path | Covered By | Assessment |
|---|---|---|
| Format detection (3 formats) | Mermaid parsing, ASCII parsing, Free-text parsing | All 3 example inputs used |
| DFD classification | Mermaid parsing (5 components, correct types) | Primary validation input used |
| STRIDE dispatch correctness | Mermaid parsing (SC-001-SC-004) | Correct -- verifies per-element dispatch |
| AI dual-dispatch | Mermaid parsing ("LLM Agent Orchestrator") | Correct -- verifies both LLM+AG |
| Output structure | "Any example -> full run" | Correct -- verifies 7 sections, frontmatter, finding IDs |
| Error handling (2 scenarios) | Empty input, bad format value | Covers NO_COMPONENTS and INVALID_FORMAT_VALUE |
| Platform neutrality | Read prompt file | Correct -- grep for platform-specific syntax |

**Gap noted**: UNSUPPORTED_FORMAT error is listed in the Error Handling section of the component table (line 99) but not explicitly tested in the validation plan. The "Error: bad format" test covers INVALID_FORMAT_VALUE (explicit invalid enum value), but there is no test for auto-detection failure (e.g., providing XML content with `format: auto`). This is low-risk since the three example inputs cover the three most common format detection paths, but adding a test for auto-detection failure would be more thorough.

### 5. Design Decisions Technical Appropriateness

**Rating**: SOUND

All five design decisions in the Key Design Decisions table (lines 174-181) are technically appropriate:

1. **Single file vs. split prompts**: Correct for a knowledge system deliverable. Split prompts would introduce coordination overhead with no demonstrated benefit. Token budget is not a constraint given the scope.

2. **Embedded vs. referenced dispatch rules**: Correct. A prompt must be self-contained at invocation time. External references would require multi-file loading, violating the platform-neutrality constraint. The dispatch rules from the interface contract are small enough to embed without token concerns.

3. **Parallel + sequential dispatch documentation**: Correct. Platform neutrality requires documenting both modes. The plan correctly defers platform-specific implementation to F-009.

4. **XML-style input boundary markers (`<architecture-input>`)**: Correct. This is an established prompt engineering pattern for separating instructions from data. Markdown headers would risk confusion with architecture content, as noted. The choice aligns with INTERFACE-CONTRACT.md Section 6 guidance.

5. **Process as default for ambiguous classification**: Correct. Process receives all 6 STRIDE categories (S,T,R,I,D,E), providing maximum threat coverage for uncertain components. The alternative (reject ambiguous) would create coverage gaps. The plan correctly specifies flagging for human review alongside the default.

### 6. Knowledge System Convention Alignment

**Rating**: ALIGNED

The plan adheres to knowledge system conventions:

- **Markdown, no runtime code**: The sole deliverable is `agents/orchestrator.md`. No scripts, no compiled code, no package dependencies. This is stated in Technical Context (line 17) and confirmed in the Tech Stack table.
- **Hub-and-spoke model**: The orchestrator consumes immutable F-001 artifacts (interface contract, schemas, templates, examples) as hub content and produces output conforming to the template. The Reference Artifacts table (Component 2, lines 102-117) correctly documents this read-only relationship.
- **Content-as-data**: Architecture input is treated as data with XML boundary markers. This aligns with the `_Global/` immutability principle adapted to the threat modeling domain.
- **No build-time/run-time conflation**: The plan correctly distinguishes between the orchestrator prompt file (a knowledge system artifact authored during build-time) and its execution by an LLM (run-time). F-009 adapters handle the run-time platform specifics.
- **File naming**: The deliverable (`agents/orchestrator.md`) follows the existing kebab-case convention established in F-001.

### 7. PRD Architect Concerns Addressed

**Rating**: PARTIALLY ADDRESSED (see Concern 1)

The PRD architect sign-off raised 2 medium concerns:

#### Concern A: FR-5 Agent Communication Mechanism

**PRD concern**: "FR-5 agent communication mechanism" -- how does the orchestrator actually communicate with threat agents?

**Plan response**: The plan addresses this in Component 1's Phase 2 description (line 96): "agent invocation protocol (parallel + sequential)" and in the Key Design Decisions table: "Both documented -- Platform neutrality constraint." The spec (FR-008) specifies "the orchestrator MUST send each dispatched agent the full parsed architecture context" and the plan's data flow diagram shows "Agent Invocation with Full Context" (line 139).

**Assessment**: The plan defines WHAT context agents receive (full parsed architecture) and documents BOTH invocation modes (parallel, sequential). However, the plan does not specify the exact format of the context payload sent to agents. This is Concern 1 below.

#### Concern B: Component Name Sanitization

**PRD concern**: Component name sanitization -- how are component names from user input handled?

**Plan response**: The plan addresses input sanitization broadly via the "Input Sanitization Boundary" section in Component 1 (line 94) and the XML boundary marker design decision. The spec addresses component name handling in Edge Cases (line 140): "What happens when a component name contains a keyword substring (e.g., 'ModelValidator' contains 'model')? Case-insensitive keyword matching applies."

**Assessment**: Input sanitization boundary (treating architecture input as data) is well-addressed. However, component name sanitization for OUTPUT is not explicitly addressed. Component names extracted from user input appear verbatim in the output tables (threats.md). If a component name contains markdown table-breaking characters (e.g., `|`, newlines), the output structure could be corrupted. This is Concern 2 below.

---

## Concerns

### Concern 1 (MEDIUM): Agent Context Payload Format Not Specified

**What**: The plan says agents receive "full parsed architecture context" but does not define the structure of this context payload. What exactly does an agent receive?

**Why it matters**: The 11 agent files (6 STRIDE + 5 AI) are already implemented (5-10KB each). They expect input in a specific format. If the orchestrator sends context in a format that doesn't match what the agents expect, dispatch will silently fail or produce malformed findings. The plan needs to ensure the orchestrator's outbound context format matches the agents' expected input format.

**Evidence**: The spec's FR-008 says "the orchestrator MUST send each dispatched agent the full parsed architecture context (all components, data flows, trust boundaries), not just the individual target component." But neither the plan nor spec specifies the serialization format of this context.

**Recommendation**: During implementation, review the existing agent files' input expectations (they have been implemented, not stubs -- confirmed by file sizes of 5-10KB) and ensure the orchestrator's agent invocation section documents the exact context format. This can be addressed during implementation without changing the plan structure. The plan should note in the implementation approach that agent input format compatibility verification is part of the authoring process.

**Severity**: MEDIUM -- addressable during implementation. Does not require plan revision.

### Concern 2 (LOW): Component Name Output Sanitization Not Addressed

**What**: Component names extracted from user-provided architecture input appear verbatim in output markdown tables. Names containing markdown-special characters (`|`, backticks, newlines) could break table structure.

**Why it matters**: The output template (`templates/threats.md`) uses markdown tables extensively. A component named `Auth | Gateway` would break every table row it appears in. This is a structural integrity concern -- the plan's Output Validation section (line 100) mentions "structural integrity check" but does not cover component name sanitization specifically.

**Evidence**: The spec edge cases (lines 138-142) address keyword matching edge cases but not output formatting edge cases. The interface contract Section 6 covers input sanitization (treating input as data) but not output sanitization (ensuring extracted names don't break output format).

**Recommendation**: Add a brief note to the implementation approach or the Phase 1 (Scope) section instructing the orchestrator to sanitize component names for markdown table compatibility (e.g., escape `|` characters, strip newlines) after extraction. This is a single-line addition to the prompt.

**Severity**: LOW -- unlikely in practice (most architecture diagrams use clean component names) but worth documenting for robustness.

---

## Observations (Informational, Non-Blocking)

### Observation 1: Agent Status Discrepancy Between PRD and Plan

The PRD FR-9 describes agents as "placeholders (status: placeholder)" and requires the orchestrator to "work with the current agent files delivered in F-001" which are "stubs." However, the plan's research phase (research.md line 11) correctly notes agents are "All implemented (~100+ lines each)" and the plan itself says "11 implemented agent prompts" (line 13). Codebase verification confirms agents are fully implemented (5-10KB each), not stubs.

The plan correctly reflects reality. The PRD's FR-9 stub compatibility requirement is based on outdated information -- the agents were implemented during F-001, not left as stubs. This has no impact on the plan since a prompt that works with implemented agents will also work with stubs (the output structure is the same; stubs just produce fewer findings).

### Observation 2: UNSUPPORTED_FORMAT Validation Gap

The validation plan includes tests for NO_COMPONENTS and INVALID_FORMAT_VALUE errors but does not include an explicit test for UNSUPPORTED_FORMAT via auto-detection failure. The Component 1 table lists this error condition. Consider adding a validation scenario: provide non-architecture content (e.g., a recipe) with `format: auto` and verify the UNSUPPORTED_FORMAT error is returned. This is low-priority since format detection failure is the least likely error path given the heuristic priority order (free-text as Priority 2 will match most inputs that aren't diagram formats).

### Observation 3: Coverage Matrix Cell Semantics

The plan's data flow diagram shows finding collection followed by "STRIDE Tables 6 + AI Tables 2" followed by "Coverage Matrix." The coverage matrix uses two cell values: a number (findings found) and `-` (analyzed, no threats found). The plan should ensure the orchestrator distinguishes between `-` (component was analyzed for this category, no threats found) and blank/N/A (component was not dispatched for this category per STRIDE-per-Element rules). The spec (US-4, scenario 7) covers the `-` case, and the coverage matrix template in threats.md documents this convention. The plan inherits this correctly.

---

## Constitution Compliance

The plan's Constitution Check table (lines 26-39) correctly assesses all 11 principles. Verified assessments:

- **Principle I (General-Purpose)**: PASS confirmed -- orchestrator is domain-agnostic (works with any architecture input)
- **Principle V (Privacy)**: PASS confirmed -- output marked confidential, input sanitization boundary enforced
- **Principle VI (Testing)**: PASS confirmed -- validation-by-example with 3 inputs is appropriate for a knowledge system (no compiled code to unit test)
- **Principle VII (Definition of Done)**: PASS confirmed -- DoD aligns with PRD Definition of Done (merged via PR, validated with examples, user-validated with mermaid example)
- **Principle IX (Git Workflow)**: PASS confirmed -- feature branch `003-orchestrator-agent` required

---

## Sign-Off

**Status**: APPROVED_WITH_CONCERNS
**Concerns**: 2 (1 MEDIUM, 1 LOW) -- both addressable during implementation
**Blockers**: 0

The plan is technically sound and ready for task breakdown. The two concerns (agent context payload format, component name output sanitization) can be resolved during prompt authoring without requiring plan revision.

**Signed**: architect | 2026-03-21
