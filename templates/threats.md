# Threat Model Report

<!--
  Canonical output template for tachi threat model reports.

  Schema version : 1.0
  Schema file    : schemas/output.yaml
  Contract       : specs/001-project-skeleton-interface/contracts/output-schema.md

  Producers      : Template engine (applying IR findings to output template)
  Consumers      : Integrators, SARIF export (F-006), downstream features

  Every generated threat model output MUST conform to this structure.
  All 7 sections are required. Sections must appear in the order listed.
-->

---

```yaml
---
schema_version: "1.0"
date: "YYYY-MM-DD"
input_format: "{detected or declared format}"
classification: "confidential"
---
```

**Frontmatter fields:**

| Field | Type | Description |
|-------|------|-------------|
| `schema_version` | string | Output schema version. Always `"1.0"` for this release. |
| `date` | string | ISO 8601 date when the threat model was generated. Format: `YYYY-MM-DD`. |
| `input_format` | string | Architecture input format that was analyzed. One of: `ascii`, `free-text`, `mermaid`, `plantuml`, `c4`. |
| `classification` | string | Data classification label for the report. Default: `confidential`. |

**Example frontmatter:**

```yaml
---
schema_version: "1.0"
date: "2026-03-21"
input_format: "mermaid"
classification: "confidential"
---
```

---

## 1. System Overview

Parsed summary of the architecture input including identified components, data flows, and technologies. This section establishes the scope of the threat model by enumerating everything that was analyzed.

### Components

List every component identified in the architecture input. Each component becomes a row in the Coverage Matrix (Section 5) and a potential target in the STRIDE and AI threat tables.

