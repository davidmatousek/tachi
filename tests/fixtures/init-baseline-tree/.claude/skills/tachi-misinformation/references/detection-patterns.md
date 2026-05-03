---
name: misinformation-detection-patterns
description: "Pattern catalog for OWASP LLM09:2025 misinformation detection — factual-integrity signal class (grounding, verification, HITL, calibration)."
consumers: [misinformation]
schema_version: "1.7"
---

# Misinformation Detection Patterns

## Overview

Detection vocabulary for OWASP LLM09:2025 Misinformation. Loaded at detection start by the `misinformation` agent via a single `**MANDATORY**: Read` directive. Scope is the **factual-integrity signal class** — grounding, verification, human-in-the-loop (HITL), and calibration primitives on LLM Process output that emits factual content to human consumers or decision-cascade consumers. This is the third and final LLM-tier signal class under the Heuristic A taxonomy formalized in ADR-031: not input-side (that is `prompt-injection` — attacker-controlled input primitives, machine-attacker), not output-side execution-sink sanitization (that is `output-integrity` per ADR-030 Decision 1 — machine-victim, bytes/strings/syntax primitives), but factual-integrity (human-victim and decision-cascade-victim, factual-content primitives).

The catalog covers five pattern categories: Ungrounded Factual Emission, Citation Fabrication, Overreliance / Missing HITL on Decision-Critical Output, Retrieval-Grounding Gap, and Confidence-Calibration Absence. Per ADR-031 Decision 4, the catalog is bounded at five categories; the "Model-Specific Hallucination" and "Feedback-Loop Overreliance" candidates are deferred to catalog-enrichment follow-on features (F-2.1 or F-3/F-6 scope) because (a) the model-specific candidate couples to model-family taxonomies that age poorly and (b) the feedback-loop candidate overlaps with F-3 ASI07 inter-agent-communication scope. Per FR-017, the five categories align with the three OWASP LLM09:2025 sub-classes (factual-emission, citation-integrity, decision-overreliance) plus two architectural-grounding sub-classes (retrieval-grounding, calibration) that complete the LLM09 surface.

**Prose-only citations** (per PRD FR-5 F-A1 catalog-absent status, referenced in pattern Primary Sources but NOT in emitted `source_attribution` arrays): `MITRE ATLAS AML.T0042 Verify Attack` (adversarial-grounding context — confirmed absent from `schemas/taxonomy/mitre-atlas.yaml`); `NIST AI 600-1 §2.4 Hallucination` (section-level IDs not populated in the curated NIST catalog). These remain semantic peers of OWASP LLM09:2025 for adopter situational awareness without triggering F-A2 referential-integrity validator rejection on emitted findings.

## Detection Scope

### Trigger Keywords

This agent activates when a DFD Process component's name or description matches any of the following keywords (case-insensitive) AND the agent can structurally identify a factual-output indicator on the same component or its connected Data Flows (two-part emission gate per FR-011 — see below):

1. `factual output`
2. `citation generation`
3. `recommendation engine`
4. `decision support`
5. `RAG` (**word-boundary match required** — use regex `\bRAG\b` to avoid substring collision with `storage`; confirmed during T012 dispatch FP dry-run that case-insensitive substring matching falsely triggers on every `storage` Data Store description across baselines. The word-boundary constraint preserves dispatch efficiency without affecting correctness because the FR-011 two-part emission gate already self-gates stylistic false positives.)
6. `grounding`
7. `hallucination`
8. `advisory`
9. `medical`
10. `legal`
11. `financial`
12. `clinical`

**Two-part emission gate (FR-011)**: Keyword match alone does NOT emit a finding. The agent MUST also identify at least one **factual-output indicator** — a structural signal that the LLM Process emits factual content to a human consumer or a decision-cascade consumer. Indicators include: explicit prose stating the Process produces diagnoses, recommendations, citations, legal/medical/financial summaries, advisory output, or decision outputs; Data Flows from the Process into automated decision systems (approve/deny, triage/classify, content-moderation rulings); explicit RAG / retrieval / grounding declarations; high-stakes domain metadata (medical, legal, financial, clinical). Absent any factual-output indicator, the agent MUST emit zero findings for that component — dispatch still occurs, but emission self-gates to prevent false positives on LLM components whose output is purely stylistic (copy generation, translation, summarization of user-supplied text without factual-claim emission).

### Applicable DFD Element Types

