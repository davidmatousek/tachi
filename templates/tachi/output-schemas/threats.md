# Threat Model Report

<!--
  Canonical output template for tachi threat model reports.

  Schema version : 1.2
  Schema file    : schemas/output.yaml
  Contract       : specs/001-project-skeleton-interface/contracts/output-schema.md

  Producers      : Template engine (applying IR findings to output template)
  Consumers      : Integrators, SARIF export (F-006), downstream features

  Every generated threat model output MUST conform to this structure.
  All 7 sections plus Section 4a are required. Sections must appear in the order listed.
-->

---

```yaml
---
schema_version: "1.3"
date: "YYYY-MM-DD"
input_format: "{detected or declared format}"
classification: "confidential"
run_id: "{YYYY-MM-DDTHH-MM-SS}"
baseline:
  source: "{baseline file path or null}"
  date: "{ISO date of baseline run or null}"
  finding_count: "{baseline finding count or null}"
  run_id: "{baseline run identifier or null}"
coverage_gate:
  status: "{pass | warn}"
  gaps: []
---
```

**Frontmatter fields:**

| Field | Type | Description |
|-------|------|-------------|
| `schema_version` | string | Output schema version. Always `"1.3"` for this release. |
| `date` | string | ISO 8601 date when the threat model was generated. Format: `YYYY-MM-DD`. |
| `input_format` | string | Architecture input format that was analyzed. One of: `ascii`, `free-text`, `mermaid`, `plantuml`, `c4`. |
| `classification` | string | Data classification label for the report. Default: `confidential`. |
| `run_id` | string | Unique identifier for this pipeline run. Format: `YYYY-MM-DDTHH-MM-SS`. Used as `baseline_run_id` in future runs. |
| `baseline.source` | string, nullable | File path of the baseline used for this run. Null when no baseline (first run). |
| `baseline.date` | string, nullable | ISO date of the baseline run. Null when no baseline. |
| `baseline.finding_count` | integer, nullable | Total findings in the baseline. Null when no baseline. |
| `baseline.run_id` | string, nullable | Run identifier of the baseline. Null when no baseline. |
| `coverage_gate.status` | string | Coverage gate result. `"pass"` (all required categories covered or analyzed clean) or `"warn"` (unresolved gaps remain). |
| `coverage_gate.gaps` | list | List of `{component, missing_category, resolution}` objects. Empty list when all required categories covered with no gaps. Resolution values: `"findings_produced"`, `"analyzed_clean"`, `"dispatch_failure"`. |

**Example frontmatter (with baseline, coverage gate pass):**

```yaml
---
schema_version: "1.3"
date: "2026-03-31"
input_format: "mermaid"
classification: "confidential"
run_id: "2026-03-31T14-22-05"
baseline:
  source: "threats.md"
  date: "2026-03-25"
  finding_count: 39
  run_id: "2026-03-25T12-53-57"
coverage_gate:
  status: "pass"
  gaps: []
---
```

**Example frontmatter (with gaps resolved by re-analysis):**

```yaml
---
schema_version: "1.3"
date: "2026-03-31"
input_format: "mermaid"
classification: "confidential"
run_id: "2026-03-31T14-22-05"
baseline:
  source: "threats.md"
  date: "2026-03-25"
  finding_count: 39
  run_id: "2026-03-25T12-53-57"
coverage_gate:
  status: "pass"
  gaps:
    - { component: "LLM Agent", missing_category: "model-theft", resolution: "findings_produced" }
    - { component: "API Gateway", missing_category: "repudiation", resolution: "analyzed_clean" }
---
```

**Example frontmatter (first run — no baseline):**

```yaml
---
schema_version: "1.3"
date: "2026-03-31"
input_format: "mermaid"
classification: "confidential"
run_id: "2026-03-31T14-22-05"
baseline:
  source: null
  date: null
  finding_count: null
  run_id: null
coverage_gate:
  status: "pass"
  gaps: []
---
```

---

## 1. System Overview

Parsed summary of the architecture input including identified components, data flows, and technologies. This section establishes the scope of the threat model by enumerating everything that was analyzed.

### Components

List every component identified in the architecture input. Each component becomes a row in the Coverage Matrix (Section 5) and a potential target in the STRIDE and AI threat tables.

