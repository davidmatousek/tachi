# Risk Scores Report

---

```yaml
---
schema_version: "1.0"
date: "2026-03-27"
source_file: "threats.md"
classification: "confidential"
scoring_weights:
  cvss_base: 0.35
  exploitability: 0.30
  scalability: 0.15
  reachability: 0.20
---
```

---

## 1. Executive Summary

**34 findings** scored across 8 threat categories (Spoofing, Tampering, Repudiation, Information Disclosure, Denial of Service, Elevation of Privilege, Agentic Threats, LLM Threats).

**Highest-Risk Component**: LLM Agent Orchestrator (composite: 8.3, severity: High)

| Metric | Value |
|--------|-------|
| Scoring date | 2026-03-27 |
| Source file | `threats.md` |
| Schema version | 1.0 |

**Severity Distribution:**

| Severity | Count | Percentage |
|----------|-------|------------|
| Critical | 0 | 0.0% |
| High | 10 | 29.4% |
| Medium | 24 | 70.6% |
| Low | 0 | 0.0% |
| **Total** | **34** | **100%** |

The majority of findings (24 of 34) fall in the Medium band, with 10 High-severity findings requiring priority remediation within 7 days. The LLM Agent Orchestrator is the highest-risk component, reflecting its central role in processing user prompts and dispatching tool calls across trust boundaries.

---

## 2. Scored Threat Table

Findings sorted by Composite score descending (highest risk first). Boundary values map to the higher severity band (e.g., 7.0 = High, 9.0 = Critical).

| ID | Component | Threat | CVSS | Exploit. | Scale. | Reach. | Composite | Severity | SLA | Disposition |
|----|-----------|--------|------|----------|--------|--------|-----------|----------|-----|-------------|
| LLM-1 | LLM Agent Orchestrator | Adversarial prompts override system prompt, bypassing safe... | 9.8 | 8.8 | 7.3 | 5.5 | 8.3 | High | 7d | Mitigate |
| S-1 | User | Attacker impersonates legitimate user by replaying or forg... | 8.2 | 7.0 | 6.8 | 9.5 | 7.9 | High | 7d | Mitigate |
| E-2 | LLM Agent Orchestrator | Attacker escalates to admin tool access through prompt inj... | 9.1 | 7.8 | 6.3 | 5.5 | 7.6 | High | 7d | Mitigate |
| AG-1 | LLM Agent Orchestrator | Orchestrator executes consequential actions without human ... | 9.1 | 7.8 | 6.3 | 5.5 | 7.6 | High | 7d | Mitigate |
| E-3 | MCP Tool Server | User invokes admin tool endpoints by manipulating tool_nam... | 9.9 | 6.8 | 5.8 | 5.5 | 7.5 | High | 7d | Mitigate |
| D-1 | Guardrails Service | Attacker floods Guardrails Service to exhaust CPU on regex... | 7.5 | 8.5 | 7.8 | 5.5 | 7.4 | High | 7d | Mitigate |
| D-2 | LLM Agent Orchestrator | Attacker sends concurrent max-length prompts to exhaust LL... | 7.5 | 8.3 | 7.5 | 5.5 | 7.3 | High | 7d | Mitigate |
| S-3 | LLM Agent Orchestrator | Attacker forges tool call requests to MCP Tool Server by i... | 9.8 | 6.0 | 5.5 | 5.5 | 7.2 | High | 7d | Mitigate |
| T-3 | MCP Tool Server | Attacker manipulates JSON-RPC tool call parameters in tran... | 8.8 | 6.8 | 5.8 | 5.5 | 7.1 | High | 7d | Mitigate |
| AG-3 | MCP Tool Server | MCP Tool Server exposes all tools to every client without ... | 9.1 | 6.3 | 5.5 | 5.5 | 7.0 | High | 7d | Mitigate |
| S-2 | Guardrails Service | Attacker bypasses Guardrails by directly accessing Orchest... | 8.2 | 6.5 | 5.0 | 5.5 | 6.7 | Medium | 30d | Review |
| E-1 | Guardrails Service | Attacker bypasses Guardrails via alternate route to Orches... | 8.8 | 5.8 | 4.8 | 5.5 | 6.6 | Medium | 30d | Review |
| D-3 | MCP Tool Server | Resource exhaustion through concurrent tool calls without ... | 7.5 | 6.3 | 5.5 | 5.5 | 6.4 | Medium | 30d | Review |
| AG-4 | MCP Tool Server | Tool call chaining enables capability escalation beyond in... | 7.5 | 6.3 | 5.5 | 5.5 | 6.4 | Medium | 30d | Review |
| T-4 | Knowledge Base | Attacker injects malicious content into Knowledge Base via... | 7.1 | 6.5 | 5.3 | 5.5 | 6.3 | Medium | 30d | Review |
| LLM-2 | LLM Agent Orchestrator | Indirect prompt injection via adversarial content in Knowl... | 7.1 | 6.5 | 5.3 | 5.5 | 6.3 | Medium | 30d | Review |
| I-1 | Guardrails Service | Rejection reasons reveal internal filtering rules to attac... | 5.3 | 7.8 | 6.0 | 5.5 | 6.2 | Medium | 30d | Review |
| T-2 | LLM Agent Orchestrator | Attacker injects malicious content by tampering with data ... | 7.1 | 6.0 | 5.0 | 5.5 | 6.1 | Medium | 30d | Review |
| D-4 | Knowledge Base | Unbounded vector search queries with adversarial inputs ex... | 7.5 | 5.3 | 4.5 | 5.5 | 6.0 | Medium | 30d | Review |
| I-4 | Knowledge Base | Query responses include internal metadata, embedding vecto... | 5.3 | 7.0 | 5.5 | 5.5 | 5.9 | Medium | 30d | Review |
| T-1 | Guardrails Service | Attacker modifies validation rules at runtime without inte... | 7.1 | 5.3 | 4.3 | 5.5 | 5.8 | Medium | 30d | Review |
| S-4 | MCP Tool Server | Attacker redirects outbound API requests by spoofing DNS o... | 7.4 | 4.5 | 4.3 | 5.5 | 5.7 | Medium | 30d | Review |
| I-3 | MCP Tool Server | Raw External API error responses forwarded without sanitiz... | 6.5 | 5.0 | 5.0 | 5.5 | 5.6 | Medium | 30d | Review |
| I-2 | LLM Agent Orchestrator | Verbose error messages leak internal service topology and ... | 6.5 | 4.8 | 4.5 | 5.5 | 5.5 | Medium | 30d | Review |
| T-5 | Audit Logger | Attacker modifies or deletes audit log entries to cover tr... | 7.1 | 4.3 | 3.5 | 5.5 | 5.4 | Medium | 30d | Review |
| D-5 | Audit Logger | High-volume logging events cause storage exhaustion disrup... | 5.3 | 5.3 | 5.0 | 5.5 | 5.3 | Medium | 30d | Review |
| R-3 | LLM Agent Orchestrator | Orchestrator executes tool calls without logging full deci... | 5.3 | 5.0 | 5.0 | 5.5 | 5.2 | Medium | 30d | Review |
| AG-2 | LLM Agent Orchestrator | Orchestrator operates in unbounded reasoning loop without ... | 5.3 | 5.0 | 5.0 | 5.5 | 5.2 | Medium | 30d | Review |
| I-5 | Audit Logger | Audit logs contain sensitive data accessible beyond the se... | 6.5 | 4.0 | 3.8 | 5.5 | 5.1 | Medium | 30d | Review |
| LLM-3 | LLM Agent Orchestrator | Systematic querying enables model extraction through disti... | 5.3 | 4.5 | 4.8 | 5.5 | 5.0 | Medium | 30d | Review |
| R-1 | User | User denies having submitted a specific prompt without non... | 4.3 | 3.0 | 3.0 | 9.5 | 4.8 | Medium | 30d | Review |
| R-5 | External API | External API interactions lack correlation identifiers for... | 4.3 | 2.5 | 2.8 | 9.5 | 4.6 | Medium | 30d | Review |
| R-2 | Guardrails Service | Insufficient detail in filtering event logs prevents recon... | 4.3 | 4.3 | 3.8 | 5.5 | 4.5 | Medium | 30d | Review |
| R-4 | MCP Tool Server | Tool executions lack requesting orchestrator context for f... | 4.3 | 3.8 | 3.5 | 5.5 | 4.3 | Medium | 30d | Review |

### Column Definitions

| Column | Description |
|--------|-------------|
| **ID** | Original finding identifier from the threat model (e.g., `S-1`, `T-2`, `AG-1`, `LLM-3`). Preserves the source finding ID without modification. |
| **Component** | Target component name as identified in the threat model. |
| **Threat** | Threat description, truncated to fit table width. Full description available in the Dimensional Breakdown (Section 3). |
| **CVSS** | CVSS 3.1 base score (0.0-10.0). Derived from attack vector, attack complexity, privileges required, user interaction, scope, and CIA impact. Full vector string shown in Section 3. |
| **Exploit.** | Exploitability score (0.0-10.0). Average of four sub-dimensions: known techniques, attack complexity, tooling availability, and skill level required. |
| **Scale.** | Scalability score (0.0-10.0). Average of four sub-dimensions: scriptability, target scope, resource requirements, and detection difficulty. |
| **Reach.** | Reachability score (0.0-10.0). Derived from trust zone placement: Untrusted/External = 8.0-10.0, Semi-Trusted/Application = 4.0-7.0, Trusted/Internal = 1.0-4.0. Default 5.0 when trust zone data is unavailable. |
| **Composite** | Weighted composite score (0.0-10.0). Formula: `(0.35 x CVSS) + (0.30 x Exploit.) + (0.15 x Scale.) + (0.20 x Reach.)`. |
| **Severity** | Severity band mapped from composite score: Critical (9.0-10.0), High (7.0-8.9), Medium (4.0-6.9), Low (0.0-3.9). |
| **SLA** | Default remediation SLA driven by severity: Critical = 24h, High = 7d, Medium = 30d, Low = 90d. |
| **Disposition** | Default risk disposition driven by severity: Critical/High = Mitigate, Medium/Low = Review. May be overridden in the Governance Fields table (Section 4). |