- **Process**: Any Process node that invokes an LLM AND exhibits a factual-output indicator. This is the ONLY applicable DFD element type per Q3 PRD architect decision (`dfd_targets: [Process]` metadata), matching F-1 precedent. Rationale: misinformation is inherently about WHAT a Process EMITS, not about data-at-rest properties (Data Store), trust-boundary-crossing properties (Data Flow), or actor identity (External Entity). Data Store integrity, Data Flow tampering, and External Entity spoofing are already owned by the STRIDE tier (`tampering`, `info-disclosure`, `spoofing`). Data Flow targeting for RAG-ingest boundaries is deferred to a future catalog-enrichment feature if production feedback surfaces the need.

## Detection Patterns

### Category 1 — Ungrounded Factual Emission

An LLM Process emits factual claims (diagnoses, recommendations, summaries of external facts, comparative judgments) without a declared grounding mechanism — no RAG layer supplying retrieved source documents, no citation verification against a corpus, no per-claim source attribution. Claims are generated from parametric memory alone and therefore are susceptible to hallucination drift, stale knowledge, and domain-mismatch errors.

**Primary citation**: `{taxonomy: owasp, id: LLM09, relationship: primary}`
**Related citation**: `{taxonomy: cwe, id: CWE-345, relationship: related}` (Insufficient Verification of Data Authenticity)
**Prose-only peers**: `MITRE ATLAS AML.T0042 Verify Attack` (catalog-absent); `NIST AI 600-1 §2.4 Hallucination` (section IDs not catalogued)

**Trigger keywords**: `factual output`, `recommendation engine`, `decision support`, `grounding`, `hallucination`, `medical`, `legal`, `financial`, `clinical`

**Applicable DFD element types**: Process

**Indicators**:
- LLM Process description emits factual claims without naming an upstream retrieval or grounding component
- No RAG layer, vector store, or document retriever appears adjacent to the LLM Process in the DFD
- Absence of per-claim source attribution in output specification (output is free-text paragraphs, not citation-tagged claims)
- High-stakes domain context (medical, legal, financial, clinical) without a declared knowledge-base binding
- Output specification uses parametric-memory language ("the model produces a summary") rather than grounded-synthesis language ("the model synthesizes retrieved sources into a summary")

**Anti-indicators** (pattern does NOT apply):
- The LLM Process declares a RAG layer with per-claim source attribution AND a retrieval-strength metric (hit-rate, recall@k) gate
- The Process's output is purely stylistic (summarization of user-supplied text, translation, copy generation) with no factual-claim emission
- The architecture declares a confidence-calibration layer that emits refusal patterns on low-confidence factual queries

**Worked Example** (clearly-fictional per NFR-6):
- **Finding**: A hypothetical clinical-decision-support component named "ClinicalSummaryBot" (fictional scenario; no real institution) produces patient-facing clinical summaries referencing drug interactions, diagnostic possibilities, and treatment recommendations. The architecture description states the component "uses an LLM to produce summaries" but lists no retrieval layer, no clinical-knowledge-base binding, and no per-claim source attribution mechanism. The Process emits factual medical claims from parametric memory alone.
- **Mitigation**: Introduce a mandatory RAG grounding layer with per-claim source attribution — each emitted clinical claim MUST be traceable to a retrieved source document (EHR entry, clinical-guideline corpus, peer-reviewed publication). Declare a retrieval-strength metric gate (e.g., `hit_rate ≥ 0.85`) that blocks model output when retrieval recall drops below threshold. Layer a confidence-calibration mechanism (temperature scaling + Expected Calibration Error monitor) that injects refusal patterns on low-confidence clinical claims rather than synthesizing from parametric memory.

### Category 2 — Citation Fabrication

An LLM Process runs a RAG pipeline or declares grounding, but does NOT verify that emitted citations actually correspond to retrieved source URIs. The model is known to emit syntactically plausible but non-existent case citations, fabricated DOIs, invented study titles, or misattributed quotes — a decoder behavior orthogonal to retrieval quality. A retrieval layer without output-time citation verification is insufficient against the citation-fabrication sub-class of LLM09.

**Primary citation**: `{taxonomy: owasp, id: LLM09, relationship: primary}`
**Related citation**: `{taxonomy: cwe, id: CWE-345, relationship: related}` (Insufficient Verification of Data Authenticity)
**Prose-only peers**: `MITRE ATLAS AML.T0042 Verify Attack` (catalog-absent); `NIST AI 600-1 §2.4 Hallucination` (section IDs not catalogued)

**Trigger keywords**: `citation generation`, `RAG` (with word-boundary match), `grounding`, `legal`, `medical`, `advisory`

