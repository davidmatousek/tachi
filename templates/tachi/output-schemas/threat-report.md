# Threat Report

<!--
  Canonical output template for tachi threat report generation.

  Schema version : 1.1
  Schema file    : schemas/report.yaml
  Contract       : specs/015-threat-report-agent/spec.md

  Producers      : Report agent (agents/threat-report.md) transforming threats.md into narrative report
  Consumers      : CISOs, security engineers, project managers, compliance teams

  Every generated threat report MUST conform to this structure.
  All 7 sections are required. Sections must appear in the order listed.
-->

---

```yaml
---
schema_version: "1.1"
date: "YYYY-MM-DD"
source_file: "{path to input threats.md}"
finding_count: "{integer — total findings from threats.md Sections 3, 4, and 4a}"
risk_distribution:
  Critical: "{integer}"
  High: "{integer}"
  Medium: "{integer}"
  Low: "{integer}"
attack_tree_count: "{integer — number of attack trees generated (Critical + High findings)}"
baseline_source: "{baseline file path or null}"
baseline_date: "{ISO date of baseline run or null}"
delta_counts:
  new: "{integer or null}"
  unchanged: "{integer or null}"
  updated: "{integer or null}"
  resolved: "{integer or null}"
---
```

**Frontmatter fields:**

| Field | Type | Description |
|-------|------|-------------|
| `schema_version` | string | Report schema version. Always `"1.1"` for this release. |
| `date` | string | ISO 8601 date when the report was generated. Format: `YYYY-MM-DD`. |
| `source_file` | string | Relative path to the `threats.md` file used as input. |
| `finding_count` | integer | Total number of findings from `threats.md` Sections 3, 4, and 4a. |
| `risk_distribution` | object | Count of findings per risk level (Critical, High, Medium, Low). |
| `attack_tree_count` | integer | Number of Mermaid attack trees with actual generated content. Counts Critical and High findings with delta_status NEW or UPDATED (fresh trees). UNCHANGED findings carried forward from baseline are excluded. When no baseline, equals total Critical + High findings. |
| `baseline_source` | string, nullable | File path of the baseline used for this report's source threats.md. Null when no baseline (first run). |
| `baseline_date` | string, nullable | ISO date of the baseline run. Null when no baseline. |
| `delta_counts` | object, nullable | Lifecycle breakdown counts. All values null when no baseline. |
| `delta_counts.new` | integer, nullable | Count of findings with delta_status NEW. |
| `delta_counts.unchanged` | integer, nullable | Count of findings with delta_status UNCHANGED. |
| `delta_counts.updated` | integer, nullable | Count of findings with delta_status UPDATED. |
| `delta_counts.resolved` | integer, nullable | Count of findings with delta_status RESOLVED (from Section 4b). |

---

## 1. Executive Summary

_Overall risk posture in one sentence summarizing the security state of the analyzed system._

_Top 3-5 threats ranked by business impact (not just technical severity). For each threat, state the affected component, the business consequence, and the risk level. Note what is working well alongside the problems identified._

_Key recommendations stating what to do (not how). Focus on outcomes that a non-technical executive can authorize or prioritize._

_Compliance relevance mapping findings to applicable frameworks (SOC2 trust services criteria, ISO 27001 control domains, CWE/OWASP references). Include only where findings have direct compliance implications._

_Remediation timeline organized by priority tier:_
- _Immediate: Critical findings requiring action before deployment_
- _Short-term: High findings to address within current cycle_
- _Medium-term: Medium findings for upcoming planning_
- _Backlog: Low findings tracked for future consideration_

> **Constraints**: ~500 word maximum. No unexplained acronyms — define every acronym on first use. Written for a non-technical audience (board members, compliance officers) who may not know STRIDE methodology.

---

## 2. Architecture Overview

### System Context

_Narrative summary of the system architecture derived from threats.md Section 1 (System Overview). Describe the components, data flows, and technologies in plain language suitable for a non-technical audience. Identify the system's purpose, its primary users, and the key data it processes._

### Trust Boundary Summary

_Narrative summary of trust zones and boundary crossings derived from threats.md Section 2 (Trust Boundaries). Explain where security posture changes, which components sit inside versus outside trust boundaries, and what controls exist at each crossing. Present in narrative form — avoid raw tables in this section._