> **Correlated findings**: For correlation groups (Section 4a of the source threat model), the primary finding is scored independently. Correlated peer findings inherit the primary's scores to maintain group consistency. Groups: CG-1 (T-4 primary, LLM-2 peer), CG-2 (E-2 primary, AG-1 peer), CG-3 (R-3 primary, AG-2 peer), CG-4 (D-3 primary, AG-4 peer).

---

## 3. Dimensional Breakdown

Per-finding detail showing the full scoring rationale for each dimension. One subsection per finding, ordered by composite score descending (matching Section 2 sort order).

### LLM-1 -- LLM Agent Orchestrator

**Threat**: Attacker submits adversarial prompts through the Guardrails Service that override the Orchestrator's system prompt, causing it to ignore safety constraints, disclose internal instructions, or produce harmful content, because user input is concatenated into the LLM prompt without structured boundary enforcement between system instructions and user content

**Category**: LLM Threats | **Original Risk Level**: Critical | **Composite**: 8.3 (High)

| Dimension | Score | Weight | Weighted |
|-----------|-------|--------|----------|
| CVSS Base | 9.8 | 0.35 | 3.43 |
| Exploitability | 8.8 | 0.30 | 2.64 |
| Scalability | 7.3 | 0.15 | 1.10 |
| Reachability | 5.5 | 0.20 | 1.10 |
| **Composite** | | | **8.3** |

**CVSS Vector**: `CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H`

**Scoring Rationale**:
- **CVSS**: 9.8 -- Direct prompt injection is a network-accessible attack requiring no authentication or user interaction. Scope is Changed because compromised orchestrator affects downstream tool server, knowledge base, and external APIs. Full CIA impact due to system prompt extraction (C:H), safety constraint bypass (I:H), and potential for uncontrolled resource consumption (A:H).
- **Exploitability**: 8.8 -- Prompt injection is extensively documented with thousands of public examples (Known Techniques: 9). Simple text input with no special conditions (Complexity: 9). Multiple frameworks like Garak and PromptBench available (Tooling: 8). No specialized skills needed; copy-paste payloads work (Skill: 9).
- **Scalability**: 7.3 -- Fully automatable via API calls with rotating payloads (Scriptability: 8). Affects all orchestrator instances with concatenated prompt design (Scope: 7). Minimal resources required (Resources: 8). Partially detectable by input classifiers but evasion techniques are documented (Detection: 6).
- **Reachability**: 5.5 -- LLM Agent Orchestrator resides in the Semi-Trusted Application Zone (baseline 5.5). Not directly internet-facing; user prompts pass through the Guardrails Service first.

---

### S-1 -- User

**Threat**: Attacker impersonates a legitimate user by replaying or forging authentication credentials when submitting prompts to the Guardrails Service, because user identity verification relies solely on bearer tokens without binding to client context such as device fingerprint or IP address

**Category**: Spoofing | **Original Risk Level**: High | **Composite**: 7.9 (High)

| Dimension | Score | Weight | Weighted |
|-----------|-------|--------|----------|
| CVSS Base | 8.2 | 0.35 | 2.87 |
| Exploitability | 7.0 | 0.30 | 2.10 |
| Scalability | 6.8 | 0.15 | 1.02 |
| Reachability | 9.5 | 0.20 | 1.90 |
| **Composite** | | | **7.9** |

**CVSS Vector**: `CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:L/A:N`

**Scoring Rationale**:
- **CVSS**: 8.2 -- Remote credential replay over HTTPS (AV:N). No special conditions for token replay (AC:L). Attacker uses stolen/forged tokens without prior auth (PR:N). No victim interaction needed (UI:N). Scope Unchanged; spoofed identity operates within the victim's authorization boundary. High confidentiality impact from accessing victim data; low integrity from submitting prompts as victim.
- **Exploitability**: 7.0 -- Token replay and session hijacking are well-documented (Known: 8). Requires capturing a valid token first (Complexity: 7). Burp Suite, ZAP available for replay attacks (Tooling: 7). Moderate skill for HTTP auth and token interception (Skill: 6).
- **Scalability**: 6.8 -- Token replay is easily scripted once captured (Scriptability: 8). Affects all users with bearer-token-only auth (Scope: 6). Minimal resources needed (Resources: 8). Replayed tokens are legitimate credentials; detection requires contextual analysis (Detection: 5).
- **Reachability**: 9.5 -- User component resides in the Untrusted User Zone (baseline 9.0). The "user" keyword adds +0.5, resulting in 9.5. Directly exposed to external attackers as the system entry point.

---

### E-2 -- LLM Agent Orchestrator

**Threat**: Attacker escalates from a standard user role to administrative capabilities by manipulating the orchestrator's tool selection logic through prompt injection, causing it to invoke privileged tool endpoints that should be restricted to administrator roles, because the Orchestrator does not enforce role-based access control on tool dispatch

**Category**: Privilege Escalation | **Original Risk Level**: Critical | **Composite**: 7.6 (High)

**Correlation Group**: CG-2 primary. Peer AG-1 inherits these scores.

| Dimension | Score | Weight | Weighted |
|-----------|-------|--------|----------|
| CVSS Base | 9.1 | 0.35 | 3.19 |
| Exploitability | 7.8 | 0.30 | 2.34 |
| Scalability | 6.3 | 0.15 | 0.95 |
| Reachability | 5.5 | 0.20 | 1.10 |
| **Composite** | | | **7.6** |

**CVSS Vector**: `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:L`

**Scoring Rationale**:
- **CVSS**: 9.1 -- Remote prompt injection (AV:N). No special conditions needed (AC:L). Requires standard user account (PR:L). No additional user interaction (UI:N). Scope Changed: privilege escalation crosses user-to-admin boundary. Admin tools expose configuration and user data (C:H), enable modifications (I:H), with limited availability impact (A:L).
- **Exploitability**: 7.8 -- Prompt injection for tool manipulation is well-documented in agentic AI research (Known: 8). Requires crafting prompts targeting tool selection; some trial-and-error (Complexity: 7). Prompt injection tools exist; tool-specific payloads need customization (Tooling: 7). Understanding of tool dispatch patterns helps but trial-and-error works (Skill: 9).
- **Scalability**: 6.3 -- Payloads can be automated but may need per-instance tuning (Scriptability: 6). Affects all standard users where RBAC is missing (Scope: 6). Minimal resources needed (Resources: 8). Tool invocation anomalies are detectable with monitoring (Detection: 5).
- **Reachability**: 5.5 -- LLM Agent Orchestrator resides in the Semi-Trusted Application Zone (baseline 5.5). No architecture.md adjustments.

---

### AG-1 -- LLM Agent Orchestrator

**Threat**: LLM Agent Orchestrator executes consequential actions (external API calls via MCP Tool Server, Knowledge Base writes) without human approval gates, because no risk-tier classification distinguishes reversible read operations from irreversible write/delete/send operations, violating the principle that high-stakes agent actions require human-in-the-loop review

**Category**: Agentic Threats | **Original Risk Level**: Critical | **Composite**: 7.6 (High)

**Correlation Group**: Scores inherited from primary finding E-2 (CG-2).

| Dimension | Score | Weight | Weighted |
|-----------|-------|--------|----------|
| CVSS Base | 9.1 | 0.35 | 3.19 |
| Exploitability | 7.8 | 0.30 | 2.34 |
| Scalability | 6.3 | 0.15 | 0.95 |
| Reachability | 5.5 | 0.20 | 1.10 |
| **Composite** | | | **7.6** |

**CVSS Vector**: `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:L`

**Scoring Rationale**:
- **CVSS**: 9.1 -- Scores inherited from CG-2 primary E-2. Excessive agent permissions combined with missing human oversight create the same attack surface.
- **Exploitability**: 7.8 -- Inherited from CG-2 primary E-2.
- **Scalability**: 6.3 -- Inherited from CG-2 primary E-2.
- **Reachability**: 5.5 -- LLM Agent Orchestrator resides in the Semi-Trusted Application Zone.

---

### E-3 -- MCP Tool Server

**Threat**: Authenticated user invokes administrative tool endpoints on the MCP Tool Server by manipulating the tool_name parameter, because the server does not enforce role-based access control on tool dispatch, allowing standard users to execute privileged operations such as configuration changes and data exports

**Category**: Privilege Escalation | **Original Risk Level**: Critical | **Composite**: 7.5 (High)

| Dimension | Score | Weight | Weighted |
|-----------|-------|--------|----------|
| CVSS Base | 9.9 | 0.35 | 3.47 |
| Exploitability | 6.8 | 0.30 | 2.04 |
| Scalability | 5.8 | 0.15 | 0.87 |
| Reachability | 5.5 | 0.20 | 1.10 |
| **Composite** | | | **7.5** |

**CVSS Vector**: `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H`

**Scoring Rationale**:
- **CVSS**: 9.9 -- Remote tool name manipulation via JSON-RPC (AV:N). Simple parameter change (AC:L). Standard user access needed (PR:L). No user interaction (UI:N). Scope Changed: escalation affects external APIs and data stores. Full CIA impact through admin tools: data export (C:H), configuration changes (I:H), service disruption capabilities (A:H).
- **Exploitability**: 6.8 -- IDOR and parameter manipulation for privilege escalation are well-documented (Known: 7). Requires knowledge of admin tool names; enumeration needed (Complexity: 7). Standard API testing tools support parameter manipulation (Tooling: 6). Moderate skill for JSON-RPC and tool naming conventions (Skill: 7).
- **Scalability**: 5.8 -- Tool name enumeration and exploitation can be scripted (Scriptability: 6). Affects all standard users reaching the orchestrator (Scope: 5). Minimal resources needed (Resources: 8). Role-based tool access violations are detectable (Detection: 4).
- **Reachability**: 5.5 -- MCP Tool Server resides in the Semi-Trusted Application Zone (baseline 5.5).

