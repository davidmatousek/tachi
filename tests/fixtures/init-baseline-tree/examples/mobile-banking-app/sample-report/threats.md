---
schema_version: "1.4"
date: "2026-04-29"
input_format: "mermaid"
classification: "confidential"
run_id: "2026-04-29T00-00-00"
baseline:
  source: null
  date: null
  finding_count: null
  run_id: null
coverage_gate:
  status: "pass"
  gaps: []
---

# WellnessBank Mobile Banking Application — Threat Model

## 1. System Overview

### Components

| Component | Type | Description |
|-----------|------|-------------|
| Mobile Banking Customer | External Entity | Retail banking end user operating the WellnessBank Android app; interacts via UI, adb shell, and Intent extras |
| Third-Party Analytics Provider | External Entity | External analytics platform receiving telemetry payloads from WellnessAnalyticsSDK over HTTPS |
| Third-Party Payment Provider | External Entity | External payment processor receiving payment authorization requests from WellnessPaySDK over HTTPS |
| WellnessBank Android Client | Process | Main Android application process (com.wellnessbank.mobile); handles credential storage, authentication, transaction requests, analytics/payment SDK orchestration; exposes mobile banking UI to the end user |
| WellnessBankDebugActivity | Process | Debug-only Android Activity retained in production release build with android:exported="true"; accessible via adb shell am start; no BuildConfig.DEBUG runtime guard; bypasses standard auth boundary into main client process |
| MoneyTransferActivity | Process | Exported Android Activity with android:exported="true" and no android:permission attribute; accepts Intent extras from external apps or shell directly into the money-movement business logic |
| WellnessAnalyticsSDK | Process | Third-party analytics SDK embedded in WellnessBank Android Client; performs outbound HTTPS telemetry to Third-Party Analytics Provider; no SDK signature verification; floating version constraint |
| WellnessPaySDK | Process | Third-party payment SDK embedded in WellnessBank Android Client; handles payment initiation and result relay; performs outbound HTTPS to Third-Party Payment Provider; no SDK signature verification |
| WellnessBank Backend API | Process | Mobile-backend REST API handling transaction processing, account reads/writes; TLS endpoint; no certificate pinning enforcement on client side |
| WellnessBankLocalDB | Data Store | On-device SQLite database caching account snapshots and recent transaction records; no SQLCipher encryption; allowBackup="true"; no scoped-storage migration |
| WellnessBankCredentialCache | Data Store | On-device SharedPreferences (MODE_PRIVATE) storing username and auth token; no EncryptedSharedPreferences; no Android Keystore binding |
| BackendUserAccountStore | Data Store | Backend relational database storing user account records; server-side surface |

### Data Flows

| Source | Destination | Data | Protocol |
|--------|-------------|------|----------|
| Mobile Banking Customer | WellnessBank Android Client | Login Credentials (UI Input) | In-app UI |
| WellnessBank Android Client | WellnessBankCredentialCache | Username + Auth Token | Internal Android IPC |
| WellnessBankCredentialCache | WellnessBank Android Client | Restored Credentials on App Launch | Internal Android IPC |
| WellnessBank Android Client | WellnessBankLocalDB | Account Snapshot + Recent Transactions | Local SQLite |
| WellnessBankLocalDB | WellnessBank Android Client | Cached Account Data | Local SQLite |
| WellnessBank Android Client | WellnessBank Backend API | Transaction Request | HTTPS |
| WellnessBank Backend API | WellnessBank Android Client | Transaction Response | HTTPS |
| WellnessBank Backend API | BackendUserAccountStore | Account Read / Write | Internal DB |
| BackendUserAccountStore | WellnessBank Backend API | Account Record | Internal DB |
| WellnessBank Android Client | WellnessAnalyticsSDK | Analytics Event | In-process |
| WellnessAnalyticsSDK | Third-Party Analytics Provider | Telemetry Payload | HTTPS |
| WellnessBank Android Client | WellnessPaySDK | Payment Initiation | In-process |
| WellnessPaySDK | Third-Party Payment Provider | Payment Authorization Request | HTTPS |
| Third-Party Payment Provider | WellnessPaySDK | Payment Confirmation | HTTPS |
| WellnessPaySDK | WellnessBank Android Client | Payment Result | In-process |
| Mobile Banking Customer | WellnessBankDebugActivity | adb shell am start (Debug Activity Bypass) | ADB / Intent |
| WellnessBankDebugActivity | WellnessBank Android Client | Privileged Action without Auth Boundary | Internal Android IPC |
| Mobile Banking Customer | MoneyTransferActivity | Intent Extras (External App or Shell) | Android Intent |
| MoneyTransferActivity | WellnessBank Android Client | Money-Movement Request | Internal Android IPC |

### Technologies

| Category | Technology | Version (if known) |
|----------|------------|--------------------|
| Mobile Platform | Android (com.wellnessbank.mobile package) | Unknown |
| Credential Storage | Android SharedPreferences MODE_PRIVATE | Platform-level |
| Local Database | SQLite (plain, no SQLCipher) | Platform-level |
| Cryptography | PBKDF2-HMAC-SHA1, 1000 iterations, no salt | Custom implementation |
| Transport | HTTPS (TLS without certificate pinning) | Platform default |
| Third-Party SDKs | WellnessAnalyticsSDK, WellnessPaySDK | Unknown |
| Build Tooling | Android Gradle (no ProGuard/R8 rules in release) | Unknown |
| Backend | REST API | Unknown |

---

## 2. Trust Boundaries

### Trust Zones

| Zone | Trust Level | Components |
|------|-------------|------------|
| User Zone | Untrusted | Mobile Banking Customer |
| Device Zone | Semi-Trusted | WellnessBank Android Client, WellnessBankDebugActivity, MoneyTransferActivity, WellnessAnalyticsSDK, WellnessPaySDK, WellnessBankLocalDB, WellnessBankCredentialCache |
| Backend Zone | Trusted | WellnessBank Backend API, BackendUserAccountStore |
| External Services | Untrusted | Third-Party Analytics Provider, Third-Party Payment Provider |

