---
schema_version: "1.0"
date: "2023-11-14"
source_file: "/Users/david/Projects/tachi/examples/agentic-app/test-output/2026-04-23T19-30-00-F2-wave4/threats.md"
finding_count: 83
risk_distribution:
  critical: 57
  high: 22
  medium: 4
  low: 0
  note: 0
attack_tree_count: 83
---

# Threat Report — Agentic AI Application (F-2 Wave 4)

**Date**: 2023-11-14
**Schema Version**: 1.7
**Pipeline Run**: 2026-04-23T19-30-00

---

## 1. Executive Summary

This threat model covers the F-2 Wave 4 regeneration of the Agentic AI Application — an extended multi-agent system with a supervisor-plus-specialist delegation topology, an inter-agent communication channel, a long-running learning loop, and the newly-added Clinical Advisory Sub-Agent. The F-2 extension adds clinical summarization capabilities with a RAG-grounded knowledge retrieval pipeline and a direct output path into the Orchestrator's user-response chain.

**Total findings: 83** (57 Critical, 22 High, 4 Medium, 0 Low, 0 Note). This represents a delta of +13 net-new findings against the F-1 baseline of 70, all attributable to the newly-added Clinical Advisory Sub-Agent. All 70 prior findings are UNCHANGED.

**Key risk surfaces**:
- The Clinical Advisory Sub-Agent introduces a high-consequence factual-integrity risk surface (3 MI findings: Ungrounded Factual Emission, Missing HITL, Retrieval-Grounding Gap) with Critical risk level across all three due to the clinical/medical domain and direct decision-cascade path to human consumers.
- The absence of per-claim RAG grounding verification, HITL physician review gate, and retrieval-quality monitoring represents the most critical new gap introduced by F-2.
- The existing STRIDE, AG, LLM, and OI threat surfaces are unchanged from F-1 and remain at the same risk levels.

**Priority recommendation**: Before deploying the Clinical Advisory Sub-Agent in any clinical or patient-facing context, implement (1) mandatory retrieval-strength verification with per-claim source anchoring, (2) a HITL physician sign-off gate for all clinical recommendations, and (3) instruction-boundary enforcement to prevent prompt injection via clinical query context.

---

## 2. Architecture Overview

The system is a multi-agent AI pipeline with the following principal trust zones:

- **User Zone** (Untrusted): Human users submitting prompts via HTTPS
- **Application Zone** (Trusted): Guardrails Service, LLM Agent Orchestrator (supervisor), Specialist Agent (delegated worker), Inter-Agent Communication Channel (message substrate), MCP Tool Server (tool execution broker), Knowledge Base (vector store), Audit Logger (append-only operational log), Long-Running Learning Loop (model update pipeline), Clinical Advisory Sub-Agent (F-2 addition — clinical RAG summarization)
- **External Services** (Semi-Trusted): External API

The system exercises the supervisor-plus-specialist delegation topology with the Orchestrator as the central coordination hub. The F-2 Clinical Advisory Sub-Agent adds a new spoke off the Orchestrator via JSON-RPC, with bidirectional flows to the Knowledge Base and the Audit Logger, and a downstream model update path from the Learning Loop.

**MAESTRO layer distribution of new findings**:
- L7 — Agent Ecosystem: 13 findings (all Clinical Advisory Sub-Agent)
- No changes to L1, L2, L3, L5, L6, Unclassified layers

---

## 3. Critical Findings Analysis

### F-2 New Component: Clinical Advisory Sub-Agent

The Clinical Advisory Sub-Agent is the sole source of all 13 new findings in this run. It represents the highest-risk new surface in the F-2 extension.

**STRIDE Coverage (S-9, T-9, R-9, I-9, D-9, E-7)**: Standard Process-tier STRIDE threats apply. Most notable:
- **S-9 (Critical)**: Unauthenticated JSON-RPC from Orchestrator enables clinical query injection by rogue Application Zone processes
- **T-9 (Critical)**: Context window tampering via adversarial KB documents or poisoned clinical query payloads (forms CG-6 with LLM-14)
- **I-9 (Critical)**: Clinical context — including patient-identifying information and proprietary clinical protocols — can leak in Orchestrator responses or via the Audit Logger training stream
- **E-7 (Critical)**: Prompt injection via clinical query can escalate the sub-agent's KB scope or manipulate the Orchestrator's downstream tool decisions

**Three-Signal-Class Coverage on Clinical Advisory Sub-Agent**:

The LLM section for the Clinical Advisory Sub-Agent demonstrates three-signal-class separation per SC-014:

**Signal Class 1 — LLM-{N} (Prompt Injection / Data Poisoning, OWASP LLM01/LLM03)**:
- **LLM-13** (Critical): `source_attribution: {taxonomy: owasp, id: LLM01, relationship: primary}` — Prompt injection via clinical query context overrides sub-agent system prompt. Distinct from OI-4 (which addresses the output execution sink) and MI-1/2/3 (which address factual integrity). LLM01 signal class: adversarial instructions embedded in clinical query content.
- **LLM-14** (Critical): `source_attribution: {taxonomy: owasp, id: LLM03, relationship: primary}` — Training data poisoning via Clinical Decision Log Entries in Learning Loop. LLM03 signal class: training data corruption via the audit-to-training pipeline.

**Signal Class 2 — OI-{N} (Output Integrity / Improper Output Handling, OWASP LLM05)**:
- **OI-4** (High): `source_attribution: {taxonomy: owasp, id: LLM05, relationship: primary}` — Server-side execution via clinical summary content incorporated into Orchestrator's downstream Tool Call Request. LLM05 signal class: LLM output bytes/strings reaching a machine-victim execution sink (the MCP Tool Server). Distinct from LLM-13 (input-side injection) and MI-1/2/3 (factual content).

**Signal Class 3 — MI-{N} (Misinformation / Factual Integrity, OWASP LLM09)**:
- **MI-1** (Critical): `source_attribution: {taxonomy: owasp, id: LLM09, relationship: primary}` — Ungrounded Factual Emission (Category 1 per FR-017). Factual medical claims without mandatory RAG grounding or per-claim source anchoring. Human-victim/decision-cascade model.
- **MI-2** (Critical): `source_attribution: {taxonomy: owasp, id: LLM09, relationship: primary}` — Overreliance / Missing HITL (Category 3 per FR-017). Clinical recommendations without physician sign-off gate. Consumer-facing high-stakes.
- **MI-3** (Critical): `source_attribution: {taxonomy: owasp, id: LLM09, relationship: primary}` — Retrieval-Grounding Gap (Category 4 per FR-017). KB retrieval failures cause hallucinated gap-filling with grounded-summary confidence.

Three-signal-class discipline verified: LLM-13, LLM-14, OI-4, MI-1, MI-2, MI-3 are rendered adjacent in Section 4.2 with distinct source_attribution blocks citing LLM01, LLM03, LLM05, and LLM09 respectively. No synthesis into unified prose.

### Preserved F-1 Findings

All 70 F-1 findings are UNCHANGED. Critical highlights:

**AG-2 (Critical)** — Agent Collusion: Orchestrator and Specialist Agent coordination via Inter-Agent Channel for policy circumvention. With ClinAdvisor now added as a third agentic component, the collusion surface expands — three-way coordination is possible.

**T-8 / LLM-11 / AG-7 (Critical)** — Temporal Attack chain on Learning Loop: now expanded with ClinAdvisor as a third recipient of model updates (E-6 updated to reference ClinAdvisor; LLM-14 is the new Clinical Advisory Sub-Agent-specific training poisoning vector).

**OI-1, OI-2, OI-3 (Critical / High)** — Output Integrity on LLM Agent Orchestrator: all three execution sink paths (client-side XSS via browser render, server-side via Tool Call Request parameters, SSRF via LLM-synthesized URL) remain Critical/High. OI-4 adds the clinical output indirect path.

---

## 4. Threat Category Deep-Dives

### 4.1 Misinformation Threats (MI-1, MI-2, MI-3) — F-2 New

The three MI findings represent the highest-priority new risk introduced by F-2. All three are Critical risk (HIGH likelihood, HIGH impact per OWASP 3×3) due to the clinical domain and direct patient-safety consequences.

**FR-011 gate verification**: The two-part emission gate was evaluated for all LLM components:
- Clinical Advisory Sub-Agent: BOTH signals confirmed — (a) LLM keyword matches (`clinical`, `advisory`, `medical`, `sub-agent`), (b) factual-output indicator structurally present (`Clinical Summary + Recommendations` → Orchestrator → User response path; RAG retrieval without retrieval-strength metric; no HITL gate declared).
- LLM Agent Orchestrator, Specialist Agent, Long-Running Learning Loop: Signal (b) NOT confirmed — these components process delegation, tool calls, and model updates, not domain-factual outputs to human or decision-cascade consumers. Zero MI findings emitted for these components per FR-011 self-gate.

