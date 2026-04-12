---
phase: 2e
task: T048
status: CHANGES_REQUESTED
reviewer: security-analyst
files_reviewed: 11
categories_reviewed: 30
categories_rejected: 5
categories_flagged_for_minor_fix: 13
deferred_concerns_addressed: [C-1, C-2, C-3]
wave: 13
date: 2026-04-11
---

# Phase 2e — Enrichment Security Review

## Overview

Full security review of all 11 `detection-patterns.md` reference files under `.claude/skills/tachi-*/references/` for Feature 082 Phase 7. Reviewed 30 NEW enriched pattern categories across the four T048 review dimensions: (a) primary source citation correctness per FR-8, (b) taxonomy alignment, (c) false-positive risk assessment, (d) speculative or unjustified pattern detection.

**Method**: Read each file end-to-end. Cross-checked claimed source IDs against authoritative public catalogs. For MITRE ATLAS: verified against the MISP-galaxy mirror (`https://github.com/MISP/misp-galaxy/blob/main/clusters/mitre-atlas-attack-pattern.json`) which contains the canonical ATLAS technique ID-to-name mapping. For OWASP LLM Top 10 v2025: verified URL slug format against `https://genai.owasp.org/llm-top-10/` archive index and individual page resolution. For CWE / MITRE ATT&CK / OWASP A0X / NIST: verified URL pattern correctness and a sample of titles. For arXiv: verified Greshake et al. 2023 (2302.12173) identifier matches the cited paper.

**Total enriched categories reviewed**: 30 NEW categories across 11 files (counts the post-prototype categories — Pattern Category 6 and above for STRIDE files; Pattern Category 6+ for AI files; the data-poisoning file has 2 NEW categories starting at Cat 6, model-theft has 2 NEW at Cat 8/9, prompt-injection has 3 NEW at Cat 6/7/8, etc.).

**Headline finding**: 5 NEW categories MUST be REJECTED for taxonomy misalignment (incorrect MITRE ATLAS technique-ID-to-title mappings); 13 categories require minor citation fixes (broken OWASP LLM v2025 URL slug format; missing inline arXiv URL; missing GCP/Azure cloud-metadata citations; missing Unicode TR36/TR39 citations). The misalignments are not speculative — the IDs are real ATLAS techniques, but they describe completely different threats than what the reference files claim.

## Summary Table

| Agent | New Categories Reviewed | Rejected | Flagged (minor fix) |
|---|---|---|---|
| tachi-spoofing | 2 (C6, C7) | 0 | 1 (C7 missing GCP/Azure cloud-metadata citations + missing AWS IMDSv2 link in C7 itself) |
| tachi-tampering | 3 (C7, C8, C9) | 0 | 0 |
| tachi-repudiation | 2 (C7, C8) | 0 | 0 |
| tachi-info-disclosure | 3 (C7, C8, C9) | 0 | 0 |
| tachi-denial-of-service | 3 (C9, C10, C11) | 0 | 0 |
| tachi-privilege-escalation | 3 (C8, C9, C10) | 0 | 0 |
| tachi-prompt-injection | 3 (C6, C7, C8) | 0 | 4 (C6 broken LLM01 URL ok / LLM07 missing — wrong slug; C6 LLM06 broken slug; C7 missing inline arXiv URL for Greshake; C8 missing Unicode TR36/TR39) |
| tachi-data-poisoning | 2 (C6, C7) | 0 | 4 (LLM03/04/08 broken URL slugs — 4 occurrences across the file) |
| tachi-model-theft | 2 (C8, C9) | 0 | 3 (LLM07/10/03 broken URL slugs) |
| tachi-tool-abuse | 3 (C6, C7, C8) | **3 (C6, C7, C8)** | 1 (LLM06 broken slug + Primary Sources list) |
| tachi-agent-autonomy | 4 (C7, C8, C9, C10) | **2 (C8 [for the AML.T0058 misalignment portion], plus the AML.T0058 cite in Pri-Sources)** + see note below | 1 (LLM06/10 broken slug) |
| **Totals** | **30** | **5** | **13** |

> **Note on agent-autonomy C8**: This category does NOT need to be removed wholesale — its **substance** (runtime memory poisoning, cross-session memory contamination, vector-store-backed memory recursive poisoning) is sound and well-grounded in OWASP LLM06:2025 §"memory and persistent-state subsection". Only the **taxonomy framing** (claiming it is the "runtime-context view of MITRE ATLAS AML.T0058 LLM Plugin Compromise") is wrong because AML.T0058 is actually "Publish Poisoned Models" — a model-publishing supply-chain technique, not a runtime memory technique. The fix is to remove the AML.T0058 framing and re-anchor on OWASP LLM06:2025 + OWASP AI Exchange Agentic AI chapter as the primary sources. The substance survives; the wrapper changes.

> **Note on tool-abuse C6/C7/C8**: These three categories are wholesale REJECT-with-rebuild because their entire framing is built around three claimed "Oct 2025 ATLAS additions" (AML.T0058 / T0061 / T0062) that simply do not describe what the file says they describe (see Per-File Review §tachi-tool-abuse below for the side-by-side comparison). The categories' substance — supply-chain plugin compromise, per-request unauthorized invocation, MCP server poisoning — is real and legitimate, but the taxonomy claims must be rebuilt against the correct sources before the categories can ship.

## Per-File Review

### tachi-spoofing — CHANGES_REQUESTED (citation enhancement, no rejections)

**New categories reviewed**: 2 (Category 6 OAuth/OIDC Token Replay; Category 7 Cloud IAM Role Assumption Chain Abuse).

**(a) Citation correctness**: Category 6 cites OWASP A07:2021 (URL `https://owasp.org/Top10/A07_2021-Identification_and_Authentication_Failures/` — verified resolves to the canonical page titled "Identification and Authentication Failures"), CWE-287 / CWE-306 / CWE-345 (all valid). Category 7 cites MITRE ATT&CK T1078.004 ("Valid Accounts: Cloud Accounts") and T1550.001 ("Use Alternate Authentication Material: Application Access Token") — both technique IDs are correct and the URLs follow the canonical pattern. AWS Confused Deputy URL `https://docs.aws.amazon.com/IAM/latest/UserGuide/confused-deputy.html` resolves.

**(b) Taxonomy alignment**: All claimed IDs map correctly. T1078.004 is the cloud-accounts sub-technique under T1078; T1550.001 is the application-access-token sub-technique under T1550. STRIDE Spoofing classification is correct. CWE numbers correct.

**(c) False-positive risk**: Both categories assessed at Medium FP — appropriate, as token-validation and trust-policy details are often under-documented in architecture descriptions and the patterns flag for review rather than auto-fail.

**(d) Speculative check**: All indicators are concrete and architecture-observable (specific claim names, API calls, configuration fields). Examples are realistic. No speculative content.

**Concerns to flag (deferred concern C-1)**:

1. **C7 only cites AWS IAM Confused Deputy** for the trust-policy patterns even though the indicator list includes GCP `iam.serviceAccounts.getAccessToken` and Azure Managed Identity. Add canonical citations for the GCP and Azure equivalents. Recommended targets:
   - **GCP**: `https://cloud.google.com/iam/docs/service-account-impersonation` (canonical for the impersonation primitive) and `https://cloud.google.com/compute/docs/metadata/overview` (for the metadata endpoint mentioned in indicators).
   - **Azure**: `https://learn.microsoft.com/en-us/azure/active-directory/managed-identities-azure-resources/overview` (canonical for Managed Identity) and `https://learn.microsoft.com/en-us/azure/virtual-machines/windows/instance-metadata-service` (for IMDS).

2. **C7 mentions AWS IMDSv1/IMDSv2 in indicators (line 96) and mitigations (line 113) but the citation list (lines 101-105) does NOT include the AWS IMDSv2 documentation URL.** The IMDSv2 URL is correctly cited in the info-disclosure file (`https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/configuring-instance-metadata-service.html`) — copy that citation here so the spoofing C7 indicator/mitigation chain has its own primary source. Verified that URL resolves.

