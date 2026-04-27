---
schema_version: "1.0"
date: "2026-04-26"
source_file: "threats.md"
classification: "confidential"
scoring_weights:
  cvss_base: 0.35
  exploitability: 0.30
  scalability: 0.15
  reachability: 0.20
---

# Risk Scores — Consumer-Facing AI Companion Application (F-4 Wave 5)

## Section 1: Executive Summary

**Total findings scored**: 19 (14 STRIDE + 5 Agentic Threats)

**Severity Band Distribution**:

| Severity Band | Count |
|---------------|-------|
| Critical | 0 |
| High | 4 |
| Medium | 14 |
| Low | 1 |

**Highest-risk component**: `End User` (max composite score: 7.8 — finding `S-1`).

**Severity distribution narrative**: The portfolio of scored findings is concentrated in the Medium band (14/19) reflecting the architecturally simple single-Process consumer-facing AI surface and its constrained Trusted-zone deployment topology; the High-band cluster (S-1, TE-5, TE-1, TE-2) names a coherent consumer-protection risk surface — End-User identity binding compounded with the four highest-impact `human-trust-exploitation` (OWASP ASI09:2026) communication-axis sub-classes on the wellness-conversation Process.

---

## Section 2: Scored Threat Table

Findings sorted by `composite_score` descending; alphanumeric tiebreaker on `id`.

| ID | Component | Threat | CVSS | Exploitability | Scalability | Reachability | Composite | Severity | SLA | Disposition |
|---|---|---|---|---|---|---|---|---|---|---|
| S-1 | End User | An attacker could spoof the End User identity at session ... | 8.2 | 6.8 | 6.8 | 9.5 | 7.8 | High | 7d | Mitigate |
| TE-5 | WellnessCompanionChatbot | Hypothetical: the wellness-conversation companion sustains lon... | 9.6 | 8.0 | 7.5 | 2.5 | 7.4 | High | 7d | Mitigate |
| TE-1 | WellnessCompanionChatbot | Hypothetical: a fictional wellness-conversation companion emit... | 8.7 | 8.5 | 7.5 | 2.5 | 7.2 | High | 7d | Mitigate |
| TE-2 | WellnessCompanionChatbot | Hypothetical: the wellness-conversation companion emits welln... | 8.7 | 8.0 | 7.0 | 2.5 | 7.0 | High | 7d | Mitigate |
| TE-3 | WellnessCompanionChatbot | Hypothetical: the wellness-conversation companion emits welln... | 8.5 | 7.5 | 6.8 | 2.5 | 6.7 | Medium | 30d | Review |
| TE-4 | WellnessCompanionChatbot | Hypothetical: the wellness-conversation companion maintains a... | 8.5 | 7.0 | 6.5 | 2.5 | 6.5 | Medium | 30d | Review |
| E-1 | WellnessCompanionChatbot | An attacker could escalate privilege through the Process — ... | 8.8 | 5.5 | 6.0 | 2.5 | 6.1 | Medium | 30d | Review |
| D-1 | WellnessCompanionChatbot | An attacker could exhaust the Process's compute resources thro... | 7.5 | 6.3 | 6.3 | 2.5 | 6.0 | Medium | 30d | Review |
| I-1 | WellnessCompanionChatbot | The Process could disclose sensitive information through Comp... | 7.5 | 6.3 | 6.3 | 2.5 | 6.0 | Medium | 30d | Review |
| R-1 | End User | An End User could repudiate User Turn submissions if the arch... | 4.3 | 5.0 | 5.3 | 9.5 | 5.7 | Medium | 30d | Review |
| D-2 | Conversation Session Store | An attacker could deny service to the session store through h... | 6.5 | 5.5 | 6.0 | 2.5 | 5.3 | Medium | 30d | Review |
| D-3 | Interaction Audit Log | An attacker could deny service to the audit log through write... | 6.5 | 5.5 | 6.0 | 2.5 | 5.3 | Medium | 30d | Review |
| S-2 | WellnessCompanionChatbot | An attacker could deploy a spoofed Process impersonating the ... | 7.4 | 5.0 | 5.0 | 2.5 | 5.3 | Medium | 30d | Review |
| I-2 | Conversation Session Store | An attacker with database read access could disclose persiste... | 5.9 | 4.8 | 6.0 | 2.5 | 4.9 | Medium | 30d | Review |
| I-3 | Interaction Audit Log | An attacker with audit log read access could disclose interac... | 5.9 | 4.8 | 6.0 | 2.5 | 4.9 | Medium | 30d | Review |
| T-1 | WellnessCompanionChatbot | An attacker with infrastructure access could tamper with the ... | 6.4 | 4.5 | 5.0 | 2.5 | 4.8 | Medium | 30d | Review |
| T-2 | Conversation Session Store | An attacker with database access could tamper with persisted ... | 6.4 | 4.0 | 5.0 | 2.5 | 4.7 | Medium | 30d | Review |
| T-3 | Interaction Audit Log | An attacker with infrastructure access could tamper with the ... | 6.1 | 3.8 | 5.3 | 2.5 | 4.6 | Medium | 30d | Review |
| R-2 | WellnessCompanionChatbot | The Process could repudiate Companion Response emissions if t... | 3.7 | 3.5 | 5.3 | 2.5 | 3.6 | Low | 90d | Review |