| Component | Type | Description |
|-----------|------|-------------|
| _{component name}_ | _{External Entity \| Process \| Data Store \| Data Flow}_ | _{brief description of the component's role}_ |

**Example:**

| Component | Type | Description |
|-----------|------|-------------|
| API Gateway | Process | Routes incoming HTTP requests to backend services and enforces rate limits |
| User Database | Data Store | PostgreSQL database storing user credentials and profile data |
| Mobile Client | External Entity | iOS/Android application that authenticates users and displays content |
| Auth Token Flow | Data Flow | JWT tokens passed from Auth Service to API Gateway on every request |
| LLM Agent | Process | Autonomous agent that processes natural-language queries using an LLM backend |

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

**Risk level computation (OWASP 3x3 matrix):**

| | LOW Likelihood | MEDIUM Likelihood | HIGH Likelihood |
|---|---|---|---|
| **HIGH Impact** | Medium | High | Critical |
| **MEDIUM Impact** | Low | Medium | High |
| **LOW Impact** | Note | Low | Medium |

### 3.1 Spoofing (S)

Threats where an attacker pretends to be something or someone else.

| ID | Component | Threat | Likelihood | Impact | Risk Level | Mitigation |
|----|-----------|--------|------------|--------|------------|------------|
| _{S-N}_ | _{component}_ | _{threat description}_ | _{LOW \| MEDIUM \| HIGH}_ | _{LOW \| MEDIUM \| HIGH}_ | _{risk from 3x3 matrix}_ | _{recommended countermeasure}_ |

**Example:**

| ID | Component | Threat | Likelihood | Impact | Risk Level | Mitigation |
|----|-----------|--------|------------|--------|------------|------------|
| S-1 | API Gateway | Attacker forges JWT tokens to impersonate authenticated users by exploiting weak signing algorithm | HIGH | HIGH | Critical | Enforce RS256 signing with key rotation every 90 days; reject HS256 tokens |

### 3.2 Tampering (T)

Threats where an attacker modifies data or code without authorization.

| ID | Component | Threat | Likelihood | Impact | Risk Level | Mitigation |
|----|-----------|--------|------------|--------|------------|------------|
| _{T-N}_ | _{component}_ | _{threat description}_ | _{LOW \| MEDIUM \| HIGH}_ | _{LOW \| MEDIUM \| HIGH}_ | _{risk from 3x3 matrix}_ | _{recommended countermeasure}_ |

**Example:**

| ID | Component | Threat | Likelihood | Impact | Risk Level | Mitigation |
|----|-----------|--------|------------|--------|------------|------------|
| T-1 | User Database | Attacker performs SQL injection through unsanitized input fields to modify user records | MEDIUM | HIGH | High | Use parameterized queries exclusively; apply input validation at API Gateway layer |

### 3.3 Repudiation (R)

Threats where an attacker denies having performed an action without the system being able to prove otherwise.

| ID | Component | Threat | Likelihood | Impact | Risk Level | Mitigation |
|----|-----------|--------|------------|--------|------------|------------|
| _{R-N}_ | _{component}_ | _{threat description}_ | _{LOW \| MEDIUM \| HIGH}_ | _{LOW \| MEDIUM \| HIGH}_ | _{risk from 3x3 matrix}_ | _{recommended countermeasure}_ |

**Example:**

| ID | Component | Threat | Likelihood | Impact | Risk Level | Mitigation |
|----|-----------|--------|------------|--------|------------|------------|
| R-1 | Auth Service | User denies performing privileged actions because audit logs do not capture sufficient session context | MEDIUM | MEDIUM | Medium | Implement immutable audit log with session ID, IP, user agent, and action timestamp for all privileged operations |

### 3.4 Information Disclosure (I)

Threats where sensitive data is exposed to unauthorized parties.

| ID | Component | Threat | Likelihood | Impact | Risk Level | Mitigation |
|----|-----------|--------|------------|--------|------------|------------|
| _{I-N}_ | _{component}_ | _{threat description}_ | _{LOW \| MEDIUM \| HIGH}_ | _{LOW \| MEDIUM \| HIGH}_ | _{risk from 3x3 matrix}_ | _{recommended countermeasure}_ |

**Example:**

| ID | Component | Threat | Likelihood | Impact | Risk Level | Mitigation |
|----|-----------|--------|------------|--------|------------|------------|
| I-1 | User Database | Database connection string with credentials exposed in application error messages returned to client | MEDIUM | HIGH | High | Implement structured error handling that returns generic error codes to clients; log detailed errors server-side only |

### 3.5 Denial of Service (D)

Threats where an attacker degrades or prevents legitimate access to the system.

| ID | Component | Threat | Likelihood | Impact | Risk Level | Mitigation |
|----|-----------|--------|------------|--------|------------|------------|
| _{D-N}_ | _{component}_ | _{threat description}_ | _{LOW \| MEDIUM \| HIGH}_ | _{LOW \| MEDIUM \| HIGH}_ | _{risk from 3x3 matrix}_ | _{recommended countermeasure}_ |

**Example:**

| ID | Component | Threat | Likelihood | Impact | Risk Level | Mitigation |
|----|-----------|--------|------------|--------|------------|------------|
| D-1 | API Gateway | Volumetric attack overwhelms the gateway with malformed requests, exhausting connection pool and blocking legitimate traffic | HIGH | MEDIUM | High | Enforce per-IP rate limiting (100 req/min); deploy upstream DDoS protection; implement circuit breaker pattern |

### 3.6 Elevation of Privilege (E)

Threats where an attacker gains higher access rights than authorized.

| ID | Component | Threat | Likelihood | Impact | Risk Level | Mitigation |
|----|-----------|--------|------------|--------|------------|------------|
| _{E-N}_ | _{component}_ | _{threat description}_ | _{LOW \| MEDIUM \| HIGH}_ | _{LOW \| MEDIUM \| HIGH}_ | _{risk from 3x3 matrix}_ | _{recommended countermeasure}_ |

**Example:**

| ID | Component | Threat | Likelihood | Impact | Risk Level | Mitigation |
|----|-----------|--------|------------|--------|------------|------------|
| E-1 | Auth Service | Attacker exploits insecure direct object reference (IDOR) to access admin endpoints by manipulating user role claims in JWT payload | MEDIUM | HIGH | High | Validate role claims server-side against authoritative user store on every request; never trust client-supplied role values |

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

| ID | Component | Threat | OWASP Reference | Likelihood | Impact | Risk Level | Mitigation |
|----|-----------|--------|------------------|------------|--------|------------|------------|
| _{AG-N}_ | _{component}_ | _{threat description}_ | _{OWASP ID or framework citation}_ | _{LOW \| MEDIUM \| HIGH}_ | _{LOW \| MEDIUM \| HIGH}_ | _{risk from 3x3 matrix}_ | _{recommended countermeasure}_ |

**Example:**

| ID | Component | Threat | OWASP Reference | Likelihood | Impact | Risk Level | Mitigation |
|----|-----------|--------|------------------|------------|--------|------------|------------|
| AG-1 | LLM Agent | Agent autonomously invokes destructive shell commands without human approval, causing data loss or system compromise | ASI-01 | MEDIUM | HIGH | High | Implement mandatory human-in-the-loop approval for all destructive operations; enforce tool allowlists with per-tool permission scopes |

### 4.2 LLM Threats (LLM)

Threats targeting the LLM itself, including prompt injection, training data poisoning, model theft, and insecure output handling.

| ID | Component | Threat | OWASP Reference | Likelihood | Impact | Risk Level | Mitigation |
|----|-----------|--------|------------------|------------|--------|------------|------------|
| _{LLM-N}_ | _{component}_ | _{threat description}_ | _{OWASP ID or framework citation}_ | _{LOW \| MEDIUM \| HIGH}_ | _{LOW \| MEDIUM \| HIGH}_ | _{risk from 3x3 matrix}_ | _{recommended countermeasure}_ |

**Example:**

| ID | Component | Threat | OWASP Reference | Likelihood | Impact | Risk Level | Mitigation |
|----|-----------|--------|------------------|------------|--------|------------|------------|
| LLM-1 | LLM Agent | Indirect prompt injection via user-supplied documents causes the agent to exfiltrate sensitive context data to an attacker-controlled endpoint | OWASP LLM01:2025 | HIGH | HIGH | Critical | Sanitize all user-supplied input before inclusion in LLM context; implement output filtering to block URLs and data patterns matching exfiltration; apply egress network controls |

---

## 5. Coverage Matrix

Cross-reference matrix showing which components were analyzed for which threat categories. Each cell contains the count of findings identified for that component-category pair. A dash (`-`) indicates no findings were identified (the component was analyzed but no threats were found for that category).

| Component | S | T | R | I | D | E | AG | LLM | Total |
|-----------|---|---|---|---|---|---|----|-----|-------|
| _{component}_ | _{count}_ | _{count}_ | _{count}_ | _{count}_ | _{count}_ | _{count}_ | _{count}_ | _{count}_ | _{total}_ |

**Example:**

| Component | S | T | R | I | D | E | AG | LLM | Total |
|-----------|---|---|---|---|---|---|----|-----|-------|
| API Gateway | 1 | - | - | - | 1 | - | - | - | 2 |
| User Database | - | 1 | - | 1 | - | - | - | - | 2 |
| Auth Service | - | - | 1 | - | - | 1 | - | - | 2 |
| LLM Agent | - | - | - | - | - | - | 1 | 1 | 2 |
| **Total** | **1** | **1** | **1** | **1** | **1** | **1** | **1** | **1** | **8** |

---

## 6. Risk Summary

Aggregate counts of findings by risk level, computed using the OWASP 3x3 matrix (likelihood x impact). Provides a quick posture assessment.

**OWASP 3x3 risk matrix reference:**

| | LOW Likelihood | MEDIUM Likelihood | HIGH Likelihood |
|---|---|---|---|
| **HIGH Impact** | Medium | High | Critical |
| **MEDIUM Impact** | Low | Medium | High |
| **LOW Impact** | Note | Low | Medium |

| Risk Level | Count | Percentage |
|------------|-------|------------|
| Critical | _{count}_ | _{count / total * 100}%_ |
| High | _{count}_ | _{count / total * 100}%_ |
| Medium | _{count}_ | _{count / total * 100}%_ |
| Low | _{count}_ | _{count / total * 100}%_ |
| Note | _{count}_ | _{count / total * 100}%_ |
| **Total** | _{total}_ | **100%** |

**Example:**

| Risk Level | Count | Percentage |
|------------|-------|------------|
| Critical | 2 | 25% |
| High | 4 | 50% |
| Medium | 1 | 12.5% |
| Low | 1 | 12.5% |
| Note | 0 | 0% |
| **Total** | **8** | **100%** |

---

## 7. Recommended Actions

Prioritized list of all findings sorted by risk level descending, providing a remediation roadmap. Critical and High findings should be addressed before deployment. Medium findings should be addressed within the current development cycle. Low and Note findings should be tracked for future consideration.

| Finding ID | Component | Threat | Risk Level | Mitigation |
|------------|-----------|--------|------------|------------|
| _{finding ID}_ | _{component}_ | _{threat summary}_ | _{risk level}_ | _{recommended countermeasure}_ |

**Example:**

| Finding ID | Component | Threat | Risk Level | Mitigation |
|------------|-----------|--------|------------|------------|
| S-1 | API Gateway | Forged JWT tokens via weak signing algorithm | Critical | Enforce RS256 signing with key rotation every 90 days; reject HS256 tokens |
| LLM-1 | LLM Agent | Indirect prompt injection exfiltrating context data | Critical | Sanitize user input before LLM context; implement output filtering and egress controls |
| T-1 | User Database | SQL injection through unsanitized input | High | Use parameterized queries; apply input validation at API Gateway |
| I-1 | User Database | Credentials exposed in error messages | High | Structured error handling with generic client responses; server-side detailed logging |
| D-1 | API Gateway | Volumetric attack exhausting connection pool | High | Per-IP rate limiting; upstream DDoS protection; circuit breaker pattern |
| E-1 | Auth Service | IDOR exploiting role claims in JWT payload | High | Server-side role validation against authoritative store on every request |
| AG-1 | LLM Agent | Uncontrolled destructive command execution | High | Human-in-the-loop approval for destructive operations; tool allowlists |
| R-1 | Auth Service | Insufficient audit logging for privileged actions | Medium | Immutable audit log with session ID, IP, user agent, and timestamp |