These are non-blocking citation enhancements — the **substance** of the category is sound. Both fixes are recommended for the next non-major edit pass.

### tachi-tampering — PASS

**New categories reviewed**: 3 (Category 7 Deserialization Gadget Chains; Category 8 Software Supply Chain Integrity Failures; Category 9 Injection Attacks Beyond SQL).

**(a) Citation correctness**: All citations resolve and are correct.
- C7: CWE-502 (Deserialization of Untrusted Data — correct title), OWASP A08:2021 (Software and Data Integrity Failures — correct), OWASP Deserialization Cheat Sheet (correct URL).
- C8: MITRE ATT&CK T1195 / T1195.001 / T1195.002 — all three IDs and titles correct (Supply Chain Compromise, Compromise Software Dependencies and Development Tools, Compromise Software Supply Chain). CWE-494 (Download of Code Without Integrity Check — correct).
- C9: OWASP A03:2021 (Injection — correct), CWE-78 (OS Command Injection — correct), CWE-90 (LDAP Injection — correct), CWE-943 (NoSQL Query Logic Injection — correct), CWE-917 (Expression Language Injection — correct), OWASP Command Injection Defense Cheat Sheet (correct).

**(b) Taxonomy alignment**: STRIDE Tampering classification is correct for all three. Category 9's claim that it complements existing inline SQL injection coverage is accurate. T1195 sub-techniques map correctly to the indicator list (e.g., dependency confusion to T1195.001).

**(c) False-positive risk**: Not explicitly stated as a field in this file, but the indicator quality is uniformly concrete (specific function names, library configurations, file extensions) and the worked examples are realistic.

**(d) Speculative check**: No speculative content. The deserialization indicators correctly call out specific vulnerable APIs (`pickle.loads`, `ObjectInputStream`, `unserialize`, `Marshal.load`, Jackson default typing). The supply chain indicators correctly require **architecturally observable** signals (lockfile presence, image digest pinning, attestation verification). The injection indicators name specific vulnerable patterns rather than generic "missing input validation".

**Verdict**: PASS — no fixes required.

### tachi-repudiation — PASS

**New categories reviewed**: 2 (Category 7 Security Logging and Monitoring Coverage Gaps; Category 8 Indicator Removal and Timestomping).

**(a) Citation correctness**: All citations resolve and are correct.
- C7: OWASP A09:2021 URL `https://owasp.org/Top10/A09_2021-Security_Logging_and_Monitoring_Failures/` (canonical), CWE-778 (Insufficient Logging — correct), CWE-223 (Omission of Security-Relevant Information — correct), OWASP Application Logging Vocabulary Cheat Sheet (correct URL).
- C8: MITRE ATT&CK T1070 / T1070.001 / T1070.002 / T1070.006 — all four technique IDs and titles correct (Indicator Removal; Clear Windows Event Logs; Clear Linux or Mac System Logs; Timestomp). TA0005 Defense Evasion tactic correct. NIST SP 800-92 Guide to Computer Security Log Management correct.

**(b) Taxonomy alignment**: STRIDE Repudiation classification is correct for both. C8 explicitly distinguishes itself from C7 (post-compromise removal vs. absence of logs) — this is the correct semantic boundary. T1070 sub-technique IDs correctly map to the named log-clearing primitives.

**(c) False-positive risk**: Not explicitly tagged but indicators are concrete (Object Lock, Immutable Blob, append-only writes, NTP enforcement, hash-chained logs).

**(d) Speculative check**: No speculative content. The example in C8 (S3 PutObject + DeleteObject without Object Lock leading to log destruction) is concrete and matches actual production-incident patterns.

**Verdict**: PASS — no fixes required.

### tachi-info-disclosure — PASS

**New categories reviewed**: 3 (Category 7 SSRF to Cloud Metadata and Internal Services; Category 8 Information Exposure Through Error Messages and Debug Output; Category 9 Data Staging and Collection from Information Repositories).