### Boundary Crossings

| Crossing | From Zone | To Zone | Components | Controls |
|----------|-----------|---------|------------|----------|
| User to Device (login) | User Zone | Device Zone | Mobile Banking Customer → WellnessBank Android Client | In-app authentication UI |
| Device to Backend (transaction) | Device Zone | Backend Zone | WellnessBank Android Client → WellnessBank Backend API | HTTPS (no certificate pinning) |
| Backend to Device (response) | Backend Zone | Device Zone | WellnessBank Backend API → WellnessBank Android Client | HTTPS (no certificate pinning) |
| Device to External (analytics) | Device Zone | External Services | WellnessAnalyticsSDK → Third-Party Analytics Provider | HTTPS (no certificate pinning) |
| Device to External (payment) | Device Zone | External Services | WellnessPaySDK → Third-Party Payment Provider | HTTPS (no certificate pinning) |
| External to Device (payment result) | External Services | Device Zone | Third-Party Payment Provider → WellnessPaySDK | HTTPS (no certificate pinning) |
| User to Device (debug bypass) | User Zone | Device Zone | Mobile Banking Customer → WellnessBankDebugActivity | None — no auth gate |
| User to Device (intent) | User Zone | Device Zone | Mobile Banking Customer → MoneyTransferActivity | None — no permission gate |

---

## 3. STRIDE Threat Tables

### 3.1 Spoofing (S)

| ID | Status | Component | MAESTRO Layer | Threat | Likelihood | Impact | Risk Level | Mitigation |
|----|--------|-----------|---------------|--------|------------|--------|------------|------------|
| S-1 | [NEW] | WellnessBank Android Client | L7 — Agent Ecosystem | **Improper Mobile Credential Usage (M1)**: Auth token and username persisted in Android SharedPreferences MODE_PRIVATE without EncryptedSharedPreferences or Android Keystore binding. Attacker recovering a lost, stolen, or rooted device can dump the app's data partition and extract long-lived credentials, achieving full account impersonation without any PIN or biometric challenge. | HIGH | HIGH | Critical | Migrate credential storage to Android Keystore + EncryptedSharedPreferences (Jetpack Security). Bind key release to BiometricPrompt.CryptoObject with StrongBox-backed keys. Rotate session and refresh tokens on every use with server-side revocation. References: OWASP M1:2024; OWASP MASTG-AUTH; CWE-287; CWE-312 |
| S-2 | [NEW] | WellnessBank Android Client | L7 — Agent Ecosystem | **Insecure Mobile Authentication/Authorization (M3)**: No biometric step-up on money-movement operations; no per-session token re-authentication on sensitive actions; no challenge-response on transaction confirmation; no risk-based MFA. An attacker who obtains a valid session token can execute fund transfers without any biometric or secondary-factor challenge. | HIGH | HIGH | Critical | Enforce BiometricPrompt step-up authentication on all money-movement, profile-change, and KYC operations. Bind refresh tokens to device fingerprint using Play Integrity API attestation; rotate on every refresh. Enforce server-side re-validation on all sensitive API endpoints. References: OWASP M3:2024; OWASP MASTG-AUTH; OWASP MASVS-AUTH; CWE-308 |
| S-3 | [NEW] | WellnessBank Android Client | L7 — Agent Ecosystem | **Credential Theft via SharedPreferences Extraction**: Long-lived auth tokens stored in MODE_PRIVATE SharedPreferences are accessible to an attacker who roots the device or uses ADB backup on pre-Android-12 devices. No live user presence is required for offline credential recovery. | MEDIUM | HIGH | High | Replace SharedPreferences with EncryptedSharedPreferences backed by Android Keystore. Enforce credential rotation policy; ensure refresh token has short TTL and is bound to device fingerprint. References: OWASP M1:2024; CWE-312 |
| S-4 | [NEW] | WellnessBank Backend API | L7 — Agent Ecosystem | **Missing Token Binding on Backend Session**: The backend API accepts HTTPS bearer tokens without certificate pinning on the client side, enabling token replay from intercepted sessions. No device-binding means a captured token is replayable from any device. | MEDIUM | MEDIUM | Medium | Implement token binding (DPoP or mTLS certificate-bound tokens) on the backend API. Verify device attestation (Play Integrity) server-side on transaction-confirmation calls. References: OWASP A07:2021; CWE-287 |
| S-5 | [NEW] | Mobile Banking Customer | L7 — Agent Ecosystem | **Long-Lived Session Token Replay**: Auth tokens persisted on device without rotation policy or revocation trigger. An attacker obtaining the token can replay it indefinitely with no expiry enforcement. | MEDIUM | HIGH | High | Enforce short-lived session tokens (max 15 min TTL); implement refresh token rotation with revocation on suspicious signals (new device, unusual location). References: OWASP A07:2021; CWE-613 |

### 3.2 Tampering (T)

