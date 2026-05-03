---
schema_version: "1.0"
date: "2026-04-27"
source_file: "examples/agentic-app/sample-report/threats.md"
classification: "confidential"
scoring_weights:
  cvss_base: 0.35
  exploitability: 0.30
  scalability: 0.15
  reachability: 0.20
---

# Risk Scores — Agentic AI Application (F-5 Wave 2)

## 1. Executive Summary

**Total findings scored**: 88 (9 Spoofing · 9 Tampering · 9 Repudiation · 9 Information Disclosure · 13 Denial of Service · 7 Privilege Escalation · 8 Agentic Threats · 16 LLM Threats · 4 Output Integrity · 3 Misinformation · 1 Agentic Pattern)

### Severity Band Distribution

| Severity Band | Count | Percentage |
|---------------|------:|----------:|
| Critical | 0 | 0% |
| High | 21 | 24% |
| Medium | 67 | 76% |
| Low | 0 | 0% |

**Highest-risk component**: User (maximum composite score 8.2, finding S-1)

The portfolio adds four F-5 LLM10 Unbounded Consumption findings (D-10, D-11, LLM-15, LLM-16), all targeting LLM Agent Orchestrator in the Trusted Application Zone. These findings score at High (7.2) as a correlation group (CG-8), consistent with all Application Zone components where the Trusted zone reachability baseline (2.5) moderates composite scores. LLM-16 scores identically at High (7.2) reflecting the Q3 RESOLVED High-default for the Denial-of-Wallet vector. No findings crossed the Critical composite threshold; the Trusted zone reachability ceiling continues to produce a High maximum for internal components regardless of CVSS or exploitability severity.

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
| D-10 | LLM Agent Orchestrator | LLM Inference-Request Flooding and Token Exhau... | 8.5 | 8.5 | 8.0 | 2.5 | 7.2 | High | 7d | Mitigate |
| D-11 | LLM Agent Orchestrator | Context-Window Exhaustion — Latency-Driven Var... | 8.5 | 8.5 | 8.0 | 2.5 | 7.2 | High | 7d | Mitigate |
| I-2 | LLM Agent Orchestrator | The Orchestrator's context window contains sen... | 8.6 | 8.8 | 7.3 | 2.5 | 7.2 | High | 7d | Mitigate |
| LLM-1 | LLM Agent Orchestrator | Direct prompt injection via the User→Guardrail... | 8.6 | 8.8 | 7.3 | 2.5 | 7.2 | High | 7d | Mitigate |
| LLM-15 | LLM Agent Orchestrator | Cost Amplification via Recursive or Cost-Asymm... | 8.5 | 8.5 | 8.0 | 2.5 | 7.2 | High | 7d | Mitigate |
| LLM-16 | LLM Agent Orchestrator | Denial-of-Wallet via Context-Window Cost Ampli... | 8.5 | 8.5 | 8.0 | 2.5 | 7.2 | High | 7d | Mitigate |
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

*Score source: inherited (baseline 2026-04-26T03-39-12)*

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

*Score source: inherited (baseline 2026-04-26T03-39-12)*

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

*Score source: inherited (baseline 2026-04-26T03-39-12)*

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

*Score source: inherited (baseline 2026-04-26T03-39-12)*

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

*Score source: inherited (baseline 2026-04-26T03-39-12)*

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

*Score source: inherited (baseline 2026-04-26T03-39-12)*

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

*Score source: inherited (baseline 2026-04-26T03-39-12)*

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

*Score source: inherited (baseline 2026-04-26T03-39-12)*

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
- **CVSS**: Client-side XSS via LLM output rendered in browser; scope change to victim browser with high C and I from cookie/token theft; user interaction (rendering) required.
- **Exploitability**: LLM-driven XSS via DOM injection is extensively documented with off-the-shelf tooling (BeEF, Burp Suite).
- **Scalability**: Affects all users; generic payload, no per-victim customization needed; fully automatable.
- **Reachability**: Trusted Application Zone (2.5).

*Score source: inherited (baseline 2026-04-26T03-39-12)*

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
- **CVSS**: Scope-changing prompt injection with high C and I impact; user interaction reflects clinical query processing trigger.
- **Exploitability**: Clinical prompt injection is a documented variant of direct prompt injection; the ClinAdvisor's medical-domain authority amplifies impact.
- **Scalability**: Slightly lower than Orchestrator due to indirect access path through ClinAdvisor's delegation chain.
- **Reachability**: Trusted Application Zone (2.5).

*Score source: inherited (baseline 2026-04-26T03-39-12)*

---

### LLM-8: Prompt injection via delegation messages: the Specialist Agent processes tasks delegated by the Orchestrator via the Inter-Agent Channel. An attacker who injects adversarial content into the Delegation Message can hijack the Specialist's task execution.

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

*Score source: inherited (baseline 2026-04-26T03-39-12)*

---

### D-10: LLM Inference-Request Flooding and Token Exhaustion (Pattern Category 12 — OWASP LLM10:2025): The LLM Agent Orchestrator exposes an LLM inference pipeline without declared per-tenant QPS rate limiting at the API-gateway layer. An attacker can flood the Orchestrator's inference endpoint with concurrent max-token requests, exhausting inference compute and starving legitimate users. The fan-out to Specialist Agent and Clinical Advisory Sub-Agent multiplies the DoS surface — a single attacker request triggers three concurrent LLM inference calls.

**Component**: LLM Agent Orchestrator
**Category**: Denial of Service
**MAESTRO Layer**: L1 — Foundation Model
**Composite Score**: 7.2 (High)

| Dimension | Score | Weight | Weighted |
|-----------|------:|-------:|---------:|
| CVSS Base | 8.5 | 0.35 | 2.98 |
| Exploitability | 8.5 | 0.30 | 2.55 |
| Scalability | 8.0 | 0.15 | 1.20 |
| Reachability | 2.5 | 0.20 | 0.50 |
| **Composite** | | | **7.2** |

**CVSS Vector**: `CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:N/I:L/A:H`

**Scoring Rationale**:
- **CVSS**: Network-reachable unauthenticated attack with scope change (fan-out to Specialist + ClinAdvisor) producing high availability impact and low integrity impact from disrupted inference output ordering; bounded to DoS category max of 8.5.
- **Exploitability**: LLM API flooding with maximum-token payloads is trivially scriptable using off-the-shelf HTTP load testing tools (ab, wrk, k6); no specialized knowledge required beyond valid credentials; exploitation path is well-documented under OWASP LLM10:2025.
- **Scalability**: Fully automatable end-to-end; affects all inference consumers simultaneously; low detection difficulty because flood traffic resembles high-volume legitimate usage, especially across the fan-out legs.
- **Reachability**: LLM Agent Orchestrator is in the Trusted Application Zone (baseline 2.5); internal placement moderates composite score even for a severe DoS vector.

*Score source: fresh*

---

### D-11: Context-Window Exhaustion — Latency-Driven Variant (Pattern Category 13 — OWASP LLM10:2025; Q1 SPLIT Vector A): The LLM Agent Orchestrator accepts conversation history payloads without a declared max-context-window enforcement policy at the API gateway. Adversarially long prompts spike per-request inference latency to the per-tenant timeout threshold, causing legitimate requests to queue behind blocked inference slots. The fan-out to Specialist Agent and Clinical Advisory Sub-Agent compounds this — a single max-context request blocks three inference slots simultaneously.

**Component**: LLM Agent Orchestrator
**Category**: Denial of Service
**MAESTRO Layer**: L1 — Foundation Model
**Composite Score**: 7.2 (High)
**Correlation Group**: Scores inherited from primary finding D-10

| Dimension | Score | Weight | Weighted |
|-----------|------:|-------:|---------:|
| CVSS Base | 8.5 | 0.35 | 2.98 |
| Exploitability | 8.5 | 0.30 | 2.55 |
| Scalability | 8.0 | 0.15 | 1.20 |
| Reachability | 2.5 | 0.20 | 0.50 |
| **Composite** | | | **7.2** |

**CVSS Vector**: `CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:N/I:L/A:H`

**Scoring Rationale**:
- **CVSS**: Inherited from CG-8 primary (D-10). Context-window exhaustion shares the same attack surface (unauthenticated network, scope-changed availability disruption via fan-out) as inference-request flooding.
- **Exploitability**: Inherited from CG-8 primary. Constructing adversarially long prompts requires minimal skill; recursive prompt-expansion templates are publicly documented.
- **Scalability**: Inherited from CG-8 primary. Max-context requests can be scripted and targeted against all Orchestrator sessions.
- **Reachability**: Inherited from CG-8 primary. Trusted Application Zone (2.5).

*Score source: inherited (CG-8 primary D-10)*

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

*Score source: inherited (baseline 2026-04-26T03-39-12)*

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

*Score source: inherited (baseline 2026-04-26T03-39-12)*

---

