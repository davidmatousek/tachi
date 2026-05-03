---
schema_version: "1.0"
date: "2026-04-29"
source_file: "examples/mobile-banking-app/sample-report/threats.md"
classification: "confidential"
scoring_weights:
  cvss_base: 0.35
  exploitability: 0.30
  scalability: 0.15
  reachability: 0.20
---

# WellnessBank Mobile Banking Application — Risk Scores

## 1. Executive Summary

**Total findings scored**: 31 across 6 STRIDE threat categories (Spoofing, Tampering, Repudiation, Information Disclosure, Denial of Service, Privilege Escalation). No AI threat findings were identified in this architecture.

### Severity Band Distribution

| Severity | Count | Percentage |
|----------|-------|------------|
| Critical | 1 | 3.2% |
| High | 11 | 35.5% |
| Medium | 19 | 61.3% |
| Low | 0 | 0.0% |

**Highest-risk component**: Mobile Banking Customer (composite score 9.3, driven by S-5 — long-lived session token replay exploitable from the Untrusted User Zone with zero authentication friction).

**Severity narrative**: The WellnessBank mobile banking application has 1 Critical finding and 11 High findings representing active remediation obligations; the remaining 19 Medium findings require timely review. The mobile-specific attack surface — unprotected credential stores, exported Activities with no permission gating, and absence of certificate pinning — drives a disproportionate concentration in the High band.

---

## 2. Scored Threat Table