| Component | Type | MAESTRO Layer | Description |
|-----------|------|---------------|-------------|
| _{component name}_ | _{External Entity \| Process \| Data Store \| Data Flow}_ | _{L1-L7 or Unclassified}_ | _{brief description of the component's role}_ |

**Example:**

| Component | Type | MAESTRO Layer | Description |
|-----------|------|---------------|-------------|
| API Gateway | Process | L4 — Deployment Infrastructure | Routes incoming HTTP requests to backend services and enforces rate limits |
| User Database | Data Store | L2 — Data Operations | PostgreSQL database storing user credentials and profile data |
| Mobile Client | External Entity | L7 — Agent Ecosystem | iOS/Android application that authenticates users and displays content |
| Auth Token Flow | Data Flow | Unclassified | JWT tokens passed from Auth Service to API Gateway on every request |
| LLM Agent | Process | L1 — Foundation Model | Autonomous agent that processes natural-language queries using an LLM backend |

### Data Flows

Describe the data flows between components. Each flow represents a communication path that crosses or operates within trust boundaries.

| Source | Destination | Data | Protocol |
|--------|-------------|------|----------|
| _{source component}_ | _{destination component}_ | _{what data moves}_ | _{transport protocol}_ |

**Example:**

| Source | Destination | Data | Protocol |
|--------|-------------|------|----------|
| Mobile Client | API Gateway | User credentials, API requests | HTTPS/TLS 1.3 |
| API Gateway | User Database | SQL queries, result sets | TCP (encrypted) |
| LLM Agent | External LLM API | Prompts, completions | HTTPS/TLS 1.3 |

### Technologies

List the technologies, frameworks, and protocols identified in the architecture input.

| Category | Technology | Version (if known) |
|----------|------------|--------------------|
| _{category}_ | _{technology name}_ | _{version or "unknown"}_ |

**Example:**

| Category | Technology | Version (if known) |
|----------|------------|--------------------|
| Runtime | Python | 3.12 |
| Framework | FastAPI | 0.110 |
| Database | PostgreSQL | 16 |
| Auth | JWT (RS256) | RFC 7519 |
| LLM Provider | OpenAI GPT-4 | 2025-01 |

---

## 2. Trust Boundaries

Identified trust zones and boundary crossings derived from the architecture input. Trust boundaries define where the security posture changes and where additional controls are required.

### Trust Zones

Each zone represents an area with a consistent security posture. Components within the same zone share a trust level.

| Zone | Trust Level | Components |
|------|-------------|------------|
| _{zone name}_ | _{trust level description}_ | _{comma-separated component names}_ |

**Example:**

| Zone | Trust Level | Components |
|------|-------------|------------|
| Public Internet | Untrusted | Mobile Client |
| DMZ | Semi-trusted | API Gateway, Load Balancer |
| Internal Network | Trusted | Auth Service, User Database, LLM Agent |
| External Services | Untrusted | External LLM API |

### Boundary Crossings

Each crossing is a point where data moves between zones with different trust levels. These are high-priority targets for threat analysis.

| Crossing | From Zone | To Zone | Components | Controls |
|----------|-----------|---------|------------|----------|
| _{crossing name}_ | _{source zone}_ | _{destination zone}_ | _{components involved}_ | _{security controls at boundary}_ |

**Example:**

| Crossing | From Zone | To Zone | Components | Controls |
|----------|-----------|---------|------------|----------|
| Client-to-DMZ | Public Internet | DMZ | Mobile Client -> API Gateway | TLS termination, WAF, rate limiting |
| DMZ-to-Internal | DMZ | Internal Network | API Gateway -> Auth Service | Mutual TLS, JWT validation |
| Internal-to-External | Internal Network | External Services | LLM Agent -> External LLM API | API key auth, egress filtering |

---

## 3. STRIDE Tables

One table per STRIDE category containing threat findings for each applicable component. Each finding row uses the Finding IR schema (`schemas/finding.yaml`).

**ID prefix convention:**

| Prefix | Category |
|--------|----------|
| S | Spoofing |
| T | Tampering |
| R | Repudiation |
| I | Information Disclosure |
| D | Denial of Service |
| E | Elevation of Privilege |

**Status column** (baseline-aware mode only): Every finding includes a delta annotation showing its lifecycle status relative to the baseline: `NEW` (discovered this run), `UNCHANGED` (identical to baseline), `UPDATED` (component context changed). `RESOLVED` findings appear in Section 4b, not in these tables. When no baseline is present (first run), all findings show `NEW`.

**Risk level computation (OWASP 3x3 matrix):**

| | LOW Likelihood | MEDIUM Likelihood | HIGH Likelihood |
|---|---|---|---|
| **HIGH Impact** | Medium | High | Critical |
| **MEDIUM Impact** | Low | Medium | High |
| **LOW Impact** | Note | Low | Medium |

### 3.1 Spoofing (S)

Threats where an attacker pretends to be something or someone else.

| ID | Status | Component | MAESTRO Layer | Threat | Likelihood | Impact | Risk Level | Mitigation |
|----|--------|-----------|---------------|--------|------------|--------|------------|------------|
| _{S-N}_ | _{NEW \| UNCHANGED \| UPDATED}_ | _{component}_ | _{L1-L7 or Unclassified}_ | _{threat description}_ | _{LOW \| MEDIUM \| HIGH}_ | _{LOW \| MEDIUM \| HIGH}_ | _{risk from 3x3 matrix}_ | _{recommended countermeasure}_ |

**Example:**

| ID | Status | Component | MAESTRO Layer | Threat | Likelihood | Impact | Risk Level | Mitigation |
|----|--------|-----------|---------------|--------|------------|--------|------------|------------|
| S-1 | UNCHANGED | API Gateway | L4 — Deployment Infrastructure | Attacker forges JWT tokens to impersonate authenticated users by exploiting weak signing algorithm | HIGH | HIGH | Critical | Enforce RS256 signing with key rotation every 90 days; reject HS256 tokens |

### 3.2 Tampering (T)

Threats where an attacker modifies data or code without authorization.

| ID | Status | Component | MAESTRO Layer | Threat | Likelihood | Impact | Risk Level | Mitigation |
|----|--------|-----------|---------------|--------|------------|--------|------------|------------|
| _{T-N}_ | _{NEW \| UNCHANGED \| UPDATED}_ | _{component}_ | _{L1-L7 or Unclassified}_ | _{threat description}_ | _{LOW \| MEDIUM \| HIGH}_ | _{LOW \| MEDIUM \| HIGH}_ | _{risk from 3x3 matrix}_ | _{recommended countermeasure}_ |

**Example:**

| ID | Status | Component | MAESTRO Layer | Threat | Likelihood | Impact | Risk Level | Mitigation |
|----|--------|-----------|---------------|--------|------------|--------|------------|------------|
| T-1 | UPDATED | User Database | L2 — Data Operations | Attacker performs SQL injection through unsanitized input fields to modify user records | MEDIUM | HIGH | High | Use parameterized queries exclusively; apply input validation at API Gateway layer |

### 3.3 Repudiation (R)

Threats where an attacker denies having performed an action without the system being able to prove otherwise.

| ID | Status | Component | MAESTRO Layer | Threat | Likelihood | Impact | Risk Level | Mitigation |
|----|--------|-----------|---------------|--------|------------|--------|------------|------------|
| _{R-N}_ | _{NEW \| UNCHANGED \| UPDATED}_ | _{component}_ | _{L1-L7 or Unclassified}_ | _{threat description}_ | _{LOW \| MEDIUM \| HIGH}_ | _{LOW \| MEDIUM \| HIGH}_ | _{risk from 3x3 matrix}_ | _{recommended countermeasure}_ |

**Example:**

| ID | Status | Component | MAESTRO Layer | Threat | Likelihood | Impact | Risk Level | Mitigation |
|----|--------|-----------|---------------|--------|------------|--------|------------|------------|
| R-1 | UNCHANGED | Auth Service | L6 — Security and Compliance | User denies performing privileged actions because audit logs do not capture sufficient session context | MEDIUM | MEDIUM | Medium | Implement immutable audit log with session ID, IP, user agent, and action timestamp for all privileged operations |

### 3.4 Information Disclosure (I)

Threats where sensitive data is exposed to unauthorized parties.

| ID | Status | Component | MAESTRO Layer | Threat | Likelihood | Impact | Risk Level | Mitigation |
|----|--------|-----------|---------------|--------|------------|--------|------------|------------|
| _{I-N}_ | _{NEW \| UNCHANGED \| UPDATED}_ | _{component}_ | _{L1-L7 or Unclassified}_ | _{threat description}_ | _{LOW \| MEDIUM \| HIGH}_ | _{LOW \| MEDIUM \| HIGH}_ | _{risk from 3x3 matrix}_ | _{recommended countermeasure}_ |

**Example:**

| ID | Status | Component | MAESTRO Layer | Threat | Likelihood | Impact | Risk Level | Mitigation |
|----|--------|-----------|---------------|--------|------------|--------|------------|------------|
| I-1 | UNCHANGED | User Database | L2 — Data Operations | Database connection string with credentials exposed in application error messages returned to client | MEDIUM | HIGH | High | Implement structured error handling that returns generic error codes to clients; log detailed errors server-side only |

### 3.5 Denial of Service (D)

Threats where an attacker degrades or prevents legitimate access to the system.

| ID | Status | Component | MAESTRO Layer | Threat | Likelihood | Impact | Risk Level | Mitigation |
|----|--------|-----------|---------------|--------|------------|--------|------------|------------|
| _{D-N}_ | _{NEW \| UNCHANGED \| UPDATED}_ | _{component}_ | _{L1-L7 or Unclassified}_ | _{threat description}_ | _{LOW \| MEDIUM \| HIGH}_ | _{LOW \| MEDIUM \| HIGH}_ | _{risk from 3x3 matrix}_ | _{recommended countermeasure}_ |

**Example:**

| ID | Status | Component | MAESTRO Layer | Threat | Likelihood | Impact | Risk Level | Mitigation |
|----|--------|-----------|---------------|--------|------------|--------|------------|------------|
| D-1 | UNCHANGED | API Gateway | L4 — Deployment Infrastructure | Volumetric attack overwhelms the gateway with malformed requests, exhausting connection pool and blocking legitimate traffic | HIGH | MEDIUM | High | Enforce per-IP rate limiting (100 req/min); deploy upstream DDoS protection; implement circuit breaker pattern |

### 3.6 Elevation of Privilege (E)

Threats where an attacker gains higher access rights than authorized.

| ID | Status | Component | MAESTRO Layer | Threat | Likelihood | Impact | Risk Level | Mitigation |
|----|--------|-----------|---------------|--------|------------|--------|------------|------------|
| _{E-N}_ | _{NEW \| UNCHANGED \| UPDATED}_ | _{component}_ | _{L1-L7 or Unclassified}_ | _{threat description}_ | _{LOW \| MEDIUM \| HIGH}_ | _{LOW \| MEDIUM \| HIGH}_ | _{risk from 3x3 matrix}_ | _{recommended countermeasure}_ |

**Example:**

| ID | Status | Component | MAESTRO Layer | Threat | Likelihood | Impact | Risk Level | Mitigation |
|----|--------|-----------|---------------|--------|------------|--------|------------|------------|
| E-1 | NEW | Auth Service | L6 — Security and Compliance | Attacker exploits insecure direct object reference (IDOR) to access admin endpoints by manipulating user role claims in JWT payload | MEDIUM | HIGH | High | Validate role claims server-side against authoritative user store on every request; never trust client-supplied role values |

---

## 4. AI Threat Tables

Threat findings from AI-specific agents, grouped by agent category. These extend STRIDE with threats unique to agentic and LLM-based systems. Each finding includes an OWASP reference in addition to the standard IR fields.

**ID prefix convention:**

| Prefix | Category |
|--------|----------|
| AG | Agentic Threats |
| LLM | LLM Threats |

### 4.1 Agentic Threats (AG)

Threats arising from autonomous agent behavior, including uncontrolled tool use, excessive autonomy, and agent-to-agent trust violations.

| ID | Status | Component | MAESTRO Layer | Threat | OWASP Reference | Likelihood | Impact | Risk Level | Mitigation |
|----|--------|-----------|---------------|--------|------------------|------------|--------|------------|------------|
| _{AG-N}_ | _{NEW \| UNCHANGED \| UPDATED}_ | _{component}_ | _{L1-L7 or Unclassified}_ | _{threat description}_ | _{OWASP ID or framework citation}_ | _{LOW \| MEDIUM \| HIGH}_ | _{LOW \| MEDIUM \| HIGH}_ | _{risk from 3x3 matrix}_ | _{recommended countermeasure}_ |

**Example:**

| ID | Status | Component | MAESTRO Layer | Threat | OWASP Reference | Likelihood | Impact | Risk Level | Mitigation |
|----|--------|-----------|---------------|--------|------------------|------------|--------|------------|------------|
| AG-1 | UNCHANGED | LLM Agent | L1 — Foundation Model | Agent autonomously invokes destructive shell commands without human approval, causing data loss or system compromise | ASI-01 | MEDIUM | HIGH | High | Implement mandatory human-in-the-loop approval for all destructive operations; enforce tool allowlists with per-tool permission scopes |

### 4.2 LLM Threats (LLM)

Threats targeting the LLM itself, including prompt injection, training data poisoning, model theft, and insecure output handling.

| ID | Status | Component | MAESTRO Layer | Threat | OWASP Reference | Likelihood | Impact | Risk Level | Mitigation |
|----|--------|-----------|---------------|--------|------------------|------------|--------|------------|------------|
| _{LLM-N}_ | _{NEW \| UNCHANGED \| UPDATED}_ | _{component}_ | _{L1-L7 or Unclassified}_ | _{threat description}_ | _{OWASP ID or framework citation}_ | _{LOW \| MEDIUM \| HIGH}_ | _{LOW \| MEDIUM \| HIGH}_ | _{risk from 3x3 matrix}_ | _{recommended countermeasure}_ |

**Example:**

| ID | Status | Component | MAESTRO Layer | Threat | OWASP Reference | Likelihood | Impact | Risk Level | Mitigation |
|----|--------|-----------|---------------|--------|------------------|------------|--------|------------|------------|
| LLM-1 | NEW | LLM Agent | L1 — Foundation Model | Indirect prompt injection via user-supplied documents causes the agent to exfiltrate sensitive context data to an attacker-controlled endpoint | OWASP LLM01:2025 | HIGH | HIGH | Critical | Sanitize all user-supplied input before inclusion in LLM context; implement output filtering to block URLs and data patterns matching exfiltration; apply egress network controls |

---

## 4a. Correlated Findings

Cross-agent correlation groups linking findings from different agent categories that target the same component for related threats. Each group represents a single underlying issue identified from multiple security perspectives. Original findings remain unchanged in their respective tables (Sections 3 and 4) — correlation groups are additive, not replacements.

| Group | Findings | Component | Threat Summary | Risk Level |
|-------|----------|-----------|----------------|------------|
| _{CG-N}_ | _{comma-separated finding IDs}_ | _{target component}_ | _{each agent perspective prefixed by category name}_ | _{highest risk among members}_ |

**Example** (multiple rules match on same component — merged into single group per algorithm):

| Group | Findings | Component | Threat Summary | Risk Level |
|-------|----------|-----------|----------------|------------|
| CG-1 | T-2, E-1, LLM-1, AG-1 | LLM Agent Orchestrator | Tampering: unauthorized modification of agent orchestration data; Privilege-Escalation: agent gains admin-level access through role manipulation; Data-Poisoning: manipulation of training data used by the orchestration layer; Agent-Autonomy: agent performs privileged operations without human approval | Critical |

**When zero correlations are detected:**

> No cross-agent correlations detected.

| Group | Findings | Component | Threat Summary | Risk Level |
|-------|----------|-----------|----------------|------------|

---

## 4b. Resolved Findings

Findings from the baseline that are no longer applicable in the current architecture. These findings are retained for audit traceability — each preserves its original ID, description, and last-known risk level. This section is only present when a baseline was used for the current run.

**When no baseline is present** (first run): Omit this section entirely. Do not include the header or an empty table.

**When a baseline is present but no findings are resolved**: Include the section header with the note: "No baseline findings were resolved in this run." followed by an empty table header.

| ID | Component | Threat | Last Risk Level | Resolution Reason |
|----|-----------|--------|-----------------|-------------------|
| _{original ID}_ | _{baseline component}_ | _{original threat description}_ | _{last-known risk level}_ | _{why the finding was resolved}_ |

**Example:**

| ID | Component | Threat | Last Risk Level | Resolution Reason |
|----|-----------|--------|-----------------|-------------------|
| T-2 | Legacy API | SQL injection through unvalidated query parameters in deprecated endpoint | High | Component 'Legacy API' removed from architecture |
| LLM-3 | Chat Widget | Indirect prompt injection via user-uploaded documents | Medium | Threat category no longer applicable to 'Chat Widget' (reclassified as External Entity) |

**Field definitions:**

| Field | Source | Description |
|-------|--------|-------------|
| ID | Baseline finding ID | The original stable finding ID — never reassigned to new findings |
| Component | Baseline component name | The component targeted by the finding at the time of its last assessment |
| Threat | Baseline threat description | The full threat description from the last assessment |
| Last Risk Level | Baseline risk level | The risk level at the time of the last active assessment (Critical/High/Medium/Low/Note) |
| Resolution Reason | Carry-forward classification | Brief explanation of why the finding is resolved (component removed, category inapplicable, etc.) |

---

## 5. Coverage Matrix

Cross-reference matrix showing which components were analyzed for which threat categories. Each cell uses a three-state model:

- **Integer**: Deduplicated finding count for that component-category pair. When findings belong to a correlation group (Section 4a), the group contributes 1 to the count collectively rather than individually.
- **`—`** (em dash): The component was analyzed for that category but no threats were found (analyzed but clean).
- **`n/a`**: The category does not apply to this component — it was not dispatched for analysis.

| Component | S | T | R | I | D | E | AG | LLM | Total |
|-----------|---|---|---|---|---|---|----|-----|-------|
| _{component}_ | _{count \| — \| n/a}_ | _{count \| — \| n/a}_ | _{count \| — \| n/a}_ | _{count \| — \| n/a}_ | _{count \| — \| n/a}_ | _{count \| — \| n/a}_ | _{count \| — \| n/a}_ | _{count \| — \| n/a}_ | _{total}_ |

**Example** (with correlation — T-2, E-1, LLM-1, AG-1 correlated on LLM Agent Orchestrator as CG-1; 4 findings merged into 1 group):

| Component | S | T | R | I | D | E | AG | LLM | Total |
|-----------|---|---|---|---|---|---|----|-----|-------|
| API Gateway | 1 | — | — | — | 1 | — | n/a | n/a | 2 |
| User Database | — | 1 | — | 1 | — | — | n/a | n/a | 2 |
| Auth Service | — | — | 1 | — | — | 1 | n/a | n/a | 2 |
| LLM Agent Orchestrator | — | 1 | — | — | — | 1 | 1 | 1 | 4 |
| **Total** | **1** | **2** | **1** | **1** | **1** | **2** | **1** | **1** | **10** |

Counts reflect deduplicated findings. 1 correlation group merged 4 individual findings.

---

## 5a. Coverage Gate Results

Coverage gate evaluation results showing whether all required threat categories were analyzed for each component based on its type. The gate loads `schemas/coverage-checklists.yaml` to determine required categories per component type (including AI subtype detection) and verifies the finding set covers all requirements.

**When the coverage gate passes with no gaps**: Include the section header with: "Coverage gate passed — all required threat categories evaluated for every component." followed by the requirements matrix.

**When gaps were detected and resolved**: Include the full results table showing each gap and its resolution.

### Coverage Requirements Matrix

Shows required vs. evaluated categories for each component based on its determined type.

| Component | Determined Type | Required Categories | Evaluated | Gaps |
|-----------|----------------|-----------------------|-----------|------|
| _{component}_ | _{external_entity \| process \| data_store \| data_flow \| llm_process \| mcp_server}_ | _{comma-separated required categories}_ | _{count evaluated}_ / _{count required}_ | _{count gaps or "None"}_ |

**Example (with one gap resolved by re-analysis):**

| Component | Determined Type | Required Categories | Evaluated | Gaps |
|-----------|----------------|-----------------------|-----------|------|
| API Gateway | process | S, T, R, I, D, E | 6 / 6 | None |
| User Database | data_store | T, I, D | 3 / 3 | None |
| LLM Agent | llm_process | S, T, R, I, D, E, LLM | 7 / 7 | None |
| Mobile Client | external_entity | S, R | 2 / 2 | None |

### Gap Resolution Details

**Present only when gaps were detected.** Shows each gap and its resolution after targeted re-analysis.

| Component | Missing Category | Agent(s) Dispatched | Resolution | Findings Added |
|-----------|-----------------|---------------------|------------|----------------|
| _{component}_ | _{category}_ | _{agent name(s)}_ | _{findings_produced \| analyzed_clean \| dispatch_failure}_ | _{count or 0}_ |

**Example:**

| Component | Missing Category | Agent(s) Dispatched | Resolution | Findings Added |
|-----------|-----------------|---------------------|------------|----------------|
| LLM Agent | model-theft | tachi-model-theft | findings_produced | 1 |
| API Gateway | repudiation | tachi-repudiation | analyzed_clean | 0 |

**Resolution values:**
- `findings_produced` — Re-analysis discovered new threats. Findings merged into the finding set with sequential IDs.
- `analyzed_clean` — Re-analysis ran but found no threats for this component-category pair. The category was evaluated; no blind spot exists.
- `dispatch_failure` — Agent dispatch failed. The gap remains unresolved. Reported as a warning.

---

## 6. Risk Summary

Aggregate counts of findings by risk level, computed using the OWASP 3x3 matrix (likelihood x impact). Provides a quick posture assessment.

### Risk Calibration Matrix

The following OWASP 3×3 risk matrix documents how risk levels are computed for every finding in this threat model. Impact (rows) and Likelihood (columns) determine the Risk Level at each intersection. All agents use this same matrix, ensuring consistent risk ratings across STRIDE and AI threat categories.

| | LOW Likelihood | MEDIUM Likelihood | HIGH Likelihood |
|---|---|---|---|
| **HIGH Impact** | Medium | High | Critical |
| **MEDIUM Impact** | Low | Medium | High |
| **LOW Impact** | Note | Low | Medium |

#### Risk by MAESTRO Layer

Finding counts and highest severity grouped by CSA MAESTRO architectural layer. Layers with zero findings are omitted. Rows ordered by highest severity descending, then finding count descending.

| MAESTRO Layer | Finding Count | Highest Severity |
|---------------|---------------|------------------|
| _{layer name}_ | _{deduplicated count}_ | _{highest risk level}_ |

**Example:**

| MAESTRO Layer | Finding Count | Highest Severity |
|---------------|---------------|------------------|
| L4 — Deployment Infrastructure | 3 | Critical |
| L2 — Data Operations | 2 | High |
| L6 — Security and Compliance | 2 | Medium |
| L1 — Foundation Model | 2 | Critical |

Risk summary counts below reflect deduplicated findings. When correlation groups exist, correlated findings count as one unique threat per group rather than individually.

| Risk Level | Count | Percentage |
|------------|-------|------------|
| Critical | _{dedup count}_ | _{dedup count / dedup total * 100}%_ |
| High | _{dedup count}_ | _{dedup count / dedup total * 100}%_ |
| Medium | _{dedup count}_ | _{dedup count / dedup total * 100}%_ |
| Low | _{dedup count}_ | _{dedup count / dedup total * 100}%_ |
| Note | _{dedup count}_ | _{dedup count / dedup total * 100}%_ |
| **Total** | _{dedup total}_ | **100%** |

When correlation groups exist and the deduplicated total differs from the raw finding count, display the count with a parenthetical raw count: e.g., `"5 (7 raw)"`. When no correlations exist, display the count alone.

**Example** (same scenario as Coverage Matrix: 10 raw findings, 1 correlation group merging 4 findings into 1 group — dedup total 7):

| Risk Level | Count | Percentage |
|------------|-------|------------|
| Critical | 1 (2 raw) | 14.3% |
| High | 3 (5 raw) | 42.8% |
| Medium | 2 | 28.6% |
| Low | 1 | 14.3% |
| Note | 0 | 0.0% |
| **Total** | **7 (10 raw)** | **100%** |

---

## 7. Recommended Actions

Prioritized list of all findings sorted by risk level descending, providing a remediation roadmap. Critical and High findings should be addressed before deployment. Medium findings should be addressed within the current development cycle. Low and Note findings should be tracked for future consideration.

**Status column** (baseline-aware mode only): Carries the `delta_status` lifecycle annotation for each finding. Values: `NEW` (discovered this run), `UNCHANGED` (identical to baseline), `UPDATED` (component context changed). RESOLVED findings do not appear in this table — they are listed in Section 4b. When no baseline is present (first run), all findings show `NEW`. The Status column enables downstream consumers (extraction scripts, report agents) to access delta information from a single parsed table.

| Finding ID | Status | Component | MAESTRO Layer | Threat | Risk Level | Mitigation |
|------------|--------|-----------|---------------|--------|------------|------------|
| _{finding ID}_ | _{NEW \| UNCHANGED \| UPDATED}_ | _{component}_ | _{L1-L7 or Unclassified}_ | _{threat summary}_ | _{risk level}_ | _{recommended countermeasure}_ |

**Example:**

| Finding ID | Status | Component | MAESTRO Layer | Threat | Risk Level | Mitigation |
|------------|--------|-----------|---------------|--------|------------|------------|
| S-1 | UNCHANGED | API Gateway | L4 — Deployment Infrastructure | Forged JWT tokens via weak signing algorithm | Critical | Enforce RS256 signing with key rotation every 90 days; reject HS256 tokens |
| LLM-1 | NEW | LLM Agent | L1 — Foundation Model | Indirect prompt injection exfiltrating context data | Critical | Sanitize user input before LLM context; implement output filtering and egress controls |
| T-1 | UPDATED | User Database | L2 — Data Operations | SQL injection through unsanitized input | High | Use parameterized queries; apply input validation at API Gateway |
| I-1 | UNCHANGED | User Database | L2 — Data Operations | Credentials exposed in error messages | High | Structured error handling with generic client responses; server-side detailed logging |
| D-1 | UNCHANGED | API Gateway | L4 — Deployment Infrastructure | Volumetric attack exhausting connection pool | High | Per-IP rate limiting; upstream DDoS protection; circuit breaker pattern |
| E-1 | NEW | Auth Service | L6 — Security and Compliance | IDOR exploiting role claims in JWT payload | High | Server-side role validation against authoritative store on every request |
| AG-1 | UNCHANGED | LLM Agent | L1 — Foundation Model | Uncontrolled destructive command execution | High | Human-in-the-loop approval for destructive operations; tool allowlists |
| R-1 | UNCHANGED | Auth Service | L5 — Evaluation and Observability | Insufficient audit logging for privileged actions | Medium | Immutable audit log with session ID, IP, user agent, and timestamp |

---

## 8. Delta Summary

_Present only when a baseline was used for the current run. Omit this entire section (header and content) on first run (no baseline)._

This section provides an aggregate lifecycle breakdown of all findings relative to the baseline, remediation proof, and a reference back to the baseline used for comparison. Section 4b provides individual resolved finding details; this section provides the summary view.

### Finding Lifecycle

| Status | Count | Description |
|--------|-------|-------------|
| NEW | _{count}_ | Findings discovered in this run with no baseline match |
| UNCHANGED | _{count}_ | Findings identical to baseline (same component, threat, assessment) |
| UPDATED | _{count}_ | Findings with changed context since baseline |
| RESOLVED | _{count}_ | Baseline findings no longer applicable (see Section 4b for details) |
| **Total** | _{total}_ | Sum of all findings (active + resolved) |

### Baseline Reference

| Field | Value |
|-------|-------|
| Source | _{baseline file path}_ |
| Date | _{baseline date}_ |
| Baseline Findings | _{baseline finding count}_ |
| Run ID | _{baseline run ID}_ |

**Example:**

### Finding Lifecycle

| Status | Count | Description |
|--------|-------|-------------|
| NEW | 5 | Findings discovered in this run with no baseline match |
| UNCHANGED | 12 | Findings identical to baseline (same component, threat, assessment) |
| UPDATED | 2 | Findings with changed context since baseline |
| RESOLVED | 3 | Baseline findings no longer applicable (see Section 4b for details) |
| **Total** | **22** | Sum of all findings (active + resolved) |

### Baseline Reference

| Field | Value |
|-------|-------|
| Source | threats.md |
| Date | 2026-03-25 |
| Baseline Findings | 20 |
| Run ID | 2026-03-25T12-53-57 |
