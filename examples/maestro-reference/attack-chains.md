---
schema_version: "1.0"
date: "2026-04-16"
chain_count: 3
surfaced_count: 3
---

# Cross-Layer Attack Chains — Healthcare Clinical Decision Support System (CDSS)

## Section 1: Chain Summary

| Chain ID | Title | Layers | Max Severity | Finding Count | Chain-Breaking Target |
|----------|-------|--------|--------------|---------------|-----------------------|
| CHAIN-001 | RAG Corpus Poisoning to False Clinical Recommendation via Agent Hijack | L2 → L3 → L5 → L6 → L7 | Critical | 5 | T-15 |
| CHAIN-002 | Prompt Injection to Orchestrator Privilege Escalation via Foundation Model | L7 → L1 → L3 → L6 | Critical | 4 | LLM-1 |
| CHAIN-003 | Outcomes Telemetry Tampering to Model Drift via Learning Loop | L5 → L1 → L3 → L7 | Critical | 4 | T-16 |

## Section 2: Chain Details

### CHAIN-001: RAG Corpus Poisoning to False Clinical Recommendation via Agent Hijack

**Layers**: L2 → L3 → L5 → L6 → L7
**Max Severity**: Critical
**Surfaced**: Yes

#### Member Findings

| Finding ID | MAESTRO Layer | Role | Component | Category | Severity |
|------------|---------------|------|-----------|----------|----------|
| T-11 | L2 — Data Operations | initial_exploit | Clinical Guideline RAG Corpus | Tampering | Critical |
| T-5 | L3 — Agent Framework | intermediate_cascade | Diagnostic Agent | Tampering | High |
| T-15 | L5 — Evaluation and Observability | intermediate_cascade | Clinical Audit Log | Tampering | High |
| T-17 | L6 — Security and Compliance | intermediate_cascade | HIPAA RBAC + Policy Engine | Tampering | Medium |
| I-1 | L7 — Agent Ecosystem | terminal_impact | Physician Clinical Portal | Info-Disclosure | High |

#### Attack Progression

An adversary initiates the chain by injecting adversarially crafted embeddings into the Clinical Guideline RAG Corpus (L2 — Data Operations). This poisoning attack corrupts the retrieval index with malicious clinical guidance documents that appear legitimate but encode attacker-preferred diagnostic recommendations. The RAG corpus lies upstream of all Diagnostic Agent guideline lookups and is unauthenticated for provenance at the embedding level.

The corrupted corpus triggers manipulation of Diagnostic Agent (L3 — Agent Framework) tool call behavior. When the Diagnostic Agent issues a guideline retrieval query, the poisoned corpus surfaces adversarial guidance, which the agent incorporates into its tool call parameters and specialist diagnostic outputs forwarded through the Inter-Agent Communication Channel. The agent's decision-making is subverted without any individual component being overtly compromised.

The compromised diagnostic output enables Clinical Audit Log (L5 — Evaluation and Observability) tampering. An attacker aware of the attack progression covers tracks by suppressing or modifying the Diagnostic Agent's decision log entries before they propagate to the Outcomes Telemetry store, eliminating the forensic trail of the poisoning event.

The audit trail suppression enables HIPAA RBAC + Policy Engine (L6 — Security and Compliance) policy tampering. Without a complete audit trail, anomalous access patterns associated with the attack are not flagged, allowing the attacker to modify RBAC policies to grant elevated access to the compromised clinical workflow.

Finally, the compounded upstream manipulations manifest as false clinical recommendation disclosure at the Physician Clinical Portal (L7 — Agent Ecosystem) — a physician receives a recommendation grounded in adversarial guidelines, presented with full apparent clinical authority.

Remediating T-15 (Clinical Audit Log tampering — the intermediate cascade at L5) would disconnect the upstream diagnostic chain from the downstream security control bypass, as the audit suppression is the structural link enabling the L6 RBAC manipulation.

#### Chain-Breaking Controls

**Target**: T-15 (L5 — Evaluation and Observability)
**Rationale**: Removing this finding at L5 disconnects 2 upstream findings from 2 downstream findings in the chain. The audit log tampering is the pivot that allows the L2 → L3 exploit chain to evade the L6 security controls.
**Recommendation**: Implement append-only audit log storage with cryptographic chaining (WORM storage or distributed ledger). Apply write-access restrictions limiting audit log writes to authenticated service identities only with per-write integrity receipts.
**Note**: This is a heuristic recommendation based on structural centrality analysis, not verified control effectiveness.

---

### CHAIN-002: Prompt Injection to Orchestrator Privilege Escalation via Foundation Model

**Layers**: L7 → L1 → L3 → L6
**Max Severity**: Critical
**Surfaced**: Yes

#### Member Findings

| Finding ID | MAESTRO Layer | Role | Component | Category | Severity |
|------------|---------------|------|-----------|----------|----------|
| S-1 | L7 — Agent Ecosystem | initial_exploit | Physician | Spoofing | Critical |
| LLM-1 | L1 — Foundation Model | intermediate_cascade | Clinical LLM | LLM (prompt injection) | Critical |
| E-4 | L3 — Agent Framework | intermediate_cascade | Supervisor Orchestrator | Privilege-Escalation | High |
| E-11 | L6 — Security and Compliance | terminal_impact | HIPAA RBAC + Policy Engine | Privilege-Escalation | Medium |

