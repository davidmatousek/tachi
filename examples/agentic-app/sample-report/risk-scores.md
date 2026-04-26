---
schema_version: "1.0"
date: "2026-04-25"
source_file: "examples/agentic-app/test-output/2026-04-26T03-39-12-F3-wave3/threats.md"
classification: "confidential"
scoring_weights:
  cvss_base: 0.35
  exploitability: 0.30
  scalability: 0.15
  reachability: 0.20
---

# Risk Scores — Agentic AI Application (F-3 Wave 3)

## 1. Executive Summary

**Total findings scored**: 84 (9 Spoofing · 9 Tampering · 9 Repudiation · 9 Information Disclosure · 9 Denial of Service · 7 Privilege Escalation · 8 Agentic Threats · 14 LLM Threats · 4 Output Integrity · 3 Misinformation · 1 Agentic Pattern · 1 NEW: AG-8)

### Severity Band Distribution

| Severity Band | Count | Percentage |
|---------------|------:|----------:|
| Critical | 0 | 0% |
| High | 17 | 20% |
| Medium | 67 | 80% |
| Low | 0 | 0% |

**Highest-risk component**: User (maximum composite score 8.2, finding S-1)

The portfolio remains dominated by Medium-severity findings (80%) with the same High-severity cluster of 17 findings as the baseline. The single new finding AG-8 (Insecure Inter-Agent Communication — OWASP ASI07:2026) enters as Medium severity with composite score 5.5, inheriting scores from correlation group primary D-4. No findings crossed the Critical composite threshold in this run; the Trusted Application Zone placement of all internal components (reachability 2.5) continues to moderate composite scores even when CVSS base and exploitability are high.

---

## 2. Scored Threat Table