| ID | Status | Component | MAESTRO Layer | Threat | Likelihood | Impact | Risk Level | Mitigation |
|----|--------|-----------|---------------|--------|------------|--------|------------|------------|
| T-1 | [NEW] | WellnessAnalyticsSDK | Unclassified | **Mobile Supply Chain Integrity (M2) — Analytics SDK**: No checksum verification on WellnessAnalyticsSDK artifact at Gradle ingestion; floating version constraint. A compromised analytics SDK maintainer can inject malicious code executing inside the app's full security context, exfiltrating session tokens from SharedPreferences. Cf. MITRE ATT&CK T1474 — prose-only; not in references per ADR-036 D-7. | MEDIUM | HIGH | High | Pin WellnessAnalyticsSDK to exact version with Gradle integrity constraints. Establish supplier provenance review gate before any SDK upgrade. Require SLSA Level-3 attestation on release APK artifacts. References: OWASP M2:2024; OWASP MASTG-ARCH; MITRE ATT&CK T1195.001; CWE-494 |
| T-2 | [NEW] | WellnessPaySDK | Unclassified | **Mobile Supply Chain Integrity (M2) — Payment SDK**: No checksum verification on WellnessPaySDK artifact; floating version constraint. A compromised payment SDK can intercept or modify payment authorization requests before they leave the device. Cf. MITRE ATT&CK T1474 — prose-only; not in references per ADR-036 D-7. | MEDIUM | HIGH | High | Pin WellnessPaySDK to exact version with Gradle integrity constraints. Enforce app-store-only distribution. Require signed-artifact policy on payment SDK ingestion. References: OWASP M2:2024; MITRE ATT&CK T1195.002; CWE-494 |
| T-3 | [NEW] | MoneyTransferActivity | Unclassified | **Mobile IPC Input Validation (M4) — Intent Hijacking into Money Movement**: Exported MoneyTransferActivity with android:exported="true" and no android:permission accepts Intent extras (recipient_account, amount) from any installed app or ADB shell directly into the money-movement flow without re-authentication, schema validation, or per-Intent caller verification. A malicious co-installed app can initiate unauthorized fund transfers under the legitimate user's authenticated session. | HIGH | HIGH | Critical | Set android:exported="false" unless cross-app invocation is required. If exported, declare android:permission with signature protection level. Validate all Intent extras against a strict schema; require re-authentication on every money-movement invocation. References: OWASP M4:2024; OWASP MASTG-CODE; OWASP MASVS-PLATFORM; CWE-20; CWE-862 |
| T-4 | [NEW] | WellnessBank Android Client | L7 — Agent Ecosystem | **Insufficient Mobile Binary Protections (M7)**: No ProGuard/R8 obfuscation in release build; no root-detection on security-critical features; no anti-tampering integrity check at startup; no debugger detection at sensitive-flow boundaries. An attacker can use Frida to hook security-critical functions, bypass client-side controls, and extract embedded API keys and session-handling logic. Cf. MITRE ATT&CK T1626 — prose-only; not in references per ADR-036 D-7. | HIGH | HIGH | Critical | Enable ProGuard/R8 (`minifyEnabled true`, `shrinkResources true`) in the release build. Integrate Play Integrity API on security-critical flows. Implement RASP with anti-tampering stubs and APK-signature integrity self-check. References: OWASP M7:2024; OWASP MASTG-RESILIENCE; OWASP MASVS-RESILIENCE |
| T-5 | [NEW] | WellnessBankLocalDB | L2 — Data Operations | **Unencrypted Local Database Tampering**: Plain SQLite database with no SQLCipher encryption. Attacker with root access or ADB access can directly modify transaction records, account snapshots, and cached data, enabling fabricated transaction history or balance manipulation. | MEDIUM | HIGH | High | Encrypt WellnessBankLocalDB using SQLCipher with a Keystore-bound key. Set allowBackup="false" with explicit Android 12+ backup rules excluding the database. References: OWASP M9:2024; OWASP MASTG-STORAGE; CWE-311 |
| T-6 | [NEW] | WellnessBankCredentialCache | L2 — Data Operations | **Credential Cache Tampering via SharedPreferences Overwrite**: SharedPreferences MODE_PRIVATE file is writable on a rooted device. Attacker can overwrite the credential store to inject forged auth tokens or corrupt cached credentials, enabling session hijacking. | MEDIUM | HIGH | High | Migrate to EncryptedSharedPreferences backed by Android Keystore. Apply file integrity validation at read time. References: OWASP M1:2024; OWASP M9:2024; CWE-312 |

### 3.3 Repudiation (R)

| ID | Status | Component | MAESTRO Layer | Threat | Likelihood | Impact | Risk Level | Mitigation |
|----|--------|-----------|---------------|--------|------------|--------|------------|------------|
| R-1 | [NEW] | WellnessBank Android Client | L7 — Agent Ecosystem | **M8 Accountability-Loss: Mobile Audit Log Gaps**: No structured audit logging on login, logout, step-up, or money-movement events; debug Log.d("auth", "user=" + username + " token=" + token) retained in release build leaks credentials to on-device logcat; no tamper-evident timestamping; no off-device forwarding to immutable store. Forensics cannot reconstruct client-side auth context for dispute resolution. Cf. MITRE ATT&CK T1398 — prose-only; not in references per ADR-036 D-7. | HIGH | HIGH | Critical | Emit structured audit log entries on every auth state transition with outcome, UTC timestamp, and correlation ID. Gate all Log.d/Log.v calls on BuildConfig.DEBUG. Add server-attested timestamps (RFC 3161) to transaction audit records. Forward audit records off-device to an immutable backend audit pipeline. References: OWASP M8:2024; CWE-778; CWE-223; OWASP MASVS-CODE |
| R-2 | [NEW] | WellnessBank Backend API | L7 — Agent Ecosystem | **Missing Backend Audit Trail on Transaction Operations**: No declared audit event emission on money-movement, account-read, or account-write operations at the backend API. Privileged operations cannot be forensically reconstructed for dispute resolution or regulatory audit. | MEDIUM | HIGH | High | Instrument every privileged backend decision point with synchronous structured audit event emission before effect; forward to SIEM or write-once bucket. Include actor identity, action, UTC timestamp, resource URN, outcome. References: OWASP A09:2021; CWE-778; CWE-223 |
| R-3 | [NEW] | Mobile Banking Customer | L7 — Agent Ecosystem | **Deniable Financial Transactions**: No non-repudiation controls on money-movement operations. A customer can plausibly deny initiating any transfer with no cryptographic evidence of user intent available to the bank. | MEDIUM | MEDIUM | Medium | Implement transaction signing at the app layer using BiometricPrompt.CryptoObject (StrongBox-backed). Retain signed transaction records server-side as non-repudiation evidence. References: OWASP A09:2021; CWE-345 |
| R-4 | [NEW] | WellnessBankDebugActivity | Unclassified | **Unlogged Debug Activity Invocations**: Debug Activity invocations via adb shell am start or external Intent are not audit logged. Privileged actions executed through the debug channel leave no accountability trail. | MEDIUM | HIGH | High | Strip WellnessBankDebugActivity from release builds. In the interim, emit a security audit event on every invocation including caller identity and invoked operation. References: OWASP M8:2024; CWE-778 |