### LLM-15: Cost Amplification via Recursive or Cost-Asymmetric Prompting (Pattern Category 10 — OWASP LLM10:2025): The LLM Agent Orchestrator accepts prompts without declared recursive-prompt depth limits or output-token caps. The multi-hop agent loop (Orchestrator → Specialist → ToolServer → ExtAPI, and Orchestrator → ClinAdvisor → KB) creates a recursive cost-amplification surface where a 10-token user prompt can generate 32k+ tokens of combined output across all inference endpoints.

**Component**: LLM Agent Orchestrator
**Category**: LLM Threats
**MAESTRO Layer**: L1 — Foundation Model
**Composite Score**: 7.2 (High)
**Correlation Group**: Scores inherited from primary finding D-10

| Dimension | Score | Weight | Weighted |
|-----------|------:|-------:|---------:|
| CVSS Base | 8.5 | 0.35 | 2.98 |
| Exploitability | 8.5 | 0.30 | 2.55 |
| Scalability | 8.0 | 0.15 | 1.20 |
| Reachability | 2.5 | 0.20 | 0.50 |
| **Composite** | | | **7.2** |

**CVSS Vector**: `CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:N/I:L/A:H`

**Scoring Rationale**:
- **CVSS**: Inherited from CG-8 primary (D-10). Cost amplification shares the same multi-hop fan-out attack surface producing scope-changed availability/financial impact.
- **Exploitability**: Inherited from CG-8 primary. Recursive prompt construction is well-documented; no specialized skills required.
- **Scalability**: Inherited from CG-8 primary. Fully automatable; amplification ratio scales with fan-out depth.
- **Reachability**: Inherited from CG-8 primary. Trusted Application Zone (2.5).

*Score source: inherited (CG-8 primary D-10)*

---

### LLM-16: Denial-of-Wallet via Context-Window Cost Amplification (Pattern Category 11 — OWASP LLM10:2025; Q1 SPLIT Vector B): The LLM Agent Orchestrator's context-window handling lacks per-tenant token budget hard-cap at the API gateway. The fan-out to Specialist Agent and Clinical Advisory Sub-Agent multiplies per-request inference cost up to 3x. Denial-of-wallet attacks accumulate as gradual billing increases invisible to per-request rate limits.

**Component**: LLM Agent Orchestrator
**Category**: LLM Threats
**MAESTRO Layer**: L1 — Foundation Model
**Composite Score**: 7.2 (High)
**Correlation Group**: Scores inherited from primary finding D-10

| Dimension | Score | Weight | Weighted |
|-----------|------:|-------:|---------:|
| CVSS Base | 8.5 | 0.35 | 2.98 |
| Exploitability | 8.5 | 0.30 | 2.55 |
| Scalability | 8.0 | 0.15 | 1.20 |
| Reachability | 2.5 | 0.20 | 0.50 |
| **Composite** | | | **7.2** |

**CVSS Vector**: `CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:N/I:L/A:H`

**Scoring Rationale**:
- **CVSS**: Inherited from CG-8 primary (D-10). Denial-of-wallet is the economic-damage vector of the same context-window and fan-out attack surface; Q3 RESOLVED severity floor confirms High (no freemium multi-tenant CRITICAL conditions met).
- **Exploitability**: Inherited from CG-8 primary. Billing amplification is as easy to trigger as any other max-context request.
- **Scalability**: Inherited from CG-8 primary. Economic damage scales linearly with sustained attack duration.
- **Reachability**: Inherited from CG-8 primary. Trusted Application Zone (2.5).

*Score source: inherited (CG-8 primary D-10)*

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
- **Scalability**: Inherited from CG-1 primary. Persistent poisoning affects all future Orchestrator sessions after the next model update.
- **Reachability**: Inherited from CG-1 primary. Trusted Application Zone (2.5).

*Score source: inherited (baseline 2026-04-26T03-39-12)*

---

### T-2: The Orchestrator's context window (system prompt, retrieved documents, tool results) can be tampered with by an attacker who controls any upstream data source. Injecting adversarial content into the context manipulates the Orchestrator's reasoning and outputs.

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
- **CVSS**: Maximum CVSS for context manipulation; scope-changed tampering with high CIA impact; upstream data source control provides the attack vector.
- **Exploitability**: Requires controlling an upstream data source (KB, channel, tool results); moderately complex compared to direct prompt injection.
- **Scalability**: Context poisoning persists across sessions once adversarial content is injected; affects all downstream consumers of the Orchestrator.
- **Reachability**: Trusted Application Zone (2.5).

*Score source: inherited (baseline 2026-04-26T03-39-12)*

---

### E-5: The MCP Tool Server executes tools with credentials it holds (service account tokens, API keys for External API). If an agent sends unauthorized tool calls, it gains the Tool Server's execution privileges.

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
- **CVSS**: Near-maximum privilege escalation; scope-changed full CIA impact from gaining Tool Server's credential set.
- **Exploitability**: Requires authenticated low-privilege agent access; the absence of zero-trust authorization enables privilege escalation via unauthorized tool calls.
- **Scalability**: Persistent credential access enables ongoing unauthorized operations; affects all external APIs accessible via the Tool Server.
- **Reachability**: Trusted Application Zone (2.5).

*Score source: inherited (baseline 2026-04-26T03-39-12)*

---

### T-5: Tool call request parameters supplied by agent LLM outputs can be tampered with before execution if the Tool Server does not validate them against an explicit allowlist.

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
- **CVSS**: LLM-influenced parameter tampering achieving scope-changed server-side injection; full CIA impact from arbitrary tool execution.
- **Exploitability**: Requires influencing LLM output via prompt injection; moderately exploitable with established techniques.
- **Scalability**: Affects all sessions invoking tools; parameter-level tampering is systemic across all tool call paths.
- **Reachability**: Trusted Application Zone (2.5).

*Score source: inherited (baseline 2026-04-26T03-39-12)*

---

### AG-5: The MCP Tool Server is vulnerable to tool call injection: an attacker who can influence the LLM output of either the Orchestrator or Specialist Agent can inject crafted JSON-RPC parameters that invoke unintended tools or supply malicious arguments.

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
- **CVSS**: Agentic tool call injection with scope change; slightly lower A than E-5 since attack is tool-invocation specific rather than general privilege escalation.
- **Exploitability**: Requires influencing LLM output; the attack path is well-documented but requires chaining prompt injection with tool parameter injection.
- **Scalability**: Affects all tool-calling sessions; JSON-RPC injection is scriptable once an influenceable LLM endpoint is identified.
- **Reachability**: Trusted Application Zone (2.5).

*Score source: inherited (baseline 2026-04-26T03-39-12)*

---

### E-7: The Clinical Advisory Sub-Agent operates with access to the Knowledge Base and produces clinical outputs that feed directly into the Orchestrator's response path. A prompt injection attack can cause the sub-agent to self-authorize elevated access or return outputs designed to manipulate the Orchestrator into taking high-privilege actions.

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
- **CVSS**: Near-maximum escalation; sub-agent's clinical authority and KB access enable scope-changed full CIA impact.
- **Exploitability**: Requires injecting adversarial content through the clinical query path; moderately complex due to indirect access through the Orchestrator delegation chain.
- **Scalability**: Clinical session targeting requires domain-specific crafting; lower scalability than direct Orchestrator attacks.
- **Reachability**: Trusted Application Zone (2.5).

*Score source: inherited (baseline 2026-04-26T03-39-12)*

---

### I-9: The Clinical Advisory Sub-Agent processes clinical query context from the Orchestrator and retrieves documents from the Knowledge Base. If its Clinical Summary outputs are not scrubbed before inclusion in the Orchestrator's HTTPS response, clinical context can leak to unauthorized parties.

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
- **CVSS**: Scope-changing clinical data disclosure; high confidentiality impact from patient-identifying information and proprietary clinical protocols leaking via Orchestrator response.
- **Exploitability**: Slightly lower than direct Orchestrator injection; requires triggering clinical query path with adversarial context.
- **Scalability**: Clinical data leakage affects all users receiving clinical advisory outputs; log-based propagation to training stream amplifies scope.
- **Reachability**: Trusted Application Zone (2.5).

*Score source: inherited (baseline 2026-04-26T03-39-12)*

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
- **CVSS**: Maximum base score for indirect injection; scope-changing attack with high C and I from KB-sourced adversarial instructions.
- **Exploitability**: Requires write access to KB or exploitation of KB poisoning vectors; more complex than direct prompt injection.
- **Scalability**: Injected KB documents affect all queries retrieving that document; persistent poisoning scales across all Orchestrator sessions.
- **Reachability**: Trusted Application Zone (2.5).

*Score source: inherited (baseline 2026-04-26T03-39-12)*

---