#### Attack Progression

The chain initiates at the Agent Ecosystem boundary (L7) where an attacker spoofs a legitimate physician identity to gain authenticated access to the Physician Clinical Portal. The spoofed session carries valid-appearing credentials that bypass initial authentication gates, establishing a foothold in the clinical query pipeline under a trusted physician identity.

The spoofed physician session shifts the attack surface to the Foundation Model layer (L1), where the attacker crafts malicious clinical queries containing adversarial prompt injection payloads embedded within the apparent clinical question. When forwarded through the API Gateway to the Clinical LLM, the injected instructions direct the model to emit completions containing embedded system commands or escalated instruction patterns that the Supervisor Orchestrator's prompt parser may interpret as trusted control signals.

The manipulated LLM completion enables Supervisor Orchestrator privilege escalation (L3 — Agent Framework). The orchestrator, receiving a completion that appears to originate from the trusted Clinical LLM inference endpoint, may execute embedded instructions that bypass its own RBAC compliance check logic, effectively granting the attacker's session elevated orchestration authority — including the ability to issue delegation commands beyond the spoofed physician's authorized scope.

The orchestrator privilege escalation manifests as HIPAA RBAC + Policy Engine administrative compromise (L6 — Security and Compliance), where the now-escalated orchestrator session is used to modify RBAC policies or exploit the policy engine's trust in the orchestrator service account, creating durable unauthorized access.

Remediating LLM-1 (prompt injection at L1 — the first intermediate cascade) breaks the chain by preventing the foundation model layer from converting the spoofed credential into an escalation payload.

#### Chain-Breaking Controls

**Target**: LLM-1 (L1 — Foundation Model)
**Rationale**: Removing this finding at L1 disconnects 1 upstream finding from 2 downstream findings in the chain. The prompt injection at the foundation model layer is the mechanism that translates external spoofing into internal privilege escalation.
**Recommendation**: Implement prompt injection detection and sanitization at the API Gateway before forwarding to the Clinical LLM. Apply output schema validation to reject completions containing system command patterns. Use system prompt hardening with instruction hierarchy enforcement.
**Note**: This is a heuristic recommendation based on structural centrality analysis, not verified control effectiveness.

---

### CHAIN-003: Outcomes Telemetry Tampering to Model Drift via Learning Loop

**Layers**: L5 → L1 → L3 → L7
**Max Severity**: Critical
**Surfaced**: Yes

#### Member Findings

| Finding ID | MAESTRO Layer | Role | Component | Category | Severity |
|------------|---------------|------|-----------|----------|----------|
| T-16 | L5 — Evaluation and Observability | initial_exploit | Outcomes Telemetry and Physician Override Audit Store | Tampering | Critical |
| LLM-2 | L1 — Foundation Model | intermediate_cascade | Clinical LLM | LLM (data poisoning) | High |
| T-4 | L3 — Agent Framework | intermediate_cascade | Supervisor Orchestrator | Tampering | High |
| I-1 | L7 — Agent Ecosystem | terminal_impact | Physician Clinical Portal | Info-Disclosure | High |

#### Attack Progression

The attack initiates at the Evaluation and Observability layer (L5) by tampering with the Outcomes Telemetry and Physician Override Audit Store. An adversary with write access to this store injects adversarially crafted physician-override signals — false feedback indicating that certain high-risk clinical recommendations were endorsed by physicians when they were not. This telemetry store is the primary feedback channel for the long-running learning loop that drives continual model re-training.

The corrupted telemetry triggers data poisoning of the Clinical LLM (L1 — Foundation Model) during the next scheduled learning loop re-training cycle. The adversarial physician-override signals are incorporated as positive training examples, causing the model to drift toward systematically producing the attacker's preferred clinical outputs for specific patient presentations — a temporal attack that may not surface until weeks after the initial telemetry injection.

The model drift enables Supervisor Orchestrator tampering (L3 — Agent Framework), where the corrupted Clinical LLM now returns biased completions that cause the orchestrator's aggregation logic to synthesize clinical recommendations that favor the attacker's preferred outcomes. The orchestrator's delegation decisions are themselves corrupted because the foundation model completion that informs them has been systematically shifted.

The compounded corruption manifests as false clinical recommendation disclosure at the Physician Clinical Portal (L7 — Agent Ecosystem), where physicians receive systematically biased recommendations for specific patient cohorts — recommendations grounded in adversarially shifted model behavior that is indistinguishable from legitimate clinical AI output.

Remediating T-16 (Outcomes Telemetry tampering at L5 — the initial exploit) prevents the adversarial signals from ever reaching the learning loop, breaking the entire chain at its source before the model layer is affected.

#### Chain-Breaking Controls

**Target**: T-16 (L5 — Evaluation and Observability)
**Rationale**: Removing this finding at L5 disconnects 0 upstream findings from 3 downstream findings in the chain. The telemetry tampering is the source exploit — remediating it eliminates the adversarial signal before it can propagate through the learning loop to the foundation model and onward.
**Recommendation**: Implement provenance attestation on all physician-override records before ingestion into the learning loop. Apply cryptographic signing of physician override events at point-of-creation. Restrict write access to the Outcomes Telemetry store to verified physician identity tokens with audit logging. Implement behavioral baselining to detect model drift after each re-training cycle.
**Note**: This is a heuristic recommendation based on structural centrality analysis, not verified control effectiveness.