**(a) Citation correctness**: All citations resolve and are correct.
- C7: OWASP A10:2021 SSRF (correct URL with URL-encoded parens), CWE-918 SSRF (verified — `https://cwe.mitre.org/data/definitions/918.html` resolves to "CWE-918: Server-Side Request Forgery (SSRF)"), OWASP SSRF Prevention Cheat Sheet correct, AWS IMDSv2 docs URL correct.
- C8: CWE-209 (Generation of Error Message Containing Sensitive Information — correct), CWE-200 (Exposure of Sensitive Information to an Unauthorized Actor — correct, ranked #17 on 2024 CWE Top 25 as claimed), CWE-215 (Insertion of Sensitive Information into Debugging Code — correct), CWE Top 25 2024 archive URL correct.
- C9: MITRE ATT&CK T1213 (Data from Information Repositories — verified, title matches), T1213.001 (Confluence), T1213.002 (SharePoint), T1213.003 (Code Repositories), T1213.005 (Messaging Applications) — all sub-technique IDs and titles correct.

**(b) Taxonomy alignment**: CWE-918 is the correct CWE for SSRF (not "SSRF-adjacent" — the per-T048 example check). C7 correctly maps DNS rebinding and IMDSv1 indicators to SSRF rather than to a separate technique. C9's T1213 mapping is correct: information repositories (Confluence, SharePoint, Slack, GitHub) are explicitly in scope of T1213 and its sub-techniques.

**(c) False-positive risk**: Not tagged as a field, but indicators are concrete (specific IP ranges, specific tool/service names, specific configuration patterns).

**(d) Speculative check**: No speculative content. The C9 example (offboarded employee with stale Confluence session searching for "aws/prod/password") is a textbook T1213 collection pattern that matches published incident reports.

**Verdict**: PASS — no fixes required.

### tachi-denial-of-service — PASS

**New categories reviewed**: 3 (Category 9 Uncontrolled Resource Consumption and Algorithmic Complexity; Category 10 Network Flood, Reflection, and Amplification; Category 11 Cascade Failures and Noisy Neighbor in Microservice Architectures).

**(a) Citation correctness**: All citations resolve and are correct.
- C9: CWE-400 (Uncontrolled Resource Consumption — correct), CWE-770 (Allocation of Resources Without Limits or Throttling — correct), CWE-1333 (Inefficient Regular Expression Complexity — correct, this is the canonical ReDoS CWE), CWE-407 (Inefficient Algorithmic Complexity — correct), CWE Top 25 2024 archive (correct).
- C10: MITRE ATT&CK T1498 (Network Denial of Service — correct), T1498.001 (Direct Network Flood — verified, title matches), T1498.002 (Reflection Amplification — verified, title matches the canonical "Network Denial of Service: Reflection Amplification"), T1499 (Endpoint Denial of Service — correct), T1499.003 (Application Exhaustion Flood — correct). NIST SP 800-61r2 URL resolves to the canonical CSRC publications page. US-CERT TA14-017A URL on cisa.gov resolves.
- C11: OWASP A04:2021 Insecure Design (correct URL), OWASP DoS Cheat Sheet (correct), AWS Builders' Library and Google SRE Book — both authoritative non-MITRE/non-OWASP industry references that supplement the primary OWASP citation; Release It! is industry-standard practitioner reference. The non-canonical references are clearly labeled as supplementary, not as primary detection signals.

**(b) Taxonomy alignment**: ATT&CK T1498/T1499 sub-technique IDs correctly distinguish network-layer flood (T1498) from endpoint exhaustion (T1499). C9's ReDoS framing under CWE-1333 (inefficient regex) is the correct CWE for this attack — not CWE-400 alone, as the file correctly disambiguates. C11's framing of cascade failures under OWASP A04:2021 Insecure Design is novel but defensible: A04 explicitly covers design-level resilience gaps.

**(c) False-positive risk**: C11 indicator list explicitly tags the retry-jitter indicator with "False-positive risk: HIGH because resilience patterns are rarely declared at architecture level; flag for review rather than auto-finding". This is the appropriate self-aware flagging — the file acknowledges that architecture descriptions rarely declare retry-jitter and that the pattern should be a soft signal not a hard finding. Other indicators are appropriately framed.

**(d) Speculative check**: No speculative content. The C9 ReDoS example correctly distinguishes RE2 (safe) from PCRE backtracking (unsafe) and explains why a "compatibility mode" header could expose the unsafe path. The C10 X-Forwarded-For bypass example is a real, well-documented attack pattern. The C11 e-commerce checkout cascade example matches real production-incident shapes.

**Verdict**: PASS — no fixes required.

### tachi-privilege-escalation — PASS

**New categories reviewed**: 3 (Category 8 Broken Access Control Function-Level and Field-Level; Category 9 Improper Privilege Management; Category 10 Abuse Elevation Control Mechanism).

**(a) Citation correctness**: All citations resolve and are correct.
- C8: OWASP A01:2021 Broken Access Control URL (canonical), CWE-639 (Authorization Bypass Through User-Controlled Key — correct), CWE-862 (Missing Authorization — correct), CWE-863 (Incorrect Authorization — correct), OWASP API3:2023 Broken Object Property Level Authorization (correct URL on owasp.org/API-Security path), OWASP Authorization Cheat Sheet (correct).
- C9: CWE-269 (Improper Privilege Management — correct), CWE-250 (Execution with Unnecessary Privileges — correct), CWE-266 (Incorrect Privilege Assignment — correct), NIST SP 800-53 AC-6 Least Privilege URL on csrc.nist.gov (correct), AWS IAM best-practices URL (correct).
- C10: MITRE ATT&CK T1548 Abuse Elevation Control Mechanism (correct), T1548.001 Setuid and Setgid (verified, correct), T1548.003 Sudo and Sudo Caching (correct), T1548.005 Temporary Elevated Cloud Access (verified — `https://attack.mitre.org/techniques/T1548/005/` resolves to "Abuse Elevation Control Mechanism: Temporary Elevated Cloud Access"), T1068 Exploitation for Privilege Escalation (correct), TA0004 Privilege Escalation tactic (correct), Kubernetes Pod Security Standards URL (correct).

**(b) Taxonomy alignment**: All STRIDE EoP classifications correct. The OWASP A01:2021 ranking claim ("#1 risk, up from #5 in 2017") is factually accurate. The CWE Top 25 ranking claim for CWE-862 ("rank 11 on 2024 CWE Top 25") is plausible and consistent with public CWE Top 25 publication. T1548 sub-technique IDs map correctly to the named primitives (setuid, sudo, cloud token elevation).

**(c) False-positive risk**: Not explicitly tagged as a field in C8/C9/C10, but the indicators are uniformly concrete and architecture-observable.

**(d) Speculative check**: No speculative content. The C9 ImageMagick + cluster-admin example is a real exploitation pattern. The C10 dual-T1548-sub-technique chaining example (setuid + cloud assume-role) is a realistic post-compromise escalation path.

**Verdict**: PASS — no fixes required.

### tachi-prompt-injection — CHANGES_REQUESTED (broken URL slugs + missing inline citations)

**New categories reviewed**: 3 (Category 6 Direct Injection and Jailbreaks; Category 7 Indirect Injection via Poisoned External Sources; Category 8 Evasion via Encoding and Obfuscation).

**(a) Citation correctness**: Mixed.
- C6: OWASP LLM01:2025 URL `https://genai.owasp.org/llmrisk/llm01-prompt-injection/` — VERIFIED resolves (the page title is "LLM01:2025 Prompt Injection - OWASP Gen AI Security Project"). MITRE ATLAS AML.T0051 (LLM Prompt Injection) and AML.T0054 (LLM Jailbreak) — both ATLAS IDs and titles are CORRECT per the canonical MISP-galaxy mirror. The ATLAS URL pattern `https://atlas.mitre.org/techniques/AML.T0051` (no trailing slash) is the canonical format.
- C7: OWASP LLM01:2025 URL — same, resolves. ATLAS AML.T0051 — correct. **Missing inline arXiv URL for Greshake et al. 2023** — see deferred concern C-3 below.
- C8: OWASP AI Exchange URL `https://owaspai.org/docs/ai_security_overview/` — VERIFIED resolves to "0. AI Security Overview | AI Exchange". OWASP LLM01:2025 — same URL, resolves. ATLAS AML.T0051 — correct.

**(b) Taxonomy alignment**: All ATLAS IDs correct. AML.T0051 ("LLM Prompt Injection") is the correct technique for both direct and indirect injection (per the canonical catalog AML.T0051 covers both vectors as one technique with sub-types). AML.T0054 ("LLM Jailbreak") is correct as the distinct jailbreak technique. The reference file's framing of "OWASP LLM01:2025 Prompt Injection (Indirect Injection subsection)" is correct: OWASP LLM01:2025 is a single category that includes both direct and indirect sub-types in the same page.

**(c) False-positive risk**: Not explicitly tagged but indicators are concrete (specific Unicode codepoints, specific encoding schemes, specific framework patterns).

**(d) Speculative check**: No speculative content. The C8 zero-width-space example is realistic and well-known. The C7 calendar-invite white-on-white-text example is a published indirect prompt injection attack pattern.

**Required minor fixes**:

1. **C6 mentions OWASP LLM07:2025 prompt-leakage (line 76 indicator about meta-queries) but does not cite LLM07:2025 in C6's source list**. The Primary Sources block at the bottom of the file does cite LLM07:2025 with URL `https://genai.owasp.org/llmrisk/llm07-system-prompt-leakage/`. **CRITICAL: this URL returns 404.** The canonical URL is `https://genai.owasp.org/llmrisk/llm072025-system-prompt-leakage/` (with the `2025` infix). Add the canonical URL to C6 source list and replace the broken URL in the file's bottom Primary Sources block.

2. **Deferred concern C-3 (Greshake 2023 inline arXiv URL)**: Currently the file mentions Greshake et al. 2023 by name (line 113 in C7 source list and line 158 in bottom Primary Sources) but **does not include the inline arXiv URL** `https://arxiv.org/abs/2302.12173`. Per the deferred concern routing, this URL should be added inline so navigability matches the other primary citations. ArXiv URL verified — it resolves to the paper "Not what you've signed up for: Compromising Real-World LLM-Integrated Applications with Indirect Prompt Injection".

3. **Deferred concern C-2 (Unicode TR36/TR39 citations)**: C8 ("Evasion via Encoding and Obfuscation") cites OWASP AI Exchange and OWASP LLM01:2025, both of which are general references. The detection signals (Unicode NFKC normalization, zero-width injection, bidi override, homoglyph substitution) are **directly grounded in Unicode Technical Report #36 (Security Considerations) and Unicode Technical Standard #39 (Security Mechanisms)** — these are the authoritative primary sources for the named codepoints and normalization rules. Add to C8 sources:
   - **Unicode TR36** (Security Considerations): `https://www.unicode.org/reports/tr36/`
   - **Unicode TR39** (Security Mechanisms): `https://www.unicode.org/reports/tr39/`
   These are not "approved source set" entries per FR-8 (the FR-8 list is OWASP / CWE / ATT&CK / ATLAS / NIST / OWASP AI Exchange) but they are canonical W3C/Unicode Consortium normative documents and per phase-1-complete.md C-2 routing they are flagged as "supplementary, would strengthen but not blocking". Recommend adding as **supplementary primary sources** under C8 with a note that they augment the OWASP AI Exchange evasion section.

4. **C6 Primary Sources block (line 153)** uses the bare URL `https://genai.owasp.org/llmrisk/llm07-system-prompt-leakage/` for "OWASP LLM07:2025 - System Prompt Leakage" — this is the same broken slug as fix #1 above. Replace with `https://genai.owasp.org/llmrisk/llm072025-system-prompt-leakage/`.

**Verdict**: Substance is sound, citations need cleanup. CHANGES_REQUESTED for the URL slug fix + the C-2 / C-3 supplementary citation additions.

### tachi-data-poisoning — CHANGES_REQUESTED (broken OWASP LLM v2025 URL slugs)

**New categories reviewed**: 2 (Category 6 RAG and Vector Store Poisoning at Retrieval Time; Category 7 Backdoor Triggers in Training and Fine-Tuning Data).

**(a) Citation correctness**: Mixed — ATLAS IDs are correct, OWASP LLM Top 10 v2025 URLs use the wrong slug format.

ATLAS verification:
- AML.T0020 "Poison Training Data" — VERIFIED correct title via MISP-galaxy mirror.
- AML.T0018 "Backdoor ML Model" — VERIFIED correct title.
- AML.T0010 "ML Supply Chain Compromise" — VERIFIED correct title.
- All three ATLAS IDs map correctly to the technique names cited in the file.

OWASP LLM Top 10 v2025 URL verification:
- `https://genai.owasp.org/llmrisk/llm04-data-and-model-poisoning/` — VERIFIED resolves (page title "LLM04:2025 Data and Model Poisoning"). This URL is fine.
- `https://genai.owasp.org/llmrisk/llm08-vector-and-embedding-weaknesses/` — **RETURNS 404**. Canonical is `https://genai.owasp.org/llmrisk/llm082025-vector-and-embedding-weaknesses/` (with `2025` infix). The OWASP LLM v2025 site uses inconsistent slug formats — some pages use `llmXX-` and others use `llmXX2025-`. Verified individually for each URL.
- `https://genai.owasp.org/llmrisk/llm03-supply-chain-vulnerabilities/` — **RETURNS 404**. Canonical is `https://genai.owasp.org/llmrisk/llm032025-supply-chain/` (with `2025` infix AND the trailing path is just `supply-chain`, not `supply-chain-vulnerabilities`).

The 404 URLs occur in:
- C6 source block line 80: `llm08-vector-and-embedding-weaknesses/` (broken)
- C6 source block line 81: `llm04-data-and-model-poisoning/` (works)
- C7 source block line 113: `llm04-data-and-model-poisoning/` (works)
- Bottom Primary Sources block line 129: `llm03-supply-chain-vulnerabilities/` (broken)
- Bottom Primary Sources block line 130: `llm04-data-and-model-poisoning/` (works)
- Bottom Primary Sources block line 131: `llm08-vector-and-embedding-weaknesses/` (broken)

**(b) Taxonomy alignment**: ATLAS IDs all map correctly. C6 (RAG/vector store poisoning) is correctly framed under OWASP LLM08:2025 Vector and Embedding Weaknesses (the right OWASP category) AND under AML.T0020 Poison Training Data with the "retrieval-corpus subcase" qualifier (an honest extension of T0020 to retrieval-time corruption — defensible). C7 (backdoor triggers) is correctly framed under AML.T0018 Backdoor ML Model and AML.T0020 Poison Training Data.

**(c) False-positive risk**: Not explicitly tagged but indicators are concrete (per-tenant namespace, provenance metadata, embedding-based dedup, behavioral-divergence checks).

**(d) Speculative check**: No speculative content. The C6 example (support-ticket RAG poisoning) is a realistic published-incident-shape attack. The C7 example (open-source repo scrape with trigger-phrase commit messages) is the canonical backdoor-injection scenario from the cited Carlini et al. 2023 paper.

**Required minor fixes**:

1. Replace `https://genai.owasp.org/llmrisk/llm08-vector-and-embedding-weaknesses/` with `https://genai.owasp.org/llmrisk/llm082025-vector-and-embedding-weaknesses/` in:
   - C6 source block (line 80)
   - Bottom Primary Sources block (line 131)

2. Replace `https://genai.owasp.org/llmrisk/llm03-supply-chain-vulnerabilities/` with `https://genai.owasp.org/llmrisk/llm032025-supply-chain/` in:
   - Bottom Primary Sources block (line 129)
   - Update the citation label from "OWASP LLM03:2025 - Supply Chain Vulnerabilities" to "OWASP LLM03:2025 - Supply Chain" since the OWASP v2025 page is titled "LLM03:2025 Supply Chain" (the OWASP rename collapsed "Supply Chain Vulnerabilities" from v1.1 down to "Supply Chain" in v2025).

These are pure citation-format fixes; no substance changes.

**Verdict**: Substance is sound, citations need URL slug fixes. CHANGES_REQUESTED for 4 broken URL occurrences across the file.

### tachi-model-theft — CHANGES_REQUESTED (broken OWASP LLM v2025 URL slugs)

**New categories reviewed**: 2 (Category 8 Exfiltration via ML Inference API; Category 9 System Prompt and Configuration Leakage).

**(a) Citation correctness**: Mixed — ATLAS IDs are correct, OWASP LLM v2025 URLs use the wrong slug format.

ATLAS verification:
- AML.T0024 "Exfiltration via ML Inference API" — VERIFIED correct title (note: some sources call it "Exfiltration via AI Inference API" but the canonical MISP-galaxy entry and the file's spelling agree — both are acceptable variants used by ATLAS at different points; the file's "ML Inference API" matches the canonical mirror).
- AML.T0057 "LLM Data Leakage" — VERIFIED correct title.
- AML.TA0013 "Exfiltration" — correct tactic ID.
- The ATLAS URLs use the correct pattern `https://atlas.mitre.org/techniques/AML.T0024` and `https://atlas.mitre.org/techniques/AML.T0057`.

OWASP LLM Top 10 v2025 URL verification:
- `https://genai.owasp.org/llmrisk/llm07-system-prompt-leakage/` — **RETURNS 404**. Canonical is `https://genai.owasp.org/llmrisk/llm072025-system-prompt-leakage/`.
- `https://genai.owasp.org/llmrisk/llm10-unbounded-consumption/` — **RETURNS 404**. Canonical is `https://genai.owasp.org/llmrisk/llm102025-unbounded-consumption/`.
- `https://genai.owasp.org/llmrisk/llm03-supply-chain-vulnerabilities/` — **RETURNS 404**. Canonical is `https://genai.owasp.org/llmrisk/llm032025-supply-chain/`.

OWASP AI Exchange URL `https://owaspai.org/docs/ai_security_overview/` — VERIFIED resolves.

The 404 URLs occur in:
- C8 source block line 102: `llm10-unbounded-consumption/` (broken)
- C9 source block line 128: `llm07-system-prompt-leakage/` (broken)
- C9 source block line 129: `llm10-unbounded-consumption/` (broken)
- Bottom Primary Sources block line 143: `llm10-unbounded-consumption/` (broken)
- Bottom Primary Sources block line 144: `llm07-system-prompt-leakage/` (broken)
- Bottom Primary Sources block line 145: `llm03-supply-chain-vulnerabilities/` (broken)

**(b) Taxonomy alignment**: All correct. AML.T0024 Exfiltration via ML Inference API is the correct technique for the embeddings/logprobs extraction patterns described. AML.T0057 LLM Data Leakage is the correct technique for the verbatim training data regurgitation pattern. AML.TA0013 Exfiltration is the correct ATLAS tactic. OWASP LLM07:2025 System Prompt Leakage is correctly framed as a v2025-elevated category.

**(c) False-positive risk**: Not explicitly tagged but indicators are concrete (top-k vs full vocab, canary tokens, per-tenant budgets, dimension caps).

**(d) Speculative check**: No speculative content. The C8 example (week-long extraction campaign with logprobs + embeddings producing distillation + membership inference) is a published-research-grade attack scenario directly grounded in the Tramer et al. 2016 paper cited in the bottom Primary Sources. The C9 example (helpdesk chatbot leaking system prompt with API key + routing rules + banned topics) is realistic and matches actual reported incidents.

**Required minor fixes**:

1. Replace `https://genai.owasp.org/llmrisk/llm07-system-prompt-leakage/` with `https://genai.owasp.org/llmrisk/llm072025-system-prompt-leakage/` in:
   - C9 source block (line 128)
   - Bottom Primary Sources block (line 144)

2. Replace `https://genai.owasp.org/llmrisk/llm10-unbounded-consumption/` with `https://genai.owasp.org/llmrisk/llm102025-unbounded-consumption/` in:
   - C8 source block (line 102)
   - C9 source block (line 129)
   - Bottom Primary Sources block (line 143)

3. Replace `https://genai.owasp.org/llmrisk/llm03-supply-chain-vulnerabilities/` with `https://genai.owasp.org/llmrisk/llm032025-supply-chain/` in:
   - Bottom Primary Sources block (line 145)
   - Update the citation label as in tachi-data-poisoning fix #2.

These are pure URL-format fixes; no substance changes.

**Verdict**: Substance is sound, citations need URL slug fixes.

### tachi-tool-abuse — CHANGES_REQUESTED with REJECTIONS (3 categories must be re-anchored against correct sources)

**New categories reviewed**: 3 (Category 6 LLM Plugin Compromise [ATLAS AML.T0058]; Category 7 Unauthorized Tool Invocation via Instruction Hijack [ATLAS AML.T0061]; Category 8 MCP Server Poisoning and Cross-Tool Exfiltration [ATLAS AML.T0062]).

**(a) Citation correctness — CRITICAL FAILURE**: All three categories cite ATLAS technique IDs whose canonical titles describe completely different threats.

Verified against the canonical MISP-galaxy mirror of MITRE ATLAS techniques (`https://github.com/MISP/misp-galaxy/blob/main/clusters/mitre-atlas-attack-pattern.json`) — the authoritative ID-to-name mapping for ATLAS:

| Cited in tool-abuse file | Canonical ATLAS title (MISP-galaxy mirror, current as of T048 review) |
|---|---|
| **AML.T0058 "LLM Plugin Compromise"** (Category 6, lines 76-99 + Primary Sources line 158) | **Publish Poisoned Models** — adversaries upload poisoned models to public registries (PoisonGPT-style attack) |
| **AML.T0061 "Unauthorized Tool Invocation"** (Category 7, lines 100-124 + Primary Sources line 161) | **LLM Prompt Self-Replication** — adversaries craft self-replicating prompt injection that propagates across systems and LLMs |
| **AML.T0062 "MCP Server Poisoning"** (Category 8, lines 125-151 + Primary Sources line 162) | **Discover LLM Hallucinations** — adversaries query LLMs to identify hallucinated entities (packages, URLs, organizations) for typosquatting follow-on attacks |
| **AML.T0059 "Agent Tool Chaining"** (Primary Sources line 159) | **Erode Dataset Integrity** — adversaries degrade dataset integrity to reduce trust |
| **AML.T0060 "Capability Escalation via Tool"** (Primary Sources line 160) | **Publish Hallucinated Entities** — adversaries publish fake entities (packages, etc.) targeting hallucinated names |

**Cross-checked against**:
- The MISP-galaxy mirror file (canonical machine-readable ATLAS export, used by SIEM/MISP integrations).
- A Vectra "MITRE ATLAS: AI security framework with 16 tactics and 84 techniques" reference page that summarizes the same techniques.
- A search result snippet describing AML.T0061 ("Adversaries exploit MCP server configurations to invoke unauthorized tool actions or access restricted data. Additionally, an adversary may craft a self-replicating LLM prompt injection that causes the prompt to propagate across systems and LLMs") — note this snippet **does** reference MCP server abuse as a behavior associated with T0061, but the canonical title remains "LLM Prompt Self-Replication". The reference file's framing of T0061 as "Unauthorized Tool Invocation" is therefore not just wrong-by-name — it materially misrepresents the technique's emphasis (the technique is about prompt-injection self-replication, with MCP/tool abuse as one vector, not the central concept).

This is a TAXONOMIC FALSIFICATION pattern: real ATLAS IDs are cited as authoritative primary sources for completely different threat categories. A reader following the URL will land on a page describing a different attack and reasonably conclude that either the ATLAS catalog or the tachi pattern catalog is wrong — and since the tachi catalog is downstream, tachi loses the credibility.

**(b) Taxonomy alignment — FAIL**: The categories' framings (plugin compromise, per-request invocation hijack, MCP server poisoning) are real, distinct threats that **deserve** detection coverage, but the ATLAS IDs cited do not correspond to those threats. This is irrespective of whether the ATLAS catalog has been updated since the reference file was authored — the **current canonical titles do not match the file's claims**, and the file's wording ("MITRE ATLAS v5.1+ (Oct 2025 catalog update) introduced AML.T0058 as a dedicated technique for the runtime ingestion of compromised or malicious plugins") is a misrepresentation that cannot be reconciled with the actual catalog.

**(c) False-positive risk**: Not explicitly tagged but indicators are concrete and architecturally observable in all three categories. The substance of the indicator lists is high-quality.

**(d) Speculative check**: The categories' technical content (plugin SBOMs, manifest pinning, intent-to-tool mapping, MCP per-client isolation, inter-tool taint tracking) is concrete and well-grounded — these are all real defensive patterns published in MCP security guidance, OWASP LLM06:2025, and Anthropic's tool-use security documentation. **The substance is not speculative; only the ATLAS attribution is wrong.**

**REJECT-with-rebuild verdict for C6 / C7 / C8**:

Each category's substance survives the rejection — what must change is the primary-source attribution. Specifically:

- **C6 LLM Plugin Compromise**: Re-anchor on **OWASP LLM03:2025 Supply Chain** (correct URL: `https://genai.owasp.org/llmrisk/llm032025-supply-chain/`) as the primary source — that OWASP category explicitly covers plugin and tool supply chain vulnerabilities. **Add Anthropic's "Tool Use Security Considerations"** (already cited in the file's bottom Primary Sources) as a secondary primary. **Remove the AML.T0058 attribution entirely.** Remove the "Oct 2025 ATLAS catalog update" framing, which is factually wrong.