### 3.4 Information Disclosure (I)

| ID | Status | Component | MAESTRO Layer | Threat | Likelihood | Impact | Risk Level | Mitigation |
|----|--------|-----------|---------------|--------|------------|--------|------------|------------|
| I-1 | [NEW] | WellnessBank Android Client | L7 — Agent Ecosystem | **Insecure Mobile Communication (M5) — Client-to-Backend**: TLS to WellnessBank Backend API without certificate pinning (no OkHttp CertificatePinner, no Network Security Config pin-set). An attacker on a rogue Wi-Fi access point can MITM the TLS session, intercepting session tokens, transaction payloads, account balances, and PII in transit. | HIGH | HIGH | Critical | Configure OkHttp CertificatePinner with primary + backup pins on all backend hosts. Declare pin-set in network_security_config.xml. Set minimum TLS version to TLS 1.3; reject RC4/3DES. References: OWASP M5:2024; OWASP MASTG-NETWORK; OWASP MASVS-NETWORK; CWE-295 |
| I-2 | [NEW] | WellnessBank Android Client | L7 — Agent Ecosystem | **Inadequate Mobile Privacy Controls (M6)**: No FLAG_SECURE on transaction-history Activity Window; recents-screen screenshots and screen-recording capture account balances, transaction amounts, and recipient names. No privacy-consent gate on analytics emission. PII cached indefinitely in WellnessBankLocalDB with no TTL expiry. | HIGH | HIGH | Critical | Apply FLAG_SECURE to all Activity Windows rendering PII or financial data. Implement privacy-consent gate before initializing analytics SDK. Apply data-minimization on caches with TTL enforcement. References: OWASP M6:2024; OWASP MASTG-PRIVACY; OWASP MASVS-PRIVACY; CWE-200 |
| I-3 | [NEW] | WellnessBankLocalDB | L2 — Data Operations | **Insecure Mobile Data Storage (M9) — Local Database**: Unencrypted SQLite database with allowBackup="true" exposes full transaction history and account snapshots to Google Drive cloud backup. Attacker compromising the user's Google account can recover complete financial history without bypassing device authentication. | HIGH | HIGH | Critical | Encrypt WellnessBankLocalDB via SQLCipher with Keystore-bound key. Set allowBackup="false" or define explicit Android 12+ backup rules excluding the database. Apply database TTL eviction policy. References: OWASP M9:2024; OWASP MASTG-STORAGE; OWASP MASVS-STORAGE; CWE-311; CWE-312 |
| I-4 | [NEW] | WellnessBank Android Client | L7 — Agent Ecosystem | **Insufficient Mobile Cryptography (M10)**: Custom key derivation from 4-digit PIN via PBKDF2-HMAC-SHA1 with 1000 iterations and no salting. The 10,000-PIN keyspace is exhausted in under one second on commodity GPU hardware. No platform-managed KMS key wrapping; no envelope encryption on cached credentials; no key rotation policy. | HIGH | HIGH | Critical | Replace PIN-based KDF with Argon2id or PBKDF2-HMAC-SHA256 at ≥600,000 iterations with per-device unique salt. Wrap the PIN-derived key with an Android Keystore-bound hardware key in an envelope-encryption scheme. References: OWASP M10:2024; OWASP MASTG-CRYPTO; OWASP MASVS-CRYPTO; CWE-916; CWE-321 |
| I-5 | [NEW] | WellnessAnalyticsSDK | Unclassified | **Insecure Mobile Communication (M5) — Analytics SDK Egress**: TLS from WellnessAnalyticsSDK to Third-Party Analytics Provider without certificate pinning. Analytics telemetry (including device identifiers, session metadata, user behavior patterns) can be intercepted on untrusted networks. | MEDIUM | MEDIUM | Medium | Configure certificate pinning on the analytics SDK egress flow. Review SDK telemetry content for PII; apply privacy-consent gate before initialization. References: OWASP M5:2024; CWE-295 |
| I-6 | [NEW] | WellnessPaySDK | Unclassified | **Insecure Mobile Communication (M5) — Payment SDK Egress**: TLS from WellnessPaySDK to Third-Party Payment Provider without certificate pinning. Payment authorization requests (including payment card data and transaction amounts) can be intercepted via MITM on rogue Wi-Fi. | MEDIUM | HIGH | High | Configure certificate pinning on WellnessPaySDK egress to payment provider. Enforce minimum TLS 1.3. References: OWASP M5:2024; OWASP MASVS-NETWORK; CWE-295 |
| I-7 | [NEW] | WellnessBankCredentialCache | L2 — Data Operations | **Insecure Mobile Data Storage (M9) — Credential Cache**: Auth tokens stored in plaintext SharedPreferences MODE_PRIVATE accessible to any process with root access or via ADB backup on older Android versions. The credential cache contains long-lived session tokens sufficient for full account access without any PIN or biometric re-challenge. | HIGH | HIGH | Critical | Migrate WellnessBankCredentialCache to EncryptedSharedPreferences (Jetpack Security) backed by Android Keystore. Enforce allowBackup="false". Implement credential TTL and rotation policy. References: OWASP M1:2024; OWASP M9:2024; CWE-312; CWE-311 |
| I-8 | [NEW] | WellnessBank Android Client | L7 — Agent Ecosystem | **Debug Log PII Leakage via Logcat**: Debug Log.d("auth", "user=" + username + " token=" + token) retained in the release build writes authentication material (username and session token) to the device-shared logcat sink accessible to other privileged apps or root shell. Any app holding READ_LOGS on older Android can harvest credentials from logcat in real time. | HIGH | HIGH | Critical | Gate all Log.d/Log.v/Log.w calls on BuildConfig.DEBUG via a logging facade (Timber). Replace sensitive-context logs with redacted structured entries. Run a lint rule (LogDetector) in CI to fail the build on unguarded Log.d usage. References: OWASP M8:2024; CWE-532; OWASP MASTG-CODE |
| I-9 | [NEW] | WellnessBank Backend API | L7 — Agent Ecosystem | **Backend API Verbose Error Response Exposure**: Mobile-backend REST APIs without declared error sanitization may return stack traces, internal service names, database field names, or configuration details in error responses visible to the mobile client. | LOW | MEDIUM | Low | Implement centralized error handling that returns generic error codes to clients; log full error context server-side only. Never serialize internal exceptions or ORM error objects in client-facing responses. References: OWASP A05:2021; CWE-209 |