| ID | Component | Threat | CVSS | Exploitability | Scalability | Reachability | Composite | Severity | SLA | Disposition |
|----|-----------|--------|------|----------------|-------------|--------------|-----------|----------|-----|-------------|
| S-5 | Mobile Banking Customer | Long-Lived Session Token Replay: no ro... | 9.8 | 9.0 | 8.3 | 9.5 | 9.3 | Critical | 24h | Mitigate |
| E-1 | WellnessBankDebugActivity | M8 Privilege-Gain: Exported Debug Acti... | 10.0 | 9.5 | 8.0 | 4.5 | 8.5 | High | 7d | Mitigate |
| E-2 | MoneyTransferActivity | Unauthorized Money Transfer via Intent... | 9.3 | 9.5 | 8.5 | 4.5 | 8.3 | High | 7d | Mitigate |
| T-3 | MoneyTransferActivity | Mobile IPC Input Validation (M4) — In... | 9.3 | 8.8 | 8.5 | 4.5 | 8.1 | High | 7d | Mitigate |
| T-4 | WellnessBank Android Client | Insufficient Mobile Binary Protections... | 9.3 | 7.8 | 8.3 | 4.5 | 7.7 | High | 7d | Mitigate |
| I-4 | WellnessBank Android Client | Insufficient Mobile Cryptography (M10)... | 7.7 | 9.0 | 8.3 | 4.5 | 7.5 | High | 7d | Mitigate |
| S-2 | WellnessBank Android Client | Insecure Mobile Authentication/Author... | 8.6 | 7.3 | 8.3 | 4.5 | 7.3 | High | 7d | Mitigate |
| I-2 | WellnessBank Android Client | Inadequate Mobile Privacy Controls (M6... | 6.2 | 8.8 | 8.5 | 4.5 | 7.0 | High | 7d | Mitigate |
| I-7 | WellnessBankCredentialCache | Insecure Mobile Data Storage (M9) — C... | 6.2 | 9.0 | 8.5 | 4.5 | 7.0 | High | 7d | Mitigate |
| R-3 | Mobile Banking Customer | Deniable Financial Transactions: no n... | 4.8 | 8.3 | 6.0 | 9.5 | 7.0 | High | 7d | Mitigate |
| S-1 | WellnessBank Android Client | Improper Mobile Credential Usage (M1)... | 7.7 | 7.5 | 7.8 | 4.5 | 7.0 | High | 7d | Mitigate |
| R-1 | WellnessBank Android Client | M8 Accountability-Loss: Mobile Audit... | 6.1 | 8.5 | 8.5 | 4.5 | 6.9 | Medium | 30d | Review |
| I-8 | WellnessBank Android Client | Debug Log PII Leakage via Logcat: cre... | 5.5 | 9.0 | 8.8 | 4.5 | 6.8 | Medium | 30d | Review |
| S-3 | WellnessBank Android Client | Credential Theft via SharedPreferences... | 6.8 | 7.8 | 7.8 | 4.5 | 6.8 | Medium | 30d | Review |
| I-1 | WellnessBank Android Client | Insecure Mobile Communication (M5) —... | 6.8 | 7.0 | 6.8 | 4.5 | 6.4 | Medium | 30d | Review |
| D-2 | WellnessBank Backend API | Missing Rate Limiting on Backend Trans... | 7.0 | 8.0 | 7.5 | 1.0 | 6.2 | Medium | 30d | Review |
| R-4 | WellnessBankDebugActivity | Unlogged Debug Activity Invocations | 4.0 | 8.8 | 8.0 | 4.5 | 6.1 | Medium | 30d | Review |
| T-1 | WellnessAnalyticsSDK | Mobile Supply Chain Integrity (M2) — ... | 8.6 | 4.5 | 5.8 | 4.5 | 6.1 | Medium | 30d | Review |
| T-2 | WellnessPaySDK | Mobile Supply Chain Integrity (M2) — ... | 8.6 | 4.5 | 5.8 | 4.5 | 6.1 | Medium | 30d | Review |
| I-3 | WellnessBankLocalDB | Insecure Mobile Data Storage (M9) — L... | 6.3 | 6.3 | 7.0 | 4.5 | 6.0 | Medium | 30d | Review |
| T-6 | WellnessBankCredentialCache | Credential Cache Tampering via Shared... | 5.5 | 6.8 | 7.0 | 4.5 | 5.9 | Medium | 30d | Review |
| I-6 | WellnessPaySDK | Insecure Mobile Communication (M5) —... | 5.3 | 7.0 | 6.5 | 4.5 | 5.8 | Medium | 30d | Review |
| T-5 | WellnessBankLocalDB | Unencrypted Local Database Tampering | 5.0 | 6.8 | 7.0 | 4.5 | 5.7 | Medium | 30d | Review |
| E-3 | WellnessBank Backend API | Server-Side Authorization Gap for Deb... | 7.4 | 6.3 | 6.0 | 1.0 | 5.6 | Medium | 30d | Review |
| I-9 | WellnessBank Backend API | Backend API Verbose Error Response Ex... | 6.0 | 7.5 | 7.0 | 1.0 | 5.6 | Medium | 30d | Review |
| R-2 | WellnessBank Backend API | Missing Backend Audit Trail on Transa... | 4.8 | 8.3 | 8.3 | 1.0 | 5.6 | Medium | 30d | Review |
| D-4 | WellnessBankCredentialCache | Credential Store Corruption Leading t... | 5.0 | 5.5 | 4.0 | 4.5 | 4.9 | Medium | 30d | Review |
| I-5 | WellnessAnalyticsSDK | Insecure Mobile Communication (M5) —... | 3.1 | 6.5 | 6.5 | 4.5 | 4.9 | Medium | 30d | Review |
| S-4 | WellnessBank Backend API | Missing Token Binding on Backend Sess... | 5.2 | 6.3 | 5.8 | 1.0 | 4.8 | Medium | 30d | Review |
| D-1 | WellnessBank Android Client | Client-Side Resource Exhaustion via U... | 4.0 | 5.0 | 5.5 | 4.5 | 4.6 | Medium | 30d | Review |
| D-3 | WellnessBankLocalDB | Local Database Saturation | 3.3 | 5.5 | 3.8 | 4.5 | 4.3 | Medium | 30d | Review |

---

## 3. Dimensional Breakdown

### S-5: Long-Lived Session Token Replay

**Component**: Mobile Banking Customer
**Category**: Spoofing
**Composite Score**: 9.3 (Critical)

| Dimension | Score | Weight | Weighted |
|-----------|-------|--------|----------|
| CVSS Base | 9.8 | 0.35 | 3.43 |
| Exploitability | 9.0 | 0.30 | 2.70 |
| Scalability | 8.3 | 0.15 | 1.25 |
| Reachability | 9.5 | 0.20 | 1.90 |
| **Composite** | | | **9.3** |

**CVSS Vector**: `CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N`

**Scoring Rationale**:
- **CVSS**: Network-accessible (AV:N), low complexity (AC:L), no privileges required (PR:N), no user interaction (UI:N); tokens can be replayed from any host giving full C:H and I:H impact on account access. Score 9.8 reflects the near-maximum exploitability surface of a credential replay with no throttle or TTL.
- **Exploitability**: Token replay is among the most documented attack patterns (Known=9). The attack is trivially simple — no special conditions, standard tools, and no specialized knowledge required (Complexity=9, Tooling=9, Skill=9). Average 9.0.
- **Scalability**: Fully automatable, affects all users with captured tokens, requires only an internet connection, and blends with legitimate traffic making detection difficult (Scriptability=9, Scope=7, Resources=9, Detection=8). Average 8.3.
- **Reachability**: The Mobile Banking Customer component sits in the User Zone (Untrusted, baseline 9.0 + "user" keyword +0.5 = 9.5, clamped to Untrusted ceiling). This component is the primary external-actor entry point with no architectural barriers.

---

### E-1: M8 Privilege-Gain: Exported Debug Activity Bypassing Auth Boundary

**Component**: WellnessBankDebugActivity
**Category**: Privilege Escalation
**Composite Score**: 8.5 (High)

| Dimension | Score | Weight | Weighted |
|-----------|-------|--------|----------|
| CVSS Base | 10.0 | 0.35 | 3.50 |
| Exploitability | 9.5 | 0.30 | 2.85 |
| Scalability | 8.0 | 0.15 | 1.20 |
| Reachability | 4.5 | 0.20 | 0.90 |
| **Composite** | | | **8.5** |

**CVSS Vector**: `CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H`

**Scoring Rationale**:
- **CVSS**: Local attack vector (ADB access), trivially low complexity, no privileges required, scope changed (auth boundary crossed into main process), full CIA impact. The CVSS 3.1 formula yields 10.0, reflecting the maximum severity of an unauthenticated privilege bypass reaching privileged banking operations.
- **Exploitability**: The `adb shell am start` invocation is a single-command exploit with no preconditions, no special tooling beyond stock ADB, and requires zero specialized knowledge. Known=9, Complexity=10, Tooling=9, Skill=10. Average 9.5.
- **Scalability**: Easily scripted and targets all production installations with USB debugging enabled. Detection is near-zero because no audit log is generated. Scriptability=9, but Scope=6 (requires physical ADB access), Resources=8, Detection=9. Average 8.0.
- **Reachability**: WellnessBankDebugActivity resides in the Device Zone (Semi-Trusted, baseline 5.5, minus 1.0 for one network boundary = 4.5, clamped to Semi-Trusted floor).

---

### E-2: Unauthorized Money Transfer via Intent Hijacking and Privilege Escalation

**Component**: MoneyTransferActivity
**Category**: Privilege Escalation
**Composite Score**: 8.3 (High)

| Dimension | Score | Weight | Weighted |
|-----------|-------|--------|----------|
| CVSS Base | 9.3 | 0.35 | 3.26 |
| Exploitability | 9.5 | 0.30 | 2.85 |
| Scalability | 8.5 | 0.15 | 1.28 |
| Reachability | 4.5 | 0.20 | 0.90 |
| **Composite** | | | **8.3** |

**CVSS Vector**: `CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:N`

**Scoring Rationale**:
- **CVSS**: Any co-installed application or ADB shell can send an Intent to the exported MoneyTransferActivity without any permission gate (PR:N). Scope changes because an unprivileged app context gains access to the authenticated banking session (S:C). Full confidentiality and integrity impact (C:H/I:H).
- **Exploitability**: Any Android application can fire an explicit Intent — no special tools, no skill, trivial complexity. Known=9, Complexity=10, Tooling=9, Skill=10. Average 9.5.
- **Scalability**: A malicious co-installed app silently triggers fund transfers for every victim installation; fully automatable, affecting all app users universally. Scriptability=9, Scope=8, Resources=9, Detection=8. Average 8.5.
- **Reachability**: MoneyTransferActivity in Device Zone (Semi-Trusted, 4.5).

---

### T-3: Mobile IPC Input Validation (M4) — Intent Hijacking into Money Movement

**Component**: MoneyTransferActivity
**Category**: Tampering
**Composite Score**: 8.1 (High)

| Dimension | Score | Weight | Weighted |
|-----------|-------|--------|----------|
| CVSS Base | 9.3 | 0.35 | 3.26 |
| Exploitability | 8.8 | 0.30 | 2.64 |
| Scalability | 8.5 | 0.15 | 1.28 |
| Reachability | 4.5 | 0.20 | 0.90 |
| **Composite** | | | **8.1** |

**CVSS Vector**: `CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:N`

**Scoring Rationale**:
- **CVSS**: Same exported Activity surface as E-2 assessed from the tampering angle — injected Intent extras modify recipient account and amount fields entering the money-movement flow directly. Scope change preserved (S:C) as the tampering crosses from the unprivileged app context into the authenticated banking session.
- **Exploitability**: Well-documented Android Intent injection; any Android app or ADB shell executes with standard tools and trivial skill. Known=8, Complexity=9, Tooling=9, Skill=9. Average 8.8.
- **Scalability**: Fully scriptable via a malicious app distributed to victims, affecting all installations universally; the invocation appears as a normal in-app action from the OS perspective, limiting detection.
- **Reachability**: Device Zone, 4.5.

---

### T-4: Insufficient Mobile Binary Protections (M7)

**Component**: WellnessBank Android Client
**Category**: Tampering
**Composite Score**: 7.7 (High)

| Dimension | Score | Weight | Weighted |
|-----------|-------|--------|----------|
| CVSS Base | 9.3 | 0.35 | 3.26 |
| Exploitability | 7.8 | 0.30 | 2.34 |
| Scalability | 8.3 | 0.15 | 1.25 |
| Reachability | 4.5 | 0.20 | 0.90 |
| **Composite** | | | **7.7** |

**CVSS Vector**: `CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:N`

**Scoring Rationale**:
- **CVSS**: No obfuscation, no root detection, and no RASP stubs in the release APK. An attacker using Frida can hook security-critical methods with scope change (S:C) affecting the broader authentication and session context. Full C:H/I:H impact.
- **Exploitability**: Frida dynamic instrumentation is extensively documented with public tutorials. Complexity is moderate (requires Frida setup and some script authoring); tools freely available. Known=9, Complexity=6, Tooling=9, Skill=7. Average 7.8.
- **Scalability**: A crafted Frida script distributes and runs against any installation; no ProGuard means decompilation is trivial and attack scripts are universally applicable. Scriptability=8, Scope=9, Resources=8, Detection=8. Average 8.3.
- **Reachability**: Device Zone, 4.5.

---

### I-4: Insufficient Mobile Cryptography (M10)

**Component**: WellnessBank Android Client
**Category**: Information Disclosure
**Composite Score**: 7.5 (High)

| Dimension | Score | Weight | Weighted |
|-----------|-------|--------|----------|
| CVSS Base | 7.7 | 0.35 | 2.70 |
| Exploitability | 9.0 | 0.30 | 2.70 |
| Scalability | 8.3 | 0.15 | 1.25 |
| Reachability | 4.5 | 0.20 | 0.90 |
| **Composite** | | | **7.5** |

**CVSS Vector**: `CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N`

**Scoring Rationale**:
- **CVSS**: The 4-digit PIN keyspace of 10,000 values is exhausted in under one second on commodity GPU hardware against PBKDF2-HMAC-SHA1 at 1000 iterations with no salting. Local access is required to dump key material (AV:L); once dumped the crack is near-instant, yielding C:H and I:H access to the encrypted credential store.
- **Exploitability**: GPU-based password cracking is fully documented with ready-made tools (hashcat). The 4-digit PIN space requires no specialized knowledge — exhausted in a single brute-force pass. Known=9, Complexity=10, Tooling=9, Skill=8. Average 9.0.
- **Scalability**: Hashcat scripts automate cracking across all dumped key material; no salting means a single attack run covers all users with the same PIN simultaneously. Scriptability=9, Scope=8, Resources=7, Detection=9. Average 8.3.
- **Reachability**: Device Zone, 4.5.

---

### S-2: Insecure Mobile Authentication/Authorization (M3)

**Component**: WellnessBank Android Client
**Category**: Spoofing
**Composite Score**: 7.3 (High)

| Dimension | Score | Weight | Weighted |
|-----------|-------|--------|----------|
| CVSS Base | 8.6 | 0.35 | 3.01 |
| Exploitability | 7.3 | 0.30 | 2.19 |
| Scalability | 8.3 | 0.15 | 1.25 |
| Reachability | 4.5 | 0.20 | 0.90 |
| **Composite** | | | **7.3** |

**CVSS Vector**: `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N`

**Scoring Rationale**:
- **CVSS**: A valid session token (PR:L) provides network-accessible (AV:N) fund transfer capability without any biometric step-up. Full C:H/I:H impact on banking operations without additional challenge. Base score 8.6.
- **Exploitability**: Token capture is a prerequisite (moderates complexity = 6), but once obtained replay is fully automated with standard HTTP interception tools. Known=8, Complexity=6, Tooling=8, Skill=7. Average 7.3.
- **Scalability**: All authenticated users are affected; exploitation is scriptable, requires minimal resources, and the replayed session blends with normal traffic. Average 8.3.
- **Reachability**: Device Zone, 4.5.

---

### I-2: Inadequate Mobile Privacy Controls (M6)

**Component**: WellnessBank Android Client
**Category**: Information Disclosure
**Composite Score**: 7.0 (High)

| Dimension | Score | Weight | Weighted |
|-----------|-------|--------|----------|
| CVSS Base | 6.2 | 0.35 | 2.17 |
| Exploitability | 8.8 | 0.30 | 2.64 |
| Scalability | 8.5 | 0.15 | 1.28 |
| Reachability | 4.5 | 0.20 | 0.90 |
| **Composite** | | | **7.0** |

**CVSS Vector**: `CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N`

**Scoring Rationale**:
- **CVSS**: The absence of FLAG_SECURE exposes full financial data to screen capture and the Android recents thumbnail. Local access, trivially low complexity, no privileges needed, high confidentiality impact on account balances and transaction history.
- **Exploitability**: No technical attack tooling required — screen recording, shoulder surfing, or recents thumbnail capture reveals all financial data. Known=8, Complexity=9, Tooling=9, Skill=9. Average 8.8.
- **Scalability**: Affects every user on every installation; the attack is passive with no anomalies detectable. Scriptability=8, Scope=9, Resources=9, Detection=8. Average 8.5.
- **Reachability**: Device Zone, 4.5.

---

### I-7: Insecure Mobile Data Storage (M9) — Credential Cache

**Component**: WellnessBankCredentialCache
**Category**: Information Disclosure
**Composite Score**: 7.0 (High)

| Dimension | Score | Weight | Weighted |
|-----------|-------|--------|----------|
| CVSS Base | 6.2 | 0.35 | 2.17 |
| Exploitability | 9.0 | 0.30 | 2.70 |
| Scalability | 8.5 | 0.15 | 1.28 |
| Reachability | 4.5 | 0.20 | 0.90 |
| **Composite** | | | **7.0** |

**CVSS Vector**: `CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N`

**Scoring Rationale**:
- **CVSS**: Plaintext auth tokens stored in MODE_PRIVATE SharedPreferences are recoverable via ADB on older Android or root access. Local attack vector, no complexity or privileges, high confidentiality impact — long-lived tokens grant full account access.
- **Exploitability**: Token extraction from SharedPreferences is one of the most frequently cited Android security issues; trivial tooling (ADB or any root file manager), zero skill requirement. Known=9, Complexity=9, Tooling=9, Skill=9. Average 9.0.
- **Scalability**: Every installation exposes plaintext tokens; extraction is fully automatable and leaves no on-device detection footprint. Scriptability=9, Scope=7, Resources=9, Detection=9. Average 8.5.
- **Reachability**: WellnessBankCredentialCache in Device Zone (Semi-Trusted, 4.5).

---

### R-3: Deniable Financial Transactions

**Component**: Mobile Banking Customer
**Category**: Repudiation
**Composite Score**: 7.0 (High)

| Dimension | Score | Weight | Weighted |
|-----------|-------|--------|----------|
| CVSS Base | 4.8 | 0.35 | 1.68 |
| Exploitability | 8.3 | 0.30 | 2.49 |
| Scalability | 6.0 | 0.15 | 0.90 |
| Reachability | 9.5 | 0.20 | 1.90 |
| **Composite** | | | **7.0** |

**CVSS Vector**: `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N`

**Scoring Rationale**:
- **CVSS**: Authenticated user (PR:L) can deny initiating any transaction; limited integrity impact (I:L) because the action occurs but attribution is unenforceable. Network vector. Lower base score of 4.8 reflects the indirect nature of the repudiation threat.
- **Exploitability**: No technical exploit needed — a customer simply asserts non-repudiation in a dispute. Always available, requires no tools or skill. Known=6, Complexity=9, Tooling=9, Skill=9. Average 8.3.
- **Scalability**: Each instance requires individual human action; scalability is limited by manual effort. Scriptability=3, Scope=3, Resources=9, Detection=9. Average 6.0.
- **Reachability**: Mobile Banking Customer in User Zone (Untrusted, 9.5) — directly accessible from the external untrusted actor with no barriers, which significantly elevates the composite score for this finding.

---

### S-1: Improper Mobile Credential Usage (M1)

**Component**: WellnessBank Android Client
**Category**: Spoofing
**Composite Score**: 7.0 (High)

| Dimension | Score | Weight | Weighted |
|-----------|-------|--------|----------|
| CVSS Base | 7.7 | 0.35 | 2.70 |
| Exploitability | 7.5 | 0.30 | 2.25 |
| Scalability | 7.8 | 0.15 | 1.17 |
| Reachability | 4.5 | 0.20 | 0.90 |
| **Composite** | | | **7.0** |

**CVSS Vector**: `CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N`

**Scoring Rationale**:
- **CVSS**: Auth token and username stored in plaintext SharedPreferences are recoverable on a rooted or stolen device via data partition dump. Local attack vector, no complexity, full C:H/I:H impact enabling complete account takeover without PIN or biometric challenge.
- **Exploitability**: ADB-based credential extraction is well-documented; tooling is freely available. Complexity is moderate because root or ADB backup access is required as a prerequisite. Known=8, Complexity=6, Tooling=8, Skill=8. Average 7.5.
- **Scalability**: Extraction scripts work across all app installations on vulnerable Android versions; offline attack leaves no detection footprint. Scriptability=7, Scope=7, Resources=8, Detection=9. Average 7.8.
- **Reachability**: WellnessBank Android Client in Device Zone (Semi-Trusted, 4.5).

---

### R-1: M8 Accountability-Loss: Mobile Audit Log Gaps

**Component**: WellnessBank Android Client
**Category**: Repudiation
**Composite Score**: 6.9 (Medium)

| Dimension | Score | Weight | Weighted |
|-----------|-------|--------|----------|
| CVSS Base | 6.1 | 0.35 | 2.14 |
| Exploitability | 8.5 | 0.30 | 2.55 |
| Scalability | 8.5 | 0.15 | 1.28 |
| Reachability | 4.5 | 0.20 | 0.90 |
| **Composite** | | | **6.9** |

**CVSS Vector**: `CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:L/A:N`

**Scoring Rationale**:
- **CVSS**: Log.d credential leakage (C:H) combined with audit gap (I:L) produces a base of 6.1. Local attack vector for the logcat read; READ_LOGS or ADB required (PR:L).
- **Exploitability**: The Log.d credential leak is trivially exploited via `adb logcat` — a single command with no skill. The audit gap is exploitable by any authenticated user who simply acts without being logged. Known=8, Complexity=8, Tooling=9, Skill=9. Average 8.5.
- **Scalability**: Every installation leaks credentials to logcat in real time; any app with READ_LOGS harvests them continuously; no forensic artifacts remain after log rotation. Average 8.5.
- **Reachability**: Device Zone, 4.5. Note: this finding carries a divergence from the OWASP 3x3 matrix (Critical at HIGH/HIGH) because the repudiation category's CVSS base captures only the audit-gap component; the exploitability and scalability dimensions elevate the composite but do not reach Critical band (composite 6.9 vs. matrix-implied Critical).

---

### I-8: Debug Log PII Leakage via Logcat

**Component**: WellnessBank Android Client
**Category**: Information Disclosure
**Composite Score**: 6.8 (Medium)

| Dimension | Score | Weight | Weighted |
|-----------|-------|--------|----------|
| CVSS Base | 5.5 | 0.35 | 1.93 |
| Exploitability | 9.0 | 0.30 | 2.70 |
| Scalability | 8.8 | 0.15 | 1.32 |
| Reachability | 4.5 | 0.20 | 0.90 |
| **Composite** | | | **6.8** |

**CVSS Vector**: `CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N`

**Scoring Rationale**:
- **CVSS**: Credentials written to the shared logcat sink (C:H) via Log.d. Local access with READ_LOGS or ADB (PR:L); no complexity or user interaction required. Base score 5.5.
- **Exploitability**: `adb logcat` is the most basic Android developer tool; no specialized knowledge needed. Universally present in all builds containing the debug statement. Known=9, Complexity=9, Tooling=9, Skill=9. Average 9.0.
- **Scalability**: Any installed app holding READ_LOGS captures credentials continuously in real time; highly automatable, affects all active sessions. Scriptability=8, Scope=9, Resources=9, Detection=9. Average 8.8.
- **Reachability**: Device Zone, 4.5.

---

### S-3: Credential Theft via SharedPreferences Extraction

**Component**: WellnessBank Android Client
**Category**: Spoofing
**Composite Score**: 6.8 (Medium)

| Dimension | Score | Weight | Weighted |
|-----------|-------|--------|----------|
| CVSS Base | 6.8 | 0.35 | 2.38 |
| Exploitability | 7.8 | 0.30 | 2.34 |
| Scalability | 7.8 | 0.15 | 1.17 |
| Reachability | 4.5 | 0.20 | 0.90 |
| **Composite** | | | **6.8** |

**CVSS Vector**: `CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:H/I:L/A:N`

**Scoring Rationale**:
- **CVSS**: ADB backup extraction on pre-Android-12 devices gives high confidentiality impact (long-lived auth tokens); lower integrity impact (I:L) because this path is read-only extraction rather than session impersonation. Local vector, no complexity, no privileges.
- **Exploitability**: ADB backup is a standard Android debugging feature; extraction is documented and requires only a USB connection on pre-Android-12 devices. Known=8, Complexity=6, Tooling=9, Skill=8. Average 7.8.
- **Scalability**: All users on pre-Android-12 devices or rooted devices are universally affected; offline extraction leaves no detection artifacts. Average 7.8.
- **Reachability**: Device Zone, 4.5.

---

### I-1: Insecure Mobile Communication (M5) — Client-to-Backend

**Component**: WellnessBank Android Client
**Category**: Information Disclosure
**Composite Score**: 6.4 (Medium)

| Dimension | Score | Weight | Weighted |
|-----------|-------|--------|----------|
| CVSS Base | 6.8 | 0.35 | 2.38 |
| Exploitability | 7.0 | 0.30 | 2.10 |
| Scalability | 6.8 | 0.15 | 1.02 |
| Reachability | 4.5 | 0.20 | 0.90 |
| **Composite** | | | **6.4** |

**CVSS Vector**: `CVSS:3.1/AV:A/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:N`

**Scoring Rationale**:
- **CVSS**: MITM on a rogue Wi-Fi access point (AV:A) requires an adjacent network position (AC:H). Without certificate pinning the TLS session can be intercepted and modified, yielding C:H/I:H impact on all traffic including session tokens and transaction data.
- **Exploitability**: Rogue AP setup is well-documented; tools like mitmproxy are freely available, but the adjacent network position requirement raises complexity to moderate. Known=8, Complexity=6, Tooling=8, Skill=6. Average 7.0.
- **Scalability**: Affects all users on untrusted Wi-Fi networks; physical proximity requirement limits automation scope. Scriptability=7, Scope=7, Resources=6, Detection=7. Average 6.8.
- **Reachability**: Device Zone, 4.5. The client-side app process originates the unprotected TLS connection.

---

### D-2: Missing Rate Limiting on Backend Transaction API

**Component**: WellnessBank Backend API
**Category**: Denial of Service
**Composite Score**: 6.2 (Medium)

| Dimension | Score | Weight | Weighted |
|-----------|-------|--------|----------|
| CVSS Base | 7.0 | 0.35 | 2.45 |
| Exploitability | 8.0 | 0.30 | 2.40 |
| Scalability | 7.5 | 0.15 | 1.13 |
| Reachability | 1.0 | 0.20 | 0.20 |
| **Composite** | | | **6.2** |

**CVSS Vector**: `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H`

**Scoring Rationale**:
- **CVSS**: An authenticated client (PR:L) can flood the backend transaction endpoint from the network (AV:N) with no rate limiting, causing high availability impact (A:H) on backend processing capacity. Base score 7.0.
- **Exploitability**: Request flooding is one of the most documented DoS patterns; standard HTTP load-testing tools work against unprotected endpoints. Known=8, Complexity=8, Tooling=8, Skill=8. Average 8.0.
- **Scalability**: Fully scriptable with minimal resources; affects all backend consumers; detectable via monitoring (limits detection sub-dimension). Scriptability=9, Scope=8, Resources=8, Detection=5. Average 7.5.
- **Reachability**: WellnessBank Backend API in Backend Zone (Trusted, 1.0) — deep within the server-side architecture, significantly reducing composite despite elevated CVSS and exploitability scores.

---

### R-4: Unlogged Debug Activity Invocations

**Component**: WellnessBankDebugActivity
**Category**: Repudiation
**Composite Score**: 6.1 (Medium)

| Dimension | Score | Weight | Weighted |
|-----------|-------|--------|----------|
| CVSS Base | 4.0 | 0.35 | 1.40 |
| Exploitability | 8.8 | 0.30 | 2.64 |
| Scalability | 8.0 | 0.15 | 1.20 |
| Reachability | 4.5 | 0.20 | 0.90 |
| **Composite** | | | **6.1** |

**CVSS Vector**: `CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N`

**Scoring Rationale**:
- **CVSS**: Debug Activity invocations leave no audit trail (I:L integrity gap). Local attack vector, no privileges, trivially low complexity. Lower base score of 4.0 reflects the indirect impact of the audit gap rather than direct data compromise.
- **Exploitability**: The same `adb shell am start` invocation used for E-1; trivial knowledge, standard tooling, single command. Known=8, Complexity=9, Tooling=9, Skill=9. Average 8.8.
- **Scalability**: Any ADB-accessible device is affected; log gaps are undetectable by design; scriptable via ADB automation. Scriptability=8, Scope=6, Resources=9, Detection=9. Average 8.0.
- **Reachability**: Device Zone, 4.5.

---

### T-1: Mobile Supply Chain Integrity (M2) — Analytics SDK

**Component**: WellnessAnalyticsSDK
**Category**: Tampering
**Composite Score**: 6.1 (Medium)

| Dimension | Score | Weight | Weighted |
|-----------|-------|--------|----------|
| CVSS Base | 8.6 | 0.35 | 3.01 |
| Exploitability | 4.5 | 0.30 | 1.35 |
| Scalability | 5.8 | 0.15 | 0.87 |
| Reachability | 4.5 | 0.20 | 0.90 |
| **Composite** | | | **6.1** |

**CVSS Vector**: `CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:C/C:H/I:H/A:L`

**Scoring Rationale**:
- **CVSS**: Supply chain compromise requires a developer to pull the tainted SDK (UI:R), but once distributed the malicious SDK executes in the app's full security context (S:C) with access to all session data (C:H/I:H). AC:H reflects the difficulty of compromising the SDK maintainer or registry.
- **Exploitability**: Supply chain attacks require significant upstream access — compromising the SDK maintainer, CI pipeline, or package registry. Known cases exist but are non-trivial; custom tooling required. Known=7, Complexity=4, Tooling=3, Skill=4. Average 4.5.
- **Scalability**: Once in the SDK the malicious code ships universally, but the initial compromise requires substantial effort and is hard to automate at scale. Scriptability=3, Scope=8, Resources=4, Detection=8. Average 5.8.
- **Reachability**: WellnessAnalyticsSDK in Device Zone (Semi-Trusted, 4.5).

---

### T-2: Mobile Supply Chain Integrity (M2) — Payment SDK

**Component**: WellnessPaySDK
**Category**: Tampering
**Composite Score**: 6.1 (Medium)

| Dimension | Score | Weight | Weighted |
|-----------|-------|--------|----------|
| CVSS Base | 8.6 | 0.35 | 3.01 |
| Exploitability | 4.5 | 0.30 | 1.35 |
| Scalability | 5.8 | 0.15 | 0.87 |
| Reachability | 4.5 | 0.20 | 0.90 |
| **Composite** | | | **6.1** |

**CVSS Vector**: `CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:C/C:H/I:H/A:L`

**Scoring Rationale**:
- **CVSS**: Identical attack class to T-1 but on the payment SDK; payment card data and transaction authorization are at stake, making the impact surface equivalent or greater than the analytics SDK.
- **Exploitability**: Same supply chain attack complexity as T-1; requires compromising the payment SDK publisher or package registry. Known=7, Complexity=4, Tooling=3, Skill=4. Average 4.5.
- **Scalability**: Same universal deployment once in the SDK, with the same supply-chain-specific constraints on initial compromise automation. Average 5.8.
- **Reachability**: WellnessPaySDK in Device Zone (Semi-Trusted, 4.5).

---

### I-3: Insecure Mobile Data Storage (M9) — Local Database

**Component**: WellnessBankLocalDB
**Category**: Information Disclosure
**Composite Score**: 6.0 (Medium)

| Dimension | Score | Weight | Weighted |
|-----------|-------|--------|----------|
| CVSS Base | 6.3 | 0.35 | 2.21 |
| Exploitability | 6.3 | 0.30 | 1.89 |
| Scalability | 7.0 | 0.15 | 1.05 |
| Reachability | 4.5 | 0.20 | 0.90 |
| **Composite** | | | **6.0** |

**CVSS Vector**: `CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N`

**Scoring Rationale**:
- **CVSS**: With `allowBackup="true"` the unencrypted SQLite database is automatically backed up to Google Drive (AV:N). An attacker who compromises the user's Google account (AC:H) recovers complete transaction history without device access. High confidentiality impact.
- **Exploitability**: Google account compromise is a documented attack path; standard phishing and credential-stuffing tools apply, but AC:H prerequisite moderates practical exploitability. Known=7, Complexity=5, Tooling=7, Skill=6. Average 6.3.
- **Scalability**: All users with Google backups enabled are affected; extraction from Google Drive backup is scriptable once credentials are obtained. Scriptability=7, Scope=8, Resources=6, Detection=7. Average 7.0.
- **Reachability**: WellnessBankLocalDB in Device Zone (Semi-Trusted, 4.5).

---

### T-6: Credential Cache Tampering via SharedPreferences Overwrite

**Component**: WellnessBankCredentialCache
**Category**: Tampering
**Composite Score**: 5.9 (Medium)

| Dimension | Score | Weight | Weighted |
|-----------|-------|--------|----------|
| CVSS Base | 5.5 | 0.35 | 1.93 |
| Exploitability | 6.8 | 0.30 | 2.04 |
| Scalability | 7.0 | 0.15 | 1.05 |
| Reachability | 4.5 | 0.20 | 0.90 |
| **Composite** | | | **5.9** |

**CVSS Vector**: `CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:U/C:L/I:H/A:L`

**Scoring Rationale**:
- **CVSS**: Root access required (PR:H) to overwrite SharedPreferences; integrity impact is high (forged tokens, credential corruption) with lower confidentiality and availability side effects.
- **Exploitability**: Requires a rooted device (moderate barrier); once root is achieved file editing is trivial. Known=7, Complexity=5, Tooling=8, Skill=7. Average 6.8.
- **Scalability**: Restricted to rooted device population; scriptable once root is available but with moderate target scope. Scriptability=7, Scope=5, Resources=8, Detection=8. Average 7.0.
- **Reachability**: Device Zone, 4.5.

---

### I-6: Insecure Mobile Communication (M5) — Payment SDK Egress

**Component**: WellnessPaySDK
**Category**: Information Disclosure
**Composite Score**: 5.8 (Medium)

| Dimension | Score | Weight | Weighted |
|-----------|-------|--------|----------|
| CVSS Base | 5.3 | 0.35 | 1.86 |
| Exploitability | 7.0 | 0.30 | 2.10 |
| Scalability | 6.5 | 0.15 | 0.98 |
| Reachability | 4.5 | 0.20 | 0.90 |
| **Composite** | | | **5.8** |

**CVSS Vector**: `CVSS:3.1/AV:A/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N`

**Scoring Rationale**:
- **CVSS**: Adjacent network position required for MITM; without certificate pinning the payment authorization flow (including card data and transaction amounts) can be intercepted. High confidentiality impact on financial data.
- **Exploitability**: Same rogue AP approach as I-1; payment data sensitivity elevates exploitation motivation; tooling and techniques well-documented. Known=8, Complexity=6, Tooling=8, Skill=6. Average 7.0.
- **Scalability**: Affects users on untrusted Wi-Fi making payments; adjacent network requirement limits scalability. Scriptability=7, Scope=6, Resources=6, Detection=7. Average 6.5.
- **Reachability**: Device Zone, 4.5.

---

### T-5: Unencrypted Local Database Tampering

**Component**: WellnessBankLocalDB
**Category**: Tampering
**Composite Score**: 5.7 (Medium)

| Dimension | Score | Weight | Weighted |
|-----------|-------|--------|----------|
| CVSS Base | 5.0 | 0.35 | 1.75 |
| Exploitability | 6.8 | 0.30 | 2.04 |
| Scalability | 7.0 | 0.15 | 1.05 |
| Reachability | 4.5 | 0.20 | 0.90 |
| **Composite** | | | **5.7** |

**CVSS Vector**: `CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:U/C:N/I:H/A:L`

**Scoring Rationale**:
- **CVSS**: Root or ADB access required (PR:H); direct SQLite modification yields high integrity impact (fabricated transaction records, balance manipulation) with minimal availability side effect.
- **Exploitability**: SQLite browsing tools are freely available; root requirement is the primary barrier. Known=7, Complexity=5, Tooling=8, Skill=7. Average 6.8.
- **Scalability**: Affects rooted device users; scriptable but constrained by root access prerequisite; offline attack avoids detection. Scriptability=7, Scope=5, Resources=8, Detection=8. Average 7.0.
- **Reachability**: WellnessBankLocalDB in Device Zone, 4.5.

---

### E-3: Server-Side Authorization Gap for Debug-Initiated Operations

**Component**: WellnessBank Backend API
**Category**: Privilege Escalation
**Composite Score**: 5.6 (Medium)

| Dimension | Score | Weight | Weighted |
|-----------|-------|--------|----------|
| CVSS Base | 7.4 | 0.35 | 2.59 |
| Exploitability | 6.3 | 0.30 | 1.89 |
| Scalability | 6.0 | 0.15 | 0.90 |
| Reachability | 1.0 | 0.20 | 0.20 |
| **Composite** | | | **5.6** |

**CVSS Vector**: `CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:L`

**Scoring Rationale**:
- **CVSS**: The backend accepts requests from debug-Activity-initiated flows relying on the client's bearer token without attestation verification. AC:H because exploiting this requires first triggering the debug Activity bypass (prerequisite chain). C:H/I:H/A:L reflects backend data exposure when the gap is exploited.
- **Exploitability**: Requires the debug Activity bypass (E-1) as a precondition, adding complexity. Moderate exploitability once the prerequisite is met. Known=7, Complexity=5, Tooling=7, Skill=6. Average 6.3.
- **Scalability**: Moderate automation; all users with ADB access to the debug Activity are affected but the prerequisite chain limits scalability. Scriptability=6, Scope=5, Resources=8, Detection=5. Average 6.0.
- **Reachability**: WellnessBank Backend API in Backend Zone (Trusted, 1.0).

---

### I-9: Backend API Verbose Error Response Exposure

**Component**: WellnessBank Backend API
**Category**: Information Disclosure
**Composite Score**: 5.6 (Medium)

| Dimension | Score | Weight | Weighted |
|-----------|-------|--------|----------|
| CVSS Base | 6.0 | 0.35 | 2.10 |
| Exploitability | 7.5 | 0.30 | 2.25 |
| Scalability | 7.0 | 0.15 | 1.05 |
| Reachability | 1.0 | 0.20 | 0.20 |
| **Composite** | | | **5.6** |

**CVSS Vector**: `CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N`

**Scoring Rationale**:
- **CVSS**: Unauthenticated network callers can trigger error conditions exposing stack traces, ORM field names, and service internals (C:L). Low complexity, no privileges, network accessible.
- **Exploitability**: Deliberately triggering API errors is trivial with standard HTTP tools (curl, Burp); well-documented reconnaissance technique. Known=6, Complexity=8, Tooling=8, Skill=8. Average 7.5.
- **Scalability**: Automatable against any endpoint; minimal resources; detectable in server access logs with adequate monitoring. Scriptability=7, Scope=7, Resources=9, Detection=5. Average 7.0.
- **Reachability**: Backend Zone (Trusted, 1.0).

---

### R-2: Missing Backend Audit Trail on Transaction Operations

**Component**: WellnessBank Backend API
**Category**: Repudiation
**Composite Score**: 5.6 (Medium)

| Dimension | Score | Weight | Weighted |
|-----------|-------|--------|----------|
| CVSS Base | 4.8 | 0.35 | 1.68 |
| Exploitability | 8.3 | 0.30 | 2.49 |
| Scalability | 8.3 | 0.15 | 1.25 |
| Reachability | 1.0 | 0.20 | 0.20 |
| **Composite** | | | **5.6** |

**CVSS Vector**: `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N`

**Scoring Rationale**:
- **CVSS**: An authenticated user (PR:L) can perform privileged operations at the backend (AV:N) that leave no audit trail. Limited integrity impact (I:L) as the gap enables post-hoc deniability rather than direct data manipulation.
- **Exploitability**: No exploit needed — authenticated users simply act without generating evidence. The gap is always present and requires no technical skill. Known=7, Complexity=8, Tooling=9, Skill=9. Average 8.3.
- **Scalability**: Applies to every authenticated transaction and account operation; highly relevant from a bulk-operation perspective; inherently undetectable. Scriptability=8, Scope=7, Resources=9, Detection=9. Average 8.3.
- **Reachability**: Backend Zone (Trusted, 1.0).

---

### D-4: Credential Store Corruption Leading to Denial of Service

**Component**: WellnessBankCredentialCache
**Category**: Denial of Service
**Composite Score**: 4.9 (Medium)

| Dimension | Score | Weight | Weighted |
|-----------|-------|--------|----------|
| CVSS Base | 5.0 | 0.35 | 1.75 |
| Exploitability | 5.5 | 0.30 | 1.65 |
| Scalability | 4.0 | 0.15 | 0.60 |
| Reachability | 4.5 | 0.20 | 0.90 |
| **Composite** | | | **4.9** |

**CVSS Vector**: `CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:U/C:N/I:L/A:H`

**Scoring Rationale**:
- **CVSS**: Root access (PR:H) enables corrupting the SharedPreferences file, causing authentication failures and re-login loops (A:H). Limited integrity side effect (I:L) from the corruption itself.
- **Exploitability**: Requires root (significant barrier); once root is obtained the corruption is trivial. Known=5, Complexity=4, Tooling=6, Skill=7. Average 5.5.
- **Scalability**: Narrow target scope (rooted devices only); individual user impact; moderate detection when the user experiences lockout. Scriptability=3, Scope=2, Resources=7, Detection=4. Average 4.0.
- **Reachability**: Device Zone, 4.5.

---

### I-5: Insecure Mobile Communication (M5) — Analytics SDK Egress

**Component**: WellnessAnalyticsSDK
**Category**: Information Disclosure
**Composite Score**: 4.9 (Medium)

| Dimension | Score | Weight | Weighted |
|-----------|-------|--------|----------|
| CVSS Base | 3.1 | 0.35 | 1.09 |
| Exploitability | 6.5 | 0.30 | 1.95 |
| Scalability | 6.5 | 0.15 | 0.98 |
| Reachability | 4.5 | 0.20 | 0.90 |
| **Composite** | | | **4.9** |

**CVSS Vector**: `CVSS:3.1/AV:A/AC:H/PR:N/UI:N/S:U/C:L/I:N/A:N`

**Scoring Rationale**:
- **CVSS**: Adjacent network MITM (AV:A, AC:H) on analytics telemetry yields low confidentiality impact (C:L — device identifiers and session metadata rather than financial data or credentials).
- **Exploitability**: Standard rogue AP technique; analytics data has lower attacker value than payment or credential data, reducing practical motivation despite similar technical complexity. Known=7, Complexity=6, Tooling=7, Skill=6. Average 6.5.
- **Scalability**: Same adjacent-network limitation as other MITM findings; analytics traffic interception affects users on untrusted Wi-Fi. Scriptability=7, Scope=6, Resources=6, Detection=7. Average 6.5.
- **Reachability**: Device Zone, 4.5.

---

### S-4: Missing Token Binding on Backend Session

**Component**: WellnessBank Backend API
**Category**: Spoofing
**Composite Score**: 4.8 (Medium)

| Dimension | Score | Weight | Weighted |
|-----------|-------|--------|----------|
| CVSS Base | 5.2 | 0.35 | 1.82 |
| Exploitability | 6.3 | 0.30 | 1.89 |
| Scalability | 5.8 | 0.15 | 0.87 |
| Reachability | 1.0 | 0.20 | 0.20 |
| **Composite** | | | **4.8** |

**CVSS Vector**: `CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:L/A:N`

**Scoring Rationale**:
- **CVSS**: Token replay from an intercepted session (AC:H — requires prior MITM or token theft). No device binding means a captured token is valid from any network origin. Limited C:L/I:L impact scoped to the replayed session's actions.
- **Exploitability**: Requires prior token capture (prerequisite raises complexity); once obtained, replay is straightforward. Known=7, Complexity=5, Tooling=7, Skill=6. Average 6.3.
- **Scalability**: Affects users whose tokens have been previously captured; moderate detection if the backend monitors unusual origin patterns. Scriptability=6, Scope=6, Resources=6, Detection=5. Average 5.8.
- **Reachability**: Backend Zone (Trusted, 1.0).

---

### D-1: Client-Side Resource Exhaustion via Unconstrained SDK I/O

**Component**: WellnessBank Android Client
**Category**: Denial of Service
**Composite Score**: 4.6 (Medium)

| Dimension | Score | Weight | Weighted |
|-----------|-------|--------|----------|
| CVSS Base | 4.0 | 0.35 | 1.40 |
| Exploitability | 5.0 | 0.30 | 1.50 |
| Scalability | 5.5 | 0.15 | 0.83 |
| Reachability | 4.5 | 0.20 | 0.90 |
| **Composite** | | | **4.6** |

**CVSS Vector**: `CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L`

**Scoring Rationale**:
- **CVSS**: Misbehaving SDK (triggered locally) causes battery/network resource drain (A:L). Local attack vector; limited availability impact on individual device.
- **Exploitability**: Requires a compromised or misbehaving SDK version; the threat is contingent on supply-chain compromise (covered by T-1, T-2). Moderate exploitability as an independent path. Known=5, Complexity=5, Tooling=5, Skill=5. Average 5.0.
- **Scalability**: Affects all app installations if a misbehaving SDK ships; partially automatable via SDK update mechanism; detectable via battery drain analytics. Scriptability=5, Scope=6, Resources=7, Detection=4. Average 5.5.
- **Reachability**: Device Zone, 4.5.

---

### D-3: Local Database Saturation

**Component**: WellnessBankLocalDB
**Category**: Denial of Service
**Composite Score**: 4.3 (Medium)

| Dimension | Score | Weight | Weighted |
|-----------|-------|--------|----------|
| CVSS Base | 3.3 | 0.35 | 1.16 |
| Exploitability | 5.5 | 0.30 | 1.65 |
| Scalability | 3.8 | 0.15 | 0.57 |
| Reachability | 4.5 | 0.20 | 0.90 |
| **Composite** | | | **4.3** |

**CVSS Vector**: `CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:L`

**Scoring Rationale**:
- **CVSS**: Uncontrolled cache growth causes device storage saturation (A:L) affecting the app process. Limited availability impact (single-user, recoverable by clearing app data). PR:L reflects the app process context.
- **Exploitability**: Requires extended normal usage without cache eviction or deliberate data generation via app abuse. Moderate complexity. Known=4, Complexity=5, Tooling=6, Skill=7. Average 5.5.
- **Scalability**: Single-user impact; manual triggering required; visible via device storage warnings, limiting scalability and stealth. Scriptability=3, Scope=2, Resources=7, Detection=3. Average 3.8.
- **Reachability**: Device Zone, 4.5.

---

## 4. Governance Fields

| ID | Component | Severity | Owner | SLA | Disposition | Review Date |
|----|-----------|----------|-------|-----|-------------|-------------|
| S-5 | Mobile Banking Customer | Critical | Unassigned | 24h | Mitigate | 2026-04-30 |
| E-1 | WellnessBankDebugActivity | High | Unassigned | 7d | Mitigate | 2026-05-06 |
| E-2 | MoneyTransferActivity | High | Unassigned | 7d | Mitigate | 2026-05-06 |
| T-3 | MoneyTransferActivity | High | Unassigned | 7d | Mitigate | 2026-05-06 |
| T-4 | WellnessBank Android Client | High | Unassigned | 7d | Mitigate | 2026-05-06 |
| I-4 | WellnessBank Android Client | High | Unassigned | 7d | Mitigate | 2026-05-06 |
| S-2 | WellnessBank Android Client | High | Unassigned | 7d | Mitigate | 2026-05-06 |
| I-2 | WellnessBank Android Client | High | Unassigned | 7d | Mitigate | 2026-05-06 |
| I-7 | WellnessBankCredentialCache | High | Unassigned | 7d | Mitigate | 2026-05-06 |
| R-3 | Mobile Banking Customer | High | Unassigned | 7d | Mitigate | 2026-05-06 |
| S-1 | WellnessBank Android Client | High | Unassigned | 7d | Mitigate | 2026-05-06 |
| R-1 | WellnessBank Android Client | Medium | Unassigned | 30d | Review | 2026-05-29 |
| I-8 | WellnessBank Android Client | Medium | Unassigned | 30d | Review | 2026-05-29 |
| S-3 | WellnessBank Android Client | Medium | Unassigned | 30d | Review | 2026-05-29 |
| I-1 | WellnessBank Android Client | Medium | Unassigned | 30d | Review | 2026-05-29 |
| D-2 | WellnessBank Backend API | Medium | Unassigned | 30d | Review | 2026-05-29 |
| R-4 | WellnessBankDebugActivity | Medium | Unassigned | 30d | Review | 2026-05-29 |
| T-1 | WellnessAnalyticsSDK | Medium | Unassigned | 30d | Review | 2026-05-29 |
| T-2 | WellnessPaySDK | Medium | Unassigned | 30d | Review | 2026-05-29 |
| I-3 | WellnessBankLocalDB | Medium | Unassigned | 30d | Review | 2026-05-29 |
| T-6 | WellnessBankCredentialCache | Medium | Unassigned | 30d | Review | 2026-05-29 |
| I-6 | WellnessPaySDK | Medium | Unassigned | 30d | Review | 2026-05-29 |
| T-5 | WellnessBankLocalDB | Medium | Unassigned | 30d | Review | 2026-05-29 |
| E-3 | WellnessBank Backend API | Medium | Unassigned | 30d | Review | 2026-05-29 |
| I-9 | WellnessBank Backend API | Medium | Unassigned | 30d | Review | 2026-05-29 |
| R-2 | WellnessBank Backend API | Medium | Unassigned | 30d | Review | 2026-05-29 |
| D-4 | WellnessBankCredentialCache | Medium | Unassigned | 30d | Review | 2026-05-29 |
| I-5 | WellnessAnalyticsSDK | Medium | Unassigned | 30d | Review | 2026-05-29 |
| S-4 | WellnessBank Backend API | Medium | Unassigned | 30d | Review | 2026-05-29 |
| D-1 | WellnessBank Android Client | Medium | Unassigned | 30d | Review | 2026-05-29 |
| D-3 | WellnessBankLocalDB | Medium | Unassigned | 30d | Review | 2026-05-29 |

---

## 5. Scoring Methodology

### Scoring Dimensions

| Dimension | Weight | Description |
|-----------|--------|-------------|
| CVSS Base | 0.35 | CVSS 3.1 base score (0.0–10.0) reflecting inherent vulnerability severity independent of environmental context |
| Exploitability | 0.30 | Operational attack feasibility: average of Known Techniques, Attack Complexity (inverted), Tooling Availability, Skill Level (inverted) |
| Scalability | 0.15 | Blast radius and attack economics: average of Scriptability, Target Scope, Resource Requirements (inverted), Detection Difficulty |
| Reachability | 0.20 | Architecture-aware exposure: trust zone position, zone name refinement, authentication barriers, and network segmentation adjustments |

### Composite Score Formula

```
Composite = (0.35 × CVSS Base) + (0.30 × Exploitability) + (0.15 × Scalability) + (0.20 × Reachability)
```

All dimension scores and composite scores are rounded to one decimal place.

### Severity Band Mapping

| Severity Band | Score Range | SLA | Disposition |
|---------------|-------------|-----|-------------|
| Critical | 9.0 – 10.0 | 24h | Mitigate |
| High | 7.0 – 8.9 | 7d | Mitigate |
| Medium | 4.0 – 6.9 | 30d | Review |
| Low | 0.0 – 3.9 | 90d | Review |

Boundary values map to the higher band (e.g., 7.0 = High, 9.0 = Critical).

### Reachability Trust Zone Baseline

| Trust Level | Zone Examples | Baseline | Clamp Range |
|-------------|--------------|----------|-------------|
| Untrusted | User Zone, External Services | 9.0 | [8.0, 10.0] |
| Semi-Trusted | Device Zone | 5.5 | [4.0, 7.0] |
| Trusted | Backend Zone | 2.5 | [1.0, 4.0] |

**Applied reachability scores in this report**:
- User Zone (Untrusted baseline 9.0 + "user" keyword +0.5 = 9.5, within Untrusted range): **9.5**
- External Services (Untrusted baseline 9.0 + "external" keyword +0.5 = 9.5, within Untrusted range): **9.5**
- Device Zone (Semi-Trusted baseline 5.5, 1 network boundary −1.0 = 4.5, within Semi-Trusted range): **4.5**
- Backend Zone (Trusted baseline 2.5, "backend" keyword −0.5 = 2.0, 1 auth barrier −1.5, 2 network boundaries −2.0 = −1.5, clamped to Trusted floor): **1.0**

### Data Sources

- **Findings**: `examples/mobile-banking-app/sample-report/threats.md` (31 STRIDE findings; AI tables empty)
- **Trust zones**: Section 2 of `threats.md` (User Zone/Untrusted, Device Zone/Semi-Trusted, Backend Zone/Trusted, External Services/Untrusted)
- **Architecture context**: `examples/mobile-banking-app/architecture.md` (authentication barriers, network boundaries)
- **Category defaults**: `schemas/risk-scoring.yaml` → `category_defaults`
- **Scoring weights**: `schemas/risk-scoring.yaml` → `weights`

### Reproducibility

Scoring was performed at temperature 0. Individual dimension scores have a ±0.5 tolerance per dimension due to subjective sub-dimension assessment. Composite scores derived from the weighted formula are deterministic given the dimension inputs. This report was scored on 2026-04-29 (SOURCE_DATE_EPOCH=1700000000).