---

### D-1 -- Guardrails Service

**Threat**: Attacker floods the Guardrails Service with high-volume prompt submissions designed to exhaust CPU on complex regex-based content filtering rules, because no rate limiting or request size caps are enforced at the entry point

**Category**: Denial of Service | **Original Risk Level**: Critical | **Composite**: 7.4 (High)

| Dimension | Score | Weight | Weighted |
|-----------|-------|--------|----------|
| CVSS Base | 7.5 | 0.35 | 2.63 |
| Exploitability | 8.5 | 0.30 | 2.55 |
| Scalability | 7.8 | 0.15 | 1.17 |
| Reachability | 5.5 | 0.20 | 1.10 |
| **Composite** | | | **7.4** |

**CVSS Vector**: `CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H`

**Scoring Rationale**:
- **CVSS**: 7.5 -- Remote flooding over HTTPS (AV:N). Simple high-volume submission (AC:L). No authentication needed (PR:N). No user interaction (UI:N). Scope Unchanged: DoS affects the Guardrails Service and its direct consumers. No data exposure or modification; high availability impact from CPU exhaustion.
- **Exploitability**: 8.5 -- HTTP flooding and ReDoS are well-known techniques (Known: 9). Simple high-volume submission; ReDoS payloads are straightforward (Complexity: 9). Many flooding tools freely available (Tooling: 8). Low skill required; script-kiddie tools available (Skill: 8).
- **Scalability**: 7.8 -- Trivially automatable with scripts or tools (Scriptability: 9). Affects all system users when Guardrails is down (Scope: 7). Moderate bandwidth for volumetric; minimal for ReDoS (Resources: 7). Volumetric DoS detectable but ReDoS payloads blend with normal traffic (Detection: 8).
- **Reachability**: 5.5 -- Guardrails Service resides in the Semi-Trusted Application Zone (baseline 5.5). Entry point for user traffic but sits behind the application boundary.

---

### D-2 -- LLM Agent Orchestrator

**Threat**: Attacker sends concurrent requests with maximum-length prompts to the Orchestrator, exhausting LLM inference compute budget and memory, blocking legitimate requests, because no per-client rate limit or token budget cap is enforced

**Category**: Denial of Service | **Original Risk Level**: Critical | **Composite**: 7.3 (High)

| Dimension | Score | Weight | Weighted |
|-----------|-------|--------|----------|
| CVSS Base | 7.5 | 0.35 | 2.63 |
| Exploitability | 8.3 | 0.30 | 2.49 |
| Scalability | 7.5 | 0.15 | 1.13 |
| Reachability | 5.5 | 0.20 | 1.10 |
| **Composite** | | | **7.3** |

**CVSS Vector**: `CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H`

**Scoring Rationale**:
- **CVSS**: 7.5 -- Remote concurrent submission (AV:N). Simple max-length prompt submission (AC:L). No authentication needed (PR:N). No user interaction (UI:N). Scope Unchanged. High availability impact from compute and memory exhaustion.
- **Exploitability**: 8.3 -- LLM compute exhaustion via long prompts is documented in AI security research (Known: 9). Simple concurrent max-length submission (Complexity: 8). HTTP load testing tools readily available (Tooling: 8). Low skill; understanding of token limits sufficient (Skill: 8).
- **Scalability**: 7.5 -- Trivially automatable concurrent submission (Scriptability: 9). Affects all orchestrator users via shared compute (Scope: 7). Moderate bandwidth for concurrent max-length prompts (Resources: 6). Volumetric patterns may be detectable but max-length legitimate prompts exist (Detection: 8).
- **Reachability**: 5.5 -- LLM Agent Orchestrator resides in the Semi-Trusted Application Zone (baseline 5.5).

---

### S-3 -- LLM Agent Orchestrator

**Threat**: Attacker forges tool call requests to the MCP Tool Server by impersonating the LLM Agent Orchestrator, because the JSON-RPC channel between orchestrator and tool server lacks mutual authentication

**Category**: Spoofing | **Original Risk Level**: Critical | **Composite**: 7.2 (High)

| Dimension | Score | Weight | Weighted |
|-----------|-------|--------|----------|
| CVSS Base | 9.8 | 0.35 | 3.43 |
| Exploitability | 6.0 | 0.30 | 1.80 |
| Scalability | 5.5 | 0.15 | 0.83 |
| Reachability | 5.5 | 0.20 | 1.10 |
| **Composite** | | | **7.2** |

**CVSS Vector**: `CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:L`

**Scoring Rationale**:
- **CVSS**: 9.8 -- Forged JSON-RPC requests over the network (AV:N). No mutual auth means no special conditions (AC:L). No credentials needed (PR:N). No user interaction (UI:N). Scope Changed: forged calls affect tool server, external API, and data stores. High CIA from data exfiltration (C:H), state modification (I:H), with limited availability impact (A:L).
- **Exploitability**: 6.0 -- Service impersonation via unauthenticated channels is known (Known: 6). Requires network access to internal JSON-RPC channel (Complexity: 6). JSON-RPC clients and network tools exist (Tooling: 6). Moderate skill for protocol and topology knowledge (Skill: 6).
- **Scalability**: 5.5 -- Scriptable once protocol format is understood (Scriptability: 7). Limited to attackers with internal network access (Scope: 4). Minimal resources once positioned (Resources: 7). Unauthenticated requests from unexpected sources are detectable (Detection: 4).
- **Reachability**: 5.5 -- LLM Agent Orchestrator resides in the Semi-Trusted Application Zone (baseline 5.5). JSON-RPC channel is internal.

---

### T-3 -- MCP Tool Server

**Threat**: Attacker manipulates JSON-RPC tool call parameters in transit between the Orchestrator and MCP Tool Server, injecting malicious payloads such as SQL fragments or shell commands into tool arguments, because parameter integrity is not verified at the tool server boundary

**Category**: Tampering | **Original Risk Level**: Critical | **Composite**: 7.1 (High)

| Dimension | Score | Weight | Weighted |
|-----------|-------|--------|----------|
| CVSS Base | 8.8 | 0.35 | 3.08 |
| Exploitability | 6.8 | 0.30 | 2.04 |
| Scalability | 5.8 | 0.15 | 0.87 |
| Reachability | 5.5 | 0.20 | 1.10 |
| **Composite** | | | **7.1** |

**CVSS Vector**: `CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:H/A:H`

**Scoring Rationale**:
- **CVSS**: 8.8 -- Network-level parameter manipulation (AV:N). Injection into unprotected JSON-RPC parameters is straightforward (AC:L). No auth needed for transit interception (PR:N). No user interaction (UI:N). Scope Unchanged: injected commands execute in tool server context. Low confidentiality (SQL may expose some data), high integrity (data modification, config corruption), high availability (shell commands can crash services).
- **Exploitability**: 6.8 -- SQL and command injection are extensively documented (Known: 8). Requires network-level access for interception (Complexity: 6). SQLMap, Burp Suite available (Tooling: 8). Moderate skill for JSON-RPC structure and payload crafting (Skill: 5).
- **Scalability**: 5.8 -- Parameter injection automatable with network interception setup (Scriptability: 6). Limited to specific orchestrator-server pairs (Scope: 5). Minimal resources once positioned (Resources: 7). Injected payloads may be detected by WAF/IDS (Detection: 5).
- **Reachability**: 5.5 -- MCP Tool Server resides in the Semi-Trusted Application Zone (baseline 5.5). Internal JSON-RPC channel.

---

### AG-3 -- MCP Tool Server

**Threat**: MCP Tool Server exposes all registered tools to every connected client (the LLM Agent Orchestrator) without per-agent capability scoping, violating the principle that agents should only access tools within their authorized capability set, because the tool registry does not enforce allowlists

**Category**: Agentic Threats | **Original Risk Level**: Critical | **Composite**: 7.0 (High)

| Dimension | Score | Weight | Weighted |
|-----------|-------|--------|----------|
| CVSS Base | 9.1 | 0.35 | 3.19 |
| Exploitability | 6.3 | 0.30 | 1.89 |
| Scalability | 5.5 | 0.15 | 0.83 |
| Reachability | 5.5 | 0.20 | 1.10 |
| **Composite** | | | **7.0** |

**CVSS Vector**: `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:L`

**Scoring Rationale**:
- **CVSS**: 9.1 -- Remote tool access via JSON-RPC (AV:N). All tools exposed by default (AC:L). Requires authenticated agent connection (PR:L). No user interaction (UI:N). Scope Changed: unrestricted tool access affects external APIs and data stores. High confidentiality and integrity from unauthorized tool access; limited availability impact (A:L).
- **Exploitability**: 6.3 -- Overly permissive MCP tool registries are documented in AI security research (Known: 7). Requires understanding of tool registry and names (Complexity: 6). Limited specialized tooling (Tooling: 4). Moderate skill for MCP protocol and capabilities (Skill: 7).
- **Scalability**: 5.5 -- Tool invocation scriptable via JSON-RPC (Scriptability: 6). Affects all agent instances connected to MCP server (Scope: 5). Minimal resources (Resources: 8). Tool invocations outside expected capability set are detectable (Detection: 3).
- **Reachability**: 5.5 -- MCP Tool Server resides in the Semi-Trusted Application Zone (baseline 5.5).

---

### S-2 -- Guardrails Service

**Threat**: Attacker bypasses the Guardrails Service by directly accessing the LLM Agent Orchestrator endpoint, impersonating the Guardrails Service identity, because inter-service authentication between the Guardrails Service and Orchestrator is not enforced

**Category**: Spoofing | **Original Risk Level**: High | **Composite**: 6.7 (Medium)

