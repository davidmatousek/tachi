---
schema_version: "1.0"
date: "2026-04-16"
source_file: "examples/maestro-reference/threats.md"
classification: "confidential"
scoring_weights:
  cvss_base: 0.35
  exploitability: 0.30
  scalability: 0.15
  reachability: 0.20
---

# Risk Scores — Healthcare Clinical Decision Support System (CDSS)

> **DISCLAIMER**: This is a security reference scenario for threat-modeling teaching purposes only. It is NOT a real clinical system and contains NO real patient data. Nothing herein constitutes medical advice, regulatory guidance, or a compliance framework recommendation.

---

## Section 1: Executive Summary

**Total findings scored**: 108

### Severity Band Distribution

| Severity Band | Count | Percentage |
|---------------|-------|------------|
| Critical | 0 | 0.0% |
| High | 6 | 5.6% |
| Medium | 96 | 88.9% |
| Low | 6 | 5.6% |

**Highest-risk component**: Physician (external entity, composite 8.4 — S-1 credential replay)

The six High-severity findings are concentrated on the externally reachable perimeter: the Physician external entity (S-1, S-2) and the Physician Clinical Portal (D-1, S-5, T-3, E-1). All other findings score Medium after the four-dimensional model applies reachability penalties — Trusted-zone components (all internal agents, models, and data stores) carry a reachability floor of 1.0, which moderates composite scores substantially even when CVSS base scores reach 9.9. Six findings score Low (I-11, I-12, D-11, D-12, LLM-3, and R-2 are the lowest-scoring findings). No findings reach the Critical composite band (≥9.0).

---

## Section 2: Scored Threat Table

Sorted by composite score descending. Secondary sort by ID alphanumerically.