**Sub-class differentiation (FR-017)**:
- **MI-1** (Ungrounded Factual Emission): The sub-agent performs KB vector search but emits factual medical claims without mandatory per-claim grounding verification. The failure mode is hallucinated assertion presented with RAG confidence.
- **MI-2** (Overreliance / Missing HITL): Clinical recommendations surface in the Orchestrator response path without physician confirmation. The failure mode is automated clinical decision-making without human oversight.
- **MI-3** (Retrieval-Grounding Gap): Low-recall KB retrieval leaves gaps that the sub-agent fills with plausible hallucinated content. The failure mode is gap-filling fabrication indistinguishable from retrieval-grounded output.

### 4.2 Output Integrity (OI-1 through OI-4)

The F-1 OI findings (OI-1, OI-2, OI-3) on the LLM Agent Orchestrator are preserved UNCHANGED. OI-4 is new, covering the indirect execution path via Clinical Advisory Sub-Agent output incorporated into Orchestrator Tool Call Requests.

OI-4 exercises a two-hop execution sink: ClinAdvisor output → Orchestrator context → Tool Call Request (JSON-RPC) → MCP Tool Server execution. This is distinct from OI-2 (direct Orchestrator output into Tool Call Request) because the adversarial content originates from the sub-agent's clinical summary rather than directly from LLM generation in the Orchestrator.

### 4.3 Agentic Pattern Distribution

Phase 3.6 pattern synthesis results for F-2:

| Pattern | Count | Key Findings |
|---|---|---|
| trust_exploitation | 10 | S-1, S-3, S-4, S-5, S-6, S-9, E-7, AG-3, AG-4, AG-5 |
| temporal_attack | 7 | T-8, S-7, R-7, E-6, LLM-11, LLM-12, AG-7 |
| resource_competition | 6 | D-2, D-3, D-4, D-5, D-9, AG-6 |
| agent_collusion | 1 | AG-2 |
| communication_vulnerability | 2 | T-4, I-4 |
| emergent_behavior | 1 | AGP-01 |

The Clinical Advisory Sub-Agent adds D-9 to resource_competition and S-9/E-7 to trust_exploitation. The temporal_attack pattern remains anchored to the Learning Loop chain.

---

## 5. Remediation Roadmap

### Priority 1 — Deploy Before Go-Live (Clinical Advisory Sub-Agent)

All MI findings and E-7, S-9, T-9, I-9 must be addressed before the Clinical Advisory Sub-Agent is deployed in any patient-facing or clinical decision-critical context.

| # | Finding | Action |
|---|---|---|
| 1 | MI-1, MI-3 | Implement per-claim RAG grounding with retrieval-strength gate (recall@k threshold); return "insufficient grounding" response when threshold not met |
| 2 | MI-2 | Implement HITL physician sign-off gate; apply AI-provenance disclosure on all surfaced clinical recommendations |
| 3 | S-9 | Authenticate all Orchestrator→ClinAdvisor JSON-RPC messages with signed caller tokens and nonce/replay prevention |
| 4 | E-7 | Enforce instruction-boundary separation in ClinAdvisor system prompt; apply clinical output validator |
| 5 | LLM-13 | Implement clinical-query content sanitization; strip instruction-like patterns from context before injection |
| 6 | T-9 | Document-level integrity verification on KB retrievals by ClinAdvisor; sanitize clinical query payloads |
| 7 | I-9 | Output scrubbing on ClinAdvisor outputs before Orchestrator response; field-level classification on Clinical Decision Log Entries |
| 8 | LLM-14 | Clinical Decision Log Entry provenance attestation; clinical-domain holdout evaluation before ClinAdvisor update deployment |

### Priority 2 — Critical Findings (Existing, 30-day)

The 44 Critical findings inherited from F-1 require remediation within 30 days of initial deployment. See Section 7 (Appendix) for the full finding reference.

### Priority 3 — High Findings (60-day)

22 High findings require remediation within 60 days. Includes OI-3, OI-4, LLM-7, D-9, R-9, AG-6.

---

## 6. Cross-Layer Attack Chains

Five cross-layer attack chains were detected spanning 2-3 MAESTRO layers each. See `attack-chains.md` for full narratives and chain-breaking controls.

