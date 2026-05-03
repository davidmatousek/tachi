# NIST AI RMF Mapping (Companion to ADR-025)

**Purpose**: Companion mapping artifact to [ADR-025](../../../../docs/architecture/02_ADRs/ADR-025-nist-ai-rmf-evaluation.md) recording tachi's **documentation-only mapping** posture toward the NIST Artificial Intelligence Risk Management Framework (AI RMF 1.0, NIST AI 100-1, January 2023) and the NIST AI 600-1 Generative AI Profile (July 2024). This file is the canonical NIST crosswalk for adopters who must cite NIST mappings during procurement, audit, or regulatory examination workflows.

ADR-025 is the source of truth for the decision, rationale, and the three-surface comparison (Functions × pipeline phases, Subcategories × control categories, GAI risks × STRIDE+AI categories). This file surfaces two of those three surfaces at the full coverage width — every tachi compensating-control category (all 8) and every NIST AI 600-1 GAI risk × tachi STRIDE+AI category pair (12 × 11) — for adopters whose workflow is tachi-indexed ("given this tachi control category, what NIST Subcategories does it inform?") rather than NIST-indexed.

Relationship labels use exactly one of: `Overlap`, `Gap`, `Conflict`, or `No equivalent`. Many-to-many mapping is used where a single tachi category legitimately addresses multiple NIST Subcategories (and vice versa). This discipline mirrors ADR-025's label discipline and is enforced for SC-004 consistency.

---

## Surface B — tachi Compensating-Control Categories × NIST AI RMF Subcategories

One row per tachi compensating-control category (all 8). NIST Subcategory citations are drawn from NIST AI 100-1 Tables 1-4 (GOVERN 1-6, MAP 1-5, MEASURE 1-4, MANAGE 1-4). Multiple NIST Subcategories per tachi category indicate that the control evidence surface contributes to more than one NIST outcome simultaneously — this is expected and reflects the NIST framework's layered organizational-outcome model.

