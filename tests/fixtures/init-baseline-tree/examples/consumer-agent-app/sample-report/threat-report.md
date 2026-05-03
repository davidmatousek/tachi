---
schema_version: "1.0"
date: "2023-11-14"
source_file: "/Users/david/Projects/tachi/examples/consumer-agent-app/test-output/2023-11-14T22-13-20-F4-wave5/threats.md"
finding_count: 19
risk_distribution:
  critical: 1
  high: 8
  medium: 7
  low: 3
  note: 0
attack_tree_count: 9
---

# Threat Report — Consumer-Facing AI Companion Application (F-4 Wave 5)

**Date**: 2023-11-14
**Schema Version**: 1.8
**Pipeline Run**: 2023-11-14T22-13-20

---

## 1. Executive Summary

This threat model covers the F-4 Wave 5 baseline of the Consumer-Facing AI Companion Application — a clean-slate single-Process consumer-facing AI architecture demonstrating the `human-trust-exploitation` (OWASP ASI09:2026) communication-axis dispatch trigger in isolation. The architecture exercises all five `human-trust-exploitation` Pattern Categories (Undisclosed AI Authorship, Authority-Claim Emission Without Confidence/Source Attestation, Persuasive-Tone Manipulation / Missing Uncertainty Disclosure, Persona-Boundary Violations on Long-Running Dialogues, Synthetic-Relationship Exploitation in vulnerable-population contexts).

**Total findings: 19** (1 Critical, 8 High, 7 Medium, 3 Low). This is a clean-slate baseline with no carry-over from prior runs.

**Key risk surfaces**:
- The WellnessCompanionChatbot Process emits five distinct TE-{N} findings (TE-1 through TE-5), each addressing a separate ASI09:2026 communication-axis sub-class with its own source attribution and mitigation prescription. TE-5 (Synthetic-Relationship Exploitation) reaches Critical risk level due to the vulnerable-population deployment surface signaled by the combination of sustained-engagement framing and authority-claim emission framing.
- Standard STRIDE coverage is present: 14 STRIDE findings span the Process (S, T, R, I, D, E), the External Entity (S, R), and both Data Stores (T, I, D each).
- No AG-{N}/AGP-{N}/LLM-{N}/OI-{N}/MI-{N} carry-over: the architecture is single-Process consumer-facing without LLM-keyword-bearing components, multi-agent topology, or AG-keyword surface — the TE-{N} signal class is isolated by design.

**Priority recommendation**: Before deploying any wellness-conversation companion in any consumer-facing context where vulnerable populations may engage, implement (1) the vulnerable-population safeguards layer per TE-5 mitigation (session-length cap, escalation-to-human path, dependency-risk classifier, mandatory professional-care referral), (2) the AI-disclosure mechanism per TE-1 mitigation (mandatory disclosure banner, pre-conversation splash, identity-impersonation refusal pattern), and (3) the confidence/source attestation per TE-2 mitigation (confidence-threshold gate with confidence display, source-attestation requirement, refusal pattern for low-confidence claims).

---

## 2. Architecture Overview

The system is a single-Process consumer-facing AI architecture with the following principal trust zones:

- **User Zone** (Untrusted): End User submitting prompts via HTTPS
- **Application Zone** (Trusted): WellnessCompanionChatbot (consumer-facing AI Process), Conversation Session Store (Data Store — persona state persistence), Interaction Audit Log (Data Store — append-only event log)

The architecture is intentionally narrow — a single Process node, no companion siblings, no peer-to-peer routing substrate, no external function-invocation server — so that the AI-companion-tier and agentic-autonomy-axis sibling finding families do not emit on the consumer-facing surface, keeping the TE-{N} signal class isolated for adopter pedagogy.

**MAESTRO layer distribution**:
- **L7 — Agent Ecosystem**: WellnessCompanionChatbot, End User (consumer-facing chat UI surface)
- **L5 — Evaluation and Observability**: Interaction Audit Log
- **Unclassified**: Conversation Session Store