### 3.5 Denial of Service (D)

| ID | Status | Component | MAESTRO Layer | Threat | Likelihood | Impact | Risk Level | Mitigation |
|----|--------|-----------|---------------|--------|------------|--------|------------|------------|
| D-1 | [NEW] | WellnessBank Android Client | L7 — Agent Ecosystem | **Client-Side Resource Exhaustion via Unconstrained SDK I/O**: Third-party analytics and payment SDKs perform unconstrained outbound network I/O with no rate limiting, circuit breaker, or battery-aware scheduling. A misbehaving or compromised SDK version can saturate device battery and network resources, degrading app availability for the legitimate user. | LOW | MEDIUM | Low | Implement circuit breakers and rate limits on SDK I/O calls. Schedule analytics emission in batches during app-idle periods. Monitor SDK network usage against a declared baseline. |
| D-2 | [NEW] | WellnessBank Backend API | L7 — Agent Ecosystem | **Missing Rate Limiting on Backend Transaction API**: No declared rate limiting or request throttling on the mobile backend REST API. High-volume transaction requests from compromised or cloned client apps can saturate backend processing capacity. | MEDIUM | HIGH | High | Implement per-device rate limiting on all transaction endpoints (max 10 transfers/minute/device). Deploy WAF with DDoS mitigation. Require Play Integrity attestation on transaction requests to reject non-genuine clients. References: OWASP A05:2021; CWE-400 |
| D-3 | [NEW] | WellnessBankLocalDB | L2 — Data Operations | **Local Database Saturation**: Uncontrolled caching in WellnessBankLocalDB can grow without bound, saturating device storage and causing application crashes or OS-level storage exhaustion. | LOW | LOW | Note | Implement cache eviction policies with maximum row count and TTL-based expiry. Monitor local DB size in analytics events. |
| D-4 | [NEW] | WellnessBankCredentialCache | L2 — Data Operations | **Credential Store Corruption Leading to Denial of Service**: Targeted corruption of SharedPreferences credential cache can trigger authentication failures and re-login loops, effectively locking out the legitimate user. | LOW | MEDIUM | Low | Implement HMAC integrity validation on cached credential entries. Provide clear recovery path (reset credentials via server-side re-auth) when cache integrity check fails. |

### 3.6 Elevation of Privilege (E)

| ID | Status | Component | MAESTRO Layer | Threat | Likelihood | Impact | Risk Level | Mitigation |
|----|--------|-----------|---------------|--------|------------|--------|------------|------------|
| E-1 | [NEW] | WellnessBankDebugActivity | Unclassified | **M8 Privilege-Gain: Exported Debug Activity Bypassing Auth Boundary**: WellnessBankDebugActivity retained in production release build with android:exported="true"; accessible via `adb shell am start`; no BuildConfig.DEBUG runtime guard; no Play Integrity attestation gate; privileged-action flow connects directly to WellnessBank Android Client bypassing the standard authentication boundary. Any process or user with ADB access can invoke privileged banking operations without authentication. Cf. MITRE ATT&CK T1626 — prose-only; not in references per ADR-036 D-7. | HIGH | HIGH | Critical | Strip WellnessBankDebugActivity from release builds via Android Gradle build-flavor configuration. Implement build-time validation asserting no `*Debug*` components ship in release artifacts. Integrate Play Integrity API on all privileged-action paths. References: OWASP M8:2024; CWE-732; OWASP MASVS-PLATFORM; OWASP MASTG-RESILIENCE |
| E-2 | [NEW] | MoneyTransferActivity | Unclassified | **Unauthorized Money Transfer via Intent Hijacking and Privilege Escalation**: Exported MoneyTransferActivity with no android:permission allows any installed app to invoke the money-movement flow. Combined with missing re-authentication at Activity entry, a malicious co-installed app escalates from unprivileged-app context to authenticated-banking-session context, executing fund transfers without any user interaction. | HIGH | HIGH | Critical | Set android:exported="false" or enforce android:permission with signature protection level. Require re-authentication at every money-movement Activity entry. Implement per-Intent caller verification (getCallingPackage() with package allowlist). References: OWASP M8:2024; OWASP M4:2024; CWE-862; CWE-732 |
| E-3 | [NEW] | WellnessBank Backend API | L7 — Agent Ecosystem | **Server-Side Authorization Gap for Debug-Initiated Operations**: Backend API may accept operations initiated via the debug Activity's privileged-action flow relying solely on the client's authenticated session token, without verifying whether the invoking context represents a legitimate in-app user action or a debug-channel bypass. | MEDIUM | HIGH | High | Implement server-side intent-source validation or require step-up authentication tokens for sensitive operations. Reject requests that cannot be traced to a legitimate user-initiated in-app action via Play Integrity API attestation. References: OWASP A01:2021; CWE-862 |