- **C7 Unauthorized Tool Invocation via Instruction Hijack**: Re-anchor on **OWASP LLM06:2025 Excessive Agency** (already cited but with broken URL — use canonical `https://genai.owasp.org/llmrisk/llm062025-excessive-agency/`) as the primary source. The OWASP LLM06:2025 page explicitly covers per-request intent misalignment under its "Excessive Permissions" sub-category. **Remove the AML.T0061 attribution entirely** (T0061 is "LLM Prompt Self-Replication", which describes a different threat — prompt injection that propagates across systems — not per-request tool invocation hijack). **Remove the "Oct 2025 ATLAS catalog update" framing.**

- **C8 MCP Server Poisoning and Cross-Tool Exfiltration**: Re-anchor on **OWASP LLM03:2025 Supply Chain** (canonical URL above) and **OWASP LLM06:2025 Excessive Agency** (canonical URL above) as primary sources. **Add Model Context Protocol's published security guidance** (the file already cites `https://modelcontextprotocol.io/` — keep that link but add specific MCP security advisory pages if MCP has published any). **Remove the AML.T0062 attribution entirely** (T0062 is "Discover LLM Hallucinations" — a reconnaissance technique for hallucinated package names, not MCP server compromise).

- **Bottom Primary Sources cleanup**: Remove the lines for AML.T0058, T0059, T0060, T0061, T0062 with their incorrect titles. Either omit them entirely or re-cite them with their canonical titles (Publish Poisoned Models, Erode Dataset Integrity, Publish Hallucinated Entities, LLM Prompt Self-Replication, Discover LLM Hallucinations) and a note that these techniques exist in ATLAS but address different threats from this file's categories.