| Dimension | Score | Weight | Weighted |
|-----------|-------|--------|----------|
| CVSS Base | 8.2 | 0.35 | 2.87 |
| Exploitability | 6.5 | 0.30 | 1.95 |
| Scalability | 5.0 | 0.15 | 0.75 |
| Reachability | 5.5 | 0.20 | 1.10 |
| **Composite** | | | **6.7** |

**CVSS Vector**: `CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:L/A:N`

**Scoring Rationale**:
- **CVSS**: 8.2 -- Direct network access to orchestrator (AV:N). No mutual auth means no special conditions (AC:L). No credentials needed (PR:N). No user interaction (UI:N). Scope Unchanged. High confidentiality from unfiltered orchestrator access; low integrity.
- **Exploitability**: 6.5 -- API gateway bypass is well-documented (Known: 7). Requires network access to internal endpoint (Complexity: 6). Standard HTTP clients work (Tooling: 7). Moderate skill for internal topology (Skill: 6).
- **Scalability**: 5.0 -- Scriptable once internal URL known (Scriptability: 6). Limited to internal network access (Scope: 4). Minimal resources (Resources: 7). Monitoring request origin at orchestrator can detect bypass (Detection: 3).
- **Reachability**: 5.5 -- Guardrails Service resides in the Semi-Trusted Application Zone (baseline 5.5).

---

### E-1 -- Guardrails Service

**Threat**: Attacker bypasses the Guardrails Service entirely by exploiting an alternate route to the LLM Agent Orchestrator (e.g., internal network access, API gateway misconfiguration), because authorization checks are only enforced at the Guardrails Service layer and not replicated at the Orchestrator

**Category**: Privilege Escalation | **Original Risk Level**: High | **Composite**: 6.6 (Medium)

| Dimension | Score | Weight | Weighted |
|-----------|-------|--------|----------|
| CVSS Base | 8.8 | 0.35 | 3.08 |
| Exploitability | 5.8 | 0.30 | 1.74 |
| Scalability | 4.8 | 0.15 | 0.72 |
| Reachability | 5.5 | 0.20 | 1.10 |
| **Composite** | | | **6.6** |

**CVSS Vector**: `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:L`

**Scoring Rationale**:
- **CVSS**: 8.8 -- Alternate route exploitation over network (AV:N). Misconfiguration or internal access exploitable without special conditions (AC:L). Some authenticated access needed (PR:L). No user interaction (UI:N). Scope Changed: bypass provides unfiltered access to orchestrator and downstream components. High CI, low A.
- **Exploitability**: 5.8 -- API gateway misconfiguration is documented (Known: 7). Requires discovery of alternate route (Complexity: 5). Network scanning and API discovery tools available (Tooling: 5). Moderate skill for recon and gateway understanding (Skill: 6).
- **Scalability**: 4.8 -- May require manual discovery but scriptable once found (Scriptability: 5). Limited to instances with specific misconfiguration (Scope: 4). Minimal resources once route identified (Resources: 7). Direct orchestrator access from unauthorized sources is detectable (Detection: 3).
- **Reachability**: 5.5 -- Guardrails Service resides in the Semi-Trusted Application Zone (baseline 5.5).

---

### D-3 -- MCP Tool Server

**Threat**: Attacker triggers resource exhaustion on the MCP Tool Server by causing the Orchestrator to issue a large number of concurrent tool calls, because no per-request tool call limit or concurrency cap is enforced on the tool execution path

**Category**: Denial of Service | **Original Risk Level**: High | **Composite**: 6.4 (Medium)

**Correlation Group**: CG-4 primary. Peer AG-4 inherits these scores.

| Dimension | Score | Weight | Weighted |
|-----------|-------|--------|----------|
| CVSS Base | 7.5 | 0.35 | 2.63 |
| Exploitability | 6.3 | 0.30 | 1.89 |
| Scalability | 5.5 | 0.15 | 0.83 |
| Reachability | 5.5 | 0.20 | 1.10 |
| **Composite** | | | **6.4** |

**CVSS Vector**: `CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H`

**Scoring Rationale**:
- **CVSS**: 7.5 -- Remote triggering via crafted prompts (AV:N). Crafting prompts for multiple tool calls is straightforward (AC:L). Unauthenticated requests may trigger cascades (PR:N). No user interaction (UI:N). Scope Unchanged. High availability impact from tool server overload.
- **Exploitability**: 6.3 -- Concurrent request DoS is well-documented (Known: 7). Requires understanding of prompt-to-tool-call mapping; indirect path (Complexity: 5). HTTP load testing tools available (Tooling: 7). Moderate skill for prompt crafting (Skill: 6).
- **Scalability**: 5.5 -- Prompt submission triggering cascades is automatable (Scriptability: 7). Affects all tool server consumers (Scope: 5). Minimal resources for prompt submission (Resources: 7). Anomalous tool call volume detectable (Detection: 3).
- **Reachability**: 5.5 -- MCP Tool Server resides in the Semi-Trusted Application Zone (baseline 5.5).

---

### AG-4 -- MCP Tool Server

**Threat**: Attacker manipulates the MCP Tool Server to chain individually authorized tool calls (e.g., database-query + file-export + network-send) to achieve data exfiltration that no single tool authorization would permit, because no cross-tool policy evaluates composite effects of sequential tool invocations

**Category**: Agentic Threats | **Original Risk Level**: High | **Composite**: 6.4 (Medium)

**Correlation Group**: Scores inherited from primary finding D-3 (CG-4).

| Dimension | Score | Weight | Weighted |
|-----------|-------|--------|----------|
| CVSS Base | 7.5 | 0.35 | 2.63 |
| Exploitability | 6.3 | 0.30 | 1.89 |
| Scalability | 5.5 | 0.15 | 0.83 |
| Reachability | 5.5 | 0.20 | 1.10 |
| **Composite** | | | **6.4** |

**CVSS Vector**: `CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H`

**Scoring Rationale**:
- **CVSS**: 7.5 -- Scores inherited from CG-4 primary D-3. Uncontrolled tool invocation enables both resource exhaustion and permission escalation.
- **Exploitability**: 6.3 -- Inherited from CG-4 primary D-3.
- **Scalability**: 5.5 -- Inherited from CG-4 primary D-3.
- **Reachability**: 5.5 -- MCP Tool Server resides in the Semi-Trusted Application Zone.

---

### T-4 -- Knowledge Base

**Threat**: Attacker injects malicious or misleading content into the Knowledge Base by exploiting write access through the orchestrator's data ingestion path, because input sanitization is not enforced before persisting data to the vector store

**Category**: Tampering | **Original Risk Level**: High | **Composite**: 6.3 (Medium)

**Correlation Group**: CG-1 primary. Peer LLM-2 inherits these scores.

| Dimension | Score | Weight | Weighted |
|-----------|-------|--------|----------|
| CVSS Base | 7.1 | 0.35 | 2.49 |
| Exploitability | 6.5 | 0.30 | 1.95 |
| Scalability | 5.3 | 0.15 | 0.80 |
| Reachability | 5.5 | 0.20 | 1.10 |
| **Composite** | | | **6.3** |

**CVSS Vector**: `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:L`

**Scoring Rationale**:
- **CVSS**: 7.1 -- Remote content injection via ingestion API (AV:N). No special conditions (AC:L). Authenticated user access needed (PR:L). No user interaction (UI:N). Scope Unchanged. No direct data exposure (C:N); high integrity impact from knowledge base poisoning (I:H); degraded response quality (A:L).
- **Exploitability**: 6.5 -- KB poisoning and indirect prompt injection via RAG are documented (Known: 7). Requires understanding of ingestion pipeline (Complexity: 6). Limited specialized tooling; custom scripts needed (Tooling: 6). Moderate skill for vector embeddings and RAG patterns (Skill: 7).
- **Scalability**: 5.3 -- Content injection automatable with ingestion format knowledge (Scriptability: 5). Affects all users retrieving poisoned documents (Scope: 6). Minimal resources (Resources: 7). Content integrity checks can detect injection (Detection: 3).
- **Reachability**: 5.5 -- Knowledge Base resides in the Semi-Trusted Application Zone (baseline 5.5).

---

### LLM-2 -- LLM Agent Orchestrator

**Threat**: Attacker exploits the RAG pipeline by injecting adversarial content into the Knowledge Base that, when retrieved by the Orchestrator during context retrieval, overrides system behavior -- causing the model to exfiltrate data from other retrieved documents or generate misleading responses (indirect prompt injection)

**Category**: LLM Threats | **Original Risk Level**: High | **Composite**: 6.3 (Medium)

**Correlation Group**: Scores inherited from primary finding T-4 (CG-1).

| Dimension | Score | Weight | Weighted |
|-----------|-------|--------|----------|
| CVSS Base | 7.1 | 0.35 | 2.49 |
| Exploitability | 6.5 | 0.30 | 1.95 |
| Scalability | 5.3 | 0.15 | 0.80 |
| Reachability | 5.5 | 0.20 | 1.10 |
| **Composite** | | | **6.3** |

**CVSS Vector**: `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:L`

**Scoring Rationale**:
- **CVSS**: 7.1 -- Scores inherited from CG-1 primary T-4. Data integrity compromise in the Knowledge Base enables both persistent data corruption and runtime prompt manipulation.
- **Exploitability**: 6.5 -- Inherited from CG-1 primary T-4.
- **Scalability**: 5.3 -- Inherited from CG-1 primary T-4.
- **Reachability**: 5.5 -- LLM Agent Orchestrator resides in the Semi-Trusted Application Zone.

---

### I-1 -- Guardrails Service

**Threat**: Guardrails Service returns detailed rejection reasons to the user that reveal internal filtering rules, regex patterns, or blocked keyword lists, enabling attackers to craft prompts that evade detection by understanding the filtering logic

**Category**: Information Disclosure | **Original Risk Level**: High | **Composite**: 6.2 (Medium)