| ID | Component | Threat | CVSS | Exploit | Scale | Reach | Composite | Severity | SLA | Disp |
|----|-----------|--------|------|---------|-------|-------|-----------|----------|-----|------|
| S-1 | Physician | Attacker replays or forges clinical query cr... | 9.1 | 8.0 | 6.8 | 9.0 | 8.4 | High | 7d | Mitigate |
| S-2 | Patient | Attacker submits fraudulent EHR update event... | 7.5 | 6.8 | 6.3 | 9.0 | 7.4 | High | 7d | Mitigate |
| D-1 | Physician Clinical Portal | Attacker floods portal with clinical query r... | 7.5 | 9.0 | 6.3 | 4.0 | 7.1 | High | 7d | Mitigate |
| E-1 | Physician Clinical Portal | Attacker escalates from low-privilege sessio... | 9.1 | 7.0 | 6.0 | 4.0 | 7.0 | High | 7d | Mitigate |
| S-5 | Inter-Agent Communication Channel | Attacker spoofs supervisor delegation messag... | 9.1 | 6.8 | 6.8 | 4.0 | 7.0 | High | 7d | Mitigate |
| T-3 | Inter-Agent Communication Channel | Attacker tampers with delegation messages or... | 9.1 | 6.5 | 6.8 | 4.0 | 7.0 | High | 7d | Mitigate |
| AG-8 | Inter-Agent Communication Channel | Compromised agent abuses inter-agent channel... | 7.7 | 8.0 | 6.3 | 4.0 | 6.8 | Medium | 30d | Review |
| D-3 | Inter-Agent Communication Channel | Delegation message flood starves specialist... | 7.7 | 8.0 | 6.3 | 4.0 | 6.8 | Medium | 30d | Review |
| E-2 | Patient Summary Generator | Attacker exploits summary generator to acces... | 9.1 | 6.5 | 6.0 | 4.0 | 6.8 | Medium | 30d | Review |
| AGP-01 | Inter-Agent Communication Channel | Multi-agent coordination creates potential f... | 9.1 | 5.8 | 6.3 | 4.0 | 6.7 | Medium | 30d | Review |
| E-8 | Clinical LLM | Prompt injection causes elevated reasoning a... | 9.1 | 7.3 | 6.8 | 1.0 | 6.6 | Medium | 30d | Review |
| E-3 | Inter-Agent Communication Channel | Compromised channel allows escalation to sup... | 9.1 | 5.8 | 6.0 | 4.0 | 6.6 | Medium | 30d | Review |
| T-8 | Clinical LLM | Attacker tampers with prompt inputs forward... | 9.1 | 7.0 | 6.8 | 1.0 | 6.5 | Medium | 30d | Review |
| I-3 | Inter-Agent Communication Channel | PHI disclosed through unencrypted inter-agen... | 7.5 | 6.8 | 6.5 | 4.0 | 6.4 | Medium | 30d | Review |
| E-7 | Clinical MCP Tool Server | Compromised agent escalates to unauthorized... | 9.9 | 6.0 | 6.3 | 1.0 | 6.4 | Medium | 30d | Review |
| S-6 | Supervisor Orchestrator | Attacker impersonates Supervisor Orchestrato... | 9.9 | 5.8 | 6.3 | 1.0 | 6.4 | Medium | 30d | Review |
| D-13 | Model Inference API Gateway | Request floods saturate inference gateway... | 7.7 | 8.0 | 6.0 | 1.0 | 6.2 | Medium | 30d | Review |
| AG-7 | Clinical MCP Tool Server | Tool chaining achieves unauthorized FHIR out... | 9.1 | 6.3 | 6.3 | 1.0 | 6.2 | Medium | 30d | Review |
| T-7 | Clinical MCP Tool Server | Compromised MCP Tool Server tampers with FHI... | 9.1 | 6.3 | 6.3 | 1.0 | 6.2 | Medium | 30d | Review |
| AG-2 | Supervisor Orchestrator | Compromised orchestrator abuses delegation a... | 9.1 | 5.8 | 6.3 | 1.0 | 6.1 | Medium | 30d | Review |
| D-17 | HIPAA RBAC + Policy Engine | RBAC request flood causes policy engine unav... | 7.5 | 8.0 | 5.5 | 1.0 | 6.1 | Medium | 30d | Review |
| I-1 | Physician Clinical Portal | PHI disclosed via insecure HTTPS config or e... | 6.5 | 6.8 | 6.3 | 4.0 | 6.1 | Medium | 30d | Review |
| LLM-4 | Risk Stratification Model | Adversarial patient records manipulate risk... | 8.7 | 6.5 | 6.0 | 1.0 | 6.1 | Medium | 30d | Review |
| T-10 | FHIR Resource Store | Attacker tampers with patient records corrup... | 8.3 | 6.8 | 6.3 | 1.0 | 6.1 | Medium | 30d | Review |
| D-2 | Patient Summary Generator | Spurious summary requests flood Patient Summ... | 5.3 | 8.8 | 5.8 | 4.0 | 6.2 | Medium | 30d | Review |
| S-3 | Physician Clinical Portal | Attacker spoofs portal to intercept clinical... | 6.5 | 5.8 | 5.5 | 4.0 | 5.6 | Medium | 30d | Review |
| T-5 | Diagnostic Agent | Attacker tampers with Diagnostic Agent tool... | 8.2 | 5.8 | 5.5 | 1.0 | 5.6 | Medium | 30d | Review |
| T-6 | Treatment Planner Agent | Attacker tampers with Treatment Planner Agen... | 8.2 | 5.8 | 5.5 | 1.0 | 5.6 | Medium | 30d | Review |
| AG-5 | Treatment Planner Agent | Treatment Planner Agent incorporates adversa... | 8.7 | 4.8 | 5.8 | 1.0 | 5.6 | Medium | 30d | Review |
| E-10 | Model Inference API Gateway | Compromised API Gateway escalates to access... | 9.1 | 4.8 | 5.5 | 1.0 | 5.6 | Medium | 30d | Review |
| S-7 | Diagnostic Agent | Attacker spoofs Diagnostic Agent to inject f... | 9.1 | 5.5 | 5.8 | 1.0 | 5.9 | Medium | 30d | Review |
| S-8 | Treatment Planner Agent | Attacker spoofs Treatment Planner Agent resp... | 9.1 | 5.5 | 5.8 | 1.0 | 5.9 | Medium | 30d | Review |
| S-9 | Clinical MCP Tool Server | Attacker spoofs MCP Tool Server to return ma... | 9.1 | 5.5 | 5.8 | 1.0 | 5.9 | Medium | 30d | Review |
| E-5 | Diagnostic Agent | Compromised Diagnostic Agent escalates to un... | 9.1 | 5.8 | 5.5 | 1.0 | 5.9 | Medium | 30d | Review |
| E-6 | Treatment Planner Agent | Compromised Treatment Planner Agent escalate... | 9.1 | 5.8 | 5.5 | 1.0 | 5.9 | Medium | 30d | Review |
| R-1 | Physician | Physician denies issuing clinical query or c... | 4.3 | 6.0 | 5.3 | 9.0 | 5.9 | Medium | 30d | Review |
| R-2 | Patient | Patient denies submitting EHR update events... | 4.3 | 6.0 | 5.3 | 9.0 | 5.9 | Medium | 30d | Review |
| AG-3 | Diagnostic Agent | Diagnostic Agent autonomously executes unaut... | 9.1 | 5.3 | 5.5 | 1.0 | 5.8 | Medium | 30d | Review |
| E-4 | Supervisor Orchestrator | Compromised orchestrator escalates to bypass... | 9.1 | 5.3 | 5.8 | 1.0 | 5.8 | Medium | 30d | Review |
| E-9 | Risk Stratification Model | Adversarially manipulated risk scores trigge... | 9.1 | 5.3 | 5.3 | 1.0 | 5.8 | Medium | 30d | Review |
| T-4 | Supervisor Orchestrator | Compromised orchestrator tampers with delega... | 8.7 | 5.5 | 6.0 | 1.0 | 5.8 | Medium | 30d | Review |
| I-2 | Patient Summary Generator | Patient summaries include unauthorized PHI... | 6.5 | 6.3 | 5.8 | 4.0 | 5.8 | Medium | 30d | Review |
| AGP-03 | Supervisor Orchestrator | Multi-agent cascading delegation exhibits em... | 9.1 | 4.8 | 5.8 | 1.0 | 5.7 | Medium | 30d | Review |
| AG-4 | Diagnostic Agent | Compromised Diagnostic Agent abuses MCP Tool... | 9.1 | 5.0 | 5.5 | 1.0 | 5.7 | Medium | 30d | Review |
| AG-6 | Treatment Planner Agent | Compromised Treatment Planner Agent abuses M... | 9.1 | 5.0 | 5.5 | 1.0 | 5.7 | Medium | 30d | Review |
| D-8 | Clinical LLM | Large prompt floods exhaust Clinical LLM inf... | 6.5 | 8.0 | 5.8 | 1.0 | 5.7 | Medium | 30d | Review |
| R-5 | Inter-Agent Communication Channel | Channel fails non-repudiable records of dele... | 6.5 | 5.8 | 5.8 | 4.0 | 5.7 | Medium | 30d | Review |
| AG-1 | Supervisor Orchestrator | Autonomous delegation bypasses human oversig... | 6.5 | 5.5 | 5.8 | 1.0 | 5.0 | Medium | 30d | Review |
| R-6 | Supervisor Orchestrator | Orchestrator fails non-repudiable records of... | 6.5 | 5.5 | 5.8 | 1.0 | 5.0 | Medium | 30d | Review |
| I-10 | FHIR Resource Store | Patient PHI disclosed via unauthorized FHIR... | 6.5 | 6.5 | 6.5 | 1.0 | 5.4 | Medium | 30d | Review |
| D-4 | Supervisor Orchestrator | High-volume task result flood causes orchest... | 6.5 | 7.0 | 5.8 | 1.0 | 5.4 | Medium | 30d | Review |
| D-5 | Diagnostic Agent | Tool call floods or retrieval storms disrupt... | 6.5 | 7.0 | 5.5 | 1.0 | 5.4 | Medium | 30d | Review |
| D-7 | Clinical MCP Tool Server | Excessive JSON-RPC calls exhaust MCP server... | 6.5 | 7.0 | 5.5 | 1.0 | 5.4 | Medium | 30d | Review |
| D-10 | FHIR Resource Store | FHIR query or write floods degrade patient r... | 6.5 | 7.0 | 5.5 | 1.0 | 5.4 | Medium | 30d | Review |
| S-4 | Patient Summary Generator | Attacker spoofs Patient Summary Generator to... | 5.9 | 5.3 | 5.3 | 4.0 | 5.3 | Medium | 30d | Review |
| AGP-02 | Outcomes Telemetry and Physician Over... | Persistent-state learning loop enables tempo... | 9.4 | 3.5 | 4.8 | 1.0 | 5.3 | Medium | 30d | Review |
| I-7 | Clinical MCP Tool Server | PHI exposed to unauthorized agents via MCP... | 6.5 | 6.3 | 6.0 | 1.0 | 5.3 | Medium | 30d | Review |
| LLM-1 | Clinical LLM | Clinical LLM PHI exposure (CG-3 peer I-7)... | 6.5 | 6.3 | 6.0 | 1.0 | 5.3 | Medium | 30d | Review |
| T-12 | Medical Literature Vector Index | Attacker injects malicious vector embeddings... | 8.2 | 4.8 | 5.5 | 1.0 | 5.3 | Medium | 30d | Review |
| T-14 | EHR Ingestion Queue | Attacker tampers with EHR events in ingestio... | 7.1 | 5.5 | 6.3 | 1.0 | 5.3 | Medium | 30d | Review |
| T-1 | Physician Clinical Portal | Attacker tampers with clinical recommendatio... | 5.3 | 5.8 | 5.5 | 4.0 | 5.2 | Medium | 30d | Review |
| D-15 | Clinical Audit Log | Excessive log entries cause disk exhaustion... | 6.5 | 6.5 | 5.0 | 1.0 | 5.2 | Medium | 30d | Review |
| D-18 | Consent and De-identification Guardrail | PHI processing flood saturates de-id capaci... | 6.5 | 6.5 | 5.0 | 1.0 | 5.2 | Medium | 30d | Review |
| I-8 | Clinical LLM | Clinical LLM surfaces PHI from training data... | 6.5 | 5.5 | 6.3 | 1.0 | 5.1 | Medium | 30d | Review |
| I-9 | Risk Stratification Model | Risk model leaks patient cohort data via mem... | 6.5 | 6.0 | 5.8 | 1.0 | 5.1 | Medium | 30d | Review |
| LLM-6 | Risk Stratification Model | Membership inference attack violates patient... | 6.5 | 6.0 | 5.5 | 1.0 | 5.1 | Medium | 30d | Review |
| AG-1 | Supervisor Orchestrator | Autonomous delegation (CG-4 peer) | 6.5 | 5.5 | 5.8 | 1.0 | 5.0 | Medium | 30d | Review |
| R-6 | Supervisor Orchestrator | Supervisor repudiation (CG-4 primary) | 6.5 | 5.5 | 5.8 | 1.0 | 5.0 | Medium | 30d | Review |
| T-11 | Clinical Guideline RAG Corpus | Attacker poisons RAG corpus adversarially... | 8.2 | 5.0 | 6.3 | 1.0 | 5.5 | Medium | 30d | Review |
| LLM-5 | Risk Stratification Model | Fine-tuning poisoning (CG-6 peer T-11)... | 8.2 | 5.0 | 6.3 | 1.0 | 5.5 | Medium | 30d | Review |
| T-16 | Outcomes Telemetry and Physician Over... | Attacker injects adversarial override signal... | 9.4 | 4.0 | 5.5 | 1.0 | 5.5 | Medium | 30d | Review |
| T-17 | HIPAA RBAC + Policy Engine | Attacker tampers with RBAC policy rules... | 9.1 | 4.3 | 5.8 | 1.0 | 5.5 | Medium | 30d | Review |
| E-11 | HIPAA RBAC + Policy Engine | Attacker exploits RBAC vulnerability to admi... | 9.1 | 4.5 | 5.3 | 1.0 | 5.5 | Medium | 30d | Review |
| E-12 | Consent and De-identification Guardrail | Attacker bypasses consent enforcement via g... | 9.1 | 4.5 | 5.0 | 1.0 | 5.5 | Medium | 30d | Review |
| T-2 | Patient Summary Generator | Attacker tampers with patient-facing summari... | 6.5 | 5.3 | 5.3 | 4.0 | 5.5 | Medium | 30d | Review |
| T-13 | Model Inference API Gateway | Attacker tampers with API Gateway configurati... | 8.7 | 4.5 | 5.8 | 1.0 | 5.5 | Medium | 30d | Review |
| I-5 | Diagnostic Agent | Diagnostic Agent exposes patient context thr... | 6.5 | 5.5 | 5.3 | 1.0 | 4.9 | Medium | 30d | Review |
| I-6 | Treatment Planner Agent | Treatment Planner Agent discloses patient da... | 6.5 | 5.5 | 5.0 | 1.0 | 4.9 | Medium | 30d | Review |
| I-14 | EHR Ingestion Queue | EHR update events in queue disclosed through... | 6.5 | 5.5 | 5.3 | 1.0 | 4.9 | Medium | 30d | Review |
| I-15 | Clinical Audit Log | Unauthorized audit log read discloses sensit... | 6.5 | 5.5 | 5.3 | 1.0 | 4.9 | Medium | 30d | Review |
| I-16 | Outcomes Telemetry and Physician Over... | Telemetry access discloses clinical patterns... | 6.5 | 5.3 | 5.3 | 1.0 | 4.9 | Medium | 30d | Review |
| R-3 | Physician Clinical Portal | Portal fails non-repudiable recommendation r... | 4.3 | 5.8 | 5.3 | 4.0 | 4.8 | Medium | 30d | Review |
| R-4 | Patient Summary Generator | Summary Generator fails non-repudiable record... | 4.3 | 5.8 | 5.3 | 4.0 | 4.8 | Medium | 30d | Review |
| R-9 | Clinical MCP Tool Server | MCP Tool Server fails non-repudiable FHIR re... | 6.5 | 5.0 | 5.8 | 1.0 | 4.8 | Medium | 30d | Review |
| T-15 | Clinical Audit Log | Attacker tampers with audit log entries... | 5.7 | 5.5 | 6.3 | 1.0 | 4.8 | Medium | 30d | Review |
| I-17 | HIPAA RBAC + Policy Engine | RBAC engine leaks access control policies... | 5.3 | 6.3 | 6.0 | 1.0 | 4.8 | Medium | 30d | Review |
| LLM-3 | Clinical LLM | Adversary extracts Clinical LLM knowledge v... | 5.3 | 6.3 | 5.5 | 1.0 | 4.8 | Medium | 30d | Review |
| D-16 | Outcomes Telemetry and Physician Over... | Spurious override signals degrade learning l... | 5.4 | 6.0 | 5.3 | 1.0 | 4.7 | Medium | 30d | Review |
| LLM-2 | Clinical LLM | Adversary poisons training data via learning... | 8.2 | 3.0 | 5.0 | 1.0 | 4.7 | Medium | 30d | Review |
| R-13 | HIPAA RBAC + Policy Engine | RBAC engine fails non-repudiable access decis... | 6.5 | 4.5 | 5.5 | 1.0 | 4.7 | Medium | 30d | Review |
| D-9 | Risk Stratification Model | High-volume risk inference requests saturate... | 4.3 | 7.3 | 5.0 | 1.0 | 4.6 | Medium | 30d | Review |
| D-6 | Treatment Planner Agent | Oversized retrieval queries exhaust Treatmen... | 4.3 | 7.0 | 5.3 | 1.0 | 4.6 | Medium | 30d | Review |
| D-11 | Clinical Guideline RAG Corpus | Retrieval floods saturate RAG Corpus capacity... | 4.3 | 7.3 | 4.8 | 1.0 | 4.6 | Medium | 30d | Review |
| D-12 | Medical Literature Vector Index | Excessive retrieval queries degrade Vector I... | 4.3 | 7.3 | 4.8 | 1.0 | 4.6 | Medium | 30d | Review |
| D-14 | EHR Ingestion Queue | Malformed EHR events cause queue saturation... | 4.3 | 7.0 | 5.0 | 1.0 | 4.6 | Medium | 30d | Review |
| I-4 | Supervisor Orchestrator | Compromise exposes aggregated sensitive pati... | 4.9 | 5.3 | 5.5 | 1.0 | 4.3 | Medium | 30d | Review |
| I-13 | Model Inference API Gateway | API Gateway exposes inference request logs c... | 4.3 | 5.5 | 5.5 | 1.0 | 4.2 | Medium | 30d | Review |
| S-14 | Consent and De-identification Guardrail | Attacker spoofs guardrail returning raw PHI... | 6.2 | 3.8 | 4.3 | 1.0 | 4.2 | Medium | 30d | Review |
| T-9 | Risk Stratification Model | Attacker tampers with fine-tuning data causi... | 7.0 | 3.0 | 4.5 | 1.0 | 4.2 | Medium | 30d | Review |
| I-18 | Consent and De-identification Guardrail | Guardrail discloses raw PHI through de-ident... | 6.5 | 4.5 | 4.8 | 1.0 | 4.5 | Medium | 30d | Review |
| S-10 | Clinical LLM | Attacker spoofs Clinical LLM completion resp... | 6.5 | 4.3 | 4.8 | 1.0 | 4.5 | Medium | 30d | Review |
| S-11 | Risk Stratification Model | Attacker spoofs Risk Stratification Model ou... | 6.5 | 4.3 | 4.8 | 1.0 | 4.5 | Medium | 30d | Review |
| S-12 | Model Inference API Gateway | Attacker spoofs API Gateway to return fabric... | 6.5 | 4.3 | 5.0 | 1.0 | 4.5 | Medium | 30d | Review |
| S-13 | HIPAA RBAC + Policy Engine | Attacker spoofs RBAC engine to issue false a... | 6.5 | 4.3 | 4.8 | 1.0 | 4.5 | Medium | 30d | Review |
| T-18 | Consent and De-identification Guardrail | Attacker tampers with de-identification conf... | 6.7 | 4.0 | 5.0 | 1.0 | 4.5 | Medium | 30d | Review |
| R-7 | Diagnostic Agent | Diagnostic Agent denies issuing tool calls... | 4.3 | 5.3 | 5.5 | 1.0 | 4.1 | Medium | 30d | Review |
| R-8 | Treatment Planner Agent | Treatment Planner Agent denies tool calls... | 4.3 | 5.3 | 5.5 | 1.0 | 4.1 | Medium | 30d | Review |
| R-10 | Clinical LLM | Clinical LLM fails non-repudiable prompt-com... | 4.3 | 5.3 | 5.5 | 1.0 | 4.1 | Medium | 30d | Review |
| R-11 | Risk Stratification Model | Risk model fails non-repudiable inference r... | 4.3 | 5.3 | 5.5 | 1.0 | 4.1 | Medium | 30d | Review |
| R-12 | Model Inference API Gateway | API Gateway fails non-repudiable inference r... | 4.3 | 5.3 | 5.5 | 1.0 | 4.1 | Medium | 30d | Review |
| I-11 | Clinical Guideline RAG Corpus | RAG Corpus inadvertently indexes patient dat... | 4.3 | 4.5 | 4.5 | 1.0 | 3.7 | Low | 90d | Review |
| I-12 | Medical Literature Vector Index | Vector Index exposes research data or cross-... | 4.3 | 4.5 | 4.5 | 1.0 | 3.7 | Low | 90d | Review |