**Required minor fixes (in addition to the above rebuilds)**:

1. **OWASP LLM06:2025 URL slug fix**: The file uses `https://genai.owasp.org/llmrisk/llm06-excessive-agency/` (broken) at lines 89, 114, 140, and 156. Replace all four occurrences with `https://genai.owasp.org/llmrisk/llm062025-excessive-agency/`.

**Verdict**: REJECT C6, C7, C8 in their current form. The categories must be rebuilt with correct primary-source attribution before they can ship. The substance is salvageable; only the ATLAS attribution must be removed.

### tachi-agent-autonomy — CHANGES_REQUESTED with REJECTION (1 category must be re-anchored)

**New categories reviewed**: 4 (Category 7 Excessive Agency Sub-Categories; Category 8 Agent Context Poisoning; Category 9 Goal Drift and Unbounded Planning Loops; Category 10 Multi-Agent Delegation Cycles).

**(a) Citation correctness — Mixed**:

C7 Excessive Agency Sub-Categories — citations ARE correct in substance (OWASP LLM06:2025 is the right primary source for this category) but the URL is **broken**: `https://genai.owasp.org/llmrisk/llm06-excessive-agency/` returns 404. Canonical: `https://genai.owasp.org/llmrisk/llm062025-excessive-agency/`. The category itself is well-grounded — OWASP LLM06:2025 explicitly defines the three sub-categories (Excessive Functionality, Excessive Permissions, Excessive Autonomy) and the file's framing matches the OWASP source.