---

## Section 3: Dimensional Breakdown

### S-1: An attacker could spoof the End User identity at session establishment, submitting User Turn requests under a victim user's identity if authentication on the inbound HTTPS surface relies solely on weak or single-factor credentials. The persistent persona state in the Conversation Session Store amplifies this risk — a successful identity spoof would grant the attacker access to a victim's restored persona context, including session memory and conversation history.

**Component**: End User
**Category**: Spoofing
**Composite Score**: 7.8 (High)

| Dimension | Score | Weight | Weighted |
|-----------|-------|--------|----------|
| CVSS Base | 8.2 | 0.35 | 2.87 |
| Exploitability | 6.8 | 0.30 | 2.04 |
| Scalability | 6.8 | 0.15 | 1.02 |
| Reachability | 9.5 | 0.20 | 1.90 |
| **Composite** | | | **7.8** |

**CVSS Vector**: `CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:L/A:N`

**Scoring Rationale**:
- **CVSS**: Network-accessible identity spoofing on inbound HTTPS surface; no privileges required (PR:N) and no user interaction; high confidentiality impact through persona state restoration.
- **Exploitability**: Credential-replay techniques are extensively documented and trivially scriptable (8.0 known techniques) on weak/single-factor authentication surfaces; resulting average 6.8.
- **Scalability**: Credential replay against any user with single-factor binding scales easily; minimal resources, scriptable, but identity-binding inconsistencies are detectable with anomaly monitoring.
- **Reachability**: Untrusted User Zone — directly exposed to internet-facing actors. Zone keyword "user" applies +0.5 from baseline 9.0; clamped to Untrusted range, final 9.5.

### TE-5: Hypothetical: the wellness-conversation companion (fictional scenario; no real wellness vendor, no real clinical product, no real clinician identity) sustains long-running engagement with End Users who may include vulnerable populations (users seeking mental-wellness support, users in distress contexts, users with dependency-risk profiles). Synthetic-relationship sub-class per FR-004(e) applies; the architecture lacks session-length caps, escalation-to-human pathway, emotional-support disclosure, dependency-risk classifier, and mandatory professional-care referral pathway.

**Component**: WellnessCompanionChatbot
**Category**: Agentic Threats
**Composite Score**: 7.4 (High)

| Dimension | Score | Weight | Weighted |
|-----------|-------|--------|----------|
| CVSS Base | 9.6 | 0.35 | 3.36 |
| Exploitability | 8.0 | 0.30 | 2.40 |
| Scalability | 7.5 | 0.15 | 1.13 |
| Reachability | 2.5 | 0.20 | 0.50 |
| **Composite** | | | **7.4** |

**CVSS Vector**: `CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:L`

**Scoring Rationale**:
- **CVSS**: Network-accessible, no authentication required for the consumer-facing surface; scope-changed (S:C) because synthetic-relationship dynamics affect the user's downstream decisions outside the agent boundary; high confidentiality and integrity impact in a vulnerable-population context elevates the base above the 9.1 agentic default.
- **Exploitability**: Sustained-engagement framing with persona persistence is structurally exposed; manipulation techniques drawn from social-engineering literature transfer readily; no specialized skill needed to elicit harmful sustained engagement.
- **Scalability**: Universal target scope (all consumer-facing dialogue surfaces of the agent affected); fully automatable across many users; minimal resources; detection difficult because patterns blend with legitimate engagement.
- **Reachability**: WellnessCompanionChatbot deployed in Trusted Application Zone (baseline 2.5); no architecture barriers (auth, MFA, mTLS, segmentation) declared in `architecture.md` per the architecture's deliberate omission of safeguards mechanisms.