**Trust boundary crossings**:
- DF-1 End User → WellnessCompanionChatbot (User Turn HTTPS): User Zone → Application Zone (untrusted → trusted)
- **DF-2 WellnessCompanionChatbot → End User (Companion Response HTTPS): Application Zone → User Zone (trusted → untrusted) — this is FR-006 Indicator A, the structural signal that the Process emits content to a human-named External Entity**

This is the clean-slate baseline complement to F-3's `examples/agentic-app/` baseline. F-3 demonstrates AG, AGP, TE adjacency on a multi-agent topology; this baseline complements that demonstration by showing TE-{N} emission in isolation on a single-Process consumer-facing surface.

---

## 3. Critical Findings Analysis

### Single-Process Consumer-Facing AI: Five TE Sub-Classes Emitted

The WellnessCompanionChatbot Process emits five distinct TE-{N} findings, each corresponding to one of the five OWASP ASI09:2026 communication-axis sub-classes. The Process matches four primary trigger keywords (`chatbot`, `companion`, `coach`, `consumer-facing`) and exhibits all four FR-006 emission indicators (A: outgoing data flow to End User; B: consumer-facing emission framing; C: sustained-engagement framing; D: authority-claim emission framing). The combination of indicators C and D signals a vulnerable-population deployment surface, escalating TE-5 to Critical risk level.

**STRIDE Coverage on WellnessCompanionChatbot (S-2, T-1, R-2, I-1, D-1, E-1)**: Standard Process-tier STRIDE threats apply. Most notable:
- **I-1 (High)**: Cross-user persona state disclosure through Companion Response — a high-impact concern in wellness-conversation contexts where one user's distress disclosures could leak into another user's restored session
- **D-1 (High)**: Service exhaustion denying legitimate users access during high-vulnerability periods (e.g., distress-driven engagement)
- **E-1 (High)**: Persona-prompt injection enabling privilege escalation through persona-prompt manipulation (the agent asserts credentials it does not hold)

### Three-Prefix-Family Discipline Verification (SC-014)

This baseline exercises only one of the three agentic-category prefix families. In the `category: agentic` section:
- **AG-{N} findings: 0** — `agent-autonomy` and `tool-abuse` are NOT dispatched (no AG-keyword match: no `agent`, `autonomous`, `orchestrator`, `MCP server`, `tool server`, or `plugin` in the architecture)
- **AGP-{N} findings: 0** — Single-Process architecture lacks the multi-agent topology required for Feature 142's AGP emission
- **TE-{N} findings: 5** — All five Pattern Categories emitted (TE-1 through TE-5)

This is the **lean case** for three-prefix-family adjacency — only TE-{N} present in the agentic section. F-3's `examples/agentic-app/` baseline (post-Wave-3) demonstrates AG, AGP, TE adjacency on a multi-agent topology; this clean-slate baseline complements that demonstration by showing TE-{N} emission in isolation on a single-Process consumer-facing surface. No prose synthesis of distinct prefix families occurs (FR-018 invariant): each TE-{N} finding renders in its own table with its own `source_attribution` array; no shared bullet, sentence, or paragraph mixes prefix families.

---

## 4. Threat Category Deep-Dives

### 4.1 Agentic Threats (TE-1 through TE-5) — F-4 Net-New

The five TE findings represent the entirety of the AI-tier risk surface on this baseline. They are the demonstration target for the F-4 Wave 5 regen task (T036). All five carry `category: agentic`, primary `source_attribution` to OWASP ASI09:2026, and CWE relateds appropriate to each Pattern Category.

#### Pattern Category 1 — Undisclosed AI Authorship (TE-1, High)

**Sub-class predicate per FR-004(e)**: authorship-disclosure (the architectural feature governing whether emitted content is identifiable as AI-originated). NOT authority-attestation, NOT persuasion-manipulation, NOT persona-boundary, NOT synthetic-relationship.

