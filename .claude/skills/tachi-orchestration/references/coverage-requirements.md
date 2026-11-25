---
source_agent: orchestrator
extracted_from: .claude/agents/tachi/orchestrator.md
version: 1.0.0
---

# Coverage Requirements Reference

The coverage gate verifies that all required threat categories have been evaluated for each component type in the architecture. It determines each component's type (including AI subtype detection), checks the current finding set for coverage gaps, and dispatches targeted re-analysis for any missing component-category pairs.

The coverage gate runs in **both baseline and stateless modes**. Its purpose is to prevent blind spots caused by LLM non-determinism -- ensuring that required threat categories are always analyzed regardless of whether a baseline exists.

---

## Step 1: Component Type Determination

For each component in the Phase 1 inventory, determine its coverage checklist type using a two-stage classification:

### AI Subtype Detection (check first)

Scan the component's name and description for AI subtype keywords. Matching is **case-insensitive** and checks for **substring presence** (e.g., "LLM Agent Orchestrator" matches keyword `llm`).

**LLM Process**: Keywords -- `llm`, `language model`, `gpt`, `claude`, `ai model`, `inference`.

**MCP Server**: Keywords -- `mcp`, `model context protocol`, `tool server`, `plugin host`.

### Standard DFD Type (fallback)

If no AI subtype keywords match, use the component's DFD element type from Phase 1 classification:

| DFD Element Type | Coverage Type |
|------------------|---------------|
| External Entity | `external_entity` |
| Process | `process` |
| Data Store | `data_store` |
| Data Flow | `data_flow` |

**AI subtype takes precedence**: A Process component matching LLM keywords is classified as `llm_process`, not `process`. This ensures AI-specific categories (`llm`, `agentic`) are included in the required set.

---

## Step 2: Required Categories per Component Type

For each component, look up the required categories based on its determined type:

| Component Type | Required Categories |
|----------------|---------------------|
| `external_entity` | spoofing, repudiation |
| `process` | spoofing, tampering, repudiation, info-disclosure, denial-of-service, privilege-escalation |
| `data_store` | tampering, info-disclosure, denial-of-service |
| `data_flow` | tampering, info-disclosure, denial-of-service |
| `llm_process` | spoofing, tampering, repudiation, info-disclosure, denial-of-service, privilege-escalation, llm |
| `mcp_server` | spoofing, tampering, repudiation, info-disclosure, denial-of-service, privilege-escalation, agentic |

**Source**: These required categories are loaded from `schemas/coverage-checklists.yaml` at runtime. The table above is a reference summary.

---

## Step 3: Coverage Evaluation

For each component, check whether the current finding set contains at least one finding for each required category.

### Current Finding Set Definition

- **Baseline mode**: The merged finding set from Phase 3a (carry-forward + new discoveries). Exclude `RESOLVED` findings -- they represent addressed threats, not current coverage.
- **Stateless mode**: All Phase 2 agent findings.

### Finding ID Prefix to Coverage Category Mapping

Map finding categories to coverage checklist categories using the finding ID prefix:

| Finding ID Prefix | Coverage Category |
|-------------------|-------------------|
| S-* | spoofing |
| T-* | tampering |
| R-* | repudiation |
| I-* | info-disclosure |
| D-* | denial-of-service |
| E-* | privilege-escalation |
| AG-* | agentic |
| LLM-* | llm |

### Evaluation per Component-Category Pair

- **Covered**: At least one active finding exists targeting this component with a matching category. No action needed.
- **Gap**: No active finding exists targeting this component with this required category. Add to the gap list.

---

## Step 4: Gap Assessment

After evaluating all component-category pairs, determine the coverage gate result:

### Pass (no gaps)

All required categories are covered for every component. The coverage gate passes silently -- no additional analysis is needed.

```yaml
coverage_gate:
  status: "pass"
  gaps: []
```

### Gaps Detected

One or more required categories are missing for one or more components.

```yaml
coverage_gate:
  status: "warn"
  gaps:
    - { component: "API Gateway", missing_category: "repudiation" }
    - { component: "User DB", missing_category: "denial-of-service" }
```

### Coverage Gate Intermediate Summary Format

```
Coverage Gate:
  Components evaluated: {count}
  Required pairs: {total component-category pairs}
  Covered: {covered count}
  Gaps: {gap count}
  Status: {pass | warn -- {gap count} gap(s) detected}
```

If gaps are detected, list each gap:

```
  Gaps:
    - {component}: {missing_category}
    - {component}: {missing_category}
```

---

## Step 5: Targeted Re-Analysis (Gaps Only)

**Skip this step if the coverage gate passed (no gaps).** Proceed directly to Risk Level Validation.