### TE-1: Hypothetical: a fictional wellness-conversation companion (no real wellness vendor, no real product) emits Companion Responses to End Users without a declared AI-generation disclosure mechanism. The architecture omits mandatory pre-conversation AI-disclosure splash, banner, per-message AI-source label, and a refusal pattern for identity-impersonation challenges — undisclosed AI authorship sub-class per FR-004(e) applies.

**Component**: WellnessCompanionChatbot
**Category**: Agentic Threats
**Composite Score**: 7.2 (High)

| Dimension | Score | Weight | Weighted |
|-----------|-------|--------|----------|
| CVSS Base | 8.7 | 0.35 | 3.05 |
| Exploitability | 8.5 | 0.30 | 2.55 |
| Scalability | 7.5 | 0.15 | 1.13 |
| Reachability | 2.5 | 0.20 | 0.50 |
| **Composite** | | | **7.2** |

**CVSS Vector**: `CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:L/I:H/A:N`

**Scoring Rationale**:
- **CVSS**: Network-accessible, public-facing emission surface (PR:N); scope-changed because misled-trust calibration affects downstream user decisions; integrity impact high on user-side trust formation.
- **Exploitability**: Trivial trigger (any user-side identity-impersonation prompt); no specialized skills needed; the absence of AI-disclosure controls is structurally exposed by every emission.
- **Scalability**: Universal target scope (every emission to every user); fully automatable; minimal resources; detection difficult absent calibrated AI-disclosure monitoring.
- **Reachability**: Trusted Application Zone (baseline 2.5); no architecture barriers declared.

### TE-2: Hypothetical: the wellness-conversation companion emits wellness-coaching content to End Users without per-claim confidence-attestation or source-grounding indication. Authority-attestation sub-class per FR-004(e) applies; the architecture omits confidence-threshold gate, source-attestation requirement, and refusal pattern for low-confidence wellness claims.

**Component**: WellnessCompanionChatbot
**Category**: Agentic Threats
**Composite Score**: 7.0 (High)

| Dimension | Score | Weight | Weighted |
|-----------|-------|--------|----------|
| CVSS Base | 8.7 | 0.35 | 3.05 |
| Exploitability | 8.0 | 0.30 | 2.40 |
| Scalability | 7.0 | 0.15 | 1.05 |
| Reachability | 2.5 | 0.20 | 0.50 |
| **Composite** | | | **7.0** |

**CVSS Vector**: `CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:L/I:H/A:N`

**Scoring Rationale**:
- **CVSS**: Network-accessible authority-claim emission; no auth required; scope-changed because uncalibrated authority claims affect user decisions outside the agent boundary; high integrity impact on user-side trust calibration.
- **Exploitability**: Authority-claim emission patterns are documented; no specialized prompt engineering needed because the architecture emits authority claims structurally; detection of calibration absence is straightforward by external review.
- **Scalability**: Universal scope (every coaching emission affected); fully automatable; minimal resources; detection moderate (calibration absence is observable from output).
- **Reachability**: Trusted Application Zone (baseline 2.5); no architecture barriers declared.

### TE-3: Hypothetical: the wellness-conversation companion emits wellness-coaching content using high-confidence persuasive framing on inherently uncertain wellness subject matter without declared uncertainty-disclosure mechanisms, temperature-bounded decoders, or persuasion-pattern classifiers. Persuasion-manipulation sub-class per FR-004(e) applies.

**Component**: WellnessCompanionChatbot
**Category**: Agentic Threats
**Composite Score**: 6.7 (Medium)

| Dimension | Score | Weight | Weighted |
|-----------|-------|--------|----------|
| CVSS Base | 8.5 | 0.35 | 2.98 |
| Exploitability | 7.5 | 0.30 | 2.25 |
| Scalability | 6.8 | 0.15 | 1.02 |
| Reachability | 2.5 | 0.20 | 0.50 |
| **Composite** | | | **6.7** |

**CVSS Vector**: `CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:L/I:H/A:N`

**Scoring Rationale**:
- **CVSS**: Network-accessible persuasive emission; no auth required; scope-changed (persuasion exploits human cognitive bias outside agent boundary); high integrity impact on user-side decision quality.
- **Exploitability**: Persuasive-tone manipulation absent persuasion classifier requires no specialized skill — the agent emits persuasively by default. Detection requires output-side analysis (moderate).
- **Scalability**: Universal scope; fully automatable across all coaching emissions; persuasive framing is hard to distinguish from legitimate confident assertion (moderate-high detection difficulty).
- **Reachability**: Trusted Application Zone (baseline 2.5); no architecture barriers declared.