---

## Section 3: Dimensional Breakdown

### S-1: Attacker may impersonate a legitimate physician by replaying or forging clinical query credentials

**Component**: Physician
**Category**: Spoofing
**MAESTRO Layer**: L7 — Agent Ecosystem
**Composite Score**: 8.4 (High)

| Dimension | Score | Weight | Weighted |
|-----------|-------|--------|----------|
| CVSS Base | 9.1 | 0.35 | 3.19 |
| Exploitability | 8.0 | 0.30 | 2.40 |
| Scalability | 6.8 | 0.15 | 1.02 |
| Reachability | 9.0 | 0.20 | 1.80 |
| **Composite** | | | **8.4** |

**CVSS Vector**: `CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:L`

**Scoring Rationale**:
- **CVSS**: Network-accessible credential replay with no auth required; high confidentiality and integrity impact (PHI access and record modification) plus low availability impact drives score to 9.1.
- **Exploitability**: Credential replay/forging is extensively documented, requires minimal skill, and multiple off-the-shelf tools exist for replay attacks; scored 8.0.
- **Scalability**: Credential replay is highly scriptable and automatable against any physician account, though targeted toward valid physician identities; moderate detection difficulty balances the score to 6.8.
- **Reachability**: Physician is an External Entity in the Untrusted zone with direct internet-facing access; no authentication barriers precede the attacker (the attacker is impersonating the authentication step); scored 9.0.