---

## 4. AI Threat Tables

### 4.1 Agentic Threats (AG)

No AI-related components were identified in the architecture input. No AG keywords (agent, autonomous, orchestrator, MCP server, tool server, plugin) matched any component name or description.

| ID | Status | Component | MAESTRO Layer | Threat | OWASP Reference | Likelihood | Impact | Risk Level | Mitigation |
|----|--------|-----------|---------------|--------|------------------|------------|--------|------------|------------|

### 4.2 LLM Threats (LLM)

No AI-related components were identified in the architecture input. No LLM keywords (LLM, model, GPT, Claude) matched any component name or description.

| ID | Status | Component | MAESTRO Layer | Threat | OWASP Reference | Likelihood | Impact | Risk Level | Mitigation |
|----|--------|-----------|---------------|--------|------------------|------------|--------|------------|------------|

---

## 4a. Correlated Findings

No cross-agent correlations detected. No AI agents were dispatched for this architecture; correlation rules CR-1 through CR-5 require at least one STRIDE and one AI finding targeting the same component.

| Group | Findings | Component | Threat Summary | Risk Level |
|-------|----------|-----------|----------------|------------|

---

## 5. Coverage Matrix

| Component | S | T | R | I | D | E | AG | LLM | Total |
|-----------|---|---|---|---|---|---|----|-----|-------|
| Mobile Banking Customer | 1 | n/a | 1 | n/a | n/a | n/a | n/a | n/a | 2 |
| Third-Party Analytics Provider | --- | n/a | --- | n/a | n/a | n/a | n/a | n/a | 0 |
| Third-Party Payment Provider | --- | n/a | --- | n/a | n/a | n/a | n/a | n/a | 0 |
| WellnessBank Android Client | 3 | 1 | 1 | 5 | 1 | --- | n/a | n/a | 11 |
| WellnessBankDebugActivity | --- | --- | 1 | --- | --- | 1 | n/a | n/a | 2 |
| MoneyTransferActivity | --- | 1 | --- | --- | --- | 1 | n/a | n/a | 2 |
| WellnessAnalyticsSDK | --- | 1 | --- | 1 | --- | --- | n/a | n/a | 2 |
| WellnessPaySDK | --- | 1 | --- | 1 | --- | --- | n/a | n/a | 2 |
| WellnessBank Backend API | 1 | --- | 1 | 1 | 1 | 1 | n/a | n/a | 5 |
| WellnessBankLocalDB | n/a | 1 | n/a | 1 | 1 | n/a | n/a | n/a | 3 |
| WellnessBankCredentialCache | n/a | 1 | n/a | 1 | 1 | n/a | n/a | n/a | 3 |
| BackendUserAccountStore | n/a | --- | n/a | --- | --- | n/a | n/a | n/a | 0 |
| **Total** | **5** | **6** | **4** | **10** | **4** | **3** | **—** | **—** | **32** |

`---` = analyzed, zero findings. `n/a` = not applicable per STRIDE-per-Element rules.

### 5a. Coverage Gate Results

| Component | Determined Type | Required Categories | Evaluated | Gaps |
|-----------|-----------------|--------------------|-----------|----|
| Mobile Banking Customer | external_entity | spoofing, repudiation | spoofing ✓, repudiation ✓ | None |
| Third-Party Analytics Provider | external_entity | spoofing, repudiation | spoofing (clean), repudiation (clean) | None |
| Third-Party Payment Provider | external_entity | spoofing, repudiation | spoofing (clean), repudiation (clean) | None |
| WellnessBank Android Client | process | spoofing, tampering, repudiation, info-disclosure, denial-of-service, privilege-escalation | All covered | None |
| WellnessBankDebugActivity | process | spoofing, tampering, repudiation, info-disclosure, denial-of-service, privilege-escalation | E-1, R-4 covered; S/T/I/D clean | None |
| MoneyTransferActivity | process | spoofing, tampering, repudiation, info-disclosure, denial-of-service, privilege-escalation | T-3, E-2 covered; S/R/I/D clean | None |
| WellnessAnalyticsSDK | process | spoofing, tampering, repudiation, info-disclosure, denial-of-service, privilege-escalation | T-1, I-5 covered; S/R/D/E clean | None |
| WellnessPaySDK | process | spoofing, tampering, repudiation, info-disclosure, denial-of-service, privilege-escalation | T-2, I-6 covered; S/R/D/E clean | None |
| WellnessBank Backend API | process | spoofing, tampering, repudiation, info-disclosure, denial-of-service, privilege-escalation | S-4, R-2, I-9, D-2, E-3 covered; T clean | None |
| WellnessBankLocalDB | data_store | tampering, info-disclosure, denial-of-service | T-5, I-3, D-3 covered | None |
| WellnessBankCredentialCache | data_store | tampering, info-disclosure, denial-of-service | T-6, I-7, D-4 covered | None |
| BackendUserAccountStore | data_store | tampering, info-disclosure, denial-of-service | All clean (no findings) | None |

**Coverage Gate Status: PASS** — All required categories evaluated for all components.

---

## 6. Risk Summary

### Risk Calibration Matrix

|                   | LOW Likelihood | MEDIUM Likelihood | HIGH Likelihood |
|-------------------|----------------|-------------------|-----------------|
| **HIGH Impact**   | Medium         | High              | Critical        |
| **MEDIUM Impact** | Low            | Medium            | High            |
| **LOW Impact**    | Note           | Low               | Medium          |

| Risk Level | Count | Percentage |
|------------|-------|------------|
| Critical | 13 | 40.6% |
| High | 11 | 34.4% |
| Medium | 3 | 9.4% |
| Low | 4 | 12.5% |
| Note | 1 | 3.1% |
| **Total** | **32** | **100%** |

### Risk by MAESTRO Layer