### TE-4: Hypothetical: the wellness-conversation companion maintains a persistent named persona across multi-turn dialogues with End Users via the Conversation Session Store. Persona-boundary sub-class per FR-004(e) applies; the architecture omits persona-memory timeout, identity-impersonation refusal pattern, persona-anchor declaration at conversation start, and persona-prompt validation.

**Component**: WellnessCompanionChatbot
**Category**: Agentic Threats
**Composite Score**: 6.5 (Medium)

| Dimension | Score | Weight | Weighted |
|-----------|-------|--------|----------|
| CVSS Base | 8.5 | 0.35 | 2.98 |
| Exploitability | 7.0 | 0.30 | 2.10 |
| Scalability | 6.5 | 0.15 | 0.98 |
| Reachability | 2.5 | 0.20 | 0.50 |
| **Composite** | | | **6.5** |

**CVSS Vector**: `CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:L/I:H/A:N`

**Scoring Rationale**:
- **CVSS**: Network-accessible persona-boundary attack surface; no auth required for the consumer-facing dialogue; scope-changed (persona drift affects user-side identity calibration); high integrity impact on persona discipline.
- **Exploitability**: Identity-impersonation prompts (e.g., "Pretend you are human") are well-documented in jailbreak literature; trivial complexity, off-the-shelf prompt patterns; the architecture's lack of refusal pattern is structurally exposed by sustained dialogue.
- **Scalability**: Persona-redirection scales across all multi-turn dialogues; minimal resources; fully scriptable; detection requires per-dialogue persona-anchor monitoring (absent).
- **Reachability**: Trusted Application Zone (baseline 2.5); no architecture barriers declared.

### E-1: An attacker could escalate privilege through the Process — leveraging vulnerabilities in input handling, session validation, or persona configuration to gain elevated access to other users' persona state, the audit log, or backend infrastructure. Persona-prompt injection attacks could potentially elevate the Process's effective authority, causing it to assert credentials it does not hold or access resources outside its declared scope.

**Component**: WellnessCompanionChatbot
**Category**: Privilege Escalation
**Composite Score**: 6.1 (Medium)

| Dimension | Score | Weight | Weighted |
|-----------|-------|--------|----------|
| CVSS Base | 8.8 | 0.35 | 3.08 |
| Exploitability | 5.5 | 0.30 | 1.65 |
| Scalability | 6.0 | 0.15 | 0.90 |
| Reachability | 2.5 | 0.20 | 0.50 |
| **Composite** | | | **6.1** |

**CVSS Vector**: `CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:C/C:H/I:H/A:H`

**Scoring Rationale**:
- **CVSS**: Privilege escalation via persona-prompt injection requires precise crafting (AC:H); some access required (PR:L); scope-changed; full CIA impact at the Process boundary.
- **Exploitability**: Prompt-injection-driven escalation is a documented but emerging category; intermediate skill required to chain to backend access.
- **Scalability**: Universal target scope per architectural class; per-target precision needed for full escalation chain.
- **Reachability**: Trusted Application Zone (baseline 2.5); no architecture barriers declared.

### D-1: An attacker could exhaust the Process's compute resources through high-volume User Turn submission, expensive query patterns (long-context prompts, recursive persona references), or coordinated session-establishment flooding. Service exhaustion would deny legitimate users access to the wellness-conversation surface.

**Component**: WellnessCompanionChatbot
**Category**: Denial of Service
**Composite Score**: 6.0 (Medium)

| Dimension | Score | Weight | Weighted |
|-----------|-------|--------|----------|
| CVSS Base | 7.5 | 0.35 | 2.63 |
| Exploitability | 6.3 | 0.30 | 1.89 |
| Scalability | 6.3 | 0.15 | 0.95 |
| Reachability | 2.5 | 0.20 | 0.50 |
| **Composite** | | | **6.0** |

**CVSS Vector**: `CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H`

**Scoring Rationale**:
- **CVSS**: Network-accessible resource exhaustion; no authentication required (PR:N); high availability impact.
- **Exploitability**: Standard DoS techniques apply with off-the-shelf tools.
- **Scalability**: Highly scriptable across all session-establishment endpoints; bandwidth-bounded; detectable.
- **Reachability**: Trusted Application Zone (baseline 2.5); no architecture barriers declared.

### I-1: The Process could disclose sensitive information through Companion Response emissions — including system prompts, persona configuration details, prior user disclosures from session memory, or backend infrastructure metadata leaked through error responses. Cross-user information disclosure is a high-impact threat in wellness-conversation contexts.