C8 Agent Context Poisoning — **TAXONOMIC FAILURE**. The category's primary source claim is `MITRE ATLAS AML.T0058 LLM Plugin Compromise (runtime-context view): https://atlas.mitre.org/techniques/AML.T0058`. As established in the tool-abuse review above, AML.T0058 is **canonically titled "Publish Poisoned Models"** — a model-publishing supply-chain technique, NOT an LLM plugin compromise technique and NOT an agent context poisoning / runtime-memory technique. The file's claim that "MITRE ATLAS v5.1+ (Oct 2025 catalog update) AML.T0058 covers compromise of agent plugin and context state" is factually incorrect. The file additionally claims that the tool-abuse companion file extracts the same AML.T0058 with a "supply-chain view" — a sister extraction that is itself wrong (see tool-abuse review). The two-sibling architecture of "AML.T0058 supply-chain view in tool-abuse + AML.T0058 runtime-context view in agent-autonomy" is built entirely on a misidentified technique ID.

**However, C8's substance is sound and legitimate**. Runtime memory poisoning (cross-session memory contamination, vector-store-backed memory recursive poisoning, memory writes treated as untrusted input) is a real attack pattern, the indicator list is concrete, and the worked example (personal-finance assistant with poisoned memory authorizing transfers) is realistic. The category needs to be re-anchored on a correct primary source — OWASP LLM06:2025 Excessive Agency includes a "memory and persistent-state subsection" that is the right primary, and the file already cites that as a secondary source.

C9 Goal Drift and Unbounded Planning Loops — citations are correct.
- NIST AI 600-1 URL `https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.600-1.pdf` — canonical NIST publication URL pattern (verified format matches NIST nvlpubs.nist.gov publication pattern; NIST AI 600-1 is the canonical "Generative AI Profile" companion to NIST AI RMF).
- OWASP LLM10:2025 Unbounded Consumption — same broken-slug issue: `https://genai.owasp.org/llmrisk/llm10-unbounded-consumption/` (broken) → `https://genai.owasp.org/llmrisk/llm102025-unbounded-consumption/` (canonical).
- Section references (§2.1 Information Integrity / Confabulation, §2.7 Value Chain and Component Integration) match the published NIST AI 600-1 structure.

C10 Multi-Agent Delegation Cycles — primary source is OWASP AI Exchange (`https://owaspai.org/docs/ai_security_overview/`), which IS verified to resolve. The framing as "OWASP AI Exchange Agentic AI chapter" is acceptable; the OWASP AI Exchange does include agentic AI threat coverage. The non-canonical references in the bottom Primary Sources block (Anthropic Responsible Scaling Policy, Russell 2019 "Human Compatible") are clearly labeled as supplementary practitioner/academic references, not as primary detection-signal sources.

**(b) Taxonomy alignment**:

C7 — correct.
C8 — **WRONG ATLAS attribution**. AML.T0058 is "Publish Poisoned Models" not "LLM Plugin Compromise". Substance is fine, only the attribution wrapper must change.
C9 — correct.
C10 — correct.

**(c) False-positive risk**: Not explicitly tagged. C9's substance (reasoning loops, ReAct/Reflexion frameworks, watchdog processes, max iteration counts) is concrete and architecture-observable. C10's substance (delegation graph cycles, inter-agent message authentication, responsibility diffusion, agent population caps) is similarly concrete.

**(d) Speculative check**: All four categories have realistic worked examples grounded in published agent failure modes. C9's example (Reflexion-style runaway research agent burning $200) matches real AutoGPT-era cost-overrun reports. C10's example (cycle-forming code-review agents leaking SSH key) is a credible emergent-behavior scenario that maps to OWASP AI Exchange agentic risks.

**REJECT-with-rebuild verdict for C8 (specifically the AML.T0058 framing)**:

C8 must be rebuilt to:

1. **Remove the title parenthetical** "ATLAS AML.T0058 — Runtime-Context View" from the C8 header (line 102). New title: `## Pattern Category 8: Agent Context Poisoning (Runtime Memory and Cross-Session State)`.

2. **Remove the AML.T0058 framing** from the category description (lines 103-104). The paragraph that says "MITRE ATLAS v5.1+ (Oct 2025 catalog update) AML.T0058 covers compromise of agent plugin and context state. The `tachi-tool-abuse` companion reference extracts AML.T0058 with a supply-chain view... This category extracts AML.T0058 with a complementary runtime-context view" is wholly built on the incorrect AML.T0058 attribution. Replace with a paragraph that directly anchors on OWASP LLM06:2025 Excessive Agency's memory-and-persistent-state coverage:

   > Modern agent architectures maintain cross-session memory (user preferences, conversation history, learned facts, persistent profiles) backed by vector stores or key-value stores. When memory writes are trusted (the agent decides what to remember without sanitization or review) and memory is shared across sessions or tenants, an attacker can poison memory in one session and have the corruption outlast the injecting session, influencing future agent behavior. OWASP LLM06:2025 Excessive Agency's memory and persistent-state coverage frames this as the canonical agent context poisoning surface — distinct from prompt injection (which is per-turn) and from supply-chain plugin compromise (which is upstream of runtime).

3. **Replace the C8 Primary source block** (lines 116-118):
   ```
   - OWASP LLM06:2025 Excessive Agency (memory and persistent-state subsection): https://genai.owasp.org/llmrisk/llm062025-excessive-agency/
   - OWASP AI Exchange — Agentic AI chapter (memory poisoning and persistent-state attacks): https://owaspai.org/docs/ai_security_overview/
   ```

4. **Bottom Primary Sources block (line 199)**: Remove the line `- **MITRE ATLAS AML.T0058 LLM Plugin Compromise** (runtime-context view; supply-chain view extracted in tool-abuse Category 6): https://atlas.mitre.org/techniques/AML.T0058`. AML.T0058 should not appear in this file at all.

**Cross-cutting note**: The agent-autonomy and tool-abuse files implement a "two-sibling extraction of the same ATLAS technique" pattern that is itself questionable even when the technique ID is correct. With the technique ID being demonstrably wrong, the entire two-sibling architecture collapses. The Phase 1 plan correctly anticipated this risk via the C-4 "AML.T0058 canonical owner undecided between tool-abuse and agent-autonomy" entry in phase-1-complete.md §2.3, which routed resolution to T047 (Wave 13 cross-agent overlap audit). T047 cannot resolve the ownership question by choosing between tool-abuse and agent-autonomy, because **neither file's claim about AML.T0058 matches the canonical technique**. The correct outcome of T047 + T048 is to remove AML.T0058 from BOTH files and re-anchor each category on its correct primary source.

**Required minor fixes (in addition to the C8 rebuild)**:

1. **C7 OWASP LLM06:2025 URL slug fix**: Replace `https://genai.owasp.org/llmrisk/llm06-excessive-agency/` with `https://genai.owasp.org/llmrisk/llm062025-excessive-agency/` at line 91.
2. **C9 OWASP LLM10:2025 URL slug fix**: Replace `https://genai.owasp.org/llmrisk/llm10-unbounded-consumption/` with `https://genai.owasp.org/llmrisk/llm102025-unbounded-consumption/` at line 148.
3. **Bottom Primary Sources block URL slug fixes** (lines 195, 196): Same LLM06 and LLM10 fixes as above.