| Dimension | Score | Weight | Weighted |
|-----------|-------|--------|----------|
| CVSS Base | 5.3 | 0.35 | 1.86 |
| Exploitability | 7.8 | 0.30 | 2.34 |
| Scalability | 6.0 | 0.15 | 0.90 |
| Reachability | 5.5 | 0.20 | 1.10 |
| **Composite** | | | **6.2** |

**CVSS Vector**: `CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N`

**Scoring Rationale**:
- **CVSS**: 5.3 -- Error messages returned via HTTPS (AV:N). Simply submit prompts triggering rejections (AC:L). Any user can trigger rejections (PR:N). No interaction needed (UI:N). Scope Unchanged. Low confidentiality (filtering rules exposed, not user data); low integrity (enables filter evasion); no availability impact.
- **Exploitability**: 7.8 -- Error message information leakage is a classic vulnerability (Known: 8). Simply sending prompts and reading rejections (Complexity: 9). Standard HTTP clients suffice (Tooling: 6). Low-to-moderate skill for reading error messages and inferring rules (Skill: 8).
- **Scalability**: 6.0 -- Automated prompt submission and rejection collection is trivially scriptable (Scriptability: 7). Affects all instances returning verbose rejections (Scope: 6). Minimal resources (Resources: 8). High volume of intentionally-rejected prompts detectable via rate analysis (Detection: 3).
- **Reachability**: 5.5 -- Guardrails Service resides in the Semi-Trusted Application Zone (baseline 5.5).

---

### T-2 -- LLM Agent Orchestrator

**Threat**: Attacker injects malicious content into the prompt context by tampering with the data flow between the Guardrails Service and the Orchestrator, because the validated prompt is not integrity-protected in transit between services

**Category**: Tampering | **Original Risk Level**: High | **Composite**: 6.1 (Medium)

| Dimension | Score | Weight | Weighted |
|-----------|-------|--------|----------|
| CVSS Base | 7.1 | 0.35 | 2.49 |
| Exploitability | 6.0 | 0.30 | 1.80 |
| Scalability | 5.0 | 0.15 | 0.75 |
| Reachability | 5.5 | 0.20 | 1.10 |
| **Composite** | | | **6.1** |

**CVSS Vector**: `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:L`

**Scoring Rationale**:
- **CVSS**: 7.1 -- MITM tampering on inter-service data flow (AV:N). No integrity protection means interception is straightforward (AC:L). Internal network access needed (PR:L). No user interaction (UI:N). Scope Unchanged. No data exposure; high integrity from altered orchestrator behavior; low availability from malformed prompts.
- **Exploitability**: 6.0 -- MITM on unprotected inter-service channels is documented (Known: 7). Requires network-level interception access (Complexity: 5). mitmproxy, Burp Suite available (Tooling: 7). Moderate skill for interception and protocol understanding (Skill: 5).
- **Scalability**: 5.0 -- Transit interception and modification automatable with proxy tools (Scriptability: 6). Limited to specific inter-service channel (Scope: 4). Minimal resources once positioned (Resources: 7). HMAC verification would detect; without it, harder (Detection: 3).
- **Reachability**: 5.5 -- LLM Agent Orchestrator resides in the Semi-Trusted Application Zone (baseline 5.5).

---

### D-4 -- Knowledge Base

**Threat**: Attacker exhausts Knowledge Base resources by triggering unbounded vector search queries with high-dimensional adversarial inputs designed to maximize computational cost, because search queries lack result limits and complexity bounds

**Category**: Denial of Service | **Original Risk Level**: Medium | **Composite**: 6.0 (Medium)

| Dimension | Score | Weight | Weighted |
|-----------|-------|--------|----------|
| CVSS Base | 7.5 | 0.35 | 2.63 |
| Exploitability | 5.3 | 0.30 | 1.59 |
| Scalability | 4.5 | 0.15 | 0.68 |
| Reachability | 5.5 | 0.20 | 1.10 |
| **Composite** | | | **6.0** |

**CVSS Vector**: `CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H`

**Scoring Rationale**:
- **CVSS**: 7.5 -- Adversarial queries submitted remotely (AV:N). Unbounded queries need no special conditions (AC:L). No per-query authentication (PR:N). No user interaction (UI:N). Scope Unchanged. High availability impact from vector search resource exhaustion.
- **Exploitability**: 5.3 -- Vector search DoS is an emerging concern (Known: 6). Requires crafting adversarial inputs; some ML knowledge helpful (Complexity: 5). Custom scripts needed (Tooling: 5). Moderate skill for vector search mechanics (Skill: 5).
- **Scalability**: 4.5 -- Adversarial query submission automatable once crafted (Scriptability: 6). Affects all KB consumers (Scope: 4). Moderate resources for crafting vector payloads (Resources: 5). Anomalous query complexity detectable (Detection: 3).
- **Reachability**: 5.5 -- Knowledge Base resides in the Semi-Trusted Application Zone (baseline 5.5).

---

### I-4 -- Knowledge Base

**Threat**: Knowledge Base returns full document contents including internal metadata, embedding vectors, and storage schema details in query responses, because field-level projection is not enforced on retrieval queries

**Category**: Information Disclosure | **Original Risk Level**: High | **Composite**: 5.9 (Medium)

| Dimension | Score | Weight | Weighted |
|-----------|-------|--------|----------|
| CVSS Base | 5.3 | 0.35 | 1.86 |
| Exploitability | 7.0 | 0.30 | 2.10 |
| Scalability | 5.5 | 0.15 | 0.83 |
| Reachability | 5.5 | 0.20 | 1.10 |
| **Composite** | | | **5.9** |

**CVSS Vector**: `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N`

**Scoring Rationale**:
- **CVSS**: 5.3 -- Query responses returned over network (AV:N). Normal queries trigger disclosure (AC:L). Authenticated access through orchestrator needed (PR:L). Automatic response (UI:N). Scope Unchanged. Embedding vectors and schema details are sensitive (C:H). No integrity or availability impact.
- **Exploitability**: 7.0 -- Over-disclosure in API responses is well-documented (Known: 7). Normal queries trigger it; no special technique (Complexity: 8). Standard API clients suffice (Tooling: 6). Low-to-moderate skill for recognizing valuable metadata (Skill: 7).
- **Scalability**: 5.5 -- Automated query and response parsing is trivially scriptable (Scriptability: 7). Affects all queries without projection (Scope: 5). Minimal resources (Resources: 7). Individual queries look normal; volume patterns detectable (Detection: 3).
- **Reachability**: 5.5 -- Knowledge Base resides in the Semi-Trusted Application Zone (baseline 5.5).

---

### T-1 -- Guardrails Service

**Threat**: Attacker modifies the validation rules or filtering configuration of the Guardrails Service at runtime, because configuration files are stored in a location writable by the application process without integrity verification

**Category**: Tampering | **Original Risk Level**: High | **Composite**: 5.8 (Medium)

| Dimension | Score | Weight | Weighted |
|-----------|-------|--------|----------|
| CVSS Base | 7.1 | 0.35 | 2.49 |
| Exploitability | 5.3 | 0.30 | 1.59 |
| Scalability | 4.3 | 0.15 | 0.65 |
| Reachability | 5.5 | 0.20 | 1.10 |
| **Composite** | | | **5.8** |

**CVSS Vector**: `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:L`

**Scoring Rationale**:
- **CVSS**: 7.1 -- Remote config modification via application process (AV:N). Writable configs accessible without special conditions (AC:L). Application-level access needed (PR:L). No user interaction (UI:N). Scope Unchanged. Modified rules bypass filtering (I:H); corrupted rules may cause errors (A:L).
- **Exploitability**: 5.3 -- Configuration tampering is a known pattern (Known: 6). Requires application-level filesystem access (Complexity: 5). Standard file access tools suffice (Tooling: 5). Moderate skill for rule format and access (Skill: 5).
- **Scalability**: 4.3 -- Scriptable but requires per-instance filesystem knowledge (Scriptability: 5). Affects only the specific instance (Scope: 3). Requires filesystem access (Resources: 6). Configuration integrity monitoring detects changes (Detection: 3).
- **Reachability**: 5.5 -- Guardrails Service resides in the Semi-Trusted Application Zone (baseline 5.5).

---

### S-4 -- MCP Tool Server

**Threat**: Attacker redirects the MCP Tool Server's outbound API requests to an attacker-controlled endpoint by spoofing DNS responses or compromising the External API's TLS certificate, because certificate pinning is not enforced on outbound HTTPS connections

**Category**: Spoofing | **Original Risk Level**: High | **Composite**: 5.7 (Medium)

| Dimension | Score | Weight | Weighted |
|-----------|-------|--------|----------|
| CVSS Base | 7.4 | 0.35 | 2.59 |
| Exploitability | 4.5 | 0.30 | 1.35 |
| Scalability | 4.3 | 0.15 | 0.65 |
| Reachability | 5.5 | 0.20 | 1.10 |
| **Composite** | | | **5.7** |

**CVSS Vector**: `CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:N`

**Scoring Rationale**:
- **CVSS**: 7.4 -- DNS spoofing/TLS compromise are network attacks (AV:N). Requires privileged network position or CA compromise (AC:H). No authenticated access needed (PR:N). No user interaction (UI:N). Scope Unchanged. Attacker receives all outbound data (C:H) and can return forged responses (I:H); no availability impact.
- **Exploitability**: 4.5 -- DNS spoofing and TLS interception are documented but require network position (Known: 7). Requires DNS infrastructure access or CA compromise (Complexity: 2). DNS spoofing tools exist (Tooling: 5). Significant skill for DNS and TLS manipulation (Skill: 4).
- **Scalability**: 4.3 -- DNS spoofing automatable but requires per-target setup (Scriptability: 4). Limited to instances using compromised DNS/CA (Scope: 3). Requires network infrastructure access (Resources: 5). Detectable with DNSSEC and certificate monitoring (Detection: 5).
- **Reachability**: 5.5 -- MCP Tool Server resides in the Semi-Trusted Application Zone (baseline 5.5).

---

### I-3 -- MCP Tool Server