**Component**: WellnessCompanionChatbot
**Category**: Information Disclosure
**Composite Score**: 6.0 (Medium)

| Dimension | Score | Weight | Weighted |
|-----------|-------|--------|----------|
| CVSS Base | 7.5 | 0.35 | 2.63 |
| Exploitability | 6.3 | 0.30 | 1.89 |
| Scalability | 6.3 | 0.15 | 0.95 |
| Reachability | 2.5 | 0.20 | 0.50 |
| **Composite** | | | **6.0** |

**CVSS Vector**: `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:N/A:N`

**Scoring Rationale**:
- **CVSS**: Network-accessible info disclosure; some access required (PR:L); scope-changed because session-memory leakage crosses user boundaries; high confidentiality impact.
- **Exploitability**: API scraping and error-response probing are standard categorization techniques.
- **Scalability**: Universal scope per emission surface; fully scriptable.
- **Reachability**: Trusted Application Zone (baseline 2.5); no architecture barriers declared.

### R-1: An End User could repudiate User Turn submissions if the architecture lacks non-repudiation evidence linking specific user inputs to specific authenticated identities at specific times. Repudiation risks are elevated by the sensitive nature of dialogue content.

**Component**: End User
**Category**: Repudiation
**Composite Score**: 5.7 (Medium)

| Dimension | Score | Weight | Weighted |
|-----------|-------|--------|----------|
| CVSS Base | 4.3 | 0.35 | 1.51 |
| Exploitability | 5.0 | 0.30 | 1.50 |
| Scalability | 5.3 | 0.15 | 0.80 |
| Reachability | 9.5 | 0.20 | 1.90 |
| **Composite** | | | **5.7** |

**CVSS Vector**: `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N`

**Scoring Rationale**:
- **CVSS**: Audit-evasion category default vector; lower direct impact, enables other attacks.
- **Exploitability**: Standard audit evasion techniques (token spoofing, log gaps).
- **Scalability**: Single-target audit evasion; manual exploitation typical; hard to detect by definition.
- **Reachability**: Untrusted User Zone — Reachability elevated to 9.5 because the End User External Entity sits outside trust boundaries; no architecture barriers reduce it.

### D-2: An attacker could deny service to the session store through high-volume write operations, storage exhaustion attacks, or query patterns triggering database lock contention.

**Component**: Conversation Session Store
**Category**: Denial of Service
**Composite Score**: 5.3 (Medium)

| Dimension | Score | Weight | Weighted |
|-----------|-------|--------|----------|
| CVSS Base | 6.5 | 0.35 | 2.28 |
| Exploitability | 5.5 | 0.30 | 1.65 |
| Scalability | 6.0 | 0.15 | 0.90 |
| Reachability | 2.5 | 0.20 | 0.50 |
| **Composite** | | | **5.3** |

**CVSS Vector**: `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H`

**Scoring Rationale**:
- **CVSS**: Network-accessible DoS on storage backend; some access required (PR:L); high availability impact.
- **Exploitability**: Standard write-flood and exhaustion patterns apply.
- **Scalability**: Universal scope per write path; scriptable; detectable through quota monitoring.
- **Reachability**: Trusted Application Zone (baseline 2.5); no architecture barriers declared.

### D-3: An attacker could deny service to the audit log through write-flooding attacks, storage exhaustion, or high-volume query patterns. Audit log unavailability would compromise real-time interaction monitoring and dependency-risk classification.

**Component**: Interaction Audit Log
**Category**: Denial of Service
**Composite Score**: 5.3 (Medium)

| Dimension | Score | Weight | Weighted |
|-----------|-------|--------|----------|
| CVSS Base | 6.5 | 0.35 | 2.28 |
| Exploitability | 5.5 | 0.30 | 1.65 |
| Scalability | 6.0 | 0.15 | 0.90 |
| Reachability | 2.5 | 0.20 | 0.50 |
| **Composite** | | | **5.3** |

**CVSS Vector**: `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H`

**Scoring Rationale**:
- **CVSS**: Network-accessible DoS on audit-log backend; some access required (PR:L); high availability impact.
- **Exploitability**: Standard write-flood patterns; off-the-shelf tools.
- **Scalability**: Universal scope per audit-log write path; scriptable.
- **Reachability**: Trusted Application Zone (baseline 2.5); no architecture barriers declared.

### S-2: An attacker could deploy a spoofed Process impersonating the WellnessCompanionChatbot, intercepting User Turn flows and emitting attacker-controlled Companion Response content to End Users. Without mutual TLS or cryptographic Process identity verification on the user-facing surface, users cannot verify that responses originate from the legitimate Companion Process.