| MAESTRO Layer | Finding Count | Highest Severity |
|---------------|---------------|------------------|
| L7 — Agent Ecosystem | 21 | Critical |
| L2 — Data Operations | 7 | Critical |
| Unclassified | 4 | Critical |

---

## 7. Recommended Actions

| Finding ID | Component | Threat | Risk Level | Mitigation |
|------------|-----------|--------|------------|------------|
| S-1 | WellnessBank Android Client | Improper Mobile Credential Usage (M1): Auth token in SharedPreferences without Keystore binding | Critical | Migrate to Android Keystore + EncryptedSharedPreferences; bind key release to BiometricPrompt.CryptoObject; rotate tokens on every use |
| S-2 | WellnessBank Android Client | Insecure Mobile Authentication/Authorization (M3): No biometric step-up on money-movement | Critical | Enforce BiometricPrompt step-up on all sensitive operations; bind refresh tokens to Play Integrity attestation |
| T-3 | MoneyTransferActivity | Mobile IPC Input Validation (M4): Exported Activity accepts Intent extras without auth or permission gate | Critical | Set android:exported="false" or declare signature-level permission; require re-auth on every invocation; validate all Intent extras |
| T-4 | WellnessBank Android Client | Insufficient Mobile Binary Protections (M7): No obfuscation, no root detection, no RASP | Critical | Enable ProGuard/R8; integrate Play Integrity API; add RASP anti-tampering stubs and APK signature integrity check |
| R-1 | WellnessBank Android Client | M8 Accountability-Loss: Missing audit logging; Log.d leakage in release build | Critical | Emit structured audit events on all auth state transitions; gate Log.d on BuildConfig.DEBUG; forward audit records off-device to immutable store |
| I-1 | WellnessBank Android Client | Insecure Mobile Communication (M5): No certificate pinning on client-to-backend TLS | Critical | Configure OkHttp CertificatePinner + Network Security Config pin-set across all environments |
| I-2 | WellnessBank Android Client | Inadequate Mobile Privacy Controls (M6): No FLAG_SECURE; PII in recents screenshots | Critical | Apply FLAG_SECURE to all financial Activity Windows; consent-gate analytics SDK; enforce cache TTL |
| I-3 | WellnessBankLocalDB | Insecure Mobile Data Storage (M9): Unencrypted SQLite; allowBackup="true" | Critical | Encrypt via SQLCipher with Keystore-bound key; set allowBackup="false" |
| I-4 | WellnessBank Android Client | Insufficient Mobile Cryptography (M10): PBKDF2 at 1000 iterations, no salt, 4-digit PIN space | Critical | Replace with Argon2id/PBKDF2-SHA256 ≥600K iterations + per-device salt; envelope-encrypt with Keystore-bound hardware key |
| I-7 | WellnessBankCredentialCache | Insecure Mobile Data Storage (M9): Auth tokens in plaintext SharedPreferences | Critical | Migrate to EncryptedSharedPreferences; set allowBackup="false" |
| I-8 | WellnessBank Android Client | Debug Log PII Leakage via Logcat: credentials in release build logcat | Critical | Gate all Log.d/Log.v on BuildConfig.DEBUG; run LogDetector lint rule in CI |
| E-1 | WellnessBankDebugActivity | M8 Privilege-Gain: Exported debug Activity retained in production bypassing auth | Critical | Strip debug Activity from release builds via build-flavor config; add build-time validation; integrate Play Integrity on privileged paths |
| E-2 | MoneyTransferActivity | Unauthorized Money Transfer via Intent Hijacking: No permission gate on exported Activity | Critical | Set android:exported="false" or signature-level permission; require re-auth at every money-movement entry |
| S-3 | WellnessBank Android Client | Credential Theft via SharedPreferences extraction on rooted device | High | EncryptedSharedPreferences + Keystore; enforce credential rotation; short-lived tokens |
| S-5 | Mobile Banking Customer | Long-lived session token replay: no rotation or expiry | High | Short-lived session tokens (15 min TTL); refresh token rotation with revocation |
| T-1 | WellnessAnalyticsSDK | Mobile Supply Chain Integrity (M2): No checksum on analytics SDK artifact | High | Pin SDK to exact version with Gradle integrity constraints; supplier provenance review gate |
| T-2 | WellnessPaySDK | Mobile Supply Chain Integrity (M2): No checksum on payment SDK artifact | High | Pin SDK to exact version with Gradle integrity constraints; app-store-only distribution |
| T-5 | WellnessBankLocalDB | Unencrypted local database tampering via root/ADB access | High | SQLCipher encryption with Keystore-bound key; allowBackup="false" |
| T-6 | WellnessBankCredentialCache | Credential cache overwrite via rooted device | High | EncryptedSharedPreferences; Keystore-bound encryption |
| R-2 | WellnessBank Backend API | Missing backend audit trail on transaction operations | High | Structured audit events on all privileged backend operations; SIEM/write-once bucket |
| R-4 | WellnessBankDebugActivity | Unlogged debug Activity invocations | High | Strip from release builds; emit audit event on any debug Activity invocation |
| I-6 | WellnessPaySDK | Insecure Mobile Communication (M5): No cert pinning on payment SDK egress | High | Certificate pinning on WellnessPaySDK → payment provider TLS flow |
| D-2 | WellnessBank Backend API | Missing rate limiting on transaction API | High | Per-device rate limiting; WAF; Play Integrity client verification |
| E-3 | WellnessBank Backend API | Server-side authorization gap for debug-initiated operations | High | Play Integrity attestation on sensitive backend operations; reject unverified client contexts |
| S-4 | WellnessBank Backend API | Missing token binding on backend session | Medium | Implement DPoP or mTLS token binding; verify Play Integrity server-side |
| R-3 | Mobile Banking Customer | Deniable financial transactions: no non-repudiation controls | Medium | Transaction signing with BiometricPrompt.CryptoObject + StrongBox-bound key |
| I-5 | WellnessAnalyticsSDK | Insecure Mobile Communication (M5): No cert pinning on analytics SDK egress | Medium | Certificate pinning on analytics SDK egress; review telemetry content for PII |
| D-1 | WellnessBank Android Client | Client-side resource exhaustion via unconstrained SDK I/O | Low | Circuit breakers and rate limits on SDK I/O; battery-aware scheduling |
| D-4 | WellnessBankCredentialCache | Credential store corruption leading to denial of service | Low | HMAC integrity validation on cached credentials; clear recovery path |
| I-9 | WellnessBank Backend API | Backend API verbose error response exposure | Low | Centralized error handling returning generic codes to client; log full context server-side only |
| D-3 | WellnessBankLocalDB | Local database saturation | Note | Cache eviction policies with max row count and TTL expiry; monitor DB size via analytics |