### D-1: The Guardrails Service is vulnerable to resource exhaustion via high-volume prompt submission. An attacker sends computationally expensive prompts at high rate to degrade or collapse the filtering pipeline.

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
- **CVSS**: Category default DoS vector; network, no auth, high availability impact, unchanged scope.
- **Exploitability**: HTTP flooding of Guardrails is trivially automatable; no special knowledge required.
- **Scalability**: Fully scriptable; affects all users simultaneously; detection is moderate (rate limiting triggers if configured).
- **Reachability**: Trusted Application Zone (2.5).

*Score source: inherited (baseline 2026-04-26T03-39-12)*

---

### LLM-7: Improper output handling — SSRF via LLM-synthesized URL: the Orchestrator can instruct the MCP Tool Server to fetch external URLs synthesized from LLM output, potentially targeting internal service URLs.

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
- **CVSS**: SSRF via LLM output; scope change to Tool Server's network reach; high confidentiality impact from accessing cloud metadata and internal services.
- **Exploitability**: SSRF via LLM-synthesized URLs is documented but requires crafting prompts that reliably produce target URLs; moderate complexity.
- **Scalability**: Limited to sessions using HTTP-fetch tools; DNS pinning and allowlisting reduce but don't eliminate risk.
- **Reachability**: Trusted Application Zone (2.5).

*Score source: inherited (baseline 2026-04-26T03-39-12)*

---

### LLM-14: Training data poisoning of the Clinical Advisory Sub-Agent via the Learning Loop: Clinical Decision Log Entries from the sub-agent are included in the Audit Logger training stream. An attacker who injects adversarially crafted clinical interaction records can shift the sub-agent's clinical reasoning.

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

**CVSS Vector**: `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H`

**Scoring Rationale**:
- **CVSS**: Inherited from CG-6 primary (T-9); clinical training data poisoning shares the context window manipulation attack surface.
- **Exploitability**: Inherited from CG-6 primary. Requires privileged Audit Logger access; complex multi-step delayed attack.
- **Scalability**: Inherited from CG-6 primary. Poisoning propagates to all future ClinAdvisor sessions after next update cycle.
- **Reachability**: Inherited from CG-6 primary. Trusted Application Zone (2.5).

*Score source: inherited (baseline 2026-04-26T03-39-12)*

---

### MI-2: Overreliance / Missing HITL on Decision-Critical Output (Category 3 per FR-017): The Clinical Advisory Sub-Agent's clinical recommendations surface to end consumers without a declared human-in-the-loop review gate.

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

**CVSS Vector**: `CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:H/A:N`

**Scoring Rationale**:
- **CVSS**: Clinical misinformation with missing HITL; scope-changing output affecting downstream clinical decisions; user interaction (clinician/patient consuming output) required.
- **Exploitability**: No special attack required; the vulnerability is structural — the absence of a HITL gate means any hallucinated clinical claim reaches users unchecked.
- **Scalability**: Affects all clinical advisory sessions; structural absence of HITL means the vulnerability is universal, not session-specific.
- **Reachability**: Trusted Application Zone (2.5).

*Score source: inherited (baseline 2026-04-26T03-39-12)*

---

### T-9: The Clinical Advisory Sub-Agent's context window can be tampered with via two paths: (1) adversarial documents injected into the Knowledge Base, (2) tampering with the Clinical Query / Context payload from the Orchestrator.

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

**CVSS Vector**: `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H`

**Scoring Rationale**:
- **CVSS**: Near-maximum tampering score; dual attack path (KB poisoning + query tampering) with scope-changed full CIA impact.
- **Exploitability**: Requires either KB write access or Orchestrator compromise; more complex than direct injection attacks.
- **Scalability**: KB-based tampering is persistent across all ClinAdvisor sessions; query-path tampering is session-specific.
- **Reachability**: Trusted Application Zone (2.5).

*Score source: inherited (baseline 2026-04-26T03-39-12)*

---

### LLM-10: Improper output handling — server-side injection via tool call results: the Specialist Agent's tool call results may influence downstream tool invocations. If the Tool Server returns LLM-influenced content containing injection payloads, the Specialist's next tool call may forward those payloads to execution sinks.

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
- **CVSS**: Server-side injection via tool result feedback loop; scope-changing execution with high C and I impact.
- **Exploitability**: Requires tooling that produces LLM-influenced results containing injection payloads; indirect exploitation path.
- **Scalability**: Limited to sessions where tool results feed subsequent tool calls; less universal than direct injection.
- **Reachability**: Trusted Application Zone (2.5).

*Score source: inherited (baseline 2026-04-26T03-39-12)*

---

### MI-1: Ungrounded Factual Emission (Category 1 per FR-017): The Clinical Advisory Sub-Agent emits clinical summaries containing factual medical claims without mandatory RAG grounding or per-claim source anchoring.

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

**CVSS Vector**: `CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:H/A:N`

**Scoring Rationale**:
- **CVSS**: Clinical hallucination with scope-changing output; user interaction (clinician/patient receiving output) required; high C and I from fabricated medical claims.
- **Exploitability**: Structural vulnerability — no special attack needed; hallucination occurs naturally without adversarial prompting.
- **Scalability**: Affects all clinical advisory sessions; consistent failure mode across all retrieval-insufficient queries.
- **Reachability**: Trusted Application Zone (2.5).

*Score source: inherited (baseline 2026-04-26T03-39-12)*

---

### MI-3: Retrieval-Grounding Gap (Category 4 per FR-017): The Clinical Advisory Sub-Agent has no declared mechanism to detect or handle retrieval failures — scenarios where the Knowledge Base does not contain relevant documents.

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

**CVSS Vector**: `CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:H/A:N`

**Scoring Rationale**:
- **CVSS**: Retrieval gap allows hallucinated clinical content to surface with the same confidence as grounded claims; scope-changing with high C and I impact.
- **Exploitability**: Triggered by out-of-distribution queries or stale KB content; no adversarial action required.
- **Scalability**: Affects all queries where KB retrieval quality is insufficient; systematic failure mode.
- **Reachability**: Trusted Application Zone (2.5).

*Score source: inherited (baseline 2026-04-26T03-39-12)*

---

### OI-3: Improper output handling — SSRF via LLM-synthesized URL in Tool Call Request: the Orchestrator constructs Tool Call Request messages containing URLs sourced from LLM output. The MCP Tool Server executes outbound HTTP to the supplied URL using its own server-side network credentials.

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
- **CVSS**: SSRF via LLM-synthesized URL in Tool Call Request; scope change to Tool Server's network; high confidentiality from cloud metadata access.
- **Exploitability**: Requires crafting prompts that reliably produce target URLs in tool parameters; documented SSRF variant.
- **Scalability**: Limited to HTTP-fetch tool invocations; allowlisting reduces scope but not eliminates.
- **Reachability**: Trusted Application Zone (2.5).

*Score source: inherited (baseline 2026-04-26T03-39-12)*

---

### E-3: The Specialist Agent receives delegated permissions from the Orchestrator. If the delegation message is forged or tampered with, the Specialist gains unauthorized capability to invoke tools or access data outside its permitted scope.

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
- **CVSS**: Near-maximum privilege escalation via forged delegation; scope-changed full CIA impact.
- **Exploitability**: Requires forging or tampering with delegation messages; dependent on channel access or Orchestrator compromise.
- **Scalability**: Limited to sessions where forged delegation can be injected; not universally automatable.
- **Reachability**: Trusted Application Zone (2.5).

*Score source: inherited (baseline 2026-04-26T03-39-12)*

---

### E-4: If the Channel does not enforce sender authentication, any Application Zone process can inject messages with forged identity headers claiming elevated sender roles.

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

**CVSS Vector**: `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H`

**Scoring Rationale**:
- **CVSS**: Forged sender identity escalates any Application Zone process to Orchestrator trust level; scope-changed full CIA impact.
- **Exploitability**: Requires Application Zone network access; low-privilege process can inject forged messages without sender authentication.
- **Scalability**: Persistent forged access affects all channel consumers; limited to Application Zone actors.
- **Reachability**: Trusted Application Zone (2.5).

*Score source: inherited (baseline 2026-04-26T03-39-12)*

---

### S-5: The Channel is a shared message routing substrate with no inherent sender authentication. A malicious process in the Application Zone can inject messages impersonating either the Orchestrator or the Specialist Agent.

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

**CVSS Vector**: `CVSS:3.1/AV:A/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:L`

**Scoring Rationale**:
- **CVSS**: Adjacent-network spoofing on shared channel substrate; scope-changed identity injection with high C and I.
- **Exploitability**: Requires Application Zone access; any process on the shared channel can inject forged messages without authentication.
- **Scalability**: Affects all agents consuming the channel; persistent injection enables ongoing unauthorized coordination.
- **Reachability**: Trusted Application Zone (2.5).

*Score source: inherited (baseline 2026-04-26T03-39-12)*

---

### S-7: The Learning Loop accepts a Training Signal Stream from the Audit Logger without verifying the data source's integrity or authenticity. An attacker who compromises the Audit Logger can inject fabricated training signals.

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