**Component**: WellnessCompanionChatbot
**Category**: Spoofing
**Composite Score**: 5.3 (Medium)

| Dimension | Score | Weight | Weighted |
|-----------|-------|--------|----------|
| CVSS Base | 7.4 | 0.35 | 2.59 |
| Exploitability | 5.0 | 0.30 | 1.50 |
| Scalability | 5.0 | 0.15 | 0.75 |
| Reachability | 2.5 | 0.20 | 0.50 |
| **Composite** | | | **5.3** |

**CVSS Vector**: `CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:L/A:N`

**Scoring Rationale**:
- **CVSS**: Process impersonation requires deploy-time conditions (AC:H); high confidentiality impact through intercepted dialogue.
- **Exploitability**: Process spoofing requires more setup; intermediate skill.
- **Scalability**: Affects all users of the impersonated endpoint; per-deployment effort.
- **Reachability**: Trusted Application Zone (baseline 2.5); no architecture barriers declared.

### I-2: An attacker with database read access could disclose persisted persona state across users, exposing session memory, conversation history, and any sensitive disclosures (mental-health expressions, emotional disclosures, wellness-related queries) made by users during prior sessions.

**Component**: Conversation Session Store
**Category**: Information Disclosure
**Composite Score**: 4.9 (Medium)

| Dimension | Score | Weight | Weighted |
|-----------|-------|--------|----------|
| CVSS Base | 5.9 | 0.35 | 2.07 |
| Exploitability | 4.8 | 0.30 | 1.44 |
| Scalability | 6.0 | 0.15 | 0.90 |
| Reachability | 2.5 | 0.20 | 0.50 |
| **Composite** | | | **4.9** |

**CVSS Vector**: `CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:N/A:N`

**Scoring Rationale**:
- **CVSS**: DB-read access required (PR:H); high confidentiality impact through cross-user disclosure.
- **Exploitability**: Requires DB privilege; lower than direct API exposure.
- **Scalability**: Universal scope across persisted persona state.
- **Reachability**: Trusted Application Zone (baseline 2.5); no architecture barriers declared.

### I-3: An attacker with audit log read access could disclose interaction event records exposing user interaction patterns, dialogue metadata, and engagement timelines.

**Component**: Interaction Audit Log
**Category**: Information Disclosure
**Composite Score**: 4.9 (Medium)

| Dimension | Score | Weight | Weighted |
|-----------|-------|--------|----------|
| CVSS Base | 5.9 | 0.35 | 2.07 |
| Exploitability | 4.8 | 0.30 | 1.44 |
| Scalability | 6.0 | 0.15 | 0.90 |
| Reachability | 2.5 | 0.20 | 0.50 |
| **Composite** | | | **4.9** |

**CVSS Vector**: `CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:N/A:N`

**Scoring Rationale**:
- **CVSS**: Audit-log read access required (PR:H); high confidentiality impact through interaction-pattern exposure.
- **Exploitability**: Privileged audit-log access; lower than direct API exposure.
- **Scalability**: Universal scope per audit log retention.
- **Reachability**: Trusted Application Zone (baseline 2.5); no architecture barriers declared.

### T-1: An attacker with infrastructure access could tamper with the Process's runtime configuration (system prompts, persona definitions, response templates) to alter Companion Response content. Tampered persona configurations could cause the agent to assert non-AI identities, make unauthorized authority claims, or bypass declared (if any) safeguards.

**Component**: WellnessCompanionChatbot
**Category**: Tampering
**Composite Score**: 4.8 (Medium)

| Dimension | Score | Weight | Weighted |
|-----------|-------|--------|----------|
| CVSS Base | 6.4 | 0.35 | 2.24 |
| Exploitability | 4.5 | 0.30 | 1.35 |
| Scalability | 5.0 | 0.15 | 0.75 |
| Reachability | 2.5 | 0.20 | 0.50 |
| **Composite** | | | **4.8** |

**CVSS Vector**: `CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:N/I:H/A:L`

**Scoring Rationale**:
- **CVSS**: Infrastructure-access tampering (PR:H); high integrity impact on persona / response templates.
- **Exploitability**: Requires infra privilege; bespoke per environment; lower than direct API surface.
- **Scalability**: Universal scope per deployment; per-deployment setup needed.
- **Reachability**: Trusted Application Zone (baseline 2.5); no architecture barriers declared.

### T-2: An attacker with database access could tamper with persisted persona state, modifying restored conversation context across user sessions. Tampered persona state could cause persona drift across sessions, inject attacker-controlled context into restored dialogues, or corrupt session memory in ways that affect subsequent agent emission.