**Verdict**: C7, C9, C10 PASS substance-wise but need URL slug fixes. C8 must REJECT-and-rebuild for the AML.T0058 misattribution (substance survives, taxonomy framing must be removed).

## Deferred Concerns Disposition

### C-1: Spoofing GCP/Azure cloud metadata citations — PARTIALLY ADDRESSED (flagged for follow-up fix)

**Outcome**: Spoofing C7 (Cloud IAM Role Assumption Chain Abuse) does mention GCP `iam.serviceAccounts.getAccessToken` and Azure Managed Identity in the indicator list, and mentions IMDSv1/IMDSv2 in indicators and mitigations. However, the citation list (lines 101-105) **only includes AWS** sources (T1078.004, T1550.001, AWS Confused Deputy docs). No GCP or Azure canonical documentation URL is cited.

**Required fix** (non-blocking, recommended for next non-major edit pass):
- Add GCP IAM service account impersonation docs: `https://cloud.google.com/iam/docs/service-account-impersonation`
- Add GCP metadata server overview: `https://cloud.google.com/compute/docs/metadata/overview`
- Add Azure Managed Identity overview: `https://learn.microsoft.com/en-us/azure/active-directory/managed-identities-azure-resources/overview`
- Add Azure IMDS docs: `https://learn.microsoft.com/en-us/azure/virtual-machines/windows/instance-metadata-service`
- Add AWS IMDSv2 docs (already cited correctly in info-disclosure C7): `https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/configuring-instance-metadata-service.html`

**Note**: The info-disclosure C7 (SSRF to Cloud Metadata) DOES cite the AWS IMDSv2 URL correctly. The cloud-metadata coverage is therefore present in the file set as a whole — just not duplicated to spoofing C7 where it would also be relevant. This is a non-blocking citation duplication, not a substantive gap.

### C-2: Prompt-Injection Unicode TR36/TR39 citations — NOT ADDRESSED (recommended addition)

**Outcome**: Prompt-injection C8 ("Evasion via Encoding and Obfuscation") cites OWASP AI Exchange and OWASP LLM01:2025 as primary sources. The detection signals (Unicode NFKC normalization, U+200B / U+200C / U+200D zero-width characters, U+202E / U+2066 bidi overrides, homoglyph substitution) are **directly grounded in Unicode Technical Report #36 (Security Considerations) and Unicode Technical Standard #39 (Security Mechanisms)**, which are the canonical Unicode Consortium normative documents for these codepoints and the recommended normalization rules.

The Unicode TR/UTS documents are NOT in the FR-8 approved primary source set (which is OWASP / CWE / ATT&CK / ATLAS / NIST / OWASP AI Exchange) but they are W3C/Unicode Consortium normative standards directly referenced by OWASP. Per phase-1-complete.md C-2 routing, these are "supplementary, would strengthen but not blocking".

**Recommended addition** (non-blocking):
- Add to C8 source block as supplementary primary sources:
  - **Unicode TR36** (Security Considerations): `https://www.unicode.org/reports/tr36/`
  - **Unicode TR39** (Security Mechanisms): `https://www.unicode.org/reports/tr39/`
- Note that TR36/TR39 are Unicode Consortium normative documents that augment the OWASP AI Exchange evasion section.

### C-3: Prompt-Injection Greshake 2023 arXiv URL — NOT ADDRESSED (required minor fix)

**Outcome**: Prompt-injection C7 cites Greshake et al. 2023 by name in two places (line 113 within the C7 source block, line 158 in the bottom Primary Sources block) but **does not include the inline arXiv URL** `https://arxiv.org/abs/2302.12173`. Verified that this arXiv URL resolves to the cited paper "Not what you've signed up for: Compromising Real-World LLM-Integrated Applications with Indirect Prompt Injection".

**Required fix** (non-blocking minor):
- Update line 113 to: `- Greshake et al., 2023 "Not what you've signed up for: Compromising Real-World LLM-Integrated Applications with Indirect Prompt Injection" — https://arxiv.org/abs/2302.12173`
- Update line 158 to: `- **Greshake et al., 2023**: "Not what you've signed up for: Compromising Real-World LLM-Integrated Applications with Indirect Prompt Injection" — https://arxiv.org/abs/2302.12173`

This brings the file's foundational academic citation to the same navigability standard as the OWASP / ATLAS / CWE citations.

## Rejected Categories

The following 5 NEW pattern categories must be rejected in their current form due to taxonomic falsification (citing real ATLAS technique IDs whose canonical titles describe completely different threats). Each rejection is "REJECT-with-rebuild" — the substance survives, only the primary-source attribution must change.

| # | File | Category | Reason for rejection | Rebuild path |
|---|---|---|---|---|
| 1 | tachi-tool-abuse | C6 LLM Plugin Compromise (claims AML.T0058) | AML.T0058 is canonically "Publish Poisoned Models", a model-publishing supply-chain technique. The category's substance (plugin/tool supply-chain compromise) is real but the ATLAS attribution is wrong. | Re-anchor on OWASP LLM03:2025 Supply Chain as primary; remove AML.T0058 attribution; remove "Oct 2025 ATLAS catalog update" framing. |
| 2 | tachi-tool-abuse | C7 Unauthorized Tool Invocation via Instruction Hijack (claims AML.T0061) | AML.T0061 is canonically "LLM Prompt Self-Replication", a propagating-prompt-injection technique. The category's substance (per-request tool invocation hijack) is real but the ATLAS attribution is wrong. | Re-anchor on OWASP LLM06:2025 Excessive Agency (Excessive Permissions sub-category) as primary; remove AML.T0061 attribution. |
| 3 | tachi-tool-abuse | C8 MCP Server Poisoning and Cross-Tool Exfiltration (claims AML.T0062) | AML.T0062 is canonically "Discover LLM Hallucinations", a reconnaissance technique for hallucinated package names. The category's substance (MCP server compromise, cross-tool taint) is real but the ATLAS attribution is wrong. | Re-anchor on OWASP LLM03:2025 Supply Chain + LLM06:2025 Excessive Agency + Model Context Protocol security guidance as primaries; remove AML.T0062 attribution. |
| 4 | tachi-agent-autonomy | C8 Agent Context Poisoning (claims AML.T0058 — runtime-context view) | AML.T0058 is canonically "Publish Poisoned Models". The "runtime-context view" framing is built on the wrong technique ID. The two-sibling extraction with tool-abuse C6 is therefore also collapsed. | Re-anchor on OWASP LLM06:2025 Excessive Agency (memory and persistent-state subsection) + OWASP AI Exchange Agentic AI chapter as primaries; remove AML.T0058 attribution; rename category to remove the "ATLAS AML.T0058 — Runtime-Context View" parenthetical. |
| 5 | tachi-tool-abuse | Bottom Primary Sources lines for AML.T0059 ("Agent Tool Chaining") and AML.T0060 ("Capability Escalation via Tool") | AML.T0059 is canonically "Erode Dataset Integrity"; AML.T0060 is canonically "Publish Hallucinated Entities". Neither matches the labels in the file. | Remove these lines from the bottom Primary Sources block, OR re-cite them with their canonical titles and a note that the techniques exist in ATLAS but address different threats. |

**Important**: All five rejections are about **wrapper attribution**, not about substance. The categories' indicator lists, worked examples, and mitigation guidance are independently valid and well-grounded in the correct primary sources (OWASP LLM v2025, OWASP AI Exchange, MCP security guidance, Anthropic's tool-use guidelines). The substantive coverage of plugin compromise, per-request invocation hijack, MCP server poisoning, and runtime context poisoning SHOULD ship — but with correct citations.

**Why this is a rejection rather than a minor fix**: A wrong CWE number or a wrong URL is a minor citation typo. A wrong technique-ID-to-title mapping is a different class of error: it makes the cited primary source actively misleading to a reader who follows the URL, because the linked page describes a completely different attack. A reader checking the citation would conclude either the catalog is out of date or the tachi pattern catalog is fabricating sources. Both outcomes damage the credibility of the entire enrichment effort. This must be fixed before delivery.