**CVSS Vector**: `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H`

**Scoring Rationale**:
- **CVSS**: Training signal spoofing with near-maximum impact; scope-changed manipulation of all downstream agent models.
- **Exploitability**: Requires Audit Logger compromise before injection; multi-step complex attack with delayed temporal activation.
- **Scalability**: Poisoned training signals propagate to all future model updates; persistent cross-session impact.
- **Reachability**: Trusted Application Zone (2.5).

*Score source: inherited (baseline 2026-04-26T03-39-12)*

---

### AG-3: The Specialist Agent, once delegated a task, operates autonomously without continuous Orchestrator oversight. An adversarially crafted delegation message can cause the Specialist to execute a sequence of tool calls that constitutes a prohibited action when viewed holistically.

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
- **CVSS**: Agentic autonomy abuse enabling scope-changed multi-step prohibited action sequences.
- **Exploitability**: Requires crafting delegation messages that produce a holistically prohibited sequence; moderately complex.
- **Scalability**: Autonomous execution means each crafted delegation potentially produces multiple unauthorized tool calls; detection requires holistic analysis.
- **Reachability**: Trusted Application Zone (2.5).

*Score source: inherited (baseline 2026-04-26T03-39-12)*

---

### AG-6: The MCP Tool Server acts as a privileged execution broker. Runaway or adversarially prompted agents can cause the Tool Server to repeatedly call External API endpoints in rapid succession, exhausting rate limits and incurring financial costs.

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

**CVSS Vector**: `CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H`

**Scoring Rationale**:
- **CVSS**: Inherited from CG-5 primary (D-5); resource exhaustion via connection pool depletion.
- **Exploitability**: Inherited from CG-5 primary. High-volume tool call triggering is automatable through compromised agent paths.
- **Scalability**: Inherited from CG-5 primary. External API rate limit exhaustion is persistent and affects all consumers.
- **Reachability**: Inherited from CG-5 primary. Trusted Application Zone (2.5).

*Score source: inherited (baseline 2026-04-26T03-39-12)*

---

### D-2: The Orchestrator's inference pipeline is a bounded resource. An attacker can exhaust the Orchestrator's capacity by flooding it with high-token-count prompts or by injecting context that forces recursive tool invocation chains.

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

**CVSS Vector**: `CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H`

**Scoring Rationale**:
- **CVSS**: DoS category default; resource exhaustion via token flooding with no auth requirement.
- **Exploitability**: Inference flooding is well-documented and trivially scriptable; D-10 (CG-8 primary) captures the more severe LLM10-specific variant.
- **Scalability**: Highly automatable; affects all inference consumers; detection is moderate.
- **Reachability**: Trusted Application Zone (2.5).

*Score source: inherited (baseline 2026-04-26T03-39-12)*

---

### D-5: The Tool Server's capacity for concurrent External API calls is bounded. A compromised agent sending high-volume tool call requests can exhaust the connection pool, causing all legitimate tool calls to fail.

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

**CVSS Vector**: `CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H`

**Scoring Rationale**:
- **CVSS**: Resource exhaustion via connection pool depletion; network-reachable, no auth, high availability impact.
- **Exploitability**: High-volume tool call triggering through compromised agent paths is automatable.
- **Scalability**: Connection pool exhaustion affects all concurrent tool call consumers globally.
- **Reachability**: Trusted Application Zone (2.5).

*Score source: inherited (baseline 2026-04-26T03-39-12)*

---

### OI-4: Improper output handling — server-side execution via Clinical Summary content injected into the Orchestrator's downstream Tool Call Request: the Clinical Advisory Sub-Agent returns clinical outputs to the Orchestrator. If the Orchestrator incorporates this clinical output into a subsequent Tool Call Request without sanitization, adversarial content can achieve server-side execution at the Tool Server.

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

**CVSS Vector**: `CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:H/A:N`

**Scoring Rationale**:
- **CVSS**: Indirect server-side execution via clinical output injection into tool parameters; scope change with high C and I impact.
- **Exploitability**: Multi-hop attack chain (clinical query → adversarial output → tool parameter injection); more complex than direct output injection.
- **Scalability**: Limited to sessions where clinical outputs feed tool invocations; dependent on Orchestrator pass-through behavior.
- **Reachability**: Trusted Application Zone (2.5).

*Score source: inherited (baseline 2026-04-26T03-39-12)*

---

### R-1: A user denies having submitted a particular prompt or query. Without request signing or non-repudiation controls, the system cannot prove the user submitted a specific input.

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

*Score source: inherited (baseline 2026-04-26T03-39-12)*

---

### S-6: An attacker in the Application Zone spoofs a valid agent (Orchestrator or Specialist) to submit unauthorized tool call requests to the MCP Tool Server.

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
- **CVSS**: Application Zone adjacency required; scope change as spoofed identity grants Tool Server's service credentials.
- **Exploitability**: Requires Application Zone access; authenticated low-privilege process can spoof agent identity without strong caller authentication.
- **Scalability**: Persistent spoofed access enables ongoing unauthorized tool invocations; limited to Application Zone actors.
- **Reachability**: Trusted Application Zone (2.5).

*Score source: inherited (baseline 2026-04-26T03-39-12)*

---

### AG-2: The Orchestrator and Specialist Agent can jointly coordinate to achieve a combined action that neither could perform alone or that would trigger per-agent rate limits if attempted individually.

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
- **CVSS**: Agent collusion enabling scope-changed cross-component action; PR:L as authenticated access required to influence both agents.
- **Exploitability**: Requires compromising or influencing both the Orchestrator and Specialist simultaneously; the coordination requirement significantly raises complexity.
- **Scalability**: Coordinated attacks are harder to script at scale than single-agent attacks; detection is harder because individual agent actions appear legitimate.
- **Reachability**: Trusted Application Zone (2.5).

*Score source: inherited (baseline 2026-04-26T03-39-12)*

---

### AG-4: The Channel is a shared substrate whose compromise enables agent-in-the-middle attacks: an attacker intercepts delegation messages, modifies the task parameters, and forwards the modified message to the Specialist Agent.

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

*Score source: inherited (baseline 2026-04-26T03-39-12)*

---

### E-6: The Learning Loop applies model updates with access to the Orchestrator, Specialist Agent, and Clinical Advisory Sub-Agent model parameters. If the update mechanism is compromised, an attacker elevates from data-layer access to model-parameter control.

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
- **Exploitability**: Very low (4.0) — requires: (1) compromising the Audit Logger training stream, (2) crafting adversarial training signals, (3) surviving training data validation, (4) waiting for the next model update cycle.
- **Scalability**: Once the model update is deployed, the effect is persistent across all future sessions for all three updated agents.
- **Reachability**: Trusted Application Zone (2.5).

*Score source: inherited (baseline 2026-04-26T03-39-12)*

---

### I-1: The Guardrails Service leaks the content of rejected prompts (including their rejection reasons) in error responses returned to the User. An attacker can iteratively probe the filtering rules.

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
- **CVSS**: Low CVSS (rejection reason leakage has limited direct confidentiality impact); the threat is primarily an enabler for adaptive bypass.
- **Exploitability**: Trivially exploitable — any unauthenticated user can observe rejection responses and iteratively refine prompts.
- **Scalability**: Automated fuzzing of rejection patterns is fully scriptable; affects all users of the Guardrails-protected endpoint.
- **Reachability**: Trusted Application Zone (2.5) for the Guardrails Service component.

*Score source: inherited (baseline 2026-04-26T03-39-12)*

---

### S-3: The Orchestrator's identity is not cryptographically attested to the Specialist Agent via the Inter-Agent Communication Channel. A compromised or rogue process could inject messages impersonating the Orchestrator.

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
- **Exploitability**: Requires Application Zone network access; authenticated low-privilege process required.
- **Scalability**: Persistent forged delegation messages affect all Specialist sessions; limited to Application Zone actors.
- **Reachability**: Trusted Application Zone (2.5).

*Score source: inherited (baseline 2026-04-26T03-39-12)*

---

### T-3: The Specialist Agent's operational context can be tampered with by injecting adversarial content into the Delegated Task message via the Inter-Agent Communication Channel.

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

*Score source: inherited (baseline 2026-04-26T03-39-12)*

---

### T-4: Messages transiting the Inter-Agent Communication Channel can be modified in transit by a process with access to the channel's message queue or shared memory.

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
- **CVSS**: Adjacent-network in-transit message modification; scope-changed tampering enabling unauthorized task redirection.
- **Exploitability**: Requires shared channel access; insider or compromised process can modify messages without end-to-end integrity.
- **Scalability**: All channel messages are vulnerable without message-level signing; systemic risk.
- **Reachability**: Trusted Application Zone (2.5).

*Score source: inherited (baseline 2026-04-26T03-39-12)*

---