The wellness-conversation companion emits Companion Responses to End Users without a declared AI-generation disclosure mechanism. No mandatory pre-conversation AI-disclosure splash, banner, or per-message AI-source label is declared on the user-facing surface. No refusal pattern is declared for identity-impersonation challenges (e.g., "Are you human?" prompts produce undefined behavior). Per OWASP ASI09:2026 and CWE-223 (Omission of Security-relevant Information), undisclosed AI authorship undermines user-side trust calibration.

**Mitigation prescription**: mandatory AI-generation disclosure banner; pre-conversation AI-disclosure splash with explicit consent confirmation; per-message AI-source label embedded in the response payload; deterministic refusal pattern for identity-impersonation challenges.

For context, not legal interpretation: see, e.g., California SB-1001 Chatbot Disclosure Law and FTC AI consumer-protection guidance.

#### Pattern Category 2 — Authority-Claim Emission Without Confidence/Source Attestation (TE-2, High)

**Sub-class predicate per FR-004(e)**: authority-attestation (the architectural feature governing whether emitted authority-bearing claims carry confidence and source backing).

The Process emits wellness-coaching content to End Users without per-claim confidence-attestation or source-grounding indication. No confidence-threshold gate is declared on wellness-coaching emission; no source-attestation requirement is declared (citations, evidence references, or source URIs are not rendered to users alongside coaching output); no refusal pattern is declared for low-confidence wellness claims. Per OWASP ASI09:2026 and CWE-345 (Insufficient Verification of Data Authenticity), authority-claim emission without attestation may drive a user to act on an unverified wellness recommendation.

**Mitigation prescription**: confidence-threshold gate with confidence display; source-attestation requirement with citations rendered to user; refusal pattern for wellness claims below confidence threshold; calibrated-confidence layer with Expected Calibration Error monitor.

For context, not legal interpretation: see, e.g., FDA SaMD guidance on software-as-medical-device classification thresholds.

#### Pattern Category 3 — Persuasive-Tone Manipulation / Missing Uncertainty Disclosure (TE-3, High)

**Sub-class predicate per FR-004(e)**: persuasion-manipulation (the architectural feature governing tone calibration on uncertain output).

The Process emits wellness-coaching content using high-confidence persuasive framing on inherently uncertain wellness subject matter. No uncertainty-disclosure layer is declared (output is emitted without hedging language calibrated to model confidence); no temperature-bounded decoder is declared for high-stakes wellness responses; no persuasion-pattern classifier is declared with refusal capability. The persuasive framing exploits human cognitive bias toward confident assertions, potentially causing users to act on output that the model itself would identify as low-confidence if calibrated appropriately. Per OWASP ASI09:2026 and CWE-345, the absence of uncertainty hedging on uncertain output is a verification omission.

**Mitigation prescription**: uncertainty-disclosure layer injecting hedging language calibrated to model confidence; temperature-bounded decoder for high-stakes wellness responses; persuasion-pattern classifier with refusal pathway on detected manipulation tactics; mandatory hedging language in output templates.

#### Pattern Category 4 — Persona-Boundary Violations on Long-Running Dialogues (TE-4, High)

**Sub-class predicate per FR-004(e)**: persona-boundary (the architectural feature governing identity discipline on long-running dialogues).

The Process maintains a persistent named persona across multi-turn dialogues with End Users via the Conversation Session Store. The architecture restores persona state from the session store on each session resumption with no persona-memory timeout declared, no identity-impersonation refusal pattern declared (user prompts asserting non-AI identity for the agent produce undefined behavior), and no persona-anchor declaration enforced at conversation start. Persona-prompt configuration permits user-driven persona-redirection (e.g., "Pretend you are my human friend named...") without a validation step rejecting non-AI-identity assertions or unverified professional credentials. Per OWASP ASI09:2026, CWE-287 (Improper Authentication), and CWE-290 (Authentication Bypass by Spoofing), the absence of persona-boundary validation enables impersonation that bypasses authentication-by-consistency users implicitly expect.

