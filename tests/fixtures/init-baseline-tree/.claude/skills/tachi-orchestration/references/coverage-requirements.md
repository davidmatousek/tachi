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
| agentic | tachi-tool-abuse, tachi-agent-autonomy |
| llm | tachi-prompt-injection, tachi-data-poisoning, tachi-model-theft |

For compound categories (`agentic`, `llm`), dispatch **all** listed agents. Findings from any of the listed agents satisfy the coverage requirement.

### Re-Analysis Context Payload

Each targeted re-analysis agent receives the same context payload structure as Phase 2, but scoped to a single component:

1. **Target component**: The specific component with the coverage gap.
2. **Full architecture context**: All components, data flows, trust boundaries (same as Phase 2).
3. **Analysis scope**: The missing threat category.
4. **Scope constraint**: `"Targeted re-analysis for coverage gap: analyze {component} for {category} threats only."`

When in baseline mode, the re-analysis uses the same **isolated discovery context** rules as Phase 2 -- no finding descriptions, scores, or mitigations are provided. Only the coverage summary is included to prevent anchoring bias.

### Re-Analysis Result Handling

| Outcome | Action |
|---------|--------|
| Findings produced | Merge new findings into the finding set. Assign sequential IDs after the highest existing ID in the category. Set `delta_status` to `NEW`. |
| No findings produced | The category was analyzed but no threats were found. Gap resolved as `"analyzed_clean"`. |
| Agent dispatch failure | Gap unresolved with resolution `"dispatch_failure"`. Coverage gate reports as warning -- does not block pipeline. |

### Re-Analysis Constraints

- **Run once per gap**: Each gap gets exactly one re-analysis attempt. No retry loops.
- **No recursive coverage checks**: Do not re-run the coverage gate after re-analysis. The gate runs once, dispatches once, and reports results.
- **Non-blocking**: The coverage gate produces warnings, not errors. The pipeline always continues to Risk Level Validation regardless of gap resolution outcomes.

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