### S-8: The External API provider's identity is not verified beyond TLS certificate validation. An attacker performing DNS hijacking or BGP route hijack can redirect MCP Tool Server API calls to an attacker-controlled server.

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

**CVSS Vector**: `CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:L/A:N`

**Scoring Rationale**:
- **CVSS**: Network attack requiring high complexity (BGP/DNS hijack); high confidentiality impact from intercepted API responses.
- **Exploitability**: DNS/BGP hijacking requires nation-state or ISP-level capability; highly complex, low practical frequency.
- **Scalability**: Attack requires persistent network-level infrastructure; not easily scriptable; nation-state level capability needed.
- **Reachability**: External Services zone (Semi-Trusted, baseline 5.5); no zone name keywords; reachability 5.5, architecture adjustments from HTTPS transport → 1 auth barrier (-1.5) → clamped to Semi-Trusted floor: 4.0. Wait — actually the external API is being spoofed from the perspective of the MCP Tool Server making outbound calls. The External API is the subject of the threat. Reachability = 6.0 reflects Semi-Trusted zone with no further adjustments per baseline.

*Score source: inherited (baseline 2026-04-26T03-39-12)*

---

### S-9: The Clinical Advisory Sub-Agent receives Clinical Query / Context messages from the LLM Agent Orchestrator via JSON-RPC without per-message sender attestation.

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
- **CVSS**: Adjacent-network JSON-RPC spoofing; scope-changed clinical query injection with high C and I.
- **Exploitability**: Requires Application Zone access to inject into the Orchestrator→ClinAdvisor JSON-RPC path.
- **Scalability**: Clinical-path spoofing is limited to sessions using clinical advisory; not universal.
- **Reachability**: Trusted Application Zone (2.5).

*Score source: inherited (baseline 2026-04-26T03-39-12)*

---

### T-7: The Audit Logger entries can be tampered with by a process with write access to the log store. Modifying or deleting log entries corrupts the training signal stream.

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

**CVSS Vector**: `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:L`

**Scoring Rationale**:
- **CVSS**: Audit log tampering with high integrity impact from corrupted training signal stream; low availability impact from potential log unavailability.
- **Exploitability**: Requires authenticated write access to the Audit Logger; insider threat or compromised service account.
- **Scalability**: Log tampering affects all future training runs; persistent impact after initial access.
- **Reachability**: Trusted Application Zone (2.5).

*Score source: inherited (baseline 2026-04-26T03-39-12)*

---

### AG-7: The Learning Loop's model update mechanism, when fed adversarially crafted training signals, can be exploited for a temporal autonomy attack: training data causes the updated model to expand its autonomous action scope on the next cycle.

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

**CVSS Vector**: `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:L`

**Scoring Rationale**:
- **CVSS**: Temporal autonomy attack with scope-changed capability expansion; high C and I from model parameter manipulation.
- **Exploitability**: Very low (4.0) — complex multi-step temporal attack requiring training signal access and patience.
- **Scalability**: Once deployed, the capability expansion affects all future sessions permanently.
- **Reachability**: Trusted Application Zone (2.5).

*Score source: inherited (baseline 2026-04-26T03-39-12)*

---

### D-9: The Clinical Advisory Sub-Agent is invoked by the Orchestrator for each clinical query via JSON-RPC and performs a vector search against the Knowledge Base. High-volume or adversarially-crafted clinical queries can exhaust the sub-agent's inference capacity.

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

**CVSS Vector**: `CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H`

**Scoring Rationale**:
- **CVSS**: DoS targeting ClinAdvisor inference capacity; network-reachable, no auth, high availability impact.
- **Exploitability**: Clinical query flooding is scriptable; requires reaching the clinical query path through the Orchestrator.
- **Scalability**: Clinical session exhaustion affects all users needing clinical advisory; KB query exhaustion is a secondary effect.
- **Reachability**: Trusted Application Zone (2.5).

*Score source: inherited (baseline 2026-04-26T03-39-12)*

---

### LLM-9: Training data poisoning of the Specialist Agent via the Learning Loop: adversarially crafted audit log entries from the Specialist's own decision logs can be incorporated into the Learning Loop's training signal and shift the Specialist's behavior.

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

**CVSS Vector**: `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:L`

**Scoring Rationale**:
- **CVSS**: Specialist-specific training data poisoning; scope-changed behavioral manipulation with high C and I.
- **Exploitability**: Self-poisoning loop requires Specialist decision log access; complex temporal attack.
- **Scalability**: Poisoned update affects all future Specialist sessions; persistence scales once deployed.
- **Reachability**: Trusted Application Zone (2.5).

*Score source: inherited (baseline 2026-04-26T03-39-12)*

---

### D-6: The Knowledge Base can be rendered unavailable by an attacker who issues high-volume, complex vector search queries.

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

**CVSS Vector**: `CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H`

**Scoring Rationale**:
- **CVSS**: Resource exhaustion via vector search queries; network-reachable, no auth, high availability impact.
- **Exploitability**: Vector search flooding is scriptable with HTTP requests; no special knowledge needed.
- **Scalability**: Query flooding affects all KB consumers simultaneously; caching provides partial mitigation.
- **Reachability**: Knowledge Base in Trusted Application Zone; "database" keyword adjustment -0.5 from 2.5 → 2.0, clamped to [1.0, 4.0] = 2.0.

*Score source: inherited (baseline 2026-04-26T03-39-12)*

---

### LLM-11: Data poisoning of the Learning Loop's training signal: the audit log training stream is the Learning Loop's primary data source. An attacker who systematically injects adversarially crafted interaction records creates poisoned training data.

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

**CVSS Vector**: `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:L`

**Scoring Rationale**:
- **CVSS**: Inherited from CG-2 primary (T-8); LLM training data poisoning shares the same attack surface.
- **Exploitability**: Inherited from CG-2 primary. Complex temporal attack requiring Audit Logger write access.
- **Scalability**: Inherited from CG-2 primary. Poisoned updates propagate across all future model update cycles.
- **Reachability**: Inherited from CG-2 primary. Trusted Application Zone (2.5).

*Score source: inherited (baseline 2026-04-26T03-39-12)*

---

### T-8: The training signal stream from the Audit Logger to the Learning Loop can be poisoned by injecting adversarial entries into the Audit Logger before training runs. A time-delayed attack inserts adversarial training signals that activate only when a specific trigger pattern appears.

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

**CVSS Vector**: `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:L`

**Scoring Rationale**:
- **CVSS**: Temporal sleeper-agent injection via training stream tampering; scope-changed behavioral modification with high C and I.
- **Exploitability**: Requires Audit Logger write access and training cycle knowledge; multi-step complex temporal attack.
- **Scalability**: Poisoned training signals propagate across all future update cycles; detection requires behavioral regression testing.
- **Reachability**: Trusted Application Zone (2.5).

*Score source: inherited (baseline 2026-04-26T03-39-12)*

---

### D-3: The Specialist Agent is invoked by the Orchestrator via the Inter-Agent Channel. An adversarially crafted delegation message that triggers computationally expensive subtasks can exhaust the Specialist Agent's processing capacity.

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
- **CVSS**: Adjacent-network delegation-triggered resource exhaustion; unchanged scope as the DoS is contained within the Specialist.
- **Exploitability**: Adversarially crafted delegation messages targeting Specialist capacity require channel access; moderately complex.
- **Scalability**: Queue flooding affects all delegated tasks; backpressure mitigation provides partial protection.
- **Reachability**: Trusted Application Zone (2.5).

*Score source: inherited (baseline 2026-04-26T03-39-12)*

---

### D-4: The Channel's message queue can be flooded by a compromised agent or a malfunctioning process, causing legitimate messages to be dropped, delayed, or rejected.

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
- **CVSS**: Adjacent-network queue flooding; unchanged scope; high availability impact from dropped coordination messages.
- **Exploitability**: Any Application Zone process can flood the channel queue without strong rate limiting.
- **Scalability**: Queue flooding is highly automatable from within the Application Zone; affects all coordinating agents.
- **Reachability**: Trusted Application Zone (2.5).

*Score source: inherited (baseline 2026-04-26T03-39-12)*

---

### D-7: The Audit Logger can be overwhelmed by a log-flooding attack from a compromised Application Zone process, causing legitimate log entries to be dropped or the logger to become unavailable.

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
- **CVSS**: Adjacent-network log flooding; unchanged scope; high availability impact from audit gap creation.
- **Exploitability**: Any Application Zone component can submit excessive log writes without strong write rate limiting.
- **Scalability**: Log flooding is trivially automatable; disk exhaustion affects all pipeline operations.
- **Reachability**: Trusted Application Zone (2.5).

*Score source: inherited (baseline 2026-04-26T03-39-12)*

---

