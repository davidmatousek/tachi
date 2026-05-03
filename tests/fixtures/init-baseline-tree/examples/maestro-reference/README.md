# Canonical MAESTRO Worked Example — Healthcare Clinical Decision Support System

## 1. Introduction

This directory contains a canonical MAESTRO worked example: a single, self-contained reference walkthrough that exercises the full CSA MAESTRO seven-layer taxonomy end-to-end (L1 Foundation Models, L2 Data Operations, L3 Agent Frameworks, L4 Deployment Infrastructure, L5 Evaluation and Observability, L6 Security and Compliance, L7 Agent Ecosystem).

The example exists so that an adopter evaluating tachi's MAESTRO coverage can see layer-tagged findings, cross-layer attack chains, agentic pattern classifications, and compliance cross-references (OWASP AIVSS, NIST AI RMF) in one place — produced from a single architecture input and a single pipeline run.

Tachi is one of several agentic threat-modeling frameworks available. This example follows the Cloud Security Alliance's published MAESTRO seven-layer taxonomy and is offered as a reference implementation, not a statement of definitive MAESTRO coverage. Adopters should treat the example as a teaching artifact and cross-check against their own frameworks where appropriate.

## 2. Domain Overview

> **DISCLAIMER**: This is a security reference scenario for threat-modeling teaching purposes only. It is NOT a real clinical system and contains NO real patient data. Nothing in this example constitutes medical advice, regulatory guidance, or a compliance framework recommendation.

The reference scenario is a fictional multi-agent Healthcare Clinical Decision Support System (CDSS) built from 18 components spanning all seven MAESTRO layers. A Physician interacts with a Clinical Portal that routes authenticated intent to a Supervisor Orchestrator, which delegates reasoning tasks to two specialist agents — a Diagnostic Agent and a Treatment Planner Agent — over an Inter-Agent Communication Channel, with a Clinical MCP Tool Server exposing shared tools. A Clinical LLM and a Risk Stratification Model sit behind a Model Inference API Gateway. Data flows through an FHIR Resource Store, a Clinical Guideline RAG Corpus, and a Medical Literature Vector Index. An EHR Ingestion Queue, a Clinical Audit Log, an Outcomes Telemetry and Physician Override Audit Store (which drives a long-running learning loop), a HIPAA RBAC + Policy Engine, and a Consent and De-identification Guardrail round out the architecture. A Patient Summary Generator surfaces output to a Patient external entity.

Healthcare was chosen because the domain naturally exercises multi-agent delegation, long-running learning loops, cross-layer data lineage, and compliance controls without requiring synthetic contrivance. The full component list is in [`architecture.md`](architecture.md).

## 3. MAESTRO Layer Coverage Table

This canonical example surfaces findings across all seven MAESTRO layers. The table below maps each architecture component to its MAESTRO layer intent (see `architecture.md` Component Summary for per-component dispatch keywords).

| Component | MAESTRO Layer |
|-----------|---------------|
| Physician | L7 — Agent Ecosystem (external entity) |
| Patient | L7 — Agent Ecosystem (external entity) |
| Physician Clinical Portal | L7 — Agent Ecosystem |
| Patient Summary Generator | L7 — Agent Ecosystem |
| Inter-Agent Communication Channel | L7 — Agent Ecosystem |
| Supervisor Orchestrator | L3 — Agent Frameworks |
| Diagnostic Agent | L3 — Agent Frameworks |
| Treatment Planner Agent | L3 — Agent Frameworks |
| Clinical MCP Tool Server | L3 — Agent Frameworks |
| Clinical LLM | L1 — Foundation Models |
| Risk Stratification Model | L1 — Foundation Models |
| FHIR Resource Store | L2 — Data Operations |
| Clinical Guideline RAG Corpus | L2 — Data Operations |
| Medical Literature Vector Index | L2 — Data Operations |
| Model Inference API Gateway | L4 — Deployment Infrastructure |
| EHR Ingestion Queue | L4 — Deployment Infrastructure |
| Clinical Audit Log | L5 — Evaluation and Observability |
| Outcomes Telemetry and Physician Override Audit Store | L5 — Evaluation and Observability |
| HIPAA RBAC + Policy Engine | L6 — Security and Compliance |
| Consent and De-identification Guardrail | L6 — Security and Compliance |