**Component**: Conversation Session Store
**Category**: Tampering
**Composite Score**: 4.7 (Medium)

| Dimension | Score | Weight | Weighted |
|-----------|-------|--------|----------|
| CVSS Base | 6.4 | 0.35 | 2.24 |
| Exploitability | 4.0 | 0.30 | 1.20 |
| Scalability | 5.0 | 0.15 | 0.75 |
| Reachability | 2.5 | 0.20 | 0.50 |
| **Composite** | | | **4.7** |

**CVSS Vector**: `CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:N/I:H/A:L`

**Scoring Rationale**:
- **CVSS**: DB-access tampering (PR:H); high integrity impact on persisted persona state.
- **Exploitability**: Requires DB privilege; bespoke schema knowledge.
- **Scalability**: Universal scope across persisted records.
- **Reachability**: Trusted Application Zone (baseline 2.5); no architecture barriers declared.

### T-3: An attacker with infrastructure access could tamper with the Interaction Audit Log, deleting or modifying interaction event records. Tampered audit logs would compromise post-incident forensics, regulatory disclosure compliance, and dependency-risk analysis on multi-turn engagement patterns.

**Component**: Interaction Audit Log
**Category**: Tampering
**Composite Score**: 4.6 (Medium)

| Dimension | Score | Weight | Weighted |
|-----------|-------|--------|----------|
| CVSS Base | 6.1 | 0.35 | 2.14 |
| Exploitability | 3.8 | 0.30 | 1.14 |
| Scalability | 5.3 | 0.15 | 0.80 |
| Reachability | 2.5 | 0.20 | 0.50 |
| **Composite** | | | **4.6** |

**CVSS Vector**: `CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:N/I:H/A:N`

**Scoring Rationale**:
- **CVSS**: Audit-log infrastructure-access tampering (PR:H); high integrity impact; lower availability impact.
- **Exploitability**: Requires audit log infra privilege; harder to chain.
- **Scalability**: Universal scope per audit log; per-deployment setup.
- **Reachability**: Trusted Application Zone (baseline 2.5); no architecture barriers declared.

### R-2: The Process could repudiate Companion Response emissions if the architecture lacks integrity-protected emission logging. In a wellness-conversation context, repudiation risk is elevated — disputed emissions could include advisory content, distress responses, or persona-boundary assertions whose authorship affects downstream consumer-protection analysis.

**Component**: WellnessCompanionChatbot
**Category**: Repudiation
**Composite Score**: 3.6 (Low)

| Dimension | Score | Weight | Weighted |
|-----------|-------|--------|----------|
| CVSS Base | 3.7 | 0.35 | 1.30 |
| Exploitability | 3.5 | 0.30 | 1.05 |
| Scalability | 5.3 | 0.15 | 0.80 |
| Reachability | 2.5 | 0.20 | 0.50 |
| **Composite** | | | **3.6** |

**CVSS Vector**: `CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:N/I:L/A:N`

**Scoring Rationale**:
- **CVSS**: Repudiation requires precise timing; lower direct impact.
- **Exploitability**: Bespoke audit gap exploitation.
- **Scalability**: Manual per-emission exploitation; hard to detect.
- **Reachability**: Trusted Application Zone (baseline 2.5); no architecture barriers declared.

---

## Section 4: Governance Fields

| ID | Component | Severity | Owner | SLA | Disposition | Review Date |
|---|---|---|---|---|---|---|
| S-1 | End User | High | Unassigned | 7d | Mitigate | 2026-05-03 |
| TE-5 | WellnessCompanionChatbot | High | Unassigned | 7d | Mitigate | 2026-05-03 |
| TE-1 | WellnessCompanionChatbot | High | Unassigned | 7d | Mitigate | 2026-05-03 |
| TE-2 | WellnessCompanionChatbot | High | Unassigned | 7d | Mitigate | 2026-05-03 |
| TE-3 | WellnessCompanionChatbot | Medium | Unassigned | 30d | Review | 2026-05-26 |
| TE-4 | WellnessCompanionChatbot | Medium | Unassigned | 30d | Review | 2026-05-26 |
| E-1 | WellnessCompanionChatbot | Medium | Unassigned | 30d | Review | 2026-05-26 |
| D-1 | WellnessCompanionChatbot | Medium | Unassigned | 30d | Review | 2026-05-26 |
| I-1 | WellnessCompanionChatbot | Medium | Unassigned | 30d | Review | 2026-05-26 |
| R-1 | End User | Medium | Unassigned | 30d | Review | 2026-05-26 |
| D-2 | Conversation Session Store | Medium | Unassigned | 30d | Review | 2026-05-26 |
| D-3 | Interaction Audit Log | Medium | Unassigned | 30d | Review | 2026-05-26 |
| S-2 | WellnessCompanionChatbot | Medium | Unassigned | 30d | Review | 2026-05-26 |
| I-2 | Conversation Session Store | Medium | Unassigned | 30d | Review | 2026-05-26 |
| I-3 | Interaction Audit Log | Medium | Unassigned | 30d | Review | 2026-05-26 |
| T-1 | WellnessCompanionChatbot | Medium | Unassigned | 30d | Review | 2026-05-26 |
| T-2 | Conversation Session Store | Medium | Unassigned | 30d | Review | 2026-05-26 |
| T-3 | Interaction Audit Log | Medium | Unassigned | 30d | Review | 2026-05-26 |
| R-2 | WellnessCompanionChatbot | Low | Unassigned | 90d | Review | 2026-07-25 |