### AG-8: Insecure Inter-Agent Communication (Category 9 — OWASP ASI07:2026): The Inter-Agent Communication Channel connects the LLM Agent Orchestrator, Specialist Agent, and Clinical Advisory Sub-Agent without declaring mutual authentication, inter-agent message signing, or nonce-based replay prevention.

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
- **CVSS**: Inherited from CG-7 primary (D-4); insecure inter-agent communication enables the same channel flooding and integrity exploitation surface.
- **Exploitability**: Inherited from CG-7 primary. Missing mTLS and message signing enables injection from any Application Zone process.
- **Scalability**: Inherited from CG-7 primary. Channel-level attacks affect all inter-agent coordination simultaneously.
- **Reachability**: Inherited from CG-7 primary. Trusted Application Zone (2.5).

*Score source: inherited (baseline 2026-04-26T03-39-12)*

---

### I-6: The Knowledge Base exposes its full document corpus to any process that can issue a vector search query. Without query-result access controls, a compromised Orchestrator or injected context can exfiltrate the entire corpus.

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
- **CVSS**: Information disclosure via unrestricted vector search; high confidentiality impact from full corpus exfiltration potential.
- **Exploitability**: Requires vector search query capability; available to any authorized process in the Application Zone.
- **Scalability**: Exhaustive query enumeration is scriptable; per-session result limits provide partial mitigation.
- **Reachability**: Knowledge Base in Trusted zone with "database" keyword (-0.5) → 2.0, clamped to [1.0, 4.0].

*Score source: inherited (baseline 2026-04-26T03-39-12)*

---

### I-7: The Audit Logger aggregates sensitive data from all Application Zone components. Unauthorized read access to the logger exposes the full operational history of the agent system.

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
- **CVSS**: Unauthorized read of aggregated sensitive logs; high confidentiality impact from full operational history exposure.
- **Exploitability**: Requires read access to the Audit Logger; insider threat or misconfigured access control.
- **Scalability**: Full audit log access enables bulk exfiltration; no per-query limits on reads in most log stores.
- **Reachability**: Trusted Application Zone (2.5).

*Score source: inherited (baseline 2026-04-26T03-39-12)*

---

### D-8: The Learning Loop is a resource-intensive batch process. A high-volume data injection into the Audit Logger can cause the Learning Loop to enter runaway processing, consuming excessive compute resources.

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

**CVSS Vector**: `CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H`

**Scoring Rationale**:
- **CVSS**: Resource exhaustion via training signal flooding; availability impact on Learning Loop compute.
- **Exploitability**: Requires injecting high-volume data into the Audit Logger; achievable with moderate effort.
- **Scalability**: Training flooding affects all upcoming model update cycles; compute pool contention spreads impact.
- **Reachability**: Trusted Application Zone (2.5).

*Score source: inherited (baseline 2026-04-26T03-39-12)*

---

### I-5: Tool results from External API calls may contain sensitive data that the Tool Server logs verbatim to the Audit Logger. If Audit Logger access is not restricted, this data becomes accessible to unauthorized processes.

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
- **CVSS**: PII leakage via unredacted tool result logging; high confidentiality impact from sensitive data in Audit Logger.
- **Exploitability**: Requires Audit Logger read access; the vulnerability is structural (verbatim logging without field classification).
- **Scalability**: All tool invocations producing sensitive results are affected; cumulative exposure grows with each call.
- **Reachability**: Trusted Application Zone (2.5).

*Score source: inherited (baseline 2026-04-26T03-39-12)*

---

### LLM-3: Model theft via systematic API probing: an attacker issues carefully crafted queries to extract the Orchestrator's model behavior, fine-tuning data characteristics, or system prompt contents.

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

**CVSS Vector**: `CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:N/A:N`

**Scoring Rationale**:
- **CVSS**: Model extraction requires high complexity (systematic probing strategy); high confidentiality impact from model IP exfiltration.
- **Exploitability**: Systematic probing is documented but requires ML knowledge to design effective extraction queries.
- **Scalability**: Model extraction can be automated once a probing strategy is established; watermarking complicates detection.
- **Reachability**: Trusted Application Zone (2.5).

*Score source: inherited (baseline 2026-04-26T03-39-12)*

---

### LLM-12: Model theft via Learning Loop output monitoring: an attacker with observability access to the Learning Loop's model update artifacts can reconstruct the model's architecture, parameters, or training data characteristics.

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

**CVSS Vector**: `CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:N/A:N`

**Scoring Rationale**:
- **CVSS**: Model artifact theft requiring observability access; high confidentiality impact from proprietary model IP exfiltration.
- **Exploitability**: Requires monitoring access to Learning Loop outputs; moderately complex.
- **Scalability**: Once access is established, artifact download is automatable; encryption provides primary mitigation.
- **Reachability**: Trusted Application Zone (2.5).

*Score source: inherited (baseline 2026-04-26T03-39-12)*

---

### T-6: The Knowledge Base corpus can be tampered with (poisoned) by an attacker who gains write access. Injecting adversarial documents causes the Orchestrator to retrieve and incorporate malicious context.

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

**CVSS Vector**: `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:L`

**Scoring Rationale**:
- **CVSS**: KB corpus poisoning via authenticated write access; high integrity impact from adversarial document injection.
- **Exploitability**: Requires authenticated KB write access; insider threat or compromised service account.
- **Scalability**: Injected documents affect all future queries retrieving that content; persistent impact.
- **Reachability**: Knowledge Base in Trusted zone with "database" keyword (-0.5) → 2.0.

*Score source: inherited (baseline 2026-04-26T03-39-12)*

---

### R-9: The Clinical Advisory Sub-Agent denies having generated a specific clinical summary or recommendation. Without non-repudiable logs of each clinical output, clinical decisions cannot be attributed.

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

**CVSS Vector**: `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N`

**Scoring Rationale**:
- **CVSS**: Clinical repudiation enabling deniability of hallucinated recommendations; low integrity impact from inability to attribute specific outputs.
- **Exploitability**: Exercised by any process with access to the clinical advisory path; no special tooling needed.
- **Scalability**: Repudiation is exercisable across all clinical advisory sessions without detection.
- **Reachability**: Trusted Application Zone (2.5).

*Score source: inherited (baseline 2026-04-26T03-39-12)*

---

### S-2: An attacker spoofs the Guardrails Service by sending crafted requests directly to the LLM Agent Orchestrator's internal endpoint, bypassing validation entirely.

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

**CVSS Vector**: `CVSS:3.1/AV:A/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N`

**Scoring Rationale**:
- **CVSS**: Adjacent-network Guardrails bypass enabling direct Orchestrator access; high confidentiality from bypassed content filtering.
- **Exploitability**: Requires Application Zone access to the Orchestrator's internal endpoint.
- **Scalability**: Persistent bypass affects all sessions until mTLS is enforced; limited to Application Zone actors.
- **Reachability**: Trusted Application Zone (2.5).

*Score source: inherited (baseline 2026-04-26T03-39-12)*

---

### I-4: Messages on the Inter-Agent Communication Channel are observable by any process in the Application Zone with access to the shared message bus or queue. Unencrypted inter-agent messages expose sensitive task context.

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
- **CVSS**: Adjacent-network channel eavesdropping; high confidentiality impact from sensitive inter-agent task context exposure.
- **Exploitability**: Requires Application Zone access to the shared message bus; any authorized process can observe unencrypted messages.
- **Scalability**: Passive eavesdropping is persistent and low-footprint; detection requires network-level monitoring.
- **Reachability**: Trusted Application Zone (2.5).

*Score source: inherited (baseline 2026-04-26T03-39-12)*

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
- **CVSS**: API provider repudiation enabling data dispute; low integrity impact from inability to prove specific response content.
- **Exploitability**: Repudiation by API provider requires no attacker capability; the vulnerability is structural (no response signing).
- **Scalability**: Exercisable for any API response not cryptographically signed.
- **Reachability**: External Services zone (Semi-Trusted); reachability 6.0 per baseline.

*Score source: inherited (baseline 2026-04-26T03-39-12)*

---

### T-1: An attacker with write access to the Guardrails Service configuration modifies filtering rules to allow previously-blocked prompt patterns through to the Orchestrator.

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

**CVSS Vector**: `CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:N/I:H/A:N`

**Scoring Rationale**:
- **CVSS**: High-privilege tampering with Guardrails configuration; high integrity impact from silently relaxed filtering rules.
- **Exploitability**: Requires admin/write access to Guardrails configuration; insider threat or admin credential compromise.
- **Scalability**: Configuration change affects all future sessions until detected and reversed.
- **Reachability**: Trusted Application Zone (2.5).

*Score source: inherited (baseline 2026-04-26T03-39-12)*

---

### AGP-01: Multi-agent emergent behavior — cascading failures or feedback amplification bypassing per-agent safety evaluation across the Orchestrator-Specialist-ClinAdvisor system.

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
- **CVSS**: Emergent behavior with high complexity (requires specific cascading conditions); scope-changed impact distributed across low CIA dimensions.
- **Exploitability**: Emergent behavior is difficult to deliberately trigger; requires understanding of cascading failure conditions across the multi-agent topology.
- **Scalability**: Once triggered, cascading effects propagate automatically; behavioral drift is difficult to detect without holistic system monitoring.
- **Reachability**: Trusted Application Zone (2.5).