**Threat**: MCP Tool Server forwards raw External API error responses to the Orchestrator without sanitization, potentially exposing third-party API keys, internal endpoint URLs, or authentication headers embedded in error payloads

**Category**: Information Disclosure | **Original Risk Level**: High | **Composite**: 5.6 (Medium)

| Dimension | Score | Weight | Weighted |
|-----------|-------|--------|----------|
| CVSS Base | 6.5 | 0.35 | 2.28 |
| Exploitability | 5.0 | 0.30 | 1.50 |
| Scalability | 5.0 | 0.15 | 0.75 |
| Reachability | 5.5 | 0.20 | 1.10 |
| **Composite** | | | **5.6** |

**CVSS Vector**: `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N`

**Scoring Rationale**:
- **CVSS**: 6.5 -- Unsanitized errors forwarded over network (AV:N). Triggering errors is straightforward (AC:L). Authenticated access through orchestrator needed (PR:L). Automatic forwarding (UI:N). Scope Unchanged. API keys, URLs, and auth headers are highly sensitive (C:H); no integrity or availability impact.
- **Exploitability**: 5.0 -- Unsanitized error forwarding is well-documented (Known: 7). Requires triggering specific error conditions (Complexity: 4). Standard API testing tools work (Tooling: 5). Moderate skill for understanding error contents (Skill: 4).
- **Scalability**: 5.0 -- Error-triggering calls automatable but require per-API understanding (Scriptability: 5). Affects all instances forwarding unsanitized errors (Scope: 5). Minimal resources (Resources: 7). Unusual error rates and sensitive data detectable (Detection: 3).
- **Reachability**: 5.5 -- MCP Tool Server resides in the Semi-Trusted Application Zone (baseline 5.5).

---

### I-2 -- LLM Agent Orchestrator

**Threat**: LLM Agent Orchestrator leaks sensitive internal state through verbose error messages when tool calls fail or context retrieval errors occur, exposing internal service topology, Knowledge Base schema details, or model configuration parameters

**Category**: Information Disclosure | **Original Risk Level**: High | **Composite**: 5.5 (Medium)

| Dimension | Score | Weight | Weighted |
|-----------|-------|--------|----------|
| CVSS Base | 6.5 | 0.35 | 2.28 |
| Exploitability | 4.8 | 0.30 | 1.44 |
| Scalability | 4.5 | 0.15 | 0.68 |
| Reachability | 5.5 | 0.20 | 1.10 |
| **Composite** | | | **5.5** |

**CVSS Vector**: `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N`

**Scoring Rationale**:
- **CVSS**: 6.5 -- Error messages returned via HTTPS (AV:N). Malformed or edge-case inputs trigger verbose errors (AC:L). Authenticated user access needed (PR:L). Automatic error responses (UI:N). Scope Unchanged. Service topology, KB schema, and model config are highly sensitive (C:H).
- **Exploitability**: 4.8 -- Verbose error exploitation is a classic technique (Known: 7). Requires triggering specific error conditions; not all inputs produce verbose errors (Complexity: 5). API testing and fuzzing tools available (Tooling: 4). Moderate skill for error handling patterns (Skill: 3).
- **Scalability**: 4.5 -- Error-triggering inputs automatable via fuzzing (Scriptability: 6). Affects all instances with verbose error handling (Scope: 4). Minimal resources (Resources: 6). High error rates from single client detectable (Detection: 2).
- **Reachability**: 5.5 -- LLM Agent Orchestrator resides in the Semi-Trusted Application Zone (baseline 5.5).

---

### T-5 -- Audit Logger

**Threat**: Attacker modifies or deletes audit log entries to cover tracks after a security incident, because the Audit Logger stores logs in a location writable by application processes that also generate the logs

**Category**: Tampering | **Original Risk Level**: High | **Composite**: 5.4 (Medium)

| Dimension | Score | Weight | Weighted |
|-----------|-------|--------|----------|
| CVSS Base | 7.1 | 0.35 | 2.49 |
| Exploitability | 4.3 | 0.30 | 1.29 |
| Scalability | 3.5 | 0.15 | 0.53 |
| Reachability | 5.5 | 0.20 | 1.10 |
| **Composite** | | | **5.4** |

**CVSS Vector**: `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:L`

**Scoring Rationale**:
- **CVSS**: 7.1 -- Remote log modification via application processes (AV:N). Writable log store accessible via same processes (AC:L). Application-level access needed (PR:L). No user interaction (UI:N). Scope Unchanged. Destroyed forensic evidence (I:H); compliance disruption (A:L).
- **Exploitability**: 4.3 -- Log tampering is a documented post-exploitation technique (Known: 6). Requires application-level access; typically after initial compromise (Complexity: 4). Standard tools suffice (Tooling: 3). Moderate skill for log format and access (Skill: 4).
- **Scalability**: 3.5 -- Log modification scripts simple but need per-instance knowledge (Scriptability: 4). Limited to specific log store instance (Scope: 2). Minimal resources with app access (Resources: 6). Hash chains and SIEM comparison detect tampering (Detection: 2).
- **Reachability**: 5.5 -- Audit Logger resides in the Semi-Trusted Application Zone (baseline 5.5).

---

### D-5 -- Audit Logger

**Threat**: Attacker causes audit log storage exhaustion by triggering high-volume logging events through rapid request submission, eventually filling disk and disrupting all services that depend on log writing, because no log volume throttling or storage quota is enforced

**Category**: Denial of Service | **Original Risk Level**: Medium | **Composite**: 5.3 (Medium)

| Dimension | Score | Weight | Weighted |
|-----------|-------|--------|----------|
| CVSS Base | 5.3 | 0.35 | 1.86 |
| Exploitability | 5.3 | 0.30 | 1.59 |
| Scalability | 5.0 | 0.15 | 0.75 |
| Reachability | 5.5 | 0.20 | 1.10 |
| **Composite** | | | **5.3** |

**CVSS Vector**: `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H`

**Scoring Rationale**:
- **CVSS**: 5.3 -- Remote rapid submission (AV:N). High-volume submission needs no special conditions (AC:L). Authenticated access needed (PR:L). No user interaction (UI:N). Scope Unchanged. High availability impact from disk exhaustion affecting dependent services.
- **Exploitability**: 5.3 -- Log flooding is a documented DoS technique (Known: 6). Requires sustained high-volume submission; indirect path (Complexity: 5). HTTP load testing tools available (Tooling: 6). Low skill for high-volume submission (Skill: 4).
- **Scalability**: 5.0 -- Rapid submission trivially automatable (Scriptability: 7). Affects all services on shared log store (Scope: 4). Moderate resources for sustained volume (Resources: 5). Rapid log growth detectable with monitoring (Detection: 4).
- **Reachability**: 5.5 -- Audit Logger resides in the Semi-Trusted Application Zone (baseline 5.5).

---

### R-3 -- LLM Agent Orchestrator

**Threat**: LLM Agent Orchestrator executes tool calls and generates responses without logging the full decision chain, enabling operators or users to deny that specific actions were requested or authorized, because decision logs lack the originating user context, selected tool, parameters, and model reasoning trace

**Category**: Repudiation | **Original Risk Level**: High | **Composite**: 5.2 (Medium)

**Correlation Group**: CG-3 primary. Peer AG-2 inherits these scores.

| Dimension | Score | Weight | Weighted |
|-----------|-------|--------|----------|
| CVSS Base | 5.3 | 0.35 | 1.86 |
| Exploitability | 5.0 | 0.30 | 1.50 |
| Scalability | 5.0 | 0.15 | 0.75 |
| Reachability | 5.5 | 0.20 | 1.10 |
| **Composite** | | | **5.2** |

**CVSS Vector**: `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N`

**Scoring Rationale**:
- **CVSS**: 5.3 -- Repudiation exploited remotely (AV:N). Insufficient logging is a default condition (AC:L). Authenticated user access needed (PR:L). No interaction needed (UI:N). Scope Unchanged. Inability to prove attribution undermines audit trail integrity (I:H).
- **Exploitability**: 5.0 -- Repudiation is less of a technical attack; more an accountability gap (Known: 5). Trivially exploited: perform actions and deny them (Complexity: 7). No specialized tooling needed (Tooling: 2). Anyone can deny actions when logging is insufficient (Skill: 6).
- **Scalability**: 5.0 -- Per-incident manual exploit; not scriptable in traditional sense (Scriptability: 3). Affects all orchestrator users; any action can be denied (Scope: 6). No resources needed beyond existing access (Resources: 9). Insufficient logging is the vulnerability itself (Detection: 3).
- **Reachability**: 5.5 -- LLM Agent Orchestrator resides in the Semi-Trusted Application Zone (baseline 5.5).

---

### AG-2 -- LLM Agent Orchestrator

**Threat**: LLM Agent Orchestrator operates in an unbounded reasoning loop where the LLM decides when to terminate based on its assessment of task completion, but no maximum iteration count, execution timeout, or cost cap constrains the loop, enabling an attacker to submit ambiguous prompts that cause indefinite resource consumption

**Category**: Agentic Threats | **Original Risk Level**: High | **Composite**: 5.2 (Medium)

**Correlation Group**: Scores inherited from primary finding R-3 (CG-3).

| Dimension | Score | Weight | Weighted |
|-----------|-------|--------|----------|
| CVSS Base | 5.3 | 0.35 | 1.86 |
| Exploitability | 5.0 | 0.30 | 1.50 |
| Scalability | 5.0 | 0.15 | 0.75 |
| Reachability | 5.5 | 0.20 | 1.10 |
| **Composite** | | | **5.2** |

**CVSS Vector**: `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N`

**Scoring Rationale**:
- **CVSS**: 5.3 -- Scores inherited from CG-3 primary R-3. Missing accountability controls combined with unconstrained operation create unauditable behavior.
- **Exploitability**: 5.0 -- Inherited from CG-3 primary R-3.
- **Scalability**: 5.0 -- Inherited from CG-3 primary R-3.
- **Reachability**: 5.5 -- LLM Agent Orchestrator resides in the Semi-Trusted Application Zone.