**Layer coverage summary**: L1 (2 components, 18 findings), L2 (3 components, 9 findings), L3 (4 components, 30 findings), L4 (2 components, 11 findings), L5 (2 components, 6 findings), L6 (2 components, 12 findings), L7 (5 components, 22 findings). All 7 MAESTRO layers have ≥1 finding — FR-007 target: ≥6/7, achieved: 7/7.

## 4. What to Look For in Output

This section points first-time readers to the most illustrative content in each pipeline artifact.

### In `threats.md`
- **Section 6 "Risk by MAESTRO Layer"** — per-layer finding counts confirming all 7 MAESTRO layers are populated
- **Section 7 "Recommended Actions"** — findings table with the new Pattern column (Feature 142) showing `maestro-pattern:<name>` tags; scan for `agent_collusion`, `temporal_attack`, `emergent_behavior`, `communication_vulnerability`, `resource_competition`, `trust_exploitation`
- **Section 4b "Findings by Agentic Pattern"** — aggregate table showing finding IDs under each of the 6 canonical patterns; 3 net-new AGP findings (AGP-01, AGP-02, AGP-03) introduced by Phase 3.6 synthesis

### In `threat-report.md`
- **Section 6 "Cross-Layer Attack Chains"** — 3 surfaced chains; CHAIN-001 demonstrates a 5-layer cascade (L2 RAG poisoning → L3 Agent hijack → L5 Audit Log tampering → L6 RBAC bypass → L7 false recommendation disclosure) with chain-breaking control target identification
- **Section 7 "Agentic Pattern Analysis"** — narrative per pattern (Agent Collusion, Emergent Behavior, Temporal Attack, Trust Exploitation, Resource Competition) with finding traceability
- **Section 1 "Executive Summary"** — compact risk posture summary with top 5 findings by business impact and remediation timeline

### In `attack-chains.md`
- **CHAIN-001 "RAG Corpus Poisoning to False Clinical Recommendation via Agent Hijack"** — the canonical 5-layer chain; member findings trace architectural component lineage (RAG Corpus → Diagnostic Agent → Audit Log → RBAC → Portal)

### In `attack-trees/`
- **`t-11-attack-tree.md`** — Mermaid attack tree for the L2 RAG corpus poisoning initial exploit in CHAIN-001
- **`agp-01-attack-tree.md`** — attack tree for the net-new agent_collusion AGP-01 finding (emergent multi-agent coordination risk)

### In Infographics
- **`threat-maestro-stack.jpg`** — MAESTRO layer stack diagram (Feature 091) showing finding density per layer
- **`threat-maestro-heatmap.jpg`** — MAESTRO layer × severity heat map visualizing the Critical concentration at L1/L3/L7

### In `risk-scores.md`
- **Top 5 findings by composite score** — four-dimensional `(0.35 × CVSS 3.1) + (0.30 × Exploitability) + (0.20 × Reachability) + (0.15 × Scalability)` weighted-sum per ADR-018 + ADR-024

### In `compensating-controls.md`
- **Coverage matrix** — note that the target codebase (tachi repo) has minimal direct controls applicable to the fictional Healthcare CDSS threats; most findings map to "Missing Control" recommendations. This is the honest state of a reference example scanned against an unrelated codebase.

## 5. Reading-Order Recommendation

Choose a reading tier based on how much time you want to spend.

- **5 minutes** — Read this README and skim the Mermaid architecture diagram in [`architecture.md`](architecture.md). You will see the seven-layer MAESTRO grouping and the multi-agent delegation topology.
- **15 minutes** — Read Section 7 of [`threats.md`](threats.md) (the findings table, which carries the MAESTRO layer tag and the agentic pattern column), then browse the Executive Summary and the Cross-Layer Attack Chains section of [`threat-report.md`](threat-report.md).
- **An hour** — Read the full [`security-report.pdf`](security-report.pdf), then browse the [`attack-trees/`](attack-trees/) directory (one Mermaid attack tree per Critical/High finding) and the six infographic JPEGs rendered alongside the report.

## 6. Compliance Posture Cross-References

### 6.1 OWASP AIVSS