| tachi Control Category | NIST AI RMF Subcategory (or "No equivalent") | Relationship | Note |
|---|---|---|---|
| **authentication** | MAP 4.2 (internal risk controls for components, including third-party AI technologies, are identified and documented); MEASURE 2.7 (AI system security and resilience are evaluated and documented); MANAGE 1.3 (responses to high-priority AI risks are developed, planned, and documented) | **Overlap** | Authentication evidence directly informs MEASURE 2.7 (the single AI RMF Subcategory that most precisely names tachi's deliverable — security and resilience evaluation). Third-party component authentication additionally informs MAP 4.2. The evidence also populates the response inventory MANAGE 1.3 expects. |
| **input-validation** | MAP 4.2; MEASURE 2.6 (AI system is evaluated regularly for safety risks, demonstrated to fail safely); MEASURE 2.7; MEASURE 2.10 (privacy risk is examined and documented); MANAGE 1.3 | **Overlap** | Input-validation is the single most multi-Subcategory control in the tachi catalog. It is a fail-safe control (MEASURE 2.6), a security-and-resilience control (MEASURE 2.7), a PII sanitization control at ingress (MEASURE 2.10), and a per-component third-party-integration control (MAP 4.2). |
| **rate-limiting** | MEASURE 2.6; MEASURE 2.7; MANAGE 1.3 | **Overlap** | Rate-limiting is a canonical fail-safe control under adversarial input — the strongest tachi category match for MEASURE 2.6 ("demonstrated to be safe, can fail safely"). It also contributes to MEASURE 2.7 availability-and-resilience evaluation and to the MANAGE 1.3 response inventory. |
| **encryption** | MAP 4.2; MEASURE 2.7; MEASURE 2.10; MANAGE 1.3 | **Overlap** | Encryption covers data-at-rest and data-in-transit, directly informing MEASURE 2.10 privacy risk documentation and MEASURE 2.7 confidentiality-and-resilience evaluation. Third-party encryption in-transit contributes to MAP 4.2. |
| **logging-audit** | GOVERN 1.4 (transparent policies, procedures, and other controls based on organizational risk priorities); MEASURE 2.7; MEASURE 2.8 (risks associated with transparency and accountability are examined and documented); MANAGE 1.3 | **Overlap** | Audit-trail evidence is the canonical transparency-and-accountability control (MEASURE 2.8) and contributes directly to the transparency-mechanism outcome GOVERN 1.4 expects. This is the single tachi control category with a GOVERN-tier contribution — though GOVERN remains a Gap at the Function level per ADR-025 Surface A (policy-tier vs artifact-tier). |
| **csrf-protection** | MEASURE 2.7; MANAGE 1.3 | **Overlap** | CSRF protection is a session-integrity web-security control. It is a measurement of AI-system resilience (MEASURE 2.7) and contributes evidence to the MANAGE 1.3 response inventory. The narrower scope (session integrity only) yields fewer Subcategory matches than authentication or input-validation. |
| **csp-security-headers** | MEASURE 2.7; MANAGE 1.3 | **Overlap** | Content Security Policy and security headers are browser-layer defense-in-depth controls. As with CSRF, the scope is focused on web-channel integrity — MEASURE 2.7 and MANAGE 1.3 are the natural matches. |
| **access-control** | MAP 4.2; MEASURE 2.7; MEASURE 2.10; MANAGE 1.3 | **Overlap** | Access-control (authorization / RBAC / data partitioning) is the canonical "who-can-read-what" privacy control (MEASURE 2.10) and a core confidentiality-and-resilience control (MEASURE 2.7). Third-party access-control boundaries additionally inform MAP 4.2. |

**Surface B observations** (from ADR-025):

- **MEASURE 2.7** (security and resilience evaluation) is the single NIST Subcategory that every tachi control category informs — it is the strongest one-to-one semantic overlap.
- **MANAGE 1.3** (high-priority response inventory) is the second single Subcategory all 8 categories inform — the `compensating-controls.md` deliverable enumerates exactly the kind of response inventory MANAGE 1.3 expects.
- **GOVERN-tier contributions are scarce** — only logging-audit touches a GOVERN Subcategory (GOVERN 1.4). This mirrors ADR-025 Surface A finding that tachi is artifact-tier and GOVERN is policy/culture-tier. The Gap is structural, not a defect.
- **Inventory mechanism** (GOVERN 1.6 — "mechanisms are in place to inventory AI systems") is **not covered** by any tachi compensating-control category. The DFD produced in Phase 1 Scope is an architecture-modeling-tier inventory artifact, but no code-level control category targets running-system inventory mechanisms. This is documented as a **Gap** in ADR-025 Surface B and is listed here for adopter awareness.
- **Operational kill-switch** (MANAGE 2.4 — "mechanisms are in place to supersede, disengage, or deactivate AI systems") is **No equivalent** in tachi — outside the code-level control scope.

---

## Surface C — NIST AI 600-1 GAI Risks × tachi STRIDE+AI Categories (Full Crosswalk)

One row per NIST AI 600-1 §2 Generative AI risk (12 total: §§2.1–2.12) × each of the 11 tachi STRIDE+AI categories (S, T, R, I, D, E + Prompt Injection, Data Poisoning, Model Theft, Agent Autonomy, Tool Abuse). Where a GAI risk naturally maps to multiple tachi categories, multiple rows are emitted with the same GAI risk column. Where a GAI risk has no tachi equivalent at all, a single `No equivalent` row is emitted to preserve the 12-risk coverage audit.

| GAI Risk (NIST AI 600-1 §2) | tachi STRIDE+AI Category | Relationship | Note |
|---|---|---|---|
| **§2.1 CBRN Information or Capabilities** | No equivalent | **No equivalent** | Content-policy harm class. Tachi does not evaluate model-output policy violations on weapons-of-mass-destruction information — outside security-analysis scope. |
| **§2.2 Confabulation** | No equivalent | **No equivalent** | Hallucination / valid-but-wrong output is a model-behavior concern, not a security-control concern. Outside tachi's STRIDE+AI scope. |
| **§2.3 Dangerous, Violent, or Hateful Content** | No equivalent | **No equivalent** | Content-policy harm class outside tachi's security-analysis scope. Fairness / moderation agents are a separate tool category. |
| **§2.4 Data Privacy** | Information Disclosure (I) | **Overlap** | PII leakage, unauthorized disclosure, and de-anonymization are exactly tachi-info-disclosure agent territory. Encryption + access-control compensating controls address the attack surface directly. |
| **§2.5 Environmental Impacts** | No equivalent | **No equivalent** | Compute-resource and ecosystem impacts outside security-analysis scope. |
| **§2.6 Harmful Bias or Homogenization** | No equivalent | **Gap** | Bias amplification and performance disparities touch model-output fairness. Tachi has no fairness-evaluation agent. Labeled **Gap** (rather than `No equivalent`) because adopters may legitimately ask "does tachi cover this?" and the honest answer is "not yet" — this is a candidate roadmap surface. |
| **§2.7 Human-AI Configuration** | No equivalent | **No equivalent** | Anthropomorphization, automation bias, over-reliance, and emotional entanglement — human-factors concerns outside tachi's threat-modeling scope. |
| **§2.8 Information Integrity** | No equivalent | **No equivalent** | Mis/disinformation campaign enablement — content-policy harm class outside tachi's security-analysis scope. |
| **§2.9 Information Security** | Tampering (T) | **Overlap** | AI 600-1 §2.9 names "compromise of confidentiality or integrity of training data, code, or model weights" — integrity compromise maps directly to tachi-tampering. |
| **§2.9 Information Security** | Information Disclosure (I) | **Overlap** | AI 600-1 §2.9 names "compromise of confidentiality…of training data, code, or model weights" — confidentiality compromise maps directly to tachi-info-disclosure. |
| **§2.9 Information Security** | Denial of Service (D) | **Overlap** | AI 600-1 §2.9 names "compromise of…availability" — availability compromise maps directly to tachi-denial-of-service. |
| **§2.9 Information Security** | Prompt Injection | **Overlap** | AI 600-1 §2.9 **explicitly names "prompt injection"** as a GAI Information Security risk. Direct one-to-one with tachi-prompt-injection agent. Strongest AI-specific cross-mapping in Surface C. |
| **§2.9 Information Security** | Data Poisoning | **Overlap** | AI 600-1 §2.9 **explicitly names "data poisoning"** and "compromise of…integrity of training data" — direct one-to-one with tachi-data-poisoning agent. |
| **§2.9 Information Security** | Spoofing (S) | **Gap** | §2.9 does not name identity-spoofing explicitly, but automated phishing enablement ("offensive cyber capabilities, including…phishing") is an adjacent concern — labeled Gap because the scope overlap is partial and tachi-spoofing's coverage of AI-enabled identity-spoofing is an adopter-surface-able topic. |
| **§2.9 Information Security** | Elevation of Privilege (E) | **Overlap** | AI 600-1 §2.9 names "automated discovery and exploitation of vulnerabilities" — privilege escalation is a canonical outcome of vulnerability exploitation. tachi-privilege-escalation agent maps directly. |
| **§2.9 Information Security** | Repudiation (R) | **No equivalent** | §2.9 does not explicitly touch non-repudiation / audit-trail concerns. tachi-repudiation's scope (transaction-integrity evidence) sits orthogonally to the GAI-specific risks §2.9 enumerates. |
| **§2.9 Information Security** | Model Theft | **Overlap** | AI 600-1 §2.9 names "compromise of…integrity of…model weights" — model extraction / weight exfiltration maps directly to tachi-model-theft agent. |
| **§2.9 Information Security** | Agent Autonomy | **Overlap** | AI 600-1 §2.9's "increased attack surface for targeted cyberattacks" applies acutely to agentic-AI runtimes where autonomy expansion enlarges the attack surface. tachi-agent-autonomy maps directly. |
| **§2.9 Information Security** | Tool Abuse | **Overlap** | AI 600-1 §2.9's "automated discovery and exploitation of vulnerabilities" maps directly to tool-call abuse in agentic systems. tachi-tool-abuse agent covers this. |
| **§2.10 Intellectual Property** | Model Theft | **Overlap** | AI 600-1 §2.10 names "exposure of trade secrets" and "exposure of model weights" — direct one-to-one with tachi-model-theft. The IP-replication aspect (alleged copyright infringement via model-trained content) sits outside tachi's scope, but the trade-secret / model-weight exposure aspect is in-scope. |
| **§2.10 Intellectual Property** | Information Disclosure (I) | **Overlap** | Trade-secret exposure is a specialized form of unauthorized disclosure; tachi-info-disclosure covers the exfiltration attack surface when the protected asset is a model, training artifact, or weight file. |
| **§2.11 Obscene, Degrading, and/or Abusive Content** | No equivalent | **No equivalent** | Content-policy harm class outside tachi's security-analysis scope. Child-safety / NCII moderation is a separate tool category. |
| **§2.12 Value Chain and Component Integration** | Tool Abuse | **Overlap** | AI 600-1 §2.12 names "non-transparent or untraceable integration of upstream third-party components" — this is exactly the third-party tool / plugin / API integration surface tachi-tool-abuse covers. |
| **§2.12 Value Chain and Component Integration** | Tampering (T) | **Overlap** | §2.12's "improper supplier vetting across the AI lifecycle" and "data that has been improperly obtained or not processed and cleaned" map to supply-chain integrity concerns — tachi-tampering covers the tampered-upstream-artifact attack surface. |
| **§2.12 Value Chain and Component Integration** | Data Poisoning | **Overlap** | §2.12's "data that has been improperly obtained or not processed and cleaned due to increased automation from GAI" is a supply-chain data-poisoning surface — tachi-data-poisoning covers the adversarial-training-data attack pattern. |

**Surface C observations** (from ADR-025):

- **§2.9 Information Security is the single densest mapping row** — 8 of 11 STRIDE+AI categories overlap, one is a partial Gap, one is No equivalent. This confirms AI 600-1 §2.9 is the natural primary linkage surface between the NIST GAI profile and tachi's security-focused pipeline.
- **§§2.4, 2.9, 2.10, 2.12 are the Overlap subset** — exactly 4 of 12 GAI risks sit within tachi's security-analysis scope as direct mappings. The security-relevant subset is small but deep.
- **7 of 12 GAI risks are `No equivalent`** (§§2.1, 2.2, 2.3, 2.5, 2.7, 2.8, 2.11) — content-policy, fairness, human-factors, and environmental harm classes tachi has deliberately not modeled. The >50% No-equivalent rate is itself evidence that AI 600-1 covers a broader harm space than tachi's security-focused pipeline. This is flagged in ADR-025 Surface C as a sixth de facto evaluation criterion: *scope completeness on the security-relevant subset is high; scope completeness on the full GAI risk set is partial by design.*
- **§2.6 Harmful Bias is the single `Gap`** — flagged deliberately (rather than as No equivalent) to mark it as a candidate roadmap surface where adopter demand may warrant future scope expansion.

---

## How to Use This Mapping

**For procurement responses**: Cite the Surface B row corresponding to the adopter's emphasized control category (e.g., "tachi's `encryption` control category maps to NIST AI RMF MEASURE 2.10, MEASURE 2.7, MAP 4.2, and MANAGE 1.3 per ADR-025 and the companion `nist-ai-rmf-mapping.md`").

**For regulatory audit**: Cite the Surface C Overlap rows for §§2.4, 2.9, 2.10, 2.12. Note explicitly the 7 `No equivalent` rows as deliberate scope boundaries so auditors do not assume coverage where none exists.

**For roadmap conversations**: Note the 2 `Gap` cells — GOVERN 1.6 (inventory mechanisms) and GAI §2.6 (harmful bias) — as the honest not-yet surfaces.

**Do NOT cite this file in isolation** — always pair it with [ADR-025](../../../../docs/architecture/02_ADRs/ADR-025-nist-ai-rmf-evaluation.md), which carries the full Decision rationale, the Surface A Functions × phases comparison, and the re-evaluation triggers.

---

## Maintenance Commitment

Per ADR-025 Consequences section, this file is maintenance-bounded. Revise when **any one** of the following occurs:

- NIST publishes **AI RMF 1.1 or 2.0** (re-evaluate Surface A Functions, Surface B Subcategory IDs — the 18 Category / 68 Subcategory structure may change).
- NIST publishes a **new AI 600-1 revision** (re-evaluate Surface C — the 12 GAI risk enumeration may change).
- NIST publishes the **SP 800-53 AI Control Overlay v1.0** (currently in concept-paper stage per research §4; drafts planned Q3 2026) — may require a third mapping surface against SP 800-53 control families.
- **tachi adds a new compensating-control category** beyond the current 8 — add a row to Surface B.
- **tachi adds a new STRIDE+AI agent** beyond the current 11 — add a column (or row set) to Surface C.

No autonomous re-baseline of this file is required when NIST publishes clarifying blog posts, playbook updates, or non-normative companion documents.

---

## References

- [ADR-025: NIST AI RMF Evaluation and Tachi Alignment Posture](../../../../docs/architecture/02_ADRs/ADR-025-nist-ai-rmf-evaluation.md) — canonical Decision source of truth.
- NIST AI 100-1 (AI RMF 1.0): `https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.100-1.pdf` (DOI `https://doi.org/10.6028/NIST.AI.100-1`).
- NIST AI 600-1 (Generative AI Profile): `https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.600-1.pdf` (DOI `https://doi.org/10.6028/NIST.AI.600-1`).
- NIST AI RMF landing page: `https://www.nist.gov/itl/ai-risk-management-framework`.
- tachi compensating-control category catalog: `../../tachi-control-analysis/references/control-categories.md`.
- tachi STRIDE+AI category catalog: `./stride-categories-shared.md`.