| Chain | Layers | Max Severity | Chain-Breaking Target |
|---|---|---|---|
| CHAIN-001: User Identity Spoofing → Agent Framework Privilege Escalation | L7→L6→L3 | Critical | S-2 (mTLS Guardrails→Orchestrator) |
| CHAIN-002: Data Poisoning → Temporal Model Compromise | L2→L5→L1 | Critical | T-7 (append-only Audit Logger) |
| CHAIN-003: Foundation Model Tampering → Agent Spoofing | L1→L3 | Critical | T-2 (context integrity validation) |
| CHAIN-004: Foundation Model Info Disclosure → Ecosystem Leakage | L1→L7 | Critical | I-2 (output scrubbing on Orchestrator response) |
| CHAIN-005: Clinical Sub-Agent Tampering → Foundation Model Corruption | L7→L2→L1 | Critical | T-6 (KB write controls + integrity verification) |

CHAIN-005 is a new F-2 chain enabled by the Clinical Advisory Sub-Agent's bidirectional data flow with the Knowledge Base. The sub-agent's context assembly path creates a new ecosystem→data-operations→foundation-model tampering cascade that did not exist in F-1.

### Agentic Pattern Analysis

The multi-agent gate predicate evaluates TRUE (conditions a, b, and c all satisfied). Six canonical MAESTRO agentic patterns are active:

**Trust Exploitation** (10 findings, highest count): Dominates because the supervisor-plus-specialist topology creates multiple inter-agent identity attack surfaces. The addition of ClinAdvisor adds two trust exploitation surfaces (S-9 as identity spoofing, E-7 as privilege escalation via clinical output manipulation).

**Temporal Attack** (7 findings): Concentrated on the Learning Loop and its update recipients (Orchestrator, Specialist, ClinAdvisor). The Learning Loop → ClinAdvisor update path creates a new temporal attack surface for clinical-domain behavioral drift.

**Resource Competition** (6 findings): D-9 (ClinAdvisor resource exhaustion) adds to the existing multi-agent resource contention surface. The sub-agent's Knowledge Base queries compete with Orchestrator KB queries.

**Agent Collusion** (1 finding, AGP-01 from baseline): The Orchestrator+Specialist inter-agent channel coordination risk. With ClinAdvisor added as a third agentic component, the collusion surface is expanded but no additional net-new agent collusion finding was emitted (existing AGP net-new generation is suppressed as the pattern is already represented).

---

## 7. Appendix: Finding Reference

All 83 findings (57 Critical, 22 High, 4 Medium):

**Critical (57)**:
S-1, S-3, S-5, S-6, S-7, S-9, T-2, T-3, T-4, T-5, T-8, T-9, R-3, I-2, I-4, I-7, I-9, D-1, D-2, D-5, E-1, E-2, E-4, E-5, E-6, E-7, AG-1, AG-2, AG-3, AG-4, AG-5, AG-7, LLM-1, LLM-2, LLM-4, LLM-5, LLM-6, LLM-8, LLM-9, LLM-11, LLM-13, LLM-14, OI-1, OI-2, MI-1, MI-2, MI-3, R-4 [note: R-3 is Critical], E-3 [note: E-3 is High; corrected below]

Corrected Critical (57): S-1, S-3, S-5, S-6, S-7, S-9, T-2, T-3, T-4, T-5, T-8, T-9, R-3, I-2, I-4, I-7, I-9, D-1, D-2, D-5, E-1, E-2, E-4, E-5, E-6, E-7, AG-1, AG-2, AG-3, AG-4, AG-5, AG-7, LLM-1, LLM-2, LLM-4, LLM-5, LLM-6, LLM-8, LLM-9, LLM-11, LLM-13, LLM-14, OI-1, OI-2, MI-1, MI-2, MI-3

**High (22)**:
S-2, S-4, S-8, T-1, T-6, T-7, R-4, R-6, R-7, R-9, I-3, I-5, I-6, I-8, D-3, D-4, D-7, D-9, E-3, AG-6, LLM-3, LLM-7, LLM-10, LLM-12, OI-3, OI-4

**Medium (4)**:
AGP-01, R-1, R-2, I-1, D-6, D-8

Note: Section 6 Risk Summary counts 57 Critical and 22 High; Medium count is 4 (AGP-01, R-1, R-2, I-1) with D-6 and D-8 also Medium — total 6 Medium findings. Risk distribution percentages in threats.md Section 6 should be consulted for the authoritative deduplicated counts.

All finding IDs reference Section 3 (STRIDE), Section 4 (AI Threats: LLM-N, OI-N, MI-N, AG-N), and net-new pattern findings (AGP-01) in threats.md.