**Applicable DFD element types**: Process

**Indicators**:
- LLM Process emits citations (case law, statutes, medical studies, peer-reviewed references, DOIs, quoted passages) without declaring an output-time citation-verification step
- RAG pipeline exists but architecture does not describe constraining decoder output to the retrieved set
- Output specification treats citation tokens as free-form model output rather than as a constrained alphabet over the retrieval corpus
- No rejection pathway for outputs whose citations fail URI resolution or corpus membership checks
- Absence of a decoder-constraint mechanism (structured output, JSON schema, grammar-constrained decoding, citation allowlist)

**Anti-indicators** (pattern does NOT apply):
- The architecture declares output-time citation verification against retrieved source URIs with a rejection pathway for unverifiable citations
- The Process uses grammar-constrained or schema-constrained decoding that restricts citation tokens to the retrieved set
- Output specification binds citations to structured retrieval-result objects rather than emitting them as free-form text

**Worked Example** (clearly-fictional per NFR-6):
- **Finding**: A generic legal-research tool named "LegalBriefAgent" (fictional scenario; no real law firm or jurisdiction) runs a retrieval pipeline over a case-law corpus and emits research memos with inline case citations and statutory references. The architecture description states "the agent performs RAG over case law" but does not specify how citations are constrained to the retrieved set. The decoder emits plausible-looking citations ("Smith v. Jones, 412 F.3d 567 (9th Cir. 2019)"; fictional case) that are syntactically correct but absent from the retrieval result set — a citation-fabrication failure mode orthogonal to retrieval quality.
- **Mitigation**: Enforce output-time citation verification against retrieved source URIs — every citation token in emitted output MUST resolve to a member of the retrieval result set for the current query, or the output is rejected and regenerated. Apply a strict citation-token decoder constraint (grammar-constrained decoding that restricts the citation alphabet to retrieval-result IDs). For high-stakes legal output, layer a human-review gate on any memo whose citation count exceeds a threshold.

### Category 3 — Overreliance / Missing HITL on Decision-Critical Output

An LLM Process emits output that drives automated consequential decisions — approve/deny rulings, triage/classification decisions, content-moderation actions, medical-triage recommendations, financial-advisory recommendations — without a human-in-the-loop (HITL) review gate, risk-threshold-based escalation, or secondary-verification mechanism. Per OWASP LLM09:2025 overreliance sub-class and CWE-223 (Omission of Security-relevant Information), the absence of HITL on high-stakes decision flows omits a required mitigation against factual-integrity failures and undisclosed-AI provenance.

**Primary citation**: `{taxonomy: owasp, id: LLM09, relationship: primary}`
**Related citation (primary)**: `{taxonomy: cwe, id: CWE-223, relationship: related}` (Omission of Security-relevant Information)
**Related citation (optional)**: `{taxonomy: cwe, id: CWE-345, relationship: related}` when factual authenticity is also unverified on the decision pathway
**Prose-only peers**: `MITRE ATLAS AML.T0042 Verify Attack` (catalog-absent); `NIST AI 600-1 §2.4 Hallucination` (section IDs not catalogued)

**Trigger keywords**: `decision support`, `recommendation engine`, `advisory`, `medical`, `legal`, `financial`, `clinical`

**Applicable DFD element types**: Process

**Indicators**:
- LLM Process output drives an automated approve/deny, triage/classify, or content-moderation decision without a human-review gate
- No risk-threshold-based auto-escalation (e.g., decisions above a monetary, severity, or uncertainty threshold route to a human reviewer)
- Absence of AI-provenance disclosure on emitted decisions — downstream consumers do not know the decision is AI-generated
- No secondary-verification mechanism (dual-model ensemble, independent verification pass, deterministic rules check) on high-stakes output
- Consumer-facing high-stakes context (medical triage, loan approval, legal recommendation, clinical decision) without an explicit HITL workflow

**Anti-indicators** (pattern does NOT apply):
- Decisions are routed through a HITL review queue with a documented reviewer SLA
- The Process emits only advisory output (human is informed, human makes the decision) and the architecture explicitly states the AI is advisory-only, not authoritative
- Low-stakes internal-only context (e.g., internal note drafting, internal summarization) where the output has no downstream consequential effect