For each gap in the gap list, dispatch the specific threat agent(s) for the missing category, targeting only the uncovered component.

### Category-to-Agent Mapping

| Missing Category | Agent(s) to Dispatch |
|------------------|----------------------|
| spoofing | tachi-spoofing |
| tampering | tachi-tampering |
| repudiation | tachi-repudiation |
| info-disclosure | tachi-info-disclosure |
| denial-of-service | tachi-denial-of-service |
| privilege-escalation | tachi-privilege-escalation |
| agentic | tachi-tool-abuse, tachi-agent-autonomy, tachi-human-trust-exploitation |
| llm | tachi-prompt-injection, tachi-data-poisoning, tachi-model-theft, tachi-output-integrity, tachi-misinformation |

Each name is the typed `subagent_type` of a roster agent. Dispatch by that name, with no stand-in. The canonical roster is `.claude/skills/tachi-shared/references/agent-roster-shared.md`, and it governs if the two differ.

For compound categories (`agentic`, `llm`), dispatch **all** listed agents. Findings from any of the listed agents satisfy the coverage requirement.

### Re-Analysis Dispatch

Each targeted re-analysis is a dispatch of its own, made under the orchestrator's Dispatch Protocol, with the templates in `.claude/skills/tachi-shared/references/dispatch-record-brief-shared.md`. This reference sets no payload of its own:

1. **One dispatch for each gap and agent.** A compound category (`agentic`, `llm`) gives one dispatch for each listed agent.
2. **The next unused dispatch ID**, taken when you decide to make the dispatch, before you write its brief.
3. **A brief** (`tachi.brief/1`) whose one target is the gap's component. It points at the architecture snapshot and the two Phase 1 files, and copies none of them. In baseline mode its `baseline_focus` keeps the **isolated discovery** rule of Phase 2: the coverage summary only, with no finding descriptions, scores, mitigations or finding IDs, to prevent anchoring bias.
4. **The fixed prompt, and nothing else**: `Read and follow the brief at {brief_path}.`
5. **One record**, with `origin` `coverage-gap`, `supersedes` `null` and a scope of exactly the gap's component.

### Re-Analysis Result Handling

The dispatch's record decides the outcome, and the end-marker rule in the dispatch record and brief reference reads the return.

| Outcome | Action |
|---------|--------|
| Findings produced (a `complete` record whose `count` is above 0) | Merge the new findings into the finding set, and set `delta_status` to `NEW`. Their IDs follow Phase 3's numbering and are recorded in the ID map: this reference sets no ID rule of its own. |
| No findings produced (a `complete` record whose `count` is 0) | The category was analyzed but no threats were found. Gap resolved as `"analyzed_clean"`. |
| Truncated return (an `unrecovered` record, with `reason` `no_end_marker`, `overflow_error`, `agent_failed` or `timed_out`) | The findings are dropped, even those the return held. Gap unresolved with resolution `"dispatch_failure"`. Coverage gate reports as warning -- does not block pipeline. The run's check then warns `coverage-gap:unrecovered:<reason>`, with exit 5. |

An agent that can't be spawned is not a row of this table: it is the stop of typed dispatch rule 2 in the orchestrator, and it ends the run.

### Re-Analysis Constraints

- **Run once per gap**: Each gap gets exactly one re-analysis attempt. No retry loops.
- **No recursive coverage checks**: Do not re-run the coverage gate after re-analysis. The gate runs once, dispatches once, and reports results.
- **Non-blocking**: The coverage gate produces warnings, not errors. The pipeline always continues to Risk Level Validation regardless of gap resolution outcomes.
- **No lineage**: A re-analysis dispatch belongs to no lineage, is never `superseded` and is never re-dispatched. The dispatches run in waves of at most 16, and each wave starts its own watch with its Agent calls, as Phase 2's waves do.

### Updated Coverage Gate Output

After re-analysis completes, update the coverage gate result:

```
Coverage Gate (after re-analysis):
  Gaps resolved (findings produced): {count}
  Gaps resolved (analyzed but clean): {count}
  Gaps unresolved (dispatch failure): {count}
  Final status: {pass | warn}
```

The `coverage_gate` frontmatter fields reflect the final state:

```yaml
coverage_gate:
  status: "pass"  # or "warn" if dispatch failures remain
  gaps:
    - { component: "API Gateway", missing_category: "repudiation", resolution: "findings_produced" }
    - { component: "User DB", missing_category: "denial-of-service", resolution: "analyzed_clean" }
```

Resolution values: `"findings_produced"`, `"analyzed_clean"`, `"dispatch_failure"`.