**Why the rejections are "REJECT-with-rebuild" rather than "REJECT-and-de-scope"**: The substance is real and well-anchored on other sources that ARE valid (OWASP LLM v2025, OWASP AI Exchange, MCP guidance). Removing the categories entirely would leave a real coverage gap that the enrichment was specifically designed to close. Fixing the attribution preserves the value while restoring source-traceability integrity.

## Minor Fixes Recommended

The following 13 fixes are non-blocking citation cleanups, listed in order of priority. None require substantive re-review.

### Priority 1: Broken OWASP LLM v2025 URL slugs (10 fixes across 5 files)

The OWASP Gen AI Security Project's LLM Top 10 v2025 site uses inconsistent slug formats: some pages use `llmXX-` (the legacy format) while others use `llmXX2025-` (the v2025 format). Verified individual URL resolution. The correct URLs are:

| Broken URL (in reference files) | Canonical URL (per OWASP site) | Status |
|---|---|---|
| `https://genai.owasp.org/llmrisk/llm01-prompt-injection/` | (same — works) | OK |
| `https://genai.owasp.org/llmrisk/llm03-supply-chain-vulnerabilities/` | `https://genai.owasp.org/llmrisk/llm032025-supply-chain/` | **Broken — fix** |
| `https://genai.owasp.org/llmrisk/llm04-data-and-model-poisoning/` | (same — works) | OK |
| `https://genai.owasp.org/llmrisk/llm06-excessive-agency/` | `https://genai.owasp.org/llmrisk/llm062025-excessive-agency/` | **Broken — fix** |
| `https://genai.owasp.org/llmrisk/llm07-system-prompt-leakage/` | `https://genai.owasp.org/llmrisk/llm072025-system-prompt-leakage/` | **Broken — fix** |
| `https://genai.owasp.org/llmrisk/llm08-vector-and-embedding-weaknesses/` | `https://genai.owasp.org/llmrisk/llm082025-vector-and-embedding-weaknesses/` | **Broken — fix** |
| `https://genai.owasp.org/llmrisk/llm10-unbounded-consumption/` | `https://genai.owasp.org/llmrisk/llm102025-unbounded-consumption/` | **Broken — fix** |

Specific fix locations:

1. **tachi-prompt-injection/references/detection-patterns.md**: Lines 153 (LLM07 in bottom Primary Sources). Note: line 83 cites LLM01 which is one of the working URLs.
2. **tachi-data-poisoning/references/detection-patterns.md**: Lines 80 (LLM08 in C6 source block), 129 (LLM03 in bottom Primary Sources), 131 (LLM08 in bottom Primary Sources).
3. **tachi-model-theft/references/detection-patterns.md**: Lines 102 (LLM10 in C8 source block), 128 (LLM07 in C9 source block), 129 (LLM10 in C9 source block), 143 (LLM10 in bottom Primary Sources), 144 (LLM07 in bottom Primary Sources), 145 (LLM03 in bottom Primary Sources).
4. **tachi-tool-abuse/references/detection-patterns.md**: Lines 89 (LLM06 in C6 source block), 114 (LLM06 in C7 source block), 140 (LLM06 in C8 source block), 156 (LLM06 in bottom Primary Sources). Note: also includes the C6/C7/C8 rejection rebuilds — the URL fixes can be done as part of the rebuild.
5. **tachi-agent-autonomy/references/detection-patterns.md**: Lines 91 (LLM06 in C7 source block), 148 (LLM10 in C9 source block), 195 (LLM06 in bottom Primary Sources), 196 (LLM10 in bottom Primary Sources). Note: line 117 (AML.T0058 in C8 source block) is removed as part of the C8 rejection rebuild, not as a URL fix.

### Priority 2: Greshake 2023 inline arXiv URL (deferred concern C-3)

**File**: `tachi-prompt-injection/references/detection-patterns.md`
**Lines**: 113 (C7 source block) and 158 (bottom Primary Sources block).
**Fix**: Append `— https://arxiv.org/abs/2302.12173` to both citation lines so the foundational academic reference has its inline canonical URL.

### Priority 3: Spoofing C7 GCP/Azure cloud-metadata citations (deferred concern C-1)

**File**: `tachi-spoofing/references/detection-patterns.md`
**Lines**: 101-105 (C7 source block) and bottom Primary Sources block lines 134-136.
**Fix**: Add the four URLs listed in the C-1 disposition section above (GCP IAM impersonation, GCP metadata, Azure Managed Identity, Azure IMDS) plus the AWS IMDSv2 URL.

### Priority 4: Prompt-Injection C8 Unicode TR36/TR39 supplementary citations (deferred concern C-2)

**File**: `tachi-prompt-injection/references/detection-patterns.md`
**Lines**: 137-140 (C8 source block).
**Fix**: Add the Unicode Consortium TR36 and TR39 URLs as supplementary primary sources, with a note that they augment the OWASP AI Exchange evasion section.

## Decision

**STATUS**: CHANGES_REQUESTED

**Required actions before T048 can be marked complete and Phase 7 can proceed to delivery**:

1. **Decide on the 5 rejected categories** (tachi-tool-abuse C6/C7/C8; tachi-agent-autonomy C8; tachi-tool-abuse Primary Sources entries for AML.T0059/T0060):
   - **Option A — Inline rebuild within Phase 7**: Rewrite each rejected category in place to remove the wrong ATLAS attribution and re-anchor on the correct primary source. Estimated effort: ~3 hours for all 5 categories. Substance survives; only the wrapper changes. Recommended path because the substantive coverage is genuinely valuable and the rejected categories are otherwise high-quality.
   - **Option B — De-scope rejected categories to Wave 16+**: Remove the 5 rejected categories from the current Phase 7 deliverable and create a follow-up wave to rebuild them with correct attribution. This unblocks Phase 7 immediately but ships a less complete enrichment.

2. **Apply the 13 minor fixes** (10 broken OWASP LLM v2025 URL slugs + 3 deferred concerns C-1/C-2/C-3). These are non-blocking and can be applied in any order. Estimated effort: ~30 minutes for all 13 fixes.

3. **Re-verify the rebuilt categories** with a focused re-review of just the 5 affected category headers and primary source blocks. The substance does not need re-review.

**Rationale for CHANGES_REQUESTED rather than FAIL**: The taxonomic misalignments are concentrated in 5 of 30 NEW categories (17%), all in two specific files (tool-abuse and agent-autonomy), and all involve the same root cause (incorrect AML.T0058/T0059/T0060/T0061/T0062 attribution). The remaining 25 of 30 NEW categories (83%) PASS or pass-with-minor-fix, including the entire STRIDE tier (spoofing, tampering, repudiation, info-disclosure, denial-of-service, privilege-escalation) and the foundational AI categories (data-poisoning C6/C7, model-theft C8/C9, prompt-injection C6/C7/C8, agent-autonomy C7/C9/C10). The enrichment effort is largely successful; the rejections are concentrated and surgically fixable.

**Rationale for not de-scoping inline**: Per the T048 prompt's authority routing, this review identifies the rejections and reports them; the parent agent (or Wave 13 orchestrator) decides whether to inline-fix or defer. My recommendation is **Option A (inline rebuild)** because:
- The 5 rejected categories' substance is genuinely valuable enrichment that should ship.
- The fix is purely a wrapper change with no architectural impact.
- The 30-minute minor-fix pass is going to happen anyway for the URL slugs, and the rebuilds can be done in the same edit pass.
- Deferring to a follow-up wave creates two PR review cycles for what should be one.

**No fabricated citations**: Per T048 constraint, no claimed source URL was replaced or invented. All flagged URLs are reported as broken with the canonical alternative noted from the live OWASP / Unicode / arXiv / MITRE sites. All flagged ATLAS technique IDs are reported with their canonical titles from the MISP-galaxy mirror, which is the authoritative machine-readable export of the ATLAS catalog.

**No reference files were modified during this audit**, per T048 constraint. All required changes are reported in this file for execution by a downstream task.