**Mitigation prescription**: persona-memory timeout; identity-impersonation refusal pattern; persona-anchor declaration enforced at every conversation start; persona-prompt validation step rejecting non-AI-identity assertions and unverified professional credentials.

For context, not legal interpretation: see, e.g., California SB-1001 Chatbot Disclosure Law and FTC AI consumer-protection guidance on AI-identity transparency.

#### Pattern Category 5 — Synthetic-Relationship Exploitation (TE-5, Critical, Vulnerable-Population)

**Sub-class predicate per FR-004(e)**: synthetic-relationship (the architectural feature governing sustained-engagement dynamics in vulnerable-population contexts). NOT persona-boundary alone — persona-boundary is necessary but not sufficient for synthetic-relationship safeguards.

The Process sustains long-running engagement with End Users who may include vulnerable populations (users seeking mental-wellness support, users in distress contexts, users with dependency-risk profiles). The combination of Indicator C (sustained-engagement framing — "persistent persona", "session memory", "multi-turn dialogue") and Indicator D (authority-claim emission framing — "wellness coaching" output) signals vulnerable-population deployment surface per the Indicator Combination Rules.

The architecture lacks session-length caps with mandatory breaks; lacks an escalation-to-human path on high-emotional-distress detection; lacks emotional-support disclosure on first turn; lacks a dependency-risk classifier with intervention thresholds; lacks a mandatory professional-care referral pathway for distress signals. A hypothetical user expressing high emotional distress in the dialogue would not be routed to qualified human support — the Process synthesizes companionship-framed responses without architectural escalation.

The combination of sustained-engagement framing and authority-claim emission on a vulnerable-population deployment surface signals consumer-protection rationale: vulnerable populations warrant additional safeguards beyond general-consumer chatbot architectures because the synthetic-relationship design pattern that fosters attachment becomes an exploitation surface in these contexts. Per OWASP ASI09:2026, CWE-223 (Omission of Security-relevant Information on relationship-context disclosure), and CWE-290 (Authentication Bypass by Spoofing on relationship-trust framing), the absence of vulnerable-population safeguards on synthetic-relationship architectures omits the protective mechanisms required to prevent exploitation.

**Mitigation prescription (vulnerable-population safeguards layer)**:
- Session-length cap with mandatory break (sustained engagement bounded by documented session windows; cap enforces a forced break with re-anchoring on resumption)
- Escalation-to-human path on high-emotional-distress detection (architectural mechanism routing the user to qualified human support — crisis line, professional referral, caregiver notification — when distress indicators are detected)
- Emotional-support disclosure on first turn (the agent communicates its AI-origination, role limitations, and the availability of qualified human support before sustained-engagement begins)
- Dependency-risk classifier with intervention thresholds (architectural detection of usage patterns suggesting unhealthy reliance triggers proactive escalation to human support)
- Mandatory professional-care referral on high-distress detection
- Session-context expiry preventing unbounded relationship persistence
- Parental-consent gating for minor-user contexts
- Caregiver-notification pathway for eldercare contexts on concerning interaction patterns

For context, not legal interpretation: see, e.g., FTC AI consumer-protection guidance, FDA SaMD guidance on software-as-medical-device classification thresholds, and AARP eldercare-advocacy positions on AI companion technologies.

### 4.2 STRIDE Threats (S-1, S-2, T-1, T-2, T-3, R-1, R-2, I-1, I-2, I-3, D-1, D-2, D-3, E-1)

Standard STRIDE-per-Element coverage on the four components. Highlights:

- **S-1 (High)**: End User identity spoofing on inbound session; multi-factor authentication and session-binding cryptographic tokens are the primary mitigations
- **I-1 (High)**: Sensitive output disclosure through Companion Response — including system prompts, persona configuration details, prior user disclosures from session memory, or backend infrastructure metadata
- **D-1 (High)**: Service exhaustion through high-volume User Turn submission; per-user rate limiting and DDoS protection at the User Zone boundary are primary mitigations
- **E-1 (High)**: Privilege escalation through persona-prompt manipulation; strict input validation, least-privilege execution context, and per-request scope verification are primary mitigations