**Worked Example** (clearly-fictional per NFR-6):
- **Finding**: A synthetic financial-advisory component named "LoanDecisionAgent" (fictional scenario; no real lender, no real customer IDs) auto-approves or auto-denies loan applications based on LLM-generated creditworthiness summaries, without a HITL review gate on decisions above $10,000 and without AI-provenance disclosure on the decision notification sent to applicants. Per OWASP LLM09:2025 overreliance sub-class combined with CWE-223 Omission of Security-relevant Information, this presents both misinformation risk (LLM factual errors in the creditworthiness summary) and decision-integrity risk (no human reviewer validates high-stakes decisions).
- **Mitigation**: Introduce a human-in-the-loop review queue on decision-critical output with a risk-threshold-based auto-escalation rule (all decisions above $10,000 loan amount OR below a model-confidence threshold OR flagging regulatory-sensitive applicant categories MUST route to a human reviewer). Add AI-provenance disclosure on all emitted decisions — applicant notifications state the decision was AI-generated and provide a human-review appeal pathway. Optionally layer a secondary-verification dual-model ensemble gate that requires both models to agree on approvals above the threshold.

### Category 4 — Retrieval-Grounding Gap

An LLM Process declares RAG grounding but the architecture exhibits a citation-claim divergence — retrieved sources do not actually support the emitted claims. Gaps arise from shallow retrieval (hit-rate too low for the claim density), stale corpus (retrieval returns outdated sources not representing current facts), retrieval-answer mismatch (retrieved sources are topically related but do not contain the specific factual claims emitted), or absent retrieval-strength metrics (no hit-rate / recall@k / retrieval-score threshold declared).

**Primary citation**: `{taxonomy: owasp, id: LLM09, relationship: primary}`
**Related citation**: `{taxonomy: cwe, id: CWE-223, relationship: related}` (Omission of Security-relevant Information — the retrieval-strength metric is a security-relevant signal whose omission degrades grounding assurance)
**Prose-only peers**: `MITRE ATLAS AML.T0042 Verify Attack` (catalog-absent); `NIST AI 600-1 §2.4 Hallucination` (section IDs not catalogued)

**Trigger keywords**: `RAG` (with word-boundary match), `grounding`, `recommendation engine`, `factual output`, `medical`, `clinical`

**Applicable DFD element types**: Process

**Indicators**:
- RAG layer is declared but no retrieval-strength metric (hit-rate, recall@k, retrieval score) is exposed to the emission logic
- No per-query retrieval-score threshold gates model output — the Process synthesizes claims regardless of retrieval quality
- Retrieval corpus has no staleness policy (no refresh cadence, no version metadata, no freshness-threshold on retrieval)
- Claim-grounding divergence is not checked post-emission — outputs can assert facts the retrieved sources do not support
- Absence of a citation-claim alignment verification step between retrieval and decoder output

**Anti-indicators** (pattern does NOT apply):
- Architecture declares a retrieval-strength metric (hit-rate, recall@k) with a per-query threshold that blocks model output when retrieval quality drops below threshold
- Retrieval corpus has a documented staleness policy with version metadata and a refresh cadence
- Post-emission citation-claim alignment verification is declared (e.g., claim-level entailment check against retrieved passages)

**Worked Example** (clearly-fictional per NFR-6):
- **Finding**: A hypothetical clinical-knowledge assistant named "MedRefBot" (fictional scenario; no real hospital, no real patient IDs) declares a RAG pipeline over a medical-literature corpus last refreshed 18 months ago. The architecture description names RAG grounding but does not expose a retrieval-strength metric to the emission path and does not declare a corpus-staleness policy. For a query about a recently-approved medication, the retrieval returns topically-adjacent but pre-approval literature, and the model synthesizes a response asserting dosing guidance not present in the retrieved sources — a retrieval-grounding-gap failure mode where the RAG layer exists but does not guarantee citation-claim alignment.
- **Mitigation**: Declare a per-query retrieval-strength metric (hit-rate or recall@k) and a threshold that blocks model output when retrieval quality is insufficient — emit refusal rather than synthesize from inadequate retrieval. Version the retrieval corpus with explicit staleness metadata and a documented refresh cadence (e.g., medical literature refreshed quarterly). Add a post-emission claim-level entailment check verifying each emitted claim is supported by the retrieved source set; reject outputs whose claims fail entailment.

### Category 5 — Confidence-Calibration Absence

An LLM Process emits factual claims without uncertainty disclaimers, calibrated probability estimates, or refusal patterns on low-confidence queries. The model asserts every output with uniform confidence regardless of actual epistemic uncertainty, creating systematic overconfidence on out-of-distribution queries, parametric-memory gaps, and retrieval-sparse regions. Calibration absence is an architectural-hygiene gap that compounds the other four pattern categories — a well-calibrated model can refuse or disclaim rather than emit confidently-wrong output.