---

### I-5 -- Audit Logger

**Threat**: Audit log entries contain sensitive data including full prompt content, user PII, and API credentials that were logged for debugging purposes, and the log store is accessible to operations staff beyond the security team

**Category**: Information Disclosure | **Original Risk Level**: High | **Composite**: 5.1 (Medium)

| Dimension | Score | Weight | Weighted |
|-----------|-------|--------|----------|
| CVSS Base | 6.5 | 0.35 | 2.28 |
| Exploitability | 4.0 | 0.30 | 1.20 |
| Scalability | 3.8 | 0.15 | 0.57 |
| Reachability | 5.5 | 0.20 | 1.10 |
| **Composite** | | | **5.1** |

**CVSS Vector**: `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N`

**Scoring Rationale**:
- **CVSS**: 6.5 -- Remote log access by operations staff (AV:N). Reading embedded sensitive data needs no special technique (AC:L). Operations staff access sufficient (PR:L). No additional interaction (UI:N). Scope Unchanged. Full prompt content, PII, and API credentials are highly sensitive (C:H).
- **Exploitability**: 4.0 -- Excessive logging of sensitive data is documented (Known: 6). Requires ops account access or compromise (Complexity: 4). Standard log viewing tools suffice (Tooling: 3). Low skill for authorized ops staff; moderate to compromise access (Skill: 3).
- **Scalability**: 3.8 -- Log scraping automatable with regex patterns (Scriptability: 5). Limited to specific log store and authorized readers (Scope: 3). Requires ops-level access (Resources: 5). Log access auditing detects unusual patterns (Detection: 2).
- **Reachability**: 5.5 -- Audit Logger resides in the Semi-Trusted Application Zone (baseline 5.5).

---

### LLM-3 -- LLM Agent Orchestrator

**Threat**: Attacker systematically queries the Orchestrator's inference endpoint to extract a functional copy of the model through distillation, because the API returns rich response data without per-user query volume limits or query pattern monitoring

**Category**: LLM Threats | **Original Risk Level**: Medium | **Composite**: 5.0 (Medium)

| Dimension | Score | Weight | Weighted |
|-----------|-------|--------|----------|
| CVSS Base | 5.3 | 0.35 | 1.86 |
| Exploitability | 4.5 | 0.30 | 1.35 |
| Scalability | 4.8 | 0.15 | 0.72 |
| Reachability | 5.5 | 0.20 | 1.10 |
| **Composite** | | | **5.0** |

**CVSS Vector**: `CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:N/A:N`

**Scoring Rationale**:
- **CVSS**: 5.3 -- Remote systematic querying (AV:N). Requires systematic patterns and ML expertise (AC:H). Authenticated API access needed (PR:L). No interaction from others (UI:N). Scope Unchanged. Model IP theft is high confidentiality impact (C:H).
- **Exploitability**: 4.5 -- Model extraction is documented in academic research (Known: 6). Requires systematic query design and ML expertise (Complexity: 3). Academic tools exist; no off-the-shelf extraction tools (Tooling: 5). Moderate-to-high skill for effective distillation (Skill: 4).
- **Scalability**: 4.8 -- Systematic query submission is highly automatable (Scriptability: 7). Limited to specific model instance (Scope: 3). Significant query volume and ML compute needed (Resources: 4). Systematic patterns detectable with monitoring (Detection: 4).
- **Reachability**: 5.5 -- LLM Agent Orchestrator resides in the Semi-Trusted Application Zone (baseline 5.5).

---

### R-1 -- User

**Threat**: User denies having submitted a specific prompt that triggered a harmful or policy-violating response, because the system does not capture non-repudiable evidence linking the authenticated user identity to the specific prompt submission

**Category**: Repudiation | **Original Risk Level**: Medium | **Composite**: 4.8 (Medium)

| Dimension | Score | Weight | Weighted |
|-----------|-------|--------|----------|
| CVSS Base | 4.3 | 0.35 | 1.51 |
| Exploitability | 3.0 | 0.30 | 0.90 |
| Scalability | 3.0 | 0.15 | 0.45 |
| Reachability | 9.5 | 0.20 | 1.90 |
| **Composite** | | | **4.8** |

**CVSS Vector**: `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N`

**Scoring Rationale**:
- **CVSS**: 4.3 -- Remote denial of submitted prompts (AV:N). Repudiation gap exists by default (AC:L). Authenticated user access needed (PR:L). No interaction needed (UI:N). Scope Unchanged. Low integrity impact from attribution gaps (I:L).
- **Exploitability**: 3.0 -- Repudiation is a well-understood concept but not a technical exploit (Known: 3). Simply deny having submitted the prompt (Complexity: 5). No tooling needed (Tooling: 1). Minimal skill; understanding of accountability gaps helpful (Skill: 3).
- **Scalability**: 3.0 -- Per-incident manual claim; not automatable (Scriptability: 2). Individual user accountability; not system-wide (Scope: 2). No resources needed (Resources: 8). Repudiation claims are overt; issue is proving attribution (Detection: 0).
- **Reachability**: 9.5 -- User component resides in the Untrusted User Zone (baseline 9.0). "User" keyword adds +0.5 = 9.5. Directly accessible by external actors.

---

### R-5 -- External API

**Threat**: External API interactions lack correlation identifiers that link API calls back to the originating user request, creating accountability gaps when external service calls produce unexpected or harmful results

**Category**: Repudiation | **Original Risk Level**: Low | **Composite**: 4.6 (Medium)

| Dimension | Score | Weight | Weighted |
|-----------|-------|--------|----------|
| CVSS Base | 4.3 | 0.35 | 1.51 |
| Exploitability | 2.5 | 0.30 | 0.75 |
| Scalability | 2.8 | 0.15 | 0.42 |
| Reachability | 9.5 | 0.20 | 1.90 |
| **Composite** | | | **4.6** |

**CVSS Vector**: `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N`

**Scoring Rationale**:
- **CVSS**: 4.3 -- External API interactions over network (AV:N). Correlation gaps exist by default (AC:L). Authenticated access through orchestrator (PR:L). Automatic API calls (UI:N). Scope Unchanged. Attribution gaps undermine forensic accountability (I:L).
- **Exploitability**: 2.5 -- Correlation gap is more of an accountability weakness (Known: 3). Trigger API calls and exploit attribution gap afterward (Complexity: 4). No tooling needed (Tooling: 1). Minimal skill required (Skill: 2).
- **Scalability**: 2.8 -- Per-incident exploitation; not meaningfully scriptable (Scriptability: 2). Affects only external API interaction path (Scope: 2). Minimal resources beyond existing access (Resources: 6). Correlation gap is a known architectural weakness (Detection: 1).
- **Reachability**: 9.5 -- External API resides in the Untrusted External Services zone (baseline 9.0). "External" keyword adds +0.5 = 9.5.

---

### R-2 -- Guardrails Service

**Threat**: Guardrails Service fails to log rejected prompts with sufficient detail to reconstruct why a prompt was blocked, enabling disputes about whether legitimate prompts were incorrectly filtered, because filtering event logs lack the original prompt content, matched rule identifier, and confidence score

**Category**: Repudiation | **Original Risk Level**: Medium | **Composite**: 4.5 (Medium)

| Dimension | Score | Weight | Weighted |
|-----------|-------|--------|----------|
| CVSS Base | 4.3 | 0.35 | 1.51 |
| Exploitability | 4.3 | 0.30 | 1.29 |
| Scalability | 3.8 | 0.15 | 0.57 |
| Reachability | 5.5 | 0.20 | 1.10 |
| **Composite** | | | **4.5** |

**CVSS Vector**: `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N`

**Scoring Rationale**:
- **CVSS**: 4.3 -- Filtering disputes from remote interactions (AV:N). Insufficient logging is a default condition (AC:L). Authenticated user access needed (PR:L). No interaction (UI:N). Scope Unchanged. Inability to reconstruct decisions undermines accountability (I:L).
- **Exploitability**: 4.3 -- Insufficient audit logging is a documented compliance weakness (Known: 4). Submit a prompt and dispute the decision (Complexity: 6). No tooling needed (Tooling: 2). Minimal skill for understanding filtering behavior (Skill: 5).
- **Scalability**: 3.8 -- Per-incident disputes; not scriptable (Scriptability: 2). Affects all filtered prompts lacking detailed records (Scope: 4). No special resources (Resources: 7). Disputes are overt; issue is proving the decision (Detection: 2).
- **Reachability**: 5.5 -- Guardrails Service resides in the Semi-Trusted Application Zone (baseline 5.5).

---

### R-4 -- MCP Tool Server

**Threat**: MCP Tool Server executes tool operations including external API calls without recording the requesting orchestrator context, making it impossible to attribute tool executions to specific user requests in forensic investigations

**Category**: Repudiation | **Original Risk Level**: Medium | **Composite**: 4.3 (Medium)

| Dimension | Score | Weight | Weighted |
|-----------|-------|--------|----------|
| CVSS Base | 4.3 | 0.35 | 1.51 |
| Exploitability | 3.8 | 0.30 | 1.14 |
| Scalability | 3.5 | 0.15 | 0.53 |
| Reachability | 5.5 | 0.20 | 1.10 |
| **Composite** | | | **4.3** |

**CVSS Vector**: `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N`

**Scoring Rationale**:
- **CVSS**: 4.3 -- Tool execution over JSON-RPC (AV:N). Missing context is a default condition (AC:L). Authenticated access through orchestrator (PR:L). No interaction (UI:N). Scope Unchanged. Inability to attribute executions undermines forensics (I:L).
- **Exploitability**: 3.8 -- Insufficient attribution in microservices is a documented forensic weakness (Known: 4). Trigger tool executions that cannot be attributed (Complexity: 6). No tooling needed (Tooling: 2). Minimal skill for understanding attribution gaps (Skill: 3).
- **Scalability**: 3.5 -- Per-incident exploitation; limited scriptability (Scriptability: 3). Affects tool executions lacking context (Scope: 3). Minimal resources (Resources: 6). Attribution gap is a known architectural weakness (Detection: 2).
- **Reachability**: 5.5 -- MCP Tool Server resides in the Semi-Trusted Application Zone (baseline 5.5).