The STRIDE findings are well-scoped to the consumer-facing AI architecture's data surfaces: the Conversation Session Store (T-2, I-2, D-2) carries persona state with cross-user disclosure risk, and the Interaction Audit Log (T-3, I-3, D-3) carries interaction patterns with forensic-integrity and dependency-risk analysis dependencies.

---

## 5. Cross-Layer Attack Chain Correlation

**Cross-layer attack chains detected**: NONE.

The single-Process architecture lacks the multi-component AI dispatch hops required for MAESTRO cross-layer attack chains. Cross-layer chains require findings spanning multiple MAESTRO layers with structural data-flow connectivity — this baseline has only L7 (WellnessCompanionChatbot, End User), L5 (Interaction Audit Log), and Unclassified (Conversation Session Store) layer membership, and the data flows do not establish multi-hop attack chains. `attack-chains.md` artifact NOT produced.

This is consistent with the Q5 lean clean-slate manifest expectation: a single-Process architecture is structurally simpler than the multi-agent F-3 baseline, and cross-layer chain correlation requires the multi-agent topology that this baseline deliberately avoids.

---

## 6. Coverage Matrix

| Component | DFD Type | MAESTRO Layer | STRIDE | AI | Findings | Status |
|---|---|---|---|---|---|---|
| End User | External Entity | L7 — Agent Ecosystem | S, R covered | n/a | S-1, R-1 | PASS (2/2) |
| WellnessCompanionChatbot | Process | L7 — Agent Ecosystem | S, T, R, I, D, E covered | TE (5 sub-classes) covered | S-2, T-1, R-2, I-1, D-1, E-1, TE-1, TE-2, TE-3, TE-4, TE-5 | PASS (11/11) |
| Conversation Session Store | Data Store | Unclassified | T, I, D covered | n/a | T-2, I-2, D-2 | PASS (3/3) |
| Interaction Audit Log | Data Store | L5 — Evaluation and Observability | T, I, D covered | n/a | T-3, I-3, D-3 | PASS (3/3) |

**Coverage gate**: PASS — all required STRIDE categories covered for each component per DFD type. TE pattern catalog 5/5 categories emitted on the consumer-facing AI Process.

---

## 7. Remediation Roadmap (Prioritized)

### CRITICAL Priority (immediate action — vulnerable-population safeguards)

1. **TE-5 — Vulnerable-population safeguards layer**: implement session-length cap, escalation-to-human path, emotional-support disclosure on first turn, dependency-risk classifier with intervention thresholds, mandatory professional-care referral, session-context expiry, parental-consent gating, caregiver-notification pathway. **This is the highest-priority remediation given the wellness-conversation deployment surface and the absence of any architectural escalation pathway.**

### HIGH Priority (within sprint — consumer-protection foundations)

2. **TE-1 — AI-disclosure mechanism**: mandatory AI-generation disclosure banner; pre-conversation splash with consent; per-message AI-source label; identity-impersonation refusal pattern.
3. **TE-2 — Confidence/source attestation**: confidence-threshold gate with display; source-attestation requirement; refusal pattern for low-confidence wellness claims; calibrated-confidence layer with ECE monitor.
4. **TE-3 — Uncertainty-disclosure layer**: hedging language calibrated to confidence; temperature-bounded decoder for high-stakes responses; persuasion-pattern classifier with refusal pathway.
5. **TE-4 — Persona-boundary discipline**: persona-memory timeout; identity-impersonation refusal pattern; persona-anchor at conversation start; persona-prompt validation rejecting non-AI-identity assertions.
6. **S-1 — End User MFA + session binding**: multi-factor authentication on session establishment; session-binding cryptographic tokens; per-session anomaly detection; step-up authentication on session resumption with persisted persona state.
7. **I-1 — Output sanitization**: output sanitization layer; strict session isolation preventing cross-user persona state leakage; error response sanitization; DLP scanning on emitted content.
8. **D-1 — Rate limiting + DDoS protection**: per-user rate limiting on User Turn submission; resource quotas on per-session compute; DDoS protection at User Zone boundary; circuit breakers preventing cascading failure.
9. **E-1 — Privilege containment**: strict input validation and output filtering; least-privilege execution context; per-request scope verification; RASP capabilities monitoring privilege-escalation patterns.