**Primary citation**: `{taxonomy: owasp, id: LLM09, relationship: primary}`
**Related citation**: `{taxonomy: cwe, id: CWE-223, relationship: related}` (Omission of Security-relevant Information — the confidence-calibration signal is a security-relevant signal whose omission obscures uncertainty)
**Prose-only peers**: `MITRE ATLAS AML.T0042 Verify Attack` (catalog-absent); `NIST AI 600-1 §2.4 Hallucination` (section IDs not catalogued)

**Trigger keywords**: `factual output`, `recommendation engine`, `decision support`, `hallucination`, `advisory`, `medical`, `legal`, `financial`, `clinical`

**Applicable DFD element types**: Process

**Indicators**:
- Output specification emits factual claims as flat assertions without calibrated-confidence annotations or uncertainty language
- No calibration layer declared (temperature scaling, Platt scaling, isotonic regression, or equivalent post-hoc calibration over raw model logits)
- No Expected Calibration Error (ECE) monitor or calibration-drift alerting on the Process
- Absence of a refusal pattern for low-confidence or out-of-distribution queries — the model synthesizes a response regardless of confidence
- Consumer-facing calibrated-confidence is not exposed on output (downstream consumers cannot distinguish high-confidence from low-confidence claims)

**Anti-indicators** (pattern does NOT apply):
- The Process declares a calibration layer (temperature scaling or equivalent) with an ECE monitor and calibration-drift alerting
- Low-confidence queries route to a documented refusal pattern rather than synthesizing a response
- Output specification exposes calibrated-confidence scores to downstream consumers alongside factual claims

**Worked Example** (clearly-fictional per NFR-6):
- **Finding**: A synthetic advisory component named "RegulatoryGuidanceAssistant" (fictional scenario; no real agency, no real regulatory citation) emits interpretations of regulatory text to compliance-officer consumers without any calibration layer, without an ECE monitor, and without a refusal pattern on ambiguous or out-of-distribution regulatory queries. The output is emitted as flat assertions ("Rule X requires Y action") regardless of the model's actual epistemic uncertainty. Compliance officers consuming the output cannot distinguish high-confidence regulatory interpretations from low-confidence extrapolations, leading to systematic overconfidence on edge-case queries.
- **Mitigation**: Introduce a calibration layer — post-hoc temperature scaling on output logits fitted on a held-out calibration set — combined with an Expected Calibration Error (ECE) monitor that alerts on calibration drift. Declare a refusal pattern for low-confidence queries: when model confidence falls below a documented threshold, the Process emits a refusal ("I cannot confidently interpret this query; please consult a human compliance officer") rather than synthesizing a response. Expose calibrated-confidence scores on all emitted claims so downstream consumers can weight output by uncertainty rather than treating every assertion as uniformly authoritative.

## Primary Sources

The pattern categories above cite the following primary and adjacent sources. Only catalog-resolvable citations appear in emitted `source_attribution` arrays per the F-A2 referential-integrity validator; catalog-absent citations appear in prose only.

**Catalog-resolvable (appear in `source_attribution`)**:
- **OWASP LLM09:2025 Misinformation** — present in `schemas/taxonomy/owasp.yaml`; primary citation on every emitted `MI-{N}` finding
- **CWE-345 Insufficient Verification of Data Authenticity** — present in `schemas/taxonomy/cwe.yaml`; related citation on categories 1, 2, 3 (optional), 4 (optional), 5 (optional)
- **CWE-223 Omission of Security-relevant Information** — present in `schemas/taxonomy/cwe.yaml`; related citation on categories 3, 4, 5

**Prose-only (NOT in `source_attribution`, referenced for adopter situational awareness)**:
- **MITRE ATLAS AML.T0042 Verify Attack** — confirmed absent from `schemas/taxonomy/mitre-atlas.yaml` at PRD time (catalog contains 12 AML techniques: T0010, T0018, T0020, T0024, T0051, T0054, T0057, T0058, T0059, T0060, T0061, T0062; T0042 not present). Upgrade pathway: if a future catalog-population feature adds T0042, this prose citation upgrades to a `source_attribution` entry as a separate additive change.
- **NIST AI 600-1 §2.4 Hallucination** — section-level IDs are not populated in `schemas/taxonomy/nist-ai-rmf.yaml` at PRD time. Upgrade pathway identical to AML.T0042.