---

### S-2: Attacker may submit fraudulent EHR update events by spoofing a patient identity

**Component**: Patient
**Category**: Spoofing
**MAESTRO Layer**: L7 — Agent Ecosystem
**Composite Score**: 7.4 (High)

| Dimension | Score | Weight | Weighted |
|-----------|-------|--------|----------|
| CVSS Base | 7.5 | 0.35 | 2.63 |
| Exploitability | 6.8 | 0.30 | 2.04 |
| Scalability | 6.3 | 0.15 | 0.95 |
| Reachability | 9.0 | 0.20 | 1.80 |
| **Composite** | | | **7.4** |

**CVSS Vector**: `CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N`

**Scoring Rationale**:
- **CVSS**: Network-accessible patient identity spoofing with no prerequisites; high integrity impact via false EHR injection into the ingestion pipeline; scored 7.5.
- **Exploitability**: Patient identity spoofing is a well-documented attack class with available tooling, but requires knowledge of patient identity tokens; scored 6.8.
- **Scalability**: Scriptable against multiple patient identities with minimal resources; moderate scope (only patient-identity targets); scored 6.3.
- **Reachability**: Patient is an External Entity in the Untrusted zone with direct access to the EHR ingestion endpoint; scored 9.0.

---

### D-1: Attacker may flood the Physician Clinical Portal with clinical query requests

**Component**: Physician Clinical Portal
**Category**: Denial of Service
**MAESTRO Layer**: L7 — Agent Ecosystem
**Composite Score**: 7.1 (High)

| Dimension | Score | Weight | Weighted |
|-----------|-------|--------|----------|
| CVSS Base | 7.5 | 0.35 | 2.63 |
| Exploitability | 9.0 | 0.30 | 2.70 |
| Scalability | 6.3 | 0.15 | 0.95 |
| Reachability | 4.0 | 0.20 | 0.80 |
| **Composite** | | | **7.1** |

**CVSS Vector**: `CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H`

**Scoring Rationale**:
- **CVSS**: Standard unauthenticated network DoS against a public-facing endpoint; high availability impact, no confidentiality or integrity loss; scored 7.5.
- **Exploitability**: DoS flooding is trivially exploitable — no skill or special conditions required, off-the-shelf tools available, extensively documented; scored 9.0.
- **Scalability**: Highly scriptable and automatable; affects all portal users; moderate resources needed for effective clinical-period disruption; scored 6.3.
- **Reachability**: Physician Clinical Portal is in the User Interface Zone (Semi-Trusted, L7) with one TLS/HTTPS barrier and one network boundary; zone floor applies; scored 4.0.

---

### E-1: Attacker may escalate from low-privilege physician session to access clinical data of other physicians or patients

**Component**: Physician Clinical Portal
**Category**: Privilege Escalation
**MAESTRO Layer**: L7 — Agent Ecosystem
**Composite Score**: 7.0 (High)

| Dimension | Score | Weight | Weighted |
|-----------|-------|--------|----------|
| CVSS Base | 9.1 | 0.35 | 3.19 |
| Exploitability | 7.0 | 0.30 | 2.10 |
| Scalability | 6.0 | 0.15 | 0.90 |
| Reachability | 4.0 | 0.20 | 0.80 |
| **Composite** | | | **7.0** |

**CVSS Vector**: `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:N`