| ID | Component | Threat | CVSS | Exploitability | Scalability | Reachability | Composite | Severity | SLA | Disposition |
|----|-----------|--------|-----:|---------------:|------------:|-------------:|----------:|----------|-----|-------------|
| S-1 | User | An attacker impersonates a legitimate user by ... | 8.2 | 8.0 | 6.8 | 9.5 | 8.2 | High | 7d | Mitigate |
| AG-1 | LLM Agent Orchestrator | Prompt injection causes the Orchestrator to au... | 10.0 | 8.8 | 7.5 | 2.5 | 7.8 | High | 7d | Mitigate |
| E-2 | LLM Agent Orchestrator | The Orchestrator has privileged access to the ... | 10.0 | 8.8 | 7.5 | 2.5 | 7.8 | High | 7d | Mitigate |
| R-3 | LLM Agent Orchestrator | The Orchestrator denies having issued a specif... | 10.0 | 8.8 | 7.5 | 2.5 | 7.8 | High | 7d | Mitigate |
| E-1 | Guardrails Service | A prompt injection attack that bypasses the Gu... | 10.0 | 8.8 | 7.3 | 2.5 | 7.7 | High | 7d | Mitigate |
| LLM-6 | LLM Agent Orchestrator | Improper output handling — server-side executi... | 10.0 | 8.8 | 7.3 | 2.5 | 7.7 | High | 7d | Mitigate |
| OI-2 | LLM Agent Orchestrator | Improper output handling — server-side executi... | 10.0 | 8.8 | 7.3 | 2.5 | 7.7 | High | 7d | Mitigate |
| LLM-5 | LLM Agent Orchestrator | Improper output handling — client-side XSS via... | 9.3 | 8.8 | 7.3 | 2.5 | 7.5 | High | 7d | Mitigate |
| OI-1 | LLM Agent Orchestrator | Improper output handling — client-side XSS via... | 9.3 | 8.8 | 7.3 | 2.5 | 7.5 | High | 7d | Mitigate |
| LLM-13 | Clinical Advisory Sub-Agent | Prompt injection via clinical query context: t... | 9.3 | 8.8 | 7.0 | 2.5 | 7.4 | High | 7d | Mitigate |
| LLM-8 | Specialist Agent | Prompt injection via delegation messages: the ... | 9.3 | 8.3 | 6.8 | 2.5 | 7.3 | High | 7d | Mitigate |
| I-2 | LLM Agent Orchestrator | The Orchestrator's context window contains sen... | 8.6 | 8.8 | 7.3 | 2.5 | 7.2 | High | 7d | Mitigate |
| LLM-1 | LLM Agent Orchestrator | Direct prompt injection via the User→Guardrail... | 8.6 | 8.8 | 7.3 | 2.5 | 7.2 | High | 7d | Mitigate |
| LLM-4 | LLM Agent Orchestrator | Training data poisoning via the Long-Running L... | 10.0 | 7.0 | 6.5 | 2.5 | 7.1 | High | 7d | Mitigate |
| T-2 | LLM Agent Orchestrator | The Orchestrator's context window (system prom... | 10.0 | 7.0 | 6.5 | 2.5 | 7.1 | High | 7d | Mitigate |
| E-5 | MCP Tool Server | The MCP Tool Server executes tools with creden... | 9.9 | 7.0 | 6.5 | 2.5 | 7.0 | High | 7d | Mitigate |
| T-5 | MCP Tool Server | Tool call request parameters supplied by agent... | 9.9 | 7.0 | 6.5 | 2.5 | 7.0 | High | 7d | Mitigate |
| AG-5 | MCP Tool Server | The MCP Tool Server is vulnerable to tool call... | 9.4 | 7.0 | 6.5 | 2.5 | 6.9 | Medium | 30d | Review |
| E-7 | Clinical Advisory Sub-Agent | The Clinical Advisory Sub-Agent operates with ... | 9.9 | 6.8 | 6.0 | 2.5 | 6.9 | Medium | 30d | Review |
| I-9 | Clinical Advisory Sub-Agent | The Clinical Advisory Sub-Agent processes clin... | 8.6 | 7.8 | 6.5 | 2.5 | 6.8 | Medium | 30d | Review |
| LLM-2 | LLM Agent Orchestrator | Indirect prompt injection via the Knowledge Ba... | 10.0 | 6.0 | 6.8 | 2.5 | 6.8 | Medium | 30d | Review |
| D-1 | Guardrails Service | The Guardrails Service is vulnerable to resour... | 7.5 | 8.5 | 7.0 | 2.5 | 6.7 | Medium | 30d | Review |
| LLM-7 | LLM Agent Orchestrator | Improper output handling — SSRF via LLM-synthe... | 8.6 | 7.0 | 6.5 | 2.5 | 6.6 | Medium | 30d | Review |
| LLM-14 | Clinical Advisory Sub-Agent | Training data poisoning of the Clinical Adviso... | 9.9 | 6.0 | 5.8 | 2.5 | 6.6 | Medium | 30d | Review |
| MI-2 | Clinical Advisory Sub-Agent | Overreliance / Missing HITL on Decision-Critic... | 8.7 | 7.0 | 6.3 | 2.5 | 6.6 | Medium | 30d | Review |
| T-9 | Clinical Advisory Sub-Agent | The Clinical Advisory Sub-Agent's context wind... | 9.9 | 6.0 | 5.8 | 2.5 | 6.6 | Medium | 30d | Review |
| LLM-10 | Specialist Agent | Improper output handling — server-side injecti... | 9.3 | 6.0 | 6.0 | 2.5 | 6.5 | Medium | 30d | Review |
| MI-1 | Clinical Advisory Sub-Agent | Ungrounded Factual Emission (Category 1 per FR... | 8.7 | 7.0 | 6.0 | 2.5 | 6.5 | Medium | 30d | Review |
| MI-3 | Clinical Advisory Sub-Agent | Retrieval-Grounding Gap (Category 4 per FR-017... | 8.7 | 6.8 | 6.0 | 2.5 | 6.5 | Medium | 30d | Review |
| OI-3 | LLM Agent Orchestrator | Improper output handling — SSRF via LLM-synthe... | 8.6 | 6.8 | 6.5 | 2.5 | 6.5 | Medium | 30d | Review |
| E-3 | Specialist Agent | The Specialist Agent receives delegated permis... | 9.9 | 5.5 | 5.5 | 2.5 | 6.4 | Medium | 30d | Review |
| E-4 | Inter-Agent Communication Channel | If the Channel does not enforce sender authent... | 9.9 | 5.5 | 5.5 | 2.5 | 6.4 | Medium | 30d | Review |
| S-5 | Inter-Agent Communication Channel | The Channel is a shared message routing substr... | 9.3 | 5.8 | 5.8 | 2.5 | 6.4 | Medium | 30d | Review |
| S-7 | Long-Running Learning Loop | The Learning Loop accepts a Training Signal St... | 9.9 | 5.0 | 6.3 | 2.5 | 6.4 | Medium | 30d | Review |
| AG-3 | Specialist Agent | The Specialist Agent, once delegated a task, o... | 9.4 | 5.0 | 5.8 | 2.5 | 6.2 | Medium | 30d | Review |
| AG-6 | MCP Tool Server | The MCP Tool Server acts as a privileged execu... | 6.5 | 8.0 | 6.8 | 2.5 | 6.2 | Medium | 30d | Review |
| D-2 | LLM Agent Orchestrator | The Orchestrator's inference pipeline is a bou... | 6.5 | 8.0 | 7.0 | 2.5 | 6.2 | Medium | 30d | Review |
| D-5 | MCP Tool Server | The Tool Server's capacity for concurrent Exte... | 6.5 | 8.0 | 6.8 | 2.5 | 6.2 | Medium | 30d | Review |
| OI-4 | Clinical Advisory Sub-Agent | Improper output handling — server-side executi... | 8.8 | 5.8 | 6.0 | 2.5 | 6.2 | Medium | 30d | Review |
| R-1 | User | A user denies having submitted a particular pr... | 4.3 | 6.5 | 5.5 | 9.5 | 6.2 | Medium | 30d | Review |
| S-6 | MCP Tool Server | An attacker in the Application Zone spoofs a v... | 9.1 | 5.5 | 5.8 | 2.5 | 6.2 | Medium | 30d | Review |
| AG-2 | LLM Agent Orchestrator | The Orchestrator and Specialist Agent can joint... | 9.4 | 4.8 | 5.8 | 2.5 | 6.1 | Medium | 30d | Review |
| AG-4 | Inter-Agent Communication Channel | The Channel is a shared substrate whose compro... | 8.4 | 5.8 | 5.5 | 2.5 | 6.0 | Medium | 30d | Review |
| E-6 | Long-Running Learning Loop | The Learning Loop applies model updates with a... | 9.9 | 4.0 | 5.8 | 2.5 | 6.0 | Medium | 30d | Review |
| I-1 | Guardrails Service | The Guardrails Service leaks the content of re... | 5.3 | 7.3 | 7.0 | 2.5 | 5.6 | Medium | 30d | Review |
| S-3 | LLM Agent Orchestrator | The Orchestrator's identity is not cryptograph... | 8.2 | 5.5 | 5.8 | 2.5 | 5.9 | Medium | 30d | Review |
| T-3 | Specialist Agent | The Specialist Agent's operational context can... | 8.2 | 5.8 | 5.5 | 2.5 | 5.9 | Medium | 30d | Review |
| T-4 | Inter-Agent Communication Channel | Messages transiting the Inter-Agent Communicat... | 8.2 | 5.8 | 5.5 | 2.5 | 5.9 | Medium | 30d | Review |
| S-8 | External API | The External API provider's identity is not ve... | 7.4 | 4.3 | 4.5 | 6.0 | 5.8 | Medium | 30d | Review |
| S-9 | Clinical Advisory Sub-Agent | The Clinical Advisory Sub-Agent receives Clini... | 8.2 | 5.5 | 5.3 | 2.5 | 5.8 | Medium | 30d | Review |
| T-7 | Audit Logger | The Audit Logger entries can be tampered with ... | 8.5 | 5.0 | 5.3 | 2.5 | 5.8 | Medium | 30d | Review |
| AG-7 | Long-Running Learning Loop | The Learning Loop's model update mechanism, wh... | 8.5 | 4.0 | 6.0 | 2.5 | 5.6 | Medium | 30d | Review |
| D-9 | Clinical Advisory Sub-Agent | The Clinical Advisory Sub-Agent is invoked by ... | 6.5 | 6.5 | 6.0 | 2.5 | 5.6 | Medium | 30d | Review |
| LLM-9 | Specialist Agent | Training data poisoning of the Specialist Agen... | 8.5 | 4.3 | 5.8 | 2.5 | 5.6 | Medium | 30d | Review |
| D-6 | Knowledge Base | The Knowledge Base can be rendered unavailable... | 6.5 | 6.8 | 6.5 | 2.0 | 5.7 | Medium | 30d | Review |
| LLM-11 | Long-Running Learning Loop | Data poisoning of the Learning Loop's training... | 8.5 | 4.3 | 6.3 | 2.5 | 5.7 | Medium | 30d | Review |
| T-8 | Long-Running Learning Loop | The training signal stream from the Audit Logg... | 8.5 | 4.3 | 6.3 | 2.5 | 5.7 | Medium | 30d | Review |
| D-3 | Specialist Agent | The Specialist Agent is invoked by the Orchest... | 5.7 | 6.8 | 6.3 | 2.5 | 5.5 | Medium | 30d | Review |
| D-4 | Inter-Agent Communication Channel | The Channel's message queue can be flooded by ... | 5.7 | 6.8 | 6.5 | 2.5 | 5.5 | Medium | 30d | Review |
| D-7 | Audit Logger | The Audit Logger can be overwhelmed by a log-f... | 5.7 | 6.8 | 6.3 | 2.5 | 5.5 | Medium | 30d | Review |
| AG-8 | Inter-Agent Communication Channel | Insecure Inter-Agent Communication (Category 9... | 5.7 | 6.8 | 6.5 | 2.5 | 5.5 | Medium | 30d | Review |
| I-6 | Knowledge Base | The Knowledge Base exposes its full document c... | 6.5 | 5.8 | 6.3 | 2.0 | 5.4 | Medium | 30d | Review |
| I-7 | Audit Logger | The Audit Logger aggregates sensitive data fro... | 6.5 | 5.8 | 6.0 | 2.5 | 5.4 | Medium | 30d | Review |
| D-8 | Long-Running Learning Loop | The Learning Loop is a resource-intensive batc... | 6.5 | 5.8 | 5.5 | 2.5 | 5.3 | Medium | 30d | Review |
| I-5 | MCP Tool Server | Tool results from External API calls may conta... | 6.5 | 5.5 | 5.5 | 2.5 | 5.3 | Medium | 30d | Review |
| LLM-3 | LLM Agent Orchestrator | Model theft via systematic API probing: an att... | 6.5 | 5.5 | 6.0 | 2.5 | 5.3 | Medium | 30d | Review |
| LLM-12 | Long-Running Learning Loop | Model theft via Learning Loop output monitorin... | 6.5 | 5.8 | 5.5 | 2.5 | 5.3 | Medium | 30d | Review |
| T-6 | Knowledge Base | The Knowledge Base corpus can be tampered with... | 7.7 | 4.5 | 5.5 | 2.0 | 5.3 | Medium | 30d | Review |
| R-9 | Clinical Advisory Sub-Agent | The Clinical Advisory Sub-Agent denies having ... | 6.5 | 5.3 | 5.5 | 2.5 | 5.2 | Medium | 30d | Review |
| S-2 | Guardrails Service | An attacker spoofs the Guardrails Service by s... | 6.3 | 5.5 | 5.3 | 2.5 | 5.2 | Medium | 30d | Review |
| I-4 | Inter-Agent Communication Channel | Messages on the Inter-Agent Communication Chan... | 5.7 | 5.8 | 5.8 | 2.5 | 5.1 | Medium | 30d | Review |
| R-8 | External API | The External API provider denies having return... | 4.3 | 5.0 | 5.3 | 6.0 | 5.0 | Medium | 30d | Review |
| T-1 | Guardrails Service | An attacker with write access to the Guardrail... | 6.6 | 4.8 | 5.0 | 2.5 | 5.0 | Medium | 30d | Review |
| AGP-01 | LLM Agent Orchestrator | Multi-agent emergent behavior — cascading failu... | 5.5 | 4.5 | 5.8 | 2.5 | 4.6 | Medium | 30d | Review |
| I-8 | Long-Running Learning Loop | The Learning Loop consumes the full Audit Logg... | 5.9 | 5.0 | 5.8 | 2.5 | 4.9 | Medium | 30d | Review |
| R-7 | Long-Running Learning Loop | The Learning Loop denies having applied a spec... | 6.5 | 4.5 | 5.3 | 2.5 | 4.9 | Medium | 30d | Review |
| S-4 | Specialist Agent | The Specialist Agent impersonates the Orchestr... | 5.7 | 5.3 | 5.3 | 2.5 | 4.9 | Medium | 30d | Review |
| I-3 | Specialist Agent | The Specialist Agent receives sensitive data v... | 5.7 | 5.3 | 5.0 | 2.5 | 4.8 | Medium | 30d | Review |
| R-2 | Guardrails Service | The Guardrails Service can deny having logged ... | 4.3 | 5.3 | 5.5 | 2.5 | 4.4 | Medium | 30d | Review |
| R-4 | Specialist Agent | The Specialist Agent denies having executed a ... | 4.3 | 5.3 | 5.3 | 2.5 | 4.4 | Medium | 30d | Review |
| R-6 | MCP Tool Server | The MCP Tool Server denies having executed a s... | 4.3 | 5.3 | 5.5 | 2.5 | 4.4 | Medium | 30d | Review |
| R-5 | Inter-Agent Communication Channel | The Channel denies having delivered or modifie... | 4.3 | 5.0 | 5.3 | 2.5 | 4.3 | Medium | 30d | Review |

---

## 3. Dimensional Breakdown

### S-1: An attacker impersonates a legitimate user by replaying stolen session tokens or forging identity credentials to bypass authentication at the User→Guardrails boundary, gaining unauthorized access to the system under a victim identity.

**Component**: User
**Category**: Spoofing
**MAESTRO Layer**: L7 — Agent Ecosystem
**Composite Score**: 8.2 (High)

| Dimension | Score | Weight | Weighted |
|-----------|------:|-------:|---------:|
| CVSS Base | 8.2 | 0.35 | 2.87 |
| Exploitability | 8.0 | 0.30 | 2.40 |
| Scalability | 6.8 | 0.15 | 1.02 |
| Reachability | 9.5 | 0.20 | 1.90 |
| **Composite** | | | **8.2** |

**CVSS Vector**: `CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:L/A:N`

**Scoring Rationale**:
- **CVSS**: Remote network attack with no privileges required; high confidentiality impact from identity hijacking, low integrity impact as the attacker operates within the victim's permitted scope.
- **Exploitability**: Session replay and credential theft are extensively documented with mature tooling (Burp Suite, credential-stuffing frameworks); low skill barrier makes exploitation highly accessible.
- **Scalability**: Credential stuffing can be fully automated across all user accounts; detection is moderate since replay traffic resembles legitimate login activity.
- **Reachability**: User component is in the Untrusted zone with "user" keyword adjustment (+0.5), yielding 9.5; the internet-facing authentication boundary is maximally exposed.

*Score source: inherited (baseline 2026-04-23T19-30-00)*

---

### AG-1: Prompt injection causes the Orchestrator to autonomously execute unauthorized high-impact actions (mass data exfiltration from KB, bulk tool invocations against External API) beyond the scope of the user's original request, exploiting the Orchestrator's broad access to system capabilities.

**Component**: LLM Agent Orchestrator
**Category**: Agentic Threats
**MAESTRO Layer**: L1 — Foundation Model
**Composite Score**: 7.8 (High)
**Correlation Group**: Scores inherited from primary finding E-2

| Dimension | Score | Weight | Weighted |
|-----------|------:|-------:|---------:|
| CVSS Base | 10.0 | 0.35 | 3.50 |
| Exploitability | 8.8 | 0.30 | 2.64 |
| Scalability | 7.5 | 0.15 | 1.13 |
| Reachability | 2.5 | 0.20 | 0.50 |
| **Composite** | | | **7.8** |

**CVSS Vector**: `CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H`

**Scoring Rationale**:
- **CVSS**: Maximum base score; remote, unauthenticated, scope-changing attack with full CIA impact — Orchestrator's broad cross-component authority means exploitation affects the entire system.
- **Exploitability**: Direct prompt injection is trivially simple to execute with no special tooling; the Orchestrator's autonomous action capabilities amplify the impact of any injection that succeeds.
- **Scalability**: Automatable against any Orchestrator-facing endpoint; affects all sessions; detection is difficult because injected instructions resemble legitimate complex requests.
- **Reachability**: Component is in the Trusted Application Zone (baseline 2.5); internal placement moderates score despite the severity of the threat.

*Score source: inherited (baseline 2026-04-23T19-30-00)*

---

### E-2: The Orchestrator has privileged access to the Knowledge Base, MCP Tool Server, and delegation authority over the Specialist Agent and Clinical Advisory Sub-Agent. A prompt injection attack that manipulates the Orchestrator's reasoning can cause it to self-authorize elevated operations: exfiltrating the full KB corpus, invoking tools outside the user's permitted scope, or issuing unauthorized delegation messages.

**Component**: LLM Agent Orchestrator
**Category**: Privilege Escalation
**MAESTRO Layer**: L1 — Foundation Model
**Composite Score**: 7.8 (High)

| Dimension | Score | Weight | Weighted |
|-----------|------:|-------:|---------:|
| CVSS Base | 10.0 | 0.35 | 3.50 |
| Exploitability | 8.8 | 0.30 | 2.64 |
| Scalability | 7.5 | 0.15 | 1.13 |
| Reachability | 2.5 | 0.20 | 0.50 |
| **Composite** | | | **7.8** |

**CVSS Vector**: `CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H`

**Scoring Rationale**:
- **CVSS**: Unauthenticated remote attacker can trigger scope-changing privilege escalation with full CIA impact; the Orchestrator's privileged position means exploitation grants access to all downstream capabilities.
- **Exploitability**: Prompt injection against an LLM with broad tool access is extensively documented; no special conditions required beyond crafting adversarial input.
- **Scalability**: Fully automatable; affects any Orchestrator session; blends with legitimate complex requests making detection difficult.
- **Reachability**: Trusted Application Zone (2.5); the internal placement is the primary score moderator.

*Score source: inherited (baseline 2026-04-23T19-30-00)*

---

### R-3: The Orchestrator denies having issued a specific delegation message or tool call request, claiming the action was performed by another process. Without per-action logging of Orchestrator-originated actions with content hashes, the Orchestrator's operational history cannot be audited.

**Component**: LLM Agent Orchestrator
**Category**: Repudiation
**MAESTRO Layer**: L1 — Foundation Model
**Composite Score**: 7.8 (High)
**Correlation Group**: Scores inherited from primary finding E-2

| Dimension | Score | Weight | Weighted |
|-----------|------:|-------:|---------:|
| CVSS Base | 10.0 | 0.35 | 3.50 |
| Exploitability | 8.8 | 0.30 | 2.64 |
| Scalability | 7.5 | 0.15 | 1.13 |
| Reachability | 2.5 | 0.20 | 0.50 |
| **Composite** | | | **7.8** |

**CVSS Vector**: `CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H`

**Scoring Rationale**:
- **CVSS**: Inherited from CG-3 primary (E-2); the absence of non-repudiation controls enables the same threat vector to operate without forensic accountability.
- **Exploitability**: Inherited from CG-3 primary. Repudiation is trivially exercised once prompt injection has occurred; no logging gaps means no forensic trail.
- **Scalability**: Inherited from CG-3 primary. The inability to attribute actions scales across all Orchestrator sessions systemically.
- **Reachability**: Inherited from CG-3 primary. Trusted Application Zone (2.5).

*Score source: inherited (baseline 2026-04-23T19-30-00)*

---

### E-1: A prompt injection attack that bypasses the Guardrails Service effectively elevates the attacker's privilege from "unauthenticated user" to "trusted caller of the Orchestrator". The attacker's prompt reaches the Orchestrator with the same trust level as validated internal inputs, enabling subsequent escalation.

**Component**: Guardrails Service
**Category**: Privilege Escalation
**MAESTRO Layer**: L6 — Security and Compliance
**Composite Score**: 7.7 (High)

| Dimension | Score | Weight | Weighted |
|-----------|------:|-------:|---------:|
| CVSS Base | 10.0 | 0.35 | 3.50 |
| Exploitability | 8.8 | 0.30 | 2.64 |
| Scalability | 7.3 | 0.15 | 1.10 |
| Reachability | 2.5 | 0.20 | 0.50 |
| **Composite** | | | **7.7** |

**CVSS Vector**: `CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H`

**Scoring Rationale**:
- **CVSS**: Guardrails bypass is a network-level unauthenticated attack granting scope-changed access to the Orchestrator tier; full CIA impact because the escalation enables all downstream abuses.
- **Exploitability**: Prompt injection bypass of guardrails is one of the most widely documented AI security techniques; extensive public research and tooling exists.
- **Scalability**: Highly scriptable; affects all user sessions; detection is moderately difficult since injected content resembles valid user prompts.
- **Reachability**: Guardrails Service is in the Trusted Application Zone (2.5); internal zone moderates despite being the first security control.

*Score source: inherited (baseline 2026-04-23T19-30-00)*

---

### LLM-6: Improper output handling — server-side execution via Tool Call Request: LLM-generated JSON-RPC parameters flowing into the MCP Tool Server may contain injection payloads (SQL fragments, shell metacharacters) that are executed server-side when the Tool Server dispatches tool invocations.

**Component**: LLM Agent Orchestrator
**Category**: LLM Threats
**MAESTRO Layer**: L1 — Foundation Model
**Composite Score**: 7.7 (High)

| Dimension | Score | Weight | Weighted |
|-----------|------:|-------:|---------:|
| CVSS Base | 10.0 | 0.35 | 3.50 |
| Exploitability | 8.8 | 0.30 | 2.64 |
| Scalability | 7.3 | 0.15 | 1.10 |
| Reachability | 2.5 | 0.20 | 0.50 |
| **Composite** | | | **7.7** |

**CVSS Vector**: `CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H`

**Scoring Rationale**:
- **CVSS**: Unauthenticated remote attacker influences LLM output that flows to a server-side execution sink; scope change (LLM → Tool Server) with full CIA impact.
- **Exploitability**: LLM output injection into downstream execution sinks is extensively documented in OWASP LLM05; tooling and proof-of-concept exploits are publicly available.
- **Scalability**: Affects all Orchestrator sessions that invoke tools; highly scriptable; server-side execution artifacts may evade application-layer monitoring.
- **Reachability**: Trusted Application Zone (2.5); the Orchestrator's internal placement moderates the reachability component.

*Score source: inherited (baseline 2026-04-23T19-30-00)*

---

### OI-2: Improper output handling — server-side execution via Tool Call Request: the Orchestrator emits "Tool Call Request (JSON-RPC)" messages to the MCP Tool Server containing LLM-synthesized parameters. If tool parameters are used to construct SQL queries, shell commands, template expressions, or filesystem paths server-side without parameterization or sanitization, an attacker who influences the Orchestrator's output achieves server-side code/command execution via the tool execution sink.

**Component**: LLM Agent Orchestrator
**Category**: LLM Threats
**MAESTRO Layer**: L1 — Foundation Model
**Composite Score**: 7.7 (High)

| Dimension | Score | Weight | Weighted |
|-----------|------:|-------:|---------:|
| CVSS Base | 10.0 | 0.35 | 3.50 |
| Exploitability | 8.8 | 0.30 | 2.64 |
| Scalability | 7.3 | 0.15 | 1.10 |
| Reachability | 2.5 | 0.20 | 0.50 |
| **Composite** | | | **7.7** |

**CVSS Vector**: `CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H`

**Scoring Rationale**:
- **CVSS**: Identical threat vector to LLM-6 from a dedicated output-integrity signal-class perspective; maximum CVSS for server-side execution via unsanitized LLM output.
- **Exploitability**: Widely documented server-side injection class with proven exploit patterns across SQL, shell, and template injection vectors.
- **Scalability**: Scales across all tool-calling sessions; parameterization failures are systemic rather than per-instance, enabling broad exploitation.
- **Reachability**: Trusted Application Zone (2.5).

*Score source: inherited (baseline 2026-04-23T19-30-00)*

---

### LLM-5: Improper output handling — client-side XSS via the Orchestrator's HTTPS response to the User: LLM-generated response content rendered as HTML in the user's browser without contextual output encoding enables stored or reflected XSS.

**Component**: LLM Agent Orchestrator
**Category**: LLM Threats
**MAESTRO Layer**: L1 — Foundation Model
**Composite Score**: 7.5 (High)

| Dimension | Score | Weight | Weighted |
|-----------|------:|-------:|---------:|
| CVSS Base | 9.3 | 0.35 | 3.26 |
| Exploitability | 8.8 | 0.30 | 2.64 |
| Scalability | 7.3 | 0.15 | 1.10 |
| Reachability | 2.5 | 0.20 | 0.50 |
| **Composite** | | | **7.5** |

**CVSS Vector**: `CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:H/A:N`

**Scoring Rationale**:
- **CVSS**: User interaction required (browser rendering the LLM response); scope changes to client browser; high C and I from session cookie/CSRF token theft.
- **Exploitability**: LLM-driven XSS is extensively documented; the attack combines prompt injection with DOM injection using mature, off-the-shelf tooling.
- **Scalability**: Fully automatable; affects all users who render LLM responses in a browser; XSS payloads are generic and require no per-victim customization.
- **Reachability**: Trusted Application Zone (2.5) for the Orchestrator component.

*Score source: inherited (baseline 2026-04-23T19-30-00)*

---

### OI-1: Improper output handling — client-side XSS via LLM response rendered in user browser: the Orchestrator's "Response (HTTPS)" data flow sends LLM-generated content directly to the User. If the client-side rendering layer injects this content into the DOM via innerHTML or equivalent without HTML entity encoding, an attacker who primes the Orchestrator to emit script payloads causes client-side execution in the victim's browser.

**Component**: LLM Agent Orchestrator
**Category**: LLM Threats
**MAESTRO Layer**: L1 — Foundation Model
**Composite Score**: 7.5 (High)

| Dimension | Score | Weight | Weighted |
|-----------|------:|-------:|---------:|
| CVSS Base | 9.3 | 0.35 | 3.26 |
| Exploitability | 8.8 | 0.30 | 2.64 |
| Scalability | 7.3 | 0.15 | 1.10 |
| Reachability | 2.5 | 0.20 | 0.50 |
| **Composite** | | | **7.5** |

**CVSS Vector**: `CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:H/A:N`

**Scoring Rationale**:
- **CVSS**: Same as LLM-5; dedicated output-integrity finding on the same client-side XSS signal class for the direct LLM→User response path.
- **Exploitability**: Identical assessment to LLM-5; client-side injection from LLM output is thoroughly documented with mature tooling.
- **Scalability**: Identical to LLM-5; affects all users rendering LLM responses.
- **Reachability**: Trusted Application Zone (2.5).

*Score source: inherited (baseline 2026-04-23T19-30-00)*

---

### LLM-13: Prompt injection via clinical query context: the Clinical Advisory Sub-Agent processes Clinical Query / Context payloads from the Orchestrator. If the clinical context contains adversarially crafted text, the injection can override the sub-agent's system prompt, cause it to fabricate clinical recommendations, reveal its system configuration, or escalate privileges within the advisory pipeline.

**Component**: Clinical Advisory Sub-Agent
**Category**: LLM Threats
**MAESTRO Layer**: L7 — Agent Ecosystem
**Composite Score**: 7.4 (High)

| Dimension | Score | Weight | Weighted |
|-----------|------:|-------:|---------:|
| CVSS Base | 9.3 | 0.35 | 3.26 |
| Exploitability | 8.8 | 0.30 | 2.64 |
| Scalability | 7.0 | 0.15 | 1.05 |
| Reachability | 2.5 | 0.20 | 0.50 |
| **Composite** | | | **7.4** |

**CVSS Vector**: `CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:H/A:N`

**Scoring Rationale**:
- **CVSS**: Prompt injection via clinical context pipeline; user interaction implicit in clinical query processing; scope change because the sub-agent's fabricated output flows into the Orchestrator's response path.
- **Exploitability**: Prompt injection is extensively documented; the clinical sub-agent provides a high-impact injection target with direct patient-safety consequences.
- **Scalability**: Slightly lower than Orchestrator LLM findings due to the specialized clinical invocation path; still broadly scriptable across all clinical queries.
- **Reachability**: Trusted Application Zone (2.5).

*Score source: inherited (baseline 2026-04-23T19-30-00)*

---

### LLM-8: Prompt injection via delegation messages: the Specialist Agent processes tasks delegated by the Orchestrator via the Inter-Agent Channel. An attacker who injects adversarial content into the Delegation Message can hijack the Specialist's task execution, causing it to perform unauthorized tool invocations or exfiltrate data through its result channel.

**Component**: Specialist Agent
**Category**: LLM Threats
**MAESTRO Layer**: Unclassified
**Composite Score**: 7.3 (High)

| Dimension | Score | Weight | Weighted |
|-----------|------:|-------:|---------:|
| CVSS Base | 9.3 | 0.35 | 3.26 |
| Exploitability | 8.3 | 0.30 | 2.49 |
| Scalability | 6.8 | 0.15 | 1.02 |
| Reachability | 2.5 | 0.20 | 0.50 |
| **Composite** | | | **7.3** |

**CVSS Vector**: `CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:H/A:N`

**Scoring Rationale**:
- **CVSS**: Delegation message injection achieves scope-changing execution; user interaction reflects the need for delegation message processing to trigger the attack.
- **Exploitability**: Slightly lower than direct Orchestrator injection (8.3 vs 8.8) because the attack requires reaching the inter-agent channel path rather than the direct user-facing endpoint.
- **Scalability**: Affects all Specialist invocations; automatable through crafted delegation messages; detection difficulty is high as injected content resembles legitimate task specifications.
- **Reachability**: Trusted Application Zone (2.5).

*Score source: inherited (baseline 2026-04-23T19-30-00)*

---

### I-2: The Orchestrator's context window contains sensitive information (retrieved documents from the Knowledge Base, tool results, system prompts). A prompt injection attack or model hallucination can cause the Orchestrator to leak this context in its HTTPS response to the User, exposing system-internal data.

**Component**: LLM Agent Orchestrator
**Category**: Information Disclosure
**MAESTRO Layer**: L1 — Foundation Model
**Composite Score**: 7.2 (High)

| Dimension | Score | Weight | Weighted |
|-----------|------:|-------:|---------:|
| CVSS Base | 8.6 | 0.35 | 3.01 |
| Exploitability | 8.8 | 0.30 | 2.64 |
| Scalability | 7.3 | 0.15 | 1.10 |
| Reachability | 2.5 | 0.20 | 0.50 |
| **Composite** | | | **7.2** |

**CVSS Vector**: `CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:N/A:N`

**Scoring Rationale**:
- **CVSS**: Unauthenticated remote attack with scope change; high confidentiality impact from context window exfiltration of KB documents, system prompts, and tool results; no integrity or availability impact.
- **Exploitability**: Context leakage via prompt injection is the most extensively documented LLM attack; immediate exploitability with no prerequisites beyond submitting crafted prompts.
- **Scalability**: Automated extraction of context across all sessions; the broad scope of exfiltratable data (entire system context) amplifies the impact per successful exploitation.
- **Reachability**: Trusted Application Zone (2.5) for the Orchestrator.

*Score source: inherited (baseline 2026-04-23T19-30-00)*

---

### LLM-1: Direct prompt injection via the User→Guardrails→Orchestrator chain: an attacker embeds adversarial instructions in the user's prompt that the Guardrails Service fails to detect, causing the Orchestrator to override its system prompt, reveal internal configuration, or execute unauthorized actions.

**Component**: LLM Agent Orchestrator
**Category**: LLM Threats
**MAESTRO Layer**: L1 — Foundation Model
**Composite Score**: 7.2 (High)
**Correlation Group**: Scores inherited from primary finding I-2

| Dimension | Score | Weight | Weighted |
|-----------|------:|-------:|---------:|
| CVSS Base | 8.6 | 0.35 | 3.01 |
| Exploitability | 8.8 | 0.30 | 2.64 |
| Scalability | 7.3 | 0.15 | 1.10 |
| Reachability | 2.5 | 0.20 | 0.50 |
| **Composite** | | | **7.2** |

**CVSS Vector**: `CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:N/A:N`

**Scoring Rationale**:
- **CVSS**: Inherited from CG-4 primary (I-2); direct prompt injection is the primary mechanism for context window leakage.
- **Exploitability**: Inherited from CG-4 primary. Direct prompt injection is trivially executed.
- **Scalability**: Inherited from CG-4 primary. Affects all Orchestrator sessions.
- **Reachability**: Inherited from CG-4 primary. Trusted Application Zone (2.5).

*Score source: inherited (baseline 2026-04-23T19-30-00)*

---

### LLM-4: Training data poisoning via the Long-Running Learning Loop: the Orchestrator ingests model updates from the Learning Loop that was trained on audit log data. An attacker who pollutes the audit log with adversarial interaction records poisons the Orchestrator's future behavior at update time.

**Component**: LLM Agent Orchestrator
**Category**: LLM Threats
**MAESTRO Layer**: L1 — Foundation Model
**Composite Score**: 7.1 (High)
**Correlation Group**: Scores inherited from primary finding T-2

| Dimension | Score | Weight | Weighted |
|-----------|------:|-------:|---------:|
| CVSS Base | 10.0 | 0.35 | 3.50 |
| Exploitability | 7.0 | 0.30 | 2.10 |
| Scalability | 6.5 | 0.15 | 0.98 |
| Reachability | 2.5 | 0.20 | 0.50 |
| **Composite** | | | **7.1** |

**CVSS Vector**: `CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:N`

**Scoring Rationale**:
- **CVSS**: Inherited from CG-1 primary (T-2); training data poisoning shares the context window manipulation attack surface.
- **Exploitability**: Inherited from CG-1 primary. Tampering with the knowledge sources feeding the context window is well-documented.
- **Scalability**: Inherited from CG-1 primary. Affects all future Orchestrator sessions after a poisoned model update.
- **Reachability**: Inherited from CG-1 primary. Trusted Application Zone (2.5).

*Score source: inherited (baseline 2026-04-23T19-30-00)*

---

### T-2: The Orchestrator's context window (system prompt, retrieved documents, tool results) can be tampered with by an attacker who controls any upstream data source — the Knowledge Base, the Inter-Agent Channel (aggregated results), or tool call responses from the MCP Tool Server.

**Component**: LLM Agent Orchestrator
**Category**: Tampering
**MAESTRO Layer**: L1 — Foundation Model
**Composite Score**: 7.1 (High)

| Dimension | Score | Weight | Weighted |
|-----------|------:|-------:|---------:|
| CVSS Base | 10.0 | 0.35 | 3.50 |
| Exploitability | 7.0 | 0.30 | 2.10 |
| Scalability | 6.5 | 0.15 | 0.98 |
| Reachability | 2.5 | 0.20 | 0.50 |
| **Composite** | | | **7.1** |

**CVSS Vector**: `CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:N`

**Scoring Rationale**:
- **CVSS**: Remote unauthenticated attack (via poisoned upstream source) with scope change affecting the Orchestrator; full C and I impact as the Orchestrator's entire reasoning can be subverted.
- **Exploitability**: Multiple attack paths (KB poisoning, tool result tampering, channel manipulation) are documented; moderate skill requirement to poison the specific upstream source.
- **Scalability**: Poisoning upstream sources affects all subsequent Orchestrator sessions; the multi-path attack surface broadens the practical scope.
- **Reachability**: Trusted Application Zone (2.5).

*Score source: inherited (baseline 2026-04-23T19-30-00)*

---

### E-5: The MCP Tool Server executes tools with credentials it holds (service account tokens, API keys for External API). If an agent sends unauthorized tool calls (via forged identity or exploited Orchestrator), it gains the Tool Server's execution privileges — invoking external APIs, writing to external systems, and accessing data sources with the server's full credential set.

**Component**: MCP Tool Server
**Category**: Privilege Escalation
**MAESTRO Layer**: L3 — Agent Framework
**Composite Score**: 7.0 (High)

| Dimension | Score | Weight | Weighted |
|-----------|------:|-------:|---------:|
| CVSS Base | 9.9 | 0.35 | 3.47 |
| Exploitability | 7.0 | 0.30 | 2.10 |
| Scalability | 6.5 | 0.15 | 0.98 |
| Reachability | 2.5 | 0.20 | 0.50 |
| **Composite** | | | **7.0** |

**CVSS Vector**: `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H`

**Scoring Rationale**:
- **CVSS**: High base score reflecting full CIA impact from credential abuse; scope change as the Tool Server's credentials grant access to external systems beyond the application boundary.
- **Exploitability**: Requires compromising the calling agent first (PR:L); documented attack pattern via forged caller identity or prompt injection escalation.
- **Scalability**: Credential abuse enables repeated automated exploitation across all permitted external targets; detection depends on monitoring anomalous API patterns.
- **Reachability**: Trusted Application Zone (2.5).

*Score source: inherited (baseline 2026-04-23T19-30-00)*

---

### T-5: Tool call request parameters supplied by agent LLM outputs can be tampered with before execution if the Tool Server does not validate them against an explicit allowlist. An attacker who can influence the Orchestrator's or Specialist's LLM output can modify JSON-RPC parameters to call unintended tools or supply malicious arguments.

**Component**: MCP Tool Server
**Category**: Tampering
**MAESTRO Layer**: L3 — Agent Framework
**Composite Score**: 7.0 (High)

| Dimension | Score | Weight | Weighted |
|-----------|------:|-------:|---------:|
| CVSS Base | 9.9 | 0.35 | 3.47 |
| Exploitability | 7.0 | 0.30 | 2.10 |
| Scalability | 6.5 | 0.15 | 0.98 |
| Reachability | 2.5 | 0.20 | 0.50 |
| **Composite** | | | **7.0** |

**CVSS Vector**: `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H`

**Scoring Rationale**:
- **CVSS**: Parameter injection achieves scope-changed code execution; high CVSS matches the severity of unsanitized LLM output reaching execution sinks.
- **Exploitability**: JSON-RPC parameter injection is well-documented; shell metacharacter and SQL injection patterns are well-understood attack techniques.
- **Scalability**: Affects all tool invocations; systematically exploitable across all agents that invoke tools; execution-level impact makes detection challenging without strict input validation telemetry.
- **Reachability**: Trusted Application Zone (2.5).

*Score source: inherited (baseline 2026-04-23T19-30-00)*

---

### AG-5: The MCP Tool Server is vulnerable to tool call injection: an attacker who can influence the LLM output of either the Orchestrator or Specialist Agent can inject crafted JSON-RPC parameters that invoke unintended tools (tool name injection) or supply malicious arguments to permitted tools (parameter injection). The Tool Server executes these with its own service credentials.

**Component**: MCP Tool Server
**Category**: Agentic Threats
**MAESTRO Layer**: L3 — Agent Framework
**Composite Score**: 6.9 (Medium)

| Dimension | Score | Weight | Weighted |
|-----------|------:|-------:|---------:|
| CVSS Base | 9.4 | 0.35 | 3.29 |
| Exploitability | 7.0 | 0.30 | 2.10 |
| Scalability | 6.5 | 0.15 | 0.98 |
| Reachability | 2.5 | 0.20 | 0.50 |
| **Composite** | | | **6.9** |

**CVSS Vector**: `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:L`

**Scoring Rationale**:
- **CVSS**: Agentic default vector; tool name injection achieves scope-changed execution but lower A than full parameter injection since availability impact depends on specific tool targets.
- **Exploitability**: Identical profile to T-5 from an exploitability standpoint; agentic framing adds the tool-name-injection vector which has emerging but growing research.
- **Scalability**: Affects all agent-to-tool-server invocations; pattern is systematic rather than instance-specific.
- **Reachability**: Trusted Application Zone (2.5).

*Score source: inherited (baseline 2026-04-23T19-30-00)*

---

### E-7: The Clinical Advisory Sub-Agent operates with access to the Knowledge Base and produces clinical outputs that feed directly into the Orchestrator's response path. A prompt injection attack embedded in the Clinical Query / Context payload can cause the sub-agent to self-authorize elevated access or return outputs designed to manipulate the Orchestrator into taking high-privilege actions.

**Component**: Clinical Advisory Sub-Agent
**Category**: Privilege Escalation
**MAESTRO Layer**: L7 — Agent Ecosystem
**Composite Score**: 6.9 (Medium)

| Dimension | Score | Weight | Weighted |
|-----------|------:|-------:|---------:|
| CVSS Base | 9.9 | 0.35 | 3.47 |
| Exploitability | 6.8 | 0.30 | 2.04 |
| Scalability | 6.0 | 0.15 | 0.90 |
| Reachability | 2.5 | 0.20 | 0.50 |
| **Composite** | | | **6.9** |

**CVSS Vector**: `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H`

**Scoring Rationale**:
- **CVSS**: High base score; the sub-agent's privileged KB access and Orchestrator integration make privilege escalation via prompt injection a full CIA-impact event.
- **Exploitability**: Slightly lower than Orchestrator-level injection because the attack path requires reaching the clinical query channel specifically; still well-documented LLM injection technique.
- **Scalability**: Affects all clinical advisory sessions; lower scalability than direct Orchestrator paths because of the specialized invocation context.
- **Reachability**: Trusted Application Zone (2.5).

*Score source: inherited (baseline 2026-04-23T19-30-00)*

---

### I-9: The Clinical Advisory Sub-Agent processes clinical query context from the Orchestrator and retrieves documents from the Knowledge Base. If its Clinical Summary + Recommendations output is not scrubbed before inclusion in the Orchestrator's HTTPS response to the User, clinical context (patient-specific data, sensitive medical records, proprietary clinical protocols) can leak to unauthorized parties. Additionally, if Clinical Decision Log Entries are not field-classified before writing to the Audit Logger, sensitive clinical data propagates into the training signal stream.

**Component**: Clinical Advisory Sub-Agent
**Category**: Information Disclosure
**MAESTRO Layer**: L7 — Agent Ecosystem
**Composite Score**: 6.8 (Medium)

| Dimension | Score | Weight | Weighted |
|-----------|------:|-------:|---------:|
| CVSS Base | 8.6 | 0.35 | 3.01 |
| Exploitability | 7.8 | 0.30 | 2.34 |
| Scalability | 6.5 | 0.15 | 0.98 |
| Reachability | 2.5 | 0.20 | 0.50 |
| **Composite** | | | **6.8** |

**CVSS Vector**: `CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:N/A:N`

**Scoring Rationale**:
- **CVSS**: Scope-changing information disclosure; clinical data leakage to unauthorized parties has HIGH confidentiality impact; unauthenticated attacker can trigger via prompt injection.
- **Exploitability**: Clinical data leakage via unscrubbed LLM output is a well-documented attack pattern with high practical impact; the clinical context (patient data, medical records) raises the stakes.
- **Scalability**: Leakage occurs systematically across all clinical sessions without output scrubbing; propagation into the training stream compounds scale.
- **Reachability**: Trusted Application Zone (2.5).

*Score source: inherited (baseline 2026-04-23T19-30-00)*

---

### LLM-2: Indirect prompt injection via the Knowledge Base: an attacker embeds adversarial instructions in documents stored in the Knowledge Base. When the Orchestrator retrieves these documents during vector search, the adversarial instructions are injected into its context window, hijacking its reasoning.

**Component**: LLM Agent Orchestrator
**Category**: LLM Threats
**MAESTRO Layer**: L1 — Foundation Model
**Composite Score**: 6.8 (Medium)

| Dimension | Score | Weight | Weighted |
|-----------|------:|-------:|---------:|
| CVSS Base | 10.0 | 0.35 | 3.50 |
| Exploitability | 6.0 | 0.30 | 1.80 |
| Scalability | 6.8 | 0.15 | 1.02 |
| Reachability | 2.5 | 0.20 | 0.50 |
| **Composite** | | | **6.8** |

**CVSS Vector**: `CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:N`

**Scoring Rationale**:
- **CVSS**: Maximum base; indirect injection via KB is effectively unauthenticated and unattended — attacker content is already resident in the knowledge store, no real-time interaction needed.
- **Exploitability**: Lower than direct injection (6.0 vs 8.8) because the attacker must first gain write access to the KB or exploit a data ingestion path; the indirect nature adds complexity.
- **Scalability**: Once adversarial documents are injected, exploitation is persistent and affects all retrieval sessions without further attacker involvement.
- **Reachability**: Trusted Application Zone (2.5).

*Score source: inherited (baseline 2026-04-23T19-30-00)*

---

### D-1: The Guardrails Service is vulnerable to resource exhaustion via high-volume prompt submission. An attacker sends computationally expensive prompts (complex regex evaluation patterns, adversarially crafted inputs that maximize rule evaluation cost) at high rate to degrade or collapse the filtering pipeline.

**Component**: Guardrails Service
**Category**: Denial of Service
**MAESTRO Layer**: L6 — Security and Compliance
**Composite Score**: 6.7 (Medium)

| Dimension | Score | Weight | Weighted |
|-----------|------:|-------:|---------:|
| CVSS Base | 7.5 | 0.35 | 2.63 |
| Exploitability | 8.5 | 0.30 | 2.55 |
| Scalability | 7.0 | 0.15 | 1.05 |
| Reachability | 2.5 | 0.20 | 0.50 |
| **Composite** | | | **6.7** |

**CVSS Vector**: `CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H`

**Scoring Rationale**:
- **CVSS**: Standard DoS vector; remote, no privileges, high availability impact from pipeline collapse.
- **Exploitability**: Volumetric DoS is the simplest attack class; no special skills required; off-the-shelf load-testing tools can be repurposed.
- **Scalability**: Highly scriptable; affects all users of the system when Guardrails collapses; detection is rapid but mitigation requires operational response.
- **Reachability**: Trusted Application Zone (2.5); the Guardrails Service sits behind the network ingress but is the first processing layer for all user traffic.

*Score source: inherited (baseline 2026-04-23T19-30-00)*

---

### LLM-7: Improper output handling — SSRF via LLM-synthesized URL: the Orchestrator can instruct the MCP Tool Server to fetch external URLs synthesized from LLM output. An attacker who influences the Orchestrator's output can cause it to emit internal service URLs (cloud metadata endpoints, internal admin APIs) as tool parameters. The Tool Server fetches these with its server-side network credentials.

**Component**: LLM Agent Orchestrator
**Category**: LLM Threats
**MAESTRO Layer**: L1 — Foundation Model
**Composite Score**: 6.6 (Medium)

| Dimension | Score | Weight | Weighted |
|-----------|------:|-------:|---------:|
| CVSS Base | 8.6 | 0.35 | 3.01 |
| Exploitability | 7.0 | 0.30 | 2.10 |
| Scalability | 6.5 | 0.15 | 0.98 |
| Reachability | 2.5 | 0.20 | 0.50 |
| **Composite** | | | **6.6** |

**CVSS Vector**: `CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:N/A:N`

**Scoring Rationale**:
- **CVSS**: SSRF achieving scope change with high confidentiality impact from internal metadata endpoint access; no integrity/availability direct impact.
- **Exploitability**: SSRF via LLM-synthesized URLs is documented in OWASP LLM05; requires crafting prompts that cause URL synthesis, a well-understood technique.
- **Scalability**: Systematic exploitation possible across all tool-calling sessions; cloud metadata endpoint access can yield credentials affecting the entire infrastructure.
- **Reachability**: Trusted Application Zone (2.5).

*Score source: inherited (baseline 2026-04-23T19-30-00)*

---

### LLM-14: Training data poisoning of the Clinical Advisory Sub-Agent via the Learning Loop: Clinical Decision Log Entries from the sub-agent are included in the Audit Logger training stream. An attacker who injects adversarially crafted clinical interaction records into the Audit Logger can shift the sub-agent's clinical reasoning toward attacker-preferred outputs.

**Component**: Clinical Advisory Sub-Agent
**Category**: LLM Threats
**MAESTRO Layer**: L7 — Agent Ecosystem
**Composite Score**: 6.6 (Medium)
**Correlation Group**: Scores inherited from primary finding T-9

| Dimension | Score | Weight | Weighted |
|-----------|------:|-------:|---------:|
| CVSS Base | 9.9 | 0.35 | 3.47 |
| Exploitability | 6.0 | 0.30 | 1.80 |
| Scalability | 5.8 | 0.15 | 0.87 |
| Reachability | 2.5 | 0.20 | 0.50 |
| **Composite** | | | **6.6** |

**CVSS Vector**: `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:N`

**Scoring Rationale**:
- **CVSS**: Inherited from CG-6 primary (T-9); training data poisoning shares the context manipulation attack surface for the Clinical Advisory Sub-Agent.
- **Exploitability**: Inherited from CG-6 primary. Adversarial KB document injection and query payload tampering are the primary vectors.
- **Scalability**: Inherited from CG-6 primary. Poisoning affects all future clinical advisory sessions.
- **Reachability**: Inherited from CG-6 primary. Trusted Application Zone (2.5).

*Score source: inherited (baseline 2026-04-23T19-30-00)*

---

### MI-2: Overreliance / Missing HITL on Decision-Critical Output (Category 3 per FR-017): The Clinical Advisory Sub-Agent's "Clinical Summary + Recommendations" output flows directly back to the LLM Agent Orchestrator and from there into the user-facing response path without a declared human-in-the-loop (HITL) review gate.

**Component**: Clinical Advisory Sub-Agent
**Category**: LLM Threats
**MAESTRO Layer**: L7 — Agent Ecosystem
**Composite Score**: 6.6 (Medium)

| Dimension | Score | Weight | Weighted |
|-----------|------:|-------:|---------:|
| CVSS Base | 8.7 | 0.35 | 3.05 |
| Exploitability | 7.0 | 0.30 | 2.10 |
| Scalability | 6.3 | 0.15 | 0.95 |
| Reachability | 2.5 | 0.20 | 0.50 |
| **Composite** | | | **6.6** |

**CVSS Vector**: `CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:H/I:H/A:N`

**Scoring Rationale**:
- **CVSS**: Clinical overreliance is a structural flaw; authenticated clinical query (PR:L) triggers scope-changed output with high C and I impact from patient-safety consequences of wrong recommendations.
- **Exploitability**: No active attack required — the failure is a systemic design gap; any clinical query can trigger patient-safety risk without HITL; well-documented AI safety risk class.
- **Scalability**: Affects every clinical advisory session systematically; the absence of a HITL gate means the risk scales with usage volume without any mitigating friction.
- **Reachability**: Trusted Application Zone (2.5).

*Score source: inherited (baseline 2026-04-23T19-30-00)*

---

### T-9: The Clinical Advisory Sub-Agent's context window can be tampered with via two paths: (1) adversarial documents injected into the Knowledge Base that are retrieved during vector search, populating the sub-agent's reasoning context with malicious clinical "facts"; (2) tampering with the Clinical Query / Context payload from the Orchestrator, which may embed attacker-controlled clinical framing. Either path causes the sub-agent to incorporate adversarial content into clinical summaries returned to the Orchestrator.

**Component**: Clinical Advisory Sub-Agent
**Category**: Tampering
**MAESTRO Layer**: L7 — Agent Ecosystem
**Composite Score**: 6.6 (Medium)

| Dimension | Score | Weight | Weighted |
|-----------|------:|-------:|---------:|
| CVSS Base | 9.9 | 0.35 | 3.47 |
| Exploitability | 6.0 | 0.30 | 1.80 |
| Scalability | 5.8 | 0.15 | 0.87 |
| Reachability | 2.5 | 0.20 | 0.50 |
| **Composite** | | | **6.6** |

**CVSS Vector**: `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:N`

**Scoring Rationale**:
- **CVSS**: High CVSS for context window tampering; scope change as adversarial content flows through clinical summaries into the Orchestrator response path; full C and I impact from corrupted clinical guidance.
- **Exploitability**: Multi-path attack (KB documents or query payload) requires initial privileged access to either path; lower exploitability than direct injection attacks.
- **Scalability**: Once KB documents are poisoned, exploitation persists across all clinical sessions; query payload tampering is limited to compromised or attacker-influenced pipeline stages.
- **Reachability**: Trusted Application Zone (2.5).

*Score source: inherited (baseline 2026-04-23T19-30-00)*

---

### LLM-10: Improper output handling — server-side injection via tool call results: the Specialist Agent's tool call results from MCP Tool Server are incorporated into its context and may influence downstream tool invocations. If the Tool Server returns LLM-influenced content that contains injection payloads, the Specialist's next tool call may forward those payloads to execution sinks.

**Component**: Specialist Agent
**Category**: LLM Threats
**MAESTRO Layer**: Unclassified
**Composite Score**: 6.5 (Medium)

| Dimension | Score | Weight | Weighted |
|-----------|------:|-------:|---------:|
| CVSS Base | 9.3 | 0.35 | 3.26 |
| Exploitability | 6.0 | 0.30 | 1.80 |
| Scalability | 6.0 | 0.15 | 0.90 |
| Reachability | 2.5 | 0.20 | 0.50 |
| **Composite** | | | **6.5** |

**CVSS Vector**: `CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:H/A:N`

**Scoring Rationale**:
- **CVSS**: Scope-changing injection via tool results; the chained nature (tool result → next tool call) creates a scope-changed execution path with high C and I impact.
- **Exploitability**: Requires the attacker to influence the tool result content (via External API compromise or prior tool call injection); moderate complexity reduces exploitability relative to direct injection.
- **Scalability**: Affects all Specialist sessions that chain tool calls; the chained injection pattern requires specific tool sequences but those sequences are common in agentic workflows.
- **Reachability**: Trusted Application Zone (2.5).

*Score source: inherited (baseline 2026-04-23T19-30-00)*

---

### MI-1: Ungrounded Factual Emission (Category 1 per FR-017): The Clinical Advisory Sub-Agent emits clinical summaries containing factual medical claims (diagnostic observations, drug-interaction assertions, clinical recommendations) to the Orchestrator's response path without mandatory RAG grounding against a verified EHR index.

**Component**: Clinical Advisory Sub-Agent
**Category**: LLM Threats
**MAESTRO Layer**: L7 — Agent Ecosystem
**Composite Score**: 6.5 (Medium)

| Dimension | Score | Weight | Weighted |
|-----------|------:|-------:|---------:|
| CVSS Base | 8.7 | 0.35 | 3.05 |
| Exploitability | 7.0 | 0.30 | 2.10 |
| Scalability | 6.0 | 0.15 | 0.90 |
| Reachability | 2.5 | 0.20 | 0.50 |
| **Composite** | | | **6.5** |

**CVSS Vector**: `CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:H/I:H/A:N`

**Scoring Rationale**:
- **CVSS**: Structural hallucination risk; clinical query triggers output (UI:R); scope change as ungrounded factual claims flow through Orchestrator to end consumers; HIGH C and I from patient-safety consequences of fabricated drug doses or contraindications.
- **Exploitability**: No active attack required — this is a structural design gap; any clinical query that exceeds KB coverage triggers hallucination risk; well-documented AI safety failure mode.
- **Scalability**: Affects every clinical advisory session where KB coverage is insufficient; scales with query volume and KB staleness; systematic rather than per-instance.
- **Reachability**: Trusted Application Zone (2.5).

*Score source: inherited (baseline 2026-04-23T19-30-00)*

---

### MI-3: Retrieval-Grounding Gap (Category 4 per FR-017): The Clinical Advisory Sub-Agent performs vector search against the Knowledge Base to retrieve supporting clinical documents. However, there is no declared mechanism to detect or handle retrieval failures — scenarios where the Knowledge Base does not contain documents relevant to the clinical query (low-recall retrieval, out-of-distribution queries, stale KB content).

**Component**: Clinical Advisory Sub-Agent
**Category**: LLM Threats
**MAESTRO Layer**: L7 — Agent Ecosystem
**Composite Score**: 6.5 (Medium)

| Dimension | Score | Weight | Weighted |
|-----------|------:|-------:|---------:|
| CVSS Base | 8.7 | 0.35 | 3.05 |
| Exploitability | 6.8 | 0.30 | 2.04 |
| Scalability | 6.0 | 0.15 | 0.90 |
| Reachability | 2.5 | 0.20 | 0.50 |
| **Composite** | | | **6.5** |

**CVSS Vector**: `CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:H/I:H/A:N`

**Scoring Rationale**:
- **CVSS**: Same structural profile as MI-1; retrieval gap causes hallucination that has same patient-safety consequence as ungrounded emission; HIGH C and I impact.
- **Exploitability**: Slightly lower than MI-1 (6.8 vs 7.0) because the failure requires an out-of-distribution or KB-stale query to trigger; the attack surface is narrower than general ungrounded emission.
- **Scalability**: Scales with KB staleness and out-of-distribution query frequency; KB currency issues are systemic operational concerns affecting all clinical queries.
- **Reachability**: Trusted Application Zone (2.5).

*Score source: inherited (baseline 2026-04-23T19-30-00)*

---

### OI-3: Improper output handling — SSRF via LLM-synthesized URL in Tool Call Request: the Orchestrator constructs "Tool Call Request (JSON-RPC)" messages containing URLs sourced from LLM output. The MCP Tool Server executes outbound HTTP to the supplied URL using its own server-side network credentials and IAM role.

**Component**: LLM Agent Orchestrator
**Category**: LLM Threats
**MAESTRO Layer**: L1 — Foundation Model
**Composite Score**: 6.5 (Medium)

| Dimension | Score | Weight | Weighted |
|-----------|------:|-------:|---------:|
| CVSS Base | 8.6 | 0.35 | 3.01 |
| Exploitability | 6.8 | 0.30 | 2.04 |
| Scalability | 6.5 | 0.15 | 0.98 |
| Reachability | 2.5 | 0.20 | 0.50 |
| **Composite** | | | **6.5** |

**CVSS Vector**: `CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:N/A:N`

**Scoring Rationale**:
- **CVSS**: SSRF via LLM output in the dedicated output-integrity signal class; scope change with high confidentiality impact from IAM credential metadata exposure.
- **Exploitability**: Identical to LLM-7 at the output-integrity level; URL synthesis from LLM output targeting internal endpoints is a well-characterized technique.
- **Scalability**: Affects all tool-fetching sessions; IAM credential theft via SSRF scales to full infrastructure compromise.
- **Reachability**: Trusted Application Zone (2.5).

*Score source: inherited (baseline 2026-04-23T19-30-00)*

---

### E-3: The Specialist Agent receives delegated permissions from the Orchestrator. If the delegation message is forged or tampered with (granting the Specialist elevated permissions beyond the original user session scope), the Specialist gains unauthorized capability to invoke tools or access data outside its permitted scope.

**Component**: Specialist Agent
**Category**: Privilege Escalation
**MAESTRO Layer**: Unclassified
**Composite Score**: 6.4 (Medium)

| Dimension | Score | Weight | Weighted |
|-----------|------:|-------:|---------:|
| CVSS Base | 9.9 | 0.35 | 3.47 |
| Exploitability | 5.5 | 0.30 | 1.65 |
| Scalability | 5.5 | 0.15 | 0.83 |
| Reachability | 2.5 | 0.20 | 0.50 |
| **Composite** | | | **6.4** |

**CVSS Vector**: `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H`

**Scoring Rationale**:
- **CVSS**: Forged delegation achieving full privilege escalation; scope change with full CIA impact from unauthorized tool access.
- **Exploitability**: Requires first compromising the delegation message path (channel tampering or Orchestrator compromise); moderate prerequisite reduces immediate exploitability.
- **Scalability**: Each forged delegation affects a specific session; less scalable than session-independent injection attacks.
- **Reachability**: Trusted Application Zone (2.5).

*Score source: inherited (baseline 2026-04-23T19-30-00)*

---

### E-4: If the Channel does not enforce sender authentication, any Application Zone process can inject messages with forged identity headers claiming elevated sender roles (e.g., claiming to be the Orchestrator to issue trusted delegation messages). This elevates the attacker from a low-privilege process to the Orchestrator's trust level.

**Component**: Inter-Agent Communication Channel
**Category**: Privilege Escalation
**MAESTRO Layer**: Unclassified
**Composite Score**: 6.4 (Medium)

| Dimension | Score | Weight | Weighted |
|-----------|------:|-------:|---------:|
| CVSS Base | 9.9 | 0.35 | 3.47 |
| Exploitability | 5.5 | 0.30 | 1.65 |
| Scalability | 5.5 | 0.15 | 0.83 |
| Reachability | 2.5 | 0.20 | 0.50 |
| **Composite** | | | **6.4** |

**CVSS Vector**: `CVSS:3.1/AV:A/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H`

**Scoring Rationale**:
- **CVSS**: Adjacent-network attack (Application Zone access required); low-privilege prerequisite (Application Zone process); scope change with full CIA impact from forged Orchestrator identity.
- **Exploitability**: Requires Application Zone process access; not trivially exploitable from the internet; needs lateral movement or insider position.
- **Scalability**: Persistent channel access enables ongoing message injection; limited to processes already in the Application Zone.
- **Reachability**: Trusted Application Zone (2.5).

*Score source: inherited (baseline 2026-04-23T19-30-00)*

---

### S-5: The Channel is a shared message routing substrate with no inherent sender authentication. A malicious process in the Application Zone can inject messages impersonating either the Orchestrator or the Specialist Agent, enabling unauthorized task injection or result fabrication.

**Component**: Inter-Agent Communication Channel
**Category**: Spoofing
**MAESTRO Layer**: Unclassified
**Composite Score**: 6.4 (Medium)

| Dimension | Score | Weight | Weighted |
|-----------|------:|-------:|---------:|
| CVSS Base | 9.3 | 0.35 | 3.26 |
| Exploitability | 5.8 | 0.30 | 1.74 |
| Scalability | 5.8 | 0.15 | 0.87 |
| Reachability | 2.5 | 0.20 | 0.50 |
| **Composite** | | | **6.4** |

**CVSS Vector**: `CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:N`

**Scoring Rationale**:
- **CVSS**: No auth required within the Application Zone; scope change as forged messages affect both Orchestrator and Specialist; high C and I from identity impersonation enabling downstream abuse.
- **Exploitability**: Requires Application Zone network access but no authentication; moderately accessible for an insider or compromised zone process.
- **Scalability**: Persistent forged message injection affects all inter-agent coordination; systematic rather than per-session.
- **Reachability**: Trusted Application Zone (2.5).

*Score source: inherited (baseline 2026-04-23T19-30-00)*

---

### S-7: The Learning Loop accepts a Training Signal Stream from the Audit Logger without verifying the data source's integrity or authenticity. An attacker who compromises the Audit Logger can inject fabricated training signals, silently manipulating future model updates under the appearance of legitimate operational data.

**Component**: Long-Running Learning Loop
**Category**: Spoofing
**MAESTRO Layer**: Unclassified
**Composite Score**: 6.4 (Medium)

| Dimension | Score | Weight | Weighted |
|-----------|------:|-------:|---------:|
| CVSS Base | 9.9 | 0.35 | 3.47 |
| Exploitability | 5.0 | 0.30 | 1.50 |
| Scalability | 6.3 | 0.15 | 0.95 |
| Reachability | 2.5 | 0.20 | 0.50 |
| **Composite** | | | **6.4** |

**CVSS Vector**: `CVSS:3.1/AV:A/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H`

**Scoring Rationale**:
- **CVSS**: Training signal injection achieves scope change with full CIA impact across all three updated models (Orchestrator, Specialist, ClinAdvisor); high-severity structural attack.
- **Exploitability**: Requires compromising the Audit Logger first (prerequisite); the temporal attack pattern (training signal fraud) is documented but requires multi-step execution.
- **Scalability**: Persistent poisoning of all future model updates; temporal delay means detection is deferred until behavioral anomalies surface post-update.
- **Reachability**: Trusted Application Zone (2.5).

*Score source: inherited (baseline 2026-04-23T19-30-00)*

---

### AG-3: The Specialist Agent, once delegated a task, operates autonomously without continuous Orchestrator oversight. An adversarially crafted delegation message can cause the Specialist to execute a sequence of tool calls that constitutes a prohibited action when viewed holistically — each individual call appears permitted, but the combination achieves an unauthorized outcome.

**Component**: Specialist Agent
**Category**: Agentic Threats
**MAESTRO Layer**: Unclassified
**Composite Score**: 6.2 (Medium)

| Dimension | Score | Weight | Weighted |
|-----------|------:|-------:|---------:|
| CVSS Base | 9.4 | 0.35 | 3.29 |
| Exploitability | 5.0 | 0.30 | 1.50 |
| Scalability | 5.8 | 0.15 | 0.87 |
| Reachability | 2.5 | 0.20 | 0.50 |
| **Composite** | | | **6.2** |

**CVSS Vector**: `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:L`

**Scoring Rationale**:
- **CVSS**: Agentic default; scope-changing multi-step tool sequence achieving prohibited outcome; lower availability impact as the primary objective is data exfiltration or privilege escalation rather than service disruption.
- **Exploitability**: Requires crafting a delegation message that triggers a specific multi-step sequence; moderate skill requirement to understand the tool call permission model.
- **Scalability**: Each attack requires task-specific crafting; limited to sessions where the Specialist is delegated tasks with tool access.
- **Reachability**: Trusted Application Zone (2.5).

*Score source: inherited (baseline 2026-04-23T19-30-00)*

---

### AG-6: The MCP Tool Server acts as a privileged execution broker. Runaway or adversarially prompted agents (Orchestrator or Specialist) can cause the Tool Server to repeatedly call External API endpoints in rapid succession, exhausting the API provider's rate limits, incurring financial costs, or triggering security lockouts that deny the system access to required external capabilities.

**Component**: MCP Tool Server
**Category**: Agentic Threats
**MAESTRO Layer**: L3 — Agent Framework
**Composite Score**: 6.2 (Medium)
**Correlation Group**: Scores inherited from primary finding D-5

| Dimension | Score | Weight | Weighted |
|-----------|------:|-------:|---------:|
| CVSS Base | 6.5 | 0.35 | 2.28 |
| Exploitability | 8.0 | 0.30 | 2.40 |
| Scalability | 6.8 | 0.15 | 1.02 |
| Reachability | 2.5 | 0.20 | 0.50 |
| **Composite** | | | **6.2** |

**CVSS Vector**: `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H`

**Scoring Rationale**:
- **CVSS**: Inherited from CG-5 primary (D-5); tool call flooding achieves availability impact through connection pool exhaustion.
- **Exploitability**: Inherited from CG-5 primary. High exploitability from automated flooding.
- **Scalability**: Inherited from CG-5 primary. Systemic effect on all tool-calling sessions.
- **Reachability**: Inherited from CG-5 primary. Trusted Application Zone (2.5).

*Score source: inherited (baseline 2026-04-23T19-30-00)*

---

### D-2: The Orchestrator's inference pipeline is a bounded resource. An attacker (or malfunctioning upstream component) can exhaust the Orchestrator's capacity by flooding it with high-token-count prompts or by injecting context that forces recursive tool invocation chains. This starves legitimate user requests of Orchestrator capacity.

**Component**: LLM Agent Orchestrator
**Category**: Denial of Service
**MAESTRO Layer**: L1 — Foundation Model
**Composite Score**: 6.2 (Medium)

| Dimension | Score | Weight | Weighted |
|-----------|------:|-------:|---------:|
| CVSS Base | 6.5 | 0.35 | 2.28 |
| Exploitability | 8.0 | 0.30 | 2.40 |
| Scalability | 7.0 | 0.15 | 1.05 |
| Reachability | 2.5 | 0.20 | 0.50 |
| **Composite** | | | **6.2** |

**CVSS Vector**: `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H`

**Scoring Rationale**:
- **CVSS**: Authenticated DoS (PR:L) achieving high availability impact by exhausting inference capacity; no C or I impact.
- **Exploitability**: High-token flooding is trivially automatable; recursive tool invocation triggering requires prompt crafting but remains accessible.
- **Scalability**: Affects all concurrent user sessions; highly scriptable; detection depends on token budget monitoring which may not be deployed by default.
- **Reachability**: Trusted Application Zone (2.5).

*Score source: inherited (baseline 2026-04-23T19-30-00)*

---

### D-5: The Tool Server's capacity for concurrent External API calls is bounded by rate limits imposed by the API provider and by the Tool Server's own connection pool. A compromised agent sending high-volume tool call requests can exhaust the connection pool, causing all legitimate tool calls to fail.

**Component**: MCP Tool Server
**Category**: Denial of Service
**MAESTRO Layer**: L3 — Agent Framework
**Composite Score**: 6.2 (Medium)

| Dimension | Score | Weight | Weighted |
|-----------|------:|-------:|---------:|
| CVSS Base | 6.5 | 0.35 | 2.28 |
| Exploitability | 8.0 | 0.30 | 2.40 |
| Scalability | 6.8 | 0.15 | 1.02 |
| Reachability | 2.5 | 0.20 | 0.50 |
| **Composite** | | | **6.2** |

**CVSS Vector**: `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H`

**Scoring Rationale**:
- **CVSS**: Authenticated DoS via connection pool exhaustion; high availability impact as all tool calls fail when the pool is saturated.
- **Exploitability**: High-volume tool call flooding requires only authenticated agent access; automatable with simple scripting.
- **Scalability**: Affects all concurrent tool-calling sessions; External API lockouts have secondary financial and access-denial consequences.
- **Reachability**: Trusted Application Zone (2.5).

*Score source: inherited (baseline 2026-04-23T19-30-00)*

---

### OI-4: Improper output handling — server-side execution via Clinical Query / Context injection into the Orchestrator's downstream Tool Call Request: the Clinical Advisory Sub-Agent returns "Clinical Summary + Recommendations" to the Orchestrator via JSON-RPC. If the Orchestrator incorporates this clinical output into a subsequent Tool Call Request without sanitization, adversarial content injected into the clinical output can achieve server-side execution at the Tool Server.

**Component**: Clinical Advisory Sub-Agent
**Category**: LLM Threats
**MAESTRO Layer**: L7 — Agent Ecosystem
**Composite Score**: 6.2 (Medium)

| Dimension | Score | Weight | Weighted |
|-----------|------:|-------:|---------:|
| CVSS Base | 8.8 | 0.35 | 3.08 |
| Exploitability | 5.8 | 0.30 | 1.74 |
| Scalability | 6.0 | 0.15 | 0.90 |
| Reachability | 2.5 | 0.20 | 0.50 |
| **Composite** | | | **6.2** |

**CVSS Vector**: `CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:H/I:H/A:N`

**Scoring Rationale**:
- **CVSS**: Chained injection path (ClinAdvisor output → Orchestrator → Tool Server); scope change with high C and I impact; user interaction reflects clinical query processing trigger.
- **Exploitability**: Multi-hop injection path requires injecting adversarial content into the clinical output that survives Orchestrator incorporation into tool parameters; moderate complexity.
- **Scalability**: Affects sessions that use clinical advisory output in downstream tool calls; specific clinical workflow dependency limits scope relative to direct tool injection.
- **Reachability**: Trusted Application Zone (2.5).

*Score source: inherited (baseline 2026-04-23T19-30-00)*

---

### R-1: A user denies having submitted a particular prompt or query, claiming the record in the Audit Logger was falsified. Without request signing or non-repudiation controls at the User→Guardrails boundary, the system cannot prove the user submitted a specific input.

**Component**: User
**Category**: Repudiation
**MAESTRO Layer**: L7 — Agent Ecosystem
**Composite Score**: 6.2 (Medium)

| Dimension | Score | Weight | Weighted |
|-----------|------:|-------:|---------:|
| CVSS Base | 4.3 | 0.35 | 1.51 |
| Exploitability | 6.5 | 0.30 | 1.95 |
| Scalability | 5.5 | 0.15 | 0.83 |
| Reachability | 9.5 | 0.20 | 1.90 |
| **Composite** | | | **6.2** |

**CVSS Vector**: `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N`

**Scoring Rationale**:
- **CVSS**: Low direct CVSS (repudiation default); limited integrity impact from false denial; primary risk is legal/compliance rather than technical exploitation.
- **Exploitability**: Any authenticated user can exercise repudiation; no technical barrier; straightforward denial tactic.
- **Scalability**: Exercisable across all user sessions; detection requires cryptographic evidence that may not be deployed.
- **Reachability**: User is in the Untrusted zone (9.5); the high reachability score significantly elevates this finding's composite despite low CVSS.

*Score source: inherited (baseline 2026-04-23T19-30-00)*

---

### S-6: An attacker in the Application Zone spoofs a valid agent (Orchestrator or Specialist) to submit unauthorized tool call requests to the MCP Tool Server. Without caller authentication, any process can invoke tools with the server's external-facing credentials.

**Component**: MCP Tool Server
**Category**: Spoofing
**MAESTRO Layer**: L3 — Agent Framework
**Composite Score**: 6.2 (Medium)

| Dimension | Score | Weight | Weighted |
|-----------|------:|-------:|---------:|
| CVSS Base | 9.1 | 0.35 | 3.19 |
| Exploitability | 5.5 | 0.30 | 1.65 |
| Scalability | 5.8 | 0.15 | 0.87 |
| Reachability | 2.5 | 0.20 | 0.50 |
| **Composite** | | | **6.2** |

**CVSS Vector**: `CVSS:3.1/AV:A/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:L`

**Scoring Rationale**:
- **CVSS**: Application Zone adjacency required; agentic default vector; scope change as spoofed identity grants Tool Server's service credentials.
- **Exploitability**: Requires Application Zone access; authenticated low-privilege process can spoof agent identity without strong caller authentication.
- **Scalability**: Persistent spoofed access enables ongoing unauthorized tool invocations; limited to Application Zone actors.
- **Reachability**: Trusted Application Zone (2.5).

*Score source: inherited (baseline 2026-04-23T19-30-00)*

---

### AG-2: The Orchestrator and Specialist Agent can jointly coordinate (via the Inter-Agent Channel) to achieve a combined action that neither could perform alone or that would trigger per-agent rate limits if attempted individually. An attacker who compromises both agents (or injects coordinated prompts via the Inter-Agent Channel) can leverage this coordination for policy circumvention or joint data exfiltration.

**Component**: LLM Agent Orchestrator
**Category**: Agentic Threats
**MAESTRO Layer**: L1 — Foundation Model
**Composite Score**: 6.1 (Medium)

| Dimension | Score | Weight | Weighted |
|-----------|------:|-------:|---------:|
| CVSS Base | 9.4 | 0.35 | 3.29 |
| Exploitability | 4.8 | 0.30 | 1.44 |
| Scalability | 5.8 | 0.15 | 0.87 |
| Reachability | 2.5 | 0.20 | 0.50 |
| **Composite** | | | **6.1** |

**CVSS Vector**: `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:L`

**Scoring Rationale**:
- **CVSS**: High CVSS for agent collusion enabling scope-changed cross-component action; PR:L as authenticated access is required to influence both agents.
- **Exploitability**: Requires compromising or influencing both the Orchestrator and Specialist simultaneously; the coordination requirement significantly raises complexity.
- **Scalability**: Coordinated attacks are harder to script at scale than single-agent attacks; detection is harder because individual agent actions appear legitimate.
- **Reachability**: Trusted Application Zone (2.5).

*Score source: inherited (baseline 2026-04-23T19-30-00)*

---

### AG-4: The Channel is a shared substrate whose compromise enables agent-in-the-middle attacks: an attacker intercepts delegation messages, modifies the task parameters (replacing legitimate tool targets with attacker-controlled endpoints), and forwards the modified message to the Specialist Agent. The Specialist executes unauthorized actions believing the instructions came from the Orchestrator.

**Component**: Inter-Agent Communication Channel
**Category**: Agentic Threats
**MAESTRO Layer**: Unclassified
**Composite Score**: 6.0 (Medium)

| Dimension | Score | Weight | Weighted |
|-----------|------:|-------:|---------:|
| CVSS Base | 8.4 | 0.35 | 2.94 |
| Exploitability | 5.8 | 0.30 | 1.74 |
| Scalability | 5.5 | 0.15 | 0.83 |
| Reachability | 2.5 | 0.20 | 0.50 |
| **Composite** | | | **6.0** |

**CVSS Vector**: `CVSS:3.1/AV:A/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:L`

**Scoring Rationale**:
- **CVSS**: Adjacent network attack for channel interception; scope-changing message modification with high C and I impact.
- **Exploitability**: Requires Application Zone network position to intercept channel messages; moderate barrier.
- **Scalability**: Persistent channel access enables ongoing message modification; detection depends on message-level integrity checking.
- **Reachability**: Trusted Application Zone (2.5).

*Score source: inherited (baseline 2026-04-23T19-30-00)*

---

### E-6: The Learning Loop applies model updates with access to the Orchestrator, Specialist Agent, and Clinical Advisory Sub-Agent model parameters. If the update mechanism is compromised (poisoned training data, unauthenticated update channel), an attacker elevates from data-layer access to model-parameter control, effectively gaining the ability to inject arbitrary behaviors into all three agents via the next update cycle.

**Component**: Long-Running Learning Loop
**Category**: Privilege Escalation
**MAESTRO Layer**: Unclassified
**Composite Score**: 6.0 (Medium)

| Dimension | Score | Weight | Weighted |
|-----------|------:|-------:|---------:|
| CVSS Base | 9.9 | 0.35 | 3.47 |
| Exploitability | 4.0 | 0.30 | 1.20 |
| Scalability | 5.8 | 0.15 | 0.87 |
| Reachability | 2.5 | 0.20 | 0.50 |
| **Composite** | | | **6.0** |

**CVSS Vector**: `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H`

**Scoring Rationale**:
- **CVSS**: Highest-CVSS privilege escalation in the portfolio; model parameter control over all three agents is a full-CIA, scope-changed event.
- **Exploitability**: Very low (4.0) — the attack requires: (1) compromising the Audit Logger training stream, (2) crafting adversarial training signals, (3) surviving training data validation, (4) waiting for the next model update cycle. Complex multi-step, delayed temporal attack.
- **Scalability**: Once the model update is deployed, the effect is persistent across all future sessions for all three updated agents; limited detection opportunity before deployment.
- **Reachability**: Trusted Application Zone (2.5).

*Score source: inherited (baseline 2026-04-23T19-30-00)*

---

### I-1: The Guardrails Service leaks the content of rejected prompts (including their rejection reasons) in error responses returned to the User. An attacker can iteratively probe the filtering rules by observing rejection reasons, enabling systematic bypass through adaptive prompt crafting.

**Component**: Guardrails Service
**Category**: Information Disclosure
**MAESTRO Layer**: L6 — Security and Compliance
**Composite Score**: 5.6 (Medium)

| Dimension | Score | Weight | Weighted |
|-----------|------:|-------:|---------:|
| CVSS Base | 5.3 | 0.35 | 1.86 |
| Exploitability | 7.3 | 0.30 | 2.19 |
| Scalability | 7.0 | 0.15 | 1.05 |
| Reachability | 2.5 | 0.20 | 0.50 |
| **Composite** | | | **5.6** |

**CVSS Vector**: `CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N`

**Scoring Rationale**:
- **CVSS**: Low CVSS (rejection reason leakage has limited direct confidentiality impact); the threat is primarily an enabler for adaptive bypass rather than direct data exfiltration.
- **Exploitability**: Trivially exploitable — any unauthenticated user can observe rejection responses and iteratively refine prompts; no tooling or skill required beyond prompt submission.
- **Scalability**: Automated fuzzing of rejection patterns is fully scriptable; affects all users of the Guardrails-protected endpoint; no per-victim customization needed.
- **Reachability**: Trusted Application Zone (2.5) for the Guardrails Service component.

*Score source: inherited (baseline 2026-04-23T19-30-00)*

---

### S-3: The Orchestrator's identity is not cryptographically attested to the Specialist Agent via the Inter-Agent Communication Channel. A compromised or rogue process could inject messages into the channel impersonating the Orchestrator, issuing unauthorized delegation instructions to the Specialist Agent.

**Component**: LLM Agent Orchestrator
**Category**: Spoofing
**MAESTRO Layer**: L1 — Foundation Model
**Composite Score**: 5.9 (Medium)

| Dimension | Score | Weight | Weighted |
|-----------|------:|-------:|---------:|
| CVSS Base | 8.2 | 0.35 | 2.87 |
| Exploitability | 5.5 | 0.30 | 1.65 |
| Scalability | 5.8 | 0.15 | 0.87 |
| Reachability | 2.5 | 0.20 | 0.50 |
| **Composite** | | | **5.9** |

**CVSS Vector**: `CVSS:3.1/AV:A/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:N`

**Scoring Rationale**:
- **CVSS**: Adjacent network spoofing with scope change; high C and I from unauthorized delegation instructions reaching the Specialist.
- **Exploitability**: Requires Application Zone network access; authenticated low-privilege process required; moderate barrier.
- **Scalability**: Persistent forged delegation messages affect all Specialist sessions; limited to Application Zone actors.
- **Reachability**: Trusted Application Zone (2.5).

*Score source: inherited (baseline 2026-04-23T19-30-00)*

---

### T-3: The Specialist Agent's operational context can be tampered with by injecting adversarial content into the Delegated Task message via the Inter-Agent Communication Channel. A compromised message in the Channel can redirect the Specialist's actions, modify its tool call targets, or exfiltrate data via a fabricated task payload.

**Component**: Specialist Agent
**Category**: Tampering
**MAESTRO Layer**: Unclassified
**Composite Score**: 5.9 (Medium)

| Dimension | Score | Weight | Weighted |
|-----------|------:|-------:|---------:|
| CVSS Base | 8.2 | 0.35 | 2.87 |
| Exploitability | 5.8 | 0.30 | 1.74 |
| Scalability | 5.5 | 0.15 | 0.83 |
| Reachability | 2.5 | 0.20 | 0.50 |
| **Composite** | | | **5.9** |

**CVSS Vector**: `CVSS:3.1/AV:A/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:N`

**Scoring Rationale**:
- **CVSS**: Adjacent-network message tampering achieving scope-changed context manipulation with high C and I impact.
- **Exploitability**: Requires Application Zone access to the channel; moderately exploitable for an insider or compromised zone process.
- **Scalability**: Message-level tampering affects targeted delegation messages; not fully automated without persistent channel access.
- **Reachability**: Trusted Application Zone (2.5).

*Score source: inherited (baseline 2026-04-23T19-30-00)*

---

### T-4: Messages transiting the Inter-Agent Communication Channel can be modified in transit by a process with access to the channel's message queue or shared memory. An agent-in-the-middle attack modifies delegation messages before delivery, redirecting specialist tasks or injecting malicious instructions without detection.

**Component**: Inter-Agent Communication Channel
**Category**: Tampering
**MAESTRO Layer**: Unclassified
**Composite Score**: 5.9 (Medium)

| Dimension | Score | Weight | Weighted |
|-----------|------:|-------:|---------:|
| CVSS Base | 8.2 | 0.35 | 2.87 |
| Exploitability | 5.8 | 0.30 | 1.74 |
| Scalability | 5.5 | 0.15 | 0.83 |
| Reachability | 2.5 | 0.20 | 0.50 |
| **Composite** | | | **5.9** |

**CVSS Vector**: `CVSS:3.1/AV:A/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:N`

**Scoring Rationale**:
- **CVSS**: In-transit message modification; scope change as tampered messages affect Specialist behavior; high C and I from redirected task execution.
- **Exploitability**: Identical to T-3 — requires Application Zone message queue access; moderately accessible.
- **Scalability**: Affects all messages transiting the channel while the attacker maintains queue access.
- **Reachability**: Trusted Application Zone (2.5).

*Score source: inherited (baseline 2026-04-23T19-30-00)*

---

### S-8: The External API provider's identity is not verified beyond TLS certificate validation. An attacker performing DNS hijacking or a BGP route hijack can redirect the MCP Tool Server's outbound API calls to an attacker-controlled server that returns malicious tool results.

**Component**: External API
**Category**: Spoofing
**MAESTRO Layer**: Unclassified
**Composite Score**: 5.8 (Medium)

| Dimension | Score | Weight | Weighted |
|-----------|------:|-------:|---------:|
| CVSS Base | 7.4 | 0.35 | 2.59 |
| Exploitability | 4.3 | 0.30 | 1.29 |
| Scalability | 4.5 | 0.15 | 0.68 |
| Reachability | 6.0 | 0.20 | 1.20 |
| **Composite** | | | **5.8** |

**CVSS Vector**: `CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:N`

**Scoring Rationale**:
- **CVSS**: High AC reflecting the complexity of DNS/BGP hijacking attacks; no privileges required but attack complexity reduces the score significantly.
- **Exploitability**: DNS/BGP route hijacking requires significant network-level capability and infrastructure; low accessibility for most attackers; well-documented but nation-state-level capability in practice.
- **Scalability**: BGP hijacking can redirect global traffic but requires substantial resources; limited scalability for most threat actors.
- **Reachability**: External API is in the Semi-Trusted External Services zone (6.0 with "external" keyword adjustment).

*Score source: inherited (baseline 2026-04-23T19-30-00)*

---

### S-9: The Clinical Advisory Sub-Agent receives Clinical Query / Context messages from the LLM Agent Orchestrator via JSON-RPC without per-message sender attestation. A compromised or rogue Application Zone process can inject crafted clinical queries impersonating the Orchestrator, causing the sub-agent to process unauthorized requests and return manipulated clinical summaries that enter the Orchestrator's response path.

**Component**: Clinical Advisory Sub-Agent
**Category**: Spoofing
**MAESTRO Layer**: L7 — Agent Ecosystem
**Composite Score**: 5.8 (Medium)

| Dimension | Score | Weight | Weighted |
|-----------|------:|-------:|---------:|
| CVSS Base | 8.2 | 0.35 | 2.87 |
| Exploitability | 5.5 | 0.30 | 1.65 |
| Scalability | 5.3 | 0.15 | 0.80 |
| Reachability | 2.5 | 0.20 | 0.50 |
| **Composite** | | | **5.8** |

**CVSS Vector**: `CVSS:3.1/AV:A/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:N`

**Scoring Rationale**:
- **CVSS**: Adjacent-network JSON-RPC spoofing with scope change; high C and I from fabricated clinical summaries entering the Orchestrator response path.
- **Exploitability**: Requires Application Zone access to inject clinical queries; moderate barrier consistent with other intra-zone spoofing threats.
- **Scalability**: Targeted clinical advisory path; lower scalability than broad Orchestrator-level spoofing.
- **Reachability**: Trusted Application Zone (2.5).

*Score source: inherited (baseline 2026-04-23T19-30-00)*

---

### T-7: The Audit Logger entries can be tampered with by a process with write access to the log store. Modifying or deleting log entries corrupts the training signal stream consumed by the Long-Running Learning Loop, causing poisoned model updates, and also destroys forensic evidence needed for incident response.

**Component**: Audit Logger
**Category**: Tampering
**MAESTRO Layer**: L5 — Evaluation and Observability
**Composite Score**: 5.8 (Medium)

| Dimension | Score | Weight | Weighted |
|-----------|------:|-------:|---------:|
| CVSS Base | 8.5 | 0.35 | 2.98 |
| Exploitability | 5.0 | 0.30 | 1.50 |
| Scalability | 5.3 | 0.15 | 0.80 |
| Reachability | 2.5 | 0.20 | 0.50 |
| **Composite** | | | **5.8** |

**CVSS Vector**: `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:N/I:H/A:L`

**Scoring Rationale**:
- **CVSS**: Scope-changing log tampering with high integrity impact (audit trail corruption) and low availability impact; confidentiality is not directly impacted by modification.
- **Exploitability**: Requires write access to the log store; authenticated service account compromise needed; moderate barrier.
- **Scalability**: Systematic log modification affects the entire training signal stream; detection depends on Merkle-chain verification which may not be deployed.
- **Reachability**: Trusted Application Zone (2.5).

*Score source: inherited (baseline 2026-04-23T19-30-00)*

---

### AG-7: The Learning Loop's model update mechanism, when fed adversarially crafted training signals, can be exploited for a temporal autonomy attack: the training data contains instructions that cause the updated model to expand its autonomous action scope on the next cycle, gradually accumulating capabilities it was not originally authorized to have.

**Component**: Long-Running Learning Loop
**Category**: Agentic Threats
**MAESTRO Layer**: Unclassified
**Composite Score**: 5.6 (Medium)

| Dimension | Score | Weight | Weighted |
|-----------|------:|-------:|---------:|
| CVSS Base | 8.5 | 0.35 | 2.98 |
| Exploitability | 4.0 | 0.30 | 1.20 |
| Scalability | 6.0 | 0.15 | 0.90 |
| Reachability | 2.5 | 0.20 | 0.50 |
| **Composite** | | | **5.6** |

**CVSS Vector**: `CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:C/C:H/I:H/A:L`

**Scoring Rationale**:
- **CVSS**: Temporal autonomy expansion with scope change; high C and I from unauthorized capability accumulation; low availability impact unless the expanded capabilities cause resource contention.
- **Exploitability**: Very low (4.0) — capability expansion via training data requires sophisticated adversarial ML expertise, Audit Logger access, and surviving multiple validation gates.
- **Scalability**: Gradual autonomy expansion affects all agents updated by the Learning Loop; temporal persistence makes detection very difficult.
- **Reachability**: Trusted Application Zone (2.5).

*Score source: inherited (baseline 2026-04-23T19-30-00)*

---

### D-9: The Clinical Advisory Sub-Agent is invoked by the Orchestrator for each clinical query via JSON-RPC and performs a vector search against the Knowledge Base. High-volume or adversarially-crafted clinical queries can exhaust the sub-agent's inference capacity or starve the Knowledge Base of query capacity, disrupting both clinical advisory and baseline Orchestrator retrieval operations.

**Component**: Clinical Advisory Sub-Agent
**Category**: Denial of Service
**MAESTRO Layer**: L7 — Agent Ecosystem
**Composite Score**: 5.6 (Medium)

| Dimension | Score | Weight | Weighted |
|-----------|------:|-------:|---------:|
| CVSS Base | 6.5 | 0.35 | 2.28 |
| Exploitability | 6.5 | 0.30 | 1.95 |
| Scalability | 6.0 | 0.15 | 0.90 |
| Reachability | 2.5 | 0.20 | 0.50 |
| **Composite** | | | **5.6** |

**CVSS Vector**: `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H`

**Scoring Rationale**:
- **CVSS**: Authenticated DoS via clinical query flooding; high availability impact as clinical advisory and KB retrieval are jointly disrupted.
- **Exploitability**: Slightly lower than general orchestrator DoS because the attack requires accessing the clinical advisory invocation path; still automatable with authenticated access.
- **Scalability**: Shared KB dependency means clinical DoS cascades to baseline Orchestrator retrieval; dual disruption amplifies impact.
- **Reachability**: Trusted Application Zone (2.5).

*Score source: inherited (baseline 2026-04-23T19-30-00)*

---

### LLM-9: Training data poisoning of the Specialist Agent via the Learning Loop: adversarially crafted audit log entries from the Specialist's own decision logs (self-poisoning) can be incorporated into the Learning Loop's training signal and returned as a model update that shifts the Specialist's behavior toward attacker-preferred outputs.

**Component**: Specialist Agent
**Category**: LLM Threats
**MAESTRO Layer**: Unclassified
**Composite Score**: 5.6 (Medium)

| Dimension | Score | Weight | Weighted |
|-----------|------:|-------:|---------:|
| CVSS Base | 8.5 | 0.35 | 2.98 |
| Exploitability | 4.3 | 0.30 | 1.29 |
| Scalability | 5.8 | 0.15 | 0.87 |
| Reachability | 2.5 | 0.20 | 0.50 |
| **Composite** | | | **5.6** |

**CVSS Vector**: `CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:C/C:H/I:H/A:N`

**Scoring Rationale**:
- **CVSS**: Self-poisoning via Specialist's own audit entries; high complexity (temporal attack); scope change as model update affects all Specialist instances.
- **Exploitability**: Requires crafting Specialist interactions that, when logged, function as adversarial training signals; highly sophisticated attack requiring ML expertise.
- **Scalability**: Affects all Specialist instances after the model update; temporal delay obscures attribution.
- **Reachability**: Trusted Application Zone (2.5).

*Score source: inherited (baseline 2026-04-23T19-30-00)*

---

### D-6: The Knowledge Base can be rendered unavailable by an attacker who issues high-volume, complex vector search queries (exhaustive nearest-neighbor searches with high dimensionality). This degrades retrieval performance for the Orchestrator.

**Component**: Knowledge Base
**Category**: Denial of Service
**MAESTRO Layer**: L2 — Data Operations
**Composite Score**: 5.7 (Medium)

| Dimension | Score | Weight | Weighted |
|-----------|------:|-------:|---------:|
| CVSS Base | 6.5 | 0.35 | 2.28 |
| Exploitability | 6.8 | 0.30 | 2.04 |
| Scalability | 6.5 | 0.15 | 0.98 |
| Reachability | 2.0 | 0.20 | 0.40 |
| **Composite** | | | **5.7** |

**CVSS Vector**: `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H`

**Scoring Rationale**:
- **CVSS**: Authenticated DoS; high availability impact from KB retrieval degradation affecting the Orchestrator's context assembly.
- **Exploitability**: Query flooding is scriptable with any authenticated vector search client; complexity budget exhaustion can be triggered with crafted high-dimensionality queries.
- **Scalability**: Affects all Orchestrator and ClinAdvisor retrieval sessions simultaneously; query-level DoS is fully automatable.
- **Reachability**: Knowledge Base in Trusted zone with "data store" keyword adjustment (-0.5) yields reachability of 2.0.

*Score source: inherited (baseline 2026-04-23T19-30-00)*

---

### LLM-11: Data poisoning of the Learning Loop's training signal: the audit log training stream is the Learning Loop's primary data source. An attacker who systematically injects adversarially crafted interaction records into the Audit Logger creates poisoned training data that shifts the updated models' behavior over the training cycle — a temporal data poisoning attack with delayed activation at the next model update.

**Component**: Long-Running Learning Loop
**Category**: LLM Threats
**MAESTRO Layer**: Unclassified
**Composite Score**: 5.7 (Medium)
**Correlation Group**: Scores inherited from primary finding T-8

| Dimension | Score | Weight | Weighted |
|-----------|------:|-------:|---------:|
| CVSS Base | 8.5 | 0.35 | 2.98 |
| Exploitability | 4.3 | 0.30 | 1.29 |
| Scalability | 6.3 | 0.15 | 0.95 |
| Reachability | 2.5 | 0.20 | 0.50 |
| **Composite** | | | **5.7** |

**CVSS Vector**: `CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:C/C:H/I:H/A:N`

**Scoring Rationale**:
- **CVSS**: Inherited from CG-2 primary (T-8); training data poisoning via audit log manipulation with complex timing requirements.
- **Exploitability**: Inherited from CG-2 primary. Temporal attack requiring coordinated audit log injection.
- **Scalability**: Inherited from CG-2 primary. Affects all future model instances after a poisoned update.
- **Reachability**: Inherited from CG-2 primary. Trusted Application Zone (2.5).

*Score source: inherited (baseline 2026-04-23T19-30-00)*

---

### T-8: The training signal stream from the Audit Logger to the Learning Loop can be poisoned (data poisoning attack) by injecting adversarial entries into the Audit Logger before training runs. A time-delayed attack (temporal attack pattern) inserts adversarial training signals that activate only when a specific trigger pattern appears in future user prompts — a sleeper-agent injection via the model update cycle.

**Component**: Long-Running Learning Loop
**Category**: Tampering
**MAESTRO Layer**: Unclassified
**Composite Score**: 5.7 (Medium)

| Dimension | Score | Weight | Weighted |
|-----------|------:|-------:|---------:|
| CVSS Base | 8.5 | 0.35 | 2.98 |
| Exploitability | 4.3 | 0.30 | 1.29 |
| Scalability | 6.3 | 0.15 | 0.95 |
| Reachability | 2.5 | 0.20 | 0.50 |
| **Composite** | | | **5.7** |

**CVSS Vector**: `CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:C/C:H/I:H/A:N`

**Scoring Rationale**:
- **CVSS**: High-complexity temporal attack requiring precise timing for trigger activation; scope change affects all three updated models; high C and I from behavioral manipulation.
- **Exploitability**: Very low exploitability (4.3) — sleeper-agent injection requires: crafting trigger-activated training signals, audit log write access, surviving training data validation, and waiting for model update deployment.
- **Scalability**: Persistent effect across all future sessions once deployed; the trigger-based activation allows targeted exploitation that is hard to detect without behavioral monitoring.
- **Reachability**: Trusted Application Zone (2.5).

*Score source: inherited (baseline 2026-04-23T19-30-00)*

---

### D-3: The Specialist Agent is invoked by the Orchestrator via the Inter-Agent Channel. An adversarially crafted delegation message that triggers computationally expensive subtasks can exhaust the Specialist Agent's processing capacity, preventing it from completing legitimate delegated work.

**Component**: Specialist Agent
**Category**: Denial of Service
**MAESTRO Layer**: Unclassified
**Composite Score**: 5.5 (Medium)

| Dimension | Score | Weight | Weighted |
|-----------|------:|-------:|---------:|
| CVSS Base | 5.7 | 0.35 | 2.00 |
| Exploitability | 6.8 | 0.30 | 2.04 |
| Scalability | 6.3 | 0.15 | 0.95 |
| Reachability | 2.5 | 0.20 | 0.50 |
| **Composite** | | | **5.5** |

**CVSS Vector**: `CVSS:3.1/AV:A/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H`

**Scoring Rationale**:
- **CVSS**: Adjacent-network DoS via delegation message flooding; high availability impact from Specialist capacity exhaustion; requires Application Zone access.
- **Exploitability**: Computationally expensive task injection through delegation messages is straightforward with channel access; task queue depth limits may not be enforced.
- **Scalability**: Affects all Specialist-delegated workloads simultaneously; crafted tasks can be mass-submitted once channel access is obtained.
- **Reachability**: Trusted Application Zone (2.5).

*Score source: inherited (baseline 2026-04-23T19-30-00)*

---

### D-4: The Channel's message queue can be flooded by a compromised agent or a malfunctioning process, causing legitimate messages to be dropped, delayed, or rejected. Queue saturation disrupts coordination between Orchestrator and Specialist Agent.

**Component**: Inter-Agent Communication Channel
**Category**: Denial of Service
**MAESTRO Layer**: Unclassified
**Composite Score**: 5.5 (Medium)

| Dimension | Score | Weight | Weighted |
|-----------|------:|-------:|---------:|
| CVSS Base | 5.7 | 0.35 | 2.00 |
| Exploitability | 6.8 | 0.30 | 2.04 |
| Scalability | 6.5 | 0.15 | 0.98 |
| Reachability | 2.5 | 0.20 | 0.50 |
| **Composite** | | | **5.5** |

**CVSS Vector**: `CVSS:3.1/AV:A/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H`

**Scoring Rationale**:
- **CVSS**: Queue flooding DoS; high availability impact from coordination disruption; requires Application Zone access.
- **Exploitability**: Message flooding is trivially automatable with any Application Zone process; per-sender rate limits may not be enforced.
- **Scalability**: Queue saturation affects all in-flight messages across all agent sessions; slightly higher scriptability than D-3 because the channel is a shared substrate.
- **Reachability**: Trusted Application Zone (2.5).

*Score source: inherited (baseline 2026-04-23T19-30-00)*

---

### D-7: The Audit Logger can be overwhelmed by a log-flooding attack from a compromised Application Zone process, causing legitimate log entries to be dropped or the logger to become unavailable, creating audit gaps and potentially cascading to block all pipeline operations that wait for log confirmation.

**Component**: Audit Logger
**Category**: Denial of Service
**MAESTRO Layer**: L5 — Evaluation and Observability
**Composite Score**: 5.5 (Medium)

| Dimension | Score | Weight | Weighted |
|-----------|------:|-------:|---------:|
| CVSS Base | 5.7 | 0.35 | 2.00 |
| Exploitability | 6.8 | 0.30 | 2.04 |
| Scalability | 6.3 | 0.15 | 0.95 |
| Reachability | 2.5 | 0.20 | 0.50 |
| **Composite** | | | **5.5** |

**CVSS Vector**: `CVSS:3.1/AV:A/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H`

**Scoring Rationale**:
- **CVSS**: Log flooding DoS; high availability impact as audit gaps cascade to block dependent operations; requires Application Zone write access to the log store.
- **Exploitability**: Log flooding is automatable with any Application Zone process that has write access to the logger.
- **Scalability**: Affects the entire pipeline's audit capability; write rate limits may not be enforced by default.
- **Reachability**: Trusted Application Zone (2.5).

*Score source: inherited (baseline 2026-04-23T19-30-00)*

---

### AG-8: Insecure Inter-Agent Communication (Category 9 — OWASP ASI07:2026): The Inter-Agent Communication Channel connects the LLM Agent Orchestrator, Specialist Agent, and (via the Orchestrator) the Clinical Advisory Sub-Agent without declaring mutual authentication, inter-agent message signing, or nonce-based replay prevention. A network-positioned attacker or a compromised Application Zone process can intercept delegation messages (AML.T0060 agent-in-the-middle topology) and replay, modify, or inject instructions to the Specialist Agent or the Orchestrator without any authentic-source signal available to the receiving component.

**Component**: Inter-Agent Communication Channel
**Category**: Agentic Threats
**MAESTRO Layer**: Unclassified
**Composite Score**: 5.5 (Medium)
**Correlation Group**: Scores inherited from primary finding D-4

| Dimension | Score | Weight | Weighted |
|-----------|------:|-------:|---------:|
| CVSS Base | 5.7 | 0.35 | 2.00 |
| Exploitability | 6.8 | 0.30 | 2.04 |
| Scalability | 6.5 | 0.15 | 0.98 |
| Reachability | 2.5 | 0.20 | 0.50 |
| **Composite** | | | **5.5** |

**CVSS Vector**: `CVSS:3.1/AV:A/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H`

**Scoring Rationale**:
- **CVSS**: Inherited from CG-7 primary (D-4); the insecure channel design shares the same attack surface and availability impact as message queue flooding — an attacker who can inject/replay messages achieves the same coordination disruption as flooding. The absence of mTLS, message signing, and replay prevention enables this attack path with the same adjacent-network, low-privilege prerequisite.
- **Exploitability**: Inherited from CG-7 primary. Message injection and replay on an unauthenticated channel substrate is automatable once Application Zone access is obtained.
- **Scalability**: Inherited from CG-7 primary. Insecure channel affects all inter-agent coordination sessions systematically.
- **Reachability**: Inherited from CG-7 primary. Trusted Application Zone (2.5).

*Score source: inherited (correlation primary D-4, baseline 2026-04-23T19-30-00)*

---

### I-6: The Knowledge Base exposes its full document corpus to any process that can issue a vector search query. Without query-result access controls, a compromised Orchestrator or injected context can exfiltrate the entire corpus by issuing exhaustive search queries.

**Component**: Knowledge Base
**Category**: Information Disclosure
**MAESTRO Layer**: L2 — Data Operations
**Composite Score**: 5.4 (Medium)

| Dimension | Score | Weight | Weighted |
|-----------|------:|-------:|---------:|
| CVSS Base | 6.5 | 0.35 | 2.28 |
| Exploitability | 5.8 | 0.30 | 1.74 |
| Scalability | 6.3 | 0.15 | 0.95 |
| Reachability | 2.0 | 0.20 | 0.40 |
| **Composite** | | | **5.4** |

**CVSS Vector**: `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N`

**Scoring Rationale**:
- **CVSS**: Authenticated query-based corpus exfiltration; high confidentiality impact from full KB extraction; no integrity or availability direct impact.
- **Exploitability**: Requires authenticated access to the KB query interface; exhaustive vector search is straightforward with any vector DB client.
- **Scalability**: Exhaustive corpus extraction can be automated; query-result limits are the primary mitigating control if deployed.
- **Reachability**: Knowledge Base reachability 2.0 (Trusted zone, data store keyword adjustment).

*Score source: inherited (baseline 2026-04-23T19-30-00)*

---

### I-7: The Audit Logger aggregates sensitive data from all Application Zone components. Unauthorized read access to the logger (misconfigured access controls, insider threat) exposes the full operational history of the agent system, including user prompts, model decisions, tool call parameters, and filter rule triggers.

**Component**: Audit Logger
**Category**: Information Disclosure
**MAESTRO Layer**: L5 — Evaluation and Observability
**Composite Score**: 5.4 (Medium)

| Dimension | Score | Weight | Weighted |
|-----------|------:|-------:|---------:|
| CVSS Base | 6.5 | 0.35 | 2.28 |
| Exploitability | 5.8 | 0.30 | 1.74 |
| Scalability | 6.0 | 0.15 | 0.90 |
| Reachability | 2.5 | 0.20 | 0.50 |
| **Composite** | | | **5.4** |

**CVSS Vector**: `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N`

**Scoring Rationale**:
- **CVSS**: Authenticated read access to the full audit trail; high confidentiality impact from operational history exposure including prompts, decisions, and tool parameters.
- **Exploitability**: Requires read access to the log store; misconfigured access controls or insider threat are the primary vectors.
- **Scalability**: Bulk log extraction is automatable; the aggregated nature of the audit trail amplifies per-access impact.
- **Reachability**: Trusted Application Zone (2.5).

*Score source: inherited (baseline 2026-04-23T19-30-00)*

---

### D-8: The Learning Loop is a resource-intensive batch process. A high-volume data injection into the Audit Logger (training signal flooding) can cause the Learning Loop to enter runaway processing, consuming excessive compute resources and either blocking legitimate model updates or degrading system performance.

**Component**: Long-Running Learning Loop
**Category**: Denial of Service
**MAESTRO Layer**: Unclassified
**Composite Score**: 5.3 (Medium)

| Dimension | Score | Weight | Weighted |
|-----------|------:|-------:|---------:|
| CVSS Base | 6.5 | 0.35 | 2.28 |
| Exploitability | 5.8 | 0.30 | 1.74 |
| Scalability | 5.5 | 0.15 | 0.83 |
| Reachability | 2.5 | 0.20 | 0.50 |
| **Composite** | | | **5.3** |

**CVSS Vector**: `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H`

**Scoring Rationale**:
- **CVSS**: Training signal flooding causing runaway batch processing; high availability impact from compute exhaustion blocking legitimate model updates.
- **Exploitability**: Requires write access to the Audit Logger; training signal flooding is straightforward once that access is obtained.
- **Scalability**: Affects the entire model update pipeline; resource quotas may not be enforced on batch workloads by default.
- **Reachability**: Trusted Application Zone (2.5).

*Score source: inherited (baseline 2026-04-23T19-30-00)*

---

### I-5: Tool results from External API calls may contain sensitive data (user records, financial data, PII) that the Tool Server logs verbatim to the Audit Logger. If Audit Logger access is not restricted, this data becomes accessible to any process that reads the audit trail, including the Learning Loop's training pipeline.

**Component**: MCP Tool Server
**Category**: Information Disclosure
**MAESTRO Layer**: L3 — Agent Framework
**Composite Score**: 5.3 (Medium)

| Dimension | Score | Weight | Weighted |
|-----------|------:|-------:|---------:|
| CVSS Base | 6.5 | 0.35 | 2.28 |
| Exploitability | 5.5 | 0.30 | 1.65 |
| Scalability | 5.5 | 0.15 | 0.83 |
| Reachability | 2.5 | 0.20 | 0.50 |
| **Composite** | | | **5.3** |

**CVSS Vector**: `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N`

**Scoring Rationale**:
- **CVSS**: Authenticated access to verbatim-logged tool results containing PII and sensitive external data; high confidentiality impact.
- **Exploitability**: Requires read access to the Audit Logger; straightforward once access controls are misconfigured or compromised.
- **Scalability**: PII propagation into the training pipeline is a systemic issue affecting all logged tool calls; hard to remediate retroactively.
- **Reachability**: Trusted Application Zone (2.5).

*Score source: inherited (baseline 2026-04-23T19-30-00)*

---

### LLM-3: Model theft via systematic API probing: an attacker issues carefully crafted queries to extract the Orchestrator's model behavior, fine-tuning data characteristics, or system prompt contents through systematic probing, enabling the attacker to build a functional replica of the model or extract proprietary training data.

**Component**: LLM Agent Orchestrator
**Category**: LLM Threats
**MAESTRO Layer**: L1 — Foundation Model
**Composite Score**: 5.3 (Medium)

| Dimension | Score | Weight | Weighted |
|-----------|------:|-------:|---------:|
| CVSS Base | 6.5 | 0.35 | 2.28 |
| Exploitability | 5.5 | 0.30 | 1.65 |
| Scalability | 6.0 | 0.15 | 0.90 |
| Reachability | 2.5 | 0.20 | 0.50 |
| **Composite** | | | **5.3** |

**CVSS Vector**: `CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:N`

**Scoring Rationale**:
- **CVSS**: Model extraction via systematic probing; user interaction required for each query; high confidentiality impact from proprietary model behavior/training data exposure; no integrity or availability impact.
- **Exploitability**: Systematic probing requires many queries (moderate complexity); ML knowledge helpful but not required; rate limiting is the primary defense.
- **Scalability**: Automatable query generation for model extraction; query anomaly detection may not be deployed; extraction can be distributed across many sessions.
- **Reachability**: Trusted Application Zone (2.5).

*Score source: inherited (baseline 2026-04-23T19-30-00)*

---

### LLM-12: Model theft via Learning Loop output monitoring: an attacker with observability access to the Learning Loop's model update artifacts (parameter diffs, update packages) can reconstruct the model's architecture, parameters, or training data characteristics — effectively stealing the proprietary model.

**Component**: Long-Running Learning Loop
**Category**: LLM Threats
**MAESTRO Layer**: Unclassified
**Composite Score**: 5.3 (Medium)

| Dimension | Score | Weight | Weighted |
|-----------|------:|-------:|---------:|
| CVSS Base | 6.5 | 0.35 | 2.28 |
| Exploitability | 5.8 | 0.30 | 1.74 |
| Scalability | 5.5 | 0.15 | 0.83 |
| Reachability | 2.5 | 0.20 | 0.50 |
| **Composite** | | | **5.3** |

**CVSS Vector**: `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N`

**Scoring Rationale**:
- **CVSS**: Authenticated access to model update artifacts enabling model reconstruction; high confidentiality impact from proprietary model theft.
- **Exploitability**: Requires observability access to the Learning Loop's output artifacts; insider or misconfigured access control is the primary vector.
- **Scalability**: One-time artifact access yields the complete model; no repeated exploitation needed.
- **Reachability**: Trusted Application Zone (2.5).

*Score source: inherited (baseline 2026-04-23T19-30-00)*

---

### T-6: The Knowledge Base corpus can be tampered with (poisoned) by an attacker who gains write access. Injecting adversarial documents into the knowledge store causes the Orchestrator to retrieve and incorporate malicious context during vector search, corrupting the Orchestrator's responses at scale.

**Component**: Knowledge Base
**Category**: Tampering
**MAESTRO Layer**: L2 — Data Operations
**Composite Score**: 5.3 (Medium)

| Dimension | Score | Weight | Weighted |
|-----------|------:|-------:|---------:|
| CVSS Base | 7.7 | 0.35 | 2.70 |
| Exploitability | 4.5 | 0.30 | 1.35 |
| Scalability | 5.5 | 0.15 | 0.83 |
| Reachability | 2.0 | 0.20 | 0.40 |
| **Composite** | | | **5.3** |

**CVSS Vector**: `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:N/I:H/A:N`

**Scoring Rationale**:
- **CVSS**: Scope-changing document injection via write access; high integrity impact as poisoned documents corrupt Orchestrator context at scale; no direct confidentiality or availability impact.
- **Exploitability**: Requires write access to the KB (service account compromise or misconfiguration); document ingestion pipeline access needed; moderate barrier.
- **Scalability**: Once injected, adversarial documents affect all retrieval sessions persistently; document-level integrity checks are the primary detection control.
- **Reachability**: Knowledge Base reachability 2.0 (Trusted zone, data store keyword adjustment).

*Score source: inherited (baseline 2026-04-23T19-30-00)*

---

### R-9: The Clinical Advisory Sub-Agent denies having generated a specific clinical summary or recommendation. Without non-repudiable logs of each clinical output (with content hash and the KB documents retrieved to produce it), clinical decisions influenced by sub-agent outputs cannot be attributed, and the sub-agent cannot be held accountable for hallucinated or incorrect recommendations.

**Component**: Clinical Advisory Sub-Agent
**Category**: Repudiation
**MAESTRO Layer**: L7 — Agent Ecosystem
**Composite Score**: 5.2 (Medium)

| Dimension | Score | Weight | Weighted |
|-----------|------:|-------:|---------:|
| CVSS Base | 6.5 | 0.35 | 2.28 |
| Exploitability | 5.3 | 0.30 | 1.59 |
| Scalability | 5.5 | 0.15 | 0.83 |
| Reachability | 2.5 | 0.20 | 0.50 |
| **Composite** | | | **5.2** |

**CVSS Vector**: `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N`

**Scoring Rationale**:
- **CVSS**: Repudiation with high integrity impact from clinical provenance loss; authenticated sub-agent can deny outputs without cryptographic attribution controls.
- **Exploitability**: Any session-level actor can exercise repudiation when clinical logs lack content hashes and signatures; straightforward denial tactic in clinical contexts.
- **Scalability**: Affects all clinical advisory sessions lacking non-repudiation controls; systemic gap rather than per-instance.
- **Reachability**: Trusted Application Zone (2.5).

*Score source: inherited (baseline 2026-04-23T19-30-00)*

---

### S-2: An attacker spoofs the Guardrails Service by sending crafted requests directly to the LLM Agent Orchestrator's internal endpoint, bypassing validation entirely. If internal service endpoints lack mutual TLS authentication, any service within the Application Zone can impersonate the Guardrails.

**Component**: Guardrails Service
**Category**: Spoofing
**MAESTRO Layer**: L6 — Security and Compliance
**Composite Score**: 5.2 (Medium)

| Dimension | Score | Weight | Weighted |
|-----------|------:|-------:|---------:|
| CVSS Base | 6.3 | 0.35 | 2.21 |
| Exploitability | 5.5 | 0.30 | 1.65 |
| Scalability | 5.3 | 0.15 | 0.80 |
| Reachability | 2.5 | 0.20 | 0.50 |
| **Composite** | | | **5.2** |

**CVSS Vector**: `CVSS:3.1/AV:A/AC:L/PR:L/UI:N/S:U/C:H/I:L/A:N`

**Scoring Rationale**:
- **CVSS**: Adjacent-network Guardrails impersonation; high confidentiality impact from bypassing validation; low integrity impact as the attack enables unfiltered prompt delivery rather than direct data modification.
- **Exploitability**: Requires Application Zone process access; mTLS absent means any Application Zone process can send requests to the Orchestrator's internal endpoint.
- **Scalability**: Persistent bypass channel once established; limited to Application Zone actors.
- **Reachability**: Trusted Application Zone (2.5).

*Score source: inherited (baseline 2026-04-23T19-30-00)*

---

### I-4: Messages on the Inter-Agent Communication Channel are observable by any process in the Application Zone with access to the shared message bus or queue. Unencrypted or insufficiently access-controlled inter-agent messages expose sensitive task context to unauthorized observers.

**Component**: Inter-Agent Communication Channel
**Category**: Information Disclosure
**MAESTRO Layer**: Unclassified
**Composite Score**: 5.1 (Medium)

| Dimension | Score | Weight | Weighted |
|-----------|------:|-------:|---------:|
| CVSS Base | 5.7 | 0.35 | 2.00 |
| Exploitability | 5.8 | 0.30 | 1.74 |
| Scalability | 5.8 | 0.15 | 0.87 |
| Reachability | 2.5 | 0.20 | 0.50 |
| **Composite** | | | **5.1** |

**CVSS Vector**: `CVSS:3.1/AV:A/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N`

**Scoring Rationale**:
- **CVSS**: Adjacent-network message observation; high confidentiality impact from sensitive task context exposure; no integrity or availability impact from passive observation.
- **Exploitability**: Requires Application Zone network access; message bus observation is passive and does not require active injection.
- **Scalability**: Persistent message observation affects all inter-agent traffic; systematic eavesdropping is fully passive and scriptable.
- **Reachability**: Trusted Application Zone (2.5).

*Score source: inherited (baseline 2026-04-23T19-30-00)*

---

### R-8: The External API provider denies having returned a specific response to the MCP Tool Server, enabling disputes over what data was received and acted upon.

**Component**: External API
**Category**: Repudiation
**MAESTRO Layer**: Unclassified
**Composite Score**: 5.0 (Medium)

| Dimension | Score | Weight | Weighted |
|-----------|------:|-------:|---------:|
| CVSS Base | 4.3 | 0.35 | 1.51 |
| Exploitability | 5.0 | 0.30 | 1.50 |
| Scalability | 5.3 | 0.15 | 0.80 |
| Reachability | 6.0 | 0.20 | 1.20 |
| **Composite** | | | **5.0** |

**CVSS Vector**: `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N`

**Scoring Rationale**:
- **CVSS**: Repudiation default; limited direct impact from provider denial; primary risk is dispute resolution and accountability rather than technical exploitation.
- **Exploitability**: Provider-side repudiation requires no technical capability from the attacker; standard dispute tactic.
- **Scalability**: Exercisable per API call without additional effort; response signing protocols would mitigate at scale.
- **Reachability**: External API is in Semi-Trusted External Services zone (6.0), which elevates this finding's composite.

*Score source: inherited (baseline 2026-04-23T19-30-00)*

---

### T-1: An attacker with write access to the Guardrails Service configuration (via a misconfigured admin endpoint or insider threat) modifies filtering rules to allow previously-blocked prompt patterns through to the Orchestrator, silently bypassing content policy enforcement.

**Component**: Guardrails Service
**Category**: Tampering
**MAESTRO Layer**: L6 — Security and Compliance
**Composite Score**: 5.0 (Medium)

| Dimension | Score | Weight | Weighted |
|-----------|------:|-------:|---------:|
| CVSS Base | 6.6 | 0.35 | 2.31 |
| Exploitability | 4.8 | 0.30 | 1.44 |
| Scalability | 5.0 | 0.15 | 0.75 |
| Reachability | 2.5 | 0.20 | 0.50 |
| **Composite** | | | **5.0** |

**CVSS Vector**: `CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:C/C:N/I:H/A:N`

**Scoring Rationale**:
- **CVSS**: High privilege required for config modification (PR:H); scope change as modified rules affect the Orchestrator's input processing; high integrity impact from silently allowing blocked prompts.
- **Exploitability**: Requires admin/insider access to the Guardrails configuration; dual-approval enforcement is the primary control.
- **Scalability**: Modified rules affect all subsequent user sessions silently; detection requires comparing rule states over time.
- **Reachability**: Trusted Application Zone (2.5).

*Score source: inherited (baseline 2026-04-23T19-30-00)*

---

### AGP-01: Multi-agent emergent behavior — cascading failures or feedback amplification bypassing per-agent safety evaluation

**Component**: LLM Agent Orchestrator
**Category**: Agentic Threats
**MAESTRO Layer**: L1 — Foundation Model
**Composite Score**: 4.6 (Medium)

| Dimension | Score | Weight | Weighted |
|-----------|------:|-------:|---------:|
| CVSS Base | 5.5 | 0.35 | 1.93 |
| Exploitability | 4.5 | 0.30 | 1.35 |
| Scalability | 5.8 | 0.15 | 0.87 |
| Reachability | 2.5 | 0.20 | 0.50 |
| **Composite** | | | **4.6** |

**CVSS Vector**: `CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:C/C:L/I:L/A:L`

**Scoring Rationale**:
- **CVSS**: High complexity reflecting the emergent and probabilistic nature of multi-agent feedback amplification; scope changes because cascading failures propagate across the Orchestrator, Specialist, and ClinAdvisor; lower C/I/A (each individual impact is limited, but collective cascade can be severe). AC:H because emergent behavior requires specific multi-agent interaction conditions to manifest.
- **Exploitability**: Low (4.5) — emergent behavior is theoretical and probabilistic; no known weaponized exploit patterns; requires understanding of the specific multi-agent interaction topology to trigger reliably; no public tooling.
- **Scalability**: Moderately scalable once the triggering conditions are understood; the feedback loop nature means a triggered cascade affects all downstream agents; difficult to detect because individual agent actions remain within nominal bounds.
- **Reachability**: Trusted Application Zone (2.5); all participating agents are internal components.

*Score source: fresh (AGP-01 not present in baseline risk-scores.md; scored in this run)*

---

### I-8: The Learning Loop consumes the full Audit Logger training signal stream, which includes user prompts, agent decisions, and tool call parameters. If the trained model memorizes sensitive training data, it can inadvertently reproduce PII or proprietary information in its responses (training data extraction attack).

**Component**: Long-Running Learning Loop
**Category**: Information Disclosure
**MAESTRO Layer**: Unclassified
**Composite Score**: 4.9 (Medium)

| Dimension | Score | Weight | Weighted |
|-----------|------:|-------:|---------:|
| CVSS Base | 5.9 | 0.35 | 2.07 |
| Exploitability | 5.0 | 0.30 | 1.50 |
| Scalability | 5.8 | 0.15 | 0.87 |
| Reachability | 2.5 | 0.20 | 0.50 |
| **Composite** | | | **4.9** |

**CVSS Vector**: `CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N`

**Scoring Rationale**:
- **CVSS**: High complexity reflecting the difficulty of systematic model memorization extraction (many queries required); high confidentiality impact from PII reproduction; no integrity or availability impact.
- **Exploitability**: Requires systematic probing to extract memorized training data; ML knowledge is helpful; academic attack class with growing practical research.
- **Scalability**: Memorization extraction can be automated via query patterns; differential privacy during training is the primary mitigating control.
- **Reachability**: Trusted Application Zone (2.5).

*Score source: inherited (baseline 2026-04-23T19-30-00)*

---

### R-7: The Learning Loop denies having applied a specific model update or claims that an update was applied with different training data than what is recorded. Without cryptographic provenance, model updates cannot be attributed to specific training runs or data sources.

**Component**: Long-Running Learning Loop
**Category**: Repudiation
**MAESTRO Layer**: Unclassified
**Composite Score**: 4.9 (Medium)

| Dimension | Score | Weight | Weighted |
|-----------|------:|-------:|---------:|
| CVSS Base | 6.5 | 0.35 | 2.28 |
| Exploitability | 4.5 | 0.30 | 1.35 |
| Scalability | 5.3 | 0.15 | 0.80 |
| Reachability | 2.5 | 0.20 | 0.50 |
| **Composite** | | | **4.9** |

**CVSS Vector**: `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N`

**Scoring Rationale**:
- **CVSS**: Model update repudiation with high integrity impact; without provenance, any model update can be plausibly denied or attributed to different training data.
- **Exploitability**: Requires insider or system-level access to Learning Loop operations; the threat is primarily an insider or operator misconduct risk.
- **Scalability**: Affects all model updates without provenance controls; systemic gap across the model update pipeline.
- **Reachability**: Trusted Application Zone (2.5).

*Score source: inherited (baseline 2026-04-23T19-30-00)*

---

### S-4: The Specialist Agent impersonates the Orchestrator when returning results to the Inter-Agent Communication Channel. A compromised Specialist Agent could inject fabricated "Aggregated Results" back to the Orchestrator, making unauthorized actions appear to have originated from valid specialist work.

**Component**: Specialist Agent
**Category**: Spoofing
**MAESTRO Layer**: Unclassified
**Composite Score**: 4.9 (Medium)

| Dimension | Score | Weight | Weighted |
|-----------|------:|-------:|---------:|
| CVSS Base | 5.7 | 0.35 | 2.00 |
| Exploitability | 5.3 | 0.30 | 1.59 |
| Scalability | 5.3 | 0.15 | 0.80 |
| Reachability | 2.5 | 0.20 | 0.50 |
| **Composite** | | | **4.9** |

**CVSS Vector**: `CVSS:3.1/AV:A/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N`

**Scoring Rationale**:
- **CVSS**: Adjacent-network result fabrication; high integrity impact from fabricated aggregated results reaching the Orchestrator as trusted specialist output.
- **Exploitability**: Requires Specialist Agent compromise; moderately complex prerequisite but straightforward once the agent is compromised.
- **Scalability**: Persistent result fabrication until the Orchestrator detects anomalies; limited to sessions where the Specialist is active.
- **Reachability**: Trusted Application Zone (2.5).

*Score source: inherited (baseline 2026-04-23T19-30-00)*

---

### I-3: The Specialist Agent receives sensitive data via delegated tasks (from the Orchestrator's context) and may include it verbatim in its results returned via the Inter-Agent Channel. If the Channel is observable or the results are logged without redaction, sensitive upstream data leaks downstream.

**Component**: Specialist Agent
**Category**: Information Disclosure
**MAESTRO Layer**: Unclassified
**Composite Score**: 4.8 (Medium)

| Dimension | Score | Weight | Weighted |
|-----------|------:|-------:|---------:|
| CVSS Base | 5.7 | 0.35 | 2.00 |
| Exploitability | 5.3 | 0.30 | 1.59 |
| Scalability | 5.0 | 0.15 | 0.75 |
| Reachability | 2.5 | 0.20 | 0.50 |
| **Composite** | | | **4.8** |

**CVSS Vector**: `CVSS:3.1/AV:A/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N`

**Scoring Rationale**:
- **CVSS**: Adjacent-network data leakage via verbatim result propagation; high confidentiality impact from sensitive upstream context reaching observable channels.
- **Exploitability**: Requires access to the Inter-Agent Channel or Audit Logger to observe leaked data; moderate barrier requiring Application Zone access.
- **Scalability**: Systematic data minimization gap affects all delegated tasks containing sensitive context.
- **Reachability**: Trusted Application Zone (2.5).

*Score source: inherited (baseline 2026-04-23T19-30-00)*

---

### R-2: The Guardrails Service can deny having logged a filtering event or claim that an input passed filtering when it was actually rejected (or vice versa). Without tamper-evident logs, the filtering pipeline's decisions cannot be verified independently.

**Component**: Guardrails Service
**Category**: Repudiation
**MAESTRO Layer**: L6 — Security and Compliance
**Composite Score**: 4.4 (Medium)

| Dimension | Score | Weight | Weighted |
|-----------|------:|-------:|---------:|
| CVSS Base | 4.3 | 0.35 | 1.51 |
| Exploitability | 5.3 | 0.30 | 1.59 |
| Scalability | 5.5 | 0.15 | 0.83 |
| Reachability | 2.5 | 0.20 | 0.50 |
| **Composite** | | | **4.4** |

**CVSS Vector**: `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N`

**Scoring Rationale**:
- **CVSS**: Repudiation default; low integrity impact from false event logging; primary risk is audit trail integrity rather than direct technical exploitation.
- **Exploitability**: Any Guardrails operator can exercise repudiation without tamper-evident logging controls.
- **Scalability**: Affects all filtering event records; systemic gap without Merkle-chain or hash-chain logging.
- **Reachability**: Trusted Application Zone (2.5).

*Score source: inherited (baseline 2026-04-23T19-30-00)*

---

### R-4: The Specialist Agent denies having executed a tool call or produced a specific result. Without signed, non-repudiable decision logs, the Specialist's actions cannot be attributed.

**Component**: Specialist Agent
**Category**: Repudiation
**MAESTRO Layer**: Unclassified
**Composite Score**: 4.4 (Medium)

| Dimension | Score | Weight | Weighted |
|-----------|------:|-------:|---------:|
| CVSS Base | 4.3 | 0.35 | 1.51 |
| Exploitability | 5.3 | 0.30 | 1.59 |
| Scalability | 5.3 | 0.15 | 0.80 |
| Reachability | 2.5 | 0.20 | 0.50 |
| **Composite** | | | **4.4** |

**CVSS Vector**: `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N`

**Scoring Rationale**:
- **CVSS**: Repudiation default; low integrity impact; primary risk is operational accountability and incident response capability.
- **Exploitability**: Any Specialist operator can exercise repudiation without signed log controls.
- **Scalability**: Affects all Specialist actions without cryptographic attribution.
- **Reachability**: Trusted Application Zone (2.5).

*Score source: inherited (baseline 2026-04-23T19-30-00)*

---

### R-6: The MCP Tool Server denies having executed a specific tool invocation or received a particular JSON-RPC request. Without signed execution logs, tool invocations cannot be attributed to the requesting agent.

**Component**: MCP Tool Server
**Category**: Repudiation
**MAESTRO Layer**: L3 — Agent Framework
**Composite Score**: 4.4 (Medium)

| Dimension | Score | Weight | Weighted |
|-----------|------:|-------:|---------:|
| CVSS Base | 4.3 | 0.35 | 1.51 |
| Exploitability | 5.3 | 0.30 | 1.59 |
| Scalability | 5.5 | 0.15 | 0.83 |
| Reachability | 2.5 | 0.20 | 0.50 |
| **Composite** | | | **4.4** |

**CVSS Vector**: `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N`

**Scoring Rationale**:
- **CVSS**: Repudiation default; low integrity impact; primary risk is tool invocation accountability and external API dispute resolution.
- **Exploitability**: Any Tool Server operator can exercise repudiation without signed log controls.
- **Scalability**: Affects all tool invocations without cryptographic attribution; systemic operational accountability gap.
- **Reachability**: Trusted Application Zone (2.5).

*Score source: inherited (baseline 2026-04-23T19-30-00)*

---

### R-5: The Channel denies having delivered or modified a specific message. Without delivery receipts and message integrity records, it is impossible to determine whether a message was delivered as sent or was modified in transit.

**Component**: Inter-Agent Communication Channel
**Category**: Repudiation
**MAESTRO Layer**: Unclassified
**Composite Score**: 4.3 (Medium)

| Dimension | Score | Weight | Weighted |
|-----------|------:|-------:|---------:|
| CVSS Base | 4.3 | 0.35 | 1.51 |
| Exploitability | 5.0 | 0.30 | 1.50 |
| Scalability | 5.3 | 0.15 | 0.80 |
| Reachability | 2.5 | 0.20 | 0.50 |
| **Composite** | | | **4.3** |

**CVSS Vector**: `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N`

**Scoring Rationale**:
- **CVSS**: Repudiation default; low integrity impact; primary risk is message delivery accountability and inter-agent coordination auditability.
- **Exploitability**: Channel-level repudiation is exercisable without delivery ACK controls.
- **Scalability**: Affects all inter-agent messages without cryptographic delivery receipts.
- **Reachability**: Trusted Application Zone (2.5).

*Score source: inherited (baseline 2026-04-23T19-30-00)*

---

## 4. Governance Fields

| ID | Component | Severity | Owner | SLA | Disposition | Review Date |
|----|-----------|----------|-------|-----|-------------|-------------|
| S-1 | User | High | Unassigned | 7d | Mitigate | 2026-05-02 |
| AG-1 | LLM Agent Orchestrator | High | Unassigned | 7d | Mitigate | 2026-05-02 |
| E-2 | LLM Agent Orchestrator | High | Unassigned | 7d | Mitigate | 2026-05-02 |
| R-3 | LLM Agent Orchestrator | High | Unassigned | 7d | Mitigate | 2026-05-02 |
| E-1 | Guardrails Service | High | Unassigned | 7d | Mitigate | 2026-05-02 |
| LLM-6 | LLM Agent Orchestrator | High | Unassigned | 7d | Mitigate | 2026-05-02 |
| OI-2 | LLM Agent Orchestrator | High | Unassigned | 7d | Mitigate | 2026-05-02 |
| LLM-5 | LLM Agent Orchestrator | High | Unassigned | 7d | Mitigate | 2026-05-02 |
| OI-1 | LLM Agent Orchestrator | High | Unassigned | 7d | Mitigate | 2026-05-02 |
| LLM-13 | Clinical Advisory Sub-Agent | High | Unassigned | 7d | Mitigate | 2026-05-02 |
| LLM-8 | Specialist Agent | High | Unassigned | 7d | Mitigate | 2026-05-02 |
| I-2 | LLM Agent Orchestrator | High | Unassigned | 7d | Mitigate | 2026-05-02 |
| LLM-1 | LLM Agent Orchestrator | High | Unassigned | 7d | Mitigate | 2026-05-02 |
| LLM-4 | LLM Agent Orchestrator | High | Unassigned | 7d | Mitigate | 2026-05-02 |
| T-2 | LLM Agent Orchestrator | High | Unassigned | 7d | Mitigate | 2026-05-02 |
| E-5 | MCP Tool Server | High | Unassigned | 7d | Mitigate | 2026-05-02 |
| T-5 | MCP Tool Server | High | Unassigned | 7d | Mitigate | 2026-05-02 |
| AG-5 | MCP Tool Server | Medium | Unassigned | 30d | Review | 2026-05-25 |
| E-7 | Clinical Advisory Sub-Agent | Medium | Unassigned | 30d | Review | 2026-05-25 |
| I-9 | Clinical Advisory Sub-Agent | Medium | Unassigned | 30d | Review | 2026-05-25 |
| LLM-2 | LLM Agent Orchestrator | Medium | Unassigned | 30d | Review | 2026-05-25 |
| D-1 | Guardrails Service | Medium | Unassigned | 30d | Review | 2026-05-25 |
| LLM-7 | LLM Agent Orchestrator | Medium | Unassigned | 30d | Review | 2026-05-25 |
| LLM-14 | Clinical Advisory Sub-Agent | Medium | Unassigned | 30d | Review | 2026-05-25 |
| MI-2 | Clinical Advisory Sub-Agent | Medium | Unassigned | 30d | Review | 2026-05-25 |
| T-9 | Clinical Advisory Sub-Agent | Medium | Unassigned | 30d | Review | 2026-05-25 |
| LLM-10 | Specialist Agent | Medium | Unassigned | 30d | Review | 2026-05-25 |
| MI-1 | Clinical Advisory Sub-Agent | Medium | Unassigned | 30d | Review | 2026-05-25 |
| MI-3 | Clinical Advisory Sub-Agent | Medium | Unassigned | 30d | Review | 2026-05-25 |
| OI-3 | LLM Agent Orchestrator | Medium | Unassigned | 30d | Review | 2026-05-25 |
| E-3 | Specialist Agent | Medium | Unassigned | 30d | Review | 2026-05-25 |
| E-4 | Inter-Agent Communication Channel | Medium | Unassigned | 30d | Review | 2026-05-25 |
| S-5 | Inter-Agent Communication Channel | Medium | Unassigned | 30d | Review | 2026-05-25 |
| S-7 | Long-Running Learning Loop | Medium | Unassigned | 30d | Review | 2026-05-25 |
| AG-3 | Specialist Agent | Medium | Unassigned | 30d | Review | 2026-05-25 |
| AG-6 | MCP Tool Server | Medium | Unassigned | 30d | Review | 2026-05-25 |
| D-2 | LLM Agent Orchestrator | Medium | Unassigned | 30d | Review | 2026-05-25 |
| D-5 | MCP Tool Server | Medium | Unassigned | 30d | Review | 2026-05-25 |
| OI-4 | Clinical Advisory Sub-Agent | Medium | Unassigned | 30d | Review | 2026-05-25 |
| R-1 | User | Medium | Unassigned | 30d | Review | 2026-05-25 |
| S-6 | MCP Tool Server | Medium | Unassigned | 30d | Review | 2026-05-25 |
| AG-2 | LLM Agent Orchestrator | Medium | Unassigned | 30d | Review | 2026-05-25 |
| AG-4 | Inter-Agent Communication Channel | Medium | Unassigned | 30d | Review | 2026-05-25 |
| E-6 | Long-Running Learning Loop | Medium | Unassigned | 30d | Review | 2026-05-25 |
| I-1 | Guardrails Service | Medium | Unassigned | 30d | Review | 2026-05-25 |
| S-3 | LLM Agent Orchestrator | Medium | Unassigned | 30d | Review | 2026-05-25 |
| T-3 | Specialist Agent | Medium | Unassigned | 30d | Review | 2026-05-25 |
| T-4 | Inter-Agent Communication Channel | Medium | Unassigned | 30d | Review | 2026-05-25 |
| S-8 | External API | Medium | Unassigned | 30d | Review | 2026-05-25 |
| S-9 | Clinical Advisory Sub-Agent | Medium | Unassigned | 30d | Review | 2026-05-25 |
| T-7 | Audit Logger | Medium | Unassigned | 30d | Review | 2026-05-25 |
| AG-7 | Long-Running Learning Loop | Medium | Unassigned | 30d | Review | 2026-05-25 |
| D-9 | Clinical Advisory Sub-Agent | Medium | Unassigned | 30d | Review | 2026-05-25 |
| LLM-9 | Specialist Agent | Medium | Unassigned | 30d | Review | 2026-05-25 |
| D-6 | Knowledge Base | Medium | Unassigned | 30d | Review | 2026-05-25 |
| LLM-11 | Long-Running Learning Loop | Medium | Unassigned | 30d | Review | 2026-05-25 |
| T-8 | Long-Running Learning Loop | Medium | Unassigned | 30d | Review | 2026-05-25 |
| D-3 | Specialist Agent | Medium | Unassigned | 30d | Review | 2026-05-25 |
| D-4 | Inter-Agent Communication Channel | Medium | Unassigned | 30d | Review | 2026-05-25 |
| D-7 | Audit Logger | Medium | Unassigned | 30d | Review | 2026-05-25 |
| AG-8 | Inter-Agent Communication Channel | Medium | Unassigned | 30d | Review | 2026-05-25 |
| I-6 | Knowledge Base | Medium | Unassigned | 30d | Review | 2026-05-25 |
| I-7 | Audit Logger | Medium | Unassigned | 30d | Review | 2026-05-25 |
| D-8 | Long-Running Learning Loop | Medium | Unassigned | 30d | Review | 2026-05-25 |
| I-5 | MCP Tool Server | Medium | Unassigned | 30d | Review | 2026-05-25 |
| LLM-3 | LLM Agent Orchestrator | Medium | Unassigned | 30d | Review | 2026-05-25 |
| LLM-12 | Long-Running Learning Loop | Medium | Unassigned | 30d | Review | 2026-05-25 |
| T-6 | Knowledge Base | Medium | Unassigned | 30d | Review | 2026-05-25 |
| R-9 | Clinical Advisory Sub-Agent | Medium | Unassigned | 30d | Review | 2026-05-25 |
| S-2 | Guardrails Service | Medium | Unassigned | 30d | Review | 2026-05-25 |
| I-4 | Inter-Agent Communication Channel | Medium | Unassigned | 30d | Review | 2026-05-25 |
| R-8 | External API | Medium | Unassigned | 30d | Review | 2026-05-25 |
| T-1 | Guardrails Service | Medium | Unassigned | 30d | Review | 2026-05-25 |
| AGP-01 | LLM Agent Orchestrator | Medium | Unassigned | 30d | Review | 2026-05-25 |
| I-8 | Long-Running Learning Loop | Medium | Unassigned | 30d | Review | 2026-05-25 |
| R-7 | Long-Running Learning Loop | Medium | Unassigned | 30d | Review | 2026-05-25 |
| S-4 | Specialist Agent | Medium | Unassigned | 30d | Review | 2026-05-25 |
| I-3 | Specialist Agent | Medium | Unassigned | 30d | Review | 2026-05-25 |
| R-2 | Guardrails Service | Medium | Unassigned | 30d | Review | 2026-05-25 |
| R-4 | Specialist Agent | Medium | Unassigned | 30d | Review | 2026-05-25 |
| R-6 | MCP Tool Server | Medium | Unassigned | 30d | Review | 2026-05-25 |
| R-5 | Inter-Agent Communication Channel | Medium | Unassigned | 30d | Review | 2026-05-25 |

---

## 5. Scoring Methodology

### Scoring Dimensions

| Dimension | Weight | Description |
|-----------|-------:|-------------|
| CVSS Base | 0.35 | CVSS 3.1 base score reflecting inherent vulnerability severity per standard metric assessment |
| Exploitability | 0.30 | Practical attack feasibility: Known Techniques + Attack Complexity + Tooling Availability + Skill Level (avg of 4 sub-dimensions) |
| Scalability | 0.15 | Blast radius and operational economics: Scriptability + Target Scope + Resource Requirements + Detection Difficulty (avg of 4 sub-dimensions) |
| Reachability | 0.20 | Architecture-aware exposure based on trust zone position: zone baseline + zone name keyword adjustments + architecture barrier adjustments |

### Composite Score Formula

```
Composite = (0.35 × CVSS Base) + (0.30 × Exploitability) + (0.15 × Scalability) + (0.20 × Reachability)
```

Composite scores are rounded to one decimal place. All dimension scores are on a 0.0–10.0 scale.

### Severity Band Mapping

| Severity Band | Score Range | SLA | Disposition |
|---------------|-------------|-----|-------------|
| Critical | 9.0 – 10.0 | 24h | Mitigate |
| High | 7.0 – 8.9 | 7d | Mitigate |
| Medium | 4.0 – 6.9 | 30d | Review |
| Low | 0.0 – 3.9 | 90d | Review |

Boundary values are inclusive to the higher band (7.0 = High, 9.0 = Critical).

### Data Sources

- **Input findings**: `examples/agentic-app/test-output/2026-04-26T03-39-12-F3-wave3/threats.md` (84 findings: 83 UNCHANGED + 1 NEW AG-8)
- **Trust zones**: Section 2 of threats.md — User Zone (Untrusted), Application Zone (Trusted), External Services (Semi-Trusted)
- **Architecture file**: `examples/agentic-app/test-output/2026-04-26T03-39-12-F3-wave3/architecture.md` (present; no explicit authentication barriers or network segmentation declarations found in architecture description — no architectural score adjustments applied)
- **Baseline**: `examples/agentic-app/test-output/2026-04-23T19-30-00-F2-wave4/risk-scores.md` (80 findings with inherited scores; AGP-01 absent from baseline risk-scores.md — scored fresh; AG-8 NEW finding inheriting from CG-7 primary D-4)
- **Category default vectors**: Per `schemas/risk-scoring.yaml` category_defaults (spoofing 8.2, tampering 7.1, repudiation 4.3, info-disclosure 6.5, denial-of-service 7.5, privilege-escalation 9.9, agentic 9.1, llm 9.3)

### Trust Zone Reachability Baselines

| Zone | Trust Level | Baseline | Keyword Adjustments | Final Reachability |
|------|-------------|----------|--------------------|--------------------|
| User Zone | Untrusted | 9.0 | "user" +0.5 → 9.5 | 9.5 |
| Application Zone | Trusted | 2.5 | None applicable | 2.5 |
| Application Zone (Knowledge Base) | Trusted | 2.5 | "data store" / "storage" -0.5 → 2.0 | 2.0 |
| External Services | Semi-Trusted | 5.5 | "external" +0.5 → 6.0 | 6.0 |

### Correlation Groups

| Group | Primary | Peers | Score Source |
|-------|---------|-------|--------------|
| CG-1 | T-2 (composite 7.1) | LLM-4 | Peers inherit primary scores |
| CG-2 | T-8 (composite 5.7) | LLM-11 | Peers inherit primary scores |
| CG-3 | E-2 (composite 7.8) | R-3, AG-1 | Peers inherit primary scores |
| CG-4 | I-2 (composite 7.2) | LLM-1 | Peers inherit primary scores |
| CG-5 | D-5 (composite 6.2) | AG-6 | Peers inherit primary scores |
| CG-6 | T-9 (composite 6.6) | LLM-14 | Peers inherit primary scores |
| CG-7 | D-4 (composite 5.5) | AG-8 | Peers inherit primary scores (AG-8 NEW but peer inherits from primary) |

### Score Source Summary

| Source | Count | Findings |
|--------|------:|---------|
| Inherited (baseline 2026-04-23T19-30-00) | 80 | All UNCHANGED findings present in baseline risk-scores.md |
| Inherited (correlation primary D-4) | 1 | AG-8 (NEW, CG-7 peer) |
| Fresh (this run) | 1 | AGP-01 (UNCHANGED but absent from baseline risk-scores.md) |
| **Total** | **82** | 84 findings scored (80 inherited + 1 correlation peer inherit + 1 fresh) |

*Note: 84 total findings = 82 score assignments (AG-8 and AGP-01 combine for 2 non-baseline-direct-inherits).*

### Reproducibility

Scores are computed at temperature 0 with ±0.5 tolerance per dimension. Inherited scores (baseline and correlation group peers) are byte-identical to their source. AGP-01 scores are freshly computed and carry ±0.5 per-dimension tolerance. All 83 UNCHANGED findings carry `score_source: inherited`; AG-8 (correlation peer) carries `score_source: inherited`; AGP-01 carries `score_source: fresh`.