---

## 9. Source Attribution


Per-finding attribution to external taxonomy frameworks (OWASP, CWE, MITRE ATT&CK, MITRE ATLAS, NIST AI RMF). Populated by F-241 Wave 5.2 / T054-T055 net-new baseline regen. Each entry resolves against `schemas/taxonomy/*.yaml` per F-A2 referential-integrity contract.


```yaml
D-1:
  - {taxonomy: owasp, id: A04, relationship: primary}
  - {taxonomy: cwe, id: CWE-400, relationship: related}
D-2:
  - {taxonomy: owasp, id: A04, relationship: primary}
  - {taxonomy: cwe, id: CWE-400, relationship: related}
D-3:
  - {taxonomy: owasp, id: A04, relationship: primary}
  - {taxonomy: cwe, id: CWE-770, relationship: related}
D-4:
  - {taxonomy: owasp, id: A04, relationship: primary}
  - {taxonomy: cwe, id: CWE-400, relationship: related}
E-1:
  - {taxonomy: owasp, id: M8, relationship: primary}
  - {taxonomy: cwe, id: CWE-285, relationship: related}
E-2:
  - {taxonomy: owasp, id: M8, relationship: primary}
  - {taxonomy: cwe, id: CWE-862, relationship: related}
E-3:
  - {taxonomy: owasp, id: A01, relationship: primary}
  - {taxonomy: cwe, id: CWE-862, relationship: related}
I-1:
  - {taxonomy: owasp, id: M5, relationship: primary}
  - {taxonomy: cwe, id: CWE-200, relationship: related}
I-2:
  - {taxonomy: owasp, id: M6, relationship: primary}
  - {taxonomy: cwe, id: CWE-200, relationship: related}
I-3:
  - {taxonomy: owasp, id: M9, relationship: primary}
  - {taxonomy: cwe, id: CWE-200, relationship: related}
I-4:
  - {taxonomy: owasp, id: M10, relationship: primary}
  - {taxonomy: cwe, id: CWE-200, relationship: related}
I-5:
  - {taxonomy: owasp, id: M5, relationship: primary}
  - {taxonomy: cwe, id: CWE-200, relationship: related}
I-6:
  - {taxonomy: owasp, id: M5, relationship: primary}
  - {taxonomy: cwe, id: CWE-200, relationship: related}
I-7:
  - {taxonomy: owasp, id: M9, relationship: primary}
  - {taxonomy: cwe, id: CWE-522, relationship: related}
I-8:
  - {taxonomy: owasp, id: M8, relationship: primary}
  - {taxonomy: cwe, id: CWE-532, relationship: related}
I-9:
  - {taxonomy: owasp, id: A05, relationship: primary}
  - {taxonomy: cwe, id: CWE-209, relationship: related}
R-1:
  - {taxonomy: owasp, id: M8, relationship: primary}
  - {taxonomy: cwe, id: CWE-778, relationship: related}
R-2:
  - {taxonomy: owasp, id: A09, relationship: primary}
  - {taxonomy: cwe, id: CWE-778, relationship: related}
R-3:
  - {taxonomy: owasp, id: A09, relationship: primary}
  - {taxonomy: cwe, id: CWE-345, relationship: related}
R-4:
  - {taxonomy: owasp, id: M8, relationship: primary}
  - {taxonomy: cwe, id: CWE-778, relationship: related}
S-1:
  - {taxonomy: owasp, id: M1, relationship: primary}
  - {taxonomy: cwe, id: CWE-522, relationship: related}
S-2:
  - {taxonomy: owasp, id: M3, relationship: primary}
  - {taxonomy: cwe, id: CWE-287, relationship: related}
S-3:
  - {taxonomy: owasp, id: M1, relationship: primary}
  - {taxonomy: cwe, id: CWE-522, relationship: related}
S-4:
  - {taxonomy: owasp, id: A07, relationship: primary}
  - {taxonomy: cwe, id: CWE-287, relationship: related}
S-5:
  - {taxonomy: owasp, id: A07, relationship: primary}
  - {taxonomy: cwe, id: CWE-613, relationship: related}
T-1:
  - {taxonomy: owasp, id: M2, relationship: primary}
  - {taxonomy: cwe, id: CWE-345, relationship: related}
T-2:
  - {taxonomy: owasp, id: M2, relationship: primary}
  - {taxonomy: cwe, id: CWE-345, relationship: related}
T-3:
  - {taxonomy: owasp, id: M4, relationship: primary}
  - {taxonomy: cwe, id: CWE-20, relationship: related}
T-4:
  - {taxonomy: owasp, id: M7, relationship: primary}
  - {taxonomy: cwe, id: CWE-94, relationship: related}
T-5:
  - {taxonomy: owasp, id: M9, relationship: primary}
  - {taxonomy: cwe, id: CWE-345, relationship: related}
T-6:
  - {taxonomy: owasp, id: M1, relationship: primary}
  - {taxonomy: cwe, id: CWE-522, relationship: related}
```