---

## 3. Threat Analysis

_Agent-by-agent narrative analysis of all findings from threats.md. Each subsection covers one STRIDE or AI threat category. For each finding, provide full reasoning explaining why the threat exists, which component is affected, and how the risk level was determined. Include finding ID references (e.g., S-1, T-2, AG-1) inline with the narrative. Progress from general category context to specific finding details._

### 3.1 Spoofing

_Narrative analysis of all Spoofing findings (S-prefixed IDs) from threats.md Section 3.1. For each finding, explain the attack scenario, affected component, and business impact in context._

### 3.2 Tampering

_Narrative analysis of all Tampering findings (T-prefixed IDs) from threats.md Section 3.2._

### 3.3 Repudiation

_Narrative analysis of all Repudiation findings (R-prefixed IDs) from threats.md Section 3.3._

### 3.4 Information Disclosure

_Narrative analysis of all Information Disclosure findings (I-prefixed IDs) from threats.md Section 3.4._

### 3.5 Denial of Service

_Narrative analysis of all Denial of Service findings (D-prefixed IDs) from threats.md Section 3.5._

### 3.6 Elevation of Privilege

_Narrative analysis of all Elevation of Privilege findings (E-prefixed IDs) from threats.md Section 3.6._

### 3.7 Agentic Threats

_Narrative analysis of all Agentic Threat findings (AG-prefixed IDs) from threats.md Section 4.1._

### 3.8 LLM Threats

_Narrative analysis of all LLM Threat findings (LLM-prefixed IDs) from threats.md Section 4.2._

> **Guidance**: When threats.md contains more than 30 findings, summarize Medium and Low findings by category rather than providing individual narrative for each. Critical and High findings always receive full individual narrative treatment regardless of total count.

---

## 4. Cross-Cutting Themes

_Identify and describe patterns that emerge across multiple findings from different agents. Each theme represents a systemic issue affecting the overall security posture rather than an isolated vulnerability._

_Each theme MUST cite contributing finding IDs and explain how the findings relate to form the pattern._

**Detection criteria** (apply all four):

- **(a) Same component targeted by multiple agents**: _Findings from different STRIDE/AI categories that all affect the same component, indicating a concentration of risk._
- **(b) Similar mitigations across categories**: _Findings from different categories that recommend overlapping or identical countermeasures, suggesting a shared root cause._
- **(c) Attack chains**: _Findings where one finding's impact enables another finding's precondition, creating a multi-step attack path._
- **(d) Component clusters with high finding counts**: _Components with disproportionately high finding counts relative to other components in the Coverage Matrix._

_When no cross-cutting themes are detected:_

> No cross-cutting themes identified. All findings represent independent threats without shared patterns across agent categories.

---

## 5. Attack Trees

_Mermaid `flowchart TD` attack trees for every Critical and High finding. Each tree visualizes the attacker's goal, decomposition into sub-goals with AND/OR gate logic, and leaf nodes representing concrete atomic attack actions._

_Each tree is presented under a heading with the finding ID, embedded as a fenced Mermaid code block. Trees are also saved as standalone files in `attack-trees/{finding-id}-attack-tree.md`._

### _{Finding-ID}_: _{Finding threat description}_

```mermaid
flowchart TD
    %% Attack tree for {Finding-ID}
    %% Root: Attacker goal derived from finding threat field
    %% Intermediate: Sub-goals with AND/OR gate decomposition
    %% Leaves: Concrete atomic attack actions

    {FindingID}_root["Attacker Goal"]
    {FindingID}_or1{{"OR"}}
    {FindingID}_sub1["Sub-goal 1"]
    {FindingID}_sub2["Sub-goal 2"]
    {FindingID}_leaf1["Atomic Action 1"]
    {FindingID}_leaf2["Atomic Action 2"]
    {FindingID}_leaf3["Atomic Action 3"]

    {FindingID}_root --> {FindingID}_or1
    {FindingID}_or1 --> {FindingID}_sub1
    {FindingID}_or1 --> {FindingID}_sub2
    {FindingID}_sub1 --> {FindingID}_leaf1
    {FindingID}_sub2 --> {FindingID}_leaf2
    {FindingID}_sub2 --> {FindingID}_leaf3

    classDef goal fill:#ff6b6b,stroke:#333,stroke-width:2px,color:#fff
    classDef andGate fill:#ffa500,stroke:#333,stroke-width:2px,color:#fff
    classDef orGate fill:#4ecdc4,stroke:#333,stroke-width:2px,color:#fff
    classDef leaf fill:#95e1d3,stroke:#333,stroke-width:2px,color:#333

    class {FindingID}_root goal
    class {FindingID}_or1 orGate
    class {FindingID}_sub1,{FindingID}_sub2 orGate
    class {FindingID}_leaf1,{FindingID}_leaf2,{FindingID}_leaf3 leaf
```

