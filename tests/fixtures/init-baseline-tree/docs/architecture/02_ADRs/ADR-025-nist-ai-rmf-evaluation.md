# ADR-025: NIST AI RMF Evaluation and Tachi Alignment Posture

**Status**: Accepted
**Date**: 2026-04-16
**Deciders**: Architect, Product Manager, Team-Lead
**Feature**: 144 (MAESTRO Companion: NIST AI RMF)
**Related ADRs**: [ADR-024](ADR-024-owasp-aivss-evaluation.md) (companion AIVSS), [ADR-020](ADR-020-maestro-layer-classification.md) (MAESTRO classification), [ADR-019](ADR-019-shared-definitions-and-model-field-governance.md) (shared definitions), [ADR-018](ADR-018-baseline-aware-pipeline-correlation.md) (baseline lineage), [ADR-021](ADR-021-source-date-epoch-for-deterministic-pdf-comparison.md) (SOURCE_DATE_EPOCH determinism), [ADR-023](ADR-023-threat-agent-skill-references-pattern.md) (skill-references pattern)

---

## Context

The **NIST Artificial Intelligence Risk Management Framework** (AI RMF 1.0, NIST AI 100-1, January 2023) is the U.S. federal reference framework for managing risks in the design, development, deployment, evaluation, and acquisition of AI systems. The framework is published by the NIST Information Technology Laboratory and is canonical at [`https://www.nist.gov/itl/ai-risk-management-framework`](https://www.nist.gov/itl/ai-risk-management-framework) (PDF [`https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.100-1.pdf`](https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.100-1.pdf), DOI [`https://doi.org/10.6028/NIST.AI.100-1`](https://doi.org/10.6028/NIST.AI.100-1)). Its operational core is the **AI RMF Core**: four high-level **Functions** (Govern, Map, Measure, Manage) decomposed into **18 Categories** and **68 Subcategories** of organizational outcomes. AI RMF 1.0 remains current as of 2026-04-15 with no published 1.1 or 2.0 revision; NIST AI 100-1 §"Update Schedule and Versions" commits to a formal community-input review "no later than 2028."

The **NIST AI 600-1 Generative AI Profile** (July 2024, Editorial Review Board approval 2024-07-25; PDF [`https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.600-1.pdf`](https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.600-1.pdf), DOI [`https://doi.org/10.6028/NIST.AI.600-1`](https://doi.org/10.6028/NIST.AI.600-1)) is a companion profile to AI RMF 1.0 that enumerates **12 Generative AI risk categories** in §§2.1–2.12 (CBRN Information, Confabulation, Dangerous/Violent/Hateful Content, Data Privacy, Environmental Impacts, Harmful Bias or Homogenization, Human-AI Configuration, Information Integrity, Information Security, Intellectual Property, Obscene/Degrading/Abusive Content, Value Chain and Component Integration). §3 ("Suggested Actions to Manage GAI Risks") cross-walks these GAI risks back to AI RMF Subcategories, making AI 600-1 the natural surface for evaluating GAI-specific overlap with downstream security tooling.

Tachi ships a six-phase agentic-AI threat-modeling pipeline. **Phase 1 Scope** parses an architecture description and classifies the data-flow diagram. **Phase 2 Threat Detection** dispatches per-element STRIDE and AI threat agents covering **11 STRIDE+AI categories**: Spoofing (S), Tampering (T), Repudiation (R), Information Disclosure (I), Denial of Service (D), Elevation of Privilege (E), Prompt Injection, Data Poisoning, Model Theft, Agent Autonomy, and Tool Abuse. **Phase 3 Compensating Controls** runs a codebase analyzer that classifies coverage across **8 control categories**: authentication, input-validation, rate-limiting, encryption, logging-audit, csrf-protection, csp-security-headers, and access-control. **Phase 3.5 Cross-Layer Chains** (conditional, ADR-020 + Feature 141) correlates findings across MAESTRO layers. **Phase 4 Assessment** produces a coverage matrix, risk summary, and recommended actions. **Phase 5 Reporting** (default-on) emits the PDF security report and infographics. Pipeline outputs are `threats.md`, `threats.sarif`, `risk-scores.md`, `compensating-controls.md`, `attack-chains.md` (conditional), and the report bundle.

This ADR evaluates AI RMF + AI 600-1 against tachi's pipeline along three orthogonal surfaces — Functions × pipeline phases, Subcategories × control categories, and GAI risks × STRIDE+AI categories — and records the chosen posture. The evaluation explicitly differs from ADR-024 (OWASP AIVSS) reasoning: AIVSS v0.8 was pre-1.0 with no external adopters, which made maturity a blocker. AI RMF 1.0 is mature (3+ year stability runway through 2028), federally adopted in procurement workflows, and referenced in financial-services examinations and healthcare AI governance. **For ADR-025, maturity is a permission, not a blocker** — the decision is reasoned afresh from the Surface mapping density and the five evaluation criteria (per PRD 144 FR-4).

<a id="surface-a"></a>
### Surface A — NIST AI RMF Functions × tachi pipeline phases

The four AI RMF Functions are organizational outcomes. Tachi's pipeline phases produce artifact-tier outputs that contribute evidence to the Map, Measure, and Manage Functions. Govern is cross-cutting at organizational policy tier and has no direct artifact-tier overlap — tachi's pipeline does not produce policy, role assignments, or culture artifacts. Cells use exactly one of `Overlap`, `Gap`, `Conflict`, or `No equivalent`.

| NIST AI RMF Function | tachi Phase 1 Scope | tachi Phase 2 Threat Detection | tachi Phase 3 Compensating Controls | tachi Phase 3.5 Cross-Layer Chains | tachi Phase 4 Assessment | tachi Phase 5 Reporting | Relationship | Note |
|---|---|---|---|---|---|---|---|---|
| **Govern** | No equivalent | No equivalent | No equivalent | No equivalent | No equivalent | No equivalent | **Gap** | Govern is organizational/policy tier — culture, accountability structures, legal/regulatory compliance, third-party policies. Tachi produces no policy, role-assignment, or governance-process artifacts. The pipeline is a *measurement instrument* a Govern-tier program may consume; it is not itself a Govern output. |
| **Map** | Direct | Partial | (n/a) | (n/a) | (n/a) | (n/a) | **Overlap** | Phase 1 establishes context (architecture parse, DFD classification, trust-boundary identification) — directly aligns with MAP 1.1 (intended purposes documented), MAP 2.1 (tasks defined), MAP 4.2 (third-party AI components identified). Phase 2 threat detection contributes to MAP 5.1 (impacts characterized). |
| **Measure** | (n/a) | Direct | Direct | Direct | Partial | (n/a) | **Overlap** | Phase 2 threat detection (`threats.md`, `threats.sarif`) and Phase 3 control verification (`compensating-controls.md`) are the strongest one-to-one mapping in this surface — they produce exactly what MEASURE 2.7 names ("AI system security and resilience…are evaluated and documented"). Phase 3.5 chain correlation contributes to MEASURE 3.1 (risk tracking). |
| **Manage** | (n/a) | (n/a) | Partial | (n/a) | Direct | Partial | **Overlap** | Phase 4 assessment outputs (coverage matrix + risk summary + recommended actions) align with MANAGE 1.2 (risk treatment prioritized by impact/likelihood) and MANAGE 1.3 (responses developed/planned/documented). The compensating-controls deliverable also speaks to MANAGE 1.4 (negative residual risks documented). Phase 5 reporting communicates Manage outcomes. |

**Surface A density**: 3 Overlap, 1 Gap, 0 Conflict, 0 No equivalent. The Govern Gap is structural (tachi is artifact-tier, Govern is policy-tier) and is not closeable by re-engineering — it is a deliberate scope boundary.

<a id="surface-b"></a>
### Surface B — NIST AI RMF Subcategories × tachi compensating-control categories

Representative Subcategories drawn from research §6.2.d (the 16 sampled agentic-AI-relevant Subcategories) crossed with the 8 tachi compensating-control categories. Many-to-many mapping where a Subcategory naturally addresses multiple control surfaces. Cells use exactly one of `Overlap`, `Gap`, `Conflict`, or `No equivalent`.

| NIST Subcategory | tachi Control Category | Relationship | Note |
|---|---|---|---|
| **GOVERN 1.4** ("transparent policies, procedures, and other controls based on organizational risk priorities") | logging-audit | **Overlap** | Audit trail evidence is a transparency control — tachi's logging-audit category surfaces whether the codebase produces the auditable record that GOVERN 1.4 expects. |
| **GOVERN 1.6** ("Mechanisms are in place to inventory AI systems") | (n/a — no tachi control category) | **Gap** | Tachi's component DFD is an AI-system inventory artifact at the architecture-modeling tier, but no compensating-control category targets inventory mechanisms in the running codebase. |
| **MAP 1.1** ("Intended purposes…are understood and documented") | (n/a — no tachi control category) | **No equivalent** | MAP 1.1 is a documentation outcome, not a code-level control. Tachi addresses this in Phase 1 Scope (context parsing), not in Phase 3 Compensating Controls. |
| **MAP 4.2** ("Internal risk controls for components…including third-party AI technologies, are identified and documented") | authentication, access-control, input-validation, encryption | **Overlap** | Third-party risk controls map directly to tachi's per-component control coverage analysis. The four control categories named are the most common third-party-integration surfaces. |
| **MEASURE 2.6** ("AI system is evaluated regularly for safety risks…demonstrated to be safe…fail safely") | rate-limiting, input-validation | **Overlap** | Fail-safe behavior under adversarial input is a rate-limiting + input-validation outcome. Tachi's coverage analysis on these categories is the closest one-to-one. |
| **MEASURE 2.7** ("AI system security and resilience…are evaluated and documented") | authentication, input-validation, rate-limiting, encryption, logging-audit, csrf-protection, csp-security-headers, access-control | **Overlap** | **Strongest direct mapping in this surface** — MEASURE 2.7 names exactly what tachi's `compensating-controls.md` documents. All 8 control categories contribute evidence to this Subcategory. |
| **MEASURE 2.8** ("Risks associated with transparency and accountability…are examined and documented") | logging-audit | **Overlap** | Audit trail is the canonical transparency-and-accountability control. |
| **MEASURE 2.10** ("Privacy risk of the AI system…is examined and documented") | encryption, access-control, input-validation | **Overlap** | Privacy controls intersect tachi's encryption (data-at-rest / data-in-transit), access-control (who can read what), and input-validation (PII sanitization at ingress) categories. |
| **MANAGE 1.2** ("Treatment of documented AI risks is prioritized based on impact, likelihood, and available resources or methods") | (n/a — orthogonal pipeline surface) | **Gap** | Prioritization is the risk-scorer's job (per ADR-024 4-dimensional composite), not the compensating-controls analyzer's. The Subcategory is met by tachi, but by Phase 2/4 not Phase 3. |
| **MANAGE 1.3** ("Responses to the AI risks deemed high priority…are developed, planned, and documented") | authentication, input-validation, rate-limiting, encryption, logging-audit, csrf-protection, csp-security-headers, access-control | **Overlap** | The `compensating-controls.md` deliverable enumerates exactly the kind of response inventory MANAGE 1.3 expects. All 8 categories contribute. |
| **MANAGE 1.4** ("Negative residual risks…are documented") | (all 8 categories indirectly) | **Overlap** | Tachi's `residual-risk.md` output (per `tachi-control-analysis` SKILL) is the canonical residual-risk record. The 8 control categories contribute directly to its computation. |
| **MANAGE 2.4** ("Mechanisms are in place…to supersede, disengage, or deactivate AI systems") | (n/a — operational kill-switch posture) | **No equivalent** | Operational kill-switch / disengagement is outside tachi's threat-modeling and code-level control scope. |

**Surface B density**: 8 Overlap, 2 Gap, 0 Conflict, 2 No equivalent across 12 Subcategory-mapping rows. MEASURE 2.7 (security and resilience evaluation) is the single strongest semantic overlap — it is essentially what tachi's pipeline produces.

<a id="surface-c"></a>
### Surface C — NIST AI 600-1 Generative AI Profile risks × tachi STRIDE+AI categories

Each of the 12 GAI risks from NIST AI 600-1 §§2.1–2.12 mapped to its closest tachi STRIDE+AI category (or `No equivalent` if outside tachi's security-analysis scope). Cells use exactly one of `Overlap`, `Gap`, `Conflict`, or `No equivalent`.

| GAI Risk (NIST AI 600-1 §2) | tachi STRIDE+AI Category | Relationship | Note |
|---|---|---|---|
| **§2.1 CBRN Information or Capabilities** | (none) | **No equivalent** | Content-policy harm class outside tachi's security-analysis scope. Tachi does not evaluate model output policy violations. |
| **§2.2 Confabulation** | (none) | **No equivalent** | Hallucination / valid-but-wrong output is a model-behavior concern, not a security-control concern. Outside tachi's STRIDE+AI scope. |
| **§2.3 Dangerous, Violent, or Hateful Content** | (none) | **No equivalent** | Content-policy harm class outside tachi's security-analysis scope. |
| **§2.4 Data Privacy** | Information Disclosure (I) | **Overlap** | PII leakage / unauthorized disclosure / de-anonymization is exactly tachi-info-disclosure agent territory; encryption + access-control compensating controls address it directly. |
| **§2.5 Environmental Impacts** | (none) | **No equivalent** | Compute-resource and ecosystem impacts outside tachi's security-analysis scope. |
| **§2.6 Harmful Bias or Homogenization** | (none) | **Gap** | Bias amplification touches model-output fairness — tachi has no fairness-evaluation agent. Treated as a Gap (rather than No equivalent) because adopters may legitimately ask "does tachi cover this?" and the answer is "not yet." |
| **§2.7 Human-AI Configuration** | (none) | **No equivalent** | Anthropomorphization, automation bias, over-reliance — human-factors concerns outside tachi's threat-modeling scope. |
| **§2.8 Information Integrity** | (none) | **No equivalent** | Mis/disinformation campaign enablement — content-policy harm class outside tachi's scope. |
| **§2.9 Information Security** | Tampering (T), Information Disclosure (I), Denial of Service (D), Prompt Injection, Data Poisoning | **Overlap** | **Strongest direct mapping in this surface** — AI 600-1 §2.9 explicitly names "prompt injection," "data poisoning," "automated discovery and exploitation of vulnerabilities," "compromise of confidentiality or integrity of training data, code, or model weights." Five tachi STRIDE+AI agents map directly. |
| **§2.10 Intellectual Property** | Model Theft | **Overlap** | "Exposure of trade secrets" / "exposure of model weights" maps directly to tachi-model-theft (LLM agent). The IP-replication aspect (alleged copyright infringement) sits outside tachi's scope, but the trade-secret exposure aspect is in-scope. |
| **§2.11 Obscene, Degrading, and/or Abusive Content** | (none) | **No equivalent** | Content-policy harm class outside tachi's security-analysis scope. |
| **§2.12 Value Chain and Component Integration** | Tool Abuse, Tampering (T) | **Overlap** | Third-party / supply-chain risk; "untraceable integration of upstream third-party components" maps to tachi-tool-abuse (agentic AI agent) and to tachi-tampering for supply-chain integrity concerns. |

**Surface C density**: 4 Overlap, 1 Gap, 0 Conflict, 7 No equivalent across 12 GAI risks (58% No equivalent). 

**>50% No equivalent acknowledgment** (per spec Edge Case 4): 7 of 12 GAI risks (§§2.1, 2.2, 2.3, 2.5, 2.7, 2.8, 2.11) sit outside tachi's STRIDE+AI scope — these are content-policy, fairness, human-factors, and environmental harm classes that tachi has deliberately not modeled. This high-mismatch rate is itself an **input to the evaluation**: it confirms that AI 600-1 covers a broader harm space than tachi's security-focused pipeline. The 4 Overlap rows (§§2.4, 2.9, 2.10, 2.12) are the security-relevant subset where tachi adds direct value; the 7 No equivalent rows mark deliberate scope boundaries that adopters must know to fill via complementary tooling. This evidence is carried forward as a sixth de facto evaluation criterion in the Rationale section: *scope completeness on the security-relevant subset is high; scope completeness on the full GAI risk set is partial by design.*

---

## Decision

**Tachi will adopt a documentation-only mapping posture toward NIST AI RMF 1.0 and the NIST AI 600-1 Generative AI Profile.** No schema change, no new agent, no new pipeline phase, and no new template page. This ADR records the three-surface comparison above as the canonical alignment artifact, and a companion shared reference at [`.claude/skills/tachi-shared/references/nist-ai-rmf-mapping.md`](../../../.claude/skills/tachi-shared/references/nist-ai-rmf-mapping.md) ships the full Subcategory-to-control-category and GAI-risk-to-STRIDE+AI crosswalks for adopters who must cite NIST mappings during procurement, audit, or examination workflows. The [`tachi-control-analysis`](../../../.claude/skills/tachi-control-analysis/SKILL.md) skill gains a short cross-reference paragraph anchoring readers to this ADR.

The decision is **not** inherited from ADR-024's diverge-from-AIVSS logic. ADR-024 chose diverge because AIVSS v0.8 was pre-1.0 with no external adopters — maturity was the blocker. AI RMF 1.0 is the inverse: 3+ year stability runway through 2028, documented federal-procurement adoption, financial-services examination references, and healthcare-AI governance use. Maturity is a permission for adoption-class options; the binding constraint that selects documentation-only over wired integration is **structural fit**: AI RMF Functions are organizational-tier outcomes (Govern is policy/culture, Manage is treatment-decision allocation), while tachi produces artifact-tier evidence. The Surface A overlap cells (Map / Measure / Manage) describe what tachi already contributes evidence to, not new behaviors a wired integration would unlock. A schema field tagging compensating controls with NIST Subcategory IDs (Option B) would add labeling overhead without changing the evidence the pipeline produces; a dedicated NIST analyzer agent (Option C) would re-traverse architectural surfaces tachi already covers, producing a parallel report that re-states existing findings under NIST vocabulary. Documentation-only mapping captures the alignment surfaces explicitly, in a single discoverable artifact, without coupling tachi's stable pipeline to a framework that operates one tier above tachi's natural artifact level.

The mapping artifact is maintenance-bounded: it must be revised when NIST AI RMF publishes a new revision (1.1 / 2.0 / a new GAI Profile version), or when tachi adds a new compensating-control category or STRIDE+AI agent. The full re-evaluation triggers (and the case for upgrading to wired integration) are captured in *When to Re-Evaluate* below.

---

## Rationale

The recommendation rests on the five evaluation criteria established in PRD 144 (maturity, adoption, compatibility, effort, compliance value), reinforced by a de facto sixth criterion surfaced by the Surface C >50% `No equivalent` finding (scope-completeness asymmetry on the GAI risk set). The reasoning is **explicitly developed afresh from the Surface A/B/C mapping** per PRD 144 FR-4, not inherited from ADR-024's divergence logic.

### Five-Criteria Justification

| Criterion | Assessment | Weight in Decision |
|-----------|------------|--------------------|
| **NIST AI RMF Maturity** | AI RMF 1.0 (January 2023) has a 3+ year stability runway with next formal review committed "no later than 2028" per NIST AI 100-1 §"Update Schedule and Versions." AI 600-1 GAI Profile (July 2024) is the stable companion. No churn risk on the 12–18 month horizon relevant to this ADR. | **Permission, not blocker** — inverts the ADR-024 posture where AIVSS v0.8 pre-1.0 maturity was the decisive block |
| **Adoption in the Wild** | Federal procurement workflows cite AI RMF; financial-services supervisory letters reference it; healthcare-AI governance playbooks reference it. Peer signal is strong enough that an adopter citing "AI RMF coverage" during a procurement review expects a substantive answer, not a deflection. | **Heavy** — non-zero number of adopter interactions benefit from an explicit mapping surface |
| **Compatibility with Tachi** | Surface A: 3 Overlap + 1 Gap (Govern is policy-tier — structural, not closeable). Surface B: 8 Overlap + 2 Gap + 2 No equivalent across 12 Subcategory rows — MEASURE 2.7 names exactly what tachi's `compensating-controls.md` documents. Surface C: 4 Overlap + 1 Gap + 7 No equivalent across the 12 GAI risks (7 are content-policy, fairness, human-factors, or environmental harm classes outside tachi's security scope). The Overlap cells describe what tachi already contributes evidence to; they do not describe new pipeline behaviors a wired integration would unlock. | **Heavy** — high Overlap density on the security-relevant subset; structural Gap on Govern (policy-tier) and on the non-security GAI risks |
| **Effort to Wire In** | Option A (documentation-only): S — ~0 additional effort beyond this ADR and the mapping reference artifact. Option B (shallow wired, schema-additive): M — ~2–4 days for schema field + control-analyzer update + template update. Option C (deep wired, new agent + phase): L — ~6–10 days for new agent, new schema, new template page, new pipeline phase, example regeneration, determinism re-baseline. | **Moderate** — effort is well-characterized; the A→B→C gradient is monotonic in cost and in pipeline-coupling risk |
| **Compliance Value for Regulated Adopters** | **SOC 2**: AI RMF is not a SOC 2 criterion; the Common Criteria CC-series covers the security/availability surface tachi already serves. Mapping is informational for Type 2 auditors who cross-walk AI controls. **FedRAMP**: NIST SP 800-53 is canonical; AI RMF is cited as a companion risk-management framework in federal AI procurement contexts and in the Executive Order on Safe, Secure, and Trustworthy AI downstream guidance. **HIPAA**: AI RMF is referenced in HHS AI risk-management guidance as a compatible framework for covered entities deploying AI; not a Security Rule requirement. **FFIEC**: AI RMF is referenced in financial-services examination guidance (OCC/FDIC/Federal Reserve supervisory letters on AI/ML risk management). **EU AI Act**: not a direct mapping target (the EU AI Act operates on its own risk tiers + conformity assessment regime), but AI RMF is widely cited as a compatible risk-management backbone for pre-market and post-market monitoring obligations. | **Heavy** — five distinct regulatory surfaces benefit from an explicit, discoverable AI RMF mapping; none require tachi to *implement* AI RMF controls, all benefit from tachi *citing* AI RMF alignment |

The **de facto sixth criterion** (surfaced by Surface C): the 58% No equivalent rate on the 12 GAI risks is not a negative — it is evidence that AI 600-1 covers a broader harm space (content policy, fairness, environmental, human-factors) than tachi's security-focused pipeline, and that the 4 Overlap rows (§§2.4 Data Privacy, 2.9 Information Security, 2.10 Intellectual Property, 2.12 Value Chain) are precisely where tachi adds direct value. The asymmetry strengthens the documentation-only case: a wired integration would be forced to either stub the 7 non-security rows (producing misleading "coverage" artifacts) or drag tachi into content-policy, fairness, and environmental-impact analysis it has deliberately scoped out.

### Explicit Comparison to ADR-024 Reasoning

ADR-024 chose **diverge** from OWASP AIVSS. The reasoning was driven by maturity (AIVSS v0.8 pre-1.0 with no external adopters) and compatibility (CVSS 3.1→4.0 version conflict + formula-shape divergence). The ADR-024 decision is *not* the template for this ADR. Three pivots distinguish the ADR-025 reasoning:

1. **Maturity inverts**: AI RMF 1.0 is stable with multi-year runway; AIVSS v0.8 was pre-1.0. Maturity moves from blocker (ADR-024) to permission (ADR-025).
2. **Compatibility surface is structurally different**: ADR-024 found structural conflict on composite formula shape (weighted-sum vs amplification model) — a calculation conflict. ADR-025 finds structural fit at the artifact tier (high Overlap on Map/Measure/Manage) with a policy-tier Gap on Govern — an orthogonality, not a conflict.
3. **Compliance-value profile is richer**: ADR-024 compliance value was "report-vs-translate" on severity bands only. ADR-025 compliance value crosses five distinct regulatory surfaces (SOC 2, FedRAMP, HIPAA, FFIEC, EU AI Act), each with different citation expectations.

The net effect: ADR-024's divergence was driven by maturity + formula conflict. ADR-025's documentation-only posture is driven by structural fit at the artifact tier + richer compliance-value surface + zero implementation effort beyond documentation. **Different inputs, different reasoning, different posture** — though both ADRs land on "no wired integration at present."

---

## Alternatives Considered

### Option A: Documentation-only mapping

**Description**: This ADR ships the three-surface mapping as the canonical alignment artifact. A new companion shared reference at [`.claude/skills/tachi-shared/references/nist-ai-rmf-mapping.md`](../../../.claude/skills/tachi-shared/references/nist-ai-rmf-mapping.md) carries the full Subcategory-to-control-category and GAI-risk-to-STRIDE+AI crosswalks for adopters who must cite NIST mappings during procurement, audit, or examination workflows. The `tachi-control-analysis` SKILL gains a short cross-reference paragraph anchoring readers to this ADR. No schema change. No agent change. No script change. No template change. No example regeneration.

**Pros**:
- Zero pipeline coupling — tachi's stable six-phase pipeline remains unchanged
- Captures the alignment surfaces explicitly in a single discoverable artifact — CISO procurement reviews, SOC 2 cross-walks, FedRAMP AI references, HIPAA compatibility statements, FFIEC supervisory responses, and EU AI Act backbone citations all anchor to one location
- Preserves tachi's architecture-aware dimensions (trust-zone reachability, scalability) that have no AI RMF equivalent at the Subcategory level — wired integration risks degrading these signals into AI RMF vocabulary that does not carry their architectural semantics
- Mirrors the Feature 143 ADR-024 docs-only precedent (different decision — diverge there — but the same "no pipeline coupling, one discoverable ADR" shape)
- Zero backward-compatibility impact — PDF baselines under `SOURCE_DATE_EPOCH=1700000000` (ADR-021) remain byte-identical trivially; no infographic or report regeneration required
- Does not preclude future wiring — the re-evaluation triggers below define concrete conditions under which Option B or Option C becomes the appropriate posture

**Cons**:
- Adopters who expect *machine-readable* AI RMF tags on individual findings or controls (rather than a narrative mapping reference) will need to perform the cross-walk themselves using the shared reference
- Compliance officers at federally regulated organizations may prefer to cite a pipeline artifact field (e.g., a `nist_ai_rmf_subcategory` tag in `compensating-controls.md`) rather than cite a repository-level ADR + mapping reference
- The mapping reference requires maintenance when NIST publishes a new AI RMF revision (1.1 / 2.0) or a new GAI Profile revision — this is a small but non-zero recurring cost
- Documentation-only posture does not surface in SARIF output, limiting tool-to-tool integration pathways for adopters whose workflow consumes `threats.sarif` or `risk-scores.sarif` into an AI RMF-aware dashboard

**Effort estimate**: **S: ~0 additional effort beyond this ADR and the `nist-ai-rmf-mapping.md` artifact**. Pure documentation. No schema, no script, no agent, no example regeneration, no CI changes.

**Compliance Value for Regulated Adopters**: **High** across five surfaces. SOC 2 Type 2 auditors cross-walking AI controls can cite the mapping reference; FedRAMP AI-procurement reviewers can cite the mapping + ADR pair; HIPAA covered entities deploying AI can cite AI RMF alignment as a compatibility statement; FFIEC examiners can cite the mapping during supervisory conversations; EU AI Act conformity-assessment preparers can cite the mapping as a risk-management backbone reference. None of these surfaces require tachi to *produce* AI RMF-tagged pipeline output — all benefit from tachi *citing* AI RMF alignment.

**Pipeline Determinism Impact**: **None**. No schema changes, no new agents, no new pipeline phases, no new scripts, no example regeneration. ADR-021 determinism invariant is preserved trivially — there are no new pipeline inputs to vary.

**Why Chosen**: This is the lowest-cost option that captures the alignment surfaces explicitly, serves the five distinct regulatory surfaces identified in the Rationale, preserves tachi's architecture-aware dimensions, and does not commit the pipeline to a framework that operates one tier above tachi's natural artifact level. The Surface A Govern Gap is structural (policy-tier vs artifact-tier) and is not closeable by re-engineering — which means no amount of wiring effort reduces the Gap. The Surface B MEASURE 2.7 Overlap is already produced by tachi's existing pipeline — which means no wiring effort *increases* what tachi already contributes. The decision criteria favor documentation over wiring when the Overlap cells describe present-tense contributions rather than new behaviors.

### Option B: Shallow wired integration

**Description**: Extend [`schemas/compensating-controls.yaml`](../../../schemas/compensating-controls.yaml) to optionally reference NIST AI RMF Subcategories on each compensating control. A new optional field (for example, `nist_ai_rmf_subcategories: [MEASURE-2.7, MANAGE-1.3]`) allows the control-analyzer agent to tag controls with the Subcategories they contribute evidence to. The control-analyzer agent gains a classification step consulting the mapping reference. The PDF security-report template gains an optional column or inline annotation when tags are present. Backward compatible: when the field is absent, downstream behavior is identical to the pre-Option-B shape.

**Pros**:
- Machine-readable AI RMF coverage surface — adopters can query `compensating-controls.md` or its SARIF equivalent for NIST-tagged controls directly
- Additive schema change preserves backward compatibility (existing examples render identically when tags are absent)
- Closes the "no AI RMF signal in SARIF" Con from Option A for a subset of the pipeline (compensating controls surface only; does not cover threat findings or risk scores)
- Delivers AI RMF citation at the pipeline-output tier rather than the repository-docs tier — closer to what a FedRAMP-style tool-to-tool integration workflow would consume
- Incremental step toward Option C if future triggers fire — does not foreclose deeper integration

**Cons**:
- Adds labeling overhead without changing the evidence tachi produces — the control-analyzer agent spends classification effort on AI RMF tags rather than on control-coverage analysis
- Only covers the compensating-controls surface; threat findings and risk scores remain un-tagged, creating an asymmetric AI RMF coverage story across pipeline outputs
- Requires the mapping reference to become a machine-consumable artifact (structured YAML/JSON) rather than a human-readable narrative — raises the maintenance cost versus Option A
- Schema bump required on `compensating-controls.yaml` (additive, so minor-bump per the ADR-020 "enum-value-only minor-bump rule" precedent or equivalent additive-field rule — not major)
- Example regeneration required to demonstrate the tagged output; backward-compat test must verify that untagged findings render byte-identical
- Partial answer to the five regulatory-surface compliance value — FedRAMP-style tool-integration use cases benefit; SOC 2 / HIPAA / FFIEC / EU AI Act narrative-citation use cases are equally well-served by Option A

**Effort estimate**: **M: ~2–4 days; additive schema field on `compensating-controls.md`, control-analyzer agent update, PDF security-report template update, backward compatible when tags absent**. Includes example regeneration + backward-compat test validation + minor schema version bump.

**Compliance Value for Regulated Adopters**: **Moderate-to-High** on tool-integration surfaces (FedRAMP AI-procurement tool chains, SARIF-consuming AI-governance dashboards); **equivalent to Option A** on narrative-citation surfaces (SOC 2, HIPAA, FFIEC, EU AI Act cross-walks). The marginal value over Option A is concentrated in machine-consumption workflows.

**Pipeline Determinism Impact**: **Additive field — no new determinism sensitivity**. The new field's values come from a deterministic lookup against the mapping reference (which itself is content-only). ADR-021 determinism is preserved when the mapping reference is treated as input-equivalent to the control-categories reference. Example regeneration under `SOURCE_DATE_EPOCH=1700000000` re-baselines the backward-compat fixtures; no new determinism failure modes introduced.

**Why Not Chosen**: The marginal compliance value over Option A is concentrated in tool-integration workflows (machine-consumption of AI RMF tags from SARIF or Markdown), which are not evidenced by any of the five regulatory surfaces identified in the Rationale as a current adopter requirement. Without concrete adopter demand for the machine-readable tagging surface, the labeling overhead + schema maintenance cost + example regeneration cycle outweigh the incremental benefit. Option B is the natural next step *if* the re-evaluation triggers fire with a tool-integration demand signal — but filing it now is premature.

### Option C: Deep wired integration

**Description**: New agent at [`.claude/agents/tachi/nist-ai-rmf-analyzer.md`](../../../.claude/agents/tachi/nist-ai-rmf-analyzer.md) that runs after the compensating-controls analyzer and produces a dedicated NIST AI RMF coverage report. The agent re-traverses the architectural surfaces already analyzed by upstream phases, correlating findings + controls against AI RMF Subcategories and AI 600-1 GAI risks. Produces a new pipeline artifact (for example, `nist-ai-rmf-coverage.md` + `nist-ai-rmf-coverage.sarif`). Requires a new schema, a new PDF template page, a new pipeline phase (call it Phase 3.75 between Phase 3 controls and Phase 4 assessment), and regeneration of all 6 example outputs.

**Pros**:
- Comprehensive AI RMF coverage surface across threats, controls, and risk scores — not limited to the compensating-controls surface like Option B
- Dedicated artifact is discoverable and self-contained; adopters cite `nist-ai-rmf-coverage.md` directly rather than reconstructing coverage from tagged fields
- Closes the asymmetric-coverage Con from Option B (threat findings and risk scores are now AI-RMF-aware alongside controls)
- Opens a future surface for AI RMF Profile variants — the agent could consume AI 600-1 GAI Profile, SP 800-53 AI Overlay (when published), or sector-specific NIST profiles (CSF 2.0 AI additions, NIST AI 600-1 sector profiles) with incremental prompt changes

**Cons**:
- Re-traverses architectural surfaces tachi already covers — produces a parallel report that re-states existing findings under NIST vocabulary rather than adding net-new analysis
- Highest-cost option by roughly an order of magnitude versus Option A; non-trivial blast radius across agents, schemas, templates, and examples
- Couples tachi's stable pipeline to a framework that operates one tier above tachi's natural artifact level — Govern Subcategories in particular are policy-tier, and a code-analysis agent cannot produce evidence for policy-tier outcomes without stubbing or fabricating
- Example regeneration invalidates all 6 PDF baselines; backward-compat test under `SOURCE_DATE_EPOCH=1700000000` requires a full re-baseline cycle
- New pipeline phase is an ADR-020 scope expansion (MAESTRO classification surface) and an ADR-021 determinism scope expansion (new phase must be deterministic-by-construction)
- Content-policy / fairness / environmental GAI risks (Surface C's 7 No equivalent rows) either get stubbed in the coverage report (misleading) or omitted (incomplete) — no clean answer

**Effort estimate**: **L: ~6–10 days; new agent, new schema, new template page, new pipeline phase, example regen required**. Includes backward-compat re-baseline, determinism validation on the new phase, SKILL.md authoring for the new agent, orchestrator dispatch-rules update, and risk-scorer / threat-report / report-assembler downstream awareness updates.

**Compliance Value for Regulated Adopters**: **High** on comprehensive-coverage use cases (tool-to-tool integration where AI RMF coverage is a first-class artifact). **Equivalent to Option A** on narrative-citation use cases. The marginal value over Option B is concentrated in "comprehensive coverage across all pipeline surfaces" workflows, which are not evidenced by any current adopter demand.

**Pipeline Determinism Impact**: **New pipeline phase — determinism must be preserved per ADR-021**. The new phase introduces new surface area for determinism regressions: LLM-driven classification of findings against Subcategories must be either deterministic-by-construction (lookup-table driven) or fenced by a deterministic reducer. Example regeneration under `SOURCE_DATE_EPOCH=1700000000` requires all 6 baselines to be re-established and the backward-compat test to be updated. This is not a blocker but is a non-trivial determinism budget.

**Why Not Chosen**: The Surface B MEASURE 2.7 Overlap finding tells us that tachi's existing pipeline *already* produces what AI RMF's central security-resilience Subcategory names. A dedicated NIST AI RMF analyzer would re-state existing findings under NIST vocabulary rather than add net-new analysis. The cost-benefit ratio against Option A is unfavorable: 6–10 days of pipeline-coupling work for a surface that restates rather than extends. The decisive tie-breaker is the Surface A Govern Gap — it is structural (policy-tier vs artifact-tier) and is not closeable by any agent tachi can author. An analyzer that claims Govern coverage would be producing fabricated policy-tier evidence; an analyzer that omits Govern delivers the same Govern-absent mapping Option A already documents.

**A hybrid B+C variant** — schema tags on compensating controls *plus* a lightweight coverage summary section in an existing artifact (rather than a dedicated new artifact) — is noted here per PRD 144 FR-003 for completeness. It would combine the machine-readable tagging of Option B with a narrative-coverage summary of Option C, at an effort in the M+ to L- range (~4–6 days). It is not surfaced as a primary option because it inherits both Option B's asymmetric-coverage problem (control-only tagging) and Option C's re-traversal problem (narrative coverage summary), without fully resolving either. It remains a design space for future re-evaluation if the triggers fire with a specific hybrid demand signal.

---

## Consequences

### Positive

- The alignment question is documented in a single linkable artifact — CISO procurement reviews, SOC 2 cross-walks, FedRAMP AI-procurement references, HIPAA compatibility statements, FFIEC supervisory responses, and EU AI Act conformity-assessment preparation all anchor here
- Zero pipeline change; zero risk to existing scoring, threat, control, or report outputs; backward-compatibility PDF baselines (per ADR-021) remain trivially byte-identical
- Tachi's architecture-aware dimensions (trust-zone reachability, scalability) are preserved — these have no AI RMF Subcategory equivalent, and wired integration risked degrading them into AI RMF vocabulary that does not carry their architectural semantics
- The companion shared reference at [`.claude/skills/tachi-shared/references/nist-ai-rmf-mapping.md`](../../../.claude/skills/tachi-shared/references/nist-ai-rmf-mapping.md) ships the full Subcategory-to-control-category and GAI-risk-to-STRIDE+AI crosswalks for adopters who must cite NIST mappings during procurement, audit, or examination workflows
- The `tachi-control-analysis` skill gains a cross-reference paragraph that downstream consumers (the control-analyzer agent and developers reading the skill) use to answer the NIST AI RMF question without leaving the skill file
- The MAESTRO compliance umbrella (closed by ADR-024 per Feature 143) is now accompanied by a companion NIST AI RMF evaluation — adopters navigating multiple agentic-AI frameworks find both evaluations under one governance surface

### Negative

- Tachi's AI RMF signal lives at the repository-docs tier (this ADR + the mapping reference) rather than at the pipeline-output tier (machine-readable tags in `compensating-controls.md` or SARIF). Adopters with tool-to-tool integration workflows must perform the cross-walk themselves using the shared reference
- The mapping reference requires maintenance when NIST publishes a new AI RMF revision (1.1 / 2.0) or a new GAI Profile revision — a small but non-zero recurring documentation cost
- No SARIF-level AI RMF tagging is produced — AI-governance dashboards that consume `threats.sarif` or `risk-scores.sarif` cannot query AI RMF coverage directly without external cross-walk
- The decision leaves open a future migration cost if the re-evaluation triggers fire and Option B or Option C becomes the appropriate posture — the three-surface analysis above is the baseline that migration would refine rather than reconstruct, bounding (but not eliminating) the future cost

### Mitigation

- **Maintenance commitment**: the `nist-ai-rmf-mapping.md` reference will be updated when NIST AI RMF publishes a new revision (1.1 / 2.0), when NIST AI 600-1 publishes a new revision, or when tachi adds a new compensating-control category or STRIDE+AI agent. The commitment is bounded — these are discrete events, not continuous drift
- The three-surface comparison (Surface A / B / C) in this ADR is preserved as a baseline that future re-evaluation refines rather than reconstructs from scratch, bounding the cost of revisiting under the triggers below
- The `tachi-control-analysis` SKILL cross-reference paragraph ensures the decision is discoverable at the point of control-analysis work, so future pipeline changes are evaluated against this ADR rather than being made in ignorance of it
- The explicit comparison to ADR-024 in the Rationale establishes the precedent that companion-ADR evaluations are reasoned afresh rather than inherited — preventing future framework evaluations from silently defaulting to ADR-024's divergence logic

### Follow-on Implementation

**No follow-on implementation Issue is filed.** This is a deliberate consequence of choosing Option A per PRD 144 FR-008 conditionality: a follow-on Issue is filed only if the decision is Option B (shallow wired integration) or Option C (deep wired integration). The re-evaluation triggers below replace the follow-on Issue as the anchor for future work.

---

## When to Re-Evaluate

This ADR's posture is valid until **at least one** of the following concrete triggers fires:

1. **≥3 regulated-industry adopter inquiries** — when three or more adopters in regulated industries (FedRAMP-scoped, SOC 2 Type 2, HIPAA-covered, FFIEC-supervised, or EU AI Act-subject) explicitly request machine-readable AI RMF tagging or a dedicated AI RMF coverage artifact that the documentation-only posture cannot satisfy. This is the canonical demand-signal trigger: documentation-only is sufficient when narrative citation serves the adopter; it becomes insufficient when tool-integration workflows emerge at scale.

2. **NIST AI RMF 2.0 publication** — when NIST publishes a formal AI RMF 2.0 revision (or an equivalent major revision such as AI RMF 1.1 with substantive structural changes to the Core or to the Categories/Subcategories). AI 100-1 §"Update Schedule and Versions" commits to a formal community-input review "no later than 2028"; this trigger anticipates that review outcome. A major revision warrants re-running Surfaces A/B/C against the new dimensions and re-assessing the five-criteria justification.

3. **SP 800-53 AI overlay GA** — when NIST publishes the AI Control Overlay for SP 800-53 as a General Availability (GA) artifact (currently in concept-paper stage with drafts planned Q3 2026 per public NIST roadmap signals). An 800-53 AI overlay is the inflection point where AI RMF alignment becomes citable inside FedRAMP-equivalent control baselines, which raises the compliance-value profile substantially and may tip the cost-benefit ratio toward Option B or Option C.

When any trigger fires, the architect (or a future equivalent role) should:

1. Re-read the relevant NIST publication and re-run the three-surface comparison (Surfaces A, B, C) in this ADR against the revised or new content
2. Reassess the five evaluation criteria (maturity, adoption, compatibility, effort, compliance value) — particularly the compliance-value surface most affected by the trigger
3. Re-author this ADR's Decision section, or supersede this ADR with a new ADR if the chosen option changes
4. If the new decision is Option B or Option C, file the follow-on implementation Issue per the FR-008 conditionality preserved across this ADR's lineage

The re-evaluation does not require waiting for a periodic schedule — it is event-triggered. If none of the triggers fire, the present posture remains valid indefinitely, subject only to the maintenance commitment on the mapping reference.

---

## References

### Internal (tachi)

- PRD 144: [`specs/144-nist-ai-rmf-evaluation-adr/`](../../../specs/144-nist-ai-rmf-evaluation-adr/)
- Companion mapping reference: [`.claude/skills/tachi-shared/references/nist-ai-rmf-mapping.md`](../../../.claude/skills/tachi-shared/references/nist-ai-rmf-mapping.md)
- Tachi control-analysis skill (cross-reference paragraph anchors to this ADR): [`.claude/skills/tachi-control-analysis/SKILL.md`](../../../.claude/skills/tachi-control-analysis/SKILL.md)
- Tachi control categories reference: [`.claude/skills/tachi-control-analysis/references/control-categories.md`](../../../.claude/skills/tachi-control-analysis/references/control-categories.md)
- Tachi STRIDE+AI categories shared reference: [`.claude/skills/tachi-shared/references/stride-categories-shared.md`](../../../.claude/skills/tachi-shared/references/stride-categories-shared.md)
- Tachi pipeline-phase architecture: [`docs/architecture/01_system_design/README.md`](../../architecture/01_system_design/README.md)
- [ADR-018](ADR-018-baseline-aware-pipeline-correlation.md) — baseline-aware pipeline correlation (lineage preserved by this ADR)
- [ADR-019](ADR-019-shared-definitions-and-model-field-governance.md) — shared cross-agent definitions (governance precedent)
- [ADR-020](ADR-020-maestro-layer-classification.md) — MAESTRO classification (companion taxonomy; AI RMF is framework-level, MAESTRO is layer-level)
- [ADR-021](ADR-021-source-date-epoch-for-deterministic-pdf-comparison.md) — SOURCE_DATE_EPOCH determinism (invariant preserved trivially by this ADR)
- [ADR-023](ADR-023-threat-agent-skill-references-pattern.md) — skill-references pattern (shape precedent for the mapping reference)
- [ADR-024](ADR-024-owasp-aivss-evaluation.md) — companion OWASP AIVSS evaluation (different decision, same companion-ADR shape)

### External (NIST canonical)

- NIST AI Risk Management Framework (home): [`https://www.nist.gov/itl/ai-risk-management-framework`](https://www.nist.gov/itl/ai-risk-management-framework)
- NIST AI 100-1 AI RMF 1.0 PDF: [`https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.100-1.pdf`](https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.100-1.pdf)
- NIST AI 600-1 Generative AI Profile PDF: [`https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.600-1.pdf`](https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.600-1.pdf)
- NIST AI 600-1 DOI: [`https://doi.org/10.6028/NIST.AI.600-1`](https://doi.org/10.6028/NIST.AI.600-1)