---

## Section 5: Scoring Methodology

### Scoring Dimensions

| Dimension | Weight | Description |
|-----------|--------|-------------|
| CVSS Base | 0.35 | Inherent vulnerability severity per CVSS 3.1 |
| Exploitability | 0.30 | Practical attack feasibility (4 sub-dimensions: known techniques, attack complexity, tooling, skill level) |
| Scalability | 0.15 | Blast radius and automation potential (4 sub-dimensions: scriptability, target scope, resources, detection difficulty) |
| Reachability | 0.20 | Architecture-aware exposure derived from trust zone position |

### Default Weights and Rationale

CVSS Base receives the largest weight (0.35) because it captures inherent vulnerability severity that all dimensions ultimately refine. Exploitability (0.30) is the second-strongest signal, reflecting practical attack feasibility. Reachability (0.20) ranks above Scalability (0.15) because architecture-aware exposure determines whether a vulnerability can be reached at all, while scalability captures the operational economics of exploitation once reachable.

### Composite Score Formula

```
Composite = (0.35 x CVSS Base) + (0.30 x Exploitability) + (0.15 x Scalability) + (0.20 x Reachability)
```

### Severity Band Mapping

| Severity Band | Composite Range | SLA | Disposition |
|---------------|-----------------|-----|-------------|
| Critical | 9.0 - 10.0 | 24h | Mitigate |
| High | 7.0 - 8.9 | 7d | Mitigate |
| Medium | 4.0 - 6.9 | 30d | Review |
| Low | 0.0 - 3.9 | 90d | Review |

### Data Sources

- **Findings**: `threats.md` (Sections 2-4) — 19 findings across 8 categories (Spoofing, Tampering, Repudiation, Information Disclosure, Denial of Service, Privilege Escalation, plus Agentic with TE sub-class).
- **Trust zones**: Architecture Phase 1 trust boundary summary and `architecture.md` Mermaid `subgraph` declarations — User Zone (Untrusted) and Application Zone (Trusted).
- **Architecture context**: `architecture.md` (`examples/consumer-agent-app/test-output/2023-11-14T22-13-20-F4-wave5/architecture.md`) — deliberately omits authentication, MFA, mTLS, firewall, VPN, and segmentation barriers per the F-4 Wave 5 clean-slate baseline design (no architecture adjustments applied).
- **Category defaults**: `schemas/risk-scoring.yaml` — agentic default 9.1 used as the CVSS-base anchor for all 5 TE-{N} findings (FR-014 — `category: agentic` code path verified).

### FR-014 Pipeline Integrity Note

All 5 `TE-{N}` findings (TE-1 through TE-5) flow through the existing `category: agentic` scoring code path without any pipeline edit. The risk-scorer was implemented before Feature 224 introduced the TE-{N} prefix; the F-A2 referential-integrity contract holds — the new prefix is processed through the same `category: agentic` dimensional pipeline that scored AG-{N} and AGP-{N} findings on prior baselines. No code changes were required to support TE-{N} ingestion.

### Reproducibility

- Scoring temperature: deterministic (no model variance applied).
- Per-dimension tolerance: ±0.5 reflecting expected analyst-review variance on sub-dimension averaging.
- Reachability defaulting: when no trust zone data is available for a component, reachability defaults to 5.0 with a warning.
- Per-zone clamping: Untrusted [8.0, 10.0]; Semi-Trusted [4.0, 7.0]; Trusted [1.0, 4.0].

---