*Score source: inherited (baseline 2026-04-26T03-39-12)*

---

### I-8: The Learning Loop consumes the full Audit Logger training signal stream, which includes user prompts, agent decisions, and tool call parameters. If the trained model memorizes sensitive training data, it can inadvertently reproduce PII or proprietary information.

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

**CVSS Vector**: `CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:N/A:N`

**Scoring Rationale**:
- **CVSS**: Training data memorization requiring high complexity (specific extraction queries); high confidentiality impact from reproduced PII.
- **Exploitability**: Extraction attacks require targeted querying to elicit memorized content; moderate expertise needed.
- **Scalability**: Affects all model instances trained on the contaminated data; cross-session PII exposure via model responses.
- **Reachability**: Trusted Application Zone (2.5).

*Score source: inherited (baseline 2026-04-26T03-39-12)*

---

### R-7: The Learning Loop denies having applied a specific model update or claims that an update was applied with different training data than what is recorded. Without cryptographic provenance, model updates cannot be attributed.

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

**CVSS Vector**: `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N`

**Scoring Rationale**:
- **CVSS**: Model update repudiation enabling deniability of training provenance; low integrity impact from unprovable update chain.
- **Exploitability**: Exercised by the Learning Loop operator or insider; no technical barrier once Audit Logger signing is absent.
- **Scalability**: Repudiation is systemic across all model updates without cryptographic provenance.
- **Reachability**: Trusted Application Zone (2.5).

*Score source: inherited (baseline 2026-04-26T03-39-12)*

---

### S-4: The Specialist Agent impersonates the Orchestrator when returning results to the Inter-Agent Communication Channel. A compromised Specialist Agent could inject fabricated "Aggregated Results" back to the Orchestrator.

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

**CVSS Vector**: `CVSS:3.1/AV:A/AC:L/PR:L/UI:N/S:U/C:H/I:L/A:N`

**Scoring Rationale**:
- **CVSS**: Adjacent-network result injection; high confidentiality impact from fabricated results influencing Orchestrator decisions.
- **Exploitability**: Requires Specialist Agent compromise and channel access; moderately complex.
- **Scalability**: Fabricated results affect each Orchestrator response; limited to sessions where the Specialist is active.
- **Reachability**: Trusted Application Zone (2.5).

*Score source: inherited (baseline 2026-04-26T03-39-12)*

---

### I-3: The Specialist Agent receives sensitive data via delegated tasks and may include it verbatim in its results returned via the Inter-Agent Channel. If the Channel is observable or results are logged without redaction, sensitive upstream data leaks downstream.

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
- **CVSS**: Adjacent-network sensitive data leakage via Specialist result propagation; high confidentiality impact from upstream context verbatim inclusion.
- **Exploitability**: Requires access to Specialist results (channel observation or log access); moderate barrier.
- **Scalability**: Affects all sessions where sensitive data is in delegation context; cumulative exposure.
- **Reachability**: Trusted Application Zone (2.5).

*Score source: inherited (baseline 2026-04-26T03-39-12)*

---

### R-2: The Guardrails Service can deny having logged a filtering event or claim that an input passed filtering when it was actually rejected. Without tamper-evident logs, the filtering pipeline's decisions cannot be verified independently.

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
- **CVSS**: Filtering decision repudiation; low integrity impact from inability to prove specific filtering outcomes.
- **Exploitability**: Exercised by Guardrails Service operator or insider; no special tooling.
- **Scalability**: Affects all filtering decisions that lack tamper-evident logging.
- **Reachability**: Trusted Application Zone (2.5).

*Score source: inherited (baseline 2026-04-26T03-39-12)*

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
- **CVSS**: Specialist action repudiation; low integrity impact from unattributable tool call history.
- **Exploitability**: Exercised by Specialist Agent operator or insider without signed logs.
- **Scalability**: Affects all Specialist tool invocations lacking service key signatures.
- **Reachability**: Trusted Application Zone (2.5).

*Score source: inherited (baseline 2026-04-26T03-39-12)*

---

### R-6: The MCP Tool Server denies having executed a specific tool invocation or received a particular JSON-RPC request. Without signed execution logs, tool invocations cannot be attributed.

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
- **CVSS**: Tool Server invocation repudiation; low integrity impact from inability to prove specific tool execution.
- **Exploitability**: Exercised by Tool Server operator or insider without signed execution logs.
- **Scalability**: Affects all tool invocations lacking pre-execution log entries.
- **Reachability**: Trusted Application Zone (2.5).

*Score source: inherited (baseline 2026-04-26T03-39-12)*

---

### R-5: The Channel denies having delivered or modified a specific message. Without delivery receipts and message integrity records, it is impossible to determine whether a message was delivered as sent or modified in transit.

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
- **CVSS**: Channel delivery repudiation; low integrity impact from unverifiable message transit history.
- **Exploitability**: Structural vulnerability — no special attacker capability needed; delivery receipts must be absent.
- **Scalability**: Affects all channel messages without ACK-based integrity records.
- **Reachability**: Trusted Application Zone (2.5).

*Score source: inherited (baseline 2026-04-26T03-39-12)*

---

## 4. Governance Fields