> **Conventions**: Node IDs use `{FindingID}_{type}{N}` format (e.g., `AG1_root`, `AG1_or1`, `AG1_leaf1`). All labels are quoted. Gate nodes use diamond `{{"AND"}}` or hexagon `{{"OR"}}` shapes. Styling via `classDef`: goal=red, andGate=orange, orGate=teal, leaf=green. Maximum ~20 nodes per tree. Never use reserved words (`end`, `default`) as bare node IDs.
>
> **Depth requirements**: Critical findings require minimum 3 levels (root, intermediate, leaf). High findings require minimum 2 levels (root, leaf).
>
> **Correlated findings**: Each correlated finding receives its own individual tree with a cross-reference note to related finding IDs — not a single unified tree for the correlation group.
>
> **Baseline handling** (three-rule approach):
>
> **Rule 1 — All UNCHANGED (no architecture change):** When `delta_counts` shows zero NEW, zero UPDATED, and zero RESOLVED findings, the architecture has not changed. For each UNCHANGED Critical/High finding, copy the full Mermaid attack tree content from the baseline's `attack-trees/{finding-id}-attack-tree.md` file. Derive the baseline directory from the `baseline.source` frontmatter field by dropping the `threats.md` filename. Include the complete Mermaid code block — do NOT output placeholder text without the actual diagram. If the baseline file is missing, generate a fresh tree as fallback.
>
> **Rule 2 — Any NEW/UPDATED/RESOLVED (architecture changed):** When `delta_counts` shows any non-zero value for `new`, `updated`, or `resolved`, the architecture has shifted and attack paths to all threats may have changed. Generate fresh attack trees for ALL Critical/High findings — including UNCHANGED ones — following all standard conventions above. For NEW findings, generate normally. For UPDATED findings, add a note below the tree: _"Context changed since baseline ({baseline_date}) — attack tree regenerated."_
>
> **Rule 3 — Post-generation reconciliation (applies only when Rule 2 fires):** After generating all fresh trees, compare each UNCHANGED finding's fresh tree against its baseline counterpart from `attack-trees/{finding-id}-attack-tree.md`. If they are structurally similar (same nodes, same paths, minor wording differences only), use the baseline version for consistency — this avoids noisy churn on trees that didn't actually change. If they are materially different (new attack paths, removed nodes, structural changes), use the fresh version. This ensures diffs between runs only show meaningful changes.
>
> **RESOLVED**: Not applicable — RESOLVED findings do not appear in Section 5. They appear only in Section 4b of the input threats.md.
>
> **No baseline**: When `baseline_source` is null in the input frontmatter, generate all attack trees fresh with no delta annotations. This is standard first-run behavior.

_When no Critical or High findings exist:_

> No Critical or High findings identified. Attack trees are generated only for Critical and High severity findings.

---

## 6. Cross-Layer Attack Chains

_Present only when the orchestrator produced an `attack-chains.md` artifact (i.e., `has-attack-chains` is true). When no attack chains exist, omit this entire section — the report proceeds directly from Section 5 to Section 7._

_For each surfaced chain (Critical/High maximum severity, top 5 by ranking):_

### _{CHAIN-ID}_: _{Chain title}_

**Layers**: _{L2 → L3 → L7}_ | **Max Severity**: _{Critical/High}_ | **Findings**: _{count}_

_150-300 word narrative walkthrough covering:_
- _Initial exploit at the source MAESTRO layer_
- _Intermediate cascades using canonical CSA causal vocabulary ("enables," "triggers," "shifts," "manifests as")_
- _Terminal business impact_

**Chain-Breaking Control**: _{Target finding ID at layer LN. Structural rationale. Control recommendation.}_