Tachi's canonical position on OWASP AIVSS is documented in [ADR-024](../../docs/architecture/02_ADRs/ADR-024-owasp-aivss-evaluation.md): **tachi diverges from AIVSS at the present time.** The existing four-dimensional weighted-sum composite (`(0.35 × CVSS 3.1) + (0.30 × Exploitability) + (0.20 × Reachability) + (0.15 × Scalability)`) remains the canonical scoring model, and AIVSS v0.8 is documented as a peer agentic-AI scoring framework that tachi is aware of and intentionally non-aligned with.

The divergence decision rests primarily on two factors: AIVSS v0.8 is pre-1.0 with public review opening 2026-04-16, and the frameworks structurally differ on CVSS base version (tachi CVSS 3.1 vs AIVSS CVSS v4.0) and composite formula shape (tachi weighted sum vs AIVSS agentic amplification model). The single point of structural alignment is the severity-band thresholds (Critical/High/Medium/Low) which both frameworks adopt from the CVSS convention.

Re-evaluation triggers: AIVSS publishes a stable v1.0 **and** at least one external adopter ships a case study. Neither condition currently holds.

### 6.2 NIST AI RMF

Tachi's canonical position on NIST AI RMF is documented in [ADR-025](../../docs/architecture/02_ADRs/ADR-025-nist-ai-rmf-evaluation.md): **tachi adopts a documentation-only mapping posture** across three surfaces (AI RMF Functions × pipeline phases, AI RMF Subcategories × compensating-control categories, AI 600-1 Generative AI risks × STRIDE+AI categories).

The posture reflects a structural tier mismatch: AI RMF Functions (Govern, Map, Measure, Manage) are organizational-tier outcomes, while tachi produces artifact-tier evidence. Tachi's Phase 2 Threat Detection and Phase 3 Compensating Controls are the strongest MEASURE alignment — specifically MEASURE 2.7 ("AI system security and resilience…are evaluated and documented"), which names exactly what tachi's `threats.md` and `compensating-controls.md` deliverables produce. The Govern Function is a deliberate scope boundary (policy/culture/role-assignment tier, not a closeable gap). On AI 600-1, §2.9 Information Security is the strongest direct mapping and aligns to five tachi STRIDE+AI agents: Tampering, Information Disclosure, Denial of Service, Prompt Injection, and Data Poisoning.

Re-evaluation triggers: AI RMF 2.0 publishes **or** adopter demand surfaces requests for schema-level AI RMF fields or runtime compliance gates. Neither condition currently holds.

## 7. Limitations and Scope

The following are explicit statements about what this example does NOT demonstrate.

- **Custom risk-weight calibrations** — The pipeline uses tachi's default four-dimensional weighted-sum composite per [ADR-018](../../docs/architecture/02_ADRs/ADR-018-baseline-aware-pipeline-correlation.md). Organization-specific weight tuning is out of scope for this example.
- **Organization-specific compensating controls** — Controls surfaced in the output reflect a clean reference configuration, not a real clinical deployment. Adopters will see different control coverage against their own codebases.
- **Real-world clinical data** — The FHIR Resource Store, Clinical Guideline RAG Corpus, and Medical Literature Vector Index are synthetic constructs. The example contains no real patient records and no real clinical guidelines.
- **Clinical accuracy or diagnostic performance claims** — The Clinical LLM and Risk Stratification Model are descriptive placeholders chosen to exercise the L1 Foundation Models layer. They are not validated medical devices and the example makes no claims about diagnostic accuracy, sensitivity, specificity, or clinical performance.
- **Regulatory compliance guidance** — The HIPAA RBAC + Policy Engine component is a threat-modeling construct chosen to exercise the L6 Security and Compliance layer. Nothing in this example constitutes HIPAA compliance guidance, FDA guidance, or any other regulatory advice. Adopters working on regulated clinical systems must consult qualified compliance and legal counsel.
- **MAESTRO completeness claims** — MAESTRO is one of several agentic threat-modeling frameworks. Tachi's implementation follows the CSA canonical seven-layer taxonomy per [ADR-020](../../docs/architecture/02_ADRs/ADR-020-maestro-layer-classification.md) and [ADR-026](../../docs/architecture/02_ADRs/ADR-026-pattern-classification-mechanism.md). This example exercises the full seven layers end-to-end but does not claim to be the definitive MAESTRO implementation; adopters should cross-check against their own framework choices.