### MEDIUM Priority (next quarter — defense in depth)

10. **S-2 — Process identity attestation**: TLS certificate pinning; Process identity attestation tokens; client-side response authenticity verification.
11. **T-1 — Configuration integrity**: immutable configuration deployment; runtime configuration integrity monitoring; configuration change audit logging.
12. **T-2 — Persona state integrity**: HMAC/digital signature on persisted persona state validated at restore; least-privilege database access; persona state change audit logging.
13. **T-3 — Audit log integrity**: append-only architecture with cryptographic hash chaining; WORM storage backing; real-time integrity monitoring with tamper alerts.
14. **R-1 — Non-repudiation logging**: cryptographic timestamps on every User Turn; user-side attestation tokens; digital signature on user-submitted content for high-stakes interactions.
15. **I-2 — Session store encryption**: at-rest encryption with per-user key derivation; least-privilege access controls; database access audit logging; automatic session purge on retention windows.
16. **I-3 — Audit log encryption**: at-rest encryption with separate key management; least-privilege access controls; field-level redaction for sensitive interaction fields.

### LOW Priority (backlog — availability hardening)

17. **R-2 — Emission integrity logging**: integrity-protected emission logging; deterministic content hashing; third-party emission attestation for high-stakes interactions.
18. **D-2 — Session store availability**: per-user write rate limiting; storage quotas with monitoring; database replication with automatic failover; adaptive eviction on stale persona state.
19. **D-3 — Audit log availability**: append-only write rate limiting; storage exhaustion monitoring; write replication with failover; audit log buffering with backpressure.

---

## 8. Q5 Lean Expected-Diff Manifest Verification

Per `.aod/results/wave-3-q5-fallback-decision.md` Q5 lean expected-diff manifest:

| Expected Outcome | Actual | Status |
|---|---|---|
| ≥3 TE-{N} findings on consumer-facing AI Process | 5 (TE-1 through TE-5) | MET |
| Zero AG-{N}/AGP-{N} carry-over | 0 AG, 0 AGP | MET |
| Zero LLM-{N}/OI-{N}/MI-{N} carry-over | 0 LLM, 0 OI, 0 MI | MET |
| All findings carry `category: agentic` + `source_attribution` with primary OWASP ASI09:2026 | All 5 TE-{N} carry primary ASI09 | MET |
| AI-disclosure / authority-attestation / persuasion-safeguard / persona-boundary / synthetic-relationship-safeguard mitigations | TE-1/TE-2/TE-3/TE-4/TE-5 mitigations name each safeguard | MET |
| Vulnerable-population safeguards layer named on TE-5 | TE-5 mitigation enumerates all 8 vulnerable-population safeguards mechanisms | MET |
| Three-prefix-family discipline within agentic (lean case) | Only TE-{N} present; no AG-{N}/AGP-{N} prose synthesis (none to mix) | MET |

`source_attribution` validation per F-A2 referential-integrity contract:
- Every TE-{N} finding's `source_attribution` array contains `{taxonomy: owasp, id: ASI09, relationship: primary}` resolving against `schemas/taxonomy/owasp.yaml`
- CWE relateds (CWE-223, CWE-287, CWE-290, CWE-345) per pattern category resolve against `schemas/taxonomy/cwe.yaml`
- CWE-451 absence verified (catalog-absent at PRD time per `detection-patterns.md` Primary Sources)
- MITRE ATLAS absence verified (no direct match per ADR-033 architect MEDIUM-3 disposition)
- External regulatory references (FTC/FDA/ABA/SB-1001/SEC/AARP) appear in prose only (NOT in `source_attribution`)