**Scoring Rationale**:
- **CVSS**: IDOR/RBAC bypass on public-facing portal with scope change (accessing other patients' PHI); requires only low-privilege session to exploit; scored 9.1.
- **Exploitability**: Horizontal privilege escalation is well-documented and exploitable with intermediate skill; IDOR enumeration tooling is readily available; scored 7.0.
- **Scalability**: Automatable enumeration against patient IDs; affects all portal users with weak RBAC; moderate detection difficulty; scored 6.0.
- **Reachability**: User Interface Zone (Semi-Trusted) with one auth barrier and one network boundary; zone floor 4.0 applies.

---

### S-5: Attacker who gains access to inter-agent message bus may spoof supervisor delegation messages

**Component**: Inter-Agent Communication Channel
**Category**: Spoofing
**MAESTRO Layer**: L7 — Agent Ecosystem
**Agentic Pattern**: trust_exploitation
**Composite Score**: 7.0 (High)

| Dimension | Score | Weight | Weighted |
|-----------|-------|--------|----------|
| CVSS Base | 9.1 | 0.35 | 3.19 |
| Exploitability | 6.8 | 0.30 | 2.04 |
| Scalability | 6.8 | 0.15 | 1.02 |
| Reachability | 4.0 | 0.20 | 0.80 |
| **Composite** | | | **7.0** |

**CVSS Vector**: `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:L`

**Scoring Rationale**:
- **CVSS**: Forged delegation messages trigger scope-changed execution across specialist agents; high CIA impact with scope change drives score to 9.1.
- **Exploitability**: Inter-agent message spoofing requires bus access (some privilege), but technique is documented in agentic threat research; scored 6.8.
- **Scalability**: A single forged delegation can cascade to multiple specialist agents simultaneously; affects all agent-coordination flows; scored 6.8.
- **Reachability**: Inter-Agent Communication Channel is in the Agent Ecosystem Zone (Semi-Trusted L7) with one auth barrier and one network boundary; zone floor 4.0.

---

### T-3: Attacker with access to the inter-agent message bus may tamper with delegation messages or specialist results in transit

**Component**: Inter-Agent Communication Channel
**Category**: Tampering
**MAESTRO Layer**: L7 — Agent Ecosystem
**Agentic Pattern**: communication_vulnerability
**Composite Score**: 7.0 (High)

| Dimension | Score | Weight | Weighted |
|-----------|-------|--------|----------|
| CVSS Base | 9.1 | 0.35 | 3.19 |
| Exploitability | 6.5 | 0.30 | 1.95 |
| Scalability | 6.8 | 0.15 | 1.02 |
| Reachability | 4.0 | 0.20 | 0.80 |
| **Composite** | | | **7.0** |

**CVSS Vector**: `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:L`

**Scoring Rationale**:
- **CVSS**: Message-in-transit manipulation in the multi-agent bus corrupts clinical reasoning across the pipeline; scope change to specialist agents; scored 9.1.
- **Exploitability**: Requires bus access (low privilege); MITM on internal channels is documented but requires positioning; scored 6.5.
- **Scalability**: Tampering propagates to all delegated agents simultaneously; easily scriptable once bus access is established; scored 6.8.
- **Reachability**: Same as S-5 — Agent Ecosystem Zone Semi-Trusted; zone floor 4.0.

---

### AG-8: Compromised agent may abuse the Inter-Agent Communication Channel for resource exhaustion

**Component**: Inter-Agent Communication Channel
**Category**: Agentic Threats
**MAESTRO Layer**: L7 — Agent Ecosystem
**Agentic Pattern**: communication_vulnerability
**Correlation Group**: Scores inherited from primary finding D-3
**Composite Score**: 6.8 (Medium)

| Dimension | Score | Weight | Weighted |
|-----------|-------|--------|----------|
| CVSS Base | 7.7 | 0.35 | 2.70 |
| Exploitability | 8.0 | 0.30 | 2.40 |
| Scalability | 6.3 | 0.15 | 0.95 |
| Reachability | 4.0 | 0.20 | 0.80 |
| **Composite** | | | **6.8** |

**CVSS Vector**: `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:N/I:N/A:H`

**Scoring Rationale**: (Inherited from CG-5 primary D-3 — same underlying DoS via inter-agent channel flooding)
- **CVSS**: Scope-changed availability impact as channel saturation affects all downstream specialist agents; scored 7.7.
- **Exploitability**: Channel flooding is easily executed by a compromised agent already on the bus; high exploitability; scored 8.0.
- **Scalability**: Scriptable and automatable; universally affects all agent instances on the channel; scored 6.3.
- **Reachability**: Agent Ecosystem Zone (Semi-Trusted L7); zone floor 4.0.

---

### D-3: Attacker may flood the Inter-Agent Communication Channel with spurious delegation messages

**Component**: Inter-Agent Communication Channel
**Category**: Denial of Service
**MAESTRO Layer**: L7 — Agent Ecosystem
**Agentic Pattern**: resource_competition
**Composite Score**: 6.8 (Medium)

| Dimension | Score | Weight | Weighted |
|-----------|-------|--------|----------|
| CVSS Base | 7.7 | 0.35 | 2.70 |
| Exploitability | 8.0 | 0.30 | 2.40 |
| Scalability | 6.3 | 0.15 | 0.95 |
| Reachability | 4.0 | 0.20 | 0.80 |
| **Composite** | | | **6.8** |

**CVSS Vector**: `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:N/I:N/A:H`

**Scoring Rationale**:
- **CVSS**: Scope change as channel saturation denies all downstream specialist agent processing; high availability impact; scored 7.7.
- **Exploitability**: Message flooding is easily scripted; widely documented DoS class; scored 8.0.
- **Scalability**: Universally affects all agent coordination flows; fully automatable; moderate resources needed; scored 6.3.
- **Reachability**: Agent Ecosystem Zone (Semi-Trusted L7); zone floor 4.0.

---

### E-2: Attacker may exploit the Patient Summary Generator to request summaries for unauthorized patients

**Component**: Patient Summary Generator
**Category**: Privilege Escalation
**MAESTRO Layer**: L7 — Agent Ecosystem
**Composite Score**: 6.8 (Medium)

| Dimension | Score | Weight | Weighted |
|-----------|-------|--------|----------|
| CVSS Base | 9.1 | 0.35 | 3.19 |
| Exploitability | 6.5 | 0.30 | 1.95 |
| Scalability | 6.0 | 0.15 | 0.90 |
| Reachability | 4.0 | 0.20 | 0.80 |
| **Composite** | | | **6.8** |

**CVSS Vector**: `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:N`

**Scoring Rationale**:
- **CVSS**: Horizontal privilege escalation to unauthorized patient records; scope change; scored 9.1.
- **Exploitability**: IDOR against patient scope requires low privilege and is documented; moderate skill needed; scored 6.5.
- **Scalability**: Automatable enumeration of patient IDs; affects all patients without proper scope enforcement; scored 6.0.
- **Reachability**: User Interface Zone (Semi-Trusted L7); zone floor 4.0.

---

### AGP-01: Multi-agent coordination creates potential for coordinated malicious action across specialist agents

**Component**: Inter-Agent Communication Channel
**Category**: Agentic Threats
**MAESTRO Layer**: L7 — Agent Ecosystem
**Agentic Pattern**: agent_collusion
**Composite Score**: 6.7 (Medium)

| Dimension | Score | Weight | Weighted |
|-----------|-------|--------|----------|
| CVSS Base | 9.1 | 0.35 | 3.19 |
| Exploitability | 5.8 | 0.30 | 1.74 |
| Scalability | 6.3 | 0.15 | 0.95 |
| Reachability | 4.0 | 0.20 | 0.80 |
| **Composite** | | | **6.7** |

**CVSS Vector**: `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:L`

**Scoring Rationale**:
- **CVSS**: Coordinated multi-agent collusion through the communication channel with scope-changed impact across all specialist agents; scored 9.1.
- **Exploitability**: Agent collusion requires understanding of multi-agent architecture and coordination patterns; moderate skill and emerging tooling; scored 5.8.
- **Scalability**: A single coordinated action can affect multiple agents simultaneously; affects all multi-agent sessions; scored 6.3.
- **Reachability**: Agent Ecosystem Zone (Semi-Trusted L7); zone floor 4.0.

---

### E-8: Attacker may exploit prompt injection in the Clinical LLM to gain elevated reasoning authority

**Component**: Clinical LLM
**Category**: Privilege Escalation
**MAESTRO Layer**: L1 — Foundation Model
**Composite Score**: 6.6 (Medium)

| Dimension | Score | Weight | Weighted |
|-----------|-------|--------|----------|
| CVSS Base | 9.1 | 0.35 | 3.19 |
| Exploitability | 7.3 | 0.30 | 2.19 |
| Scalability | 6.8 | 0.15 | 1.02 |
| Reachability | 1.0 | 0.20 | 0.20 |
| **Composite** | | | **6.6** |

**CVSS Vector**: `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:N`

**Scoring Rationale**:
- **CVSS**: Prompt injection causing scope-changed elevated authority output; full C/I impact; scored 9.1.
- **Exploitability**: Prompt injection is extensively documented with available tooling; requires low privilege to submit prompts; scored 7.3.
- **Scalability**: Easily repeated and scriptable; affects all LLM inference sessions via the API gateway; scored 6.8.
- **Reachability**: Foundation Models Zone (Trusted L1) requires traversal through the API gateway, RBAC, and agent framework layers; scored 1.0.

---

### E-3: Attacker may escalate Inter-Agent Communication Channel access to supervisor-level delegation authority

**Component**: Inter-Agent Communication Channel
**Category**: Privilege Escalation
**MAESTRO Layer**: L7 — Agent Ecosystem
**Agentic Pattern**: trust_exploitation
**Composite Score**: 6.6 (Medium)

| Dimension | Score | Weight | Weighted |
|-----------|-------|--------|----------|
| CVSS Base | 9.1 | 0.35 | 3.19 |
| Exploitability | 5.8 | 0.30 | 1.74 |
| Scalability | 6.0 | 0.15 | 0.90 |
| Reachability | 4.0 | 0.20 | 0.80 |
| **Composite** | | | **6.6** |

**CVSS Vector**: `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:N`

**Scoring Rationale**:
- **CVSS**: Channel privilege escalation to supervisor-level enables scope-changed unauthorized clinical operations; scored 9.1.
- **Exploitability**: Requires bus access and knowledge of supervisor message format; moderate complexity; scored 5.8.
- **Scalability**: Once channel authority is obtained, operations can be executed across all specialist agents; scored 6.0.
- **Reachability**: Agent Ecosystem Zone (Semi-Trusted L7); zone floor 4.0.

---

### T-8: Attacker may tamper with Clinical LLM prompt inputs forwarded by the API Gateway

**Component**: Clinical LLM
**Category**: Tampering
**MAESTRO Layer**: L1 — Foundation Model
**Composite Score**: 6.5 (Medium)

| Dimension | Score | Weight | Weighted |
|-----------|-------|--------|----------|
| CVSS Base | 9.1 | 0.35 | 3.19 |
| Exploitability | 7.0 | 0.30 | 2.10 |
| Scalability | 6.8 | 0.15 | 1.02 |
| Reachability | 1.0 | 0.20 | 0.20 |
| **Composite** | | | **6.5** |

**CVSS Vector**: `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:N`

**Scoring Rationale**:
- **CVSS**: Prompt manipulation at the API gateway layer with scope-changed impact on clinical reasoning outputs; scored 9.1.
- **Exploitability**: Adversarial token injection is well-documented; requires low privilege to inject into the gateway; scored 7.0.
- **Scalability**: Easily repeated across inference sessions; affects all clinical reasoning requests; scored 6.8.
- **Reachability**: Foundation Models Zone (Trusted L1); multiple barriers reduce to 1.0.

---

*(Dimensional breakdowns continue for all 108 findings in the same format. The above covers the top 14 findings by composite score. The remaining 94 findings are scored per the table in Section 2.)*

---

## Section 4: Governance Fields

Scoring date: 2026-04-16. Review dates: Critical +1 day (2026-04-17), High +7 days (2026-04-23), Medium +30 days (2026-05-16), Low +90 days (2026-07-15).

| ID | Component | Severity | Owner | SLA | Disposition | Review Date |
|----|-----------|----------|-------|-----|-------------|-------------|
| S-1 | Physician | High | Unassigned | 7d | Mitigate | 2026-04-23 |
| S-2 | Patient | High | Unassigned | 7d | Mitigate | 2026-04-23 |
| D-1 | Physician Clinical Portal | High | Unassigned | 7d | Mitigate | 2026-04-23 |
| E-1 | Physician Clinical Portal | High | Unassigned | 7d | Mitigate | 2026-04-23 |
| S-5 | Inter-Agent Communication Channel | High | Unassigned | 7d | Mitigate | 2026-04-23 |
| T-3 | Inter-Agent Communication Channel | High | Unassigned | 7d | Mitigate | 2026-04-23 |
| AG-8 | Inter-Agent Communication Channel | Medium | Unassigned | 30d | Review | 2026-05-16 |
| D-3 | Inter-Agent Communication Channel | Medium | Unassigned | 30d | Review | 2026-05-16 |
| E-2 | Patient Summary Generator | Medium | Unassigned | 30d | Review | 2026-05-16 |
| AGP-01 | Inter-Agent Communication Channel | Medium | Unassigned | 30d | Review | 2026-05-16 |
| E-8 | Clinical LLM | Medium | Unassigned | 30d | Review | 2026-05-16 |
| E-3 | Inter-Agent Communication Channel | Medium | Unassigned | 30d | Review | 2026-05-16 |
| T-8 | Clinical LLM | Medium | Unassigned | 30d | Review | 2026-05-16 |
| I-3 | Inter-Agent Communication Channel | Medium | Unassigned | 30d | Review | 2026-05-16 |
| E-7 | Clinical MCP Tool Server | Medium | Unassigned | 30d | Review | 2026-05-16 |
| S-6 | Supervisor Orchestrator | Medium | Unassigned | 30d | Review | 2026-05-16 |
| D-13 | Model Inference API Gateway | Medium | Unassigned | 30d | Review | 2026-05-16 |
| AG-7 | Clinical MCP Tool Server | Medium | Unassigned | 30d | Review | 2026-05-16 |
| T-7 | Clinical MCP Tool Server | Medium | Unassigned | 30d | Review | 2026-05-16 |
| AG-2 | Supervisor Orchestrator | Medium | Unassigned | 30d | Review | 2026-05-16 |
| D-17 | HIPAA RBAC + Policy Engine | Medium | Unassigned | 30d | Review | 2026-05-16 |
| I-1 | Physician Clinical Portal | Medium | Unassigned | 30d | Review | 2026-05-16 |
| LLM-4 | Risk Stratification Model | Medium | Unassigned | 30d | Review | 2026-05-16 |
| T-10 | FHIR Resource Store | Medium | Unassigned | 30d | Review | 2026-05-16 |
| D-2 | Patient Summary Generator | Medium | Unassigned | 30d | Review | 2026-05-16 |
| S-3 | Physician Clinical Portal | Medium | Unassigned | 30d | Review | 2026-05-16 |
| T-5 | Diagnostic Agent | Medium | Unassigned | 30d | Review | 2026-05-16 |
| T-6 | Treatment Planner Agent | Medium | Unassigned | 30d | Review | 2026-05-16 |
| AG-5 | Treatment Planner Agent | Medium | Unassigned | 30d | Review | 2026-05-16 |
| E-10 | Model Inference API Gateway | Medium | Unassigned | 30d | Review | 2026-05-16 |
| S-7 | Diagnostic Agent | Medium | Unassigned | 30d | Review | 2026-05-16 |
| S-8 | Treatment Planner Agent | Medium | Unassigned | 30d | Review | 2026-05-16 |
| S-9 | Clinical MCP Tool Server | Medium | Unassigned | 30d | Review | 2026-05-16 |
| E-5 | Diagnostic Agent | Medium | Unassigned | 30d | Review | 2026-05-16 |
| E-6 | Treatment Planner Agent | Medium | Unassigned | 30d | Review | 2026-05-16 |
| R-1 | Physician | Medium | Unassigned | 30d | Review | 2026-05-16 |
| R-2 | Patient | Medium | Unassigned | 30d | Review | 2026-05-16 |
| AG-3 | Diagnostic Agent | Medium | Unassigned | 30d | Review | 2026-05-16 |
| E-4 | Supervisor Orchestrator | Medium | Unassigned | 30d | Review | 2026-05-16 |
| E-9 | Risk Stratification Model | Medium | Unassigned | 30d | Review | 2026-05-16 |
| T-4 | Supervisor Orchestrator | Medium | Unassigned | 30d | Review | 2026-05-16 |
| I-2 | Patient Summary Generator | Medium | Unassigned | 30d | Review | 2026-05-16 |
| AGP-03 | Supervisor Orchestrator | Medium | Unassigned | 30d | Review | 2026-05-16 |
| AG-4 | Diagnostic Agent | Medium | Unassigned | 30d | Review | 2026-05-16 |
| AG-6 | Treatment Planner Agent | Medium | Unassigned | 30d | Review | 2026-05-16 |
| D-8 | Clinical LLM | Medium | Unassigned | 30d | Review | 2026-05-16 |
| R-5 | Inter-Agent Communication Channel | Medium | Unassigned | 30d | Review | 2026-05-16 |
| I-10 | FHIR Resource Store | Medium | Unassigned | 30d | Review | 2026-05-16 |
| D-4 | Supervisor Orchestrator | Medium | Unassigned | 30d | Review | 2026-05-16 |
| D-5 | Diagnostic Agent | Medium | Unassigned | 30d | Review | 2026-05-16 |
| D-7 | Clinical MCP Tool Server | Medium | Unassigned | 30d | Review | 2026-05-16 |
| D-10 | FHIR Resource Store | Medium | Unassigned | 30d | Review | 2026-05-16 |
| S-4 | Patient Summary Generator | Medium | Unassigned | 30d | Review | 2026-05-16 |
| AGP-02 | Outcomes Telemetry and Physician Override Audit Store | Medium | Unassigned | 30d | Review | 2026-05-16 |
| I-7 | Clinical MCP Tool Server | Medium | Unassigned | 30d | Review | 2026-05-16 |
| LLM-1 | Clinical LLM | Medium | Unassigned | 30d | Review | 2026-05-16 |
| T-12 | Medical Literature Vector Index | Medium | Unassigned | 30d | Review | 2026-05-16 |
| T-14 | EHR Ingestion Queue | Medium | Unassigned | 30d | Review | 2026-05-16 |
| T-1 | Physician Clinical Portal | Medium | Unassigned | 30d | Review | 2026-05-16 |
| D-15 | Clinical Audit Log | Medium | Unassigned | 30d | Review | 2026-05-16 |
| D-18 | Consent and De-identification Guardrail | Medium | Unassigned | 30d | Review | 2026-05-16 |
| I-8 | Clinical LLM | Medium | Unassigned | 30d | Review | 2026-05-16 |
| I-9 | Risk Stratification Model | Medium | Unassigned | 30d | Review | 2026-05-16 |
| LLM-6 | Risk Stratification Model | Medium | Unassigned | 30d | Review | 2026-05-16 |
| T-11 | Clinical Guideline RAG Corpus | Medium | Unassigned | 30d | Review | 2026-05-16 |
| LLM-5 | Risk Stratification Model | Medium | Unassigned | 30d | Review | 2026-05-16 |
| T-16 | Outcomes Telemetry and Physician Override Audit Store | Medium | Unassigned | 30d | Review | 2026-05-16 |
| T-17 | HIPAA RBAC + Policy Engine | Medium | Unassigned | 30d | Review | 2026-05-16 |
| E-11 | HIPAA RBAC + Policy Engine | Medium | Unassigned | 30d | Review | 2026-05-16 |
| E-12 | Consent and De-identification Guardrail | Medium | Unassigned | 30d | Review | 2026-05-16 |
| T-2 | Patient Summary Generator | Medium | Unassigned | 30d | Review | 2026-05-16 |
| T-13 | Model Inference API Gateway | Medium | Unassigned | 30d | Review | 2026-05-16 |
| I-5 | Diagnostic Agent | Medium | Unassigned | 30d | Review | 2026-05-16 |
| I-6 | Treatment Planner Agent | Medium | Unassigned | 30d | Review | 2026-05-16 |
| I-14 | EHR Ingestion Queue | Medium | Unassigned | 30d | Review | 2026-05-16 |
| I-15 | Clinical Audit Log | Medium | Unassigned | 30d | Review | 2026-05-16 |
| I-16 | Outcomes Telemetry and Physician Override Audit Store | Medium | Unassigned | 30d | Review | 2026-05-16 |
| R-3 | Physician Clinical Portal | Medium | Unassigned | 30d | Review | 2026-05-16 |
| R-4 | Patient Summary Generator | Medium | Unassigned | 30d | Review | 2026-05-16 |
| R-9 | Clinical MCP Tool Server | Medium | Unassigned | 30d | Review | 2026-05-16 |
| T-15 | Clinical Audit Log | Medium | Unassigned | 30d | Review | 2026-05-16 |
| I-17 | HIPAA RBAC + Policy Engine | Medium | Unassigned | 30d | Review | 2026-05-16 |
| LLM-3 | Clinical LLM | Medium | Unassigned | 30d | Review | 2026-05-16 |
| D-16 | Outcomes Telemetry and Physician Override Audit Store | Medium | Unassigned | 30d | Review | 2026-05-16 |
| LLM-2 | Clinical LLM | Medium | Unassigned | 30d | Review | 2026-05-16 |
| R-13 | HIPAA RBAC + Policy Engine | Medium | Unassigned | 30d | Review | 2026-05-16 |
| D-9 | Risk Stratification Model | Medium | Unassigned | 30d | Review | 2026-05-16 |
| D-6 | Treatment Planner Agent | Medium | Unassigned | 30d | Review | 2026-05-16 |
| D-11 | Clinical Guideline RAG Corpus | Medium | Unassigned | 30d | Review | 2026-05-16 |
| D-12 | Medical Literature Vector Index | Medium | Unassigned | 30d | Review | 2026-05-16 |
| D-14 | EHR Ingestion Queue | Medium | Unassigned | 30d | Review | 2026-05-16 |
| AG-1 | Supervisor Orchestrator | Medium | Unassigned | 30d | Review | 2026-05-16 |
| R-6 | Supervisor Orchestrator | Medium | Unassigned | 30d | Review | 2026-05-16 |
| I-4 | Supervisor Orchestrator | Medium | Unassigned | 30d | Review | 2026-05-16 |
| I-13 | Model Inference API Gateway | Medium | Unassigned | 30d | Review | 2026-05-16 |
| S-14 | Consent and De-identification Guardrail | Medium | Unassigned | 30d | Review | 2026-05-16 |
| T-9 | Risk Stratification Model | Medium | Unassigned | 30d | Review | 2026-05-16 |
| I-18 | Consent and De-identification Guardrail | Medium | Unassigned | 30d | Review | 2026-05-16 |
| S-10 | Clinical LLM | Medium | Unassigned | 30d | Review | 2026-05-16 |
| S-11 | Risk Stratification Model | Medium | Unassigned | 30d | Review | 2026-05-16 |
| S-12 | Model Inference API Gateway | Medium | Unassigned | 30d | Review | 2026-05-16 |
| S-13 | HIPAA RBAC + Policy Engine | Medium | Unassigned | 30d | Review | 2026-05-16 |
| T-18 | Consent and De-identification Guardrail | Medium | Unassigned | 30d | Review | 2026-05-16 |
| R-7 | Diagnostic Agent | Medium | Unassigned | 30d | Review | 2026-05-16 |
| R-8 | Treatment Planner Agent | Medium | Unassigned | 30d | Review | 2026-05-16 |
| R-10 | Clinical LLM | Medium | Unassigned | 30d | Review | 2026-05-16 |
| R-11 | Risk Stratification Model | Medium | Unassigned | 30d | Review | 2026-05-16 |
| R-12 | Model Inference API Gateway | Medium | Unassigned | 30d | Review | 2026-05-16 |
| I-11 | Clinical Guideline RAG Corpus | Low | Unassigned | 90d | Review | 2026-07-15 |
| I-12 | Medical Literature Vector Index | Low | Unassigned | 90d | Review | 2026-07-15 |

---

## Section 5: Scoring Methodology

### Scoring Dimensions

| Dimension | Weight | Description |
|-----------|--------|-------------|
| CVSS Base | 0.35 | CVSS 3.1 base score reflecting inherent vulnerability severity (attack vector, complexity, prerequisites, CIA impact). Independent of deployment context. |
| Exploitability | 0.30 | Practical attack feasibility: Known Techniques + Attack Complexity + Tooling Availability + Skill Level (average of 4 sub-dimensions, 0–10). |
| Scalability | 0.15 | Attack blast radius and automation potential: Scriptability + Target Scope + Resource Requirements + Detection Difficulty (average of 4 sub-dimensions, 0–10). |
| Reachability | 0.20 | Architecture-aware exposure based on trust zone placement: Untrusted [8.0–10.0], Semi-Trusted [4.0–7.0], Trusted [1.0–4.0]. Adjusted for authentication barriers (−1.5/barrier) and network segmentation (−1.0/boundary) per architecture.md. |

### Composite Score Formula

```
Composite = (0.35 × CVSS Base) + (0.30 × Exploitability) + (0.15 × Scalability) + (0.20 × Reachability)
```

All scores rounded to one decimal place. Range: 0.0–10.0.

### Severity Band Mapping

| Severity Band | Score Range | SLA | Disposition |
|---------------|-------------|-----|-------------|
| Critical | 9.0 – 10.0 | 24h | Mitigate |
| High | 7.0 – 8.9 | 7d | Mitigate |
| Medium | 4.0 – 6.9 | 30d | Review |
| Low | 0.0 – 3.9 | 90d | Review |

Boundary values map to the higher band (7.0 = High, 9.0 = Critical).

### Trust Zone Reachability Assignments (this run)

| Zone | Trust Level | Baseline | Architecture Adj | Final Reach |
|------|-------------|----------|-----------------|-------------|
| External Zone | Untrusted | 9.0 | 0 | 9.0 |
| User Interface Zone (L7) | Semi-Trusted | 6.0 | −2.0 (1 auth + 1 net) | 4.0 |
| Agent Ecosystem Zone (L7) | Semi-Trusted | 5.5 | −2.5 (1 auth + 1 net) | 4.0 |
| Agent Frameworks Zone (L3) | Trusted | 2.5 | −3.5 (2 auth + 1 net) | 1.0 |
| Foundation Models Zone (L1) | Trusted | 2.5 | −3.5 (2 auth + 1 net) | 1.0 |
| Data Operations Zone (L2) | Trusted | 2.5 | −3.5 (2 auth + 1 net) | 1.0 |
| Deployment Infrastructure Zone (L4) | Trusted | 2.5 | −3.5 (2 auth + 1 net) | 1.0 |
| Evaluation and Observability Zone (L5) | Trusted | 2.5 | −3.5 (2 auth + 1 net) | 1.0 |
| Security and Compliance Zone (L6) | Trusted | 2.5 | −3.5 (2 auth + 1 net) | 1.0 |

### Correlation Group Score Inheritance

Six correlation groups (CG-1 through CG-6) were identified in Section 4a of threats.md. Per-group primary and peer scores:

| Group | Primary | Peers | Composite | Severity |
|-------|---------|-------|-----------|----------|
| CG-1 | T-7 | AG-7 | 6.2 | Medium |
| CG-2 | E-7 | (AG-7 already in CG-1) | 6.4 | Medium |
| CG-3 | I-7 | LLM-1 | 5.3 | Medium |
| CG-4 | R-6 | AG-1 | 5.0 | Medium |
| CG-5 | D-3 | AG-8 | 6.8 | Medium |
| CG-6 | T-11 | LLM-5 | 5.5 | Medium |

### Data Sources

- **Findings**: `examples/maestro-reference/threats.md` (108 findings, schema v1.4)
- **Trust Zones**: `threats.md` Section 2 (9 zones, 20 components)
- **Architecture**: `examples/maestro-reference/architecture.md` (Mermaid flowchart, CDSS reference)
- **Category Defaults**: `schemas/risk-scoring.yaml` (CVSS baselines per category)
- **Scoring date**: 2026-04-16

### Reproducibility

Scores are produced at temperature 0. Per-dimension tolerance: ±0.5. Composite score tolerance: ±0.3 due to rounding across four weighted sub-scores. All numeric values carry exactly one decimal place with trailing zeros preserved.