---

## 4. Governance Fields

Remediation tracking metadata for each scored finding. Default values are severity-driven and intended for manual override by security managers during risk review.

| ID | Severity | Owner | SLA | Disposition | Review Date |
|----|----------|-------|-----|-------------|-------------|
| LLM-1 | High | Unassigned | 7d | Mitigate | 2026-04-03 |
| S-1 | High | Unassigned | 7d | Mitigate | 2026-04-03 |
| E-2 | High | Unassigned | 7d | Mitigate | 2026-04-03 |
| AG-1 | High | Unassigned | 7d | Mitigate | 2026-04-03 |
| E-3 | High | Unassigned | 7d | Mitigate | 2026-04-03 |
| D-1 | High | Unassigned | 7d | Mitigate | 2026-04-03 |
| D-2 | High | Unassigned | 7d | Mitigate | 2026-04-03 |
| S-3 | High | Unassigned | 7d | Mitigate | 2026-04-03 |
| T-3 | High | Unassigned | 7d | Mitigate | 2026-04-03 |
| AG-3 | High | Unassigned | 7d | Mitigate | 2026-04-03 |
| S-2 | Medium | Unassigned | 30d | Review | 2026-04-26 |
| E-1 | Medium | Unassigned | 30d | Review | 2026-04-26 |
| D-3 | Medium | Unassigned | 30d | Review | 2026-04-26 |
| AG-4 | Medium | Unassigned | 30d | Review | 2026-04-26 |
| T-4 | Medium | Unassigned | 30d | Review | 2026-04-26 |
| LLM-2 | Medium | Unassigned | 30d | Review | 2026-04-26 |
| I-1 | Medium | Unassigned | 30d | Review | 2026-04-26 |
| T-2 | Medium | Unassigned | 30d | Review | 2026-04-26 |
| D-4 | Medium | Unassigned | 30d | Review | 2026-04-26 |
| I-4 | Medium | Unassigned | 30d | Review | 2026-04-26 |
| T-1 | Medium | Unassigned | 30d | Review | 2026-04-26 |
| S-4 | Medium | Unassigned | 30d | Review | 2026-04-26 |
| I-3 | Medium | Unassigned | 30d | Review | 2026-04-26 |
| I-2 | Medium | Unassigned | 30d | Review | 2026-04-26 |
| T-5 | Medium | Unassigned | 30d | Review | 2026-04-26 |
| D-5 | Medium | Unassigned | 30d | Review | 2026-04-26 |
| R-3 | Medium | Unassigned | 30d | Review | 2026-04-26 |
| AG-2 | Medium | Unassigned | 30d | Review | 2026-04-26 |
| I-5 | Medium | Unassigned | 30d | Review | 2026-04-26 |
| LLM-3 | Medium | Unassigned | 30d | Review | 2026-04-26 |
| R-1 | Medium | Unassigned | 30d | Review | 2026-04-26 |
| R-5 | Medium | Unassigned | 30d | Review | 2026-04-26 |
| R-2 | Medium | Unassigned | 30d | Review | 2026-04-26 |
| R-4 | Medium | Unassigned | 30d | Review | 2026-04-26 |

### Field Definitions

| Field | Description | Default |
|-------|-------------|---------|
| **ID** | Finding identifier matching Section 2. | Preserved from source threat model. |
| **Severity** | Severity band from composite score. | Critical (9.0-10.0), High (7.0-8.9), Medium (4.0-6.9), Low (0.0-3.9). |
| **Owner** | Responsible party for remediation or risk acceptance. | `Unassigned` -- populate during risk review. |
| **SLA** | Remediation deadline relative to scoring date. | Critical = 24 hours, High = 7 days, Medium = 30 days, Low = 90 days. |
| **Disposition** | Risk treatment decision. | Critical/High = `Mitigate`, Medium/Low = `Review`. Valid values: Mitigate, Review, Accept, Transfer. |
| **Review Date** | Date by which the disposition must be reviewed. | Scoring date + SLA duration (e.g., scoring on 2026-03-27 with 7d SLA = 2026-04-03). |

### Override Guidance

- **Owner**: Assign during remediation planning. Each finding should have a named owner before the SLA expires.
- **Disposition**: Change from default when a risk acceptance or transfer decision is made. Document the justification in your risk register.
  - `Accept` -- Risk is acknowledged and accepted at the current level. Requires documented justification and management approval.
  - `Transfer` -- Risk is transferred to a third party (e.g., insurance, vendor SLA). Document the transfer mechanism.
- **SLA**: Override when organizational policy defines different remediation windows. The default SLAs follow industry-standard baselines (24h/7d/30d/90d).
- **Review Date**: Automatically recalculates when SLA is overridden.

---

## 5. Scoring Methodology

This section documents the quantitative scoring model used to produce the risk scores in this report. All scores are derived from the threat findings identified during threat modeling and are intended to replace qualitative risk ratings with data-backed, reproducible numeric assessments.

### 5.1 Scoring Dimensions

Each threat finding is assessed across four independent dimensions, each producing a score on a 0.0 to 10.0 scale.

| Dimension | Weight | What It Measures |
|-----------|--------|------------------|
| **CVSS Base** | 35% | Intrinsic severity of the vulnerability using CVSS 3.1 base metrics: attack vector, attack complexity, privileges required, user interaction, scope, and confidentiality/integrity/availability impact. Each finding includes the full CVSS vector string for auditability. |
| **Exploitability** | 30% | Practical likelihood of exploitation based on known attack techniques, tooling availability, required skill level, and attack complexity. Higher scores indicate threats with well-documented exploit paths and readily available tooling. |
| **Scalability** | 15% | Potential for automated, large-scale exploitation based on scriptability, breadth of target scope, resource requirements for the attacker, and difficulty of detection. Higher scores indicate threats that can be weaponized across many targets with minimal effort. |
| **Reachability** | 20% | Exposure of the targeted component within the system's trust boundary architecture. Derived from trust zone data in the threat model and supplemented by architecture documentation when available. Higher scores indicate components directly exposed to untrusted networks. |

### 5.2 Default Weights and Rationale

The default weight allocation reflects the following priorities:

- **CVSS Base (35%)** receives the highest weight because intrinsic vulnerability severity is the strongest predictor of potential damage. CVSS 3.1 is an industry-standard metric with well-understood interpretation.
- **Exploitability (30%)** is weighted second because a severe vulnerability that is difficult to exploit in practice poses less immediate risk than one with known, tooled attack paths.
- **Reachability (20%)** accounts for architectural context. A critical vulnerability behind multiple trust boundaries and authentication layers presents less operational risk than the same vulnerability on an internet-facing endpoint.
- **Scalability (15%)** receives the lowest weight because while automation potential increases aggregate risk, it is less deterministic than the other dimensions and often correlates with exploitability.

These weights are fixed for this scoring run and are recorded in the report frontmatter for reproducibility.

### 5.3 Composite Score Formula

The composite risk score for each finding is calculated as a weighted sum of the four dimension scores:

```
Composite = (0.35 x CVSS Base) + (0.30 x Exploitability) + (0.15 x Scalability) + (0.20 x Reachability)
```

The composite score is bounded to the 0.0-10.0 range. Because each dimension is independently scored on a 0.0-10.0 scale and the weights sum to 1.0, the composite inherently falls within this range.

### 5.4 Severity Band Mapping

Composite scores are mapped to severity bands that drive default governance actions:

| Severity | Composite Score Range | Default SLA | Default Disposition |
|----------|-----------------------|-------------|---------------------|
| **Critical** | 9.0 -- 10.0 | 24 hours | Mitigate |
| **High** | 7.0 -- 8.9 | 7 days | Mitigate |
| **Medium** | 4.0 -- 6.9 | 30 days | Review |
| **Low** | 0.0 -- 3.9 | 90 days | Review |

Boundary values map to the higher band (e.g., a composite score of exactly 7.0 maps to High, not Medium). These bands are aligned with the severity classifications defined in `schemas/output.yaml` to maintain backward compatibility with existing tachi threat model output.

### 5.5 Data Sources

Scoring draws on the following inputs:

- **Threat findings**: Parsed from `threats.md` (markdown table format) or `threats.sarif` (SARIF 2.1.0 JSON). All original threat metadata (ID, component, category, description, likelihood, impact) is preserved through the scoring pipeline.
- **Trust zone data**: Extracted from `threats.md` Section 2 (trust zone table) as the primary source for reachability scoring. Components in Untrusted/External zones score 8.0-10.0 reachability; Semi-Trusted/Application zones score 4.0-7.0; Trusted/Internal zones score 1.0-4.0.
- **Architecture documentation**: When `architecture.md` is available, it provides supplementary context such as authentication barriers and network exposure details that refine the baseline reachability score derived from trust zones. No `architecture.md` was available for this scoring run.
- **Category default vectors**: CVSS 3.1 baseline vectors are defined per STRIDE threat category in `schemas/risk-scoring.yaml`. This includes tachi-specific defaults for AI threat categories (agentic and LLM) that lack standard CVSS mappings. Per-threat analysis may refine these baselines based on the specific threat description.

### 5.6 Reproducibility

Scoring is performed at LLM temperature 0 to maximize consistency. For the same threat model input, each dimension score is expected to be reproducible within a **+/- 0.5 tolerance** across runs. This tolerance reflects the inherent variability in LLM-based analysis and is considered acceptable for risk prioritization purposes.

Factors that may cause minor score variation between runs include model version updates and non-deterministic sampling behavior at temperature 0. The composite formula, weights, and severity band mappings are deterministic -- only the per-dimension LLM assessments carry the stated tolerance.