> _Disclaimer: Chain-breaking controls are structurally derived from graph centrality analysis and should be validated against the specific deployment context._

**Impacted Findings**: _{Finding IDs with MAESTRO layers and roles (initial exploit, intermediate cascade, terminal impact)}_

> **Constraints**: Each chain narrative MUST be 150-300 words. Use canonical CSA MAESTRO causal vocabulary for all layer transitions. Chains ordered by maximum severity (Critical first), then chain length (longer first), then chain ID (alphabetical).

---

## 7. Remediation Roadmap

_Prioritized table of all findings ordered by risk level (Critical first, then High, Medium, Low). Within the same risk level, items are grouped by component. Each item is directly convertible to a development task or backlog item._

| Finding ID | Component | Mitigation | Effort | Dependencies |
|------------|-----------|------------|--------|--------------|
| _{finding-id}_ | _{component}_ | _{mitigation text preserving original from threats.md}_ | _{Low \| Medium \| High}_ | _{dependency notes or "None"}_ |

**Priority tiers:**

| Risk Level | Priority Tier | Timeline |
|------------|---------------|----------|
| Critical | Immediate | Before deployment |
| High | Short-term | Current development cycle |
| Medium | Medium-term | Upcoming planning cycle |
| Low | Backlog | Future consideration |

**Effort scale:**

| Effort | Description |
|--------|-------------|
| Low | Single-component change, well-understood fix, minimal testing |
| Medium | Multi-component coordination, moderate complexity, standard testing |
| High | Architectural change, cross-system impact, extensive testing required |

> **Correlation groups**: Correlated findings from threats.md Section 4a are consolidated into a single roadmap item using the primary finding ID. The mitigation notes the correlation scope and lists contributing finding IDs.

---

## 8. Appendix: Finding Reference

_Complete mapping table from report sections back to original finding IDs in threats.md. Every finding ID from threats.md Sections 3, 4, and 4a MUST appear in this table — zero finding loss._

| Finding ID | Report Section | Heading Reference |
|------------|----------------|-------------------|
| _{finding-id}_ | _{section number where finding is discussed}_ | _{heading text of the subsection containing the finding}_ |

> **Completeness rule**: Cross-check this table against threats.md Sections 3 (STRIDE Tables), 4 (AI Threat Tables), and 4a (Correlated Findings). Every finding ID in the input must have a row in this table. Missing findings indicate a generation error that must be corrected before the report is considered complete.

---

## 9. Delta Summary

_Present only when the input threats.md contains baseline data (i.e., `baseline.source` is non-null in frontmatter). Omit this entire section on first run (no baseline)._

This section provides a narrative summary of how the threat landscape has evolved since the baseline assessment. It complements the per-finding delta annotations in Sections 3 and 5 with an aggregate view.

### Finding Lifecycle Breakdown

_Table summarizing finding counts by lifecycle status._

| Status | Count | Description |
|--------|-------|-------------|
| NEW | _{count}_ | Findings discovered in this run with no baseline match |
| UNCHANGED | _{count}_ | Findings identical to baseline (same component, threat, assessment) |
| UPDATED | _{count}_ | Findings with changed context since baseline |
| RESOLVED | _{count}_ | Baseline findings no longer applicable (from Section 4b) |
| **Total** | _{total}_ | Sum of all findings (active + resolved) |

### Remediation Progress

_Narrative paragraph describing remediation progress since the baseline. Reference RESOLVED findings from Section 4b by ID and resolution reason. Quantify the reduction in active threats. Note any risk level changes in UPDATED findings. Written for a non-technical audience._

### Baseline Reference

| Field | Value |
|-------|-------|
| Source | _{baseline file path from frontmatter}_ |
| Date | _{baseline date from frontmatter}_ |
| Baseline Findings | _{baseline finding count from frontmatter}_ |
| Run ID | _{baseline run ID from frontmatter}_ |

> **Generation guidance**: Delta counts are computed from the input threats.md: count findings by `delta_status` in Sections 3 and 4, plus RESOLVED findings from Section 4b. The sum of NEW + UNCHANGED + UPDATED + RESOLVED must equal the total. When generating the remediation progress narrative, cite specific resolved findings and their resolution reasons to provide concrete remediation proof.