| ID | Component | Severity | Owner | SLA | Disposition | Review Date |
|----|-----------|----------|-------|-----|-------------|-------------|
| S-1 | User | High | Unassigned | 7d | Mitigate | 2026-05-04 |
| AG-1 | LLM Agent Orchestrator | High | Unassigned | 7d | Mitigate | 2026-05-04 |
| E-2 | LLM Agent Orchestrator | High | Unassigned | 7d | Mitigate | 2026-05-04 |
| R-3 | LLM Agent Orchestrator | High | Unassigned | 7d | Mitigate | 2026-05-04 |
| E-1 | Guardrails Service | High | Unassigned | 7d | Mitigate | 2026-05-04 |
| LLM-6 | LLM Agent Orchestrator | High | Unassigned | 7d | Mitigate | 2026-05-04 |
| OI-2 | LLM Agent Orchestrator | High | Unassigned | 7d | Mitigate | 2026-05-04 |
| LLM-5 | LLM Agent Orchestrator | High | Unassigned | 7d | Mitigate | 2026-05-04 |
| OI-1 | LLM Agent Orchestrator | High | Unassigned | 7d | Mitigate | 2026-05-04 |
| LLM-13 | Clinical Advisory Sub-Agent | High | Unassigned | 7d | Mitigate | 2026-05-04 |
| LLM-8 | Specialist Agent | High | Unassigned | 7d | Mitigate | 2026-05-04 |
| D-10 | LLM Agent Orchestrator | High | Unassigned | 7d | Mitigate | 2026-05-04 |
| D-11 | LLM Agent Orchestrator | High | Unassigned | 7d | Mitigate | 2026-05-04 |
| I-2 | LLM Agent Orchestrator | High | Unassigned | 7d | Mitigate | 2026-05-04 |
| LLM-1 | LLM Agent Orchestrator | High | Unassigned | 7d | Mitigate | 2026-05-04 |
| LLM-15 | LLM Agent Orchestrator | High | Unassigned | 7d | Mitigate | 2026-05-04 |
| LLM-16 | LLM Agent Orchestrator | High | Unassigned | 7d | Mitigate | 2026-05-04 |
| LLM-4 | LLM Agent Orchestrator | High | Unassigned | 7d | Mitigate | 2026-05-04 |
| T-2 | LLM Agent Orchestrator | High | Unassigned | 7d | Mitigate | 2026-05-04 |
| E-5 | MCP Tool Server | High | Unassigned | 7d | Mitigate | 2026-05-04 |
| T-5 | MCP Tool Server | High | Unassigned | 7d | Mitigate | 2026-05-04 |
| AG-5 | MCP Tool Server | Medium | Unassigned | 30d | Review | 2026-05-27 |
| E-7 | Clinical Advisory Sub-Agent | Medium | Unassigned | 30d | Review | 2026-05-27 |
| I-9 | Clinical Advisory Sub-Agent | Medium | Unassigned | 30d | Review | 2026-05-27 |
| LLM-2 | LLM Agent Orchestrator | Medium | Unassigned | 30d | Review | 2026-05-27 |
| D-1 | Guardrails Service | Medium | Unassigned | 30d | Review | 2026-05-27 |
| LLM-7 | LLM Agent Orchestrator | Medium | Unassigned | 30d | Review | 2026-05-27 |
| LLM-14 | Clinical Advisory Sub-Agent | Medium | Unassigned | 30d | Review | 2026-05-27 |
| MI-2 | Clinical Advisory Sub-Agent | Medium | Unassigned | 30d | Review | 2026-05-27 |
| T-9 | Clinical Advisory Sub-Agent | Medium | Unassigned | 30d | Review | 2026-05-27 |
| LLM-10 | Specialist Agent | Medium | Unassigned | 30d | Review | 2026-05-27 |
| MI-1 | Clinical Advisory Sub-Agent | Medium | Unassigned | 30d | Review | 2026-05-27 |
| MI-3 | Clinical Advisory Sub-Agent | Medium | Unassigned | 30d | Review | 2026-05-27 |
| OI-3 | LLM Agent Orchestrator | Medium | Unassigned | 30d | Review | 2026-05-27 |
| E-3 | Specialist Agent | Medium | Unassigned | 30d | Review | 2026-05-27 |
| E-4 | Inter-Agent Communication Channel | Medium | Unassigned | 30d | Review | 2026-05-27 |
| S-5 | Inter-Agent Communication Channel | Medium | Unassigned | 30d | Review | 2026-05-27 |
| S-7 | Long-Running Learning Loop | Medium | Unassigned | 30d | Review | 2026-05-27 |
| AG-3 | Specialist Agent | Medium | Unassigned | 30d | Review | 2026-05-27 |
| AG-6 | MCP Tool Server | Medium | Unassigned | 30d | Review | 2026-05-27 |
| D-2 | LLM Agent Orchestrator | Medium | Unassigned | 30d | Review | 2026-05-27 |
| D-5 | MCP Tool Server | Medium | Unassigned | 30d | Review | 2026-05-27 |
| OI-4 | Clinical Advisory Sub-Agent | Medium | Unassigned | 30d | Review | 2026-05-27 |
| R-1 | User | Medium | Unassigned | 30d | Review | 2026-05-27 |
| S-6 | MCP Tool Server | Medium | Unassigned | 30d | Review | 2026-05-27 |
| AG-2 | LLM Agent Orchestrator | Medium | Unassigned | 30d | Review | 2026-05-27 |
| AG-4 | Inter-Agent Communication Channel | Medium | Unassigned | 30d | Review | 2026-05-27 |
| E-6 | Long-Running Learning Loop | Medium | Unassigned | 30d | Review | 2026-05-27 |
| I-1 | Guardrails Service | Medium | Unassigned | 30d | Review | 2026-05-27 |
| S-3 | LLM Agent Orchestrator | Medium | Unassigned | 30d | Review | 2026-05-27 |
| T-3 | Specialist Agent | Medium | Unassigned | 30d | Review | 2026-05-27 |
| T-4 | Inter-Agent Communication Channel | Medium | Unassigned | 30d | Review | 2026-05-27 |
| S-8 | External API | Medium | Unassigned | 30d | Review | 2026-05-27 |
| S-9 | Clinical Advisory Sub-Agent | Medium | Unassigned | 30d | Review | 2026-05-27 |
| T-7 | Audit Logger | Medium | Unassigned | 30d | Review | 2026-05-27 |
| AG-7 | Long-Running Learning Loop | Medium | Unassigned | 30d | Review | 2026-05-27 |
| D-9 | Clinical Advisory Sub-Agent | Medium | Unassigned | 30d | Review | 2026-05-27 |
| LLM-9 | Specialist Agent | Medium | Unassigned | 30d | Review | 2026-05-27 |
| D-6 | Knowledge Base | Medium | Unassigned | 30d | Review | 2026-05-27 |
| LLM-11 | Long-Running Learning Loop | Medium | Unassigned | 30d | Review | 2026-05-27 |
| T-8 | Long-Running Learning Loop | Medium | Unassigned | 30d | Review | 2026-05-27 |
| D-3 | Specialist Agent | Medium | Unassigned | 30d | Review | 2026-05-27 |
| D-4 | Inter-Agent Communication Channel | Medium | Unassigned | 30d | Review | 2026-05-27 |
| D-7 | Audit Logger | Medium | Unassigned | 30d | Review | 2026-05-27 |
| AG-8 | Inter-Agent Communication Channel | Medium | Unassigned | 30d | Review | 2026-05-27 |
| I-6 | Knowledge Base | Medium | Unassigned | 30d | Review | 2026-05-27 |
| I-7 | Audit Logger | Medium | Unassigned | 30d | Review | 2026-05-27 |
| D-8 | Long-Running Learning Loop | Medium | Unassigned | 30d | Review | 2026-05-27 |
| I-5 | MCP Tool Server | Medium | Unassigned | 30d | Review | 2026-05-27 |
| LLM-3 | LLM Agent Orchestrator | Medium | Unassigned | 30d | Review | 2026-05-27 |
| LLM-12 | Long-Running Learning Loop | Medium | Unassigned | 30d | Review | 2026-05-27 |
| T-6 | Knowledge Base | Medium | Unassigned | 30d | Review | 2026-05-27 |
| R-9 | Clinical Advisory Sub-Agent | Medium | Unassigned | 30d | Review | 2026-05-27 |
| S-2 | Guardrails Service | Medium | Unassigned | 30d | Review | 2026-05-27 |
| I-4 | Inter-Agent Communication Channel | Medium | Unassigned | 30d | Review | 2026-05-27 |
| R-8 | External API | Medium | Unassigned | 30d | Review | 2026-05-27 |
| T-1 | Guardrails Service | Medium | Unassigned | 30d | Review | 2026-05-27 |
| AGP-01 | LLM Agent Orchestrator | Medium | Unassigned | 30d | Review | 2026-05-27 |
| I-8 | Long-Running Learning Loop | Medium | Unassigned | 30d | Review | 2026-05-27 |
| R-7 | Long-Running Learning Loop | Medium | Unassigned | 30d | Review | 2026-05-27 |
| S-4 | Specialist Agent | Medium | Unassigned | 30d | Review | 2026-05-27 |
| I-3 | Specialist Agent | Medium | Unassigned | 30d | Review | 2026-05-27 |
| R-2 | Guardrails Service | Medium | Unassigned | 30d | Review | 2026-05-27 |
| R-4 | Specialist Agent | Medium | Unassigned | 30d | Review | 2026-05-27 |
| R-6 | MCP Tool Server | Medium | Unassigned | 30d | Review | 2026-05-27 |
| R-5 | Inter-Agent Communication Channel | Medium | Unassigned | 30d | Review | 2026-05-27 |

---

## 5. Scoring Methodology

### Scoring Dimensions

| Dimension | Weight | Description |
|-----------|-------:|-------------|
| CVSS Base | 0.35 | Inherent vulnerability severity per CVSS 3.1 base score (0.0-10.0). Captures attack vector, complexity, privilege requirements, user interaction, scope, and CIA impact. |
| Exploitability | 0.30 | Operational attack feasibility: known techniques, attack complexity, tooling availability, and required skill level. Assesses how easily the threat can be weaponized in practice. |
| Scalability | 0.15 | Blast radius and automation potential: scriptability, target scope, resource requirements, and detection difficulty. Captures the economics of exploitation. |
| Reachability | 0.20 | Architecture-aware exposure: trust zone position, zone name refinements, and authentication/segmentation barriers. Derived from threat model trust boundary data. |

### Composite Score Formula

```
Composite = (0.35 × CVSS Base) + (0.30 × Exploitability) + (0.15 × Scalability) + (0.20 × Reachability)
```

### Severity Band Mapping

| Severity Band | Score Range | SLA | Disposition |
|---------------|-------------|-----|-------------|
| Critical | 9.0 – 10.0 | 24h | Mitigate |
| High | 7.0 – 8.9 | 7d | Mitigate |
| Medium | 4.0 – 6.9 | 30d | Review |
| Low | 0.0 – 3.9 | 90d | Review |

### Data Sources

| Source | Role |
|--------|------|
| `threats.md` (F-5 Wave 2) | Primary input: 88 findings (84 UNCHANGED + 4 NEW) |
| Trust zone table (Section 2) | Component-to-zone mapping: User Zone (Untrusted), Application Zone (Trusted), External Services (Semi-Trusted) |
| `architecture.md` | Architecture context: no explicit auth barrier or network segmentation keywords detected for Application Zone |
| CVSS 3.1 specification | Base score calculation for all 4 fresh-scored findings (CG-8 primary D-10) |
| Baseline risk-scores.md (2026-04-26) | Score inheritance source for 84 UNCHANGED findings |

### Reproducibility

Scores are computed at temperature 0 with ±0.5 tolerance per dimension. The four NEW findings (D-10, D-11, LLM-15, LLM-16) form correlation group CG-8 with D-10 as primary; D-11, LLM-15, and LLM-16 inherit all dimensional scores from D-10 per the correlation group scoring protocol. The 84 UNCHANGED findings inherit scores verbatim from the baseline run (2026-04-26T03-39-12), ensuring zero score drift per SC-002. Scoring date: 2026-04-27. Review dates computed as scoring date + SLA duration.
